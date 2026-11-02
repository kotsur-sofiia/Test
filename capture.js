/* Review and commit one dictation to the existing local diaries. */
'use strict';
(() => {
 for(const key of ['sleepEvents','workouts'])if(!Array.isArray(state[key]))state[key]=[];
 const root=$('[data-voice-section="capture"]'),editor=root.querySelector('.voice-editor'),date=root.querySelector('.voice-date');
 date.max=today;
 const review=$('#capture-review'),items=$('#capture-items'),message=$('#capture-status'),links=$('#capture-links');let drafts=[];
 const titles={food:'Питание',sleep:'Сон', 'sleep-event':'Отметка сна',workout:'Тренировка',water:'Вода',note:'Заметка'};
 function input(card,label,type,value,key){const l=textEl('label',label);const field=document.createElement(type==='textarea'?'textarea':'input');if(type!=='textarea')field.type=type;field.value=value??'';field.dataset.field=key;if(type==='number'){field.min='0';field.step='any';field.inputMode='decimal';}l.append(field);card.append(l);return field;}
 function select(card,label,key,options,value){const l=textEl('label',label),field=document.createElement('select');field.dataset.field=key;for(const [v,t]of options){const o=textEl('option',t);o.value=v;field.append(o);}field.value=value;l.append(field);card.append(l);return field;}
 function validDay(day){return /^\d{4}-\d{2}-\d{2}$/.test(day)&&Number.isFinite(+parseDay(day))&&localDate(parseDay(day))===day&&day<=localDate();}
 function invalidate(){review.hidden=true;drafts=[];message.textContent='';links.replaceChildren();}
 editor.addEventListener('input',invalidate);date.addEventListener('change',invalidate);
 function analyze(){if(editor.readOnly)return;if(!editor.value.trim()){message.textContent='Сначала надиктуй или введи текст.';return;}if(!validDay(date.value)){message.textContent='Выбери корректную дату не позднее сегодняшней.';return;}
  drafts=LunaCaptureParser.parse(editor.value.trim(),date.value,allProducts());items.replaceChildren();links.replaceChildren();
  drafts.forEach((d,index)=>{const card=document.createElement('article');card.className='capture-item';card.dataset.index=index;const include=textEl('label','Добавить запись','capture-include'),box=document.createElement('input');box.type='checkbox';box.checked=true;box.dataset.field='include';include.prepend(box);card.append(textEl('h3',titles[d.kind]),include,textEl('p',d.text,'fine'));
   if(d.kind!=='note')select(card,'Формат записи','mode',[['structured','Запись для дневника'],['note','Только текстовая заметка']],'structured');
   const day=input(card,'Дата','date',d.date,'date');day.max=today;
   if(d.kind==='food'){select(card,'Продукт для расчёта','product',[['','Сохранить заметкой без расчёта'],...allProducts().map(p=>[p.id,p.name])],d.product);const grams=input(card,'Порция, граммов','number',d.grams,'grams');grams.min='1';grams.max='3000';if(!d.product)card.append(textEl('p','Точный продукт не определён. Выбери его из базы или оставь заметку без КБЖУ.','capture-warning'));}
   if(d.kind==='sleep'){select(card,'Тип сна','type',[['night','Ночной сон'],['nap','Дневной сон']],d.type);input(card,'Засыпание (дата и время)','datetime-local',d.start,'start');input(card,'Пробуждение (дата и время)','datetime-local',d.end,'end');}
   if(d.kind==='sleep-event'){select(card,'Событие','event',[['bed','Засыпание'],['wake','Пробуждение']],d.event);input(card,'Дата и время','datetime-local',d.at,'at');}
   if(d.kind==='workout'){input(card,'Тренировка','text',d.name,'name');const min=input(card,'Длительность, минут (если известна)','number',d.minutes,'minutes');min.max='1440';}
   if(d.kind==='water'){const ml=input(card,'Выпито, мл','number',d.ml,'ml');ml.min='1';ml.max='10000';}
   if(d.kind==='note')select(card,'Раздел','section',[['activity','Другие записи'],['food','Питание'],['sleep','Сон'],['cycle','Цикл']],d.section||'activity');
   if(d.warning)card.append(textEl('p',d.warning,'capture-warning'));
   input(card,'Текст записи','textarea',d.text,'text');items.append(card);
  });review.hidden=false;message.textContent=`Распределено записей: ${drafts.length}. Проверь значения и нажми «Добавить в дневники».`;
 }
 window.addEventListener('luna:capture-ready',analyze);
 function render(){
  function history(selector,entries,describe,key){const list=$(selector);list.replaceChildren();if(!entries.length)return;for(const entry of [...entries].sort((a,b)=>(b.date||b.at||'').localeCompare(a.date||a.at||''))){const row=textEl('div',describe(entry),'record');row.append(removeButton(`Удалить запись ${entry.id}`,()=>{const old=state[key];state[key]=old.filter(v=>v.id!==entry.id);if(!save()){state[key]=old;render();}else render();}));list.append(row);}}
  history('#sleep-events',state.sleepEvents,e=>`${e.event==='wake'?'Пробуждение':'Засыпание'} · ${fmtTime(e.at)} · отдельная отметка, без расчёта длительности`,'sleepEvents');
  history('#workout-history',state.workouts,e=>`${fmtDay(e.date)} · ${e.name}${e.minutes?' · '+e.minutes+' мин':''}`,'workouts');
  history('#general-history',state.voiceNotes.filter(e=>e.section==='activity'),e=>`${fmtDay(e.date)} · ${e.text}`,'voiceNotes');
 }
 review.onsubmit=e=>{e.preventDefault();const batch={meals:[],sleep:[],sleepEvents:[],workouts:[],water:[],voiceNotes:[]};const areas=new Set();try{
  for(const card of items.children){const get=key=>card.querySelector(`[data-field="${key}"]`)?.value;const d=drafts[Number(card.dataset.index)];if(!card.querySelector('[data-field="include"]').checked)continue;const day=get('date'),text=get('text')?.trim();if(!validDay(day))throw Error('Проверь дату записи.');if(!text||text.length>4000)throw Error('Текст записи должен содержать от 1 до 4000 символов.');const common={id:crypto.randomUUID(),date:day,text,source:'capture',transcript:editor.value.trim(),createdAt:new Date().toISOString()};
   function note(section){batch.voiceNotes.push({...common,section,updatedAt:common.createdAt});areas.add(section==='activity'?'activity':section);}
   if(get('mode')==='note'){note(d.kind==='food'||d.kind==='water'?'food':d.kind.startsWith('sleep')?'sleep':'activity');continue;}
   if(d.kind==='food'){const p=allProducts().find(p=>p.id===get('product'));if(!p){note('food');continue;}const grams=Number(get('grams'));if(!Number.isFinite(grams)||grams<1||grams>3000)throw Error('Порция должна быть от 1 до 3000 г.');batch.meals.push({...common,product:p.id,grams,snapshot:structuredClone(p)});areas.add('food');}
   else if(d.kind==='sleep'){const a=new Date(get('start')),b=new Date(get('end'));if(!get('start')||!get('end')||!Number.isFinite(+a)||!Number.isFinite(+b)||b<=a||b-a>86400000||b>new Date())throw Error('Проверь даты сна: пробуждение позже засыпания, не в будущем; длительность до 24 часов.');if([...state.sleep,...batch.sleep].some(s=>a<new Date(s.end)&&b>new Date(s.start)))throw Error('Этот сон пересекается с уже записанным промежутком.');batch.sleep.push({...common,date:localDate(b),start:a.toISOString(),end:b.toISOString(),type:get('type')});areas.add('sleep');}
   else if(d.kind==='sleep-event'){const at=new Date(get('at'));if(!get('at')||!Number.isFinite(+at)||at>new Date())throw Error('Проверь дату и время отметки сна: она не может быть в будущем.');batch.sleepEvents.push({...common,date:localDate(at),event:get('event'),at:at.toISOString()});areas.add('sleep');}
   else if(d.kind==='workout'){const raw=get('minutes'),mins=raw===''?null:Number(raw),name=get('name').trim();if(!name||name.length>500||mins!==null&&(!Number.isFinite(mins)||mins<=0||mins>1440))throw Error('Укажи название тренировки и длительность от 1 до 1440 минут или оставь её пустой.');batch.workouts.push({...common,name,minutes:mins});areas.add('activity');}
   else if(d.kind==='water'){const ml=Number(get('ml'));if(!Number.isInteger(ml)||ml<1||ml>10000)throw Error('Объём воды должен быть целым числом от 1 до 10000 мл.');batch.water.push({...common,ml,container:'glass'});areas.add('water');}
   else note(get('section'));
  }
  if(!areas.size)throw Error('Выбери хотя бы одну запись.');
  const old={};for(const key of Object.keys(batch)){old[key]=state[key];state[key]=[...state[key],...batch[key]];}
  if(!save()){Object.assign(state,old);render();window.LunaVoice.refresh();throw Error('Не удалось сохранить записи. Черновик оставлен: скопируй текст или попробуй ещё раз.');}
  const foodDay=batch.meals[0]?.date||batch.water[0]?.date||batch.voiceNotes.find(n=>n.section==='food')?.date;if(foodDay){$('#food-date').value=foodDay;$('#food-date').dispatchEvent(new Event('change'));}
  review.hidden=true;editor.value='';drafts=[];message.textContent='Записи добавлены в дневники.';links.replaceChildren();for(const area of areas){const a=textEl('a',{food:'Открыть питание',water:'Открыть воду',sleep:'Открыть сон',activity:'Открыть активность и заметки',cycle:'Открыть цикл'}[area],'text-link');a.href='#'+area;links.append(a);}render();
 }catch(error){message.textContent=error.message;}};
 window.LunaCapture=Object.freeze({render});render();
})();
