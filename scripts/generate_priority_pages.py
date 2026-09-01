#!/usr/bin/env python3
"""Generate the 10 prepared SEO pages as a reversible static overlay."""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST_PATH = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
CONTENT_PATH = ROOT / "seo" / "SEO_PAGES_2026.md"
CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "https://canisharethis.com").rstrip("/")


def inline(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"`(.+?)`", r"<code>\1</code>", value)
    return value


def slugify(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "section"


def extract_page_section(source: str, route: str) -> str:
    pattern = re.compile(
        rf"^#\s+\d+\.\s+{re.escape(route)}\s*$\n(?P<body>.*?)(?=^---\s*$|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"No content section found for {route}")
    body = match.group("body")
    marker = "## Above-the-fold answer"
    if marker not in body:
        raise RuntimeError(f"Missing above-the-fold section for {route}")
    return body.split(marker, 1)[1].strip()


def static_route_exists(route: str, priority_routes: set[str]) -> bool:
    if route in priority_routes or route == "/":
        return True
    rel = route.lstrip("/").rstrip("/")
    return any(
        p.is_file()
        for p in (DIST / rel, DIST / f"{rel}.html", DIST / rel / "index.html")
    )


def render_body(markdown: str, priority_routes: set[str]) -> str:
    """Turn editorial markdown into short, scannable responsive content cards."""
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    mode = "lead"
    section_open = False
    faq_open = False
    related_open = False

    def close_faq() -> None:
        nonlocal faq_open
        if faq_open:
            out.append("</article>")
            faq_open = False

    def close_section() -> None:
        nonlocal section_open
        close_faq()
        if section_open:
            out.append("</section>")
            section_open = False

    def close_related() -> None:
        nonlocal related_open
        if related_open:
            out.append("</div></nav>")
            related_open = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(x.strip() for x in paragraph).strip()
            if text:
                css = ' class="lead-text"' if mode == "lead" else ""
                out.append(f"<p{css}>{inline(text)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            out.append('<ul class="check-list">' + "".join(list_items) + "</ul>")
            list_items = []

    def open_content_section(title: str) -> None:
        nonlocal section_open
        close_related()
        close_section()
        ident = slugify(title)
        out.append(f'<section class="content-card" id="{html.escape(ident, quote=True)}">')
        out.append(f"<h2>{inline(title)}</h2>")
        section_open = True

    out.append('<section class="lead-card" aria-label="Quick answer">')

    for raw in markdown.splitlines():
        text = raw.strip()
        if not text:
            flush_paragraph()
            flush_list()
            continue

        if text == "## Main copy":
            flush_paragraph()
            flush_list()
            out.append("</section>")
            mode = "main"
            continue

        if text == "## FAQ":
            flush_paragraph()
            flush_list()
            close_related()
            close_section()
            mode = "faq"
            out.append('<section class="faq-section" aria-labelledby="faq-title">')
            out.append('<div class="section-heading"><span class="section-kicker">FAQ</span><h2 id="faq-title">Frequently asked questions</h2></div>')
            section_open = True
            continue

        if text == "## Internal links":
            flush_paragraph()
            flush_list()
            close_section()
            mode = "related"
            out.append('<nav class="related-section" aria-labelledby="related-title">')
            out.append('<div class="section-heading"><span class="section-kicker">Keep checking</span><h2 id="related-title">Related checks</h2></div>')
            out.append('<div class="related-grid">')
            related_open = True
            continue

        if text.startswith("## "):
            flush_paragraph()
            flush_list()
            open_content_section(text[3:])
            mode = "main"
            continue

        if text.startswith("### "):
            flush_paragraph()
            flush_list()
            title = text[4:].strip()
            if mode == "faq":
                close_faq()
                out.append('<article class="faq-card">')
                out.append(f"<h3>{inline(title)}</h3>")
                faq_open = True
            else:
                open_content_section(title)
                mode = "main"
            continue

        if text.startswith("- "):
            flush_paragraph()
            item = text[2:].strip()
            if mode == "related":
                match = re.match(r"`?(/[^`\s]+)`?\s*(?:(?:—|-)\s*(.+))?$", item)
                if match:
                    target, label = match.groups()
                    if static_route_exists(target, priority_routes):
                        label = (label or target.strip("/").replace("-", " ").title()).strip()
                        out.append(
                            f'<a class="related-card" href="{html.escape(target, quote=True)}">'
                            f'<span class="related-label">{inline(label)}</span>'
                            '<span class="related-arrow" aria-hidden="true">→</span>'
                            "</a>"
                        )
                    continue
            list_items.append(f"<li>{inline(item)}</li>")
            continue

        numbered = re.match(r"^\d+\.\s+(.+)$", text)
        if numbered:
            flush_paragraph()
            list_items.append(f"<li>{inline(numbered.group(1))}</li>")
            continue

        paragraph.append(text)

    flush_paragraph()
    flush_list()

    if mode == "lead":
        out.append("</section>")
    elif mode == "related":
        close_related()
    else:
        close_section()

    return "\n".join(out)


def json_ld(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_page(route: dict, body_html: str) -> str:
    path = route["path"]
    canonical = CANONICAL_HOST + path
    title = route["title"]
    description = route["description"]
    h1 = route["h1"]
    cluster_label = {
        "google-drive": "Google Drive",
        "dropbox": "Dropbox",
        "comparison": "Comparison",
    }.get(route.get("cluster", ""), str(route.get("cluster", "Link sharing")).replace("-", " ").title())

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": CANONICAL_HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": canonical},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": CANONICAL_HOST + "/"},
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="robots" content="noindex,follow">
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:url" content="{html.escape(canonical, quote=True)}">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">{json_ld(breadcrumb)}</script>
  <script type="application/ld+json">{json_ld(webpage)}</script>
  <style>
    :root{{
      color-scheme:light dark;
      --bg:#f5f6f8;
      --card:#ffffff;
      --card-soft:#f9fafb;
      --text:#17191d;
      --muted:#69707d;
      --line:#e4e7ec;
      --accent:#111827;
      --accent-text:#ffffff;
      --shadow:0 12px 34px rgba(17,24,39,.06);
      --radius:20px;
    }}
    @media(prefers-color-scheme:dark){{
      :root{{
        --bg:#0d0f12;
        --card:#15181d;
        --card-soft:#111419;
        --text:#f3f4f6;
        --muted:#a6acb7;
        --line:#2a2f37;
        --accent:#f3f4f6;
        --accent-text:#111318;
        --shadow:0 14px 34px rgba(0,0,0,.22);
      }}
    }}
    *{{box-sizing:border-box}}
    html{{scroll-behavior:smooth}}
    body{{
      margin:0;
      background:var(--bg);
      color:var(--text);
      font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      -webkit-font-smoothing:antialiased;
    }}
    a{{color:inherit}}
    header{{
      position:sticky;
      top:0;
      z-index:10;
      border-bottom:1px solid var(--line);
      background:var(--bg);
    }}
    .nav{{
      max-width:1100px;
      margin:auto;
      padding:14px 24px;
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:16px;
    }}
    .brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}
    .button{{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-height:44px;
      background:var(--accent);
      color:var(--accent-text);
      padding:10px 16px;
      border-radius:12px;
      text-decoration:none;
      font-weight:750;
      line-height:1.2;
    }}
    main{{max-width:980px;margin:0 auto;padding:42px 24px 80px}}
    .hero{{max-width:820px;margin:0 auto 28px}}
    .crumbs{{font-size:14px;color:var(--muted);margin-bottom:20px}}
    .crumbs a{{text-underline-offset:3px}}
    .eyebrow{{
      display:inline-flex;
      align-items:center;
      padding:6px 10px;
      margin-bottom:14px;
      border:1px solid var(--line);
      border-radius:999px;
      background:var(--card);
      color:var(--muted);
      font-size:13px;
      font-weight:750;
    }}
    h1{{
      max-width:790px;
      font-size:clamp(34px,6vw,58px);
      line-height:1.03;
      letter-spacing:-.045em;
      margin:0;
      text-wrap:balance;
    }}
    .article{{max-width:820px;margin:0 auto}}
    .lead-card{{
      margin:0 0 20px;
      padding:clamp(22px,4vw,34px);
      border:1px solid var(--line);
      border-radius:var(--radius);
      background:var(--card);
      box-shadow:var(--shadow);
    }}
    .lead-card::before{{
      content:"Quick answer";
      display:block;
      margin-bottom:10px;
      color:var(--muted);
      font-size:12px;
      font-weight:850;
      letter-spacing:.09em;
      text-transform:uppercase;
    }}
    .lead-text{{font-size:clamp(17px,2.5vw,20px);line-height:1.62;margin:0 0 14px}}
    .lead-text:last-child{{margin-bottom:0}}
    .content-card{{
      margin:16px 0;
      padding:clamp(20px,3.5vw,30px);
      border:1px solid var(--line);
      border-radius:var(--radius);
      background:var(--card);
    }}
    .content-card h2{{
      margin:0 0 14px;
      font-size:clamp(22px,3vw,28px);
      line-height:1.18;
      letter-spacing:-.025em;
      text-wrap:balance;
    }}
    p{{margin:0 0 15px}}
    p:last-child{{margin-bottom:0}}
    .check-list{{
      list-style:none;
      padding:0;
      margin:18px 0 0;
      display:grid;
      gap:10px;
    }}
    .check-list li{{
      position:relative;
      padding:12px 14px 12px 40px;
      border-radius:13px;
      background:var(--card-soft);
      border:1px solid var(--line);
    }}
    .check-list li::before{{
      content:"✓";
      position:absolute;
      left:14px;
      top:12px;
      font-weight:900;
    }}
    code{{font-size:.9em;background:var(--card-soft);border:1px solid var(--line);padding:2px 6px;border-radius:6px}}
    .section-heading{{margin:34px 0 14px}}
    .section-heading h2{{
      margin:2px 0 0;
      font-size:clamp(25px,3.5vw,32px);
      line-height:1.15;
      letter-spacing:-.03em;
    }}
    .section-kicker{{
      color:var(--muted);
      font-size:12px;
      font-weight:850;
      letter-spacing:.09em;
      text-transform:uppercase;
    }}
    .faq-section{{margin-top:20px}}
    .faq-card{{
      margin:12px 0;
      padding:20px 22px;
      border:1px solid var(--line);
      border-radius:16px;
      background:var(--card);
    }}
    .faq-card h3{{margin:0 0 8px;font-size:18px;line-height:1.3;letter-spacing:-.01em}}
    .related-section{{margin-top:24px}}
    .related-grid{{
      display:grid;
      grid-template-columns:repeat(2,minmax(0,1fr));
      gap:12px;
    }}
    .related-card{{
      min-height:76px;
      padding:17px 18px;
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:16px;
      border:1px solid var(--line);
      border-radius:16px;
      background:var(--card);
      text-decoration:none;
      font-weight:750;
      transition:transform .16s ease,box-shadow .16s ease;
    }}
    .related-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow)}}
    .related-arrow{{font-size:22px;color:var(--muted);flex:0 0 auto}}
    .cta{{
      margin:28px 0 0;
      padding:clamp(24px,4vw,34px);
      border:1px solid var(--line);
      background:var(--card);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
    }}
    .cta h2{{margin:0 0 8px;font-size:clamp(24px,3.5vw,30px);letter-spacing:-.025em}}
    .cta p{{max-width:640px;color:var(--muted);margin-bottom:18px}}
    footer{{border-top:1px solid var(--line);padding:28px 20px;text-align:center;color:var(--muted);font-size:14px}}
    @media(max-width:680px){{
      .nav{{padding:11px 16px}}
      .brand{{font-size:15px}}
      .nav .button{{min-height:40px;padding:9px 12px;font-size:14px}}
      main{{padding:28px 14px 58px}}
      .hero{{margin-bottom:20px}}
      .crumbs{{margin-bottom:16px}}
      h1{{font-size:clamp(32px,11vw,44px);line-height:1.06}}
      .lead-card,.content-card,.cta{{border-radius:17px}}
      .content-card{{margin:12px 0}}
      .related-grid{{grid-template-columns:1fr}}
      .related-card{{min-height:64px}}
      .section-heading{{margin-top:28px}}
      .faq-card{{padding:18px}}
    }}
    @media(min-width:900px){{
      .content-card{{padding:30px 32px}}
      .faq-card{{padding:22px 24px}}
    }}
    @media(prefers-reduced-motion:reduce){{
      *{{scroll-behavior:auto!important;transition:none!important}}
    }}
  </style>
