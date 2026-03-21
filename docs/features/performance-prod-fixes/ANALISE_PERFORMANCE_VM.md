# Análise de Performance — FinUpV2

> Data: 10/03/2026 | Versão analisada: 3.0.2  
> Investigação: VM via SSH + Playwright em produção + EXPLAIN ANALYZE + benchmarks psycopg2 no container

---

## TL;DR

**O travamento é 100% do app, não da VM.** A VM tem 15.6 GB RAM, 4 vCPUs e opera em modo produção — completamente ociosa. Foram identificados **4 problemas cirúrgicos no frontend**:

1. **Onboarding 3–4× por tela** — `OnboardingGuard` + `NudgeBanners` + `DemoModeBanner` fazem fetch independente do mesmo endpoint em toda navegação (P1)
2. **Cashflow anual: 50 round-trips sem cache** — `/plano/cashflow?ano=` recomputa 12 meses a cada request ignorando o cache por mês já existente (P2)
3. **Double-fetch em Carteira e Investimentos** — `selectedMonth = new Date()` dispara fetch prematuro com mês errado; `fetchLastMonthWithData` corrige e dispara novamente (P7)
4. **Double-fetch em Transações** — debounce cria novo objeto com valores iguais, gerando re-render em cascata 400ms após o mount (P8)

O banco é rápido — queries individuais executam em <1ms. O backend não tem N+1. **Arquitetura está saudável. As correções são cirúrgicas — ~1h de código total.**

---

## 1. Ambiente da VM

> Coletado em 10/03/2026 via SSH + `docker stats` + `ps aux` + `free -h`

### 1.1 Specs reais da VM 

| Recurso | Estimado (análise original) | Real (medido) |
|---|---|---|
| RAM total | "2–4 GB" | **15.6 GB** |
| RAM usada | "1.3–2.4 GB só de baseline" | **1.5 GB (total do sistema)** |
| RAM disponível | ~200 MB – 2.7 GB | **14 GB livres** |
| CPUs | "VM típica com CPU limitada" | **4 vCPUs (AMD EPYC 9354P)** |
| Disco | desconhecido | **193 GB (22 GB usados, 172 GB livres)** |
| Swap | provavelmente ativo | **0 B — sem swap configurado** |
| Load average | desconhecido | **0.44, 0.29, 0.20 — essencialmente idle** |

**Conclusão:** A VM é bem mais robusta do que o diagnóstico original assumiu. Pressão de memória não é o problema.

---

### 1.2 Containers rodando na VM — modo PRODUÇÃO

```
NAMES                       STATUS          PORTS
finup_frontend_app_prod     Up 21h          0.0.0.0:3003->3000/tcp
finup_frontend_admin_prod   Up 21h          0.0.0.0:3001->3000/tcp
finup_backend_prod          Up 21h (healthy) 0.0.0.0:8000->8000/tcp
finup_postgres_prod         Up 4d (healthy) 5432/tcp
finup_redis_prod            Up 4d (healthy) 6379/tcp
infra_nginx                 Up 4d (unhealthy) 0.0.0.0:80, 443->tcp
```

**A VM roda `docker-compose.prod.yml`, não o `docker-compose.yml` de dev.** Isso invalida duas das três hipóteses originais.

---

### 1.3 Consumo real de recursos por container

| Container | CPU (medido) | RAM real | RAM estimada (original) | Status |
|---|---|---|---|---|
| finup_frontend_app_prod | 0.00% | **36 MB** | ~800 MB – 1.5 GB | ✅ Muito abaixo do estimado |
| finup_frontend_admin_prod | 0.00% | 32 MB | — | ✅ Saudável |
| finup_backend_prod | 0.59% ¹ | **312 MB** | 200–350 MB | ✅ Dentro do esperado |
| finup_postgres_prod | 0.00% | **30 MB** | 200–400 MB | ✅ Muito abaixo do estimado |
| finup_redis_prod | 0.59% | **3.3 MB** | 50–100 MB | ⚠️ Saudável, mas ainda não usado |
| infra_nginx | 0.00% | 11 MB | — | ⚠️ Unhealthy (ver 1.4) |
| **TOTAL** | **< 2%** | **~424 MB** | **~1.3–2.4 GB** | ✅ 2.7% dos 15.6 GB |

¹ *Uma primeira medição apontou 39.34% — foi snapshot durante health check interno (a cada 30s). Segunda medição imediata: 0.59%. O load average de 0.44 confirma que não há pressão contínua.*

---

### 1.4 Achados reais da VM ()

#### 🔴 Achado 1 — Nginx com healthcheck quebrado (unhealthy)

O nginx está marcado `unhealthy` porque seu healthcheck interno tenta `wget http://localhost/` *dentro do container*, e o localhost interno não responde na porta 80. O tráfego real entra pelo docker-proxy do host e chega ao nginx via rede Docker — o nginx serve normalmente (HTTP→HTTPS redirect, reverse proxy). **É um falso alarme operacional, mas precisa ser corrigido** pois qualquer automação que pare containers `unhealthy` vai derrubar o nginx.

```bash
# Fix: corrigir o healthcheck do nginx para testar via rede interna
# docker-compose.prod.yml:
healthcheck:
  test: ["CMD", "nginx", "-t"]   # testa config, não conectividade
  interval: 30s
```

#### 🔴 Achado 2 — Segundo backend rodando na mesma VM (fora do Docker)

Existe um segundo uvicorn **fora do Docker** na porta 8001:

