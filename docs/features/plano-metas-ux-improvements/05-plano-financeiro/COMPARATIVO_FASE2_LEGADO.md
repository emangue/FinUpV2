# Comparativo Fase 2 — Legado vs PLANO_DE_AJUSTE

**Data:** 28/02/2026  
**Objetivo:** Reavaliar a Fase 2 (projeção, tabela recibo, cashflow) contra o legado antes de implementar.

---

## 1. O que o legado prevê

### 1.1 Cashflow engine (TECH_SPEC legado)

**Endpoint:** `GET /plano/cashflow?ano=2026` (não "cashflow-mensal")

**Estrutura de resposta:**
```json
{
  "ano": 2026,
  "nudge_acumulado": -333.40,
  "meses": [
    {
      "mes_referencia": "2026-03",
      "renda_esperada": 15000.00,
      "gastos_recorrentes": 10700.00,
      "gastos_extras_esperados": 1267.00,
      "gastos_realizados": 650.00,
      "aporte_planejado": 2500.00,
      "saldo_projetado": -2000.00,
      "status_mes": "parcial",
      "nudge_aposentadoria_mes": -828.00,
      "grupos": [...],
      "expectativas": [...]
    }
  ]
}
```

**Fontes de dados:**
- `user_financial_profile` → renda_mensal
- `budget_planning` → gastos_recorrentes (plano base)
- `base_expectativas` → gastos_extras_esperados, ganhos extras
- `journal_entries` → gastos_realizados (meses passados/atual)
- `investimentos_cenarios` → aporte_planejado, nudge

**Sem base_expectativas (Fase 2):** `gastos_extras_esperados = 0`, `expectativas = []`.

---

### 1.2 Tabela recibo (UX legado)

**Colunas:** Mês | Renda | Gastos | Aporte | Saldo

**Extras do legado:**
- Nota para meses anômalos (ex: "IPVA", "13º")
- Status visual: ✅ (ok), ⚠️ (saldo pequeno), ❌ (saldo negativo)
- Resumo do ano: Renda total, Gastos total, Aportes total, Saldo ano
- Aviso: "X meses com saldo negativo"

**Origem:** `CashflowRecibo` reutiliza padrão de `plano-chart.tsx` (tabela colapsável).

---

### 1.3 Projeção com slider (05-plano vs legado)

| Aspecto | Legado | 05-plano PLANO.md |
|---------|--------|-------------------|
| Slider "Reduzir gastos em X%" | ❌ Não existe | ✅ GET /plano/projecao?reducao_pct= |
| ProjecaoChart (linha poupança acumulada) | ❌ Não existe | ✅ Existe |
| Slider de aporte (teto = disponível) | ✅ Etapa 4 do wizard | ✅ Etapa 4 |
| Tabela recibo mês a mês | ✅ Sim | ✅ TabelaReciboAnual |

**Conclusão:** O legado foca em **cashflow + recibo**. O "ProjecaoChart" com slider de redução é uma adição do 05-plano (útil para cenários "e se eu reduzir?"), mas não é obrigatório no legado.

---

## 2. PLANO_DE_AJUSTE Fase 2 atual — gaps

| Task atual | Legado | Ajuste |
|------------|--------|--------|
| 2.1 GET /plano/projecao | Não existe no legado | Manter (valor agregado do 05-plano) |
| 2.2 ProjecaoChart | Não existe | Manter (opcional, pode ser Fase 2.1b) |
| 2.3 GET /plano/cashflow-mensal | Legado usa **cashflow** | Renomear para `GET /plano/cashflow?ano=` |
| 2.4 TabelaReciboAnual | CashflowRecibo / ReciboPorMes | Alinhar colunas: Mês \| Renda \| Gastos \| Aporte \| Saldo |
| 2.5 Integrar na tela | CTA "Ver cashflow anual" | Manter |
| 2.6 PUT /plano/perfil | Já existe em parte (renda) | Expandir: idade, aposentadoria, taxa |

---

## 3. Estrutura do cashflow (sem base_expectativas)

Para Fase 2, **sem** `base_expectativas`:

| Campo | Fonte | Observação |
|-------|-------|------------|
| renda_esperada | user_financial_profile.renda_mensal | Fixo por mês |
| gastos_recorrentes | budget_planning (soma por mes_referencia) | Plano base |
| gastos_extras_esperados | 0 | Fase 4 |
| gastos_realizados | journal_entries (meses passados/atual) | Meses futuros: null |
| aporte_planejado | user_financial_profile ou campo dedicado | Fase 3 define origem |
| saldo_projetado | renda − gastos − aporte | Calculado |

**Meses passados:** usar `gastos_realizados` do journal.  
**Meses futuros:** usar `gastos_recorrentes` (budget_planning).

---

## 4. Ajustes no PLANO_DE_AJUSTE

1. **Endpoint:** `GET /plano/cashflow?ano=` (não cashflow-mensal)
2. **Schema:** Alinhar campos ao legado (renda_esperada, gastos_recorrentes, gastos_realizados, aporte_planejado, saldo_projetado, status_mes)
3. **TabelaReciboAnual:** Colunas Mês | Renda | Gastos | Aporte | Saldo + status visual + resumo do ano
4. **ProjecaoChart:** Manter como task separada (valor do 05-plano, não bloqueia recibo)
5. **Ordem:** Cashflow primeiro (alimenta recibo), depois ProjecaoChart

---

## 5. Referências

- Legado TECH_SPEC: `_legado/02-TECH_SPEC/TECH_SPEC.md` (linhas 307–458, 631–636, 880–930)
- Legado UX: `_legado/UX_PLANO_FINANCEIRO_INTEGRADO.md` (Etapa 4, linhas 496–565)
- plano-chart: `features/plano-aposentadoria/components/plano-chart.tsx` (tabela "Primeiros meses")
