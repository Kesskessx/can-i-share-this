'use strict';

const crypto = require('node:crypto');

const MAX_FILE_BYTES = 3 * 1024 * 1024;
const EXECUTABLE_EXTS = new Set(['exe','msi','msix','scr','bat','cmd','com','ps1','vbs','jar','apk','dmg','pkg','iso','img','hta','appinstaller','elf']);
const ARCHIVE_EXTS = new Set(['zip','rar','7z','gz','tgz','bz2','xz']);
const OFFICE_EXTS = new Set(['doc','docx','docm','xls','xlsx','xlsm','ppt','pptx','pptm']);

function clean(v, max = 1000) { return String(v == null ? '' : v).replace(/\0/g, '').trim().slice(0, max); }
function extOf(name) { const m = clean(name, 300).toLowerCase().match(/\.([a-z0-9]{1,12})$/); return m ? m[1] : ''; }
function decodeFileData(value) {
  const raw = String(value || '');
  const comma = raw.indexOf(',');
  const b64 = raw.startsWith('data:') && comma >= 0 ? raw.slice(comma + 1) : raw;
  if (!/^[A-Za-z0-9+/=\r\n]+$/.test(b64)) throw new Error('Invalid file encoding.');
  const buf = Buffer.from(b64, 'base64');
  if (!buf.length || buf.length > MAX_FILE_BYTES) throw new Error('File must be between 1 byte and 3 MB.');
  return buf;
}

function sniffMime(buf) {
  const h = buf.subarray(0, 16);
  const ascii = h.toString('latin1');
  if (h[0] === 0x25 && h[1] === 0x50 && h[2] === 0x44 && h[3] === 0x46) return 'application/pdf';
  if (h[0] === 0x50 && h[1] === 0x4b && [0x03,0x05,0x07].includes(h[2]) && [0x04,0x06,0x08].includes(h[3])) return 'application/zip';
  if (h[0] === 0x4d && h[1] === 0x5a) return 'application/x-dosexec';
  if (h[0] === 0x7f && ascii.slice(1,4) === 'ELF') return 'application/x-elf';
  if (h[0] === 0x89 && ascii.slice(1,4) === 'PNG') return 'image/png';
  if (h[0] === 0xff && h[1] === 0xd8 && h[2] === 0xff) return 'image/jpeg';
  if (ascii.slice(0,6) === 'GIF87a' || ascii.slice(0,6) === 'GIF89a') return 'image/gif';
  if (ascii.slice(0,4) === 'Rar!') return 'application/vnd.rar';
  if (h[0] === 0x37 && h[1] === 0x7a && h[2] === 0xbc && h[3] === 0xaf) return 'application/x-7z-compressed';
  if (h[0] === 0x1f && h[1] === 0x8b) return 'application/gzip';
  const text = buf.subarray(0, Math.min(buf.length, 4096)).toString('utf8');
  if (/^(From|Return-Path|Received|Subject|Message-ID|MIME-Version):/mi.test(text)) return 'message/rfc822';
  if (/^[\x09\x0A\x0D\x20-\x7E\u0080-\uFFFF]*$/.test(text)) return 'text/plain';
  return 'application/octet-stream';
}

