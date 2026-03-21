# Sprint 3 — Backend Cache Cashflow: `/plano/cashflow` Anual em 0.3s

> **Esforço total:** ~15 minutos  
> **Item:** P2  
> **Pré-requisito:** Tabela `plano_cashflow_mes` deve existir (já existe em produção)  
> **Impacto:** Budget/Plano: 5.8s → **~0.3s**

---

## 🔗 Rastreamento de Erros — Do Sintoma ao Fix

### P2 — Endpoint Anual `/plano/cashflow` com 50 Queries em Loop

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Budget/Plano demora **5.8s** para carregar. O gráfico de cashflow anual é o último elemento a aparecer. |
| **Medido com `perf_measure.py`** | `Budget/Plano: 5800ms` — API call mais lenta identificada: `GET /plano/cashflow?ano=2026 → 4400ms`. |
| **Arquivo exato** | `app_dev/backend/app/domains/plano/service.py` — função `get_cashflow()` |
| **Causa raiz** | Loop de 12 iterações com 4 queries por mês = **48 queries** + 2 pré-loop = **50 queries por request**. O banco é rápido (50 queries em 111ms), mas o overhead acumulado de **50 round-trips Python→PostgreSQL** gera 4.4s percebidos. |
| **O cache por mês já existe** | `get_cashflow_mes_cached()` e a tabela `plano_cashflow_mes` já existem e funcionam para o endpoint **mensal**. O endpoint **anual** os ignora completamente — chama `get_cashflow()` diretamente. |
| **O fix** | Reescrever o endpoint anual para chamar `get_cashflow_mes_cached(db, user_id, ano, mes)` em loop. Cache hit = 1 query por mês → 12 meses = 12 queries. Redução: 50 → 12 queries. |

### Verificar a causa antes de implementar

```bash
# Confirmar: endpoint anual usa get_cashflow() (sem cache)
grep -n "get_cashflow\b\|get_cashflow_mes_cached" \
  app_dev/backend/app/domains/plano/router.py
# Deve mostrar: get_cashflow(db, ...) no endpoint /cashflow (sem cached)
# E: get_cashflow_mes_cached no endpoint /cashflow/mes

# Confirmar: tabela de cache existe em produção
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM plano_cashflow_mes;"
# → deve ter linhas (cache já populado para usuários ativos)

# Confirmar: função get_cashflow_mes_cached existe e importa
docker exec finup_backend_dev python3 -c \
  "from app.domains.plano.service import get_cashflow_mes_cached; print('✅', get_cashflow_mes_cached)"
```

---

## Contexto — Por Que o Endpoint Anual é Lento

### O endpoint atual

`GET /api/v1/plano/cashflow?ano=2026` é chamado pela página Budget/Plano para renderizar o gráfico de cashflow anual dos 12 meses. Em produção, demora **4.4s** por chamada.

### A causa: 50 queries em loop

Em `app_dev/backend/app/domains/plano/service.py`, a função `get_cashflow()` executa um loop de 12 iterações, com **4 queries por mês**:

```python
for m in range(1, 13):          # 12 iterações
    renda_realizada  = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Receita").scalar()
    investimentos    = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Investimentos").scalar()
    gastos_rec       = db.query(SUM(BudgetPlanning.valor_planejado)).join(...).scalar()
    gastos_real      = db.query(SUM(Valor)).filter(MesFatura=m, CategoriaGeral="Despesa").scalar()

# + 2 queries pré-loop para expectativas
# Total: 50 queries por chamada ao endpoint anual
```

**Benchmark confirmado:** 50 queries executadas em 111ms no banco (rápido). O overhead acumulado de round-trips Python→PostgreSQL×50 + rede cliente→servidor = **4.4s percebidos**.

### O cache por mês já existe (e funciona)

O endpoint mensal `GET /plano/cashflow/mes?ano=&mes=` usa `get_cashflow_mes_cached()`, que:
1. Lê da tabela `plano_cashflow_mes` se o registro existir (cache hit = 1 query)
2. Computa e salva na tabela se não existir (cache miss = 50 queries, mas só na primeira vez)
3. É invalidado por `invalidate_cashflow_cache(db, user_id, ano, mes)` quando há mudanças

**O problema:** o endpoint **anual** ignora completamente este cache — ele chama `get_cashflow()` diretamente, recomputando 50 queries a cada request.

