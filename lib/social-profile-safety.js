function cleanText(value, max = 500) {
  return String(value || '').replace(/\u0000/g, '').trim().slice(0, max);
}

const PLATFORM_HOSTS = [
  { platform: 'Instagram', hosts: ['instagram.com', 'www.instagram.com'] },
  { platform: 'Facebook', hosts: ['facebook.com', 'www.facebook.com', 'm.facebook.com'] },
  { platform: 'TikTok', hosts: ['tiktok.com', 'www.tiktok.com'] },
  { platform: 'X', hosts: ['x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'] },
  { platform: 'Telegram', hosts: ['t.me', 'telegram.me', 'www.telegram.me'] },
  { platform: 'Discord', hosts: ['discord.com', 'www.discord.com', 'discordapp.com', 'www.discordapp.com'] }
];

const RESERVED = {
  Instagram: new Set(['p', 'reel', 'reels', 'stories', 'explore', 'accounts', 'direct', 'about', 'developer']),
  Facebook: new Set(['watch', 'groups', 'marketplace', 'gaming', 'events', 'reel', 'reels', 'share', 'help', 'privacy']),
  TikTok: new Set(['discover', 'explore', 'foryou', 'live', 'login', 'signup', 'about']),
  X: new Set(['home', 'explore', 'search', 'messages', 'settings', 'i', 'intent', 'share', 'compose', 'notifications']),
  Telegram: new Set(['joinchat', 'share', 'proxy', 'socks']),
  Discord: new Set([])
};

const BRANDS = [
  'paypal', 'amazon', 'netflix', 'apple', 'microsoft', 'google', 'meta', 'instagram', 'facebook',
  'tiktok', 'twitter', 'telegram', 'discord', 'binance', 'coinbase', 'revolut', 'wise', 'stripe',
  'dhl', 'fedex', 'ups', 'usps', 'chronopost', 'laposte', 'whatsapp', 'chase', 'barclays', 'hsbc',
  'santander', 'natwest', 'monzo', 'n26'
];

