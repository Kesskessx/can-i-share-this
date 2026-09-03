#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOME = DIST / 'index.html'
HOST = 'https://canisharethis.com'
UPDATED = '2026-09-02'

STYLE = r'''
<style id="cist-benchmark-v16-style">
.scanner-proof{margin:12px auto 0;max-width:680px;border:1px solid var(--line);border-radius:13px;background:color-mix(in srgb,var(--card) 82%,var(--soft));text-align:left}.scanner-proof summary{display:flex;align-items:center;gap:7px;padding:10px 12px;color:var(--text);font-size:10px;font-weight:950;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;list-style:none}.scanner-proof summary::-webkit-details-marker{display:none}.scanner-proof summary::after{content:'+';margin-left:auto;color:var(--muted);font-size:15px}.scanner-proof[open] summary::after{content:'−'}.scanner-proof-body{padding:0 12px 11px}.scanner-proof-items{display:flex;gap:6px;flex-wrap:wrap}.scanner-proof-item{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--muted);font-size:9px;font-weight:800}.scanner-proof-item::before{content:'✓';color:var(--green);font-weight:950}.scanner-proof-note{display:block;margin-top:7px;color:var(--muted);font-size:9px;line-height:1.4}.home-explain{margin-top:34px}.home-section-kicker{margin:0 0 6px;color:var(--muted);font-size:10px;font-weight:950;letter-spacing:.08em;text-transform:uppercase}.home-explain h2,.use-cases h2{margin:0;font-size:clamp(24px,4vw,32px);letter-spacing:-.035em;line-height:1.1}.home-section-intro{margin:8px 0 0;color:var(--muted);font-size:13px;line-height:1.5}.how-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:13px}.how-card{display:flex;align-items:center;gap:9px;min-width:0;padding:11px;border:1px solid var(--line);border-radius:13px;background:var(--card)}.how-num{display:grid;place-items:center;flex:0 0 auto;width:26px;height:26px;border-radius:8px;background:color-mix(in srgb,var(--cist-accent) 10%,var(--soft));color:var(--cist-accent);font-size:11px;font-weight:950}.how-card strong{display:block;font-size:12px;line-height:1.2}.how-card p{margin:2px 0 0;color:var(--muted);font-size:9px;line-height:1.3}.use-cases{margin-top:34px}.use-case-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-top:14px}.use-case{display:flex;min-height:96px;padding:12px 8px;border:1px solid var(--line);border-radius:14px;background:var(--card);text-decoration:none;text-align:center;transition:transform .15s ease,border-color .15s ease;align-items:center;justify-content:center}.use-case:hover,.use-case:focus-visible{transform:translateY(-1px);border-color:color-mix(in srgb,var(--cist-accent) 45%,var(--line))}.use-case-icon{display:block;font-size:24px;line-height:1}.use-case strong{display:block;margin-top:7px;font-size:12px}.use-case small{display:block;margin-top:3px;color:var(--muted);font-size:9px;line-height:1.3}.domain-age-context{margin-top:9px;padding:10px 11px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--soft) 54%,transparent);text-align:left}.domain-age-row{display:flex;align-items:flex-start;gap:9px}.domain-age-icon{font-size:17px;line-height:1}.domain-age-copy{min-width:0}.domain-age-kicker{display:block;color:var(--muted);font-size:8px;font-weight:950;letter-spacing:.07em;text-transform:uppercase}.domain-age-value{display:block;margin-top:2px;color:var(--text);font-size:11px;font-weight:900}.domain-age-detail{display:block;margin-top:2px;color:var(--muted);font-size:9px;line-height:1.4}.domain-age-context.domain-age-warn{border-color:color-mix(in srgb,var(--amber) 38%,var(--line));background:color-mix(in srgb,var(--amber) 6%,var(--card))}.domain-age-context.domain-age-warn .domain-age-value{color:var(--amber)}.risk-factor-top{position:relative;padding-right:66px}.risk-factor-symbol{display:grid;place-items:center;width:22px;height:22px;flex:0 0 auto;border-radius:7px;background:var(--card);border:1px solid var(--line);font-size:11px}.risk-factor-state{position:absolute;right:0;top:1px;padding:3px 6px;border-radius:999px;background:var(--soft);color:var(--muted);font-size:7px;font-weight:950;letter-spacing:.05em;text-transform:uppercase}.risk-factor.risk-good .risk-factor-state{background:color-mix(in srgb,var(--green) 12%,var(--card));color:var(--green)}.risk-factor.risk-warn .risk-factor-state{background:color-mix(in srgb,var(--amber) 12%,var(--card));color:var(--amber)}.risk-factor.risk-bad .risk-factor-state{background:color-mix(in srgb,var(--red) 12%,var(--card));color:var(--red)}
@media(max-width:700px){.use-case-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.use-case{min-height:108px}.how-grid{gap:6px}.how-card{display:block;padding:9px;text-align:center}.how-num{margin:0 auto 6px}.how-card p{display:none}.scanner-proof{margin-top:11px}.risk-factor-top{padding-right:60px}}
</style>
'''

