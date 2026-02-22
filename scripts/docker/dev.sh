#!/bin/bash

# ============================================
# Script de Desenvolvimento Docker
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 FinUp - Ambiente Docker de Desenvolvimento${NC}"
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    echo "Inicie o Docker Desktop e tente novamente."
    exit 1
fi

# Função de ajuda
show_help() {
    cat << EOF
Uso: ./scripts/docker/dev.sh [COMANDO]

Comandos disponíveis:
  up          Subir todos os serviços (padrão)
  down        Parar todos os serviços
  restart     Reiniciar todos os serviços
  build       Rebuild imagens
  logs        Ver logs em tempo real
  logs-app    Logs do frontend app
  logs-admin  Logs do frontend admin
  logs-back   Logs do backend
  ps          Status dos containers
  exec-back   Acessar shell do backend
  exec-db     Acessar PostgreSQL
  clean       Limpar tudo (CUIDADO: apaga volumes!)
  help        Mostrar esta ajuda

Exemplos:
  ./scripts/docker/dev.sh up
  ./scripts/docker/dev.sh logs
  ./scripts/docker/dev.sh exec-back
EOF
}

# Comando padrão
COMMAND=${1:-up}

case "$COMMAND" in
    up)
        echo -e "${GREEN}▶️  Subindo containers...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✅ Containers rodando!${NC}"
        echo ""
        echo "URLs de acesso:"
        echo -e "  ${GREEN}App Principal:${NC}  http://localhost:3000"
        echo -e "  ${YELLOW}Painel Admin:${NC}   http://localhost:3001"
        echo -e "  ${GREEN}Backend API:${NC}    http://localhost:8000/docs"
        echo -e "  ${GREEN}Health Check:${NC}   http://localhost:8000/api/health"
        echo ""
        echo "Ver logs: ./scripts/docker/dev.sh logs"
        ;;
    down)
        echo -e "${YELLOW}⏹️  Parando containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Containers parados${NC}"
        ;;
    restart)
        echo -e "${YELLOW}🔄 Reiniciando containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}✅ Containers reiniciados${NC}"
        ;;
    build)
        echo -e "${GREEN}🔨 Rebuilding imagens...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Build concluído${NC}"
        ;;
    logs)
        echo -e "${GREEN}📋 Logs em tempo real (Ctrl+C para sair)${NC}"
        docker-compose logs -f
        ;;
    logs-app)
        echo -e "${GREEN}📋 Logs do Frontend App${NC}"
        docker-compose logs -f frontend-app
        ;;
    logs-admin)
        echo -e "${YELLOW}📋 Logs do Frontend Admin${NC}"
        docker-compose logs -f frontend-admin
        ;;
    logs-back)
        echo -e "${GREEN}📋 Logs do Backend${NC}"
        docker-compose logs -f backend
        ;;
    ps)
        echo -e "${GREEN}📊 Status dos containers${NC}"
        docker-compose ps
        ;;
    exec-back)
        echo -e "${GREEN}🐚 Acessando shell do backend...${NC}"
        docker-compose exec backend /bin/bash
        ;;
    exec-db)
        echo -e "${GREEN}🐘 Acessando PostgreSQL...${NC}"
        docker-compose exec postgres psql -U finup_user -d finup_db_dev
        ;;
    clean)
        echo -e "${RED}⚠️  ATENÇÃO: Isso vai apagar TODOS os volumes (dados do banco!)${NC}"
        read -p "Tem certeza? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            echo -e "${GREEN}✅ Volumes removidos${NC}"
        else
            echo "Operação cancelada"
        fi
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconhecido: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
