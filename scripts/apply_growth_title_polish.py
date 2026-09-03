#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

TITLES = {
    "scam-checker.html": "Scam Checker — Links, QR Codes, Email & Downloads",
    "google-safe-browsing-vs-link-checker.html": "Google Safe Browsing vs Link Checker — What's Different?",
    "urlscan-alternative-for-simple-link-checks.html": "urlscan.io Alternative — Simple Link Checks Explained",
}


def main() -> None:
    for filename, title in TITLES.items():
        path = DIST / filename
        if not path.is_file():
            raise RuntimeError(f"Missing growth page: {filename}")
        source = path.read_text(encoding="utf-8")
        source, count = re.subn(r"<title>.*?</title>", f"<title>{title}</title>", source, count=1, flags=re.S | re.I)
        if count != 1:
            raise RuntimeError(f"Missing title tag in {filename}")
        source = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', source, count=1, flags=re.I)
        path.write_text(source, encoding="utf-8")
    print(f"Polished {len(TITLES)} growth-page search titles")


if __name__ == "__main__":
    main()
