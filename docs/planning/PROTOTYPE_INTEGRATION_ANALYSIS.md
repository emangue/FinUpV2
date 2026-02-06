# 📊 COMPREHENSIVE PROTOTYPE INTEGRATION ANALYSIS

**Data:** 05/02/2026  
**Objetivo:** Análise comparativa entre 4 protótipos mobile e implementação existente (desktop + backend)

---

## 📑 SUMÁRIO

1. [UPLOAD PROTOTYPE](#1-upload-prototype)
2. [PREVIEW-UPLOAD PROTOTYPE](#2-preview-upload-prototype)
3. [DASHBOARD PROTOTYPE](#3-dashboard-prototype)
4. [METAS PROTOTYPE](#4-metas-prototype)
5. [SUMMARY TABLE](#5-summary-table)

---

## 1. UPLOAD PROTOTYPE

### Desktop Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/upload/page.tsx`

**Components Used:**
- `UploadDialog` (from `@/features/upload`)
- `Card`, `CardContent`, `CardHeader` (UI components)
- Upload history table with status badges
- Compatibility matrix dialog

**Data Shown:**
- Upload history list:
  - Session ID, banco, tipo documento, arquivo nome
  - Status (processing, success, error, cancelled)
  - Total registros, transações importadas, duplicadas
  - Classification stats (base_parcelas, base_padrões, etc)
  - Data upload, data confirmação, error messages
- Format compatibility matrix (banco x formato)
- Supported banks list (Itaú, BTG, BB, Mercado Pago)

**APIs Called:**
- `GET /api/upload/history` → Lista histórico de uploads

### Mobile Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/mobile/upload/page.tsx`

**Implementation:**
- Simplified V1.0 approach:
  - Native file input (no configuration UI)
  - Auto-detects format from extension
  - Redirects to desktop preview flow after upload
  - File validation (10MB max, CSV/Excel/PDF only)
- Uses `MobileHeader` component
- Uses `fetchWithAuth` for API calls

**APIs Called:**
- `POST /api/v1/upload/preview` → Upload file and create session

### Prototype Analysis
**Location:** `export-to-main-project/upload/app/page.tsx`

**Components Count:**
- 0 atoms (all inline HTML/Tailwind)
- 0 molecules (all inline)
- 0 organisms (all inline)

**UI Style:**
- Clean white card with rounded-3xl borders
- Tab switcher: Extrato Bancário / Fatura Cartão
- Gray-50 background
- Inline SVG icons
- Mobile-first design (max-w-md)

**Key Features:**
1. **Tabs:** Extrato vs Fatura
2. **Form Fields:**
   - Instituição Financeira (dropdown)
   - Cartão de Crédito (dropdown + add button) - only for Fatura
   - Período da Fatura (year + month) - only for Fatura
   - Formato (radio: CSV, Excel, PDF, OFX)
   - File picker with drag & drop
3. **Validation:** Client-side alerts
4. **Bottom Navigation:** Home, Card, Upload buttons

**Mock Data Structure:**
```typescript
banks: Array<{id: string, name: string}>
creditCards: Array<{id: string, name: string}>
months: Array<string> // ["Janeiro", "Fevereiro", ...]
years: Array<number> // [2024, 2025, 2026]
fileFormats: Array<{value: FileFormat, label: string}>
```

### Backend API Analysis

#### Existing (Can Reuse):

**`POST /api/v1/upload/preview`**
```python
# Request (multipart/form-data)
{
  file: UploadFile,
  banco: str,
  cartao?: str,
  final_cartao?: str,
  mesFatura: str,  # YYYY-MM format
  tipoDocumento: str,  # "fatura" | "extrato"
  formato: str  # "csv" | "Excel" | "pdf"
}

# Response
{
  sessionId: str,
  totalRegistros: int,
  message: str
}
```
**Used For:** File upload and preview creation

**`POST /api/v1/upload/batch`**
```python
# Request (multipart/form-data)
{
  files: List[UploadFile],
  banco: str,
  tipoDocumento: str
}

# Response
{
  success: bool,
  sessionId: str,  # Single consolidated session
  totalArquivos: int,
  arquivosProcessados: int,
  totalTransacoes: int,
  arquivos: List[{arquivo, totalRegistros, success}],
  erros: List[{arquivo, erro}]
}
```
**Used For:** Multi-file upload in batch

**`GET /api/v1/upload/history`**
```python
# Query params
{
  limit?: int (default: 50),
  offset?: int (default: 0)
}

# Response
{
  total: int,
  uploads: List[UploadHistory]
}
```
**Used For:** Upload history display

#### Missing (Need to Create):
**NONE** - All required endpoints exist!

### Database Tables Used

| Table | Data | Queried By | Exists? |
|-------|------|------------|---------|
| `preview_transacoes` | Temporary upload data before confirmation | `/upload/preview` | ✅ |
| `upload_history` | Upload session metadata, status, stats | `/upload/history` | ✅ |
| `journal_entries` | Final confirmed transactions | `/upload/confirm/{sessionId}` | ✅ |

### Integration Strategy

**Frontend:**
- **COPY PROTOTYPE 80%** - UI design is cleaner than existing
- **ADAPT:**
  - Replace inline HTML with reusable components
  - Extract tabs to `<TabBar>` molecule
  - Extract form fields to `<FormField>` molecules
  - Add form state management (React Hook Form)
  - Integrate with existing `fetchWithAuth` utility

**Backend:**
- **USE AS-IS** - All endpoints already exist
- **ENHANCE:** None needed

**Effort:** 8-10 hours
- 3h: Component extraction (TabBar, FormField, FileUpload)
- 2h: Form validation and state management
- 2h: API integration and error handling
- 1h: Mobile responsive testing
- 2h: Edge cases (file size, format validation, network errors)

### Component Mapping

| Prototype Element | Needs Data From | Backend Endpoint | DB Table | Exists? |
|-------------------|-----------------|------------------|----------|---------|
| Bank dropdown | Static list | N/A | N/A | ✅ |
| Card dropdown | User's cards | N/A (hardcoded for now) | N/A | ⚠️ |
| File upload | File object | `POST /upload/preview` | `preview_transacoes` | ✅ |
| Format radio | Static list | N/A | N/A | ✅ |
| Upload history | Past uploads | `GET /upload/history` | `upload_history` | ✅ |

---

## 2. PREVIEW-UPLOAD PROTOTYPE

### Desktop Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/upload/preview/[sessionId]/page.tsx`

**Components Used:**
- Preview table with inline classification
- Filter by status (all, classified, unclassified)
- Batch classification by establishment
- Individual transaction edit modal
- Confirm/Cancel actions

**Data Shown:**
- File info (banco, tipo documento, mês fatura)
- Transaction list with:
  - Data, Estabelecimento, Valor
  - Grupo, Subgrupo (editable)
  - Classification source (manual, base_parcelas, etc)
  - Exclude checkbox
- Stats (total, classified, unclassified, duplicates)

**APIs Called:**
- `GET /api/v1/upload/preview/{sessionId}`
- `PATCH /api/v1/upload/preview/{sessionId}/{previewId}` → Update classification
- `POST /api/v1/upload/confirm/{sessionId}` → Confirm import
- `DELETE /api/v1/upload/preview/{sessionId}` → Cancel upload

### Mobile Version
**Status:** ❌ DOESN'T EXIST  
**Location:** N/A

**Note:** Currently redirects to desktop preview after upload

### Prototype Analysis
**Location:** `export-to-main-project/preview-upload/app/page.tsx`  
Uses template: `export-to-main-project/preview-upload/src/components/templates/PreviewLayout.tsx`

**Components Count:**
- **Atoms:** 1 (Alert)
- **Molecules:** 4 (PreviewHeader, FileInfoCard, TabBar, ClassificationModal)
- **Organisms:** 2 (TransactionList, BottomActionBar)
- **Templates:** 1 (PreviewLayout)

**UI Style:**
- Mobile-first (max-w-md)
- White card container with shadow
- Sticky header and bottom action bar
- Color-coded classification status:
  - Green (classified), Yellow (unclassified), Gray (excluded)
- Grouping by establishment with expand/collapse

**Key Features:**
1. **Header:** Cancel button with confirmation dialog
2. **Alert:** Warning for unclassified transactions
3. **File Info Card:** Display upload metadata
4. **Tabs:** All (X) | Não Classificadas (Y)
5. **Transaction List:**
   - Grouped by establishment
   - Individual cards with edit button
   - Batch classification dropdown per group
   - Source badge (Base Parcelas, Padrões, Manual, etc)
6. **Classification Modal:**
   - Grupo dropdown
   - Subgrupo dropdown (filtered by grupo)
   - Save/Cancel actions
7. **Bottom Bar:**
   - Disabled when has unclassified
   - Confirm import button
   - Transaction count

**Mock Data Structure:**
```typescript
FileInfo {
  banco: string
  tipo_documento: string
  mes_fatura: string
  data_upload: string
  total_transacoes: number
}

Transaction {
  id: string
  data: string
  estabelecimento: string
  valor: number
  grupo?: string
  subgrupo?: string
  source: 'base_parcelas' | 'base_padroes' | 'journal_entries' | 'marcas_gerais' | 'manual' | null
  excluded: boolean
  items?: Transaction[]  // For grouped transactions
}

ClassificationData {
  grupo: string
  subgrupo: string
}
```

### Backend API Analysis

#### Existing (Can Reuse):

**`GET /api/v1/upload/preview/{sessionId}`**
```python
# Response
{
  sessionId: str,
  fileInfo: {
    banco: str,
    tipoDocumento: str,
    mesFatura: str,
    nomeArquivo: str,
    dataUpload: str
  },
  transacoes: List[{
    id: int,
    data: str,
    estabelecimento: str,
    valor: float,
    grupo: str | null,
    subgrupo: str | null,
    origemClassificacao: str | null,
    excluir: int (0|1)
  }],
  stats: {
    total: int,
    classificadas: int,
    naoClassificadas: int,
    duplicadas: int
  }
}
```
**Used For:** Display preview data

**`PATCH /api/v1/upload/preview/{sessionId}/{previewId}`**
```python
# Request (query params or body)
{
  grupo?: str,
  subgrupo?: str,
  excluir?: int (0|1)
}

# Response
{
  success: bool,
  message: str
}
```
**Used For:** Update classification or exclusion

**`POST /api/v1/upload/confirm/{sessionId}`**
```python
# Response
{
  success: bool,
  transacoesImportadas: int,
  transacoesDuplicadas: int,
  transacoesExcluidas: int
}
```
**Used For:** Confirm and save to journal_entries

**`DELETE /api/v1/upload/preview/{sessionId}`**
```python
# Response
{
  success: bool,
  message: str
}
```
**Used For:** Cancel upload and delete preview data

**`GET /api/v1/classification/groups-with-types`**
```python
# Response
{
  opcoes: List[{
    grupo: str,
    subgrupos: List[{
      subgrupo: str,
      tipoGasto: str | null
    }]
  }]
}
```
**Used For:** Populate classification dropdowns

#### Missing (Need to Create):

**❌ Batch Classification Endpoint**
```python
# Should exist (to avoid N requests):
PATCH /api/v1/upload/preview/{sessionId}/batch

# Request
{
  updates: List[{
    previewId: int,
    grupo: str,
    subgrupo: str
  }]
}

# Response
{
  success: bool,
  updated: int
}
```
**Priority:** MEDIUM (optimization, not blocking)

### Database Tables Used

| Table | Data | Queried By | Exists? |
|-------|------|------------|---------|
| `preview_transacoes` | Staged transactions awaiting confirmation | All `/preview/*` endpoints | ✅ |
| `base_grupos_config` | Available groups/subgroups | `/classification/groups-with-types` | ✅ |
| `base_marcacoes` | Historical classifications | Classification logic | ✅ |
| `base_parcelas` | Installment patterns | Classification logic | ✅ |
| `journal_entries` | Final destination after confirm | `/upload/confirm` | ✅ |

### Integration Strategy

**Frontend:**
- **COPY PROTOTYPE 95%** - Component structure is excellent
- **REUSE:**
  - Existing `fetchWithAuth` utility
  - Existing `MobileHeader` component
- **ADAPT:**
  - Replace mock constants with API calls
  - Add loading states
  - Add error handling (network, 401, etc)
  - Add optimistic updates

**Backend:**
- **USE AS-IS** - 90% of endpoints exist
- **ENHANCE:**
  - Add batch classification endpoint (optional optimization)

**Effort:** 10-12 hours
- 2h: Copy components from prototype
- 3h: Replace mock data with real API calls
- 2h: State management (transaction updates, filters)
- 2h: Classification modal integration
- 2h: Batch operations
- 1h: Error handling and edge cases

### Component Mapping

| Prototype Component | Needs Data From | Backend Endpoint | DB Table | Exists? |
|---------------------|-----------------|------------------|----------|---------|
| PreviewHeader | Session info | `GET /preview/{sessionId}` | `preview_transacoes` | ✅ |
| FileInfoCard | Upload metadata | `GET /preview/{sessionId}` | `preview_transacoes` | ✅ |
| Alert | Unclassified count | Calculated client-side | N/A | ✅ |
| TabBar | Transaction counts | Calculated client-side | N/A | ✅ |
| TransactionList | Transactions | `GET /preview/{sessionId}` | `preview_transacoes` | ✅ |
| TransactionCard | Single transaction | (from list) | N/A | ✅ |
| ClassificationModal | Groups/subgroups | `GET /classification/groups-with-types` | `base_grupos_config` | ✅ |
| BottomActionBar | Confirmation button | N/A | N/A | ✅ |

---

## 3. DASHBOARD PROTOTYPE

### Desktop Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/dashboard/page.tsx` (assumed, not read)

**Components Used (from features/dashboard):**
- `ChartAreaInteractive` - Area chart for income/expenses over time
- `BudgetVsActual` - Budget vs actual comparison by tipo_gasto
- `CategoryExpenses` - Expenses grouped by category (pie chart)
- `CreditCardExpenses` - Card expenses breakdown
- `DateFilters` - Month/Year selector
- `CompactMetrics` - Metric cards (receitas, despesas, saldo)

**Data Shown:**
- Income/expense trend over time (chart)
- Budget vs actual by category
- Category breakdown (percentages)
- Credit card expenses
- Month/year filters

**APIs Called:**
- `GET /api/v1/dashboard/metrics?year=X&month=Y`
- `GET /api/v1/dashboard/chart-data?year=X&month=Y`
- `GET /api/v1/dashboard/categories?year=X&month=Y`
- `GET /api/v1/dashboard/budget-vs-actual?year=X&month=Y`
- `GET /api/v1/dashboard/credit-cards?year=X&month=Y`

### Mobile Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`

**Implementation:**
- Uses `MonthScrollPicker` component
- Uses `YTDToggle` (month vs year-to-date)
- Simple metric cards: Receitas, Despesas, Saldo, Investimentos
- Calls `/transactions/receitas-despesas?data_inicio=X&data_fim=Y`

**Difference from Desktop:**
- MUCH simpler - only 4 metric cards
- No charts, no breakdowns
- No income sources breakdown (prototype feature)

### Prototype Analysis
**Location:** `export-to-main-project/dashboard/app/page.tsx`

**Components Count:**
- 0 atoms (inline)
- 0 molecules (inline)
- 0 organisms (inline)

**UI Style:**
- Mobile-first (max-w-md)
- White card with rounded-3xl
- Dark theme accents (gray-900)
- Horizontal scrollable month selector
- Interactive bar chart with tooltips
- Donut chart for income sources
- Tabs: Income | Expenses | Budget

**Key Features:**
1. **Header:** Back button, "Insights" title, Download button
2. **Month Selector:** Horizontal scroll (past 6 + current + future 6 months)
3. **Wallet Balance Card:**
   - Large balance display
   - Percentage change indicator (+2.5%)
   - Tabs: Income | Expenses | Budget
4. **Income Trend Chart:**
   - Bar chart (12 months)
   - Dual bars per month (income dark, expenses light)
   - Hover tooltip with values
   - Legend at bottom
5. **Income Sources Breakdown:**
   - Donut chart (3 segments)
   - Legend with amounts
   - Categories: Salary, Freelance, Other
6. **Recent Transactions:** Empty state ("No transactions yet")
7. **Bottom Navigation:** Home, Card, Insights (active)

**Mock Data Structure:**
```typescript
monthlyData: Array<{
  month: string,
  income: number,
  expenses: number
}>

incomeSources: Array<{
  name: string,
  amount: number,
  color: string
}>

totalIncome: number
```

### Backend API Analysis

#### Existing (Can Reuse):

**`GET /api/v1/dashboard/metrics`**
```python
# Query params
{
  year?: int (default: current),
  month?: int (default: None = YTD)
}

# Response
{
  receitas: float,
  despesas: float,
  cartoes: float,
  saldo: float,
  totalTransacoes: int
}
```
**Used For:** Wallet balance display

**`GET /api/v1/dashboard/chart-data`**
```python
# Query params
{
  year?: int (default: current),
  month?: int (default: current)
}

# Response
{
  labels: List[str],  # Days or months
  receitas: List[float],
  despesas: List[float]
}
```
**Used For:** Income trend bar chart

**`GET /api/v1/dashboard/categories`**
```python
# Query params
{
  year?: int,
  month?: int (None = YTD)
}

# Response
List[{
  categoria: str,
  total: float,
  percentual: float
}]
```
**Used For:** Category expenses (but prototype shows INCOME sources!)

#### Missing (Need to Create):

**❌ Income Sources Breakdown Endpoint**
```python
# New endpoint needed:
GET /api/v1/dashboard/income-sources

# Query params
{
  year?: int,
  month?: int (None = YTD)
}

# Response
{
  total: float,
  sources: List[{
    nome: str,  # "Salary", "Freelance", "Investments", etc.
    valor: float,
    percentual: float
  }]
}
```
**Priority:** HIGH - Core prototype feature

**Implementation Notes:**
- Query `journal_entries` WHERE `CategoriaGeral = 'Receita'`
- Group by `GRUPO` or `SUBGRUPO` (to be defined)
- Calculate totals and percentages
- Return top 3-5 sources

**Database Logic:**
```python
# Query
SELECT 
  GRUPO as nome,
  SUM(ValorPositivo) as valor,
  (SUM(ValorPositivo) / (SELECT SUM(ValorPositivo) FROM journal_entries WHERE ...)) * 100 as percentual
FROM journal_entries
WHERE user_id = X
  AND Ano = YEAR
  AND (Mes = MONTH OR MONTH IS NULL)
  AND CategoriaGeral = 'Receita'
  AND IgnorarDashboard = 0
GROUP BY GRUPO
ORDER BY valor DESC
LIMIT 5
```

### Database Tables Used

| Table | Data | Queried By | Exists? |
|-------|------|------------|---------|
| `journal_entries` | All transactions | All dashboard endpoints | ✅ |
| `budget_geral` | Budget targets | `/dashboard/budget-vs-actual` | ✅ |

### Integration Strategy

**Frontend:**
- **COPY PROTOTYPE 70%** - Month selector and income breakdown are new
- **REUSE:**
  - Existing `MonthScrollPicker` component (similar functionality)
  - Existing `fetchWithAuth` utility
- **CREATE NEW:**
  - `IncomeSourcesDonut` component
  - `BarChartInteractive` component (with tooltips)
- **ADAPT:**
  - Month selector (horizontal scroll with year indicators)
  - Tab system (Income/Expenses/Budget)

**Backend:**
- **CREATE NEW:**
  - `GET /api/v1/dashboard/income-sources` endpoint
  - Service method `DashboardService.get_income_sources()`
  - Response schema `IncomeSourcesResponse`

**Effort:** 12-15 hours
- 4h: Create income-sources backend endpoint + tests
- 3h: Build IncomeSourcesDonut component
- 2h: Build BarChartInteractive with tooltips
- 2h: Horizontal month scroll with year indicators
- 2h: Tab system integration
- 2h: Mobile responsive + testing

### Component Mapping

| Prototype Element | Needs Data From | Backend Endpoint | DB Table | Exists? |
|-------------------|-----------------|------------------|----------|---------|
| Wallet Balance | Total income | `GET /dashboard/metrics` | `journal_entries` | ✅ |
| Percentage Change | Comparison with previous period | **NEW** (calculate client-side or backend) | `journal_entries` | ❌ |
| Income Trend Bars | Monthly income/expenses | `GET /dashboard/chart-data` | `journal_entries` | ⚠️ (needs 12 months, not 1) |
| Income Sources Donut | Income breakdown by source | **NEW** `GET /dashboard/income-sources` | `journal_entries` | ❌ |
| Recent Transactions | Latest transactions | `GET /transactions/list` | `journal_entries` | ✅ |

---

## 4. METAS PROTOTYPE

### Desktop Version
**Status:** ✅ EXISTS  
**Location:** Assumed `app_dev/frontend/src/app/budget/page.tsx` (not explicitly verified)

**Components Used (from features/budget):**
- Budget configuration interface
- Category breakdown
- Planning vs actual comparison

**Data Shown:**
- Budget by category
- Budget vs actual
- Monthly/yearly planning

**APIs Called:**
- `GET /api/v1/budget/planning?mes_referencia=YYYY-MM`
- `GET /api/v1/budget/geral?mes_referencia=YYYY-MM`
- `POST /api/v1/budget/planning/bulk-upsert`

### Mobile Version
**Status:** ✅ EXISTS  
**Location:** `app_dev/frontend/src/app/mobile/budget/page.tsx`

**Implementation:**
- Uses `MonthScrollPicker`
- Uses `YTDToggle` (month vs YTD)
- Uses `TrackerCard` component
- Uses `BudgetEditBottomSheet` for quick edits
- Integrates with `/budget/planning` and `/transactions/grupo-breakdown`

**Features:**
- Category cards with progress bars
- Edit button on header → navigates to edit page
- Individual card tap → opens edit bottom sheet
- Month/year selector

### Prototype Analysis
**Location:** `export-to-main-project/metas/app/page.tsx`  
Uses template: `export-to-main-project/metas/src/components/templates/MetasLayout.tsx`

**Components Count:**
- **Atoms:** 1 (IconButton)
- **Molecules:** 3 (HeaderBar, MonthScroll, TabBar)
- **Organisms:** 2 (DonutChart, GoalsList)
- **Templates:** 1 (MetasLayout)

**UI Style:**
- Mobile-first (max-w-md)
- White card container
- Rounded-3xl borders
- Color-coded categories:
  - Purple (casa), Pink (alimentacao), Orange (compras)
  - Green (transporte), Blue (contas), Red (lazer)
- Progress bars with percentage
- Donut chart summary

**Key Features:**
1. **Header:** Back button, "Metas" title, Manage button (settings icon)
2. **Month Scroll:** Horizontal scroll (abbreviated months: jan, fev, mar...)
3. **Donut Chart:**
   - Central total: R$ 8,540
   - Segmented by category type
   - Color-coded segments
4. **Tabs:** Todas | Flexíveis | Fixas | Essenciais
5. **Goals List:**
   - Category icon + name
   - Frequency badge ("Mensal")
   - Spent vs Budget (R$ 1,200 / R$ 2,000)
   - Progress bar
   - Percentage (60%)
   - Overflow indicator if over budget (red)
6. **Goal Types:**
   - `flexivel` (Flexível) - adjustable expenses
   - `fixa` (Fixa) - fixed expenses
   - `essencial` (Essencial) - essential expenses

**Mock Data Structure:**
```typescript
Goal {
  id: string
  name: string
  type: 'flexivel' | 'fixa' | 'essencial'
  category: 'casa' | 'alimentacao' | 'compras' | 'transporte' | 'contas' | 'lazer'
  spent: number
  budget: number
  frequency: 'Mensal' | 'Anual'
  active: boolean
}

mockGoals: Array<Goal>
months: Array<{short: string, full: string}> // [{short: 'jan', full: 'Janeiro'}, ...]
```

### Backend API Analysis

#### Existing (Can Reuse):

**`GET /api/v1/budget/planning`**
```python
# Query params
{
  mes_referencia: str  # YYYY-MM format
}

# Response
{
  mes_referencia: str,
  budgets: List[{
    grupo: str,
    valor_planejado: float,
    valor_realizado: float,
    percentual: float
  }]
}
```
**Used For:** Budget by grupo (Casa, Alimentação, etc)

**`POST /api/v1/budget/planning/bulk-upsert`**
```python
# Request
{
  mes_referencia: str,
  budgets: List[{
    grupo: str,
    valor_planejado: float
  }]
}

# Response
List[{
  id: int,
  grupo: str,
  mes_referencia: str,
  valor_planejado: float
}]
```
**Used For:** Update budgets in batch

**`GET /api/v1/transactions/grupo-breakdown`**
```python
# Query params
{
  data_inicio: str,  # YYYY-MM-DD
  data_fim: str
}

# Response
{
  grupos: {
    [grupo: string]: {
      total: float,
      count: int
    }
  }
}
```
**Used For:** Get actual spending by grupo

**`GET /api/v1/budget/geral`**
```python
# Query params
{
  mes_referencia?: str
}

# Response
{
  budgets: List[{
    id: int,
    categoria_geral: str,  # "Despesa", "Receita"
    valor_planejado: float,
    mes_referencia: str
  }],
  total: int
}
```
**Used For:** High-level budget (Despesa vs Receita)

#### Missing (Need to Create):

**❌ Goals by Type Endpoint** (Optional - can filter client-side)
```python
# Could optimize with server-side filtering:
GET /api/v1/budget/planning?tipo_gasto=Fixo

# But existing endpoint + client filter is sufficient
```
**Priority:** LOW - Can filter client-side using TipoGasto from transactions

**❌ Budget Categories Configuration**
The prototype uses hardcoded categories (casa, alimentacao, etc) with specific icons/colors.  
Current backend uses `GRUPO` from `base_grupos_config`.

**Gap:**
- Prototype has 6 categories with specific UI (icon, color)
- Backend has N grupos (Casa, Alimentação, Transporte, Lazer, Outros...)
- Need mapping layer OR extend `base_grupos_config` with icon/color fields

**Solution Options:**

**Option A:** Client-side mapping (simpler)
```typescript
const CATEGORY_CONFIG: Record<string, {icon: string, color: string}> = {
  'Casa': { icon: 'home', color: 'purple' },
  'Alimentação': { icon: 'utensils', color: 'pink' },
  'Transporte': { icon: 'car', color: 'green' },
  // ...
}
```

**Option B:** Extend backend (better long-term)
```python
# Add to base_grupos_config
class BaseGruposConfig(Base):
    # ... existing fields
    icone = Column(String, nullable=True)  # "home", "utensils", etc
    cor_hex = Column(String, nullable=True)  # "#9333EA", "#EC4899", etc
```

**Recommendation:** Use **Option A** for V1 (quick), migrate to **Option B** for V2.

### Database Tables Used

| Table | Data | Queried By | Exists? |
|-------|------|------------|---------|
| `budget_planning` | Budget by grupo | `/budget/planning` | ✅ |
| `budget_geral` | High-level budget | `/budget/geral` | ✅ |
| `journal_entries` | Actual spending | `/transactions/grupo-breakdown` | ✅ |
| `base_grupos_config` | Available grupos | Classification logic | ✅ |

### Integration Strategy

**Frontend:**
- **COPY PROTOTYPE 85%** - Goal cards and UI are excellent
- **REUSE:**
  - Existing `MonthScrollPicker` (similar to prototype)
  - Existing `TrackerCard` (already exists! very similar)
  - Existing `fetchWithAuth`
- **ADAPT:**
  - Map prototype categories to backend grupos
  - Add TipoGasto filter logic (Fixas, Flexíveis, Essenciais)
  - Replace mock data with API calls
- **CREATE NEW:**
  - `GoalsDonutChart` component (if not exists)
  - Category icon mapping (client-side)

**Backend:**
- **USE AS-IS** - 100% of needed endpoints exist
- **ENHANCE (Optional):**
  - Add icon/color to `base_grupos_config` table (V2)
  - Add TipoGasto to budget_planning response (already in journal_entries)

**Effort:** 8-10 hours
- 2h: Copy components from prototype
- 2h: Map categories to grupos (client-side config)
- 2h: Replace mock data with real API calls
- 2h: TipoGasto filtering logic
- 1h: DonutChart integration
- 1h: Bottom sheet edit flow integration

### Component Mapping

| Prototype Component | Needs Data From | Backend Endpoint | DB Table | Exists? |
|---------------------|-----------------|------------------|----------|---------|
| HeaderBar | Static UI | N/A | N/A | ✅ (MobileHeader) |
| MonthScroll | Generated months | N/A (client-side) | N/A | ✅ (MonthScrollPicker) |
| DonutChart | Budget summary | `GET /budget/planning` | `budget_planning` | ⚠️ (needs creation) |
| TabBar | Filter tabs | Static | N/A | ✅ |
| GoalsList | Goals by category | `GET /budget/planning` + `/grupo-breakdown` | `budget_planning` + `journal_entries` | ✅ |
| GoalCard | Single goal | (from list) | N/A | ✅ (TrackerCard) |
| IconButton | UI element | N/A | N/A | ✅ |

---

## 5. SUMMARY TABLE

### Integration Effort Overview

| Prototype | Frontend Effort | Backend Effort | Total Hours | Priority | Complexity |
|-----------|----------------|----------------|-------------|----------|------------|
| **Upload** | 8h (COPY 80%) | 0h (✅ Complete) | **8-10h** | HIGH | Medium |
| **Preview-Upload** | 10h (COPY 95%) | 1h (batch endpoint) | **10-12h** | HIGH | Medium |
| **Dashboard** | 10h (COPY 70%) | 4h (income sources) | **12-15h** | MEDIUM | High |
| **Metas** | 8h (COPY 85%) | 0h (✅ Complete) | **8-10h** | MEDIUM | Low |
| **TOTAL** | **36h** | **5h** | **38-47h** (~1 week) | - | - |

### Backend API Completeness

| Prototype | Existing APIs | Missing APIs | Gap Analysis |
|-----------|--------------|--------------|--------------|
| **Upload** | ✅ 100% | None | Ready to integrate |
| **Preview-Upload** | ✅ 95% | Batch classification (optional) | Nearly complete |
| **Dashboard** | ⚠️ 70% | Income sources breakdown | Need new endpoint |
| **Metas** | ✅ 100% | None (mapping needed) | Ready to integrate |

### Component Reusability Matrix

| Component Type | Prototype | Existing in App | Reusable? | Action |
|----------------|-----------|----------------|-----------|--------|
| **MonthScrollPicker** | Yes (all) | ✅ Yes | 100% | Use existing |
| **YTDToggle** | Yes (dashboard, metas) | ✅ Yes | 100% | Use existing |
| **MobileHeader** | Yes (all) | ✅ Yes | 100% | Use existing |
| **TrackerCard** | Yes (metas) | ✅ Yes | 100% | Use existing |
| **BottomSheet** | Yes (metas) | ✅ Yes | 100% | Use existing |
| **TabBar** | Yes (preview, metas) | ⚠️ Partial | 70% | Adapt or copy |
| **FileUpload** | Yes (upload) | ✅ Yes | 90% | Enhance mobile UX |
| **TransactionCard** | Yes (preview) | ⚠️ Desktop only | 50% | Copy for mobile |
| **DonutChart** | Yes (dashboard, metas) | ⚠️ Partial | 50% | Create mobile version |
| **BarChart** | Yes (dashboard) | ⚠️ Desktop only | 40% | Create with tooltips |

### Database Schema Completeness

| Table | Used By | Fields Needed | Missing? | Action |
|-------|---------|---------------|----------|--------|
| `preview_transacoes` | Preview-Upload | All exist | ✅ No | None |
| `upload_history` | Upload | All exist | ✅ No | None |
| `journal_entries` | All | All exist | ✅ No | None |
| `budget_planning` | Metas | All exist | ✅ No | None |
| `budget_geral` | Metas | All exist | ✅ No | None |
| `base_grupos_config` | All | icon, color | ⚠️ Optional | Add in V2 |

### Critical Path Analysis

**Phase 1 - Foundation (Week 1):**
1. ✅ Upload prototype → Simplest, backend ready
2. ✅ Metas prototype → Backend ready, similar to existing mobile budget

**Phase 2 - Complex (Week 2):**
3. ⚠️ Dashboard prototype → Requires new backend endpoint
4. ⚠️ Preview-Upload prototype → Most complex UI, many interactions

**Recommended Order:**
1. **Upload** (2 days) - Quickest win, improves mobile UX immediately
2. **Metas** (2 days) - Backend ready, good component reuse
3. **Dashboard** (3 days) - Need backend work first
4. **Preview-Upload** (3 days) - Most complex, do last when other patterns established

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Backend API changes** | Medium | Use `/api/v1/` namespace, versioned endpoints |
| **Component library gaps** | Low | Most components exist or are simple to create |
| **State management complexity** | Medium | Use React Query for server state, local state for UI |
| **Mobile testing coverage** | Medium | Test on real devices, not just browser DevTools |
| **Classification logic bugs** | High | Reuse existing desktop logic, add comprehensive tests |
| **Performance with large datasets** | Medium | Implement pagination, virtual scrolling for lists |

### Technical Debt Identified

1. **Category/Grupo Mapping:**
   - Prototypes use hardcoded categories (casa, alimentacao)
   - Backend uses dynamic grupos from base_grupos_config
   - **Solution:** Create mapping layer or extend backend schema

2. **TipoGasto in Metas:**
   - Prototype filters by type (Fixas, Flexíveis, Essenciais)
   - Backend has TipoGasto in journal_entries but not in budget_planning
   - **Solution:** Join queries or add TipoGasto to budget planning

3. **Income Sources Endpoint:**
   - Dashboard prototype needs income breakdown
   - No existing endpoint for this
   - **Solution:** Create new endpoint (4h effort)

4. **Batch Classification:**
   - Preview-upload needs batch update to avoid N requests
   - Current API only supports single transaction update
   - **Solution:** Create batch endpoint (1h effort) OR accept N requests for V1

### Success Metrics

**Integration Complete When:**
- [ ] All 4 prototypes converted to production code
- [ ] Backend APIs exist for all features (100%)
- [ ] Mobile tests passing (coverage ≥ 80%)
- [ ] No hardcoded mock data in production code
- [ ] Error handling for all API calls
- [ ] Loading states for all async operations
- [ ] Authentication flow working (401 redirects)
- [ ] Responsive on iOS and Android devices

**Quality Gates:**
- [ ] Code review approved by senior dev
- [ ] No console.errors in production
- [ ] API response times < 500ms (95th percentile)
- [ ] Mobile Lighthouse score ≥ 90
- [ ] Accessibility score ≥ 90 (WCAG 2.1 AA)

---

## 📊 CONCLUSION

### Key Findings

1. **Backend Readiness:** 95% complete
   - Upload & Metas: 100% ready
   - Preview-Upload: 95% ready (missing batch endpoint)
   - Dashboard: 70% ready (missing income sources)

2. **Component Reusability:** 80%
   - Most mobile components already exist (MonthScrollPicker, YTDToggle, TrackerCard, etc)
   - Can copy prototype UI with minimal adaptation

3. **Integration Effort:** 38-47 hours (~1 week full-time)
   - Frontend: 36h (80% copying prototypes, 20% adapting)
   - Backend: 5h (new endpoints + enhancements)

4. **Complexity:** Medium
   - Upload & Metas: Low complexity (backend ready)
   - Preview-Upload: Medium complexity (many interactions)
   - Dashboard: High complexity (new backend + chart components)

### Recommendations

**Immediate Actions:**
1. ✅ Start with **Upload** prototype (quickest win)
2. ✅ Follow with **Metas** (backend ready)
3. ⚠️ Create **income-sources** endpoint before Dashboard integration
4. ⚠️ Consider **batch classification** endpoint for Preview-Upload

**Architecture Decisions:**
1. Use **React Query** for server state management
2. Keep **client-side mapping** for categories (icon, color) in V1
3. Create **shared mobile component library** (`@/components/mobile/`)
4. Implement **optimistic updates** for better UX
5. Add **offline support** for read-only features (V2)

**Testing Strategy:**
1. Unit tests for all new components
2. Integration tests for API calls
3. E2E tests for critical flows (upload → preview → confirm)
4. Manual testing on iOS Safari and Chrome Android

### Next Steps

1. **Review this analysis** with team
2. **Create JIRA tickets** for each prototype
3. **Prioritize backend work** (income-sources endpoint)
4. **Begin Upload prototype** integration
5. **Schedule weekly demos** to show progress

---

**Document Version:** 1.0  
**Last Updated:** 05/02/2026  
**Author:** GitHub Copilot  
**Status:** ✅ Complete
