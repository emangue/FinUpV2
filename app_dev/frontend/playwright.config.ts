import { defineConfig, devices } from '@playwright/test';

/**
 * Configuração Playwright - FinUp Mobile V1.0
 * Sprint 4 - E2E Testing
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  /* Configuração de timeout */
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },

  /* Execução */
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  /* Reporter */
  reporter: [
    ['html'],
    ['list']
  ],

  /* Configuração global */
  use: {
    /* URL base */
    baseURL: 'http://localhost:3000',

    /* Trace on fail */
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  /* Projetos de teste */
  projects: [
    /* Mobile iOS Safari */
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 13 Pro'],
        viewport: { width: 390, height: 844 },
      },
    },

    /* Mobile Android Chrome */
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 393, height: 851 },
      },
    },

    /* Desktop para comparação */
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* Web Server */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
