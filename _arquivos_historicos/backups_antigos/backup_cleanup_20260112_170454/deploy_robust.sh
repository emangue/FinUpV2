#!/bin/bash

# ==========================================
# DEPLOY ROBUSTO - SISTEMA DE FINANÇAS V4
# ==========================================

set -e  # Para imediatamente se houver erro

echo "🚀 Iniciando deploy robusto..."

# Configurações
SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"
MAX_RETRIES=3

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# Função para executar comandos SSH com timeout e retry
ssh_exec() {
    local cmd="$1"
    local retry_count=0
    
    log "Executando: $cmd"
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if timeout 30 ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SERVER" "$cmd" 2>/dev/null; then
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        warn "Tentativa $retry_count/$MAX_RETRIES falhou. Reentando em 3s..."
        sleep 3
    done
    
    error "Comando falhou após $MAX_RETRIES tentativas: $cmd"
    return 1
}

# Função para aguardar serviço ficar online
wait_for_service() {
    local url="$1"
    local timeout_seconds=${2:-60}
    local elapsed=0
    
    log "Aguardando $url ficar disponível (timeout: ${timeout_seconds}s)..."
    
    while [ $elapsed -lt $timeout_seconds ]; do
        if curl -s -m 5 "$url" >/dev/null 2>&1; then
            log "✅ $url está respondendo!"
            return 0
        fi
        
        echo -n "."
        sleep 3
        elapsed=$((elapsed + 3))
    done
    
    error "❌ Timeout aguardando $url"
    return 1
}

# ==========================================
# INÍCIO DO DEPLOY
# ==========================================

log "1. Verificando conectividade SSH..."
if ! ssh_exec "echo 'SSH funcionando'"; then
    error "Não conseguiu conectar via SSH"
    exit 1
fi

log "2. Parando processos antigos..."
ssh_exec "pkill -f 'uvicorn app.main:app' || true"
ssh_exec "pkill -f 'next start' || true"
ssh_exec "pkill -f 'npm start' || true"
ssh_exec "fuser -k 8000/tcp 2>/dev/null || true"
ssh_exec "fuser -k 3000/tcp 2>/dev/null || true"
sleep 5

log "3. Verificando estrutura de pastas..."
ssh_exec "mkdir -p /var/www/financas /var/lib/financas/{db,uploads,backups} /var/log"
ssh_exec "chmod 755 /var/www/financas /var/lib/financas"
ssh_exec "chmod 777 /var/lib/financas/{db,uploads,backups}"

log "4. Sincronizando código..."
if ! rsync -avz --delete -e "ssh -i $SSH_KEY -o ConnectTimeout=10" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='_csvs_historico' \
    app_dev/ "$SERVER":/var/www/financas/app_dev/; then
    error "Falha ao sincronizar código"
    exit 1
fi

log "5. Configurando Python venv..."
ssh_exec "cd /var/www/financas/app_dev/backend && python3 -m venv venv"
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && pip install --upgrade pip"
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && pip install -r requirements.txt"

log "6. Inicializando banco de dados..."
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && python -c \"
from app.core.database import engine, Base
from app.domains.users.models import User
from app.domains.transactions.models import JournalEntry
from app.domains.categories.models import BaseMarcacao, TipoGasto
from app.domains.cards.models import Card
from app.domains.upload.history_models import UploadHistory
from app.domains.upload.models import IgnorarDashboard

print('Criando tabelas...')
Base.metadata.create_all(bind=engine)
print('✅ Database inicializado!')
\""

log "7. Iniciando Backend (uvicorn)..."
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &"
sleep 5

# Verificar se backend subiu
if ! wait_for_service "http://148.230.78.91:8000/api/health" 30; then
    error "Backend não subiu. Verificando logs..."
    ssh_exec "tail -20 /var/log/backend.log"
    exit 1
fi

log "8. Configurando Frontend Node.js..."
ssh_exec "cd /var/www/financas/app_dev/frontend && npm install"
ssh_exec "cd /var/www/financas/app_dev/frontend && npm run build"

log "9. Iniciando Frontend (Next.js)..."
ssh_exec "cd /var/www/financas/app_dev/frontend && nohup npm start > /var/log/frontend.log 2>&1 &"
sleep 10

# Verificar se frontend subiu
if ! wait_for_service "http://148.230.78.91:3000" 45; then
    warn "Frontend pode não ter subido completamente. Verificando logs..."
    ssh_exec "tail -20 /var/log/frontend.log"
fi

log "10. Verificação final dos processos..."
ssh_exec "ps aux | grep -E '(uvicorn|next)' | grep -v grep | head -5"

log "11. Testando portas..."
ssh_exec "netstat -tlnp | grep -E '(8000|3000)'"

# ==========================================
# TESTES FINAIS
# ==========================================

log "12. Testes de conectividade externa..."

echo ""
log "============================================"
log "🎉 DEPLOY CONCLUÍDO!"
log "============================================"

if curl -s -m 10 "http://148.230.78.91:8000/api/health" | grep -q "healthy"; then
    log "✅ Backend funcionando: http://148.230.78.91:8000/api/health"
else
    warn "❌ Backend pode não estar funcionando"
fi

if curl -s -m 10 "http://148.230.78.91:3000" | grep -q -i "finanças\|financas\|html"; then
    log "✅ Frontend funcionando: http://148.230.78.91:3000"
else
    warn "❌ Frontend pode não estar funcionando"
fi

echo ""
log "📊 URLs para acesso:"
echo "  Backend:  http://148.230.78.91:8000/docs"
echo "  Frontend: http://148.230.78.91:3000"
echo "  Health:   http://148.230.78.91:8000/api/health"
echo ""
log "🔑 Login padrão:"
echo "  Email:    admin@financas.com"
echo "  Senha:    admin123"
echo ""
log "📋 Logs para debug:"
echo "  Backend:  ssh $SERVER 'tail -f /var/log/backend.log'"
echo "  Frontend: ssh $SERVER 'tail -f /var/log/frontend.log'"
echo ""