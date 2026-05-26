# OCI VM con Terraform en Docker

Crea una VM `VM.Standard.A1.Flex` (ARM, Always Free) con Oracle Linux 8 en Oracle Cloud usando Terraform dentro de un contenedor Docker — sin instalar Terraform localmente.

---

## Prerequisitos

- Docker Desktop instalado y corriendo
- Cuenta de Oracle Cloud con API Keys configuradas en `~/.oci/oci_api_key.pem`
- Llave SSH en `~/.ssh/id_rsa.pub` (si no la tienes: `ssh-keygen -t ed25519 -f ~/.ssh/id_rsa`)

---

## Setup inicial (solo la primera vez)

### 1. API Keys de OCI

En la consola OCI: **Profile → API Keys → Add API Key**

Descarga la private key y guárdala:
```bash
mkdir -p ~/.oci
mv ~/Downloads/oci_api_key.pem ~/.oci/oci_api_key.pem
chmod 600 ~/.oci/oci_api_key.pem
```

### 2. Variables de Terraform

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars` con tus valores (se obtienen en OCI Console → Profile):

```hcl
tenancy_ocid     = "ocid1.tenancy.oc1..xxxxx"
user_ocid        = "ocid1.user.oc1..xxxxx"
fingerprint      = "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
private_key_path = "~/.oci/oci_api_key.pem"

region           = "sa-bogota-1"
compartment_ocid = "ocid1.compartment.oc1..xxxxx"

ssh_public_key_path = "~/.ssh/id_rsa.pub"
```

### 3. Construir la imagen Docker

```bash
docker compose build
```

Descarga Terraform 1.9 y el provider de OCI dentro de la imagen. Solo necesitas repetirlo si cambias el `Dockerfile` o los archivos `.tf`.

---

## Uso

Todos los comandos van con el helper `tf.sh`:

```bash
./tf.sh init      # primera vez, o tras cambiar providers
./tf.sh plan      # previsualiza los cambios sin aplicar nada
./tf.sh apply     # crea la infraestructura (pide confirmación: escribe "yes")
./tf.sh output    # muestra IPs y comando SSH tras el apply
./tf.sh destroy   # elimina todo (pide confirmación: escribe "yes")
```

### Conectarse a la VM

```bash
ssh opc@<IP_PUBLICA>   # el usuario en Oracle Linux es "opc"
```

---

## Reintento automático por falta de capacidad

El free tier de OCI (`VM.Standard.A1.Flex`) frecuentemente muestra `Out of host capacity`. El script `retry-apply.sh` reintenta automáticamente hasta que haya disponibilidad:

```bash
./retry-apply.sh        # reintenta cada 5 minutos (default)
./retry-apply.sh 10     # reintenta cada 10 minutos
```

Genera un log resumido en `retry-apply.log` para revisar el historial durante el día:

```
=== Inicio: 2026-05-25 18:50:00 | intervalo: 5m ===
[--] #1 18:50:12 — Sin capacidad. Proximo intento en 5m
[--] #2 18:55:14 — Sin capacidad. Proximo intento en 5m
[OK] #4 19:05:09 — VM creada exitosamente
    instance_public_ip = "158.xxx.xxx.xxx"
```

El script se detiene solo al crear la VM, o inmediatamente si ocurre un error distinto al de capacidad.

---

## Recursos del Free Tier

| Recurso | Este proyecto | Límite gratuito |
|---|---|---|
| OCPUs (A1.Flex) | 2 | 4 en total |
| RAM | 12 GB | 24 GB en total |
| Boot Volume | 50 GB | 200 GB en total |
| IPs públicas | 1 | 2 en total |

---

## Troubleshooting

**`401-NotAuthenticated`**
Verifica que el `fingerprint` en `terraform.tfvars` coincida con el de tu API Key en OCI Console, y que `~/.oci/oci_api_key.pem` exista y tenga permisos `600`.

**`Out of host capacity`**
La región no tiene capacidad para A1.Flex. Usa `./retry-apply.sh` para reintentar automáticamente.

**`terraform.tfvars` no existe**
```bash
cp terraform.tfvars.example terraform.tfvars
```

**`tf.sh` sin permisos**
```bash
chmod +x tf.sh retry-apply.sh
```
