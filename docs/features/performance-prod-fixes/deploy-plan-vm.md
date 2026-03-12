# 🚀 Plano de Deploy — Performance Prod Fixes (Sprints 1–4)

**Branch:** `perf/performance-prod-fixes`  
**HEAD local:** `c76b9847`  
**VM atual:** `021a0708` (sem nenhum sprint desta branch)  
**Data:** 2026  

---

## 📋 Resumo do que está indo para produção

| Sprint | Items | O que muda |
|--------|-------|------------|
| **S1** | P5, P7, P8 | Healthcheck frontend; elimina double-fetch Carteira/Investimentos; corrige debounce Transações |
| **S2** | P1 | Cache localStorage/sessionStorage para onboarding (elimina ~8 fetches extras por sessão) |
| **S3** | P2 | Endpoint `/plano/cashflow` usa cache por mês — 12 queries em vez de ~50 por page load |
| **S4** | P3, P6, P9 | React Query (dedup + stale cache); Redis onboarding cache TTL 5 min; Investimentos via overview endpoint |

**Impactos de infraestrutura na VM:**
- Backend precisa de **rebuild** → `redis>=5.0.0` adicionado em `requirements.txt`
- Frontend precisa de **rebuild** → `@tanstack/react-query@^5` adicionado em `package.json`
- Redis já está rodando na VM (`finup_redis_prod` Up 5 days, healthy) ✅
- `REDIS_URL` já deve estar no `.env.prod` da VM (verificar na Fase 2)

---

## ⚠️ Pré-requisitos

- [ ] SSH `minha-vps-hostinger` funcionando: `ssh minha-vps-hostinger "echo ok"`
- [ ] Docker Desktop rodando localmente (para build linux/amd64)
- [ ] `.env.local` na raiz do projeto com `ADMIN_PASSWORD` (para scripts de validação)
- [ ] Tempo estimado: ~25 min (build local ~10 min + SCP ~5 min + VM up ~10 min)

---

## FASE 0 — Pré-deploy local

### 0.1 — Push da branch (OBRIGATÓRIO — o deploy valida que local == origin)

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

git push origin perf/performance-prod-fixes
```

Esperado:
```
* [new branch]  perf/performance-prod-fixes -> perf/performance-prod-fixes
```

### 0.2 — Verificar `.env.local` para os scripts de validação

```bash
# O arquivo deve ter ADMIN_PASSWORD (sem aspas)
cat .env.local | grep -E "ADMIN_|FRONTEND_"
```

Se não tiver:
```bash
echo "ADMIN_PASSWORD=SUA_SENHA_AQUI" >> .env.local
echo "FRONTEND_URL=https://meufinup.com.br" >> .env.local
```

### 0.3 — Verificar REDIS_URL na VM

```bash
ssh minha-vps-hostinger "grep REDIS_URL /var/www/finup/.env.prod"
```

Se não existir:
```bash
ssh minha-vps-hostinger "echo 'REDIS_URL=redis://finup_redis_prod:6379/0' >> /var/www/finup/.env.prod"
```

> **Nota:** Dentro dos containers Docker, o host do Redis é `finup_redis_prod` (nome do container na rede Docker),
> não `localhost`. A URL correta é `redis://finup_redis_prod:6379/0`.

---

## FASE 1 — Deploy para VM

### 1.1 — Executar o deploy completo

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

./deploy/scripts/deploy_docker_build_local.sh
```

O script faz automaticamente:
1. ✅ Valida git limpo e push feito
2. ✅ Build local linux/amd64 de 3 imagens: `finup-backend`, `finup-frontend-app`, `finup-frontend-admin`
3. ✅ `docker save` → tar temporário em `/tmp/`
4. ✅ `scp` para VM em `/tmp/finup-images.tar`
5. ✅ Na VM: `git checkout perf/performance-prod-fixes && git pull`
6. ✅ Na VM: `docker load` + `docker compose up -d`
7. ✅ Aguarda backend health (até 60s)
8. ✅ `alembic upgrade head` (migrations)

**Se falhar no passo 2 por OOM local:** não deve acontecer — build é local, não na VM.

**Se falhar no passo 6 (git checkout na VM):**
```bash
# Verificar manualmente na VM
ssh minha-vps-hostinger "cd /var/www/finup && git fetch origin && git checkout perf/performance-prod-fixes && git pull origin perf/performance-prod-fixes"
```

---

## FASE 2 — Verificações pós-deploy na VM

Executar cada verificação e confirmar antes de avançar.

### 2.1 — Containers rodando

```bash
ssh minha-vps-hostinger "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

