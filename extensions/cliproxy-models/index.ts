import { readFile, writeFile, rename, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { findPackageJSON } from 'node:module';
import { pathToFileURL } from 'node:url';
import { randomUUID } from 'node:crypto';
import { getAgentDir, getPackageDir, type ExtensionAPI } from '@earendil-works/pi-coding-agent';
import { createProvider, openAIResponsesApi, type Model, type Api } from '@earendil-works/pi-ai';
import { PROVIDERS, gatewayModels, parseCatalog } from './catalog.mjs';
import { gatewayMetadata } from './metadata.mjs';
import { validateGatewayUrl } from './gateway-url.mjs';

// Both profiles already store their gateway access key here. Never use the Go
// subscription key or the CLIProxyAPI management key for model discovery.
export default async function (pi: ExtensionAPI) {
  const agentDir = getAgentDir();
  const keyPath = join(agentDir, 'cliproxy-api-key');
  const cachePath = join(agentDir, 'cliproxy-model-catalog.json');
  let warning: string | undefined;
  let count = 0;
  const catalogs: Record<string, readonly Model<Api>[]> = {};
  for (const provider of ['openai-codex', 'google', 'opencode-go', 'opencode']) {
    try {
      // Resolve from Pi, not this extension: the official Nix package uses sibling packages.
      const aiPackage = findPackageJSON('@earendil-works/pi-ai', pathToFileURL(join(getPackageDir(), 'package.json')));
      if (!aiPackage) continue;
      const catalogPath = join(dirname(aiPackage), `dist/providers/data/${provider}.json`);
      const catalog = JSON.parse(await readFile(catalogPath, 'utf8'));
      catalogs[provider] = Object.values(catalog).flatMap(group => Object.values(group as Record<string, Model<Api>>));
    } catch { /* Missing catalog: adapter metadata or conservative defaults. */ }
  }

  async function refresh() {
    const config = JSON.parse(await readFile(join(agentDir, 'models.json'), 'utf8'));
    const baseUrl = config.providers?.cliproxy?.baseUrl?.replace(/\/+$/, '');
    if (typeof baseUrl !== 'string') throw new Error('Gateway not configured');
    validateGatewayUrl(baseUrl);
    const key = (await readFile(keyPath, 'utf8')).trim();
    if (!key || /\s/u.test(key)) throw new Error('Gateway key unavailable');
    let rows;
    try {
      const response = await fetch(`${baseUrl}/models`, {
        headers: { Authorization: `Bearer ${key}` },
        signal: AbortSignal.timeout(8000), redirect: 'error',
      });
      if (!response.ok) { await response.body?.cancel(); throw new Error('Catalog unavailable'); }
      // Bound streamed size rather than relying on Content-Length.
      const reader = response.body?.getReader();
      if (!reader) throw new Error('Empty catalog');
      const parts: Uint8Array[] = [];
      let bytes = 0;
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > 1024 * 1024) { await reader.cancel(); throw new Error('Catalog too large'); }
        parts.push(chunk.value);
      }
      rows = parseCatalog(JSON.parse(Buffer.concat(parts).toString('utf8')));
      warning = undefined;
      // Cache only validated IDs and ownership, never the key or raw response.
      const temp = `${cachePath}.${randomUUID()}.tmp`;
      try {
        await writeFile(temp, JSON.stringify({ baseUrl, observedAt: Date.now(), data: rows }), { mode: 0o600 });
        await rename(temp, cachePath);
      } catch { /* Read-only profile: discovery still works without persistence. */ }
      finally { await rm(temp, { force: true }).catch(() => undefined); }
    } catch {
      const cached = JSON.parse(await readFile(cachePath, 'utf8'));
      if (cached.baseUrl !== baseUrl || !Number.isFinite(cached.observedAt) || Date.now() - cached.observedAt > 24 * 60 * 60_000 || cached.observedAt > Date.now()) throw new Error('No fresh cached catalog');
      rows = parseCatalog(cached);
      warning = 'Gateway discovery failed; using its saved model list (at most 24 hours old).';
    }
    register(rows, baseUrl);
  }

  function register(rows: ReturnType<typeof parseCatalog>, baseUrl: string) {
    const grouped = gatewayModels(rows, catalogs, gatewayMetadata) as Record<
      string, Array<Omit<Model<'openai-responses'>, 'provider' | 'baseUrl'>>
    >;
    count = Object.values(grouped).reduce((total, models) => total + models.length, 0);
    for (const [id, name] of Object.entries(PROVIDERS)) {
      pi.registerProvider(createProvider({
        id,
        name,
        baseUrl, api: openAIResponsesApi(),
        auth: { apiKey: {
          name: 'CLIProxyAPI gateway access key',
          async check({ ctx }) {
            return await ctx.fileExists(keyPath) ? { type: 'api_key', source: 'profile gateway key' } : undefined;
          },
          async resolve({ signal }) {
            const apiKey = (await readFile(keyPath, { encoding: 'utf8', signal })).trim();
            return apiKey ? { auth: { apiKey }, source: 'profile gateway key' } : undefined;
          },
        } },
        models: grouped[id].map(model => ({ ...model, api: 'openai-responses' as const, provider: id, baseUrl })),
      }));
    }
  }

  // Startup factory is awaited by Pi and BB's get_available_models probe.
  // There is no background process, timer, generated models.json, or auth copy.
  try { await refresh(); } catch {
    warning = 'Gateway models could not be discovered. Existing explicit models are unchanged.';
  }
  pi.on('session_start', (_event, ctx) => {
    if (warning && ctx.hasUI) ctx.ui.notify(warning, 'warning');
  });
  pi.on('before_provider_headers', (event, ctx) => {
    if (ctx.model?.provider === 'cliproxy-go') {
      event.headers['x-opencode-session'] = ctx.sessionManager.getSessionId();
    }
  });
  pi.registerCommand('gateway-models-refresh', {
    description: 'Refresh Codex, Antigravity, OpenCode Go and Command Code models from CLIProxyAPI',
    handler: async (_args, ctx) => {
      await ctx.waitForIdle();
      try {
        await refresh();
        // Recompose user overrides and the synchronous available-model snapshot
        // after runtime registration, including native provider filters.
        await ctx.modelRegistry.refresh({ allowNetwork: false, signal: AbortSignal.timeout(8000) });
        ctx.ui.notify(warning ?? `Discovered ${count} gateway models. Pi overrides remain in models.json.`, warning ? 'warning' : 'info');
      } catch { ctx.ui.notify('Gateway discovery failed. The existing model list is unchanged.', 'warning'); }
    },
  });
}
