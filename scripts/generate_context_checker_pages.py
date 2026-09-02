#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"
UPDATED = "2026-09-03"

PAGES = [{'path': '/sms-link-checker',
  'keyword': 'sms link checker',
  'title': 'SMS Link Checker: Check a Suspicious Text Message Link',
  'description': 'Received a suspicious text? Check the link’s destination, redirects, known threat reports and warning signs before you open it or enter information.',
  'h1': 'Check a suspicious link from a text message',
  'kicker': 'SMS & text-message safety',
  'answer': 'Do not open an unexpected link just because it arrived by text. Paste the URL into the checker first, then independently verify the sender through a website, app or phone number you already trust.',
  'why': ['Text-message scams often create urgency around deliveries, tolls, bank alerts, account problems, prizes or unpaid fees. The sender name and phone number are not enough to prove who sent the message.',
          'A link can look familiar while leading to a different domain, a shortened destination or a page designed to collect payment details, passwords or identity information.'],
  'checks': [('Final destination', 'See the website the link resolves to after redirects.'),
             ('Known threat reports', 'Compare eligible public URLs with known malware and phishing threat lists.'),
             ('URL warning signs', 'Look for suspicious domain patterns, unusual redirects and risky downloads.'),
             ('Content context', 'Identify common link types such as social, cloud, shopping, files, gambling or crypto.')],
  'safe_steps': ['Do not reply to an unexpected text to verify it.',
                 'Open the company’s official app or type its known website yourself.',
                 'If the message mentions a charge, delivery or account problem, check that account independently.',
                 'Never provide one-time codes, passwords or card details because a text tells you to act quickly.'],
  'faqs': [('Can a text from a real-looking sender still be fake?',
            'Yes. Sender names and phone numbers can be misleading or spoofed. Verify the request through a separate trusted channel.'),
           ('Does a clean scan mean the SMS link is safe?',
            'No. It means the checks did not report a known technical threat or obvious warning sign. A new scam page may not yet appear in reputation systems.'),
           ('Should I click a shortened link in a text?',
            'Treat shortened links cautiously because the visible URL hides the final website. Resolve and inspect the destination before interacting with it.'),
           ('What if I already entered my password?',
            'Change the password on the real service, revoke unfamiliar sessions, enable multi-factor authentication where available and change reused passwords.')],
  'related': ['/phishing-link-checker',
              '/fake-package-delivery-scam',
              '/scam-warning-signs',
              '/what-to-do-after-clicking-a-phishing-link'],
  'sources': [('FTC — How to Recognize and Report Spam Text Messages',
               'https://consumer.ftc.gov/articles/how-recognize-and-report-spam-text-messages'),
              ('FTC — Is That Unexpected Text a Scam?',
               'https://consumer.ftc.gov/consumer-alerts/2025/04/unexpected-text-scam'),
              ('FTC — How To Recognize and Avoid Phishing Scams',
               'https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams')]},
 {'path': '/whatsapp-link-checker',
  'keyword': 'whatsapp link checker',
  'title': 'WhatsApp Link Checker: Check a Suspicious WhatsApp URL',
  'description': 'Check a suspicious WhatsApp link before opening it. Inspect the destination, redirects, content type, domain context and known threat reports in one scan.',
  'h1': 'Check a suspicious WhatsApp link',
  'kicker': 'WhatsApp message safety',
  'answer': 'A WhatsApp message can come from an unknown number, a compromised account or someone impersonating a contact. Check the link separately and verify any request for money, login details or investment through another channel.',
  'why': ['Scams on messaging apps can begin with an unexpected investment offer, fake support message, job opportunity, prize, delivery notice or a message from an account pretending to be someone you know.',
          'Even when a WhatsApp conversation looks normal, the linked website is a separate trust decision. The important questions are where the link really goes, what kind of content it contains and whether independent threat sources report it.'],
  'checks': [('Destination', 'Follow safe redirect logic to show the final public website.'),
             ('Link category',
              'Recognize social, video, audio, cloud, shopping, file, finance and other common link types.'),
             ('Threat reputation', 'For eligible public links, check known malware and phishing reports.'),
             ('Domain context', 'Use signals such as domain age and the exact final hostname as context, not proof.')],
  'safe_steps': ['Confirm unexpected requests with the person using a separate call or an existing conversation.',
                 'Never send money or crypto because a new contact promises guaranteed returns or urgent help.',
                 'Do not share verification codes, recovery codes or passwords in chat.',
                 'Use the official website or app independently for account, payment or support actions.'],
  'faqs': [('Can a WhatsApp account be compromised?',
            'Yes. A genuine contact’s account can be taken over, so an unexpected request should still be verified independently.'),
           ('Can Can I Share This? read my WhatsApp conversation?',
            'No. The checker only analyzes the link or email address you choose to submit; it does not need access to your WhatsApp chats.'),
           ('Why are investment links on WhatsApp risky?',
            'Unexpected investment contacts can direct people to fake platforms that display invented profits or block withdrawals. Verify the company independently before sending funds.'),
           ('What should I do with a suspicious WhatsApp link?',
            'Do not open it first. Copy the URL, check the final domain and threat signals, then contact the supposed sender through another trusted route.')],
  'related': ['/crypto-investment-scam', '/phishing-link-checker', '/scam-warning-signs', '/lookalike-domain-examples'],
  'sources': [('FTC — Investment scams and messaging apps',
               'https://consumer.ftc.gov/consumer-alerts/2026/04/people-losing-big-investment-scams-learn-how-spot-and-avoid-them'),
              ('FTC — How To Recognize and Avoid Phishing Scams',
               'https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams')]},
 {'path': '/qr-code-scam-checker',
  'keyword': 'qr code scam checker',
  'title': 'QR Code Scam Checker: Check a QR Link Before You Open It',
  'description': 'Decoded a QR code you do not trust? Check its destination, redirects, domain context and known threat reports before signing in, paying or downloading.',
  'h1': 'Check a suspicious QR code link',
  'kicker': 'QR-code safety',
  'answer': 'A QR code hides its destination until it is decoded. If a QR code is unexpected or attached to a payment, parking, delivery or account request, inspect the decoded URL before visiting the website.',
  'why': ['QR codes can be placed in texts, emails, letters, parking signs, packages and physical stickers. The image itself does not show whether the destination is the organization you expect.',
          'Scammers can use QR codes to send people to lookalike payment or login pages. The safest workflow is to decode first, inspect the domain and then use an independently known website for sensitive actions.'],
  'checks': [('Decoded destination', 'Use the site’s QR tool to extract the URL without treating the QR image as trustworthy.'),
             ('Redirect chain', 'Show when the decoded link changes destination.'),
             ('Threat reports', 'Check eligible public destinations against known malware and phishing reports.'),
             ('Context', 'Identify the content type, final domain and other warning signals before you act.')],
  'safe_steps': ['Do not scan a QR code just because it appears on an official-looking letter or sign.',
                 'Compare the final domain with the organization’s real website.',
                 'For payments, open the official app or type the known address yourself.',
                 'If a sticker appears to cover another QR code, do not use it.'],
  'faqs': [('Can a QR code itself contain malware?',
            'A QR code usually contains data such as a URL. The danger is typically what the decoded destination asks you to open, download, pay or enter.'),
           ('Can I check a QR code without visiting its website?',
            'Yes. Decode the QR code first and inspect the resulting URL before deciding whether to visit it.'),
           ('Why are QR payment scams effective?',
            'The destination is visually hidden in the code, so people may focus on the surrounding logo or sign instead of the actual domain.'),
           ('What if the QR code came by text?',
            'Treat both the message and QR destination as untrusted until you verify the request through an official channel.')],
  'related': ['/qr-code-link-checker', '/phishing-link-checker', '/bank-impersonation-scam', '/scam-warning-signs'],
  'sources': [('FTC — Traffic violation text and QR-code scam',
               'https://consumer.ftc.gov/consumer-alerts/2026/04/text-about-traffic-violation-probably-scam'),
              ('FTC — Cryptocurrency QR payment scam', 'https://consumer.ftc.gov/new-crypto-payment-scam-alert')]},
 {'path': '/download-link-checker',
  'keyword': 'download link checker',
  'title': 'Download Link Checker: Check a File URL Before Downloading',
  'description': 'Check a download link before opening it. Identify file types, redirects, final domains and known threat reports, with extra caution for software and archives.',
  'h1': 'Check a download link before opening the file',
  'kicker': 'Download & file safety',
  'answer': 'A download link deserves more caution than a normal webpage because the destination may deliver software, an archive or another file. Check the final domain and file type first, and get software from the publisher’s official site whenever possible.',
  'why': ['File links can hide behind generic download buttons, short URLs, cloud shares or redirects. A filename alone does not prove what a server will return, and an archive can contain files that are not visible until it is opened.',
          'The checker can identify common URL and response file types and highlight executable or compressed formats. That is context, not a malware scan of the file contents.'],
  'checks': [('File type', 'Identify common formats such as PDF, ZIP, RAR, EXE, APK, image, audio and video.'),
             ('Final website', 'Show which domain actually serves the link after redirects.'),
             ('Known URL threats', 'Check eligible public URLs against known malware and phishing reports.'),
             ('Download context', 'Warn when the destination appears to be software or a compressed archive.')],
  'safe_steps': ['Prefer the software publisher’s official download page or a trusted app store.',
                 'Do not disable security software because an installer tells you to.',
                 'Be cautious with executables, scripts, disk images and archives from unexpected messages.',
                 'After downloading, use your device’s security tools and verify publisher signatures or hashes when the publisher provides them.'],
  'faqs': [('Does this scan the file itself for malware?',
            'No. The link checker evaluates the URL, destination and file context. It should not be treated as a full antivirus scan of downloaded bytes.'),
           ('Why is a ZIP file treated cautiously?',
            'Archives can contain multiple files, including executable or script content that is not obvious from the link itself.'),
           ('Is an HTTPS download automatically safe?',
            'No. HTTPS protects the connection to a website; it does not prove that the site or file is trustworthy.'),
           ('What is the safest place to download software?',
            'Use the publisher’s official website or a trusted platform and confirm the exact domain before downloading.')],
  'related': ['/safe-link-checker',
              '/phishing-link-checker',
              '/what-to-do-after-clicking-a-phishing-link',
              '/scam-warning-signs'],
  'sources': [('FTC — Phishing scams can include harmful downloads',
               'https://consumer.ftc.gov/consumer-alerts/2024/12/phishing-scams-can-be-hard-spot'),
              ('CISA — Counter-phishing recommendations',
               'https://www.cisa.gov/sites/default/files/publications/Capacity_Enhancement_Guide-Counter-Phishing-Recommendations_for_Non-Federal_Organizations_0.pdf')]},
 {'path': '/short-link-checker',
  'keyword': 'short link checker',
  'title': 'Short Link Checker: Reveal and Check a Shortened URL',
  'description': 'Check a Bitly, t.co, TinyURL or other short link before trusting it. Reveal the final destination, redirects and known threat signals first.',
  'h1': 'Check where a shortened link really goes',
  'kicker': 'Short URL safety',
  'answer': 'Shortened URLs hide the final website. Before signing in, paying or downloading, resolve the short link, inspect the final hostname and verify that it matches the service you expected.',
  'why': ['Short links are useful and often legitimate, but the visible address removes information you would normally use to judge a destination. That makes the final domain more important than the shortener brand.',
          'Attackers can also combine multiple redirects. A reputable shortener does not guarantee that every destination created through it is trustworthy.'],
  'checks': [('Shortener recognition', 'Recognize common shortening domains such as bit.ly, t.co and TinyURL.'),
             ('Final destination', 'Follow allowed redirects and show the final public hostname.'),
             ('Redirect changes', 'Flag when the link moves to a different website.'),
             ('Threat reports', 'Check eligible public final URLs against known threat sources.')],
  'safe_steps': ['Focus on the final domain, not the shortener’s reputation.',
                 'If the destination asks for a login, open that service independently instead.',
                 'Do not continue if the final domain is unexpected, misspelled or unrelated to the message.',
                 'Be extra cautious when a short link ends in a download or payment page.'],
  'faqs': [('Are all shortened links dangerous?',
            'No. Short links are widely used for legitimate reasons. The risk is that the visible link hides the final destination.'),
           ('Does Bitly guarantee the final page is safe?',
            'No shortener can make every destination trustworthy. Evaluate the final website separately.'),
           ('What is a redirect chain?',
            'It is the sequence of URLs a browser follows before reaching the final page. Cross-domain redirects can be important context.'),
           ('Why should I avoid logging in through a short link?',
            'For sensitive actions, it is safer to open the service through its official app, a saved bookmark or an address you type yourself.')],
  'related': ['/check-if-link-expires', '/phishing-url-signals', '/lookalike-domain-examples', '/safe-link-checker'],
  'sources': [('CISA — Shortened URLs can mask destinations in phishing',
               'https://www.cisa.gov/sites/default/files/publications/AA22-047A%20Russian%20State-Sponsored%20Cyber%20Actors%20Target%20CDC%20Networks.pdf'),
              ('CISA — Technical Trends in Phishing Attacks',
               'https://www.cisa.gov/sites/default/files/publications/phishing_trends0511.pdf')]},
 {'path': '/is-this-email-safe',
  'keyword': 'is this email safe',
  'title': 'Is This Email Safe? Check a Sender Address for Warning Signs',
  'description': 'Check an email address for domain and mail-security warning signs, including MX, SPF, DMARC, domain age and possible lookalike patterns.',
  'h1': 'Is this email address safe?',
  'kicker': 'Sender-address safety',
  'answer': 'An email address alone cannot prove who is behind a message, but its domain can reveal useful warning signs. Check the address, then verify unexpected requests through an independent channel before replying, paying or sharing information.',
  'why': ['Display names are easy to imitate, and a familiar-looking address can use a subtly different domain. Domain-level signals help explain whether a sender address has normal mail infrastructure and whether the domain is unusually new or resembles a known brand.',
          'SPF and DMARC are useful authentication signals, but their presence does not prove that a specific message or sender is legitimate. Treat them as part of the evidence, not a green light.'],
  'checks': [('Mail servers', 'Look for MX records showing whether the domain is configured to receive email.'),
             ('SPF & DMARC', 'Report published sender-authentication policies and important policy context.'),
             ('Domain age', 'Use RDAP registration data when available as a contextual signal.'),
             ('Lookalike patterns', 'Check for domain spellings that may imitate a recognizable brand.')],
  'safe_steps': ['Do not use the display name as proof of identity.',
                 'Compare the full domain after the @ symbol with the organization’s official domain.',
                 'Verify requests for money, credentials or documents using a saved phone number or official website.',
                 'Inspect message headers when you need evidence about the actual delivery path and authentication results.'],
  'faqs': [('Can SPF and DMARC prove an email is legitimate?',
            'No. They help authenticate permitted sending infrastructure and domain policy, but a legitimate domain can still send an unwanted message or have a compromised account.'),
           ('What does a very new email domain mean?',
            'It is a reason for extra verification, not proof of fraud. Many legitimate organizations also use recently registered domains.'),
           ('Can the checker tell whether a mailbox exists?',
            'Not reliably without interacting with the mail provider, which can be inaccurate and privacy-invasive. The checker focuses on domain-level signals.'),
           ('Does the email checker send my address to Google Web Risk?',
            'No. The email path uses email and domain checks rather than sending the email address to the URL threat-list service.')],
  'related': ['/email-safety-checker',
              '/fake-email-address-signs',
              '/spf-dmarc-email-security',
              '/account-verification-scam'],
  'sources': [('FTC — How To Recognize and Avoid Phishing Scams',
               'https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams'),
              ('FTC — Protect yourself from phishing scams',
               'https://consumer.ftc.gov/consumer-alerts/2025/04/protect-yourself-phishing-scams')]},
 {'path': '/gambling-link-safety',
  'keyword': 'gambling link safety',
  'title': 'Gambling Link Safety: Check a Casino or Betting Website',
  'description': 'Check a casino or betting link for technical warning signs, final destination and content category. A clean scan does not prove licensing or trustworthiness.',
  'h1': 'Check a gambling or betting link',
  'kicker': 'Gambling-link transparency',
  'answer': 'A gambling site can have no known malware or phishing report and still carry financial, age-restriction or licensing risks. Treat technical security and gambling legitimacy as separate questions.',
  'why': ['Malware and phishing reputation systems answer a narrow technical question. They do not determine whether an operator is licensed in your location, whether withdrawals will be honored or whether gambling is appropriate for you.',
          'The checker therefore labels known gambling and betting content separately from the malware/phishing verdict. This prevents a green technical result from being presented as a broad endorsement.'],
  'checks': [('Technical reputation', 'Check eligible public URLs for known malware and phishing reports.'),
             ('Content category', 'Identify gambling or betting context separately from technical safety.'),
             ('Destination', 'Show the final hostname so you can compare it with the operator you intended to visit.'),
             ('Domain context', 'Show redirects and domain-age context when available.')],
  'safe_steps': ['Check the operator with the gambling regulator that applies to your location.',
                 'Do not assume a site is licensed because it looks professional or uses HTTPS.',
                 'Be cautious if a site avoids identity or age checks where those are legally expected.',
                 'Do not send additional money because a platform says a fee is required to release winnings or withdrawals.'],
  'faqs': [("Does 'no known threat' mean an online casino is trustworthy?",
            'No. It only means the technical threat sources checked did not report a known malware or phishing match. Licensing, fairness, withdrawal and financial risks are separate.'),
           ('Why does the checker show a gambling content warning?',
            'Because real-money gambling is a distinct content and financial-risk category even when the website is not technically malicious.'),
           ('Can the checker verify a gambling license?',
            'Not currently. Licensing depends on jurisdiction and should be checked directly with the relevant regulator.'),
           ('Is a new gambling domain automatically a scam?',
            'No. A recent registration is contextual evidence only. Combine it with licensing checks, exact-domain verification and other warning signs.')],
  'related': ['/scam-warning-signs', '/crypto-investment-scam', '/safe-link-checker', '/methodology'],
  'sources': [('UK Gambling Commission — Illegal online gambling indicators',
               'https://www.gamblingcommission.gov.uk/report/illegal-online-gambling-phase-1-exploring-consumer-pathways-into-using/potential-indicators-of-illegal-gambling-activity-main-findings-illegal'),
              ('UK Gambling Commission — Illegal online gambling research',
               'https://www.gamblingcommission.gov.uk/report/illegal-online-gambling-phase-2-identifying-indicators-of-consumer')]},
 {'path': '/crypto-scam-link-checker',
  'keyword': 'crypto scam link checker',
  'title': 'Crypto Scam Link Checker: Check an Investment or Wallet URL',
  'description': 'Check a crypto, wallet or investment link for domain, redirect and known threat signals before signing in, connecting a wallet or sending cryptocurrency.',
  'h1': 'Check a suspicious crypto or investment link',
  'kicker': 'Crypto & investment safety',
  'answer': 'Do not treat a polished crypto website or displayed account balance as proof that an investment is real. Check the exact domain, then independently research the company before connecting a wallet or sending funds.',
  'why': ['Crypto scams can use fake exchanges, investment dashboards, wallet-support pages, celebrity impersonation or direct messages promising guaranteed returns. Some platforms display invented profits and later demand extra fees before a withdrawal.',
          'Because legitimate crypto services also involve financial risk, the checker separates content category from technical malware and phishing reputation. A technically clean result is not investment advice or proof that a platform is legitimate.'],
  'checks': [('Crypto context', 'Identify known crypto, wallet and financial-service content as a separate category.'),
             ('Domain & redirects', 'Show the exact final domain and whether the link changes website.'),
             ('Known threats', 'Check eligible public URLs for known malware and phishing reports.'),
             ('Domain age', 'Show registration-age context when RDAP data is available.')],
  'safe_steps': ['Never trust guaranteed returns, risk-free profit or pressure to act immediately.',
                 'Research the company independently and check applicable regulatory registrations.',
                 "Do not connect a wallet or approve a transaction merely to 'verify' an account.",
                 'Treat requests to pay crypto in order to unlock, recover or withdraw funds as a major warning sign.'],
  'faqs': [('Can a crypto site be a scam even if Google Web Risk reports nothing?',
            'Yes. Reputation systems are useful for known malicious URLs but cannot determine whether every investment platform is genuine or financially trustworthy.'),
           ('What if someone on WhatsApp or social media sent the investment link?',
            'Unexpected investment coaching through messaging or social platforms deserves strong skepticism. Verify the company independently before sending money.'),
           ('Does a padlock or HTTPS mean a crypto site is legitimate?',
            'No. HTTPS secures the network connection; scammers can also use valid certificates.'),
           ('Should I pay a fee to release crypto profits?',
            'Unexpected taxes, unlock fees, verification deposits or recovery payments demanded before withdrawal are major scam warning signs.')],
  'related': ['/crypto-investment-scam', '/whatsapp-link-checker', '/lookalike-domain-examples', '/scam-warning-signs'],
  'sources': [('FTC — What To Know About Cryptocurrency and Scams',
               'https://consumer.ftc.gov/articles/what-know-about-cryptocurrency-scams'),
              ('FTC — Investment Scams', 'https://consumer.ftc.gov/articles/investment-scams'),
              ('FTC — 2026 investment scam warning',
               'https://consumer.ftc.gov/consumer-alerts/2026/04/people-losing-big-investment-scams-learn-how-spot-and-avoid-them')]}]

