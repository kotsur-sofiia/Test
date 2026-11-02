/* Personal day map. Removing a card never removes its diary or notes. */
'use strict';
(() => {
  const topics = [
    {id:'affirmation', title:'Аффирмация', hint:'Добрые слова для себя', icon:'♡'},
    {id:'cycle', title:'Цикл', hint:'Календарь и самочувствие', icon:'◌', href:'#cycle'},
    {id:'sleep', title:'Отдых', hint:'Сон и восстановление', icon:'☾', href:'#sleep'},
    {id:'food', title:'Питание', hint:'Продукты и баланс за день', icon:'♧', href:'#food'},
    {id:'water', title:'Вода', hint:'Маленькие глотки заботы', icon:'♧', href:'#water-form'},
    {id:'skin', title:'Кожа', hint:'Уход и твои наблюдения', icon:'✧', prompt:'Как чувствует себя кожа?', placeholder:'Уход, ощущения, что подошло сегодня…'},
    {id:'books', title:'Книги', hint:'Страницы, мысли и открытия', icon:'▤', prompt:'Что ты читаешь?', placeholder:'Название книги, прочитанные страницы, мысль на память…'},
    {id:'activity', title:'Движение', hint:'Тренировки и активность', icon:'↗', href:'#activity'}
  ];
  const initialOrder = ['affirmation','cycle','sleep','food','water'];
  const grid = $('#day-widgets');
  const picker = $('#widget-picker');
  const notesDialog = $('#widget-notes');
  const nodes = new Map([...grid.children].map(node => [node.dataset.widgetId, node]));
  let editing = false;
  let noteTopic = null;
  const drafts = new Map();

  function readMap() {
    const saved = state.dayMap && typeof state.dayMap === 'object' ? state.dayMap : {};
    const custom = [];
    if (Array.isArray(saved.custom)) for (const topic of saved.custom) {
      if (typeof topic?.id !== 'string' || !topic.id.startsWith('custom-') || typeof topic.title !== 'string' || !topic.title.trim() || custom.some(t => t.id === topic.id)) continue;
      custom.push({id:topic.id, title:topic.title.trim().slice(0,40)});
    }
    const known = new Set([...topics,...custom].map(t => t.id));
    const order = Array.isArray(saved.order) ? [...new Set(saved.order.filter(id => known.has(id)))] : [...initialOrder];
    // Keep notes for removed cards, including any unknown future topics.
    const notes = Array.isArray(saved.notes) ? saved.notes.filter(n => typeof n?.id === 'string' && typeof n.topic === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(n.date) && typeof n.text === 'string') : [];
    return {...saved, version:1, order, custom, notes};
  }

  function catalog(map = readMap()) {
    return [...topics, ...map.custom.map(t => ({...t, hint:'Твоя личная тема', icon:'✧', prompt:'Что хочется запомнить?', placeholder:'Несколько слов о своём дне…'}))];
  }
  function available(id) { return id !== 'cycle' || $('#cycle').dataset.available !== 'false'; }
  function announce(text, error = false) {
    for (const id of ['day-builder-status','widget-picker-status']) {
      const element = $('#'+id);
      element.textContent = text;
      element.classList.toggle('error', error);
    }
  }
  function commit(next, message) {
    const old = state.dayMap;
    state.dayMap = next;
    if (!save()) {
      if (old === undefined) delete state.dayMap; else state.dayMap = old;
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
    const link = document.createElement(topic.href ? 'a' : 'button');
    link.className = 'mini';
    if (topic.href) link.href = topic.href;
    else { link.type = 'button'; link.onclick = () => openNotes(topic.id); }
    link.append(textEl('span',topic.title.toLocaleUpperCase('ru')), textEl('strong',topic.hint), textEl('p',topic.href ? 'Открыть дневник' : 'Добавить заметку'));
    card.append(link);
    nodes.set(topic.id, card);
    return card;
  }

  function addControls(card, topic) {
    if (card.querySelector('.widget-controls')) return;
    const controls = document.createElement('div');
    controls.className = 'widget-controls';
    controls.setAttribute('role','group');
    controls.setAttribute('aria-label','Настроить: '+topic.title);
    for (const [action, text, label, delta] of [['up','↑','Выше',-1],['down','↓','Ниже',1],['remove','×','Убрать',0]]) {
      const control = button(label+': '+topic.title,text,() => {
        const map = readMap(), index = map.order.indexOf(topic.id);
        if (index < 0) return;
        if (!delta) {
          map.order.splice(index,1);
          if (commit(map,'Виджет убран. Записи сохранены; его можно вернуть через «Добавить».')) $('#edit-day').focus({preventScroll:true});
        } else {
          const target = index + delta;
          if (target < 0 || target >= map.order.length) return;
          [map.order[index],map.order[target]] = [map.order[target],map.order[index]];
          if (commit(map,'Порядок виджетов сохранён.')) {
            const current = card.querySelector('[data-action="'+action+'"]');
            (current.disabled ? card.querySelector('[data-action="remove"]') : current).focus({preventScroll:true});
          }
        }
      });
      control.dataset.action = action;
      controls.append(control);
    }
    card.prepend(controls);
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
      addControls(card, topic);
      const selected = map.order.includes(id);
      card.hidden = !selected || !editing && !available(id);
      if (!card.hidden) visibleCount++;
      card.classList.toggle('widget-unavailable', !available(id));
      card.querySelector('.widget-controls').hidden = !editing;
      card.querySelector('[data-action="up"]').disabled = map.order.indexOf(id) === 0;
      card.querySelector('[data-action="down"]').disabled = map.order.indexOf(id) === map.order.length-1;
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
    $('#edit-day').hidden = map.order.length === 0;
    $('#edit-day').textContent = editing ? 'Готово' : 'Изменить';
    $('#edit-day').setAttribute('aria-pressed',String(editing));
    grid.classList.toggle('is-editing',editing);
    $('#day-edit-help').hidden = !editing;
    if (picker.open) renderPicker();
    if (notesDialog.open) renderNotes();
  }

  function renderPicker() {
    const map = readMap(), list = $('#widget-options');
    list.replaceChildren();
    for (const topic of catalog(map)) {
      const added = map.order.includes(topic.id);
      const choice = button((added ? 'Добавлен: ' : 'Добавить: ')+topic.title,'',() => {
        const next = readMap();
        if (next.order.includes(topic.id) || !available(topic.id)) return;
        next.order.push(topic.id);
        if (commit(next,'«'+topic.title+'» добавлен в карту дня.')) {
          const focus = list.querySelector('button:not(:disabled)') || picker.querySelector('[data-close-dialog]');
          focus.focus({preventScroll:true});
        }
      });
      choice.className = 'widget-choice';
      choice.dataset.topic = topic.id;
      choice.disabled = added || !available(topic.id);
      const icon = textEl('span',topic.icon,'widget-choice-icon');
      icon.setAttribute('aria-hidden','true');
      const body = document.createElement('span');
      body.append(textEl('strong',topic.title),textEl('small',!available(topic.id) ? 'Недоступен по сведениям анкеты' : topic.hint));
      choice.append(icon,body,textEl('span',added ? '✓' : '+','widget-choice-add'));
      list.append(choice);
    }
  }

  function openNotes(id) {
    const topic = catalog().find(t => t.id === id);
    if (!topic) return;
    noteTopic = id;
    const draft = drafts.get(id);
    $('#widget-notes-title').textContent = topic.title;
    $('#widget-note-label').textContent = topic.prompt;
    $('#widget-note-text').placeholder = topic.placeholder;
    $('#widget-note-date').value = draft?.date || localDate();
    $('#widget-note-text').value = draft?.text || '';
    $('#widget-note-status').textContent = '';
    renderNotes();
    notesDialog.showModal();
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

  const help = textEl('p','Стрелками меняй порядок. Крестик убирает только виджет — записи остаются.','fine');
  help.id = 'day-edit-help'; help.hidden = true;
  $('#day-widgets').before(help);
  $('#edit-day').onclick = () => { editing = !editing; render(); };
  for (const id of ['add-widget','add-widget-top']) $('#'+id).onclick = () => { announce(''); renderPicker(); picker.showModal(); };
  $('#custom-widget-form').onsubmit = event => {
    event.preventDefault();
    const title = $('#custom-widget-title').value.trim();
    if (!title) { $('#custom-widget-title').setCustomValidity('Введи название темы.'); $('#custom-widget-title').reportValidity(); return; }
    const map = readMap();
    if (map.custom.length >= 30) { announce('Можно создать до 30 своих тем. Готовые темы доступны выше.',true); return; }
    const id = 'custom-'+crypto.randomUUID();
    map.custom.push({id,title}); map.order.push(id);
    if (commit(map,'Тема «'+title+'» добавлена.')) $('#custom-widget-title').value = '';
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
  for (const dialog of [picker,notesDialog]) {
    dialog.querySelector('[data-close-dialog]').onclick = () => dialog.close();
    dialog.addEventListener('click', event => { if (event.target === dialog) { const b = dialog.getBoundingClientRect(); if (event.clientX < b.left || event.clientX > b.right || event.clientY < b.top || event.clientY > b.bottom) dialog.close(); } });
  }
  notesDialog.addEventListener('close',() => {
    if (noteTopic) drafts.set(noteTopic,{date:$('#widget-note-date').value,text:$('#widget-note-text').value});
    noteTopic = null;
  });
  grid.addEventListener('click',event => {
    const link = event.target.closest('a.mini');
    if (!link) return;
    if (link.getAttribute('aria-disabled') === 'true') { event.preventDefault(); return; }
    if (['#food','#water-form'].includes(link.hash)) {
      $('#food-date').value = localDate(); renderFood(); window.LunaVoice?.refresh();
    }
  });
  window.addEventListener('hashchange',() => {
    for (const dialog of [picker,notesDialog]) if (dialog.open) dialog.close();
    render();
  });
  document.addEventListener('visibilitychange',() => { if (!document.hidden) render(); });
  window.WomanDayMap = Object.freeze({render, refreshDay:render});
  render();
})();
