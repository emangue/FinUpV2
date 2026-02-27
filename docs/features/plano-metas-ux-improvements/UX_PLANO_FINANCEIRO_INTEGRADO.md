# UX — Plano Financeiro Integrado (Gastos + Aposentadoria)

**Data:** 26/02/2026  
**Status:** � Decisões tomadas — pronto para Tech Spec  
**Objetivo:** Pensar como seria a experiência completa de construção de plano, integrando renda, gastos, gastos extraordinários, evolução e o "recibo" final

---

## Decisões tomadas

| Questão | Decisão |
|---------|---------|
| Entry point | **Nova tab no bottom nav: "Plano"** — substitui "Metas" (ver mapa abaixo) |
| Plano unificado? | **Sim** — um só construtor, gastos + aposentadoria integrados |
| Evolução por grupo | **Não** — apenas inflação global ("seus gastos evoluem com o IPCA") |
| Parcelamento no banco | **N linhas** (via `budget_planning` + campos de parcela) — ponte para `base_parcelas` futura |
| Recibo | **Apenas 1 ano** de exemplo, resumo anual no final |

---

## Mapa do app atual e impacto da mudança

### Bottom nav hoje (5 tabs)
```
[Dashboard] [Transações] [Metas●] [Carteira] [Perfil]
                          ↑ FAB preto
```
"Metas" (Target icon, FAB central) → `/mobile/budget` → lista de metas de gasto por grupo

### Telas conectadas ao tema de plano (inventário)

| Tela | Path | O que faz hoje | Impacto |
|------|------|----------------|---------|
| Metas | `/mobile/budget` | Lista metas por grupo (budget_planning) | **Transforma**: vira "Acompanhamento" |
| Meta detalhe | `/mobile/budget/[goalId]` | Mostra gasto vs meta do grupo | Mantém |
| Nova meta | `/mobile/budget/new` | Form simples de criar meta | **Substitui**: entra pelo Construtor |
| Editar metas | `/mobile/budget/edit` | Edita valores bulk | **Substitui**: entra pelo Construtor |
| Personalizar plano | `/mobile/personalizar-plano` | Wizard do plano de aposentadoria | **Unifica**: vira parte do Construtor |
| Dashboard → aba Resultado → OrcamentoTab | `/mobile/dashboard` | Mostra despesas vs plano + investimentos vs plano | Mantém, alimentado pelo novo plano |
| Dashboard → aba Patrimônio → PlanoAposentadoriaTab | `/mobile/dashboard` | Card com CTA para personalizar plano, gráfico de projeção | **Atualiza**: CTA vai para o Construtor unificado |
| Carteira → botão "Simular" | `/mobile/carteira` | `router.push('/mobile/dashboard?tab=patrimonio')` | **Atualiza**: vai para o Construtor |

### Bottom nav proposto

```
[Dashboard] [Transações] [Plano●] [Carteira] [Perfil]
                          ↑ FAB preto (ícone: LineChart ou Compass)
```

- **"Metas" → "Plano"**: a tab central passa a ser o Plano Financeiro Integrado
- Ao tocar no FAB: se a pessoa nunca configurou → abre o Construtor (wizard 4 etapas)
- Se já configurou → abre a tela de **Acompanhamento do Plano** (nova tela de monitoramento)

### Nova tela: Acompanhamento do Plano (`/mobile/plano`)

Quando o plano já existe, esta é a tela que aparece ao tocar no FAB:

```
┌─────────────────────────────────────────────────────┐
│  Plano 2026                          [Editar] [⚙️]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  MARÇO 2026                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │  Renda esperada        R$ 15.000             │  │
│  │  Gastos planejados   − R$ 14.500  ⚠️ IPVA   │  │
│  │  Aporte planejado    − R$  2.500             │  │
│  │  Saldo previsto        − R$ 2.000  ❌        │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  GASTOS vs PLANO (grupos)                           │
│  Casa       ████████░░  R$2.800/R$3.000  93%  ✅   │
│  Alimentação███████████ R$2.700/R$2.500 108%  ⚠️   │
│  Transporte  ████░░░░░░  R$  650/R$1.000  65%  ✅   │
│                                                     │
│  INVESTIMENTOS vs PLANO                             │
│  R$ 1.800 / R$ 2.500 aportados   72%  ⚠️           │
│                                                     │
│  [Ver recibo do ano ↓]   [Editar plano]             │
└─────────────────────────────────────────────────────┘
```