STYLE = r"""
<style>
:root{--bg:#0b0d12;--card:#11151d;--soft:#171c26;--text:#f5f7fb;--muted:#a7b0c0;--line:#252b37;--accent:#8ea2ff;--green:#69d6a3;--amber:#f0bf66}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}header{border-bottom:1px solid var(--line);background:rgba(11,13,18,.94);position:sticky;top:0;z-index:5}.nav{max-width:1000px;margin:auto;padding:14px 22px;display:flex;justify-content:space-between;gap:16px;align-items:center}.brand{font-weight:900;color:var(--text)}.button{display:inline-block;padding:9px 12px;border-radius:10px;background:var(--accent);color:#0a0c12;font-weight:900}.button:hover{text-decoration:none;filter:brightness(1.04)}main{max-width:820px;margin:auto;padding:38px 22px 72px}.crumbs{font-size:12px;color:var(--muted);margin-bottom:22px}.kicker{display:inline-block;color:var(--accent);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.09em}h1{font-size:clamp(32px,5vw,52px);line-height:1.04;margin:9px 0 15px;letter-spacing:-.035em}h2{font-size:22px;line-height:1.2;margin:0 0 10px}h3{font-size:16px;line-height:1.3;margin:0 0 5px}p{margin:0 0 14px}.answer{margin:20px 0;padding:18px 19px;border:1px solid color-mix(in srgb,var(--accent) 38%,var(--line));border-radius:16px;background:color-mix(in srgb,var(--accent) 7%,var(--card));font-size:16px}.answer strong{display:block;margin-bottom:5px;color:var(--accent);font-size:11px;letter-spacing:.08em;text-transform:uppercase}.card{margin-top:16px;padding:19px;border:1px solid var(--line);border-radius:16px;background:var(--card)}.check-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:14px}.check{padding:14px;border:1px solid var(--line);border-radius:13px;background:var(--soft)}.check p{font-size:13px;color:var(--muted);margin:0}ul{margin:8px 0 0;padding-left:21px}li+li{margin-top:7px}.limits{border-color:color-mix(in srgb,var(--amber) 32%,var(--line));background:color-mix(in srgb,var(--amber) 5%,var(--card))}.limits strong{color:var(--amber)}.faq details{padding:13px 0;border-top:1px solid var(--line)}.faq details:first-of-type{border-top:0}.faq summary{cursor:pointer;font-weight:850}.faq p{margin:8px 0 0;color:var(--muted)}.related{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:10px}.related a{padding:11px 12px;border:1px solid var(--line);border-radius:11px;background:var(--soft);font-size:12px;font-weight:800}.sources{font-size:12px;color:var(--muted)}.cta{margin-top:24px;padding:22px;border-radius:18px;border:1px solid color-mix(in srgb,var(--accent) 35%,var(--line));background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 10%,var(--card)),var(--card))}.updated{margin-top:24px;color:var(--muted);font-size:11px}footer{border-top:1px solid var(--line);padding:28px 22px;color:var(--muted);text-align:center;font-size:12px}
@media(max-width:650px){.nav{padding:12px 16px}main{padding:30px 16px 60px}.check-grid,.related{grid-template-columns:1fr}h1{font-size:36px}}
</style>
"""

