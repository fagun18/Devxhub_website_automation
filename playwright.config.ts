import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 120000,
  expect: { timeout: 15000 },
  fullyParallel: false,
  reporter: [
    ['list'],
    ['html', { 
      outputFolder: 'playwright-report', 
      open: 'never',
      attachments: 'on'
    }]
  ],
  use: {
    baseURL: 'https://devxhub.com',
    headless: true,
    viewport: { width: 1280, height: 800 },
    ignoreHTTPSErrors: true,
    actionTimeout: 30000,
    navigationTimeout: 90000
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
});


