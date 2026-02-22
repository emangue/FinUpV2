#!/bin/bash

# Deploy branch na VM com BUILD LOCAL (evita OOM na VM)
# Uso: ./scripts/deploy/deploy_branch_vm_build_local.sh
#
# Fluxo: build local → rsync .next → VM: pull + migrations + restart

set -e

BRANCH=$(git branch --show-current)
VM_HOST="minha-vps-hostinger"
VM_PATH="/var/www/finup"

echo "🚀 DEPLOY BRANCH (build local): $BRANCH"
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

git fetch origin "$BRANCH" --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "none")
if [ "$REMOTE" = "none" ] || [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Execute: git push origin $BRANCH"
    exit 1
fi

echo "✅ Git OK (${LOCAL:0:7})"
echo ""

# 1. Build local do frontend
echo "📦 1. Build local do frontend..."
cd app_dev/frontend
npm ci --quiet
npm run build
cd ../..
echo "✅ Build local concluído"
echo ""

# 2. Deploy na VM (backup PG + pull + migrations + rsync + restart)
echo "🚀 2. Deploy na VM..."
ssh -o ConnectTimeout=10 "$VM_HOST" "
    set -e
    cd $VM_PATH || exit 1

    echo '📥 Backup PostgreSQL (antes de migrations)...'
    pg_dump -U finup_user finup_db > backup_pre_deploy_\$(date +%Y%m%d_%H%M).sql 2>/dev/null || echo '   (ignorado se pg_dump indisponível)'

    echo '📥 Git fetch e checkout...'
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH

    echo '🗄️  Migrations...'
    cd app_dev/backend
    source venv/bin/activate 2>/dev/null || source ../../venv/bin/activate
    alembic upgrade head
    cd ../..
" || { echo "❌ Falha no SSH (pull/migrations)"; exit 1; }

echo "📤 3. Enviando .next para VM (tar+ssh, mais leve que rsync)..."
# Tar+ssh usa menos memória no remoto que rsync; remove .next antigo antes
ssh -o ServerAliveInterval=30 -o ConnectTimeout=30 "$VM_HOST" "rm -rf $VM_PATH/app_dev/frontend/.next.old 2>/dev/null; mv $VM_PATH/app_dev/frontend/.next $VM_PATH/app_dev/frontend/.next.old 2>/dev/null; mkdir -p $VM_PATH/app_dev/frontend/.next"
tar czf - -C app_dev/frontend .next | ssh -o ServerAliveInterval=30 -o ConnectTimeout=60 "$VM_HOST" "cd $VM_PATH/app_dev/frontend && tar xzf -"
ssh "$VM_HOST" "rm -rf $VM_PATH/app_dev/frontend/.next.old"
echo "✅ .next enviado"

echo ""
echo "🔄 4. Reiniciando frontend (porta 3003)..."
ssh -o ConnectTimeout=10 "$VM_HOST" "
    pkill -f 'next start -p 3003' 2>/dev/null || true
    sleep 2
    cd $VM_PATH/app_dev/frontend
    sudo -u deploy nohup npm run start -- -p 3003 > /tmp/finup-frontend.log 2>&1 &
    sleep 5
    grep -q Ready /tmp/finup-frontend.log 2>/dev/null && echo '✅ Frontend OK' || tail -5 /tmp/finup-frontend.log
"

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "   Branch: $BRANCH"
echo "   https://meufinup.com.br"
echo "   https://meufinup.com.br/mobile/dashboard"
