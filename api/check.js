const dns = require('node:dns').promises;
const net = require('node:net');

const MAX_REDIRECTS = 5;
const MAX_HTML_BYTES = 65536;
const TIMEOUT_MS = 8000;

const SHORTENER_HOSTS = new Set([
  'bit.ly', 'tinyurl.com', 't.co', 'rb.gy', 'rebrand.ly', 'is.gd', 'cutt.ly',
  'shorturl.at', 'tiny.cc', 'buff.ly', 'ow.ly', 'lnkd.in', 'goo.gl', 'trib.al'
]);

const EXECUTABLE_EXTENSIONS = new Set([
  '.exe', '.msi', '.msix', '.scr', '.bat', '.cmd', '.com', '.ps1', '.vbs',
  '.jar', '.apk', '.dmg', '.pkg', '.iso', '.img', '.hta', '.appinstaller'
]);
const ARCHIVE_EXTENSIONS = new Set(['.zip', '.rar', '.7z', '.gz', '.tgz', '.bz2']);

const BRAND_DOMAINS = {
  google: ['google.com', 'googleusercontent.com', 'googleapis.com', 'gstatic.com'],
  microsoft: ['microsoft.com', 'live.com', 'office.com', 'office365.com', 'microsoftonline.com', 'sharepoint.com', 'onedrive.com'],
  apple: ['apple.com', 'icloud.com'],
  paypal: ['paypal.com'],
  amazon: ['amazon.com', 'amazon.fr', 'amazon.co.uk', 'amazon.de'],
  netflix: ['netflix.com'],
  dropbox: ['dropbox.com', 'dropboxusercontent.com'],
  notion: ['notion.so', 'notion.site'],
  whatsapp: ['whatsapp.com', 'wa.me'],
  facebook: ['facebook.com', 'fb.com', 'messenger.com'],
  instagram: ['instagram.com'],
  dhl: ['dhl.com'],
  fedex: ['fedex.com'],
  ups: ['ups.com']
};

const PHISHING_TERMS = [
  'login', 'log-in', 'signin', 'sign-in', 'verify', 'verification', 'secure',
  'security', 'account', 'password', 'wallet', 'payment', 'invoice', 'parcel',
  'delivery', 'gift', 'prize', 'claim', 'recover', 'recovery', 'reset', 'confirm',
  'update', 'unlock', 'suspend', 'suspended', 'billing'
];

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
  return x === '::1' || x === '::' || x.startsWith('fc') || x.startsWith('fd') ||
    x.startsWith('fe8') || x.startsWith('fe9') || x.startsWith('fea') || x.startsWith('feb') ||
    x.startsWith('::ffff:127.') || x.startsWith('::ffff:10.') ||
    x.startsWith('::ffff:192.168.') || x.startsWith('::ffff:169.254.');
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

function hostMatches(host, domain) {
  return host === domain || host.endsWith(`.${domain}`);
}
function displayHost(host) {
  return String(host || '').toLowerCase().replace(/^www\./, '');
}
function baseDomain(host) {
  const clean = displayHost(host);
  const parts = clean.split('.').filter(Boolean);
  if (parts.length <= 2) return clean;
  const countrySecondLevels = new Set(['co.uk', 'org.uk', 'com.au', 'com.br', 'co.jp', 'co.nz']);
  const lastTwo = parts.slice(-2).join('.');
  if (countrySecondLevels.has(lastTwo) && parts.length >= 3) return parts.slice(-3).join('.');
  return lastTwo;
}
function pathExtension(pathname) {
  const clean = String(pathname || '').toLowerCase().split('/').pop() || '';
  const match = clean.match(/(\.[a-z0-9]{1,12})$/);
  return match ? match[1] : '';
}
function addSignal(signals, code, severity, title, detail, weight) {
  signals.push({ code, severity, title, detail, weight });
}

