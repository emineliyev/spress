const { test, expect } = require('@playwright/test');

// A plain narrow viewport, not `devices['iPhone 13']` — that preset also
// carries `defaultBrowserType: 'webkit'`, which this project doesn't
// install (only chromium, per playwright.config.js). The mobile nav
// behavior under test is a pure CSS breakpoint (≤768px), so viewport
// width is all that actually matters here.
test.use({ viewport: { width: 390, height: 844 } });

test('mobile menu opens, shows social links, and closes on Escape', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('.site-header__social')).toBeHidden();

    await page.click('[data-action="toggle-menu"]');
    const nav = page.locator('.nav');
    await expect(nav).toHaveClass(/is-open/);
    await expect(page.locator('.nav__social')).toBeVisible();
    await expect(page.locator('.nav__social-link')).toHaveCount(1); // one social link seeded

    await page.keyboard.press('Escape');
    await expect(nav).not.toHaveClass(/is-open/);
});
