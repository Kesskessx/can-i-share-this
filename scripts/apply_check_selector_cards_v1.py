#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-check-selector-v1-style">
/* Replace the old compressed type row with one professional, interactive selector. */
.cist-input-types-v2,#capability-strip{display:none!important}
#image-safety-tools.image-tools{margin-top:10px!important;min-height:18px!important}
#image-safety-tools .image-tool{display:none!important}
#image-safety-tools .image-note{margin:0!important;text-align:center!important;font-size:10px!important;line-height:1.35!important;color:var(--muted)!important}

#cist-check-selector{width:min(760px,calc(100% - 28px));margin:14px auto 0;text-align:left}
.cist-check-selector-kicker{margin:0 0 9px;text-align:center;color:color-mix(in srgb,var(--text) 72%,var(--muted));font-size:11px;font-weight:780;letter-spacing:.005em}
.cist-check-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.cist-check-card{appearance:none;display:grid;grid-template-columns:31px minmax(0,1fr);gap:9px;align-items:center;min-width:0;min-height:66px;padding:10px 11px;border:1px solid color-mix(in srgb,var(--line) 90%,transparent);border-radius:13px;background:color-mix(in srgb,var(--card) 91%,transparent);color:var(--text);font:inherit;text-align:left;cursor:pointer;box-shadow:none;transition:border-color .16s ease,background .16s ease,transform .16s ease,box-shadow .16s ease}
.cist-check-card:hover{transform:translateY(-1px);border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 36%,var(--line));background:color-mix(in srgb,var(--cist-accent,#788ff7) 4%,var(--card));box-shadow:0 7px 22px rgba(0,0,0,.12)}
.cist-check-card:focus-visible{outline:2px solid color-mix(in srgb,var(--cist-accent,#788ff7) 72%,white);outline-offset:2px}
.cist-check-card[aria-pressed="true"]{border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 62%,var(--line));background:color-mix(in srgb,var(--cist-accent,#788ff7) 8%,var(--card));box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--cist-accent,#788ff7) 10%,transparent)}
.cist-check-card-icon{display:grid;place-items:center;width:31px;height:31px;border-radius:9px;background:color-mix(in srgb,var(--soft) 88%,transparent);font-size:15px;line-height:1}
.cist-check-card-copy{min-width:0}.cist-check-card-title{display:block;color:var(--text);font-size:10.5px;font-weight:900;line-height:1.2;white-space:nowrap}.cist-check-card-desc{display:block;margin-top:3px;color:var(--muted);font-size:8.5px;font-weight:650;line-height:1.25;overflow-wrap:anywhere}
.cist-more-checks-wrap{display:flex;justify-content:center;margin-top:8px}
#cist-more-checks{appearance:none;border:0;background:transparent;color:var(--muted);padding:5px 9px;border-radius:9px;font:inherit;font-size:9.5px;font-weight:850;cursor:pointer;transition:color .15s ease,background .15s ease}
#cist-more-checks:hover,#cist-more-checks:focus-visible{color:var(--text);background:color-mix(in srgb,var(--soft) 72%,transparent);outline:none}
#cist-more-checks .cist-more-arrow{display:inline-block;margin-left:4px;transition:transform .16s ease}
#cist-more-checks[aria-expanded="true"] .cist-more-arrow{transform:rotate(180deg)}
#cist-more-grid{margin-top:7px}
#cist-more-grid[hidden]{display:none!important}
.cist-check-helper{margin:7px 0 0;text-align:center;color:var(--muted);font-size:8.5px;line-height:1.3;min-height:11px}

@media(max-width:700px){
 #cist-check-selector{width:calc(100% - 24px);margin-top:12px}
 .cist-check-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
 .cist-check-card{min-height:62px;padding:9px 10px;grid-template-columns:29px minmax(0,1fr);gap:8px}
 .cist-check-card-icon{width:29px;height:29px;font-size:14px}
 .cist-check-card-title{font-size:10px}.cist-check-card-desc{font-size:8px}
 .cist-check-selector-kicker{font-size:10.5px;margin-bottom:8px}
}
@media(max-width:370px){.cist-check-card-desc{display:none}.cist-check-card{min-height:49px}}
@media(prefers-reduced-motion:reduce){.cist-check-card,#cist-more-checks .cist-more-arrow{transition:none}.cist-check-card:hover{transform:none}}
</style>
'''

SCRIPT = r'''
<script id="cist-check-selector-v1-script">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),tools=document.getElementById('image-safety-tools');
  if(!form||!input)return;
  var old=document.getElementById('cist-check-selector');if(old)old.remove();

  var primary=[
    {id:'link',icon:'🔗',title:'Link',desc:'Redirects & threat checks',placeholder:'Paste a link to check'},
    {id:'email',icon:'✉️',title:'Email',desc:'Sender & scam signals',placeholder:'Paste an email address to check'},
    {id:'message',icon:'💬',title:'Message',desc:'Phishing & pressure',placeholder:'Paste a suspicious message'},
    {id:'social',icon:'👤',title:'Social profile',desc:'Impersonation & fake accounts',placeholder:'Paste a social profile URL or @username'}
  ];
  var extra=[
    {id:'qr',icon:'📷',title:'QR code',desc:'Decode before you open',action:'camera'},
    {id:'image',icon:'🖼️',title:'Image',desc:'Analyze screenshots & photos',action:'image'},
    {id:'file',icon:'📄',title:'File',desc:'Unsafe download signals',placeholder:'Paste a file or download link to check'},
    {id:'crypto',icon:'₿',title:'Crypto address',desc:'Wallet & scam context',placeholder:'Paste a crypto address to check'}
  ];

  function card(item){
    var b=document.createElement('button');b.type='button';b.className='cist-check-card';b.dataset.check=item.id;b.setAttribute('aria-pressed','false');
    var ic=document.createElement('span');ic.className='cist-check-card-icon';ic.setAttribute('aria-hidden','true');ic.textContent=item.icon;
    var cp=document.createElement('span');cp.className='cist-check-card-copy';var t=document.createElement('strong');t.className='cist-check-card-title';t.textContent=item.title;var d=document.createElement('span');d.className='cist-check-card-desc';d.textContent=item.desc;cp.appendChild(t);cp.appendChild(d);b.appendChild(ic);b.appendChild(cp);
    b.addEventListener('click',function(){select(item,true)});return b;
  }
  function grid(items,id){var g=document.createElement('div');g.className='cist-check-grid';if(id)g.id=id;items.forEach(function(x){g.appendChild(card(x))});return g}

  var section=document.createElement('section');section.id='cist-check-selector';section.setAttribute('aria-label','Choose what to check');
  var kicker=document.createElement('p');kicker.className='cist-check-selector-kicker';kicker.textContent='One scanner for links, messages, profiles and more.';section.appendChild(kicker);
  section.appendChild(grid(primary,'cist-primary-checks'));
  var moreWrap=document.createElement('div');moreWrap.className='cist-more-checks-wrap';var more=document.createElement('button');more.id='cist-more-checks';more.type='button';more.setAttribute('aria-expanded','false');more.setAttribute('aria-controls','cist-more-grid');more.innerHTML='<span>+4 more checks</span><span class="cist-more-arrow" aria-hidden="true">⌄</span>';moreWrap.appendChild(more);section.appendChild(moreWrap);
  var moreGrid=grid(extra,'cist-more-grid');moreGrid.hidden=true;section.appendChild(moreGrid);
  var helper=document.createElement('p');helper.className='cist-check-helper';helper.setAttribute('aria-live','polite');section.appendChild(helper);
  (tools||form).insertAdjacentElement('afterend',section);

  function setActive(id){section.querySelectorAll('.cist-check-card').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.check===id?'true':'false')})}
  function focusInput(placeholder){if(placeholder)input.placeholder=placeholder;try{input.focus({preventScroll:true})}catch(e){input.focus()}}
  function select(item,userAction){
    setActive(item.id);helper.textContent='';
    if(item.action==='camera'){
      var camera=document.getElementById('take-photo');helper.textContent='Open the camera or choose a QR screenshot.';if(camera&&userAction){camera.click();return}
    }
    if(item.action==='image'){
      var image=document.getElementById('choose-image');helper.textContent='Choose a screenshot or photo to analyze.';if(image&&userAction){image.click();return}
    }
    focusInput(item.placeholder||'Paste something suspicious to check');
  }
  more.addEventListener('click',function(){var open=more.getAttribute('aria-expanded')==='true';more.setAttribute('aria-expanded',open?'false':'true');moreGrid.hidden=open;more.querySelector('span:first-child').textContent=open?'+4 more checks':'Hide extra checks'});

  function detect(v){
    v=String(v||'').trim();if(!v)return'';
    if(/^@[A-Za-z0-9._-]{2,64}$/.test(v))return'social';
    if(/^https?:\/\/(?:www\.)?(?:instagram\.com|tiktok\.com|x\.com|twitter\.com|facebook\.com|t\.me|telegram\.me)\//i.test(v))return'social';
    if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))return'email';
    if(/^0x[a-fA-F0-9]{40}$/.test(v)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v))return'crypto';
    if(/^https?:\/\//i.test(v))return'link';
    return'message';
  }
  input.addEventListener('input',function(){var id=detect(input.value);setActive(id);if(id==='crypto'&&moreGrid.hidden){/* Keep the compact layout closed; active state is enough when expanded later. */}});
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=re.sub(r'\s*<style id="cist-check-selector-v1-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-check-selector-v1-script">.*?</script>','',source,count=1,flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source=source.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
    required=['One scanner for links, messages, profiles and more.','Impersonation & fake accounts','+4 more checks','cist-check-card','choose-image','take-photo','aria-pressed']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Check selector guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied professional clickable homepage check selector')

if __name__=='__main__':
    main()
