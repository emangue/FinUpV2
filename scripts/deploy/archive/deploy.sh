#!/bin/bash

# =============================================================================
# DEPLOY ÚNICO - FinUp (app_dev) na VM
# =============================================================================
# Uso: ./scripts/deploy/deploy.sh
#
# Fluxo: valida git → pull na VM → migrations → build na VM → restart frontend
# Restart usa pkill+nohup (systemctl não disponível no servidor).
# Frontend na porta 3003 (Easypanel usa 3000).
#
# Ref: docs/deploy/DEPLOY_PROCESSO_CONSOLIDADO.md
# =============================================================================

set -e

BRANCH=$(git branch --show-current)
VM_HOST="minha-vps-hostinger"
VM_PATH="/var/www/finup"
FRONTEND_PORT=3003

echo "🚀 DEPLOY FinUp - branch: $BRANCH"
echo "========================================"

# --- 1. Validar que estamos na raiz ---
if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute da raiz do projeto!"
    exit 1
fi

# --- 2. Validar git (ignora untracked) ---
if [ -n "$(git status --porcelain -uno)" ]; then
    echo "⚠️  Há mudanças não commitadas. Commit e push primeiro."
    git status --short -uno
    exit 1
fi

# --- 3. Validar que não existe middleware.ts (conflito com proxy) ---
if [ -f "app_dev/frontend/src/middleware.ts" ]; then
    echo "⚠️  Remova app_dev/frontend/src/middleware.ts (use apenas proxy.ts)"
    exit 1
fi

# --- 4. Validar sync com remote ---
git fetch origin "$BRANCH" 2>/dev/null || {
    echo "⚠️  git fetch falhou. Verifique: git remote -v"
    echo "   Se origin não existir: git remote add origin https://github.com/emangue/FinUpV2.git"
    exit 1
}
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "none")
if [ "$REMOTE" = "none" ] || [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Execute: git push origin $BRANCH"
    exit 1
fi

echo "✅ Pré-requisitos OK (${LOCAL:0:7})"
echo ""

# --- 5. Deploy na VM ---
echo "🚀 Deploy no servidor..."
ssh -o ConnectTimeout=15 -o ServerAliveInterval=30 "$VM_HOST" "
    set -e
    cd $VM_PATH || exit 1

    echo '📥 Git pull...'
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH

    echo '🗄️  Migrations...'
    cd app_dev/backend
    source venv/bin/activate 2>/dev/null || source ../../venv/bin/activate
    alembic upgrade head
    cd ../..

    echo '📦 Frontend - build...'
    cd app_dev/frontend
    npm ci --quiet
    NODE_OPTIONS=--max-old-space-size=4096 npm run build
    cd ../..
" || {
    echo ""
    echo "❌ Deploy falhou. Se foi OOM no build, use: ./scripts/deploy/deploy_build_local.sh"
    exit 1
}

# --- 6. Restart frontend (pkill + nohup, sem systemctl) ---
echo ""
echo "🔄 Reiniciando frontend (porta $FRONTEND_PORT)..."
ssh -o ConnectTimeout=15 "$VM_HOST" "
    pkill -f 'next start -p $FRONTEND_PORT' 2>/dev/null || true
    sleep 2
    cd $VM_PATH/app_dev/frontend
    sudo -u deploy nohup npm run start -- -p $FRONTEND_PORT > /tmp/finup-frontend.log 2>&1 &
    sleep 5
    if grep -q 'Ready' /tmp/finup-frontend.log 2>/dev/null; then
        echo '✅ Frontend OK'
    else
        tail -10 /tmp/finup-frontend.log
        echo '⚠️  Verifique /tmp/finup-frontend.log na VM'
    fi
"

# --- 7. Health check backend ---
echo ""
echo "🏥 Health check..."
if ssh -o ConnectTimeout=5 "$VM_HOST" "curl -s -f http://localhost:8000/api/health" >/dev/null 2>&1; then
    echo "✅ Backend OK"
else
    echo "⚠️  Backend pode precisar de restart manual"
fi

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "   https://meufinup.com.br"
echo "   https://meufinup.com.br/mobile/dashboard"
