// @ts-check
const path = require('path');
const { defineConfig, devices } = require('@playwright/test');
const { resolvePythonBin } = require('./python-bin');

const projectRoot = path.resolve(__dirname, '..');
const pythonBin = resolvePythonBin(projectRoot);

const PORT = 8811;
const BASE_URL = `http://127.0.0.1:${PORT}`;

module.exports = defineConfig({
    testDir: './tests',
    fullyParallel: false, // shares one seeded database — parallel runs would race each other's writes
    workers: 1, // same reason, across spec files too — one shared e2e database/server, not one per worker
    retries: process.env.CI ? 1 : 0,
    reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
    globalSetup: require.resolve('./global-setup.js'),
    use: {
        baseURL: BASE_URL,
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
    },
    projects: [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    ],
    webServer: {
        command: `${pythonBin} manage.py runserver ${PORT} --noreload`,
        cwd: projectRoot,
        url: BASE_URL,
        reuseExistingServer: false,
        env: { ...process.env, DJANGO_SETTINGS_MODULE: 'config.settings.e2e' },
        timeout: 30_000,
    },
});
