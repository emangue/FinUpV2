#!/bin/bash

# ==========================================
# DEPLOY SIMPLIFICADO SEM TIMEOUT
# Versão mais compatível do deploy
# ==========================================

echo "🚀 Deploy Simplificado"
echo "=================================================="

# Configurações
SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

# Função SSH simplificada
ssh_exec() {
    local cmd="$1"
    log "Executando: $cmd"
    
    if ssh -i "$SSH_KEY" "$SERVER" "$cmd"; then
        return 0
    else
        error "Falha ao executar: $cmd"
        return 1
    fi
}

echo ""
log "1. Testando conectividade SSH..."
if ! ssh_exec "echo 'SSH OK'"; then
    error "Não conseguiu conectar via SSH"
    exit 1
fi

log "2. Parando processos antigos..."
ssh_exec "pkill -f 'uvicorn app.main:app' || true"
ssh_exec "pkill -f 'next start' || true"
ssh_exec "pkill -f 'npm start' || true"
ssh_exec "fuser -k 8000/tcp 2>/dev/null || true"
ssh_exec "fuser -k 3000/tcp 2>/dev/null || true"

sleep 3

log "3. Verificando/criando estrutura de pastas..."
ssh_exec "mkdir -p /var/www/financas /var/lib/financas/{db,uploads,backups} /var/log"
ssh_exec "chmod 755 /var/www/financas /var/lib/financas"
ssh_exec "chmod 777 /var/lib/financas/{db,uploads,backups}"

log "4. Sincronizando código..."
if ! rsync -avz --delete -e "ssh -i $SSH_KEY" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='_csvs_historico' \
    --exclude='deploy_manual*' \
    --exclude='*.backup' \
    app_dev/ "$SERVER":/var/www/financas/app_dev/; then
    error "Falha ao sincronizar código"
    exit 1
fi

log "5. Configurando Python backend..."
ssh_exec "cd /var/www/financas/app_dev/backend && python3 -m venv venv"
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && pip install --upgrade pip"
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && pip install -r requirements.txt"

log "6. Criando banco de dados..."
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && python -c \"
try:
    from app.core.database import engine, Base
    from app.domains.users.models import User
    from app.domains.transactions.models import JournalEntry
    from app.domains.categories.models import BaseMarcacao, TipoGasto
    from app.domains.cards.models import Card
    from app.domains.upload.history_models import UploadHistory
    from app.domains.upload.models import IgnorarDashboard

    print('Criando tabelas...')
    Base.metadata.create_all(bind=engine)
    print('✅ Database criado!')
except Exception as e:
    print(f'❌ Erro no banco: {e}')
\""

log "7. Iniciando backend..."
ssh_exec "cd /var/www/financas/app_dev/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &"

sleep 10

log "8. Verificando backend..."
if ssh_exec "curl -s localhost:8000/api/health"; then
    log "✅ Backend funcionando!"
else
    warn "Backend pode não estar funcionando. Verificando logs..."
    ssh_exec "tail -20 /var/log/backend.log"
fi

log "9. Configurando frontend..."
ssh_exec "cd /var/www/financas/app_dev/frontend && npm install"
ssh_exec "cd /var/www/financas/app_dev/frontend && npm run build"

log "10. Iniciando frontend..."
ssh_exec "cd /var/www/financas/app_dev/frontend && nohup npm start > /var/log/frontend.log 2>&1 &"

sleep 10

log "11. Verificação final..."
ssh_exec "ps aux | grep -E '(uvicorn|next)' | grep -v grep | head -5"

echo ""
log "============================================"
log "🎉 DEPLOY CONCLUÍDO!"
log "============================================"
echo ""

# Testes finais externos
log "Testando acesso externo..."

if curl -s -m 10 "http://148.230.78.91:8000/api/health" | grep -q "healthy"; then
    log "✅ Backend acessível: http://148.230.78.91:8000"
else
    warn "⚠️  Backend pode não estar acessível externamente"
    log "Testando localmente no servidor..."
    ssh_exec "curl -s localhost:8000/api/health"
fi

if curl -s -m 10 "http://148.230.78.91:3000" | grep -q -i "html"; then
    log "✅ Frontend acessível: http://148.230.78.91:3000"
else
    warn "⚠️  Frontend pode não estar acessível externamente"
fi

echo ""
log "📊 URLs de acesso:"
echo "  Frontend: http://148.230.78.91:3000"
echo "  Backend:  http://148.230.78.91:8000"
echo "  API Docs: http://148.230.78.91:8000/docs"
echo "  Health:   http://148.230.78.91:8000/api/health"
echo ""

log "🔧 Para ver logs:"
echo "  Backend:  ssh $SERVER 'tail -f /var/log/backend.log'"
echo "  Frontend: ssh $SERVER 'tail -f /var/log/frontend.log'"
echo ""

log "Deploy concluído! 🚀"