PROOF = r'''  <details id="scanner-proof" class="scanner-proof">
    <summary><span aria-hidden="true">🛡️</span><span>Technical checks</span></summary>
    <div class="scanner-proof-body"><div class="scanner-proof-items">
      <span class="scanner-proof-item">Google Web Risk</span>
      <span class="scanner-proof-item">Redirect analysis</span>
      <span class="scanner-proof-item">File type detection</span>
      <span class="scanner-proof-item">Domain age via RDAP</span>
      <span class="scanner-proof-item">Email domain checks</span>
    </div>
    <small class="scanner-proof-note">Known-threat checks apply to eligible public links. We do not show an accuracy percentage unless it has been independently validated.</small>
    </div>
  </details>
'''

HOME_SECTIONS = r'''  <section id="how-it-works" class="home-explain" aria-labelledby="how-title">
    <p class="home-section-kicker">How it works</p>
    <h2 id="how-title">Three steps. One clear answer.</h2>
    <div class="how-grid">
      <article class="how-card"><span class="how-num">1</span><div><strong>Paste</strong><p>A link, email or QR code</p></div></article>
      <article class="how-card"><span class="how-num">2</span><div><strong>Automatic checks</strong><p>Destination, risks and context</p></div></article>
      <article class="how-card"><span class="how-num">3</span><div><strong>Clear result</strong><p>Verdict and next action</p></div></article>
    </div>
  </section>

  <section id="use-cases" class="use-cases" aria-labelledby="use-case-title">
    <p class="home-section-kicker">One scanner, more signals</p>
    <h2 id="use-case-title">What can I check?</h2>
    <p class="home-section-intro">Paste it into the same scanner. We automatically detect what it is.</p>
    <div class="use-case-grid">
      <a class="use-case" href="/sms-link-checker"><span><span class="use-case-icon" aria-hidden="true">📱</span><strong>SMS link</strong><small>Suspicious text message</small></span></a>
      <a class="use-case" href="/whatsapp-link-checker"><span><span class="use-case-icon" aria-hidden="true">💬</span><strong>WhatsApp</strong><small>Message or group link</small></span></a>
      <a class="use-case" href="/qr-code-scam-checker"><span><span class="use-case-icon" aria-hidden="true">🔳</span><strong>QR code</strong><small>Reveal its destination</small></span></a>
      <a class="use-case" href="/download-link-checker"><span><span class="use-case-icon" aria-hidden="true">📦</span><strong>Download</strong><small>File or installer link</small></span></a>
      <a class="use-case" href="/short-link-checker"><span><span class="use-case-icon" aria-hidden="true">🔗</span><strong>Short link</strong><small>Reveal hidden redirects</small></span></a>
      <a class="use-case" href="/email-safety-checker"><span><span class="use-case-icon" aria-hidden="true">✉️</span><strong>Email</strong><small>Sender-domain signals</small></span></a>
      <a class="use-case" href="/crypto-scam-link-checker"><span><span class="use-case-icon" aria-hidden="true">₿</span><strong>Crypto</strong><small>Wallet or investment link</small></span></a>
      <a class="use-case" href="/gambling-link-safety"><span><span class="use-case-icon" aria-hidden="true">🎰</span><strong>Gambling</strong><small>Betting or casino website</small></span></a>
    </div>
  </section>
'''

