#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

STYLE = r'''
<style id="cist-capability-strip-style">
.capability-strip{width:min(720px,calc(100% - 28px));margin:22px auto 0;text-align:center}
.capability-label{margin:0 0 10px;color:var(--muted);font-size:12px;font-weight:800;letter-spacing:.01em}
.capability-list{display:flex;align-items:center;justify-content:center;gap:7px;flex-wrap:wrap}
.capability-chip{display:inline-flex;align-items:center;gap:6px;min-height:34px;padding:7px 10px;border:1px solid color-mix(in srgb,var(--line) 88%,transparent);border-radius:999px;background:color-mix(in srgb,var(--card) 82%,transparent);color:var(--muted);font-size:12px;font-weight:750;line-height:1;text-decoration:none;white-space:nowrap;transition:border-color .16s ease,background .16s ease,color .16s ease,transform .16s ease}
.capability-chip:hover{color:var(--text);border-color:color-mix(in srgb,var(--text) 18%,var(--line));background:var(--card);transform:translateY(-1px)}
.capability-icon{font-size:14px;line-height:1}
@media(max-width:600px){
  .capability-strip{margin-top:18px}
  .capability-label{margin-bottom:9px}
  .capability-list{justify-content:flex-start;flex-wrap:nowrap;overflow-x:auto;padding:0 1px 6px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .capability-list::-webkit-scrollbar{display:none}
  .capability-chip{flex:0 0 auto;min-height:33px;padding:7px 10px}
}
@media(prefers-reduced-motion:reduce){.capability-chip{transition:none}.capability-chip:hover{transform:none}}
</style>
'''

SECTION = r'''
<section id="capability-strip" class="capability-strip" aria-labelledby="capability-title">
  <p id="capability-title" class="capability-label">One scanner. More signals.</p>
  <nav class="capability-list" aria-label="Specialized safety checks">
    <a class="capability-chip" href="/sms-link-checker"><span class="capability-icon" aria-hidden="true">📱</span><span>SMS</span></a>
    <a class="capability-chip" href="/whatsapp-link-checker"><span class="capability-icon" aria-hidden="true">💬</span><span>WhatsApp</span></a>
    <a class="capability-chip" href="/qr-code-link-checker"><span class="capability-icon" aria-hidden="true">🔳</span><span>QR</span></a>
    <a class="capability-chip" href="/download-link-checker"><span class="capability-icon" aria-hidden="true">📦</span><span>Files</span></a>
    <a class="capability-chip" href="/short-link-checker"><span class="capability-icon" aria-hidden="true">🔗</span><span>Short links</span></a>
    <a class="capability-chip" href="/email-safety-checker"><span class="capability-icon" aria-hidden="true">✉️</span><span>Email</span></a>
    <a class="capability-chip" href="/crypto-scam-link-checker"><span class="capability-icon" aria-hidden="true">₿</span><span>Crypto</span></a>
    <a class="capability-chip" href="/gambling-link-safety"><span class="capability-icon" aria-hidden="true">🎰</span><span>Gambling</span></a>
  </nav>
</section>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError("Homepage not found")

    source = HOME.read_text(encoding="utf-8")

    source = re.sub(
        r'\s*<style id="cist-capability-strip-style">.*?</style>',
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'\s*<section id="capability-strip".*?</section>',
        "",
        source,
        count=1,
        flags=re.S,
    )

    if "</head>" not in source:
        raise RuntimeError("Homepage head closing tag not found")
    source = source.replace("</head>", STYLE + "\n</head>", 1)

    hero_pattern = r'(<section[^>]*class="[^"]*\bhero\b[^"]*"[^>]*>.*?</section>)'
    source, count = re.subn(hero_pattern, r"\1\n" + SECTION, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Expected one hero section, found {count}")

    required = [
        'id="capability-strip"',
        "One scanner. More signals.",
        "/sms-link-checker",
        "/whatsapp-link-checker",
        "/qr-code-link-checker",
        "/download-link-checker",
        "/short-link-checker",
        "/email-safety-checker",
        "/crypto-scam-link-checker",
        "/gambling-link-safety",
        "@media(max-width:600px)",
        "overflow-x:auto",
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f"Capability strip guard failed: missing {token}")

    HOME.write_text(source, encoding="utf-8")
    print("Applied compact homepage capability strip")


if __name__ == "__main__":
    main()
