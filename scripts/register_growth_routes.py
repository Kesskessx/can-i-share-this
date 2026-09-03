#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"

ROUTES = [
    {"path":"/about","status":"active","index":True,"canonical":"/about","cluster":"trust-methodology","role":"reference","intent":"explain what Can I Share This is and distinguish it from ShareThis","primaryKeyword":"about Can I Share This","breadcrumbLabel":"About"},
    {"path":"/supported-checks","status":"active","index":True,"canonical":"/supported-checks","cluster":"universal-safety","role":"hub","intent":"browse every input type and safety check supported by Can I Share This","primaryKeyword":"supported safety checks","breadcrumbLabel":"Supported Checks"},
    {"path":"/scan-examples","status":"active","index":True,"canonical":"/scan-examples","cluster":"universal-safety","role":"reference","intent":"see synthetic examples of suspicious links QR destinations sender addresses and scan signals","primaryKeyword":"link scan examples","breadcrumbLabel":"Scan Examples"},
    {"path":"/security","status":"active","index":True,"canonical":"/security","cluster":"trust-methodology","role":"policy","intent":"understand scanner security privacy telemetry external reputation checks and limitations","primaryKeyword":"Can I Share This security","breadcrumbLabel":"Security"},
    {"path":"/scam-checker","status":"active","index":True,"canonical":"/scam-checker","cluster":"universal-safety","role":"hub","intent":"check suspicious links QR codes sender addresses short links and downloads for scam context","primaryKeyword":"scam checker","breadcrumbLabel":"Scam Checker"},
    {"path":"/virustotal-alternative-for-link-checks","status":"active","index":True,"canonical":"/virustotal-alternative-for-link-checks","cluster":"universal-safety","role":"comparison","intent":"compare a simple pre-click link checker with VirusTotal multi-engine URL analysis","primaryKeyword":"VirusTotal alternative for link checks","breadcrumbLabel":"VirusTotal Alternative"},
    {"path":"/google-safe-browsing-vs-link-checker","status":"active","index":True,"canonical":"/google-safe-browsing-vs-link-checker","cluster":"trust-methodology","role":"comparison","intent":"compare Google Safe Browsing reputation lists with structural and contextual link checking","primaryKeyword":"Google Safe Browsing vs link checker","breadcrumbLabel":"Google Safe Browsing vs Link Checker"},
    {"path":"/urlscan-alternative-for-simple-link-checks","status":"active","index":True,"canonical":"/urlscan-alternative-for-simple-link-checks","cluster":"universal-safety","role":"comparison","intent":"compare a simple pre-click link checker with urlscan website scanning","primaryKeyword":"urlscan alternative for simple link checks","breadcrumbLabel":"urlscan Alternative"}
]


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {route["path"]: route for route in data["routes"]}
    for route in ROUTES:
        existing[route["path"]] = route
    data["routes"] = sorted(existing.values(), key=lambda item: (item["path"] != "/", item["path"]))
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f'Registered {len(ROUTES)} growth routes in SEO manifest')


if __name__ == "__main__":
    main()
