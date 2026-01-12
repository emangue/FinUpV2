# 🚀 PLANO DE DEPLOY PARA PRODUÇÃO - Sistema de Finanças V4

**Data Início:** 12 de Janeiro de 2026  
**Objetivo:** Preparar aplicação para deploy seguro na VM de produção  
**Repositório GitHub:** https://github.com/emangue/FinUpV2  

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Fases do Projeto](#fases-do-projeto)
3. [Checklist de Progresso](#checklist-de-progresso)
4. [Decisões Técnicas](#decisões-técnicas)
5. [Estrutura de Arquivos](#estrutura-de-arquivos)
6. [Detalhamento das Tarefas](#detalhamento-das-tarefas)

---

## 🎯 VISÃO GERAL

### Objetivo Principal
Transformar o sistema de desenvolvimento local em uma aplicação de produção segura, autenticada e pronta para deploy em VM com múltiplos usuários (<100 usuários).

### Estrutura de Pastas
- **Desenvolvimento:** `app_dev/` (máquina local)
- **Produção:** `app/` (VM servidor)
- **Deploy:** `app_dev/` será copiada e renomeada para `app/` na VM

### Premissas Importantes
- ✅ Layout/visão do frontend **NÃO deve mudar**
- ✅ Sistema já está 100% modularizado e isolado por usuário
- ✅ Arquivos CSV históricos (`_csvs_historico/`) **NUNCA vão para produção**
- ✅ Sistema suporta <100 usuários simultâneos (SQLite suficiente)
- ✅ Uso de instância única com multi-tenancy

---

## 📊 FASES DO PROJETO

### **FASE 1: Limpeza e Backup** ⏳ EM ANDAMENTO
**Duração estimada:** 0.5 dia  
**Responsável:** AI Copilot  

**Objetivo:** Limpar arquivos temporários e fazer backup seguro no GitHub

**Status:** 🟡 Em Andamento

---

### **FASE 2: Autenticação e Segurança** 🟡 EM ANDAMENTO
**Duração estimada:** 2-3 dias  
**Responsável:** AI Copilot  

**Objetivo:** Implementar autenticação JWT completa com todas as camadas de segurança

**Status:** 🟡 Backend 75% completo | Frontend 0% | Rate limiting pendente

**Últimas atualizações:**
- ✅ 12/01 09:52 - Tabela refresh_tokens criada
- ✅ 12/01 09:55 - Commit feat(auth) enviado para GitHub
- 🟡 12/01 10:00 - Aguardando rate limiting e frontend

---

### **FASE 3: Infraestrutura de Deploy** ⏸️ AGUARDANDO
**Duração estimada:** 2 dias  
**Responsável:** AI Copilot + DevOps  

**Objetivo:** Criar Docker, nginx, SSL, systemd para deploy na VM

**Status:** ⏸️ Não Iniciada

---

### **FASE 4: Backup e Monitoring** ⏸️ AGUARDANDO
**Duração estimada:** 1-2 dias  
**Responsável:** AI Copilot + DevOps  

**Objetivo:** Configurar backup S3 e monitoring Prometheus/Grafana

**Status:** ⏸️ Não Iniciada

---

### **FASE 5: Testes e Validação** ⏸️ AGUARDANDO
**Duração estimada:** 1-2 dias  
**Responsável:** Time QA + Emanuel  

**Objetivo:** Validar segurança, performance e isolamento de usuários

**Status:** ⏸️ Não Iniciada

---

### **FASE 6: Deploy Produção** ⏸️ AGUARDANDO
**Duração estimada:** 1 dia  
**Responsável:** DevOps + Emanuel  

**Objetivo:** Deploy final na VM com migração de dados

**Status:** ⏸️ Não Iniciada

---

## ✅ CHECKLIST DE PROGRESSO

### FASE 1: Limpeza e Backup (6/6) ✅

- [x] **1.1** - Criar pasta `_historico/` e mover documentação antiga
  - **Status:** ✅ Concluída em 12/01 09:47

- [x] **1.2** - Remover arquivos temporários e de debug
  - **Status:** ✅ Concluída em 12/01 09:48

- [x] **1.3** - Atualizar `.gitignore` para proteger `_csvs_historico/`
  - **Status:** ✅ Concluída em 12/01 09:45

- [x] **1.4** - Atualizar `copilot-instructions.md` sobre CSVs históricos
  - **Status:** ✅ Concluída em 12/01 09:45

- [x] **1.5** - Limpar `app_dev/uploads_temp/` e remover scripts antigos
  - **Status:** ✅ Concluída em 12/01 09:48

- [x] **1.6** - Commit e Push para GitHub (FinUpV2)
  - **Status:** ✅ Concluída em 12/01 09:50
  - **Commit:** 99f946e4

---

### FASE 2: Autenticação e Segurança (10/15) 🟡

#### 2.1 - Backend: Autenticação JWT (6/7)

- [x] **2.1.1** - Instalar dependências de segurança
  - **Status:** ✅ Concluída em 12/01 09:50

- [x] **2.1.2** - Substituir hash SHA256 por bcrypt (cost=12)
  - **Status:** ✅ Concluída em 12/01 09:51

- [x] **2.1.3** - Criar endpoint `/api/v1/auth/login` (POST)
  - **Status:** ✅ Concluída em 12/01 09:52

- [x] **2.1.4** - Criar endpoint `/api/v1/auth/logout` (POST)
  - **Status:** ✅ Concluída em 12/01 09:52

- [x] **2.1.5** - Criar endpoint `/api/v1/auth/me` (GET)
  - **Status:** ✅ Concluída em 12/01 09:52

- [x] **2.1.6** - Reativar validação JWT em `get_current_user_id()`
  - **Status:** ✅ Concluída em 12/01 09:52

- [ ] **2.1.7** - Forçar reset de senha para usuários existentes
  - **Status:** ⏸️ Não Iniciada

---

#### 2.2 - Backend: Tokens e Refresh (3/3)

- [x] **2.2.1** - Implementar Refresh Tokens
  - **Status:** ✅ Concluída em 12/01 09:52

- [x] **2.2.2** - Criar endpoint `/api/v1/auth/refresh` (POST)
  - **Status:** ✅ Concluída em 12/01 09:52

- [x] **2.2.3** - Configurar expiração de tokens
  - **Status:** ✅ Concluída em 12/01 09:51

---

#### 2.3 - Backend: Rate Limiting (0/2)

- [ ] **2.3.1** - Instalar e configurar slowapi
  - **Motivo:** Proteger contra brute force em endpoint de login
  - **O que é:** Biblioteca que limita número de requisições por IP/usuário
  - **Como funciona:** Conta requisições, retorna HTTP 429 se exceder limite
  - **Arquivo:** `app_dev/backend/requirements.txt` + `app_dev/backend/app/main.py`
  - **Limite:** 5 requisições/minuto por IP em `/auth/login`
  - **Status:** ⏸️ Não Iniciada

- [ ] **2.3.2** - Documentar rate limiting nginx para produção
  - **Motivo:** Proteção adicional em nível de proxy reverso
  - **O que é:** Nginx limita requisições globais antes de chegar ao backend
  - **Arquivo:** Criar `app_dev/deploy/nginx.conf`
  - **Limite:** 10 requisições/segundo global + burst de 20
  - **Status:** ⏸️ Não Iniciada

---

#### 2.4 - Variáveis de Ambiente (0/3)

- [ ] **2.4.1** - Gerar SECRET_KEY forte para produção
  - **Motivo:** Secret key atual é fraca e está no código (pode ser forjado JWT)
  - **Como gerar:** `openssl rand -hex 32` (256 bits)
  - **Arquivo:** Criar `app_dev/backend/.env.example` (template)
  - **Valor:** SECRET_KEY será diferente em dev e prod
  - **Status:** ⏸️ Não Iniciada

- [ ] **2.4.2** - Instalar python-dotenv e migrar config.py
  - **Motivo:** Separar configurações por ambiente (dev/prod)
  - **Arquivo:** `app_dev/backend/app/core/config.py`
  - **Código:** Usar `os.getenv("SECRET_KEY", "default-dev-only")`
  - **Status:** ⏸️ Não Iniciada

- [ ] **2.4.3** - Atualizar .gitignore para proteger senhas reset
  - **Motivo:** Arquivo com novas senhas não pode ir para GitHub
  - **Arquivo:** `.gitignore`
  - **Adicionar:** `app_dev/backend/.passwords_reset.txt`
  - **Status:** ⏸️ Não Iniciada

---

#### 2.5 - Frontend: Integração Autenticação (0/3)

- [ ] **2.5.1** - Conectar página de login ao backend real
  - **Motivo:** Tela existe mas não funciona (bypass total)
  - **Como funciona:** Chama `/api/v1/auth/login`, salva cookie, redireciona
  - **Arquivo:** `app_dev/frontend/src/app/login/page.tsx`
  - **IMPORTANTE:** Manter layout/visão exatamente como está
  - **Código:** Usar `credentials: 'include'` em todas as chamadas fetch
  - **Status:** ⏸️ Não Iniciada

- [ ] **2.5.2** - Reativar middleware de autenticação
  - **Motivo:** Middleware está com bypass total, precisa validar sessão
  - **Como funciona:** Chama `/api/v1/auth/me` antes de cada página, redireciona para /login se não autenticado
  - **Arquivo:** `app_dev/frontend/src/middleware.ts` linha 20
  - **Código atual:** `return NextResponse.next()` (bypass)
  - **Status:** ⏸️ Não Iniciada

- [ ] **2.5.3** - Reativar hook useAuth
  - **Motivo:** Hook tem bypass, precisa verificar autenticação real
  - **Arquivo:** `app_dev/frontend/src/hooks/useAuth.ts`
  - **Como funciona:** Chama `/api/v1/auth/me`, armazena estado do usuário
  - **Status:** ⏸️ Não Iniciada

---

### FASE 3: Infraestrutura de Deploy (0/7)

- [ ] **3.1** - Criar Dockerfile multi-stage (backend + frontend)
  - **Motivo:** Containerizar aplicação para deploy reproduzível
  - **O que é:** Dockerfile multi-stage compila backend e frontend em estágios separados, depois junta
  - **Como funciona:** Stage 1: build frontend (npm build), Stage 2: setup backend (pip install), Stage 3: runtime final
  - **Arquivo:** `app_dev/Dockerfile`
  - **Base image:** python:3.11-slim + node:20 para build
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.2** - Criar docker-compose.yml para produção
  - **Motivo:** Orquestrar containers (app + nginx + volumes)
  - **O que é:** Docker Compose gerencia múltiplos containers com dependências
  - **Como usar:** `docker-compose up -d` para iniciar tudo
  - **Arquivo:** `app_dev/docker-compose.yml`
  - **Serviços:** app (backend+frontend), nginx (proxy), volumes (db, logs, backups)
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.3** - Configurar nginx como proxy reverso com SSL
  - **Motivo:** Nginx serve HTTPS, proxy para backend, serve frontend estático
  - **O que é:** Nginx intercepta requisições HTTPS (443), roteia /api para backend (8000), / para frontend
  - **Arquivo:** `app_dev/deploy/nginx.conf`
  - **Configuração:** SSL cert path, proxy_pass, rate limiting, gzip
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.4** - Criar script de configuração Let's Encrypt SSL
  - **Motivo:** HTTPS obrigatório para produção (segurança + SEO)
  - **O que é:** Let's Encrypt fornece certificados SSL gratuitos com renovação automática
  - **Como usar:** Rodar `certbot-setup.sh` na VM, responder domínio, certificado gerado em /etc/letsencrypt/
  - **Arquivo:** `app_dev/scripts/certbot-setup.sh`
  - **Renovação:** Cron automático roda `certbot renew` a cada 60 dias
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.5** - Criar systemd service para auto-restart
  - **Motivo:** Aplicação reinicia automaticamente após reboot da VM
  - **O que é:** Systemd gerencia serviços Linux, inicia/para/restart automaticamente
  - **Como usar:** `systemctl enable financas`, depois app inicia em todo boot
  - **Arquivo:** `app_dev/scripts/financas.service`
  - **Config:** WorkingDirectory=/var/www/app, User=financas, Restart=always
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.6** - Criar script de deploy completo
  - **Motivo:** Automatizar processo de deploy (build, validação, deploy)
  - **Como usar:** Rodar `./deploy.sh` localmente, faz build, valida segurança, envia para VM
  - **Arquivo:** `app_dev/scripts/deploy.sh`
  - **Etapas:** 1) security check, 2) build docker, 3) rsync para VM, 4) restart containers
  - **Status:** ⏸️ Não Iniciada

- [ ] **3.7** - Documentar estrutura de pastas na VM
  - **Motivo:** Definir onde cada arquivo fica protegido na VM
  - **Estrutura:**
    - `/var/www/app/` - Código da aplicação (permissão 755)
    - `/var/lib/financas/db/` - Database SQLite (permissão 700, user financas:financas)
    - `/var/log/financas/` - Logs da aplicação (permissão 750)
    - `/backup/financas/` - Backups diários (permissão 700)
    - `/etc/letsencrypt/` - Certificados SSL (permissão 755)
  - **Arquivo:** `app_dev/DEPLOY_GUIDE.md`
  - **Status:** ⏸️ Não Iniciada

---

### FASE 4: Backup e Monitoring (0/6)

#### 4.1 - Backup Automático S3 (0/3)

- [ ] **4.1.1** - Configurar backup diário para S3
  - **Motivo:** SQLite na VM pode ser perdido, backup remoto é essencial
  - **O que é S3:** Amazon S3 (Simple Storage Service) - armazenamento de objetos na nuvem
  - **É pago?** SIM. Custo aproximado: $0.023/GB/mês (~R$0.12/GB/mês). Para DB de 1GB = ~R$1.50/mês
  - **Como funciona:** Cron roda script diário, faz dump do SQLite, criptografa, envia para S3 via `rclone`
  - **Arquivo:** `app_dev/scripts/backup-s3.sh`
  - **Configuração:** AWS credentials em `/root/.aws/credentials`, bucket name em .env
  - **Status:** ⏸️ Não Iniciada

- [ ] **4.1.2** - Instalar e configurar rclone para S3
  - **Motivo:** rclone é ferramenta confiável para sync com S3
  - **O que é:** Cliente rsync-like para cloud storage (S3, GDrive, Dropblaze, etc)
  - **Como configurar:** `rclone config`, selecionar S3, informar access key + secret key
  - **Arquivo:** Criar `app_dev/scripts/rclone-setup.sh`
  - **Criptografia:** Usar `rclone crypt` para criptografar antes de enviar
  - **Status:** ⏸️ Não Iniciada

- [ ] **4.1.3** - Configurar cron para backup diário às 03:00
  - **Motivo:** Backup automático sem intervenção manual
  - **Arquivo:** `/etc/cron.d/financas-backup`
  - **Comando:** `0 3 * * * /var/www/app/scripts/backup-s3.sh >> /var/log/financas/backup.log 2>&1`
  - **Status:** ⏸️ Não Iniciada

---

#### 4.2 - Monitoring Prometheus + Grafana (0/3)

- [ ] **4.2.1** - Criar endpoint `/api/health` com métricas
  - **Motivo:** Monitorar saúde da aplicação (CPU, RAM, DB size, uptime)
  - **O que é:** Endpoint que retorna JSON com métricas da aplicação
  - **Como usar:** Prometheus scrape esse endpoint a cada 15s
  - **Arquivo:** `app_dev/backend/app/main.py`
  - **Métricas:** uptime, db_size_mb, active_users, total_transactions, memory_usage_mb
  - **Status:** ⏸️ Não Iniciada

- [ ] **4.2.2** - Configurar Prometheus para coletar métricas
  - **Motivo:** Armazenar histórico de métricas para análise
  - **O que é Prometheus:** Sistema de monitoring open-source, armazena time-series data
  - **Como funciona:** Prometheus faz scrape do `/api/health` a cada 15s, armazena dados
  - **Arquivo:** `app_dev/deploy/prometheus.yml`
  - **Container:** Rodar Prometheus em container separado no docker-compose
  - **Status:** ⏸️ Não Iniciada

- [ ] **4.2.3** - Configurar Grafana com dashboard de finanças
  - **Motivo:** Visualizar métricas em dashboards bonitos e alertas
  - **O que é Grafana:** Ferramenta de visualização, conecta em Prometheus, cria gráficos
  - **Como usar:** Acessar `https://financas.com.br/grafana`, ver dashboards de CPU, RAM, DB, erros
  - **Arquivo:** `app_dev/deploy/grafana-dashboard.json`
  - **Alertas:** Email se CPU > 80%, DB > 5GB, erros > 10/min
  - **Status:** ⏸️ Não Iniciada

---

### FASE 5: Testes e Validação (0/5)

- [ ] **5.1** - Criar script de teste de isolamento de usuários
  - **Motivo:** Garantir que user A não vê dados do user B
  - **Como funciona:** Cria 3 usuários, insere transações, valida queries filtram por user_id
  - **Arquivo:** `app_dev/tests/test_user_isolation.py`
  - **Validações:** 50+ queries em todos os domínios (transactions, budget, upload, etc)
  - **Status:** ⏸️ Não Iniciada

- [ ] **5.2** - Rodar scanners de segurança (safety, bandit, pip-audit)
  - **Motivo:** Detectar vulnerabilidades conhecidas em dependências
  - **O que são:** safety=CVEs, bandit=análise estática Python, pip-audit=vulnerabilidades PyPI
  - **Como rodar:** `./scripts/security-check.sh` (roda os 3 automaticamente)
  - **Arquivo:** Criar `app_dev/scripts/security-check.sh`
  - **Bloqueio:** Se encontrar CRITICAL, deploy é bloqueado
  - **Status:** ⏸️ Não Iniciada

- [ ] **5.3** - Testar autenticação (login, logout, tokens, rate limiting)
  - **Motivo:** Validar fluxo completo de autenticação
  - **Arquivo:** `app_dev/tests/test_auth_flow.py`
  - **Casos:** login sucesso, login falha, logout, refresh token, rate limit 429
  - **Status:** ⏸️ Não Iniciada

- [ ] **5.4** - Testar backup e restore do banco
  - **Motivo:** Garantir que backup funciona e pode ser restaurado
  - **Como:** Fazer backup S3, deletar banco local, restaurar, validar dados
  - **Status:** ⏸️ Não Iniciada

- [ ] **5.5** - Teste de carga (JMeter ou Locust)
  - **Motivo:** Validar que sistema aguenta 100 usuários simultâneos
  - **Ferramenta:** Locust (Python-based, mais simples)
  - **Cenário:** 100 usuários virtuais fazendo login + consultas + uploads
  - **Métricas:** Response time < 500ms, error rate < 1%
  - **Status:** ⏸️ Não Iniciada

---

### FASE 6: Deploy Produção (0/6)

- [ ] **6.1** - Criar usuário dedicado `financas:financas` na VM
  - **Motivo:** Não rodar aplicação como root (segurança)
  - **Comando:** `useradd -r -s /bin/bash -d /var/www/app financas`
  - **Status:** ⏸️ Não Iniciada

- [ ] **6.2** - Criar estrutura de pastas na VM
  - **Comando:** `mkdir -p /var/www/app /var/lib/financas/db /var/log/financas /backup/financas`
  - **Permissões:** `chown -R financas:financas` em todas
  - **Status:** ⏸️ Não Iniciada

- [ ] **6.3** - Fazer backup do banco atual da VM
  - **Motivo:** Backup de segurança antes de substituir aplicação
  - **Comando:** `cp /var/www/app/financas.db /backup/financas/pre-deploy-$(date +%Y%m%d).db`
  - **Status:** ⏸️ Não Iniciada

- [ ] **6.4** - Rsync de `app_dev/` para VM como `app/`
  - **Motivo:** Enviar código novo para VM
  - **Comando:** `rsync -avz --exclude venv --exclude node_modules app_dev/ user@vm:/var/www/app/`
  - **Status:** ⏸️ Não Iniciada

- [ ] **6.5** - Configurar .env de produção na VM
  - **Motivo:** Variáveis de ambiente de prod (SECRET_KEY, DATABASE_URL, CORS)
  - **Arquivo:** `/var/www/app/.env`
  - **Valores:** SECRET_KEY forte, DATABASE_PATH=/var/lib/financas/db/financas.db, CORS=https://financas.com.br
  - **Status:** ⏸️ Não Iniciada

- [ ] **6.6** - Iniciar containers e validar funcionamento
  - **Comando:** `cd /var/www/app && docker-compose up -d`
  - **Validação:** `curl https://financas.com.br/api/health` deve retornar HTTP 200
  - **Status:** ⏸️ Não Iniciada

---

## 🔧 DECISÕES TÉCNICAS

### Hashing de Senha
**Decisão:** Bcrypt com cost=12  
**Motivo:** Padrão da indústria, mais seguro que SHA256  
**Alternativa rejeitada:** Argon2id (mais moderno mas dependência extra)

### Armazenamento de Token Frontend
**Decisão:** HttpOnly Cookie + endpoint /auth/me  
**Motivo:** Mais seguro que localStorage (protege contra XSS)  
**Alternativa rejeitada:** localStorage (vulnerável a XSS)

### Database em Produção
**Decisão:** SQLite único com backup diário S3  
**Motivo:** <100 usuários simultâneos, SQLite suficiente e mais simples  
**Alternativa rejeitada:** PostgreSQL (complexidade desnecessária para escala atual)

### SSL/HTTPS
**Decisão:** Let's Encrypt via Certbot  
**Motivo:** Gratuito, renovação automática, simples para VM única  
**Alternativa rejeitada:** Traefik (mais complexo, overhead desnecessário)

### Rate Limiting
**Decisão:** Nginx (global) + slowapi (granular)  
**Motivo:** Dupla proteção, nginx bloqueia DDoS, slowapi protege endpoints específicos  

### Frontend Build
**Decisão:** Build estático servido por nginx  
**Motivo:** Mais rápido, menos recursos, layout não muda  
**Alternativa rejeitada:** Next.js standalone (SSR desnecessário para app financeiro)

### Backup
**Decisão:** S3 com rclone criptografado  
**Motivo:** Redundância geográfica, baixo custo (~R$1.50/mês para 1GB)  
**Custo:** S3 custa $0.023/GB/mês = ~R$0.12/GB/mês  

### Refresh Tokens
**Decisão:** Implementar agora (access 15min + refresh 7 dias)  
**Motivo:** Evita usuários deslogados frequentemente, aumenta segurança  

### Multi-tenancy
**Decisão:** Instância única com isolamento por user_id  
**Motivo:** <100 usuários totais, isolamento já implementado 100%  

### Monitoring
**Decisão:** Prometheus + Grafana em containers  
**Motivo:** Open-source, padrão da indústria, fácil configuração  

---

## 📁 ESTRUTURA DE ARQUIVOS

### Arquivos Criados Durante o Projeto

```
app_dev/
├── .env.example                      # Template de variáveis de ambiente
├── .env                              # Variáveis de ambiente (gitignore)
├── Dockerfile                        # Containerização multi-stage
├── docker-compose.yml                # Orquestração de containers
├── DEPLOY_GUIDE.md                   # Guia de deploy na VM
├── DEPLOY_SECURITY.md                # Checklist de segurança
│
├── backend/
│   ├── requirements.txt              # ✏️ ATUALIZADO: +passlib, +python-jose, +slowapi
│   ├── requirements-dev.txt          # 🆕 NOVO: safety, bandit, pip-audit
│   ├── .passwords_reset.txt          # 🆕 NOVO: Senhas reset (gitignore)
│   │
│   ├── app/
│   │   ├── main.py                   # ✏️ ATUALIZADO: slowapi, /api/health
│   │   │
│   │   ├── core/
│   │   │   └── config.py             # ✏️ ATUALIZADO: dotenv, SECRET_KEY forte
│   │   │
│   │   ├── shared/
│   │   │   ├── dependencies.py       # ✏️ ATUALIZADO: JWT validation reativada
│   │   │   └── utils.py              # ✏️ ATUALIZADO: bcrypt em vez de SHA256
│   │   │
│   │   └── domains/
│   │       └── users/
│   │           ├── router.py         # ✏️ ATUALIZADO: /login, /logout, /me, /refresh
│   │           ├── models.py         # ✏️ ATUALIZADO: tabela refresh_tokens
│   │           └── migration.py      # 🆕 NOVO: Migração SHA256 → bcrypt
│   │
│   └── tests/
│       ├── test_auth_flow.py         # 🆕 NOVO: Testes de autenticação
│       └── test_user_isolation.py    # 🆕 NOVO: Testes de isolamento
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── login/
│   │   │       └── page.tsx          # ✏️ ATUALIZADO: Conecta backend real
│   │   │
│   │   ├── middleware.ts             # ✏️ ATUALIZADO: Validação reativada
│   │   │
│   │   └── hooks/
│   │       └── useAuth.ts            # ✏️ ATUALIZADO: Auth real reativada
│   │
│   └── public/
│       └── (mantém tudo como está)  # ⚠️ LAYOUT NÃO MUDA
│
├── deploy/
│   ├── nginx.conf                    # 🆕 NOVO: Configuração nginx proxy
│   ├── prometheus.yml                # 🆕 NOVO: Config Prometheus
│   └── grafana-dashboard.json        # 🆕 NOVO: Dashboard Grafana
│
└── scripts/
    ├── certbot-setup.sh              # 🆕 NOVO: SSL Let's Encrypt
    ├── backup-s3.sh                  # 🆕 NOVO: Backup diário S3
    ├── rclone-setup.sh               # 🆕 NOVO: Configuração rclone
    ├── security-check.sh             # 🆕 NOVO: safety + bandit + pip-audit
    ├── deploy.sh                     # 🆕 NOVO: Deploy completo automatizado
    └── financas.service              # 🆕 NOVO: Systemd service
```

### Arquivos Removidos/Movidos

```
_historico/                           # 🆕 NOVO: Documentação histórica
├── BUGS_historico.md                 # ⬅️ MOVIDO de raiz
├── CLEANUP_REPORT.md                 # ⬅️ MOVIDO de raiz
├── MODULARIDADE_*.md                 # ⬅️ MOVIDO de raiz (4 arquivos)
└── STATUS_04012026.md                # ⬅️ MOVIDO de raiz

REMOVIDOS da raiz:
- debug_*.py (3 arquivos)
- check_*.py (5 arquivos)
- test_*.py (2 arquivos)
- test_*.csv (2 arquivos)
- regenerate_*.py (3 arquivos)
- migrate_*.py (1 arquivo)
- *.pid (2 arquivos)
- arquivo_teste_n8n.json

REMOVIDOS de app_dev/:
- run.py (Flask antigo)
- run_dev_api.py (duplicado)
- start_all_servers.sh (substituído)
- stop_all_servers.sh (substituído)

MANTIDOS (mas não vão pra prod):
- _csvs_historico/ (testes locais apenas)
```

---

## 📝 DETALHAMENTO DAS TAREFAS

### Como Usar Este Documento

1. **Progresso:** Marcar `[x]` nas tarefas concluídas
2. **Status:** Atualizar emoji de status (⏸️ → 🟡 → ✅)
3. **Bloqueios:** Documentar na seção "Bloqueios" se houver
4. **Decisões:** Adicionar decisões técnicas na seção apropriada

### Convenções de Status

- ⏸️ **Não Iniciada** - Tarefa aguardando início
- 🟡 **Em Andamento** - Trabalho ativo
- ✅ **Concluída** - Tarefa finalizada e validada
- ❌ **Bloqueada** - Impedimento identificado
- 🔄 **Em Revisão** - Aguardando review/validação

### Dependências Entre Fases

```
FASE 1 (Limpeza)
    ↓
FASE 2 (Autenticação) ← deve vir antes do deploy
    ↓
FASE 3 (Infraestrutura)
    ↓
FASE 4 (Backup) ← pode rodar em paralelo com testes
    ↓
FASE 5 (Testes) ← valida tudo antes de prod
    ↓
FASE 6 (Deploy)
```

---

## 🚨 BLOQUEIOS E RISCOS

### Bloqueios Atuais
*Nenhum bloqueio identificado no momento*

### Riscos Identificados

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Migração de senhas SHA256 falha | ALTO | BAIXO | Backup completo antes, script de rollback |
| S3 custos inesperados | MÉDIO | BAIXO | Monitorar billing AWS diariamente |
| Downtime durante deploy | MÉDIO | MÉDIO | Deploy em horário de baixo uso (madrugada) |
| Layout frontend muda acidentalmente | ALTO | BAIXO | Não tocar em componentes visuais |
| Database corrompe durante migração | ALTO | BAIXO | Backup triplo (local + S3 + snapshot VM) |

---

## 📞 CONTATOS E SUPORTE

**Responsável Técnico:** Emanuel  
**DevOps:** [A definir]  
**Repositório:** https://github.com/emangue/FinUpV2  
**VM Produção:** [Endereço a definir]  

---

## 📅 TIMELINE

| Fase | Duração Estimada | Data Início | Data Fim Estimada |
|------|------------------|-------------|-------------------|
| FASE 1 | 0.5 dia | 12/01/2026 | 12/01/2026 |
| FASE 2 | 2-3 dias | 12/01/2026 | 15/01/2026 |
| FASE 3 | 2 dias | 15/01/2026 | 17/01/2026 |
| FASE 4 | 1-2 dias | 17/01/2026 | 19/01/2026 |
| FASE 5 | 1-2 dias | 19/01/2026 | 21/01/2026 |
| FASE 6 | 1 dia | 21/01/2026 | 22/01/2026 |
| **TOTAL** | **7-10 dias** | **12/01/2026** | **22/01/2026** |

---

## ✅ CRITÉRIOS DE SUCESSO

### Critérios Técnicos
- [ ] Autenticação JWT funcionando em prod
- [ ] 100% dos endpoints protegidos
- [ ] Isolamento de usuários validado (0 vazamentos)
- [ ] Backup S3 rodando diariamente
- [ ] Monitoring ativo (Prometheus + Grafana)
- [ ] SSL HTTPS funcionando
- [ ] Response time < 500ms (p95)
- [ ] Error rate < 1%

### Critérios de Negócio
- [ ] Layout/visão frontend preservado 100%
- [ ] Suporte a <100 usuários simultâneos
- [ ] Custo S3 < R$5/mês
- [ ] Downtime deploy < 5 minutos
- [ ] Usuários podem fazer login com novas senhas

---

**Última Atualização:** 12 de Janeiro de 2026  
**Versão do Documento:** 1.0.0  
**Status Geral:** 🟡 Em Andamento - FASE 1
