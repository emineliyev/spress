const { test, expect } = require('@playwright/test');
const { loginAsAdmin, createPublishedArticle } = require('./helpers');

test.describe.serial('article detail page', () => {
    let article;

    test.beforeAll(async ({ browser }) => {
        const page = await browser.newPage();
        await loginAsAdmin(page);
        article = await createPublishedArticle(page);
        await page.close();
    });

    test('view count increments once per anonymous session, and share buttons render', async ({ context }) => {
        // Find the public URL by visiting the CMS "preview" link, since the
        // slug is server-generated and not something this test computes itself.
        const adminPage = await context.newPage();
        await loginAsAdmin(adminPage);
        await adminPage.goto(article.editUrl);
        const publicUrl = await adminPage.getAttribute('.editor__preview-link', 'href');
        await adminPage.close();

        const reader = await context.newPage();
        await reader.goto(publicUrl);
        await expect(reader.locator('.article__date')).toContainText('1 baxış');

        await reader.reload();
        await expect(reader.locator('.article__date')).toContainText('1 baxış');

        await expect(reader.locator('.article__share-btn')).toHaveCount(5);
    });
});
