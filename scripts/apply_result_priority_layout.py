#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-result-priority-style">
body.cist-result-active .one-click-note,
body.cist-result-active .check-strip,
body.cist-result-active .under-form,
body.cist-result-active #capability-strip,
body.cist-result-active #scanner-proof{display:none!important}
body.cist-result-active #result{margin-top:14px}
@media(max-width:600px){body.cist-result-active #result{margin-top:10px}}
</style>
'''

SCRIPT = r'''
<script id="cist-result-priority-script">
(function(){
  var form=document.getElementById('scan-form');
  var result=document.getElementById('result');
  if(!form||!result)return;

  /* Keep the verdict directly below the scanner on desktop and mobile. */
  form.insertAdjacentElement('afterend',result);

  function sync(){
    var active=!result.classList.contains('hidden');
    document.body.classList.toggle('cist-result-active',active);
    if(active){
      requestAnimationFrame(function(){
        var top=form.getBoundingClientRect().top+window.scrollY-12;
        if(window.scrollY>top+160)window.scrollTo({top:Math.max(0,top),behavior:'smooth'});
      });
    }
  }

  new MutationObserver(sync).observe(result,{attributes:true,attributeFilter:['class']});
  document.addEventListener('cist:result-updated',sync);
  var again=document.getElementById('again');
  if(again)again.addEventListener('click',function(){setTimeout(sync,0)});
  sync();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    if 'id="cist-result-priority-style"' not in source:
        source=source.replace('</head>',STYLE+'\n</head>',1)
    if 'id="cist-result-priority-script"' not in source:
        source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['id="scan-form"','id="result"','cist-result-active','form.insertAdjacentElement(\'afterend\',result)']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Result priority guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied result-priority layout for desktop and mobile')

if __name__=='__main__':
    main()
