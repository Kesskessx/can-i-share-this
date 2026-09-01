#!/usr/bin/env python3
"""Apply Link Safety V6 positioning and the live safety-result panel to built HTML."""

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
#cist-safety-result{max-width:820px;margin:24px auto;padding:0 16px;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:inherit}
.cist-safety-card{border:1px solid rgba(127,127,127,.28);border-radius:18px;padding:20px;background:rgba(127,127,127,.06)}
.cist-safety-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:14px}.cist-safety-title{display:flex;gap:10px;align-items:center}.cist-safety-icon{font-size:24px}.cist-safety-title h2{font-size:22px;line-height:1.2;margin:0}.cist-safety-sub{font-size:13px;opacity:.7;margin-top:4px}.cist-safety-badge{white-space:nowrap;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:800;border:1px solid currentColor}
.cist-safety-low .cist-safety-badge{color:#137333}.cist-safety-caution .cist-safety-badge{color:#a15c00}.cist-safety-high .cist-safety-badge{color:#b3261e}.cist-safety-unknown .cist-safety-badge{opacity:.7}
.cist-safety-score{font-size:14px;margin:0 0 14px;opacity:.82}.cist-safety-signals{display:grid;gap:9px;margin:0;padding:0;list-style:none}.cist-safety-signals li{padding:11px 12px;border-radius:12px;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.18)}.cist-safety-signals strong{display:block;font-size:14px;margin-bottom:2px}.cist-safety-signals span{font-size:13px;opacity:.78}.cist-safety-note{margin:14px 0 0;font-size:12px;line-height:1.5;opacity:.72}.cist-safety-more{display:inline-block;margin-top:14px;font-size:13px;font-weight:750;text-underline-offset:3px}
#seo-safety-checks{max-width:980px;margin:28px auto;padding:24px;border:1px solid rgba(127,127,127,.25);border-radius:18px}#seo-safety-checks h2{margin-top:0}.seo-safety-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.seo-safety-card{display:block;padding:16px;border:1px solid rgba(127,127,127,.23);border-radius:14px;text-decoration:none}.seo-safety-card strong{display:block;margin-bottom:5px}.seo-safety-card span{display:block;font-size:14px;opacity:.72}
.seo-safety-bridge{margin:22px 0;padding:18px;border:1px solid rgba(127,127,127,.23);border-radius:16px}.seo-safety-bridge h2{margin-top:0}.seo-safety-bridge ul{margin-bottom:0}
@media(max-width:680px){.cist-safety-head{flex-direction:column}.seo-safety-grid{grid-template-columns:1fr}#seo-safety-checks{margin:20px 16px;padding:18px}.cist-safety-card{padding:17px}}
</style>
'''

SCRIPT = r'''
<script id="cist-safety-v6-script">
(function(){
  if(window.__cistSafetyV6Installed)return;
  window.__cistSafetyV6Installed=true;
  var nativeFetch=window.fetch;
  if(typeof nativeFetch!=="function")return;
  function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]})}
  function render(data){
    if(!data||!data.safety)return;
    var s=data.safety;
    var host=document.querySelector("main")||document.body;
    var root=document.getElementById("cist-safety-result");
    if(!root){root=document.createElement("section");root.id="cist-safety-result";root.setAttribute("aria-live","polite");host.appendChild(root)}
    var status=["low","caution","high","unknown"].indexOf(s.status)>=0?s.status:"unknown";
    var badge=status==="low"?"Low observed risk":status==="caution"?"Caution":status==="high"?"High risk signals":"Unknown";
    var signals=Array.isArray(s.signals)?s.signals:[];
    var list=signals.length?'<ul class="cist-safety-signals">'+signals.map(function(x){return '<li><strong>'+esc(x.title||"Signal detected")+'</strong><span>'+esc(x.detail||"")+'</span></li>'}).join("")+'</ul>':'<ul class="cist-safety-signals"><li><strong>No obvious suspicious URL patterns found</strong><span>This does not certify the destination as safe or malware-free.</span></li></ul>';
    var rep=s.reputation&&s.reputation.reason?s.reputation.reason:"No external reputation result is available.";
    root.className="cist-safety-"+status;
    root.innerHTML='<div class="cist-safety-card"><div class="cist-safety-head"><div class="cist-safety-title"><span class="cist-safety-icon" aria-hidden="true">🛡️</span><div><h2>Safety</h2><div class="cist-safety-sub">'+esc(s.verdict||"Link risk assessment")+'</div></div></div><span class="cist-safety-badge">'+esc(badge)+'</span></div><p class="cist-safety-score">Observed risk score: <strong>'+esc(Number.isFinite(s.riskScore)?s.riskScore:0)+'/100</strong></p>'+list+'<p class="cist-safety-note">'+esc(rep)+' '+esc(s.disclaimer||"")+'</p><a class="cist-safety-more" href="/safe-link-checker">How the safety check works →</a></div>';
  }
  window.fetch=function(){
    var args=arguments;
    var target="";
    try{target=typeof args[0]==="string"?args[0]:(args[0]&&args[0].url)||""}catch(e){}
    return nativeFetch.apply(this,args).then(function(response){
      try{
        if(/\/api\/check(?:\?|$)/.test(String(target))){
          response.clone().json().then(render).catch(function(){})
        }
      }catch(e){}
      return response;
    })
  };
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
    source = re.sub(r"<title>.*?</title>", "<title>Can I Share This? — Check Link Access, Privacy, Safety & Expiration</title>", source, count=1, flags=re.I | re.S)
    description = "Check a link before you open or share it. Review recipient access, suspicious scam and phishing signals, privacy risks and expiration before you click or send."
    meta = f'<meta name="description" content="{html.escape(description, quote=True)}">'
    if re.search(r'<meta\s+name=["\']description["\'][^>]*>', source, flags=re.I):
        source = re.sub(r'<meta\s+name=["\']description["\'][^>]*>', meta, source, count=1, flags=re.I)
    else:
        source = source.replace("</head>", meta + "\n</head>", 1)
    source = re.sub(r"BEFORE\s+YOU\s+SHARE", "BEFORE YOU OPEN OR SHARE", source, flags=re.I)
    source = re.sub(r"Will it open\?\s*Is it private\?\s*Will it expire\?", "Will it open? Is it private? Is it safe? Will it expire?", source, flags=re.I)
    if 'id="seo-safety-checks"' not in source:
        cards = "".join(f'<a class="seo-safety-card" href="{href}"><strong>{html.escape(label)}</strong><span>{html.escape(desc)}</span></a>' for href, label, desc in SAFETY_LINKS)
        block = ('<section id="seo-safety-checks" aria-labelledby="seo-safety-title"><h2 id="seo-safety-title">Got a suspicious link?</h2><p>Paste it into the checker before you open, sign in, pay, download, or forward it. The safety verdict looks for common scam and phishing warning signs without automatically sending private URLs to third-party scanners.</p>' + f'<div class="seo-safety-grid">{cards}</div></section>')
        source = source.replace("</main>", block + "\n</main>", 1) if "</main>" in source else source.replace("</body>", block + "\n</body>", 1)
    path.write_text(source, encoding="utf-8")


def add_safety_bridges() -> None:
    target_routes = ["/google-drive-link-checker", "/dropbox-link-checker", "/drive-vs-dropbox-share-link-checker", "/privacy-link-checker", "/recipient-access-checker", "/remove-tracking-from-url"]
    block = ('<section class="seo-safety-bridge" aria-labelledby="seo-safety-bridge-title"><h2 id="seo-safety-bridge-title">Checking a link you received?</h2><p>Access and privacy are only part of the decision. If the link was unexpected, review its scam and phishing warning signs before opening it.</p><ul><li><a href="/safe-link-checker">Safe Link Checker</a></li><li><a href="/scam-link-checker">Scam Link Checker</a></li><li><a href="/phishing-link-checker">Phishing Link Checker</a></li></ul></section>')
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
    print("Applied Link Safety V6 positioning and live safety panel")


if __name__ == "__main__":
    main()
