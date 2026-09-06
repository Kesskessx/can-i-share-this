'use strict';

const crypto=require('node:crypto');
const zlib=require('node:zlib');

const MAX_BYTES=3*1024*1024;
const MAX_ARCHIVE_ENTRIES=180;
const MAX_ENTRY_OUTPUT=384*1024;
const MAX_TOTAL_OUTPUT=1600*1024;
const DANGEROUS_EXT=new Set(['exe','msi','msix','scr','bat','cmd','com','ps1','vbs','vbe','js','jse','wsf','wsh','hta','jar','apk','dmg','pkg','iso','img','appinstaller','lnk']);
const DOC_EXT=new Set(['pdf','doc','docx','xls','xlsx','ppt','pptx','txt','csv','rtf','jpg','jpeg','png','webp']);
const ARCHIVE_EXT=new Set(['zip','rar','7z','gz','tgz']);

function clean(v,max=1000){return String(v==null?'':v).replace(/\0/g,'').replace(/\r/g,'').trim().slice(0,max)}
function unique(items,max=30){const out=[],seen=new Set();for(const x of items||[]){const v=clean(x,1000),k=v.toLowerCase();if(!v||seen.has(k))continue;seen.add(k);out.push(v);if(out.length>=max)break}return out}
function extension(name){const m=clean(name,260).toLowerCase().match(/\.([a-z0-9]{1,16})$/);return m?m[1]:''}
function allExtensions(name){return (clean(name,260).toLowerCase().match(/\.([a-z0-9]{1,16})/g)||[]).map(x=>x.slice(1))}
function hasDoubleExtension(name){const xs=allExtensions(name);if(xs.length<2)return false;const last=xs[xs.length-1];return DANGEROUS_EXT.has(last)&&xs.slice(0,-1).some(x=>DOC_EXT.has(x)||ARCHIVE_EXT.has(x))}
function safeBase64(value){try{const b=Buffer.from(String(value||''),'base64');return b.length?b:null}catch(_){return null}}
function parseFilePayload(file){
  if(!file||typeof file!=='object')throw new Error('File payload required.');
  const name=clean(file.name||'upload.bin',260).replace(/[\\/]/g,'_');
  const declaredMime=clean(file.mimeType||file.type||'application/octet-stream',180).toLowerCase();
  let data=file.dataBase64||file.data||'';
  const m=String(data).match(/^data:([^;,]+);base64,([A-Za-z0-9+/=\s]+)$/i);
  if(m){data=m[2]}
  const bytes=safeBase64(String(data).replace(/\s+/g,''));
  if(!bytes)throw new Error('File data is missing or invalid.');
  if(bytes.length>MAX_BYTES)throw new Error('File too large. Maximum size: 3 MB.');
  return {name,declaredMime,bytes};
}
function sniffMime(bytes){
  if(bytes.slice(0,5).toString('ascii')==='%PDF-')return'application/pdf';
  if(bytes.length>=4&&bytes.readUInt32LE(0)===0x04034b50)return'application/zip';
  if(bytes.slice(0,2).toString('ascii')==='MZ')return'application/x-msdownload';
  if(bytes.slice(0,4).equals(Buffer.from([0x7f,0x45,0x4c,0x46])))return'application/x-elf';
  if(bytes.slice(0,6).toString('binary')==='Rar!\x1a\x07')return'application/vnd.rar';
  if(bytes.slice(0,6).equals(Buffer.from([0x37,0x7a,0xbc,0xaf,0x27,0x1c])))return'application/x-7z-compressed';
  if(bytes[0]===0x1f&&bytes[1]===0x8b)return'application/gzip';
  if(bytes.slice(0,8).equals(Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a])))return'image/png';
  if(bytes[0]===0xff&&bytes[1]===0xd8&&bytes[2]===0xff)return'image/jpeg';
  if(bytes.slice(0,4).toString('ascii')==='RIFF'&&bytes.slice(8,12).toString('ascii')==='WEBP')return'image/webp';
  const head=bytes.slice(0,8192).toString('utf8');
  if(/^From:|^Return-Path:|^Received:/mi.test(head)&&/^Subject:|^Date:/mi.test(head))return'message/rfc822';
  if(/^#!\s*\/(?:usr\/bin|bin)\//.test(head))return'text/x-script';
  if(/^[\x09\x0a\x0d\x20-\x7e\u00a0-\uffff]+$/.test(head))return'text/plain';
  return'application/octet-stream';
}
function mimeMatchesExtension(ext,mime){
  const map={pdf:['application/pdf'],zip:['application/zip'],docx:['application/zip'],xlsx:['application/zip'],pptx:['application/zip'],exe:['application/x-msdownload'],eml:['message/rfc822'],png:['image/png'],jpg:['image/jpeg'],jpeg:['image/jpeg'],webp:['image/webp']};
  return !map[ext]||map[ext].includes(mime);
}
function extractUrls(text){return unique((String(text||'').match(/https?:\/\/[^\s<>"'\]\)]+/gi)||[]).map(x=>x.replace(/[.,;!?]+$/,'')),30)}
function extractEmails(text){return unique((String(text||'').match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,24}/gi)||[]),20)}
function parseHeaders(raw){
  const split=String(raw||'').split(/\r?\n\r?\n/,1)[0]||'';
  const unfolded=split.replace(/\r?\n[ \t]+/g,' ');
  const out={};
  for(const line of unfolded.split(/\r?\n/)){const i=line.indexOf(':');if(i<=0)continue;const k=line.slice(0,i).trim().toLowerCase(),v=line.slice(i+1).trim();if(!out[k])out[k]=[];out[k].push(v)}
  return out;
}
function emailDomain(value){const m=clean(value,600).match(/@([A-Z0-9.-]+\.[A-Z]{2,24})/i);return m?m[1].toLowerCase():null}
function authResult(headers,name){const raw=(headers['authentication-results']||[]).join(' ').toLowerCase();const m=raw.match(new RegExp('(?:^|[;\\s])'+name+'=([a-z]+)','i'));return m?m[1]:null}
function attachmentNames(raw){
  const out=[];const re=/(?:filename|name)\*?\s*=\s*(?:UTF-8''|"?)([^";\r\n]+)/gi;let m;
  while((m=re.exec(String(raw||'')))&&out.length<20){let v=m[1].trim().replace(/^"|"$/g,'');try{v=decodeURIComponent(v)}catch(_){}out.push(v)}return unique(out,20)
}
function analyzeEml(bytes,name){
  const raw=bytes.toString('utf8');const headers=parseHeaders(raw);
  const first=k=>(headers[k]&&headers[k][0])||null;
  const from=first('from'),replyTo=first('reply-to'),returnPath=first('return-path'),messageId=first('message-id');
  const fromDomain=emailDomain(from),replyDomain=emailDomain(replyTo),returnDomain=emailDomain(returnPath);
  const spf=authResult(headers,'spf'),dkim=authResult(headers,'dkim'),dmarc=authResult(headers,'dmarc');
  const signals=[];
  if(fromDomain&&replyDomain&&fromDomain!==replyDomain)signals.push({code:'eml-replyto-mismatch',severity:'medium',title:'Reply-To domain differs from From',detail:`The visible sender uses ${fromDomain}, while replies are directed to ${replyDomain}. This can be legitimate but should be verified.`});
  if(fromDomain&&returnDomain&&fromDomain!==returnDomain)signals.push({code:'eml-returnpath-mismatch',severity:'context',title:'Return-Path differs from From',detail:`The envelope return domain is ${returnDomain}, different from the visible From domain ${fromDomain}. Forwarding and mailing services can cause this.`});
  if(dmarc==='fail')signals.push({code:'eml-dmarc-fail',severity:'high',title:'DMARC authentication failed',detail:'The received-message Authentication-Results header reports DMARC=fail.'});
  if(spf==='fail'||spf==='softfail')signals.push({code:'eml-spf-fail',severity:'medium',title:'SPF did not pass',detail:`Authentication-Results reports SPF=${spf}.`});
  if(dkim==='fail')signals.push({code:'eml-dkim-fail',severity:'medium',title:'DKIM authentication failed',detail:'Authentication-Results reports DKIM=fail.'});
  const attachments=attachmentNames(raw);
  for(const a of attachments){const ext=extension(a);if(DANGEROUS_EXT.has(ext)||hasDoubleExtension(a))signals.push({code:'eml-risky-attachment',severity:'high',title:'Risky attachment name',detail:`The email references an attachment named ${clean(a,120)}.`})}
  const urls=extractUrls(raw),emails=extractEmails(raw);
  const received=(headers.received||[]).length;
  return {emailMessage:{from,replyTo,returnPath,messageId,fromDomain,replyToDomain:replyDomain,returnPathDomain:returnDomain,authentication:{spf,dkim,dmarc},receivedHops:received,attachments},urls,emails,signals};
}
function zipEntries(bytes){
  const entries=[];let pos=0,totalOut=0;
  while(pos+46<=bytes.length&&entries.length<MAX_ARCHIVE_ENTRIES){
    const sig=bytes.readUInt32LE(pos);
    if(sig!==0x02014b50){pos++;continue}
    const flags=bytes.readUInt16LE(pos+8),method=bytes.readUInt16LE(pos+10),compSize=bytes.readUInt32LE(pos+20),uncompSize=bytes.readUInt32LE(pos+24),nameLen=bytes.readUInt16LE(pos+28),extraLen=bytes.readUInt16LE(pos+30),commentLen=bytes.readUInt16LE(pos+32),localOffset=bytes.readUInt32LE(pos+42);
    if(pos+46+nameLen+extraLen+commentLen>bytes.length)break;
    const name=bytes.slice(pos+46,pos+46+nameLen).toString('utf8').replace(/\0/g,'').slice(0,260);
    let text='';
    if(!(flags&1)&&uncompSize<=MAX_ENTRY_OUTPUT&&totalOut<MAX_TOTAL_OUTPUT&&localOffset+30<=bytes.length&&bytes.readUInt32LE(localOffset)===0x04034b50){
      const ln=bytes.readUInt16LE(localOffset+26),le=bytes.readUInt16LE(localOffset+28),start=localOffset+30+ln+le,end=start+compSize;
      if(end<=bytes.length){try{let out=null;if(method===0)out=bytes.slice(start,end);else if(method===8)out=zlib.inflateRawSync(bytes.slice(start,end),{maxOutputLength:MAX_ENTRY_OUTPUT});if(out){totalOut+=out.length;text=out.toString('utf8').slice(0,MAX_ENTRY_OUTPUT)}}catch(_){}}
    }
    entries.push({name,method,compressedSize:compSize,uncompressedSize:uncompSize,text});
    pos+=46+nameLen+extraLen+commentLen;
  }
  return entries;
}
function analyzeZip(bytes){
  const entries=zipEntries(bytes);const names=entries.map(x=>x.name),signals=[];let urls=[],emails=[];
  const lower=names.map(x=>x.toLowerCase());
  if(lower.some(x=>x.endsWith('vbaproject.bin')))signals.push({code:'office-macros',severity:'high',title:'Office macros detected',detail:'The Office archive contains vbaProject.bin. Macros can be legitimate, but unexpected macro-enabled documents should not be trusted.'});
  if(lower.some(x=>x.includes('/externallinks/')))signals.push({code:'office-external-links',severity:'medium',title:'Office external links detected',detail:'The document contains external-link components.'});
  if(lower.some(x=>x.includes('/embeddings/')))signals.push({code:'office-embedded-object',severity:'medium',title:'Embedded Office object detected',detail:'The document contains an embedded object.'});
  const risky=names.filter(x=>DANGEROUS_EXT.has(extension(x))||hasDoubleExtension(x)).slice(0,6);
  if(risky.length)signals.push({code:'archive-risky-file',severity:'high',title:'Archive contains executable or script-like files',detail:`Examples: ${risky.join(', ')}`});
  for(const e of entries){if(!e.text)continue;urls=urls.concat(extractUrls(e.text));emails=emails.concat(extractEmails(e.text));if(/TargetMode=["']External["']/i.test(e.text))signals.push({code:'office-external-target',severity:'medium',title:'External relationship detected',detail:`${e.name} contains an external relationship target.`})}
  return {entries:names.slice(0,80),urls:unique(urls,30),emails:unique(emails,20),signals:uniqueSignals(signals)};
}
function uniqueSignals(items){const out=[],seen=new Set();for(const x of items||[]){const k=`${x.code}:${x.detail}`;if(seen.has(k))continue;seen.add(k);out.push(x);if(out.length>=12)break}return out}
function scoreSignals(signals){let score=0;for(const s of signals){score+=s.severity==='high'?38:s.severity==='medium'?18:s.severity==='low'?8:2}return Math.min(100,score)}

function analyzeUploadedFile(payload){
  const {name,declaredMime,bytes}=parseFilePayload(payload);const ext=extension(name),actualMime=sniffMime(bytes),signals=[];
  if(DANGEROUS_EXT.has(ext))signals.push({code:'file-executable-extension',severity:'high',title:'Executable or script-like file extension',detail:`The file name ends in .${ext}. Do not run unexpected software from an untrusted sender.`});
  if(hasDoubleExtension(name))signals.push({code:'file-double-extension',severity:'high',title:'Misleading double extension',detail:`The file name ${name} ends with a dangerous extension after a document/archive-looking extension.`});
  if(!mimeMatchesExtension(ext,actualMime)&&actualMime!=='application/octet-stream'&&actualMime!=='text/plain')signals.push({code:'file-type-mismatch',severity:'high',title:'File extension and real type do not match',detail:`The name suggests .${ext||'unknown'}, while the file signature looks like ${actualMime}.`});
  let urls=[],emails=[],archive=null,emailMessage=null;
  const textSample=bytes.slice(0,Math.min(bytes.length,2*1024*1024)).toString('latin1');
  if(actualMime==='application/pdf'){
    const pdfSignals=[[/\/JavaScript\b|\/JS\b/i,'pdf-javascript','PDF contains JavaScript markers'],[/\/OpenAction\b/i,'pdf-openaction','PDF contains an automatic OpenAction'],[/\/Launch\b/i,'pdf-launch','PDF contains a Launch action'],[/\/EmbeddedFile\b/i,'pdf-embedded-file','PDF contains an embedded-file marker']];
    for(const [re,code,title] of pdfSignals)if(re.test(textSample))signals.push({code,severity:code==='pdf-javascript'||code==='pdf-launch'?'high':'medium',title,detail:'This structural marker can be legitimate in some PDFs, but unexpected active content deserves caution.'});
    urls=extractUrls(textSample);emails=extractEmails(textSample);
  } else if(actualMime==='application/zip'){
    archive=analyzeZip(bytes);signals.push(...archive.signals);urls=archive.urls;emails=archive.emails;
  } else if(actualMime==='message/rfc822'||ext==='eml'){
    const eml=analyzeEml(bytes,name);emailMessage=eml.emailMessage;signals.push(...eml.signals);urls=eml.urls;emails=eml.emails;
  } else if(actualMime==='application/x-msdownload'||actualMime==='application/x-elf'){
    signals.push({code:'file-binary-executable',severity:'high',title:'Executable binary detected',detail:`The file signature indicates ${actualMime}.`});
  } else {
    urls=extractUrls(textSample);emails=extractEmails(textSample);
  }
  const hash=crypto.createHash('sha256').update(bytes).digest('hex');
  const score=scoreSignals(signals),status=score>=60?'high':score>=25?'caution':'low';
  return {
    inputType:'file',
    file:{name,size:bytes.length,declaredMime,actualMime,extension:ext||null,sha256:hash,hashReputationChecked:false,archiveEntries:archive?archive.entries.length:0},
    emailMessage,
    detectedElements:{urls:unique(urls,20),domains:[],emails:unique(emails,15),phones:[],crypto:[],qr:[],files:unique([name,...(emailMessage&&emailMessage.attachments||[])],20),socialProfiles:[],claimedBrands:[]},
    archive:archive?{entries:archive.entries.slice(0,40)}:null,
    safety:{status,riskScore:score,verdict:status==='high'?'High-risk file indicators detected':status==='caution'?'File needs verification':'No major structural warning found',signals:uniqueSignals(signals),checksPerformed:['SHA-256 hash','Magic-byte file type','Extension/type consistency','Double-extension check',...(actualMime==='application/pdf'?['PDF active-content markers']:[]),...(actualMime==='application/zip'?['Archive/Office structure']:[]),...(emailMessage?['Raw email headers and authentication results']:[])],disclaimer:'This is static analysis. The file is not executed. A low-risk result cannot guarantee that a file is harmless.'}
  };
}

module.exports={MAX_BYTES,analyzeUploadedFile,parseFilePayload,sniffMime,analyzeEml,analyzeZip,hasDoubleExtension};