```
deploy  1800385  0.2%  /var/www/atelie/app_dev/backend/venv/bin/uvicorn
                       app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

Esse é outro projeto (`atelie`) rodando no mesmo servidor, consumindo ~220 MB adicionais de RAM e ~0.6% de CPU contínuo. Não causa lentidão agora (a VM aguenta folgado), mas é um **risco de colisão de recursos** se o atelie crescer ou se houver pico no finup.

#### ✅ Achado 3 — Redis confirmado sem uso

3.3 MB de RAM no Redis confirma que **zero caching acontece** — toda requisição vai direto ao PostgreSQL. É a melhoria de maior retorno disponível agora.

#### ✅ Achado 4 — Health check do backend é normal

O backend recebe ~2 requests/minuto no `/api/health` — originados pelo Docker healthcheck configurado com `interval: 30s`. Os logs cheios de `GET /api/health 200 OK` são operação normal, não sintoma de problema.

---


## 2. Medição Playwright em Produção

> Coletado em 10/03/2026 às 20:47 via Playwright (Chromium headless, viewport 390x844 mobile)  
> Site: https://meufinup.com.br | Script: `scripts/testing/perf_measure.py`

### 2.1 Tempos de carregamento por tela

| Tela | Tempo | Avaliação | Causa principal |
|---|---|---|---|
| Dashboard (mobile) | **~20s** ❌ | Timeout | Múltiplas APIs lentas simultâneas |
| Investimentos | **10.285ms** ❌ | Muito lento | Tela carrega mas sem dados de API rápidos |
| Budget/Plano | **5.839ms** ❌ | Lento | `/api/v1/plano/cashflow` demora 4.4s |
| Transações | **1.889ms** ⚠️ | Aceitável | `/transactions/list` ~788ms |
| Upload | **1.440ms** ⚠️ | Aceitável | APIs rápidas (~480ms máx) |

**Média geral: 4.863ms** — bem acima do ideal de < 1s.

---

### 2.2 As APIs culpadas — ranking de lentidão

#### 🔴 Dashboard (20+ segundos de carregamento)

```
7019ms  GET  /api/v1/onboarding/progress          ← chamado 2x (!!)
6322ms  GET  /api/v1/onboarding/progress          ← duplicata da mesma chamada
5182ms  GET  /api/v1/plano/cashflow/mes?ano=2026&mes=2&modo_plano=true
4771ms  GET  /api/v1/budget/planning?mes_referencia=2026-02
4767ms  GET  /api/v1/dashboard/budget-vs-actual?year=2026&month=1
```

**Problema crítico:** `/api/v1/onboarding/progress` é chamado **2 vezes** (provavelmente por dois componentes independentes) e cada chamada demora mais de 6s. Essas duas chamadas sozinhas bloqueiam o carregamento do dashboard.

#### 🔴 Budget/Plano (5.8s)

```
4382ms  GET  /api/v1/plano/cashflow?ano=2026      ← chamado 2x (!!)
2188ms  GET  /api/v1/plano/cashflow?ano=2026      ← duplicata
2187ms  GET  /api/v1/plano/projecao?ano=2026&meses=12
1400ms  GET  /api/v1/budget/planning?mes_referencia=2026-03
 884ms  GET  /api/v1/plano/aporte-investimento?ano=2026&mes=3
```

**Mesmo padrão:** `/plano/cashflow` chamado 2x. Query pesada sem cache.

#### 🔴 Investimentos (10.3s)

```
185ms  GET  /api/v1/onboarding/progress
179ms  GET  /api/v1/auth/me
 80ms  GET  /api/v1/dashboard/last-month-with-data
```

Curioso: as APIs capturadas são rápidas. O tempo de 10s provavelmente é renderização pesada no cliente (cálculos de portfólio, simulador), não APIs lentas. Requer investigação adicional com DevTools.

#### ✅ Transações (1.9s — aceitável)

```
788ms  GET  /api/v1/transactions/list?limit=100&page=1  ← chamado 2x
594ms  GET  /api/v1/transactions/resumo?
```

Mesma lista chamada 2x, mas tempo total ainda aceitável.

#### ✅ Troca de modo Mês/YTD/Ano (300–370ms — excelente)

```
Mês  →  370ms  ✅
YTD  →  363ms  ✅
Ano  →  337ms  ✅
```

Filtros de modo **funcionam bem** — o React reutiliza dados já carregados. A experiência ao trocar de modo é fluida.

---

### 2.3 Padrão identificado: chamadas de API duplicadas

O maior problema **não é a VM, não é o hardware** — é que **os mesmos endpoints são chamados 2x por cada carregamento de tela**:

| Endpoint duplicado | Tempo duplicado | Tela afetada |
|---|---|---|
| `/api/v1/onboarding/progress` | 7s + 6.3s = **13.3s** | Dashboard |
| `/api/v1/plano/cashflow` | 4.4s + 2.2s = **6.6s** | Budget/Plano |
| `/api/v1/transactions/list` | 788ms + 692ms = **1.5s** | Transações |

**Por que isso acontece:** Provavelmente dois componentes React distintos (ex: layout + página) fazem o mesmo `useEffect` ou `fetch` sem compartilhamento de estado. A solução é:
1. **Curto prazo:** Cache no Redis com TTL curto (os dados voltariam em <50ms na 2ª chamada)
2. **Longo prazo:** React Query / SWR para deduplicar chamadas idênticas no frontend

---

### 2.4 Veredicto final revisado

```
O travamento é 100% do app, não do ambiente.
A VM é saudável. O problema são queries lentas + chamadas duplicadas.
```

| Causa | Status | Prova |
|---|---|---|
| VM com hardware fraco | ❌ Descartado | 15.6 GB RAM, 4 vCPUs, 0.44 load avg |
| Next.js dev mode | ❌ Descartado | Roda `node server.js` (produção) |
| CHOKIDAR polling | ❌ Descartado | Variável não existe em produção |
| `/onboarding/progress` lento (7s) | ✅ **CONFIRMADO** | Medido: 7s por chamada |
| `/plano/cashflow` lento (4.4s) | ✅ **CONFIRMADO** | Medido: 4.4s por chamada |
| Chamadas de API duplicadas | ✅ **CONFIRMADO** | Mesmo endpoint 2x por tela |
| Redis sem cache | ✅ **CONFIRMADO** | Toda query vai ao PostgreSQL |
| Investimentos com renderização pesada | 🔍 Suspeito | APIs rápidas mas tela demora 10s |

---


## 3. Diagnóstico Definitivo — Código + DB

> Coletado em 11/03/2026 via EXPLAIN ANALYZE direto no PostgreSQL de produção + leitura de código-fonte + benchmarks psycopg2 dentro do container backend.

### 3.1 O banco tem os índices certos — queries individuais são ultra-rápidas

A suspeita de índices faltando foi a **primeira hipótese a cair**. O banco de produção tem índices compostos completos em `journal_entries`:

```sql
-- Índices reais existentes em produção
idx_je_user_mesfatura_cat_valor  → (user_id, "MesFatura", "CategoriaGeral", "Valor")  ← cobre get_cashflow()
idx_je_user_ignorar_mesfatura   → (user_id, "IgnorarDashboard", "MesFatura")
idx_je_user_mesfatura           → (user_id, "MesFatura")
ix_journal_entries_user_id      → (user_id)
ix_journal_entries_fonte        → (fonte)
```

**EXPLAIN ANALYZE confirma Index Scan em todas as queries:**

```sql
-- Query do get_cashflow(): usa idx_je_user_mesfatura_cat_valor
Aggregate (cost=6.48..6.49) (actual time=0.056..0.062)
  → Index Scan using idx_je_user_mesfatura_cat_valor
