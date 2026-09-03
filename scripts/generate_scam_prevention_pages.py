#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOST = 'https://canisharethis.com'
UPDATED = '2026-09-02'

SCAM_PAGES = [
    {
        'path': '/fake-package-delivery-scam',
        'title': 'Fake Package Delivery Scam: Texts, Fees and Tracking Links',
        'description': 'Learn how fake package delivery scams use missed-delivery texts, small redelivery fees and lookalike tracking links, and how to verify a parcel safely.',
        'h1': 'Fake package delivery scams',
        'kicker': 'Delivery scam prevention',
        'quick': 'A delivery message is suspicious when it creates urgency, asks you to pay a small unexpected fee, or sends you to a domain that does not match the carrier you expected. Do not use the message link to verify the parcel. Open the carrier app or website independently and check the tracking number there.',
        'how': [
            'The message usually claims that a parcel could not be delivered, an address needs confirmation, customs or redelivery charges are due, or a package is waiting. The amount requested may be small so the payment feels routine.',
            'The link can lead to a convincing copy of a carrier or postal website. The goal may be to collect card details, account credentials, personal information or payment through a fraudulent checkout.'
        ],
        'red_flags': [
            'You were not expecting the parcel or the timing does not make sense.',
            'The message demands immediate action to avoid return, cancellation or extra fees.',
            'The visible carrier name does not match the real domain after you inspect the link.',
            'The page asks for card details, passwords or identity information for a minor delivery issue.',
            'The sender uses a shortened link, unusual domain or unrelated hostname.'
        ],
        'verify': [
            'Do not tap the message link. Open the official carrier app, type the known carrier website yourself, or use a tracking number from the merchant order page. If the parcel is genuine, the delivery status should exist independently of the message.',
            'If you received a link, paste the URL or sender address into Can I Share This? before opening it. A low-risk technical result does not replace checking the parcel through the official carrier.'
        ],
        'after': 'If you entered card details, contact the card issuer promptly and monitor transactions. If you entered a password, change it on the real service and anywhere the same password was reused. If you only opened the page, close it and avoid downloading or installing anything it offered.',
        'sources': [
            ('FTC — How To Recognize and Avoid Phishing Scams', 'https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams'),
            ('CISA — Recognize and Report Phishing', 'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing'),
        ],
        'related': ['/scam-warning-signs', '/what-to-do-after-clicking-a-phishing-link', '/phishing-url-signals'],
    },
    {
        'path': '/advance-fee-scam',
        'title': 'Advance-Fee Scam: Inheritance, Prince, Lottery and Frozen-Funds Scams',
        'description': 'Understand advance-fee scams involving inheritance, royal or diplomatic stories, lotteries, frozen funds and repeated fees before a promised payout.',
        'h1': 'Advance-fee scams',
        'kicker': 'Upfront-payment scam',
        'quick': 'An advance-fee scam promises money, access, a prize, inheritance, investment return or financial help, but requires you to pay first. The story can involve a prince, royal family, lawyer, diplomat, lottery, inheritance, frozen bank account or loan. The recurring pattern is the important part: money is promised later, while real money is demanded now.',
        'how': [
            'The scammer creates a high-value opportunity and gives a reason the funds cannot be released normally. A fee is introduced for taxes, legal documents, insurance, customs, transfer charges, anti-money-laundering clearance or another invented obstacle.',
            'After one payment, another problem often appears. The promised payout remains just out of reach while the victim is asked for additional fees or personal documents.'
        ],
        'red_flags': [
            'An unsolicited stranger says you are entitled to a large sum, prize or inheritance.',
            'You must pay taxes, processing, legal or transfer fees before receiving the money.',
            'The sender asks for secrecy or claims normal banking procedures cannot be used.',
            'The story relies on impressive titles, officials, lawyers, diplomats or royal connections without independent verification.',
            'Payment is requested through wire transfer, crypto, gift cards or another hard-to-reverse method.'
        ],
        'verify': [
            'Do not verify the story using phone numbers, documents or websites supplied only by the sender. Independently identify the alleged institution, lawyer, lottery or bank and contact it through public official channels.',
            'Real institutions can charge legitimate fees in some circumstances, but an unexpected promise of a large payment combined with pressure to send money first is a major warning pattern.'
        ],
        'after': 'Stop additional payments and preserve messages, receipts, wallet addresses and transaction references. Contact the bank, payment provider or exchange used for the transfer immediately. Report the fraud to the relevant national authority and do not pay a second person who promises to recover the money for another upfront fee.',
        'sources': [
            ('FTC — What To Know About Advance-Fee Loans', 'https://consumer.ftc.gov/articles/what-know-about-advance-fee-loans'),
            ('FTC — Impersonator Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams'),
        ],
        'related': ['/gift-card-scam', '/crypto-investment-scam', '/how-to-report-a-scam'],
    },
    {
        'path': '/bank-impersonation-scam',
        'title': 'Bank Impersonation Scam: Fake Fraud Alerts and Security Calls',
        'description': 'Learn how bank impersonation scams use fake fraud alerts, caller ID, urgent transfers and verification requests, and how to contact your bank safely.',
        'h1': 'Bank impersonation scams',
        'kicker': 'Financial impersonation',
        'quick': 'A bank impersonation scam makes you believe your account or card is under immediate threat, then directs you to transfer money, reveal codes, install software or use a link supplied by the caller. End the contact and reach your bank through the number on your card, official app or independently typed website.',
        'how': [
            'The scam can begin with a text about a suspicious payment, a call from someone claiming to be the fraud department, or a message telling you that an account needs urgent security verification. Caller ID and sender names can be misleading.',
            'The attacker may already know basic personal information and use it to sound credible. The objective is usually to obtain authentication codes, card details, account access or a transfer that the victim authorizes under pressure.'
        ],
        'red_flags': [
            'You are told to move money to a safe, secure or temporary account.',
            'The caller asks for a one-time code, password, PIN or full card details.',
            'You are told not to hang up, not to contact anyone else, or to keep the case secret.',
            'A link in a text or email is presented as the only way to stop fraud.',
            'The caller wants remote access to your phone or computer.'
        ],
        'verify': [
            'End the call or message. Open the official banking app yourself or call the number printed on the physical card. Do not use a phone number, link or QR code provided by the suspicious contact.',
            'Check recent transactions independently. If the bank really needs action, its official channels should show the problem or allow you to reach a verified fraud team.'
        ],
        'after': 'If you shared codes, credentials or approved a transfer, contact the bank immediately and explain that you may have been manipulated by an impersonator. Ask about account protection, card replacement and transfer recall options. Change compromised passwords and review other accounts that reused them.',
        'sources': [
            ('FTC — Impersonator Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams'),
            ('FTC — Business Impersonator Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams/business-impersonator-scams'),
        ],
        'related': ['/account-verification-scam', '/scam-warning-signs', '/what-to-do-if-you-gave-a-scammer-your-password'],
    },
    {
        'path': '/account-verification-scam',
        'title': 'Account Verification Scam: Fake Security and Login Messages',
        'description': 'Spot fake account verification messages that imitate PayPal, Microsoft, Google, Amazon, Netflix and other services to steal logins or payment details.',
        'h1': 'Account verification scams',
        'kicker': 'Fake security alert',
        'quick': 'A fake account-verification message claims that your account is locked, suspended, compromised or needs confirmation, then sends you to a login page controlled by someone else. Instead of using the link, open the real app or type the service address yourself and check whether the warning exists there.',
        'how': [
            'The message may imitate a familiar service and mention a failed payment, unusual login, password expiry, account suspension or required identity check. The destination often copies the genuine login page closely.',
            'Once credentials are entered, the attacker can capture the password and sometimes request a one-time code as a second step. Some pages also collect card details or identity documents.'
        ],
        'red_flags': [
            'An unexpected message says immediate verification is required to avoid losing access.',
            'The link uses a misspelled brand, added security words or an unrelated domain.',
            'The page asks for more information than the service normally requests during login.',
            'Your password manager does not recognize the domain where the login form appears.',
            'The message asks you to reply with a code or send a screenshot of a verification prompt.'
        ],
        'verify': [
            'Open the service through a trusted bookmark or official app. Check account notifications, security activity and billing there. Do not rely on branding, logos or HTTPS alone.',
            'Paste the suspicious URL or sender email into Can I Share This? to inspect domain and sender warning signs before interacting with the message.'
        ],
        'after': 'If you submitted a password, change it immediately on the real service and revoke unfamiliar sessions. If the same password was reused elsewhere, change those accounts too. If you shared a one-time code, recovery code or financial information, treat the account as potentially compromised and contact the provider.',
        'sources': [
            ('FTC — How To Recognize and Avoid Phishing Scams', 'https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams'),
            ('CISA — Recognize and Report Phishing', 'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing'),
        ],
        'related': ['/what-to-do-if-you-gave-a-scammer-your-password', '/phishing-url-signals', '/lookalike-domain-examples'],
    },
    {
        'path': '/romance-scam',
        'title': 'Romance Scam: Online Relationship Warning Signs',
        'description': 'Learn how romance scams build trust over time, why requests for money or investment are dangerous, and how to verify an online relationship independently.',
        'h1': 'Romance scams',
        'kicker': 'Relationship scam prevention',
        'quick': 'A romance scam uses emotional trust to make financial requests feel personal and urgent. The relationship may develop over weeks or months before money, crypto, travel costs, medical emergencies or investment opportunities appear. Never send money or financial credentials to an online romantic interest you have not independently verified.',
        'how': [
            'The person may contact you through dating apps or social media, move the conversation to private messaging, communicate frequently and create a believable reason they cannot meet. The emotional investment is part of the fraud mechanism.',
            'Requests can begin with a small emergency and escalate. Some romance scams transition into cryptocurrency or investment schemes where the victim is directed to a fake platform.'
        ],
        'red_flags': [
            'The relationship becomes intense unusually quickly while in-person meetings repeatedly fail.',
            'There is a recurring emergency involving travel, medical care, military service, customs or frozen funds.',
            'You are asked to send money, crypto, gift cards, banking help or receive funds on someone else’s behalf.',
            'The person pressures you to keep the relationship or financial request private.',
            'They introduce an investment opportunity and coach you through deposits.'
        ],
        'verify': [
            'Slow the interaction down and discuss it with someone you trust. Search independently for the person’s claimed organization or profession and use reverse-image tools where appropriate to see whether profile photos appear under different identities.',
            'Do not treat a video call as complete proof of identity or trustworthiness. Financial requests should be evaluated separately from the emotional relationship.'
        ],
        'after': 'Stop sending money, preserve the conversation and transaction records, and contact the payment provider. Report the profile to the platform and the fraud to the appropriate authority. Be alert for recovery scammers who contact victims after a loss and promise to retrieve funds for another payment.',
        'sources': [
            ('FTC — What To Know About Romance Scams', 'https://consumer.ftc.gov/articles/what-know-about-romance-scams'),
            ('FTC — Romance Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams/romance-scams'),
        ],
        'related': ['/crypto-investment-scam', '/gift-card-scam', '/how-to-report-a-scam'],
    },
    {
        'path': '/job-offer-scam',
        'title': 'Job Offer Scam: Fake Recruiters, Remote Work and Task Scams',
        'description': 'Spot fake job offers, recruiter messages, task scams, fake checks and jobs that require you to pay before getting paid.',
        'h1': 'Job offer scams',
        'kicker': 'Employment scam prevention',
        'quick': 'A job scam often promises easy remote work, unusually high pay or quick hiring, then asks for money, crypto, equipment payments, banking information or paid tasks. A legitimate job should not require you to send money in order to receive wages.',
        'how': [
            'Fake recruiters can imitate real companies, use copied job descriptions and conduct interviews by text or messaging apps. Some send counterfeit checks for equipment and ask the victim to forward part of the money elsewhere.',
            'Task scams show fake earnings for simple online actions and later require the worker to deposit personal funds, often in cryptocurrency, before supposedly unlocking commissions or withdrawals.'
        ],
        'red_flags': [
            'The recruiter contacts you unexpectedly with little detail about the actual role.',
            'Hiring happens extremely quickly without normal interviews or verification.',
            'You must pay for training, equipment, software, deposits or access to tasks.',
            'A check is sent with instructions to buy equipment or send money onward.',
            'You are asked to receive packages, move money or use your personal bank account for company transactions.'
        ],
        'verify': [
            'Find the employer’s official careers page independently and check whether the role exists. Contact the company using an address or phone number from its official website rather than details supplied by the recruiter.',
            'Check the sender domain carefully. A real company name in the display name does not make a free-mail address or lookalike domain legitimate.'
        ],
        'after': 'If you sent money or deposited a suspicious check, contact your bank or payment provider immediately. If you shared identity documents or tax information, monitor for identity misuse. Report the fake recruiter profile and preserve job ads, email headers and payment instructions.',
        'sources': [
            ('FTC — Job Scams', 'https://consumer.ftc.gov/articles/job-scams'),
            ('FTC — How to Spot and Avoid Task Scams', 'https://consumer.ftc.gov/consumer-alerts/2025/08/how-spot-avoid-task-scams'),
        ],
        'related': ['/scam-warning-signs', '/crypto-investment-scam', '/how-to-report-a-scam'],
    },
    {
        'path': '/marketplace-scam',
        'title': 'Marketplace Scam: Fake Buyers, Sellers and Payment Links',
        'description': 'Learn how marketplace scams use fake payment confirmations, off-platform links, shipping tricks and account impersonation on resale platforms.',
        'h1': 'Marketplace scams',
        'kicker': 'Buying and selling safely',
        'quick': 'A marketplace scam moves trust away from the platform’s normal protections. The buyer or seller may send a fake payment page, claim you must pay a fee to receive money, request off-platform contact or use a counterfeit confirmation email. Keep payment and messaging inside the marketplace whenever possible.',
        'how': [
            'A fake buyer can claim that payment is pending and send a link asking the seller to enter card details or pay an upgrade fee. A fake seller can request bank transfer, crypto or another payment method that bypasses platform dispute systems.',
            'Scammers may also send counterfeit emails that resemble marketplace notifications, or use stolen accounts with good history to appear more credible.'
        ],
        'red_flags': [
            'The other person insists on moving immediately to WhatsApp, SMS or email.',
            'You receive a payment link instead of seeing the transaction inside the platform.',
            'You are told to pay money in order to receive money from a buyer.',
            'The seller refuses protected payment and demands bank transfer, crypto or gift cards.',
            'The deal becomes urgent because another buyer, courier or supposed support agent is waiting.'
        ],
        'verify': [
            'Open the marketplace app or website directly and verify the order, payment and shipping status there. Do not rely on screenshots or emails alone.',
            'If a link claims to be a marketplace payment page, inspect the real domain before entering card information. A lookalike page can copy the platform design while using an unrelated hostname.'
        ],
        'after': 'If card details or account credentials were entered on a fake page, contact the issuer and change the marketplace password. Report the account and listing to the platform. Keep transaction messages and shipping information in case a dispute or fraud report is needed.',
        'sources': [
            ('FTC — Online Shopping', 'https://consumer.ftc.gov/articles/online-shopping'),
            ('FTC — Business Impersonator Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams/business-impersonator-scams'),
        ],
        'related': ['/account-verification-scam', '/fake-package-delivery-scam', '/what-to-do-if-you-gave-a-scammer-your-password'],
    },
    {
        'path': '/tech-support-scam',
        'title': 'Tech Support Scam: Fake Virus Alerts and Remote-Access Calls',
        'description': 'Spot fake Microsoft, Apple and antivirus support warnings that request remote access, payments or software installation.',
        'h1': 'Tech support scams',
        'kicker': 'Fake computer support',
        'quick': 'A tech-support scam claims that your device has a virus, security problem or account issue, then asks you to call a number, install remote-access software or pay for unnecessary service. Unexpected support contacts should not be trusted because they display a familiar company name or logo.',
        'how': [
            'The scam may start with a browser pop-up, search result, phone call, email or text. The operator creates urgency and may ask to control the computer remotely so they can show harmless system information as evidence of infection.',
            'Remote access can expose files, passwords and financial accounts. The scammer may also request payment for fake repairs or manipulate the victim into logging into online banking.'
        ],
        'red_flags': [
            'A pop-up says you must call a phone number to remove a virus.',
            'An unsolicited caller claims to be Microsoft, Apple, your ISP or antivirus support.',
            'You are asked to install remote-control software before the issue is independently verified.',
            'The technician wants payment by gift card, crypto, wire transfer or another unusual method.',
            'You are told to log into banking while the remote session is active.'
        ],
        'verify': [
            'Close the browser or end the call. If you need support, open the vendor’s official website yourself and use the support channel published there. Do not call a number that appeared only in a warning pop-up.',
            'Use the operating system’s built-in security tools or a trusted security product to run a scan if you are concerned about malware.'
        ],
        'after': 'If remote access was granted, disconnect the device from the network, end the remote session and remove unfamiliar remote-control software. Change important passwords from a trusted device and contact financial institutions if banking was accessed during the session.',
        'sources': [
            ('FTC — How To Spot, Avoid, and Report Tech Support Scams', 'https://consumer.ftc.gov/articles/how-spot-avoid-and-report-tech-support-scams'),
            ('FTC — Tech Support Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams/tech-support-scams'),
        ],
        'related': ['/gift-card-scam', '/what-to-do-if-you-gave-a-scammer-your-password', '/how-to-report-a-scam'],
    },
    {
        'path': '/crypto-investment-scam',
        'title': 'Crypto Investment Scam: Fake Platforms, Profits and Recovery Schemes',
        'description': 'Learn how fake crypto investment platforms display invented profits, pressure victims to deposit more and demand fees before withdrawals.',
        'h1': 'Crypto investment scams',
        'kicker': 'Investment scam prevention',
        'quick': 'A crypto investment scam can show convincing dashboards and fake profits while the victim’s real cryptocurrency is controlled by the scammer. A common warning sign is being told to deposit more money, pay tax or unlock fees before a withdrawal can be processed.',
        'how': [
            'The scheme may begin through social media, a romance relationship, a messaging group, a fake celebrity endorsement or an unsolicited investment expert. The victim is guided to a website or app that appears to show successful trades.',
            'Small withdrawals may sometimes be allowed to build confidence. Larger withdrawals can then be blocked while the platform demands additional deposits, taxes, verification payments or liquidity fees.'
        ],
        'red_flags': [
            'Guaranteed or unusually consistent returns are promised with little explanation of risk.',
            'A stranger personally coaches you through buying and transferring cryptocurrency.',
            'The platform is accessible only through a link or app supplied by the promoter.',
            'Withdrawals require new payments, taxes or deposits before funds can be released.',
            'Someone later offers to recover lost crypto for an upfront fee.'
        ],
        'verify': [
            'Research the company independently, including the legal entity, regulator where applicable and domain history. Do not rely on reviews or certificates shown only on the investment website.',
            'Never use a wallet address merely because a stranger says it belongs to an exchange, investment account or recovery service. Crypto transfers are difficult to reverse once confirmed.'
        ],
        'after': 'Stop sending additional funds and preserve wallet addresses, transaction hashes, chat logs and website details. Contact the exchange or service used to purchase or transfer the crypto and report the incident to the appropriate financial or cybercrime authority. Ignore unsolicited recovery offers.',
        'sources': [
            ('FTC — Cryptocurrency Scams', 'https://consumer.ftc.gov/articles/what-know-about-cryptocurrency-and-scams'),
            ('FBI IC3 — Crime Information', 'https://www.ic3.gov/CrimeInfo'),
        ],
        'related': ['/romance-scam', '/advance-fee-scam', '/how-to-report-a-scam'],
    },
    {
        'path': '/gift-card-scam',
        'title': 'Gift Card Scam: Why Scammers Demand Gift Card Numbers',
        'description': 'Learn why urgent demands for gift cards are a major scam warning sign and what to do if you already shared a gift card number or PIN.',
        'h1': 'Gift card scams',
        'kicker': 'Payment scam prevention',
        'quick': 'Gift cards are designed for purchases and gifts, not for paying banks, government agencies, tech support, employers, utilities, prizes or online romantic interests. A person who demands gift-card numbers or PINs as payment is giving you a strong scam warning sign.',
        'how': [
            'The scammer creates an urgent reason for payment and tells the victim exactly which cards to buy. After purchase, the victim is instructed to read the card number and PIN or send a photo of the card.',
            'Once those codes are shared, the value can be transferred or spent quickly. The surrounding story varies, but the unusual payment method is the common warning pattern.'
        ],
        'red_flags': [
            'A government agency, bank, employer or support technician asks for gift cards.',
            'A prize, debt, fine, utility bill or emergency must supposedly be paid immediately with cards.',
            'The person stays on the phone while you travel to a store and buy the cards.',
            'You are told to scratch the back and send the code or a photo.',
            'The caller warns you not to tell the cashier why you are buying the cards.'
        ],
        'verify': [
            'Stop before buying or sharing any card code. Contact the organization or person independently using a known number or official website. Legitimate businesses may sell or accept gift cards for normal purchases, but that is different from demanding card codes to resolve an emergency.',
            'If someone claims to be a relative or friend in trouble, contact that person through a number or account you already know.'
        ],
        'after': 'Contact the gift-card issuer immediately and keep the card and receipt. Some issuers may be able to freeze remaining value if reported quickly. Report the scam and preserve the messages or phone details used to demand payment.',
        'sources': [
            ('FTC — Avoiding and Reporting Gift Card Scams', 'https://consumer.ftc.gov/articles/avoiding-and-reporting-gift-card-scams'),
            ('FTC — Impersonator Scams', 'https://consumer.ftc.gov/features/pass-it-on/impersonator-scams'),
        ],
        'related': ['/tech-support-scam', '/advance-fee-scam', '/how-to-report-a-scam'],
    },
]

