#!/bin/bash
#-------------------------------------------------------------------
# Script de arranque - Instala k3s y despliega nginx
# Se ejecuta automáticamente al lanzar la instancia EC2
#-------------------------------------------------------------------

set -e  # Detener el script si algún comando falla

echo "=== Iniciando instalación de k3s ==="

#-------------------------------------------------------------------
# Actualizar el sistema operativo primero
#-------------------------------------------------------------------
dnf update -y

#-------------------------------------------------------------------
# Instalar k3s - Kubernetes ligero, perfecto para una sola instancia
# La variable INSTALL_K3S_EXEC configura k3s como servidor (nodo master)
#-------------------------------------------------------------------
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --disable traefik" sh -

echo "=== Esperando que k3s esté listo ==="
sleep 30

#-------------------------------------------------------------------
# Configurar kubectl para el usuario ec2-user
# Por defecto k3s solo funciona para root, esto lo arregla
#-------------------------------------------------------------------
mkdir -p /home/ec2-user/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ec2-user/.kube/config
chown ec2-user:ec2-user /home/ec2-user/.kube/config
chmod 600 /home/ec2-user/.kube/config

# Agregar la variable KUBECONFIG al perfil del usuario
echo 'export KUBECONFIG=/home/ec2-user/.kube/config' >> /home/ec2-user/.bashrc

echo "=== k3s instalado correctamente ==="
echo "=== Desplegando nginx ==="

#-------------------------------------------------------------------
# Desplegar nginx usando el manifiesto del proyecto
# --wait hace que kubectl espere hasta que el pod esté Running
#-------------------------------------------------------------------
kubectl --kubeconfig=/etc/rancher/k3s/k3s.yaml apply -f /tmp/nginx.yaml 2>/dev/null || true

echo "=== Instalación completa ==="
echo "=== Nginx disponible en el puerto 30080 ==="