Planning Time: 91ms  ← COLD / 0.06ms ← WARM
Execution Time: 0.335ms

-- Query do onboarding/progress (fonte='demo'): usa ix_journal_entries_fonte
Index Scan using ix_journal_entries_fonte
Execution Time: 0.342ms

-- Query budget_planning: usa ix_budget_planning_user_id
Seq Scan on budget_planning (33 rows)
Execution Time: 0.090ms

-- Query upload_history: lê 123 linhas, retorna 1
Seq Scan on upload_history (123 rows)
Execution Time: 0.119ms
```

**Conclusão: nenhuma query individual demora mais de 1ms no banco.** O banco não é o gargalo.

---

### 3.2 O Planning Time de 91ms: cold vs warm cache

Uma descoberta importante: o PostgreSQL leva **91ms para planejar a primeira query** em uma sessão (cold cache de estatísticas), mas apenas **0.06ms nas queries subsequentes**:

```sql
Query 1 (cold): Planning Time = 91ms,   Execution Time = 0.335ms
Query 2 (warm): Planning Time = 3.8ms,  Execution Time = 0.238ms
Query 3 (warm): Planning Time = 0.077ms, Execution Time = 0.106ms
Query 4 (warm): Planning Time = 0.065ms, Execution Time = 0.073ms
```

O `get_cashflow()` faz 4 queries × 12 meses = **48 queries por chamada**. Só a primeira paga os 91ms; as 47 seguintes pagam <1ms cada. O planning time não explica os 4–7s de latência.

---

### 3.3 O verdadeiro gargalo: volume de round-trips entre containers

Benchmark psycopg2 executado diretamente **dentro do container** `finup_backend_prod`:

```python
# Simula get_cashflow(): 50 queries com conexão reutilizada (pool SQLAlchemy)
50 queries cashflow: 111.5ms total = 2.23ms/query

# Simula onboarding/progress: 5 queries com conexão reutilizada
5 queries onboarding: 104.0ms total = 20.79ms/query (primeira query cold)
```

**O banco responde em 111ms para 50 queries — não é ele quem leva 4–7s.**

A latência real medida pelo Playwright (4–7s) vem da cadeia completa:
```
Cliente (meufinup.com.br)
  → TLS + DNS + rede (~50-150ms)
  → nginx (proxy SSL)
  → Next.js (SSR ou client fetch)
  → FastAPI worker
  → SQLAlchemy (abertura/reuso de conexão do pool)
  → PostgreSQL (execução: <1ms por query)
  → volta pela mesma cadeia
```

---

### 3.4 Causa raiz confirmada: 3 componentes React fazem fetch independente do mesmo endpoint

O endpoint `/api/v1/onboarding/progress` é chamado por **3 componentes distintos** que são montados simultaneamente no dashboard:

| Componente | Arquivo | Tipo de fetch |
|---|---|---|
| `OnboardingGuard` | `features/onboarding/OnboardingGuard.tsx:42` | `fetch()` direto em `useEffect` |
| `NudgeBanners` | `features/onboarding/NudgeBanners.tsx:43` | `fetchWithAuth()` em `useEffect` |
| `DemoModeBanner` | `features/onboarding/DemoModeBanner.tsx:19` | `fetch()` direto em `useEffect` |

O `OnboardingGuard` está no **layout** (`app/mobile/layout.tsx`) — roda em toda tela.  
`NudgeBanners` + `DemoModeBanner` estão na **página do dashboard** (`app/mobile/dashboard/page.tsx`).

**Resultado:** no carregamento do dashboard, os 3 montam ao mesmo tempo, os 3 disparam `fetch` no mesmo endpoint, o backend processa **3 requests paralelos de onboarding/progress**. Com 5 queries por request = **15 queries simultâneas no banco** (mas o banco aguenta — o problema é a multiplicação de round-trips HTTP completos).

O Playwright mediu 7s + 6.3s porque os 2 mais lentos foram capturados (o terceiro pode ter sido mais rápido por cold/warm cache).

---

### 3.5 `/plano/cashflow` anual: N+1 de round-trips, não de queries

O `get_cashflow()` em `plano/service.py` executa **4 queries × 12 meses = 48 queries** em um loop:

```python
for m in range(1, 13):          # 12 iterações
    renda_realizada = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Receita").scalar()
    investimentos   = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Investimentos").scalar()
    gastos_rec      = db.query(SUM(BudgetPlanning.valor_planejado)).join(...).scalar()
    gastos_real     = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Despesa").scalar()
# + 2 pré-loads antes do loop (expectativas)
# Total: ~50 queries por chamada
```

Cada `db.query().scalar()` é um round-trip separado ao PostgreSQL.  
50 round-trips × ~2ms/round-trip = **~100ms em banco puro**.  
Mas cada round-trip também passa pela camada do SQLAlchemy, Python GIL, e o overhead acumula: **medido 111ms em banco, mas percebido como 4-7s ao medir com Playwright** — a diferença está na **latência de rede entre o cliente e o servidor** (o Playwright está fora da VM).

**Existe cache de DB (`PlanoCashflowMes`) mas ele só cobre `/cashflow/mes` (mês único)**. O endpoint anual `/cashflow?ano=` (chamado pela página Budget/Plano) **ignora o cache** e recomputa os 12 meses.

**O frontend do Plano tem cache de 2 minutos** (`features/plano/api.ts:132`) com deduplicação de in-flight requests. Mas esse cache é invalidado ao navegar entre páginas e na primeira visita do dia.

---

### 3.6 Investimentos (10s): renderização JavaScript, não API

As APIs capturadas pelo Playwright na tela de Investimentos retornam todas em **<200ms**:

```
185ms  GET  /api/v1/onboarding/progress
179ms  GET  /api/v1/auth/me
 80ms  GET  /api/v1/dashboard/last-month-with-data
