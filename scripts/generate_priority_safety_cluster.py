#!/usr/bin/env python3
from pathlib import Path
import html, json, re

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
HOST='https://canisharethis.com'

PAGES=[
('/scam-link-checker','scam link checker','Scam Link Checker — Check Suspicious URLs Before You Trust Them','Scam Link Checker: Check a Suspicious URL Before You Trust It','Check a suspicious link for deceptive domains, redirects, risky downloads and known threat signals before you open or share it.'),
('/phishing-link-checker','phishing link checker','Phishing Link Checker — Check a Suspicious URL Before Login','Phishing Link Checker: Check a URL Before You Sign In','Check a suspicious URL for phishing warning signs such as lookalike domains, unexpected redirects, credential requests and known threat reports.'),
('/qr-scam-checker','QR scam checker','QR Scam Checker — Check a QR Code Before You Open It','QR Scam Checker: Check a QR Code Before You Open It','Scan or upload a QR code, reveal its destination and check the resulting URL for scam, phishing and redirect warning signs before opening it.'),
('/email-scam-checker','email scam checker','Email Scam Checker — Check a Suspicious Email Address','Email Scam Checker: Check a Suspicious Email Address','Check a suspicious email address and its domain for structural warning signs before replying, paying or sharing sensitive information.'),
('/whatsapp-scam-checker','WhatsApp scam checker','WhatsApp Scam Checker — Check Suspicious Links and Messages','WhatsApp Scam Checker: Check a Suspicious Link or Message','Check links and suspicious details received on WhatsApp before you open, reply, pay or share personal information.'),
('/sms-scam-checker','SMS scam checker','SMS Scam Checker — Check Suspicious Text Message Links','SMS Scam Checker: Check a Suspicious Text Message Link','Check links from suspicious SMS messages for phishing, fake delivery, payment and account-warning signals before opening them.'),
('/short-url-checker','short URL checker','Short URL Checker — Reveal and Check Shortened Links','Short URL Checker: Check the Destination Behind a Short Link','Check shortened URLs such as bit.ly, t.co and TinyURL, follow their redirects and review the final destination before clicking.'),
('/fake-website-checker','fake website checker','Fake Website Checker — Check If a Site Looks Suspicious','Fake Website Checker: Check a Suspicious Website','Check a website for lookalike domains, suspicious redirects, risky downloads and known threat signals before entering credentials or payment details.'),
('/download-safety-checker','download safety checker','Download Safety Checker — Check a Download Link Before Opening','Download Safety Checker: Check a File Link Before You Download','Check a download URL for risky file types, deceptive destinations, redirects and known threat signals before downloading or running a file.'),
]

COMMON=[
('What this checker looks for','Can I Share This? combines URL structure, redirect behavior, destination changes, file-type signals and configured threat-reputation sources. The result is designed to highlight warning signs, not to promise that an item is safe.'),
('Why context still matters','Scammers often use urgency, impersonation and familiar brands to make a request feel legitimate. A technically ordinary link can still be part of a scam, so verify unexpected requests for passwords, payments, codes or downloads through the official service.'),
('How to use the result','Treat a high-risk result as a reason to stop. Treat a low-risk result as one piece of evidence rather than a guarantee. If the request involves money, credentials or account recovery, open the official app or type the known website address yourself.'),
]

SPECIFIC={
'/scam-link-checker':('Common scam-link warning signs','Unexpected payment requests, fake delivery notices, account suspension warnings, investment promises, prize claims and requests to move a conversation off-platform are common scam contexts.'),
'/phishing-link-checker':('Phishing signs to check','Look for a domain that does not match the brand, small spelling changes, unexpected sign-in prompts, requests for one-time codes and pages that imitate a familiar login screen.'),
'/qr-scam-checker':('Why QR codes need checking','A QR code hides its destination until it is decoded. Stickers placed over legitimate codes, fake parking-payment codes and malicious restaurant or parcel QR codes can redirect to phishing or payment pages.'),
'/email-scam-checker':('What an email-address check can tell you','A domain can be checked for structural and mail-related signals, but a valid address does not prove the sender owns a claimed identity. Always verify sensitive requests independently.'),
'/whatsapp-scam-checker':('Common WhatsApp scam patterns','Impersonation, investment groups, fake job offers, parcel messages, account-recovery requests and urgent money transfers are common. Check any destination before following instructions.'),
'/sms-scam-checker':('Common SMS scam patterns','Delivery failures, unpaid tolls, bank alerts, tax refunds and account warnings are frequently used to push recipients toward a phishing page. Do not rely on the sender name alone.'),
'/short-url-checker':('Why short links deserve extra scrutiny','Shorteners hide the final hostname. The important evidence is where the redirect chain ends, whether the destination matches the claimed service and whether the request makes sense.'),
'/fake-website-checker':('Fake-site warning signs','Lookalike domains, copied branding, newly created domains, unusual checkout flows, impossible discounts, missing contact details and pressure to pay by irreversible methods are useful warning signs.'),
'/download-safety-checker':('Download-link warning signs','Unexpected .exe, .msi, .apk, archive or disk-image downloads deserve extra caution. A trusted-looking cloud-storage link can still host a malicious file.'),
}

