#!/usr/bin/env python3
from pathlib import Path
import html
import json
import re

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
HOST='https://canisharethis.com'


def esc(v, quote=False): return html.escape(str(v), quote=quote)
def j(v): return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

STYLE='''
:root{color-scheme:light dark;--bg:#f6f7f9;--card:#fff;--text:#17191d;--muted:#69717e;--line:#e1e5ea;--soft:#f1f3f6;--accent:#6f7fe8;--green:#18794e;--amber:#a15c00}
@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a7adb7;--line:#2a2f37;--soft:#1b1f25;--accent:#8ea2ff;--green:#76d596;--amber:#ffc268}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}a{color:inherit}.wrap{width:min(860px,calc(100% - 30px));margin:auto}header{border-bottom:1px solid var(--line)}header .wrap{height:64px;display:flex;align-items:center;justify-content:space-between}.brand{text-decoration:none;font-weight:900;letter-spacing:-.025em}.brand span{color:var(--accent)}.navlink{font-size:13px;color:var(--muted)}main{padding:48px 0 72px}.kicker{font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.11em;color:var(--muted)}h1{font-size:clamp(38px,7vw,62px);line-height:1.02;letter-spacing:-.045em;margin:10px 0 16px}.intro{max-width:720px;color:var(--muted);font-size:18px;margin:0 0 28px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:22px 0 30px}.mini{border:1px solid var(--line);background:var(--card);border-radius:16px;padding:16px}.mini strong{display:block;font-size:13px}.mini span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.card{border:1px solid var(--line);background:var(--card);border-radius:19px;padding:clamp(20px,4vw,30px);margin:12px 0}.card h2{margin:0 0 12px;font-size:24px;letter-spacing:-.025em}.card h3{font-size:15px;margin:18px 0 6px}.card p{margin:0 0 13px}.card p:last-child{margin-bottom:0}.card ul{margin:8px 0 0;padding-left:20px}.card li{margin:7px 0}.tag{display:inline-flex;padding:4px 8px;border-radius:999px;background:var(--soft);font-size:11px;font-weight:800;margin:2px 4px 2px 0}.warning{border-left:3px solid var(--amber);padding-left:13px;color:var(--muted)}.good{color:var(--green);font-weight:800}.cta{margin-top:22px;text-align:center}.button{display:inline-flex;padding:11px 16px;background:var(--text);color:var(--bg);border-radius:12px;text-decoration:none;font-weight:850}footer{border-top:1px solid var(--line);padding:22px 0 30px;color:var(--muted);font-size:12px;text-align:center}@media(max-width:640px){main{padding:34px 0 54px}.grid{grid-template-columns:1fr}.intro{font-size:16px}.card{border-radius:16px}}
'''

def security_page():
    title='Security & Privacy — Can I Share This?'
    desc='How Can I Share This? handles links, images, QR codes, external security providers, analytics and the limits of safety verdicts.'
    schema={"@context":"https://schema.org","@type":"WebPage","name":title,"url":HOST+'/security',"description":desc,"isPartOf":{"@type":"WebSite","name":"Can I Share This?","url":HOST+'/'}}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc,True)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{HOST}/security"><script type="application/ld+json">{j(schema)}</script><style>{STYLE}</style></head><body>
