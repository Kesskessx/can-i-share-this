#!/usr/bin/env bash
set -euo pipefail
rm -rf dist
mkdir -p dist
cat chunks/site.part* | base64 -d > /tmp/cist-site.tgz
tar -xzf /tmp/cist-site.tgz -C dist
printf 'Built %s static files\n' "$(find dist -type f | wc -l)"
