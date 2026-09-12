'use strict';

const { VALID_EVENTS, normalizeId, trackViralEvent } = require('../lib/shared-results');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const event = String(body.event || '');
    if (!VALID_EVENTS.has(event)) return res.status(400).json({ error: 'Unknown event' });

    const resultId = normalizeId(body.resultId);
    const parentResultId = normalizeId(body.parentResultId);
    await trackViralEvent(event, { resultId, parentResultId });
    return res.status(204).end();
  } catch (error) {
    console.error('[cist-viral-event]', error && error.message ? error.message : error);
    return res.status(500).json({ error: 'Could not record event' });
  }
};
