#!/usr/bin/env python3
"""Can I Share This? — universal deterministic safety scanner.

Designed for Vercel's Python runtime and local use. No external Python
packages or AI/API keys are required. The scanner does NOT claim that content
is safe; it scores observable risk signals and returns explainable evidence.

POST JSON examples:
  {"input": "https://example.com/login"}
  {"input": "Your parcel is held. Pay €1.99 at https://..."}
  {"input": "support@example.com"}
  {"input": "@someprofile"}
  {"input": "0x...", "context": "Send payment here"}
  {"input": "", "extractedText": "OCR text", "qrValues": ["https://..."]}

Local CLI:
  python api/python-scan.py "text or URL to scan"
"""

from __future__ import annotations

import ipaddress
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from email.utils import parseaddr
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, unquote, urlsplit

VERSION = "1.1.0"
MAX_INPUT_CHARS = 50_000
MAX_SIGNALS = 20
MAX_ENTITIES = 30

URL_RE = re.compile(r"https?://[^\s<>\"'\]\[(){}]+", re.I)
BARE_DOMAIN_RE = re.compile(
    r"(?<![@\w])(?:www\.)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?:/[^\s<>\"']*)?",
    re.I,
)
EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63})(?![\w.-])", re.I)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d .()\-/]{7,}\d)(?!\w)")
HANDLE_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9._-]{2,64}\b")
ETH_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
BTC_RE = re.compile(r"\b(?:bc1[ac-hj-np-z02-9]{11,87}|[13][1-9A-HJ-NP-Za-km-z]{25,34})\b", re.I)
LTC_RE = re.compile(r"\b(?:ltc1[ac-hj-np-z02-9]{11,87}|[LM][1-9A-HJ-NP-Za-km-z]{26,43})\b", re.I)
TRON_RE = re.compile(r"\bT[1-9A-HJ-NP-Za-km-z]{33}\b")
SOL_RE = re.compile(r"(?<![A-Za-z0-9])[1-9A-HJ-NP-Za-km-z]{32,44}(?![A-Za-z0-9])")

SOCIAL_HOSTS = {
    "instagram.com": "instagram", "www.instagram.com": "instagram",
    "facebook.com": "facebook", "www.facebook.com": "facebook", "m.facebook.com": "facebook",
    "tiktok.com": "tiktok", "www.tiktok.com": "tiktok",
    "x.com": "x", "www.x.com": "x", "twitter.com": "x", "www.twitter.com": "x",
    "t.me": "telegram", "telegram.me": "telegram", "www.telegram.me": "telegram",
    "discord.com": "discord", "www.discord.com": "discord",
    "linkedin.com": "linkedin", "www.linkedin.com": "linkedin",
}

SHORTENERS = {
    "bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "buff.ly", "is.gd", "cutt.ly",
    "rebrand.ly", "shorturl.at", "tiny.cc", "rb.gy", "lnkd.in", "trib.al", "ift.tt",
}

SUSPICIOUS_TLDS = {
    "zip", "mov", "click", "top", "xyz", "work", "support", "help", "live", "buzz", "rest",
    "fit", "cam", "quest", "monster", "beauty", "lol", "mom", "country", "stream",
}

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com", "temp-mail.org",
    "yopmail.com", "throwawaymail.com", "sharklasers.com", "getnada.com", "maildrop.cc",
}

FREE_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com",
    "icloud.com", "proton.me", "protonmail.com", "aol.com", "gmx.com", "gmx.fr", "orange.fr",
}

