#!/bin/bash
# Script de Validação de Sincronização Local ↔️ Servidor
# Garante que servidor nunca tem mudanças que local não tem

set -e

echo "🔍 VALIDAÇÃO DE SINCRONIZAÇÃO - $(date)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVER="root@148.230.78.91"
SERVER_PATH="/var/www/finup"

# 1. Verificar commits
echo "📊 1/5 - Verificando commits..."
LOCAL_COMMIT=$(git log --oneline -1 | awk '{print $1}')
SERVER_COMMIT=$(ssh $SERVER "cd $SERVER_PATH && git log --oneline -1" | awk '{print $1}')

echo "   Local:    $LOCAL_COMMIT"
echo "   Servidor: $SERVER_COMMIT"

if [ "$LOCAL_COMMIT" == "$SERVER_COMMIT" ]; then
    echo -e "   ${GREEho ""

# 2. Verificar mudanças locais não-commitadas
echo "📝 2/5 - Verificando mudanças locais..."
if git diff-index --quiet HEAD --; then
    echo -e "   ${GREEN}✅ Nenhuma mudança não-commitada localmente${NC}"
else
    echo -e "   ${YELLOW}⚠️  Existem mudanças não-commitadas${NC}"
    git status --short
    echo "   Ação: Commitar ou descartar mudanças"
fi
echo ""

# 3. Verificar mudanças no servidor
echo "🖥️  3/5 - Verificando mudanças no servidor..."
SERVER_STATUS=$(ssh $SERVER "cd $SERVER_PATH && git status --short" || echo "ERRO")

if [ -z "$SERVER_STATUS" ]; then
    echo -e "   ${GREEN}✅ Nenhuma mudança no servidor${NC}"
elif " ]; then
    echo -e "   ${RED}❌ Erro ao verificar servidor${NC}"
else
    echo -e "   ${RED}❌ SERVIDOR TEM MUDANÇAS NÃO-COMMITADAS!${NC}"
    echo "$SERVER_STATUS"
    echo -e "   ${RED}AÇÃO URGENTE: Alguém editou diretamente no servidor!${NC}"
fi
echo ""

# 4. Verificar dados sensíveis no git
echo "🔒 4/5 - Verificando dados sensíveis no git..."
SENSITIVE_FILES=$(git log --all --full-history -- '**/.env*' '**/*secret*' 2>/dev/null | head -5)

if [ -z "$SENSITIVE_FILES" ]; then
    echo -e "   ${GREEN}✅ Nenhum arquivo sensível no histórico${NC}"
else
    echo -e "   ${RED}❌ ARQUIVOS SENSÍVEIS ENCONTRADOS NO GIT!${NC}"
    echo "$SENSITIVE_FILES"
    echo -e "   ${RED}AÇÃO URGENTE: Remover do histórico e trocar secrets!${NC}"
fi
echo ""

# 5. Verificar .gitignore
echo "🛡️  5/5 - Verificando proteç
if [ -z "$SERVER_STATUS" ]; then
    echo -e "   ${GREEN}✅ Nenhuma mudança no 

if [ "$PROTECTED" -gt 5 ]; then
    echo -e "   ${GREEN}✅ .gitignore protege $PROTECTED tipos de arquivos sensíveis${NC}"
else
    echo -e "   ${YELLOW}⚠️  .gitignore pode estar incompleto ($PROTECTED proteções)${NC}"
fi
echo ""

# Resumo
echo "═══════════════════════════════════════════════════════════════"
if [ "$LOCAL_COMMIT" == "$SERVER_COMMIT" ] && [ -z "$SERVER_STATUS" ] && [ -z "$SENSITIVE_FILES" ]; then
    echo -e "${GREEN}✅ SINCRONIZAÇÃO PERFEITA - Tudo OK!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  ATENÇÃO NECESSÁRIA - Revisar pontos acima${NC}"
    exit 1
fi
