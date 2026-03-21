#!/bin/bash

# =============================================================================
# DEPLOY COM BUILD LOCAL - Alternativa quando OOM na VM
# =============================================================================
# Uso: ./scripts/deploy/deploy_build_local.sh
#
# Fluxo: build local → tar+ssh .next → VM: pull + migrations → restart frontend
# Use quando deploy.sh falhar por OOM no npm run build.
#
# Ref: docs/deploy/DEPLOY_PROCESSO_CONSOLIDADO.md
# =============================================================================

set -e

BRANCH=$(git branch --show-current)
VM_HOST="minha-vps-hostinger"
VM_PATH="/var/www/finup"
FRONTEND_PORT=3003

echo "🚀 DEPLOY (build local): $BRANCH"
echo "========================================"

if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute da raiz do projeto!"
    exit 1
fi

if [ -n "$(git status --porcelain -uno)" ]; then
    echo "⚠️  Há mudanças não commitadas. Commit e push primeiro."
    git status --short -uno
    exit 1
fi

git fetch origin "$BRANCH" 2>/dev/null || true
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "none")
if [ "$REMOTE" = "none" ] || [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Execute: git push origin $BRANCH"
    exit 1
fi

echo "✅ Git OK"
echo ""

# 1. Build local
echo "📦 Build local do frontend..."
cd app_dev/frontend
npm ci --quiet
npm run build
cd ../..
echo "✅ Build concluído"
echo ""

# 2. Pull + migrations na VM
echo "📥 Git pull e migrations na VM..."
ssh -o ConnectTimeout=15 "$VM_HOST" "
    set -e
    cd $VM_PATH
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    cd app_dev/backend
    source venv/bin/activate 2>/dev/null || source ../../venv/bin/activate
    alembic upgrade head
" || { echo "❌ Falha SSH"; exit 1; }

# 3. Enviar .next via tar
echo "📤 Enviando .next..."
ssh "$VM_HOST" "rm -rf $VM_PATH/app_dev/frontend/.next.old; mv $VM_PATH/app_dev/frontend/.next $VM_PATH/app_dev/frontend/.next.old 2>/dev/null; mkdir -p $VM_PATH/app_dev/frontend/.next"
tar czf - -C app_dev/frontend .next | ssh -o ServerAliveInterval=30 "$VM_HOST" "cd $VM_PATH/app_dev/frontend && tar xzf -"
ssh "$VM_HOST" "rm -rf $VM_PATH/app_dev/frontend/.next.old"
echo "✅ .next enviado"

# 4. Restart frontend
echo ""
echo "🔄 Reiniciando frontend..."
ssh "$VM_HOST" "
    pkill -f 'next start -p $FRONTEND_PORT' 2>/dev/null || true
    sleep 2
    cd $VM_PATH/app_dev/frontend
    sudo -u deploy nohup npm run start -- -p $FRONTEND_PORT > /tmp/finup-frontend.log 2>&1 &
    sleep 5
    tail -3 /tmp/finup-frontend.log
"

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "   https://meufinup.com.br"
