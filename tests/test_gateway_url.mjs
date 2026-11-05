import assert from 'node:assert/strict';
import test from 'node:test';
import { validateGatewayUrl } from '../extensions/cliproxy-models/gateway-url.mjs';

test('remote TLS and the fixed local gateway are accepted', () => {
  for (const url of ['https://gateway.example/v1', 'http://127.0.0.1:8317/v1']) {
    assert.doesNotThrow(() => validateGatewayUrl(url));
  }
});

test('the local exception cannot authorize other cleartext destinations or credentials', () => {
  for (const url of [
    'http://gateway.example:8317/v1', 'http://localhost:8317/v1',
    'http://0.0.0.0:8317/v1', 'http://127.0.0.1:8318/v1',
    'http://127.0.0.1/v1', 'http://[::1]:8317/v1',
    'http://127.0.0.1.example:8317/v1',
    'http://user:password@127.0.0.1:8317/v1',
    'http://127.0.0.1:8317/v1?key=value', 'http://127.0.0.1:8317/v1#fragment',
    'https://user:password@gateway.example/v1',
    'https://gateway.example/v1?key=value', 'https://gateway.example/v1#fragment',
    'file:///etc/passwd', 'not a URL',
  ]) {
    assert.throws(() => validateGatewayUrl(url), undefined, url);
  }
});
