#!/usr/bin/env python3
from pathlib import Path

path = Path('api/python_scan.py')
s = path.read_text(encoding='utf-8')

# 1) Keep the scanner patch idempotent: only add missing rules.
repls = [
(
'''        r"\\bseed phrase|recovery phrase|private key|phrase de r[ée]cup[ée]ration|cl[ée] priv[ée]e\\b",\n''',
'''        r"\\bseed phrase|recovery phrase|private key|phrase de r[ée]cup[ée]ration|cl[ée] priv[ée]e\\b",\n        r"\\b(enter|provide|confirm|send|share|verify|saisir|fournir|confirmer|envoyer|partager).{0,35}\\b(card|bank|banking|carte|bancaire).{0,20}\\b(details|information|credentials|code|number|coordonn[ée]es|num[ée]ro)\\b",\n'''
),
(
'''        r"\\b(crypto|bitcoin|btc|ethereum|eth|usdt|wallet|portefeuille crypto)\\b",\n''',
'''        r"\\b(crypto|bitcoin|btc|ethereum|eth|usdt|wallet|portefeuille crypto)\\b",\n        r"\\b(send|pay|transfer|envoyer|payer|virer).{0,30}\\b(money|funds?|crypto|usdt|fee|deposit|argent|fonds|frais|acompte|virement)\\b",\n        r"\\b(activation|registration|processing|release|delivery|redelivery).{0,20}\\b(fee|deposit)\\b",\n'''
),
(
'''        r"\\b(guaranteed|garanti|risk[- ]?free|sans risque).{0,35}\\b(return|profit|rendement|gain)\\b",\n''',
'''        r"\\b(guaranteed|garanti|risk[- ]?free|sans risque).{0,35}\\b(return|returns|profit|profits|rendement|rendements|gain|gains)\\b",\n        r"\\b(crypto|bitcoin|btc|ethereum|eth|usdt).{0,35}\\b(return|returns|profit|profits|rendement|rendements|gain|gains)\\b",\n'''
),
(
'''        port = f":{u.port}" if u.port and not ((u.scheme == "http" and u.port == 80) or (u.scheme == "https" and u.port == 443)) else ""\n        path = u.path or ""\n        query = f"?{u.query}" if u.query else ""\n        return f"{u.scheme.lower()}://{host}{port}{path}{query}"\n''',
'''        port = f":{u.port}" if u.port and not ((u.scheme == "http" and u.port == 80) or (u.scheme == "https" and u.port == 443)) else ""\n        # Preserve the fact that user-info existed so analyze_url can flag the\n        # deceptive user@host pattern, but redact the original value/password.\n        userinfo = "user@" if u.username is not None else ""\n        path = u.path or ""\n        query = f"?{u.query}" if u.query else ""\n        return f"{u.scheme.lower()}://{userinfo}{host}{port}{path}{query}"\n'''
),
]

for old, new in repls:
    if new in s:
        continue
    if old in s:
        s = s.replace(old, new, 1)

# 2) Remove accidental duplicate score_breakdown() definitions.
marker = 'def score_breakdown(signals: Sequence[Signal]) -> Dict[str, int]:'
positions = []
start = 0
while True:
    idx = s.find(marker, start)
    if idx < 0:
        break
    positions.append(idx)
    start = idx + len(marker)
if len(positions) > 1:
    # Keep the last definition and remove earlier copies, including surrounding blank lines.
    s = s[:positions[0]] + s[positions[-1]:]

# 3) Reward independent social-engineering evidence without making ordinary
# social links risky on their own.
anchor = '''    if "credentials" in ids and "support" in ids:\n        score += 8\n\n    score = int(round(clamp(score, 0, 100)))\n'''
replacement = '''    if "credentials" in ids and "support" in ids:\n        score += 8\n\n    social_scenarios = {"prize", "job", "romance", "investment", "support", "impersonation", "invoice"}\n    if "offplatform" in ids and ids & social_scenarios:\n        score += 8\n    if "offplatform" in ids and ids & {"payment", "credentials", "urgency", "secrecy"}:\n        score += 6\n    if ids & social_scenarios and ids & {"payment", "credentials"} and ids & {"urgency", "secrecy", "threat"}:\n        score += 6\n\n    score = int(round(clamp(score, 0, 100)))\n'''
if replacement not in s and anchor in s:
    s = s.replace(anchor, replacement, 1)

# 4) Bump engine version once the hardened scoring is present.
if 'social_scenarios = {' in s:
    s = s.replace('VERSION = "1.1.0"', 'VERSION = "1.1.1"', 1)

path.write_text(s, encoding='utf-8')
print('Applied/verified adversarial gap fixes')
