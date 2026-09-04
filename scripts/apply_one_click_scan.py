#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

STYLE = r'''
<style id="cist-one-click-scan-style">
.one-click-note{width:min(650px,100%);margin:9px auto 0;color:var(--muted);font-size:11px;line-height:1.4;text-align:center}
.paste:disabled{opacity:.65;cursor:wait}
@media(max-width:600px){.one-click-note{padding:0 6px;font-size:10px}.paste{min-width:104px}}
</style>
'''

SCRIPT = r'''
<script id="cist-one-click-scan">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),paste=document.getElementById('paste'),analyze=document.getElementById('analyze'),result=document.getElementById('result');
  if(!form||!input||!paste||!analyze)return;
  function emailValue(v){return String(v||'').trim().replace(/^mailto:/i,'')}
  function looksLikeEmail(v){v=emailValue(v);return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function buttonLabel(){return looksLikeEmail(input.value)?'Check email':'Check link'}
  function resetButton(){var label=buttonLabel();if(!analyze.disabled&&analyze.textContent!==label)analyze.textContent=label}
  function unlockForNextScan(){
    input.disabled=false;input.readOnly=false;analyze.disabled=false;paste.disabled=false;
    document.documentElement.style.pointerEvents='';document.body.style.pointerEvents='';
    document.documentElement.style.cursor='';document.body.style.cursor='';
    document.body.classList.remove('cist-full-scan-running');
    analyze.textContent=buttonLabel();paste.textContent='Paste & check';
  }
  input.addEventListener('input',function(){unlockForNextScan();resetButton()});
  paste.addEventListener('click',async function(e){
    e.preventDefault();e.stopImmediatePropagation();
    unlockForNextScan();
    paste.disabled=true;paste.textContent='Pasting…';
    var shouldSubmit=false;
    try{
      var text=await navigator.clipboard.readText();
      if(text){
        input.value=text.trim();
        input.dispatchEvent(new Event('input',{bubbles:true}));
        if(result)result.classList.add('hidden');
        shouldSubmit=true;
      }else input.focus();
    }catch(err){
      input.focus();paste.textContent='Paste manually';
      setTimeout(function(){if(!paste.disabled)paste.textContent='Paste & check'},1200);
    }finally{
      paste.disabled=false;
      if(paste.textContent==='Pasting…')paste.textContent='Paste & check';
      analyze.disabled=false;
      if(shouldSubmit)setTimeout(function(){try{form.requestSubmit()}catch(e){analyze.click()}},0);
    }
  },true);
  form.addEventListener('submit',function(){input.disabled=false;input.readOnly=false},true);
  window.addEventListener('pageshow',unlockForNextScan);
  unlockForNextScan();resetButton();
})();
</script>
'''

NOTE = '''<div class="one-click-note">Quick check first. The extra online reputation check runs only after you choose it and confirm that the public link may be shared.</div>'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError("Homepage not found")
    source = HOME.read_text(encoding="utf-8")

    if 'id="cist-one-click-scan-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, paste_count = re.subn(
        r'(<button id="paste" class="paste" type="button">)(.*?)(</button>)',
        r'\1Paste &amp; check\3', source, count=1
    )
    if paste_count != 1:
        raise RuntimeError(f"Fast scan failed: paste button replaced {paste_count} times")

    source, analyze_count = re.subn(
        r'(<button id="analyze" class="primary" type="submit">)(.*?)(</button>)',
        r'\1Check link\3', source, count=1
    )
    if analyze_count != 1:
        raise RuntimeError(f"Fast scan failed: analyze button replaced {analyze_count} times")

    if 'class="one-click-note"' not in source:
        source = source.replace('</form>', '</form>\n    ' + NOTE, 1)

    source = source.replace("on?'Analyzing…':'Analyze'", "on?'Checking…':'Check link'")
    source = source.replace("verdict.textContent='Analyzing…'", "verdict.textContent='Checking your link…'")
    source = source.replace("'Checking the URL and destination.'", "'Looking for scams, harmful files and known threats.'")

    if 'id="cist-one-click-scan"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = ['Paste &amp; check', '>Check link</button>', 'Quick check first.', 'id="cist-one-click-scan"', 'form.requestSubmit()', 'unlockForNextScan()', 'input.readOnly=false']
    for token in required:
        if token not in source:
            raise RuntimeError(f"Fast scan guard failed: missing {token}")
    if 'deepConfirm.click()' in source or '#deep,#consent{display:none' in source:
        raise RuntimeError("Fast scan guard failed: deep scan must require explicit consent")

    HOME.write_text(source, encoding="utf-8")
    print("Applied repeatable paste-and-check scanner controls")


if __name__ == '__main__':
    main()
