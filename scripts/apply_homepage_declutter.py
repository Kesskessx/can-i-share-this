#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="homepage-declutter-v1"' in s: raise SystemExit('already applied')
css=r'''<style id="homepage-declutter-v1">
/* Keep the scanner and hero intact; only hide known duplicate UI blocks. */
.capability-strip,.universal-scanner-note,.trust-row,.signals-strip,.checks-available,.checks-panel{display:none!important}
#scan-form button[type="submit"]{font-size:0!important}#scan-form button[type="submit"]:after{content:'Analyze';font-size:16px}
.image-note{font-size:0!important}.image-note:after{content:'Private by design · No account required';font-size:11px}
@media(max-width:600px){.hero p{max-width:520px;margin-left:auto;margin-right:auto}.image-tools{margin-top:10px}.image-analysis{margin-top:12px}}
</style>'''
js=r'''<script id="homepage-declutter-script">(function(){
/* Hide only the exact matching element. Never climb to parent containers. */
var duplicateTexts=['Link · Email · QR · Image · Crypto','One scanner · Type detection is automatic','One scanner. More signals.','Scan a QR code','Nothing you paste is saved','No account needed'];
document.querySelectorAll('body *').forEach(function(el){
  if(el.children.length)return;
  var t=(el.textContent||'').trim();
  if(duplicateTexts.indexOf(t)>=0)el.style.display='none';
});
var submit=document.querySelector('#scan-form button[type="submit"]');
if(submit)submit.textContent='Analyze';
})();</script>'''
if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Decluttered homepage without hiding scanner containers')
