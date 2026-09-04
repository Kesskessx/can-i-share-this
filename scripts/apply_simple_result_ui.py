#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-simple-result-ui-style">
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
body.cist-simple-result-final .universal-summary{margin-top:14px}
body.cist-simple-result-final .universal-summary-heading{display:none}
body.cist-simple-result-final .universal-summary-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
body.cist-simple-result-final #technical{margin-top:14px}
body.cist-simple-result-final #actions{margin-top:14px}
body.cist-simple-result-final #actions #deep{display:none!important}
body.cist-simple-result-final #signals li:nth-child(n+4){display:none!important}
@media(max-width:700px){body.cist-simple-result-final .universal-summary-grid{grid-template-columns:1fr}body.cist-simple-result-final .universal-summary-item{padding:10px 11px}}
</style>
'''

SCRIPT = r'''
<script id="cist-simple-result-ui">
(function(){
  var input=document.getElementById('url'),result=document.getElementById('result'),card=document.getElementById('result-card');
  var reputation=document.getElementById('reputation'),universal=document.getElementById('universal-summary');
  var verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),technical=document.getElementById('technical');
  if(!input||!result||!card)return;
  var finalizedFor='';
  function value(){return String(input.value||'').trim()}
  function isEmail(){var v=value().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function isCrypto(){var v=value();return /^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v)}
  function isMessage(){var v=value();return !isEmail()&&!isCrypto()&&!/^https?:\/\//i.test(v)&&(/\s/.test(v)||v.length>180)}
  function isLink(){return !isEmail()&&!isCrypto()&&!isMessage()&&!result.classList.contains('hidden')}
  function finalReputation(){return Boolean(reputation&&reputation.classList.contains('reputation-alert'))}
  function status(){if(card.classList.contains('status-high'))return'high';if(card.classList.contains('status-caution'))return'caution';if(card.classList.contains('status-low'))return'low';return'unknown'}
  function applyCopy(){
    var s=status(),kind=isEmail()?'email':isCrypto()?'crypto':isMessage()?'message':'link';
    if(verdict)verdict.textContent=s==='high'?'Dangerous':s==='caution'?'Caution':s==='low'?'Low risk':'Incomplete';
    if(!summary)return;
    if(s==='high')summary.textContent=kind==='message'?'Strong scam or phishing warning signs were found in this message.':kind==='email'?'High-risk warning signs were found for this email address or domain.':kind==='crypto'?'This crypto address failed or triggered high-risk checks.':'Known or strong danger signals were found for this link.';
    else if(s==='caution')summary.textContent=kind==='message'?'This message contains signs that should be verified before you act.':kind==='email'?'This sender or domain needs verification before you trust it.':kind==='crypto'?'The address format may be valid, but trust and ownership are not verified.':'This link has characteristics that deserve verification.';
    else if(s==='low')summary.textContent=kind==='message'?'No obvious scam pattern was found in the checks performed.':kind==='email'?'No obvious address-level warning signs were found.':kind==='crypto'?'No structural problem was found, but ownership is not verified.':'No known phishing or malware threat was found in the checks performed.';
    else summary.textContent='The check could not be completed with enough confidence.';
  }
  function simplify(){
    if(result.classList.contains('hidden'))return;
    var current=value();
    var link=isLink(),ready=!link||finalReputation()||card.classList.contains('status-high');if(!ready)return;
    if(finalizedFor===current&&document.body.classList.contains('cist-simple-result-final')){applyCopy();return}
    finalizedFor=current;applyCopy();
    document.body.classList.remove('cist-full-scan-running');document.body.classList.add('cist-simple-result-final');
    if(universal)universal.classList.remove('hidden');if(technical){technical.classList.remove('hidden');technical.open=false}
  }
  function reset(){finalizedFor='';document.body.classList.remove('cist-simple-result-final')}
  input.addEventListener('input',reset);var form=document.getElementById('scan-form');if(form)form.addEventListener('submit',reset,true);var again=document.getElementById('again');if(again)again.addEventListener('click',function(){setTimeout(reset,0)});
  if(reputation)new MutationObserver(function(){if(finalReputation())simplify()}).observe(reputation,{attributes:true,attributeFilter:['class']});
  document.addEventListener('cist:result-updated',simplify);simplify();
})();
</script>
'''

def main():
    if not HOME.is_file(): raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    import re
    source=re.sub(r'\s*<style id="cist-simple-result-ui-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-simple-result-ui">.*?</script>','',source,count=1,flags=re.S)
    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['cist-simple-result-final','Low risk','Strong scam or phishing warning signs','attributeFilter:[\'class\']','isMessage()']
    forbidden=['childList:true,subtree:true']
    for token in required:
        if token not in source: raise RuntimeError(f'Simple result UI guard failed: missing {token}')
    for token in forbidden:
        if token in source: raise RuntimeError(f'Simple result UI guard failed: forbidden {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied three-level concise result UI')

if __name__=='__main__': main()
