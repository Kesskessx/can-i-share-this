#!/usr/bin/env python3
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

LABELS = {
    '/social-media-profile-checker': 'Social media profile checker',
    '/fake-instagram-profile-checker': 'Fake Instagram profile checker',
    '/fake-facebook-profile-checker': 'Fake Facebook profile checker',
    '/fake-tiktok-account-checker': 'Fake TikTok account checker',
    '/fake-x-profile-checker': 'Fake X profile checker',
    '/telegram-scam-profile-checker': 'Telegram scam profile checker',
    '/how-to-spot-a-fake-social-media-profile': 'How to spot a fake social profile',
    '/celebrity-impersonation-scam': 'Celebrity impersonation scam',
    '/influencer-impersonation-scam': 'Influencer impersonation scam',
    '/catfish-profile-checker': 'Catfish profile checker',
}

# Hub-and-spoke linking makes each page's purpose clearer than an all-to-all mesh.
LINKS = {
    '/social-media-profile-checker': [
        '/fake-instagram-profile-checker',
        '/fake-facebook-profile-checker',
        '/fake-tiktok-account-checker',
        '/fake-x-profile-checker',
        '/telegram-scam-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/celebrity-impersonation-scam',
        '/influencer-impersonation-scam',
        '/catfish-profile-checker',
    ],
    '/fake-instagram-profile-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/influencer-impersonation-scam',
        '/catfish-profile-checker',
    ],
    '/fake-facebook-profile-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/celebrity-impersonation-scam',
        '/catfish-profile-checker',
    ],
    '/fake-tiktok-account-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/influencer-impersonation-scam',
        '/celebrity-impersonation-scam',
    ],
    '/fake-x-profile-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/influencer-impersonation-scam',
        '/celebrity-impersonation-scam',
    ],
    '/telegram-scam-profile-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/catfish-profile-checker',
    ],
    '/how-to-spot-a-fake-social-media-profile': [
        '/social-media-profile-checker',
        '/fake-instagram-profile-checker',
        '/fake-facebook-profile-checker',
        '/fake-tiktok-account-checker',
        '/fake-x-profile-checker',
        '/telegram-scam-profile-checker',
    ],
    '/celebrity-impersonation-scam': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/fake-instagram-profile-checker',
        '/fake-tiktok-account-checker',
        '/fake-x-profile-checker',
    ],
    '/influencer-impersonation-scam': [
        '/social-media-profile-checker',
        '/fake-instagram-profile-checker',
        '/fake-tiktok-account-checker',
        '/fake-x-profile-checker',
    ],
    '/catfish-profile-checker': [
        '/social-media-profile-checker',
        '/how-to-spot-a-fake-social-media-profile',
        '/fake-instagram-profile-checker',
        '/fake-facebook-profile-checker',
    ],
}

STYLE = '''<style id="social-cluster-links-style">.social-cluster-links{margin:28px 0 0;padding:18px 0 0;border-top:1px solid var(--line,#d9dde5)}.social-cluster-links strong{display:block;margin-bottom:10px;font-size:14px}.social-cluster-links div{display:flex;gap:8px;flex-wrap:wrap}.social-cluster-links a{display:inline-flex;padding:7px 10px;border:1px solid var(--line,#d9dde5);border-radius:999px;color:inherit;text-decoration:none;font-size:12px}.social-cluster-links a:hover{text-decoration:underline}</style>'''

for path in LABELS:
    target = DIST / f'{path.lstrip("/")}.html'
    if not target.is_file():
        raise RuntimeError(f'Missing social profile page: {path}')
    source = target.read_text(encoding='utf-8')
    source = re.sub(
        r'<nav id="social-cluster-links" class="social-cluster-links"[^>]*>.*?</nav>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    links = ''.join(
        f'<a href="{html.escape(other_path, quote=True)}">{html.escape(LABELS[other_path])}</a>'
        for other_path in LINKS[path]
    )
    heading = 'Platform-specific and related checks' if path == '/social-media-profile-checker' else 'Related social-profile checks'
    block = (
        '<nav id="social-cluster-links" class="social-cluster-links" aria-label="Social profile safety guides">'
        f'<strong>{html.escape(heading)}</strong><div>{links}</div></nav>'
    )
    if '</article>' in source:
        source = source.replace('</article>', block + '</article>', 1)
    elif '</main>' in source:
        source = source.replace('</main>', block + '</main>', 1)
    else:
        raise RuntimeError(f'Cannot place social cluster links on {path}')
    if 'id="social-cluster-links-style"' not in source:
        source = source.replace('</head>', STYLE + '</head>', 1)
    target.write_text(source, encoding='utf-8')

print(f'Applied intent-focused internal linking to {len(LABELS)} social-profile pages')
