'use strict';

const { createSharedResult } = require('../lib/shared-results');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const summary = body.summary;
    if (!summary || typeof summary !== 'object' || Array.isArray(summary)) {
      return res.status(400).json({ error: 'Share summary required' });
    }
    const row = await createSharedResult(summary, body.parentResultId || null);
    return res.status(201).json({
      id: row.id,
      url: `https://canisharethis.com/r/${row.id}`
    });
  } catch (error) {
    console.error('[cist-share-result]', error && error.message ? error.message : error);
    return res.status(500).json({ error: 'Could not create shared result' });
  }
};
