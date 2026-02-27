# UX — Plano Financeiro Integrado (Gastos + Aposentadoria)

**Data:** 26/02/2026  
**Status:** � Decisões tomadas — pronto para Tech Spec  
**Objetivo:** Pensar como seria a experiência completa de construção de plano, integrando renda, gastos, gastos extraordinários, evolução e o "recibo" final

---

## Decisões tomadas

| Questão | Decisão |
|---------|---------|
| Entry point | **Upload como FAB central** — ação primária que alimenta todo o app; "Plano" é aba fixa à direita; "Perfil" move para ⚙️ no header de Início |
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

### Bottom nav proposto — redesenhado

#### Racional da mudança

O nav atual coloca "Metas" como FAB central — mas o usuário **não cria metas diariamente**. O que ele faz mensalmente (e que desencadeia tudo no app) é o **upload do extrato**. O upload alimenta:
- categorização → conciliação do Plano → vínculo de aportes na Carteira

Referências de mercado:
- **Kinvo**: FAB central = "Novo aporte"
- **Warren**: FAB central = "Investir"
- **YNAB**: FAB central = "Adicionar transação"
- **Nubank**: FAB central = "Pix" (ação primária do produto)

Em todos os casos: **o FAB central é a ação primária que mais valor gera**. Para este app, é o upload.

"Perfil" é acessado raramente (configurações, senha) — não merece uma das 5 abas primárias.

#### Nova estrutura

```
[Início] [Transações] [ ⬆️ ] [Plano] [Carteira]
                       ↑
                  FAB elevado
                   "Upload"
```

| Aba | Ícone | Path | O que resolve |
|-----|-------|------|---------------|
| **Início** | 🏠 House | `/mobile/dashboard` | Visão geral do mês: gastos, nudge, alertas, últimas transações |
| **Transações** | ☰ List | `/mobile/transactions` | Lista completa com filtros e busca |
| **⬆️ Upload** | ↑ Upload (FAB) | abre bottom sheet | Ação primária — upload de extrato ou fatura |
| **Plano** | 📊 ChartLine | `/mobile/plano` | Plano Financeiro Integrado (era "Metas") |
| **Carteira** | 👛 Wallet | `/mobile/carteira` | Patrimônio, investimentos, vínculo de aportes |

**Perfil** move para: ⚙️ ícone no canto direito do header de Início.

---

### Arquitetura de navegação — conteúdo e atalhos por tela

#### 🏠 Início (`/mobile/dashboard`)

```
┌─────────────────────────────────────────────────────────┐
│  Fevereiro 2026                 [🔔 2]  [⚙️ Perfil]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌── RESUMO DO MÊS ────────────────────────────────┐   │
│  │  Gasto:   R$ 8.320  /  Plano R$ 9.500   87%  ✅  │   │
│  │  Aporte:  R$ 1.800  /  Plano R$ 2.500   72%  ⚠️  │   │
│  │  Saldo estimado restante:  R$ 1.180              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌── NUDGE (se desvio > R$50 e meses_restantes≥12) ─┐  │
│  │  📉 Você está R$700 abaixo do aporte planejado    │  │
│  │     Isso pode custar 0,8 anos de aposentadoria    │  │
│  │  [Ver impacto no Plano →]                         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌── ALERTAS CONTEXTUAIS ────────────────────────────┐  │
│  │  ⚠️  2 aportes aguardando vínculo   → Carteira   │  │
│  │  📤 Último upload há 31 dias        → Upload      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ÚLTIMAS TRANSAÇÕES                            [Ver →]  │
│  ·  Supermercado Extra     − R$  340   Alimentação      │
│  ·  TED XP Invest          − R$ 1.800  Investimentos ⚠️ │
│  ·  Shell Gas Station      − R$   89   Transporte       │
└─────────────────────────────────────────────────────────┘
```

**Atalhos rápidos de Início:**
- Card de resumo → tap → abre `/mobile/plano` na aba do mês corrente
- Nudge card → tap → abre `/mobile/plano` com o mês destacado
- Badge "aportes" → tap → abre `/mobile/carteira` no modal de vínculo
- Badge "último upload" → tap → abre o bottom sheet de Upload
- Transação com ⚠️ → tap → abre modal de vínculo daquela transação
- "Ver →" últimas transações → abre `/mobile/transactions` com filtro do mês corrente

---

#### 📋 Transações (`/mobile/transactions`)

```
┌─────────────────────────────────────────────────────────┐
│  Transações            [🔍 Buscar]  [Fev 2026 ▼]       │
├─────────────────────────────────────────────────────────┤
│  [Todos]  [Despesa]  [Receita]  [Investimento]          │
├─────────────────────────────────────────────────────────┤
│  26/02 · Supermercado Extra · Alimentação  − R$  340   │
│  25/02 · TED XP Invest · Investimentos  ⚠️ − R$ 1.800  │
│  25/02 · Shell Gas Station · Transporte    − R$   89   │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

**Ações nas transações:**
- Swipe left → opções: Editar grupo, Excluir, Vincular ao portfólio
- Tap em transação com ⚠️ (GRUPO='Investimentos' sem vínculo) → modal de vínculo
- Filtro de mês: date picker de mês/ano
- Filtro de tipo: Todos / Despesa / Receita / Investimento

---

#### ⬆️ Upload (FAB central — bottom sheet)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  O que você quer subir?                                 │
│                                                         │
│  ┌────────────────────────────┐  ┌───────────────────┐  │
│  │  📄 Extrato bancário       │  │  💳 Fatura cartão │  │
│  │  OFX, CSV, PDF             │  │  CSV, PDF         │  │
│  └────────────────────────────┘  └───────────────────┘  │
│                                                         │
│  Último upload: Extrato Bradesco (21/02/2026)           │
│                                                         │
│  [Cancelar]                                             │
└─────────────────────────────────────────────────────────┘
```

**Fluxo pós-upload:**
1. Upload → tela de pré-visualização (tabela de transações detectadas)
2. Confirmar → fases 1–7 executadas no backend
3. Retorna ao Início com toast: `"32 transações processadas · 2 aportes para vincular"`
4. Badges ⚠️ aparecem no Início e na aba Carteira

---

#### 📊 Plano (`/mobile/plano`) — era "Metas"

**Comportamento condicional:**
- Sem plano configurado → abre o Construtor (wizard 4 etapas)
- Com plano → abre Acompanhamento do Plano

```
┌─────────────────────────────────────────────────────────┐
│  Plano 2026                       [Editar] [+ Sazonal]  │
├─────────────────────────────────────────────────────────┤
│  ◀ Fev 2026  ▶ Mar 2026                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Renda        R$ 15.000                          │   │
│  │  Gastos     − R$ 12.800  (R$ 14.500 prev.) ⚠️   │   │
│  │  Aporte     − R$  1.800  (R$  2.500 prev.) ⚠️   │   │
│  │  Saldo          R$    400                    ✅   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  POR GRUPO                                              │
│  Alimentação  ██████████  R$2.700 / R$2.500  108% ⚠️   │
│  Casa         ████████░░  R$2.800 / R$3.000   93% ✅   │
│  Transporte   ████░░░░░░  R$  650 / R$1.000   65% ✅   │
│                                                         │
│  📅 SAZONAIS PREVISTOS                                  │
│  Mar: IPVA R$2.300  ·  Abr: IPTU R$1.800               │
│                                                         │
│  [Ver cashflow anual ↓]                                 │
└─────────────────────────────────────────────────────────┘
```

**Atalhos rápidos de Plano:**
- Tap no grupo → drill-down para `/mobile/budget/[goalId]`
- "Ver cashflow anual" → tabela 12 meses
- Badge de sazonais → editar gasto sazonal
- Nudge no topo (se ativo): shortcut para cálculo de impacto na aposentadoria

