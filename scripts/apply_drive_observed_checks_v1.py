#!/usr/bin/env python3
"""Add product-specific observed-check data to existing Google Drive pages.

Claims mirror api/check.js behavior. Each page gets a distinct evidence block
so the hub, permissions, signed-out and troubleshooting intents stay separate.
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
    "/google-drive-link-checker": {
        "use": "Use this page when you have the final Drive share URL and want a broad recipient-style check before sending it.",
        "observed": "This is the cluster hub. It summarizes the public response rather than diagnosing one specific Google Drive setting.",
        "rows": [
            ("Redirect path", "Follows up to 5 HTTP redirects and records the final URL and host."),
            ("HTTP response", "Reports the returned status and whether a public request was reachable."),
            ("Access wall", "Checks for 401/403 plus visible sign-in, request-access, permission and access-denied cues."),
            ("Returned content", "Reads up to the first 64 KB of HTML for page title, description and observable access signals."),
        ],
    },
    "/google-drive-permission-checker": {
        "use": "Use this page when the URL itself looks correct but a recipient appears blocked by permissions, account requirements or organization policy.",
        "observed": "This page is about access-control symptoms, not general URL validity.",
        "rows": [
            ("Permission symptoms", "Flags 401/403 responses and visible “request access”, “you need permission” or “access denied” wording."),
            ("Private ACL limit", "The scanner cannot read Google Drive's private sharing list, group membership or Workspace policy configuration."),
        ],
    },
    "/check-google-drive-link-without-signing-in": {
        "use": "Use this page when the exact question is whether the link exposes a usable signed-out or anonymous recipient experience.",
        "observed": "The check is made as a public web request rather than through your own Google session.",
        "rows": [
            ("Signed-out signal", "Reports observable login/sign-in barriers in the public response and redirect path."),
            ("Session limit", "A public request cannot reproduce every recipient's cookies, Google account state or organization membership."),
        ],
    },
    "/is-my-google-drive-link-public": {
        "use": "Use this page to distinguish a recipient-accessible link from one restricted to explicitly approved Google accounts.",
        "observed": "Google Drive's General access setting is authoritative; this page explains how the scanner's public observation relates to that setting.",
        "rows": [
            ("Public response", "A response without an observable access wall is supporting evidence, not proof of the underlying sharing configuration."),
            ("Authoritative setting", "Confirm General access in Google Drive: “Anyone with the link” and “Restricted” represent different sharing states."),
        ],
    },
    "/google-drive-link-not-working": {
        "use": "Use this page after someone reports that the link fails, asks for access, redirects unexpectedly or requires another Google account.",
        "observed": "This page is for troubleshooting the failure path rather than simply deciding whether a link is public.",
        "rows": [
            ("Failure path", "The checker records redirects, the final destination and the returned HTTP status to show where the request ended."),
            ("Visible blockers", "It can surface sign-in, request-access and permission wording when those cues appear in the returned page."),
        ],
    },
    "/google-drive-folder-sharing-checker": {
        "use": "Use this page for a shared Drive folder, where folder access and access to individual child items can differ.",
        "observed": "This page focuses on the folder URL's recipient-facing response, not file-level permission inheritance.",
        "rows": [
            ("Folder response", "Checks the folder URL's public response, redirects and observable login/access barriers."),
            ("Child-item limit", "The scanner cannot enumerate private folder members or infer every file's effective permission from the folder URL alone."),
        ],
    },
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

def route_file(route: str) -> Path:
    rel = route.strip("/")
    for p in (DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel):
        if p.is_file():
            return p
    raise RuntimeError(f"Missing Drive route: {route}")

def block(route: str) -> str:
    cfg = PAGES[route]
    rows = "".join(
        f'<div class="drive-row"><dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd></div>'
        for label, value in cfg["rows"]
    )
    return (
        f"\n{START}\n"
        '<section class="drive-observed-v1" aria-label="Observed Google Drive access checks">'
        '<h2>What the checker can actually observe for this question</h2>'
        f'<p><strong>Best use:</strong> {html.escape(cfg["use"])}</p>'
        f'<p>{html.escape(cfg["observed"])}</p>'
        f'<dl>{rows}</dl>'
        '<p class="drive-limit"><strong>Limit:</strong> Can I Share This? does not authenticate as your recipient or read private Google Drive ACLs. Google Drive’s own sharing controls remain authoritative.</p>'
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
        if "What the checker can actually observe for this question" not in doc:
            raise RuntimeError(f"Drive observed-check guard failed: {route}")
        p.write_text(doc, encoding="utf-8")
    print(f"Added intent-specific observed scanner evidence to {len(PAGES)} existing Google Drive pages")

if __name__ == "__main__":
    main()
