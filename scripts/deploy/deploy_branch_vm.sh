#!/bin/bash

# Deploy branch atual na VM (ex: feature/revisao-completa-do-app)
# Uso: ./scripts/deploy/deploy_branch_vm.sh

set -e

BRANCH=$(git branch --show-current)
echo "🚀 DEPLOY BRANCH: $BRANCH"
echo "========================================"

if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute da raiz do projeto!"
    exit 1
fi

# Apenas mudanças em arquivos rastreados (ignora untracked)
if [ -n "$(git status --porcelain -uno)" ]; then
    echo "⚠️  Há mudanças não commitadas em arquivos rastreados. Commit e push primeiro."
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

echo "🚀 Deploy no servidor..."
ssh -o ConnectTimeout=10 minha-vps-hostinger "
    set -e
    cd /var/www/finup || exit 1

    echo '📥 Backup PostgreSQL...'
    pg_dump -U finup_user finup_db > backup_pre_deploy_\$(date +%Y%m%d_%H%M).sql 2>/dev/null || echo '   (ignorado se pg_dump não disponível)'

    echo '📥 Git fetch e checkout...'
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH

    echo '🗄️  Migrations...'
    cd app_dev/backend
    source venv/bin/activate 2>/dev/null || source ../../venv/bin/activate
    alembic upgrade head
    cd ../..

    echo '📦 Frontend - build (NODE_OPTIONS para evitar OOM)...'
    cd app_dev/frontend
    npm ci --quiet
    NODE_OPTIONS=--max-old-space-size=4096 npm run build
    cd ../..

    echo '🔄 Reiniciando frontend (porta 3003, sem systemctl)...'
    pkill -f 'next start -p 3003' 2>/dev/null || true
    sleep 2
    cd app_dev/frontend
    sudo -u deploy nohup npm run start -- -p 3003 > /tmp/finup-frontend.log 2>&1 &
    sleep 5
    if grep -q Ready /tmp/finup-frontend.log 2>/dev/null; then
        echo '✅ Frontend OK'
    else
        tail -5 /tmp/finup-frontend.log
    fi

    echo '🏥 Health check backend...'
    if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        echo '✅ Backend OK'
    else
        echo '⚠️  Backend pode precisar restart manual'
    fi

    echo '✅ Deploy concluído!'
"

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "   Branch: $BRANCH"
echo "   https://meufinup.com.br"
echo "   https://meufinup.com.br/mobile/dashboard"
