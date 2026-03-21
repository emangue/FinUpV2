# Projeção de Economia — Extraordinários Ausentes + Oportunidades de API

> Tela: `localhost:3000/mobile/plano`
> Data: Março/2026

---

## Problema Principal: Extraordinários Cancelam na Curva Laranja

### Comportamento atual (bug)

A tela de Plano mostra três linhas no gráfico de projeção de poupança:

| Linha | Cor | Descrição |
|-------|-----|-----------|
| Plano | Azul | Poupança acumulada sem redução de gastos |
| Real + Plano | Verde | Dados realizados + projeção futura base |
| Real + Economia | Laranja tracejada | Dados realizados + projeção com slider "Reduzir gastos em X%" |

**O bug:** a linha laranja (Economia) não reflete os extraordinários (IPVA, 13º salário, bônus, viagens, parcelas futuras). Ela mostra apenas o ganho matemático da redução percentual de gastos recorrentes — uma linha suavizada, sem os "degraus" e quedas que os extraordinários causariam.

**Resultado visual:** a curva laranja parece artificial — cresce de forma constante, sem mostrar que em março haverá um grande débito de seguro, ou que em dezembro haverá entrada do 13º salário.

---

## Diagnóstico Técnico

### Onde está o bug

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`
**Função:** `PlanoService.get_projecao()` — linhas 466-533

A função tem dois branches:

```python
# Branch 1: curva azul (sem_patrimonio=True AND reducao_pct == 0)
if sem_patrimonio and reducao_pct == 0:
    exp_por_mes = self.get_expectativas_por_mes_para_ano(user_id, ano)
    for i, m in enumerate(cashflow["meses"][:meses]):
        mes_ref = m["mes_referencia"]
        exp = exp_por_mes.get(mes_ref, {"debitos": 0.0, "creditos": 0.0})
        creditos = exp["creditos"]
        debitos = exp["debitos"]
        aporte_mes = aporte_planejado                    # ← valor fixo do perfil
        extras_mes = creditos - debitos                  # ← NET dos extraordinários
        aporte_total_mes = aporte_mes + extras_mes       # ← correto: inclui tudo
        acumulado_aportes += aporte_total_mes

# Branch 2: curva laranja (qualquer reducao_pct > 0) ← BUG AQUI
else:
    for i, m in enumerate(cashflow["meses"][:meses]):
        renda_mes   = m.get("renda_usada") or 0.0          # = renda_base + creditos_extras
        gastos_base = m.get("gastos_usados") or ...        # = gastos_rec_corr (sem extras)
        extras      = m.get("gastos_extras_esperados", 0)  # = debitos_extras
        gastos      = (gastos_base * fator) + extras       # reduz recorrentes, mantém débitos
        aporte_mes  = m.get("aporte_usado") or ...         # = renda_usada - total_gastos  ← problema
        saldo_mes   = renda_mes - gastos - aporte_mes
        acumulado  += saldo_mes
```

### Por que os extraordinários cancelam

O campo `aporte_usado` no cashflow é calculado como:

```python
# service.py linha 426 (dentro de get_cashflow)
r = round(renda_usada / 100) * 100       # renda_base + creditos_extras (arredondado)
g = round(total_gastos / 100) * 100      # gastos_rec + debitos_extras (arredondado)
a = (r - g) if renda_usada else 0        # ← aporte_usado já absorveu TUDO
```

Então no branch 2, para meses futuros:

```
saldo_mes = renda_mes         - gastos                     - aporte_mes
          = (renda_base + Ce) - ((gastos_rec * fator) + De) - (renda_base + Ce - gastos_rec - De)
          = renda_base + Ce   - gastos_rec*fator - De       - renda_base - Ce + gastos_rec + De
          = gastos_rec - gastos_rec*fator
          = gastos_rec * (reducao_pct / 100)
