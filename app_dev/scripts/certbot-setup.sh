#!/bin/bash
# ==========================================
# Certbot Setup - Let's Encrypt SSL
# ==========================================
# 
# Gera certificados SSL GRATUITOS via Let's Encrypt
# Configuração automática de renovação via cron
#
# ⚠️ MEGA IMPORTANTE: HTTPS é obrigatório em produção!
#
# Uso:
#   sudo ./certbot-setup.sh
#
# Pré-requisitos:
#   - Domínio apontando para o servidor (DNS configurado)
#   - Portas 80 e 443 abertas no firewall
#   - Nginx parado (certbot usa porta 80 temporariamente)
# ==========================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo -e "Let's Encrypt SSL - Configuração"
echo -e "==========================================${NC}"
echo ""

# ==========================================
# Verificar se está rodando como root
# ==========================================
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERRO: Este script precisa ser executado como root${NC}"
    echo "Execute com: sudo ./certbot-setup.sh"
    exit 1
fi

# ==========================================
# Solicitar domínio
# ==========================================
echo -e "${YELLOW}[1/6]${NC} Configuração do domínio"
echo ""
read -p "Digite o domínio (ex: financas.seudomain.com.br): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}ERRO: Domínio não pode ser vazio${NC}"
    exit 1
fi

echo ""
read -p "Digite o email para notificações (ex: admin@seudomain.com.br): " EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}ERRO: Email não pode ser vazio${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Domínio: $DOMAIN${NC}"
echo -e "${GREEN}✓ Email: $EMAIL${NC}"
echo ""

# ==========================================
# Instalar Certbot
# ==========================================
echo -e "${YELLOW}[2/6]${NC} Instalando Certbot..."

if ! command -v certbot &> /dev/null; then
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        yum install -y certbot python3-certbot-nginx
    else
        echo -e "${RED}ERRO: Sistema operacional não suportado${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Certbot instalado${NC}"
else
    echo -e "${GREEN}✓ Certbot já instalado${NC}"
fi

# ==========================================
# Parar Nginx (se estiver rodando)
# ==========================================
echo -e "${YELLOW}[3/6]${NC} Verificando Nginx..."

if systemctl is-active --quiet nginx; then
    echo "Parando Nginx temporariamente..."
    systemctl stop nginx
    NGINX_WAS_RUNNING=true
else
    NGINX_WAS_RUNNING=false
fi

echo -e "${GREEN}✓ Nginx parado${NC}"

# ==========================================
# Gerar certificado SSL
# ==========================================
echo -e "${YELLOW}[4/6]${NC} Gerando certificado SSL..."
echo ""
echo -e "${BLUE}Aguarde, isso pode levar alguns minutos...${NC}"
echo ""

certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    --preferred-challenges http

if [ $? -ne 0 ]; then
    echo -e "${RED}ERRO: Falha ao gerar certificado${NC}"
    echo ""
    echo "Possíveis causas:"
    echo "  - DNS não está apontando para este servidor"
    echo "  - Portas 80/443 bloqueadas no firewall"
    echo "  - Domínio inválido ou já com certificado ativo"
    exit 1
fi

echo -e "${GREEN}✓ Certificado gerado com sucesso!${NC}"
echo ""
echo "Certificado salvo em:"
echo "  /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo ""

# ==========================================
# Configurar renovação automática
# ==========================================
echo -e "${YELLOW}[5/6]${NC} Configurando renovação automática..."

# Criar script de renovação
cat > /etc/cron.daily/certbot-renew << 'EOF'
#!/bin/bash
# Renovação automática de certificados Let's Encrypt
# Executado diariamente pelo cron

# Tentar renovar (só renova se faltarem < 30 dias)
certbot renew --quiet --post-hook "systemctl reload nginx"

# Log
if [ $? -eq 0 ]; then
    echo "$(date): Certificados verificados/renovados" >> /var/log/letsencrypt/renew.log
fi
EOF

chmod +x /etc/cron.daily/certbot-renew

# Criar diretório de logs
mkdir -p /var/log/letsencrypt

echo -e "${GREEN}✓ Renovação automática configurada${NC}"
echo "  - Cron: /etc/cron.daily/certbot-renew"
echo "  - Logs: /var/log/letsencrypt/renew.log"
echo ""

# ==========================================
# Atualizar nginx.conf com domínio
# ==========================================
echo -e "${YELLOW}[6/6]${NC} Atualizando configuração do nginx..."

NGINX_CONF="/app/deploy/nginx.conf"

if [ -f "$NGINX_CONF" ]; then
    # Backup
    cp "$NGINX_CONF" "$NGINX_CONF.backup"
    
    # Substituir domínio placeholder
    sed -i "s/financas.seudomain.com.br/$DOMAIN/g" "$NGINX_CONF"
    
    echo -e "${GREEN}✓ Nginx configurado${NC}"
    echo "  - Config: $NGINX_CONF"
    echo "  - Backup: $NGINX_CONF.backup"
else
    echo -e "${YELLOW}WARN: nginx.conf não encontrado em $NGINX_CONF${NC}"
    echo "Configure manualmente para usar:"
    echo "  ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;"
    echo "  ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;"
fi

echo ""

# ==========================================
# Reiniciar Nginx (se estava rodando)
# ==========================================
if [ "$NGINX_WAS_RUNNING" = true ]; then
    echo "Reiniciando Nginx..."
    systemctl start nginx
    
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓ Nginx reiniciado${NC}"
    else
        echo -e "${RED}ERRO: Falha ao reiniciar Nginx${NC}"
        echo "Verifique logs: journalctl -u nginx -n 50"
        exit 1
    fi
fi

# ==========================================
# Finalização
# ==========================================
echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ Configuração concluída com sucesso!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Certificado SSL:${NC}"
echo "  Domínio:  $DOMAIN"
echo "  Validade: 90 dias"
echo "  Renovação: Automática (via cron diário)"
echo ""
echo -e "${BLUE}Próximos passos:${NC}"
echo "  1. Verificar certificado:"
echo "     certbot certificates"
echo ""
echo "  2. Testar renovação manual:"
echo "     certbot renew --dry-run"
echo ""
echo "  3. Iniciar aplicação:"
echo "     docker-compose up -d"
echo ""
echo "  4. Acessar via HTTPS:"
echo "     https://$DOMAIN"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "  - Certificado expira em 90 dias"
echo "  - Renovação automática via cron"
echo "  - Verificar logs: /var/log/letsencrypt/renew.log"
echo ""
echo -e "${BLUE}Testar SSL:${NC}"
echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "  (Deve retornar A ou A+)"
echo ""
