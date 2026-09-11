#!/usr/bin/env python3
from pathlib import Path

p = Path('api/python_scan.py')
s = p.read_text(encoding='utf-8')
old = '    urls = extract_urls(all_text, [v for v in qr_values if str(v).lower().startswith(("http://", "https://"))])'
new = '''    url_text = all_text
    # When extracted file content is present, a plain filename such as
    # "invoice.pdf" is context, not a bare web domain. Keep URLs found in
    # extracted text and QR values while excluding the filename itself.
    if extracted and primary and re.fullmatch(r"[^/\\\\\\s]+\\.(?:pdf|doc|docx|xls|xlsx|csv|txt|rtf|eml|msg|zip|rar|7z|jpg|jpeg|png|webp|gif|heic|svg)", primary.strip(), re.I):
        url_text = "\\n".join(x for x in (context, extracted, *qr_values) if x)[:MAX_INPUT_CHARS]
    urls = extract_urls(url_text, [v for v in qr_values if str(v).lower().startswith(("http://", "https://"))])'''
if old not in s:
    raise SystemExit('Target scanner line not found; refusing unsafe patch')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('Patched api/python_scan.py')
