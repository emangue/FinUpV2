#!/bin/bash
# ==========================================
# Backup Automático para S3 (AWS)
# ==========================================
# 
# Faz backup criptografado do banco SQLite para S3
# Roda via cron diariamente
# Custo: ~R$1.50/mês para 1GB
#
# Uso:
#   ./backup-to-s3.sh
#
# Pré-requisitos:
#   - rclone instalado e configurado
#   - Variáveis S3_* definidas no .env
# ==========================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Backup para S3 - Iniciando${NC}"
echo -e "${GREEN}===========================================${NC}"

# ==========================================
# Variáveis
# ==========================================
BACKUP_DIR="/var/lib/financas/backups"
DB_PATH="/var/lib/financas/db/financas.db"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/financas_backup_$DATE.db"
S3_BUCKET=${S3_BUCKET:-"s3://financas-backups"}
S3_PATH="$S3_BUCKET/daily/$DATE/"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# ==========================================
# Verificar rclone
# ==========================================
if ! command -v rclone &> /dev/null; then
    echo -e "${RED}ERRO: rclone não instalado${NC}"
    echo "Instale com: curl https://rclone.org/install.sh | sudo bash"
    exit 1
fi

# ==========================================
# Criar diretório de backup
# ==========================================
mkdir -p "$BACKUP_DIR"

# ==========================================
# Copiar banco de dados (hot backup)
# ==========================================
echo -e "${YELLOW}[1/4]${NC} Copiando banco de dados..."

if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}ERRO: Banco não encontrado em $DB_PATH${NC}"
    exit 1
fi

# SQLite hot backup (sem travar o banco)
sqlite3 "$DB_PATH" ".backup $BACKUP_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup criado: $SIZE${NC}"
else
    echo -e "${RED}ERRO: Falha ao criar backup${NC}"
    exit 1
fi

# ==========================================
# Comprimir backup (opcional)
# ==========================================
echo -e "${YELLOW}[2/4]${NC} Comprimindo backup..."

gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

SIZE_COMPRESSED=$(du -h "$BACKUP_FILE" | cut -f1)
echo -e "${GREEN}✓ Backup comprimido: $SIZE_COMPRESSED${NC}"

# ==========================================
# Upload para S3 (criptografado)
# ==========================================
echo -e "${YELLOW}[3/4]${NC} Enviando para S3..."

# rclone com criptografia AES-256
rclone copy "$BACKUP_FILE" "$S3_PATH" \
    --progress \
    --transfers 4 \
    --checkers 8 \
    --contimeout 60s \
    --timeout 300s \
    --retries 3 \
    --low-level-retries 10 \
    --stats 1s

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Upload concluído${NC}"
else
    echo -e "${RED}ERRO: Falha no upload para S3${NC}"
    exit 1
fi

# ==========================================
# Limpar backups antigos (local)
# ==========================================
echo -e "${YELLOW}[4/4]${NC} Limpando backups antigos..."

# Manter apenas últimos N dias localmente
find "$BACKUP_DIR" -name "financas_backup_*.db.gz" -type f -mtime +$RETENTION_DAYS -delete

LOCAL_COUNT=$(find "$BACKUP_DIR" -name "financas_backup_*.db.gz" -type f | wc -l)
echo -e "${GREEN}✓ Backups locais: $LOCAL_COUNT (últimos $RETENTION_DAYS dias)${NC}"

# Limpar backups antigos no S3 (opcional)
# rclone delete "$S3_BUCKET/daily" --min-age ${RETENTION_DAYS}d

# ==========================================
# Finalização
# ==========================================
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}✓ Backup concluído com sucesso!${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo "Backup: $BACKUP_FILE"
echo "S3 Path: $S3_PATH"
echo "Tamanho: $SIZE_COMPRESSED"
echo ""
echo -e "${YELLOW}Verificar no S3:${NC}"
echo "  rclone ls $S3_PATH"
echo ""
