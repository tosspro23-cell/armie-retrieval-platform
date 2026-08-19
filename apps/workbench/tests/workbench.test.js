import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8');

test('Workbench exposes Query Lab navigation and audit/evidence views', () => {
  for (const marker of ['Workbench', 'Query Lab', 'Case Library', 'Audit', 'Evidence', 'Raw Trace', 'Download Trace JSON']) {
    assert.ok(source.includes(marker), `missing UI marker: ${marker}`);
  }
});

test('Workbench exposes backend-unavailable recovery and provider-specific scores', () => {
  for (const marker of ['Backend unavailable', 'Retry connection', 'make workbench', 'Scores are provider-specific', 'AppErrorBoundary']) {
    assert.ok(source.includes(marker), `missing resilience marker: ${marker}`);
  }
});

test('Query Lab exposes structured comparison dimensions before raw JSON', () => {
  for (const marker of ['function Comparison', 'Overlap and ranking', 'Jaccard overlap', 'Latency delta', 'Rank movement', 'Raw comparison JSON']) {
    assert.ok(source.includes(marker), `missing comparison marker: ${marker}`);
  }
});

test('Score and unavailable-value semantics are explicit', () => {
  for (const marker of ['score_type', 'score_source', 'Not applicable', 'Not available']) {
    assert.ok(source.includes(marker), `missing semantic marker: ${marker}`);
  }
});

test('Constraint UX distinguishes semantic intent from registry-backed filters', () => {
  for (const marker of ['Semantic query', 'Must-have filters', 'not automatically converted into filters', 'Base retriever: H2 Dense', 'Exclude', 'constraintRequirement']) {
    assert.ok(source.includes(marker), `missing constraint UX marker: ${marker}`);
  }
});

test('Clarification UX preserves resolution and confirmation boundaries', () => {
  for (const marker of ['InterpretationPanel', 'Interpretation review', 'Review intent', 'clarification_id', 'Confirm interpretation', 'VALIDATED_CONTRACT', 'Search with confirmed constraints', 'never executes C1']) {
    assert.ok(source.includes(marker), `missing clarification marker: ${marker}`);
  }
});
