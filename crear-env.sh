#!/usr/bin/env bash
# Genera .env con valores aleatorios. No lee ni muestra el resultado.
set -euo pipefail
cd "$(dirname "$0")"

N8N_VERSION="2.46.6"
POSTGRES_USER="n8n"
POSTGRES_DB="n8n"
POSTGRES_PASSWORD="$(openssl rand -base64 24)"
N8N_ENCRYPTION_KEY="$(openssl rand -hex 32)"
WEBHOOK_URL=""

cat > .env <<EOF
N8N_VERSION=${N8N_VERSION}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
WEBHOOK_URL=${WEBHOOK_URL}
EOF

echo "Archivo .env creado."
