#!/bin/bash
# ==========================================
# Script de Setup rclone para S3
# ==========================================
# 
# Configura rclone com AWS S3 para backups criptografados
# Deve ser executado APÓS o deploy na VM
#
# Uso:
#   sudo ./setup-rclone.sh
#
# Pré-requisitos:
#   - Conta AWS com S3 bucket criado
#   - IAM user com permissões PutObject, GetObject, DeleteObject
#   - Access Key ID e Secret Access Key
#
# ==========================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "=========================================="
echo "  rclone Setup - S3 Backup Configuration"
echo "=========================================="
echo -e "${NC}"

# ==========================================
# Verificar se rclone está instalado
# ==========================================
if ! command -v rclone &> /dev/null; then
    echo -e "${YELLOW}rclone não instalado, instalando...${NC}"
    curl https://rclone.org/install.sh | sudo bash
    echo -e "${GREEN}✓ rclone instalado${NC}"
else
    echo -e "${GREEN}✓ rclone já instalado ($(rclone version | head -1))${NC}"
fi

# ==========================================
# Coletar informações AWS
# ==========================================
echo ""
echo -e "${YELLOW}Informações AWS S3:${NC}"
echo ""
read -p "Digite o nome do S3 bucket (ex: financas-backups): " S3_BUCKET
read -p "Digite a região AWS (ex: us-east-1, sa-east-1): " AWS_REGION
read -p "Digite o Access Key ID: " AWS_ACCESS_KEY_ID
read -sp "Digite o Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""

# ==========================================
# Criar configuração rclone
# ==========================================
echo ""
echo -e "${YELLOW}Criando configuração rclone...${NC}"

# Diretório de config
mkdir -p ~/.config/rclone

# Criar config
cat > ~/.config/rclone/rclone.conf << EOF
[s3]
type = s3
provider = AWS
env_auth = false
access_key_id = $AWS_ACCESS_KEY_ID
secret_access_key = $AWS_SECRET_ACCESS_KEY
region = $AWS_REGION
server_side_encryption = AES256
storage_class = STANDARD

[s3-crypt]
type = crypt
remote = s3:$S3_BUCKET
filename_encryption = standard
directory_name_encryption = true
password = $(rclone obscure "$(openssl rand -base64 32)")
password2 = $(rclone obscure "$(openssl rand -base64 32)")
EOF

# Proteger arquivo de config
chmod 600 ~/.config/rclone/rclone.conf

echo -e "${GREEN}✓ Configuração rclone criada${NC}"

# ==========================================
# Testar conexão
# ==========================================
echo ""
echo -e "${YELLOW}Testando conexão com S3...${NC}"

if rclone lsd s3: &> /dev/null; then
    echo -e "${GREEN}✓ Conexão com S3 OK${NC}"
else
    echo -e "${RED}ERRO: Falha ao conectar no S3${NC}"
    echo "Verifique:"
    echo "  - Access Key e Secret Key estão corretos"
    echo "  - Bucket existe e está na região correta"
    echo "  - IAM user tem permissões necessárias"
    exit 1
fi

# ==========================================
# Criar bucket se não existir
# ==========================================
echo ""
echo -e "${YELLOW}Verificando bucket...${NC}"

if rclone lsd s3: | grep -q "$S3_BUCKET"; then
    echo -e "${GREEN}✓ Bucket '$S3_BUCKET' já existe${NC}"
else
    echo -e "${YELLOW}Criando bucket '$S3_BUCKET'...${NC}"
    rclone mkdir s3:$S3_BUCKET
    echo -e "${GREEN}✓ Bucket criado${NC}"
fi

# ==========================================
# Testar upload criptografado
# ==========================================
echo ""
echo -e "${YELLOW}Testando backup criptografado...${NC}"

# Criar arquivo de teste
TEST_FILE="/tmp/financas-test-backup.txt"
echo "Backup test - $(date)" > $TEST_FILE

# Upload com criptografia
if rclone copy $TEST_FILE s3-crypt:test/ --progress; then
    echo -e "${GREEN}✓ Upload criptografado OK${NC}"
    
    # Listar arquivo
    echo -e "${BLUE}Arquivo no S3 (criptografado):${NC}"
    rclone ls s3:$S3_BUCKET/test/
    
    # Limpar teste
    rclone delete s3-crypt:test/
    rm -f $TEST_FILE
else
    echo -e "${RED}ERRO: Falha no upload de teste${NC}"
    exit 1
fi

# ==========================================
# Atualizar script de backup
# ==========================================
echo ""
echo -e "${YELLOW}Atualizando script de backup...${NC}"

