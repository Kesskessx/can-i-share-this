#!/usr/bin/env python3
from pathlib import Path

DIST = Path(__file__).resolve().parents[1] / 'dist'

REPLACEMENTS = {
    'Images selected through <strong>Photo</strong> or <strong>Camera</strong> are sent to the image-analysis endpoint and then to Google Gemini for visual interpretation. Can I Share This? does not intentionally write those image bytes to persistent application storage.':
    'Images selected through <strong>Photo</strong> or <strong>Camera</strong> are processed in the browser for OCR and QR extraction. Raw image bytes are not sent to Google Gemini by the Gemini-free image scanner.',
    "Google is an external processor for this feature, so the image leaves Can I Share This? infrastructure during analysis. Provider-side handling is governed by Google's applicable Gemini/API terms and account configuration.":
    'Extracted text, links and QR destinations may then be sent to Can I Share This? for deterministic safety checks. The scanner does not require a vision-AI provider for this flow.',
    '<li><strong>Google Gemini</strong> for screenshot and photo interpretation;</li>':
    '<li><strong>Local browser OCR and QR decoding</strong> for screenshot and photo evidence extraction;</li>',
    'AI is used for interpreting images and context, not as the sole authority for link safety.':
    'Image evidence is extracted locally in the browser and combined with deterministic technical checks; no AI opinion is required for the image-safety flow.',
    'Screenshot and photo analysis uses Google Gemini to interpret visible content such as text, brand clues, links and suspicious context. The AI result is combined with technical checks when a URL, email or QR destination can be extracted; AI is not treated as the sole proof that something is safe or dangerous.':
    'Screenshot and photo analysis uses local browser OCR and QR decoding to extract visible text, links and destinations. Extracted evidence is then combined with technical checks; raw image bytes are not required by the Gemini-free safety flow.',
    'Uploaded image bytes are processed transiently by Can I Share This? and sent to the external AI provider for analysis.':
    'Image OCR and QR extraction are performed locally in the browser when supported; extracted evidence is then analyzed by the safety pipeline.'
}

changed = 0
for name in ('security.html', 'methodology.html'):
    path = DIST / name
    if not path.is_file():
        continue
    text = path.read_text(encoding='utf-8')
    before = text
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    if text != before:
        path.write_text(text, encoding='utf-8')
        changed += 1

print(f'Applied Gemini-free transparency copy to {changed} page(s)')
