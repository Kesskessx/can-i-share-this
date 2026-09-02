#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
MANIFEST = ROOT / 'seo' / 'SEO_ROUTE_MANIFEST.json'

SCAM_FLOWS = {
    'fake-package-delivery-scam.html': ['Unexpected message', 'Fake tracking page', 'Small fee', 'Card or data theft'],
    'advance-fee-scam.html': ['Large promise', 'Upfront fee', 'New obstacle', 'More payments'],
    'bank-impersonation-scam.html': ['Fraud alert', 'Urgency', 'Transfer or code', 'Account loss'],
    'account-verification-scam.html': ['Security warning', 'Fake login', 'Password or code', 'Account takeover'],
    'romance-scam.html': ['Build trust', 'Create emergency', 'Ask for money', 'Repeat pressure'],
    'job-offer-scam.html': ['Easy offer', 'Fast hiring', 'Upfront payment', 'Financial loss'],
    'marketplace-scam.html': ['Buyer or seller message', 'Off-platform link', 'Fake payment', 'Money or account loss'],
    'tech-support-scam.html': ['Fake alert', 'Call or chat', 'Remote access', 'Payment or data theft'],
    'crypto-investment-scam.html': ['Fake profits', 'More deposits', 'Withdrawal blocked', 'Extra fees'],
    'gift-card-scam.html': ['Urgent request', 'Buy gift cards', 'Share the codes', 'Funds are gone'],
}

SCAM_FILES = set(SCAM_FLOWS)
SAFETY_FILES = {
    'what-to-do-after-clicking-a-phishing-link.html',
    'what-to-do-if-you-gave-a-scammer-your-password.html',
    'how-to-report-a-scam.html',
    'scam-warning-signs.html',
}
AUTHORITY_FILES = {
    'how-link-scanning-works.html',
    'phishing-url-signals.html',
    'lookalike-domain-examples.html',
    'redirect-risk-explained.html',
    'shortened-url-risks.html',
}
EMAIL_FILES = {
    'email-safety-checker.html',
    'fake-email-address-signs.html',
    'spf-dmarc-email-security.html',
}
EXTRA_FILES = {
    'methodology.html',
    'safe-link-checker.html',
    'phishing-link-checker.html',
    'short-link-checker.html',
    'scam-prevention.html',
}

STYLE = r'''
<style id="cist-readability-v1">
.reading-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:-8px 0 18px;color:var(--muted);font-size:12px;font-weight:750}.reading-meta .dot{opacity:.55}.quick:before,.lead-card:before{content:"At a glance"!important}.answer>strong:first-child{font-size:0}.answer>strong:first-child:after{content:"At a glance";font-size:13px}
.process-flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin:0 0 15px}.flow-step{position:relative;display:flex;align-items:center;justify-content:center;min-height:58px;padding:10px 20px 10px 10px;border:1px solid var(--line);border-radius:13px;background:var(--soft);font-size:12px;font-weight:800;line-height:1.3;text-align:center}.flow-step:not(:last-child):after{content:"→";position:absolute;right:-8px;z-index:2;width:16px;height:16px;display:grid;place-items:center;border:1px solid var(--line);border-radius:999px;background:var(--card);color:#7788eb;font-size:11px}
.more-detail{margin-top:12px;border-top:1px solid var(--line);padding-top:10px}.more-detail summary{cursor:pointer;list-style:none;color:#7788eb;font-size:12px;font-weight:850;user-select:none}.more-detail summary::-webkit-details-marker{display:none}.more-detail summary:after{content:" +"}.more-detail[open] summary:after{content:" −"}.more-detail>p{margin-top:10px!important;color:var(--muted)}
.faq-card[open]{background:var(--card)}details.faq-card>summary{cursor:pointer;list-style:none;font-weight:800;line-height:1.35}details.faq-card>summary::-webkit-details-marker{display:none}details.faq-card>summary:after{content:"+";float:right;margin-left:12px;color:#7788eb}details.faq-card[open]>summary:after{content:"−"}.faq-answer{padding-top:10px;color:var(--muted)}
.card p,.content-card p,.step p,.lead-card p,.answer p{max-width:72ch}.card h2,.content-card h2,.step h2{max-width:28ch}.flags li,.check-list li,.points li{line-height:1.5}.sources,.source-details{font-size:14px}.sources a,.source-details a{text-underline-offset:3px}
@media(max-width:680px){.process-flow{grid-template-columns:1fr 1fr}.flow-step:nth-child(2):after{display:none}.flow-step{min-height:54px;padding:9px 12px}.reading-meta{margin-top:-4px}}
@media(max-width:420px){.process-flow{grid-template-columns:1fr}.flow-step:not(:last-child):after{content:"↓";right:50%;bottom:-9px;top:auto;transform:translateX(50%)}.flow-step{min-height:48px}}
</style>
'''


def priority_files() -> set[str]:
    files: set[str] = set()
    if not MANIFEST.is_file():
        return files
    try:
        data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    except Exception:
        return files
    for route in data.get('routes', []):
        path = str(route.get('path', '')).strip('/')
        if path:
            files.add(path + '.html')
    return files