DOMAIN_CONTEXT = r'''      <section id="url-domain-age" class="domain-age-context hidden" aria-label="Domain age context">
        <div class="domain-age-row"><span class="domain-age-icon" aria-hidden="true">🕒</span><div class="domain-age-copy"><span class="domain-age-kicker">Domain age</span><strong id="url-domain-age-value" class="domain-age-value">Checking registration age…</strong><small id="url-domain-age-detail" class="domain-age-detail">Only the final registered domain is queried via RDAP. The full URL is not sent for this lookup.</small></div></div>
      </section>
'''

SCRIPT = r'''
<script id="cist-benchmark-v16">
(function(){
  var input=document.getElementById('url'),result=document.getElementById('result'),card=document.getElementById('result-card'),risk=document.getElementById('risk-breakdown');
  var ageBox=document.getElementById('url-domain-age'),ageValue=document.getElementById('url-domain-age-value'),ageDetail=document.getElementById('url-domain-age-detail'),techGrid=document.getElementById('tech-grid');
  if(!input||!result||!card||!ageBox||!ageValue||!ageDetail)return;
  var ageCache={},agePending={},lastRequested='';
  var icons={'reputation':'🛡️','url signals':'🔎','destination':'↪️','content':'📄','address signals':'✉️','mail delivery':'📬','authentication':'🔐','domain age':'🕒'};

  function emailMode(){var v=String(input.value||'').trim().replace(/^mailto:/i,'');return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)}
  function hostOnly(value){try{return new URL(String(value||'')).hostname.toLowerCase().replace(/^www\./,'')}catch(e){return''}}
  function finalDomain(){var d=window.cistUniversalResultData||{};return String(d.finalHost||hostOnly(d.finalUrl)||hostOnly(input.value)||'').toLowerCase().replace(/^www\./,'')}
  function setText(el,text){if(el&&el.textContent!==String(text))el.textContent=String(text)}
  function ageLabel(days){if(!Number.isFinite(days))return null;if(days<60)return days+' day'+(days===1?'':'s')+' old';if(days<730)return 'About '+Math.max(2,Math.round(days/30))+' months old';return 'About '+Math.max(2,Math.round(days/365))+' years old'}
  function upsertTech(value){
    if(!techGrid)return;var item=techGrid.querySelector('[data-url-domain-age-tech]');if(!item){item=document.createElement('div');item.className='tech';item.setAttribute('data-url-domain-age-tech','');item.innerHTML='<span>Domain age</span><strong></strong>';techGrid.appendChild(item)}
    var strong=item.querySelector('strong');setText(strong,value);
  }
  function renderAge(payload){
    var days=payload&&Number.isFinite(payload.ageDays)?payload.ageDays:null,known=Boolean(payload&&payload.known),label=ageLabel(days);ageBox.className='domain-age-context';
    if(known&&label){
      setText(ageValue,label);upsertTech(label);
      if(days<30){ageBox.classList.add('domain-age-warn');setText(ageDetail,'Very new domain — verify it carefully. Domain age is context, not proof of fraud.');}
      else if(days<90){ageBox.classList.add('domain-age-warn');setText(ageDetail,'Recently registered domain. This deserves context, but age alone does not prove abuse.');}
      else setText(ageDetail,'Registration age via RDAP. Older domains can still be compromised, so age is never a safety guarantee.');
    }else if(known){setText(ageValue,'Registration date unavailable');setText(ageDetail,'RDAP responded, but no usable registration date was returned.');upsertTech('Could not verify date');}
    else{setText(ageValue,'Could not verify');setText(ageDetail,'Registration age was unavailable. This does not make the domain safer or more dangerous.');upsertTech('Could not verify');}
    ageBox.classList.remove('hidden');
  }
  async function ensureAge(){
    if(emailMode()||result.classList.contains('hidden')){ageBox.classList.add('hidden');return}
    var domain=finalDomain();if(!domain||domain.indexOf('.')<0)return;if(ageCache[domain]){renderAge(ageCache[domain]);return}if(agePending[domain])return;
    lastRequested=domain;agePending[domain]=true;ageBox.className='domain-age-context';setText(ageValue,'Checking registration age…');setText(ageDetail,'Only the final registered domain is queried via RDAP. The full URL is not sent for this lookup.');ageBox.classList.remove('hidden');
    try{
      var r=await fetch('/api/domain-age',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({domain:domain})});var data=await r.json();ageCache[domain]=data;if(finalDomain()===domain&&!emailMode())renderAge(data);
    }catch(e){var fallback={known:false,ageDays:null};ageCache[domain]=fallback;if(finalDomain()===domain&&!emailMode())renderAge(fallback)}finally{delete agePending[domain]}
  }
  function decorateRisk(){
    if(!risk)return;var note=risk.querySelector('.risk-breakdown-note');setText(note,'Four independent signal groups — not a safety guarantee.');
    Array.from(risk.querySelectorAll('.risk-factor')).forEach(function(box){var top=box.querySelector('.risk-factor-top'),labelEl=box.querySelector('.risk-factor-label');if(!top||!labelEl)return;var key=String(labelEl.textContent||'').trim().toLowerCase();var symbol=top.querySelector('.risk-factor-symbol');if(!symbol){symbol=document.createElement('span');symbol.className='risk-factor-symbol';symbol.setAttribute('aria-hidden','true');top.insertBefore(symbol,top.firstChild)}setText(symbol,icons[key]||'•');var state=top.querySelector('.risk-factor-state');if(!state){state=document.createElement('span');state.className='risk-factor-state';top.appendChild(state)}var text=box.classList.contains('risk-bad')?'High risk':box.classList.contains('risk-warn')?'Review':box.classList.contains('risk-good')?'No known issue':'Info';setText(state,text)});
  }
  function update(){decorateRisk();ensureAge()}
  document.addEventListener('cist:result-updated',update);
  input.addEventListener('input',function(){lastRequested='';ageBox.classList.add('hidden');var old=techGrid&&techGrid.querySelector('[data-url-domain-age-tech]');if(old)old.remove()});
  update();
})();
</script>
'''

