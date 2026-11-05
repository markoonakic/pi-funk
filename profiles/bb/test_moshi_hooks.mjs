// Run: node --test profiles/bb/test_moshi_hooks.mjs (Node >=24).
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { stripTypeScriptTypes } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

const hook = new URL('../../extensions/moshi-hooks.ts', import.meta.url);

test('Moshi sends user prompts, not custom-message starts', {
  skip: !existsSync(hook) && 'The machine-local Moshi hook is not installed',
}, () => {
  const handlers = new Map();
  const sent = [];
  // Strip only the runtime import/export so no actual helper process can start.
  const source = readFileSync(hook, 'utf8')
    .replace('import { spawn } from "node:child_process"', '')
    .replace('export default function moshiPiHook', 'function moshiPiHook');
  vm.runInNewContext(stripTypeScriptTypes(source) + '\nmoshiPiHook(pi)', {
    pi: { on: (name, handler) => handlers.set(name, handler) },
    process: { cwd: () => '/fixture' },
    spawn: () => ({ stdin: { end: value => sent.push(JSON.parse(value)) }, unref() {} }),
  });
  const start = handlers.get('before_agent_start');
  for (const event of [
    { messageType: 'custom', message: { customType: 'fixture', content: 'not user input' } },
    { prompt: undefined },
  ]) start(event, {});
  assert.deepEqual(sent, []);
  for (const event of [{ prompt: 'Pi 1.1 prompt' }, { messageType: 'user', prompt: '' },
    { messageType: 'user', prompt: 'Pi 1.4 prompt' }]) start(event, {});
  assert.deepEqual(sent.map(payload => [payload.hook_event_name, payload.prompt]), [
    ['UserPromptSubmit', 'Pi 1.1 prompt'], ['UserPromptSubmit', ''], ['UserPromptSubmit', 'Pi 1.4 prompt'],
  ]);
});
