#!/bin/bash
# Atalho: Para o ambiente Docker de desenvolvimento.
# Uso: ./scripts/deploy/quick_stop_docker.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../docker/dev.sh" stop
