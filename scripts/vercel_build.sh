#!/usr/bin/env bash
set -euo pipefail

bash build.sh
python3 scripts/apply_x_viral_loop.py
python3 scripts/apply_link_first_home_v1.py
python3 scripts/audit_link_first_detail_v2.py
python3 scripts/extract_homepage_css.py
python3 scripts/audit_gsc_priority.py
python3 scripts/audit_homepage_weight.py
