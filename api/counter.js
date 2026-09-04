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
  const r = await fetch(cfg.url, {
    method: 'POST',
    headers: { authorization: `Bearer ${cfg.token}`, 'content-type': 'application/json' },
    body: JSON.stringify(command)
  });
  if (!r.ok) throw new Error(`Counter storage error ${r.status}`);
  const data = await r.json();
  return data.result;
}

async function snapshot() {
  const cfg = redisConfig();
  if (!cfg) return { total: memory.total, byType: memory.byType, persistent: false };
  const rows = await redis(['HGETALL', 'cist:scan-counts']);
  const obj = Object.create(null);
  if (Array.isArray(rows)) for (let i = 0; i < rows.length; i += 2) obj[rows[i]] = Number(rows[i + 1] || 0);
  const byType = {};
  for (const type of TYPES) byType[type] = Number(obj[`type:${type}`] || 0);
  return { total: Number(obj.total || 0), byType, persistent: true };
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  try {
    if (req.method === 'POST') {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const type = TYPES.has(String(body.type || '')) ? String(body.type) : 'other';
      if (redisConfig()) {
        await redis(['HINCRBY', 'cist:scan-counts', 'total', 1]);
        await redis(['HINCRBY', 'cist:scan-counts', `type:${type}`, 1]);
      } else {
        memory.total += 1;
        memory.byType[type] = (memory.byType[type] || 0) + 1;
      }
    } else if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' });
    }
    return res.status(200).json(await snapshot());
  } catch (e) {
    console.error('[cist-counter]', e && e.message ? e.message : e);
    return res.status(500).json({ error: 'Counter unavailable' });
  }
};
