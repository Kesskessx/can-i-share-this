const analyzeHandler = require('./analyze');

const MAX_CHILD_CHECKS = 3;
const RISK_ORDER = { unknown: 0, low: 1, caution: 2, high: 3 };

function clean(value, max = 500) {
  return String(value == null ? '' : value).replace(/\u0000/g, '').trim().slice(0, max);
}

function normalizeRisk(value) {
  const risk = clean(value, 20).toLowerCase();
  return Object.prototype.hasOwnProperty.call(RISK_ORDER, risk) ? risk : 'unknown';
}

function riskFromBody(body) {
  if (!body || typeof body !== 'object') return 'unknown';
  const candidates = [
    body.safety && body.safety.status,
    body.analysis && body.analysis.risk,
    body.risk,
    body.profileRisk,
    body.socialProfile && body.socialProfile.risk,
    body.socialProfile && body.socialProfile.riskLevel
  ];
  for (const value of candidates) {
    const risk = normalizeRisk(value);
    if (risk !== 'unknown') return risk;
  }
  return 'unknown';
}

function highestRisk(values) {
  return values.map(normalizeRisk).reduce((best, risk) => RISK_ORDER[risk] > RISK_ORDER[best] ? risk : best, 'unknown');
}

function verdictFor(risk) {
  return risk === 'high' ? 'DANGEROUS' : risk === 'caution' ? 'CAUTION' : risk === 'low' ? 'SAFE' : 'UNKNOWN';
}

function captureHandler(handler, body) {
  return new Promise((resolve) => {
    let done = false;
    const finish = (status, payload, headers = {}) => {
      if (done) return;
      done = true;
      resolve({ status, body: payload, headers });
    };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(key, value) { this.headers[String(key).toLowerCase()] = value; return this; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload, this.headers); return this; },
      end(payload) {
        let parsed = payload;
        if (typeof payload === 'string') {
          try { parsed = JSON.parse(payload); } catch (_) {}
        }
        finish(this.statusCode, parsed, this.headers);
        return this;
      }
    };
    const req = { method: 'POST', body };
    Promise.resolve(handler(req, res)).catch((err) => finish(500, { error: err && err.message ? err.message : 'Scan failed' }));
  });
}

function addCandidate(list, seen, type, value, source) {
  const cleaned = clean(value, 1200);
  if (!cleaned) return;
  const key = `${type}:${cleaned.toLowerCase()}`;
  if (seen.has(key)) return;
  seen.add(key);
  list.push({ type, value: cleaned, source });
}

function looksCrypto(value) {
  const v = clean(value, 160);
  return /^0x[a-fA-F0-9]{40}$/.test(v) ||
    /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v) ||
    /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v) ||
    /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v) ||
    /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v);
}