---

#### 👛 Carteira (`/mobile/carteira`)

```
┌─────────────────────────────────────────────────────────┐
│  Minha Carteira                                  [🔍]   │
├─────────────────────────────────────────────────────────┤
│  ⚠️  2 aportes aguardando vínculo           [Vincular→] │
│     TED XP R$1.800  ·  PIX BTG R$2.000                 │
├─────────────────────────────────────────────────────────┤
│       PATRIMÔNIO BRUTO    R$  762.143,30                │
│     − IR estimado         R$  −12.450,00                │
│       ══════════════════════════════════                │
│       PATRIMÔNIO LÍQUIDO  R$  749.693,30          ℹ️   │
│                                                         │
│              (donut chart — por tipo de ativo)          │
│                                                         │
│  ATIVOS   R$1.3M    PASSIVOS  −R$530K                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  PRODUTOS (14)                                          │
│  ┌── Apartamento · Snapshot ─────────────────────────┐  │
│  │  R$ 450.000  (digitado Jan/26)         [Atualizar] │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌── PETR4 · Ação · 100 cotas ───────────────────────┐  │
│  │  R$ 4.120  (+7,0%)  ·  IR: isento este mês 🟢     │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌── CDB XP 112% CDI · Fixo ─────────────────────────┐  │
│  │  R$ 28.953  (+1,84%)  ·  IR retido na fonte       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Atalhos rápidos de Carteira:**
- Badge "N aportes" → abre modal de vínculo diretamente
- Tap em produto → detalhe (posição, custo médio, IR, projeção)
- [Atualizar] em Snapshot → form de atualização de valor
- Detalhe de variável → [Registrar venda] → modal de venda/resgate

---

### Mapa de flows principais (happy paths)

```
Upload extrato
    │
    ▼
Confirmar upload (fases 1-7 no backend)
    │
    ├──→ Início: toast "32 transações processadas"
    │
    └──→ Se GRUPO='Investimentos' detectado:
            Início badge ⚠️ "2 aportes aguardando"
            Carteira badge ⚠️
                │
                ▼
            Modal de vínculo (automático ou manual)
                │
                ├──→ track='variavel' (ação/FII/ETF)
                │       Posição + custo médio calculados
                │       IR estimado atualizado
                │
                └──→ track='fixo' (renda fixa)
                        CDI/SELIC acumulado via cache BCB
```

```
Início: nudge "R$700 abaixo do aporte planejado"
    │
    ▼
  [Ver impacto no Plano →]
    │
    ▼
Plano: mês corrente destacado, desvio sinalizado
    │
    ▼
  [Editar plano] → ajustar meta de aporte
```

- **"Metas" → "Plano"**: a tab passou a ser o Plano Financeiro Integrado
- Ao tocar na aba Plano: se sem plano configurado → abre o Construtor (wizard 4 etapas)
- Se já configurado → abre a tela de **Acompanhamento do Plano**

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

## Arquitetura de dados — três camadas

```
CAMADA 1 — REALIZADO (imutável após confirmado)
├── journal_entries    → transações importadas e confirmadas
└── base_parcelas      → tracker de parcelamentos realizados
                         (qtd_pagas cresce a cada upload)
                         ✅ NUNCA recebe projeções

CAMADA 2 — EXPECTATIVAS (nova tabela: base_expectativas)
   Tudo que é esperado para meses futuros. Duas origens:
   A) 'usuario'  → sazonais e rendas declaradas no Construtor de Plano
   B) 'sistema'  → inferido automaticamente a partir de base_parcelas
                   (qtd_parcelas - qtd_pagas = parcelas ainda por vir)

CAMADA 3 — PLANO BASE (alvo mensal recorrente)
└── budget_planning    → meta mensal por grupo (fica como está)
```

`base_parcelas` fica limpo — é registro histórico do que já aconteceu. `base_expectativas` é a camada de projeção.

### Schema: `base_expectativas`

```sql
CREATE TABLE base_expectativas (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,

    -- O quê
    descricao        VARCHAR(200),     -- "IPVA 2026" ou "LOJA AMERICANAS 5/12"
    valor            DECIMAL(10,2),
    grupo            VARCHAR(100),     -- mesmo grupo do budget_planning
    tipo_lancamento  VARCHAR(10),      -- 'debito' | 'credito'

    -- Quando
    mes_referencia   VARCHAR(7) NOT NULL,  -- "2026-05"

    -- Origem
    tipo_expectativa VARCHAR(30) NOT NULL,
    -- 'sazonal_plano'  → usuário declarou no Construtor
    -- 'renda_plano'    → renda extraordinária declarada
    -- 'parcela_futura' → derivada automaticamente de base_parcelas

    origem VARCHAR(20) NOT NULL,
    -- 'usuario' → entrada manual
    -- 'sistema' → gerada automaticamente no upload confirm

    -- Link para base_parcelas (quando tipo='parcela_futura')
    id_parcela    VARCHAR(64),   -- FK → base_parcelas.id_parcela
    parcela_seq   INTEGER,       -- qual parcela é essa (ex: 5)
    parcela_total INTEGER,       -- total (ex: 12)

    -- Conciliação
    status           VARCHAR(20) DEFAULT 'pendente',
    -- 'pendente'   → ainda não chegou no extrato
    -- 'realizado'  → chegou e foi matched automaticamente
    -- 'divergente' → chegou mas valor difere (requer atenção)
    -- 'cancelado'  → usuário cancelou manualmente

    journal_entry_id INTEGER,        -- FK → journal_entries.id (quando realizado)
    valor_realizado  DECIMAL(10,2),  -- valor efetivo (pode diferir do esperado)
    realizado_em     TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (user_id, id_parcela, parcela_seq)  -- evita duplicar parcelas futuras
);
```

### Como parcelas futuras são geradas (Fase 6 do upload confirm)

Hoje o upload confirm tem uma Fase 5 que atualiza `base_parcelas.qtd_pagas`. A Fase 6 (nova) roda logo depois:

```
FASE 5 (existente): atualiza base_parcelas.qtd_pagas e status

FASE 6 (nova — duas partes):

PARTE A — marcar expectativas como realizadas:
  Para cada transação parcelada do upload atual:
    → buscar base_expectativas WHERE id_parcela=X AND parcela_seq=N AND status='pendente'
    → se valor OK (±5%): status = 'realizado', setar journal_entry_id
    → se valor diverge: status = 'divergente', registrar valor_realizado

PARTE B — criar expectativas futuras (até o fim da série):
  Para cada base_parcelas WHERE status='ativa':
    parcelas_a_criar = range(qtd_pagas + 1, qtd_parcelas + 1)  ← TODAS até o fim
    para cada seq em parcelas_a_criar:
      mes_futuro = data_inicio + (seq - 1) meses
      INSERT INTO base_expectativas (
        id_parcela, parcela_seq, parcela_total,
        descricao = f"{estabelecimento_base} {seq}/{qtd_parcelas}",
        valor, grupo, mes_referencia = mes_futuro,
        tipo_expectativa = 'parcela_futura',
        origem = 'sistema', status = 'pendente'
      )
      ON CONFLICT (user_id, id_parcela, parcela_seq) DO NOTHING
```

**Exemplo:** LOJA 4/12 detectada no upload de fevereiro → sistema cria expectativas para parcelas 5, 6, 7, 8, 9, 10, 11 e 12 — todas de uma vez, cada uma no mês correto.

### Conciliação de sazonais declarados pelo usuário

Matching automático (opção escolhida): ao final do upload confirm, para cada transação que **não** é parcela conhecida, tentar match com `base_expectativas WHERE tipo='sazonal_plano'`:

```
critérios para match automático:
  1. mesmo grupo (ou grupo próximo)
  2. mesmo mês de referência
  3. valor dentro de ±10% do esperado