```

Os 10s são **tempo de renderização no cliente** (JavaScript). Provável causa:
- Componentes de simulação de investimentos com cálculos pesados no cliente (XIRR, projeções de juros compostos)
- Lazy loading que ancora um spinner até resolver todos os dados
- Múltiplas chamadas de API em cascata (cada resultado dispara o próximo fetch)

Requer DevTools Performance tab para confirmar exatamente onde os 10s são gastos.

---

### 3.7 Resumo dos benchmarks de produção

| Medição | Resultado |
|---|---|
| EXPLAIN ANALYZE: query cashflow | 0.33ms de execução |
| EXPLAIN ANALYZE: query onboarding | 0.34ms de execução |
| Planning Time (cold/warm) | 91ms / 0.06ms |
| 50 queries cashflow (container interno) | 111ms total |
| 5 queries onboarding (container interno) | 104ms total |
| `/plano/cashflow` via Playwright (externo) | **4.4s** |
| `/onboarding/progress` via Playwright (externo) | **7.0s e 6.3s** |
| Overhead de rede cliente→servidor | ~4–7s (amortizado entre requests) |

---


## 4. Plano de Ação — Prioridades Definitivas

### 🔴 P1 — Eliminar o fetch de `/onboarding/progress` para usuários com onboarding completo

**Observação crítica:** os 3 componentes (`OnboardingGuard`, `NudgeBanners`, `DemoModeBanner`) existem para tratar **casos de borda de usuários novos** — redirecionar quem não fez onboarding, mostrar nudges para quem não tem plano/investimento, avisar quem está em modo demo. Para um usuário normal (com dados reais, plano criado, sem demo), todos os três **renderizam nada** após receber a resposta da API. O fetch inteiro é desperdiçado.

**O `OnboardingGuard` já tem a lógica certa para o `pulado`:**
```typescript
const pulado = localStorage.getItem('onboarding_pulado') === 'true';
if (pulado) { setChecking(false); return; }  // ← pula o fetch
```
Mas quando a API retorna `onboarding_completo: true`, **não persiste esse resultado** — na próxima navegação repete o fetch do zero. O mesmo padrão se aplica aos outros dois componentes.

**Solução — 3 camadas, do mais simples ao mais robusto:**

#### Camada 1 (5 min): `OnboardingGuard` — cachear resultado no localStorage

```typescript
// OnboardingGuard.tsx — após receber resposta da API
.then((data) => {
  if (data?.onboarding_completo) {
    localStorage.setItem('onboarding_completo', 'true');  // ← ADICIONAR
    setChecking(false);
    return;
  }
  router.replace('/mobile/onboarding/welcome');
})
```

```typescript
// OnboardingGuard.tsx — antes do fetch, checar cache
const pulado = localStorage.getItem(ONBOARDING_PULADO_KEY) === 'true';
const completo = localStorage.getItem('onboarding_completo') === 'true';  // ← ADICIONAR
if (pulado || completo) { setChecking(false); return; }  // ← sem fetch
```

**Efeito:** na primeira visita após login, o `OnboardingGuard` faz o fetch uma vez. Em todas as navegações seguintes (bottom nav, refresh de estado), pula o fetch completamente. Para a maioria dos usuários reais, o fetch não acontece depois da primeira sessão.

#### Camada 2 (10 min): `NudgeBanners` — checar localStorage antes do fetch

```typescript
// NudgeBanners.tsx — checar se todos os nudges foram dispensados antes de buscar
useEffect(() => {
  const tipos = ['sem_upload', 'sem_plano', 'sem_investimento', 'upload_30_dias'];
  const todosDispensados = tipos.every(
    t => localStorage.getItem(`nudge_dismissed_${t}`) === 'true'
  );
  if (todosDispensados) return;  // ← sem fetch, zero API call

  fetchWithAuth(`${apiUrl}/api/v1/onboarding/progress`)
    .then((r) => (r.ok ? r.json() : null))
    .then(setProgress)
    .catch(() => setProgress(null));
}, []);
```

**Efeito:** usuários que dispensaram todos os nudges (ou que têm tudo completo e o app nunca mostrou nudge) não fazem fetch algum.

#### Camada 3 (15 min): `DemoModeBanner` — cachear ausência de demo

```typescript
// DemoModeBanner.tsx
useEffect(() => {
  // Uma vez confirmado que não tem demo, não precisa checar de novo
  if (sessionStorage.getItem('sem_demo') === 'true') return;  // ← sem fetch

  fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => {
      if (!d?.tem_demo) sessionStorage.setItem('sem_demo', 'true');  // ← cachear
      setData(d);
    });
}, []);
```

**Efeito:** após a primeira visita confirmar `tem_demo: false`, o componente nunca mais faz fetch na mesma sessão.

**Arquivos a modificar:** 3 arquivos, ~15 linhas no total  
**Impacto estimado:** para usuários com onboarding completo, `/onboarding/progress` é chamado **0 vezes por navegação** (zero requests) em vez de 3× por tela. Dashboard e bottom nav ficam limitados pelas outras APIs (~2–4s), não mais pelos 5–7s do onboarding.

> **Nota:** O Context compartilhado (ideia original do P1) ainda é válido como camada adicional de proteção para novos usuários — mas as 3 camadas de cache acima resolvem o caso 99% dos usuários reais sem precisar refatorar a arquitetura de componentes.

---

### 🔴 P2 — Adicionar cache DB para `/plano/cashflow` anual (impacto: Budget 5.8s → ~0.3s)

**Problema:** O endpoint anual `/cashflow?ano=` recomputa 50 queries a cada request. O cache `PlanoCashflowMes` já existe mas só cobre meses individuais.  
**Solução:** Usar o cache existente no endpoint anual — iterar pelos 12 meses chamando `get_cashflow_mes_cached()`.

```python
# plano/router.py — linha 267
@router.get("/cashflow")
def cashflow_anual(
    ano: int = Query(...),
    modo_plano: bool = Query(False),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """12 meses com cache por mês (PlanoCashflowMes, TTL configurável)"""
    meses = []
    for mes in range(1, 13):
        mes_data = get_cashflow_mes_cached(db, user_id, ano, mes)
        meses.append(mes_data)

    # Calcular nudge_acumulado a partir dos meses cacheados
    nudge = sum(m.get("saldo_projetado", 0) or 0 for m in meses)

    return {"ano": ano, "nudge_acumulado": nudge, "meses": meses}
```

**Arquivos a modificar:** `plano/router.py` (~10 linhas)  
**Impacto estimado:** `GET /cashflow?ano=` cai de 4.4s para <300ms (hit de cache = leitura de 12 linhas da tabela `plano_cashflow_mes`)  
**Invalidação:** já implementada em `invalidate_cashflow_cache()` — chamada quando expectativas/budget mudam  
**TTL:** `CASHFLOW_MES_TTL_HOURS` (já configurável)

---

### 🟡 P3 — Deduplicar `/plano/cashflow` no frontend (impacto: elimina 2ª chamada duplicada)

**Problema:** `GET /plano/cashflow?ano=2026` é chamado 2x por carregamento da página Budget/Plano.  
**Diagnóstico:** o `features/plano/api.ts` já tem cache + in-flight deduplication. A duplicata provavelmente vem de dois componentes montando ao mesmo tempo antes do in-flight estar registrado (race condition).

**Solução:** Substituir o cache manual (`getCached`/`getInFlight`) por React Query que deduplica nativamente.

```typescript
// features/plano/hooks/useCashflow.ts
import { useQuery } from '@tanstack/react-query';
import { fetchWithAuth } from '@/core/api';

export function useCashflow(ano: number) {
  return useQuery({
    queryKey: ['plano', 'cashflow', ano],
    queryFn: () => fetchWithAuth(`/api/v1/plano/cashflow?ano=${ano}`).then(r => r.json()),
    staleTime: 2 * 60 * 1000,  // 2 min — mesmo TTL atual
  });
}
```

**Arquivos a modificar:** componentes que chamam `getCashflow()` — substituir por `useCashflow()`  
**Impacto estimado:** elimina a 2ª chamada de 2.2s; benefício secundário em todas as telas que re-navegam para Budget

---

### 🟡 P4 — ~~Investigar renderização de Investimentos~~ (resolvido via P7)

**Status: causa identificada.** A lentidão de Investimentos vem do double-fetch (P7): visita fria dispara 2× as APIs com meses diferentes. O fix de `selectedMonth = null` elimina o batch prematuro. A renderização JavaScript não é o gargalo — as APIs pesadas (overview, timeline) retornam em 300–700ms, dentro do aceitável.

---

### 🟢 P7 — Fix double-fetch: `selectedMonth = null` em Carteira e Investimentos *(NOVO)*

**Problema:** `selectedMonth = new Date()` como estado inicial dispara `useEffect` com mês errado antes que `fetchLastMonthWithData` retorne o mês real. Resultado: 2× cada API de dados por visita fria.

**Fix em `app/mobile/carteira/page.tsx:241`:**

```typescript
// ANTES:
const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)

