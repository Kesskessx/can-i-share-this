#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

STYLE = r'''
<style id="cist-one-click-scan-style">
.one-click-note{width:min(650px,100%);margin:9px auto 0;color:var(--muted);font-size:11px;line-height:1.4;text-align:center}
#deep,#consent{display:none!important}
.result-card.one-click-running .actions,.result-card.one-click-running .advice,.result-card.one-click-running .why-verdict,.result-card.one-click-running .contextual-prevention,.result-card.one-click-running .risk-meter{display:none!important}
.result-card.one-click-running .status-icon,.result-card.one-click-running h2{color:var(--cist-accent)}
.paste:disabled{opacity:.65;cursor:wait}
@media(max-width:600px){.one-click-note{padding:0 6px;font-size:10px}.paste{min-width:104px}}
</style>
'''

SCRIPT = r'''
<script id="cist-one-click-scan">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),paste=document.getElementById('paste'),analyze=document.getElementById('analyze');
  var card=document.getElementById('result-card'),icon=document.getElementById('status-icon'),verdict=document.getElementById('verdict'),summary=document.getElementById('summary');
  var actions=document.getElementById('actions'),deepConfirm=document.getElementById('deep-confirm'),reputation=document.getElementById('reputation');
  var advice=document.getElementById('advice'),adviceText=document.getElementById('advice-text'),whyVerdict=document.getElementById('why-verdict'),whyList=document.getElementById('why-list');
  if(!form||!input||!paste||!analyze||!card||!actions||!deepConfirm||!reputation)return;

  var deepRunning=false,quickStatus='unknown',quickWhy='';
  function emailValue(v){return String(v||'').trim().replace(/^mailto:/i,'')}
  function looksLikeEmail(v){v=emailValue(v);return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function buttonLabel(){return looksLikeEmail(input.value)?'Check email':'Check link'}
  function resetButton(){var label=buttonLabel();if(!deepRunning&&!analyze.disabled&&analyze.textContent!==label)analyze.textContent=label}
  function localStatus(){if(card.classList.contains('status-high'))return 'high';if(card.classList.contains('status-caution'))return 'caution';if(card.classList.contains('status-low'))return 'low';return 'unknown'}
  function restoreQuickReasons(extra){if(!whyVerdict||!whyList)return;whyList.innerHTML=(quickWhy||'')+(extra?'<li>'+extra+'</li>':'');if(whyList.innerHTML)whyVerdict.classList.remove('hidden')}

  function startFullCheck(){
    if(deepRunning||looksLikeEmail(input.value)||reputation.classList.contains('reputation-alert'))return;
    deepRunning=true;quickStatus=localStatus();quickWhy=whyList?whyList.innerHTML:'';
    card.className='result-card one-click-running';icon.textContent='…';verdict.textContent='Checking your link…';summary.textContent='Looking for scams, harmful files and known threats.';
    reputation.className='reputation reputation-pending';reputation.innerHTML='<strong>Running the full safety check…</strong><span>Checking the link and known online threat lists.</span>';reputation.classList.remove('hidden');
    analyze.disabled=true;analyze.textContent='Checking…';
    deepConfirm.click();
  }

  function finishFullCheck(){
    if(!deepRunning||!reputation.classList.contains('reputation-alert'))return;
    deepRunning=false;analyze.disabled=false;analyze.textContent=buttonLabel();
    var text=(reputation.textContent||'').toLowerCase();
    var knownDanger=reputation.classList.contains('bad')&&text.indexOf('dangerous link')>=0;
    var noKnown=text.indexOf('no known danger')>=0;
    var privacy=text.indexOf('kept it private')>=0||text.indexOf('did not send this link')>=0;

    if(knownDanger){
      card.classList.remove('one-click-running');
      adviceText.textContent='Do not open this link. If the message claims to be from a company, open that company’s official app or website yourself instead.';
      advice.classList.remove('hidden');
      return;
    }

    if(noKnown&&quickStatus==='high'){
      card.className='result-card status-high';icon.textContent='×';verdict.textContent='Dangerous warning signs found';
      summary.textContent='Our checks found strong warning signs. The link was not reported on the known-threat lists we checked, but that does not make it safe.';
      adviceText.textContent='Do not open this link. Verify the sender or go to the official website yourself.';advice.classList.remove('hidden');
      reputation.className='reputation bad reputation-alert';reputation.innerHTML='<strong>Strong warning signs found</strong><span>Known-threat lists did not report this link, but our own checks found serious warning signs.</span>';
      restoreQuickReasons('Known-threat lists did not report this link.');
      return;
    }

    if(noKnown&&quickStatus==='caution'){
      card.className='result-card status-caution';icon.textContent='!';verdict.textContent='Be careful with this link';
      summary.textContent='We found some warning signs. The online safety lists we checked did not report a known threat.';
      adviceText.textContent='Only continue if you expected this link and recognize where it goes. Do not enter a password, payment information or download a file unless you are sure.';advice.classList.remove('hidden');
      reputation.className='reputation reputation-alert';reputation.innerHTML='<strong>No known threat reported, but warning signs remain</strong><span>A link can still be unsafe even when it is not yet on a known-threat list.</span>';
      restoreQuickReasons('Known-threat lists did not report this link.');
      return;
    }

    if(noKnown){
      card.className='result-card status-low reputation-checked-safe';icon.textContent='✓';verdict.textContent='No known danger reported';
      summary.textContent='We checked the link itself and known online threat lists. Nothing dangerous was reported. This does not guarantee that the website is safe.';
      adviceText.textContent='If you expected this link and recognize the website, you can decide whether to open it. Be careful if it asks for a password, payment or download.';advice.classList.remove('hidden');
      reputation.classList.add('hidden');
      return;
    }

    if(privacy){
      card.className=quickStatus==='high'?'result-card status-high':'result-card status-caution';icon.textContent=quickStatus==='high'?'×':'!';
      verdict.textContent=quickStatus==='high'?'Dangerous warning signs found':'Extra check skipped to protect your privacy';
      summary.textContent=quickStatus==='high'?'Our own checks found strong warning signs. We did not send this private-looking link to outside safety services.':'This link looks like it contains private access information, so we did not send it to outside safety services.';
      adviceText.textContent=quickStatus==='high'?'Do not open this link. Verify the sender or use the official website yourself.':'Only open this private link if you expected it and trust the sender. The outside safety-list check was intentionally skipped.';advice.classList.remove('hidden');
      restoreQuickReasons('The outside safety-list check was skipped to protect private access information.');
      return;
    }

    if(quickStatus==='high'){
      card.className='result-card status-high';icon.textContent='×';verdict.textContent='Dangerous warning signs found';summary.textContent='Our own checks found strong warning signs. The online threat-list check could not be completed.';
      adviceText.textContent='Do not open this link. Verify the sender or use the official website yourself.';restoreQuickReasons('The online threat-list check could not be completed.');
    }else{
      card.className='result-card status-caution';icon.textContent='!';verdict.textContent='Safety check incomplete';summary.textContent='We could not complete the online threat-list check, so we cannot give a complete result.';
      adviceText.textContent='If you do not recognize this link, do not open it. Try again later or verify the sender another way.';restoreQuickReasons('The online threat-list check could not be completed.');
    }
    advice.classList.remove('hidden');
  }

  input.addEventListener('input',resetButton);
  form.addEventListener('submit',function(){if(!looksLikeEmail(input.value)){verdict.textContent='Checking your link…';summary.textContent='Looking for scams, harmful files and known threats.'}},false);

  paste.addEventListener('click',async function(e){
    e.preventDefault();e.stopImmediatePropagation();paste.disabled=true;paste.textContent='Pasting…';
    try{var text=await navigator.clipboard.readText();if(text){input.value=text;input.dispatchEvent(new Event('input',{bubbles:true}));form.requestSubmit()}else{input.focus()}}
    catch(err){input.focus();paste.textContent='Paste manually';setTimeout(function(){paste.textContent='Paste & check'},1200)}
    finally{paste.disabled=false;if(paste.textContent==='Pasting…')paste.textContent='Paste & check'}
  },true);

  var observer=new MutationObserver(function(){
    if(!deepRunning&&!looksLikeEmail(input.value)&&!actions.classList.contains('hidden')&&reputation.classList.contains('reputation-pending'))startFullCheck();
    if(deepRunning&&reputation.classList.contains('reputation-alert'))finishFullCheck();
    resetButton();
  });
  observer.observe(card,{subtree:true,childList:true,attributes:true,characterData:true});
  observer.observe(analyze,{subtree:true,childList:true,attributes:true,characterData:true});
  resetButton();
})();
</script>
'''

