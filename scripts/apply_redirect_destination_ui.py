#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-redirect-destination-style">
.cist-destination-hint{max-width:760px;margin:9px auto 0;text-align:center;font-size:12px;color:var(--muted);font-weight:650}
.cist-destination{margin-top:14px;border:1px solid var(--line);border-radius:16px;padding:15px 16px;background:color-mix(in srgb,var(--card) 94%,transparent);text-align:left}
.cist-destination-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.cist-destination-title{margin:0;font-size:15px;font-weight:850;letter-spacing:-.015em;color:var(--text)}
.cist-destination-state{font-size:11px;font-weight:850;border-radius:999px;padding:5px 8px;background:var(--soft);white-space:nowrap}
.cist-destination.direct .cist-destination-state{color:var(--green)}
.cist-destination.redirected .cist-destination-state{color:var(--amber)}
.cist-destination.suspicious{border-color:color-mix(in srgb,var(--red) 42%,var(--line))}
.cist-destination.suspicious .cist-destination-state{color:var(--red)}
.cist-destination-chain{margin-top:12px;display:grid;gap:5px}
.cist-destination-hop{display:flex;align-items:center;gap:8px;min-width:0}
.cist-destination-arrow{color:var(--muted);font-size:12px;flex:0 0 auto}
.cist-destination-host{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cist-destination-final{margin-top:11px;padding-top:11px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);word-break:break-word}
.cist-destination-final strong{color:var(--text)}
.cist-destination-note{margin-top:6px;font-size:12px;color:var(--muted);line-height:1.45}
@media(max-width:600px){.cist-destination{padding:13px;border-radius:14px}.cist-destination-head{align-items:center}.cist-destination-host{font-size:11px}.cist-destination-hint{font-size:11px;margin-top:8px}}
</style>
'''

SCRIPT = r'''
<script id="cist-redirect-destination-script">
(function(){
  var input=document.getElementById('url'),form=document.getElementById('scan-form'),card=document.getElementById('result-card');
  if(!input||!form||!card)return;
  var last=null,lastInput='';
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function normalizedUrl(v){v=String(v||'').trim();if(!v)return null;try{return new URL(/^https?:\/\//i.test(v)?v:'https://'+v)}catch(e){return null}}
  function host(v){try{return new URL(v).hostname.toLowerCase().replace(/^www\./,'')}catch(e){return ''}}
  function base(h){h=String(h||'').toLowerCase().replace(/^www\./,'');var p=h.split('.').filter(Boolean);if(p.length<=2)return h;var two=p.slice(-2).join('.');var s={'co.uk':1,'org.uk':1,'com.au':1,'com.br':1,'co.jp':1,'co.nz':1};return s[two]&&p.length>=3?p.slice(-3).join('.'):two}
  function isUrlScan(data){return data&&typeof data==='object'&&(data.detectedType==='url'||data.finalUrl||Array.isArray(data.redirects))}
  function ensureHint(){
    if(document.querySelector('.cist-destination-hint'))return;
    var hint=document.createElement('div');hint.className='cist-destination-hint';hint.textContent='See the real destination before you open a link.';
    var tools=document.getElementById('image-safety-tools'),types=document.querySelector('.cist-input-types-v2');(types||tools||form).insertAdjacentElement('afterend',hint);
  }
  function ensureBox(){
    var box=document.getElementById('cist-destination');if(box)return box;
    box=document.createElement('section');box.id='cist-destination';box.className='cist-destination hidden';box.setAttribute('aria-live','polite');
    var anchor=document.getElementById('universal-summary')||document.getElementById('technical');
    if(anchor&&card.contains(anchor))anchor.insertAdjacentElement('afterend',box);else card.appendChild(box);
    return box;
  }
  function render(){
    var box=ensureBox();if(!last||!isUrlScan(last)){box.classList.add('hidden');return}
    var start=normalizedUrl(lastInput||input.value);var startHost=start?start.hostname.toLowerCase().replace(/^www\./,''):'';
    var finalUrl=String(last.finalUrl||'');var finalHost=String(last.finalHost||host(finalUrl)||startHost).toLowerCase().replace(/^www\./,'');
    var redirects=Array.isArray(last.redirects)?last.redirects:[];
    if(!finalHost){box.classList.add('hidden');return}
    var changed=!!startHost&&base(startHost)!==base(finalHost);var safety=last.safety||{};var signals=Array.isArray(safety.signals)?safety.signals:[];
    var danger=signals.some(function(s){return s&&s.severity==='high'})||safety.status==='high';
    var caution=danger||safety.status==='caution'||signals.some(function(s){return s&&['domain-change','punycode','ip-host'].indexOf(s.code)>=0&&s.severity!=='low'});
    var state=!redirects.length&&!changed?'direct':changed&&caution?'suspicious':'redirected';
    var label=state==='direct'?'Direct link':state==='suspicious'?'Suspicious redirect':'Redirected';
    var chain=[];if(startHost)chain.push(startHost);redirects.forEach(function(r){var h=host(r&&r.url);if(h&&chain[chain.length-1]!==h)chain.push(h)});if(finalHost&&chain[chain.length-1]!==finalHost)chain.push(finalHost);if(!chain.length)chain=[finalHost];
    var chainHtml=chain.map(function(h,i){return '<div class="cist-destination-hop">'+(i?'<span class="cist-destination-arrow">↓</span>':'<span class="cist-destination-arrow">●</span>')+'<span class="cist-destination-host">'+esc(h)+'</span></div>'}).join('');
    var note=state==='direct'?'No redirect was detected before reaching this destination.':state==='suspicious'?'The link ends on a different domain and other warning signs were detected. Verify the final domain before signing in, paying or downloading anything.':changed?'The link ends on a different domain than the one you received. Confirm that this destination is expected.':'This link uses one or more redirects before reaching its final destination.';
    box.className='cist-destination '+state;
    box.innerHTML='<div class="cist-destination-head"><h3 class="cist-destination-title">Where does this link really go?</h3><span class="cist-destination-state">'+label+'</span></div><div class="cist-destination-chain">'+chainHtml+'</div><div class="cist-destination-final"><strong>Final destination:</strong> '+esc(finalHost)+'</div><div class="cist-destination-note">'+esc(note)+'</div>';
  }
  var originalFetch=window.fetch;
  if(typeof originalFetch==='function'){
    window.fetch=function(resource,options){
      var url=typeof resource==='string'?resource:(resource&&resource.url)||'';
      return originalFetch.apply(this,arguments).then(function(response){
        try{
          var path=new URL(url,location.href).pathname;
          if(path==='/api/check'||path==='/api/analyze'){
            var scanValue=String(input.value||'').trim();
            response.clone().json().then(function(data){if(isUrlScan(data)){last=data;lastInput=scanValue;setTimeout(render,0)}}).catch(function(){});
          }
        }catch(e){}
        return response;
      });
    };
  }
  form.addEventListener('submit',function(){last=null;lastInput=String(input.value||'').trim();var b=document.getElementById('cist-destination');if(b)b.classList.add('hidden')},true);
  input.addEventListener('input',function(){var b=document.getElementById('cist-destination');if(b)b.classList.add('hidden')});
  document.addEventListener('cist:result-updated',function(){setTimeout(render,0)});
  ensureHint();ensureBox();
})();
</script>
'''

def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    if 'id="cist-redirect-destination-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)
    if 'id="cist-redirect-destination-script"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)
    required = ['Where does this link really go?', 'See the real destination before you open a link.', "path==='/api/check'||path==='/api/analyze'", 'Final destination:', 'Suspicious redirect']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Redirect destination UI guard failed: missing {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Added real destination redirect chain UI')

if __name__ == '__main__':
    main()