Esperado:
```
NAMES                       STATUS
finup_backend_prod          Up X minutes (healthy)
finup_frontend_app_prod     Up X minutes (healthy)   ← P5: healthcheck novo
finup_frontend_admin_prod   Up X minutes
finup_postgres_prod         Up X days (healthy)
finup_redis_prod            Up X days (healthy)
infra_nginx                 Up X days                ← pode estar unhealthy (issue pré-existente)
```

- [ ] `finup_backend_prod` está `healthy`?
- [ ] `finup_frontend_app_prod` está `healthy`? (Sprint 1 P5 adicionou healthcheck com `curl`)
- [ ] `finup_redis_prod` está `healthy`?

### 2.2 — Redis Python instalado no backend

```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod pip show redis 2>&1 | head -3"
```

Esperado:
```
Name: redis
Version: 5.x.x
```

Se não aparecer, o rebuild não incluiu o pacote:
```bash
# Forçar rebuild apenas do backend
ssh minha-vps-hostinger "cd /var/www/finup && docker compose -p finup -f docker-compose.prod.yml build --no-cache backend && docker compose -p finup -f docker-compose.prod.yml up -d backend"
```

### 2.3 — React Query instalado no frontend

```bash
ssh minha-vps-hostinger "docker exec finup_frontend_app_prod node -e \"const p=require('/app/node_modules/@tanstack/react-query/package.json'); console.log(p.version)\" 2>&1"
```

Esperado: `5.x.x`

> **Nota:** No Next.js standalone, o `node_modules` fica em `/app/node_modules/`.
> Se o path não funcionar, verificar com:
> ```bash
> ssh minha-vps-hostinger "docker exec finup_frontend_app_prod find /app -name 'react-query' -maxdepth 5 -type d 2>/dev/null | head -3"
> ```

### 2.4 — Health check completo

```bash
ssh minha-vps-hostinger "curl -sf http://localhost:8000/api/health && echo OK"
```

Esperado: `{"status":"ok",...}OK`

### 2.5 — Redis respondendo e REDIS_URL configurado no backend

```bash
# Ping direto
ssh minha-vps-hostinger "docker exec finup_redis_prod redis-cli ping"

# Verificar se backend consegue conectar (logs na inicialização)
ssh minha-vps-hostinger "docker logs finup_backend_prod 2>&1 | grep -i redis | tail -5"
```

Esperado (ping): `PONG`  
Esperado (logs): sem erros de conexão Redis (erros são silenciosos por design — ver `redis_client.py`)

### 2.6 — Versão do commit na VM

```bash
ssh minha-vps-hostinger "cd /var/www/finup && git log --oneline -3"
```

Deve mostrar `c76b9847` como HEAD.

---

## FASE 3 — Validação Sprint 1: Double-fetch eliminado (`perf_s1_verify.py`)

Executar do MacBook local, apontando para produção.

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Opção A: Usando .env.local (recomendado)
python3 docs/features/performance-prod-fixes/perf_s1_verify.py

# Opção B: Passando credenciais via env
ADMIN_PASSWORD="sua_senha" python3 docs/features/performance-prod-fixes/perf_s1_verify.py --url https://meufinup.com.br

# Opção C: Com browser visível (debug)
python3 docs/features/performance-prod-fixes/perf_s1_verify.py --headed
```

**O que testa:**

| Teste | Critério de PASS | O que verifica |
|-------|-----------------|----------------|
| P7 Carteira | ≤ 1 batch de `/investimentos` em < 1000ms | `selectedMonth = null` inicial + guard |
| P7 Investimentos | ≤ 1 batch de `/investimentos` em < 1000ms | mesmo padrão |
| P8 Transações | ≤ 1 batch de `transactions/list` (window 300ms) em < 700ms | debounce via functional setState |

**Se P7 falhar:** verificar `carteira/page.tsx` linha ~241 e `investimentos/page.tsx` linha ~51 — o `useState<Date | null>(null)` deve estar presente.

**Se P8 falhar:** verificar `transactions/page.tsx` — o `setDebouncedPeriod` deve usar functional update com comparação de igualdade.

**Pré-requisito:** Playwright instalado:
```bash
pip install playwright && playwright install chromium
# ou se usando venv:
source app_dev/venv/bin/activate && pip install playwright && playwright install chromium
```

---

## FASE 4 — Validação Sprint 2: Onboarding cache (`perf_s2_verify.py`)

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Opção A: Usando .env.local
python3 docs/features/performance-prod-fixes/perf_s2_verify.py

# Opção B: Com browser visível (debug)
python3 docs/features/performance-prod-fixes/perf_s2_verify.py --headed
```

