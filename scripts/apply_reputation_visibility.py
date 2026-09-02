#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-reputation-visibility">
.check-strip{display:block;margin-top:16px;text-align:center}.check-strip .check-label{display:block;margin:0 0 8px;color:var(--text);font-size:12px;font-weight:850}.check-grid{width:min(650px,100%);margin:0 auto;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.check-item{position:relative;display:flex;min-height:54px;align-items:center;gap:8px;padding:9px 10px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 76%,var(--soft));text-align:left}.check-item:before{content:"✓";display:grid;place-items:center;flex:0 0 auto;width:22px;height:22px;border-radius:50%;background:var(--cist-accent-soft);color:var(--cist-accent);font-size:11px;font-weight:950}.check-item strong{display:block;color:var(--text);font-size:11px;line-height:1.15}.check-item small{display:block;margin-top:2px;color:var(--muted);font-size:9px;line-height:1.2}.under-form{margin-top:10px}.under-form .trust-item,.under-form .trust-link{display:inline-flex;align-items:center;gap:4px;padding:4px 7px;border-radius:999px;background:color-mix(in srgb,var(--soft) 70%,transparent);text-decoration:none}.under-form .trust-link{color:var(--cist-accent);font-weight:750}
.actions #deep{flex:1 1 100%;min-height:44px;border-color:var(--cist-accent);background:var(--cist-accent);color:#fff;box-shadow:0 6px 18px rgba(101,120,232,.18)}.actions #deep:hover{filter:brightness(1.04)}.actions #deep:focus-visible{outline:3px solid var(--cist-accent-line);outline-offset:2px}
.reputation{margin-top:14px;padding:14px 15px;border:1px solid var(--line);border-radius:13px;background:var(--soft);font-size:13px;line-height:1.4}.reputation strong{display:block;margin-bottom:3px;color:var(--text);font-size:13px}.reputation span{display:block;color:var(--muted);font-size:12px}.reputation-pending{border-color:var(--cist-accent-line);background:var(--cist-accent-soft)}.reputation-alert{border-width:2px;padding:15px 16px}.reputation-alert.bad{border-color:color-mix(in srgb,var(--red) 58%,var(--line));background:color-mix(in srgb,var(--red) 8%,var(--card));color:var(--red)}.reputation-alert.bad strong{color:var(--red);font-size:15px}.reputation-alert.good{border-color:color-mix(in srgb,var(--green) 42%,var(--line));background:color-mix(in srgb,var(--green) 7%,var(--card))}.reputation-alert.good strong{color:var(--green)}
.result-card.status-high{border-color:color-mix(in srgb,var(--red) 42%,var(--line))}.result-card.status-high .advice{border-color:color-mix(in srgb,var(--red) 28%,var(--line));background:color-mix(in srgb,var(--red) 5%,var(--card))}
@media(max-width:600px){.check-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.check-item{min-height:50px;padding:8px 9px}.under-form{gap:6px}.under-form .trust-item,.under-form .trust-link{padding:3px 6px}.reputation{padding:12px 13px}.reputation-alert{padding:13px 14px}}
</style>
'''

CHECK_BLOCK = '''<div class="check-strip" aria-label="What we check">
      <span class="check-label">What we check</span>
      <div class="check-grid">
        <span class="check-item"><span><strong>Phishing</strong><small>Suspicious patterns</small></span></span>
        <span class="check-item"><span><strong>Malware</strong><small>Dangerous signals</small></span></span>
        <span class="check-item"><span><strong>Redirects</strong><small>Final destination</small></span></span>
        <span class="check-item"><span><strong>Lookalikes</strong><small>Impersonation domains</small></span></span>
      </div>
    </div>'''

TRUST_BLOCK = '''<div class="under-form"><span class="trust-item">🔒 Inputs aren’t stored</span><span class="trust-item">✓ No signup</span><a class="trust-link" href="/qr-code-link-checker">▦ Scan a QR code</a></div>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Reputation visibility patch failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-reputation-visibility"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(
        r'<div class="check-strip" aria-label="What we check">.*?</div>\s*(?=<div class="under-form">)',
        CHECK_BLOCK + '\n    ',
        source,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f'Reputation visibility patch failed: What we check block replaced {count} times')

    source, count = re.subn(
        r'<div class="under-form"><span>🔒 Inputs aren’t stored</span><span>No signup</span><a href="/qr-code-link-checker">Scan a QR code</a></div>',
        TRUST_BLOCK,
        source,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f'Reputation visibility patch failed: trust row replaced {count} times')

    # A heuristic score must never look like a complete safety score.
    source = source.replace('aria-label="Risk score"', 'aria-label="Local signal score"')
    source = source.replace('<span>Risk score</span>', '<span>Local signal score</span>')

    source = replace_once(
        source,
        "else{lastVerdict=status==='low'?'Looks low risk':status==='caution'?'Use caution':status==='high'?'High-risk link':'Check incomplete';summary.textContent=status==='low'?'No obvious high-risk link signals were detected.':status==='caution'?'Some link warning signs need verification before you continue.':status==='high'?'Strong warning signs were detected. Do not open this link.':(data.error||'We could not fully assess this destination.')}",
        "else{lastVerdict=status==='low'?'No obvious local warning signs':status==='caution'?'Use caution':status==='high'?'High-risk link':'Check incomplete';summary.textContent=status==='low'?'Local checks found no obvious high-risk link signals. Reputation has not been checked yet.':status==='caution'?'Some link warning signs need verification before you continue.':status==='high'?'Strong warning signs were detected. Do not open this link.':(data.error||'We could not fully assess this destination.')}",
        'URL quick verdict copy',
    )

    source = replace_once(
        source,
        "if(currentInputType==='email'){deep.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden')}else{deep.classList.remove('hidden')}",
        "if(currentInputType==='email'){deep.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden')}else{deep.classList.remove('hidden');deep.disabled=false;deep.textContent='Check reputation';reputation.className='reputation reputation-pending';reputation.innerHTML='<strong>Reputation not checked yet</strong><span>Check known malware and phishing reports before opening the link.</span>';reputation.classList.remove('hidden')}",
        'pending reputation state',
    )

    source = replace_once(
        source,
        "if(d.status==='known-dangerous'){reputation.className='reputation bad';reputation.textContent='Known threat reported. Do not open this link.';lastStatus='high';lastVerdict='DANGEROUS LINK'}else if(d.status==='no-known-threat'){reputation.className='reputation good';reputation.textContent='No known threat was found by the available reputation sources.'}else if(d.status==='privacy-blocked'){reputation.className='reputation';reputation.textContent='Deep scan was blocked because this URL appears to contain sensitive access data.'}else{reputation.className='reputation';reputation.textContent='External reputation could not be confirmed right now.'}",
        "if(d.status==='known-dangerous'){var googleProvider=(d.providers||[]).find(function(p){return p&&p.provider==='Google Web Risk'});var malwareMatch=!!(googleProvider&&/MALWARE/i.test(String(googleProvider.detail||'')));var threatLabel=malwareMatch?'Known malware threat':'Known threat';card.className='result-card status-high';icon.textContent='×';verdict.textContent=threatLabel;summary.textContent=malwareMatch?'Google Web Risk reported this URL as MALWARE. Do not open it.':'A reputation source reported this URL as dangerous. Do not open it.';adviceText.textContent=guidance('high');advice.classList.remove('hidden');riskMeter.classList.add('hidden');deep.classList.add('hidden');reputation.className='reputation bad reputation-alert';reputation.innerHTML='<strong>Known threat reported — do not open</strong><span>This reputation match overrides the local heuristic score.</span>';lastStatus='high';lastVerdict=threatLabel}else if(d.status==='no-known-threat'){reputation.className='reputation good reputation-alert';reputation.innerHTML='<strong>No known threat found</strong><span>Available reputation sources did not report this URL. This is not a guarantee that the link is safe.</span>';deep.textContent='Recheck reputation'}else if(d.status==='privacy-blocked'){reputation.className='reputation reputation-alert';reputation.innerHTML='<strong>Reputation check blocked for privacy</strong><span>This URL appears to contain sensitive access data, so it was not sent to external threat databases.</span>'}else{reputation.className='reputation reputation-alert';reputation.innerHTML='<strong>Reputation unavailable</strong><span>External reputation could not be confirmed right now. Treat the local result as incomplete.</span>'}",
        'deep reputation result states',
    )

    required = [
        'What we check',
        'class="check-grid"',
        'Local signal score',
        'No obvious local warning signs',
        'Reputation not checked yet',
        'Known threat reported — do not open',
        'This reputation match overrides the local heuristic score.',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Reputation visibility guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Improved scanner check visibility and reputation warning hierarchy')


if __name__ == '__main__':
    main()
