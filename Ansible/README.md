# Ansible Control Node — Guía de Uso

Nodo de control Ansible dockerizado sobre **CentOS Stream 9** con `ansible-core 2.17`.  
La idea: corres el contenedor, montas tus playbooks e inventario, y desde ahí ejecutas contra hosts remotos sin instalar Ansible en tu Mac.

---

## Estructura del proyecto

```
Ansible/
├── Dockerfile              # Imagen del nodo de control (CentOS 9 + ansible-core 2.17)
├── docker-compose.yml      # Levanta el contenedor con los volúmenes necesarios
├── .gitignore              # Excluye inventory/hosts (contiene IPs/contraseñas)
├── inventory/
│   ├── hosts               # Inventario principal (ignorado en git — ver abajo)
│   └── hosts.example       # Plantilla de inventario para commitear
├── playbooks/
│   └── *.yml               # Tus playbooks van aquí
└── roles/
    └── <nombre-rol>/       # Roles reutilizables
```

---

## Inicio rápido

### 1. Construir la imagen

```bash
cd Ansible/
docker compose build
```

### 2. Levantar el contenedor (modo interactivo)

```bash
docker compose up -d
docker exec -it ansible-control-node bash
```

Desde dentro del contenedor ya tienes acceso a:
- `ansible` y `ansible-playbook`
- Tus playbooks en `/ansible/playbooks`
- Tu inventario en `/ansible/inventory`
- Tus claves SSH de `~/.ssh` montadas en solo lectura

### 3. Verificar instalación

```bash
# Dentro del contenedor
ansible --version
```

---

## Configurar el inventario (hosts remotos)

El inventario le dice a Ansible **a qué hosts conectarse** y cómo.

### Crear `inventory/hosts`

Este archivo está en `.gitignore` — ponle datos reales sin miedo.

```ini
# inventory/hosts

# --- Servidores individuales ---
[webservers]
web01 ansible_host=192.168.1.10 ansible_user=ubuntu ansible_ssh_private_key_file=/root/.ssh/id_rsa
web02 ansible_host=192.168.1.11 ansible_user=ubuntu ansible_ssh_private_key_file=/root/.ssh/id_rsa

[dbservers]
db01  ansible_host=192.168.1.20 ansible_user=centos ansible_ssh_private_key_file=/root/.ssh/id_rsa

# --- Grupo que agrupa grupos ---
[production:children]
webservers
dbservers

# --- Variables compartidas por grupo ---
[webservers:vars]
ansible_python_interpreter=/usr/bin/python3

[all:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### Crear `inventory/hosts.example` (sí va en git)

```ini
# inventory/hosts.example — copia esto a inventory/hosts y rellena con tus datos

[webservers]
web01 ansible_host=<IP> ansible_user=<USER> ansible_ssh_private_key_file=/root/.ssh/id_rsa

[dbservers]
db01 ansible_host=<IP> ansible_user=<USER> ansible_ssh_private_key_file=/root/.ssh/id_rsa
```

---

## Autenticación SSH

El `docker-compose.yml` ya monta `~/.ssh` del host en `/root/.ssh` (solo lectura).  
Solo necesitas asegurarte de que la clave correcta esté ahí.

### Opción A — Clave existente en tu Mac

```bash
# En tu Mac (fuera del contenedor)
ls ~/.ssh/
# Verifica que exista id_rsa o id_ed25519
```

### Opción B — Generar y distribuir una clave nueva

```bash
# En tu Mac
ssh-keygen -t ed25519 -f ~/.ssh/ansible_key -C "ansible-control-node"

# Copiar la clave pública al host remoto
ssh-copy-id -i ~/.ssh/ansible_key.pub usuario@IP-del-host
```

Luego en tu inventario usa: `ansible_ssh_private_key_file=/root/.ssh/ansible_key`

### Opción C — Contraseña (solo para pruebas)

Instala `sshpass` (ya está en el Dockerfile) y en el inventario:

```ini
web01 ansible_host=192.168.1.10 ansible_user=ubuntu ansible_password=mi_password ansible_become_password=mi_password
```

---

## Comandos ad-hoc (sin playbook)

Útiles para tareas rápidas o verificar conectividad.

```bash
# Dentro del contenedor

# Probar conectividad a todos los hosts
ansible all -i /ansible/inventory/hosts -m ping

# Probar solo un grupo
ansible webservers -i /ansible/inventory/hosts -m ping

# Ejecutar un comando en todos los hosts
ansible all -i /ansible/inventory/hosts -m shell -a "uptime"

# Ver uso de disco en dbservers
ansible dbservers -i /ansible/inventory/hosts -m shell -a "df -h"

# Copiar un archivo a todos los webservers
ansible webservers -i /ansible/inventory/hosts -m copy \
  -a "src=/ansible/playbooks/config.conf dest=/etc/myapp/config.conf"

# Instalar un paquete (con escalada de privilegios)
ansible webservers -i /ansible/inventory/hosts -m dnf \
  -a "name=nginx state=present" --become
```

---

## Playbooks

Un playbook es un archivo YAML que define **qué hacer y en qué hosts**.

### Playbook básico — `playbooks/ping.yml`

```yaml
---
- name: Verificar conectividad
  hosts: all
  gather_facts: false

  tasks:
    - name: Ping
      ansible.builtin.ping:
