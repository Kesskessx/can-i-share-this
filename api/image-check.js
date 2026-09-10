'use strict';

const checkHandler = require('./check');
const emailHandler = require('./email-check');
const cryptoHandler = require('./crypto-check');
const messageHandler = require('./message-check');

const RISK_ORDER = { unknown: 0, low: 1, caution: 2, high: 3 };

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('cache-control', 'no-store, max-age=0');
  res.end(JSON.stringify(body));
}

function safeText(value, max = 4000) {
  return typeof value === 'string' ? value.slice(0, max) : '';
}

function unique(values, max = 10) {
  return [...new Set((Array.isArray(values) ? values : []).map(v => String(v || '').trim()).filter(Boolean))].slice(0, max);
}

function extractUrls(text) {
  return unique((String(text || '').match(/https?:\/\/[^\s<>"')\]]+/gi) || []).map(v => v.replace(/[.,;!?]+$/g, '')));
}

function extractEmails(text) {
  return unique(String(text || '').match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi) || []);
}

function extractPhones(text) {
  return unique(String(text || '').match(/(?:\+?\d[\d\s().-]{7,}\d)/g) || []);
}

function looksCrypto(value) {
  const v = String(value || '').trim();
  return /^0x[a-fA-F0-9]{40}$/.test(v) || /^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v) || /^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v) || /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v) || /^[13][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v);
}

