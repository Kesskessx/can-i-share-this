#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="homepage-declutter-v1"' in s: raise SystemExit('already applied')
css=r'''<style id="homepage-declutter-v1">
/* Compact homepage: one scanner, four balanced capability cards, no duplicate CTAs. */
#capability-strip,.capability-strip,.cist-capabilities,.unified-scanner-label,.scanner-proof,#scanner-proof,#cist-stats,.cist-stats,.trust-row,.signals-strip,.checks-available,.checks-panel{display:none!important}
#scan-form button[type="submit"]{font-size:0!important}#scan-form button[type="submit"]:after{content:'Analyze';font-size:16px}
.image-note{font-size:0!important}.image-note:after{content:'Private by design · No account required';font-size:11px}
.hero .eyebrow{display:none!important}
.footer-resource-links a[href="/safe-link-checker"],.footer-resource-links a[href="/google-drive-link-checker"],.footer-resource-links a[href="/dropbox-link-checker"],.footer-resource-links a[href="/scam-prevention"],.footer-resource-links a[href="/scan-examples"]{display:none!important}
.footer-resource-links i{display:none!important}.footer-resource-links{gap:10px!important}.footer-label{display:none!important}
a[href="/qr-code-link-checker"],.qr-cta,.qr-code-cta,.qr-scanner-cta{display:none!important}
@media(max-width:600px){
  .hero{padding-top:34px!important;padding-bottom:14px!important}
  .hero .sub{max-width:560px!important;margin:12px auto 18px!important;line-height:1.45!important}
  #image-safety-tools.image-tools{margin-top:12px!important;gap:10px!important}
  #image-safety-tools .image-tool{min-height:54px!important;border-radius:16px!important;font-size:14px!important;font-weight:750!important}
  .image-note{margin-top:5px!important;line-height:1.35!important}
  .image-analysis{margin-top:12px}
  .site-footer{margin-top:22px!important;padding-top:20px!important}
  .footer-resource-links{row-gap:8px!important}
}
</style>'''
js=r'''<script id="homepage-declutter-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function hideLeaf(el){if(!el)return;var control=el.closest&&el.closest('a,button');(control||el).style.display='none'}
var exact=['Link · Email · QR · Image · Crypto','One scanner · Type detection is automatic','One scanner. More signals.'];
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(exact.indexOf(t)>=0)hideLeaf(el)});
/* Hide duplicate trust pills and the obsolete standalone QR CTA, including icon-prefixed variants. */
document.querySelectorAll('a,button,span,div').forEach(function(el){var t=norm(el.textContent);if(t==='Scan a QR code'||t.endsWith(' Scan a QR code')||t==='Nothing you paste is saved'||t.endsWith(' Nothing you paste is saved')||t==='No account needed'||t.endsWith(' No account needed'))hideLeaf(el)});
/* Hide the old technical proof card if an earlier class name survives. */
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(t==='CHECKS AVAILABLE'){var x=el;while(x.parentElement&&norm(x.parentElement.textContent).indexOf('Google Web Risk')>=0&&norm(x.parentElement.textContent).length<700)x=x.parentElement;x.style.display='none'}});
/* Keep four What we check cards and turn the old copycat card into message/email safety. */
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('Copycat sites')===0&&t.indexOf('Look-alike website names')>0&&t.length<180){el.style.display='';var title=el.querySelector('strong,b,h3,h4');if(title)title.textContent='Suspicious messages';var nodes=el.querySelectorAll('span,p,small,div');for(var i=0;i<nodes.length;i++){if(norm(nodes[i].textContent)==='Look-alike website names')nodes[i].textContent='Scam emails and messages'}}});
/* Remove the long scanner disclaimer from the homepage; details remain on Security/Supported Checks. */
document.querySelectorAll('p,small,div').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('One complete check. Public links may be compared with external phishing')===0&&t.length<500)el.style.display='none'});
var sub=document.querySelector('.hero .sub');if(sub)sub.textContent='One scanner for suspicious links, emails, QR codes, images, files and crypto.';
var submit=document.querySelector('#scan-form button[type="submit"]');if(submit)submit.textContent='Analyze';
})();</script>'''
if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied compact homepage cleanup with four balanced checks')
