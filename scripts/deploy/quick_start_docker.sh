#!/bin/bash
# Atalho: Inicia o ambiente Docker de desenvolvimento.
# Uso: ./scripts/deploy/quick_start_docker.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../docker/dev.sh" start
