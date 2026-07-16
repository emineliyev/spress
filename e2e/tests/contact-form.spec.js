const { test, expect } = require('@playwright/test');

test('empty submission shows Azerbaijani required-field errors', async ({ page }) => {
    await page.goto('/contacts/');
    await page.click('.contact-page__form button[type="submit"]');
    await expect(page.locator('.contact-page__form')).toContainText('Bu sahənin doldurulması mütləqdir.');
});

test('invalid email shows an Azerbaijani error message', async ({ page }) => {
    await page.goto('/contacts/');
    await page.fill('#id_name', 'Test İstifadəçi');
    await page.fill('#id_email', 'not-an-email');
    await page.fill('#id_subject', 'Test mövzu');
    await page.fill('#id_message', 'Test mesajı');
    await page.click('.contact-page__form button[type="submit"]');
    await expect(page.locator('.contact-page__form')).toContainText('Düzgün e-poçt ünvanı daxil edin.');
});

test('valid submission succeeds', async ({ page }) => {
    await page.goto('/contacts/');
    await page.fill('#id_name', 'Test İstifadəçi');
    await page.fill('#id_email', 'test@example.com');
    await page.fill('#id_subject', 'Test mövzu');
    await page.fill('#id_message', 'Test mesajı');
    await page.click('.contact-page__form button[type="submit"]');
    await expect(page.locator('.alert--success, .toast')).toContainText(/göndərildi/i);
});
