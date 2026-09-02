#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

STYLE = r'''
<style id="cist-wordmark-logo-style">
.cist-wordmark{
  display:inline-flex;
  align-items:baseline;
  gap:.23em;
  color:var(--text,#17191d)!important;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-weight:850!important;
  letter-spacing:-.035em;
  line-height:1;
  text-decoration:none!important;
  white-space:nowrap;
}
.cist-wordmark-accent{color:#6578e8}
@media(prefers-color-scheme:dark){
  .cist-wordmark{color:var(--text,#f3f4f6)!important}
  .cist-wordmark-accent{color:#8ea2ff}
}
@media(max-width:600px){
  .cist-wordmark{font-size:14px!important;letter-spacing:-.025em}
}
</style>
'''

WORDMARK = '<span class="cist-wordmark-main">Can I Share</span><span class="cist-wordmark-accent">This?</span>'


def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def transform_anchor(match: re.Match[str]) -> str:
    attrs = match.group("attrs")
    body = match.group("body")
    text = plain_text(body).replace("↗ ", "").strip()
    classes = re.search(r'class="([^"]*)"', attrs, flags=re.I)
    class_names = classes.group(1).split() if classes else []

    if text != "Can I Share This?":
        return match.group(0)
    if not any(name in {"brand", "header-brand"} for name in class_names):
        return match.group(0)

    if classes:
        merged = class_names[:]
        if "cist-wordmark" not in merged:
            merged.append("cist-wordmark")
        attrs = attrs[:classes.start(1)] + " ".join(merged) + attrs[classes.end(1):]
    else:
        attrs += ' class="cist-wordmark"'

    return f"<a{attrs}>{WORDMARK}</a>"


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist/ does not exist")

    updated = 0
    found = 0
    for path in sorted(DIST.rglob("*.html")):
        source = path.read_text(encoding="utf-8")
        original = source

        source, count = re.subn(
            r"<a(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
            transform_anchor,
            source,
            flags=re.I | re.S,
        )
        if count:
            found += source.count('class="cist-wordmark-main"')

        if 'class="cist-wordmark-main"' in source and 'id="cist-wordmark-logo-style"' not in source:
            if "</head>" not in source:
                raise RuntimeError(f"Missing </head> in {path.name}")
            source = source.replace("</head>", STYLE + "\n</head>", 1)

        if source != original:
            path.write_text(source, encoding="utf-8")
            updated += 1

    home = DIST / "index.html"
    if not home.is_file():
        raise RuntimeError("Homepage not found")
    home_source = home.read_text(encoding="utf-8")
    required = [
        'class="cist-wordmark-main"',
        'class="cist-wordmark-accent">This?</span>',
        '#6578e8',
        '#8ea2ff',
    ]
    for token in required:
        if token not in home_source:
            raise RuntimeError(f"Wordmark guard failed: missing {token}")
    if "↗ Can I Share This?" in home_source:
        raise RuntimeError("Legacy arrow wordmark is still present on homepage")

    print(f"Applied text-only wordmark logo to {updated} pages ({found} brand anchors)")


if __name__ == "__main__":
    main()
