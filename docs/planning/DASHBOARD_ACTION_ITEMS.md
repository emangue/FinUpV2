# 🎯 Dashboard Integration - Action Items

**Created:** 2026-02-05  
**Status:** Ready for Implementation  
**Owner:** Development Team

---

## 🔍 Research Completed

✅ Desktop dashboard fully analyzed  
✅ Mobile dashboard (main app) inventoried  
✅ Prototype features documented  
✅ Gap analysis completed  
✅ Integration strategy defined

**Key Finding:** Main app already has 70% complete mobile dashboard at `/dashboard/mobile`. Best strategy is to enhance it, not rebuild from prototype.

---

## 📋 Priority 1: Essential Mobile Features (This Sprint)

### 1.1 CategoryExpensesMobile Component

**File:** `src/features/dashboard/components/mobile/category-expenses-mobile.tsx`

**Requirements:**
- Collapsible card (collapsed by default)
- Show top 5 categories when collapsed
- "Ver mais" button to expand all
- Each category shows:
  - Icon/emoji
  - Category name
  - Total amount
  - Percentage bar
  - Percentage value
- Color coding by amount
- Touch-friendly tap targets

**Data Source:** Existing API `/dashboard/categories`

**Estimated Effort:** 4 hours

**Acceptance Criteria:**
- [ ] Component created in mobile folder
- [ ] Uses existing API endpoint
- [ ] Responsive to screen size
- [ ] Animations smooth (expand/collapse)
- [ ] Tested on iOS and Android
- [ ] Matches design system colors

---

### 1.2 CreditCardExpensesMobile Component

**File:** `src/features/dashboard/components/mobile/credit-card-mobile.tsx`

**Requirements:**
- Collapsible card (collapsed by default)
- Show top 3 cards when collapsed
- "Ver detalhes" button to expand
- Each card shows:
  - Card icon (visa/master/etc)
  - Card name/last 4 digits
  - Total spent
  - Percentage of total
  - Progress bar
  - Number of transactions
- Tap card to see transactions (future)

**Data Source:** Existing API `/dashboard/credit-cards`

**Estimated Effort:** 4 hours

**Acceptance Criteria:**
- [ ] Component created in mobile folder
- [ ] Uses existing API endpoint
- [ ] Card brand icons rendered
- [ ] Smooth animations
- [ ] Tested on multiple devices
- [ ] Loading and error states

---

### 1.3 BottomNavigation Component

**File:** `src/components/bottom-navigation.tsx`

**Requirements:**
- Fixed bottom bar (z-index high)
- 4-5 navigation items:
  - 🏠 Início (/)
  - 💳 Transações (/transactions)
  - 📊 Dashboard (/dashboard/mobile)
  - ⚙️ Configurações (/settings)
  - (Optional: 📤 Importar (/upload))
- Active state highlighted
- Icons + labels
- Smooth transitions
- Only show on mobile (< lg breakpoint)
- Safe area padding for iOS

**Estimated Effort:** 3 hours

**Acceptance Criteria:**
- [ ] Component created and styled
- [ ] Navigation works correctly
- [ ] Active state updates
- [ ] Hidden on desktop
- [ ] Safe area respected
- [ ] Tested on iOS/Android

---

### 1.4 Add Components to Mobile Dashboard

**File:** `src/app/dashboard/mobile/page.tsx`

**Requirements:**
- Import new components
- Add CategoryExpensesMobile below BudgetMobile
- Add CreditCardExpensesMobile below CategoryExpenses
- Ensure proper spacing (space-y-4)
- Test data flow
- Verify loading states

**Estimated Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Components integrated
- [ ] Data flows correctly
- [ ] Loading states work
- [ ] Error handling in place
- [ ] Tested with real data

---

## 📋 Priority 2: Backend Enhancements (Next Sprint)

### 2.1 Income Sources API Endpoint

**File:** `app_dev/backend/app/domains/dashboard/router.py`

**Requirements:**
```python
@router.get("/income-sources", response_model=list[IncomeSource])
def get_income_sources(
    year: int = Query(...),
    month: Optional[int] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna receitas agrupadas por Grupo onde CategoriaGeral='Receita'
    
    Response:
    [
        {
            "source": "Salário",
            "total": 10000.00,
            "percentual": 45.5,
            "num_transacoes": 1
        },
        ...
    ]
    """
```

