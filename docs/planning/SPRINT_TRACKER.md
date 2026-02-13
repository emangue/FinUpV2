# 📊 Sprint Tracker - Integração Mobile Protótipos

**Data de Início:** 06/02/2026  
**Data de Conclusão:** [Em andamento]  
**Status Geral:** ✅ Sprint 3.2 Concluída → Dashboard Mobile Completo!

---

## 📚 Documentação do Projeto - Guia de Consulta

### 🎯 Antes de Começar - Leitura Obrigatória

| Documento | Localização | Quando Consultar | Tempo de Leitura |
|-----------|-------------|------------------|------------------|
| **MOBILE_INTEGRATION_PLAN.md** | `docs/planning/` | 📖 **LER PRIMEIRO** - Plano mestre completo com todos os detalhes | 45-60 min |
| **PROTOTYPES_FULL_ANALYSIS.md** | `docs/planning/` | 🔍 Dúvida sobre backend/APIs/tabelas de cada protótipo | 15-20 min |

### 📊 Durante Dashboard - Referências Específicas

| Documento | Localização | Quando Consultar |
|-----------|-------------|------------------|
| **DASHBOARD_RESEARCH_FINDINGS.md** | `docs/dashboard/` | Comparação desktop vs mobile vs protótipo |
| **DASHBOARD_COMPARISON_VISUAL.md** | `docs/dashboard/` | Diagramas visuais das diferenças |
| **DASHBOARD_ACTION_ITEMS.md** | `docs/dashboard/` | Tarefas específicas do dashboard |
| **README_DASHBOARD_RESEARCH.md** | `docs/dashboard/` | Índice da pesquisa de dashboard |

### 🏗️ Arquitetura e Processos

| Documento | Localização | Quando Consultar |
|-----------|-------------|------------------|
| **WOW.md** | `docs/` | Processo de desenvolvimento (PRD → Tech Spec → Sprint) |
| **ANALISE_MOBILE_V1_BENCHMARK.md** | `docs/` | Exemplo de implementação mobile anterior (85% perfeito) |

### 📋 Templates Para Criar Documentos

| Template | Localização | Quando Usar |
|----------|-------------|-------------|
| **TEMPLATE_PRD.md** | `docs/templates/` | Criar PRD de nova feature |
| **TEMPLATE_TECH_SPEC.md** | `docs/templates/` | Especificação técnica detalhada |
| **TEMPLATE_SPRINT.md** | `docs/templates/` | Documentar conclusão de sprint |
| **TEMPLATE_FIX.md** | `docs/templates/` | Documentar bugs e fixes |

---

## 🎯 Checklist Pré-Execução (20 minutos)

Executar **ANTES** de começar qualquer sprint:

- [ ] **1. Criar branch de feature**
  ```bash
  git checkout -b feature/mobile-prototypes-integration
  git push -u origin feature/mobile-prototypes-integration
  ```

- [ ] **2. Backup do banco de dados**
  ```bash
  ./scripts/deploy/backup_daily.sh
  ls -lh app_dev/backend/database/backups_daily/
  ```

- [ ] **3. Validar servidores rodando**
  ```bash
  curl http://localhost:8000/api/health  # Backend
  curl http://localhost:3000/            # Frontend
  ```

- [ ] **4. Instalar dependências frontend**
  ```bash
  cd app_dev/frontend
  npm install react-window @types/react-window react-virtuoso
  ```

- [ ] **5. Criar estrutura de pastas**
  ```bash
  mkdir -p app_dev/frontend/src/app/mobile/{upload,preview,insights,goals}
  mkdir -p app_dev/frontend/src/features/upload/{components,hooks,types,utils}
  ```

- [ ] **6. Criar tag git (checkpoint)**
  ```bash
  git tag -a v-mobile-integration-start -m "Checkpoint: início integração mobile"
  git push origin v-mobile-integration-start
  ```

---

## 📅 Week 1 - Upload & Preview Mobile

### ✅ Sprint 1.1: Upload Frontend (CONCLUÍDO)

**🎯 Objetivo:** Tela de upload mobile com auto-login

**Status:** ✅ CONCLUÍDO (06/02/2026)

**📋 Tarefas Realizadas:**
- [x] Página de upload mobile criada em `/app/mobile/upload/page.tsx`
- [x] Auto-login implementado (paliativo DEV)
- [x] Componentes integrados:
  - BankSelector (API real)
  - CardSelector (API real)
  - FormatSelector
  - FileInput (drag & drop)
  - MonthYearPicker
- [x] Validação de campos implementada
- [x] Feedback visual de loading
- [x] Teste em mobile Chrome DevTools

**✅ Critérios de Conclusão:**
- [x] UI renderiza corretamente em mobile
- [x] Drag & drop funciona
- [x] Seletores funcionam com API real
- [x] Botão upload mostra feedback

**🐛 Bugs Encontrados:**
- ✅ Corrigido: BankSelector enviava ID em vez de nome
- ✅ Corrigido: Format precisava ser uppercase (CSV, Excel)
- ✅ Corrigido: Card precisava enviar nome + final digits

**📊 Tempo Real:** ~6 horas (estimado: 6-8h) ✅ Dentro do estimado

---

### ✅ Sprint 1.2: Upload Backend Real (CONCLUÍDO)

**🎯 Objetivo:** Conectar frontend com API de upload existente

**Status:** ✅ CONCLUÍDO (06/02/2026)

**📋 Tarefas Realizadas:**
- [x] Hook `useUpload` criado em `features/upload/hooks/use-upload.ts`
- [x] Conectado: `POST /api/v1/upload/preview`
- [x] BankSelector → `GET /api/v1/banks`
- [x] CardSelector → `GET /api/v1/cards`
- [x] Upload retorna sessionId
- [x] Redirect para `/mobile/preview/{sessionId}` implementado

**✅ Critérios de Conclusão:**
- [x] Upload envia arquivo real
- [x] sessionId retornado e capturado
- [x] Redirecionamento automático funciona
- [x] Loading states corretos

**🐛 Bugs Encontrados:**
- ✅ Corrigido: Mapeamento de campos (banco nome vs ID)
- ✅ Corrigido: Validação de formato uppercase

**📊 Tempo Real:** ~3 horas (estimado: 2-3h) ✅ Dentro do estimado

