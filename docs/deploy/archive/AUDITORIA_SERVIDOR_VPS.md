# 🔍 AUDITORIA COMPLETA DO SERVIDOR VPS

**Data:** 21 de janeiro de 2026  
**Servidor:** srv1045889.hstgr.cloud (148.230.78.91)  
**OS:** Ubuntu 24.04 LTS  
**Uptime:** 108 dias (desde ~05 Out 2025)

---

## 🚨 SITUAÇÃO ATUAL: MÚLTIPLOS DEPLOYS ATIVOS

### ❌ PROBLEMA: 3 Versões da Aplicação Rodando Simultaneamente

| Deploy | Localização | Status | Porta | Tipo | Problema |
|--------|-------------|--------|-------|------|----------|
| **1. Easypanel** | `/opt/financial-app/` | ✅ Ativo | 5000 | Flask antigo | Usando SQLite, arquitetura antiga |
| **2. financas** | `/var/www/financas/` | ⚠️ Parado | - | FastAPI novo | Sem processos ativos |
| **3. financas_completo** | `/var/www/financas_completo/` | ✅ Ativo | 8000 | FastAPI | Rodando direto (sem systemd) |

---

## 📋 DETALHAMENTO DOS DEPLOYS

### 1️⃣ Deploy Easypanel (ANTIGO - Flask)

**Path:** `/opt/financial-app/`

**Características:**
- ✅ **Ativo:** Gunicorn rodando (PID 2622096, 2622097)
- 🔧 **Framework:** Flask (arquitetura antiga)
- 💾 **Database:** SQLite (`financas.db` - 132KB)
- 🌐 **Porta:** 5000 (localhost)
- 👤 **Usuário:** `financial-app`
- 🔐 **Nginx:** Configurado (`/etc/nginx/sites-enabled/financial-app`)
- 📦 **Gerenciamento:** Supervisor/Gunicorn

**Problemas:**
- ❌ Arquitetura antiga (Flask monolítico)
- ❌ SQLite (não adequado para produção)
- ❌ Sem domínios modulares (DDD)
- ❌ Sem estrutura app_dev/

**Processos ativos:**
```bash
financi+ 2622096  /opt/financial-app/venv/bin/gunicorn --bind 127.0.0.1:5000
financi+ 2622097  /opt/financial-app/venv/bin/gunicorn (worker)
```

---

### 2️⃣ Deploy /var/www/financas (INCOMPLETO)

**Path:** `/var/www/financas/`

**Características:**
- ❌ **Status:** Sem processos rodando
- 📁 **Estrutura:** Tem `app_dev/` (FastAPI)
- 🔧 **Framework:** FastAPI (arquitetura nova)
- 📂 **Conteúdo:** Repositório Git com docs/scripts de dev

**Conteúdo:**
```
app_dev/           # Estrutura correta (backend + frontend)
quick_start.sh     # Scripts de desenvolvimento
quick_stop.sh
codigos_apoio/     # Scripts auxiliares
_historico/        # Documentação
*.md               # Vários docs (PLANO_DEPLOY_PRODUCAO.md, etc)
```

**Problemas:**
- ❌ Nunca foi inicializado
- ❌ Tem arquivos de desenvolvimento (quick_*.sh)
- ❌ Git com histórico inteiro (.git/)
- ⚠️ Estrutura correta mas não está rodando

---

### 3️⃣ Deploy /var/www/financas_completo (ATIVO - FastAPI)

**Path:** `/var/www/financas_completo/`

**Características:**
- ✅ **Ativo:** Python/Uvicorn rodando (PID 1712161, 1712164)
- 🔧 **Framework:** FastAPI
- 💾 **Database:** Provavelmente PostgreSQL
- 🌐 **Porta:** 8080 (exposta publicamente - ❌ INSEGURO)
- 👤 **Usuário:** root (❌ INSEGURO)
- 📦 **Gerenciamento:** Processo direto (sem systemd)

**Conteúdo:**
```
backend/
  app/
  venv/
  database/
frontend/
  node_modules/
  src/
docker-compose.yml
Dockerfile
deploy/
monitoring/
```

**Processos ativos:**
```bash
root     1712161  python run.py --host 0.0.0.0 --port 8080
root     1712164  /var/www/financas_completo/backend/venv/bin/python (worker)
```

