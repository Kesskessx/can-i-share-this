const SENSITIVE_QUERY_KEYS = new Set([
  'access_token','id_token','refresh_token','auth_token','authorization','bearer',
  'signature','sig','x-amz-signature','x-goog-signature','x-goog-credential',
  'api_key','apikey','client_secret','secret','password','passwd','session','sessionid'
]);

const WEB_RISK_KEY_RE = /^AIza[0-9A-Za-z_-]{35}$/;
const WEB_RISK_EXTENDED = 'SOCIAL_ENGINEERING_EXTENDED_COVERAGE';
const WEB_RISK_THREAT_TYPES = [
  'MALWARE',
  'SOCIAL_ENGINEERING',
  'UNWANTED_SOFTWARE',
  WEB_RISK_EXTENDED
];

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
    if (SENSITIVE_QUERY_KEYS.has(normalized) || normalized.includes('token') || normalized.includes('secret')) found.push(key);
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

function webRiskFailure(status) {
  if (status === 400) return 'Google Web Risk rejected the request. Check the API configuration and enabled threat types.';
  if (status === 401 || status === 403) return 'Google Web Risk rejected the server credentials or API access. Check the Vercel key and Google Cloud API restrictions.';
  if (status === 429) return 'Google Web Risk rate limit was reached. Try again shortly.';
  return `Google Web Risk returned HTTP ${status}.`;
}

async function checkWebRisk(url) {
  const key = String(process.env.GOOGLE_WEB_RISK_API_KEY || '').trim();
  if (!key) {
    return { provider: 'Google Web Risk', checked: false, status: 'not-configured', detail: 'Google Web Risk is ready but no server API key is configured yet.' };
  }
  if (!WEB_RISK_KEY_RE.test(key)) {
    return { provider: 'Google Web Risk', checked: false, status: 'misconfigured', detail: 'The Google Web Risk server key has an unexpected format. Check GOOGLE_WEB_RISK_API_KEY in Vercel.' };
  }

  try {
    const params = new URLSearchParams();
    for (const threatType of WEB_RISK_THREAT_TYPES) params.append('threatTypes', threatType);
    params.set('uri', url.toString());
    params.set('key', key);

    const response = await fetchWithTimeout(`https://webrisk.googleapis.com/v1/uris:search?${params.toString()}`, {
      method: 'GET',
      headers: { 'user-agent': 'CanIShareThis/7.5 (+https://canisharethis.com)' }
    });

    if (!response.ok) {
      return { provider: 'Google Web Risk', checked: false, status: 'unavailable', httpStatus: response.status, detail: webRiskFailure(response.status) };
    }

    const data = await response.json();
    const types = Array.isArray(data?.threat?.threatTypes) ? data.threat.threatTypes : [];
    const standardTypes = types.filter(type => type !== WEB_RISK_EXTENDED);
    const extendedCoverage = types.includes(WEB_RISK_EXTENDED);
    const dangerous = standardTypes.length > 0;
    const caution = !dangerous && extendedCoverage;

    let status = 'no-known-threat';
    let detail = 'No matching threat was returned by Google Web Risk.';
    if (dangerous) {
      status = 'known-threat';
      detail = `Google Web Risk reports: ${types.join(', ')}.`;
    } else if (caution) {
      status = 'extended-coverage-match';
      detail = 'Google Web Risk Extended Coverage returned a potential social-engineering match. Treat this as a caution signal because this list intentionally favors broader phishing coverage.';
    }

    return {
      provider: 'Google Web Risk',
      checked: true,
      dangerous,
      caution,
      status,
      threatTypes: types,
      expiresAt: data?.threat?.expireTime || undefined,
      detail
    };
  } catch (error) {
    const detail = error?.name === 'AbortError'
      ? 'Google Web Risk timed out for this scan.'
      : 'Google Web Risk could not be reached for this scan.';
    return { provider: 'Google Web Risk', checked: false, status: 'unavailable', detail };
  }
}

async function checkPhishTank(url) {
  const appKey = process.env.PHISHTANK_APP_KEY;
  if (!appKey) return { provider: 'PhishTank', checked: false, status: 'not-configured', detail: 'PhishTank is available when an application key is configured.' };

  const body = new URLSearchParams({ url: url.toString(), format: 'json', app_key: appKey });
  try {
    const response = await fetchWithTimeout('https://checkurl.phishtank.com/checkurl/', {
      method: 'POST',
      headers: {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'CanIShareThis/7.5 (+https://canisharethis.com)'
      },
      body
    });
    if (!response.ok) return { provider: 'PhishTank', checked: false, status: 'unavailable', detail: `Provider returned HTTP ${response.status}.` };
    const data = await response.json();
    const result = data?.results || data?.result || {};
    const inDatabase = truthy(result.in_database);
    const verified = truthy(result.verified);
    const valid = truthy(result.valid);
    const dangerous = inDatabase && verified && valid;
    return {
      provider: 'PhishTank',
      checked: true,
      dangerous,
      status: dangerous ? 'known-phishing' : 'no-known-phish',
      detail: dangerous ? 'This URL is listed as a verified phishing page in PhishTank.' : 'No verified phishing match was returned by PhishTank.',
      referenceId: result.phish_id || undefined
    };
  } catch {
    return { provider: 'PhishTank', checked: false, status: 'unavailable', detail: 'PhishTank could not be reached for this scan.' };
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
        verdict: 'External reputation check was blocked for privacy',
        sensitiveParameters: sensitive,
        providers: [],
        disclaimer: 'This URL appears to contain a token, signature, session identifier, or other sensitive query parameter. The URL was not sent to external providers.'
      });
    }

    const providers = await Promise.all([checkWebRisk(url), checkPhishTank(url)]);
    const dangerousProviders = providers.filter(item => item.dangerous);
    const cautionProviders = providers.filter(item => item.caution);
    const checkedProviders = providers.filter(item => item.checked);
    let status = 'unknown';
    let verdict = 'External reputation is currently unavailable';

    if (dangerousProviders.length) {
      status = 'known-dangerous';
      verdict = 'Known threat reported by an external reputation source';
    } else if (cautionProviders.length) {
      status = 'caution';
      verdict = 'Potential phishing signal reported by an extended-coverage reputation source';
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
