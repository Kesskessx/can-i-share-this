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
printf 'Built %s static files\n' "$(find dist -type f | wc -l)"
