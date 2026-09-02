#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-link-type-v1-style">
.link-type-card{margin-top:16px;padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 70%,transparent);text-align:left}.link-type-row{display:flex;align-items:center;gap:11px}.link-type-icon{display:grid;place-items:center;flex:0 0 auto;width:38px;height:38px;border-radius:11px;background:var(--card);border:1px solid var(--line);font-size:20px}.link-type-copy{min-width:0;flex:1}.link-type-kicker{display:block;margin-bottom:1px;color:var(--muted);font-size:10px;font-weight:850;text-transform:uppercase;letter-spacing:.08em}.link-type-copy strong{display:block;font-size:14px;line-height:1.2}.link-type-copy small{display:block;margin-top:2px;color:var(--muted);font-size:11px;line-height:1.35}.link-type-platform{flex:0 0 auto;max-width:150px;padding:5px 8px;border-radius:999px;background:var(--cist-accent-soft);color:var(--cist-accent);font-size:10px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media(max-width:600px){.link-type-card{padding:11px 12px}.link-type-row{gap:9px}.link-type-icon{width:36px;height:36px}.link-type-platform{max-width:105px}}
</style>
'''

TYPE_BLOCK = r'''      <section id="link-type-card" class="link-type-card hidden" aria-labelledby="link-type-title">
        <div class="link-type-row">
          <span id="link-type-icon" class="link-type-icon" aria-hidden="true">🌐</span>
          <div class="link-type-copy"><span class="link-type-kicker">What is this?</span><strong id="link-type-title">Website</strong><small id="link-type-detail">A regular web page</small></div>
          <span id="link-type-platform" class="link-type-platform hidden"></span>
        </div>
      </section>
'''

HELPERS = r'''
  function cistHostMatches(host,domain){return host===domain||host.endsWith('.'+domain)}
  function cistLinkType(data){
    var raw=String(data&&data.finalUrl||input.value||'');
    var host=String(data&&data.finalHost||'').toLowerCase().replace(/^www\./,'');
    var path='';
    try{var parsed=new URL(raw);path=String(parsed.pathname||'').toLowerCase();if(!host)host=String(parsed.hostname||'').toLowerCase().replace(/^www\./,'')}catch(e){}
    var file=(path.split('/').pop()||'').split('?')[0].split('#')[0];
    var ext=(file.match(/(\.[a-z0-9]{1,10})$/)||[])[1]||'';
    var result={icon:'🌐',label:'Website',detail:'A regular web page',platform:''};
    var audio=['.mp3','.wav','.flac','.m4a','.aac','.ogg','.opus','.wma'];
    var video=['.mp4','.webm','.mov','.mkv','.avi','.m4v','.mpeg','.mpg'];
    var images=['.jpg','.jpeg','.png','.gif','.webp','.svg','.avif','.bmp','.heic'];
    var docs=['.doc','.docx','.xls','.xlsx','.ppt','.pptx','.odt','.ods','.odp','.rtf','.txt','.csv','.epub'];
    var archives=['.zip','.rar','.7z','.gz','.tgz','.bz2','.tar'];
    var software=['.exe','.msi','.msix','.apk','.dmg','.pkg','.jar','.scr','.bat','.cmd','.ps1','.vbs','.iso','.img','.appinstaller'];
    if(software.indexOf(ext)>=0)return{icon:'💾',label:'Software or app file',detail:'A file that may install or run software',platform:ext.toUpperCase().slice(1)};
    if(archives.indexOf(ext)>=0)return{icon:'📦',label:'Compressed file',detail:'An archive that can contain one or more files',platform:ext.toUpperCase().slice(1)};
    if(ext==='.pdf')return{icon:'📄',label:'PDF document',detail:'A document that can be read or downloaded',platform:'PDF'};
    if(docs.indexOf(ext)>=0)return{icon:'📄',label:'Document or data file',detail:'A file meant to be read, edited or downloaded',platform:ext.toUpperCase().slice(1)};
    if(audio.indexOf(ext)>=0)return{icon:'🎵',label:'Music or audio',detail:'An audio file or music link',platform:ext.toUpperCase().slice(1)};
    if(video.indexOf(ext)>=0)return{icon:'🎬',label:'Video',detail:'A video file or video link',platform:ext.toUpperCase().slice(1)};
    if(images.indexOf(ext)>=0)return{icon:'🖼️',label:'Image',detail:'An image file or picture link',platform:ext.toUpperCase().slice(1)};

    if(cistHostMatches(host,'youtube.com')||cistHostMatches(host,'youtu.be'))return{icon:'🎬',label:'Video',detail:'A page for watching or sharing video',platform:'YouTube'};
    if(cistHostMatches(host,'vimeo.com'))return{icon:'🎬',label:'Video',detail:'A page for watching or sharing video',platform:'Vimeo'};
    if(cistHostMatches(host,'twitch.tv'))return{icon:'📺',label:'Live video or stream',detail:'A live-streaming or video page',platform:'Twitch'};
    if(cistHostMatches(host,'spotify.com'))return{icon:'🎵',label:'Music or audio',detail:'A music, podcast or audio page',platform:'Spotify'};
    if(cistHostMatches(host,'soundcloud.com'))return{icon:'🎵',label:'Music or audio',detail:'A music or audio page',platform:'SoundCloud'};
    if(cistHostMatches(host,'music.apple.com'))return{icon:'🎵',label:'Music or audio',detail:'A music or audio page',platform:'Apple Music'};
    if(cistHostMatches(host,'deezer.com'))return{icon:'🎵',label:'Music or audio',detail:'A music or audio page',platform:'Deezer'};
    if(cistHostMatches(host,'bandcamp.com'))return{icon:'🎵',label:'Music or audio',detail:'A music or artist page',platform:'Bandcamp'};

    if(cistHostMatches(host,'tiktok.com'))return{icon:'📱',label:'Social video',detail:'A social-media video or profile link',platform:'TikTok'};
    if(cistHostMatches(host,'instagram.com'))return{icon:'📱',label:'Social media',detail:'A post, reel, story or profile link',platform:'Instagram'};
    if(cistHostMatches(host,'facebook.com')||cistHostMatches(host,'fb.com'))return{icon:'📱',label:'Social media',detail:'A post, page, video or profile link',platform:'Facebook'};
    if(cistHostMatches(host,'x.com')||cistHostMatches(host,'twitter.com'))return{icon:'📱',label:'Social media',detail:'A post, media or profile link',platform:'X / Twitter'};
    if(cistHostMatches(host,'reddit.com'))return{icon:'💬',label:'Community or discussion',detail:'A discussion, post or community link',platform:'Reddit'};
    if(cistHostMatches(host,'linkedin.com'))return{icon:'📱',label:'Social or professional page',detail:'A professional post, profile or company page',platform:'LinkedIn'};

    if(cistHostMatches(host,'drive.google.com'))return{icon:'☁️',label:'Cloud file or folder',detail:'A shared file or folder stored online',platform:'Google Drive'};
    if(cistHostMatches(host,'docs.google.com'))return{icon:'📄',label:'Online document',detail:'A shared document, sheet, form or presentation',platform:'Google Docs'};
    if(cistHostMatches(host,'dropbox.com')||cistHostMatches(host,'dropboxusercontent.com'))return{icon:'☁️',label:'Cloud file or folder',detail:'A shared file or folder stored online',platform:'Dropbox'};
    if(cistHostMatches(host,'onedrive.live.com')||cistHostMatches(host,'1drv.ms'))return{icon:'☁️',label:'Cloud file or folder',detail:'A shared file or folder stored online',platform:'OneDrive'};
    if(cistHostMatches(host,'sharepoint.com'))return{icon:'☁️',label:'Cloud file or work document',detail:'A shared work file, folder or page',platform:'SharePoint'};
    if(cistHostMatches(host,'icloud.com'))return{icon:'☁️',label:'Cloud file or shared page',detail:'Content shared through Apple iCloud',platform:'iCloud'};
    if(cistHostMatches(host,'wetransfer.com')||cistHostMatches(host,'we.tl'))return{icon:'☁️',label:'File transfer',detail:'A link used to send or download files',platform:'WeTransfer'};
    if(cistHostMatches(host,'notion.so')||cistHostMatches(host,'notion.site'))return{icon:'📄',label:'Online document or workspace',detail:'A shared page or workspace',platform:'Notion'};

    if(cistHostMatches(host,'amazon.com')||cistHostMatches(host,'amazon.fr')||cistHostMatches(host,'ebay.com')||cistHostMatches(host,'etsy.com')||cistHostMatches(host,'aliexpress.com'))return{icon:'🛒',label:'Shopping link',detail:'A product, shop or marketplace page',platform:host.indexOf('amazon.')>=0?'Amazon':host.indexOf('ebay.')>=0?'eBay':host.indexOf('etsy.')>=0?'Etsy':'AliExpress'};
    if(cistHostMatches(host,'whatsapp.com')||cistHostMatches(host,'wa.me'))return{icon:'💬',label:'Message or contact link',detail:'A chat, contact or group link',platform:'WhatsApp'};
    if(cistHostMatches(host,'t.me')||cistHostMatches(host,'telegram.me'))return{icon:'💬',label:'Message or group link',detail:'A chat, channel, contact or group link',platform:'Telegram'};
    if(cistHostMatches(host,'discord.com')||cistHostMatches(host,'discord.gg'))return{icon:'💬',label:'Chat or invite link',detail:'A Discord page, server invite or message link',platform:'Discord'};
    if(cistHostMatches(host,'github.com'))return{icon:'🧩',label:'Code or developer link',detail:'A repository, release, issue or developer page',platform:'GitHub'};

    var shorteners=['bit.ly','tinyurl.com','t.co','rb.gy','rebrand.ly','is.gd','cutt.ly','tiny.cc','ow.ly','lnkd.in'];
    if(shorteners.some(function(d){return cistHostMatches(host,d)}))return{icon:'🔗',label:'Shortened link',detail:'A short link that forwards to another destination',platform:host};
    return result;
  }
  function renderLinkType(data){
    var panel=document.getElementById('link-type-card'),iconEl=document.getElementById('link-type-icon'),titleEl=document.getElementById('link-type-title'),detailEl=document.getElementById('link-type-detail'),platformEl=document.getElementById('link-type-platform');
    if(!panel||!iconEl||!titleEl||!detailEl||!platformEl)return;
    var t=cistLinkType(data||{});iconEl.textContent=t.icon;titleEl.textContent=t.label;detailEl.textContent=t.detail;
    if(t.platform){platformEl.textContent=t.platform;platformEl.classList.remove('hidden')}else{platformEl.textContent='';platformEl.classList.add('hidden')}
    panel.classList.remove('hidden');
  }
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Link type V1 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-link-type-v1-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    if 'id="link-type-card"' not in source:
        source = replace_once(source, '      <section id="why-verdict"', TYPE_BLOCK + '      <section id="why-verdict"', 'result placement')

    if 'function cistLinkType(data)' not in source:
        source = replace_once(source, '  function renderQuick(data){', HELPERS + '  function renderQuick(data){renderLinkType(data);', 'result renderer')

    if "function loading(){var linkTypePanel=" not in source:
        source = replace_once(source, '  function loading(){', "  function loading(){var linkTypePanel=document.getElementById('link-type-card');if(linkTypePanel)linkTypePanel.classList.add('hidden');", 'new scan reset')

    required = [
        'id="link-type-card"',
        'What is this?',
        'Music or audio',
        'Software or app file',
        "cistHostMatches(host,'youtube.com')",
        "cistHostMatches(host,'spotify.com')",
        "cistHostMatches(host,'drive.google.com')",
        'renderQuick(data){renderLinkType(data);',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Link type V1 guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied lightweight universal link type detection V1')


if __name__ == '__main__':
    main()
