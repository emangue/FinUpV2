#!/bin/bash

# =============================================================================
# deploy_docker_build_local.sh — Deploy com BUILD LOCAL (evita OOM/npm na VM)
# =============================================================================
#
# Uso: ./scripts/deploy/deploy_docker_build_local.sh
#
# Quando usar: Quando deploy_docker_vm.sh falha por OOM ou npm ci na VM
#
# Fluxo:
#   1. Build das imagens Docker LOCALMENTE (backend + frontend-app + frontend-admin)
#   2. docker save → tar
#   3. scp para VM
#   4. docker load na VM
#   5. git pull + migrations + docker compose up -d
#
# Requisitos:
#   - Docker instalado localmente
#   - .env.prod na VM (para migrations e variáveis)
#   - NEXT_PUBLIC_BACKEND_URL: https://meufinup.com.br/api (ou do .env.prod na VM)
# =============================================================================

set -e

VM_HOST="${VM_HOST:-minha-vps-hostinger}"
VM_PATH="${VM_PATH:-/var/www/finup}"
COMPOSE_FILE="docker-compose.prod.yml"
BRANCH=$(git branch --show-current)
BACKEND_URL="${NEXT_PUBLIC_BACKEND_URL:-https://meufinup.com.br/api}"

echo ""
echo "🚀 DEPLOY DOCKER (build local) → VM"
echo "    Branch : $BRANCH"
echo "    Host   : $VM_HOST"
echo "    Path   : $VM_PATH"
echo "    NEXT_PUBLIC_BACKEND_URL: $BACKEND_URL"
echo "=========================================="

# Raiz do projeto
if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute da raiz do projeto!"
    exit 1
fi

# Git limpo
if [ -n "$(git status --porcelain -uno)" ]; then
    echo "❌ Há mudanças não commitadas. Commit e push primeiro."
    git status --short -uno
    exit 1
fi

git fetch origin "$BRANCH" 2>/dev/null || true
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "none")
if [ "$REMOTE" = "none" ] || [ "$LOCAL" != "$REMOTE" ]; then
    echo "❌ Execute: git push origin $BRANCH"
    exit 1
fi

echo "✅ Pré-requisitos OK (commit ${LOCAL:0:7})"
echo ""

# Obter NEXT_PUBLIC_BACKEND_URL da VM se não definido
if [ -z "$NEXT_PUBLIC_BACKEND_URL" ]; then
    BACKEND_URL=$(ssh -o ConnectTimeout=5 "$VM_HOST" "grep NEXT_PUBLIC_BACKEND_URL $VM_PATH/.env.prod 2>/dev/null | cut -d= -f2-" || true)
    [ -z "$BACKEND_URL" ] && BACKEND_URL="https://meufinup.com.br/api"
fi
export NEXT_PUBLIC_BACKEND_URL="$BACKEND_URL"

echo "🔨 Fase 1: Build local das imagens..."
docker compose -p finup -f "$COMPOSE_FILE" build --no-cache
echo ""

echo "📦 Fase 2: Salvando imagens em tar..."
TAR_FILE="/tmp/finup-images-$(date +%Y%m%d%H%M%S).tar"
# -p finup garante nomes consistentes: finup-backend, finup-frontend-app, finup-frontend-admin
docker save finup-backend:latest finup-frontend-app:latest finup-frontend-admin:latest -o "$TAR_FILE" 2>/dev/null || {
    echo "❌ Imagens não encontradas. Verifique: docker images | grep finup"
    exit 1
}
echo "   Salvo em: $TAR_FILE"
echo ""

echo "📤 Fase 3: Enviando para VM..."
scp -o ConnectTimeout=15 "$TAR_FILE" "$VM_HOST:/tmp/finup-images.tar"
rm -f "$TAR_FILE"
echo ""

echo "📥 Fase 4: Na VM - git pull, load, up..."
ssh -o ConnectTimeout=30 -o ServerAliveInterval=60 "$VM_HOST" "cd $VM_PATH && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH && docker load -i /tmp/finup-images.tar && rm -f /tmp/finup-images.tar && docker compose -p finup -f $COMPOSE_FILE --env-file .env.prod up -d"
echo "   Aguardando backend..."
for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    if ssh -o ConnectTimeout=5 "$VM_HOST" "docker exec finup_backend_prod curl -sf http://localhost:8000/api/health" >/dev/null 2>&1; then
        echo "   Backend pronto!"
        break
    fi
    sleep 5
done
ssh -o ConnectTimeout=10 "$VM_HOST" "docker exec finup_backend_prod alembic upgrade head"
echo "   Migrations OK"

echo ""
echo "=========================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "   https://meufinup.com.br"
echo "=========================================="
