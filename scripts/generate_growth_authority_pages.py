#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"
PUBLISHED = "2026-09-03"
UPDATED = "2026-09-03"

PAGES = [
    {
        "path": "/about",
        "title": "About Can I Share This? — Independent Online Safety Checker",
        "description": "Learn what Can I Share This? checks, why it exists, how it approaches suspicious links and messages, and how it differs from ShareThis.",
        "h1": "What is Can I Share This?",
        "kicker": "About the service",
        "intro": "Can I Share This? is an independent online safety checker built to help people inspect suspicious links, QR destinations, sender addresses, short links and download URLs before trusting them.",
        "sections": [
            ("One question, multiple safety signals", ["The product is designed around a simple decision: should you trust what you received enough to continue? Instead of forcing users to choose between separate technical tools, it combines structural URL checks, redirect context, destination signals, sender-domain checks and optional reputation lookups into one workflow.", "The result is intentionally written in plain language. A scan can reduce uncertainty, but it cannot guarantee that a sender, website or file is safe."]),
            ("Independent from ShareThis", ["Can I Share This? is available at canisharethis.com. It is not ShareThis, is not affiliated with ShareThis, and does not provide social-sharing buttons for websites. The similarity is limited to words in the name."]),
            ("What the service checks", ["Current checks cover suspicious web links, links received through SMS or WhatsApp, QR-code destinations, shortened URLs, download links and sender email addresses. Specialized pages explain Google Drive, Dropbox, phishing, malware, scam and privacy-related checks."]),
            ("How decisions are explained", ["The scanner separates observed signals from the final recommendation. Redirects, unusual domains, encoded URLs, login behavior or risky download responses are context, not automatic proof of abuse. When external reputation checks are available, they are presented separately from the quick structural scan."]),
            ("Privacy and limitations", ["The service is designed for pre-click checking without requiring an account. Application telemetry is designed to avoid storing submitted URLs or hostnames. Some optional external reputation checks can require sending a public URL to a third-party threat service, so the interface asks for explicit consent before that step."])
        ],
        "links": [("Supported checks", "/supported-checks"), ("Scan examples", "/scan-examples"), ("Security and privacy", "/security"), ("Methodology", "/methodology")],
        "sources": []
    },
    {
        "path": "/supported-checks",
        "title": "Supported Checks — Links, QR Codes, Email, Files and Scam Signals",
        "description": "See what Can I Share This? can inspect: suspicious links, SMS and WhatsApp links, QR codes, email addresses, downloads, short links and scam-related signals.",
        "h1": "What Can I Share This? can check",
        "kicker": "Supported checks",
        "intro": "One scanner covers several common ways suspicious content reaches you. The checks below share the same goal: expose the destination, surface warning signs and give a clear next action before you trust it.",
        "cards": [
            ("Links", "Inspect URL structure, destination, redirects and warning signs before opening.", "/safe-link-checker"),
            ("SMS", "Check a suspicious link copied from a text message without opening it in the message.", "/sms-link-checker"),
            ("WhatsApp", "Inspect a link received through WhatsApp before continuing to the destination.", "/whatsapp-link-checker"),
            ("QR codes", "Decode a QR image first, then inspect the URL it contains before visiting it.", "/qr-code-link-checker"),
            ("Email addresses", "Inspect sender-address and domain signals that may indicate impersonation or spoofing risk.", "/email-safety-checker"),
            ("Downloads", "Check a download URL for destination changes and response patterns associated with risky files.", "/download-link-checker"),
            ("Short links", "Resolve shortened links and show the final destination before you trust the visible short URL.", "/short-link-checker"),
            ("Scam context", "Combine technical signals with common scam patterns and practical next-step guidance.", "/scam-checker")
        ],
        "sections": [("What a check does not mean", ["A low-risk result means the checks performed did not find strong warning signs. It does not certify the destination, sender or file as safe. For unexpected requests involving passwords, payment details, one-time codes, identity documents or recovery phrases, verify independently through the official service."])],
        "links": [("See scan examples", "/scan-examples"), ("Read the methodology", "/methodology"), ("Security and privacy", "/security")],
        "sources": []
    },
    {
        "path": "/scan-examples",
        "title": "Link and Scam Scan Examples — How to Read Safety Signals",
        "description": "See safe, synthetic examples of suspicious SMS links, fake delivery URLs, shortened links, sender emails and QR destinations, with example verdict logic.",
        "h1": "Examples of what a scan can reveal",
        "kicker": "Synthetic scan examples",
        "intro": "These examples are intentionally synthetic and use reserved example domains. They illustrate how several weak signals can combine into a stronger warning without exposing or promoting real malicious links.",
        "examples": [
            ("Unexpected delivery text", "https://parcel-update.example/fee", "Caution", ["The message context is unsolicited delivery pressure.", "The domain is unrelated to the courier the message claims to represent.", "The page may request a small payment, which should be verified through the courier's official site."]),
            ("Shortened account-reset link", "https://short.example/a8x2", "Inspect destination", ["The visible URL hides the final hostname.", "Resolve the redirect before signing in.", "A legitimate short link can still be risky if the final destination is unexpected."]),
            ("Lookalike login domain", "https://account.example.com.security-check.example.net", "High caution", ["Trusted-looking words appear on the left, but the controlling destination is under example.net.", "The URL contains account and security language.", "Do not enter credentials until the official domain is independently verified."]),
            ("Suspicious sender address", "billing@secure-account.example", "Verify sender", ["The display name is not evidence of sender identity.", "The domain should be compared with the organization's known official domain.", "Authentication records can add context but do not prove the message content is legitimate."]),
            ("QR code to an unfamiliar host", "https://verify-ticket.example/session", "Caution", ["A QR code hides the destination until decoded.", "Read the decoded hostname before visiting it.", "Unexpected payment or login requests after scanning deserve independent verification."])
        ],
        "sections": [("How to use examples correctly", ["No single example signal is a universal malicious indicator. Redirects, login pages, shortened URLs and unfamiliar domains all have legitimate uses. The useful pattern is convergence: context, destination identity, requested action and technical signals pointing in the same direction."]), ("Why reserved example domains are used", ["The examples avoid live suspicious infrastructure. Reserved example names are suitable for documentation because they are not intended to become operational phishing destinations."])],
        "links": [("Check a link", "/"), ("Supported checks", "/supported-checks"), ("Phishing URL signals", "/phishing-url-signals"), ("Lookalike domain examples", "/lookalike-domain-examples")],
        "sources": [("IANA — Reserved Domains", "https://www.iana.org/help/example-domains")]
    },
    {
        "path": "/security",
        "title": "Security and Privacy — How Can I Share This? Handles Safety Checks",
        "description": "Understand quick scans, optional external reputation checks, URL handling, telemetry, limitations and privacy safeguards used by Can I Share This?.",
        "h1": "Security and privacy",
        "kicker": "Trust center",
        "intro": "A safety checker should explain what it sends, what it stores and what its verdict can and cannot prove. This page documents those boundaries for Can I Share This?.",
        "sections": [
            ("Quick scan", ["The quick scan is designed to inspect the submitted destination from the service side rather than opening it inside your signed-in browser session. It can evaluate URL structure, redirects, response metadata and other warning signs without inheriting your browser cookies."]),
            ("Optional external reputation checks", ["Reputation services answer a different question: whether a public URL is already known to external threat systems. Because private sharing links may contain tokens or sensitive query parameters, Can I Share This? keeps this step separate and asks for consent before sending a URL to an external reputation provider."]),
            ("Telemetry", ["Application analytics are designed around aggregate events such as whether a scan was started or completed. Submitted URLs and hostnames are intentionally excluded from application scan telemetry. Infrastructure providers may still process technical request metadata according to their own operational and security policies."]),
            ("Sensitive links", ["Do not submit secret recovery links, password-reset tokens, private document links or signed URLs to third-party reputation services unless you understand the disclosure risk. The interface warns about this before optional external checks."]),
            ("What the scanner cannot guarantee", ["A destination can change after a scan. New threats can exist before reputation databases know about them. A technically ordinary page can still be part of fraud, and a legitimate service can use redirects, login pages or uncommon infrastructure. Treat the result as decision support rather than certification."]),
            ("Responsible use", ["Use the scanner to inspect links you are entitled to check. Do not use it to probe private systems, bypass access controls or disclose other people's confidential links."])
        ],
        "links": [("Privacy policy", "/privacy"), ("Methodology", "/methodology"), ("How link scanning works", "/how-link-scanning-works"), ("About", "/about")],
        "sources": []
    },
    {
        "path": "/scam-checker",
        "title": "Scam Checker — Check Links, QR Codes and Sender Signals Before You Trust Them",
        "description": "Use a universal scam checker for suspicious links, QR-code destinations, email sender signals, shortened URLs and downloads before you trust a message.",
        "h1": "Check suspicious things before you trust them",
        "kicker": "Universal scam checker",
        "intro": "Scams do not arrive in one format. A suspicious message can contain a normal-looking URL, a QR code, a shortened link, a sender address or a download. Can I Share This? brings those signals into one pre-trust workflow.",
        "sections": [
            ("Start with the thing you received", ["Paste the link or sender address into the homepage scanner, or use the QR checker for an image. The first goal is to expose what is hidden: the real hostname, final destination, redirects or sender-domain context."]),
            ("Separate technical risk from persuasion", ["A scam can use technically ordinary infrastructure. Urgency, impersonation, unexpected payment requests and demands for credentials are contextual warning signs that matter even when the URL itself looks conventional."]),
            ("Use the recommended action", ["The result should answer what to do next: continue cautiously, verify independently, avoid signing in, avoid payment, or stop. When the request is unexpected, use the official app or type the known official website yourself rather than following the message."]),
            ("No scanner can certify legitimacy", ["A scam checker reduces uncertainty. It cannot prove that a business, sender or transaction is legitimate, and it cannot detect every new threat. High-impact actions still require independent verification."])
        ],
        "links": [("Open the scanner", "/"), ("Supported checks", "/supported-checks"), ("Scam warning signs", "/scam-warning-signs"), ("Scam prevention", "/scam-prevention")],
        "sources": []
    },
    {
        "path": "/virustotal-alternative-for-link-checks",
        "title": "VirusTotal Alternative for Simple Link Checks — What Is Different?",
        "description": "Compare Can I Share This? with VirusTotal for URL checks. Understand multi-engine reputation analysis versus a simpler pre-click safety workflow.",
        "h1": "A simpler alternative for pre-click link checks",
        "kicker": "Comparison",
        "intro": "VirusTotal and Can I Share This? solve overlapping but different problems. VirusTotal provides detailed URL analysis using security-partner results. Can I Share This? focuses on a simpler question for everyday users: what warning signs are visible, where does the link go, and what should I do next?",
        "sections": [
            ("Where VirusTotal is stronger", ["VirusTotal can analyze URLs and present results from multiple security partners. That depth is useful for analysts, researchers and users who want detailed reputation evidence across engines."]),
            ("Where Can I Share This? is different", ["Can I Share This? emphasizes destination clarity, redirect context, plain-language warning signs and a recommended action. It also covers adjacent inputs such as QR destinations and sender email addresses through the same product experience."]),
            ("They are not interchangeable", ["Can I Share This? is not a replacement for forensic malware analysis or multi-engine threat research. VirusTotal is not designed primarily as a minimal consumer decision interface. The right choice depends on whether you need deep evidence or fast pre-click context."]),
            ("Privacy consideration", ["Any service that receives a submitted URL may learn that URL. Avoid submitting secret reset links, private document URLs or signed links to external services unless you understand the disclosure implications."])
        ],
        "links": [("Check a link", "/"), ("Security and privacy", "/security"), ("How link scanning works", "/how-link-scanning-works")],
        "sources": [("VirusTotal — URL API reference", "https://docs.virustotal.com/reference/url"), ("VirusTotal — Analysis objects", "https://docs.virustotal.com/reference/analyses-object")]
    },
    {
        "path": "/google-safe-browsing-vs-link-checker",
        "title": "Google Safe Browsing vs a Link Checker — Reputation Lists and URL Signals",
        "description": "Understand the difference between Google Safe Browsing threat-list checks and a broader link checker that also explains redirects, domains and context.",
        "h1": "Google Safe Browsing and link checking answer different questions",
        "kicker": "Comparison",
        "intro": "Google Safe Browsing checks URLs against Google's updated sets of unsafe web resources. A broader link checker can add structural and contextual signals such as the visible hostname, redirects, destination changes and the action the page asks you to take.",
        "sections": [
            ("What Safe Browsing is designed to do", ["Google documents Safe Browsing as a service that lets client applications check URLs against updated lists of unsafe web resources, including social-engineering and malware-related destinations. Current Safe Browsing documentation includes real-time and list-based modes."]),
            ("Why a no-match is not a guarantee", ["A threat-list system is strongest when a destination is already known to the service. New or narrowly targeted malicious pages may exist before they are classified. A result with no known match should therefore not be treated as proof of legitimacy."]),
            ("What a structural link check adds", ["A structural scanner can highlight an unexpected final hostname, a shortened destination, multiple redirects, unusual URL encoding or a forced download even when no reputation source has classified the URL. Those are decision signals, not malware verdicts."]),
            ("Commercial API note", ["Google states that Safe Browsing APIs are for non-commercial use and directs commercial malicious-URL detection use cases to Web Risk. This comparison describes product concepts; it does not imply that Can I Share This? uses Google Safe Browsing for every scan."])
        ],
        "links": [("Safe link checker", "/safe-link-checker"), ("Methodology", "/methodology"), ("Security and privacy", "/security")],
        "sources": [("Google Safe Browsing — Overview", "https://developers.google.com/safe-browsing/reference"), ("Google Safe Browsing", "https://developers.google.com/safe-browsing/")]
    },
    {
        "path": "/urlscan-alternative-for-simple-link-checks",
        "title": "urlscan.io Alternative for Simple Link Checks — When You Need Less Detail",
        "description": "Compare a simple pre-click link checker with urlscan.io browser-style URL scanning, scan visibility controls and detailed website scan results.",
        "h1": "A simpler option when you do not need a full website scan",
        "kicker": "Comparison",
        "intro": "urlscan.io is built for submitting URLs to a website-scanning platform and retrieving detailed results. Can I Share This? is aimed at a lighter decision: reveal the destination, explain the strongest warning signs and tell an everyday user what to do next.",
        "sections": [
            ("What urlscan.io provides", ["urlscan.io documents an API for submitting URLs for scanning and retrieving scan results. It also supports scan visibility choices such as public, unlisted and private, plus search across existing scans and detailed page artifacts in supported cases."]),
            ("Why the workflows feel different", ["A browser-style website scan is useful when you want deeper technical evidence about a page and its network behavior. A pre-click consumer checker can be faster to interpret because it deliberately hides most forensic detail behind a simple verdict and recommended action."]),
            ("When to use which", ["Use a detailed website scanner when you need investigation data. Use a simple checker when the immediate question is whether an unexpected link deserves trust. For sensitive URLs, review the destination service's visibility and privacy behavior before submitting anything."]),
            ("Not a forensic replacement", ["Can I Share This? does not position itself as a substitute for browser sandboxing, incident response tooling or professional website forensics."])
        ],
        "links": [("Check a link", "/"), ("Scan examples", "/scan-examples"), ("Security and privacy", "/security")],
        "sources": [("urlscan.io — Quickstart Guide", "https://docs.urlscan.io/guides/quickstart"), ("urlscan.io — API documentation", "https://urlscan.io/docs/api/")]
    }
]

