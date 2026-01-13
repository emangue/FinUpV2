#!/bin/bash

# ==========================================
# ORQUESTRADOR DE DEPLOY LIMPO
# Executa auditoria → limpeza → deploy fresco
# ==========================================

SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

echo "🎯 ORQUESTRADOR DE DEPLOY LIMPO"
echo "=================================================="
echo ""

# Verificar conectividade
log "Verificando conectividade SSH..."
if ! timeout 10 ssh -i "$SSH_KEY" "$SERVER" "echo 'OK'" >/dev/null 2>&1; then
    error "Não conseguiu conectar no servidor via SSH"
    exit 1
fi
log "✅ SSH funcionando"

echo ""
log "📋 Plano de execução:"
echo "  1. 🔍 Auditoria completa do servidor"
echo "  2. 🧹 Limpeza total (se usuário confirmar)"
echo "  3. 🚀 Deploy fresco e organizado"
echo "  4. ✅ Verificação final"
echo ""

read -p "Continuar? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Operação cancelada"
    exit 0
fi

echo ""
log "=== ETAPA 1: AUDITORIA ==="
chmod +x audit_server.sh
log "Executando auditoria..."
./audit_server.sh > audit_report.txt 2>&1
echo ""
warn "📄 Relatório de auditoria salvo em: audit_report.txt"
echo ""

read -p "Ver relatório agora? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=== RELATÓRIO DE AUDITORIA ==="
    cat audit_report.txt
    echo ""
fi

echo ""
warn "⚠️  PRÓXIMO PASSO: LIMPEZA TOTAL"
warn "⚠️  Isso vai remover TUDO do sistema de finanças no servidor"
echo ""
read -p "Prosseguir com limpeza? Digite 'SIM' para confirmar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    log "Limpeza cancelada. Processo interrompido."
    exit 0
fi

echo ""
log "=== ETAPA 2: LIMPEZA ==="
log "Copiando e executando script de limpeza..."

if ! scp -i "$SSH_KEY" clean_server.sh "$SERVER":/tmp/; then
    error "Falha ao copiar script de limpeza"
    exit 1
fi

log "Executando limpeza no servidor..."
ssh -i "$SSH_KEY" "$SERVER" "chmod +x /tmp/clean_server.sh && /tmp/clean_server.sh" || {
    error "Falha na limpeza"
    exit 1
}

log "✅ Limpeza concluída"

echo ""
log "=== ETAPA 3: DEPLOY FRESCO ==="
log "Copiando e executando deploy fresco..."

if ! scp -i "$SSH_KEY" fresh_deploy.sh "$SERVER":/tmp/; then
    error "Falha ao copiar script de deploy"
    exit 1
fi

log "Executando deploy fresco no servidor..."
ssh -i "$SSH_KEY" "$SERVER" "chmod +x /tmp/fresh_deploy.sh && /tmp/fresh_deploy.sh" || {
    error "Falha no deploy"
    exit 1
fi

log "✅ Deploy fresco concluído"

echo ""
log "=== ETAPA 4: VERIFICAÇÃO FINAL ==="

sleep 5

# Testar URLs
log "Testando conectividade externa..."

if curl -s -m 10 "http://148.230.78.91:8000/api/health" | grep -q "healthy"; then
    log "✅ Backend funcionando: http://148.230.78.91:8000"
else
    warn "⚠️  Backend pode não estar acessível externamente"
fi

if curl -s -m 10 "http://148.230.78.91:8000/" | grep -q -i "finanças"; then
    log "✅ Frontend funcionando: http://148.230.78.91:8000"
else
    warn "⚠️  Frontend pode ter problemas"
fi

echo ""
log "============================================"
log "🎉 DEPLOY LIMPO CONCLUÍDO!"
log "============================================"
echo ""

log "🌐 URLs para acesso:"
echo "  Sistema:   http://148.230.78.91:8000"
echo "  API Docs:  http://148.230.78.91:8000/api/docs"
echo "  Health:    http://148.230.78.91:8000/api/health"
echo ""

log "🔧 Comandos úteis no servidor:"
echo "  ssh $SERVER 'financas-status'"
echo "  ssh $SERVER 'tail -f /var/log/financas/backend.log'"
echo ""

log "📊 Estado final:"
ssh -i "$SSH_KEY" "$SERVER" "
echo '  Processos: '$(ps aux | grep uvicorn | grep -v grep | wc -l)
echo '  Portas ocupadas: '$(netstat -tlnp 2>/dev/null | grep ':8000' | wc -l)
echo '  Uso disco /var: '$(du -sh /var 2>/dev/null | cut -f1)
"

echo ""
log "📄 Relatórios gerados:"
echo "  audit_report.txt - Estado antes da limpeza"
echo ""

info "🎯 Sistema limpo e funcionando!"
info "🚀 Pronto para desenvolvimento incremental!"