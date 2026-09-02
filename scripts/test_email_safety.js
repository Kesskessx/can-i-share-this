const assert = require('node:assert');
const {
  assessEmail,
  findBrandLookalike,
  parseEmailAddress
} = require('../lib/email-safety');

function dns(overrides = {}) {
  return {
    domainExists: true,
    domainExistsKnown: true,
    mxKnown: true,
    hasMx: true,
    mxCount: 2,
    spfKnown: true,
    hasSpf: true,
    dmarcKnown: true,
    hasDmarc: true,
    ...overrides
  };
}

const paypal = parseEmailAddress('support@paypal.com');
assert.equal(paypal.domain, 'paypal.com');
assert.equal(findBrandLookalike(paypal.domain), null);
let result = assessEmail({ ...paypal, dnsInfo: dns() });
assert.equal(result.status, 'low');
assert.equal(result.riskScore, 0);

const fakePaypal = parseEmailAddress('security@paypa1-security.com');
assert.equal(findBrandLookalike(fakePaypal.domain), 'paypal');
result = assessEmail({ ...fakePaypal, dnsInfo: dns() });
assert.ok(result.riskScore >= 45);
assert.ok(result.signals.some(signal => signal.code === 'email-brand-paypal'));

const disposable = parseEmailAddress('hello@mailinator.com');
result = assessEmail({ ...disposable, dnsInfo: dns() });
assert.equal(result.status, 'caution');
assert.ok(result.signals.some(signal => signal.code === 'email-disposable'));

const missingDomain = parseEmailAddress('billing@example-invalid-domain.test');
result = assessEmail({
  ...missingDomain,
  dnsInfo: dns({ domainExists: false, hasMx: false, hasSpf: false, hasDmarc: false })
});
assert.ok(result.riskScore >= 25);
assert.ok(result.signals.some(signal => signal.code === 'email-domain-missing'));

assert.throws(() => parseEmailAddress('not-an-email'));
assert.throws(() => parseEmailAddress('two@@example.com'));
assert.throws(() => parseEmailAddress('a@localhost'));

console.log('Email safety unit checks passed');
