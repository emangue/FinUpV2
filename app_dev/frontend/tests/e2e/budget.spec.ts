/**
 * E2E Test: Budget Mobile
 * Sprint 4 - Mobile V1.0
 */

import { test, expect } from '@playwright/test';
import { loginAsAdmin, waitForPageLoad, navigateBottomNav, waitForSuccessToast } from './helpers';

test.describe('Budget Mobile - Visualização', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'budget');
    await waitForPageLoad(page);
  });

  test('deve exibir lista de categorias com metas', async ({ page }) => {
    // Verificar trackers de categoria
    const trackers = await page.locator('[data-testid="tracker-card"]').count();
    expect(trackers).toBeGreaterThan(0);
  });

  test('deve exibir progresso em cada categoria', async ({ page }) => {
    // Verificar barras de progresso
    const progressBars = await page.locator('[role="progressbar"]').all();
    expect(progressBars.length).toBeGreaterThan(0);
    
    for (const bar of progressBars) {
      await expect(bar).toBeVisible();
    }
  });

  test('deve exibir valores atualizados', async ({ page }) => {
    // Verificar valores monetários
    const amounts = await page.getByText(/R\$ \d+/).all();
    expect(amounts.length).toBeGreaterThan(0);
  });
});

test.describe('Budget Mobile - Edição Individual', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'budget');
    await waitForPageLoad(page);
  });

  test('deve abrir bottom sheet ao clicar em categoria', async ({ page }) => {
    // Clicar no primeiro tracker
    const firstTracker = page.locator('[data-testid="tracker-card"]').first();
    await firstTracker.click();
    
    // Verificar bottom sheet aberto
    await expect(page.getByText('Editar Meta')).toBeVisible();
    await expect(page.locator('input[type="number"]')).toBeVisible();
  });

  test('deve permitir editar valor', async ({ page }) => {
    // Abrir bottom sheet
    await page.locator('[data-testid="tracker-card"]').first().click();
    await page.waitForSelector('input[type="number"]');
    
    // Limpar e digitar novo valor
    const input = page.locator('input[type="number"]');
    await input.clear();
    await input.fill('1500');
    
    // Verificar valor
    await expect(input).toHaveValue('1500');
  });

  test('deve salvar alteração com sucesso', async ({ page }) => {
    // Abrir bottom sheet
    await page.locator('[data-testid="tracker-card"]').first().click();
    
    // Editar valor
    const input = page.locator('input[type="number"]');
    await input.clear();
    await input.fill('2000');
    
    // Salvar
    await page.click('button:has-text("Salvar")');
    
    // Verificar toast de sucesso
    await waitForSuccessToast(page);
    
    // Bottom sheet deve fechar
    await expect(page.getByText('Editar Meta')).not.toBeVisible();
  });

  test('deve cancelar edição', async ({ page }) => {
    // Abrir bottom sheet
    await page.locator('[data-testid="tracker-card"]').first().click();
    
    // Editar valor
    const input = page.locator('input[type="number"]');
    const originalValue = await input.inputValue();
    await input.clear();
    await input.fill('9999');
    
    // Cancelar
    await page.click('button:has-text("Cancelar")');
    
    // Bottom sheet deve fechar
    await expect(page.getByText('Editar Meta')).not.toBeVisible();
  });
});

test.describe('Budget Mobile - Edição em Massa', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'budget');
    await waitForPageLoad(page);
  });

  test('deve navegar para página de edição em massa', async ({ page }) => {
    // Clicar no botão Editar Tudo
    await page.click('button:has-text("Editar Tudo"), [aria-label*="Editar"]');
    
    // Verificar navegação
    await page.waitForURL(/\/mobile\/budget\/edit/);
    expect(page.url()).toContain('/mobile/budget/edit');
  });

  test('deve exibir todos os inputs de categorias', async ({ page }) => {
    // Ir para edição em massa
    await page.click('button:has-text("Editar Tudo"), [aria-label*="Editar"]');
    await page.waitForLoadState('networkidle');
    
    // Verificar múltiplos inputs
    const inputs = await page.locator('input[type="number"]').count();
    expect(inputs).toBeGreaterThan(3); // Pelo menos 4 categorias
  });

  test('deve permitir editar múltiplas categorias', async ({ page }) => {
    // Ir para edição em massa
    await page.click('button:has-text("Editar Tudo"), [aria-label*="Editar"]');
    await page.waitForLoadState('networkidle');
    
    // Editar primeira categoria
    const inputs = await page.locator('input[type="number"]').all();
    if (inputs.length >= 2) {
      await inputs[0].clear();
      await inputs[0].fill('1000');
      
      await inputs[1].clear();
      await inputs[1].fill('2000');
      
      // Verificar valores
      await expect(inputs[0]).toHaveValue('1000');
      await expect(inputs[1]).toHaveValue('2000');
    }
  });

  test('deve salvar todas as alterações', async ({ page }) => {
    // Ir para edição em massa
    await page.click('button:has-text("Editar Tudo"), [aria-label*="Editar"]');
    await page.waitForLoadState('networkidle');
    
    // Editar valores
    const inputs = await page.locator('input[type="number"]').all();
    if (inputs.length > 0) {
      await inputs[0].clear();
      await inputs[0].fill('5000');
    }
    
    // Salvar
    await page.click('button:has-text("Salvar Tudo")');
    
    // Verificar toast ou redirecionamento
    await page.waitForTimeout(1000);
    
    // Deve voltar para lista
    await page.waitForURL(/\/mobile\/budget$/);
  });
});

test.describe('Budget - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'budget');
  });

  test('inputs devem ter labels acessíveis', async ({ page }) => {
    // Ir para edição em massa
    await page.click('button:has-text("Editar Tudo"), [aria-label*="Editar"]');
    await page.waitForLoadState('networkidle');
    
    // Verificar inputs com ID e label
    const inputs = await page.locator('input[type="number"]').all();
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      
      // Deve ter ID ou aria-label
      expect(id || ariaLabel).toBeTruthy();
    }
  });
});