**Implementation Steps:**
1. Add schema in `schemas.py`
2. Add repository method in `repository.py`
3. Add service method in `service.py`
4. Add router endpoint in `router.py`
5. Test with Postman
6. Document in API docs

**Estimated Effort:** 3 hours

**Acceptance Criteria:**
- [ ] Endpoint returns correct data
- [ ] Handles month=None for YTD
- [ ] Percentages sum to 100%
- [ ] Respects user_id filter
- [ ] Tested with multiple scenarios
- [ ] API docs updated

---

### 2.2 Growth Calculation Enhancement

**File:** `app_dev/backend/app/domains/dashboard/repository.py`

**Requirements:**
- Enhance existing `get_metrics()` method
- Add optional parameter: `compare_previous: bool = False`
- If True, calculate:
  - `previous_period_balance` (same period last year)
  - `growth_percentage` ((current - previous) / previous * 100)
  - `growth_absolute` (current - previous)
- Update schema to include new fields

**Implementation Steps:**
1. Update `DashboardMetrics` schema
2. Modify repository to support comparison
3. Update service layer
4. Test with various date ranges
5. Document in API docs

**Estimated Effort:** 4 hours

**Acceptance Criteria:**
- [ ] Calculates growth correctly
- [ ] Handles edge cases (no previous data)
- [ ] Backward compatible (compare=False default)
- [ ] Tested with real data
- [ ] API docs updated
- [ ] Frontend can consume

---

### 2.3 Recent Transactions Endpoint

**Note:** This endpoint likely already exists in `/transactions/list`

**Requirements:**
- Verify endpoint supports `limit` parameter
- Verify returns only non-ignored transactions
- Verify sorts by date descending
- Add dashboard-specific filter if needed

**Implementation Steps:**
1. Test existing `/transactions/list?limit=5`
2. If missing, add to transactions domain
3. Document for dashboard use
4. Test performance

**Estimated Effort:** 2 hours (if exists) or 4 hours (if create)

**Acceptance Criteria:**
- [ ] Endpoint returns last 5 transactions
- [ ] Respects user_id
- [ ] Sorted by date DESC
- [ ] Includes necessary fields
- [ ] Performant (< 100ms)
- [ ] Documented

---

## 📋 Priority 3: New Feature Components (Sprint 3)

### 3.1 IncomeSources Component

**File:** `src/features/dashboard/components/shared/income-sources.tsx`

**Requirements:**
- Desktop and Mobile variants (or responsive)
- Donut chart showing distribution
- List of sources with amounts
- Color-coded segments
- Tap/click source to see transactions (future)
- Empty state if no income

**Dependencies:**
- Backend: `/dashboard/income-sources` endpoint (Priority 2.1)
- Library: recharts (already installed)

**Estimated Effort:** 6 hours

**Acceptance Criteria:**
- [ ] Desktop version complete
- [ ] Mobile version complete
- [ ] Donut chart renders correctly
- [ ] Colors match design system
- [ ] Percentages accurate
- [ ] Loading/error states
- [ ] Tested on multiple browsers

---

### 3.2 GrowthIndicator Component

**File:** `src/features/dashboard/components/shared/growth-indicator.tsx`

**Requirements:**
- Small badge-style component
- Shows: "+2.5%" or "-1.2%"
- Color: green (positive), red (negative)
- Icon: ↑ (up) or ↓ (down)
- Tooltip with details on hover
- Can be inline or standalone

**Dependencies:**
- Backend: Enhanced `/dashboard/metrics?compare=true` (Priority 2.2)

**Estimated Effort:** 2 hours

**Acceptance Criteria:**
- [ ] Component created
- [ ] Correct color logic
- [ ] Icon renders
- [ ] Tooltip works
- [ ] Reusable across pages
- [ ] Accessible (ARIA)

---

### 3.3 RecentTransactions Component

**File:** `src/features/dashboard/components/mobile/recent-transactions-mobile.tsx`

**Requirements:**
- Collapsible card
- Shows last 5 transactions
- Each transaction:
  - Icon (category/type)
  - Name/description
  - Date
  - Amount (colored)
- Tap transaction to see details
- "Ver todas" button to go to transactions page
- Empty state

**Dependencies:**
- Backend: `/transactions/list?limit=5` (Priority 2.3)

