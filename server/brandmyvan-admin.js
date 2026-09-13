const fs=require('node:fs');
const path=require('node:path');
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
module.exports=async function(req,res){
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('X-Content-Type-Options','nosniff');
 const action=req.query.operation;
 if(action==='bmv-admin-page'&&req.method==='GET'){
  res.setHeader('Content-Type','text/html; charset=utf-8');
  res.setHeader('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; img-src data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");
  return res.status(200).send(fs.readFileSync(path.join(__dirname,'brandmyvan-admin.html'),'utf8'));
 }
 const url=process.env.SUPABASE_URL,key=process.env.SUPABASE_SECRET_KEY||process.env.SUPABASE_SERVICE_ROLE_KEY;
 if(!url||!key)return res.status(503).json({error:'Service temporairement indisponible.'});
 async function call(route,options={}){
  const headers={apikey:key,'Content-Type':'application/json',...(key.startsWith('sb_secret_')?{}:{Authorization:'Bearer '+key}),...options.headers};
  const response=await fetch(url.replace(/\/$/,'')+route,{...options,headers,signal:AbortSignal.timeout(12000)});
  const data=await response.json().catch(()=>null);return {ok:response.ok,status:response.status,data};
 }
 if(!['GET','POST'].includes(req.method))return res.status(405).json({error:'Méthode non autorisée.'});
 if(req.method==='POST'){
  let origin;try{origin=new URL(req.headers.origin).host;}catch{}
  if(origin!==req.headers.host)return res.status(403).json({error:'Origine refusée.'});
  if(!(req.headers['content-type']||'').startsWith('application/json'))return res.status(415).json({error:'JSON requis.'});
 }
 let body={};try{if(req.method==='POST'){const raw=typeof req.body==='string'?req.body:JSON.stringify(req.body);if(!raw||Buffer.byteLength(raw)>5000)throw Error();body=JSON.parse(raw);}}catch{return res.status(400).json({error:'Requête invalide.'});}
 const cookie=String(req.headers.cookie||'').split(';').map(s=>s.trim()).find(s=>s.startsWith('__Host-bmv_admin='));
 const token=cookie?cookie.slice('__Host-bmv_admin='.length):'';
 async function allowed(user){if(!user?.id||!UUID.test(user.id)||!user.email_confirmed_at)return false;const r=await call('/rest/v1/brandmyvan_admins?user_id=eq.'+user.id+'&select=user_id');return r.ok&&r.data?.length===1;}
 try{
  if(action==='bmv-availability'&&req.method==='GET'){
   const r=await call('/rest/v1/brandmyvan_logo_requests?status=eq.confirmed&select=spot_id,price_eur');
   if(!r.ok)throw Error();return res.status(200).json({confirmed:r.data});
  }
  if(action==='bmv-admin-login'&&req.method==='POST'){
   if(typeof body.email!=='string'||body.email.length>254||typeof body.password!=='string'||body.password.length>1024)return res.status(400).json({error:'Identifiants invalides.'});
   const r=await call('/auth/v1/token?grant_type=password',{method:'POST',body:JSON.stringify({email:body.email,password:body.password})});
   if(!r.ok||!await allowed(r.data?.user))return res.status(401).json({error:'Connexion refusée. Utilisez le compte administrateur activé.'});
   res.setHeader('Set-Cookie','__Host-bmv_admin='+r.data.access_token+'; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age='+Math.min(r.data.expires_in||3600,3600));
   return res.status(200).json({ok:true});
  }
  if(action==='bmv-admin-logout'&&req.method==='POST'){
   res.setHeader('Set-Cookie','__Host-bmv_admin=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0');
   if(token)await call('/auth/v1/logout?scope=local',{method:'POST',headers:{Authorization:'Bearer '+token}});
   return res.status(200).json({ok:true});
  }
  if(!token)return res.status(401).json({error:'Connectez-vous pour accéder aux demandes.'});
  const auth=await call('/auth/v1/user',{headers:{Authorization:'Bearer '+token}});
  if(!auth.ok||!await allowed(auth.data))return res.status(401).json({error:'Session expirée ou accès non autorisé.'});
  if(action==='bmv-admin-list'&&req.method==='GET'){
   const status=['pending_review','confirmed','declined'].includes(req.query.status)?req.query.status:null;
   const offset=Math.max(0,Math.min(100000,parseInt(req.query.offset,10)||0));
   const r=await call('/rest/v1/brandmyvan_logo_requests?select=id,created_at,company,email,spot_id,price_eur,status,revision&order=created_at.desc,id.desc&limit=51&offset='+offset+(status?'&status=eq.'+status:''));
   if(!r.ok)throw Error();return res.status(200).json({rows:r.data.slice(0,50),hasMore:r.data.length>50});
  }
  if(action==='bmv-admin-detail'&&req.method==='GET'&&UUID.test(req.query.id||'')){
   const r=await call('/rest/v1/brandmyvan_logo_requests?select=id,created_at,company,email,spot_id,price_eur,status,revision,duration_months,logo_name,logo_png,artwork_png,placement,reviewed_at&id=eq.'+req.query.id);
   if(!r.ok)throw Error();return r.data.length?res.status(200).json(r.data[0]):res.status(404).json({error:'Demande introuvable.'});
  }
  if(action==='bmv-admin-review'&&req.method==='POST'&&UUID.test(body.id||'')&&Number.isInteger(body.revision)&&['pending_review','confirmed','declined'].includes(body.status)){
   const r=await call('/rest/v1/rpc/review_brandmyvan_request',{method:'POST',body:JSON.stringify({p_id:body.id,p_status:body.status,p_revision:body.revision,p_admin:auth.data.id})});
   if(!r.ok)throw Error();
   if(r.data.error)return res.status(409).json({error:r.data.error==='spot_taken'?'Cet emplacement est déjà confirmé pour une autre marque.':'La demande a changé. Actualisez avant de réessayer.'});
   return res.status(200).json(r.data);
  }
  return res.status(400).json({error:'Action invalide.'});
 }catch{return res.status(503).json({error:'Le service ne répond pas. Réessayez dans un instant.'});}
};
