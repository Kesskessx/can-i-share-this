#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qsl

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "tests" / "universal_safety_matrix.json"
SEO_GENERATOR = ROOT / "scripts" / "generate_context_checker_pages.py"

ALLOWED_MODES = {
    "safe-live",
    "offline-fixture",
    "official-threat-fixture",
    "privacy-guard",
    "email-safe",
}
NETWORK_MODES = {"safe-live", "official-threat-fixture"}
SAFE_LIVE_HOSTS = {
    "google.com", "www.google.com",
    "x.com", "reddit.com", "www.reddit.com",
    "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
    "open.spotify.com", "spotify.com",
    "drive.google.com", "dropbox.com", "www.dropbox.com",
    "onedrive.live.com", "notion.so", "www.notion.so",
    "amazon.com", "www.amazon.com", "github.com",
    "gamdom.com", "www.gamdom.com",
    "coinbase.com", "www.coinbase.com",
}
OFFICIAL_THREAT_HOSTS = {"testsafebrowsing.appspot.com"}
REQUIRED_CONTENT = {
    "Website", "Social media", "Social video", "Community or discussion",
    "Video", "Music or audio", "Cloud file or folder", "Online document or workspace",
    "Shopping link", "Code or developer link", "PDF document", "Image",
    "Document or data file", "Compressed file", "Software or app file",
    "Shortened link", "Gambling / betting website", "Crypto / financial website",
    "Adult-content website", "Weapons-related website", "Drug-related website",
    "Torrent / file-sharing website",
}
REQUIRED_ROUTES = {
    "/sms-link-checker",
    "/whatsapp-link-checker",
    "/qr-code-scam-checker",
    "/download-link-checker",
    "/short-link-checker",
    "/is-this-email-safe",
    "/gambling-link-safety",
    "/crypto-scam-link-checker",
}
FORBIDDEN_MARKETING = {
    "100% safe",
    "guaranteed safe",
    "guarantees safety",
    "virus-free",
    "malware-free guarantee",
}

def registeredish_host(host: str) -> str:
    return host.lower().strip(".")

def load_pages_literal(source: str):
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "PAGES" for t in node.targets):
                return ast.literal_eval(node.value)
    raise RuntimeError("PAGES literal not found in SEO generator")

def validate_matrix():
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if len(cases) < 45:
        raise RuntimeError(f"Expected at least 45 matrix cases, found {len(cases)}")

    ids = set()
    modes = set()
    contents = set()
    privacy_count = email_count = redirect_count = age_count = threat_count = 0

    for case in cases:
        cid = case.get("id")
        if not cid or cid in ids:
            raise RuntimeError(f"Missing or duplicate test id: {cid}")
        ids.add(cid)

        mode = case.get("mode")
        if mode not in ALLOWED_MODES:
            raise RuntimeError(f"{cid}: unsupported mode {mode}")
        modes.add(mode)

        value = str(case.get("input", ""))
        expected = case.get("expected") or {}
        if expected.get("content"):
            contents.add(expected["content"])

        if "REDACTED_TEST_" not in value and re.search(r"(?i)(token|password|secret|apikey|api_key)=([^&\s]+)", value):
            raise RuntimeError(f"{cid}: possible real secret-like test value")

        if mode in NETWORK_MODES:
            parsed = urlparse(value)
            host = registeredish_host(parsed.hostname or "")
            if mode == "safe-live" and host not in SAFE_LIVE_HOSTS:
                raise RuntimeError(f"{cid}: live host not allowlisted: {host}")
            if mode == "official-threat-fixture" and host not in OFFICIAL_THREAT_HOSTS:
                raise RuntimeError(f"{cid}: non-official threat fixture host: {host}")

        if mode == "privacy-guard":
            privacy_count += 1
            if expected.get("external_reputation") != "blocked":
                raise RuntimeError(f"{cid}: privacy guard must require external reputation blocking")
            parsed = urlparse(value)
            if not (parsed.username or parsed.password or parse_qsl(parsed.query, keep_blank_values=True)):
                raise RuntimeError(f"{cid}: privacy guard has no credential/query signal")

        if expected.get("input_type") == "email":
            email_count += 1
            if expected.get("external_web_risk") not in {"not-used", None}:
                raise RuntimeError(f"{cid}: email path must not use Web Risk")

        fixture = case.get("fixture") or {}
        if fixture.get("redirects"):
            redirect_count += 1
        if "domain_age_days" in fixture:
            age_count += 1
        if mode == "official-threat-fixture":
            threat_count += 1

    missing_content = REQUIRED_CONTENT - contents
    if missing_content:
        raise RuntimeError("Missing content coverage: " + ", ".join(sorted(missing_content)))
    if privacy_count < 3 or email_count < 4 or redirect_count < 2 or age_count < 4 or threat_count < 2:
        raise RuntimeError(
            f"Coverage too small: privacy={privacy_count}, email={email_count}, "
            f"redirect={redirect_count}, domain_age={age_count}, threat={threat_count}"
        )
    if modes != ALLOWED_MODES:
        raise RuntimeError(f"Matrix does not exercise every mode: {sorted(modes)}")
    return len(cases)

