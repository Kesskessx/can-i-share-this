const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');
const imageHandler = require('./image-check');
const messageHandler = require('./message-check');
const socialProfileHandler = require('./social-profile-check');

const SOCIAL_HOSTS = new Set([
  'instagram.com', 'www.instagram.com',
  'facebook.com', 'www.facebook.com', 'm.facebook.com',
  'tiktok.com', 'www.tiktok.com',
  'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com',
  't.me', 'telegram.me', 'www.telegram.me',
  'discord.com', 'www.discord.com', 'discordapp.com', 'www.discordapp.com'
]);

function isSocialProfileUrl(value) {
  let url;
  try { url = new URL(value); } catch (_) { return false; }
  if (!SOCIAL_HOSTS.has(url.hostname.toLowerCase())) return false;
  const parts = url.pathname.split('/').filter(Boolean);
  const host = url.hostname.toLowerCase();

  if (host.includes('tiktok.com')) return parts.some(v => v.startsWith('@'));
  if (host === 'discord.com' || host === 'www.discord.com' || host === 'discordapp.com' || host === 'www.discordapp.com') return parts[0] === 'users' && Boolean(parts[1]);
  if (host === 'facebook.com' || host === 'www.facebook.com' || host === 'm.facebook.com') {
    if (url.pathname.toLowerCase() === '/profile.php') return Boolean(url.searchParams.get('id'));
    return Boolean(parts[0]) && !['watch','groups','marketplace','gaming','events','reel','reels','share','help','privacy'].includes(parts[0].toLowerCase());
  }
  if (host === 't.me' || host === 'telegram.me' || host === 'www.telegram.me') return Boolean(parts[0]) && !parts[0].startsWith('+') && !['joinchat','share','proxy','socks'].includes(parts[0].toLowerCase());
  if (host === 'x.com' || host === 'www.x.com' || host === 'twitter.com' || host === 'www.twitter.com') return Boolean(parts[0]) && !['home','explore','search','messages','settings','i','intent','share','compose','notifications'].includes(parts[0].toLowerCase());
  if (host === 'instagram.com' || host === 'www.instagram.com') return Boolean(parts[0]) && !['p','reel','reels','stories','explore','accounts','direct','about','developer'].includes(parts[0].toLowerCase());
  return false;
}

function detectType(input) {
  const value = String(input || '').trim();
  if (!value) return 'unknown';
  if (/^@[A-Za-z0-9._-]{2,64}$/.test(value)) return 'social-profile';
  if (/^https?:\/\//i.test(value) && isSocialProfileUrl(value)) return 'social-profile';
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

  if (detectedType === 'social-profile') {
    req.body = { input: original };
    return socialProfileHandler(req, out);
  }
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