<header><div class="wrap"><a class="brand" href="/">Can I Share <span>This?</span></a><a class="navlink" href="/methodology">Methodology</a></div></header>
<main class="wrap"><div class="kicker">Security & transparency</div><h1>What happens when you analyze something</h1><p class="intro">Can I Share This? combines local checks, server-side analysis and selected external security services. This page explains what is processed, what may leave the service, and what a verdict does not prove.</p>
<div class="grid"><div class="mini"><strong>Privacy-first</strong><span>No account is required to run the scanner.</span></div><div class="mini"><strong>External checks are limited</strong><span>Sensitive URLs are blocked from reputation lookups when known private-token patterns are detected.</span></div><div class="mini"><strong>No safety guarantee</strong><span>A low-risk result means no known danger was found in the checks performed.</span></div></div>
<section class="card"><h2>What Can I Share This? processes</h2><p>The scanner can receive links, email addresses, crypto addresses, text extracted from messages, QR-code destinations, and screenshots or photos. Different input types use different checks.</p><p><span class="tag">URL structure</span><span class="tag">Redirects</span><span class="tag">Domain context</span><span class="tag">Email domain checks</span><span class="tag">File indicators</span><span class="tag">QR decoding</span><span class="tag">Image analysis</span></p></section>
<section class="card"><h2>Links and external threat intelligence</h2><p>Public URLs may be compared with external phishing or malware intelligence such as Google Web Risk. Before an eligible URL is shared externally, the backend checks for known sensitive query-parameter patterns such as access tokens, authorization tokens, signatures and secrets.</p><p class="warning">If a URL contains a recognized sensitive parameter, the external reputation lookup is blocked. This protection is deliberately conservative, but no automated filter can recognize every secret format.</p></section>
<section class="card"><h2>Images and screenshots</h2><p>Images selected through <strong>Photo</strong> or <strong>Camera</strong> are sent to the image-analysis endpoint and then to Google Gemini for visual interpretation. Can I Share This? does not intentionally write those image bytes to persistent application storage.</p><p>Google is an external processor for this feature, so the image leaves Can I Share This? infrastructure during analysis. Provider-side handling is governed by Google's applicable Gemini/API terms and account configuration.</p><p>When the browser supports it, QR codes are also decoded locally with the browser's barcode detector. If a URL is recovered from the QR code, that destination is then sent through the normal link-safety pipeline.</p></section>
<section class="card"><h2>What is not sent with a normal link check</h2><ul><li>Your browser cookies or signed-in web session are not forwarded to the destination.</li><li>The scanner does not intentionally send passwords entered elsewhere in your browser.</li><li>Anonymous usage counters record aggregate scan activity, not the scanned content itself.</li></ul></section>
<section class="card"><h2>How verdicts are produced</h2><p>The system combines observable signals rather than relying on a single AI opinion. Technical checks can include URL structure, destination changes, domain age context, content type, file/download indicators and known-threat reputation. AI is used for interpreting images and context, not as the sole authority for link safety.</p><p><span class="good">Low risk</span> means no known danger was found in the checks performed. <strong>Caution</strong> means one or more signals deserve verification. <strong>High risk</strong> means strong warning signs or a known threat were found.</p></section>
<section class="card"><h2>What the scanner cannot guarantee</h2><p>No scanner can certify that a site, sender, image or file is safe. New threats may not yet exist in reputation databases, pages can change after a scan, legitimate services can be compromised, and a technically valid email or crypto address can still belong to a scammer.</p><p>For passwords, payments, recovery phrases, one-time codes or identity documents, independently verify the destination even when the result is low risk.</p></section>
<section class="card"><h2>Service dependencies</h2><p>Some checks depend on external services and public infrastructure. Current integrations can include:</p><ul><li><strong>Google Web Risk</strong> for eligible known-threat URL checks;</li><li><strong>Google Gemini</strong> for screenshot and photo interpretation;</li><li><strong>RDAP infrastructure</strong> for domain registration-age context;</li><li>DNS and destination HTTP responses for reachability and redirect analysis.</li></ul><p>If an external service is unavailable, the result should be treated as incomplete rather than as evidence that the input is safe.</p></section>
<section class="card"><h2>Data retention and analytics</h2><p>The product is designed around transient analysis. The application does not intentionally maintain a searchable history of user-submitted links or uploaded images. Aggregate counters may store totals by input category, and operational hosting/provider logs can exist independently of the application logic.</p></section>
<div class="cta"><a class="button" href="/">Open the scanner</a></div></main><footer><div class="wrap"><a href="/methodology">Methodology</a> · <a href="/supported-checks">Supported Checks</a> · <a href="/about">About</a></div></footer></body></html>'''


def patch_methodology():
    p=DIST/'methodology.html'
    if not p.is_file(): return
    s=p.read_text(encoding='utf-8')
    s=s.replace('How the link safety check works','How the safety scanner works',1)
    s=s.replace('Got a suspicious link?','Got something suspicious?',1)
    s=s.replace('Paste it into the checker before you open it.','Paste it, upload it or photograph it before you trust it.',1)
    s=s.replace('Analyze the link','Open the scanner',1)
    marker='<section class="card"><h2>What the scanner cannot guarantee</h2>'
    extra='''<section class="card"><h2>Images, QR codes and AI</h2><p>Screenshot and photo analysis uses Google Gemini to interpret visible content such as text, brand clues, links and suspicious context. The AI result is combined with technical checks when a URL, email or QR destination can be extracted; AI is not treated as the sole proof that something is safe or dangerous.</p><p>On supported browsers, QR decoding is attempted locally first. Uploaded image bytes are processed transiently by Can I Share This? and sent to the external AI provider for analysis. See the <a href="/security">Security & Privacy</a> page for data-handling details.</p></section>\n'''
    if marker in s and 'Images, QR codes and AI' not in s: s=s.replace(marker,extra+marker,1)
    p.write_text(s,encoding='utf-8')


def sitemap_add(path):
    p=DIST/'sitemap.xml'
    if not p.is_file(): return
    s=p.read_text(encoding='utf-8')
    url=HOST+path
    if url not in s: s=s.replace('</urlset>',f'  <url><loc>{url}</loc></url>\n</urlset>',1)
    p.write_text(s,encoding='utf-8')

if __name__=='__main__':
    if not DIST.is_dir(): raise RuntimeError('dist missing')
    (DIST/'security.html').write_text(security_page(),encoding='utf-8')
    patch_methodology()
    sitemap_add('/security')
    print('Generated security transparency page and upgraded methodology')
