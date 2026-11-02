/* Calendar-based rotation, independent of storage, time zone offsets and network. */
'use strict';
(() => {
 const phrases=Object.freeze([
 'Я достойна любви и заботы.',
 'Я выбираю свой ритм.',
 'Моя ценность — во мне.',
 'Мне можно отдыхать.',
 'Я слышу своё тело.',
 'Мне можно быть собой.',
 'Я могу просить поддержки.',
 'Я на своей стороне.',
 'Мои чувства важны.',
 'Я заслуживаю уважения.',
 'Я забочусь о себе.',
 'Моё тело достойно заботы.',
 'Мне можно меняться.',
 'Я выбираю бережность.',
 'Я благодарна себе.',
 'Я выбираю то, что мне близко.',
 'Моя мягкость — моя сила.',
 'Я принимаю себя разной.',
 'Я оставляю место радости.',
 'Сегодня я добра к себе.',
 'Мне можно выбирать тишину.',
 'Мои достижения важны.',
 'Я достойна заботы всегда.',
 'Я говорю с собой по-доброму.',
 'Я отпускаю чужие ожидания.',
 'Я замечаю простые радости.',
 'Мои границы важны.',
 'Я иду своим путём.',
 'Моё внимание к себе ценно.',
 'Я отношусь к себе с теплом.',
 'Я выбираю заботу о себе.'
 ]);
 function dayKey(date){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;}
 function forDate(date){const n=Math.floor(Date.UTC(date.getFullYear(),date.getMonth(),date.getDate())/86400000);return phrases[((n%phrases.length)+phrases.length)%phrases.length];}
 let timer;
 function refresh(){const now=new Date(),text=document.getElementById('daily-affirmation');if(text){text.textContent=forDate(now);text.dataset.date=dayKey(now);}window.WomanDayMap?.refreshDay();clearTimeout(timer);const next=new Date(now.getFullYear(),now.getMonth(),now.getDate()+1);timer=setTimeout(refresh,Math.max(1000,next-now+50));}
 window.LifeAffirmation=Object.freeze({forDate,dayKey});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});window.addEventListener('pageshow',refresh);window.addEventListener('hashchange',refresh);refresh();
})();