Esta tela **já existe em embrião** como `OrcamentoTab` no dashboard (mostra gastos vs plano). A ideia é evoluí-la para a tela central de acompanhamento, com:
- Contexto do mês atual (saldo previsto)
- Alerta visual para meses com sazonais
- Link para o recibo anual

---

## O problema central (que esta UX resolve)

Hoje o usuário tem dois mundos separados:
- **Plano de Aposentadoria** (`/mobile/personalizar-plano`): define aporte, retorno, projeção de patrimônio — muito bem feito, tem o "recibo" mês-a-mês
- **Metas de Gastos** (`/mobile/budget`): define quanto quer gastar por grupo — mas sem âncora de renda, sem evolução, sem conexão com o quanto sobra para investir

O resultado: a pessoa pode criar um plano de gastos de R$ 20.000/mês ganhando R$ 15.000, e um plano de aposentadoria com aporte de R$ 5.000 — e o app nunca avisa que a conta não fecha.

**A proposta:** Uma tela de construção de plano que começa pela renda e distribui o dinheiro de cima para baixo — gastos → sobra → aporte.

---

## Proposta de fluxo — "Construtor de Plano"

Novo entry point: `/mobile/construir-plano` (ou integrado ao fluxo atual de metas)

### ETAPA 1 — Ponto de partida: sua renda

```
┌─────────────────────────────────────────────────────┐
│  ← Construir Plano                          [1 de 4]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  RENDA                          ─────────────────── │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Renda média mensal                          │   │
│  │                                              │   │
│  │  R$ [    15.000    ]                         │   │
│  │  💡 Quanto você recebe líquido por mês       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  GANHOS EXTRAORDINÁRIOS         ─────────────────── │
│  (13º, bônus, freelance, aluguel...)                │
│                                                     │
│  ┌ Adicionar ganho extraordinário ──────────────┐   │
│  │  Descrição   [13º salário        ]           │   │
│  │  Valor       [R$ 15.000          ]           │   │
│  │  Mês         [Dezembro  ▼]                   │   │
│  │  Recorrência [Anual     ▼]                   │   │
│  │                                              │   │
│  │  ☐ Evoluir valor    5 % ▼ / R$ ▼            │   │
│  │  → Ano 1: R$ 15.000 → Ano 2: R$ 15.750      │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  [+ Adicionar ganho]                                │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Renda total esperada (2026)                 │   │
│  │  R$ 195.000/ano  •  R$ 16.250 média/mês     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│            [Continuar →]                            │
└─────────────────────────────────────────────────────┘
```

**Notas de UX:**
- Ganhos extraordinários: **exatamente o mesmo componente** que já existe para "Aportes Extraordinários" no plano de aposentadoria — mesma UI, mesmo conceito de evolução (% ou R$/ano)
- Preview da renda total anualizada aparece em tempo real embaixo
- Não é obrigatório preencher ganhos extras

---

### ETAPA 2 — Distribuição de gastos (âncora nos dados reais)

```
┌─────────────────────────────────────────────────────┐
│  ← Construir Plano                          [2 de 4]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sua renda: R$ 15.000/mês                           │
│  ┌──────────────────────────────────────────────┐  │
│  │ ████████████████████░░░░░░  R$ 11.200 gastos │  │
│  │                              R$  3.800 livre  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  PLANO DE GASTOS               ─────────────────── │
│  Baseado nos últimos 3 meses                        │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │ 🏠 Casa              R$ 3.200    ← média   │     │
│  │    Meta planejada:  [R$ 3.000]  ✏️         │     │
│  │    ☐ Evoluir valor   5 % ▼ / R$ ▼         │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │ 🍔 Alimentação       R$ 2.800    ← média   │     │
│  │    Meta planejada:  [R$ 2.500]  ✏️         │     │
│  │    ☐ Evoluir valor                         │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │ 🚗 Transporte        R$ 1.100    ← média   │     │
│  │    Meta planejada:  [R$ 1.000]  ✏️         │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │ 💳 Cartão            R$ 2.400    ← média   │     │
│  │    Meta planejada:  [R$ 2.200]  ✏️         │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  [+ Adicionar grupo]                                │
│                                                     │
│  ──────────────────────────────────────────────    │
│  Total planejado:  R$ 10.700/mês                   │
│  Livre para aporte: R$ 4.300/mês  ✅               │
│                                                     │
│            [Continuar →]                            │
└─────────────────────────────────────────────────────┘
```

