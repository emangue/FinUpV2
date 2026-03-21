# Skill: Deploy

> Skill de deploy autossuficiente com validação completa embutida: pré-deploy, versão, branch, mudanças, migrations e go/no-go antes de subir para produção.

---

## Contexto fixo do projeto

| Item | Valor |
|---|---|
| SSH Host | `minha-vps-hostinger` |
| Path na VM | `/var/www/finup` |
| Compose prod | `docker-compose.prod.yml` |
| Backend prod | `finup_backend_prod` (:8000) |
| Frontend app | `finup_frontend_app_prod` (:3003) |
| Frontend admin | `finup_frontend_admin_prod` (:3001) |
| Backend dev | `finup_backend_dev` (:8000) |
| DB dev | `finup_postgres_dev` |
| Versão local | `VERSION.md` (campo `Versão Atual`) |
| Migrations | `app_dev/backend/migrations/versions/` |
| Backend URL | `http://localhost:8000` |
| Frontend URL | `http://localhost:3000` |
| Admin Email | `admin@financas.com` |

---

## FASE 1 — Diagnóstico git e versão

Execute todos os comandos e guarde os resultados para o painel final.

### 1.1 Branch e commits locais

```bash
git branch --show-current
git status --short | grep -v '^??'
git log --oneline -5
```

**Avalie:**
- Fora de `main` → **BLOCKER**
- Arquivos modificados/staged → **BLOCKER**

### 1.2 Sincronismo com remoto

```bash
git fetch origin --quiet
git log HEAD..origin/$(git branch --show-current) --oneline
git log origin/$(git branch --show-current)..HEAD --oneline
```

- Commits locais não enviados → precisa de `git push` antes do deploy

### 1.3 Versão local

```bash
grep -m1 "Versão Atual" VERSION.md
git log --oneline -1
```

### 1.4 Versão e commit na VM

```bash
ssh minha-vps-hostinger "cd /var/www/finup && git log --oneline -1 && grep -m1 'Versão Atual' VERSION.md 2>/dev/null"
```

### 1.5 Commits que serão deployados

```bash
COMMIT_VM=$(ssh minha-vps-hostinger "cd /var/www/finup && git rev-parse HEAD" 2>/dev/null)
git log ${COMMIT_VM}..HEAD --oneline 2>/dev/null || git log --oneline -10
```

### 1.6 Arquivos alterados desde o commit da VM

```bash
git diff --name-status ${COMMIT_VM} HEAD 2>/dev/null
```

**Classifique:**
- `app_dev/backend/` → backend mudou
- `app_dev/frontend/` → frontend mudou
- `app_dev/backend/migrations/versions/` → **migration obrigatória**
- `docker-compose.prod.yml` ou `Dockerfile` → rebuild necessário

### 1.7 SSH e disco da VM

```bash
ssh minha-vps-hostinger "echo 'SSH OK'"
ssh minha-vps-hostinger "df -h / | tail -1 && docker system df --format 'Images: {{.ImagesSize}}  Containers: {{.ContainersSize}}'"
```

- SSH falhou → **BLOCKER**
- Disco `<` 500MB → **BLOCKER**

---

## FASE 2 — Pré-deploy: ambiente local (embutido)

> Executa todos os checks do predeploy.py diretamente — sem chamar script externo.

### 2.1 B — Bloqueantes do ambiente local

**B1 — Docker: 5 containers running**
```bash
for c in finup_backend_dev finup_frontend_app_dev finup_frontend_admin_dev finup_postgres_dev finup_redis_dev; do
  state=$(docker inspect --format="{{.State.Status}}" $c 2>/dev/null)
  echo "$c → $state"
done
```
Todos devem retornar `running`. Qualquer outro valor → **BLOCKER**.

**B2 — Backend health**
```bash
curl -s http://localhost:8000/api/health
```
Deve conter `"healthy"`. Senão → **BLOCKER**.

**B3 — Login JWT**
```bash
# Substitua SENHA pela senha do admin (pergunte ao usuário se não souber)
curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"SENHA"}'
```
Deve retornar `access_token`. Guarde como `TOKEN`. Se não retornar → **BLOCKER**.

