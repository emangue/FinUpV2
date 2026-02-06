# Implementation Guide - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0  
**Objetivo:** Ordem exata de implementação com dependências claras

---

## 1. Grafo de Dependências (DAG)

```
Sprint 0: Setup
├── Design Tokens ────────────┐
│   ├── mobile-colors.ts      │
│   ├── mobile-dimensions.ts  │ (DEPENDÊNCIA)
│   └── mobile-typography.ts  │
│                              ▼
├── Componentes Base ──────────────┐
│   ├── IconButton            │    │
│   ├── MobileHeader ◄────────┘    │ (DEPENDÊNCIA)
│   └── BottomNavigation           │
│                                   ▼
└── Backend ────────────────────────────┐
    └── copy-to-year endpoint          │
                                        │
                                        ▼
Sprint 1: Dashboard + Profile ──────────┐
├── MonthScrollPicker ◄─────────────────┘ (DEPENDÊNCIA)
├── YTDToggle
├── Dashboard Page
└── Profile Page
         │
         ▼
Sprint 2: Metas + Upload
├── DonutChart
├── TrackerCard
├── CategoryRowInline
├── Budget Page
└── Upload Page
         │
         ▼
Sprint 3: Transações + A11y
├── GrupoBreakdownBottomSheet
├── BudgetEditBottomSheet
└── Validação Acessibilidade
         │
         ▼
Sprint 4: QA + Polish
└── Testes + Ajustes
```

---

## 2. Ordem de Implementação Detalhada

### Sprint 0: Setup e Componentes Base

#### Fase 0.1: Design Tokens (1-2h) 🔴 CRÍTICO - FAZER PRIMEIRO

**Ordem exata:**

1. **Criar pasta config:**
   ```bash
   mkdir -p app_dev/frontend/src/config
   ```

2. **Criar mobile-colors.ts:**
   ```bash
   # Copiar código da TECH_SPEC.md Seção 2.3.1
   touch app_dev/frontend/src/config/mobile-colors.ts
   ```
   
   **Validação:**
   ```typescript
   // Teste rápido
   import { categoryColors, getCategoryColor } from './mobile-colors';
   console.log(getCategoryColor('Moradia')); // 'purple'
   ```

3. **Criar mobile-dimensions.ts:**
   ```bash
   touch app_dev/frontend/src/config/mobile-dimensions.ts
   ```
   
   **Validação:**
   ```typescript
   import { mobileDimensions } from './mobile-dimensions';
   console.log(mobileDimensions.sizes.touchTargetMinimum.px); // 44
   ```

4. **Criar mobile-typography.ts:**
   ```bash
   touch app_dev/frontend/src/config/mobile-typography.ts
   ```
   
   **Validação:**
   ```typescript
   import { mobileTypography } from './mobile-typography';
   console.log(mobileTypography.pageTitle.tailwind); // 'text-[34px]...'
   ```

**Critério de conclusão:**
- ✅ 3 arquivos criados
- ✅ Imports sem erro
- ✅ TypeScript compila: `npm run build`

---

#### Fase 0.2: Componentes Base (4-6h)

**⚠️ ATENÇÃO:** IconButton e MobileHeader **DEPENDEM** dos design tokens criados na Fase 0.1.

**Ordem exata:**

1. **Criar pasta mobile:**
   ```bash
   mkdir -p app_dev/frontend/src/components/mobile
   ```

2. **Criar IconButton (1h):**
   ```bash
   touch app_dev/frontend/src/components/mobile/icon-button.tsx
   ```
   
   **Código:** Ver TECH_SPEC.md Seção 3.2
   
   **Teste rápido:**
   ```typescript
   // app_dev/frontend/src/app/test-icon-button/page.tsx
   import { IconButton } from '@/components/mobile/icon-button';
   import { Search } from 'lucide-react';
   
   export default function TestPage() {
     return (
       <IconButton 
         icon={<Search />}
         label="Buscar"
         onClick={() => alert('Clicked!')}
       />
     );
   }
   ```
   
   **Validação:**
   - [ ] Botão renderiza
   - [ ] Tamanho correto (44x44px)
   - [ ] Click funciona