```

Onde `Ce` = créditos extraordinários e `De` = débitos extraordinários.

**Resultado:** `Ce` e `De` somem completamente da equação. A curva laranja mostra apenas `Σ gastos_rec_mes * reducao_pct/100` — um valor constante e suavizado, sem nenhuma variação sazonal dos extraordinários.

---

### Comparação: comportamento esperado vs atual

| Cenário | Curva Azul (correto) | Curva Laranja (atual, errado) | Curva Laranja (esperado) |
|---------|---------------------|-------------------------------|--------------------------|
| Março: IPVA R$ 3.000 | ↓ dip de 3.000 | sem variação | ↓ dip de 3.000 |
| Julho: Bônus R$ 8.000 | ↑ spike de 8.000 | sem variação | ↑ spike de 8.000 |
| Dez: 13º R$ 5.000 | ↑ spike de 5.000 | sem variação | ↑ spike de 5.000 |
| Janeiro: Seguro R$ 2.000 | ↓ dip de 2.000 | sem variação | ↓ dip de 2.000 |

---

## Solução

### Fórmula correta para a curva laranja

```
saldo_mes = renda - gastos_rec × (1 - %economia) + aportes_extraordinarios - gastos_extraordinarios
```

Mapeado para os campos do cashflow (todos já existem no output de `get_cashflow()`):

```
saldo_mes = m["renda_esperada"]
          - m["gastos_recorrentes"] × (1 - reducao_pct/100)
          + m["extras_creditos"]
          - m["extras_debitos"]
```

**Propriedades da fórmula:**
- `renda_esperada` = renda base planejada (sem extraordinários embutidos)
- `gastos_recorrentes` = só os gastos recorrentes (o slider age aqui e somente aqui)
- `extras_creditos` / `extras_debitos` = extraordinários brutos, sem redução pelo slider
- Quando `reducao_pct = 0`: `saldo_mes = renda_esperada - gastos_recorrentes + Ce - De`
  - Que equivale a `aporte_planejado + Ce - De` = idêntico à curva azul ✅

### Correção no service

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

```python
def get_projecao(self, user_id, ano, meses=12, reducao_pct=0.0, sem_patrimonio=False):
    cashflow = self.get_cashflow(user_id, ano, modo_plano_sempre=sem_patrimonio)
    profile = self.db.query(UserFinancialProfile).filter_by(user_id=user_id).first()
    patrimonio = 0.0 if sem_patrimonio else float(profile.patrimonio_atual or 0)
    aporte_planejado = float(profile.aporte_planejado or 0) if profile else 0.0

    fator = 1.0 - (reducao_pct / 100.0)
    acumulado = patrimonio
    serie = []

    if sem_patrimonio and reducao_pct == 0:
        # Curva azul — comportamento atual, correto (não alterar)
        exp_por_mes = self.get_expectativas_por_mes_para_ano(user_id, ano)
        acumulado_aportes = 0.0
        for i, m in enumerate(cashflow["meses"][:meses]):
            mes_ref = m["mes_referencia"]
            exp = exp_por_mes.get(mes_ref, {"debitos": 0.0, "creditos": 0.0})
            extras_mes = exp["creditos"] - exp["debitos"]
            aporte_total_mes = aporte_planejado + extras_mes
            acumulado_aportes += aporte_total_mes
            serie.append({
                "mes": i + 1,
                "mes_referencia": mes_ref,
                "saldo_mes": round(aporte_total_mes, 2),
                "acumulado": round(acumulado_aportes, 2),
            })
    else:
        # Curva laranja — CORREÇÃO:
        # Formula: renda - gastos_rec*(1-%eco) + extras_creditos - extras_debitos
        # Todos os campos já estão disponíveis no cashflow output.
        for i, m in enumerate(cashflow["meses"][:meses]):
            if m.get("use_realizado"):
                # Meses passados com dados reais: usar valores realizados diretamente
                renda_real   = m.get("renda_realizada") or 0.0
                gastos_real  = m.get("gastos_realizados") or 0.0
                invest_real  = m.get("investimentos_realizados") or 0.0
                saldo_mes    = renda_real - gastos_real - invest_real
            else:
                # Meses futuros: aplicar a fórmula correta
                # O slider reduz APENAS os gastos recorrentes
                # Extraordinários ficam integrais (bônus não é "economizado", IPVA não é negociável)
                renda_base       = m.get("renda_esperada") or 0.0
                gastos_rec       = m.get("gastos_recorrentes") or 0.0
                creditos_extras  = m.get("extras_creditos") or 0.0   # bônus, 13º, LTRP...
                debitos_extras   = m.get("extras_debitos") or 0.0    # IPVA, seguro, viagem...

                saldo_mes = (
                    renda_base
                    - gastos_rec * fator      # ← redução aplicada só aqui
                    + creditos_extras          # ← aumenta a poupança (não sofre redução)
                    - debitos_extras           # ← diminui a poupança (não sofre redução)
                )

            acumulado += saldo_mes
            serie.append({
                "mes": i + 1,
                "mes_referencia": m["mes_referencia"],
                "saldo_mes": round(saldo_mes, 2),
                "acumulado": round(acumulado, 2),
            })

    return {
        "patrimonio_inicial": patrimonio,
        "reducao_pct": reducao_pct,
        "serie": serie,
    }
