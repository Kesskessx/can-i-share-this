'use strict';

const checkHandler=require('./check');
const emailHandler=require('./email-check');
const cryptoHandler=require('./crypto-check');
const imageHandler=require('./image-check');
const messageHandler=require('./message-check');
const socialProfileHandler=require('../lib/social-profile-safety');
const { enrichScanResult:enrichScanResultV2 }=require('../lib/mega-evidence');
const { enrichScanResult:enrichScanResultV3, upgradeMegaResult }=require('../lib/mega-evidence-v3');
const { orchestrateImageResult }=require('../lib/image-evidence-orchestrator');
const { orchestrateUniversal }=require('../lib/universal-evidence-orchestrator');
const { analyzeFile }=require('../lib/file-safety');

const SOCIAL_HOSTS=new Set(['instagram.com','www.instagram.com','facebook.com','www.facebook.com','m.facebook.com','tiktok.com','www.tiktok.com','x.com','www.x.com','twitter.com','www.twitter.com','t.me','telegram.me','www.telegram.me','discord.com','www.discord.com','discordapp.com','www.discordapp.com','youtube.com','www.youtube.com','linkedin.com','www.linkedin.com']);

function leadingUrl(value){const m=String(value||'').trim().match(/^https?:\/\/[^\s<>"']+/i);return m?m[0]:null}
function isSocialProfileUrl(value){let u;try{u=new URL(value)}catch(_){return false}const host=u.hostname.toLowerCase();if(!SOCIAL_HOSTS.has(host))return false;const p=u.pathname.split('/').filter(Boolean);if(host.includes('tiktok.com'))return p.some(x=>x.startsWith('@'));if(host.includes('discord'))return p[0]==='users'&&Boolean(p[1]);if(host.includes('facebook.com'))return u.pathname.toLowerCase()==='/profile.php'?Boolean(u.searchParams.get('id')):Boolean(p[0])&&!['watch','groups','marketplace','gaming','events','reel','reels','share','help','privacy'].includes(p[0].toLowerCase());if(host==='t.me'||host.includes('telegram.me'))return Boolean(p[0])&&!p[0].startsWith('+')&&!['joinchat','share','proxy','socks'].includes(p[0].toLowerCase());if(host.includes('x.com')||host.includes('twitter.com'))return Boolean(p[0])&&!['home','explore','search','messages','settings','i','intent','share','compose','notifications'].includes(p[0].toLowerCase());if(host.includes('instagram.com'))return Boolean(p[0])&&!['p','reel','reels','stories','explore','accounts','direct','about','developer'].includes(p[0].toLowerCase());if(host.includes('youtube.com'))return Boolean(p[0]);if(host.includes('linkedin.com'))return p[0]==='in'||p[0]==='company';return false}
function detectType(input){const v=String(input||'').trim();if(!v)return'unknown';if(/^@[A-Za-z0-9._-]{2,64}$/.test(v))return'social-profile';const first=leadingUrl(v);if(first&&isSocialProfileUrl(first))return'social-profile';if(/^https?:\/\//i.test(v))return'url';if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))return'email';if(/^0x[a-fA-F0-9]{40}$/.test(v)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v)||/^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v)||/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(v))return'crypto';if(/https?:\/\/[^\s<>"']+/i.test(v))return'message-url';if(/[^\s@]+@[^\s@]+\.[^\s@]+/.test(v))return'message-email';return'message'}

function capture(handler,body){return new Promise(resolve=>{let done=false;const finish=(status,payload)=>{if(done)return;done=true;resolve({status,body:payload})};const res={statusCode:200,headers:{},setHeader(k,v){this.headers[String(k).toLowerCase()]=v;return this},getHeader(k){return this.headers[String(k).toLowerCase()]},status(c){this.statusCode=c;return this},json(p){finish(this.statusCode,p);return this},end(p){let x=p;if(typeof p==='string'){try{x=JSON.parse(p)}catch(_){}}finish(this.statusCode,x);return this}};Promise.resolve(handler({method:'POST',body},res)).then(()=>{if(!done)finish(res.statusCode,null)}).catch(e=>finish(500,{error:e&&e.message||'Check failed'}))})}

async function specialized(detectedType,original){
  if(detectedType==='url')return capture(checkHandler,{url:original});
  if(detectedType==='email')return capture(emailHandler,{input:original});
  if(detectedType==='crypto')return capture(cryptoHandler,{input:original});
  if(detectedType==='social-profile')return capture(socialProfileHandler,{input:original});
  return capture(messageHandler,{input:original,message:original});
}

function legacyEnrich(detectedType,original,body){
  if(!body||typeof body!=='object'||Array.isArray(body)||body.error)return body;
  try{return enrichScanResultV3({detectedType,originalInput:original,body:{detectedType,...body}})}catch(e){console.error('Mega Scanner legacy enrichment failed',e);return{detectedType,...body}}
}

async function analyzeImage(image,externalConsent){
  const captured=await capture(imageHandler,{image});
  if(captured.status>=400||!captured.body||typeof captured.body!=='object')return{status:captured.status||500,body:captured.body||{error:'Image analysis failed'}};
  try{
    const imageOrchestrated=await orchestrateImageResult(captured.body);
    const v2=enrichScanResultV2({detectedType:'image',originalInput:'',body:{detectedType:'image',...imageOrchestrated}});
    const upgraded=upgradeMegaResult(v2);
    const universal=await orchestrateUniversal({detectedType:'image',originalInput:'',baseResult:upgraded,externalConsent});
    return{status:captured.status||200,body:universal};
  }catch(e){
    console.error('Universal image orchestration failed',e);
    const fallback=legacyEnrich('image','',captured.body);
    return{status:captured.status||200,body:fallback};
  }
}

module.exports=async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST')return res.status(405).json({error:'Method not allowed'});
  let body=req.body||{};if(typeof body==='string'){try{body=JSON.parse(body)}catch(_){body={}}}
  const externalConsent=body.externalConsent===true||body.deepConsent===true;

  if(typeof body.image==='string'&&body.image.startsWith('data:image/')){
    const out=await analyzeImage(body.image,externalConsent);return res.status(out.status).json(out.body);
  }

  if(body.file&&typeof body.file==='object'&&typeof body.file.data==='string'){
    try{
      const fileAnalysis=await analyzeFile(body.file);
      const universal=await orchestrateUniversal({detectedType:'file',originalInput:'',baseResult:fileAnalysis,fileAnalysis,externalConsent});
      return res.status(200).json(universal);
    }catch(e){return res.status(400).json({error:e&&e.message||'File analysis failed',detectedType:'file'})}
  }

  const original=String(body.input||body.url||body.email||body.address||body.message||'').trim();
  if(!original)return res.status(400).json({error:'Input required',detectedType:'unknown'});
  const detectedType=detectType(original);
  const primary=await specialized(detectedType,original);
  if(primary.status>=400||!primary.body||typeof primary.body!=='object')return res.status(primary.status||500).json(primary.body||{error:'Primary analysis failed'});
  const enriched=legacyEnrich(detectedType,original,primary.body);
  try{
    const universal=await orchestrateUniversal({detectedType,originalInput:original,baseResult:enriched,externalConsent});
    return res.status(primary.status||200).json(universal);
  }catch(e){console.error('Universal evidence orchestration failed',e);return res.status(primary.status||200).json(enriched)}
};
