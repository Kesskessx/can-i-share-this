'use strict';

function clean(v,max=500){return String(v==null?'':v).replace(/\0/g,'').replace(/\s+/g,' ').trim().slice(0,max)}
function arr(v){return Array.isArray(v)?v:[]}
function uniq(items,key=x=>String(x),max=40){const out=[],seen=new Set();for(const x of items||[]){const k=key(x);if(!k||seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=max)break}return out}
function resultRisk(result){return clean(result&&result.megaScanner&&result.megaScanner.finalRisk||result&&result.explanation&&result.explanation.verdict||result&&result.safety&&result.safety.status||'unknown',30).toLowerCase()}
function sourceName(x){return clean(x,80)}

function applyConfidenceCoverage(input){
  if(!input||typeof input!=='object'||Array.isArray(input)||input.error)return input;
  const el=input.detectedElements||{},completed=[],pending=[],sources=[],independent=[];
  const addCompleted=(id,label,source,weight=1)=>{completed.push({id,label,source,weight});if(source)sources.push(source)};
  const addPending=(id,label,reason)=>pending.push({id,label,reason});

  addCompleted('base','Primary safety analysis','Mega Scanner',1);
  if(input.detectedType==='image'||input.analysis&&input.analysis.visible_text)addCompleted('extraction','Evidence extraction','Image/text extraction',.6);
  if(input.file&&input.file.sha256)addCompleted('file-static','Static file structure and SHA-256','Local static analysis',2);
  if(input.emailMessage)addCompleted('eml','Raw email headers and authentication results','Email headers',2);

  for(const c of arr(input.crossChecks)){
    const type=clean(c&&c.type,50)||'element';
    if(c&&Number(c.status)>=200&&Number(c.status)<300&&['low','caution','high'].includes(clean(c.risk,20)))addCompleted(`check:${type}:${completed.length}`,`${type.replace(/-/g,' ')} specialized check`,`${type} scanner`,1.5);
    else addPending(`check:${type}:${pending.length}`,`${type.replace(/-/g,' ')} specialized check`,'The specialized check did not complete with a usable result.');
  }
  for(const d of arr(input.domainIntelligence)){
    if(d&&d.completed){addCompleted(`domain:${d.domain}`,`Domain intelligence for ${d.domain}`,'DNS / RDAP / TLS',2);independent.push({type:'domain-intelligence',label:`DNS/RDAP intelligence for ${d.domain}`})}
    else addPending(`domain:${d&&d.domain||pending.length}`,'Domain intelligence','DNS/RDAP data was unavailable.');
  }
  for(const w of arr(input.webpageChecks)){
    if(w&&w.checked){addCompleted(`page:${w.finalUrl||completed.length}`,'Live webpage structure check','Live webpage HTML',2);independent.push({type:'webpage',label:'Live webpage structure was checked independently'})}
    else addPending(`page:${pending.length}`,'Live webpage structure check','The page could not be read or was not HTML.');
  }
  for(const r of arr(input.relationshipChecks)){
    const label=clean(r&&r.type,80).replace(/-/g,' ')||'identity relationship';
    if(r&&['confirmed','conflict','not-found','consistent'].includes(r.status)){addCompleted(`rel:${completed.length}`,label,'Relationship check',2);if(r.status==='confirmed'||r.status==='consistent')independent.push({type:'relationship',label:clean(r.detail,300)||'Identity relationship confirmed'})}
    else addPending(`rel:${pending.length}`,label,clean(r&&r.detail,300)||'The relationship could not be independently verified.');
  }

  const reputation=input.externalReputation||{};
  const eligible=Number(reputation.eligible||0);
  if(eligible>0){
    if(reputation.consent===true){
      const checked=arr(reputation.urlChecks).filter(x=>x&&x.checked===true).length+arr(reputation.cryptoChecks).filter(x=>x&&x.checked===true).length;
      if(checked)for(let i=0;i<checked;i++)addCompleted(`reputation:${i}`,'External reputation/activity source','External reputation',2.5);
      if(checked)independent.push({type:'external-reputation',label:`${checked} external reputation/activity source${checked===1?'':'s'} completed`});
      if(checked<eligible)addPending('reputation-incomplete','External reputation','Some eligible entities could not be checked externally.');
    }else addPending('reputation-consent','External reputation','Not checked because explicit consent is required before sharing URLs or wallet addresses with external providers.');
  }

  const positive=arr(input.positiveEvidence);
  for(const p of positive)independent.push({type:'confirmed-evidence',label:clean(p&&p.title,200)||'Independent evidence confirmed'});
  const noWarnings=arr(input.noWarningEvidence);
  const risk=resultRisk(input);
  const relevant=completed.length+pending.length;
  const completedWeight=completed.reduce((n,x)=>n+Number(x.weight||1),0);
  const pendingWeight=pending.reduce((n)=>n+1,0);
  const ratio=relevant?completed.length/relevant:0;
  const weightedRatio=(completedWeight+pendingWeight)>0?completedWeight/(completedWeight+pendingWeight):0;
  const independentUnique=uniq(independent,x=>`${x.type}:${x.label}`,12);
  const aiDependent=(input.detectedType==='image'?1:0)+(input.message&&input.message.aiAssisted?1:0);
  let score=.28+weightedRatio*.42+Math.min(.24,independentUnique.length*.07)-Math.min(.1,aiDependent*.03)-Math.min(.12,pending.length*.015);
  if(risk==='high'&&independentUnique.length)score+=.03;
  score=Math.max(.2,Math.min(.96,score));
  let level='low';if(ratio>=.72&&independentUnique.length>=2)level='high';else if(ratio>=.48||independentUnique.length>=1)level='medium';
  if(pending.length===0&&ratio>=.8&&independentUnique.length>=2)level='high';

  const warnings=[];
  for(const d of arr(input.domainIntelligence))for(const s of arr(d&&d.signals))warnings.push({title:clean(s.title,180),detail:clean(s.detail,360),source:'Domain intelligence'});
  for(const w of arr(input.webpageChecks))for(const s of arr(w&&w.findings))if(['high','medium','low'].includes(s&&s.severity))warnings.push({title:clean(s.title,180),detail:clean(s.detail,360),source:'Webpage'});
  for(const r of arr(input.relationshipChecks))if(r&&r.status==='conflict')warnings.push({title:'Identity relationship conflict',detail:clean(r.detail,360),source:'Relationship check'});

  const coverage={
    completed:completed.length,relevant,pending:pending.length,ratio:Number(ratio.toFixed(2)),
    completedChecks:completed.slice(0,20),pendingChecks:pending.slice(0,12),
    independentEvidence:independentUnique,
    independentEvidenceCount:independentUnique.length,
    aiDependentObservations:aiDependent,
    sources:uniq(sources.map(sourceName).filter(Boolean),x=>x,16),
    warningSignals:uniq(warnings,x=>`${x.title}:${x.detail}`,10),
    noWarningFindings:noWarnings.slice(0,8),
    couldNotVerify:arr(input.explanation&&input.explanation.couldNotVerify).slice(0,8)
  };
  const ex=input.explanation&&typeof input.explanation==='object'?{...input.explanation}:{};
  ex.confidence={level,score:Number(score.toFixed(2)),explanation:`${completed.length}/${relevant||completed.length} relevant checks completed; ${independentUnique.length} independent evidence source${independentUnique.length===1?'':'s'}; ${pending.length} unresolved check${pending.length===1?'':'s'}.`};
  return{...input,explanation:ex,coverageMatrix:coverage,megaScanner:{...(input.megaScanner||{}),coverageVersion:'4.0',evidenceCoverage:coverage.ratio}};
}

module.exports={applyConfidenceCoverage};
