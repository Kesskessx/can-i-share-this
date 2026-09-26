#!/usr/bin/env python3
"""Audit canonical static pages for likely search-intent cannibalization.

This is intentionally conservative: it fails only on exact duplicate titles/H1s
between different canonical URLs. Near-duplicates are printed for review.
"""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITEMAP = DIST / "sitemap.xml"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"

STOP = {
    "the","a","an","and","or","to","of","for","your","you","is","my","this","that",
    "with","without","before","after","how","what","why","does","do","will","can","i",
    "it","in","on","from","our","anyone","link","links","checker","check","checking",
    "page","site","shared","sharing","share",
}

def clean_text(value: str) -> str:
    value = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()

def extract(pattern: str, doc: str) -> str:
    m = re.search(pattern, doc, re.I | re.S)
    return clean_text(m.group(1)) if m else ""

def tokens(value: str) -> set[str]:
    words = re.sub(r"[^a-z0-9]+", " ", value.lower()).split()
    return {w for w in words if len(w) >= 3 and w not in STOP}

def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0

def route_file(route: str) -> Path | None:
    clean = route.strip("/")
    candidates = [DIST / "index.html"] if not clean else [
        DIST / f"{clean}.html",
        DIST / clean / "index.html",
        DIST / clean,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None

def main() -> None:
    if not SITEMAP.is_file():
        raise SystemExit("Cannibalization audit: sitemap missing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    meta_by_path = {r["path"]: r for r in manifest.get("routes", [])}

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(SITEMAP).getroot()
    urls = [u.find("sm:loc", ns).text for u in root.findall("sm:url", ns)]
    pages = []

    for url in urls:
        route = urlparse(url).path or "/"
        path = route_file(route)
        if not path:
            continue
        doc = path.read_text(encoding="utf-8")
        title = extract(r"<title>(.*?)</title>", doc)
        h1 = extract(r"<h1\b[^>]*>([\s\S]*?)</h1>", doc)
        desc = extract(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', doc)
        main = extract(r"<main\b[^>]*>([\s\S]*?)</main>", doc) or clean_text(doc)
        cfg = meta_by_path.get(route, {})
        meta_text = " ".join([route, title, h1, desc, cfg.get("intent",""), cfg.get("primaryKeyword","")])
        pages.append({
            "route": route,
            "title": title,
            "h1": h1,
            "desc": desc,
            "cluster": cfg.get("cluster","unregistered"),
            "role": cfg.get("role","unregistered"),
            "intent": cfg.get("intent",""),
            "meta_tokens": tokens(meta_text),
            "body_tokens": tokens(main[:30000]),
        })

    exact_title = defaultdict(list)
    exact_h1 = defaultdict(list)
    for p in pages:
        if p["title"]:
            exact_title[p["title"].casefold()].append(p["route"])
        if p["h1"]:
            exact_h1[p["h1"].casefold()].append(p["route"])

    failures = []
    for value, routes in exact_title.items():
        if len(routes) > 1:
            failures.append(f"duplicate title across {routes}")
    for value, routes in exact_h1.items():
        if len(routes) > 1:
            failures.append(f"duplicate H1 across {routes}")

    pairs = []
    for i, a in enumerate(pages):
        for b in pages[i+1:]:
            meta_score = jaccard(a["meta_tokens"], b["meta_tokens"])
            body_score = jaccard(a["body_tokens"], b["body_tokens"])
            same_cluster = a["cluster"] == b["cluster"] and a["cluster"] != "unregistered"
            # Emphasize intent/metadata similarity; body templates can be shared safely.
            risk = (0.78 * meta_score) + (0.22 * body_score)
            if risk >= 0.34 or (same_cluster and meta_score >= 0.32):
                pairs.append({
                    "risk": risk,
                    "meta": meta_score,
                    "body": body_score,
                    "same_cluster": same_cluster,
                    "a": a,
                    "b": b,
                })

    pairs.sort(key=lambda x: x["risk"], reverse=True)

    print(f"Cannibalization audit: {len(pages)}/{len(urls)} sitemap URLs analyzed")
    print("Top review pairs:")
    for pair in pairs[:30]:
        a, b = pair["a"], pair["b"]
        print(
            f"REVIEW risk={pair['risk']:.2f} meta={pair['meta']:.2f} body={pair['body']:.2f} "
            f"cluster={'same' if pair['same_cluster'] else 'different'} :: "
            f"{a['route']} [{a['role']}: {a['intent']}] <-> "
            f"{b['route']} [{b['role']}: {b['intent']}]"
        )

    cluster_counts = defaultdict(int)
    for p in pages:
        cluster_counts[p["cluster"]] += 1
    print("Cluster sizes: " + ", ".join(f"{k}={v}" for k,v in sorted(cluster_counts.items())))

    if failures:
        raise SystemExit("Cannibalization audit failed:\n- " + "\n- ".join(failures))

if __name__ == "__main__":
    main()
