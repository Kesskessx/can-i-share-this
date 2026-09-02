#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-recommended-action-v13-style">
.recommended-action{margin-top:12px;padding:14px 15px;border:1px solid var(--line);border-radius:14px;background:var(--card);text-align:left}.recommended-action-row{display:flex;gap:11px;align-items:flex-start}.recommended-action-icon{display:grid;place-items:center;flex:0 0 auto;width:38px;height:38px;border-radius:11px;background:var(--soft);font-size:19px;font-weight:900}.recommended-action-copy{min-width:0;flex:1}.recommended-action-kicker{display:block;margin-bottom:2px;color:var(--muted);font-size:9px;font-weight:950;letter-spacing:.09em;text-transform:uppercase}.recommended-action-title{display:block;color:var(--text);font-size:15px;line-height:1.28;font-weight:900}.recommended-action-detail{display:block;margin-top:4px;color:var(--muted);font-size:11px;line-height:1.45}.recommended-action-reasons{margin:9px 0 0;padding:9px 0 0 18px;border-top:1px solid var(--line);color:var(--muted);font-size:10px;line-height:1.5}.recommended-action-reasons li+li{margin-top:2px}.recommended-action.action-bad{border-color:color-mix(in srgb,var(--red) 42%,var(--line));background:color-mix(in srgb,var(--red) 7%,var(--card))}.recommended-action.action-bad .recommended-action-icon,.recommended-action.action-bad .recommended-action-kicker,.recommended-action.action-bad .recommended-action-title{color:var(--red)}.recommended-action.action-warn{border-color:color-mix(in srgb,var(--amber) 38%,var(--line));background:color-mix(in srgb,var(--amber) 6%,var(--card))}.recommended-action.action-warn .recommended-action-icon,.recommended-action.action-warn .recommended-action-kicker,.recommended-action.action-warn .recommended-action-title{color:var(--amber)}.recommended-action.action-good{border-color:color-mix(in srgb,var(--green) 34%,var(--line));background:color-mix(in srgb,var(--green) 5%,var(--card))}.recommended-action.action-good .recommended-action-icon,.recommended-action.action-good .recommended-action-kicker,.recommended-action.action-good .recommended-action-title{color:var(--green)}.recommended-action.action-pending .recommended-action-icon{color:var(--cist-accent)}
@media(max-width:600px){.recommended-action{padding:12px}.recommended-action-icon{width:35px;height:35px}.recommended-action-title{font-size:14px}}
</style>
'''

BLOCK = r'''      <section id="recommended-action" class="recommended-action hidden" aria-labelledby="recommended-action-title">
        <div class="recommended-action-row">
          <span id="recommended-action-icon" class="recommended-action-icon" aria-hidden="true">…</span>
          <div class="recommended-action-copy">
            <span class="recommended-action-kicker">Recommended action</span>
            <strong id="recommended-action-title" class="recommended-action-title">Wait for the full safety check</strong>
            <small id="recommended-action-detail" class="recommended-action-detail">Do not open the link until the checks finish.</small>
          </div>
        </div>
        <ul id="recommended-action-reasons" class="recommended-action-reasons"></ul>
      </section>
