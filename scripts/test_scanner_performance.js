const fs = require('node:fs');
const assert = require('node:assert/strict');

const api = fs.readFileSync('api/check.js', 'utf8');
const homepage = fs.readFileSync('dist/index.html', 'utf8');

const redirectLimitMatch = api.match(/const MAX_REDIRECTS = (\d+);/);
assert.ok(redirectLimitMatch, 'redirect limit must be explicit');
const redirectLimit = Number(redirectLimitMatch[1]);
assert.ok(redirectLimit >= 1 && redirectLimit <= 5, 'redirect limit must stay bounded to five or fewer');
assert.match(api, /const TOTAL_TIMEOUT_MS = 7000;/, 'server scan must have a total deadline');
assert.match(api, /const DNS_TIMEOUT_MS = 1500;/, 'DNS lookup must have a deadline');
assert.match(homepage, /AbortController/, 'browser requests must have a deadline');
assert.match(homepage, /analyze\.textContent!==label/, 'button observer must not rewrite unchanged text');
assert.match(homepage, /One complete check\./, 'single complete scan disclosure must remain visible in source');
assert.match(homepage, /id="deep"/, 'deep scan control must remain in the document');
assert.match(homepage, /id="deep-confirm"/, 'deep scan confirmation control must remain in the document');
assert.match(homepage, /deepConfirm\.click\(\)/, 'public-link reputation stage must start after the initial result');
assert.match(homepage, /#deep,#consent\{display:none!important\}/, 'legacy deep-scan controls must stay hidden in single-scan UX');
assert.match(homepage, /cist:result-updated/, 'result panels must update through an explicit event');
assert.match(homepage, /isPublicLink\(v\)/, 'automatic external reputation stage must remain limited to public links');

console.log('Scanner performance and consent checks passed');
