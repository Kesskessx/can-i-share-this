#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-universal-result-v12-style">
.universal-summary{margin-top:14px;text-align:left}.universal-summary-heading{margin:0 0 8px;color:var(--muted);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.universal-summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.universal-summary-item{min-width:0;display:grid;gap:4px;padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--soft) 64%,transparent)}.universal-summary-label{display:block;margin:0;color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.06em;text-transform:uppercase}.universal-summary-value{display:block;color:var(--text);font-size:13px;font-weight:850;line-height:1.28;overflow-wrap:anywhere}.universal-summary-note{display:block;margin:0;color:var(--muted);font-size:10px;line-height:1.35;overflow-wrap:anywhere}.universal-summary-item.safety-good .universal-summary-value{color:var(--green)}.universal-summary-item.safety-warn .universal-summary-value{color:var(--amber)}.universal-summary-item.safety-bad .universal-summary-value{color:var(--red)}.redirect-route{margin-top:9px;padding:10px 12px;border:1px solid color-mix(in srgb,var(--amber) 28%,var(--line));border-radius:12px;background:color-mix(in srgb,var(--amber) 5%,var(--card));text-align:left}.redirect-route strong{display:block;font-size:11px;line-height:1.35}.redirect-route span{display:block;margin-top:3px;color:var(--muted);font-size:10px;line-height:1.4;overflow-wrap:anywhere}
@media(max-width:600px){.universal-summary-grid{grid-template-columns:1fr}.universal-summary-item{padding:10px 11px}.universal-summary-value{font-size:12px}}
</style>
'''

BLOCK = r'''      <section id="universal-summary" class="universal-summary hidden" aria-labelledby="universal-summary-heading">
        <h3 id="universal-summary-heading" class="universal-summary-heading">At a glance</h3>
        <div class="universal-summary-grid">
          <div id="universal-safety" class="universal-summary-item"><span class="universal-summary-label">Safety</span><strong id="universal-safety-value" class="universal-summary-value">Checking…</strong><small id="universal-safety-note" class="universal-summary-note">Waiting for the full safety check.</small></div>
          <div class="universal-summary-item"><span class="universal-summary-label">Content</span><strong id="universal-content-value" class="universal-summary-value">Website</strong><small id="universal-content-note" class="universal-summary-note">A regular web page</small></div>
          <div class="universal-summary-item"><span class="universal-summary-label">Destination</span><strong id="universal-destination-value" class="universal-summary-value">—</strong><small id="universal-destination-note" class="universal-summary-note">Final website after redirects</small></div>
          <div class="universal-summary-item"><span class="universal-summary-label">Advice</span><strong id="universal-advice-value" class="universal-summary-value">Check the website name before opening.</strong><small id="universal-advice-note" class="universal-summary-note">The result is guidance, not a guarantee.</small></div>
        </div>
        <div id="redirect-route" class="redirect-route hidden"><strong>This link changes destination</strong><span id="redirect-route-text"></span></div>
      </section>
