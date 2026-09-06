'use strict';

const assert=require('node:assert/strict');
const { collectEvidence, brandRelations }=require('../lib/universal-evidence-orchestrator');
const { analyzeEml, analyzeFile }=require('../lib/file-safety');
const { analyzePhone }=require('../lib/phone-context');
const { buildConfidence }=require('../lib/confidence-engine');

(async()=>{
  const msg='PayPal security: urgent. Visit https://paypal-security-check.example/login and https://example.org/help. Reply support@paypal-security-check.example or WhatsApp +234 812 345 6789. Send BTC to bc1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq.';
  const ev=collectEvidence({detectedType:'message',originalInput:msg,baseResult:{message:{claimedBrands:['PayPal']}},fileAnalysis:null});
  assert.ok(ev.urls.length>=2,'all URLs should be extracted');
  assert.ok(ev.emails.length>=1,'email should be extracted');
  assert.ok(ev.phones.length>=1,'phone should be extracted');
  assert.ok(ev.domains.includes('paypal-security-check.example'),'domain should be extracted');
  assert.ok(ev.claimedBrands.some(x=>String(x).toLowerCase()==='paypal'),'claimed brand should be preserved');

  const conflicts=brandRelations({claimedBrands:['paypal'],domains:['paypal-security-check.example'],urls:[]},[],[]);
  assert.equal(conflicts[0].status,'conflict');
  const official=brandRelations({claimedBrands:['paypal'],domains:['paypal.com'],urls:[]},[],[]);
  assert.equal(official[0].status,'confirmed');

  const eml=analyzeEml('From: PayPal <support@paypal.com>\r\nReply-To: paypal-help@gmail.com\r\nReturn-Path: <bounce@mailer.example>\r\nAuthentication-Results: mx.example; spf=fail dkim=pass dmarc=fail\r\nSubject: Verify now\r\n\r\nOpen https://paypal-security-check.example/login');
  assert.equal(eml.fromDomain,'paypal.com');
  assert.equal(eml.replyDomain,'gmail.com');
  assert.ok(eml.warnings.some(x=>x.code==='reply-to-mismatch'));
  assert.ok(eml.warnings.some(x=>x.code==='dmarc-fail'));

  const file=await analyzeFile({name:'invoice.pdf.exe',mime:'application/pdf',data:Buffer.from('MZ powershell cmd.exe').toString('base64')});
  assert.equal(file.safety.status,'high');
  assert.ok(file.safety.signals.some(x=>x.code==='double-extension'));
  assert.equal(file.file.detectedMime,'application/x-dosexec');

  const phone=analyzePhone('+234 812 345 6789','French bank support in France. Contact me on WhatsApp for payment.');
  assert.equal(phone.country,'Nigeria');
  assert.ok(phone.signals.some(x=>x.code==='phone-geography-mismatch'));

  const confidence=buildConfidence({
    detectedType:'message',originalInput:'test',
    detectedElements:{urls:['https://example.com'],domains:['example.com'],emails:[],phones:[],crypto:[],qr:[],socialProfiles:[],claimedBrands:[],files:[]},
    crossChecks:[{type:'url',risk:'low',status:200,summary:'No obvious warning'}],
    domainIntelligence:[{domain:'example.com',state:'checked',risk:'low',registration:{ageDays:500}}],
    pageInspections:[{state:'checked',signals:[]}],reputationChecks:[{checked:false,status:'consent-required'}],relationshipChecks:[],brandRelations:[]
  });
  assert.ok(confidence.coverage.total>=4);
  assert.ok(confidence.coverage.completed>=3);
  assert.ok(['low','medium','high'].includes(confidence.confidence.level));

  console.log('Universal Evidence Engine tests passed');
})().catch(err=>{console.error(err);process.exit(1)});
