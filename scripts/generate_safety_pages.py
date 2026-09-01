#!/usr/bin/env python3
"""Generate the public Link Safety V6 SEO cluster and add it to the sitemap."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"

PAGES = [
    {
        "path": "/safe-link-checker",
        "title": "Safe Link Checker — Check a Link Before You Open or Share It",
        "description": "Check a link for suspicious URL patterns, lookalike domains, redirects, shortened URLs and risky downloads before you open or share it.",
        "h1": "Check a Link Before You Open or Share It",
        "kicker": "Link safety",
        "lead": [
            "A link can load correctly and still be risky. Can I Share This? checks the URL and its redirect path for common warning signs before you open it, sign in, pay, download a file, or forward it to someone else.",
            "The result is a risk assessment, not a guarantee. A new phishing or malware page can exist before any reputation database knows about it, so a clean-looking result should never override common sense or a warning from your browser or security software."
        ],
        "sections": [
            ("What the safety check looks for", [
                "The checker reviews signals that can be evaluated without trusting the sender's browser session: direct IP-address links, punycode domains, shortened URLs, unusually deep subdomains, brand-lookalike hostnames, suspicious account or payment wording, multiple redirects, destination-domain changes, and direct executable or archive downloads.",
                "These signals are combined into a risk score so one weak indicator does not automatically label a link as malicious. A shortened URL, for example, is not inherently dangerous; it simply hides the destination and deserves extra attention."
            ]),
            ("What a low-risk result actually means", [
                "A low-risk result means the checker did not find obvious suspicious URL patterns in the checks it performed. It does not mean the site is certified safe, virus-free, legitimate, or trustworthy.",
                "If the link asks for a password, card number, recovery phrase, identity document, or payment, verify the domain independently. For unexpected messages, contact the sender through a channel you already trust instead of replying through the suspicious link."
            ]),
            ("What to do with a caution or high-risk result", [
                "Stop before entering information or running a downloaded file. Read the exact warning, inspect the final hostname after redirects, and compare it with the official website you expected to reach.",
                "For a brand or bank, open the official app or type the known website address yourself. Do not use a login or payment page simply because the message creating the urgency looks convincing."
            ]),
            ("Privacy-first by default", [
                "The built-in safety analysis is performed by Can I Share This? without automatically submitting the pasted URL to a third-party reputation scanner. That matters because private share links can contain access tokens or other sensitive parameters.",
                "The safety result clearly distinguishes local risk signals from external reputation checks. If no external reputation source was queried, the interface says so instead of pretending that the link was checked against every known threat database."
            ])
        ],
        "faqs": [
            ("Can a link be dangerous even if it uses HTTPS?", "Yes. HTTPS encrypts the connection to the domain, but a phishing site can also use HTTPS. Always verify where the link actually leads."),
            ("Does a low-risk result mean the link has no virus?", "No. The checker looks for observable risk signals. It cannot guarantee that a page or download is free of malware."),
            ("Should I open a shortened link?", "A short link is not automatically malicious, but it hides the destination. Check where it redirects before entering credentials or downloading anything."),
            ("Do you send my private link to VirusTotal?", "No. The default Link Safety analysis does not automatically submit pasted URLs to third-party reputation services."),
        ],
        "related": [
            ("/scam-link-checker", "Scam Link Checker", "Review scam-oriented warning signs before paying or responding."),
            ("/phishing-link-checker", "Phishing Link Checker", "Check login and brand-impersonation warning signs."),
            ("/privacy-link-checker", "Link Privacy Checker", "Review tracking and privacy signals before sharing."),
            ("/recipient-access-checker", "Recipient Access Checker", "Check whether another person is likely to open the link."),
        ],
    },
    {
        "path": "/scam-link-checker",
        "title": "Scam Link Checker — Check Suspicious Links Before You Click",
        "description": "Check a suspicious link for scam warning signs such as lookalike domains, payment language, shortened URLs, redirects and risky downloads.",
        "h1": "Check a Suspicious Link for Scam Warning Signs",
        "kicker": "Scam links",
        "lead": [
            "Unexpected delivery fees, account warnings, prizes, invoices and payment requests often arrive with a link designed to create urgency. Paste the URL into Can I Share This? before clicking through or entering information.",
            "The checker highlights suspicious URL patterns and redirect behavior. It does not decide whether a person or company is honest, and it cannot guarantee that an unflagged link is legitimate."
        ],
        "sections": [
            ("Common scam-link patterns", [
                "Scam links often imitate a recognizable company while using a different domain, hide the destination behind a shortener, or place words such as verify, payment, parcel, billing, account, unlock or claim inside the hostname and path.",
                "No single keyword proves fraud. The safety score becomes more useful when several independent signals appear together, such as a brand lookalike plus an account-verification path plus an unexpected executable download."
            ]),
            ("Check the final domain, not the message text", [
                "The sender name in an SMS, email or chat can be misleading. A logo and professional-looking page can also be copied. The domain after redirects is a stronger clue because it shows where your browser would actually connect.",
                "If a message claims to be from a delivery company, marketplace, bank or subscription service, compare the final domain with the official site you already know. When in doubt, open the official app independently."
            ]),
            ("Payment and identity requests deserve extra caution", [
                "A small delivery charge, refundable verification payment, urgent invoice or account-recovery request can be used to collect card details or credentials. Do not let the amount or urgency make the link seem automatically harmless.",
                "Never provide recovery phrases, one-time codes, passwords or card data merely because a link passed a structural check. The checker helps you spot warning signs; it cannot authenticate the person who sent the message."
            ])
        ],
        "faqs": [
            ("Can you tell me with certainty whether a link is a scam?", "No. The tool can identify suspicious technical and URL signals, but intent and legitimacy cannot always be determined from a link alone."),
            ("Why are shortened URLs marked for caution?", "They hide the destination until a redirect occurs. That makes it harder to judge the real domain from the message itself."),
            ("What should I do if the link looks like my bank?", "Do not sign in through the message. Open the bank's official app or type its known address independently."),
            ("Can a real company use a complicated tracking link?", "Yes. Legitimate marketing and authentication flows can produce long or redirected URLs, which is why individual signals are not treated as proof of fraud."),
        ],
        "related": [
            ("/safe-link-checker", "Safe Link Checker", "Run the broader safety assessment."),
            ("/phishing-link-checker", "Phishing Link Checker", "Focus on credential and login risks."),
            ("/remove-tracking-from-url", "Remove Tracking From a URL", "Clean unnecessary tracking parameters before sharing."),
        ],
    },
    {
        "path": "/phishing-link-checker",
        "title": "Phishing Link Checker — Check Login and Lookalike URL Risks",
        "description": "Check a link for phishing warning signs including lookalike brand domains, suspicious login wording, punycode, redirects and insecure authentication pages.",
        "h1": "Check a Link for Phishing Warning Signs",
        "kicker": "Phishing",
        "lead": [
            "Phishing pages try to make a fake destination look familiar enough that you enter a password, payment detail or recovery code. Can I Share This? checks the URL and redirect path for technical warning signs before you trust the page.",
            "A phishing page can be brand new and visually convincing, so the absence of a warning is never permission to ignore an unexpected request for sensitive information."
        ],
        "sections": [
            ("Lookalike domains are more important than the logo", [
                "A page can copy a company's colors, logo and login layout in minutes. The hostname is harder to fake without using a different domain, a deceptive subdomain or an internationalized lookalike.",
                "The checker flags known brand names appearing on domains that are not recognized as the brand's normal domains. This is a heuristic: it is designed to make you inspect the domain, not to issue a legal conclusion about ownership."
            ]),
            ("Login pages need context", [
                "A login form is normal on many legitimate sites. Risk increases when authentication appears on an unencrypted HTTP page, after an unexpected chain of redirects, or on a domain that does not match the service you expected.",
                "If the message says your account is suspended, payment failed, or identity must be verified immediately, open the service independently rather than using the message link."
            ]),
            ("What the checker cannot see", [
                "A URL-only assessment cannot prove what a page will do tomorrow, whether a downloaded file contains previously unknown malware, or whether the sender's story is genuine. Dynamic attacks can also change content by country, device or time.",
                "Use the safety verdict as one decision input. Browser warnings, endpoint security, password managers, official apps and independent verification remain important layers of protection."
            ])
        ],
        "faqs": [
            ("What is a punycode domain?", "It is an ASCII representation used for internationalized domain names. It is legitimate technology, but it can also be used to create visually confusing lookalikes."),
            ("Is every login link phishing?", "No. Login pages are common. The tool looks for combinations of signals rather than treating authentication alone as malicious."),
            ("Can HTTPS phishing sites exist?", "Yes. HTTPS proves that the connection is encrypted to that domain; it does not prove that the domain belongs to the company you intended to visit."),
            ("Should I enter a one-time code after checking the link?", "Only if you independently trust the destination and initiated the authentication flow. A clean structural result is not proof that a request for a code is legitimate."),
        ],
        "related": [
            ("/safe-link-checker", "Safe Link Checker", "Run the broader link-safety assessment."),
            ("/scam-link-checker", "Scam Link Checker", "Review scam and payment-warning signals."),
            ("/privacy-link-checker", "Link Privacy Checker", "Check whether the URL exposes unnecessary parameters."),
        ],
    },
]


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def json_ld(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_page(page: dict) -> str:
    canonical = HOST + page["path"]
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": "Link Safety", "item": HOST + "/safe-link-checker"},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": canonical},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["title"],
        "description": page["description"],
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": HOST + "/"},
        "about": {"@type": "Thing", "name": "Link safety and phishing risk assessment"},
    }
    lead = "".join(f"<p>{esc(p)}</p>" for p in page["lead"])
    sections = "".join('<section class="card">' + f'<h2>{esc(title)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in paragraphs) + "</section>" for title, paragraphs in page["sections"])
    faqs = "".join(f'<article class="faq"><h3>{esc(q)}</h3><p>{esc(a)}</p></article>' for q, a in page["faqs"])
    related = "".join(f'<a class="related" href="{esc(href, True)}"><strong>{esc(label)}</strong><span>{esc(desc)}</span><b aria-hidden="true">→</b></a>' for href, label, desc in page["related"])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'], True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(page['title'], True)}"><meta property="og:description" content="{esc(page['description'], True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld(breadcrumb)}</script><script type="application/ld+json">{json_ld(webpage)}</script>
<style>
:root{{color-scheme:light dark;--bg:#f5f6f8;--card:#fff;--text:#17191d;--muted:#68707c;--line:#e2e6eb;--soft:#f8fafb;--accent:#111827;--accentText:#fff;--warn:#9a6700;--shadow:0 12px 34px rgba(17,24,39,.06)}}@media(prefers-color-scheme:dark){{:root{{--bg:#0d0f12;--card:#15181d;--text:#f3f4f6;--muted:#a6acb7;--line:#2a2f37;--soft:#111419;--accent:#f3f4f6;--accentText:#111318;--warn:#f0b429;--shadow:0 14px 34px rgba(0,0,0,.22)}}}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit}}header{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}.nav{{max-width:1040px;margin:auto;padding:14px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}.button{{display:inline-flex;min-height:44px;align-items:center;justify-content:center;background:var(--accent);color:var(--accentText);padding:10px 16px;border-radius:12px;text-decoration:none;font-weight:780}}main{{max-width:900px;margin:auto;padding:42px 22px 76px}}.crumbs{{font-size:14px;color:var(--muted);margin-bottom:20px}}.kicker{{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 10px;color:var(--muted);font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(34px,7vw,60px);line-height:1.02;letter-spacing:-.045em;margin:14px 0 24px;text-wrap:balance}}.lead{{padding:clamp(22px,4vw,34px);border:1px solid var(--line);border-radius:22px;background:var(--card);box-shadow:var(--shadow);margin-bottom:18px}}.lead:before{{content:"Safety note";display:block;color:var(--warn);font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px}}.lead p{{font-size:clamp(17px,2.5vw,20px)}}p{{margin:0 0 15px}}p:last-child{{margin-bottom:0}}.card{{margin:14px 0;padding:clamp(20px,3.5vw,30px);border:1px solid var(--line);border-radius:20px;background:var(--card)}}h2{{font-size:clamp(22px,3.5vw,29px);line-height:1.18;letter-spacing:-.025em;margin:0 0 14px}}.section-title{{margin:38px 0 14px}}.section-title span{{color:var(--muted);font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}.section-title h2{{margin:3px 0 0;font-size:clamp(26px,4vw,34px)}}.faq{{margin:10px 0;padding:20px 22px;border:1px solid var(--line);border-radius:17px;background:var(--card)}}.faq h3{{font-size:18px;line-height:1.3;margin:0 0 8px}}.related-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.related{{position:relative;display:flex;flex-direction:column;gap:5px;min-height:124px;padding:18px 44px 18px 18px;border:1px solid var(--line);border-radius:17px;background:var(--card);text-decoration:none}}.related span{{color:var(--muted);font-size:14px}}.related b{{position:absolute;right:18px;top:18px}}.cta{{margin-top:34px;padding:26px;border:1px solid var(--line);border-radius:22px;background:var(--card);text-align:center}}.cta h2{{margin:0 0 8px}}footer{{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:14px}}@media(max-width:640px){{main{{padding:30px 16px 58px}}.nav{{padding:11px 16px}}.button{{padding:9px 12px;min-height:40px}}h1{{font-size:clamp(34px,11vw,47px)}}.lead,.card{{border-radius:17px}}.related-grid{{grid-template-columns:1fr}}.related{{min-height:0}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style></head><body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main><div class="crumbs"><a href="/">Home</a> / <a href="/safe-link-checker">Link Safety</a></div><span class="kicker">{esc(page['kicker'])}</span><h1>{esc(page['h1'])}</h1><section class="lead">{lead}</section>{sections}<div class="section-title"><span>Questions</span><h2>Frequently asked questions</h2></div><section>{faqs}</section><div class="section-title"><span>Keep checking</span><h2>Related checks</h2></div><nav class="related-grid" aria-label="Related link checks">{related}</nav><section class="cta"><h2>Got a suspicious link?</h2><p>Paste it into Can I Share This? before you open or forward it.</p><p><a class="button" href="/">Check the link</a></p></section></main><footer>Can I Share This? · Check before you open or share</footer></body></html>'''


def write_pages() -> None:
    for page in PAGES:
        target = DIST / f"{page['path'].strip('/')}.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(page), encoding="utf-8")


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
    for page in PAGES:
        urls.add(HOST + page["path"])
    entries = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding="utf-8")


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist/ does not exist; run this after the base build")
    write_pages()
    update_sitemap()
    print(f"Generated {len(PAGES)} Link Safety V6 SEO pages")


if __name__ == "__main__":
    main()