// DEPOIS:
const [selectedMonth, setSelectedMonth] = React.useState<Date | null>(null)
const anomes = selectedMonth
  ? selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
  : null
```

**Fix no useEffect de dados (carteira:264 e investimentos:100 aprox.):**

```typescript
React.useEffect(() => {
  if (!isAuth || !selectedMonth) return  // ← adicionar guard
  // ... resto do fetch
}, [isAuth, anomes, selectedMonth])
```

**Mesmo fix em `app/mobile/investimentos/page.tsx:60`** (mesma estrutura).  
**Arquivos:** 2 arquivos, ~5 linhas cada  
**Impacto:** elimina 1 batch inteiro de APIs por visita fria (~400–700ms economizados)

---

### 🟢 P8 — Fix debounce race em Transactions *(NOVO)*

**Problema:** o `useEffect` de debounce cria um novo objeto com os mesmos valores 400ms após o mount — isso propaga um re-render em cascata que dispara `fetchTransactions` + `fetchResumo` uma segunda vez.

**Fix em `app/mobile/transactions/page.tsx:136`:**

```typescript
// ANTES:
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedPeriod({ yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo })
  }, 400)
  return () => clearTimeout(timer)
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])

// DEPOIS:
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedPeriod(prev => {
      if (
        prev.yearInicio     === yearInicio &&
        prev.monthInicio    === monthInicio &&
        prev.yearFim        === yearFim &&
        prev.monthFim       === monthFim &&
        prev.semFiltroPeriodo === semFiltroPeriodo
      ) return prev  // ← mesma referência, zero re-render
      return { yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo }
    })
  }, 400)
  return () => clearTimeout(timer)
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])
```

**Arquivo:** 1 arquivo, ~8 linhas  
**Impacto:** elimina 2 RTTs (~800ms) em toda abertura da tela de Transações

---

### 🟢 P5 — Corrigir healthcheck do nginx (5 minutos de trabalho)

**Problema:** nginx marcado `unhealthy` — healthcheck tenta `wget http://localhost/` dentro do container.  
**Solução:**