function analyzeSafety({ rawInput, initialUrl, finalUrl, redirects = [], contentType = '', contentDisposition = '', loginRequired = false }) {
  const signals = [];
  let parsed = finalUrl || initialUrl || null;
  if (!parsed) {
    try { parsed = new URL(rawInput); } catch {}
  }
  if (!parsed || !parsed.hostname) {
    return {
      status: 'unknown', riskScore: 0,
      verdict: 'Not enough information to assess this link', signals: [],
      checksPerformed: ['URL structure'],
      reputation: { checked: false, status: 'not-checked', reason: 'Privacy-first mode: the URL was not submitted to a third-party reputation service.' },
      disclaimer: 'A link checker cannot guarantee that a destination is safe. Avoid entering passwords or payment details unless you trust the destination.'
    };
  }

  const host = displayHost(parsed.hostname);
  const initialHost = displayHost(initialUrl?.hostname || host);
  const ext = pathExtension(parsed.pathname);
  const urlText = parsed.toString();
  const hostAndPath = `${host}${parsed.pathname}`.toLowerCase();

  if (parsed.protocol === 'http:') addSignal(signals, 'http', 'medium', 'Unencrypted HTTP', 'The destination does not use HTTPS, so traffic can be intercepted or modified in transit.', 18);
  if (net.isIP(host)) addSignal(signals, 'ip-host', 'medium', 'Direct IP address', 'The link uses an IP address instead of a normal domain name. That is unusual for consumer-facing links.', 22);
  if (host.includes('xn--')) addSignal(signals, 'punycode', 'medium', 'Punycode domain', 'The hostname contains an internationalized-domain encoding that can sometimes be used for lookalike domains.', 22);
  if (SHORTENER_HOSTS.has(host)) addSignal(signals, 'shortener', 'medium', 'Shortened link', 'The visible URL hides the final destination. Review the resolved domain before entering sensitive information.', 14);

  const labels = host.split('.').filter(Boolean);
  if (labels.length >= 6) addSignal(signals, 'deep-subdomain', 'low', 'Many subdomains', 'A deeply nested hostname can make the real registered domain harder to notice.', 8);
  const hyphens = (host.match(/-/g) || []).length;
  if (hyphens >= 4) addSignal(signals, 'many-hyphens', 'low', 'Unusually hyphenated domain', 'The hostname contains many hyphens, a pattern sometimes seen in disposable or deceptive domains.', 7);
  if (parsed.port && !['80', '443'].includes(parsed.port)) addSignal(signals, 'unusual-port', 'low', 'Unusual network port', `The destination uses port ${parsed.port}, which is uncommon for ordinary public web links.`, 7);

  for (const [brand, officialDomains] of Object.entries(BRAND_DOMAINS)) {
    const mentionsBrand = host.includes(brand);
    const official = officialDomains.some(domain => hostMatches(host, domain));
    if (mentionsBrand && !official) {
      addSignal(signals, `brand-${brand}`, 'high', `Possible ${brand[0].toUpperCase() + brand.slice(1)} lookalike`, `The hostname contains “${brand}” but is not on a recognized ${brand} domain. Verify the domain carefully before signing in or paying.`, 38);
      break;
    }
  }

  const terms = PHISHING_TERMS.filter(term => hostAndPath.includes(term));
  if (terms.length >= 4) addSignal(signals, 'phishing-language', 'medium', 'Multiple high-pressure account terms', `The URL contains several terms often used in phishing flows: ${terms.slice(0, 5).join(', ')}.`, 20);
  else if (terms.length >= 2 && terms.some(term => host.includes(term))) addSignal(signals, 'phishing-language', 'low', 'Suspicious account language in domain', `The hostname contains account/security wording (${terms.slice(0, 4).join(', ')}). Treat unexpected links with caution.`, 10);

  if (EXECUTABLE_EXTENSIONS.has(ext)) addSignal(signals, 'executable-download', 'high', 'Executable download', `The URL appears to point directly to a ${ext} file. Do not run unexpected software from an untrusted sender.`, 42);
  else if (ARCHIVE_EXTENSIONS.has(ext)) addSignal(signals, 'archive-download', 'medium', 'Archive download', `The URL appears to point to a ${ext} archive. Archives can contain executable or script files, so inspect the source carefully.`, 14);

  const disposition = String(contentDisposition || '').toLowerCase();
  if (disposition.includes('attachment') && !EXECUTABLE_EXTENSIONS.has(ext)) addSignal(signals, 'forced-download', 'low', 'Forced file download', 'The server is asking the browser to download a file rather than display a normal page.', 8);
  const pctCount = (urlText.match(/%[0-9a-f]{2}/gi) || []).length;
  if (pctCount >= 10) addSignal(signals, 'heavy-encoding', 'low', 'Heavily encoded URL', 'A large amount of percent-encoding makes the real path harder to read.', 6);
  if (urlText.length > 1800) addSignal(signals, 'very-long-url', 'low', 'Very long URL', 'The link is unusually long, which can hide parameters or redirect targets.', 7);
  if (redirects.length >= 3) addSignal(signals, 'many-redirects', 'medium', 'Multiple redirects', `The link redirected ${redirects.length} times before reaching its destination.`, 12);
  if (initialHost && host && baseDomain(initialHost) !== baseDomain(host)) addSignal(signals, 'domain-change', 'low', 'Destination domain changed', `The link started on ${initialHost} and ended on ${host}. Confirm that the final domain is expected.`, 9);
  if (loginRequired && parsed.protocol === 'http:') addSignal(signals, 'password-over-http', 'high', 'Login on an unencrypted page', 'The destination appears to ask for authentication while using HTTP. Do not enter credentials.', 35);

  const type = String(contentType || '').toLowerCase();
  if (type && !type.includes('text/html') && /application\/(x-msdownload|octet-stream|java-archive)|application\/vnd\.android\.package-archive/.test(type)) addSignal(signals, 'binary-content', 'high', 'Binary file response', 'The destination responds with a binary or installable file type rather than a normal webpage.', 32);

  const riskScore = Math.min(100, signals.reduce((sum, signal) => sum + signal.weight, 0));
  const status = riskScore >= 60 ? 'high' : riskScore >= 30 ? 'caution' : 'low';
  const verdict = status === 'high' ? 'High-risk URL patterns detected' : status === 'caution' ? 'Suspicious signals detected' : 'No obvious suspicious URL patterns detected';
  return {
    status, riskScore, verdict,
    signals: signals.map(({ weight, ...signal }) => signal),
    checksPerformed: ['URL and domain structure', 'Common brand-lookalike patterns', 'Short-link and redirect behavior', 'Executable/download indicators', 'Basic phishing-language signals'],
    reputation: { checked: false, status: 'not-checked', reason: 'Privacy-first mode: the URL was not submitted to a third-party reputation service.' },
    disclaimer: 'This is a risk assessment, not a guarantee. A new phishing or malware page may have no known warning signs yet.'
  };
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let rawInput = '';
  let initialUrl = null;
  try {
    const raw = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    rawInput = String(raw.url || '').trim();
    let current = safeUrl(rawInput);
    initialUrl = new URL(current.toString());
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
          method: 'GET', redirect: 'manual', signal: controller.signal,
          headers: {
            'user-agent': 'CanIShareThis/1.1 (+https://canisharethis.com)',
            'accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8'
          }
        });
      } finally { clearTimeout(timer); }
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
    const contentType = response.headers.get('content-type') || '';
    const contentDisposition = response.headers.get('content-disposition') || '';
    const safety = analyzeSafety({ rawInput, initialUrl, finalUrl: current, redirects, contentType, contentDisposition, loginRequired });

    return res.status(200).json({
      reachable: true, status: response.status, finalUrl: current.toString(), finalHost: current.hostname,
      addresses: finalAddresses.length ? finalAddresses : firstAddresses, responseMs: totalMs,
      redirects, loginRequired, pageTitle: meta.title || undefined, pageDescription: meta.description || undefined,
      safety
    });
  } catch (err) {
    const message = err && err.name === 'AbortError' ? 'Destination timed out.' : (err?.message || 'Check failed.');
    let fallbackUrl = null;
    try { fallbackUrl = new URL(rawInput); } catch {}
    const safety = analyzeSafety({ rawInput, initialUrl: initialUrl || fallbackUrl, finalUrl: fallbackUrl, redirects: [] });
    return res.status(200).json({ reachable: false, status: 0, redirects: [], loginRequired: false, addresses: [], error: message, safety });
  }
};
