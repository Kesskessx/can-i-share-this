#!/usr/bin/env python3
# Generate five citation-friendly authority pages for the link-safety knowledge cluster.

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"
UPDATED = "2026-09-02"

AUTHORITY_PATHS = [
    "/how-link-scanning-works",
    "/phishing-url-signals",
    "/lookalike-domain-examples",
    "/redirect-risk-explained",
    "/shortened-url-risks",
]

PAGES = [
    {
        "path": "/how-link-scanning-works",
        "title": "How Link Scanning Works: URL, Redirect and Risk Checks",
        "description": "A technical but practical explanation of how link scanners inspect URL structure, redirects, destination domains, downloads and reputation signals.",
        "h1": "How link scanning works",
        "kicker": "Link safety reference",
        "quick": "A useful link scan does more than ask whether a page loads. It parses the URL, follows a bounded redirect chain, inspects the final destination and response, and combines multiple warning signs into a risk assessment. A scan can reduce uncertainty, but it cannot certify that a destination is safe.",
        "points": [
            "The visible link and the final destination may be different.",
            "URL structure, domain identity, redirects and download behavior are separate signals.",
            "One weak signal should not be treated as proof of malicious intent.",
            "A low-risk result means no obvious warning signs were found in the checks performed, not that the site is guaranteed safe.",
        ],
        "sections": [
            ("1. Parse the URL before making a network request", [
                "A scanner first separates the scheme, hostname, port, path, query and fragment. This matters because the hostname identifies the network destination while words placed elsewhere in the URL can be visually distracting. The generic URI syntax standardized in RFC 3986 is the foundation for interpreting those components.",
                "Can I Share This? rejects non-HTTP(S) destinations and credential-bearing URLs. It also checks structural signals such as direct IP-address hosts, punycode, unusually deep subdomains, uncommon ports, heavy percent-encoding and very long URLs. None of those signals alone proves abuse."
            ]),
            ("2. Resolve the destination and follow redirects", [
                "The address shown in a message is not always the address that ultimately loads. URL shorteners, analytics platforms, authentication systems and malicious redirectors can all send a browser through one or more intermediate URLs.",
                "The scanner follows a bounded redirect chain and records destination changes. It then highlights the final hostname so the user can compare it with the service or organization they expected. A domain change is context, not an automatic verdict: legitimate services also redirect between domains."
            ]),
            ("3. Inspect the response without using your signed-in browser session", [
                "The quick scan requests the destination from the server side rather than opening it inside the user's authenticated browser. It can inspect basic response metadata, identify certain forced downloads or binary responses, and look for simple signs that a page is asking for authentication.",
                "This separation is important. A server-side check does not inherit the user's cookies or logged-in state, so it cannot reproduce every personalized page or account-specific flow. Dynamic content can also vary by geography, device, time or request headers."
            ]),
            ("4. Combine signals instead of relying on one rule", [
                "Useful detection is multi-signal. A shortened URL is common and often legitimate. A login page is common and often legitimate. A redirect is common and often legitimate. Risk becomes more meaningful when independent signals reinforce one another, such as a brand-lookalike hostname combined with account-verification wording and an unexpected executable download.",
                "Can I Share This? converts observed warning signs into a risk score and plain-language status. The score is not a probability that a site is malicious. It is a summary of the signals found during that scan."
            ]),
            ("5. Keep structural checks separate from reputation checks", [
                "A reputation service asks whether a URL or destination is already known to threat-intelligence systems. That is different from examining the structure and behavior of the link itself. New malicious pages can exist before reputation databases have seen them.",
                "Can I Share This? keeps the optional reputation lookup separate because private sharing links may contain access tokens or sensitive query parameters. The quick scan does not pretend that a URL was checked against every external threat database when it was not."
            ]),
            ("What a scanner cannot prove", [
                "A scanner cannot guarantee that a page will remain unchanged, that a download contains no previously unknown malware, or that the person who sent the link is trustworthy. It also cannot infer business legitimacy from URL structure alone.",
                "For unexpected requests involving passwords, one-time codes, payment details, identity documents or recovery phrases, verify the destination independently even when the technical result appears low risk."
            ]),
        ],
        "sources": [
            ("RFC 3986 — URI Generic Syntax", "https://www.rfc-editor.org/info/rfc3986/"),
            ("WHATWG URL Standard", "https://url.spec.whatwg.org/"),
            ("CISA — Secure Our World", "https://www.cisa.gov/secure-our-world"),
        ],
        "related": ["/phishing-url-signals", "/redirect-risk-explained", "/shortened-url-risks", "/methodology"],
    },
    {
        "path": "/phishing-url-signals",
        "title": "Phishing URL Signals: What to Check Before You Click",
        "description": "Learn which URL signals can indicate phishing, which clues are weak by themselves, and how to verify the real destination before entering credentials.",
        "h1": "Phishing URL signals",
        "kicker": "Phishing reference",
        "quick": "The strongest phishing clues usually come from combinations: an unexpected message, a hostname that does not belong to the claimed service, credential or payment pressure, and redirects to an unfamiliar destination. HTTPS or a professional-looking page does not prove legitimacy.",
        "points": [
            "Read the hostname, not just the words around it.",
            "Urgency and account language are contextual clues, not proof by themselves.",
            "HTTPS encrypts a connection; it does not authenticate the sender's story.",
            "Unexpected requests for credentials or payment deserve independent verification.",
        ],
        "sections": [
            ("Start with the hostname", [
                "The hostname is the part of a web address that identifies the destination host. Attackers can place trusted-looking words in subdomains, paths or query parameters, so the presence of a brand name somewhere in the URL is not enough.",
                "A practical check is to identify the registrable domain you are actually visiting and compare it with the official domain you expected. Can I Share This? also flags some cases where a recognizable brand name appears in a hostname that is not one of the service's recognized domains."
            ]),
            ("Lookalikes, punycode and visual confusion", [
                "Internationalized Domain Names are legitimate and allow domain names in many languages and scripts. Browsers may represent some of them in an ASCII form beginning with xn--, commonly called punycode.",
                "Because different characters can look similar, internationalized names can also be abused for visual impersonation. Punycode is therefore a reason to inspect a hostname carefully, not evidence that every internationalized domain is malicious."
            ]),
            ("Account, login and payment wording", [
                "Phishing campaigns often use words associated with login, verification, security, billing, delivery, password resets or account suspension. Those terms can also appear on legitimate sites.",
                "The useful question is whether the language matches the surrounding context. A cluster of high-pressure account terms on an unfamiliar hostname is more concerning than a single word such as login on a known service."
            ]),
            ("Short links and redirects can hide context", [
                "A shortened link prevents the recipient from seeing the destination directly. Redirect chains can also move the browser from a familiar-looking domain to another host before a form or download appears.",
                "Can I Share This? resolves supported short links and tracks redirect behavior so the final destination can be evaluated. A redirect is not malicious by default, but a surprising destination change should be explained before credentials are entered."
            ]),
            ("HTTPS is necessary but not sufficient", [
                "HTTPS protects the connection between the browser and the site. It does not establish that the site belongs to the organization named in a message. A phishing operator can obtain HTTPS for a domain they control.",
                "Treat HTTPS as transport security, not a trust badge. Domain identity, context and the sensitivity of the requested action still matter."
            ]),
            ("What to do when several signals line up", [
                "Do not sign in through the message. Open the official app or type a known official address independently. If the message came from a colleague or company, verify the request through a separate trusted channel.",
                "CISA advises users to be cautious with unexpected messages and suspicious links and to verify before interacting. A scanner supports that decision; it does not replace it."
            ]),
        ],
        "sources": [
            ("CISA — Secure Our World", "https://www.cisa.gov/secure-our-world"),
            ("ICANN — Internationalized Domain Names", "https://www.icann.org/en/resources/idn"),
            ("RFC 3986 — URI Generic Syntax", "https://www.rfc-editor.org/info/rfc3986/"),
        ],
        "related": ["/lookalike-domain-examples", "/shortened-url-risks", "/how-link-scanning-works", "/phishing-link-checker"],
    },
    {
        "path": "/lookalike-domain-examples",
        "title": "Lookalike Domain Examples: How Deceptive URLs Hide the Real Domain",
        "description": "See safe, synthetic examples of lookalike-domain techniques, misleading subdomains and internationalized domains, with a method for finding the real hostname.",
        "h1": "Lookalike domain examples",
        "kicker": "Domain reference",
        "quick": "A lookalike domain tries to make the destination appear related to a trusted organization while using a different hostname. The safest way to analyze it is to identify the actual hostname and registrable domain, then compare that with the official domain you expected.",
        "points": [
            "A brand-like word in a subdomain does not control the registrable domain.",
            "Extra hyphens, labels or characters can make a different hostname look familiar.",
            "Internationalized domains are legitimate technology but can create visual ambiguity.",
            "Examples below use reserved example domains and are intentionally non-operational.",
        ],
        "examples": [
            ("account.example.com", "A normal subdomain of example.com. The controlling domain is example.com."),
            ("example.com.security-check.example.net", "The trusted-looking text appears on the left, but the destination belongs to example.net."),
            ("example-support-login.example", "A separate domain that uses descriptive words to create familiarity. Words alone do not prove affiliation."),
            ("xn--example-... .example", "Illustrative punycode-style notation. Real IDNs can be legitimate; inspect the Unicode name and domain ownership rather than assuming malicious intent."),
        ],
        "sections": [
            ("The rightmost domain labels matter", [
                "People tend to scan URLs from left to right, which makes long subdomain strings easy to misread. In a hostname such as account.example.com.security-check.example.net, the destination is under example.net, not example.com.",
                "Attackers can exploit this reading habit by placing familiar names early in a hostname. A scanner can flag unusually deep subdomains, but users should still learn to identify the actual registrable domain."
            ]),
            ("Misspellings and inserted words", [
                "Lookalikes can add a character, remove a character, replace a character with a visually similar one, or attach words such as secure, support, verify or login. Some legitimate third-party services also use brand-related words, so a textual resemblance is a warning to verify ownership rather than proof of fraud.",
                "Can I Share This? includes a limited heuristic for recognizable brand names appearing on domains that are not in its recognized-domain list. This is intentionally conservative and should be read as a prompt to inspect the destination."
            ]),
            ("Internationalized Domain Names and punycode", [
                "ICANN's IDN program supports domain names containing characters from many scripts. At the protocol level, some internationalized labels are represented in ASCII using an xn-- prefix.",
                "That mechanism is not malicious. The security issue is visual similarity: two different Unicode strings can sometimes look confusingly alike. A punycode label therefore deserves careful inspection when the link was unexpected."
            ]),
            ("Subdomains versus ownership", [
                "A subdomain is controlled by whoever controls its parent domain. For example, help.example.com is under example.com. By contrast, example.com.help-center.example.net is under example.net even though example.com appears inside the hostname.",
                "This distinction is one of the most useful skills for manually checking suspicious links because copied logos, page titles and path names do not change who controls the destination domain."
            ]),
            ("Safe way to verify a suspected lookalike", [
                "Do not test the destination by logging in. Find the official site through a bookmark, official app, trusted search result or known documentation, then compare the hostname character by character.",
                "If the message asks for sensitive information, contact the organization through an independently obtained channel. A domain that only resembles an official name should not inherit the official site's trust."
            ]),
        ],
        "sources": [
            ("ICANN — Internationalized Domain Names", "https://www.icann.org/en/resources/idn"),
            ("RFC 3986 — URI Generic Syntax", "https://www.rfc-editor.org/info/rfc3986/"),
            ("IANA — Reserved Domains", "https://www.iana.org/help/example-domains"),
        ],
        "related": ["/phishing-url-signals", "/how-link-scanning-works", "/redirect-risk-explained", "/safe-link-checker"],
    },
    {
        "path": "/redirect-risk-explained",
        "title": "Redirect Risk Explained: When a Link Changes Destination",
        "description": "Understand HTTP redirects, why legitimate sites use them, how redirects can hide a final destination, and which redirect patterns deserve more caution.",
        "h1": "Redirect risk explained",
        "kicker": "Redirect reference",
        "quick": "A redirect tells a browser to continue to another URL. Redirects are normal on the web, but they can also hide or change the final destination. Risk increases when a link passes through several redirects, unexpectedly changes to a different domain, or ends on a destination that does not match the sender's claim.",
        "points": [
            "A redirect is a mechanism, not a malicious verdict.",
            "The final destination matters more than the first visible URL.",
            "Cross-domain changes deserve context and verification.",
            "Open redirect weaknesses can make a trusted-looking starting URL lead somewhere untrusted.",
        ],
        "sections": [
            ("Why websites redirect", [
                "Websites redirect for many legitimate reasons: moving a page, enforcing HTTPS, shortening marketing links, measuring campaigns, switching language or geography, and completing authentication flows.",
                "Common HTTP redirect status codes include 301, 302, 303, 307 and 308. The important security question is not merely whether a redirect happened, but where the chain ended and whether that destination was expected."
            ]),
            ("Why redirects can create risk", [
                "A sender can present a URL whose first hostname looks familiar while relying on an intermediate service to send the browser elsewhere. Shorteners are a common example, but any redirecting endpoint can obscure the destination until the request is made.",
                "OWASP documents unvalidated redirects as a phishing risk because an attacker may be able to craft a trusted-looking URL that forwards users to an untrusted site."
            ]),
            ("Cross-domain redirects", [
                "Moving from one hostname to another is common in large platforms, payment processors and identity systems. It is therefore a weak signal by itself.",
                "The change becomes more meaningful when the final domain is unrelated to what the message promised, the redirect chain is unexpected, or the destination asks for sensitive information. Can I Share This? shows the final hostname and records destination changes so users can evaluate that context."
            ]),
            ("Multiple redirects", [
                "Longer redirect chains make manual inspection harder and create more opportunities for the destination to change. They can also result from completely legitimate ad-tech or tracking infrastructure.",
                "The scanner treats several redirects as a cautionary signal rather than proof of abuse. The purpose is to draw attention to the final host and reduce the chance that the user judges the link only by its starting address."
            ]),
            ("Open redirects", [
                "An open redirect occurs when a site accepts a destination supplied by the user without sufficiently restricting where it may send visitors. This can let attackers wrap an untrusted destination inside a URL hosted on a legitimate domain.",
                "A scanner that follows redirects can expose the final host, but the safest response to an unexpected login or payment request is still to open the official service independently."
            ]),
            ("How to interpret redirect results", [
                "A same-site redirect from HTTP to HTTPS is usually routine. A known shortener resolving to an expected official domain can also be routine. A chain that unexpectedly leaves the claimed organization and ends on an unfamiliar login or download host deserves caution.",
                "The destination should make sense before any password, payment, download or account-recovery action is taken."
            ]),
        ],
        "sources": [
            ("OWASP — Unvalidated Redirects and Forwards Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html"),
            ("RFC 9110 — HTTP Semantics", "https://www.rfc-editor.org/info/rfc9110"),
            ("RFC 3986 — URI Generic Syntax", "https://www.rfc-editor.org/info/rfc3986/"),
        ],
        "related": ["/shortened-url-risks", "/how-link-scanning-works", "/phishing-url-signals", "/safe-link-checker"],
    },
    {
        "path": "/shortened-url-risks",
        "title": "Shortened URL Risks: How to Check a Short Link Safely",
        "description": "Learn why shortened URLs hide the destination, when short links are legitimate, which warning signs matter, and how to inspect the final domain before clicking.",
        "h1": "Shortened URL risks",
        "kicker": "Short-link reference",
        "quick": "A shortened URL replaces a long destination with a compact address that redirects when opened. Shorteners are widely used for legitimate sharing and analytics, but the shortened form hides the final hostname. Treat that loss of visibility as a reason to resolve the destination before entering credentials, paying or downloading files.",
        "points": [
            "Short links are not malicious by default.",
            "The main security trade-off is that the destination is hidden.",
            "The final hostname should match the context in which the link was received.",
            "Unexpected short links combined with urgency, login requests or downloads deserve more caution.",
        ],
        "sections": [
            ("What a URL shortener actually does", [
                "A shortener stores or computes a mapping from a compact URL to a longer destination. When the short URL is requested, the service normally responds with an HTTP redirect that sends the browser to the target.",
                "Services such as bit.ly, tinyurl.com and t.co are common examples. Their presence tells you that the visible URL is an intermediary; it does not tell you whether the final destination is good or bad."
            ]),
            ("Why hidden destinations matter", [
                "With a normal URL, a careful user can often inspect the hostname before opening it. A short URL removes that clue from the message. The recipient must resolve the redirect before the final domain becomes visible.",
                "That makes short links useful in phishing and scam messages because the sender can conceal an unfamiliar domain. It also makes them useful for ordinary marketing, social-media character limits and analytics, so context remains essential."
            ]),
            ("Signals that make a short link more concerning", [
                "Concern increases when the message is unexpected, creates urgency, asks for a password or payment, promises a prize, requests a delivery fee, or claims an account is about to be suspended. A surprising final hostname or a chain of several redirects adds more reason to stop.",
                "A short link that resolves directly to an official domain you independently recognize is less concerning, but the destination page and requested action still need to make sense."
            ]),
            ("How Can I Share This? handles short links", [
                "The scanner recognizes a set of common shortening services and marks the hidden-destination characteristic as a cautionary signal. It then follows supported redirects and displays the final hostname.",
                "The shortener signal is deliberately not enough to produce a malicious verdict on its own. The result becomes more informative when it is combined with destination changes, lookalike-domain indicators, download behavior and other URL signals."
            ]),
            ("How to check a short link without trusting it", [
                "Paste the short URL into a scanner that resolves redirects without using your signed-in browser session. Read the final hostname and any redirect warnings before deciding whether the destination fits the message.",
                "For sensitive actions, bypass the link entirely: open the known official app or website yourself. This removes the shortener and the sender's redirect chain from the trust decision."
            ]),
            ("Limits of short-link analysis", [
                "A resolved destination can change later, and some services can route users differently based on time, geography or device. A clean destination at scan time therefore does not guarantee future behavior.",
                "The scan should be treated as evidence about the observed redirect path at that moment, not permanent certification of the short URL."
            ]),
        ],
        "sources": [
            ("CISA — Secure Our World", "https://www.cisa.gov/secure-our-world"),
            ("RFC 9110 — HTTP Semantics", "https://www.rfc-editor.org/info/rfc9110"),
            ("OWASP — Unvalidated Redirects and Forwards Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html"),
        ],
        "related": ["/redirect-risk-explained", "/phishing-url-signals", "/how-link-scanning-works", "/short-link-checker"],
    },
]


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def json_ld(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def label_for(path: str) -> str:
    authority = {p["path"]: p["h1"] for p in PAGES}
    fallbacks = {
        "/methodology": "Methodology",
        "/phishing-link-checker": "Phishing Link Checker",
        "/safe-link-checker": "Safe Link Checker",
        "/short-link-checker": "Short Link Checker",
    }
    return authority.get(path, fallbacks.get(path, path))


def render_examples(items: list[tuple[str, str]]) -> str:
    if not items:
        return ""
    rows = "".join(
        f'<div class="example"><code>{esc(example)}</code><p>{esc(explanation)}</p></div>'
        for example, explanation in items
    )
    return f'<section class="card"><h2>Safe synthetic examples</h2><p>These examples are for explanation only and use reserved example namespaces.</p><div class="examples">{rows}</div></section>'


def render_page(page: dict) -> str:
    canonical = HOST + page["path"]
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": page["h1"],
        "description": page["description"],
        "datePublished": UPDATED,
        "dateModified": UPDATED,
        "mainEntityOfPage": canonical,
        "author": {"@type": "Organization", "name": "Can I Share This?", "url": HOST + "/"},
        "publisher": {"@type": "Organization", "name": "Can I Share This?", "url": HOST + "/"},
        "about": {"@type": "Thing", "name": "URL and link safety"},
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": "Link Safety", "item": HOST + "/safe-link-checker"},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": canonical},
        ],
    }
    points = "".join(f"<li>{esc(x)}</li>" for x in page["points"])
    sections = "".join(
        '<section class="card">' + f"<h2>{esc(title)}</h2>" +
        "".join(f"<p>{esc(p)}</p>" for p in paragraphs) + "</section>"
        for title, paragraphs in page["sections"]
    )
    sources = "".join(
        f'<li><a href="{esc(url, True)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>'
        for label, url in page["sources"]
    )
    related = "".join(
        f'<a href="{esc(path, True)}">{esc(label_for(path))}</a>'
        for path in page["related"]
    )
    examples = render_examples(page.get("examples", []))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page["title"])}</title>
