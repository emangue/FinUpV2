/**
 * Helpers para testes E2E - FinUp Mobile V1.0
 * Sprint 4
 */

import { Page, expect } from '@playwright/test';

/**
 * Realiza login no sistema
 */
export async function loginAsAdmin(page: Page) {
  await page.goto('/auth/login');
  
  // Preencher credenciais
  await page.fill('input[type="email"]', 'admin@financas.com');
  await page.fill('input[type="password"]', 'admin123');
  
  // Clicar no botão de login
  await page.click('button[type="submit"]');
  
  // Aguardar redirecionamento
  await page.waitForURL('/mobile/dashboard');
}

/**
 * Verifica se está em tela mobile
 */
export async function isMobileView(page: Page): Promise<boolean> {
  const viewportSize = page.viewportSize();
  return viewportSize ? viewportSize.width < 768 : false;
}

/**
 * Navega usando bottom navigation
 */
export async function navigateBottomNav(page: Page, tab: 'dashboard' | 'budget' | 'transactions' | 'upload' | 'profile') {
  const selectors = {
    dashboard: 'nav a[href="/mobile/dashboard"]',
    budget: 'nav a[href="/mobile/budget"]',
    transactions: 'nav a[href="/mobile/transactions"]',
    upload: 'button[aria-label="Upload"]', // FAB central
    profile: 'nav a[href="/mobile/profile"]',
  };
  
  await page.click(selectors[tab]);
  await page.waitForLoadState('networkidle');
}

/**
 * Aguarda carregamento completo da página
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForSelector('[role="progressbar"]', { state: 'hidden', timeout: 5000 }).catch(() => {});
}

/**
 * Formata valor monetário para input
 */
export function formatCurrencyInput(value: number): string {
  return value.toFixed(2).replace('.', ',');
}

/**
 * Verifica se elemento está visível
 */
export async function isVisible(page: Page, selector: string): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Aguarda por toast de sucesso
 */
export async function waitForSuccessToast(page: Page, message?: string) {
  const toastSelector = '.bg-green-50, [role="alert"]';
  await page.waitForSelector(toastSelector, { timeout: 3000 });
  
  if (message) {
    await expect(page.locator(toastSelector)).toContainText(message);
  }
}

/**
 * Simula scroll para baixo
 */
export async function scrollDown(page: Page, distance: number = 300) {
  await page.evaluate((scrollDistance) => {
    window.scrollBy(0, scrollDistance);
  }, distance);
  await page.waitForTimeout(300);
}

/**
 * Verifica touch target mínimo (WCAG 2.5.5)
 */
export async function verifyTouchTarget(page: Page, selector: string) {
  const element = await page.locator(selector);
  const box = await element.boundingBox();
  
  expect(box).not.toBeNull();
  if (box) {
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.height).toBeGreaterThanOrEqual(44);
  }
}

/**
 * Seleciona mês no MonthScrollPicker
 */
export async function selectMonth(page: Page, monthOffset: number = 0) {
  // Offset: 0 = mês atual, -1 = mês anterior, 1 = próximo mês
  const months = await page.locator('[data-testid="month-picker-item"]').all();
  
  if (months.length > 0) {
    const targetIndex = Math.max(0, Math.min(months.length - 1, monthOffset + 1));
    await months[targetIndex].click();
    await page.waitForTimeout(500);
  }
}
