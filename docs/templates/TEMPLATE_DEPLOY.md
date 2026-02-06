# 🚀 DEPLOY CHECKLIST - [Feature Name]

**Versão do Template:** 1.0  
**Última Atualização:** [Data]  
**Responsável Deploy:** [Nome]  
**Ambiente:** [Produção/Staging]  
**Data Deploy:** [DD/MM/YYYY HH:MM]

---

## 📋 PRÉ-DEPLOY - VALIDAÇÕES OBRIGATÓRIAS

### ✅ Código e Versionamento

- [ ] **Git Status Limpo**
  ```bash
  git status  # Sem uncommitted changes
  git log --oneline -5  # Últimos commits validados
  ```

- [ ] **Branch Correta**
  - [ ] Deploy de `main` (produção) ou `staging` (homologação)
  - [ ] Não fazer deploy de branches `feature/*` ou `fix/*`

- [ ] **Tag Criada**
  ```bash
  git tag -a v1.2.0 -m "Release Feature X"
  git push origin v1.2.0
  ```

- [ ] **CHANGELOG.md Atualizado**
  - [ ] Nova versão documentada
  - [ ] Features listadas
  - [ ] Fixes listados
  - [ ] Breaking changes (se houver)

---

### 🗄️ Database e Migrations

- [ ] **Migrations Validadas Localmente**
  ```bash
  cd app_dev/backend
  source venv/bin/activate
  alembic upgrade head  # Dev environment
  alembic history  # Verificar ordem
  ```

- [ ] **Backup Criado ANTES do Deploy**
  ```bash
  # SQLite (local)
  ./scripts/deploy/backup_daily.sh
  
  # PostgreSQL (produção)
  ssh user@server "pg_dump -U finup_user finup_db > /backup/finup_$(date +%Y%m%d_%H%M%S).sql"
  ```

- [ ] **Schema Validado**
  - [ ] Novas colunas têm DEFAULT ou NULL
  - [ ] Foreign keys corretas
  - [ ] Índices criados para performance
  - [ ] Nenhuma migration destrutiva (DROP) sem validação

- [ ] **Downgrade Testado (Rollback)**
  ```bash
  alembic downgrade -1  # Testar reversão
  alembic upgrade head  # Voltar ao topo
  ```

---

### 🧪 Testes e Qualidade

- [ ] **Todos os Testes Passando**
  ```bash
  # Unit tests (se houver)
  pytest app_dev/backend/tests/
  
  # E2E tests
  cd app_dev/frontend
  npx playwright test
  ```

- [ ] **Coverage ≥ 80%** (se aplicável)
  ```bash
  pytest --cov=app --cov-report=term-missing
  ```

- [ ] **Linters Passando**
  ```bash
  # Backend
  cd app_dev/backend
  ruff check app/
  
  # Frontend
  cd app_dev/frontend
  npm run lint
  ```

- [ ] **Build Sem Erros**
  ```bash
  # Frontend build
  cd app_dev/frontend
  npm run build
  ```

---

### 🔐 Segurança

- [ ] **Secrets Não Commitados**
  ```bash
  git log --all --full-history -- '**/.env*' '**/*secret*'
  # Deve retornar vazio!
  ```

- [ ] **Variáveis de Ambiente Configuradas**
  - [ ] `.env` no servidor tem todas as keys necessárias
  - [ ] Nenhum secret hardcoded no código
  - [ ] JWT_SECRET_KEY único por ambiente
  - [ ] DATABASE_URL correto (PostgreSQL prod)

- [ ] **CORS Configurado**
  - [ ] BACKEND_CORS_ORIGINS específico (não "*")
  - [ ] Frontend domain permitido

- [ ] **Rate Limiting Ativo**
  - [ ] Login: 5/minute
  - [ ] Global: 200/minute
  - [ ] Upload: 10/minute

---

### 📊 Performance

- [ ] **Lighthouse ≥ 85** (todas as páginas)
  ```bash
  npx lighthouse http://localhost:3000 --view
  npx lighthouse http://localhost:3000/dashboard --view
  ```

- [ ] **Queries Otimizadas**
  - [ ] Nenhuma query N+1 detectada
  - [ ] Índices em colunas filtradas
  - [ ] Eager loading de relationships

- [ ] **Assets Otimizados**
  - [ ] Imagens comprimidas
  - [ ] JS bundle < 500KB
  - [ ] CSS minificado

---

## 🚀 DEPLOY - EXECUÇÃO

