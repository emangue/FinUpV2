# Mapeamento de Código e APIs Mortas — app_dev

**Data:** 2026-03-02
**Escopo:** `app_dev/backend` + `app_dev/frontend/src`
**Método:** Varredura de arquivos + cruzamento de imports/rotas + leitura de `main.py`

---

## Resumo executivo

| Categoria | Quantidade | Pode deletar? |
|---|---|---|
| Arquivos backend duplicados (`* 2.py`, `* 3.py`) | **87** | ✅ Sim |
| Arquivos frontend duplicados (`* 2.tsx`, `* 6.tsx`…) | **9** | ✅ Sim |
| Database backups (pasta raiz + nomeados) | **~20** | ✅ Sim (manter só 1) |
| Python backups (`.backup_*`) | **3** | ✅ Sim |
| Componentes com sufixo `-old` | **2** | ✅ Sim |
| Domínio backend sem router/uso | **1** (`patterns`) | ✅ Sim |
| Funções frontend stub | **2** | ⚠️ Revisar |
| **TOTAL** | **~124 artefatos** | |

---

## 1. Arquivos Duplicados — Backend (87 arquivos)

Padrão: arquivos nomeados `arquivo 2.py` / `arquivo 3.py` são versões antigas criadas manualmente em vez de usar git. Nenhum é importado em `main.py` ou referenciado em qualquer outro módulo ativo.

**Certeza: ALTA** — Python não importa arquivos com espaço no nome por convenção; confirmado que `main.py` só importa os arquivos sem número.

### 1.1 `app/core/`
```
app/core/config 2.py
app/core/config 3.py
```

### 1.2 `app/shared/`
```
app/shared/__init__ 2.py
app/shared/dependencies 2.py
```

### 1.3 `domains/budget/`
```
domains/budget/models 2.py
domains/budget/models 3.py
domains/budget/router 2.py
domains/budget/router 3.py
domains/budget/schemas 2.py
domains/budget/service 2.py
domains/budget/service 3.py
```

### 1.4 `domains/classification/`
```
domains/classification/router 2.py
domains/classification/schemas 2.py
```

### 1.5 `domains/compatibility/`
```
domains/compatibility/router 2.py
```

### 1.6 `domains/dashboard/`
```
domains/dashboard/repository 2.py
domains/dashboard/repository 3.py
domains/dashboard/router 2.py
domains/dashboard/router 3.py
domains/dashboard/schemas 2.py
domains/dashboard/schemas 3.py
domains/dashboard/service 2.py
domains/dashboard/service 3.py
```

### 1.7 `domains/grupos/`
```
domains/grupos/models 2.py
domains/grupos/schemas 2.py
domains/grupos/schemas 3.py
domains/grupos/service 2.py
```

### 1.8 `domains/investimentos/`
```
domains/investimentos/models 2.py
domains/investimentos/repository 2.py
domains/investimentos/repository 3.py
domains/investimentos/router 2.py
domains/investimentos/router 3.py
domains/investimentos/schemas 2.py
domains/investimentos/schemas 3.py
domains/investimentos/service 2.py
```

### 1.9 `domains/marcacoes/`
```
domains/marcacoes/__init__ 2.py
domains/marcacoes/repository 2.py
domains/marcacoes/router 2.py
domains/marcacoes/schemas 2.py
domains/marcacoes/service 2.py
```

### 1.10 `domains/screen_visibility/`
```
domains/screen_visibility/router 2.py
```

### 1.11 `domains/transactions/`
```
domains/transactions/repository 2.py
domains/transactions/router 2.py
domains/transactions/router 3.py
domains/transactions/schemas 2.py
domains/transactions/schemas 3.py
domains/transactions/service 2.py
domains/transactions/service 3.py
```

### 1.12 `domains/upload/`
```
domains/upload/__init__ 2.py
domains/upload/__init__ 3.py
domains/upload/history_schemas 2.py
domains/upload/repository 2.py
domains/upload/repository 3.py
domains/upload/router 2.py
domains/upload/service 2.py
domains/upload/service 3.py
```

