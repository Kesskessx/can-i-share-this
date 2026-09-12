'use strict';

const React = require('react');

function esc(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function compact(value, max = 220) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, max);
}

function verdictLabel(verdict) {
  if (verdict === 'high') return 'HIGH RISK';
  if (verdict === 'caution') return 'VERIFY FIRST';
  if (verdict === 'low') return 'NO MAJOR WARNING';
  return 'INCOMPLETE';
}

function verdictColor(verdict) {
  if (verdict === 'high') return '#ff7770';
  if (verdict === 'caution') return '#f0b85b';
  if (verdict === 'low') return '#61c99a';
  return '#a5afc1';
}

function pageHtml(row) {
  const id = row.id;
  const payload = row.payload || {};
  const verdict = payload.verdict || 'unknown';
  const label = verdictLabel(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const canonical = `https://canisharethis.com/r/${id}`;
  const ogImage = `https://canisharethis.com/og/${id}`;
  const description = [payload.headline, ...reasons.slice(0, 2).map((r) => r && r.title)]
    .filter(Boolean).map((x) => compact(x, 100)).join(' · ').slice(0, 220) || 'Shared safety scan from Can I Share This?';
  const reasonsHtml = reasons.length
    ? reasons.map((r) => `<li><strong>${esc(r.title || 'Signal')}</strong><span>${esc(r.detail || '')}</span></li>`).join('')
    : '<li><strong>No additional warning detail</strong><span>Run a fresh scan before relying on this result.</span></li>';
  const source = JSON.stringify({ id, verdict, headline: payload.headline || 'Can I Share This? scan result' }).replace(/</g, '\\u003c');

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(label)} — Can I Share This?</title>
<meta name="description" content="${esc(description)}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Can I Share This?">
<meta property="og:title" content="${esc(label)} — Can I Share This?">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${ogImage}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(label)} safety scan result">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(label)} — Can I Share This?">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${ogImage}">
<meta name="theme-color" content="#0b0e14">
<style>
:root{color-scheme:dark;--bg:#0b0e14;--card:#131822;--text:#f5f7fb;--muted:#9ca7b8;--line:#2b3342;--accent:#788ff7;--good:#61c99a;--warn:#f0b85b;--bad:#ff7770}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse 720px 420px at 50% 70px,rgba(120,143,247,.12),transparent 72%),var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(760px,calc(100% - 28px));margin:auto;padding:26px 0 56px}.brand{font-weight:900;letter-spacing:-.035em;text-decoration:none}.brand b{color:var(--accent)}.result,.scanner{border:1px solid var(--line);border-radius:20px;background:rgba(19,24,34,.95);box-shadow:0 18px 48px rgba(0,0,0,.2)}.result{margin-top:38px;overflow:hidden}.head{padding:25px;border-bottom:1px solid var(--line)}.kicker{font-size:10px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}h1{margin:8px 0 0;font-size:clamp(38px,7vw,62px);line-height:.98;letter-spacing:-.05em}.result[data-risk=high] h1{color:var(--bad)}.result[data-risk=caution] h1{color:var(--warn)}.result[data-risk=low] h1{color:var(--good)}.headline{margin:13px 0 0;color:var(--muted);font-size:17px}.body{padding:22px 25px 25px}.meta{display:flex;gap:7px;flex-wrap:wrap}.pill{padding:5px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:10px;font-weight:800}.reasons{display:grid;gap:8px;margin:17px 0 0;padding:0;list-style:none}.reasons li{padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02)}.reasons strong,.reasons span{display:block}.reasons strong{font-size:12px}.reasons span{margin-top:3px;color:var(--muted);font-size:11px}.action{margin-top:16px;padding:13px 14px;border-left:3px solid var(--accent);border-radius:10px;background:rgba(120,143,247,.07);font-weight:750}.note{margin:12px 0 0;color:var(--muted);font-size:10px}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.btn{appearance:none;border:1px solid var(--line);border-radius:10px;background:#181d28;color:var(--text);padding:9px 12px;font:inherit;font-size:12px;font-weight:850;cursor:pointer;text-decoration:none}.btn.primary{background:var(--accent);border-color:var(--accent);color:white}.scanner{margin-top:20px;padding:22px}.scanner h2{margin:0;font-size:23px;letter-spacing:-.035em}.scanner>p{margin:6px 0 14px;color:var(--muted);font-size:12px}.scan-form{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}.scan-form input{min-width:0;height:50px;padding:0 13px;border:1px solid var(--line);border-radius:11px;background:#0e1219;color:var(--text);font:inherit;outline:none}.scan-form input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(120,143,247,.12)}.scan-form button{height:50px;padding:0 18px;border:0;border-radius:11px;background:var(--accent);color:white;font:inherit;font-weight:900;cursor:pointer}.scan-form button:disabled{opacity:.6}.status{min-height:18px;margin-top:8px;color:var(--muted);font-size:11px}.fresh{display:none;margin-top:13px;padding:14px;border:1px solid var(--line);border-radius:13px;background:#10151e}.fresh.show{display:block}.fresh h3{margin:0;font-size:18px}.fresh p{margin:5px 0 0;color:var(--muted);font-size:12px}.fresh .btn{margin-top:12px}@media(max-width:620px){.wrap{padding-top:18px}.result{margin-top:26px}.head,.body,.scanner{padding:18px}.scan-form{grid-template-columns:1fr}.scan-form button{width:100%}.buttons .btn{flex:1;text-align:center}}
</style>
</head>
<body>
<main class="wrap">
<a class="brand" href="/"><span>Can I Share </span><b>This?</b></a>
<section class="result" data-risk="${esc(verdict)}">
<div class="head"><div class="kicker">Shared safety scan</div><h1>${esc(label)}</h1><p class="headline">${esc(payload.headline || 'Can I Share This? scan result')}</p></div>
<div class="body"><div class="meta"><span class="pill">Confidence: ${esc(payload.confidence || 'unknown')}</span><span class="pill">Privacy-filtered snapshot</span></div><ul class="reasons">${reasonsHtml}</ul><div class="action">${esc(payload.action || 'Verify independently before acting.')}</div><p class="note">This result is a snapshot, not a guarantee. Run a fresh scan before relying on it.</p><div class="buttons"><button id="share-source" class="btn primary" type="button">Share on X</button><a class="btn" href="/">Open full scanner</a></div></div>
</section>
<section class="scanner"><h2>Check something suspicious</h2><p>Paste a link, message, email, social profile or crypto address. The result appears here.</p><form id="scan" class="scan-form"><input id="input" autocomplete="off" spellcheck="false" placeholder="Paste something suspicious…" required><button id="analyze" type="submit">Analyze</button></form><div id="status" class="status" role="status" aria-live="polite"></div><div id="fresh" class="fresh"></div></section>
</main>
<script>
(function(){
var SOURCE=${source},form=document.getElementById('scan'),input=document.getElementById('input'),button=document.getElementById('analyze'),status=document.getElementById('status'),fresh=document.getElementById('fresh'),latest=null;
function api(action,body){return fetch('/api/event?action='+encodeURIComponent(action),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:action==='viral-event'})}
function event(name,resultId,parentId){api('viral-event',{event:name,resultId:resultId||null,parentResultId:parentId||null}).catch(function(){})}
function intent(url,headline,verdict){var lead=verdict==='high'?'Would you open this?':verdict==='caution'?'Would you trust this?':'I checked this before opening it.';return'https://x.com/intent/tweet?text='+encodeURIComponent(lead+' '+String(headline||'Can I Share This? scan result'))+'&url='+encodeURIComponent(url)}
function openX(url,headline,verdict){window.open(intent(url,headline,verdict),'_blank','noopener,noreferrer')}
function html(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function label(v){return v==='high'?'HIGH RISK':v==='caution'?'VERIFY FIRST':v==='low'?'NO MAJOR WARNING':'INCOMPLETE'}
event('result_view',SOURCE.id,null);
document.getElementById('share-source').addEventListener('click',function(){event('share_x',SOURCE.id,null);openX(location.href,SOURCE.headline,SOURCE.verdict)});
form.addEventListener('submit',async function(e){e.preventDefault();var value=String(input.value||'').trim();if(!value)return;latest=null;fresh.classList.remove('show');fresh.innerHTML='';button.disabled=true;button.textContent='Analyzing…';status.textContent='Checking available evidence…';try{var response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})});var data=await response.json();if(!response.ok||data.error)throw new Error(data.error||'Analysis failed');latest=data;var s=data.shareSummary||{},risk=(data.megaScanner&&data.megaScanner.finalRisk)||s.verdict||'unknown',reasons=Array.isArray(s.reasons)?s.reasons.slice(0,3):[];fresh.innerHTML='<h3>'+html(label(risk))+'</h3><p>'+html(s.headline||data.summary||'Fresh scan completed.')+'</p>'+(reasons.length?'<ul class="reasons">'+reasons.map(function(r){return'<li><strong>'+html(r.title||'Signal')+'</strong><span>'+html(r.detail||'')+'</span></li>'}).join('')+'</ul>':'')+'<button id="share-fresh" class="btn primary" type="button">Share this result on X</button>';fresh.classList.add('show');status.textContent='Fresh scan completed.';event('new_scan',null,SOURCE.id);document.getElementById('share-fresh').addEventListener('click',async function(){if(!latest||!latest.shareSummary)return;var shareButton=this,popup=window.open('about:blank','_blank');if(popup)try{popup.opener=null}catch(_){}shareButton.disabled=true;shareButton.textContent='Preparing…';try{var created=await api('share-result',{summary:latest.shareSummary,parentResultId:SOURCE.id}),out=await created.json();if(!created.ok||!out.url)throw new Error(out.error||'Share failed');event('new_share',out.id,SOURCE.id);event('share_x',out.id,SOURCE.id);var target=intent(out.url,latest.shareSummary.headline,latest.shareSummary.verdict);if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');shareButton.textContent='Shared on X'}catch(err){if(popup)popup.close();shareButton.disabled=false;shareButton.textContent='Share this result on X';status.textContent='Could not prepare shared result.'}})}catch(err){status.textContent=err&&err.message?err.message:'Analysis unavailable.'}finally{button.disabled=false;button.textContent='Analyze'}})
})();
</script>
</body></html>`;
}

async function ogImageResponse(row) {
  const payload = row.payload || {};
  const verdict = payload.verdict || 'unknown';
  const color = verdictColor(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const { ImageResponse } = await import('@vercel/og');
  const e = React.createElement;
  const reasonCards = reasons.map((r, i) => e('div',{key:i,style:{display:'flex',alignItems:'center',gap:14,padding:'11px 14px',border:'1px solid #2b3342',borderRadius:14,background:'#121722'}},e('div',{style:{width:10,height:10,borderRadius:99,background:color,flex:'0 0 auto'}}),e('div',{style:{display:'flex',flexDirection:'column'}},e('div',{style:{fontSize:22,fontWeight:800,color:'#f5f7fb'}},compact(r&&r.title,70)||'Signal'),e('div',{style:{fontSize:16,color:'#9ca7b8',marginTop:2}},compact(r&&r.detail,120)))));
  return new ImageResponse(e('div',{style:{width:'100%',height:'100%',display:'flex',flexDirection:'column',padding:56,background:'radial-gradient(circle at 76% 16%, rgba(120,143,247,.20), transparent 34%), #0b0e14',color:'#f5f7fb',fontFamily:'sans-serif'}},e('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center'}},e('div',{style:{display:'flex',fontSize:30,fontWeight:900}},'Can I Share ',e('span',{style:{color:'#788ff7',marginLeft:5}},'This?')),e('div',{style:{fontSize:17,color:'#9ca7b8',border:'1px solid #2b3342',borderRadius:99,padding:'8px 13px'}},'Shared safety scan')),e('div',{style:{display:'flex',flexDirection:'column',marginTop:46}},e('div',{style:{display:'flex',alignSelf:'flex-start',fontSize:19,fontWeight:900,color:color,border:`1px solid ${color}`,borderRadius:99,padding:'7px 12px'}},verdictLabel(verdict)),e('div',{style:{fontSize:52,fontWeight:900,lineHeight:1.05,letterSpacing:'-0.04em',marginTop:16,maxWidth:1040}},compact(payload.headline,170)||'Can I Share This? scan result')),e('div',{style:{display:'flex',flexDirection:'column',gap:9,marginTop:28}},...(reasonCards.length?reasonCards:[e('div',{key:'empty',style:{padding:'13px 15px',border:'1px solid #2b3342',borderRadius:14,color:'#9ca7b8',fontSize:19}},'Run a fresh scan before relying on this result.')])),e('div',{style:{display:'flex',justifyContent:'space-between',marginTop:'auto',fontSize:17,color:'#9ca7b8'}},e('div',null,`Confidence: ${compact(payload.confidence,20)||'unknown'}`),e('div',{style:{color:'#dbe1ec',fontWeight:800}},'canisharethis.com'))),{width:1200,height:630});
}

module.exports = { pageHtml, ogImageResponse };
