#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>QR Code Link Checker — Check Before You Scan</title>
  <meta name="description" content="Upload a screenshot of a suspicious QR code, reveal its link without opening it, and send it to the Can I Share This? safety checker.">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://canisharethis.com/qr-code-link-checker">
  <style>
    :root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#6d7480;--line:#e2e5e9;--button:#17191d;--buttonText:#fff;--soft:#f1f3f5}
    @media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--button:#f4f5f7;--buttonText:#111318;--soft:#1c2026}}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}header{height:64px;border-bottom:1px solid var(--line);display:flex;align-items:center}.top{width:min(760px,calc(100% - 32px));margin:auto}.brand{text-decoration:none;font-weight:850}.wrap{width:min(680px,calc(100% - 28px));margin:auto;padding:clamp(52px,9vw,92px) 0 70px;text-align:center}h1{font-size:clamp(38px,7vw,60px);line-height:1;letter-spacing:-.05em;margin:0}.sub{max-width:560px;margin:18px auto 28px;color:var(--muted);font-size:18px}.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:24px;box-shadow:0 18px 50px rgba(17,24,39,.08)}.upload{display:block;border:1px dashed var(--line);border-radius:16px;padding:28px 18px;background:var(--soft);cursor:pointer;font-weight:800}.upload input{position:absolute;opacity:0;pointer-events:none}.small{font-size:12px;color:var(--muted);margin:12px 0 0}.status{margin-top:16px;padding:13px 14px;border-radius:12px;background:var(--soft);text-align:left}.hidden{display:none!important}.back{display:inline-block;margin-top:22px;font-size:14px;color:var(--muted)}
  </style>
</head>
<body>
<header><div class="top"><a class="brand" href="/">↗ Can I Share This?</a></div></header>
<main class="wrap">
  <p style="margin:0 0 12px;color:var(--muted);font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.08em">QR safety scanner</p>
  <h1>Don’t scan it yet.</h1>
  <p class="sub">Upload a screenshot of a suspicious QR code. We’ll reveal the link without opening it, then check it on the homepage.</p>
  <div class="card">
    <label class="upload">Choose QR screenshot<input id="qr-file" type="file" accept="image/*"></label>
    <p class="small">Your image stays in your browser and is not uploaded to our server.</p>
    <div id="qr-status" class="status hidden" aria-live="polite"></div>
  </div>
  <a class="back" href="/">← Paste a link instead</a>
</main>
<script>
(function(){
  var file=document.getElementById('qr-file'),status=document.getElementById('qr-status');
  function show(msg){status.textContent=msg;status.classList.remove('hidden')}
  file.addEventListener('change',async function(){
    var f=file.files&&file.files[0];if(!f)return;
    if(!('BarcodeDetector' in window)){show('QR scanning is not supported by this browser yet. Try Chrome on Android, or paste the link on the homepage.');return}
    show('Reading QR code…');
    try{
      var detector=new BarcodeDetector({formats:['qr_code']});
      var bitmap=await createImageBitmap(f);
      var codes=await detector.detect(bitmap);
      bitmap.close&&bitmap.close();
      var value=(codes[0]&&codes[0].rawValue||'').trim();
      if(!value){show('No QR code was found in this image. Try a clearer screenshot.');return}
      if(!/^https?:\/\//i.test(value)){show('A QR code was found, but it does not contain a normal web link.');return}
      sessionStorage.setItem('cist_pending_url',value);
      show('Link found. Opening the safety checker…');
      location.href='/';
    }catch(e){show('We could not read this QR code. Try a clearer screenshot or paste the link manually.');}
  });
})();
</script>
</body>
</html>'''


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / 'qr-code-link-checker.html').write_text(HTML, encoding='utf-8')
    sitemap = DIST / 'sitemap.xml'
    if sitemap.exists():
        source = sitemap.read_text(encoding='utf-8')
        url = 'https://canisharethis.com/qr-code-link-checker'
        if url not in source:
            block = f'<url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
            source = source.replace('</urlset>', block + '</urlset>')
            sitemap.write_text(source, encoding='utf-8')
    print('Generated QR code safety scanner page')

if __name__ == '__main__':
    main()
