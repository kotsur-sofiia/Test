/* One diary shell stays above the selected topic. Forms remain mounted. */
'use strict';
(() => {
  const profileSections = new Set(['account','settings','subscription','devices']);
  const titles={account:'Профиль',settings:'Настройки',subscription:'Подписка',devices:'Подключённые устройства',capture:'Голосовая запись',library:'Медиатека',friends:'Друзья'};
  function measurePanel(panel, read) {
    const hidden=panel.hidden, visibility=panel.style.visibility;
    const display=panel.style.getPropertyValue('display'),priority=panel.style.getPropertyPriority('display');
    const concealed=hidden||getComputedStyle(panel).display==='none';
    if (concealed) {
      panel.style.visibility='hidden'; panel.hidden=false;
      if(getComputedStyle(panel).display==='none')panel.style.setProperty('display',panel.matches('nav[data-menu]')?'flex':'block','important');
    }
    try { return read(); }
    finally {
      if(concealed) {
        panel.hidden=hidden; panel.style.visibility=visibility;
        if(display)panel.style.setProperty('display',display,priority); else panel.style.removeProperty('display');
      }
    }
  }
  function labelBottom(panel, selector) {
    return Math.max(0,...[...panel.querySelectorAll(selector)].filter(e=>e.getClientRects().length).map(e=>e.getBoundingClientRect().bottom-panel.getBoundingClientRect().top));
  }
  function sharedShoreGeometry(header, navigation, gap) {
    const root=document.documentElement, style=getComputedStyle(root);
    const tabs=document.querySelector('.profile-tabs'), menu=navigation.querySelector('[data-menu=profile]'), diary=$('#diary-shell');
    const topicGap=parseFloat(style.getPropertyValue('--topic-label-gap'));
    const profileGap=parseFloat(style.getPropertyValue('--profile-row-gap'));
    const diaryExtent=measurePanel(diary,()=>labelBottom(diary,'.topic-label'))-(topicGap-10);
    const profileExtent=measurePanel(tabs,()=>tabs.getBoundingClientRect().height)+measurePanel(navigation,()=>measurePanel(menu,()=>labelBottom(navigation,'[data-menu=profile] a')))-(profileGap-16);
    const extent=Math.max(diaryExtent,profileExtent);
    root.style.setProperty('--topic-label-gap',(10+extent-diaryExtent)+'px');
    root.style.setProperty('--profile-row-gap',(16+extent-profileExtent)+'px');
    // One invisible text probe measures all headings, independent of the active route.
    const heading=$('#page-title'), probe=document.createElement('span');
    probe.setAttribute('aria-hidden','true');
    probe.style.cssText='position:fixed;left:0;top:-10000px;visibility:hidden;pointer-events:none;display:block;margin:0;padding:0;line-height:1.12;letter-spacing:.015em;text-transform:uppercase;white-space:normal;overflow-wrap:anywhere;';
    probe.style.width=heading.getBoundingClientRect().width+'px';
    probe.style.setProperty('font-family',getComputedStyle(heading).fontFamily,'important');
    probe.style.setProperty('font-weight','500','important');
    document.body.append(probe);
    let normalHeight=0,maxHeight=0;
    try {
      for (const [id,text] of Object.entries({...titles,diary:'Дневник',about:'Обо мне'})) {
        probe.style.fontSize=id==='devices'?'var(--device-title-size)':'var(--page-title-size)';
        probe.textContent=text;
        const height=probe.getBoundingClientRect().height;
        if(id==='diary')normalHeight=height;
        maxHeight=Math.max(maxHeight,height);
      }
    } finally { probe.remove(); }
    const top=header.getBoundingClientRect().top+parseFloat(getComputedStyle(header).paddingTop);
    return {captionBottom:top+normalHeight+gap+extent,maximumBottom:top+maxHeight+gap+extent};
  }
  function updateTopPanel() {
    const header = document.querySelector('main>header');
    const navigation = document.querySelector('.section-navigation');
    navigation.hidden = ![...navigation.querySelectorAll('nav')].some(nav=>!nav.hidden&&getComputedStyle(nav).display!=='none');
    const headingBottom = $('#page-title').getBoundingClientRect().bottom;
    const headingGap = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--heading-controls-gap'));
    const shared=sharedShoreGeometry(header,navigation,headingGap);
    let cursor = headingBottom+headingGap;
    let bottom = headingBottom;
    let controlsTop = null;
    for (const panel of [document.querySelector('.profile-tabs'),navigation,$('#diary-shell')]) {
      if (panel.hidden) continue;
      if (controlsTop===null) controlsTop=cursor;
      panel.style.top=cursor+'px';
      cursor+=panel.getBoundingClientRect().height;
      // Measure painted controls and captions, excluding transparent glow padding.
      for (const label of panel.querySelectorAll('.topic-label,nav a,.profile-tab-control a')) {
        if (label.checkVisibility()) bottom=Math.max(bottom,label.getBoundingClientRect().bottom);
      }
    }
    document.documentElement.style.setProperty('--top-panel-height',(controlsTop===null ? header.getBoundingClientRect().bottom : bottom+12)+'px');
    // Stretch the actual document photo so even the highest part of the foam
    // passes below the last caption, including the second profile menu.
    const wide=matchMedia('(min-width:768px)').matches;
    const photoHeight=(shared.maximumBottom+18)/(wide ? .13 : .165);
    document.documentElement.style.setProperty('--shore-photo-height',photoHeight+'px');
    document.documentElement.style.setProperty('--shore-fade-start',(controlsTop===null ? shared.captionBottom : bottom)+'px');
    document.documentElement.style.setProperty('--shore-fade-end',(photoHeight*(wide ? .181 : .198))+'px');
  }
  function current() {
    if (location.hash === '#goals') history.replaceState(null,'','#profile');
    let raw;
    try { raw = decodeURIComponent(location.hash.slice(1) || 'home'); } catch { raw = 'home'; }
    const id = raw === 'cycle-form' ? 'cycle' : raw === 'home' ? (window.WomanDayMap?.homeTopic() ?? ($('#cycle').dataset.available === 'false' ? 'food' : 'cycle')) : raw;
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
    const heading=$('#page-title');
    heading.textContent=route.area==='diary'&&section!=='profile'?'Дневник':section==='profile'?'Обо мне':(titles[route.id]||titles[route.area]||'Профиль');
    if(section!=='cycle')window.WomanPeriodEditor?.close();
    for (const panel of document.querySelectorAll('[data-main-view]')) {
      panel.hidden = panel.dataset.mainView !== route.area || panel.id !== (route.area === 'profile' ? route.profileSection : section);
    }
    $('#diary-shell').hidden = route.area !== 'diary' || section === 'profile';
    for (const menu of document.querySelectorAll('.section-navigation nav[data-menu]')) menu.hidden = menu.dataset.menu !== route.area;
    const profileArea = route.area === 'profile' || route.area === 'friends';
    const profileTabs = document.querySelector('.profile-tabs');
    profileTabs.hidden = !profileArea;
    for (const link of profileTabs.querySelectorAll('a')) {
      const selected = link.hash === (route.area === 'friends' ? '#friends' : '#account');
      if (selected) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    }
    for (const link of document.querySelectorAll('.bottom-nav a')) {
      const active = link.dataset.view === (profileArea ? 'profile' : route.area);
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
    updateTopPanel();
  }
  function navigate() {
    refresh();
    requestAnimationFrame(() => {
      const route = current();
      if(route.raw==='cycle-form'&&$('#cycle').dataset.available!=='false'){window.WomanPeriodEditor?.open();return;}
      if (route.target?.matches('[data-main-view]') || route.raw === 'home') window.scrollTo({top:0,behavior:'instant'});
      else (route.target && !route.target.closest('[hidden]') ? route.target : document.querySelector('[data-main-view]:not([hidden])'))?.scrollIntoView({block:'start',behavior:'instant'});
    });
  }
  window.addEventListener('load',navigate);
  window.addEventListener('hashchange',navigate);
  window.addEventListener('resize',updateTopPanel);
  const topPanelObserver = new ResizeObserver(updateTopPanel);
  for (const panel of document.querySelectorAll('main>header,#page-title,.profile-tabs,.section-navigation,#diary-shell')) topPanelObserver.observe(panel);
  document.fonts.ready.then(updateTopPanel);
  window.LunaNavigation = Object.freeze({refresh});
  refresh();
})();