**Notas de UX:**
- Cada grupo exibe a **média real dos últimos 3 meses** ao lado do campo editável (âncora na realidade)
- Se a pessoa digitar uma meta acima da média: leve aviso amarelo ("R$ 200 acima da sua média")
- **Sem evolução individual por grupo** — todos os gastos crescem pela inflação global (configurada uma única vez, ver seção "Evolução de gastos" abaixo). Gastos sazonais mantêm evolução própria (Etapa 3)
- O saldo livre (renda − gastos) aparece em tempo real na barra superior
- Saldo negativo → barra fica vermelha, botão "Continuar" desabilita com mensagem

---

### ETAPA 3 — Gastos extraordinários

```
┌─────────────────────────────────────────────────────┐
│  ← Construir Plano                          [3 de 4]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  GASTOS SAZONAIS                ─────────────────── │
│  Coisas que você gasta em meses específicos         │
│                                                     │
│  ┌ Adicionar gasto sazonal ─────────────────────┐  │
│  │  Descrição   [IPVA                ]           │  │
│  │  Valor       [R$ 3.800            ]           │  │
│  │  Mês         [Março      ▼]                   │  │
│  │  Grupo       [Carro      ▼]  ← sua categori  │  │
│  │  Recorrência [Anual      ▼]                   │  │
│  │                                               │  │
│  │  ☐ Parcelado   [12] parcelas de [R$ 317]     │  │
│  │    → Distribui de março a fevereiro/27        │  │
│  │                                               │  │
│  │  ☐ Evoluir valor   7 % ▼ / R$ ▼              │  │
│  │  → 2026: R$ 3.800 → 2027: R$ 4.066           │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  Adicionados:                                       │
│  • IPVA — Mar 2026 — R$ 3.800 — Anual  ✏️ 🗑️     │
│  • IPTU — Fev 2026 — R$ 2.200 — Anual  ✏️ 🗑️     │
│  • Matrícula escola — Jan 2027 — R$ 1.500  ✏️ 🗑️  │
│  • Viagem Europa — Jul 2026 — R$ 12.000   ✏️ 🗑️   │
│                                                     │
│  ──────────────────────────────────────────────    │
│  Impacto médio mensal: + R$ 1.625/mês              │
│  (R$ 19.500 no ano, distribuído em 12 meses)       │
│                                                     │
│            [Continuar →]                            │
└─────────────────────────────────────────────────────┘
```

**Notas de UX:**
- Mesmo padrão visual dos ganhos extraordinários (etapa 1) — simetria perfeita
- Campo **Grupo** vincula o gasto sazonal à categoria (aparece no plano de gastos do mês certo)
- **Parcelado**: toggle que substitui "mês único" por "distribuir em N meses" — se IPVA é parcelado em 3x, aparece como R$ 1.267 em março, abril e maio
- **Evoluir**: igual ao padrão já implementado (% ou R$/ano, com preview de 3 anos)
- "Impacto médio mensal" ajuda a pessoa entender quanto dos gastos sazonais pesa no mês médio

---

### ETAPA 4 — Aporte e "recibo" do plano

