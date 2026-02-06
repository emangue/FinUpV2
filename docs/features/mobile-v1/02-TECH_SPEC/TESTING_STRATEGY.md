# Testing Strategy - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0  
**Objetivo:** Garantir que cada sprint não quebre funcionalidades existentes

---

## 1. Estratégia de Testes Incremental

### 1.1 Princípios

1. **Teste antes de avançar:** Cada sprint só começa após smoke tests do sprint anterior
2. **Regressão automática:** Suite de testes E2E roda em cada PR
3. **Validação contínua:** Testes unitários rodam em cada commit
4. **Mobile-first:** Testes em dispositivos reais, não apenas simuladores

---

## 2. Smoke Tests por Sprint

### Sprint 0: Setup + Componentes Base

**Objetivo:** Validar que a estrutura básica funciona antes de criar telas.

#### Checklist de Validação

**Backend:**
- [ ] Servidor FastAPI rodando (http://localhost:8000)
- [ ] Health check responde 200: `GET /health`
- [ ] Login funciona: `POST /auth/login` retorna token
- [ ] Novo endpoint `POST /budget/geral/copy-to-year` criado
- [ ] Swagger docs acessível: http://localhost:8000/docs

**Frontend:**
- [ ] Next.js rodando (http://localhost:3000)
- [ ] Arquivos de design tokens criados:
  - [ ] `src/config/mobile-colors.ts` existe
  - [ ] `src/config/mobile-dimensions.ts` existe
  - [ ] `src/config/mobile-typography.ts` existe
- [ ] Componentes base criados:
  - [ ] `src/components/mobile/mobile-header.tsx` existe
  - [ ] `src/components/mobile/bottom-navigation.tsx` existe
  - [ ] `src/components/mobile/icon-button.tsx` existe

**Testes Manuais:**
```bash
# 1. Backend
cd app_dev/backend
source venv/bin/activate
python -c "from app.domains.budget.service import BudgetService; print('✅ Import OK')"

# 2. Frontend
cd app_dev/frontend
npm run build
# Deve compilar sem erros
```

**Critério de Sucesso:** 100% dos itens acima checados antes de iniciar Sprint 1.

---

### Sprint 1: Dashboard + Profile

**Objetivo:** Dashboard e Profile mobile funcionam sem quebrar desktop.

#### Testes de Regressão Desktop

**ANTES de começar Sprint 1, validar que desktop ainda funciona:**

1. [ ] Login desktop funciona (`/login`)
2. [ ] Dashboard desktop carrega (`/dashboard`)
3. [ ] Transações desktop funcionam (`/transactions`)
4. [ ] Budget desktop funciona (`/budget`)
5. [ ] Upload desktop funciona (`/upload`)

**Como testar:**
```bash
# 1. Abrir navegador desktop (>1024px)
# 2. Navegar para cada rota acima
# 3. Validar que não há erros no console
# 4. Validar que dados carregam
```

#### Testes Funcionais Sprint 1

**Dashboard Mobile:**
```typescript
// tests/e2e/sprint1-dashboard.spec.ts

test('Dashboard mobile deve carregar métricas', async ({ page }) => {
  // Setup: viewport mobile
  await page.setViewportSize({ width: 390, height: 844 });
  
  // 1. Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'senha123');
  await page.click('button[type="submit"]');
  
  // 2. Deve redirecionar para /mobile/dashboard
  await expect(page).toHaveURL('/mobile/dashboard');
  
  // 3. MobileHeader deve estar visível
  await expect(page.locator('header h1')).toContainText('Dashboard');
  
  // 4. MonthScrollPicker deve estar visível
  const monthPicker = page.locator('[data-testid="month-scroll-picker"]');
  await expect(monthPicker).toBeVisible();
  
  // 5. Métricas devem carregar (loading → dados)
  await page.waitForSelector('[data-testid="metric-cards"]');
  const realizadoCard = page.locator('text=/R\\$ \\d+/').first();
  await expect(realizadoCard).toBeVisible();
  
  // 6. BottomNavigation deve estar fixo no rodapé
  const bottomNav = page.locator('[data-testid="bottom-navigation"]');
  await expect(bottomNav).toBeVisible();
  await expect(bottomNav).toHaveCSS('position', 'fixed');
});

test('MonthScrollPicker deve mudar métricas ao swipe', async ({ page }) => {
  // ... (login + setup)
  
  // 1. Capturar valor inicial
  const valorInicial = await page.locator('[data-testid="realizado-valor"]').innerText();
  
  // 2. Clicar em mês anterior
  await page.click('text="JAN"');
  
  // 3. Aguardar loading
  await page.waitForTimeout(500);
  
  // 4. Valor deve ter mudado
  const valorNovo = await page.locator('[data-testid="realizado-valor"]').innerText();
  expect(valorNovo).not.toBe(valorInicial);
});

test('YTD Toggle deve agregar dados do ano', async ({ page }) => {
  // ... (login + setup)
  
  // 1. Clicar em YTD
  await page.click('text="YTD"');
  
  // 2. Aguardar loading
  await page.waitForSelector('[data-loading="false"]');
  
  // 3. Validar que MonthScrollPicker está desabilitado
  const monthPicker = page.locator('[data-testid="month-scroll-picker"]');
  await expect(monthPicker).toHaveAttribute('disabled', '');
  
  // 4. Valor de realizado deve ser maior (agregado)
  const valorYTD = await page.locator('[data-testid="realizado-valor"]').innerText();
  expect(valorYTD).toMatch(/R\$ \d{1,3}\.\d{3}/); // Formato mil+
});
```

**Profile Mobile:**
```typescript
// tests/e2e/sprint1-profile.spec.ts

test('Profile mobile deve exibir dados do usuário', async ({ page }) => {
  // ... (login + setup)
  
  // 1. Navegar para profile via bottom nav
  await page.click('[aria-label="Perfil"]');
  await expect(page).toHaveURL('/mobile/profile');
  
  // 2. Deve exibir nome e email
  await expect(page.locator('text="Emanuel Silva"')).toBeVisible();
  await expect(page.locator('text="usuario@email.com"')).toBeVisible();
});

test('Profile mobile deve permitir alterar nome', async ({ page }) => {
  // ... (login + navegar para profile)
  
  // 1. Editar nome
  await page.fill('[name="nome"]', 'Emanuel Silva Santos');
  await page.click('text="Salvar Alterações"');
  
  // 2. Toast de sucesso
  await expect(page.locator('text="Perfil atualizado"')).toBeVisible();
  
  // 3. Reload e validar persistência
  await page.reload();
  await expect(page.locator('[name="nome"]')).toHaveValue('Emanuel Silva Santos');
});

test('Logout deve redirecionar para login', async ({ page }) => {
  // ... (login + navegar para profile)
  
  // 1. Clicar em Sair
  await page.click('text="Sair da Conta"');
  
  // 2. Deve redirecionar para /login
  await expect(page).toHaveURL('/login');
  
  // 3. Token deve ter sido removido
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeNull();
});
```

**Critério de Sucesso:**
- ✅ Todos os testes de regressão desktop passam
- ✅ Todos os testes funcionais Sprint 1 passam
- ✅ Lighthouse score ≥ 90 (mobile)
- ✅ Sem erros no console

---

### Sprint 2: Metas + Upload

**Objetivo:** Metas e Upload mobile funcionam.

#### Testes de Regressão (Sprint 0 + 1)

**ANTES de começar Sprint 2, validar:**

1. [ ] Dashboard mobile ainda funciona (smoke test)
2. [ ] Profile mobile ainda funciona (smoke test)
3. [ ] Login mobile ainda funciona
4. [ ] Desktop não quebrou

**Como testar:**
```bash
npm run test:e2e -- --grep "Sprint 1"
# Todos os testes do Sprint 1 devem passar
```

#### Testes Funcionais Sprint 2

**Metas Mobile - Visualização:**
```typescript
// tests/e2e/sprint2-budget-view.spec.ts

test('Budget mobile deve exibir DonutChart', async ({ page }) => {
  // ... (login + navegar para /mobile/budget)
  
  // 1. DonutChart deve estar visível
  const donut = page.locator('[data-testid="donut-chart"]');
  await expect(donut).toBeVisible();
  
  // 2. Valor central deve estar correto
  const centerLabel = donut.locator('text=/R\\$ \\d+/');
  await expect(centerLabel).toBeVisible();
});

test('CategoryRowInline deve navegar para transações', async ({ page }) => {
  // ... (login + navegar para /mobile/budget)
  
  // 1. Clicar em "Moradia"
  await page.click('[data-category="Moradia"]');
  
  // 2. Deve redirecionar para /mobile/transactions?grupo=Moradia
  await expect(page).toHaveURL(/\/mobile\/transactions\?grupo=Moradia/);
});

test('YTD Toggle deve funcionar em Budget', async ({ page }) => {
  // ... (login + navegar para /mobile/budget)
  
  // 1. Clicar em YTD
  await page.click('text="YTD"');
  
  // 2. Valores devem agregar ano inteiro
  await page.waitForSelector('[data-loading="false"]');
  
  // 3. DonutChart deve atualizar
  const valorYTD = await page.locator('[data-testid="donut-center-value"]').innerText();
  expect(valorYTD).toMatch(/R\$ \d{2,3}\.\d{3}/); // Valor maior
});
```

**Metas Mobile - Edição:**
```typescript
// tests/e2e/sprint2-budget-edit.spec.ts

test('Budget edit deve abrir bottom sheet', async ({ page }) => {
  // ... (login + navegar para /mobile/budget/edit)
  
  // 1. Clicar em TrackerCard
  await page.click('[data-tracker="Alimentação"]');
  
  // 2. Bottom sheet deve abrir
  const sheet = page.locator('[role="dialog"]');
  await expect(sheet).toBeVisible();
  await expect(sheet.locator('text="Editar Meta - Alimentação"')).toBeVisible();
});

test('Budget edit deve salvar novo valor', async ({ page }) => {
  // ... (abrir bottom sheet de Alimentação)
  
  // 1. Alterar valor
  await page.fill('[type="number"]', '2500');
  await page.click('text="Salvar"');
  
  // 2. Toast de sucesso
  await expect(page.locator('text="Meta atualizada"')).toBeVisible();
  
  // 3. TrackerCard deve atualizar
  const card = page.locator('[data-tracker="Alimentação"]');
  await expect(card.locator('text="R$ 2.500"')).toBeVisible();
});

test('Copiar para ano inteiro deve funcionar', async ({ page }) => {
  // ... (navegar para /mobile/budget/edit)
  
  // 1. Clicar em "Colar para 2026"
  await page.click('text="Colar para 2026"');
  
  // 2. Confirm dialog
  await expect(page.locator('text="Copiar para todo o ano?"')).toBeVisible();
  await page.click('text="Substituir meses existentes"');
  
  // 3. Aguardar API call
  await page.waitForResponse(resp => 
    resp.url().includes('/budget/geral/copy-to-year') && resp.status() === 200
  );
  
  // 4. Toast de sucesso
  await expect(page.locator('text=/Copiado para \\d+ meses/')).toBeVisible();
});
```

**Upload Mobile:**
```typescript
// tests/e2e/sprint2-upload.spec.ts

test('Upload deve abrir file picker', async ({ page }) => {
  // ... (login + navegar para /mobile/upload)
  
  // 1. Clicar em "Selecionar Arquivo"
  const fileInput = page.locator('input[type="file"]');
  await expect(fileInput).toBeAttached();
  
  // 2. Simular upload (arquivo de teste)
  await fileInput.setInputFiles('tests/fixtures/extrato_itau.pdf');
  
  // 3. Preview deve carregar
  await expect(page.locator('text="Preview"')).toBeVisible();
});

test('Upload deve importar transações', async ({ page }) => {
  // ... (upload arquivo)
  
  // 1. Clicar em "Confirmar Importação"
  await page.click('text="Confirmar Importação"');
  
  // 2. Aguardar API call
  await page.waitForResponse(resp => 
    resp.url().includes('/upload') && resp.status() === 200
  );
  
  // 3. Toast de sucesso
  await expect(page.locator('text=/\\d+ transações importadas/')).toBeVisible();
  
  // 4. Redirecionar para /mobile/transactions
  await expect(page).toHaveURL('/mobile/transactions');
});
```

**Critério de Sucesso:**
- ✅ Testes de regressão passam (Sprint 0 + 1)
- ✅ Todos os testes funcionais Sprint 2 passam
- ✅ Endpoint `copy-to-year` funciona (backend)
- ✅ Upload importa corretamente

---

### Sprint 3: Transações + Acessibilidade

**Objetivo:** Transações melhoradas + validação a11y.

#### Testes de Regressão (Sprint 0 + 1 + 2)

**ANTES de começar Sprint 3, rodar suite completa:**

```bash
npm run test:e2e
# Todos os testes dos Sprints 0, 1, 2 devem passar
```

#### Testes de Acessibilidade

**Automatizados (axe-core):**
```typescript
// tests/a11y/mobile-accessibility.spec.ts

import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Acessibilidade Mobile', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/mobile/dashboard');
    await injectAxe(page);
  });
  
  test('Dashboard mobile deve passar WCAG AA', async ({ page }) => {
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });
  
  test('MobileHeader deve ter ARIA labels', async ({ page }) => {
    const backButton = page.locator('[aria-label="Voltar"]');
    await expect(backButton).toBeAttached();
    
    const searchButton = page.locator('[aria-label="Buscar"]');
    await expect(searchButton).toBeAttached();
  });
  
  test('Touch targets devem ter mínimo 44px', async ({ page }) => {
    const buttons = page.locator('button:visible');
    const count = await buttons.count();
    
    for (let i = 0; i < count; i++) {
      const box = await buttons.nth(i).boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });
  
  test('Contraste de cores deve ser ≥ 4.5:1', async ({ page }) => {
    await checkA11y(page, null, {
      rules: {
        'color-contrast': { enabled: true },
      },
    });
  });
});
```

**Manuais (Screen Readers):**

**iOS (VoiceOver):**
1. [ ] Ativar VoiceOver: Settings > Accessibility > VoiceOver
2. [ ] Navegar por cada tela mobile:
   - [ ] Dashboard: Ouve "Dashboard, heading level 1"
   - [ ] Bottom Nav: Ouve "Dashboard, tab 1 of 5"
   - [ ] MonthScrollPicker: Ouve "Janeiro 2026, selected"
   - [ ] TrackerCard: Ouve "Moradia, 84%, R$ 2.100 de R$ 2.500"
3. [ ] Validar que TODAS as ações são anunciadas

**Android (TalkBack):**
1. [ ] Ativar TalkBack: Settings > Accessibility > TalkBack
2. [ ] Mesma validação acima

**Critério de Sucesso:**
- ✅ 0 erros críticos no axe-core
- ✅ Touch targets ≥ 44px (100%)
- ✅ Contraste ≥ 4.5:1 (100%)
- ✅ Screen readers anunciam todas as ações

---

### Sprint 4: QA + Ajustes Finais

**Objetivo:** Validação completa e deploy ready.

#### Testes de Performance

**Lighthouse CI:**
```yaml
# .github/workflows/lighthouse.yml

name: Lighthouse CI

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000/mobile/dashboard
            http://localhost:3000/mobile/budget
            http://localhost:3000/mobile/transactions
          configPath: './lighthouserc.json'
```

**lighthouserc.json:**
```json
{
  "ci": {
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "interactive": ["error", { "maxNumericValue": 3000 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    }
  }
}
```

#### Testes em Dispositivos Reais

**Checklist de Dispositivos:**

| Dispositivo | Resolução | OS | Tester | Status |
|-------------|-----------|----|----|--------|
| iPhone SE (2020) | 375x667px | iOS 17+ | QA1 | [ ] |
| iPhone 14 | 390x844px | iOS 17+ | QA1 | [ ] |
| iPhone 14 Pro Max | 428x926px | iOS 17+ | QA2 | [ ] |
| Samsung Galaxy S21 | 360x800px | Android 13+ | QA2 | [ ] |
| Google Pixel 7 | 412x915px | Android 14+ | QA3 | [ ] |

**Para cada dispositivo, validar:**
1. [ ] Login funciona
2. [ ] Dashboard carrega métricas
3. [ ] MonthScrollPicker swipe funciona
4. [ ] Budget visualização e edição funcionam
5. [ ] Upload funciona (câmera + galeria)
6. [ ] Transações carregam e filtram
7. [ ] Profile edita e logout funciona
8. [ ] Não há erros visuais (layout quebrado)
9. [ ] Touch targets são confortáveis
10. [ ] Performance é fluída (sem lags)

---

## 3. Suite de Testes Automatizada

### 3.1 Estrutura de Testes

```
tests/
├── unit/
│   ├── components/
│   │   ├── mobile-header.test.tsx
│   │   ├── tracker-card.test.tsx
│   │   ├── donut-chart.test.tsx
│   │   └── ...
│   ├── hooks/
│   │   ├── use-auth.test.ts
│   │   └── ...
│   └── utils/
│       ├── format-currency.test.ts
│       └── ...
│
├── integration/
│   ├── dashboard-flow.spec.ts
│   ├── budget-flow.spec.ts
│   └── upload-flow.spec.ts
│
├── e2e/
│   ├── sprint1-dashboard.spec.ts
│   ├── sprint1-profile.spec.ts
│   ├── sprint2-budget-view.spec.ts
│   ├── sprint2-budget-edit.spec.ts
│   ├── sprint2-upload.spec.ts
│   └── sprint3-transactions.spec.ts
│
├── a11y/
│   └── mobile-accessibility.spec.ts
│
└── fixtures/
    ├── extrato_itau.pdf
    ├── user_test.json
    └── ...
```

---

### 3.2 Scripts de Teste

**package.json:**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:a11y": "playwright test tests/a11y",
    "test:sprint1": "playwright test --grep 'Sprint 1'",
    "test:sprint2": "playwright test --grep 'Sprint 2'",
    "test:regression": "playwright test tests/e2e/sprint*.spec.ts"
  }
}
```

---

### 3.3 CI/CD Pipeline

**GitHub Actions:**
```yaml
# .github/workflows/ci.yml