### 1️⃣ Parar Servidores

```bash
# Local (dev)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./scripts/deploy/quick_stop.sh

# Produção (servidor)
ssh user@servidor
systemctl stop finup-backend finup-frontend
```

**Checklist:**
- [ ] Backend parado (porta 8000 livre)
- [ ] Frontend parado (porta 3000 livre)
- [ ] Nenhum processo órfão (`lsof -ti:8000`)

---

### 2️⃣ Pull do Código

```bash
# Produção
ssh user@servidor
cd /var/www/finup

# Validar branch
git branch  # Deve estar em main

# Fazer backup do código atual (se necessário)
cp -r /var/www/finup /backup/finup_$(date +%Y%m%d_%H%M%S)

# Pull
git pull origin main
```

**Checklist:**
- [ ] Pull bem-sucedido
- [ ] Nenhum conflito de merge
- [ ] Tag correta (`git describe --tags`)

---

### 3️⃣ Instalar Dependências

```bash
# Backend
cd /var/www/finup/app_dev/backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd /var/www/finup/app_dev/frontend
npm install
npm run build
```

**Checklist:**
- [ ] Nenhum erro de instalação
- [ ] Versões corretas (`pip list | grep fastapi`)
- [ ] Build frontend sem warnings críticos

---

### 4️⃣ Aplicar Migrations

```bash
cd /var/www/finup/app_dev/backend
source venv/bin/activate

# Ver migrations pendentes
alembic current
alembic history

# BACKUP CRÍTICO ANTES DE APLICAR
pg_dump -U finup_user finup_db > /backup/pre_migration_$(date +%Y%m%d_%H%M%S).sql

# Aplicar migrations
alembic upgrade head

# Validar sucesso
alembic current  # Deve mostrar última revision
```

**Checklist:**
- [ ] Backup criado ANTES do upgrade
- [ ] Upgrade sem erros
- [ ] Revision atual correta
- [ ] Tabelas criadas (`\dt` no psql)

---

### 5️⃣ Iniciar Servidores

```bash
# Produção
systemctl start finup-backend
systemctl start finup-frontend

# Verificar status
systemctl status finup-backend
systemctl status finup-frontend

# Ver logs em tempo real
journalctl -u finup-backend -f
journalctl -u finup-frontend -f
```

**Checklist:**
- [ ] Backend ativo (`systemctl is-active finup-backend`)
- [ ] Frontend ativo (`systemctl is-active finup-frontend`)
- [ ] Nenhum erro nos logs

---

## ✅ PÓS-DEPLOY - SMOKE TESTS

### 🔍 Health Checks

```bash
# Backend health
curl -s https://meufinup.com.br/api/health | jq .
# Esperado: {"status": "ok", "version": "1.2.0"}

# Frontend acessível
curl -I https://meufinup.com.br
# Esperado: HTTP/1.1 200 OK
```

**Checklist:**
- [ ] `/api/health` retorna 200
- [ ] Frontend carrega (`curl -I` = 200)
- [ ] HTTPS ativo (certificado válido)

---

### 🔐 Autenticação

```bash
# Testar login
curl -X POST https://meufinup.com.br/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"[SENHA]"}' | jq .

# Esperado: {"access_token": "eyJ...", "token_type": "bearer"}
```

**Checklist:**
- [ ] Login bem-sucedido
- [ ] Token JWT retornado
- [ ] Endpoint protegido aceita token

---

### 📊 Funcionalidades Críticas

**Testar MANUALMENTE no navegador:**

- [ ] **Login** - `https://meufinup.com.br`
  - [ ] Email/senha corretos aceitos
  - [ ] Redirecionamento para dashboard

- [ ] **Dashboard** - `https://meufinup.com.br/dashboard`
  - [ ] Gráficos carregam
  - [ ] Dados exibidos (não vazio)
  - [ ] Filtros funcionam (mês/ano)

- [ ] **Transações** - `https://meufinup.com.br/transactions`
  - [ ] Lista carrega
  - [ ] Paginação funciona
  - [ ] Edição funciona
  - [ ] Exclusão funciona

- [ ] **Upload** - `https://meufinup.com.br/upload`
  - [ ] Arrastar arquivo funciona
  - [ ] Processamento OK
  - [ ] Preview exibido

- [ ] **Mobile** - `https://meufinup.com.br/mobile/profile`
  - [ ] Layout responsivo
  - [ ] Toque funciona
  - [ ] Scroll suave