3. **Criar MobileHeader (2h):**
   ```bash
   touch app_dev/frontend/src/components/mobile/mobile-header.tsx
   ```
   
   **Código:** Ver TECH_SPEC.md Seção 3.1
   
   **Teste rápido:**
   ```typescript
   // app_dev/frontend/src/app/test-mobile-header/page.tsx
   import { MobileHeader } from '@/components/mobile/mobile-header';
   import { Search, Calendar } from 'lucide-react';
   
   export default function TestPage() {
     return (
       <MobileHeader 
         title="Dashboard"
         leftAction="logo"
         rightActions={[
           { icon: <Search />, label: 'Buscar', onClick: () => {} },
           { icon: <Calendar />, label: 'Calendário', onClick: () => {} }
         ]}
       />
     );
   }
   ```
   
   **Validação:**
   - [ ] Header renderiza
   - [ ] Logo aparece
   - [ ] Botões direita funcionam
   - [ ] Touch targets ≥ 44px

4. **Criar BottomNavigation (3-4h):**
   ```bash
   touch app_dev/frontend/src/components/mobile/bottom-navigation.tsx
   ```
   
   **Código:** Ver TECH_SPEC.md Seção 3.2
   
   **Teste rápido:**
   ```typescript
   // app_dev/frontend/src/app/mobile/layout.tsx
   import { BottomNavigation } from '@/components/mobile/bottom-navigation';
   
   export default function MobileLayout({ children }: { children: React.ReactNode }) {
     return (
       <div className="min-h-screen bg-white pb-20">
         {children}
         <BottomNavigation />
       </div>
     );
   }
   ```
   
   **Validação:**
   - [ ] Navegação fixa no rodapé
   - [ ] 5 tabs visíveis
   - [ ] FAB central destacado
   - [ ] Click muda de tab (indicador visual)

**Critério de conclusão:**
- ✅ 3 componentes criados
- ✅ Todos os testes rápidos passam
- ✅ Sem erros no console

---

#### Fase 0.3: Backend - Novo Endpoint (2-3h)

**⚠️ ATENÇÃO:** Este endpoint é necessário para Sprint 2 (Budget), mas deve ser criado AGORA para evitar bloqueio.

1. **Criar função no service:**
   ```bash
   # Editar arquivo existente
   vim app_dev/backend/app/domains/budget/service.py
   ```
   
   **Adicionar:**
   ```python
   def copy_budget_to_year(
       self,
       user_id: int,
       mes_origem: str,  # "2026-02"
       ano_destino: int,
       substituir_existentes: bool
   ) -> dict:
       # Ver código completo em API_SPEC.md Seção 3.4
       pass
   ```

2. **Adicionar rota:**
   ```bash
   vim app_dev/backend/app/domains/budget/router.py
   ```
   
   **Adicionar:**
   ```python
   @router.post("/geral/copy-to-year", response_model=CopyToYearResponse)
   async def copy_budget_to_year(
       payload: CopyToYearPayload,
       current_user: User = Depends(get_current_user),
       session: Session = Depends(get_session)
   ):
       service = BudgetService(session)
       result = service.copy_budget_to_year(
           user_id=current_user.id,
           mes_origem=payload.mes_origem,
           ano_destino=payload.ano_destino,
           substituir_existentes=payload.substituir_existentes
       )
       return result
   ```

