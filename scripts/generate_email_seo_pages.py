#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOST = 'https://canisharethis.com'
UPDATED = '2026-09-02'

EMAIL_PATHS = [
    '/email-safety-checker',
    '/fake-email-address-signs',
    '/spf-dmarc-email-security',
]

PAGES = [
    {
        'path': '/email-safety-checker',
        'title': 'Email Safety Checker: Check a Suspicious Sender Address',
        'description': 'Check a suspicious email address for domain, MX, SPF, DMARC, domain-age, lookalike and disposable-email warning signs before you reply.',
        'h1': 'Email safety checker',
        'kicker': 'Suspicious sender check',
        'quick': 'An email address can be checked for technical and impersonation warning signs without proving who controls the mailbox. Can I Share This? inspects the sender domain, mail-routing records, SPF and DMARC posture, domain age, lookalike patterns and disposable-email signals. A low-risk result does not prove that the sender is trustworthy.',
        'points': [
            'The checker analyzes the domain behind the address, not the contents of the mailbox.',
            'MX, SPF and DMARC provide useful context but cannot establish a sender’s identity by themselves.',
            'Very new, disposable or brand-lookalike domains deserve stronger independent verification.',
            'The address itself is not added to aggregate scan telemetry.',
        ],
        'sections': [
            ('What the email checker looks at', [
                'The scan begins by validating the address format and extracting the domain after the @ sign. It then performs DNS checks for mail routing and authentication records, evaluates the domain name for visual impersonation patterns, and checks whether the provider is known to be temporary or disposable.',
                'The current email scan also reads the domain’s SPF and DMARC posture, checks for MTA-STS and TLS reporting records when available, looks for DNSSEC delegation information, and uses public RDAP registration data on a best-effort basis to estimate domain age. These signals are combined into a warning score rather than treated as independent proof of fraud.'
            ]),
            ('Why domain age can matter', [
                'A newly registered domain is not automatically suspicious. New businesses, projects and campaigns legitimately create domains every day. The signal becomes more useful when a very recent registration appears together with another warning sign, such as a brand-like spelling, account-verification language or an unexpected payment request.',
                'Can I Share This? treats registration age as context. If public RDAP data is unavailable or does not expose a usable creation date, the checker does not penalize the address for missing age data.'
            ]),
            ('What SPF and DMARC can and cannot tell you', [
                'SPF allows a domain to publish which systems are authorized to use that domain in specific SMTP identities. DMARC adds alignment and a domain-owner policy for mail that fails authentication. A well-configured policy can reduce spoofing of a domain, but it does not prove that every mailbox or every message from that domain is legitimate.',
                'The checker therefore distinguishes between simple presence and policy quality. For example, an unusually permissive SPF record or a DMARC p=none monitoring policy is different from a stronger configuration, but neither condition alone means the sender is a scammer.'
            ]),
            ('Lookalike and disposable sender domains', [
                'Impersonation often relies on small spelling changes, digit substitutions, added security words or other visual tricks that make a different domain resemble a known service. The checker compares the registrable label against a limited set of recognized brands and flags close matches that are not recognized official domains.',
                'Temporary email providers are also detected from a local list. Disposable email is legitimate in many privacy and testing contexts, so the result is shown as a caution signal rather than proof of malicious intent.'
            ]),
            ('What the checker cannot verify', [
                'An address-level scan cannot reliably prove that a specific mailbox exists, identify the person operating it, or determine whether a message was actually sent by that mailbox. SMTP mailbox probing is often blocked, rate-limited or distorted by catch-all configurations.',
                'For unexpected requests involving payment, passwords, one-time codes, identity documents or account recovery, verify the sender through a separate trusted channel even when the technical result is low risk.'
            ]),
        ],
        'sources': [
            ('RFC 7208 — Sender Policy Framework (SPF)', 'https://datatracker.ietf.org/doc/html/rfc7208'),
            ('RFC 9989 — Domain-Based Message Authentication, Reporting, and Conformance (DMARC)', 'https://datatracker.ietf.org/doc/html/rfc9989'),
            ('RFC 9082 — Registration Data Access Protocol (RDAP) Query Format', 'https://datatracker.ietf.org/doc/html/rfc9082'),
        ],
        'related': ['/fake-email-address-signs', '/spf-dmarc-email-security', '/phishing-url-signals', '/methodology'],
    },
    {
        'path': '/fake-email-address-signs',
        'title': 'How to Spot a Fake Email Address: Sender & Domain Warning Signs',
        'description': 'Learn how to inspect a suspicious sender address for lookalike domains, recent registration, disposable providers and weak mail-domain signals.',
        'h1': 'How to spot a fake email address',
        'kicker': 'Email impersonation guide',
        'quick': 'A suspicious email address is best evaluated by reading the real domain after the @ sign, comparing it with the organization you expected, and then checking supporting signals such as domain age, mail records and authentication policy. No single spelling trick, DNS record or risk score proves that an address is fake.',
        'points': [
            'Focus on the domain after @, not the display name shown by the mail app.',
            'Small spelling changes and digit substitutions can create convincing brand lookalikes.',
            'A recently registered domain is more meaningful when combined with other suspicious context.',
            'A valid MX record only shows that the domain is configured to receive mail; it does not verify the sender’s identity.',
        ],
        'sections': [
            ('Start with the part after the @ sign', [
                'Mail apps often emphasize a friendly display name such as “PayPal Support” or “Microsoft Security”. Display names are not unique and can be chosen by the sender. The domain after the @ sign is therefore a more useful starting point for checking who the address claims to represent.',
                'Compare that domain with the official domain you independently know or find through the organization’s official website. Do not assume affiliation because a brand name appears somewhere inside a longer domain.'
            ]),
            ('Look for character substitutions and added words', [
                'Impersonation domains can replace letters with digits, insert or remove characters, or append words such as secure, verification, billing, account or support. A domain such as a misspelled brand followed by “-security” can look plausible at a glance while belonging to an unrelated registrant.',
                'Can I Share This? uses conservative visual-normalization and edit-distance heuristics for a limited set of recognizable brands. The purpose is to surface a warning for manual verification, not to label every similar name as malicious.'
            ]),
            ('Check whether the domain is unusually new', [
                'Fraud campaigns can use newly registered domains because the operator only needs the infrastructure for a short period. The same fact also applies to legitimate new organizations, so registration age should never be used as a standalone verdict.',
                'Public RDAP services can expose registration events for many domains. When a usable registration date is available, the checker turns that into an approximate age and gives very recent domains more weight only as part of a multi-signal assessment.'
            ]),
            ('Mail records are context, not identity', [
                'MX records indicate where a domain receives mail. SPF describes which systems are authorized for certain SMTP identities. DMARC describes alignment and handling policy. These technologies make spoofing harder when properly deployed, but they do not prove that the person behind a particular mailbox is legitimate.',
                'A scammer can register a new domain and configure MX, SPF and DMARC correctly. Conversely, a legitimate small organization can have imperfect mail authentication. Treat these records as evidence about the domain’s setup, not a background check on the sender.'
            ]),
            ('When to stop and verify another way', [
                'Independent verification becomes especially important when an unexpected email asks for money, credentials, recovery codes, identity documents, cryptocurrency, gift cards or urgent account action.',
                'Open the official app or site yourself, use a phone number you obtained independently, or contact the person through a channel you already trust. Do not use contact details supplied only inside the suspicious message.'
            ]),
        ],
        'sources': [
            ('CISA — Recognize and Report Phishing', 'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing'),
            ('RFC 9082 — RDAP Query Format', 'https://datatracker.ietf.org/doc/html/rfc9082'),
            ('ICANN — Internationalized Domain Names', 'https://www.icann.org/resources/pages/idn-2012-02-25-en'),
        ],
        'related': ['/email-safety-checker', '/spf-dmarc-email-security', '/lookalike-domain-examples', '/phishing-url-signals'],
    },
    {
        'path': '/spf-dmarc-email-security',
        'title': 'SPF and DMARC Email Security: What the Records Really Tell You',
        'description': 'Understand SPF quality, DMARC policies, MTA-STS and TLS reporting, and why authentication records do not by themselves prove that a sender is trustworthy.',
        'h1': 'SPF and DMARC email security',
        'kicker': 'Mail authentication reference',
        'quick': 'SPF and DMARC help receiving systems evaluate whether mail is authorized to use a domain and how authentication failures should be handled. Strong policies reduce some forms of spoofing, but they authenticate domain use and alignment rather than the real-world identity or intentions of the person sending a message.',
        'points': [
            'SPF presence is less informative than the actual policy that was published.',
            'DMARC p=none is a monitoring policy; quarantine and reject request stronger handling for failures.',
            'SPF and DMARC can be configured correctly on a maliciously registered domain.',
            'MTA-STS and TLS-RPT address transport security and reporting, not sender trustworthiness.',
        ],
        'sections': [
            ('SPF: authorization for SMTP identities', [
                'SPF is defined in RFC 7208. A domain publishes a TXT policy describing which hosts are authorized to use that domain in the SMTP MAIL FROM or HELO identities. Receiving systems evaluate the policy during message handling.',
                'A checker should therefore inspect more than whether “v=spf1” exists. Multiple SPF records can invalidate evaluation, an unqualified or +all mechanism can be overly permissive, and policies with too many DNS-dependent mechanisms can exceed the SPF processing limit.'
            ]),
            ('DMARC: alignment and handling policy', [
                'DMARC is standardized in RFC 9989. It evaluates whether authenticated identifiers align with the domain visible to the user and lets a domain owner publish a requested handling policy for failures.',
                'The policy value matters. p=none is intended for monitoring and reporting rather than requesting quarantine or rejection. p=quarantine and p=reject express stronger requested handling. A pct value below 100 can limit application of the published policy.'
            ]),
            ('Why strong authentication does not equal a safe sender', [
                'A threat actor who legitimately controls a domain can configure SPF and DMARC for that domain. Authentication can then succeed even though the message itself is deceptive. The protocols answer questions about authorized use of a domain; they do not certify the business, person or offer described in the message.',
                'That is why Can I Share This? combines authentication posture with domain identity, registration age, disposable-provider checks and lookalike analysis rather than turning SPF or DMARC into a binary scam verdict.'
            ]),
            ('MTA-STS and TLS reporting', [
                'MTA-STS, defined in RFC 8461, lets receiving domains publish a policy for TLS-secured SMTP delivery. TLS-RPT, defined in RFC 8460, provides reporting about TLS delivery failures. These are useful signs of mail-security maturity.',
                'Their absence is common and is not treated as evidence of a scam. In the checker they are presented as technical posture information rather than major risk-score penalties.'
            ]),
            ('DNSSEC and registration data', [
                'DNSSEC can provide cryptographic protection for DNS data when the delegation and validating resolver path support it. As with MTA-STS, the presence or absence of DNSSEC is not a sender-identity verdict.',
                'Registration age comes from public RDAP data on a best-effort basis. It is a separate contextual signal: a very young domain can increase uncertainty, while a long registration history does not guarantee that a mailbox or account has not been compromised.'
            ]),
        ],
        'sources': [
            ('RFC 7208 — Sender Policy Framework (SPF)', 'https://datatracker.ietf.org/doc/html/rfc7208'),
            ('RFC 9989 — DMARC', 'https://datatracker.ietf.org/doc/html/rfc9989'),
            ('RFC 8461 — SMTP MTA Strict Transport Security', 'https://datatracker.ietf.org/doc/html/rfc8461'),
            ('RFC 8460 — SMTP TLS Reporting', 'https://datatracker.ietf.org/doc/html/rfc8460'),
        ],
        'related': ['/email-safety-checker', '/fake-email-address-signs', '/methodology', '/how-link-scanning-works'],
    },
]


