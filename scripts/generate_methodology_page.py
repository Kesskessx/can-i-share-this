#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"
PATH = "/methodology"


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def json_ld(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_page() -> str:
    canonical = HOST + PATH
    title = "How Can I Share This? Checks Suspicious Links — Methodology"
    description = "See what Can I Share This? checks, how the risk score works, how redirects and reputation checks are handled, and what a safety verdict can and cannot prove."
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": HOST + "/"},
        "about": {"@type": "Thing", "name": "URL safety assessment methodology"},
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": "Methodology", "item": canonical},
        ],
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description, True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title, True)}"><meta property="og:description" content="{esc(description, True)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld(breadcrumb)}</script><script type="application/ld+json">{json_ld(webpage)}</script>
<style>
:root{{color-scheme:light dark;--bg:#f5f6f8;--card:#fff;--text:#17191d;--muted:#68707c;--line:#e2e6eb;--soft:#f8fafb;--accent:#111827;--accentText:#fff;--green:#137333;--amber:#9a5b00;--shadow:0 12px 34px rgba(17,24,39,.06)}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0d0f12;--card:#15181d;--text:#f3f4f6;--muted:#a6acb7;--line:#2a2f37;--soft:#111419;--accent:#f3f4f6;--accentText:#111318;--green:#75d18b;--amber:#ffc266;--shadow:0 14px 34px rgba(0,0,0,.22)}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit}}header{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}.nav{{max-width:1040px;margin:auto;padding:14px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}.button{{display:inline-flex;min-height:44px;align-items:center;justify-content:center;background:var(--accent);color:var(--accentText);padding:10px 16px;border-radius:12px;text-decoration:none;font-weight:780}}main{{max-width:900px;margin:auto;padding:42px 22px 76px}}.crumbs{{font-size:14px;color:var(--muted);margin-bottom:20px}}.kicker{{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 10px;color:var(--muted);font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(36px,7vw,62px);line-height:1.02;letter-spacing:-.047em;margin:14px 0 20px;text-wrap:balance}}.intro{{font-size:clamp(18px,2.6vw,21px);color:var(--muted);max-width:760px;margin:0 0 28px}}.summary{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 28px}}.summary div{{padding:18px;border:1px solid var(--line);border-radius:17px;background:var(--card)}}.summary strong{{display:block;font-size:14px;margin-bottom:4px}}.summary span{{display:block;color:var(--muted);font-size:13px}}.card{{margin:14px 0;padding:clamp(20px,3.5vw,30px);border:1px solid var(--line);border-radius:20px;background:var(--card);box-shadow:var(--shadow)}}h2{{font-size:clamp(22px,3.5vw,29px);line-height:1.18;letter-spacing:-.025em;margin:0 0 14px}}h3{{font-size:17px;margin:18px 0 7px}}p{{margin:0 0 15px}}p:last-child{{margin-bottom:0}}ul{{margin:10px 0 0;padding-left:21px}}li{{margin:7px 0}}.note{{border-left:3px solid var(--amber);padding-left:14px;color:var(--muted)}}.good{{color:var(--green);font-weight:780}}.cta{{margin-top:28px;padding:26px;border:1px solid var(--line);border-radius:22px;background:var(--card);text-align:center}}.cta h2{{margin-bottom:8px}}footer{{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:14px}}footer a{{text-underline-offset:3px}}@media(max-width:640px){{main{{padding:30px 16px 58px}}.nav{{padding:11px 16px}}.button{{padding:9px 12px;min-height:40px}}h1{{font-size:clamp(35px,11vw,48px)}}.summary{{grid-template-columns:1fr}}.card{{border-radius:17px}}}}
</style>
</head><body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main>
<div class="crumbs"><a href="/">Home</a> / Methodology</div>
<span class="kicker">Transparency</span>
<h1>How the link safety check works</h1>
<p class="intro">Can I Share This? is designed to help you spot warning signs before opening a suspicious URL. It combines observable URL and destination signals into a simple verdict, while clearly separating that first check from optional third-party reputation lookups.</p>
<div class="summary" aria-label="Method summary"><div><strong>1 · Inspect</strong><span>URL structure and suspicious patterns</span></div><div><strong>2 · Follow</strong><span>Redirects and final destination</span></div><div><strong>3 · Explain</strong><span>Risk signals and next action</span></div></div>
<section class="card"><h2>What the quick scan checks</h2><p>The first scan examines signals that can be evaluated without trusting the sender or using your signed-in browser session. Depending on the URL and response, the checker can look for:</p><ul><li>direct IP-address links, punycode and visually confusing hostnames;</li><li>shortened URLs and unusually complex subdomain structures;</li><li>brand-lookalike domains and phishing-style wording;</li><li>unexpected ports, insecure HTTP and suspicious login contexts;</li><li>executable, archive or forced-download indicators;</li><li>redirect chains, destination changes and basic response metadata.</li></ul><p class="note">A signal is evidence to inspect, not proof by itself. Legitimate sites can use redirects, long URLs or unusual infrastructure.</p></section>
<section class="card"><h2>How the risk score should be read</h2><p>Signals are combined into a risk score and a plain-language verdict. The score is <strong>not a probability that a site is malicious</strong>. It is a way to summarize the warning signs observed during this specific check.</p><p>A low-risk result means no obvious danger was found in the checks performed. A caution result means characteristics deserve verification. A high-risk result means the observed warning signs are strong enough that you should avoid opening the link and use the official site or app instead.</p></section>
<section class="card"><h2>Why the final destination matters</h2><p>The text shown in a message is not necessarily where a link ends. Shorteners, tracking systems and malicious redirectors can send a browser through several addresses before reaching the final host.</p><p>The result therefore highlights the <strong>final destination</strong> and, when relevant, shows that the host changed after redirects. A destination change is not automatically malicious, but it is important context when the message claims to come from a bank, delivery company, marketplace or other recognizable service.</p></section>
<section class="card"><h2>Optional reputation checks</h2><p>The quick scan and the external reputation check are deliberately separate. If you choose <strong>Check reputation</strong>, the interface asks for consent before a public URL is shared with supported external threat databases.</p><p>Private or signed links can contain access credentials inside their query parameters. The deep-check flow is designed to block known sensitive parameters instead of sending those URLs to an external reputation provider.</p></section>
<section class="card"><h2>Privacy by design</h2><p>Checks are performed without your browser session cookies. Product analytics are limited to interaction events such as opening the homepage, pasting, analyzing and starting a deep scan; the scanned URL itself is not included in those analytics events.</p><p>The QR-code scanner also keeps the image decoding in the browser on supported devices rather than uploading the screenshot to the scanning API.</p></section>
<section class="card"><h2>What the scanner cannot guarantee</h2><p>No URL checker can certify that a link is safe. A page can change after it was checked, a new phishing site may not yet appear in reputation databases, and previously unknown malware may evade existing defenses.</p><p>Can I Share This? is not a replacement for browser security warnings, endpoint protection, password managers, official apps or independent verification of an unexpected request. If a link asks for a password, payment, recovery phrase, identity document or one-time code, verify the destination independently even when the structural result is low risk.</p></section>
<section class="card"><h2>How to use the verdict</h2><p><span class="good">Low risk:</span> continue cautiously only if the link was expected. <strong>Caution:</strong> verify the sender and final domain before signing in, paying or downloading. <strong>High risk:</strong> do not open the link; reach the service through its official website or app.</p></section>
<section class="cta"><h2>Got a suspicious link?</h2><p>Paste it into the checker before you open it.</p><p><a class="button" href="/">Analyze the link</a></p></section>
</main>
<footer>Can I Share This? · <a href="/safe-link-checker">Safe Link Checker</a> · <a href="/privacy">Privacy</a></footer>
</body></html>'''


def update_sitemap() -> None:
    sitemap = DIST / "sitemap.xml"
    urls: set[str] = set()
    if sitemap.is_file():
        old = sitemap.read_text(encoding="utf-8", errors="replace")
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(HOST + (parsed.path.rstrip("/") or "/"))
    urls.add(HOST + "/")
    urls.add(HOST + PATH)
    entries = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding="utf-8")


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist/ does not exist; run this after the base build")
    (DIST / "methodology.html").write_text(render_page(), encoding="utf-8")
    update_sitemap()
    print("Generated transparent link safety methodology page")


if __name__ == "__main__":
    main()
