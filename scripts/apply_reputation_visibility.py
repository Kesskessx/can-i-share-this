#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-reputation-visibility">
.check-strip{display:block;margin-top:16px;text-align:center}.check-strip .check-label{display:block;margin:0 0 8px;color:var(--text);font-size:12px;font-weight:850}.check-grid{width:min(650px,100%);margin:0 auto;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.check-item{position:relative;display:flex;min-height:58px;align-items:center;gap:8px;padding:9px 10px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 76%,var(--soft));text-align:left}.check-item:before{content:"✓";display:grid;place-items:center;flex:0 0 auto;width:22px;height:22px;border-radius:50%;background:var(--cist-accent-soft);color:var(--cist-accent);font-size:11px;font-weight:950}.check-item strong{display:block;color:var(--text);font-size:11px;line-height:1.15}.check-item small{display:block;margin-top:3px;color:var(--muted);font-size:9px;line-height:1.25}.under-form{margin-top:10px}.under-form .trust-item,.under-form .trust-link{display:inline-flex;align-items:center;gap:4px;padding:4px 7px;border-radius:999px;background:color-mix(in srgb,var(--soft) 70%,transparent);text-decoration:none}.under-form .trust-link{color:var(--cist-accent);font-weight:750}
.actions #deep{flex:1 1 100%;min-height:46px;border-color:var(--cist-accent);background:var(--cist-accent);color:#fff;box-shadow:0 6px 18px rgba(101,120,232,.18);font-size:14px}.actions #deep:hover{filter:brightness(1.04)}.actions #deep:focus-visible{outline:3px solid var(--cist-accent-line);outline-offset:2px}
.reputation{margin-top:14px;padding:14px 15px;border:1px solid var(--line);border-radius:13px;background:var(--soft);font-size:13px;line-height:1.4}.reputation strong{display:block;margin-bottom:3px;color:var(--text);font-size:13px}.reputation span{display:block;color:var(--muted);font-size:12px}.reputation-pending{border-color:var(--cist-accent-line);background:var(--cist-accent-soft)}.reputation-alert{border-width:2px;padding:15px 16px}.reputation-alert.bad{border-color:color-mix(in srgb,var(--red) 58%,var(--line));background:color-mix(in srgb,var(--red) 8%,var(--card));color:var(--red)}.reputation-alert.bad strong{color:var(--red);font-size:15px}.reputation-alert.good{border-color:color-mix(in srgb,var(--green) 42%,var(--line));background:color-mix(in srgb,var(--green) 7%,var(--card))}.reputation-alert.good strong{color:var(--green)}
.result-card.status-low .status-icon,.result-card.status-low h2{color:var(--cist-accent)}.result-card.status-low.reputation-checked-safe .status-icon,.result-card.status-low.reputation-checked-safe h2{color:var(--green)}.result-card.status-high{border-color:color-mix(in srgb,var(--red) 42%,var(--line))}.result-card.status-high .advice{border-color:color-mix(in srgb,var(--red) 28%,var(--line));background:color-mix(in srgb,var(--red) 5%,var(--card))}
@media(max-width:600px){.check-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.check-item{min-height:56px;padding:8px 9px}.under-form{gap:6px}.under-form .trust-item,.under-form .trust-link{padding:3px 6px}.reputation{padding:12px 13px}.reputation-alert{padding:13px 14px}}
</style>
'''

CHECK_BLOCK = '''<div class="check-strip" aria-label="What we check">
      <span class="check-label">What we check</span>
      <div class="check-grid">
        <span class="check-item"><span><strong>Fake websites</strong><small>Tricks that steal passwords</small></span></span>
        <span class="check-item"><span><strong>Harmful files</strong><small>Malware and unsafe downloads</small></span></span>
        <span class="check-item"><span><strong>Link destination</strong><small>Where the link really goes</small></span></span>
        <span class="check-item"><span><strong>Copycat sites</strong><small>Look-alike website names</small></span></span>
      </div>
    </div>'''

TRUST_BLOCK = '''<div class="under-form"><span class="trust-item">🔒 Nothing you paste is saved</span><span class="trust-item">✓ No account needed</span><a class="trust-link" href="/qr-code-link-checker">▦ Scan a QR code</a></div>'''


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

    # Keep the quick heuristic clearly separate from external threat-list checks.
    source = source.replace('aria-label="Risk score"', 'aria-label="Warning-sign score"')
    source = source.replace('<span>Risk score</span>', '<span>Warning-sign score</span>')

    source = replace_once(
        source,
        "card.className='result-card status-'+status;icon.textContent=status==='low'?'✓':status==='caution'?'!':status==='high'?'×':'?';",
        "card.className='result-card status-'+status;icon.textContent=status==='low'?'i':status==='caution'?'!':status==='high'?'×':'?';",
        'neutral quick-check icon',
    )

    source = replace_once(
        source,
        "else{lastVerdict=status==='low'?'Looks low risk':status==='caution'?'Use caution':status==='high'?'High-risk link':'Check incomplete';summary.textContent=status==='low'?'No obvious high-risk link signals were detected.':status==='caution'?'Some link warning signs need verification before you continue.':status==='high'?'Strong warning signs were detected. Do not open this link.':(data.error||'We could not fully assess this destination.')}",
        "else{lastVerdict=status==='low'?'No obvious warning signs yet':status==='caution'?'Be careful with this link':status==='high'?'Dangerous link signs':'Check incomplete';summary.textContent=status==='low'?'The first check did not find anything obvious. One more security check is recommended before you open the link.':status==='caution'?'We found warning signs. Check the sender and website before you continue.':status==='high'?'Strong warning signs were found. Do not open this link.':(data.error||'We could not fully check this link.')}",
        'plain-language URL quick verdict',
    )

    source = source.replace(
        "If you expected this link, you can continue cautiously. Be extra careful if the message asks for a password, payment, or download.",
        "Before opening this link, run the extra safety check below. The quick check alone cannot confirm that a link is safe.",
        1,
    )

    source = source.replace(
        'Reputation checks share this public URL with external threat databases. Private or signed links may contain access tokens.',
        'This extra check sends the public link to external security services. Do not continue if the URL itself contains a private sign-in code or secret access link.',
        1,
    )

    source = replace_once(
        source,
        "if(currentInputType==='email'){deep.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden')}else{deep.classList.remove('hidden')}",
        "if(currentInputType==='email'){deep.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden')}else{deep.classList.remove('hidden');deep.disabled=false;deep.textContent='Run extra safety check';reputation.className='reputation reputation-pending';reputation.innerHTML='<strong>One more check recommended</strong><span>Compare this link with known malware and phishing reports before opening it.</span>';reputation.classList.remove('hidden')}",
        'plain-language extra-check state',
    )

    source = replace_once(
        source,
        "if(d.status==='known-dangerous'){reputation.className='reputation bad';reputation.textContent='Known threat reported. Do not open this link.';lastStatus='high';lastVerdict='DANGEROUS LINK'}else if(d.status==='no-known-threat'){reputation.className='reputation good';reputation.textContent='No known threat was found by the available reputation sources.'}else if(d.status==='privacy-blocked'){reputation.className='reputation';reputation.textContent='Deep scan was blocked because this URL appears to contain sensitive access data.'}else{reputation.className='reputation';reputation.textContent='External reputation could not be confirmed right now.'}",
        "if(d.status==='known-dangerous'){var googleProvider=(d.providers||[]).find(function(p){return p&&p.provider==='Google Web Risk'});var malwareMatch=!!(googleProvider&&/MALWARE/i.test(String(googleProvider.detail||'')));card.className='result-card status-high';icon.textContent='×';verdict.textContent='Dangerous link';summary.textContent=malwareMatch?\"Google's security service says this link is known to contain harmful software. Do not open it.\":'A security service reported this link as dangerous. Do not open it.';adviceText.textContent='Do not open this link. Close the message and visit the company or service through its official website or app instead.';advice.classList.remove('hidden');riskMeter.classList.add('hidden');deep.classList.add('hidden');whyList.innerHTML='<li>'+esc(malwareMatch?\"Google's security service reported this link as harmful.\":'An external security service reported this link as dangerous.')+'</li>';whyVerdict.classList.remove('hidden');reputation.className='reputation bad reputation-alert';reputation.innerHTML='<strong>Dangerous link — do not open</strong><span>This link appears on a known threat list. The earlier quick score no longer applies.</span>';lastStatus='high';lastVerdict='DANGEROUS LINK'}else if(d.status==='no-known-threat'){card.className='result-card status-low reputation-checked-safe';icon.textContent='✓';verdict.textContent='No known danger found';summary.textContent='The security services checked did not report this link as a known threat. This still cannot guarantee that the link is safe.';riskMeter.classList.add('hidden');whyList.innerHTML='<li>No known danger was reported by the security services we checked.</li>';whyVerdict.classList.remove('hidden');reputation.className='reputation good reputation-alert';reputation.innerHTML='<strong>No known danger found in security lists</strong><span>The services we checked did not report this link. That does not guarantee it is safe.</span>';deep.textContent='Check again';lastStatus='low';lastVerdict='NO KNOWN DANGER FOUND'}else if(d.status==='privacy-blocked'){reputation.className='reputation reputation-alert';reputation.innerHTML='<strong>We did not send this link for the extra check</strong><span>The URL looks like it contains private access information, so we kept it private.</span>'}else{reputation.className='reputation reputation-alert';reputation.innerHTML='<strong>Extra safety check unavailable</strong><span>We could not check the external security lists right now. Do not rely on the quick check alone.</span>'}",
        'plain-language external safety results',
    )

    required = [
        'Fake websites',
        'Harmful files',
        'Link destination',
        'Copycat sites',
        'Nothing you paste is saved',
        'Warning-sign score',
        'No obvious warning signs yet',
        'One more check recommended',
        'Run extra safety check',
        'Dangerous link — do not open',
        'No known danger found in security lists',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Reputation visibility guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Simplified scanner language and made external safety results unmistakable')


if __name__ == '__main__':
    main()