BRANDS: Dict[str, Tuple[str, ...]] = {
    "paypal": ("paypal.com",),
    "google": ("google.com", "google.fr", "accounts.google.com"),
    "google drive": ("drive.google.com", "google.com"),
    "microsoft": ("microsoft.com", "live.com", "office.com", "outlook.com"),
    "apple": ("apple.com", "icloud.com"),
    "amazon": ("amazon.com", "amazon.fr", "amazon.de", "amazon.co.uk"),
    "netflix": ("netflix.com",),
    "meta": ("meta.com", "facebook.com", "instagram.com"),
    "facebook": ("facebook.com", "meta.com"),
    "instagram": ("instagram.com", "meta.com"),
    "whatsapp": ("whatsapp.com",),
    "tiktok": ("tiktok.com",),
    "x": ("x.com", "twitter.com"),
    "linkedin": ("linkedin.com",),
    "dropbox": ("dropbox.com",),
    "dhl": ("dhl.com", "dhl.fr"),
    "ups": ("ups.com",),
    "fedex": ("fedex.com",),
    "chronopost": ("chronopost.fr",),
    "laposte": ("laposte.fr",),
    "la poste": ("laposte.fr",),
    "banque postale": ("labanquepostale.fr",),
    "revolut": ("revolut.com",),
    "stripe": ("stripe.com",),
    "coinbase": ("coinbase.com",),
    "binance": ("binance.com",),
}
# Expanded first-party domain intelligence. Keep this deterministic: these are
# canonical domains, not reputation claims.
BRANDS.update({
    "ameli": ("ameli.fr",),
    "assurance maladie": ("ameli.fr",),
    "impots": ("impots.gouv.fr",),
    "impots.gouv.fr": ("impots.gouv.fr",),
    "service public": ("service-public.fr",),
    "france travail": ("francetravail.fr",),
    "caf": ("caf.fr",),
    "urssaf": ("urssaf.fr",),
    "edf": ("edf.fr",),
    "engie": ("engie.fr",),
    "orange": ("orange.fr",),
    "sfr": ("sfr.fr",),
    "free": ("free.fr",),
    "bouygues telecom": ("bouyguestelecom.fr",),
    "societe generale": ("societegenerale.fr",),
    "credit agricole": ("credit-agricole.fr",),
    "credit mutuel": ("creditmutuel.fr",),
    "bnp paribas": ("mabanque.bnpparibas", "bnpparibas.com"),
    "boursobank": ("boursobank.com",),
    "n26": ("n26.com",),
    "wise": ("wise.com",),
    "visa": ("visa.com", "visa.fr"),
    "mastercard": ("mastercard.com", "mastercard.fr"),
    "github": ("github.com",),
    "discord": ("discord.com", "discord.gg"),
    "steam": ("steampowered.com", "steamcommunity.com"),
    "booking": ("booking.com",),
    "airbnb": ("airbnb.com", "airbnb.fr"),
    "uber": ("uber.com",),
    "vinted": ("vinted.fr", "vinted.com"),
})

CONFUSABLE_ASCII = str.maketrans({
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t",
})


def brand_key(value: str) -> str:
    value = fold(value).translate(CONFUSABLE_ASCII)
    return re.sub(r"[^a-z0-9]", "", value)


def levenshtein_limited(a: str, b: str, limit: int = 1) -> int:
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
            row_min = min(row_min, cur[-1])
        if row_min > limit:
            return limit + 1
        prev = cur
    return prev[-1]


def detect_brand_lookalike(host: str) -> Optional[Tuple[str, str]]:
    registered = registered_guess(host)
    labels = [x for x in registered.split('.')[:-1] if x]
    if not labels:
        return None
    compact_labels = [brand_key(x) for x in labels]
    for brand, official_domains in BRANDS.items():
        if any(host == d or host.endswith('.' + d) for d in official_domains):
            continue
        key = brand_key(brand)
        # Short/generic brand names (x, free, caf, etc.) are deliberately
        # excluded from fuzzy matching to avoid false positives.
        if len(key) < 5:
            continue
        for label in compact_labels:
            if len(label) < 5:
                continue
            distance = levenshtein_limited(label, key, 1)
            if label == key or distance <= 1:
                return brand, label
    return None

