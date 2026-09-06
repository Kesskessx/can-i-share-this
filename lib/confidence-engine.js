'use strict';

function clean(v,max=500){return String(v==null?'':v).replace(/\0/g,'').replace(/\s+/g,' ').trim().slice(0,max)}
const RANK={unknown:0,low:1,caution:2,high:3};
function risk(v){const x=clean(v,30).toLowerCase();return Object.prototype.hasOwnProperty.call(RANK,x)?x:'unknown'}
function uniq(items,key,max=20){const out=[],seen=new Set();for(const x of items||[]){const k=key(x);if(!k||seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=max)break}return out}

function strongestRisk(result){
  const values=[result&&result.analysis&&result.analysis.risk,result&&result.safety&&result.safety.status,result&&result.megaScanner&&result.megaScanner.finalRisk];
  for(const c of result&&result.crossChecks||[])values.push(c&&c.risk);
  for(const d of result&&result.domainIntelligence||[])values.push(d&&d.risk);
  for(const p of result&&result.pageInspections||[])for(const s of p&&p.signals||[])values.push(s&&s.severity==='high'?'high':s&&s.severity==='medium'?'caution':'low');
  for(const r of result&&result.reputationChecks||[])if(r&&r.status==='known-dangerous')values.push('high');
  return values.reduce((b,x)=>RANK[risk(x)]>RANK[b]?risk(x):b,'unknown');
}

