/**
 * E2E Test: Authentication Flow
 * Sprint 4 - Mobile V1.0
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication - Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
  });

  test('deve exibir formulário de login', async ({ page }) => {
    // Verificar elementos da página
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('deve mostrar erro com credenciais inválidas', async ({ page }) => {
    // Preencher com credenciais inválidas
    await page.fill('input[type="email"]', 'invalido@teste.com');
    await page.fill('input[type="password"]', 'senhaerrada');
    
    // Tentar login
    await page.click('button[type="submit"]');
    
    // Verificar mensagem de erro
    await expect(page.locator('.text-red-600, .bg-red-50')).toBeVisible();
  });

  test('deve fazer login com sucesso e redirecionar', async ({ page }) => {
    // Preencher credenciais válidas
    await page.fill('input[type="email"]', 'admin@financas.com');
    await page.fill('input[type="password"]', 'admin123');
    
    // Fazer login
    await page.click('button[type="submit"]');
    
    // Verificar redirecionamento
    await page.waitForURL(/\/mobile\/dashboard/, { timeout: 5000 });
    await expect(page).toHaveURL(/\/mobile\/dashboard/);
  });

  test('deve persistir token após login', async ({ page, context }) => {
    // Login
    await page.fill('input[type="email"]', 'admin@financas.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/mobile\/dashboard/);
    
    // Verificar localStorage
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();
    expect(token).toMatch(/^[\w-]+\.[\w-]+\.[\w-]+$/); // JWT format
  });
});

test.describe('Authentication - Logout Flow', () => {
  test('deve fazer logout e redirecionar para login', async ({ page }) => {
    // Login primeiro
    await page.goto('/auth/login');
    await page.fill('input[type="email"]', 'admin@financas.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/mobile\/dashboard/);
    
    // Navegar para profile
    await page.click('a[href="/mobile/profile"]');
    await page.waitForLoadState('networkidle');
    
    // Fazer logout
    await page.click('button:has-text("Sair da Conta")');
    
    // Verificar redirecionamento
    await page.waitForURL(/\/auth\/login/);
    
    // Verificar token removido
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeNull();
  });
});

test.describe('Authentication - Protected Routes', () => {
  test('deve redirecionar para login se não autenticado', async ({ page }) => {
    // Limpar storage
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    
    // Tentar acessar rota protegida
    await page.goto('/mobile/dashboard');
    
    // Deve redirecionar para login
    await page.waitForURL(/\/auth\/login/, { timeout: 5000 });
  });
});
