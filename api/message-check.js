const checkHandler = require('./check');
const emailHandler = require('./email-check');

function cleanText(v, max = 5000) { return String(v || '').trim().slice(0, max); }
function cleanJsonText(text) { return String(text || '').replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim(); }
function riskRank(v) { return v === 'high' ? 3 : v === 'caution' ? 2 : v === 'low' ? 1 : 0; }
function scoreFor(v) { return v === 'high' ? 85 : v === 'caution' ? 50 : v === 'low' ? 15 : 0; }
function extractUrls(text) { return [...new Set((text.match(/https?:\/\/[^\s<>"']+/gi) || []).map(v => v.replace(/[),.;!?]+$/, '')))].slice(0, 5); }
function extractEmails(text) { return [...new Set((text.match(/[^\s@]+@[^\s@]+\.[^\s@]+/g) || []).map(v => v.replace(/[),.;!?]+$/, '')))].slice(0, 5); }
function extractPhones(text) { return [...new Set((text.match(/(?:\+?\d[\d .()\-]{7,}\d)/g) || []).map(v => v.trim()))].slice(0, 5); }

function heuristicSignals(text) {
  const tests = [
    [/\b(urgent|urgently|immediately|within 24 hours|act now|last warning|suspend(?:ed|ed today)?|expire(?:s|d)? today)\b/i, 'urgency', 'The message uses urgency or deadline pressure.'],
    [/\b(password|passcode|one[- ]?time code|otp|verification code|recovery phrase|seed phrase|private key)\b/i, 'credentials', 'The message asks for authentication or secret information.'],
    [/\b(pay|payment|fee|invoice|bank transfer|wire|gift card|crypto|bitcoin|wallet|deposit|refund)\b/i, 'payment', 'The message contains payment or money-related language.'],
    [/\b(click|tap|open|download|install|verify|confirm|login|log in|sign in)\b/i, 'action_request', 'The message asks the recipient to take an action.'],
    [/\b(do not tell|keep this confidential|secret|don't contact|do not contact)\b/i, 'secrecy', 'The message asks for secrecy or discourages independent verification.']
  ];
  return tests.filter(([re]) => re.test(text)).map(([, type, detail]) => ({ type, detail }));
}

function captureHandler(handler, body) {
  return new Promise((resolve) => {
    let done = false;
    const finish = (status, payload) => { if (!done) { done = true; resolve({ status, body: payload }); } };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) { this.headers[String(k).toLowerCase()] = v; return this; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, payload); return this; },
      end(payload) { try { finish(this.statusCode, JSON.parse(payload)); } catch { finish(this.statusCode, payload); } return this; }
    };
    const req = { method: 'POST', body };
    Promise.resolve(handler(req, res)).catch(err => finish(500, { error: err && err.message ? err.message : 'Check failed' }));
  });
}

async function geminiMessageAnalysis(text) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) return null;
  const model = process.env.GEMINI_MODEL || 'gemini-flash-latest';
  const prompt = `You are the message-risk interpretation component for Can I Share This?. Analyze the message below for scam/phishing/social-engineering indicators. Do not claim certainty and do not infer facts not present. Consider urgency, impersonation, credential requests, payment requests, secrecy, threats, suspicious links, brand/domain mismatch, unexpected downloads, crypto requests and manipulation. Return JSON only: {"risk":"low|caution|high|unknown","confidence":0.0,"summary":"one short sentence","recommended_action":"one short action","claimed_brands":[],"suspicious_signals":[{"type":"short_type","detail":"specific evidence from the message"}]}. Keep at most 3 suspicious_signals. Message:\n${text}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'X-goog-api-key': key },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.1, maxOutputTokens: 700 } }),
      signal: controller.signal
    });
    if (!r.ok) return null;
    const data = await r.json().catch(() => null);
    const raw = data?.candidates?.[0]?.content?.parts?.map(p => p.text || '').join('') || '';
    const parsed = JSON.parse(cleanJsonText(raw));
    return {
      risk: ['low','caution','high','unknown'].includes(parsed.risk) ? parsed.risk : 'unknown',
      confidence: Number.isFinite(parsed.confidence) ? Math.max(0, Math.min(1, parsed.confidence)) : null,
      summary: cleanText(parsed.summary, 350),
      recommended_action: cleanText(parsed.recommended_action, 300),
      claimed_brands: Array.isArray(parsed.claimed_brands) ? parsed.claimed_brands.filter(x => typeof x === 'string').slice(0, 5) : [],
      suspicious_signals: Array.isArray(parsed.suspicious_signals) ? parsed.suspicious_signals.slice(0, 3).map(s => ({ type: cleanText(s?.type, 70) || 'signal', detail: cleanText(s?.detail, 250) })).filter(s => s.detail) : []
    };
  } catch (_) { return null; } finally { clearTimeout(timer); }
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const body = typeof req.body === 'string' ? (() => { try { return JSON.parse(req.body); } catch { return {}; } })() : (req.body || {});
  const message = cleanText(body.input || body.message, 5000);
  if (!message) return res.status(400).json({ error: 'Message required' });

  const urls = extractUrls(message), emails = extractEmails(message), phones = extractPhones(message);
  const heuristics = heuristicSignals(message);
  const aiPromise = geminiMessageAnalysis(message);
  let technical = null;
  if (urls[0]) technical = (await captureHandler(checkHandler, { url: urls[0] })).body;
  else if (emails[0]) technical = (await captureHandler(emailHandler, { input: emails[0] })).body;
  const ai = await aiPromise;

  const techRisk = technical?.safety?.status || 'unknown';
  const aiRisk = ai?.risk || 'unknown';
  let risk = riskRank(techRisk) >= riskRank(aiRisk) ? techRisk : aiRisk;
  if (risk === 'unknown' && heuristics.length >= 2) risk = 'caution';
  if (risk === 'low' && heuristics.some(s => ['credentials','payment','secrecy'].includes(s.type))) risk = 'caution';

  const mergedSignals = [];
  for (const s of (technical?.safety?.signals || [])) {
    const detail = cleanText(s?.title || s?.detail, 220); if (detail && !mergedSignals.some(x => x.title === detail)) mergedSignals.push({ title: detail });
  }
  for (const s of (ai?.suspicious_signals || heuristics)) {
    const detail = cleanText(s?.detail, 220); if (detail && !mergedSignals.some(x => x.title === detail)) mergedSignals.push({ title: detail });
  }

  const score = Math.max(Number(technical?.safety?.riskScore || 0), scoreFor(aiRisk), risk === 'caution' ? 45 : risk === 'high' ? 85 : 10);
  const summary = ai?.summary || (risk === 'high' ? 'The message contains strong scam or phishing warning signs.' : risk === 'caution' ? 'The message contains signs that should be verified before acting.' : risk === 'low' ? 'No obvious scam pattern was found in the message.' : 'The message could not be fully assessed.');
  const recommended = ai?.recommended_action || (risk === 'high' ? 'Do not follow the request. Verify the sender through an official channel.' : risk === 'caution' ? 'Verify the sender and any destination independently before continuing.' : 'Continue cautiously, especially if the request was unexpected.');

  return res.status(200).json({
    inputType: 'message',
    message: { urls, emails, phones, claimedBrands: ai?.claimed_brands || [], aiAssisted: Boolean(ai) },
    technicalCheck: technical ? { inputType: technical.inputType || (urls[0] ? 'url' : 'email'), finalUrl: technical.finalUrl, finalHost: technical.finalHost, safety: technical.safety } : null,
    safety: { status: risk, riskScore: Math.min(100, Math.round(score)), verdict: risk === 'high' ? 'DANGEROUS' : risk === 'caution' ? 'CAUTION' : risk === 'low' ? 'SAFE' : 'UNKNOWN', signals: mergedSignals.slice(0, 3), checksPerformed: ['Message context analysis', ...(technical ? ['Extracted entity technical check'] : [])] },
    summary,
    recommendedAction: recommended
  });
};