'''

HELPERS = r'''
  function cistFileExt(name){var m=String(name||'').toLowerCase().match(/(\.[a-z0-9]{1,12})$/);return m?m[1]:''}
  function cistTypeFromResponse(data){
    var mime=String(data&&data.contentType||'').toLowerCase().split(';')[0].trim();
    var ext=cistFileExt(data&&data.fileName||'');
    function out(icon,label,detail,badge,kind){return{icon:icon,label:label,detail:detail,badge:badge||'',kind:kind||''}}
    if(mime==='application/pdf'||ext==='.pdf')return out('📄','PDF document','The server says this is a PDF file','PDF','document');
    if(mime.indexOf('audio/')===0)return out('🎵','Music or audio','The server says this is audio',mime.split('/')[1].toUpperCase(),'audio');
    if(mime.indexOf('video/')===0)return out('🎬','Video','The server says this is video',mime.split('/')[1].toUpperCase(),'video');
    if(mime.indexOf('image/')===0)return out('🖼️','Image','The server says this is an image',mime.split('/')[1].toUpperCase(),'image');
    if(['application/zip','application/x-zip-compressed','application/x-rar-compressed','application/vnd.rar','application/x-7z-compressed','application/gzip','application/x-tar'].indexOf(mime)>=0)return out('📦','Compressed file','The server says this is a compressed archive','Archive','archive');
    if(['application/x-msdownload','application/x-msdos-program','application/vnd.microsoft.portable-executable','application/vnd.android.package-archive','application/java-archive','application/x-apple-diskimage'].indexOf(mime)>=0)return out('💾','Software or app file','The server returned an installable or executable file','Download','software');
    if(mime==='application/octet-stream')return out('💾','Downloadable file','The server returned a generic downloadable file','Download','download');
    if(mime.indexOf('application/vnd.openxmlformats-officedocument')===0||mime.indexOf('application/msword')===0||mime.indexOf('application/vnd.ms-')===0||mime==='text/csv'||mime==='text/plain')return out('📄','Document or data file','The server says this is a document or data file','File','document');
    return null;
  }
  function cistApplyServerType(data){
    var t=cistTypeFromResponse(data);if(!t)return null;
    var icon=document.getElementById('link-type-icon'),title=document.getElementById('link-type-title'),detail=document.getElementById('link-type-detail'),platform=document.getElementById('link-type-platform');
    if(icon)icon.textContent=t.icon;if(title)title.textContent=t.label;if(detail)detail.textContent=t.detail;
    if(platform){platform.textContent=t.badge;if(t.badge)platform.classList.remove('hidden');else platform.classList.add('hidden')}
    return t;
  }
  function cistHostOnly(value){try{return new URL(String(value||'')).hostname.toLowerCase().replace(/^www\./,'')}catch(e){return''}}
  function cistRedirectInfo(data){
    var hosts=[];function push(h){if(h&&hosts[hosts.length-1]!==h)hosts.push(h)}
    push(cistHostOnly(input.value));
    (Array.isArray(data&&data.redirects)?data.redirects:[]).forEach(function(r){push(cistHostOnly(r&&r.url))});
    push(String(data&&data.finalHost||'').toLowerCase().replace(/^www\./,''));
    return{count:Array.isArray(data&&data.redirects)?data.redirects.length:0,hosts:hosts};
  }
  function cistAdviceFor(typeLabel,sensitive){
    var x=String(typeLabel||'').toLowerCase();
    if(sensitive){var s=String(sensitive.typeLabel||'').toLowerCase();if(s.indexOf('gambling')>=0)return['Real-money gambling can lead to financial loss.','This type of content may also be age-restricted.'];if(s.indexOf('adult')>=0)return['This page may contain age-restricted material.','Open it only if that is what you expected.'];if(s.indexOf('crypto')>=0)return['Double-check the exact website before sending money or crypto.','Financial links are common targets for impersonation scams.'];if(s.indexOf('torrent')>=0)return['Files from sharing sites deserve extra caution.','Check the source and what you are allowed to download.'];if(s.indexOf('weapons')>=0||s.indexOf('drug')>=0)return['This page may contain regulated or age-restricted content.','Rules can vary by location.']}
    if(x.indexOf('software')>=0||x.indexOf('downloadable')>=0)return['Unexpected software can harm your device.','Only run files you deliberately requested from a source you trust.'];
    if(x.indexOf('compressed')>=0)return['Compressed files can hide other files inside.','Check the sender and inspect the contents before opening them.'];
    if(x.indexOf('shortened')>=0)return['Short links hide the real website until they are followed.','Confirm the final destination shown here.'];
    if(x.indexOf('document')>=0||x.indexOf('pdf')>=0)return['Documents can contain links or prompts that ask for sensitive information.','Check who sent it before trusting instructions inside.'];
    return['Check that you recognize the final website.','Be cautious if it asks for a password, payment or download.'];
  }
  function cistUniversalSafety(){
    var card=document.getElementById('result-card'),verdict=document.getElementById('verdict');var text=String(verdict&&verdict.textContent||'');var lower=text.toLowerCase();
    if(card&&card.classList.contains('status-high'))return{value:'Dangerous warning signs',note:'Do not open this link unless you can independently verify it.',cls:'safety-bad'};
    if(card&&card.classList.contains('status-caution'))return{value:'Be careful',note:'Some checks found warning signs or could not be completed.',cls:'safety-warn'};
    if((card&&card.classList.contains('reputation-checked-safe'))||lower.indexOf('no known threat found')>=0||lower.indexOf('no known danger reported')>=0)return{value:'No known threat found',note:'Nothing dangerous was reported by the known threat lists checked.',cls:'safety-good'};
    if((card&&card.classList.contains('one-click-running'))||lower.indexOf('checking')>=0)return{value:'Checking safety…',note:'Checking the link and known online threat lists.',cls:''};
    return{value:'No obvious local warning signs',note:'The full online threat-list result may still be pending.',cls:''};
  }
  function cistUpdateUniversalSummary(){
    var data=window.cistUniversalResultData;if(!data)return;
    var panel=document.getElementById('universal-summary');if(!panel)return;
    var serverType=cistApplyServerType(data);
    var typeTitle=document.getElementById('link-type-title'),typeDetail=document.getElementById('link-type-detail'),contentValue=document.getElementById('universal-content-value'),contentNote=document.getElementById('universal-content-note');
    var typeLabel=String(typeTitle&&typeTitle.textContent||serverType&&serverType.label||'Website');
    if(contentValue)contentValue.textContent=typeLabel;
    if(contentNote){var note=String(typeDetail&&typeDetail.textContent||'A regular web page');if(data.fileName)note+=' · '+String(data.fileName).slice(0,90);contentNote.textContent=note}
    var dest=document.getElementById('universal-destination-value'),destNote=document.getElementById('universal-destination-note');var finalHost=String(data.finalHost||cistHostOnly(data.finalUrl)||'Unknown destination').replace(/^www\./,'');
    if(dest)dest.textContent=finalHost;
    var route=cistRedirectInfo(data);if(destNote)destNote.textContent=route.count?route.count+' redirect'+(route.count===1?'':'s')+' followed':'Direct destination';
    var routeBox=document.getElementById('redirect-route'),routeText=document.getElementById('redirect-route-text');
    if(routeBox&&routeText&&route.count>0&&route.hosts.length>1){routeText.textContent=route.hosts.join(' → ');routeBox.classList.remove('hidden')}else if(routeBox){routeBox.classList.add('hidden')}
    var safety=cistUniversalSafety(),safetyBox=document.getElementById('universal-safety'),safetyValue=document.getElementById('universal-safety-value'),safetyNote=document.getElementById('universal-safety-note');if(safetyValue)safetyValue.textContent=safety.value;if(safetyNote)safetyNote.textContent=safety.note;if(safetyBox){safetyBox.classList.remove('safety-good','safety-warn','safety-bad');if(safety.cls)safetyBox.classList.add(safety.cls)}
    var advice=cistAdviceFor(typeLabel,window.cistSensitiveCategoryCurrent),typeLower=typeLabel.toLowerCase();var special=window.cistSensitiveCategoryCurrent||/(software|downloadable|compressed|shortened|document|pdf)/.test(typeLower);if(safety.cls==='safety-good'&&!special)advice=['Continue only if you expected this link.','Be cautious if it asks for a password, payment or download.'];var adviceValue=document.getElementById('universal-advice-value'),adviceNote=document.getElementById('universal-advice-note');if(adviceValue)adviceValue.textContent=advice[0];if(adviceNote)adviceNote.textContent=advice[1];
    var oldType=document.getElementById('link-type-card');if(oldType)oldType.classList.add('hidden');
    panel.classList.remove('hidden');
  }
  function renderUniversalResult(data){window.cistUniversalResultData=data||{};cistUpdateUniversalSummary()}