---

### ✅ Sprint 1.3: Preview Frontend + Backend (CONCLUÍDO)

**🎯 Objetivo:** Tela de preview com classificação e dados reais

**Status:** ✅ CONCLUÍDO (06/02/2026)

**📋 Tarefas Realizadas:**
- [x] Página de preview mobile criada em `/app/mobile/preview/[sessionId]/page.tsx`
- [x] Componentes extraídos e funcionais:
  - [x] FileInfoCard - exibe banco, cartão, arquivo, mês, soma total
  - [x] TransactionCard - exibe transação com grupo/subgrupo/origem
  - [x] TransactionList - lista com filtros
  - [x] TabBar - 8 filtros (todas, classificadas, não classificadas, etc)
  - [x] PreviewLayout - template principal

**Funcionalidades Implementadas:**
- [x] **Agrupamento inteligente de transações**
  - Agrupa por: description + grupo + subgrupo
  - Transações com mesmo nome mas grupos diferentes ficam separadas
  - Exibe contagem de ocorrências
  - Cards expansíveis para ver itens do grupo

- [x] **Classificação de transações**
  - Dropdowns sempre habilitados (mesmo já classificado)
  - Grupos e subgrupos carregados de `/api/v1/categories/grupos-subgrupos`
  - Mesma base que "Gestão de Categorias"
  - Auto-save ao selecionar grupo + subgrupo
  - Reclassificação muda origem para "Manual"

- [x] **Exibição de dados**
  - Valores formatados em R$ (validação contra NaN)
  - Origem da classificação visível e com cores
  - FileInfo com totalizadores
  - Cálculo correto de soma total

- [x] **Integração com Backend**
  - `GET /api/v1/upload/preview/{sessionId}` - busca dados
  - `GET /api/v1/categories/grupos-subgrupos` - busca categorias
  - Autenticação via fetchWithAuth (JWT)
  - Mapeamento correto de campos da API

**✅ Critérios de Conclusão:**
- [x] Preview carrega dados reais do sessionId
- [x] Agrupamento funciona corretamente
- [x] Valores exibidos sem NaN
- [x] Dropdowns populados com dados reais
- [x] Classificação persiste visualmente (backend save pendente)
- [x] Origem visível e diferenciada por cor
- [x] Tabs filtram (implementação básica)

**🐛 Bugs Encontrados e Corrigidos:**
- ✅ NaN nos valores - corrigido com validação no formatCurrency
- ✅ Import paths (@/types vs ../types) - corrigido
- ✅ Data mapping (Valor vs valor) - corrigido
- ✅ Agrupamento simples - corrigido para incluir grupo/subgrupo na chave
- ✅ Dropdowns desabilitados quando classificado - corrigido, agora sempre habilitados
- ✅ Grupos/subgrupos hardcoded - corrigido, agora vem da API
- ✅ Erro 401 ao buscar categorias - corrigido usando fetchWithAuth
- ✅ TypeError "data.map is not a function" - corrigido formato da API

**⚠️ Pendências para Sprint 1.4:**
- [ ] Salvar classificação no backend (atualmente só visual)
- [ ] Botão "Confirmar Importação" funcional
- [ ] API de confirmação
- [ ] Feedback de sucesso/erro

**📊 Tempo Real:** ~8 horas (estimado: 16-18h frontend + 4-6h backend = 20-24h)  
**⚠️ Observação:** Muitas funcionalidades já existiam ou foram simplificadas, economizando ~12-16h

---

### 🔵 Sprint 1.4: Confirmar Importação (PRÓXIMA)

**🎯 Objetivo:** Permitir salvar classificações e confirmar importação

**Status:** 🔵 PRÓXIMA - Pronta para iniciar

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Backend API Preview" (linha ~750)

**📋 Tarefas:**
- [ ] **Salvar classificação no backend**
  - Endpoint atual: `PATCH /api/v1/upload/preview/{sessionId}/{previewId}`
  - Params: `?grupo=X&subgrupo=Y`
  - Implementar no `handleBatchUpdate` do PreviewLayout
  - Atualizar origem para "Manual" quando reclassificar
  - Tempo estimado: 2h

- [ ] **Implementar botão "Confirmar Importação"**
  - No `BottomActionBar`
  - Desabilitar se `stats.naoClassificadas > 0`
  - Loading state durante confirmação
  - Tempo estimado: 1h

- [ ] **API de confirmação**
  - Endpoint: `POST /api/v1/upload/confirm/{sessionId}`
  - Validar que todas estão classificadas
  - Inserir em `journal_entries`
  - Retornar resumo de importação
  - Tempo estimado: 2h

- [ ] **Feedback de sucesso**
  - Modal de confirmação
  - Resumo: "X transações importadas com sucesso"
  - Botão "Ver Dashboard"
  - Botão "Novo Upload"
  - Tempo estimado: 1h

- [ ] **Tratamento de erros**
  - Duplicatas detectadas → exibir aviso
  - Erro de validação → exibir mensagem
  - Erro de banco → retry ou cancelar
  - Tempo estimado: 1h

- [ ] **Limpeza de sessão**
  - DELETE após confirmação ou cancelamento
  - Limpar arquivos temporários
  - Tempo estimado: 30min

**✅ Critérios de Conclusão:**
- [ ] Classificação salva no backend em tempo real
- [ ] Botão Confirmar só habilitado quando 100% classificado
- [ ] Confirmação importa para journal_entries
- [ ] Modal de sucesso exibe resumo
- [ ] Erros tratados gracefully
- [ ] Sessão limpa após conclusão

**🐛 Bugs Conhecidos:**
- Nenhum ainda

**📊 Tempo Estimado:** 7-8 horas

---

## 📅 Week 1 - Metas Mobile

### � Sprint 2.1: Metas Frontend (EM ANDAMENTO)

**🎯 Objetivo:** Tela de metas funcionando com dados reais de `budget_planning`

**Status:** 🟡 EM ANDAMENTO (06/02/2026)

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "4️⃣ Metas (Goals)" (linha ~1050)  
  ⚠️ **ATENÇÃO:** Planejamento original previa `budget_geral`, mas decisão tomada foi usar `budget_planning`
