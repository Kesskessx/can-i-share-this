'use strict';

const tls = require('node:tls');
const { analyzeEmailAddress, registrableDomain } = require('./email-safety');

const TLS_TIMEOUT_MS = 1800;
const CACHE_TTL_MS = 10 * 60 * 1000;
const cache = new Map();

function clean(v, max = 500) {
  return String(v == null ? '' : v).replace(/\0/g, '').trim().slice(0, max);
}

function normalizeDomain(value) {
  let raw = clean(value, 700).toLowerCase();
  if (!raw) return '';
  try {
    const u = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`);
    return u.hostname.toLowerCase().replace(/^www\./, '');
  } catch (_) {
    return raw.replace(/^https?:\/\//, '').split(/[\/?#]/)[0].replace(/^www\./, '');
  }
}

function tlsCertificate(domain) {
  return new Promise(resolve => {
    let settled = false;
    const finish = value => { if (!settled) { settled = true; resolve(value); } };
    const socket = tls.connect({ host: domain, port: 443, servername: domain, rejectUnauthorized: false }, () => {
      try {
        const cert = socket.getPeerCertificate(true) || {};
        const issuer = cert.issuer && typeof cert.issuer === 'object'
          ? Object.values(cert.issuer).filter(Boolean).join(', ')
          : '';
        const validFrom = cert.valid_from ? new Date(cert.valid_from).toISOString() : null;
        const validTo = cert.valid_to ? new Date(cert.valid_to).toISOString() : null;
        finish({ checked: true, available: Boolean(cert && cert.subject), validFrom, validTo, issuer: clean(issuer, 220) || null, subjectAltNames: clean(cert.subjectaltname, 600) || null });
      } catch (_) {
        finish({ checked: true, available: false });
      } finally {
        socket.destroy();
      }
    });
    socket.setTimeout(TLS_TIMEOUT_MS, () => { socket.destroy(); finish({ checked: false, available: false, reason: 'timeout' }); });
    socket.on('error', () => finish({ checked: false, available: false, reason: 'unavailable' }));
  });
}

async function inspectDomain(value) {
  const domain = normalizeDomain(value);
  if (!domain || !domain.includes('.')) return { domain, state: 'invalid' };
  const cached = cache.get(domain);
  if (cached && cached.expiresAt > Date.now()) return cached.value;

  let emailResult = null;
  let tlsInfo = null;
  await Promise.all([
    analyzeEmailAddress(`scanner@${domain}`).then(v => { emailResult = v; }).catch(() => {}),
    tlsCertificate(domain).then(v => { tlsInfo = v; }).catch(() => {})
  ]);

  const email = emailResult && emailResult.email || {};
  const safety = emailResult && emailResult.safety || {};
  const out = {
    domain,
    registrableDomain: registrableDomain(domain),
    state: emailResult ? 'checked' : 'partial',
    dns: {
      exists: email.domainExists === true,
      hasMx: email.hasMx === true,
      mxCount: Number.isFinite(email.mxCount) ? email.mxCount : null,
      hasSpf: email.hasSpf === true,
      spfQuality: email.spfQuality || null,
      hasDmarc: email.hasDmarc === true,
      dmarcPolicy: email.dmarcPolicy || null,
      dnssecKnown: email.dnssecKnown === true,
      hasDnssec: email.hasDnssec === true,
      hasMtaSts: email.hasMtaSts === true,
      hasTlsRpt: email.hasTlsRpt === true
    },
    registration: {
      known: email.rdapKnown === true,
      registeredAt: email.registeredAt || null,
      ageDays: Number.isFinite(email.domainAgeDays) ? email.domainAgeDays : null
    },
    tls: tlsInfo || { checked: false, available: false },
    risk: safety.status || 'unknown',
    riskScore: Number.isFinite(safety.riskScore) ? safety.riskScore : null,
    signals: Array.isArray(safety.signals) ? safety.signals.slice(0, 8) : [],
    sources: ['DNS', 'RDAP', ...(tlsInfo && tlsInfo.checked ? ['TLS certificate'] : [])]
  };

  if (cache.size > 200) cache.delete(cache.keys().next().value);
  cache.set(domain, { expiresAt: Date.now() + CACHE_TTL_MS, value: out });
  return out;
}

module.exports = { inspectDomain, normalizeDomain };
