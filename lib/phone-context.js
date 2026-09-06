'use strict';

const PREFIXES = [
  ['+351','Portugal'],['+234','Nigeria'],['+353','Ireland'],['+352','Luxembourg'],['+358','Finland'],['+386','Slovenia'],['+420','Czechia'],['+421','Slovakia'],
  ['+33','France'],['+44','United Kingdom'],['+49','Germany'],['+34','Spain'],['+39','Italy'],['+32','Belgium'],['+41','Switzerland'],['+31','Netherlands'],
  ['+91','India'],['+81','Japan'],['+82','South Korea'],['+86','China'],['+61','Australia'],['+64','New Zealand'],['+55','Brazil'],['+52','Mexico'],['+27','South Africa'],['+1','United States / Canada']
];

const COUNTRY_WORDS = {
  France:['france','french','paris','lyon','marseille'],
  'United Kingdom':['uk','united kingdom','britain','british','london'],
  Germany:['germany','german','berlin'], Spain:['spain','spanish','madrid'], Italy:['italy','italian','rome'],
  Belgium:['belgium','belgian','brussels'], Switzerland:['switzerland','swiss'], Portugal:['portugal','portuguese'],
  Nigeria:['nigeria','nigerian'], India:['india','indian'], 'United States / Canada':['united states','usa','american','canada','canadian']
};

function normalizePhone(value) {
  let raw = String(value || '').trim();
  const plus = raw.startsWith('+');
  let digits = raw.replace(/\D/g,'');
  if (raw.startsWith('00')) { digits = digits.slice(2); raw = '+' + digits; }
  else raw = (plus ? '+' : '') + digits;
  return { raw:String(value||'').trim(), normalized:raw, digits };
}

function countryFor(phone) {
  const n = phone.normalized;
  if (!n.startsWith('+')) return null;
  const hit = PREFIXES.find(([p]) => n.startsWith(p));
  return hit ? hit[1] : null;
}

function claimedCountries(text) {
  const low = String(text || '').toLowerCase();
  const out = [];
  for (const [country,words] of Object.entries(COUNTRY_WORDS)) if (words.some(w => low.includes(w))) out.push(country);
  return out;
}

function analyzePhone(value, contextText='') {
  const p = normalizePhone(value);
  const country = countryFor(p);
  const claimed = claimedCountries(contextText);
  const signals = [];
  if (p.normalized && !p.normalized.startsWith('+')) signals.push({ code:'phone-no-country-code', severity:'low', title:'Country cannot be confirmed from the number', detail:'The number is written without an international country code.' });
  if (country && claimed.length && !claimed.includes(country) && !(country === 'United States / Canada' && claimed.includes('United States / Canada'))) {
    signals.push({ code:'phone-geography-mismatch', severity:'medium', title:'Phone country does not match the claimed geography', detail:`The number appears to use ${country}'s calling code while the message/profile references ${claimed.slice(0,2).join(' / ')}.` });
  }
  const low = String(contextText || '').toLowerCase();
  if (/whatsapp|telegram/.test(low) && /contact|message|move|continue|reach me|text me/.test(low)) signals.push({ code:'off-platform-contact', severity:'low', title:'Conversation is being moved to another channel', detail:'Moving an unexpected conversation to WhatsApp or Telegram is context worth verifying, especially with money or credential requests.' });
  return {
    input:value,
    normalized:p.normalized || null,
    country,
    lineType:'unknown',
    ownershipVerified:false,
    claimedCountries:claimed,
    signals,
    disclaimer:'Country-code context does not identify the owner or prove that a number is fraudulent.'
  };
}

module.exports = { analyzePhone, normalizePhone };