SAFETY_PAGES = [
    {
        'path': '/what-to-do-after-clicking-a-phishing-link',
        'title': 'Clicked a Phishing Link? What To Do Next',
        'description': 'Clicked a suspicious or phishing link? Use a practical response checklist for passwords, downloads, browser prompts, payments and account security.',
        'h1': 'What to do after clicking a phishing link',
        'kicker': 'After-click response',
        'quick': 'Clicking a suspicious link does not automatically mean your device or account is compromised. The next steps depend on what happened after the click. Close the page, do not download or install anything, and act quickly if you entered credentials, payment details or security codes.',
        'steps': [
            ('1. Close the page and stop interacting', 'Do not continue through warnings, downloads, login prompts or payment forms. If a file downloaded automatically, do not open it until you know what it is.'),
            ('2. Identify what information you entered', 'A click alone is different from submitting a password, card number, one-time code or identity document. Write down what you provided so you can protect the affected accounts.'),
            ('3. Change compromised credentials from the real service', 'If you entered a password, open the genuine service independently, change the password and review active sessions. Reused passwords should be changed on other accounts too.'),
            ('4. Check the device if software was installed', 'If you installed an app, browser extension, configuration profile or executable from the suspicious page, disconnect if necessary, remove unfamiliar software and run trusted security scans.'),
            ('5. Contact financial providers when money or card data is involved', 'If card or banking information was submitted, contact the issuer through its official number and explain that the details may have been captured by a phishing page.'),
        ],
        'sources': [
            ('CISA — Recognize and Report Phishing', 'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing'),
            ('FTC — How To Recognize and Avoid Phishing Scams', 'https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams'),
        ],
        'related': ['/what-to-do-if-you-gave-a-scammer-your-password', '/how-to-report-a-scam', '/scam-warning-signs'],
    },
    {
        'path': '/what-to-do-if-you-gave-a-scammer-your-password',
        'title': 'Gave a Scammer Your Password? Secure the Account Now',
        'description': 'What to do if you entered your password on a fake site: change credentials, end sessions, secure recovery methods and protect reused accounts.',
        'h1': 'What to do if you gave a scammer your password',
        'kicker': 'Account recovery',
        'quick': 'Change the password on the real service immediately, end unfamiliar sessions, verify recovery email and phone details, and change any other account that reused the same password. If a one-time code or recovery code was also shared, treat the account as potentially compromised even if the password has already been changed.',
        'steps': [
            ('1. Use the real app or website', 'Do not return through the suspicious message. Open the service from a trusted bookmark, official app or address you type yourself.'),
            ('2. Change the password', 'Choose a unique password that is not reused on another service. If the account no longer lets you sign in, use the provider’s official recovery process.'),
            ('3. End active sessions and review recent activity', 'Sign out unfamiliar devices or sessions, check recent security events and remove app passwords or connected applications you do not recognize.'),
            ('4. Check recovery methods and multi-factor authentication', 'Confirm that recovery email addresses, phone numbers and authentication methods still belong to you. Replace exposed recovery codes.'),
            ('5. Protect accounts that reused the password', 'Credential reuse lets one stolen password affect multiple services. Change any other account that used the same or a closely related password.'),
        ],
        'sources': [
            ('CISA — Use Strong Passwords', 'https://www.cisa.gov/secure-our-world/use-strong-passwords'),
            ('FTC — How To Recognize and Avoid Phishing Scams', 'https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams'),
        ],
        'related': ['/what-to-do-after-clicking-a-phishing-link', '/account-verification-scam', '/how-to-report-a-scam'],
    },
    {
        'path': '/how-to-report-a-scam',
        'title': 'How To Report a Scam and Preserve Useful Evidence',
        'description': 'Learn what to save, who to contact first and how to report scams to payment providers, platforms and national fraud or cybercrime authorities.',
        'h1': 'How to report a scam',
        'kicker': 'Fraud reporting guide',
        'quick': 'If money, credentials or personal information were exposed, protect the account or payment method first. Then preserve useful evidence and report the incident to the relevant platform, financial provider and national fraud or cybercrime authority. Reporting routes differ by country, so use official government or police resources for your location.',
        'steps': [
            ('1. Protect money and accounts first', 'Contact the bank, card issuer, exchange, marketplace or payment provider through an official channel. Ask what can be frozen, recalled, disputed or secured.'),
            ('2. Preserve evidence', 'Keep screenshots, sender addresses, phone numbers, URLs, transaction references, wallet addresses, usernames and timestamps. Do not keep interacting with the scammer just to collect more evidence.'),
            ('3. Report the account or content to the platform', 'Email providers, social networks, marketplaces, dating apps and messaging services can investigate accounts and remove malicious content when reports contain enough context.'),
            ('4. Use the official fraud-reporting channel for your country', 'Government, police and national cybercrime reporting systems vary by jurisdiction. Search for the official public service rather than using a recovery company that contacts you unsolicited.'),
            ('5. Watch for recovery scams', 'Victim lists can be reused. A second scammer may promise to recover lost money, crypto or accounts for an upfront fee. Treat unsolicited recovery offers as another warning sign.'),
        ],
        'sources': [
            ('FTC — ReportFraud', 'https://reportfraud.ftc.gov/'),
            ('FBI IC3 — Internet Crime Complaint Center', 'https://www.ic3.gov/'),
        ],
        'related': ['/scam-warning-signs', '/what-to-do-after-clicking-a-phishing-link', '/advance-fee-scam'],
    },
    {
        'path': '/scam-warning-signs',
        'title': 'Scam Warning Signs: A Practical Checklist Before You Act',
        'description': 'Use a practical scam warning-sign checklist for urgency, impersonation, unusual payments, suspicious links, secrecy and requests for sensitive information.',
        'h1': 'Common scam warning signs',
        'kicker': 'Scam prevention checklist',
        'quick': 'Scams use different stories but repeat many of the same pressure patterns: unexpected contact, urgency, impersonation, secrecy, unusual payment methods, requests for passwords or codes, and links that do not match the organization being claimed. One sign is not proof, but several together should make you stop and verify independently.',
        'steps': [
            ('Unexpected contact', 'A message, call or social-media approach arrives without a normal reason and quickly asks you to take action.'),
            ('Urgency or fear', 'You are told an account will close, a parcel will be returned, a payment will fail, police action is coming or an opportunity will disappear unless you act immediately.'),
            ('Impersonation', 'The sender claims to be a bank, employer, government agency, marketplace, delivery company, relative or major technology company.'),
            ('Unusual payment method', 'Gift cards, crypto, wire transfers or payments to a “safe account” are requested instead of a normal commercial process.'),
            ('Sensitive information', 'The person asks for passwords, one-time codes, recovery codes, identity documents or full card information.'),
            ('Secrecy and isolation', 'You are told not to contact the bank, employer, family member, cashier or another person who could challenge the story.'),
            ('Suspicious link or sender', 'The visible brand does not match the actual domain, the address is a lookalike, or a short link hides the destination.'),
        ],
        'sources': [
            ('FTC — Scams', 'https://consumer.ftc.gov/scams'),
            ('CISA — Recognize and Report Phishing', 'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing'),
        ],
        'related': ['/fake-package-delivery-scam', '/bank-impersonation-scam', '/account-verification-scam'],
    },
]

