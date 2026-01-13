#!/bin/bash

# ==========================================
# DEPLOY FINAL - SISTEMA DE FINANÇAS V4
# ==========================================

echo "🚀 Iniciando deploy final..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Função para executar comandos SSH com retry
ssh_exec() {
    local max_attempts=3
    local attempt=1
    local cmd="$1"
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Tentativa $attempt/$max_attempts: $cmd${NC}"
        
        if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o ServerAliveInterval=5 "$SERVER" "$cmd" 2>/dev/null; then
            return 0
        fi
        
        echo -e "${RED}Falha na tentativa $attempt${NC}"
        attempt=$((attempt + 1))
        sleep 2
    done
    
    return 1
}

# Função para testar URL
test_url() {
    local url="$1"
    local max_attempts=5
    local attempt=1
    
    echo -e "${YELLOW}Testando $url...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -m 5 "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $url está respondendo!${NC}"
            return 0
        fi
        echo -e "${YELLOW}Tentativa $attempt/$max_attempts para $url${NC}"
        attempt=$((attempt + 1))
        sleep 3
    done
    
    echo -e "${RED}❌ $url não está respondendo${NC}"
    return 1
}

echo -e "${YELLOW}1. Verificando processos existentes...${NC}"
ssh_exec "ps aux | grep -E '(uvicorn|next)' | grep -v grep"

echo -e "${YELLOW}2. Limpando processos antigos...${NC}"
ssh_exec "pkill -f uvicorn || true"
ssh_exec "pkill -f next || true" 
ssh_exec "fuser -k 8000/tcp 2>/dev/null || true"
ssh_exec "fuser -k 3000/tcp 2>/dev/null || true"

echo -e "${YELLOW}3. Aguardando limpeza...${NC}"
sleep 5

echo -e "${YELLOW}4. Iniciando Backend...${NC}"
if ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 & sleep 3 && curl -s localhost:8000/api/health"; then
    echo -e "${GREEN}✅ Backend iniciado com sucesso${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar backend${NC}"
    echo "Verificando logs..."
    ssh_exec "tail -20 /var/log/backend.log"
    exit 1
fi

echo -e "${YELLOW}5. Iniciando Frontend...${NC}"
if ssh_exec "cd /var/www/financas/app_dev/frontend && nohup npm start > /var/log/frontend.log 2>&1 & sleep 5 && ps aux | grep next | head -2"; then
    echo -e "${GREEN}✅ Frontend iniciado${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar frontend${NC}"
    echo "Verificando logs..."
    ssh_exec "tail -20 /var/log/frontend.log"
fi

echo -e "${YELLOW}6. Testando URLs externamente...${NC}"
sleep 10

# Testar backend
if test_url "http://148.230.78.91:8000/api/health"; then
    echo -e "${GREEN}✅ Backend acessível externamente${NC}"
else
    echo -e "${RED}❌ Backend não acessível externamente${NC}"
    echo "Testando internamente..."
    ssh_exec "curl -s localhost:8000/api/health"
fi

# Testar frontend
if test_url "http://148.230.78.91:3000"; then
    echo -e "${GREEN}✅ Frontend acessível externamente${NC}"
else
    echo -e "${RED}❌ Frontend não acessível externamente${NC}"
fi

echo -e "${YELLOW}7. Status final dos processos...${NC}"
ssh_exec "ps aux | grep -E '(uvicorn|next)' | grep -v grep"

echo -e "${YELLOW}8. Status das portas...${NC}"
ssh_exec "netstat -tlnp | grep -E '(8000|3000)'"

echo ""
echo "============================================"
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO!${NC}"
echo ""
echo -e "${YELLOW}URLs para testar:${NC}"
echo "Backend:  http://148.230.78.91:8000/api/health"
echo "Frontend: http://148.230.78.91:3000"
echo "Login:    admin@financas.com / admin123"
echo ""
echo -e "${YELLOW}Logs em caso de problemas:${NC}"
echo "Backend:  tail -f /var/log/backend.log"
echo "Frontend: tail -f /var/log/frontend.log"
echo "============================================"