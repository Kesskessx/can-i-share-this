#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'
html = HOME.read_text(encoding='utf-8')

if 'id="analyze-loading-halo-style"' in html:
    raise SystemExit('analyze loading halo already applied')

css = r'''
<style id="analyze-loading-halo-style">
@keyframes cistAnalyzeHaloPulse {
  0%,100% {
    box-shadow:
      0 0 0 0 rgba(120,143,247,.18),
      0 0 18px rgba(120,143,247,.24),
      0 8px 24px rgba(120,143,247,.18);
  }
  50% {
    box-shadow:
      0 0 0 7px rgba(120,143,247,.08),
      0 0 34px rgba(120,143,247,.48),
      0 10px 30px rgba(120,143,247,.28);
  }
}

#analyze.cist-analyzing {
  opacity:.98!important;
  cursor:progress!important;
  filter:none!important;
  animation:cistAnalyzeHaloPulse 1.15s ease-in-out infinite!important;
  will-change:box-shadow;
}

@media(prefers-reduced-motion:reduce){
  #analyze.cist-analyzing {
    animation:none!important;
    box-shadow:
      0 0 0 3px rgba(120,143,247,.14),
      0 0 24px rgba(120,143,247,.34),
      0 8px 24px rgba(120,143,247,.18)!important;
  }
}
</style>
'''

script = r'''
<script id="analyze-loading-halo-script">
(function(){
  var form=document.getElementById('scan-form');
  var analyze=document.getElementById('analyze');
  var input=document.getElementById('url');
  if(!form||!analyze)return;

  var startedAt=0;
  var fallbackTimer=0;
  var minimumVisibleMs=650;

  function clearFallback(){
    if(fallbackTimer){clearTimeout(fallbackTimer);fallbackTimer=0;}
  }

  function startHalo(){
    clearFallback();
    startedAt=Date.now();
    analyze.classList.add('cist-analyzing');
    analyze.setAttribute('aria-busy','true');
    fallbackTimer=setTimeout(stopHalo,12000);
  }

  function stopHalo(){
    clearFallback();
    analyze.classList.remove('cist-analyzing');
    analyze.removeAttribute('aria-busy');
    startedAt=0;
  }

  function stopHaloAfterMinimum(){
    if(!startedAt){stopHalo();return;}
    var remaining=minimumVisibleMs-(Date.now()-startedAt);
    if(remaining>0){setTimeout(stopHalo,remaining);}
    else stopHalo();
  }

  form.addEventListener('submit',function(){
    startHalo();
  },true);

  document.addEventListener('cist:result-updated',stopHaloAfterMinimum);
  if(input)input.addEventListener('input',stopHalo);
  window.addEventListener('pageshow',stopHalo);
})();
</script>
'''

if '</head>' not in html or '</body>' not in html:
    raise SystemExit('missing document boundary')

html = html.replace('</head>', css + '\n</head>', 1)
html = html.replace('</body>', script + '\n</body>', 1)

required = [
    'id="analyze-loading-halo-style"',
    'id="analyze-loading-halo-script"',
    '#analyze.cist-analyzing',
    "analyze.classList.add('cist-analyzing')",
    "document.addEventListener('cist:result-updated',stopHaloAfterMinimum)",
    'minimumVisibleMs=650',
]
for token in required:
    if token not in html:
        raise RuntimeError(f'Analyze halo guard failed: missing {token}')

HOME.write_text(html, encoding='utf-8')
print('Applied reliable blue loading halo to Analyze button')