def esc(value: str, attr: bool = False) -> str:
    return html.escape(str(value), quote=attr)

def label_for(path: str) -> str:
    labels = {
        "/phishing-link-checker": "Phishing link checker",
        "/fake-package-delivery-scam": "Fake package delivery scams",
        "/scam-warning-signs": "Scam warning signs",
        "/what-to-do-after-clicking-a-phishing-link": "What to do after clicking",
        "/crypto-investment-scam": "Crypto investment scams",
        "/lookalike-domain-examples": "Lookalike domain examples",
        "/qr-code-link-checker": "QR code link checker",
        "/bank-impersonation-scam": "Bank impersonation scams",
        "/safe-link-checker": "Safe link checker",
        "/phishing-url-signals": "Phishing URL signals",
        "/check-if-link-expires": "Check if a link expires",
        "/email-safety-checker": "Email safety checker",
        "/fake-email-address-signs": "Fake email address signs",
        "/spf-dmarc-email-security": "SPF and DMARC guide",
        "/account-verification-scam": "Account verification scams",
        "/methodology": "Methodology",
        "/whatsapp-link-checker": "WhatsApp link checker",
    }
    return labels.get(path, path.strip("/").replace("-", " ").title())

def faq_schema(page: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in page["faqs"]
        ],
    }

