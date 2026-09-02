#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

REPLACEMENTS = [
    ('Checking link signals…', 'Checking the link…'),
    ('Domain · Redirects · Phishing signals · Downloads', 'Website address · Where it goes · Fake-site signs · Downloads'),
    ('Checking email signals…', 'Checking the email address…'),
    ('Address · Mail setup · Impersonation · Domain age', 'Address · Mail setup · Copycat signs · Website age'),
    ('Why this verdict?', 'Why am I seeing this result?'),
    ('Final destination', 'Where this link goes'),
    ('>Check reputation</button>', '>Run extra safety check</button>'),
    ('Checking reputation…', 'Checking known threat lists…'),
    ('External reputation could not be checked right now.', 'The extra safety check could not be completed right now.'),
]


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')
    for old, new in REPLACEMENTS:
        source = source.replace(old, new)

    required = [
        'Checking the link…',
        'Website address · Where it goes · Fake-site signs · Downloads',
        'Why am I seeing this result?',
        'Where this link goes',
        'Run extra safety check',
        'Checking known threat lists…',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Plain-language guard failed: missing {token}')

    # Keep advanced diagnostics labelled as advanced; only simplify the primary experience.
    if 'Technical details <span class="advanced-label">(advanced)</span>' not in source:
        raise RuntimeError('Plain-language guard failed: advanced technical disclosure missing')

    HOME.write_text(source, encoding='utf-8')
    print('Applied plain-language scanner copy for non-technical users')


if __name__ == '__main__':
    main()
