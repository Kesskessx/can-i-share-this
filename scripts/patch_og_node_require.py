#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'lib' / 'shared-result-render.js'
text = path.read_text(encoding='utf-8')
anchor = "const React = require('react');"
static_import = "const { ImageResponse } = require('@vercel/og');"
dynamic_import = "  const { ImageResponse } = await import('@vercel/og');\n"

if static_import not in text:
    if anchor not in text:
        raise SystemExit('React import anchor not found')
    text = text.replace(anchor, anchor + "\n" + static_import, 1)
text = text.replace(dynamic_import, '', 1)
path.write_text(text, encoding='utf-8')
print('Patched @vercel/og to use static CommonJS require in Node runtime')