def webpage_schema(page: dict) -> dict:
    canonical = HOST + page["path"]
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["title"],
        "description": page["description"],
        "url": canonical,
        "dateModified": UPDATED,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": HOST},
        "about": [
            {"@type": "Thing", "name": page["keyword"]},
            {"@type": "Thing", "name": "online safety"},
            {"@type": "Thing", "name": "scam prevention"},
        ],
    }

def breadcrumb_schema(page: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": page["h1"], "item": HOST + page["path"]},
        ],
    }

def common_head(page: dict) -> str:
    canonical = HOST + page["path"]
    schemas = [webpage_schema(page), faq_schema(page), breadcrumb_schema(page)]
    schema_html = "".join(
        '<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
        for s in schemas
    )
    return f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'], True)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{esc(canonical, True)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(page['title'], True)}">
<meta property="og:description" content="{esc(page['description'], True)}"><meta property="og:url" content="{esc(canonical, True)}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(page['title'], True)}">
<meta name="twitter:description" content="{esc(page['description'], True)}">
{schema_html}"""

def render(page: dict) -> str:
    checks = "".join(
        f'<article class="check"><h3>{esc(title)}</h3><p>{esc(text)}</p></article>'
        for title, text in page["checks"]
    )
    why = "".join(f"<p>{esc(p)}</p>" for p in page["why"])
    steps = "".join(f"<li>{esc(x)}</li>" for x in page["safe_steps"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in page["faqs"])
    related = "".join(
        f'<a href="{esc(path, True)}">{esc(label_for(path))} →</a>'
        for path in page["related"]
    )
    sources = "".join(
        f'<li><a href="{esc(url, True)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>'
        for label, url in page["sources"]
    )
    return f"""<!doctype html>