function textCandidates(text, source = 'input') {
  const value = clean(text, 7000);
  const list = [];
  const seen = new Set();
  for (const url of (value.match(/https?:\/\/[^\s<>"']+/gi) || [])) {
    addCandidate(list, seen, 'url', url.replace(/[),.;!?]+$/, ''), source);
  }
  for (const email of (value.match(/[^\s@]+@[^\s@]+\.[^\s@]+/g) || [])) {
    addCandidate(list, seen, 'email', email.replace(/[),.;!?]+$/, ''), source);
  }
  for (const token of value.split(/\s+/)) {
    const cleaned = token.replace(/^[('"\[]+|[)'",.;!?\]]+$/g, '');
    if (looksCrypto(cleaned)) addCandidate(list, seen, 'crypto', cleaned, source);
  }
  return list;
}

function socialUrlFromImage(profile) {
  if (!profile || typeof profile !== 'object') return '';
  const username = clean(profile.username, 120).replace(/^@/, '');
  if (!username) return '';
  const platform = clean(profile.platform, 80).toLowerCase();
  if (platform.includes('instagram')) return `https://www.instagram.com/${username}/`;
  if (platform.includes('tiktok')) return `https://www.tiktok.com/@${username}`;
  if (platform === 'x' || platform.includes('twitter')) return `https://x.com/${username}`;
  if (platform.includes('facebook')) return `https://www.facebook.com/${username}`;
  if (platform.includes('telegram')) return `https://t.me/${username}`;
  return `@${username}`;
}

function imageCandidates(analysis) {
  const list = [];
  const seen = new Set();
  if (!analysis || typeof analysis !== 'object') return list;
  for (const url of Array.isArray(analysis.urls) ? analysis.urls : []) addCandidate(list, seen, 'url', url, 'screenshot');
  for (const qr of Array.isArray(analysis.qr_values) ? analysis.qr_values : []) {
    if (/^https?:\/\//i.test(clean(qr, 1200))) addCandidate(list, seen, 'url', qr, 'qr');
    else if (looksCrypto(qr)) addCandidate(list, seen, 'crypto', qr, 'qr');
  }
  for (const email of Array.isArray(analysis.emails) ? analysis.emails : []) addCandidate(list, seen, 'email', email, 'screenshot');
  const social = socialUrlFromImage(analysis.social_profile);
  if (social) addCandidate(list, seen, 'social-profile', social, 'screenshot');
  for (const extra of textCandidates(analysis.visible_text || '', 'screenshot-text')) addCandidate(list, seen, extra.type, extra.value, extra.source);
  return list;
}

function candidateInput(candidate) {
  return { input: candidate.value };
}

function summarizeChild(candidate, result) {
  const body = result && result.body && typeof result.body === 'object' ? result.body : {};
  const risk = riskFromBody(body);
  const summary = clean(
    body.summary ||
    (body.analysis && body.analysis.summary) ||
    (body.safety && body.safety.summary) ||
    (body.socialProfile && body.socialProfile.summary),
    320
  );
  return {
    type: clean(body.detectedType || candidate.type, 40),
    source: candidate.source,
    value: clean(candidate.value, 240),
    risk,
    verdict: verdictFor(risk),
    status: result.status,
    summary
  };
}

function mergePrimary(primaryBody, childChecks) {
  const body = primaryBody && typeof primaryBody === 'object' ? { ...primaryBody } : {};
  const primaryRisk = riskFromBody(body);
  const overallRisk = highestRisk([primaryRisk, ...childChecks.map(x => x.risk)]);
  const elevated = RISK_ORDER[overallRisk] > RISK_ORDER[primaryRisk];

  if (body.analysis && typeof body.analysis === 'object') {
    const analysis = { ...body.analysis };
    if (elevated) {
      analysis.risk = overallRisk;
      analysis.summary = overallRisk === 'high'
        ? 'A high-risk indicator was found when the screenshot evidence was cross-checked.'
        : 'Additional checks found evidence that should be verified before continuing.';
      analysis.recommended_action = overallRisk === 'high'
        ? 'Do not click, reply, pay or sign in. Verify the sender or service through an official channel.'
        : 'Verify the sender, destination or request independently before continuing.';
      const signals = Array.isArray(analysis.suspicious_signals) ? [...analysis.suspicious_signals] : [];
      const strongest = childChecks.find(x => x.risk === overallRisk);
      if (strongest) signals.unshift({ type: 'cross_check', detail: `A detected ${strongest.type} returned a ${overallRisk}-risk result.` });
      analysis.suspicious_signals = signals.slice(0, 8);
    }
    body.analysis = analysis;
  }

  if (body.safety && typeof body.safety === 'object' && elevated) {
    body.safety = {
      ...body.safety,
      status: overallRisk,
      verdict: verdictFor(overallRisk),
      riskScore: Math.max(Number(body.safety.riskScore || 0), overallRisk === 'high' ? 90 : overallRisk === 'caution' ? 55 : 15)
    };
  }

  body.megaScan = {
    version: '1.0',
    mode: 'automatic',
    overallRisk,
    primaryRisk,
    crossChecked: childChecks.length,
    checks: childChecks,
    note: childChecks.length
      ? 'Detected evidence was routed through the relevant existing scanners.'
      : 'The input was routed to the relevant existing scanner.'
  };
  return body;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_) { body = {}; }
  }

  const primary = await captureHandler(analyzeHandler, body);
  if (primary.status >= 400 || !primary.body || typeof primary.body !== 'object') {
    return res.status(primary.status || 500).json(primary.body || { error: 'Scan failed' });
  }

  const detectedType = clean(primary.body.detectedType, 40);
  let candidates = [];
  if (detectedType === 'image' && primary.body.analysis) {
    candidates = imageCandidates(primary.body.analysis);
  } else if (detectedType.startsWith('message')) {
    const original = clean(body.input || body.message || '', 7000);
    candidates = textCandidates(original, 'message');
  }

  const primaryValue = clean(body.input || body.url || body.email || body.address || body.message || '', 1200).toLowerCase();
  candidates = candidates.filter(c => clean(c.value, 1200).toLowerCase() !== primaryValue).slice(0, MAX_CHILD_CHECKS);

  const results = await Promise.all(candidates.map(candidate => captureHandler(analyzeHandler, candidateInput(candidate))));
  const childChecks = results.map((result, index) => summarizeChild(candidates[index], result));
  const merged = mergePrimary(primary.body, childChecks);

  return res.status(primary.status || 200).json(merged);
};