ALL_PATHS = ['/scam-prevention'] + [p['path'] for p in SCAM_PAGES] + [p['path'] for p in SAFETY_PAGES]
assert len(ALL_PATHS) == 15
assert len(set(ALL_PATHS)) == len(ALL_PATHS)


def esc(value: object, quote: bool = False) -> str:
    return html.escape(str(value), quote=quote)


def json_ld(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def common_head(title: str, description: str, canonical: str, kind: str = 'Article') -> str:
    data = {
        '@context': 'https://schema.org',
        '@type': kind,
        'headline' if kind == 'Article' else 'name': title,
        'description': description,
        'url': canonical,
        'datePublished': UPDATED,
        'dateModified': UPDATED,
        'author': {'@type': 'Organization', 'name': 'Can I Share This?', 'url': HOST + '/'},
        'publisher': {'@type': 'Organization', 'name': 'Can I Share This?', 'url': HOST + '/'},
        'isPartOf': {'@type': 'WebSite', 'name': 'Can I Share This?', 'url': HOST + '/'},
    }
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description, True)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{esc(canonical, True)}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(title, True)}"><meta property="og:description" content="{esc(description, True)}"><meta property="og:url" content="{esc(canonical, True)}"><meta name="twitter:card" content="summary"><script type="application/ld+json">{json_ld(data)}</script>'''


