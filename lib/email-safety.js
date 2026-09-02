const dns = require('node:dns').promises;
const { domainToASCII } = require('node:url');

const DNS_TIMEOUT_MS = 3500;

const DISPOSABLE_DOMAINS = new Set([
  '10minutemail.com', '10minutemail.net', 'dispostable.com', 'emailondeck.com',
  'fakeinbox.com', 'guerrillamail.com', 'guerrillamail.net', 'guerrillamail.org',
  'maildrop.cc', 'mailinator.com', 'mailnesia.com', 'mintemail.com',
  'moakt.com', 'mytemp.email', 'sharklasers.com', 'spamgourmet.com',
  'temp-mail.org', 'tempail.com', 'tempmail.com', 'tempmail.net',
  'throwawaymail.com', 'trashmail.com', 'yopmail.com', 'yopmail.fr'
]);

const BRAND_DOMAINS = {
  google: ['google.com', 'googlemail.com', 'gmail.com'],
  microsoft: ['microsoft.com', 'live.com', 'outlook.com', 'hotmail.com', 'office.com', 'office365.com', 'microsoftonline.com'],
  apple: ['apple.com', 'icloud.com'],
  paypal: ['paypal.com'],
  amazon: ['amazon.com', 'amazon.fr', 'amazon.co.uk', 'amazon.de', 'amazonaws.com'],
  netflix: ['netflix.com'],
  dropbox: ['dropbox.com'],
  notion: ['notion.so', 'notion.site'],
  whatsapp: ['whatsapp.com'],
  facebook: ['facebook.com', 'meta.com'],
  instagram: ['instagram.com'],
  dhl: ['dhl.com', 'dhl.de'],
  fedex: ['fedex.com'],
  ups: ['ups.com'],
  stripe: ['stripe.com'],
  coinbase: ['coinbase.com']
};

const SUSPICIOUS_DOMAIN_TERMS = [
  'verify', 'verification', 'secure', 'security', 'account', 'password',
  'payment', 'billing', 'invoice', 'recover', 'recovery', 'reset',
  'unlock', 'suspend', 'support', 'wallet'
];

function hostMatches(host, domain) {
  return host === domain || host.endsWith(`.${domain}`);
}

function registrableLabel(domain) {
  const parts = String(domain || '').toLowerCase().split('.').filter(Boolean);
  if (parts.length < 2) return parts[0] || '';
  const countrySecondLevels = new Set(['co.uk', 'org.uk', 'com.au', 'com.br', 'co.jp', 'co.nz']);
  const lastTwo = parts.slice(-2).join('.');
  if (countrySecondLevels.has(lastTwo) && parts.length >= 3) return parts[parts.length - 3];
  return parts[parts.length - 2];
}

function visualNormalize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/0/g, 'o')
    .replace(/1/g, 'l')
    .replace(/3/g, 'e')
    .replace(/5/g, 's')
    .replace(/7/g, 't')
    .replace(/[^a-z]/g, '');
}

function parseEmailAddress(input) {
  const value = String(input || '').trim();
  if (!value || value.length > 254 || /\s/.test(value)) throw new Error('Enter one valid email address.');
  const at = value.lastIndexOf('@');
  if (at <= 0 || at !== value.indexOf('@')) throw new Error('Enter one valid email address.');

  const local = value.slice(0, at);
  const rawDomain = value.slice(at + 1).replace(/\.$/, '');
  if (!local || local.length > 64 || !rawDomain || rawDomain.length > 253) throw new Error('Enter one valid email address.');
  if (!/^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+$/.test(local) || local.startsWith('.') || local.endsWith('.') || local.includes('..')) {
    throw new Error('This email address uses a format the checker does not support.');
  }

  const domain = domainToASCII(rawDomain.toLowerCase());
  if (!domain || !domain.includes('.') || domain.length > 253) throw new Error('Enter a public email domain.');
  const labels = domain.split('.');
  if (labels.some(label => !label || label.length > 63 || !/^[a-z0-9-]+$/.test(label) || label.startsWith('-') || label.endsWith('-'))) {
    throw new Error('Enter a valid email domain.');
  }

  return { local, domain, hadUnicodeDomain: rawDomain.toLowerCase() !== domain };
}

