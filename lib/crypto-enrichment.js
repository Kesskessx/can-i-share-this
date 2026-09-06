'use strict';

function clean(v,max=300){return String(v==null?'':v).trim().slice(0,max)}
function withTimeout(ms){const c=new AbortController();const t=setTimeout(()=>c.abort(),ms);return {signal:c.signal,done:()=>clearTimeout(t)}}

function networkFor(address){
  const v=clean(address,180);
  if(/^bc1/i.test(v)||/^[13][1-9A-HJ-NP-Za-km-z]{25,34}$/.test(v))return'bitcoin';
  if(/^0x[a-fA-F0-9]{40}$/.test(v))return'ethereum';
  if(/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v))return'tron';
  if(/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(v))return'solana';
  return'unknown';
}

async function bitcoinActivity(address){
  const timer=withTimeout(3500);
  try{
    const r=await fetch(`https://blockstream.info/api/address/${encodeURIComponent(address)}`,{headers:{accept:'application/json','user-agent':'CanIShareThis/4.0'},signal:timer.signal});
    if(!r.ok)return{provider:'Blockstream',checked:false,status:'unavailable'};
    const j=await r.json();
    const chain=j.chain_stats||{},mempool=j.mempool_stats||{};
    return{provider:'Blockstream',checked:true,status:'activity-available',transactionCount:Number(chain.tx_count||0)+Number(mempool.tx_count||0),fundedSats:Number(chain.funded_txo_sum||0),spentSats:Number(chain.spent_txo_sum||0),mempoolTxCount:Number(mempool.tx_count||0)};
  }catch(_){return{provider:'Blockstream',checked:false,status:'unavailable'}}finally{timer.done()}
}

async function ethereumActivity(address){
  const key=String(process.env.ETHERSCAN_API_KEY||'').trim();
  if(!key)return{provider:'Etherscan',checked:false,status:'not-configured'};
  const timer=withTimeout(4000);
  try{
    const qs=new URLSearchParams({chainid:'1',module:'account',action:'txlist',address,sort:'desc',page:'1',offset:'10',apikey:key});
    const r=await fetch(`https://api.etherscan.io/v2/api?${qs}`,{signal:timer.signal,headers:{accept:'application/json'}});
    if(!r.ok)return{provider:'Etherscan',checked:false,status:'unavailable'};
    const j=await r.json();
    const txs=Array.isArray(j.result)?j.result:[];
    const times=txs.map(x=>Number(x.timeStamp||0)).filter(Boolean).sort((a,b)=>a-b);
    return{provider:'Etherscan',checked:true,status:'activity-available',recentTransactionsReturned:txs.length,latestActivityAt:times.length?new Date(times[times.length-1]*1000).toISOString():null,oldestActivityInSampleAt:times.length?new Date(times[0]*1000).toISOString():null};
  }catch(_){return{provider:'Etherscan',checked:false,status:'unavailable'}}finally{timer.done()}
}

async function enrichCrypto(address){
  const network=networkFor(address);
  let activity={provider:null,checked:false,status:'unsupported'};
  if(network==='bitcoin')activity=await bitcoinActivity(address);
  else if(network==='ethereum')activity=await ethereumActivity(address);
  return{network,activity,reputation:{checked:false,status:'not-integrated'},interpretation:activity.checked?'Public blockchain activity was found. Activity alone does not identify the owner or establish trustworthiness.':'No public activity enrichment was available for this scan.',disclaimer:'A new, inactive or highly active wallet is not by itself evidence of fraud.'};
}

module.exports={enrichCrypto,networkFor};
