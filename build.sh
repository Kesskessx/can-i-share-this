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
python3 scripts/generate_minimal_homepage.py
python3 scripts/generate_qr_page.py
INDEXNOW_KEY="$(tr -d '\r\n' < seo/indexnow-key.txt)"
if [[ ! "$INDEXNOW_KEY" =~ ^[A-Za-z0-9-]{8,128}$ ]]; then
  echo "Invalid IndexNow key format" >&2
  exit 1
fi
printf '%s\n' "$INDEXNOW_KEY" > "dist/${INDEXNOW_KEY}.txt"
printf 'Built %s static files\n' "$(find dist -type f | wc -l)"