**Problemas CRÍTICOS:**
- ❌ **Rodando como root** (risco de segurança)
- ❌ **Porta 8000 exposta publicamente** (deveria ser localhost)
- ❌ **Sem systemd service** (não reinicia em crash)
- ❌ **Estrutura não é app_dev/** (diferente do padrão)
- ⚠️ Tem Docker mas não está usando

---

## 🌐 SERVIÇOS ATIVOS

### Nginx
- **Status:** ✅ Ativo
- **Portas:** 80 (HTTP), 443 (HTTPS)
- **Sites habilitados:** 
  - `/etc/nginx/sites-enabled/financial-app` → Proxy para porta 5000 (Easypanel)

### Docker/Easypanel
- **Status:** ✅ Ativo
- **Containers:**
  - `easypanel` (porta 3000)
  - `traefik` (múltiplas instâncias - ⚠️ problema)
  - `n8n_postgres` (PostgreSQL isolado)
  - `n8n_redis` (Redis isolado)

### Fail2Ban
- **Status:** ✅ Ativo
- **Proteção SSH:** Funcionando

---

## 📊 RECURSOS DO SERVIDOR

| Recurso | Total | Usado | Livre | Uso% |
|---------|-------|-------|-------|------|
| **CPU** | 2 cores | - | - | - |
| **RAM** | 8 GB | ~2GB | ~6GB | 25% |
| **Disco** | 96 GB | 12 GB | 85 GB | 12% |

---

## 🔐 SEGURANÇA

### ✅ Pontos Positivos
- SSH com chaves (root tem 2 chaves autorizadas)
- Fail2Ban ativo
- Nginx configurado
- Certbot instalado (SSL disponível)

### ❌ Pontos Negativos
- **Aplicação rodando como root** (`financas_completo`)
- **Porta 8000 exposta publicamente** (deveria ser 127.0.0.1)
- **Múltiplas versões ativas** (confusão)
- **Sem firewall UFW** (apenas iptables padrão)
- **3 deploys simultâneos** (qual é o oficial?)

---

## 🗑️ RECOMENDAÇÕES DE LIMPEZA

### DEVE REMOVER:

#### 1. `/opt/financial-app/` (Easypanel Flask)
**Razão:** Arquitetura antiga, Flask monolítico, SQLite

```bash
# Parar aplicação
supervisorctl stop financial-app
systemctl stop financial-app 2>/dev/null

# Backup antes de remover
tar -czf /root/backup_financial_app_$(date +%Y%m%d).tar.gz /opt/financial-app/

# Remover
rm -rf /opt/financial-app/
userdel -r financial-app  # Remove usuário também
```

#### 2. `/var/www/financas/` (Deploy Incompleto)
**Razão:** Nunca foi ativado, tem arquivos de dev

```bash
# Backup (se tiver algo útil)
tar -czf /root/backup_financas_$(date +%Y%m%d).tar.gz /var/www/financas/

# Remover
rm -rf /var/www/financas/
```

#### 3. `/var/www/financas_completo/` (Temporário)
**Razão:** Estrutura errada, rodando inseguro, será substituído

```bash
# Parar processos
kill 1712161 1712164

# Backup do banco (IMPORTANTE!)
cp /var/www/financas_completo/backend/database/*.db /root/backup_db_$(date +%Y%m%d).db

# Remover após deploy limpo
rm -rf /var/www/financas_completo/
```

#### 4. Nginx config antigo
```bash
rm /etc/nginx/sites-enabled/financial-app
rm /etc/nginx/sites-available/financial-app
```

---

## 🚀 PLANO DE DEPLOY LIMPO

### Estrutura Final Desejada:

```
/var/www/financas/
└── app_dev/                          # ÚNICO diretório do Git
    ├── backend/
    │   ├── app/
    │   │   ├── core/
    │   │   ├── domains/
    │   │   ├── shared/
    │   │   └── main.py
    │   ├── database/
    │   ├── venv/
    │   ├── .env                      # Configurações (NÃO no Git)
    │   └── run.py
    │
    └── frontend/
        ├── src/
        ├── node_modules/
        └── .env.production           # Configurações (NÃO no Git)
```

### Passos do Deploy:

1. **Limpar servidor** (remover 3 deploys antigos)
2. **Configurar PostgreSQL** (migrar de SQLite)
3. **Clonar repositório limpo** (apenas app_dev/)
4. **Configurar .env seguro** (JWT secret, DB password)
5. **Criar services systemd** (backend + frontend)
6. **Configurar Nginx** (reverse proxy + SSL)
7. **Testar e ativar**

---

## 📝 COMANDOS ÚTEIS

### Ver logs dos processos ativos
```bash
# Easypanel Flask
tail -f /opt/financial-app/logs/error.log

# FastAPI (financas_completo)
ps aux | grep python | grep 1712161
lsof -p 1712161  # Ver arquivos/portas abertas
```

### Verificar portas
```bash
ss -tulpn | grep LISTEN | grep -E ":(5000|8000|8080)"
```

### Verificar usuários ativos
```bash
who
last | head -10
```

---

## ✅ PRÓXIMOS PASSOS

1. **Confirmar remoção** dos 3 deploys antigos
2. **Backup dos dados** (SQLite atual)
3. **Limpar GitHub** (apenas app_dev/)
4. **Deploy limpo** seguindo GUIA_DEPLOY_PRODUCAO.md
5. **Configurar SSL** (Let's Encrypt)
6. **Testar aplicação** nova

---

**Aguardando autorização para iniciar limpeza! 🧹**