'''

OBSERVER = r'''
<script id="cist-universal-result-v12-observer">
(function(){
  document.addEventListener('cist:result-updated',function(){if(window.cistUniversalResultData)cistUpdateUniversalSummary()});
})();
</script>
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Universal result V1.2 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-universal-result-v12-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    if 'id="universal-summary"' not in source:
        source = replace_once(source, '      <section id="link-type-card"', BLOCK + '      <section id="link-type-card"', 'summary placement')

    if 'function cistTypeFromResponse(data)' not in source:
        source = replace_once(source, '  function cistSensitiveHost(host,domains)', HELPERS + '  function cistSensitiveHost(host,domains)', 'helper insertion')

    source = replace_once(
        source,
        '  function renderQuick(data){renderLinkType(data);renderSensitiveCategory(data);',
        '  function renderQuick(data){renderLinkType(data);renderSensitiveCategory(data);renderUniversalResult(data);',
        'result hook'
    )

    old_loading = "window.cistSensitiveCategoryCurrent=null;"
    new_loading = "window.cistSensitiveCategoryCurrent=null;window.cistUniversalResultData=null;var universalPanel=document.getElementById('universal-summary');if(universalPanel)universalPanel.classList.add('hidden');var redirectPanel=document.getElementById('redirect-route');if(redirectPanel)redirectPanel.classList.add('hidden');"
    source = replace_once(source, old_loading, new_loading, 'new scan reset')

    if 'id="cist-universal-result-v12-observer"' not in source:
        source = source.replace('</body>', OBSERVER + '\n</body>', 1)

    required = [
        'id="universal-summary"', 'At a glance', 'Safety', 'Content', 'Destination', 'Advice',
        'function cistTypeFromResponse(data)', 'application/pdf', 'application/x-msdownload',
        'This link changes destination', "route.hosts.join(' → ')",
        'Unexpected software can harm your device.', 'Compressed files can hide other files inside.',
        'Short links hide the real website until they are followed.',
        "document.addEventListener('cist:result-updated'",
        'renderSensitiveCategory(data);renderUniversalResult(data);',
        "value:'No known threat found'", 'Nothing dangerous was reported by the known threat lists checked.'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Universal result V1.2 guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied universal result V1.2 with synchronized final safety state and concise copy')


if __name__ == '__main__':
    main()
