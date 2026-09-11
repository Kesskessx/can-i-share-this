#!/usr/bin/env python3
"""Deterministic adversarial/regression suite for the local Python scanner.

These are synthetic fixtures designed to exercise families of scam signals.
They are not a real-world benchmark or a claim about prevalence.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "api" / "python_scan.py"
spec = importlib.util.spec_from_file_location("python_scan", MODULE)
scanner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = scanner
spec.loader.exec_module(scanner)

passed = 0
failed = []


def check(name, payload, predicate, expectation):
    global passed
    result = scanner.scan(payload)
    try:
        assert predicate(result), expectation
        passed += 1
    except Exception as exc:
        failed.append((name, str(exc), result))


# 1) BENIGN/OFFICIAL: known first-party domains must not be reported as
# brand-domain mismatch/lookalike when the claimed brand matches the host.
official = [
    ("paypal", "paypal.com"), ("google", "google.com"),
    ("microsoft", "microsoft.com"), ("apple", "apple.com"),
    ("amazon", "amazon.com"), ("netflix", "netflix.com"),
    ("facebook", "facebook.com"), ("instagram", "instagram.com"),
    ("whatsapp", "whatsapp.com"), ("tiktok", "tiktok.com"),
    ("linkedin", "linkedin.com"), ("dropbox", "dropbox.com"),
    ("dhl", "dhl.com"), ("ups", "ups.com"), ("fedex", "fedex.com"),
    ("chronopost", "chronopost.fr"), ("la poste", "laposte.fr"),
    ("ameli", "ameli.fr"), ("urssaf", "urssaf.fr"),
    ("france travail", "francetravail.fr"), ("edf", "edf.fr"),
    ("engie", "engie.fr"), ("orange", "orange.fr"),
    ("societe generale", "societegenerale.fr"),
    ("credit agricole", "credit-agricole.fr"),
    ("credit mutuel", "creditmutuel.fr"),
    ("boursobank", "boursobank.com"), ("revolut", "revolut.com"),
    ("github", "github.com"), ("vinted", "vinted.fr"),
]

for brand, domain in official:
    check(
        f"official_{brand}_{domain}",
        {"input": f"https://{domain}/help", "context": f"Official {brand} help page"},
        lambda r: r["risk"] == "low"
        and "brand_domain_mismatch" not in r["categories"]
        and "brand_domain_lookalike" not in r["categories"],
        "official brand domain should remain low risk without identity mismatch",
    )

benign_messages = [
    "Meeting moved to 14:00 tomorrow. See you there.",
    "Merci pour votre commande, votre facture est disponible dans votre espace client habituel.",
    "Your package arrived and is available at the reception desk.",
    "Can you send me the photos from yesterday when you have time?",
    "The project review is scheduled for Friday morning.",
    "Votre rendez-vous a bien été confirmé pour mardi à 10h.",
    "Please review the attached draft before our meeting next week.",
    "Le restaurant confirme votre réservation pour deux personnes.",
    "Your password was changed successfully from account settings.",
    "Here are the notes from today's call. No action is required.",
    "La livraison est prévue entre 9h et 12h demain.",
    "Thanks for your payment. The receipt is available in your account.",
    "Your monthly statement is ready in the mobile banking application.",
    "Je serai en retard de dix minutes, désolé.",
    "The invoice was approved by accounting and is already paid.",
    "Votre colis a été remis au gardien de l'immeuble.",
    "Please use the normal company portal for your timesheet this week.",
    "The support ticket has been closed after your confirmation.",
    "Your booking is confirmed; no additional payment is required.",
    "Merci, le virement a bien été reçu hier.",
]
for i, text in enumerate(benign_messages, 1):
    check(
        f"benign_message_{i:02d}",
        {"input": text},
        lambda r: r["risk"] in {"low", "caution"} and r["score"] < 60,
        "ordinary benign text must not become high risk",
    )

# 2) BRAND LOOKALIKE: typo/homoglyph-style labels must be recognized.
lookalikes = [
    ("paypal", "paypa1.com"),
    ("microsoft", "micros0ft.com"),
    ("amazon", "amaz0n.com"),
    ("netflix", "netf1ix.com"),
    ("facebook", "facebo0k.com"),
    ("instagram", "instagran.com"),
    ("linkedin", "linkedinn.com"),
    ("revolut", "revo1ut.com"),
    ("ameli", "amell.fr"),
    ("urssaf", "urssat.fr"),
    ("vinted", "vintedd.com"),
    ("booking", "booklng.com"),
    ("airbnb", "airbnnb.com"),
    ("github", "githvb.com"),
    ("discord", "discorb.com"),
    ("coinbase", "coinbas3.com"),
    ("binance", "binanc3.com"),
    ("dropbox", "dropb0x.com"),
    ("chronopost", "chronop0st.fr"),
    ("boursobank", "bours0bank.com"),
]
for brand, domain in lookalikes:
    check(
        f"lookalike_{brand}_{domain}",
        {"input": f"https://{domain}/login"},
        lambda r: "brand_domain_lookalike" in r["categories"],
        "near-brand domain should emit brand_domain_lookalike",
    )

# 3) STRONG PHISHING: independent evidence families should combine into high risk.
phish_brands = [
    ("PayPal", "paypal-account-check.xyz"),
    ("Microsoft", "microsoft-security-check.top"),
    ("Apple", "apple-id-confirm.click"),
    ("Amazon", "amazon-order-security.xyz"),
    ("Netflix", "netflix-billing-check.top"),
    ("Instagram", "instagram-account-verify.click"),
    ("Facebook", "facebook-security-review.xyz"),
    ("LinkedIn", "linkedin-profile-confirm.top"),
    ("Dropbox", "dropbox-document-login.click"),
    ("Revolut", "revolut-account-review.xyz"),
    ("Ameli", "ameli-remboursement-check.top"),
    ("La Poste", "laposte-colis-confirm.click"),
    ("DHL", "dhl-redelivery-payment.xyz"),
    ("Chronopost", "chronopost-delivery-fee.top"),
    ("Boursobank", "boursobank-secure-login.click"),
    ("Credit Agricole", "credit-agricole-verification.xyz"),
    ("Societe Generale", "societegenerale-alert.top"),
    ("Vinted", "vinted-payment-confirm.click"),
    ("Coinbase", "coinbase-wallet-verify.xyz"),
    ("Binance", "binance-security-check.top"),
]

for brand, domain in phish_brands:
    for variant in (1, 2):
        if variant == 1:
            text = (
                f"{brand} security alert: verify your password and security code immediately "
                f"or your account will be suspended: https://{domain}/login"
            )
        else:
            text = (
                f"Urgent {brand} notice. Confirm your account credentials now to avoid account closure. "
                f"Use https://{domain}/verify-account"
            )
        check(
            f"phish_{brand}_{variant}",
            {"input": text},
            lambda r: r["risk"] == "high" and r["score"] >= 60,
            "multi-signal credential phishing should be high risk",
        )

# 4) SCAM SCENARIOS: varied social-engineering patterns.
scenarios = [
    "DHL: parcel held. Pay the redelivery fee immediately at https://dhl-fee-now.xyz/pay",
    "La Poste: votre colis est bloqué. Payez 1,99 EUR maintenant: https://laposte-colis.top/pay",
    "Microsoft support: install AnyDesk now and send us your verification code.",
    "Apple support: share the one-time code immediately so we can secure your account.",
    "Guaranteed crypto returns: send USDT today to unlock 300% profit.",
    "Investment opportunity with guaranteed returns. Deposit crypto now before the offer expires.",
    "Congratulations, you won a prize. Pay a small processing fee to receive it today.",
    "You have won the lottery. Send the transfer fee immediately to release your winnings.",
    "Remote job available. Contact us on Telegram and pay a registration deposit before starting.",
    "Work from home task job. Message us on WhatsApp and send the activation fee today.",
    "Invoice update: our bank details changed. Use the new IBAN and pay this invoice today.",
    "Supplier notice: new bank account for this invoice. Please transfer funds urgently.",
    "Hey love, I am stranded abroad. Please send money urgently and keep this between us.",
    "I need help with an emergency. Send a money transfer today and don't tell anyone.",
    "Bank fraud team: provide your OTP and PIN now to stop an unauthorized payment.",
    "Security department: confirm your password and verification code immediately.",
    "Your account is suspended. Confirm your login now at https://account-restore-now.xyz/login",
    "Final warning: your mailbox will be closed unless you verify your password today.",
    "Refund pending. Enter your card details now to receive the money: https://refund-fast.top/card",
    "Tax refund waiting. Confirm your banking details immediately at https://tax-refund-check.xyz/login",
]
for i, text in enumerate(scenarios, 1):
    check(
        f"scenario_{i:02d}",
        {"input": text},
        lambda r: r["risk"] in {"caution", "high"} and r["score"] >= 25,
        "known scam scenario should not remain low risk",
    )

# 5) URL TECHNICAL ANOMALIES: assert the relevant deterministic signal exists.
url_cases = [
    ("http", "http://example.com/login", "url_http"),
    ("raw_ip", "https://203.0.113.10/login", "url_ip"),
    ("private_ip", "http://192.168.1.12/login", "url_private"),
    ("punycode", "https://xn--pple-43d.com/login", "url_punycode"),
    ("short_bitly", "https://bit.ly/example", "url_shortener"),
    ("short_tinyurl", "https://tinyurl.com/example", "url_shortener"),
    ("suspicious_tld", "https://secure-account-check.xyz/login", "url_tld"),
    ("many_subdomains", "https://a.b.c.d.e.example.com/login", "url_subdomains"),
    ("sensitive_path", "https://example.com/verify-account/login", "url_sensitive_path"),
    ("userinfo", "https://paypal.com@example.net/login", "url_userinfo"),
    ("redirect_param", "https://example.com/?redirect=https%3A%2F%2Fevil.test", "url_redirect_param"),
    ("encoded", "https://example.com/%76%65%72%69%66%79", "url_encoding"),
]
for name, url, category in url_cases:
    check(
        f"url_{name}",
        {"input": url},
        lambda r, category=category: category in r["categories"],
        f"URL should emit {category}",
    )

TOTAL = passed + len(failed)
print(f"ADVERSARIAL SCANNER TESTS: {passed}/{TOTAL} passed")
if failed:
    print("FAILURES:")
    for name, error, result in failed:
        print(f"- {name}: {error}; risk={result.get('risk')} score={result.get('score')} categories={result.get('categories')}")
    raise SystemExit(1)

assert TOTAL >= 120, f"suite unexpectedly small: {TOTAL}"
print("ALL ADVERSARIAL SCANNER TESTS PASSED")
