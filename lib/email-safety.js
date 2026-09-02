const dns = require('node:dns').promises;
const { domainToASCII } = require('node:url');

const DNS_TIMEOUT_MS = 3500;
const RDAP_TIMEOUT_MS = 4000;

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

const COMMON_MULTI_LABEL_SUFFIXES = new Set([
  'co.uk', 'org.uk', 'me.uk', 'ac.uk',
  'com.au', 'net.au', 'org.au',
  'com.br', 'com.cn', 'com.hk', 'com.mx', 'com.sg', 'com.tr',
  'co.jp', 'co.nz', 'co.kr', 'co.in', 'co.za'
]);

function hostMatches(host, domain) {
  return host === domain || host.endsWith(`.${domain}`);
}

function registrableDomain(domain) {
  const parts = String(domain || '').toLowerCase().split('.').filter(Boolean);
  if (parts.length < 2) return parts.join('.');
  const lastTwo = parts.slice(-2).join('.');
  if (COMMON_MULTI_LABEL_SUFFIXES.has(lastTwo) && parts.length >= 3) return parts.slice(-3).join('.');
  return lastTwo;
}

function registrableLabel(domain) {
  const value = registrableDomain(domain);
  const parts = value.split('.').filter(Boolean);
  return parts[0] || '';
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

function editDistance(a, b) {
  const left = String(a || '');
  const right = String(b || '');
  if (left === right) return 0;
  if (!left.length) return right.length;
  if (!right.length) return left.length;
  let previous = Array.from({ length: right.length + 1 }, (_, i) => i);
  for (let i = 1; i <= left.length; i += 1) {
    const current = [i];
    for (let j = 1; j <= right.length; j += 1) {
      current[j] = Math.min(
        current[j - 1] + 1,
        previous[j] + 1,
        previous[j - 1] + (left[i - 1] === right[j - 1] ? 0 : 1)
      );
    }
    previous = current;
  }
  return previous[right.length];
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
    new Promise((_, reject) => setTimeout(() => reject(Object.assign(new Error('Timeout'), { code: 'ETIMEOUT' })), ms))
  ]);
}

async function queryDns(promiseFactory) {
  try {
    const records = await timeout(promiseFactory());
    return { known: true, records: Array.isArray(records) ? records : [] };
  } catch (err) {
    if (['ENODATA', 'ENOTFOUND', 'ENONAME', 'ENOTEMPTY'].includes(err && err.code)) {
      return { known: true, records: [] };
    }
    return { known: false, records: [] };
  }
}

function flattenTxt(records) {
  return records.map(record => Array.isArray(record) ? record.join('') : String(record || ''));
}

function parseTagRecord(record) {
  const out = {};
  String(record || '').split(';').forEach(part => {
    const index = part.indexOf('=');
    if (index <= 0) return;
    const key = part.slice(0, index).trim().toLowerCase();
    const value = part.slice(index + 1).trim();
    if (key) out[key] = value;
  });
  return out;
}

function analyzeSpfRecord(records) {
  const spfRecords = records.filter(value => /^v=spf1\b/i.test(String(value || '').trim()));
  const record = spfRecords[0] || '';
  const tokens = record ? record.trim().split(/\s+/).slice(1) : [];
  const allToken = tokens.find(token => /^[+?~-]?all$/i.test(token)) || '';
  const allQualifier = allToken ? (/^[+?~-]/.test(allToken) ? allToken[0] : '+') : null;
  const lookupTerms = tokens.filter(token => {
    const bare = token.replace(/^[+?~-]/, '').toLowerCase();
    return /^(include:|a(?::|\/|$)|mx(?::|\/|$)|ptr(?::|$)|exists:)/.test(bare) || /^redirect=/.test(bare);
  });
  const usesPtr = tokens.some(token => /^[-+?~]?ptr(?::|$)/i.test(token));
  let quality = 'present';
  if (!record) quality = 'missing';
  else if (spfRecords.length > 1) quality = 'invalid-multiple';
  else if (allQualifier === '+') quality = 'permissive';
  else if (allQualifier === '?') quality = 'neutral';
  else if (allQualifier === '-') quality = 'strict';
  else if (allQualifier === '~') quality = 'softfail';

  return {
    record,
    recordCount: spfRecords.length,
    allQualifier,
    lookupCount: lookupTerms.length,
    potentialLookupOverflow: lookupTerms.length > 10,
    usesPtr,
    quality
  };
}

