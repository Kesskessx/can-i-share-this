'use strict';

const COUNTRY_CODES = [
  ['1','US/Canada'],['7','Russia/Kazakhstan'],['20','Egypt'],['27','South Africa'],['30','Greece'],['31','Netherlands'],['32','Belgium'],['33','France'],['34','Spain'],['36','Hungary'],['39','Italy'],['40','Romania'],['41','Switzerland'],['43','Austria'],['44','United Kingdom'],['45','Denmark'],['46','Sweden'],['47','Norway'],['48','Poland'],['49','Germany'],['51','Peru'],['52','Mexico'],['53','Cuba'],['54','Argentina'],['55','Brazil'],['56','Chile'],['57','Colombia'],['58','Venezuela'],['60','Malaysia'],['61','Australia'],['62','Indonesia'],['63','Philippines'],['64','New Zealand'],['65','Singapore'],['66','Thailand'],['81','Japan'],['82','South Korea'],['84','Vietnam'],['86','China'],['90','Turkey'],['91','India'],['92','Pakistan'],['93','Afghanistan'],['94','Sri Lanka'],['95','Myanmar'],['98','Iran'],['211','South Sudan'],['212','Morocco'],['213','Algeria'],['216','Tunisia'],['218','Libya'],['220','Gambia'],['221','Senegal'],['222','Mauritania'],['223','Mali'],['224','Guinea'],['225','Ivory Coast'],['226','Burkina Faso'],['227','Niger'],['228','Togo'],['229','Benin'],['230','Mauritius'],['231','Liberia'],['232','Sierra Leone'],['233','Ghana'],['234','Nigeria'],['235','Chad'],['236','Central African Republic'],['237','Cameroon'],['238','Cape Verde'],['239','Sao Tome and Principe'],['240','Equatorial Guinea'],['241','Gabon'],['242','Congo'],['243','DR Congo'],['244','Angola'],['245','Guinea-Bissau'],['248','Seychelles'],['249','Sudan'],['250','Rwanda'],['251','Ethiopia'],['252','Somalia'],['253','Djibouti'],['254','Kenya'],['255','Tanzania'],['256','Uganda'],['260','Zambia'],['263','Zimbabwe'],['351','Portugal'],['352','Luxembourg'],['353','Ireland'],['354','Iceland'],['355','Albania'],['356','Malta'],['357','Cyprus'],['358','Finland'],['359','Bulgaria'],['370','Lithuania'],['371','Latvia'],['372','Estonia'],['373','Moldova'],['374','Armenia'],['375','Belarus'],['376','Andorra'],['377','Monaco'],['378','San Marino'],['380','Ukraine'],['381','Serbia'],['382','Montenegro'],['383','Kosovo'],['385','Croatia'],['386','Slovenia'],['387','Bosnia and Herzegovina'],['389','North Macedonia'],['420','Czech Republic'],['421','Slovakia'],['423','Liechtenstein'],['880','Bangladesh'],['886','Taiwan'],['960','Maldives'],['961','Lebanon'],['962','Jordan'],['963','Syria'],['964','Iraq'],['965','Kuwait'],['966','Saudi Arabia'],['967','Yemen'],['968','Oman'],['970','Palestine'],['971','United Arab Emirates'],['972','Israel'],['973','Bahrain'],['974','Qatar'],['975','Bhutan'],['976','Mongolia'],['977','Nepal']
].sort((a,b)=>b[0].length-a[0].length);

const GEO_TERMS = {
  France: ['france','french','français','francaise','française','paris','lyon','marseille'],
  'United Kingdom': ['united kingdom','uk','britain','british','london'],
  Germany: ['germany','german','deutschland'],
  Spain: ['spain','spanish','españa'],
  Italy: ['italy','italian','italia'],
  Nigeria: ['nigeria','nigerian'],
  India: ['india','indian'],
  'United States': ['united states','usa','u.s.','american'],
  Canada: ['canada','canadian'],
  Australia: ['australia','australian'],
  Switzerland: ['switzerland','swiss'],
  Belgium: ['belgium','belgian'],
  Netherlands: ['netherlands','dutch'],
  Portugal: ['portugal','portuguese'],
  Morocco: ['morocco','moroccan','maroc']
};

