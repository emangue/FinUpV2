#!/bin/bash

# ==========================================
# DEPLOY VIA SCP + SSH EXECUÇÃO REMOTA
# ==========================================

echo "🚀 Deploy via transferência de arquivo..."

SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

log "1. Copiando script para servidor..."
if ! scp -i "$SSH_KEY" deploy_server.sh "$SERVER":/tmp/deploy.sh; then
    error "Falha ao copiar script"
    exit 1
fi

log "2. Tornando script executável..."
if ! ssh -i "$SSH_KEY" "$SERVER" "chmod +x /tmp/deploy.sh"; then
    error "Falha ao tornar script executável"
    exit 1
fi

log "3. Executando deploy no servidor..."
echo "=================================================="
ssh -i "$SSH_KEY" "$SERVER" "cd /tmp && ./deploy.sh" || {
    error "Falha na execução do deploy"
    exit 1
}

echo "=================================================="
log "🎉 Deploy concluído!"
log "Acesse: http://148.230.78.91:3000"