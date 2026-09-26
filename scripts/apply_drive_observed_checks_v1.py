#!/usr/bin/env python3
"""Add product-specific observed-check data to existing Google Drive pages.

Claims in this block mirror api/check.js behavior. The copy deliberately
separates observable recipient-facing signals from private Google Drive ACLs.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
START = "<!-- DRIVE_OBSERVED_CHECKS_V1_START -->"
END = "<!-- DRIVE_OBSERVED_CHECKS_V1_END -->"

PAGES = {
    "/google-drive-link-checker": (
        "Use this page when you have the final Drive share URL and want a broad recipient-style check before sending it.",
        "A public request can reveal the response status, redirect chain, final Google host, page metadata, content type and an observable sign-in or access wall.",
    ),
    "/google-drive-permission-checker": (
        "Use this page when the URL looks correct but you suspect the recipient is being blocked by permissions, account requirements or organization policy.",
        "The scanner can flag 401/403 responses and visible phrases such as “sign in”, “request access”, “you need permission” or “access denied”; it cannot read the file's private ACL.",
    ),
    "/check-google-drive-link-without-signing-in": (
        "Use this page when the specific question is whether the recipient experience works from a signed-out or anonymous context.",
        "The scanner makes a public request rather than using your Google session, follows redirects and reports whether the response exposes an observable login/access barrier.",
    ),
    "/is-my-google-drive-link-public": (
        "Use this page when you need to distinguish a link that is recipient-accessible from one that is Restricted to explicitly approved accounts.",
        "The authoritative setting remains Google Drive’s General access value. The scanner can observe the public response but cannot inspect Google’s private sharing list.",
    ),
    "/google-drive-link-not-working": (
        "Use this page after a recipient reports that the link fails, asks for access, redirects unexpectedly or requires a different Google account.",
        "The checker follows up to five redirects and inspects the first part of the returned page for recipient-facing access signals, while also reporting the final destination and HTTP response.",
    ),
    "/google-drive-folder-sharing-checker": (
        "Use this page for a shared Drive folder, where the folder itself and items inside it can have different effective access behavior.",
        "The scanner can observe the folder URL’s public response and access-wall signals, but it cannot enumerate private folder members or infer every child item's permission.",
    ),
}

STYLE = """
<style id="drive-observed-checks-v1-style">
.drive-observed-v1{max-width:900px;margin:22px auto 0;padding:clamp(18px,3vw,24px);border:1px solid var(--line,#dfe3ea);border-radius:18px;background:var(--card,#fff)}
.drive-observed-v1 h2{margin:0 0 8px;font-size:clamp(20px,3vw,26px);line-height:1.2;letter-spacing:-.02em}
.drive-observed-v1>p{margin:0 0 12px;max-width:76ch}
.drive-observed-v1 dl{margin:0;display:grid;gap:0}
.drive-observed-v1 .drive-row{display:grid;grid-template-columns:minmax(130px,.34fr) minmax(0,1fr);gap:14px;padding:10px 0;border-top:1px solid var(--line,#dfe3ea)}
.drive-observed-v1 dt{font-weight:800}.drive-observed-v1 dd{margin:0;color:var(--muted,#69707d)}
.drive-observed-v1 .drive-limit{margin-top:10px;padding-top:10px;border-top:1px solid var(--line,#dfe3ea);font-size:13px;color:var(--muted,#69707d)}
@media(max-width:620px){.drive-observed-v1 .drive-row{grid-template-columns:1fr;gap:3px}}
</style>
"""

ROWS = [
    ("Redirects", "Follows up to 5 HTTP redirects and records the final URL."),
    ("Access-wall signals", "Checks 401/403 responses plus visible sign-in, login, request-access, permission and access-denied cues."),
    ("Returned page", "Reads up to the first 64 KB of HTML for title, description and observable access signals."),
    ("Destination evidence", "Reports final host, HTTP status, content type and other URL-level safety signals when available."),
]

def route_file(route: str) -> Path:
    rel = route.strip("/")
    for p in (DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel):
        if p.is_file():
            return p
    raise RuntimeError(f"Missing Drive route: {route}")

def block(route: str) -> str:
    use_case, observed = PAGES[route]
    rows = "".join(
        f'<div class="drive-row"><dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd></div>'
        for label, value in ROWS
    )
    return (
        f"\n{START}\n"
        '<section class="drive-observed-v1" aria-label="Observed Google Drive access checks">'
        '<h2>What the checker can actually observe</h2>'
        f'<p><strong>Best use:</strong> {html.escape(use_case)}</p>'
        f'<p>{html.escape(observed)}</p>'
        f'<dl>{rows}</dl>'
        '<p class="drive-limit"><strong>Limit:</strong> Can I Share This? does not authenticate as your recipient, read private Google Drive ACLs, or guarantee that every recipient account has access. Google Drive’s own General access and account-level sharing rules remain authoritative.</p>'
        '</section>'
        f"\n{END}\n"
    )

def main() -> None:
    for route in PAGES:
        p = route_file(route)
        doc = p.read_text(encoding="utf-8")
        doc = re.sub(re.escape(START) + r".*?" + re.escape(END), "", doc, flags=re.S)
        if 'id="drive-observed-checks-v1-style"' not in doc:
            doc = doc.replace("</head>", STYLE + "\n</head>", 1)
        b = block(route)
        if "<!-- SEO_PRIORITY_NETWORK_START -->" in doc:
            doc = doc.replace("<!-- SEO_PRIORITY_NETWORK_START -->", b + "\n<!-- SEO_PRIORITY_NETWORK_START -->", 1)
        elif "</main>" in doc:
            doc = doc.replace("</main>", b + "</main>", 1)
        else:
            raise RuntimeError(f"Cannot place Drive observed-check block: {route}")
        if "What the checker can actually observe" not in doc or "Follows up to 5 HTTP redirects" not in doc:
            raise RuntimeError(f"Drive observed-check guard failed: {route}")
        p.write_text(doc, encoding="utf-8")
    print(f"Added observed scanner evidence to {len(PAGES)} existing Google Drive pages")

if __name__ == "__main__":
    main()
