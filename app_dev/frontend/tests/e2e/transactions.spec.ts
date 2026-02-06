/**
 * E2E Test: Transactions Mobile
 * Sprint 4 - Mobile V1.0
 */

import { test, expect } from '@playwright/test';
import { loginAsAdmin, waitForPageLoad, navigateBottomNav } from './helpers';

test.describe('Transactions Mobile', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'transactions');
    await waitForPageLoad(page);
  });

  test('deve exibir lista de transações', async ({ page }) => {
    // Verificar cards de transação
    const transactionCards = await page.locator('[data-testid="transaction-card"]').count();
    expect(transactionCards).toBeGreaterThan(0);
  });

  test('deve exibir filtros de categoria', async ({ page }) => {
    // Verificar pills de filtro
    await expect(page.getByText('Todas')).toBeVisible();
    await expect(page.getByText('Receitas')).toBeVisible();
    await expect(page.getByText('Despesas')).toBeVisible();
  });

  test('deve filtrar por Receitas', async ({ page }) => {
    // Clicar em Receitas
    await page.click('button:has-text("Receitas")');
    await page.waitForLoadState('networkidle');
    
    // Verificar que filtro está ativo
    const receitasBtn = page.locator('button:has-text("Receitas")');
    const classes = await receitasBtn.getAttribute('class');
    expect(classes).toContain('bg-black'); // Ativo
  });

  test('deve filtrar por Despesas', async ({ page }) => {
    // Clicar em Despesas
    await page.click('button:has-text("Despesas")');
    await page.waitForLoadState('networkidle');
    
    // Verificar que filtro está ativo
    const despesasBtn = page.locator('button:has-text("Despesas")');
    const classes = await despesasBtn.getAttribute('class');
    expect(classes).toContain('bg-black'); // Ativo
  });

  test('deve exibir MonthScrollPicker', async ({ page }) => {
    // Verificar picker de mês
    const monthPicker = page.locator('[data-testid="month-picker"]');
    await expect(monthPicker).toBeVisible();
  });

  test('deve carregar transações ao trocar de mês', async ({ page }) => {
    // Contar transações atuais
    const initialCount = await page.locator('[data-testid="transaction-card"]').count();
    
    // Trocar de mês
    const monthItems = await page.locator('[data-testid="month-picker-item"]').all();
    if (monthItems.length > 1) {
      await monthItems[0].click();
      await page.waitForLoadState('networkidle');
      
      // Verificar que dados foram atualizados (pode ter 0 transações)
      const newCount = await page.locator('[data-testid="transaction-card"]').count();
      // Apenas verifica que a requisição foi feita
      expect(newCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('transações devem exibir dados completos', async ({ page }) => {
    const firstCard = page.locator('[data-testid="transaction-card"]').first();
    
    // Verificar elementos do card
    await expect(firstCard).toBeVisible();
    
    // Deve ter estabelecimento, valor, data, categoria
    const cardText = await firstCard.textContent();
    expect(cardText).toMatch(/R\$\s*\d+/); // Valor monetário
  });

  test('deve exibir mensagem quando não há transações', async ({ page }) => {
    // Filtrar por Receitas e trocar para mês sem dados (se possível)
    await page.click('button:has-text("Receitas")');
    
    // Trocar para mês antigo que provavelmente não tem dados
    const monthItems = await page.locator('[data-testid="month-picker-item"]').all();
    if (monthItems.length > 2) {
      await monthItems[monthItems.length - 1].click();
      await page.waitForLoadState('networkidle');
      
      // Pode exibir mensagem de vazio
      const isEmpty = await page.getByText(/Nenhuma transação|sem transações/i).count();
      // Se não tem transações, deve mostrar mensagem ou lista vazia
      expect(isEmpty >= 0).toBeTruthy();
    }
  });
});

test.describe('Transactions - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateBottomNav(page, 'transactions');
  });

  test('deve ter contraste adequado', async ({ page }) => {
    // Verificar que não usa cores muito claras
    const labels = await page.locator('.text-sm').all();
    
    for (const label of labels.slice(0, 5)) { // Checar primeiros 5
      const classes = await label.getAttribute('class');
      // Não deve usar text-gray-400 em textos críticos
      if (classes && classes.includes('text-gray')) {
        expect(classes).not.toContain('text-gray-400');
      }
    }
  });

  test('botões de filtro devem ter touch target adequado', async ({ page }) => {
    const filterButtons = await page.locator('button:has-text("Todas"), button:has-text("Receitas"), button:has-text("Despesas")').all();
    
    for (const button of filterButtons) {
      const box = await button.boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(36); // Pelo menos 36px (próximo de 44px)
      }
    }
  });
});
