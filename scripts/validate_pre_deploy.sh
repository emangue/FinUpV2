#!/bin/bash
# Script de Validação Pré-Deploy
# Verifica se a estrutura está correta antes de fazer deploy

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🔍 Validação Pré-Deploy - Sistema de Gestão Financeira${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Função para erro
error() {
    echo -e "${RED}❌ $1${NC}"
    ERRORS=$((ERRORS + 1))
}

# Função para warning
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

# Função para sucesso
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo -e "${BLUE}📁 Verificando estrutura de diretórios...${NC}"
echo ""

# Verificar app/
if [ -d "app/" ]; then
    success "app/ existe"
else
    error "app/ não existe"
fi

# Verificar subpastas de app/
if [ -d "app/blueprints/" ]; then
    success "app/blueprints/ existe"
else
    error "app/blueprints/ não existe"
fi

if [ -d "app/utils/" ]; then
    success "app/utils/ existe"
else
    error "app/utils/ não existe"
fi

if [ -d "app/templates/" ]; then
    success "app/templates/ existe"
else
    error "app/templates/ não existe"
fi

if [ -d "app/static/" ]; then
    success "app/static/ existe"
else
    error "app/static/ não existe"
fi

echo ""
echo -e "${BLUE}📄 Verificando arquivos críticos...${NC}"
echo ""

# Arquivos da aplicação
[ -f "app/run.py" ] && success "app/run.py existe" || error "app/run.py não existe"
[ -f "app/__init__.py" ] && success "app/__init__.py existe" || error "app/__init__.py não existe"
[ -f "app/models.py" ] && success "app/models.py existe" || error "app/models.py não existe"
[ -f "app/config.py" ] && success "app/config.py existe" || error "app/config.py não existe"

# Arquivos de configuração
[ -f "requirements.txt" ] && success "requirements.txt existe" || error "requirements.txt não existe"
[ -f "VERSION.md" ] && success "VERSION.md existe" || warning "VERSION.md não existe na raiz"

echo ""
echo -e "${BLUE}🗄️  Verificando banco de dados...${NC}"
echo ""

if [ -f "app/financas.db" ]; then
    success "app/financas.db existe"
    
    # Verificar se tem usuários
    USER_COUNT=$(sqlite3 app/financas.db "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    if [ "$USER_COUNT" -gt 0 ]; then
        success "Banco contém $USER_COUNT usuário(s)"
    else
        warning "Banco sem usuários - admin será criado no deploy"
    fi
else
    error "app/financas.db não existe"
fi

echo ""
echo -e "${BLUE}🚫 Verificando que DEV não será deployado...${NC}"
echo ""

if [ -d "app_dev/" ]; then
    warning "app_dev/ existe localmente (OK - será excluído no rsync)"
    
    # Verificar se está no exclude do script
    if grep -q "exclude 'app_dev/'" deployment_scripts/deploy_hostinger.sh 2>/dev/null; then
        success "app_dev/ está no exclude do rsync"
    else
        error "app_dev/ NÃO está no exclude do rsync - SERÁ ENVIADO!"
    fi
else
    success "app_dev/ não existe (deploy de produção pura)"
fi

echo ""
echo -e "${BLUE}📦 Verificando scripts de deploy...${NC}"
echo ""

[ -f "deployment_scripts/deploy_hostinger.sh" ] && success "Script de deploy existe" || error "Script de deploy não existe"
[ -f "scripts/create_admin_user.py" ] && success "Script de criação de admin existe" || warning "Script de admin não existe"

echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📊 Resumo da Validação${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Perfeito! Nenhum erro ou warning.${NC}"
    echo -e "${GREEN}✅ Sistema pronto para deploy!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) encontrado(s)${NC}"
    echo -e "${YELLOW}⚠️  Deploy pode continuar, mas revise os warnings${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS erro(s) crítico(s) encontrado(s)${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) também encontrado(s)${NC}"
    fi
    echo -e "${RED}❌ NÃO FAÇA DEPLOY até corrigir os erros!${NC}"
    exit 1
fi
