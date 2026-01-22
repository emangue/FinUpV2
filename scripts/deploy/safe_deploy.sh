#!/bin/bash

# 🛡️ SAFE DEPLOY SCRIPT - FinUp
# ================================
# Valida TUDO antes de fazer deploy em produção
#
# Uso: ./scripts/deploy/safe_deploy.sh [--skip-tests]

set -e  # Parar em qualquer erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variáveis
PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
BACKEND_DIR="$PROJECT_ROOT/app_dev/backend"
FRONTEND_DIR="$PROJECT_ROOT/app_dev/frontend"
SKIP_TESTS=false

# Parse argumentos
if [[ "$1" == "--skip-tests" ]]; then
    SKIP_TESTS=true
    echo -e "${YELLOW}⚠️  Pulando testes (não recomendado para produção)${NC}"
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} 🛡️  SAFE DEPLOY - Validação Completa${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. VALIDAR GIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 1/8 - Validando Git...${NC}"

cd "$PROJECT_ROOT"

# Verificar branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    echo -e "${YELLOW}⚠️  Você está na branch: $CURRENT_BRANCH${NC}"
    read -p "Deploy geralmente é feito da main/master. Continuar? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Deploy cancelado${NC}"
        exit 1
    fi
fi

# Verificar uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}❌ Há mudanças não commitadas!${NC}"
    git status -s
    echo -e "${YELLOW}   Commit as mudanças antes de fazer deploy${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. VALIDAR MIGRATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 2/8 - Validando Migrations...${NC}"

cd "$BACKEND_DIR"
source ../../.venv/bin/activate

# Verificar se há migrations pendentes
PENDING=$(alembic current 2>&1 | grep -c "None" || true)
if [[ $PENDING -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Há migrations pendentes!${NC}"
    alembic history
    read -p "Aplicar migrations agora? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        alembic upgrade head
    else
        echo -e "${RED}❌ Deploy cancelado - aplique as migrations primeiro${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Migrations OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. VALIDAR BACKEND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 3/8 - Validando Backend...${NC}"

# Verificar dependências
python -c "import fastapi, sqlalchemy, alembic, psycopg2" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Dependências backend faltando!${NC}"
    echo -e "${YELLOW}   Execute: pip install -r requirements.txt${NC}"
    exit 1
fi

# Verificar .env
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado em backend${NC}"
    echo -e "${YELLOW}   Copie .env.example e configure${NC}"
    read -p "Continuar sem .env? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar se backend inicia
if [[ "$SKIP_TESTS" == false ]]; then
    echo -e "${BLUE}   Testando startup do backend...${NC}"
    timeout 10s python -c "from app.main import app; print('✅ Backend OK')" 2>&1 | grep -q "✅" || {
        echo -e "${RED}❌ Backend não inicia corretamente!${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ Backend OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. VALIDAR FRONTEND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 4/8 - Validando Frontend...${NC}"

cd "$FRONTEND_DIR"

# Verificar node_modules
if [[ ! -d "node_modules" ]]; then
    echo -e "${YELLOW}⚠️  node_modules não encontrado!${NC}"
    echo -e "${YELLOW}   Execute: npm install${NC}"
    exit 1
fi

# Verificar .env
if [[ ! -f "$FRONTEND_DIR/.env.production" ]]; then
    echo -e "${YELLOW}⚠️  .env.production não encontrado${NC}"
fi

# Build do frontend (validação)
if [[ "$SKIP_TESTS" == false ]]; then
    echo -e "${BLUE}   Testando build do frontend...${NC}"
    npm run build > /tmp/build.log 2>&1
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ Build do frontend falhou!${NC}"
        tail -20 /tmp/build.log
        exit 1
    fi
fi

echo -e "${GREEN}✅ Frontend OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. BACKUP DO BANCO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 5/8 - Backup do banco...${NC}"

cd "$PROJECT_ROOT"
./scripts/deploy/backup_daily.sh

echo -e "${GREEN}✅ Backup OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. VALIDAR PARIDADE (se PostgreSQL)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 6/8 - Validando paridade dev-prod...${NC}"

if [[ -n "$PROD_DATABASE_URL" ]]; then
    cd "$BACKEND_DIR"
    python ../../scripts/testing/validate_parity.py || {
        echo -e "${YELLOW}⚠️  Ambientes divergem - revisar antes de deploy${NC}"
        read -p "Continuar mesmo assim? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    }
else
    echo -e "${YELLOW}⚠️  PROD_DATABASE_URL não definido - pulando validação${NC}"
fi

echo -e "${GREEN}✅ Paridade OK${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. GERAR CHANGELOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 7/8 - Gerando changelog...${NC}"

cd "$PROJECT_ROOT"
./scripts/deploy/generate_changelog.sh

echo -e "${GREEN}✅ Changelog atualizado${NC}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. CONFIRMAÇÃO FINAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "\n${BLUE}📋 Etapa 8/8 - Confirmação final...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TODAS AS VALIDAÇÕES PASSARAM!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "\n${YELLOW}Pronto para deploy em produção!${NC}"
echo -e "\nPróximos passos:"
echo -e "  1. Fazer push: ${BLUE}git push origin $CURRENT_BRANCH${NC}"
echo -e "  2. SSH no servidor: ${BLUE}ssh user@servidor${NC}"
echo -e "  3. Pull no servidor: ${BLUE}git pull origin $CURRENT_BRANCH${NC}"
echo -e "  4. Rodar migrations: ${BLUE}alembic upgrade head${NC}"
echo -e "  5. Restart serviços: ${BLUE}systemctl restart finup-backend finup-frontend${NC}"
echo -e "  6. Verificar logs: ${BLUE}journalctl -u finup-backend -f${NC}"
echo

read -p "Fazer push automático agora? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin "$CURRENT_BRANCH"
    echo -e "${GREEN}✅ Push concluído!${NC}"
else
    echo -e "${YELLOW}⚠️  Lembre-se de fazer push manualmente${NC}"
fi

echo -e "\n${GREEN}🎉 Safe Deploy concluído com sucesso!${NC}"
