const { test, expect } = require('@playwright/test');
const { loginAsAdmin } = require('./helpers');

test('CMS root redirects an anonymous visitor to login', async ({ page }) => {
    const response = await page.goto('/cms/');
    expect(response.request().url()).toContain('/accounts/login/');
});

test('correct credentials reach the CMS dashboard', async ({ page }) => {
    await loginAsAdmin(page);
    await expect(page).toHaveURL(/\/cms\/$/);
});

test('repeated wrong passwords lock the account out', async ({ page }) => {
    // A username that isn't a real account — the lockout counter is keyed
    // on (ip, submitted username) regardless of whether it exists
    // (apps/accounts/services.py), so this doesn't touch e2e_admin's own
    // lockout state and can't affect later specs that log in as it.
    const throwawayUsername = 'e2e-lockout-probe';

    await page.goto('/accounts/login/');
    for (let i = 0; i < 5; i++) {
        await page.fill('#id_username', throwawayUsername);
        await page.fill('#id_password', 'wrong-password');
        await page.click('.login-page__form button[type="submit"]');
    }
    // The 6th attempt must be blocked before credentials are even checked.
    await page.fill('#id_username', throwawayUsername);
    await page.fill('#id_password', 'wrong-password');
    await page.click('.login-page__form button[type="submit"]');
    await expect(page.locator('.form-errors, .errorlist, .alert--danger')).toContainText(/cəhd/i);
});