function clean(value, max = 5000) {
  return String(value == null ? '' : value).replace(/\0/g,'').replace(/\s+/g,' ').trim().slice(0,max);
}

function normalizeDigits(value) {
  const raw = clean(value,120);
  const plus = raw.trim().startsWith('+');
  const digits = raw.replace(/\D/g,'');
  if (!digits) return { raw, international: false, digits: '', e164: null };
  if (plus) return { raw, international: true, digits, e164: `+${digits}` };
  if (digits.startsWith('00') && digits.length > 4) return { raw, international: true, digits: digits.slice(2), e164: `+${digits.slice(2)}` };
  return { raw, international: false, digits, e164: null };
}

function countryForDigits(digits) {
  for (const [code,country] of COUNTRY_CODES) if (String(digits||'').startsWith(code)) return { countryCode:`+${code}`, country };
  return { countryCode:null, country:null };
}

function claimedGeographies(context) {
  const low = ` ${clean(context,12000).toLowerCase()} `;
  const out=[];
  for (const [country,terms] of Object.entries(GEO_TERMS)) {
    if (terms.some(term => low.includes(` ${term.toLowerCase()} `) || low.includes(term.toLowerCase()))) out.push(country);
  }
  return out.slice(0,5);
}

function countryCompatible(detected, claimed) {
  if (!detected || !claimed) return true;
  if (detected === claimed) return true;
  if (detected === 'US/Canada' && (claimed === 'United States' || claimed === 'Canada')) return true;
  return false;
}

function analyzePhone(value, context='') {
  const n = normalizeDigits(value);
  const signals=[];
  let status='unknown';
  let countryCode=null,country=null;
  if (n.international && n.digits.length >= 7 && n.digits.length <= 15) {
    ({countryCode,country}=countryForDigits(n.digits));
    status='low';
  } else if (n.digits.length >= 7 && n.digits.length <= 15) {
    status='unknown';
    signals.push({code:'phone-local-format',severity:'context',title:'Local-format phone number',detail:'The number has no international country code, so its country cannot be determined reliably.'});
  } else {
    status='caution';
    signals.push({code:'phone-format-unusual',severity:'low',title:'Unusual phone-number format',detail:'The value does not look like a standard public phone number.'});
  }

  const claims=claimedGeographies(context);
  const mismatches=country ? claims.filter(x=>!countryCompatible(country,x)) : [];
  if (country && claims.length && mismatches.length === claims.length) {
    status='caution';
    signals.push({code:'phone-geography-mismatch',severity:'medium',title:'Phone country does not match the claimed geography',detail:`The number appears to use ${countryCode} (${country}), while the surrounding content refers to ${claims.join(', ')}. This is context, not proof of fraud.`});
  }
  const low=clean(context,12000).toLowerCase();
  const movesOffPlatform=/\b(whatsapp|telegram|signal)\b/.test(low);
  if (movesOffPlatform && status==='caution') {
    signals.push({code:'phone-off-platform-context',severity:'context',title:'Off-platform contact request',detail:'The surrounding content also asks to continue through a private messaging service. Combined with other inconsistencies, this deserves verification.'});
  }

  return {
    inputType:'phone',
    phone:{
      normalized:n.e164,
      international:n.international,
      countryCode,
      country,
      numberType:'not-verified',
      ownershipVerified:false,
      claimedGeographies:claims
    },
    safety:{
      status,
      riskScore:status==='caution'?35:status==='low'?8:0,
      verdict:status==='caution'?'Phone context needs verification':status==='low'?'Phone format is plausible':'Phone country could not be established',
      signals,
      checksPerformed:['Phone-number structure','International country-code context','Claimed-geography consistency'],
      disclaimer:'This does not identify or verify the owner of the phone number. Country-code information is contextual and can be spoofed or used while roaming.'
    }
  };
}

module.exports={analyzePhone,normalizeDigits,countryForDigits,claimedGeographies};
