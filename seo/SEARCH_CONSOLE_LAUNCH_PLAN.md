# Search Console launch and measurement plan — 2026

Status: PREPARED ONLY — use after production deployment

## Objective

Measure whether the Google Drive and Dropbox content clusters generate qualified organic traffic that actually uses the checker, instead of optimizing only for impressions or raw clicks.

## 1. Pre-launch baseline

Before the 10 pages are published, record the previous 28 days for:

- total Google Search clicks
- total impressions
- average CTR
- average position
- branded vs non-branded queries
- organic sessions landing on the homepage
- checker submissions from organic sessions, if analytics supports it

Keep this baseline so later growth is not confused with normal sitewide fluctuations.

## 2. Sitemap submission

After production verification:

1. Confirm `https://YOUR-PRODUCTION-DOMAIN/sitemap.xml` returns HTTP 200.
2. Confirm it contains only canonical indexable production URLs.
3. Reference the sitemap in `robots.txt`.
4. Submit the sitemap through Google Search Console.
5. Monitor processing errors and indexed URL counts.

Sitemap submission helps discovery but does not guarantee crawling or indexing.

## 3. URL Inspection priority order

Inspect these first after launch:

1. `/google-drive-link-checker`
2. `/dropbox-link-checker`
3. `/google-drive-link-not-working`
4. `/dropbox-shared-link-not-working`
5. `/drive-vs-dropbox-share-link-checker`

Then inspect the remaining support pages.

Check:

- page is indexable
- Google-selected canonical matches intended canonical
- rendered content includes the unique page copy
- page is not blocked by robots or noindex
- HTTP status is correct

## 4. Query clusters to monitor

### Google Drive cluster

Track query themes rather than only exact keywords:

- google drive link checker
- check google drive link
- google drive permission checker
- google drive link not working
- google drive link works for me not others
- test google drive share link
- google drive folder sharing

### Dropbox cluster

- dropbox link checker
- test dropbox link
- dropbox permission checker
- dropbox shared link not working
- dropbox link expired
- dropbox link expiration checker

### Cross-platform intent

- check if link works for someone else
- recipient access checker
- shared link checker
- file sharing link checker
- drive vs dropbox sharing

Do not create new pages automatically for every query variation. First determine whether the new query represents distinct user intent.

## 5. Page-level success metrics

For each SEO route monitor:

- impressions
- clicks
- CTR
- average position
- number of ranking queries
- organic landing sessions
- checker-start rate
- checker-completion rate
- successful verdict display rate
- return-to-search or short-session signal where available

Primary business metric:

`organic checker completions / organic landing sessions`

A page that ranks but does not lead users into the checker is less valuable than one with fewer clicks but strong product usage.

## 6. 14 / 30 / 60 day review

### Day 14

Focus on technical discovery:

- pages crawled
- pages indexed
- canonical mismatches
- accidental noindex
- unexpected 404/5xx
- sitemap errors

Do not rewrite pages aggressively based on two weeks of sparse ranking data.

### Day 30

Review:

- queries gaining impressions
- pages with impressions but weak CTR
- query intent that does not match the current title/H1
- internal-link gaps
- pages that receive no impressions at all

Adjust titles/descriptions only where evidence supports the change.

### Day 60

Decide which cluster deserves expansion.

Expand only from observed demand, for example:

- distinct Google Drive error states
- distinct Dropbox expiration/access problems
- OneDrive or Notion if the product already supports them well
- recipient-access workflow pages tied to actual checker capabilities

## 7. Generative AI Search reporting

Google introduced dedicated Generative AI performance reporting in Search Console during 2026, with rollout initially limited to a subset of sites.

If the property has access, track:

- impressions from generative AI Search features
- pages cited or surfaced most often
- query/topic patterns associated with AI visibility
- downstream checker usage from those visits

Do not optimize solely for generative impressions. Compare them with qualified product actions.

## 8. Content improvement loop

Use Search Console evidence to improve existing pages before creating more pages.

Priority order:

1. Fix indexing/canonical problems.
2. Improve pages receiving impressions but weak CTR.
3. Improve pages receiving clicks but weak checker usage.
4. Add missing answers based on real query language.
5. Add original examples/evidence from checker behavior.
6. Create a new page only for materially distinct intent.

## 9. Cannibalization check

The Google Drive pages intentionally overlap semantically, so monitor whether Google repeatedly swaps multiple URLs for the same high-value query.

Potential warning signs:

- two pages alternate for the same query without either gaining stable position
- support pages outrank the intended hub for broad cluster queries
- impressions split across near-identical intents

If this happens, strengthen hub/support internal linking, differentiate intent, or consolidate pages rather than creating more keyword variants.

## 10. Launch dashboard fields

Recommended weekly table:

| Page | Indexed | Clicks | Impressions | CTR | Avg position | Organic sessions | Checker completions | Conversion rate | Main query cluster | Action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|

Keep Google Drive and Dropbox cluster totals separately so the winning acquisition channel becomes obvious.

## Official references checked 2026-09-01

- Generative AI performance reports: https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- Generative AI optimization guide: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Sitemap documentation: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Canonicalization documentation: https://developers.google.com/search/docs/crawling-indexing/canonicalization
