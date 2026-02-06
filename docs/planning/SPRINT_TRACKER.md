# 📊 Sprint Tracker - Integração Mobile Protótipos

**Data de Início:** [A definir]  
**Data de Conclusão:** [A definir]  
**Status Geral:** 🟡 Planejamento Completo → Pronto para Iniciar

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

### Sprint 1.1: Upload Frontend (6-8h)

**🎯 Objetivo:** Tela de upload mobile com mock data

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → Seção "1️⃣ Upload Mobile" (linha ~540)
- PROTOTYPES_FULL_ANALYSIS.md → "Upload" (linha ~50)

**📋 Tarefas:**
- [ ] Copiar página principal
  - Origem: `export-to-main-project/upload/app/page.tsx`
  - Destino: `app_dev/frontend/src/app/mobile/upload/page.tsx`
  - Tempo: 1h

- [ ] Extrair componentes (6 componentes)
  - [ ] FileInput (drag & drop) → `features/upload/components/file-input.tsx`
  - [ ] BankSelector → `features/upload/components/bank-selector.tsx`
  - [ ] CardSelector → `features/upload/components/card-selector.tsx`
  - [ ] MonthYearPicker → `features/upload/components/month-year-picker.tsx`
  - [ ] FormatSelector → `features/upload/components/format-selector.tsx`
  - [ ] UploadForm → `features/upload/components/upload-form.tsx`
  - Tempo: 3-4h

- [ ] Criar mock data
  - Arquivo: `features/upload/mocks/mockUploadData.ts`
  - Bancos hardcoded, cartões fake
  - Tempo: 1h

- [ ] Testar em mobile (iPhone SE, 14 Pro)
  - Chrome DevTools responsive
  - Tempo: 1h

**✅ Critérios de Conclusão:**
- [ ] UI renderiza corretamente em mobile
- [ ] Drag & drop funciona
- [ ] Seletores funcionam com mock data
- [ ] Botão upload mostra feedback (sem API ainda)

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 6-8h)

---

### Sprint 1.2: Upload Backend Real (2-3h)

**🎯 Objetivo:** Conectar frontend com API de upload existente

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Backend API Upload" (linha ~590)

**📋 Tarefas:**
- [ ] Criar hook `useUpload`
  - Arquivo: `features/upload/hooks/use-upload.ts`
  - Conectar: `POST /api/v1/upload/preview`
  - Tempo: 1h

- [ ] Conectar BankSelector → `GET /api/v1/banks`
  - Tempo: 30min

- [ ] Conectar CardSelector → `GET /api/v1/cards`
  - Tempo: 30min

- [ ] Implementar progress bar
  - Upload file com acompanhamento
  - Tempo: 30min

- [ ] Redirecionar após sucesso
  - Navigate to: `/mobile/preview?sessionId={id}`
  - Tempo: 30min

**✅ Critérios de Conclusão:**
- [ ] Upload envia arquivo real
- [ ] sessionId retornado e armazenado
- [ ] Redirecionamento automático funciona
- [ ] Loading states corretos

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 2-3h)

---

### Sprint 1.3: Preview Frontend (16-18h)

**🎯 Objetivo:** Tela de preview com classificação (mock data)

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "2️⃣ Preview Mobile" (linha ~670)
- PROTOTYPES_FULL_ANALYSIS.md → "Preview-Upload" (linha ~150)

**📋 Tarefas:**
- [ ] Copiar página principal
  - Origem: `export-to-main-project/preview-upload/app/page.tsx`
  - Destino: `app_dev/frontend/src/app/mobile/preview/page.tsx`
  - Tempo: 2h

- [ ] Extrair componentes (7 componentes)
  - [ ] FileInfoCard → `features/upload/components/preview/file-info-card.tsx` (1h)
  - [ ] TransactionCard → `features/upload/components/preview/transaction-card.tsx` (2h)
  - [ ] TransactionList (virtual scroll) → `features/upload/components/preview/transaction-list.tsx` (3h)
  - [ ] ClassificationBottomSheet → `features/upload/components/preview/classification-bottom-sheet.tsx` (4h)
  - [ ] AlertValidation → `features/upload/components/preview/alert-validation.tsx` (1h)
  - [ ] BottomActionBar → `features/upload/components/preview/bottom-action-bar.tsx` (1h)
  - [ ] TabBar (8 filtros) → `features/upload/components/preview/tab-bar.tsx` (2h)

- [ ] Implementar lógica de agrupamento
  - Arquivo: `features/upload/utils/group-transactions.ts`
  - Agrupar por nome + valor
  - Tempo: 2h

