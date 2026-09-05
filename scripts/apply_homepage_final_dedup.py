#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def strip_container_with_text(source: str, needle: str, tags=('section','div','aside')) -> tuple[str, bool]:
    for tag in tags:
        pattern = re.compile(rf'<{tag}\b[^>]*>.*?{re.escape(needle)}.*?</{tag}>', re.I | re.S)
        matches = list(pattern.finditer(source))
        if not matches:
            continue
        match = min(matches, key=lambda m: len(m.group(0)))
        return source[:match.start()] + source[match.end():], True
    return source, False


def visible_source(source: str) -> str:
    cleaned = re.sub(r'<script\b[^>]*>.*?</script>', '', source, flags=re.I | re.S)
    cleaned = re.sub(r'<style\b[^>]*>.*?</style>', '', cleaned, flags=re.I | re.S)
    return cleaned


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    # Remove static copies when possible.
    source, _ = strip_container_with_text(source, 'What we check')
    source = re.sub(
        r'<(?:p|div|span|strong|b)[^>]*>\s*See the real destination before you open a link\.?\s*</(?:p|div|span|strong|b)>',
        '', source, count=1, flags=re.I | re.S
    )
    source = re.sub(r'\s*<a\b[^>]*href=["\']/security["\'][^>]*>\s*Security\s*</a>', '', source, count=1, flags=re.I)
    source, _ = strip_container_with_text(source, 'Is Can I Share This? related to ShareThis?')

    # Runtime cleanup handles blocks assembled by earlier homepage scripts.
    cleanup_js = r'''<script id="homepage-final-dedup-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function removeClosest(el){if(!el)return;var box=el.closest('section,aside');if(!box){box=el;while(box.parentElement&&norm(box.parentElement.textContent).length<900)box=box.parentElement}if(box&&box!==document.body)box.remove()}
function run(){
  document.querySelectorAll('h2,h3,h4,strong,b,p,div,span').forEach(function(el){
    var t=norm(el.textContent);
    if(t==='What we check')removeClosest(el);
    if(t==='See the real destination before you open a link.'||t==='See the real destination before you open a link')removeClosest(el);
    if(t==='Is Can I Share This? related to ShareThis?')removeClosest(el);
  });
  document.querySelectorAll('a[href="/security"]').forEach(function(a){
    var prev=a.previousElementSibling,next=a.nextElementSibling;a.remove();
    if(prev&&prev.tagName==='I'&&norm(prev.textContent)==='·')prev.remove();
    else if(next&&next.tagName==='I'&&norm(next.textContent)==='·')next.remove();
  });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();</script>'''
    source = source.replace('</body>', cleanup_js + '\n</body>', 1)

    # Remove separator artifacts left by static footer-link deletion.
    source = re.sub(r'(<div class="footer-resource-links">)\s*<i[^>]*>·</i>', r'\1', source, flags=re.I)
    source = re.sub(r'<i[^>]*>·</i>\s*(</div>)', r'\1', source, flags=re.I)
    source = re.sub(r'(<i[^>]*>·</i>\s*){2,}', '<i aria-hidden="true">·</i>', source, flags=re.I)

    visible = visible_source(source)
    if re.search(r'href=["\']/security["\']', visible, re.I):
        raise RuntimeError('Visible Security footer link survived final homepage cleanup')

    required = [
        'Private by design · No account required',
        'URL', 'Email', 'Message', 'Social profile', 'QR', 'Image', 'File', 'Crypto address',
        'Supported Checks', 'About', 'Business inquiries',
        'No scanner can guarantee that a link or sender is safe.',
        '@CanIShareLink',
        'homepage-final-dedup-script',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Homepage cleanup removed required content: {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Removed remaining visible homepage duplicate sections')


if __name__ == '__main__':
    main()
