'use strict';

const { getSharedResult } = require('../lib/shared-results');

function esc(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function cap(value) {
  const v = String(value || '').trim();
  return v ? v.charAt(0).toUpperCase() + v.slice(1) : '';
}
function safeJson(value) {
  return JSON.stringify(value).replace(/</g, '\\u003c').replace(/-->/g, '--\\u003e');
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).send('Method not allowed');
  const id = String((req.query && req.query.id) || '').trim();
  let shared = null;
  try {
    shared = await getSharedResult(id);
  } catch (error) {
    console.error('[cist-result-page]', error && error.message ? error.message : error);
    return res.status(503).send('Shared result temporarily unavailable');
  }
  if (!shared) return res.status(404).send('Shared result not found');

  const p = shared.payload;
  const verdict = p.verdict || 'unknown';
  const reasons = Array.isArray(p.reasons) ? p.reasons.slice(0, 3) : [];
  const description = reasons.length
    ? reasons.map((r) => r.title).filter(Boolean).join(' · ').slice(0, 190)
    : p.headline.slice(0, 190);
  const canonical = `https://canisharethis.com/r/${encodeURIComponent(shared.id)}`;
  const og = `https://canisharethis.com/og/${encodeURIComponent(shared.id)}`;
  const title = `${cap(verdict)} risk — Can I Share This?`;

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=86400');
  return res.status(200).send(`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="${esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Can I Share This?">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:image" content="${esc(og)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${esc(og)}">
<style>
:root{color-scheme:light dark;--bg:#f6f7fb;--card:#fff;--text:#121826;--muted:#667085;--line:#e4e7ec;--accent:#5b6ef5;--soft:#f2f4f7;--danger:#b42318;--warn:#b54708;--ok:#067647}
@media(prefers-color-scheme:dark){:root{--bg:#0f1117;--card:#171a22;--text:#f3f4f6;--muted:#a3aab8;--line:#2b303b;--soft:#20242d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(760px,calc(100% - 28px));margin:0 auto;padding:30px 0 56px}.brand{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}.brand a{color:var(--text);text-decoration:none;font-weight:900;letter-spacing:-.03em}.brand small{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 18px 50px rgba(16,24,40,.08)}.kicker{font-size:11px;text-transform:uppercase;letter-spacing:.09em;font-weight:900;color:var(--muted)}h1{font-size:clamp(26px,6vw,42px);line-height:1.05;letter-spacing:-.04em;margin:8px 0 12px}.status{display:inline-flex;padding:7px 10px;border:1px solid var(--line);border-radius:999px;font-size:12px;font-weight:900;text-transform:uppercase}.status.high{color:var(--danger)}.status.caution{color:var(--warn)}.status.low{color:var(--ok)}.lead{color:var(--muted);line-height:1.55;font-size:14px}.reasons{display:grid;gap:9px;margin:18px 0 0;padding:0;list-style:none}.reasons li{padding:12px 13px;border:1px solid var(--line);border-radius:13px;background:var(--soft)}.reasons strong{display:block;font-size:13px;margin-bottom:3px}.reasons span{display:block;color:var(--muted);font-size:12px;line-height:1.45}.action{margin:16px 0 0;font-weight:750;line-height:1.5}.row{display:flex;gap:9px;flex-wrap:wrap;margin-top:18px}.btn{appearance:none;border:1px solid var(--line);background:var(--text);color:var(--bg);border-radius:12px;padding:11px 14px;font:inherit;font-weight:850;cursor:pointer;text-decoration:none}.btn.secondary{background:var(--card);color:var(--text)}.privacy{margin-top:14px;color:var(--muted);font-size:11px;line-height:1.5}.scanner{margin-top:18px}.scanner h2{margin:0 0 5px;font-size:21px;letter-spacing:-.03em}.scanner p{margin:0 0 14px;color:var(--muted);font-size:13px}.scanform{display:flex;gap:8px}.scanform input{flex:1;min-width:0;padding:13px 14px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--text);font:inherit}.scanform button{border:0;border-radius:12px;padding:0 16px;background:var(--accent);color:#fff;font:inherit;font-weight:900;cursor:pointer}.fresh{display:none;margin-top:14px}.fresh.show{display:block}.fresh h3{margin:0 0 8px;font-size:18px}.fresh ul{margin:10px 0 0;padding-left:18px;color:var(--muted);font-size:12px}.error{color:var(--danger);font-size:12px;margin-top:10px}@media(max-width:560px){.wrap{padding-top:18px}.card{padding:17px}.scanform{display:grid}.scanform button{min-height:46px}}
</style>
</head>
<body>
<main class="wrap">
  <div class="brand"><a href="/">Can I Share This?</a><small>Privacy-filtered result</small></div>
  <section class="card" id="shared-card">
    <div class="kicker">Shared scan summary</div>
    <h1>${esc(p.headline)}</h1>
    <span class="status ${esc(verdict)}">${esc(verdict)} risk · ${esc(p.confidence)} confidence</span>
    <p class="lead">This is a privacy-filtered summary of a previous scan. Run a fresh scan before relying on it.</p>
    <ul class="reasons">${reasons.map((r) => `<li><strong>${esc(r.title || 'Signal')}</strong><span>${esc(r.detail || '')}</span></li>`).join('')}</ul>
    <p class="action">${esc(p.action)}</p>
    <div class="row"><button class="btn" id="share-current" type="button">Share on X</button><a class="btn secondary" href="/">Open full scanner</a></div>
    <div class="privacy">The shared result excludes the original message, full email addresses, phone numbers and crypto addresses.</div>
  </section>

  <section class="card scanner">
    <div class="kicker">Check something yourself</div>
    <h2>Paste anything suspicious</h2>
    <p>Link, message, email, profile or crypto address.</p>
    <form class="scanform" id="fresh-form"><input id="fresh-input" autocomplete="off" placeholder="Paste something suspicious" required><button id="fresh-submit" type="submit">Check it</button></form>
    <div id="fresh-error" class="error"></div>
    <div id="fresh-result" class="fresh"></div>
  </section>
</main>
<script>
(function(){
  var resultId=${safeJson(shared.id)}, parentResultId=${safeJson(shared.parentResultId)}, currentSummary=${safeJson(p)}, freshSummary=null;
  function postEvent(event,result,parent){try{fetch('/api/viral-event',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({event:event,resultId:result||null,parentResultId:parent||null}),keepalive:true}).catch(function(){})}catch(_){}}
  function xIntent(summary,url){var text='Would you open this? '+String(summary.headline||'Can I Share This? scan result').slice(0,150)+' '+url;return 'https://x.com/intent/tweet?text='+encodeURIComponent(text)}
  function openIntent(summary,url){window.open(xIntent(summary,url),'_blank','noopener,noreferrer')}
  postEvent('result_view',resultId,parentResultId);
  document.getElementById('share-current').addEventListener('click',function(){postEvent('share_x',resultId,parentResultId);openIntent(currentSummary,location.href)});
  var form=document.getElementById('fresh-form'),input=document.getElementById('fresh-input'),out=document.getElementById('fresh-result'),err=document.getElementById('fresh-error'),submit=document.getElementById('fresh-submit');
  function escapeHtml(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function renderFresh(summary){var rs=Array.isArray(summary.reasons)?summary.reasons.slice(0,3):[];out.innerHTML='<div class="kicker">Fresh scan result</div><h3>'+escapeHtml(summary.headline||'Scan complete')+'</h3><span class="status '+escapeHtml(summary.verdict||'unknown')+'">'+escapeHtml(summary.verdict||'unknown')+' risk · '+escapeHtml(summary.confidence||'unknown')+' confidence</span><ul>'+rs.map(function(r){return '<li><strong>'+escapeHtml(r.title||'Signal')+':</strong> '+escapeHtml(r.detail||'')+'</li>'}).join('')+'</ul><div class="row"><button class="btn" type="button" id="share-fresh">Share this result on X</button></div>';out.classList.add('show');document.getElementById('share-fresh').addEventListener('click',shareFresh)}
  async function shareFresh(){if(!freshSummary)return;var popup=window.open('about:blank','_blank');try{var response=await fetch('/api/share',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({summary:freshSummary,parentResultId:resultId})});if(!response.ok)throw new Error('share');var data=await response.json();postEvent('new_share',data.id,resultId);postEvent('share_x',data.id,resultId);var target=xIntent(freshSummary,data.url);if(popup)popup.location=target;else location.href=target}catch(e){if(popup)popup.close();err.textContent='Could not create a share link.'}}
  form.addEventListener('submit',async function(e){e.preventDefault();var value=input.value.trim();if(!value)return;err.textContent='';submit.disabled=true;submit.textContent='Checking…';out.classList.remove('show');try{var response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})});var data=await response.json();if(!response.ok||data.error)throw new Error(data.error||'Scan failed');freshSummary=data.shareSummary||null;if(!freshSummary)throw new Error('No share summary');postEvent('new_scan',resultId,parentResultId);renderFresh(freshSummary)}catch(ex){err.textContent=ex&&ex.message?ex.message:'Scan failed.'}finally{submit.disabled=false;submit.textContent='Check it'}});
})();
</script>
</body>
</html>`);
};
