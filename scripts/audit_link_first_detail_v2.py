#!/usr/bin/env python3
from pathlib import Path
import re

HOME=Path(__file__).resolve().parents[1]/"dist"/"index.html"

def main():
    if not HOME.is_file():
        raise SystemExit("Link-first/V2 integration audit failed: homepage missing")
    s=HOME.read_text(encoding="utf-8")
    if 'cist-detailed-analysis-v2-script' not in s:
        raise SystemExit("Link-first/V2 integration audit failed: Detailed Analysis V2 missing")

    match=re.search(r'<script id="cist-link-first-home-v1-script">(.*?)</script>',s,re.S)
    if not match:
        raise SystemExit("Link-first/V2 integration audit failed: link-first script missing")
    script=match.group(1)

    required=[
        "preservedDetail=document.getElementById('cist-detail-v2')",
        "body.insertBefore(preservedDetail,old)",
        "if(old)old.remove()",
        "card.insertBefore(detail,actions)",
    ]
    missing=[x for x in required if x not in script]
    if missing:
        raise SystemExit("Link-first/V2 integration audit failed:\n- "+"\n- ".join("missing "+x for x in missing))

    preserve=script.index("body.insertBefore(preservedDetail,old)")
    remove=script.index("if(old)old.remove()")
    reattach=script.index("card.insertBefore(detail,actions)")
    if not (preserve < remove < reattach):
        raise SystemExit("Link-first/V2 integration audit failed: preserve/remove/reattach order is unsafe")

    print("Link-first/V2 integration audit passed: detail survives result rerenders")

if __name__=="__main__":
    main()