```
┌─────────────────────────────────────────────────────┐
│  ← Construir Plano                          [4 de 4]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  SEU PLANO FINANCEIRO           ─────────────────── │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Renda mensal média      R$ 15.000          │   │
│  │  Gastos planejados     − R$ 10.700          │   │
│  │  Sazonais (média/mês)  −  R$  1.625         │   │
│  │  ─────────────────────────────────          │   │
│  │  Aporte disponível       R$  2.675 ✅        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Quanto você quer investir por mês?                 │
│                                                     │
│  R$ [   2.500   ] /mês                              │
│  ──────────  slider ──────────                     │
│  [500] [1k] [1,5k] [2k] [2,5k] [máx]              │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │  💡 Com R$ 2.500/mês + seu patrimônio     │     │
│  │  atual de R$ 760.000, você atinge sua     │     │
│  │  meta de aposentadoria em 2038 (12 anos)  │     │
│  │  → Plano de Aposentadoria vinculado ✓     │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  RECIBO 2026 (mês a mês)        ─────────────────── │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Mês    Renda   Gastos  Aporte  Saldo         │  │
│  │ Jan    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Fev    15.000  12.900   2.500    +600  ⚠️ IPTU│  │
│  │ Mar    15.000  14.500   2.500  −2.000  ❌ IPVA│  │
│  │ Abr    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Mai    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Jun    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Jul    15.000  22.700   2.500  −9.200  ❌ Viagem│
│  │ Ago    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Set    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Out    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Nov    15.000  10.700   2.500  +1.800  ✅    │  │
│  │ Dez    30.000  10.700   2.500 +16.800  ✅ 13°│  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ⚠️ 2 meses com saldo negativo (Mar e Jul)         │
│  💡 Use o 13° de Dez para cobrir os negativos      │
│                                                     │
│  RESUMO DO ANO                 ─────────────────── │
│  Renda total:   R$ 195.000                         │
│  Gastos total:  R$ 147.300                         │
│  Aportes total: R$  30.000                         │
│  Saldo ano:     R$  17.700                         │
│                                                     │
│  [Salvar Plano Completo]                            │
└─────────────────────────────────────────────────────┘
```

**Notas de UX:**
- O slider de aporte tem como **teto o saldo disponível médio** (não pode propor mais do que a renda permite em média)
- Se a pessoa insistir em aporte maior: aviso "em X meses do ano seu saldo ficará negativo"
- **Integração com o plano de aposentadoria**: o aporte definido aqui atualiza automaticamente o cenário de aposentadoria (ou pergunta se quer vincular)
- A tabela "Recibo mês a mês" é o equivalente da tabela "Primeiros meses do plano" que já existe no plano de aposentadoria — mesma UI, contexto diferente
- Meses ⚠️ (saldo pequeno) e ❌ (saldo negativo) ficam destacados com cor
- Cada linha anômala explica o porquê (gasto sazonal ou ganho extra)
- **Nota abaixo de cada mês anômalo** — não uma coluna extra, apenas uma linha de contexto cinza

---

## Evolução de gastos — inflação global

**Decisão:** evolução por grupo individual é complexidade desnecessária. O construtor terá um único campo de inflação esperada (padrão: IPCA ~5%), e todos os gastos crescem uniformemente.

```
┌──────────────────────────────────────────────────┐
│  CORREÇÃO ANUAL DOS GASTOS        ─────────────  │
│                                                  │
│  Seus gastos evoluem com a inflação              │
│                                                  │
│  Inflação esperada: [ 5,0 ] % a.a.               │
│                     ←──────────────→             │
│                     2%          10%              │
│                                                  │
│  💡 Padrão: IPCA histórico (~5%). Ajuste se      │
│     seus gastos crescem mais rápido.             │
│                                                  │
│  Exemplo — Gastos de R$ 10.700/mês:              │
│  2026: R$ 10.700  → 2027: R$ 11.235  (+5%)      │
│  2028: R$ 11.797  → 2029: R$ 12.387  (+5%)      │
└──────────────────────────────────────────────────┘
```

Ganhos e gastos sazonais extraordinários **mantêm** o campo de evolução individual (% ou R$/ano) — porque 13º pode não seguir inflação, IPVA pode ter alíquota diferente, etc.

---

## Comportamento do "recibo" quando há parcelamentos

Gasto sazonal IPVA de R$ 3.800 parcelado em 3x:

```
Mar/26: Gastos R$ 11.967  ← + R$ 1.267 (IPVA 1/3)
Abr/26: Gastos R$ 11.967  ← + R$ 1.267 (IPVA 2/3)  
Mai/26: Gastos R$ 11.967  ← + R$ 1.267 (IPVA 3/3)
Jun/26: Gastos R$ 10.700  ← normal, sem parcela
```

Versus à vista:
```
Mar/26: Gastos R$ 14.500  ← + R$ 3.800 (IPVA à vista) ❌
Abr/26: Gastos R$ 10.700  ← normal
```

A pessoa pode escolher e ver o impacto em tempo real na tabela.

---

## Resumo visual — mapa de componentes

