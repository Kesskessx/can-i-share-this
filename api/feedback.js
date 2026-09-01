module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const body = typeof req.body === 'string' ? (() => { try { return JSON.parse(req.body); } catch { return {}; } })() : (req.body || {});
  const vote = body.vote === 'yes' || body.vote === 'no' ? body.vote : null;
  if (!vote) return res.status(400).json({ error: 'Invalid vote' });
  return res.status(200).json({ ok: true });
};
