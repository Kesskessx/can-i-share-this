#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-social-profile-v2-style">
body.cist-social-profile-result #cist-compact-result .cist-key-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
body.cist-social-profile-result #cist-compact-result .cist-key-item{min-height:58px}
body.cist-social-profile-result #cist-compact-result .cist-compact-why{border-left-color:color-mix(in srgb,var(--cist-accent,#788ff7) 68%,var(--line))}
body.cist-social-profile-result #technical{display:none!important}
.cist-social-profile-limit{margin-top:9px;color:var(--muted);font-size:9px;line-height:1.4}
@media(max-width:700px){body.cist-social-profile-result #cist-compact-result .cist-key-grid{grid-template-columns:1fr}}
</style>
'''

SCRIPT = r'''
<script id="cist-social-profile-v2-script">
(function(){
  var input=document.getElementById('url'),card=document.getElementById('result-card'),result=document.getElementById('result');
  if(!input||!card||!result)return;
  var last=null,applying=false;

  function clean(v){return String(v||'').replace(/\s+/g,' ').trim()}
  function route(resource){try{return new URL(typeof resource==='string'?resource:(resource&&resource.url)||'',location.href).pathname}catch(e){return''}}
  function socialData(d){return d&&typeof d==='object'&&(d.detectedType==='social-profile'||d.inputType==='social-profile')&&d.socialProfile}
  function icon(label){var l=String(label).toLowerCase();if(l.indexOf('platform')>=0)return'◎';if(l.indexOf('profile')>=0)return'👤';if(l.indexOf('public')>=0)return'◉';if(l.indexOf('imperson')>=0)return'🎭';if(l.indexOf('bio')>=0||l.indexOf('content')>=0)return'💬';if(l.indexOf('external')>=0)return'↗';return'✓'}
  function item(grid,label,value){if(!value)return;var box=document.createElement('div');box.className='cist-key-item';var ic=document.createElement('span');ic.className='cist-key-icon';ic.setAttribute('aria-hidden','true');ic.textContent=icon(label);var cp=document.createElement('div');cp.className='cist-key-copy';var sm=document.createElement('small');sm.textContent=label;var st=document.createElement('strong');st.textContent=value;cp.appendChild(sm);cp.appendChild(st);box.appendChild(ic);box.appendChild(cp);grid.appendChild(box)}
  function actionParts(text){text=clean(text);var m=text.match(/^(.+?[.!?])(?:\s+)(.+)$/);return m?[m[1],m[2]]:[text,'']}
  function publicLabel(p){var d=p&&p.profileData||{};if(d.publicMetadataRead&&d.suppliedContextAnalyzed)return'Public metadata + supplied text';if(d.publicMetadataRead)return'Public metadata read';if(d.suppliedContextAnalyzed)return'Supplied profile text';if(d.state==='blocked')return'Blocked by platform';if(d.state==='limited')return'Limited metadata';return'Identifier only'}
  function bioLabel(p){var c=p&&p.categories||{},n=Number(c.credentialSignals||0)+Number(c.moneySignals||0)+Number(c.contactSignals||0);return n?String(n)+' warning signal'+(n===1?'':'s'):'No obvious warning wording'}
  function impersonationLabel(p){var n=Number(p&&p.categories&&p.categories.impersonationSignals||0);return n?String(n)+' signal'+(n===1?'':'s')+' found':'No obvious impersonation signal'}
  function externalLabel(p){var d=p&&p.profileData||{},n=Number(d.externalLinkCount||0),short=Number(d.shortLinkCount||0);if(short)return n+' external · '+short+' shortened';return n?n+' external link'+(n===1?'':'s'):'None detected'}
  function reasons(d){var sig=d&&d.safety&&Array.isArray(d.safety.signals)?d.safety.signals:[];if(!sig.length)return clean(d.summary)||'No obvious impersonation or scam pattern was detected in the information available to this scan.';return sig.slice(0,2).map(function(s){return clean(s.title)+(s.detail?' — '+clean(s.detail):'')}).join(' · ')}
  function setDetected(){var el=document.querySelector('.cist-detected-type');if(el&&last)el.innerHTML='Detected automatically: <strong>Social profile</strong>'}
  function apply(){
    if(applying||!last||result.classList.contains('hidden'))return;
    var panel=document.getElementById('cist-compact-result');if(!panel){setTimeout(apply,60);return}
    applying=true;
    try{
      document.body.classList.add('cist-social-profile-result','cist-compact-result-active');
      setDetected();
      var d=last,p=d.socialProfile||{},s=d.safety||{};
      var verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),badge=document.getElementById('cist-compact-confidence');
      if(verdict)verdict.textContent=s.verdict||'Social profile analysis';
      if(summary)summary.textContent=d.summary||'';
      if(badge){badge.textContent='Profile analysis';badge.style.display='inline-flex'}
      panel.innerHTML='';
      var action=document.createElement('div');action.className='cist-compact-action';var label=document.createElement('span');label.className='cist-compact-label';label.textContent='What you should do';var parts=actionParts(d.recommendedAction||'Verify the exact handle independently before trusting the account.');var strong=document.createElement('strong');strong.textContent=parts[0];action.appendChild(label);action.appendChild(strong);if(parts[1]){var note=document.createElement('p');note.textContent=parts[1];action.appendChild(note)}panel.appendChild(action);
      var title=document.createElement('div');title.className='cist-key-title';title.textContent='Profile checks';panel.appendChild(title);var grid=document.createElement('div');grid.className='cist-key-grid';panel.appendChild(grid);
      item(grid,'Platform',p.platform||'Social platform');item(grid,'Profile',p.username?'@'+p.username:'Could not isolate');item(grid,'Public profile data',publicLabel(p));item(grid,'Impersonation',impersonationLabel(p));item(grid,'Bio / contact',bioLabel(p));item(grid,'External links',externalLabel(p));
      var why=document.createElement('div');why.className='cist-compact-why';var lead=document.createElement('strong');lead.textContent='Why this verdict: ';why.appendChild(lead);why.appendChild(document.createTextNode(reasons(d)));panel.appendChild(why);
      var lim=document.createElement('div');lim.className='cist-social-profile-limit';lim.textContent=clean(d.limitations);panel.appendChild(lim);
      var technical=document.getElementById('technical');if(technical)technical.open=false;
    }finally{applying=false}
  }
  function reset(){last=null;document.body.classList.remove('cist-social-profile-result')}

  var originalFetch=window.fetch;
  if(typeof originalFetch==='function')window.fetch=function(resource,options){var path=route(resource);return originalFetch.apply(this,arguments).then(function(response){
    if(path==='/api/analyze')response.clone().json().then(function(data){if(socialData(data)){last=data;window.cistSocialProfileResultData=data;setTimeout(apply,50)}}).catch(function(){});return response;
  });};

  input.addEventListener('input',reset);
  document.addEventListener('cist:result-updated',function(){setTimeout(apply,90)});
  new MutationObserver(function(m){if(!last||applying)return;for(var i=0;i<m.length;i++){var t=m[i].target;if(t&&t.closest&&t.closest('#cist-compact-result'))continue;setTimeout(apply,45);break}}).observe(card,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class']});
})();
</script>
'''


def patch_counter(source):
    source = source.replace(
        "var labels={link:'Links',qr:'QR',email:'Email',file:'Files',shortlink:'Short links',crypto:'Crypto',message:'Messages',other:'Other'};",
        "var labels={link:'Links',qr:'QR',email:'Email',file:'Files',shortlink:'Short links',crypto:'Crypto',message:'Messages',social:'Social profiles',other:'Other'};"
    )
    source = source.replace(
        "var order=['link','qr','email','file','shortlink','crypto','message','other'];",
        "var order=['link','qr','email','file','shortlink','crypto','message','social','other'];"
    )
    marker = "var v=String(input&&input.value||'').trim();if(/^mailto:/i.test(v)||/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v))return 'email';"
    replacement = "var v=String(input&&input.value||'').trim();if(/^@[A-Za-z0-9._-]{2,64}$/.test(v))return 'social';if(/^mailto:/i.test(v)||/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v))return 'email';"
    source = source.replace(marker, replacement)
    old = "try{var u=new URL(/^https?:\\/\\//i.test(v)?v:'https://'+v);var h=u.hostname.toLowerCase(),p=u.pathname.toLowerCase();if(/(^|\\.)(bit\\.ly|t\\.co|tinyurl\\.com|is\\.gd|ow\\.ly|buff\\.ly|rebrand\\.ly|cutt\\.ly|rb\\.gy)$/.test(h))return 'shortlink';"
    new = "try{var first=(v.match(/^https?:\\/\\/[^\\s<>\\\"']+/i)||[])[0]||v;var u=new URL(/^https?:\\/\\//i.test(first)?first:'https://'+first);var h=u.hostname.toLowerCase(),p=u.pathname.toLowerCase(),parts=u.pathname.split('/').filter(Boolean);var social=(/(^|\\.)instagram\\.com$/.test(h)&&parts.length&&!['p','reel','reels','stories','explore','accounts','direct'].includes((parts[0]||'').toLowerCase()))||(/(^|\\.)tiktok\\.com$/.test(h)&&parts.some(function(x){return x.charAt(0)==='@'}))||(/(^|\\.)(x\\.com|twitter\\.com)$/.test(h)&&parts.length&&!['home','explore','search','messages','settings','i','intent'].includes((parts[0]||'').toLowerCase()))||((/(^|\\.)facebook\\.com$/.test(h)||h==='m.facebook.com')&&parts.length&&!['watch','groups','marketplace','gaming','events','reel','reels','share'].includes((parts[0]||'').toLowerCase()))||((h==='t.me'||h==='telegram.me'||h==='www.telegram.me')&&parts.length&&!['joinchat','share','proxy','socks'].includes((parts[0]||'').toLowerCase()));if(social)return 'social';if(/(^|\\.)(bit\\.ly|t\\.co|tinyurl\\.com|is\\.gd|ow\\.ly|buff\\.ly|rebrand\\.ly|cutt\\.ly|rb\\.gy)$/.test(h))return 'shortlink';"
    source = source.replace(old, new)
    return source


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    source = re.sub(r'\s*<style id="cist-social-profile-v2-style">.*?</style>', '', source, count=1, flags=re.S)
    source = re.sub(r'\s*<script id="cist-social-profile-v2-script">.*?</script>', '', source, count=1, flags=re.S)
    source = patch_counter(source)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source = source.replace('</head>', STYLE+'\n</head>', 1)
    source = source.replace('</body>', SCRIPT+'\n</body>', 1)
    required = ['Profile checks','Public profile data','Impersonation','Bio / contact','External links','cist-social-profile-result',"social:'Social profiles'","return 'social'"]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Social profile V2 guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied useful social profile result UI and social usage counter type')

if __name__=='__main__':
    main()
