#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Technical-details copy failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    source = replace_once(
        source,
        '<details id="technical" class="technical hidden"><summary>Technical details</summary><div id="tech-grid" class="tech-grid"></div><ul id="providers" class="providers"></ul></details>',
        '<details id="technical" class="technical hidden"><summary>Technical details <span class="advanced-label">(advanced)</span></summary><p class="technical-help">For advanced users. These technical signals help explain the result; they are not a guarantee that a sender or link is safe.</p><div id="tech-grid" class="tech-grid"></div><ul id="providers" class="providers"></ul></details>',
        'advanced summary and explanation'
    )

    source = replace_once(
        source,
        'details.technical summary{cursor:pointer;color:var(--muted);font-size:13px;font-weight:750}.tech-grid',
        'details.technical summary{cursor:pointer;color:var(--muted);font-size:13px;font-weight:750}.advanced-label{font-weight:600;opacity:.82}.technical-help{margin:10px 0 0;color:var(--muted);font-size:12px;line-height:1.45}.tech-grid',
        'technical help styles'
    )

    old_labels = [
        ('<span>Final host</span>', '<span>Final destination</span>'),
        ('<span>HTTP status</span>', '<span>Website response</span>'),
        ('<span>Redirects</span>', '<span>Redirects followed</span>'),
        ('<span>MX records</span>', '<span>Mail servers (MX)</span>'),
        ('<span>SPF quality</span>', '<span>SPF protection</span>'),
        ('<span>DMARC policy</span>', '<span>DMARC protection</span>'),
        ('<span>DNSSEC</span>', '<span>DNSSEC protection</span>'),
    ]
    for old, new in old_labels:
        if old not in source:
            raise RuntimeError(f'Technical-details copy failed: missing label {old}')
        source = source.replace(old, new)

    old_values = (
        "var spfLabel=info.spfQuality&&info.spfQuality!=='unknown'?String(info.spfQuality).replace(/-/g,' '):(info.hasSpf?'Found':'Not found');"
        "var dmarcLabel=info.hasDmarc?(info.dmarcPolicy?String(info.dmarcPolicy).toUpperCase():'Found'):'Not found';"
        "var ageLabel=Number.isFinite(info.domainAgeDays)?info.domainAgeDays+' days':'Unavailable';"
        "var dnssecLabel=info.dnssecKnown?(info.hasDnssec?'Present':'Not detected'):'Unknown';"
        "var mtaLabel=info.mtaStsKnown?(info.hasMtaSts?'Present':'Not detected'):'Unknown';"
        "var tlsRptLabel=info.tlsRptKnown?(info.hasTlsRpt?'Present':'Not detected'):'Unknown';"
    )
    new_values = (
        "var spfRaw=info.spfQuality&&info.spfQuality!=='unknown'?String(info.spfQuality):'';"
        "var spfLabels={strict:'Strict (-all)',softfail:'Soft fail (~all)',permissive:'Very permissive (+all)',neutral:'Neutral (?all)','invalid-multiple':'Invalid: multiple records',present:'Present',missing:'Not found'};"
        "var spfLabel=spfRaw?(spfLabels[spfRaw]||spfRaw.replace(/-/g,' ')):(info.hasSpf?'Present':'Not found');"
        "var dmarcRaw=info.dmarcPolicy?String(info.dmarcPolicy).toLowerCase():'';"
        "var dmarcLabels={none:'Monitoring only (p=none)',quarantine:'Quarantine requested (p=quarantine)',reject:'Reject requested (p=reject)'};"
        "var dmarcLabel=info.hasDmarc?(dmarcRaw?(dmarcLabels[dmarcRaw]||dmarcRaw):'Present'):'Not found';"
        "var ageLabel=Number.isFinite(info.domainAgeDays)?info.domainAgeDays+' days':'Could not verify';"
        "var dnssecLabel=info.dnssecKnown?(info.hasDnssec?'Present':'Not detected'):'Could not determine';"
        "var mtaLabel=info.mtaStsKnown?(info.hasMtaSts?'Present':'Not detected'):'Could not determine';"
        "var tlsRptLabel=info.tlsRptKnown?(info.hasTlsRpt?'Present':'Not detected'):'Could not determine';"
    )
    source = replace_once(source, old_values, new_values, 'friendly email technical values')

    required = [
        'Technical details <span class="advanced-label">(advanced)</span>',
        'For advanced users. These technical signals help explain the result',
        'Final destination',
        'Website response',
        'Redirects followed',
        'Mail servers (MX)',
        'SPF protection',
        'DMARC protection',
        'Monitoring only (p=none)',
        'Could not verify',
        'Could not determine',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Technical-details copy guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Made advanced technical details clearer while keeping them collapsed by default')


if __name__ == '__main__':
    main()
