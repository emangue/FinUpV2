# Infraestrutura e Ambiente de Produção - FinUp

**Data:** 31/01/2026  
**Versão:** 1.0  
**Status:** Documentação completa da infraestrutura

---

## 🌍 Visão Geral

### Ambientes

| Ambiente | Localização | Banco | URL | Status |
|----------|-------------|-------|-----|--------|
| **Desenvolvimento** | Local (Mac) | SQLite | http://localhost:3000 | ✅ Ativo |
| **Produção** | VPS Hostinger | PostgreSQL | https://finup.srv1045889.hstgr.cloud/ | ✅ Ativo |

---

## 🖥️ Servidor de Produção

### Informações Básicas

| Item | Valor |
|------|-------|
| **IP Público** | 64.23.241.43 |
| **Hostname** | srv1045889.hstgr.cloud |
| **Provider** | Hostinger VPS |
| **Sistema Operacional** | Linux (Ubuntu/Debian) |
| **Usuário SSH** | root |
| **Path da Aplicação** | `/var/www/finup` |
| **Alias SSH** | `minha-vps-hostinger` |

### Softwares Instalados

| Software | Versão | Uso |
|----------|--------|-----|
| **Python** | 3.12.3 | Backend FastAPI |
| **Node.js** | 20.20.0 | Frontend Next.js |
| **PostgreSQL** | 16.x | Banco de dados |
| **Nginx** | Latest | Reverse proxy + SSL |
| **systemd** | - | Process manager |

---

## 🗄️ Banco de Dados

### Desenvolvimento (SQLite)

**Path:** `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db`

**Connection String:**
```
sqlite:///app_dev/backend/database/financas_dev.db
```

**Características:**
- ✅ Arquivo local (portabilidade)
- ✅ Sem instalação de servidor
- ✅ Backup simples (copiar arquivo)
- ⚠️ Single-user
- ⚠️ Sem replicação

---

### Produção (PostgreSQL)

**Host:** 127.0.0.1 (localhost no servidor)  
**Porta:** 5432  
**Database:** `finup_db`  
**Usuário:** `finup_user`  
**Senha:** `FinUp2026SecurePass` (⚠️ deve ser trocada em produção real)

**Connection String:**
```
postgresql://finup_user:FinUp2026SecurePass@127.0.0.1:5432/finup_db
```

**Características:**
- ✅ Multi-user concurrent
- ✅ ACID compliant
- ✅ Replicação e backup nativos
- ✅ Performance superior (índices, query planner)
- ✅ Schema idêntico ao SQLite (SQLAlchemy abstrai diferenças)

---

## 🔧 Configuração de Ambientes

### Arquivo `.env` (Desenvolvimento)

**Path:** `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/.env`

```bash
# App
APP_NAME=Sistema de Finanças API
APP_VERSION=1.0.0
DEBUG=true

# Database - SQLite (padrão, DATABASE_URL vazio)
# DATABASE_URL=   # Vazio = usa SQLite

# Ou PostgreSQL local (opcional)
# DATABASE_URL=postgresql://finup_user:senha@localhost:5432/finup_db_dev

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Server
HOST=0.0.0.0
PORT=8000
```

---

### Arquivo `.env` (Produção)

**Path:** `/var/www/finup/app_dev/backend/.env`

```bash
# App
APP_NAME=Sistema de Finanças API
APP_VERSION=1.0.0
DEBUG=false  # ⚠️ SEMPRE false em produção

# Database - PostgreSQL
DATABASE_URL=postgresql://finup_user:FinUp2026SecurePass@127.0.0.1:5432/finup_db

# JWT (⚠️ deve ser diferente de dev)
JWT_SECRET_KEY=<secret_64_chars_gerado_com_openssl>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (⚠️ usar domínio real)
BACKEND_CORS_ORIGINS=https://finup.srv1045889.hstgr.cloud

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 🚀 Deploy

### SSH Access

**Configuração no `~/.ssh/config`:**

```
Host minha-vps-hostinger
    HostName 64.23.241.43
    User root
    IdentityFile ~/.ssh/id_rsa_hostinger
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

**Comandos úteis:**

```bash
# Conectar via SSH
ssh minha-vps-hostinger

# Executar comando remoto
ssh minha-vps-hostinger 'comando'

# Transferir arquivos (rsync)
rsync -avz --exclude 'node_modules' local/ minha-vps-hostinger:/var/www/finup/
```

---

### Processo de Deploy Seguro

**Script:** `scripts/deploy/deploy_safe_v2.sh`

**Fluxo:**

