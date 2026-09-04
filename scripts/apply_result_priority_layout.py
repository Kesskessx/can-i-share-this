#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-result-priority-style">
body.cist-result-active #result{margin-top:14px}
body.cist-result-active .cist-after-result{margin-top:14px}
@media(max-width:600px){
  body.cist-result-active #result{margin-top:10px}
  body.cist-result-active .cist-after-result{margin-top:12px}
}
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

  var selectors=['.one-click-note','.check-strip','.under-form','#capability-strip','#scanner-proof'];
  var items=[];
  selectors.forEach(function(selector,index){
    var node=document.querySelector(selector);
    if(!node)return;
    var marker=document.createComment('cist-result-layout-'+index);
    node.parentNode.insertBefore(marker,node);
    items.push({node:node,marker:marker});
  });

  function moveBelowResult(){
    var anchor=result;
    items.forEach(function(item){
      item.node.classList.add('cist-after-result');
      anchor.insertAdjacentElement('afterend',item.node);
      anchor=item.node;
    });
  }

  function restoreOriginalLayout(){
    items.forEach(function(item){
      item.node.classList.remove('cist-after-result');
      if(item.marker.parentNode)item.marker.parentNode.insertBefore(item.node,item.marker.nextSibling);
    });
  }

  function sync(){
    var active=!result.classList.contains('hidden');
    document.body.classList.toggle('cist-result-active',active);
    if(active){
      moveBelowResult();
      requestAnimationFrame(function(){
        var top=form.getBoundingClientRect().top+window.scrollY-12;
        if(window.scrollY>top+160)window.scrollTo({top:Math.max(0,top),behavior:'smooth'});
      });
    }else{
      restoreOriginalLayout();
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

    import re
    source=re.sub(r'\s*<style id="cist-result-priority-style">.*?</style>', '', source, count=1, flags=re.S)
    source=re.sub(r'\s*<script id="cist-result-priority-script">.*?</script>', '', source, count=1, flags=re.S)

    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)

    required=[
        'id="scan-form"',
        'id="result"',
        'cist-result-active',
        "form.insertAdjacentElement('afterend',result)",
        "'.one-click-note'",
        "'.check-strip'",
        "'.under-form'",
        "'#capability-strip'",
        "'#scanner-proof'",
        'moveBelowResult()',
        'restoreOriginalLayout()'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Result priority guard failed: missing {token}')

    HOME.write_text(source,encoding='utf-8')
    print('Moved homepage guidance below results on desktop and mobile')

if __name__=='__main__':
    main()
