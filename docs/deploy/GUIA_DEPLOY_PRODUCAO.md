# 🚀 GUIA DE DEPLOY EM PRODUÇÃO - Sistema de Finanças V5

**Engenheiro DevOps/SecOps:** Guia de Implementação (Runbook)  
**Stack:** FastAPI (Backend) + Next.js (Frontend) + PostgreSQL  
**Foco:** Security by Design para dados financeiros sensíveis

---

## 📋 ÍNDICE

1. [Pré-Requisitos](#1-pré-requisitos)
2. [Hardening do Servidor (Infraestrutura)](#2-hardening-do-servidor)
3. [Gestão de Segredos e Variáveis](#3-gestão-de-segredos)
4. [Banco de Dados Seguro](#4-banco-de-dados-seguro)
5. [Deploy da Aplicação](#5-deploy-da-aplicação)
6. [Servidor Web e HTTPS](#6-servidor-web-e-https)
7. [Monitoramento e Manutenção](#7-monitoramento-e-manutenção)
8. [Backup Automatizado](#8-backup-automatizado)
9. [Rollback e Disaster Recovery](#9-rollback-e-disaster-recovery)

---

## 1. PRÉ-REQUISITOS

### Informações Necessárias

- **VPS:** Ubuntu 22.04 LTS (limpo)
- **IP do servidor:** `SEU_IP_AQUI`
- **Domínio:** `seu-dominio.com` (apontando para o IP)
- **Email para SSL:** `seu-email@example.com`

### Acesso Inicial

```bash
# Conectar como root pela primeira vez
ssh root@SEU_IP_AQUI
```

---

## 2. HARDENING DO SERVIDOR

### 2.1. Atualizar Sistema

**Por quê:** Patches de segurança críticos devem ser aplicados antes de qualquer configuração.

```bash
apt update && apt upgrade -y
apt install -y curl git ufw fail2ban nginx certbot python3-certbot-nginx
```

### 2.2. Criar Usuário Administrativo (Sem Root)

**Por quê:** Usar root diretamente é perigoso. Um usuário sudo com acesso limitado reduz vetores de ataque.

```bash
# Criar usuário 'deploy' (escolha outro nome se preferir)
adduser deploy

# Adicionar ao grupo sudo
usermod -aG sudo deploy

# Testar acesso sudo
su - deploy
sudo whoami  # Deve retornar 'root'
exit
```

### 2.3. Configurar SSH com Chaves (Desabilitar Senhas)

**Por quê:** Login por senha é vulnerável a ataques de força bruta. SSH Keys são exponencialmente mais seguros.

#### 2.3.1. Gerar chave SSH no SEU COMPUTADOR LOCAL (se não tiver)

```bash
# No seu Mac (local)
ssh-keygen -t ed25519 -C "seu-email@example.com" -f ~/.ssh/id_financas_vps

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/id_financas_vps.pub deploy@SEU_IP_AQUI
```

#### 2.3.2. Configurar SSH no Servidor

```bash
# No servidor, como usuário 'deploy'
sudo nano /etc/ssh/sshd_config
```

**Editar/adicionar estas linhas:**

```bash
# Porta customizada (opcional mas recomendado)
Port 2222

# Desabilitar root login
PermitRootLogin no

# Desabilitar autenticação por senha
PasswordAuthentication no
PubkeyAuthentication yes

# Desabilitar login vazio
PermitEmptyPasswords no

# Limite de tentativas
MaxAuthTries 3

# Timeout de login
LoginGraceTime 20
```

**Reiniciar SSH:**

```bash
sudo systemctl restart sshd

# ⚠️ NÃO FECHE A SESSÃO ATUAL! Teste em nova aba:
ssh -i ~/.ssh/id_financas_vps -p 2222 deploy@SEU_IP_AQUI
```

### 2.4. Configurar Firewall (UFW)

**Por quê:** Bloquear todas as portas exceto as necessárias é a primeira linha de defesa contra invasões.

```bash
# Desabilitar IPv6 (opcional, se não usar)
sudo nano /etc/default/ufw
# Adicionar: IPV6=no

# Configurações básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (porta customizada se mudou)
sudo ufw allow 2222/tcp comment 'SSH'

# Permitir HTTP e HTTPS (Nginx)
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# IMPORTANTE: NÃO permitir portas 8000 (FastAPI) e 3000 (Next.js)
# Elas devem ficar APENAS em localhost (Nginx fará proxy)

# Ativar firewall
sudo ufw enable

# Verificar status
sudo ufw status verbose
```

### 2.5. Configurar Fail2Ban (Anti Força-Bruta)

**Por quê:** Bloqueia IPs que tentam múltiplos logins falhos, protegendo contra bots de força bruta.

```bash
# Criar configuração local
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

**Configuração mínima:**

```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 3
destemail = seu-email@example.com
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = 2222
logpath = /var/log/auth.log
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
```

**Iniciar serviço:**

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verificar status
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

---

## 3. GESTÃO DE SEGREDOS

### 3.1. Preparar Diretório da Aplicação

```bash
# Criar estrutura
sudo mkdir -p /var/www/financas
sudo chown deploy:deploy /var/www/financas
cd /var/www/financas
```

### 3.2. Clonar Repositório (Git)

**⚠️ CRÍTICO:** NUNCA commite arquivos `.env` no Git!

```bash
# Instalar Git LFS (se usar arquivos grandes)
sudo apt install git-lfs
git lfs install

# Clonar repositório (use SSH para segurança)
git clone git@github.com:SEU_USUARIO/ProjetoFinancasV5.git .

# Ou via HTTPS (menos seguro)
# git clone https://github.com/SEU_USUARIO/ProjetoFinancasV5.git .
```

### 3.3. Criar Arquivo .env do Backend (SEGURO)

**Por quê:** Variáveis de ambiente não devem estar hardcoded. Arquivo `.env` centraliza segredos com permissões restritas.

```bash
cd /var/www/financas/app_dev/backend
nano .env
```

**Conteúdo do `.env`:**

```bash
# ========================================
# CONFIGURAÇÕES DE PRODUÇÃO
# ⚠️ NUNCA COMMITAR ESTE ARQUIVO NO GIT
# ========================================

# App
APP_NAME="Sistema de Finanças API"
APP_VERSION="1.0.0"
DEBUG=false

# Database PostgreSQL
DATABASE_URL="postgresql://financas_user:SENHA_SUPER_SEGURA_AQUI@127.0.0.1:5432/financas_db"

# CORS (domínio público)
BACKEND_CORS_ORIGINS="https://seu-dominio.com,https://www.seu-dominio.com"

# Server
HOST="127.0.0.1"  # ⚠️ IMPORTANTE: APENAS localhost!
PORT=8000

# JWT Authentication
JWT_SECRET_KEY="GERE_UMA_STRING_ALEATORIA_DE_64_CARACTERES_AQUI"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Gerar JWT Secret seguro:**

```bash
openssl rand -hex 32
# Copie o output e cole em JWT_SECRET_KEY
```

**Configurar permissões (CRUCIAL):**

```bash
# Apenas dono (deploy) pode ler/escrever
chmod 600 .env
chown deploy:deploy .env

# Verificar
ls -la .env
# Deve mostrar: -rw------- 1 deploy deploy
```

### 3.4. Criar .env do Frontend

```bash
cd /var/www/financas/app_dev/frontend
nano .env.production
```

**Conteúdo:**

```bash
NEXT_PUBLIC_API_URL=https://seu-dominio.com/api
NODE_ENV=production
```

**Permissões:**

```bash
chmod 600 .env.production
chown deploy:deploy .env.production
```

### 3.5. Garantir .env no .gitignore

```bash
cd /var/www/financas
cat .gitignore | grep ".env"

# Se não tiver, adicionar:
echo "*.env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore
```

---

## 4. BANCO DE DADOS SEGURO

### 4.1. Instalar PostgreSQL

**Por quê:** SQLite não é adequado para produção (sem controle de acesso, lock issues, sem rede). PostgreSQL é robusto e seguro.

```bash
sudo apt install -y postgresql postgresql-contrib
```

### 4.2. Configurar PostgreSQL para Localhost APENAS

**Por quê:** Banco de dados NUNCA deve ser exposto publicamente. Apenas a aplicação local deve acessá-lo.

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

**Editar linha:**

```ini
# Escutar APENAS em localhost
listen_addresses = '127.0.0.1'
```

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

**Configuração mínima:**

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Usuário financas_user via senha (localhost)
local   financas_db     financas_user                           scram-sha-256
host    financas_db     financas_user   127.0.0.1/32            scram-sha-256

# Bloquear todo o resto (comentar regras padrão permissivas)
```

**Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
```

### 4.3. Criar Banco e Usuário com Privilégios Mínimos

**Por quê:** Princípio do menor privilégio (PoLP). Usuário da aplicação não deve ter poderes administrativos.

```bash
sudo -u postgres psql
```

**Dentro do psql:**

```sql
-- Criar banco
CREATE DATABASE financas_db;

-- Criar usuário com senha forte
CREATE USER financas_user WITH ENCRYPTED PASSWORD 'SENHA_SUPER_SEGURA_AQUI';

-- Garantir privilégios APENAS no banco específico
GRANT CONNECT ON DATABASE financas_db TO financas_user;

\c financas_db

-- Privilégios mínimos (CRUD tables)
GRANT USAGE ON SCHEMA public TO financas_user;
GRANT CREATE ON SCHEMA public TO financas_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO financas_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO financas_user;

-- Futuras tabelas automaticamente
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO financas_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO financas_user;

\q
```

### 4.4. Migrar Dados de SQLite para PostgreSQL

```bash
cd /var/www/financas/app_dev/backend

# Instalar ferramenta de migração
pip install pgloader

# Criar script de migração (no servidor)
nano migrate_to_postgres.sh
```

**Script:**

```bash
#!/bin/bash
SQLITE_PATH="/caminho/backup/financas_dev.db"
PG_URL="postgresql://financas_user:SENHA@127.0.0.1:5432/financas_db"

pgloader $SQLITE_PATH $PG_URL
```

**Executar:**

```bash
chmod +x migrate_to_postgres.sh
./migrate_to_postgres.sh
```

### 4.5. Testar Conexão

```bash
# Testar acesso via aplicação
cd /var/www/financas/app_dev/backend
source venv/bin/activate
python -c "from app.core.database import engine; print(engine.connect())"
```

---

## 5. DEPLOY DA APLICAÇÃO

### 5.1. Configurar Ambiente Python (Backend)

```bash
cd /var/www/financas/app_dev/backend

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Criar venv
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Ajustar SQLAlchemy para PostgreSQL
pip install psycopg2-binary
```

### 5.2. Atualizar config.py para Produção

```bash
nano app/core/config.py
```

**Modificar para ler DATABASE_URL do .env:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8'
    )
    
    APP_NAME: str = "Sistema de Finanças API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # ⚠️ PRODUÇÃO
    
    # Database - Agora PostgreSQL via .env
    DATABASE_URL: str
    
    BACKEND_CORS_ORIGINS: Union[list[str], str]
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
```

### 5.3. Criar Serviço Systemd (Backend)

**Por quê:** Systemd gerencia o processo, reinicia em caso de crash, e inicia no boot.

```bash
sudo nano /etc/systemd/system/financas-backend.service
```

**Conteúdo:**

```ini
[Unit]
Description=Sistema Financeiro - FastAPI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/financas/app_dev/backend
Environment="PATH=/var/www/financas/app_dev/backend/venv/bin"
ExecStart=/var/www/financas/app_dev/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2

# Segurança
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/financas/app_dev/backend/database

# Restart em caso de falha
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Habilitar e iniciar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable financas-backend
sudo systemctl start financas-backend

# Verificar status
sudo systemctl status financas-backend

# Logs
sudo journalctl -u financas-backend -f
```

### 5.4. Configurar Frontend (Next.js)

```bash
cd /var/www/financas/app_dev/frontend

# Instalar Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar dependências
npm ci --production

# Build otimizado
npm run build
```

### 5.5. Criar Serviço Systemd (Frontend)

```bash
sudo nano /etc/systemd/system/financas-frontend.service
```

**Conteúdo:**

```ini
[Unit]
Description=Sistema Financeiro - Next.js Frontend
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/financas/app_dev/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start

# Segurança
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true

# Restart
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Habilitar e iniciar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable financas-frontend
sudo systemctl start financas-frontend

# Verificar
sudo systemctl status financas-frontend
```

---

## 6. SERVIDOR WEB E HTTPS

### 6.1. Configurar Nginx como Reverse Proxy

**Por quê:** Nginx esconde as portas internas (8000, 3000), adiciona segurança, compressão, e facilita SSL.

```bash
sudo nano /etc/nginx/sites-available/financas
```

**Configuração completa com segurança:**

```nginx
# Redirecionar HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Permitir Certbot
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Principal
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;

    # SSL (Certbot vai preencher automaticamente)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # SSL Moderno (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # ========================================
    # CABEÇALHOS DE SEGURANÇA (CRÍTICOS)
    # ========================================
    
    # HSTS (6 meses) - Forçar HTTPS no browser
    add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload" always;
    
    # Bloquear Clickjacking
    add_header X-Frame-Options "DENY" always;
    
    # Bloquear MIME Sniffing
    add_header X-Content-Type-Options "nosniff" always;
    
    # XSS Protection (legacy mas não faz mal)
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Referrer Policy (privacidade)
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Content Security Policy (CSP) - AJUSTE conforme necessário
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://seu-dominio.com; frame-ancestors 'none';" always;
    
    # Permissions Policy (Feature Policy)
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # ========================================
    # PROXY PARA FRONTEND (Next.js)
    # ========================================
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # ========================================
    # PROXY PARA BACKEND (FastAPI)
    # ========================================
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate Limiting (anti DDoS básico)
        limit_req zone=api burst=20 nodelay;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Bloquear acesso direto a arquivos sensíveis
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Logs
    access_log /var/log/nginx/financas_access.log;
    error_log /var/log/nginx/financas_error.log warn;
}

# Rate Limiting Zone (definir no http block do nginx.conf)
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

**Habilitar site:**

```bash
sudo ln -s /etc/nginx/sites-available/financas /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remover site padrão

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 6.2. Instalar Certificado SSL (Let's Encrypt)

**Por quê:** HTTPS criptografa toda comunicação. Obrigatório para dados financeiros (PCI DSS, LGPD).

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado (automático via Nginx)
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com --email seu-email@example.com --agree-tos --no-eff-email --redirect

# Testar renovação automática
sudo certbot renew --dry-run
```

**Certbot configura renovação automática via cron/systemd timer (certificados expiram em 90 dias).**

### 6.3. Validar Segurança SSL

**Testar em:** https://www.ssllabs.com/ssltest/

**Meta:** Nota A+ no SSL Labs

---

## 7. MONITORAMENTO E MANUTENÇÃO

### 7.1. Logs Centralizados

```bash
# Backend (FastAPI)
sudo journalctl -u financas-backend -f

# Frontend (Next.js)
sudo journalctl -u financas-frontend -f

# Nginx
sudo tail -f /var/log/nginx/financas_access.log
sudo tail -f /var/log/nginx/financas_error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### 7.2. Monitoramento de Recursos

```bash
# Instalar htop
sudo apt install htop

# Monitorar em tempo real
htop

# Ou usar glances (mais completo)
sudo apt install glances
glances
```

### 7.3. Alertas de Disco/Memória

```bash
# Criar script de alerta
sudo nano /usr/local/bin/check_resources.sh
```

**Script:**

```bash
#!/bin/bash
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERTA: Disco em ${DISK_USAGE}%" | mail -s "Alerta Disco VPS" seu-email@example.com
fi

if [ $MEM_USAGE -gt 80 ]; then
    echo "ALERTA: Memória em ${MEM_USAGE}%" | mail -s "Alerta Memória VPS" seu-email@example.com
fi
```

**Agendar no cron (diário):**

```bash
sudo chmod +x /usr/local/bin/check_resources.sh
sudo crontab -e

# Adicionar:
0 9 * * * /usr/local/bin/check_resources.sh
```

---

## 8. BACKUP AUTOMATIZADO

### 8.1. Script de Backup PostgreSQL

```bash
sudo nano /usr/local/bin/backup_financas.sh
```

**Script:**

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/financas"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
sudo -u postgres pg_dump financas_db | gzip > $BACKUP_DIR/financas_db_${DATE}.sql.gz

# Backup arquivos de configuração
tar -czf $BACKUP_DIR/config_${DATE}.tar.gz /var/www/financas/app_dev/backend/.env /var/www/financas/app_dev/frontend/.env.production

# Remover backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "[$(date)] Backup concluído: financas_db_${DATE}.sql.gz" >> /var/log/backup_financas.log

# Opcional: Enviar para S3/Backblaze/rsync remoto
# aws s3 cp $BACKUP_DIR/financas_db_${DATE}.sql.gz s3://seu-bucket/backups/
```

**Agendar backup diário:**

```bash
sudo chmod +x /usr/local/bin/backup_financas.sh
sudo crontab -e

# Backup diário às 3h da manhã
0 3 * * * /usr/local/bin/backup_financas.sh
```

### 8.2. Backup Inicial Manual

```bash
sudo /usr/local/bin/backup_financas.sh
ls -lh /var/backups/financas/
```

---

## 9. ROLLBACK E DISASTER RECOVERY

### 9.1. Restaurar Banco de Dados

```bash
# Listar backups disponíveis
ls -lh /var/backups/financas/

# Restaurar backup específico
gunzip < /var/backups/financas/financas_db_20260121_030000.sql.gz | sudo -u postgres psql financas_db
```

### 9.2. Rollback de Código (Git)

```bash
cd /var/www/financas

# Ver commits recentes
git log --oneline -10

# Voltar para commit específico
git checkout <commit-hash>

# Reiniciar serviços
sudo systemctl restart financas-backend financas-frontend
```

### 9.3. Procedimento de Emergência

**Se o site cair:**

```bash
# 1. Verificar status dos serviços
sudo systemctl status financas-backend
sudo systemctl status financas-frontend
sudo systemctl status nginx
sudo systemctl status postgresql

# 2. Verificar logs
sudo journalctl -u financas-backend -n 50 --no-pager
sudo journalctl -u financas-frontend -n 50 --no-pager

# 3. Reiniciar serviços problemáticos
sudo systemctl restart financas-backend
sudo systemctl restart financas-frontend

# 4. Verificar conectividade
curl -I https://seu-dominio.com
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:3000
```

---

## 📋 CHECKLIST FINAL DE SEGURANÇA

Antes de considerar o deploy concluído, verificar:

- [ ] ✅ Root login SSH está DESABILITADO
- [ ] ✅ Login por senha SSH está DESABILITADO (apenas chaves)
- [ ] ✅ Firewall UFW está ATIVO e configurado
- [ ] ✅ Fail2Ban está ATIVO e monitorando SSH
- [ ] ✅ PostgreSQL escuta APENAS em 127.0.0.1
- [ ] ✅ FastAPI escuta APENAS em 127.0.0.1 (Nginx faz proxy)
- [ ] ✅ Next.js escuta APENAS em 127.0.0.1 (Nginx faz proxy)
- [ ] ✅ Arquivo `.env` tem permissões 600 (apenas dono lê)
- [ ] ✅ JWT_SECRET_KEY é ÚNICO e ALEATÓRIO (64+ chars)
- [ ] ✅ Senha do PostgreSQL é FORTE (16+ chars, aleatória)
- [ ] ✅ SSL/HTTPS está ATIVO (Certbot configurado)
- [ ] ✅ SSL Labs retorna nota A ou A+
- [ ] ✅ Cabeçalhos de segurança estão ativos (HSTS, CSP, etc)
- [ ] ✅ Backup automático está AGENDADO (cron)
- [ ] ✅ DEBUG está FALSE no backend (.env)
- [ ] ✅ CORS está restrito ao domínio público (não `*`)
- [ ] ✅ Monitoramento de recursos está ATIVO
- [ ] ✅ Logs estão sendo escritos corretamente
- [ ] ✅ Serviços reiniciam automaticamente em caso de crash
- [ ] ✅ Testado rollback manual (restaurar backup)

---

## 🎯 PRÓXIMOS PASSOS (Opcional - Melhorias Futuras)

### Segurança Avançada

1. **WAF (Web Application Firewall):**
   - Cloudflare (grátis) ou ModSecurity

2. **IDS/IPS:**
   - Instalar OSSEC ou Wazuh para detecção de intrusões

3. **2FA para SSH:**
   - Google Authenticator + PAM

4. **Gestão de Segredos Profissional:**
   - HashiCorp Vault ou AWS Secrets Manager

### Performance

1. **CDN:**
   - Cloudflare ou AWS CloudFront para assets estáticos

2. **Caching:**
   - Redis para cache de sessões/API

3. **Database Pooling:**
   - PgBouncer para gerenciar conexões PostgreSQL

### Monitoramento Profissional

1. **APM (Application Performance Monitoring):**
   - New Relic, Datadog, ou self-hosted Grafana + Prometheus

2. **Error Tracking:**
   - Sentry para capturar erros em tempo real

3. **Uptime Monitoring:**
   - UptimeRobot ou Pingdom (alertas se site cair)

---

## 📚 REFERÊNCIAS

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Mozilla SSL Config:** https://ssl-config.mozilla.org/
- **CIS Benchmarks Ubuntu:** https://www.cisecurity.org/benchmark/ubuntu_linux
- **LGPD:** https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd
- **PCI DSS:** https://www.pcisecuritystandards.org/

---

## 🆘 SUPORTE E CONTATOS

**Documentação Interna:**
- GUIA_SERVIDORES.md (desenvolvimento)
- DATABASE_CONFIG.md
- PLANO_AUTENTICACAO.md

**Em caso de problemas:**
1. Verificar logs: `sudo journalctl -u financas-backend -n 100`
2. Testar conectividade: `curl http://127.0.0.1:8000/api/health`
3. Revisar configurações: `.env`, `nginx.conf`, `systemd services`

---

**Última atualização:** 21 de janeiro de 2026  
**Versão do Guia:** 1.0.0  
**Responsável:** DevOps/SecOps Team
