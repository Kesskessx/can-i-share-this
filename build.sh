#!/usr/bin/env bash
set -euo pipefail
rm -rf dist
mkdir -p dist
cat chunks/site.part* | base64 -d > /tmp/cist-site.tgz
tar --no-same-owner -xzf /tmp/cist-site.tgz -C dist
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
python3 scripts/generate_missing_route_pages.py
python3 scripts/generate_security_transparency.py
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
python3 scripts/apply_reputation_visibility.py
python3 scripts/apply_plain_language.py
python3 scripts/apply_one_click_scan.py
python3 scripts/apply_link_type_v1.py
python3 scripts/apply_sensitive_category_v11.py
python3 scripts/apply_universal_result_v12.py
python3 scripts/apply_recommended_action_v13.py
python3 scripts/apply_benchmark_upgrades_v16.py
python3 scripts/generate_context_checker_pages.py
python3 scripts/generate_growth_authority_pages.py
python3 scripts/apply_growth_title_polish.py
python3 scripts/apply_readability_v1.py
python3 scripts/apply_wordmark_logo.py
python3 scripts/apply_homepage_brand_accent.py
python3 scripts/apply_brand_favicon.py
python3 scripts/apply_vercel_analytics.py
python3 scripts/ensure_indexable_robots.py
python3 scripts/register_growth_routes.py
python3 scripts/apply_seo_registry.py
python3 scripts/apply_capability_strip.py
python3 scripts/remove_redundant_home_sections.py
python3 scripts/apply_entity_identity.py
python3 scripts/apply_breadcrumb_schema.py
python3 scripts/apply_crypto_input.py
python3 scripts/apply_result_priority_layout.py
python3 scripts/apply_single_complete_scan.py
python3 scripts/apply_simple_result_ui.py
python3 scripts/apply_homepage_stats.py
python3 scripts/apply_image_safety_input.py
python3 scripts/apply_universal_scanner_design.py
python3 scripts/apply_unified_scanner_ui.py
python3 scripts/apply_homepage_declutter.py
python3 scripts/apply_universal_backend_routing.py
python3 scripts/apply_full_message_ui.py
python3 scripts/apply_homepage_visual_hierarchy_v2.py
python3 scripts/apply_clean_link_tool.py
python3 scripts/apply_redirect_destination_ui.py
python3 scripts/apply_lookalike_explanation_ui.py
python3 scripts/apply_domain_context_ui.py
python3 scripts/apply_business_contact.py
python3 scripts/audit_seo_registry.py
python3 scripts/audit_internal_routes.py
INDEXNOW_KEY="$(tr -d '\r\n' < seo/indexnow-key.txt)"
if [[ ! "$INDEXNOW_KEY" =~ ^[A-Za-z0-9-]{8,128}$ ]]; then
  echo "Invalid IndexNow key format" >&2
  exit 1
fi
printf '%s\n' "$INDEXNOW_KEY" > "dist/${INDEXNOW_KEY}.txt"
printf 'Built %s static files\n' "$(find dist -type f | wc -l)"
