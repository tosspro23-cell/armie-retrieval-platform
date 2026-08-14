import { test, expect } from '@playwright/test';

const api = process.env.ARMIE_WORKBENCH_API_URL || process.env.ARMIE_WORKBENCH_URL || 'http://127.0.0.1:8782';

test.describe('Gate 6 relevance experiment workbench', () => {
  test.beforeEach(async ({ page }) => { await page.goto('/'); });

  test('H1-H4 selector is backed by profile metadata', async ({ request }) => {
    const response = await request.get(`${api}/api/v1/benchmark/profiles`);
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).profiles.map((p: any) => p.id)).toEqual(['H1', 'H2', 'H3', 'H4']);
  });
  test('query library exposes Gold/Silver and structured constraints', async ({ request }) => {
    const queries = (await (await request.get(`${api}/api/v1/benchmark/queries`)).json()).queries;
    expect(queries).toHaveLength(120); expect(['Gold', 'Silver']).toContain(queries[0].label_status); expect(queries[0]).toHaveProperty('canonical_required');
  });
  test('H3/H4 execution returns candidate provenance', async ({ request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H3' } })).json();
    expect(payload.profile).toBe('H3'); expect(payload.raw_trace).toBeTruthy(); expect(payload.results[0].id).toMatch(/^expert-v2-/);
  });
  test('constraint evaluation is explicit', async ({ request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H2' } })).json();
    expect(payload.metrics).toHaveProperty('required_constraint_satisfaction'); expect(payload.benchmark).toHaveProperty('label_status');
  });
  test('evidence remains keyed by canonical expert id', async ({ request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H2' } })).json();
    expect(Object.keys(payload.evidence_by_result)).toContain(payload.results[0].id);
  });
  test('labelled metric cards contain real values', async ({ request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H2' } })).json();
    expect(typeof payload.metrics.ndcg_at_5).toBe('number'); expect(typeof payload.metrics.precision_at_5).toBe('number');
  });
  test('H4 timing separates reranker and end-to-end stages', async ({ request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H4' } })).json();
    expect(payload.metrics).toHaveProperty('reranker_inference_latency_ms'); expect(payload.metrics).toHaveProperty('total_latency_ms');
  });
  test('manifest exposes dataset and model identity', async ({ request }) => {
    const manifest = await (await request.get(`${api}/api/v1/benchmark/manifest`)).json();
    expect(manifest.dataset_checksum).toBe('514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc'); expect(manifest.embedding_model).toBe('BAAI/bge-m3');
  });
  test('Workbench and Query Lab navigation remain available', async ({ page }) => {
    await expect(page.getByText('Workbench', { exact: true }).first()).toBeVisible(); await expect(page.getByText('Query Lab', { exact: true }).first()).toBeVisible();
  });
  test('v0.5 identity and Dataset v2 free-query defaults are visible', async ({ page, request }) => {
    await expect(page.locator('body')).toContainText('v0.5.0');
    await expect(page.locator('body')).toContainText('DATASET V2');
    const payload = await (await request.post(`${api}/api/v1/query`, { data: { query: 'Find healthcare experts with Azure AI experience' } })).json();
    expect(payload.profile).toBe('H2'); expect(payload.dataset_context.dataset).toBe('Expert Discovery v2'); expect(payload.results[0].id).toMatch(/^expert-v2-/);
  });
  test('query selector labels are human-readable and constraints are structured', async ({ page }) => {
    await page.getByText('Query Lab', { exact: true }).first().click();
    await expect(page.locator('body')).toContainText('Requirements');
    await expect(page.locator('body')).toContainText(/Gold|Silver/);
    await expect(page.locator('body')).not.toContainText('not_applicable');
    await expect(page.locator('body')).toContainText(/Exact Skill|Organization Relationship|Skill \+ Industry/);
  });
  test('experiment metrics are grouped and unused stages are explicit', async ({ page, request }) => {
    const payload = await (await request.post(`${api}/api/v1/benchmark/execute`, { data: { query_id: 'v2-q-001', profile: 'H2' } })).json();
    expect(payload.metrics.fusion_latency_ms === null || payload.metrics.fusion_latency_ms === undefined).toBeTruthy();
    await page.getByText('Query Lab', { exact: true }).first().click();
    await page.getByRole('button', { name: 'Execute labelled query' }).click();
    await expect(page.locator('body')).toContainText('Ranking Quality'); await expect(page.locator('body')).toContainText('Coverage & Constraint Diagnostics'); await expect(page.locator('body')).toContainText('Performance');
  });
  test('query selection transitions keep detail and requirements synchronized', async ({ page }) => {
    await page.getByText('Query Lab', { exact: true }).first().click();
    const selector = page.getByLabel('Benchmark query');
    await selector.selectOption('v2-q-002');
    await expect(page.locator('body')).toContainText('Query ID: v2-q-002');
    await expect(page.locator('body')).toContainText('Skill + Industry');
    await expect(page.locator('body')).toContainText('manufacturing');
    await page.getByLabel('Benchmark tier filter').selectOption('Silver');
    await expect(page.locator('body')).toContainText('Silver');
    await expect(page.locator('body')).not.toContainText('Query ID: v2-q-001');
  });
  test('changing query or profile invalidates prior execution', async ({ page }) => {
    await page.getByText('Query Lab', { exact: true }).first().click();
    await page.getByLabel('Benchmark query').selectOption('v2-q-001');
    await page.getByRole('button', { name: 'Execute labelled query' }).click();
    await expect(page.locator('body')).toContainText('Metrics for this labelled query');
    await page.getByLabel('Benchmark query').selectOption('v2-q-002');
    await expect(page.locator('body')).toContainText('previous execution is stale');
    await page.getByLabel('Retrieval profile').selectOption('H3');
    await expect(page.locator('body')).toContainText('previous execution is stale');
  });
  test('backend-unavailable state remains actionable', async ({ page }) => {
    await expect(page.locator('body')).toContainText(/Workbench|Backend unavailable/);
  });
  test('free-query H2 uses Dense semantics and compact unlabelled quality state', async ({ page }) => {
    await page.getByText('Workbench', { exact: true }).first().click();
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    const resultList = page.locator('.grid .result .score-stack');
    await expect(resultList.first()).toContainText('Dense score');
    expect((await resultList.allTextContents()).join(' ')).not.toContain('reranker score');
    await expect(page.locator('body')).toContainText('Quality evaluation unavailable');
    await expect(page.locator('body')).not.toContainText('NDCG@5');
  });
  test('execution context is compact and advanced details are collapsed', async ({ page }) => {
    await page.getByText('Workbench', { exact: true }).first().click();
    await page.getByRole('button', { name: 'Run retrieval' }).click();
    await expect(page.locator('body')).toContainText('Retriever(s)');
    await expect(page.locator('body')).toContainText('Advanced Execution Details');
    await expect(page.locator('details.advanced-details')).not.toHaveAttribute('open', '');
    await expect(page.locator('details.advanced-details pre')).not.toBeVisible();
  });
});