- [ ] Implementar contadores
  - Arquivo: `features/upload/utils/calculate-counters.ts`
  - 8 contadores (all, classified, unclassified, etc)
  - Tempo: 1h

- [ ] Criar mock data (58 transações)
  - Arquivo: `features/upload/mocks/mockPreviewData.ts`
  - Incluir duplicatas, classificadas, não classificadas
  - Tempo: 1h

**✅ Critérios de Conclusão:**
- [ ] Lista virtualizada funciona (100+ transações sem lag)
- [ ] Tabs filtram corretamente
- [ ] Agrupamento expande/colapsa
- [ ] Classification modal abre e valida campos
- [ ] Alert de validação atualiza em tempo real
- [ ] Botão Confirmar desabilita se houver não classificadas

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 16-18h)

---

### Sprint 1.4: Preview Backend Real (4-6h)

**🎯 Objetivo:** Conectar preview com APIs reais

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Backend API Preview" (linha ~750)

**📋 Tarefas:**
- [ ] Criar hook `usePreview`
  - `GET /api/v1/upload/preview/{sessionId}`
  - Tempo: 1h

- [ ] Criar hook `useClassification`
  - `PATCH /api/v1/upload/preview/{sessionId}/classify`
  - Optimistic update
  - Tempo: 2h

- [ ] Criar hook `useConfirmation`
  - `POST /api/v1/upload/preview/{sessionId}/confirm`
  - Validação + redirect
  - Tempo: 1h

- [ ] Conectar grupos/subgrupos
  - `GET /api/v1/marcacoes/grupos`
  - Popular dropdowns
  - Tempo: 1h

- [ ] Implementar cancelamento
  - `DELETE /api/v1/upload/preview/{sessionId}`
  - Tempo: 30min

**✅ Critérios de Conclusão:**
- [ ] Preview carrega dados reais do sessionId
- [ ] Classificação salva no backend
- [ ] Confirmação importa para journal_entries
- [ ] Cancelamento deleta sessão
- [ ] Redirecionamento após confirmação funciona

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 4-6h)

---

## 📅 Week 1 - Metas Mobile (Paralelo com Upload/Preview)

### Sprint 2.1: Metas Frontend (12-14h)

**🎯 Objetivo:** 4 telas de metas com mock data

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "4️⃣ Metas (Goals)" (linha ~1050)
- PROTOTYPES_FULL_ANALYSIS.md → "Metas" (linha ~300)

**📋 Tarefas - Tela 1: Goals List (4h):**
- [ ] Copiar página principal
  - Origem: `export-to-main-project/metas/app/page.tsx`
  - Destino: `app_dev/frontend/src/app/mobile/goals/page.tsx`
  
- [ ] Extrair componentes
  - [ ] GoalCard
  - [ ] GoalsList
  - [ ] DonutChart (metas overview)
  - [ ] TabBar (Gastos/Investimentos)

**📋 Tarefas - Tela 2: Goal Details (3h):**
- [ ] Página: `app_dev/frontend/src/app/mobile/goals/[id]/page.tsx`
- [ ] ProgressCard
- [ ] MonthlyBreakdownChart
- [ ] TransactionList

**📋 Tarefas - Tela 3: Edit Goal (3h):**
- [ ] Página: `app_dev/frontend/src/app/mobile/goals/edit/[id]/page.tsx`
- [ ] GoalEditForm
- [ ] IconPicker
- [ ] ColorPicker

**📋 Tarefas - Tela 4: Manage Goals (2h):**
- [ ] Página: `app_dev/frontend/src/app/mobile/goals/manage/page.tsx`
- [ ] Active goals list
- [ ] Archived goals list
- [ ] Toggle/Delete buttons

**✅ Critérios de Conclusão:**
- [ ] 4 telas renderizam corretamente
- [ ] Navegação entre telas funciona
- [ ] Charts legíveis em mobile
- [ ] Forms validam campos

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 12-14h)

---

### Sprint 2.2: Migration budget_geral (1h)

**🎯 Objetivo:** Adicionar colunas para metas em budget_geral

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Migration budget_geral" (linha ~2060)

**📋 Tarefas:**
- [ ] Criar migration Alembic
  ```bash
  cd app_dev/backend
  source ../../.venv/bin/activate
  alembic revision -m "add meta fields to budget_geral"
  ```

- [ ] Copiar SQL do MOBILE_INTEGRATION_PLAN.md
  - 9 colunas: tipo_meta, ativo, icone, cor, ordem, alerta_80, alerta_100, descricao, prazo

