// Remote gateways require TLS. The temporary local service has one fixed listener.
export function validateGatewayUrl(baseUrl) {
  const url = new URL(baseUrl);
  const local = url.protocol === 'http:' && url.hostname === '127.0.0.1' && url.port === '8317';
  if ((url.protocol !== 'https:' && !local) || url.username || url.password || url.search || url.hash) {
    throw new Error('Invalid gateway URL');
  }
}
