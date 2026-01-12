#!/bin/bash
# ==========================================
# Docker Entrypoint - Sistema de Finanças v4
# ==========================================
# 
# Inicializa backend FastAPI + frontend Next.js
# Cria banco de dados se não existir
# Roda migrations
# 
# Uso: docker-entrypoint.sh [start|bash]
# ==========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Sistema de Finanças v4 - Iniciando${NC}"
echo -e "${GREEN}===========================================${NC}"

# ==========================================
# 1. Verificar variáveis de ambiente obrigatórias
# ==========================================
echo -e "${YELLOW}[1/5]${NC} Verificando variáveis de ambiente..."

if [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}ERRO: SECRET_KEY não definida!${NC}"
    echo "Defina via -e SECRET_KEY=... ou no .env"
    exit 1
fi

if [ -z "$DATABASE_PATH" ]; then
    echo -e "${YELLOW}WARN: DATABASE_PATH não definida, usando padrão${NC}"
    export DATABASE_PATH="/var/lib/financas/db/financas.db"
fi

echo -e "${GREEN}✓ Variáveis OK${NC}"

# ==========================================
# 2. Criar diretórios necessários
# ==========================================
echo -e "${YELLOW}[2/5]${NC} Criando diretórios..."

mkdir -p "$(dirname "$DATABASE_PATH")"
mkdir -p /var/lib/financas/uploads
mkdir -p /var/lib/financas/backups
mkdir -p /app/backend/logs

echo -e "${GREEN}✓ Diretórios criados${NC}"

# ==========================================
# 3. Inicializar banco de dados
# ==========================================
echo -e "${YELLOW}[3/5]${NC} Verificando banco de dados..."

cd /app/backend

if [ ! -f "$DATABASE_PATH" ]; then
    echo -e "${YELLOW}Banco não existe, criando...${NC}"
    python -c "
from app.core.database import engine, Base
from app.domains.users.models import User
from app.domains.users.service import hash_password
from sqlalchemy.orm import Session
from datetime import datetime

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Criar admin padrão
db = Session(bind=engine)
try:
    admin = User(
        email='admin@financas.com',
        password_hash=hash_password('admin123'),
        nome='Administrador',
        role='admin',
        ativo=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(admin)
    db.commit()
    print('✓ Admin criado: admin@financas.com / admin123')
except Exception as e:
    print(f'Erro ao criar admin: {e}')
    db.rollback()
finally:
    db.close()
"
    echo -e "${GREEN}✓ Banco criado e inicializado${NC}"
else
    echo -e "${GREEN}✓ Banco já existe${NC}"
fi

# ==========================================
# 4. Iniciar Backend (FastAPI)
# ==========================================
echo -e "${YELLOW}[4/5]${NC} Iniciando Backend (porta 8000)..."

cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend iniciado (PID: $BACKEND_PID)${NC}"

# ==========================================
# 5. Iniciar Frontend (Next.js)
# ==========================================
echo -e "${YELLOW}[5/5]${NC} Iniciando Frontend (porta 3000)..."

cd /app/frontend
npm start &
FRONTEND_PID=$!

echo -e "${GREEN}✓ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

# ==========================================
# Finalização
# ==========================================
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}✓ Sistema iniciado com sucesso!${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo -e "Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "Login padrão: ${YELLOW}admin@financas.com${NC} / ${YELLOW}admin123${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Altere a senha padrão após primeiro login!${NC}"
echo ""

# ==========================================
# Trap para capturar SIGTERM e fazer shutdown graceful
# ==========================================
trap "echo 'Parando serviços...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGTERM SIGINT

# Manter container rodando e exibir logs
wait $BACKEND_PID $FRONTEND_PID
