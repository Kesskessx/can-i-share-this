#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"dist"/"index.html"

def main():
    if not HOME.is_file():
        raise SystemExit("Detailed Analysis V2 audit failed: dist/index.html missing")
    s=HOME.read_text(encoding="utf-8")
    failures=[]
    for token in (
        'id="cist-detailed-analysis-v2-style"',
        'id="cist-detailed-analysis-v2-script"',
        'Detailed analysis',
        'What the scan observed',
        'Redirect chain',
        'Domain & response',
        'What this result does not mean',
        'Advanced technical details',
    ):
        if token not in s:
            failures.append(f"missing {token}")
    if 'id="cist-visible-technical-evidence-v1-script"' in s:
        failures.append("legacy always-open technical detail script still present")

    m=re.search(r'<script id="cist-detailed-analysis-v2-script">(.*?)</script>',s,re.S)
    if not m:
        failures.append("Detailed Analysis V2 script block missing")
    else:
        with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False,encoding="utf-8") as f:
            f.write(m.group(1)); path=f.name
        p=subprocess.run(["node","--check",path],capture_output=True,text=True)
        if p.returncode!=0:
            failures.append("JavaScript syntax check failed: "+(p.stderr.strip() or p.stdout.strip()))

    if failures:
        raise SystemExit("Detailed Analysis V2 audit failed:\n- "+"\n- ".join(failures))
    print("Detailed Analysis V2 audit passed")

if __name__=="__main__":
    main()
