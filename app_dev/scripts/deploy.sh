#!/bin/bash
# ==========================================
# Script de Deploy - Sistema de Finanças v4
# ==========================================
# 
# Automatiza deploy completo em VM de produção:
# - Validação de pré-requisitos
# - Build Docker
# - Setup SSL (Let's Encrypt)
# - Inicialização de serviços
# - Configuração de backups
#
# Uso:
#   sudo ./deploy.sh
#
# ⚠️ Executar apenas em servidor de produção!
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
echo "  Sistema de Finanças v4 - Deploy"
echo "=========================================="
echo -e "${NC}"

# ==========================================
# Verificar root
# ==========================================
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERRO: Este script precisa ser executado como root${NC}"
    echo "Execute com: sudo ./deploy.sh"
    exit 1
fi

# ==========================================
# STEP 1: Validar pré-requisitos
# ==========================================
echo -e "${YELLOW}[1/8]${NC} Validando pré-requisitos..."

# Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERRO: Docker não instalado${NC}"
    echo "Instale com: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}ERRO: Docker Compose não instalado${NC}"
    echo "Instale com: sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

# Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git não instalado, instalando...${NC}"
    apt-get update && apt-get install -y git
fi

echo -e "${GREEN}✓ Pré-requisitos OK${NC}"

# ==========================================
# STEP 2: Configurar ambiente
# ==========================================
echo -e "${YELLOW}[2/8]${NC} Configurando ambiente..."

# Criar usuário financas
if ! id "financas" &>/dev/null; then
    useradd -r -s /bin/bash -d /var/www/financas -m financas
    echo -e "${GREEN}✓ Usuário financas criado${NC}"
fi

# Criar diretórios
mkdir -p /var/www/financas
mkdir -p /var/lib/financas/db
mkdir -p /var/lib/financas/uploads
mkdir -p /var/lib/financas/backups

# Permissões
chown -R financas:financas /var/www/financas /var/lib/financas

echo -e "${GREEN}✓ Ambiente configurado${NC}"

# ==========================================
# STEP 3: Clonar/Atualizar repositório
# ==========================================
echo -e "${YELLOW}[3/8]${NC} Baixando código..."

cd /var/www/financas

if [ -d ".git" ]; then
    echo "Atualizando repositório..."
    git pull origin main
else
    echo "Clonando repositório..."
    read -p "URL do repositório (ex: https://github.com/emangue/FinUpV2): " REPO_URL
    git clone "$REPO_URL" .
fi

# Copiar app_dev/ para raiz (estrutura de produção)
if [ -d "app_dev" ]; then
    cp -r app_dev/* .
fi

echo -e "${GREEN}✓ Código atualizado${NC}"

# ==========================================
# STEP 4: Configurar .env
# ==========================================
echo -e "${YELLOW}[4/8]${NC} Configurando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    echo "Criando .env de produção..."
    
    # Gerar SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Solicitar domínio
    read -p "Digite o domínio (ex: financas.seudomain.com.br): " DOMAIN
    read -p "Digite o email para notificações: " EMAIL
    
    cat > .env << EOF
# Produção - Sistema de Finanças v4
ENVIRONMENT=production
DEBUG=False

# Segurança
SECRET_KEY=$SECRET_KEY

# Database
DATABASE_PATH=/var/lib/financas/db/financas.db

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
LOGIN_RATE_LIMIT_PER_MINUTE=5

# CORS (HTTPS obrigatório!)
BACKEND_CORS_ORIGINS=https://$DOMAIN

# Next.js
NEXT_PUBLIC_BACKEND_URL=https://$DOMAIN
NEXT_TELEMETRY_DISABLED=1

# Backup S3 (opcional)
S3_BUCKET=s3://financas-backups
BACKUP_RETENTION_DAYS=30

# Admin
ADMIN_EMAIL=$EMAIL
EOF

    echo -e "${GREEN}✓ .env criado${NC}"
else
    echo -e "${GREEN}✓ .env já existe${NC}"
fi

# ==========================================
# STEP 5: SSL via Let's Encrypt
# ==========================================
echo -e "${YELLOW}[5/8]${NC} Configurando SSL..."

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "Gerando certificado SSL..."
    chmod +x scripts/certbot-setup.sh
    ./scripts/certbot-setup.sh
else
    echo -e "${GREEN}✓ Certificado SSL já existe${NC}"
fi

# ==========================================
# STEP 6: Build Docker
# ==========================================
echo -e "${YELLOW}[6/8]${NC} Construindo imagem Docker..."

docker-compose build --no-cache

echo -e "${GREEN}✓ Imagem Docker criada${NC}"

# ==========================================
# STEP 7: Iniciar serviços
# ==========================================
echo -e "${YELLOW}[7/8]${NC} Iniciando serviços..."

# Parar containers antigos
docker-compose down || true

# Iniciar containers
docker-compose up -d

# Aguardar inicialização
echo "Aguardando serviços iniciarem..."
sleep 10

# Verificar saúde
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Serviços iniciados${NC}"
else
    echo -e "${RED}ERRO: Falha ao iniciar serviços${NC}"
    docker-compose logs
    exit 1
fi

# ==========================================
# STEP 8: Configurar systemd e backups
# ==========================================
echo -e "${YELLOW}[8/8]${NC} Configurando auto-restart e backups..."

# Systemd service
cp scripts/financas.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable financas
echo -e "${GREEN}✓ Auto-restart configurado${NC}"

# Backup cron
chmod +x scripts/backup-to-s3.sh
cat > /etc/cron.daily/financas-backup << 'EOF'
#!/bin/bash
/var/www/financas/scripts/backup-to-s3.sh >> /var/log/financas-backup.log 2>&1
EOF
chmod +x /etc/cron.daily/financas-backup
echo -e "${GREEN}✓ Backup automático configurado${NC}"

# ==========================================
# Finalização
# ==========================================
echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ Deploy concluído com sucesso!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Informações do Deploy:${NC}"
echo "  Domínio:   https://$DOMAIN"
echo "  Database:  /var/lib/financas/db/financas.db"
echo "  Logs:      docker-compose logs -f"
echo "  Status:    docker-compose ps"
echo ""
echo -e "${BLUE}Comandos úteis:${NC}"
echo "  Reiniciar:  sudo systemctl restart financas"
echo "  Logs:       sudo journalctl -u financas -f"
echo "  Parar:      docker-compose down"
echo "  Backup:     ./scripts/backup-to-s3.sh"
echo ""
echo -e "${YELLOW}⚠️  PRÓXIMOS PASSOS:${NC}"
echo "  1. Acessar: https://$DOMAIN"
echo "  2. Login:   admin@financas.com / admin123"
echo "  3. ⚠️  IMPORTANTE: Alterar senha padrão!"
echo ""
echo -e "${BLUE}Testar SSL:${NC}"
echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo -e "${BLUE}Monitoramento:${NC}"
echo "  Health:  curl https://$DOMAIN/api/health"
echo "  Metrics: docker stats"
echo ""
