const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');
const imageHandler = require('./image-check');
const messageHandler = require('./message-check');

function detectType(input) {
  const value = String(input || '').trim();
  if (!value) return 'unknown';
  if (/^https?:\/\//i.test(value)) return 'url';
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'email';
  if (/^0x[a-fA-F0-9]{40}$/.test(value) || /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(value) || /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(value) || /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value)) return 'crypto';
  if (/https?:\/\/[^\s<>"']+/i.test(value)) return 'message-url';
  if (/[^\s@]+@[^\s@]+\.[^\s@]+/.test(value)) return 'message-email';
  return 'message';
}

function wrapResponse(res, detectedType) {
  const originalJson = res.json.bind(res);
  res.json = function (body) {
    if (body && typeof body === 'object' && !Array.isArray(body)) return originalJson({ detectedType, ...body });
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

  if (typeof body.image === 'string' && body.image.startsWith('data:image/')) {
    req.body = { image: body.image };
    return imageHandler(req, wrapResponse(res, 'image'));
  }

  const original = String(body.input || body.url || body.email || body.address || body.message || '').trim();
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

  req.body = { input: original, message: original };
  return messageHandler(req, out);
};
