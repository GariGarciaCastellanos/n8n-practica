#!/usr/bin/env bash
# Actualiza solo la linea N8N_VERSION de .env. No lee ni muestra el resto del archivo.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${1:-}" ]; then
  echo "Uso: $0 <version>" >&2
  exit 1
fi

NUEVA_VERSION="$1"
sed -i "s|^N8N_VERSION=.*|N8N_VERSION=${NUEVA_VERSION}|" .env

echo "N8N_VERSION actualizada en .env."
