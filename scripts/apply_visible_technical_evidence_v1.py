#!/usr/bin/env python3
from pathlib import Path

HOME = Path(__file__).resolve().parents[1] / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-visible-technical-evidence-v1-style">
body.cist-visible-tech-result #technical{display:block!important}
body.cist-visible-tech-result #technical>summary{display:none!important}
body.cist-visible-tech-result #technical>.technical-help{margin-top:0}
body.cist-visible-tech-result #cist-advanced-tech-v2{display:block!important}
</style>
'''

SCRIPT = r'''
<script id="cist-visible-technical-evidence-v1-script">
(function(){
  var result=document.getElementById('result'), technical=document.getElementById('technical'), card=document.getElementById('result-card');
  if(!result||!technical)return;
  function sync(){
    var visible=!result.classList.contains('hidden');
    document.body.classList.toggle('cist-visible-tech-result',visible);
    if(visible){
      technical.open=true;
      technical.setAttribute('open','');
      var summary=technical.querySelector('summary');
      if(summary)summary.setAttribute('aria-hidden','true');
    }else{
      document.body.classList.remove('cist-visible-tech-result');
    }
  }
  document.addEventListener('cist:mega-result',function(){setTimeout(sync,0)});
  document.addEventListener('cist:result-updated',function(){setTimeout(sync,0)});
  var reset=document.getElementById('cist-unified-reset');
  if(reset)reset.addEventListener('click',function(){document.body.classList.remove('cist-visible-tech-result')});
  if(card)new MutationObserver(function(){setTimeout(sync,0)}).observe(card,{attributes:true,attributeFilter:['class']});
  new MutationObserver(function(){setTimeout(sync,0)}).observe(result,{attributes:true,attributeFilter:['class']});
  sync();
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s=HOME.read_text(encoding='utf-8')
if 'id="technical"' not in s or 'cist-advanced-tech-v2' not in s:
    raise RuntimeError('Technical evidence UI not found')
s=s.replace('</head>',STYLE+'\n</head>',1)
s=s.replace('</body>',SCRIPT+'\n</body>',1)
for token in ['cist-visible-tech-result','technical.open=true','cist-visible-technical-evidence-v1-script']:
    if token not in s:
        raise RuntimeError('Visible technical evidence guard failed: '+token)
HOME.write_text(s,encoding='utf-8')
print('Technical evidence is visible directly in result')