BACKUP_SCRIPT="/var/www/financas/scripts/backup-to-s3.sh"

if [ -f "$BACKUP_SCRIPT" ]; then
    # Substituir placeholder do bucket
    sed -i "s|S3_BUCKET=\"s3://financas-backups\"|S3_BUCKET=\"s3://$S3_BUCKET\"|g" $BACKUP_SCRIPT
    echo -e "${GREEN}✓ Script de backup atualizado${NC}"
fi

# ==========================================
# Configurar backup diário via cron
# ==========================================
echo ""
echo -e "${YELLOW}Configurando backup automático...${NC}"

# Criar script cron
cat > /etc/cron.daily/financas-backup << 'EOF'
#!/bin/bash
/var/www/financas/scripts/backup-to-s3.sh >> /var/log/financas-backup.log 2>&1
EOF

chmod +x /etc/cron.daily/financas-backup

echo -e "${GREEN}✓ Backup diário configurado${NC}"

# ==========================================
# Criar script de restore
# ==========================================
echo ""
echo -e "${YELLOW}Criando script de restore...${NC}"

cat > /var/www/financas/scripts/restore-from-s3.sh << 'EOF'
#!/bin/bash
# Script de restore do backup S3

set -e

echo "=========================================="
echo "  Restore de Backup - S3"
echo "=========================================="
echo ""

# Listar backups disponíveis
echo "Backups disponíveis:"
rclone lsl s3-crypt:daily/ | tail -10

echo ""
read -p "Digite o nome do arquivo para restaurar: " BACKUP_FILE

# Baixar
RESTORE_DIR="/tmp/restore"
mkdir -p $RESTORE_DIR

echo "Baixando backup..."
rclone copy "s3-crypt:daily/$BACKUP_FILE" $RESTORE_DIR --progress

# Descompactar
cd $RESTORE_DIR
gunzip "$BACKUP_FILE"

DB_FILE="${BACKUP_FILE%.gz}"

echo ""
echo "✓ Backup restaurado em: $RESTORE_DIR/$DB_FILE"
echo ""
echo "Para aplicar o restore:"
echo "  1. Parar containers: docker-compose down"
echo "  2. Fazer backup do DB atual: cp /var/lib/financas/db/financas.db /var/lib/financas/db/financas.db.backup"
echo "  3. Substituir: cp $RESTORE_DIR/$DB_FILE /var/lib/financas/db/financas.db"
echo "  4. Iniciar containers: docker-compose up -d"
echo ""
EOF

chmod +x /var/www/financas/scripts/restore-from-s3.sh

echo -e "${GREEN}✓ Script de restore criado${NC}"

# ==========================================
# Teste final
# ==========================================
echo ""
echo -e "${YELLOW}Executando backup de teste...${NC}"

if /var/www/financas/scripts/backup-to-s3.sh; then
    echo -e "${GREEN}✓ Backup de teste executado com sucesso${NC}"
else
    echo -e "${RED}ERRO: Falha no backup de teste${NC}"
    echo "Verifique os logs em /var/log/financas-backup.log"
    exit 1
fi

# ==========================================
# Finalização
# ==========================================
echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ rclone configurado com sucesso!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Informações:${NC}"
echo "  Bucket:       s3://$S3_BUCKET"
echo "  Região:       $AWS_REGION"
echo "  Encryption:   AES-256 (server-side + rclone crypt)"
echo "  Backup:       Diário via cron (/etc/cron.daily/)"
echo "  Logs:         /var/log/financas-backup.log"
echo ""
echo -e "${BLUE}Comandos úteis:${NC}"
echo "  Listar backups:     rclone ls s3-crypt:daily/"
echo "  Backup manual:      /var/www/financas/scripts/backup-to-s3.sh"
echo "  Restore:            /var/www/financas/scripts/restore-from-s3.sh"
echo "  Verificar cron:     crontab -l"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "  - Guarde suas credenciais AWS em local seguro!"
echo "  - Arquivo de config: ~/.config/rclone/rclone.conf"
echo "  - Testar restore periodicamente"
echo ""
echo -e "${BLUE}Custo estimado S3:${NC}"
echo "  Storage: ~R$ 0,10/GB/mês"
echo "  Backup 1GB: ~R$ 1,50/mês (estimativa)"
echo ""
echo -e "${BLUE}IAM Policy mínima necessária:${NC}"
cat << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::SEU-BUCKET/*",
        "arn:aws:s3:::SEU-BUCKET"
      ]
    }
  ]
}
POLICY
echo ""
