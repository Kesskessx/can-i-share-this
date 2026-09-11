#!/usr/bin/env python3
from pathlib import Path

p = Path('api/python_scan.py')
s = p.read_text(encoding='utf-8')
old = '''    if p and any(p == c for c in cryptos):
        return "crypto"
    if p:
        n = normalize_url(p)'''
new = '''    if p and any(p == c for c in cryptos):
        return "crypto"
    # A browser-uploaded filename plus extracted content is a file/message input,
    # not a bare domain even when the extension is also a valid public TLD.
    if p and len(all_text.strip()) > len(p) and re.fullmatch(
        r"[^/\\\\\\s]+\\.(?:pdf|doc|docx|xls|xlsx|csv|txt|rtf|eml|msg|zip|rar|7z|jpg|jpeg|png|webp|gif|heic|svg)",
        p,
        re.I,
    ):
        return "message-url" if urls else ("message-email" if emails else "message")
    if p:
        n = normalize_url(p)'''
if old not in s:
    raise SystemExit('Target detect_type block not found; refusing unsafe patch')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('Patched file input classification in api/python_scan.py')
