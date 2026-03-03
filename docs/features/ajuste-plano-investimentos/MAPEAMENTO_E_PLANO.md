# 📐 Mapeamento + Plano de Execução — API de Aporte de Investimento Detalhado

**Feature:** `ajuste-plano-investimentos`  
**Data:** 2026-03-02  
**Status:** 🟡 Rascunho — aguardando aprovação

---

## 1. Problema

O dashboard (tela `Orçamento → Investimentos vs Plano`) precisa exibir o **plano de investimento mensal** composto por:

- `aporte_fixo_mensal` — o valor que o usuário se compromete a investir todo mês
- `aportes_extraordinários` — entradas pontuais que também viram investimento (bônus, 13º, LTRP, etc.)

**Hoje o dashboard só recebe um número total por chamada** (`aporte: float`), sem saber:
- Qual parcela é fixa vs. extra
- Quais são as extras (nome, valor, recorrência)
- O breakout por mês do ano inteiro numa única resposta

Isso impede o frontend de mostrar detalhe, tooltips, e futuramente gráfico de composição do aporte.

---

## 2. Diagnóstico — O Que Já Existe

### 2.1 Fontes de dados existentes

| Fonte | Tabela / Campo | Conteúdo | Limitação |
|---|---|---|---|
| **Cenário principal** | `investimentos_cenarios` → `aporte_mensal` | Aporte fixo mensal do cenário | Só o fixo, sem extras |
| **Projeção do cenário** | `investimentos_cenario_projecao` → `aporte` | Total por mês (fixo + extra calculado) | Já calculado, mas sem desagregação |
| **Extras do cenário** | `investimentos_cenarios` → `extras_json` | JSON com lista de extras (mês, valor, recorrência, evolução) | Precisa de parsing; não é endpoint público |
| **Perfil financeiro** | `user_financial_profile` → `aporte_planejado` | Aporte fixo do wizard (sem cenário) | Sem extras; fallback |
| **Expectativas de plano** | `base_expectativas` (tipo `credito`) | Receitas extraordinárias (13º, bônus) | São **renda**, não aporte de investimento — fonte diferente |

### 2.2 APIs existentes

| Endpoint | Retorno | Uso atual |
|---|---|---|
| `GET /investimentos/cenarios/principal/aporte-mes?year=&month=` | `{aporte: float}` | OrcamentoTab — valor total do mês |
| `GET /investimentos/cenarios/principal/aporte-periodo?year=&ytd_month=` | `{aporte: float}` | OrcamentoTab — total YTD |
| `GET /plano/cashflow?ano=&modo_plano=true` | Array de 12 meses c/ `aporte_planejado` | OrcamentoTab — fallback quando sem cenário |
| `GET /plano/perfil` | `{aporte_planejado, ...}` | Wizard / perfil |

### 2.3 Fluxo atual no `OrcamentoTab`

```
fetchAportePrincipalPorMes(year, month)    → /investimentos/cenarios/principal/aporte-mes
  └── Cenário principal → CenarioProjecao.aporte (fixo + extra)     → número único
      Fallback: InvestimentoCenario.aporte_mensal

fetchAportePrincipalPeriodo(year, ytdMonth) → /investimentos/cenarios/principal/aporte-periodo
  └── Soma CenarioProjecao.aporte Jan..N     → número único
      Fallback: aporte_mensal × N meses

Fallback final (frontend): if (cenarioAporte === 0) usa planoMes.aporte_planejado (wizard)
```

**Resultado:** 2 chamadas separadas + fallback no frontend. Nenhuma delas expõe a composição (fixo vs. extra) nem a lista de extras com descrição.

---

## 3. Requisito da Nova API

### 3.1 Contrato proposto

```
GET /plano/aporte-investimento?ano=2026[&mes=3]
```

**Query params:**
- `ano` (obrigatório): int — ano de referência
- `mes` (opcional): int 1–12 — se informado, retorna só aquele mês; caso contrário, retorna os 12 meses

**Response (mês específico):**
```json
{
  "fonte": "cenario",
  "cenario_id": 12,
  "aporte_fixo_mensal": 2700.00,
  "mes": {
    "mes_referencia": "2026-03",
    "aporte_fixo": 2700.00,
    "aporte_extra": 90000.00,
    "aporte_total": 92700.00,
    "extras": [
      {
        "descricao": "Bonus",
        "valor": 90000.00,
        "recorrencia": "anual",
        "evoluir": true,
        "evolucaoValor": 15,
        "evolucaoTipo": "percentual"
      }
    ]
  }
}
```

