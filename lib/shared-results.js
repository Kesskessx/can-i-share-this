'use strict';

const crypto = require('crypto');

const VERDICTS = new Set(['low', 'caution', 'high', 'unknown']);
const CONFIDENCE = new Set(['low', 'medium', 'high', 'unknown']);
const VIRAL_EVENTS = new Set(['share_x', 'result_view', 'new_scan', 'new_share']);

function text(value, max) {
  return String(value == null ? '' : value).replace(/\0/g, '').replace(/\s+/g, ' ').trim().slice(0, max);
}

function config() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error('Shared-result storage is not configured');
  return { url: url.replace(/\/$/, ''), key };
}

async function supabase(path, options = {}) {
  const cfg = config();
  const headers = {
    apikey: cfg.key,
    'content-type': 'application/json',
    ...(options.headers || {})
  };
  if (!cfg.key.startsWith('sb_secret_')) headers.authorization = `Bearer ${cfg.key}`;
  const response = await fetch(`${cfg.url}${path}`, { ...options, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(`Shared-result storage error ${response.status}${detail ? `: ${detail.slice(0, 180)}` : ''}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function sanitizeSummary(input) {
  const value = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
  const verdictRaw = text(value.verdict, 20).toLowerCase();
  const confidenceRaw = text(value.confidence, 20).toLowerCase();
  const reasons = Array.isArray(value.reasons) ? value.reasons.slice(0, 3).map((reason) => ({
    title: text(reason && reason.title, 100) || 'Signal',
    detail: text(reason && reason.detail, 280)
  })).filter((reason) => reason.title || reason.detail) : [];
  const evidence = Array.isArray(value.evidence) ? value.evidence.slice(0, 5).map((item) => ({
    type: ['brand', 'domain'].includes(text(item && item.type, 20).toLowerCase()) ? text(item.type, 20).toLowerCase() : 'signal',
    value: text(item && item.value, 160)
  })).filter((item) => item.value) : [];
  const brandMismatch = Array.isArray(value.brandMismatch) ? value.brandMismatch.slice(0, 2).map((item) => ({
    brand: text(item && item.brand, 80),
    domain: text(item && item.domain, 180),
    role: text(item && item.role, 40)
  })).filter((item) => item.brand || item.domain) : [];

  return {
    schema: 1,
    verdict: VERDICTS.has(verdictRaw) ? verdictRaw : 'unknown',
    headline: text(value.headline, 190) || 'Shared Can I Share This? result',
    confidence: CONFIDENCE.has(confidenceRaw) ? confidenceRaw : 'unknown',
    reasons,
    action: text(value.action, 300) || 'Verify independently before acting.',
    evidence,
    brandMismatch,
    note: 'Privacy-filtered shared summary. Run a fresh scan to verify the current result.'
  };
}

function validId(value) {
  const id = text(value, 32);
  return /^[A-Za-z0-9_-]{6,24}$/.test(id) ? id : null;
}

async function createSharedResult(summary, parentResultId = null) {
  const payload = sanitizeSummary(summary);
  const parent = validId(parentResultId);
  for (let attempt = 0; attempt < 4; attempt++) {
    const id = crypto.randomBytes(7).toString('base64url');
    try {
      await supabase('/rest/v1/shared_scan_results', {
        method: 'POST',
        headers: { Prefer: 'return=minimal' },
        body: JSON.stringify({ id, payload, parent_result_id: parent })
      });
      return { id, payload, parentResultId: parent };
    } catch (error) {
      if (attempt === 3 || !/409|duplicate|unique/i.test(String(error && error.message))) throw error;
    }
  }
  throw new Error('Unable to create shared result');
}

async function getSharedResult(id) {
  const safeId = validId(id);
  if (!safeId) return null;
  const rows = await supabase(`/rest/v1/shared_scan_results?select=id,payload,parent_result_id,created_at&id=eq.${encodeURIComponent(safeId)}&limit=1`);
  if (!Array.isArray(rows) || !rows.length) return null;
  return {
    id: rows[0].id,
    payload: sanitizeSummary(rows[0].payload),
    parentResultId: validId(rows[0].parent_result_id),
    createdAt: rows[0].created_at || null
  };
}

async function trackViralEvent(eventType, resultId = null, parentResultId = null) {
  const event = text(eventType, 30);
  if (!VIRAL_EVENTS.has(event)) throw new Error('Unknown viral event');
  await supabase('/rest/v1/viral_events', {
    method: 'POST',
    headers: { Prefer: 'return=minimal' },
    body: JSON.stringify({
      event_type: event,
      result_id: validId(resultId),
      parent_result_id: validId(parentResultId)
    })
  });
}

module.exports = { sanitizeSummary, createSharedResult, getSharedResult, trackViralEvent, validId };
