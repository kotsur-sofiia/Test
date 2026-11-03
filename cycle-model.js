/* Calendar estimates only. A missed expected start never creates a new period. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WomanCycleModel=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
  'use strict';
  const names = {menstrual:'Менструальная фаза',follicular:'Фолликулярная фаза',ovulation:'Предполагаемая овуляция',luteal:'Лютеиновая фаза'};
  function serial(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const stamp = Date.parse(value+'T12:00:00Z');
    return Number.isFinite(stamp) && new Date(stamp).toISOString().slice(0,10) === value ? Math.floor(stamp/86400000) : null;
  }
  function snapshot({date,periods,length,periodLength,predict}) {
    const target = serial(date);
    const starts = (Array.isArray(periods)?periods:[]).filter(value => serial(value)!==null && serial(value)<=target).sort();
    const base = starts.at(-1);
    if (target === null || !base) return {status:'empty',date,day:null,phase:null,remaining:null,progress:0};
    const elapsed = target-serial(base), day = elapsed+1;
    const valid = Number.isInteger(length) && length>=21 && length<=45 && Number.isInteger(periodLength) && periodLength>=1 && periodLength<=10;
    if (!predict || !valid) return {status:'unavailable',date,base,day,phase:null,remaining:null,progress:valid?Math.min(1,elapsed/length):0};
    if (elapsed >= length) return {status:'awaiting',date,base,day,length,periodLength,phase:null,displayPhase:'luteal',displayPhaseName:names.luteal,remaining:0,overdue:elapsed-length,progress:1};
    const ov = Math.max(periodLength+2,length-14);
    const phase = day<=periodLength ? 'menstrual' : day<ov-1 ? 'follicular' : day<=ov+1 ? 'ovulation' : 'luteal';
    return {status:'estimated',date,base,day,length,periodLength,phase,phaseName:names[phase],remaining:length-elapsed,progress:elapsed/length};
  }
  function advice(s) {
    if (s.status !== 'estimated') return {
      summary:s.status==='empty'?'Отметь первый день последней менструации, чтобы видеть день цикла.':s.status==='awaiting'?'Новая менструация пока не отмечена. Подпись «лютеиновая фаза» сохраняется условно; ориентируйся на самочувствие.':'По сведениям анкеты календарная схема фаз сейчас неприменима.',
      tips:[{title:'Ориентируйся на ощущения',text:'Отмечай самочувствие, сон и необычные изменения. Не нужно подстраивать день под календарный прогноз.'},{title:'Сохраняй привычную заботу',text:'Регулярная еда, вода по жажде и достаточный отдых полезны независимо от предполагаемой фазы.'},{title:'Замечай изменения',text:'Если цикл изменился или симптомы мешают обычной жизни, обсуди это с врачом. При сильной боли или очень обильном кровотечении обратись за медицинской помощью.'}]
    };
    const focus = {
      menstrual:s.day<=2?'В первые дни оставь возможность для пауз. При дискомфорте выбирай посильную активность и привычные способы отдыха.':'Продолжай отмечать длительность и интенсивность выделений. Возвращайся к привычной нагрузке по самочувствию.',
      follicular:'Если энергии достаточно, запланируй приятное дело или привычную тренировку. Календарная фаза не обязывает быть активнее.',
      ovulation:'Сохраняй привычный ритм и замечай свои ощущения. По календарю нельзя подтвердить овуляцию или определить безопасные дни.',
      luteal:s.remaining<=7?'До ожидаемой менструации около недели или меньше. Если замечаешь усталость или ПМС, оставь больше времени для отдыха и запиши симптомы.':'Продолжай привычный режим. Если появляются изменения сна, настроения или аппетита, отмечай их без оценки и сравнивай со своим опытом.'
    };
    return {
      summary:'День '+s.day+' · '+names[s.phase].toLocaleLowerCase('ru')+' по календарной оценке. Выбирай то, что подходит твоему самочувствию.',
      tips:[{title:'Твой ритм сегодня',text:focus[s.phase]},{title:'Питание и вода',text:s.phase==='menstrual'?'Ешь регулярно и разнообразно: привычные источники белка, овощи и продукты с железом. Пей по жажде; добавки не назначаются по дню цикла.':'Регулярные приёмы пищи, разнообразие и вода по жажде поддерживают привычный ритм. Специальная диета по фазам не обязательна.'},{title:'Сон и самочувствие',text:'Оставь достаточно времени для сна. Если симптомы повторяются, записывай их; выраженные боль, перепады настроения или нарушения сна стоит обсудить с врачом.'}]
    };
  }
  return Object.freeze({snapshot,advice,names});
});