STYLE = '''<style>:root{color-scheme:light dark;--bg:#f6f7f9;--card:#fff;--text:#17191d;--muted:#68717d;--line:#e2e6eb;--soft:#f1f3f6;--accent:#17191d;--accentText:#fff;--warn:#8c5b00;--shadow:0 12px 34px rgba(17,24,39,.055)}@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--soft:#1c2026;--accent:#f4f5f7;--accentText:#111318;--warn:#f1bd5b;--shadow:0 14px 34px rgba(0,0,0,.23)}}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.68 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}a{color:inherit}header{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(9px);border-bottom:1px solid var(--line)}.nav{max-width:1040px;margin:auto;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px}.brand{font-weight:850;text-decoration:none;letter-spacing:-.02em}.button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:9px 15px;border-radius:11px;background:var(--accent);color:var(--accentText);text-decoration:none;font-weight:800}main{max-width:900px;margin:auto;padding:36px 20px 70px}.crumbs{color:var(--muted);font-size:13px;margin-bottom:18px}.kicker{display:inline-block;border:1px solid var(--line);border-radius:999px;background:var(--card);padding:5px 9px;color:var(--muted);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}h1{font-size:clamp(34px,7vw,58px);line-height:1.03;letter-spacing:-.045em;margin:13px 0 21px;text-wrap:balance}.quick,.card,.after{border:1px solid var(--line);background:var(--card);border-radius:18px;box-shadow:var(--shadow)}.quick{padding:clamp(20px,4vw,30px);font-size:clamp(17px,2.4vw,20px);margin-bottom:15px}.quick:before{content:"Quick answer";display:block;color:var(--warn);font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}.card{padding:clamp(19px,3.4vw,28px);margin:13px 0}.after{padding:20px 22px;margin:13px 0}.after strong{display:block;margin-bottom:6px}h2{font-size:clamp(22px,3.5vw,28px);line-height:1.2;letter-spacing:-.025em;margin:0 0 12px}h3{line-height:1.3}.card p{margin:0 0 13px}.card p:last-child{margin-bottom:0}.flags{margin:0;padding-left:20px}.flags li{margin:8px 0}.section-title{margin:32px 0 10px}.section-title span{color:var(--muted);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}.section-title h2{margin:3px 0 0}.sources{margin:0;padding-left:20px}.sources li{margin:8px 0}.related-grid,.hub-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.related{position:relative;display:flex;flex-direction:column;gap:4px;padding:16px 36px 16px 16px;border:1px solid var(--line);border-radius:15px;background:var(--card);text-decoration:none}.related span{font-size:13px;color:var(--muted);line-height:1.45}.related b{position:absolute;right:14px;top:14px}.cta{margin-top:28px;padding:24px;border:1px solid var(--line);border-radius:18px;background:var(--card);text-align:center}.cta h2{margin:0 0 7px}.cta p{margin:8px 0}.steps{display:grid;gap:10px}.step{padding:18px 20px;border:1px solid var(--line);border-radius:15px;background:var(--card)}.step h2{font-size:19px;margin:0 0 6px}.step p{margin:0;color:var(--muted)}footer{border-top:1px solid var(--line);padding:22px;text-align:center;color:var(--muted);font-size:13px}@media(max-width:700px){main{padding:28px 15px 55px}.nav{padding:10px 15px}h1{font-size:clamp(33px,11vw,46px)}.quick,.card{border-radius:16px}.related-grid,.hub-grid{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}</style>'''