STYLE = """
:root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#69717d;--line:#e1e5ea;--accent:#6578e8;--soft:#f1f3f6}
@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a8afba;--line:#2a2f37;--accent:#8ea2ff;--soft:#1c2026}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}header{border-bottom:1px solid var(--line)}.top{width:min(900px,calc(100% - 32px));height:62px;margin:auto;display:flex;align-items:center;justify-content:space-between}.brand{text-decoration:none;font-weight:850}.topnav{font-size:13px;color:var(--muted)}main{width:min(760px,calc(100% - 28px));margin:auto;padding:58px 0 70px}.kicker{margin:0 0 10px;color:var(--accent);font-size:12px;font-weight:850;letter-spacing:.09em;text-transform:uppercase}h1{margin:0;font-size:clamp(36px,7vw,58px);line-height:1.02;letter-spacing:-.045em}.intro{font-size:19px;color:var(--muted);margin:18px 0 34px}.section{margin-top:30px}.section h2{font-size:24px;line-height:1.2;letter-spacing:-.025em;margin:0 0 10px}.section p{margin:8px 0;color:var(--muted)}.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:26px 0}.card{display:block;padding:17px;border:1px solid var(--line);border-radius:15px;background:var(--card);text-decoration:none}.card strong{display:block;margin-bottom:5px}.card span{color:var(--muted);font-size:14px}.examples{display:grid;gap:12px;margin:26px 0}.example{padding:18px;border:1px solid var(--line);border-radius:15px;background:var(--card)}.example h2{font-size:19px;margin:0 0 5px}.sample{font:13px/1.45 ui-monospace,SFMono-Regular,Consolas,monospace;word-break:break-all;color:var(--muted)}.verdict{display:inline-block;margin:8px 0;padding:4px 8px;border-radius:999px;background:var(--soft);font-size:12px;font-weight:800}.example ul{margin:7px 0 0;padding-left:20px;color:var(--muted);font-size:14px}.related,.sources{margin-top:34px;padding-top:18px;border-top:1px solid var(--line)}.related h2,.sources h2{font-size:15px}.related-links{display:flex;flex-wrap:wrap;gap:8px}.related-links a{padding:7px 10px;border:1px solid var(--line);border-radius:999px;text-decoration:none;font-size:13px}.sources ul{padding-left:18px;color:var(--muted)}footer{width:min(760px,calc(100% - 28px));margin:0 auto 28px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;text-align:center}@media(max-width:620px){main{padding-top:42px}.cards{grid-template-columns:1fr}.topnav{display:none}}
"""


