function cleanText(value, max = 500) {
  return String(value || '').trim().slice(0, max);
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
  'dhl', 'fedex', 'ups', 'usps', 'chronopost', 'laposte'
];

const QUALIFIER_WORDS = ['support', 'help', 'security', 'secure', 'verify', 'verification', 'official', 'service', 'customer', 'recovery', 'admin'];
const MONEY_WORDS = ['crypto', 'bitcoin', 'btc', 'wallet', 'giveaway', 'airdrop', 'invest', 'investment', 'trading', 'giftcard', 'gift-card', 'prize'];
const VERIFY_SYMBOL_RE = /[✓✔☑✅☒☑︎]/u;

function platformForHost(hostname) {
  const host = String(hostname || '').toLowerCase();
  for (const item of PLATFORM_HOSTS) {
    if (item.hosts.includes(host)) return item.platform;
  }
  return null;
}

function extractProfile(input) {
  const value = cleanText(input, 1200);
  if (/^@[A-Za-z0-9._-]{2,64}$/.test(value)) {
    return { platform: 'Unknown social platform', username: value.slice(1), url: null, source: 'handle' };
  }

  let url;
  try { url = new URL(value); } catch (_) { return null; }
  const platform = platformForHost(url.hostname);
  if (!platform) return null;

  const parts = url.pathname.split('/').filter(Boolean).map(v => decodeURIComponent(v));
  let username = '';

  if (platform === 'TikTok') {
    const p = parts.find(v => v.startsWith('@'));
    username = p ? p.slice(1) : '';
  } else if (platform === 'Discord') {
    if (parts[0] === 'users' && parts[1]) username = parts[1];
  } else if (platform === 'Facebook') {
    if (url.pathname.toLowerCase().endsWith('/profile.php') || url.pathname.toLowerCase() === '/profile.php') username = url.searchParams.get('id') || '';
    else username = parts[0] || '';
  } else {
    username = parts[0] || '';
  }

  if (username && RESERVED[platform] && RESERVED[platform].has(username.toLowerCase())) username = '';
  if (platform === 'Telegram' && (username.startsWith('+') || username === 'joinchat')) username = '';

  return { platform, username, url: url.toString(), source: 'url' };
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

function brandEvidence(username) {
  const raw = cleanText(username, 120);
  const skel = skeleton(raw);
  const literal = compact(raw);
  for (const brand of BRANDS) {
    if (!skel.includes(brand)) continue;
    const obfuscated = !literal.includes(brand) && skel.includes(brand);
    return { brand, obfuscated, skeleton: skel };
  }
  return null;
}

function hasWord(username, words) {
  const low = String(username || '').toLowerCase().replace(/[._-]+/g, ' ');
  const compacted = low.replace(/\s+/g, '');
  return words.some(word => low.split(/\s+/).includes(word) || compacted.includes(word.replace(/[-\s]/g, '')));
}

function addSignal(signals, type, title, detail, weight) {
  if (!signals.some(s => s.type === type && s.detail === detail)) signals.push({ type, title, detail, weight });
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_) { body = {}; }
  }
  const input = cleanText(body.input || body.url || body.handle, 1200);
  if (!input) return res.status(400).json({ error: 'Social profile URL or username required' });

  const profile = extractProfile(input);
  if (!profile) return res.status(400).json({ error: 'Use a supported social profile URL or an @username.' });

  const username = cleanText(profile.username, 120);
  const signals = [];
  let score = 0;
  const brand = username ? brandEvidence(username) : null;
  const qualifier = username && hasWord(username, QUALIFIER_WORDS);
  const money = username && hasWord(username, MONEY_WORDS);
  const fakeBadge = VERIFY_SYMBOL_RE.test(input) || VERIFY_SYMBOL_RE.test(username);

  if (!username) {
    addSignal(signals, 'profile-not-specific', 'Profile could not be isolated', 'The URL points to a supported social platform, but not to a clearly identifiable public profile.', 22);
    score += 22;
  }

  if (brand) {
    if (brand.obfuscated) {
      addSignal(signals, 'brand-lookalike', 'Brand name appears obfuscated', `The username resembles ${brand.brand} after common look-alike character substitutions.`, 58);
      score += 58;
    } else if (qualifier) {
      addSignal(signals, 'brand-support-claim', 'Brand-style support identity', `The username combines ${brand.brand} with support, security, verification or official-style wording.`, 32);
      score += 32;
    }
  }

  if (qualifier && !brand) {
    addSignal(signals, 'authority-wording', 'Authority-style wording', 'The username uses support, security, verification or official-style wording.', 18);
    score += 18;
  }

  if (money) {
    addSignal(signals, 'money-themed-identity', 'Money or giveaway wording', 'The username contains crypto, investment, giveaway, prize or wallet-related wording.', 24);
    score += 24;
  }

  if (fakeBadge) {
    addSignal(signals, 'visual-verification-symbol', 'Verification-like symbol', 'A checkmark-style symbol appears in the supplied profile text. This is not proof of platform verification.', 28);
    score += 28;
  }

  if (brand && brand.obfuscated && (qualifier || money)) score = Math.max(score, 78);
  else if (brand && brand.obfuscated) score = Math.max(score, 68);

  score = Math.min(100, score);
  const status = score >= 70 ? 'high' : score >= 30 ? 'caution' : 'low';
  const verdict = status === 'high' ? 'High impersonation risk' : status === 'caution' ? 'Profile needs verification' : 'No obvious impersonation signs';

  let summary;
  if (status === 'high') summary = brand
    ? `This profile uses an identity that strongly resembles ${brand.brand}, with additional impersonation warning signs.`
    : 'This profile contains multiple impersonation warning signs.';
  else if (status === 'caution') summary = brand
    ? `This profile uses a ${brand.brand}-related identity that should be verified through an official source.`
    : 'This profile contains identity signals that should be verified before you trust it.';
  else summary = 'No obvious impersonation pattern was detected in the supplied profile identifier, but the account identity is not verified.';

  const recommendedAction = status === 'high'
    ? 'Do not reply, send money, codes or documents. Verify the account from the organization’s official website, then block and report it if the identity does not match.'
    : status === 'caution'
      ? 'Verify the account independently from the official website or another trusted channel before replying, paying or sharing sensitive information.'
      : 'If the contact was unexpected, verify the account independently before sharing money, codes, passwords or personal documents.';

  return res.status(200).json({
    inputType: 'social-profile',
    socialProfile: {
      platform: profile.platform,
      username: username || null,
      profileUrl: profile.url,
      claimedBrand: brand ? brand.brand : null,
      identityVerified: false,
      source: profile.source
    },
    safety: {
      status,
      riskScore: score,
      verdict,
      signals: signals.slice(0, 4).map(s => ({ title: s.title, detail: s.detail, type: s.type })),
      checksPerformed: [
        'Social platform and profile detection',
        'Username impersonation patterns',
        'Look-alike character analysis',
        'Authority and money-related wording'
      ]
    },
    summary,
    recommendedAction,
    limitations: 'This check does not prove who controls the account and does not scrape private profiles, followers or biometric data.'
  });
};
