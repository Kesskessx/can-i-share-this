(()=>{
 const config=window.BMV_CONFIG;window.BMV_CONFIRMED=new Set();
 function apply(data){
  window.BMV_CONFIRMED=new Set(data.confirmed.map(r=>r.spot_id));
  const count=window.BMV_CONFIRMED.size,total=data.confirmed.reduce((n,r)=>n+r.price_eur,0),money=n=>'€'+n.toLocaleString('en-US');
  const header=document.querySelector('.header-progress');header.querySelector('span').textContent=count+' / 20 confirmed';header.querySelector('strong').textContent=money(total)+' reserved';
  const cells=document.querySelectorAll('.status-strip>div');
  cells[0].querySelector('strong').textContent=(20-count)+' spots';cells[1].querySelector('span').textContent='Confirmed';cells[1].querySelector('strong').textContent=count;
  cells[2].querySelector('span').textContent='Reserved value · not payments';cells[2].querySelector('strong').textContent=money(total)+' / €10,000';
  for(const option of document.querySelectorAll('#spotChoice option')){const s=config.spots.find(s=>s.id===option.value);if(s){option.disabled=window.BMV_CONFIRMED.has(s.id);option.textContent=s.id+' · '+s.view+' · '+money(s.price)+(option.disabled?' · confirmed':'');}}
  window.dispatchEvent(new CustomEvent('bmv:availability'));
 }
 async function update(){try{const r=await fetch('/api/counter?operation=bmv-availability',{cache:'no-store'});if(!r.ok)throw Error();apply(await r.json());}catch{const h=document.querySelector('.header-progress');h.querySelector('span').textContent='Availability pending';h.querySelector('strong').textContent='€10,000 goal';}}
 update();window.addEventListener('focus',update);setInterval(update,60000);
})();