</head>
<body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main>
  <section class="hero">
    <div class="crumbs"><a href="/">Home</a> / {html.escape(cluster_label)}</div>
    <span class="eyebrow">{html.escape(cluster_label)} guide</span>
    <h1>{html.escape(h1)}</h1>
  </section>
  <article class="article">
    {body_html}
    <section class="cta">
      <h2>Check the link before you send it</h2>
      <p>Paste the final share URL into Can I Share This? and review the recipient-access verdict before sending.</p>
      <a class="button" href="/">Check a link</a>
    </section>
  </article>
</main>
<footer>Can I Share This? · Recipient-access checks before sharing</footer>
</body>
</html>"""


def write_route(route: dict, source: str, priority_routes: set[str]) -> None:
    section = extract_page_section(source, route["path"])
    body_html = render_body(section, priority_routes)
    target = DIST / f"{route['path'].lstrip('/').rstrip('/')}.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_page(route, body_html), encoding="utf-8")


def update_sitemap(routes: list[dict]) -> None:
    sitemap = DIST / "sitemap.xml"
    urls: set[str] = set()

    if sitemap.is_file():
        old = sitemap.read_text(encoding="utf-8", errors="replace")
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(CANONICAL_HOST + (parsed.path.rstrip("/") or "/"))

    urls.add(CANONICAL_HOST + "/")
    for route in routes:
        urls.add(CANONICAL_HOST + route["path"])

    entries = "\n".join(
        f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls)
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries
        + '\n</urlset>\n'
    )
    sitemap.write_text(xml, encoding="utf-8")


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    routes = manifest["routes"]
    source = CONTENT_PATH.read_text(encoding="utf-8")
    priority_routes = {route["path"] for route in routes}

    for route in routes:
        write_route(route, source, priority_routes)
    update_sitemap(routes)
    print(f"Generated {len(routes)} priority SEO pages on top of the static preview")


if __name__ == "__main__":
    main()
