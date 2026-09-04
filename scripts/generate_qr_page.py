#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>QR Code Link Checker — Check Before You Scan</title>
  <meta name="description" content="Scan a QR code with your phone camera or choose an image, reveal its link without opening it, and check the destination with Can I Share This?.">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://canisharethis.com/qr-code-link-checker">
  <style>
    :root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#6d7480;--line:#e2e5e9;--button:#17191d;--buttonText:#fff;--soft:#f1f3f5}
    @media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--button:#f4f5f7;--buttonText:#111318;--soft:#1c2026}}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}button{font:inherit}header{height:64px;border-bottom:1px solid var(--line);display:flex;align-items:center}.top{width:min(760px,calc(100% - 32px));margin:auto}.brand{text-decoration:none;font-weight:850}.wrap{width:min(680px,calc(100% - 28px));margin:auto;padding:clamp(42px,8vw,82px) 0 70px;text-align:center}h1{font-size:clamp(38px,7vw,60px);line-height:1;letter-spacing:-.05em;margin:0}.sub{max-width:560px;margin:18px auto 28px;color:var(--muted);font-size:18px}.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:20px;box-shadow:0 18px 50px rgba(17,24,39,.08)}.primary,.secondary,.upload{width:100%;min-height:54px;border-radius:14px;font-weight:850;cursor:pointer;display:flex;align-items:center;justify-content:center}.primary{border:1px solid var(--button);background:var(--button);color:var(--buttonText)}.secondary,.upload{border:1px solid var(--line);background:var(--soft);color:var(--text)}.upload{margin-top:10px}.upload input{position:absolute;opacity:0;pointer-events:none}.small{font-size:12px;color:var(--muted);margin:12px 0 0}.status{margin-top:14px;padding:13px 14px;border-radius:12px;background:var(--soft);text-align:left}.hidden{display:none!important}.camera{position:relative;margin-top:14px;border-radius:18px;overflow:hidden;background:#050505;aspect-ratio:3/4;max-height:62vh}.camera video{width:100%;height:100%;object-fit:cover;display:block}.target{position:absolute;left:50%;top:50%;width:min(68vw,250px);height:min(68vw,250px);transform:translate(-50%,-50%);border:3px solid rgba(255,255,255,.94);border-radius:22px;box-shadow:0 0 0 999px rgba(0,0,0,.18);pointer-events:none}.camera-note{position:absolute;left:12px;right:12px;bottom:12px;padding:8px 10px;border-radius:10px;background:rgba(0,0,0,.64);color:#fff;font-size:13px}.stop{margin-top:10px}.info{margin-top:18px;padding:20px;text-align:left;border:1px solid var(--line);border-radius:18px;background:var(--card)}.info h2{margin:0 0 8px;font-size:19px}.info p{margin:0;color:var(--muted)}.info p+h2{margin-top:18px}.back{display:inline-block;margin-top:22px;font-size:14px;color:var(--muted)}
  </style>
</head>
<body>
<header><div class="top"><a class="brand" href="/">↗ Can I Share This?</a></div></header>
<main class="wrap">
  <p style="margin:0 0 12px;color:var(--muted);font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.08em">QR safety scanner</p>
  <h1>Check the QR before opening it.</h1>
  <p class="sub">Point your phone camera at a QR code. We reveal the destination without visiting it, then pass the URL to the safety checker.</p>
  <div class="card">
    <button id="camera-start" class="primary" type="button">Use camera to scan QR</button>
    <label class="upload">Choose QR image<input id="qr-file" type="file" accept="image/*" capture="environment"></label>
    <p class="small">Camera and image decoding happen in your browser. Reading the QR does not open its destination.</p>
    <div id="camera-box" class="camera hidden">
      <video id="camera-video" playsinline muted></video>
      <div class="target" aria-hidden="true"></div>
      <div class="camera-note">Hold the QR code inside the frame</div>
    </div>
    <button id="camera-stop" class="secondary stop hidden" type="button">Stop camera</button>
    <div id="qr-status" class="status hidden" aria-live="polite"></div>
  </div>
  <section class="info">
    <h2>What happens next</h2>
    <p>The QR payload is decoded first. If it contains an HTTP or HTTPS address, the destination is transferred to Can I Share This? for its normal checks. The scanner does not navigate to that destination.</p>
    <h2>What this cannot prove</h2>
    <p>A readable code and a clean URL result do not authenticate the person, sign, invoice or payment request around it. For payments or account access, independently verify the final domain or use the official app.</p>
  </section>
  <a class="back" href="/">← Paste a link instead</a>
</main>
<script>
(function(){
  var file=document.getElementById('qr-file'),status=document.getElementById('qr-status');
  var start=document.getElementById('camera-start'),stop=document.getElementById('camera-stop');
  var box=document.getElementById('camera-box'),video=document.getElementById('camera-video');
  var stream=null,running=false,detector=null,lastDetect=0;
  function show(msg){status.textContent=msg;status.classList.remove('hidden')}
  function supported(){return 'BarcodeDetector' in window}
  function stopCamera(){running=false;if(stream){stream.getTracks().forEach(function(t){t.stop()});stream=null}video.srcObject=null;box.classList.add('hidden');stop.classList.add('hidden');start.classList.remove('hidden')}
  function finish(value){value=(value||'').trim();if(!value)return false;stopCamera();if(!/^https?:\/\//i.test(value)){show('QR found, but it does not contain a normal HTTP or HTTPS web link.');return true}try{sessionStorage.setItem('cist_pending_url',value)}catch(e){}show('Link found. Opening the safety checker…');location.href='/';return true}
  async function detectLoop(ts){if(!running)return;if(ts-lastDetect>180&&video.readyState>=2){lastDetect=ts;try{var codes=await detector.detect(video);if(codes&&codes[0]&&finish(codes[0].rawValue))return}catch(e){}}requestAnimationFrame(detectLoop)}
  start.addEventListener('click',async function(){
    if(!supported()){show('Live QR detection is not supported by this browser. Use “Choose QR image” instead.');return}
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){show('Camera access is not available in this browser. Use “Choose QR image” instead.');return}
    show('Requesting camera permission…');
    try{
      detector=new BarcodeDetector({formats:['qr_code']});
      stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'},width:{ideal:1280},height:{ideal:1280}},audio:false});
      video.srcObject=stream;await video.play();running=true;start.classList.add('hidden');box.classList.remove('hidden');stop.classList.remove('hidden');show('Camera ready. Point it at a QR code.');requestAnimationFrame(detectLoop)
    }catch(e){stopCamera();show(e&&e.name==='NotAllowedError'?'Camera permission was denied. Allow camera access in your browser settings or choose a QR image.':'The camera could not be started. Choose a QR image instead.')}
  });
  stop.addEventListener('click',function(){stopCamera();show('Camera stopped.')});
  file.addEventListener('change',async function(){
    var f=file.files&&file.files[0];if(!f)return;if(!supported()){show('QR image decoding is not supported by this browser. Try Chrome on Android.');return}show('Reading QR code…');
    try{var imageDetector=new BarcodeDetector({formats:['qr_code']});var bitmap=await createImageBitmap(f);var codes=await imageDetector.detect(bitmap);bitmap.close&&bitmap.close();if(!(codes&&codes[0]&&finish(codes[0].rawValue)))show('No QR code was found. Try a clearer image or use the camera scanner.')}catch(e){show('We could not read this QR code. Try a clearer image or use the camera scanner.')}
  });
  document.addEventListener('visibilitychange',function(){if(document.hidden&&running)stopCamera()});window.addEventListener('pagehide',stopCamera);
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
