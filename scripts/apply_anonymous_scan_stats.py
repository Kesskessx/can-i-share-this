#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Anonymous scan stats patch failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    old_track = "  function track(event){try{var b=new Blob([JSON.stringify({event:event})],{type:'application/json'});navigator.sendBeacon('/api/event',b)}catch(e){}}"
    new_track = "  function track(event,payload){try{var body={event:event};if(payload&&typeof payload==='object'){Object.keys(payload).forEach(function(k){body[k]=payload[k]})}var b=new Blob([JSON.stringify(body)],{type:'application/json'});navigator.sendBeacon('/api/event',b)}catch(e){}}\n  function trackScanSummary(data){try{var s=data&&data.safety?data.safety:{};var status=['low','caution','high'].indexOf(s.status)>=0?s.status:'unknown';var sig=Array.isArray(s.signals)?s.signals:[];var codes=sig.map(function(x){return String(x&&x.code||'')});var has=function(code){return codes.indexOf(code)>=0};var starts=function(prefix){return codes.some(function(code){return code.indexOf(prefix)===0})};track('scan_result',{status:status,redirected:Array.isArray(data&&data.redirects)&&data.redirects.length>0,shortened:has('shortener'),phishing:has('phishing-language')||starts('brand-'),lookalike:starts('brand-')||has('punycode'),domain_changed:has('domain-change'),risky_download:has('executable-download')||has('binary-content')||has('forced-download')||has('archive-download')})}catch(e){}}"
    source = replace_once(source, old_track, new_track, 'tracking helper')

    old_scan = "try{var r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})});renderQuick(await r.json())}catch(e)"
    new_scan = "try{var r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})});var d=await r.json();renderQuick(d);trackScanSummary(d)}catch(e)"
    source = replace_once(source, old_scan, new_scan, 'scan result telemetry')

    # Privacy guardrails: the telemetry helper must never serialize the scanned URL or hostname.
    helper = source[source.index('function trackScanSummary'):source.index('function busy', source.index('function trackScanSummary'))]
    forbidden = ['currentUrl', 'finalHost', 'hostname', 'rawInput', 'query', 'finalUrl']
    for token in forbidden:
        if token in helper:
            raise RuntimeError(f'Privacy guard failed: {token} found in aggregate telemetry helper')

    HOME.write_text(source, encoding='utf-8')
    print('Applied anonymous aggregate scan telemetry without URLs or hostnames')


if __name__ == '__main__':
    main()
