'use strict';

const assert = require('node:assert/strict');
const {parseFilePayload, MAX_BYTES} = require('../lib/file-safety');
const {applyConfidenceCoverage} = require('../lib/confidence-coverage');

for (const data of ['%%%invalid%%%', 'a', 'YQ===', 'YQ=', 'Y=Q=', 'YR==', 'data:text/plain;base64,%%%']) {
  assert.throws(() => parseFilePayload({name: 'test.txt', data}), /invalid/);
}
for (const data of ['YQ==', 'YQ', 'data:text/plain;base64,YQ==', ' YQ==\n']) {
  assert.equal(parseFilePayload({name:'test.txt',data}).bytes.toString(), 'a');
}
assert.throws(() => parseFilePayload({data:'A'.repeat(4*Math.ceil(MAX_BYTES/3)+4)}), /too large/);
assert.equal(parseFilePayload({data:Buffer.alloc(MAX_BYTES).toString('base64')}).bytes.length,MAX_BYTES);

const coverage = applyConfidenceCoverage({
  crossChecks:[{type:'url'}, {type:'email',status:500,risk:'low'}, {type:'phone',status:200,risk:'unknown'}, {type:'url',status:200,risk:'low'}],
  externalReputation:{consent:true,eligible:2,urlChecks:[{}, {checked:false}],cryptoChecks:[]}
}).coverageMatrix;
assert.equal(coverage.completed, 2, 'Only the primary check and explicit usable URL result completed');
assert.equal(coverage.pending, 4);
assert(!coverage.completedChecks.some(x => x.id.startsWith('reputation:')));
const many = applyConfidenceCoverage({crossChecks:Array.from({length:18},()=>({type:'url',status:500}))}).coverageMatrix;
assert.equal(many.pending,18, 'Unresolved count must not be truncated with the display list');

// Exercise the actual API dispatcher with isolated scanner dependencies.
// Remote checks are stubbed; file decoding and HTTP validation remain real.
function stub(path, value) { require.cache[require.resolve(path)] = {id:require.resolve(path),filename:require.resolve(path),loaded:true,exports:value}; }
const routed = [];
for (const [path,label] of [['../api/check','url'],['../api/email-check','email'],['../api/crypto-check','crypto'],['../api/message-check','message'],['../api/image-check','image'],['../lib/social-profile-safety','social']]) {
  stub(path, async (req,res)=>{routed.push(label);res.status(200).json({safety:{status:'caution'},received:req.body});});
}
stub('../lib/universal-evidence-orchestrator',{orchestrateUniversalEvidence:async ({baseResult})=>baseResult});
stub('../lib/mega-evidence',{enrichScanResult:({body})=>body});
stub('../lib/mega-evidence-v3',{upgradeMegaResult:x=>x});
stub('../lib/image-evidence-orchestrator',{orchestrateImageResult:async x=>x});
const handler=require('../api/analyze');
async function request(body) {
  const res={statusCode:200,setHeader(){},status(code){this.statusCode=code;return this},json(body){this.body=body;return this}};
  await handler({method:'POST',body},res);
  return res;
}
(async()=>{
  for (const [input,expected] of [
    ['https://example.com','url'],
    ['https://example.com Pay immediately and send your password','message'],
    ['https://instagram.com/example','social'],
    ['https://instagram.com/example send the verification code','message'],
    ['Contact support@example.com immediately','message'],
    ['support@example.com','email'],
    ['0x1111111111111111111111111111111111111111','crypto']
  ]) {const res=await request({input});assert.equal(res.statusCode,200);assert.equal(routed.pop(),expected,input);}
  for(const body of ['null','[]','42'])assert.equal((await request(body)).statusCode,400);
  assert.equal((await request({file:{name:'test.txt',data:'%%%invalid%%%'}})).statusCode,400);
  assert.equal((await request({file:{name:'test.txt',data:'YQ=='}})).statusCode,200);
  assert.equal((await request({file:{name:'test.txt',data:'A'.repeat(4*Math.ceil(MAX_BYTES/3)+4)}})).statusCode,413);
  console.log('Scanner diagnostics regression tests passed: routing, upload validation, HTTP errors and coverage');
})().catch(e=>{console.error(e);process.exitCode=1});
