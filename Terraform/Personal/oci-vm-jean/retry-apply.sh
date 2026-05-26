#!/bin/bash
# Reintenta terraform apply cada N minutos hasta que OCI tenga capacidad disponible.
# Uso: ./retry-apply.sh [minutos]   (default: 5)

WAIT_MINUTES=${1:-5}
WAIT_SECONDS=$((WAIT_MINUTES * 60))
LOG_FILE="retry-apply.log"

CAPACITY_ERRORS="Out of host capacity|InsufficientServiceCapacity|shape is not available|Capacity is not available"

log() {
  echo "$1" | tee -a "$LOG_FILE"
}

attempt=1
log "=== Inicio: $(date '+%Y-%m-%d %H:%M:%S') | intervalo: ${WAIT_MINUTES}m ==="

while true; do
  echo "──────────────────────────────────────────"
  echo "Intento #$attempt — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "──────────────────────────────────────────"

  output=$(./tf.sh apply -auto-approve 2>&1)
  exit_code=$?
  echo "$output"

  if [ $exit_code -eq 0 ]; then
    echo ""
    echo "VM creada exitosamente."
    log "[OK] #$attempt $(date '+%H:%M:%S') — VM creada exitosamente"
    tf_output=$(./tf.sh output 2>&1)
    echo "$tf_output"
    public_ip=$(echo "$tf_output" | grep -E "instance_public_ip|public_ip" | head -1)
    [ -n "$public_ip" ] && log "    $public_ip"
    exit 0
  fi

  if echo "$output" | grep -qE "$CAPACITY_ERRORS"; then
    echo ""
    echo "Sin capacidad en la region. Reintentando en $WAIT_MINUTES min..."
    log "[--] #$attempt $(date '+%H:%M:%S') — Sin capacidad. Proximo intento en ${WAIT_MINUTES}m"
    sleep $WAIT_SECONDS
    attempt=$((attempt + 1))
  else
    error_line=$(echo "$output" | grep -E "Error:|error" | head -1)
    log "[!!] #$attempt $(date '+%H:%M:%S') — Error inesperado: $error_line"
    echo ""
    echo "Error inesperado (no es de capacidad). Revisa el output arriba."
    exit 1
  fi
done