**O que testa:**

| Teste | Critério de PASS | O que verifica |
|-------|-----------------|----------------|
| P1-A: 1ª visita dashboard | ≤ 2 chamadas de `/onboarding/progress` | OnboardingGuard faz fetch apenas 1x |
| P1-B: Cache persistido | `localStorage['onboarding_completo'] == 'true'` | setItem após fetch bem-sucedido |
| P1-C: 2ª visita dashboard | **0 chamadas** de `/onboarding/progress` | Guard lê localStorage antes do fetch |
| P1-D: Navegação bottom nav | **0 chamadas** | Cache ainda ativo após troca de rota |

**Se P1-C ou P1-D falharem** (cache não sendo lido):
```bash
# Abrir com browser para inspecionar localStorage manualmente
python3 docs/features/performance-prod-fixes/perf_s2_verify.py --headed
```

---

## FASE 5 — Validação Sprint 3: Cache cashflow backend (P2)

Validação manual via DevTools ou curl. O endpoint `/plano/cashflow` deve disparar apenas **1 request** por carregamento da tela de Plano.

### 5.1 — Medir tempo de resposta do cashflow

```bash
# Obter token primeiro
TOKEN=$(curl -s -X POST https://meufinup.com.br/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"SUA_SENHA"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")

# Medir tempo da 1ª chamada (sem cache)
time curl -sf "https://meufinup.com.br/api/v1/plano/cashflow?ano=$(date +%Y)" \
  -H "Authorization: Bearer $TOKEN" -o /dev/null

# Medir tempo da 2ª chamada (mesmo mês, deve vir do cache Python)
time curl -sf "https://meufinup.com.br/api/v1/plano/cashflow?ano=$(date +%Y)" \
  -H "Authorization: Bearer $TOKEN" -o /dev/null
```

Esperado: 2ª chamada ≈ igual à 1ª (cache é no loop interno por mês, não no endpoint inteiro).

### 5.2 — Verificar no DevTools

Abrir `https://meufinup.com.br/mobile/plano` → Network tab → filtrar por `cashflow`.  
Deve aparecer **apenas 1 request** para `/plano/cashflow` por carregamento (não 2 como antes).

---

## FASE 6 — Validação Sprint 4: Redis + React Query (P3/P6)

### 6.1 — Redis: cache de onboarding sendo criado na VM

```bash
# Acesse o dashboard no browser (https://meufinup.com.br/mobile/dashboard)
# Depois verificar:
ssh minha-vps-hostinger "docker exec finup_redis_prod redis-cli keys 'onboarding:*'"
```

Esperado após primeiro acesso:
```
1) "onboarding:progress:1"
```

Verificar TTL (deve ser ~300 segundos):
```bash
ssh minha-vps-hostinger "docker exec finup_redis_prod redis-cli ttl 'onboarding:progress:1'"
```

Esperado: valor entre 1 e 300.

### 6.2 — Redis: cache invalida após upload

```bash
# Antes do upload
ssh minha-vps-hostinger "docker exec finup_redis_prod redis-cli keys 'onboarding:*'"

# Fazer upload de um arquivo no app

# Após upload (cache deve ter sido deletado)
ssh minha-vps-hostinger "docker exec finup_redis_prod redis-cli keys 'onboarding:*'"
```

Esperado: chave deletada após upload bem-sucedido.

### 6.3 — React Query: deduplicação de requests no Plano

Abrir `https://meufinup.com.br/mobile/plano` → Network tab → filtrar por `cashflow`.

Verificar:
- 1ª visita: **1 request** para `/plano/cashflow`
- Voltar ao dashboard e voltar para Plano: **0 requests** (dados vêm do cache React Query, stale < 2 min)
- Após 2 minutos: 1 request novo (revalidação em background)

Se aparecerem 2 requests (sem deduplicação):
- Verificar se `QueryProvider` está no `layout.tsx`
- Verificar se `TabelaReciboAnual` e `ProjecaoChart` usam o mesmo `queryKey: ['plano','cashflow','anual', ano]`

### 6.4 — Verificar logs do backend (Redis silencioso em erros)

```bash
ssh minha-vps-hostinger "docker logs finup_backend_prod 2>&1 | grep -i 'redis\|cache' | tail -10"
```

