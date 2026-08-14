import { test, expect } from '@playwright/test';

test.describe('Gate 7C live Workbench to C1 integration', () => {
  test.beforeEach(async ({ page }) => { await page.goto('/'); });

  async function enableC1(page: any) {
    await page.getByLabel('Structured contract mode').check();
  }

  test('free query remains C0/H2 Dense', async ({ page }) => {
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Dense (C0)');
    await expect(page.locator('.result').first()).toContainText('Dense score');
    await expect(page.locator('body')).toContainText('Manufacturing');
  });

  test('years constraint reaches live C1', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Years experience minimum').fill('10');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Constraint-aware Dense (C1)');
    await expect(page.locator('body')).toContainText('Contract summary · VALID', { timeout: 120000 });
    await expect(page.locator('body')).toContainText('constraint_prefilter', { timeout: 120000 });
    await expect(page.locator('.result')).toHaveCount(5, { timeout: 120000 });
    await expect(page.locator('.constraint-evidence')).toHaveCount(5, { timeout: 120000 });
    await expect(page.locator('.constraint-evidence').first()).toContainText('Years experience:');
  });

  test('registry-backed Healthcare filter makes industry an eligibility requirement', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Required industry').selectOption('healthcare');
    await expect(page.getByLabel('Required industry')).toHaveValue('healthcare');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Required: Industry: Healthcare');
    await expect(page.locator('.result')).toHaveCount(0);
    await expect(page.locator('body')).toContainText('Strict shortfall');
  });

  test('higher years threshold preserves strict Top-K and exposes candidate facts', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Years experience minimum').fill('25');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Contract summary · VALID', { timeout: 120000 });
    const resultCount = await page.locator('.result').count();
    expect(resultCount).toBeLessThanOrEqual(5);
    await expect(page.locator('.constraint-evidence').first()).toContainText('Years experience:');
  });

  test('seniority and multi-constraint conjunction reach C1', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Required industry').selectOption('manufacturing');
    await page.getByLabel('Years experience minimum').fill('10');
    await page.getByLabel('Required seniority').selectOption('senior');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Constraint-aware Dense (C1)');
    await expect(page.locator('body')).toContainText('industry');
    await expect(page.locator('body')).toContainText('seniority');
    await expect(page.locator('.constraint-evidence').first()).toContainText('Seniority');
  });

  test('explicit exclusion is visible and enforced by C1', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Excluded industry').selectOption('manufacturing');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Exclude industry: Manufacturing');
    await expect(page.locator('body')).toContainText('Contract summary · VALID');
    await expect(page.locator('.constraint-evidence').first()).toContainText('must not match');
  });

  test('unsupported deferred constraint is explicit and does not fall back', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Constraint scenario').selectOption('unsupported');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Contract summary · UNSUPPORTED_CONSTRAINT');
    await expect(page.locator('body')).toContainText('retrieval was not executed');
    await expect(page.locator('body')).not.toContainText('Dense (C0)');
  });

  test('strict shortfall is rendered without ineligible backfill', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Years experience minimum').fill('1000');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('returned 0 of 5 requested');
    await expect(page.locator('body')).toContainText('Strict shortfall');
  });

  test('C1 provenance is rendered in the execution trace', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Required industry').selectOption('healthcare');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await page.getByRole('button', { name: 'Raw Trace' }).click();
    await expect(page.locator('body')).toContainText('constraint_prefilter');
    await expect(page.locator('body')).toContainText('index_compatibility');
    await expect(page.locator('body')).toContainText('filter_applied');
  });
});
