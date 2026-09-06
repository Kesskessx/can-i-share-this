'use strict';

const BRAND_DOMAINS = Object.freeze({
  google: ['google.com','gmail.com','googlemail.com','googleusercontent.com','googleapis.com','gstatic.com'],
  microsoft: ['microsoft.com','live.com','outlook.com','hotmail.com','office.com','office365.com','microsoftonline.com','sharepoint.com','onedrive.com'],
  apple: ['apple.com','icloud.com'],
  paypal: ['paypal.com'],
  amazon: ['amazon.com','amazon.fr','amazon.co.uk','amazon.de','amazonaws.com'],
  netflix: ['netflix.com'],
  dropbox: ['dropbox.com','dropboxusercontent.com'],
  notion: ['notion.so','notion.site'],
  meta: ['meta.com'],
  facebook: ['facebook.com','fb.com','messenger.com'],
  instagram: ['instagram.com'],
  whatsapp: ['whatsapp.com','wa.me'],
  tiktok: ['tiktok.com'],
  x: ['x.com','twitter.com'],
  telegram: ['telegram.org','t.me','telegram.me'],
  discord: ['discord.com','discord.gg','discordapp.com'],
  linkedin: ['linkedin.com'],
  youtube: ['youtube.com','youtu.be','googlevideo.com'],
  binance: ['binance.com'],
  coinbase: ['coinbase.com'],
  kraken: ['kraken.com'],
  revolut: ['revolut.com'],
  wise: ['wise.com'],
  stripe: ['stripe.com'],
  dhl: ['dhl.com','dhl.de'],
  fedex: ['fedex.com'],
  ups: ['ups.com'],
  usps: ['usps.com'],
  chronopost: ['chronopost.fr'],
  'la poste': ['laposte.fr'],
  github: ['github.com','githubusercontent.com'],
  cloudflare: ['cloudflare.com'],
  adobe: ['adobe.com'],
  steam: ['steampowered.com','steamcommunity.com'],
  spotify: ['spotify.com'],
  airbnb: ['airbnb.com','airbnb.fr'],
  booking: ['booking.com']
});

const ALIASES = Object.freeze({
  'microsoft 365': 'microsoft', 'office 365': 'microsoft', outlook: 'microsoft', onedrive: 'microsoft',
  gmail: 'google', youtube: 'youtube', twitter: 'x', 'x.com': 'x',
  'la poste': 'la poste', laposte: 'la poste', meta: 'meta'
});

const IDENTITY_WORDS = ['support','security','secure','official','verification','verify','account','customer service','help desk','team','billing','payment','recovery','administrator','admin'];

function clean(value, max = 300) {
  return String(value == null ? '' : value).replace(/\0/g, '').replace(/\s+/g, ' ').trim().slice(0, max);
}

function normalizeBrand(value) {
  const raw = clean(value, 120).toLowerCase().replace(/[®™]/g, '').trim();
  if (!raw) return '';
  if (BRAND_DOMAINS[raw]) return raw;
  if (ALIASES[raw]) return ALIASES[raw];
  const compact = raw.replace(/[^a-z0-9]+/g, ' ').trim();
  if (BRAND_DOMAINS[compact]) return compact;
  if (ALIASES[compact]) return ALIASES[compact];
  return compact;
}

function normalizeHost(value) {
  const raw = clean(value, 500).toLowerCase();
  if (!raw) return '';
  try {
    const u = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`);
    return u.hostname.toLowerCase().replace(/^www\./, '');
  } catch (_) {
    return raw.replace(/^https?:\/\//, '').split(/[\/?#]/)[0].replace(/^www\./, '');
  }
}

function hostMatches(host, domain) {
  host = normalizeHost(host); domain = normalizeHost(domain);
  return Boolean(host && domain && (host === domain || host.endsWith(`.${domain}`)));
}

function officialDomains(brand) {
  return BRAND_DOMAINS[normalizeBrand(brand)] || [];
}

function brandDomainStatus(brand, host) {
  const normalized = normalizeBrand(brand);
  const domain = normalizeHost(host);
  if (!normalized || !domain) return { brand: normalized, domain, status: 'unknown', official: false };
  const domains = officialDomains(normalized);
  if (!domains.length) return { brand: normalized, domain, status: 'unregistered-brand', official: false };
  const official = domains.some(d => hostMatches(domain, d));
  return { brand: normalized, domain, status: official ? 'confirmed' : 'conflict', official };
}

function hostLooksLikeBrand(host, brand) {
  const domain = normalizeHost(host);
  const normalized = normalizeBrand(brand).replace(/[^a-z0-9]/g, '');
  if (!domain || !normalized) return false;
  const label = domain.split('.')[0].replace(/[^a-z0-9]/g, '');
  return label.includes(normalized) || normalized.includes(label) && label.length >= 5;
}

function identityContext(source, start, end) {
  const left = Math.max(0, start - 70), right = Math.min(source.length, end + 70);
  const context = source.slice(left, right).toLowerCase();
  if (IDENTITY_WORDS.some(word => context.includes(word))) return true;
  if (/\b(i am|i'm|we are|this is|from|represent(?:ing)?|on behalf of)\b/.test(context)) return true;
  return false;
}

function detectBrandClaims(text) {
  const source = clean(text, 20000).toLowerCase();
  const claims = [];
  const add = (needle, canonical) => {
    let pos = 0;
    while ((pos = source.indexOf(needle, pos)) >= 0) {
      const before = pos > 0 ? source[pos - 1] : ' ';
      const after = source[pos + needle.length] || ' ';
      const boundary = !/[a-z0-9]/.test(before) && !/[a-z0-9]/.test(after);
      if (boundary && identityContext(source, pos, pos + needle.length)) {
        if (!claims.includes(canonical)) claims.push(canonical);
        return;
      }
      pos += Math.max(1, needle.length);
    }
  };
  for (const brand of Object.keys(BRAND_DOMAINS)) add(brand, brand);
  for (const [alias, canonical] of Object.entries(ALIASES)) add(alias, canonical);
  return claims.slice(0, 10);
}

function knownBrandFromHost(host) {
  const domain = normalizeHost(host);
  for (const [brand, domains] of Object.entries(BRAND_DOMAINS)) {
    if (domains.some(d => hostMatches(domain, d))) return brand;
  }
  return null;
}

module.exports = {
  BRAND_DOMAINS,
  normalizeBrand,
  normalizeHost,
  hostMatches,
  officialDomains,
  brandDomainStatus,
  hostLooksLikeBrand,
  detectBrandClaims,
  knownBrandFromHost
};
