const dns = require('node:dns').promises;
const net = require('node:net');

const MAX_REDIRECTS = 5;
const MAX_HTML_BYTES = 65536;
const TIMEOUT_MS = 8000;

function isPrivateIPv4(ip) {
  const p = ip.split('.').map(Number);
  if (p.length !== 4 || p.some(n => !Number.isInteger(n) || n < 0 || n > 255)) return true;
  return p[0] === 10 || p[0] === 127 || p[0] === 0 ||
    (p[0] === 169 && p[1] === 254) ||
    (p[0] === 172 && p[1] >= 16 && p[1] <= 31) ||
    (p[0] === 192 && p[1] === 168) ||
    (p[0] === 100 && p[1] >= 64 && p[1] <= 127) ||
    (p[0] >= 224);
}

function isPrivateIPv6(ip) {
  const x = ip.toLowerCase();
  return x === '::1' || x === '::' || x.startsWith('fc') || x.startsWith('fd') || x.startsWith('fe8') || x.startsWith('fe9') || x.startsWith('fea') || x.startsWith('feb') || x.startsWith('::ffff:127.') || x.startsWith('::ffff:10.') || x.startsWith('::ffff:192.168.') || x.startsWith('::ffff:169.254.');
}

function isPrivateIp(ip) {
  const family = net.isIP(ip);
  if (family === 4) return isPrivateIPv4(ip);
  if (family === 6) return isPrivateIPv6(ip);
  return true;
}

async function resolvePublic(hostname) {
  const h = hostname.toLowerCase();
  if (h === 'localhost' || h.endsWith('.localhost') || h.endsWith('.local') || h === 'metadata.google.internal') {
    throw new Error('Private or local hosts are not allowed.');
  }
  const records = await dns.lookup(hostname, { all: true, verbatim: true });
  if (!records.length || records.some(r => isPrivateIp(r.address))) {
    throw new Error('Private or local network targets are not allowed.');
  }
  return records;
}

function safeUrl(input) {
  const u = new URL(input);
  if (!['http:', 'https:'].includes(u.protocol)) throw new Error('Only HTTP and HTTPS links are supported.');
  if (u.username || u.password) throw new Error('Credential-bearing URLs are not allowed.');
  return u;
}

async function readPrefix(response, limit = MAX_HTML_BYTES) {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (total < limit) {
      const { done, value } = await reader.read();
      if (done) break;
      const remaining = limit - total;
      const part = value.byteLength > remaining ? value.slice(0, remaining) : value;
      chunks.push(part);
      total += part.byteLength;
      if (part.byteLength < value.byteLength) break;
    }
  } finally {
    try { await reader.cancel(); } catch {}
  }
  const merged = Buffer.concat(chunks.map(x => Buffer.from(x)));
  return merged.toString('utf8');
}

function textMeta(html) {
  const title = (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim().slice(0, 180);
  const description = (html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']*)["']/i)?.[1] || html.match(/<meta[^>]+content=["']([^"']*)["'][^>]+name=["']description["']/i)?.[1] || '').replace(/\s+/g, ' ').trim().slice(0, 300);
  return { title, description };
}

function loginHeuristic(url, status, html) {
  if ([401, 403].includes(status)) return true;
  const path = `${url.pathname}${url.search}`.toLowerCase();
  if (/\b(login|log-in|signin|sign-in|auth|oauth|accounts?)\b/.test(path)) return true;
  const sample = html.toLowerCase().slice(0, MAX_HTML_BYTES);
  return /type=["']password["']/.test(sample) || /\b(sign in|log in|request access|you need permission|access denied)\b/.test(sample);
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const raw = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    let current = safeUrl(String(raw.url || ''));
    const redirects = [];
    let firstAddresses = [];
    let finalAddresses = [];
    let response = null;
    let html = '';
    let totalMs = 0;

    for (let i = 0; i <= MAX_REDIRECTS; i++) {
      const addresses = await resolvePublic(current.hostname);
      if (i === 0) firstAddresses = addresses;
      finalAddresses = addresses;

      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
      const started = Date.now();
      try {
        response = await fetch(current, {
          method: 'GET',
          redirect: 'manual',
          signal: controller.signal,
          headers: {
            'user-agent': 'CanIShareThis/1.0 (+https://canisharethis.com)',
            'accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8'
          }
        });
      } finally {
        clearTimeout(timer);
      }
      const elapsed = Date.now() - started;
      totalMs += elapsed;

      const loc = response.headers.get('location');
      if (loc && [301, 302, 303, 307, 308].includes(response.status)) {
        if (i === MAX_REDIRECTS) throw new Error('Too many redirects.');
        const next = safeUrl(new URL(loc, current).toString());
        redirects.push({ status: response.status, url: next.toString(), responseMs: elapsed });
        current = next;
        continue;
      }

      const type = (response.headers.get('content-type') || '').toLowerCase();
      if (type.includes('text/html') || type.includes('application/xhtml+xml')) html = await readPrefix(response);
      break;
    }

    if (!response) throw new Error('No response received.');
    const meta = textMeta(html);
    const loginRequired = loginHeuristic(current, response.status, html);

    return res.status(200).json({
      reachable: true,
      status: response.status,
      finalUrl: current.toString(),
      finalHost: current.hostname,
      addresses: finalAddresses.length ? finalAddresses : firstAddresses,
      responseMs: totalMs,
      redirects,
      loginRequired,
      pageTitle: meta.title || undefined,
      pageDescription: meta.description || undefined
    });
  } catch (err) {
    const message = err && err.name === 'AbortError' ? 'Destination timed out.' : (err?.message || 'Check failed.');
    return res.status(200).json({ reachable: false, status: 0, redirects: [], loginRequired: false, addresses: [], error: message });
  }
};
