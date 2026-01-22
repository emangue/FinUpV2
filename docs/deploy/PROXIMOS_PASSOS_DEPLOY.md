# 🎉 LIMPEZA CONCLUÍDA - PRÓXIMOS PASSOS

**Data:** 21 de janeiro de 2026  
**Status:** ✅ Servidor limpo | ✅ Repositório criado | ⏳ Aguardando push GitHub

---

## ✅ O QUE JÁ FOI FEITO

### 1️⃣ **Servidor Limpo (148.230.78.91)**

| Ação | Status |
|------|--------|
| Backup dos 3 deploys antigos | ✅ Salvo em `/root/backups_pre_deploy/` |
| Parada de todos os processos | ✅ Concluída |
| Remoção `/opt/financial-app/` | ✅ Removido |
| Remoção `/var/www/financas/` | ✅ Removido |
| Remoção `/var/www/financas_completo/` | ✅ Removido |
| Configs Nginx antigas | ✅ Removidas |
| Criação usuário `deploy` | ✅ Criado com sudo |
| Python 3.12 instalado | ✅ Instalado |
| PostgreSQL instalado e ativo | ✅ Rodando |
| Node.js 20 LTS instalado | ✅ v20.20.0 |
| Nginx ativo | ✅ Rodando |

**Servidor está LIMPO e PRONTO para deploy!** 🧹

---

### 2️⃣ **Repositório FinUp Criado**

| Ação | Status |
|------|--------|
| Novo diretório `FinUp` | ✅ Criado |
| Cópia `app_dev/` | ✅ Copiado |
| `.gitignore` completo | ✅ Criado |
| `README.md` profissional | ✅ Criado |
| `.env.example` documentado | ✅ Criado |
| `GUIA_DEPLOY_PRODUCAO.md` | ✅ Copiado |
| Commit inicial | ✅ Feito (377 arquivos) |

**Local:** `/Users/emangue/Documents/ProjetoVSCode/FinUp`

---

## 🚀 PRÓXIMOS PASSOS (EXECUTE MANUALMENTE)

### PASSO 1: Publicar no GitHub

```bash
cd /Users/emangue/Documents/ProjetoVSCode/FinUp

# Adicionar remote (se não fez)
git remote add origin https://github.com/emangue/FinUp.git

# Push para GitHub
git push -u origin main
```

**Será solicitado login do GitHub (use token de acesso pessoal).**

---

### PASSO 2: Clonar no Servidor

```bash
# Conectar ao servidor
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# Criar diretório para a aplicação
sudo mkdir -p /var/www/finup
sudo chown deploy:deploy /var/www/finup

# Trocar para usuário deploy
su - deploy
cd /var/www/finup

# Clonar repositório
git clone https://github.com/emangue/FinUp.git .

# Verificar estrutura
ls -la
```

---

### PASSO 3: Configurar PostgreSQL

```bash
# No servidor, como root
sudo -u postgres psql

# No psql:
CREATE DATABASE finup_db;
CREATE USER finup_user WITH ENCRYPTED PASSWORD 'SENHA_SUPER_SEGURA';
GRANT ALL PRIVILEGES ON DATABASE finup_db TO finup_user;
\q
```

**Gerar senha forte:**
```bash
openssl rand -base64 24
```

---

### PASSO 4: Configurar Backend

```bash
# Como usuário deploy
cd /var/www/finup/app_dev/backend

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary  # PostgreSQL adapter

# Criar .env
nano .env
```

**Conteúdo do `.env`:**
```bash
APP_NAME="FinUp"
APP_VERSION="1.0.0"
DEBUG=false

# PostgreSQL
DATABASE_URL=postgresql://finup_user:SUA_SENHA_AQUI@127.0.0.1:5432/finup_db

# CORS (seu domínio)
BACKEND_CORS_ORIGINS=https://seu-dominio.com

# Server
HOST=127.0.0.1
PORT=8000

# JWT (gerar com: openssl rand -hex 32)
JWT_SECRET_KEY=COLE_AQUI_64_CARACTERES_ALEATORIOS
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Gerar JWT Secret:**
```bash
openssl rand -hex 32
```

**Salvar e proteger:**
```bash
chmod 600 .env
```

**Inicializar banco:**
```bash
# Se tiver script init_db.py
python init_db.py

