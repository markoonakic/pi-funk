# Gateway model discovery

Native Pi providers for four subscriptions routed through CLIProxyAPI. Standalone
Pi discovers this directory through its normal extensions path. BB's isolated
launcher selects it explicitly even though ambient extensions are disabled.

| Display name | Stable Pi provider ID | Example model ID sent to the gateway |
| --- | --- | --- |
| Codex | `openai-codex` | `gpt-6-astra` |
| Antigravity | `antigravity` | `gemini-3.8-flash-high` |
| OpenCode Go | `cliproxy-go` | `go/glm-5.3-flash` |
| Command Code | `cliproxy` | `cc/z-ai/glm-5.3-flash` |

Model names stay clean (`GLM 5.3 Flash`). BB Custom UI's plugin-only content
script formats the separate native source qualifier as `Command Code` or
`OpenCode Go`. BB core is unchanged. If the UI plugin is disabled or the picker
markup no longer matches, the original technical qualifier remains visible.
Command Code automatic discovery uses `cc/` route IDs to prevent collisions with
Codex and Antigravity. Existing threads using old Command Code IDs must select the
new route. Go and Command Code models stay separate routes. The label adapter does not
change BB's search logic; technical IDs and model names remain searchable.

## Availability and refresh

- Reads the configured `providers.cliproxy.baseUrl` and the current profile's
  private `cliproxy-api-key`. The key is a gateway inference key, never an
  upstream subscription key or a management key.
- Remote gateways require HTTPS. The sole HTTP exception is the local
  `127.0.0.1:8317` listener. User information, queries, fragments, other HTTP
  hosts, and other HTTP ports remain rejected. This does not disable TLS checks.
- Fetches `/v1/models` at startup with an 8-second deadline, no redirects, and a
  1 MiB response limit. No model request is sent for discovery.
- Uses `owned_by` for all four providers. Command Code automatic discovery
  publishes `command-code` ownership and `cc/` IDs. Recognized vendor prefixes
  remain a fallback for older unowned aliases; new providers do not need this
  fallback. Explicitly unrelated owners are never claimed.
- Only currently advertised chat models appear. An account's model allow-list,
  entitlement, regional restrictions, or cooldown can reduce the gateway list.
  No upstream allow-list or consent setting is changed by this extension.
- No chat-model exclusions are applied, including Muse Spark. Image-generation
  and review-only endpoints are excluded from the coding-agent model picker.
- `/gateway-models-refresh` refreshes an existing Pi runtime. New runtimes fetch
  automatically. BB separately caches its picker catalog for up to ten minutes;
  refreshing one Pi thread does not invalidate BB's server-side picker cache.
- A failed fetch can reuse the same gateway's validated catalog for up to 24
  hours, with a warning. Only IDs, ownership, timestamp and gateway URL are
  cached in the private profile. Keys and response/error bodies are not cached.

## Metadata versus overrides

Discovery determines **which models exist**, not every model capability.
CLIProxyAPI's model endpoint omits most context, output and thinking metadata.

1. Installed Pi catalogs supply known Codex, Google and Go model metadata. Node's
   package resolver locates pi-ai relative to the running Pi package, so both
   nested and sibling Nix package layouts work. Discovery does not read
   metadata from an unrelated global npm installation.
2. `metadata.mjs` supplies gateway-specific defaults: Antigravity information
   from CLIProxyAPI v7.3.6 and previously reviewed Command Code route settings.
   These are adapter compatibility data, not another per-user override file.
3. Unknown models receive conservative client defaults: text input, 128k
   context, 16k output and no advertised thinking control. Those values are not
   verified upstream maxima. New-model metadata may need an adapter/catalog update.
4. Pi's native provider composition applies `models.json` overrides on top.

The current `models.json` contains connection settings for the four providers
and reviewed per-model overrides under `openai-codex.modelOverrides`.
GPT-6.1 Terra joins the configured Astra, Sol, and Luna models at 1,000,000 context
and 128,000 output tokens. Its reasoning map and image support follow
[Pi's published Codex metadata](https://pi.dev/models/openai-codex/gpt-6-1-terra),
but are explicit overrides while the Nix-managed Pi 1.4 catalog lacks this ID.
Remove those capability overrides when the installed catalog supplies them;
keep the deliberate context/output override. No model arrays are required for
any of the four sources. These client limits do not prove that the gateway
accepts one-million-token requests; the existing compaction reserve is unchanged.

Example of a future optional user customization (not currently applied):

```json
{
  "providers": {
    "cliproxy-go": {
      "modelOverrides": {
        "go/glm-5.3-flash": { "name": "GLM 5.3 Flash" }
      }
    }
  }
}
```

Per-token costs are left unpriced (zero in Pi's required numeric fields); that
means **not priced here**, not free service. Subscription quota is shown by BB's
CLIProxyAPI Usage plugin. Maximum request sizes and regional access still depend
on each upstream service.

Go requests get a stable `x-opencode-session` from Pi's session manager. All four
providers use the gateway's Responses endpoint; the gateway owns upstream
protocol conversion and account selection.

## Checks

```sh
node --test profiles/bb/test_gateway_catalog.mjs profiles/bb/test_gateway_url.mjs
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s profiles/bb -p test_gateway_runtime.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s profiles/bb -p test_launch.py
```

The runtime check uses the actual Pi CLI, fake credentials and a cached catalog.
It checks native registration, clean names and distinct source IDs, Codex overrides, the
refresh command, Muse Spark availability, and that no key is copied into catalog output.
It never sends a model request. The package-layout correction passes this check
with installed Pi 1.1.0 and the Node 24 Pi 1.4.0 Nix candidate. Pi's extension
import shim exposes the Responses API factory through pi-ai's compatibility
surface, while provider registration uses `createProvider`. These isolated
checks do not mean that the candidate has been deployed.