---

## O Fix

**Arquivo:** `app_dev/backend/app/domains/plano/router.py`

Alterar o endpoint anual para iterar pelos 12 meses chamando `get_cashflow_mes_cached()` em vez de `get_cashflow()`.

### Passo 1 — Localizar o endpoint anual

Buscar no `plano/router.py` pelo endpoint `GET /cashflow` (sem o `/mes`):

```python
@router.get("/cashflow")
def cashflow_anual(
    ano: int = Query(...),
    modo_plano: bool = Query(False),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_cashflow(db, user_id, ano, modo_plano)
    #       ^^^^^^^^^^^^^ chama a função pesada (50 queries)
```

### Passo 2 — Verificar import de `get_cashflow_mes_cached`

No topo do `router.py`, verificar se `get_cashflow_mes_cached` já está importado. Se não:

```python
# Adicionar ao bloco de imports de plano/service.py:
from app.domains.plano.service import (
    get_cashflow,
    get_cashflow_mes_cached,   # ← adicionar se não existir
    invalidate_cashflow_cache,
    # ... outros imports existentes
)
```

### Passo 3 — Reescrever o endpoint anual

```python
# ANTES:
@router.get("/cashflow")
def cashflow_anual(
    ano: int = Query(...),
    modo_plano: bool = Query(False),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_cashflow(db, user_id, ano, modo_plano)

# DEPOIS:
@router.get("/cashflow")
def cashflow_anual(
    ano: int = Query(...),
    modo_plano: bool = Query(False),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Retorna cashflow de todos os 12 meses do ano.
    Usa get_cashflow_mes_cached() por mês para aproveitar a tabela
    plano_cashflow_mes como cache (hit = 1 query por mês em vez de 50).
    """
    meses = []
    for mes in range(1, 13):
        mes_data = get_cashflow_mes_cached(db, user_id, ano, mes)
        meses.append(mes_data)

    # Calcular nudge_acumulado somando saldo_projetado dos 12 meses
    # (mesma lógica que get_cashflow() fazia ao final)
    nudge_acumulado = sum(
        (m.get("saldo_projetado") or 0)
        for m in meses
        if isinstance(m, dict)
    )

    return {
        "ano": ano,
        "nudge_acumulado": nudge_acumulado,
        "meses": meses,
    }
```

### Passo 4 — Verificar shape do response

O frontend espera um shape específico de `GET /cashflow?ano=`. Verificar em `features/plano/api.ts` ou similar qual interface é esperada:

```typescript
// Localizar em: features/plano/api.ts ou features/plano/types/
interface CashflowAnual {
  ano: number
  nudge_acumulado: number
  meses: CashflowMes[]
}

interface CashflowMes {
  mes: number
  // ... campos específicos do mês
}
```

O response do novo endpoint retorna exatamente o mesmo shape: `{ ano, nudge_acumulado, meses: [...12 objetos] }`. Cada elemento de `meses` é o retorno de `get_cashflow_mes_cached()`, que deve ter o mesmo shape que `get_cashflow()` retornava por mês.

> **Validação crítica:** comparar o shape do objeto único de mês entre `get_cashflow()` e `get_cashflow_mes_cached()`. Se houver diferença de campos, o frontend pode quebrar silenciosamente (dados ausentes, não erro visível).

---

## Comportamento do Cache

### Cache miss (primeira visita do mês no ano)

```
request: GET /cashflow?ano=2026
→ loop 12 meses:
  - mes=1:  plano_cashflow_mes não tem registro → computa (4 queries) → salva
  - mes=2:  plano_cashflow_mes não tem registro → computa (4 queries) → salva
  - ...
  - mes=12: plano_cashflow_mes não tem registro → computa (4 queries) → salva
→ 48 queries total (igual ao antes)
→ resultado salvo em cache para próximas requests
```

### Cache hit (segunda visita em diante)

```
request: GET /cashflow?ano=2026
→ loop 12 meses:
  - mes=1:  plano_cashflow_mes tem registro → retorna direto (1 query)
  - mes=2:  plano_cashflow_mes tem registro → retorna direto (1 query)
  - ...
  - mes=12: plano_cashflow_mes tem registro → retorna direto (1 query)
→ 12 queries total (leitura de 12 linhas)
→ tempo esperado: ~20–50ms (vs 4.4s antes)
```

