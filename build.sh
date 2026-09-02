#!/usr/bin/env bash
set -euo pipefail
rm -rf dist
mkdir -p dist
cat chunks/site.part* | base64 -d > /tmp/cist-site.tgz
tar -xzf /tmp/cist-site.tgz -C dist
python3 scripts/generate_priority_pages.py
python3 scripts/enable_indexing.py
python3 scripts/apply_seo_architecture.py
python3 scripts/generate_safety_pages.py
python3 scripts/apply_safety_v6.py
python3 scripts/generate_scam_safety_cluster.py
python3 scripts/generate_minimal_homepage.py
python3 scripts/generate_qr_page.py
python3 scripts/add_x_footer.py
python3 scripts/apply_homepage_search_seo.py
python3 scripts/generate_methodology_page.py
python3 scripts/generate_authority_pages.py
python3 scripts/generate_email_seo_pages.py
python3 scripts/align_email_dmarc_rfc9989.py
python3 scripts/generate_scam_prevention_pages.py
python3 scripts/apply_scam_icons.py
python3 scripts/apply_scam_trust_tests.py
python3 scripts/apply_design_polish.py
python3 scripts/apply_anonymous_scan_stats.py
python3 scripts/apply_email_input.py
python3 scripts/apply_email_v11_ui.py
python3 scripts/apply_technical_details_copy.py
python3 scripts/apply_footer_navigation.py
python3 scripts/apply_header_navigation.py
python3 scripts/apply_link_accent.py
python3 scripts/apply_scanner_ux_v2.py
python3 scripts/apply_readability_v1.py
python3 scripts/apply_wordmark_logo.py
python3 scripts/apply_homepage_brand_accent.py
python3 scripts/apply_brand_favicon.py
INDEXNOW_KEY="$(tr -d '\r\n' < seo/indexnow-key.txt)"
if [[ ! "$INDEXNOW_KEY" =~ ^[A-Za-z0-9-]{8,128}$ ]]; then
  echo "Invalid IndexNow key format" >&2
  exit 1
fi
printf '%s\n' "$INDEXNOW_KEY" > "dist/${INDEXNOW_KEY}.txt"
printf 'Built %s static files\n' "$(find dist -type f | wc -l)"
