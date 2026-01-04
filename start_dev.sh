#!/bin/bash
# Script de inicialização do ambiente DEV
# Uso: ./start_dev.sh

echo "=============================================="
echo "  🚀 Sistema Financeiro v4.0.0-dev"
echo "=============================================="
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se está no diretório correto
if [ ! -d "app_dev" ]; then
    echo -e "${YELLOW}⚠️  Execute este script da raiz do projeto!${NC}"
    echo "   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4"
    exit 1
fi

echo -e "${BLUE}📦 Verificando ambiente...${NC}"

# Verifica virtualenv
if [ ! -d "app_dev/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtualenv não encontrado. Criando...${NC}"
    cd app_dev
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Verifica node_modules
if [ ! -d "app_dev/frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Dependências do frontend não instaladas. Instalando...${NC}"
    cd app_dev/frontend
    npm install
    cd ../..
fi

# Verifica banco de dados
if [ ! -f "app_dev/financas_dev.db" ]; then
    echo -e "${YELLOW}⚠️  Banco de dados não encontrado. Inicializando...${NC}"
    cd app_dev
    source venv/bin/activate
    python init_db.py
    cd ..
fi

echo ""
echo -e "${GREEN}✅ Ambiente configurado!${NC}"
echo ""
echo "=============================================="
echo "  📋 Comandos para iniciar:"
echo "=============================================="
echo ""
echo -e "${BLUE}Terminal 1 - Backend (porta 8000):${NC}"
echo "  python run_dev_api.py"
echo ""
echo -e "${BLUE}Terminal 2 - Frontend (porta 3000):${NC}"
echo "  cd app_dev/frontend && npm run dev"
echo ""
echo "=============================================="
echo "  🌐 Acesso:"
echo "=============================================="
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000/api/v1"
echo "  Health:    http://localhost:8000/api/health"
echo ""
echo "  Login: admin@email.com / admin123"
echo ""
echo "=============================================="
