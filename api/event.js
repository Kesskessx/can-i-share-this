const ALLOWED_EVENTS = new Set(['homepage_view', 'paste', 'analyze', 'deep_scan', 'scan_result']);
const ALLOWED_STATUSES = new Set(['low', 'caution', 'high', 'unknown']);

function bool(value) {
  return value === true;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const event = String(body.event || '');
    if (!ALLOWED_EVENTS.has(event)) return res.status(400).json({ error: 'Unknown event' });

    // Privacy contract: never log the scanned URL, hostname, query string, pasted text,
    // IP address, user agent, or any free-form field supplied by the browser.
    if (event === 'scan_result') {
      const status = ALLOWED_STATUSES.has(String(body.status || '')) ? String(body.status) : 'unknown';
      console.log('[cist-scan-aggregate]', JSON.stringify({
        event: 'scan_result',
        status,
        redirected: bool(body.redirected),
        shortened: bool(body.shortened),
        phishing: bool(body.phishing),
        lookalike: bool(body.lookalike),
        domain_changed: bool(body.domain_changed),
        risky_download: bool(body.risky_download),
        timestamp: new Date().toISOString()
      }));
      return res.status(204).end();
    }

    // Intentionally do not log the scanned URL, hostname, query string, or pasted text.
    console.log('[cist-event]', JSON.stringify({
      event,
      path: '/',
      timestamp: new Date().toISOString()
    }));
    return res.status(204).end();
  } catch {
    return res.status(400).json({ error: 'Invalid event payload' });
  }
};