function analyzeDmarcRecord(records) {
  const dmarcRecords = records.filter(value => /^v=dmarc1\b/i.test(String(value || '').trim()));
  const record = dmarcRecords[0] || '';
  const tags = parseTagRecord(record);
  const testingValue = String(tags.t || '').toLowerCase();
  const legacyPctValue = tags.pct === undefined ? null : Number.parseInt(tags.pct, 10);
  return {
    record,
    recordCount: dmarcRecords.length,
    policy: String(tags.p || '').toLowerCase() || null,
    subdomainPolicy: String(tags.sp || '').toLowerCase() || null,
    testing: testingValue === 'y' ? true : testingValue === 'n' ? false : null,
    legacyPct: Number.isFinite(legacyPctValue) ? Math.max(0, Math.min(100, legacyPctValue)) : null
  };
}

async function inspectDns(domain) {
  const [mx, txt, dmarc, a, aaaa, ns, ds, mtaSts, tlsRpt] = await Promise.all([
    queryDns(() => dns.resolveMx(domain)),
    queryDns(() => dns.resolveTxt(domain)),
    queryDns(() => dns.resolveTxt(`_dmarc.${domain}`)),
    queryDns(() => dns.resolve4(domain)),
    queryDns(() => dns.resolve6(domain)),
    queryDns(() => dns.resolveNs(domain)),
    queryDns(() => dns.resolve(domain, 'DS')),
    queryDns(() => dns.resolveTxt(`_mta-sts.${domain}`)),
    queryDns(() => dns.resolveTxt(`_smtp._tls.${domain}`))
  ]);

  const mxRecords = mx.records.filter(record => record && record.exchange && record.exchange !== '.');
  const txtRecords = flattenTxt(txt.records);
  const dmarcRecords = flattenTxt(dmarc.records);
  const mtaStsRecords = flattenTxt(mtaSts.records);
  const tlsRptRecords = flattenTxt(tlsRpt.records);
  const domainExists = [mx.records, a.records, aaaa.records, ns.records].some(records => records.length > 0);
  const spf = analyzeSpfRecord(txtRecords);
  const dmarcInfo = analyzeDmarcRecord(dmarcRecords);

  return {
    domainExists,
    domainExistsKnown: mx.known || a.known || aaaa.known || ns.known,
    mxKnown: mx.known,
    hasMx: mxRecords.length > 0,
    mxCount: mxRecords.length,
    spfKnown: txt.known,
    hasSpf: spf.recordCount > 0,
    spf,
    dmarcKnown: dmarc.known,
    hasDmarc: dmarcInfo.recordCount > 0,
    dmarc: dmarcInfo,
    dnssecKnown: ds.known,
    hasDnssec: ds.records.length > 0,
    mtaStsKnown: mtaSts.known,
    hasMtaSts: mtaStsRecords.some(value => /^v=stsv1\b/i.test(value.trim())),
    tlsRptKnown: tlsRpt.known,
    hasTlsRpt: tlsRptRecords.some(value => /^v=tlsrptv1\b/i.test(value.trim()))
  };
}

function extractRegistrationDate(payload) {
  const events = Array.isArray(payload && payload.events) ? payload.events : [];
  const preferred = ['registration', 'registered', 'created', 'creation'];
  for (const action of preferred) {
    const match = events.find(event => String(event && event.eventAction || '').toLowerCase() === action && event.eventDate);
    if (match) return String(match.eventDate);
  }
  return null;
}

async function inspectRdap(domain) {
  if (typeof globalThis.fetch !== 'function') return { known: false, queriedDomain: registrableDomain(domain), registeredAt: null, ageDays: null };
  const queriedDomain = registrableDomain(domain);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
  try {
    const response = await globalThis.fetch(`https://rdap.org/domain/${encodeURIComponent(queriedDomain)}`, {
      method: 'GET',
      headers: { accept: 'application/rdap+json, application/json' },
      redirect: 'follow',
      signal: controller.signal
    });
    if (!response.ok) return { known: false, queriedDomain, registeredAt: null, ageDays: null };
    const payload = await response.json();
    const registeredAt = extractRegistrationDate(payload);
    if (!registeredAt) return { known: true, queriedDomain, registeredAt: null, ageDays: null };
    const createdMs = Date.parse(registeredAt);
    if (!Number.isFinite(createdMs)) return { known: true, queriedDomain, registeredAt: null, ageDays: null };
    const ageDays = Math.max(0, Math.floor((Date.now() - createdMs) / 86400000));
    return { known: true, queriedDomain, registeredAt: new Date(createdMs).toISOString(), ageDays };
  } catch (_) {
    return { known: false, queriedDomain, registeredAt: null, ageDays: null };
  } finally {
    clearTimeout(timer);
  }
}

