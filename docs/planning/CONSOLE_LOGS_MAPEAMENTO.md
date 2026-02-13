# 🗺️ Mapeamento Completo de Console.logs - Frontend

**Data:** 09/02/2026  
**Status:** 230 console.logs identificados após limpeza inicial  
**Progresso:** 76 logs já removidos (6 arquivos), 226 restantes

---

## 📊 Resumo Estatístico

### ✅ Arquivos Já Limpos (6 arquivos - 76 logs removidos)
1. ✅ `add-group-modal.tsx` → 17 logs removidos + bloco DEBUG INFO
2. ✅ `settings/exclusoes/page.tsx` → 16 logs removidos
3. ✅ `goals-api.ts` → 13 logs removidos
4. ✅ `settings/cartoes/page.tsx` → 11 logs removidos
5. ✅ `upload/preview/[sessionId]/page.tsx` → 10 logs removidos
6. ✅ `upload-api.ts` → 9 logs removidos

### 🎯 Logs Restantes por Categoria
- **API/Services:** ~80 logs (dashboard-api, auth, upload, etc.)
- **Pages (Desktop):** ~60 logs (budget, transactions, dashboard, settings)
- **Pages (Mobile):** ~40 logs (mobile/*, preview)
- **Components:** ~25 logs (modals, sidebars, cards)
- **Contexts/Hooks:** ~15 logs (AuthContext, hooks personalizados)
- **Outros:** ~6 logs (tests, comentários)

---

## 📂 Detalhamento por Arquivo

### 1. **app/api/[...proxy]/route.ts** (3 logs)
```typescript
Linha 100  | console.log('[Proxy] Added token from cookie');
Linha 119  | console.log(`[Proxy] ${method} ${fullUrl}`);
Linha 149  | console.error('[Proxy] Error');
```
**Prioridade:** 🔴 ALTA (API crítica)  
**Ação:** Remover logs de debug, manter apenas error logging via sistema estruturado

---

### 2. **app/budget/configuracoes/page.tsx** (3 logs)
```typescript
Linha 50   | console.error('Erro ao carregar configurações');
Linha 77   | console.error('Erro ao salvar cores');
Linha 97   | console.error('Erro ao salvar budget total');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Substituir por toast notifications

---

### 3. **app/budget/detalhada/page.tsx** (8 logs)
```typescript
Linha 176  | console.log('Categorias carregadas');
Linha 180  | console.error('Erro ao carregar categorias');
Linha 204  | console.error('Erro ao carregar orçamento detalhado');
Linha 247  | console.error('Erro ao salvar orçamento');
Linha 287  | console.error('Erro ao copiar mês anterior');
Linha 323  | console.error('Erro ao adicionar categoria');
Linha 347  | console.error('Erro ao deletar categoria');
Linha 391  | console.error('Erro ao reordenar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Substituir por error handling UI (toasts)

---

### 4. **app/budget/page.tsx** (6 logs) + **app/budget/page 2.tsx** (6 logs)
```typescript
// page.tsx
Linha 72   | console.log('Grupos carregados da API');
Linha 80   | console.error('Erro ao carregar grupos disponíveis');
Linha 111  | console.log('Budget carregado');
Linha 122  | console.error('Erro ao carregar orçamento');
Linha 167  | console.error('Erro ao salvar orçamento');
Linha 207  | console.error('Erro ao copiar mês anterior');

// page 2.tsx (arquivo duplicado - considerar remover)
Linha 72   | console.log('Grupos carregados da API');
Linha 80   | console.error('Erro ao carregar grupos disponíveis');
Linha 111  | console.log('Budget carregado');
Linha 122  | console.error('Erro ao carregar orçamento');
Linha 167  | console.error('Erro ao salvar orçamento');
Linha 207  | console.error('Erro ao copiar mês anterior');
```
**Prioridade:** 🔴 ALTA (arquivo duplicado!)  
**Ação:** 1) Remover page 2.tsx (duplicado), 2) Limpar page.tsx

---

### 5. **app/budget/planning/page.tsx** (4 logs)
```typescript
Linha 118  | console.error('Erro ao carregar planejamento');
Linha 163  | console.error('Erro ao adicionar item');
Linha 198  | console.error('Erro ao atualizar item');
Linha 224  | console.error('Erro ao remover item');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Substituir por toasts

---

### 6. **app/budget/simples/page.tsx** (9 logs)
```typescript
Linha 80   | console.error('Erro ao buscar grupos');
Linha 110  | console.log('Grupos carregados');
Linha 111  | console.log('Médias calculadas');
Linha 116  | console.error('Erro ao carregar grupos');
Linha 162  | console.error('Erro ao carregar orçamento');
Linha 208  | console.error('Erro ao salvar orçamento');
Linha 272  | console.error('Erro ao copiar mês anterior');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug, manter error handling

---

### 7. **app/dashboard/mobile/page.tsx** (2 logs)
```typescript
Linha 71   | console.error('Error fetching metrics');
Linha 107  | console.error('Error fetching chart data');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile crítico)  
**Ação:** Silent errors ou toast

---

### 8. **app/dashboard/page.tsx** (4 logs) + **app/dashboard/page 2.tsx** (4 logs)
```typescript
// page.tsx
Linha 157  | console.error('Error fetching metrics');
Linha 210  | console.error('Error fetching chart data');
Linha 250  | console.error('Error fetching category data');
Linha 362  | console.log('🔄 Atualizando dashboard manualmente...');

// page 2.tsx (duplicado - remover)
Linha 157  | console.error('Error fetching metrics');
Linha 210  | console.error('Error fetching chart data');
Linha 250  | console.error('Error fetching category data');
Linha 362  | console.log('🔄 Atualizando dashboard manualmente...');
```
**Prioridade:** 🔴 ALTA (dashboard principal + duplicado)  
**Ação:** 1) Remover page 2.tsx, 2) Limpar page.tsx

---

### 9. **app/mobile/budget/edit/page.tsx** (4 logs)
```typescript
Linha 66   | console.error('Erro ao buscar orçamentos');
Linha 71   | console.log('Dados recebidos');
Linha 93   | console.error('Erro ao buscar orçamentos');
Linha 143  | console.error('Erro ao salvar metas');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile)  
**Ação:** Remover logs de debug

---

### 10. **app/mobile/budget/manage/page.tsx** (5 logs)
```typescript
Linha 45   | console.log(`✅ Meta ${goal.nome} ${!currentState ? 'ativada' : 'desativada'}`);
Linha 47   | console.error('Failed to toggle goal');
Linha 66   | console.log(`✅ Valor da meta ${goal.nome} atualizado`);
Linha 71   | console.error('Failed to update goal value');
Linha 84   | console.error('Failed to save changes');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile)  
**Ação:** Substituir por feedback visual

---

### 11. **app/mobile/budget/new/page.tsx** (1 log)
```typescript
Linha 98   | console.error('Erro ao salvar meta');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast de erro

---

### 12. **app/mobile/dashboard/page.tsx** (5 logs)
```typescript
Linha 56   | console.log('✅ Último mês com dados');
Linha 59   | console.error('❌ Erro ao buscar último mês');
Linha 82   | console.log('🎯 Dashboard Page - expenseSources');
Linha 83   | console.log('🎯 Dashboard Page - totalDespesas');
Linha 84   | console.log('🎯 Dashboard Page - loadingExpenses');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile dashboard)  
**Ação:** Remover logs de debug

---

### 13. **app/mobile/preview/[sessionId]/page.tsx** (4 logs)
```typescript
Linha 72   | console.log('🔍 DEBUG - Dados recebidos do backend');
Linha 73   | console.log('🔍 DEBUG - Primeiro registro');
Linha 133  | console.log('🔍 DEBUG - Transações agrupadas');
Linha 134  | console.log('🔍 DEBUG - Total de grupos/transações');
```
**Prioridade:** 🔴 ALTA (logs de DEBUG explícitos)  
**Ação:** Remover todos os logs de DEBUG

---

### 14. **app/mobile/profile/page.tsx** (3 logs)
```typescript
Linha 77   | console.error('Erro ao carregar perfil');
Linha 135  | console.error('Erro ao atualizar perfil');
Linha 189  | console.error('Erro ao alterar senha');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast de erro

---

### 15. **app/mobile/transactions/page.tsx** (4 logs)
```typescript
Linha 73   | console.error('Não autenticado. Redirecionando para login...');
Linha 86   | console.error('Erro ao buscar transações');
Linha 189  | console.log('Clicked transaction');
Linha 201  | console.log('Nova transação');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile transações)  
**Ação:** Remover logs de debug

---

### 16. **app/mobile/upload/page.tsx** (9 logs) 🔴 PRIORIDADE ALTA
```typescript
Linha 54   | console.group('✅ [MOBILE-UPLOAD] Auto-login bem-sucedido');
Linha 55   | console.log('👤 Usuário');
Linha 56   | console.log('🔑 Token recebido (primeiros 30 chars)');
Linha 57   | console.groupEnd();
Linha 60   | console.error('❌ [MOBILE-UPLOAD] Falha no auto-login');
Linha 63   | console.error('[mobile-upload] Erro no auto-login');
Linha 99   | console.group('🚀 [MOBILE-UPLOAD] handleSubmit iniciado');
Linha 100  | console.log('📋 Formulário');
Linha 108  | console.log('📎 Arquivo');
Linha 113  | console.log('🔑 Autenticado?', isAuthenticated());
Linha 114  | console.groupEnd();
Linha 156  | console.log('✅ [MOBILE-UPLOAD] Upload bem-sucedido! SessionId');
Linha 160  | console.error('❌ [MOBILE-UPLOAD] Erro no upload');
```
**Prioridade:** 🔴 ALTA (muitos logs com console.group)  
**Ação:** Remover todos os logs de debug e grupos

---

### 17. **app/settings/admin/page.tsx** (9 logs) 🔴 PRIORIDADE ALTA
```typescript
Linha 79   | console.error('Erro ao buscar usuários');
Linha 95   | console.log('Editando usuário');
Linha 105  | console.log('Salvando usuário. Modo edição');
Linha 123  | console.log('URL');
Linha 124  | console.log('Method');
Linha 149  | console.error('Erro do servidor');
Linha 168  | console.error('Erro ao salvar usuário');
Linha 194  | console.error('Erro ao deletar usuário');
Linha 232  | console.error('Erro ao alterar senha');
```
**Prioridade:** 🔴 ALTA (página de admin)  
**Ação:** Remover logs de debug, manter error handling estruturado

---

### 18. **app/settings/categorias-genericas/page.tsx** (7 logs)
```typescript
Linha 134  | console.error('Erro');
Linha 148  | console.error('Erro ao carregar stats');
Linha 160  | console.error('Erro ao carregar opções de grupo');
Linha 192  | console.error('Erro');
Linha 211  | console.error('Erro');
Linha 227  | console.error('Erro');
Linha 243  | console.error('Erro');
Linha 263  | console.error('Erro');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Melhorar mensagens de erro e usar toasts

---

### 19. **app/settings/grupos/page.tsx** (1 log)
```typescript
Linha 112  | console.error('Erro ao carregar opções');
```
**Prioridade:** 🟢 BAIXA  
**Ação:** Toast de erro

---

### 20. **app/settings/page.tsx** (2 logs) + **app/settings/page 2.tsx** (2 logs)
```typescript
// page.tsx
Linha 91   | console.error('Erro ao buscar bancos');
Linha 116  | console.error('Erro ao salvar banco');

// page 2.tsx (duplicado - remover)
Linha 91   | console.error('Erro ao buscar bancos');
Linha 116  | console.error('Erro ao salvar banco');
```
**Prioridade:** 🔴 ALTA (duplicado)  
**Ação:** Remover page 2.tsx

---

### 21. **app/settings/profile/page.tsx** (2 logs)
```typescript
Linha 77   | console.error('Erro ao salvar perfil');
Linha 131  | console.error('Erro ao alterar senha');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toasts

---

### 22. **app/settings/screens/page.tsx** (3 logs)
```typescript
Linha 191  | console.error('Erro ao buscar telas');
Linha 240  | console.warn(`Screen não encontrado no banco`);
Linha 279  | console.error('Erro ao salvar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Error handling estruturado

---

### 23. **app/transactions/migracoes/page.tsx** (3 logs)
```typescript
Linha 118  | console.error("Erro ao carregar opções");
Linha 157  | console.error("Erro ao gerar preview");
Linha 204  | console.error("Erro ao executar migração");
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toasts

---

### 24. **app/transactions/mobile/page.tsx** (1 log)
```typescript
Linha 57   | console.error('Error fetching transactions');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile)  
**Ação:** Silent error ou toast

---

### 25. **app/transactions/page.tsx** (4 logs)
```typescript
Linha 219  | console.error('Erro ao buscar total filtrado');
Linha 288  | console.error('Erro ao buscar transações');
Linha 372  | console.error('Erro ao buscar transações');
Linha 419  | console.error('Erro ao atualizar IgnorarDashboard');
```
**Prioridade:** 🟠 MÉDIA-ALTA (página principal)  
**Ação:** Error handling estruturado

---

### 26. **app/upload/confirm-ai/page.tsx** (6 logs)
```typescript
Linha 141  | console.error('Erro ao recuperar arquivo da sessão');
Linha 167  | console.log('Dados processados');
Linha 187  | console.log('Dados classificados');
Linha 214  | console.error('Erro no processamento');
Linha 313  | console.log('Transações confirmadas');
Linha 319  | console.error('Erro ao confirmar transações');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug

---

### 27. **app/upload/confirm/page.tsx** (3 logs)
```typescript
Linha 145  | console.error('Erro ao buscar sessão de upload');
Linha 245  | console.log('Salvando transações');
Linha 253  | console.error('Erro ao salvar transações');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug

---

### 28. **app/upload/page.tsx** (1 log)
```typescript
Linha 64   | console.error('Erro ao buscar histórico');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 29. **components/app-sidebar.tsx** (4 logs) + **components/app-sidebar 2.tsx** (4 logs)
```typescript
// app-sidebar.tsx
Linha 395  | console.log('[AppSidebar] Sem token, não carregando status de telas');
Linha 407  | console.error('[AppSidebar] Erro ao carregar status');
Linha 415  | console.error('[AppSidebar] Resposta não é um array');
Linha 425  | console.error('[AppSidebar] Erro ao carregar status');

// app-sidebar 2.tsx (duplicado)
Linha 391  | console.log('[AppSidebar] Sem token, não carregando status de telas');
Linha 403  | console.error('[AppSidebar] Erro ao carregar status');
Linha 411  | console.error('[AppSidebar] Resposta não é um array');
Linha 421  | console.error('[AppSidebar] Erro ao carregar status');
```
**Prioridade:** 🔴 ALTA (componente global + duplicado)  
**Ação:** 1) Remover app-sidebar 2.tsx, 2) Limpar app-sidebar.tsx

---

### 30. **components/mobile/budget-edit-bottom-sheet.tsx** (1 log)
```typescript
Linha 69   | console.error('Erro ao salvar meta');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 31. **components/mobile/tracker-card.tsx** (1 log - comentado)
```typescript
Linha 195  | *   onClick={() => console.log('Card clicado')}
```
**Prioridade:** 🟢 BAIXA (comentário)  
**Ação:** Remover comentário

---

### 32. **components/mobile/transaction-card.tsx** (2 logs - comentados)
```typescript
Linha 227  | *   onClick={() => console.log('Transaction clicked')}
Linha 235  | *   onClick={() => console.log('Income clicked')}
```
**Prioridade:** 🟢 BAIXA (comentários)  
**Ação:** Remover comentários

---

### 33. **contexts/AuthContext.tsx** (2 logs) + **contexts/AuthContext 2.tsx** (5 logs)
```typescript
// AuthContext.tsx
Linha 79   | console.error('Erro no login');
Linha 114  | console.error('Erro ao carregar usuário');

// AuthContext 2.tsx (duplicado - remover)
Linha 73   | console.log('[AuthContext] Login bem-sucedido');
Linha 87   | console.log('[AuthContext] Login completo');
Linha 93   | console.error('Erro no login');
Linha 128  | console.error('Erro ao carregar usuário');
```
**Prioridade:** 🔴 ALTA (contexto de autenticação + duplicado)  
**Ação:** 1) Remover AuthContext 2.tsx, 2) Limpar AuthContext.tsx

---

### 34. **core/hooks/use-require-auth.ts** (2 logs)
```typescript
Linha 37   | console.warn('🚨 [AUTH] Usuário não autenticado - Redirecionando para login');
Linha 66   | console.warn('🚨 [AUTH] Usuário não autenticado - Redirecionando para login');
```
**Prioridade:** 🔴 ALTA (hook de autenticação)  
**Ação:** Remover logs, manter lógica de redirect

---

### 35. **core/utils/api-client.ts** (1 log - comentado)
```typescript
Linha 83   | * console.log(resumo.total_investido)
```
**Prioridade:** 🟢 BAIXA (comentário)  
**Ação:** Remover comentário

---

### 36. **features/auth/hooks/use-token.ts** (6 logs)
```typescript
Linha 15   | console.error('Erro ao salvar token');
Linha 24   | console.error('Erro ao recuperar token');
Linha 34   | console.error('Erro ao remover token');
Linha 52   | console.error('Erro ao validar token');
Linha 61   | console.error('Erro ao decodificar token');
Linha 73   | console.error('Erro ao extrair user_id');
```
**Prioridade:** 🔴 ALTA (gerenciamento de tokens)  
**Ação:** Silent errors, crítico para segurança

---

### 37. **features/banks/hooks/use-banks.ts** (1 log)
```typescript
Linha 22   | console.error('[useBanks] Erro ao buscar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 38. **features/budget/components/budget-media-drilldown-modal.tsx** (2 logs) + **budget-media-drilldown-modal-old.tsx** (2 logs)
```typescript
// budget-media-drilldown-modal.tsx
Linha 162  | console.error('Erro ao carregar detalhamento');
Linha 165  | console.error('Erro ao carregar detalhamento');

// budget-media-drilldown-modal-old.tsx (arquivo old - considerar remover)
Linha 90   | console.error('Erro ao carregar detalhamento');
Linha 93   | console.error('Erro ao carregar detalhamento');
```
**Prioridade:** 🟠 MÉDIA-ALTA (remover arquivo old)  
**Ação:** Deletar -old.tsx, limpar modal principal

---

### 39. **features/categories/components/category-form-modal.tsx** (1 log)
```typescript
Linha 72   | console.error('Erro ao salvar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 40. **features/categories/hooks/use-categories.ts** (1 log)
```typescript
Linha 21   | console.error('[useCategories] Erro ao buscar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 41. **features/dashboard/components/bar-chart.tsx** (2 logs)
```typescript
Linha 65   | console.log('📊 BarChart - Dados da API');
Linha 66   | console.log('📊 BarChart - displayData gerado');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug

---

### 42. **features/dashboard/components/budget-vs-actual.tsx** (1 log)
```typescript
Linha 66   | console.error('Error fetching budget vs actual');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 43. **features/dashboard/components/credit-card-expenses.tsx** (1 log)
```typescript
Linha 65   | console.error('Erro ao buscar dados dos cartões');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 44. **features/dashboard/components/mobile/budget-mobile.tsx** (1 log)
```typescript
Linha 58   | console.error('Error fetching budget');
```
**Prioridade:** 🟠 MÉDIA-ALTA (mobile)  
**Ação:** Silent error

---

### 45. **features/dashboard/components/tipo-gasto-breakdown-modal.tsx** (1 log)
```typescript
Linha 70   | console.error('Erro ao buscar subgrupos');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 46. **features/dashboard/hooks/use-dashboard.ts** (4 logs)
```typescript
Linha 129  | console.log('🔍 useExpenseSources - Buscando despesas');
Linha 131  | console.log('✅ useExpenseSources - Dados recebidos');
Linha 135  | console.log('📊 useExpenseSources - Sources');
Linha 136  | console.log('💰 useExpenseSources - Total');
```
**Prioridade:** 🟠 MÉDIA-ALTA (hook de dashboard)  
**Ação:** Remover logs de debug

---

### 47. **features/dashboard/services/dashboard-api.ts** (7 logs) 🔴 PRIORIDADE ALTA
```typescript
Linha 95   | console.log('🌐 fetchExpenseSources - URL');
Linha 97   | console.log('📡 fetchExpenseSources - Response status');
Linha 101  | console.log('📦 fetchExpenseSources - Raw data');
Linha 102  | console.log('📦 fetchExpenseSources - Budgets array');
Linha 106  | console.log('🔍 Antes do filtro - total budgets');
Linha 109  | console.log('🔍 Filtrando item');
```
**Prioridade:** 🔴 ALTA (serviço crítico de dashboard)  
**Ação:** Remover todos os logs de debug

---

### 48. **features/goals/components/EditGoalModal.tsx** (2 logs)
```typescript
Linha 73   | console.error('Erro ao salvar meta');
Linha 92   | console.error('Erro ao excluir meta');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toasts

---

### 49. **features/goals/components/ManageGoalsListItem.tsx** (1 log)
```typescript
Linha 48   | console.error('Erro ao salvar');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 50. **features/goals/hooks/use-edit-goal.ts** (1 log)
```typescript
Linha 52   | console.log('TODO');
```
**Prioridade:** 🟢 BAIXA (comentário TODO)  
**Ação:** Implementar ou remover

---

### 51. **features/goals/hooks/use-goal-detail.ts** (1 log)
```typescript
Linha 28   | console.error('Erro ao carregar meta');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 52. **features/goals/hooks/use-goals.ts** (1 log)
```typescript
Linha 31   | console.error('Erro ao carregar metas');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 53. **features/investimentos/components/__tests__/export-investimentos.test.tsx** (4 logs)
```typescript
Linha 89   | global.console.log = jest.fn()
Linha 90   | // Mock console.log
Linha 217  | // Mock console.log para simular delay
Linha 218  | global.console.log = jest.fn().mockImplementation(() => {...})
```
**Prioridade:** 🟢 BAIXA (testes - mocks válidos)  
**Ação:** Manter (parte do teste)

---

### 54. **features/investimentos/components/error-boundary.tsx** (1 log)
```typescript
Linha 34   | console.error('Erro capturado no ErrorBoundary');
```
**Prioridade:** 🟠 MÉDIA-ALTA (error boundary)  
**Ação:** Manter para debug crítico ou enviar para sistema de logging

---

### 55. **features/investimentos/components/export-investimentos.tsx** (4 logs)
```typescript
Linha 177  | console.log(`✅ ${investimentos.length} investimentos exportados para CSV`);
Linha 180  | console.error('Erro ao exportar CSV');
Linha 198  | console.log(`✅ ${investimentos.length} investimentos exportados para Excel`);
Linha 201  | console.error('Erro ao exportar Excel');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Substituir por toasts

---

### 56. **features/investimentos/components/simulador-cenarios.tsx** (5 logs)
```typescript
Linha 99   | console.error('Erro ao buscar patrimônio atual');
Linha 254  | console.error('Erro ao simular cenário');
Linha 328  | console.error('Erro ao salvar cenário');
Linha 360  | console.log('📊 Valores da Simulação');
Linha 376  | console.log('💰 Cálculo Rentabilidade');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug, manter error handling

---

### 57. **features/investimentos/hooks/use-error-handling.ts** (1 log)
```typescript
Linha 42   | console.error('Error captured');
```
**Prioridade:** 🟠 MÉDIA-ALTA (hook de error handling)  
**Ação:** Manter ou enviar para sistema de logging

---

### 58. **features/investimentos/hooks/use-investimentos.ts** (1 log)
```typescript
Linha 54   | console.error('Erro ao carregar investimentos');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 59. **features/investimentos/hooks/use-rendimentos-timeline.ts** (1 log)
```typescript
Linha 36   | console.error('Erro ao carregar timeline');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 60. **features/investimentos/hooks/use-toast-notifications.ts** (1 log)
```typescript
Linha 19   | console.log(`[${type.toUpperCase()}] ${options.title}`, options.description)
```
**Prioridade:** 🟢 BAIXA (hook de notificações)  
**Ação:** Remover ou tornar condicional (dev mode)

---

### 61. **features/preview/lib/constants.ts** (2 logs)
```typescript
Linha 29   | console.log('✅ Grupos carregados');
Linha 30   | console.log('✅ Subgrupos por grupo');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Remover logs de debug

---

### 62. **features/preview/templates/PreviewLayout.tsx** (4 logs)
```typescript
Linha 37   | console.log('🔍 DEBUG - Resposta da API grupos-subgrupos');
Linha 41   | console.error('❌ Erro ao buscar grupos/subgrupos');
Linha 44   | console.error('❌ Erro ao buscar grupos/subgrupos');
Linha 114  | console.log('Transações para importar');
```
**Prioridade:** 🟠 MÉDIA-ALTA (preview de upload)  
**Ação:** Remover logs de DEBUG

---

### 63. **features/transactions/components/edit-transaction-modal.tsx** (5 logs)
```typescript
Linha 101  | console.error('Erro ao buscar grupos');
Linha 121  | console.error('Erro na resposta');
Linha 125  | console.error('Erro ao salvar');
Linha 147  | console.error('Erro na resposta');
Linha 151  | console.error('Erro ao excluir');
```
**Prioridade:** 🟠 MÉDIA-ALTA (modal de edição)  
**Ação:** Substituir por toasts

---

### 64. **features/upload/components/upload-dialog.tsx** (5 logs)
```typescript
Linha 268  | console.log('🔍 Compatibilidade carregada');
Linha 282  | console.log('📊 Compatibilidade processada');
Linha 285  | .catch(err => console.error('❌ Erro ao buscar compatibilidade'));
Linha 291  | console.log('💳 Cartões carregados');
Linha 294  | .catch(err => console.error('❌ Erro ao buscar cartões'));
```
**Prioridade:** 🟠 MÉDIA-ALTA (dialog de upload)  
**Ação:** Remover logs de debug

---

### 65. **features/upload/hooks/use-banks.ts** (1 log)
```typescript
Linha 24   | console.error('Erro ao carregar bancos');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 66. **features/upload/hooks/use-credit-cards.ts** (1 log)
```typescript
Linha 24   | console.error('Erro ao carregar cartões');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 67. **features/upload/hooks/use-preview-data.ts** (1 log)
```typescript
Linha 29   | console.error('Erro ao carregar preview');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Silent error

---

### 68. **features/upload/hooks/use-upload.ts** (1 log)
```typescript
Linha 45   | console.error('Erro no upload');
```
**Prioridade:** 🟡 MÉDIA  
**Ação:** Toast

---

### 69. **lib/api-client.ts** (1 log) + **lib/api-client 2.ts** (1 log)
```typescript
// api-client.ts
Linha 45   | console.warn('[API] 401 Unauthorized - Redirecionando para login')

// api-client 2.ts (duplicado - remover)
Linha 45   | console.warn('[API] 401 Unauthorized - Redirecionando para login')
```
**Prioridade:** 🔴 ALTA (client de API + duplicado)  
**Ação:** 1) Remover api-client 2.ts, 2) Limpar api-client.ts

---

### 70. **lib/db-config.ts** (1 log) + **lib/db-config 2.ts** (1 log)
```typescript
// db-config.ts
Linha 65   | console.log('🗄️ Abrindo banco (ÚNICO para toda aplicação)');

// db-config 2.ts (duplicado - remover)
Linha 65   | console.log('🗄️ Abrindo banco (ÚNICO para toda aplicação)');
```
**Prioridade:** 🔴 ALTA (config de DB + duplicado)  
**Ação:** 1) Remover db-config 2.ts, 2) Remover log de db-config.ts

---

## 🚨 Arquivos Duplicados - REMOVER IMEDIATAMENTE

Foram identificados **8 arquivos duplicados** que devem ser removidos:

1. ❌ `app/budget/page 2.tsx` → Usar apenas `page.tsx`
2. ❌ `app/dashboard/page 2.tsx` → Usar apenas `page.tsx`
3. ❌ `app/settings/page 2.tsx` → Usar apenas `page.tsx`
4. ❌ `components/app-sidebar 2.tsx` → Usar apenas `app-sidebar.tsx`
5. ❌ `contexts/AuthContext 2.tsx` → Usar apenas `AuthContext.tsx`
6. ❌ `lib/api-client 2.ts` → Usar apenas `api-client.ts`
7. ❌ `lib/db-config 2.ts` → Usar apenas `db-config.ts`
8. ❌ `features/budget/components/budget-media-drilldown-modal-old.tsx` → Usar apenas sem -old

**Comando para remover:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src
rm "app/budget/page 2.tsx"
rm "app/dashboard/page 2.tsx"
rm "app/settings/page 2.tsx"
rm "components/app-sidebar 2.tsx"
rm "contexts/AuthContext 2.tsx"
rm "lib/api-client 2.ts"
rm "lib/db-config 2.ts"
rm "features/budget/components/budget-media-drilldown-modal-old.tsx"
```

---

## 🎯 Plano de Limpeza Sugerido

### Fase 1 - Remoção de Duplicados (Imediato)
- [ ] Remover 8 arquivos duplicados listados acima
- **Impacto:** -24 logs (aproximadamente)

### Fase 2 - Arquivos Críticos de Segurança (Alta Prioridade)
- [ ] `app/api/[...proxy]/route.ts` (3 logs)
- [ ] `features/auth/hooks/use-token.ts` (6 logs)
- [ ] `core/hooks/use-require-auth.ts` (2 logs)
- [ ] `contexts/AuthContext.tsx` (2 logs)
- [ ] `lib/api-client.ts` (1 log)
- **Impacto:** -14 logs | **Total acumulado:** -38 logs

### Fase 3 - Mobile Critical (Alta Prioridade)
- [ ] `app/mobile/upload/page.tsx` (9 logs + console.group)
- [ ] `app/mobile/preview/[sessionId]/page.tsx` (4 logs DEBUG)
- [ ] `app/mobile/dashboard/page.tsx` (5 logs)
- [ ] `app/mobile/transactions/page.tsx` (4 logs)
- **Impacto:** -22 logs | **Total acumulado:** -60 logs

### Fase 4 - Settings/Admin (Alta Prioridade)
- [ ] `app/settings/admin/page.tsx` (9 logs)
- [ ] `components/app-sidebar.tsx` (4 logs)
- **Impacto:** -13 logs | **Total acumulado:** -73 logs

### Fase 5 - Dashboard Services (Alta Prioridade)
- [ ] `features/dashboard/services/dashboard-api.ts` (7 logs)
- [ ] `features/dashboard/hooks/use-dashboard.ts` (4 logs)
- [ ] `app/dashboard/page.tsx` (4 logs)
- **Impacto:** -15 logs | **Total acumulado:** -88 logs

### Fase 6 - Budget Pages (Média Prioridade)
- [ ] `app/budget/simples/page.tsx` (9 logs)
- [ ] `app/budget/detalhada/page.tsx` (8 logs)
- [ ] `app/budget/page.tsx` (6 logs)
- [ ] `app/budget/planning/page.tsx` (4 logs)
- [ ] `app/budget/configuracoes/page.tsx` (3 logs)
- **Impacto:** -30 logs | **Total acumulado:** -118 logs

### Fase 7 - Upload/Preview (Média Prioridade)
- [ ] `app/upload/confirm-ai/page.tsx` (6 logs)
- [ ] `features/upload/components/upload-dialog.tsx` (5 logs)
- [ ] `features/preview/templates/PreviewLayout.tsx` (4 logs)
- [ ] `app/upload/confirm/page.tsx` (3 logs)
- **Impacto:** -18 logs | **Total acumulado:** -136 logs

### Fase 8 - Transactions (Média Prioridade)
- [ ] `features/transactions/components/edit-transaction-modal.tsx` (5 logs)
- [ ] `app/transactions/page.tsx` (4 logs)
- [ ] `app/transactions/migracoes/page.tsx` (3 logs)
- **Impacto:** -12 logs | **Total acumulado:** -148 logs

### Fase 9 - Investimentos (Média Prioridade)
- [ ] `features/investimentos/components/simulador-cenarios.tsx` (5 logs)
- [ ] `features/investimentos/components/export-investimentos.tsx` (4 logs)
- **Impacto:** -9 logs | **Total acumulado:** -157 logs

### Fase 10 - Componentes Diversos (Baixa Prioridade)
- [ ] Todos os outros componentes com 1-3 logs cada
- [ ] Remover comentários com console.log
- **Impacto:** ~50-60 logs | **Total acumulado:** ~210-220 logs

---

## 📊 Estatísticas por Tipo de Log

- **console.log (debug):** ~90 logs (40%)
- **console.error:** ~120 logs (52%)
- **console.warn:** ~5 logs (2%)
- **console.group/groupEnd:** ~8 logs (3%)
- **Comentários com console:** ~7 logs (3%)

**Total:** 230 logs

---

## ✅ Progresso Atual

### Já Limpos (6 arquivos - 76 logs)
- ✅ add-group-modal.tsx (17)
- ✅ settings/exclusoes/page.tsx (16)
- ✅ goals-api.ts (13)
- ✅ settings/cartoes/page.tsx (11)
- ✅ upload/preview/[sessionId]/page.tsx (10)
- ✅ upload-api.ts (9)

### Progresso Total
- **Limpos:** 76 / 302 logs (25%)
- **Restantes:** 226 logs (75%)
- **Arquivos limpos:** 6 arquivos
- **Arquivos com logs:** ~70 arquivos

---

## 🛠️ Scripts Úteis

### Verificar logs restantes por arquivo:
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
grep -r "console\." app_dev/frontend/src --include="*.ts" --include="*.tsx" -c | grep -v ":0$" | sort -t: -k2 -rn
```

### Contar total de logs:
```bash
grep -r "console\." app_dev/frontend/src --include="*.ts" --include="*.tsx" | grep -v node_modules | wc -l
```

### Verificar arquivo específico:
```bash
grep -n "console\." app_dev/frontend/src/PATH/TO/FILE.tsx
```

---

## 📝 Notas Importantes

1. **Arquivos de teste (.test.tsx):** Manter console.log nos mocks
2. **Error boundaries:** Considerar manter console.error para debug crítico
3. **API errors:** Preferir toasts/notificações UI em vez de console.error
4. **Debug logs:** Remover TODOS os logs com emojis/DEBUG
5. **console.group:** Remover TODOS (overhead de performance)

---

**Documento criado em:** 09/02/2026  
**Última atualização:** 09/02/2026  
**Autor:** GitHub Copilot  
**Versão:** 1.0
