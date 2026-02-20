#!/bin/bash

# Deploy app_dev (BAU) - git pull + build frontend + restart
# Uso: ./scripts/deploy/deploy_app_dev.sh

set -e

echo "🚀 DEPLOY APP_DEV (BAU)"
echo "========================================"

if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute da raiz do projeto!"
    exit 1
fi

# Verificar git
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Há mudanças não commitadas. Commit e push primeiro."
    git status --short
    exit 1
fi

git fetch origin main --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Execute: git push origin main"
    exit 1
fi

echo "✅ Git OK (${LOCAL:0:7})"
echo ""

echo "🚀 Deploy no servidor..."
ssh -o ConnectTimeout=10 minha-vps-hostinger "
    set -e
    cd /var/www/finup || exit 1
    
    echo '📥 Git pull...'
    # Remover arquivos untracked que conflitam com o merge (ex: criados manualmente no servidor)
    rm -f scripts/database/reset_teste_copiar_admin_10x.py 2>/dev/null || true
    git pull origin main || exit 1
    
    echo '🗄️  Migração grupos (Aplicações→Investimentos, Fatura→Transferência)...'
    PY=python3
    [ -x app_dev/backend/venv/bin/python3 ] && PY=app_dev/backend/venv/bin/python3
    [ -x app_dev/venv/bin/python3 ] && PY=app_dev/venv/bin/python3
    (\$PY scripts/migration/migrate_grupos_producao.py) || echo '   (ignorado se já migrado ou sem DATABASE_URL)'
    
    echo '📦 Frontend - build...'
    cd app_dev/frontend
    npm ci --quiet
    npm run build
    cd ../..
    
    echo '🔄 Reiniciando serviços...'
    systemctl restart finup-backend finup-frontend
    
    echo '⏳ Aguardando inicialização (10s)...'
    sleep 10
    
    echo '🏥 Health check (retry 3x)...'
    for i in 1 2 3; do
      if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        echo '✅ Backend OK'
        break
      fi
      if [ \$i -eq 3 ]; then
        echo '❌ Backend health falhou após 3 tentativas'
        echo '📋 Logs:'
        journalctl -u finup-backend -n 15 --no-pager
        exit 1
      fi
      echo \"   Tentativa \$i falhou, aguardando 3s...\"
      sleep 3
    done
    
    echo '✅ Deploy concluído!'
"

echo ""
echo "🎉 APP_DEV DEPLOYADO!"
echo "   https://meufinup.com.br"
echo "   https://meufinup.com.br/mobile/dashboard"
