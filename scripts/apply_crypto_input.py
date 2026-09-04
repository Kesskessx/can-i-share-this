#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

SCRIPT = r'''
<script id="cist-crypto-input-v1">
(function(){
  var input=document.getElementById('url'),form=document.getElementById('scan-form');
  if(!input||!form)return;
  var result=document.getElementById('result'),card=document.getElementById('result-card'),icon=document.getElementById('status-icon'),verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),advice=document.getElementById('advice'),adviceText=document.getElementById('advice-text'),actions=document.getElementById('actions'),deep=document.getElementById('deep'),consent=document.getElementById('consent'),reputation=document.getElementById('reputation'),technical=document.getElementById('technical'),techGrid=document.getElementById('tech-grid'),providers=document.getElementById('providers'),signals=document.getElementById('signals'),inputKind=document.getElementById('input-kind'),analyze=document.getElementById('analyze'),scanProgress=document.getElementById('scan-progress'),scanProgressTitle=document.getElementById('scan-progress-title'),scanProgressItems=document.getElementById('scan-progress-items'),whyVerdict=document.getElementById('why-verdict'),whyList=document.getElementById('why-list'),contextualPrevention=document.getElementById('contextual-prevention');
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function looksCrypto(v){
    v=String(v||'').trim();
    return /^0x[a-fA-F0-9]{40}$/.test(v)||/^(bc1|ltc1)[ac-hj-np-z02-9]{11,89}$/i.test(v)||/^[13LM3DAT][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v)||/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(v);
  }
  function setKind(){var v=input.value.trim();if(looksCrypto(v)&&inputKind){inputKind.textContent='Crypto';inputKind.classList.remove('hidden')}}
  input.addEventListener('input',setKind,true);input.addEventListener('paste',function(){setTimeout(setKind,0)},true);
  form.addEventListener('submit',async function(e){
    var value=input.value.trim();if(!looksCrypto(value))return;
    e.preventDefault();e.stopImmediatePropagation();
    if(result)result.classList.remove('hidden');if(card)card.className='result-card';if(icon)icon.textContent='…';if(verdict)verdict.textContent='Checking address…';if(summary)summary.textContent='Validating the address format and detected network.';
    [advice,actions,consent,reputation,technical,signals,whyVerdict,contextualPrevention].forEach(function(el){if(el)el.classList.add('hidden')});
    if(analyze){analyze.disabled=true;analyze.textContent='Analyzing…'}
    if(scanProgress){scanProgress.classList.remove('hidden');if(scanProgressTitle)scanProgressTitle.textContent='Checking crypto address…';if(scanProgressItems)scanProgressItems.textContent='Format · Network · Checksum · Safety limits'}
    try{
      var r=await fetch('/api/crypto-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input:value})});
      var d=await r.json();if(!r.ok)throw new Error(d&&d.error||'Request failed');
      var c=d.crypto||{},valid=!!c.formatValid;
      if(card)card.className='result-card '+(valid?'status-caution':'status-high');if(icon)icon.textContent=valid?'✓':'×';
      if(verdict)verdict.textContent=valid?'Valid address format':'Invalid or unsupported address';
      if(summary)summary.textContent=valid?('Detected network: '+(c.network||'Unknown')+'. Format validation passed, but this does not prove the wallet is trustworthy.'):'This value did not pass the supported crypto address-format checks.';
      if(advice&&adviceText){adviceText.textContent=valid?'Before sending funds, verify the address with the recipient through a separate trusted channel. A valid address can still belong to a scammer.':'Do not send funds to this address until you have verified the network and copied the address again from a trusted source.';advice.classList.remove('hidden')}
      if(actions)actions.classList.remove('hidden');if(deep)deep.classList.add('hidden');if(consent)consent.classList.add('hidden');if(reputation)reputation.classList.add('hidden');
      if(technical&&techGrid){techGrid.innerHTML='<div class="tech"><span>Network</span><strong>'+esc(c.network||'Unknown')+'</strong></div><div class="tech"><span>Address type</span><strong>'+esc(c.addressType||'Unknown')+'</strong></div><div class="tech"><span>Format</span><strong>'+(valid?'Valid':'Invalid')+'</strong></div><div class="tech"><span>Reputation</span><strong>Not checked</strong></div>';technical.classList.remove('hidden')}
      if(whyVerdict&&whyList){whyList.innerHTML=valid?'<li>The address structure matches the detected network.</li><li>Where available, the encoded address checksum was validated.</li><li>Ownership, transaction history and scam reputation are not verified by this check.</li>':'<li>The address structure or checksum does not match a supported network.</li>';whyVerdict.classList.remove('hidden')}
      if(inputKind){inputKind.textContent='Crypto';inputKind.classList.remove('hidden')}
    }catch(err){if(card)card.className='result-card status-unknown';if(icon)icon.textContent='?';if(verdict)verdict.textContent='Check incomplete';if(summary)summary.textContent='The crypto address check could not complete. Please try again.'}
    finally{if(analyze){analyze.disabled=false;analyze.textContent='Analyze'}if(scanProgress)scanProgress.classList.add('hidden')}
  },true);
})();
</script>
'''

def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=source.replace('placeholder="Paste a link or email address…"','placeholder="Paste a link, email or crypto address…"',1)
    source=source.replace('aria-label="Link or email address to analyze"','aria-label="Link, email or crypto address to analyze"',1)
    if 'id="cist-crypto-input-v1"' not in source:
        source=source.replace('</body>',SCRIPT+'\n</body>',1)
    HOME.write_text(source,encoding='utf-8')
    print('Integrated crypto address checks into universal scanner')

if __name__=='__main__':
    main()