- docs/features/mobile-v1/02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md → Análise completa das 2 tabelas
- docs/features/mobile-v1/02-TECH_SPEC/API_SPEC.md → APIs de `/budget/planning`

**🔄 DECISÃO TÉCNICA CRITICAL:**

| Planejado Original | Decisão Real | Motivo |
|-------------------|--------------|--------|
| Estender `budget_geral` com colunas (tipo_meta, ativo, icone, cor) | ✅ Usar `budget_planning` COMO ESTÁ | ✅ Já tem grupos (Alimentação, Casa, Carro)<br>✅ APIs já existem<br>✅ 0 migrations necessárias<br>✅ Alinha com tela desktop "Budget Simples" |
| Criar migration Alembic | ❌ CANCELADO | Não precisa - tabela já serve |
| Criar campos novos | ❌ CANCELADO | Campos existentes são suficientes |
| Criar endpoints toggle/delete | ⚠️ OPCIONAL | Bulk-upsert já permite CRUD completo |

**📋 Tarefas Realizadas (Tela 1: Goals List):**
- [x] **Estrutura de features criada**
  - `features/goals/types/index.ts` - Interface Goal adaptada de budget_planning
  - `features/goals/lib/utils.ts` - Helpers (formatCurrency, calculateStatus, etc)
  - `features/goals/components/index.ts` - Export barrel
  
- [x] **Componentes criados**
  - [x] GoalCard (exibe meta com progresso, valor atual vs alvo)
  - [x] DonutChart (overview de todas metas do mês com segmentos coloridos)
  - [x] Export barrel para facilitar imports
  
- [x] **Integração com API real**
  - [x] `features/goals/services/goals-api.ts` criado
  - [x] Conectado: `GET /api/v1/budget/planning?mes_referencia=YYYY-MM`
  - [x] Mapeamento: budget_planning → Goal interface
  - [x] Estrutura descoberta: `{ mes_referencia, budgets: [...] }`
  - [x] Hook `useGoals(selectedMonth)` criado
  - [x] useEffect reage a mudança de mês
  
- [x] **Página principal criada**
  - Destino: `app_dev/frontend/src/app/mobile/budget/page.tsx`
  - [x] MobileHeader com botão + (nova meta)
  - [x] MonthScrollPicker (scroll horizontal de meses)
  - [x] DonutChart mostrando visão geral
  - [x] Filtros: Todas(16) / Ativas(16) / Concluídas(0) / Atrasadas(0)
  - [x] Lista de GoalCards com dados reais (16 metas em Fev/2026)

**🔍 Bugs Encontrados e Corrigidos:**
- ✅ API retornava `{ budgets: [...] }` mas código esperava `{ planning: [...] }` - CORRIGIDO
- ✅ Campos com maiúsculas (Grupo, Orcamento) vs minúsculas - normalização implementada
- ✅ useGoals não aceitava selectedMonth - parâmetro adicionado
- ✅ fetchGoals não usava selectedMonth - integração completa

**✅ Critérios de Conclusão (Tela 1 - Concluída):**
- [x] Tela renderiza corretamente
- [x] Dados reais carregam de `budget_planning`
- [x] DonutChart mostra visão geral com cores
- [x] GoalCards exibem progresso corretamente
- [x] MonthScrollPicker funciona
- [x] Filtros contam corretamente (16 metas)
- [x] Navegação para /mobile/budget/[id] configurada

**📋 Tarefas Realizadas (Tela 2: Goal Details):**
- [x] **Estrutura de página criada**
  - Destino: `app_dev/frontend/src/app/mobile/budget/[goalId]/page.tsx`
  - Roteamento dinâmico com `useParams()` para capturar goalId
  - Integração com `useGoalDetail(goalId)` hook
  
- [x] **Componentes implementados**
  - [x] MobileHeader com botões ArrowLeft (voltar) e Edit2 (editar)
  - [x] Progress Circle (SVG) com cores dinâmicas:
    * Verde (<75% do orçamento)
    * Laranja (75-99%)
    * Vermelho (≥100% - estourou orçamento)
  - [x] Values Grid (Gasto, Meta, Restante) formatados em R$
  - [x] Transaction History placeholder (TODO: integrar com API)
  - [x] Bottom Actions (Voltar, Editar Meta)
  
- [x] **API corrigida**
  - `fetchGoalById()` atualizado para usar `data.budgets || data.planning || data.items`
  - Normalização de campos (Grupo vs grupo, Orcamento vs orcamento)
  - Consistente com `fetchGoals()`

**🔍 Bugs Encontrados e Corrigidos:**
- ✅ fetchGoalById usava estrutura antiga (data.planning) - CORRIGIDO para data.budgets
- ✅ Falta de normalização de campos da API - IMPLEMENTADA
- ✅ Import path incorreto MobileHeader (`@/components/mobile-header`) - CORRIGIDO para `@/components/mobile/mobile-header`

**✅ Critérios de Conclusão (Tela 2 - ✅ CONCLUÍDA):**
- [x] Estrutura criada com roteamento dinâmico
- [x] useGoalDetail hook integrado
- [x] Progress circle com cores responsivas
- [x] Valores formatados corretamente
- [x] Import paths corrigidos
- [x] Build sem erros
- [x] ✅ **TESTADO (07/02):** Navegação funcionando - clica em GoalCard e abre detalhes
- [x] ✅ **TESTADO (07/02):** Carregamento de dados correto
- [x] ✅ **TESTADO (07/02):** Botão voltar funciona

**⚠️ Pendências (Telas 3, 4):**
- [x] ✅ **CONCLUÍDA (07/02):** Edit Goal (modal overlay)
  - ✅ EditGoalModal component criado
  - ✅ useEditGoal hook criado
  - ✅ Integração com Goal Details concluída
  - ✅ Bug corrigido: apiClient → fetchWithAuth
  - ✅ Bug corrigido: mes_referencia → prazo (interface Goal)
  - ✅ **TESTADO (07/02):** Edição de meta funcionando
  - ✅ **TESTADO (07/02):** Validação de campos OK
  - ✅ **TESTADO (07/02):** Refresh automático após save
- [ ] 🔵 **PRÓXIMA:** Manage Goals (ativar/desativar/deletar)
- [ ] Transaction History integration (Goal Details - integrar com API de transações)

