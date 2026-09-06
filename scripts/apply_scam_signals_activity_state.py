#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-scam-signals-activity-style">
#cist-scam-signals-rail .cist-signal-activity{
  display:block!important;
  margin-top:7px!important;
  color:var(--muted,#9ba6ba)!important;
  font-size:9px!important;
  font-weight:700!important;
  line-height:1.35!important;
}
#cist-scam-signals-rail .cist-signal-zero-note{
  display:block!important;
  margin-top:3px!important;
  color:var(--muted,#9ba6ba)!important;
  font-size:8.5px!important;
  line-height:1.35!important;
}
</style>
'''

SCRIPT = r'''
<script id="cist-scam-signals-activity-script">
(function(){
  var rail=document.getElementById('cist-scam-signals-rail');
  if(!rail)return;
  var primary=rail.querySelector('.cist-signal-primary');
  var label=rail.querySelector('.cist-signal-primary-label');
  var total=document.getElementById('cist-signal-total');
  if(!primary||!label||!total)return;

  var activity=document.getElementById('cist-signal-activity');
  if(!activity){activity=document.createElement('span');activity.id='cist-signal-activity';activity.className='cist-signal-activity';primary.appendChild(activity)}
  var zero=document.getElementById('cist-signal-zero-note');
  if(!zero){zero=document.createElement('span');zero.id='cist-signal-zero-note';zero.className='cist-signal-zero-note';primary.appendChild(zero)}

  function render(data){
    var d=data&&data.daily||{};
    var scans=Number(d.total||0),signals=Number(d.signalTotal||0);
    activity.textContent=scans.toLocaleString()+' scan'+(scans===1?'':'s')+' analyzed today';
    label.textContent=signals===0?'No scam signals detected yet':'Signals detected today';
    zero.textContent=signals===0&&scans>0?'The counter is active — today’s scans have not triggered these warning categories.':'';
  }
  function refresh(){
    fetch('/api/counter',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('activity');return r.json()}).then(render).catch(function(){activity.textContent='Activity unavailable';zero.textContent=''})
  }
  document.addEventListener('cist:result-updated',function(){setTimeout(refresh,450)});
  document.addEventListener('visibilitychange',function(){if(!document.hidden)refresh()});
  window.addEventListener('focus',refresh);
  setInterval(function(){if(!document.hidden)refresh()},15000);
  refresh();
})();
</script>
'''

def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    if 'id="cist-scam-signals-rail"' not in source:
        raise RuntimeError('Scam signals rail not found')
    source=re.sub(r'\s*<style id="cist-scam-signals-activity-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-scam-signals-activity-script">.*?</script>','',source,count=1,flags=re.S)
    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    for token in ['No scam signals detected yet','cist-signal-activity','Activity unavailable','/api/counter']:
        if token not in source:
            raise RuntimeError(f'Scam activity guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied explicit scam signals activity state')

if __name__=='__main__':
    main()
