'use strict';

const checkHandler=require('../api/check');
const emailHandler=require('../api/email-check');
const cryptoHandler=require('../api/crypto-check');
const deepCheckHandler=require('../api/deep-check');
const socialProfileHandler=require('./social-profile-safety');
const { analyzePhone }=require('./phone-safety');
const { analyzeDomain }=require('./domain-intelligence');
const { analyzeWebpage }=require('./webpage-intelligence');
const { enrichCryptoAddress }=require('./crypto-enrichment');
const { verifyWebsiteSocialRelationship, extractDomainsFromText, canonicalSocial }=require('./evidence-relations');
const { detectBrandClaims, normalizeBrand, normalizeHost, brandDomainStatus, hostLooksLikeBrand }=require('./brand-registry');
const { registrableDomain }=require('./email-safety');

const RANK={unknown:0,low:1,caution:2,high:3};
const SOCIAL_HOSTS=new Set(['x.com','twitter.com','instagram.com','facebook.com','tiktok.com','youtube.com','linkedin.com','t.me','telegram.me','discord.com','discord.gg']);
const FREE_EMAIL=new Set(['gmail.com','googlemail.com','outlook.com','hotmail.com','live.com','yahoo.com','icloud.com','proton.me','protonmail.com','aol.com']);
const MAX_SPECIALIZED=10,MAX_DOMAINS=4,MAX_WEBPAGES=3;