NOTE = '''<div class="one-click-note">One click runs the full check. Public links may be compared with online safety lists. Links that look like they contain private access codes are kept private.</div>'''


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
        raise RuntimeError(f"One-click scan failed: paste button replaced {paste_count} times")

    source, analyze_count = re.subn(
        r'(<button id="analyze" class="primary" type="submit">)(.*?)(</button>)',
        r'\1Check link\3', source, count=1
    )
    if analyze_count != 1:
        raise RuntimeError(f"One-click scan failed: analyze button replaced {analyze_count} times")

    if 'class="one-click-note"' not in source:
        source = source.replace('</form>', '</form>\n    ' + NOTE, 1)

    source = source.replace("on?'Analyzing…':'Analyze'", "on?'Checking…':'Check link'")
    source = source.replace("verdict.textContent='Analyzing…'", "verdict.textContent='Checking your link…'")
    source = source.replace("'Checking the URL and destination.'", "'Looking for scams, harmful files and known threats.'")

    if 'id="cist-one-click-scan"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'Paste &amp; check',
        '>Check link</button>',
        'One click runs the full check.',
        'id="cist-one-click-scan"',
        'deepConfirm.click()',
        'No known danger reported',
        'Extra check skipped to protect your privacy',
        'Dangerous warning signs found',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f"One-click scan guard failed: missing {token}")

    HOME.write_text(source, encoding="utf-8")
    print("Applied one-click full link scan with automatic threat-list check")


if __name__ == '__main__':
    main()
