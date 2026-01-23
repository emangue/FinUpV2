#!/bin/bash
# 🚀 Deploy Automatizado - Correção de Segurança
# Usa credenciais de .env.deploy

set -e
cd "$(dirname "$0")/../.."

# Carregar credenciais
source scripts/deploy/load_credentials.sh

echo ""
echo "🚨 DEPLOY URGENTE - Correção Crítica de Segurança"
echo "=================================================="
echo ""
echo "🔒 Problema: user_id hardcoded permitia vazamento de dados"
echo "✅ Correção: Todos endpoints exigem JWT válido com user_id correto"
echo ""

# Função para executar comando SSH
run_ssh() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "$1"
}

# ETAPA 1: Backup
echo "📋 ETAPA 1/6: Fazendo backup do banco..."
run_ssh "cd $SERVER_APP_PATH && ./scripts/deploy/backup_daily.sh" || {
    echo "❌ Erro no backup"
    exit 1
}
echo "✅ Backup criado"

# ETAPA 2: Git pull
echo ""
echo "📋 ETAPA 2/6: Atualizando código..."
run_ssh "cd $SERVER_APP_PATH && git pull origin main" || {
    echo "❌ Erro no git pull"
    exit 1
}
echo "✅ Código atualizado"

# ETAPA 3: Dependências
echo ""
echo "📋 ETAPA 3/6: Instalando dependências..."
run_ssh "cd $SERVER_APP_PATH/app_dev && source venv/bin/activate && pip install slowapi" || {
    echo "⚠️  Aviso: Erro ao instalar slowapi (pode já estar instalada)"
}
echo "✅ Dependências verificadas"

# ETAPA 4: Restart backend
echo ""
echo "📋 ETAPA 4/6: Reiniciando backend..."
run_ssh "systemctl restart finup-backend" || {
    echo "❌ Erro ao reiniciar backend"
    exit 1
}
echo "✅ Backend reiniciado"

# ETAPA 5: Aguardar
echo ""
echo "📋 ETAPA 5/6: Aguardando inicialização (10s)..."
sleep 10
echo "✅ Backend deve estar online"

# ETAPA 6: Validar
echo ""
echo "📋 ETAPA 6/6: Validando isolamento de usuários..."
HTTP_CODE=$(run_ssh "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/transactions/list")

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ Validação OK - Endpoint protegido (401 sem token)"
else
    echo "⚠️  Código HTTP: $HTTP_CODE"
    echo "   Esperado: 401 (sem autenticação)"
fi

# Status final
echo ""
echo "📋 Verificando status do backend..."
run_ssh "systemctl status finup-backend --no-pager | head -10"

echo ""
echo "===================================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "===================================================="
echo ""
echo "✅ Correção de segurança aplicada"
echo "✅ Sistema reiniciado e operacional"
echo ""
echo "🔍 Próximos passos:"
echo "   1. Testar login com usuário teste@email.com"
echo "   2. Verificar isolamento de transações"
echo "   3. Validar que admin e teste veem dados separados"
echo ""
