const VOTES = new Set(['yes', 'no']);
const REASONS = new Set(['wrong_verdict', 'wrong_destination', 'unclear_explanation', 'incomplete_scan']);
const INPUT_TYPES = new Set(['link', 'email', 'message', 'crypto', 'qr', 'image', 'file', 'other']);
const STATUSES = new Set(['low', 'caution', 'high', 'unknown']);

function parseBody(req) {
  if (typeof req.body !== 'string') return req.body || {};
  if (Buffer.byteLength(req.body, 'utf8') > 4096) throw new Error('Payload too large');
  return JSON.parse(req.body || '{}');
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = parseBody(req);
    const vote = VOTES.has(String(body.vote || '')) ? String(body.vote) : null;
    const reason = REASONS.has(String(body.reason || '')) ? String(body.reason) : null;
    const inputType = INPUT_TYPES.has(String(body.input_type || '')) ? String(body.input_type) : 'other';
    const status = STATUSES.has(String(body.status || '')) ? String(body.status) : 'unknown';
    const signalCount = Math.max(0, Math.min(6, Number.isInteger(body.signal_count) ? body.signal_count : 0));

    if (!vote || (vote === 'no' && !reason) || (vote === 'yes' && reason)) {
      return res.status(400).json({ error: 'Invalid feedback' });
    }

    // Privacy contract: never log the scanned URL, hostname, email address,
    // message, crypto address, IP address, user agent, or free-form text.
    console.log('[cist-feedback]', JSON.stringify({
      vote,
      reason,
      input_type: inputType,
      status,
      signal_count: signalCount,
      timestamp: new Date().toISOString()
    }));

    return res.status(204).end();
  } catch (_) {
    return res.status(400).json({ error: 'Invalid feedback payload' });
  }
};
