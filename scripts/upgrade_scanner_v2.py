#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('api/python_scan.py')
s = path.read_text(encoding='utf-8')

s = s.replace('VERSION = "1.0.0"', 'VERSION = "1.1.0"')

brand_block = r'''
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
'''

marker = '}\n\nRULES: Sequence[Tuple[str, int, str, Sequence[str]]] = ('
if 'CONFUSABLE_ASCII' not in s:
    if marker not in s:
        raise SystemExit('BRANDS marker not found')
    s = s.replace(marker, '}' + brand_block + '\nRULES: Sequence[Tuple[str, int, str, Sequence[str]]] = (', 1)

lookalike_inject = '''    lookalike = detect_brand_lookalike(host)\n    if lookalike:\n        brand, matched_label = lookalike\n        add_signal(signals, Signal(\n            "brand_domain_lookalike", "high", 24,\n            f"Domain closely resembles a known brand ({brand})",\n            f"Brand: {brand}; domain: {host}; matched label: {matched_label}", "url"\n        ))\n        result["lookalikeBrand"] = brand\n'''
needle = '    tf = fold(full_text)\n    claimed: List[str] = []\n'
if 'lookalike = detect_brand_lookalike(host)' not in s:
    if needle not in s:
        raise SystemExit('analyze_url marker not found')
    s = s.replace(needle, lookalike_inject + needle, 1)

new_combined = r'''def score_breakdown(signals: Sequence[Signal]) -> Dict[str, int]:
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
'''

pattern = re.compile(r'def combined_risk\(signals: Sequence\[Signal\], text: str\) -> Tuple\[int, str\]:.*?(?=\ndef make_summary)', re.S)
if not pattern.search(s):
    raise SystemExit('combined_risk block not found')
s = pattern.sub(new_combined.rstrip() + '\n', s, count=1)

tech_needle = '            "inputCharacters": len(all_text),\n            "urlDetails": url_details,\n'
tech_repl = '            "inputCharacters": len(all_text),\n            "scoreBreakdown": score_breakdown(signals),\n            "urlDetails": url_details,\n'
if '"scoreBreakdown": score_breakdown(signals)' not in s:
    if tech_needle not in s:
        raise SystemExit('technical output marker not found')
    s = s.replace(tech_needle, tech_repl, 1)

path.write_text(s, encoding='utf-8')
print('scanner upgraded to v1.1.0')
