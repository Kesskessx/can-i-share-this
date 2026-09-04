const TYPES = new Set(['link','qr','email','file','shortlink','crypto','message','other']);
const memory = { total: 0, byType: Object.create(null) };

function supabaseConfig() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;
  return url && key ? { url: url.replace(/\/$/, ''), key } : null;
}

async function supabase(path, options = {}) {
  const cfg = supabaseConfig();
  if (!cfg) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 1500);
  try {
    const headers = {
      apikey: cfg.key,
      'content-type': 'application/json',
      ...(options.headers || {})
    };
    if (!cfg.key.startsWith('sb_secret_')) headers.authorization = `Bearer ${cfg.key}`;
    const r = await fetch(`${cfg.url}${path}`, {
      ...options,
      headers,
      signal: controller.signal
    });
    if (!r.ok) {
      let detail = '';
      try { detail = await r.text(); } catch (_) {}
      throw new Error(`Supabase counter error ${r.status}${detail ? `: ${detail.slice(0, 180)}` : ''}`);
    }
    if (r.status === 204) return null;
    return r.json();
  } finally {
    clearTimeout(timer);
  }
}

async function supabaseSnapshot() {
  const rows = await supabase('/rest/v1/scan_counters?select=scan_type,count');
  const byType = {};
  for (const type of TYPES) byType[type] = 0;
  let total = 0;
  if (Array.isArray(rows)) {
    for (const row of rows) {
      if (row.scan_type === 'total') total = Number(row.count || 0);
      else if (TYPES.has(row.scan_type)) byType[row.scan_type] = Number(row.count || 0);
    }
  }
  return { total, byType, persistent: true };
}

async function incrementSupabase(type) {
  await supabase('/rest/v1/rpc/increment_scan_counter', {
    method: 'POST',
    body: JSON.stringify({ p_type: type })
  });
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
  const timer = setTimeout(() => controller.abort(), 1200);
  try {
    const r = await fetch(cfg.url, {
      method: 'POST',
      headers: { authorization: `Bearer ${cfg.token}`, 'content-type': 'application/json' },
      body: JSON.stringify(command),
      signal: controller.signal
    });
    if (!r.ok) throw new Error(`Counter storage error ${r.status}`);
    const data = await r.json();
    return data.result;
  } finally {
    clearTimeout(timer);
  }
}

function memorySnapshot() {
  return { total: memory.total, byType: memory.byType, persistent: false };
}

async function redisSnapshot() {
  const rows = await redis(['HGETALL', 'cist:scan-counts']);
  const obj = Object.create(null);
  if (Array.isArray(rows)) for (let i = 0; i < rows.length; i += 2) obj[rows[i]] = Number(rows[i + 1] || 0);
  const byType = {};
  for (const type of TYPES) byType[type] = Number(obj[`type:${type}`] || 0);
  return { total: Number(obj.total || 0), byType, persistent: true };
}

function incrementMemory(type) {
  memory.total += 1;
  memory.byType[type] = (memory.byType[type] || 0) + 1;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'GET' && req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let type = 'other';
  if (req.method === 'POST') {
    try {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      type = TYPES.has(String(body.type || '')) ? String(body.type) : 'other';
    } catch (_) {}
  }

  if (supabaseConfig()) {
    try {
      if (req.method === 'POST') await incrementSupabase(type);
      return res.status(200).json(await supabaseSnapshot());
    } catch (e) {
      console.error('[cist-counter-supabase-fallback]', e && e.message ? e.message : e);
    }
  }

  if (redisConfig()) {
    try {
      if (req.method === 'POST') {
        await redis(['HINCRBY', 'cist:scan-counts', 'total', 1]);
        await redis(['HINCRBY', 'cist:scan-counts', `type:${type}`, 1]);
      }
      return res.status(200).json(await redisSnapshot());
    } catch (e) {
      console.error('[cist-counter-redis-fallback]', e && e.message ? e.message : e);
    }
  }

  if (req.method === 'POST') incrementMemory(type);
  return res.status(200).json(memorySnapshot());
};