**📊 Dados de Teste Verificados:**
- ✅ Feb/2026: 16 metas (Casa R$6000, Carro R$1500, Alimentação R$500, etc)
- ✅ Valores reais vindos de `budget_planning.valor_planejado`
- ✅ Progresso calculado (valor_atual vs valor_alvo)
- ✅ Navegação configurada: `/mobile/budget/${goalId}`

**📊 Tempo Real:** ~10 horas (estimado original: 12-14h para 4 telas)  
**✅ Concluído:** Telas 1, 2 e 3 (Goals List, Goal Details, Edit Goal)  
**⏸️ Pendente:** Tela 4 (Manage Goals) - estimativa 2-3h

---

### ❌ Sprint 2.2: Migration budget_geral (CANCELADA)

**🎯 Objetivo:** Adicionar colunas para metas em budget_geral

**Status:** ❌ CANCELADA - Decisão de usar `budget_planning` torna desnecessário

**📖 Motivo do Cancelamento:**
- ✅ `budget_planning` já tem estrutura adequada (grupos por mês)
- ✅ Evita migration complexa (9 colunas)
- ✅ Reutiliza APIs existentes 100%
- ✅ Alinha com tela desktop "Budget Simples"

**📊 Tempo Economizado:** ~1-2h (migration + testes + validação)

---

### ❌ Sprint 2.3: Metas Backend (CANCELADA)

**🎯 Objetivo:** Estender budget APIs + criar 2 endpoints novos

**Status:** ❌ CANCELADA - APIs de `budget_planning` já existem e funcionam

**📖 Motivo do Cancelamento:**
- ✅ `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` já existe
- ✅ `POST /api/v1/budget/planning/bulk-upsert` já existe (CRUD completo)
- ✅ Filtros por mês já funcionam nativamente
- ✅ Não precisa de toggle/delete específico (bulk-upsert zera valores)

**APIs Existentes Reutilizadas:**
```bash
# Listar metas do mês
GET /api/v1/budget/planning?mes_referencia=2026-02

# Criar/Atualizar metas (bulk)
POST /api/v1/budget/planning/bulk-upsert
Body: {
  "mes_referencia": "2026-02",
  "budgets": [
    { "grupo": "Casa", "valor_planejado": 6000 },
    { "grupo": "Carro", "valor_planejado": 1500 }
  ]
}
```

**📊 Tempo Economizado:** ~3-4h (endpoints + model + testes)

---

### ⚠️ Sprint 2.4: Metas Integração (SIMPLIFICADA → Parte da 2.1)

**🎯 Objetivo:** Conectar frontend metas com backend real

**Status:** ⚠️ SIMPLIFICADA - Integração já foi feita na Sprint 2.1

**📖 O que foi feito (já concluído):**
- [x] Hook `useGoals(selectedMonth)` criado
- [x] Service `goals-api.ts` conectado em `GET /budget/planning`
- [x] Mapeamento `budget_planning → Goal interface`
- [x] CRUD básico funciona (GET para leitura, bulk-upsert para escrita)

**📋 Tarefas Restantes (se necessário):**
- [ ] Create Goal (modal ou página `/mobile/budget/new`)
- [ ] Update Goal (requer ID específico ou bulk-upsert?)
- [ ] Delete Goal (zerar valor_planejado ou remover?)

**📊 Tempo Real:** Já incluído na Sprint 2.1 (~1h do total de 4h)

---

## 📅 Week 2 - Dashboard Mobile (Redesign)

### ✅ Sprint 3.1: Dashboard Backend (CONCLUÍDO)

**🎯 Objetivo:** Criar 2 APIs novas para dashboard

**Status:** ✅ CONCLUÍDO (08/02/2026)

**📋 Tarefas Realizadas:**
- [x] GET /dashboard/income-sources criada
  - Breakdown de receitas por fonte (grupo)
  - SQL: GROUP BY GRUPO WHERE CategoriaGeral='Receita'
  - Calcula percentuais automaticamente
  - Retorna: sources[] + total_receitas

- [x] Enhancement GET /dashboard/metrics
  - Adicionado campo change_percentage
  - Compara mês atual vs mês anterior
  - Casos especiais: month=1 (vs Dez ano anterior), month=None (null)
  - Formato: float com 1 decimal

- [x] Testes realizados
  ```bash
  curl /dashboard/income-sources?year=2026&month=1
  # Retornou: {"sources":[{"fonte":"Salário","total":2080.58,"percentual":100.0,"num_transacoes":1}],"total_receitas":2080.58}
  
  curl /dashboard/metrics?year=2026&month=2
  # Retornou: change_percentage=-100.0 (mês sem transações)
  ```

**🐛 Bugs Encontrados e Corrigidos:**
- ✅ Sintaxe: "IncomeSources Response" → "IncomeSourcesResponse"
- ✅ Python 3.9: `float | None` → `Optional[float]`
- ✅ Campo uppercase: `JournalEntry.Grupo` → `JournalEntry.GRUPO`

**✅ Critérios de Conclusão:**
- [x] income-sources retorna dados corretos
- [x] changePercentage calculado
- [x] Performance <2s (instantâneo)
- [x] Schemas Pydantic validando corretamente

**📊 Tempo Real:** 40min (estimado: 3-4h) - bugs de sintaxe atrasaram

---

### 🔄 Sprint 3.2: Dashboard Frontend (COMPLETA)

**🎯 Objetivo:** Substituir tela simples pelo design do protótipo

**Status:** ✅ COMPLETA (23/01/2026)

**📋 Todas as 4 Fases Implementadas:**
- [x] **Fase 1: Refatorar BarChart (1h)**
  - Alturas fixas em pixels (50-125px)
  - Ordem: Despesas (gray-400) → Receitas (gray-900)
  - Width: w-2 (8px fixo)
  - Container: h-40 (160px)
  - Gap: gap-1 (4px), justify-between
  - Labels: text-[9px]

- [x] **Fase 2: DonutChart Expenses (1.5h)**
  - Hook useExpenseSources criado
  - Service fetchExpenseSources com TOP 5 logic
  - ExpenseSource type adicionado
  - Props activeTab implementada
  - Budget_planning integração completa