const AUTHORITY_WORDS = ['support', 'help', 'security', 'secure', 'verify', 'verification', 'official', 'service', 'customer', 'recovery', 'admin'];
const MONEY_WORDS = ['crypto', 'bitcoin', 'btc', 'wallet', 'giveaway', 'airdrop', 'invest', 'investment', 'trading', 'giftcard', 'gift-card', 'prize', 'profit', 'returns'];
const CREDENTIAL_PHRASES = ['password', 'verification code', 'security code', 'one time code', 'one-time code', 'otp', 'login code', 'send code', 'share code', 'verify your account', 'confirm your account'];
const RECOVERY_PHRASES = ['seed phrase', 'recovery phrase', 'wallet recovery', 'account recovery service', 'recover your account', 'unlock your account'];
const URGENCY_PHRASES = ['urgent', 'immediately', 'act now', 'limited time', 'final notice', 'account suspended', 'account locked', 'expires today'];
const PAYMENT_PHRASES = ['send money', 'pay a fee', 'payment required', 'wire transfer', 'gift card', 'guaranteed return', 'guaranteed profit', 'double your', 'investment opportunity'];
const CONTACT_PHRASES = ['contact me on whatsapp', 'message me on whatsapp', 'contact on telegram', 'message on telegram', 'dm me', 'private message me', 'contact support on'];
const SHORTENER_HOSTS = new Set(['bit.ly', 't.co', 'tinyurl.com', 'is.gd', 'ow.ly', 'buff.ly', 'rebrand.ly', 'cutt.ly', 'rb.gy']);
const VERIFY_SYMBOL_RE = /[✓✔☑✅☒☑︎]/u;
const URL_RE = /https?:\/\/[^\s<>"')\]]+/ig;

function platformForHost(hostname) {
  const host = String(hostname || '').toLowerCase();
  for (const item of PLATFORM_HOSTS) if (item.hosts.includes(host)) return item.platform;
  return null;
}

function supportedSocialUrl(value) {
  try {
    const url = new URL(value);
    return Boolean(platformForHost(url.hostname));
  } catch (_) {
    return false;
  }
}

function extractProfile(input) {
  const value = cleanText(input, 4000);
  const handleMatch = value.match(/^@([A-Za-z0-9._-]{2,64})(?:\s+[\s\S]*)?$/);
  if (handleMatch && !/^https?:\/\//i.test(value)) {
    const context = cleanText(value.slice(handleMatch[0].indexOf(handleMatch[1]) + handleMatch[1].length + 1), 1800);
    return { platform: 'Unknown social platform', username: handleMatch[1], url: null, source: context ? 'handle+context' : 'handle', suppliedContext: context };
  }

  const urls = value.match(URL_RE) || [];
  let url = null;
  for (const raw of urls) {
    if (!supportedSocialUrl(raw)) continue;
    try { url = new URL(raw); break; } catch (_) {}
  }
  if (!url) {
    try {
      const direct = new URL(value);
      if (platformForHost(direct.hostname)) url = direct;
    } catch (_) {}
  }
  if (!url) return null;

  const platform = platformForHost(url.hostname);
  const parts = url.pathname.split('/').filter(Boolean).map(v => {
    try { return decodeURIComponent(v); } catch (_) { return v; }
  });
  let username = '';

  if (platform === 'TikTok') {
    const p = parts.find(v => v.startsWith('@'));
    username = p ? p.slice(1) : '';
  } else if (platform === 'Discord') {
    if (parts[0] === 'users' && parts[1]) username = parts[1];
  } else if (platform === 'Facebook') {
    if (url.pathname.toLowerCase() === '/profile.php') username = url.searchParams.get('id') || '';
    else username = parts[0] || '';
  } else {
    username = parts[0] || '';
  }

  if (username && RESERVED[platform] && RESERVED[platform].has(username.toLowerCase())) username = '';
  if (platform === 'Telegram' && (username.startsWith('+') || username.toLowerCase() === 'joinchat')) username = '';

  const normalizedUrl = url.toString();
  const context = cleanText(value.replace(normalizedUrl, '').replace(url.href, '').replace(url.toString(), ''), 1800);
  return { platform, username, url: normalizedUrl, source: context ? 'url+context' : 'url', suppliedContext: context };
}

function skeleton(value) {
  return String(value || '')
    .normalize('NFKD')
    .replace(/[IІӀⅼ]/g, 'l')
    .toLowerCase()
    .replace(/[а]/g, 'a').replace(/[е]/g, 'e').replace(/[о]/g, 'o').replace(/[р]/g, 'p')
    .replace(/[с]/g, 'c').replace(/[х]/g, 'x').replace(/[у]/g, 'y').replace(/[к]/g, 'k')
    .replace(/[м]/g, 'm').replace(/[т]/g, 't').replace(/[в]/g, 'b').replace(/[н]/g, 'h')
    .replace(/0/g, 'o').replace(/1/g, 'l').replace(/3/g, 'e').replace(/4/g, 'a').replace(/5/g, 's').replace(/7/g, 't')
    .replace(/[^a-z0-9]/g, '');
}

function compact(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function brandEvidence(value) {
  const raw = cleanText(value, 300);
  const skel = skeleton(raw);
  const literal = compact(raw);
  for (const brand of BRANDS) {
    if (!skel.includes(brand)) continue;
    return { brand, obfuscated: !literal.includes(brand) && skel.includes(brand), skeleton: skel };
  }
  return null;
}

function normalizedWords(value) {
  return String(value || '').toLowerCase().replace(/[._-]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function hasWord(value, words) {
  const low = normalizedWords(value);
  const compacted = low.replace(/\s+/g, '');
  return words.some(word => low.split(/\s+/).includes(word) || compacted.includes(word.replace(/[-\s]/g, '')));
}

function containsPhrase(value, phrases) {
  const low = normalizedWords(value);
  return phrases.some(phrase => low.includes(phrase));
}

function decodeHtml(value) {
  return cleanText(String(value || '')
    .replace(/&amp;/gi, '&').replace(/&quot;/gi, '"').replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<').replace(/&gt;/gi, '>').replace(/&nbsp;/gi, ' ')
    .replace(/&#(\d+);/g, (_, n) => { try { return String.fromCodePoint(Number(n)); } catch { return ''; } })
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => { try { return String.fromCodePoint(parseInt(n, 16)); } catch { return ''; } }), 1000);
}

function attr(tag, name) {
  const match = String(tag || '').match(new RegExp('\\b' + name + '\\s*=\\s*(["\\\'])([\\s\\S]*?)\\1', 'i'));
  return match ? decodeHtml(match[2]) : '';
}

function parseMetadata(html) {
  const source = String(html || '').slice(0, 350000);
  const meta = Object.create(null);
  const tags = source.match(/<meta\b[^>]*>/gi) || [];
  for (const tag of tags) {
    const key = (attr(tag, 'property') || attr(tag, 'name')).toLowerCase();
    const content = attr(tag, 'content');
    if (key && content && !meta[key]) meta[key] = content;
  }
  const titleMatch = source.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  const title = decodeHtml(meta['og:title'] || meta['twitter:title'] || (titleMatch ? titleMatch[1].replace(/<[^>]+>/g, ' ') : ''));
  const description = decodeHtml(meta['og:description'] || meta['twitter:description'] || meta.description || '');
  return { title: cleanText(title, 260), description: cleanText(description, 700) };
}

function cleanDisplayName(title, platform, username) {
  let out = cleanText(title, 220);
  if (!out) return '';
  const u = String(username || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  if (u) out = out.replace(new RegExp('\\(@?' + u + '\\)', 'ig'), '').replace(new RegExp('@' + u, 'ig'), '');
  out = out.replace(/\s*[|•·-]\s*(Instagram|Facebook|TikTok|X|Twitter|Telegram|Discord).*$/i, '')
    .replace(/\s+on\s+(Instagram|Facebook|TikTok|X|Twitter|Telegram|Discord).*$/i, '')
    .replace(/\s*\(.*?photos and videos.*?\)\s*$/i, '')
    .trim();
  if (platform && out.toLowerCase() === platform.toLowerCase()) return '';
  return cleanText(out, 160);
}

async function fetchPublicMetadata(profile) {
  if (!profile || !profile.url) return { state: 'not-requested', title: '', displayName: '', description: '', statusCode: null, finalUrl: null };
  let current;
  try { current = new URL(profile.url); } catch (_) { return { state: 'unavailable', title: '', displayName: '', description: '', statusCode: null, finalUrl: null }; }
  if (!platformForHost(current.hostname)) return { state: 'unavailable', title: '', displayName: '', description: '', statusCode: null, finalUrl: null };
  if (current.protocol !== 'https:') current.protocol = 'https:';

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2400);
  try {
    let response = null;
    for (let hop = 0; hop < 3; hop++) {
      response = await fetch(current.toString(), {
        redirect: 'manual',
        signal: controller.signal,
        headers: {
          'user-agent': 'Mozilla/5.0 (compatible; CanIShareThis/1.0; +https://canisharethis.com)',
          'accept': 'text/html,application/xhtml+xml',
          'accept-language': 'en-US,en;q=0.8'
        }
      });
      if (response.status >= 300 && response.status < 400) {
        const location = response.headers.get('location');
        if (!location) break;
        const next = new URL(location, current);
        if (!platformForHost(next.hostname)) return { state: 'blocked-redirect', title: '', displayName: '', description: '', statusCode: response.status, finalUrl: current.toString() };
        current = next;
        continue;
      }
      break;
    }
    if (!response) return { state: 'unavailable', title: '', displayName: '', description: '', statusCode: null, finalUrl: current.toString() };
    const type = String(response.headers.get('content-type') || '').toLowerCase();
    if (!response.ok || (type && !type.includes('text/html') && !type.includes('application/xhtml+xml'))) {
      return { state: response.status === 401 || response.status === 403 || response.status === 429 ? 'blocked' : 'unavailable', title: '', displayName: '', description: '', statusCode: response.status, finalUrl: current.toString() };
    }
    const html = (await response.text()).slice(0, 350000);
    const parsed = parseMetadata(html);
    const displayName = cleanDisplayName(parsed.title, profile.platform, profile.username);
    return {
      state: parsed.title || parsed.description ? 'read' : 'limited',
      title: parsed.title,
      displayName,
      description: parsed.description,
      statusCode: response.status,
      finalUrl: current.toString()
    };
  } catch (_) {
    return { state: 'unavailable', title: '', displayName: '', description: '', statusCode: null, finalUrl: current.toString() };
  } finally {
    clearTimeout(timer);
  }
}

function uniqueExternalLinks(text, profile) {
  const out = [];
  const seen = new Set();
  for (const raw of String(text || '').match(URL_RE) || []) {
    try {
      const url = new URL(raw);
      const host = url.hostname.toLowerCase().replace(/^www\./, '');
      if (profile && profile.url) {
        try { if (new URL(profile.url).hostname.toLowerCase().replace(/^www\./, '') === host) continue; } catch (_) {}
      }
      if (platformForHost(url.hostname)) continue;
      if (seen.has(host)) continue;
      seen.add(host);
      out.push({ host, shortener: SHORTENER_HOSTS.has(host) });
    } catch (_) {}
  }
  return out.slice(0, 6);
}

function severityFor(weight) {
  return weight >= 40 ? 'high' : weight >= 20 ? 'medium' : 'low';
}

function addSignal(signals, type, title, detail, weight) {
  if (!signals.some(s => s.type === type && s.detail === detail)) signals.push({ type, title, detail, weight, severity: severityFor(weight) });
}

function signalCount(signals, prefixes) {
  return signals.filter(s => prefixes.some(prefix => s.type === prefix || s.type.startsWith(prefix))).length;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_) { body = {}; }
  }
  const input = cleanText(body.input || body.url || body.handle, 4000);
  if (!input) return res.status(400).json({ error: 'Social profile URL or username required' });

  const profile = extractProfile(input);
  if (!profile) return res.status(400).json({ error: 'Use a supported social profile URL or an @username.' });

  const metadata = await fetchPublicMetadata(profile);
  const username = cleanText(profile.username, 120);
  const suppliedContext = cleanText(profile.suppliedContext, 1800);
  const publicText = cleanText([metadata.displayName, metadata.description, suppliedContext].filter(Boolean).join(' '), 2400);
  const signals = [];
  let score = 0;

  const usernameBrand = username ? brandEvidence(username) : null;
  const displayBrand = metadata.displayName ? brandEvidence(metadata.displayName) : null;
  const contextBrand = publicText ? brandEvidence(publicText) : null;
  const claimedBrand = (usernameBrand || displayBrand || contextBrand || {}).brand || null;
  const authorityInUsername = username && hasWord(username, AUTHORITY_WORDS);
  const moneyInUsername = username && hasWord(username, MONEY_WORDS);
  const authorityInContext = publicText && hasWord(publicText, AUTHORITY_WORDS);
  const moneyInContext = publicText && hasWord(publicText, MONEY_WORDS);
  const credentialRequest = publicText && containsPhrase(publicText, CREDENTIAL_PHRASES);
  const recoveryRequest = publicText && containsPhrase(publicText, RECOVERY_PHRASES);
  const urgency = publicText && containsPhrase(publicText, URGENCY_PHRASES);
  const payment = publicText && containsPhrase(publicText, PAYMENT_PHRASES);
  const offPlatformContact = publicText && containsPhrase(publicText, CONTACT_PHRASES);
  const fakeBadge = VERIFY_SYMBOL_RE.test(input) || VERIFY_SYMBOL_RE.test(publicText);
  const externalLinks = uniqueExternalLinks([metadata.description, suppliedContext].filter(Boolean).join(' '), profile);
  const shortLinks = externalLinks.filter(x => x.shortener);

  if (!username) {
    addSignal(signals, 'profile-not-specific', 'Profile could not be isolated', 'The supplied URL points to a supported platform, but a specific public username could not be isolated.', 18);
    score += 18;
  }

  if (usernameBrand) {
    if (usernameBrand.obfuscated) {
      addSignal(signals, 'brand-lookalike', 'Brand name appears obfuscated', `The username resembles ${usernameBrand.brand} after common look-alike character substitutions.`, 58);
      score += 58;
    } else if (authorityInUsername) {
      addSignal(signals, 'brand-support-claim', 'Brand-style support identity', `The username combines ${usernameBrand.brand} with support, security, verification or official-style wording.`, 32);
      score += 32;
    }
  }

  if (authorityInUsername && !usernameBrand) {
    addSignal(signals, 'authority-wording', 'Authority-style username', 'The username uses support, security, verification, recovery or official-style wording.', 16);
    score += 16;
  }

  if (moneyInUsername) {
    addSignal(signals, 'money-themed-identity', 'Money or giveaway wording', 'The username contains crypto, investment, giveaway, prize or wallet-related wording.', 22);
    score += 22;
  }

  if (displayBrand && username && !compact(username).includes(displayBrand.brand)) {
    addSignal(signals, 'display-name-brand-claim', 'Display name claims a brand', `The public display name references ${displayBrand.brand}, while the username uses a different identity. Verify the handle from the brand’s official website.`, 18);
    score += 18;
  }

  if ((contextBrand || displayBrand) && authorityInContext) {
    const brandName = (contextBrand || displayBrand).brand;
    addSignal(signals, 'public-brand-support-claim', 'Public profile claims official/support status', `The public profile text combines ${brandName} with support, official, security, verification or recovery wording.`, 24);
    score += 24;
  }

  if (credentialRequest) {
    addSignal(signals, 'credential-request', 'Credentials or verification codes requested', 'The supplied/public profile text appears to ask for passwords, login codes, OTPs or account verification details.', 48);
    score += 48;
  }

  if (recoveryRequest) {
    addSignal(signals, 'recovery-phrase-risk', 'Account or wallet recovery claim', 'The profile text mentions seed phrases, recovery phrases, wallet recovery or account-unlock services. These are common scam themes.', 52);
    score += 52;
  }

  if (payment || (moneyInContext && urgency)) {
    addSignal(signals, 'payment-investment-pitch', 'Payment or investment pitch', 'The profile text combines money, investment, payment or guaranteed-return language with pressure or solicitation.', 34);
    score += 34;
  } else if (moneyInContext) {
    addSignal(signals, 'money-themed-bio', 'Crypto or investment wording in profile', 'The public/supplied profile text contains crypto, investment, giveaway or prize-related wording.', 16);
    score += 16;
  }

  if (urgency && (authorityInContext || credentialRequest || payment)) {
    addSignal(signals, 'urgency-pressure', 'Urgency or account-pressure language', 'The profile text uses urgent, suspended, locked or limited-time language alongside another risk signal.', 24);
    score += 24;
  }

  if (offPlatformContact && (claimedBrand || authorityInContext || moneyInContext)) {
    addSignal(signals, 'off-platform-contact', 'Moves contact to another app', 'The profile asks people to continue on WhatsApp, Telegram or private messages while also making support, brand or money-related claims.', 22);
    score += 22;
  }

  if (shortLinks.length) {
    addSignal(signals, 'short-link-in-profile', 'Shortened external link', `The public/supplied profile text contains a shortened external link (${shortLinks[0].host}), which hides the final destination.`, 20);
    score += 20;
  }

  if (fakeBadge) {
    addSignal(signals, 'visual-verification-symbol', 'Verification-like symbol', 'A checkmark-style symbol appears in the supplied/public profile text. This is not proof of platform verification.', 18);
    score += 18;
  }

  if (usernameBrand && usernameBrand.obfuscated && (authorityInUsername || moneyInUsername || authorityInContext || moneyInContext)) score = Math.max(score, 78);
  if (credentialRequest && (claimedBrand || authorityInContext)) score = Math.max(score, 76);
  if (recoveryRequest) score = Math.max(score, 74);

  score = Math.min(100, score);
  const status = score >= 70 ? 'high' : score >= 30 ? 'caution' : 'low';
  const verdict = status === 'high' ? 'High impersonation / scam risk' : status === 'caution' ? 'Profile needs verification' : 'No obvious scam profile pattern';

  let summary;
  if (status === 'high') summary = claimedBrand
    ? `This profile contains strong impersonation or scam signals around ${claimedBrand}.`
    : 'This profile contains multiple strong impersonation or scam signals.';
  else if (status === 'caution') summary = claimedBrand
    ? `This profile makes ${claimedBrand}-related identity or contact claims that should be verified independently.`
    : 'This profile contains identity, contact or money-related signals that should be verified before you trust it.';
  else summary = metadata.state === 'read' || suppliedContext
    ? 'No obvious scam or impersonation pattern was found in the profile identifier and the public/supplied profile text that could be analyzed.'
    : 'No obvious impersonation pattern was found in the profile identifier. Public profile text could not be reliably read, so the account identity is not verified.';

  const recommendedAction = status === 'high'
    ? 'Do not reply, pay, send codes or documents. Find the real organization or person independently and compare the exact handle before interacting.'
    : status === 'caution'
      ? 'Verify the exact handle from an official website or another trusted channel before replying, paying or sharing sensitive information.'
      : 'If the contact was unexpected, still verify the account independently before sending money, passwords, codes or personal documents.';

  const metadataLabel = suppliedContext
    ? (metadata.state === 'read' ? 'Public metadata + supplied profile text' : 'Supplied profile text analyzed')
    : metadata.state === 'read' ? 'Public profile metadata read'
      : metadata.state === 'blocked' ? 'Platform blocked public metadata access'
        : metadata.state === 'limited' ? 'Public page read, profile metadata limited'
          : profile.url ? 'Public profile metadata unavailable' : 'Identifier only';

  return res.status(200).json({
    inputType: 'social-profile',
    socialProfile: {
      platform: profile.platform,
      username: username || null,
      profileUrl: profile.url,
      displayName: metadata.displayName || null,
      publicBio: metadata.description || null,
      claimedBrand,
      identityVerified: false,
      source: profile.source,
      profileData: {
        state: metadata.state,
        label: metadataLabel,
        publicMetadataRead: metadata.state === 'read',
        suppliedContextAnalyzed: Boolean(suppliedContext),
        externalLinkCount: externalLinks.length,
        externalDomains: externalLinks.map(x => x.host),
        shortLinkCount: shortLinks.length
      },
      categories: {
        impersonationSignals: signalCount(signals, ['brand-', 'display-name-', 'public-brand-', 'authority-', 'visual-verification']),
        credentialSignals: signalCount(signals, ['credential-', 'recovery-']),
        moneySignals: signalCount(signals, ['money-', 'payment-', 'short-link-']),
        contactSignals: signalCount(signals, ['off-platform-', 'urgency-'])
      }
    },
    safety: {
      status,
      riskScore: score,
      verdict,
      signals: signals.sort((a, b) => b.weight - a.weight).slice(0, 6).map(s => ({ title: s.title, detail: s.detail, type: s.type, severity: s.severity })),
      checksPerformed: [
        'Social platform and profile detection',
        'Username impersonation and look-alike analysis',
        'Public display-name and bio metadata when accessible',
        'Support / official / recovery wording',
        'Credential, payment, crypto and giveaway language',
        'Off-platform contact and shortened external links'
      ]
    },
    summary,
    recommendedAction,
    limitations: metadata.state === 'read' || suppliedContext
      ? 'This check analyzes identifiers and available public/supplied profile text. It does not prove who controls the account, verify followers, or access private profile data.'
      : 'The platform did not expose reliable public profile metadata to this scan. The result is based mainly on the profile identifier and does not prove who controls the account.'
  });
};
