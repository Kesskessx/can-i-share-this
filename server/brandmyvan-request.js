const {createHash,createHmac}=require('node:crypto');
const {spots,version,model}=require('../brandmyvan/funding-spots.js');
function imagePNG(value){
 if(typeof value!=='string'||value.length>1900000||!/^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/.test(value))throw Error('Use a PNG logo prepared by the editor.');
 const bytes=Buffer.from(value.split(',')[1],'base64');
 if(bytes.length<33||bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||bytes.toString('ascii',12,16)!=='IHDR')throw Error('The image is not a valid PNG.');
 const width=bytes.readUInt32BE(16),height=bytes.readUInt32BE(20);
 if(!width||!height||width>2048||height>2048)throw Error('Image dimensions are too large.');
 return {width,height};
}
function validate(body){
 if(!body||typeof body!=='object'||Array.isArray(body))throw Error('Invalid request.');
 if(body.website_check)throw Error('Invalid request.');
 if(!/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(body.id||''))throw Error('Reload the editor and try again.');
 const spot=spots.find(s=>s.id===body.spotId);if(!spot||body.version!==version)throw Error('This placement has changed. Reload the page.');
 const company=String(body.company||'').trim(),email=String(body.email||'').trim().toLowerCase();
 if(!company||company.length>100||/[\r\n\x00]/.test(company))throw Error('Enter your brand name.');
 if(email.length>254||!/^\S+@[^\s@]+\.[^\s@]+$/.test(email))throw Error('Enter a valid email address.');
 const a=body.adjustment;if(!a||!['scale','x','y'].every(k=>typeof a[k]==='number'&&Number.isFinite(a[k])&&a[k]>=0&&a[k]<=1)||a.scale<.3)throw Error('Invalid logo position.');
 imagePNG(body.logo);const art=imagePNG(body.artwork),aspect=spot.uw*(spot.view==='rear'?model.width:model.length)/(spot.vh*model.height);
 if(art.width!==1024||art.height!==Math.round(1024/aspect))throw Error('Preview dimensions do not match this spot.');
 return {id:body.id,company,email,spot_id:spot.id,price_eur:spot.price,logo_name:String(body.logoName||'logo.png').replace(/[\r\n\x00]/g,'').slice(0,120),logo_png:body.logo,artwork_png:body.artwork,placement:{version,model:'van-realistic.glb',side:spot.view,u:spot.u,v:spot.v,width:spot.uw,height:spot.vh,edge:spot.edge||'rectangle',adjustment:{scale:a.scale,x:a.x,y:a.y}}};
}
module.exports=async function handler(req,res){
 res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json; charset=utf-8');
 const url=process.env.SUPABASE_URL,key=process.env.SUPABASE_SECRET_KEY||process.env.SUPABASE_SERVICE_ROLE_KEY;
 if(req.method==='GET')return res.status(200).json({available:!!(url&&key)});
 if(req.method!=='POST'){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed.'});}
 if(!url||!key)return res.status(503).json({error:'Reservations are temporarily unavailable. Your preview is still available.'});
 if(!(req.headers['content-type']||'').startsWith('application/json'))return res.status(415).json({error:'Send an application/json request.'});
 if(req.headers.origin){try{if(new URL(req.headers.origin).host!==req.headers.host)return res.status(403).json({error:'Send this request from the van editor.'});}catch{return res.status(403).json({error:'Invalid origin.'});}}
 let request;
 try{
  const raw=typeof req.body==='string'?req.body:JSON.stringify(req.body);
  if(!raw||Buffer.byteLength(raw)>3900000)return res.status(413).json({error:'The logo is too large. Use a smaller image.'});
  request=validate(typeof req.body==='string'?JSON.parse(raw):req.body);
 }catch(error){return res.status(400).json({error:error.message||'Invalid request.'});}
 const ip=String(req.headers['x-vercel-forwarded-for']||req.headers['x-forwarded-for']||req.socket?.remoteAddress||'unknown').split(',')[0].trim();
 const client=createHmac('sha256',key).update('brandmyvan:'+ip).digest('hex');
 const hash=createHash('sha256').update(JSON.stringify(request)).digest('hex');
 try{
  const headers={apikey:key,'Content-Type':'application/json'};if(!key.startsWith('sb_secret_'))headers.Authorization=`Bearer ${key}`;
  const response=await fetch(`${url.replace(/\/$/,'')}/rest/v1/rpc/submit_brandmyvan_logo_request`,{method:'POST',headers,body:JSON.stringify({p_request:request,p_client:client,p_hash:hash}),signal:AbortSignal.timeout(15000)});
  const data=await response.json();if(!response.ok){if(String(data.message||'').includes('spot_taken'))return res.status(409).json({error:'This spot has just been confirmed. Please choose another spot.'});throw Error('Storage unavailable');}
  if(data.error==='rate_limit')return res.status(429).json({error:'Too many requests. Please try again later.'});
  if(data.error==='id_conflict')return res.status(409).json({error:'The request changed. Reload the page before sending a new request.'});
  if(!data.id)throw Error('Storage unavailable');
  return res.status(201).json({id:data.id,status:'pending_review'});
 }catch{return res.status(503).json({error:'The request could not be saved. Your logo is still here; please retry.'});}
};
module.exports.validate=validate;
