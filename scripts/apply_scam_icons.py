#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / 'dist' / 'scam-prevention.html'

SCAM_ICONS = {
    '/fake-package-delivery-scam': ('📦', 'Fake package delivery scams'),
    '/advance-fee-scam': ('💸', 'Advance-fee scams'),
    '/bank-impersonation-scam': ('🏦', 'Bank impersonation scams'),
    '/account-verification-scam': ('🔐', 'Account verification scams'),
    '/romance-scam': ('❤️', 'Romance scams'),
    '/job-offer-scam': ('💼', 'Job offer scams'),
    '/marketplace-scam': ('🛒', 'Marketplace scams'),
    '/tech-support-scam': ('🖥️', 'Tech support scams'),
    '/crypto-investment-scam': ('₿', 'Crypto investment scams'),
    '/gift-card-scam': ('🎁', 'Gift card scams'),
}

STYLE = '''<style id="scam-icon-style">
.scam-icon{display:inline-block;min-width:1.45em;margin-right:.28em;text-align:center;font-size:1.02em;line-height:1;vertical-align:-.06em}
@media(max-width:700px){.scam-icon{min-width:1.35em;margin-right:.22em}}
</style>'''


def main() -> None:
    if not HUB.is_file():
        raise RuntimeError('Scam prevention hub not found')

    source = HUB.read_text(encoding='utf-8')

    if 'id="scam-icon-style"' not in source:
        if '</head>' not in source:
            raise RuntimeError('Scam prevention hub has no </head> anchor')
        source = source.replace('</head>', STYLE + '</head>', 1)

    for path, (icon, label) in SCAM_ICONS.items():
        anchor = f'<a class="related" href="{path}"><strong>{label}</strong>'
        replacement = (
            f'<a class="related" href="{path}"><strong>'
            f'<span class="scam-icon" aria-hidden="true">{icon}</span>{label}</strong>'
        )
        if replacement in source:
            continue
        if anchor not in source:
            raise RuntimeError(f'Scam icon anchor not found for {path}')
        source = source.replace(anchor, replacement, 1)

    for path, (icon, label) in SCAM_ICONS.items():
        expected = f'href="{path}"><strong><span class="scam-icon" aria-hidden="true">{icon}</span>{label}</strong>'
        if expected not in source:
            raise RuntimeError(f'Scam icon validation failed for {path}')

    HUB.write_text(source, encoding='utf-8')
    print(f'Added professional visual icons to {len(SCAM_ICONS)} common scam cards')


if __name__ == '__main__':
    main()
