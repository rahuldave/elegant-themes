(() => {
  const themes = window.THEME_LIBRARY;
  const allowedPages = ['index.html','typography.html','code.html','components.html'];
  const params = new URLSearchParams(location.search);
  let mode = params.get('mode') === 'dark' ? 'dark' : 'light';
  let group = ['custom','bootstrap','bootswatch','refined','comparisons'].includes(params.get('group')) ? params.get('group') : 'all';
  let page = allowedPages.includes(params.get('page')) ? params.get('page') : 'index.html';
  const perThemeMode = new Map();
  const pairOrder = ['folio-original','folio','atelier-original','atelier','nocturne-original','nocturne','zephyr','zephyr-reading','simplex','simplex-reading','pulse','pulse-reading','litera','litera-reading','darkly','darkly-reading'];
  const grid = document.querySelector('#theme-grid');
  const search = document.querySelector('#theme-search');
  const pageSelect = document.querySelector('#specimen-page');
  search.value = params.get('q') || '';
  pageSelect.value = page;

  function previewUrl(theme) {
    const selectedMode = theme.paired ? (perThemeMode.get(theme.id) || mode) : 'original';
    return `previews/${theme.id}/${page}?mode=${selectedMode}`;
  }

  function saveLocation() {
    const p = new URLSearchParams();
    if (mode !== 'light') p.set('mode',mode);
    if (group !== 'all') p.set('group',group);
    if (page !== 'index.html') p.set('page',page);
    if (search.value.trim()) p.set('q',search.value.trim());
    history.replaceState(null,'',location.pathname + (p.size ? '?' + p : '') + location.hash);
  }

  function updateButtons() {
    document.querySelectorAll('[data-group]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.group === group)));
    document.querySelectorAll('[data-global-mode]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.globalMode === mode)));
    document.querySelectorAll('[data-card-mode]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.cardMode === (perThemeMode.get(b.dataset.theme) || mode))));
  }

  function updateFrames(onlyTheme) {
    themes.filter(t => !onlyTheme || t.id === onlyTheme).forEach(t => {
      const frame = document.getElementById(`preview-${t.id}`);
      const next = previewUrl(t);
      frame.dataset.preview = next;
      if (frame.hasAttribute('src') && frame.getAttribute('src') !== next) frame.setAttribute('src',next);
      document.querySelector(`[data-theme-card="${t.id}"] .full-preview`).href = next;
      frame.title = `${t.name}: ${pageSelect.selectedOptions[0].text}, ${t.paired ? (perThemeMode.get(t.id) || mode) + ' mode' : 'native palette'}`;
    });
    updateButtons();
    saveLocation();
  }

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const frame = entry.target;
        frame.src = frame.dataset.preview;
        observer.unobserve(frame);
      }
    });
  },{rootMargin:'700px'});

  for (const [i,t] of themes.entries()) {
    const card = document.createElement('article');
    card.className = 'theme-card';
    card.dataset.themeCard = t.id;
    card.setAttribute('aria-labelledby',`title-${t.id}`);
    const modeControls = t.paired
      ? `<div class="card-mode" role="group" aria-label="${t.name} color mode"><button data-card-mode="light" data-theme="${t.id}">Light</button><button data-card-mode="dark" data-theme="${t.id}">Dark</button></div>`
      : '<span class="palette-label">Native palette</span>';
    card.innerHTML = `<div class="card-heading"><div class="card-title"><span class="card-number">${String(i+1).padStart(2,'0')}</span><h2 id="title-${t.id}">${t.name}</h2></div>${modeControls}</div>
      <div class="specimen-wrap"><iframe id="preview-${t.id}" title="${t.name} specimen" loading="lazy" data-preview="${previewUrl(t)}" style="--frame-paper:${t.colors[0]}"></iframe></div>
      <div class="card-details">${t.typeScore ? `<p class="score-line">Typography <strong>${t.typeScore}/100</strong> · Design <strong>${t.designScore}/100</strong> <a href="typography-report.html#theme-${t.id}">Why?</a></p>` : ''}<p class="card-description">${t.description}</p><div class="card-type-row"><span class="type-label">${t.type}</span><span class="swatches" aria-hidden="true">${t.colors.map(c=>`<i style="--swatch:${c}"></i>`).join('')}</span></div>
      <div class="card-links"><a class="full-preview" href="${previewUrl(t)}" target="_blank" rel="noopener">Full preview ↗</a><a href="${t.source}" target="_blank" rel="noopener">${['custom','refined'].includes(t.group) ? 'Theme source' : 'Original theme'} ↗</a><a href="${t.guide}">Theme handbook</a><span class="family-badge">${t.group === 'custom' ? 'Custom' : t.group === 'bootstrap' ? 'Bootstrap' : t.group === 'refined' ? 'Reading refinement' : 'Bootswatch'}</span></div>
      <div class="install-line"><code>${t.install}</code><button class="copy-command" data-copy="${t.id}" aria-label="Copy ${t.name} installation setting">Copy</button></div></div>`;
    grid.append(card);
    observer.observe(card.querySelector('iframe'));
  }

  function filterCards(scrollToResults = false) {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    themes.forEach(t => {
      const matches = (group === 'all' || t.group === group || (group === 'comparisons' && pairOrder.includes(t.id))) && `${t.name} ${t.description} ${t.type} ${t.group}`.toLowerCase().includes(query);
      document.querySelector(`[data-theme-card="${t.id}"]`).hidden = !matches;
      if (matches) visible++;
    });
    const ordered = group === 'comparisons' ? [...themes].sort((a,b)=>pairOrder.indexOf(a.id)-pairOrder.indexOf(b.id)) : themes;
    ordered.forEach(t=>grid.append(document.querySelector(`[data-theme-card="${t.id}"]`)));
    document.querySelector('#result-count').textContent = `${visible} ${visible === 1 ? 'design' : 'designs'}${visible < themes.length ? ' of ' + themes.length : ''}`;
    document.querySelector('#empty-state').hidden = visible > 0;
    updateButtons();
    saveLocation();
    if (scrollToResults) document.getElementById('designs').scrollIntoView({block:'start'});
  }

  document.querySelectorAll('[data-group]').forEach(b => b.addEventListener('click',() => {group=b.dataset.group;filterCards(true);}));
  document.querySelectorAll('[data-global-mode]').forEach(b => b.addEventListener('click',() => {mode=b.dataset.globalMode;perThemeMode.clear();updateFrames();}));
  document.querySelectorAll('[data-card-mode]').forEach(b => b.addEventListener('click',() => {const t=themes.find(t=>t.id===b.dataset.theme);themes.filter(x=>x.paired && (x.id===t.id || (t.comparison && x.comparison===t.comparison))).forEach(x=>perThemeMode.set(x.id,b.dataset.cardMode));updateFrames();}));
  document.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click',async () => {
    const text = themes.find(t=>t.id===b.dataset.copy).install;
    try {await navigator.clipboard.writeText(text);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1600);} catch {b.textContent='Select the text';}
  }));
  search.addEventListener('input',() => filterCards(true));
  pageSelect.addEventListener('change',() => {page=pageSelect.value;updateFrames();});
  window.addEventListener('message',event => {
    if (event.origin !== location.origin || event.data?.type !== 'specimen-page' || !allowedPages.includes(event.data.page)) return;
    if (!themes.some(t=>document.getElementById(`preview-${t.id}`).contentWindow===event.source)) return;
    page=event.data.page;pageSelect.value=page;updateFrames();
  });
  filterCards();updateFrames();
})();