**Estimated Effort:** 4 hours

**Acceptance Criteria:**
- [ ] Component created
- [ ] Lists 5 transactions
- [ ] Correct icons
- [ ] Amount formatting
- [ ] Navigation works
- [ ] Empty state shown
- [ ] Loading state
- [ ] Error handling

---

### 3.4 TabsView Component (Optional)

**File:** `src/features/dashboard/components/shared/tabs-view.tsx`

**Requirements:**
- 3 tabs: Income | Expenses | Budget
- Content changes based on active tab
- State persists during session
- URL param optional (?tab=income)

**Tab Content:**
- **Income Tab:**
  - IncomeSources component
  - Total income card
  - Income trend mini-chart
  
- **Expenses Tab:**
  - CategoryExpenses component
  - CreditCardExpenses component
  - Total expenses card
  
- **Budget Tab:**
  - BudgetVsActual component
  - Savings progress
  - Monthly summary

**Estimated Effort:** 6 hours

**Acceptance Criteria:**
- [ ] Tabs render correctly
- [ ] Content switches smoothly
- [ ] State persists
- [ ] URL param works
- [ ] Responsive design
- [ ] Tested on mobile/desktop
- [ ] Keyboard accessible

---

## 📋 Priority 4: Polish & UX (Sprint 4)

### 4.1 Responsive Layout System

**Files:**
- `src/components/responsive-layout.tsx` (new)
- `src/components/dashboard-layout.tsx` (update)
- `src/components/mobile-layout.tsx` (new)

**Requirements:**
- Single layout component that adapts
- Sidebar on desktop (≥ lg breakpoint)
- Bottom nav on mobile (< lg breakpoint)
- Smooth transition between modes
- Context for active page

**Estimated Effort:** 5 hours

---

### 4.2 Loading Skeletons

**Files:** Various component files

**Requirements:**
- Add skeleton states to all widgets
- Use consistent skeleton style
- Smooth transitions to real data
- No layout shift

**Estimated Effort:** 3 hours

---

### 4.3 Error Boundaries

**Files:** Component error boundaries

**Requirements:**
- Catch component errors gracefully
- Show friendly error message
- Log to console/monitoring
- Retry button

**Estimated Effort:** 2 hours

---

### 4.4 Performance Optimization

**Requirements:**
- Lazy load components
- Memoize expensive computations
- Optimize chart rendering
- Add caching for API calls
- Reduce bundle size

**Estimated Effort:** 4 hours

---

## 📋 Priority 5: Testing & Documentation (Ongoing)

### 5.1 Component Tests

**Requirements:**
- Unit tests for all new components
- Integration tests for API calls
- E2E tests for critical flows
- Test coverage ≥ 80%

**Tools:** Jest, React Testing Library, Playwright

**Estimated Effort:** 8 hours

---

### 5.2 API Documentation

**Requirements:**
- Update API docs for new endpoints
- Add request/response examples
- Document error codes
- Add authentication requirements

**Estimated Effort:** 2 hours

---

### 5.3 Component Documentation

**Requirements:**
- Storybook stories for components
- Props documentation
- Usage examples
- Design system integration

**Estimated Effort:** 4 hours

---

## 🗓️ Sprint Planning

### Sprint 1 (Current) - Essential Mobile Features
**Duration:** 1 week  
**Focus:** Get mobile dashboard to 90% completion

**Tasks:**
- [x] Research existing dashboard (done)
- [ ] CategoryExpensesMobile (4h)
- [ ] CreditCardExpensesMobile (4h)
- [ ] BottomNavigation (3h)
- [ ] Integration (1h)
- [ ] Testing (4h)

**Total:** ~16 hours

---

### Sprint 2 - Backend Enhancements
**Duration:** 1 week  
**Focus:** Add missing APIs for new features

**Tasks:**
- [ ] Income Sources API (3h)
- [ ] Growth Calculation (4h)
- [ ] Recent Transactions (2h)
- [ ] Testing & Documentation (3h)

**Total:** ~12 hours

---

### Sprint 3 - New Feature Components
**Duration:** 1 week  
**Focus:** Add income sources and growth indicators

**Tasks:**
- [ ] IncomeSources Component (6h)
- [ ] GrowthIndicator Component (2h)
- [ ] RecentTransactions Component (4h)
- [ ] Integration (2h)
- [ ] Testing (3h)