RULES: Sequence[Tuple[str, int, str, Sequence[str]]] = (
    ("credentials", 28, "Requests credentials, codes or account verification", (
        r"\b(password|passcode|mot de passe|contrase(?:n|ñ)a|passwort)\b",
        r"\b(otp|one[- ]?time code|verification code|security code|code de v[ée]rification|code sms|tan)\b",
        r"\b(confirm|verify|validate|secure|unlock|restore).{0,28}\b(account|compte|identity|identit[ée]|login)\b",
        r"\bseed phrase|recovery phrase|private key|phrase de r[ée]cup[ée]ration|cl[ée] priv[ée]e\b",
    )),
    ("payment", 20, "Requests money or a payment action", (
        r"\b(pay|payment|payer|paiement|pago|bezahlen|zahlung|pagamento)\b",
        r"\b(bank transfer|wire transfer|virement|transferencia bancaria|[üu]berweisung|bonifico|deposit|d[ée]p[oô]t|recharge)\b",
        r"\b(gift card|carte cadeau|voucher|coupon).{0,25}\b(code|number|num[ée]ro|photo)\b",
        r"\b(crypto|bitcoin|btc|ethereum|eth|usdt|wallet|portefeuille crypto)\b",
    )),
    ("urgency", 13, "Uses urgency or a short deadline", (
        r"\b(urgent|urgently|imm[ée]diatement|immédiat|immediately|asap|now|maintenant|ahora|sofort|subito)\b",
        r"\b(within|dans les|sous|en)\s+\d{1,2}\s*(minutes?|mins?|hours?|heures?|h)\b",
        r"\b(last chance|derni[èe]re chance|final warning|dernier avertissement|ultima oportunidad)\b",
    )),
    ("threat", 18, "Threatens loss, suspension, penalties or legal consequences", (
        r"\b(account|compte|card|carte|service).{0,25}\b(suspend|suspended|blocked|locked|ferm[ée]|bloqu[ée]|désactiv[ée])\b",
        r"\b(fine|penalty|amende|lawsuit|police|arrest|legal action|poursuites?|tribunal)\b",
        r"\b(delete|close|terminate|supprimer|cl[oô]turer).{0,25}\b(account|compte|data|donn[ée]es)\b",
    )),
    ("delivery", 12, "Claims a parcel/delivery issue and asks for action", (
        r"\b(parcel|package|delivery|colis|livraison|paquete|entrega|paket|consegna)\b.{0,45}\b(held|failed|pending|fee|pay|adresse|address|bloqu[ée]|suspendu)\b",
        r"\b(customs|douane|frais de douane|shipping fee|redelivery|reprogramm)\b",
    )),
    ("support", 16, "Uses tech-support or remote-access language", (
        r"\b(technical support|tech support|support technique|microsoft support|apple support)\b",
        r"\b(anydesk|teamviewer|rustdesk|remote desktop|bureau [àa] distance|remote access)\b",
        r"\b(call|phone|appelez|contact).{0,28}\b(support|technician|technicien|security team)\b",
    )),
    ("investment", 18, "Promises investment returns or trading profits", (
        r"\b(guaranteed|garanti|risk[- ]?free|sans risque).{0,35}\b(return|profit|rendement|gain)\b",
        r"\b(double|triple|doubler|tripler).{0,25}\b(money|argent|investment|investissement|crypto)\b",
        r"\b(trading|forex|investment|investissement).{0,35}\b(signal|mentor|expert|profit|return)\b",
    )),
    ("prize", 15, "Claims a prize, giveaway or unexpected reward", (
        r"\b(winner|won|congratulations|gagn[ée]|f[ée]licitations|prize|prix|lottery|loterie|giveaway)\b",
        r"\b(claim|r[ée]clamer|collect|recevoir).{0,35}\b(prize|reward|prix|gain|cadeau)\b",
    )),
    ("job", 15, "Contains common fake-job/task scam wording", (
        r"\b(job|emploi|travail|work from home|t[ée]l[ée]travail).{0,40}\b(telegram|whatsapp|crypto|commission|daily)\b",
        r"\b(task|t[âa]che).{0,30}\b(commission|recharge|deposit|d[ée]p[oô]t|withdraw|retirer)\b",
    )),
    ("romance", 12, "Contains romance/relationship scam payment language", (
        r"\b(love|amour|ch[ée]ri|baby|darling).{0,60}\b(money|argent|gift card|crypto|ticket|billet)\b",
        r"\b(military|soldier|oil rig|doctor abroad|deployed).{0,60}\b(money|fee|package|inheritance)\b",
    )),
    ("invoice", 13, "Contains invoice or payment-detail change language", (
        r"\b(invoice|facture|payment details|coordonn[ée]es bancaires|bank details|iban)\b",
        r"\b(new|nouveau|changed|modifi[ée]).{0,25}\b(iban|bank account|compte bancaire|payment details)\b",
    )),
    ("impersonation", 14, "Claims authority or identity to pressure the recipient", (
        r"\b(ceo|boss|manager|director|directeur|patron|hr|ressources humaines)\b.{0,55}\b(urgent|gift card|transfer|virement|confidential)\b",
        r"\b(police|government|gouvernement|tax|imp[oô]ts|bank|banque).{0,50}\b(pay|payer|code|verify|v[ée]rifier)\b",
    )),
    ("offplatform", 8, "Pushes the conversation to another platform", (
        r"\b(move|continue|contact|message|write|rejoindre|contactez).{0,25}\b(telegram|whatsapp|signal)\b",
    )),
    ("secrecy", 10, "Requests secrecy or bypassing normal procedures", (
        r"\b(don'?t tell|do not tell|keep this secret|confidential|ne dites pas|secret|discret)\b",
        r"\b(bypass|avoid|contourner).{0,25}\b(process|procedure|security|bank|verification)\b",
    )),
)

SUSPICIOUS_URL_WORDS = re.compile(
    r"(?:login|signin|verify|verification|secure|security|account|wallet|recover|update|billing|invoice|"
    r"password|webscr|auth|unlock|support|parcel|delivery|confirm|bonus|airdrop|claim|gift|crypto)", re.I
)