**Response (ano inteiro, sem `mes`):**
```json
{
  "fonte": "cenario",
  "cenario_id": 12,
  "aporte_fixo_mensal": 2700.00,
  "total_fixo_ano": 32400.00,
  "total_extras_ano": 142600.00,
  "total_ano": 175000.00,
  "meses": [
    {
      "mes_referencia": "2026-01",
      "aporte_fixo": 2700.00,
      "aporte_extra": 50000.00,
      "aporte_total": 52700.00,
      "extras": [
        { "descricao": "LTRP", "valor": 50000.00, "recorrencia": "anual" }
      ]
    },
    {
      "mes_referencia": "2026-02",
      "aporte_fixo": 2700.00,
      "aporte_extra": 0.00,
      "aporte_total": 2700.00,
      "extras": []
    },
    {
      "mes_referencia": "2026-03",
      "aporte_fixo": 2700.00,
      "aporte_extra": 90000.00,
      "aporte_total": 92700.00,
      "extras": [
        { "descricao": "Bonus", "valor": 90000.00, "recorrencia": "anual", "evoluir": true, "evolucaoValor": 15, "evolucaoTipo": "percentual" }
      ]
    },
    ...
  ]
}
```

**Quando não há cenário principal:**
```json
{
  "fonte": "perfil",
  "cenario_id": null,
  "aporte_fixo_mensal": 2700.00,
  "meses": [
    { "mes_referencia": "2026-01", "aporte_fixo": 2700.00, "aporte_extra": 0.00, "aporte_total": 2700.00, "extras": [] },
    ...
  ],
  "total_fixo_ano": 32400.00,
  "total_extras_ano": 0.00,
  "total_ano": 32400.00
}
```

**Quando não há nem cenário nem perfil:**
```json
{
  "fonte": null,
  "cenario_id": null,
  "aporte_fixo_mensal": 0.00,
  "meses": [...meses com zeros...],
  "total_fixo_ano": 0.00,
  "total_extras_ano": 0.00,
  "total_ano": 0.00
}
```

### 3.2 Lógica de montagem da resposta

```
1. Busca cenário principal (InvestimentoCenario WHERE principal=True AND ativo=True)

  SE cenário existe:
    fonte = "cenario"
    aporte_fixo_mensal = cenario.aporte_mensal

    Para cada mês do ano:
      - aporte_total = CenarioProjecao.aporte WHERE anomes = YYYYMM  (já calculado)
      - aporte_extra = aporte_total - aporte_fixo_mensal
      - extras = parse(cenario.extras_json) → filtrar os que batem com o mês do calendário
        (usar a mesma lógica de _calcular_projecao_mensal do InvestimentoService)

  SE não existe cenário:
    fonte = "perfil"
    aporte_fixo_mensal = user_financial_profile.aporte_planejado (ou 0)
    extras = [] em todos os meses
    aporte_total = aporte_fixo_mensal para todos os meses
```

---

## 4. Mapeamento de Impacto

### 4.1 O que NÃO muda

- `GET /investimentos/cenarios/principal/aporte-mes` — **mantido** (OrcamentoTab ainda usa)
- `GET /investimentos/cenarios/principal/aporte-periodo` — **mantido** (OrcamentoTab ainda usa)
- Modelos de banco (sem migration) — todos os dados já existem
- Frontend OrcamentoTab — **não quebra**; nova API é **adicional**

### 4.2 Arquivos a criar/modificar

**Backend — apenas adições (0 quebras):**

| Arquivo | Ação | Descrição |
|---|---|---|
| `app/domains/investimentos/repository.py` | Adicionar método | `get_aporte_detalhado_por_ano(user_id, ano)` |
| `app/domains/investimentos/service.py` | Adicionar método | `get_aporte_investimento_detalhado(user_id, ano, mes)` |
| `app/domains/plano/router.py` | Adicionar endpoint | `GET /plano/aporte-investimento` |
| `app/domains/plano/service.py` | Adicionar método | `get_aporte_investimento(user_id, ano, mes)` que orquestra cenário + perfil |
| `app/domains/plano/schemas.py` | Adicionar schemas | `AporteExtraDetalhe`, `AporteMesDetalhe`, `AporteInvestimentoResponse` |

> **Decisão de domínio:** O endpoint fica em `/plano/` (não `/investimentos/`) porque consolida duas fontes — cenário e perfil — e o domínio `plano` é o orquestrador do plano financeiro pessoal. O `PlanoService` já faz esse papel em `/plano/cashflow` e `/plano/resumo`.

**Frontend — opcional (sem urgência):**

| Arquivo | Ação | Descrição |
|---|---|---|
| `features/dashboard/services/dashboard-api.ts` | Adicionar função | `fetchAporteInvestimentoDetalhado(year, month?)` |
| `features/dashboard/components/orcamento-tab.tsx` | (Opcional) Migrar | Substituir 2 chamadas por 1, usar detalhe de extras |

---

