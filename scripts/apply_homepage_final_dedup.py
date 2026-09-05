#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def visible_source(source: str) -> str:
    cleaned = re.sub(r'<script\b[^>]*>.*?</script>', '', source, flags=re.I | re.S)
    cleaned = re.sub(r'<style\b[^>]*>.*?</style>', '', cleaned, flags=re.I | re.S)
    return cleaned


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    # Safe static removals only: exact leaf sentence + exact footer link.
    source = re.sub(
        r'<(?:p|span|strong|b)[^>]*>\s*See the real destination before you open a link\.?\s*</(?:p|span|strong|b)>',
        '', source, count=1, flags=re.I | re.S
    )
    source = re.sub(r'\s*<a\b[^>]*href=["\']/security["\'][^>]*>\s*Security\s*</a>', '', source, count=1, flags=re.I)

    # Runtime cleanup handles blocks assembled or reshaped by earlier homepage scripts.
    cleanup_js = r'''<script id="homepage-final-dedup-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function removeChecks(el){
  var node=el;
  for(var i=0;i<5&&node&&node!==document.body;i++,node=node.parentElement){
    var t=norm(node.textContent);
    if(t.indexOf('What we check')>=0&&t.indexOf('Fake websites')>=0&&t.indexOf('Harmful files')>=0&&t.length<900){node.remove();return;}
  }
  if(el.parentElement)el.parentElement.remove();else el.remove();
}
function removeShareThis(el){
  var node=el;
  for(var i=0;i<4&&node&&node!==document.body;i++,node=node.parentElement){
    var t=norm(node.textContent);
    if(t.indexOf('Is Can I Share This? related to ShareThis?')>=0&&t.indexOf('independent safety-checking service')>=0&&t.length<650){node.remove();return;}
  }
  var next=el.nextElementSibling;if(next&&norm(next.textContent).indexOf('No. Can I Share This? is an independent')===0)next.remove();el.remove();
}
function run(){
  document.querySelectorAll('h2,h3,h4,strong,b,p,div,span').forEach(function(el){
    var t=norm(el.textContent);
    if(t==='What we check')removeChecks(el);
    else if(t==='See the real destination before you open a link.'||t==='See the real destination before you open a link')el.remove();
    else if(t==='Is Can I Share This? related to ShareThis?')removeShareThis(el);
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
    print('Removed remaining visible homepage duplicate sections safely')


if __name__ == '__main__':
    main()
