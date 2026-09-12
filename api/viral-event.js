'use strict';

const { trackViralEvent } = require('../lib/shared-results');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    await trackViralEvent(body.event, body.resultId || null, body.parentResultId || null);
    return res.status(204).end();
  } catch (error) {
    if (/Unknown viral event/.test(String(error && error.message))) return res.status(400).json({ error: 'Unknown event' });
    console.error('[cist-viral-event]', error && error.message ? error.message : error);
    return res.status(500).json({ error: 'Unable to record event' });
  }
};