```
PersonalizarPlanoFinanceiro (nova tela, ~4 seções)
│
├── Seção 1: Renda
│   ├── Campo renda mensal líquida
│   └── GanhosExtraordinariosEditor (reutiliza o mesmo componente do plano de aposentadoria)
│       └── props: label="Ganho", tipo="credito"
│
├── Seção 2: Gastos por grupo
│   └── GrupoGastoEditor (novo componente)
│       ├── Exibe média 3 meses (vem da API: budget/media-3-meses)
│       ├── Campo meta planejada
│       └── EvoluirValorToggle (novo, reutilizável)
│           └── mesmo padrão do evoluir nos aportes extraordinários
│
├── Seção 3: Gastos sazonais
│   └── GastosExtraordinariosEditor (espelho do GanhosExtraordinarios)
│       ├── props: label="Gasto", tipo="debito"
│       ├── Campo "Grupo" (vincula ao grupo do plano)
│       └── Toggle "Parcelado" + nº de parcelas
│
└── Seção 4: Aporte + Recibo
    ├── Resumo (renda - gastos - sazonais = disponível)
    ├── Slider aporte (máx = disponível médio)
    ├── IntegrationCard → conecta com plano aposentadoria
    └── ReciboPorMes (tabela) ← mesmo padrão do plano-chart.tsx
        └── Mês | Renda | Gastos | Aporte | Saldo | Nota
```

---

## Parcelamento — estratégia e ponte para base_parcelas

**Decisão:** registrar no banco como N linhas em `budget_planning`, com campos de parcela.

### Por que N linhas (não cálculo no frontend)

- O recibo mês-a-mês precisa dos valores por mês no banco para comparar com o realizado
- Parcelas no plano serão a **versão futura** do que `base_parcelas` faz para o realizado: compra parcelada detectada no extrato → parcelas esperadas nos próximos meses
- A ponte futura: se a `base_parcelas` detectar uma parcela de 12x cujas mensalidades futuras ainda não têm entrada no `budget_planning`, o app pode sugerir: "Você tem LOJA 4/12 — quer adicionar as parcelas 5 a 12 no seu plano?"

### Campos novos em `budget_planning`

```python
# Novos campos (nullable — retrocompatível)
is_parcela     = Column(Integer, default=0)        # 0=normal, 1=parcela
parcela_seq    = Column(Integer, nullable=True)     # 1, 2, 3...
parcela_total  = Column(Integer, nullable=True)     # total de parcelas
parcela_ref    = Column(String(100), nullable=True) # "IPVA 2026" (agrupa)
```

### Como aparece na tela de Acompanhamento

```
Mar/26 — Gastos R$ 11.967
  Carro  R$ 8.167  → R$ 6.900 normal + R$ 1.267 IPVA (1/3) ← badge
```

Badge `(1/3)` ao lado do gasto sazonal parcelado, para a pessoa saber que há mais parcelas vindo.

---

## Resumo de componentes reutilizados vs novos

| Componente | Status | Origem |
|-----------|--------|--------|
| `GanhosExtraordinariosEditor` | **Reutilizar** | PersonalizarPlanoLayout.tsx — mesmo componente |
| `GastosExtraordinariosEditor` | **Novo** (espelho) | Mesmo padrão + campo Grupo + toggle Parcelado |
| `EvoluirValorInflacao` | **Novo (simples)** | Slider % único para todos os gastos |
| `ReciboPorMes` | **Reutilizar** | plano-chart.tsx linha 406+ — mesma tabela, colunas diferentes |
| `AcompanhamentoPlano` | **Evoluir** | OrcamentoTab.tsx no dashboard — expandir para tela própria |
| `PersonalizarPlanoLayout` | **Integrar** | Vira Etapa 4+ do Construtor (aporte + projeção) |

---

## API — o que precisa ser criado

| Endpoint | Status | Notas |
|----------|--------|-------|
| `GET /budget/media-3-meses` | **Já existe** | Campo `valor_medio_3_meses` em `budget_planning` — só expor |
| `GET /budget/plano-anual?ano=2026` | **Novo** | Retorna os 12 meses com renda, gastos, aportes, sazonais e saldo por mês |
| `POST /user/financial-profile` | **Novo** | Salva renda mensal + inflação esperada |
| `GET /user/financial-profile` | **Novo** | Carrega dados para preencher o Construtor |
| `POST /budget/planning/bulk-upsert` | **Já existe** | Usado para salvar todas as metas dos 12 meses de uma vez |