function buildCoverage(result){
  const el=result&&result.detectedElements||{};
  const expected=[];
  const add=(id,label,needed=true)=>{if(needed&&!expected.some(x=>x.id===id))expected.push({id,label})};
  add('content','Content / context',Boolean(result&&result.originalInput)||Boolean(result&&result.analysis&&result.analysis.visible_text)||result&&result.detectedType==='file');
  add('url','URL technical check',Boolean((el.urls||[]).length));
  add('domain','DNS / RDAP domain intelligence',Boolean((el.domains||[]).length||(el.urls||[]).length));
  add('email','Email/domain check',Boolean((el.emails||[]).length));
  add('social','Social-profile check',Boolean((el.socialProfiles||[]).length));
  add('phone','Phone context',Boolean((el.phones||[]).length));
  add('crypto','Crypto context/activity',Boolean((el.crypto||[]).length));
  add('qr','QR destination check',Boolean((el.qr||[]).length));
  add('file','Static file inspection',Boolean(result&&result.fileAnalysis||((el.files||[]).length&&result&&result.detectedType==='file'));
  add('relationship','Identity/relationship checks',Boolean((el.socialProfiles||[]).length&&((el.domains||[]).length||(el.urls||[]).length)||(el.claimedBrands||[]).length&&((el.domains||[]).length||(el.urls||[]).length)));
  add('page','Live webpage behavior',Boolean((el.urls||[]).length));
  add('reputation','External reputation',Boolean((el.urls||[]).length));

  const done=new Set();
  if(result&&result.analysis||result&&result.safety)done.add('content');
  if((result&&result.crossChecks||[]).some(x=>x&&x.type==='url'&&Number(x.status||200)<500))done.add('url');
  if((result&&result.domainIntelligence||[]).some(x=>x&&['checked','partial'].includes(x.state)))done.add('domain');
  if((result&&result.crossChecks||[]).some(x=>x&&x.type==='email'&&Number(x.status||200)<500))done.add('email');
  if((result&&result.crossChecks||[]).some(x=>x&&x.type==='social-profile'&&Number(x.status||200)<500))done.add('social');
  if((result&&result.phoneContext||[]).length)done.add('phone');
  if((result&&result.cryptoEnrichment||[]).length)done.add('crypto');
  if((el.qr||[]).length&&((result&&result.crossChecks||[]).some(x=>x&&x.source&&String(x.source).includes('qr'))))done.add('qr');
  if(result&&result.fileAnalysis)done.add('file');
  if((result&&result.relationshipChecks||[]).length||(result&&result.brandRelations||[]).length)done.add('relationship');
  if((result&&result.pageInspections||[]).some(x=>x&&x.state==='checked'))done.add('page');
  if((result&&result.reputationChecks||[]).some(x=>x&&x.checked===true||x&&x.status==='privacy-blocked'))done.add('reputation');

  const rows=expected.map(x=>({...x,status:done.has(x.id)?'completed':'not-completed'}));
  const completed=rows.filter(x=>x.status==='completed').length;
  return{completed,total:rows.length,ratio:rows.length?completed/rows.length:0,rows};
}

function independentConfirmations(result){
  const out=[];
  for(const rel of result&&result.relationshipChecks||[])if(rel&&rel.positive&&rel.status==='confirmed')out.push({source:'Website',title:'Website links to the same social profile',detail:clean(rel.detail,420)});
  for(const rel of result&&result.brandRelations||[])if(rel&&rel.status==='confirmed')out.push({source:rel.source||'Domain',title:clean(rel.title||'Brand/domain relationship confirmed',180),detail:clean(rel.detail,420)});
  for(const d of result&&result.domainIntelligence||[])if(d&&d.state==='checked'&&d.registration&&Number.isFinite(d.registration.ageDays)&&d.registration.ageDays>365)out.push({source:'RDAP',title:'Established domain registration history',detail:`${d.domain} has public registration data indicating it is more than one year old. Domain age is context, not proof of ownership.`});
  return uniq(out,x=>`${x.source}:${x.title}:${x.detail}`,8);
}

function warningSignals(result){
  const out=[];
  const push=(source,title,detail,severity='caution')=>out.push({source,severity,title:clean(title,180),detail:clean(detail,420)});
  for(const c of result&&result.crossChecks||[])if(['high','caution'].includes(risk(c&&c.risk)))push(c.type||'Scanner',c.summary||`${c.type} check raised a warning`,c.value||'',risk(c.risk));
  for(const d of result&&result.domainIntelligence||[])for(const s of d&&d.signals||[])if(['high','medium'].includes(String(s&&s.severity||'')))push('DNS/RDAP',s.title,s.detail,s.severity==='high'?'high':'caution');
  for(const p of result&&result.pageInspections||[])for(const s of p&&p.signals||[])if(['high','medium'].includes(String(s&&s.severity||'')))push('Webpage',s.title,s.detail,s.severity==='high'?'high':'caution');
  for(const ph of result&&result.phoneContext||[])for(const s of ph&&ph.signals||[])if(['high','medium'].includes(String(s&&s.severity||'')))push('Phone context',s.title,s.detail,s.severity==='high'?'high':'caution');
  if(result&&result.fileAnalysis)for(const s of result.fileAnalysis.safety&&result.fileAnalysis.safety.signals||[])if(['high','medium'].includes(String(s&&s.severity||'')))push('File',s.title,s.detail,s.severity==='high'?'high':'caution');
  for(const r of result&&result.reputationChecks||[])if(r&&r.status==='known-dangerous')push(r.provider||'Reputation','Known threat reported',r.detail||'An external source reported this URL as dangerous.','high');
  return uniq(out,x=>`${x.source}:${x.title}:${x.detail}`,10);
}

function noWarnings(result){
  const out=[];
  for(const c of result&&result.crossChecks||[])if(risk(c&&c.risk)==='low')out.push({source:c.type||'Scanner',title:`No major warning from the ${c.type||'specialized'} check`,detail:clean(c.summary,360)});
  for(const r of result&&result.reputationChecks||[])if(r&&r.checked&&['no-known-threat','no-known-phish'].includes(r.status))out.push({source:r.provider||'Reputation',title:'No known threat returned',detail:clean(r.detail,360)});
  return uniq(out,x=>`${x.source}:${x.title}`,8);
}

function identityLevel(result,confirmations,warnings){
  const conflicts=[];
  for(const b of result&&result.brandRelations||[])if(b&&b.status==='conflict')conflicts.push(b);
  for(const p of result&&result.pageInspections||[])for(const c of p&&p.brandConflicts||[])conflicts.push(c);
  if(conflicts.length)return{level:'low',label:'Identity conflict',score:0.2};
  if(confirmations.some(x=>/same social profile|relationship confirmed/i.test(x.title)))return{level:'high',label:'Strong identity consistency',score:0.9};
  const el=result&&result.detectedElements||{};
  if((el.claimedBrands||[]).length&&((el.domains||[]).length||(el.urls||[]).length))return{level:'medium',label:'Identity needs verification',score:0.55};
  return{level:'unknown',label:'Identity not established',score:0.35};
}

function couldNotVerify(result,coverage){
  const out=[];
  for(const row of coverage.rows)if(row.status!=='completed')out.push(`${row.label} did not complete`);
  const el=result&&result.detectedElements||{};
  if((el.phones||[]).length)out.push('Who actually controls the detected phone number');
  if((el.socialProfiles||[]).length)out.push('Who actually controls the social account and its historical ownership');
  if((el.crypto||[]).length)out.push('Who controls the crypto address');
  if(result&&result.fileAnalysis&&result.fileAnalysis.file)out.push('Static inspection does not safely execute the uploaded file');
  return uniq(out,x=>x.toLowerCase(),6);
}

function buildConfidence(result){
  const coverage=buildCoverage(result),confirmed=independentConfirmations(result),warnings=warningSignals(result),noWarning=noWarnings(result);
  const identity=identityLevel(result,confirmed,warnings),finalRisk=strongestRisk(result);
  const independent=confirmed.length;
  const external=(result&&result.reputationChecks||[]).filter(x=>x&&x.checked).length;
  const technical=Math.min(8,(result&&result.crossChecks||[]).filter(x=>Number(x&&x.status||500)<500).length+(result&&result.domainIntelligence||[]).filter(x=>x&&x.state==='checked').length+(result&&result.pageInspections||[]).filter(x=>x&&x.state==='checked').length+(result&&result.fileAnalysis?1:0));
  let score=0.25+coverage.ratio*0.38+Math.min(0.18,independent*0.08)+Math.min(0.1,external*0.05)+Math.min(0.09,technical*0.015);
  const aiDependent=Boolean(result&&result.provider==='gemini'||result&&result.analysis&&result.analysis.aiAssisted);
  if(aiDependent&&independent===0)score-=0.08;
  if(finalRisk==='unknown')score-=0.12;
  score=Math.max(0.12,Math.min(0.96,score));
  const level=score>=0.78?'high':score>=0.52?'medium':'low';
  let decision='VERIFY FIRST';
  if(finalRisk==='high')decision='HIGH RISK';
  else if(finalRisk==='low'&&identity.level==='high'&&score>=0.72)decision='LIKELY OK';
  else if(finalRisk==='low'&&identity.level==='unknown'&&score<0.52)decision='NOT ENOUGH EVIDENCE';
  const limitations=couldNotVerify(result,coverage);
  const sources=uniq([
    ...(technical?['Specialized scanners']:[]),
    ...((result&&result.domainIntelligence||[]).length?['DNS','RDAP','TLS']:[]),
    ...((result&&result.relationshipChecks||[]).length?['Website relationships']:[]),
    ...((result&&result.pageInspections||[]).some(x=>x&&x.state==='checked')?['Live webpage']:[]),
    ...((result&&result.reputationChecks||[]).filter(x=>x&&x.checked).map(x=>x.provider||'External reputation')),
    ...(result&&result.fileAnalysis?['Static file inspection']:[]),
    ...(aiDependent?['AI-assisted extraction']:[])
  ],x=>x,12);
  return{decision,finalRisk,identity,confidence:{level,score:Number(score.toFixed(2)),explanation:`${coverage.completed}/${coverage.total||0} relevant checks completed; ${independent} independent confirmation${independent===1?'':'s'}; ${technical} technical check${technical===1?'':'s'}.`},coverage,independentConfirmations:confirmed,warnings,noWarningFound:noWarning,couldNotVerify:limitations,sources};
}

module.exports={buildConfidence,buildCoverage,strongestRisk};
