# 🚀 Deploy de Atualizações - meufinup.com.br

**Data:** 14/02/2026  
**Objetivo:** Atualizar o app em produção com as alterações recentes (feature/consolidate-budget-tables + correções de build)  
**Foco:** Avaliação de diferenças, base de dados PostgreSQL e execução segura

---

## 📋 ÍNDICE

1. [Avaliação de Diferenças](#1-avaliação-de-diferenças)
2. [Infraestrutura e Credenciais](#2-infraestrutura-e-credenciais)
3. [Base de Dados - Detalhamento Crítico](#3-base-de-dados---detalhamento-crítico)
4. [Pré-Deploy - Checklist Obrigatório](#4-pré-deploy---checklist-obrigatório)
5. [Execução do Deploy](#5-execução-do-deploy)
6. [Pós-Deploy e Validação](#6-pós-deploy-e-validação)
7. [Rollback](#7-rollback)

---

## 1. AVALIAÇÃO DE DIFERENÇAS

### 1.1 Estado Atual

| Item | Local (Dev) | Produção (meufinup) |
|------|-------------|---------------------|
| **Branch** | `feature/consolidate-budget-tables` | `main` (último deploy) |
| **Banco** | SQLite (`financas_dev.db`) | PostgreSQL (`finup_db`) |
| **Path local** | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5` | `/var/www/finup` |
| **Venv** | `app_dev/venv` | `app_dev/venv` |

### 1.2 Principais Alterações a Deployar

#### Backend
- **Budget Consolidation:** 4 tabelas → 1 tabela (`budget_planning`)
- **base_marcacoes:** Remoção de colunas `TipoGasto` e `CategoriaGeral` (JOIN com `base_grupos_config`)
- **Domínios modificados:** `budget`, `marcacoes`, `categories`, `upload` (classifier, marker)
- **Novos repositórios:** `repository_categoria_config.py`, `repository_geral.py`

#### Frontend
- **Correções de build:** Dashboard components index, Preview paths, tipos TypeScript
- **Suspense:** Páginas mobile com `useSearchParams` (transactions, budget/edit, budget/[goalId], budget/new)
- **Componentes:** Ajustes em `BottomActionBar`, `PreviewLayout`, `TransactionCard`, `CategoryIcon`

#### Migrations Pendentes (ordem)
1. `635e060a2434` - Consolidate budget tables (4→1)
2. `599d728bc4da` - Cleanup base_marcacoes (remove TipoGasto, CategoriaGeral)

### 1.3 Tabelas Afetadas no PostgreSQL

| Ação | Tabela | Detalhes |
|------|--------|----------|
| **DROP** | `budget_geral` | Consolidada em budget_planning |
| **DROP** | `budget_categoria_config` | Funcionalidade removida |
| **DROP** | `budget_geral_historico` | Consolidada em budget_planning |
| **ALTER** | `budget_planning` | Novos campos: grupo, tipo_gasto, valor_medio_3_meses, ativo |
| **ALTER** | `base_marcacoes` | Remove colunas TipoGasto, CategoriaGeral |

### 1.4 Dependências Críticas

- **599d728bc4da** exige que **todos** os grupos em `base_marcacoes` existam em `base_grupos_config`
- Se houver órfãos, a migration **falha** com erro explícito
- Validar antes: `SELECT m.GRUPO FROM base_marcacoes m LEFT JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo WHERE g.nome_grupo IS NULL;`

---

## 2. INFRAESTRUTURA E CREDENCIAIS

### 2.1 Servidor

| Item | Valor |
|------|-------|
| **Alias SSH** | `minha-vps-hostinger` |
| **IP** | 148.230.78.91 |
| **Hostname** | srv1045889.hstgr.cloud |
| **User** | root |
| **Path app** | `/var/www/finup` |
| **Chave SSH** | `~/.ssh/id_ed25519` ou `~/.ssh/id_rsa_hostinger` |

### 2.2 Credenciais (`.env.deploy` - NUNCA commitar)

Arquivo local: `/.env.deploy` (na raiz do projeto)

```bash
# Variáveis esperadas (exemplo - NÃO preencher aqui)
SERVER_USER=root
SERVER_HOST=148.230.78.91
SERVER_PASSWORD=<senha_backup>
SERVER_APP_PATH=/var/www/finup
```

**Carregar credenciais:**
```bash
source scripts/deploy/load_credentials.sh
```

### 2.3 PostgreSQL (Produção)

| Item | Valor |
|------|-------|
| **Host** | 127.0.0.1 |
| **Porta** | 5432 |
| **Database** | finup_db |
| **User** | finup_user |
| **Password** | FinUp2026SecurePass |
| **Connection string** | `postgresql://finup_user:FinUp2026SecurePass@127.0.0.1:5432/finup_db` |

### 2.4 URLs

| Recurso | URL |
|---------|-----|
| **App** | https://meufinup.com.br |
| **API Health** | https://meufinup.com.br/api/health |
| **API Docs** | https://meufinup.com.br/docs |
| **Alternativa** | https://finup.srv1045889.hstgr.cloud |

### 2.5 Serviços systemd

| Serviço | Comando |
|---------|---------|
| Backend | `systemctl restart finup-backend` |
| Frontend | `systemctl restart finup-frontend` |
| Status | `systemctl status finup-backend finup-frontend` |
| Logs | `journalctl -u finup-backend -f` |

---

## 3. BASE DE DADOS - DETALHAMENTO CRÍTICO

### 3.1 Diferenças SQLite (dev) vs PostgreSQL (prod)

| Aspecto | SQLite (dev) | PostgreSQL (prod) |
|---------|--------------|-------------------|
| **Arquivo/URL** | `financas_dev.db` | `finup_db` em 127.0.0.1:5432 |
| **Path** | `app_dev/backend/database/financas_dev.db` | N/A (serviço) |
| **Backup** | `backup_daily.sh` (copia .db) | `pg_dump` (ver seção 3.3) |
| **Alembic** | Funciona em ambos | Mesmo schema, tipos compatíveis |

### 3.2 Migrations - Ordem e Impacto

```
f6f307855c81 (initial_schema)
    ↓
6977f246014c (add_ativo_field_to_budget_planning)
    ↓
9feefd17fcda (adiciona_index_composto_base_padroes)
    ↓
635e060a2434 (consolidate_budget_tables)  ← DROP 3 tabelas, ALTER budget_planning
    ↓
599d728bc4da (cleanup_base_marcacoes)    ← ALTER base_marcacoes (remove 2 colunas)
```

### 3.3 Backup PostgreSQL (OBRIGATÓRIO antes de migrations)

**No servidor:**

```bash
# Conectar
ssh minha-vps-hostinger

# Criar backup com timestamp
BACKUP_DIR="/root/backups/finup"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup completo do banco
PGPASSWORD=FinUp2026SecurePass pg_dump -U finup_user -h 127.0.0.1 finup_db \
  | gzip > $BACKUP_DIR/finup_db_pre_deploy_$TIMESTAMP.sql.gz

echo "✅ Backup: finup_db_pre_deploy_$TIMESTAMP.sql.gz"
ls -lh $BACKUP_DIR/
```

**Script existente (se configurado):**
```bash
/root/backup_finup.sh
```

### 3.4 Tabelas a Serem Removidas (migration 635e060a2434)

Antes do deploy, verificar se existem e quantos registros têm:

```sql
-- No servidor: PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db

SELECT 'budget_geral' as tabela, COUNT(*) FROM budget_geral
UNION ALL
SELECT 'budget_categoria_config', COUNT(*) FROM budget_categoria_config
UNION ALL
SELECT 'budget_geral_historico', COUNT(*) FROM budget_geral_historico;
```

A migration **635e060a2434** migra dados para `budget_planning` antes de dropar.

### 3.5 Validação Pré-Migration (599d728bc4da)

**OBRIGATÓRIO:** Garantir que não há grupos órfãos em `base_marcacoes`:

```sql
-- Grupos em base_marcacoes SEM correspondência em base_grupos_config
SELECT m.GRUPO, COUNT(*) as qtd
FROM base_marcacoes m
LEFT JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo
WHERE g.nome_grupo IS NULL
GROUP BY m.GRUPO;
```

Se retornar linhas, **corrigir antes**:

```sql
-- Inserir configs faltantes (exemplo - ajustar valores)
INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
SELECT DISTINCT m.GRUPO, 'Ajustável', 'Despesa'
FROM base_marcacoes m
LEFT JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo
WHERE g.nome_grupo IS NULL;
```

### 3.6 Restaurar Backup (em caso de rollback)

```bash
# Parar backend
systemctl stop finup-backend

# Restaurar
gunzip < /root/backups/finup/finup_db_pre_deploy_YYYYMMDD_HHMMSS.sql.gz \
  | PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db

# Reiniciar
systemctl start finup-backend
```

---

## 4. PRÉ-DEPLOY - CHECKLIST OBRIGATÓRIO

### 4.1 Código

- [ ] **Merge para main:** `feature/consolidate-budget-tables` → `main`
- [ ] **Git status limpo:** `git status` sem alterações
- [ ] **Build frontend OK:** `cd app_dev/frontend && npm run build`
- [ ] **Backend inicia:** `cd app_dev/backend && source venv/bin/activate && python -c "from app.main import app"`

### 4.2 Migrations

- [ ] **Alembic history:** `alembic history` - verificar ordem
- [ ] **Current em dev:** `alembic current` - deve estar em `599d728bc4da` (head)
- [ ] **Teste downgrade/upgrade:** `alembic downgrade -1` e `alembic upgrade head`

### 4.3 Banco Produção

- [ ] **Backup PostgreSQL criado** (seção 3.3)
- [ ] **Validação base_grupos_config** (seção 3.5) - 0 órfãos
- [ ] **Conexão testada:** `PGPASSWORD=... psql -U finup_user -h 127.0.0.1 -d finup_db -c "SELECT 1;"`

### 4.4 Servidor

- [ ] **SSH OK:** `ssh minha-vps-hostinger 'echo OK'`
- [ ] **Serviços ativos:** `ssh minha-vps-hostinger 'systemctl status finup-backend finup-frontend'`
- [ ] **Health check:** `curl -s https://meufinup.com.br/api/health`

---

## 5. EXECUÇÃO DO DEPLOY

### 5.1 Fluxo Recomendado

```
LOCAL → git push origin main → SERVIDOR (git pull + migrations + restart)
```

### 5.2 Opção A: Script Safe Deploy (com migrations)

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# 1. Garantir que está em main e sincronizado
git checkout main
git pull origin main
git merge feature/consolidate-budget-tables  # ou já mergeado

# 2. Commit e push
git add .
git status  # conferir
git push origin main

# 3. Deploy com migrations
./scripts/deploy/deploy_safe_v2.sh --with-migrations
```

### 5.3 Opção B: Manual (mais controle)

```bash
# 1. LOCAL - Push
git push origin main

# 2. SERVIDOR - Conectar
ssh minha-vps-hostinger

# 3. Backup do banco (OBRIGATÓRIO)
BACKUP_DIR="/root/backups/finup"
mkdir -p $BACKUP_DIR
PGPASSWORD=FinUp2026SecurePass pg_dump -U finup_user -h 127.0.0.1 finup_db \
  | gzip > $BACKUP_DIR/finup_db_pre_deploy_$(date +%Y%m%d_%H%M%S).sql.gz

# 4. Pull e migrations
cd /var/www/finup
git pull origin main

cd app_dev/backend
source venv/bin/activate
alembic upgrade head

# 5. Dependências (se requirements.txt mudou)
pip install -r requirements.txt

# 6. Frontend (build)
cd ../frontend
npm ci
npm run build

# 7. Restart serviços
systemctl restart finup-backend finup-frontend

# 8. Validar
sleep 5
curl -s localhost:8000/api/health
systemctl status finup-backend finup-frontend --no-pager
```

### 5.4 Quick Deploy (sem migrations - apenas código)

```bash
./scripts/deploy/quick_deploy.sh
```

**Atenção:** Não aplica migrations. Use apenas se não houver mudanças de schema.

---

## 6. PÓS-DEPLOY E VALIDAÇÃO

### 6.1 Health Check

```bash
curl -s https://meufinup.com.br/api/health | jq .
# Esperado: {"status":"healthy","database":"connected"}
```

### 6.2 Smoke Tests

- [ ] **Login:** https://meufinup.com.br/login
- [ ] **Dashboard:** https://meufinup.com.br/dashboard
- [ ] **Transações:** https://meufinup.com.br/transactions
- [ ] **Budget/Metas:** https://meufinup.com.br/budget/planning
- [ ] **Mobile:** https://meufinup.com.br/mobile/dashboard
- [ ] **Upload:** https://meufinup.com.br/upload

### 6.3 Logs

```bash
ssh minha-vps-hostinger 'journalctl -u finup-backend -n 50 --no-pager'
ssh minha-vps-hostinger 'journalctl -u finup-frontend -n 30 --no-pager'
```

### 6.4 Verificar Migrations Aplicadas

```bash
ssh minha-vps-hostinger "cd /var/www/finup/app_dev/backend && source venv/bin/activate && alembic current"
# Esperado: 599d728bc4da (head)
```

---

## 7. ROLLBACK

### 7.1 Rollback de Código (sem reverter banco)

```bash
ssh minha-vps-hostinger
cd /var/www/finup
git log --oneline -5
git checkout <commit-anterior>
systemctl restart finup-backend finup-frontend
```

### 7.2 Rollback de Migrations + Banco

```bash
# 1. Restaurar backup (seção 3.6)
# 2. Reverter código para commit anterior
# 3. Restart serviços
```

### 7.3 Contatos de Emergência

- **Documentação:** `docs/deploy/`, `docs/features/mobile-v1/02-TECH_SPEC/INFRASTRUCTURE.md`
- **Scripts:** `scripts/deploy/`
- **Validação:** `./scripts/deploy/validate_server_access.sh`

---

## 📎 ANEXOS

### A. Estrutura de Migrations (ordem de aplicação)

```
f6f307855c81 (initial_schema)
    → 6977f246014c (add_ativo_field_to_budget_planning)
    → 9feefd17fcda (adiciona_index_composto_base_padroes)
    → 635e060a2434 (consolidate_budget_tables)  ← DROP 3 tabelas
    → 599d728bc4da (cleanup_base_marcacoes) [HEAD]
```

### B. Arquivos de Configuração no Servidor

| Arquivo | Path |
|---------|------|
| Backend .env | `/var/www/finup/app_dev/backend/.env` |
| Frontend .env | `/var/www/finup/app_dev/frontend/.env.production` |
| Nginx | `/etc/nginx/sites-available/finup` |
| Backend service | `/etc/systemd/system/finup-backend.service` |
| Frontend service | `/etc/systemd/system/finup-frontend.service` |

### C. Venv no Servidor

O `deploy_safe_v2.sh` usa `cd app_dev/backend && source venv/bin/activate`. Se o venv estiver em `app_dev/venv`, ajustar:

```bash
cd /var/www/finup/app_dev/backend
source ../venv/bin/activate  # ou source ../../venv/bin/activate conforme estrutura
alembic upgrade head
```

### D. Referências

- `docs/deploy/GUIA_DEPLOY_PRODUCAO.md` - Guia completo de infraestrutura
- `docs/deploy/DEPLOY_PROCESS.md` - Regras de deploy
- `docs/deploy/STATUS_DEPLOY.md` - Status atual
- `docs/features/budget-consolidation/BREAKING_CHANGES.md` - Mudanças da consolidação
- `.github/copilot-instructions.md` - Regras e credenciais SSH

---

**Última atualização:** 14/02/2026
