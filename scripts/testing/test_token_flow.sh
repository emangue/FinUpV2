#!/bin/bash

# ============================================================================
# Script de Teste - Fluxo de Token JWT
# Simula login e requisições para validar se token está funcionando
# ============================================================================

set -e  # Parar em caso de erro

echo "🔐 TESTE DE FLUXO DE TOKEN JWT"
echo "======================================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs
BACKEND_URL="http://localhost:8000"
LOGIN_URL="$BACKEND_URL/api/v1/auth/login"
RESUMO_URL="$BACKEND_URL/api/v1/investimentos/resumo"

echo "📝 TESTE 1: Login com usuário teste"
echo "----------------------------------------------------------------------"
echo "POST $LOGIN_URL"
echo '{"email": "teste@email.com", "password": "teste123"}'
echo ""

# Fazer login e capturar token
LOGIN_RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@email.com", "password": "teste123"}')

# Extrair token usando jq (se disponível) ou grep
if command -v jq &> /dev/null; then
  TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
  USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.id')
  USER_EMAIL=$(echo "$LOGIN_RESPONSE" | jq -r '.user.email')
else
  # Fallback sem jq
  TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  USER_ID=$(echo "$LOGIN_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)
  USER_EMAIL=$(echo "$LOGIN_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4 | head -1)
fi

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
  echo -e "${RED}❌ ERRO: Login falhou ou token não retornado${NC}"
  echo "Response:"
  echo "$LOGIN_RESPONSE" | head -20
  exit 1
fi

echo -e "${GREEN}✅ Login bem-sucedido${NC}"
echo "   User ID:  $USER_ID"
echo "   Email:    $USER_EMAIL"
echo "   Token:    ${TOKEN:0:30}..."
echo ""

echo "📝 TESTE 2: Requisição SEM token (deve retornar dados do admin)"
echo "----------------------------------------------------------------------"
echo "GET $RESUMO_URL"
echo "Authorization: (nenhum)"
echo ""

RESUMO_SEM_TOKEN=$(curl -s "$RESUMO_URL")

if command -v jq &> /dev/null; then
  TOTAL_SEM_TOKEN=$(echo "$RESUMO_SEM_TOKEN" | jq -r '.total_investido // "ERRO"')
else
  TOTAL_SEM_TOKEN=$(echo "$RESUMO_SEM_TOKEN" | grep -o '"total_investido":"[^"]*' | cut -d'"' -f4)
fi

echo "Response:"
echo "$RESUMO_SEM_TOKEN" | head -10
echo ""

if [[ "$TOTAL_SEM_TOKEN" == *"1226805"* ]] || [[ "$TOTAL_SEM_TOKEN" == *"1.226"* ]]; then
  echo -e "${YELLOW}⚠️  SEM TOKEN: Retornou dados do admin (fallback user_id=1)${NC}"
  echo "   Total: $TOTAL_SEM_TOKEN (admin)"
else
  echo -e "   Total: $TOTAL_SEM_TOKEN"
fi
echo ""

echo "📝 TESTE 3: Requisição COM token (deve retornar dados do teste)"
echo "----------------------------------------------------------------------"
echo "GET $RESUMO_URL"
echo "Authorization: Bearer ${TOKEN:0:30}..."
echo ""

RESUMO_COM_TOKEN=$(curl -s "$RESUMO_URL" \
  -H "Authorization: Bearer $TOKEN")

if command -v jq &> /dev/null; then
  TOTAL_COM_TOKEN=$(echo "$RESUMO_COM_TOKEN" | jq -r '.total_investido // "ERRO"')
  USER_ID_RESPONSE=$(echo "$RESUMO_COM_TOKEN" | jq -r '.user_id // "N/A"')
else
  TOTAL_COM_TOKEN=$(echo "$RESUMO_COM_TOKEN" | grep -o '"total_investido":"[^"]*' | cut -d'"' -f4)
  USER_ID_RESPONSE="N/A"
fi

echo "Response:"
echo "$RESUMO_COM_TOKEN" | head -10
echo ""

# Validar se retornou dados corretos (teste = ~235k, admin = ~1.226k)
if [[ "$TOTAL_COM_TOKEN" == *"235"* ]] || [[ "$TOTAL_COM_TOKEN" == *"235413"* ]]; then
  echo -e "${GREEN}✅ COM TOKEN: Retornou dados do TESTE (user_id=4)${NC}"
  echo "   Total: $TOTAL_COM_TOKEN (teste - CORRETO)"
  TESTE_TOKEN_OK=1
elif [[ "$TOTAL_COM_TOKEN" == *"1226"* ]] || [[ "$TOTAL_COM_TOKEN" == *"1.226"* ]]; then
  echo -e "${RED}❌ COM TOKEN: Ainda retornando dados do ADMIN (fallback)${NC}"
  echo "   Total: $TOTAL_COM_TOKEN (admin - ERRADO)"
  TESTE_TOKEN_OK=0
else
  echo -e "${YELLOW}⚠️  Total inesperado: $TOTAL_COM_TOKEN${NC}"
  TESTE_TOKEN_OK=0
fi
echo ""

echo "======================================================================"
echo "📊 RESUMO DOS TESTES"
echo "======================================================================"
echo ""
echo "1. Login:                    ✅ Sucesso (token obtido)"
echo "2. Request sem token:        ⚠️  Fallback para admin (esperado)"

if [ "$TESTE_TOKEN_OK" -eq 1 ]; then
  echo -e "3. Request com token:        ${GREEN}✅ Retornou dados do teste${NC}"
  echo ""
  echo -e "${GREEN}🎉 SUCESSO! Token está funcionando corretamente${NC}"
  echo ""
  echo "Próximos passos:"
  echo "  1. Abrir http://localhost:3000/login no navegador"
  echo "  2. Login: teste@email.com / teste123"
  echo "  3. Verificar console.log (F12) com mensagens '[api-client]' e '[AuthContext]'"
  echo "  4. Acessar investimentos e verificar R$ 235.413,03 (não R$ 1.226.805,43)"
  echo ""
  exit 0
else
  echo -e "3. Request com token:        ${RED}❌ Ainda retornando admin${NC}"
  echo ""
  echo -e "${RED}🚨 FALHA! Token não está sendo reconhecido pelo backend${NC}"
  echo ""
  echo "Debug necessário:"
  echo "  1. Verificar logs do backend: tail -f backend.log | grep -i 'auth\|token'"
  echo "  2. Verificar se dependência get_current_user_id_optional está sendo usada"
  echo "  3. Testar endpoint /api/v1/auth/me com token"
  echo "  4. Verificar se extract_user_id_from_token() está funcionando"
  echo ""
  echo "Teste manual com curl:"
  echo "  curl -H 'Authorization: Bearer $TOKEN' $BACKEND_URL/api/v1/auth/me"
  echo ""
  exit 1
fi