function addSignal(signals, code, severity, title, detail, weight) {
  signals.push({ code, severity, title, detail, weight });
}

function findBrandLookalike(domain) {
  const rawLabel = registrableLabel(domain).toLowerCase();
  const label = visualNormalize(rawLabel);
  const hasPressureTerm = SUSPICIOUS_DOMAIN_TERMS.some(term => rawLabel.includes(term));
  for (const [brand, officialDomains] of Object.entries(BRAND_DOMAINS)) {
    const official = officialDomains.some(officialDomain => hostMatches(domain, officialDomain));
    if (official) continue;
    const normalizedBrand = visualNormalize(brand);
    const exact = label === normalizedBrand;
    const embeddedWithPressure = hasPressureTerm && (label.startsWith(normalizedBrand) || label.endsWith(normalizedBrand));
    const maxDistance = normalizedBrand.length >= 7 ? 2 : 1;
    const near = Math.abs(label.length - normalizedBrand.length) <= maxDistance && editDistance(label, normalizedBrand) <= maxDistance;
    if (exact || embeddedWithPressure || near) return brand;
  }
  return null;
}

function assessEmail({ local, domain, hadUnicodeDomain = false, dnsInfo, rdapInfo = {} }) {
  const signals = [];
  const brand = findBrandLookalike(domain);
  const label = registrableLabel(domain);
  const spf = dnsInfo.spf || {};
  const dmarc = dnsInfo.dmarc || {};

  if (domain.includes('xn--') || hadUnicodeDomain) {
    addSignal(signals, 'email-punycode', 'medium', 'Internationalized or punycode domain', 'The email domain uses an internationalized-domain encoding. This is legitimate technology, but visually confusing domains deserve extra verification.', 20);
  }

  if (brand) {
    const labelName = brand[0].toUpperCase() + brand.slice(1);
    addSignal(signals, `email-brand-${brand}`, 'high', `Possible ${labelName} lookalike domain`, `The email domain closely resembles ${labelName} but is not one of the recognized official domains in this checker. Verify the sender through the official website or app.`, 45);
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
  } else if (dnsInfo.hasSpf) {
    if (spf.recordCount > 1) {
      addSignal(signals, 'email-spf-multiple', 'medium', 'Multiple SPF policies found', 'More than one SPF record was found. Multiple SPF records can make SPF evaluation invalid or unreliable.', 10);
    }
    if (spf.allQualifier === '+') {
      addSignal(signals, 'email-spf-permissive', 'medium', 'SPF policy is unusually permissive', 'The SPF policy ends in +all or an unqualified all mechanism, which can authorize any sender. That weakens the domain authentication signal.', 18);
    } else if (spf.allQualifier === '?') {
      addSignal(signals, 'email-spf-neutral', 'low', 'SPF policy uses a neutral all mechanism', 'The SPF policy uses ?all, which does not provide a strong pass-or-fail position for otherwise unmatched senders.', 5);
    }
    if (spf.potentialLookupOverflow) {
      addSignal(signals, 'email-spf-lookups', 'low', 'SPF policy may exceed lookup limits', 'The SPF record contains more than ten obvious DNS-lookup mechanisms. Complex SPF policies can fail evaluation if the protocol lookup limit is exceeded.', 7);
    }
    if (spf.usesPtr) {
      addSignal(signals, 'email-spf-ptr', 'low', 'SPF policy uses the deprecated ptr mechanism', 'The SPF record uses ptr, a mechanism discouraged by the SPF specification because it is slow and unreliable.', 3);
    }
  }

  if (dnsInfo.dmarcKnown && !dnsInfo.hasDmarc) {
    addSignal(signals, 'email-no-dmarc', 'low', 'No DMARC policy found', 'No DMARC policy was found for the domain. DMARC helps domain owners define how unauthenticated mail should be handled, but its absence alone does not mean an address is malicious.', 5);
  } else if (dnsInfo.hasDmarc) {
    if (dmarc.recordCount > 1) {
      addSignal(signals, 'email-dmarc-multiple', 'medium', 'Multiple DMARC policies found', 'More than one DMARC record was detected. A domain should publish a single applicable DMARC policy.', 8);
    }
    if (dmarc.policy === 'none') {
      addSignal(signals, 'email-dmarc-monitoring', 'low', 'DMARC is monitoring only', 'The domain publishes DMARC with p=none. This provides reporting and alignment information but does not request quarantine or rejection of failing messages.', 3);
    }
    if (dmarc.testing === true) {
      addSignal(signals, 'email-dmarc-testing', 'low', 'DMARC testing mode is enabled', 'The DMARC record uses t=y, indicating testing behavior under the current DMARC specification. Treat the published enforcement posture with additional context.', 2);
    }
  }

  if (Number.isFinite(rdapInfo.ageDays)) {
    if (rdapInfo.ageDays <= 7) {
      addSignal(signals, 'email-domain-age-7', 'high', 'Domain registered within the last week', `Public RDAP data indicates the domain was registered about ${rdapInfo.ageDays} day${rdapInfo.ageDays === 1 ? '' : 's'} ago. New domains can be legitimate, but very recent registration deserves strong verification when the sender is unexpected.`, 30);
    } else if (rdapInfo.ageDays <= 30) {
      addSignal(signals, 'email-domain-age-30', 'medium', 'Very recently registered domain', `Public RDAP data indicates the domain was registered about ${rdapInfo.ageDays} days ago. Recent registration is not proof of fraud, but it increases uncertainty for an unexpected sender.`, 22);
    } else if (rdapInfo.ageDays <= 90) {
      addSignal(signals, 'email-domain-age-90', 'medium', 'Recently registered domain', `Public RDAP data indicates the domain is about ${rdapInfo.ageDays} days old. Treat the age as context rather than proof of malicious intent.`, 14);
    } else if (rdapInfo.ageDays <= 365) {
      addSignal(signals, 'email-domain-age-365', 'low', 'Relatively new domain', `Public RDAP data indicates the domain is about ${rdapInfo.ageDays} days old. New businesses and projects can legitimately use new domains.`, 5);
    }
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
    checksPerformed: [
      'Email syntax',
      'Domain DNS',
      'MX mail routing',
      'SPF and DMARC presence',
      'SPF policy quality',
      'DMARC enforcement and testing policy',
      'DNSSEC DS presence',
      'MTA-STS and TLS reporting presence',
      'Domain registration age via RDAP',
      'Brand-lookalike patterns',
      'Disposable-domain signals'
    ],
    disclaimer: 'This checks the address and domain, not the contents of a message or the identity of the person using the mailbox. A low-risk result does not prove that the sender is trustworthy. Domain-age data is best-effort and may be unavailable for some registries.'
  };
}