@dataclass(frozen=True)
class Signal:
    id: str
    severity: str
    weight: int
    title: str
    detail: str
    source: str = "content"


def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)).lower()


def uniq(items: Iterable[str], limit: int = MAX_ENTITIES) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        item = str(item).strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def normalize_url(raw: str) -> Optional[str]:
    raw = raw.strip().rstrip(".,;:!?)]}")
    if not raw:
        return None
    if not re.match(r"^[a-z][a-z0-9+.-]*://", raw, re.I):
        raw = "https://" + raw
    try:
        u = urlsplit(raw)
        if u.scheme.lower() not in {"http", "https"} or not u.hostname:
            return None
        host = u.hostname.encode("idna").decode("ascii").lower().rstrip(".")
        port = f":{u.port}" if u.port and not ((u.scheme == "http" and u.port == 80) or (u.scheme == "https" and u.port == 443)) else ""
        path = u.path or ""
        query = f"?{u.query}" if u.query else ""
        return f"{u.scheme.lower()}://{host}{port}{path}{query}"
    except (ValueError, UnicodeError):
        return None


def extract_urls(text: str, extra: Sequence[str] = ()) -> List[str]:
    candidates: List[str] = list(extra or [])
    candidates += URL_RE.findall(text)
    bare_source = URL_RE.sub(" ", text)
    bare_source = EMAIL_RE.sub(" ", bare_source)
    candidates += BARE_DOMAIN_RE.findall(bare_source)
    out: List[str] = []
    for c in candidates:
        n = normalize_url(c)
        if n:
            out.append(n)
    return uniq(out)


def extract_crypto(text: str) -> List[str]:
    candidates: List[str] = []
    for rx in (ETH_RE, BTC_RE, LTC_RE, TRON_RE):
        candidates.extend(rx.findall(text))
    if re.search(r"\b(sol|solana|wallet|crypto|address|adresse)\b", text, re.I):
        candidates.extend(SOL_RE.findall(text))
    return uniq(candidates)


def _looks_social_profile_path(url: str) -> bool:
    try:
        u = urlsplit(url)
        host = (u.hostname or "").lower()
        parts = [p for p in u.path.split("/") if p]
        if not parts:
            return False
        first = parts[0].lower()
        if "instagram.com" in host:
            return first not in {"p", "reel", "reels", "stories", "explore", "accounts", "direct"}
        if "tiktok.com" in host:
            return first.startswith("@")
        if host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
            return first not in {"home", "explore", "search", "messages", "settings", "i", "intent", "share"}
        if "facebook.com" in host:
            return first not in {"watch", "groups", "marketplace", "gaming", "events", "reel", "reels", "share"}
        if host in {"t.me", "telegram.me", "www.telegram.me"}:
            return first not in {"joinchat", "share", "proxy", "socks"} and not first.startswith("+")
        if "linkedin.com" in host:
            return first in {"in", "company", "school"}
        return host in SOCIAL_HOSTS
    except Exception:
        return False


def detect_type(primary: str, all_text: str, urls: Sequence[str], emails: Sequence[str], cryptos: Sequence[str]) -> str:
    p = primary.strip()
    if p and len(p) <= 80 and HANDLE_RE.fullmatch(p):
        return "social-profile"
    if p and EMAIL_RE.fullmatch(p):
        return "email"
    if p and any(p == c for c in cryptos):
        return "crypto"
    # A browser-uploaded filename plus extracted content is a file/message input,
    # not a bare domain even when the extension is also a valid public TLD.
    if p and len(all_text.strip()) > len(p) and re.fullmatch(
        r"[^/\\\s]+\.(?:pdf|doc|docx|xls|xlsx|csv|txt|rtf|eml|msg|zip|rar|7z|jpg|jpeg|png|webp|gif|heic|svg)",
        p,
        re.I,
    ):
        return "message-url" if urls else ("message-email" if emails else "message")
    if p:
        n = normalize_url(p)
        if n and (p.lower().startswith(("http://", "https://", "www.")) or BARE_DOMAIN_RE.fullmatch(p)):
            try:
                host = urlsplit(n).hostname or ""
                return "social-profile" if host in SOCIAL_HOSTS and _looks_social_profile_path(n) else "url"
            except ValueError:
                pass
    if urls:
        return "message-url"
    if emails:
        return "message-email"
    return "message" if all_text.strip() else "unknown"


def severity_for(weight: int) -> str:
    if weight >= 24:
        return "high"
    if weight >= 14:
        return "medium"
    return "low"


def add_signal(signals: List[Signal], signal: Signal) -> None:
    key = (signal.id, signal.detail.casefold())
    if any((s.id, s.detail.casefold()) == key for s in signals):
        return
    if len(signals) < MAX_SIGNALS:
        signals.append(signal)


