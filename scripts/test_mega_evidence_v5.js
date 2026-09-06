'use strict';
const assert = require('node:assert/strict');
const { upgradeMegaResult } = require('../lib/mega-evidence-v3');

function ok(name, fn) { fn(); console.log(`Mega V5 test passed: ${name}`); }

ok('no confirmed relationship does not become positive proof', () => {
  const out = upgradeMegaResult({
    detectedType: 'image',
    analysis: { risk: 'low', social_profile: { platform: 'Instagram', username: 'example' } },
    crossChecks: [
      { type: 'url', value: 'https://youtube.com', risk: 'low', summary: 'No obvious suspicious URL patterns detected' },
      { type: 'social-profile', value: 'https://instagram.com/example', risk: 'low', summary: 'No obvious scam or impersonation pattern found' }
    ],
    relationshipChecks: [{ type: 'website-social', websiteDomain: 'youtube.com', socialPlatform: 'instagram', socialHandle: 'example', status: 'not-found', positive: false, detail: 'No exact link found.' }],
    detectedElements: {
      urls: ['https://youtube.com'], domains: ['youtube.com'], emails: [], phones: [], crypto: [], qr: [],
      files: ['youtube.com'], socialProfiles: ['https://instagram.com/example'], claimedBrands: ['YouTube']
    },
    brandMismatch: { detected: false, items: [] }, correlations: [],
    explanation: { verdict: 'low', headline: 'No major warning', reasons: [], action: 'Continue carefully', confidence: { level: 'medium', score: 0.70 } },
    evidenceGraph: { nodes: [], edges: [] }, megaScanner: { finalRisk: 'low' }
  });
  assert.equal(out.positiveEvidence.length, 0);
  assert.ok(out.noWarningEvidence.length >= 2);
  assert.equal(out.identityConsistency.level, 'medium');
  assert.equal(out.detectedElements.files.length, 0);
  assert.match(out.explanation.headline, /not independently confirmed/i);
  assert.equal(out.verifiedRelationships.length, 0);
});

ok('confirmed reciprocal link is positive proof', () => {
  const out = upgradeMegaResult({
    detectedType: 'image',
    analysis: { risk: 'low', social_profile: { platform: 'X', username: 'CanIshareLink' } },
    crossChecks: [
      { type: 'url', value: 'https://canisharethis.com', risk: 'low', summary: 'No major URL warning' },
      { type: 'social-profile', value: 'https://x.com/CanIshareLink', risk: 'low', summary: 'No strong impersonation pattern' }
    ],
    relationshipChecks: [{ type: 'website-social', websiteDomain: 'canisharethis.com', socialPlatform: 'x', socialHandle: 'canisharelink', status: 'confirmed', positive: true, detail: 'canisharethis.com links to the same X profile @canisharelink.' }],
    detectedElements: { urls: ['https://canisharethis.com'], domains: ['canisharethis.com'], emails: [], phones: [], crypto: [], qr: [], files: [], socialProfiles: ['https://x.com/CanIshareLink'], claimedBrands: ['Can I Share This?'] },
    brandMismatch: { detected: false, items: [] }, correlations: [],
    explanation: { verdict: 'low', headline: 'Looks normal', reasons: [], action: 'Continue carefully', confidence: { level: 'medium', score: 0.70 } },
    evidenceGraph: { nodes: [], edges: [] }, megaScanner: { finalRisk: 'low' }
  });
  assert.equal(out.positiveEvidence.some(x => x.type === 'reciprocal-social-link'), true);
  assert.equal(out.identityConsistency.level, 'high');
  assert.equal(out.verifiedRelationships.length, 1);
  assert.equal(out.noWarningEvidence.some(x => x.type === 'social-check-low'), true);
});

ok('absence of warning is not copied into WHY reasons', () => {
  const out = upgradeMegaResult({
    analysis: { risk: 'low' }, crossChecks: [], relationshipChecks: [],
    detectedElements: { urls: [], domains: [], files: [], socialProfiles: [], claimedBrands: [], emails: [], phones: [], crypto: [], qr: [] },
    brandMismatch: { detected: false, items: [] }, correlations: [],
    explanation: { verdict: 'low', headline: 'No warning', reasons: [
      { title: 'No obvious impersonation signs', detail: 'No obvious scam or impersonation pattern was found.' }
    ], confidence: { score: 0.55 } },
    evidenceGraph: { nodes: [], edges: [] }, megaScanner: { finalRisk: 'low' }
  });
  assert.equal(out.explanation.reasons.length, 0);
});