function extractCrypto(text) {
  return unique(String(text || '').split(/\s+/).map(v => v.replace(/^[('"\[]+|[)'",.;!?\]]+$/g, '')).filter(looksCrypto), 6);
}

function captureHandler(handler, body) {
  return new Promise(resolve => {
    let done = false;
    const finish = (status, payload) => { if (!done) { done = true; resolve({ status, body: payload }); } };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) { this.headers[String(k).toLowerCase()] = v; return this; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload); return this; },
      end(payload) {
        let parsed = payload;
        if (typeof payload === 'string') { try { parsed = JSON.parse(payload); } catch (_) {} }
        finish(this.statusCode, parsed); return this;
      }
    };
    Promise.resolve(handler({ method: 'POST', body }, res)).catch(err => finish(500, { error: err && err.message ? err.message : 'Check failed' }));
  });
}

function childRisk(body) {
  if (!body || typeof body !== 'object') return 'unknown';
  const values = [body.risk, body.analysis && body.analysis.risk, body.safety && body.safety.status, body.profileRisk];
  for (const v of values) if (Object.prototype.hasOwnProperty.call(RISK_ORDER, String(v || '').toLowerCase())) return String(v).toLowerCase();
  return 'unknown';
}

function strongestRisk(items, fallback) {
  return items.reduce((best, item) => RISK_ORDER[item.risk] > RISK_ORDER[best] ? item.risk : best, fallback);
}

function keywordSignals(text) {
  const raw = String(text || '');
  const t = raw.toLowerCase();
  const groups = [
    ['credentials', /\b(password|passcode|verification code|security code|otp|2fa|login code|seed phrase|recovery phrase)\b/i, 3, 'Requests credentials, codes or recovery information.'],
    ['payment', /\b(pay now|payment required|send money|bank transfer|wire transfer|gift card|crypto payment|bitcoin payment|usdt|wallet address)\b/i, 2, 'Requests payment or transfer of funds.'],
    ['urgency', /\b(urgent|immediately|act now|within 24 hours|final warning|account suspended|account locked|limited time)\b/i, 1, 'Uses urgency or account-threat language.'],
    ['impersonation', /\b(customer support|support team|security team|fraud department|official support|administrator)\b/i, 1, 'Claims to represent support, security or an administrator.'],
    ['remote-access', /\b(anydesk|teamviewer|remote desktop|screen share|install this app|download this app)\b/i, 3, 'Requests remote access or installation of software.'],
    ['prize', /\b(you won|winner|prize|giveaway|claim your reward|lottery)\b/i, 2, 'Contains prize or reward language commonly used in scams.'],
    ['move-channel', /\b(contact me on telegram|message me on whatsapp|move to telegram|move to whatsapp)\b/i, 1, 'Attempts to move the conversation to another messaging service.']
  ];
  const signals = [];
  let score = 0;
  for (const [type, re, weight, detail] of groups) {
    if (re.test(raw)) { score += weight; signals.push({ type, detail }); }
  }
  if (/\b(dear customer|dear user|valued customer)\b/i.test(t)) { score += 1; signals.push({ type: 'generic-greeting', detail: 'Uses a generic recipient greeting.' }); }
  return { score, signals };
}

async function crossChecks(urls, emails, crypto, visibleText) {
  const tasks = [];
  for (const url of urls.slice(0, 2)) tasks.push({ type: 'url', value: url, promise: captureHandler(checkHandler, { url }) });
  for (const email of emails.slice(0, 1)) tasks.push({ type: 'email', value: email, promise: captureHandler(emailHandler, { input: email }) });
  for (const address of crypto.slice(0, 1)) tasks.push({ type: 'crypto', value: address, promise: captureHandler(cryptoHandler, { input: address }) });
  if (!tasks.length && visibleText) tasks.push({ type: 'message', value: visibleText.slice(0, 1200), promise: captureHandler(messageHandler, { input: visibleText, message: visibleText }) });
  const settled = await Promise.all(tasks.map(async t => ({ type: t.type, value: t.value, result: await t.promise })));
  return settled.map(x => ({ type: x.type, value: safeText(x.value, 220), risk: childRisk(x.result.body), status: x.result.status }));
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed' });
  let body = req.body || {};
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (_) { body = {}; } }

  const visibleText = safeText(body.visibleText || body.text || '', 12000).trim();
  const qrValues = unique(body.qrValues || body.qr_values || (body.inputSource === 'qr' && body.input ? [body.input] : []), 6);
  const combined = [visibleText, ...qrValues].join('\n');
  const urls = unique([...extractUrls(combined), ...qrValues.filter(v => /^https?:\/\//i.test(v))]);
  const emails = extractEmails(combined);
  const phones = extractPhones(combined);
  const crypto = extractCrypto(combined);

  if (!visibleText && !qrValues.length) {
    return json(res, 200, {
      ok: true,
      provider: 'local-rules',
      model: null,
      analysis: {
        risk: 'unknown', confidence: 0.1,
        summary: 'No readable text or QR code was supplied by the local image extractor.',
        recommended_action: 'Do not rely on this image result. Check any visible link, sender or request separately.',
        visible_text: '', urls: [], emails: [], phones: [], qr_values: [], claimed_brands: [], social_profile: null,
        suspicious_signals: []
      },
      crossChecks: [], orchestrated: true
    });
  }

  const heuristics = keywordSignals(combined);
  const checks = await crossChecks(urls, emails, crypto, visibleText);
  let risk = heuristics.score >= 5 ? 'high' : heuristics.score >= 2 ? 'caution' : 'low';
  risk = strongestRisk(checks, risk);
  if (!visibleText && qrValues.length && risk === 'low') risk = 'unknown';

  const signals = [...heuristics.signals];
  checks.filter(c => c.risk === 'high' || c.risk === 'caution').forEach(c => signals.unshift({ type: 'cross-check', detail: `Detected ${c.type} returned ${c.risk} risk.` }));

  const summary = risk === 'high'
    ? 'The locally extracted image evidence contains high-risk scam or phishing indicators.'
    : risk === 'caution'
      ? 'The locally extracted image evidence contains indicators that should be verified before continuing.'
      : risk === 'low'
        ? 'No obvious high-risk scam indicators were found in the text and QR evidence extracted from this image.'
        : 'The image evidence was too limited for a reliable safety conclusion.';

  const recommended = risk === 'high'
    ? 'Do not click, reply, pay, sign in or share a code. Verify the sender or service through an official channel.'
    : risk === 'caution'
      ? 'Verify the sender, destination and request independently before continuing.'
      : risk === 'low'
        ? 'Continue cautiously and verify unexpected requests before sharing sensitive information.'
        : 'Check any visible link, sender or request separately before taking action.';

  return json(res, 200, {
    ok: true,
    provider: 'local-rules',
    model: null,
    analysis: {
      risk,
      confidence: risk === 'unknown' ? 0.2 : Math.min(0.86, 0.48 + heuristics.score * 0.06 + checks.length * 0.05),
      summary,
      recommended_action: recommended,
      visible_text: visibleText,
      urls,
      emails,
      phones,
      qr_values: qrValues,
      claimed_brands: [],
      social_profile: null,
      suspicious_signals: signals.slice(0, 8)
    },
    crossChecks: checks,
    orchestrated: true
  });
};
