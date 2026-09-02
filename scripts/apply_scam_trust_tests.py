#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

TESTS = {
    'fake-package-delivery-scam.html': {
        'message': 'Your parcel is waiting. Pay €1.99 to reschedule delivery: delivery-track-support.example',
        'legit': 'Not necessarily. Small redelivery fees, urgency and lookalike tracking links are common phishing patterns. Verify the parcel in the carrier’s official app or website instead of using the message link.',
        'suspicious': 'Good instinct. An unexpected delivery message, a small payment request and a link outside the carrier’s known domain are strong warning signs.'
    },
    'advance-fee-scam.html': {
        'message': 'You have been selected to receive an inheritance of $850,000. A $430 processing fee is required before the funds can be released.',
        'legit': 'Not necessarily. A large promised payout combined with an upfront fee is the core pattern of an advance-fee scam. Verify the institution independently and do not send money first.',
        'suspicious': 'Good instinct. Unexpected money promises, invented release fees and pressure to pay before receiving funds are classic advance-fee warning signs.'
    },
    'bank-impersonation-scam.html': {
        'message': 'Fraud alert: your account is at risk. Move your balance to this secure account now to protect your funds.',
        'legit': 'Not necessarily. Banks do not protect an account by asking customers to move money to a “safe” account supplied in an unexpected message or call. Contact the bank through the official app or the number on your card.',
        'suspicious': 'Good instinct. Urgent transfer instructions, “safe account” language and pressure not to hang up are major bank-impersonation warning signs.'
    },
    'account-verification-scam.html': {
        'message': 'Your account will be suspended today. Verify your identity now using the secure link below.',
        'legit': 'Not necessarily. Account-security scams often copy familiar brands and create urgency. Open the real app or type the known service address yourself instead of signing in through the message.',
        'suspicious': 'Good instinct. Unexpected suspension warnings, urgent verification requests and login links are common account-phishing patterns.'
    },
    'romance-scam.html': {
        'message': 'I’m stuck overseas and need €500 for an emergency. I’ll repay you as soon as I get home. Please don’t tell anyone yet.',
        'legit': 'Not necessarily. Emotional trust does not make a financial request safe. Emergencies, secrecy and repeated reasons not to meet are common romance-scam patterns.',
        'suspicious': 'Good instinct. A sudden money request, secrecy and an online relationship that cannot be independently verified should trigger caution.'
    },
    'job-offer-scam.html': {
        'message': 'You’ve been selected for a remote position. Purchase the equipment today and we’ll reimburse you with your first paycheck.',
        'legit': 'Not necessarily. Legitimate employers should not require you to send money to obtain wages. Verify the role on the company’s official careers page and contact the employer independently.',
        'suspicious': 'Good instinct. Fast hiring, equipment payments, fake checks and requests to pay before getting paid are common job-scam warning signs.'
    },
    'marketplace-scam.html': {
        'message': 'Payment completed. Click this link to upgrade your seller account before the money can be released.',
        'legit': 'Not necessarily. Marketplace scammers often send fake payment confirmations and off-platform links. Check the transaction inside the marketplace itself instead of trusting the message.',
        'suspicious': 'Good instinct. A request to leave the platform, pay a fee or use an external payment link is a strong marketplace-scam signal.'
    },
    'tech-support-scam.html': {
        'message': 'Microsoft Security Alert: your computer is infected. Call support now and install the remote assistance tool to prevent data loss.',
        'legit': 'Not necessarily. Browser pop-ups and unsolicited calls that demand remote access are common tech-support scam techniques. Close the page and use the vendor’s official support channel independently.',
        'suspicious': 'Good instinct. Unexpected infection warnings, urgent phone numbers, payment demands and remote-access requests are major warning signs.'
    },
    'crypto-investment-scam.html': {
        'message': 'Your account has earned $12,480. Deposit $900 in tax and verification fees to unlock your withdrawal.',
        'legit': 'Not necessarily. Fake investment platforms can display invented profits and then demand more money before withdrawals. Do not pay additional fees to release supposed gains.',
        'suspicious': 'Good instinct. Guaranteed-looking profits, withdrawal blocks and new fees before releasing funds are common crypto-investment scam patterns.'
    },
    'gift-card-scam.html': {
        'message': 'I need this handled urgently. Buy four gift cards, scratch the backs and send me the codes. I’ll reimburse you later.',
        'legit': 'Not necessarily. Gift cards are effectively cash once the code is shared. Legitimate employers, banks and government agencies do not use gift cards as an emergency payment method.',
        'suspicious': 'Good instinct. Urgent gift-card purchases and requests for card numbers or PINs are major scam warning signs.'
    },
}

