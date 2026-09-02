#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit

ORIGIN = "https://canisharethis.com"
SITEMAP_URL = ORIGIN + "/sitemap.xml"
ROBOTS_URL = ORIGIN + "/robots.txt"
USER_AGENT = "CanIShareThis-Production-Audit/1.0"
TIMEOUT = 20
EXPECTED_MIN_URLS = 60


class RedirectTracker(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[tuple[int, str]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_h1 = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.h1s: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.descriptions: list[str] = []
        self.analytics = False

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        attrs_d = {str(k).lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
            self.h1_parts = []
        elif tag == "link" and "canonical" in attrs_d.get("rel", "").lower().split():
            href = attrs_d.get("href", "").strip()
            if href:
                self.canonicals.append(href)
        elif tag == "meta":
            name = attrs_d.get("name", "").strip().lower()
            content = attrs_d.get("content", "").strip()
            if name == "robots":
                self.robots.append(content)
            elif name == "description":
                self.descriptions.append(content)
        elif tag == "script":
            src = attrs_d.get("src", "")
            if "/_vercel/insights/script.js" in src or "vercel-insights.com" in src:
                self.analytics = True

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
            text = clean("".join(self.h1_parts))
            if text:
                self.h1s.append(text)
            self.h1_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)

    @property
    def title(self) -> str:
        return clean("".join(self.title_parts))


@dataclass
class FetchResult:
    requested_url: str
    final_url: str
    status: int
    body: bytes
    headers: dict[str, str]
    redirects: list[tuple[int, str]]
    elapsed_ms: int


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def normalize_url(url: str) -> str:
    p = urlsplit(url.strip())
    path = p.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, "", ""))