resultado:
  match ok     → status = 'realizado'
  valor diverge→ status = 'divergente' (mostra na tela: "IPVA esperado R$3.800, veio R$3.950")
  sem match    → expectativa fica 'pendente' até o final do mês, vira alerta
```

---

## Budget at risk — forecast vs orçamento por grupo

**Decisão:** dado que temos orçamento planejado (`budget_planning`) e expectativas conhecidas (`base_expectativas`), o app deve mostrar antecipadamente se um mês vai estourar — antes de o mês começar.

### Lógica por (grupo, mês)

```
total_esperado = budget_planning.valor_planejado     ← gasto recorrente do grupo
              + SUM(base_expectativas.valor           ← sazonais + parcelas futuras
                    WHERE grupo=X AND mes=Y
                    AND status IN ('pendente','divergente'))

status_previsao:
  '✅ ok'       → total_esperado ≤ orçamento
  '⚠️ atenção'  → total_esperado ≤ orçamento × 1.2  (até 20% acima)
  '❌ estouro'  → total_esperado > orçamento × 1.2
```

Para o mês atual (em andamento), a projeção usa dado misto:

```
projecao_mes_atual =
    SUM(journal_entries realizados até hoje no mês)   ← real
  + SUM(base_expectativas pendentes do mesmo mês)     ← compromissos conhecidos

→ "Março: R$650 realizados + R$1.267 IPVA esperado = R$1.917 projetado / R$1.000 orçado → ❌ vai estourar"
```

### Como aparece na tela de Acompanhamento

```
┌─────────────────────────────────────────────────────┐
│  Plano 2026  ← mês atual: Março                     │
├─────────────────────────────────────────────────────┤
│  GASTOS vs PLANO                                    │
│                                                     │
│  Casa       ████████░░  R$2.800/R$3.000  93%  ✅   │
│  Alimentação███████████ R$2.700/R$2.500 108%  ⚠️   │
│  Carro       ████░░░░░░  R$  650/R$1.000  65%       │
│              ↑ real      + R$1.267 IPVA esperado    │
│              → projeção: R$1.917 / R$1.000  192% ❌ │
│                                                     │
│  PRÓXIMOS MESES — alertas antecipados               │
│  Abr  ⚠️  Carro: R$2.267 esperado / R$1.000 plano  │
│  Mai  ⚠️  Carro: R$2.267 esperado / R$1.000 plano  │  ← parcelas 3 e 4
│  Jul  ❌  Viagem: R$12.000 esperado / não planejado │
│  Dez  ✅  13º: +R$15.000 esperado                  │
└─────────────────────────────────────────────────────┘
```

A seção "Próximos meses — alertas antecipados" é gerada diretamente de `base_expectativas`, sem nenhum cálculo extra: basta comparar com `budget_planning` do mesmo grupo e mês.

### Graus de confiança da expectativa

| Tipo | Confiança | Exemplo |
|------|-----------|---------|
| Parcela futura (`sistema`) | 🟢 Alta | LOJA 5/12 — valor fixo, mês calculado |
| Sazonal declarado (`usuario`) | 🟡 Média | IPVA — usuário estimou R$3.800 |
| Renda extraordinária | 🟡 Média | 13º — usuário estimou R$15.000 |

Confiança aparece como cor do badge na tela (verde = certo, amarelo = estimado).

---

## Nudge de aposentadoria — impacto de cada desvio no patrimônio futuro

**Conceito:** cada estouro ou economia mensal tem um valor composto até a data de aposentadoria. Mostrar esse número transforma um desvio abstrato ("gastei R$267 a mais") em algo concreto e motivador ("esse estouro vale R$828 a menos na aposentadoria").

Os parâmetros já existem no plano de aposentadoria do usuário: `taxa_retorno_mensal` e `data_aposentadoria`. O cálculo reutiliza isso.

### Fórmula

```
nudge_mes = Δaporte × (1 + taxa_mensal)^meses_restantes

onde:
  Δaporte         = aporte_realizado − aporte_planejado
                    (negativo = estouro → menos dinheiro investido)
  taxa_mensal     = taxa_retorno do plano de aposentadoria (ex: 0.8%/mês ≈ 10% a.a.)
  meses_restantes = meses entre o mês do desvio e a data de aposentadoria
```

**Exemplo concreto:**
- Usuário planeja aposentar em 12 anos (144 meses)
- Taxa: 0,8%/mês
- Março: estouro de R$267 no grupo Carro → aporte foi R$267 menor
- Nudge: `−267 × (1,008)^144 = −267 × 3,10 = −R$828`
- Frase: *"Esse estouro de março vai custar R$828 na sua aposentadoria"*

O sinal é simétrico — economia gera nudge positivo:
- Alimentação: R$300 abaixo do orçamento → `+300 × 3,10 = +R$930` na aposentadoria

### Running acumulado (nudge do ano)

Para o painel de acompanhamento anual, acumula cada mês com seu $n$ correto:

```
nudge_acumulado = Σ (por mês M já encerrado ou em andamento)
                    Δaporte(M) × (1 + taxa)^(meses_aposentadoria − M)
