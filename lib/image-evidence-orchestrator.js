'use strict';

const checkHandler = require('../api/check');
const emailHandler = require('../api/email-check');
const cryptoHandler = require('../api/crypto-check');
const messageHandler = require('../api/message-check');
const socialProfileHandler = require('./social-profile-safety');
const { verifyWebsiteSocialRelationship, extractDomainsFromText } = require('./evidence-relations');

const RANK = { unknown: 0, low: 1, caution: 2, high: 3 };
const MAX_EXTRA_CHECKS = 8;

function clean(v, max = 1200) {
  return String(v == null ? '' : v).replace(/\0/g, '').trim().slice(0, max);
}
function risk(v) {
  const x = clean(v, 30).toLowerCase();
  return Object.prototype.hasOwnProperty.call(RANK, x) ? x : 'unknown';
}
function strongest(items) {
  return (items || []).reduce((best, x) => RANK[risk(x)] > RANK[best] ? risk(x) : best, 'unknown');
}
function unique(items, keyFn, max = 20) {
  const out = [], seen = new Set();
  for (const item of items || []) {
    const key = keyFn(item);
    if (!key || seen.has(key)) continue;
    seen.add(key); out.push(item);
    if (out.length >= max) break;
  }
  return out;
}
function socialTarget(profile) {
  if (!profile || typeof profile !== 'object') return '';
  const username = clean(profile.username, 120).replace(/^@/, '');
  const platform = clean(profile.platform, 60).toLowerCase();
  if (!username) return '';
  if (platform.includes('instagram')) return `https://www.instagram.com/${username}/`;
  if (platform.includes('tiktok')) return `https://www.tiktok.com/@${username}`;
  if (platform === 'x' || platform.includes('twitter')) return `https://x.com/${username}`;
  if (platform.includes('facebook')) return `https://www.facebook.com/${username}`;
  if (platform.includes('telegram')) return `https://t.me/${username}`;
  return `@${username}`;
}
function looksCrypto(v) {
  v = clean(v, 180);
  return /^0x[a-fA-F0-9]{40}$/.test(v) || /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v) ||
    /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v) || /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v) ||
    /^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v);
}
function cryptoFromText(text) {
  return unique(String(text || '').split(/\s+/).map(x => x.replace(/^[('"\[]+|[)'",.;!?\]]+$/g, '')).filter(looksCrypto), x => x.toLowerCase(), 5);
}
function fileNames(text) {
  const re = /\b[\w()\[\]. -]{1,90}\.(?:exe|msi|msix|scr|bat|cmd|com|ps1|vbs|jar|apk|dmg|pkg|iso|img|hta|appinstaller|zip|rar|7z|pdf|docx?|xlsx?|pptx?)\b/gi;
  return unique((String(text || '').match(re) || []).map(x => clean(x, 120)), x => x.toLowerCase(), 8);
}
function accountContext(analysis) {
  const text = clean([analysis && analysis.visible_text, ...((analysis && analysis.suspicious_signals) || []).map(s => `${s && s.type || ''} ${s && s.detail || ''}`)].join(' '), 12000);
  const followers = text.match(/\b([0-9][0-9.,kKmM]*)\s+followers?\b/i);
  const following = text.match(/\b([0-9][0-9.,kKmM]*)\s+following\b/i);
  const joined = text.match(/\bjoined\s+([A-Za-z]+\s+\d{4})\b/i);
  const weakSignal = /low[_ -]?account[_ -]?metrics|minimal account history|few followers|only one follower|new account|recent account|account age/i.test(text);
  return {
    followers: followers ? followers[1] : null,
    following: following ? following[1] : null,
    joined: joined ? joined[1] : null,
    maturity: weakSignal || joined ? 'limited' : 'unknown',
    note: weakSignal || joined ? 'Limited account history is context, not proof of impersonation.' : null
  };
}
function weakAccountOnly(analysis) {
  if (!analysis || risk(analysis.risk) !== 'caution') return false;
  const signals = Array.isArray(analysis.suspicious_signals) ? analysis.suspicious_signals : [];
  if (!signals.length) return false;
  const weak = /low[_ -]?account[_ -]?metrics|minimal account history|few followers|follower|following|new account|recent account|account age|joined/i;
  return signals.every(s => weak.test(`${s && s.type || ''} ${s && s.detail || ''}`));
}
function normalizeWeakAccountRisk(analysis) {
  if (!weakAccountOnly(analysis)) return analysis;
  return {
    ...analysis,
    risk: 'low',
    summary: 'No strong impersonation sign was found in the visible evidence. The account appears new or has limited public history.',
    recommended_action: 'Treat the account as new, not automatically suspicious. Verify its website and official cross-links before sharing sensitive information.',
    suspicious_signals: (analysis.suspicious_signals || []).map(s => ({ ...s, context_only: true }))
  };
}

function capture(handler, body) {
  return new Promise(resolve => {
    let done = false;
    const finish = (status, payload) => { if (!done) { done = true; resolve({ status, body: payload }); } };
    const res = {
      statusCode: 200, headers: {},
      setHeader(k, v) { this.headers[String(k).toLowerCase()] = v; return this; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload); return this; },
      end(payload) { let p = payload; if (typeof p === 'string') { try { p = JSON.parse(p); } catch (_) {} } finish(this.statusCode, p); return this; }
    };
    const req = { method: 'POST', body };
    Promise.resolve(handler(req, res)).catch(err => finish(500, { error: err && err.message ? err.message : 'Check failed' }));
  });
}
function riskFromBody(body) {
  if (!body || typeof body !== 'object') return 'unknown';
  return strongest([
    body.safety && body.safety.status,
    body.analysis && body.analysis.risk,
    body.risk,
    body.profileRisk,
    body.socialProfile && (body.socialProfile.risk || body.socialProfile.riskLevel)
  ]);
}
function summaryFromBody(body) {
  return clean(body && (body.summary || (body.safety && body.safety.verdict) || (body.analysis && body.analysis.summary) || (body.socialProfile && body.socialProfile.summary)), 320);
}
function candidateKey(x) { return `${x.type}:${clean(x.value, 1000).toLowerCase()}`; }

function extractEvidence(result) {
  const analysis = result && result.analysis && typeof result.analysis === 'object' ? result.analysis : {};
  const visible = clean(analysis.visible_text, 12000);
  const candidates = [];
  const add = (type, value, source, priority) => {
    value = clean(value, type === 'message' ? 6000 : 1200);
    if (!value) return;
    candidates.push({ type, value, source, priority });
  };
  for (const u of analysis.urls || []) add('url', u, 'screenshot', 10);
  for (const q of analysis.qr_values || []) {
    if (/^https?:\/\//i.test(q)) add('url', q, 'qr', 11);
    else if (looksCrypto(q)) add('crypto', q, 'qr', 8);
    else if (/^[a-z0-9.-]+\.[a-z]{2,24}(?:\/|$)/i.test(q)) add('url', `https://${q}`, 'qr-domain', 9);
  }
  for (const e of analysis.emails || []) add('email', e, 'screenshot', 9);
  const social = socialTarget(analysis.social_profile);
  if (social) add('social-profile', social, 'screenshot', 12);
  for (const x of cryptoFromText(visible)) add('crypto', x, 'screenshot-text', 7);
  const knownUrlDomains = new Set((analysis.urls || []).map(u => { try { return new URL(u).hostname.toLowerCase().replace(/^www\./, ''); } catch (_) { return ''; } }));
  for (const d of extractDomainsFromText(visible)) if (!knownUrlDomains.has(d)) add('url', `https://${d}/`, 'visible-domain', 8);
  if (visible.length >= 20) add('message', visible, 'visible-text', 6);

  const deduped = unique(candidates.sort((a, b) => b.priority - a.priority), candidateKey, 20);
  const quotas = { 'social-profile': 1, url: 3, email: 2, crypto: 1, message: 1 };
  const used = {};
  const selected = [];
  for (const x of deduped) {
    if (!quotas[x.type] || (used[x.type] || 0) >= quotas[x.type]) continue;
    used[x.type] = (used[x.type] || 0) + 1; selected.push(x);
    if (selected.length >= MAX_EXTRA_CHECKS) break;
  }
  const websites = unique(deduped.filter(x => x.type === 'url').map(x => x.value), x => { try { return new URL(x).hostname.toLowerCase(); } catch (_) { return ''; } }, 5);
  return {
    candidates: selected,
    websites,
    socialProfile: analysis.social_profile || null,
    elements: {
      urls: unique((analysis.urls || []).map(String), x => x.toLowerCase(), 10),
      domains: extractDomainsFromText(visible),
      emails: unique((analysis.emails || []).map(String), x => x.toLowerCase(), 8),
      phones: unique((analysis.phones || []).map(String), x => x, 8),
      crypto: cryptoFromText([visible, ...(analysis.qr_values || [])].join(' ')),
      qr: unique((analysis.qr_values || []).map(String), x => x, 8),
      files: fileNames(visible),
      socialProfiles: social ? [social] : [],
      claimedBrands: unique((analysis.claimed_brands || []).map(String), x => x.toLowerCase(), 8)
    },
    account: accountContext(analysis)
  };
}

async function runCandidate(candidate) {
  if (candidate.type === 'url') return capture(checkHandler, { url: candidate.value });
  if (candidate.type === 'email') return capture(emailHandler, { input: candidate.value });
  if (candidate.type === 'crypto') return capture(cryptoHandler, { input: candidate.value });
  if (candidate.type === 'social-profile') return capture(socialProfileHandler, { input: candidate.value });
  if (candidate.type === 'message') return capture(messageHandler, { input: candidate.value, message: candidate.value });
  return { status: 200, body: {} };
}
function child(candidate, scan) {
  const body = scan && scan.body && typeof scan.body === 'object' ? scan.body : {};
  let display = clean(candidate.value, 260);
  if (candidate.type === 'email') display = display.replace(/^[^@]+@/, '[mailbox]@');
  if (candidate.type === 'crypto') display = '[crypto address]';
  return {
    type: candidate.type, source: candidate.source, value: display,
    risk: riskFromBody(body), status: scan.status, summary: summaryFromBody(body),
    finalUrl: clean(body.finalUrl, 400) || null,
    claimedBrand: clean(body.socialProfile && body.socialProfile.claimedBrand, 120) || null,
    profileExternalDomains: Array.isArray(body.socialProfile && body.socialProfile.profileData && body.socialProfile.profileData.externalDomains)
      ? body.socialProfile.profileData.externalDomains.slice(0, 5) : []
  };
}

async function orchestrateImageResult(baseResult) {
  if (!baseResult || typeof baseResult !== 'object' || !baseResult.analysis) return baseResult;
  const result = { ...baseResult, analysis: normalizeWeakAccountRisk(baseResult.analysis) };
  const evidence = extractEvidence(result);
  const existing = Array.isArray(result.crossChecks) ? result.crossChecks : [];
  const existingKeys = new Set(existing.map(x => `${clean(x.type, 50)}:${clean(x.value, 1000).toLowerCase()}`));
  const missing = evidence.candidates.filter(x => !existingKeys.has(candidateKey(x)));

  const [scanSettled, relationships] = await Promise.all([
    Promise.allSettled(missing.map(runCandidate)),
    verifyWebsiteSocialRelationship({ websites: evidence.websites, socialProfile: evidence.socialProfile })
  ]);
  const extra = scanSettled.map((entry, i) => entry.status === 'fulfilled'
    ? child(missing[i], entry.value)
    : { type: missing[i].type, source: missing[i].source, value: clean(missing[i].value, 220), risk: 'unknown', status: 500, summary: 'This extracted element could not be checked.' });
  const allChecks = unique([...existing, ...extra], x => `${clean(x.type, 50)}:${clean(x.value, 1000).toLowerCase()}`, 12);
  const checkRisk = strongest(allChecks.map(x => x.risk));
  const currentRisk = risk(result.analysis.risk);
  let analysis = result.analysis;
  if (RANK[checkRisk] > RANK[currentRisk]) {
    analysis = {
      ...analysis,
      risk: checkRisk,
      summary: checkRisk === 'high'
        ? 'One or more elements extracted from the screenshot produced a high-risk result when checked independently.'
        : 'One or more elements extracted from the screenshot need independent verification.',
      recommended_action: checkRisk === 'high'
        ? 'Do not click, reply, pay, sign in or send codes. Verify the claimed service through an official channel.'
        : 'Verify the extracted destination, sender or profile independently before continuing.',
      suspicious_signals: [
        { type: 'multi_element_cross_check', detail: `${allChecks.filter(x => ['high','caution'].includes(risk(x.risk))).length} extracted element(s) raised a caution or high-risk result.` },
        ...(analysis.suspicious_signals || [])
      ].slice(0, 10)
    };
  }

  return {
    ...result,
    analysis,
    crossChecks: allChecks,
    relationshipChecks: relationships,
    detectedElements: evidence.elements,
    accountContext: evidence.account,
    orchestrated: true,
    orchestration: {
      version: '3.0',
      extractedElementCount: Object.values(evidence.elements).reduce((n, arr) => n + (Array.isArray(arr) ? arr.length : 0), 0),
      specializedChecksRun: allChecks.length,
      relationshipChecksRun: relationships.length,
      scanners: unique(allChecks.map(x => x.type), x => x, 10),
      contextualOnly: [
        ...(evidence.elements.phones.length ? ['Phone numbers are analyzed in message context; ownership is not inferred.'] : []),
        ...(evidence.elements.files.length ? ['File names visible in a screenshot can be assessed for extension/context, but the file contents are not scanned unless the file itself is uploaded.'] : [])
      ]
    }
  };
}

module.exports = { orchestrateImageResult, extractEvidence, normalizeWeakAccountRisk, weakAccountOnly };
