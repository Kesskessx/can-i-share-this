#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-single-complete-scan-style">
#deep,#consent{display:none!important}
body.cist-full-scan-running #result{opacity:.98}
body.cist-full-scan-running #actions{pointer-events:auto}
button:disabled{cursor:default!important}
</style>
'''

SCRIPT = r'''
<script id="cist-single-complete-scan">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),result=document.getElementById('result');
  var deepConfirm=document.getElementById('deep-confirm'),reputation=document.getElementById('reputation');
  var analyze=document.getElementById('analyze'),paste=document.getElementById('paste');
  if(!form||!input||!result||!deepConfirm)return;
  var startedFor='',watchdog=0;
  function value(){return String(input.value||'').trim()}
  function email(v){v=String(v||'').trim().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function crypto(v){v=String(v||'').trim();return /^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v)}
  function isPublicLink(v){return !!v&&!email(v)&&!crypto(v)&&(/^(https?:\/\/)/i.test(v)||/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(?:[\/:?#]|$)/i.test(v))}
  function stopWatchdog(){if(watchdog){clearTimeout(watchdog);watchdog=0}}
  function unlockUi(){
    document.body.classList.remove('cist-full-scan-running');
    document.documentElement.style.cursor='';document.body.style.cursor='';
    if(analyze){analyze.disabled=false;if(!/Check (link|email)/i.test(analyze.textContent||''))analyze.textContent=email(value())?'Check email':'Check link'}
    if(paste){paste.disabled=false;if(paste.textContent==='Pasting…')paste.textContent='Paste & check'}
  }
  function reset(){startedFor='';stopWatchdog();unlockUi()}
  form.addEventListener('submit',reset,true);
  input.addEventListener('input',reset);
  window.addEventListener('pageshow',unlockUi);
  document.addEventListener('visibilitychange',function(){if(!document.hidden)unlockUi()});
  document.addEventListener('cist:result-updated',function(){
    var v=value();
    if(!isPublicLink(v)||startedFor===v)return;
    startedFor=v;
    document.body.classList.add('cist-full-scan-running');
    if(reputation){reputation.className='reputation reputation-pending';reputation.innerHTML='<strong>Completing safety check…</strong><span>Checking known phishing and malware reports for this public link.</span>';reputation.classList.remove('hidden')}
    stopWatchdog();
    watchdog=setTimeout(function(){
      if(startedFor===v&&document.body.classList.contains('cist-full-scan-running')){
        unlockUi();
        if(reputation&&!reputation.classList.contains('reputation-alert')){
          reputation.className='reputation reputation-alert';
          reputation.innerHTML='<strong>Safety check timed out</strong><span>The external security check took too long. The page is responsive again; do not treat the incomplete result as a safety guarantee.</span>';
          reputation.classList.remove('hidden');
        }
      }
    },9000);
    setTimeout(function(){deepConfirm.click()},0);
  });
  if(reputation){
    new MutationObserver(function(){
      if(startedFor&&reputation.classList.contains('reputation-alert')){stopWatchdog();unlockUi()}
    }).observe(reputation,{attributes:true,attributeFilter:['class'],childList:true,subtree:true});
  }
  unlockUi();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=source.replace('Quick check first. The extra online reputation check runs only after you choose it and confirm that the public link may be shared.','One complete check. Public links may be compared with external phishing and malware databases. Links containing private access tokens are not shared externally.')
    source=source.replace('Run extra safety check','Safety check')
    source=source.replace('One more check recommended','Completing safety check')
    source=source.replace('The first check did not find anything obvious. One more security check is recommended before you open the link.','No obvious warning signs were found in the first stage. The complete safety check is still running.')
    source=source.replace('Before opening this link, run the extra safety check below. The quick check alone cannot confirm that a link is safe.','Wait for the complete result before deciding whether to open this link.')

    quick = "fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})})"
    quick_timed = "Promise.race([fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})}),new Promise(function(_,reject){setTimeout(function(){reject(new Error('scan-timeout'))},8000)})])"
    if quick in source:
        source=source.replace(quick,quick_timed,1)

    deep = "fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl,consent:true})})"
    deep_timed = "Promise.race([fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl,consent:true})}),new Promise(function(_,reject){setTimeout(function(){reject(new Error('deep-timeout'))},8000)})])"
    if deep in source:
        source=source.replace(deep,deep_timed,1)

    if 'id="cist-single-complete-scan-style"' not in source:
        source=source.replace('</head>',STYLE+'\n</head>',1)
    if 'id="cist-single-complete-scan"' not in source:
        source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['One complete check.','id="cist-single-complete-scan"','#deep,#consent{display:none!important}','deepConfirm.click()','Safety check timed out','scan-timeout','deep-timeout','pointer-events:auto','unlockUi()']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Single complete scan guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied single-button complete safety scan UX with click-state recovery')

if __name__=='__main__':
    main()
