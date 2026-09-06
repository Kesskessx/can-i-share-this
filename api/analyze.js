'use strict';

const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');
const imageHandler = require('./image-check');
const messageHandler = require('./message-check');
const socialProfileHandler = require('../lib/social-profile-safety');
const { enrichScanResult: enrichScanResultV2 } = require('../lib/mega-evidence');
const { enrichScanResult: enrichScanResultV3, upgradeMegaResult } = require('../lib/mega-evidence-v3');
const { orchestrateImageResult } = require('../lib/image-evidence-orchestrator');

const SOCIAL_HOSTS = new Set([
  'instagram.com', 'www.instagram.com',
  'facebook.com', 'www.facebook.com', 'm.facebook.com',
  'tiktok.com', 'www.tiktok.com',
  'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com',
  't.me', 'telegram.me', 'www.telegram.me',
  'discord.com', 'www.discord.com', 'discordapp.com', 'www.discordapp.com'
]);
const SOCIAL_AVATAR_CACHE = new Map();
const SOCIAL_AVATAR_TTL_MS = 10 * 60 * 1000;

function leadingUrl(value) {
  const match = String(value || '').trim().match(/^https?:\/\/[^\s<>"']+/i);
  return match ? match[0] : null;
}

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
  const firstUrl = leadingUrl(value);
  if (firstUrl && isSocialProfileUrl(firstUrl)) return 'social-profile';
  if (/^https?:\/\//i.test(value)) return 'url';
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'email';
  if (/^0x[a-fA-F0-9]{40}$/.test(value) || /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(value) || /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(value) || /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(value) || /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value)) return 'crypto';
  if (/https?:\/\/[^\s<>"']+/i.test(value)) return 'message-url';
  if (/[^\s@]+@[^\s@]+\.[^\s@]+/.test(value)) return 'message-email';
  return 'message';
}

function enrichBody(detectedType, originalInput, body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return body;
  const base = { detectedType, ...body };
  if (base.error) return base;
  try {
    return enrichScanResultV3({ detectedType, originalInput, body: base });
  } catch (err) {
    console.error('Mega Scanner enrichment failed', err);
    return base;
  }
}

function wrapResponse(res, detectedType, originalInput = '') {
  const originalJson = typeof res.json === 'function' ? res.json.bind(res) : null;
  const originalEnd = typeof res.end === 'function' ? res.end.bind(res) : null;
  let insideJson = false;

  if (originalJson) {
    res.json = function (body) {
      insideJson = true;
      try { return originalJson(enrichBody(detectedType, originalInput, body)); }
      finally { insideJson = false; }
    };
  }

  if (originalEnd) {
    res.end = function (payload, encoding, callback) {
      if (insideJson || typeof payload !== 'string') return originalEnd(payload, encoding, callback);
      try {
        const parsed = JSON.parse(payload);
        const enriched = enrichBody(detectedType, originalInput, parsed);
        return originalEnd(JSON.stringify(enriched), encoding, callback);
      } catch (_) {
        return originalEnd(payload, encoding, callback);
      }
    };
  }
  return res;
}

function captureHandler(handler, req) {
  return new Promise(resolve => {
    let done = false;
    const finish = (status, payload) => {
      if (done) return;
      done = true;
      resolve({ status, body: payload });
    };
    const fake = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) { this.headers[String(k).toLowerCase()] = v; return this; },
      getHeader(k) { return this.headers[String(k).toLowerCase()]; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload); return this; },
      end(payload) {
        let body = payload;
        if (typeof payload === 'string') {
          try { body = JSON.parse(payload); } catch (_) {}
        }
        finish(this.statusCode, body);
        return this;
      }
    };
    Promise.resolve(handler(req, fake)).then(() => {
      if (!done) finish(fake.statusCode, null);
    }).catch(err => finish(500, { error: err && err.message ? err.message : 'Image analysis failed' }));
  });
}

async function analyzeImage(req, res, image) {
  const imageReq = { ...req, body: { image }, method: 'POST' };
  const captured = await captureHandler(imageHandler, imageReq);
  if (captured.status >= 400 || !captured.body || typeof captured.body !== 'object') {
    return res.status(captured.status || 500).json(captured.body || { error: 'Image analysis failed' });
  }
  try {
    const orchestrated = await orchestrateImageResult(captured.body);
    const v2 = enrichScanResultV2({ detectedType: 'image', originalInput: '', body: { detectedType: 'image', ...orchestrated } });
    const final = upgradeMegaResult(v2);
    return res.status(captured.status || 200).json(final);
  } catch (err) {
    console.error('Mega Scanner image orchestration failed', err);
    const fallback = enrichScanResultV3({ detectedType: 'image', originalInput: '', body: { detectedType: 'image', ...captured.body } });
    return res.status(captured.status || 200).json(fallback);
  }
}

