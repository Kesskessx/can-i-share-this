'use strict';

const checkHandler=require('./check');
const emailHandler=require('./email-check');
const cryptoHandler=require('./crypto-check');
const imageHandler=require('./image-check');
const messageHandler=require('./message-check');
const socialProfileHandler=require('../lib/social-profile-safety');
const { analyzeUploadedFile, parseFilePayload }=require('../lib/file-safety');
const { enrichScanResult: enrichScanResultV2 }=require('../lib/mega-evidence');
const { upgradeMegaResult }=require('../lib/mega-evidence-v3');
const { orchestrateImageResult }=require('../lib/image-evidence-orchestrator');
const { orchestrateUniversalEvidence }=require('../lib/universal-evidence-orchestrator');
const { applyConfidenceCoverage }=require('../lib/confidence-coverage');

const SOCIAL_HOSTS=new Set([
  'instagram.com','www.instagram.com','facebook.com','www.facebook.com','m.facebook.com',
  'tiktok.com','www.tiktok.com','x.com','www.x.com','twitter.com','www.twitter.com',
  't.me','telegram.me','www.telegram.me','discord.com','www.discord.com','discordapp.com','www.discordapp.com'
]);
const SOCIAL_AVATAR_CACHE=new Map();
const SOCIAL_AVATAR_TTL_MS=10*60*1000;

