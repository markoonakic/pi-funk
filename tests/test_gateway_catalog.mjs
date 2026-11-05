import test from 'node:test';
import assert from 'node:assert/strict';
import { PROVIDERS, gatewayModels, modelSource, parseCatalog } from '../extensions/cliproxy-models/catalog.mjs';
import { gatewayMetadata } from '../extensions/cliproxy-models/metadata.mjs';

const rows = [
  { id: 'gpt-6-astra', owned_by: 'openai' },
  { id: 'gemini-3.8-flash-high', owned_by: 'antigravity' },
  { id: 'go/glm-5.3-flash', owned_by: 'opencode-go' },
  { id: 'z-ai/glm-5.3-flash', owned_by: '' },
];
const knownGLM = { id: 'glm-5.3-flash', name: 'GLM 5.3 Flash', reasoning: true, input: ['text'], contextWindow: 1000000, maxTokens: 64000 };
const catalogs = { 'opencode-go': [knownGLM], 'openai-codex': [{ id: 'gpt-6-astra', name: 'GPT 6 Astra', reasoning: true, contextWindow: 272000, maxTokens: 128000 }] };

test('model names stay clean and provider identity remains separate', () => {
  assert.deepEqual(PROVIDERS, { 'openai-codex': 'Codex', antigravity: 'Antigravity', 'cliproxy-go': 'OpenCode Go', cliproxy: 'Command Code' });
  const result = gatewayModels(rows, catalogs, gatewayMetadata);
  for (const provider of Object.keys(PROVIDERS)) {
    assert.equal(result[provider].length, 1);
    assert.ok(!result[provider][0].name.includes(' · '));
    assert.equal(result[provider][0].api, 'openai-responses');
  }
  assert.equal(result['cliproxy-go'][0].id, 'go/glm-5.3-flash');
  assert.equal(result.cliproxy[0].id, 'z-ai/glm-5.3-flash');
  assert.equal(result['cliproxy-go'][0].name, 'GLM 5.3 Flash');
  assert.equal(result.cliproxy[0].name, 'GLM 5.3 Flash');
  assert.notEqual(result['cliproxy-go'][0].id, result.cliproxy[0].id);
});

test('uses route metadata rather than applying direct Go controls to Command Code', () => {
  const result = gatewayModels(rows, catalogs, gatewayMetadata);
  assert.equal(result.cliproxy[0].maxTokens, 131072);
  assert.equal(result.cliproxy[0].thinkingLevelMap.medium, 'high');
  assert.equal(result.antigravity[0].contextWindow, 1048576);
  assert.equal(result.antigravity[0].reasoning, true);
  assert.equal(result['openai-codex'][0].contextWindow, 272000); // user override is Pi-owned
  assert.equal(result['cliproxy-go'][0].maxTokens, 64000);
  assert.equal(knownGLM.name, 'GLM 5.3 Flash'); // source data was not mutated
});

test('retains reviewed capabilities for every previously configured non-Codex model', () => {
  for (const [provider, models] of Object.entries(gatewayMetadata)) {
    for (const [id, metadata] of Object.entries(models)) {
      const owner = provider === 'cliproxy' ? 'command-code' : 'antigravity';
      const result = gatewayModels([{ id, owned_by: owner }], {}, gatewayMetadata)[provider][0];
      assert.ok(result, id);
      assert.equal(result.contextWindow, metadata.contextWindow, id);
      assert.equal(result.maxTokens, metadata.maxTokens, id);
      assert.equal(result.reasoning, metadata.reasoning, id);
    }
  }
});

test('includes Muse Spark from both source routes', () => {
  const result = gatewayModels([
    { id: 'go/muse-spark-1.3-contributor', owned_by: 'opencode-go' },
    { id: 'meta/muse-spark-1.3-contributor', owned_by: '' },
    { id: 'meta/muse-spark-1.2', owned_by: 'command-code' },
  ]);
  assert.equal(Object.values(result).flat().length, 3);
});

test('does not expose non-chat endpoints or claim unrelated providers', () => {
  for (const row of [
    { id: 'gpt-image-2.5', owned_by: 'openai' },
    { id: 'codex-auto-review', owned_by: 'openai' },
    { id: 'gemini-3.1-flash-image', owned_by: 'antigravity' },
    { id: 'vendor/other', owned_by: 'unrelated' },
    { id: 'go/wrong-owner', owned_by: '' },
    { id: 'unknown/model', owned_by: '' },
    { id: 'unowned-model', owned_by: '' },
  ]) assert.equal(modelSource(row), undefined, row.id);
  assert.equal(modelSource({ id: 'go/deepseek-v4-flash-vision-exp', owned_by: 'opencode-go' }), 'cliproxy-go');
});

test('new advertised models appear without a models.json entry or allow-list', () => {
  const result = gatewayModels([{ id: 'go/new-chat-model', owned_by: 'opencode-go' }]);
  assert.equal(result['cliproxy-go'][0].name, 'New Chat Model');
  assert.equal(result['cliproxy-go'][0].contextWindow, 128000);
  assert.equal(result['cliproxy-go'][0].reasoning, false);
  assert.deepEqual(result['cliproxy-go'][0].input, ['text']);
  assert.equal(result['cliproxy-go'][0].maxTokens, 16384);
});

test('Command Code ownership supports any vendor and cc routes retain metadata', () => {
  const result = gatewayModels([
    { id: 'cc/new-vendor/new-model', owned_by: 'command-code' },
    { id: 'cc/gpt-6-sol', owned_by: 'command-code' },
    { id: 'cc/z-ai/glm-5.3-flash', owned_by: 'command-code' },
    { id: 'gpt-6-sol', owned_by: 'openai' },
  ], {}, gatewayMetadata);
  assert.equal(result.cliproxy.length, 3);
  assert.equal(result['openai-codex'].length, 1);
  assert.equal(result.cliproxy.find(m => m.id === 'cc/z-ai/glm-5.3-flash').maxTokens, 131072);
});

test('rejects malformed and excessive catalogs; deduplicates and strips fields', () => {
  assert.throws(() => parseCatalog({}));
  assert.throws(() => parseCatalog({ data: Array(2001).fill({ id: 'x' }) }));
  assert.deepEqual(parseCatalog({ data: [null, {}, { id: 123 }, { id: '<script>' }, { id: 'bad\nmodel' }] }), []);
  assert.deepEqual(parseCatalog({ data: [{ id: 'go/x', owned_by: 'opencode-go', api_key: 'DO_NOT_KEEP' }, { id: 'go/x', owned_by: 'opencode-go' }] }), [{ id: 'go/x', owned_by: 'opencode-go' }]);
  assert.deepEqual(Object.values(gatewayModels([])).flat(), []);
});
