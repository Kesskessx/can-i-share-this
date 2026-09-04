#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-simple-result-ui-style">
/* Keep the result focused on one verdict and a few useful facts. */
body.cist-full-scan-running #universal-summary,
body.cist-full-scan-running #risk-breakdown,
body.cist-full-scan-running #recommended-action,
body.cist-full-scan-running #why-verdict,
body.cist-full-scan-running #advice,
body.cist-full-scan-running #reputation,
body.cist-full-scan-running #technical{display:none!important}

body.cist-simple-result-final #risk-breakdown,
body.cist-simple-result-final #recommended-action,
body.cist-simple-result-final #why-verdict,
body.cist-simple-result-final #advice,
body.cist-simple-result-final #reputation{display:none!important}

body.cist-simple-result-final #universal-safety{display:none!important}
body.cist-simple-result-final .universal-summary{margin-top:16px}
body.cist-simple-result-final .universal-summary-heading{display:none}
body.cist-simple-result-final .universal-summary-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
body.cist-simple-result-final #technical{margin-top:16px}
body.cist-simple-result-final #actions{margin-top:16px}
body.cist-simple-result-final #actions #deep{display:none!important}

@media(max-width:700px){
  body.cist-simple-result-final .universal-summary-grid{grid-template-columns:1fr}
  body.cist-simple-result-final .universal-summary-item{padding:10px 11px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-simple-result-ui">
(function(){
  var input=document.getElementById('url'),result=document.getElementById('result'),card=document.getElementById('result-card');
  var reputation=document.getElementById('reputation'),universal=document.getElementById('universal-summary');
  var verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),technical=document.getElementById('technical');
  if(!input||!result||!card)return;

  function isEmail(){var v=String(input.value||'').trim().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function isCrypto(){var v=String(input.value||'').trim();return /^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v)}
  function publicLink(){return !isEmail()&&!isCrypto()&&!result.classList.contains('hidden')}

  function finalReputation(){
    if(!reputation)return false;
    return reputation.classList.contains('reputation-alert');
  }

  function syncFinalCopy(){
    if(!publicLink()||!finalReputation())return;
    var bad=reputation.classList.contains('bad')||card.classList.contains('status-high');
    var good=reputation.classList.contains('good')||card.classList.contains('reputation-checked-safe');
    if(bad){
      if(verdict)verdict.textContent='Dangerous link';
      if(summary)summary.textContent='A known security service reported this link as dangerous. Do not open it.';
    }else if(good){
      if(verdict)verdict.textContent='No known danger found';
      if(summary)summary.textContent='No known phishing or malware threat was reported for this link.';
    }
    document.body.classList.remove('cist-full-scan-running');
    document.body.classList.add('cist-simple-result-final');
    if(universal)universal.classList.remove('hidden');
    if(technical){technical.classList.remove('hidden');technical.open=false}
  }

  function reset(){document.body.classList.remove('cist-simple-result-final')}
  input.addEventListener('input',reset);
  var form=document.getElementById('scan-form');if(form)form.addEventListener('submit',reset,true);
  var again=document.getElementById('again');if(again)again.addEventListener('click',function(){setTimeout(reset,0)});

  if(reputation)new MutationObserver(syncFinalCopy).observe(reputation,{attributes:true,attributeFilter:['class'],childList:true,subtree:true});
  document.addEventListener('cist:result-updated',syncFinalCopy);
  syncFinalCopy();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    if 'id="cist-simple-result-ui-style"' not in source:
        source=source.replace('</head>',STYLE+'\n</head>',1)
    if 'id="cist-simple-result-ui"' not in source:
        source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['cist-simple-result-final','#universal-safety{display:none!important}','No known phishing or malware threat was reported for this link.','technical.open=false']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Simple result UI guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied simplified novice-friendly final result UI')

if __name__=='__main__':
    main()