### 1.13 `domains/upload/processors/`
```
domains/upload/processors/__init__ 2.py
domains/upload/processors/classifier 2.py
domains/upload/processors/raw/__init__ 2.py
domains/upload/processors/raw/base 2.py
domains/upload/processors/raw/btg_extrato 2.py
domains/upload/processors/raw/btg_extrato 3.py
domains/upload/processors/raw/csv/__init__ 2.py
domains/upload/processors/raw/csv/itau_fatura 2.py
domains/upload/processors/raw/excel/__init__ 2.py
domains/upload/processors/raw/excel/btg_extrato 2.py
domains/upload/processors/raw/excel/itau_extrato 2.py
domains/upload/processors/raw/excel/mercadopago_extrato 2.py
domains/upload/processors/raw/itau_extrato 2.py
domains/upload/processors/raw/itau_extrato 3.py
domains/upload/processors/raw/itau_fatura 2.py
domains/upload/processors/raw/pdf/__init__ 2.py
domains/upload/processors/raw/pdf/itau_extrato_pdf 2.py
domains/upload/processors/raw/pdf/itau_fatura_pdf 2.py
domains/upload/processors/raw/pdf/mercadopago_extrato_pdf 2.py
domains/upload/processors/raw/registry 2.py
```

### 1.14 `domains/users/`
```
domains/users/__init__ 2.py
domains/users/router 2.py
```

---

## 2. Arquivos Duplicados — Frontend (9 arquivos)

Mesmo padrão de versionamento manual com espaço+número. Next.js só reconhece `page.tsx` para roteamento; arquivos com espaço no nome não são carregados.

**Certeza: ALTA**

```
src/app/mobile/budget/page 6.tsx
src/app/mobile/preview/[sessionId]/page 2.tsx
src/app/upload/preview/[sessionId]/page 2.tsx
src/app/upload/preview/[sessionId]/page 3.tsx

src/features/investimentos/components/__tests__/export-investimentos.test 2.tsx
src/features/investimentos/components/__tests__/portfolio-overview.test 2.tsx
src/features/investimentos/components/mobile/dashboard-investimentos-mobile 2.tsx
src/features/investimentos/components/visao-por-corretora 6.tsx
src/features/investimentos/hooks/__tests__/use-investimentos.test 2.tsx
```

---

## 3. Componentes Frontend com sufixo `-old` (2 arquivos)

Confirmado via `grep`: nenhum dos dois é importado em lugar algum do codebase.

**Certeza: ALTÍSSIMA**

```
src/features/budget/components/budget-media-drilldown-modal-old.tsx
src/features/dashboard/components/credit-card-expenses-old.tsx
```

---

## 4. Database Backups (~20 arquivos)

### 4.1 Na pasta raiz `database/` (misturado com o DB ativo)
```
database/financas_dev 2.db
database/financas_dev 3.db
database/financas_dev.db 2.backup_pre_consolidation_20260213_191101
database/financas_dev.db.backup_antes_fase3_20260114_133129
database/financas_dev.db.backup_antes_fase3_20260114_133157
database/financas_dev.db.backup_antes_fase3_20260114_133209
database/financas_dev.db.backup_fase4_20260114_134155
database/financas_dev.db.backup_fase4_20260114_134342
database/financas_dev.db.backup_fase4_20260114_134407
database/financas_dev.db.backup_fase4_20260114_134637
database/financas_dev.db.backup_pre_cleanup_20260213_194451
database/financas_dev.db.backup_pre_consolidation_20260213_191101
database/financas_dev_backup_20260110_212636.db
database/financas_dev_backup_20260110_212756.db
database/financas_dev_backup_20260119_135417.db → 135747.db  (6 arquivos)
database/financas_dev_empty_backup.db
```

### 4.2 Na pasta `database/backups/`
```
backups/financas_dev_backup_20260110_132204.db
backups/financas_dev_backup_20260110_132236.db
backups/financas_dev_backup_20260110_132518.db
backups/financas_dev_backup_20260110_133001.db
backups/financas_dev_backup_v3_20260110_133852.db
```

**Recomendação:** manter apenas o backup mais recente (`backup_pre_consolidation_20260213`) como referência. Os de janeiro/2026 são muito antigos para terem valor de rollback real.

---

## 5. Python Backups (3 arquivos)

```
domains/budget/service.py 2.backup_consolidation
domains/budget/service.py.backup_consolidation
domains/upload/processors/generic_rules_classifier.py.backup_fase5_20260114_135241
```

