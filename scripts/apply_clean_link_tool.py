#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="clean-link-tool-style"' in s:
    raise SystemExit('clean link tool already applied')

css=r'''<style id="clean-link-tool-style">
.clean-link-tool{max-width:760px;margin:10px auto 0;padding:12px 14px;border:1px solid rgba(120,143,247,.24);border-radius:14px;background:rgba(120,143,247,.055);display:none;align-items:center;justify-content:space-between;gap:12px;text-align:left}.clean-link-tool.show{display:flex}.clean-link-copy{appearance:none;border:1px solid rgba(120,143,247,.44);background:rgba(120,143,247,.12);color:var(--text);border-radius:10px;padding:8px 11px;font:inherit;font-size:12px;font-weight:800;cursor:pointer;white-space:nowrap}.clean-link-copy:hover{background:rgba(120,143,247,.18)}.clean-link-text{min-width:0}.clean-link-title{font-size:12px;font-weight:850;color:var(--text)}.clean-link-meta{margin-top:3px;font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.clean-link-removed{color:#9fb0ff;font-weight:800}@media(max-width:600px){.clean-link-tool{margin-top:8px;padding:11px 12px;align-items:flex-start}.clean-link-copy{padding:8px 10px}.clean-link-meta{white-space:normal;overflow:visible}}
</style>'''

js=r'''<script id="clean-link-tool-script">(function(){
var TRACKING_KEYS=['fbclid','gclid','dclid','msclkid','igshid','mc_cid','mc_eid','vero_conv','vero_id','yclid','_ga','_gl','ref','ref_src','ref_url','spm','si'];
function isTracking(k){var x=String(k||'').toLowerCase();return x.indexOf('utm_')===0||TRACKING_KEYS.indexOf(x)>=0||x.indexOf('pk_')===0||x.indexOf('mtm_')===0}
function clean(raw){try{var u=new URL(raw);if(!/^https?:$/.test(u.protocol))return null;var removed=[];Array.from(u.searchParams.keys()).forEach(function(k){if(isTracking(k)){removed.push(k);u.searchParams.delete(k)}});if(!removed.length)return null;return {url:u.toString(),removed:removed}}catch(e){return null}}
function copyText(v,btn){var done=function(){var old=btn.textContent;btn.textContent='Copied';setTimeout(function(){btn.textContent=old},1200)};if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(v).then(done).catch(function(){fallback(v);done()})}else{fallback(v);done()}}
function fallback(v){var t=document.createElement('textarea');t.value=v;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();try{document.execCommand('copy')}catch(e){}t.remove()}
function init(){var input=document.getElementById('url'),form=document.getElementById('scan-form');if(!input||!form)return;var box=document.createElement('div');box.className='clean-link-tool';box.setAttribute('aria-live','polite');box.innerHTML='<div class="clean-link-text"><div class="clean-link-title">Cleaner link available</div><div class="clean-link-meta"></div></div><button class="clean-link-copy" type="button">Copy clean link</button>';
 var anchor=document.querySelector('.cist-input-types-v2')||document.getElementById('image-safety-tools')||form;anchor.insertAdjacentElement('afterend',box);var meta=box.querySelector('.clean-link-meta'),btn=box.querySelector('.clean-link-copy'),current='';
 function update(){var out=clean((input.value||'').trim());if(!out){box.classList.remove('show');current='';return}current=out.url;meta.innerHTML='<span class="clean-link-removed">'+out.removed.length+' tracking parameter'+(out.removed.length>1?'s':'')+' removed</span> · '+out.url.replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]});box.classList.add('show')}
 input.addEventListener('input',update);input.addEventListener('change',update);btn.addEventListener('click',function(){if(current)copyText(current,btn)});update()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();</script>'''

if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Added one-click clean link utility')
