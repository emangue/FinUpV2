# 📐 Análise de Modularidade - Sustentabilidade do App

**Data:** 14/02/2026  
**Referência:** `.github/copilot-instructions.md` (Arquitetura Modular)  
**Objetivo:** Avaliar conformidade com princípios de isolamento e identificar débitos técnicos

---

## 1. RESUMO EXECUTIVO

| Dimensão | Status | Principais Problemas |
|----------|--------|----------------------|
| **Backend - Isolamento de domínios** | 🟡 Parcial | Imports cruzados extensivos (upload, transactions, etc.) |
| **Frontend - Isolamento de features** | 🟠 Crítico | Imports cruzados, 77+ arquivos duplicados |
| **Componentes compartilhados** | 🟠 Crítico | BottomNav em dashboard, usado por 3+ features |
| **Débito técnico** | 🔴 Alto | Arquivos " 2", " 3" espalhados |
| **Estrutura de camadas** | 🟢 OK | Repository→Service→Router (backend), components→hooks→services (frontend) |

---

## 2. BACKEND - DOMÍNIOS

### 2.1 Estrutura Atual

```
app_dev/backend/app/domains/
├── auth/          ├── budget/        ├── cards/
├── categories/    ├── classification/├── compatibility/
├── dashboard/     ├── exclusoes/     ├── grupos/
├── investimentos/ ├── marcacoes/     ├── patterns/
├── screen_visibility/
├── transactions/  ├── upload/        └── users/
```

### 2.2 Mapa de Dependências Cruzadas

| Domínio | Importa de | Violação? |
|---------|------------|-----------|
| **upload** | exclusoes, compatibility, transactions, grupos, categories, budget | ⚠️ Hub - muitos domínios |
| **transactions** | grupos, patterns, categories, budget | ⚠️ Acoplado |
| **marcacoes** | grupos, categories, transactions | ⚠️ Acoplado |
| **dashboard** | transactions, budget | ⚠️ Esperado (agregação) |
| **budget** | transactions, grupos | ⚠️ Acoplado |
| **auth** | users | ✅ Aceitável (auth+users são um bounded context) |
| **classification** | upload, transactions, grupos | ⚠️ Acoplado |
| **grupos** | transactions | ⚠️ Acoplado |

### 2.3 Análise

**Pontos positivos:**
- Camadas Repository → Service → Router respeitadas
- Uso de `app.core` e `app.shared` para dependências globais
- Imports dentro do mesmo domínio seguem o padrão

**Problemas:**
1. **Upload como hub:** O domínio `upload` importa de 6+ domínios. É um orquestrador natural, mas viola o princípio "cada domínio é autocontido".
2. **Models compartilhados:** `JournalEntry`, `BaseGruposConfig`, `BaseMarcacao` são importados entre domínios. Ideal: extrair para `app.shared.models` ou usar eventos.
3. **Imports lazy (dentro de funções):** Vários `from app.domains.X` dentro de funções – evita circular imports mas indica acoplamento.

### 2.4 Recomendações Backend

| Prioridade | Ação |
|------------|------|
| Média | Documentar dependências aceitáveis (ex: dashboard→transactions é agregação) |
| Baixa | Extrair modelos compartilhados para `shared/` (refatoração grande) |
| Baixa | Avaliar event-driven para desacoplar upload de transactions |

---

## 3. FRONTEND - FEATURES

### 3.1 Imports Cruzados entre Features (VIOLAÇÃO)

| Feature origem | Feature destino | Arquivo | Componente |
|---------------|----------------|---------|------------|
| **preview** | upload | TransactionCard.tsx | AddGroupDialog |
| **investimentos** | dashboard | dashboard-investimentos-mobile.tsx | BottomNav |

**Regra violada:** *"Não importar de outras features. Criar componente compartilhado se usado por múltiplas features."*

### 3.2 Componentes Compartilhados em Features (VIOLAÇÃO)

| Componente | Localização atual | Usado por | Ação correta |
|------------|------------------|-----------|---------------|
| **BottomNav** | `features/dashboard/components/mobile/bottom-nav.tsx` | dashboard, transactions, investimentos | Mover para `components/mobile/bottom-nav.tsx` |
| **AddGroupDialog** | `features/upload/components/add-group-dialog.tsx` | preview, upload | Mover para `components/` ou criar feature `shared-dialogs` |

### 3.3 Estrutura de Index (Barrel Exports)

