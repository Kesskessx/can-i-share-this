'use strict';

const baseAnalyze = require('./analyze');
const { orchestrateImageResult } = require('../lib/image-evidence-orchestrator');
const { upgradeMegaResult } = require('../lib/mega-evidence-v3');

function captureBase(req) {
  return new Promise(resolve => {
    let done = false;
    const finish = (status, headers, payload) => {
      if (done) return;
      done = true;
      resolve({ status, headers: { ...headers }, body: payload });
    };
    const fake = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) { this.headers[String(k).toLowerCase()] = v; return this; },
      getHeader(k) { return this.headers[String(k).toLowerCase()]; },
      status(code) { this.statusCode = code; return this; },
      json(payload) { finish(this.statusCode, this.headers, payload); return this; },
      end(payload) {
        let body = payload;
        if (typeof payload === 'string') {
          try { body = JSON.parse(payload); } catch (_) {}
        }
        finish(this.statusCode, this.headers, body);
        return this;
      }
    };
    Promise.resolve(baseAnalyze(req, fake)).then(() => {
      if (!done) finish(fake.statusCode, fake.headers, null);
    }).catch(err => finish(500, fake.headers, { error: err && err.message ? err.message : 'Analysis failed' }));
  });
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const captured = await captureBase(req);
    for (const [k, v] of Object.entries(captured.headers || {})) {
      if (String(k).toLowerCase() === 'content-length') continue;
      try { res.setHeader(k, v); } catch (_) {}
    }
    if (captured.status >= 400 || !captured.body || typeof captured.body !== 'object') {
      return res.status(captured.status || 500).json(captured.body || { error: 'Analysis failed' });
    }

    let body = captured.body;
    if (body.detectedType === 'image') body = await orchestrateImageResult(body);
    body = upgradeMegaResult(body);
    return res.status(captured.status || 200).json(body);
  } catch (err) {
    console.error('Mega Scanner V3 route error', err);
    return res.status(502).json({ error: 'The universal safety analysis could not complete.' });
  }
};
