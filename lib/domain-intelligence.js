'use strict';

const dns=require('node:dns').promises;
const tls=require('node:tls');
const net=require('node:net');
const { analyzeEmailAddress, registrableDomain }=require('./email-safety');
const { normalizeHost, brandDomainStatus, hostLooksLikeBrand }=require('./brand-registry');

function clean(v,max=500){return String(v==null?'':v).replace(/\0/g,'').replace(/\s+/g,' ').trim().slice(0,max)}
function timeout(promise,ms){return Promise.race([promise,new Promise((_,reject)=>setTimeout(()=>reject(new Error('timeout')),ms))])}
function isPrivateIPv4(ip){const p=String(ip).split('.').map(Number);return p.length!==4||p.some(n=>!Number.isInteger(n))||p[0]===10||p[0]===127||p[0]===0||(p[0]===169&&p[1]===254)||(p[0]===172&&p[1]>=16&&p[1]<=31)||(p[0]===192&&p[1]===168)||(p[0]===100&&p[1]>=64&&p[1]<=127)||p[0]>=224}
function isPrivateIPv6(ip){const x=String(ip||'').toLowerCase();return x==='::1'||x==='::'||x.startsWith('fc')||x.startsWith('fd')||x.startsWith('fe8')||x.startsWith('fe9')||x.startsWith('fea')||x.startsWith('feb')}
function isPrivateIp(ip){const f=net.isIP(ip);return f===4?isPrivateIPv4(ip):f===6?isPrivateIPv6(ip):true}

async function publicAddresses(host){
  try{const rows=await timeout(dns.lookup(host,{all:true,verbatim:true}),1500);if(!rows.length||rows.some(x=>isPrivateIp(x.address)))return[];return rows.map(x=>x.address).slice(0,6)}catch(_){return[]}
}
async function nameServers(host){try{return(await timeout(dns.resolveNs(registrableDomain(host)),1800)).map(x=>clean(x,253).toLowerCase()).slice(0,8)}catch(_){return[]}}
async function inspectCertificate(host){
  const addresses=await publicAddresses(host);if(!addresses.length)return{checked:false,status:'unavailable'};
  return new Promise(resolve=>{let done=false;const finish=v=>{if(done)return;done=true;resolve(v)};const socket=tls.connect({host,port:443,servername:host,rejectUnauthorized:false,timeout:2200},()=>{try{const cert=socket.getPeerCertificate(true)||{},authorized=socket.authorized===true,validTo=cert.valid_to?new Date(cert.valid_to):null,validFrom=cert.valid_from?new Date(cert.valid_from):null,now=Date.now(),daysRemaining=validTo&&Number.isFinite(validTo.getTime())?Math.floor((validTo.getTime()-now)/86400000):null;finish({checked:true,status:'read',authorized,subjectCN:clean(cert.subject&&cert.subject.CN,180)||null,issuerCN:clean(cert.issuer&&cert.issuer.CN,180)||null,validFrom:validFrom&&Number.isFinite(validFrom.getTime())?validFrom.toISOString():null,validTo:validTo&&Number.isFinite(validTo.getTime())?validTo.toISOString():null,daysRemaining,subjectAltNameCount:clean(cert.subjectaltname,8000).split(',').filter(Boolean).length})}catch(_){finish({checked:false,status:'unavailable'})}try{socket.end()}catch(_){}});socket.on('timeout',()=>{try{socket.destroy()}catch(_){ }finish({checked:false,status:'timeout'})});socket.on('error',()=>finish({checked:false,status:'unavailable'}));setTimeout(()=>{try{socket.destroy()}catch(_){ }finish({checked:false,status:'timeout'})},2600)})
}

async function analyzeDomain(domain,{claimedBrands=[]}={}){
  const host=normalizeHost(domain);if(!host||!host.includes('.'))return{domain:host,status:'invalid',completed:false};
  const [emailProbe,ns,cert,addresses]=await Promise.all([analyzeEmailAddress(`scan@${host}`).catch(()=>null),nameServers(host),inspectCertificate(host),publicAddresses(host)]);
  const e=emailProbe&&emailProbe.email||{},safety=emailProbe&&emailProbe.safety||{status:'unknown',signals:[]};
  const brandRelations=[];for(const brand of claimedBrands||[]){const rel=brandDomainStatus(brand,host);if(rel.brand)brandRelations.push({...rel,looksLikeBrand:hostLooksLikeBrand(host,rel.brand)})}
  const lookalikeConflicts=brandRelations.filter(x=>x.status==='conflict'&&x.looksLikeBrand),unrelated=brandRelations.filter(x=>x.status==='conflict'&&!x.looksLikeBrand),signals=[];
  if(Number.isFinite(e.domainAgeDays)&&e.domainAgeDays<=7)signals.push({code:'domain-very-new',severity:'medium',title:'Domain registered within the last week',detail:`RDAP indicates this domain is about ${e.domainAgeDays} day${e.domainAgeDays===1?'':'s'} old. Domain age is context and is not proof of fraud.`});
  else if(Number.isFinite(e.domainAgeDays)&&e.domainAgeDays<=30)signals.push({code:'domain-new',severity:'low',title:'Recently registered domain',detail:`RDAP indicates this domain is about ${e.domainAgeDays} days old. Recent registration increases uncertainty for an unexpected request but is not proof of fraud.`});
  if(lookalikeConflicts.length)signals.push({code:'domain-brand-conflict',severity:'high',title:'Brand-like domain is not recognized as official',detail:`${host} resembles the claimed ${lookalikeConflicts.map(x=>x.brand).join(', ')} identity but is not in the recognized official-domain set.`});
  else if(unrelated.length)signals.push({code:'domain-brand-unverified',severity:'context',title:'External domain relationship is not confirmed',detail:`${host} is not an official domain for the claimed identity. Unrelated third-party domains can be legitimate, so this is recorded as unverified rather than malicious.`});
  if(cert.checked&&cert.daysRemaining!==null&&cert.daysRemaining<0)signals.push({code:'tls-expired',severity:'medium',title:'TLS certificate appears expired',detail:'The current TLS certificate is past its validity date.'});
  if(cert.checked&&!cert.authorized)signals.push({code:'tls-not-authorized',severity:'medium',title:'TLS certificate was not trusted by the runtime',detail:'The HTTPS certificate could not be validated by the server runtime. This can have benign causes but deserves caution.'});
  return{domain:host,registrableDomain:registrableDomain(host),completed:Boolean(emailProbe),status:lookalikeConflicts.length?'conflict':safety.status||'unknown',dns:{domainExists:Boolean(e.domainExists),hasMx:Boolean(e.hasMx),mxCount:e.mxCount??null,hasSpf:Boolean(e.hasSpf),spfQuality:e.spfQuality||'unknown',hasDmarc:Boolean(e.hasDmarc),dmarcPolicy:e.dmarcPolicy||null,hasDnssec:Boolean(e.hasDnssec),hasMtaSts:Boolean(e.hasMtaSts),hasTlsRpt:Boolean(e.hasTlsRpt),nameServers:ns,addresses},rdap:{known:Boolean(e.rdapKnown),registeredAt:e.registeredAt||null,ageDays:Number.isFinite(e.domainAgeDays)?e.domainAgeDays:null},tls:cert,claimedBrandRelations:brandRelations,signals,sourceTypes:['DNS','RDAP',...(cert.checked?['TLS certificate']:[])],disclaimer:'Domain age, DNS configuration and certificates are context. They do not prove that a site or sender is trustworthy.'};
}

module.exports={analyzeDomain,inspectCertificate,publicAddresses};
