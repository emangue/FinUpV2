#!/bin/bash

# ==========================================
# LIMPEZA COMPLETA DO SERVIDOR
# Remove TUDO relacionado ao sistema de finanças
# ==========================================

set -e

echo "🧹 LIMPEZA COMPLETA DO SERVIDOR"
echo "=================================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo $0"
    exit 1
fi

echo ""
warn "⚠️  ATENÇÃO: Este script vai DELETAR TUDO relacionado ao sistema de finanças!"
warn "⚠️  Isso inclui:"
warn "     - Todos os processos Python/Node em execução"
warn "     - Todas as pastas em /var/www/financas"
warn "     - Todos os logs relacionados"
warn "     - Bancos de dados em /var/lib/financas"
warn "     - Configurações nginx relacionadas"
echo ""

read -p "Tem certeza que quer continuar? Digite 'CONFIRMO' para prosseguir: " confirmacao

if [ "$confirmacao" != "CONFIRMO" ]; then
    log "Operação cancelada."
    exit 0
fi

echo ""
log "Iniciando limpeza completa..."

log "1. Parando TODOS os processos relacionados..."
# Matar processos específicos
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "next" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "node.*financas" 2>/dev/null || true
pkill -f "python.*financas" 2>/dev/null || true

# Forçar liberação das portas
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true

log "Aguardando processos terminarem..."
sleep 5

log "2. Removendo pastas da aplicação..."
if [ -d "/var/www/financas" ]; then
    log "Removendo /var/www/financas..."
    rm -rf /var/www/financas
    log "✅ /var/www/financas removido"
else
    log "ℹ️  /var/www/financas não existia"
fi

# Remover outras possíveis localizações
rm -rf /var/www/html/financas 2>/dev/null || true
rm -rf /opt/financas 2>/dev/null || true
rm -rf /home/*/financas 2>/dev/null || true

log "3. Removendo dados e configurações..."
if [ -d "/var/lib/financas" ]; then
    log "Removendo /var/lib/financas..."
    rm -rf /var/lib/financas
    log "✅ /var/lib/financas removido"
else
    log "ℹ️  /var/lib/financas não existia"
fi

log "4. Removendo logs..."
rm -f /var/log/backend.log 2>/dev/null || true
rm -f /var/log/frontend.log 2>/dev/null || true
rm -f /var/log/financas*.log 2>/dev/null || true
rm -f /var/log/uvicorn*.log 2>/dev/null || true
rm -f /var/log/next*.log 2>/dev/null || true

log "5. Removendo configurações nginx..."
if [ -f "/etc/nginx/sites-enabled/financas" ]; then
    log "Removendo configuração nginx financas..."
    rm -f /etc/nginx/sites-enabled/financas
    rm -f /etc/nginx/sites-available/financas
    
    # Testar e recarregar nginx se estiver rodando
    if systemctl is-active --quiet nginx; then
        nginx -t && systemctl reload nginx
        log "✅ Nginx recarregado"
    fi
else
    log "ℹ️  Configuração nginx não encontrada"
fi

log "6. Removendo serviços systemd..."
if [ -f "/etc/systemd/system/financas.service" ]; then
    systemctl stop financas.service 2>/dev/null || true
    systemctl disable financas.service 2>/dev/null || true
    rm -f /etc/systemd/system/financas.service
    systemctl daemon-reload
    log "✅ Serviço systemd removido"
else
    log "ℹ️  Serviço systemd não encontrado"
fi

log "7. Limpando arquivos temporários..."
rm -f /tmp/deploy*.sh 2>/dev/null || true
rm -f /tmp/financas* 2>/dev/null || true
rm -rf /tmp/pip-* 2>/dev/null || true

log "8. Verificação final..."
echo ""

# Verificar se ainda há processos
PROCESSOS=$(ps aux | grep -E "(uvicorn|next.*financas|python.*financas)" | grep -v grep | wc -l)
if [ "$PROCESSOS" -eq 0 ]; then
    log "✅ Nenhum processo relacionado encontrado"
else
    warn "⚠️  Ainda há $PROCESSOS processos rodando:"
    ps aux | grep -E "(uvicorn|next|python)" | grep -v grep
fi

# Verificar portas
PORTAS=$(netstat -tlnp 2>/dev/null | grep -E ":(8000|3000)" | wc -l)
if [ "$PORTAS" -eq 0 ]; then
    log "✅ Portas 8000 e 3000 livres"
else
    warn "⚠️  Ainda há portas ocupadas:"
    netstat -tlnp | grep -E ":(8000|3000)"
fi

# Verificar pastas
if [ ! -d "/var/www/financas" ] && [ ! -d "/var/lib/financas" ]; then
    log "✅ Todas as pastas removidas"
else
    warn "⚠️  Ainda existem pastas:"
    ls -la /var/www/financas 2>/dev/null || true
    ls -la /var/lib/financas 2>/dev/null || true
fi

echo ""
log "============================================"
log "🎉 LIMPEZA COMPLETA FINALIZADA!"
log "============================================"
echo ""
log "📊 Status pós-limpeza:"
log "  - Processos Python/Node: $(ps aux | grep -E '(python|node)' | grep -v grep | wc -l)"
log "  - Portas 8000/3000: $(netstat -tlnp 2>/dev/null | grep -E ':(8000|3000)' | wc -l || echo 0) ocupadas"
log "  - Uso de disco /var: $(du -sh /var 2>/dev/null | cut -f1)"
echo ""
log "🚀 Servidor limpo e pronto para novo deploy!"
log "🎯 Próximo passo: Execute fresh_deploy.sh"
echo ""