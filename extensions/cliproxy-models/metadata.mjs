// Gateway adapter metadata, not an availability list or user settings file.
// Antigravity: CLIProxyAPI v7.3.6 internal/registry/models/models.json.
// Command Code: retain this setup's reviewed route capabilities during migration
// from explicit models.json entries. Do not substitute direct Go thinking maps
// for Command Code's request translator. New IDs still come from /v1/models.
const flashThinking = { off: null, minimal: 'low', low: 'low', medium: 'medium', high: 'high' };
const flash = { reasoning: true, input: ['text', 'image'], contextWindow: 1048576, maxTokens: 65536, thinkingLevelMap: flashThinking };
const pro = { reasoning: true, input: ['text', 'image'], contextWindow: 1048576, maxTokens: 65535 };
const claude = { reasoning: true, input: ['text', 'image'], contextWindow: 200000, maxTokens: 64000 };

export const gatewayMetadata = {
  antigravity: {
    'gemini-3.8-flash-high': { ...flash, name: 'Gemini 3.8 Flash' },
    'gemini-3.7-flash-high': { ...flash, name: 'Gemini 3.7 Flash' },
    'gemini-3.6-flash-high': { ...flash, name: 'Gemini 3.6 Flash' },
    'gemini-3-flash': { ...flash, name: 'Gemini 3 Flash' },
    // Explicit gateway alias already configured in CLIProxyAPI.
    'ag-gemini-3-flash': { ...flash, name: 'Gemini 3 Flash (alias)' },
    'gemini-pro-agent': { ...pro, name: 'Gemini 3.1 Pro (High)' },
    'gemini-3.1-pro-low': { ...pro, name: 'Gemini 3.1 Pro (Low)' },
    'gemini-3.1-flash-lite': { ...pro, name: 'Gemini 3.1 Flash Lite' },
    'gemini-3.5-flash-lite': { ...pro, name: 'Gemini 3.5 Flash Lite' },
    'claude-opus-4-6-thinking': { ...claude, name: 'Claude Opus 4.6 (Thinking)' },
    'claude-sonnet-4-6': { ...claude, name: 'Claude Sonnet 4.6' },
    'gpt-oss-120b-medium': { name: 'GPT-OSS 120B (Medium)', reasoning: false, input: ['text'], contextWindow: 114000, maxTokens: 32768 },
  },
  cliproxy: {
    'deepseek/deepseek-v4.1-flash': {
      name: 'DeepSeek V4.1 Flash', reasoning: true, input: ['text'],
      contextWindow: 1000000, maxTokens: 128000, thinkingLevelMap: flashThinking,
    },
    'z-ai/glm-5.3-flash': {
      name: 'GLM 5.3 Flash', reasoning: true, input: ['text', 'image'],
      contextWindow: 1000000, maxTokens: 131072,
      thinkingLevelMap: { off: null, minimal: 'low', low: 'low', medium: 'high', high: 'high', xhigh: 'max', max: 'max' },
    },
    'xiaomi/mimo-v2.6-flash': {
      name: 'MiMo V2.6 Flash', reasoning: true, input: ['text'], contextWindow: 1048576, maxTokens: 128000,
    },
    'xiaomi/mimo-v2.6-pro': {
      name: 'MiMo V2.6 Pro', reasoning: true, input: ['text'], contextWindow: 1048576, maxTokens: 128000,
    },
  },
};