3. **Teste manual:**
   ```bash
   # 1. Rodar servidor
   cd app_dev/backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   
   # 2. Testar no Swagger
   # http://localhost:8000/docs
   # POST /api/v1/budget/geral/copy-to-year
   ```
   
   **Body de teste:**
   ```json
   {
     "mes_origem": "2026-02",
     "ano_destino": 2026,
     "substituir_existentes": true
   }
   ```
   
   **Resposta esperada:**
   ```json
   {
     "sucesso": true,
     "meses_criados": 11,
     "metas_copiadas": 22,
     "mensagem": "Metas copiadas de 2026-02 para 11 meses de 2026"
   }
   ```

**Critério de conclusão:**
- ✅ Endpoint funciona no Swagger
- ✅ Resposta correta (status 200)
- ✅ Dados persistem no banco

---

### Sprint 1: Dashboard + Profile (14-21h)

#### Fase 1.1: Estrutura de Rotas (1h)

**Ordem exata:**

1. **Criar pasta mobile:**
   ```bash
   mkdir -p app_dev/frontend/src/app/mobile
   ```

2. **Criar layout mobile:**
   ```bash
   touch app_dev/frontend/src/app/mobile/layout.tsx
   ```
   
   **Código:**
   ```typescript
   import { BottomNavigation } from '@/components/mobile/bottom-navigation';
   
   export default function MobileLayout({ children }: { children: React.ReactNode }) {
     return (
       <div className="min-h-screen bg-white pb-20">
         {children}
         <BottomNavigation />
       </div>
     );
   }
   ```

3. **Criar middleware de redirecionamento:**
   ```bash
   touch app_dev/frontend/src/middleware.ts
   ```
   
   **Código:** Ver TECH_SPEC.md Seção 2.2.2

**Critério de conclusão:**
- ✅ Pasta mobile criada
- ✅ Layout existe
- ✅ Middleware redireciona mobile → `/mobile/*`

---

#### Fase 1.2: MonthScrollPicker (4-6h) 🔴 CRÍTICO

**⚠️ DEPENDÊNCIA:** Design tokens (Fase 0.1)

1. **Criar componente:**
   ```bash
   touch app_dev/frontend/src/components/mobile/month-scroll-picker.tsx
   ```
   
   **Código:** Ver PRD Seção 4.1.6 (linhas 643-718)

2. **Teste isolado:**
   ```typescript
   // app_dev/frontend/src/app/test-month-picker/page.tsx
   'use client';
   
   import { useState } from 'react';
   import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker';
   
   export default function TestPage() {
     const [year, setYear] = useState(2026);
     const [month, setMonth] = useState(2);
     
     return (
       <div className="p-4">
         <p>Selecionado: {month}/{year}</p>
         <MonthScrollPicker
           selectedYear={year}
           selectedMonth={month}
           onMonthChange={(y, m) => {
             setYear(y);
             setMonth(m);
           }}
         />
       </div>
     );
   }
   ```
   
   **Validação:**
   - [ ] Scroll horizontal funciona
   - [ ] Pill selecionada destaca (preto)
   - [ ] Callback é chamado ao clicar
   - [ ] Últimos 12 meses + próximos 3 visíveis

**Critério de conclusão:**
- ✅ Componente renderiza
- ✅ Scroll suave
- ✅ Seleção funciona

---

#### Fase 1.3: YTDToggle (2-3h)

**⚠️ DEPENDÊNCIA:** Design tokens (Fase 0.1)

1. **Criar componente:**
   ```bash
   touch app_dev/frontend/src/components/mobile/ytd-toggle.tsx
   ```
   
   **Código:** Ver PRD Seção 4.3.5 (linhas 1031-1086)

2. **Teste isolado:**
   ```typescript
   // app_dev/frontend/src/app/test-ytd-toggle/page.tsx
   'use client';
   
   import { useState } from 'react';
   import { YTDToggle } from '@/components/mobile/ytd-toggle';
   
   export default function TestPage() {
     const [mode, setMode] = useState<'month' | 'ytd'>('month');
     
     return (
       <div className="p-4">
         <p>Modo: {mode}</p>
         <YTDToggle
           mode={mode}
           onChange={setMode}
         />
       </div>
     );
   }
   ```