def strip_text(source: str) -> str:
    main = re.search(r'<main\b[^>]*>(.*?)</main>', source, flags=re.I | re.S)
    body = main.group(1) if main else source
    body = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', body, flags=re.I | re.S)
    body = re.sub(r'<[^>]+>', ' ', body)
    return html.unescape(body)


def read_minutes(source: str) -> int:
    words = re.findall(r"\b[\w’'-]+\b", strip_text(source), flags=re.UNICODE)
    return max(1, min(6, math.ceil(len(words) / 230)))


def guide_label(filename: str) -> str:
    if filename in SCAM_FILES or filename in SAFETY_FILES:
        return 'Practical safety guide'
    if filename in EMAIL_FILES:
        return 'Email safety reference'
    if filename in AUTHORITY_FILES:
        return 'Link safety reference'
    return 'Practical guide'


def add_meta(source: str, filename: str) -> str:
    if 'class="reading-meta"' in source:
        return source
    match = re.search(r'</h1>', source, flags=re.I)
    if not match:
        return source
    minutes = read_minutes(source)
    label = guide_label(filename)
    meta = f'<div class="reading-meta"><span>{minutes} min read</span><span class="dot" aria-hidden="true">·</span><span>{html.escape(label)}</span></div>'
    return source[:match.end()] + meta + source[match.end():]


def add_flow(source: str, filename: str) -> str:
    steps = SCAM_FLOWS.get(filename)
    if not steps or 'class="process-flow"' in source:
        return source
    cards = ''.join(f'<div class="flow-step">{html.escape(step)}</div>' for step in steps)
    flow = f'<div class="process-flow" aria-label="Typical scam sequence">{cards}</div>'
    match = re.search(r'(<section class="quick">.*?</section>)', source, flags=re.I | re.S)
    if not match:
        return source
    return source[:match.end()] + flow + source[match.end():]


def collapse_secondary_paragraphs(source: str, filename: str) -> str:
    if filename not in AUTHORITY_FILES | EMAIL_FILES | SCAM_FILES:
        return source

    pattern = re.compile(
        r'<section class="card"><h2>(?P<title>.*?)</h2>(?P<p1><p>.*?</p>)(?P<p2><p>.*?</p>)(?P<tail>.*?)</section>',
        flags=re.I | re.S,
    )

    def repl(match: re.Match[str]) -> str:
        title_plain = re.sub(r'<[^>]+>', '', match.group('title')).strip().lower()
        if any(x in title_plain for x in ('warning signs', 'related', 'check a suspicious', 'primary reference', 'sources')):
            return match.group(0)
        if filename in SCAM_FILES and not (
            title_plain.startswith('how this scam usually works') or title_plain.startswith('how to verify')
        ):
            return match.group(0)
        return (
            '<section class="card"><h2>' + match.group('title') + '</h2>' + match.group('p1') +
            '<details class="more-detail"><summary>More detail</summary>' + match.group('p2') + '</details>' +
            match.group('tail') + '</section>'
        )

    return pattern.sub(repl, source)


def collapse_priority_faq(source: str) -> str:
    if '<article class="faq-card">' not in source:
        return source
    pattern = re.compile(r'<article class="faq-card">\s*<h3>(.*?)</h3>(.*?)</article>', flags=re.I | re.S)
    return pattern.sub(r'<details class="faq-card"><summary>\1</summary><div class="faq-answer">\2</div></details>', source)


def apply_to_file(path: Path) -> bool:
    source = path.read_text(encoding='utf-8')
    original = source
    if 'id="cist-readability-v1"' in source:
        return False

    source = source.replace('>Quick answer<', '>At a glance<')
    source = add_meta(source, path.name)
    source = add_flow(source, path.name)
    source = collapse_secondary_paragraphs(source, path.name)
    source = collapse_priority_faq(source)
    if '</head>' in source:
        source = source.replace('</head>', STYLE + '</head>', 1)

    if source != original:
        path.write_text(source, encoding='utf-8')
        return True
    return False


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist/ does not exist')

    targets = SCAM_FILES | SAFETY_FILES | AUTHORITY_FILES | EMAIL_FILES | EXTRA_FILES | priority_files()
    updated = 0
    missing: list[str] = []
    for filename in sorted(targets):
        path = DIST / filename
        if not path.is_file():
            # Some optional legacy routes may not exist in every build.
            if filename in {'phishing-link-checker.html', 'short-link-checker.html'}:
                continue
            missing.append(filename)
            continue
        if apply_to_file(path):
            updated += 1

    required_missing = [x for x in missing if x in SCAM_FILES | SAFETY_FILES | AUTHORITY_FILES | EMAIL_FILES]
    if required_missing:
        raise RuntimeError('Missing required readability targets: ' + ', '.join(required_missing))

    print(f'Applied concise readability layout to {updated} content pages')


if __name__ == '__main__':
    main()
