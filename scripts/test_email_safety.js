const assert = require('node:assert');
const {
  assessEmail,
  findBrandLookalike,
  parseEmailAddress,
  analyzeSpfRecord,
  analyzeDmarcRecord,
  registrableDomain
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
    spf: {
      recordCount: 1,
      allQualifier: '-',
      lookupCount: 1,
      potentialLookupOverflow: false,
      usesPtr: false,
      quality: 'strict'
    },
    dmarcKnown: true,
    hasDmarc: true,
    dmarc: {
      recordCount: 1,
      policy: 'reject',
      subdomainPolicy: null,
      pct: 100
    },
    dnssecKnown: true,
    hasDnssec: true,
    mtaStsKnown: true,
    hasMtaSts: true,
    tlsRptKnown: true,
    hasTlsRpt: true,
    ...overrides
  };
}

const paypal = parseEmailAddress('support@paypal.com');
assert.equal(paypal.domain, 'paypal.com');
assert.equal(findBrandLookalike(paypal.domain), null);
let result = assessEmail({ ...paypal, dnsInfo: dns(), rdapInfo: { known: true, ageDays: 5000 } });
assert.equal(result.status, 'low');
assert.equal(result.riskScore, 0);

const fakePaypal = parseEmailAddress('security@paypa1-security.com');
assert.equal(findBrandLookalike(fakePaypal.domain), 'paypal');
result = assessEmail({ ...fakePaypal, dnsInfo: dns(), rdapInfo: { known: true, ageDays: 4 } });
assert.ok(result.riskScore >= 60);
assert.ok(result.signals.some(signal => signal.code === 'email-brand-paypal'));
assert.ok(result.signals.some(signal => signal.code === 'email-domain-age-7'));

const fakeMicrosoft = parseEmailAddress('billing@micros0ft.com');
assert.equal(findBrandLookalike(fakeMicrosoft.domain), 'microsoft');

const disposable = parseEmailAddress('hello@mailinator.com');
result = assessEmail({ ...disposable, dnsInfo: dns(), rdapInfo: { known: false } });
assert.equal(result.status, 'caution');
assert.ok(result.signals.some(signal => signal.code === 'email-disposable'));

const missingDomain = parseEmailAddress('billing@example-invalid-domain.test');
result = assessEmail({
  ...missingDomain,
  dnsInfo: dns({ domainExists: false, hasMx: false, hasSpf: false, hasDmarc: false, spf: {}, dmarc: {} }),
  rdapInfo: { known: false }
});
assert.ok(result.riskScore >= 25);
assert.ok(result.signals.some(signal => signal.code === 'email-domain-missing'));

const permissiveSpf = analyzeSpfRecord(['v=spf1 include:_spf.example.net +all']);
assert.equal(permissiveSpf.quality, 'permissive');
assert.equal(permissiveSpf.allQualifier, '+');
assert.equal(permissiveSpf.lookupCount, 1);

const overloadedSpf = analyzeSpfRecord([
  'v=spf1 include:a.example include:b.example include:c.example include:d.example include:e.example include:f.example include:g.example include:h.example include:i.example include:j.example include:k.example -all'
]);
assert.equal(overloadedSpf.potentialLookupOverflow, true);

const dmarcReject = analyzeDmarcRecord(['v=DMARC1; p=reject; sp=quarantine; pct=100']);
assert.equal(dmarcReject.policy, 'reject');
assert.equal(dmarcReject.subdomainPolicy, 'quarantine');
assert.equal(dmarcReject.pct, 100);

const dmarcMonitor = analyzeDmarcRecord(['v=DMARC1; p=none; pct=25']);
assert.equal(dmarcMonitor.policy, 'none');
assert.equal(dmarcMonitor.pct, 25);
result = assessEmail({
  ...parseEmailAddress('hello@example.com'),
  dnsInfo: dns({ dmarc: dmarcMonitor }),
  rdapInfo: { known: true, ageDays: 3000 }
});
assert.ok(result.signals.some(signal => signal.code === 'email-dmarc-monitoring'));
assert.ok(result.signals.some(signal => signal.code === 'email-dmarc-partial'));

assert.equal(registrableDomain('mail.example.co.uk'), 'example.co.uk');
assert.equal(registrableDomain('sub.example.com'), 'example.com');

assert.throws(() => parseEmailAddress('not-an-email'));
assert.throws(() => parseEmailAddress('two@@example.com'));
assert.throws(() => parseEmailAddress('a@localhost'));

console.log('Email safety v1.1 unit checks passed');
