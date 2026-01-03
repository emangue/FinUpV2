#!/bin/bash
# Deploy Script para Hostinger VPS
# Data: 2026-01-02
# VM: srv1045889.hstgr.cloud (148.230.78.91)
# OS: Ubuntu 24.04.3 LTS

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SSH_KEY="$HOME/.ssh/id_rsa_hostinger"
SSH_USER="root"
SSH_HOST="148.230.78.91"
APP_DIR="/opt/financial-app"
APP_USER="financial-app"
DOMAIN=""  # Vazio = usar IP
PYTHON_VERSION="3.12"

echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🚀 Hostinger VPS Deployment Script${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""
echo -e "VM: ${GREEN}srv1045889.hstgr.cloud (148.230.78.91)${NC}"
echo -e "OS: ${GREEN}Ubuntu 24.04.3 LTS${NC}"
echo -e "Python: ${GREEN}Python 3.12.3${NC}"
echo ""

# Função para executar comando via SSH
ssh_exec() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "$@"
}

# Função para copiar arquivo via SCP
scp_copy() {
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$1" "$SSH_USER@$SSH_HOST:$2"
}

# Passo 1: Instalar dependências do sistema
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📦 Step 1: Installing System Dependencies${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
apt-get update
apt-get install -y \
    python3-pip \
    python3-venv \
    sqlite3 \
    nginx \
    ufw \
    fail2ban \
    supervisor \
    git

echo "✅ System dependencies installed"
EOF

# Passo 2: Criar usuário da aplicação
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}👤 Step 2: Creating Application User${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << EOF
if ! id -u $APP_USER > /dev/null 2>&1; then
    useradd -m -s /bin/bash $APP_USER
    echo "✅ User $APP_USER created"
else
    echo "ℹ️  User $APP_USER already exists"
fi
EOF

# Passo 3: Criar diretórios
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📁 Step 3: Creating Directories${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << EOF
mkdir -p $APP_DIR
mkdir -p $APP_DIR/instance
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/uploads_temp
mkdir -p /backups/financial-app
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /backups/financial-app
echo "✅ Directories created"
EOF

# Passo 4: Sincronizar arquivos do projeto
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}📤 Step 4: Syncing Project Files${NC}"
echo -e "${BLUE}=================================================================================${NC}"

rsync -avz --progress \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '*.db' \
    --exclude '*.db-*' \
    --exclude '.git/' \
    --exclude 'flask_session/' \
    --exclude 'changes/' \
    --exclude '_temp_scripts/' \
    --exclude '_csvs_historico/' \
    --exclude 'financas.db.backup_*' \
    --exclude 'uploads_temp/' \
    --exclude '*.md' \
    --exclude '.env' \
    ./ "$SSH_USER@$SSH_HOST:$APP_DIR/"

echo -e "${GREEN}✅ Files synced${NC}"

# Passo 5: Criar ambiente virtual e instalar dependências Python
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🐍 Step 5: Creating Virtual Environment & Installing Dependencies${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << EOF
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
echo "✅ Python dependencies installed"
EOF

# Passo 6: Copiar banco de dados
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🗄️  Step 6: Copying Database${NC}"
echo -e "${BLUE}=================================================================================${NC}"

scp_copy "financas.db" "$APP_DIR/instance/financas.db"
ssh_exec "chown $APP_USER:$APP_USER $APP_DIR/instance/financas.db"
echo -e "${GREEN}✅ Database copied${NC}"

# Passo 7: Criar arquivo .env de produção
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}⚙️  Step 7: Creating Production .env${NC}"
echo -e "${BLUE}=================================================================================${NC}"

SECRET_KEY=$(openssl rand -hex 32)

ssh_exec << EOF
cat > $APP_DIR/.env << 'ENVEOF'
# Environment
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=$SECRET_KEY

# Database
DATABASE_URI=$APP_DIR/instance/financas.db

# Paths
UPLOAD_FOLDER=$APP_DIR/uploads_temp
SESSION_FILE_DIR=$APP_DIR/flask_session
LOG_FILE=$APP_DIR/logs/app.log

# Session
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# Server
PREFERRED_URL_SCHEME=http
ENVEOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env
echo "✅ .env file created"
EOF

# Passo 8: Criar arquivo de serviço systemd
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🔧 Step 8: Creating Systemd Service${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
cat > /etc/systemd/system/financial-app.service << 'SERVICEEOF'
[Unit]
Description=Financial Management System
After=network.target

[Service]
Type=notify
User=financial-app
Group=financial-app
WorkingDirectory=/opt/financial-app
Environment="PATH=/opt/financial-app/venv/bin"
ExecStart=/opt/financial-app/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /opt/financial-app/logs/access.log \
    --error-logfile /opt/financial-app/logs/error.log \
    --log-level info \
    run:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable financial-app
echo "✅ Systemd service created"
EOF

# Passo 9: Configurar Nginx
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🌐 Step 9: Configuring Nginx${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
cat > /etc/nginx/sites-available/financial-app << 'NGINXEOF'
server {
    listen 80;
    server_name 148.230.78.91;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static {
        alias /opt/financial-app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /opt/financial-app/uploads_temp;
        internal;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
NGINXEOF

ln -sf /etc/nginx/sites-available/financial-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl restart nginx
echo "✅ Nginx configured"
EOF

# Passo 10: Configurar Firewall
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🔥 Step 10: Configuring Firewall (UFW)${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "✅ Firewall configured"
EOF

# Passo 11: Configurar Fail2ban
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🛡️  Step 11: Configuring Fail2ban${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
cat > /etc/fail2ban/jail.local << 'FAIL2BANEOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /opt/financial-app/logs/error.log
FAIL2BANEOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "✅ Fail2ban configured"
EOF

# Passo 12: Configurar backup automático
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}💾 Step 12: Setting Up Automated Backups${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << EOF
# Criar script de backup na VM
cat > /opt/financial-app/backup.sh << 'BACKUPEOF'
#!/bin/bash
cd /opt/financial-app
source venv/bin/activate
python scripts/backup_database.py auto
BACKUPEOF

chmod +x /opt/financial-app/backup.sh
chown $APP_USER:$APP_USER /opt/financial-app/backup.sh

# Adicionar ao crontab do usuário da aplicação
(crontab -u $APP_USER -l 2>/dev/null || true; echo "0 3 * * * /opt/financial-app/backup.sh >> /opt/financial-app/logs/backup.log 2>&1") | crontab -u $APP_USER -

echo "✅ Automated backups configured (daily at 3 AM)"
EOF

# Passo 13: Ajustar permissões finais
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🔑 Step 13: Setting Final Permissions${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << EOF
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod 600 $APP_DIR/.env
chmod 644 $APP_DIR/instance/financas.db
echo "✅ Permissions set"
EOF

# Passo 14: Iniciar aplicação
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🚀 Step 14: Starting Application${NC}"
echo -e "${BLUE}=================================================================================${NC}"

ssh_exec << 'EOF'
systemctl start financial-app
sleep 3
systemctl status financial-app --no-pager
echo ""
echo "✅ Application started"
EOF

# Passo 15: Verificar saúde
echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}🏥 Step 15: Health Check${NC}"
echo -e "${BLUE}=================================================================================${NC}"

sleep 5

if ssh_exec "curl -f -s http://127.0.0.1:5000/ > /dev/null"; then
    echo -e "${GREEN}✅ Application is responding${NC}"
else
    echo -e "${RED}❌ Application is not responding${NC}"
    ssh_exec "journalctl -u financial-app -n 50 --no-pager"
    exit 1
fi

# Resumo Final
echo ""
echo -e "${GREEN}=================================================================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}=================================================================================${NC}"
echo ""
echo -e "🌐 Application URL: ${BLUE}http://148.230.78.91${NC}"
echo ""
echo -e "📊 Useful Commands:"
echo -e "  ${YELLOW}Check status:${NC}    ssh -i $SSH_KEY root@148.230.78.91 'systemctl status financial-app'"
echo -e "  ${YELLOW}View logs:${NC}       ssh -i $SSH_KEY root@148.230.78.91 'journalctl -u financial-app -f'"
echo -e "  ${YELLOW}Restart app:${NC}     ssh -i $SSH_KEY root@148.230.78.91 'systemctl restart financial-app'"
echo -e "  ${YELLOW}View backups:${NC}    ssh -i $SSH_KEY root@148.230.78.91 'ls -lh /backups/financial-app/'"
echo ""
echo -e "🔒 Next Steps:"
echo -e "  1. Test application: http://148.230.78.91"
echo -e "  2. Login with your credentials"
echo -e "  3. Verify transactions are visible"
echo -e "  4. Optional: Configure domain + SSL (Let's Encrypt)"
echo ""
echo -e "${BLUE}=================================================================================${NC}"
