# Safe integration checkpoint — 2026-09-01

Branch: `seo-2026-safe-integration`

## Current status

- The legacy static preview is reconstructed from the existing chunk bundle.
- The 10 priority Google Drive / Dropbox SEO pages are generated as a reversible overlay after the legacy build.
- The SEO route manifest remains the source of truth for title, meta description and H1 values.
- The preview is explicitly non-indexable through page-level `noindex` and Vercel `X-Robots-Tag: noindex, nofollow`.
- Preview API requests continue to proxy to `https://canisharethis.com/api/*`; no production API source has been recovered into this repository.
- GitHub Actions rebuilds and validates the preview on every push to this branch.
- Redeploy trigger after Gemini production environment configuration: 2026-09-04.

## Automated gates

The validation workflow must remain green before any further integration step. It verifies:

1. Static reconstruction succeeds.
2. Exactly 10 priority routes exist in the manifest.
3. Every priority route produces HTML.
4. Title, meta description and H1 match the manifest.
5. Canonical paths are correct and do not use a Vercel preview hostname.
6. Priority routes exist in the sitemap.
7. Local generated links are not broken.
8. `robots.txt` and `sitemap.xml` are present.
9. The preview-only safety marker is present.
10. The preview API rewrite remains pointed at the stable production API.

## Production merge gate

DO NOT merge this branch into `main` or promote it to the production domain until all of the following are true:

- The real production application source has been recovered and committed to a controlled branch/repository.
- The real production API implementation is available; the preview proxy is no longer needed.
- The current production site and recovered source are verified to represent the same behavior.
- The SEO pages are integrated into the real application architecture rather than relying on the preview-only static overlay.
- Preview-only `noindex` controls are removed only in the production-ready configuration.
- A production candidate passes build, functional link-check tests, mobile/desktop visual checks, SEO validation and regression checks.
- A rollback commit/deployment is identified before promotion.

## Files that are preview infrastructure, not production architecture

- `chunks/site.part*`
- `build.sh` static reconstruction mechanism
- `/api/*` external rewrite in `vercel.json`
- `PREVIEW_ONLY.md`

These are useful for validating content and routing safely, but they must not be mistaken for recovered production source code.

## Safe next engineering objective

Recover or reconnect the actual production source. Until then, this branch is a validated preview artifact and content integration checkpoint, not a production candidate.
