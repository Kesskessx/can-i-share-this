'use strict';

const React = require('react');
const { getSharedResult, normalizeId } = require('../lib/shared-results');

function text(value, max = 180) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, max);
}

function label(verdict) {
  if (verdict === 'high') return 'HIGH RISK';
  if (verdict === 'caution') return 'VERIFY FIRST';
  if (verdict === 'low') return 'NO MAJOR WARNING';
  return 'INCOMPLETE';
}

function palette(verdict) {
  if (verdict === 'high') return { accent: '#ff7770', soft: '#351d22' };
  if (verdict === 'caution') return { accent: '#f0b85b', soft: '#332819' };
  if (verdict === 'low') return { accent: '#61c99a', soft: '#173028' };
  return { accent: '#93a0b8', soft: '#202633' };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'HEAD') return res.status(405).end('Method not allowed');
  const id = normalizeId(req.query && req.query.id);
  if (!id) return res.status(404).end('Not found');

  try {
    const row = await getSharedResult(id);
    if (!row) return res.status(404).end('Not found');
    const payload = row.payload || {};
    const verdict = payload.verdict || 'unknown';
    const colors = palette(verdict);
    const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
    const { ImageResponse } = await import('@vercel/og');
    const e = React.createElement;

    const reasonNodes = reasons.map((reason, index) =>
      e('div', {
        key: `r${index}`,
        style: {
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          padding: '12px 16px',
          border: '1px solid #2b3342',
          borderRadius: 16,
          background: '#121722'
        }
      },
        e('div', {
          style: {
            width: 12,
            height: 12,
            borderRadius: 999,
            background: colors.accent,
            flex: '0 0 auto'
          }
        }),
        e('div', {
          style: {
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0
          }
        },
          e('div', { style: { color: '#f4f7fb', fontSize: 24, fontWeight: 800 } }, text(reason && reason.title, 70) || 'Signal'),
          e('div', { style: { color: '#9ca7b8', fontSize: 17, marginTop: 3 } }, text(reason && reason.detail, 120))
        )
      )
    );

    const image = new ImageResponse(
      e('div', {
        style: {
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          padding: 58,
          background: 'radial-gradient(circle at 76% 16%, rgba(120,143,247,.22), transparent 34%), #0b0e14',
          color: '#f4f7fb',
          fontFamily: 'sans-serif'
        }
      },
        e('div', {
          style: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }
        },
          e('div', { style: { display: 'flex', fontSize: 30, fontWeight: 900, letterSpacing: '-0.04em' } },
            'Can I Share ',
            e('span', { style: { color: '#7f93ff', marginLeft: 5 } }, 'This?')
          ),
          e('div', {
            style: {
              fontSize: 18,
              color: '#9ca7b8',
              border: '1px solid #2b3342',
              borderRadius: 999,
              padding: '8px 14px'
            }
          }, 'Shared safety scan')
        ),
        e('div', {
          style: {
            marginTop: 48,
            display: 'flex',
            flexDirection: 'column'
          }
        },
          e('div', {
            style: {
              display: 'flex',
              alignSelf: 'flex-start',
              color: colors.accent,
              background: colors.soft,
              border: `1px solid ${colors.accent}`,
              borderRadius: 999,
              padding: '8px 14px',
              fontSize: 20,
              fontWeight: 900,
              letterSpacing: '0.06em'
            }
          }, label(verdict)),
          e('div', {
            style: {
              marginTop: 18,
              fontSize: 54,
              lineHeight: 1.04,
              letterSpacing: '-0.045em',
              fontWeight: 900,
              maxWidth: 1010
            }
          }, text(payload.headline, 170) || 'Can I Share This? scan result')
        ),
        e('div', {
          style: {
            marginTop: 30,
            display: 'flex',
            flexDirection: 'column',
            gap: 10
          }
        }, ...(reasonNodes.length ? reasonNodes : [
          e('div', {
            key: 'none',
            style: {
              padding: '14px 16px',
              border: '1px solid #2b3342',
              borderRadius: 16,
              background: '#121722',
              color: '#9ca7b8',
              fontSize: 20
            }
          }, 'Run a fresh scan before relying on this shared result.')
        ])),
        e('div', {
          style: {
            marginTop: 'auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            color: '#9ca7b8',
            fontSize: 18
          }
        },
          e('div', null, `Confidence: ${text(payload.confidence, 20) || 'unknown'}`),
          e('div', { style: { color: '#d9deea', fontWeight: 800 } }, 'canisharethis.com')
        )
      ),
      { width: 1200, height: 630 }
    );

    res.statusCode = 200;
    image.headers.forEach((value, key) => res.setHeader(key, value));
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    if (req.method === 'HEAD') return res.end();
    const buffer = Buffer.from(await image.arrayBuffer());
    return res.end(buffer);
  } catch (error) {
    console.error('[cist-result-og]', error && error.message ? error.message : error);
    return res.status(503).end('Image unavailable');
  }
};
