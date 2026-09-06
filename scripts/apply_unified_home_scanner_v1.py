#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-unified-home-scanner-v1-style">
#cist-mega-screenshot-kicker,
#cist-mega-paste-separator,
.unified-scanner-label,
#image-safety-tools{display:none!important}

#cist-unified-home-scanner{
  width:min(720px,calc(100% - 28px));
  margin:16px auto 0;
  padding:11px;
  border:1px solid color-mix(in srgb,var(--cist-accent,#788ff7) 48%,var(--line));
  border-radius:20px;
  background:linear-gradient(180deg,color-mix(in srgb,var(--cist-accent,#788ff7) 5%,var(--card)),var(--card));
  box-shadow:0 15px 38px rgba(0,0,0,.11),0 0 0 1px color-mix(in srgb,var(--cist-accent,#788ff7) 8%,transparent);
  transition:border-color .16s ease,box-shadow .16s ease,transform .16s ease;
}
#cist-unified-home-scanner:focus-within{
  border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 78%,var(--line));
  box-shadow:0 18px 42px rgba(0,0,0,.14),0 0 0 3px color-mix(in srgb,var(--cist-accent,#788ff7) 12%,transparent);
}
#cist-unified-home-scanner.cist-unified-drag{
  border-style:dashed;
  background:color-mix(in srgb,var(--cist-accent,#788ff7) 10%,var(--card));
}
#cist-unified-home-scanner #scan-form{
  width:100%!important;
  max-width:none!important;
  margin:0!important;
  padding:0!important;
  display:grid!important;
  grid-template-columns:minmax(0,1fr) auto auto auto!important;
  align-items:center!important;
  gap:8px!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
}
#cist-unified-home-scanner .input-wrap{
  min-width:0!important;
  width:100%!important;
  height:54px!important;
  padding:0 4px!important;
  border:0!important;
  border-radius:13px!important;
  background:transparent!important;
  box-shadow:none!important;
}
#cist-unified-home-scanner #url{
  width:100%!important;
  min-width:0!important;
  height:54px!important;
  padding:0 10px!important;
  font-size:14px!important;
  border:0!important;
  outline:0!important;
  background:transparent!important;
  color:var(--text)!important;
}
#cist-unified-home-scanner #url::placeholder{color:color-mix(in srgb,var(--muted) 86%,transparent)}
#cist-unified-home-scanner #choose-image,
#cist-unified-home-scanner #paste,
#cist-unified-home-scanner #analyze{
  width:auto!important;
  min-width:0!important;
  height:46px!important;
  margin:0!important;
  padding:0 14px!important;
  border-radius:12px!important;
  white-space:nowrap!important;
  font-size:12.5px!important;
  font-weight:850!important;
  cursor:pointer!important;
}
#cist-unified-home-scanner #choose-image{
  border:1px solid var(--line)!important;
  background:color-mix(in srgb,var(--soft) 72%,var(--card))!important;
  color:var(--text)!important;
}
#cist-unified-home-scanner #choose-image:hover,
#cist-unified-home-scanner #paste:hover{
  border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 42%,var(--line))!important;
}
#cist-unified-home-scanner #paste{
  border:1px solid transparent!important;
  background:var(--soft)!important;
  color:var(--text)!important;
}
#cist-unified-home-scanner #analyze{
  min-width:104px!important;
  border:0!important;
  background:var(--cist-accent,#788ff7)!important;
  color:#fff!important;
  box-shadow:0 8px 20px color-mix(in srgb,var(--cist-accent,#788ff7) 22%,transparent)!important;
}
#cist-unified-home-scanner #analyze:disabled{opacity:.58!important;box-shadow:none!important}
#cist-unified-home-note{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  min-height:18px;
  margin-top:6px;
  color:var(--muted);
  font-size:9.5px;
  line-height:1.35;
  text-align:center;
}
#cist-unified-home-note strong{color:var(--text);font-weight:800}
#cist-unified-home-note .cist-dot{opacity:.55}
#cist-unified-home-scanner + #cist-mega-badges,
#cist-unified-home-scanner ~ #cist-mega-badges{margin-top:10px!important}

@media(max-width:700px){
  #cist-unified-home-scanner{
    width:calc(100% - 24px);
    margin-top:13px;
    padding:10px;
    border-radius:18px;
  }
  #cist-unified-home-scanner #scan-form{
    grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.15fr)!important;
    gap:7px!important;
  }
  #cist-unified-home-scanner .input-wrap{
    grid-column:1 / -1;
    height:52px!important;
    padding:0 2px!important;
    border-bottom:1px solid color-mix(in srgb,var(--line) 76%,transparent)!important;
    border-radius:0!important;
  }
  #cist-unified-home-scanner #url{height:51px!important;padding:0 8px!important;font-size:13.5px!important}
  #cist-unified-home-scanner #choose-image,
  #cist-unified-home-scanner #paste,
  #cist-unified-home-scanner #analyze{
    width:100%!important;
    height:44px!important;
    padding:0 7px!important;
    font-size:11.5px!important;
  }
  #cist-unified-home-note{font-size:9px;margin-top:7px;flex-wrap:wrap}
}
@media(max-width:390px){
  #cist-unified-home-scanner #choose-image,
  #cist-unified-home-scanner #paste,
  #cist-unified-home-scanner #analyze{font-size:10.5px!important}
}
</style>
'''

SCRIPT = r'''
<script id="cist-unified-home-scanner-v1-script">
(function(){
  var form=document.getElementById('scan-form');
  var tools=document.getElementById('image-safety-tools');
  var choose=document.getElementById('choose-image');
  var file=document.getElementById('image-file');
  var cameraFile=document.getElementById('camera-file');
  var input=document.getElementById('url');
  var inputWrap=form&&form.querySelector('.input-wrap');
  var paste=document.getElementById('paste');
  var analyze=document.getElementById('analyze');
  if(!form||!choose||!file||!input||!inputWrap||!paste||!analyze)return;

  var old=document.getElementById('cist-unified-home-scanner');
  if(old)return;

  var host=document.createElement('div');
  host.id='cist-unified-home-scanner';
  host.setAttribute('aria-label','Universal safety scanner');

  var parent=form.parentNode;
  var first=tools&&tools.parentNode===parent?tools:form;
  parent.insertBefore(host,first);

  // Keep the existing controls and event listeners, but place them in one visual component.
  if(paste.parentNode!==form)form.appendChild(paste);
  if(choose.parentNode!==form)form.appendChild(choose);
  if(file.parentNode!==form)form.appendChild(file);
  if(cameraFile&&cameraFile.parentNode!==form)form.appendChild(cameraFile);
  if(analyze.parentNode!==form)form.appendChild(analyze);

  // Stable order: text field → screenshot → paste → analyze.
  form.appendChild(inputWrap);
  form.appendChild(choose);
  form.appendChild(paste);
  form.appendChild(analyze);
  form.appendChild(file);
  if(cameraFile)form.appendChild(cameraFile);
  host.appendChild(form);

  var note=document.createElement('div');
  note.id='cist-unified-home-note';
  note.innerHTML='<span>Private by design</span><span class="cist-dot">·</span><span>No account required</span><span class="cist-dot">·</span><span>Automatic type detection</span>';
  host.appendChild(note);

  var kicker=document.getElementById('cist-mega-screenshot-kicker');if(kicker)kicker.remove();
  var sep=document.getElementById('cist-mega-paste-separator');if(sep)sep.remove();
  document.querySelectorAll('.unified-scanner-label').forEach(function(n){n.remove()});
  if(tools&&tools.parentNode)tools.remove();

  input.placeholder='Paste a link, message, email, profile or anything suspicious…';
  input.setAttribute('aria-label','Paste suspicious content to analyze');
  choose.textContent='＋ Screenshot';
  choose.setAttribute('aria-label','Add a screenshot to analyze');

  // Earlier image scripts rename this button after a scan. Keep the unified label stable.
  var renaming=false;
  var observer=new MutationObserver(function(){
    if(renaming)return;
    var t=(choose.textContent||'').trim().toLowerCase();
    if(t==='upload image'||t==='upload screenshot'||t==='upload photo'||t==='photo'||t==='image'){
      renaming=true;choose.textContent='＋ Screenshot';renaming=false;
    }
  });
  observer.observe(choose,{childList:true,subtree:true,characterData:true});

  function sendImage(files){
    if(!files||!files.length)return false;
    var f=Array.from(files).find(function(x){return /^image\/(jpeg|png|webp)$/i.test(x.type||'')});
    if(!f)return false;
    try{
      var dt=new DataTransfer();dt.items.add(f);file.files=dt.files;
      file.dispatchEvent(new Event('change',{bubbles:true}));
      return true;
    }catch(e){return false}
  }

  ['dragenter','dragover'].forEach(function(type){host.addEventListener(type,function(e){
    if(!(e.dataTransfer&&e.dataTransfer.types&&Array.from(e.dataTransfer.types).indexOf('Files')>=0))return;
    e.preventDefault();host.classList.add('cist-unified-drag');
  })});
  ['dragleave','drop'].forEach(function(type){host.addEventListener(type,function(e){
    if(type==='drop'){e.preventDefault();sendImage(e.dataTransfer&&e.dataTransfer.files)}
    host.classList.remove('cist-unified-drag');
  })});

  // If an image is on the clipboard, treat it as a screenshot even when the text field is focused.
  host.addEventListener('paste',function(e){
    var files=e.clipboardData&&e.clipboardData.files;
    if(files&&files.length&&Array.from(files).some(function(x){return /^image\//i.test(x.type||'')})){
      e.preventDefault();sendImage(files);
    }
  });

  file.addEventListener('change',function(){
    if(file.files&&file.files.length){note.innerHTML='<strong>Analyzing screenshot…</strong><span class="cist-dot">·</span><span>Checking every detected element</span>'}
  });
  document.addEventListener('cist:mega-result',function(){
    note.innerHTML='<span>Private by design</span><span class="cist-dot">·</span><span>No account required</span><span class="cist-dot">·</span><span>Automatic type detection</span>';
    if(!/analyz/i.test(choose.textContent||''))choose.textContent='＋ Screenshot';
  });
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s=HOME.read_text(encoding='utf-8')
s=re.sub(r'\s*<style id="cist-unified-home-scanner-v1-style">.*?</style>','',s,count=1,flags=re.S)
s=re.sub(r'\s*<script id="cist-unified-home-scanner-v1-script">.*?</script>','',s,count=1,flags=re.S)
for token in ['id="scan-form"','id="choose-image"','id="image-file"','id="paste"','id="analyze"']:
    if token not in s:
        raise RuntimeError('Unified scanner prerequisite missing: '+token)
s=s.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
for token in ['cist-unified-home-scanner','＋ Screenshot','Automatic type detection']:
    if token not in s:
        raise RuntimeError('Unified scanner guard failed: '+token)
HOME.write_text(s,encoding='utf-8')
print('Applied single-card unified homepage scanner')
