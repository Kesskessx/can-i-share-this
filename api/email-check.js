const { analyzeEmailAddress } = require('../lib/email-safety');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const input = String(body.input || body.email || '').trim();
    if (!input) return res.status(400).json({ error: 'Email address required' });

    const result = await analyzeEmailAddress(input);
    return res.status(200).json(result);
  } catch (err) {
    return res.status(200).json({
      inputType: 'email',
      reachable: false,
      redirects: [],
      error: err && err.message ? err.message : 'Email address check failed.',
      safety: {
        status: 'unknown',
        riskScore: 0,
        verdict: 'Email address check incomplete',
        signals: [],
        checksPerformed: ['Email syntax'],
        disclaimer: 'This checks the address and domain, not the contents of a message or the identity of the person using the mailbox.'
      }
    });
  }
};
