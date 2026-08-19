# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Context

This is a subdirectory within a DevOps mono-repo at `../` (JeanCossio). The repo is a personal lab and learning portfolio covering: Terraform (OCI + AWS), Ansible, Docker/Compose, Kubernetes, CloudFormation, and Python apps.

**Proyecto_CVIA**: k3s en EC2 t4g.micro (AWS ARM free tier) con nginx. Objetivo: Kubernetes barato (~$0–7/mes) para aprendizaje y portafolio.

## Estilo de Código

Todo el código se escribe como lo escribiría Jean — DevOps principiante construyendo portafolio para conseguir empleo:

- **Separadores de sección**: `#-------------------------------------------------------------------` antes de cada bloque lógico
- **Comentarios en español** explicando el propósito de cada recurso/bloque
- **Variables siempre con `description`** en español y `default` definido
- **Tags obligatorios en AWS**: `Name` y `Environment` en todos los recursos
- **Provider AWS**: `~> 5.0`, `required_version = ">= 1.0.0"`
- **Archivos separados**: `main.tf` / `variables.tf` / `outputs.tf` — nunca todo en uno
- **Sin abstracciones**: todo inline, nada de módulos a menos que sea obvio reutilizar

## Common Stack Conventions (across the mono-repo)

### Docker
- Base images: `python:3.12-alpine` for Python services, minimal images preferred
- Named volumes for persistent data; bind-mounts for local source code during dev
- Compose files named `docker-compose.yml` or `compose.yml`
- Containers built locally (`build: .`), not pulled unless it's a pure infrastructure service

### Terraform
- Provider: OCI (`oracle/oci ~> 6.0`) and AWS; credentials via variables, never hardcoded
- Required Terraform version: `>= 1.0.0`
- File layout: `main.tf`, `variables.tf`, `outputs.tf` per module
- OCI shapes in use: `VM.Standard.A1.Flex` (ARM/aarch64, Oracle Linux 8)

### Ansible
- Inventory at `inventory/`, playbooks at `playbooks/`, roles at `roles/`
- Managed via Docker Compose with a dedicated container

### Python
- Standard library + pip; `requirements.txt` for dependencies
- Scripts are standalone (not packages); run directly with `python script.py`

## Development Workflow

```bash
# Docker Compose (start services)
docker compose up -d

# Terraform (from a tf project directory)
terraform init
terraform plan
terraform apply

# Ansible (via Docker)
docker compose run --rm ansible ansible-playbook playbooks/<playbook>.yml

# Python (local)
pip install -r requirements.txt
python <script>.py
```

## Cloud Providers

- **OCI (Oracle Cloud Infrastructure)**: Primary compute (ARM free-tier VMs), auth via API key (`~/.oci/config`)
- **AWS**: VPC, networking, CloudFormation stacks; auth via environment variables or `~/.aws/credentials`

## Automejora

Después de CUALQUIER corrección del usuario o error identificado, invocar `/aprender` para registrar la lección en la sección de abajo. No esperar a que el usuario lo pida.

Criterios para registrar: error específico a este proyecto, accionable como regla, no duplicado.

## Lecciones Aprendidas

<!-- Las lecciones se agregan automáticamente con /aprender -->