def related_cards(paths: list[str]) -> str:
    labels = {p['path']: p['h1'] for p in SCAM_PAGES + SAFETY_PAGES}
    labels['/scam-prevention'] = 'Scam prevention center'
    labels['/'] = 'Safety checker'
    labels['/phishing-url-signals'] = 'Phishing URL signals'
    labels['/lookalike-domain-examples'] = 'Lookalike domain examples'
    return ''.join(f'<a class="related" href="{esc(path, True)}"><strong>{esc(labels.get(path, path.strip("/").replace("-", " ").title()))}</strong><span>Read the prevention guide and verify suspicious messages independently.</span><b aria-hidden="true">→</b></a>' for path in paths)


def render_scam(page: dict) -> str:
    canonical = HOST + page['path']
    how = ''.join(f'<p>{esc(p)}</p>' for p in page['how'])
    flags = ''.join(f'<li>{esc(x)}</li>' for x in page['red_flags'])
    verify = ''.join(f'<p>{esc(p)}</p>' for p in page['verify'])
    sources = ''.join(f'<li><a href="{esc(url, True)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>' for label, url in page['sources'])
    return f'''<!doctype html><html lang="en"><head>{common_head(page['title'], page['description'], canonical)}{STYLE}</head><body><header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link or email</a></div></header><main><div class="crumbs"><a href="/">Home</a> / <a href="/scam-prevention">Scam Prevention</a></div><span class="kicker">{esc(page['kicker'])}</span><h1>{esc(page['h1'])}</h1><section class="quick">{esc(page['quick'])}</section><section class="card"><h2>How this scam usually works</h2>{how}</section><section class="card"><h2>Warning signs</h2><ul class="flags">{flags}</ul></section><section class="card"><h2>How to verify the situation safely</h2>{verify}</section><section class="after"><strong>If you already acted</strong>{esc(page['after'])}</section><div class="section-title"><span>Sources</span><h2>Primary prevention references</h2></div><section class="card"><ul class="sources">{sources}</ul></section><div class="section-title"><span>Related</span><h2>Continue checking</h2></div><nav class="related-grid">{related_cards(page['related'])}</nav><section class="cta"><h2>Received a suspicious message?</h2><p>Paste its link or sender email address into Can I Share This? before you trust it.</p><p><a class="button" href="/">Analyze it</a></p></section></main><footer>Can I Share This? · Scam prevention and safety checking</footer></body></html>'''


