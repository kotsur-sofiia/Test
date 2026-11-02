/* Main areas share the existing DOM so navigation preserves unsaved inputs. */
'use strict';
(() => {
 const phone=matchMedia('(max-width:767px),(max-width:1023px) and (pointer:coarse)');
 const profileSections=new Set(['account','settings','subscription','devices']);
 function current(){if(location.hash==='#goals')history.replaceState(null,'','#profile');let id;try{id=decodeURIComponent(location.hash.slice(1)||'home');}catch{id='home';}const target=document.getElementById(id);const area=target?.closest('[data-main-view]')?.dataset.mainView||'profile';return {id,target,area,profileSection:profileSections.has(id)?id:'account'};}
 function refresh(){const route=current();let section=route.target?.closest('#profile,#food,#sleep,#cycle,#activity')?.id||'home';if(section==='cycle'&&$('#cycle').dataset.available==='false')section='home';document.body.dataset.view=route.area;document.body.dataset.section=route.area==='diary'?section:route.profileSection;for(const panel of document.querySelectorAll('[data-main-view]')){let visible=panel.dataset.mainView===route.area;if(route.area==='profile')visible=visible&&panel.id===route.profileSection;if(route.area==='diary'){if(section==='profile')visible=visible&&panel.id==='profile';else{visible=visible&&panel.id!=='profile';visible=visible&&panel.id===section;}}if(panel.id==='cycle'&&panel.dataset.available==='false')visible=false;panel.hidden=!visible;}
  for(const menu of document.querySelectorAll('.section-navigation nav[data-menu]'))menu.hidden=menu.dataset.menu!==route.area;
  for(const link of document.querySelectorAll('.bottom-nav a')){const active=link.dataset.view===route.area;link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
  let diarySection=section;if(diarySection==='cycle'&&$('#cycle').dataset.available==='false')diarySection='home';
  for(const link of document.querySelectorAll('.section-navigation nav a')){const selected=route.area==='profile'?link.hash==='#'+route.profileSection:route.area==='diary'?link.hash==='#'+diarySection:link.hash==='#'+route.area;link.classList.toggle('active',selected);if(selected)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
  const activeLink=document.querySelector('.section-navigation nav:not([hidden]) a.active');if(activeLink){const menu=activeLink.parentElement,a=activeLink.getBoundingClientRect(),b=menu.getBoundingClientRect();if(a.left<b.left)menu.scrollLeft-=b.left-a.left+6;else if(a.right>b.right)menu.scrollLeft+=a.right-b.right+6;}
  window.LunaVoice?.refresh();
 }
 function startsAtTop(route){return ['profile','home'].includes(route.id)||route.target?.matches('[data-main-view]');}
 function navigate(){refresh();requestAnimationFrame(()=>{const route=current();if(startsAtTop(route)){window.scrollTo({top:0,behavior:'instant'});return;}const target=route.target&&!route.target.closest('[hidden]')?route.target:document.querySelector('[data-main-view]:not([hidden])');target?.scrollIntoView({block:'start',behavior:'instant'});});}
 $('#settings-export').onclick=()=>$('#export-data').click();
 phone.addEventListener('change',refresh);
 window.addEventListener('load',()=>{if(startsAtTop(current()))window.scrollTo({top:0,behavior:'instant'});});window.addEventListener('hashchange',navigate);window.LunaNavigation=Object.freeze({refresh});refresh();
})();
