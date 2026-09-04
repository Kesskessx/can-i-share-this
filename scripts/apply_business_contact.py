#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'dist'/'index.html'
CONTACT=ROOT/'dist'/'contact.html'
MANIFEST=ROOT/'seo'/'SEO_ROUTE_MANIFEST.json'
EMAIL='canisharethis@proton.me'
SUBJECT='Business inquiry — CanIShareThis'
MAILTO=f'mailto:{EMAIL}?subject=Business%20inquiry%20%E2%80%94%20CanIShareThis'

if not HOME.is_file(): raise RuntimeError('Homepage not found')
source=HOME.read_text(encoding='utf-8')

# Add a compact business contact item to the existing footer without adding homepage bulk.
if 'Business inquiries' not in source:
    marker='<a href="/about">About</a>'
    replacement='<a href="/about">About</a><i aria-hidden="true">·</i>\n        <a href="/contact">Business inquiries</a>'
    if marker not in source: raise RuntimeError('Footer About link not found')
    source=source.replace(marker,replacement,1)

# Add direct email link beside social/footer trust area.
if 'footer-business-email' not in source:
    marker='<div class="footer-social">'
    if marker not in source: raise RuntimeError('Footer social area not found')
    source=source.replace(marker,f'<div class="footer-business-email"><a href="{MAILTO}">{EMAIL}</a></div>\n      '+marker,1)
    source=source.replace('.footer-resource-links a,.footer-social a{color:var(--muted);text-decoration:none}', '.footer-resource-links a,.footer-social a,.footer-business-email a{color:var(--muted);text-decoration:none}',1)
    source=source.replace('.footer-resource-links a:hover,.footer-social a:hover{color:var(--text);text-decoration:underline;text-underline-offset:3px}', '.footer-resource-links a:hover,.footer-social a:hover,.footer-business-email a:hover{color:var(--text);text-decoration:underline;text-underline-offset:3px}',1)

HOME.write_text(source,encoding='utf-8')

CONTACT.write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Business & Partnerships | CanIShareThis</title>
<meta name="description" content="Contact CanIShareThis for partnerships, integrations, API opportunities, press, business inquiries, or acquisition discussions.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://canisharethis.com/contact">
<style>
:root{{--bg:#080b12;--card:#101522;--line:rgba(148,163,184,.18);--text:#f8fafc;--muted:#9aa4b2;--accent:#788ff7}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 50% 0,rgba(120,143,247,.08),transparent 34%),var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
a{{color:inherit}}.wrap{{width:min(760px,calc(100% - 32px));margin:0 auto}}header{{padding:24px 0;border-bottom:1px solid var(--line)}}.brand{{font-weight:850;text-decoration:none}}main{{padding:70px 0 80px}}.eyebrow{{font-size:12px;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#9fb0ff}}h1{{font-size:clamp(38px,7vw,64px);line-height:1.02;letter-spacing:-.045em;margin:14px 0 18px}}.lead{{font-size:18px;line-height:1.65;color:var(--muted);max-width:650px}}.card{{margin-top:32px;padding:24px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.018));box-shadow:0 18px 50px rgba(0,0,0,.2)}}.topics{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:20px 0}}.topic{{padding:13px 14px;border:1px solid var(--line);border-radius:12px;color:#dbe3ef;background:rgba(255,255,255,.02)}}.cta{{display:inline-flex;align-items:center;justify-content:center;margin-top:6px;padding:13px 18px;border-radius:12px;background:var(--accent);color:white;text-decoration:none;font-weight:850;box-shadow:0 0 24px rgba(120,143,247,.18)}}.email{{margin-top:14px;color:var(--muted);font-size:13px}}footer{{padding:24px 0;border-top:1px solid var(--line);color:var(--muted);font-size:12px}}@media(max-width:600px){{main{{padding-top:46px}}.topics{{grid-template-columns:1fr}}.card{{padding:18px}}}}
</style></head><body><header><div class="wrap"><a class="brand" href="/">Can I Share This?</a></div></header><main><div class="wrap"><div class="eyebrow">Business & partnerships</div><h1>Work with CanIShareThis</h1><p class="lead">For partnerships, integrations, API opportunities, press, business inquiries, or acquisition discussions, contact us directly.</p><section class="card"><strong>Relevant inquiries</strong><div class="topics"><div class="topic">Partnerships & distribution</div><div class="topic">API & product integrations</div><div class="topic">Press & creator inquiries</div><div class="topic">Acquisition & business discussions</div></div><a class="cta" href="{MAILTO}">Email CanIShareThis</a><div class="email">{EMAIL}</div></section></div></main><footer><div class="wrap">Privacy-first · No signup · <a href="/">Back to scanner</a></div></footer></body></html>''',encoding='utf-8')

# Register the utility contact route for the build audit. Keep it noindex so it does not alter the SEO sitemap.
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
routes=manifest.setdefault('routes',[])
if not any(route.get('path')=='/contact' for route in routes):
    routes.append({
        'path':'/contact','status':'active','index':False,'canonical':'/contact',
        'cluster':'trust-methodology','role':'utility',
        'intent':'contact CanIShareThis for business inquiries',
        'primaryKeyword':'CanIShareThis business contact'
    })
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('Added business contact page, footer inquiry links, and registered /contact route')