<html lang="en" data-page-batch="context-seo-v1">
<head>{common_head(page)}{STYLE}</head>
<body>
<header><nav class="nav" aria-label="Main navigation"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Open safety checker</a></nav></header>
<main>
<div class="crumbs"><a href="/">Home</a> / {esc(page['h1'])}</div>
<span class="kicker">{esc(page['kicker'])}</span>
<h1>{esc(page['h1'])}</h1>
<section class="answer"><strong>At a glance</strong>{esc(page['answer'])}</section>

<section class="card">
<h2>Why this deserves a check</h2>
{why}
</section>

<section class="card">
<h2>What Can I Share This? checks</h2>
<div class="check-grid">{checks}</div>
</section>

<section class="card limits">
<h2>What the result cannot prove</h2>
<p><strong>No scanner can guarantee that a link, sender or website is safe.</strong> A result can report known threats and warning signals, but it cannot prove identity, business legitimacy, licensing, product quality or future behavior. For sensitive actions, verify the organization independently.</p>
</section>

<section class="card">
<h2>Safer next steps</h2>
<ul>{steps}</ul>
</section>

<section class="card faq">
<h2>Frequently asked questions</h2>
{faq}
</section>

<section class="card">
<h2>Related safety guides</h2>
<nav class="related" aria-label="Related safety guides">{related}</nav>
</section>

