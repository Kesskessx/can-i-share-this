const assert = require('node:assert/strict');
const handler = require('../api/feedback');

async function request(body, method = 'POST') {
  let code = 200;
  let payload;
  let ended = false;
  const req = { method, body };
  const res = {
    setHeader() {},
    status(value) { code = value; return this; },
    json(value) { payload = value; return this; },
    end() { ended = true; return this; }
  };
  await handler(req, res);
  return { code, payload, ended };
}

(async () => {
  const originalLog = console.log;
  const logs = [];
  console.log = (...args) => logs.push(args.join(' '));
  try {
    assert.equal((await request({ vote: 'yes', input_type: 'link', status: 'low', signal_count: 1 })).code, 204);
    assert.equal((await request({ vote: 'no', reason: 'wrong_verdict', input_type: 'email', status: 'high', signal_count: 99 })).code, 204);
    assert.equal((await request({ vote: 'no', input_type: 'link', status: 'caution' })).code, 400);
    assert.equal((await request({ vote: 'yes', reason: 'wrong_verdict' })).code, 400);
    assert.equal((await request({ vote: 'maybe' })).code, 400);
    assert.equal((await request({}, 'GET')).code, 405);

    const joined = logs.join('\n');
    assert.match(joined, /\[cist-feedback\]/);
    assert.match(joined, /"vote":"yes"/);
    assert.match(joined, /"reason":"wrong_verdict"/);
    assert.match(joined, /"signal_count":6/);

    await request({ vote: 'yes', input_type: 'link', status: 'low', url: 'https://secret.example/token', message: 'private text' });
    const privateCheck = logs.join('\n');
    assert.doesNotMatch(privateCheck, /secret\.example/);
    assert.doesNotMatch(privateCheck, /private text/);
  } finally {
    console.log = originalLog;
  }
  console.log('Anonymous result feedback checks passed');
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
