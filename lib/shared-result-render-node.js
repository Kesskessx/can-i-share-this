'use strict';

const sharp = require('sharp');

const OG_VERSION = '3';

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
  if (verdict === 'high') return { accent: '#ff7770', soft: '#321d22', glow: '#ff7770' };
  if (verdict === 'caution') return { accent: '#f0b85b', soft: '#312719', glow: '#f0b85b' };
  if (verdict === 'low') return { accent: '#61c99a', soft: '#173028', glow: '#61c99a' };
  return { accent: '#a5afc1', soft: '#202633', glow: '#788ff7' };
}

function socialHook(verdict) {
  if (verdict === 'caution' || verdict === 'unknown') return 'Would you trust this?';
  return 'Would you open this?';
}

function signalLabel(verdict, count) {
  if (!count) return 'FRESH CHECK RECOMMENDED';
  if (verdict === 'high') return `${count} WARNING SIGNAL${count === 1 ? '' : 'S'}`;
  if (verdict === 'caution') return `${count} SIGNAL${count === 1 ? '' : 'S'} TO VERIFY`;
  return `${count} SIGNAL${count === 1 ? '' : 'S'} REVIEWED`;
}

function shortSummary(verdict, count) {
  if (verdict === 'high') return count ? `${count} warning signal${count === 1 ? '' : 's'} detected. Verify before opening.` : 'Warning signals detected. Verify before opening.';
  if (verdict === 'caution') return count ? `${count} signal${count === 1 ? '' : 's'} need verification before you trust it.` : 'Some signals need verification before you trust it.';
  if (verdict === 'low') return count ? `No major safety warning found. ${count} signal${count === 1 ? '' : 's'} still reviewed below.` : 'No major safety warning found in this snapshot.';
  return 'The scan could not establish a complete result. Verify independently.';
}

function socialDescription(payload, reasons) {
  const titles = reasons.slice(0, 2).map((r) => clean(r && r.title, 56)).filter(Boolean);
  const prefix = shortSummary(payload.verdict || 'unknown', reasons.length);
  return clean(`${prefix}${titles.length ? ` ${titles.join(' · ')}` : ''} Scan yours free.`, 220);
}

