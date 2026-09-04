const MAX_BYTES = 4 * 1024 * 1024;
const ALLOWED_MIME = new Set(['image/jpeg', 'image/png', 'image/webp']);

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('cache-control', 'no-store, max-age=0');
  res.end(JSON.stringify(body));
}

function parseDataUrl(value) {
  const match = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/i.exec(String(value || ''));
  if (!match) return null;
  const mimeType = match[1].toLowerCase();
  if (!ALLOWED_MIME.has(mimeType)) return null;
  const data = match[2];
  let bytes;
  try { bytes = Buffer.from(data, 'base64'); } catch (_) { return null; }
  if (!bytes.length || bytes.length > MAX_BYTES) return null;
  return { mimeType, data };
}

function safeText(v, max = 500) {
  return typeof v === 'string' ? v.slice(0, max) : '';
}

function normalizeOutput(raw) {
  const out = raw && typeof raw === 'object' ? raw : {};
  const arr = (v, maxItems = 10, maxLen = 300) => Array.isArray(v)
    ? v.filter(x => typeof x === 'string').slice(0, maxItems).map(x => x.slice(0, maxLen))
    : [];
  const signals = Array.isArray(out.suspicious_signals)
    ? out.suspicious_signals.slice(0, 8).map(s => {
        if (typeof s === 'string') return { type: 'signal', detail: s.slice(0, 300) };
        if (!s || typeof s !== 'object') return null;
        return { type: safeText(s.type, 80) || 'signal', detail: safeText(s.detail, 300) };
      }).filter(Boolean)
    : [];
  const risk = ['low', 'caution', 'high', 'unknown'].includes(out.risk) ? out.risk : 'unknown';
  return {
    risk,
    confidence: Number.isFinite(out.confidence) ? Math.max(0, Math.min(1, out.confidence)) : null,
    summary: safeText(out.summary, 700),
    recommended_action: safeText(out.recommended_action, 500),
    visible_text: safeText(out.visible_text, 3500),
    urls: arr(out.urls),
    emails: arr(out.emails),
    phones: arr(out.phones),
    qr_values: arr(out.qr_values),
    claimed_brands: arr(out.claimed_brands, 8, 120),
    suspicious_signals: signals
  };
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed' });

  const image = parseDataUrl(req.body && req.body.image);
  if (!image) return json(res, 400, { error: 'Use a JPEG, PNG or WebP image up to 4 MB.' });

  const key = process.env.GEMINI_API_KEY;
  if (!key) return json(res, 503, { error: 'Image analysis is not configured yet.' });

  const model = process.env.GEMINI_MODEL || 'gemini-flash-latest';
  const prompt = `You are a security extraction component for Can I Share This?. Analyze this screenshot or photo for scam and phishing indicators. Do not claim certainty. Extract only evidence visible in the image. Detect visible text, URLs, email addresses, phone numbers, QR-code contents if readable, brands or organizations being claimed, requests for login/payment/crypto/download, urgency, threats, impersonation, and brand/domain mismatch. Return JSON only with this exact shape: {"risk":"low|caution|high|unknown","confidence":0.0,"summary":"short plain-language summary","recommended_action":"short action","visible_text":"important visible text","urls":[],"emails":[],"phones":[],"qr_values":[],"claimed_brands":[],"suspicious_signals":[{"type":"short_type","detail":"specific visible evidence"}]}. If the image is unrelated or unreadable, use risk unknown. Never invent a URL, email, phone number, QR value or brand.`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'X-goog-api-key': key
      },
      body: JSON.stringify({
        contents: [{ parts: [
          { text: prompt },
          { inline_data: { mime_type: image.mimeType, data: image.data } }
        ] }],
        generationConfig: { responseMimeType: 'application/json', temperature: 0.1 }
      }),
      signal: controller.signal
    });
    const data = await r.json().catch(() => null);
    if (!r.ok) {
      console.error('Gemini image check failed', r.status, data && data.error && data.error.message);
      return json(res, r.status === 429 ? 429 : 502, {
        error: r.status === 429 ? 'Image analysis quota is temporarily exhausted.' : 'Image analysis is temporarily unavailable.'
      });
    }
    const text = data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts
      ? data.candidates[0].content.parts.map(p => p.text || '').join('') : '';
    let parsed;
    try { parsed = JSON.parse(text); } catch (_) {
      return json(res, 502, { error: 'Image analysis returned an unreadable result.' });
    }
    return json(res, 200, { ok: true, analysis: normalizeOutput(parsed), provider: 'gemini', model });
  } catch (err) {
    if (err && err.name === 'AbortError') return json(res, 504, { error: 'Image analysis timed out.' });
    console.error('Image check error', err);
    return json(res, 502, { error: 'Image analysis is temporarily unavailable.' });
  } finally {
    clearTimeout(timer);
  }
}
