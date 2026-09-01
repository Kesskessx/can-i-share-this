#!/usr/bin/env python3
"""Apply Link Safety V6.1 positioning, homepage scanner and safety result UI."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

SAFETY_LINKS = [
    ("/safe-link-checker", "Safe Link Checker", "Check suspicious URL, redirect and download signals."),
    ("/scam-link-checker", "Scam Link Checker", "Review warning signs before paying or responding."),
    ("/phishing-link-checker", "Phishing Link Checker", "Check login and brand-lookalike URL risks."),
]

STYLE = r'''
<style id="cist-safety-v6-style">
#cist-safety-console{max-width:920px;margin:26px auto 34px;padding:clamp(20px,4vw,34px);border:1px solid rgba(127,127,127,.28);border-radius:24px;background:rgba(127,127,127,.055);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.cist-console-kicker{font-size:12px;font-weight:850;letter-spacing:.1em;text-transform:uppercase;opacity:.68;margin-bottom:7px}.cist-console-title{font-size:clamp(25px,4vw,38px);line-height:1.08;letter-spacing:-.03em;margin:0 0 9px}.cist-console-lead{max-width:720px;margin:0 0 20px;opacity:.76}
.cist-url-row{display:flex;gap:10px;align-items:stretch}.cist-url-input{flex:1;min-width:0;min-height:52px;padding:0 16px;border:1px solid rgba(127,127,127,.35);border-radius:14px;background:rgba(127,127,127,.06);color:inherit;font:inherit;outline:none}.cist-url-input:focus{border-color:currentColor;box-shadow:0 0 0 3px rgba(127,127,127,.12)}
.cist-actions{display:flex;gap:10px;margin-top:11px;flex-wrap:wrap}.cist-action{min-height:46px;padding:0 17px;border-radius:12px;border:1px solid rgba(127,127,127,.32);font-weight:800;font:inherit;cursor:pointer}.cist-action-primary{background:currentColor}.cist-action-primary span{filter:invert(1)}.cist-action-secondary{background:transparent;color:inherit}.cist-action:disabled{opacity:.45;cursor:not-allowed}
.cist-consent{display:flex;gap:9px;align-items:flex-start;margin:14px 0 0;font-size:13px;line-height:1.45;opacity:.78}.cist-consent input{margin-top:3px}.cist-private-note{margin:9px 0 0;font-size:12px;opacity:.66}
#cist-console-result{margin-top:20px}.cist-result-shell{border-top:1px solid rgba(127,127,127,.25);padding-top:20px}.cist-verdict{display:flex;align-items:flex-start;justify-content:space-between;gap:15px;margin-bottom:15px}.cist-verdict h3{margin:0;font-size:22px}.cist-verdict p{margin:4px 0 0;font-size:13px;opacity:.72}.cist-risk-pill{white-space:nowrap;border:1px solid currentColor;border-radius:999px;padding:7px 10px;font-size:12px;font-weight:850}.cist-low .cist-risk-pill{color:#137333}.cist-caution .cist-risk-pill{color:#a15c00}.cist-high .cist-risk-pill,.cist-known-dangerous .cist-risk-pill{color:#b3261e}
.cist-result-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}.cist-result-card{padding:15px;border:1px solid rgba(127,127,127,.22);border-radius:15px;background:rgba(127,127,127,.05)}.cist-result-card h4{margin:0 0 8px;font-size:14px}.cist-result-card p{margin:0;font-size:13px;line-height:1.5;opacity:.8}.cist-result-card ul{margin:7px 0 0;padding-left:18px;font-size:13px}.cist-result-card li{margin:5px 0}.cist-provider{padding:9px 0;border-top:1px solid rgba(127,127,127,.18)}.cist-provider:first-of-type{border-top:0;padding-top:0}.cist-provider strong{display:block;font-size:13px}.cist-provider span{display:block;font-size:12px;opacity:.72;margin-top:2px}.cist-result-foot{margin:13px 0 0;font-size:12px;line-height:1.5;opacity:.68}
#cist-safety-result{max-width:820px;margin:24px auto;padding:0 16px;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:inherit}.cist-safety-card{border:1px solid rgba(127,127,127,.28);border-radius:18px;padding:20px;background:rgba(127,127,127,.06)}.cist-safety-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:14px}.cist-safety-title{display:flex;gap:10px;align-items:center}.cist-safety-icon{font-size:24px}.cist-safety-title h2{font-size:22px;line-height:1.2;margin:0}.cist-safety-sub{font-size:13px;opacity:.7;margin-top:4px}.cist-safety-badge{white-space:nowrap;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:800;border:1px solid currentColor}.cist-safety-low .cist-safety-badge{color:#137333}.cist-safety-caution .cist-safety-badge{color:#a15c00}.cist-safety-high .cist-safety-badge{color:#b3261e}.cist-safety-score{font-size:14px;margin:0 0 14px;opacity:.82}.cist-safety-signals{display:grid;gap:9px;margin:0;padding:0;list-style:none}.cist-safety-signals li{padding:11px 12px;border-radius:12px;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.18)}.cist-safety-signals strong{display:block;font-size:14px;margin-bottom:2px}.cist-safety-signals span{font-size:13px;opacity:.78}.cist-safety-note{margin:14px 0 0;font-size:12px;line-height:1.5;opacity:.72}
#seo-safety-checks{max-width:980px;margin:28px auto;padding:24px;border:1px solid rgba(127,127,127,.25);border-radius:18px}#seo-safety-checks h2{margin-top:0}.seo-safety-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.seo-safety-card{display:block;padding:16px;border:1px solid rgba(127,127,127,.23);border-radius:14px;text-decoration:none}.seo-safety-card strong{display:block;margin-bottom:5px}.seo-safety-card span{display:block;font-size:14px;opacity:.72}.seo-safety-bridge{margin:22px 0;padding:18px;border:1px solid rgba(127,127,127,.23);border-radius:16px}.seo-safety-bridge h2{margin-top:0}.seo-safety-bridge ul{margin-bottom:0}
@media(max-width:680px){#cist-safety-console{margin:18px 0 26px;padding:18px;border-radius:18px}.cist-url-row{display:block}.cist-url-input{width:100%}.cist-actions{display:grid;grid-template-columns:1fr}.cist-action{width:100%}.cist-verdict{display:block}.cist-risk-pill{display:inline-block;margin-top:10px}.cist-result-grid{grid-template-columns:1fr}.cist-safety-head{flex-direction:column}.seo-safety-grid{grid-template-columns:1fr}#seo-safety-checks{margin:20px 16px;padding:18px}}
</style>
'''

CONSOLE = r'''
<section id="cist-safety-console" aria-labelledby="cist-console-title">
  <div class="cist-console-kicker">Link Safety · V6.1</div>
  <h2 class="cist-console-title" id="cist-console-title">Paste a suspicious link. Don’t open it.</h2>
  <p class="cist-console-lead">Check common scam, phishing, malware-download and redirect warning signs first. Quick Check stays privacy-first; Deep Safety Scan can also consult external threat-intelligence sources.</p>
  <form id="cist-safety-form">
    <div class="cist-url-row"><input class="cist-url-input" id="cist-safety-url" name="url" type="url" inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="https://example.com/suspicious-link" required aria-label="Link to check"></div>
    <div class="cist-actions">
      <button class="cist-action cist-action-primary" id="cist-quick-btn" type="submit"><span>Quick Check</span></button>
      <button class="cist-action cist-action-secondary" id="cist-deep-btn" type="button" disabled>Deep Safety Scan</button>
    </div>
    <label class="cist-consent"><input id="cist-deep-consent" type="checkbox"> <span>I understand that Deep Safety Scan shares this URL with external threat-intelligence providers. Do not use it for private or signed links.</span></label>
    <p class="cist-private-note">Quick Check does not submit your URL to a third-party reputation database. Deep Scan automatically refuses URLs that appear to contain sensitive tokens or signatures.</p>
  </form>
  <div id="cist-console-result" aria-live="polite"></div>
</section>
'''

SCRIPT = r'''
<script id="cist-safety-v6-script">
(function(){
  if(window.__cistSafetyV61Installed)return;window.__cistSafetyV61Installed=true;
  var nativeFetch=window.fetch;if(typeof nativeFetch!=="function")return;
  function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]})}
  function labelLocal(s){return !s?"Unknown":s.status==="low"?"Low observed risk":s.status==="caution"?"Caution":s.status==="high"?"High risk signals":"Unknown"}
  function localClass(s){return s&&["low","caution","high"].indexOf(s.status)>=0?s.status:"unknown"}
  function signalList(s){var x=s&&Array.isArray(s.signals)?s.signals:[];if(!x.length)return '<li>No obvious suspicious URL patterns were detected.</li>';return x.slice(0,6).map(function(i){return '<li><strong>'+esc(i.title||"Signal")+'</strong> — '+esc(i.detail||"")+'</li>'}).join("")}
  function providerHtml(deep){if(!deep)return '<p>Run Deep Safety Scan to consult external reputation sources.</p>';if(deep.privacyBlocked)return '<p><strong>Privacy protection:</strong> '+esc(deep.disclaimer||deep.verdict||"Deep Scan blocked")+'</p>';var p=Array.isArray(deep.providers)?deep.providers:[];if(!p.length)return '<p>'+esc(deep.verdict||"External reputation unavailable")+'</p>';return p.map(function(x){var mark=x.dangerous?"🔴":x.checked?"✓":"○";return '<div class="cist-provider"><strong>'+mark+' '+esc(x.provider||"Provider")+'</strong><span>'+esc(x.detail||x.status||"")+'</span></div>'}).join("")}
  function renderConsole(quick,deep){var root=document.getElementById("cist-console-result");if(!root||!quick)return;var s=quick.safety||{};var cls=deep&&deep.status==="known-dangerous"?"known-dangerous":localClass(s);var verdict=deep&&deep.status==="known-dangerous"?deep.verdict:(s.verdict||"Link risk assessment");var score=Number.isFinite(s.riskScore)?s.riskScore:0;var finalHost=quick.finalHost||"Unknown";var redirects=Array.isArray(quick.redirects)?quick.redirects.length:0;var privacy=deep?(deep.privacyBlocked?"Deep Scan was blocked to protect a sensitive-looking URL.":"You explicitly allowed external reputation checks for this scan."):"Quick Check kept third-party reputation lookups off.";root.className="cist-"+cls;root.innerHTML='<div class="cist-result-shell"><div class="cist-verdict"><div><h3>'+esc(verdict)+'</h3><p>Observed URL-pattern risk score: '+esc(score)+'/100</p></div><span class="cist-risk-pill">'+esc(deep&&deep.status==="known-dangerous"?"Known threat":labelLocal(s))+'</span></div><div class="cist-result-grid"><section class="cist-result-card"><h4>🛡️ Safety signals</h4><ul>'+signalList(s)+'</ul></section><section class="cist-result-card"><h4>🌐 Destination</h4><p>Final host: <strong>'+esc(finalHost)+'</strong><br>HTTP status: '+esc(quick.status||0)+'<br>Redirects followed: '+esc(redirects)+'</p></section><section class="cist-result-card"><h4>🔎 External reputation</h4>'+providerHtml(deep)+'</section><section class="cist-result-card"><h4>🔐 Privacy</h4><p>'+esc(privacy)+'</p></section></div><p class="cist-result-foot">'+esc((deep&&deep.disclaimer)||s.disclaimer||"No link checker can guarantee that a destination is malware-free. Do not enter passwords or run unexpected downloads unless you trust the sender and destination.")+'</p></div>'}
  async function quickCheck(url){var r=await nativeFetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:url})});return await r.json()}
  async function deepCheck(url){var r=await nativeFetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:url,consent:true})});return await r.json()}
  async function run(mode){var input=document.getElementById('cist-safety-url'),root=document.getElementById('cist-console-result');if(!input||!root)return;var url=input.value.trim();if(!url){input.focus();return}root.innerHTML='<p>Checking link…</p>';try{var q=await quickCheck(url);if(mode==='deep'){root.innerHTML='<p>Quick analysis complete. Checking external reputation…</p>';var target=q.finalUrl||url;var d=await deepCheck(target);renderConsole(q,d)}else{renderConsole(q,null)}}catch(e){root.innerHTML='<p>Unable to complete this check. Verify the URL and try again.</p>'}}
  function install(){var form=document.getElementById('cist-safety-form'),deep=document.getElementById('cist-deep-btn'),consent=document.getElementById('cist-deep-consent');if(form)form.addEventListener('submit',function(e){e.preventDefault();run('quick')});if(consent&&deep)consent.addEventListener('change',function(){deep.disabled=!consent.checked});if(deep)deep.addEventListener('click',function(){if(!consent||!consent.checked)return;run('deep')})}
  function renderLegacy(data){if(!data||!data.safety||document.getElementById('cist-safety-console'))return;var s=data.safety,host=document.querySelector('main')||document.body,root=document.getElementById('cist-safety-result');if(!root){root=document.createElement('section');root.id='cist-safety-result';root.setAttribute('aria-live','polite');host.appendChild(root)}var status=localClass(s);root.className='cist-safety-'+status;root.innerHTML='<div class="cist-safety-card"><div class="cist-safety-head"><div class="cist-safety-title"><span class="cist-safety-icon">🛡️</span><div><h2>Safety</h2><div class="cist-safety-sub">'+esc(s.verdict||"Link risk assessment")+'</div></div></div><span class="cist-safety-badge">'+esc(labelLocal(s))+'</span></div><p class="cist-safety-score">Observed risk score: <strong>'+esc(Number.isFinite(s.riskScore)?s.riskScore:0)+'/100</strong></p><ul class="cist-safety-signals">'+signalList(s)+'</ul><p class="cist-safety-note">'+esc(s.disclaimer||"")+'</p></div>'}
  window.fetch=function(){var args=arguments,target='';try{target=typeof args[0]==='string'?args[0]:(args[0]&&args[0].url)||''}catch(e){}return nativeFetch.apply(this,args).then(function(response){try{if(/\/api\/check(?:\?|$)/.test(String(target))&&!document.getElementById('cist-safety-console'))response.clone().json().then(renderLegacy).catch(function(){})}catch(e){}return response})};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();
</script>
'''


def route_file(route: str) -> Path | None:
    if route == "/":
        p = DIST / "index.html"
        return p if p.is_file() else None
    rel = route.strip("/")
    for p in (DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel):
        if p.is_file():
            return p
    return None


def patch_homepage() -> None:
    path = route_file("/")
    if not path:
        raise RuntimeError("Homepage not found")
    source = path.read_text(encoding="utf-8", errors="replace")
    source = re.sub(r"<title>.*?</title>", "<title>Check a Link for Scams, Phishing & Malware | Can I Share This?</title>", source, count=1, flags=re.I | re.S)
    description = "Paste a suspicious URL before you open it. Check scam, phishing, malware-download, redirect, privacy and recipient-access signals with an optional Deep Safety Scan."
    meta = f'<meta name="description" content="{html.escape(description, quote=True)}">'
    if re.search(r'<meta\s+name=["\']description["\'][^>]*>', source, flags=re.I):
        source = re.sub(r'<meta\s+name=["\']description["\'][^>]*>', meta, source, count=1, flags=re.I)
    else:
        source = source.replace("</head>", meta + "\n</head>", 1)
    source = re.sub(r"BEFORE\s+YOU\s+SHARE|BEFORE\s+YOU\s+OPEN\s+OR\s+SHARE", "BEFORE YOU OPEN OR SHARE", source, flags=re.I)
    source = re.sub(r"Will it open\?\s*Is it private\?\s*(?:Is it safe\?\s*)?Will it expire\?", "Is it safe? Will it open? Is it private? Will it expire?", source, flags=re.I)
    source = re.sub(r'(<h1(?:\s[^>]*)?>).*?(</h1>)', r'\1Check a link before you open or share it\2', source, count=1, flags=re.I | re.S)
    if 'id="cist-safety-console"' not in source:
        h1 = re.search(r'</h1>', source, flags=re.I)
        if h1:
            source = source[:h1.end()] + "\n" + CONSOLE + source[h1.end():]
        elif re.search(r'<main(?:\s[^>]*)?>', source, flags=re.I):
            source = re.sub(r'(<main(?:\s[^>]*)?>)', r'\1\n' + CONSOLE, source, count=1, flags=re.I)
        else:
            source = source.replace("<body>", "<body>\n" + CONSOLE, 1)
    if 'id="seo-safety-checks"' not in source:
        cards = "".join(f'<a class="seo-safety-card" href="{href}"><strong>{html.escape(label)}</strong><span>{html.escape(desc)}</span></a>' for href, label, desc in SAFETY_LINKS)
        block = ('<section id="seo-safety-checks" aria-labelledby="seo-safety-title"><h2 id="seo-safety-title">More link safety checks</h2><p>Use the dedicated guides for suspicious links, scam messages and phishing attempts. Google Drive and Dropbox tools remain available for recipient-access checks.</p>' + f'<div class="seo-safety-grid">{cards}</div></section>')
        source = source.replace("</main>", block + "\n</main>", 1) if "</main>" in source else source.replace("</body>", block + "\n</body>", 1)
    path.write_text(source, encoding="utf-8")


def add_safety_bridges() -> None:
    target_routes = ["/google-drive-link-checker", "/dropbox-link-checker", "/drive-vs-dropbox-share-link-checker", "/privacy-link-checker", "/recipient-access-checker", "/remove-tracking-from-url"]
    block = ('<section class="seo-safety-bridge" aria-labelledby="seo-safety-bridge-title"><h2 id="seo-safety-bridge-title">Checking a link you received?</h2><p>If the link was unexpected, review scam, phishing and malware-download warning signs before opening it.</p><ul><li><a href="/safe-link-checker">Safe Link Checker</a></li><li><a href="/scam-link-checker">Scam Link Checker</a></li><li><a href="/phishing-link-checker">Phishing Link Checker</a></li></ul></section>')
    for route in target_routes:
        path = route_file(route)
        if not path:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        if 'class="seo-safety-bridge"' in source:
            continue
        if '<section class="cta">' in source:
            source = source.replace('<section class="cta">', block + '\n<section class="cta">', 1)
        elif "</main>" in source:
            source = source.replace("</main>", block + "\n</main>", 1)
        else:
            source = source.replace("</body>", block + "\n</body>", 1)
        path.write_text(source, encoding="utf-8")


def inject_live_panel() -> None:
    for path in DIST.rglob("*.html"):
        source = path.read_text(encoding="utf-8", errors="replace")
        if 'id="cist-safety-v6-style"' not in source:
            source = source.replace("</head>", STYLE + "\n</head>", 1)
        if 'id="cist-safety-v6-script"' not in source:
            source = source.replace("</body>", SCRIPT + "\n</body>", 1)
        path.write_text(source, encoding="utf-8")


def main() -> None:
    patch_homepage()
    add_safety_bridges()
    inject_live_panel()
    print("Applied Link Safety V6.1 homepage scanner and Deep Safety Scan UI")


if __name__ == "__main__":
    main()
