#!/usr/bin/env bash
set -euo pipefail

docker compose exec -u node n8n n8n export:workflow --backup --output=/tmp/export/

rm -rf workflows
mkdir -p workflows
docker compose exec -T -u node n8n tar -C /tmp/export -cf - . | tar -xf - -C workflows

echo "Flujos exportados en la carpeta workflows/"
