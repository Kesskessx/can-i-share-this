(()=>{
  const card=document.querySelector('.campaign-card');
  const filters={
    search:document.getElementById('searchFilter'),
    country:document.getElementById('countryFilter'),
    category:document.getElementById('categoryFilter'),
    budget:document.getElementById('budgetFilter')
  };
  const grid=document.getElementById('campaignGrid');
  const empty=document.getElementById('emptyResult');
  const count=document.getElementById('resultCount');
  const networkButtons=[...document.querySelectorAll('[data-network-filter]')];
  let activeNetwork='all';
  const normalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();

  function applyFilters(){
    const query=normalize(filters.search.value);
    const matchesSearch=!query||normalize(card.dataset.search).includes(query);
    const matchesCountry=filters.country.value==='all'||card.dataset.country===filters.country.value;
    const matchesCategory=filters.category.value==='all'||card.dataset.categories.split(' ').includes(filters.category.value);
    const matchesBudget=filters.budget.value==='all'||Number(card.dataset.price)<=Number(filters.budget.value);
    const matchesNetwork=activeNetwork==='all'||card.dataset.networks.split(' ').includes(activeNetwork);
    const visible=matchesSearch&&matchesCountry&&matchesCategory&&matchesBudget&&matchesNetwork;
    card.hidden=!visible;
    empty.hidden=visible;
    grid.classList.toggle('single-result',visible);
    count.textContent=visible?'1 campagne disponible':'0 campagne disponible';
  }

  function resetFilters(){
    filters.search.value='';
    filters.country.value='all';
    filters.category.value='all';
    filters.budget.value='all';
    activeNetwork='all';
    networkButtons.forEach(button=>{const active=button.dataset.networkFilter==='all';button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});
    applyFilters();
    filters.search.focus();
  }

  Object.values(filters).forEach(control=>control.addEventListener(control.tagName==='INPUT'?'input':'change',applyFilters));
  networkButtons.forEach(button=>button.addEventListener('click',()=>{
    activeNetwork=button.dataset.networkFilter;
    networkButtons.forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
    applyFilters();
  }));
  document.getElementById('vanFilters').addEventListener('submit',event=>{event.preventDefault();applyFilters();});
  document.getElementById('resetFilters').addEventListener('click',resetFilters);
  document.getElementById('emptyReset').addEventListener('click',resetFilters);

  async function updateAvailability(){
    try{
      const response=await fetch('/api/counter?operation=bmv-availability',{cache:'no-store'});
      if(!response.ok)throw new Error('availability');
      const data=await response.json();
      const confirmed=Array.isArray(data.confirmed)?data.confirmed:[];
      const available=Math.max(0,20-confirmed.length);
      const reserved=confirmed.reduce((total,item)=>total+(Number(item.price_eur)||0),0);
      document.getElementById('availableSpots').textContent=available+' emplacement'+(available===1?'':'s');
      document.getElementById('reservedAmount').textContent=reserved.toLocaleString('fr-FR')+' € sur 10 000 €';
      document.getElementById('reservedProgress').style.width=Math.min(100,reserved/100)+'%';
      card.dataset.available=String(available>0);
      const status=card.querySelector('.campaign-status');
      status.lastChild.textContent=available>0?' Campagne ouverte':' Campagne complète';
    }catch{
      document.getElementById('availableSpots').textContent='Disponibilité sur la fiche';
    }
  }

  applyFilters();
  updateAvailability();
  window.addEventListener('focus',updateAvailability);
})();