---

### 📈 Performance

```bash
# Lighthouse no servidor
npx lighthouse https://meufinup.com.br --view

# Query lenta (verificar logs)
ssh user@servidor "journalctl -u finup-backend --since '5 minutes ago' | grep 'slow query'"
```

**Checklist:**
- [ ] Lighthouse ≥ 85
- [ ] Página carrega < 3s
- [ ] Nenhuma query > 1s (ver logs)

---

## 🚨 ROLLBACK - SE DEPLOY FALHAR

### 1️⃣ Identificar Problema

```bash
# Ver logs de erro
journalctl -u finup-backend --since '10 minutes ago' | grep -i error
journalctl -u finup-frontend --since '10 minutes ago' | grep -i error

# Verificar status
systemctl status finup-backend
systemctl status finup-frontend
```

---

### 2️⃣ Rollback do Código

```bash
ssh user@servidor
cd /var/www/finup

# Ver última tag estável
git tag -l --sort=-version:refname | head -5

# Voltar para tag estável
git checkout v1.1.0

# Reinstalar dependências (se necessário)
cd app_dev/backend && pip install -r requirements.txt
cd app_dev/frontend && npm install && npm run build
```

---

### 3️⃣ Rollback do Banco (SE MIGRATION DEU ERRO)

```bash
# Restaurar backup PostgreSQL
ssh user@servidor
psql -U finup_user finup_db < /backup/pre_migration_YYYYMMDD_HHMMSS.sql

# OU downgrade Alembic (se migration não destrutiva)
cd /var/www/finup/app_dev/backend
source venv/bin/activate
alembic downgrade -1  # Volta 1 revision
```

**⚠️ CUIDADO:** Rollback de migrations pode perder dados recentes!

---

### 4️⃣ Reiniciar Servidores

```bash
systemctl restart finup-backend finup-frontend

# Verificar saúde
curl -s https://meufinup.com.br/api/health | jq .
```

---

### 5️⃣ Comunicar Rollback

- [ ] Notificar stakeholders (email/Slack)
- [ ] Documentar problema em `FIX_[data]_[descricao].md`
- [ ] Criar issue no GitHub
- [ ] Agendar novo deploy após correção

---

## 📝 PÓS-DEPLOY COMPLETO

### ✅ Checklist Final

- [ ] **Servidores Operacionais**
  - Backend online (systemctl status)
  - Frontend online (systemctl status)

- [ ] **Smoke Tests Passaram**
  - Health checks OK
  - Autenticação OK
  - Funcionalidades críticas OK

- [ ] **Performance Validada**
  - Lighthouse ≥ 85
  - Queries < 1s
  - Página < 3s

- [ ] **Monitoramento Ativo**
  - Logs sendo coletados
  - Alertas configurados (se houver)
  - Backup diário agendado

- [ ] **Documentação Atualizada**
  - CHANGELOG.md tem nova versão
  - README.md atualizado (se necessário)
  - POST_MORTEM.md criado (48h após deploy)

---

### 📊 Métricas do Deploy

**Preencher ao final:**

| Métrica                     | Valor |
|----------------------------|-------|
| Tempo total deploy         | ___ min |
| Downtime                   | ___ min |
| Bugs encontrados pós-deploy| ___ |
| Rollbacks necessários      | ___ |
| Lighthouse Score (antes)   | ___ |
| Lighthouse Score (depois)  | ___ |

---

### 🎯 Ações Pós-Deploy

- [ ] **48h:** Monitorar erros em produção (Sentry/logs)
- [ ] **48h:** Criar POST_MORTEM.md (o que funcionou, o que melhorar)
- [ ] **7 dias:** Validar métricas (usuários ativos, performance)
- [ ] **7 dias:** Coletar feedback de usuários
- [ ] **30 dias:** Retrospectiva de impacto (KPIs alcançados?)

---

## 🔗 Referências

- **WoW:** `/docs/WOW.md`
- **Scripts:** `/scripts/deploy/`
- **Servidor:** `/docs/deploy/GUIA_SERVIDORES.md`
- **SSH:** `/docs/deploy/SSH_ACCESS.md`
- **Backup:** `/docs/deploy/BACKUP_STRATEGY.md`

---

**✅ Deploy finalizado com sucesso!**  
**📅 Data/Hora:** [PREENCHER]  
**👤 Responsável:** [NOME]  
**🏷️ Versão:** [v1.2.0]
