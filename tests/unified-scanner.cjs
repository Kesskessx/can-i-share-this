const assert=require('node:assert/strict');
const {extractEvidence}=require('../lib/universal-evidence-orchestrator');
const wallet='0x0000000000000000000000000000000000000000';
const evidence=(text,base={})=>extractEvidence({detectedType:'message',originalInput:text,baseResult:base});
assert.deepEqual(evidence(wallet).phones,[]);
assert.deepEqual(evidence(wallet).crypto,[wallet]);
assert.deepEqual(evidence(wallet+' Call +33 6 12 34 56 78').phones,['+33 6 12 34 56 78']);
assert.deepEqual(evidence(wallet,{detectedElements:{phones:[wallet.slice(2)]}}).phones,[]);
console.log('Unified scanner: crypto/phone separation passed');

const {recalcFinalRisk}=require('../lib/mega-evidence-v3');
assert.equal(recalcFinalRisk({safety:{status:'caution'}}),'caution');
assert.equal(recalcFinalRisk({safety:{status:'high'}}),'high');
console.log('Primary scanner warnings survive final verdict');
