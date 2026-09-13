const $=id=>document.getElementById(id),labels={pending_review:'À étudier',confirmed:'Confirmée',declined:'Refusée'};
let offset=0,current=null,busy=false,sequence=0;
const money=n=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
function message(text=''){$('message').textContent=text;}
function lock(value){busy=value;document.querySelectorAll('button,select,input,textarea').forEach(b=>b.disabled=value);}
async function api(action,body,params={}){
 const query=new URLSearchParams({operation:action,...params});
 const r=await fetch('/api/counter?'+query,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,cache:'no-store',signal:AbortSignal.timeout(18000)});
 const data=await r.json();
 if(r.status===401){$('login').hidden=false;$('dashboard').hidden=true;$('list').replaceChildren();$('detail').replaceChildren();current=null;}
 if(!r.ok)throw Error(data.error||'Erreur de connexion.');return data;
}
function el(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
async function list(){
 const n=++sequence;message();const data=await api('bmv-admin-list',null,{offset:String(offset),status:$('filter').value});if(n!==sequence)return;
 $('login').hidden=true;$('dashboard').hidden=false;$('list').replaceChildren();
 for(const r of data.rows){const button=el('button');button.className='request';button.classList.toggle('selected',current?.id===r.id);button.append(el('strong',r.company),el('span',r.spot_id+' · '+money(r.price_eur)+' · '+labels[r.status]+' · '+(r.payment_status==='paid'?'Payée':r.production_status==='ready_to_print'?'Prête à imprimer':'Non payée')),el('span',new Date(r.created_at).toLocaleDateString('fr-FR')));button.onclick=()=>detail(r.id).catch(e=>message(e.message));$('list').append(button);}
 if(!data.rows.length)$('list').append(el('p','Aucune demande dans cette catégorie.'));
 $('prev').disabled=offset===0;$('next').disabled=!data.hasMore;$('page').textContent='Page '+(offset/50+1);
}
async function detail(id){
 if(busy)return;lock(true);message();
 try{current=await api('bmv-admin-detail',null,{id});renderDetail();}
 finally{lock(false);}
}
function renderDetail(){
 const r=current,box=$('detail');box.replaceChildren(el('h2',r.company),el('p',labels[r.status]+' · '+r.spot_id+' · '+money(r.price_eur)));
 const dl=el('dl');for(const [k,v] of [['Contact',r.email],['Reçue le',new Date(r.created_at).toLocaleString('fr-FR')],['Durée',r.duration_months+' mois'],['Paiement',r.payment_status==='paid'?'Reçu'+(r.paid_at?' le '+new Date(r.paid_at).toLocaleDateString('fr-FR'):''):'Non reçu'],['Production',({waiting:'En attente',ready_to_print:'Prête à imprimer',printed:'Imprimée',installed:'Posée'})[r.production_status]],['Référence',r.id]])dl.append(el('dt',k),el('dd',v));box.append(dl);
 for(const [key,title,name] of [['logo_png','Logo fourni','logo.png'],['artwork_png','Placement enregistré','placement.png']]){
  box.append(el('h3',title));const img=el('img');img.src=r[key];img.alt=title+' de '+r.company;box.append(img);
  const download=el('a','Télécharger '+title.toLowerCase());download.href=r[key];download.download=r.spot_id+'-'+name;box.append(download);
 }
 const workflow=el('form');workflow.className='workflow';workflow.append(el('h3','Suivi privé'));
 const paymentLabel=el('label','Paiement');const payment=el('select');payment.name='payment_status';for(const [v,t] of [['unpaid','Non reçu'],['paid','Reçu']]){const o=el('option',t);o.value=v;o.selected=r.payment_status===v;payment.append(o);}paymentLabel.append(payment);
 const productionLabel=el('label','Avancement');const production=el('select');production.name='production_status';for(const [v,t] of [['waiting','En attente'],['ready_to_print','Prête à imprimer'],['printed','Imprimée'],['installed','Posée sur le van']]){const o=el('option',t);o.value=v;o.selected=r.production_status===v;production.append(o);}productionLabel.append(production);
 const notesLabel=el('label','Notes privées');const notes=el('textarea');notes.name='private_notes';notes.maxLength=5000;notes.rows=6;notes.value=r.private_notes||'';notes.placeholder='Échanges, facture, contraintes d’impression…';notesLabel.append(notes);
 const save=el('button','Enregistrer le suivi');save.className='primary';workflow.append(paymentLabel,productionLabel,notesLabel,save);
 workflow.onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true);message();try{await api('bmv-admin-manage',{id:r.id,revision:r.revision,payment_status:payment.value,production_status:production.value,private_notes:notes.value});current=await api('bmv-admin-detail',null,{id:r.id});renderDetail();message('Suivi privé enregistré.');await list();}catch(e){message(e.message);}finally{lock(false);}};
 const pdf=el('button','Télécharger la fiche partenaire PDF');pdf.type='button';pdf.className='pdf-button';pdf.onclick=async()=>{if(busy)return;lock(true);message('Création du PDF…');try{await window.BMV_PDF.download(r);message('Fiche partenaire téléchargée.');}catch{message('Le PDF n’a pas pu être créé. Réessayez.');}finally{lock(false);}};box.append(pdf);
 box.append(workflow);
 const actions=el('div');actions.className='toolbar';
 for(const [status,title] of [['confirmed','Confirmer cet emplacement'],['declined','Refuser la demande'],['pending_review','Remettre à étudier']]){
  if(status===r.status)continue;const button=el('button',title);button.className=status==='confirmed'?'primary':status==='declined'?'danger':'';
  button.onclick=async()=>{
   if(busy)return;const question=status==='confirmed'?'Réserver '+r.spot_id+' pour '+r.company+' ? Cela ne valide aucun paiement.':status==='declined'?'Refuser cette demande ? Si elle était confirmée, son emplacement redeviendra disponible.':'Remettre cette demande à étudier ? Son éventuelle réservation sera libérée.';
   if(!confirm(question))return;lock(true);message();try{await api('bmv-admin-review',{id:r.id,revision:r.revision,status});current=await api('bmv-admin-detail',null,{id:r.id});renderDetail();message('Statut enregistré. Aucun e-mail envoyé.');}catch(e){message(e.message);}finally{lock(false);await list().catch(e=>message(e.message));}
  };actions.append(button);
 }box.append(actions);
 if(r.status!=='pending_review'){
  const emailBox=el('section');emailBox.className='email-draft';emailBox.append(el('h3','Préparer l’e-mail à la marque'));
  const help=el('p','Relisez le message, téléchargez la fiche PDF puis joignez-la vous-même avant l’envoi. Le site ouvre seulement un brouillon : aucun e-mail n’est envoyé automatiquement.');help.className='email-help';emailBox.append(help);
  const grid=el('div');grid.className='email-grid';
  const kindLabel=el('label','Message');const kind=el('select');
  const allowed=[];if(r.status==='confirmed')allowed.push(['accepted','Emplacement confirmé']);if(r.payment_status==='paid')allowed.push(['payment','Paiement reçu']);if(r.status==='declined')allowed.push(['declined','Demande refusée']);
  for(const [value,title] of allowed){const option=el('option',title);option.value=value;kind.append(option);}
  if(r.payment_status==='paid')kind.value='payment';
  const langLabel=el('label','Langue');const lang=el('select');for(const [value,title] of [['en','English'],['fr','Français']]){const option=el('option',title);option.value=value;lang.append(option);}
  kindLabel.append(kind);langLabel.append(lang);grid.append(kindLabel,langLabel);emailBox.append(grid);
  const subjectLabel=el('label','Objet');const subject=el('input');subject.type='text';subject.maxLength=180;subjectLabel.append(subject);
  const bodyLabel=el('label','Message');const body=el('textarea');body.maxLength=5000;bodyLabel.append(body);emailBox.append(subjectLabel,bodyLabel);
  const updateDraft=()=>{const draft=window.BMV_EMAIL.make(r,kind.value,lang.value);subject.value=draft.subject;body.value=draft.body;};
  kind.onchange=updateDraft;lang.onchange=updateDraft;updateDraft();
  const emailActions=el('div');emailActions.className='email-actions';
  const copy=el('button','Copier le message');copy.type='button';copy.onclick=async()=>{const value=subject.value+'\n\n'+body.value;try{await navigator.clipboard.writeText(value);}catch{const temp=el('textarea');temp.value=value;document.body.append(temp);temp.select();document.execCommand('copy');temp.remove();}message('Objet et message copiés.');};
  const open=el('button','Ouvrir dans mon application e-mail');open.type='button';open.className='primary';open.onclick=()=>{location.href=window.BMV_EMAIL.mailto(r.email,subject.value,body.value);};
  emailActions.append(copy,open);emailBox.append(emailActions);box.append(emailBox);
 }
}
$('login').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true);message();try{await api('bmv-admin-login',{email:$('email').value.trim(),password:$('password').value});$('password').value='';await list();}catch(e){message(e.message);}finally{lock(false);}};
$('logout').onclick=async()=>{sequence++;try{await api('bmv-admin-logout',{});$('dashboard').hidden=true;$('login').hidden=false;$('list').replaceChildren();$('detail').replaceChildren();current=null;message('Déconnexion effectuée.');}catch(e){message(e.message);}};
$('filter').onchange=()=>{offset=0;list().catch(e=>message(e.message));};
$('refresh').onclick=()=>list().catch(e=>message(e.message));
$('prev').onclick=()=>{offset=Math.max(0,offset-50);list().catch(e=>message(e.message));};
$('next').onclick=()=>{offset+=50;list().catch(e=>message(e.message));};

const activationToken=new URLSearchParams(location.hash.slice(1)).get('activate');
if(activationToken){
 history.replaceState(null,'',location.pathname+location.search);
 $('login').hidden=true;$('activation').hidden=false;
}else{list().catch(e=>message(e.message));}
$('activation').onsubmit=async e=>{
 e.preventDefault();if(busy)return;
 if($('newPassword').value!==$('confirmPassword').value){message('Les deux mots de passe doivent être identiques.');return;}
 lock(true);message();
 try{
  const data=await api('bmv-admin-activate',{token:activationToken,password:$('newPassword').value});
  $('newPassword').value='';$('confirmPassword').value='';
  $('activation').hidden=true;$('login').hidden=false;$('email').value=data.email;
  message('Votre accès administrateur est activé. Connectez-vous avec le mot de passe que vous venez de choisir.');
 }catch(error){message(error.message);}finally{lock(false);}
};