PAGE_STYLE = '''
:root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#6d7480;--line:#e2e5e9;--soft:#f1f3f5;--accent:#6578e8}@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--soft:#1c2026;--accent:#8ea2ff}}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}.wrap{width:min(820px,calc(100% - 30px));margin:auto}header{border-bottom:1px solid var(--line)}header .wrap{height:64px;display:flex;align-items:center;justify-content:space-between}.brand{text-decoration:none;font-weight:900;letter-spacing:-.025em}.brand span{color:var(--accent)}nav{display:flex;gap:14px;font-size:12px;color:var(--muted)}main{padding:56px 0 68px}.kicker{margin:0;color:var(--accent);font-size:11px;font-weight:950;letter-spacing:.08em;text-transform:uppercase}h1{margin:8px 0 14px;font-size:clamp(36px,7vw,58px);line-height:1.02;letter-spacing:-.05em}.lead{margin:0;color:var(--muted);font-size:18px;max-width:720px}.box{margin-top:24px;padding:18px;border:1px solid var(--line);border-radius:16px;background:var(--card)}.box h2{margin:0 0 8px;font-size:21px}.box p{margin:0;color:var(--muted)}.box ul{margin:10px 0 0;padding-left:20px;color:var(--muted)}.box li+li{margin-top:6px}.cta{display:inline-block;margin-top:16px;padding:11px 15px;border-radius:11px;background:var(--text);color:var(--bg);text-decoration:none;font-weight:900}.faq{margin-top:30px}.faq details{padding:13px 0;border-top:1px solid var(--line)}.faq summary{cursor:pointer;font-weight:850}.faq p{color:var(--muted)}.related{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}.related a{padding:7px 10px;border:1px solid var(--line);border-radius:999px;text-decoration:none;font-size:11px;color:var(--muted)}footer{border-top:1px solid var(--line);padding:24px 0;color:var(--muted);font-size:11px}@media(max-width:600px){header nav{display:none}main{padding-top:40px}}
'''

