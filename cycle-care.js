/* Clockwise cycle dial and an optional, explicitly requested server AI response. */
'use strict';
(() => {
  const model = window.WomanCycleModel;
  const ns = 'http://www.w3.org/2000/svg';
  const answers = new Map();
  let pending = null, sequence = 0, lastDay = localDate();
  function snapshot() { return model.snapshot({date:selected,periods:state.periods,length:state.cycleLength,periodLength:state.periodLength,predict:canPredictCycle(state.profile)}); }
  function key(s) { return JSON.stringify([s.date,s.base,s.day,s.length,s.periodLength,s.phase,s.status]); }
  function endpoint() {
    try {
      if (!window.WOMAN_CONFIG?.cycleGuidanceUrl) return null;
      const url = new URL(window.WOMAN_CONFIG.cycleGuidanceUrl,location.href);
      return url.protocol==='https:' || ['localhost','127.0.0.1'].includes(url.hostname) && url.protocol==='http:' ? url.href : null;
    } catch { return null; }
  }
  function cancel() { sequence++; pending?.controller.abort(); pending=null; }
  function days(n) { const t=n%100,d=n%10;return n+' '+(t>=11&&t<=14?'дней':d===1?'день':d>=2&&d<=4?'дня':'дней'); }
  function showTips(value) {
    $('#phase-description').textContent=value.summary;
    const list=$('#phase-tips');list.replaceChildren();
    for (const [index,tip] of value.tips.entries()) {
      const row=document.createElement('div');row.className='tip';
      const icon=textEl('span',['♡','♧','☾'][index]||'♡');icon.setAttribute('aria-hidden','true');
      const body=document.createElement('div');body.append(textEl('b',tip.title),textEl('p',tip.text));row.append(icon,body);list.append(row);
    }
  }
  function render() {
    const s=snapshot(), context=key(s), busy=pending?.key===context;
    if (pending && !busy) cancel();
    $('#cycle-start-action').hidden=false;
    $('#cycle-dial-day').textContent=s.day??'—';$('#cycle-dial').style.setProperty('--day-size',s.day>9999?'48px':s.day>999?'64px':'');
    const names={menstrual:'МЕНСТРУАЛЬНАЯ',follicular:'ФОЛЛИКУЛЯРНАЯ',ovulation:'ОВУЛЯТОРНАЯ',luteal:'ЛЮТЕИНОВАЯ'};
    $('#cycle-phase-name').textContent=names[s.displayPhase||s.phase]||(s.status==='empty'?'ОТМЕТЬ НАЧАЛО':'БЕЗ ПРОГНОЗА');
    $('#cycle-phase-word').textContent=s.phase||s.status==='awaiting'?'фаза':s.status==='empty'?'цикла':'фазы';
    const delayed=s.status==='awaiting'&&s.overdue>0;
    $('#cycle-dial-countdown').classList.toggle('is-delayed',delayed);
    $('#cycle-countdown-label').textContent=delayed?'ЗАДЕРЖКА':'до менструации';
    $('#cycle-countdown-value').textContent=delayed?days(s.overdue):s.remaining>0?'≈ '+days(s.remaining):s.status==='awaiting'?'ожидается сегодня':s.status==='empty'?'нет данных':'без прогноза';
    $('#cycle-dial-note').textContent=s.status==='awaiting'?'Лютеиновая фаза остаётся условной подписью до новой отметки менструации.':'Фаза и дата следующей менструации — ориентировочная оценка, а не подтверждение овуляции.';
    $('#cycle-dial').setAttribute('aria-label',[s.displayPhaseName||s.phaseName||'Фаза не определена',s.day?'День цикла '+s.day:'Нет отметки начала',$('#cycle-dial-countdown').textContent].join('. '));
    $('#cycle-dial').dataset.status=s.status;
    const progress=$('#cycle-dial-progress');progress.style.strokeDasharray=(s.progress*100)+' 100';
    const angle=s.progress*2*Math.PI-Math.PI/2;
    $('#cycle-dial-marker').setAttribute('cx',160+139*Math.cos(angle));$('#cycle-dial-marker').setAttribute('cy',160+139*Math.sin(angle));
    // Keep the cut stem on the groove and the leafy olive sprig along its tangent.
    $('#cycle-twig-marker').setAttribute('transform','translate('+(160+139*Math.cos(angle))+' '+(160+139*Math.sin(angle))+') rotate('+(angle*180/Math.PI+180)+')');
    const ticks=$('#cycle-dial-ticks');ticks.replaceChildren();
    for (let i=0;i<(s.length||28);i++) {
      const a=i/(s.length||28)*2*Math.PI-Math.PI/2,line=document.createElementNS(ns,'line');
      for (const [name,value] of Object.entries({x1:160+123*Math.cos(a),y1:160+123*Math.sin(a),x2:160+128*Math.cos(a),y2:160+128*Math.sin(a)})) line.setAttribute(name,value);
      ticks.append(line);
    }
    $('#phase-title').textContent=s.displayPhaseName||s.phaseName||'Забота о себе';
    const answer=answers.get(context);showTips(answer||model.advice(s));
    $('#cycle').dataset.guidanceSource=answer?'ai':'reference';
    const configured=Boolean(endpoint());
    $('#cycle-ai-request').hidden=!configured||s.status!=='estimated';
    $('#cycle-ai-request').disabled=Boolean(busy)||!navigator.onLine;
    $('#cycle-ai-request').textContent=busy?'Подбираем рекомендации…':answer?'Обновить рекомендации ИИ':'Подобрать рекомендации с ИИ';
    $('#cycle-ai-status').textContent=busy?'Подбираем мягкие подсказки для этого дня цикла.':!configured?'ИИ пока не подключён. Эти подсказки справочные.':!navigator.onLine?'Без интернета доступны справочные подсказки.':s.status==='estimated'?'По нажатию ИИ получит только день, предполагаемую фазу и обычную длительность цикла. Ответ не заменяет медицинскую консультацию.':'';
  }
  function refresh() { if ($('#cycle').hidden) { if(pending)cancel();return; } render(); }
  async function request() {
    const url=endpoint(), s=snapshot();
    if (!url || !navigator.onLine || s.status!=='estimated' || pending) return;
    const controller=new AbortController(), context=key(s), token=++sequence;
    pending={controller,key:context};render();
    const timeout=setTimeout(()=>controller.abort(),15000);
    try {
      const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store',signal:controller.signal,body:JSON.stringify({cycleDay:s.day,cycleLength:s.length,periodLength:s.periodLength,phase:s.phase})});
      if (!response.ok) throw new Error('Unavailable');
      const data=await response.json();
      if (data.source!=='ai'||typeof data.summary!=='string'||!data.summary.trim()||data.summary.length>1200||!Array.isArray(data.tips)||data.tips.length!==3||data.tips.some(t=>typeof t?.title!=='string'||!t.title.trim()||t.title.length>120||typeof t.text!=='string'||!t.text.trim()||t.text.length>1600)) throw new Error('Invalid response');
      if (token!==sequence||key(snapshot())!==context||$('#cycle').hidden) return;
      answers.set(context,data);if(answers.size>30)answers.delete(answers.keys().next().value);
      pending=null;render();$('#cycle-ai-status').textContent='Рекомендации подготовлены ИИ. Ориентируйся на своё самочувствие; это не диагноз и не назначение.';
    } catch {
      if(token!==sequence)return;
      answers.delete(context);pending=null;render();$('#cycle-ai-status').textContent='Не удалось получить ответ ИИ. Справочные подсказки остаются доступны — попробуй позже.';
    } finally { clearTimeout(timeout); }
  }
  function refreshDay() {
    const now=localDate();
    if(now!==lastDay){if(selected===lastDay)selected=now;lastDay=now;window.WomanPeriodEditor?.render();renderCycle();}
    else refresh();
  }
  $('#cycle-ai-request').onclick=request;
  window.addEventListener('offline',()=>{cancel();refresh();});window.addEventListener('online',refresh);
  window.WomanCycleCare=Object.freeze({render,refresh,refreshDay});
  render();
})();
