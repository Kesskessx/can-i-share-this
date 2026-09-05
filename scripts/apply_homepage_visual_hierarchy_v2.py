#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="homepage-visual-hierarchy-v2"' in s:
    raise SystemExit('already applied')

css=r'''<style id="homepage-visual-hierarchy-v2">
.hero{padding-top:34px!important;padding-bottom:22px!important}
.hero h1{font-size:clamp(46px,5.1vw,68px)!important;line-height:1.04!important;letter-spacing:-.045em!important;max-width:850px!important;margin-left:auto!important;margin-right:auto!important}
.hero .sub{max-width:690px!important;margin:17px auto 25px!important;font-size:18px!important;line-height:1.45!important;color:color-mix(in srgb,var(--text) 70%,var(--muted))!important}
#scan-form{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;padding:8px!important;border:1px solid rgba(120,143,247,.72)!important;border-radius:20px!important;background:linear-gradient(180deg,rgba(23,27,38,.98),rgba(17,20,29,.98))!important;box-shadow:0 0 0 1px rgba(120,143,247,.12),0 0 24px rgba(120,143,247,.18),0 14px 40px rgba(0,0,0,.22)!important;transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease!important}
#scan-form:hover{border-color:rgba(132,153,255,.88)!important;box-shadow:0 0 0 1px rgba(120,143,247,.16),0 0 30px rgba(120,143,247,.24),0 16px 42px rgba(0,0,0,.24)!important}
#scan-form:focus-within{border-color:#8da1ff!important;box-shadow:0 0 0 3px rgba(120,143,247,.16),0 0 34px rgba(120,143,247,.32),0 18px 46px rgba(0,0,0,.26)!important}
#scan-form input,#scan-form textarea{min-height:54px!important;background:transparent!important}
#scan-form button[type="submit"]{min-height:54px!important;background:#788ff7!important;color:#fff!important;border-color:transparent!important;box-shadow:0 8px 24px rgba(120,143,247,.20)!important}
#scan-form button[type="submit"]:hover{filter:brightness(1.08)}
#image-safety-tools.image-tools{max-width:760px!important;margin-top:10px!important;display:flex!important;justify-content:center!important;gap:9px!important;flex-wrap:wrap!important}
#image-safety-tools .image-tool{flex:0 1 180px!important;min-height:40px!important;border-radius:12px!important;padding:9px 14px!important;font-size:12px!important;font-weight:760!important;background:transparent!important}
#image-safety-tools .image-note{flex-basis:100%!important;margin:1px 0 0!important;font-size:11px!important;line-height:1.35!important}
.cist-input-types-v2{max-width:760px;margin:7px auto 0;text-align:center;color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.015em}
.cist-input-types-v2 span{white-space:nowrap}.cist-input-types-v2 span:not(:last-child)::after{content:' · ';opacity:.6;margin:0 3px}
.hero [class*="check"],.hero [class*="capabil"]{box-sizing:border-box}
.cist-example-v2{display:none!important}
.site-footer{margin-top:34px!important}.footer-resource-links{align-items:center!important}.footer-resource-links a{transition:color .15s ease}.footer-resource-links a:hover{color:var(--text)!important}
@media(min-width:760px){.hero div:has(> div > strong:first-child){max-width:820px}}
@media(max-width:600px){.hero{padding-top:22px!important;padding-bottom:18px!important}.hero h1{font-size:clamp(38px,11.5vw,52px)!important}.hero .sub{font-size:16px!important;margin:14px auto 21px!important}#scan-form{border-radius:17px!important;box-shadow:0 0 0 1px rgba(120,143,247,.12),0 0 20px rgba(120,143,247,.16),0 12px 34px rgba(0,0,0,.22)!important}.site-footer{margin-top:30px!important}}
</style>'''

js=r'''<script id="homepage-visual-hierarchy-v2-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function init(){
 var form=document.getElementById('scan-form'); if(!form)return;
 var sub=document.querySelector('.hero .sub'); if(sub)sub.textContent='Links, emails, messages, social profiles, QR codes, images, files and crypto. One scanner.';
 var tools=document.getElementById('image-safety-tools');
 if(tools){var up=document.getElementById('choose-image'),cam=document.getElementById('take-photo');if(up)up.textContent='Upload photo';if(cam)cam.textContent='Scan QR / Camera';var note=tools.querySelector('.image-note');if(note)note.textContent='Private by design · No account required';}
 var privacy=[];document.querySelectorAll('p,small,div,span').forEach(function(el){var t=norm(el.textContent);if((t==='Private by design · No account required'||t==='Private by design · No account required · Images are not stored by Can I Share This?')&&el.children.length===0)privacy.push(el)});for(var pi=1;pi<privacy.length;pi++)privacy[pi].style.display='none';
 if(!document.querySelector('.cist-input-types-v2')){var types=document.createElement('div');types.className='cist-input-types-v2';types.setAttribute('aria-label','Supported input types');['🔗 URL','✉️ Email','💬 Message','👤 Social profile','📷 QR','🖼️ Image','📄 File','₿ Crypto address'].forEach(function(x){var e=document.createElement('span');e.textContent=x;types.appendChild(e)});(tools||form).insertAdjacentElement('afterend',types)}
 var labels={'Fake websites':'Phishing & impersonation','Harmful files':'Malware & unsafe downloads','Link destination':'Redirects & final destination','Suspicious messages':'Scam & social-engineering signals'};
 document.querySelectorAll('strong,b,h3,h4').forEach(function(el){var k=norm(el.textContent);if(labels[k]){var box=el.parentElement;if(box){var nodes=box.querySelectorAll('p,small,span,div');for(var i=0;i<nodes.length;i++){var t=norm(nodes[i].textContent);if(t&&t!==k&&t.length<90){nodes[i].textContent=labels[k];break}}}}});
 var example=document.querySelector('.cist-example-v2');if(example)example.remove();
 document.querySelectorAll('section,div').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('Example analysis')===0&&t.indexOf('No malicious redirects detected')>0&&t.length<500)el.remove()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();</script>'''

if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage HTML')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied compact header-to-hero spacing with blue scanner glow')
