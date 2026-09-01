const ALLOWED_EVENTS = new Set(['homepage_view', 'paste', 'analyze', 'deep_scan']);

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const event = String(body.event || '');
    if (!ALLOWED_EVENTS.has(event)) return res.status(400).json({ error: 'Unknown event' });

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