**B4 — Git workspace limpo**
```bash
git status --short | grep -v '^??'
```
Sem saída = limpo. Com saída → **BLOCKER** (arquivos não commitados).

---

### 2.2 API — Smoke Tests (11 endpoints)

Com o `TOKEN` obtido no B3, execute cada check abaixo. Esperado: HTTP 200.

```bash
MONTH=$(date +%Y-%m)
YEAR=$(date +%Y)
TOKEN="<token_do_B3>"

# A1 — Health (sem auth)
curl -s -o /dev/null -w "A1 /api/health → %{http_code}\n" "http://localhost:8000/api/health"

# A2 — Dashboard last month
curl -s -o /dev/null -w "A2 /dashboard/last-month → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/dashboard/last-month-with-data"

# A3 — Dashboard metrics
curl -s -o /dev/null -w "A3 /dashboard/metrics → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/dashboard/metrics?mes_referencia=$MONTH"

# A4 — Budget
curl -s -o /dev/null -w "A4 /budget → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/budget?mes_referencia=$MONTH"

# A5 — Investimentos
curl -s -o /dev/null -w "A5 /investimentos → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/investimentos/"

# A6 — Cenários
curl -s -o /dev/null -w "A6 /investimentos/cenarios → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/investimentos/cenarios"

# A7 — Plano perfil
curl -s -o /dev/null -w "A7 /plano/perfil → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/plano/perfil"

# A8 — Plano cashflow
curl -s -o /dev/null -w "A8 /plano/cashflow → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/plano/cashflow?ano=$YEAR"

# A9 — Upload history
curl -s -o /dev/null -w "A9 /upload/history → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/upload/history"

# A10 — Grupos
curl -s -o /dev/null -w "A10 /grupos → %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/grupos/"

# A11 — Swagger (sem auth)
curl -s -o /dev/null -w "A11 /docs → %{http_code}\n" \
  "http://localhost:8000/docs"
```

Qualquer retorno diferente de 200 → registrar como FAIL no painel.

---

### 2.3 DB — Banco de dados (7 tabelas)

```bash
# Conta registros nas tabelas críticas
for table_min in \
  "journal_entries:100" \
  "investimentos_portfolio:1" \
  "investimentos_cenarios:1" \
  "plano_cashflow_mes:1" \
  "budget_planning:0" \
  "base_marcacoes:1" \
  "users:1"
do
  table="${table_min%%:*}"
  min="${table_min##*:}"
  count=$(docker exec finup_postgres_dev psql -U finup_user -d finup_db \
    -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ')
  echo "DB $table → $count registros (mín: $min)"
done
```

Tabela não encontrada ou contagem abaixo do mínimo → registrar como FAIL.

---

### 2.4 Migration — Detecção

```bash
# Migrations no repositório
ls -t app_dev/backend/migrations/versions/*.py | grep -v __pycache__ | head -5

# Migration atual no container de dev
docker exec finup_backend_dev alembic -c /app/alembic.ini current 2>/dev/null
```

Se há arquivos `.py` mais novos que `COMMIT_VM` em `migrations/versions/` → **migration obrigatória** no deploy.

---

## FASE 3 — Painel consolidado (go / no-go)

Apresente o painel antes de qualquer execução:

