'use strict';

const assert = require('node:assert/strict');
const { extractEvidence, normalizeWeakAccountRisk } = require('../lib/image-evidence-orchestrator');
const { upgradeMegaResult } = require('../lib/mega-evidence-v3');
const { canonicalSocial, extractDomainsFromText } = require('../lib/evidence-relations');

function ok(name, fn) { fn(); console.log(`Mega V3 test passed: ${name}`); }

ok('extract all useful screenshot elements', () => {
  const data = extractEvidence({ analysis: {
    urls: ['https://example.com/login'],
    emails: ['support@example.net'],
    phones: ['+33612345678'],
    qr_values: ['https://qr.example.org/pay', '0x1111111111111111111111111111111111111111'],
    claimed_brands: ['Example'],
    social_profile: { platform: 'X', username: 'ExampleHelp' },
    visible_text: 'Example support. Website example.com. Open invoice.pdf. Send 0x1111111111111111111111111111111111111111 now.'
  }});
  const types = new Set(data.candidates.map(x => x.type));
  for (const expected of ['social-profile','url','email','crypto','message']) assert.equal(types.has(expected), true, expected);
  assert.equal(data.elements.files.some(x => x.toLowerCase().endsWith('invoice.pdf')), true);
  assert.equal(data.elements.phones[0], '+33612345678');
});

ok('new account metrics are context not scam proof', () => {
  const out = normalizeWeakAccountRisk({
    risk: 'caution', summary: 'Profile needs verification',
    suspicious_signals: [{ type: 'low_account_metrics', detail: 'Only 1 follower and 2 following; account joined recently.' }]
  });
  assert.equal(out.risk, 'low');
  assert.match(out.summary, /No strong impersonation sign/i);
  assert.equal(out.suspicious_signals[0].context_only, true);
});

ok('reciprocal website link raises identity consistency, not risk', () => {
  const out = upgradeMegaResult({
    detectedType: 'image',
    analysis: { risk: 'low', social_profile: { platform: 'X', username: 'CanIshareLink' } },
    crossChecks: [
      { type: 'url', value: 'https://canisharethis.com', risk: 'low', summary: 'No obvious suspicious URL patterns detected' },
      { type: 'social-profile', value: 'https://x.com/CanIshareLink', risk: 'low', summary: 'No obvious scam profile pattern' }
    ],
    relationshipChecks: [{ type: 'website-social', websiteDomain: 'canisharethis.com', socialPlatform: 'x', socialHandle: 'canisharelink', status: 'confirmed', positive: true, detail: 'canisharethis.com links to the same X profile @canisharelink.' }],
    detectedElements: { urls: ['https://canisharethis.com'], domains: ['canisharethis.com'], socialProfiles: ['https://x.com/CanIshareLink'], emails: [], phones: [], crypto: [], qr: [], files: [], claimedBrands: ['Can I Share This?'] },
    accountContext: { maturity: 'limited', note: 'Limited account history is context, not proof of impersonation.' },
    brandMismatch: { detected: false, items: [] }, correlations: [],
    evidenceGraph: { version: '2.0', nodes: [{ id: 'e1', type: 'domain', value: 'canisharethis.com' }], edges: [] },
    explanation: { verdict: 'caution', headline: 'Profile needs verification', reasons: [
      { title: 'Low account metrics', detail: 'Only 1 follower and 2 following.' },
      { title: 'Profile needs verification', detail: 'Only 1 follower and 2 following.' }
    ], action: 'Verify independently', confidence: { level: 'medium', score: 0.7 }, couldNotVerify: ['Anything not visible in the screenshot'] },
    shareSummary: {}, megaScanner: { version: '2.0', finalRisk: 'caution' }
  });
  assert.equal(out.megaScanner.finalRisk, 'low');
  assert.equal(out.identityConsistency.level, 'high');
  assert.equal(out.positiveEvidence.some(x => x.type === 'reciprocal-social-link'), true);
  assert.match(out.explanation.headline, /mutually consistent/i);
  assert.equal(out.explanation.couldNotVerify.some(x => /Anything not visible/i.test(x)), false);
});

ok('strong mismatch remains high despite a positive relation', () => {
  const out = upgradeMegaResult({
    analysis: { risk: 'low' }, crossChecks: [],
    relationshipChecks: [{ websiteDomain: 'example.com', socialPlatform: 'x', socialHandle: 'brand', status: 'confirmed', positive: true, detail: 'example.com links to X @brand.' }],
    brandMismatch: { detected: true, items: [{ brand: 'PayPal', observedDomain: 'paypal-login.example', role: 'destination', severity: 'high' }] },
    correlations: [], explanation: { reasons: [], confidence: { score: 0.6 } }, evidenceGraph: { nodes: [], edges: [] }, megaScanner: { finalRisk: 'low' }
  });
  assert.equal(out.megaScanner.finalRisk, 'high');
  assert.equal(out.identityConsistency.level, 'low');
});

ok('social and bare-domain normalization', () => {
  const social = canonicalSocial('https://x.com/CanIshareLink');
  assert.equal(social.platform, 'x');
  assert.equal(social.handle, 'canisharelink');
  const domains = extractDomainsFromText('Visit canisharethis.com or https://example.org/path');
  assert.equal(domains.includes('canisharethis.com'), true);
  assert.equal(domains.includes('example.org'), true);
});
