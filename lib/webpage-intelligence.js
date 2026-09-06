'use strict';

const dns=require('node:dns').promises;
const net=require('node:net');
const { detectBrandClaims, brandDomainStatus, normalizeHost }=require('./brand-registry');

const MAX_HTML=160*1024;
const MAX_REDIRECTS=3;
function clean(v,max=1200){return String(v==null?'':v).replace(/\0/g,'').replace(/\s+/g,' ').trim().slice(0,max)}
function isPrivateIPv4(ip){const p=String(ip).split('.').map(Number);return p.length!==4||p.some(n=>!Number.isInteger(n))||p[0]===10||p[0]===127||p[0]===0||(p[0]===169&&p[1]===254)||(p[0]===172&&p[1]>=16&&p[1]<=31)||(p[0]===192&&p[1]===168)||(p[0]===100&&p[1]>=64&&p[1]<=127)||p[0]>=224}
function isPrivateIPv6(ip){const x=String(ip||'').toLowerCase();return x==='::1'||x==='::'||x.startsWith('fc')||x.startsWith('fd')||x.startsWith('fe8')||x.startsWith('fe9')||x.startsWith('fea')||x.startsWith('feb')}
function isPrivateIp(ip){const f=net.isIP(ip);return f===4?isPrivateIPv4(ip):f===6?isPrivateIPv6(ip):true}
async function ensurePublic(host){const rows=await Promise.race([dns.lookup(host,{all:true,verbatim:true}),new Promise((_,r)=>setTimeout(()=>r(new Error('DNS timeout')),1300))]);if(!rows.length||rows.some(x=>isPrivateIp(x.address)))throw new Error('Private host')}
function attr(tag,name){const m=String(tag||'').match(new RegExp('\\b'+name+'\\s*=\\s*(["\\\'])([\\s\\S]*?)\\1','i'));return m?m[2]:''}
function tags(html,name){return String(html||'').match(new RegExp('<'+name+'\\b[^>]*>','gi'))||[]}
function titleText(html){const m=String(html||'').match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);return clean(m?m[1].replace(/<[^>]+>/g,' '):'',300)}
function metaDescription(html){const metas=tags(html,'meta');for(const tag of metas){const n=(attr(tag,'name')||attr(tag,'property')).toLowerCase();if(n==='description'||n==='og:description')return clean(attr(tag,'content'),500)}return''}
function baseDomain(host){const x=normalizeHost(host),p=x.split('.').filter(Boolean);if(p.length<=2)return x;const cc=new Set(['co.uk','org.uk','com.au','co.jp','co.nz','com.br']);const last=p.slice(-2).join('.');return cc.has(last)?p.slice(-3).join('.'):last}
function sameSite(a,b){return baseDomain(a)===baseDomain(b)}
function safeTarget(action,base){try{return new URL(action||base,base)}catch(_){return null}}
function unique(items,key=x=>String(x),max=20){const out=[],seen=new Set();for(const x of items||[]){const k=key(x);if(!k||seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=max)break}return out}
async function readHtml(response){if(!response.body)return'';const reader=response.body.getReader();const parts=[];let total=0;try{while(total<MAX_HTML){const {done,value}=await reader.read();if(done)break;const rem=MAX_HTML-total,part=value.byteLength>rem?value.slice(0,rem):value;parts.push(Buffer.from(part));total+=part.byteLength;if(part.byteLength<value.byteLength)break}}finally{try{await reader.cancel()}catch(_){}}return Buffer.concat(parts).toString('utf8')}