**Critério de conclusão:**
- ✅ Toggle renderiza
- ✅ Selecionado destaca (branco + sombra)
- ✅ Callback é chamado

---

#### Fase 1.4: Dashboard Page (4-6h)

**⚠️ DEPENDÊNCIAS:**
- MonthScrollPicker (Fase 1.2)
- YTDToggle (Fase 1.3)
- MobileHeader (Fase 0.2)

1. **Criar página:**
   ```bash
   mkdir -p app_dev/frontend/src/app/mobile/dashboard
   touch app_dev/frontend/src/app/mobile/dashboard/page.tsx
   ```

2. **Implementação incremental:**
   
   **Passo 1: Estrutura básica (1h)**
   ```typescript
   import { MobileHeader } from '@/components/mobile/mobile-header';
   import { Search, Calendar } from 'lucide-react';
   
   export default function DashboardMobilePage() {
     return (
       <div className="min-h-screen bg-white">
         <MobileHeader 
           title="Dashboard"
           leftAction="logo"
           rightActions={[
             { icon: <Search />, label: 'Buscar', onClick: () => {} },
             { icon: <Calendar />, label: 'Calendário', onClick: () => {} }
           ]}
         />
         <div className="p-5">
           <h2>Dashboard Mobile</h2>
         </div>
       </div>
     );
   }
   ```
   
   **Passo 2: Adicionar MonthScrollPicker (1h)**
   ```typescript
   'use client';
   
   import { useState } from 'react';
   import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker';
   
   export default function DashboardMobilePage() {
     const [year, setYear] = useState(2026);
     const [month, setMonth] = useState(2);
     
     return (
       <>
         {/* Header */}
         <MonthScrollPicker
           selectedYear={year}
           selectedMonth={month}
           onMonthChange={(y, m) => {
             setYear(y);
             setMonth(m);
             // TODO: fetchMetrics(y, m)
           }}
         />
         {/* Resto do conteúdo */}
       </>
     );
   }
   ```
   
   **Passo 3: Adicionar YTDToggle (30min)**
   ```typescript
   const [ytdMode, setYTDMode] = useState<'month' | 'ytd'>('month');
   
   <YTDToggle
     mode={ytdMode}
     onChange={(mode) => {
       setYTDMode(mode);
       // TODO: fetchMetrics com YTD
     }}
   />
   ```
   
   **Passo 4: Integrar com API (2-3h)**
   ```typescript
   const [loading, setLoading] = useState(true);
   const [metrics, setMetrics] = useState(null);
   
   useEffect(() => {
     fetchMetrics();
   }, [year, month, ytdMode]);
   
   const fetchMetrics = async () => {
     setLoading(true);
     try {
       const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
       const token = localStorage.getItem('token');
       
       const params = ytdMode === 'ytd' 
         ? `?year=${year}&ytd=true`
         : `?year=${year}&month=${month}`;
       
       const response = await fetch(
         `${apiUrl}/api/v1/dashboard/budget-vs-actual${params}`,
         { headers: { 'Authorization': `Bearer ${token}` } }
       );
       
       const data = await response.json();
       setMetrics(data);
     } finally {
       setLoading(false);
     }
   };
   ```

**Critério de conclusão:**
- ✅ Página carrega
- ✅ MonthScrollPicker funciona
- ✅ YTDToggle funciona
- ✅ Métricas carregam da API
- ✅ Loading state funciona

---

#### Fase 1.5: Profile Page (4-6h)

**⚠️ DEPENDÊNCIAS:**
- MobileHeader (Fase 0.2)

1. **Criar página:**
   ```bash
   mkdir -p app_dev/frontend/src/app/mobile/profile
   touch app_dev/frontend/src/app/mobile/profile/page.tsx
   ```

2. **Código completo:** Ver PRD Seção 4.4.2 (linhas 1407-1630)

