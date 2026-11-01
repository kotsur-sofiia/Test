/* Main areas share the existing DOM so navigation preserves unsaved inputs. */
'use strict';
(() => {
 const phone=matchMedia('(max-width:767px),(max-width:1023px) and (pointer:coarse)');
 const profileSections=new Set(['profile','settings','goals']);
 function current(){let id;try{id=decodeURIComponent(location.hash.slice(1)||'profile');}catch{id='profile';}const target=document.getElementById(id);const area=target?.closest('[data-main-view]')?.dataset.mainView||'profile';return {id,target,area,profileSection:profileSections.has(id)?id:'profile'};}
 function refresh(){const route=current();let section=route.target?.closest('#food,#sleep,#cycle')?.id||'home';if(section==='cycle'&&$('#cycle').dataset.available==='false')section='home';document.body.dataset.view=route.area;for(const panel of document.querySelectorAll('[data-main-view]')){let visible=panel.dataset.mainView===route.area;if(route.area==='profile')visible=visible&&panel.id===route.profileSection;if(route.area==='diary'&&phone.matches)visible=visible&&(panel.id===section||!panel.id&&section==='home');if(panel.id==='cycle'&&panel.dataset.available==='false')visible=false;panel.hidden=!visible;}
  for(const menu of document.querySelectorAll('.sidebar nav[data-menu]'))menu.hidden=menu.dataset.menu!==route.area;
  for(const link of document.querySelectorAll('.bottom-nav a')){const active=link.dataset.view===route.area;link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
  let diarySection=section;if(diarySection==='cycle'&&$('#cycle').dataset.available==='false')diarySection='home';
  for(const link of document.querySelectorAll('.sidebar nav a')){const selected=route.area==='profile'?link.hash==='#'+route.profileSection:route.area==='diary'?link.hash==='#'+diarySection:link.hash==='#'+route.area;link.classList.toggle('active',selected);if(selected)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
  window.LunaVoice?.refresh();
 }
 function navigate(){refresh();requestAnimationFrame(()=>{const route=current();const target=route.target&&!route.target.closest('[hidden]')?route.target:document.querySelector('[data-main-view]:not([hidden])');target?.scrollIntoView({block:'start',behavior:'instant'});});}
 $('#settings-export').onclick=()=>$('#export-data').click();
 phone.addEventListener('change',refresh);
 window.addEventListener('hashchange',navigate);window.LunaNavigation=Object.freeze({refresh});refresh();
})();