name: CI Pipeline

on:
  pull_request:
    branches: [main, feature/mobile-v1]
  push:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
  
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
```

---

## 4. Definição de Pronto (Definition of Done)

### 4.1 Cada Task

- [ ] Código implementado
- [ ] Testes unitários passando (se aplicável)
- [ ] Sem erros de TypeScript
- [ ] Sem warnings no console
- [ ] Code review aprovado

---

### 4.2 Cada Sprint

- [ ] Todos os testes de regressão passando
- [ ] Testes funcionais do sprint passando
- [ ] Smoke tests manuais validados
- [ ] Desktop não quebrou (validação manual)
- [ ] Deploy em ambiente de staging OK

---

### 4.3 Release V1.0

- [ ] Todos os sprints completos (0-4)
- [ ] Suite completa de E2E passando
- [ ] Lighthouse score ≥ 90 (mobile)
- [ ] Acessibilidade WCAG AA (0 erros críticos)
- [ ] Testes em 5 dispositivos reais OK
- [ ] Performance validada (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Documentação atualizada
- [ ] Aprovação do stakeholder

---

## 5. Rollback Strategy

### 5.1 Se Sprint Falha

**Sintomas:**
- Mais de 50% dos testes de regressão falham
- Bugs críticos encontrados
- Performance degrada significativamente

**Ação:**
1. [ ] Reverter branch: `git revert HEAD~1`
2. [ ] Investigar causa raiz
3. [ ] Corrigir em nova branch
4. [ ] Re-testar suite completa
5. [ ] Merge novamente

---

### 5.2 Se Deploy Falha

**Sintomas:**
- Erros em produção
- Usuários reportam bugs críticos
- Métricas de performance caem

**Ação:**
1. [ ] Rollback imediato: `git revert <commit>` + deploy
2. [ ] Notificar stakeholders
3. [ ] Investigar causa raiz em staging
4. [ ] Hotfix em nova branch
5. [ ] Re-deploy após validação

---

**Fim da Testing Strategy**

**Data:** 31/01/2026  
**Status:** ✅ Completo  
**Próxima revisão:** Após cada sprint
