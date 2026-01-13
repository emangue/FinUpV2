#!/bin/bash
# Backup diário automático do banco de dados
# Mantém apenas os últimos 7 dias

DB_PATH="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database"
DB_FILE="$DB_PATH/financas_dev.db"
BACKUP_DIR="$DB_PATH/backups_daily"
DATA_HOJE=$(date +%Y-%m-%d)
BACKUP_FILE="$BACKUP_DIR/financas_dev_${DATA_HOJE}.db"

# Criar pasta de backups se não existir
mkdir -p "$BACKUP_DIR"

# Verificar se já existe backup de hoje
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ Backup de hoje já existe: $BACKUP_FILE"
    exit 0
fi

# Fazer backup
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "✅ Backup criado: $BACKUP_FILE"
    
    # Limpar backups antigos (manter apenas últimos 7 dias)
    find "$BACKUP_DIR" -name "financas_dev_*.db" -type f -mtime +7 -delete
    echo "🧹 Backups antigos (>7 dias) removidos"
    
    # Mostrar backups existentes
    echo ""
    echo "📦 Backups disponíveis:"
    ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print "   " $9 " (" $5 ")"}'
else
    echo "❌ Erro: Banco de dados não encontrado em $DB_FILE"
    exit 1
fi
