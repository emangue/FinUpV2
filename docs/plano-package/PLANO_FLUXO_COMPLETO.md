# Plano Financeiro e Aposentadoria — Fluxo Completo e Todos os Arquivos

> Mapa detalhado do wizard de criação de plano (4 passos) e do planejador de aposentadoria.
> Inclui backend, frontend, dados, fluxos e lógica de negócio.

---

## Índice

1. [Todos os Arquivos](#1-todos-os-arquivos)
2. [Visão Geral: Como as duas features se relacionam](#2-visão-geral-como-as-duas-features-se-relacionam)
3. [Wizard de 4 Passos (Construir Plano)](#3-wizard-de-4-passos-construir-plano)
4. [Backend: Plano Financeiro](#4-backend-plano-financeiro)
   - [Modelos e Tabelas](#modelos-e-tabelas)
   - [Endpoints (Router)](#endpoints-router)
   - [Lógica de Negócio (Service)](#lógica-de-negócio-service)
5. [Componentes do Hub do Plano](#5-componentes-do-hub-do-plano)
6. [Plano de Aposentadoria](#6-plano-de-aposentadoria)
   - [Tab Principal](#tab-principal)
   - [Personalizar Plano (Simulador)](#personalizar-plano-simulador)
   - [Gráfico de Linha do Tempo](#gráfico-de-linha-do-tempo)
   - [Central de Cenários](#central-de-cenários)
   - [API de Aposentadoria](#api-de-aposentadoria)
7. [Fluxos de Dados Completos](#7-fluxos-de-dados-completos)

---

## 1. Todos os Arquivos

| Arquivo no pacote | Arquivo original | O que faz |
|-------------------|-----------------|-----------|
| `backend_plano_ENDPOINTS_router.py` | `domains/plano/router.py` | Todos os endpoints do plano financeiro |
| `backend_plano_LOGICA_cashflow_projecao_orcamento.py` | `domains/plano/service.py` | Toda a lógica: cashflow, projeção, orçamento, impacto |
| `backend_plano_MODELOS_tabelas.py` | `domains/plano/models.py` | Tabelas: user_financial_profile, plano_metas_categoria, base_expectativas |
| `backend_plano_SCHEMAS.py` | `domains/plano/schemas.py` | Schemas Pydantic de entrada/saída |
| `frontend_TELA_construir-plano_page.tsx` | `app/mobile/construir-plano/page.tsx` | Tela que abre o wizard (wrapper simples) |
| `frontend_plano_WIZARD_4_passos.tsx` | `features/plano/components/PlanoWizard.tsx` | Wizard completo: 4 passos guiados |
| `frontend_plano_TIPOS_wizard_state.ts` | `features/plano/types/plano-wizard-state.ts` | Tipos TypeScript do estado do wizard |
| `frontend_plano_API_chamadas.ts` | `features/plano/api.ts` | Todas as chamadas de API do plano (15+ funções) |
| `frontend_plano_CARD_resumo_orcamentario.tsx` | `features/plano/components/PlanoResumoCard.tsx` | Card "Restrição orçamentária" (renda vs despesas vs investimentos) |
| `frontend_plano_TABELA_cashflow_anual.tsx` | `features/plano/components/TabelaReciboAnual.tsx` | Tabela do cashflow anual com modal de cálculo detalhado |
| `frontend_plano_GRAFICO_projecao_poupanca.tsx` | `features/plano/components/ProjecaoChart.tsx` | Gráfico de linhas da projeção de poupança com slider de economia |
| `frontend_plano_LISTA_orcamento_por_categoria.tsx` | `features/plano/components/OrcamentoCategorias.tsx` | Lista de grupos com barra de progresso (gasto vs meta) |
| `frontend_plano_CARD_anos_perdidos_aposentadoria.tsx` | `features/plano/components/AnosPerdidasCard.tsx` | Card âmbar de alerta com anos perdidos de aposentadoria |
| `frontend_plano_WIDGET_resumo_renda_gasto.tsx` | `features/plano/components/BudgetWidget.tsx` | Widget compacto: renda, gasto, disponível/poupança |
| `frontend_plano_FORM_declarar_renda.tsx` | `features/plano/components/RendaDeclaracaoForm.tsx` | Formulário simples de declaração de renda mensal |
| `frontend_aposentadoria_TIPOS.ts` | `features/plano-aposentadoria/types.ts` | Tipos: AporteExtraordinario, PlanoProfile, InvestimentoCenario |
| `frontend_aposentadoria_PERFIS_conservador_moderado_arrojado.ts` | `features/plano-aposentadoria/lib/plan-profiles.ts` | Perfis pré-definidos de retorno/inflação |
| `frontend_aposentadoria_API_chamadas.ts` | `features/plano-aposentadoria/services/plano-api.ts` | API: salvar, atualizar, carregar cenários de aposentadoria |
| `frontend_aposentadoria_TAB_principal.tsx` | `features/plano-aposentadoria/components/plano-aposentadoria-tab.tsx` | Aba de aposentadoria no dashboard (CTA ou lista de cenários) |
| `frontend_aposentadoria_LAYOUT_personalizar_plano.tsx` | `features/plano-aposentadoria/components/PersonalizarPlanoLayout.tsx` | Simulador completo: sliders, aportes extras, projeção SVG |
| `frontend_aposentadoria_GRAFICO_linha_do_tempo.tsx` | `features/plano-aposentadoria/components/plano-chart.tsx` | Gráfico de linha (realizado + projetado) ao longo dos anos |
| `frontend_aposentadoria_CENTRAL_cenarios.tsx` | `features/plano-aposentadoria/components/central-cenarios.tsx` | Gerenciador de cenários: listar, editar nome, excluir, destacar |

---

## 2. Visão Geral: Como as duas features se relacionam

```
PLANO FINANCEIRO (curto/médio prazo)       APOSENTADORIA (longo prazo)
─────────────────────────────────────      ──────────────────────────────────────
Wizard de 4 passos                         Simulador (PersonalizarPlanoLayout)
  ↓                                          ↓
user_financial_profile                     investimentos_cenario_projecao
  renda_mensal_liquida                       aporte_mensal, taxa_retorno_anual
  aporte_planejado                ──────►    patrimonio_inicial (= patrimonio_atual)
  taxa_retorno_anual                         periodo_meses, renda_mensal_alvo
  patrimonio_atual               ◄──────
  idade_aposentadoria
  ↓
Dashboard:
  PlanoResumoCard    → renda vs gastos vs investimentos
  TabelaReciboAnual  → cashflow mês a mês (12 meses)
  ProjecaoChart      → patrimônio acumulado ao longo do ano
  AnosPerdidasCard   → impacto de gastar acima do orçamento
  OrcamentoCategorias → gasto por grupo vs meta
  ↓
Aposentadoria (aba Patrimônio no Dashboard):
  PlanoAposentadoriaTab  → CTA ou lista de cenários
  PlanoChart             → linha do tempo (passado realizado + futuro projetado)
  CentralCenarios        → gerenciar múltiplos cenários
```

Os dois mundos compartilham um campo crítico: `patrimonio_atual` em `user_financial_profile`. O wizard de plano lê e escreve esse campo; o simulador de aposentadoria o usa como ponto de partida da projeção.

---

## 3. Wizard de 4 Passos (Construir Plano)

**Arquivos:** `frontend_TELA_construir-plano_page.tsx`, `frontend_plano_WIZARD_4_passos.tsx`, `frontend_plano_TIPOS_wizard_state.ts`

### Entrada na tela

A página `/mobile/construir-plano` é um wrapper que:
- Inicializa o estado com `initialPlanoWizardState`
- Renderiza `<PlanoWizard state={...} onStateChange={...} onFinish={() => router.push('/mobile/plano')} />`
- Ao finalizar: navega de volta para `/mobile/plano`

### Estado do Wizard (PlanoWizardState)

```typescript
interface PlanoWizardState {
  renda_mensal: number                    // declarada no passo 1
  ganhos_extras: {
    descricao: string
    valor: number
  }[]
  gastos_por_grupo: {
    grupo: string
    valor_planejado: number
    mes_referencia: string               // "YYYY-MM"
  }[]
  sazonais: {
    mes: number
    descricao: string
    valor: number
  }[]
  aporte: number                         // declarado no passo 4
}
```

### Passo 1 — Renda

**O que o usuário faz:** Informa a renda mensal líquida.

**Visual:**
- Título: "Qual é a sua renda mensal líquida?"
- Subtítulo: "Salário + freelance + aluguéis, já descontado impostos e deduções"
- Input de valor (R$, aceita decimais)
- Botão "Próximo" com chevron →

**O que acontece ao avançar:**
- Se `renda > 0` → chama `postRenda(renda)` → `POST /plano/renda`
- Salva em `user_financial_profile.renda_mensal_liquida`
- Erros são silenciados (catch vazio) — não bloqueia progresso

**Inicialização:**
- Ao abrir o passo, chama `getPerfil()` → `GET /plano/perfil`
- Preenche o input com a renda já salva (se existir)

---

### Passo 2 — Gastos

**O que o usuário faz:** (Placeholder atual)

**Visual:**
- Mensagem apontando para a tela de Metas (`/mobile/budget/manage`)
- Ainda não tem formulário próprio — usuário gerencia metas na tela de Budget

**Futuro:** Previsto para ter formulário inline de criação de metas por grupo.

---

### Passo 3 — Sazonais

**O que o usuário faz:** (Placeholder atual)

**Visual:**
- Mensagem informativa sobre gastos sazonais (IPVA, IPTU, viagens, etc.)
- Não tem formulário ativo ainda

**Futuro:** Formulário para criar `base_expectativas` do tipo `sazonal_plano`.

---

### Passo 4 — Aporte

**O que o usuário faz:** Informa quanto quer guardar/investir por mês.

**Visual:**
- Título: "Quanto você quer guardar por mês?"
- Subtítulo: "Este é o aporte planejado para investimentos"
- Input de valor (R$, aceita decimais)
- Botão "Finalizar" (último passo)

**O que acontece ao finalizar:**
- Se `aporte > 0` → chama `putPerfil({ aporte_planejado: aporte })` → `PUT /plano/perfil`
- Salva em `user_financial_profile.aporte_planejado`
- Em seguida: chama `onFinish()` → navega para `/mobile/plano`

---

### Indicador de Progresso Visual

- 4 círculos no topo (um por passo)
- Círculo cheio = passo concluído
- Círculo com borda + cor = passo atual
- Círculo vazio = passo futuro
- Label do passo atual abaixo dos círculos

---

## 4. Backend: Plano Financeiro

**Arquivos:** `backend_plano_MODELOS_tabelas.py`, `backend_plano_ENDPOINTS_router.py`, `backend_plano_LOGICA_cashflow_projecao_orcamento.py`, `backend_plano_SCHEMAS.py`

### Modelos e Tabelas

#### `user_financial_profile` — Perfil financeiro (1 por usuário)

```
user_id              → FK users (UNIQUE — um por usuário)
renda_mensal_liquida → Float, nullable (declarada no wizard passo 1)
aporte_planejado     → Float, default=0 (declarado no wizard passo 4)
idade_atual          → Integer, nullable
idade_aposentadoria  → Integer, default=65
patrimonio_atual     → Float, default=0 (saldo líquido atual)
taxa_retorno_anual   → Float, default=0.08 (8% a.a.)
updated_at           → DateTime
```

#### `plano_metas_categoria` — Meta por grupo e mês

```
user_id    → FK
grupo      → nome do grupo (ex: "Alimentação")
valor_meta → Float (meta de gasto ou investimento)
ano        → Integer
mes        → Integer, nullable (null = meta anual)
UNIQUE(user_id, grupo, ano, mes)
```

#### `base_expectativas` — Lançamentos futuros planejados

```
user_id          → FK
descricao        → String (ex: "IPVA 2026", "13º salário")
valor            → Float
grupo            → String, nullable (qual grupo afeta)
tipo_lancamento  → "debito" | "credito"
mes_referencia   → "YYYY-MM" (mês que vai acontecer)
tipo_expectativa → "sazonal_plano" | "renda_plano" | "parcela_futura"
origem           → "usuario" | "sistema"
id_parcela       → para parcelamentos (mesmo id do upload)
parcela_seq      → número da parcela (1, 2, 3...)
parcela_total    → total de parcelas
status           → "pendente" | "realizado" | "divergente" | "cancelado"
journal_entry_id → FK quando a transação real acontecer
valor_realizado  → valor da transação real
realizado_em     → data que aconteceu
UNIQUE(user_id, id_parcela, parcela_seq)
```

---

### Endpoints (Router)

`backend_plano_ENDPOINTS_router.py` — prefixo: `/plano`

| Método | Rota | O que faz |
|--------|------|-----------|
| `POST` | `/plano/renda` | Salva renda mensal (upsert em user_financial_profile) |
| `GET` | `/plano/renda` | Retorna renda declarada ou null |
| `GET` | `/plano/resumo?ano=&mes=` | Retorna renda, total_budget, disponivel_real |
| `GET` | `/plano/orcamento?ano=&mes=` | Retorna gasto vs meta por grupo |
| `GET` | `/plano/impacto-longo-prazo?ano=&mes=` | Retorna anos perdidos de aposentadoria |
| `POST` | `/plano/metas/{grupo}` | Salva meta de gasto para um grupo e mês |
| `GET` | `/plano/perfil` | Retorna perfil financeiro completo |
| `PUT` | `/plano/perfil` | Atualiza campos do perfil (todos opcionais) |
| `GET` | `/plano/cashflow?ano=` | Retorna cashflow dos 12 meses do ano |
| `GET` | `/plano/cashflow/detalhe-mes?ano=&mes=` | Diagnóstico: cálculo exato de um mês |
| `GET` | `/plano/projecao?ano=&meses=&reducao_pct=` | Retorna projeção de poupança acumulada |
| `GET` | `/plano/expectativas?mes=` | Lista expectativas (opcional: filtro por mês) |
| `POST` | `/plano/expectativas` | Cria novo lançamento futuro (sazonal, extra, parcela) |
| `DELETE` | `/plano/expectativas/{id}` | Remove lançamento futuro |

---

### Lógica de Negócio (Service)

`backend_plano_LOGICA_cashflow_projecao_orcamento.py` — os métodos mais complexos:

#### `get_resumo(user_id, ano, mes)`
```
renda              → user_financial_profile.renda_mensal_liquida
total_budget       → SUM(valor_planejado) de budget_planning
                     WHERE CategoriaGeral = 'Despesa' AND mes_referencia = 'YYYY-MM'
disponivel_real    → renda - total_budget
```

#### `get_orcamento(user_id, ano, mes)`
Para cada grupo de despesa:
```
gasto_real → SUM(ABS(Valor)) de journal_entries
             WHERE CategoriaGeral='Despesa' AND Ano=ano AND Mes=mes
meta       → plano_metas_categoria.valor_meta
             OU fallback: budget_planning.valor_planejado
percentual → (gasto_real / meta) * 100
status     → "ok" | "alerta" (>75%) | "excedido" (>100%) | "sem_meta"
```

#### `get_impacto_longo_prazo(user_id, ano, mes)`
Calcula o custo de gastar acima da renda:
```
gastos_totais   → SUM(ABS(Valor)) de journal_entries (Despesa + Investimentos)
deficit_mensal  → max(0, gastos_totais - renda)

Se deficit_mensal > 0:
  anos_até_aposent    → idade_aposentadoria - idade_atual
  meses_até_aposent   → anos_até_aposent * 12
  taxa_mensal         → (1 + taxa_retorno_anual)^(1/12) - 1
  custo_oportunidade  → deficit_mensal * ((1+taxa)^meses - 1) / taxa
                        (valor futuro de perder 1 mês de déficit)
  anos_perdidos       → custo_oportunidade / (renda_passiva_mensal_alvo * 12)
                        onde renda_passiva_alvo = renda * 0.04 * 12
```

#### `get_cashflow(user_id, ano)` — O mais complexo
Retorna 12 meses. Para cada mês:

**Determinação de renda:**
```
renda_realizada → SUM de journal_entries CREDITO no mês
renda_esperada  → user_financial_profile.renda_mensal_liquida
renda_usada     → renda_realizada se >= 90% da esperada
                  senão renda_esperada
use_realizado   → True se renda_usada == renda_realizada
```

**Determinação de gastos:**
```
gastos_realizados → SUM(ABS(Valor)) de journal_entries Despesa
gastos_recorrentes → SUM(valor_planejado) de budget_planning Despesa
gastos_usados     → gastos_realizados se use_realizado
                    senão gastos_recorrentes

gastos_extras     → SUM(valor) de base_expectativas debito
                    apenas quando NOT use_realizado (modo planejado)

total_gastos      → gastos_usados + gastos_extras
```

**Determinação de aporte:**
```
aporte_real     → SUM(ABS(Valor)) de journal_entries Investimentos
aporte_planejado → user_financial_profile.aporte_planejado
aporte_usado    → aporte_real se use_realizado
                  senão aporte_planejado
```

**Cálculo final:**
```
saldo_projetado → renda_usada - total_gastos
                  (aporte NÃO desconta do saldo — é separado)

status_mes:
  "ok"      → saldo >= 0 e gastos <= recorrentes
  "parcial" → saldo >= 0 mas gastos > recorrentes
  "negativo"→ saldo < 0
  "futuro"  → mês ainda não chegou
```

#### `get_projecao(user_id, ano, meses, reducao_pct)`
Acumulação patrimonial mês a mês:
```
acumulado_inicial → user_financial_profile.patrimonio_atual

Para cada mês do cashflow:
  se use_realizado (mês passado com dados reais):
    aporte_efetivo → aporte_real do cashflow
  senão (mês futuro):
    gastos_ajustados → total_gastos * (1 - reducao_pct/100)
    aporte_efetivo   → renda - gastos_ajustados

  acumulado += aporte_efetivo
  (sem juros — é apenas fluxo de caixa, não projeção de investimento)
```

A projeção de investimentos com juros compostos fica no módulo de aposentadoria.

---

## 5. Componentes do Hub do Plano

Todos aparecem na página `/mobile/plano`. Arquivo de API comum: `frontend_plano_API_chamadas.ts`.

---

### PlanoResumoCard (`frontend_plano_CARD_resumo_orcamentario.tsx`)

Card índigo com resumo da restrição orçamentária.

**Condição de exibição:** Não renderiza se `renda = null` OU `total_budget = 0`.

**Modo 1 — Com dados realizados** (há transações no mês):
```
Grid 3 colunas:
  RECEITAS  | DESPESAS         | INVESTIDOS
  [verde]   | [vermelho]       | [azul]
            | "XXX abaixo"(✓) |
            | "XXX acima" (✗)  |
```
Badge: "Dentro do plano" (verde) ou "Acima do plano" (âmbar)

**Modo 2 — Apenas planejamento** (sem transações ainda):
```
Grid 3 colunas:
  RENDA    | PLANEJADO | DISPONÍVEL
  [normal] | [normal]  | [verde se ≥0, vermelho se <0]
```
Rodapé: "Disponível = Renda − total das metas por grupo"

**Dados buscados:**
- `getResumoPlano(ano, mes)` → renda, total_budget, disponivel_real
- `fetchIncomeSources()` → total de receitas realizadas
- `fetchGoals(mes)` → metas com valor_realizado
- `fetchAportePrincipalPorMes(mes)` → aporte planejado

---

### TabelaReciboAnual (`frontend_plano_TABELA_cashflow_anual.tsx`)

Tabela recolhível com cashflow dos 12 meses.

**Colunas:** Mês | Renda | Gastos | Aporte | Saldo | Status | Calc

**Ícones de status:** ✓ verde (ok) | ✗ vermelho (negativo) | ◐ âmbar (parcial) | ○ cinza (futuro)

**Valores:** Formato compacto: "25k", "1,5M", "—" (zero ou ausente)

**Saldo:** Vermelho se negativo, cinza-900 se positivo.

**Rodapé:** "Resumo [ANO]" com totais do ano.

**Alerta:** Se há meses negativos → "X mês/meses com saldo negativo" (âmbar).

**Modal de Cálculo Exato** (botão 🧮 em cada linha):
- Fórmula exata do cálculo (SQL/lógica)
- Totais: realizado vs planejado (cards azul e âmbar)
- Fonte usada e valor exibido
- Contagem de transações
- Breakdown por grupo (realizado e planejado)
- Tabela de transações do mês (rolável, máx 48px)
- **Formulário "Adicionar gasto extraordinário":**
  - Input: descrição (ex: "IPVA")
  - Input: valor (ex: 1500)
  - Ao salvar: `postExpectativa()` com `tipo_expectativa = "sazonal_plano"`
  - Atualiza o cashflow após adicionar

**Dados buscados:**
- `getCashflow(ano)` → array dos 12 meses
- `getCashflowDetalheMes(ano, mes)` → detalhe por mês (ao abrir modal)
- `postExpectativa(payload)` → ao adicionar gasto extra

---

### ProjecaoChart (`frontend_plano_GRAFICO_projecao_poupanca.tsx`)

Gráfico de linhas de projeção de poupança.

**Slider:** "Reduzir gastos em: 0% – 50%" (step 5%)
- Ao mover: recalcula a linha laranja sem nova requisição

**Até 3 linhas:**
| Linha | Cor | Estilo | Condição |
|-------|-----|--------|----------|
| Plano | Índigo #6366f1 | Sólido | Sempre |
| Real | Verde #22c55e | Sólido | Só nos meses com `use_realizado = true` |
| Plano com Economia | Âmbar #f59e0b | Tracejado | Só quando slider > 0 |

**Eixos:**
- X: "Jan/2026", "Fev/2026"...
- Y: formato compacto ("25k", "1,5M", valores negativos com −)

**Tooltip:** "Mês [label]: R$ X.XXX,XX"

**Rodapé:**
- Slider = 0%: "Fim do ano: XXXk"
- Slider > 0%: "Base: XXXk · Com X% economia: XXXk"

**Dados buscados:**
- `getProjecao(ano, 12, reducaoPct)` → série base + série com redução
- `getCashflow(ano)` → para determinar onde aplicar linha verde (meses realizados)

---

### OrcamentoCategorias (`frontend_plano_LISTA_orcamento_por_categoria.tsx`)

Lista de grupos com progresso visual.

**Por grupo:**
- Nome do grupo
- Barra de progresso (% gasto / meta)
- Valor gasto e meta
- Status em texto

**Cores por status:**
| Status | Cor |
|--------|-----|
| ok (≤75%) | Esmeralda |
| alerta (75–100%) | Âmbar |
| excedido (>100%) | Vermelho |
| sem_meta | Cinza |

**Dados:** `getOrcamento(ano, mes)`

---

### AnosPerdidasCard (`frontend_plano_CARD_anos_perdidos_aposentadoria.tsx`)

Card de alerta âmbar. **Só aparece se `anos_perdidos > 0`**.

**Conteúdo:**
- Ícone de alerta (laranja)
- Mensagem: "Com esse nível de gasto você está perdendo ~N anos de aposentadoria"
- Subtexto: "Déficit mensal: R$ X.XXX"

**Dados:** `getImpactoLongoPrazo(ano, mes)`

---

### BudgetWidget (`frontend_plano_WIDGET_resumo_renda_gasto.tsx`)

Widget compacto no topo do Dashboard.

**Estado sem renda configurada:**
- Card cinza com CTA: "Configure seu plano financeiro"
- Link para `/mobile/perfil/financeiro`

**Estado normal (3 colunas):**
- Renda | Gasto | Poupança (ou Disponível)
- Link para `/mobile/perfil/financeiro`
- Mostra percentual de poupança ou valor disponível

**Dados:** `getRenda()`, `getResumoPlano(ano, mes)`

---

### RendaDeclaracaoForm (`frontend_plano_FORM_declarar_renda.tsx`)

Formulário simples de entrada de renda.

**Campo:** Input de valor monetário (≥ 0, aceita decimais)
**Submit:** Chama `postRenda(valor)` → `POST /plano/renda`
**Inicialização:** Carrega `getRenda()` para preencher valor existente
**Estados:** loading, erro, sucesso

---

## 6. Plano de Aposentadoria

### Tab Principal (`frontend_aposentadoria_TAB_principal.tsx`)

Aparece na aba "Patrimônio" do Dashboard.

**Props:** `patrimonioLiquido`, `idadeAtual`, `onCreatePlan`

**Estado 1 — Sem cenários (CTA):**

Card visual com:
- Timeline horizontal: HOJE ──────► APOSENTADORIA
- Curva SVG ascendente (ilustrativa)
- Pills: patrimônio atual (embaixo esq) e meta (em cima dir)
- Título: "Construa Seu Plano"
- Subtítulo: "4 passos para saber se você está no caminho certo"
- Lista de 4 passos informativos:
  1. Defina sua renda alvo na aposentadoria
  2. Informe seu patrimônio atual
  3. Configure taxa de retorno e inflação
  4. Adicione aportes extraordinários
- Botão **"+ Criar Meu Plano"** → chama `onCreatePlan()`
- Rodapé: explicação da regra dos 4%

**Estado 2 — Com cenários:**
- `PlanoChart` (gráfico linha do tempo)
- `CentralCenarios` (lista de cenários)

---

### Personalizar Plano (Simulador) (`frontend_aposentadoria_LAYOUT_personalizar_plano.tsx`)

1.187 linhas. O simulador mais complexo do app.

**Props:** `cenarioId?` — se passado, edita cenário existente; se null, cria novo.

**Campos configuráveis:**

| Campo | Default | Descrição |
|-------|---------|-----------|
| Idade atual | 35 | Sua idade hoje |
| Idade de aposentadoria | 65 | Quando quer parar |
| Aporte mensal | 5.000 | Quanto vai investir por mês |
| Retorno anual | 10% | Taxa de retorno esperada |
| Inflação anual | 4,5% | Correção monetária esperada |
| Patrimônio atual | (do dashboard) | Quanto já tem hoje |
| Renda mensal alvo | 25.000 | Quanto quer receber na aposentadoria |

**Perfis pré-definidos** (`frontend_aposentadoria_PERFIS_conservador_moderado_arrojado.ts`):

| Perfil | Retorno | Inflação |
|--------|---------|---------|
| Conservador | 6% a.a. | 4% a.a. |
| Moderado | 10% a.a. | 4,5% a.a. |
| Arrojado | 14% a.a. | 5% a.a. |

**Aportes Extraordinários:**

Cada aporte extra tem:
```typescript
{
  id: string
  mesAno: number           // mês de ocorrência (1-12)
  valor: number
  descricao: string
  recorrencia: 'unico' | 'trimestral' | 'semestral' | 'anual'
  evoluir: boolean         // se cresce ao longo do tempo
  evolucaoValor: number    // quanto cresce
  evolucaoTipo: 'percentual' | 'nominal'
}
```

**Lógica de Projeção (useMemo — client-side, sem API):**

```
periodo_meses = (retire - age) * 12
taxa_mensal   = (1 + retorno/100)^(1/12) - 1

extras_expandidos = expandExtras(extras)
  → Expande recorrências (trimestral = meses 1, 4, 7, 10...)
  → Aplica evolução YoY se evoluir = true

pNom = patrimonio_atual
para cada mês:
  pNom = pNom * (1 + taxa_mensal) + aporte_mensal + extras_expandidos[mês]

pReal = pNom / (1 + inflacao/100)^(periodo_meses/12)

rendaPassivaNom = pNom * 0.04 / 12    (regra dos 4%)
rendaPassivaReal = pReal * 0.04 / 12

sentiment:
  😊 se rendaPassivaReal >= rendaMensal
  😐 se >= 70% da meta
  😟 se < 70%
```

**Gráfico SVG integrado:**
- Curva Bézier nominal (patrimônio em valor nominal)
- Curva Bézier real (patrimônio em valor real, ajustado pela inflação)
- Ponto inicial: patrimônio atual
- Ponto final: projeção na aposentadoria

**Painel de resultados:**
- Patrimônio nominal e real
- Renda passiva mensal (nominal e real)
- Total de aportes realizados
- Rendimentos (pNom − totalAportes)
- Perda pela inflação (pNom − pReal)
- Multiplicador (pReal / totalAportes)
- Emoji de sentimento (😊 / 😐 / 😟)

**Ao salvar:**
- Chama `salvarPlano(payload, patrimonioLiquido, anomesPatrimonio)` → `frontend_aposentadoria_API_chamadas.ts`
- Cria `InvestimentoCenario` no backend
- Taxa mensal = `(1 + retorno/100)^(1/12) - 1` convertida antes de salvar
- `periodo_meses = (retire - age) * 12`
- Extras salvos como JSON em `extras_json`
- Mostra tela de sucesso com ✓ e link para o dashboard

---

### Gráfico de Linha do Tempo (`frontend_aposentadoria_GRAFICO_linha_do_tempo.tsx`)

**Props:** `cenarioId?`

**Dados buscados:**
- `getPatrimonioTimeline(ano_inicio, ano_fim)` → patrimônio histórico mensal
- `getCenarioProjecao(cenarioId)` → itens da projeção do cenário
- `getCenario(cenarioId)` → metadados do cenário

**Duas linhas:**
| Linha | Cor | Estilo | O que mostra |
|-------|-----|--------|-------------|
| Realizado | Vermelho | Sólido | Patrimônio real histórico (último mês de cada ano) |
| Projetado | Cinza | Tracejado | Patrimônio planejado pelo cenário |

**Eixo X:** Anos (ex: 2020, 2021 ... 2060)
**Eixo Y:** Valores em reais (compacto)

**Pontos destacados:** Só no ano atual e no último ano da projeção.

**Seção "Primeiros meses" (expansível):**
- Tabela dos primeiros 24 meses da projeção
- Colunas: Período | Ano/Mês | Aporte | Patrimônio fim do mês
- Inclui linha do patrimônio inicial

---

### Central de Cenários (`frontend_aposentadoria_CENTRAL_cenarios.tsx`)

**Props:** `cenarios: InvestimentoCenario[]`, `onRefresh: () => void`

**Por cenário (card expansível):**
- Nome do cenário
- Faixa de idade: "35 → 65 anos (30 anos)"
- Renda mensal alvo
- Patrimônio inicial, aporte mensal
- Taxas: retorno e inflação
- Aportes extraordinários (se houver)
- **Botões:**
  - ⭐ Marcar como principal (destaque)
  - ✏️ Editar nome → Dialog com Input
  - 🗑️ Deletar → AlertDialog de confirmação
  - > Expandir/recolher detalhes
  - "Editar plano completo" → abre PersonalizarPlanoLayout com `cenarioId`

**Botão "Novo Cenário"** no final da lista.

---

### API de Aposentadoria (`frontend_aposentadoria_API_chamadas.ts`)

**Funções principais:**

| Função | O que faz |
|--------|-----------|
| `salvarPlano(payload, patrimonioLiquido, anomesPatrimonio)` | Cria novo cenário de aposentadoria |
| `atualizarPlano(cenarioId, payload, ...)` | Atualiza cenário existente |
| `carregarPlano(cenarioId)` | Carrega cenário e parse dos extras |
| `retornoAaToMensal(retornoAa)` | `(1 + retorno/100)^(1/12) - 1` |
| `nextAnomes(anomes)` | Próximo mês no formato YYYYMM |
| `toExtrasJson(extras)` | Serializa aportes extras para JSON |
| `parseExtrasJson(json)` | Deserializa do banco |

**Conversão de taxa antes de salvar:**
```
taxa_retorno_mensal = (1 + taxa_retorno_anual)^(1/12) - 1
periodo_meses = (retire_age - age) * 12
```

---

## 7. Fluxos de Dados Completos

### Fluxo A — Declarar Renda no Wizard

```
Usuário digita renda
  → PlanoWizard (passo 1)
  → postRenda(valor)
  → POST /plano/renda
  → Service.upsert_renda()
  → UPDATE user_financial_profile SET renda_mensal_liquida = valor
```

### Fluxo B — Ver Resumo do Plano

```
/mobile/plano carrega
  → getResumoPlano(ano, mes)
  → GET /plano/resumo?ano=&mes=
  → Service.get_resumo():
      renda = user_financial_profile.renda_mensal_liquida
      total_budget = SUM(budget_planning.valor_planejado) WHERE categoria='Despesa'
      disponivel = renda - total_budget
  → PlanoResumoCard exibe os 3 valores
```

### Fluxo C — Cashflow Anual

```
TabelaReciboAnual carrega
  → getCashflow(ano)
  → GET /plano/cashflow?ano=
  → Service.get_cashflow():
      Para cada mês 1-12:
        renda_usada     = realizada (se ≥90%) ou planejada
        gastos_usados   = realizados (se use_realizado) ou recorrentes
        gastos_extras   = expectativas planejadas (se não realizado)
        aporte_usado    = real ou planejado
        saldo           = renda - (gastos + extras)
        status          = ok/parcial/negativo/futuro
  → TabelaReciboAnual renderiza linha por mês
```

### Fluxo D — Projeção com Slider

```
Usuário move slider para 20%
  → ProjecaoChart state: reducaoPct = 20
  → getProjecao(ano, 12, 20)
  → GET /plano/projecao?meses=12&reducao_pct=20
  → Service.get_projecao():
      patrimonio_inicial = user_financial_profile.patrimonio_atual
      Para cada mês futuro:
        gastos_ajustados = total_gastos * (1 - 0.20)
        aporte_efetivo = renda - gastos_ajustados
        acumulado += aporte_efetivo
  → Linha âmbar (com economia) é renderizada no gráfico
```

### Fluxo E — Criar Cenário de Aposentadoria

```
Usuário preenche PersonalizarPlanoLayout e clica "Salvar"
  → salvarPlano(payload, patrimonioLiquido, anomesPatrimonio)
  → Converte retorno a.a. → mensal
  → Calcula periodo_meses
  → POST /investimentos/cenarios
  → Cria InvestimentoCenario no banco
  → Frontend mostra tela de sucesso
  → Link para /mobile/dashboard → aba Patrimônio
```

### Fluxo F — Ver Gráfico de Linha do Tempo

```
PlanoChart carrega com cenarioId
  → getPatrimonioTimeline(-5 anos, +35 anos)
  → getCenarioProjecao(cenarioId)
  → getCenario(cenarioId)
  → Combina:
      - Linha vermelha (realizado): histórico do patrimônio
      - Linha cinza (projetado): valores do cenário
  → SVG renderizado com Recharts
  → Seção "Primeiros 24 meses" disponível para expandir
```

### Fluxo G — Adicionar Gasto Sazonal pelo Modal de Cálculo

```
Usuário abre modal de cálculo em jan/2026
  → Clica "Adicionar gasto extraordinário"
  → Digita "IPVA" e R$ 1.500
  → Clica "Adicionar"
  → postExpectativa({
      descricao: "IPVA",
      valor: 1500,
      mes_referencia: "2026-01",
      tipo_lancamento: "debito",
      tipo_expectativa: "sazonal_plano"
    })
  → POST /plano/expectativas
  → Salva em base_expectativas
  → getCashflow() é chamado novamente
  → Tabela atualiza: gastos_extras de jan/2026 agora inclui R$ 1.500
```

---

*Para contexto arquitetural geral, ver: `../VISAO_GERAL_COMPLETA.md`*
*Para detalhes das telas, ver: `../TELAS_DETALHADAS.md`*
