'use strict';

const assert=require('node:assert');
const { brandDomainStatus }=require('../lib/brand-registry');
const { analyzePhone }=require('../lib/phone-safety');
const { analyzeUploadedFile }=require('../lib/file-safety');
const { inspectHtml }=require('../lib/webpage-intelligence');
const { extractEvidence, candidateList, buildRelationGraph }=require('../lib/universal-evidence-orchestrator');
const { applyConfidenceCoverage }=require('../lib/confidence-coverage');
const { detectNetwork }=require('../lib/crypto-enrichment');

function filePayload(name,type,buffer){return{name,mimeType:type,dataBase64:buffer.toString('base64')}}

// 1. A normal message must become many evidence objects, not one first URL.
const wallet='0x1111111111111111111111111111111111111111';
const message='Urgent PayPal support: https://paypal-security-check.example/login and https://example.net/help. Email agent@example.org, call +234 801 234 5678 and pay '+wallet+'.';
const evidence=extractEvidence({detectedType:'message-url',originalInput:message,baseResult:{message:{urls:[],emails:[],phones:[]}}});
assert(evidence.urls.length>=2,'expected multiple URLs');
assert(evidence.emails.includes('agent@example.org'),'expected email extraction');
assert(evidence.phones.length>=1,'expected phone extraction');
assert(evidence.crypto.includes(wallet),'expected crypto extraction');
assert(evidence.claimedBrands.includes('paypal'),'expected claimed-brand extraction');
const candidates=candidateList(evidence,'message-url',message);
assert(candidates.some(x=>x.type==='url'),'URL candidate missing');
assert(candidates.some(x=>x.type==='email'),'email candidate missing');
assert(candidates.some(x=>x.type==='phone'),'phone candidate missing');
assert(candidates.some(x=>x.type==='crypto'),'crypto candidate missing');

// 2. Brand registry must distinguish an official domain from a conflicting one.
assert.equal(brandDomainStatus('PayPal','paypal.com').status,'confirmed');
assert.equal(brandDomainStatus('PayPal','paypal-security-check.example').status,'conflict');

// 3. Phone country mismatch is context, not owner identification.
const phone=analyzePhone('+234 801 234 5678','I am your French bank in France. Contact me on WhatsApp now.');
assert.equal(phone.phone.country,'Nigeria');
assert.equal(phone.phone.ownershipVerified,false);
assert.equal(phone.safety.status,'caution');
assert(phone.safety.signals.some(x=>x.code==='phone-geography-mismatch'));

// 4. Static file analysis catches misleading names and active PDF markers without execution.
const pdf=Buffer.from('%PDF-1.7\n1 0 obj << /OpenAction 2 0 R /JavaScript (alert(1)) >>\nhttps://example.com\n%%EOF','latin1');
const pdfResult=analyzeUploadedFile(filePayload('invoice.pdf.exe','application/octet-stream',pdf));
assert.equal(pdfResult.file.actualMime,'application/pdf');
assert.equal(pdfResult.safety.status,'high');
assert(pdfResult.safety.signals.some(x=>x.code==='file-double-extension'));
assert(pdfResult.safety.signals.some(x=>x.code==='pdf-javascript'));
assert(pdfResult.detectedElements.urls.includes('https://example.com'));

// 5. Raw EML authentication and routing mismatches are extracted.
const eml=Buffer.from([
  'From: PayPal Support <support@paypal.com>',
  'Reply-To: paypal-security@gmail.com',
  'Return-Path: <bounce@mailer.example>',
  'Subject: Verify now',
  'Date: Sun, 06 Sep 2026 20:00:00 +0000',
  'Message-ID: <1@example>',
  'Authentication-Results: mx.example; spf=fail smtp.mailfrom=mailer.example; dkim=fail header.d=paypal.com; dmarc=fail header.from=paypal.com',
  'Received: from mailer.example by mx.example;',
  '',
  'Verify at https://paypal-security-check.example/login'
].join('\r\n'),'utf8');
const emlResult=analyzeUploadedFile(filePayload('suspicious.eml','message/rfc822',eml));
assert(emlResult.emailMessage,'EML metadata missing');
assert.equal(emlResult.emailMessage.authentication.dmarc,'fail');
assert(emlResult.safety.signals.some(x=>x.code==='eml-replyto-mismatch'));
assert(emlResult.safety.signals.some(x=>x.code==='eml-dmarc-fail'));

// 6. Webpage structural analysis catches cross-domain credential collection and brand conflict.
const page=inspectHtml('<html><head><title>Microsoft Account Security</title></head><body><form method="post" action="https://collector.example/submit"><input type="password" name="password"></form></body></html>','https://microsoft-login.example/');
assert(page.hasPasswordField);
assert(page.findings.some(x=>x.code==='cross-domain-password-form'));
assert(page.findings.some(x=>x.code==='page-brand-domain-conflict'));

// 7. Relation graph keeps relationship status explicit.
const graph=buildRelationGraph({claimedBrands:['paypal'],domains:['paypal-security-check.example'],emails:[],socialProfiles:[],phones:[],crypto:[],files:[]},[{type:'claimed-brand-domain',status:'conflict',brand:'paypal',websiteDomain:'paypal-security-check.example'}]);
assert(graph.edges.some(x=>x.status==='conflict'));

// 8. Confidence is explained by completed/relevant checks rather than an opaque number.
const covered=applyConfidenceCoverage({
  detectedType:'message',
  megaScanner:{finalRisk:'low'},
  explanation:{verdict:'low',couldNotVerify:['Who controls the account']},
  detectedElements:{urls:['https://example.com'],domains:['example.com'],emails:[],phones:[],crypto:[],files:[],socialProfiles:[],claimedBrands:[]},
  crossChecks:[{type:'url',status:200,risk:'low',value:'https://example.com'}],
  domainIntelligence:[{domain:'example.com',completed:true,signals:[]}],
  webpageChecks:[{checked:true,finalUrl:'https://example.com',findings:[]}],
  relationshipChecks:[{type:'website-social',status:'confirmed',positive:true,detail:'Confirmed relationship'}],
  externalReputation:{consent:false,eligible:1,urlChecks:[],cryptoChecks:[]},
  positiveEvidence:[{title:'Confirmed relationship'}],
  noWarningEvidence:[{title:'No major URL warning'}]
});
assert(covered.coverageMatrix.relevant>covered.coverageMatrix.completed,'consent-gated reputation should remain pending');
assert(covered.coverageMatrix.independentEvidenceCount>=2);
assert(/relevant checks completed/.test(covered.explanation.confidence.explanation));

// 9. External crypto routing recognizes supported public networks.
assert.equal(detectNetwork(wallet),'ethereum');
assert.equal(detectNetwork('bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'),'bitcoin');

console.log('Universal Evidence V4 tests passed');
