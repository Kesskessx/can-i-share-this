from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'dist/index.html'
s=p.read_text()
style='''<style id="cist-unified-controller-style">
#scan-form #analyze::after{content:none!important;display:none!important}
#scan-form #analyze{font-size:14px!important}
body.cist-unified-controller #result,body.cist-unified-controller #cist-loading-halo{display:none!important}
#cist-unified-status{max-width:820px;margin:16px auto;color:var(--text);font-size:14px}
#cist-unified-status:empty{display:none}
#cist-unified-reset{margin-top:16px;padding:10px 16px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);cursor:pointer}
</style>'''
script=r'''<script id="cist-unified-controller-script">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),button=document.getElementById('analyze'),host=document.getElementById('cist-unified-home-scanner'),panel=document.getElementById('cist-mega-v2-panel');
  if(!form||!input||!button||!host||!panel)return;
  document.body.classList.add('cist-unified-controller');
  var status=document.createElement('div');status.id='cist-unified-status';status.setAttribute('role','status');host.insertAdjacentElement('afterend',status);
  var reset=document.createElement('button');reset.id='cist-unified-reset';reset.type='button';reset.textContent='Check another';panel.appendChild(reset);
  var busy=false;
  function label(){button.textContent=busy?'Analyzing…':'Analyze';button.disabled=busy}
  function clear(){panel.classList.remove('cist-show');status.textContent='';var old=document.getElementById('image-analysis');if(old)old.classList.add('hidden');window.cistMegaLastResult=null;
    ['cist-v4-coverage','cist-v4-reputation','cist-v4-advanced'].forEach(function(id){var el=document.getElementById(id);if(el)el.remove()});
  }
  label();input.addEventListener('input',function(){if(!busy)clear()});
  reset.addEventListener('click',function(){if(busy)return;clear();input.value='';input.dispatchEvent(new Event('input',{bubbles:true}));input.focus()});
  document.addEventListener('submit',function(e){
    if(e.target!==form)return;e.preventDefault();e.stopImmediatePropagation();
    if(busy)return;var value=input.value.trim();if(!value){clear();status.textContent='Paste content or upload a file to analyze.';input.focus();return}
    // Bare domains stay usable without rewriting messages or email addresses.
    if(/^(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+(?::\d+)?(?:\/\S*)?$/i.test(value))value='https://'+value;
    fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})}).catch(function(){});
  },true);
  var original=window.fetch.bind(window);
  window.fetch=async function(resource,options){
    var url;try{url=new URL(typeof resource==='string'?resource:resource.url,location.href)}catch(_){return original.apply(window,arguments)}
    if(url.origin!==location.origin||url.pathname!=='/api/analyze')return original.apply(window,arguments);
    if(busy)throw new Error('An analysis is already running.');
    busy=true;clear();status.textContent='Analyzing the available evidence…';label();
    var opts=Object.assign({},options||{}),controller=new AbortController(),timer=setTimeout(function(){controller.abort()},45000);
    var parentSignal=opts.signal,onAbort=function(){controller.abort()};if(parentSignal){if(parentSignal.aborted)controller.abort();else parentSignal.addEventListener('abort',onAbort,{once:true})}opts.signal=controller.signal;
    try{var response=await original(resource,opts);var data=await response.clone().json();
      if(!response.ok||data.error)throw new Error(response.status===429?'Analysis temporarily rate-limited. Please try again later.':data.error||'The analysis could not complete.');
      status.textContent='';return response;
    }catch(e){panel.classList.remove('cist-show');status.textContent=e.name==='AbortError'?'Analysis timed out. No safety conclusion is available.':e.message||'Analysis unavailable. No safety conclusion is available.';throw e}
    finally{clearTimeout(timer);if(parentSignal)parentSignal.removeEventListener('abort',onAbort);busy=false;label()}
  };
  document.addEventListener('cist:mega-result',function(e){if(!e.detail||e.detail.error)return;var old=document.getElementById('image-analysis');if(old)old.classList.add('hidden');setTimeout(label,0)});
})();
</script>'''
s=s.replace('</head>',style+'\n</head>',1).replace('</body>',script+'\n</body>',1)
p.write_text(s)
print('Unified text and upload result lifecycle')
