#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mega-scanner-home-v1-style">
/* Mega Scanner: one universal paste field + one screenshot entry point. */
#cist-check-selector,.unified-scanner-label,#capability-strip,.cist-input-types-v2{display:none!important}
#image-safety-tools.image-tools{width:min(720px,calc(100% - 28px));margin:10px auto 0!important;padding:10px 12px!important;display:grid!important;grid-template-columns:1fr!important;gap:6px!important;border:1px dashed color-mix(in srgb,var(--line) 88%,transparent)!important;border-radius:14px!important;background:color-mix(in srgb,var(--card) 88%,transparent)!important;min-height:0!important}
#image-safety-tools .image-tool{display:none!important}
#image-safety-tools #choose-image{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-height:44px!important;padding:10px 14px!important;border:1px solid color-mix(in srgb,var(--line) 92%,transparent)!important;border-radius:11px!important;background:color-mix(in srgb,var(--soft) 78%,transparent)!important;color:var(--text)!important;font-size:12px!important;font-weight:850!important;cursor:pointer!important}
#image-safety-tools #choose-image:hover{border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 42%,var(--line))!important;background:color-mix(in srgb,var(--cist-accent,#788ff7) 6%,var(--soft))!important}
#image-safety-tools .image-note{margin:0!important;text-align:center!important;font-size:9.5px!important;line-height:1.35!important;color:var(--muted)!important}
#cist-mega-or{width:min(720px,calc(100% - 28px));margin:7px auto -3px;text-align:center;color:var(--muted);font-size:9.5px;font-weight:800;letter-spacing:.01em}
#cist-mega-badges{width:min(720px,calc(100% - 28px));margin:8px auto 0;display:flex;justify-content:center;gap:6px;flex-wrap:wrap;color:var(--muted);font-size:9px;font-weight:760}
#cist-mega-badges span{padding:4px 7px;border:1px solid color-mix(in srgb,var(--line) 80%,transparent);border-radius:999px;background:color-mix(in srgb,var(--card) 72%,transparent)}
@media(max-width:600px){
 #image-safety-tools.image-tools{width:calc(100% - 24px);padding:9px!important;margin-top:8px!important}
 #image-safety-tools #choose-image{min-height:42px!important}
 #cist-mega-or,#cist-mega-badges{width:calc(100% - 24px)}
 #cist-mega-badges{gap:5px;margin-top:7px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-mega-scanner-home-v1-script">
(function(){
  var input=document.getElementById('url'),form=document.getElementById('scan-form'),tools=document.getElementById('image-safety-tools'),upload=document.getElementById('choose-image');
  if(!input||!form||!tools||!upload)return;
  input.placeholder='Paste a link, email, message, profile or crypto address';
  input.setAttribute('aria-label','Paste anything suspicious to check');
  upload.textContent='Upload screenshot';
  upload.setAttribute('aria-label','Upload a screenshot to analyze');
  var old=document.getElementById('cist-mega-or');if(old)old.remove();
  var label=document.createElement('div');label.id='cist-mega-or';label.textContent='or analyze a screenshot';tools.insertAdjacentElement('beforebegin',label);
  var badges=document.getElementById('cist-mega-badges');if(badges)badges.remove();
  badges=document.createElement('div');badges.id='cist-mega-badges';badges.setAttribute('aria-label','Automatically detected input types');
  ['Links','Emails','Messages','Profiles','QR','Crypto'].forEach(function(x){var s=document.createElement('span');s.textContent=x;badges.appendChild(s)});
  tools.insertAdjacentElement('afterend',badges);
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    source = re.sub(r'\s*<style id="cist-mega-scanner-home-v1-style">.*?</style>', '', source, count=1, flags=re.S)
    source = re.sub(r'\s*<script id="cist-mega-scanner-home-v1-script">.*?</script>', '', source, count=1, flags=re.S)

    # Screenshot evidence is cross-checked inside the existing image scanner; avoid a duplicate second scan.
    source = source.replace('Running it through the existing safety scanner…', 'Cross-checked with the relevant safety scanners.')
    source = source.replace("box.classList.remove('hidden');runTarget(target)", "box.classList.remove('hidden')", 1)

    if '/api/analyze' not in source:
        raise RuntimeError('Universal analyze endpoint missing from homepage')
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')

    source = source.replace('</head>', STYLE + '\n</head>', 1)
    source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'cist-mega-scanner-home-v1-style',
        'Upload screenshot',
        'Paste anything suspicious to check',
        '/api/analyze',
        '#cist-check-selector',
        'or analyze a screenshot'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Mega Scanner homepage guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied Mega Scanner homepage: universal paste + screenshot upload')


if __name__ == '__main__':
    main()