### Invalidação automática (já implementada)

O cache é invalidado automaticamente quando:
- Usuário edita uma transação → `invalidate_cashflow_cache(db, user_id, ano, mes)` é chamado
- Usuário cria expectativa/budget → invalidação por ano
- Usuário faz upload de arquivo → meses do arquivo são invalidados

**Nenhuma mudança necessária na invalidação** — ela já existe e funcionará corretamente com o novo endpoint.

---

## Verificação de `get_cashflow_mes_cached`

Antes de implementar, confirmar que a função existe e está importável:

```bash
# Dentro do container backend:
docker exec finup_backend_dev python3 -c "
from app.domains.plano.service import get_cashflow_mes_cached
print('✅ Função existe:', get_cashflow_mes_cached)
"

# Verificar tabela existe:
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "\d plano_cashflow_mes"
```

Se `get_cashflow_mes_cached` não existir ainda (só `get_cashflow_mes`), criar o wrapper:

```python
# plano/service.py — adicionar função se não existir:

def get_cashflow_mes_cached(
    db: Session,
    user_id: int,
    ano: int,
    mes: int,
) -> dict:
    """
    Retorna cashflow do mês com cache em plano_cashflow_mes.
    Cache miss: computa e salva.
    Cache hit: retorna direto da tabela.
    """
    # Tentar cache
    cached = db.query(PlanoCashflowMes).filter(
        PlanoCashflowMes.user_id == user_id,
        PlanoCashflowMes.ano == ano,
        PlanoCashflowMes.mes == mes,
    ).first()

    if cached:
        return cached.dados  # JSON armazenado

    # Cache miss — computar
    dados = _compute_cashflow_mes(db, user_id, ano, mes)

    # Salvar no cache
    registro = PlanoCashflowMes(
        user_id=user_id,
        ano=ano,
        mes=mes,
        dados=dados,
        updated_at=datetime.utcnow(),
    )
    db.add(registro)
    db.commit()

    return dados
```

---

## Validação

### Testes manuais (Docker local)

```bash
# 1. Iniciar ambiente local
./scripts/deploy/quick_start_docker.sh

# 2. Testar endpoint anual (deve responder em <500ms agora)
time curl -s -X GET \
  "http://localhost:8000/api/v1/plano/cashflow?ano=2026&modo_plano=false" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool | head -30

# 3. Segunda chamada deve ser ainda mais rápida (cache hit)
time curl -s -X GET \
  "http://localhost:8000/api/v1/plano/cashflow?ano=2026&modo_plano=false" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool | head -5
```

**Resultados esperados:**
```
1ª chamada: ~200–500ms (cache miss — computa e salva)
2ª chamada: ~20–50ms   (cache hit — lê 12 linhas)
```

### Comparar shape do response

```bash
# Response do endpoint mensal (referência):
curl "http://localhost:8000/api/v1/plano/cashflow/mes?ano=2026&mes=3" \
  -H "Authorization: Bearer <token>" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sorted(d.keys()))"

# Response do endpoint anual, mês individual (deve ter mesmos campos):
curl "http://localhost:8000/api/v1/plano/cashflow?ano=2026" \
  -H "Authorization: Bearer <token>" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Shape anual:', sorted(d.keys()))
print('Shape mês[0]:', sorted(d['meses'][0].keys()))
"
```

### Validar no frontend

Navegar para `/mobile/budget` e verificar:
- Gráfico de cashflow anual renderiza corretamente
- 12 barras/pontos aparecem (um por mês)
- Valores batem com os do endpoint mensal individual

---

## Playwright — Avaliação Pré/Pós Sprint 3

### Passo 1 — Medir o endpoint anual ANTES

```bash
# Tempo do endpoint antes do fix (deve ser ~4400ms):
time curl -s \
  "http://localhost:8000/api/v1/plano/cashflow?ano=$(date +%Y)&modo_plano=false" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool | head -5

# Salvar baseline da página Budget/Plano:
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_baseline_pre_s3.txt

# Contar queries executadas (log do PostgreSQL):
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM plano_cashflow_mes WHERE user_id = 1;"
```

### Passo 2 — Medir DEPOIS (cache hit)

