#!/bin/bash

# 🚀 Deploy Rápido - Fluxo: LOCAL → GIT → SERVIDOR
# Uso: ./scripts/deploy/quick_deploy.sh

set -e

echo "🚀 INICIANDO DEPLOY RÁPIDO"
echo "========================================"

# Verificar se estamos na raiz do projeto
if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute este script da raiz do projeto ProjetoFinancasV5!"
    exit 1
fi

# 1. VALIDAÇÃO LOCAL
echo "🔍 1. Verificando git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Há mudanças não commitadas:"
    git status --short
    echo ""
    echo "💡 Commit suas mudanças primeiro:"
    echo "   git add ."
    echo "   git commit -m 'sua mensagem'"
    exit 1
fi

echo "✅ Git status limpo"

# 2. VERIFICAR SE ESTÁ SINCRONIZADO
echo "🔍 2. Verificando se local está sincronizado..."
git fetch origin main --quiet

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo "⚠️  Local e remoto estão dessincronizados"
    echo "💡 Execute: git push origin main"
    exit 1
fi

echo "✅ Local sincronizado com GitHub"

# 3. DEPLOY NO SERVIDOR
echo "🚀 3. Fazendo deploy no servidor..."

# SSH config deve estar configurado como 'minha-vps-hostinger'
ssh -o ConnectTimeout=10 minha-vps-hostinger "
    cd /var/www/finup || exit 1
    
    echo '📥 Fazendo git pull...'
    git pull origin main || exit 1
    
    echo '🔄 Reiniciando backend...'
    systemctl restart finup-backend || exit 1
    
    echo '⏳ Aguardando backend inicializar...'
    sleep 3
    
    echo '🔍 Verificando status do backend...'
    if ! systemctl is-active --quiet finup-backend; then
        echo '❌ Backend não iniciou corretamente!'
        systemctl status finup-backend --no-pager
        exit 1
    fi
    
    echo '🏥 Testando health check...'
    if ! curl -s -f http://localhost:8000/api/health >/dev/null; then
        echo '❌ Health check falhou!'
        echo '📋 Últimos logs:'
        journalctl -u finup-backend -n 10 --no-pager
        exit 1
    fi
    
    echo '✅ Deploy concluído com sucesso!'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOY REALIZADO COM SUCESSO!"
    echo "========================================"
    echo "✅ Código sincronizado: LOCAL → GIT → SERVIDOR"
    echo "✅ Backend rodando corretamente"
    echo "✅ Health check passou"
    echo ""
    echo "💡 Acesse: https://finup.srv1045889.hstgr.cloud/"
    echo "💡 API Docs: https://finup.srv1045889.hstgr.cloud/docs"
else
    echo ""
    echo "❌ DEPLOY FALHOU!"
    echo "========================================"
    echo "💡 Verifique os logs no servidor:"
    echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -n 20'"
fi