- [x] **Fase 3: Paleta Cinza (0.5h)**
  - GRAY_COLORS: 6 tons de cinza
  - Removidas cores vibrantes
  - Paleta aplicada em income E expenses

- [x] **Fase 4: Validação (0.5h)**
  - Servidores reiniciados (PID: 47375, 47387)
  - Testes manuais realizados
  - Visual matching com protótipo

**✅ Critérios de Conclusão:**
- [x] BarChart com alturas fixas
- [x] Ordem correta (despesas/receitas)
- [x] Cores cinzas (gray-400/gray-900)
- [x] DonutChart funciona para income E expenses
- [x] TOP 5 grupos + "Outros" em expenses
- [x] Integração com budget_planning
- [x] Paleta apenas cinzas
- [x] Labels text-[9px]
- [x] Visual idêntico ao protótipo

**📚 Documentação Criada:**
- ✅ `/docs/dashboard/PROTOTYPO_ANALISE_COMPLETA.md` - Análise + implementação

**📊 Tempo Real:** 3.5h (estimado: 3-4h) ✅ Dentro do estimado

**🎯 Componentes Modificados (6 arquivos):**
1. `features/dashboard/types/index.ts` - ExpenseSource type
2. `features/dashboard/services/dashboard-api.ts` - fetchExpenseSources
3. `features/dashboard/hooks/use-dashboard.ts` - useExpenseSources
4. `features/dashboard/components/donut-chart.tsx` - activeTab support
5. `features/dashboard/components/bar-chart.tsx` - fixed heights
6. `app/mobile/dashboard/page.tsx` - expenses integration

**🌐 Testar:** http://localhost:3000/mobile/dashboard

---

**📋 Tarefas Realizadas:**
- [x] **Substituição completa da página**
  - Origem: `app/mobile/dashboard/page.tsx` (antiga - 4 cards simples)
  - Destino: SUBSTITUÍDO pelo novo design
  - Removido: Cards simples de Receitas/Despesas/Saldo/Investimentos
  - Adicionado: Layout sofisticado com charts

- [x] **Componentes criados** (reutilizáveis)
  - [x] WalletBalanceCard (`features/dashboard/components/wallet-balance-card.tsx`)
    - Exibe saldo com variação % vs mês anterior
    - Cor dinâmica (verde/vermelho baseado em +/-)
  - [x] BarChart (`features/dashboard/components/bar-chart.tsx`)
    - Gráfico de barras para receitas vs despesas
    - Tooltip ao hover mostrando valores
    - Legend com cores
  - [x] DonutChart (`features/dashboard/components/donut-chart.tsx`)
    - Gráfico de rosca para fontes de receita
    - Segmentos coloridos com percentuais
    - Legend lateral com valores

- [x] **Infraestrutura criada**
  - [x] Types: `features/dashboard/types/index.ts`
  - [x] Service: `features/dashboard/services/dashboard-api.ts`
  - [x] Hooks: `features/dashboard/hooks/use-dashboard.ts`
    - `useDashboardMetrics(year, month)`
    - `useIncomeSources(year, month)`
    - `useChartData(year, month)`

- [x] **Integração com APIs**
  - [x] GET /dashboard/metrics (com change_percentage)
  - [x] GET /dashboard/income-sources (novo)
  - [x] GET /dashboard/chart-data (existente)
  - [x] YTD toggle funcional (mês vs ano)
  - [x] MonthScrollPicker integrado

- [x] **Features implementadas**
  - [x] Header com botão Download (placeholder)
  - [x] Date display (Mês/Ano selecionado)
  - [x] Tabs: Receitas / Despesas / Orçamento
  - [x] Loading states
  - [x] Botão "Ver Todas as Transações"

**✅ Critérios de Conclusão:**
- [x] Tela antiga COMPLETAMENTE substituída
- [x] Novo design renderiza corretamente
- [x] Charts responsivos e interativos
- [x] Dados reais das APIs
- [x] YTD toggle funciona
- [x] Performance adequada

**🎯 Comparação Antes vs Depois:**

**ANTES (Tela antiga):**
- 4 cards simples empilhados
- Apenas valores numéricos
- Sem visualização gráfica
- Sem breakdown de fontes
- Sem variação %

**DEPOIS (Nova tela):**
- WalletBalanceCard com change %
- BarChart interativo (receitas vs despesas)
- DonutChart de fontes de receita
- Tabs para filtrar visualizações
- Design moderno tipo fintech

**📊 Tempo Real:** ~1.5h (estimado: 8-10h)  
**⚠️ Observação:** Uso de componentes já criados (MonthScrollPicker, YTDToggle, MobileHeader) economizou ~6h

**🔍 ANÁLISE CRÍTICA (08/02/2026):**

Após comparação detalhada com protótipo de referência (`/dashboard/app/page.tsx`), foram identificadas **divergências críticas** que impedem o dashboard de funcionar corretamente:

