# Universal Safety Checker — prepared test + SEO batch

Prepared: 2026-09-03  
Branch: `prep/universal-tests-seo-batch`  
Production impact: **none until merged and integrated into `build.sh`**

## 1. Regression battery

`tests/universal_safety_matrix.json` contains **45 cases** covering:

- regular websites
- X, Reddit and TikTok
- YouTube and Spotify
- Google Drive, Dropbox, OneDrive and Notion
- shopping and developer links
- PDF, DOCX, XLSX, images, audio and video files
- ZIP / RAR archives
- EXE / APK software
- Bitly / t.co short links
- same-domain and cross-domain redirects
- gambling, crypto, adult, weapons, drug and torrent/file-sharing context
- four domain-age states
- official Google Safe Browsing malware and phishing fixtures
- three privacy boundary cases
- four email paths

No real access token, password, private share or personal email address is stored in the test matrix.

### Test layers

**Deterministic classification**  
`node scripts/test_universal_matrix.js`

This reads the generated homepage and executes the same `cistLinkType` and `cistSensitiveCategory` functions used by the scanner. It checks the offline/public URL classification cases without making network requests.

**Preparation contract**  
`python3 scripts/validate_prepared_batch.py`

This validates matrix coverage, privacy constraints, live-host allowlists and the SEO page specification.

**Live smoke after deployment**  
Use only cases marked `safe-live` and `official-threat-fixture`. Never send `privacy-guard` or `offline-fixture` cases to external services.

## 2. Eight SEO pages ready to generate

The pages are stored as full content specifications in `scripts/generate_context_checker_pages.py`.

| Route | Main intent | Distinct purpose |
| --- | --- | --- |
| `/sms-link-checker` | sms link checker | suspicious links received by SMS/text |
| `/whatsapp-link-checker` | whatsapp link checker | links received in WhatsApp conversations |
| `/qr-code-scam-checker` | qr code scam checker | decoded QR destinations and QR-payment scams |
| `/download-link-checker` | download link checker | file type, software/archive and download context |
| `/short-link-checker` | short link checker | shortener detection and final-destination verification |
| `/email-safety-checker` | is this email safe | enriches the existing sender-address hub instead of creating a competing page |
| `/gambling-link-safety` | gambling link safety | separates technical threats from gambling/licensing context |
| `/crypto-scam-link-checker` | crypto scam link checker | crypto/investment links, wallet and payment caution |

Each page includes:

- unique Title, meta description and H1
- direct `At a glance` answer
- unique explanatory content
- four scanner-capability explanations
- four safer next steps
- explicit scanner limitations
- four FAQs
- FAQPage + WebPage + Breadcrumb structured data
- at least four internal links
- primary prevention/regulatory references
- CTA to the universal checker
- canonical URL and `index,follow`

The generator also appends missing routes to the generated sitemap.

## 3. Merge/deploy plan

When the Vercel build quota is available:

1. Rebase/refresh this branch from the latest validated `main` if needed.
2. Run the normal build.
3. Run `python3 scripts/validate_prepared_batch.py`.
4. Run `node scripts/test_universal_matrix.js` against the generated homepage.
5. Add `python3 scripts/generate_context_checker_pages.py` to `build.sh` after the existing content generators and before robots/route audits.
6. Build again.
7. Confirm all eight HTML pages exist, are in the sitemap, have correct canonical/robots/schema and pass the internal-route audit.
8. Merge as **one controlled production batch** and deploy once.
9. Run only the allowlisted live smoke cases against production.

## Guardrails

- A `no-known-threat` result is never described as proof of safety.
- Domain age is context, not a fraud verdict.
- Gambling/crypto category labels are separate from malware/phishing reputation.
- Email addresses do not use Google Web Risk.
- URLs containing access credentials or sensitive query parameters stay out of external reputation checks.
- The SEO pages do not claim antivirus-style file scanning or licensing verification.
