const { test, expect } = require('@playwright/test');
const { loginAsAdmin, createPublishedArticle } = require('./helpers');

test.describe.serial('homepage and navigation', () => {
    let article;

    test.beforeAll(async ({ browser }) => {
        const page = await browser.newPage();
        await loginAsAdmin(page);
        article = await createPublishedArticle(page, { breaking: true });
        await page.close();
    });

    test('homepage renders and lists the article', async ({ page }) => {
        const response = await page.goto('/');
        expect(response.status()).toBe(200);
        await expect(page.locator('body')).toContainText(article.title);
    });

    test('breaking ticker shows the article with a lightning icon and links to it', async ({ page }) => {
        await page.goto('/');
        const ticker = page.locator('[data-component="breaking-ticker"]');
        await expect(ticker).toBeVisible();
        await expect(ticker.locator('.breaking-ticker__icon').first()).toBeVisible();
        await expect(ticker.locator('.breaking-ticker__item').first()).toContainText(article.title);
    });

    test('breaking ticker pauses its scroll animation on hover', async ({ page }) => {
        await page.goto('/');
        const track = page.locator('.breaking-ticker__track');
        // force: true — the track is continuously animating (translateX),
        // so Playwright's normal actionability check ("element is stable
        // across two animation frames") never passes; a real user's mouse
        // doesn't need that guarantee to trigger :hover.
        await track.hover({ force: true });
        const playState = await track.evaluate((el) => getComputedStyle(el).animationPlayState);
        expect(playState).toBe('paused');
    });

    test('category link is highlighted as active while browsing that category', async ({ page }) => {
        await page.goto('/');
        const categoryLink = page.locator('.nav__list > .nav__item > .nav__link[href^="/category"]').first();
        const href = await categoryLink.getAttribute('href');
        await page.goto(href);
        await expect(page.locator('.nav__link.is-active')).toContainText(await categoryLink.textContent());
    });
});