```

### Por que o fix anterior estava errado e este está correto

| Situação | Fórmula anterior (bug) | Fórmula correta |
|----------|----------------------|-----------------|
| Março com IPVA R$ 3.000 | `saldo_mes` ignora os R$ 3.000 | `saldo_mes -= 3.000` → dip visível |
| Dezembro com 13º R$ 5.000 | `saldo_mes` ignora os R$ 5.000 | `saldo_mes += 5.000` → spike visível |
| eco=0 vs eco=0 (azul) | valores diferentes (bug) | valores idênticos ✅ |
| Slider de 0 → 15% | só muda a inclinação | muda a inclinação E mantém sazonalidade |

---

## Oportunidades de Performance na Tela de Plano

### Mapeamento de APIs no mount

A tela de Plano aciona múltiplos componentes independentes que fazem fetch no mount:

| Componente | Endpoint | Cache | Observação |
|------------|----------|-------|------------|
| `PlanoHubPage` | `GET /plano/resumo?ano=Y&mes=M` | ❌ | mount |
| `PlanoHubPage` | `GET /plano/orcamento?ano=Y&mes=M` | ❌ | mount |
| `PlanoResumoCard` | `GET /dashboard/income-sources?ano=Y&mes=M` | 2 min | via use-dashboard |
| `PlanoResumoCard` | `GET /budget/planning?mes_referencia=YYYY-MM` | 2 min | via use-goals |
| `PlanoResumoCard` | `GET /dashboard/aporte-investimento-detalhado?ano=Y&mes=M` | ❌ | sem cache |
| `AnosPerdidasCard` | `GET /plano/impacto-longo-prazo?ano=Y&mes=M` | ❌ | sem cache |
| `ProjecaoChart` | `GET /plano/projecao?ano=Y&meses=12&reducao_pct=0&sem_patrimonio=true` | ❌ | curva azul |
| `ProjecaoChart` | `GET /plano/cashflow?ano=Y` | ❌ | dados realizados |
| `ProjecaoChart` | `GET /plano/projecao?...&reducao_pct=X` | ❌ | curva laranja (se slider > 0) |

**Total no cold start:** 8-9 chamadas simultâneas, nenhuma com cache.

---

### P-Plano-1 — `ProjecaoChart` refaz 3 fetches a cada mudança do slider

**Impacto:** Alto na UX — cada arraste do slider dispara 1-3 chamadas de API.

**Localização:** `src/features/plano/components/ProjecaoChart.tsx` — useEffect reage a `reducaoPct`.

**Comportamento atual:**
```typescript
// ProjecaoChart.tsx linha ~68
useEffect(() => {
  getProjecao(ano, 12, 0, true)            // sempre busca base
  getCashflow(ano)                          // sempre busca cashflow
  if (reducaoPct > 0) getProjecao(ano, 12, reducaoPct, true)  // curva laranja
}, [selectedYear, reducaoPct])  // ← dispara em CADA mudança de reducaoPct
```

O slider tem step de 5% (0, 5, 10, ..., 50%). Se o usuário arrasta de 0 para 30%, dispara 6 re-fetches.

**Solução:** debounce de 400ms + cache das projeções já calculadas:

```typescript
// Debounce no onChange do slider
const [sliderValue, setSliderValue] = useState(0)
const [debouncedPct, setDebouncedPct] = useState(0)