def analyze_phrase_rules(text: str, signals: List[Signal]) -> None:
    f = fold(text)
    for rule_id, weight, title, patterns in RULES:
        hits = 0
        evidence = ""
        for pattern in patterns:
            m = re.search(pattern, f, re.I | re.S)
            if m:
                hits += 1
                evidence = m.group(0)[:160]
        if hits:
            effective = min(weight + (hits - 1) * 4, weight + 8)
            add_signal(signals, Signal(rule_id, severity_for(effective), effective, title, evidence or title))


def host_is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def private_or_local_host(host: str) -> bool:
    h = host.lower().rstrip(".")
    if h in {"localhost", "localhost.localdomain"} or h.endswith((".localhost", ".local", ".internal")):
        return True
    try:
        ip = ipaddress.ip_address(h.strip("[]"))
        return bool(ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
    except ValueError:
        return False


def registered_guess(host: str) -> str:
    parts = host.lower().strip(".").split(".")
    if len(parts) <= 2:
        return host.lower().strip(".")
    common_second = {"co.uk", "com.au", "com.br", "co.jp", "co.nz", "com.mx", "co.in"}
    last2 = ".".join(parts[-2:])
    if last2 in common_second and len(parts) >= 3:
        return ".".join(parts[-3:])
    return last2


def looks_random_label(label: str) -> bool:
    if len(label) < 12:
        return False
    digits = sum(c.isdigit() for c in label)
    hyphens = label.count("-")
    vowels = sum(c in "aeiou" for c in label.lower())
    return digits >= 5 or hyphens >= 3 or (len(label) >= 18 and vowels <= 2)


def analyze_url(url: str, full_text: str, signals: List[Signal]) -> Dict[str, Any]:
    result: Dict[str, Any] = {"url": url}
    try:
        u = urlsplit(url)
    except ValueError:
        add_signal(signals, Signal("url_invalid", "medium", 16, "Malformed URL", url, "url"))
        return result
    host = (u.hostname or "").lower().rstrip(".")
    result.update({"host": host, "scheme": u.scheme.lower(), "registeredDomainGuess": registered_guess(host)})
    if u.scheme.lower() == "http":
        add_signal(signals, Signal("url_http", "low", 8, "Connection is not HTTPS", host, "url"))
    if host_is_ip(host):
        add_signal(signals, Signal("url_ip", "medium", 16, "URL uses a raw IP address", host, "url"))
    if private_or_local_host(host):
        add_signal(signals, Signal("url_private", "medium", 16, "URL points to a private/local network", host, "url"))
    if host.startswith("xn--") or ".xn--" in host:
        add_signal(signals, Signal("url_punycode", "medium", 14, "Internationalized/punycode hostname", host, "url"))
    if host in SHORTENERS:
        add_signal(signals, Signal("url_shortener", "low", 9, "Shortened link hides the final destination", host, "url"))
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in SUSPICIOUS_TLDS:
        add_signal(signals, Signal("url_tld", "low", 7, "TLD is frequently seen in disposable or abusive URLs", "." + tld, "url"))
    labels = host.split(".")
    if len(labels) >= 5:
        add_signal(signals, Signal("url_subdomains", "low", 7, "Hostname contains many subdomains", host, "url"))
    if any(looks_random_label(x) for x in labels[:-1]):
        add_signal(signals, Signal("url_random", "low", 8, "Hostname contains an unusual random-looking label", host, "url"))
    decoded = unquote((u.path or "") + ("?" + u.query if u.query else ""))
    if SUSPICIOUS_URL_WORDS.search(decoded):
        add_signal(signals, Signal("url_sensitive_path", "low", 7, "URL path uses login/payment/security language", decoded[:180], "url"))
    if re.search(r"%[0-9a-f]{2}", url, re.I) and len(re.findall(r"%[0-9a-f]{2}", url, re.I)) >= 3:
        add_signal(signals, Signal("url_encoding", "low", 6, "URL contains heavy percent-encoding", url[:180], "url"))
    if len(url) > 180:
        add_signal(signals, Signal("url_long", "low", 5, "Unusually long URL", f"{len(url)} characters", "url"))
    if "@" in u.netloc:
        add_signal(signals, Signal("url_userinfo", "high", 25, "URL contains user-info before the hostname", u.netloc[:180], "url"))
    params = dict(parse_qsl(u.query, keep_blank_values=True))
    if any(k.lower() in {"redirect", "redirect_uri", "url", "target", "dest", "destination", "continue", "return", "next"} for k in params):
        add_signal(signals, Signal("url_redirect_param", "low", 6, "URL contains a redirect/destination parameter", u.query[:180], "url"))
    lookalike = detect_brand_lookalike(host)
    if lookalike:
        brand, matched_label = lookalike
        add_signal(signals, Signal(
            "brand_domain_lookalike", "high", 24,
            f"Domain closely resembles a known brand ({brand})",
            f"Brand: {brand}; domain: {host}; matched label: {matched_label}", "url"
        ))
        result["lookalikeBrand"] = brand
    tf = fold(full_text)
    claimed: List[str] = []
    claim_action_context = bool(re.search(
        r"\b(verify|verification|login|sign in|account|security|secure|payment|pay|payer|parcel|delivery|colis|livraison|unlock|confirm|code|password|mot de passe|invoice|facture)\b",
        tf, re.I
    ))
    for brand, official_domains in BRANDS.items():
        brand_folded = fold(brand)
        if re.search(r"(?<!\w)" + re.escape(brand_folded) + r"(?!\w)", tf):
            claimed.append(brand)
            host_mentions_brand = brand_folded.replace(" ", "") in fold(host).replace("-", "")
            if (claim_action_context or host_mentions_brand) and not any(host == d or host.endswith("." + d) for d in official_domains):
                add_signal(signals, Signal(
                    "brand_domain_mismatch", "medium", 18,
                    f"Claimed brand does not match the link domain ({brand})",
                    f"Claim: {brand}; link: {host}", "url"
                ))
    result["claimedBrands"] = uniq(claimed, 10)
    return result


def analyze_email(email: str, text: str, signals: List[Signal]) -> Dict[str, Any]:
    _, addr = parseaddr(email)
    addr = (addr or email).strip().lower()
    domain = addr.rsplit("@", 1)[-1] if "@" in addr else ""
    result = {"email": addr, "domain": domain}
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        add_signal(signals, Signal("email_disposable", "medium", 18, "Disposable email provider", domain, "email"))
    tf = fold(text)
    for brand, official_domains in BRANDS.items():
        if re.search(r"(?<!\w)" + re.escape(fold(brand)) + r"(?!\w)", tf):
            if domain in FREE_EMAIL_DOMAINS and not any(domain == d or domain.endswith("." + d) for d in official_domains):
                add_signal(signals, Signal(
                    "brand_email_mismatch", "medium", 17,
                    f"Brand claim is sent from a consumer email domain ({brand})",
                    f"Claim: {brand}; sender domain: {domain}", "email"
                ))
            elif domain and not any(domain == d or domain.endswith("." + d) for d in official_domains) and brand in fold(addr):
                add_signal(signals, Signal(
                    "brand_email_lookalike", "medium", 18,
                    f"Sender domain resembles a brand but is not a known official domain ({brand})",
                    domain, "email"
                ))
    return result


def score_breakdown(signals: Sequence[Signal]) -> Dict[str, int]:
    groups = {
        "identity": {"brand_domain_mismatch", "brand_domain_lookalike", "brand_email_mismatch", "brand_email_lookalike", "email_disposable"},
        "requestedAction": {"credentials", "payment", "crypto_context"},
        "pressure": {"urgency", "threat", "secrecy"},
        "scenario": {"delivery", "support", "investment", "prize", "job", "romance", "invoice", "impersonation", "offplatform"},
        "technicalUrl": {"url_http", "url_ip", "url_private", "url_punycode", "url_shortener", "url_tld", "url_subdomains", "url_random", "url_sensitive_path", "url_encoding", "url_long", "url_userinfo", "url_redirect_param", "many_links"},
    }
    out: Dict[str, int] = {}
    for name, ids in groups.items():
        vals = sorted((s.weight for s in signals if s.id in ids), reverse=True)
        if not vals:
            out[name] = 0
        elif name == "technicalUrl" and len(vals) > 1:
            out[name] = int(round(vals[0] + vals[1] * 0.35))
        else:
            out[name] = vals[0]
    return out


def score_breakdown(signals: Sequence[Signal]) -> Dict[str, int]:
    groups = {
        "identity": {"brand_domain_mismatch", "brand_domain_lookalike", "brand_email_mismatch", "brand_email_lookalike", "email_disposable"},
        "requestedAction": {"credentials", "payment", "crypto_context"},
        "pressure": {"urgency", "threat", "secrecy"},
        "scenario": {"delivery", "support", "investment", "prize", "job", "romance", "invoice", "impersonation", "offplatform"},
        "technicalUrl": {"url_http", "url_ip", "url_private", "url_punycode", "url_shortener", "url_tld", "url_subdomains", "url_random", "url_sensitive_path", "url_encoding", "url_long", "url_userinfo", "url_redirect_param", "many_links"},
    }
    out: Dict[str, int] = {}
    for name, ids in groups.items():
        vals = sorted((s.weight for s in signals if s.id in ids), reverse=True)
        if not vals:
            out[name] = 0
        elif name == "technicalUrl" and len(vals) > 1:
            out[name] = int(round(vals[0] + vals[1] * 0.35))
        else:
            out[name] = vals[0]
    return out


def combined_risk(signals: Sequence[Signal], text: str) -> Tuple[int, str]:
    breakdown = score_breakdown(signals)
    # Evidence families are capped by taking their strongest signal. This keeps
    # repeated wording from artificially inflating risk while rewarding
    # independent evidence from identity, requested action, pressure, scenario
    # and URL structure.
    score = sum(breakdown.values())
    ids = {s.id for s in signals}

    if ids & {"credentials", "payment"} and ids & {"urgency", "threat", "brand_domain_mismatch", "brand_domain_lookalike", "url_shortener", "url_userinfo"}:
        score += 8
    if "credentials" in ids and ids & {"brand_domain_mismatch", "brand_domain_lookalike", "brand_email_mismatch", "brand_email_lookalike"}:
        score += 10
    if "payment" in ids and ids & {"crypto_context", "investment", "prize", "job", "romance"}:
        score += 8
    if "payment" in ids and ids & {"brand_domain_mismatch", "brand_domain_lookalike"}:
        score += 10
    if "job" in ids and "offplatform" in ids and "payment" in ids:
        score += 12
    if "credentials" in ids and "support" in ids:
        score += 8

    score = int(round(clamp(score, 0, 100)))
    if not text.strip():
        return score, "unknown"
    if score >= 60:
        return score, "high"
    if score >= 25:
        return score, "caution"
    return score, "low"

def make_summary(risk: str, signals: Sequence[Signal]) -> str:
    if risk == "unknown":
        return "Not enough analyzable evidence was provided to reach a useful risk assessment."
    top = sorted(signals, key=lambda s: s.weight, reverse=True)[:3]
    if risk == "high":
        lead = "Multiple high-risk scam or phishing indicators were found."
    elif risk == "caution":
        lead = "Suspicious indicators were found and the content should be verified independently."
    else:
        lead = "No strong scam indicators were found in the evidence this scanner can inspect."
    if top:
        return lead + " Main signals: " + "; ".join(s.title for s in top) + "."
    return lead


def recommended_action(risk: str, detected_type: str) -> str:
    if risk == "high":
        return "Do not click, sign in, pay, send codes, install software or reply. Verify the sender or service through an official channel you open independently."
    if risk == "caution":
        return "Verify the sender and destination independently before continuing. Do not provide credentials, codes or payment details until verified."
    if risk == "low":
        if detected_type in {"url", "message-url"}:
            return "No strong warning was detected, but this is not a guarantee of safety. Confirm the domain and expected context before opening or signing in."
        return "No strong warning was detected, but automated checks cannot prove legitimacy. Confirm unexpected requests independently."
    return "Provide the full text, URL, sender address, QR destination or OCR text for a more complete check."


def confidence_score(detected_type: str, text: str, urls: Sequence[str], signals: Sequence[Signal], extras: Dict[str, Any]) -> float:
    c = 0.32
    if detected_type != "unknown": c += 0.12
    if len(text) >= 30: c += 0.10
    if len(text) >= 120: c += 0.08
    if urls: c += 0.10
    if signals: c += 0.08
    if extras.get("extractedText"): c += 0.06
    if extras.get("qrValues"): c += 0.06
    return round(clamp(c, 0.2, 0.92), 2)


def scan(payload: Dict[str, Any]) -> Dict[str, Any]:
    primary = str(payload.get("input") or payload.get("url") or payload.get("email") or payload.get("address") or payload.get("message") or "")
    context = str(payload.get("context") or "")
    extracted = str(payload.get("extractedText") or payload.get("ocrText") or "")
    qr_values = payload.get("qrValues") or payload.get("qr_values") or []
    if not isinstance(qr_values, list):
        qr_values = []
    qr_values = [str(v)[:3000] for v in qr_values[:10]]
    all_text = "\n".join(x for x in (primary, context, extracted, *qr_values) if x)[:MAX_INPUT_CHARS]
    emails = uniq(EMAIL_RE.findall(all_text))
    phones = uniq(m.group(0).strip() for m in PHONE_RE.finditer(all_text))
    handles = uniq(HANDLE_RE.findall(all_text))
    cryptos = extract_crypto(all_text)
    url_text = all_text
    # When extracted file content is present, a plain filename such as
    # "invoice.pdf" is context, not a bare web domain. Keep URLs found in
    # extracted text and QR values while excluding the filename itself.
    if extracted and primary and re.fullmatch(r"[^/\\\s]+\.(?:pdf|doc|docx|xls|xlsx|csv|txt|rtf|eml|msg|zip|rar|7z|jpg|jpeg|png|webp|gif|heic|svg)", primary.strip(), re.I):
        url_text = "\n".join(x for x in (context, extracted, *qr_values) if x)[:MAX_INPUT_CHARS]
    urls = extract_urls(url_text, [v for v in qr_values if str(v).lower().startswith(("http://", "https://"))])
    detected_type = detect_type(primary, all_text, urls, emails, cryptos)
    signals: List[Signal] = []
    analyze_phrase_rules(all_text, signals)
    url_details = [analyze_url(u, all_text, signals) for u in urls[:8]]
    email_details = [analyze_email(e, all_text, signals) for e in emails[:8]]
    if cryptos and re.search(r"\b(send|pay|transfer|deposit|payer|envoyer|virement|d[ée]p[oô]t|wallet|crypto|bitcoin|usdt)\b", fold(all_text)):
        add_signal(signals, Signal("crypto_context", "medium", 17, "Crypto address appears in a payment/transfer context", cryptos[0], "crypto"))
    if len(urls) >= 3:
        add_signal(signals, Signal("many_links", "low", 5, "Message contains multiple links", str(len(urls)), "content"))
    score, risk = combined_risk(signals, all_text)
    extras = {"extractedText": extracted, "qrValues": qr_values}
    confidence = confidence_score(detected_type, all_text, urls, signals, extras)
    sorted_signals = sorted(signals, key=lambda s: s.weight, reverse=True)
    categories = uniq((s.id for s in sorted_signals), 12)
    social_profile: Optional[Dict[str, Any]] = None
    for u in urls:
        try:
            host = (urlsplit(u).hostname or "").lower()
            if host in SOCIAL_HOSTS and _looks_social_profile_path(u):
                social_profile = {"platform": SOCIAL_HOSTS[host], "url": u}
                break
        except Exception:
            pass
    if not social_profile and primary.strip().startswith("@"):
        social_profile = {"platform": "unknown", "username": primary.strip()[:80]}
    return {
        "ok": True,
        "engine": {"name": "cist-python-rules", "version": VERSION, "aiRequired": False},
        "detectedType": detected_type,
        "risk": risk,
        "score": score,
        "confidence": confidence,
        "confidenceMeaning": "coverage of analyzable evidence, not a probability of safety",
        "summary": make_summary(risk, sorted_signals),
        "recommendedAction": recommended_action(risk, detected_type),
        "entities": {
            "urls": urls, "emails": emails, "phones": phones,
            "socialHandles": handles, "cryptoAddresses": cryptos, "qrValues": uniq(qr_values, 10),
        },
        "socialProfile": social_profile,
        "signals": [asdict(s) for s in sorted_signals],
        "categories": categories,
        "technical": {
            "inputCharacters": len(all_text),
            "scoreBreakdown": score_breakdown(signals),
            "urlDetails": url_details,
            "emailDetails": email_details,
            "limitations": [
                "Deterministic rules cannot prove that content is legitimate or malicious.",
                "This endpoint does not open arbitrary URLs or execute downloaded content.",
                "Image understanding depends on OCR/QR data supplied by the client; there is no vision model in this engine.",
                "Domain reputation, malware feeds and live account metadata require separate evidence providers.",
            ],
        },
    }


class handler(BaseHTTPRequestHandler):
    def _json(self, status: int, body: Dict[str, Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:
        self._json(200, {"ok": True, "engine": "cist-python-rules", "version": VERSION,
                         "usage": "POST JSON with input and optional context/extractedText/qrValues"})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            return self._json(400, {"ok": False, "error": "Invalid Content-Length"})
        if length <= 0:
            return self._json(400, {"ok": False, "error": "JSON body required"})
        if length > 256_000:
            return self._json(413, {"ok": False, "error": "Request too large"})
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._json(400, {"ok": False, "error": "Invalid JSON"})
        if not isinstance(body, dict):
            return self._json(400, {"ok": False, "error": "JSON object required"})
        try:
            result = scan(body)
        except Exception as exc:
            print(f"python_scan error: {type(exc).__name__}: {exc}", file=sys.stderr)
            return self._json(500, {"ok": False, "error": "Analysis failed"})
        self._json(200, result)


def _cli(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        print("Usage: python python-scan.py 'text or URL'", file=sys.stderr)
        return 2
    result = scan({"input": " ".join(argv[1:])})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv))