3. **Validação:**
   - [ ] Exibe dados do usuário
   - [ ] Edição de nome/email funciona
   - [ ] Alterar senha funciona
   - [ ] **Logout funciona e redireciona para /login** 🔴 CRÍTICO

**Critério de conclusão:**
- ✅ Profile renderiza
- ✅ Edições salvam
- ✅ Logout funciona

---

### Sprint 2: Metas + Upload (16-24h)

#### Fase 2.1: DonutChart (3-4h)

**⚠️ DEPENDÊNCIA:** Instalar Recharts

1. **Instalar dependência:**
   ```bash
   cd app_dev/frontend
   npm install recharts
   ```

2. **Criar componente:**
   ```bash
   touch app_dev/frontend/src/components/mobile/donut-chart.tsx
   ```
   
   **Código:** Ver PRD Seção 4.3.4 (linhas 925-1026)

3. **Teste isolado:**
   ```typescript
   // app_dev/frontend/src/app/test-donut-chart/page.tsx
   import { DonutChart } from '@/components/mobile/donut-chart';
   
   export default function TestPage() {
     return (
       <DonutChart
         data={[
           { name: 'Moradia', value: 2100, color: '#DDD6FE' },
           { name: 'Alimentação', value: 1850, color: '#DBEAFE' },
         ]}
         total={10000}
         centerLabel="R$ 3.950,00"
         centerSubtitle="realizado de R$ 10.000"
         periodLabel="Fevereiro 2026"
       />
     );
   }
   ```

**Critério de conclusão:**
- ✅ Gráfico renderiza
- ✅ Texto central está correto
- ✅ Segmento cinza aparece para parte não preenchida

---

#### Fase 2.2: TrackerCard (4-6h)

**⚠️ DEPENDÊNCIA:** Design tokens (Fase 0.1)

1. **Criar componente:**
   ```bash
   touch app_dev/frontend/src/components/mobile/tracker-card.tsx
   ```
   
   **Código:** Ver STYLE_GUIDE.md (linhas 230-322)

2. **Teste isolado:**
   ```typescript
   import { TrackerCard } from '@/components/mobile/tracker-card';
   import { Home } from 'lucide-react';
   
   export default function TestPage() {
     return (
       <TrackerCard
         category="Moradia"
         frequency="Todo Mês"
         currentAmount={2100}
         totalAmount={2500}
         icon={Home}
         colorScheme="purple"
         onClick={() => alert('Clicked!')}
       />
     );
   }
   ```

**Critério de conclusão:**
- ✅ Card renderiza corretamente
- ✅ Progress bar anima
- ✅ Click funciona

---

#### Fase 2.3: CategoryRowInline (2-3h)

1. **Criar componente:**
   ```bash
   touch app_dev/frontend/src/components/mobile/category-row-inline.tsx
   ```
   
   **Código:** Ver PRD Seção 4.3.6

**Critério de conclusão:**
- ✅ Renderiza inline
- ✅ Badge % aparece
- ✅ Progress bar funciona

---

#### Fase 2.4: Budget Page (8-12h)

**⚠️ DEPENDÊNCIAS:**
- DonutChart (Fase 2.1)
- TrackerCard (Fase 2.2)
- CategoryRowInline (Fase 2.3)
- YTDToggle (Fase 1.3)
- copy-to-year endpoint (Fase 0.3)

**Implementar em 2 sub-fases:**

**Fase 2.4.1: Visualização (4-6h)**
```bash
mkdir -p app_dev/frontend/src/app/mobile/budget
touch app_dev/frontend/src/app/mobile/budget/page.tsx
```

**Fase 2.4.2: Edição (4-6h)**
```bash
mkdir -p app_dev/frontend/src/app/mobile/budget/edit
touch app_dev/frontend/src/app/mobile/budget/edit/page.tsx
```

---

#### Fase 2.5: Upload Page (6-9h)