function timeout(promise, ms = DNS_TIMEOUT_MS) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(Object.assign(new Error('DNS timeout'), { code: 'ETIMEOUT' })), ms))
  ]);
}

async function queryDns(promiseFactory) {
  try {
    const records = await timeout(promiseFactory());
    return { known: true, records: Array.isArray(records) ? records : [] };
  } catch (err) {
    if (['ENODATA', 'ENOTFOUND', 'ENONAME', 'ENOTIMP', 'ENOTEMPTY'].includes(err && err.code)) {
      return { known: true, records: [] };
    }
    return { known: false, records: [] };
  }
}

function flattenTxt(records) {
  return records.map(record => Array.isArray(record) ? record.join('') : String(record || ''));
}

async function inspectDns(domain) {
  const [mx, txt, dmarc, a, aaaa, ns] = await Promise.all([
    queryDns(() => dns.resolveMx(domain)),
    queryDns(() => dns.resolveTxt(domain)),
    queryDns(() => dns.resolveTxt(`_dmarc.${domain}`)),
    queryDns(() => dns.resolve4(domain)),
    queryDns(() => dns.resolve6(domain)),
    queryDns(() => dns.resolveNs(domain))
  ]);

  const mxRecords = mx.records.filter(record => record && record.exchange && record.exchange !== '.');
  const txtRecords = flattenTxt(txt.records);
  const dmarcRecords = flattenTxt(dmarc.records);
  const domainExists = [mx.records, a.records, aaaa.records, ns.records].some(records => records.length > 0);

  return {
    domainExists,
    domainExistsKnown: mx.known || a.known || aaaa.known || ns.known,
    mxKnown: mx.known,
    hasMx: mxRecords.length > 0,
    mxCount: mxRecords.length,
    spfKnown: txt.known,
    hasSpf: txtRecords.some(value => /^v=spf1\b/i.test(value.trim())),
    dmarcKnown: dmarc.known,
    hasDmarc: dmarcRecords.some(value => /^v=dmarc1\b/i.test(value.trim()))
  };
}

function addSignal(signals, code, severity, title, detail, weight) {
  signals.push({ code, severity, title, detail, weight });
}

function findBrandLookalike(domain) {
  const label = visualNormalize(registrableLabel(domain));
  for (const [brand, officialDomains] of Object.entries(BRAND_DOMAINS)) {
    const official = officialDomains.some(officialDomain => hostMatches(domain, officialDomain));
    if (official) continue;
    const normalizedBrand = visualNormalize(brand);
    if (domain.includes(brand) || (label.length >= normalizedBrand.length && label.includes(normalizedBrand))) {
      return brand;
    }
  }
  return null;
}