def render_safety(page: dict) -> str:
    canonical = HOST + page['path']
    steps = ''.join(f'<article class="step"><h2>{esc(title)}</h2><p>{esc(text)}</p></article>' for title, text in page['steps'])
    sources = ''.join(f'<li><a href="{esc(url, True)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>' for label, url in page['sources'])
    return f'''<!doctype html><html lang="en"><head>{common_head(page['title'], page['description'], canonical)}{STYLE}</head><body><header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Open safety checker</a></div></header><main><div class="crumbs"><a href="/">Home</a> / <a href="/scam-prevention">Scam Prevention</a></div><span class="kicker">{esc(page['kicker'])}</span><h1>{esc(page['h1'])}</h1><section class="quick">{esc(page['quick'])}</section><section class="steps">{steps}</section><div class="section-title"><span>Sources</span><h2>Primary prevention references</h2></div><section class="card"><ul class="sources">{sources}</ul></section><div class="section-title"><span>Related</span><h2>Continue checking</h2></div><nav class="related-grid">{related_cards(page['related'])}</nav><section class="cta"><h2>Check suspicious links and sender addresses</h2><p>Use the same homepage field for a URL or email address.</p><p><a class="button" href="/">Analyze it</a></p></section></main><footer>Can I Share This? · Scam prevention and safety checking</footer></body></html>'''


