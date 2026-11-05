// Model discovery owns availability. Metadata does not grant access to a model.
// Model IDs and provider IDs are stable; friendly labels are presentation only.
export const PROVIDERS = {
  'openai-codex': 'Codex',
  antigravity: 'Antigravity',
  'cliproxy-go': 'OpenCode Go',
  cliproxy: 'Command Code',
};

export function parseCatalog(raw) {
  if (!raw || !Array.isArray(raw.data) || raw.data.length > 2000) throw new Error('Invalid gateway catalog');
  const seen = new Set();
  return raw.data.flatMap(row => {
    if (!row || typeof row.id !== 'string' || row.id.length > 256 || !/^[a-zA-Z0-9][a-zA-Z0-9._/:+-]*$/.test(row.id)) return [];
    if (seen.has(row.id)) return [];
    seen.add(row.id);
    return [{ id: row.id, owned_by: typeof row.owned_by === 'string' ? row.owned_by : '' }];
  });
}

export function modelSource(row) {
  // Image-generation and review-only endpoints are not coding-agent chat models.
  if (/^(gpt-image(?:-|$)|codex-auto-review$)/i.test(row.id) || /(?:^|[-/])image(?:-|$)/i.test(row.id)) return undefined;
  if (row.id.startsWith('go/') && row.owned_by === 'opencode-go') return 'cliproxy-go';
  if (row.owned_by === 'openai' || row.owned_by === 'codex') return 'openai-codex';
  if (row.owned_by === 'antigravity') return 'antigravity';
  // The deployed Command Code plugin omits ownership on vendor/model aliases.
  // Do not treat arbitrary unowned or explicitly unrelated models as Command Code.
  if (row.owned_by === 'command-code' ||
      (!row.owned_by && /^(deepseek|z-ai|zai-org|xiaomi|moonshotai|minimaxai|qwen|google|meta|xai|stepfun|tencent|nvidia|sakana|thinkingmachines|poolside)\//i.test(row.id))) return 'cliproxy';
  return undefined;
}

function readableName(id) {
  const brands = { glm: 'GLM', gpt: 'GPT', deepseek: 'DeepSeek', mimo: 'MiMo', qwen: 'Qwen', kimi: 'Kimi', minimax: 'MiniMax', oss: 'OSS' };
  return id.split('/').at(-1).split('-').map(part => brands[part.toLowerCase()] ?? part[0].toUpperCase() + part.slice(1)).join(' ');
}

export function gatewayModels(rows, catalogs = {}, gatewayMetadata = {}) {
  const result = Object.fromEntries(Object.keys(PROVIDERS).map(id => [id, []]));
  const index = Object.fromEntries(Object.entries(catalogs).map(([provider, models]) => [provider, new Map(models.map(model => [model.id.toLowerCase(), model]))]));
  for (const row of rows) {
    const provider = modelSource(row);
    if (!provider) continue;
    let known;
    const baseID = row.id.split('/').at(-1).toLowerCase();
    if (provider === 'openai-codex') known = index['openai-codex']?.get(row.id.toLowerCase());
    else if (provider === 'antigravity') known = index.google?.get(row.id.toLowerCase());
    else known = index['opencode-go']?.get(baseID) ?? index.opencode?.get(baseID);
    // Reviewed transport-specific metadata takes precedence over direct-provider
    // catalogs. This is part of the adapter, not a second user override file.
    const metadataID = provider === 'cliproxy' ? row.id.replace(/^cc\//, '') : row.id;
    known = { ...known, ...gatewayMetadata[provider]?.[metadataID] };
    const name = (known.name ?? readableName(row.id)).replace(/\s*·\s*(Codex|Antigravity|OpenCode Go|Command Code)$/u, '');
    result[provider].push({
      id: row.id,
      name,
      api: 'openai-responses',
      reasoning: known.reasoning ?? false,
      ...(known.thinkingLevelMap ? { thinkingLevelMap: known.thinkingLevelMap } : {}),
      input: (known.input ?? ['text']).filter(type => type === 'text' || type === 'image'),
      // Conservative client defaults if neither catalog describes a new model.
      // These are NOT a claim that the upstream context size was discovered.
      contextWindow: known.contextWindow ?? 128000,
      maxTokens: known.maxTokens ?? 16384,
      // Subscription quota belongs to the usage panel, not a guessed API bill.
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    });
  }
  for (const models of Object.values(result)) models.sort((a, b) => a.id.localeCompare(b.id));
  return result;
}