useEffect(() => {
  const timer = setTimeout(() => setDebouncedPct(sliderValue), 400)
  return () => clearTimeout(timer)
}, [sliderValue])

// Cache de projeções (evita refetch do mesmo percentual)
const projCache = useRef<Map<number, ProjecaoData>>(new Map())

useEffect(() => {
  if (projCache.current.has(debouncedPct)) {
    setProjecaoData(projCache.current.get(debouncedPct)!)
    return
  }
  getProjecao(ano, 12, debouncedPct, true).then((data) => {
    projCache.current.set(debouncedPct, data)
    setProjecaoData(data)
  })
}, [debouncedPct, ano])
```

**Impacto esperado:** de N fetches por arraste → 1 fetch por posição final do slider.

---

### P-Plano-2 — `GET /plano/cashflow` na ProjecaoChart duplica o fetch do dashboard

**Impacto:** Médio — se o usuário vem do dashboard, o cashflow já foi buscado e cacheado ali.

**Problema:** o componente `ProjecaoChart` faz `getCashflow(ano)` sem verificar se o dado já existe em cache de outra tela. Como o plano não tem cache algum, é sempre um novo request.

**Solução:** incluir `plano/cashflow` no utilitário `in-memory-cache.ts` (B4 do plano principal) com TTL de 2 min. O hit cross-componente funciona automaticamente.

---

### P-Plano-3 — Nenhum endpoint de plano tem cache

Todos os endpoints consumidos pela tela de Plano fazem fetch toda vez que o componente renderiza ou o mês muda:

| Endpoint | TTL sugerido |
|----------|-------------|
| `GET /plano/resumo` | 2 min |
| `GET /plano/orcamento` | 2 min |
| `GET /plano/cashflow` | 2 min |
| `GET /plano/projecao` | 5 min por `(ano, reducao_pct)` |
| `GET /plano/impacto-longo-prazo` | 5 min |

Cache key sugerida para projeção: `plano:projecao:${ano}:${reducaoPct}:${semPatrimonio}`.

---

### P-Plano-4 — `GET /plano/cashflow` ainda computa 48-60 queries (tabela materializada)

Mesmo problema documentado como **A1** no plano geral (`04-cashflow-tabela-materializada.md`).

O endpoint `GET /plano/cashflow?ano=Y` está no caminho crítico da `ProjecaoChart` — é chamado no mount e a projeção depende do resultado. Com 48-60 queries dinâmicas por request, é o maior gargalo isolado da tela.

**A tabela materializada (`plano_cashflow_mes`) já está planejada no A1 e deve ser implementada antes das melhorias da ProjecaoChart.** Quando implementada:

- `get_cashflow()` → 1 query por mês (SELECT da tabela materializada)
- `get_projecao()` → 1 query para buscar os 12 meses do ano
- A ProjecaoChart passa de 300-800ms para ~30ms por request de cashflow

**Observação importante:** a correção do bug da curva laranja usa os campos `gastos_recorrentes`, `extras_creditos` e `extras_debitos` que **já estão mapeados na tabela materializada** proposta no A1. Ou seja, implementar A1 não só resolve o gargalo de performance como também disponibiliza os campos necessários para a curva laranja de forma eficiente.

Se A1 não estiver implementado quando a correção da curva laranja for feita, a correção funciona da mesma forma — apenas mais lenta (ainda faz as 48-60 queries dinamicamente). Não há dependência bloqueante, mas A1 deve ser prioridade.

---

### P-Plano-5 — Slider re-busca a base (reducao_pct=0) em todo mount

**Problema:** `ProjecaoChart` busca `getProjecao(..., reducao_pct=0, ...)` sempre no mount, inclusive em re-renders por mudança de mês. Esse dado poderia ser buscado uma única vez e mantido em ref enquanto o ano não mudar.

```typescript
// Melhorar: separar fetch da base do fetch do slider
const baseDataRef = useRef<ProjecaoData | null>(null)