function clean(v,max=6000){return String(v==null?'':v).replace(/\0/g,'').trim().slice(0,max)}
function risk(v){const x=clean(v,30).toLowerCase();return Object.prototype.hasOwnProperty.call(RANK,x)?x:'unknown'}
function strongest(values){return(values||[]).reduce((best,x)=>RANK[risk(x)]>RANK[best]?risk(x):best,'unknown')}
function unique(items,keyFn=x=>String(x),max=30){const out=[],seen=new Set();for(const x of items||[]){const k=keyFn(x);if(!k||seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=max)break}return out}
function extractUrls(text){return unique((String(text||'').match(/https?:\/\/[^\s<>"'\]\)]+/gi)||[]).map(x=>x.replace(/[),.;!?]+$/,'')),x=>x.toLowerCase(),20)}
function extractEmails(text){return unique((String(text||'').match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,24}/gi)||[]),x=>x.toLowerCase(),15)}
function extractPhones(text){return unique((String(text||'').match(/(?:\+|00)?\d[\d .()\-]{7,}\d/g)||[]).map(x=>x.trim()),x=>x.replace(/\D/g,''),10)}
function looksCrypto(v){const x=clean(v,180);return /^0x[a-fA-F0-9]{40}$/.test(x)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(x)||/^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(x)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(x)||/^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(x)||/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(x)}
function extractCrypto(text){return unique(String(text||'').split(/\s+/).map(x=>x.replace(/^[('"\[]+|[)'",.;!?\]]+$/g,'')).filter(looksCrypto),x=>x.toLowerCase(),8)}
function emailDomain(v){const m=clean(v,400).match(/@([^@\s>]+)$/);return m?normalizeHost(m[1]):''}
function isSocialUrl(value){try{return SOCIAL_HOSTS.has(normalizeHost(new URL(value).hostname))}catch(_){return false}}
function socialObject(value){const c=canonicalSocial(value);if(!c)return null;return{platform:c.platform==='x'?'X':c.platform.charAt(0).toUpperCase()+c.platform.slice(1),username:c.handle,url:c.url}}
function riskFromBody(body){if(!body||typeof body!=='object')return'unknown';return strongest([body.safety&&body.safety.status,body.analysis&&body.analysis.risk,body.risk,body.profileRisk,body.socialProfile&&(body.socialProfile.risk||body.socialProfile.riskLevel)])}
function summaryFromBody(body){return clean(body&&(body.summary||(body.safety&&body.safety.verdict)||(body.analysis&&body.analysis.summary)||(body.socialProfile&&body.socialProfile.summary)),360)}
function capture(handler,body){return new Promise(resolve=>{let done=false;const finish=(status,payload)=>{if(!done){done=true;resolve({status,body:payload})}};const res={statusCode:200,headers:{},setHeader(k,v){this.headers[String(k).toLowerCase()]=v;return this},status(code){this.statusCode=code;return this},json(payload){finish(this.statusCode,payload);return this},end(payload){let p=payload;if(typeof p==='string'){try{p=JSON.parse(p)}catch(_){}}finish(this.statusCode,p);return this}};const req={method:'POST',body};Promise.resolve(handler(req,res)).then(()=>{if(!done)finish(res.statusCode,null)}).catch(err=>finish(500,{error:err&&err.message||'Check failed'}))})}

function normalizedExistingElements(base){
  const a=base&&base.analysis||{},m=base&&base.message||{},e=base&&base.detectedElements||{};
  return{urls:[...(e.urls||[]),...(a.urls||[]),...(m.urls||[])],domains:[...(e.domains||[])],emails:[...(e.emails||[]),...(a.emails||[]),...(m.emails||[])],phones:[...(e.phones||[]),...(a.phones||[]),...(m.phones||[])],crypto:[...(e.crypto||[])],qr:[...(e.qr||[]),...(a.qr_values||[])],files:[...(e.files||[])],socialProfiles:[...(e.socialProfiles||[])],claimedBrands:[...(e.claimedBrands||[]),...(a.claimed_brands||[]),...(m.claimedBrands||[])]};
}
function extractEvidence({detectedType,originalInput,baseResult}){
  const base=baseResult||{},existing=normalizedExistingElements(base),analysis=base.analysis||{};
  const visible=clean([originalInput,analysis.visible_text,base.summary,base.pageTitle,base.pageDescription].filter(Boolean).join('\n'),20000);
  const urls=unique([...existing.urls,...extractUrls(visible)],x=>String(x).toLowerCase(),20);
  const emails=unique([...existing.emails,...extractEmails(visible)],x=>String(x).toLowerCase(),15);
  const phones=unique([...existing.phones,...extractPhones(visible)],x=>String(x).replace(/\D/g,''),10);
  const crypto=unique([...existing.crypto,...extractCrypto(visible),...(existing.qr||[]).filter(looksCrypto)],x=>String(x).toLowerCase(),8);
  const qr=unique(existing.qr,x=>String(x),10);
  for(const q of qr)if(/^https?:\/\//i.test(q)&&!urls.some(x=>x.toLowerCase()===q.toLowerCase()))urls.push(q);
  const domains=[];const addDomain=v=>{const d=normalizeHost(v);if(d&&d.includes('.')&&!domains.includes(d))domains.push(d)};
  for(const d of existing.domains)addDomain(d);for(const u of urls)addDomain(u);for(const e of emails)addDomain(emailDomain(e));for(const d of extractDomainsFromText(visible))addDomain(d);
  const social=[];const addSocial=v=>{if(!v)return;const obj=typeof v==='object'&&v.username?v:socialObject(String(v));if(!obj||!obj.username)return;const key=`${String(obj.platform).toLowerCase()}:${String(obj.username).toLowerCase()}`;if(!social.some(x=>`${String(x.platform).toLowerCase()}:${String(x.username).toLowerCase()}`===key))social.push(obj)};
  for(const s of existing.socialProfiles)addSocial(s);for(const u of urls)if(isSocialUrl(u))addSocial(u);if(analysis.social_profile)addSocial(analysis.social_profile);if(base.socialProfile)addSocial(base.socialProfile);
  const claimedBrands=unique([...existing.claimedBrands,...detectBrandClaims(visible)].map(normalizeBrand).filter(Boolean),x=>x,10);
  const files=unique([...(existing.files||[]),base.file&&base.file.name].filter(Boolean),x=>String(x).toLowerCase(),20);
  return{visible,urls,domains,emails,phones,crypto,qr,files,socialProfiles:social,claimedBrands};
}

function candidateList(evidence,detectedType,originalInput){
  const out=[];const add=(type,value,source,priority)=>{value=clean(value,type==='phone'?120:1200);if(value)out.push({type,value,source,priority})};
  for(const s of evidence.socialProfiles)if(s.url)add('social-profile',s.url,'extracted',12);
  for(const u of evidence.urls)if(!isSocialUrl(u))add('url',u,'extracted',11);
  for(const e of evidence.emails)add('email',e,'extracted',10);
  for(const c of evidence.crypto)add('crypto',c,'extracted',9);
  for(const p of evidence.phones)add('phone',p,'extracted',8);
  const key=x=>`${x.type}:${x.type==='phone'?x.value.replace(/\D/g,''):x.value.toLowerCase()}`;
  const dedup=unique(out.sort((a,b)=>b.priority-a.priority),key,30),selected=[];const quotas={'social-profile':2,url:4,email:3,crypto:2,phone:3},used={};
  for(const x of dedup){if((used[x.type]||0)>=quotas[x.type])continue;const sameOriginal=(detectedType==='url'&&x.type==='url'&&x.value===originalInput)||(detectedType==='email'&&x.type==='email'&&x.value.toLowerCase()===String(originalInput).toLowerCase())||(detectedType==='crypto'&&x.type==='crypto'&&x.value===originalInput)||(detectedType==='social-profile'&&x.type==='social-profile'&&String(originalInput).includes(x.value));if(sameOriginal)continue;used[x.type]=(used[x.type]||0)+1;selected.push(x);if(selected.length>=MAX_SPECIALIZED)break}
  return selected;
}
async function runCandidate(c,context){if(c.type==='url')return capture(checkHandler,{url:c.value});if(c.type==='email')return capture(emailHandler,{input:c.value});if(c.type==='crypto')return capture(cryptoHandler,{input:c.value});if(c.type==='social-profile')return capture(socialProfileHandler,{input:c.value});if(c.type==='phone')return{status:200,body:analyzePhone(c.value,context)};return{status:200,body:{}}}
function child(c,scan){const b=scan&&scan.body&&typeof scan.body==='object'?scan.body:{};let value=c.value;if(c.type==='email')value=value.replace(/^[^@]+@/,'[mailbox]@');if(c.type==='phone')value='Phone number';if(c.type==='crypto')value='[crypto address]';return{type:c.type,source:c.source,value:clean(value,280),risk:riskFromBody(b),status:scan.status,summary:summaryFromBody(b),finalUrl:clean(b.finalUrl,500)||null,details:c.type==='phone'?b.phone||null:null,profileExternalDomains:Array.isArray(b.socialProfile&&b.socialProfile.profileData&&b.socialProfile.profileData.externalDomains)?b.socialProfile.profileData.externalDomains.slice(0,8):[]}}

function websiteUrls(evidence){return unique(evidence.urls.filter(u=>!isSocialUrl(u)),u=>normalizeHost(u),6)}
function emailWebsiteRelations(evidence){const out=[],sites=websiteUrls(evidence).map(normalizeHost),emails=evidence.emails.map(emailDomain).filter(Boolean);for(const ed of unique(emails,x=>x,6))for(const site of sites.slice(0,3)){const same=registrableDomain(ed)===registrableDomain(site);if(same)out.push({type:'website-email',status:'confirmed',positive:true,websiteDomain:site,emailDomain:ed,detail:`The email domain ${ed} matches the website domain ${site}.`});else if(!FREE_EMAIL.has(ed))out.push({type:'website-email',status:'not-found',positive:false,websiteDomain:site,emailDomain:ed,detail:`The email domain ${ed} does not match the website domain ${site}. This is not automatically malicious, but the relationship is not confirmed.`})}return out.slice(0,8)}
function brandRelations(evidence){
  const out=[];
  for(const brand of evidence.claimedBrands)for(const domain of evidence.domains.slice(0,6)){
    if(SOCIAL_HOSTS.has(domain))continue;
    const r=brandDomainStatus(brand,domain);
    if(r.status==='confirmed')out.push({type:'claimed-brand-domain',status:'confirmed',positive:true,brand:r.brand,websiteDomain:domain,detail:`${domain} is in the recognized official-domain set for ${r.brand}.`});
    else if(r.status==='conflict'&&hostLooksLikeBrand(domain,r.brand))out.push({type:'claimed-brand-domain',status:'conflict',positive:false,severity:'high',brand:r.brand,websiteDomain:domain,detail:`${domain} resembles the claimed ${r.brand} identity but is not a recognized official domain.`});
    else if(r.status==='conflict')out.push({type:'claimed-brand-domain',status:'unverified',positive:false,brand:r.brand,websiteDomain:domain,detail:`${domain} is an external domain whose relationship to the claimed ${r.brand} identity was not established.`});
  }
  return unique(out,x=>`${x.type}:${x.brand}:${x.websiteDomain}`,12);
}
function emlRelations(base){const e=base&&base.emailMessage;if(!e)return[];const out=[];if(e.fromDomain&&e.replyToDomain){const same=registrableDomain(e.fromDomain)===registrableDomain(e.replyToDomain);out.push({type:'email-from-replyto',status:same?'confirmed':'conflict',positive:same,severity:same?undefined:'medium',detail:same?`From and Reply-To use the same organizational domain (${e.fromDomain}).`:`From uses ${e.fromDomain}, while Reply-To uses ${e.replyToDomain}.`})}if(e.authentication&&e.authentication.dmarc==='fail')out.push({type:'email-authentication',status:'conflict',positive:false,severity:'high',detail:'The received message reports DMARC=fail in Authentication-Results.'});return out}
function profileWebsiteRelations(checks,evidence){const out=[];const sites=websiteUrls(evidence).map(normalizeHost);for(const c of checks||[]){if(c.type!=='social-profile')continue;for(const d of c.profileExternalDomains||[]){const host=normalizeHost(d);if(sites.some(s=>registrableDomain(s)===registrableDomain(host)))out.push({type:'profile-bio-website',status:'confirmed',positive:true,websiteDomain:host,detail:`The social-profile metadata references the same website domain ${host}.`})}}return out}

async function relationshipChecks(evidence,checks,base){const sites=websiteUrls(evidence),tasks=[];for(const social of evidence.socialProfiles.slice(0,2))tasks.push(verifyWebsiteSocialRelationship({websites:sites,socialProfile:social}));const socialResults=(await Promise.all(tasks)).flat();return unique([...socialResults,...emailWebsiteRelations(evidence),...brandRelations(evidence),...emlRelations(base),...profileWebsiteRelations(checks,evidence)],x=>`${x.type}:${x.detail}`,24)}

function arrProvidersChecked(v){return Array.isArray(v)?v.filter(x=>x&&x.checked).length:0}
async function externalChecks(evidence,consent){
  const urls=websiteUrls(evidence).slice(0,3),cryptos=evidence.crypto.slice(0,2),eligible=urls.length+cryptos.length;
  if(!consent)return{consent:false,eligible,status:eligible?'consent-required':'not-applicable',urlChecks:[],cryptoChecks:[]};
  const [urlSettled,cryptoSettled]=await Promise.all([Promise.allSettled(urls.map(u=>capture(deepCheckHandler,{url:u,consent:true}))),Promise.allSettled(cryptos.map(a=>enrichCryptoAddress(a,{consent:true})))]);
  const urlChecks=urlSettled.map((x,i)=>{if(x.status!=='fulfilled')return{urlHost:normalizeHost(urls[i]),checked:false,status:'unavailable'};const b=x.value.body||{};return{urlHost:normalizeHost(urls[i]),checked:b.privacyBlocked?false:arrProvidersChecked(b.providers)>0,status:b.status||'unknown',dangerous:b.status==='known-dangerous',providers:Array.isArray(b.providers)?b.providers.map(p=>({provider:p.provider,status:p.status,checked:p.checked,dangerous:p.dangerous,detail:clean(p.detail,300)})):[],privacyBlocked:Boolean(b.privacyBlocked)}});
  const cryptoChecks=cryptoSettled.map((x,i)=>x.status==='fulfilled'?{address:'[crypto address]',...x.value}:{address:'[crypto address]',checked:false,status:'unavailable'});
  return{consent:true,eligible,status:'completed',urlChecks,cryptoChecks};
}

function buildRelationGraph(evidence,relations){
  const nodes=[],edges=[],map=new Map();const add=(type,value,extra={})=>{value=clean(value,400);if(!value)return null;const key=`${type}:${value.toLowerCase()}`;if(map.has(key))return map.get(key);const id=`r${nodes.length+1}`;nodes.push({id,type,value,...extra});map.set(key,id);return id};
  for(const b of evidence.claimedBrands)add('brand',b);for(const d of evidence.domains)add('domain',d);for(const e of evidence.emails)add('email',`[mailbox]@${emailDomain(e)}`);for(const s of evidence.socialProfiles)add('social',`${s.platform} @${s.username}`);for(const p of evidence.phones)add('phone','Phone number');for(const c of evidence.crypto)add('crypto','Crypto address');for(const f of evidence.files)add('file',f);
  for(const rel of relations||[]){let a=null,b=null;if(rel.type==='website-social'){a=add('domain',rel.websiteDomain);b=add('social',`${String(rel.socialPlatform).toUpperCase()} @${rel.socialHandle}`)}else if(rel.type==='website-email'){a=add('domain',rel.websiteDomain);b=add('email',`[mailbox]@${rel.emailDomain}`)}else if(rel.type==='claimed-brand-domain'){a=add('brand',rel.brand);b=add('domain',rel.websiteDomain)}else if(rel.type==='email-from-replyto'){a=add('email-domain','From');b=add('email-domain','Reply-To')}else if(rel.type==='profile-bio-website'){a=add('social','Social profile');b=add('domain',rel.websiteDomain)}if(a&&b)edges.push({from:a,to:b,relation:rel.type,status:rel.status,strength:rel.status==='confirmed'?'strong':rel.status==='conflict'?'conflict':'unknown'})}
  return{version:'4.0',nodes:nodes.slice(0,40),edges:edges.slice(0,60)};
}
function additionalCorrelations(evidence,domains,relations,base){
  const out=[],domainBy=new Map((domains||[]).map(x=>[x.domain,x]));
  for(const rel of relations||[])if(rel.type==='claimed-brand-domain'&&rel.status==='conflict'){const d=domainBy.get(rel.websiteDomain);if(d&&Number.isFinite(d.rdap&&d.rdap.ageDays)&&d.rdap.ageDays<=30)out.push({type:'brand-new-domain',severity:'high',title:'Brand mismatch combined with a recently registered domain',detail:`${rel.websiteDomain} conflicts with the claimed ${rel.brand} identity and was registered about ${d.rdap.ageDays} days ago.`})}
  const text=clean([evidence.visible,base&&base.summary].join(' '),16000).toLowerCase(),hasCrypto=evidence.crypto.length>0,payment=/\b(pay|payment|fee|deposit|transfer|invoice|refund|wallet|crypto|bitcoin)\b/.test(text),urgent=/\b(urgent|immediately|act now|today|suspended|locked|final notice)\b/.test(text);if(hasCrypto&&payment&&urgent)out.push({type:'urgent-crypto-payment',severity:'high',title:'Urgent crypto payment request',detail:'The content combines urgency, payment language and a crypto address. Verify the request independently before sending funds.'});return out.slice(0,8)
}
function aggregateRisk(base,checks,domains,pages,relations,external,correlations){
  const values=[riskFromBody(base),...checks.map(x=>x.risk),...pages.map(x=>x.status)];
  for(const d of domains){if((d.signals||[]).some(s=>s.code==='domain-brand-conflict'))values.push('high');else if((d.signals||[]).some(s=>s.code==='domain-very-new'||s.code==='domain-new'))values.push('caution')}
  for(const r of relations)if(r.status==='conflict')values.push(r.severity==='high'?'high':'caution');for(const x of external.urlChecks||[])if(x.dangerous)values.push('high');for(const c of correlations)values.push(c.severity==='high'?'high':'caution');return strongest(values)
}

async function orchestrateUniversalEvidence({detectedType,originalInput='',baseResult={},externalConsent=false}){
  const evidence=extractEvidence({detectedType,originalInput,baseResult}),candidates=candidateList(evidence,detectedType,originalInput),existing=Array.isArray(baseResult.crossChecks)?baseResult.crossChecks:[];
  const existingKeys=new Set(existing.map(x=>`${clean(x.type,50)}:${clean(x.value,1200).toLowerCase()}`));
  const missing=candidates.filter(x=>!existingKeys.has(`${x.type}:${x.type==='phone'?'phone number':x.type==='crypto'?'[crypto address]':x.type==='email'?x.value.replace(/^[^@]+@/,'[mailbox]@').toLowerCase():x.value.toLowerCase()}`));
  const sites=websiteUrls(evidence),domainTargets=unique(evidence.domains.filter(d=>!SOCIAL_HOSTS.has(d)),x=>x,MAX_DOMAINS);
  const [scanSettled,domainSettled,pageSettled,external]=await Promise.all([Promise.allSettled(missing.map(x=>runCandidate(x,evidence.visible))),Promise.allSettled(domainTargets.map(d=>analyzeDomain(d,{claimedBrands:evidence.claimedBrands}))),Promise.allSettled(sites.slice(0,MAX_WEBPAGES).map(analyzeWebpage)),externalChecks(evidence,externalConsent)]);
  const extra=scanSettled.map((x,i)=>x.status==='fulfilled'?child(missing[i],x.value):{type:missing[i].type,source:missing[i].source,value:missing[i].type==='phone'?'Phone number':'Extracted element',risk:'unknown',status:500,summary:'This extracted element could not be checked.'});
  const checks=unique([...existing,...extra],x=>`${clean(x.type,50)}:${clean(x.value,500).toLowerCase()}`,16);
  const domains=domainSettled.map((x,i)=>x.status==='fulfilled'?x.value:{domain:domainTargets[i],completed:false,status:'unavailable',signals:[]});
  const pages=pageSettled.map((x,i)=>x.status==='fulfilled'?x.value:{checked:false,status:'unavailable',url:sites[i],findings:[]});
  const relations=await relationshipChecks(evidence,checks,baseResult),correlations=additionalCorrelations(evidence,domains,relations,baseResult),finalRisk=aggregateRisk(baseResult,checks,domains,pages,relations,external,correlations);
  const safety={...(baseResult.safety||{})};if(RANK[finalRisk]>RANK[risk(safety.status)]){safety.status=finalRisk;safety.riskScore=Math.max(Number(safety.riskScore||0),finalRisk==='high'?85:finalRisk==='caution'?50:10);safety.verdict=finalRisk==='high'?'High-risk correlated evidence detected':finalRisk==='caution'?'Evidence needs verification':'No major warning found'}
  const detectedElements={urls:evidence.urls,domains:evidence.domains,emails:evidence.emails,phones:evidence.phones,crypto:evidence.crypto,qr:evidence.qr,files:evidence.files,socialProfiles:evidence.socialProfiles.map(s=>s.url||`${s.platform} @${s.username}`),claimedBrands:evidence.claimedBrands};
  return{...baseResult,detectedType,safety,crossChecks:checks,detectedElements,domainIntelligence:domains,webpageChecks:pages,relationshipChecks:relations,relationGraph:buildRelationGraph(evidence,relations),externalReputation:external,correlations:unique([...(baseResult.correlations||[]),...correlations],x=>`${x.type}:${x.detail}`,16),universalOrchestration:{version:'4.0',specializedChecksRun:checks.length,domainChecksRun:domains.length,webpageChecksRun:pages.length,relationshipChecksRun:relations.length,externalConsent:Boolean(externalConsent),externalEligible:external.eligible,scanners:unique(checks.map(x=>x.type),x=>x,12)}};
}

module.exports={orchestrateUniversalEvidence,extractEvidence,candidateList,buildRelationGraph};
