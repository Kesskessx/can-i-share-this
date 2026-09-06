#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-advanced-technical-v2-style">
body.cist-advanced-tech-active #technical #tech-grid,
body.cist-advanced-tech-active #technical #providers{display:none!important}

#cist-advanced-tech-v2{display:none;margin-top:11px}
body.cist-advanced-tech-active #cist-advanced-tech-v2{display:block}
.cist-tech-v2-section{padding:12px 0;border-top:1px solid var(--line)}
.cist-tech-v2-section:first-child{border-top:0;padding-top:2px}
.cist-tech-v2-title{margin:0 0 8px;color:var(--text);font-size:10px;font-weight:900;letter-spacing:.065em;text-transform:uppercase}
.cist-tech-v2-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
.cist-tech-v2-row{min-width:0;padding:9px 10px;border-radius:10px;background:var(--soft)}
.cist-tech-v2-row small{display:block;color:var(--muted);font-size:8px;font-weight:800;letter-spacing:.035em;text-transform:uppercase}
.cist-tech-v2-row strong{display:block;margin-top:3px;color:var(--text);font-size:11px;line-height:1.35;overflow-wrap:anywhere}
.cist-tech-v2-wide{grid-column:1/-1}
.cist-tech-v2-provider{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:9px 10px;border-radius:10px;background:var(--soft)}
.cist-tech-v2-provider+.cist-tech-v2-provider{margin-top:6px}
.cist-tech-v2-provider-name{font-size:10px;font-weight:850;color:var(--text)}
.cist-tech-v2-provider-state{font-size:9px;font-weight:850;color:var(--muted);text-align:right}
.cist-tech-v2-provider-state.good{color:var(--green)}
.cist-tech-v2-provider-state.bad{color:var(--red)}
.cist-tech-v2-provider-state.warn{color:var(--amber)}
.cist-tech-v2-note{margin:7px 0 0;color:var(--muted);font-size:9px;line-height:1.45}

body.cist-compact-result-active:not(.cist-show-other-checks) .check-strip,
body.cist-compact-result-active:not(.cist-show-other-checks) #image-safety-tools,
body.cist-compact-result-active:not(.cist-show-other-checks) .cist-input-types-v2,
body.cist-compact-result-active:not(.cist-show-other-checks) .cist-destination-hint{display:none!important}
#cist-other-checks-toggle{display:none;width:max-content;max-width:100%;margin:12px auto 0;border:0;background:transparent;color:var(--cist-accent,#788ff7);font:inherit;font-size:11px;font-weight:800;cursor:pointer;padding:7px 9px;border-radius:9px}
#cist-other-checks-toggle:hover{background:var(--soft)}
body.cist-compact-result-active #cist-other-checks-toggle{display:block}
body.cist-show-other-checks #cist-other-checks-toggle{margin-bottom:4px}