<meta name="description" content="{esc(page["description"], True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(page["title"], True)}"><meta property="og:description" content="{esc(page["description"], True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld(article)}</script><script type="application/ld+json">{json_ld(breadcrumb)}</script>
<style>
:root{{--bg:#f5f6f8;--card:#fff;--text:#17191d;--muted:#68707c;--line:#e2e6eb;--soft:#f8fafb;--accent:#111827;--accentText:#fff;--shadow:0 12px 34px rgba(17,24,39,.06)}}@media(prefers-color-scheme:dark){{:root{{--bg:#0d0f12;--card:#15181d;--text:#f3f4f6;--muted:#a6acb7;--line:#2a2f37;--soft:#111419;--accent:#f3f4f6;--accentText:#111318;--shadow:0 14px 34px rgba(0,0,0,.22)}}}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit}}header{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}.nav{{max-width:1040px;margin:auto;padding:14px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}.button{{display:inline-flex;min-height:44px;align-items:center;justify-content:center;background:var(--accent);color:var(--accentText);padding:10px 16px;border-radius:12px;text-decoration:none;font-weight:780}}main{{max-width:900px;margin:auto;padding:42px 22px 76px}}.crumbs{{font-size:14px;color:var(--muted);margin-bottom:20px}}.kicker{{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 10px;color:var(--muted);font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(36px,7vw,62px);line-height:1.02;letter-spacing:-.047em;margin:14px 0 20px;text-wrap:balance}}.quick{{font-size:clamp(18px,2.6vw,21px);color:var(--muted);max-width:800px;margin:0}}.answer{{padding:22px 24px;border:1px solid var(--line);border-radius:18px;background:var(--card);margin:0 0 16px}}.answer strong{{display:block;margin-bottom:7px}}.points{{margin:0 0 28px;padding:18px 20px 18px 40px;border:1px solid var(--line);border-radius:18px;background:var(--soft)}}.points li{{margin:6px 0}}.card{{margin:14px 0;padding:clamp(20px,3.5vw,30px);border:1px solid var(--line);border-radius:20px;background:var(--card);box-shadow:var(--shadow)}}h2{{font-size:clamp(22px,3.5vw,29px);line-height:1.18;letter-spacing:-.025em;margin:0 0 14px}}p{{margin:0 0 15px}}p:last-child{{margin-bottom:0}}.examples{{display:grid;gap:10px;margin-top:16px}}.example{{padding:14px;border-radius:13px;background:var(--soft)}}code{{display:block;font:700 13px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;word-break:break-word}}.example p{{margin:6px 0 0;color:var(--muted);font-size:14px}}.sources ul{{margin:10px 0 0;padding-left:20px}}.sources li{{margin:7px 0}}.related{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}.related a{{border:1px solid var(--line);background:var(--soft);border-radius:999px;padding:8px 11px;text-decoration:none;font-size:13px;font-weight:750}}.meta{{margin-top:18px;color:var(--muted);font-size:13px}}footer{{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:14px}}footer a{{text-underline-offset:3px}}@media(max-width:640px){{main{{padding:30px 16px 58px}}.nav{{padding:11px 16px}}.button{{padding:9px 12px;min-height:40px}}h1{{font-size:clamp(35px,11vw,48px)}}.card{{border-radius:17px}}}}
</style>
</head><body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main>
<div class="crumbs"><a href="/">Home</a> / <a href="/safe-link-checker">Link safety</a> / {esc(page["h1"])}</div>
<span class="kicker">{esc(page["kicker"])}</span>
<h1>{esc(page["h1"])}</h1>
<div class="answer"><strong>Quick answer</strong><p class="quick">{esc(page["quick"])}</p></div>
<ul class="points">{points}</ul>
{examples}
{sections}
<section class="card sources"><h2>Primary references</h2><p>These references define or document the web and security concepts discussed above.</p><ul>{sources}</ul><p class="meta">Last reviewed: September 2, 2026.</p></section>
<section class="card"><h2>Related reference pages</h2><div class="related">{related}</div></section>
<section class="card"><h2>Check a suspicious link</h2><p>Use the scanner to inspect the URL, redirects and final destination before you open it.</p><p><a class="button" href="/">Analyze the link</a></p></section>
</main>
<footer>Can I Share This? · <a href="/methodology">Methodology</a> · <a href="/privacy">Privacy</a></footer>
</body></html>'''


def write_pages() -> None:
    for page in PAGES:
        target = DIST / f'{page["path"].strip("/")}.html'
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
    for path in AUTHORITY_PATHS:
        urls.add(HOST + path)
    entries = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding="utf-8")


def add_cluster_entrypoints() -> None:
    links = "".join(
        f'<li><a href="{esc(path, True)}">{esc(label_for(path))}</a></li>'
        for path in AUTHORITY_PATHS
    )
    block = (
        '<section class="card" id="authority-reference-library">'
        '<h2>Link safety reference library</h2>'
        '<p>Technical reference pages explaining the signals used when evaluating suspicious links.</p>'
        f'<ul>{links}</ul></section>'
    )
    for filename in ("methodology.html", "safe-link-checker.html"):
        target = DIST / filename
        if not target.is_file():
            continue
        source = target.read_text(encoding="utf-8")
        if 'id="authority-reference-library"' in source:
            continue
        anchor = '<section class="cta">'
        if anchor not in source:
            raise RuntimeError(f"Authority cluster entrypoint anchor missing in {filename}")
        source = source.replace(anchor, block + anchor, 1)
        target.write_text(source, encoding="utf-8")


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist/ does not exist; run this after the base build")
    write_pages()
    add_cluster_entrypoints()
    update_sitemap()
    print(f"Generated {len(PAGES)} authority reference pages")


if __name__ == "__main__":
    main()