function extractUrls(text) { return [...new Set((String(text || '').match(/https?:\/\/[^\s<>"']+/gi) || []).map(x => x.replace(/[),.;!?]+$/,'')))].slice(0,12); }
function extractEmails(text) { return [...new Set((String(text || '').match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,24}/gi) || []).map(x => x.toLowerCase()))].slice(0,12); }

function parseHeaders(raw) {
  const normalized = String(raw || '').replace(/\r\n/g,'\n');
  const split = normalized.split(/\n\n/, 2);
  const head = split[0] || '';
  const unfolded = head.replace(/\n[ \t]+/g, ' ');
  const headers = {};
  for (const line of unfolded.split('\n')) {
    const i = line.indexOf(':'); if (i <= 0) continue;
    const key = line.slice(0,i).trim().toLowerCase();
    const value = line.slice(i+1).trim();
    if (!headers[key]) headers[key] = [];
    headers[key].push(value);
  }
  return { headers, body: normalized.slice(head.length + (normalized.slice(head.length).startsWith('\n\n') ? 2 : 0)) };
}

function addressDomain(value) {
  const m = String(value || '').match(/<?[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,24})>?/i);
  return m ? m[1].toLowerCase() : null;
}

function parseAuthResults(headers) {
  const auth = [...(headers['authentication-results'] || []), ...(headers['arc-authentication-results'] || [])].join(' ').toLowerCase();
  const pick = name => {
    const m = auth.match(new RegExp('\\b'+name+'\\s*=\\s*(pass|fail|softfail|neutral|none|temperror|permerror)','i'));
    return m ? m[1].toLowerCase() : null;
  };
  return { spf: pick('spf'), dkim: pick('dkim'), dmarc: pick('dmarc') };
}

function analyzeEml(text) {
  const { headers, body } = parseHeaders(text);
  const from = (headers.from || [])[0] || '';
  const replyTo = (headers['reply-to'] || [])[0] || '';
  const returnPath = (headers['return-path'] || [])[0] || '';
  const fromDomain = addressDomain(from), replyDomain = addressDomain(replyTo), returnDomain = addressDomain(returnPath);
  const auth = parseAuthResults(headers);
  const urls = extractUrls(body);
  const emails = extractEmails(body);
  const warnings = [];
  if (replyDomain && fromDomain && replyDomain !== fromDomain) warnings.push({ code:'reply-to-mismatch', severity:'medium', title:'Reply-To domain differs from From', detail:`The visible sender uses ${fromDomain}, but replies go to ${replyDomain}.` });
  if (returnDomain && fromDomain && returnDomain !== fromDomain) warnings.push({ code:'return-path-mismatch', severity:'low', title:'Return-Path differs from From', detail:`The envelope return domain is ${returnDomain}, while the visible From domain is ${fromDomain}. This can be legitimate for mail providers, so treat it as context.` });
  for (const [k,v] of Object.entries(auth)) if (v === 'fail' || v === 'permerror') warnings.push({ code:`${k}-fail`, severity:k === 'dmarc' ? 'high' : 'medium', title:`${k.toUpperCase()} authentication did not pass`, detail:`Authentication-Results reports ${k}=${v}.` });
  return {
    from: clean(from,320), replyTo: clean(replyTo,320), returnPath: clean(returnPath,320),
    fromDomain, replyDomain, returnDomain,
    subject: clean((headers.subject || [])[0],500),
    messageId: clean((headers['message-id'] || [])[0],320),
    receivedCount: (headers.received || []).length,
    authentication: auth,
    urls, emails,
    warnings,
    headersPresent: Object.keys(headers).slice(0,30)
  };
}

async function hashReputation(sha256) {
  const key = String(process.env.VIRUSTOTAL_API_KEY || '').trim();
  if (!key) return { provider:'VirusTotal', checked:false, status:'not-configured', lookup:'sha256-only' };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3500);
  try {
    const r = await fetch(`https://www.virustotal.com/api/v3/files/${encodeURIComponent(sha256)}`, { headers:{'x-apikey':key,'accept':'application/json'}, signal:controller.signal });
    if (r.status === 404) return { provider:'VirusTotal', checked:true, status:'not-found', malicious:0, suspicious:0, lookup:'sha256-only' };
    if (!r.ok) return { provider:'VirusTotal', checked:false, status:'unavailable', httpStatus:r.status, lookup:'sha256-only' };
    const j = await r.json();
    const stats = j && j.data && j.data.attributes && j.data.attributes.last_analysis_stats || {};
    const malicious = Number(stats.malicious || 0), suspicious = Number(stats.suspicious || 0);
    return { provider:'VirusTotal', checked:true, status: malicious > 0 ? 'known-malicious' : suspicious > 0 ? 'suspicious' : 'no-malicious-engine-match', malicious, suspicious, harmless:Number(stats.harmless||0), lookup:'sha256-only' };
  } catch (_) { return { provider:'VirusTotal', checked:false, status:'unavailable', lookup:'sha256-only' }; }
  finally { clearTimeout(timer); }
}

async function analyzeFile(file) {
  const name = clean(file && file.name, 300) || 'uploaded-file';
  const declaredMime = clean(file && file.mime, 160).toLowerCase() || null;
  const buf = decodeFileData(file && file.data);
  const sha256 = crypto.createHash('sha256').update(buf).digest('hex');
  const detectedMime = sniffMime(buf);
  const ext = extOf(name);
  const lower = name.toLowerCase();
  const sample = buf.subarray(0, Math.min(buf.length, 900000)).toString('latin1');
  const textSample = buf.subarray(0, Math.min(buf.length, 900000)).toString('utf8');
  const signals = [];
  const add = (code,severity,title,detail) => signals.push({code,severity,title,detail});
  const doubleExt = /\.(pdf|docx?|xlsx?|pptx?|jpg|jpeg|png|txt)\.(exe|scr|bat|cmd|com|msi|ps1|vbs|jar|apk)$/i.test(lower);
  if (doubleExt) add('double-extension','high','Misleading double extension','The filename appears to disguise an executable or script behind a familiar document/image extension.');
  if (EXECUTABLE_EXTS.has(ext) || ['application/x-dosexec','application/x-elf'].includes(detectedMime)) add('executable-file','high','Executable or installable file','Unexpected executable files can run code on the device.');
  if (ARCHIVE_EXTS.has(ext) || /application\/(zip|x-7z-compressed|vnd\.rar)/.test(detectedMime)) add('archive-file','medium','Archive file','Archives can conceal scripts or executables; inspect their contents before opening.');
  const claimedDoc = /^(application\/pdf|application\/vnd\.|text\/)/.test(declaredMime || '') || /\.(pdf|docx?|xlsx?|pptx?)$/i.test(lower);
  if (claimedDoc && ['application/x-dosexec','application/x-elf'].includes(detectedMime)) add('mime-mismatch','high','File type does not match its name','The file appears executable even though its name/type suggests a document.');
  if (/vbaProject\.bin/i.test(sample) || /AutoOpen|Document_Open|Workbook_Open/i.test(sample)) add('office-macro','high','Office macro indicators detected','The file contains strings associated with Office macros or automatic macro execution.');
  if (detectedMime === 'application/pdf' && /\/JavaScript|\/JS\b|\/OpenAction|\/Launch\b/i.test(sample)) add('pdf-active-content','high','Active PDF content detected','The PDF contains markers for JavaScript, launch actions or automatic actions.');
  if (/powershell|cmd\.exe|wscript|cscript|mshta|rundll32/i.test(sample)) add('script-launcher-strings','high','Command execution strings detected','The file contains references to common command/script launchers.');

  const urls = extractUrls(textSample);
  const emails = extractEmails(textSample);
  const isEml = ext === 'eml' || declaredMime === 'message/rfc822' || detectedMime === 'message/rfc822';
  const eml = isEml ? analyzeEml(buf.toString('utf8')) : null;
  if (eml) signals.push(...eml.warnings);
  const reputation = await hashReputation(sha256);
  if (reputation.checked && reputation.malicious > 0) add('hash-known-malicious','high','File hash reported maliciously','An external reputation source reports malicious detections for this exact SHA-256 hash.');

  const rank = {low:1,medium:2,high:3};
  const strongest = signals.reduce((m,s)=>Math.max(m,rank[s.severity]||0),0);
  const risk = strongest >= 3 ? 'high' : strongest === 2 ? 'caution' : 'low';
  return {
    inputType:'file',
    file:{ name, size:buf.length, declaredMime, detectedMime, extension:ext || null, sha256, hashLookupOnly:true },
    eml,
    extracted:{ urls:[...new Set([...(eml&&eml.urls||[]),...urls])].slice(0,12), emails:[...new Set([...(eml&&eml.emails||[]),...emails])].slice(0,12) },
    reputation,
    safety:{ status:risk, riskScore:risk==='high'?85:risk==='caution'?48:12, signals, checksPerformed:['SHA-256','Magic-byte MIME detection','Extension/type consistency','Executable/archive indicators','Office/PDF active-content markers',...(eml?['Email header authentication relationships']:[]),...(reputation.checked?['Hash reputation']:['Hash reputation available when configured'])] },
    summary:risk==='high'?'High-risk file indicators were detected.':risk==='caution'?'The file contains indicators that deserve verification.':'No major warning was found in the lightweight static file checks.',
    recommendedAction:risk==='high'?'Do not open or execute this file until it is independently verified.':'Open only if you expected the file and trust its source.'
  };
}

module.exports = { analyzeFile, analyzeEml, sniffMime, MAX_FILE_BYTES };