def esc(value: object, quote: bool = False) -> str:
    return html.escape(str(value), quote=quote)


def json_ld(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def label_for(path: str) -> str:
    labels = {
        '/email-safety-checker': 'Email safety checker',
        '/fake-email-address-signs': 'Fake email address signs',
        '/spf-dmarc-email-security': 'SPF and DMARC email security',
        '/phishing-url-signals': 'Phishing URL signals',
        '/lookalike-domain-examples': 'Lookalike domain examples',
        '/how-link-scanning-works': 'How link scanning works',
        '/methodology': 'Methodology',
    }
    return labels.get(path, path.strip('/').replace('-', ' ').title())


def render_page(page: dict) -> str:
    canonical = HOST + page['path']
    article = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': page['h1'],
        'description': page['description'],
        'url': canonical,
        'datePublished': UPDATED,
        'dateModified': UPDATED,
        'author': {'@type': 'Organization', 'name': 'Can I Share This?', 'url': HOST + '/'},
        'publisher': {'@type': 'Organization', 'name': 'Can I Share This?', 'url': HOST + '/'},
        'about': {'@type': 'Thing', 'name': 'Email sender safety and domain authentication'},
    }
    breadcrumb = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': HOST + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Email safety', 'item': HOST + '/email-safety-checker'},
            {'@type': 'ListItem', 'position': 3, 'name': page['h1'], 'item': canonical},
        ],
    }
    points = ''.join(f'<li>{esc(item)}</li>' for item in page['points'])
    sections = ''.join(
        '<section class="card">' + f'<h2>{esc(title)}</h2>' + ''.join(f'<p>{esc(p)}</p>' for p in paragraphs) + '</section>'
        for title, paragraphs in page['sections']
    )
    sources = ''.join(
        f'<li><a href="{esc(url, True)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>'
        for label, url in page['sources']
    )
    related = ''.join(
        f'<a href="{esc(path, True)}">{esc(label_for(path))}</a>'
        for path in page['related']
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'], True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(page['title'], True)}"><meta property="og:description" content="{esc(page['description'], True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld(article)}</script><script type="application/ld+json">{json_ld(breadcrumb)}</script>
<style>
:root{{--bg:#f5f6f8;--card:#fff;--text:#17191d;--muted:#68707c;--line:#e2e6eb;--soft:#f8fafb;--accent:#111827;--accentText:#fff;--shadow:0 12px 34px rgba(17,24,39,.06)}}@media(prefers-color-scheme:dark){{:root{{--bg:#0d0f12;--card:#15181d;--text:#f3f4f6;--muted:#a6acb7;--line:#2a2f37;--soft:#111419;--accent:#f3f4f6;--accentText:#111318;--shadow:0 14px 34px rgba(0,0,0,.22)}}}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit}}header{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}.nav{{max-width:1040px;margin:auto;padding:14px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}.button{{display:inline-flex;min-height:44px;align-items:center;justify-content:center;background:var(--accent);color:var(--accentText);padding:10px 16px;border-radius:12px;text-decoration:none;font-weight:780}}main{{max-width:900px;margin:auto;padding:42px 22px 76px}}.crumbs{{font-size:14px;color:var(--muted);margin-bottom:20px}}.kicker{{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 10px;color:var(--muted);font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(36px,7vw,62px);line-height:1.02;letter-spacing:-.047em;margin:14px 0 20px;text-wrap:balance}}.quick{{font-size:clamp(18px,2.6vw,21px);color:var(--muted);max-width:800px;margin:0}}.answer{{padding:22px 24px;border:1px solid var(--line);border-radius:18px;background:var(--card);margin:0 0 16px}}.answer strong{{display:block;margin-bottom:7px}}.points{{margin:0 0 28px;padding:18px 20px 18px 40px;border:1px solid var(--line);border-radius:18px;background:var(--soft)}}.points li{{margin:6px 0}}.card{{margin:14px 0;padding:clamp(20px,3.5vw,30px);border:1px solid var(--line);border-radius:20px;background:var(--card);box-shadow:var(--shadow)}}h2{{font-size:clamp(22px,3.5vw,29px);line-height:1.18;letter-spacing:-.025em;margin:0 0 14px}}p{{margin:0 0 15px}}p:last-child{{margin-bottom:0}}.sources ul{{margin:10px 0 0;padding-left:20px}}.sources li{{margin:7px 0}}.related{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}.related a{{border:1px solid var(--line);background:var(--soft);border-radius:999px;padding:8px 11px;text-decoration:none;font-size:13px;font-weight:750}}.meta{{margin-top:18px;color:var(--muted);font-size:13px}}footer{{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:14px}}footer a{{text-underline-offset:3px}}@media(max-width:640px){{main{{padding:30px 16px 58px}}.nav{{padding:11px 16px}}.button{{padding:9px 12px;min-height:40px}}h1{{font-size:clamp(35px,11vw,48px)}}.card{{border-radius:17px}}}}
</style>
</head><body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check an email</a></div></header>
<main>
<div class="crumbs"><a href="/">Home</a> / <a href="/email-safety-checker">Email safety</a> / {esc(page['h1'])}</div>
<span class="kicker">{esc(page['kicker'])}</span>
<h1>{esc(page['h1'])}</h1>
<div class="answer"><strong>Quick answer</strong><p class="quick">{esc(page['quick'])}</p></div>
<ul class="points">{points}</ul>
{sections}
<section class="card sources"><h2>Primary references</h2><p>These references define or document the email and domain-security concepts discussed above.</p><ul>{sources}</ul><p class="meta">Last reviewed: September 2, 2026.</p></section>
<section class="card"><h2>Related email and link safety pages</h2><div class="related">{related}</div></section>
<section class="card"><h2>Check a suspicious email address</h2><p>Paste the address into the same Can I Share This? scanner used for suspicious links. The checker automatically detects that the input is an email address.</p><p><a class="button" href="/">Analyze the email address</a></p></section>
</main>
<footer>Can I Share This? · <a href="/methodology">Methodology</a> · <a href="/privacy">Privacy</a></footer>
</body></html>'''


def write_pages() -> None:
    for page in PAGES:
        target = DIST / f"{page['path'].strip('/')}.html"
        target.write_text(render_page(page), encoding='utf-8')


def update_sitemap() -> None:
    sitemap = DIST / 'sitemap.xml'
    urls: set[str] = set()
    if sitemap.is_file():
        old = sitemap.read_text(encoding='utf-8', errors='replace')
        for loc in re.findall(r'<loc>\s*(.*?)\s*</loc>', old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(HOST + (parsed.path.rstrip('/') or '/'))
    urls.add(HOST + '/')
    for path in EMAIL_PATHS:
        urls.add(HOST + path)
    entries = '\n'.join(f'  <url><loc>{html.escape(url)}</loc></url>' for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding='utf-8')


def add_cluster_entrypoints() -> None:
    links = ''.join(f'<li><a href="{esc(path, True)}">{esc(label_for(path))}</a></li>' for path in EMAIL_PATHS)
    block = (
        '<section class="card" id="email-safety-library">'
        '<h2>Email safety guides</h2>'
        '<p>Focused references for checking suspicious sender addresses and understanding email-domain authentication.</p>'
        f'<ul>{links}</ul></section>'
    )
    for filename in ('methodology.html', 'safe-link-checker.html'):
        target = DIST / filename
        if not target.is_file():
            continue
        source = target.read_text(encoding='utf-8')
        if 'id="email-safety-library"' in source:
            continue
        anchor = '<section class="cta">'
        if anchor not in source:
            raise RuntimeError(f'Email SEO cluster entrypoint anchor missing in {filename}')
        source = source.replace(anchor, block + anchor, 1)
        target.write_text(source, encoding='utf-8')


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist/ does not exist; run this after the base build')
    write_pages()
    add_cluster_entrypoints()
    update_sitemap()
    print(f'Generated {len(PAGES)} email safety SEO pages')


if __name__ == '__main__':
    main()