def render_hub() -> str:
    title = 'Scam Prevention Center — Common Scams, Warning Signs and What To Do'
    description = 'Practical guides to recognize delivery, bank, account, romance, job, marketplace, tech-support and crypto scams before you act.'
    canonical = HOST + '/scam-prevention'
    scam_cards = ''.join(f'<a class="related" href="{esc(p["path"], True)}"><strong>{esc(p["h1"])}</strong><span>{esc(p["description"])}</span><b aria-hidden="true">→</b></a>' for p in SCAM_PAGES)
    safety_cards = ''.join(f'<a class="related" href="{esc(p["path"], True)}"><strong>{esc(p["h1"])}</strong><span>{esc(p["description"])}</span><b aria-hidden="true">→</b></a>' for p in SAFETY_PAGES)
    return f'''<!doctype html><html lang="en"><head>{common_head(title, description, canonical, 'WebPage')}{STYLE}</head><body><header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link or email</a></div></header><main><div class="crumbs"><a href="/">Home</a> / Scam Prevention</div><span class="kicker">Prevention library</span><h1>Scam prevention center</h1><section class="quick">Scams change their story, but many reuse the same pressure techniques: urgency, impersonation, suspicious links, unusual payments and requests for credentials or codes. These guides explain the common patterns and the safest way to verify a message without trusting the message itself.</section><section class="card"><h2>Use the situation, not one signal, to choose a guide</h2><p>Start with the scenario that matches the message: a delivery fee, bank alert, account warning, job offer, marketplace payment or investment promise. Each guide separates technical link evidence from the sender's story and lists an independent verification route.</p><p>No clean URL result proves that a payment request, recruiter, seller or investment is genuine. When money, credentials, codes or remote access are involved, stop and contact the organization through its official app, saved number or known website.</p></section><div class="section-title"><span>Common scams</span><h2>Recognize the pattern before you act</h2></div><nav class="hub-grid" aria-label="Common scam prevention guides">{scam_cards}</nav><div class="section-title"><span>After an incident</span><h2>What to do next</h2></div><nav class="hub-grid" aria-label="Scam response guides">{safety_cards}</nav><section class="cta"><h2>Check the message before you trust it</h2><p>Paste a suspicious link or sender email address into Can I Share This?.</p><p><a class="button" href="/">Analyze it</a></p></section></main><footer>Can I Share This? · Scam prevention and safety checking</footer></body></html>'''


