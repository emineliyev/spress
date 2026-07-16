// Credentials match apps/core/management/commands/bootstrap_e2e_db.py.
const ADMIN_USERNAME = 'e2e_admin';
const ADMIN_PASSWORD = 'E2E-test-password-123';

async function loginAsAdmin(page) {
    await page.goto('/accounts/login/');
    await page.fill('#id_username', ADMIN_USERNAME);
    await page.fill('#id_password', ADMIN_PASSWORD);
    await page.click('.login-page__form button[type="submit"]');
    await page.waitForURL('**/cms/');
}

/**
 * Creates a published article through the real CMS form (not a shortcut
 * around it) and returns its detail-page URL. Assumes the caller is
 * already logged in as an administrator.
 */
async function createPublishedArticle(page, { title, breaking = false } = {}) {
    const articleTitle = title || `E2E xəbər ${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

    await page.goto('/cms/xeberler/yeni/');
    await page.waitForSelector('.ck-toolbar');
    await page.fill('[data-role="title-input"]', articleTitle);
    await page.fill('.editor__excerpt-input', 'E2E qısa təsvir');
    await page.selectOption('#id_category', { index: 1 });
    await page.selectOption('#id_status', 'published');
    if (breaking) {
        await page.check('#id_is_breaking');
    }
    await page.click('.editor__sidebar button[type="submit"]');
    await page.waitForURL('**/redakte/');

    return { title: articleTitle, editUrl: page.url() };
}

module.exports = { loginAsAdmin, createPublishedArticle, ADMIN_USERNAME, ADMIN_PASSWORD };