<section class="card">
<h2>Primary references</h2>
<ul class="sources">{sources}</ul>
</section>

<section class="cta">
<h2>Check it before you trust it</h2>
<p>Paste the suspicious link or email address into the same checker. You will get the destination, available threat signals and a plain-language recommendation without a signup.</p>
<a class="button" href="/">Check a link or email</a>
</section>
<p class="updated">Last reviewed: {UPDATED} · Can I Share This? safety content</p>
</main>
<footer>Can I Share This? · Privacy-first scam and link checking</footer>
</body></html>"""

def add_to_sitemap(paths: list[str]) -> None:
    sitemap = DIST / "sitemap.xml"
    if not sitemap.is_file():
        raise RuntimeError("dist/sitemap.xml not found; run the normal site build first")
    source = sitemap.read_text(encoding="utf-8")
    additions = []
    for path in paths:
        url = HOST + path
        if f"<loc>{url}</loc>" in source:
            continue
        additions.append(f"  <url><loc>{url}</loc><lastmod>{UPDATED}</lastmod></url>")
    if additions:
        if "</urlset>" not in source:
            raise RuntimeError("sitemap.xml does not contain </urlset>")
        source = source.replace("</urlset>", "\n" + "\n".join(additions) + "\n</urlset>", 1)
        sitemap.write_text(source, encoding="utf-8")

def validate_page_data() -> None:
    seen = set()
    for page in PAGES:
        path = page["path"]
        if path in seen:
            raise RuntimeError(f"Duplicate SEO route: {path}")
        seen.add(path)
        if not re.fullmatch(r"/[a-z0-9-]+", path):
            raise RuntimeError(f"Invalid route: {path}")
        if not 35 <= len(page["title"]) <= 65:
            raise RuntimeError(f"Title length out of range for {path}: {len(page['title'])}")
        if not 110 <= len(page["description"]) <= 160:
            raise RuntimeError(f"Description length out of range for {path}: {len(page['description'])}")
        if len(page["faqs"]) < 4 or len(page["checks"]) < 4 or len(page["safe_steps"]) < 4:
            raise RuntimeError(f"Thin page data for {path}")
        if len(set(page["related"])) != len(page["related"]):
            raise RuntimeError(f"Duplicate related link in {path}")

def main() -> None:
    validate_page_data()
    if not DIST.is_dir():
        raise RuntimeError("dist directory not found; run the normal site build first")
    for page in PAGES:
        target = DIST / (page["path"].strip("/") + ".html")
        target.write_text(render(page), encoding="utf-8")
        print("Prepared", target.relative_to(ROOT))
    add_to_sitemap([p["path"] for p in PAGES])
    print(f"Generated {len(PAGES)} context-specific SEO checker pages")

if __name__ == "__main__":
    main()
