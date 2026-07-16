const path = require('path');

/**
 * Resolves the Python interpreter used to run manage.py for the e2e
 * suite (global-setup.js's DB bootstrap, playwright.config.js's
 * webServer). Defaults to this repo's venv; set PLAYWRIGHT_PYTHON_BIN
 * to override — CI (.github/workflows/ci.yml) has no venv, just the
 * runner's own `python` on PATH.
 */
function resolvePythonBin(projectRoot) {
    if (process.env.PLAYWRIGHT_PYTHON_BIN) {
        return process.env.PLAYWRIGHT_PYTHON_BIN;
    }
    return process.platform === 'win32'
        ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
        : path.join(projectRoot, '.venv', 'bin', 'python');
}

module.exports = { resolvePythonBin };
