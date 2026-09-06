'use strict';

const dns = require('node:dns').promises;
const net = require('node:net');

const FETCH_TIMEOUT_MS = 3200;
const DNS_TIMEOUT_MS = 1200;
const MAX_HTML_BYTES = 140000;
const SOCIAL_HOSTS = new Set([
  'x.com','twitter.com','instagram.com','facebook.com','tiktok.com','youtube.com','linkedin.com','t.me','telegram.me','discord.com','discord.gg'
]);
const NON_DOMAIN_TLDS = new Set([
  'pdf','doc','docx','xls','xlsx','ppt','pptx','zip','rar','7z','exe','msi','msix','scr','bat','cmd','com','ps1','vbs','jar','apk','dmg','pkg','iso','img','hta','appinstaller','jpg','jpeg','png','webp','gif','svg','mp3','mp4','mov','avi','mkv','txt','csv'
]);

function clean(v, max = 600) {
  return String(v == null ? '' : v).replace(/\0/g, '').replace(/\s+/g, ' ').trim().slice(0, max);
}

function isPrivateIPv4(ip) {
  const p = ip.split('.').map(Number);
  if (p.length !== 4 || p.some(n => !Number.isInteger(n) || n < 0 || n > 255)) return true;
  return p[0] === 10 || p[0] === 127 || p[0] === 0 ||
    (p[0] === 169 && p[1] === 254) ||
    (p[0] === 172 && p[1] >= 16 && p[1] <= 31) ||
    (p[0] === 192 && p[1] === 168) ||
    (p[0] === 100 && p[1] >= 64 && p[1] <= 127) || p[0] >= 224;
}
function isPrivateIPv6(ip) {
  const x = String(ip || '').toLowerCase();
  return x === '::1' || x === '::' || x.startsWith('fc') || x.startsWith('fd') ||
    x.startsWith('fe8') || x.startsWith('fe9') || x.startsWith('fea') || x.startsWith('feb') ||
    x.startsWith('::ffff:127.') || x.startsWith('::ffff:10.') || x.startsWith('::ffff:192.168.') || x.startsWith('::ffff:169.254.');
}
function isPrivateIp(ip) {
  const family = net.isIP(ip);
  if (family === 4) return isPrivateIPv4(ip);
  if (family === 6) return isPrivateIPv6(ip);
  return true;
}

async function resolvePublic(hostname) {
  const h = clean(hostname, 253).toLowerCase();
  if (!h || h === 'localhost' || h.endsWith('.localhost') || h.endsWith('.local') || h === 'metadata.google.internal') throw new Error('Private host');
  const records = await Promise.race([
    dns.lookup(h, { all: true, verbatim: true }),
    new Promise((_, reject) => setTimeout(() => reject(new Error('DNS timeout')), DNS_TIMEOUT_MS))
  ]);
  if (!records.length || records.some(r => isPrivateIp(r.address))) throw new Error('Private host');
  return records;
}

function canonicalSocial(value) {
  try {
    const u = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);
    const host = u.hostname.toLowerCase().replace(/^www\./, '');
    const parts = u.pathname.split('/').filter(Boolean);
    let platform = '', handle = '';
    if (host === 'x.com' || host === 'twitter.com') { platform = 'x'; handle = parts[0] || ''; }
    else if (host === 'instagram.com') { platform = 'instagram'; handle = parts[0] || ''; }
    else if (host === 'tiktok.com') { platform = 'tiktok'; handle = (parts.find(x => x.startsWith('@')) || '').replace(/^@/, ''); }
    else if (host === 'facebook.com') { platform = 'facebook'; handle = parts[0] || ''; }
    else if (host === 'youtube.com') { platform = 'youtube'; handle = parts[0] || ''; }
    else if (host === 'linkedin.com') { platform = 'linkedin'; handle = parts.slice(0, 2).join('/'); }
    else if (host === 't.me' || host === 'telegram.me') { platform = 'telegram'; handle = parts[0] || ''; }
    else if (host === 'discord.com' || host === 'discord.gg') { platform = 'discord'; handle = parts.join('/'); }
    if (!platform || !handle) return null;
    return { platform, handle: handle.toLowerCase().replace(/^@/, ''), host, url: u.toString() };
  } catch (_) { return null; }
}

function socialFromProfile(profile) {
  if (!profile || typeof profile !== 'object') return null;
  const username = clean(profile.username, 120).replace(/^@/, '');
  const platform = clean(profile.platform, 40).toLowerCase();
  if (!username) return null;
  if (platform.includes('instagram')) return canonicalSocial(`https://instagram.com/${username}`);
  if (platform.includes('tiktok')) return canonicalSocial(`https://tiktok.com/@${username}`);
  if (platform === 'x' || platform.includes('twitter')) return canonicalSocial(`https://x.com/${username}`);
  if (platform.includes('facebook')) return canonicalSocial(`https://facebook.com/${username}`);
  if (platform.includes('telegram')) return canonicalSocial(`https://t.me/${username}`);
  return null;
}