> Se `REDIS_URL` estiver errado, o sistema continua funcionando (fallback silencioso).
> O sinal de que Redis está funcionando é a chave aparecer em `redis-cli keys`.

---

## FASE 7 — Medição de performance completa (opcional mas recomendado)

Executar o script de benchmark completo e salvar resultado:

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

source app_dev/venv/bin/activate

python3 scripts/testing/perf_measure.py \
  --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_resultado_pos_deploy_s1234_$(date +%Y%m%d_%H%M%S).txt
```

Comparar com baseline anterior em `deploy/history/`.

---

## FASE 8 — Merge e cleanup

Após todas as validações passarem:

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Merge na main
git checkout main
git merge perf/performance-prod-fixes --no-ff -m "perf: sprints 1-4 — performance prod fixes (P1-P9)"
git push origin main

# Tag de release
git tag -a v$(cat VERSION.md | tr -d '[:space:]') -m "Performance fixes sprints 1-4" 2>/dev/null || \
git tag -a "perf-s1-s4-$(date +%Y%m%d)" -m "Performance fixes sprints 1-4"
git push origin --tags

# A VM vai pegar via próximo deploy ou pull manual
ssh minha-vps-hostinger "cd /var/www/finup && git fetch origin && git checkout main && git pull origin main"
```

---

## 🔍 Troubleshooting rápido

### Redis não conecta no backend

```bash
# Verificar REDIS_URL no .env.prod
ssh minha-vps-hostinger "grep REDIS_URL /var/www/finup/.env.prod"

# Valor correto (dentro da rede Docker, usar nome do container)
# REDIS_URL=redis://finup_redis_prod:6379/0

# Reiniciar backend após corrigir
ssh minha-vps-hostinger "cd /var/www/finup && docker compose -p finup -f docker-compose.prod.yml restart backend"
```

### `finup_frontend_app_prod` não está healthy após deploy

```bash
# Ver logs
ssh minha-vps-hostinger "docker logs finup_frontend_app_prod 2>&1 | tail -30"

# Verificar healthcheck manual
ssh minha-vps-hostinger "docker exec finup_frontend_app_prod curl -sf http://localhost:3000/ | head -5"
```

### `infra_nginx` unhealthy (issue pré-existente)

Este container estava unhealthy antes desta branch. Não é causado pelas mudanças desta branch.
Verificar se o site está acessível mesmo assim:
```bash
curl -sf https://meufinup.com.br/ | head -3
```

### Scripts perf_s1/s2 não encontram .env.local

O `PROJECT_ROOT` nos scripts aponta para 4 níveis acima do arquivo:
`docs/features/performance-prod-fixes/` → `docs/features/` → `docs/` → raiz do projeto.

Verificar:
```bash
python3 -c "from pathlib import Path; p = Path('docs/features/performance-prod-fixes/perf_s1_verify.py').resolve().parent.parent.parent.parent; print(p)"
# Deve imprimir: /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
```

Se não encontrar, passar credenciais via env:
```bash
ADMIN_PASSWORD="senha" FRONTEND_URL="https://meufinup.com.br" \
  python3 docs/features/performance-prod-fixes/perf_s1_verify.py
```

---

## ✅ Checklist final

- [ ] **Fase 0**: `git push origin perf/performance-prod-fixes` feito
- [ ] **Fase 0**: `REDIS_URL` no `.env.prod` da VM verificado
- [ ] **Fase 1**: Deploy `deploy_docker_build_local.sh` concluído sem erros
- [ ] **Fase 2.1**: Todos containers rodando (backend + frontend healthy)
- [ ] **Fase 2.2**: `pip show redis` mostra versão 5.x no backend
- [ ] **Fase 2.3**: `@tanstack/react-query` presente no frontend
- [ ] **Fase 2.6**: VM no commit `c76b9847`
- [ ] **Fase 3**: `perf_s1_verify.py` → todos PASS (P7 Carteira, P7 Investimentos, P8 Transações)
- [ ] **Fase 4**: `perf_s2_verify.py` → todos PASS (P1-A, P1-B, P1-C, P1-D)
- [ ] **Fase 5**: `/plano/cashflow` aparece 1x por carregamento de tela
- [ ] **Fase 6.1**: `redis-cli keys 'onboarding:*'` mostra chave após acesso ao dashboard
- [ ] **Fase 6.2**: Chave deletada após upload
- [ ] **Fase 6.3**: React Query deduplica requests no Plano (2ª visita = 0 requests)
- [ ] **Fase 8**: Merge em main e tag criados
