const { execFileSync } = require('child_process');
const path = require('path');
const { resolvePythonBin } = require('./python-bin');

/**
 * Runs once before the whole e2e suite (playwright.config.js's
 * `globalSetup`) — creates/migrates/reseeds the dedicated e2e database
 * so every run starts from the same known state, regardless of what a
 * previous run (or a crashed one) left behind.
 */
module.exports = async () => {
    const projectRoot = path.resolve(__dirname, '..');

    execFileSync(resolvePythonBin(projectRoot), ['manage.py', 'bootstrap_e2e_db'], {
        cwd: projectRoot,
        stdio: 'inherit',
        env: { ...process.env, DJANGO_SETTINGS_MODULE: 'config.settings.e2e' },
    });
};
