#!/usr/bin/env python3
"""Apply GSC-driven SEO consolidation and authority improvements.

Runs late in the build so it patches the final static HTML emitted by the
existing generators without creating new indexable routes.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
START = "<!-- GSC_PRIORITY_SEO_START -->"
END = "<!-- GSC_PRIORITY_SEO_END -->"

REDIRECTED_ROUTES = {
    "/check-google-drive-link",
    "/google-drive-share-link-test",
    "/how-to-check-a-link-without-clicking-it",
}

STYLE = r"""
<style id="gsc-priority-seo-style">
.gsc-seo{max-width:900px;margin:28px auto 0;padding:0 2px}
.gsc-seo .gsc-card{margin:16px 0;padding:clamp(20px,3vw,30px);border:1px solid var(--line,#e4e7ec);border-radius:20px;background:var(--card,#fff)}
.gsc-seo h2{margin:0 0 12px;font-size:clamp(22px,3vw,30px);line-height:1.18;letter-spacing:-.025em}
.gsc-seo h3{margin:22px 0 8px;font-size:18px;line-height:1.3}
.gsc-seo p{margin:0 0 14px}
.gsc-seo ul,.gsc-seo ol{margin:12px 0 0;padding-left:22px}
.gsc-seo li{margin:8px 0}
.gsc-seo code{overflow-wrap:anywhere}
.gsc-seo .gsc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
.gsc-seo .gsc-mini{padding:15px;border:1px solid var(--line,#e4e7ec);border-radius:14px;background:var(--card-soft,#f9fafb)}
.gsc-seo .gsc-mini h3{margin:0 0 6px;font-size:16px}
.gsc-seo .gsc-example{margin:12px 0;padding:14px;border:1px solid var(--line,#e4e7ec);border-radius:14px;background:var(--card-soft,#f9fafb);overflow-wrap:anywhere}
.gsc-seo .gsc-source{font-size:14px;color:var(--muted,#69707d)}
.gsc-seo .gsc-source a{text-underline-offset:3px}
.gsc-seo .gsc-note{padding:14px 16px;border-left:3px solid currentColor;background:var(--card-soft,#f9fafb);border-radius:10px}
@media(max-width:680px){.gsc-seo .gsc-grid{grid-template-columns:1fr}}
</style>
"""


def route_file(route: str) -> Path | None:
    rel = route.strip("/")
    candidates = [DIST / rel, DIST / f"{rel}.html", DIST / rel / "index.html"]
    if route == "/": candidates = [DIST / "index.html"]
    for path in candidates:
        if path.is_file(): return path
    return None


def set_title(doc: str, title: str) -> str:
    escaped = html.escape(title)
    doc = re.sub(r"<title>.*?</title>", f"<title>{escaped}</title>", doc, count=1, flags=re.I | re.S)
    doc = re.sub(r'(<meta\s+property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])', lambda m: m.group(1) + html.escape(title, quote=True) + m.group(2), doc, count=1, flags=re.I)
    return doc


def set_description(doc: str, description: str) -> str:
    value = html.escape(description, quote=True)
    doc = re.sub(r'(<meta\s+name=["\']description["\']\s+content=["\'])[^"\']*(["\'])', lambda m: m.group(1) + value + m.group(2), doc, count=1, flags=re.I)
    doc = re.sub(r'(<meta\s+property=["\']og:description["\']\s+content=["\'])[^"\']*(["\'])', lambda m: m.group(1) + value + m.group(2), doc, count=1, flags=re.I)
    return doc


def set_first_h1(doc: str, h1: str) -> str:
    escaped = html.escape(h1)
    return re.sub(r"(<h1\b[^>]*>).*?(</h1>)", rf"\1{escaped}\2", doc, count=1, flags=re.I | re.S)


def ensure_style(doc: str) -> str:
    if 'id="gsc-priority-seo-style"' in doc: return doc
    if "</head>" in doc: return doc.replace("</head>", STYLE + "\n</head>", 1)
    return STYLE + doc


def inject(doc: str, content: str) -> str:
    doc = re.sub(re.escape(START) + r".*?" + re.escape(END), "", doc, flags=re.S)
    block = f"\n{START}\n<section class=\"gsc-seo\" aria-label=\"Detailed guidance\">\n{content}\n</section>\n{END}\n"
    if "</main>" in doc:
        head, tail = doc.rsplit("</main>", 1)
        return head + block + "</main>" + tail
    if "</body>" in doc: return doc.replace("</body>", block + "</body>", 1)
    return doc + block


def patch(route: str, content: str, *, title: str | None = None, description: str | None = None, h1: str | None = None) -> None:
    path = route_file(route)
    if not path: raise RuntimeError(f"Missing generated route: {route}")
    doc = path.read_text(encoding="utf-8")
    doc = ensure_style(doc)
    if title: doc = set_title(doc, title)
    if description: doc = set_description(doc, description)
    if h1: doc = set_first_h1(doc, h1)
    doc = inject(doc, content)
    path.write_text(doc, encoding="utf-8")
    print(f"GSC SEO patched {route}")


def remove_redirects_from_sitemap() -> None:
    path = DIST / "sitemap.xml"
    if not path.exists(): return
    text = path.read_text(encoding="utf-8")
    for route in REDIRECTED_ROUTES:
        absolute = f"https://canisharethis.com{route}"
        text = re.sub(rf"<url>\s*<loc>{re.escape(absolute)}</loc>.*?</url>\s*", "", text, flags=re.I | re.S)
    path.write_text(text, encoding="utf-8")
    print("Removed redirected duplicate URLs from sitemap")


GOOGLE_DRIVE = r"""
<div class="gsc-card">
  <h2>Common Google Drive link problems</h2>
  <p>A Google Drive URL can be valid and still fail for the recipient. The most common cause is access configuration, not a broken URL.</p>
  <div class="gsc-grid">
    <div class="gsc-mini"><h3>“You need access”</h3><p>The file is restricted to specific accounts or groups. The recipient must request access or the owner must change sharing.</p></div>
    <div class="gsc-mini"><h3>Sign-in required</h3><p>Work, school, or organization policies can require the correct Google account even when the URL itself is valid.</p></div>
    <div class="gsc-mini"><h3>File moved or deleted</h3><p>A previously shared URL can stop working after the item is deleted, moved to a restricted location, or ownership changes.</p></div>
    <div class="gsc-mini"><h3>Restricted organization</h3><p>Workspace administrators can limit external sharing, so a link may work internally but fail for outside recipients.</p></div>
    <div class="gsc-mini"><h3>Wrong sharing level</h3><p>“Restricted” and “Anyone with the link” produce very different recipient experiences.</p></div>
    <div class="gsc-mini"><h3>Malformed or copied URL</h3><p>Truncated links, extra punctuation, or a copied tracking wrapper can prevent the intended destination from opening correctly.</p></div>
  </div>
</div>
<div class="gsc-card">
  <h2>What to check before you send a Drive link</h2>
  <ol>
    <li>Paste the Google Drive URL into the checker above.</li>
    <li>Confirm the detected destination is actually a Google Drive domain.</li>
    <li>Review access and sign-in signals.</li>
    <li>If the recipient should not need an account, verify the file is set to <strong>Anyone with the link</strong>.</li>
    <li>Open the link in a private/incognito window as a final recipient-style test when appropriate.</li>
  </ol>
  <p class="gsc-note">A safety or access check cannot override the owner’s Google Drive permissions. Only the file owner or an authorized Workspace administrator can change access.</p>
  <p class="gsc-source">Official reference: <a href="https://support.google.com/drive/answer/2494822?hl=en" rel="noopener noreferrer">Google Drive Help — Share files from Google Drive</a>.</p>
</div>
"""

REMOVE_TRACKING = r"""
<div class="gsc-card">
  <h2>Remove tracking parameters without breaking the destination</h2>
  <p>The cleaner removes common marketing and click-attribution parameters while preserving the base URL and parameters that may be required for the page to work.</p>
  <div class="gsc-example"><strong>Before</strong><br><code>https://example.com/article?utm_source=x&amp;utm_medium=social&amp;fbclid=abc123</code></div>
  <div class="gsc-example"><strong>After</strong><br><code>https://example.com/article</code></div>
  <h3>Common tracking parameters</h3>
  <ul>
    <li><code>utm_source</code>, <code>utm_medium</code>, <code>utm_campaign</code>, <code>utm_term</code>, <code>utm_content</code></li>
    <li><code>fbclid</code> and similar social click identifiers</li>
    <li><code>gclid</code> and advertising attribution identifiers</li>
    <li>Known analytics parameters that do not normally identify the destination resource</li>
  </ul>
</div>
<div class="gsc-card">
  <h2>Tracking parameter vs required parameter</h2>
  <p>Not every query parameter is tracking. Some URLs use parameters for search queries, file IDs, language, authentication state, pagination, or product variants. The tool therefore favors conservative removal instead of deleting every value after a question mark.</p>
  <p class="gsc-note">Always verify the cleaned URL still opens the intended public page before sharing it. Sensitive tokens or private access keys should not be shared, even after unrelated tracking parameters are removed.</p>
</div>
"""

EMAIL = r"""
<div class="gsc-card">
  <h2>What the email safety checker actually checks</h2>
  <div class="gsc-grid">
    <div class="gsc-mini"><h3>Address format</h3><p>Checks whether the submitted address has a supported, plausible email structure.</p></div>
    <div class="gsc-mini"><h3>Domain existence</h3><p>Looks for DNS evidence that the domain exists and can receive or publish email-related records.</p></div>
    <div class="gsc-mini"><h3>MX records</h3><p>Checks whether the domain publishes mail-exchanger records when DNS data is available.</p></div>
    <div class="gsc-mini"><h3>SPF and DMARC</h3><p>Inspects published sender-authentication policy signals. Missing or weak policy is context, not proof of fraud.</p></div>
    <div class="gsc-mini"><h3>Lookalike domains</h3><p>Flags domains that visually resemble selected well-known brands but are not recognized official domains.</p></div>
    <div class="gsc-mini"><h3>Disposable domains</h3><p>Identifies a maintained set of known temporary-email providers as a contextual warning signal.</p></div>
    <div class="gsc-mini"><h3>Domain age context</h3><p>Uses public RDAP registration data when available. A new domain can deserve more scrutiny but is not automatically malicious.</p></div>
    <div class="gsc-mini"><h3>Internationalized domains</h3><p>Highlights punycode or internationalized-domain encodings that can sometimes make visual impersonation harder to notice.</p></div>
  </div>
</div>
<div class="gsc-card">
  <h2>What this checker cannot prove</h2>
  <p>It cannot prove who controls a mailbox, guarantee that a sender is legitimate, or authenticate the exact message from an address alone. Display-name spoofing and message-level social engineering require the full message context.</p>
  <p>For a suspicious email, verify the company through a website or app you already trust rather than using the contact details or links inside the message.</p>
  <p class="gsc-source">Phishing reference: <a href="https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams" rel="noopener noreferrer">U.S. Federal Trade Commission — How to recognize and avoid phishing scams</a>.</p>
</div>
"""

HOW_SCANNING = r"""
<div class="gsc-card"><h2>What happens when CanIShareThis scans a link</h2><ol><li><strong>Normalize the input.</strong> The scanner parses the submitted URL and identifies the hostname, protocol, path, query parameters, and recognizable platform patterns.</li><li><strong>Inspect the URL structure.</strong> It looks for suspicious formatting, deceptive hostname patterns, unusual encodings, risky parameters, and other structural warning signals.</li><li><strong>Follow destination signals.</strong> When a network check is available, the scanner evaluates redirects and exposes the final destination so a shortened or wrapped link is easier to understand.</li><li><strong>Evaluate domain context.</strong> Domain and reputation signals are combined with the URL structure rather than treated as a single yes/no blacklist result.</li><li><strong>Inspect content context when supported.</strong> Download links, cloud-sharing links, social profiles, and other recognizable inputs can receive additional checks relevant to that type.</li><li><strong>Return a risk-oriented result.</strong> The result summarizes the strongest signals and a recommended action instead of claiming that a link is guaranteed safe.</li></ol></div>
<div class="gsc-card"><h2>Signals are combined, not treated as proof</h2><p>No single signal is sufficient on its own. HTTPS does not prove legitimacy. A new domain is not automatically malicious. A clean reputation lookup does not guarantee that a page is harmless. Redirects are not inherently dangerous. The scanner combines available evidence and keeps uncertainty visible.</p></div>
"""

SCAM_SIGNS = r"""<div class="gsc-card"><h2>Common scam warning signs</h2><p>Urgency, unexpected requests for money or credentials, identity claims that do not match the sender or destination, unusual payment methods, secrecy, and attempts to move conversations off-platform are recurring scam signals.</p></div>"""
CLICKED_PHISHING = r"""<div class="gsc-card"><h2>Prioritize what was exposed</h2><p>If you entered a password, payment detail, downloaded a file, or shared identity information after clicking a phishing link, act on that exposed item first and use official account or provider channels.</p></div>"""
SAFE_LINK = r"""<div class="gsc-card"><h2>Use this page when you already have a link to inspect</h2><p>This is the transactional checker: paste the URL and review the destination, structural warning signs, redirects, reputation context, and other available signals. It is intentionally different from the manual safety guide.</p></div>"""
MANUAL_GUIDE = r"""<div class="gsc-card"><h2>Manual pre-click link safety workflow</h2><ol><li>Read the actual hostname from right to left and identify the registrable domain.</li><li>Check for misspellings, extra brand words, misleading subdomains, punycode, or unusual URL encoding.</li><li>Do not treat HTTPS or a padlock as proof that the site is legitimate.</li><li>Expand or inspect shortened links before opening them when the destination is unclear.</li><li>Consider the context: unexpected urgency, login requests, payments, downloads, and identity claims increase the need for independent verification.</li><li>When possible, navigate to the organization through a known official app, bookmark, or manually typed domain instead of the supplied link.</li></ol></div>"""


def main() -> None:
    patch(
        "/google-drive-link-checker",
        GOOGLE_DRIVE,
        description="Check a Google Drive link before you share it. See whether a recipient is likely to open it, hit a permission wall, or need to sign in.",
    )
    patch("/remove-tracking-from-url", REMOVE_TRACKING, title="Remove Tracking From URL — Clean UTM & Click Parameters", description="Remove common tracking parameters such as UTM tags, fbclid and ad click IDs while preserving URL parameters that may be required for the destination.", h1="Remove Tracking From a URL")
    patch("/email-safety-checker", EMAIL, title="Email Safety Checker — Check Sender & Domain Warning Signs", description="Check an email address for domain, MX, SPF, DMARC, lookalike, disposable-domain and registration-age warning signals. No identity guarantee.", h1="Email Safety Checker")
    patch("/how-link-scanning-works", HOW_SCANNING, title="How Link Scanning Works — What CanIShareThis Checks", description="See how CanIShareThis evaluates URL structure, redirects, domain context, reputation, lookalikes, privacy signals and supported link types—and where scanning has limits.", h1="How CanIShareThis Scans a Link")
    patch("/scam-warning-signs", SCAM_SIGNS, description="Learn the scam warning signs that repeat across email, text, social media, marketplaces, crypto, payments and impersonation attempts, with official safety references.")
    patch("/what-to-do-after-clicking-a-phishing-link", CLICKED_PHISHING, description="Clicked a phishing link? Follow prioritized steps for exposed passwords, account sessions, downloads, payment details and identity information.")
    patch("/safe-link-checker", SAFE_LINK, description="Paste a URL into the Safe Link Checker to inspect destination, redirects, structural warning signs, reputation context and other available safety signals.")
    patch("/how-to-check-if-a-link-is-safe", MANUAL_GUIDE, description="Use a manual pre-click workflow to inspect a URL, identify the real domain, recognize deceptive formatting and verify suspicious context independently.")
    remove_redirects_from_sitemap()


if __name__ == "__main__":
    main()
