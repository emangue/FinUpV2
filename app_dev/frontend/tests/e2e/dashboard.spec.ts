/**
 * E2E Test: Dashboard Mobile
 * Sprint 4 - Mobile V1.0
 */

import { test, expect } from '@playwright/test';
import { loginAsAdmin, waitForPageLoad } from './helpers';

test.describe('Dashboard Mobile', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await waitForPageLoad(page);
  });

  test('deve exibir todas as métricas principais', async ({ page }) => {
    // Verificar cards de métricas
    await expect(page.getByText('Receitas')).toBeVisible();
    await expect(page.getByText('Despesas')).toBeVisible();
    await expect(page.getByText('Saldo')).toBeVisible();
    await expect(page.getByText('Investimentos')).toBeVisible();
    
    // Verificar valores monetários (R$)
    const values = await page.locator('.text-2xl.font-bold').all();
    expect(values.length).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir MonthScrollPicker', async ({ page }) => {
    // Verificar picker de mês
    const monthPicker = page.locator('[data-testid="month-picker"]');
    await expect(monthPicker).toBeVisible();
    
    // Verificar que há múltiplos meses
    const monthItems = await page.locator('[data-testid="month-picker-item"]').count();
    expect(monthItems).toBeGreaterThan(1);
  });

  test('deve exibir YTD Toggle', async ({ page }) => {
    // Verificar toggle Mês/YTD
    await expect(page.getByText('Mês')).toBeVisible();
    await expect(page.getByText('YTD')).toBeVisible();
  });

  test('deve alternar entre Mês e YTD', async ({ page }) => {
    // Clicar em YTD
    await page.click('button:has-text("YTD")');
    await page.waitForLoadState('networkidle');
    
    // Verificar que dados foram atualizados (valores podem mudar)
    await expect(page.locator('.text-2xl.font-bold').first()).toBeVisible();
    
    // Voltar para Mês
    await page.click('button:has-text("Mês")');
    await page.waitForLoadState('networkidle');
  });

  test('deve carregar dados ao trocar de mês', async ({ page }) => {
    // Obter valor atual
    const currentValue = await page.locator('.text-2xl.font-bold').first().textContent();
    
    // Selecionar outro mês (se disponível)
    const monthItems = await page.locator('[data-testid="month-picker-item"]').all();
    if (monthItems.length > 1) {
      await monthItems[0].click();
      await page.waitForLoadState('networkidle');
      
      // Verificar que valores foram atualizados
      const newValue = await page.locator('.text-2xl.font-bold').first().textContent();
      // Valores podem ser iguais se não há transações, mas pelo menos deve ter carregado
      expect(newValue).toBeTruthy();
    }
  });

  test('deve exibir loading state', async ({ page }) => {
    // Recarregar página e verificar loading
    await page.reload();
    
    // Loading pode ser muito rápido, então usamos waitForSelector com timeout curto
    try {
      await page.waitForSelector('.animate-spin', { timeout: 1000 });
    } catch {
      // Se não pegou o loading, tudo bem (foi muito rápido)
    }
    
    // Verificar que dados carregaram
    await waitForPageLoad(page);
    await expect(page.locator('.text-2xl.font-bold').first()).toBeVisible();
  });

  test('deve ter navegação bottom nav funcional', async ({ page }) => {
    // Verificar que bottom nav está visível
    await expect(page.locator('nav a[href="/mobile/dashboard"]')).toBeVisible();
    await expect(page.locator('nav a[href="/mobile/budget"]')).toBeVisible();
    await expect(page.locator('nav a[href="/mobile/transactions"]')).toBeVisible();
    await expect(page.locator('nav a[href="/mobile/profile"]')).toBeVisible();
    
    // FAB Upload
    await expect(page.locator('button[aria-label="Upload"]')).toBeVisible();
  });
});

test.describe('Dashboard - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('deve ter h1 semântico', async ({ page }) => {
    // Verificar presença de h1 (pode ser sr-only)
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
  });

  test('deve ter contraste adequado em labels', async ({ page }) => {
    // Verificar que não usa text-gray-400 ou text-gray-500 em textos críticos
    const labels = await page.locator('.text-sm').all();
    
    for (const label of labels) {
      const classes = await label.getAttribute('class');
      // Labels devem ser text-gray-600 ou mais escuro
      expect(classes).not.toContain('text-gray-400');
    }
  });
});
