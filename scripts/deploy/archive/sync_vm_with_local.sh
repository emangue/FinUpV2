#!/bin/bash

################################################################################
# Script: Sincronizar VM com Versão Local
# Descrição: Aplica plano P0 para alinhar VM com estado local
# Data: 06/03/2026
# Autor: Sistema FinUp
################################################################################

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
VM_HOST="minha-vps-hostinger"
VM_PATH="/var/www/finup"
BACKUP_DIR="/tmp/backups_finup"
LOG_FILE="/tmp/sync_vm_$(date +%Y%m%d_%H%M%S).log"

################################################################################
# Funções Utilitárias
################################################################################

log() {
    echo -e "${BLUE}[$(date +%Y-%m-%d\ %H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

confirm() {
    read -p "$(echo -e ${YELLOW}$1${NC} [y/N]: )" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

ssh_vm() {
    ssh "$VM_HOST" "$@"
}

################################################################################
# Validações Pré-Execução
################################################################################

pre_check() {
    log "🔍 Validações pré-execução..."
    
    # 1. Verificar conectividade SSH
    if ! ssh_vm "echo '✅ SSH OK'" > /dev/null 2>&1; then
        log_error "Falha ao conectar via SSH na VM"
        exit 1
    fi
    log_success "SSH conectado"
    
    # 2. Verificar git status local
    if [[ -n $(git status --short) ]]; then
        log_warning "Git local tem mudanças não commitadas"
        git status --short
        if ! confirm "Continuar mesmo assim?"; then
            exit 1
        fi
    fi
    log_success "Git local OK"
    
    # 3. Verificar docker na VM
    if ! ssh_vm "docker ps > /dev/null 2>&1"; then
        log_error "Docker não está rodando na VM"
        exit 1
    fi
    log_success "Docker VM OK"
    
    # 4. Criar diretório de backup na VM
    ssh_vm "mkdir -p $BACKUP_DIR"
    log_success "Diretório de backup criado"
}

################################################################################
# Etapa 1: Backup do Banco
################################################################################

backup_database() {
    log "💾 Etapa 1/5: Backup do banco de dados..."
    
    BACKUP_FILE="$BACKUP_DIR/backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql"
    
    log "Criando backup em: $BACKUP_FILE"
    ssh_vm "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db > $BACKUP_FILE"
    
    # Verificar tamanho do backup
    BACKUP_SIZE=$(ssh_vm "ls -lh $BACKUP_FILE | awk '{print \$5}'")
    log_success "Backup criado: $BACKUP_SIZE"
    
    # Fazer backup local também (segurança extra)
    log "Copiando backup para local..."
    scp "$VM_HOST:$BACKUP_FILE" "/tmp/" > /dev/null 2>&1 || true
    log_success "Backup copiado localmente"
}

################################################################################
# Etapa 2: Aplicar Migrations
################################################################################

apply_migrations() {
    log "🔄 Etapa 2/5: Aplicando migrations pendentes..."
    
    # Verificar versão atual
    CURRENT_VERSION=$(ssh_vm "docker exec finup_backend_prod alembic current 2>/dev/null | tail -1")
    log "Versão atual: $CURRENT_VERSION"
    
    # Listar migrations pendentes
    log "Migrations pendentes:"
    ssh_vm "docker exec finup_backend_prod alembic history --verbose 2>/dev/null | head -20"
    
    if ! confirm "Aplicar migrations agora?"; then
        log_warning "Migrations não aplicadas (usuário cancelou)"
        return
    fi
    
    # Aplicar migrations
    log "Aplicando: alembic upgrade head..."
    ssh_vm "docker exec finup_backend_prod alembic upgrade head" || {
        log_error "Falha ao aplicar migrations!"
        log_warning "Execute rollback manual se necessário"
        exit 1
    }
    
    # Verificar nova versão
    NEW_VERSION=$(ssh_vm "docker exec finup_backend_prod alembic current 2>/dev/null | tail -1")
    log_success "Migrations aplicadas! Nova versão: $NEW_VERSION"
    
    # Validar schema
    log "Validando schema..."
    TABLE_COUNT=$(ssh_vm 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = '"'"'public'"'"'"' | tr -d ' ')
    log_success "Total de tabelas: $TABLE_COUNT"
}

################################################################################
# Etapa 3: Restart Containers
################################################################################

restart_containers() {
    log "🔄 Etapa 3/5: Restart dos containers..."
    
    log "Ordem: postgres → redis → backend → frontend → nginx"
    
    # Postgres (se necessário)
    log "Restartando postgres..."
    ssh_vm "cd $VM_PATH && docker-compose -f docker-compose.prod.yml restart postgres" || true
    sleep 5
    
    # Redis
    log "Restartando redis..."
    ssh_vm "cd $VM_PATH && docker-compose -f docker-compose.prod.yml restart redis" || true
    sleep 3
    
    # Backend
    log "Restartando backend..."
    ssh_vm "cd $VM_PATH && docker-compose -f docker-compose.prod.yml restart backend" || true
    sleep 10
    
    # Frontend App
    log "Restartando frontend-app..."
    ssh_vm "cd $VM_PATH && docker-compose -f docker-compose.prod.yml restart frontend-app" || true
    sleep 5
    
    # Nginx
    log "Restartando nginx..."
    ssh_vm "cd $VM_PATH && docker-compose -f docker-compose.prod.yml restart nginx" || true
    sleep 5
    
    log_success "Todos os containers restartados"
}

################################################################################
# Etapa 4: Validar Health
################################################################################

validate_health() {
    log "🏥 Etapa 4/5: Validando health dos containers..."
    
    # Aguardar containers estabilizarem
    log "Aguardando 30 segundos para estabilização..."
    sleep 30
    
    # Verificar status dos containers
    log "Status dos containers:"
    ssh_vm "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    
    # Verificar health endpoint
    log "Testando /api/health..."
    HEALTH_RESPONSE=$(ssh_vm "curl -s http://localhost/api/health" || echo '{"status":"error"}')
    echo "$HEALTH_RESPONSE"
    
    if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
        log_success "Health check OK!"
    else
        log_warning "Health check retornou resposta inesperada"
    fi
    
    # Contar unhealthy containers
    UNHEALTHY_COUNT=$(ssh_vm "docker ps | grep -c unhealthy || true")
    if [[ "$UNHEALTHY_COUNT" -gt 0 ]]; then
        log_warning "$UNHEALTHY_COUNT container(s) ainda unhealthy"
        log "Aguarde alguns minutos e execute: docker ps"
    else
        log_success "Todos os containers estão healthy!"
    fi
}

################################################################################
# Etapa 5: Limpar Processos Ateliê
################################################################################

cleanup_atelie() {
    log "🧹 Etapa 5/5: Limpando processos do Ateliê..."
    
    # Verificar se existem processos
    ATELIE_PROCS=$(ssh_vm "ps aux | grep -E '/var/www/atelie' | grep -v grep | wc -l")
    
    if [[ "$ATELIE_PROCS" -eq 0 ]]; then
        log_success "Nenhum processo do Ateliê encontrado"
        return
    fi
    
    log "Encontrados $ATELIE_PROCS processos do Ateliê"
    ssh_vm "ps aux | grep -E '/var/www/atelie' | grep -v grep"
    
    if ! confirm "Matar estes processos?"; then
        log_warning "Processos do Ateliê não foram mortos"
        return
    fi
    
    # Matar processos uvicorn
    log "Matando uvicorn do Ateliê..."
    ssh_vm "pkill -f '/var/www/atelie/app_dev/backend/venv/bin/uvicorn' || true"
    
    # Matar processos Node
    log "Matando Node.js do Ateliê..."
    ssh_vm "pkill -f '/var/www/atelie/app_dev/frontend' || true"
    
    sleep 3
    
    # Validar
    REMAINING=$(ssh_vm "ps aux | grep -E '/var/www/atelie' | grep -v grep | wc -l")
    if [[ "$REMAINING" -eq 0 ]]; then
        log_success "Todos os processos do Ateliê foram mortos"
    else
        log_warning "$REMAINING processo(s) ainda rodando"
    fi
}

################################################################################
# Resumo Final
################################################################################

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ SINCRONIZAÇÃO CONCLUÍDA${NC}"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📊 Próximos passos:"
    echo "  1. Validar funcionamento do sistema (acessar frontend)"
    echo "  2. Monitorar logs por algumas horas"
    echo "  3. Executar plano P1 (limpeza de tabelas antigas)"
    echo ""
    echo "📝 Log completo: $LOG_FILE"
    echo ""
    echo "🔍 Comandos úteis de validação:"
    echo "  ssh $VM_HOST 'docker ps'"
    echo "  ssh $VM_HOST 'docker logs finup_backend_prod --tail 50'"
    echo "  ssh $VM_HOST 'curl -s http://localhost/api/health'"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

################################################################################
# Função Principal
################################################################################

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "🚀 Sincronização VM com Versão Local - Plano P0"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Este script irá:"
    echo "  1. Fazer backup do banco de dados"
    echo "  2. Aplicar 11 migrations pendentes"
    echo "  3. Restart coordenado dos containers"
    echo "  4. Validar health dos serviços"
    echo "  5. Limpar processos duplicados (Ateliê)"
    echo ""
    echo "⏱️  Tempo estimado: 20-30 minutos"
    echo "⚠️  Downtime esperado: 2-5 minutos"
    echo ""
    
    if ! confirm "Deseja continuar?"; then
        log_warning "Operação cancelada pelo usuário"
        exit 0
    fi
    
    log "Iniciando sincronização..."
    log "Log: $LOG_FILE"
    
    # Executar etapas
    pre_check
    backup_database
    apply_migrations
    restart_containers
    validate_health
    cleanup_atelie
    
    # Resumo
    print_summary
}

################################################################################
# Executar
################################################################################

main "$@"
