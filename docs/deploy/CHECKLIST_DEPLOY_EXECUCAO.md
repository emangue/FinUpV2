# ✅ Checklist de Deploy - Execução em Andamento

**Data início:** 14/02/2026  
**Objetivo:** Deploy seguro e completo para meufinup.com.br  
**Referência:** [DEPLOY_MEUFINUP_ATUALIZACAO_2026.md](./DEPLOY_MEUFINUP_ATUALIZACAO_2026.md)

---

## FASE 1 - PRÉ-DEPLOY LOCAL

### 1.1 Git e Código
- [x] **1.1.1** Git status limpo (sem alterações não commitadas) ✅
- [ ] **1.1.2** Branch: `main` (ou merge de feature concluído)
- [ ] **1.1.3** Código commitado e sincronizado com remoto

**Comentários:**
> ✅ Commit abf3f9b9 feito. Merge para main pendente.

### 1.2 Validação Técnica
- [x] **1.2.1** Build frontend OK (`npm run build`) ✅
- [x] **1.2.2** Backend inicia sem erros ✅
- [x] **1.2.3** Alembic current = head (599d728bc4da) ✅
- [ ] **1.2.4** Migrations testadas localmente (upgrade/downgrade)

**Comentários:**
> ✅ Build OK após `npm ci` (node_modules reinstalado). Alembic em 599d728bc4da (head).

### 1.3 Backup Local
- [x] **1.3.1** Backup SQLite executado (`./scripts/deploy/backup_daily.sh`) ✅

**Comentários:**
> ✅ Backup: financas_dev_2026-02-14.db em backups_daily/

---

## FASE 2 - PREPARAÇÃO PARA DEPLOY

### 2.1 Merge e Push
- [ ] **2.1.1** Merge `feature/consolidate-budget-tables` → `main`
- [ ] **2.1.2** `git push origin main`

**Comentários:**
> _Aguardando execução..._

### 2.2 Validação Servidor (pré-pull)
- [ ] **2.2.1** SSH conecta (`ssh minha-vps-hostinger`)
- [ ] **2.2.2** Serviços ativos (finup-backend, finup-frontend)
- [ ] **2.2.3** Health check atual OK

**Comentários:**
> _Aguardando execução..._

---

## FASE 3 - BACKUP PRODUÇÃO (CRÍTICO)

### 3.1 Backup PostgreSQL
- [ ] **3.1.1** Backup criado no servidor (`pg_dump` → .sql.gz)
- [ ] **3.1.2** Arquivo de backup verificado (tamanho > 0)

**Comentários:**
> _OBRIGATÓRIO antes de migrations. Rollback depende deste backup._

---

## FASE 4 - VALIDAÇÃO PRÉ-MIGRATION (PostgreSQL)

### 4.1 base_grupos_config
- [ ] **4.1.1** Query: grupos órfãos em base_marcacoes (deve retornar 0 linhas)
- [ ] **4.1.2** Se houver órfãos: INSERT em base_grupos_config antes de rodar 599d728bc4da

**Comentários:**
> _Migration 599d728bc4da FALHA se existirem grupos em base_marcacoes sem config._

---

## FASE 5 - DEPLOY NO SERVIDOR

### 5.1 Código
- [ ] **5.1.1** `cd /var/www/finup && git pull origin main`
- [ ] **5.1.2** Conflitos resolvidos (se houver)

### 5.2 Migrations
- [ ] **5.2.1** `alembic upgrade head` executado
- [ ] **5.2.2** Sem erros na saída
- [ ] **5.2.3** `alembic current` = 599d728bc4da

### 5.3 Dependências
- [ ] **5.3.1** `pip install -r requirements.txt` (se requirements mudou)
- [ ] **5.3.2** Frontend: `npm ci && npm run build`

### 5.4 Restart
- [ ] **5.4.1** `systemctl restart finup-backend`
- [ ] **5.4.2** `systemctl restart finup-frontend`
- [ ] **5.4.3** Aguardar 5s e verificar status

---

## FASE 6 - VALIDAÇÃO PÓS-DEPLOY

### 6.1 Health e Serviços
- [ ] **6.1.1** `curl localhost:8000/api/health` → status healthy
- [ ] **6.1.2** `systemctl is-active finup-backend` → active
- [ ] **6.1.3** `systemctl is-active finup-frontend` → active

### 6.2 Smoke Tests (URLs públicas)
- [ ] **6.2.1** https://meufinup.com.br → 200
- [ ] **6.2.2** https://meufinup.com.br/api/health → JSON OK
- [ ] **6.2.3** https://meufinup.com.br/login → carrega
- [ ] **6.2.4** https://meufinup.com.br/dashboard → (após login)
- [ ] **6.2.5** https://meufinup.com.br/mobile/dashboard → carrega

### 6.3 Logs
- [ ] **6.3.1** `journalctl -u finup-backend -n 20` sem erros críticos
- [ ] **6.3.2** `journalctl -u finup-frontend -n 20` sem erros críticos

---

## RESUMO FINAL

| Fase | Status | Observações |
|------|--------|-------------|
| 1. Pré-deploy local | ⏳ | |
| 2. Preparação | ⏳ | |
| 3. Backup produção | ⏳ | |
| 4. Validação pré-migration | ⏳ | |
| 5. Deploy servidor | ⏳ | |
| 6. Validação pós | ⏳ | |

**Deploy concluído em:** _-_  
**Commit deployado:** _-_
