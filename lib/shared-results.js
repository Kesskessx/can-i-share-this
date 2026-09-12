'use strict';

const crypto = require('crypto');

const VALID_ID = /^[A-Za-z0-9_-]{8,32}$/;
const VALID_VERDICTS = new Set(['low', 'caution', 'high', 'unknown']);
const VALID_CONFIDENCE = new Set(['low', 'medium', 'high', 'unknown']);
const VALID_EVENTS = new Set(['share_x', 'result_view', 'new_scan', 'new_share']);

function text(value, max = 280) {
  return String(value == null ? '' : value)
    .replace(/\0/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, max);
}

function normalizeId(value) {
  const id = text(value, 40);
  return VALID_ID.test(id) ? id : null;
}

function normalizeSummary(input) {
  const source = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
  const verdict = VALID_VERDICTS.has(text(source.verdict, 20).toLowerCase())
    ? text(source.verdict, 20).toLowerCase()
    : 'unknown';
  const confidence = VALID_CONFIDENCE.has(text(source.confidence, 20).toLowerCase())
    ? text(source.confidence, 20).toLowerCase()
    : 'unknown';

  const reasons = Array.isArray(source.reasons)
    ? source.reasons.slice(0, 3).map((reason) => ({
        title: text(reason && reason.title, 120) || 'Signal',
        detail: text(reason && reason.detail, 320)
      })).filter((reason) => reason.title || reason.detail)
    : [];

  const evidence = Array.isArray(source.evidence)
    ? source.evidence.slice(0, 5).map((item) => ({
        type: text(item && item.type, 32),
        value: text(item && item.value, 180)
      })).filter((item) => item.type && item.value)
    : [];

  const brandMismatch = Array.isArray(source.brandMismatch)
    ? source.brandMismatch.slice(0, 2).map((item) => ({
        brand: text(item && item.brand, 80),
        domain: text(item && item.domain, 180),
        role: text(item && item.role, 40)
      })).filter((item) => item.brand || item.domain)
    : [];

  return {
    schema: 2,
    verdict,
    headline: text(source.headline, 220) || 'Can I Share This? scan result',
    confidence,
    reasons,
    action: text(source.action, 360) || 'Verify independently before acting.',
    evidence,
    brandMismatch,
    note: 'Privacy-filtered shared summary. Run a fresh scan before relying on it.'
  };
}

function config() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return null;
  return { url: url.replace(/\/$/, ''), key };
}

async function request(path, options = {}) {
  const cfg = config();
  if (!cfg) throw new Error('Shared-result storage is not configured');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3000);
  try {
    const headers = {
      apikey: cfg.key,
      'content-type': 'application/json',
      ...(options.headers || {})
    };
    if (!cfg.key.startsWith('sb_secret_')) headers.authorization = `Bearer ${cfg.key}`;
    const response = await fetch(`${cfg.url}${path}`, {
      ...options,
      headers,
      signal: controller.signal
    });
    const raw = await response.text();
    let body = null;
    if (raw) {
      try { body = JSON.parse(raw); } catch (_) { body = raw; }
    }
    if (!response.ok) {
      const err = new Error(`Shared-result storage error ${response.status}`);
      err.status = response.status;
      err.detail = body;
      throw err;
    }
    return body;
  } finally {
    clearTimeout(timer);
  }
}

function createId() {
  return crypto.randomBytes(9).toString('base64url').slice(0, 12);
}

async function createSharedResult(summary, parentResultId = null) {
  const payload = normalizeSummary(summary);
  const parent = normalizeId(parentResultId);
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const id = createId();
    try {
      const rows = await request('/rest/v1/shared_scan_results', {
        method: 'POST',
        headers: { Prefer: 'return=representation' },
        body: JSON.stringify([{ id, payload, parent_result_id: parent }])
      });
      const row = Array.isArray(rows) ? rows[0] : null;
      if (row && row.id) return { id: row.id, payload: row.payload || payload, parentResultId: row.parent_result_id || parent };
      return { id, payload, parentResultId: parent };
    } catch (error) {
      const duplicate = error && error.status === 409;
      if (!duplicate || attempt === 3) throw error;
    }
  }
  throw new Error('Could not allocate shared result id');
}

async function getSharedResult(id) {
  const normalized = normalizeId(id);
  if (!normalized) return null;
  const rows = await request(
    `/rest/v1/shared_scan_results?id=eq.${encodeURIComponent(normalized)}&select=id,payload,parent_result_id,created_at&limit=1`,
    { method: 'GET' }
  );
  return Array.isArray(rows) && rows[0] ? rows[0] : null;
}

async function trackViralEvent(eventType, { resultId = null, parentResultId = null } = {}) {
  const event = text(eventType, 32);
  if (!VALID_EVENTS.has(event)) throw new Error('Unknown viral event');
  const result = normalizeId(resultId);
  const parent = normalizeId(parentResultId);
  await request('/rest/v1/viral_events', {
    method: 'POST',
    headers: { Prefer: 'return=minimal' },
    body: JSON.stringify([{ event_type: event, result_id: result, parent_result_id: parent }])
  });
}

module.exports = {
  VALID_EVENTS,
  normalizeId,
  normalizeSummary,
  createSharedResult,
  getSharedResult,
  trackViralEvent
};