def fetch(url: str) -> FetchResult:
    tracker = RedirectTracker()
    opener = urllib.request.build_opener(tracker)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain;q=0.9,*/*;q=0.8"})
    start = time.monotonic()
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            body = r.read(3_000_000)
            status = int(getattr(r, "status", r.getcode()))
            final_url = r.geturl()
            headers = {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        body = e.read(500_000)
        status = int(e.code)
        final_url = e.geturl()
        headers = {k.lower(): v for k, v in e.headers.items()}
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return FetchResult(url, final_url, status, body, headers, list(tracker.chain), elapsed_ms)


def decode_body(result: FetchResult) -> str:
    content_type = result.headers.get("content-type", "")
    m = re.search(r"charset=([^;\s]+)", content_type, re.I)
    enc = (m.group(1).strip('"\'') if m else "utf-8") or "utf-8"
    try:
        return result.body.decode(enc, errors="replace")
    except LookupError:
        return result.body.decode("utf-8", errors="replace")


def load_sitemap() -> list[str]:
    res = fetch(SITEMAP_URL)
    if res.status != 200:
        raise RuntimeError(f"sitemap.xml returned HTTP {res.status}")
    root = ET.fromstring(decode_body(res))
    urls: list[str] = []
    for elem in root.iter():
        if elem.tag.lower().endswith("loc") and elem.text:
            value = elem.text.strip()
            if value.startswith(ORIGIN):
                urls.append(value)
    urls = list(dict.fromkeys(urls))
    if len(urls) < EXPECTED_MIN_URLS:
        raise RuntimeError(f"sitemap contains only {len(urls)} URLs; expected at least {EXPECTED_MIN_URLS}")
    return urls


def check_robots() -> list[str]:
    issues: list[str] = []
    res = fetch(ROBOTS_URL)
    text = decode_body(res)
    if res.status != 200:
        issues.append(f"robots.txt HTTP {res.status}")
    if "User-agent: *" not in text:
        issues.append("robots.txt missing User-agent: *")
    if "Allow: /" not in text:
        issues.append("robots.txt missing Allow: /")
    if SITEMAP_URL not in text:
        issues.append("robots.txt missing sitemap declaration")
    return issues


def soft_404(title: str, body_text: str) -> bool:
    t = title.lower()
    prefix = clean(re.sub(r"<[^>]+>", " ", body_text[:2500])).lower()
    markers = ["404", "not found", "page not found", "this page could not be found"]
    return any(m in t for m in markers) or prefix.startswith("404: not_found") or "code: not_found" in prefix


def main() -> None:
    fatal: list[str] = []
    warnings: list[str] = []
    fatal.extend(check_robots())

    urls = load_sitemap()
    sitemap_norm = {normalize_url(u) for u in urls}
    rows: list[dict[str, object]] = []
    titles: defaultdict[str, list[str]] = defaultdict(list)
    h1s: defaultdict[str, list[str]] = defaultdict(list)
    canonicals_seen: defaultdict[str, list[str]] = defaultdict(list)

    print(f"Auditing {len(urls)} production URLs from {SITEMAP_URL}")
    print("URL\tHTTP\tRedirects\tCanonical\tRobots\tTitle\tH1\tAnalytics\tms\tProblems")

    for i, url in enumerate(urls, 1):
        problems: list[str] = []
        try:
            res = fetch(url)
            body_text = decode_body(res)
        except Exception as exc:
            problems.append(f"FETCH_ERROR {type(exc).__name__}: {exc}")
            print(f"{url}\tERR\t-\t-\t-\t-\t-\t-\t-\t{' | '.join(problems)}")
            fatal.extend(f"{url}: {p}" for p in problems)
            continue

        if res.status != 200:
            problems.append(f"HTTP_{res.status}")

        if res.redirects:
            if normalize_url(res.final_url) != normalize_url(url):
                problems.append(f"REDIRECT_TO {res.final_url}")
            else:
                warnings.append(f"{url}: unnecessary redirect chain {res.redirects}")

        ctype = res.headers.get("content-type", "").lower()
        if "text/html" not in ctype:
            problems.append(f"CONTENT_TYPE {ctype or 'missing'}")
            parser = PageParser()
        else:
            parser = PageParser()
            try:
                parser.feed(body_text)
            except Exception as exc:
                problems.append(f"HTML_PARSE {type(exc).__name__}")

        title = parser.title
        canonical = parser.canonicals[0] if len(parser.canonicals) == 1 else ""
        robots = parser.robots[0] if parser.robots else ""
        description = parser.descriptions[0] if parser.descriptions else ""
        h1 = parser.h1s[0] if len(parser.h1s) == 1 else ""

        if len(parser.canonicals) != 1:
            problems.append(f"CANONICAL_COUNT_{len(parser.canonicals)}")
        elif normalize_url(canonical) != normalize_url(url):
            problems.append(f"CANONICAL_MISMATCH {canonical}")

        if not robots:
            problems.append("ROBOTS_META_MISSING")
        else:
            rlow = robots.lower().replace(" ", "")
            if "noindex" in rlow:
                problems.append("NOINDEX")
            if "index" not in rlow:
                warnings.append(f"{url}: robots meta does not explicitly contain index ({robots})")

        if not title:
            problems.append("TITLE_MISSING")
        if not description:
            problems.append("DESCRIPTION_MISSING")
        if len(parser.h1s) != 1:
            problems.append(f"H1_COUNT_{len(parser.h1s)}")
        if soft_404(title, body_text):
            problems.append("SOFT_404_SIGNAL")
        if not parser.analytics:
            warnings.append(f"{url}: Vercel Analytics script not detected")

        if title:
            titles[title].append(url)
        if h1:
            h1s[h1].append(url)
        if canonical:
            canonicals_seen[normalize_url(canonical)].append(url)

        if normalize_url(url) not in sitemap_norm:
            problems.append("NOT_IN_SITEMAP")

        row = {
            "url": url,
            "http": res.status,
            "redirects": len(res.redirects),
            "canonical": canonical,
            "robots": robots,
            "title": title,
            "h1": h1,
            "analytics": parser.analytics,
            "ms": res.elapsed_ms,
            "problems": problems,
        }
        rows.append(row)
        print(
            f"{url}\t{res.status}\t{len(res.redirects)}\t{canonical or '-'}\t{robots or '-'}\t"
            f"{title or '-'}\t{h1 or '-'}\t{'yes' if parser.analytics else 'no'}\t{res.elapsed_ms}\t"
            f"{' | '.join(problems) if problems else 'OK'}"
        )
        fatal.extend(f"{url}: {p}" for p in problems)
        time.sleep(0.05)

    for title, members in titles.items():
        if len(members) > 1:
            fatal.append("DUPLICATE_TITLE " + title + " -> " + ", ".join(members))
    for h1, members in h1s.items():
        if len(members) > 1:
            warnings.append("DUPLICATE_H1 " + h1 + " -> " + ", ".join(members))
    for canonical, members in canonicals_seen.items():
        if len(members) > 1:
            fatal.append("DUPLICATE_CANONICAL " + canonical + " <- " + ", ".join(members))

    status_counts = Counter(int(r["http"]) for r in rows)
    redirect_count = sum(int(r["redirects"]) for r in rows)
    avg_ms = round(sum(int(r["ms"]) for r in rows) / len(rows)) if rows else 0

    print("\n=== PRODUCTION AUDIT SUMMARY ===")
    print(f"Sitemap URLs: {len(urls)}")
    print("HTTP statuses: " + ", ".join(f"{k}={v}" for k, v in sorted(status_counts.items())))
    print(f"Redirect hops observed: {redirect_count}")
    print(f"Average response time: {avg_ms} ms")
    print(f"Fatal SEO/availability issues: {len(fatal)}")
    print(f"Warnings: {len(warnings)}")

    if warnings:
        print("\n=== WARNINGS ===")
        for item in warnings:
            print("WARN", item)

    if fatal:
        print("\n=== FAILURES ===")
        for item in fatal:
            print("FAIL", item)
        sys.exit(1)

    print("PRODUCTION AUDIT PASSED")


if __name__ == "__main__":
    main()
