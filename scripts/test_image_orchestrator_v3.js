'use strict';
const assert = require('node:assert/strict');
const { extractEvidence } = require('../lib/image-evidence-orchestrator');
const result = extractEvidence({analysis:{
  urls:['https://canisharethis.com'],
  emails:['hello@example.com'],
  phones:['+33123456789'],
  qr_values:['https://example.org/path'],
  claimed_brands:['Can I Share This?'],
  social_profile:{platform:'X',username:'CanIshareLink'},
  visible_text:'Can I Share This? @CanIshareLink canisharethis.com hello@example.com +33123456789 invoice.pdf'
}});
const types=new Set(result.candidates.map(x=>x.type));
['url','email','social-profile','message'].forEach(x=>assert.equal(types.has(x),true,x));
assert.equal(result.elements.files.includes('invoice.pdf'),true);
assert.equal(result.elements.socialProfiles.length,1);
console.log('Image orchestrator V3 test passed');
