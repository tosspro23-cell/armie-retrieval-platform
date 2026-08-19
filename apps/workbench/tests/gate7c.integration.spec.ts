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
    await expect(page.locator('body')).toContainText(/Financial Services|Manufacturing/);
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

  test('Founder ambiguous query is governed from clarification through confirmed C1', async ({ page }) => {
    await page.getByLabel('Free query').fill('Find healthcare experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Review intent' }).click();
    await expect(page.locator('body')).toContainText('NEEDS CLARIFICATION');
    await expect(page.locator('body')).toContainText('1 clarification requires resolution.');
    await expect(page.locator('.querybar button')).toBeDisabled();
    await expect(page.locator('body')).not.toContainText('No clarification is currently blocking.');

    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await expect(page.locator('body')).toContainText('INTERPRETATION COMPLETE');
    await expect(page.locator('.querybar button')).toBeDisabled();
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await expect(page.locator('body')).toContainText('VALIDATED CONTRACT');
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('body')).toContainText('Constraint-aware Dense (C1)', { timeout: 120000 });
  });

  test('C1 primary Search auto-starts governed interpretation before retrieval', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find healthcare experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('NEEDS CLARIFICATION');
    await expect(page.locator('.result')).toHaveCount(0);
    await expect(page.locator('.querybar button')).toBeDisabled();

    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await expect(page.locator('body')).toContainText('INTERPRETATION COMPLETE');
    await expect(page.locator('.interpretation-panel')).not.toContainText('Execution complete');
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await expect(page.locator('body')).toContainText('VALIDATED CONTRACT');
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('body')).toContainText('Constraint-aware Dense (C1)', { timeout: 120000 });
  });

  test('C1 primary Search governs an unambiguous query and waits for confirmation', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find principal search engineers');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('INTERPRETATION COMPLETE');
    await expect(page.locator('body')).toContainText('Confirmation required before a validated contract.');
    await expect(page.locator('.result')).toHaveCount(0);
  });

  test('confirmed Founder execution populates canonical result panels', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('body')).toContainText('Execution complete: 5 result(s)', { timeout: 120000 });
    await expect(page.locator('.result')).toHaveCount(5, { timeout: 120000 });
    await expect(page.locator('body')).not.toContainText('Run a query to see the deterministic evidence summary.');
    await expect(page.locator('body')).toContainText('constraint_prefilter', { timeout: 120000 });
    await expect(page.locator('body')).toContainText('End-to-end latency');
  });

  test('confirmed zero-result execution renders an executed empty state', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find healthcare experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('body')).toContainText('Execution complete: 0 result(s)', { timeout: 120000 });
    await expect(page.locator('.result')).toHaveCount(0);
    await expect(page.locator('body')).toContainText('returned 0 of 5 requested', { timeout: 120000 });
    await expect(page.locator('body')).not.toContainText('Run a query to see the deterministic evidence summary.');
  });

  test('editing a confirmed clarification retires execution until reconfirmation', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('.result')).toHaveCount(5, { timeout: 120000 });

    await page.getByRole('button', { name: 'MAXIMUM' }).click();
    await expect(page.locator('body')).toContainText('INTERPRETATION COMPLETE');
    await expect(page.locator('body')).toContainText('Confirmation required before a validated contract.');
    await expect(page.locator('.result')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Search with confirmed constraints' })).toHaveCount(0);
  });

  test('a new session clears prior governed execution state', async ({ page }) => {
    await enableC1(page);
    await page.getByLabel('Free query').fill('Find experts with Azure AI experience around 20 years');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await page.getByRole('button', { name: 'MINIMUM' }).click();
    await page.getByRole('button', { name: 'Confirm interpretation' }).click();
    await page.getByRole('button', { name: 'Search with confirmed constraints' }).click();
    await expect(page.locator('.result')).toHaveCount(5, { timeout: 120000 });

    await page.getByRole('button', { name: 'New session' }).click();
    await expect(page.locator('.result')).toHaveCount(0);
    await expect(page.locator('body')).toContainText('Run a query to see the deterministic evidence summary.');
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('NEEDS CLARIFICATION');
    await expect(page.locator('.result')).toHaveCount(0);
  });
});
