(()=>{
 const config=window.BMV_CONFIG;window.BMV_CONFIRMED=new Set();
 function apply(data){
  window.BMV_CONFIRMED=new Set(data.confirmed.map(r=>r.spot_id));
  const count=window.BMV_CONFIRMED.size,total=data.confirmed.reduce((n,r)=>n+r.price_eur,0),paid=data.confirmed.filter(r=>r.payment_status==='paid').reduce((n,r)=>n+r.price_eur,0),money=n=>n.toLocaleString('fr-FR')+' €',viewNames={left:'gauche',right:'droite',rear:'arrière'};
  const header=document.querySelector('.header-progress');header.querySelector('span').textContent=count+' / 20 confirmés';header.querySelector('strong').textContent=money(total)+' réservés';
  const cells=document.querySelectorAll('.status-strip>div');
  cells[0].querySelector('strong').textContent=(20-count)+' emplacement'+(20-count===1?'':'s');cells[1].querySelector('span').textContent='Confirmés';cells[1].querySelector('strong').textContent=count;
  cells[2].querySelector('span').textContent='Paiements reçus';cells[2].querySelector('strong').textContent=money(paid)+' / 10 000 €';
  for(const option of document.querySelectorAll('#spotChoice option')){const s=config.spots.find(s=>s.id===option.value);if(s){option.disabled=window.BMV_CONFIRMED.has(s.id);option.textContent=s.id+' · '+viewNames[s.view]+' · '+money(s.price)+(option.disabled?' · confirmé':'');}}
  window.dispatchEvent(new CustomEvent('bmv:availability'));
 }
 async function update(){try{const r=await fetch('/api/counter?operation=bmv-availability',{cache:'no-store'});if(!r.ok)throw Error();apply(await r.json());}catch{const h=document.querySelector('.header-progress');h.querySelector('span').textContent='Disponibilité à confirmer';h.querySelector('strong').textContent='Objectif 10 000 €';}}
 update();window.addEventListener('focus',update);setInterval(update,60000);
})();
