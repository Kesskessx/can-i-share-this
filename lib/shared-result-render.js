'use strict';

const React = require('react');

function esc(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function text(value, max = 220) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, max);
}

function verdictLabel(value) {
  if (value === 'high') return 'HIGH RISK';
  if (value === 'caution') return 'VERIFY FIRST';
  if (value === 'low') return 'NO MAJOR WARNING';
  return 'INCOMPLETE';
}

function description(payload) {
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 2).map((x) => x.title).filter(Boolean) : [];
  return [payload.headline, ...reasons].filter(Boolean).join(' · ').slice(0, 220);
}

function pageHtml(row) {
  const id = row.id;
  const payload = row.payload || {};
  const label = verdictLabel(payload.verdict);
  const desc = description(payload) || 'Privacy-filtered safety scan result from Can I Share This?';
  const canonical = `https://canisharethis.com/r/${id}`;
  const ogImage = `https://canisharethis.com/og/${id}`;
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const reasonsHtml = reasons.length
    ? reasons.map((r) => `<li><strong>${esc(r.title || 'Signal')}</strong><span>${esc(r.detail || '')}</span></li>`).join('')
    : '<li><strong>No additional signal</strong><span>The shared summary contains no extra warning detail.</span></li>';

  const safePayload = JSON.stringify({
    id,
    verdict: payload.verdict || 'unknown',
    headline: payload.headline || 'Can I Share This? scan result',
    confidence: payload.confidence || 'unknown',
    action: payload.action || 'Verify independently before acting.'
  }).replace(/</g, '\\u003c');

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(label)} — Can I Share This?</title>
<meta name="description" content="${esc(desc)}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Can I Share This?">
<meta property="og:title" content="${esc(label)} — Can I Share This?">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${ogImage}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(label)} safety scan result">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(label)} — Can I Share This?">
<meta name="twitter:description" content="${esc(desc)}">
<meta name="twitter:image" content="${ogImage}">
<meta name="theme-color" content="#0d0f14">
<style>
:root{color-scheme:dark;--bg:#0b0d12;--card:#141822;--text:#f5f7fb;--muted:#99a2b3;--line:#2a3140;--accent:#788ff7;--good:#61c99a;--warn:#f0b85b;--bad:#ff7770}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse 720px 420px at 50% 80px,rgba(120,143,247,.12),transparent 72%),var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}.wrap{width:min(760px,calc(100% - 28px));margin:0 auto;padding:28px 0 56px}.brand{display:inline-flex;gap:.22em;font-weight:900;letter-spacing:-.035em;text-decoration:none}.brand b{color:var(--accent)}.result{margin-top:42px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.015));box-shadow:0 22px 58px rgba(0,0,0,.24);overflow:hidden}.head{padding:26px;border-bottom:1px solid var(--line)}.kicker{color:var(--muted);font-size:11px;font-weight:900;letter-spacing:.09em;text-transform:uppercase}.verdict{margin:8px 0 0;font-size:clamp(36px,7vw,64px);line-height:.98;letter-spacing:-.05em}.result[data-risk="high"] .verdict{color:var(--bad)}.result[data-risk="caution"] .verdict{color:var(--warn)}.result[data-risk="low"] .verdict{color:var(--good)}.headline{margin:13px 0 0;color:var(--muted);font-size:17px;max-width:620px}.body{padding:22px 26px 26px}.meta{display:flex;gap:8px;flex-wrap:wrap}.pill{padding:6px 9px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.025);color:var(--muted);font-size:11px;font-weight:800}.reasons{display:grid;gap:9px;margin:18px 0 0;padding:0;list-style:none}.reasons li{padding:12px 13px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.02)}.reasons strong,.reasons span{display:block}.reasons strong{font-size:12px}.reasons span{margin-top:3px;color:var(--muted);font-size:11px}.action{margin-top:18px;padding:14px;border-left:3px solid var(--accent);background:rgba(120,143,247,.07);border-radius:10px;font-weight:750}.note{margin:14px 0 0;color:var(--muted);font-size:10px}.share{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}.btn{appearance:none;border:1px solid var(--line);border-radius:11px;background:#181d28;color:var(--text);padding:10px 13px;font:inherit;font-size:12px;font-weight:850;cursor:pointer;text-decoration:none}.btn.primary{background:var(--accent);border-color:var(--accent);color:white}.scanner{margin-top:22px;padding:22px;border:1px solid var(--line);border-radius:20px;background:var(--card)}.scanner h2{margin:0;font-size:22px;letter-spacing:-.035em}.scanner p{margin:7px 0 15px;color:var(--muted);font-size:12px}.scan-form{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}.scan-form input{min-width:0;height:50px;padding:0 13px;border:1px solid var(--line);border-radius:12px;background:#0e1118;color:var(--text);font:inherit;outline:none}.scan-form input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(120,143,247,.12)}.scan-form button{height:50px;padding:0 18px;border:0;border-radius:12px;background:var(--accent);color:white;font:inherit;font-weight:900;cursor:pointer}.fresh{display:none;margin-top:14px;padding:15px;border:1px solid var(--line);border-radius:14px;background:#10141c}.fresh.show{display:block}.fresh h3{margin:0;font-size:19px}.fresh p{margin:6px 0 0;color:var(--muted);font-size:12px}.fresh .fresh-share{margin-top:12px}.status{min-height:18px;margin-top:9px;color:var(--muted);font-size:11px}@media(max-width:620px){.wrap{padding-top:20px}.result{margin-top:28px}.head,.body,.scanner{padding:18px}.scan-form{grid-template-columns:1fr}.scan-form button{width:100%}.share .btn{flex:1;text-align:center}}
</style>
</head>
<body>
<main class="wrap">
<a class="brand" href="https://canisharethis.com/">Can I Share <b>This?</b></a>
<section class="result" data-risk="${esc(payload.verdict || 'unknown')}"><div class="head"><div class="kicker">Shared safety scan</div><h1 class="verdict">${esc(label)}</h1><p class="headline">${esc(payload.headline || 'Can I Share This? scan result')}</p></div><div class="body"><div class="meta"><span class="pill">Confidence: ${esc(payload.confidence || 'unknown')}</span><span class="pill">Privacy-filtered result</span></div><ul class="reasons">${reasonsHtml}</ul><div class="action">${esc(payload.action || 'Verify independently before acting.')}</div><p class="note">This shared result is a snapshot. Run a fresh scan before relying on it.</p><div class="share"><button id="share-current" class="btn primary" type="button">Share on X</button><a class="btn" href="https://canisharethis.com/">Open full scanner</a></div></div></section>
<section class="scanner" aria-labelledby="fresh-title"><h2 id="fresh-title">Check something suspicious</h2><p>Paste a link, message, email, social profile or crypto address. The new scan stays on this page.</p><form id="viral-scan-form" class="scan-form"><input id="viral-input" autocomplete="off" spellcheck="false" placeholder="Paste something suspicious…" required><button id="viral-analyze" type="submit">Analyze</button></form><div id="viral-status" class="status" role="status" aria-live="polite"></div><div id="viral-fresh" class="fresh"></div></section>
</main>
<script>
(function(){var SOURCE=${safePayload};var form=document.getElementById('viral-scan-form'),input=document.getElementById('viral-input'),button=document.getElementById('viral-analyze'),status=document.getElementById('viral-status'),fresh=document.getElementById('viral-fresh'),shareCurrent=document.getElementById('share-current'),latest=null;
function api(action,body){return fetch('/api/event?action='+encodeURIComponent(action),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:action==='viral-event'})}
function postEvent(event,resultId,parentResultId){try{api('viral-event',{event:event,resultId:resultId||null,parentResultId:parentResultId||null}).catch(function(){})}catch(_){}}
postEvent('result_view',SOURCE.id,null);
function xIntent(url,headline,verdict){var prefix=verdict==='high'?'Would you open this?':verdict==='caution'?'Would you trust this?':'I checked this before opening it.';var t=prefix+' '+String(headline||'Can I Share This? scan result');return'https://twitter.com/intent/tweet?text='+encodeURIComponent(t)+'&url='+encodeURIComponent(url)}
function openX(url,headline,verdict){window.open(xIntent(url,headline,verdict),'_blank','noopener,noreferrer')}
shareCurrent.addEventListener('click',function(){postEvent('share_x',SOURCE.id,null);openX(location.href,SOURCE.headline,SOURCE.verdict)});
function x(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function lbl(r){return r==='high'?'HIGH RISK':r==='caution'?'VERIFY FIRST':r==='low'?'NO MAJOR WARNING':'INCOMPLETE'}
form.addEventListener('submit',async function(e){e.preventDefault();var value=String(input.value||'').trim();if(!value)return;latest=null;fresh.classList.remove('show');fresh.innerHTML='';button.disabled=true;button.textContent='Analyzing…';status.textContent='Checking available evidence…';try{var response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})});var data=await response.json();if(!response.ok||data.error)throw new Error(data.error||'Analysis failed');latest=data;var s=data.shareSummary||{},risk=(data.megaScanner&&data.megaScanner.finalRisk)||s.verdict||'unknown',reasons=Array.isArray(s.reasons)?s.reasons.slice(0,3):[];fresh.innerHTML='<h3>'+x(lbl(risk))+'</h3><p>'+x(s.headline||data.summary||'Fresh scan completed.')+'</p>'+(reasons.length?'<ul class="reasons">'+reasons.map(function(r){return'<li><strong>'+x(r.title||'Signal')+'</strong><span>'+x(r.detail||'')+'</span></li>'}).join('')+'</ul>':'')+'<button id="share-fresh" class="btn primary fresh-share" type="button">Share this result on X</button>';fresh.classList.add('show');status.textContent='Fresh scan completed.';postEvent('new_scan',null,SOURCE.id);document.getElementById('share-fresh').addEventListener('click',async function(){if(!latest||!latest.shareSummary)return;var b=this,popup=window.open('about:blank','_blank');if(popup)try{popup.opener=null}catch(_){}b.disabled=true;b.textContent='Preparing…';try{var created=await api('share-result',{summary:latest.shareSummary,parentResultId:SOURCE.id}),out=await created.json();if(!created.ok||!out.url)throw new Error(out.error||'Share failed');postEvent('new_share',out.id,SOURCE.id);postEvent('share_x',out.id,SOURCE.id);var target=xIntent(out.url,latest.shareSummary.headline,latest.shareSummary.verdict);if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');b.textContent='Shared on X'}catch(err){if(popup)popup.close();b.disabled=false;b.textContent='Share this result on X';status.textContent='Could not prepare the shared result.'}})}catch(err){status.textContent=err&&err.message?err.message:'Analysis unavailable.'}finally{button.disabled=false;button.textContent='Analyze'}})})();
</script>
</body></html>`;
}

function palette(verdict) {
  if (verdict === 'high') return { accent: '#ff7770', soft: '#351d22' };
  if (verdict === 'caution') return { accent: '#f0b85b', soft: '#332819' };
  if (verdict === 'low') return { accent: '#61c99a', soft: '#173028' };
  return { accent: '#93a0b8', soft: '#202633' };
}

async function ogImageResponse(row) {
  const payload = row.payload || {};
  const verdict = payload.verdict || 'unknown';
  const colors = palette(verdict);
  const reasons = Array.isArray(payload.reasons) ? payload.reasons.slice(0, 3) : [];
  const { ImageResponse } = await import('@vercel/og');
  const e = React.createElement;
  const reasonNodes = reasons.map((reason, index) => e('div',{key:`r${index}`,style:{display:'flex',alignItems:'center',gap:16,padding:'12px 16px',border:'1px solid #2b3342',borderRadius:16,background:'#121722'}},e('div',{style:{width:12,height:12,borderRadius:999,background:colors.accent,flex:'0 0 auto'}}),e('div',{style:{display:'flex',flexDirection:'column',minWidth:0}},e('div',{style:{color:'#f4f7fb',fontSize:24,fontWeight:800}},text(reason&&reason.title,70)||'Signal'),e('div',{style:{color:'#9ca7b8',fontSize:17,marginTop:3}},text(reason&&reason.detail,120)))));
  return new ImageResponse(e('div',{style:{width:'100%',height:'100%',display:'flex',flexDirection:'column',padding:58,background:'radial-gradient(circle at 76% 16%, rgba(120,143,247,.22), transparent 34%), #0b0e14',color:'#f4f7fb',fontFamily:'sans-serif'}},e('div',{style:{display:'flex',alignItems:'center',justifyContent:'space-between'}},e('div',{style:{display:'flex',fontSize:30,fontWeight:900,letterSpacing:'-0.04em'}},'Can I Share ',e('span',{style:{color:'#7f93ff',marginLeft:5}},'This?')),e('div',{style:{fontSize:18,color:'#9ca7b8',border:'1px solid #2b3342',borderRadius:999,padding:'8px 14px'}},'Shared safety scan')),e('div',{style:{marginTop:48,display:'flex',flexDirection:'column'}},e('div',{style:{display:'flex',alignSelf:'flex-start',color:colors.accent,background:colors.soft,border:`1px solid ${colors.accent}`,borderRadius:999,padding:'8px 14px',fontSize:20,fontWeight:900,letterSpacing:'0.06em'}},verdictLabel(verdict)),e('div',{style:{marginTop:18,fontSize:54,lineHeight:1.04,letterSpacing:'-0.045em',fontWeight:900,maxWidth:1010}},text(payload.headline,170)||'Can I Share This? scan result')),e('div',{style:{marginTop:30,display:'flex',flexDirection:'column',gap:10}},...(reasonNodes.length?reasonNodes:[e('div',{key:'none',style:{padding:'14px 16px',border:'1px solid #2b3342',borderRadius:16,background:'#121722',color:'#9ca7b8',fontSize:20}},'Run a fresh scan before relying on this shared result.')])),e('div',{style:{marginTop:'auto',display:'flex',alignItems:'center',justifyContent:'space-between',color:'#9ca7b8',fontSize:18}},e('div',null,`Confidence: ${text(payload.confidence,20)||'unknown'}`),e('div',{style:{color:'#d9deea',fontWeight:800}},'canisharethis.com'))),{width:1200,height:630});
}

module.exports = { pageHtml, ogImageResponse };
