# Deploy Branch feature/revisao-completa-do-app na VM

**Data:** 21/02/2026  
**Branch:** `feature/revisao-completa-do-app`  
**Objetivo:** Subir alterações na VM e validar schema local (SQLite) vs PostgreSQL (produção).

---

## Resumo das alterações no branch

- **Backend:** Endpoints `orcamento-investimentos`, `aporte-periodo`, `aporte-mes`; suporte YTD/ano em métricas e chart
- **Migrations novas:**
  - `d7e8f9a0b1c2` – Sprint H: Cenários aposentadoria (investimentos_cenarios, investimentos_cenario_projecao)
  - `e8f9a0b1c2d3` – Coluna `aporte` em investimentos_cenario_projecao
- **Frontend:** Dashboard mobile (Mês/YTD/Ano), OrcamentoTab resiliente, BarChart modo anual

---

## Pré-requisitos

1. **PROD_DATABASE_URL** no `.env` do backend (para validação de schema):
   ```
   PROD_DATABASE_URL=postgresql://finup_user:SENHA@127.0.0.1:5432/finup_db
   ```
   *(Use a URL real do PostgreSQL na VM – pode ser via túnel SSH se necessário.)*

2. **Backup** do banco local antes de qualquer alteração crítica.

---

## Etapa 1 – Local: validações e backup

```bash
# 1. Backup do banco local
./scripts/deploy/backup_daily.sh

# 2. Garantir que migrations estão aplicadas localmente
cd app_dev/backend
source ../../venv/bin/activate   # ou .venv
alembic current
alembic upgrade head

# 3. (Opcional) Safe deploy – valida Git, backend, frontend
./scripts/deploy/safe_deploy.sh
```

---

## Etapa 2 – Validação de schema (Local vs Prod)

Compara estrutura de tabelas/colunas entre SQLite local e PostgreSQL na VM.

```bash
cd app_dev/backend

# Carregar PROD_DATABASE_URL do .env (ou export manual)
# Se PostgreSQL da VM não for acessível diretamente, use túnel:
# ssh -L 5432:127.0.0.1:5432 user@148.230.78.91

python ../../scripts/deploy/validate_schema_local_vs_prod.py
```

**Resultado esperado antes do deploy:**
- Tabelas/colunas que existem no local e faltam no prod (ex.: `investimentos_cenario_projecao`, coluna `aporte`)
- Após rodar `alembic upgrade head` no servidor, a validação deve indicar schemas compatíveis.

---

## Etapa 3 – Push da branch

```bash
git push origin feature/revisao-completa-do-app
```

---

## Etapa 4 – Deploy na VM

Conectar na VM e executar:

```bash
# 1. Ir ao diretório do projeto
cd /var/www/finup   # ou path configurado

# 2. Backup do PostgreSQL (antes de migrations)
pg_dump -U finup_user finup_db > backup_pre_deploy_$(date +%Y%m%d_%H%M).sql

# 3. Pull da branch
git fetch origin
git checkout feature/revisao-completa-do-app
git pull origin feature/revisao-completa-do-app

# 4. Ativar venv e aplicar migrations
cd app_dev/backend
source venv/bin/activate
alembic upgrade head

# 5. Rebuild frontend (se houver mudanças)
cd ../frontend
npm install
npm run build

# 6. Reiniciar serviços
sudo systemctl restart finup-backend finup-frontend

# 7. Verificar logs
sudo journalctl -u finup-backend -f -n 50
```

---

## Etapa 5 – Validação pós-deploy

1. **Health check:** `curl https://seu-dominio/api/health`
2. **Dashboard mobile:** Acessar `/mobile/dashboard` e conferir:
   - Toggle Mês/YTD/Ano
   - Resumo (Receitas, Despesas, Investidos)
   - Gráfico anual
   - Aba Patrimônio com aporte do cenário principal
3. **Logs:** Sem erros 404 ou 500 nos endpoints novos.

---

## Rollback (se necessário)

```bash
# Na VM
cd /var/www/finup
git checkout main
git pull origin main

cd app_dev/backend
alembic downgrade -1   # ou até a revisão anterior

sudo systemctl restart finup-backend finup-frontend

# Restaurar banco (se migrations quebraram algo)
# psql -U finup_user finup_db < backup_pre_deploy_YYYYMMDD_HHMM.sql
```

---

## Checklist rápido

- [ ] Backup local (`backup_daily.sh`)
- [ ] Migrations aplicadas localmente (`alembic upgrade head`)
- [ ] Validação de schema (`validate_schema_local_vs_prod.py`)
- [ ] Push da branch
- [ ] Backup PostgreSQL na VM
- [ ] Pull da branch na VM
- [ ] `alembic upgrade head` na VM
- [ ] Rebuild frontend
- [ ] Restart serviços
- [ ] Teste manual no dashboard mobile

---

## Referências

- [PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md](PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md)
- [VALIDACAO_GIT_20FEV2026.md](VALIDACAO_GIT_20FEV2026.md)
- [safe_deploy.sh](../../scripts/deploy/safe_deploy.sh)
