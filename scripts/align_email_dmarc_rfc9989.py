#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'dist' / 'spf-dmarc-email-security.html'


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'DMARC SEO alignment failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not PAGE.is_file():
        raise RuntimeError('SPF/DMARC SEO page not found')

    source = PAGE.read_text(encoding='utf-8')
    source = replace_once(
        source,
        'DMARC p=none is a monitoring policy; quarantine and reject request stronger handling for failures.',
        'DMARC p=none is a monitoring policy; quarantine and reject request different handling for authentication failures.',
        'summary wording'
    )
    source = replace_once(
        source,
        'The policy value matters. p=none is intended for monitoring and reporting rather than requesting quarantine or rejection. p=quarantine and p=reject express stronger requested handling. A pct value below 100 can limit application of the published policy.',
        'The policy value matters. p=none is intended for monitoring and reporting rather than requesting quarantine or rejection. p=quarantine and p=reject request different handling for authentication failures. RFC 9989 removed the historic pct tag and defines the t tag for testing behavior, so this checker treats t=y as a testing signal rather than scoring legacy pct values.',
        'current RFC 9989 policy wording'
    )
    if 'historic pct tag' not in source or 't=y' not in source:
        raise RuntimeError('DMARC SEO alignment guard failed')
    PAGE.write_text(source, encoding='utf-8')
    print('Aligned email DMARC SEO copy with RFC 9989')


if __name__ == '__main__':
    main()
