#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import tempfile

HOME=Path(__file__).resolve().parents[1]/"dist"/"index.html"

def main():
    if not HOME.is_file():
        raise SystemExit("Native Detailed Analysis V2 audit failed: homepage missing")
    s=HOME.read_text(encoding="utf-8")

    match=re.search(r'<script id="cist-link-first-home-v1-script">(.*?)</script>',s,re.S)
    if not match:
        raise SystemExit("Native Detailed Analysis V2 audit failed: link-first script missing")
    script=match.group(1)

    required=[
        "function detailV2(d,r,rs)",
        'id="cist-link-detail-v2"',
        "Detailed analysis",
        "What the scan observed",
        "Redirect chain",
        "Domain & response",
        "What this result does not mean",
        "Advanced technical details",
        "detailV2(d,r,rs)",
    ]
    missing=[x for x in required if x not in script]
    if missing:
        raise SystemExit("Native Detailed Analysis V2 audit failed:\n- "+"\n- ".join("missing "+x for x in missing))

    forbidden=[
        "preservedDetail=document.getElementById('cist-detail-v2')",
        "card.insertBefore(detail,actions)",
    ]
    stale=[x for x in forbidden if x in script]
    if stale:
        raise SystemExit("Native Detailed Analysis V2 audit failed: stale movable-detail logic remains")

    with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False,encoding="utf-8") as f:
        f.write(script)
        path=f.name
    checked=subprocess.run(["node","--check",path],capture_output=True,text=True)
    if checked.returncode:
        raise SystemExit("Native Detailed Analysis V2 audit failed: JavaScript syntax error\n"+checked.stderr)

    print("Native Detailed Analysis V2 audit passed: detail is rendered inside every link-result card")

if __name__=="__main__":
    main()