function assessEmail({ local, domain, hadUnicodeDomain = false, dnsInfo }) {
  const signals = [];
  const brand = findBrandLookalike(domain);
  const label = registrableLabel(domain);

  if (domain.includes('xn--') || hadUnicodeDomain) {
    addSignal(signals, 'email-punycode', 'medium', 'Internationalized or punycode domain', 'The email domain uses an internationalized-domain encoding. This is legitimate technology, but visually confusing domains deserve extra verification.', 20);
  }

  if (brand) {
    const labelName = brand[0].toUpperCase() + brand.slice(1);
    addSignal(signals, `email-brand-${brand}`, 'high', `Possible ${labelName} lookalike domain`, `The email domain resembles ${labelName} but is not one of the recognized official domains in this checker. Verify the sender through the official website or app.`, 45);
  }

  if (DISPOSABLE_DOMAINS.has(domain)) {
    addSignal(signals, 'email-disposable', 'medium', 'Disposable email provider', 'The address uses a known temporary or disposable email domain. That does not prove fraud, but it provides less stable sender identity.', 28);
  }

  if (dnsInfo.domainExistsKnown && !dnsInfo.domainExists) {
    addSignal(signals, 'email-domain-missing', 'high', 'Email domain did not resolve', 'The domain did not return normal public DNS records during this check. The address may be mistyped, inactive, or fabricated.', 34);
  }

  if (dnsInfo.mxKnown && !dnsInfo.hasMx) {
    addSignal(signals, 'email-no-mx', 'medium', 'No MX mail record found', 'No dedicated MX record was found for this domain. This is unusual for an address expected to receive normal email, but it is not proof of fraud.', 14);
  }

  if (dnsInfo.spfKnown && !dnsInfo.hasSpf) {
    addSignal(signals, 'email-no-spf', 'low', 'No SPF policy found', 'No SPF policy was found in the domain TXT records. SPF is only one layer of sender authentication, so its absence is a weak signal.', 4);
  }

  if (dnsInfo.dmarcKnown && !dnsInfo.hasDmarc) {
    addSignal(signals, 'email-no-dmarc', 'low', 'No DMARC policy found', 'No DMARC policy was found for the domain. DMARC helps domain owners define how unauthenticated mail should be handled, but its absence alone does not mean an address is malicious.', 5);
  }

  const suspiciousTerms = SUSPICIOUS_DOMAIN_TERMS.filter(term => domain.includes(term));
  if (suspiciousTerms.length >= 2) {
    addSignal(signals, 'email-pressure-domain', 'low', 'Security or account wording in domain', `The domain contains several account or security terms (${suspiciousTerms.slice(0, 4).join(', ')}). This can be legitimate, but it is common in impersonation domains.`, 9);
  }

  const hyphens = (label.match(/-/g) || []).length;
  const digits = (label.match(/\d/g) || []).length;
  if (hyphens >= 3 || digits >= 4) {
    addSignal(signals, 'email-complex-domain', 'low', 'Unusually complex email domain', 'The main domain label contains an unusual number of hyphens or digits. Inspect the spelling carefully.', 6);
  }

  const riskScore = Math.min(100, signals.reduce((sum, signal) => sum + signal.weight, 0));
  const status = riskScore >= 60 ? 'high' : riskScore >= 25 ? 'caution' : 'low';
  const verdict = status === 'high'
    ? 'High-risk email address signals detected'
    : status === 'caution'
      ? 'Suspicious email address signals detected'
      : 'No obvious suspicious email address signals detected';

  return {
    status,
    riskScore,
    verdict,
    signals: signals.map(({ weight, ...signal }) => signal),
    checksPerformed: ['Email syntax', 'Domain DNS', 'MX mail routing', 'SPF and DMARC presence', 'Brand-lookalike patterns', 'Disposable-domain signals'],
    disclaimer: 'This checks the address and domain, not the contents of a message or the identity of the person using the mailbox. A low-risk result does not prove that the sender is trustworthy.'
  };
}

async function analyzeEmailAddress(input) {
  const parsed = parseEmailAddress(input);
  const dnsInfo = await inspectDns(parsed.domain);
  const safety = assessEmail({ ...parsed, dnsInfo });
  return {
    inputType: 'email',
    reachable: dnsInfo.domainExists,
    emailDomain: parsed.domain,
    email: {
      domain: parsed.domain,
      domainExists: dnsInfo.domainExists,
      hasMx: dnsInfo.hasMx,
      mxCount: dnsInfo.mxCount,
      hasSpf: dnsInfo.hasSpf,
      hasDmarc: dnsInfo.hasDmarc
    },
    redirects: [],
    safety
  };
}

module.exports = {
  analyzeEmailAddress,
  assessEmail,
  findBrandLookalike,
  parseEmailAddress
};
