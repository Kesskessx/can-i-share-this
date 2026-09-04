#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="homepage-declutter-v1"' in s: raise SystemExit('already applied')
css=r'''<style id="homepage-declutter-v1">
/* Final mobile cleanup: keep the scanner, one privacy line and one compact explanation. */
#capability-strip,.capability-strip,.cist-capabilities,.unified-scanner-label,.scanner-proof,#scanner-proof,#cist-stats,.cist-stats,.trust-row,.signals-strip,.checks-available,.checks-panel{display:none!important}
#scan-form button[type="submit"]{font-size:0!important}#scan-form button[type="submit"]:after{content:'Analyze';font-size:16px}
.image-note{font-size:0!important}.image-note:after{content:'Private by design · No account required';font-size:11px}
.hero .eyebrow{display:none!important}
.footer-resource-links a[href="/safe-link-checker"],.footer-resource-links a[href="/google-drive-link-checker"],.footer-resource-links a[href="/dropbox-link-checker"],.footer-resource-links a[href="/scam-prevention"],.footer-resource-links a[href="/scan-examples"]{display:none!important}
.footer-resource-links i{display:none!important}.footer-resource-links{gap:10px!important}.footer-label{display:none!important}
@media(max-width:600px){.hero{padding-top:34px!important}.hero .sub{max-width:560px!important;margin:12px auto 18px!important;line-height:1.45!important}.image-tools{margin-top:10px}.image-analysis{margin-top:12px}.site-footer{margin-top:22px!important}}
</style>'''
js=r'''<script id="homepage-declutter-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function hideSelfOrSameTextParent(el){if(!el)return;var t=norm(el.textContent),x=el;while(x.parentElement&&norm(x.parentElement.textContent)===t&&x.parentElement!==document.body)x=x.parentElement;x.style.display='none'}
var exact=['Link · Email · QR · Image · Crypto','One scanner · Type detection is automatic','One scanner. More signals.','Scan a QR code','Nothing you paste is saved','No account needed'];
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(exact.indexOf(t)>=0)hideSelfOrSameTextParent(el)});
/* Hide the old technical proof card if an earlier class name survives. */
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(t==='CHECKS AVAILABLE'){var x=el;while(x.parentElement&&norm(x.parentElement.textContent).indexOf('Google Web Risk')>=0&&norm(x.parentElement.textContent).length<700)x=x.parentElement;x.style.display='none'}});
/* Hide duplicate privacy pills and the separate QR CTA as complete controls, not only their inner text. */
document.querySelectorAll('a,button,span,div').forEach(function(el){var t=norm(el.textContent);if(t==='Scan a QR code'||t==='Nothing you paste is saved'||t==='No account needed')hideSelfOrSameTextParent(el)});
/* Reduce What we check from four cards to three by removing the redundant copycat card. */
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('Copycat sites')===0&&t.indexOf('Look-alike website names')>0&&t.length<180)el.style.display='none'});
/* Remove the long scanner disclaimer from the homepage; details remain on Security/Supported Checks. */
document.querySelectorAll('p,small,div').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('One complete check. Public links may be compared with external phishing')===0&&t.length<500)el.style.display='none'});
var sub=document.querySelector('.hero .sub');if(sub)sub.textContent='One scanner for suspicious links, emails, QR codes, images, files and crypto.';
var submit=document.querySelector('#scan-form button[type="submit"]');if(submit)submit.textContent='Analyze';
})();</script>'''
if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied final compact homepage cleanup')