FAQ=[
('Can a checker prove that something is safe?','No. A checker can reduce uncertainty by finding warning signs and known threats, but new, targeted or context-dependent scams may not be listed anywhere yet.'),
('Does HTTPS mean a site is legitimate?','No. HTTPS encrypts the connection to a domain. Scam and phishing sites can also use valid TLS certificates.'),
('Should I open the link if no warning is found?','Only if the request and destination make sense. For passwords, payments, recovery codes or downloads, independently verify the request first.'),
]

def page_html(path,keyword,title,h1,desc):
    related=''.join(f'<a href="{p}">{html.escape(h)}</a>' for p,k,t,h,d in PAGES if p!=path)[:100000]
    sec=''.join(f'<section><h2>{html.escape(h)}</h2><p>{html.escape(p)}</p></section>' for h,p in [SPECIFIC[path]]+COMMON)
    faq_items=''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q,a in FAQ)
    faq_schema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    breadcrumb={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Can I Share This?","item":HOST+'/'},{"@type":"ListItem","position":2,"name":h1,"item":HOST+path}]}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{HOST+path}"><meta name="robots" content="index,follow"><script type="application/ld+json">{json.dumps(breadcrumb,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(faq_schema,separators=(',',':'))}</script><style>body{{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#071018;color:#eaf2f7;line-height:1.65}}main{{max-width:900px;margin:auto;padding:42px 20px 72px}}a{{color:#65d7ff}}.back{{display:inline-block;margin-bottom:28px}}h1{{font-size:clamp(34px,6vw,58px);line-height:1.03;margin:0 0 18px}}h2{{font-size:24px;margin-top:36px}}.lead{{font-size:19px;color:#b8c7d2;max-width:760px}}.cta{{display:inline-block;margin:18px 0 30px;padding:13px 18px;border-radius:12px;background:#eaf2f7;color:#071018;text-decoration:none;font-weight:700}}section,details{{border-top:1px solid #1d2b36;padding-top:20px}}details{{padding:16px 0}}summary{{font-weight:700;cursor:pointer}}.related{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:16px}}.related a{{padding:12px;border:1px solid #1d2b36;border-radius:10px;text-decoration:none;background:#0c1720}}</style></head><body><main><a class="back" href="/">← Main safety checker</a><p>ONLINE SAFETY CHECK</p><h1>{html.escape(h1)}</h1><p class="lead">{html.escape(desc)}</p><a class="cta" href="/#scan-form">Check now</a>{sec}<section><h2>Related safety checks</h2><div class="related">{related}</div></section><section><h2>Frequently asked questions</h2>{faq_items}</section></main></body></html>'''

def main():
    DIST.mkdir(exist_ok=True)
    for row in PAGES:
        path=row[0].strip('/')
        out=DIST/path/'index.html'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(page_html(*row),encoding='utf-8')
    sitemap=DIST/'sitemap.xml'
    if sitemap.exists():
        text=sitemap.read_text(encoding='utf-8')
        for path,*_ in PAGES:
            loc=f'<loc>{HOST+path}</loc>'
            if loc not in text:
                entry=f'<url><loc>{HOST+path}</loc></url>'
                text=text.replace('</urlset>',entry+'\n</urlset>')
        sitemap.write_text(text,encoding='utf-8')
    hub=DIST/'safe-link-checker'/'index.html'
    if hub.exists():
        text=hub.read_text(encoding='utf-8')
        if 'id="priority-safety-cluster"' not in text:
            links=''.join(f'<a href="{p}">{html.escape(h)}</a>' for p,k,t,h,d in PAGES)
            block=f'<section id="priority-safety-cluster"><h2>Specialized safety checks</h2><div class="related">{links}</div></section>'
            text=text.replace('</main>',block+'</main>',1) if '</main>' in text else text.replace('</body>',block+'</body>',1)
            hub.write_text(text,encoding='utf-8')
    print(f'Generated {len(PAGES)} priority safety SEO pages with internal linking')

if __name__=='__main__': main()
