'use strict';

const { createSharedResult, getSharedResult, normalizeId, trackViralEvent, VALID_EVENTS } = require('../lib/shared-results');
const { pageHtml, ogImageResponse } = require('../lib/shared-result-render');

const ALLOWED_EVENTS = new Set(['homepage_view', 'paste', 'analyze', 'deep_scan', 'scan_result']);
const ALLOWED_STATUSES = new Set(['low', 'caution', 'high', 'unknown']);

function bool(value) {
  return value === true;
}

function bodyOf(req) {
  if (typeof req.body === 'string') return JSON.parse(req.body || '{}');
  return req.body || {};
}

async function sharedPage(req, res) {
  const id = normalizeId(req.query && req.query.id);
  if (!id) return res.status(404).end('Shared result not found');
  const row = await getSharedResult(id);
  if (!row) return res.status(404).end('Shared result not found');
  const html = pageHtml(row);
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=0, s-maxage=300, stale-while-revalidate=86400');
  if (req.method === 'HEAD') return res.status(200).end();
  return res.status(200).send(html);
}

async function sharedOg(req, res) {
  const id = normalizeId(req.query && req.query.id);
  if (!id) return res.status(404).end('Image not found');
  const row = await getSharedResult(id);
  if (!row) return res.status(404).end('Image not found');
  const image = await ogImageResponse(row);
  res.statusCode = 200;
  image.headers.forEach((value, key) => res.setHeader(key, value));
  res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
  if (req.method === 'HEAD') return res.end();
  return res.end(Buffer.from(await image.arrayBuffer()));
}

async function createShare(req, res) {
  const body = bodyOf(req);
  if (!body.summary || typeof body.summary !== 'object' || Array.isArray(body.summary)) {
    return res.status(400).json({ error: 'Share summary required' });
  }
  const row = await createSharedResult(body.summary, body.parentResultId || null);
  return res.status(201).json({ id: row.id, url: `https://canisharethis.com/r/${row.id}` });
}

async function viralEvent(req, res) {
  const body = bodyOf(req);
  const event = String(body.event || '');
  if (!VALID_EVENTS.has(event)) return res.status(400).json({ error: 'Unknown event' });
  await trackViralEvent(event, {
    resultId: normalizeId(body.resultId),
    parentResultId: normalizeId(body.parentResultId)
  });
  return res.status(204).end();
}

async function legacyEvent(req, res) {
  const body = bodyOf(req);
  const event = String(body.event || '');
  if (!ALLOWED_EVENTS.has(event)) return res.status(400).json({ error: 'Unknown event' });

  if (event === 'scan_result') {
    const status = ALLOWED_STATUSES.has(String(body.status || '')) ? String(body.status) : 'unknown';
    console.log('[cist-scan-aggregate]', JSON.stringify({
      event: 'scan_result',
      status,
      redirected: bool(body.redirected),
      shortened: bool(body.shortened),
      phishing: bool(body.phishing),
      lookalike: bool(body.lookalike),
      domain_changed: bool(body.domain_changed),
      risky_download: bool(body.risky_download),
      timestamp: new Date().toISOString()
    }));
    return res.status(204).end();
  }

  console.log('[cist-event]', JSON.stringify({ event, path: '/', timestamp: new Date().toISOString() }));
  return res.status(204).end();
}

module.exports = async function handler(req, res) {
  const action = String((req.query && req.query.action) || 'event');
  try {
    if ((req.method === 'GET' || req.method === 'HEAD') && action === 'result-page') return await sharedPage(req, res);
    if ((req.method === 'GET' || req.method === 'HEAD') && action === 'result-og') return await sharedOg(req, res);

    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
    if (action === 'share-result') return await createShare(req, res);
    if (action === 'viral-event') return await viralEvent(req, res);
    return await legacyEvent(req, res);
  } catch (error) {
    console.error('[cist-event-error]', action, error && error.message ? error.message : error);
    if (action === 'result-page') return res.status(503).end('Shared result temporarily unavailable');
    if (action === 'result-og') return res.status(503).end('Image unavailable');
    if (error instanceof SyntaxError) return res.status(400).json({ error: 'Invalid event payload' });
    return res.status(500).json({ error: 'Request could not be completed' });
  }
};
