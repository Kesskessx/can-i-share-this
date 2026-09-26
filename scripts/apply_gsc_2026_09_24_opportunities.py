#!/usr/bin/env python3
"""GSC opportunity pass based on the 2026-09-24 Search Console export.

Focuses authority on URLs already earning impressions instead of generating
more pages: Drive troubleshooting, the Drive cluster, and download checking.
"""
from __future__ import annotations
import html, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
START="<!-- GSC_2026_09_24_START -->"; END="<!-- GSC_2026_09_24_END -->"

def page(route):
    rel=route.strip("/")
    for p in (DIST/f"{rel}.html",DIST/rel/"index.html",DIST/rel):
        if p.is_file(): return p
    raise RuntimeError(f"Missing route: {route}")

def meta(doc,key,value,prop=False):
    a="property" if prop else "name"; v=html.escape(value,quote=True)
    pat=rf'(<meta\s+{a}=["\']{re.escape(key)}["\']\s+content=["\'])[^"\']*(["\'])'
    if re.search(pat,doc,re.I):
        return re.sub(pat,lambda m:m.group(1)+v+m.group(2),doc,count=1,flags=re.I)
    return doc.replace("</head>",f'<meta {a}="{key}" content="{v}">\n</head>',1)

def patch(route,title,desc,h1,body):
    p=page(route); d=p.read_text(encoding="utf-8")
    d=re.sub(r"<title>.*?</title>",f"<title>{html.escape(title)}</title>",d,count=1,flags=re.I|re.S)
    d=meta(meta(meta(d,"description",desc),"og:title",title,True),"og:description",desc,True)
    d=re.sub(r"(<h1\b[^>]*>).*?(</h1>)",rf"\1{html.escape(h1)}\2",d,count=1,flags=re.I|re.S)
    d=re.sub(re.escape(START)+r".*?"+re.escape(END),"",d,flags=re.S)
    block=f'\n{START}\n<section class="gsc-opportunity" aria-label="Related checks">{body}</section>\n{END}\n'
    d=d.rsplit("</main>",1)[0]+block+"</main>"+d.rsplit("</main>",1)[1] if "</main>" in d else d.replace("</body>",block+"</body>",1)
    p.write_text(d,encoding="utf-8")

patch("/google-drive-link-not-working",
"Google Drive Link Not Working? Fix Access & Permission Problems",
"Google Drive link not working? Diagnose access denied, wrong-account, sharing-permission, Workspace restriction, moved-file and broken-link problems.",
"Google Drive Link Not Working? Fix Access & Permission Problems",
"""<div class="gsc-op-card"><h2>Find the exact reason your Google Drive link is not working</h2><p>Start with the symptom the recipient sees: <strong>You need access</strong>, a sign-in request, a missing file, or a link that opens for the owner but not for anyone else.</p><ol><li><strong>You need access:</strong> check General access and the recipient account.</li><li><strong>Wrong account:</strong> retry with the Google account that was actually granted access.</li><li><strong>Works for you only:</strong> test the recipient experience in a private window.</li><li><strong>Organization restriction:</strong> Workspace policy may block external sharing.</li><li><strong>File unavailable:</strong> confirm it was not deleted, moved, or transferred with different permissions.</li></ol><div class="gsc-op-links"><a href="/google-drive-link-checker">Test the Drive link</a><a href="/is-my-google-drive-link-public">Check whether the link is public</a><a href="/google-drive-permission-checker">Check Drive permissions</a><a href="/check-google-drive-link-without-signing-in">Test without signing in</a></div></div>""")

patch("/google-drive-link-checker",
"Google Drive Link Checker — Test Access Before Sharing",
"Check a Google Drive link before sharing. Test recipient-facing access, permission walls, sign-in requirements and destination signals.",
"Google Drive Link Checker",
"""<div class="gsc-op-card"><h2>Google Drive troubleshooting</h2><p>If the URL is valid but the recipient still cannot open it, use the dedicated troubleshooting pages instead of repeatedly changing the link.</p><div class="gsc-op-links"><a href="/google-drive-link-not-working">Google Drive link not working</a><a href="/is-my-google-drive-link-public">Is my Drive link public?</a><a href="/google-drive-permission-checker">Google Drive permission checker</a><a href="/check-google-drive-link-without-signing-in">Check a Drive link without signing in</a></div></div>""")


patch("/is-my-google-drive-link-public",
"Is My Google Drive Link Public? Check Sharing Access",
"Check whether a Google Drive link is accessible to anyone with the link or restricted to specific accounts. Verify recipient access before sharing.",
"Is My Google Drive Link Public? Check Sharing Access",
"""<div class="gsc-op-card"><h2>How to tell if your Google Drive link is public</h2><p><strong>A Drive link can be opened without a specific invitation when General access is set to Anyone with the link.</strong> If General access is Restricted, only accounts explicitly granted access can open it. A Google Workspace administrator can also limit external sharing.</p><ol><li>Open the file or folder in Google Drive and choose <strong>Share</strong>.</li><li>Check <strong>General access</strong>: Anyone with the link means the URL can be opened by people who have it; Restricted means access is limited to approved accounts.</li><li>Use a private browser window or a signed-out session to test the recipient experience.</li><li>If the link still asks for access, check Workspace restrictions and the exact Google account being used.</li></ol><div class="gsc-op-links"><a href="/google-drive-link-checker">Test the Drive link</a><a href="/google-drive-permission-checker">Check Drive permissions</a><a href="/google-drive-anyone-with-the-link-vs-restricted">Anyone with the link vs Restricted</a></div></div>""")

patch("/download-link-checker",
"Download Link Checker — Check a File URL Before Opening",
"Check a download link before opening a file. Inspect redirects, destination-domain mismatches, suspicious URL signals and unexpected download context.",
"Download Link Checker",
"""<div class="gsc-op-card"><h2>Check the destination before you download</h2><p>A download link can redirect away from the domain you expect or disguise an unexpected file type. Check the URL first, then verify the final domain and the context in which you received the file.</p><ul><li>Compare the final destination with the expected website.</li><li>Treat unexpected executables, scripts, archives and macro-enabled files with extra caution.</li><li>Be more cautious with unsolicited invoices, delivery notices, job files and account alerts.</li></ul><div class="gsc-op-links"><a href="/malware-link-checker">Malware link checker</a><a href="/safe-link-checker">Safe link checker</a><a href="/how-to-check-if-a-link-is-safe">Manual link safety guide</a></div></div>""")

# Reinforce contextual links from the main checker without adding new URLs.
p=page("/safe-link-checker"); d=p.read_text(encoding="utf-8")
needle="<!-- GSC_2026_09_24_HOME_LINKS -->"
if needle not in d:
    block=f'{needle}<section class="gsc-opportunity" aria-label="Popular specialized checks"><div class="gsc-op-card"><h2>Specialized link checks</h2><div class="gsc-op-links"><a href="/download-link-checker">Check a download link</a><a href="/google-drive-link-checker">Check a Google Drive link</a><a href="/google-drive-link-not-working">Fix a Drive link that is not working</a></div></div></section>'
    d=d.rsplit("</main>",1)[0]+block+"</main>"+d.rsplit("</main>",1)[1] if "</main>" in d else d.replace("</body>",block+"</body>",1)
    p.write_text(d,encoding="utf-8")
print("Applied GSC 2026-09-24 opportunity pass")