- [ ] Aplicar migration
  ```bash
  alembic upgrade head
  ```

- [ ] Verificar migration aplicada
  ```bash
  alembic current
  sqlite3 app_dev/backend/database/financas_dev.db ".schema budget_geral"
  ```

**✅ Critérios de Conclusão:**
- [ ] Migration criada sem erros
- [ ] Colunas adicionadas à tabela
- [ ] alembic current mostra migration aplicada

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 1h)

---

### Sprint 2.3: Metas Backend (3-4h)

**🎯 Objetivo:** Estender budget APIs + criar 2 endpoints novos

**📖 Consultar:**
- MOBILE_INTEGRATION_PLAN.md → "Goals Backend" (linha ~1980)

**📋 Tarefas:**
- [ ] Atualizar Budget Model
  - Arquivo: `app_dev/backend/app/domains/budget/models.py`
  - Adicionar campos novos (tipo_meta, ativo, etc)
  - Tempo: 30min

- [ ] Criar endpoint PATCH /budget/{id}/toggle
  - Ativar/desativar meta
  - Tempo: 1h

- [ ] Criar endpoint DELETE /budget/{id}
  - Soft delete (não remover do banco)
  - Tempo: 1h

- [ ] Atualizar GET /budget/
  - Adicionar filtros: ?active=true&tipo_meta=gasto
  - Tempo: 1h

- [ ] Testar endpoints
  ```bash
  curl http://localhost:8000/api/v1/budget/
  curl -X PATCH http://localhost:8000/api/v1/budget/1/toggle
  ```
  - Tempo: 30min

**✅ Critérios de Conclusão:**
- [ ] 2 novos endpoints funcionam
- [ ] Filtros funcionam
- [ ] Soft delete não quebra dados existentes

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 3-4h)

---

### Sprint 2.4: Metas Integração (2-3h)

**🎯 Objetivo:** Conectar frontend metas com backend real

**📋 Tarefas:**
- [ ] Criar hook `useGoals`
  - GET /budget/?active=true
  - Tempo: 1h

- [ ] Criar hook `useGoalTransactions`
  - GET /transactions/?grupo={goal.name}
  - Calcular spent
  - Tempo: 1h

- [ ] Conectar CRUD
  - Create, Update, Delete, Toggle
  - Tempo: 1h

**✅ Critérios de Conclusão:**
- [ ] Metas carregam dados reais
- [ ] CRUD completo funciona
- [ ] Progresso calcula corretamente

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 2-3h)

---

## 📅 Week 2 - Dashboard Mobile (Redesign)

### Sprint 3.1: Dashboard Backend (3-4h)

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
- [ ] Seletor de mês atualiza dados
- [ ] YTD toggle funciona

**🐛 Bugs Encontrados:**
- Nenhum ainda

**📊 Tempo Real:** ___ horas (estimado: 8-10h)

---

## 📊 Resumo de Progresso

### Estatísticas Gerais

| Categoria | Estimado | Real | Status |
|-----------|----------|------|--------|
| **Week 1 - Upload/Preview** | 28-35h | ___h | 🔴 Not Started |
| **Week 1 - Metas** | 18-22h | ___h | 🔴 Not Started |
| **Week 2 - Dashboard** | 11-14h | ___h | 🔴 Not Started |
| **TOTAL** | **38-47h** | **___h** | 🔴 Not Started |

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

---

## 🐛 Bugs e Bloqueadores

### Bloqueadores Ativos

Nenhum no momento

### Bugs Encontrados

Nenhum no momento

### Riscos Identificados

| Risco | Impacto | Mitigação | Status |
|-------|---------|-----------|--------|
| Preview performance (100+ transações) | Alto | Virtual scrolling implementado | ✅ Mitigado |
| Dashboard não é novo | Médio | Documentação clara criada | ✅ Mitigado |
| Schema metas | Alto | Decisão tomada: estender budget_geral | ✅ Resolvido |

---

## 📝 Notas de Desenvolvimento

### Decisões Técnicas Tomadas

1. **✅ Dashboard = Redesign** (não funcionalidade nova)
   - Desktop e mobile já existem
   - Protótipo é apenas nova UI/UX
   - Backend 100% reutilizável

2. **✅ Metas = Estender budget_geral** (não criar tabela nova)
   - Reutiliza APIs de budget
   - Migration simples (9 colunas)
   - Economia de 6-8h de desenvolvimento

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
