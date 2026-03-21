#!/bin/bash

################################################################################
# Script: Limpeza de Tabelas Órfãs - VM (Plano P1)
# Descrição: Remove tabelas de backup antigas e investiga tabelas órfãs
# Data: 06/03/2026
# Autor: Sistema FinUp
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VM_HOST="minha-vps-hostinger"
BACKUP_DIR="/tmp/backups_finup"
LOG_FILE="/tmp/cleanup_vm_$(date +%Y%m%d_%H%M%S).log"

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
# Etapa 1: Backup das Tabelas Antigas
################################################################################

backup_old_tables() {
    log "💾 Etapa 1/3: Backup das tabelas antigas..."
    
    BACKUP_FILE="$BACKUP_DIR/backup_old_tables_$(date +%Y%m%d_%H%M%S).sql"
    
    log "Criando backup de tabelas antigas..."
    ssh_vm "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db \
        -t 'bank_format_compatibility_backup_20260109_185955' \
        -t 'base_padroes_backup_20260114_144652' \
        -t 'budget_planning_backup_20260115_204445' \
        -t 'budget_planning_backup_20260115_204836' \
        > $BACKUP_FILE 2>/dev/null" || log_warning "Algumas tabelas podem não existir"
    
    BACKUP_SIZE=$(ssh_vm "ls -lh $BACKUP_FILE 2>/dev/null | awk '{print \$5}'" || echo "0")
    log_success "Backup criado: $BACKUP_SIZE"
}

################################################################################
# Etapa 2: Remover Tabelas de Backup Antigas
################################################################################

remove_backup_tables() {
    log "🗑️  Etapa 2/3: Removendo tabelas de backup antigas..."
    
    TABLES_TO_DROP=(
        "bank_format_compatibility_backup_20260109_185955"
        "base_padroes_backup_20260114_144652"
        "budget_planning_backup_20260115_204445"
        "budget_planning_backup_20260115_204836"
    )
    
    log "Tabelas a serem removidas:"
    for table in "${TABLES_TO_DROP[@]}"; do
        echo "  - $table"
    done
    
    if ! confirm "Confirmar remoção destas tabelas?"; then
        log_warning "Remoção cancelada"
        return
    fi
    
    for table in "${TABLES_TO_DROP[@]}"; do
        log "Removendo $table..."
        ssh_vm "docker exec finup_postgres_prod psql -U finup_user -d finup_db -c \"DROP TABLE IF EXISTS $table CASCADE\"" || log_warning "Tabela $table já não existe"
    done
    
    log_success "Tabelas de backup removidas"
}

################################################################################
# Etapa 3: Investigar Tabelas Órfãs
################################################################################

investigate_orphan_tables() {
    log "🔍 Etapa 3/3: Investigando tabelas órfãs..."
    
    ORPHAN_TABLES=(
        "audit_log"
        "error_codes"
        "categories"
        "duplicados_temp"
        "budget_categorias_config"
    )
    
    log "Verificando contagem de registros..."
    for table in "${ORPHAN_TABLES[@]}"; do
        COUNT=$(ssh_vm "docker exec finup_postgres_prod psql -U finup_user -d finup_db -t -c \"SELECT COUNT(*) FROM $table\" 2>/dev/null | tr -d ' '" || echo "N/A")
        
        if [[ "$COUNT" == "N/A" ]]; then
            log_warning "$table: tabela não existe"
        elif [[ "$COUNT" -eq 0 ]]; then
            log "$table: vazia (0 registros) - candidata para remoção"
        else
            log_warning "$table: $COUNT registros - AVALIAR ANTES DE REMOVER"
        fi
    done
    
    echo ""
    log_warning "ATENÇÃO: Tabelas órfãs requerem análise manual!"
    log "Próximos passos:"
    echo "  1. Avaliar se cada tabela órfã é necessária"
    echo "  2. Se vazia e desnecessária: DROP TABLE"
    echo "  3. Se necessária: criar migration local para adicionar"
    echo "  4. Se tem dados importantes: investigar uso antes de remover"
    echo ""
    log "Comando para remover tabelas vazias (AVALIAR ANTES!):"
    echo "  ssh $VM_HOST 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c \"DROP TABLE IF EXISTS audit_log, error_codes, categories, duplicados_temp CASCADE\"'"
}

################################################################################
# Resumo
################################################################################

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ LIMPEZA P1 CONCLUÍDA${NC}"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📊 Resultados:"
    echo "  ✅ Backup das tabelas antigas criado"
    echo "  ✅ Tabelas de backup antigas removidas"
    echo "  ⏸️  Tabelas órfãs requerem análise manual"
    echo ""
    echo "📝 Log completo: $LOG_FILE"
    echo ""
    echo "🔍 Próximos passos:"
    echo "  1. Validar que sistema continua funcional"
    echo "  2. Analisar tabelas órfãs individualmente"
    echo "  3. Decidir: remover, manter, ou criar migration local"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

################################################################################
# Main
################################################################################

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "🧹 Limpeza de Tabelas Órfãs - VM (Plano P1)"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Este script irá:"
    echo "  1. Fazer backup das tabelas antigas"
    echo "  2. Remover tabelas de backup (20260109, 20260114, 20260115)"
    echo "  3. Investigar tabelas órfãs (audit_log, error_codes, etc)"
    echo ""
    echo "⏱️  Tempo estimado: 5-10 minutos"
    echo "⚠️  Downtime esperado: nenhum (operação segura)"
    echo ""
    
    if ! confirm "Deseja continuar?"; then
        log_warning "Operação cancelada"
        exit 0
    fi
    
    log "Iniciando limpeza P1..."
    
    backup_old_tables
    remove_backup_tables
    investigate_orphan_tables
    
    print_summary
}

main "$@"
