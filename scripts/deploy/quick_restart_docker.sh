#!/bin/bash
# Atalho: Reinicia o ambiente Docker de desenvolvimento.
# Uso: ./scripts/deploy/quick_restart_docker.sh [serviço]
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../docker/dev.sh" restart "$@"
