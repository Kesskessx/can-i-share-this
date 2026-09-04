const TYPES = new Set(['link','qr','email','file','shortlink','crypto','message','other']);
const memory = { total: 0, byType: Object.create(null) };

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

async function persistentSnapshot() {
  const rows = await redis(['HGETALL', 'cist:scan-counts']);
  const obj = Object.create(null);
  if (Array.isArray(rows)) for (let i = 0; i < rows.length; i += 2) obj[rows[i]] = Number(rows[i + 1] || 0);
  const byType = {};
  for (const type of TYPES) byType[type] = Number(obj[`type:${type}`] || 0);
  return { total: Number(obj.total || 0), byType, persistent: true };
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

  if (!redisConfig()) {
    if (req.method === 'POST') {
      memory.total += 1;
      memory.byType[type] = (memory.byType[type] || 0) + 1;
    }
    return res.status(200).json(memorySnapshot());
  }

  try {
    if (req.method === 'POST') {
      await redis(['HINCRBY', 'cist:scan-counts', 'total', 1]);
      await redis(['HINCRBY', 'cist:scan-counts', `type:${type}`, 1]);
    }
    return res.status(200).json(await persistentSnapshot());
  } catch (e) {
    console.error('[cist-counter-fallback]', e && e.message ? e.message : e);
    if (req.method === 'POST') {
      memory.total += 1;
      memory.byType[type] = (memory.byType[type] || 0) + 1;
    }
    return res.status(200).json(memorySnapshot());
  }
};