**Certeza: ALTA** — Backups manuais de refatorações antigas já concluídas.

---

## 6. Domínio Backend Incompleto — `patterns`

**Localização:** `app/domains/patterns/`
**Conteúdo:** apenas `__init__.py` e `models.py` (define modelo `BasePadroes`)
**Status:** sem `router.py`, sem `service.py`, sem `repository.py`
**Registrado em `main.py`:** ❌ NÃO
**Chamado no frontend:** ❌ NÃO

**Contexto:** Parece ser um domínio iniciado para padrões de classificação automática que foi abandonado. O modelo existe mas nunca foi conectado à API.

**Certeza: MÉDIA** — Pode ser infraestrutura planejada. Verificar se há intenção de continuar antes de deletar.

---

## 7. Funções Frontend Stub (código não operacional)

**Arquivo:** `src/features/goals/services/goals-api.ts`

```typescript
// Linha ~321
export async function fetchLinkedBudgets(goalId: number) {
  return {
    budgets: [],
    message: 'Funcionalidade em desenvolvimento'
  }
}

// Linha ~332
export async function toggleBudgetLink(goalId: number, budgetId: number, vincular: boolean) {
  return {
    success: true,
    message: 'Funcionalidade em desenvolvimento'
  }
}
```

**Status:** Funções que retornam dados fixos sem fazer chamada à API. Nunca chegaram a ser implementadas.
**Certeza: MÉDIA** — Verificar se são chamadas em algum componente antes de remover. Se chamadas, o comportamento atual é silenciosamente incorreto.

---

## 8. O que NÃO é código morto (falsos positivos)

Os domínios a seguir **parecem** pouco usados mas têm chamadas reais no frontend:

| Domínio | Onde é usado no frontend |
|---|---|
| `classification` | `settings/categorias-genericas/page.tsx` (CRUD completo de regras) |
| `compatibility` | `settings/bancos/page.tsx` + `mobile/cards/page.tsx` |
| `screen_visibility` | `api.config.ts` (constantes) + `settings/screens/page.tsx` |
| `onboarding` | `OnboardingGuard`, `NudgeBanners`, `DemoModeBanner`, `OnboardingChecklist` |
| `exclusoes` | `settings/exclusoes/page.tsx` + `mobile/exclusions/page.tsx` |

---

## 9. Plano de limpeza por prioridade

### Prioridade 1 — Deletar sem risco (zero impacto em produção)
- **87 arquivos** backend `* 2.py` / `* 3.py` → nunca importados, Python ignora nomes com espaço
- **9 arquivos** frontend `* 2.tsx` etc → Next.js nunca roteia para eles
- **2 componentes** `-old.tsx` → confirmado sem imports

**Comando de referência para backend:**
```bash
find app_dev/backend -name "* 2.*" -o -name "* 3.*" | grep -v __pycache__ | sort
# Revisar lista, depois:
find app_dev/backend -name "* 2.*" -delete
find app_dev/backend -name "* 3.*" -delete
```

**Comando de referência para frontend:**
```bash
find app_dev/frontend/src -name "* 2.*" -o -name "* 3.*" -o -name "* 4.*" -o -name "* 5.*" -o -name "* 6.*" -delete
find app_dev/frontend/src -name "*-old.*" -delete
```

### Prioridade 2 — Deletar após revisão rápida
- **3 Python backups** `.backup_*`
- **~18 DB backups** antigos (manter apenas o de 13/02/2026)

### Prioridade 3 — Decisão necessária
- **`domains/patterns/`** → Feature futura ou abandonada? Decidir antes de deletar.
- **Funções stub** `goals-api.ts` → Verificar se são chamadas; se sim, exibem comportamento silenciosamente errado.

---

## 10. Impacto esperado da limpeza

| Antes | Depois |
|---|---|
| ~87 + 9 = 96 arquivos duplicados causando confusão na IDE | 0 duplicatas |
| Autocompletar sugere `router 2.py` como opção | Apenas o arquivo correto aparece |
| DB com 20+ arquivos .backup espalhados | Pasta limpa, 1 backup por convenção |
| Domínio `patterns` visível no explorer sem função | Removido ou documentado como backlog |
| ~124 artefatos mortos no total | Projeto com apenas código operacional |
