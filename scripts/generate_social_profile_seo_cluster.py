#!/usr/bin/env python3
"""Generate the Social Profile Safety SEO cluster and register its routes.

The pages deliberately avoid claiming that a profile is definitively fake. They
teach verification workflows and route visitors to the universal scanner.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
HOST = "https://canisharethis.com"

PAGES = [
    {
        "path": "/social-media-profile-checker",
        "keyword": "social media profile checker",
        "title": "Social Media Profile Checker — Check Impersonation Risk",
        "description": "Check a suspicious social media profile for impersonation warning signs, lookalike usernames, fake verification cues, risky links and scam patterns.",
        "h1": "Social Media Profile Checker",
        "lead": "Paste a public social profile URL or username into Can I Share This? to look for impersonation and scam warning signs. The checker does not prove who controls an account; it helps you decide what needs independent verification before you reply, pay or share information.",
        "sections": [
            ("What the profile checker looks for", "The scanner can recognize supported Instagram, Facebook, TikTok, X, Telegram and Discord profile URLs and usernames. It looks for brand-style usernames, common lookalike character substitutions, authority words such as support or verification, money-related wording and other identity signals. If a screenshot is supplied, image analysis can also extract visible profile text, links, QR codes and verification-like symbols."),
            ("Why a convincing profile can still be risky", "A copied logo, familiar display name, large follower count or professional biography does not independently authenticate the person behind an account. Impersonators can copy public photos and descriptions in minutes. The strongest verification usually comes from an independent path: the official company website, a known creator website, a previously trusted contact channel or the platform's own account information."),
            ("Check the links, not only the username", "A suspicious account often becomes dangerous when it sends you somewhere else. Links in a biography or message can lead to lookalike domains, phishing pages, malware downloads, fake investment platforms or payment requests. The universal scanner can inspect extracted links, redirects, final destinations and known threat signals separately from the profile identity check."),
            ("How to use the result", "Treat No obvious impersonation signs as limited evidence, not proof that the profile is genuine. Profile needs verification means there are identity or context signals worth checking. High impersonation risk means multiple warning signs justify stopping the interaction until the claimed identity can be confirmed through an independent source."),
        ],
        "faqs": [
            ("Can a profile checker prove an account is fake?", "No. Public signals can indicate impersonation risk, but they cannot prove who controls an account."),
            ("Which social networks are supported?", "The first version supports Instagram, Facebook, TikTok, X, Telegram and Discord profile links, plus standalone usernames."),
            ("Can I upload a screenshot instead of a link?", "Yes. A screenshot can be analyzed for visible usernames, biography text, links, QR codes, claimed brands and scam wording."),
            ("Does the checker analyze private followers?", "No. It does not scrape private profiles, analyze follower lists or perform facial recognition."),
        ],
    },
    {
        "path": "/fake-instagram-profile-checker",
        "keyword": "fake Instagram profile checker",
        "title": "Fake Instagram Profile Checker — Spot Impersonation Signs",
        "description": "Check an Instagram profile for impersonation warning signs, lookalike usernames, fake verification cues, suspicious bio links and scam behavior.",
        "h1": "Fake Instagram Profile Checker",
        "lead": "Check an Instagram profile before trusting a giveaway, support message, investment pitch, collaboration request or unexpected DM. The result estimates impersonation risk without claiming that the account is definitively fake.",
        "sections": [
            ("Start with the real Instagram username", "Display names are easy to copy. Focus on the actual @username and compare every character with the account you expected. Substitutions such as a zero for the letter o, a capital I for a lowercase l, extra dots or added words like support and official can create a convincing lookalike at a glance."),
            ("Do not treat a checkmark in the bio as verification", "A user can place checkmark characters, emojis or words such as verified in a display name or biography. That visual cue is different from platform verification. Verify important accounts through Instagram's interface and, when possible, follow a link from the person's or organization's official website."),
            ("Inspect bio links and DM requests", "An impersonation profile may use a familiar identity only to move you toward a phishing page, fake shop, crypto wallet or messaging app. Be especially cautious when a new contact asks for payment, gift cards, crypto, a login code, identity documents or an urgent move to Telegram or WhatsApp."),
            ("Safer verification workflow", "Open the brand or creator's official website independently and use its Instagram link if one is published. Compare username, account history and linked domains. If money, credentials or personal documents are involved, do not rely on the profile alone even when the account looks polished."),
        ],
        "faqs": [
            ("How can I tell if an Instagram account is impersonating someone?", "Compare the exact username, official website links, verification status and the nature of any request. Lookalike characters and off-platform payment requests are important warning signs."),
            ("Can fake Instagram accounts copy real photos?", "Yes. Public photos, biographies and logos can be copied, so visual similarity alone does not authenticate an account."),
            ("Is a large follower count proof an Instagram account is real?", "No. Follower counts can be manipulated and legitimate accounts can also be compromised."),
            ("What should I do with a suspicious Instagram DM?", "Do not send money, codes or documents. Verify the claimed identity independently, then block and report the account if it does not match."),
        ],
    },
    {
        "path": "/fake-facebook-profile-checker",
        "keyword": "fake Facebook profile checker",
        "title": "Fake Facebook Profile Checker — Check Impersonation Risk",
        "description": "Check a suspicious Facebook profile or page for impersonation signals, copied identities, risky links, urgent money requests and scam patterns.",
        "h1": "Fake Facebook Profile Checker",
        "lead": "Use the checker when a Facebook profile or page claims to be a company, public figure, friend, relative or support team and the request feels unusual. It evaluates visible risk signals without declaring an identity genuine or fake.",
        "sections": [
            ("Copied names and photos are weak identity evidence", "Facebook profiles can reuse public names, photos and logos. A scammer may also create a new profile that resembles someone you know and then send friend requests to that person's contacts. Treat the profile URL, username, Page transparency information and independent contact history as stronger clues than the profile picture alone."),
            ("Watch for account recovery and payment stories", "Common impersonation approaches include emergency money requests, fake marketplace payments, prize claims, account recovery messages and supposed support agents. Requests for gift cards, crypto, bank transfers, login codes or remote-access software deserve immediate skepticism."),
            ("Check external destinations", "A Facebook message can contain a link that appears to lead to Meta, a bank, a marketplace or a delivery service while actually opening an unrelated domain. Scan the link separately and compare the final hostname with the organization the message claims to represent."),
            ("Verify through a second channel", "If a profile claims to be someone you already know, contact that person using a phone number or channel you already trusted before the new message arrived. For businesses and public figures, navigate to the official website independently and follow its social links rather than trusting a link supplied by the suspicious account."),
        ],
        "faqs": [
            ("Can a fake Facebook profile use the same name and photo as a real person?", "Yes. Public names and photos can be copied, so they should not be treated as proof of identity."),
            ("What is a common Facebook impersonation scam?", "A cloned profile may contact friends or relatives with an urgent request for money, gift cards, codes or help recovering an account."),
            ("Should I trust a Facebook business page because it has reviews?", "Reviews and activity can add context but do not replace independent verification when the page asks for money or sensitive information."),
            ("Can I check a Facebook profile link without logging in?", "The scanner can evaluate the URL and username signals it can observe, but some Facebook content may require login and cannot be fully inspected."),
        ],
    },
    {
        "path": "/fake-tiktok-account-checker",
        "keyword": "fake TikTok account checker",
        "title": "Fake TikTok Account Checker — Check Copycat Profiles",
        "description": "Check a TikTok account for impersonation warning signs, copycat usernames, fake giveaways, suspicious bio links and off-platform scam requests.",
        "h1": "Fake TikTok Account Checker",
        "lead": "Check a TikTok profile that appears to copy a creator, celebrity, brand or support account. The checker highlights impersonation signals and suspicious destinations while avoiding unsupported claims about the person controlling the account.",
        "sections": [
            ("Copycat usernames can be difficult to notice", "TikTok usernames are compact and often viewed quickly on mobile. Added underscores, repeated letters, number substitutions and words such as backup, support or official can make an impersonator look plausible. Compare the exact @username rather than relying on the display name shown above it."),
            ("Giveaways and investment pitches raise the stakes", "A copied creator identity can be used to announce a prize, private investment group, crypto opportunity or exclusive merchandise offer. The profile becomes much higher risk when the conversation asks you to pay a fee, send crypto, buy gift cards or provide a one-time code to claim something."),
            ("Bio links deserve their own scan", "A TikTok bio can send users to storefronts, link aggregators, messaging apps and external websites. An unfamiliar link is not automatically malicious, but a brand claim combined with an unrelated or lookalike destination should be independently verified before you sign in or pay."),
            ("Use the creator's known channels", "For a creator or celebrity, compare links from a known official website and other long-established profiles. Do not assume a direct message is genuine merely because the account reposts the same public videos as the real creator."),
        ],
        "faqs": [
            ("Can someone copy a TikTok creator's videos to make a fake account?", "Yes. Public videos and profile images can be reposted, so copied content is not proof that the account is controlled by the original creator."),
            ("Are TikTok giveaway messages usually scams?", "Not all giveaways are scams, but unexpected prize claims that require payment, crypto, gift cards or login codes are strong warning signs."),
            ("What should I check in a TikTok username?", "Look for substituted characters, extra punctuation, added numbers and authority words that make the username resemble a known account."),
            ("Can the checker verify a TikTok blue check?", "It can identify visible verification-like cues in screenshots, but platform verification should be confirmed in TikTok itself."),
        ],
    },
    {
        "path": "/fake-x-profile-checker",
        "keyword": "fake X profile checker",
        "title": "Fake X Profile Checker — Check Impersonation Warning Signs",
        "description": "Check an X profile for impersonation risk, lookalike handles, copied brand identities, fake support messages, crypto scams and suspicious links.",
        "h1": "Fake X Profile Checker",
        "lead": "Check an X profile or @handle before trusting a support reply, investment pitch, giveaway or direct message. The scanner focuses on observable impersonation signals rather than assuming that an account is genuine because it looks established.",
        "sections": [
            ("The handle matters more than the display name", "An X display name can copy a company or public figure exactly. The @handle is a stronger identifier, but even handles can use subtle spelling changes, swapped characters and added support words. Read the complete handle before replying to an account that contacted you unexpectedly."),
            ("Support impersonation is common around public complaints", "Posting publicly about a payment, exchange, wallet or account problem can attract impostors that reply as supposed customer support. They may ask you to continue in direct messages, visit a recovery site or reveal credentials. Navigate to the company's official support channel independently instead."),
            ("Crypto and giveaway claims need stronger verification", "X is frequently used for crypto discussion, so a crypto-related profile is not inherently malicious. Risk increases sharply when a copied identity promises guaranteed returns, asks for a wallet transfer, advertises a send-one-get-two promotion or requests a recovery phrase or private key."),
            ("Inspect every external domain", "A legitimate-looking profile can link to a fraudulent website. Compare the final registered domain with the brand being claimed and scan shortened URLs or redirect chains before entering credentials, connecting a wallet or downloading a file."),
        ],
        "faqs": [
            ("Does a verified X account guarantee the person is trustworthy?", "No. Verification status and identity signals can add context, but accounts can be compromised and verification does not make every offer or link safe."),
            ("How do fake support accounts find users on X?", "They can monitor public posts that mention a company, wallet, exchange or support problem and reply while pretending to represent that service."),
            ("Should I ever send a crypto recovery phrase to X support?", "No legitimate support process should require you to reveal a wallet seed or recovery phrase."),
            ("Can a fake X profile use a similar handle to a real brand?", "Yes. Small spelling changes and character substitutions can make a handle look nearly identical at a glance."),
        ],
    },
    {
        "path": "/telegram-scam-profile-checker",
        "keyword": "Telegram scam profile checker",
        "title": "Telegram Scam Profile Checker — Check Suspicious Accounts",
        "description": "Check a suspicious Telegram username or profile link for impersonation signals, fake support identities, crypto scams, investment pitches and risky links.",
        "h1": "Telegram Scam Profile Checker",
        "lead": "Check a Telegram username or profile link before sending money, crypto, documents or account codes. Telegram is widely used for legitimate communities, but direct-message impersonation and investment scams make independent identity verification especially important.",
        "sections": [
            ("A familiar name is not enough", "Telegram usernames can imitate companies, exchanges, project founders and support teams. A scammer may use the same logo and display name while changing a single character in the username. Compare the exact username with the one published by the official organization."),
            ("Be cautious when someone moves you to Telegram", "A conversation that begins on Instagram, X, a dating app or a marketplace may be moved to Telegram to reduce platform oversight or continue a scam privately. Moving platforms is not proof of fraud, but it becomes a meaningful warning sign when combined with payment pressure or identity claims."),
            ("Crypto support should never need your seed phrase", "Wallet and exchange impersonators may promise account recovery, token migrations, airdrops or investment access. Never provide a private key, seed phrase or recovery phrase to a support account. Treat requests to connect a wallet to an unfamiliar site as a separate high-risk decision."),
            ("Verify channels from the official source", "For a company, project or public figure, use the official website to find the legitimate Telegram link. Search results, forwarded messages and screenshots can all point to copycat channels or accounts, so the verification path matters."),
        ],
        "faqs": [
            ("How can I check a Telegram username for scam signs?", "Compare the exact username with the official source, inspect lookalike characters and review any payment, investment or credential request."),
            ("Is Telegram itself unsafe?", "No. Telegram is a legitimate messaging service. Risk depends on the account, request, links and context."),
            ("Can Telegram support ask for my crypto seed phrase?", "No legitimate wallet or exchange support process should require your seed phrase or private key."),
            ("What if a Telegram account sends an investment website?", "Scan the destination separately, verify the organization independently and do not rely on screenshots of profits or testimonials as proof."),
        ],
    },
    {
        "path": "/how-to-spot-a-fake-social-media-profile",
        "keyword": "how to spot a fake social media profile",
        "title": "How to Spot a Fake Social Media Profile: Practical Checks",
        "description": "Learn how to spot a fake social media profile by checking usernames, verification, account history, links, money requests and independent identity sources.",
        "h1": "How to Spot a Fake Social Media Profile",
        "lead": "No single clue proves that a social account is fake. A reliable check combines the exact username, independent identity sources, account behavior, external links and the request being made. The more important the decision, the stronger the verification should be.",
        "sections": [
            ("1. Compare the exact username", "Start with the stable identifier rather than the display name. Look for letter substitutions, added punctuation, zeros replacing letters, duplicated characters and words such as official, support, backup or security. Compare it with a username linked from the claimed person's or company's official website."),
            ("2. Separate visual appearance from identity", "Logos, profile photos, bios and public posts can be copied. A checkmark character placed in a name is not the same as platform verification. Even genuine verified accounts can be compromised, so appearance should support other evidence rather than replace it."),
            ("3. Judge the request", "Urgent requests for money, crypto, gift cards, passwords, one-time codes or personal documents are more important than cosmetic profile details. Also be cautious when a new contact quickly proposes romance, employment, investment or a move to another messaging platform."),
            ("4. Inspect every destination", "Check bio links and message URLs before opening them. Look for unrelated registered domains, brand lookalikes, suspicious redirects, fresh domains, unexpected downloads and login pages that do not belong to the claimed organization."),
            ("5. Verify independently", "Do not use the phone number, link or verification method supplied only by the suspicious account. Find the official website or use a contact channel you already trusted. For someone you know personally, contact them through an existing phone number or account."),
        ],
        "faqs": [
            ("What is the biggest sign of a fake social media profile?", "There is no single universal sign. A mismatched identity combined with an urgent request for money, credentials or off-platform contact is substantially more concerning than any one cosmetic clue."),
            ("Does a new account mean it is fake?", "No. Legitimate people create new accounts. Account age is context, not proof."),
            ("Can follower counts be trusted?", "Follower counts can provide context but can be manipulated and should not be used as identity proof."),
            ("What should I do if I think a profile is impersonating someone?", "Stop sensitive interaction, verify the identity independently, preserve evidence if needed, and use the platform's block and report tools."),
        ],
    },
    {
        "path": "/celebrity-impersonation-scam",
        "keyword": "celebrity impersonation scam",
        "title": "Celebrity Impersonation Scam — How Fake Profiles Operate",
        "description": "Learn how celebrity impersonation scams use copycat profiles, private messages, fake giveaways, romance, investments and payment requests—and how to verify them.",
        "h1": "Celebrity Impersonation Scam",
        "lead": "Celebrity impersonation scams exploit a public identity to create instant trust. The account may copy photos, posts and branding, then claim the celebrity is privately contacting selected fans. The safest response is to verify independently before treating any private request as authentic.",
        "sections": [
            ("Why celebrity impersonation is persuasive", "Public figures already have a large library of photos, videos, interviews and voice recordings available online. That makes it easy to build a convincing copycat profile and increasingly easy to create synthetic audio or video. Familiarity with the celebrity can cause a victim to overlook the weak link: the account actually making the request."),
            ("Common scam stories", "Impersonators may offer exclusive fan access, prizes, charitable opportunities, investments or private relationships. A frequent pattern is a request for a membership fee, gift card, crypto transfer, shipping charge or payment to a supposed assistant or manager."),
            ("Private contact is not proof of special access", "A message that says the celebrity uses a secret account or cannot speak publicly is difficult to verify by design. Secrecy, urgency and requests not to contact the official team remove independent checks and should increase caution rather than trust."),
            ("How to verify a celebrity profile", "Start from an official website, agency page or long-established verified account and compare the linked usernames. Treat any request for money, codes or financial information as a separate decision that needs stronger evidence than a profile photo, voice message or video call."),
        ],
        "faqs": [
            ("Do celebrities contact fans privately?", "Some public figures interact with fans, but an unexpected private message should not be treated as proof of identity, especially when money or secrecy is involved."),
            ("Can scammers fake a celebrity voice?", "Synthetic and cloned audio can imitate voices, so a voice message alone is not reliable identity proof."),
            ("What payments are common in celebrity impersonation scams?", "Gift cards, crypto, wire transfers, membership fees and supposed shipping or processing fees are common patterns."),
            ("Should I report a celebrity impersonation account?", "If independent verification indicates the account is impersonating someone, preserve relevant evidence and report the account through the platform's impersonation tools."),
        ],
    },
    {
        "path": "/influencer-impersonation-scam",
        "keyword": "influencer impersonation scam",
        "title": "Influencer Impersonation Scam — Fake Creator Accounts",
        "description": "Recognize influencer impersonation scams involving copycat creator profiles, giveaways, sponsorship offers, fake shops, investments and payment requests.",
        "h1": "Influencer Impersonation Scam",
        "lead": "Copycat influencer accounts can target both followers and businesses. They reuse public content to imitate a creator, then send giveaway messages, investment offers, collaboration requests or fake sponsorship instructions that lead to payments or credential theft.",
        "sections": [
            ("Creators are easy to visually copy", "Influencers publish the exact assets an impersonator needs: profile images, videos, logos, speaking style and sponsor relationships. A copycat can therefore look authentic without controlling any of the creator's official accounts."),
            ("Followers and brands face different hooks", "Followers may receive prize, crypto or private-community offers. Businesses may receive fake media-kit links, invoice instructions or sponsorship negotiations. In both cases, verify the sender through the creator's established business contact rather than replying only inside the new conversation."),
            ("Check usernames, email domains and landing pages together", "An impersonator may use a social username close to the creator's, a free or lookalike email address and a copied landing page. Each clue may seem minor separately. Combined mismatches are stronger evidence that the claimed identity needs verification."),
            ("Protect sponsorship payments", "Before paying an invoice or shipping valuable products, confirm bank details and contract changes through a previously verified contact channel. A compromised legitimate account can also send fraudulent payment instructions, so account authenticity and transaction authenticity are separate questions."),
        ],
        "faqs": [
            ("How do fake influencer accounts copy real creators?", "They can reuse public videos, profile photos, captions and branding while changing the username slightly."),
            ("Can a fake influencer account offer a real-looking sponsorship?", "Yes. Scammers can imitate creator or agency branding and send fake contracts, invoices or download links."),
            ("What should a brand verify before paying an influencer?", "Confirm the creator's business contact, contract identity and payment details through a known independent channel."),
            ("Is a creator's follower count enough to verify the account?", "No. Counts can be copied visually, manipulated or belong to a compromised genuine account."),
        ],
    },
    {
        "path": "/catfish-profile-checker",
        "keyword": "catfish profile checker",
        "title": "Catfish Profile Checker — Check Identity and Scam Warning Signs",
        "description": "Check a suspicious dating or social profile for catfishing warning signs, identity inconsistencies, rapid emotional pressure, money requests and risky links.",
        "h1": "Catfish Profile Checker",
        "lead": "A catfish profile uses a false or misleading identity to build trust online. The checker can surface profile and message warning signs, but it cannot prove a person's real-world identity. Use it as one part of a broader verification process before sending money, intimate material or personal documents.",
        "sections": [
            ("Catfishing is about identity, not just profile photos", "A misleading profile may use stolen photos, invented life details or a real person's identity without permission. Some catfish interactions seek attention or relationships; others develop into romance scams, investment fraud, sextortion or requests for emergency money."),
            ("Rapid intimacy and repeated excuses matter", "Be cautious when a new contact becomes intensely romantic or committed very quickly while repeatedly avoiding ordinary verification. Travel, military service, offshore work, broken cameras and emergencies can be real circumstances, but a pattern of excuses combined with financial requests deserves stronger scrutiny."),
            ("Money changes the risk level", "Requests for travel costs, medical bills, customs fees, investments, crypto, gift cards or loans are major decision points. Do not send money because a profile seems emotionally convincing. Verify the person's identity and circumstances independently first."),
            ("Protect private material and documents", "Do not send identity documents, account recovery codes or intimate images under pressure. Personal material can be used for account takeover, identity fraud or blackmail. If threats begin, preserve evidence and use the platform's reporting tools rather than paying for silence."),
        ],
        "faqs": [
            ("Can a catfish profile use real photos?", "Yes. Stolen or copied photos can belong to a real person who has no connection to the account contacting you."),
            ("Can this checker confirm someone's real identity?", "No. It can identify warning signs but cannot perform definitive identity or biometric verification."),
            ("What is a strong catfishing warning sign?", "A combination of rapid emotional pressure, persistent avoidance of independent verification and requests for money or sensitive material is especially concerning."),
            ("Should I send money to someone I have only met online?", "Treat any financial request as high stakes and verify the identity and circumstances independently before considering it."),
        ],
    },
]

STYLE = """
<style>
:root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#69707b;--line:#e1e5ea;--accent:#788ff7;--soft:#f0f2f5}
@media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a8afba;--line:#2a2f37;--soft:#1d2127}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}.wrap{width:min(820px,calc(100% - 32px));margin:auto}header{border-bottom:1px solid var(--line);padding:18px 0}.brand{text-decoration:none;font-weight:850}.hero{padding:62px 0 28px}.eyebrow{font-size:12px;font-weight:850;letter-spacing:.09em;text-transform:uppercase;color:var(--accent)}h1{font-size:clamp(38px,7vw,60px);line-height:1.02;letter-spacing:-.045em;margin:10px 0 18px}.lead{font-size:19px;color:var(--muted);max-width:760px}.cta{margin:28px 0;padding:20px;border:1px solid var(--line);border-radius:16px;background:var(--card)}.cta strong{display:block;font-size:18px}.cta a{display:inline-block;margin-top:12px;padding:10px 14px;border-radius:10px;background:var(--accent);color:white;text-decoration:none;font-weight:800}article{padding-bottom:54px}section{margin-top:38px}h2{font-size:27px;line-height:1.18;letter-spacing:-.025em}p{color:var(--muted)}.faq{border-top:1px solid var(--line);padding-top:30px}.faq details{padding:13px 0;border-bottom:1px solid var(--line)}.faq summary{cursor:pointer;font-weight:780}.note{padding:15px 17px;background:var(--soft);border-radius:12px;font-size:14px;color:var(--muted)}footer{border-top:1px solid var(--line);padding:24px 0 36px;color:var(--muted);font-size:13px}
</style>
"""


def page_html(page: dict) -> str:
    path = page["path"]
    canonical = HOST + path
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in page["faqs"]
        ],
    }
    sections = "".join(
        f'<section><h2>{html.escape(title)}</h2><p>{html.escape(body)}</p></section>'
        for title, body in page["sections"]
    )
    faqs = "".join(
        f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for q, a in page["faqs"]
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(page["title"])}</title>
<meta name="description" content="{html.escape(page["description"], quote=True)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:title" content="{html.escape(page["title"], quote=True)}"><meta property="og:description" content="{html.escape(page["description"], quote=True)}"><meta property="og:url" content="{canonical}">
<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False, separators=(',', ':'))}</script>{STYLE}</head>
<body><header><div class="wrap"><a class="brand" href="/">Can I Share This?</a></div></header>
<main class="wrap"><div class="hero"><div class="eyebrow">Social profile safety</div><h1>{html.escape(page["h1"])}</h1><p class="lead">{html.escape(page["lead"])}</p></div>
<div class="cta"><strong>Check the profile before you trust it</strong><p>Paste the profile URL, @username, suspicious message or screenshot into the universal scanner.</p><a href="/">Open the safety checker</a></div>
<article>{sections}<p class="note"><strong>Important:</strong> Can I Share This? evaluates observable risk signals. It does not prove who controls an account, perform facial recognition, scrape private profiles or authenticate a person's real-world identity.</p>
<section class="faq"><h2>Frequently asked questions</h2>{faqs}</section></article></main>
<footer><div class="wrap">Independent safety guidance · Results are signals, not identity certification.</div></footer></body></html>'''


def register_routes() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    routes = manifest["routes"]
    by_path = {r["path"]: r for r in routes}
    for page in PAGES:
        role = "hub" if page["path"] == "/social-media-profile-checker" else "guide"
        route = {
            "path": page["path"], "status": "active", "index": True,
            "canonical": page["path"], "cluster": "social-profile-safety", "role": role,
            "intent": f'help users evaluate {page["keyword"]} intent without claiming definitive identity verification',
            "primaryKeyword": page["keyword"],
        }
        if page["path"] in by_path:
            by_path[page["path"]].update(route)
        else:
            routes.append(route)
    routes.sort(key=lambda r: (r["path"] != "/", r["path"]))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    seen_titles = set()
    for page in PAGES:
        if page["title"] in seen_titles:
            raise RuntimeError(f'Duplicate SEO title: {page["title"]}')
        seen_titles.add(page["title"])
        target = DIST / f'{page["path"].lstrip("/")}.html'
        target.write_text(page_html(page), encoding="utf-8")
    register_routes()
    print(f'Generated and registered {len(PAGES)} social-profile SEO pages')


if __name__ == "__main__":
    main()
