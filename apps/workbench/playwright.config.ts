import { defineConfig, devices } from '@playwright/test';

const founderEnvironment = process.env.PLAYWRIGHT_FOUNDER_ENV === '1';
const backend = process.env.PLAYWRIGHT_BACKEND ?? 'http://127.0.0.1:8782';
const frontend = process.env.PLAYWRIGHT_FRONTEND ?? 'http://127.0.0.1:5177';

export default defineConfig({
  testDir: './',
  fullyParallel: false,
  retries: 0,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL: frontend,
    browserName: 'chromium',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    ...devices['Desktop Chrome'],
  },
  webServer: founderEnvironment ? undefined : [
    {
      command: 'PYTHONPATH=src API_HOST=127.0.0.1 API_PORT=8782 python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8782',
      cwd: '../..',
      url: `${backend}/api/v1/health`,
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: 'VITE_PROXY_TARGET=http://127.0.0.1:8782 UI_PORT=5177 npm run dev -- --host 127.0.0.1 --port 5177',
      cwd: '.',
      url: frontend,
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
