#!/usr/bin/env bash
# Añade N8N_RUNNERS_AUTH_TOKEN a .env si no existe. No lee ni muestra el resto del archivo.
set -euo pipefail
cd "$(dirname "$0")"

if grep -q "^N8N_RUNNERS_AUTH_TOKEN=" .env; then
  echo "N8N_RUNNERS_AUTH_TOKEN ya existia en .env, no se ha tocado."
  exit 0
fi

TOKEN="$(openssl rand -hex 32)"
echo "N8N_RUNNERS_AUTH_TOKEN=${TOKEN}" >> .env

echo "N8N_RUNNERS_AUTH_TOKEN añadido a .env."