async function analyzeEmailAddress(input) {
  const parsed = parseEmailAddress(input);
  const [dnsInfo, rdapInfo] = await Promise.all([
    inspectDns(parsed.domain),
    inspectRdap(parsed.domain)
  ]);
  const safety = assessEmail({ ...parsed, dnsInfo, rdapInfo });
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
      spfQuality: dnsInfo.spf ? dnsInfo.spf.quality : 'unknown',
      spfLookupCount: dnsInfo.spf ? dnsInfo.spf.lookupCount : null,
      hasDmarc: dnsInfo.hasDmarc,
      dmarcPolicy: dnsInfo.dmarc ? dnsInfo.dmarc.policy : null,
      dmarcSubdomainPolicy: dnsInfo.dmarc ? dnsInfo.dmarc.subdomainPolicy : null,
      dmarcTesting: dnsInfo.dmarc ? dnsInfo.dmarc.testing : null,
      dnssecKnown: dnsInfo.dnssecKnown,
      hasDnssec: dnsInfo.hasDnssec,
      mtaStsKnown: dnsInfo.mtaStsKnown,
      hasMtaSts: dnsInfo.hasMtaSts,
      tlsRptKnown: dnsInfo.tlsRptKnown,
      hasTlsRpt: dnsInfo.hasTlsRpt,
      rdapKnown: rdapInfo.known,
      registeredAt: rdapInfo.registeredAt,
      domainAgeDays: rdapInfo.ageDays
    },
    redirects: [],
    safety
  };
}

module.exports = {
  analyzeEmailAddress,
  assessEmail,
  findBrandLookalike,
  parseEmailAddress,
  analyzeSpfRecord,
  analyzeDmarcRecord,
  registrableDomain
};