**Total:** ~17 hours

---

### Sprint 4 - Polish & Optional Features
**Duration:** 1 week  
**Focus:** Responsive layout, tabs, UX improvements

**Tasks:**
- [ ] Responsive Layout (5h)
- [ ] TabsView (6h)
- [ ] Loading Skeletons (3h)
- [ ] Error Boundaries (2h)
- [ ] Performance (4h)
- [ ] Testing (4h)

**Total:** ~24 hours

---

## ✅ Definition of Done

For each task to be considered complete:

- [ ] Code written and reviewed
- [ ] Component works on desktop (if applicable)
- [ ] Component works on mobile (if applicable)
- [ ] Tested on Chrome, Safari, Firefox
- [ ] Tested on iOS and Android (mobile)
- [ ] Loading states implemented
- [ ] Error states implemented
- [ ] Empty states implemented
- [ ] Accessibility checked (keyboard, screen reader)
- [ ] Performance acceptable (< 100ms render)
- [ ] No console errors or warnings
- [ ] Code follows project conventions
- [ ] PR approved and merged
- [ ] Documentation updated

---

## 🚀 Quick Start (For Developers)

### To Start Working on Sprint 1:

1. **Read Research Documents:**
   ```bash
   cat docs/planning/DASHBOARD_RESEARCH_FINDINGS.md
   cat docs/planning/DASHBOARD_COMPARISON_VISUAL.md
   ```

2. **Set Up Development Environment:**
   ```bash
   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
   ./scripts/deploy/quick_start.sh
   ```

3. **Open Mobile Dashboard:**
   - Navigate to: http://localhost:3000/dashboard/mobile
   - Login with test account
   - Inspect existing components

4. **Create Feature Branch:**
   ```bash
   git checkout -b feature/mobile-category-expenses
   ```

5. **Create Component File:**
   ```bash
   mkdir -p app_dev/frontend/src/features/dashboard/components/mobile
   touch app_dev/frontend/src/features/dashboard/components/mobile/category-expenses-mobile.tsx
   ```

6. **Start Coding:**
   - Copy structure from existing `budget-mobile.tsx`
   - Adapt for category expenses
   - Test with real API data

7. **Test Locally:**
   ```bash
   # Backend should be running (port 8000)
   # Frontend should be running (port 3000)
   # Test on mobile viewport in browser DevTools
   ```

8. **Submit PR:**
   - Create PR with screenshots
   - Request review
   - Address feedback
   - Merge when approved

---

## 📞 Support & Questions

**Questions About:**
- Architecture → Read `DASHBOARD_RESEARCH_FINDINGS.md`
- Visual Design → Read `DASHBOARD_COMPARISON_VISUAL.md`
- API Endpoints → Check `app_dev/backend/app/domains/dashboard/router.py`
- Existing Components → Check `app_dev/frontend/src/features/dashboard/components/`
- Integration Strategy → See Part 4 of research document

**Need Help?**
- Check existing mobile components for patterns
- Review desktop components for logic reuse
- Test with real data using existing APIs
- Follow project conventions (see `.github/copilot-instructions.md`)

---

## 📊 Progress Tracking

Use this checklist to track overall progress:

### Sprint 1 (Essential Mobile)
- [ ] CategoryExpensesMobile created
- [ ] CreditCardExpensesMobile created
- [ ] BottomNavigation created
- [ ] Components integrated
- [ ] Tested on devices
- [ ] PR merged

### Sprint 2 (Backend APIs)
- [ ] Income Sources API added
- [ ] Growth Calculation added
- [ ] Recent Transactions verified
- [ ] APIs tested
- [ ] Documentation updated
- [ ] PR merged

### Sprint 3 (New Features)
- [ ] IncomeSources component created
- [ ] GrowthIndicator component created
- [ ] RecentTransactions component created
- [ ] Components integrated
- [ ] Tested thoroughly
- [ ] PR merged

### Sprint 4 (Polish)
- [ ] Responsive Layout implemented
- [ ] TabsView implemented
- [ ] Loading skeletons added
- [ ] Error boundaries added
- [ ] Performance optimized
- [ ] PR merged

---

**Status:** Ready for Sprint 1  
**Next Step:** Assign tasks and start development  
**Questions?** See research documents or ask in team chat
