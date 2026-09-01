const SENSITIVE_QUERY_KEYS = new Set([
  'access_token','id_token','refresh_token','auth_token','authorization','bearer',
  'signature','sig','x-amz-signature','x-goog-signature','x-goog-credential',
  'api_key','apikey','client_secret','secret','password','passwd','session','sessionid'
]);

function parsePublicUrl(input) {
  const url = new URL(String(input || '').trim());
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Only HTTP and HTTPS links are supported.');
  if (url.username || url.password) throw new Error('Credential-bearing URLs cannot be deep-scanned.');
  return url;
}

function sensitiveParameters(url) {
  const found = [];
  for (const [key] of url.searchParams.entries()) {
    const normalized = key.toLowerCase();
    if (SENSITIVE_QUERY_KEYS.has(normalized) || normalized.includes('token') || normalized.includes('secret')) {
      found.push(key);
    }
  }
  return [...new Set(found)].slice(0, 8);
}

function truthy(value) {
  return value === true || value === 'true' || value === 'yes' || value === 'y' || value === 1 || value === '1';
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 6500) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function checkPhishTank(url) {
  const body = new URLSearchParams({ url: url.toString(), format: 'json' });
  if (process.env.PHISHTANK_APP_KEY) body.set('app_key', process.env.PHISHTANK_APP_KEY);
  try {
    const response = await fetchWithTimeout('https://checkurl.phishtank.com/checkurl/', {
      method: 'POST',
      headers: {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'CanIShareThis/6.1 (+https://canisharethis.com)'
      },
      body
    });
    if (!response.ok) {
      return { provider: 'PhishTank', checked: false, status: 'unavailable', detail: `Provider returned HTTP ${response.status}.` };
    }
    const data = await response.json();
    const result = data?.results || data?.result || {};
    const inDatabase = truthy(result.in_database);
    const verified = truthy(result.verified);
    const valid = truthy(result.valid);
    const dangerous = inDatabase && verified && valid;
    return {
      provider: 'PhishTank',
      checked: true,
      status: dangerous ? 'known-phishing' : 'no-known-phish',
      dangerous,
      detail: dangerous
        ? 'This URL is listed as a verified phishing page in PhishTank.'
        : inDatabase
          ? 'The URL exists in PhishTank, but it is not currently confirmed as a valid verified phish.'
          : 'No matching phishing record was found in PhishTank.',
      referenceId: result.phish_id || undefined
    };
  } catch (error) {
    return { provider: 'PhishTank', checked: false, status: 'unavailable', detail: 'PhishTank could not be reached for this scan.' };
  }
}

async function checkGoogleSafeBrowsing(url) {
  const key = process.env.GOOGLE_SAFE_BROWSING_API_KEY;
  if (!key) {
    return { provider: 'Google Safe Browsing', checked: false, status: 'not-configured', detail: 'Google Safe Browsing is ready but no server API key is configured yet.' };
  }
  try {
    const response = await fetchWithTimeout(`https://safebrowsing.googleapis.com/v4/threatMatches:find?key=${encodeURIComponent(key)}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        client: { clientId: 'can-i-share-this', clientVersion: '6.1' },
        threatInfo: {
          threatTypes: ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
          platformTypes: ['ANY_PLATFORM'],
          threatEntryTypes: ['URL'],
          threatEntries: [{ url: url.toString() }]
        }
      })
    });
    if (!response.ok) {
      return { provider: 'Google Safe Browsing', checked: false, status: 'unavailable', detail: `Provider returned HTTP ${response.status}.` };
    }
    const data = await response.json();
    const matches = Array.isArray(data?.matches) ? data.matches : [];
    const dangerous = matches.length > 0;
    return {
      provider: 'Google Safe Browsing',
      checked: true,
      status: dangerous ? 'known-threat' : 'no-known-threat',
      dangerous,
      detail: dangerous ? 'Google Safe Browsing reports this URL as matching a known threat list.' : 'No matching threat was returned by Google Safe Browsing.',
      threatTypes: [...new Set(matches.map(item => item?.threatType).filter(Boolean))]
    };
  } catch (error) {
    return { provider: 'Google Safe Browsing', checked: false, status: 'unavailable', detail: 'Google Safe Browsing could not be reached for this scan.' };
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    if (body.consent !== true) {
      return res.status(400).json({ error: 'Deep Scan requires explicit consent before the URL is shared with external threat-intelligence providers.' });
    }
    const url = parsePublicUrl(body.url);
    const sensitive = sensitiveParameters(url);
    if (sensitive.length) {
      return res.status(200).json({
        deepScan: true,
        privacyBlocked: true,
        status: 'privacy-blocked',
        verdict: 'Deep Scan was not sent to external providers',
        sensitiveParameters: sensitive,
        providers: [],
        disclaimer: 'This URL appears to contain a token, signature, session identifier, or other sensitive query parameter. Use Quick Check instead.'
      });
    }

    const providers = await Promise.all([checkPhishTank(url), checkGoogleSafeBrowsing(url)]);
    const dangerousProviders = providers.filter(item => item.dangerous);
    const checkedProviders = providers.filter(item => item.checked);
    let status = 'unknown';
    let verdict = 'External reputation is currently unavailable';
    if (dangerousProviders.length) {
      status = 'known-dangerous';
      verdict = 'Known threat reported by an external reputation source';
    } else if (checkedProviders.length) {
      status = 'no-known-threat';
      verdict = 'No known threat found by the available reputation sources';
    }

    return res.status(200).json({
      deepScan: true,
      privacyBlocked: false,
      status,
      verdict,
      checkedUrlHost: url.hostname,
      providers,
      disclaimer: 'No reputation service can guarantee that a URL is safe. New or targeted threats may not be listed yet.'
    });
  } catch (error) {
    const message = error?.name === 'AbortError' ? 'External reputation lookup timed out.' : (error?.message || 'Deep Scan failed.');
    return res.status(200).json({ deepScan: true, status: 'unknown', verdict: 'Deep Scan could not complete', providers: [], error: message });
  }
};