```

Cada mês tem um expoente diferente — desvios de janeiro pesam mais que os de novembro porque têm mais tempo para compostar.

**Exemplo — running de 2026 (até março):**
```
Jan: Δ = +150 (economizou) → +150 × (1,008)^156 = +R$495
Fev: Δ =   −0 (ok)        →   0
Mar: Δ = −267 (estouro)   → −267 × (1,008)^144 = −R$828
──────────────────────────────────────────────────────
Nudge acumulado 2026 até março: −R$333 na aposentadoria
```

### Como aparece na tela

**Por mês (alerta pontual):**
```
┌─────────────────────────────────────────────────────┐
│  Carro  192% do orçamento  ❌ vai estourar           │
│  R$650 real + R$1.267 IPVA esperado = R$1.917       │
│  Estouro: R$917 acima do plano                      │
│                                                     │
│  💸 Isso vale −R$2.842 na sua aposentadoria         │
│     (R$917 × compostos por 144 meses a 0,8%/mês)   │
└─────────────────────────────────────────────────────┘
```

**Running anual (no topo da tela de Acompanhamento):**
```
┌─────────────────────────────────────────────────────┐
│  Plano 2026  ← mês atual: Março                     │
│                                                     │
│  💸 Impacto acumulado na aposentadoria              │
│     Jan–Mar: −R$333  ← estouros pesam mais que economias
│     ████░░░░░░░░░░  Progresso do ano               │
│     [ver detalhe por mês ↓]                         │
├─────────────────────────────────────────────────────┤
│  GASTOS vs PLANO  ...                               │
```

Ou versão positiva quando o usuário está abaixo do orçamento:
```
│  🎯 Impacto acumulado na aposentadoria              │
│     Jan–Mar: +R$1.240  ← você está economizando!   │
```

### O que é necessário para calcular

O backend precisa de dois inputs do plano de aposentadoria:

| Campo | Onde já existe | Uso |
|-------|---------------|-----|
| `taxa_retorno_mensal` | `cenario_aposentadoria` ou `plano_investimento` | expoente base |
| `data_aposentadoria` ou `anos_faltantes` | mesmo modelo | calcula `meses_restantes` por mês |

O endpoint `GET /budget/cashflow?ano=2026` já devolve `delta_aporte` por mês. Basta o frontend (ou o backend) multiplicar pelo fator de composição. Preferível calcular no **backend** para evitar expor a taxa e a data de aposentadoria no cliente desnecessariamente.

### Quando NÃO mostrar

- Usuário não configurou o plano de aposentadoria → nudge não aparece (sem taxa, sem data)
- Data de aposentadoria no passado ou menos de 1 ano → nudge irrelevante, omitir
- Desvio menor que R$50 → sem nudge (ruído)

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
| `GET /budget/cashflow?ano=2026` | **Novo** | Retorna os 12 meses: realizado + expectativas + plano base + saldo projetado + status por grupo + `nudge_aposentadoria` por mês e acumulado |
| `POST /user/financial-profile` | **Novo** | Salva renda mensal + inflação esperada |
| `GET /user/financial-profile` | **Novo** | Carrega dados para preencher o Construtor |
| `POST /budget/planning/bulk-upsert` | **Já existe** | Salva metas dos 12 meses de uma vez |
| `POST /budget/expectativas` | **Novo** | Salva sazonais/rendas declaradas pelo usuário |
| `GET /budget/expectativas?mes=2026-04` | **Novo** | Lista expectativas do mês com status de conciliação |

---

## Módulo 2 — Budget ↔ Patrimônio (conexão de aportes)

### Problema

Quando o usuário faz "TED XP INVEST R$5.000" e sobe o extrato, o app sabe que gastou R$5.000 com investimentos — mas **não sabe o que ele comprou**. Resultado:
- `investimentos_historico.aporte_mes` fica zero → rentabilidade calculada incorretamente (aparece que rendeu R$5.000, quando na verdade foi o aporte)
- Impossível calcular custo médio de ações
- Impossível comparar renda fixa com o CDI contratado

### 3 tracks de produto

Cada produto do portfólio tem um `track` que define como seu valor é calculado:

| Track | Tipo de produto | Como o valor é apurado |
|-------|----------------|----------------------|
| `snapshot` | Imóvel, FGTS, Previdência, Conta corrente | Usuário digita o valor mensalmente. `rendimento = Δvalor - aportes` |
| `fixo` | CDB, LCI, LCA, Tesouro Direto, Debentures | Sistema calcula via CDI/IPCA acumulado real (API Bacen). `valor_atual = capital × Π(1 + cdi_dia)` |
| `variavel` | Ações, FIIs, ETFs, BDRs | Sistema busca cotação diária (brapi). `valor_atual = posição × preço_dia`. Custo médio ponderado das compras |

### UX — Badge de aportes pendentes

Imediatamente após um upload que contenha `GRUPO='Investimentos'`:

```
┌─────────────────────────────────────────────────────┐
│  Minha Carteira                            🔍       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚠️  2 aportes aguardando vínculo         [Vincular →] │
│     TED XP R$5.000 · PIX BTG R$2.000               │
│                                                     │
│         MEU PORTFÓLIO                              │
│            R$ 1.9M                                  │
│            7 tipos                                  │
│         (donut chart)                               │
└─────────────────────────────────────────────────────┘
```

O badge aparece **somente** enquanto houver `journal_entries` com `GRUPO='Investimentos'` sem `investimentos_transacoes` vinculado. Some ao vincular todos.

### UX — Match automático (produto único detectado)

Quando o `Estabelecimento` contém o `texto_match` de exatamente 1 produto do portfólio:

```
┌─────────────────────────────────────────────────────┐
│  Aporte detectado                               [✕] │
├─────────────────────────────────────────────────────┤
│  TED XP RENDA FIXA LTDA                            │
│  R$ 1.150,00  ·  15/02/2026                        │
│                                                     │
│  Parece que é um aporte em:                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  💰 CDB XP 112% CDI                          │  │
│  │     Renda Fixa · Liquidez diária             │  │
│  │     Saldo atual: R$ 28.430                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  [Não é esse produto]    [✅ Confirmar vínculo]     │
└─────────────────────────────────────────────────────┘
```

### UX — Modal de vínculo manual

Quando há 0 ou N matches (usuário escolhe "Não é esse produto" ou match falhou):

```
┌─────────────────────────────────────────────────────┐
│  Vincular aporte ao portfólio              [✕]      │
├─────────────────────────────────────────────────────┤
│  TED XP INVEST                                      │
│  R$ 5.000,00  ·  15/02/2026                        │
│                                                     │
│  O que você fez com esse dinheiro?                 │
│  Pode dividir em vários produtos ↓                 │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  PETR4 · Ação · 100 cotas × R$38,50         │  │
│  │  Subtotal: R$ 3.850,00              [✕ rem.] │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  CDB XP 112% CDI · Renda Fixa               │  │
│  │  Subtotal: R$ 1.150,00              [✕ rem.] │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  [+ Adicionar produto]                             │
│                                                     │
│  Total vinculado: R$ 5.000 / R$ 5.000  ✅          │
│                                                     │
│  [Cancelar]              [Confirmar vínculo]        │
└─────────────────────────────────────────────────────┘
```

**Regras do modal:**
- Deve somar 100% do valor da transação para habilitar "Confirmar"
- Produto pode ser existente no portfólio ou novo (abre sub-modal de criação)
- Para ações/FIIs (`track='variavel'`): campos extras aparecem → `Ticker`, `Qtd de cotas`, `Preço por cota`
- Para renda fixa (`track='fixo'`): campos extras → `Indexador` (CDI/IPCA/SELIC/Prefixado), `Taxa %`, `Vencimento` (ou "Liquidez diária")
- Para snapshot: só o valor (não tem campos extras)

### UX — Detalhes extras por tipo de produto (dentro do modal)

**Track `variavel` — Ações, FIIs, ETFs:**
```
┌──────────────────────────────────────────────────────┐
│  Produto: [PETR4 — Petrobras PN        ▼] (busca)   │
│  Quantidade de cotas: [___100___]                    │
│  Preço por cota:      [R$ 38,50_____]                │
│  Subtotal calculado:   R$ 3.850,00   ✅              │
└──────────────────────────────────────────────────────┘
```
O ticker serve para busca de cotação diária no brapi e custo médio histórico.

**Track `fixo` — Renda fixa:**
```
┌──────────────────────────────────────────────────────┐
│  Produto: [CDB XP 112% CDI            ▼]            │
│                                                      │
│  Tipo:  [○ Pré-fixado]  [◉ Pós-fixado]               │
│                                                      │
│  ── PÓS-FIXADO ───────────────────────────────────  │
│  Indexador: [CDI                       ▼]            │
│             CDI ─ SELIC ─ IPCA ─ IGPM ─ INCC          │
│             IPCA+X ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│  Taxa: [112___] % do CDI                             │
│     (112% CDI | IPCA + 6,5% | 100% SELIC)           │
│                                                      │
│  ── PRÉ-FIXADO (quando selecionado) ─────────────   │
│  Taxa: [13,50_] % a.a.                               │
│  (capitalização diária pela taxa nominal anual)       │
│                                                      │
│  Vencimento: [dd/mm/aaaa]  ou [☑ Liquidez diária]   │
│  Subtotal: R$ 1.150,00                               │
└──────────────────────────────────────────────────────┘
```

**Regras de exibição do campo Taxa:**
- CDI / SELIC: exibe como "% do indicador" (ex: 112% CDI, 100% SELIC)
- IPCA / IGPM / INCC: exibe como "+ X% a.a." (ex: IPCA + 6,5%)
- IPCA+X: idem, com label explicativo "Inflação + spread"
- Pré-fixado: exibe como "% a.a. (pré-fixado)"

### UX — Venda / Resgate de ativo

O modal de vínculo (e o detalhe do produto) permitem registrar **vendas e resgates** além de aportes. O fluxo transacional concilia os dois casos.

**Seleção do tipo da operação:**
```
┌───────────────────────────────────────────────────┐
│  O que aconteceu com esse dinheiro?         [x]   │
├───────────────────────────────────────────────────┤
│  [◉ Aporte / Compra]   [○ Venda / Resgate]         │
│                                                     │
│  ── VENDA / RESGATE (quando selecionado) ────────   │
│  Produto: [PETR4 — Petrobras PN        ▼]          │
│  Quantidade vendida: [___100___] cotas              │
│  Preço de venda: [R$ 41,20________]                 │
│  Valor bruto:    R$ 4.120,00  (autocalculado)      │
│                                                     │
│  Para onde foi o dinheiro?                         │
│  [◉ Caiu na minha conta bancária]                  │
│  [○ Ficou na corretora (esperando oportunidade)]   │
│                                                     │
│  IR retido (opcional): [R$ 0,00_______]             │
│    (informe se a corretora já descontou o IR)      │
│                                                     │
│  [Cancelar]         [Registrar venda]               │
└───────────────────────────────────────────────────┘
```

**Quando destino = "Ficou na corretora":**
- Sistema cria automaticamente um produto `track='saldo_corretora'` (ex: "Caixa — XP Investimentos") ou incrementa o saldo existente
- Produto aparece na carteira com badge "💵 Disponível" e sem cálculo de rentabilidade
- Usuário pode vincular futuros aportes a este saldo como origem (feature de fase 2)

**Quando destino = "Conta bancária":**
- Se o extrato já foi subido: o crédito correspondente pode ser conciliado via `journal_entry_id`
- Badge de venda some do produto e posição é atualizada

### UX — Tela de patrimônio com tracks ativos

Na tela `/mobile/carteira`, ao selecionar um produto:

**Produto `variavel` (PETR4 — Ação):**
```
PETR4 · Petrobras PN · Ação
─────────────────────────────────────────────────────
 Posição atual:      100 cotas
 Custo médio:        R$ 38,50
 Preço hoje:         R$ 41,20  (atualizado 26/02/2026 17h)
 Valor atual:        R$ 4.120,00
