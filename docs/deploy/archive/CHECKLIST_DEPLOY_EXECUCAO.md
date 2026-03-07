# ✅ Checklist de Deploy - Execução em Andamento

**Data início:** 14/02/2026  
**Objetivo:** Deploy seguro e completo para meufinup.com.br  
**Referência:** [DEPLOY_MEUFINUP_ATUALIZACAO_2026.md](./DEPLOY_MEUFINUP_ATUALIZACAO_2026.md)

---

## FASE 1 - PRÉ-DEPLOY LOCAL

### 1.1 Git e Código
- [x] **1.1.1** Git status limpo (sem alterações não commitadas) ✅
- [x] **1.1.2** Branch: `main` (ou merge de feature concluído) ✅
- [x] **1.1.3** Código commitado e sincronizado com remoto ✅

**Comentários:**
> ✅ Merge concluído. Push main → origin (a657a52f).

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
- [x] **2.1.1** Merge `feature/consolidate-budget-tables` → `main` ✅
- [x] **2.1.2** `git push origin main` ✅

**Comentários:**
> ✅ Concluído. main em a657a52f.

### 2.2 Validação Servidor (pré-pull)
- [x] **2.2.1** SSH conecta (`ssh minha-vps-hostinger`) ✅
- [x] **2.2.2** Serviços ativos (finup-backend, finup-frontend) ✅
- [ ] **2.2.3** Health check atual OK

**Comentários:**
> ✅ SSH e path /var/www/finup OK. Backend e frontend ativos.

---

## FASE 3 - BACKUP PRODUÇÃO (CRÍTICO)

### 3.1 Backup PostgreSQL
- [x] **3.1.1** Backup criado no servidor (`pg_dump` → .sql.gz) ✅
- [x] **3.1.2** Arquivo de backup verificado (tamanho > 0) ✅

**Comentários:**
> ✅ finup_db_pre_deploy_20260214_172344.sql.gz (408K)

---

## FASE 4 - VALIDAÇÃO PRÉ-MIGRATION (PostgreSQL)

### 4.1 base_grupos_config
- [x] **4.1.1** Query: grupos órfãos em base_marcacoes (deve retornar 0 linhas) ✅
- [x] **4.1.2** Se houver órfãos: INSERT em base_grupos_config antes de rodar 599d728bc4da ✅

**Comentários:**
> ✅ Havia 6 órfãos "Outros". INSERT executado. Órfãos = 0.

---

## FASE 5 - DEPLOY NO SERVIDOR

### 5.1 Código
- [x] **5.1.1** `cd /var/www/finup && git pull origin main` ✅
- [x] **5.1.2** Conflitos resolvidos (se houver) ✅

### 5.2 Migrations
- [x] **5.2.1** `alembic upgrade head` executado ✅
- [x] **5.2.2** Sem erros na saída ✅
- [x] **5.2.3** `alembic current` = 599d728bc4da ✅

**Comentários:**
> Correções aplicadas: 635e (1→true para boolean), 599d (quoted "GRUPO"/"SUBGRUPO" para PostgreSQL). INSERT "Outros" em base_grupos_config antes da migration.

### 5.3 Dependências
- [x] **5.3.1** `pip install -r requirements.txt` (se requirements mudou) ✅
- [ ] **5.3.2** Frontend: `npm ci && npm run build` ⚠️

**Comentários:**
> ⚠️ Build frontend no servidor falha: Module not found (wallet-constants, goals/lib/utils). Build local OK. Investigar path/workspace root no servidor.

### 5.4 Restart
- [x] **5.4.1** `systemctl restart finup-backend` ✅
- [ ] **5.4.2** `systemctl restart finup-frontend` ⚠️ (falha: sem build válido)
- [x] **5.4.3** Aguardar 5s e verificar status ✅

---

## FASE 6 - VALIDAÇÃO PÓS-DEPLOY

### 6.1 Health e Serviços
- [x] **6.1.1** `curl localhost:8000/api/health` → status healthy ✅
- [x] **6.1.2** `systemctl is-active finup-backend` → active ✅
- [ ] **6.1.3** `systemctl is-active finup-frontend` → active ⚠️ (crash: no production build)

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
| 1. Pré-deploy local | ✅ | Build, backup, commit OK |
| 2. Preparação | ✅ | Merge main, push OK |
| 3. Backup produção | ✅ | finup_db_pre_deploy_20260214_172344.sql.gz |
| 4. Validação pré-migration | ✅ | INSERT Outros em base_grupos_config |
| 5. Deploy servidor | ⚠️ | Backend ✅, Migrations ✅, Frontend ❌ |
| 6. Validação pós | ⚠️ | Backend healthy, Frontend sem build |

**Deploy concluído em:** 14/02/2026 ~17:30 UTC  
**Commit deployado:** f7a9027f (main)

### ⚠️ PENDÊNCIA: Frontend
- Build no servidor falha: `Module not found` (wallet-constants, goals/lib/utils)
- Backend e API funcionando: https://meufinup.com.br/api/health
- Próximo passo: Corrigir imports ou criar arquivos faltantes no servidor