```
╔═══════════════════════════════════════════════════════════════╗
║                  PAINEL DE DEPLOY — FinUp                    ║
╠═══════════════════════════════════════════════════════════════╣
║  GIT & VERSÃO                                                ║
║  Branch atual        │ main                         ✅/❌   ║
║  Git workspace       │ limpo / X arquivos           ✅/❌   ║
║  Push pendente       │ N commits / nenhum           ✅/❌   ║
║  Versão local        │ X.Y.Z (commit: abc1234)             ║
║  Versão na VM        │ X.Y.Z (commit: def5678)             ║
║  Commits a deployr   │ N commits                           ║
╠═══════════════════════════════════════════════════════════════╣
║  MUDANÇAS                                                    ║
║  Backend mudou?      │ sim/não                      🔵/⬜   ║
║  Frontend mudou?     │ sim/não                      🔵/⬜   ║
║  Dockerfile mudou?   │ sim/não                      🔵/⬜   ║
║  Migration?          │ SIM — obrigatório / não      🔴/✅   ║
╠═══════════════════════════════════════════════════════════════╣
║  INFRA                                                       ║
║  SSH acessível       │ sim/não                      ✅/❌   ║
║  Disco VM            │ XGB livre                    ✅/⚠️   ║
╠═══════════════════════════════════════════════════════════════╣
║  PRÉ-DEPLOY LOCAL                                            ║
║  B1 Docker (5/5)     │ running / X down             ✅/❌   ║
║  B2 Health           │ healthy / falhou             ✅/❌   ║
║  B3 Login JWT        │ token OK / sem token         ✅/❌   ║
║  B4 Git status       │ limpo / sujo                 ✅/❌   ║
║  API Smoke Tests     │ 11/11 / X falha(s)           ✅/❌   ║
║  DB Checks           │ 7/7 / X falha(s)             ✅/❌   ║
╠═══════════════════════════════════════════════════════════════╣
║  BLOCKERS            │ N                                    ║
║  AVISOS              │ N                                    ║
╠═══════════════════════════════════════════════════════════════╣
║  VEREDICTO           │ ✅ PODE DEPLOIAR / ❌ BLOQUEADO      ║
╚═══════════════════════════════════════════════════════════════╝
```

**Com BLOCKERS → pare e descreva o que precisa ser resolvido.**
**Só avisos → descreva e pergunte se quer continuar.**

---

## FASE 4 — Plano de execução

Apresente o plano exato antes de executar qualquer coisa:

```
PLANO:
1. git push origin main
2. bash deploy/scripts/deploy_docker_vm.sh   ← ou deploy_docker_build_local.sh
3. [Se migration detectada] alembic upgrade head
4. Validação pós-deploy
```

**Escolha do script:**
- VM `>` 1GB livre → `deploy_docker_vm.sh` (build na VM, mais rápido)
- VM `<` 1GB livre → `deploy_docker_build_local.sh` (build local + SCP, mais seguro)

**Pergunte:** "Posso executar este plano?" — só execute após confirmação.

---

## FASE 5 — Execução

### 5.1 Push

```bash
git push origin $(git branch --show-current)
```

### 5.2 Deploy

```bash
# Opção A — build na VM
bash deploy/scripts/deploy_docker_vm.sh

# Opção B — build local + SCP
bash deploy/scripts/deploy_docker_build_local.sh
```

### 5.3 Migration (somente se detectada na Fase 2.4)

```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic -c /app/alembic.ini upgrade head"
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic -c /app/alembic.ini current"
```

Confirme que `alembic current` termina com `(head)`.

### 5.4 Validação pós-deploy

```bash
ssh minha-vps-hostinger "curl -s http://localhost:8000/api/health | python3 -m json.tool"
ssh minha-vps-hostinger "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep finup"
bash deploy/scripts/validate_deploy.sh
```

---

## FASE 6 — Relatório final

```
╔═══════════════════════════════════════════════════════════════╗
║                RESULTADO DO DEPLOY — FinUp                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Versão deployada    │ X.Y.Z                                 ║
║  Commit              │ abc1234                               ║
║  Branch              │ main                                  ║
║  Data/hora           │ DD/MM/YYYY HH:MM                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Backend             │ ✅ UP / ❌ FALHOU                     ║
║  Frontend app        │ ✅ UP / ❌ FALHOU                     ║
║  Frontend admin      │ ✅ UP / ❌ FALHOU                     ║
║  Migration           │ ✅ aplicada / ⏭️ não necessária       ║
╠═══════════════════════════════════════════════════════════════╣
║  STATUS GERAL        │ ✅ DEPLOY OK / ❌ VERIFICAR           ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Rollback de emergência

```bash
# Ver commit anterior
git log --oneline -5

# Reverter na VM
ssh minha-vps-hostinger "cd /var/www/finup && git checkout <commit-anterior>"
ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml up -d --build"

# Reverter migration (se aplicada)
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic -c /app/alembic.ini downgrade -1"
```

---

## Regras invioláveis

- NUNCA editar arquivos diretamente na VM
- NUNCA fazer deploy sem push antes
- NUNCA pular migration se detectada
- NUNCA deployar com BLOCKER sem confirmação explícita
- Sempre registrar commit deployado no relatório final
