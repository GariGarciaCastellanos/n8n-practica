#!/usr/bin/env bash
# Actualiza solo la linea WEBHOOK_URL de .env. No lee ni muestra el resto del archivo.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${1:-}" ]; then
  echo "Uso: $0 <url-publica-con-barra-final>" >&2
  exit 1
fi

NUEVA_URL="$1"
sed -i "s|^WEBHOOK_URL=.*|WEBHOOK_URL=${NUEVA_URL}|" .env

echo "WEBHOOK_URL actualizada en .env."
