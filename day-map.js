/* Personal day map. Removing a card never removes its diary or notes. */
'use strict';
(() => {
  const topics = [
    {id:'membership', title:'Подписка', hint:'Возможности приложения', icon:'◇', href:'#membership'},
    {id:'cycle', title:'Цикл', hint:'Календарь и самочувствие', icon:'◌', href:'#cycle'},
    {id:'food', title:'Питание', hint:'Продукты и баланс за день', icon:'♧', href:'#food'},
    {id:'water', title:'Гидратация', hint:'Вода и выпитый объём', icon:'♧', href:'#water'},
    {id:'skin', title:'Кожа', hint:'Уход и твои наблюдения', icon:'✧', prompt:'Как чувствует себя кожа?', placeholder:'Уход, ощущения, что подошло сегодня…'},
    {id:'affirmation', title:'Аффирмации', hint:'Добрые слова для себя', icon:'♡', href:'#affirmation'},
    {id:'meditation', title:'Медитация', hint:'Практика и ощущения', icon:'☾', prompt:'Как прошла практика?', placeholder:'Практика, её длительность и ощущения после…'},
    {id:'books', title:'Книги', hint:'Страницы, мысли и открытия', icon:'▤', prompt:'Что ты читаешь?', placeholder:'Название книги, прочитанные страницы, мысль на память…'},
    {id:'activity', title:'Активность', hint:'Тренировки и движение', icon:'↗', href:'#activity'},
    {id:'drawing', title:'Рисование', hint:'Идеи и творческие заметки', icon:'✎', prompt:'Что хочется нарисовать или запомнить?', placeholder:'Идея, материалы, впечатления от рисования…'},
    {id:'sleep', title:'Отдых', hint:'Сон и восстановление', icon:'☾', href:'#sleep'}
  ];
  const initialOrder = ['cycle','food','skin','books'];
  const previousInitialOrder = ['cycle','food','water','skin','activity'];
  const grid = $('#day-widgets');
  const picker = $('#widget-picker');
  const nodes = new Map([...grid.children].map(node => [node.dataset.widgetId, node]));
  let noteTopic = null;
  let activeTopic = 'cycle';
  const drafts = new Map();

  function readMap() {
    const saved = state.dayMap && typeof state.dayMap === 'object' ? state.dayMap : {};
    const custom = [];
    if (Array.isArray(saved.custom)) for (const topic of saved.custom) {
      if (typeof topic?.id !== 'string' || !topic.id.startsWith('custom-') || typeof topic.title !== 'string' || !topic.title.trim() || custom.some(t => t.id === topic.id)) continue;
      custom.push({id:topic.id, title:topic.title.trim().slice(0,40)});
    }
    const known = new Set([...topics,...custom].map(t => t.id));
    let order = Array.isArray(saved.order) ? [...new Set(saved.order.filter(id => known.has(id)))] : [...initialOrder];
    // Refresh the old default once; preserve deliberately customised maps and all notes.
    if(saved.topicRailVersion!==1&&order.length===previousInitialOrder.length&&order.every((id,index)=>id===previousInitialOrder[index]))order=[...initialOrder];
    // Put cycle first on upgrade; later explicit ordering in this editor is retained.
    if (saved.version !== 2 && order.includes('cycle')) { order.splice(order.indexOf('cycle'),1); order.unshift('cycle'); }
    // Keep notes for removed cards, including any unknown future topics.
    const notes = Array.isArray(saved.notes) ? saved.notes.filter(n => typeof n?.id === 'string' && typeof n.topic === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(n.date) && typeof n.text === 'string') : [];
    return {...saved, version:2, topicRailVersion:1, order, custom, notes};
  }

  function catalog(map = readMap()) {
    return [...topics, ...map.custom.map(t => ({...t, hint:'Твоя личная тема', icon:'✧', prompt:'Что хочется запомнить?', placeholder:'Несколько слов о своём дне…'}))];
  }
  function available(id) { return id !== 'cycle' || $('#cycle').dataset.available !== 'false'; }
  function homeTopic() {
    const order = readMap().order.filter(available);
    return order.includes(activeTopic) ? activeTopic : order.includes('cycle') ? 'cycle' : order[0] || 'empty';
  }
  function announce(text, error = false) {
    for (const id of ['day-builder-status','widget-picker-status']) {
      const element = $('#'+id);
      element.textContent = text;
      element.classList.toggle('error', error);
    }
  }
  function commit(next, message) {
    const old = state.dayMap;
    const previousTopic = activeTopic;
    state.dayMap = next;
    if (!save()) {
      if (old === undefined) delete state.dayMap; else state.dayMap = old;
      activeTopic = previousTopic;
      window.LunaNavigation.refresh();
      render();
      announce('Не удалось сохранить изменения. Проверь свободное место и попробуй ещё раз.', true);
      return false;
    }
    announce(message);
    return true;
  }

  function button(label, text, action) {
    const element = textEl('button', text);
    element.type = 'button';
    element.setAttribute('aria-label', label);
    element.onclick = action;
    return element;
  }

  function makeCard(topic) {
    const card = document.createElement('article');
    card.className = 'day-widget';
    card.dataset.widgetId = topic.id;
    const link = document.createElement('a');
    link.className = 'mini';
    link.href = topic.href || '#'+topic.id;
    link.append(textEl('span',topic.title.toLocaleUpperCase('ru')), textEl('strong',topic.hint), textEl('p',topic.href ? 'Открыть дневник' : 'Добавить заметку'));
    card.append(link);
    nodes.set(topic.id, card);
    return card;
  }

  const iconPaths = {
    membership:'<path d="m12 3 9 9-9 9-9-9Z"/>',
    meditation:'<path d="M12 12c-5-8-9-6-9-2 0 6 6 9 9 9 3 0 9-3 9-9 0-4-4-6-9 2ZM12 12V4M9 5l3-2 3 2"/>',
    drawing:'<path d="m5 15-2 6 6-2L21 7l-4-4ZM14 6l4 4M5 15l4 4"/>',
    cycle:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="4" r="2" fill="currentColor" stroke="none"/>',
    food:'<path d="M5 3v6a3 3 0 0 0 6 0V3M8 3v18M19 21V3c-5 0-5 10 0 10"/>',
    water:'<path d="M12 3C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-12ZM8 15a4 4 0 0 0 4 4"/>',
    skin:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z"/>',
    activity:'<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    sleep:'<path d="M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11Z"/>',
    books:'<path d="M3 4h5c2 0 4 1 4 2 0-1 2-2 4-2h5v15h-5c-2 0-4 1-4 2 0-1-2-2-4-2H3ZM12 6v15"/>',
    affirmation:'<path d="M12 20 4 12C-2 5 7 0 12 7c5-7 14-2 8 5Z"/>'
  };
  const natureTiles={cycle:0,food:1,water:2,skin:3,affirmation:4,meditation:5,books:6,activity:7,drawing:8,sleep:9,membership:10};
  function natureIcon(element,id){const tile=natureTiles[id]??11;element.replaceChildren();element.classList.add('nature-topic-image');element.style.setProperty('--nature-x',(tile%4)*100/3+'%');element.style.setProperty('--nature-y',Math.floor(tile/4)*50+'%');}
  function decorate(card, topic) {
    const link = card.querySelector('.mini');
    if (!link.querySelector('.topic-orb')) {
      const orb = document.createElement('span');
      orb.className = 'topic-orb'; orb.setAttribute('aria-hidden','true');
      if (iconPaths[topic.id]) orb.innerHTML = '<svg viewBox="0 0 24 24">'+iconPaths[topic.id]+'</svg>';
      else orb.textContent = '✧';
      const label = link.querySelector('span'); label.className = 'topic-label'; label.textContent = topic.title.toLocaleUpperCase('ru');
      natureIcon(orb,topic.id);link.prepend(orb);
    }
    link.setAttribute('aria-label',topic.title);
  }
  function routeChanged(id) {
    if (catalog().some(t => t.id === id)) activeTopic = id;
    for (const [topic,node] of nodes) {
      const link = node.querySelector('.mini');
      link.classList.toggle('active',topic === id);
      if (topic === id) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    }
    const topic = catalog().find(t => t.id === id);
    if (topic && !topic.href) openNotes(id);
    else rememberDraft();
  }

  function summary(topic, map, date) {
    const notes = map.notes.filter(n => n.topic === topic.id && n.date === date);
    if (topic.id === 'cycle') {
      if (!available('cycle')) return ['Сейчас недоступен','Учитываются сведения из анкеты'];
      const phase = phaseAt(date);
      return phase ? ['День '+phase.day+' цикла',phases[phase.key].name] : ['Познакомимся?','Календарь и самочувствие'];
    }
    if (topic.id === 'sleep') {
      const records = state.sleep.filter(s => localDate(new Date(s.end)) === date);
      return records.length ? [duration(Math.round(records.reduce((sum,s) => sum+minutes(s),0))),'Сон за сегодня'] : ['Время отдохнуть','Ночной сон и маленькие паузы днём'];
    }
    if (topic.id === 'food') {
      const count = state.meals.filter(m => m.date === date).length;
      return [count ? 'Продуктов сегодня: '+count : 'Забота в тарелке','Продукты и баланс за день'];
    }
    if (topic.id === 'water') {
      const total = state.water.filter(w => w.date === date).reduce((sum,w) => sum+w.ml,0);
      return [total.toLocaleString('ru')+' мл','Выпито сегодня · без обязательной нормы'];
    }
    if (topic.id === 'activity') return ['Движение в своём ритме','Тренировки и заметки'];
    return [notes.length ? notes.at(-1).text : topic.hint, notes.length ? 'Записей сегодня: '+notes.length+' · открыть' : 'Добавить заметку'];
  }

  function render() {
    const map = readMap(), all = catalog(map), date = localDate();
    for (const [id,card] of nodes) if (!all.some(t => t.id === id)) { card.remove(); nodes.delete(id); }
    const ordered = [...map.order,...all.map(t => t.id).filter(id => !map.order.includes(id))];
    let visibleCount = 0;
    for (const id of ordered) {
      const topic = all.find(t => t.id === id);
      const card = nodes.get(id) || makeCard(topic);
      decorate(card,topic);
      const selected = map.order.includes(id);
      card.hidden = !selected || !available(id);
      if (!card.hidden) visibleCount++;
      card.classList.toggle('widget-unavailable', !available(id));
      if (id !== 'affirmation') {
        const link = card.querySelector('.mini');
        const [title,description] = summary(topic,map,date);
        link.querySelector('strong').textContent = title;
        link.querySelector('p').textContent = description;
        link.setAttribute('aria-disabled',String(!available(id)));
      }
      grid.append(card);
    }
    $('#day-empty').hidden = visibleCount > 0;
    if (picker.open) renderPicker();
    routeChanged(document.body.dataset.topic);
    if (noteTopic && !$('#topic-notes').hidden) renderNotes();
  }

  function focusEditorRow(id, action='toggle') {
    const row = [...$('#widget-options').children].find(node => node.dataset.topic === id);
    const target = row?.querySelector('[data-action="'+action+'"]');
    (target && !target.disabled ? target : row?.querySelector('[data-action="toggle"]'))?.focus({preventScroll:true});
  }
  function toggleTopic(id) {
    const map=readMap(),index=map.order.indexOf(id),enabled=index>=0;
    if (!enabled && !available(id)) return;
    if (enabled) map.order.splice(index,1);
    else if (id==='cycle') map.order.unshift(id);
    else map.order.push(id);
    if (commit(map,enabled?'Тема выключена. Все записи сохранены.':'Тема включена.')) {
      if (enabled && activeTopic===id) { history.replaceState(null,'','#home'); window.LunaNavigation.refresh(); }
      focusEditorRow(id);
    }
  }
  function saveTopicOrder(order,id){
    const map=readMap();
    if(order.length!==map.order.length||new Set(order).size!==order.length||order.some(topic=>!map.order.includes(topic))){renderPicker();return;}
    if(order.every((topic,index)=>topic===map.order[index])){announce('Порядок тем не изменён.');return;}
    map.order=order;if(commit(map,'Порядок тем сохранён.'))focusEditorRow(id,'reorder');
  }
  function renderPicker() {
    reordering.cancel();
    const map=readMap(),list=$('#widget-options'),all=catalog(map),scroll=picker.scrollTop;
    list.replaceChildren();
    const order=[...map.order,...all.map(t=>t.id).filter(id=>!map.order.includes(id))];
    for(const id of order){
      const topic=all.find(t=>t.id===id),index=map.order.indexOf(id),enabled=index>=0;
      const row=document.createElement('div');row.className='topic-editor-row'+(enabled?' is-enabled':'');row.dataset.topic=id;
      const info=document.createElement('div');info.className='topic-editor-info';
      const description=document.createElement('div');description.className='topic-editor-description';
      description.append(textEl('strong',topic.title.toLocaleUpperCase('ru')));description.title=topic.title;
      info.append(description);
      const toggle=button((enabled?'Выключить: ':'Включить: ')+topic.title,'',()=>toggleTopic(id));
      toggle.className='topic-toggle';toggle.dataset.action='toggle';toggle.setAttribute('role','switch');toggle.setAttribute('aria-checked',String(enabled));
      toggle.disabled=!enabled&&!available(id);const track=document.createElement('span');track.className='switch-track';track.setAttribute('aria-hidden','true');track.append(textEl('span','','switch-knob'));toggle.append(track);info.append(toggle);row.append(info);
      if(toggle.disabled)toggle.setAttribute('aria-label',topic.title+' — недоступен по сведениям анкеты');
      if(enabled){
        const grip=button('Переместить: '+topic.title,'⠿',()=>{});grip.className='topic-drag-handle';grip.dataset.action='reorder';grip.setAttribute('aria-pressed','false');grip.setAttribute('aria-describedby','topic-reorder-help');info.prepend(grip);
      }
      list.append(row);
    }
    picker.scrollTop=scroll;
  }

  function openNotes(id) {
    const topic = catalog().find(t => t.id === id);
    if (!topic) return;
    if (noteTopic === id) return;
    rememberDraft();
    noteTopic = id;
    const draft = drafts.get(id);
    $('#widget-notes-title').textContent = topic.title;
    $('#widget-note-label').textContent = topic.prompt;
    $('#widget-note-text').placeholder = topic.placeholder;
    $('#widget-note-date').value = draft?.date || localDate();
    $('#widget-note-text').value = draft?.text || '';
    $('#widget-note-status').textContent = '';
    renderNotes();
  }
  function rememberDraft() {
    if (noteTopic) drafts.set(noteTopic,{date:$('#widget-note-date').value,text:$('#widget-note-text').value});
    noteTopic = null;
  }
  function renderNotes() {
    const list = $('#widget-note-history'), date = $('#widget-note-date').value;
    list.replaceChildren();
    const notes = readMap().notes.filter(n => n.topic === noteTopic && n.date === date);
    if (!notes.length) list.append(textEl('p','Здесь появятся твои записи за выбранный день.','fine'));
    for (const note of [...notes].reverse()) {
      const row = document.createElement('div');
      row.className = 'widget-note';
      row.append(textEl('p',note.text));
      row.append(button('Удалить заметку: '+note.text.slice(0,40),'×',() => {
        const next = readMap();
        next.notes = next.notes.filter(n => n.id !== note.id);
        const ok = commit(next,'Заметка удалена.');
        $('#widget-note-status').textContent = ok ? 'Заметка удалена.' : 'Не удалось удалить заметку. Попробуй ещё раз.';
      }));
      list.append(row);
    }
  }

  $('#add-widget').onclick = () => { announce(''); renderPicker(); picker.showModal(); };
  function showCustom(show) { $('#custom-widget-form').hidden=!show;$('#show-custom-widget').setAttribute('aria-expanded',String(show));if(show)$('#custom-widget-title').focus(); }
  $('#show-custom-widget').onclick=()=>showCustom($('#custom-widget-form').hidden);
  $('#cancel-custom-widget').onclick=()=>{showCustom(false);$('#show-custom-widget').focus();};
  $('#custom-widget-form').onsubmit = event => {
    event.preventDefault();
    const title = $('#custom-widget-title').value.trim();
    if (!title) { $('#custom-widget-title').setCustomValidity('Введи название темы.'); $('#custom-widget-title').reportValidity(); return; }
    const map = readMap();
    if (map.custom.length >= 30) { announce('Можно создать до 30 своих тем. Готовые темы доступны выше.',true); return; }
    const id = 'custom-'+crypto.randomUUID();
    map.custom.push({id,title}); map.order.push(id);
    if (commit(map,'Тема «'+title+'» добавлена.')) { $('#custom-widget-title').value='';showCustom(false);focusEditorRow(id); }
  };
  $('#custom-widget-title').oninput = event => event.target.setCustomValidity('');
  $('#widget-note-date').onchange = renderNotes;
  $('#widget-note-form').onsubmit = event => {
    event.preventDefault();
    const text = $('#widget-note-text').value.trim(), date = $('#widget-note-date').value;
    if (!text || !date || !noteTopic) return;
    const map = readMap();
    map.notes.push({id:crypto.randomUUID(), topic:noteTopic, date, text});
    if (commit(map,'Заметка сохранена.')) {
      $('#widget-note-text').value = '';
      drafts.delete(noteTopic);
      $('#widget-note-status').textContent = 'Заметка сохранена.';
    } else $('#widget-note-status').textContent = 'Не удалось сохранить заметку. Текст остался в поле — попробуй ещё раз.';
  };
  for (const dialog of [picker]) {
    dialog.querySelector('[data-close-dialog]').onclick = () => dialog.close();
    dialog.addEventListener('click', event => { if (event.target === dialog) { const b = dialog.getBoundingClientRect(); if (event.clientX < b.left || event.clientX > b.right || event.clientY < b.top || event.clientY > b.bottom) dialog.close(); } });
  }
  grid.addEventListener('click',event => {
    const link = event.target.closest('a.mini');
    if (!link) return;
    if (link.getAttribute('aria-disabled') === 'true') { event.preventDefault(); return; }
    if (['#food','#water'].includes(link.hash)) {
      $('#food-date').value = localDate(); renderFood(); window.LunaVoice?.refresh();
    }
  });
  window.addEventListener('hashchange',() => {
    if (picker.open) picker.close();
    render();
  });
  document.addEventListener('visibilitychange',() => { if (!document.hidden) render(); });
  const reordering=WomanTopicReorder.attach({list:$('#widget-options'),dialog:picker,onDrop:saveTopicOrder,announce});
  window.WomanDayMap = Object.freeze({render, homeTopic, routeChanged, refreshDay:() => { render(); window.WomanCycleCare?.refreshDay(); }});
  render();
  window.LunaNavigation.refresh();
})();
