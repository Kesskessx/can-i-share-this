const TYPES = new Set(['link','qr','email','file','shortlink','crypto','message','social','other']);

function parisDayKey() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date());
  const get = type => parts.find(p => p.type === type)?.value || '';
  return `${get('year')}-${get('month')}-${get('day')}`;
}

function normalizeType(value) {
  const raw = String(value || '').toLowerCase();
  if (raw === 'url') return 'link';
  if (raw === 'social-profile') return 'social';
  return TYPES.has(raw) ? raw : 'other';
}

function durationBucket(value) {
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0) return null;
  return Math.max(250, Math.min(15000, Math.round(n / 250) * 250));
}

function emptyByType() {
  const out = {};
  for (const type of TYPES) out[type] = 0;
  return out;
}

function buildDaily(day, rows) {
  const byType = emptyByType();
  let total = 0;
  let warnings = 0;
  let durationTotal = 0;
  let durationSamples = 0;
  const prefix = `day:${day}:`;

  for (const row of Array.isArray(rows) ? rows : []) {
    const key = String(row.scan_type || '');
    if (!key.startsWith(prefix)) continue;
    const tail = key.slice(prefix.length);
    const count = Number(row.count || 0);
    if (!Number.isFinite(count) || count < 0) continue;
    if (tail === 'total') total = count;
    else if (tail === 'warnings') warnings = count;
    else if (tail.startsWith('type:')) {
      const type = tail.slice(5);
      if (TYPES.has(type)) byType[type] = count;
    } else if (tail.startsWith('duration:')) {
      const bucket = Number(tail.slice(9));
      if (Number.isFinite(bucket) && bucket > 0) {
        durationTotal += bucket * count;
        durationSamples += count;
      }
    }
  }

  return {
    day,
    total,
    warnings,
    byType,
    averageMs: durationSamples ? Math.round(durationTotal / durationSamples) : null,
    durationSamples
  };
}

function supabaseConfig() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;
  return url && key ? { url: url.replace(/\/$/, ''), key } : null;
}

async function supabase(path, options = {}) {
  const cfg = supabaseConfig();
  if (!cfg) throw new Error('Persistent counter storage is not configured.');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 1800);
  try {
    const headers = {
      apikey: cfg.key,
      'content-type': 'application/json',
      ...(options.headers || {})
    };
    if (!cfg.key.startsWith('sb_secret_')) headers.authorization = `Bearer ${cfg.key}`;
    const response = await fetch(`${cfg.url}${path}`, { ...options, headers, signal: controller.signal });
    if (!response.ok) {
      let detail = '';
      try { detail = await response.text(); } catch (_) {}
      throw new Error(`Supabase daily counter error ${response.status}${detail ? `: ${detail.slice(0, 160)}` : ''}`);
    }
    if (response.status === 204) return null;
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

async function incrementKey(key) {
  await supabase('/rest/v1/rpc/increment_daily_scan_counter', {
    method: 'POST',
    body: JSON.stringify({ p_key: key })
  });
}

async function snapshot(day) {
  const rows = await supabase('/rest/v1/scan_counters?select=scan_type,count');
  return buildDaily(day, rows);
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'GET' && req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const day = parisDayKey();
  try {
    if (req.method === 'POST') {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const type = normalizeType(body.type);
      const warning = body.warning === true;
      const bucket = durationBucket(body.durationMs);
      const keys = [`day:${day}:total`, `day:${day}:type:${type}`];
      if (warning) keys.push(`day:${day}:warnings`);
      if (bucket) keys.push(`day:${day}:duration:${bucket}`);
      await Promise.all(keys.map(incrementKey));
    }
    return res.status(200).json({ persistent: true, daily: await snapshot(day) });
  } catch (error) {
    console.error('[cist-daily-counter]', error && error.message ? error.message : error);
    return res.status(503).json({ persistent: false, error: 'Daily statistics are temporarily unavailable.' });
  }
};