def validate_seo_batch():
    source = SEO_GENERATOR.read_text(encoding="utf-8")
    pages = load_pages_literal(source)
    routes = {p["path"] for p in pages}
    if routes != REQUIRED_ROUTES:
        raise RuntimeError(f"Prepared SEO routes differ from expected: {sorted(routes)}")
    if len(pages) != 8:
        raise RuntimeError(f"Expected exactly 8 prepared SEO pages, found {len(pages)}")

    all_text = source.lower()
    for forbidden in FORBIDDEN_MARKETING:
        if forbidden in all_text:
            raise RuntimeError(f"Forbidden absolute-safety claim in SEO batch: {forbidden}")

    for page in pages:
        path = page["path"]
        title = page["title"]
        desc = page["description"]
        if not 35 <= len(title) <= 65:
            raise RuntimeError(f"{path}: title length {len(title)} outside 35..65")
        if not 110 <= len(desc) <= 160:
            raise RuntimeError(f"{path}: description length {len(desc)} outside 110..160")
        if len(page.get("answer", "")) < 120:
            raise RuntimeError(f"{path}: At-a-glance answer is too thin")
        if len(page.get("why", [])) < 2:
            raise RuntimeError(f"{path}: needs at least two unique explanatory paragraphs")
        if len(page.get("checks", [])) < 4:
            raise RuntimeError(f"{path}: needs at least four scanner capability explanations")
        if len(page.get("safe_steps", [])) < 4:
            raise RuntimeError(f"{path}: needs at least four safer next steps")
        if len(page.get("faqs", [])) < 4:
            raise RuntimeError(f"{path}: needs at least four FAQs")
        if len(page.get("related", [])) < 4:
            raise RuntimeError(f"{path}: needs at least four internal related links")
        if len(page.get("sources", [])) < 2:
            raise RuntimeError(f"{path}: needs at least two primary references")
        for label, url in page["sources"]:
            if not url.startswith("https://"):
                raise RuntimeError(f"{path}: source must use HTTPS: {url}")
        for related in page["related"]:
            if not related.startswith("/"):
                raise RuntimeError(f"{path}: related link must be internal: {related}")

    required_tokens = [
        'data-page-batch="context-seo-v1"',
        "At a glance",
        "What Can I Share This? checks",
        "What the result cannot prove",
        "No scanner can guarantee that a link, sender or website is safe.",
        "Frequently asked questions",
        "application/ld+json",
        "FAQPage",
        "BreadcrumbList",
        "index,follow",
        "Check it before you trust it",
    ]
    for token in required_tokens:
        if token not in source:
            raise RuntimeError(f"SEO generator is missing required token: {token}")
    return len(pages)

def main():
    for path in (MATRIX, SEO_GENERATOR):
        if not path.is_file():
            raise RuntimeError(f"Missing prepared file: {path}")
    case_count = validate_matrix()
    page_count = validate_seo_batch()
    print(f"Prepared batch validated: {case_count} Universal Safety Checker cases + {page_count} SEO pages")

if __name__ == "__main__":
    main()
