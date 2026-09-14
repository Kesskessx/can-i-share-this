#!/usr/bin/env python3
"""Apply Search Console opportunity fixes from the 2026-09-14 export.

Targets existing routes only. This runs late in the static build so it can
strengthen metadata, visible copy, and internal linking without creating new
indexable URLs.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
START = "<!-- GSC_2026_09_14_START -->"
END = "<!-- GSC_2026_09_14_END -->"

STYLE = r"""
<style id="gsc-2026-09-14-style">
.gsc-opportunity{max-width:900px;margin:18px auto 0;padding:0 2px}
.gsc-opportunity .gsc-op-card{margin:16px 0;padding:clamp(20px,3vw,30px);border:1px solid var(--line,#e4e7ec);border-radius:20px;background:var(--card,#fff)}
.gsc-opportunity h2{margin:0 0 12px;font-size:clamp(22px,3vw,30px);line-height:1.18;letter-spacing:-.025em}
.gsc-opportunity h3{margin:20px 0 7px;font-size:18px;line-height:1.3}
.gsc-opportunity p{margin:0 0 14px}
.gsc-opportunity ul,.gsc-opportunity ol{margin:12px 0 0;padding-left:22px}
.gsc-opportunity li{margin:8px 0}
.gsc-opportunity .gsc-op-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
.gsc-opportunity .gsc-op-mini{padding:15px;border:1px solid var(--line,#e4e7ec);border-radius:14px;background:var(--card-soft,#f9fafb)}
.gsc-opportunity .gsc-op-mini h3{margin:0 0 6px;font-size:16px}
.gsc-opportunity .gsc-op-note{padding:14px 16px;border-left:3px solid currentColor;background:var(--card-soft,#f9fafb);border-radius:10px}
.gsc-opportunity .gsc-op-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.gsc-opportunity .gsc-op-links a{display:inline-block;padding:10px 12px;border:1px solid var(--line,#e4e7ec);border-radius:12px;text-decoration:none}
.gsc-opportunity .gsc-op-links a:hover{text-decoration:underline}
@media(max-width:680px){.gsc-opportunity .gsc-op-grid{grid-template-columns:1fr}}
</style>
"""


def route_file(route: str) -> Path | None:
    rel = route.strip("/")
    candidates = [DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel]
    if route == "/":
        candidates = [DIST / "index.html"]
    for path in candidates:
        if path.is_file():
            return path
    return None


def set_title(doc: str, title: str) -> str:
    value = html.escape(title)
    return re.sub(r"<title>.*?</title>", f"<title>{value}</title>", doc, count=1, flags=re.I | re.S)


def set_meta(doc: str, key: str, value: str, *, prop: bool = False) -> str:
    attr = "property" if prop else "name"
    escaped = html.escape(value, quote=True)
    pattern = rf'(<meta\s+{attr}=["\']{re.escape(key)}["\']\s+content=["\'])[^"\']*(["\'])'
    if re.search(pattern, doc, flags=re.I):
        return re.sub(pattern, lambda m: m.group(1) + escaped + m.group(2), doc, count=1, flags=re.I)
    tag = f'<meta {attr}="{html.escape(key, quote=True)}" content="{escaped}">'
    return doc.replace("</head>", tag + "\n</head>", 1) if "</head>" in doc else tag + "\n" + doc


def set_first_h1(doc: str, h1: str) -> str:
    value = html.escape(h1)
    return re.sub(r"(<h1\b[^>]*>).*?(</h1>)", rf"\1{value}\2", doc, count=1, flags=re.I | re.S)


def ensure_style(doc: str) -> str:
    if 'id="gsc-2026-09-14-style"' in doc:
        return doc
    return doc.replace("</head>", STYLE + "\n</head>", 1) if "</head>" in doc else STYLE + doc


def inject(doc: str, content: str) -> str:
    doc = re.sub(re.escape(START) + r".*?" + re.escape(END), "", doc, flags=re.S)
    block = f'\n{START}\n<section class="gsc-opportunity" aria-label="Search guidance">\n{content}\n</section>\n{END}\n'
    if "</main>" in doc:
        head, tail = doc.rsplit("</main>", 1)
        return head + block + "</main>" + tail
    if "</body>" in doc:
        return doc.replace("</body>", block + "</body>", 1)
    return doc + block


def patch(
    route: str,
    content: str,
    *,
    title: str | None = None,
    description: str | None = None,
    h1: str | None = None,
) -> None:
    path = route_file(route)
    if not path:
        raise RuntimeError(f"Missing generated route: {route}")

    doc = path.read_text(encoding="utf-8")
    doc = ensure_style(doc)
    if title:
        doc = set_title(doc, title)
        doc = set_meta(doc, "og:title", title, prop=True)
    if description:
        doc = set_meta(doc, "description", description)
        doc = set_meta(doc, "og:description", description, prop=True)
    if h1:
        doc = set_first_h1(doc, h1)
    doc = inject(doc, content)
    path.write_text(doc, encoding="utf-8")
    print(f"GSC opportunity patched {route}")


DRIVE_NOT_WORKING = r"""
<div class="gsc-op-card">
  <h2>Google Drive link not opening? Check these causes first</h2>
  <p>If a Google Drive link is not working for someone else, the URL itself is often fine. The failure usually comes from permissions, the Google account being used, Workspace restrictions, or a file that was moved, deleted, or had its sharing settings changed.</p>
  <div class="gsc-op-grid">
    <div class="gsc-op-mini"><h3>“You need access”</h3><p>The recipient is not included in the file’s current sharing rules.</p></div>
    <div class="gsc-op-mini"><h3>Wrong Google account</h3><p>The file may be shared with one address while Drive opens under another signed-in account.</p></div>
    <div class="gsc-op-mini"><h3>External sharing blocked</h3><p>A Google Workspace administrator can restrict access outside a company, school, or managed domain.</p></div>
    <div class="gsc-op-mini"><h3>File moved or deleted</h3><p>A previously working share link can fail after ownership, location, or availability changes.</p></div>
    <div class="gsc-op-mini"><h3>Incomplete copied link</h3><p>URLs pasted from messages or formatted documents can be truncated or include unwanted punctuation.</p></div>
    <div class="gsc-op-mini"><h3>Sender session hides the problem</h3><p>The owner can open the file because their browser is already authenticated; that does not prove recipient access.</p></div>
  </div>
</div>
<div class="gsc-op-card">
  <h2>Fastest way to diagnose a broken Drive link</h2>
  <ol>
    <li>Test the exact share URL you intend to send.</li>
    <li>Check whether the result indicates a sign-in or permission barrier.</li>
    <li>If the file should be public-by-link, review Google Drive’s General access setting.</li>
    <li>If access should stay private, add the intended recipient’s correct Google account instead of making the file public.</li>
    <li>Re-test after changing permissions.</li>
  </ol>
  <p class="gsc-op-note">A link checker can identify recipient-facing access signals, but it cannot override Google Drive permissions or Workspace administrator policies.</p>
  <div class="gsc-op-links">
    <a href="/google-drive-link-checker">Check a Google Drive link</a>
    <a href="/google-drive-permission-checker">Check Drive permissions</a>
    <a href="/check-google-drive-link-without-signing-in">Test without signing in</a>
  </div>
</div>
"""

DROPBOX_NOT_WORKING = r"""
<div class="gsc-op-card">
  <h2>Dropbox shared link not working? Match the error to the cause</h2>
  <p>A Dropbox share link can stop opening because the file was moved or deleted, the shared link was disabled, access is limited to a team or account, or the owner does not currently have permission to create the type of link being attempted.</p>
  <div class="gsc-op-grid">
    <div class="gsc-op-mini"><h3>“You don’t have permission to create a link”</h3><p>The account, team policy, folder ownership, or sharing restrictions can prevent link creation even when the file itself is visible to you.</p></div>
    <div class="gsc-op-mini"><h3>Recipient cannot open the link</h3><p>The shared item may require a Dropbox account, team membership, or explicit access.</p></div>
    <div class="gsc-op-mini"><h3>Link was disabled</h3><p>An owner or administrator can revoke a previously working shared link.</p></div>
    <div class="gsc-op-mini"><h3>File moved or deleted</h3><p>Changing the underlying item or its ownership can make an old share URL unusable.</p></div>
    <div class="gsc-op-mini"><h3>Expiration or team policy</h3><p>Some plans and organization settings can impose expiration or sharing restrictions.</p></div>
    <div class="gsc-op-mini"><h3>Malformed URL</h3><p>A truncated or altered Dropbox URL can fail even when the original shared link is valid.</p></div>
  </div>
</div>
<div class="gsc-op-card">
  <h2>What to do when Dropbox says you cannot create a link</h2>
  <ol>
    <li>Confirm you have permission to share the file or folder, not only permission to view it.</li>
    <li>Check whether the item belongs to another person, shared folder, or managed team space.</li>
    <li>Review team sharing rules if the account is managed by an organization.</li>
    <li>Create a fresh shared link when allowed, then test that exact URL before sending it.</li>
  </ol>
  <div class="gsc-op-links">
    <a href="/dropbox-link-checker">Check a Dropbox link</a>
    <a href="/dropbox-permission-checker">Check Dropbox permissions</a>
    <a href="/check-dropbox-link-without-account">Test without a Dropbox account</a>
  </div>
</div>
"""

DOWNLOAD_LINK = r"""
<div class="gsc-op-card">
  <h2>Check a download link before opening the file</h2>
  <p>A download URL can look normal while redirecting to another domain, using a misleading filename, or pointing to an unexpected file type. The safest decision comes from checking the destination and context before opening the downloaded content.</p>
  <div class="gsc-op-grid">
    <div class="gsc-op-mini"><h3>Final destination</h3><p>See whether redirects lead somewhere different from the domain you expected.</p></div>
    <div class="gsc-op-mini"><h3>Domain mismatch</h3><p>A file claiming to come from one service should not silently resolve to an unrelated or suspicious host.</p></div>
    <div class="gsc-op-mini"><h3>Unexpected file type</h3><p>Executable, script, archive, or macro-enabled files deserve more scrutiny when you expected a document, image, or ordinary installer.</p></div>
    <div class="gsc-op-mini"><h3>Message context</h3><p>Unexpected invoices, delivery notices, job files, account alerts, and urgent attachments are common social-engineering patterns.</p></div>
  </div>
  <p class="gsc-op-note">A URL check reduces uncertainty but cannot guarantee that every downloaded file is harmless. Keep the operating system and security software current and avoid opening files you did not expect.</p>
  <div class="gsc-op-links">
    <a href="/malware-link-checker">Check malware-related link signals</a>
    <a href="/safe-link-checker">Run a general link safety check</a>
    <a href="/how-to-check-if-a-link-is-safe">Manual pre-click safety guide</a>
  </div>
</div>
"""

DRIVE_HUB_LINKS = r"""
<div class="gsc-op-card">
  <h2>Related Google Drive checks</h2>
  <p>If the link itself resolves but the recipient still cannot open the file, continue with the permission and troubleshooting checks.</p>
  <div class="gsc-op-links">
    <a href="/google-drive-link-not-working">Fix a Google Drive link that is not working</a>
    <a href="/google-drive-permission-checker">Check Google Drive permissions</a>
    <a href="/check-google-drive-link-without-signing-in">Test recipient access without signing in</a>
  </div>
</div>
"""


def main() -> None:
    patch(
        "/google-drive-link-not-working",
        DRIVE_NOT_WORKING,
        title="Google Drive Link Not Working? Fix Access & Opening Problems",
        description="Google Drive link not working or not opening? Diagnose permissions, wrong-account issues, Workspace restrictions, moved files, deleted files, and copied-link problems.",
        h1="Google Drive Link Not Working? Diagnose the Access Problem",
    )
    patch(
        "/dropbox-shared-link-not-working",
        DROPBOX_NOT_WORKING,
        title="Dropbox Shared Link Not Working? Fix Permission & Access Errors",
        description="Dropbox shared link not working? Diagnose permission errors, disabled links, team restrictions, deleted or moved files, expiration, and account-access problems.",
        h1="Dropbox Shared Link Not Working? Diagnose the Problem",
    )
    patch(
        "/download-link-checker",
        DOWNLOAD_LINK,
        title="Download Link Checker — Check a File URL Before Opening It",
        description="Check a download link before opening a file. Review redirects, destination domains, suspicious URL signals, and unexpected download context.",
        h1="Download Link Checker",
    )
    patch(
        "/google-drive-link-checker",
        DRIVE_HUB_LINKS,
        description="Check a Google Drive link before sharing it. Review recipient access, permission walls, sign-in requirements, broken-link causes, and destination signals.",
    )


if __name__ == "__main__":
    main()
