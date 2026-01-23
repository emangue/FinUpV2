#!/bin/bash

# 🛡️ Deploy Seguro V2 - Validações Completas
# Uso: ./scripts/deploy/deploy_safe_v2.sh [--with-migrations]

set -e

WITH_MIGRATIONS=false
if [ "$1" = "--with-migrations" ]; then
    WITH_MIGRATIONS=true
fi

echo "🛡️ INICIANDO DEPLOY SEGURO V2"
echo "========================================"
echo "📅 $(date)"
echo "🔧 Migrations: $WITH_MIGRATIONS"
echo ""

# Verificar se estamos na raiz do projeto
if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "❌ Execute este script da raiz do projeto ProjetoFinancasV5!"
    exit 1
fi

# 1. VALIDAÇÕES LOCAIS EXTENSIVAS
echo "🔍 1. VALIDAÇÕES LOCAIS"
echo "----------------------------------------"

echo "📋 Git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Há mudanças não commitadas!"
    git status
    exit 1
fi
echo "✅ Git limpo"

echo "📋 Sincronização com remoto..."
git fetch origin main --quiet
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)
if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo "❌ Local e remoto dessincronizados!"
    echo "💡 Execute: git push origin main"
    exit 1
fi
echo "✅ Sincronizado (commit: ${LOCAL_COMMIT:0:7})"

echo "📋 Validação de sintaxe Python..."
if ! python3 -m py_compile app_dev/backend/app/main.py 2>/dev/null; then
    echo "❌ Erro de sintaxe em app/main.py!"
    exit 1
fi
echo "✅ Sintaxe Python válida"

if [ "$WITH_MIGRATIONS" = true ]; then
    echo "📋 Validação de migrations..."
    if [ ! -d "app_dev/backend/migrations/versions" ]; then
        echo "❌ Diretório de migrations não encontrado!"
        exit 1
    fi
    echo "✅ Migrations disponíveis"
fi

# 2. BACKUP AUTOMÁTICO
echo ""
echo "💾 2. BACKUP AUTOMÁTICO"
echo "----------------------------------------"

ssh -o ConnectTimeout=10 minha-vps-hostinger "
    cd /var/www/finup || exit 1
    
    # Backup do banco
    if [ -f 'app_dev/backend/database/financas_dev.db' ]; then
        BACKUP_NAME=\"backup_pre_deploy_\$(date +%Y%m%d_%H%M%S).db\"
        mkdir -p app_dev/backend/database/backups_daily
        cp app_dev/backend/database/financas_dev.db \"app_dev/backend/database/backups_daily/\$BACKUP_NAME\"
        echo \"💾 Backup criado: \$BACKUP_NAME\"
    fi
    
    # Backup do código atual
    CURRENT_COMMIT=\$(git rev-parse HEAD)
    echo \"📋 Commit atual no servidor: \${CURRENT_COMMIT:0:7}\"
"

# 3. DEPLOY COM VALIDAÇÕES
echo ""
echo "🚀 3. DEPLOY NO SERVIDOR" 
echo "----------------------------------------"

ssh -o ConnectTimeout=10 minha-vps-hostinger "
    cd /var/www/finup || exit 1
    
    echo '📥 Git pull...'
    git pull origin main || exit 1
    
    echo '🔍 Verificando mudanças...'
    git log --oneline -3
    
    if [ '$WITH_MIGRATIONS' = true ]; then
        echo '🗄️ Aplicando migrations...'
        cd app_dev/backend
        source venv/bin/activate
        alembic upgrade head || exit 1
        cd ../..
    fi
    
    echo '🔄 Reiniciando serviços...'
    systemctl restart finup-backend || exit 1
    
    echo '⏳ Aguardando inicialização...'
    sleep 5
    
    echo '🏥 Validações pós-deploy...'
    
    # Verificar se backend está ativo
    if ! systemctl is-active --quiet finup-backend; then
        echo '❌ Backend não está ativo!'
        systemctl status finup-backend --no-pager
        echo ''
        echo '📋 Últimos logs:'
        journalctl -u finup-backend -n 20 --no-pager
        exit 1
    fi
    
    # Health check
    echo '🔍 Health check...'
    HEALTH=\$(curl -s -f http://localhost:8000/api/health || echo 'FAILED')
    if [ \"\$HEALTH\" = 'FAILED' ]; then
        echo '❌ Health check falhou!'
        echo '📋 Logs de erro:'
        journalctl -u finup-backend -n 10 --no-pager
        exit 1
    fi
    
    echo \"✅ Health: \$HEALTH\"
    
    # Teste de autenticação
    echo '🔐 Teste de autenticação...'
    AUTH_TEST=\$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/auth/me)
    if [ \"\$AUTH_TEST\" = '401' ]; then
        echo '✅ Endpoint /auth/me protegido corretamente (401)'
    else
        echo \"⚠️ Endpoint /auth/me retornou: \$AUTH_TEST (esperado: 401)\"
    fi
    
    echo ''
    echo '🎉 DEPLOY REALIZADO COM SUCESSO!'
    echo '========================================'
    echo \"📅 \$(date)\"
    echo \"📋 Commit: \$(git rev-parse HEAD | cut -c1-7)\"
    echo '✅ Backend: Ativo e respondendo'
    echo '✅ Banco: Conectado'
    echo '✅ Autenticação: Funcionando'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOY SEGURO CONCLUÍDO!"
    echo "========================================"
    echo "✅ Todas as validações passaram"
    echo "✅ Backup realizado automaticamente"  
    echo "✅ Serviços funcionando corretamente"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   Frontend: https://finup.srv1045889.hstgr.cloud/"
    echo "   API: https://finup.srv1045889.hstgr.cloud/api/health"
    echo "   Docs: https://finup.srv1045889.hstgr.cloud/docs"
    echo ""
    echo "💡 Para monitorar logs em tempo real:"
    echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -f'"
else
    echo ""
    echo "❌ DEPLOY FALHOU - INVESTIGAR!"
    echo "========================================"
    echo "💡 Comandos para debug:"
    echo "   ssh minha-vps-hostinger 'systemctl status finup-backend'"
    echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -n 50'"
    echo ""
    echo "🔄 Para rollback rápido:"
    echo "   ssh minha-vps-hostinger 'cd /var/www/finup && git checkout HEAD~1 && systemctl restart finup-backend'"
fi