function decodeHtml(value) {
  return String(value || '')
    .replace(/&amp;/gi, '&').replace(/&quot;/gi, '"').replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<').replace(/&gt;/gi, '>')
    .replace(/&#(\d+);/g, (_, n) => { try { return String.fromCodePoint(Number(n)); } catch { return ''; } })
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => { try { return String.fromCodePoint(parseInt(n, 16)); } catch { return ''; } });
}

function htmlAttr(tag, name) {
  const match = String(tag || '').match(new RegExp('\\b' + name + '\\s*=\\s*(["\\\'])([\\s\\S]*?)\\1', 'i'));
  return match ? decodeHtml(match[2]).trim() : '';
}

function avatarFromHtml(html, baseUrl) {
  const tags = String(html || '').slice(0, 350000).match(/<meta\b[^>]*>/gi) || [];
  const wanted = new Set(['og:image', 'og:image:secure_url', 'twitter:image', 'twitter:image:src']);
  for (const tag of tags) {
    const key = (htmlAttr(tag, 'property') || htmlAttr(tag, 'name')).toLowerCase();
    if (!wanted.has(key)) continue;
    const content = htmlAttr(tag, 'content');
    if (!content) continue;
    try {
      const image = new URL(content, baseUrl);
      if (image.protocol === 'https:') return image.toString();
    } catch (_) {}
  }
  return null;
}

function cacheAvatar(key, value) {
  if (SOCIAL_AVATAR_CACHE.size >= 100) {
    const first = SOCIAL_AVATAR_CACHE.keys().next().value;
    if (first) SOCIAL_AVATAR_CACHE.delete(first);
  }
  SOCIAL_AVATAR_CACHE.set(key, { value, expiresAt: Date.now() + SOCIAL_AVATAR_TTL_MS });
  return value;
}

async function fetchSocialAvatar(profileUrl) {
  if (!profileUrl || !isSocialProfileUrl(profileUrl)) return null;
  const cached = SOCIAL_AVATAR_CACHE.get(profileUrl);
  if (cached && cached.expiresAt > Date.now()) return cached.value;
  if (cached) SOCIAL_AVATAR_CACHE.delete(profileUrl);

  let current;
  try { current = new URL(profileUrl); } catch (_) { return null; }
  if (current.protocol !== 'https:') current.protocol = 'https:';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 1200);
  try {
    let response = null;
    for (let hop = 0; hop < 3; hop++) {
      response = await fetch(current.toString(), {
        redirect: 'manual', signal: controller.signal,
        headers: {
          'user-agent': 'Mozilla/5.0 (compatible; CanIShareThis/3.0; +https://canisharethis.com)',
          'accept': 'text/html,application/xhtml+xml', 'accept-language': 'en-US,en;q=0.8'
        }
      });
      if (response.status >= 300 && response.status < 400) {
        const location = response.headers.get('location');
        if (!location) break;
        const next = new URL(location, current);
        if (!SOCIAL_HOSTS.has(next.hostname.toLowerCase())) return cacheAvatar(profileUrl, null);
        current = next;
        continue;
      }
      break;
    }
    if (!response || !response.ok) return cacheAvatar(profileUrl, null);
    const type = String(response.headers.get('content-type') || '').toLowerCase();
    if (type && !type.includes('text/html') && !type.includes('application/xhtml+xml')) return cacheAvatar(profileUrl, null);
    const html = await response.text();
    return cacheAvatar(profileUrl, avatarFromHtml(html, current));
  } catch (_) {
    return cacheAvatar(profileUrl, null);
  } finally {
    clearTimeout(timer);
  }
}

function wrapSocialResponse(res, detectedType, originalInput, avatarPromise) {
  const out = wrapResponse(res, detectedType, originalInput);
  const baseJson = out.json.bind(out);
  out.json = function (body) {
    if (!body || typeof body !== 'object' || Array.isArray(body) || !body.socialProfile) return baseJson(body);
    return Promise.resolve(avatarPromise).then(avatarUrl => baseJson({
      ...body,
      socialProfile: { ...body.socialProfile, avatarUrl: avatarUrl || null, avatarState: avatarUrl ? 'available' : 'unavailable' }
    })).catch(() => baseJson({
      ...body,
      socialProfile: { ...body.socialProfile, avatarUrl: null, avatarState: 'unavailable' }
    }));
  };
  return out;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }

  if (typeof body.image === 'string' && body.image.startsWith('data:image/')) {
    return analyzeImage(req, res, body.image);
  }

  const original = String(body.input || body.url || body.email || body.address || body.message || '').trim();
  if (!original) return res.status(400).json({ error: 'Input required', detectedType: 'unknown' });
  const detectedType = detectType(original);

  if (detectedType === 'social-profile') {
    const profileUrl = leadingUrl(original);
    const avatarPromise = profileUrl && isSocialProfileUrl(profileUrl) ? fetchSocialAvatar(profileUrl) : Promise.resolve(null);
    req.body = { input: original };
    return socialProfileHandler(req, wrapSocialResponse(res, detectedType, original, avatarPromise));
  }

  const out = wrapResponse(res, detectedType, original);
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