useEffect(() => {
  // Só refaz a base quando o ano muda (não quando o slider muda)
  Promise.all([
    getProjecao(ano, 12, 0, true),
    getCashflow(ano),
  ]).then(([base, cashflow]) => {
    baseDataRef.current = base
    setCashflowData(cashflow)
    setBaseData(base)
  })
}, [ano])  // ← separado do effect do slider

useEffect(() => {
  if (!debouncedPct) return
  getProjecao(ano, 12, debouncedPct, true).then(setReducaoData)
}, [debouncedPct, ano])
```

---

## Arquivos a Criar/Modificar

| Arquivo | Ação | Item |
|---------|------|------|
| `app_dev/backend/app/domains/plano/service.py` | Reescrever branch 2 de `get_projecao()` (linhas 511-528) | Bug principal |
| `src/features/plano/components/ProjecaoChart.tsx` | Separar effects de base e slider + debounce 400ms | P-Plano-1, P-Plano-5 |
| `src/features/plano/api.ts` | Adicionar cache com `in-memory-cache.ts` para todas as funções | P-Plano-2, P-Plano-3 |

## Análise de Impacto — Nada Quebra

### Consumers do endpoint `/plano/projecao`

| Consumer | Como chama | Impactado? |
|----------|-----------|------------|
| `ProjecaoChart.tsx` | `getProjecao(ano, 12, 0, true)` e `getProjecao(ano, 12, reducaoPct, true)` | ✅ funciona corretamente |
| `PlanoAposentadoriaStepContent.tsx` | chama `getProjecaoLonga` (endpoint separado) | ✅ não afetado |
| Outros serviços backend | nenhum | ✅ não há |

### Por que `sem_patrimonio=True` elimina qualquer risco

Quando `sem_patrimonio=True` (único modo usado pelo frontend):
- `get_projecao()` chama `get_cashflow(..., modo_plano_sempre=True)`
- `modo_plano_sempre=True` → `use_realizado=False` em **todos os 12 meses**
- O branch `if m.get("use_realizado"):` da fix **nunca é alcançado**
- Todos os 12 meses usam a fórmula nova: `renda_esperada - gastos_rec*fator + Ce - De`

### Como o frontend constrói a curva laranja

```typescript
// ProjecaoChart.tsx linhas 124-133
const serieRealMaisEconomia = seriePlano.map((_, i) => {
  // Meses passados: usa investimentos_realizados do cashflow (ignora projecao)
  if (i <= lastRealIdx && serieReal[i] != null) return serieReal[i]

  // Meses futuros: pega o DELTA da projeção a partir do último mês realizado
  return realAteMes + (serieReducao[i].acumulado - ytdReducao)
  //                   ↑ delta com sazonalidade dos extraordinários (correto com o fix)
})
```

Com o fix, `ytdReducao` (acumulado no último mês realizado) passa a incluir os extraordinários dos meses passados. Isso é correto — o ponto de ancoragem da curva laranja agora reflete a realidade antes de projetar o futuro.

### Shape do response — inalterado

```python
# Antes e depois do fix: mesmo shape
{
  "patrimonio_inicial": float,
  "reducao_pct": float,
  "serie": [
    { "mes": int, "mes_referencia": str, "saldo_mes": float, "acumulado": float }
  ]
}
```

---

## Checklist de Validação

- [ ] Curva laranja mostra dip nos meses com débitos extraordinários (IPVA, seguros)
- [ ] Curva laranja mostra spike nos meses com créditos extraordinários (13º, bônus)
- [ ] Curva azul não muda após a correção (branch 1 não foi tocado)
- [ ] Slider em 0%: curva laranja coincide com curva azul (sem patrimônio inicial)
- [ ] Slider em 15%: curva laranja fica acima da azul em `Σ gastos_rec_mes * 0.15` nos meses sem extraordinários
- [ ] Débitos extras não são reduzidos pelo slider (IPVA é R$ X independente do slider)
- [ ] Arrastar slider rapidamente: apenas 1 request ao parar (debounce funcionando)
- [ ] Navegar dashboard → plano: cashflow é servido do cache (sem request extra)
