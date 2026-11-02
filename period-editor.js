/* Explicit start/end records. An unknown end is never filled from an average. */
'use strict';
(() => {
  const dates=window.WomanPeriodDates;
  const dialog=$('#period-dialog');
  let loadedStart=null,endDirty=false;
  const text=id=>$('#period-'+id),picker=id=>$('#period-'+id+'-calendar');
  function read(id) { return dates.parse(text(id).value); }
  function set(id,iso) { text(id).value=dates.format(iso);picker(id).value=iso||''; }
  function load(start) {loadedStart=start;set('start',start);set('end',state.periodEnds[start]||null);endDirty=false;}
  function open(start) {if(start)load(start);if(!dialog.open)dialog.showModal();}
  function close() {if(dialog.open)dialog.close();}
  $('#cycle-start-action').onclick=()=>open();
  $('#period-dialog-close').onclick=close;
  function sync(id) {
    const iso=read(id);picker(id).value=iso||'';
    if(iso)text(id).value=dates.format(iso);
    if(id==='start'&&iso!==loadedStart){if(!endDirty)set('end',state.periodEnds[iso]||null);loadedStart=iso;}
  }
  for(const id of ['start','end']) {
    text(id).addEventListener('input',()=>{if(id==='end')endDirty=true;$('#period-form-error').textContent='';if(/^\d{8}$/.test(text(id).value))sync(id);});
    text(id).addEventListener('blur',()=>sync(id));
    picker(id).addEventListener('change',()=>{if(id==='end')endDirty=true;set(id,picker(id).value);sync(id);$('#period-form-error').textContent='';});
    picker(id).addEventListener('click',()=>{try{picker(id).showPicker?.();}catch{picker(id).focus();}});
  }
  function render() {
    for(const id of ['start','end'])picker(id).max=localDate();
    const history=$('#period-history');history.replaceChildren();
    for(const start of [...state.periods].filter(dates.validISO).sort().reverse()){
      const end=state.periodEnds[start],row=document.createElement('div');row.className='period-record';
      const description=document.createElement('div');description.className='period-record-copy';
      description.append(textEl('strong','Начало: '+dates.format(start)),textEl('p',dates.validISO(end)?'Окончание: '+dates.format(end)+' · '+dates.days(start,end)+' дн.':'Окончание не отмечено','fine'));
      row.append(description);
      const actions=document.createElement('div');actions.className='period-record-actions';
      const edit=textEl('button','Изменить');edit.type='button';edit.setAttribute('aria-label','Изменить даты '+dates.format(start));edit.onclick=()=>{open(start);$('#period-form-status').textContent='Измени даты и нажми «Сохранить даты».';text('start').focus();};
      actions.append(edit,removeButton('Удалить отметку '+start,()=>{
        const old={periods:state.periods,ends:state.periodEnds};state.periods=old.periods.filter(value=>value!==start);state.periodEnds={...old.ends};delete state.periodEnds[start];
        if(!save()){state.periods=old.periods;state.periodEnds=old.ends;refreshAll();$('#period-form-error').textContent='Не удалось удалить запись. Попробуй ещё раз.';return;}
        $('#period-form-status').textContent='Запись удалена.';
      }));row.append(actions);history.append(row);
    }
  }
  function refreshAll(){renderCycle();renderProfile();window.LunaNavigation.refresh();window.WomanDayMap?.render();}
  $('#cycle-form').onsubmit=event=>{
    event.preventDefault();sync('start');sync('end');
    const start=read('start'),end=read('end');
    let error=dates.validate({start,end:text('end').value.trim()?end||'invalid':null,periods:state.periods,ends:state.periodEnds,today:localDate()});
    $('#period-form-error').textContent=error;$('#period-form-status').textContent='';if(error)return;
    const old={periods:state.periods,ends:state.periodEnds,selected};
    state.periods=state.periods.includes(start)?state.periods:[...state.periods,start];state.periodEnds={...state.periodEnds};
    if(end)state.periodEnds[start]=end;else delete state.periodEnds[start];
    selected=localDate();
    if(!save()){
      state.periods=old.periods;state.periodEnds=old.ends;selected=old.selected;refreshAll();
      $('#period-form-error').textContent='Не удалось сохранить даты. Введённые значения остались в полях — попробуй ещё раз.';return;
    }
    loadedStart=start;endDirty=false;$('#period-form-status').textContent='Даты сохранены.';
    $('#cycle-period-status').textContent='Даты сохранены.';close();
  };
  load([...state.periods].filter(value=>dates.validISO(value)&&value<=localDate()).sort().at(-1)||localDate());
  window.WomanPeriodEditor=Object.freeze({render,open,close});render();
})();