```

### Playbook real — `playbooks/setup_webserver.yml`

```yaml
---
- name: Configurar servidor web
  hosts: webservers
  become: true          # sudo en el host remoto

  vars:
    app_port: 8080
    app_user: deploy

  tasks:
    - name: Actualizar paquetes del sistema
      ansible.builtin.dnf:
        name: "*"
        state: latest

    - name: Instalar Nginx
      ansible.builtin.dnf:
        name: nginx
        state: present

    - name: Asegurar que Nginx está corriendo y habilitado
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

    - name: Abrir puerto en firewall
      ansible.posix.firewalld:
        port: "{{ app_port }}/tcp"
        permanent: true
        state: enabled
      notify: Recargar firewall

  handlers:
    - name: Recargar firewall
      ansible.builtin.service:
        name: firewalld
        state: reloaded
```

### Ejecutar un playbook

```bash
# Dentro del contenedor

# Sintaxis básica
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml

# Dry-run (simular sin cambiar nada)
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml --check

# Ver qué cambiaría (diff)
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml --check --diff

# Solo en un host específico
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml --limit web01

# Solo en un grupo
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml --limit webservers

# Con variables extra
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml \
  -e "app_port=9090"

# Verbose (debug)
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/setup_webserver.yml -vvv
```

---

## Variables y precedencia

Ansible tiene muchos lugares para poner variables. De mayor a menor precedencia:

| Prioridad | Dónde |
|-----------|-------|
| 1 (mayor) | `-e` en CLI |
| 2 | `vars` en el play |
| 3 | `host_vars/<hostname>.yml` |
| 4 | `group_vars/<grupo>.yml` |
| 5 (menor) | Variables del inventario |

### Estructura recomendada

```
inventory/
  hosts
  host_vars/
    web01.yml        # Variables específicas de web01
  group_vars/
    webservers.yml   # Variables para todos los webservers
    all.yml          # Variables globales
```

`group_vars/all.yml`:
```yaml
ansible_python_interpreter: /usr/bin/python3
ntp_server: pool.ntp.org
```

`group_vars/webservers.yml`:
```yaml
nginx_worker_processes: 4
app_port: 8080
```

---

## Roles (para proyectos más grandes)

Un rol es un playbook modular y reutilizable. Estructura estándar:

```
roles/
└── nginx/
    ├── tasks/
    │   └── main.yml      # Tareas principales
    ├── handlers/
    │   └── main.yml      # Handlers (reiniciar servicio, etc.)
    ├── templates/
    │   └── nginx.conf.j2 # Plantillas Jinja2
    ├── files/
    │   └── index.html    # Archivos estáticos
    ├── vars/
    │   └── main.yml      # Variables del rol
    └── defaults/
        └── main.yml      # Variables con valores por defecto
```

Usar un rol en un playbook:

```yaml
---
- name: Desplegar app
  hosts: webservers
  become: true
  roles:
    - nginx
    - { role: app_deploy, app_version: "1.2.3" }
```

---

## Flujo de trabajo completo — ejemplo práctico

### Objetivo: desplegar un cambio en producción

```bash
# 1. Entrar al contenedor
docker exec -it ansible-control-node bash

# 2. Verificar que todos los hosts responden
ansible all -i /ansible/inventory/hosts -m ping

# 3. Dry-run del playbook
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/deploy.yml --check --diff

# 4. Ejecutar primero en un solo host
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/deploy.yml --limit web01

# 5. Si todo está bien, ejecutar en el resto
ansible-playbook -i /ansible/inventory/hosts /ansible/playbooks/deploy.yml --limit webservers

# 6. Verificar el resultado
ansible webservers -i /ansible/inventory/hosts -m shell -a "systemctl status nginx"
```

---

## Troubleshooting frecuente

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `UNREACHABLE` | No hay conectividad SSH | Verificar IP, puerto 22, firewall |
| `Permission denied` | Clave SSH no autorizada | Correr `ssh-copy-id` en el host remoto |
| `sudo: command not found` | `become: true` sin sudo instalado | Instalar sudo en el host remoto |
| `Python not found` | Python no instalado en host remoto | Agregar `ansible_python_interpreter=/usr/bin/python3` |
| `Host key verification failed` | Primera conexión sin trust | La var `ANSIBLE_HOST_KEY_CHECKING=False` ya está en compose |

### Probar SSH manualmente (desde el contenedor)

```bash
ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=no usuario@192.168.1.10
```

---

## Referencia rápida de comandos

```bash
# Listar hosts del inventario
ansible all -i /ansible/inventory/hosts --list-hosts

# Listar grupos
ansible all -i /ansible/inventory/hosts --list-groups  # (via -m debug en older versions)

# Ver variables de un host
ansible web01 -i /ansible/inventory/hosts -m setup

# Recolectar solo facts de red
ansible web01 -i /ansible/inventory/hosts -m setup -a "filter=ansible_interfaces"

# Ejecutar con tags específicos
ansible-playbook playbooks/deploy.yml --tags "config,restart"

# Saltar tags
ansible-playbook playbooks/deploy.yml --skip-tags "notify"
```
