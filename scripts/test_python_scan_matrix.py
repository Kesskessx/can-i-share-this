#!/usr/bin/env python3
# Regression matrix for all scanner input types.
# Trigger after scanner v1.1 scoring and brand-intelligence upgrade.
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "api" / "python_scan.py"
spec = importlib.util.spec_from_file_location("python_scan", MODULE)
scanner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = scanner
spec.loader.exec_module(scanner)


def run(name, payload, check):
    result = scanner.scan(payload)
    check(result)
    print(json.dumps({
        "case": name,
        "detectedType": result.get("detectedType"),
        "risk": result.get("risk"),
        "score": result.get("score"),
        "confidence": result.get("confidence"),
        "categories": result.get("categories", []),
    }, ensure_ascii=False))


def require(cond, message):
    if not cond:
        raise AssertionError(message)


run("benign_url", {"input": "https://example.com/about"}, lambda r: (
    require(r["detectedType"] == "url", r),
    require(r["risk"] == "low", r),
    require(r["score"] < 25, r),
))

run("phishing_url", {
    "input": "https://paypal-login-security.xyz/verify-account",
    "context": "PayPal security: verify your account password immediately or your account will be suspended."
}, lambda r: (
    require(r["detectedType"] == "url", r),
    require(r["risk"] == "high", r),
    require(r["score"] >= 60, r),
    require("brand_domain_mismatch" in r["categories"], r),
))

run("official_email", {"input": "support@paypal.com"}, lambda r: (
    require(r["detectedType"] == "email", r),
    require(r["risk"] == "low", r),
))

run("email_impersonation", {
    "input": "paypal-security@gmail.com",
    "context": "PayPal: verify your account and security code now."
}, lambda r: (
    require(r["detectedType"] == "email", r),
    require(r["risk"] in {"caution", "high"}, r),
    require("brand_email_mismatch" in r["categories"], r),
))

run("parcel_message", {
    "input": "DHL: votre colis est bloqué. Payez 1,99 € immédiatement ici: https://dhl-delivery-pay.xyz/parcel"
}, lambda r: (
    require(r["detectedType"] == "message-url", r),
    require(r["risk"] == "high", r),
    require(r["score"] >= 60, r),
))

run("social_profile_url", {"input": "https://instagram.com/example_profile"}, lambda r: (
    require(r["detectedType"] == "social-profile", r),
    require(r.get("socialProfile", {}).get("platform") == "instagram", r),
))

run("social_handle", {"input": "@example_profile"}, lambda r: (
    require(r["detectedType"] == "social-profile", r),
    require(r.get("socialProfile", {}).get("username") == "@example_profile", r),
))

run("qr_image", {
    "input": "",
    "extractedText": "DHL parcel held. Pay now to schedule redelivery.",
    "qrValues": ["https://dhl-redelivery-pay.xyz/confirm"]
}, lambda r: (
    require(r["detectedType"] == "message-url", r),
    require(r["entities"]["qrValues"], r),
    require(r["risk"] in {"caution", "high"}, r),
))

run("ocr_image", {
    "input": "",
    "extractedText": "Microsoft technical support: install AnyDesk immediately and send the security code."
}, lambda r: (
    require(r["detectedType"] == "message", r),
    require(r["risk"] in {"caution", "high"}, r),
    require("support" in r["categories"], r),
))

run("file_extracted_text", {
    "input": "invoice.pdf",
    "extractedText": "Invoice update: our bank details changed. Please use the new IBAN and pay today."
}, lambda r: (
    require(r["detectedType"] == "message", r),
    require(r["risk"] in {"caution", "high"}, r),
    require("invoice" in r["categories"], r),
))

run("crypto_payment", {
    "input": "0x1111111111111111111111111111111111111111",
    "context": "Send crypto payment to this wallet now."
}, lambda r: (
    require(r["detectedType"] == "crypto", r),
    require(r["entities"]["cryptoAddresses"], r),
    require(r["risk"] in {"caution", "high"}, r),
    require("crypto_context" in r["categories"], r),
))

run("phone_extraction", {
    "input": "Call support now at +33 6 12 34 56 78 and send your verification code."
}, lambda r: (
    require(r["detectedType"] == "message", r),
    require(r["entities"]["phones"], r),
    require(r["risk"] in {"caution", "high"}, r),
))

run("empty", {"input": ""}, lambda r: (
    require(r["detectedType"] == "unknown", r),
    require(r["risk"] == "unknown", r),
))

print("ALL PYTHON SCANNER FORMAT TESTS PASSED")
