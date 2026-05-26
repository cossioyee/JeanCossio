#!/bin/bash
# Helper para ejecutar comandos de Terraform dentro del contenedor Docker
# Uso: ./tf.sh <comando>
# Ejemplos:
#   ./tf.sh init
#   ./tf.sh plan
#   ./tf.sh apply
#   ./tf.sh destroy

set -e

# Crea archivos de estado vacíos si no existen (Docker no puede montar archivos que no existen)
touch terraform.tfstate
mkdir -p .terraform

docker compose run --rm terraform "$@"
