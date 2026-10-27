const storageKey = 'little-steps-tasks-v1';
const initial = [{id:'first',text:'Выпить стакан воды',done:true},{id:'second',text:'Выйти на небольшую прогулку',done:false},{id:'third',text:'Сделать что-то приятное для себя',done:false}];
let tasks;
try { const stored = JSON.parse(localStorage.getItem(storageKey)); tasks = Array.isArray(stored) && stored.every(t => t && typeof t.id === 'string' && typeof t.text === 'string' && typeof t.done === 'boolean') ? stored : initial; } catch { tasks = initial; }
const list = document.querySelector('#task-list');
const notice = document.querySelector('#notice');
document.querySelector('#date').textContent = new Intl.DateTimeFormat('ru', {weekday:'long',day:'numeric',month:'long'}).format(new Date()).toUpperCase();
function save() { try { localStorage.setItem(storageKey,JSON.stringify(tasks)); } catch { notice.hidden=false; notice.textContent='Браузер не разрешает сохранение. Задачи доступны до закрытия страницы.'; } render(); }
function render() {
  list.replaceChildren();
  for (const task of tasks) {
    const item=document.createElement('li'); item.classList.toggle('done',task.done);
    const label=document.createElement('label');
    const check=document.createElement('input'); check.type='checkbox'; check.checked=task.done;
    check.addEventListener('change',()=>{task.done=check.checked;save();});
    const text=document.createElement('span'); text.textContent=task.text; label.append(check,text);
    const remove=document.createElement('button'); remove.className='delete'; remove.textContent='×'; remove.setAttribute('aria-label',`Удалить: ${task.text}`);
    remove.addEventListener('click',()=>{tasks=tasks.filter(t=>t.id!==task.id);save();});
    item.append(label,remove);list.append(item);
  }
  const done=tasks.filter(t=>t.done).length;
  document.querySelector('#counter').textContent=`${done} из ${tasks.length}`;
  document.querySelector('#remaining').textContent=tasks.length?`Осталось: ${tasks.length-done}`:'Чистый лист';
  document.querySelector('#progress').max=tasks.length||1;document.querySelector('#progress').value=done;
  document.querySelector('#encouragement').textContent=tasks.length&&done===tasks.length?'Всё готово. Время отдохнуть ✨':'Каждый маленький шаг считается ✨';
}
document.querySelector('#task-form').addEventListener('submit',event=>{event.preventDefault();const input=document.querySelector('#task-input');const text=input.value.trim();if(!text)return;tasks.push({id:crypto.randomUUID(),text,done:false});input.value='';save();input.focus();});
function connection(){const status=document.querySelector('#connection');status.textContent=navigator.onLine?'На связи':'Без интернета';status.classList.toggle('offline',!navigator.onLine);}
window.addEventListener('online',connection);window.addEventListener('offline',connection);
let installPrompt;const install=document.querySelector('#install');
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installPrompt=event;install.hidden=false;document.querySelector('#install-hint').hidden=true;});
install.addEventListener('click',async()=>{if(!installPrompt)return;await installPrompt.prompt();installPrompt=null;install.hidden=true;document.querySelector('#install-hint').hidden=false;});
window.addEventListener('appinstalled',()=>{install.hidden=true;document.querySelector('#install-hint').hidden=true;});
if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{notice.hidden=false;notice.textContent='Офлайн-режим пока недоступен. Обновите страницу при подключении к интернету.';});
connection();render();
