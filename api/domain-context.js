const net = require('node:net');

const TIMEOUT_MS = 3500;

function baseDomain(host) {
  const clean = String(host || '').toLowerCase().replace(/^www\./, '');
  const parts = clean.split('.').filter(Boolean);
  if (parts.length <= 2) return clean;
  const countrySecondLevels = new Set(['co.uk','org.uk','com.au','com.br','co.jp','co.nz']);
  const lastTwo = parts.slice(-2).join('.');
  if (countrySecondLevels.has(lastTwo) && parts.length >= 3) return parts.slice(-3).join('.');
  return lastTwo;
}
function eventDate(data, action) {
  const e = Array.isArray(data?.events) ? data.events.find(x => String(x?.eventAction || '').toLowerCase() === action) : null;
  return e?.eventDate || null;
}
function registrarName(data) {
  const entities = Array.isArray(data?.entities) ? data.entities : [];
  const registrar = entities.find(e => Array.isArray(e?.roles) && e.roles.includes('registrar'));
  const card = registrar?.vcardArray?.[1];
  if (!Array.isArray(card)) return null;
  const fn = card.find(row => Array.isArray(row) && row[0] === 'fn');
  return fn?.[3] || null;
}
module.exports = async function handler(req,res){
  res.setHeader('Cache-Control','public, s-maxage=21600, stale-while-revalidate=86400');
  if(req.method!=='POST') return res.status(405).json({error:'Method not allowed'});
  let controller;
  try{
    const body=typeof req.body==='string'?JSON.parse(req.body):(req.body||{});
    const raw=String(body.domain||body.url||'').trim();
    let host=raw;
    try{ host=new URL(/^https?:\/\//i.test(raw)?raw:'https://'+raw).hostname; }catch{}
    host=String(host).toLowerCase().replace(/\.$/,'');
    if(!host || net.isIP(host) || host==='localhost' || !host.includes('.')) return res.status(400).json({error:'A public domain is required.'});
    const domain=baseDomain(host);
    controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),TIMEOUT_MS);
    let response;
    try{response=await fetch('https://rdap.org/domain/'+encodeURIComponent(domain),{headers:{accept:'application/rdap+json, application/json','user-agent':'CanIShareThis/1.0'},signal:controller.signal});}finally{clearTimeout(timer)}
    if(!response.ok) return res.status(200).json({available:false,domain,reason:'RDAP data unavailable'});
    const data=await response.json();
    const created=eventDate(data,'registration');
    const updated=eventDate(data,'last changed');
    const expires=eventDate(data,'expiration');
    const createdMs=created?Date.parse(created):NaN;
    const ageDays=Number.isFinite(createdMs)?Math.max(0,Math.floor((Date.now()-createdMs)/86400000)):null;
    const ageLabel=ageDays==null?'Unknown':ageDays<30?'Very new':ageDays<180?'New':ageDays<365?'Less than 1 year old':'Established';
    return res.status(200).json({available:true,domain,created,updated,expires,ageDays,ageLabel,registrar:registrarName(data),statuses:Array.isArray(data.status)?data.status.slice(0,6):[]});
  }catch(err){
    const reason=err?.name==='AbortError'?'RDAP lookup timed out':'RDAP lookup failed';
    return res.status(200).json({available:false,reason});
  }
};