def render(page: dict) -> str:
    path = page["path"]
    url = HOST + path
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "datePublished": PUBLISHED,
        "dateModified": UPDATED,
        "isPartOf": {"@id": HOST + "/#website"},
        "publisher": {"@id": HOST + "/#organization"}
    }
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{html.escape(page["title"])}</title>',
        f'<meta name="description" content="{html.escape(page["description"], quote=True)}">',
        '<meta name="robots" content="index,follow">',
        f'<link rel="canonical" href="{html.escape(url, quote=True)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{html.escape(page["title"], quote=True)}">',
        f'<meta property="og:description" content="{html.escape(page["description"], quote=True)}">',
        f'<meta property="og:url" content="{html.escape(url, quote=True)}">',
        '<meta name="twitter:card" content="summary">',
        f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>',
        f'<style>{STYLE}</style></head><body>',
        '<header><div class="top"><a class="brand" href="/">Can I Share This?</a><a class="topnav" href="/supported-checks">Supported checks</a></div></header>',
        '<main>',
        f'<p class="kicker">{html.escape(page["kicker"])}</p>',
        f'<h1>{html.escape(page["h1"])}</h1>',
        f'<p class="intro">{html.escape(page["intro"])}</p>'
    ]
    if page.get("cards"):
        parts.append('<div class="cards">')
        for title, text, href in page["cards"]:
            parts.append(f'<a class="card" href="{html.escape(href, quote=True)}"><strong>{html.escape(title)}</strong><span>{html.escape(text)}</span></a>')
        parts.append('</div>')
    if page.get("examples"):
        parts.append('<div class="examples">')
        for title, sample, verdict, signals in page["examples"]:
            lis = ''.join(f'<li>{html.escape(signal)}</li>' for signal in signals)
            parts.append(f'<article class="example"><h2>{html.escape(title)}</h2><div class="sample">{html.escape(sample)}</div><span class="verdict">{html.escape(verdict)}</span><ul>{lis}</ul></article>')
        parts.append('</div>')
    for heading, paragraphs in page.get("sections", []):
        parts.append(f'<section class="section"><h2>{html.escape(heading)}</h2>')
        for paragraph in paragraphs:
            parts.append(f'<p>{html.escape(paragraph)}</p>')
        parts.append('</section>')
    if page.get("links"):
        parts.append('<section class="related"><h2>Related checks and guides</h2><div class="related-links">')
        for label, href in page["links"]:
            parts.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
        parts.append('</div></section>')
    if page.get("sources"):
        parts.append('<section class="sources"><h2>Sources</h2><ul>')
        for label, href in page["sources"]:
            parts.append(f'<li><a href="{html.escape(href, quote=True)}" rel="noopener noreferrer">{html.escape(label)}</a></li>')
        parts.append('</ul></section>')
    parts.append('</main><footer>Independent online safety checker · No scanner can guarantee a destination or sender is safe.</footer></body></html>')
    return ''.join(parts)


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        target = DIST / f'{page["path"].lstrip("/")}.html'
        target.write_text(render(page), encoding="utf-8")
        print(f'Generated {target.name}')
    print(f'Generated {len(PAGES)} growth and authority pages')


if __name__ == "__main__":
    main()
