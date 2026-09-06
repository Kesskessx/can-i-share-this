const TYPES = new Set(['link','qr','email','file','shortlink','crypto','message','social','other']);
const memory = { total: 0, byType: Object.create(null), daily: Object.create(null) };

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

function buildDaily(day, entries) {
  const byType = emptyByType();
  let total = 0;
  let warnings = 0;
  let durationTotal = 0;
  let durationSamples = 0;
  const prefix = `day:${day}:`;

  for (const [key, raw] of entries) {
    if (!String(key).startsWith(prefix)) continue;
    const tail = String(key).slice(prefix.length);
    const count = Number(raw || 0);
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
  if (!cfg) return null;
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
      throw new Error(`Supabase counter error ${response.status}${detail ? `: ${detail.slice(0, 180)}` : ''}`);
    }
    if (response.status === 204) return null;
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

async function supabaseRows() {
  const rows = await supabase('/rest/v1/scan_counters?select=scan_type,count');
  return Array.isArray(rows) ? rows : [];
}

function supabaseSnapshot(rows, day) {
  const byType = emptyByType();
  let total = 0;
  for (const row of rows) {
    if (row.scan_type === 'total') total = Number(row.count || 0);
    else if (TYPES.has(row.scan_type)) byType[row.scan_type] = Number(row.count || 0);
  }
  return {
    total,
    byType,
    persistent: true,
    daily: buildDaily(day, rows.map(row => [row.scan_type, row.count]))
  };
}

async function incrementSupabaseGlobal(type) {
  await supabase('/rest/v1/rpc/increment_scan_counter', {
    method: 'POST',
    body: JSON.stringify({ p_type: type })
  });
}

async function incrementSupabaseDailyKey(key) {
  await supabase('/rest/v1/rpc/increment_daily_scan_counter', {
    method: 'POST',
    body: JSON.stringify({ p_key: key })
  });
}

async function incrementSupabaseDaily({ day, type, metricsOnly, warning, durationMs }) {
  const keys = [];
  if (!metricsOnly) {
    keys.push(`day:${day}:total`);
    keys.push(`day:${day}:type:${type}`);
  }
  if (metricsOnly && warning) keys.push(`day:${day}:warnings`);
  const bucket = metricsOnly ? durationBucket(durationMs) : null;
  if (bucket) keys.push(`day:${day}:duration:${bucket}`);
  if (keys.length) await Promise.all(keys.map(incrementSupabaseDailyKey));
}

function redisConfig() {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
  return url && token ? { url: url.replace(/\/$/, ''), token } : null;
}

async function redis(command) {
  const cfg = redisConfig();
  if (!cfg) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 1500);
  try {
    const response = await fetch(cfg.url, {
      method: 'POST',
      headers: { authorization: `Bearer ${cfg.token}`, 'content-type': 'application/json' },
      body: JSON.stringify(command),
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`Counter storage error ${response.status}`);
    const data = await response.json();
    return data.result;
  } finally {
    clearTimeout(timer);
  }
}

async function redisEntries() {
  const rows = await redis(['HGETALL', 'cist:scan-counts']);
  const entries = [];
  if (Array.isArray(rows)) {
    for (let i = 0; i < rows.length; i += 2) entries.push([rows[i], Number(rows[i + 1] || 0)]);
  }
  return entries;
}

function redisSnapshot(entries, day) {
  const obj = Object.create(null);
  for (const [key, value] of entries) obj[key] = Number(value || 0);
  const byType = emptyByType();
  for (const type of TYPES) byType[type] = Number(obj[`type:${type}`] || 0);
  return {
    total: Number(obj.total || 0),
    byType,
    persistent: true,
    daily: buildDaily(day, entries)
  };
}

async function incrementRedis({ day, type, metricsOnly, warning, durationMs }) {
  if (!metricsOnly) {
    await redis(['HINCRBY', 'cist:scan-counts', 'total', 1]);
    await redis(['HINCRBY', 'cist:scan-counts', `type:${type}`, 1]);
    await redis(['HINCRBY', 'cist:scan-counts', `day:${day}:total`, 1]);
    await redis(['HINCRBY', 'cist:scan-counts', `day:${day}:type:${type}`, 1]);
  }
  if (metricsOnly && warning) await redis(['HINCRBY', 'cist:scan-counts', `day:${day}:warnings`, 1]);
  const bucket = metricsOnly ? durationBucket(durationMs) : null;
  if (bucket) await redis(['HINCRBY', 'cist:scan-counts', `day:${day}:duration:${bucket}`, 1]);
}

function memoryDay(day) {
  if (!memory.daily[day]) {
    memory.daily[day] = { total: 0, warnings: 0, byType: emptyByType(), durations: Object.create(null) };
  }
  return memory.daily[day];
}

function incrementMemory({ day, type, metricsOnly, warning, durationMs }) {
  const daily = memoryDay(day);
  if (!metricsOnly) {
    memory.total += 1;
    memory.byType[type] = (memory.byType[type] || 0) + 1;
    daily.total += 1;
    daily.byType[type] = (daily.byType[type] || 0) + 1;
  }
  if (metricsOnly && warning) daily.warnings += 1;
  const bucket = metricsOnly ? durationBucket(durationMs) : null;
  if (bucket) daily.durations[bucket] = (daily.durations[bucket] || 0) + 1;
}

function memorySnapshot(day) {
  const daily = memoryDay(day);
  const entries = [
    [`day:${day}:total`, daily.total],
    [`day:${day}:warnings`, daily.warnings],
    ...Object.entries(daily.byType).map(([type, count]) => [`day:${day}:type:${type}`, count]),
    ...Object.entries(daily.durations).map(([bucket, count]) => [`day:${day}:duration:${bucket}`, count])
  ];
  return { total: memory.total, byType: memory.byType, persistent: false, daily: buildDaily(day, entries) };
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'GET' && req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const day = parisDayKey();
  let type = 'other';
  let metricsOnly = false;
  let warning = false;
  let durationMs = null;

  if (req.method === 'POST') {
    try {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      type = normalizeType(body.type);
      metricsOnly = body.metricsOnly === true;
      warning = body.warning === true;
      durationMs = Number(body.durationMs);
    } catch (_) {}
  }

  if (supabaseConfig()) {
    try {
      if (req.method === 'POST' && !metricsOnly) await incrementSupabaseGlobal(type);
      if (req.method === 'POST') await incrementSupabaseDaily({ day, type, metricsOnly, warning, durationMs });
      return res.status(200).json(supabaseSnapshot(await supabaseRows(), day));
    } catch (error) {
      console.error('[cist-counter-supabase-fallback]', error && error.message ? error.message : error);
    }
  }

  if (redisConfig()) {
    try {
      if (req.method === 'POST') await incrementRedis({ day, type, metricsOnly, warning, durationMs });
      return res.status(200).json(redisSnapshot(await redisEntries(), day));
    } catch (error) {
      console.error('[cist-counter-redis-fallback]', error && error.message ? error.message : error);
    }
  }

  if (req.method === 'POST') incrementMemory({ day, type, metricsOnly, warning, durationMs });
  return res.status(200).json(memorySnapshot(day));
};