```bash
# 1. Validações Locais
✅ Git status (deve estar limpo)
✅ Sincronização com remoto
✅ Sintaxe Python válida
✅ Migrations (se necessário)

# 2. Backup Automático no Servidor
💾 Backup do banco PostgreSQL
💾 Backup do código atual (commit hash)

# 3. Deploy
📥 Git pull origin main
🗄️ Alembic upgrade head (se --with-migrations)
🔄 Restart systemd services

# 4. Validações Pós-Deploy
✅ Backend ativo (systemctl is-active)
✅ Health check (GET /api/health)
✅ Autenticação protegida (GET /api/v1/auth/me → 401)

# 5. Rollback Automático (se falhar)
🔙 git checkout HEAD~1
🔄 systemctl restart finup-backend
```

**Uso:**

```bash
# Deploy simples
./scripts/deploy/deploy_safe_v2.sh

# Deploy com migrations
./scripts/deploy/deploy_safe_v2.sh --with-migrations
```

---

## 🔐 Segurança

### Credenciais (⚠️ NUNCA commitar!)

**Arquivo:** `.env.deploy` (local, `.gitignore`)

```bash
SERVER_USER=root
SERVER_HOST=64.23.241.43
SERVER_PASSWORD=5CX.MvU;8ql,gWW,Rz;a
SERVER_APP_PATH=/var/www/finup
```

**Chaves SSH:**
- `~/.ssh/id_rsa_hostinger` (RSA 4096 bits)
- `~/.ssh/id_ed25519_deploy` (ED25519)

---

### Boas Práticas

1. ✅ **NUNCA** commitar `.env` no git
2. ✅ Usar senhas fortes (mín. 32 caracteres)
3. ✅ JWT_SECRET_KEY diferente por ambiente
4. ✅ `DEBUG=false` em produção
5. ✅ CORS restrito ao domínio real
6. ✅ Trocar senha PostgreSQL periodicamente (3 meses)
7. ✅ Backup diário automático

---

## 🔄 Systemd Services

### Backend Service

**Path:** `/etc/systemd/system/finup-backend.service`

```ini
[Unit]
Description=FinUp Backend API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/finup/app_dev/backend
Environment="PATH=/var/www/finup/app_dev/venv/bin"
ExecStart=/var/www/finup/app_dev/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Comandos:**

```bash
# Iniciar
sudo systemctl start finup-backend

# Parar
sudo systemctl stop finup-backend

# Restart
sudo systemctl restart finup-backend

# Status
sudo systemctl status finup-backend

# Logs
sudo journalctl -u finup-backend -f
```

---

### Frontend Service

**Path:** `/etc/systemd/system/finup-frontend.service`

```ini
[Unit]
Description=FinUp Frontend Next.js
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/finup/app_dev/frontend
Environment="PATH=/usr/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 🌐 Nginx

**Config:** `/etc/nginx/sites-available/finup`

```nginx
server {
    listen 80;
    server_name finup.srv1045889.hstgr.cloud;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# Backend
ssh minha-vps-hostinger 'journalctl -u finup-backend -f'

# Frontend
ssh minha-vps-hostinger 'journalctl -u finup-frontend -f'

# Nginx
ssh minha-vps-hostinger 'journalctl -u nginx -f'

# PostgreSQL
ssh minha-vps-hostinger 'journalctl -u postgresql -f'
```

---

### Health Checks

```bash
# Backend health
curl https://finup.srv1045889.hstgr.cloud/api/health

# API docs
curl https://finup.srv1045889.hstgr.cloud/docs

# Frontend
curl -I https://finup.srv1045889.hstgr.cloud/
```

---

## 💾 Backup

### Backup Automático Diário

**Script:** `/root/backup_finup.sh`

```bash
#!/bin/bash
BACKUP_DIR=/root/backups/finup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
PGPASSWORD=FinUp2026SecurePass pg_dump -U finup_user -h 127.0.0.1 finup_db \
  | gzip > $BACKUP_DIR/finup_db_$TIMESTAMP.sql.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "✅ Backup concluído: finup_db_$TIMESTAMP.sql.gz"
```

**Cron (diário às 3h):**

```bash
0 3 * * * /root/backup_finup.sh >> /var/log/finup_backup.log 2>&1
```

---

### Backup Manual

```bash
# No servidor
ssh minha-vps-hostinger

# Backup do banco
PGPASSWORD=FinUp2026SecurePass pg_dump -U finup_user -h 127.0.0.1 finup_db \
  | gzip > /root/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup do código
tar -czf /root/code_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/finup
```

---

## 🔄 Migração SQLite → PostgreSQL

### Script de Migração

**Path:** `scripts/migration/sqlite_to_postgres.py`

**Uso:**

