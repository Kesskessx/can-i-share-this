#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="homepage-visual-hierarchy-v2"' in s:
    raise SystemExit('already applied')

css=r'''<style id="homepage-visual-hierarchy-v2">
/* Final homepage presentation pass: stronger scanner, quieter hero, clearer product language. */
.hero{padding-top:92px!important;padding-bottom:28px!important}
.hero h1{font-size:clamp(46px,5.25vw,70px)!important;line-height:1.04!important;letter-spacing:-.045em!important;max-width:850px!important;margin-left:auto!important;margin-right:auto!important}
.hero .sub{max-width:690px!important;margin:18px auto 28px!important;font-size:19px!important;line-height:1.45!important;color:color-mix(in srgb,var(--text) 67%,var(--muted))!important}
#scan-form{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;padding:8px!important;border:1px solid color-mix(in srgb,var(--accent) 24%,var(--line))!important;border-radius:20px!important;background:color-mix(in srgb,var(--card) 94%,var(--accent) 6%)!important;box-shadow:0 18px 55px rgba(0,0,0,.18),0 0 0 1px rgba(255,255,255,.015)!important;transition:border-color .18s ease,box-shadow .18s ease!important}
#scan-form:focus-within{border-color:color-mix(in srgb,var(--accent) 58%,var(--line))!important;box-shadow:0 18px 55px rgba(0,0,0,.22),0 0 0 3px color-mix(in srgb,var(--accent) 12%,transparent)!important}
#scan-form input,#scan-form textarea{min-height:54px!important}
#scan-form button[type="submit"]{min-height:54px!important;background:var(--accent)!important;color:#fff!important;border-color:transparent!important;box-shadow:0 8px 24px color-mix(in srgb,var(--accent) 22%,transparent)!important}
#scan-form button[type="submit"]:hover{filter:brightness(1.08)}
#image-safety-tools.image-tools{max-width:760px!important;margin-top:11px!important;display:flex!important;justify-content:center!important;gap:9px!important;flex-wrap:wrap!important}
#image-safety-tools .image-tool{flex:0 1 180px!important;min-height:40px!important;border-radius:12px!important;padding:9px 14px!important;font-size:12px!important;font-weight:760!important;background:transparent!important}
#image-safety-tools .image-note{flex-basis:100%!important;margin-top:1px!important;font-size:11px!important}
.cist-input-types-v2{max-width:760px;margin:9px auto 0;text-align:center;color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.015em}
.cist-input-types-v2 span{white-space:nowrap}.cist-input-types-v2 span:not(:last-child)::after{content:' · ';opacity:.6;margin:0 3px}
.cist-example-v2{max-width:760px;margin:26px auto 0;padding:18px 20px;border:1px solid var(--line);border-radius:18px;background:color-mix(in srgb,var(--card) 96%,var(--accent) 4%);text-align:left}
.cist-example-top{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:13px}
.cist-example-label{font-size:11px;color:var(--muted);font-weight:750;text-transform:uppercase;letter-spacing:.07em}.cist-example-score{font-size:13px;font-weight:800}.cist-example-score b{color:#62c58b}.cist-example-title{font-size:17px;font-weight:850}.cist-example-findings{display:grid;grid-template-columns:1fr 1fr;gap:8px 18px;margin-top:12px;color:var(--muted);font-size:12px;line-height:1.45}.cist-example-findings strong{color:var(--text);font-weight:800}.cist-example-findings .warn strong{color:#e8b45f}
.site-footer{margin-top:58px!important}.footer-resource-links{align-items:center!important}.footer-resource-links a{transition:color .15s ease}.footer-resource-links a:hover{color:var(--text)!important}
@media(max-width:600px){.hero{padding-top:48px!important;padding-bottom:20px!important}.hero h1{font-size:clamp(40px,12vw,54px)!important}.hero .sub{font-size:16px!important;margin:14px auto 22px!important}.cist-example-v2{margin-top:20px;padding:16px}.cist-example-findings{grid-template-columns:1fr}.cist-example-top{align-items:flex-start}.site-footer{margin-top:38px!important}}
</style>'''

js=r'''<script id="homepage-visual-hierarchy-v2-script">(function(){
function init(){
 var form=document.getElementById('scan-form'); if(!form)return;
 var sub=document.querySelector('.hero .sub'); if(sub)sub.textContent='Links, emails, QR codes, files and messages. One scanner. Multiple safety signals.';
 var tools=document.getElementById('image-safety-tools');
 if(tools){var up=document.getElementById('choose-image'),cam=document.getElementById('take-photo');if(up)up.textContent='Upload photo';if(cam)cam.textContent='Scan QR / Camera';}
 if(!document.querySelector('.cist-input-types-v2')){var types=document.createElement('div');types.className='cist-input-types-v2';types.setAttribute('aria-label','Supported input types');['URL','Email','Message','QR','Image','File','Crypto address'].forEach(function(x){var e=document.createElement('span');e.textContent=x;types.appendChild(e)});(tools||form).insertAdjacentElement('afterend',types)}
 var labels={'Fake websites':'Phishing & impersonation','Harmful files':'Malware & unsafe downloads','Link destination':'Redirects & final destination','Suspicious messages':'Scam & social-engineering signals'};
 document.querySelectorAll('strong,b,h3,h4').forEach(function(el){var k=(el.textContent||'').trim();if(labels[k]){var box=el.parentElement;if(box){var nodes=box.querySelectorAll('p,small,span,div');for(var i=0;i<nodes.length;i++){var t=(nodes[i].textContent||'').trim();if(t&&t!==k&&t.length<90){nodes[i].textContent=labels[k];break}}}}});
 if(!document.querySelector('.cist-example-v2')){var ex=document.createElement('section');ex.className='cist-example-v2';ex.setAttribute('aria-label','Example safety analysis');ex.innerHTML='<div class="cist-example-top"><div><div class="cist-example-label">Example analysis</div><div class="cist-example-title">Low risk</div></div><div class="cist-example-score"><b>82</b> / 100</div></div><div class="cist-example-findings"><div><strong>✓</strong> No malicious redirects detected</div><div><strong>✓</strong> Domain signals look normal</div><div><strong>✓</strong> No suspicious download detected</div><div class="warn"><strong>!</strong> Sender cannot be verified</div></div>';var anchor=document.querySelector('.site-footer,footer');if(anchor)anchor.parentNode.insertBefore(ex,anchor);else document.body.appendChild(ex)}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();</script>'''

if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied homepage visual hierarchy v2')