## 5. Plano de Execução (Sprints)

### Sprint 1 — Backend (estimativa: 1–2h)

**Objetivo:** Implementar e testar o endpoint sem tocar no frontend.

#### T1 — Schemas (`app/domains/plano/schemas.py`)

```python
class AporteExtraDetalhe(BaseModel):
    descricao: str
    valor: float
    recorrencia: str        # unico | anual | semestral | trimestral
    evoluir: bool = False
    evolucaoValor: float = 0.0
    evolucaoTipo: str = "percentual"

class AporteMesDetalhe(BaseModel):
    mes_referencia: str     # YYYY-MM
    aporte_fixo: float
    aporte_extra: float
    aporte_total: float
    extras: list[AporteExtraDetalhe]

class AporteInvestimentoResponse(BaseModel):
    fonte: Optional[str]    # "cenario" | "perfil" | None
    cenario_id: Optional[int]
    aporte_fixo_mensal: float
    total_fixo_ano: float
    total_extras_ano: float
    total_ano: float
    mes: Optional[AporteMesDetalhe] = None   # quando ?mes= informado
    meses: Optional[list[AporteMesDetalhe]] = None  # quando ano inteiro
```

#### T2 — Service (`app/domains/plano/service.py`)

Novo método `get_aporte_investimento(user_id, ano, mes=None)`:

```
1. Tenta buscar cenário principal via InvestimentoCenario
2. Se encontrou:
   a. aporte_fixo_mensal = cenario.aporte_mensal
   b. Para cada mês do ano:
      - Consulta CenarioProjecao.aporte (anomes = ano*100+m) → aporte_total
      - aporte_extra = aporte_total - aporte_fixo_mensal
      - Parse extras_json → filtrar extras do mês usando lógica calendário
   c. fonte = "cenario"
3. Se não encontrou:
   a. Consulta UserFinancialProfile.aporte_planejado
   b. aporte_fixo_mensal = profile.aporte_planejado (ou 0)
   c. Todos os meses = aporte_fixo_mensal, sem extras
   d. fonte = "perfil" ou None se aporte=0
4. Montar AporteInvestimentoResponse
5. Se mes informado: retornar só aquele mês em .mes
   Senão: retornar todos em .meses com totais anuais
```

**Parsing de `extras_json` por mês calendário:**
O `extras_json` usa `mesAno` = mês do calendário (1=Jan … 12=Dez) + `recorrencia`.
Reutilizar a lógica já existente em `InvestimentoService._calcular_projecao_mensal`.

> ⚠️ **Cuidado:** Não replicar a lógica — extraí-la para um método auxiliar privado ou importar do `InvestimentoService`. Avaliar se vale mover para `app/shared/` ou deixar inline no `PlanoService` com comentário de referência cruzada.

#### T3 — Router (`app/domains/plano/router.py`)

```python
@router.get("/aporte-investimento")
def aporte_investimento(
    ano: int = Query(..., ge=2020, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Aporte de investimento planejado: fixo + extras por mês/ano."""
    service = PlanoService(db)
    return service.get_aporte_investimento(user_id, ano, mes)
```

#### T4 — Teste manual

```bash
# Mês específico com cenário
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/plano/aporte-investimento?ano=2026&mes=3"

# Ano inteiro
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/plano/aporte-investimento?ano=2026"

# Usuário sem cenário (fallback perfil)
# → verificar que "fonte" = "perfil", sem extras
```

**Critérios de aceite do Sprint 1:**
- [ ] `fonte: "cenario"` quando há cenário principal
- [ ] `fonte: "perfil"` quando não há cenário (usa `aporte_planejado`)
- [ ] `extras[]` com descrição, valor, recorrência para cada mês com extra
- [ ] `aporte_extra` = `aporte_total` - `aporte_fixo` (deve ser ≥ 0)
- [ ] Para março/2026 com Bonus (R$90k): `aporte_total ≈ 92.700`
- [ ] `total_extras_ano` = soma de todos os extras = coerente com `/cenarios/principal/aporte-periodo`

---

### Sprint 2 — Frontend (estimativa: 1h, opcional)

**Objetivo:** Usar a nova API no OrcamentoTab para reduzir chamadas e exibir composição.

#### T5 — `dashboard-api.ts`

