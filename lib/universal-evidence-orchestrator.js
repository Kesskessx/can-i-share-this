'use strict';

const checkHandler=require('../api/check');
const emailHandler=require('../api/email-check');
const cryptoHandler=require('../api/crypto-check');
const messageHandler=require('../api/message-check');
const deepCheckHandler=require('../api/deep-check');
const socialProfileHandler=require('./social-profile-safety');
const { inspectDomain, normalizeDomain }=require('./domain-intelligence');
const { verifyWebsiteSocialRelationship, extractDomainsFromText, canonicalSocial }=require('./evidence-relations');
const { inspectWebpage }=require('./webpage-inspector');
const { analyzePhone }=require('./phone-context');
const { enrichCrypto }=require('./crypto-enrichment');
const { buildConfidence }=require('./confidence-engine');

const MAX_SPECIALIZED=8, MAX_DOMAINS=4, MAX_PAGES=2, MAX_REPUTATION=3;
const RANK={unknown:0,low:1,caution:2,high:3};
const BRAND_DOMAINS={
  google:['google.com','gmail.com','googleusercontent.com'],microsoft:['microsoft.com','live.com','office.com','microsoftonline.com'],apple:['apple.com','icloud.com'],paypal:['paypal.com'],amazon:['amazon.com','amazon.fr','amazon.co.uk','amazon.de'],netflix:['netflix.com'],meta:['meta.com','facebook.com','instagram.com'],facebook:['facebook.com'],instagram:['instagram.com'],tiktok:['tiktok.com'],x:['x.com','twitter.com'],twitter:['x.com','twitter.com'],telegram:['telegram.org','t.me'],discord:['discord.com','discord.gg'],binance:['binance.com'],coinbase:['coinbase.com'],revolut:['revolut.com'],wise:['wise.com'],stripe:['stripe.com'],dhl:['dhl.com'],fedex:['fedex.com'],ups:['ups.com'],chronopost:['chronopost.fr'],laposte:['laposte.fr']
};
function clean(v,m=1200){return String(v==null?'':v).replace(/\0/g,'').trim().slice(0,m)}
function risk(v){const x=clean(v,30).toLowerCase();return Object.prototype.hasOwnProperty.call(RANK,x)?x:'unknown'}
function uniq(items,key,max=30){const out=[],seen=new Set();for(const x of items||[]){const k=key(x);if(!k||seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=max)break}return out}
function extractUrls(text){return uniq((String(text||'').match(/https?:\/\/[^\s<>"']+/gi)||[]).map(x=>x.replace(/[),.;!?]+$/,'')),x=>x.toLowerCase(),12)}
function extractEmails(text){return uniq((String(text||'').match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,24}/gi)||[]).map(x=>x.replace(/[),.;!?]+$/,'')),x=>x.toLowerCase(),10)}
function extractPhones(text){return uniq((String(text||'').match(/(?:\+?\d[\d .()\-]{7,}\d)/g)||[]).map(x=>x.trim()),x=>x.replace(/\D/g,''),8)}
function looksCrypto(v){v=clean(v,180);return /^0x[a-fA-F0-9]{40}$/.test(v)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^ltc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v)||/^[13LMDA9][1-9A-HJ-NP-Za-km-z]{25,44}$/.test(v)}
function cryptoFromText(text){return uniq(String(text||'').split(/\s+/).map(x=>x.replace(/^[('"\[]+|[)'",.;!?\]]+$/g,'')).filter(looksCrypto),x=>x.toLowerCase(),6)}
function domainsFromUrls(urls){return uniq((urls||[]).map(x=>{try{return normalizeDomain(new URL(x).hostname)}catch(_){return''}}).filter(Boolean),x=>x,10)}
function brandWords(text){const low=String(text||'').toLowerCase();return uniq(Object.keys(BRAND_DOMAINS).filter(b=>new RegExp('(?:^|[^a-z0-9])'+b.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?:[^a-z0-9]|$)','i').test(low)),x=>x,10)}
function hostMatches(host,d){return host===d||host.endsWith('.'+d)}

function capture(handler,body){return new Promise(resolve=>{let done=false;const finish=(status,payload)=>{if(done)return;done=true;resolve({status,body:payload})};const res={statusCode:200,headers:{},setHeader(k,v){this.headers[String(k).toLowerCase()]=v;return this},getHeader(k){return this.headers[String(k).toLowerCase()]},status(c){this.statusCode=c;return this},json(p){finish(this.statusCode,p);return this},end(p){let x=p;if(typeof p==='string'){try{x=JSON.parse(p)}catch(_){}}finish(this.statusCode,x);return this}};Promise.resolve(handler({method:'POST',body},res)).then(()=>{if(!done)finish(res.statusCode,null)}).catch(e=>finish(500,{error:e&&e.message||'Check failed'}))})}
function riskFromBody(b){if(!b||typeof b!=='object')return'unknown';const vals=[b.safety&&b.safety.status,b.analysis&&b.analysis.risk,b.risk,b.profileRisk,b.socialProfile&&(b.socialProfile.risk||b.socialProfile.riskLevel)];return vals.reduce((best,x)=>RANK[risk(x)]>RANK[best]?risk(x):best,'unknown')}
function summaryFromBody(b){return clean(b&&(b.summary||(b.safety&&b.safety.verdict)||(b.analysis&&b.analysis.summary)||(b.socialProfile&&b.socialProfile.summary)),360)}
function socialTarget(profile){if(!profile||typeof profile!=='object')return'';const u=clean(profile.username,120).replace(/^@/,'');const p=clean(profile.platform,60).toLowerCase();if(!u)return'';if(p.includes('instagram'))return`https://instagram.com/${u}`;if(p.includes('tiktok'))return`https://tiktok.com/@${u}`;if(p==='x'||p.includes('twitter'))return`https://x.com/${u}`;if(p.includes('facebook'))return`https://facebook.com/${u}`;if(p.includes('telegram'))return`https://t.me/${u}`;if(p.includes('youtube'))return`https://youtube.com/${u}`;if(p.includes('linkedin'))return`https://linkedin.com/in/${u}`;return`@${u}`}

function collectEvidence({detectedType,originalInput,baseResult,fileAnalysis}){
  const analysis=baseResult&&baseResult.analysis||{};
  const existing=baseResult&&baseResult.detectedElements||{};
  const fileExtract=fileAnalysis&&fileAnalysis.extracted||{};
  const visible=[originalInput,analysis.visible_text,baseResult&&baseResult.message&&baseResult.message.text,fileAnalysis&&fileAnalysis.eml&&fileAnalysis.eml.subject].filter(Boolean).join('\n');
  const urls=uniq([...(existing.urls||[]),...(analysis.urls||[]),...(baseResult&&baseResult.message&&baseResult.message.urls||[]),...(fileExtract.urls||[]),...extractUrls(visible)],x=>String(x).toLowerCase(),14);
  const emails=uniq([...(existing.emails||[]),...(analysis.emails||[]),...(baseResult&&baseResult.message&&baseResult.message.emails||[]),...(fileExtract.emails||[]),...extractEmails(visible)],x=>String(x).toLowerCase(),12);
  const phones=uniq([...(existing.phones||[]),...(analysis.phones||[]),...(baseResult&&baseResult.message&&baseResult.message.phones||[]),...extractPhones(visible)],x=>String(x).replace(/\D/g,''),10);
  const qr=uniq([...(existing.qr||[]),...(analysis.qr_values||[])],x=>String(x),10);
  for(const q of qr)if(/^https?:\/\//i.test(q)&&!urls.some(x=>String(x).toLowerCase()===String(q).toLowerCase()))urls.push(q);
  const crypto=uniq([...(existing.crypto||[]),...cryptoFromText(visible),...qr.filter(looksCrypto)],x=>String(x).toLowerCase(),8);
  const domains=uniq([...(existing.domains||[]),...domainsFromUrls(urls),...extractDomainsFromText(visible),...emails.map(x=>String(x).split('@')[1]).filter(Boolean)],x=>normalizeDomain(x),12).map(normalizeDomain).filter(Boolean);
  const socialProfiles=[];
  for(const s of existing.socialProfiles||[])socialProfiles.push(s);
  const profile=analysis.social_profile||baseResult&&baseResult.socialProfile||null;
  const st=socialTarget(profile);if(st)socialProfiles.push(st);
  for(const u of urls)if(canonicalSocial(u))socialProfiles.push(u);
  const brands=uniq([...(existing.claimedBrands||[]),...(analysis.claimed_brands||[]),...(baseResult&&baseResult.message&&baseResult.message.claimedBrands||[]),...brandWords(visible)],x=>String(x).toLowerCase(),10);
  const files=uniq([...(existing.files||[]),...(fileAnalysis&&fileAnalysis.file?[fileAnalysis.file.name]:[])],x=>String(x).toLowerCase(),10);
  return{urls,domains,emails,phones,crypto,qr,socialProfiles:uniq(socialProfiles,x=>typeof x==='string'?x.toLowerCase():JSON.stringify(x),10),claimedBrands:brands,files,visibleText:visible};
}

function candidates(elements,detectedType,originalInput){
  const out=[];const add=(type,value,source,priority)=>{value=clean(value,type==='message'?6000:1200);if(value)out.push({type,value,source,priority})};
  for(const s of elements.socialProfiles)add('social-profile',s,'extracted',13);
  for(const u of elements.urls)add('url',u,'extracted',12);
  for(const e of elements.emails)add('email',e,'extracted',11);
  for(const c of elements.crypto)add('crypto',c,'extracted',9);
  if(elements.visibleText&&elements.visibleText.length>=20)add('message',elements.visibleText,'content',7);
  if(['url','email','crypto','social-profile','message'].includes(detectedType)){const map={'url':'url','email':'email','crypto':'crypto','social-profile':'social-profile','message':'message'};add(map[detectedType],originalInput,'primary',20)}
  const dedup=uniq(out.sort((a,b)=>b.priority-a.priority),x=>`${x.type}:${x.value.toLowerCase()}`,30);const quotas={'social-profile':2,url:3,email:2,crypto:2,message:1},used={},picked=[];
  for(const x of dedup){if((used[x.type]||0)>=(quotas[x.type]||0))continue;used[x.type]=(used[x.type]||0)+1;picked.push(x);if(picked.length>=MAX_SPECIALIZED)break}return picked;
}
async function runCandidate(c){if(c.type==='url')return capture(checkHandler,{url:c.value});if(c.type==='email')return capture(emailHandler,{input:c.value});if(c.type==='crypto')return capture(cryptoHandler,{input:c.value});if(c.type==='social-profile')return capture(socialProfileHandler,{input:c.value});if(c.type==='message')return capture(messageHandler,{input:c.value,message:c.value});return{status:200,body:{}}}
function child(c,r){const b=r&&r.body&&typeof r.body==='object'?r.body:{};let value=clean(c.value,260);if(c.type==='email')value=value.replace(/^[^@]+@/,'[mailbox]@');if(c.type==='crypto')value='[crypto address]';return{type:c.type,source:c.source,value,risk:riskFromBody(b),status:r.status,summary:summaryFromBody(b),finalUrl:clean(b.finalUrl,500)||null,checksPerformed:(b.safety&&b.safety.checksPerformed)||[]}}

function brandRelations(elements,domainInfo,pageInspections){
  const out=[];for(const rawBrand of elements.claimedBrands||[]){const brand=String(rawBrand).toLowerCase().replace(/[^a-z0-9]/g,'');const official=BRAND_DOMAINS[brand];if(!official)continue;for(const d of elements.domains||[]){const domain=normalizeDomain(d);if(!domain)continue;if(official.some(x=>hostMatches(domain,x)))out.push({type:'brand-domain',brand,domain,status:'confirmed',source:'Domain',title:'Claimed brand matches the destination domain',detail:`${domain} is within the recognized ${brand} domain set.`});else out.push({type:'brand-domain',brand,domain,status:'conflict',severity:'high',source:'Domain',title:'Claimed brand does not match the destination domain',detail:`The content claims ${brand}, but the observed domain is ${domain}.`})}}
  for(const p of pageInspections||[])for(const c of p&&p.brandConflicts||[])out.push({type:'page-brand-domain',brand:c.brand,domain:c.host,status:'conflict',severity:'high',source:'Live webpage',title:'Live page branding conflicts with its domain',detail:`The live page references ${c.brand} while being served from ${c.host}.`});
  return uniq(out,x=>`${x.type}:${x.brand}:${x.domain}:${x.status}`,12);
}

function graph(elements,checks,relationships,brands,domains,pages){
  const nodes=[],edges=[],map=new Map();const addNode=(type,value,stage,source)=>{value=clean(value,500);if(!value)return null;const k=`${type}:${value.toLowerCase()}`;if(map.has(k))return map.get(k);const id=`e${nodes.length+1}`;nodes.push({id,type,value,stage,source});map.set(k,id);return id};const edgeSet=new Set(),addEdge=(from,to,relation,status)=>{if(!from||!to||from===to)return;const k=`${from}:${to}:${relation}:${status}`;if(edgeSet.has(k))return;edgeSet.add(k);edges.push({from,to,relation,status})};
  for(const u of elements.urls||[])addNode('url',u,'extracted','input');for(const d of elements.domains||[])addNode('domain',d,'extracted','input');for(const e of elements.emails||[])addNode('email',e.replace(/^[^@]+@/,'[mailbox]@'),'extracted','input');for(const p of elements.phones||[])addNode('phone','[phone number]','extracted','input');for(const c of elements.crypto||[])addNode('crypto','[crypto address]','extracted','input');for(const s of elements.socialProfiles||[])addNode('social',typeof s==='string'?s:JSON.stringify(s),'extracted','input');for(const b of elements.claimedBrands||[])addNode('brand',b,'observed','content');for(const f of elements.files||[])addNode('file',f,'observed','file');
  for(const c of checks||[]){const n=addNode(c.type,c.value,'verified','specialized scanner');if(c.finalUrl){const f=addNode('url',c.finalUrl,'verified','redirect resolution');addEdge(n,f,'resolves_to',c.risk)}}
  for(const r of relationships||[]){const d=addNode('domain',r.websiteDomain,'verified','website');const s=addNode('social',`${r.socialPlatform} @${r.socialHandle}`,'verified','website');addEdge(d,s,'links_to_exact_profile',r.status)}
  for(const b of brands||[]){const bn=addNode('brand',b.brand,'observed','content'),dn=addNode('domain',b.domain,'verified','domain');addEdge(bn,dn,'claimed_identity_domain',b.status)}
  return{version:'4.0',nodes:nodes.slice(0,45),edges:edges.slice(0,60)};
}

async function reputationFor(url,consent){if(!consent)return{provider:'External reputation',checked:false,status:'consent-required',detail:'External reputation was not checked because consent was not provided.'};const r=await capture(deepCheckHandler,{url,consent:true});const b=r.body||{};const providers=Array.isArray(b.providers)?b.providers:[];if(b.privacyBlocked)return{provider:'External reputation',checked:false,status:'privacy-blocked',detail:b.disclaimer||'Sensitive URL parameters prevented external sharing.'};const dangerous=providers.find(x=>x&&x.dangerous);if(dangerous)return{provider:dangerous.provider||'External reputation',checked:true,status:'known-dangerous',detail:dangerous.detail||b.verdict};const checked=providers.filter(x=>x&&x.checked);return{provider:checked.length?checked.map(x=>x.provider).join(' + '):'External reputation',checked:checked.length>0,status:checked.length?'no-known-threat':'unavailable',detail:b.verdict||'External reputation could not complete.',providers}}

async function orchestrateUniversal({detectedType,originalInput='',baseResult={},fileAnalysis=null,externalConsent=false}){
  const result={...baseResult,detectedType,originalInput:detectedType==='file'?'':clean(originalInput,7000)};
  const elements=collectEvidence({detectedType,originalInput,result:baseResult,baseResult,fileAnalysis});result.detectedElements=elements;
  const picked=candidates(elements,detectedType,originalInput);const scans=await Promise.allSettled(picked.map(runCandidate));const crossChecks=scans.map((x,i)=>x.status==='fulfilled'?child(picked[i],x.value):{type:picked[i].type,source:picked[i].source,value:clean(picked[i].value,220),risk:'unknown',status:500,summary:'This extracted element could not be checked.'});result.crossChecks=uniq([...(baseResult.crossChecks||[]),...crossChecks],x=>`${x.type}:${String(x.value||'').toLowerCase()}`,14);

  const domainNames=elements.domains.slice(0,MAX_DOMAINS);const domainSettled=await Promise.allSettled(domainNames.map(inspectDomain));result.domainIntelligence=domainSettled.map((x,i)=>x.status==='fulfilled'?x.value:{domain:domainNames[i],state:'unavailable'});
  const relationshipProfile=baseResult.analysis&&baseResult.analysis.social_profile||baseResult.socialProfile||null;result.relationshipChecks=await verifyWebsiteSocialRelationship({websites:elements.urls.length?elements.urls:elements.domains.map(d=>`https://${d}/`),socialProfile:relationshipProfile}).catch(()=>[]);
  const pageSettled=await Promise.allSettled(elements.urls.slice(0,MAX_PAGES).map(inspectWebpage));result.pageInspections=pageSettled.map((x,i)=>x.status==='fulfilled'?x.value:{state:'unavailable',url:elements.urls[i]});
  result.brandRelations=brandRelations(elements,result.domainIntelligence,result.pageInspections);
  result.phoneContext=elements.phones.slice(0,4).map(p=>analyzePhone(p,elements.visibleText));
  const cryptoSettled=await Promise.allSettled(elements.crypto.slice(0,2).map(enrichCrypto));result.cryptoEnrichment=cryptoSettled.map((x,i)=>x.status==='fulfilled'?{address:'[crypto address]',...x.value}:{address:'[crypto address]',network:'unknown',activity:{checked:false,status:'unavailable'}});
  const reputationSettled=await Promise.allSettled(elements.urls.slice(0,MAX_REPUTATION).map(u=>reputationFor(u,externalConsent)));result.reputationChecks=reputationSettled.map((x,i)=>x.status==='fulfilled'?{urlHost:(()=>{try{return new URL(elements.urls[i]).hostname}catch(_){return null}})(),...x.value}:{checked:false,status:'unavailable'});
  if(fileAnalysis)result.fileAnalysis=fileAnalysis;
  result.evidenceGraph=graph(elements,result.crossChecks,result.relationshipChecks,result.brandRelations,result.domainIntelligence,result.pageInspections);
  const confidence=buildConfidence(result);result.assessment=confidence;
  result.megaScanner={...(result.megaScanner||{}),finalRisk:confidence.finalRisk,decision:confidence.decision,identityConsistency:confidence.identity,confidence:confidence.confidence,coverage:confidence.coverage,independentConfirmations:confidence.independentConfirmations,warningSignals:confidence.warnings,noWarningFound:confidence.noWarningFound,couldNotVerify:confidence.couldNotVerify,sources:confidence.sources};
  result.explanation={...(result.explanation||{}),verdict:confidence.finalRisk,headline:confidence.decision==='HIGH RISK'?'High-risk evidence was found.':confidence.decision==='LIKELY OK'?'Independent checks support this result.':confidence.decision==='NOT ENOUGH EVIDENCE'?'Not enough independent evidence was available.':'Verify first — some important relationships remain unconfirmed.',confidence:confidence.confidence,couldNotVerify:confidence.couldNotVerify};
  return result;
}

module.exports={orchestrateUniversal,collectEvidence,brandRelations};
