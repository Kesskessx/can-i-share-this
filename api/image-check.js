const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');
const socialProfileHandler = require('../lib/social-profile-safety');

const MAX_BYTES = 4 * 1024 * 1024;
const ALLOWED_MIME = new Set(['image/jpeg', 'image/png', 'image/webp']);
const MAX_CROSS_CHECKS = 3;
const RISK_ORDER = { unknown: 0, low: 1, caution: 2, high: 3 };

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('cache-control', 'no-store, max-age=0');
  res.end(JSON.stringify(body));
}

function parseDataUrl(value) {
  const match = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/i.exec(String(value || ''));
  if (!match) return null;
  const mimeType = match[1].toLowerCase();
  if (!ALLOWED_MIME.has(mimeType)) return null;
  const data = match[2];
  let bytes;
  try { bytes = Buffer.from(data, 'base64'); } catch (_) { return null; }
  if (!bytes.length || bytes.length > MAX_BYTES) return null;
  return { mimeType, data };
}

function safeText(v, max = 500) {
  return typeof v === 'string' ? v.slice(0, max) : '';
}

function normalizeOutput(raw) {
  const out = raw && typeof raw === 'object' ? raw : {};
  const arr = (v, maxItems = 10, maxLen = 300) => Array.isArray(v)
    ? v.filter(x => typeof x === 'string').slice(0, maxItems).map(x => x.slice(0, maxLen))
    : [];
  const signals = Array.isArray(out.suspicious_signals)
    ? out.suspicious_signals.slice(0, 8).map(s => {
        if (typeof s === 'string') return { type: 'signal', detail: s.slice(0, 300) };
        if (!s || typeof s !== 'object') return null;
        return { type: safeText(s.type, 80) || 'signal', detail: safeText(s.detail, 300) };
      }).filter(Boolean)
    : [];
  const risk = ['low', 'caution', 'high', 'unknown'].includes(out.risk) ? out.risk : 'unknown';
  const social = out.social_profile && typeof out.social_profile === 'object' ? out.social_profile : null;
  return {
    risk,
    confidence: Number.isFinite(out.confidence) ? Math.max(0, Math.min(1, out.confidence)) : null,
    summary: safeText(out.summary, 700),
    recommended_action: safeText(out.recommended_action, 500),
    visible_text: safeText(out.visible_text, 3500),
    urls: arr(out.urls),
    emails: arr(out.emails),
    phones: arr(out.phones),
    qr_values: arr(out.qr_values),
    claimed_brands: arr(out.claimed_brands, 8, 120),
    social_profile: social ? {
      platform: safeText(social.platform, 80),
      username: safeText(social.username, 120),
      display_name: safeText(social.display_name, 160),
      verification_evidence: safeText(social.verification_evidence, 240)
    } : null,
    suspicious_signals: signals
  };
}

function cleanJsonText(text) {
  return String(text || '').replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();
}

function normalizeRisk(value) {
  const risk = String(value || '').toLowerCase();
  return Object.prototype.hasOwnProperty.call(RISK_ORDER, risk) ? risk : 'unknown';
}

function riskFromBody(body) {
  if (!body || typeof body !== 'object') return 'unknown';
  const values = [
    body.safety && body.safety.status,
    body.analysis && body.analysis.risk,
    body.risk,
    body.profileRisk,
    body.socialProfile && body.socialProfile.risk,
    body.socialProfile && body.socialProfile.riskLevel
  ];
  for (const value of values) {
    const risk = normalizeRisk(value);
    if (risk !== 'unknown') return risk;
  }
  return 'unknown';
}

function captureHandler(handler, body) {
  return new Promise((resolve) => {
    let done = false;
    const finish = (status, payload) => {
      if (done) return;
      done = true;
      resolve({ status, body: payload });
    };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(key, value) { this.headers[String(key).toLowerCase()] = value; return this; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload); return this; },
      end(payload) {
        let parsed = payload;
        if (typeof payload === 'string') {
          try { parsed = JSON.parse(payload); } catch (_) {}
        }
        finish(this.statusCode, parsed);
        return this;
      }
    };
    const req = { method: 'POST', body };
    Promise.resolve(handler(req, res)).catch(err => finish(500, { error: err && err.message ? err.message : 'Check failed' }));
  });
}

