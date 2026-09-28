#!/usr/bin/env python3
"""Late, reversible GSC conversion pass for the 2026-09-28 report.

Targets only pages already earning useful impressions. It does not create or
rename routes. The pass exposes the existing link-checking backend above the
fold, removes duplicated troubleshooting overlays, and adds concise intent-
matched guidance. Build guards fail closed if expected page structure changes.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
START = "<!-- GSC_2026_09_28_CONVERSION_START -->"
END = "<!-- GSC_2026_09_28_CONVERSION_END -->"

DRIVE_ROUTE = "/google-drive-link-not-working"
DRIVE_CHECKER_ROUTE = "/google-drive-link-checker"
DOWNLOAD_ROUTE = "/download-link-checker"

DRIVE_TITLE = "Google Drive Link Not Working? 7 Fixes That Actually Work"
DRIVE_DESCRIPTION = (
    "Google Drive link not working? Fix You need access, wrong-account, "
    "sharing-permission, Workspace, moved-file and sign-in problems, then test the link."
)
DRIVE_H1 = DRIVE_TITLE

STYLE = r"""
<style id="gsc-2026-09-28-conversion-style">
.gsc-conversion-wrap{max-width:820px;margin:0 auto 22px}
.gsc-conversion-tool{padding:clamp(20px,4vw,30px);border:1px solid var(--line,#e4e7ec);border-radius:20px;background:var(--card,#fff);box-shadow:var(--shadow,0 12px 34px rgba(17,24,39,.06))}
.gsc-conversion-kicker{margin:0 0 7px;color:var(--muted,#69707d);font-size:12px;font-weight:850;letter-spacing:.09em;text-transform:uppercase}
.gsc-conversion-tool h2{margin:0 0 8px;font-size:clamp(24px,3.3vw,32px);line-height:1.15;letter-spacing:-.03em}
.gsc-conversion-tool>p{margin:0 0 16px;color:var(--muted,#69707d)}
.gsc-conversion-tool .cist-url-row{display:flex;gap:9px;align-items:stretch}
.gsc-conversion-tool .cist-url-input{width:100%;min-width:0;min-height:52px;padding:0 15px;border:1px solid var(--line,#e4e7ec);border-radius:13px;background:var(--card-soft,#f9fafb);color:inherit;font:inherit;outline:none}
.gsc-conversion-tool .cist-url-input:focus{border-color:currentColor;box-shadow:0 0 0 3px rgba(127,127,127,.12)}
.gsc-conversion-tool .cist-actions{margin-top:9px;display:flex;gap:9px}
.gsc-conversion-tool .cist-action{min-height:48px;padding:0 17px;border:1px solid var(--line,#e4e7ec);border-radius:12px;background:var(--accent,#111827);color:var(--accent-text,#fff);font:inherit;font-weight:800;cursor:pointer}
.gsc-conversion-tool .cist-action span{filter:none!important}
.gsc-conversion-note{margin:10px 0 0!important;font-size:12px;line-height:1.45;color:var(--muted,#69707d)!important}
.gsc-conversion-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.gsc-conversion-links a{display:inline-flex;padding:8px 10px;border:1px solid var(--line,#e4e7ec);border-radius:999px;text-decoration:none;font-size:12px;font-weight:750}
.gsc-conversion-links a:hover{text-decoration:underline}
#gsc-quick-diagnosis{max-width:820px;margin:0 auto 22px;padding:clamp(20px,4vw,30px);border:1px solid var(--line,#e4e7ec);border-radius:20px;background:var(--card,#fff)}
#gsc-quick-diagnosis h2{margin:0 0 8px;font-size:clamp(23px,3vw,30px);line-height:1.18;letter-spacing:-.025em}
#gsc-quick-diagnosis>p{margin:0 0 16px;color:var(--muted,#69707d)}
.gsc-diagnosis-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.gsc-diagnosis-table{width:100%;border-collapse:collapse;min-width:660px;font-size:14px}
.gsc-diagnosis-table th,.gsc-diagnosis-table td{padding:12px 13px;border-top:1px solid var(--line,#e4e7ec);vertical-align:top;text-align:left}
.gsc-diagnosis-table th{color:var(--muted,#69707d);font-size:11px;letter-spacing:.07em;text-transform:uppercase}
.gsc-diagnosis-table td:first-child{font-weight:800}
.gsc-diagnosis-table code{white-space:nowrap}
.gsc-sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@media(max-width:680px){
  .gsc-conversion-wrap,#gsc-quick-diagnosis{margin-bottom:14px}
  .gsc-conversion-tool,#gsc-quick-diagnosis{border-radius:17px}
  .gsc-conversion-tool .cist-url-row{display:block}
  .gsc-conversion-tool .cist-url-input{font-size:16px}
  .gsc-conversion-tool .cist-actions{display:block}
  .gsc-conversion-tool .cist-action{width:100%}
}
</style>
"""

DIAGNOSIS = r"""
<section id="gsc-quick-diagnosis" aria-labelledby="gsc-diagnosis-title">
  <h2 id="gsc-diagnosis-title">Match the error to the likely cause</h2>
  <p>Start with the exact symptom the recipient sees, then change only the setting that matches it.</p>
  <div class="gsc-diagnosis-scroll">
    <table class="gsc-diagnosis-table">
      <thead><tr><th>What you see</th><th>Likely cause</th><th>What to do</th></tr></thead>
      <tbody>
        <tr><td>“You need access”</td><td>Sharing permissions</td><td>Check General access or add the recipient’s correct Google account.</td></tr>
        <tr><td>Sign-in required</td><td>Wrong account or Workspace policy</td><td>Retry with the authorized account, then check organization sharing rules.</td></tr>
        <tr><td>Works for me only</td><td>Owner browser session</td><td>Test the same URL in a private window or signed-out session.</td></tr>
        <tr><td>File does not exist</td><td>Moved, deleted or ownership changed</td><td>Open the original item in Drive and create or copy the current share URL.</td></tr>
        <tr><td>Anyone with the link still fails</td><td>Workspace restriction or wrong item</td><td>Confirm the exact file or folder and whether external sharing is allowed.</td></tr>
      </tbody>
    </table>
  </div>
</section>
"""

def route_file(route: str) -> Path:
    rel = route.strip("/")
    for candidate in (DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel):
        if candidate.is_file():
            return candidate
    raise RuntimeError(f"Missing route: {route}")


def set_title(doc: str, value: str) -> str:
    escaped = html.escape(value)
    doc, count = re.subn(r"<title>.*?</title>", f"<title>{escaped}</title>", doc, count=1, flags=re.I | re.S)
    if count != 1:
        raise RuntimeError("Could not update title")
    doc = re.sub(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])',
        lambda m: m.group(1) + html.escape(value, quote=True) + m.group(2),
        doc,
        count=1,
        flags=re.I,
    )
    return doc


def set_meta(doc: str, name: str, value: str, *, prop: bool = False) -> str:
    attr = "property" if prop else "name"
    escaped = html.escape(value, quote=True)
    pattern = rf'(<meta\s+{attr}=["\']{re.escape(name)}["\']\s+content=["\'])[^"\']*(["\'])'
    if re.search(pattern, doc, re.I):
        return re.sub(pattern, lambda m: m.group(1) + escaped + m.group(2), doc, count=1, flags=re.I)
    if "</head>" not in doc:
        raise RuntimeError(f"Missing </head> while adding {name}")
    return doc.replace("</head>", f'<meta {attr}="{html.escape(name, quote=True)}" content="{escaped}">\n</head>', 1)


def set_h1(doc: str, value: str) -> str:
    escaped = html.escape(value)
    doc, count = re.subn(r"(<h1\b[^>]*>).*?(</h1>)", rf"\1{escaped}\2", doc, count=1, flags=re.I | re.S)
    if count != 1:
        raise RuntimeError("Could not update H1")
    return doc


def strip_block(doc: str, start: str, end: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end), "", doc, flags=re.S)


def ensure_style(doc: str) -> str:
    doc = re.sub(r'\s*<style id="gsc-2026-09-28-conversion-style">.*?</style>', "", doc, flags=re.S)
    if "</head>" not in doc:
        raise RuntimeError("Missing </head>")
    return doc.replace("</head>", STYLE + "\n</head>", 1)


def checker_block(kind: str) -> str:
    if kind == "drive":
        title = "Check your Google Drive link"
        lead = "Paste the exact Drive URL the recipient is opening. The checker inspects the destination, redirects and visible access or sign-in barriers."
        placeholder = "https://drive.google.com/..."
        button = "Check Drive link"
        links = (
            '<a href="/google-drive-permission-checker">Check permissions</a>'
            '<a href="/check-google-drive-link-without-signing-in">Test without signing in</a>'
            '<a href="/is-my-google-drive-link-public">Is the link public?</a>'
        )
    else:
        title = "Check the download link before opening it"
        lead = "Paste the file URL to inspect where it goes, whether it redirects and whether the destination looks different from what you expected."
        placeholder = "https://example.com/file.zip"
        button = "Check download link"
        links = (
            '<a href="/malware-link-checker">Malware link checker</a>'
            '<a href="/safe-link-checker">Safe link checker</a>'
            '<a href="/how-to-check-if-a-link-is-safe">Manual safety guide</a>'
        )

    return f"""
{START}
<section class="gsc-conversion-wrap" aria-label="Link checker">
  <div class="gsc-conversion-tool">
    <p class="gsc-conversion-kicker">Check first</p>
    <h2>{html.escape(title)}</h2>
    <p>{html.escape(lead)}</p>
    <form id="cist-safety-form">
      <label class="gsc-sr-only" for="cist-safety-url">URL to check</label>
      <div class="cist-url-row">
        <input class="cist-url-input" id="cist-safety-url" name="url" type="url" inputmode="url" autocomplete="off" spellcheck="false" placeholder="{html.escape(placeholder, quote=True)}" required>
      </div>
      <div class="cist-actions">
        <button class="cist-action cist-action-primary" type="submit"><span>{html.escape(button)}</span></button>
      </div>
    </form>
    <p class="gsc-conversion-note">No account required. A link check cannot override Google Drive permissions or prove that every downloaded file is harmless.</p>
    <div class="gsc-conversion-links">{links}</div>
    <div id="cist-console-result" aria-live="polite"></div>
  </div>
</section>
{END}
"""


def insert_checker(doc: str, kind: str) -> str:
    doc = strip_block(doc, START, END)
    block = checker_block(kind)
    marker = '<article class="article">'
    if marker not in doc:
        raise RuntimeError("Priority article marker changed")
    return doc.replace(marker, block + "\n" + marker, 1)


def patch_drive_problem() -> None:
    path = route_file(DRIVE_ROUTE)
    doc = path.read_text(encoding="utf-8")
    if 'id="cist-safety-v6-script"' not in doc:
        raise RuntimeError("Existing safety checker runtime missing from Drive troubleshooting page")
    doc = set_title(doc, DRIVE_TITLE)
    doc = set_meta(doc, "description", DRIVE_DESCRIPTION)
    doc = set_meta(doc, "og:description", DRIVE_DESCRIPTION, prop=True)
    doc = set_h1(doc, DRIVE_H1)
    doc = strip_block(doc, "<!-- GSC_2026_09_14_START -->", "<!-- GSC_2026_09_14_END -->")
    doc = strip_block(doc, "<!-- GSC_2026_09_24_START -->", "<!-- GSC_2026_09_24_END -->")
    doc = ensure_style(doc)
    doc = insert_checker(doc, "drive")
    doc = doc.replace('<article class="article">', DIAGNOSIS + '\n<article class="article">', 1)
    path.write_text(doc, encoding="utf-8")


def patch_checker_page(route: str, kind: str) -> None:
    path = route_file(route)
    doc = path.read_text(encoding="utf-8")
    if 'id="cist-safety-v6-script"' not in doc:
        raise RuntimeError(f"Existing safety checker runtime missing from {route}")
    doc = ensure_style(doc)
    doc = insert_checker(doc, kind)
    path.write_text(doc, encoding="utf-8")


def guard() -> None:
    drive = route_file(DRIVE_ROUTE).read_text(encoding="utf-8")
    if drive.count('id="cist-safety-form"') != 1:
        raise RuntimeError("Drive page must contain exactly one embedded checker form")
    if drive.count('id="gsc-quick-diagnosis"') != 1:
        raise RuntimeError("Drive diagnosis table missing or duplicated")
    if "GSC_2026_09_14_START" in drive or "GSC_2026_09_24_START" in drive:
        raise RuntimeError("Duplicate historical GSC blocks survived on Drive troubleshooting page")
    if html.unescape(re.search(r"<title>(.*?)</title>", drive, re.I | re.S).group(1)) != DRIVE_TITLE:
        raise RuntimeError("Drive title guard failed")
    if len(re.findall(r"<h1\b", drive, re.I)) != 1:
        raise RuntimeError("Drive page H1 count changed")
    for href in (
        "/google-drive-link-checker",
        "/google-drive-permission-checker",
        "/check-google-drive-link-without-signing-in",
        "/is-my-google-drive-link-public",
    ):
        if f'href="{href}"' not in drive:
            raise RuntimeError(f"Drive page lost required internal link: {href}")

    for route in (DRIVE_CHECKER_ROUTE, DOWNLOAD_ROUTE):
        doc = route_file(route).read_text(encoding="utf-8")
        if doc.count('id="cist-safety-form"') != 1:
            raise RuntimeError(f"{route} must contain exactly one embedded checker form")
        if doc.count('id="cist-console-result"') != 1:
            raise RuntimeError(f"{route} checker result target missing or duplicated")
        if len(re.findall(r"<h1\b", doc, re.I)) != 1:
            raise RuntimeError(f"{route} H1 count changed")


def main() -> None:
    patch_drive_problem()
    patch_checker_page(DRIVE_CHECKER_ROUTE, "drive")
    patch_checker_page(DOWNLOAD_ROUTE, "download")
    guard()
    print("Applied safe GSC 2026-09-28 conversion pass")


if __name__ == "__main__":
    main()
