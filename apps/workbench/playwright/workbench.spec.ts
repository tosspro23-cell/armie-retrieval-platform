import { expect, test } from '@playwright/test';

const query = 'Find healthcare experts with Azure AI experience';

test('Audit exposes real planner, dense, and fusion details', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Retrieval profile').selectOption('H3');
  await page.getByRole('button', { name: 'Run retrieval' }).click();
  const planner = page.locator('.audit-stage').filter({ has: page.locator('summary span').filter({ hasText: 'planner' }) });
  await expect(planner).toContainText(/rule/i);
  await expect(planner).toContainText('hybrid');
  await planner.locator('summary').first().click();
  await expect(planner).toContainText('retrievers');
  await page.locator('.audit-stage').filter({ has: page.locator('summary span').filter({ hasText: 'dense' }) }).locator('summary').first().click();
  const dense = page.locator('.audit-stage').filter({ has: page.locator('summary span').filter({ hasText: 'dense' }) });
  await expect(dense).not.toContainText('{\n}');
  const fusion = page.locator('.audit-stage').filter({ has: page.locator('summary span').filter({ hasText: 'fusion' }) });
  await fusion.locator('summary').first().click();
  await expect(fusion).toContainText('reciprocal_rank_fusion');
});

test('Evidence follows canonical result selection', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Run retrieval' }).click();
  const results = page.locator('article.result');
  await results.nth(0).click();
  await expect(page.getByRole('heading', { name: /Selected result:/ })).toContainText('expert-');
  await expect(page.getByText('Evidence is projected from the retrieval trace')).toBeVisible();
  const firstHeading = await page.getByRole('heading', { name: /Selected result:/ }).textContent();
  await results.nth(1).click();
  await expect(page.getByRole('heading', { name: /Selected result:/ })).not.toHaveText(firstHeading || '');
});

test('Verification renders findings, not only the summary badge', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Run retrieval' }).click();
  await page.getByRole('button', { name: 'Verification' }).click();
  await expect(page.locator('.finding').first()).toBeVisible();
  await expect(page.locator('.finding').first()).toContainText('Expected:');
});

test('Model-enhanced summary and metrics expose execution context', async ({ page }) => {
  test.setTimeout(45_000);
  await page.goto('/');
  await page.locator('select').first().selectOption('model-enhanced');
  await page.getByRole('button', { name: 'Run retrieval' }).click();
  await expect(page.getByRole('button', { name: 'Run retrieval' })).toBeEnabled({ timeout: 30_000 });
  await expect(page.getByText(/Planner: ollama/).last()).toBeVisible();
  await expect(page.getByText(/reranker: bge_cross_encoder/).last()).toBeVisible();
  await expect(page.locator('article.result')).toHaveCount(5);
  await expect(page.getByText('Advanced Execution Details')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Metrics' })).toBeVisible();
});