function socialProfileTarget(profile) {
  if (!profile || typeof profile !== 'object') return '';
  const username = safeText(profile.username, 120).replace(/^@/, '').trim();
  if (!username) return '';
  const platform = safeText(profile.platform, 80).toLowerCase();
  if (platform.includes('instagram')) return `https://www.instagram.com/${username}/`;
  if (platform.includes('tiktok')) return `https://www.tiktok.com/@${username}`;
  if (platform === 'x' || platform.includes('twitter')) return `https://x.com/${username}`;
  if (platform.includes('facebook')) return `https://www.facebook.com/${username}`;
  if (platform.includes('telegram')) return `https://t.me/${username}`;
  return `@${username}`;
}

function looksCrypto(value) {
  const v = String(value || '').trim();
  return /^0x[a-fA-F0-9]{40}$/.test(v) ||
    /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v) ||
    /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v) ||
    /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v) ||
    /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v);
}

function evidenceCandidates(analysis) {
  const out = [];
  const seen = new Set();
  const add = (type, value, source) => {
    const cleaned = String(value || '').trim().slice(0, 1200);
    if (!cleaned) return;
    const key = `${type}:${cleaned.toLowerCase()}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push({ type, value: cleaned, source });
  };
  for (const url of analysis.urls || []) add('url', url, 'screenshot');
  for (const qr of analysis.qr_values || []) {
    if (/^https?:\/\//i.test(qr)) add('url', qr, 'qr');
    else if (looksCrypto(qr)) add('crypto', qr, 'qr');
  }
  for (const email of analysis.emails || []) add('email', email, 'screenshot');
  const social = socialProfileTarget(analysis.social_profile);
  if (social) add('social-profile', social, 'screenshot');
  const visible = String(analysis.visible_text || '');
  for (const token of visible.split(/\s+/)) {
    const cleaned = token.replace(/^[('"\[]+|[)'",.;!?\]]+$/g, '');
    if (looksCrypto(cleaned)) add('crypto', cleaned, 'screenshot-text');
  }
  return out.slice(0, MAX_CROSS_CHECKS);
}

async function runCandidate(candidate) {
  if (candidate.type === 'url') return captureHandler(checkHandler, { url: candidate.value });
  if (candidate.type === 'email') return captureHandler(emailHandler, { input: candidate.value });
  if (candidate.type === 'crypto') return captureHandler(cryptoHandler, { input: candidate.value });
  if (candidate.type === 'social-profile') return captureHandler(socialProfileHandler, { input: candidate.value });
  return { status: 200, body: {} };
}

function childSummary(candidate, result) {
  const body = result && result.body && typeof result.body === 'object' ? result.body : {};
  const risk = riskFromBody(body);
  const summary = safeText(
    body.summary ||
    (body.safety && body.safety.summary) ||
    (body.socialProfile && body.socialProfile.summary),
    260
  );
  return {
    type: candidate.type,
    source: candidate.source,
    value: safeText(candidate.value, 220),
    risk,
    status: result.status,
    summary
  };
}

async function crossCheckAnalysis(analysis) {
  const candidates = evidenceCandidates(analysis);
  if (!candidates.length) return { analysis, checks: [] };
  const results = await Promise.all(candidates.map(runCandidate));
  const checks = results.map((result, i) => childSummary(candidates[i], result));
  const strongest = checks.reduce((best, item) => RISK_ORDER[item.risk] > RISK_ORDER[best.risk] ? item : best, { risk: 'unknown' });
  const currentRisk = normalizeRisk(analysis.risk);
  if (strongest.risk && RISK_ORDER[strongest.risk] > RISK_ORDER[currentRisk]) {
    const merged = { ...analysis, risk: strongest.risk };
    merged.summary = strongest.risk === 'high'
      ? 'A high-risk indicator was found when the screenshot evidence was cross-checked.'
      : 'Additional checks found evidence that should be verified before continuing.';
    merged.recommended_action = strongest.risk === 'high'
      ? 'Do not click, reply, pay or sign in. Verify the sender or service through an official channel.'
      : 'Verify the sender, destination or request independently before continuing.';
    const signals = Array.isArray(merged.suspicious_signals) ? [...merged.suspicious_signals] : [];
    signals.unshift({ type: 'cross_check', detail: `A detected ${strongest.type} returned a ${strongest.risk}-risk result.` });
    merged.suspicious_signals = signals.slice(0, 8);
    return { analysis: merged, checks };
  }
  return { analysis, checks };
}

async function callGemini({ key, model, image, prompt, signal }) {
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'X-goog-api-key': key
    },
    body: JSON.stringify({
      contents: [{ parts: [
        { inline_data: { mime_type: image.mimeType, data: image.data } },
        { text: prompt }
      ] }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 1400
      }
    }),
    signal
  });
  const data = await r.json().catch(() => null);
  return { r, data };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed' });

  const image = parseDataUrl(req.body && req.body.image);
  if (!image) return json(res, 400, { error: 'Use a JPEG, PNG or WebP image up to 4 MB.' });

  const key = process.env.GEMINI_API_KEY;
  if (!key) return json(res, 503, { error: 'Image analysis is not configured yet.' });

  const prompt = `You are a security extraction component for Can I Share This?. Analyze this screenshot or photo for scam, phishing and social-profile impersonation indicators. Do not claim certainty and do not identify a person biometrically. Extract only evidence visible in the image. Detect visible text, URLs, email addresses, phone numbers, QR-code contents if readable, brands or organizations being claimed, requests for login/payment/crypto/download, urgency, threats, impersonation, brand/domain mismatch, attempts to move the conversation to Telegram or WhatsApp, requests for passwords/codes/documents, and fake-looking verification symbols placed in a display name or biography. If a social profile or direct-message interface is visible, extract the platform, visible @username, display name and what visible evidence exists for verification; do not assume a checkmark is genuine platform verification. Return JSON only with this exact shape: {"risk":"low|caution|high|unknown","confidence":0.0,"summary":"short plain-language summary","recommended_action":"short action","visible_text":"important visible text","urls":[],"emails":[],"phones":[],"qr_values":[],"claimed_brands":[],"social_profile":{"platform":"","username":"","display_name":"","verification_evidence":""},"suspicious_signals":[{"type":"short_type","detail":"specific visible evidence"}]}. For a visible social profile, use cautious result language: no obvious impersonation signs, profile needs verification, or high impersonation risk. Never state that a profile is definitely fake. If the image is unrelated or unreadable, use risk unknown and social_profile null. Never invent a URL, email, phone number, QR value, brand, username or verification status.`;

  const preferred = process.env.GEMINI_MODEL || 'gemini-flash-latest';
  const models = [...new Set([preferred, 'gemini-2.5-flash-lite'])];
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);

  try {
    let lastStatus = 502;
    let lastMessage = '';
    for (const model of models) {
      const { r, data } = await callGemini({ key, model, image, prompt, signal: controller.signal });
      if (!r.ok) {
        lastStatus = r.status;
        lastMessage = data && data.error && data.error.message ? String(data.error.message) : '';
        console.error('Gemini image check failed', model, r.status, lastMessage);
        if (r.status === 429) return json(res, 429, { error: 'Image analysis quota is temporarily exhausted.' });
        if (![400, 403, 404].includes(r.status)) break;
        continue;
      }

      const text = data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts
        ? data.candidates[0].content.parts.map(p => p.text || '').join('') : '';
      let parsed;
      try { parsed = JSON.parse(cleanJsonText(text)); } catch (_) {
        lastStatus = 502;
        lastMessage = 'Unreadable JSON response';
        continue;
      }
      const normalized = normalizeOutput(parsed);
      const enriched = await crossCheckAnalysis(normalized);
      return json(res, 200, {
        ok: true,
        analysis: enriched.analysis,
        crossChecks: enriched.checks,
        orchestrated: true,
        provider: 'gemini',
        model
      });
    }

    return json(res, lastStatus === 401 || lastStatus === 403 ? 503 : 502, {
      error: lastStatus === 401 || lastStatus === 403
        ? 'Image analysis authentication is not available.'
        : 'Image analysis is temporarily unavailable.'
    });
  } catch (err) {
    if (err && err.name === 'AbortError') return json(res, 504, { error: 'Image analysis timed out.' });
    console.error('Image check error', err);
    return json(res, 502, { error: 'Image analysis is temporarily unavailable.' });
  } finally {
    clearTimeout(timer);
  }
};