STYLE = r'''
<style id="cist-trust-test-style">
.trust-test{margin:16px 0;padding:clamp(18px,3.5vw,26px);border:1px solid var(--line);border-radius:18px;background:linear-gradient(145deg,color-mix(in srgb,var(--card) 94%,#8ea2ff 6%),var(--card));box-shadow:var(--shadow)}
.trust-test-head{display:flex;align-items:baseline;justify-content:space-between;gap:10px 16px;flex-wrap:wrap;margin-bottom:13px}.trust-test-head span{color:#7788eb;font-size:11px;font-weight:900;letter-spacing:.09em;text-transform:uppercase}.trust-test-head h2{margin:0}
.trust-example{padding:15px 16px;border:1px solid var(--line);border-radius:14px;background:var(--soft)}.trust-example-label{display:block;margin-bottom:7px;color:var(--muted);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.trust-example blockquote{margin:0;font-size:15px;font-weight:650;line-height:1.5;letter-spacing:-.01em}
.trust-actions{display:flex;gap:8px;margin-top:12px}.trust-choice{flex:1;min-height:42px;padding:9px 12px;border:1px solid var(--line);border-radius:11px;background:var(--card);color:var(--text);font:inherit;font-size:13px;font-weight:850;cursor:pointer}.trust-choice:hover,.trust-choice:focus-visible{border-color:#8ea2ff;outline:none}.trust-choice[aria-pressed="true"]{border-color:#8ea2ff;background:color-mix(in srgb,var(--card) 88%,#8ea2ff 12%)}
.trust-feedback{margin-top:12px;padding:13px 14px;border-left:3px solid #8ea2ff;border-radius:0 11px 11px 0;background:color-mix(in srgb,var(--soft) 88%,#8ea2ff 12%)}.trust-feedback strong{display:block;margin-bottom:3px;font-size:13px}.trust-feedback p{margin:0;color:var(--muted);font-size:13px;line-height:1.5}.trust-feedback a{display:inline-block;margin-top:7px;color:#7788eb;font-size:12px;font-weight:850;text-decoration:none}.trust-feedback a:hover{text-decoration:underline;text-underline-offset:3px}
@media(prefers-color-scheme:dark){.trust-test-head span,.trust-feedback a{color:#8ea2ff}.trust-test{background:linear-gradient(145deg,color-mix(in srgb,var(--card) 91%,#8ea2ff 9%),var(--card))}}
@media(max-width:560px){.trust-test{padding:16px;border-radius:16px}.trust-actions{display:grid;grid-template-columns:1fr 1fr}.trust-example{padding:13px 14px}.trust-example blockquote{font-size:14px}}
</style>
'''

SCRIPT = r'''
<script id="cist-trust-test-script">
(function(){
  document.querySelectorAll('.scam-trust-test').forEach(function(test){
    var buttons=test.querySelectorAll('[data-trust-choice]');
    var feedback=test.querySelectorAll('[data-trust-feedback]');
    buttons.forEach(function(button){
      button.addEventListener('click',function(){
        var choice=button.getAttribute('data-trust-choice');
        buttons.forEach(function(b){b.setAttribute('aria-pressed',b===button?'true':'false')});
        feedback.forEach(function(box){box.hidden=box.getAttribute('data-trust-feedback')!==choice});
        var shown=test.querySelector('[data-trust-feedback="'+choice+'"]');
        if(shown) shown.focus({preventScroll:true});
      });
    });
  });
})();
</script>
'''


def esc(value: str, quote: bool = False) -> str:
    return html.escape(value, quote=quote)


def block(data: dict[str, str]) -> str:
    return f'''<section class="trust-test scam-trust-test" aria-labelledby="trust-test-title">
<div class="trust-test-head"><span>Quick test</span><h2 id="trust-test-title">Would you trust this?</h2></div>
<div class="trust-example"><span class="trust-example-label">Example message</span><blockquote>“{esc(data['message'])}”</blockquote></div>
<div class="trust-actions" role="group" aria-label="Choose how this message looks to you">
<button class="trust-choice" type="button" data-trust-choice="legitimate" aria-pressed="false">Looks legitimate</button>
<button class="trust-choice" type="button" data-trust-choice="suspicious" aria-pressed="false">Suspicious</button>
</div>
<div class="trust-feedback" data-trust-feedback="legitimate" tabindex="-1" hidden><strong>Not necessarily.</strong><p>{esc(data['legit'])}</p><a href="/">Check the link or sender →</a></div>
<div class="trust-feedback" data-trust-feedback="suspicious" tabindex="-1" hidden><strong>Good instinct.</strong><p>{esc(data['suspicious'])}</p><a href="/">Check the link or sender →</a></div>
</section>'''


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist/ does not exist')

    updated = 0
    for filename, data in TESTS.items():
        path = DIST / filename
        if not path.is_file():
            raise RuntimeError(f'Missing scam page: {filename}')
        source = path.read_text(encoding='utf-8')
        if 'class="trust-test scam-trust-test"' in source:
            continue
        anchor = '<section class="card"><h2>How this scam usually works</h2>'
        if anchor not in source:
            raise RuntimeError(f'Trust test anchor missing: {filename}')
        source = source.replace(anchor, block(data) + anchor, 1)
        if 'id="cist-trust-test-style"' not in source:
            source = source.replace('</head>', STYLE + '</head>', 1)
        if 'id="cist-trust-test-script"' not in source:
            source = source.replace('</body>', SCRIPT + '</body>', 1)
        path.write_text(source, encoding='utf-8')
        updated += 1

    print(f'Added interactive trust tests to {updated} scam pages')


if __name__ == '__main__':
    main()
