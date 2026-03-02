# FinUp — Detalhamento de Telas, Botões e Gráficos

> Documento para validação de ideias sem precisar abrir o código.
> Cada tela está descrita com seus elementos, estados, ações e navegação.

---

## Índice

1. [Layout Mobile (navegação global)](#1-layout-mobile)
2. [Dashboard](#2-dashboard)
3. [Plano — Hub](#3-plano-hub)
4. [Construir Plano (Wizard)](#4-construir-plano-wizard)
5. [Budget — Lista de Metas](#5-budget-lista-de-metas)
6. [Budget — Gerenciar Metas](#6-budget-gerenciar-metas)
7. [Budget — Detalhe de Meta](#7-budget-detalhe-de-meta)
8. [Perfil do Usuário](#8-perfil-do-usuário)
9. [Componentes Reutilizáveis](#9-componentes-reutilizáveis)
   - [PlanoResumoCard](#planoResumocard)
   - [TabelaReciboAnual (Cashflow)](#tabelareciboanual-cashflow)
   - [ProjecaoChart](#projecaochart)
   - [EditGoalModal](#editgoalmodal)
   - [NudgeBanners](#nudgebanners)
   - [EmptyState](#emptystate)

---

## 1. Layout Mobile

**Arquivo:** `app_dev/frontend/src/app/mobile/layout.tsx`

Envolve todas as páginas em `/mobile/*`. Define a estrutura global.

### Estrutura
```
OnboardingGuard (proteção de rotas)
  └── PendingUploadProvider (contexto de upload em andamento)
        ├── [página atual]
        └── BottomNavigation (condicional)
```

### BottomNavigation
- Fica **fixo na parte inferior** da tela
- **Oculto nas rotas de onboarding** (`/mobile/onboarding/*`)
- 5 abas:

| Aba | Ícone | Rota |
|-----|-------|------|
| Home | Casa | `/mobile/dashboard` |
| Upload | Seta pra cima | `/mobile/upload` |
| Plano | Gráfico/alvo | `/mobile/plano` |
| Carteira | Carteira | `/mobile/carteira` |
| Perfil | Pessoa | `/mobile/profile` |

- Aba ativa: destaque visual (cor diferente)
- As páginas têm `pb-20` para não ficar atrás da barra de navegação

### OnboardingGuard
- Redireciona para `/mobile/onboarding/welcome` se o usuário não completou onboarding
- Permite acesso livre após onboarding concluído

---

## 2. Dashboard

**Arquivo:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

Tela inicial do app. Mostra o resumo financeiro do período.

---

### Header (fixo no topo, z-20)

**Linha 1:**
- Esquerda: `MonthScrollPicker` ou `YearScrollPicker` (depende do modo de período)
  - Scroll horizontal para trocar de mês/ano
  - Período selecionado muda todos os dados da tela
- Direita: 2 botões de ícone
  - **Engrenagem/Configurações** → navega para `/mobile/profile`
  - **Upload** (seta pra cima) → navega para `/mobile/upload`

**Linha 2 — Filtro de Período:**
3 botões tipo toggle (só um ativo por vez):
- **Mês** — exibe dados do mês selecionado
- **YTD** — exibe acumulado do ano até o mês atual
- **Ano** — exibe o ano inteiro

---

### Estados da Tela

| Estado | O que aparece |
|--------|--------------|
| Verificando auth | Spinner + "Verificando autenticação..." (tela cheia) |
| Carregando dados | Spinner + "Carregando..." |
| Com dados | Conteúdo completo |

---

### Banners (aparecem acima das abas, em ordem de prioridade)

1. **DemoModeBanner** — aparece se o usuário está usando dados de demo
2. **NudgeBanners** — nudge contextual (ver seção [NudgeBanners](#nudgebanners))
3. **OnboardingChecklist** — progresso do onboarding (desaparece quando completo)

---

### Abas do Conteúdo Principal

#### Aba "Resultado"
1. **BudgetWidget** — card horizontal com resumo rápido:
   - Total de receitas vs. total de despesas
   - Saldo do período (receita − despesa)

2. **BarChart** (Recharts):
   - Tipo: Barras verticais agrupadas
   - Dados: Receitas e Despesas por mês
   - Modo **Mês**: 7 barras (últimos 7 meses)
   - Modo **Ano/YTD**: barras do ano completo
   - Eixo X: nomes dos meses (Jan, Fev, Mar...)
   - Eixo Y: valores em reais
   - Cores: azul para receita, vermelho/rosa para despesa
   - Sem legenda visível diretamente no gráfico

3. **OrcamentoTab** — breakdown de gastos por grupo:
   - Lista de grupos com barra de progresso (gasto/meta)
   - Filtro de tipo: Despesas | Receitas | Cartões

4. **GastosPorCartaoBox** — breakdown de despesas por cartão de crédito

5. Link **"Ver Todas as Transações"** → `/mobile/transactions`

#### Aba "Patrimônio"
1. **PatrimonioTab** — resumo do patrimônio líquido
2. **PlanoAposentadoriaTab** — sub-abas dentro desta aba:
   - "Resultado": performance atual
   - "Plano": metas de aposentadoria

---

### Dados Buscados pela Página

| Hook/Função | Endpoint | O que traz |
|-------------|----------|-----------|
| `useDashboardMetrics` | `GET /dashboard/metrics` | total_despesas, total_receitas, patrimonio_liquido |
| `useIncomeSources` | `GET /dashboard/income-sources` | Breakdown de receitas |
| `useExpenseSources` | `GET /dashboard/expense-sources` | Breakdown de despesas |
| `useChartData` | `GET /dashboard/chart-data` | Dados mensais para o gráfico (modo mês) |
| `useChartDataYearly` | `GET /dashboard/chart-data-yearly` | Dados anuais para o gráfico |
| `fetchLastMonthWithData` | `GET /dashboard/last-month-with-data` | Último mês com transações (para default) |

---

## 3. Plano — Hub

**Arquivo:** `app_dev/frontend/src/app/mobile/plano/page.tsx`

Central do plano financeiro. Agrega renda, metas, cashflow e projeções.

---

### Header (fixo no topo)

- Botão "Voltar" (seta) → `router.back()`
- Título: "Plano"
- Abaixo do header: `MonthScrollPicker` com label "Orçamento em:"
  - Muda o mês de referência de todos os componentes da página

---

### Estado Vazio (quando não há renda E não há metas)

- Ícone: 📋
- Título: "Seu plano começa com seus gastos reais"
- Descrição: "Suba seu extrato ou crie metas manualmente para acompanhar seu orçamento."
- Botão primário: **"Construir plano"** → `/mobile/construir-plano`
- Botão secundário: **"Subir extrato primeiro"** → `/mobile/upload`

---

### Conteúdo Principal (lista vertical de cards)

#### Card 1 — "Editar plano" (link)
- Ícone: lápis em círculo índigo
- Título: "Editar plano"
- Subtítulo: "Renda, metas, sazonais e aporte"
- Clique → `/mobile/construir-plano`

#### Card 2 — PlanoResumoCard
Ver detalhes completos em [PlanoResumoCard](#planoresumocard).

#### Card 3 — AnosPerdidasCard
- Exibe "anos perdidos" — impacto no prazo de aposentadoria se gastar acima do planejado
- Exemplo: "Se gastar 15% acima, atrasa aposentadoria em 3,2 anos"

#### Card 4 — TabelaReciboAnual (Cashflow Anual)
Ver detalhes completos em [TabelaReciboAnual](#tabelareciboanual-cashflow).

#### Card 5 — ProjecaoChart
Ver detalhes completos em [ProjecaoChart](#projecaochart).

#### Card 6 — OrcamentoCategorias
- Lista de grupos com: meta planejada, gasto real, percentual e barra de progresso

#### Card 7 — "Gerenciar metas por grupo" (link)
- Ícone: alvo em círculo índigo
- Título: "Gerenciar metas por grupo"
- Subtítulo: "Defina quanto planeja gastar em cada categoria"
- Clique → `/mobile/budget/manage`

---

### Dados Buscados

| Função | Endpoint | O que traz |
|--------|----------|-----------|
| `getResumoPlano()` | `GET /plano/resumo?ano=&mes=` | renda, total_budget, disponivel_real |
| `getOrcamento()` | `GET /plano/orcamento?ano=&mes=` | metas vs realizado por grupo |

### Lógica de Estado Vazio
- `semRenda` = `resumo.renda` é null
- `semMetas` = lista de metas vazia
- Estado vazio mostrado quando **ambos** forem verdadeiros

---

## 4. Construir Plano (Wizard)

**Arquivo:** `app_dev/frontend/src/app/mobile/construir-plano/page.tsx`

Wrapper simples que renderiza o componente `PlanoWizard`.

- **Ao finalizar o wizard** → navega para `/mobile/plano`
- O wizard é um fluxo de múltiplos passos (implementado em `PlanoWizard`):
  - Passo 1: Definir renda mensal líquida
  - Passo 2: Criar metas de gasto por grupo (base de gastos reais)
  - Passo 3: Gastos sazonais (IPVA, viagens, etc.)
  - Passo 4: Configurar aporte (poupança mensal)

---

## 5. Budget — Lista de Metas

**Arquivo:** `app_dev/frontend/src/app/mobile/budget/page.tsx`

Visão geral das metas de orçamento do mês.

---

### Header (fixo, 3 elementos)

- **Esquerda**: `MonthScrollPicker` (flex-1 — ocupa o máximo de espaço)
- **Direita** (3 botões de ícone, não se expandem):
  - Pessoa → `/mobile/profile`
  - Engrenagem → `/mobile/budget/manage`
  - **+** (mais) → `/mobile/budget/new`

---

### Estados

| Estado | O que aparece |
|--------|--------------|
| Carregando | Spinner + "Carregando metas..." |
| Erro | Box vermelho + mensagem + botão "Tentar novamente" |
| Sem metas | EmptyState com CTA "Criar plano" → `/mobile/budget/new` |
| Com metas | DonutChart + lista de GoalListItem |

---

### DonutChart (quando há metas)
- Tipo: Gráfico rosca (donut/pie)
- Exibe uso percentual total do orçamento
- Cada fatia = um grupo de despesa
- **Filtro**: só exibe metas de "gastos" (exclui investimentos)
- Fica em card branco acima da lista

---

### GoalListItem (um por meta)
- Layout de card clicável
- Exibe:
  - Nome do grupo (ex: "Alimentação")
  - Círculo de progresso com percentual
  - Valor gasto real vs. meta planejada (ex: "R$ 850 / R$ 1.200")
  - Badge de status: "No caminho", "Acima do orçamento", etc.
- **Filtro**: só exibe metas de tipo "gastos" (investimentos excluídos)
- **Clique** → `/mobile/budget/[goalId]?mes=YYYY-MM`

---

### Comportamento Especial
- URL aceita `?mes=YYYY-MM` para preservar o mês ao voltar de outra tela
- Se não houver `?mes=`, carrega o último mês com transações automaticamente
- `sessionStorage["goals-need-refresh"]` → força atualização ao voltar da tela de detalhe

---

### Dados Buscados

| Hook | Endpoint | O que traz |
|------|----------|-----------|
| `useGoals()` | `GET /budget/?mes=YYYY-MM` | Lista de metas com realizado |
| `fetchLastMonthWithData()` | `GET /dashboard/last-month-with-data` | Mês padrão |

---

## 6. Budget — Gerenciar Metas

**Arquivo:** `app_dev/frontend/src/app/mobile/budget/manage/page.tsx`

Tela administrativa das metas. Ativa/desativa e edita valores.

---

### Header (fixo)

- **Esquerda**: Botão "Voltar" → `/mobile/budget`
- **Centro**: "Gerenciar Metas"
- **Direita**: Botão **"Salvar"** (azul)
  - Fica "Salvando..." enquanto processa
  - Ao salvar com sucesso: alerta "Alterações salvas com sucesso!" + volta para `/mobile/budget`
  - Erro: alerta de falha

**Abaixo do header**: MonthScrollPicker (mês de referência)

---

### Instruções
- Texto pequeno: "Ative/desative ou edite cada meta individualmente. Use o botão Salvar para confirmar as alterações."
- Aparece apenas se houver metas

---

### Estado Vazio
- "Nenhuma meta encontrada"
- "Crie sua primeira meta para começar"

---

### ManageGoalsListItem (um por meta com ID)

Cada item na lista tem:
- **Toggle switch** (ativar/desativar a meta)
  - Ação imediata: chama `toggleGoalAtivo(goalId, novoEstado)` na API
- **Botão de editar** → `/mobile/budget/[goalId]?mes=YYYY-MM`
- **Input de valor** — mostra `valor_planejado`, editável inline
- **Checkbox "Aplicar até fim do ano"**:
  - Quando marcado: `updateGoalValor()` propaga o valor para todos os meses seguintes
- **Filtro**: só metas de "gastos" (investimentos excluídos)

---

### Botão "Nova Meta" (no final da lista)
- Gradiente azul, texto branco
- → `/mobile/budget/new`

---

### Dados Buscados

| Hook/Função | Endpoint | O que traz |
|-------------|----------|-----------|
| `useGoals()` | `GET /budget/?mes=YYYY-MM` | Lista de metas |
| `toggleGoalAtivo()` | `POST /budget/{id}/toggle` | Ativa/desativa |
| `updateGoalValor()` | `PUT /budget/{id}` | Atualiza valor (com opção de propagar) |

---

## 7. Budget — Detalhe de Meta

**Arquivo:** `app_dev/frontend/src/app/mobile/budget/[goalId]/page.tsx`

Tela detalhada de uma meta específica, com subgrupos e botão de edição.

---

### Header
- Título: "Detalhes da Meta"
- Direita: Ícone de **lápis** → abre `EditGoalModal`

### Subtítulo
- Abaixo do header: mês/ano da meta (ex: "Janeiro 2026")

---

### Estados

| Estado | O que aparece |
|--------|--------------|
| Carregando | Spinner tela cheia + "Carregando..." |
| Meta não encontrada | "Meta não encontrada" + botão "Voltar" → `/mobile/budget` |
| Com dados | Layout completo |

---

### Layout Principal

#### Seção de Cabeçalho da Meta
- Ícone 🎯 em círculo azul
- Nome do grupo como `<h2>`
- Badge "Meta"
- Subtítulo: "Orçamento [mês de referência]"

#### Círculo de Progresso Grande (SVG)
- Raio: 70px
- **Verde**: gasto < 75% da meta
- **Laranja**: gasto entre 75% e 99%
- **Vermelho**: gasto ≥ 100%
- Centro exibe:
  - Linha 1 (grande): percentual (ex: "73%")
  - Linha 2 (média): valor real gasto (ex: "R$ 875")
  - Linha 3 (pequena): "de R$ 1.200" (meta)
- O visual satura em 100%, mas o texto mostra o real (ex: "127%")

#### Grid de 3 Valores
- **Gasto**: valor real gasto (absoluto)
- **Meta**: valor planejado
- **Restante** (se dentro da meta, texto verde) **ou Estouro** (se acima, texto vermelho com −)

#### Seção "Subgrupos"
- Título "Subgrupos"
- Tabela com cada subgrupo do grupo:
  - Nome do subgrupo (clicável)
  - Percentual do total da meta gasto naquele subgrupo
  - Valor absoluto gasto
- **Estado carregando**: "Carregando..."
- **Estado vazio**: "Nenhum subgrupo com transações neste mês"
- **Clique em subgrupo** → `/mobile/transactions?year=YYYY&month=MM&grupo=[grupo]&subgrupo=[subgrupo]&from=metas&goalId=[id]`

#### Botões Fixos no Rodapé (2 colunas)
- **"Voltar"** (branco/contorno) → `/mobile/budget`
- **"Editar Meta"** (azul) → abre `EditGoalModal`

---

### EditGoalModal
Abre quando: clique no lápis do header OU clique em "Editar Meta".
Ver detalhes em [EditGoalModal](#editgoalmodal).

**Após salvar**: atualiza os dados da meta + fecha modal + marca `sessionStorage["goals-need-refresh"]`
**Após deletar**: volta para `/mobile/budget`

---

### Dados Buscados

| Hook/Função | Endpoint | O que traz |
|-------------|----------|-----------|
| `useGoalDetail()` | `GET /budget/{id}?mes=YYYY-MM` | Dados da meta + subgrupos |
| `useEditGoal()` | — | Funções updateGoal() e deleteGoal() |
| Subgrupos (fallback) | `GET /dashboard/subgrupos-by-tipo?year=&month=&grupo=` | Breakdown de subgrupos |

---

## 8. Perfil do Usuário

**Arquivo:** `app_dev/frontend/src/app/mobile/profile/page.tsx`

Configurações e dados pessoais do usuário.

---

### Estados
| Estado | O que aparece |
|--------|--------------|
| Verificando auth | Spinner + "Verificando autenticação..." |
| Carregando perfil | Spinner + "Carregando perfil..." |
| Com dados | Página completa |

---

### Banners (topo da página)
- **Verde** (sucesso): aparece após salvar; some automaticamente após 3 segundos
- **Vermelho** (erro): aparece quando API retorna erro

---

### Seção 1 — Avatar Card (card branco com sombra)
- Esquerda: Círculo grande (fundo índigo-100) com ícone de pessoa
- Direita:
  - Nome do usuário (`<h2>`)
  - Email do usuário (subtítulo)
  - Badge "Usuário" (role, em índigo)

---

### Seção 2 — Editar Perfil (recolhível)

**Colapsado**: botão com ícone de pessoa + "Editar Perfil" + seta direita

**Expandido** (formulário):
- Título: "Editar Perfil"
- Campo: **Nome** (texto, obrigatório)
- Campo: **Email** (email, obrigatório)
- Botão **"Cancelar"** → reverte campos para valores originais, fecha o formulário
- Botão **"Salvar"** (índigo) → `PUT /api/v1/auth/update-profile { nome, email }`
  - Estado durante envio: "Salvando..."
  - Sucesso: banner verde + fecha formulário
  - Erro: banner vermelho

---

### Seção 3 — Alterar Senha (recolhível)

**Colapsado**: botão com ícone de cadeado + "Alterar Senha" + seta direita

**Expandido** (formulário):
- Título: "Alterar Senha"
- Campo: **Senha Atual** (password)
- Campo: **Nova Senha** (password, mínimo 6 caracteres)
- Campo: **Confirmar Nova Senha** (password)
- Validações client-side:
  - Senha atual: obrigatória
  - Nova senha: mínimo 6 chars
  - Confirmação: deve ser idêntica à nova senha
- Botão **"Cancelar"** → fecha o formulário
- Botão **"Alterar Senha"** (índigo) → `POST /api/v1/auth/change-password { current_password, new_password }`
  - Estado durante envio: "Salvando..."

---

### Seção 4 — Gerenciamento (card com divisórias)

Header: "GERENCIAMENTO" (texto cinza, maiúsculas)

5 itens clicáveis (cada um: ícone colorido | label | seta direita):

| Ícone | Cor | Label | Destino |
|-------|-----|-------|---------|
| $ (cifrão) | Esmeralda | Plano | `/mobile/plano` |
| Paleta | Azul | Central de Grupos | `/mobile/grupos` |
| Cartão | Roxo | Meus Cartões | `/mobile/cards` |
| Banido | Vermelho | Excluir / Ignorar | `/mobile/exclusions` |
| Upload | Índigo | Painel de Uploads | `/mobile/uploads` |

---

### Seção 5 — Configurações (card com divisórias)

Header: "CONFIGURAÇÕES" (texto cinza, maiúsculas)

3 itens com toggle:

| Ícone | Cor | Label | Tipo |
|-------|-----|-------|------|
| Sino | Verde | Notificações | Toggle on/off |
| Lua | Cinza escuro | Modo Escuro | Toggle on/off |
| Globo | Azul | Idioma | Read-only "Português" (sem ação) |

---

### Seção 6 — Logout
- Botão full-width, fundo vermelho-50, texto vermelho-600
- Ícone: LogOut
- Texto: "Sair da Conta"
- Ação: limpa `localStorage` (token) + navega para `/auth/login`

---

### Rodapé
- "FinUp Mobile v1.0"
- "© 2026 - Todos os direitos reservados"

---

### Dados Buscados

| Endpoint | O que traz |
|----------|-----------|
| `GET /api/v1/auth/me` | { id, nome, email, role } |

---

## 9. Componentes Reutilizáveis

---

### PlanoResumoCard

**Arquivo:** `app_dev/frontend/src/features/plano/components/PlanoResumoCard.tsx`

Card de resumo financeiro. Aparece na tela do Plano Hub.

**Condição de exibição**: Não renderiza se `renda = null` OU se `total_budget = 0`.

**Aparência base:**
- Fundo: índigo-50, borda índigo-100, arredondado-2xl, padding 4
- Linha do título: "Restrição orçamentária (metas)" + badge

**Badge de status:**
- "Dentro do plano" → fundo verde
- "Acima do plano" → fundo âmbar

---

#### Modo 1 — Com dados realizados (`temRealizado = true`)

Grid de 3 colunas, texto centralizado:

| Coluna | Label | Valor | Sublabel |
|--------|-------|-------|----------|
| Receitas | "RECEITAS" (índigo, maiúsculas) | Total receitas (verde, negrito, grande) | "sem plano" (se não há meta de receita) |
| Despesas | "DESPESAS" (índigo, maiúsculas) | Total despesas (vermelho, negrito, grande) | "XXX abaixo" (verde) ou "XXX acima" (vermelho) |
| Investidos | "INVESTIDOS" (índigo, maiúsculas) | Total investido (azul, negrito, grande) | "100% do aporte" (verde) ou "X% do aporte" (âmbar) ou "sem plano" |

Bordas laterais separam as 3 colunas.

---

#### Modo 2 — Sem dados realizados (`temRealizado = false`)

Grid de 3 colunas, texto centralizado:

| Coluna | Label | Valor |
|--------|-------|-------|
| Renda | "RENDA" | `resumo.renda` |
| Planejado | "PLANEJADO" | `resumo.total_budget` |
| Disponível | "DISPONÍVEL" | `resumo.disponivel_real` (verde se ≥ 0, vermelho se < 0) |

Rodapé: "Disponível = Renda − total das metas por grupo"

---

#### Dados Buscados

| Função | Endpoint | O que traz |
|--------|----------|-----------|
| `getResumoPlano()` | `GET /plano/resumo?ano=&mes=` | renda, total_budget, disponivel_real |
| `fetchIncomeSources()` | `GET /dashboard/income-sources` | Total de receitas |
| `fetchGoals()` | `GET /budget/?mes=` | Metas com valor_realizado |
| `fetchAportePrincipalPorMes()` | `GET /plano/aporte-mensal?mes=` | Valor de aporte planejado |

---

### TabelaReciboAnual (Cashflow)

**Arquivo:** `app_dev/frontend/src/features/plano/components/TabelaReciboAnual.tsx`

Tabela recolhível com o cashflow mensal do ano inteiro. Aparece no Plano Hub.

---

#### Header (botão toggle, largura total)
- Esquerda: "Cashflow anual [ANO]" (negrito, preto)
- Direita: Chevron ↑ quando expandido, ↓ quando recolhido
- Fundo: branco, hover: cinza-50

---

#### Tabela (quando expandida)

**Colunas:**
| Coluna | Descrição |
|--------|-----------|
| Mês | "Jan/2024", "Fev/2024"... |
| Renda | Receita do mês (formato compacto: "25k", "1,5M", "—") |
| Gastos | Total de despesas do mês |
| Aporte | Valor investido/guardado |
| Saldo | Renda − Gastos − Aporte (vermelho se negativo) |
| Status | Ícone de situação (coluna estreita) |
| Calculadora | Botão para abrir modal de detalhe (coluna estreita) |

**Ícones de Status:**
- ✓ verde = ok (mês dentro do plano)
- ✗ vermelho = negativo (saldo negativo)
- ◐ âmbar = parcial (dentro, mas não ideal)
- ○ cinza = futuro (mês ainda não aconteceu)

**Rodapé da tabela:**
- Fundo: cinza-50, negrito, borda dupla no topo
- "Resumo [ANO]" | [totalRenda] | [totalGastos] | [totalAporte] | [totalSaldo]
- Saldo: vermelho-600 se negativo

**Alerta abaixo da tabela** (se houver meses negativos):
- Texto âmbar: "X mês/meses com saldo negativo"

---

#### Modal de Detalhe (botão calculadora)

Cobre a tela: overlay preto/50, centralizado, modal branco arredondado.

**Header do modal:**
- Título: "Cálculo exato — [Mês]/[Ano]"
- Botão X (fechar)

**Conteúdo do modal (rolável):**

1. **Fórmula** (caixa cinza, fonte monospace):
   - Texto exato do cálculo realizado (ex: `SUM(Valor) WHERE MesFatura = '2026-01'`)

2. **Filtro de MesFatura:**
   - "Filtro MesFatura: [valor]"

3. **Grid de Totais (2 colunas):**
   - Caixa azul-50: "Total realizado: R$ X.XXX"
   - Caixa âmbar-50: "Total planejado: R$ X.XXX"

4. **Fonte usada:**
   - "Fonte usada: [fonte] → Valor exibido: [valor]"

5. **Quantidade:**
   - "[N] transações somadas"

6. **Realizado por grupo:**
   - Lista: "• Alimentação: R$ 850"

7. **Planejado por grupo:**
   - Lista: "• Alimentação: R$ 1.200"

8. **Adicionar Gasto Extraordinário** (separador + seção):
   - Estado inicial: botão "+" com "Adicionar gasto extraordinário"
   - Ao clicar, formulário inline:
     - Descrição: "Coisas que você lembra no meio do caminho (ex: IPVA, presente, conserto)"
     - Input texto: "Descrição (ex: IPVA)"
     - Input número: "Valor (ex: 1500 ou 1500,50)"
     - Botão **"Adicionar"** (índigo, desabilitado se vazio) → `POST /plano/expectativas` com `tipo_expectativa = "sazonal_plano"`
     - Botão **"Cancelar"** → fecha o formulário
   - Após adicionar: limpa o formulário, atualiza os dados de cashflow

9. **Tabela de transações** (scroll interno, máx. 48 de altura):
   - Cabeçalho fixo: Estabelecimento | Valor | Grupo | Data
   - Linhas: estabelecimento truncado (com tooltip no hover), valor, grupo, data

---

#### Dados Buscados

| Função | Endpoint | O que traz |
|--------|----------|-----------|
| `getCashflow(ano)` | `GET /plano/cashflow?ano=` | Array de meses com renda, gastos, aporte, saldo, status |
| `getCashflowDetalheMes(ano, mes)` | `GET /plano/cashflow/detalhe-mes?ano=&mes=` | Detalhamento completo do cálculo do mês |
| `postExpectativa()` | `POST /plano/expectativas` | Cria gasto extraordinário |

---

### ProjecaoChart

**Arquivo:** `app_dev/frontend/src/features/plano/components/ProjecaoChart.tsx`

Gráfico de linha mostrando projeção de patrimônio acumulado ao longo do ano. Aparece no Plano Hub.

---

#### Header do Card
- Título: "Projeção de poupança"
- Descrição: "Patrimônio acumulado mês a mês. Subir = guardando mais; descer = gastando mais que a renda."
- **Slider "Reduzir gastos em:"**
  - Range: 0% a 50%, passo de 5%
  - Exibe o valor à direita (ex: "0%", "15%")
  - Ao mexer no slider: recalcula linha laranja no gráfico (sem nova requisição)
  - Botões − e + ao lado do slider

---

#### Gráfico (Recharts LineChart)

- Altura do container: 256px (h-64)
- Grid: linhas tracejadas, cinza claro
- Eixo X: meses (ex: "Jan/2026")
- Eixo Y: valores compactos ("25k", "1,5M", valores negativos com −)
- Tooltip (hover): exibe "Mês [label]: R$ X.XXX,XX" (formato completo)

**Até 3 linhas:**

| Linha | Cor | Traço | Condição de exibição |
|-------|-----|-------|---------------------|
| Real | Verde (#22c55e) | Sólido | Só meses em que `use_realizado = true` no cashflow |
| Plano | Índigo (#6366f1) | Sólido | Sempre |
| Plano com redução | Âmbar (#f59e0b) | Tracejado ("4 2") | Só quando slider > 0% |

---

#### Rodapé do Card
- Texto xs, cinza-600
- Se slider = 0: "Fim do ano: XXXk"
- Se slider > 0: "Base: XXXk · Com X% economia: XXXk"

---

#### Estados

| Estado | O que aparece |
|--------|--------------|
| Carregando | Spinner (índigo, animate-spin) |
| Erro | Mensagem de erro em vermelho |
| Sem dados | "Sem dados de projeção" |
| Com dados | Gráfico completo |

---

#### Dados Buscados

| Função | Endpoint | O que traz |
|--------|----------|-----------|
| `getProjecao(ano, 12, reducaoPct)` | `GET /plano/projecao?meses=12&reducao_pct=` | Série de projeção (plano + plano com redução) |
| `getCashflow(ano)` | `GET /plano/cashflow?ano=` | Cashflow com flag `use_realizado` para linha verde |

---

### EditGoalModal

**Arquivo:** `app_dev/frontend/src/features/goals/components/EditGoalModal.tsx`

Modal de edição de meta. Aparece na tela de Detalhe da Meta.

---

#### Estrutura Visual

- **Overlay**: cobre tela inteira, fundo preto/50
- **Modal**: branco, topo arredondado (mobile: abre de baixo), máx. 90% da altura, rolável
- **Animação**: `animate-slide-up` (sobe de baixo para cima)

---

#### Header do Modal (fixo no topo do modal)

- Esquerda: Botão **X** (fechar) — desabilitado se salvando/deletando
- Centro: "Editar Meta"
- Direita: Botão **"Salvar"** (texto azul, sem fundo)
  - Exibe "Salvando..." durante envio
  - Desabilitado se salvando ou deletando

Abaixo: data da meta em texto xs cinza (right-align)

---

#### Formulário

**Campo 1 — Nome da Meta** (obrigatório):
- Label: "Nome da Meta *"
- Input de texto
- Placeholder: "Ex: Alimentação, Casa, Carro"
- Fundo: cinza-50, borda cinza-200, arredondado-xl, focus: anel azul

**Campo 2 — Descrição** (opcional):
- Label: "Descrição (opcional)"
- Input de texto
- Placeholder: "Ex: Gastos com supermercado e restaurantes"

**Campo 3 — Cor no gráfico** (color picker):
- Label: "Cor no gráfico"
- Grade de bolinhas coloridas (w-8 h-8, arredondadas)
  - Selecionada: borda cinza-900, escala 110%
  - Não selecionada: sem borda, hover: escala 105%
- Link "Remover cor personalizada" (aparece se houver cor selecionada)

**Campo 4 — Orçamento Mensal** (obrigatório):
- Label: "Orçamento Mensal *"
- Input de texto com "R$" como prefixo sobreposto
- `inputMode="decimal"` (abre teclado numérico no mobile)
- Placeholder: "0.00"
- Aceita: apenas números e ponto/vírgula decimal

**Info Box** (azul-50, borda azul-200):
- Ícone de info (azul-600)
- "Sobre o orçamento"
- Explicação: "O valor planejado será comparado com suas transações reais do mês..."

**Seção Recorrência** (separada por borda no topo):
- Label: "Recorrência"
- Checkbox estilizado: "Aplicar para meses posteriores"
  - Quando marcado: fundo azul-50, borda azul-200
  - Texto de explicação: "As alterações serão aplicadas para todos os meses seguintes"

---

#### Rodapé do Modal (fixo no fundo do modal, com borda no topo)

1. **Botão Salvar** (principal):
   - Gradiente azul-500 → azul-600
   - Texto branco, arredondado-2xl, py-4, negrito
   - Sombra + hover: sombra maior + scale
   - "Salvando..." durante envio

2. **Botão Deletar** (secundário):
   - Fundo branco, texto vermelho-600, borda vermelho-200
   - Arredondado-2xl, py-4, negrito, hover: fundo vermelho-50
   - "Excluindo..." durante processo

---

#### Modal de Confirmação de Deleção

Abre sobre o EditGoalModal.
- Overlay adicional
- Título: "Excluir meta"
- Descrição: "Deseja realmente excluir a meta "[nome]"? Esta ação não pode ser desfeita."
- Botão **"Cancelar"** (contorno)
- Botão **"Excluir"** (vermelho destrutivo, "Excluindo..." durante processo)

---

#### Validações

| Campo | Regra | Mensagem de erro |
|-------|-------|-----------------|
| Nome | Obrigatório, não vazio | Toast de erro |
| Orçamento | Obrigatório, > 0 | Toast de erro |

---

#### API

- **onSave(data)**: chamado com `{ nome, descricao, orcamento, cor, aplicarMesesFuturos }`
- **onDelete()**: chamado após confirmação de deleção

---

### NudgeBanners

**Arquivo:** `app_dev/frontend/src/features/onboarding/NudgeBanners.tsx`

Exibe **apenas um banner por vez**, baseado em prioridade. Aparece no topo do Dashboard.

---

#### Lógica de Prioridade

Verifica cada condição em ordem. Mostra o **primeiro** que for verdadeiro e ainda não foi fechado pelo usuário:

1. **"sem_upload"** — Usuário nunca fez upload
2. **"sem_plano"** — Fez upload, mas não criou plano
3. **"sem_investimento"** — Tem plano, mas não adicionou investimentos
4. **"upload_30_dias"** — Último upload foi há mais de 30 dias

---

#### Aparência de Cada Nudge

**sem_upload:**
- Fundo azul-50, borda azul-200
- Ícone Upload
- "Suba seu extrato e veja para onde vai seu dinheiro"
- Botão "Fazer upload" (contorno azul) → `/mobile/upload`
- Botão X (fechar)

**sem_plano:**
- Fundo índigo-50, borda índigo-200
- Ícone Alvo
- "Ótimo início! Crie seu Plano para ter um orçamento real"
- Botão "Criar plano" (contorno índigo) → `/mobile/plano`
- Botão X (fechar)

**sem_investimento:**
- Fundo verde-50, borda verde-200
- Ícone Carteira
- "Complete seu patrimônio! Adicione seus investimentos"
- Botão "Adicionar" (contorno verde) → `/mobile/carteira`
- Botão X (fechar)

**upload_30_dias:**
- Fundo âmbar-50, borda âmbar-200
- Ícone RefreshCw (atualizar)
- "Hora de atualizar! Suba o extrato de [MÊS ANTERIOR]"
- Botão "Atualizar" (contorno âmbar) → `/mobile/upload`
- Botão X (fechar)

---

#### Persistência

- Ao fechar um nudge: salva em `localStorage["nudge_dismissed_[tipo]"] = "true"`
- Nudge fechado não aparece mais até limpar o localStorage
- Ao carregar: verifica localStorage antes de decidir qual nudge mostrar

---

#### Dados Buscados

| Endpoint | O que verifica |
|----------|---------------|
| `GET /api/v1/onboarding/progress` | `primeiro_upload`, `plano_criado`, `investimento_adicionado`, `ultimo_upload_em` |

---

### EmptyState

**Arquivo:** `app_dev/frontend/src/components/empty-state.tsx`

Componente padronizado para estados vazios.

---

#### Layout

```
[ícone emoji grande]
[título]
[descrição]
[botão primário CTA]
[link secundário opcional]
```

- Container: flex coluna, items-center, justify-center, py-20, px-6, text-center
- Ícone: span com `role="img"`, tamanho text-5xl
- Título: h3, text-lg, semibold, cinza-900
- Descrição: p, text-sm, cor muted, max-w-xs
- Botão primário: Link + Button, texto com " →" no final
- Link secundário: texto pequeno, hover: sublinhado

---

#### Props

| Prop | Tipo | Descrição |
|------|------|-----------|
| `icon` | string | Emoji (ex: "📋", "🎯") |
| `title` | string | Título do estado vazio |
| `description` | string | Explicação |
| `ctaLabel` | string | Texto do botão primário |
| `ctaHref` | string | Rota do botão primário |
| `ctaSecondaryLabel` | string? | Texto do link secundário |
| `ctaSecondaryHref` | string? | Rota do link secundário |

---

#### Usos no App

| Tela | Ícone | Primário | Secundário |
|------|-------|----------|-----------|
| Plano Hub (sem dados) | 📋 | "Construir plano" → `/mobile/construir-plano` | "Subir extrato primeiro" → `/mobile/upload` |
| Budget (sem metas) | 🎯 | "Criar plano" → `/mobile/budget/new` | — |

---

## Resumo: Mapa de Navegação

```
/mobile/dashboard
  ├── → /mobile/profile (engrenagem no header)
  ├── → /mobile/upload (ícone upload no header)
  └── → /mobile/transactions ("Ver todas as transações")

/mobile/plano
  ├── → /mobile/construir-plano ("Editar plano" card / CTA vazio)
  ├── → /mobile/upload (CTA vazio)
  └── → /mobile/budget/manage ("Gerenciar metas" card)

/mobile/construir-plano
  └── → /mobile/plano (ao finalizar wizard)

/mobile/budget
  ├── → /mobile/profile (ícone pessoa)
  ├── → /mobile/budget/manage (engrenagem)
  ├── → /mobile/budget/new (botão +)
  └── → /mobile/budget/[goalId]?mes= (clique na meta)

/mobile/budget/manage
  ├── → /mobile/budget (voltar / após salvar)
  ├── → /mobile/budget/[goalId]?mes= (editar meta)
  └── → /mobile/budget/new (botão Nova Meta)

/mobile/budget/[goalId]
  ├── → /mobile/budget (voltar / após deletar)
  └── → /mobile/transactions?grupo=&subgrupo= (clique em subgrupo)

/mobile/profile
  ├── → /auth/login (logout)
  ├── → /mobile/plano
  ├── → /mobile/grupos
  ├── → /mobile/cards
  ├── → /mobile/exclusions
  └── → /mobile/uploads
```

---

*Documento de referência para validação de ideias de UX e produto.*
*Para arquitetura técnica e banco de dados, ver: `docs/VISAO_GERAL_COMPLETA.md`*
