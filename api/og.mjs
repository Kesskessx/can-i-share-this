import React from 'react';
import { ImageResponse } from '@vercel/og';
import sharedResults from '../lib/shared-results.js';

const { getSharedResult } = sharedResults;
const h = React.createElement;

function cap(value) {
  const v = String(value || '').trim();
  return v ? v.charAt(0).toUpperCase() + v.slice(1) : '';
}

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).send('Method not allowed');
  const id = String((req.query && req.query.id) || '').trim();
  let shared;
  try {
    shared = await getSharedResult(id);
  } catch (error) {
    console.error('[cist-og]', error && error.message ? error.message : error);
    return res.status(503).send('Image unavailable');
  }
  if (!shared) return res.status(404).send('Not found');

  const p = shared.payload;
  const reasons = Array.isArray(p.reasons) ? p.reasons.slice(0, 3) : [];
  const palette = p.verdict === 'high'
    ? { accent: '#d92d20', soft: '#fff1f0' }
    : p.verdict === 'caution'
      ? { accent: '#dc6803', soft: '#fff6ed' }
      : p.verdict === 'low'
        ? { accent: '#079455', soft: '#ecfdf3' }
        : { accent: '#667085', soft: '#f2f4f7' };

  const reasonNodes = reasons.length ? reasons.map((reason, index) => h('div', {
    key: `r-${index}`,
    style: { display: 'flex', alignItems: 'center', gap: 14, fontSize: 25, fontWeight: 700, color: '#344054' }
  },
  h('div', { style: { width: 10, height: 10, borderRadius: 999, background: palette.accent, display: 'flex', flexShrink: 0 } }),
  h('div', { style: { display: 'flex' } }, String(reason.title || 'Signal').slice(0, 90))
  )) : [h('div', { key: 'none', style: { display: 'flex', fontSize: 25, color: '#667085' } }, 'Run a fresh scan to verify the current result.')];

  const element = h('div', {
    style: {
      width: '100%', height: '100%', display: 'flex', flexDirection: 'column',
      background: '#f8f9fc', color: '#101828', padding: '58px 66px', fontFamily: 'Noto Sans'
    }
  },
  h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
    h('div', { style: { display: 'flex', fontSize: 29, fontWeight: 900, letterSpacing: '-1px' } }, 'Can I Share This?'),
    h('div', { style: { display: 'flex', fontSize: 20, color: '#667085' } }, 'Privacy-filtered scan result')
  ),
  h('div', { style: { display: 'flex', flexDirection: 'column', marginTop: 46 } },
    h('div', {
      style: {
        display: 'flex', alignSelf: 'flex-start', padding: '10px 17px', borderRadius: 999,
        background: palette.soft, color: palette.accent, border: `2px solid ${palette.accent}`,
        fontSize: 22, fontWeight: 900, textTransform: 'uppercase'
      }
    }, `${cap(p.verdict)} risk · ${cap(p.confidence)} confidence`),
    h('div', {
      style: { display: 'flex', marginTop: 24, maxWidth: 1030, fontSize: 52, lineHeight: 1.08, fontWeight: 900, letterSpacing: '-2px' }
    }, String(p.headline || 'Shared scan result').slice(0, 180))
  ),
  h('div', { style: { display: 'flex', flexDirection: 'column', gap: 14, marginTop: 34 } }, ...reasonNodes),
  h('div', { style: { display: 'flex', marginTop: 'auto', justifyContent: 'space-between', alignItems: 'flex-end' } },
    h('div', { style: { display: 'flex', fontSize: 21, color: '#667085' } }, 'Open the result and run your own scan.'),
    h('div', { style: { display: 'flex', fontSize: 24, fontWeight: 900 } }, `canisharethis.com/r/${shared.id}`)
  ));

  const image = new ImageResponse(element, { width: 1200, height: 630 });
  const bytes = Buffer.from(await image.arrayBuffer());
  res.setHeader('Content-Type', 'image/png');
  res.setHeader('Cache-Control', 'public, max-age=86400, s-maxage=31536000, immutable');
  return res.status(200).send(bytes);
}