─────────────────────────────────────────────────────
 Resultado:          + R$ 270,00  (+7,0%)
 IR: Ação · 15%       R$  40,50  do ganho
     🟢 Isento este mês  (vendas R$0 < R$20k)  ← ou
     🔴 Não isento       (vendas R$22k > R$20k)
 Valor líquido est.:    R$ 4.079,50
─────────────────────────────────────────────────────
 Aportes vinculados: 2  [ver histórico]  [Registrar venda]
```

**Produto `variavel` (MXRF11 — FII):**
```
MXRF11 · Maxi Renda FII · Fundo Imobiliário
─────────────────────────────────────────────────────
 Posição atual:      500 cotas
 Custo médio:        R$ 10,20
 Preço hoje:         R$ 10,85  (+6,4%)
 Valor atual:        R$ 5.425,00
─────────────────────────────────────────────────────
 Resultado:          + R$ 325,00  (+6,4%)
 IR: FII · 20%        R$  65,00  — sem isenção de R$20k
 Valor líquido est.:    R$ 5.360,00
─────────────────────────────────────────────────────
 Aportes vinculados: 1  [ver histórico]  [Registrar venda]
```

**Produto `fixo` (CDB 112% CDI — Pós-fixado):**
```
CDB XP · Renda Fixa · Pós-fixado · Liquidez diária
─────────────────────────────────────────────────────
 Capital aplicado:   R$ 28.430,00
 Indexador:         112% CDI  (pós-fixado)
 CDI acumulado:      +1,84% (Jan–Fev 2026, fonte: Bacen)
 Valor estimado:     R$ 28.953,13
─────────────────────────────────────────────────────
 Rentabilidade:      + R$  523,13  (+1,84% efetivo × 112%)
 IR: Retido na fonte · estimativa: 15% (> 720 dias)
     Não entra no IR estimado do portfólio
─────────────────────────────────────────────────────
 Aportes vinculados: 3  [ver histórico]  [Registrar resgate]
```

**Produto `fixo` (LCA 13,5% a.a. — Pré-fixado):**
```
LCA Banco BTG · Renda Fixa · Pré-fixado · Vence 15/01/2027
─────────────────────────────────────────────────────
 Capital aplicado:   R$ 10.000,00
 Regime:            13,5% a.a. (pré-fixado)
 Dias decorridos:    220 diasúteis (aprox.)
 Valor estimado:     R$ 10.790,00
─────────────────────────────────────────────────────
 Rentabilidade:      + R$  790,00  (+7,9% em 220 DU)
 Projeção ao vencer: R$ 11.350,00
 IR: Retido na fonte · estimativa: 17,5% (361–720 dias)
─────────────────────────────────────────────────────
 Aportes vinculados: 1  [ver histórico]  [Registrar resgate]
```

**Produto `saldo_corretora` (Caixa XP):**
```
💵 Caixa — XP Investimentos · Disponível
─────────────────────────────────────────────────────
 Saldo:              R$ 3.850,00
 Origem:            Venda PETR4 em 15/02/2026
 Rentabilidade:      N/A (dinheiro à vista)
 IR estimado:        R$ 0 (não há rendimento)
─────────────────────────────────────────────────────
 [Registrar novo aporte com este saldo]
```

### UX — Resumo do portfólio com IR estimado

No topo da tela de Carteira (após o donut):

```
┌─────────────────────────────────────────────────────┐
│  R$ 759.693,30   Patrimônio Líquido (bruto)         │
│  −R$  12.450,00  IR estimado (ganho de capital)*    │
│  ═══════════════                                    │
│  R$ 747.243,30   Patrimônio líquido após IR est.    │
│                                                     │
│  * Estimativa sobre ações/FIIs. IR de renda fixa    │
│    já retido na fonte. Não considera isenção de     │
│    R$20k/mês ou day trade.                          │
└─────────────────────────────────────────────────────┘
```

### Fontes de dados externas

| Dado | Fonte | Frequência | Custo |
|------|-------|-----------|-------|
| CDI diário | [API BCB série 4389](https://api.bcb.gov.br/dados/serie/bcdata.sgs.4389/dados) | 1x/dia | Gratuito |
| SELIC diária | [API BCB série 11](https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados) | 1x/dia | Gratuito |
| IPCA mensal | [API BCB série 433](https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados) | 1x/mês | Gratuito |
| IGPM mensal | [API BCB série 189](https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados) | 1x/mês | Gratuito |
| INCC mensal | [API BCB série 192](https://api.bcb.gov.br/dados/serie/bcdata.sgs.192/dados) | 1x/mês | Gratuito |
| Cotação ações/FIIs | [brapi.dev](https://brapi.dev) | 1x/dia (18h) | Gratuito (15k req/mês) |

Todos os dados ficam em cache local na tabela `market_data_cache` — nenhuma chamada externa no request do usuário.

---

## Upload Redesign + Jornada do Novo Usuário

> **Contexto:** O upload é a ação mais importante do app. Tudo nasce dele — budget, plano, vínculo de aportes. Por isso, remover qualquer fricção do fluxo de upload é prioridade máxima. Esta seção cobre 4 temas: (1) detecção automática, (2) multi-arquivo, (3) import de dados históricos e (4) jornada completa do novo usuário.

---

### Tema 1 — Detecção automática de arquivo (Smart Detection)

#### Problema atual

O usuário abre a tela de upload e enfrenta um formulário vazio: banco, tipo de conta, período. Ele tem que preencher tudo antes de poder escolher o arquivo. Isso cria fricção desnecessária — o arquivo em si já tem todas essas informações.

#### Novo fluxo

```
[Usuário drop ou seleciona arquivo]
         ↓
[Backend analisa o arquivo em < 2s]
         ↓
[Card de detecção exibido com confiança por campo]
         ↓
