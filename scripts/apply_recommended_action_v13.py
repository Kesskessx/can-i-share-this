#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-recommended-action-v13-style">
.risk-breakdown{margin-top:12px;text-align:left}.risk-breakdown-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:0 0 8px}.risk-breakdown-heading{margin:0;color:var(--muted);font-size:10px;font-weight:950;letter-spacing:.08em;text-transform:uppercase}.risk-breakdown-note{color:var(--muted);font-size:9px;line-height:1.3;text-align:right}.risk-breakdown-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.risk-factor{min-width:0;padding:10px 11px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--soft) 58%,transparent)}.risk-factor-top{display:flex;align-items:center;gap:7px}.risk-factor-dot{width:8px;height:8px;flex:0 0 auto;border-radius:50%;background:var(--muted);opacity:.72}.risk-factor-label{color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.05em;text-transform:uppercase}.risk-factor-value{display:block;margin-top:4px;color:var(--text);font-size:12px;font-weight:850;line-height:1.3;overflow-wrap:anywhere}.risk-factor-detail{display:block;margin-top:2px;color:var(--muted);font-size:9px;line-height:1.4;overflow-wrap:anywhere}.risk-factor.risk-good .risk-factor-dot{background:var(--green);opacity:1}.risk-factor.risk-good .risk-factor-value{color:var(--green)}.risk-factor.risk-warn{border-color:color-mix(in srgb,var(--amber) 30%,var(--line));background:color-mix(in srgb,var(--amber) 5%,var(--card))}.risk-factor.risk-warn .risk-factor-dot{background:var(--amber);opacity:1}.risk-factor.risk-warn .risk-factor-value{color:var(--amber)}.risk-factor.risk-bad{border-color:color-mix(in srgb,var(--red) 36%,var(--line));background:color-mix(in srgb,var(--red) 6%,var(--card))}.risk-factor.risk-bad .risk-factor-dot{background:var(--red);opacity:1}.risk-factor.risk-bad .risk-factor-value{color:var(--red)}
.recommended-action{margin-top:12px;padding:14px 15px;border:1px solid var(--line);border-radius:14px;background:var(--card);text-align:left}.recommended-action-row{display:flex;gap:11px;align-items:flex-start}.recommended-action-icon{display:grid;place-items:center;flex:0 0 auto;width:38px;height:38px;border-radius:11px;background:var(--soft);font-size:19px;font-weight:900}.recommended-action-copy{min-width:0;flex:1}.recommended-action-kicker{display:block;margin-bottom:2px;color:var(--muted);font-size:9px;font-weight:950;letter-spacing:.09em;text-transform:uppercase}.recommended-action-title{display:block;color:var(--text);font-size:15px;line-height:1.28;font-weight:900}.recommended-action-detail{display:block;margin-top:4px;color:var(--muted);font-size:11px;line-height:1.45}.recommended-action-reasons{margin:9px 0 0;padding:9px 0 0 18px;border-top:1px solid var(--line);color:var(--muted);font-size:10px;line-height:1.5}.recommended-action-reasons li+li{margin-top:2px}.recommended-action.action-bad{border-color:color-mix(in srgb,var(--red) 42%,var(--line));background:color-mix(in srgb,var(--red) 7%,var(--card))}.recommended-action.action-bad .recommended-action-icon,.recommended-action.action-bad .recommended-action-kicker,.recommended-action.action-bad .recommended-action-title{color:var(--red)}.recommended-action.action-warn{border-color:color-mix(in srgb,var(--amber) 38%,var(--line));background:color-mix(in srgb,var(--amber) 6%,var(--card))}.recommended-action.action-warn .recommended-action-icon,.recommended-action.action-warn .recommended-action-kicker,.recommended-action.action-warn .recommended-action-title{color:var(--amber)}.recommended-action.action-good{border-color:color-mix(in srgb,var(--green) 34%,var(--line));background:color-mix(in srgb,var(--green) 5%,var(--card))}.recommended-action.action-good .recommended-action-icon,.recommended-action.action-good .recommended-action-kicker,.recommended-action.action-good .recommended-action-title{color:var(--green)}.recommended-action.action-pending .recommended-action-icon{color:var(--cist-accent)}
@media(max-width:600px){.risk-breakdown-head{display:block}.risk-breakdown-note{display:block;margin-top:2px;text-align:left}.risk-breakdown-grid{grid-template-columns:1fr}.risk-factor{padding:9px 10px}.recommended-action{padding:12px}.recommended-action-icon{width:35px;height:35px}.recommended-action-title{font-size:14px}}
</style>
'''

RISK_BLOCK = r'''      <section id="risk-breakdown" class="risk-breakdown hidden" aria-labelledby="risk-breakdown-heading">
        <div class="risk-breakdown-head"><h3 id="risk-breakdown-heading" class="risk-breakdown-heading">Risk breakdown</h3><small class="risk-breakdown-note">Independent signals — not a safety guarantee.</small></div>
        <div class="risk-breakdown-grid">
          <div id="risk-factor-1" class="risk-factor risk-neutral"><div class="risk-factor-top"><span class="risk-factor-dot" aria-hidden="true"></span><span id="risk-factor-1-label" class="risk-factor-label">Reputation</span></div><strong id="risk-factor-1-value" class="risk-factor-value">Not checked</strong><small id="risk-factor-1-detail" class="risk-factor-detail">Known threat-list status</small></div>
          <div id="risk-factor-2" class="risk-factor risk-neutral"><div class="risk-factor-top"><span class="risk-factor-dot" aria-hidden="true"></span><span id="risk-factor-2-label" class="risk-factor-label">URL signals</span></div><strong id="risk-factor-2-value" class="risk-factor-value">Checking</strong><small id="risk-factor-2-detail" class="risk-factor-detail">Local warning signs</small></div>
          <div id="risk-factor-3" class="risk-factor risk-neutral"><div class="risk-factor-top"><span class="risk-factor-dot" aria-hidden="true"></span><span id="risk-factor-3-label" class="risk-factor-label">Destination</span></div><strong id="risk-factor-3-value" class="risk-factor-value">Checking</strong><small id="risk-factor-3-detail" class="risk-factor-detail">Redirect behavior</small></div>
          <div id="risk-factor-4" class="risk-factor risk-neutral"><div class="risk-factor-top"><span class="risk-factor-dot" aria-hidden="true"></span><span id="risk-factor-4-label" class="risk-factor-label">Content</span></div><strong id="risk-factor-4-value" class="risk-factor-value">Website</strong><small id="risk-factor-4-detail" class="risk-factor-detail">What the link appears to contain</small></div>
        </div>
      </section>
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
  var panel=document.getElementById('recommended-action'),riskPanel=document.getElementById('risk-breakdown'),card=document.getElementById('result-card'),result=document.getElementById('result'),input=document.getElementById('url');
  var icon=document.getElementById('recommended-action-icon'),title=document.getElementById('recommended-action-title'),detail=document.getElementById('recommended-action-detail'),reasonsEl=document.getElementById('recommended-action-reasons');
  var verdict=document.getElementById('verdict'),reputation=document.getElementById('reputation'),whyList=document.getElementById('why-list'),techGrid=document.getElementById('tech-grid');
  var universal=document.getElementById('universal-summary');
  if(!panel||!riskPanel||!card||!input||!icon||!title||!detail||!reasonsEl)return;

  function emailMode(){var v=String(input.value||'').trim().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function emailDomain(){var v=String(input.value||'').trim().replace(/^mailto:/i,'');return (v.split('@')[1]||'').toLowerCase()}
  function hostOnly(value){try{return new URL(String(value||'')).hostname.toLowerCase().replace(/^www\./,'')}catch(e){return''}}
  function pushReason(list,text){text=String(text||'').trim();if(text&&list.indexOf(text)<0&&list.length<3)list.push(text)}
  function quickReasons(list){if(!whyList)return;Array.from(whyList.querySelectorAll('li')).slice(0,3).forEach(function(li){pushReason(list,li.textContent)})}
  function redirectContext(data){
    var start=hostOnly(input.value),finish=String(data&&data.finalHost||hostOnly(data&&data.finalUrl)||'').toLowerCase().replace(/^www\./,'');
    var count=Array.isArray(data&&data.redirects)?data.redirects.length:0;
    return{count:count,start:start,finish:finish,cross:Boolean(start&&finish&&start!==finish)};
  }
  function isShortener(host){return['bit.ly','tinyurl.com','t.co','rb.gy','rebrand.ly','is.gd','cutt.ly','tiny.cc','ow.ly','lnkd.in','1drv.ms','we.tl'].indexOf(String(host||'').toLowerCase())>=0}
  function setText(el,text){if(el&&el.textContent!==String(text))el.textContent=String(text)}
  function setAction(kind,symbol,heading,body,reasons){
    panel.className='recommended-action action-'+kind;setText(icon,symbol);setText(title,heading);setText(detail,body);
    var wanted=(reasons||[]).slice(0,3);var current=Array.from(reasonsEl.children).map(function(li){return li.textContent});
    if(JSON.stringify(current)!==JSON.stringify(wanted)){reasonsEl.innerHTML='';wanted.forEach(function(text){var li=document.createElement('li');li.textContent=text;reasonsEl.appendChild(li)})}
    reasonsEl.classList.toggle('hidden',!wanted.length);panel.classList.remove('hidden');
  }
  function setFactor(n,label,value,detailText,kind){
    var box=document.getElementById('risk-factor-'+n),labelEl=document.getElementById('risk-factor-'+n+'-label'),valueEl=document.getElementById('risk-factor-'+n+'-value'),detailEl=document.getElementById('risk-factor-'+n+'-detail');
    if(!box)return;box.className='risk-factor risk-'+(kind||'neutral');setText(labelEl,label);setText(valueEl,value);setText(detailEl,detailText);
  }
  function technicalValue(names){
    if(!techGrid)return'';var wanted=(names||[]).map(function(x){return String(x).toLowerCase()});var value='';
    Array.from(techGrid.querySelectorAll('.tech')).some(function(item){var s=item.querySelector('span'),strong=item.querySelector('strong');var label=String(s&&s.textContent||'').trim().toLowerCase();if(wanted.indexOf(label)>=0){value=String(strong&&strong.textContent||'').trim();return true}return false});
    return value;
  }
  function knownThreat(){var t=String(reputation&&reputation.textContent||'').toLowerCase();return Boolean(reputation&&reputation.classList.contains('bad')&&(t.indexOf('dangerous link')>=0||t.indexOf('known threat')>=0||t.indexOf('malware')>=0||t.indexOf('phishing')>=0))}

  function syncEmailUniversalSummary(){
    if(!emailMode()||!universal)return;
    var high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),low=card.classList.contains('status-low');
    var safetyBox=document.getElementById('universal-safety'),safetyValue=document.getElementById('universal-safety-value'),safetyNote=document.getElementById('universal-safety-note');
    if(safetyBox){var cls=high?'safety-bad':caution?'safety-warn':'';var next='universal-summary-item'+(cls?' '+cls:'');if(safetyBox.className!==next)safetyBox.className=next}
    setText(safetyValue,high?'High-risk email signals':caution?'Suspicious email signals':low?'No obvious address warning signs':'Check incomplete');
    setText(safetyNote,'Address and domain checks cannot prove who controls a mailbox.');
    setText(document.getElementById('universal-content-value'),'Email address');
    setText(document.getElementById('universal-content-note'),'Mailbox and sender domain');
    setText(document.getElementById('universal-destination-value'),emailDomain()||'Unknown domain');
    setText(document.getElementById('universal-destination-note'),'Sender domain');
    setText(document.getElementById('universal-advice-value'),high?'Verify this sender through another channel.':caution?'Verify the sender before replying.':low?'Treat unexpected requests cautiously.':'The sender could not be fully checked.');
    setText(document.getElementById('universal-advice-note'),'Do not rely on an email address alone to establish identity.');
    var routeBox=document.getElementById('redirect-route');if(routeBox)routeBox.classList.add('hidden');
    universal.classList.remove('hidden');
  }

  function renderUrlRisk(){
    var data=window.cistUniversalResultData||{},route=redirectContext(data),typeTitle=document.getElementById('link-type-title'),typeDetail=document.getElementById('link-type-detail');
    var type=String(typeTitle&&typeTitle.textContent||'Website'),typeLower=type.toLowerCase(),sensitive=window.cistSensitiveCategoryCurrent||null;
    var high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),checkedSafe=card.classList.contains('reputation-checked-safe'),running=card.classList.contains('one-click-running');
    var threat=knownThreat(),startShort=isShortener(route.start),riskyDownload=/(software|downloadable|compressed)/.test(typeLower);

    if(threat)setFactor(1,'Reputation','Known threat reported','An online threat database reported this URL.','bad');
    else if(checkedSafe)setFactor(1,'Reputation','No known threat reported','No known malware or phishing match was returned.','good');
    else if(running)setFactor(1,'Reputation','Checking threat lists','Known malware and phishing reports are still being checked.','neutral');
    else setFactor(1,'Reputation','Not checked or unavailable','No completed external reputation result is available.','neutral');

    if(high)setFactor(2,'URL signals','Strong warning signs','Local URL checks found high-risk characteristics.','bad');
    else if(caution)setFactor(2,'URL signals','Warning signs found','Local URL checks found characteristics that deserve caution.','warn');
    else if(running)setFactor(2,'URL signals','Local checks complete','The online reputation check is still running.','neutral');
    else setFactor(2,'URL signals','No obvious local warning signs','Local checks did not find an obvious high-risk URL pattern.','neutral');

    if(route.cross)setFactor(3,'Destination','Redirects to another website',(route.start||'Original site')+' → '+(route.finish||'final site'),'warn');
    else if(startShort)setFactor(3,'Destination','Shortened destination','The original short link hides where it ultimately leads.','warn');
    else if(route.count)setFactor(3,'Destination','Redirects followed',route.count+' redirect'+(route.count===1?'':'s')+' stayed on the same website.','neutral');
    else setFactor(3,'Destination','Direct destination',route.finish||route.start||'No redirect detected.','neutral');

    if(riskyDownload)setFactor(4,'Content',type,'Downloads and archives deserve extra caution before opening.','warn');
    else if(sensitive)setFactor(4,'Content',String(sensitive.typeLabel||type),String(sensitive.reason||'This category deserves extra context.'),'warn');
    else setFactor(4,'Content',type,String(typeDetail&&typeDetail.textContent||'What the link appears to contain.'),'neutral');
    riskPanel.classList.remove('hidden');
  }

  function renderEmailRisk(){
    var high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),low=card.classList.contains('status-low');
    if(high)setFactor(1,'Address signals','High-risk warning signs','The address or sender domain triggered strong warning signs.','bad');
    else if(caution)setFactor(1,'Address signals','Warning signs found','Some address or domain characteristics deserve verification.','warn');
    else if(low)setFactor(1,'Address signals','No obvious address warning signs','This does not prove who controls the mailbox.','neutral');
    else setFactor(1,'Address signals','Check incomplete','The address could not be fully assessed.','neutral');

    var mx=technicalValue(['Mail servers (MX)','MX records']);var mxLow=mx.toLowerCase();
    if(mxLow.indexOf('not found')>=0)setFactor(2,'Mail delivery','No mail servers found','The domain does not appear to publish normal mail-server records.','warn');
    else if(mx)setFactor(2,'Mail delivery','Mail servers found','MX: '+mx+'. This is an operational signal, not proof of trust.','neutral');
    else setFactor(2,'Mail delivery','Could not determine','Mail-server information is unavailable.','neutral');

    var spf=technicalValue(['SPF protection','SPF quality','SPF']),dmarc=technicalValue(['DMARC protection','DMARC policy','DMARC']);var auth=(spf+' '+dmarc).toLowerCase();
    if(auth.indexOf('not found')>=0)setFactor(3,'Authentication','Protection missing','SPF: '+(spf||'Unknown')+' · DMARC: '+(dmarc||'Unknown'),'warn');
    else if(auth.indexOf('p=none')>=0||auth.indexOf('monitoring only')>=0)setFactor(3,'Authentication','Monitoring-only policy','SPF: '+(spf||'Unknown')+' · DMARC: '+(dmarc||'Unknown'),'warn');
    else if(spf&&dmarc)setFactor(3,'Authentication','Authentication records found','SPF: '+spf+' · DMARC: '+dmarc+'. Presence does not prove sender identity.','neutral');
    else setFactor(3,'Authentication','Could not determine','SPF and DMARC could not both be verified.','neutral');

    var age=technicalValue(['Domain age']),m=String(age||'').match(/(\d+)\s*days?/i),days=m?parseInt(m[1],10):null;
    if(days!==null&&days<30)setFactor(4,'Domain age','Very new domain',days+' days old. New domains deserve extra verification.','warn');
    else if(days!==null&&days<90)setFactor(4,'Domain age','Recently registered domain',days+' days old. Recent registration is context, not proof of abuse.','warn');
    else if(days!==null)setFactor(4,'Domain age',days+' days old','Domain age alone does not prove that a sender is trustworthy.','neutral');
    else setFactor(4,'Domain age','Could not verify','Registration age is unavailable.','neutral');
    riskPanel.classList.remove('hidden');
  }

  function urlAction(){
    var reasons=[],data=window.cistUniversalResultData||{},typeTitle=document.getElementById('link-type-title');
    var type=String(typeTitle&&typeTitle.textContent||'Website'),typeLower=type.toLowerCase(),sensitive=window.cistSensitiveCategoryCurrent||null,route=redirectContext(data);
    var threat=knownThreat(),high=card.classList.contains('status-high'),caution=card.classList.contains('status-caution'),checkedSafe=card.classList.contains('reputation-checked-safe');
    var riskyDownload=/(software|downloadable|compressed)/.test(typeLower),shortened=isShortener(route.start)||typeLower.indexOf('shortened')>=0;

    if(card.classList.contains('one-click-running')||String(verdict&&verdict.textContent||'').toLowerCase().indexOf('checking')>=0){
      setAction('pending','…','Wait for the full safety check','Do not open the link until the online threat-list check finishes.',['Known malware and phishing reports are still being checked.']);return;
    }
    if(high||threat){
      if(threat)pushReason(reasons,'A known online threat report was returned.');quickReasons(reasons);
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
      setAction('warn','!',heading,'The threat lists did not report a known danger, but the link context still deserves a manual check.',reasons);return;
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
    if(result&&result.classList.contains('hidden')){panel.classList.add('hidden');riskPanel.classList.add('hidden');return}
    if(emailMode()){syncEmailUniversalSummary();renderEmailRisk();emailAction()}else{renderUrlRisk();urlAction()}
  }

  var queued=false;
  new MutationObserver(function(records){
    if(queued)return;
    var relevant=records.some(function(m){var el=m.target&&m.target.nodeType===1?m.target:(m.target&&m.target.parentElement);return !(el&&el.closest&&(el.closest('#recommended-action')||el.closest('#risk-breakdown')||el.closest('#universal-summary')))});
    if(!relevant)return;queued=true;queueMicrotask(function(){queued=false;update()});
  }).observe(card,{subtree:true,childList:true,attributes:true,characterData:true});
  if(universal)new MutationObserver(function(){if(emailMode())queueMicrotask(syncEmailUniversalSummary)}).observe(universal,{subtree:true,childList:true,attributes:true,characterData:true});
  input.addEventListener('input',function(){panel.classList.add('hidden');riskPanel.classList.add('hidden')});
  update();
})();
</script>
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Recommended action V1.3 / Risk breakdown V1.4 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-recommended-action-v13-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    if 'id="recommended-action"' not in source:
        source = replace_once(source, '      <section id="link-type-card"', RISK_BLOCK + BLOCK + '      <section id="link-type-card"', 'action and risk placement')

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
        'id="risk-breakdown"', 'Risk breakdown', 'Independent signals — not a safety guarantee.',
        'Reputation', 'URL signals', 'Destination', 'Content',
        'Address signals', 'Mail delivery', 'Authentication', 'Domain age',
        'Known threat reported', 'No known threat reported', 'Redirects to another website', 'Very new domain',
        'Email address', 'Mailbox and sender domain', 'Sender domain',
        "el.closest('#recommended-action')||el.closest('#risk-breakdown')||el.closest('#universal-summary')",
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Recommended action V1.3 / Risk breakdown V1.4 guard failed: missing {token}')

    if '100% safe' in source:
        raise RuntimeError('Risk breakdown V1.4 safety guard failed: absolute safety claim found')

    HOME.write_text(source, encoding='utf-8')
    print('Applied Recommended Action V1.3 and universal Risk Breakdown V1.4')


if __name__ == '__main__':
    main()