function inspectHtml(html,url){
  const host=normalizeHost(url),findings=[],forms=[];
  const inputTags=tags(html,'input');
  const passwordInputs=inputTags.filter(t=>(attr(t,'type')||'').toLowerCase()==='password');
  const paymentInputs=inputTags.filter(t=>/card|cc-number|credit|cvv|cvc|expiry|exp-date/i.test(`${attr(t,'name')} ${attr(t,'id')} ${attr(t,'autocomplete')}`));
  const formTags=String(html||'').match(/<form\b[^>]*>[\s\S]*?<\/form>/gi)||[];
  for(const block of formTags.slice(0,20)){
    const open=block.match(/^<form\b[^>]*>/i)?.[0]||'';const action=attr(open,'action');const method=(attr(open,'method')||'get').toLowerCase();const target=safeTarget(action,url);const hasPassword=/type\s*=\s*(["'])password\1/i.test(block);const hasPayment=/card|cc-number|credit.?card|cvv|cvc|expiry|exp-date/i.test(block);const cross=Boolean(target&&target.hostname&&!sameSite(host,target.hostname));
    forms.push({action:target?target.toString():null,actionHost:target?normalizeHost(target.hostname):null,method,hasPassword,hasPayment,crossDomainAction:cross});
    if(hasPassword&&cross)findings.push({code:'cross-domain-password-form',severity:'high',title:'Password form submits to another domain',detail:`A password form on ${host} appears to submit to ${normalizeHost(target.hostname)}.`});
    else if(hasPassword)findings.push({code:'password-form',severity:'context',title:'Password form detected',detail:'The page contains a password field. This is expected on legitimate login pages but makes identity verification more important.'});
    if(hasPayment&&cross)findings.push({code:'cross-domain-payment-form',severity:'high',title:'Payment form submits to another domain',detail:`A payment-related form appears to submit to ${normalizeHost(target.hostname)}.`});
    else if(hasPayment)findings.push({code:'payment-form',severity:'context',title:'Payment fields detected',detail:'The page contains payment-related form fields.'});
  }
  const iframeHosts=[];for(const tag of tags(html,'iframe')){const src=attr(tag,'src');const t=safeTarget(src,url);if(t&&t.hostname&&!sameSite(host,t.hostname))iframeHosts.push(normalizeHost(t.hostname))}
  if(iframeHosts.length>=3)findings.push({code:'many-external-iframes',severity:'low',title:'Several external iframes detected',detail:`The page embeds content from ${unique(iframeHosts,x=>x,4).join(', ')}.`});
  const metaRefresh=(tags(html,'meta').find(t=>(attr(t,'http-equiv')||'').toLowerCase()==='refresh'))||null;
  if(metaRefresh)findings.push({code:'meta-refresh',severity:'low',title:'Automatic page refresh/redirect marker',detail:'The page contains an HTML meta-refresh directive.'});
  const autoDownloads=tags(html,'a').filter(t=>/\bdownload(?:\s|=|>)/i.test(t)).length;
  if(autoDownloads)findings.push({code:'download-links',severity:'context',title:'Download links detected',detail:`The page contains ${autoDownloads} link${autoDownloads===1?'':'s'} marked for download.`});
  const title=titleText(html),description=metaDescription(html),brandClaims=detectBrandClaims(`${title} ${description}`);
  const brandRelations=brandClaims.map(brand=>brandDomainStatus(brand,host));
  const conflicts=brandRelations.filter(x=>x.status==='conflict');
  if(conflicts.length)findings.push({code:'page-brand-domain-conflict',severity:'high',title:'Page identity does not match the domain',detail:`The page metadata references ${conflicts.map(x=>x.brand).join(', ')}, but ${host} is not a recognized official domain for that identity.`});
  const iconHosts=[];for(const tag of String(html||'').match(/<link\b[^>]*>/gi)||[]){if(!/\brel\s*=\s*(["'])[^"']*icon/i.test(tag))continue;const href=attr(tag,'href'),u=safeTarget(href,url);if(u&&u.hostname&&!sameSite(host,u.hostname))iconHosts.push(normalizeHost(u.hostname))}
  return {title,description,hasPasswordField:passwordInputs.length>0,hasPaymentField:paymentInputs.length>0,forms:forms.slice(0,10),externalIframeHosts:unique(iframeHosts,x=>x,8),externalIconHosts:unique(iconHosts,x=>x,6),brandClaims,brandRelations,findings:unique(findings,x=>`${x.code}:${x.detail}`,12)};
}

function riskFromFindings(findings){let score=0;for(const x of findings||[])score+=x.severity==='high'?35:x.severity==='medium'?18:x.severity==='low'?7:1;return{score:Math.min(100,score),status:score>=60?'high':score>=25?'caution':'low'}}

async function analyzeWebpage(urlValue){
  let current;try{current=new URL(String(urlValue||'').trim())}catch(_){return{checked:false,status:'invalid',findings:[]}}
  if(!['http:','https:'].includes(current.protocol)||current.username||current.password)return{checked:false,status:'invalid',findings:[]};
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5200);const redirects=[];
  try{
    let response=null,html='';
    for(let i=0;i<=MAX_REDIRECTS;i++){
      await ensurePublic(current.hostname);
      response=await fetch(current,{redirect:'manual',signal:controller.signal,headers:{'user-agent':'CanIShareThis/4.0 (+https://canisharethis.com)','accept':'text/html,application/xhtml+xml','accept-language':'en-US,en;q=0.8'}});
      const loc=response.headers.get('location');if(loc&&response.status>=300&&response.status<400){const next=new URL(loc,current);redirects.push(next.toString());current=next;continue}
      const type=String(response.headers.get('content-type')||'').toLowerCase();if(!response.ok||!type.includes('text/html'))return{checked:true,status:'not-html',httpStatus:response.status,finalUrl:current.toString(),findings:[],redirects};
      html=await readHtml(response);break;
    }
    const page=inspectHtml(html,current.toString()),risk=riskFromFindings(page.findings);
    return{checked:true,status:risk.status,riskScore:risk.score,httpStatus:response&&response.status,finalUrl:current.toString(),redirects,page,findings:page.findings,sourceTypes:['Live webpage HTML']};
  }catch(err){return{checked:false,status:err&&err.name==='AbortError'?'timeout':'unavailable',findings:[]}}
  finally{clearTimeout(timer)}
}

module.exports={analyzeWebpage,inspectHtml};
