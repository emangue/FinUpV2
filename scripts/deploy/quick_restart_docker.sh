#!/bin/bash
#
# Quick Restart - Docker Version
# Reinicia todos os containers
#

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"

echo -e "${YELLOW}🔄 Reiniciando containers Docker...${NC}"

# Navegar para raiz do projeto
cd "$PROJECT_ROOT"

# Reiniciar
docker-compose restart

echo ""
echo -e "${GREEN}✅ Containers reiniciados!${NC}"
echo ""
echo "📋 Ver status: docker-compose ps"
echo "📋 Ver logs:   docker-compose logs -f"
echo ""