PAGES = [
    {
        'slug': 'whatsapp-link-checker',
        'title': 'WhatsApp Link Checker: Check a Suspicious WhatsApp URL',
        'description': 'Got a suspicious WhatsApp link? Check the destination, redirects, file type, domain context and known threat reports before you trust it.',
        'kicker': 'WhatsApp scam prevention',
        'h1': 'Check a suspicious WhatsApp link',
        'lead': 'Copy the link without opening it, paste it into Can I Share This?, and review where it really goes before you sign in, pay or download anything.',
        'quick': 'A WhatsApp message can come from a hacked contact, unknown number, fake group, impersonator or compromised account. A familiar sender name does not make the destination trustworthy. Check the link separately from the person who sent it.',
        'checks': [
            'The final website after redirects and shortened links.',
            'Known malware and phishing reports for eligible public URLs.',
            'File or download signals, including executable and archive responses.',
            'Registration age of the final domain as context, not proof of safety.'
        ],
        'warning': [
            'Unexpected requests to log in, verify an account, pay a fee or claim a prize.',
            'A link whose final domain does not match the company or person you expected.',
            'A file, APK, ZIP or installer sent without a clear reason.',
            'Pressure to act immediately or keep the conversation secret.'
        ],
        'faq': [
            ('Can a WhatsApp link be phishing?', 'Yes. WhatsApp messages can contain links to lookalike login pages, fake payment pages or malicious downloads. The messaging app itself does not make an external website trustworthy.'),
            ('Does this checker read my WhatsApp messages?', 'No. The checker only analyzes the link or email address you choose to paste. It does not connect to or read your WhatsApp conversations.'),
            ('What if the message came from someone I know?', 'Treat the link separately from the sender identity. Accounts can be compromised. If the request is unusual, confirm it through another channel before paying, logging in or sharing information.')
        ],
        'related': [('/sms-link-checker', 'Suspicious SMS link'), ('/qr-code-link-checker', 'QR code checker'), ('/phishing-link-checker', 'Phishing link guide')]
    },
    {
        'slug': 'download-link-checker',
        'title': 'Download Link Checker: Check a File Link Before Opening It',
        'description': 'Check a suspicious download link for destination changes, file type, executable or archive signals, domain age and known online threat reports.',
        'kicker': 'Download safety',
        'h1': 'Check a download link before opening it',
        'lead': 'A download can look harmless while leading to an installer, archive or binary file. Check the destination and response type before you decide whether to open it.',
        'quick': 'The scanner does not execute the file. It inspects the link, final destination and response signals to identify common download risks. No scanner can guarantee that a file is harmless, so unexpected software should still be verified with the publisher.',
        'checks': [
            'The real destination after redirects and shortened URLs.',
            'The response content type and filename when the server provides them.',
            'Executable, app package, archive and forced-download indicators.',
            'Known malware and phishing reports for eligible public URLs.'
        ],
        'warning': [
            'Unexpected EXE, MSI, APK, DMG, ZIP, RAR or script downloads.',
            'A download hosted on a domain unrelated to the software publisher.',
            'A shortened link that hides where the file is hosted.',
            'Instructions to disable antivirus, browser warnings or operating-system protections.'
        ],
        'faq': [
            ('Does the checker run or install the file?', 'No. The link checker does not execute or install software. It analyzes URL, destination and response signals.'),
            ('Can a ZIP file be dangerous?', 'A ZIP or other archive is not automatically malicious, but it can contain executable or script files. Unexpected archives deserve additional verification before opening their contents.'),
            ('Does “no known threat” mean a download is safe?', 'No. New or targeted malicious files may not yet appear in known threat data. Verify the publisher and obtain software from the official source whenever possible.')
        ],
        'related': [('/safe-link-checker', 'Safe link checker'), ('/how-to-check-if-a-link-is-safe', 'How to check a link'), ('/can-a-link-give-you-a-virus', 'Can a link give you a virus?')]
    }
]


def render_page(page: dict) -> str:
    canonical = f"{HOST}/{page['slug']}"
    faq_schema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
            for q, a in page['faq']
        ]
    }
    webpage_schema = {
        '@context': 'https://schema.org', '@type': 'WebPage',
        'name': page['title'], 'description': page['description'], 'url': canonical,
        'dateModified': UPDATED
    }
    checks = ''.join(f'<li>{html.escape(x)}</li>' for x in page['checks'])
    warning = ''.join(f'<li>{html.escape(x)}</li>' for x in page['warning'])
    faq_html = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in page['faq'])
    related = ''.join(f'<a href="{html.escape(url)}">{html.escape(label)}</a>' for url, label in page['related'])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(page['title'])}</title><meta name="description" content="{html.escape(page['description'])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(page['title'])}"><meta property="og:description" content="{html.escape(page['description'])}"><meta property="og:url" content="{canonical}">
