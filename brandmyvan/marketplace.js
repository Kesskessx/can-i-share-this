(()=>{
  const cards=[...document.querySelectorAll('.campaign-card')];
  const fofoCard=document.querySelector('[data-profile-id="fofo"]');
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
  const categoryLinks=[...document.querySelectorAll('[data-category-quick]')];
  let activeNetwork='all';
  const normalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();

  function syncCategoryLinks(){
    categoryLinks.forEach(link=>link.classList.toggle('active',link.dataset.categoryQuick===filters.category.value));
  }

  function applyFilters(){
    const query=normalize(filters.search.value);
    let visibleCount=0;
    cards.forEach(card=>{
      const matchesSearch=!query||normalize(card.dataset.search).includes(query);
      const matchesCountry=filters.country.value==='all'||card.dataset.country===filters.country.value;
      const matchesCategory=filters.category.value==='all'||card.dataset.categories.split(' ').includes(filters.category.value);
      const matchesBudget=filters.budget.value==='all'||Number(card.dataset.price)<=Number(filters.budget.value);
      const matchesNetwork=activeNetwork==='all'||card.dataset.networks.split(' ').includes(activeNetwork);
      const visible=matchesSearch&&matchesCountry&&matchesCategory&&matchesBudget&&matchesNetwork;
      card.hidden=!visible;
      if(visible)visibleCount+=1;
    });
    empty.hidden=visibleCount>0;
    grid.hidden=visibleCount===0;
    count.textContent=visibleCount+' créateur'+(visibleCount===1?'':'s')+' disponible'+(visibleCount===1?'':'s');
    syncCategoryLinks();
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
  categoryLinks.forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault();
    filters.category.value=link.dataset.categoryQuick;
    applyFilters();
    document.getElementById('explore').scrollIntoView();
  }));
  document.getElementById('vanFilters').addEventListener('submit',event=>{
    event.preventDefault();
    applyFilters();
    document.getElementById('explore').scrollIntoView();
  });
  document.getElementById('resetFilters').addEventListener('click',resetFilters);
  document.getElementById('emptyReset').addEventListener('click',resetFilters);

  async function updateAvailability(){
    try{
      const response=await fetch('/api/counter?operation=bmv-availability',{cache:'no-store'});
      if(!response.ok)throw new Error('availability');
      const data=await response.json();
      const confirmed=Array.isArray(data.confirmed)?data.confirmed:[];
      const available=Math.max(0,20-confirmed.length);
      document.getElementById('availableSpots').textContent=available+' emplacement'+(available===1?'':'s');
      document.getElementById('snapshotSpots').textContent=String(available);
      fofoCard.dataset.available=String(available>0);
      const status=fofoCard.querySelector('.campaign-status');
      status.lastChild.textContent=available>0?' Campagne ouverte':' Campagne complète';
    }catch{
      document.getElementById('availableSpots').textContent='Disponibilité sur la fiche';
    }
  }

  applyFilters();
  updateAvailability();
  window.addEventListener('focus',updateAvailability);
})();