function extractDomainsFromText(text) {
  const out = [], seen = new Set();
  const re = /(?:https?:\/\/)?(?:www\.)?([a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?(?:\.[a-z]{2,24})+)(?:[\/:?#][^\s<>"']*)?/gi;
  let m;
  while ((m = re.exec(String(text || ''))) && out.length < 8) {
    const domain = clean(m[1], 253).toLowerCase().replace(/^www\./, '');
    const tld = domain.split('.').pop();
    if (!domain || NON_DOMAIN_TLDS.has(tld) || SOCIAL_HOSTS.has(domain) || seen.has(domain)) continue;
    seen.add(domain);
    out.push(domain);
  }
  return out;
}

function hrefs(html, baseUrl) {
  const out = [];
  const seen = new Set();
  const re = /<a\b[^>]*\bhref\s*=\s*(["'])(.*?)\1/gi;
  let m;
  while ((m = re.exec(String(html || ''))) && out.length < 100) {
    let raw = m[2].replace(/&amp;/gi, '&').trim();
    if (!raw || /^javascript:|^mailto:|^tel:/i.test(raw)) continue;
    try {
      const u = new URL(raw, baseUrl);
      if (!['http:', 'https:'].includes(u.protocol)) continue;
      const value = u.toString();
      if (seen.has(value)) continue;
      seen.add(value); out.push(value);
    } catch (_) {}
  }
  return out;
}

async function fetchPublicHtml(urlValue) {
  let current;
  try { current = new URL(/^https?:\/\//i.test(urlValue) ? urlValue : `https://${urlValue}`); } catch (_) { return { state: 'invalid' }; }
  if (!['http:', 'https:'].includes(current.protocol) || current.username || current.password) return { state: 'invalid' };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    for (let hop = 0; hop < 3; hop++) {
      await resolvePublic(current.hostname);
      const r = await fetch(current.toString(), {
        redirect: 'manual', signal: controller.signal,
        headers: {
          'user-agent': 'Mozilla/5.0 (compatible; CanIShareThis/3.0; +https://canisharethis.com)',
          'accept': 'text/html,application/xhtml+xml', 'accept-language': 'en-US,en;q=0.8'
        }
      });
      if (r.status >= 300 && r.status < 400) {
        const loc = r.headers.get('location'); if (!loc) return { state: 'redirect-without-location' };
        const next = new URL(loc, current); if (!['http:', 'https:'].includes(next.protocol)) return { state: 'blocked-redirect' };
        current = next; continue;
      }
      const type = String(r.headers.get('content-type') || '').toLowerCase();
      if (!r.ok || (type && !type.includes('text/html') && !type.includes('application/xhtml+xml'))) return { state: 'unavailable', status: r.status, finalUrl: current.toString() };
      const reader = r.body && r.body.getReader ? r.body.getReader() : null;
      let html = '';
      if (reader) {
        const chunks = []; let total = 0;
        while (total < MAX_HTML_BYTES) {
          const { done, value } = await reader.read(); if (done) break;
          const remaining = MAX_HTML_BYTES - total; const part = value.byteLength > remaining ? value.slice(0, remaining) : value;
          chunks.push(Buffer.from(part)); total += part.byteLength; if (part.byteLength < value.byteLength) break;
        }
        try { await reader.cancel(); } catch (_) {}
        html = Buffer.concat(chunks).toString('utf8');
      } else html = (await r.text()).slice(0, MAX_HTML_BYTES);
      return { state: 'read', status: r.status, finalUrl: current.toString(), html };
    }
    return { state: 'too-many-redirects' };
  } catch (err) {
    return { state: err && err.name === 'AbortError' ? 'timeout' : 'unavailable' };
  } finally { clearTimeout(timer); }
}

function sameSocial(a, b) {
  return Boolean(a && b && a.platform === b.platform && a.handle === b.handle);
}

async function verifyWebsiteSocialRelationship({ websites = [], socialProfile = null }) {
  const social = socialFromProfile(socialProfile);
  if (!social) return [];
  const domains = [];
  for (const item of websites) {
    try {
      const u = new URL(/^https?:\/\//i.test(item) ? item : `https://${item}`);
      const d = u.hostname.toLowerCase().replace(/^www\./, '');
      if (!SOCIAL_HOSTS.has(d) && !domains.includes(d)) domains.push(d);
    } catch (_) {}
  }
  const results = [];
  for (const domain of domains.slice(0, 2)) {
    const page = await fetchPublicHtml(`https://${domain}/`);
    if (page.state !== 'read') {
      results.push({ type: 'website-social', websiteDomain: domain, socialPlatform: social.platform, socialHandle: social.handle, status: 'unavailable', positive: false, detail: `Could not independently read ${domain} to verify its social links.` });
      continue;
    }
    const links = hrefs(page.html, page.finalUrl);
    const socialLinks = links.map(canonicalSocial).filter(Boolean);
    const exact = socialLinks.find(x => sameSocial(x, social));
    if (exact) {
      results.push({ type: 'website-social', websiteDomain: domain, socialPlatform: social.platform, socialHandle: social.handle, status: 'confirmed', positive: true, detail: `${domain} links to the same ${social.platform.toUpperCase()} profile @${social.handle}.` });
    } else {
      results.push({ type: 'website-social', websiteDomain: domain, socialPlatform: social.platform, socialHandle: social.handle, status: 'not-found', positive: false, detail: `${domain} was readable, but a link to this exact ${social.platform.toUpperCase()} profile was not found on the homepage.` });
    }
  }
  return results;
}

module.exports = { verifyWebsiteSocialRelationship, extractDomainsFromText, canonicalSocial };