[Usuário confirma (1 clique) ou edita campos incertos]
         ↓
[Processar]
```

#### Sinais de detecção (por prioridade)

| Sinal | Exemplo | Confiança |
|-------|---------|-----------|
| Formato OFX — tags `BANKID`, `ACCTTYPE`, `DTSTART/DTEND` | `BANKID:237` → Bradesco | 🟢 Alta |
| Nome do arquivo — padrões conhecidos | `extrato-bradesco-jan-2026.csv` | 🟢 Alta |
| Cabeçalho CSV — colunas específicas por banco | `"Data","Histórico","Valor"` → Bradesco | 🟢 Alta |
| Conteúdo — primeiras linhas com padrão de data/valor | detecta período automaticamente | 🟡 Média |
| Histórico do usuário — último upload deste banco | Bradesco sempre conta corrente | 🟡 Média |
| Extensão do arquivo | `.ofx` → extrato, `.pdf` → fatura | 🔴 Baixa |

**Banco de fingerprints dos processadores:**

```python
FINGERPRINTS = {
    "bradesco_extrato_csv": {
        "extensao": ".csv",
        "colunas_obrigatorias": ["Data", "Histórico", "Valor"],
        "banco": "Bradesco",
        "tipo": "extrato",
        "conta": "corrente",
    },
    "nubank_fatura_csv": {
        "extensao": ".csv",
        "colunas_obrigatorias": ["date", "title", "amount"],
        "banco": "Nubank",
        "tipo": "fatura",
    },
    "itau_extrato_xls": {
        "extensao": ".xls",
        "banco": "Itaú",
        "tipo": "extrato",
    },
    "btg_extrato_csv": {
        "extensao": ".csv",
        "colunas_obrigatorias": ["Data", "Descrição", "Valor"],
        "banco": "BTG",
        "tipo": "extrato",
    },
    # ...
}
```

#### UX — Card de detecção por arquivo

**Alta confiança (≥ 85% campos detectados):**

```
┌─────────────────────────────────────────────────────────┐
│  📄 extrato-bradesco-jan-2026.csv                       │
│                                                         │
│  ✅ Banco:          Bradesco                            │
│  ✅ Tipo:           Extrato bancário (Conta Corrente)   │
│  ✅ Período:        Janeiro 2026  (01/01 – 31/01)       │
│  ✅ Transações:     47 detectadas em pré-análise        │
│                                                         │
│  [✏️ Editar]                [✅ Confirmar e processar]  │
└─────────────────────────────────────────────────────────┘
```

**Confiança parcial (50–84%):**

```
┌─────────────────────────────────────────────────────────┐
│  📄 extrato_jan.csv                          ⚠️ Revisar │
│                                                         │
│  ✅ Banco:          Bradesco  (detectado pelo conteúdo)  │
│  ✅ Tipo:           Extrato bancário                    │
│  ❓ Período:        Não detectado automaticamente       │
│     → [Selecionar período]                              │
│                                                         │
│  [✏️ Editar]            [✅ Confirmar e processar]      │
└─────────────────────────────────────────────────────────┘
```

**Arquivo não reconhecido (< 50%):**

```
┌─────────────────────────────────────────────────────────┐
│  📄 arquivo.csv                           ❌ Não reconhecido │
│                                                         │
│  Não conseguimos identificar este arquivo.              │
│  Preencha as informações abaixo:                        │
│                                                         │
│  Banco: [____________] Tipo: [Extrato ▼]               │
│  Período: [MM/AAAA]                                     │
│                                                         │
│  [Cancelar]                [✅ Processar assim mesmo]   │
└─────────────────────────────────────────────────────────┘
```

**Alerta de duplicata:**

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️  Arquivo possivelmente duplicado                    │
│                                                         │
│  Bradesco Conta Corrente — Janeiro 2026                 │
│  já foi carregado em 15/01/2026                         │
│  (47 transações idênticas detectadas)                   │
│                                                         │
│  [Cancelar]              [Carregar de qualquer forma]   │
└─────────────────────────────────────────────────────────┘
```

---

### Tema 2 — Upload de múltiplos arquivos

#### Por que importa

Um novo usuário com 12 meses de extratos precisa fazer 12 uploads separados hoje. No novo fluxo, ele dropa tudo de uma vez. A vantagem vai além da conveniência: ao processar 12 meses juntos, a classificação em lote é exponencialmente mais eficiente — o usuário classifica **estabelecimentos únicos**, não transações.

**Exemplo:** 12 meses de extrato → 1.247 transações → apenas 73 estabelecimentos únicos. Classificar 73 = tudo classificado.

#### UX — Tela de multi-upload

**Estado 1 — Drop zone vazia:**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│         ┌───────────────────────────────┐              │
│         │                               │              │
│         │   📁 Arraste seus arquivos    │              │
│         │      aqui, ou clique          │              │
│         │                               │              │
│         │  OFX · CSV · XLS · PDF        │              │
│         └───────────────────────────────┘              │
│                                                         │
│  Pode subir vários arquivos de uma vez!                 │
│  Extratos e faturas de bancos diferentes — tudo junto.  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Estado 2 — Analisando (files dropados, backend detectando):**

```
┌─────────────────────────────────────────────────────────┐
│  4 arquivos detectados                     [+ Adicionar] │
│                                                         │
│  ⏳ extrato-bradesco-jan-2026.csv   analisando...       │
│  ⏳ extrato-bradesco-fev-2026.csv   analisando...       │
│  ⏳ nubank-fatura-jan-2026.csv      analisando...       │
│  ⏳ nubank-fatura-fev-2026.csv      analisando...       │
└─────────────────────────────────────────────────────────┘
```

**Estado 3 — Todos analisados, pronto para processar:**

```
┌─────────────────────────────────────────────────────────┐
│  4 arquivos prontos                        [+ Adicionar] │
│                                                         │
│  ✅ Bradesco Extrato  Jan/26  47 transações             │
│  ✅ Bradesco Extrato  Fev/26  52 transações             │
│  ✅ Nubank Fatura     Jan/26  34 transações             │
│  ✅ Nubank Fatura     Fev/26  29 transações             │
│     ─────────────────────────────────────               │
│     Total: 162 transações em 4 arquivos                 │
│                                                         │
│  ⚠️  Bradesco Extrato Mar/26  já foi carregado antes    │
│     [Remover] [Incluir mesmo assim]                     │
│                                                         │
│              [Processar todos →]                        │
└─────────────────────────────────────────────────────────┘
```

**Estado 4 — Processando:**

```
┌─────────────────────────────────────────────────────────┐
│  Processando seus arquivos...                           │
│                                                         │
│  ✅ Bradesco Extrato  Jan/26   47 transações ✓          │
│  🔄 Bradesco Extrato  Fev/26   processando...  45%      │
│  ⏳ Nubank Fatura     Jan/26   aguardando...            │
│  ⏳ Nubank Fatura     Fev/26   aguardando...            │
└─────────────────────────────────────────────────────────┘
```

**Estado 5 — Concluído:**

```
┌─────────────────────────────────────────────────────────┐
│  🎉  162 transações processadas!                        │
│                                                         │
│  ✅ Bradesco Extrato  Jan/26   47 transações            │
│  ✅ Bradesco Extrato  Fev/26   52 transações            │
│  ✅ Nubank Fatura     Jan/26   34 transações            │
│  ✅ Nubank Fatura     Fev/26   29 transações            │
│                                                         │
│  📋 73 estabelecimentos para classificar                │
│     (classifique 1 vez → aplica em todas as ocorrências)│
│                                                         │
│  💰 3 aportes aguardando vínculo                        │
│                                                         │
│  [Classificar estabelecimentos →]                       │
└─────────────────────────────────────────────────────────┘
```