```bash
# Dry-run (não aplica mudanças)
python scripts/migration/sqlite_to_postgres.py \
  --source sqlite:///app_dev/backend/database/financas_dev.db \
  --target postgresql://finup_user:senha@localhost/finup_db_dev \
  --dry-run

# Migração real
python scripts/migration/sqlite_to_postgres.py \
  --source sqlite:///app_dev/backend/database/financas_dev.db \
  --target postgresql://finup_user:senha@localhost/finup_db_dev
```

**O que faz:**
1. ✅ Valida schema source e target
2. ✅ Migra tabelas respeitando foreign keys
3. ✅ Valida contagens antes/depois
4. ✅ Rollback automático em erro
5. ✅ Log detalhado de todo processo

---

## 🎯 Comandos Rápidos

### Desenvolvimento Local

```bash
# Iniciar backend (SQLite)
cd app_dev/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Iniciar frontend
cd app_dev/frontend
npm run dev
```

---

### Produção (Servidor)

```bash
# Conectar via SSH
ssh minha-vps-hostinger

# Status de todos os serviços
systemctl status finup-backend finup-frontend nginx postgresql --no-pager

# Restart completo
systemctl restart finup-backend finup-frontend nginx

# Consultar banco
PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db

# Deploy seguro
./scripts/deploy/deploy_safe_v2.sh
```

---

## 📝 Tabela Resumo: Dev vs Prod

| Aspecto | Desenvolvimento (Local) | Produção (VPS) |
|---------|------------------------|----------------|
| **Código** | `/Users/emangue/.../ProjetoFinancasV5` | `/var/www/finup` |
| **Python** | venv em `.venv/` | venv em `app_dev/venv/` |
| **Database** | SQLite `financas_dev.db` | PostgreSQL `finup_db` |
| **Dados** | ~11.500 registros | ~11.500 registros (migrados) |
| **URL** | http://localhost:3000 | https://finup.srv1045889.hstgr.cloud/ |
| **Porta Backend** | 8000 (manual) | 8000 (systemd) |
| **Porta Frontend** | 3000 (npm run dev) | 3000 (npm start + Nginx) |
| **Logs** | `temp/logs/backend.log` | `journalctl -u finup-backend` |
| **Backup** | Manual (copiar .db) | Automático (cron diário) |
| **SSL** | Não | Sim (Nginx + Let's Encrypt) |
| **Process Manager** | Manual (Ctrl+C) | systemd (restart automático) |
| **Debug** | `DEBUG=true` | `DEBUG=false` |

---

## ⚠️ IMPORTANTE

### Diferenças Críticas SQLite vs PostgreSQL

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Sintaxe Data** | `DATE('now')` | `NOW()`, `CURRENT_TIMESTAMP` |
| **Autoincrement** | `AUTOINCREMENT` | `SERIAL`, `BIGSERIAL` |
| **Boolean** | 0/1 (INTEGER) | `TRUE`/`FALSE` |
| **Strings** | Case-insensitive by default | Case-sensitive |
| **Foreign Keys** | Precisa `PRAGMA foreign_keys=ON` | Sempre ativo |
| **Transactions** | File lock | MVCC (multi-version) |

**✅ SQLAlchemy abstrai essas diferenças!**

---

## 🚨 Troubleshooting

### Backend não inicia

```bash
# Ver logs
journalctl -u finup-backend -n 50

# Verificar .env
cat /var/www/finup/app_dev/backend/.env

# Testar conexão banco
PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db -c "SELECT 1;"

# Restart
systemctl restart finup-backend
```

---

### Erro 502 Bad Gateway

```bash
# Verificar se backend está ativo
systemctl status finup-backend

# Verificar porta 8000
netstat -tlnp | grep 8000

# Restart backend
systemctl restart finup-backend

# Restart nginx
systemctl restart nginx
```

---

### Banco não conecta

```bash
# Verificar se PostgreSQL está ativo
systemctl status postgresql

# Verificar conexões ativas
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='finup_db';"

# Restart PostgreSQL (⚠️ cuidado em produção!)
systemctl restart postgresql
```

---

## 📞 URLs de Produção

| Serviço | URL |
|---------|-----|
| **Frontend** | https://finup.srv1045889.hstgr.cloud/ |
| **API Health** | https://finup.srv1045889.hstgr.cloud/api/health |
| **API Docs** | https://finup.srv1045889.hstgr.cloud/docs |
| **API Base** | https://finup.srv1045889.hstgr.cloud/api/v1 |

---

**Data:** 31/01/2026  
**Status:** ✅ Documentação completa  
**Próxima atualização:** Após deploy mobile v1.0
