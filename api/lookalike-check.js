const BRAND_DOMAINS = {
  google: ['google.com', 'gmail.com'],
  microsoft: ['microsoft.com', 'live.com', 'outlook.com', 'office.com', 'office365.com', 'microsoftonline.com'],
  apple: ['apple.com', 'icloud.com'],
  paypal: ['paypal.com'],
  amazon: ['amazon.com', 'amazon.fr', 'amazon.co.uk', 'amazon.de'],
  netflix: ['netflix.com'],
  dropbox: ['dropbox.com'],
  notion: ['notion.so', 'notion.site'],
  whatsapp: ['whatsapp.com', 'wa.me'],
  facebook: ['facebook.com', 'fb.com'],
  instagram: ['instagram.com'],
  dhl: ['dhl.com'],
  fedex: ['fedex.com'],
  ups: ['ups.com'],
  stripe: ['stripe.com'],
  coinbase: ['coinbase.com'],
  binance: ['binance.com']
};

function displayHost(host) {
  return String(host || '').toLowerCase().replace(/^www\./, '');
}

function hostMatches(host, domain) {
  return host === domain || host.endsWith(`.${domain}`);
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

function registrableLabel(host) {
  const base = baseDomain(host);
  const parts = base.split('.');
  return parts[0] || '';
}

function skeleton(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/0/g, 'o')
    .replace(/[1l|]/g, 'i')
    .replace(/3/g, 'e')
    .replace(/5/g, 's')
    .replace(/7/g, 't')
    .replace(/8/g, 'b')
    .replace(/[^a-z0-9]/g, '');
}

function distance(a, b) {
  a = String(a || ''); b = String(b || '');
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  const prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    let diagonal = prev[0];
    prev[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const old = prev[j];
      prev[j] = Math.min(prev[j] + 1, prev[j - 1] + 1, diagonal + (a[i - 1] === b[j - 1] ? 0 : 1));
      diagonal = old;
    }
  }
  return prev[b.length];
}

function analyze(url) {
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Only HTTP and HTTPS links are supported.');
  const host = displayHost(parsed.hostname);
  const label = registrableLabel(host);
  const compact = skeleton(label);
  const findings = [];

  if (host.includes('xn--')) {
    findings.push({
      severity: 'caution',
      code: 'punycode',
      title: 'Internationalized domain encoding',
      detail: 'This hostname uses Punycode. That can be legitimate, but it is also used to create domains that visually imitate familiar names.'
    });
  }

  for (const [brand, domains] of Object.entries(BRAND_DOMAINS)) {
    if (domains.some(domain => hostMatches(host, domain))) continue;
    const brandKey = skeleton(brand);
    const directMention = compact.includes(brandKey) || skeleton(host).includes(brandKey);
    const d = distance(compact, brandKey);
    const confusableMatch = compact !== brandKey && skeleton(compact) === skeleton(brandKey);
    if (directMention) {
      findings.push({
        severity: 'high',
        code: `brand-${brand}`,
        title: `Possible ${brand} impersonation`,
        detail: `The domain contains “${brand}” but is not an official ${brand} domain.`
      });
      break;
    }
    if ((brandKey.length >= 5 && d === 1) || confusableMatch) {
      findings.push({
        severity: 'high',
        code: `typo-${brand}`,
        title: `Possible ${brand} lookalike`,
        detail: `The domain “${host}” is visually or typographically very close to ${brand}, but it is not an official ${brand} domain.`
      });
      break;
    }
  }

  return {
    host,
    status: findings.some(x => x.severity === 'high') ? 'high' : findings.length ? 'caution' : 'clear',
    findings
  };
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const url = String(body.url || '').trim();
    if (!url) return res.status(400).json({ error: 'URL required' });
    return res.status(200).json(analyze(url));
  } catch (err) {
    return res.status(400).json({ error: err?.message || 'Invalid URL' });
  }
};