<script type="application/ld+json">{json.dumps(webpage_schema, separators=(',', ':'))}</script><script type="application/ld+json">{json.dumps(faq_schema, separators=(',', ':'))}</script><style>{PAGE_STYLE}</style></head>
<body><header><div class="wrap"><a class="brand" href="/">Can I Share <span>This?</span></a><nav><a href="/">Check</a><a href="/scam-prevention">Prevention</a><a href="/methodology">Methodology</a></nav></div></header>
<main class="wrap"><p class="kicker">{html.escape(page['kicker'])}</p><h1>{html.escape(page['h1'])}</h1><p class="lead">{html.escape(page['lead'])}</p>
<section class="box"><h2>At a glance</h2><p>{html.escape(page['quick'])}</p><a class="cta" href="/">Check it now</a></section>
<section class="box"><h2>What the checker looks at</h2><ul>{checks}</ul></section>
<section class="box"><h2>Warning signs worth checking</h2><ul>{warning}</ul></section>
<section class="faq"><h2>Common questions</h2>{faq_html}</section>
<section class="box"><h2>Related safety guides</h2><div class="related">{related}</div></section>
</main><footer><div class="wrap"><strong>Privacy-first · No signup.</strong> No scanner can guarantee that a link, download or sender is safe.</div></footer></body></html>'''


def add_to_sitemap(slug: str) -> None:
    sitemap = DIST / 'sitemap.xml'
    if not sitemap.is_file():
        return
    source = sitemap.read_text(encoding='utf-8')
    url = f'{HOST}/{slug}'
    if url in source:
        return
    node = f'  <url><loc>{url}</loc><lastmod>{UPDATED}</lastmod></url>\n'
    if '</urlset>' not in source:
        raise RuntimeError('Benchmark V1.6 failed: sitemap closing tag not found')
    sitemap.write_text(source.replace('</urlset>', node + '</urlset>', 1), encoding='utf-8')


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Benchmark V1.6 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-benchmark-v16-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)
    if 'id="scanner-proof"' not in source:
        source = replace_once(source, '  <section id="result"', PROOF + '\n  <section id="result"', 'proof strip')
    if 'id="url-domain-age"' not in source:
        source = replace_once(source, '      <section id="recommended-action"', DOMAIN_CONTEXT + '      <section id="recommended-action"', 'domain age context')
    if 'id="how-it-works"' not in source:
        source = replace_once(source, '</main>', HOME_SECTIONS + '\n</main>', 'homepage education sections')
    if 'id="cist-benchmark-v16"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'id="how-it-works"', 'Three steps. One clear answer.',
        '/sms-link-checker', '/whatsapp-link-checker', '/email-safety-checker', '/qr-code-scam-checker', '/download-link-checker',
        '/short-link-checker', '/crypto-scam-link-checker', '/gambling-link-safety',
        'id="scanner-proof"', 'Google Web Risk', 'Redirect analysis', 'File type detection', 'Domain age via RDAP',
        'We do not show an accuracy percentage unless it has been independently validated.',
        'id="url-domain-age"', "fetch('/api/domain-age'", 'Only the final registered domain is queried via RDAP.',
        'Four independent signal groups — not a safety guarantee.', 'risk-factor-symbol', 'risk-factor-state'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Benchmark V1.6 guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')

    for page in PAGES:
        target = DIST / f"{page['slug']}.html"
        target.write_text(render_page(page), encoding='utf-8')
        add_to_sitemap(page['slug'])

    for slug in ['whatsapp-link-checker', 'download-link-checker']:
        target = DIST / f'{slug}.html'
        if not target.is_file() or '<meta name="robots" content="index,follow">' not in target.read_text(encoding='utf-8'):
            raise RuntimeError(f'Benchmark V1.6 SEO guard failed for {slug}')

    print('Applied 5 benchmark upgrades: how-it-works, SEO use cases, URL domain age, verifiable credibility, and visual risk breakdown')


if __name__ == '__main__':
    main()
