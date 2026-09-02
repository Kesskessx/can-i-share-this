const net = require('node:net');
const { domainToASCII } = require('node:url');

const RDAP_TIMEOUT_MS = 2500;
const COMMON_MULTI_LABEL_SUFFIXES = new Set([
  'co.uk', 'org.uk', 'me.uk', 'ac.uk',
  'com.au', 'net.au', 'org.au',
  'com.br', 'com.cn', 'com.hk', 'com.mx', 'com.sg', 'com.tr',
  'co.jp', 'co.nz', 'co.kr', 'co.in', 'co.za'
]);

function registrableDomain(hostname) {
  const parts = String(hostname || '').toLowerCase().replace(/\.$/, '').split('.').filter(Boolean);
  if (parts.length < 2) return parts.join('.');
  const lastTwo = parts.slice(-2).join('.');
  if (COMMON_MULTI_LABEL_SUFFIXES.has(lastTwo) && parts.length >= 3) return parts.slice(-3).join('.');
  return lastTwo;
}

function normalizeDomain(input) {
  let value = String(input || '').trim();
  if (!value || value.length > 253) throw new Error('Enter a public domain name.');
  try {
    value = value.includes('://') ? new URL(value).hostname : new URL(`https://${value}`).hostname;
  } catch {
    throw new Error('Enter a valid public domain name.');
  }
  value = domainToASCII(value.toLowerCase().replace(/\.$/, ''));
  if (!value || value.length > 253 || net.isIP(value)) throw new Error('Domain age is available for public domain names only.');
  const labels = value.split('.');
  if (labels.length < 2 || labels.some(label => !label || label.length > 63 || !/^[a-z0-9-]+$/.test(label) || label.startsWith('-') || label.endsWith('-'))) {
    throw new Error('Enter a valid public domain name.');
  }
  return registrableDomain(value);
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

async function inspectDomainAge(domain) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
  try {
    const response = await fetch(`https://rdap.org/domain/${encodeURIComponent(domain)}`, {
      method: 'GET',
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        accept: 'application/rdap+json, application/json',
        'user-agent': 'CanIShareThis/1.6 (+https://canisharethis.com)'
      }
    });
    if (!response.ok) return { known: false, queriedDomain: domain, registeredAt: null, ageDays: null };
    const payload = await response.json();
    const registeredAt = extractRegistrationDate(payload);
    if (!registeredAt) return { known: true, queriedDomain: domain, registeredAt: null, ageDays: null };
    const createdMs = Date.parse(registeredAt);
    if (!Number.isFinite(createdMs)) return { known: true, queriedDomain: domain, registeredAt: null, ageDays: null };
    const ageDays = Math.max(0, Math.floor((Date.now() - createdMs) / 86400000));
    return { known: true, queriedDomain: domain, registeredAt: new Date(createdMs).toISOString(), ageDays };
  } catch {
    return { known: false, queriedDomain: domain, registeredAt: null, ageDays: null };
  } finally {
    clearTimeout(timer);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let domain = '';
  try {
    const raw = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    domain = normalizeDomain(raw.domain || raw.host || '');
  } catch (err) {
    return res.status(200).json({ known: false, queriedDomain: null, registeredAt: null, ageDays: null, error: err?.message || 'Invalid domain.' });
  }

  const result = await inspectDomainAge(domain);
  return res.status(200).json({ ...result, source: 'RDAP', privacy: 'Only the registered domain is queried. The full URL is not sent for this lookup.' });
};
