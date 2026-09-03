#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

TARGET_IDS = ("how-it-works", "use-cases")
TARGET_TEXT = (
    "Three steps. One clear answer.",
    "Check the suspicious thing you received.",
)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError("Homepage not found")

    source = HOME.read_text(encoding="utf-8")
    removed = 0

    for section_id in TARGET_IDS:
        pattern = rf'\s*<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>.*?</section>'
        source, count = re.subn(pattern, "", source, count=1, flags=re.S)
        removed += count

    for text in TARGET_TEXT:
        if text in source:
            raise RuntimeError(f"Redundant homepage section still present: {text}")

    if removed != 2:
        raise RuntimeError(f"Expected to remove 2 redundant homepage sections, removed {removed}")

    if 'id="capability-strip"' not in source:
        raise RuntimeError("Capability strip must remain on homepage")

    HOME.write_text(source, encoding="utf-8")
    print("Removed redundant homepage explainer sections")


if __name__ == "__main__":
    main()
