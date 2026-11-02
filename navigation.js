/* One diary shell stays above the selected topic. Forms remain mounted. */
'use strict';
(() => {
  const profileSections = new Set(['account','settings','subscription','devices']);
  function current() {
    if (location.hash === '#goals') history.replaceState(null,'','#profile');
    let raw;
    try { raw = decodeURIComponent(location.hash.slice(1) || 'home'); } catch { raw = 'home'; }
    const id = raw === 'home' ? (window.WomanDayMap?.homeTopic() ?? ($('#cycle').dataset.available === 'false' ? 'food' : 'cycle')) : raw;
    const notes = ['skin','books','meditation','drawing'].includes(id) || id.startsWith('custom-');
    const target = id === 'affirmation' ? $('#home') : id === 'empty' ? $('#day-placeholder') : notes ? $('#topic-notes') : document.getElementById(id);
    const area = target?.closest('[data-main-view]')?.dataset.mainView || 'profile';
    const section = target?.closest('[data-main-view]')?.id;
    const topic = notes ? id : section==='home' ? 'affirmation' : section==='day-placeholder' ? 'empty' : section;
    return {id,raw,target,area,section,topic,profileSection:profileSections.has(id) ? id : 'account'};
  }
  function refresh() {
    const route = current();
    let section = route.section;
    if (section === 'cycle' && $('#cycle').dataset.available === 'false') section = 'day-placeholder';
    document.body.dataset.view = route.area;
    document.body.dataset.section = route.area === 'diary' ? section : route.profileSection;
    document.body.dataset.topic = route.topic;
    for (const panel of document.querySelectorAll('[data-main-view]')) {
      panel.hidden = panel.dataset.mainView !== route.area || panel.id !== (route.area === 'profile' ? route.profileSection : section);
    }
    $('#diary-shell').hidden = route.area !== 'diary' || section === 'profile';
    for (const menu of document.querySelectorAll('.section-navigation nav[data-menu]')) menu.hidden = menu.dataset.menu !== route.area;
    for (const link of document.querySelectorAll('.bottom-nav a')) {
      const active = link.dataset.view === route.area;
      link.classList.toggle('active',active);
      if (active) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    }
    for (const link of document.querySelectorAll('.section-navigation nav a')) {
      const selected = link.hash === '#'+(route.area === 'profile' ? route.profileSection : route.raw);
      link.classList.toggle('active',selected);
      if (selected) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    }
    window.WomanDayMap?.routeChanged(route.topic);
    window.LunaVoice?.refresh();
    window.WomanCycleCare?.refresh();
  }
  function navigate() {
    refresh();
    requestAnimationFrame(() => {
      const route = current();
      if (route.target?.matches('[data-main-view]') || route.raw === 'home') window.scrollTo({top:0,behavior:'instant'});
      else (route.target && !route.target.closest('[hidden]') ? route.target : document.querySelector('[data-main-view]:not([hidden])'))?.scrollIntoView({block:'start',behavior:'instant'});
    });
  }
  $('#settings-export').onclick = () => $('#export-data').click();
  window.addEventListener('load',navigate);
  window.addEventListener('hashchange',navigate);
  window.LunaNavigation = Object.freeze({refresh});
  refresh();
})();
