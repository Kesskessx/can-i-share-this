#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def strip_container_with_text(source: str, needle: str, tags=('section','div','aside')) -> tuple[str, bool]:
    for tag in tags:
        pattern = re.compile(rf'<{tag}\b[^>]*>.*?{re.escape(needle)}.*?</{tag}>', re.I | re.S)
        matches = list(pattern.finditer(source))
        if not matches:
            continue
        match = min(matches, key=lambda m: len(m.group(0)))
        return source[:match.start()] + source[match.end():], True
    return source, False


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    # The supported-input strip already explains what the scanner accepts.
    source, _ = strip_container_with_text(source, 'What we check')

    # Destination checking is already part of the scanner and Supported Checks.
    source = re.sub(
        r'<(?:p|div|span|strong|b)[^>]*>\s*See the real destination before you open a link\.?\s*</(?:p|div|span|strong|b)>',
        '', source, count=1, flags=re.I | re.S
    )

    # Keep the footer focused on complementary destinations.
    source = re.sub(r'\s*<a\b[^>]*href=["\']/security["\'][^>]*>\s*Security\s*</a>', '', source, count=1, flags=re.I)

    # Visible ShareThis disambiguation belongs on About, not on the compact homepage.
    source, _ = strip_container_with_text(source, 'Is Can I Share This? related to ShareThis?')

    # Remove separator artifacts after link deletion.
    source = re.sub(r'(<div class="footer-resource-links">)\s*<i[^>]*>·</i>', r'\1', source, flags=re.I)
    source = re.sub(r'<i[^>]*>·</i>\s*(</div>)', r'\1', source, flags=re.I)
    source = re.sub(r'(<i[^>]*>·</i>\s*){2,}', '<i aria-hidden="true">·</i>', source, flags=re.I)

    forbidden = [
        'What we check',
        'See the real destination before you open a link.',
        'Is Can I Share This? related to ShareThis?',
    ]
    for token in forbidden:
        if token in source:
            raise RuntimeError(f'Duplicate homepage content survived: {token}')
    if re.search(r'href=["\']/security["\']', source, re.I):
        raise RuntimeError('Security footer link survived final homepage cleanup')

    required = [
        'Private by design · No account required',
        'URL', 'Email', 'Message', 'Social profile', 'QR', 'Image', 'File', 'Crypto address',
        'Supported Checks', 'About', 'Business inquiries',
        'No scanner can guarantee that a link or sender is safe.',
        '@CanIShareLink',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Homepage cleanup removed required content: {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Removed remaining duplicate homepage sections')


if __name__ == '__main__':
    main()
