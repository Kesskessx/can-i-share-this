#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    old_hero = 'Links, emails, messages, social profiles, QR codes, images, files and crypto. One scanner.'
    new_hero = 'Analyze suspicious content before you open, reply, pay or share.'
    source = source.replace(old_hero, new_hero)

    # Keep the privacy promise next to the scanner and remove the near-duplicate footer promise.
    source = re.sub(
        r'\s*<span>Privacy-first · No signup</span>',
        '',
        source,
        count=1,
    )

    # The universal input is no longer link-only.
    source = source.replace('Check link', 'Check')

    if old_hero in source:
        raise RuntimeError('Duplicate supported-input sentence survived homepage cleanup')
    if '<span>Privacy-first · No signup</span>' in source:
        raise RuntimeError('Duplicate privacy promise survived homepage cleanup')
    if 'Analyze suspicious content before you open, reply, pay or share.' not in source:
        raise RuntimeError('Homepage benefit copy was not installed')
    if 'Private by design · No account required' not in source:
        raise RuntimeError('Primary privacy promise must remain visible near the scanner')
    if 'No scanner can guarantee that a link or sender is safe.' not in source:
        raise RuntimeError('Safety limitation must remain in the footer')

    HOME.write_text(source, encoding='utf-8')
    print('Removed duplicate homepage copy and generalized the scanner CTA')


if __name__ == '__main__':
    main()
