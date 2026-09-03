#!/usr/bin/env python3
"""Generate a focused 10-page anti-scam/link-safety SEO cluster.

Each page targets a distinct search intent and links back to the main scanner plus
other relevant guides. The generator also exposes the cluster from the existing
Safe Link Checker hub and updates the sitemap.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"

PAGES = [
    {
        "path": "/malware-link-checker",
        "keyword": "malware link checker",
        "title": "Malware Link Checker — Check a URL Before You Open It",
        "description": "Check a suspicious URL for malware-download warning signs, dangerous redirects, deceptive domains and other link risks before you open it.",
        "h1": "Malware Link Checker: Check a URL Before You Open It",
        "kicker": "Malware links",
        "quick": "Paste the URL into the main checker before visiting it. We inspect observable warning signs such as risky download extensions, deceptive hostnames, redirects and destination changes. A clean result is not a guarantee that a page or file is malware-free.",
        "sections": [
            ("What a malware link can do", [
                "A malicious link can lead to a fake login page, a drive-by download, an executable file, a booby-trapped archive, or a compromised website that redirects visitors elsewhere. The danger is not always visible in the message that carried the link.",
                "Some malicious pages are short-lived or targeted to a specific device, country or browser. That is why a URL safety check should be treated as one layer of protection rather than a certificate that a destination is safe."
            ]),
            ("What the checker can detect before you click", [
                "Can I Share This? checks URL and destination signals including direct executable or archive downloads, shortened links, unusual domain shapes, punycode, direct IP-address destinations, suspicious account or payment wording, redirect chains and changes to the final hostname.",
                "The optional reputation check can also consult configured threat-intelligence sources for known malicious URLs. New threats may not appear in reputation databases immediately, so the result always distinguishes known reputation from structural warning signs."
            ]),
            ("How to handle a suspicious download link", [
                "Do not run an unexpected file simply because the link uses HTTPS or came from a known contact. Accounts can be compromised, and legitimate cloud-storage services can host malicious files.",
                "If the message claims to provide an invoice, update, security tool, delivery document or shared file, verify the sender independently. Prefer the vendor's official app or website when downloading software."
            ]),
            ("A low-risk result is not a virus scan", [
                "The checker evaluates the link and destination signals that are available to it. It does not execute every downloaded file in a malware sandbox and cannot rule out a previously unknown exploit.",
                "Keep your browser and operating system updated, use built-in endpoint protection, and do not bypass browser or antivirus warnings because another tool returned a low-risk result."
            ]),
        ],
        "faqs": [
            ("Can a link install malware just by opening it?", "Modern browsers reduce this risk, but malicious pages can still exploit vulnerabilities, trick you into downloading a file, or steal credentials. Treat unexpected links cautiously."),
            ("Does HTTPS mean a download is safe?", "No. HTTPS encrypts the connection to a domain. It does not verify that the file or website is legitimate or malware-free."),
            ("Can a PDF or ZIP link be dangerous?", "Yes. Documents and archives can contain malicious content or files. Unexpected downloads deserve extra scrutiny."),
            ("Is this a replacement for antivirus software?", "No. A link checker and endpoint security protect against different parts of the problem and should be used together."),
        ],
        "related": [
            ("/can-a-link-give-you-a-virus", "Can a link give you a virus?", "Understand what can happen after opening a malicious URL."),
            ("/how-to-check-a-link-without-clicking-it", "Check a link without clicking", "Inspect a suspicious URL before visiting it."),
            ("/safe-link-checker", "Safe Link Checker", "Run the broader URL safety check."),
        ],
    },
    {
        "path": "/short-link-checker",
        "keyword": "short link checker",
        "title": "Short Link Checker — Check Shortened URLs Before Clicking",
        "description": "Check shortened URLs such as Bitly, TinyURL and t.co before clicking. Reveal redirect and destination warning signs with a privacy-first link check.",
        "h1": "Short Link Checker: Check the Destination Before Clicking",
        "kicker": "Short URLs",
        "quick": "Shortened links are not automatically dangerous, but they hide the destination. Paste the short URL into the checker so you can review redirect behavior and the final hostname before deciding whether to continue.",
        "sections": [
            ("Why short links deserve an extra check", [
                "Services such as Bitly, TinyURL and t.co replace a long destination with a compact address. That is useful for messages and social media, but it also removes the most useful clue a recipient normally sees: the real destination domain.",
                "A legitimate marketing link and a phishing link can therefore look very similar before the redirect happens. The shortener itself is not the verdict; the final destination and the context of the message matter more."
            ]),
            ("What happens when the checker follows redirects", [
                "The checker requests the URL without your browser cookies and records the redirect chain it can observe. It then evaluates the final hostname and other URL-level warning signs instead of judging only the shortener's domain.",
                "Some links behave differently by device, region or login state. A server-side redirect check can therefore differ from what a browser or mobile app eventually sees."
            ]),
            ("Red flags after a short URL expands", [
                "Be cautious if a familiar brand name appears on an unrelated domain, if the destination requests credentials unexpectedly, if several unrelated domains appear in the redirect chain, or if the final URL immediately downloads an executable or archive.",
                "A clean expansion does not authenticate the sender. If the message claims to be from a bank, marketplace, delivery company or employer, independently open the official service when the request involves money or credentials."
            ]),
        ],
        "faqs": [
            ("Are Bitly links safe?", "Bitly is a legitimate shortening service, but any shortening service can point to safe or unsafe destinations. Check the final URL rather than trusting the shortener alone."),
            ("Can a short link hide another redirect?", "Yes. A shortener may redirect to a URL that redirects again. Multiple redirects are not proof of fraud, but they make the destination harder to judge."),
            ("Will checking the link open it on my device?", "The main checker performs its server-side check without navigating your browser to the destination."),
            ("Should I trust a short link from a friend?", "Only if the message and request make sense. A friend's account can be compromised, so unexpected login or payment links still deserve verification."),
        ],
        "related": [
            ("/is-a-bitly-link-safe", "Is a Bitly link safe?", "See how to judge Bitly links specifically."),
            ("/how-to-check-a-link-without-clicking-it", "Check without clicking", "Inspect a URL before opening it."),
            ("/phishing-link-checker", "Phishing Link Checker", "Check credential-stealing warning signs."),
        ],
    },
    {
        "path": "/how-to-check-if-a-link-is-safe",
        "keyword": "how to check if a link is safe",
        "title": "How to Check If a Link Is Safe Before You Click",
        "description": "Learn how to check if a link is safe before clicking: inspect the real domain, redirects, short links, phishing signs, downloads and reputation warnings.",
        "h1": "How to Check If a Link Is Safe Before You Click",
        "kicker": "Safety guide",
        "quick": "Copy the link without opening it, paste it into a URL safety checker, inspect the final domain and warning signs, and independently verify any unexpected request for passwords, payments or downloads.",
        "sections": [
            ("1. Look at the real domain", [
                "Read the hostname from right to left around the registered domain instead of trusting words elsewhere in the URL. A scammer can place a company name in a subdomain or path while using an unrelated destination domain.",
                "Watch for small spelling changes, extra words, unusual characters and internationalized lookalikes. A professional logo or familiar page design does not prove ownership of the domain."
            ]),
            ("2. Check redirects and shortened URLs", [
                "Short URLs and tracking links hide the final destination. Use a checker that can reveal the redirect chain before you decide whether the final hostname matches what you expected.",
                "Redirects are common on legitimate websites, so they are not automatically malicious. The important question is whether the chain unexpectedly moves to a different organization or ends on a suspicious destination."
            ]),
            ("3. Treat urgent login, payment and download requests as higher risk", [
                "Messages about suspended accounts, failed deliveries, refunds, invoices, prizes and security alerts often create urgency so you act before checking the destination.",
                "If the link asks for a password, card number, one-time code, recovery phrase or software download, verify the request through an official app, a bookmark you already trust, or a website address you type yourself."
            ]),
            ("4. Use reputation as evidence, not certainty", [
                "Threat-reputation services are useful for known phishing and malware URLs, but a brand-new malicious page can exist before it is listed. Conversely, an unfamiliar URL is not automatically malicious.",
                "Combine reputation with domain inspection, redirect behavior, message context and browser or security warnings. No single green check should override a serious red flag."
            ]),
        ],
        "faqs": [
            ("What is the fastest way to check a suspicious link?", "Copy the URL without opening it, paste it into a link safety checker, then verify the final domain and any warnings before continuing."),
            ("Can I check a link without visiting the website?", "Yes. A server-side URL checker can inspect many link and redirect signals without navigating your browser to the destination."),
            ("Is a padlock enough to trust a link?", "No. The padlock means the connection is encrypted to that domain; phishing sites can also use HTTPS."),
            ("What if the checker finds nothing suspicious?", "Continue cautiously. A clean result reduces some uncertainty but cannot prove that a new or targeted threat is safe."),
        ],
        "related": [
            ("/how-to-check-a-link-without-clicking-it", "Check a link without clicking", "Use a safer workflow for suspicious URLs."),
            ("/how-to-tell-if-a-link-is-phishing", "Tell if a link is phishing", "Focus on credential-stealing signs."),
            ("/safe-link-checker", "Safe Link Checker", "Paste a URL into the main safety tool."),
        ],
    },
    {
        "path": "/can-a-link-give-you-a-virus",
        "keyword": "can a link give you a virus",
        "title": "Can a Link Give You a Virus? What Happens After You Click",
        "description": "Can clicking a link give you a virus? Learn how malicious links lead to malware downloads, phishing pages and exploits, and how to check a URL first.",
        "h1": "Can a Link Give You a Virus?",
        "kicker": "Malware basics",
        "quick": "Yes, a malicious link can expose you to malware risk, although the exact path varies. It may lead to a malicious download, exploit a browser vulnerability, or trick you into installing software. Many attacks instead steal passwords through phishing rather than installing a traditional virus.",
        "sections": [
            ("A malicious link does not always mean an automatic infection", [
                "Modern browsers isolate web content and block many dangerous behaviors, so simply loading a page does not guarantee malware will install. However, browser or plugin vulnerabilities can exist, and attackers frequently rely on social engineering instead of a silent exploit.",
                "A page may tell you that an update is required, present a fake CAPTCHA that asks you to run a command, or offer an invoice, document or app that is actually malicious."
            ]),
            ("Phishing is often the bigger danger", [
                "Many harmful links are designed to steal credentials rather than infect a device. A fake Microsoft, Google, bank, marketplace or delivery login can capture passwords and one-time codes if the user trusts the page.",
                "That means antivirus alone cannot answer whether a link is safe. The destination domain, the request being made and the context of the message are also important."
            ]),
            ("How to reduce the risk before clicking", [
                "Keep your operating system and browser updated, avoid disabling built-in security warnings, and check unexpected links before opening them. For software, go directly to the official vendor instead of downloading an update from a message.",
                "If a suspicious link contains a file extension such as .exe, .msi, .apk, .scr or an archive, do not assume it is harmless because the sender appears familiar."
            ]),
        ],
        "faqs": [
            ("Can an iPhone get malware from a link?", "Mobile operating systems use strong isolation, but malicious links can still lead to phishing, configuration abuse, unwanted downloads or exploitation of software vulnerabilities. Keep the device updated."),
            ("Can Android get a virus from a link?", "A link can lead to malicious APK downloads, phishing pages or exploits. Avoid installing apps from unexpected links and keep Android and Play Protect updated."),
            ("Can a link steal my password without malware?", "Yes. Phishing pages are specifically designed to collect credentials without needing to install malware."),
            ("What if I already downloaded a file?", "Do not run it if you are unsure. Use your device's security software and verify the file's source independently."),
        ],
        "related": [
            ("/malware-link-checker", "Malware Link Checker", "Inspect a suspicious URL before opening it."),
            ("/how-to-check-if-a-link-is-safe", "How to check if a link is safe", "Use a practical pre-click checklist."),
            ("/phishing-link-checker", "Phishing Link Checker", "Check credential-theft warning signs."),
        ],
    },
    {
        "path": "/how-to-tell-if-a-link-is-phishing",
        "keyword": "how to tell if a link is phishing",
        "title": "How to Tell If a Link Is Phishing: 7 Warning Signs",
        "description": "Learn how to tell if a link is phishing by checking the real domain, lookalike spelling, login requests, urgency, redirects, HTTPS and message context.",
        "h1": "How to Tell If a Link Is Phishing",
        "kicker": "Phishing guide",
        "quick": "The strongest clues are a mismatched or lookalike domain, an unexpected request to sign in, urgency, a hidden destination, and a request for passwords, payment details or one-time codes. Check the URL before opening it and verify important requests through the official service.",
        "sections": [
            ("1. The domain does not match the company", [
                "A phishing URL may contain a brand name while the actual registered domain belongs to someone else. Do not judge a link by the first familiar word you see; identify the real hostname and compare it with the service's known domain.",
                "Small substitutions such as extra hyphens, swapped letters, added words and internationalized lookalikes are common ways to make a domain feel familiar at a glance."
            ]),
            ("2. The link creates urgency around an account", [
                "Messages that claim your account will be closed, a payment failed, a parcel cannot be delivered, or suspicious activity requires immediate verification are designed to shorten your decision time.",
                "Urgency alone does not prove phishing, but an unexpected login request combined with a questionable domain is a strong reason to stop and verify independently."
            ]),
            ("3. The page asks for information the sender should not need", [
                "Be especially cautious with requests for passwords, recovery phrases, one-time codes, full card details or identity documents. Legitimate support teams generally do not need you to reveal secrets through an unsolicited link.",
                "Password managers can also provide a useful clue: if your saved credentials do not recognize the domain, check the hostname carefully instead of manually typing the password."
            ]),
            ("4. HTTPS does not prove legitimacy", [
                "A phishing website can obtain a valid TLS certificate and display a padlock. HTTPS protects the connection to that domain; it does not certify that the domain belongs to the company shown on the page.",
                "Treat HTTPS as a baseline security feature, not a trust badge. Domain ownership and message context remain essential."
            ]),
        ],
        "faqs": [
            ("What is the easiest phishing sign to check?", "Check whether the final registered domain actually belongs to the organization named in the message."),
            ("Can phishing links come from a real person's account?", "Yes. Compromised email and social accounts can send malicious links from people you know."),
            ("Does a phishing checker guarantee a link is safe?", "No. New phishing pages may not yet be known, and some attacks change content depending on the visitor."),
            ("Should I reply to ask if the sender is real?", "For a suspicious or high-value request, verify through a separate channel you already trust rather than replying to the same conversation."),
        ],
        "related": [
            ("/phishing-link-checker", "Phishing Link Checker", "Run a phishing-oriented URL assessment."),
            ("/fake-package-delivery-link", "Fake package delivery links", "Recognize a common phishing scenario."),
            ("/sms-link-checker", "SMS Link Checker", "Check links received by SMS."),
        ],
    },
    {
        "path": "/how-to-check-a-link-without-clicking-it",
        "keyword": "how to check a link without clicking it",
        "title": "How to Check a Link Without Clicking It",
        "description": "Check a suspicious link without opening it in your browser. Copy the URL, inspect the destination, redirects and phishing warning signs first.",
        "h1": "How to Check a Link Without Clicking It",
        "kicker": "Pre-click check",
        "quick": "Copy the destination URL instead of opening it, paste it into a server-side link checker, review the final hostname and warnings, then decide whether to visit the site independently.",
        "sections": [
            ("Copy the URL instead of opening it", [
                "On desktop, you can usually right-click a link and copy its address. On mobile, press and hold the link and choose the option to copy it rather than open it. The exact wording varies by app.",
                "Be careful with buttons in emails and messages: the text shown on the button is not necessarily the URL it opens. Copy the destination itself when the app allows it."
            ]),
            ("Paste the link into a separate checker", [
                "A link checker can request the destination from its own server so your browser does not navigate directly to the suspicious page. It can inspect the URL, follow redirects and identify several structural warning signs.",
                "This does not make the destination harmless. The purpose is to gather more evidence before you expose your browser or credentials to it."
            ]),
            ("Read the final hostname before anything else", [
                "If the link redirects, compare the final hostname with the organization you expected. A familiar brand name elsewhere in the URL does not compensate for an unrelated final domain.",
                "For banking, payroll, marketplace payments and account recovery, use the official app or a trusted bookmark instead of continuing through an unexpected message link."
            ]),
        ],
        "faqs": [
            ("Does copying a link open it?", "Normally, copying a URL does not navigate to it. Use your app's copy-link action rather than tapping the link."),
            ("Can I preview a link safely by hovering over it?", "Hovering can reveal the URL in many desktop browsers and mail clients, but it does not perform a full safety check and may not show every redirect."),
            ("What if the URL is shortened?", "Use a checker that follows redirects so you can inspect the final destination before opening it."),
            ("Can I check a QR code without scanning it into a website?", "Yes. A QR safety tool can decode a screenshot locally and show the URL before navigation."),
        ],
        "related": [
            ("/short-link-checker", "Short Link Checker", "Reveal destinations hidden by short URLs."),
            ("/how-to-check-a-qr-code-before-opening", "Check a QR code before opening", "Use the same pre-click principle with QR codes."),
            ("/safe-link-checker", "Safe Link Checker", "Analyze the URL now."),
        ],
    },
    {
        "path": "/is-a-bitly-link-safe",
        "keyword": "is a bitly link safe",
        "title": "Is a Bitly Link Safe? How to Check Before Clicking",
        "description": "Bitly is legitimate, but a Bitly link can redirect to any destination. Learn how to check a bit.ly URL and its final destination before clicking.",
        "h1": "Is a Bitly Link Safe?",
        "kicker": "Bitly safety",
        "quick": "Bitly itself is a legitimate URL-shortening service, but a bit.ly link is not automatically safe because the creator chooses the destination. Check where the link redirects before entering credentials, paying or downloading anything.",
        "sections": [
            ("Why Bitly cannot guarantee the destination", [
                "URL shorteners are infrastructure: legitimate companies, newsletters, creators and ordinary users rely on them, but attackers can also attempt to shorten harmful destinations. The bit.ly hostname tells you which shortening service is used, not who owns the final page.",
                "The risk question should therefore move from 'Is Bitly safe?' to 'Where does this particular Bitly link go, and does that destination make sense?'"
            ]),
            ("Check the final destination", [
                "Paste the full bit.ly URL into a short-link checker and inspect the final hostname after redirects. Compare it with the brand, person or service mentioned in the message.",
                "If the destination suddenly asks you to sign in, pay a small delivery fee, install an application or download a file, verify the request independently before continuing."
            ]),
            ("Context still matters", [
                "A Bitly link can resolve to a technically normal website while the surrounding message is fraudulent. For example, a scam can send a victim to a genuine payment service but lie about why money should be sent.",
                "A URL checker helps with destination risk; it cannot validate every story, seller, recruiter or investment claim associated with a link."
            ]),
        ],
        "faqs": [
            ("Is bit.ly a virus?", "No. bit.ly is a legitimate URL-shortening domain. Individual shortened links can still point to harmful destinations."),
            ("Can Bitly links be used for phishing?", "Shortened URLs can be abused because they hide the final destination, which is why you should inspect the resolved URL."),
            ("Does the checker need to open Bitly on my phone?", "No. The main checker can request the link server-side and report the redirect information it observes."),
            ("Should I trust a Bitly link sent by a company?", "Verify that the final destination matches the company's official domain, especially for logins, payments or downloads."),
        ],
        "related": [
            ("/short-link-checker", "Short Link Checker", "Inspect Bitly, TinyURL, t.co and other short URLs."),
            ("/how-to-check-if-a-link-is-safe", "How to check if a link is safe", "Use the broader safety checklist."),
            ("/scam-link-checker", "Scam Link Checker", "Review scam-oriented warning signs."),
        ],
    },
    {
        "path": "/sms-link-checker",
        "keyword": "suspicious text message link",
        "title": "Suspicious Text Message Link? Check It Before You Tap",
        "description": "Received a suspicious link by SMS? Learn how to check text-message links for phishing, fake delivery, account and payment warning signs before tapping.",
        "h1": "Got a Suspicious Link in a Text Message?",
        "kicker": "SMS scams",
        "quick": "Do not tap the link. Copy it from the message if possible, check the destination separately, and verify the request through the company's official app or website. Unexpected delivery fees, account alerts and payment requests are common smishing themes.",
        "sections": [
            ("Why SMS links feel convincing", [
                "Text messages are short, immediate and often read on a phone where full URLs are harder to inspect. Attackers use that limited space to create urgency around deliveries, bank alerts, tolls, taxes, subscription renewals or account verification.",
                "The sender name or phone number is not sufficient proof. Sender IDs can be spoofed in some contexts, and compromised accounts or services can also distribute malicious messages."
            ]),
            ("Common smishing warning signs", [
                "Treat an unexpected request for a small payment, password, one-time code or identity information as higher risk. Look closely at the destination domain, spelling, shortened URLs and whether the message pressures you to act immediately.",
                "Messages can also be fraudulent without containing a technically malicious website. A scammer may send you to a legitimate payment platform while lying about the reason for payment."
            ]),
            ("Safer way to respond", [
                "Do not reply with personal information. If the message claims to be from a delivery company, bank, marketplace or government service, open the official app or type the known website yourself.",
                "If the message came from someone you know but seems unusual, contact them through another channel before following the request."
            ]),
        ],
        "faqs": [
            ("What is smishing?", "Smishing is phishing delivered through SMS or text messaging, usually to steal credentials, payment details or other sensitive information."),
            ("Can replying to a scam text be risky?", "Replying can confirm that a number is active and may continue the interaction. Use official reporting or blocking tools instead when appropriate."),
            ("What if the text says my package is waiting?", "Open the carrier's official app or website independently and check the tracking number there instead of paying through an unexpected link."),
            ("Can I paste the SMS link into the checker?", "Yes. Copy the URL without opening it and paste it into the main scanner."),
        ],
        "related": [
            ("/fake-package-delivery-link", "Fake package delivery link", "Check a common SMS scam pattern."),
            ("/how-to-tell-if-a-link-is-phishing", "How to tell if a link is phishing", "Learn the main phishing warning signs."),
            ("/scam-link-checker", "Scam Link Checker", "Analyze the suspicious URL."),
        ],
    },
    {
        "path": "/fake-package-delivery-link",
        "keyword": "fake package delivery link",
        "title": "Fake Package Delivery Link? How to Spot the Scam",
        "description": "Learn how to spot fake package-delivery links, small-fee scams and phishing messages. Check the URL before entering payment or account details.",
        "h1": "Fake Package Delivery Link? Check Before You Pay",
        "kicker": "Delivery scams",
        "quick": "Unexpected messages claiming a parcel needs a small fee, address confirmation or urgent rescheduling are a common phishing pattern. Do not pay through the message link; verify the tracking information on the carrier's official site or app.",
        "sections": [
            ("Why delivery scams ask for a small amount", [
                "A low fee can feel too small to justify suspicion, but the objective may be to collect card details, credentials or personal information rather than the fee itself. The message often creates urgency by claiming the parcel will be returned or delivery will fail.",
                "Attackers can imitate carrier branding and use domains that contain familiar delivery words. The real registered domain matters more than the logo or page design."
            ]),
            ("Verify the shipment independently", [
                "Use a tracking number in the carrier's official app or website rather than opening the message link. If no tracking number is provided, check the store or marketplace where you actually placed the order.",
                "If you are not expecting a parcel, that is another reason to avoid interacting with the link. Do not provide card details merely to find out what the package supposedly contains."
            ]),
            ("What a link checker can tell you", [
                "A checker can flag lookalike domains, suspicious payment wording, shorteners, redirects and other URL-level warning signs before you visit the destination.",
                "It cannot confirm that a real shipment exists. The final verification still needs to come from the carrier or merchant through a channel you independently trust."
            ]),
        ],
        "faqs": [
            ("Do delivery companies charge redelivery fees by text?", "Policies vary, but an unexpected fee request should always be verified through the carrier's official website or app rather than the message link."),
            ("Can a fake delivery page steal card details?", "Yes. Fake checkout forms can collect payment and identity information even when the requested amount is very small."),
            ("What if the domain contains the carrier's name?", "A brand name can appear in a subdomain or unrelated registered domain. Compare the actual domain with the carrier's official site."),
            ("Should I click just to see the tracking number?", "No. Copy and check the URL first, or visit the carrier independently."),
        ],
        "related": [
            ("/sms-link-checker", "SMS Link Checker", "Use a safer workflow for SMS links."),
            ("/scam-link-checker", "Scam Link Checker", "Check the suspicious delivery URL."),
            ("/how-to-check-a-link-without-clicking-it", "Check without clicking", "Inspect the URL first."),
        ],
    },
    {
        "path": "/how-to-check-a-qr-code-before-opening",
        "keyword": "how to check a QR code before opening",
        "title": "How to Check a QR Code Link Before Opening It",
        "description": "Check a QR code before opening its link. Decode a screenshot, inspect the URL for phishing or scam signs, and avoid automatic navigation.",
        "h1": "How to Check a QR Code Before Opening Its Link",
        "kicker": "QR safety",
        "quick": "Take a screenshot or photo of the QR code and decode it without automatically navigating to the destination. Read the URL first, then run it through a safety checker before opening it.",
        "sections": [
            ("Why QR codes hide an important clue", [
                "With a normal link, you may be able to see or copy the hostname before opening it. A QR code hides the destination inside an image, so scanning apps that navigate immediately can remove that moment of inspection.",
                "QR codes are useful and usually harmless, but stickers placed over parking meters, menus, posters or payment terminals can redirect people to fraudulent pages."
            ]),
            ("Decode first, navigate second", [
                "Use a QR tool that reveals the text or URL before opening it. Can I Share This?'s QR page decodes a selected image in the browser and then lets you send the extracted URL to the main checker.",
                "Reading the QR content is not the same as trusting it. Check whether the destination domain matches the organization or service you expected."
            ]),
            ("Be especially careful with QR payments and logins", [
                "A QR code that leads to a payment form, account login, crypto transfer or app download deserves independent verification. For parking and public payments, compare the destination with the operator's official signage or app.",
                "Do not install an application or mobile configuration profile merely because a QR code instructs you to do so."
            ]),
        ],
        "faqs": [
            ("Can scanning a QR code give me a virus?", "Simply decoding the QR content is different from opening its destination. Risk increases when you navigate to a malicious page or install content it provides."),
            ("Can a QR code be changed with a sticker?", "Yes. A printed QR code can be covered by another code, which is why physical context and the decoded domain matter."),
            ("Does the QR image need to be uploaded to your server?", "The QR scanner is designed to decode the selected image locally in the browser before the extracted URL is analyzed."),
            ("What if the QR code contains text instead of a URL?", "Do not treat arbitrary text or commands as instructions to run. Only navigate when you understand and trust the destination."),
        ],
        "related": [
            ("/qr-code-link-checker", "QR Code Link Checker", "Decode a QR screenshot before opening it."),
            ("/how-to-check-a-link-without-clicking-it", "Check a link without clicking", "Use the same pre-click workflow for normal URLs."),
            ("/phishing-link-checker", "Phishing Link Checker", "Check the extracted URL for phishing signs."),
        ],
    },
]

# The cluster deliberately contains exactly 10 pages.
assert len(PAGES) == 10


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def json_ld(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_page(page: dict) -> str:
    canonical = HOST + page["path"]
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": "Link Safety", "item": HOST + "/safe-link-checker"},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": canonical},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["title"],
        "description": page["description"],
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": HOST + "/"},
        "about": {"@type": "Thing", "name": page["keyword"]},
    }
    sections = "".join(
        '<section class="card">' + f'<h2>{esc(title)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in paragraphs) + "</section>"
        for title, paragraphs in page["sections"]
    )
    faqs = "".join(f'<article class="faq"><h3>{esc(q)}</h3><p>{esc(a)}</p></article>' for q, a in page["faqs"])
    related = "".join(
        f'<a class="related" href="{esc(href, True)}"><strong>{esc(label)}</strong><span>{esc(desc)}</span><b aria-hidden="true">→</b></a>'
        for href, label, desc in page["related"]
    )
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'], True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(page['title'], True)}"><meta property="og:description" content="{esc(page['description'], True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld(breadcrumb)}</script><script type="application/ld+json">{json_ld(webpage)}</script>
<style>
:root{{color-scheme:light dark;--bg:#f6f7f9;--card:#fff;--text:#17191d;--muted:#69717c;--line:#e2e6eb;--soft:#f7f9fb;--accent:#15171a;--accentText:#fff;--warn:#956100;--shadow:0 12px 34px rgba(17,24,39,.055)}}@media(prefers-color-scheme:dark){{:root{{--bg:#0d0f12;--card:#15181d;--text:#f3f4f6;--muted:#a6acb7;--line:#2a2f37;--soft:#111419;--accent:#f3f4f6;--accentText:#111318;--warn:#f2bd54;--shadow:0 14px 34px rgba(0,0,0,.22)}}}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit}}header{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}.nav{{max-width:1040px;margin:auto;padding:13px 20px;display:flex;align-items:center;justify-content:space-between;gap:14px}}.brand{{font-weight:850;text-decoration:none;letter-spacing:-.02em}}.button{{display:inline-flex;min-height:42px;align-items:center;justify-content:center;background:var(--accent);color:var(--accentText);padding:9px 15px;border-radius:11px;text-decoration:none;font-weight:800}}main{{max-width:900px;margin:auto;padding:38px 20px 72px}}.crumbs{{font-size:13px;color:var(--muted);margin-bottom:19px}}.kicker{{display:inline-block;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:5px 9px;color:var(--muted);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(34px,7vw,58px);line-height:1.03;letter-spacing:-.045em;margin:13px 0 21px;text-wrap:balance}}.quick{{padding:clamp(20px,4vw,30px);border:1px solid var(--line);border-radius:20px;background:var(--card);box-shadow:var(--shadow);font-size:clamp(17px,2.4vw,20px);margin-bottom:17px}}.quick:before{{content:"Quick answer";display:block;color:var(--warn);font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}}.card{{margin:13px 0;padding:clamp(19px,3.4vw,28px);border:1px solid var(--line);border-radius:18px;background:var(--card)}}h2{{font-size:clamp(22px,3.5vw,28px);line-height:1.2;letter-spacing:-.025em;margin:0 0 12px}}p{{margin:0 0 14px}}p:last-child{{margin-bottom:0}}.section-title{{margin:34px 0 12px}}.section-title span{{color:var(--muted);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}.section-title h2{{margin:3px 0 0;font-size:clamp(25px,4vw,32px)}}.faq{{margin:9px 0;padding:18px 20px;border:1px solid var(--line);border-radius:15px;background:var(--card)}}.faq h3{{font-size:17px;line-height:1.3;margin:0 0 7px}}.related-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}.related{{position:relative;display:flex;flex-direction:column;gap:4px;padding:16px 38px 16px 16px;border:1px solid var(--line);border-radius:15px;background:var(--card);text-decoration:none}}.related span{{color:var(--muted);font-size:13px;line-height:1.45}}.related b{{position:absolute;right:15px;top:15px}}.cta{{margin-top:30px;padding:24px;border:1px solid var(--line);border-radius:19px;background:var(--card);text-align:center}}.cta h2{{margin:0 0 7px}}footer{{border-top:1px solid var(--line);padding:22px;text-align:center;color:var(--muted);font-size:13px}}@media(max-width:700px){{main{{padding:28px 15px 55px}}.nav{{padding:10px 15px}}h1{{font-size:clamp(33px,11vw,46px)}}.quick,.card{{border-radius:16px}}.related-grid{{grid-template-columns:1fr}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style></head><body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main><div class="crumbs"><a href="/">Home</a> / <a href="/safe-link-checker">Link Safety</a></div><span class="kicker">{esc(page['kicker'])}</span><h1>{esc(page['h1'])}</h1><section class="quick">{esc(page['quick'])}</section>{sections}<div class="section-title"><span>Questions</span><h2>Frequently asked questions</h2></div><section>{faqs}</section><div class="section-title"><span>Related</span><h2>Keep checking safely</h2></div><nav class="related-grid" aria-label="Related safety guides">{related}</nav><section class="cta"><h2>Check the link before you open it</h2><p>Paste the suspicious URL into Can I Share This? for a fast, privacy-first risk assessment.</p><p><a class="button" href="/">Analyze the link</a></p></section></main><footer>Can I Share This? · Check suspicious links before you click</footer>
</body></html>'''


def write_pages() -> None:
    for page in PAGES:
        target = DIST / f"{page['path'].strip('/')}.html"
        target.write_text(render_page(page), encoding="utf-8")


def update_sitemap() -> None:
    sitemap = DIST / "sitemap.xml"
    urls: set[str] = set()
    if sitemap.is_file():
        old = sitemap.read_text(encoding="utf-8", errors="replace")
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(HOST + (parsed.path.rstrip("/") or "/"))
    urls.add(HOST + "/")
    for page in PAGES:
        urls.add(HOST + page["path"])
    entries = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding="utf-8")


def expose_from_safety_hub() -> None:
    hub = DIST / "safe-link-checker.html"
    if not hub.is_file():
        return
    text = hub.read_text(encoding="utf-8")
    marker = '<section class="cta"><h2>Got a suspicious link?</h2>'
    if marker not in text or 'id="safety-guides-cluster"' in text:
        return
    cards = "".join(
        f'<a class="related" href="{esc(page["path"], True)}"><strong>{esc(page["h1"])}</strong><span>{esc(page["description"])}</span><b aria-hidden="true">→</b></a>'
        for page in PAGES
    )
    block = '<div id="safety-guides-cluster" class="section-title"><span>Safety guides</span><h2>Common suspicious-link questions</h2></div><nav class="related-grid" aria-label="Link safety guides">' + cards + '</nav>'
    text = text.replace(marker, block + marker, 1)
    hub.write_text(text, encoding="utf-8")


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist/ does not exist; run this after the base build")
    write_pages()
    update_sitemap()
    expose_from_safety_hub()
    print(f"Generated {len(PAGES)} focused anti-scam SEO pages")


if __name__ == "__main__":
    main()
