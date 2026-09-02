#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')
    old = "techGrid.innerHTML='<div class=\"tech\"><span>Email domain</span><strong>'+esc(emailDomain||'Unknown')+'</strong></div><div class=\"tech\"><span>MX records</span><strong>'+(info.hasMx?'Found':'Not found')+'</strong></div><div class=\"tech\"><span>SPF</span><strong>'+(info.hasSpf?'Found':'Not found')+'</strong></div><div class=\"tech\"><span>DMARC</span><strong>'+(info.hasDmarc?'Found':'Not found')+'</strong></div>'"
    new = "var spfLabel=info.spfQuality&&info.spfQuality!=='unknown'?String(info.spfQuality).replace(/-/g,' '):(info.hasSpf?'Found':'Not found');var dmarcLabel=info.hasDmarc?(info.dmarcPolicy?String(info.dmarcPolicy).toUpperCase():'Found'):'Not found';var ageLabel=Number.isFinite(info.domainAgeDays)?info.domainAgeDays+' days':'Unavailable';var dnssecLabel=info.dnssecKnown?(info.hasDnssec?'Present':'Not detected'):'Unknown';var mtaLabel=info.mtaStsKnown?(info.hasMtaSts?'Present':'Not detected'):'Unknown';var tlsRptLabel=info.tlsRptKnown?(info.hasTlsRpt?'Present':'Not detected'):'Unknown';techGrid.innerHTML='<div class=\"tech\"><span>Email domain</span><strong>'+esc(emailDomain||'Unknown')+'</strong></div><div class=\"tech\"><span>MX records</span><strong>'+(info.hasMx?'Found':'Not found')+'</strong></div><div class=\"tech\"><span>SPF quality</span><strong>'+esc(spfLabel)+'</strong></div><div class=\"tech\"><span>DMARC policy</span><strong>'+esc(dmarcLabel)+'</strong></div><div class=\"tech\"><span>Domain age</span><strong>'+esc(ageLabel)+'</strong></div><div class=\"tech\"><span>DNSSEC</span><strong>'+esc(dnssecLabel)+'</strong></div><div class=\"tech\"><span>MTA-STS</span><strong>'+esc(mtaLabel)+'</strong></div><div class=\"tech\"><span>TLS-RPT</span><strong>'+esc(tlsRptLabel)+'</strong></div>'"

    if old not in source:
        raise RuntimeError('Email v1.1 UI anchor not found')
    source = source.replace(old, new, 1)

    required = ['SPF quality', 'DMARC policy', 'Domain age', 'DNSSEC', 'MTA-STS', 'TLS-RPT']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Email v1.1 UI guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied email safety v1.1 result details')


if __name__ == '__main__':
    main()