#### Fluxo de classificação em lote (pós-upload)

Em vez de mostrar as 162 transações individualmente, agrupa por estabelecimento com frequência:

```
┌─────────────────────────────────────────────────────────┐
│  Classifique os estabelecimentos                        │
│  73 únicos  ·  162 transações totais                    │
│                                            [Salvar tudo]│
├─────────────────────────────────────────────────────────┤
│  Uber                                  34x  R$ 1.245    │
│  Grupo: [Transporte ▼]                       [✅ Salvar] │
├─────────────────────────────────────────────────────────┤
│  iFood                                 28x  R$   890    │
│  Grupo: [Alimentação ▼]                      [✅ Salvar] │
├─────────────────────────────────────────────────────────┤
│  TED XP INVESTIMENTOS                   3x  R$ 9.000   │
│  Grupo: [Investimentos ▼]                    [✅ Salvar] │
├─────────────────────────────────────────────────────────┤
│  Mercado Extra                         12x  R$ 2.100    │
│  Grupo: [Alimentação ▼]                      [✅ Salvar] │
├─────────────────────────────────────────────────────────┤
│  ...  (69 outros)                                       │
└─────────────────────────────────────────────────────────┘
```

- Cada decisão é salva em `base_marcacoes` → futuro upload já reconhece
- Sugestões automáticas baseadas no histórico (Uber → Transporte já foi classificado antes)
- "Salvar tudo" aplica as sugestões automáticas para os não-editados

---

### Tema 3 — Import de dados históricos (planilha própria)

#### Quem usa

Usuários que já têm anos de dados organizados no Excel/Google Sheets e não querem reclassificar tudo. Eles querem importar o histórico já tratado, mantendo os grupos que já deram ao longo do tempo.

#### Três modos de entrada

| Modo | Quando usar |
|------|------------|
| **Upload de extrato** (padrão) | Arquivo bancário em formato nativo (OFX, CSV do banco) |
| **Import de planilha** (novo) | Usuário tem seus dados organizados no Excel/Sheets |
| **Inserção manual** (futuro) | Cadastro de transações avulsas |

#### UX — Fluxo de import de planilha

**Passo 1 — Escolha o modo:**

```
┌─────────────────────────────────────────────────────────┐
│  O que você quer subir?                                 │
│                                                         │
│  ┌────────────────────┐  ┌───────────────────────────┐  │
│  │  📄 Extrato        │  │  📊 Minha planilha        │  │
│  │  bancário          │  │  de dados                 │  │
│  │                    │  │                           │  │
│  │  OFX, CSV do       │  │  Excel, Google Sheets     │  │
│  │  seu banco         │  │  já organizados            │  │
│  └────────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Passo 2 — Guia de preparação (modo planilha):**

```
┌─────────────────────────────────────────────────────────┐
│  📊 Import de dados históricos                     [✕]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ① Baixe nosso template                                 │
│    [⬇️ Download template.xlsx]  [⬇️ Download template.csv] │
│                                                         │
│  ② Preencha com seus dados                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Colunas obrigatórias:                             │ │
│  │  data       DD/MM/YYYY   ex: 15/01/2026            │ │
│  │  descricao  texto        ex: Supermercado Extra     │ │
│  │  valor      número       ex: -350.00 (negativo=gasto)│ │
│  │                                                    │ │
│  │  Colunas opcionais (já preenchidas = menos trabalho):│ │
│  │  grupo      texto        ex: Alimentação           │ │
│  │  conta      texto        ex: Bradesco              │ │
│  │  cartao     texto        ex: Nubank                │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ③ Suba o arquivo preenchido                            │
│    [📁 Escolher arquivo]                                │
│                                                         │
│  [Dúvidas? Ver guia completo ↓]                         │
└─────────────────────────────────────────────────────────┘
```

**Passo 3 — Validação pré-upload:**

```
┌─────────────────────────────────────────────────────────┐
│  Validando seu arquivo...                               │
├─────────────────────────────────────────────────────────┤
│  ✅ 2.847 linhas encontradas                            │
│  ✅ Colunas obrigatórias: data, descricao, valor        │
│  ✅ Coluna opcional: grupo (preenchida em 94% das linhas)│
│  ⚠️  87 linhas com valor zerado → serão ignoradas       │
│  ⚠️  12 linhas com data inválida → serão ignoradas      │
│                                                         │
│  Período detectado: Jan/2024 → Dez/2025 (2 anos)       │
│                                                         │
│  Preview (primeiras 5 linhas):                          │
│  DATA        DESCRIÇÃO              VALOR    GRUPO      │
│  01/01/2024  Supermercado Extra    -350.00   Alimentação│
│  02/01/2024  Uber                   -28.50   Transporte │
│  02/01/2024  TED XP INVESTIMENTOS -5000.00  Investimentos│
│  03/01/2024  Salário              15000.00   Receita    │
│  04/01/2024  Netflix               -55.90   Lazer      │
│                                                         │
│  [Voltar e corrigir]     [Importar 2.748 transações →]  │
└─────────────────────────────────────────────────────────┘
```

**Passo 4 — Processamento simplificado:**

O import de planilha pula as fases de detecção/parsing (os dados já são estruturados). O processo é:

```
Importação de planilha
1. Validar formato e colunas
2. Gerar IdTransacao para deduplicação
3. Mapear grupos → base_marcacoes existentes
   - Se grupo preenchido e existe → aceitar diretamente
   - Se grupo preenchido mas não existe → criar novo grupo (confirmar com usuário)
   - Se grupo vazio → entra na tela de classificação
4. Inserir em journal_entries
5. Atualizar base_marcacoes (novos padrões aprendidos)
6. Detectar transações de investimento (GRUPO='Investimentos') → fila de vínculo
```

**Resultado pós-import:**

```
┌─────────────────────────────────────────────────────────┐
│  🎉  2.748 transações importadas!                       │
│                                                         │
│  ✅ 2.587 já classificadas (94%)  — grupo preenchido    │
│  📋 161 precisam de classificação                       │
│                                                         │
│  📅 Cobrindo: Jan/2024 → Dez/2025 (2 anos de dados)    │
│                                                         │
│  💰 23 aportes aguardando vínculo com investimentos     │
│                                                         │
│  [Classificar 161 restantes →]   [Ir para o Dashboard] │
└─────────────────────────────────────────────────────────┘
```

#### Grupos desconhecidos — confirmar antes de criar

```
┌─────────────────────────────────────────────────────────┐
│  Grupos novos detectados na planilha                    │
│                                                         │
│  Encontramos grupos que não existem no app.             │
│  O que quer fazer com eles?                             │
│                                                         │
│  "Saúde"          → [Criar como novo grupo] [Mapear →▼]│
│  "Moradia"        → [Criar como novo grupo] [Mapear →▼]│
│  "Educação"       → ✅ já existe no app                 │
│                                                         │
│  [Confirmar e importar]                                 │
└─────────────────────────────────────────────────────────┘
```

---

### Tema 4 — Jornada do novo usuário

#### Premissa

O app sem dados é uma tela vazia. A jornada do novo usuário precisa responder 3 perguntas:
1. **O quê?** — o que o app faz (promessa em 1 frase)
2. **Por onde?** — como começar sem se perder
3. **Por quê agora?** — o que o usuário ganha ao colocar dados imediatamente

#### Fluxo de onboarding (telas)

**Tela 1 — Welcome:**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              [Ilustração: dashboard vivo]               │
│                                                         │
│  Bem-vindo ao FinUp                                     │
│                                                         │
│  Conecte seus gastos reais                              │
│  ao seu futuro financeiro.                              │
│                                                         │
│  Suba seus extratos bancários, e o app                  │
│  cuida do resto — classificação, plano                  │
│  e acompanhamento do patrimônio.                        │
│                                                         │
│           [Vamos começar →]                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Tela 2 — Escolha o ponto de partida:**

```
┌─────────────────────────────────────────────────────────┐
│  Como você quer começar?                                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  📤  Subir meus extratos bancários              │   │
│  │      Recomendado para começar do zero           │   │
│  │      OFX, CSV, XLS — detectamos automaticamente │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  📊  Já tenho minha planilha organizada         │   │
│  │      Importe seus dados históricos              │   │
│  │      com grupos já preenchidos                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  🔍  Quero explorar primeiro                    │   │
│  │      Ver como funciona com dados de exemplo     │   │
│  │      Adiciono meus dados depois                 │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Path A — Subir extratos (primeiro upload guiado):**

