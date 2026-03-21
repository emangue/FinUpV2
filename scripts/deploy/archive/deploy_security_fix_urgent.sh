#!/bin/bash
# 🚨 DEPLOY URGENTE - Correção Crítica de Segurança (user_id hardcoded)
# Data: 23/01/2026
# Severidade: CRÍTICA

set -e  # Para em qualquer erro

echo "🚨 DEPLOY URGENTE - Correção Crítica de Segurança"
echo "=================================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuração do servidor
SERVER="root@64.23.241.43"
APP_PATH="/var/www/finup"

echo "🔒 Problema: user_id hardcoded permitia vazamento de dados entre usuários"
echo "✅ Correção: Todos endpoints agora exigem JWT válido com user_id correto"
echo ""

# Confirmar deploy
read -p "⚠️  Continuar com deploy em produção? (s/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Deploy cancelado"
    exit 1
fi

echo ""
echo "📋 ETAPA 1/7: Verificando conexão SSH..."
if ! ssh -o ConnectTimeout=5 $SERVER "echo 'Conectado'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Não foi possível conectar ao servidor${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Conexão OK${NC}"

echo ""
echo "📋 ETAPA 2/7: Fazendo backup do banco de dados..."
ssh $SERVER "cd $APP_PATH && ./scripts/deploy/backup_daily.sh" || {
    echo -e "${RED}❌ Erro ao fazer backup${NC}"
    exit 1
}
echo -e "${GREEN}✅ Backup criado${NC}"

echo ""
echo "📋 ETAPA 3/7: Verificando branch atual..."
CURRENT_BRANCH=$(ssh $SERVER "cd $APP_PATH && git branch --show-current")
echo "Branch atual: $CURRENT_BRANCH"
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  Atenção: Servidor não está na branch main${NC}"
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Deploy cancelado"
        exit 1
    fi
fi

echo ""
echo "📋 ETAPA 4/7: Puxando código atualizado..."
ssh $SERVER "cd $APP_PATH && git fetch origin && git pull origin main" || {
    echo -e "${RED}❌ Erro ao fazer git pull${NC}"
    exit 1
}
echo -e "${GREEN}✅ Código atualizado${NC}"

echo ""
echo "📋 ETAPA 5/7: Verificando dependências..."
ssh $SERVER "cd $APP_PATH/app_dev && source venv/bin/activate && pip list | grep slowapi" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  slowapi não encontrado, instalando..."
    ssh $SERVER "cd $APP_PATH/app_dev && source venv/bin/activate && pip install slowapi"
fi
echo -e "${GREEN}✅ Dependências OK${NC}"

echo ""
echo "📋 ETAPA 6/7: Reiniciando serviço backend..."
ssh $SERVER "systemctl restart finup-backend" || {
    echo -e "${RED}❌ Erro ao reiniciar backend${NC}"
    echo "Verificando logs..."
    ssh $SERVER "journalctl -u finup-backend -n 30"
    exit 1
}
echo -e "${GREEN}✅ Backend reiniciado${NC}"

# Aguardar backend inicializar
echo ""
echo "⏳ Aguardando backend inicializar (10 segundos)..."
sleep 10

echo ""
echo "📋 ETAPA 7/7: Validando correção de segurança..."

# Teste 1: Sem token (deve retornar 401)
echo -n "  Test 1: Endpoint sem token... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' https://finup.emanuelguerra.me/api/v1/transactions/list")
if [ "$HTTP_CODE" == "401" ]; then
    echo -e "${GREEN}✅ OK (401 Unauthorized)${NC}"
else
    echo -e "${RED}❌ FALHOU (esperado 401, recebido $HTTP_CODE)${NC}"
    exit 1
fi

# Teste 2: Login com usuário teste
echo -n "  Test 2: Login usuário teste... "
LOGIN_RESPONSE=$(ssh $SERVER "curl -s -X POST https://finup.emanuelguerra.me/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"teste@email.com\",\"password\":\"teste123\"}'")
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ OK (token gerado)${NC}"
    
    # Extrair user_id do response
    USER_ID=$(echo "$LOGIN_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "    user_id do teste: $USER_ID"
    
    # Extrair token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    # Teste 3: Transações com token (deve filtrar por user_id correto)
    echo -n "  Test 3: Transações filtradas por user_id... "
    TRANSACTIONS=$(ssh $SERVER "curl -s -H 'Authorization: Bearer $TOKEN' https://finup.emanuelguerra.me/api/v1/transactions/list?limit=5")
    
    if echo "$TRANSACTIONS" | grep -q "transactions"; then
        # Verificar se todos os user_id são iguais ao do login
        USER_IDS=$(echo "$TRANSACTIONS" | grep -o '"user_id":[0-9]*' | cut -d':' -f2 | sort -u)
        if [ "$USER_IDS" == "$USER_ID" ]; then
            echo -e "${GREEN}✅ OK (todas transações com user_id=$USER_ID)${NC}"
        else
            echo -e "${RED}❌ FALHOU (encontrados user_ids diferentes: $USER_IDS)${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ FALHOU (resposta inválida)${NC}"
        echo "Response: $TRANSACTIONS"
        exit 1
    fi
else
    echo -e "${RED}❌ FALHOU (login falhou)${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "=================================================="
echo ""
echo "📊 Resumo:"
echo "  ✅ Backup do banco criado"
echo "  ✅ Código atualizado (git pull)"
echo "  ✅ Backend reiniciado"
echo "  ✅ Validação de segurança: PASSOU"
echo ""
echo "🔒 Correção de segurança aplicada:"
echo "  - Removido user_id=1 hardcoded"
echo "  - JWT obrigatório em todos endpoints"
echo "  - Isolamento de dados validado"
echo ""
echo "📋 Próximos passos:"
echo "  1. Testar login em https://finup.emanuelguerra.me"
echo "  2. Verificar que transações mostram dados corretos"
echo "  3. Monitorar logs: journalctl -u finup-backend -f"
echo ""
echo "📁 Documentação:"
echo "  - docs/planning/VULNERABILIDADE_CRITICA_USER_ID.md"
echo "  - docs/planning/CORRECAO_SEGURANCA_USER_ID_23_01_2026.md"
echo ""
