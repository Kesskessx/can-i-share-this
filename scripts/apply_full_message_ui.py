#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'dist'/'index.html'
if not HOME.is_file(): raise RuntimeError('Homepage not found')
s=HOME.read_text(encoding='utf-8')
if 'id="cist-full-message-ui"' in s: raise SystemExit('already applied')

css=r'''<style id="cist-full-message-style">
#url{white-space:nowrap}
body.cist-message-result #actions #deep{display:none!important}
body.cist-message-result #reputation{display:none!important}
</style>'''
js=r'''<script id="cist-full-message-ui">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),result=document.getElementById('result'),card=document.getElementById('result-card');
  var icon=document.getElementById('status-icon'),verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),signals=document.getElementById('signals'),advice=document.getElementById('advice'),adviceText=document.getElementById('advice-text'),actions=document.getElementById('actions'),technical=document.getElementById('technical'),techGrid=document.getElementById('tech-grid'),analyze=document.getElementById('analyze');
  if(!form||!input||!result||!card)return;
  input.placeholder='Paste a link, email, message or crypto address…';
  input.setAttribute('aria-label','Paste a link, email, message or crypto address to analyze');
  function isEmail(v){return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)}
  function isCrypto(v){return /^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|ltc1[ac-hj-np-z02-9]{20,90}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v)}
  function isMessage(v){return v&&!/^https?:\/\//i.test(v)&&!isEmail(v)&&!isCrypto(v)&&(/\s/.test(v)||v.length>180)}
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function loading(){document.body.classList.remove('cist-simple-result-final');document.body.classList.add('cist-message-result');result.classList.remove('hidden');card.className='result-card';if(icon)icon.textContent='…';if(verdict)verdict.textContent='Analyzing…';if(summary)summary.textContent='Checking the message, extracted destinations and manipulation signals.';if(signals){signals.innerHTML='';signals.classList.add('hidden')}if(advice)advice.classList.add('hidden');if(technical)technical.classList.add('hidden');if(analyze){analyze.disabled=true;analyze.textContent='Analyzing…'}}
  function render(d){var s=d&&d.safety?d.safety:{},status=['low','caution','high'].indexOf(s.status)>=0?s.status:'unknown';card.className='result-card status-'+status;if(icon)icon.textContent=status==='low'?'✓':status==='caution'?'!':status==='high'?'×':'?';if(verdict)verdict.textContent=status==='low'?'Low risk':status==='caution'?'Caution':status==='high'?'Dangerous':'Incomplete';if(summary)summary.textContent=d.summary||(status==='low'?'No obvious scam pattern was found in the checks performed.':status==='caution'?'This message contains signs that should be verified before acting.':status==='high'?'Strong scam or phishing warning signs were found.':'The message could not be fully assessed.');var list=Array.isArray(s.signals)?s.signals.slice(0,3):[];if(signals){signals.innerHTML=list.map(function(x){return '<li>'+esc(x.title||x.detail||'Warning sign detected')+'</li>'}).join('');signals.classList.toggle('hidden',!list.length)}if(advice&&adviceText){adviceText.textContent=d.recommendedAction||(status==='high'?'Do not follow the request. Verify the sender through an official channel.':'Verify the sender independently before continuing.');advice.classList.remove('hidden')}if(actions)actions.classList.remove('hidden');if(technical&&techGrid){var m=d.message||{},parts=[];if((m.urls||[]).length)parts.push('<div class="tech"><span>URL detected</span><strong>'+esc(m.urls[0])+'</strong></div>');if((m.emails||[]).length)parts.push('<div class="tech"><span>Email detected</span><strong>'+esc(m.emails[0])+'</strong></div>');if((m.phones||[]).length)parts.push('<div class="tech"><span>Phone detected</span><strong>'+esc(m.phones[0])+'</strong></div>');if((m.claimedBrands||[]).length)parts.push('<div class="tech"><span>Claimed brand</span><strong>'+esc(m.claimedBrands[0])+'</strong></div>');if(parts.length){techGrid.innerHTML=parts.join('');technical.classList.remove('hidden');technical.open=false}}document.dispatchEvent(new CustomEvent('cist:result-updated'));}
  form.addEventListener('submit',async function(e){var raw=String(input.value||'').trim();if(!isMessage(raw))return;e.preventDefault();e.stopImmediatePropagation();loading();try{var controller=new AbortController(),timer=setTimeout(function(){controller.abort()},18000);var r=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:raw}),signal:controller.signal});clearTimeout(timer);var d=await r.json();if(!r.ok)throw new Error(d&&d.error?d.error:'Message check failed');render(d)}catch(err){render({summary:err&&err.name==='AbortError'?'Message analysis timed out.':'Message analysis could not complete.',recommendedAction:'Verify the sender independently before acting.',safety:{status:'unknown',signals:[]}})}finally{if(analyze){analyze.disabled=false;analyze.textContent='Analyze'}}},true);
  input.addEventListener('input',function(){document.body.classList.remove('cist-message-result')});
})();
</script>'''
if '</head>' not in s or '</body>' not in s: raise RuntimeError('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
HOME.write_text(s,encoding='utf-8')
print('Enabled full-message analysis UI')
