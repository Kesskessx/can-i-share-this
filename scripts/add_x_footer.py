#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"

X_URL = "https://x.com/CanIShareLink"
STYLE = r'''
<style id="cist-x-footer-style">
.x-follow{margin:10px auto 0;display:flex;justify-content:center}
.x-follow a{display:inline-flex;align-items:center;gap:6px;padding:2px 0;border:0;text-decoration:none;color:var(--muted);background:transparent;font-weight:650;font-size:12px;transition:color .15s ease}
.x-follow a:hover{color:var(--text)}
.x-follow-logo{font-size:13px;line-height:1;font-weight:900}
@media(prefers-reduced-motion:reduce){.x-follow a{transition:none}}
</style>
'''
BLOCK = f'''<div class="x-follow"><a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="Can I Share This on X"><span class="x-follow-logo" aria-hidden="true">𝕏</span><span>@CanIShareLink</span></a></div>'''


def main():
    source = INDEX.read_text(encoding="utf-8")
    if 'id="cist-x-footer-style"' not in source:
        source = source.replace("</head>", STYLE + "\n</head>", 1)
    if 'class="x-follow"' not in source:
        source = source.replace("</footer>", BLOCK + "</footer>", 1)
    INDEX.write_text(source, encoding="utf-8")
    print("Added compact X profile link to homepage footer")


if __name__ == "__main__":
    main()