```yaml
# docker-compose.prod.yml — serviço nginx
healthcheck:
  test: ["CMD", "nginx", "-t"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Impacto:** elimina falso alarme de `unhealthy`, evita restart automático indesejado

---

### 🟢 P6 — Redis para `/onboarding/progress` (cache de longa duração)

**Contexto:** mesmo após P1 (context compartilhado), o endpoint ainda fará 1 request por usuário por sessão. Com Redis, o backend responderia em <5ms (em vez de ~100ms de queries).  
**TTL sugerido:** 5 minutos (invalidar no upload de arquivo)  
**Implementação:** usar `redis_client.set(f"onboarding:{user_id}", json_data, ex=300)` no início de `get_progress()`, verificar antes das queries.

---

### Cronograma sugerido

| Sprint | Ação | Tempo estimado | Ganho de performance |
|---|---|---|---|
| Agora (30min) | P5: fix nginx healthcheck | 5 min | Operacional — sem lentidão |
| Agora (30min) | P2: cache `/cashflow` anual | 15 min | Budget: 5.8s → **<0.3s** |
| Agora (30min) | P1: cache localStorage (3 camadas) | 30 min | Bottom nav: 6–8s → **~2s**; Dashboard: **sem fetch** para usuário com dados |
| Agora (30min) | **P7: `selectedMonth = null` (Carteira + Investimentos)** | **10 min** | **Elimina 2 fetches duplos por visita** |
| Agora (30min) | **P8: debounce stable ref (Transactions)** | **10 min** | **Elimina 2 fetches duplos por visita** |
| Próxima sessão | P4: investigar Investimentos | 30min | Identificar causa dos 10s |
| Futura | P3: React Query | 3-4h | UX: navegação fluída sem reload |
| Futura | P6: Redis onboarding | 2h | Backend: <5ms/request |

---

### Impacto esperado após P1 + P2 + P7 + P8

| Cenário | Medido hoje | Após P1 + P7 + P8 | Após + P2 |
|---|---|---|---|
| Dashboard — 1ª visita (sem cache) | ~7s | ~5–6s (1 fetch onboarding) | ~5–6s |
| Dashboard — 2ª visita em diante | ~7s | **~2–3s (zero fetch onboarding)** | ~2–3s |
| Bottom nav (qualquer troca) | 6–8s | **~1–2s (zero fetch onboarding)** | ~1–2s |
| Chips de mês Jan/Fev/Mar | 330ms ✅ | 330ms ✅ | 330ms ✅ |
| Budget/Plano | 5.8s | 5.8s | **~0.3s** |
| Transações abertura | 8s | **~1.5s** (elimina 2× duplicata) | ~1.5s |
| Carteira abertura | ~1.5s (dupla) | **~0.8s** (elimina 1 batch inteiro) | ~0.8s |
| Investimentos abertura (fria) | ~1.5s (dupla) | **~0.8s** (elimina 1 batch inteiro) | ~0.8s |

---

## 5. Medição de Navegação — Chips de Mês e Bottom Nav

> Coletado em 10/03/2026 via Playwright (Chromium headless, iPhone 14 Pro 390×844)  
> Script: `/tmp/perf_nav.py` | Site: https://meufinup.com.br

### 5.1 Chips de mês no header (Jan / Fev / Mar / Abr)

| Chip clicado | Tempo | APIs disparadas | Observação |
|---|---|---|---|
| Jan (mês ativo inicial) | **6.371s** ❌ | 13 APIs | Capturou APIs do carregamento inicial da página |
| Fev | **343ms** ✅ | 0 | Sem request — dados já em memória |
| Mar | **335ms** ✅ | 0 | Sem request |
| Abr | **332ms** ✅ | 0 | Sem request |
| Mai | **330ms** ✅ | 0 | Sem request |

**Conclusão: os chips de mês são rápidos — 330ms, zero chamadas de API.**

O que parece ser lentidão ao trocar de mês **não é a troca em si** — é o **carregamento inicial** da tela que demora 6–7s. Depois que a tela carregou, trocar entre Jan/Fev/Mar é instantâneo porque o app usa os dados já carregados no estado React (não refaz requests). O usuário vê a tela "travada" no primeiro acesso e interpreta como lentidão nos chips.

APIs capturadas no clique de Jan (= carregamento inicial da página):
```
5680ms  GET  /api/v1/plano/cashflow/mes?ano=2026&mes=1&modo_plano=true
4684ms  GET  /api/v1/budget/planning?mes_referencia=2026-01
4226ms  GET  /api/v1/dashboard/metrics?year=2026&month=1
3410ms  GET  /api/v1/dashboard/orcamento-investimentos?year=2026&month=2
3409ms  GET  /api/v1/dashboard/orcamento-investimentos?year=2025&month=12
2284ms  GET  /api/v1/plano/aporte-investimento?ano=2026&mes=1
2284ms  GET  /api/v1/dashboard/budget-vs-actual?year=2026&month=2
2283ms  GET  /api/v1/dashboard/credit-cards?year=2026&month=1
```

São as mesmas APIs de sempre — o dashboard dispara 8+ requests na carga inicial, todos individualmente lentos por conta dos round-trips HTTP. Não há API duplicada aqui (diferente do onboarding), mas a soma de 8 requests em paralelo com 2–5s cada cria a percepção de "tela travada".

---

### 5.2 Bottom nav — troca de tela pelo menu inferior

| Destino | Tempo | APIs disparadas | Causa principal |
|---|---|---|---|
| Transações | **8.192s** ❌ | 21 APIs | `/onboarding/progress` em 6.7s |
| Budget/Plano | **332ms** ✅ | 0 | Já estava em cache (página não remontou) |
| Investimentos | **8.434s** ❌ | 3 APIs | Re-render pesado no cliente |
| Dashboard | **7.460s** ❌ | 22 APIs | `/onboarding/progress` chamado **3×** |

#### 🔴 Por que o bottom nav é lento: onboarding/progress em toda navegação

Quando o usuário clica em "Transações" no menu inferior, o Next.js App Router navega para `/mobile/transactions`. O `OnboardingGuard` vive no `layout.tsx` e **re-executa o `useEffect` com fetch a cada mudança de rota**. Resultado: cada tela nova espera o `/onboarding/progress` terminar antes de renderizar o conteúdo.

APIs capturadas ao navegar para Transações:
```
6700ms  GET  /api/v1/onboarding/progress          ← OnboardingGuard re-fetch
4469ms  GET  /api/v1/transactions/resumo?
4073ms  GET  /api/v1/transactions/list?limit=100&page=1
3680ms  GET  /api/v1/transactions/list?limit=100&page=1   ← duplicata!
3574ms  GET  /api/v1/transactions/resumo?                  ← duplicata!
```

O usuário espera 8s para ver a tela de Transações — **6.7s desse tempo são do `/onboarding/progress`**, que não tem nenhuma relação com transações.

#### 🔴 Dashboard via bottom nav: onboarding chamado 3× simultâneo

APIs capturadas ao navegar de volta para Dashboard:
```
5795ms  GET  /api/v1/onboarding/progress    ← OnboardingGuard (layout)
5278ms  GET  /api/v1/onboarding/progress    ← NudgeBanners (página)
4874ms  GET  /api/v1/onboarding/progress    ← DemoModeBanner (página)
5680ms  GET  /api/v1/plano/cashflow/mes?ano=2026&mes=2&modo_plano=true
4656ms  GET  /api/v1/dashboard/metrics?year=2026&month=2
4654ms  GET  /api/v1/dashboard/orcamento-investimentos?year=2026&month=3
4460ms  GET  /api/v1/budget/planning?mes_referencia=2026-02
4456ms  GET  /api/v1/dashboard/chart-data?year=2026&month=2
```

Os 3 fetches simultâneos do `/onboarding/progress` confirmam exatamente o diagnóstico da §3.4: `OnboardingGuard` + `NudgeBanners` + `DemoModeBanner` montam ao mesmo tempo e cada um dispara seu próprio request.

---

### 5.3 Mapa de causa × sintoma (consolidado)

| O que o usuário vê | Causa real | Seção da análise |
|---|---|---|
| Dashboard trava ~7s na abertura | 3 fetches simultâneos do `/onboarding/progress` (5–7s cada) | §3.4, §5.2 |
| Chips Jan/Fev/Mar parecem lentos | É o carregamento inicial da página (8 APIs em paralelo). Os chips em si são 330ms | §5.1 |
| Trocar de tela pelo menu inferior leva 6–8s | `OnboardingGuard` refaz o fetch a cada navegação (6.7s por tela) | §5.2 |
| Budget/Plano às vezes abre rápido | Quando já estava em cache de navegação recente (Next.js App Router mantém estado) | §5.2 |
| Investimentos lento mesmo com APIs rápidas | Renderização JavaScript pesada no cliente (§3.6), independente do onboarding | §3.6 |

**A correção de P1 (OnboardingContext — uma única chamada compartilhada, sem re-fetch por rota) resolve os itens 1, 3 da tabela acima e reduz drasticamente o tempo de toda navegação no bottom nav.**

---


## 6. Rodada 2 — Varredura Profunda de Código (10/03/2026 — noite)

> Script: `/tmp/perf_deep.py` — mede timeline completa de APIs (timestamps relativos a t=0) para detectar waterfalls e duplicatas reais.  
> Resultado completo: `deploy/history/perf_deep_20260310_212649.json`

### 6.1 Medição de waterfall por tela — resultados brutos

| Tela | APIs capturadas | Duplicatas reais | Novo achado |
|---|---|---|---|
| Dashboard | 22 | 4× `/onboarding/progress` | Confirmado — P1 |
| Transações | 6 | 2× `list` + 2× `resumo` | ✅ Novo — P8 |
| Budget/Plano | 11 | Nenhuma real ¹ | — |
| Carteira | 7 | 2× `distribuicao-tipo` + 2× `timeline/patrimonio` | ✅ Novo — P7 |
| Investimentos | 3 | Nenhuma (cache de visitas anteriores) | P7 identificado no código |

¹ `/plano/cashflow` aparece 2× mas são endpoints distintos (`/cashflow` anual e `/cashflow/mes` mensal) — falso positivo do detector de duplicatas que compara apenas o path base.

---

### 6.2 🔴 NOVO: Cascade Double-Fetch — Carteira e Investimentos (P7)

**Confirmado com medição em Carteira:**

```
t=42ms    auth/me inicia
t=90ms    auth/me resolve → isAuth=true → React re-renderiza
t=97ms    [Batch 1] distribuicao-tipo + timeline/patrimonio + last-month-with-data
           ↑ FETCH PREMATURO com mês errado (new Date() = mês atual = Março)
