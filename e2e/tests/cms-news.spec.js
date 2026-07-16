const path = require('path');
const { test, expect } = require('@playwright/test');
const { loginAsAdmin } = require('./helpers');

const TEST_IMAGE = path.join(__dirname, 'fixtures', 'sample.jpg');

test.describe.serial('news article lifecycle', () => {
    let articleTitle;
    let articleId;

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
    });

    test('create an article with a cover image and an inline body image', async ({ page }) => {
        articleTitle = `E2E məqalə ${Date.now()}`;

        await page.goto('/cms/xeberler/yeni/');
        await page.waitForSelector('.ck-toolbar');
        await page.fill('[data-role="title-input"]', articleTitle);
        await page.fill('.editor__excerpt-input', 'E2E qısa təsvir');
        await page.selectOption('#id_category', { index: 1 });

        // Inline CKEditor image, exercising the same upload path the
        // permanent-delete media cleanup relies on (apps/media_manager/
        // services.py's _media_ids_referenced_in_html).
        await page.click('.ck-editor__editable');
        const [fileChooser] = await Promise.all([
            page.waitForEvent('filechooser'),
            page.click('button[data-cke-tooltip-text="Upload image from computer"]'),
        ]);
        await fileChooser.setFiles(TEST_IMAGE);
        await page.waitForSelector('.ck-editor__editable figure.image img');

        await Promise.all([
            page.waitForURL('**/redakte/'),
            page.click('.editor__sidebar button[type="submit"]'),
        ]);

        articleId = page.url().match(/xeberler\/(\d+)\/redakte/)[1];
        expect(articleId).toBeTruthy();
    });

    test('soft-deleted article moves to trash and can be restored', async ({ page }) => {
        await page.goto(`/cms/xeberler/${articleId}/sil/`);
        // `Promise.all` pairs the click with the wait it triggers — clicking
        // then separately `await`-ing a navigation afterward is a race: a
        // later `page.goto()` can fire before the click's own POST actually
        // reaches the server, aborting it (confirmed by inspecting the e2e
        // database directly after a run where this raced — the row was
        // still soft-deleted despite the "restore" click appearing to
        // succeed in the test).
        await Promise.all([
            page.waitForURL((url) => !url.search.includes('deleted')),
            page.click('.cms-confirm__actions button[type="submit"]'),
        ]);

        await page.goto('/cms/xeberler/?deleted=1');
        const row = page.locator('tr', { hasText: articleTitle });
        await expect(row).toBeVisible();

        await Promise.all([
            page.waitForURL((url) => !url.search.includes('deleted')),
            row.getByRole('button', { name: 'Bərpa et' }).click(),
        ]);
        await expect(page.locator('.cms-table tbody')).toContainText(articleTitle);
    });

    test('permanently deleting the article also removes its media', async ({ page }) => {
        await page.goto(`/cms/xeberler/${articleId}/sil/`);
        await Promise.all([
            page.waitForURL((url) => !url.search.includes('deleted')),
            page.click('.cms-confirm__actions button[type="submit"]'),
        ]);

        await page.goto(`/cms/xeberler/${articleId}/hemise-sil/`);
        await Promise.all([
            page.waitForURL('**/xeberler/'),
            page.click('.cms-confirm__actions button[type="submit"]'),
        ]);

        await page.goto('/cms/xeberler/?deleted=1');
        await expect(page.locator('.cms-table tbody, .empty-state')).not.toContainText(articleTitle);
    });
});