```typescript
export interface AporteExtraDetalhe {
  descricao: string
  valor: number
  recorrencia: string
  evoluir: boolean
  evolucaoValor: number
  evolucaoTipo: string
}

export interface AporteMesDetalhe {
  mes_referencia: string
  aporte_fixo: number
  aporte_extra: number
  aporte_total: number
  extras: AporteExtraDetalhe[]
}

export interface AporteInvestimentoResponse {
  fonte: 'cenario' | 'perfil' | null
  cenario_id: number | null
  aporte_fixo_mensal: number
  total_fixo_ano: number
  total_extras_ano: number
  total_ano: number
  mes?: AporteMesDetalhe
  meses?: AporteMesDetalhe[]
}

export async function fetchAporteInvestimentoDetalhado(
  year: number,
  month?: number
): Promise<AporteInvestimentoResponse | null> {
  try {
    const params = new URLSearchParams({ ano: year.toString() })
    if (month != null) params.append('mes', month.toString())
    const response = await fetchWithAuth(`${BASE_URL}/plano/aporte-investimento?${params}`)
    if (!response.ok) return null
    return response.json()
  } catch {
    return null
  }
}
```

#### T6 — `orcamento-tab.tsx` (migração das duas chamadas para uma)

Substituir:
```tsx
isAnoOuYtd
  ? fetchAportePrincipalPeriodo(year, ytdMonthProp)
  : fetchAportePrincipalPorMes(year, mesRef),
```

Por:
```tsx
fetchAporteInvestimentoDetalhado(year, isAnoOuYtd ? undefined : mesRef),
```

E extrair:
```tsx
const aporteDetalhe = results[5].status === 'fulfilled' ? results[5].value : null
const cenarioAporte = isAnoOuYtd
  ? (aporteDetalhe?.total_ano ?? 0)
  : (aporteDetalhe?.mes?.aporte_total ?? 0)
// Fallback: aporte_fixo_mensal quando fonte = "perfil"
// Extras disponíveis: aporteDetalhe?.mes?.extras ou aporteDetalhe?.meses
```

**Critérios de aceite do Sprint 2:**
- [ ] OrcamentoTab funciona igual ao antes (valor total igual)
- [ ] Nenhuma regressão visual
- [ ] `aporteDetalhe.mes.extras` acessível para futuros tooltips/detalhe

---

## 6. Riscos e Decisões

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Parsing de `extras_json` duplicado entre `InvestimentoService` e `PlanoService` | Alta | Extrair helper em `app/shared/` ou fazer `PlanoService` chamar `InvestimentoService` via import documentado (orquestrador) |
| `CenarioProjecao` sem linhas para o ano pedido | Média | Fallback: recalcular on-the-fly com `_calcular_projecao_mensal` (ou recriar projeção) |
| Divergência entre `CenarioProjecao.aporte` e parsing direto de `extras_json` | Baixa | Usar `CenarioProjecao` como fonte do total; extras_json só para metadados (descrição, recorrência) |
| YTD: ytdMonth ≠ mês atual | Baixa | Parâmetro `mes` corta a lista no frontend; backend retorna o ano inteiro |

### Decisão de domínio

> O endpoint vive em `/plano/` e não em `/investimentos/` porque:
> 1. Consolida duas fontes (cenário + perfil) — papel orquestrador do domínio `plano`
> 2. Evita acoplamento direto entre `OrcamentoTab` e `InvestimentoCenario`
> 3. O `PlanoService` já tem precedente de agregar fontes (`get_cashflow`, `get_resumo`)

---

## 7. Checklist Final

### Sprint 1 — Backend
- [ ] Schemas criados e validados
- [ ] `PlanoService.get_aporte_investimento` implementado
- [ ] Endpoint `GET /plano/aporte-investimento` registrado no router
- [ ] Teste manual OK para: cenário com extras, cenário sem extras, sem cenário
- [ ] Valor total bate com `/cenarios/principal/aporte-mes` e `/aporte-periodo`

### Sprint 2 — Frontend
- [ ] `fetchAporteInvestimentoDetalhado` implementado
- [ ] OrcamentoTab migrado sem regressão
- [ ] Tipos TypeScript alinhados com response do backend

---

## 8. Referências

| Arquivo | Relevância |
|---|---|
| `app_dev/backend/app/domains/investimentos/models.py` | `InvestimentoCenario`, `CenarioProjecao`, `AporteExtraordinario` |
| `app_dev/backend/app/domains/investimentos/repository.py` L713–775 | `get_aporte_principal_por_mes`, `get_aporte_principal_periodo` |
| `app_dev/backend/app/domains/investimentos/service.py` L350–428 | `_calcular_projecao_mensal` — lógica de parse de `extras_json` |
| `app_dev/backend/app/domains/plano/models.py` | `UserFinancialProfile`, `BaseExpectativa` |
| `app_dev/backend/app/domains/plano/service.py` | `get_cashflow` — precedente de orquestração de fontes |
| `app_dev/backend/app/domains/plano/router.py` | Local do novo endpoint |
| `app_dev/frontend/src/features/dashboard/services/dashboard-api.ts` | `fetchAportePrincipalPorMes`, `fetchAportePrincipalPeriodo` |
| `app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx` | Consumer principal dos dados de aporte |