**Features com index.ts na raiz:** dashboard, investimentos, budget, categories, banks, transactions, upload  
**Features sem index na raiz:** preview (tem em components e types, mas não raiz), goals (parcial)

**Regra:** *"Usar index - path direto ao componente é proibido"*

Alguns imports usam path direto:
- `@/features/transactions/components/transaction-filters` (deveria ser `@/features/transactions`)
- `@/features/goals/hooks/use-goals` (OK se exportado no index)

### 3.4 Arquivos Duplicados (DÉBITO TÉCNICO CRÍTICO)

**77+ arquivos** com sufixo ` 2`, ` 3`, ` 4`, ` 5` no frontend:

| Categoria | Quantidade | Exemplos |
|-----------|------------|----------|
| components/ui | ~15 | button 5.tsx, chart 5.tsx |
| features/investimentos | ~25 | portfolio-overview 2.tsx, use-investimentos 2.ts |
| features/dashboard | ~12 | budget-vs-actual 2.tsx |
| features/transactions | ~4 | edit-transaction-modal 2.tsx |
| app/ | ~10 | page 2.tsx, layout 2.tsx |
| components/ | ~8 | app-sidebar 2.tsx |

**Backend:** 5 arquivos duplicados (classifier 2.py, repository 2.py, etc.)

**Impacto:** Confusão, risco de editar versão errada, aumento de bundle, dificuldade de manutenção.

---

## 4. PÁGINAS (APP) → FEATURES

**Status:** ✅ Correto

As páginas em `app/` importam de `features/` – é a camada de composição. Exemplos:
- `app/dashboard/page.tsx` → `@/features/dashboard/components/*`
- `app/mobile/budget/page.tsx` → `@/features/goals/*`
- `app/transactions/page.tsx` → `@/features/transactions/*`

---

## 5. CORE E CONFIG

**Status:** ✅ Bem utilizado

- `@/core/config/api.config` – centralizado
- `@/core/utils/api-client` – fetch com auth
- `fetchWithAuth` usado nas features (não URL hardcoded)

---

## 6. CHECKLIST DE SUSTENTABILIDADE

| Item | Status |
|------|--------|
| Backend: camadas Repository→Service→Router | ✅ |
| Backend: sem user_id hardcoded | ✅ |
| Frontend: features com components/hooks/services | ✅ |
| Frontend: API via api.config / fetchWithAuth | ✅ |
| Frontend: páginas importam de features | ✅ |
| **Frontend: sem imports cruzados entre features** | ❌ |
| **Frontend: componentes compartilhados em components/** | ❌ |
| **Sem arquivos duplicados ( 2, 3, 4)** | ❌ |
| Backend: domínios autocontidos | 🟡 Parcial |

---

## 7. PLANO DE AÇÃO - MODULARIDADE

### Fase 1 - Correções Rápidas (1-2 dias)

1. **Mover BottomNav para components**
   - Criar `components/mobile/bottom-nav.tsx` (ou renomear o existente)
   - Atualizar imports em: investimentos, transactions/mobile, dashboard/mobile
   - Remover de `features/dashboard/components/mobile/`

2. **Resolver AddGroupDialog**
   - Opção A: Mover para `components/dialogs/add-group-dialog.tsx`
   - Opção B: Manter em upload e fazer preview usar via prop/callback (inversão de dependência)
   - Opção C: Criar feature `shared-dialogs` se houver mais dialogs compartilhados

### Fase 2 - Limpeza de Duplicados (3-5 dias)

1. **Auditar arquivos " 2", " 3", etc.**
   - Para cada par: comparar com original, decidir qual manter
   - Consolidar em um único arquivo
   - Remover duplicados

2. **Prioridade:** investimentos (25 arquivos), dashboard (12), components/ui (15)

### Fase 3 - Backend (opcional, 1-2 sprints)

1. Documentar grafo de dependências aceitas
2. Extrair modelos compartilhados para `shared/models` (se fizer sentido)
3. Avaliar eventos para desacoplar upload

---

## 8. MÉTRICAS SUGERIDAS

| Métrica | Atual | Meta |
|---------|-------|------|
| Imports cruzados entre features | 2 | 0 |
| Componentes compartilhados em features | 2 | 0 |
| Arquivos duplicados ( 2, 3, 4) | 77+ | 0 |
| Domínios backend com >3 dependências | 4 | Reduzir |
| Cobertura de index (barrel) nas features | ~80% | 100% |

---

**Documento:** Análise de Modularidade  
**Última atualização:** 14/02/2026  
**Próxima revisão:** Após Fase 1 do plano de ação