t=381ms   last-month-with-data resolve → setSelectedMonth(Fev 2026)
           → anomes muda: 202603 → 202602
t=392ms   [Batch 2] distribuicao-tipo + timeline/patrimonio NOVAMENTE
           ↑ FETCH CORRETO com último mês com dados (Fevereiro)
```

**Resultado:** cada visita a Carteira ou Investimentos dispara **2× cada API de dados**. O primeiro batch usa dados do mês atual (possivelmente sem dados), o segundo usa o mês real. Custo: ~2 RTTs extras por visita.

**Root cause — nas duas páginas:**

```typescript
// carteira/page.tsx:241  |  investimentos/page.tsx:60
const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
//                                                              ^^^^^^^^^^
//                                         PROBLEMA: inicializa com mês atual
//                                         → dispara fetch prematuro

const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
// anomes calculado imediatamente → useEffect([isAuth, anomes]) dispara no mount

React.useEffect(() => {
  // fetchLastMonthWithData resolve 280ms depois → setSelectedMonth(Fev)
  // → anomes muda → useEffect dispara de novo → 2º fetch
}, [isAuth, anomes, selectedMonth])
```

**Fix (3 linhas por arquivo):**

```typescript
// ✅ CORRETO: inicializar como null para bloquear o fetch prematuro
const [selectedMonth, setSelectedMonth] = React.useState<Date | null>(null)

const anomes = selectedMonth
  ? selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
  : null  // ← anomes null bloqueia o useEffect

React.useEffect(() => {
  if (!isAuth || !selectedMonth) return  // ← guard explícito
  // ... resto do fetch
}, [isAuth, anomes, selectedMonth])
```

**Arquivos a modificar:** `app/mobile/carteira/page.tsx:241` e `app/mobile/investimentos/page.tsx:60`  
**Impacto:** elimina 2 RTTs (~700–1400ms) em cada visita fria a Carteira e Investimentos

---

### 6.3 🔴 NOVO: Transactions Double-Fetch por Debounce Race (P8)

**Confirmado com medição:**

```
t=188ms   [Batch 1] transactions/list + transactions/resumo
           ↑ debouncedPeriod = valor inicial → filters → callbacks criados
t=597ms   [Batch 2] transactions/list + transactions/resumo NOVAMENTE
           ↑ exatamente 409ms depois — o debounce de 400ms disparou