function leadingUrl(value){const m=String(value||'').trim().match(/^https?:\/\/[^\s<>"']+/i);return m?m[0]:null}
function isSocialProfileUrl(value){
  let url;try{url=new URL(value)}catch(_){return false}
  if(!SOCIAL_HOSTS.has(url.hostname.toLowerCase()))return false;
  const parts=url.pathname.split('/').filter(Boolean),host=url.hostname.toLowerCase();
  if(host.includes('tiktok.com'))return parts.some(v=>v.startsWith('@'));
  if(host.includes('discord'))return parts[0]==='users'&&Boolean(parts[1]);
  if(host.includes('facebook.com')){if(url.pathname.toLowerCase()==='/profile.php')return Boolean(url.searchParams.get('id'));return Boolean(parts[0])&&!['watch','groups','marketplace','gaming','events','reel','reels','share','help','privacy'].includes(parts[0].toLowerCase())}
  if(host==='t.me'||host.includes('telegram.me'))return Boolean(parts[0])&&!parts[0].startsWith('+')&&!['joinchat','share','proxy','socks'].includes(parts[0].toLowerCase());
  if(host==='x.com'||host==='www.x.com'||host.includes('twitter.com'))return Boolean(parts[0])&&!['home','explore','search','messages','settings','i','intent','share','compose','notifications'].includes(parts[0].toLowerCase());
  if(host.includes('instagram.com'))return Boolean(parts[0])&&!['p','reel','reels','stories','explore','accounts','direct','about','developer'].includes(parts[0].toLowerCase());
  return false;
}
function detectType(input){
  const value=String(input||'').trim();if(!value)return'unknown';
  if(/^@[A-Za-z0-9._-]{2,64}$/.test(value))return'social-profile';
  const first=leadingUrl(value);if(first===value&&isSocialProfileUrl(first))return'social-profile';
  if(first===value)return'url';
  if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))return'email';
  if(/^0x[a-fA-F0-9]{40}$/.test(value)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(value)||/^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(value)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(value)||/^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(value)||/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value))return'crypto';
  if(/https?:\/\/[^\s<>"']+/i.test(value))return'message-url';
  if(/[^\s@]+@[^\s@]+\.[^\s@]+/.test(value))return'message-email';
  return'message';
}

function captureHandler(handler,body){return new Promise(resolve=>{let done=false;const finish=(status,payload)=>{if(done)return;done=true;resolve({status,body:payload})};const fake={statusCode:200,headers:{},setHeader(k,v){this.headers[String(k).toLowerCase()]=v;return this},getHeader(k){return this.headers[String(k).toLowerCase()]},status(code){this.statusCode=code;return this},json(payload){finish(this.statusCode,payload);return this},end(payload){let b=payload;if(typeof payload==='string'){try{b=JSON.parse(payload)}catch(_){}}finish(this.statusCode,b);return this}};Promise.resolve(handler({method:'POST',body},fake)).then(()=>{if(!done)finish(fake.statusCode,null)}).catch(err=>finish(500,{error:err&&err.message?err.message:'Analysis failed'}))})}

function decodeHtml(value){return String(value||'').replace(/&amp;/gi,'&').replace(/&quot;/gi,'"').replace(/&#39;|&apos;/gi,"'").replace(/&lt;/gi,'<').replace(/&gt;/gi,'>').replace(/&#(\d+);/g,(_,n)=>{try{return String.fromCodePoint(Number(n))}catch{return''}}).replace(/&#x([0-9a-f]+);/gi,(_,n)=>{try{return String.fromCodePoint(parseInt(n,16))}catch{return''}})}
function htmlAttr(tag,name){const m=String(tag||'').match(new RegExp('\\b'+name+'\\s*=\\s*(["\\\'])([\\s\\S]*?)\\1','i'));return m?decodeHtml(m[2]).trim():''}
function avatarFromHtml(html,baseUrl){const tags=String(html||'').slice(0,350000).match(/<meta\b[^>]*>/gi)||[],wanted=new Set(['og:image','og:image:secure_url','twitter:image','twitter:image:src']);for(const tag of tags){const key=(htmlAttr(tag,'property')||htmlAttr(tag,'name')).toLowerCase();if(!wanted.has(key))continue;const content=htmlAttr(tag,'content');if(!content)continue;try{const image=new URL(content,baseUrl);if(image.protocol==='https:')return image.toString()}catch(_){}}return null}
function cacheAvatar(key,value){if(SOCIAL_AVATAR_CACHE.size>=100){const first=SOCIAL_AVATAR_CACHE.keys().next().value;if(first)SOCIAL_AVATAR_CACHE.delete(first)}SOCIAL_AVATAR_CACHE.set(key,{value,expiresAt:Date.now()+SOCIAL_AVATAR_TTL_MS});return value}
async function fetchSocialAvatar(profileUrl){
  if(!profileUrl||!isSocialProfileUrl(profileUrl))return null;const cached=SOCIAL_AVATAR_CACHE.get(profileUrl);if(cached&&cached.expiresAt>Date.now())return cached.value;if(cached)SOCIAL_AVATAR_CACHE.delete(profileUrl);
  let current;try{current=new URL(profileUrl)}catch(_){return null}if(current.protocol!=='https:')current.protocol='https:';const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),1200);
  try{let response=null;for(let hop=0;hop<3;hop++){response=await fetch(current.toString(),{redirect:'manual',signal:controller.signal,headers:{'user-agent':'Mozilla/5.0 (compatible; CanIShareThis/4.0; +https://canisharethis.com)','accept':'text/html,application/xhtml+xml','accept-language':'en-US,en;q=0.8'}});if(response.status>=300&&response.status<400){const location=response.headers.get('location');if(!location)break;const next=new URL(location,current);if(!SOCIAL_HOSTS.has(next.hostname.toLowerCase()))return cacheAvatar(profileUrl,null);current=next;continue}break}if(!response||!response.ok)return cacheAvatar(profileUrl,null);const type=String(response.headers.get('content-type')||'').toLowerCase();if(type&&!type.includes('text/html')&&!type.includes('application/xhtml+xml'))return cacheAvatar(profileUrl,null);return cacheAvatar(profileUrl,avatarFromHtml(await response.text(),current))}catch(_){return cacheAvatar(profileUrl,null)}finally{clearTimeout(timer)}
}

async function baseTextScan(detectedType,original){
  if(detectedType==='url')return captureHandler(checkHandler,{url:original});
  if(detectedType==='email')return captureHandler(emailHandler,{input:original});
  if(detectedType==='crypto')return captureHandler(cryptoHandler,{input:original});
  if(detectedType==='social-profile'){
    const profileUrl=leadingUrl(original);const [scan,avatar]=await Promise.all([captureHandler(socialProfileHandler,{input:original}),profileUrl?fetchSocialAvatar(profileUrl):Promise.resolve(null)]);
    if(scan.body&&scan.body.socialProfile)scan.body={...scan.body,socialProfile:{...scan.body.socialProfile,avatarUrl:avatar||null,avatarState:avatar?'available':'unavailable'}};
    return scan;
  }
  return captureHandler(messageHandler,{input:original,message:original});
}

async function finalizeResult({detectedType,originalInput,baseResult,externalConsent}){
  const universal=await orchestrateUniversalEvidence({detectedType,originalInput,baseResult,externalConsent});
  const v2=enrichScanResultV2({detectedType,originalInput,body:{detectedType,...universal}});
  const upgraded=upgradeMegaResult(v2);
  return applyConfidenceCoverage(upgraded);
}

async function analyzeImage(res,image,externalConsent){
  const captured=await captureHandler(imageHandler,{image});
  if(captured.status>=400||!captured.body||typeof captured.body!=='object')return res.status(captured.status||500).json(captured.body||{error:'Image analysis failed'});
  try{const imageOrchestrated=await orchestrateImageResult(captured.body);const final=await finalizeResult({detectedType:'image',originalInput:'',baseResult:imageOrchestrated,externalConsent});return res.status(200).json(final)}catch(err){console.error('Universal image orchestration failed',err);return res.status(200).json(applyConfidenceCoverage(upgradeMegaResult(enrichScanResultV2({detectedType:'image',originalInput:'',body:{detectedType:'image',...captured.body}}))))}
}
async function analyzeFile(res,file,externalConsent){
  try{parseFilePayload(file)}catch(err){return res.status(/too large/i.test(err.message)?413:400).json({detectedType:'file',error:err.message})}
  try{const base=analyzeUploadedFile(file);const final=await finalizeResult({detectedType:'file',originalInput:base.file&&base.file.name||'',baseResult:base,externalConsent});return res.status(200).json(final)}catch(err){return res.status(500).json({detectedType:'file',error:'File analysis failed. Please try again.'})}
}

module.exports=async function handler(req,res){
  res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method!=='POST')return res.status(405).json({error:'Method not allowed'});
  let body=req.body||{};if(typeof body==='string'){try{body=JSON.parse(body)}catch{body={}}}
  if(!body||typeof body!=='object'||Array.isArray(body))return res.status(400).json({error:'Invalid request body'});
  const externalConsent=body.externalConsent===true;
  if(typeof body.image==='string'&&body.image.startsWith('data:image/'))return analyzeImage(res,body.image,externalConsent);
  if(body.file&&typeof body.file==='object')return analyzeFile(res,body.file,externalConsent);
  const original=String(body.input||body.url||body.email||body.address||body.message||'').trim();
  if(!original)return res.status(400).json({error:'Input required',detectedType:'unknown'});
  const detectedType=detectType(original);
  const captured=await baseTextScan(detectedType,original);
  if(captured.status>=400&&captured.body&&captured.body.error)return res.status(captured.status).json({detectedType,...captured.body});
  try{const final=await finalizeResult({detectedType,originalInput:original,baseResult:captured.body||{},externalConsent});return res.status(200).json(final)}catch(err){console.error('Universal evidence orchestration failed',err);const fallback=enrichScanResultV2({detectedType,originalInput:original,body:{detectedType,...(captured.body||{})}});return res.status(200).json(applyConfidenceCoverage(upgradeMegaResult(fallback)))}
};
