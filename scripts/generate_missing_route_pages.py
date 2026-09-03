#!/usr/bin/env python3
"""Generate previously-linked public routes so internal navigation never points to a 404."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"

STYLE = r'''
<style id="cist-route-repair-style">
:root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#6d7480;--line:#e2e5e9;--soft:#f1f3f5;--accent:#6578e8;--button:#17191d;--buttonText:#fff;--shadow:0 16px 46px rgba(17,24,39,.07)}
@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--soft:#1c2026;--accent:#8ea2ff;--button:#f4f5f7;--buttonText:#111318;--shadow:0 18px 48px rgba(0,0,0,.25)}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}a{color:inherit}.site-head{border-bottom:1px solid var(--line)}.site-head-inner{width:min(920px,calc(100% - 32px));min-height:64px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{text-decoration:none;font-weight:850;letter-spacing:-.025em}.brand-accent{color:var(--accent)}.home-link{font-size:13px;color:var(--muted);text-decoration:none}main{width:min(820px,calc(100% - 28px));margin:auto;padding:clamp(42px,8vw,78px) 0 70px}.eyebrow{margin:0 0 12px;color:var(--accent);font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}h1{font-size:clamp(36px,7vw,58px);line-height:1.02;letter-spacing:-.045em;margin:0 0 18px}.lead{font-size:clamp(17px,2vw,20px);color:var(--muted);max-width:720px;margin:0 0 28px}.cta{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 18px;border-radius:12px;background:var(--button);color:var(--buttonText);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:28px}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:var(--shadow)}.card.wide{grid-column:1/-1}.card h2{font-size:20px;line-height:1.25;margin:0 0 10px}.card h3{font-size:16px;margin:18px 0 6px}.card p{margin:0 0 12px;color:var(--muted)}.card p:last-child{margin-bottom:0}.card ul{margin:8px 0 0;padding-left:20px;color:var(--muted)}.card li+li{margin-top:7px}.related{margin-top:24px;padding-top:20px;border-top:1px solid var(--line);display:flex;gap:9px 16px;flex-wrap:wrap}.related a{font-size:13px;color:var(--muted);text-underline-offset:3px}.note{margin-top:20px;color:var(--muted);font-size:13px}.site-foot{width:min(820px,calc(100% - 28px));margin:0 auto 28px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12px;text-align:center}.site-foot a{color:var(--muted);text-underline-offset:3px}
@media(max-width:680px){.grid{grid-template-columns:1fr}.card.wide{grid-column:auto}.site-head-inner{min-height:58px}.home-link{display:none}}
</style>
'''

PAGES = {
    "/privacy": {
        "title": "Privacy and Data Handling — Can I Share This?",
        "description": "How Can I Share This? handles link checks, email checks, analytics and optional external reputation lookups.",
        "eyebrow": "Privacy",
        "h1": "Privacy by design, with clear limits",
        "lead": "Can I Share This? is designed to help you inspect suspicious links without requiring an account. This page explains what is processed during a check and when a URL may be shared with an external threat-intelligence provider.",
        "cta": ("/", "Open the checker"),
        "cards": [
            ("Quick link checks", [
                "When you submit a public HTTP or HTTPS link, the server analyzes the URL and may fetch the destination to inspect redirects, reachability and basic warning signs. The application is designed not to store the scanned URL in its own scan-history database.",
                "Quick Check does not automatically send the pasted URL to an external reputation database. It evaluates the signals implemented by Can I Share This? first."
            ]),
            ("Optional reputation checks", [
                "The external reputation check requires an explicit confirmation in the interface. When you continue, the public URL may be submitted to configured providers such as Google Web Risk or PhishTank so they can return known-threat information.",
                "If the URL appears to contain a token, signature, session identifier or another sensitive-looking query parameter, the Deep Scan is designed to block the external lookup instead of forwarding that URL."
            ]),
            ("Email checks", [
                "If you paste an email address, the service can inspect its format and domain-level signals. The checker is intended for safety analysis, not for building a contact list or requiring an account.",
                "Do not paste passwords, one-time codes, private messages or other secrets into the checker."
            ]),
            ("Analytics and telemetry", [
                "The site uses Vercel Web Analytics for aggregate page-view and visitor analytics. The application also has anonymous product telemetry for events such as opening the homepage or starting an analysis.",
                "The custom scan telemetry is designed not to include the scanned URL or hostname. Hosting and security infrastructure may still process ordinary request metadata needed to deliver and protect the service."
            ]),
            ("What we do not promise", [
                "No internet service can promise that infrastructure providers retain zero operational metadata. The privacy claims on this site refer to the application's intended behavior and the data it deliberately sends to its own telemetry endpoints.",
                "No scanner can guarantee that a link, sender or website is safe. New and targeted threats may not yet appear in reputation databases."
            ]),
            ("Questions", [
                "For a private or signed share link, avoid Deep Scan unless you are comfortable sharing the URL with external reputation providers. For the most privacy-sensitive case, use the local warning-sign result and verify the sender through another trusted channel.",
                "Last updated: September 2, 2026."
            ]),
        ],
        "related": [("/methodology", "Methodology"), ("/safe-link-checker", "Safe Link Checker")],
    },
    "/privacy-link-checker": {
        "title": "Link Privacy Checker — Check a URL Before You Share It",
        "description": "Review a link for privacy-sensitive URL parameters, redirects and sharing risks before you forward it to someone else.",
        "eyebrow": "Link privacy",
        "h1": "Check a link before you share it",
        "lead": "Share links can expose more than the page you intended. Long query strings may contain tracking parameters, signed access data or session-like tokens. Use the checker to review the destination and warning signs before forwarding a URL.",
        "cta": ("/", "Check this link"),
        "cards": [
            ("What to look for", [
                "Review the final destination after redirects, especially when the visible link is shortened or comes from a message you did not expect.",
                "Pay extra attention to parameters with names such as token, signature, session, credential or secret. A parameter name alone does not prove that the value is sensitive, but it is a reason not to repost the link publicly."
            ]),
            ("Deep Scan privacy protection", [
                "Can I Share This? separates its first-party warning-sign analysis from external reputation checks. The external check only runs after you confirm that the public URL may be shared with threat-intelligence providers.",
                "The Deep Scan includes a guard that refuses URLs containing several common token- or signature-like parameter names. This reduces accidental disclosure, but it cannot recognize every private-link format."
            ]),
            ("Tracking parameters", [
                "Marketing parameters such as UTM tags are often harmless but can reveal campaign or referral information when a URL is forwarded. Removing unnecessary tracking can make a shared link cleaner and easier to inspect.",
                "Use the tracking-removal tool for ordinary analytics parameters, but do not delete parameters from signed or authenticated links unless you understand what they do; changing them may break access."
            ]),
            ("Important limitation", [
                "A privacy check cannot determine every piece of information that a destination will collect after you open it. Cookies, browser fingerprinting, account state and scripts on the destination are separate from what is visible in the URL itself.",
                "If a link grants access to a private document, use the sharing controls of the original service instead of relying only on the URL text."
            ]),
        ],
        "related": [("/remove-tracking-from-url", "Remove tracking from URL"), ("/safe-link-checker", "Safe Link Checker"), ("/privacy", "Privacy")],
    },
    "/recipient-access-checker": {
        "title": "Recipient Access Checker — Will This Link Open for Someone Else?",
        "description": "Check whether a public link resolves, redirects or appears to require login before you send it to someone else.",
        "eyebrow": "Recipient access",
        "h1": "Will this link open for the recipient?",
        "lead": "A link that works for you may depend on your existing login or permissions. Can I Share This? can inspect public reachability, redirects and some login-wall signals before you send the link.",
        "cta": ("/", "Check the link"),
        "cards": [
            ("What the checker can tell you", [
                "The link checker can follow public redirects, report the final hostname, show the website response and flag some pages that appear to require authentication or permission.",
                "This is useful for catching broken destinations, unexpected redirect chains and obvious login walls before you share a link."
            ]),
            ("What it cannot simulate", [
                "The checker does not log in as your recipient and cannot know their Google, Microsoft, Dropbox, Notion or company-account permissions.",
                "A successful HTTP response also does not prove that another person has permission to view the same document. Always verify the sharing setting in the service that created the link."
            ]),
            ("For cloud-storage links", [
                "For Google Drive or Dropbox, confirm whether the item is restricted, shared with named accounts, or available to anyone with the link. Use the provider's own sharing dialog as the source of truth.",
                "If the link contains a signed token or access credential, avoid posting it publicly and avoid external reputation checks unless you understand what information the URL contains."
            ]),
            ("A practical pre-send check", [
                "Paste the URL into Can I Share This?, inspect the final destination, then open the provider's sharing controls. If the recipient still reports an access problem, ask them for the exact error rather than repeatedly generating new public links.",
                "The tool is a pre-send diagnostic, not a substitute for the destination service's authorization system."
            ]),
        ],
        "related": [("/google-drive-link-checker", "Google Drive link checker"), ("/dropbox-link-checker", "Dropbox link checker"), ("/privacy-link-checker", "Link Privacy Checker")],
    },
}


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def render(path: str, page: dict) -> str:
    canonical = HOST + path
    cards = []
    for title, paragraphs in page["cards"]:
        body = "".join(f"<p>{esc(p)}</p>" for p in paragraphs)
        cards.append(f'<section class="card"><h2>{esc(title)}</h2>{body}</section>')
    related = "".join(f'<a href="{esc(href, True)}">{esc(label)}</a>' for href, label in page["related"])
    cta_href, cta_label = page["cta"]
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'], True)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(page['title'], True)}"><meta property="og:description" content="{esc(page['description'], True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary">
{STYLE}
</head>
<body>
<header class="site-head"><div class="site-head-inner"><a class="brand" href="/">Can I Share <span class="brand-accent">This?</span></a><a class="home-link" href="/">Link checker</a></div></header>
<main>
<p class="eyebrow">{esc(page['eyebrow'])}</p>
<h1>{esc(page['h1'])}</h1>
<p class="lead">{esc(page['lead'])}</p>
<a class="cta" href="{esc(cta_href, True)}">{esc(cta_label)}</a>
<div class="grid">{''.join(cards)}</div>
<nav class="related" aria-label="Related resources">{related}</nav>
<p class="note">No scanner can guarantee that a link or sender is safe.</p>
</main>
<footer class="site-foot">Can I Share This? · <a href="/privacy">Privacy</a> · <a href="/methodology">Methodology</a></footer>
</body>
</html>'''


def add_to_sitemap(paths: list[str]) -> None:
    sitemap = DIST / "sitemap.xml"
    if not sitemap.is_file():
        return
    text = sitemap.read_text(encoding="utf-8")
    additions = []
    for path in paths:
        loc = f"{HOST}{path}"
        if loc not in text:
            additions.append(f"  <url><loc>{loc}</loc></url>")
    if additions:
        if "</urlset>" in text:
            text = text.replace("</urlset>", "\n" + "\n".join(additions) + "\n</urlset>", 1)
        else:
            raise RuntimeError("sitemap.xml has no closing urlset tag")
        sitemap.write_text(text, encoding="utf-8")


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist directory not found")
    for path, page in PAGES.items():
        target = DIST / f"{path.lstrip('/')}.html"
        target.write_text(render(path, page), encoding="utf-8")
    add_to_sitemap(list(PAGES))
    print(f"Generated {len(PAGES)} repaired public routes: " + ", ".join(PAGES))


if __name__ == "__main__":
    main()