| Aspecto | Protótipo Referência ✅ | Implementação Atual ❌ | Impacto |
|---------|------------------------|----------------------|---------|
| **1. Estrutura do BarChart** | Alturas fixas em pixels (65px, 80px, 95px, etc.) | Alturas proporcionais com calculateHeight() | 🔴 CRÍTICO - Barras não aparecem corretamente |
| **2. Ordem das Barras** | Expenses (cinza) PRIMEIRO, depois Income (preto) | Receitas (azul) primeiro, Despesas (vermelho) | 🟡 MÉDIO - Ordem invertida |
| **3. Cores** | Cinza (#9CA3AF) + Preto (#1F2937) | Azul (#3B82F6) + Vermelho (#EF4444) | 🟡 MÉDIO - Não match protótipo |
| **4. Gap entre barras** | gap-1 (4px) entre expense/income | gap-0.5 (2px) | 🟢 BAIXO |
| **5. Width das barras** | w-2 (8px) fixo | w-full (responsivo) | 🔴 CRÍTICO - Barras muito largas |
| **6. Container height** | h-40 (160px) | h-56 (224px) | 🟡 MÉDIO |
| **7. Months labels** | text-[9px] centralizado | text-[11px] | 🟢 BAIXO |
| **8. Labels do mês** | Estrutura separada (`<div>` fora do chart) | Dentro do flex-col | 🔴 CRÍTICO - Pode afetar layout |
| **9. Donut Chart cores** | Cinzas gradientes (#1F2937, #4B5563, #9CA3AF) | Cores variadas DEFAULT_COLORS | 🟡 MÉDIO |
| **10. Tab "Expenses"** | Mostra donut de despesas com 7 categorias | Não implementado (só income) | 🔴 CRÍTICO - Feature faltando |

**🐛 PROBLEMAS IDENTIFICADOS:**

1. **BarChart não funciona corretamente:**
   - Usa proporções dinâmicas em vez de alturas fixas
   - Barras com minHeight podem não aparecer
   - Ordem invertida (azul/vermelho vs cinza/preto)
   - Largura responsiva causa barras muito grossas

2. **Donut Chart incompleto:**
   - Funciona apenas para tab "Income"
   - Tab "Expenses" não exibe donut de categorias
   - Cores não seguem paleta cinza do protótipo

3. **Dados mockados vs reais:**
   - Protótipo usa dados fixos (5.2M, 6.1M, 7.5M, etc.)
   - Implementação usa API com dados reais (podem estar vazios em Fev/2026)
   - Fallback existe mas não segue estrutura do protótipo

**✅ O QUE ESTÁ CORRETO:**
- [x] MonthScrollPicker integrado
- [x] Tabs funcionando
- [x] WalletBalanceCard com change %
- [x] Header e navegação
- [x] Loading states

**❌ O QUE PRECISA SER CORRIGIDO:**
- [ ] BarChart: Usar alturas fixas como no protótipo
- [ ] BarChart: Inverter ordem (expenses primeiro, income depois)
- [ ] BarChart: Mudar cores (cinza + preto)
- [ ] BarChart: Usar w-2 fixo (não w-full)
- [ ] BarChart: Container h-40 (não h-56)
- [ ] DonutChart: Implementar tab "Expenses" com categorias
- [ ] DonutChart: Usar cores cinzas (#1F2937, #4B5563, #9CA3AF)
- [ ] Labels: Estrutura separada fora do chart

**📋 AÇÕES NECESSÁRIAS:**

1. **Criar arquivo de referência completo** (`/docs/dashboard/PROTOTYPO_COMPLETO.md`)
2. **Refazer BarChart** seguindo estrutura exata do protótipo
3. **Implementar DonutChart de Expenses**
4. **Ajustar cores para paleta cinza**
5. **Validar com dados mockados** antes de integrar APIs

**⏰ TEMPO ADICIONAL ESTIMADO:** 2-3h (refatoração completa)

**📚 DOCUMENTAÇÃO CRIADA:**
- ✅ `/docs/dashboard/PROTOTYPO_ANALISE_COMPLETA.md` - Análise detalhada de divergências (500+ linhas)
  * Comparação lado a lado: Protótipo vs Atual
  * Identificação de 10 divergências críticas
  * Plano de correção em 4 fases
  * Critérios de sucesso definidos

**🎯 PRÓXIMAS AÇÕES (Aguardando Aprovação):**

1. **Revisar Análise:** Ler `/docs/dashboard/PROTOTYPO_ANALISE_COMPLETA.md`
2. **Aprovar Plano:** Confirmar correções necessárias
3. **Executar Fase 1:** Refatorar BarChart (1-1.5h)
4. **Executar Fase 2:** Implementar DonutChart Expenses (0.5-1h)
5. **Executar Fase 3:** Ajustar paleta de cores (0.5h)
6. **Executar Fase 4:** Validação final (0.5h)

**⚠️ DECISÃO NECESSÁRIA:** Aprovar início das correções ou ajustar plano

---

---

### Sprint 3.3: Dashboard Backend Real (8h)

**🎯 Objetivo:** Criar 2 APIs novas para dashboard

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Dashboard Backend" (linha ~1920)
- DASHBOARD_RESEARCH_FINDINGS.md

**📋 Tarefas:**
- [ ] Criar GET /dashboard/income-sources
  - Breakdown de receitas por fonte (donut chart)
  - SQL: GROUP BY Grupo WHERE CategoriaGeral='Receita'
  - Calcular percentuais
  - Tempo: 2-3h

- [ ] Estender GET /dashboard/metrics
  - Adicionar campo changePercentage
  - Comparar mês atual vs anterior
  - Tempo: 1h

- [ ] Testar endpoints
  ```bash
  curl "http://localhost:8000/api/v1/dashboard/income-sources?year=2026&month=2"
  curl "http://localhost:8000/api/v1/dashboard/metrics?year=2026&month=2"
  ```

**✅ Critérios de Conclusão:**
- [ ] income-sources retorna dados corretos
- [ ] changePercentage calculado
- [ ] Performance <2s

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 3-4h)

---

### Sprint 3.2: Dashboard Frontend (8-10h)

**🎯 Objetivo:** Substituir mobile atual pelo design do protótipo

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "3️⃣ Dashboard Mobile" (linha ~745)
- DASHBOARD_COMPARISON_VISUAL.md

**📋 Tarefas:**
- [ ] Copiar página principal
  - Origem: `export-to-main-project/dashboard/app/page.tsx`
  - Destino: Substituir `app_dev/frontend/src/app/mobile/dashboard/page.tsx`
  - Tempo: 2h

- [ ] Extrair charts (reusáveis)
  - [ ] BarChart → `components/mobile/bar-chart.tsx` (2h)
  - [ ] DonutChart → `components/mobile/donut-chart.tsx` (2h)

- [ ] Outros componentes
  - [ ] WalletBalanceCard (1h)
  - [ ] MetricCards (1h)
  - [ ] YTDToggle (30min)

- [ ] Integrar com APIs (6 existentes + 2 novas)
  - Hooks: useDashboardMetrics, useIncomes, useChart
  - Tempo: 2h

**✅ Critérios de Conclusão:**
- [ ] Novo design renderiza corretamente
- [ ] Charts responsivos
- [ Sprint 1.1 - Upload Frontend** | 6-8h | 6h | ✅ Concluído |
| **Sprint 1.2 - Upload Backend** | 2-3h | 3h | ✅ Concluído |
| **Sprint 1.3 - Preview (Frontend+Backend)** | 20-24h | 8h | ✅ Concluído |
| **Sprint 1.4 - Confirmar Importação** | 7-8h | ___h | ⏸️ Adiada |
| **Sprint 2.1 - Metas Frontend** | 12-14h | 8h | 🟡 Em Andamento |
| **Week 1 - Upload/Preview** | 35-43h | 17h | ✅ Fase concluída |
| **Week 1 - Metas** | 18-22h | 8h | 🟡 Em Andamento |
| **Week 2 - Dashboard** | 11-14h | ___h | 🔴 Not Started |
| **TOTAL GERAL** | **64-79h** | **25h** | 🟡 32% Completo |

### Progresso por Protótipo

- [x] **Upload Mobile** (9h real vs 8-11h estimado) - ✅ 100% Completo
  - Backend: ✅ 100% (APIs já existiam)
  - Frontend: ✅ 100%
  
- [ ] **Preview Mobile** (8h real vs 20-24h estimado) - ⚠️ 80% Completo (Import adiado)
  - Backend: ✅ 95% (API de confirmação adiada)
  - Frontend: ✅ 100% (falta integrar import)
  
- [ ] **Metas** (0h vs 18-22h estimado) - 🔵 Iniciando Sprint 2.1
  - Backend: ⚠️ 90% (falta toggle/delete)
  - Frontend: 🔴 0% - **PRÓXIMA SPRINT**

### Backend APIs Criadas/Modificadas

- [x] **Sprint 1.3:** Nenhuma (todas já existiam, apenas integradas)
- [ ] **Sprint 1.4:** POST /upload/confirm/{sessionId} (Pendente)
- [ ] GET /dashboard/income-sources (Dashboard)
- [ ] Enhancement GET /dashboard/metrics (Dashboard)
- [ ] PATCH /budget/{id}/toggle (Metas)
- [ ] DELETE /budget/{id} (Metas - soft delete)

**Total:** 0/5 criadas (5 pendentes
### Progresso por Protótipo

- [ ] **Upload Mobile** (8-11h) - Backend: ✅ 100% | Frontend: 🔴 0%
- [ ] **Preview Mobile** (20-24h) - Backend: ✅ 95% | Frontend: 🔴 0%
- [ ] **Dashboard Mobile** (11-14h) - Backend: ⚠️ 75% | Frontend: 🔴 0%
- [ ] **Metas** (18-22h) - Backend: ⚠️ 90% | Frontend: 🔴 0%

### Backend APIs Criadas

- [ ] GET /dashboard/income-sources (Dashboard)
- [ ] Enhancement GET /dashboard/metrics (Dashboard)
- [ ] PATCH /budget/{id}/toggle (Metas)
- [ ] DELETE /budget/{id} (Metas - soft delete)
- [ ] PATCH /upload/preview/{id}/batch (Preview - opcional)

**Total:** 0/5 criadas (4 obrigatórias + 1 opcional)

---Agrupamento otimizado implementado | ✅ Mitigado |
| Dashboard não é novo | Médio | Documentação clara criada | ✅ Mitigado |
| Schema metas | Alto | Decisão tomada: estender budget_geral | ✅ Resolvido |
| Confirmação precisa validar duplicatas | Médio | Backend já tem lógica, reutilizar | ⚠️ Monitorar |

---

## 📝 Notas de Desenvolvimento

### Decisões Técnicas Tomadas

1. **✅ Sprint 1.3 - Agrupamento Inteligente**
   - Chave: `description + grupo + subgrupo`
   - Não agrupa se classificações diferentes
   - Economia de ~12h (lógica mais simples que estimado)

2. **✅ Sprint 1.3 - Dropdowns Sempre Habilitados**
   - Permite reclassificar transações já marcadas
   - Origem muda para "Manual" ao reclassificar
   - UX melhor que modal separado

3. **✅ Sprint 1.3 - Grupos da API Real**
   - Endpoint: `/api/v1/categories/grupos-subgrupos`
   - Mesma base que "Gestão de Categorias"
   - Formato: `{ grupos: [], subgruposPorGrupo: {} }`

4. **✅ Dashboard = Redesign** (não funcionalidade nova)
   - Desktop e mobile já existem
   - Protótipo é apenas nova UI/UX
   - Backend 100% reutilizável

5. **✅ CRÍTICO - Metas = Usar budget_planning** (NÃO budget_geral)
   - **Planejado:** Estender `budget_geral` com 9 colunas novas
   - **Decisão Real:** Usar `budget_planning` como está
   - **Motivo:**
     * ✅ Já tem grupos (Alimentação, Casa, Carro) - granularidade perfeita
     * ✅ APIs já existem (`GET /budget/planning`, `POST /budget/planning/bulk-upsert`)
     * ✅ 0 migrations necessárias
     * ✅ Alinha com tela desktop "Budget Simples"
     * ✅ Dados reais desde o dia 1 (16 metas em Fev/2026)
   - **Economia:** ~6-8h de desenvolvimento (migration + model + endpoints + testes)
   - **Referência:** docs/features/mobile-v1/02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md

### Lições Aprendidas (Sprints 1.3 e 2.1)

1. **Componentes Feature-Based funcionam melhor**
   - Estrutura: `features/{preview,goals}/{components,hooks,services,types,lib}`
   - Imports relativos evitam problemas de alias
   - Fácil de testar isoladamente

2. **Formatação de moeda precisa validação robusta**
   - Sempre validar `isNaN()` antes de formatar
   - Aceitar string ou number como input
   - Fallback para "R$ 0,00" em caso de erro

3. **Agrupamento simples é melhor**
   - Versão inicial: apenas por nome → gerava falsos positivos
   - Versão final: nome + grupo + subgrupo → preciso
   - Mais simples = menos bugs

4. **SEMPRE investigar tabelas existentes antes de criar novas**
   - Planejamento inicial: criar campos em `budget_geral`
   - Investigação: descobrir `budget_planning` já existia e servia
   - Economia: ~6-8h (migration + model + endpoints + testes)
   - **Lição:** Fazer análise técnica detalhada ANTES de planejar sprints

5. **API já tem quase tudo pronto**
   - Não assumir que precisa criar endpoints novos
   - Verificar se APIs existentes podem ser adaptadas
   - Reutilização > Criação

---

## 🎯 Progresso Geral do Projeto

**✅ Upload & Preview (Week 1):**
- [x] Upload mobile funcionando com APIs reais
- [x] Preview carrega dados do sessionId
- [x] Agrupamento de transações funcionando
- [x] Classificação com dropdowns populados
- [ ] ⏸️ **Adiado:** Salvar classificação no backend
- [ ] ⏸️ **Adiado:** Confirmar importação para journal_entries
- [ ] ⏸️ **Adiado:** Feedback de sucesso/erro

**🟡 Metas (Week 1 - Em andamento):**
- [x] Goals List (tela principal) - 16 metas carregando ✅
- [x] DonutChart com visão geral ✅
- [x] Integração com `budget_planning` ✅
- [x] MonthScrollPicker funcionando ✅
- [x] Goal Details ✅ CONCLUÍDA (07/02)
  - [x] Página com roteamento dinâmico `/mobile/budget/[goalId]`
  - [x] Progress circle com SVG e cores dinâmicas
  - [x] Values grid (Gasto, Meta, Restante)
  - [x] API fetchGoalById corrigida
  - [x] ✅ Navegação testada e funcionando
- [x] Edit Goal ✅ CONCLUÍDA (07/02)
  - [x] Modal EditGoalModal com form validado
  - [x] Hook useEditGoal com bulk-upsert
  - [x] Integração com Goal Details
  - [x] Bug fixes: apiClient → fetchWithAuth, mes_referencia → prazo
  - [x] ✅ Edição testada e funcionando (validação, refresh, delete)
- [x] Manage Goals 🟡 EM DESENVOLVIMENTO (07/02)
  - [x] Página `/mobile/budget/manage` criada
  - [x] Componente ManageGoalsListItem com toggle switches
  - [x] Lista todas as metas (gastos + investimentos)
  - [x] Toggle ativar/desativar implementado (soft delete via valor_planejado = 0)
  - [x] Botão editar navega para Goal Details
  - [x] Botão "Gerenciar" no header da lista de metas
  - [x] MonthScrollPicker adicionado (escolher mês)
  - [x] ✅ **TESTADO (08/02):** Tela funcionando com scroll de mês e edição
  - [x] ✅ **MELHORADO (08/02):** Input editável inline com debounce
  - [x] ✅ **MELHORADO (08/02):** Exibe média dos últimos 3 meses
  - [x] ✅ **MELHORADO (08/02):** Barra visual comparando meta vs média real
  - [x] ✅ **MELHORADO (08/02):** Cores dinâmicas (verde/amarelo/vermelho) baseadas em % da meta
  - [x] ✅ **BACKEND:** Retorna `valor_medio_3_meses` no endpoint
  - [x] ✅ **FRONTEND:** Interface Goal com campo `valor_medio_3_meses`
  - [x] ✅ **API:** Função `updateGoalValor()` para edição inline
  - [ ] 🔄 **Limitação:** Reativar meta não restaura orçamento original (precisa edit manual)
  - [x] ✅ Edição e validação testadas
- [ ] 🔵 **PRÓXIMA:** Manage Goals (ativar/desativar/deletar)
- [ ] Transaction History (Goal Details - transações da meta)

**🔴 Dashboard (Week 2 - Não iniciado):**
- [ ] Novo design implementado
- [ ] Charts responsivos
- [ ] Income sources funcionando
- [ ] Métricas com changePercentage

**📊 Qualidade:**
- [x] Performance: Upload/Preview <3s ✅
- [x] Performance: Goals List <2s ✅
- [x] No console errors ✅
- [x] Mobile responsive ✅

**🚀 Deploy:**
- [ ] Merge na main
- [ ] Tag de release criada
- [ ] Changelog atualizado
- [ ] Backup realizado

---

**Última Atualização:** 08/02/2026 11:30 - Emanuel  
**Próxima Ação:** Testar edição inline! Vá em http://localhost:3000/mobile/budget/manage, clique no valor, edite, e veja salvar automaticamente + barra visual da média 3 meses!  
**Estado Atual:** Servidores rodando (Backend: 19961, Frontend: 19972). ✅ Tela 4 com edição inline + média 3 meses FUNCIONANDO!  
**Concluído Hoje:** 
- ✅ Tela 3 Edit Goal - modal, edição, validação, refresh - TUDO OK!
- ✅ Tela 4 Manage Goals - implementada, testada, MonthScrollPicker adicionado, edição via botão funcionando
- ✅ **NOVO:** Input editável inline com auto-save (debounce 800ms)
- ✅ **NOVO:** Exibe média dos últimos 3 meses (valor real de gasto)
- ✅ **NOVO:** Barra visual comparando meta vs média (cores dinâmicas)
- ✅ **BACKEND:** service.py retorna valor_medio_3_meses
- ✅ **FRONTEND:** Interface + API + componente atualizados
**Tempo Real Sprint 2.1:** ~13 horas (de 12-14h estimadas) - ✅ SPRINT COMPLETA com melhorias extras!  
**Adiado:** Sprint 1.4 - Confirmar Importação (retomar depois)  
**Cancelado:** Sprints 2.2 e 2.3 - Decisão de usar `budget_planning` tornou desnecessários

3. **✅ Virtual Scrolling = react-window** (Preview)
   - Performance garantida para 100+ transações
   - Biblioteca leve e madura

### Lições Aprendidas

_Preencher durante execução_

### Melhorias Futuras

_Preencher durante execução_

---

## 🎯 Critérios de Conclusão Final

Projeto só é marcado como **completo** quando:

- [ ] **TODAS as 7 telas** implementadas e testadas
- [ ] **Fluxos completos** funcionam end-to-end:
  - [ ] Upload → Preview → Confirm → Transactions
  - [ ] Dashboard mobile com dados reais
  - [ ] Goals CRUD completo
- [ ] **Performance:**
  - [ ] App carrega em <3s
  - [ ] Preview com 100+ transações sem lag
  - [ ] Charts responsivos
- [ ] **Backend:**
  - [ ] 4-5 novos endpoints criados
  - [ ] Migration aplicada em dev
  - [ ] Logs sem erros
- [ ] **Deploy:**
  - [ ] Merge na main
  - [ ] Tag de release criada
  - [ ] Changelog atualizado

---

**Última Atualização:** {{ data_atual }}  
**Responsável:** [Nome]  
**Próxima Revisão:** [Data]
