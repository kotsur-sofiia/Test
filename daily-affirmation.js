/* Calendar-based rotation, independent of storage, time zone offsets and network. */
'use strict';
(() => {
 const phrases=Object.freeze([
 'Я достойна любви и заботы — в том числе своей собственной.',
 'Я могу выбирать свой ритм и бережно относиться к себе.',
 'Моя ценность не зависит от того, сколько я успела сегодня.',
 'Я разрешаю себе отдыхать и восстанавливать силы.',
 'Я учусь слышать своё тело с вниманием и добротой.',
 'Мне не нужно быть идеальной, чтобы любить себя.',
 'Я могу говорить о своих потребностях и просить поддержки.',
 'Сегодня я выбираю быть на своей стороне.',
 'Моим чувствам есть место, и я могу относиться к ним бережно.',
 'Я заслуживаю уважения — и от других, и от себя.',
 'Я могу заботиться о себе маленькими шагами.',
 'Моё тело заслуживает заботы без сравнений и критики.',
 'Я разрешаю себе меняться и узнавать себя заново.',
 'Я могу поставить паузу и спросить себя: что мне сейчас нужно?',
 'Я благодарна себе за каждый шаг навстречу своему благополучию.',
 'Мне можно выбирать то, что поддерживает именно меня.',
 'Я могу быть мягкой к себе и уверенной в своих границах.',
 'Я принимаю себя не только в сильные, но и в уязвимые дни.',
 'Я оставляю место для радости в своём обычном дне.',
 'Сегодня достаточно одного доброго поступка по отношению к себе.',
 'Я имею право на своё пространство, время и тишину.',
 'Я могу замечать свои достижения без обесценивания.',
 'Я достойна заботы на каждом этапе своей жизни.',
 'Я выбираю поддерживать себя добрыми словами.',
 'Я могу отпускать ожидания, которые мне больше не подходят.',
 'Я разрешаю себе получать удовольствие от простых вещей.',
 'У меня есть право сказать «нет» и сохранить свои силы.',
 'Я могу идти своим путём, не сравнивая его с чужим.',
 'Моё внимание к себе — ценно, даже если это всего несколько минут.',
 'Я заслуживаю отношений с собой, в которых есть тепло.',
 'Сегодня я могу начать с заботы, а не с требований к себе.'
 ]);
 function dayKey(date){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;}
 function forDate(date){const n=Math.floor(Date.UTC(date.getFullYear(),date.getMonth(),date.getDate())/86400000);return phrases[((n%phrases.length)+phrases.length)%phrases.length];}
 let timer;
 function refresh(){const now=new Date(),text=document.getElementById('daily-affirmation');if(text){text.textContent=forDate(now);text.dataset.date=dayKey(now);}renderCurrentDate(now);clearTimeout(timer);const next=new Date(now.getFullYear(),now.getMonth(),now.getDate()+1);timer=setTimeout(refresh,Math.max(1000,next-now+50));}
 window.LifeAffirmation=Object.freeze({forDate,dayKey});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});window.addEventListener('pageshow',refresh);window.addEventListener('hashchange',refresh);refresh();
})();