**⚠️ DEPENDÊNCIA:** MobileHeader (Fase 0.2)

```bash
mkdir -p app_dev/frontend/src/app/mobile/upload
touch app_dev/frontend/src/app/mobile/upload/page.tsx
```

---

### Sprint 3: Transações + A11y (6-10h)

#### Fase 3.1: GrupoBreakdownBottomSheet (4-6h)

**⚠️ DEPENDÊNCIA:** Criar endpoint backend `GET /transactions/grupo-breakdown`

1. **Backend primeiro (2-3h):**
   ```bash
   # Ver API_SPEC.md Seção 4.4
   vim app_dev/backend/app/domains/transactions/service.py
   ```

2. **Frontend depois (2-3h):**
   ```bash
   touch app_dev/frontend/src/components/mobile/grupo-breakdown-sheet.tsx
   ```
   
   **Código:** Ver TECH_SPEC.md Seção 3.9

---

#### Fase 3.2: Acessibilidade (2-4h)

**Validação sistemática:**

1. **Touch targets (1h):**
   ```bash
   # Rodar script de validação
   npm run test:a11y -- --grep "Touch targets"
   ```

2. **ARIA labels (1h):**
   ```bash
   # Adicionar em todos os IconButtons
   # Ver TESTING_STRATEGY.md
   ```

3. **Contraste (30min):**
   ```bash
   # Usar ferramenta automática
   npx axe http://localhost:3000/mobile/dashboard
   ```

4. **Screen readers (1-2h):**
   - [ ] Testar com VoiceOver (iOS)
   - [ ] Testar com TalkBack (Android)

---

### Sprint 4: QA + Polish (8-12h)

**Ordem:**

1. **Testes E2E (3-4h):** Rodar suite completa
2. **Dispositivos reais (3-4h):** Testar em 5 dispositivos
3. **Performance (2-3h):** Lighthouse + otimizações
4. **Ajustes finais (2-3h):** Bugs encontrados

---

## 3. Checklist de Validação por Fase

### Após Fase 0.1 (Design Tokens)
- [ ] 3 arquivos criados
- [ ] `npm run build` sem erros
- [ ] Imports funcionam

### Após Fase 0.2 (Componentes Base)
- [ ] 3 componentes criados
- [ ] Testes isolados passam
- [ ] BottomNavigation visível

### Após Fase 0.3 (Backend)
- [ ] Endpoint funciona no Swagger
- [ ] Teste manual OK

### Após Sprint 1
- [ ] Dashboard mobile funciona
- [ ] Profile mobile funciona
- [ ] Logout funciona
- [ ] Testes de regressão passam

### Após Sprint 2
- [ ] Budget visualização funciona
- [ ] Budget edição funciona
- [ ] Upload funciona
- [ ] Copiar para ano funciona

### Após Sprint 3
- [ ] Drill-down subgrupos funciona
- [ ] Acessibilidade validada (0 erros críticos)

### Após Sprint 4
- [ ] Todos os testes E2E passam
- [ ] Lighthouse score ≥ 90
- [ ] 5 dispositivos validados

---

## 4. Comandos Úteis

### Desenvolvimento
```bash
# Frontend dev
cd app_dev/frontend
npm run dev

# Backend dev
cd app_dev/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Testes
npm run test:watch           # Unit tests
npm run test:e2e:ui          # E2E com UI
npm run test:a11y            # Acessibilidade
```

### Build
```bash
# Frontend build
npm run build
npm run start

# Backend
# (Já roda em produção via systemd)
```

### Validação
```bash
# TypeScript check
npx tsc --noEmit

# Linter
npm run lint

# Lighthouse
npx lighthouse http://localhost:3000/mobile/dashboard --view
```

---

**Fim do Implementation Guide**

**Data:** 31/01/2026  
**Status:** ✅ Completo  
**Use este guia:** Como checklist passo a passo!