@media(max-width:700px){
 .cist-tech-v2-grid{grid-template-columns:1fr}
 .cist-tech-v2-wide{grid-column:auto}
 .cist-tech-v2-provider{gap:8px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-advanced-technical-v2-script">
(function(){
  var result=document.getElementById('result'),card=document.getElementById('result-card'),technical=document.getElementById('technical'),form=document.getElementById('scan-form'),input=document.getElementById('url');
  if(!result||!card||!technical||!form||!input)return;
  var lastScan=null,lastDeep=null,lastDomainAge=null,scanCompletedAt=null;

  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function route(resource){try{return new URL(typeof resource==='string'?resource:(resource&&resource.url)||'',location.href).pathname}catch(e){return''}}
  function isUrlData(data){return data&&typeof data==='object'&&(data.detectedType==='url'||data.finalUrl||data.finalHost)}
  function isUrlInput(){return /^https?:\/\//i.test(clean(input.value))||(lastScan&&lastScan.detectedType==='url')}
  function yesNo(v){return v===true?'Yes':v===false?'No':'Could not determine'}
  function safeUrl(v){
    try{var u=new URL(String(v||''));var shown=u.origin+u.pathname;return shown+(u.search?'?…':'')}
    catch(e){return clean(v)}
  }
  function finalHost(){var d=lastScan||window.cistUniversalResultData||{};return clean(d.finalHost)||function(){try{return new URL(d.finalUrl||input.value).hostname}catch(e){return''}}()}
  function addRow(grid,label,value,wide){if(value===undefined||value===null||value==='')return;var row=document.createElement('div');row.className='cist-tech-v2-row'+(wide?' cist-tech-v2-wide':'');var sm=document.createElement('small');sm.textContent=label;var st=document.createElement('strong');st.textContent=String(value);row.appendChild(sm);row.appendChild(st);grid.appendChild(row)}
  function section(root,title){var s=document.createElement('section');s.className='cist-tech-v2-section';var h=document.createElement('h4');h.className='cist-tech-v2-title';h.textContent=title;s.appendChild(h);root.appendChild(s);return s}
  function grid(section){var g=document.createElement('div');g.className='cist-tech-v2-grid';section.appendChild(g);return g}
  function providerState(p){
    if(!p)return{label:'Not checked',cls:''};
    if(p.dangerous||p.status==='known-threat'||p.status==='known-phishing')return{label:'Threat match',cls:'bad'};
    if(p.checked)return{label:'Checked · No match',cls:'good'};
    if(p.status==='unavailable'||p.status==='misconfigured')return{label:'Unavailable',cls:'warn'};
    return{label:'Not checked',cls:''};
  }
  function addProvider(section,p,name){var row=document.createElement('div');row.className='cist-tech-v2-provider';var n=document.createElement('span');n.className='cist-tech-v2-provider-name';n.textContent=name;var s=providerState(p);var st=document.createElement('span');st.className='cist-tech-v2-provider-state '+s.cls;st.textContent=s.label;row.appendChild(n);row.appendChild(st);section.appendChild(row)}
  function domainAgeText(){
    var el=document.getElementById('url-domain-age-value'),t=clean(el&&el.textContent);if(t&&t!=='Checking registration age…')return t;
    if(lastDomainAge&&Number.isFinite(lastDomainAge.ageDays)){var d=lastDomainAge.ageDays;if(d<60)return d+' days';if(d<730)return'About '+Math.max(2,Math.round(d/30))+' months';return'About '+Math.max(2,Math.round(d/365))+' years'}
    return lastDomainAge&&lastDomainAge.known?'Registration date unavailable':'Could not verify';
  }
  function ensureBox(){var box=document.getElementById('cist-advanced-tech-v2');if(box)return box;box=document.createElement('div');box.id='cist-advanced-tech-v2';technical.appendChild(box);return box}
  function deepProvider(name){var list=lastDeep&&Array.isArray(lastDeep.providers)?lastDeep.providers:[];for(var i=0;i<list.length;i++)if(list[i]&&list[i].provider===name)return list[i];return null}
  function signalSummary(){var sig=lastScan&&lastScan.safety&&Array.isArray(lastScan.safety.signals)?lastScan.safety.signals:[];if(!sig.length)return'0 warning signals';var high=sig.filter(function(x){return x&&x.severity==='high'}).length,med=sig.filter(function(x){return x&&x.severity==='medium'}).length,low=sig.filter(function(x){return x&&x.severity==='low'}).length;var parts=[];if(high)parts.push(high+' high');if(med)parts.push(med+' medium');if(low)parts.push(low+' low');return parts.join(' · ')}
  function render(){
    if(result.classList.contains('hidden')||!isUrlInput()){document.body.classList.remove('cist-advanced-tech-active');return}
    var d=lastScan||window.cistUniversalResultData||{};if(!d||(!d.finalUrl&&!d.finalHost&&!d.status)){return}
    var box=ensureBox();box.innerHTML='';

    var urlSec=section(box,'URL analysis'),ug=grid(urlSec);
    addRow(ug,'Input URL',safeUrl(input.value),true);
    addRow(ug,'Final URL',safeUrl(d.finalUrl||input.value),true);
    addRow(ug,'Final host',finalHost()||'Could not verify');
    addRow(ug,'HTTP response',d.status||'Could not verify');
    addRow(ug,'Redirects followed',Array.isArray(d.redirects)?d.redirects.length:'Could not verify');
    addRow(ug,'HTTPS',function(){try{return new URL(d.finalUrl||input.value).protocol==='https:'?'Yes':'No'}catch(e){return'Could not determine'}}());
    addRow(ug,'Content type',clean(d.contentType)||'Not reported');
    addRow(ug,'Response time',Number.isFinite(d.responseMs)?d.responseMs+' ms':'Not reported');
    addRow(ug,'Login wall detected',yesNo(d.loginRequired));
    if(Array.isArray(d.addresses)&&d.addresses.length){var ips=d.addresses.slice(0,2).map(function(x){return x&&x.address}).filter(Boolean).join(', ');addRow(ug,'Resolved IP'+(d.addresses.length>1?'s':''),ips,true)}

    var domainSec=section(box,'Domain'),dg=grid(domainSec);
    addRow(dg,'Registered host',finalHost()||'Could not verify');
    addRow(dg,'Domain age',domainAgeText());
    addRow(dg,'RDAP lookup',lastDomainAge?(lastDomainAge.known?'Completed':'Unavailable'):(domainAgeText()!=='Could not verify'?'Completed':'Unavailable'));

    var threatSec=section(box,'Threat intelligence');
    addProvider(threatSec,deepProvider('Google Web Risk'),'Google Web Risk');
    addProvider(threatSec,deepProvider('PhishTank'),'PhishTank');
    var tg=grid(threatSec);addRow(tg,'URL warning signals',signalSummary(),true);
    var note=document.createElement('p');note.className='cist-tech-v2-note';note.textContent='A provider shown as “Not checked” did not participate in this result. No threat database can guarantee that a new or targeted link is safe.';threatSec.appendChild(note);

    var scanSec=section(box,'Scan'),sg=grid(scanSec);
    addRow(sg,'Scan completed',scanCompletedAt?scanCompletedAt.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}):'Just now');
    var checks=d.safety&&Array.isArray(d.safety.checksPerformed)?d.safety.checksPerformed:[];addRow(sg,'Checks performed',checks.length?checks.join(' · '):'URL structure and destination checks',true);

    var oldHelp=technical.querySelector('.technical-help');if(oldHelp)oldHelp.textContent='Request, destination, domain and threat-intelligence data from this scan. These signals explain the result; they are not a safety guarantee.';
    var sm=technical.querySelector('summary');if(sm)sm.textContent='Technical details (advanced)';
    document.body.classList.add('cist-advanced-tech-active');
  }

  var originalFetch=window.fetch;
  if(typeof originalFetch==='function')window.fetch=function(resource,options){var path=route(resource);return originalFetch.apply(this,arguments).then(function(response){
    if(path==='/api/check'||path==='/api/analyze'||path==='/api/deep-check'||path==='/api/domain-age')response.clone().json().then(function(data){
      if((path==='/api/check'||path==='/api/analyze')&&isUrlData(data)){lastScan=data;scanCompletedAt=new Date()}
      else if(path==='/api/deep-check'){lastDeep=data}
      else if(path==='/api/domain-age'){lastDomainAge=data}
      setTimeout(render,0);
    }).catch(function(){});return response});};

  function ensureToggle(){var b=document.getElementById('cist-other-checks-toggle');if(b)return b;b=document.createElement('button');b.id='cist-other-checks-toggle';b.type='button';b.textContent='Run another type of check ↓';result.insertAdjacentElement('afterend',b);b.addEventListener('click',function(){var on=document.body.classList.toggle('cist-show-other-checks');b.textContent=on?'Hide other check types ↑':'Run another type of check ↓'});return b}
  function reset(){lastScan=null;lastDeep=null;lastDomainAge=null;scanCompletedAt=null;document.body.classList.remove('cist-advanced-tech-active','cist-show-other-checks');var b=document.getElementById('cist-other-checks-toggle');if(b)b.textContent='Run another type of check ↓'}
  input.addEventListener('input',reset);form.addEventListener('submit',function(){document.body.classList.remove('cist-show-other-checks')},true);document.addEventListener('cist:result-updated',function(){setTimeout(render,50)});
  new MutationObserver(function(){setTimeout(render,50)}).observe(card,{attributes:true,attributeFilter:['class']});
  ensureToggle();render();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=re.sub(r'\s*<style id="cist-advanced-technical-v2-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-advanced-technical-v2-script">.*?</script>','',source,count=1,flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source=source.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
    required=['URL analysis','Threat intelligence','HTTP response','Response time','Login wall detected','Checked · No match','Not checked','Run another type of check ↓','cist-advanced-tech-active']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Advanced technical result guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied non-redundant advanced technical URL details')

if __name__=='__main__':
    main()
