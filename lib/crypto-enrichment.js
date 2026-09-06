'use strict';

function clean(v,max=300){return String(v==null?'':v).replace(/\0/g,'').trim().slice(0,max)}
function withTimeout(promise,ms){return Promise.race([promise,new Promise((_,reject)=>setTimeout(()=>reject(Object.assign(new Error('timeout'),{name:'AbortError'})),ms))])}
async function jsonFetch(url,options,ms=4500){const r=await withTimeout(fetch(url,options),ms);if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}
function detectNetwork(address){
  const a=clean(address,160);
  if(/^0x[a-fA-F0-9]{40}$/.test(a))return'ethereum';
  if(/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(a)||/^[13][1-9A-HJ-NP-Za-km-z]{25,34}$/.test(a))return'bitcoin';
  if(/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(a))return'solana';
  return'unsupported';
}
async function bitcoinActivity(address){
  const d=await jsonFetch(`https://mempool.space/api/address/${encodeURIComponent(address)}`,{headers:{'user-agent':'CanIShareThis/4.0 (+https://canisharethis.com)'}},4500);
  const c=d.chain_stats||{},m=d.mempool_stats||{};
  return{provider:'mempool.space',network:'Bitcoin',checked:true,transactionCount:Number(c.tx_count||0)+Number(m.tx_count||0),fundedSats:Number(c.funded_txo_sum||0)+Number(m.funded_txo_sum||0),spentSats:Number(c.spent_txo_sum||0)+Number(m.spent_txo_sum||0),publicLabels:[],reputationChecked:false};
}
async function ethereumActivity(address){
  const rpc=async(method,params)=>jsonFetch('https://cloudflare-eth.com',{method:'POST',headers:{'content-type':'application/json','user-agent':'CanIShareThis/4.0 (+https://canisharethis.com)'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})},4500);
  const [balance,nonce]=await Promise.all([rpc('eth_getBalance',[address,'latest']),rpc('eth_getTransactionCount',[address,'latest'])]);
  const hexToBig=x=>{try{return BigInt(x||'0x0')}catch(_){return 0n}};
  return{provider:'Cloudflare Ethereum Gateway',network:'Ethereum / EVM',checked:true,transactionCount:Number(hexToBig(nonce&&nonce.result)),balanceWei:hexToBig(balance&&balance.result).toString(),publicLabels:[],reputationChecked:false};
}
async function solanaActivity(address){
  const body=method=>({jsonrpc:'2.0',id:1,method,params:method==='getBalance'?[address,{commitment:'confirmed'}]:[address,{limit:20,commitment:'confirmed'}]});
  const [bal,sigs]=await Promise.all([
    jsonFetch('https://api.mainnet-beta.solana.com',{method:'POST',headers:{'content-type':'application/json','user-agent':'CanIShareThis/4.0 (+https://canisharethis.com)'},body:JSON.stringify(body('getBalance'))},4500),
    jsonFetch('https://api.mainnet-beta.solana.com',{method:'POST',headers:{'content-type':'application/json','user-agent':'CanIShareThis/4.0 (+https://canisharethis.com)'},body:JSON.stringify(body('getSignaturesForAddress'))},4500)
  ]);
  const list=Array.isArray(sigs&&sigs.result)?sigs.result:[];
  return{provider:'Solana public RPC',network:'Solana',checked:true,recentTransactionSample:list.length,balanceLamports:Number(bal&&bal.result&&bal.result.value||0),lastSeenUnix:list[0]&&list[0].blockTime||null,publicLabels:[],reputationChecked:false};
}
async function enrichCryptoAddress(address,{consent=false}={}){
  const network=detectNetwork(address);
  if(!consent)return{checked:false,status:'consent-required',network,detail:'External chain-activity lookup was not performed. It would share the public wallet address with a third-party public blockchain service.'};
  try{
    let result;if(network==='bitcoin')result=await bitcoinActivity(address);else if(network==='ethereum')result=await ethereumActivity(address);else if(network==='solana')result=await solanaActivity(address);else return{checked:false,status:'unsupported',network,detail:'No external activity provider is configured for this network.'};
    return{...result,status:'activity-read',detail:'Public blockchain activity was read. Activity is context only and does not identify the wallet owner or prove trustworthiness.'};
  }catch(err){return{checked:false,status:err&&err.name==='AbortError'?'timeout':'unavailable',network,detail:'Public blockchain activity could not be retrieved for this scan.'}}
}
module.exports={enrichCryptoAddress,detectNetwork};
