'use strict';

const sharp = require('sharp');

function clean(value, max = 220) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, max);
}

function html(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
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

function pageHtml(row) {
  const id = row.id;
  const payload = row.payload || {};
  const verdict = payload.verdict || 'unknown';
  const label = verdictLabel(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const canonical = `https://canisharethis.com/r/${id}`;
  const image = `https://canisharethis.com/og/${id}`;
  const description = [payload.headline, ...reasons.slice(0, 2).map((r) => r && r.title)]
    .filter(Boolean).map((v) => clean(v, 100)).join(' · ').slice(0, 220) || 'Shared safety scan from Can I Share This?';
  const reasonHtml = (reasons.length ? reasons : [{ title: 'Fresh verification recommended', detail: 'Run a fresh scan before relying on this snapshot.' }])
    .map((r) => `<li><strong>${html(r.title || 'Signal')}</strong><span>${html(r.detail || '')}</span></li>`).join('');
  const source = JSON.stringify({ id, verdict, headline: payload.headline || 'Can I Share This? scan result' }).replace(/</g, '\\u003c');

  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${html(label)} — Can I Share This?</title><meta name="description" content="${html(description)}"><meta name="robots" content="noindex,follow"><link rel="canonical" href="${canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Can I Share This?"><meta property="og:title" content="${html(label)} — Can I Share This?"><meta property="og:description" content="${html(description)}"><meta property="og:url" content="${canonical}"><meta property="og:image" content="${image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="${html(label)} safety scan result">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${html(label)} — Can I Share This?"><meta name="twitter:description" content="${html(description)}"><meta name="twitter:image" content="${image}"><meta name="theme-color" content="#0b0e14">
<style>:root{color-scheme:dark;--bg:#0b0e14;--card:#131822;--text:#f5f7fb;--muted:#9ca7b8;--line:#2b3342;--accent:#788ff7;--good:#61c99a;--warn:#f0b85b;--bad:#ff7770}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse 720px 420px at 50% 70px,rgba(120,143,247,.12),transparent 72%),var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(760px,calc(100% - 28px));margin:auto;padding:26px 0 56px}.brand{font-weight:900;letter-spacing:-.035em;text-decoration:none}.brand b{color:var(--accent)}.result,.scanner{border:1px solid var(--line);border-radius:20px;background:rgba(19,24,34,.95);box-shadow:0 18px 48px rgba(0,0,0,.2)}.result{margin-top:38px;overflow:hidden}.head{padding:25px;border-bottom:1px solid var(--line)}.kicker{font-size:10px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}h1{margin:8px 0 0;font-size:clamp(38px,7vw,62px);line-height:.98;letter-spacing:-.05em}.result[data-risk=high] h1{color:var(--bad)}.result[data-risk=caution] h1{color:var(--warn)}.result[data-risk=low] h1{color:var(--good)}.headline{margin:13px 0 0;color:var(--muted);font-size:17px}.body{padding:22px 25px 25px}.pill{display:inline-flex;padding:5px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:10px;font-weight:800}.reasons{display:grid;gap:8px;margin:17px 0 0;padding:0;list-style:none}.reasons li{padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02)}.reasons strong,.reasons span{display:block}.reasons strong{font-size:12px}.reasons span{margin-top:3px;color:var(--muted);font-size:11px}.action{margin-top:16px;padding:13px 14px;border-left:3px solid var(--accent);border-radius:10px;background:rgba(120,143,247,.07);font-weight:750}.note{margin:12px 0 0;color:var(--muted);font-size:10px}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.btn{appearance:none;border:1px solid var(--line);border-radius:10px;background:#181d28;color:var(--text);padding:9px 12px;font:inherit;font-size:12px;font-weight:850;cursor:pointer;text-decoration:none}.btn.primary{background:var(--accent);border-color:var(--accent);color:white}.scanner{margin-top:20px;padding:22px}.scanner h2{margin:0;font-size:23px;letter-spacing:-.035em}.scanner>p{margin:6px 0 14px;color:var(--muted);font-size:12px}.scan{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}.scan input{min-width:0;height:50px;padding:0 13px;border:1px solid var(--line);border-radius:11px;background:#0e1219;color:var(--text);font:inherit;outline:none}.scan input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(120,143,247,.12)}.scan button{height:50px;padding:0 18px;border:0;border-radius:11px;background:var(--accent);color:white;font:inherit;font-weight:900;cursor:pointer}.scan button:disabled{opacity:.6}.status{min-height:18px;margin-top:8px;color:var(--muted);font-size:11px}.fresh{display:none;margin-top:13px;padding:14px;border:1px solid var(--line);border-radius:13px;background:#10151e}.fresh.show{display:block}.fresh h3{margin:0;font-size:18px}.fresh p{margin:5px 0 0;color:var(--muted);font-size:12px}.fresh .btn{margin-top:12px}@media(max-width:620px){.wrap{padding-top:18px}.result{margin-top:26px}.head,.body,.scanner{padding:18px}.scan{grid-template-columns:1fr}.scan button{width:100%}.buttons .btn{flex:1;text-align:center}}</style></head><body>
<main class="wrap"><a class="brand" href="/">Can I Share <b>This?</b></a><section class="result" data-risk="${html(verdict)}"><div class="head"><div class="kicker">Shared safety scan</div><h1>${html(label)}</h1><p class="headline">${html(payload.headline || 'Can I Share This? scan result')}</p></div><div class="body"><span class="pill">Confidence: ${html(payload.confidence || 'unknown')}</span><ul class="reasons">${reasonHtml}</ul><div class="action">${html(payload.action || 'Verify independently before acting.')}</div><p class="note">Privacy-filtered snapshot. Run a fresh scan before relying on it.</p><div class="buttons"><button id="share-source" class="btn primary" type="button">Share on X</button><a class="btn" href="/">Open full scanner</a></div></div></section>
<section class="scanner"><h2>Check something suspicious</h2><p>Paste a link, message, email, social profile or crypto address. The new result appears directly below.</p><form id="scan" class="scan"><input id="input" autocomplete="off" spellcheck="false" placeholder="Paste something suspicious…" required><button id="analyze" type="submit">Analyze</button></form><div id="status" class="status" role="status" aria-live="polite"></div><div id="fresh" class="fresh"></div></section></main>
<script>(function(){var SOURCE=${source},form=document.getElementById('scan'),input=document.getElementById('input'),button=document.getElementById('analyze'),status=document.getElementById('status'),fresh=document.getElementById('fresh'),latest=null;function api(action,body){return fetch('/api/event?action='+encodeURIComponent(action),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:action==='viral-event'})}function evt(name,resultId,parentId){api('viral-event',{event:name,resultId:resultId||null,parentResultId:parentId||null}).catch(function(){})}function intent(url,headline,verdict){var lead=verdict==='high'?'Would you open this?':verdict==='caution'?'Would you trust this?':'I checked this before opening it.';return'https://x.com/intent/tweet?text='+encodeURIComponent(lead+' '+String(headline||'Can I Share This? scan result'))+'&url='+encodeURIComponent(url)}function safe(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function lab(v){return v==='high'?'HIGH RISK':v==='caution'?'VERIFY FIRST':v==='low'?'NO MAJOR WARNING':'INCOMPLETE'}evt('result_view',SOURCE.id,null);document.getElementById('share-source').addEventListener('click',function(){evt('share_x',SOURCE.id,null);window.open(intent(location.href,SOURCE.headline,SOURCE.verdict),'_blank','noopener,noreferrer')});form.addEventListener('submit',async function(e){e.preventDefault();var value=String(input.value||'').trim();if(!value)return;latest=null;fresh.classList.remove('show');button.disabled=true;button.textContent='Analyzing…';status.textContent='Checking available evidence…';try{var response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})}),data=await response.json();if(!response.ok||data.error)throw new Error(data.error||'Analysis failed');latest=data;var s=data.shareSummary||{},risk=(data.megaScanner&&data.megaScanner.finalRisk)||s.verdict||'unknown',reasons=Array.isArray(s.reasons)?s.reasons.slice(0,3):[];fresh.innerHTML='<h3>'+safe(lab(risk))+'</h3><p>'+safe(s.headline||data.summary||'Fresh scan completed.')+'</p>'+(reasons.length?'<ul class="reasons">'+reasons.map(function(r){return'<li><strong>'+safe(r.title||'Signal')+'</strong><span>'+safe(r.detail||'')+'</span></li>'}).join('')+'</ul>':'')+'<button id="share-fresh" class="btn primary" type="button">Share this result on X</button>';fresh.classList.add('show');status.textContent='Fresh scan completed.';evt('new_scan',null,SOURCE.id);document.getElementById('share-fresh').addEventListener('click',async function(){var b=this,popup=window.open('about:blank','_blank');b.disabled=true;b.textContent='Preparing…';try{var created=await api('share-result',{summary:latest.shareSummary,parentResultId:SOURCE.id}),out=await created.json();if(!created.ok||!out.url)throw new Error(out.error||'Share failed');evt('new_share',out.id,SOURCE.id);evt('share_x',out.id,SOURCE.id);var target=intent(out.url,latest.shareSummary.headline,latest.shareSummary.verdict);if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');b.textContent='Shared on X'}catch(err){if(popup)popup.close();b.disabled=false;b.textContent='Share this result on X';status.textContent='Could not prepare shared result.'}})}catch(err){status.textContent=err&&err.message?err.message:'Analysis unavailable.'}finally{button.disabled=false;button.textContent='Analyze'}})})();</script></body></html>`;
}

function wrap(value, maxChars, maxLines) {
  const words = clean(value, 500).split(' ').filter(Boolean), lines = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length <= maxChars || !current) current = next;
    else { lines.push(current); current = word; if (lines.length >= maxLines - 1) break; }
  }
  if (current && lines.length < maxLines) lines.push(current);
  if (lines.length === maxLines && words.join(' ').length > lines.join(' ').length) lines[maxLines - 1] = `${lines[maxLines - 1].replace(/[. …]+$/, '').slice(0, Math.max(1, maxChars - 1))}…`;
  return lines;
}

function textLines(lines, x, y, fontSize, weight, color, gap) {
  return lines.map((line, i) => `<text x="${x}" y="${y + i * gap}" font-family="Arial,Helvetica,sans-serif" font-size="${fontSize}" font-weight="${weight}" fill="${color}">${xml(line)}</text>`).join('');
}

function reasonCard(reason, index, color) {
  const top = 335 + index * 74;
  return `<g><rect x="58" y="${top}" width="1084" height="62" rx="14" fill="#121722" stroke="#2b3342"/><circle cx="82" cy="${top + 31}" r="6" fill="${color}"/><text x="102" y="${top + 26}" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#f5f7fb">${xml(clean(reason && reason.title, 76) || 'Signal')}</text><text x="102" y="${top + 47}" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#9ca7b8">${xml(wrap(reason && reason.detail, 92, 1)[0] || '')}</text></g>`;
}

async function ogImageResponse(row) {
  const payload = row && row.payload ? row.payload : {}, verdict = payload.verdict || 'unknown', colors = palette(verdict), headline = wrap(payload.headline || 'Can I Share This? scan result', 43, 2), reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const cards = (reasons.length ? reasons : [{ title: 'Fresh verification recommended', detail: 'Run a fresh scan before relying on this shared snapshot.' }]).map((reason, i) => reasonCard(reason, i, colors.accent)).join('');
  const badgeWidth = Math.max(150, verdictLabel(verdict).length * 15 + 36);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><defs><radialGradient id="g" cx="78%" cy="14%" r="62%"><stop offset="0" stop-color="#788ff7" stop-opacity=".24"/><stop offset=".58" stop-color="#788ff7" stop-opacity=".04"/><stop offset="1" stop-color="#0b0e14" stop-opacity="0"/></radialGradient></defs><rect width="1200" height="630" fill="#0b0e14"/><rect width="1200" height="630" fill="url(#g)"/><text x="58" y="76" font-family="Arial,Helvetica,sans-serif" font-size="30" font-weight="800" fill="#f5f7fb">Can I Share <tspan fill="#788ff7">This?</tspan></text><rect x="954" y="48" width="188" height="40" rx="20" fill="#121722" stroke="#2b3342"/><text x="1048" y="74" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#9ca7b8">Shared safety scan</text><rect x="58" y="124" width="${badgeWidth}" height="42" rx="21" fill="${colors.soft}" stroke="${colors.accent}"/><text x="76" y="152" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="800" letter-spacing="1" fill="${colors.accent}">${xml(verdictLabel(verdict))}</text>${textLines(headline,58,226,48,800,'#f5f7fb',54)}${cards}<text x="58" y="602" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#9ca7b8">Confidence: ${xml(payload.confidence || 'unknown')}</text><text x="1142" y="602" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#dbe1ec">canisharethis.com</text></svg>`;
  const png = await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toBuffer();
  return new Response(png, { status: 200, headers: { 'Content-Type': 'image/png', 'Content-Length': String(png.length) } });
}

module.exports = { pageHtml, ogImageResponse };
