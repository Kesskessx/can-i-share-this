#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

if not HOME.is_file():
    raise RuntimeError('Homepage not found')

source = HOME.read_text(encoding='utf-8')
replacements = {
    "fetch('/api/check'": "fetch('/api/analyze'",
    'fetch("/api/check"': 'fetch("/api/analyze"',
    "fetch('/api/email-check'": "fetch('/api/analyze'",
    'fetch("/api/email-check"': 'fetch("/api/analyze"',
    "fetch('/api/crypto-check'": "fetch('/api/analyze'",
    'fetch("/api/crypto-check"': 'fetch("/api/analyze"',
    "fetch('/api/image-check'": "fetch('/api/analyze'",
    'fetch("/api/image-check"': 'fetch("/api/analyze"',
}
changed = 0
for old, new in replacements.items():
    count = source.count(old)
    if count:
        source = source.replace(old, new)
        changed += count

if changed < 2:
    raise RuntimeError(f'Universal backend routing expected at least 2 endpoint replacements, got {changed}')

for legacy in ['/api/check', '/api/email-check', '/api/crypto-check', '/api/image-check']:
    if f"fetch('{legacy}'" in source or f'fetch("{legacy}"' in source:
        raise RuntimeError(f'Legacy homepage endpoint still used: {legacy}')

if '/api/analyze' not in source:
    raise RuntimeError('Universal analyze endpoint missing from homepage')

HOME.write_text(source, encoding='utf-8')
print(f'Routed {changed} homepage requests through /api/analyze')
