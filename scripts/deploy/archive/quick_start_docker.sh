#!/bin/bash
#
# Quick Start - Docker Version
# Inicia todos os containers (backend, frontend app, frontend admin, postgres, redis)
#

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"

echo -e "${GREEN}🐳 Iniciando ambiente Docker...${NC}"

# Navegar para raiz do projeto
cd "$PROJECT_ROOT"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    echo -e "${YELLOW}   Abra o Docker Desktop e tente novamente.${NC}"
    exit 1
fi

# Iniciar containers
echo -e "${YELLOW}📦 Iniciando containers...${NC}"
docker-compose up -d

# Aguardar health checks
echo -e "${YELLOW}⏳ Aguardando serviços ficarem prontos...${NC}"
sleep 5

# Verificar status
echo ""
echo -e "${GREEN}📊 Status dos containers:${NC}"
docker-compose ps

# Verificar health do backend
echo ""
echo -e "${YELLOW}🧪 Testando backend...${NC}"
sleep 3
HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null || echo "erro")

if [[ $HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Backend: OK${NC}"
else
    echo -e "${RED}⚠️  Backend ainda iniciando... aguarde mais alguns segundos${NC}"
fi

echo ""
echo -e "${GREEN}✅ Ambiente Docker iniciado!${NC}"
echo ""
echo "📱 URLs disponíveis:"
echo "   - Frontend App:   http://localhost:3000"
echo "   - Frontend Admin: http://localhost:3001"
echo "   - Backend API:    http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo ""
echo "🔐 Login padrão:"
echo "   Email: admin@financas.com"
echo "   Senha: Admin123!"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver logs:       docker-compose logs -f [backend|frontend-app|frontend-admin]"
echo "   - Parar tudo:     ./scripts/deploy/quick_stop_docker.sh"
echo "   - Reiniciar:      ./scripts/deploy/quick_restart_docker.sh"
echo ""