# Ou rodar migrations
python app/domains/*/scripts/migrate_*.py
```

---

### PASSO 5: Criar Systemd Service (Backend)

```bash
# Como root
sudo nano /etc/systemd/system/finup-backend.service
```

**Conteúdo:**
```ini
[Unit]
Description=FinUp Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/finup/app_dev/backend
Environment="PATH=/var/www/finup/app_dev/backend/venv/bin"
ExecStart=/var/www/finup/app_dev/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2

PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/finup/app_dev/backend/database

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Ativar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable finup-backend
sudo systemctl start finup-backend
sudo systemctl status finup-backend
```

---

### PASSO 6: Configurar Frontend

```bash
# Como usuário deploy
cd /var/www/finup/app_dev/frontend

# Instalar dependências
npm ci

# Criar .env.production
nano .env.production
```

**Conteúdo:**
```bash
NEXT_PUBLIC_API_URL=https://seu-dominio.com/api/v1
NODE_ENV=production
```

**Build:**
```bash
npm run build
```

---

### PASSO 7: Criar Systemd Service (Frontend)

```bash
# Como root
sudo nano /etc/systemd/system/finup-frontend.service
```

**Conteúdo:**
```ini
[Unit]
Description=FinUp Frontend
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/finup/app_dev/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start

PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Ativar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable finup-frontend
sudo systemctl start finup-frontend
sudo systemctl status finup-frontend
```

---

### PASSO 8: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/finup
```

**Conteúdo completo em:** `GUIA_DEPLOY_PRODUCAO.md` (seção 6.1)

**Resumo:**
- Proxy `/` → Frontend (porta 3000)
- Proxy `/api/` → Backend (porta 8000)
- SSL/HTTPS com Certbot
- Cabeçalhos de segurança (HSTS, CSP, etc)

**Ativar:**
```bash
sudo ln -s /etc/nginx/sites-available/finup /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### PASSO 9: Instalar SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

### PASSO 10: Configurar Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
sudo ufw status
```

---

## 📊 ARQUIVOS DE BACKUP NO SERVIDOR

**Localização:** `/root/backups_pre_deploy/`

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `easypanel_financas_*.db` | 132KB | SQLite Easypanel (Flask antigo) |
| `financas_completo_*.db` | 2.6MB | SQLite financas_completo (FastAPI) |
| `nginx_financial_app.conf` | 1.5KB | Config Nginx antiga |

**Para restaurar dados (se necessário):**
```bash
# Converter SQLite → PostgreSQL
sudo apt install pgloader
pgloader /root/backups_pre_deploy/financas_completo_*.db postgresql://finup_user:senha@localhost/finup_db
```

---

## 🔍 TROUBLESHOOTING

### Backend não inicia
```bash
sudo journalctl -u finup-backend -n 50
```

### Frontend não inicia
```bash
sudo journalctl -u finup-frontend -n 50
```

### Nginx erros
```bash
sudo tail -f /var/log/nginx/error.log
```

### PostgreSQL erros
```bash
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

---

## ✅ CHECKLIST FINAL

Antes de considerar deploy completo:

- [ ] GitHub: `FinUp` publicado
- [ ] Servidor: Repositório clonado em `/var/www/finup`
- [ ] PostgreSQL: Banco `finup_db` criado e funcional
- [ ] Backend: `.env` configurado com senhas seguras
- [ ] Backend: Service rodando (`systemctl status finup-backend`)
- [ ] Frontend: Build concluído (`npm run build`)
- [ ] Frontend: Service rodando (`systemctl status finup-frontend`)
- [ ] Nginx: Configurado e testado (`nginx -t`)
- [ ] SSL: Certificado instalado (Certbot)
- [ ] Firewall: UFW ativo com regras corretas
- [ ] Teste: Site acessível via `https://seu-dominio.com`
- [ ] Teste: API acessível via `https://seu-dominio.com/docs`
- [ ] Teste: Login funcionando

---

## 🎯 DOCUMENTAÇÃO COMPLETA

Ver: `/Users/emangue/Documents/ProjetoVSCode/FinUp/GUIA_DEPLOY_PRODUCAO.md`

---

**Status Atual:**
- ✅ Servidor limpo e preparado
- ✅ Repositório FinUp criado localmente
- ⏳ Aguardando push para GitHub
- ⏳ Aguardando configuração final no servidor

**Próximo: Execute PASSO 1 (push GitHub) e continue sequencialmente!** 🚀