```bash
# 1ª chamada (cache miss — computa e salva):
time curl -s \
  "http://localhost:8000/api/v1/plano/cashflow?ano=$(date +%Y)&modo_plano=false" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -3
# Esperado: ~200–500ms

# 2ª chamada (cache hit — lê 12 linhas da tabela):
time curl -s \
  "http://localhost:8000/api/v1/plano/cashflow?ano=$(date +%Y)&modo_plano=false" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -3
# Esperado: ~20–50ms

# Playwright full:
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_resultado_s3.txt

grep -E "Budget|Plano" deploy/history/perf_baseline_pre_s3.txt
grep -E "Budget|Plano" deploy/history/perf_resultado_s3.txt
```

### Metas de aprovação

| Cenário | Antes | Meta pós-S3 | Critério de falha |
|---|---|---|---|
| `GET /cashflow?ano=` (1ª chamada) | ~4400ms | **< 500ms** | > 1000ms → ainda chama `get_cashflow()` diretamente |
| `GET /cashflow?ano=` (2ª+ chamada) | ~4400ms | **< 50ms** | > 200ms → cache não está sendo usado |
| Budget/Plano (Playwright) | ~5800ms | **< 1500ms** | > 3000ms → cache miss em todas as visitas |
| Shape do response | igual | **igual** | Dados diferentes/ausentes → regredir o frontend |

### Validar shape do response (crítico)

```bash
# Verificar que o novo endpoint retorna os mesmos campos que antes:
curl -s "http://localhost:8000/api/v1/plano/cashflow?ano=$(date +%Y)" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Shape raiz:', sorted(d.keys()))
print('Shape meses[0]:', sorted(d['meses'][0].keys()) if d.get('meses') else 'VAZIO')
print('Total meses:', len(d.get('meses', [])))
"
# Resultado esperado:
# Shape raiz: ['ano', 'meses', 'nudge_acumulado']
# Shape meses[0]: ['gastos_reais', 'gastos_recorrentes', 'investimentos', 'mes', ...]
# Total meses: 12
```

---

## Checklist Sprint 3

### Implementação
- [ ] `plano/router.py`: endpoint `GET /cashflow` reescrito com loop de `get_cashflow_mes_cached`
- [ ] `get_cashflow_mes_cached` existe e está importado
- [ ] `nudge_acumulado` calculado corretamente a partir dos 12 meses
- [ ] Shape do response idêntico ao anterior

### Qualidade
- [ ] Nenhum erro Python ao iniciar o backend: `docker-compose logs backend | grep ERROR`
- [ ] FastAPI docs (`/docs`) mostra o endpoint com schema correto
- [ ] `tsc --noEmit` no frontend: sem erros relacionados a `CashflowAnual`

### Performance
- [ ] 1ª chamada: < 500ms (cache miss aceitável)
- [ ] 2ª+ chamada: < 100ms (cache hit)
- [ ] Playwright Budget/Plano: tempo total < 1.5s

### Invalidação
- [ ] Editar uma transação do mês 3 → chamar `GET /cashflow?ano=2026` → mês 3 recomputado
- [ ] Criar nova expectativa → cashflow do mês afetado recomputado

### Git e Deploy
- [ ] Commit: `perf(plano): endpoint cashflow anual usa cache por mês (P2)`
- [ ] Push e deploy
- [ ] Smoke test em produção: `curl https://meufinup.com.br/api/v1/plano/cashflow?ano=2026 ...`

---

## Impacto Esperado

| Cenário | Hoje | Após Sprint 3 |
|---------|------|--------------|
| Budget/Plano — 1ª visita (cache miss) | 4.4s | ~300–500ms |
| Budget/Plano — 2ª+ visita (cache hit) | 4.4s | **~20–50ms** |
| Budget/Plano — 2ª chamada duplicada eliminada (S1/P3) | +2.2s extra | **eliminada pelo Sprint 4** |

**Nota:** a 2ª chamada duplicada de `/plano/cashflow` (via `budget/page.tsx`) será eliminada no Sprint 4 com React Query. Por ora, com cache, mesmo a 2ª chamada responderá em <50ms — imperceptível.

---

**Análise base:** [ANALISE_PERFORMANCE_VM.md](ANALISE_PERFORMANCE_VM.md) — Seção P2  
**Próximo passo:** [Sprint 4 — React Query + Redis](sprint-4-react-query-redis.md)
