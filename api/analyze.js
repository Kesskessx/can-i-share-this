const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');

function detectType(input) {
  const value = String(input || '').trim();
  if (!value) return 'unknown';
  if (/^https?:\/\//i.test(value)) return 'url';
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'email';
  if (/^0x[a-fA-F0-9]{40}$/.test(value) || /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(value) || /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(value) || /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value)) return 'crypto';
  const url = value.match(/https?:\/\/[^\s<>"']+/i);
  if (url) return 'message-url';
  const email = value.match(/[^\s@]+@[^\s@]+\.[^\s@]+/);
  if (email) return 'message-email';
  return 'message';
}

function wrapResponse(res, detectedType) {
  const originalJson = res.json.bind(res);
  res.json = function (body) {
    if (body && typeof body === 'object' && !Array.isArray(body)) {
      return originalJson({ detectedType, ...body });
    }
    return originalJson(body);
  };
  return res;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const original = String(body.input || body.url || body.email || body.address || '').trim();
  if (!original) return res.status(400).json({ error: 'Input required', detectedType: 'unknown' });

  const detectedType = detectType(original);
  const out = wrapResponse(res, detectedType);

  if (detectedType === 'url') {
    req.body = { url: original };
    return checkHandler(req, out);
  }
  if (detectedType === 'email') {
    req.body = { input: original };
    return emailHandler(req, out);
  }
  if (detectedType === 'crypto') {
    req.body = { input: original };
    return cryptoHandler(req, out);
  }
  if (detectedType === 'message-url') {
    const match = original.match(/https?:\/\/[^\s<>"']+/i);
    req.body = { url: match ? match[0].replace(/[),.;!?]+$/, '') : original };
    return checkHandler(req, out);
  }
  if (detectedType === 'message-email') {
    const match = original.match(/[^\s@]+@[^\s@]+\.[^\s@]+/);
    req.body = { input: match ? match[0].replace(/[),.;!?]+$/, '') : original };
    return emailHandler(req, out);
  }

  return res.status(200).json({
    detectedType: 'message',
    inputType: 'message',
    safety: {
      status: 'unknown',
      riskScore: 0,
      verdict: 'No supported link, email, or crypto address was detected',
      signals: [],
      checksPerformed: ['Input type detection']
    },
    verdict: 'Paste a link, email address, crypto address, or upload an image for a complete check.'
  });
};
