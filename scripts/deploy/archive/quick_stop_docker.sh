#!/bin/bash
#
# Quick Stop - Docker Version
# Para todos os containers (mantém dados nos volumes)
#

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"

echo -e "${YELLOW}🛑 Parando containers Docker...${NC}"

# Navegar para raiz do projeto
cd "$PROJECT_ROOT"

# Parar containers (mantém volumes)
docker-compose down

echo -e "${GREEN}✅ Containers parados!${NC}"
echo -e "${YELLOW}ℹ️  Dados preservados nos volumes Docker${NC}"
echo ""
echo "Para iniciar novamente: ./scripts/deploy/quick_start_docker.sh"
echo "Para remover volumes:   docker-compose down -v"
echo ""
