const crypto = require('crypto');

const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function decodeBase58(value) {
  let num = 0n;
  for (const ch of value) {
    const n = BASE58.indexOf(ch);
    if (n < 0) return null;
    num = num * 58n + BigInt(n);
  }
  let hex = num.toString(16);
  if (hex.length % 2) hex = '0' + hex;
  let body = hex ? Buffer.from(hex, 'hex') : Buffer.alloc(0);
  let zeros = 0;
  while (zeros < value.length && value[zeros] === '1') zeros++;
  if (zeros) body = Buffer.concat([Buffer.alloc(zeros), body]);
  return body;
}

function validBase58Check(value, versions) {
  const decoded = decodeBase58(value);
  if (!decoded || decoded.length < 5) return false;
  const payload = decoded.subarray(0, -4);
  const checksum = decoded.subarray(-4);
  const first = crypto.createHash('sha256').update(payload).digest();
  const second = crypto.createHash('sha256').update(first).digest();
  if (!crypto.timingSafeEqual(checksum, second.subarray(0, 4))) return false;
  return !versions || versions.includes(payload[0]);
}

const BECH32_CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';
function bech32Polymod(values) {
  const gen = [0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3];
  let chk = 1;
  for (const value of values) {
    const top = chk >>> 25;
    chk = ((chk & 0x1ffffff) << 5) ^ value;
    for (let i = 0; i < 5; i++) if ((top >>> i) & 1) chk ^= gen[i];
  }
  return chk >>> 0;
}
function hrpExpand(hrp) {
  const out = [];
  for (const c of hrp) out.push(c.charCodeAt(0) >>> 5);
  out.push(0);
  for (const c of hrp) out.push(c.charCodeAt(0) & 31);
  return out;
}
function validBech32(address, expectedHrp) {
  if (!address || address !== address.toLowerCase()) return false;
  const pos = address.lastIndexOf('1');
  if (pos < 1 || pos + 7 > address.length || address.length > 90) return false;
  const hrp = address.slice(0, pos);
  if (hrp !== expectedHrp) return false;
  const data = [];
  for (const c of address.slice(pos + 1)) {
    const n = BECH32_CHARSET.indexOf(c);
    if (n < 0) return false;
    data.push(n);
  }
  const pm = bech32Polymod(hrpExpand(hrp).concat(data));
  return pm === 1 || pm === 0x2bc830a3;
}

function detectAddress(input) {
  const value = String(input || '').trim();
  if (!value || value.length > 140) return { valid:false, network:'Unknown', type:'Unknown', checksum:false };

  if (/^0x[a-fA-F0-9]{40}$/.test(value)) {
    return { valid:true, network:'Ethereum / EVM', type:'0x address', checksum:false, note:'Hex format is valid. Mixed-case EIP-55 checksum is not evaluated in this lightweight check.' };
  }

  const lower = value.toLowerCase();
  if (lower.startsWith('bc1')) {
    const ok = validBech32(lower, 'bc');
    return { valid:ok, network:'Bitcoin', type:'Bech32 / Bech32m', checksum:true };
  }
  if (/^[13][1-9A-HJ-NP-Za-km-z]{25,34}$/.test(value)) {
    const ok = validBase58Check(value, [0x00,0x05]);
    return { valid:ok, network:'Bitcoin', type:value[0] === '1' ? 'P2PKH' : 'P2SH', checksum:true };
  }

  if (lower.startsWith('ltc1')) {
    const ok = validBech32(lower, 'ltc');
    return { valid:ok, network:'Litecoin', type:'Bech32 / Bech32m', checksum:true };
  }
  if (/^[LM3][1-9A-HJ-NP-Za-km-z]{25,34}$/.test(value)) {
    const ok = validBase58Check(value, [0x30,0x32,0x05]);
    return { valid:ok, network:'Litecoin', type:'Base58Check', checksum:true };
  }

  if (/^[DA9][1-9A-HJ-NP-Za-km-z]{25,34}$/.test(value)) {
    const ok = validBase58Check(value, [0x1e,0x16]);
    if (ok) return { valid:true, network:'Dogecoin', type:'Base58Check', checksum:true };
  }

  if (/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(value)) {
    const ok = validBase58Check(value, [0x41]);
    return { valid:ok, network:'TRON', type:'Base58Check', checksum:true };
  }

  if (/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value)) {
    const decoded = decodeBase58(value);
    if (decoded && decoded.length === 32) return { valid:true, network:'Solana', type:'Base58 public key', checksum:false, note:'The public-key length is valid, but Solana addresses do not include an address checksum.' };
  }

  return { valid:false, network:'Unknown', type:'Unknown', checksum:false };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error:'Method not allowed' });
  const input = req.body && (req.body.input || req.body.address);
  const result = detectAddress(input);
  const signals = result.valid ? [
    { code:'crypto-format-valid', title:'Address format is valid', detail: result.checksum ? 'The address structure and encoded checksum passed.' : 'The address structure matches the detected network.' },
    { code:'crypto-reputation-unchecked', title:'Reputation is not verified', detail:'A valid wallet address can still belong to a scammer. This check does not prove ownership, identity, transaction history, sanctions status, or trustworthiness.' }
  ] : [
    { code:'crypto-format-invalid', title:'Invalid or unsupported crypto address', detail:'The value does not pass the supported address-format checks.' }
  ];
  return res.status(200).json({
    inputType:'crypto',
    crypto:{ address:String(input || '').trim(), network:result.network, addressType:result.type, formatValid:result.valid, checksumValidated:result.checksum, note:result.note || null, reputationChecked:false },
    safety:{ status:result.valid ? 'caution' : 'high', riskScore:result.valid ? 35 : 90, signals },
    verdict:result.valid ? 'VALID ADDRESS FORMAT' : 'INVALID OR UNSUPPORTED ADDRESS'
  });
};