function pageHtml(row) {
  const id = row.id;
  const payload = row.payload || {};
  const verdict = payload.verdict || 'unknown';
  const label = verdictLabel(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const canonical = `https://canisharethis.com/r/${id}`;
  const image = `https://canisharethis.com/og/${id}?v=${OG_VERSION}`;
  const hook = socialHook(verdict);
  const description = socialDescription(payload, reasons);
  const socialTitle = `${hook} — ${label}`;
  const reasonHtml = (reasons.length ? reasons : [{ title: 'Fresh verification recommended', detail: 'Run a fresh scan before relying on this snapshot.' }])
    .map((r) => `<li><strong>${html(r.title || 'Signal')}</strong><span>${html(r.detail || '')}</span></li>`).join('');
  const source = JSON.stringify({
    id,
    verdict,
    headline: payload.headline || 'Can I Share This? scan result',
    reasonCount: reasons.length
  }).replace(/</g, '\\u003c');

  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${html(socialTitle)} | Can I Share This?</title><meta name="description" content="${html(description)}"><meta name="robots" content="noindex,follow"><link rel="canonical" href="${canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Can I Share This?"><meta property="og:title" content="${html(socialTitle)}"><meta property="og:description" content="${html(description)}"><meta property="og:url" content="${canonical}"><meta property="og:image" content="${image}"><meta property="og:image:secure_url" content="${image}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="${html(`${hook} ${label}. ${signalLabel(verdict, reasons.length)}.`)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@CanIShareLink"><meta name="twitter:creator" content="@CanIShareLink"><meta name="twitter:title" content="${html(socialTitle)}"><meta name="twitter:description" content="${html(description)}"><meta name="twitter:image" content="${image}"><meta name="twitter:image:alt" content="${html(`${hook} ${label}. ${signalLabel(verdict, reasons.length)}.`)}"><meta name="theme-color" content="#0b0e14">
<style>:root{color-scheme:dark;--bg:#0b0e14;--card:#131822;--text:#f5f7fb;--muted:#9ca7b8;--line:#2b3342;--accent:#788ff7;--good:#61c99a;--warn:#f0b85b;--bad:#ff7770}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse 720px 420px at 50% 70px,rgba(120,143,247,.12),transparent 72%),var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(760px,calc(100% - 28px));margin:auto;padding:26px 0 56px}.brand{font-weight:900;letter-spacing:-.035em;text-decoration:none}.brand b{color:var(--accent)}.result,.scanner{border:1px solid var(--line);border-radius:20px;background:rgba(19,24,34,.95);box-shadow:0 18px 48px rgba(0,0,0,.2)}.result{margin-top:38px;overflow:hidden}.head{padding:25px;border-bottom:1px solid var(--line)}.kicker{font-size:10px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}h1{margin:8px 0 0;font-size:clamp(38px,7vw,62px);line-height:.98;letter-spacing:-.05em}.result[data-risk=high] h1{color:var(--bad)}.result[data-risk=caution] h1{color:var(--warn)}.result[data-risk=low] h1{color:var(--good)}.headline{margin:13px 0 0;color:var(--muted);font-size:17px}.body{padding:22px 25px 25px}.pill{display:inline-flex;padding:5px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:10px;font-weight:800}.reasons{display:grid;gap:8px;margin:17px 0 0;padding:0;list-style:none}.reasons li{padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02)}.reasons strong,.reasons span{display:block}.reasons strong{font-size:12px}.reasons span{margin-top:3px;color:var(--muted);font-size:11px}.action{margin-top:16px;padding:13px 14px;border-left:3px solid var(--accent);border-radius:10px;background:rgba(120,143,247,.07);font-weight:750}.note{margin:12px 0 0;color:var(--muted);font-size:10px}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.btn{appearance:none;border:1px solid var(--line);border-radius:10px;background:#181d28;color:var(--text);padding:9px 12px;font:inherit;font-size:12px;font-weight:850;cursor:pointer;text-decoration:none}.btn.primary{background:var(--accent);border-color:var(--accent);color:white}.scanner{margin-top:20px;padding:22px}.scanner h2{margin:0;font-size:23px;letter-spacing:-.035em}.scanner>p{margin:6px 0 14px;color:var(--muted);font-size:12px}.scan{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}.scan input{min-width:0;height:50px;padding:0 13px;border:1px solid var(--line);border-radius:11px;background:#0e1219;color:var(--text);font:inherit;outline:none}.scan input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(120,143,247,.12)}.scan button{height:50px;padding:0 18px;border:0;border-radius:11px;background:var(--accent);color:white;font:inherit;font-weight:900;cursor:pointer}.scan button:disabled{opacity:.6}.status{min-height:18px;margin-top:8px;color:var(--muted);font-size:11px}.fresh{display:none;margin-top:13px;padding:14px;border:1px solid var(--line);border-radius:13px;background:#10151e}.fresh.show{display:block}.fresh h3{margin:0;font-size:18px}.fresh p{margin:5px 0 0;color:var(--muted);font-size:12px}.fresh .btn{margin-top:12px}.viral-hint{margin:14px 0 0;color:var(--muted);font-size:11px}.viral-hint b{color:var(--text)}@media(max-width:620px){.wrap{padding-top:18px}.result{margin-top:26px}.head,.body,.scanner{padding:18px}.scan{grid-template-columns:1fr}.scan button{width:100%}.buttons .btn{flex:1;text-align:center}}</style></head><body>
<main class="wrap"><a class="brand" href="/">Can I Share <b>This?</b></a><section class="result" data-risk="${html(verdict)}"><div class="head"><div class="kicker">Shared safety scan</div><h1>${html(label)}</h1><p class="headline">${html(payload.headline || 'Can I Share This? scan result')}</p></div><div class="body"><span class="pill">Confidence: ${html(payload.confidence || 'unknown')}</span><ul class="reasons">${reasonHtml}</ul><div class="action">${html(payload.action || 'Verify independently before acting.')}</div><p class="note">Privacy-filtered snapshot. Run a fresh scan before relying on it.</p><div class="buttons"><button id="share-source" class="btn primary" type="button">Share on X</button><a class="btn" href="/">Open full scanner</a></div><p class="viral-hint"><b>Challenge your followers:</b> ask “Would you open this?”</p></div></section>
<section class="scanner"><h2>Got another suspicious link?</h2><p>Run a fresh scan, then post the result on X and ask your followers what they would do.</p><form id="scan" class="scan"><input id="input" autocomplete="off" spellcheck="false" placeholder="Paste a link, message, email or username…" required><button id="analyze" type="submit">Check it</button></form><div id="status" class="status" role="status" aria-live="polite"></div><div id="fresh" class="fresh"></div></section></main>
<script>(function(){var SOURCE=${source},form=document.getElementById('scan'),input=document.getElementById('input'),button=document.getElementById('analyze'),status=document.getElementById('status'),fresh=document.getElementById('fresh'),latest=null;function api(action,body){return fetch('/api/event?action='+encodeURIComponent(action),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:action==='viral-event'})}function evt(name,resultId,parentId){api('viral-event',{event:name,resultId:resultId||null,parentResultId:parentId||null}).catch(function(){})}function postText(source){var v=String(source&&source.verdict||'unknown'),n=Number(source&&source.reasonCount||0),plural=n===1?'':'s';if(v==='high')return'⚠️ Would you open this?\n\nCan I Share This? found '+(n||'multiple')+' warning signal'+(n===1?'':'s')+'.';if(v==='caution')return'👀 Would you trust this?\n\n'+(n||'Some')+' signal'+plural+' need verification.';if(v==='low')return'🔎 I checked this before opening it.\n\nNo major warning found'+(n?' · '+n+' signal'+plural+' reviewed':'')+'.\nWould you trust it?';return'🔎 I checked this before opening it.\n\nThe result was incomplete. Would you trust it?'}function intent(url,source){return'https://x.com/intent/tweet?text='+encodeURIComponent(postText(source))+'&url='+encodeURIComponent(url)}function safe(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function lab(v){return v==='high'?'HIGH RISK':v==='caution'?'VERIFY FIRST':v==='low'?'NO MAJOR WARNING':'INCOMPLETE'}evt('result_view',SOURCE.id,null);document.getElementById('share-source').addEventListener('click',function(){evt('share_x',SOURCE.id,null);window.open(intent(location.href,SOURCE),'_blank','noopener,noreferrer')});form.addEventListener('submit',async function(e){e.preventDefault();var value=String(input.value||'').trim();if(!value)return;latest=null;fresh.classList.remove('show');button.disabled=true;button.textContent='Checking…';status.textContent='Checking available evidence…';try{var response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})}),data=await response.json();if(!response.ok||data.error)throw new Error(data.error||'Analysis failed');latest=data;var s=data.shareSummary||{},risk=(data.megaScanner&&data.megaScanner.finalRisk)||s.verdict||'unknown',reasons=Array.isArray(s.reasons)?s.reasons.slice(0,3):[];fresh.innerHTML='<h3>'+safe(lab(risk))+'</h3><p>'+safe(s.headline||data.summary||'Fresh scan completed.')+'</p>'+(reasons.length?'<ul class="reasons">'+reasons.map(function(r){return'<li><strong>'+safe(r.title||'Signal')+'</strong><span>'+safe(r.detail||'')+'</span></li>'}).join('')+'</ul>':'')+'<button id="share-fresh" class="btn primary" type="button">Post my result on X</button>';fresh.classList.add('show');status.textContent='Fresh scan completed.';evt('new_scan',null,SOURCE.id);document.getElementById('share-fresh').addEventListener('click',async function(){var b=this,popup=window.open('about:blank','_blank');b.disabled=true;b.textContent='Preparing…';try{var created=await api('share-result',{summary:latest.shareSummary,parentResultId:SOURCE.id}),out=await created.json();if(!created.ok||!out.url)throw new Error(out.error||'Share failed');evt('new_share',out.id,SOURCE.id);evt('share_x',out.id,SOURCE.id);var target=intent(out.url,{verdict:latest.shareSummary.verdict,reasonCount:Array.isArray(latest.shareSummary.reasons)?latest.shareSummary.reasons.length:0});if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');b.textContent='Posted on X'}catch(err){if(popup)popup.close();b.disabled=false;b.textContent='Post my result on X';status.textContent='Could not prepare shared result.'}})}catch(err){status.textContent=err&&err.message?err.message:'Analysis unavailable.'}finally{button.disabled=false;button.textContent='Check it'}})})();</script></body></html>`;
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
  return lines.map((line, i) => `<text x="${x}" y="${y + i * gap}" font-family="DejaVu Sans,Arial,sans-serif" font-size="${fontSize}" font-weight="${weight}" fill="${color}">${xml(line)}</text>`).join('');
}

function reasonCard(reason, index, color) {
  const top = 338 + index * 104;
  const title = wrap(reason && reason.title ? reason.title : 'Signal', 48, 1)[0] || 'Signal';
  const detail = wrap(reason && reason.detail ? reason.detail : '', 88, 1)[0] || '';
  return `<g><rect x="58" y="${top}" width="1084" height="88" rx="18" fill="#121722" stroke="#2b3342"/><rect x="58" y="${top}" width="5" height="88" rx="2.5" fill="${color}"/><circle cx="91" cy="${top + 31}" r="7" fill="${color}"/><text x="114" y="${top + 38}" font-family="DejaVu Sans,Arial,sans-serif" font-size="24" font-weight="800" fill="#f5f7fb">${xml(title)}</text>${detail ? `<text x="91" y="${top + 68}" font-family="DejaVu Sans,Arial,sans-serif" font-size="16" fill="#aab4c3">${xml(detail)}</text>` : ''}</g>`;
}

async function ogImageResponse(row) {
  const payload = row && row.payload ? row.payload : {};
  const verdict = payload.verdict || 'unknown';
  const colors = palette(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const visibleReasons = (reasons.length ? reasons : [{ title: 'Fresh verification recommended', detail: 'Run a fresh scan before relying on this shared snapshot.' }]).slice(0, 2);
  const cards = visibleReasons.map((reason, i) => reasonCard(reason, i, colors.accent)).join('');
  const hook = socialHook(verdict);
  const label = verdictLabel(verdict);
  const signals = signalLabel(verdict, reasons.length);
  const summary = shortSummary(verdict, reasons.length);
  const badgeWidth = Math.max(160, label.length * 15 + 42);
  const signalWidth = Math.max(210, signals.length * 12 + 38);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><defs><radialGradient id="g" cx="82%" cy="8%" r="70%"><stop offset="0" stop-color="${colors.glow}" stop-opacity=".20"/><stop offset=".52" stop-color="#788ff7" stop-opacity=".035"/><stop offset="1" stop-color="#0b0e14" stop-opacity="0"/></radialGradient><linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${colors.accent}" stop-opacity=".55"/><stop offset="1" stop-color="#788ff7" stop-opacity=".05"/></linearGradient></defs><rect width="1200" height="630" fill="#0b0e14"/><rect width="1200" height="630" fill="url(#g)"/><rect x="0" y="0" width="1200" height="5" fill="url(#edge)"/><text x="58" y="73" font-family="DejaVu Sans,Arial,sans-serif" font-size="29" font-weight="800" fill="#f5f7fb">Can I Share <tspan fill="#788ff7">This?</tspan></text><rect x="914" y="40" width="228" height="46" rx="23" fill="#171d2a" stroke="#3a4660"/><text x="1028" y="69" text-anchor="middle" font-family="DejaVu Sans,Arial,sans-serif" font-size="14" font-weight="800" fill="#dfe5ef">SCAN YOURS FREE →</text><text x="58" y="166" font-family="DejaVu Sans,Arial,sans-serif" font-size="62" font-weight="800" letter-spacing="-2" fill="#f7f9fc">${xml(hook)}</text><rect x="58" y="205" width="${badgeWidth}" height="46" rx="23" fill="${colors.soft}" stroke="${colors.accent}"/><text x="80" y="235" font-family="DejaVu Sans,Arial,sans-serif" font-size="18" font-weight="800" letter-spacing="1" fill="${colors.accent}">${xml(label)}</text><rect x="${74 + badgeWidth}" y="205" width="${signalWidth}" height="46" rx="23" fill="#141a25" stroke="#30394a"/><text x="${94 + badgeWidth}" y="235" font-family="DejaVu Sans,Arial,sans-serif" font-size="16" font-weight="800" letter-spacing=".5" fill="#b8c2d0">${xml(signals)}</text>${textLines(wrap(summary, 82, 1),58,301,21,600,'#b4becd',28)}${cards}<text x="1142" y="585" text-anchor="end" font-family="DejaVu Sans,Arial,sans-serif" font-size="16" font-weight="800" fill="#e5e9f0">canisharethis.com</text></svg>`;
  const png = await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toBuffer();
  return new Response(png, { status: 200, headers: { 'Content-Type': 'image/png', 'Content-Length': String(png.length) } });
}

module.exports = { pageHtml, ogImageResponse };
