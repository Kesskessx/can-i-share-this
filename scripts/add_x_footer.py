#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"

X_URL = "https://x.com/CanIShareLink"
STYLE = r'''
<style id="cist-x-footer-style">
.x-follow{margin:14px auto 0;display:flex;justify-content:center}
.x-follow a{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--text);background:var(--card);font-weight:750;font-size:13px;transition:transform .15s ease,border-color .15s ease}
.x-follow a:hover{transform:translateY(-1px);border-color:var(--muted)}
.x-follow-logo{font-size:16px;line-height:1;font-weight:900}
@media(prefers-reduced-motion:reduce){.x-follow a{transition:none}.x-follow a:hover{transform:none}}
</style>
'''
BLOCK = f'''<div class="x-follow"><a href="{X_URL}" target="_blank" rel="noopener noreferrer" aria-label="Follow Can I Share This on X"><span class="x-follow-logo" aria-hidden="true">𝕏</span><span>Follow @CanIShareLink</span></a></div>'''


def main():
    source = INDEX.read_text(encoding="utf-8")
    if 'id="cist-x-footer-style"' not in source:
        source = source.replace("</head>", STYLE + "\n</head>", 1)
    if 'class="x-follow"' not in source:
        source = source.replace("</footer>", BLOCK + "</footer>", 1)
    INDEX.write_text(source, encoding="utf-8")
    print("Added X profile link to homepage footer")


if __name__ == "__main__":
    main()
