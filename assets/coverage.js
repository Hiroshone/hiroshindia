(() => {
  const directory = document.querySelector('#state-directory');
  if (!directory) return;
  const search = document.querySelector('#district-search');
  const select = document.querySelector('#coverage-state');
  const sections = [...directory.querySelectorAll('.coverage-state')];
  const normalise = value => value.toLowerCase().replace(/[^a-z0-9]/g, '');
  const aliases = {bangalore:'bengaluru',trivandrum:'thiruvananthapuram',calcutta:'kolkata',bombay:'mumbai',madras:'chennai',pondicherry:'puducherry',orissa:'odisha',uttaranchal:'uttarakhand',cochin:'ernakulam',kochi:'ernakulam',alleppey:'alappuzha',quilon:'kollam',calicut:'kozhikode'};
  function filter() {
    const term = normalise(search.value.trim());
    const query = aliases[term] || term;
    document.querySelector('.state-jumps').hidden = Boolean(query || select.value);
    let districtCount = 0, stateCount = 0;
    for (const section of sections) {
      const stateMatch = !select.value || select.value === section.dataset.state;
      const nameMatch = normalise(section.dataset.name).includes(query);
      let count = 0;
      for (const row of section.querySelectorAll('li')) {
        const match = stateMatch && (!query || nameMatch || normalise(row.dataset.district).includes(query));
        row.hidden = !match;
        if (match) count++;
      }
      section.hidden = !count;
      section.open = Boolean(count && (query || select.value));
      if (count) stateCount++;
      districtCount += count;
    }
    document.querySelector('#coverage-status').textContent = `${districtCount} districts in ${stateCount} states / union territories`;
    document.querySelector('#coverage-empty').hidden = districtCount > 0;
  }
  document.querySelector('.coverage-controls').hidden = false;
  search.addEventListener('input', filter);
  select.addEventListener('change', filter);
  document.querySelector('#coverage-reset').addEventListener('click', () => {search.value='';select.value='';filter();search.focus();});
  function openHash() {
    if (!/^#state-\d+$/.test(location.hash)) return;
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    search.value='';select.value='';filter();target.open=true;target.scrollIntoView({block:'start'});
  }
  window.addEventListener('hashchange', openHash);
  document.querySelector('.state-jumps').addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link && link.hash === location.hash) openHash();
  });
  filter();openHash();
})();
