'use strict';
const assert = require('node:assert/strict');
const { enrichScanResult } = require('../lib/mega-evidence');

function run(name, input, type, body, check) {
  const out = enrichScanResult({ detectedType: type, originalInput: input, body });
  check(out);
  console.log(`Mega evidence test passed: ${name}`);
}

run('official brand domain', 'https://www.paypal.com/signin', 'url', {
  finalUrl: 'https://www.paypal.com/signin', safety: { status: 'low', riskScore: 0, signals: [] }
}, out => {
  assert.equal(out.brandMismatch.detected, false);
  assert.equal(out.megaScanner.finalRisk, 'low');
});

run('brand lookalike correlation', 'PayPal security: verify now https://paypal-secure-login.example', 'message-url', {
  message: { urls: ['https://paypal-secure-login.example'], claimedBrands: ['PayPal'] },
  safety: { status: 'caution', riskScore: 45, signals: [{ type: 'urgency', title: 'Urgency', detail: 'Act immediately.' }] }
}, out => {
  assert.equal(out.brandMismatch.detected, true);
  assert.equal(out.megaScanner.finalRisk, 'high');
  assert.ok(out.correlations.some(c => c.id === 'brand-domain-mismatch'));
});

run('casual brand mention', 'I bought this on Amazon. Seller page: https://example.com/item', 'message-url', {
  message: { urls: ['https://example.com/item'], claimedBrands: [] },
  safety: { status: 'low', riskScore: 5, signals: [] }
}, out => {
  assert.equal(out.brandMismatch.detected, false);
  assert.equal(out.megaScanner.finalRisk, 'low');
});

run('sender mismatch', 'support@paypal-security-mail.example', 'email', {
  safety: { status: 'caution', riskScore: 40, signals: [] }
}, out => {
  assert.equal(out.brandMismatch.detected, true);
  assert.equal(out.megaScanner.finalRisk, 'high');
});

run('share summary privacy', 'Call +33612345678 and send to 0x1111111111111111111111111111111111111111', 'message', {
  message: { phones: ['+33612345678'] },
  safety: { status: 'caution', riskScore: 45, signals: [{ type: 'payment', title: 'Payment request', detail: 'Send payment to 0x1111111111111111111111111111111111111111 and call +33612345678.' }] }
}, out => {
  const raw = JSON.stringify(out.shareSummary);
  assert.equal(raw.includes('+33612345678'), false);
  assert.equal(raw.includes('0x1111111111111111111111111111111111111111'), false);
});
