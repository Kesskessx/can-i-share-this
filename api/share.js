'use strict';

const { createSharedResult } = require('../lib/shared-results');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const created = await createSharedResult(body.summary || body.shareSummary, body.parentResultId || null);
    return res.status(201).json({
      id: created.id,
      url: `https://canisharethis.com/r/${created.id}`,
      parentResultId: created.parentResultId
    });
  } catch (error) {
    console.error('[cist-share-create]', error && error.message ? error.message : error);
    return res.status(500).json({ error: 'Unable to create shared result' });
  }
};
