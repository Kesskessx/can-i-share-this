'use strict';

const sharp = require('sharp');
const { pageHtml } = require('./shared-result-render');

function clean(value, max = 220) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, max);
}

function xml(value) {
  return clean(value, 500).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;'
  }[c]));
}

function verdictLabel(verdict) {
  if (verdict === 'high') return 'HIGH RISK';
  if (verdict === 'caution') return 'VERIFY FIRST';
  if (verdict === 'low') return 'NO MAJOR WARNING';
  return 'INCOMPLETE';
}

function palette(verdict) {
  if (verdict === 'high') return { accent: '#ff7770', soft: '#321d22' };
  if (verdict === 'caution') return { accent: '#f0b85b', soft: '#312719' };
  if (verdict === 'low') return { accent: '#61c99a', soft: '#173028' };
  return { accent: '#a5afc1', soft: '#202633' };
}

function wrap(value, maxChars, maxLines) {
  const words = clean(value, 500).split(' ').filter(Boolean);
  const lines = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length <= maxChars || !current) current = next;
    else {
      lines.push(current);
      current = word;
      if (lines.length >= maxLines - 1) break;
    }
  }
  if (current && lines.length < maxLines) lines.push(current);
  if (lines.length === maxLines && words.join(' ').length > lines.join(' ').length) {
    lines[maxLines - 1] = `${lines[maxLines - 1].replace(/[. …]+$/, '').slice(0, Math.max(1, maxChars - 1))}…`;
  }
  return lines;
}

function textLines(lines, x, y, fontSize, weight, color, lineGap) {
  return lines.map((line, index) => `<text x="${x}" y="${y + index * lineGap}" font-family="Arial,Helvetica,sans-serif" font-size="${fontSize}" font-weight="${weight}" fill="${color}">${xml(line)}</text>`).join('');
}

function reasonCard(reason, index, color) {
  const top = 335 + index * 74;
  const title = clean(reason && reason.title, 76) || 'Signal';
  const detail = wrap(reason && reason.detail, 92, 1)[0] || '';
  return `<g>
    <rect x="58" y="${top}" width="1084" height="62" rx="14" fill="#121722" stroke="#2b3342"/>
    <circle cx="82" cy="${top + 31}" r="6" fill="${color}"/>
    <text x="102" y="${top + 26}" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#f5f7fb">${xml(title)}</text>
    <text x="102" y="${top + 47}" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#9ca7b8">${xml(detail)}</text>
  </g>`;
}

async function ogImageResponse(row) {
  const payload = row && row.payload ? row.payload : {};
  const verdict = payload.verdict || 'unknown';
  const colors = palette(verdict);
  const headline = wrap(payload.headline || 'Can I Share This? scan result', 43, 2);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const cards = reasons.length
    ? reasons.map((reason, index) => reasonCard(reason, index, colors.accent)).join('')
    : reasonCard({ title: 'Fresh verification recommended', detail: 'Run a fresh scan before relying on this shared snapshot.' }, 0, colors.accent);

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
    <defs>
      <radialGradient id="glow" cx="78%" cy="14%" r="62%"><stop offset="0" stop-color="#788ff7" stop-opacity=".24"/><stop offset=".58" stop-color="#788ff7" stop-opacity=".04"/><stop offset="1" stop-color="#0b0e14" stop-opacity="0"/></radialGradient>
    </defs>
    <rect width="1200" height="630" fill="#0b0e14"/>
    <rect width="1200" height="630" fill="url(#glow)"/>
    <text x="58" y="76" font-family="Arial,Helvetica,sans-serif" font-size="30" font-weight="800" fill="#f5f7fb">Can I Share <tspan fill="#788ff7">This?</tspan></text>
    <rect x="954" y="48" width="188" height="40" rx="20" fill="#121722" stroke="#2b3342"/>
    <text x="1048" y="74" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#9ca7b8">Shared safety scan</text>
    <rect x="58" y="124" width="${Math.max(150, verdictLabel(verdict).length * 15 + 36)}" height="42" rx="21" fill="${colors.soft}" stroke="${colors.accent}"/>
    <text x="76" y="152" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="800" letter-spacing="1" fill="${colors.accent}">${xml(verdictLabel(verdict))}</text>
    ${textLines(headline, 58, 226, 48, 800, '#f5f7fb', 54)}
    ${cards}
    <text x="58" y="602" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#9ca7b8">Confidence: ${xml(payload.confidence || 'unknown')}</text>
    <text x="1142" y="602" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#dbe1ec">canisharethis.com</text>
  </svg>`;

  const png = await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toBuffer();
  return new Response(png, {
    status: 200,
    headers: {
      'Content-Type': 'image/png',
      'Content-Length': String(png.length)
    }
  });
}

module.exports = { pageHtml, ogImageResponse };