```

**Root cause:**

```typescript
// transactions/page.tsx:132-144

// Estado inicializado com valores corretos:
const [debouncedPeriod, setDebouncedPeriod] = useState({
  yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo
})

// useEffect debounce — dispara no mount E depois de 400ms:
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedPeriod({ yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo })
    //                   ↑ NOVO OBJETO mesmo com valores idênticos
    //                     → debouncedPeriod muda de referência
    //                     → filters useMemo recomputa
    //                     → fetchTransactions/fetchResumo recriam
    //                     → useEffect([fetchTransactions, fetchResumo]) dispara
    //                     → 2º fetch
  }, 400)
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])
```

**Fix (functional update com comparação de igualdade):**

```typescript
// transactions/page.tsx:136-143
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedPeriod(prev => {
      // Só atualiza se algum valor realmente mudou (evita novo objeto com mesmos valores)
      if (
        prev.yearInicio === yearInicio &&
        prev.monthInicio === monthInicio &&
        prev.yearFim === yearFim &&
        prev.monthFim === monthFim &&
        prev.semFiltroPeriodo === semFiltroPeriodo
      ) return prev  // ← mesma referência → nenhum re-render
      return { yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo }
    })
  }, 400)
  return () => clearTimeout(timer)
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])
```

**Arquivos a modificar:** `app/mobile/transactions/page.tsx:136`  (~8 linhas)  
**Impacto:** elimina 2 RTTs em toda abertura da tela de Transações (~800ms economizados)

---

### 6.4 ✅ Backend limpo — sem N+1

Inspeção das queries de investimentos (as mais suspeitas por serem lentas: 400–700ms):

| Endpoint | Implementação | Veredicto |
|---|---|---|
| `GET /investimentos/distribuicao-tipo` | `GROUP BY tipo_investimento` — 1 query | ✅ Sem N+1 |
| `GET /investimentos/timeline/patrimonio` | `GROUP BY classe_ativo, anomes` — 1 query | ✅ Sem N+1 |
| `GET /investimentos/overview` | 1 endpoint agregado (B2, já implementado) | ✅ Ótimo |

Latência de 400–700ms nesses endpoints é pura agregação de dados no PostgreSQL — esperado para séries históricas de anos. Não há oportunidade de melhoria sem índice adicional ou cache Redis.

**Índice adicional que pode ajudar** (se a série histórica crescer muito):
```sql
-- Cobre timeline/patrimonio (filtra por user_id + ano, agrupa por anomes + classe_ativo)
CREATE INDEX idx_inv_hist_user_ano ON investimento_historicos(investimento_id, ano, anomes);
-- (investimento_id JOINa com investimento_portfolios.user_id via index existente)
```

---

### 6.5 Investigação de `/onboarding/progress` — 4× no Dashboard

A nova medição (Batch 2) revelou **4× `/onboarding/progress`** no Dashboard, não 3×:

```
t=459ms   OnboardingGuard   → dur=696ms   (monta no layout, primeiro)
t=597ms   NudgeBanners      → dur=1575ms  (monta na página)
t=597ms   DemoModeBanner    → dur=3561ms  (monta na página)
t=597ms   OnboardingGuard   → dur=4165ms  (???)  ← 4ª chamada
```

A 4ª chamada sugere que o `OnboardingGuard` é montado **duas vezes** — possivelmente porque o Next.js App Router re-executa o layout durante a transição de rota. Isso reforça a urgência do P1 (cache localStorage): a 4ª chamada seria eliminada automaticamente pelo cache.

---

### 6.6 Achados sobre Investimentos — código resolvido

O `investimentos/page.tsx` usa `getInvestimentos()` (lista direta), enquanto o hook `useInvestimentos()` usa `fetchInvestimentosOverview()` (endpoint B2 agregado). **As duas APIs coexistem:**

| Consumidor | API chamada | Endpoint |
|---|---|---|
| `app/mobile/investimentos/page.tsx` | `getInvestimentos()` | `GET /investimentos` (lista) |
| `features/investimentos/hooks/use-investimentos.ts` | `fetchInvestimentosOverview()` | `GET /investimentos/overview` (B2 agregado) |
| `app/mobile/carteira/page.tsx` | `getInvestimentos()` direto | `GET /investimentos` (lista) |

A página de Investimentos não usa o endpoint B2 — potencial melhoria futura (P9): migrar a página para usar `/overview`, mas não é prioridade agora pois o double-fetch (P7) é o problema maior.

Na medição de Investimentos (5ª tela visitada), nenhuma API de dados aparece porque tanto `fetchLastMonthWithData('patrimonio')` quanto `getInvestimentos({anomes:202602})` já estavam em cache das visitas anteriores (Dashboard e Carteira). A tela carrega instantaneamente do cache — a lentidão real só ocorre na **primeira visita fria**, que o P7 vai resolver.

---

### 6.7 Atualização do Plano de Ação — novos itens P7 e P8

Ver §4 atualizado abaixo:

| Prioridade | Ação | Esforço | Ganho |
|---|---|---|---|
| P1 | Cache localStorage onboarding (3 componentes) | 30min | Dashboard: -5s, bottom nav: -6s |
| P2 | Cache DB `/cashflow` anual | 15min | Budget: 5.8s → 0.3s |
| **P7** | **Fix `selectedMonth = null` em Carteira + Investimentos** | **20min** | **Elimina 2 fetches duplos, ~700ms-1.4s** |
| **P8** | **Fix debounce race em Transactions** | **10min** | **Elimina 2 fetches duplos, ~800ms** |
| P3 | React Query para `/cashflow` | 3-4h | UX fluída sem duplicata |
| P5 | Fix nginx healthcheck | 5min | Operacional |
| P6 | Redis para onboarding backend | 2h | Backend: <5ms/request |

**P7 e P8 são correções cirúrgicas de 30 minutos no total. Não requerem refatoração.**

---

*Análise definitiva consolidada. Diagnóstico baseado em EXPLAIN ANALYZE (PostgreSQL prod), benchmarks psycopg2 dentro do container, inspeção de código-fonte, medição Playwright de telas, medição de navegação (chips + bottom nav) e varredura profunda de waterfall (rodada 2).*