def write_pages() -> None:
    (DIST / 'scam-prevention.html').write_text(render_hub(), encoding='utf-8')
    for page in SCAM_PAGES:
        (DIST / f"{page['path'].strip('/')}.html").write_text(render_scam(page), encoding='utf-8')
    for page in SAFETY_PAGES:
        (DIST / f"{page['path'].strip('/')}.html").write_text(render_safety(page), encoding='utf-8')


def update_sitemap() -> None:
    sitemap = DIST / 'sitemap.xml'
    urls: set[str] = set()
    if sitemap.is_file():
        old = sitemap.read_text(encoding='utf-8', errors='replace')
        for loc in re.findall(r'<loc>\s*(.*?)\s*</loc>', old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(HOST + (parsed.path.rstrip('/') or '/'))
    urls.add(HOST + '/')
    for path in ALL_PATHS:
        urls.add(HOST + path)
    entries = '\n'.join(f'  <url><loc>{html.escape(url)}</loc></url>' for url in sorted(urls))
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding='utf-8')


def expose_from_existing_pages() -> None:
    for filename in ['safe-link-checker.html', 'methodology.html', 'email-safety-checker.html']:
        target = DIST / filename
        if not target.is_file():
            continue
        text = target.read_text(encoding='utf-8')
        if 'href="/scam-prevention"' in text:
            continue
        footer_index = text.rfind('</main>')
        if footer_index < 0:
            continue
        block = '<section id="scam-prevention-library" class="cta"><h2>Scam prevention guides</h2><p>Learn how common delivery, bank, account, marketplace and impersonation scams work.</p><p><a class="button" href="/scam-prevention">Open the Scam Prevention Center</a></p></section>'
        text = text[:footer_index] + block + text[footer_index:]
        target.write_text(text, encoding='utf-8')


def validate() -> None:
    for path in ALL_PATHS:
        target = DIST / f"{path.strip('/')}.html"
        if not target.is_file() or target.stat().st_size < 1500:
            raise RuntimeError(f'Missing or incomplete prevention page: {path}')
        text = target.read_text(encoding='utf-8')
        for token in ['index,follow', 'canonical', 'application/ld+json', 'Can I Share This?']:
            if token not in text:
                raise RuntimeError(f'Prevention page {path} missing {token}')
    sitemap = (DIST / 'sitemap.xml').read_text(encoding='utf-8')
    for path in ALL_PATHS:
        if HOST + path not in sitemap:
            raise RuntimeError(f'Sitemap missing {path}')


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist/ does not exist')
    write_pages()
    update_sitemap()
    expose_from_existing_pages()
    validate()
    print(f'Generated {len(ALL_PATHS)} scam-prevention and response pages')


if __name__ == '__main__':
    main()
