#!/bin/bash
# Script de Comparação Local vs VM
# Analisa diferenças antes de fazer deploy

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
VM_HOST="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/id_rsa_hostinger"
VM_APP_DIR="/opt/financial-app"
LOCAL_DIR="$(pwd)"

echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🔍 Comparação Local vs VM - Sistema de Gestão Financeira${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""

# Verificar se está na raiz do projeto
if [ ! -f "VERSION.md" ] || [ ! -d "app" ]; then
    echo -e "${RED}❌ ERRO: Execute este script da raiz do projeto!${NC}"
    exit 1
fi

# Verificar conectividade com VM
echo -e "${CYAN}📡 Testando conexão com VM...${NC}"
if ! ssh -i "$SSH_KEY" "$VM_HOST" "echo OK" &>/dev/null; then
    echo -e "${RED}❌ ERRO: Não foi possível conectar à VM${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Conexão estabelecida${NC}"
echo ""

# Pegar versões
echo -e "${CYAN}📌 Verificando versões...${NC}"
LOCAL_VERSION=$(cat VERSION.md 2>/dev/null | head -1 || echo "desconhecida")
VM_VERSION=$(ssh -i "$SSH_KEY" "$VM_HOST" "cat $VM_APP_DIR/VERSION.md 2>/dev/null | head -1" || echo "desconhecida")

echo -e "   Local: ${GREEN}$LOCAL_VERSION${NC}"
echo -e "   VM:    ${YELLOW}$VM_VERSION${NC}"
echo ""

# Criar manifesto local
echo -e "${CYAN}📦 Gerando manifesto local...${NC}"
TEMP_LOCAL="/tmp/local_manifest_$$.txt"
find app/ -type f ! -path "*/\.*" ! -name "*.pyc" ! -name "*.db" | sort > "$TEMP_LOCAL"
LOCAL_FILES=$(wc -l < "$TEMP_LOCAL" | xargs)
echo -e "${GREEN}✅ $LOCAL_FILES arquivos locais mapeados${NC}"
echo ""

# Criar manifesto remoto
echo -e "${CYAN}📦 Gerando manifesto remoto (VM)...${NC}"
TEMP_REMOTE="/tmp/remote_manifest_$$.txt"
ssh -i "$SSH_KEY" "$VM_HOST" "cd $VM_APP_DIR && find app/ -type f ! -path '*/\.*' ! -name '*.pyc' ! -name '*.db' | sort" > "$TEMP_REMOTE"
REMOTE_FILES=$(wc -l < "$TEMP_REMOTE" | xargs)
echo -e "${GREEN}✅ $REMOTE_FILES arquivos remotos mapeados${NC}"
echo ""

# Comparar listas de arquivos
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📊 Análise de Diferenças${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""

# Arquivos novos (existem no local mas não na VM)
NEW_FILES=$(comm -23 "$TEMP_LOCAL" "$TEMP_REMOTE")
NEW_COUNT=$(echo "$NEW_FILES" | grep -v "^$" | wc -l | xargs)

if [ "$NEW_COUNT" -gt 0 ]; then
    echo -e "${GREEN}📄 Arquivos NOVOS ($NEW_COUNT):${NC}"
    echo "$NEW_FILES" | head -20
    if [ "$NEW_COUNT" -gt 20 ]; then
        echo -e "${YELLOW}   ... e mais $((NEW_COUNT - 20)) arquivo(s)${NC}"
    fi
    echo ""
fi

# Arquivos deletados (existem na VM mas não no local)
DELETED_FILES=$(comm -13 "$TEMP_LOCAL" "$TEMP_REMOTE")
DELETED_COUNT=$(echo "$DELETED_FILES" | grep -v "^$" | wc -l | xargs)

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo -e "${RED}🗑️  Arquivos que serão DELETADOS da VM ($DELETED_COUNT):${NC}"
    echo "$DELETED_FILES" | head -20
    if [ "$DELETED_COUNT" -gt 20 ]; then
        echo -e "${YELLOW}   ... e mais $((DELETED_COUNT - 20)) arquivo(s)${NC}"
    fi
    echo ""
fi

# Arquivos comuns (verificar modificações)
COMMON_FILES=$(comm -12 "$TEMP_LOCAL" "$TEMP_REMOTE")
COMMON_COUNT=$(echo "$COMMON_FILES" | grep -v "^$" | wc -l | xargs)

echo -e "${CYAN}🔄 Verificando modificações em arquivos comuns ($COMMON_COUNT)...${NC}"

MODIFIED_COUNT=0
MODIFIED_LIST=""

# Verificar alguns arquivos críticos
CRITICAL_FILES=(
    "app/models.py"
    "app/config.py"
    "app/__init__.py"
    "app/run.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOCAL_HASH=$(md5 -q "$file" 2>/dev/null || md5sum "$file" 2>/dev/null | cut -d' ' -f1)
        REMOTE_HASH=$(ssh -i "$SSH_KEY" "$VM_HOST" "md5sum $VM_APP_DIR/$file 2>/dev/null | cut -d' ' -f1" || echo "")
        
        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
            echo -e "${YELLOW}   ⚠️  MODIFICADO: $file${NC}"
            MODIFIED_COUNT=$((MODIFIED_COUNT + 1))
            MODIFIED_LIST="$MODIFIED_LIST\n   - $file"
        fi
    fi
done

if [ "$MODIFIED_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Nenhuma modificação detectada nos arquivos críticos${NC}"
fi
echo ""

# Verificar banco de dados
echo -e "${CYAN}🗄️  Verificando banco de dados...${NC}"
if [ -f "app/financas.db" ]; then
    LOCAL_DB_SIZE=$(du -h app/financas.db | cut -f1)
    REMOTE_DB_SIZE=$(ssh -i "$SSH_KEY" "$VM_HOST" "du -h $VM_APP_DIR/instance/financas.db 2>/dev/null | cut -f1" || echo "N/A")
    echo -e "   Local:  ${LOCAL_DB_SIZE}"
    echo -e "   Remoto: ${REMOTE_DB_SIZE}"
else
    echo -e "${YELLOW}⚠️  Banco local não encontrado${NC}"
fi
echo ""

# Verificar Git
echo -e "${CYAN}🔀 Verificando status Git...${NC}"
GIT_STATUS=$(git status --short 2>/dev/null || echo "erro")
if [ "$GIT_STATUS" = "erro" ]; then
    echo -e "${RED}❌ Não é um repositório Git${NC}"
elif [ -z "$GIT_STATUS" ]; then
    echo -e "${GREEN}✅ Working tree limpo${NC}"
else
    echo -e "${YELLOW}⚠️  Há mudanças não commitadas:${NC}"
    echo "$GIT_STATUS" | head -5
    if [ $(echo "$GIT_STATUS" | wc -l) -gt 5 ]; then
        echo -e "${YELLOW}   ... e mais mudanças${NC}"
    fi
fi

# Verificar se está sincronizado com remote
git fetch origin main &>/dev/null || true
LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "erro")
REMOTE_COMMIT=$(git rev-parse origin/main 2>/dev/null || echo "erro")

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo -e "${GREEN}✅ Sincronizado com origin/main${NC}"
else
    echo -e "${YELLOW}⚠️  Há commits locais não enviados${NC}"
fi
echo ""

# Limpar arquivos temporários
rm -f "$TEMP_LOCAL" "$TEMP_REMOTE"

# Resumo final
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📋 Resumo${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""
echo -e "Versão Local:         ${GREEN}$LOCAL_VERSION${NC}"
echo -e "Versão VM:            ${YELLOW}$VM_VERSION${NC}"
echo -e "Arquivos Novos:       ${GREEN}$NEW_COUNT${NC}"
echo -e "Arquivos Deletados:   ${RED}$DELETED_COUNT${NC}"
echo -e "Arquivos Modificados: ${YELLOW}$MODIFIED_COUNT${NC} (críticos verificados)"
echo ""

# Decisão
WARNINGS=0
ERRORS=0

if [ -n "$GIT_STATUS" ]; then
    echo -e "${RED}❌ Git tem mudanças não commitadas${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo -e "${RED}❌ Git local não está sincronizado com origin/main${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $DELETED_COUNT arquivo(s) serão deletados da VM${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$MODIFIED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $MODIFIED_COUNT arquivo(s) crítico(s) serão modificados${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo -e "${BLUE}=================================================================================${NC}"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ $ERRORS ERRO(S) CRÍTICO(S) - NÃO FAÇA DEPLOY ATÉ CORRIGIR!${NC}"
    echo -e "${RED}   1. Commit mudanças: git add -A && git commit -m 'mensagem'${NC}"
    echo -e "${RED}   2. Push para remote: git push origin main${NC}"
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS WARNING(S) - REVISE ANTES DE CONTINUAR${NC}"
    echo -e "${YELLOW}   Mudanças significativas serão aplicadas na VM${NC}"
    echo ""
    exit 0
else
    echo -e "${GREEN}✅ Tudo OK - Deploy pode ser realizado com segurança${NC}"
    echo ""
    exit 0
fi
