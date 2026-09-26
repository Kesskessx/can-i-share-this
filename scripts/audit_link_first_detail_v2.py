#!/usr/bin/env python3
from pathlib import Path

HOME=Path(__file__).resolve().parents[1]/"dist"/"index.html"

def main():
    if not HOME.is_file():
        raise SystemExit("Link-first/V2 integration audit failed: homepage missing")
    s=HOME.read_text(encoding="utf-8")
    required=[
        'cist-detailed-analysis-v2-script',
        "preservedDetail=document.getElementById('cist-detail-v2')",
        "body.insertBefore(preservedDetail,old)",
        "card.insertBefore(detail,actions)",
        "document.getElementById('cist-link-first-result')",
    ]
    missing=[x for x in required if x not in s]
    if missing:
        raise SystemExit("Link-first/V2 integration audit failed:\n- "+"\n- ".join("missing "+x for x in missing))
    preserve=s.index("body.insertBefore(preservedDetail,old)")
    remove=s.index("if(old)old.remove()")
    reattach=s.index("card.insertBefore(detail,actions)")
    if not (preserve < remove < reattach):
        raise SystemExit("Link-first/V2 integration audit failed: preserve/remove/reattach order is unsafe")
    print("Link-first/V2 integration audit passed: detail survives result rerenders")

if __name__=="__main__":
    main()
