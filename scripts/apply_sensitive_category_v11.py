#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-sensitive-v11-style">
.content-warning{margin-top:10px;padding:12px 14px;border:1px solid color-mix(in srgb,var(--amber) 36%,var(--line));border-radius:13px;background:color-mix(in srgb,var(--amber) 7%,var(--card));text-align:left}.content-warning-row{display:flex;gap:10px;align-items:flex-start}.content-warning-icon{display:grid;place-items:center;flex:0 0 auto;width:34px;height:34px;border-radius:10px;background:color-mix(in srgb,var(--amber) 10%,var(--card));font-size:18px}.content-warning-copy{min-width:0;flex:1}.content-warning-kicker{display:block;color:var(--amber);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.content-warning-copy strong{display:block;margin-top:1px;color:var(--text);font-size:13px;line-height:1.25}.content-warning-copy small{display:block;margin-top:3px;color:var(--muted);font-size:11px;line-height:1.4}.content-warning-badge{flex:0 0 auto;padding:4px 7px;border-radius:999px;border:1px solid color-mix(in srgb,var(--amber) 28%,var(--line));color:var(--amber);font-size:9px;font-weight:900;white-space:nowrap}
@media(max-width:600px){.content-warning{padding:11px 12px}.content-warning-badge{display:none}}
</style>
'''

WARNING_BLOCK = r'''      <section id="content-warning" class="content-warning hidden" aria-labelledby="content-warning-title">
        <div class="content-warning-row">
          <span id="content-warning-icon" class="content-warning-icon" aria-hidden="true">⚠️</span>
          <div class="content-warning-copy"><span class="content-warning-kicker">Content category</span><strong id="content-warning-title">Sensitive content</strong><small id="content-warning-detail"></small></div>
          <span id="content-warning-badge" class="content-warning-badge"></span>
        </div>
      </section>
'''

HELPERS = r'''
  function cistSensitiveHost(host,domains){return domains.some(function(d){return host===d||host.endsWith('.'+d)})}
  function cistTermHits(text,terms){return terms.reduce(function(n,t){return n+(text.indexOf(t)>=0?1:0)},0)}
  function cistSensitiveCategory(data){
    var host=String(data&&data.finalHost||'').toLowerCase().replace(/^www\./,'');
    var meta=(String(data&&data.pageTitle||'')+' '+String(data&&data.pageDescription||'')).toLowerCase();
    var path='';try{path=new URL(String(data&&data.finalUrl||input.value||'')).pathname.toLowerCase()}catch(e){}
    var text=(host+' '+path+' '+meta).replace(/\s+/g,' ');

    var gamblingDomains=['gamdom.com','stake.com','bet365.com','draftkings.com','fanduel.com','pokerstars.com','betfair.com','unibet.com','williamhill.com','bovada.lv'];
    if(cistSensitiveHost(host,gamblingDomains)||cistTermHits(meta,['online casino','sports betting','sportsbook','casino games','slot games','betting site'])>=1||cistTermHits(meta,['casino','betting','slots','poker'])>=2){
      return{icon:'🎰',typeLabel:'Gambling / betting website',typeDetail:'Casino games, sports betting or wagering content',title:'Gambling or betting content',detail:'This type of site can involve real-money gambling and is often age-restricted.',badge:'Age-restricted',reason:'This appears to be a gambling or betting website.'};
    }

    var adultDomains=['pornhub.com','xvideos.com','xnxx.com','redtube.com','youporn.com'];
    if(cistSensitiveHost(host,adultDomains)||cistTermHits(meta,['adult videos','porn videos','xxx videos','18+ adult'])>=1||cistTermHits(meta,['porn','xxx','adult content'])>=2){
      return{icon:'🔞',typeLabel:'Adult-content website',typeDetail:'Sexually explicit or adult-oriented content',title:'Adult content',detail:'This site appears to contain adult material and may be age-restricted.',badge:'18+',reason:'This appears to be an adult-content website.'};
    }

    var torrentDomains=['thepiratebay.org','1337x.to','yts.mx','torrentgalaxy.to'];
    if(cistSensitiveHost(host,torrentDomains)||cistTermHits(meta,['torrent download','magnet link','torrent files'])>=1){
      return{icon:'🧲',typeLabel:'Torrent / file-sharing website',typeDetail:'Links used to share or download files',title:'Torrent or file-sharing content',detail:'Files shared this way may be legal or copyright-restricted. Check the source and what you are allowed to download.',badge:'File sharing',reason:'This appears to be a torrent or file-sharing website.'};
    }

    var cryptoDomains=['coinbase.com','binance.com','kraken.com','crypto.com','metamask.io','okx.com','bybit.com'];
    if(cistSensitiveHost(host,cryptoDomains)||cistTermHits(meta,['cryptocurrency exchange','crypto exchange','buy bitcoin','trade crypto'])>=1||cistTermHits(meta,['crypto','bitcoin','ethereum','wallet'])>=3){
      return{icon:'₿',typeLabel:'Crypto / financial website',typeDetail:'Cryptocurrency, wallet or trading services',title:'Financial / crypto content',detail:'Money or crypto transactions can involve financial loss. Double-check the exact website before signing in or sending funds.',badge:'Financial',reason:'This appears to be a cryptocurrency or financial-service website.'};
    }

    var weaponsDomains=['gunbroker.com','brownells.com','midwayusa.com'];
    if(cistSensitiveHost(host,weaponsDomains)||cistTermHits(meta,['firearms','ammunition','firearm dealer','gun store'])>=2){
      return{icon:'⚠️',typeLabel:'Weapons-related website',typeDetail:'Firearms, ammunition or weapons-related content',title:'Weapons-related content',detail:'This site appears to contain regulated or age-restricted weapons-related material.',badge:'Restricted',reason:'This appears to be a weapons-related website.'};
    }

    if(cistTermHits(meta,['cannabis dispensary','thc products','marijuana dispensary','recreational cannabis'])>=1||cistTermHits(meta,['cannabis','marijuana','thc','dispensary'])>=3){
      return{icon:'⚠️',typeLabel:'Drug-related website',typeDetail:'Cannabis or drug-related content',title:'Drug-related content',detail:'This site appears to contain controlled, regulated or age-restricted drug-related material.',badge:'Restricted',reason:'This appears to contain drug-related content.'};
    }

    return null;
  }
  function cistApplySensitiveFinal(){
    var c=window.cistSensitiveCategoryCurrent;if(!c)return;
    var cardEl=document.getElementById('result-card'),verdictEl=document.getElementById('verdict'),summaryEl=document.getElementById('summary'),whyEl=document.getElementById('why-verdict'),whyListEl=document.getElementById('why-list');
    if(!cardEl||!verdictEl||!summaryEl)return;
    if(cardEl.classList.contains('reputation-checked-safe')){
      if(verdictEl.textContent!=='No known malware or phishing threat')verdictEl.textContent='No known malware or phishing threat';
      var wanted='Known online threat lists did not report malware or phishing for this link. The content category shown below is a separate warning.';
      if(summaryEl.textContent!==wanted)summaryEl.textContent=wanted;
      if(whyListEl&&!whyListEl.querySelector('[data-sensitive-reason]')){var li=document.createElement('li');li.setAttribute('data-sensitive-reason','1');li.textContent=c.reason;whyListEl.appendChild(li);if(whyEl)whyEl.classList.remove('hidden')}
    }
  }
  function renderSensitiveCategory(data){
    var panel=document.getElementById('content-warning'),iconEl=document.getElementById('content-warning-icon'),titleEl=document.getElementById('content-warning-title'),detailEl=document.getElementById('content-warning-detail'),badgeEl=document.getElementById('content-warning-badge');
    var typeIcon=document.getElementById('link-type-icon'),typeTitle=document.getElementById('link-type-title'),typeDetail=document.getElementById('link-type-detail');
    if(!panel||!iconEl||!titleEl||!detailEl||!badgeEl)return;
    var c=cistSensitiveCategory(data||{});window.cistSensitiveCategoryCurrent=c||null;
    if(!c){panel.classList.add('hidden');return}
    iconEl.textContent=c.icon;titleEl.textContent=c.title;detailEl.textContent=c.detail;badgeEl.textContent=c.badge;panel.classList.remove('hidden');
    if(typeIcon)typeIcon.textContent=c.icon;if(typeTitle)typeTitle.textContent=c.typeLabel;if(typeDetail)typeDetail.textContent=c.typeDetail;
    cistApplySensitiveFinal();
  }
'''

OBSERVER = r'''
<script id="cist-sensitive-v11-observer">
(function(){
  var card=document.getElementById('result-card');if(!card)return;
  var scheduled=false;
  var observer=new MutationObserver(function(){if(scheduled)return;scheduled=true;queueMicrotask(function(){scheduled=false;if(window.cistSensitiveCategoryCurrent)cistApplySensitiveFinal()})});
  observer.observe(card,{subtree:true,childList:true,attributes:true,characterData:true});
})();
</script>
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Sensitive category V1.1 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-sensitive-v11-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    if 'id="content-warning"' not in source:
        source = replace_once(source, '      <section id="why-verdict"', WARNING_BLOCK + '      <section id="why-verdict"', 'warning placement')

    if 'function cistSensitiveCategory(data)' not in source:
        source = replace_once(source, '  function cistHostMatches(host,domain)', HELPERS + '  function cistHostMatches(host,domain)', 'helper insertion')

    source = replace_once(
        source,
        '  function renderQuick(data){renderLinkType(data);',
        '  function renderQuick(data){renderLinkType(data);renderSensitiveCategory(data);',
        'result hook'
    )

    old_loading = "function loading(){var linkTypePanel=document.getElementById('link-type-card');if(linkTypePanel)linkTypePanel.classList.add('hidden');"
    new_loading = "function loading(){var linkTypePanel=document.getElementById('link-type-card');if(linkTypePanel)linkTypePanel.classList.add('hidden');var sensitivePanel=document.getElementById('content-warning');if(sensitivePanel)sensitivePanel.classList.add('hidden');window.cistSensitiveCategoryCurrent=null;"
    source = replace_once(source, old_loading, new_loading, 'new scan reset')

    if 'id="cist-sensitive-v11-observer"' not in source:
        source = source.replace('</body>', OBSERVER + '\n</body>', 1)

    required = [
        'id="content-warning"',
        'Content category',
        'Gambling / betting website',
        "'gamdom.com'",
        'Adult-content website',
        'Torrent / file-sharing website',
        'Crypto / financial website',
        'Weapons-related website',
        'Drug-related website',
        'No known malware or phishing threat',
        'renderLinkType(data);renderSensitiveCategory(data);',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Sensitive category V1.1 guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied lightweight sensitive-content transparency V1.1')


if __name__ == '__main__':
    main()
