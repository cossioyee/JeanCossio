# CVIA — Cluster k3s en AWS con Panel Web

Cluster de Kubernetes ligero (k3s) en una EC2 t4g.micro ARM, gestionado desde un sitio estático en S3. Costo: ~$0–7/mes.

## Arquitectura

```
Sitio S3 (index.html)
    ↓  GitHub API (token en localStorage)
GitHub Actions (cvia-deploy.yml)
    ↓  terraform apply / destroy
EC2 t4g.micro ARM + k3s + nginx  →  http://<IP>:30080
```

---

## Prerequisitos

**Opción A — con Docker (recomendado, sin instalar Terraform localmente):**

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Docker Desktop | cualquiera | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| AWS CLI | v2 | `brew install awscli` |
| Git | cualquiera | ya instalado en macOS |

**Opción B — instalación local:**

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| AWS CLI | v2 | `brew install awscli` |
| Terraform | >= 1.0 | `brew tap hashicorp/tap && brew install hashicorp/tap/terraform` |
| Git | cualquiera | ya instalado en macOS |

Credenciales AWS configuradas:
```bash
aws configure
# AWS Access Key ID:     <tu key>
# AWS Secret Access Key: <tu secret>
# Default region:        us-east-1
# Default output format: json
```

---

## Setup Inicial (una sola vez)

### 1. Crear Key Pair en AWS para SSH

```bash
aws ec2 create-key-pair \
  --key-name cvia-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/cvia-key.pem

chmod 400 ~/.ssh/cvia-key.pem
```

### 2. Configurar credenciales para el contenedor (solo Opción A)

```bash
cd Proyecto_CVIA
cp .env.example .env
# Editar .env con tu AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY
```

### 3. Levantar los buckets S3 (launcher)

**Con Docker:**
```bash
cd Proyecto_CVIA
docker compose run --rm launcher init
docker compose run --rm launcher apply
```

**Local:**
```bash
cd Proyecto_CVIA/launcher
terraform init
terraform apply
```

Anota los outputs que aparecen al final:
```
tf_state_bucket  = "cvia-tf-state-xxxxxx"   ← lo necesitas en los pasos 4 y 5
sitio_web_bucket = "cvia-sitio-web-xxxxxx"  ← lo necesitas en el paso 6
sitio_web_url    = "http://cvia-sitio-web-xxxxxx.s3-website-us-east-1.amazonaws.com"
```

### 4. Migrar el estado de Terraform a S3

**Con Docker:**
```bash
cd Proyecto_CVIA
docker compose run --rm terraform init -backend-config="bucket=<tf_state_bucket>"
# Cuando pregunte si migrar el estado existente → escribe: yes
```

**Local:**
```bash
cd Proyecto_CVIA/terraform
terraform init -backend-config="bucket=<tf_state_bucket>"
# Cuando pregunte si migrar el estado existente → escribe: yes
```

### 5. Configurar GitHub Actions

En tu repo GitHub → **Settings → Secrets and variables → Actions**:

**Secrets** (valores privados):
| Nombre | Valor |
|---|---|
| `AWS_ACCESS_KEY_ID` | Tu Access Key de AWS |
| `AWS_SECRET_ACCESS_KEY` | Tu Secret Key de AWS |

**Variables** (valores no sensibles):
| Nombre | Valor |
|---|---|
| `TF_STATE_BUCKET` | El nombre del bucket del paso 3 (`cvia-tf-state-xxxxxx`) |

### 6. Subir el sitio web a S3

```bash
aws s3 cp Proyecto_CVIA/static/index.html s3://<sitio_web_bucket>/index.html
```

### 7. Crear GitHub Personal Access Token

1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Clic **Generate new token**
3. Scope requerido: marcar **`workflow`** (dentro de `repo`)
4. Copiar el token generado (`ghp_...`)

---

## Uso Diario

### Abrir el panel de control

Abrir en el navegador la URL del sitio (output `sitio_web_url` del paso 2):
```
http://cvia-sitio-web-xxxxxx.s3-website-us-east-1.amazonaws.com
```

### Primera vez: ingresar el token

1. Pegar el token de GitHub en el campo de la parte superior
2. Clic **Guardar** — queda guardado en el navegador (localStorage)

### Levantar el cluster

1. Clic **🚀 Levantar Cluster**
2. Aparece un link directo al run de GitHub Actions
3. Esperar ~5 minutos mientras GitHub Actions corre el `terraform apply`
4. Al terminar, el resumen del workflow muestra la IP y URL de nginx

Verificar que nginx está corriendo:
```bash
# Desde el navegador
http://<IP>:30080

# O desde la terminal
curl http://<IP>:30080
```

### Destruir el cluster

1. Clic **💣 Destruir Cluster**
2. GitHub Actions corre `terraform destroy -auto-approve`
3. En ~3 minutos la EC2, VPC y todos los recursos son eliminados
4. El estado del bucket S3 y el sitio web se mantienen (costo mínimo: ~$0.01/mes)

### Conectarse por SSH a la instancia (opcional)

```bash
# La IP aparece en el resumen del workflow de GitHub Actions
ssh -i ~/.ssh/cvia-key.pem ec2-user@<IP>

# Ver pods de kubernetes
kubectl get pods -n cvia

# Ver logs de nginx
kubectl logs -n cvia deploy/nginx
```

---

## Costos Estimados

| Recurso | Costo/mes |
|---|---|
| EC2 t4g.micro (solo cuando está levantado) | $0 free tier / ~$6 después |
| S3 buckets (siempre activos) | ~$0.02 |
| GitHub Actions | $0 (repo público) |
| **Total cluster levantado** | **~$0–6/mes** |
| **Total cluster destruido** | **~$0.02/mes** |

> Destruir el cluster cuando no lo uses. El sitio S3 queda activo siempre para poder volver a levantarlo cuando quieras.

---

## Estructura del Proyecto

```
Proyecto_CVIA/
├── docker-compose.yml  # Contenedor de Terraform (servicios: launcher, terraform)
├── .env.example        # Plantilla de credenciales AWS (copiar a .env)
├── launcher/           # Terraform: crea los buckets S3 (correr solo una vez)
├── terraform/          # Terraform: VPC + EC2 + k3s (gestionado por GitHub Actions)
├── k8s/
│   └── nginx.yaml      # Manifiesto de nginx en k3s
├── scripts/
│   └── install-k3s.sh  # Bootstrap: instala k3s en la EC2 al lanzar
└── static/
    └── index.html      # Panel de control web

.github/workflows/
└── cvia-deploy.yml     # GitHub Actions: ejecuta terraform apply/destroy
```

---

## Solución de Problemas

**El workflow falla en `terraform init`**
→ Verificar que la variable `TF_STATE_BUCKET` en GitHub Actions tiene el nombre correcto del bucket.

**Error 401 en el sitio web al hacer clic en los botones**
→ El token de GitHub expiró o no tiene el scope `workflow`. Generar uno nuevo y guardarlo en el panel.

**nginx no responde en `:30080` después de levantar**
→ El script de instalación de k3s tarda ~2 minutos adicionales después de que terraform termina. Esperar y reintentar.

**Quiero conectarme por SSH pero no tengo la IP**
→ Ir a GitHub Actions → último run de `apply` → ver el Step Summary al final del workflow.