'''

SCRIPT = r'''
<script id="cist-recommended-action-v13">
(function(){
  var panel=document.getElementById('recommended-action'),card=document.getElementById('result-card'),result=document.getElementById('result'),input=document.getElementById('url');
  var icon=document.getElementById('recommended-action-icon'),title=document.getElementById('recommended-action-title'),detail=document.getElementById('recommended-action-detail'),reasonsEl=document.getElementById('recommended-action-reasons');
  var verdict=document.getElementById('verdict'),reputation=document.getElementById('reputation'),whyList=document.getElementById('why-list');
  if(!panel||!card||!input||!icon||!title||!detail||!reasonsEl)return;

  function emailMode(){var v=String(input.value||'').trim().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function hostOnly(value){try{return new URL(String(value||'')).hostname.toLowerCase().replace(/^www\./,'')}catch(e){return''}}
  function pushReason(list,text){text=String(text||'').trim();if(text&&list.indexOf(text)<0&&list.length<3)list.push(text)}
  function quickReasons(list){if(!whyList)return;Array.from(whyList.querySelectorAll('li')).slice(0,3).forEach(function(li){pushReason(list,li.textContent)})}
  function redirectContext(data){
    var start=hostOnly(input.value),finish=String(data&&data.finalHost||hostOnly(data&&data.finalUrl)||'').toLowerCase().replace(/^www\./,'');
    var count=Array.isArray(data&&data.redirects)?data.redirects.length:0;
    return{count:count,start:start,finish:finish,cross:Boolean(start&&finish&&start!==finish)};
  }
  function setAction(kind,symbol,heading,body,reasons){
    panel.className='recommended-action action-'+kind;icon.textContent=symbol;title.textContent=heading;detail.textContent=body;
    reasonsEl.innerHTML='';(reasons||[]).slice(0,3).forEach(function(text){var li=document.createElement('li');li.textContent=text;reasonsEl.appendChild(li)});
    reasonsEl.classList.toggle('hidden',!reasonsEl.children.length);panel.classList.remove('hidden');
  }
  function urlAction(){
    var reasons=[],data=window.cistUniversalResultData||{},typeTitle=document.getElementById('link-type-title');
    var type=String(typeTitle&&typeTitle.textContent||'Website'),typeLower=type.toLowerCase(),sensitive=window.cistSensitiveCategoryCurrent||null,route=redirectContext(data);
    var repText=String(reputation&&reputation.textContent||'').toLowerCase(),knownThreat=Boolean(reputation&&reputation.classList.contains('bad')&&(repText.indexOf('dangerous link')>=0||repText.indexOf('known threat')>=0||repText.indexOf('malware')>=0||repText.indexOf('phishing')>=0));
    var high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),checkedSafe=card.classList.contains('reputation-checked-safe');
    var riskyDownload=/(software|downloadable|compressed)/.test(typeLower),shortened=typeLower.indexOf('shortened')>=0;

    if(card.classList.contains('one-click-running')||String(verdict&&verdict.textContent||'').toLowerCase().indexOf('checking')>=0){
      setAction('pending','…','Wait for the full safety check','Do not open the link until the online threat-list check finishes.',['Known malware and phishing reports are still being checked.']);return;
    }
    if(high||knownThreat){
      if(knownThreat)pushReason(reasons,'A known online threat report was returned.');quickReasons(reasons);
      if(riskyDownload)pushReason(reasons,'This destination delivers a file that deserves extra caution.');
      if(route.cross)pushReason(reasons,'The link changes website before reaching its final destination.');
      setAction('bad','×','Do not open this link','A known threat or strong warning signs were found. Use the official website or app instead.',reasons);return;
    }
    if(caution){
      quickReasons(reasons);if(riskyDownload)pushReason(reasons,'This link leads to software, a download or a compressed file.');if(shortened)pushReason(reasons,'A shortened link can hide its final website.');if(route.cross)pushReason(reasons,'The link redirects to a different website.');if(sensitive)pushReason(reasons,sensitive.reason);
      setAction('warn','!','Verify before continuing','Something about this link needs independent verification before you sign in, pay, download, or share information.',reasons);return;
    }
    if(checkedSafe&&(riskyDownload||shortened||route.cross||sensitive)){
      if(riskyDownload)pushReason(reasons,'No known threat was reported, but downloads can still be risky.');if(shortened)pushReason(reasons,'The original link hides the final website.');if(route.cross)pushReason(reasons,'The link redirects to a different website.');if(sensitive)pushReason(reasons,sensitive.reason);
      var heading=riskyDownload?'Verify this download before opening it':(shortened||route.cross?'Verify the final website before continuing':'Verify the website before continuing');
      setAction('warn','! ',heading,'The threat lists did not report a known danger, but the link context still deserves a manual check.',reasons);return;
    }
    if(checkedSafe){
      pushReason(reasons,'Known threat lists did not report malware or phishing for this link.');pushReason(reasons,'No scanner can guarantee that a website is safe.');
      setAction('good','✓','No known threat found — continue only if expected','Only continue if you recognize the destination and expected to receive this link.',reasons);return;
    }
    pushReason(reasons,'The full online threat-list result is not available yet.');
    setAction('pending','…','Run the full safety check first','Local checks alone cannot confirm that a link is safe.',reasons);
  }
  function emailAction(){
    var reasons=[],high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),low=card.classList.contains('status-low'),v=String(verdict&&verdict.textContent||'').toLowerCase();
    if(v.indexOf('checking')>=0||v.indexOf('analyz')>=0){setAction('pending','…','Checking this email address','Wait for the address and domain checks to finish.',['The checker is reviewing sender-domain signals.']);return}
    quickReasons(reasons);
    if(high){setAction('bad','×','Do not trust this sender yet','Verify the organization through its official website or another channel before replying, paying, or sharing information.',reasons);return}
    if(caution){setAction('warn','!','Verify the sender before replying','Do not open attachments, pay, or share sensitive information until you confirm who controls this mailbox.',reasons);return}
    if(low){pushReason(reasons,'Address-level checks cannot prove who is actually using a mailbox.');setAction('good','✓','No obvious address warning signs — stay cautious','Unexpected requests for passwords, payments or sensitive information should still be verified another way.',reasons);return}
    setAction('warn','!','Verify the sender another way','The email address could not be fully checked, so treat unexpected requests cautiously.',reasons);
  }
  function update(){
    if(result&&result.classList.contains('hidden')){panel.classList.add('hidden');return}
    if(emailMode())emailAction();else urlAction();
  }

  var queued=false;
  new MutationObserver(function(records){
    if(queued)return;
    var relevant=records.some(function(m){var el=m.target&&m.target.nodeType===1?m.target:(m.target&&m.target.parentElement);return !(el&&el.closest&&el.closest('#recommended-action'))});
    if(!relevant)return;queued=true;queueMicrotask(function(){queued=false;update()});
  }).observe(card,{subtree:true,childList:true,attributes:true,characterData:true});
  input.addEventListener('input',function(){panel.classList.add('hidden')});
  update();
})();
</script>
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Recommended action V1.3 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-recommended-action-v13-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    if 'id="recommended-action"' not in source:
        source = replace_once(source, '      <section id="link-type-card"', BLOCK + '      <section id="link-type-card"', 'action placement')

    if 'id="cist-recommended-action-v13"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'id="recommended-action"', 'Recommended action',
        'Do not open this link', 'Verify before continuing',
        'No known threat found — continue only if expected',
        'Run the full safety check first',
        'Verify the sender before replying',
        'No obvious address warning signs — stay cautious',
        "card.classList.contains('reputation-checked-safe')",
        'The link redirects to a different website.',
        'No scanner can guarantee that a website is safe.',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Recommended action V1.3 guard failed: missing {token}')

    if '100% safe' in source:
        raise RuntimeError('Recommended action V1.3 safety guard failed: absolute safety claim found')

    HOME.write_text(source, encoding='utf-8')
    print('Applied Recommended Action V1.3 decision layer')


if __name__ == '__main__':
    main()
