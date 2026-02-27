# UX — Plano Financeiro Integrado (Gastos + Aposentadoria)

**Data:** 26/02/2026  
**Status:** 🟡 Rascunho para validação  
**Objetivo:** Pensar como seria a experiência completa de construção de plano, integrando renda, gastos, gastos extraordinários, evolução e o "recibo" final

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
- **Evolução por grupo** funciona exatamente como nos ganhos/aportes extraordinários: checkbox "Evoluir valor" → % ou R$/ano
  - Exemplos de uso natural: "Escola das crianças aumenta 10%/ano", "Aluguel reajusta pelo IGPM"
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
│  RECIBO MÊS A MÊS              ─────────────────── │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Mês     Renda    Gastos   Aporte  Saldo      │  │
│  │ Jan/26  15.000   10.700   2.500   1.800  ✅  │  │
│  │ Fev/26  15.000   12.900   2.500     600  ⚠️  │  │
│  │         ↑ IPTU R$2.200                       │  │
│  │ Mar/26  15.000   14.500   2.500  -2.000  ❌  │  │
│  │         ↑ IPVA R$3.800                       │  │
│  │ Abr/26  15.000   10.700   2.500   1.800  ✅  │  │
│  │ ...                                           │  │
│  │ Jul/26  15.000   22.700   2.500  -9.200  ❌  │  │
│  │         ↑ Viagem R$12.000                    │  │
│  │ Dez/26  30.000   10.700   2.500  16.800  ✅  │  │
│  │         ↑ 13º R$15.000                       │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ⚠️ 3 meses com saldo negativo                    │
│  Sugestão: aumentar aporte em Dez/26 para cobrir   │
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

## Conceito de evolução de gastos — como funciona

Igual ao existente para aportes/ganhos extraordinários:

```
┌────────────────────────────────────────────────┐
│ 🏠 Casa              R$ 3.200 ← média 3 meses │
│    Meta 2026:       [R$ 3.000]                 │
│                                                │
│    ☐ Evoluir valor anualmente                  │
│        [  5  ] %  ▼     ou     [150] R$ ▼     │
│                                                │
│    📈 Projeção:                                │
│       2026: R$ 3.000                           │
│       2027: R$ 3.150  (+5%)                    │
│       2028: R$ 3.308  (+5%)                    │
│       2029: R$ 3.473  (+5%)                    │
└────────────────────────────────────────────────┘
```

**Por que isso importa:** Aluguel reajusta pelo IGPM (~5%/ano), escola das crianças reajusta (~8-10%/ano), plano de saúde reajusta (~10-15%/ano). Sem isso, o plano fica desatualizado no segundo ano.

No recibo, os gastos com evolução aparecem com o valor do ano correspondente — mês a mês, o app aplica a evolução corretamente.

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

## Perguntas para validação antes de implementar

1. **Onde fica o entry point?** Opções:
   - A) Botão "Construir Plano" na tela `/mobile/budget` (acima da lista de metas)
   - B) Tela separada no menu de navegação ("Plano" vira uma seção própria)
   - C) Integrado ao fluxo do Plano de Aposentadoria (etapa 0 antes de definir aporte)

2. **Plano de aposentadoria separado ou unificado?**
   - A) O construtor substitui ambas as telas (uma só experiência)
   - B) O construtor é um onboarding novo, mas as duas telas existentes ficam para edição avançada

3. **Evolução de gastos: por grupo ou por gasto sazonal apenas?**
   - Hoje o plano de aposentadoria tem evolução nos aportes extraordinários
   - Na proposta: cada grupo de gasto mensal também pode evoluir
   - Isso é mais poderoso mas também mais complexo — vale a pena?

4. **Parcelamento: registrar no banco como N linhas ou calcular no frontend?**
   - Banco: mais pesado mas correto para o histórico
   - Frontend: mais simples, mas se o usuário editar o banco não reflete

5. **API necessária nova:** `GET /budget/media-3-meses?user_id=X` (já existe lógica de média no `valor_medio_3_meses` do modelo — só expor no endpoint)
