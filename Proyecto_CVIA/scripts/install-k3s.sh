#!/bin/bash
set -euo pipefail

# Instalar k3s
curl -sfL https://get.k3s.io | sh -

# Esperar que k3s esté listo
timeout 120 bash -c 'until /usr/local/bin/kubectl get nodes 2>/dev/null | grep -q Ready; do sleep 5; done'

# Copiar kubeconfig para ec2-user
mkdir -p /home/ec2-user/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ec2-user/.kube/config
chown -R ec2-user:ec2-user /home/ec2-user/.kube