```
┌─────────────────────────────────────────────────────────┐
│  Suba seu primeiro extrato                      Passo 1/2│
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │   📁 Arraste o arquivo aqui                       │  │
│  │      ou toque para selecionar                     │  │
│  │                                                   │  │
│  │   Formatos aceitos:                               │  │
│  │   OFX · CSV (Bradesco, Nubank, BTG, XP...)       │  │
│  │   XLS · PDF                                       │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  💡 Dica: pode subir vários meses de uma vez!           │
│                                                         │
│  Quanto mais dados, mais preciso fica o seu plano.      │
└─────────────────────────────────────────────────────────┘
```

Após primeiro upload + classificação → celebração:

```
┌─────────────────────────────────────────────────────────┐
│  🎉 Incrível! Seus dados estão no app!                  │
│                                                         │
│  47 transações carregadas                               │
│  Janeiro 2026  ·  Bradesco Conta Corrente               │
│                                                         │
│  Próximos passos (leva 5 min):                          │
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │  ✅ 1. Subiu seu primeiro extrato              │    │
│  │  ⬜ 2. Criar seu Plano Financeiro              │    │
│  │  ⬜ 3. Adicionar investimentos                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  [Criar meu Plano agora →]   [Ver minhas transações]   │
└─────────────────────────────────────────────────────────┘
```

**Path B — Import de planilha:** vai direto para o fluxo do Tema 3.

**Path C — Modo exploração:**
- Carrega dataset de exemplo (persona fictícia: 6 meses de dados, perfil classe média)
- Banner fixo no topo de todas as telas: `"Modo demonstração · [Adicionar meus dados reais]"`
- Qualquer ação destrutiva (editar, deletar) → aviso de que é dados de exemplo

#### Empty states por tela

**Início — sem dados:**

```
┌─────────────────────────────────────────────────────────┐
│  Início                                     [⚙️ Perfil] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         [Ilustração: gráfico vazio animado]             │
│                                                         │
│  Seu painel financeiro está aguardando                  │
│  seus dados reais.                                      │
│                                                         │
│  Suba um extrato bancário para começar a               │
│  entender para onde vai o seu dinheiro.                 │
│                                                         │
│  [📤 Subir primeiro extrato]                            │
│                                                         │
│  ou  [Ver como funciona →] (modo demo)                  │
└─────────────────────────────────────────────────────────┘
```

**Transações — sem dados:**

```
┌─────────────────────────────────────────────────────────┐
│  Transações                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         [Ilustração: lista vazia]                       │
│                                                         │
│  Nenhuma transação ainda.                               │
│                                                         │
│  Suba um extrato bancário para que suas                 │
│  transações apareçam aqui automaticamente.              │
│                                                         │
│  [📤 Subir extrato]                                     │
└─────────────────────────────────────────────────────────┘
```

**Plano — sem dados:**

```
┌─────────────────────────────────────────────────────────┐
│  Plano Financeiro                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         [Ilustração: bússola ou mapa]                   │
│                                                         │
│  Seu plano financeiro começa aqui.                      │
│                                                         │
│  Primeiro, precisamos entender seus gastos reais.       │
│  Suba um extrato para que possamos sugerir              │
│  um plano baseado no que você já gasta.                 │
│                                                         │
│  [📤 Subir extrato primeiro]                            │
│                                                         │
│  ou  [Criar plano manualmente →]                        │
└─────────────────────────────────────────────────────────┘
```

**Carteira — sem dados:**

```
┌─────────────────────────────────────────────────────────┐
│  Minha Carteira                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         [Ilustração: cofre ou gráfico]                  │
│                                                         │
│  Veja seu patrimônio completo aqui.                     │
│                                                         │
│  Adicione seus investimentos para acompanhar            │
│  rentabilidade, IR estimado e evolução.                 │
│                                                         │
│  [Adicionar primeiro investimento]                      │
│                                                         │
│  Ou suba um extrato com aportes para                    │
│  vincular automaticamente.                              │
└─────────────────────────────────────────────────────────┘
```

#### Bases criadas automaticamente no primeiro login

Quando o usuário cria sua conta, o backend cria automaticamente:

```python
GRUPOS_PADRAO = [
    # Despesas
    {"nome": "Alimentação",    "categoria_geral": "Despesa",     "cor": "#FF6B6B"},
    {"nome": "Transporte",     "categoria_geral": "Despesa",     "cor": "#4ECDC4"},
    {"nome": "Casa",           "categoria_geral": "Despesa",     "cor": "#45B7D1"},
    {"nome": "Saúde",          "categoria_geral": "Despesa",     "cor": "#96CEB4"},
    {"nome": "Lazer",          "categoria_geral": "Despesa",     "cor": "#FFEAA7"},
    {"nome": "Educação",       "categoria_geral": "Despesa",     "cor": "#DDA0DD"},
    {"nome": "Outros",         "categoria_geral": "Despesa",     "cor": "#B0B0B0"},
    # Investimentos
    {"nome": "Investimentos",  "categoria_geral": "Investimento","cor": "#2ECC71"},
    # Receitas
    {"nome": "Receita",        "categoria_geral": "Receita",     "cor": "#F7DC6F"},
    {"nome": "Transferência",  "categoria_geral": "Transferência","cor": "#AEB6BF"},
]
```

- `base_grupos_config` populado com os grupos padrão
- `user_financial_profile` criado com valores zerados (pronto para receber renda declarada)
- Modo demo disponível (dados de exemplo pré-gerados, isolados por usuário)

#### Checklist de progresso ("Primeiros passos")

Exibido no Início enquanto o usuário não tiver completado todos os itens:

```
┌─────────────────────────────────────────────────────────┐
│  Seus primeiros passos  · 1/4 concluídos               │
│                                                         │
│  ✅ Criou sua conta                                     │
│  ⬜ Subiu seu primeiro extrato             [→ Fazer]   │
│  ⬜ Criou seu Plano Financeiro             [→ Fazer]   │
│  ⬜ Adicionou um investimento              [→ Fazer]   │
└─────────────────────────────────────────────────────────┘
```

- Cada item completado → check animado + mensagem de parabéns
- Ao completar todos os 4 → card some, é substituído pelo resumo normal do mês

#### Notificações de ativação (in-app e push futuro)

| Gatilho | Mensagem | CTA |
|---------|---------|-----|
| Cadastro feito, sem upload em 1 dia | "Suba seu extrato bancário e veja para onde vai seu dinheiro" | Upload |
| Primeiro upload feito | "Ótimo início! Agora crie seu Plano para ter um orçamento real" | Criar Plano |
| Plano criado, sem investimento | "Complete seu patrimônio! Adicione seus investimentos" | Carteira |
| Último upload há > 30 dias | "Hora de atualizar seus dados! Suba o extrato de [mês]" | Upload |
| 3 aportes aguardando vínculo há > 7 dias | "Você tem 3 aportes para vincular em Carteira" | Carteira |
