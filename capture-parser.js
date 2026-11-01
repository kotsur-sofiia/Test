/* Local, conservative Russian diary extraction. No remote language model. */
(function(root){
 'use strict';
 const words={ноль:0,один:1,одна:1,одну:1,час:1,два:2,две:2,три:3,четыре:4,пять:5,шесть:6,семь:7,восемь:8,девять:9,десять:10,одиннадцать:11,двенадцать:12,тринадцать:13,четырнадцать:14,пятнадцать:15,шестнадцать:16,семнадцать:17,восемнадцать:18,девятнадцать:19,двадцать:20,тридцать:30,сорок:40,пятьдесят:50,шестьдесят:60,семьдесят:70,восемьдесят:80,девяносто:90,сто:100,двести:200,триста:300,четыреста:400,пятьсот:500,шестьсот:600,семьсот:700,восемьсот:800,девятьсот:900,восьми:8,шести:6,семи:7,девяти:9,десяти:10,одиннадцати:11,двенадцати:12};
 function normalize(text){return text.toLowerCase().replace(/ё/g,'е').replace(/([0-9]),([0-9])/g,'$1.$2').replace(/[а-я]+(?:\s+[а-я]+)*/g,phrase=>{const parts=phrase.split(/\s+/);let out=[],n=null;for(const word of parts){if(Object.hasOwn(words,word)&&word!=='час'){n=(n??0)+words[word];}else{if(n!==null){out.push(String(n));n=null;}out.push(word);}}if(n!==null)out.push(String(n));return out.join(' ');});}
 const aliases={salmon:/лосос|семг/,rice:/рис(?:а|ом|у)?(?:\s|$)/,broccoli:/брокколи/,oats:/овсян|овсян[а-я]*|овсяны/,egg:/яйц/,lentils:/чечевиц/,spinach:/шпинат/,yogurt:/йогурт/,banana:/банан/,orange:/апельсин/,almonds:/миндал/};
 function matchProduct(name,products){const matches=products.filter(p=>normalize(p.name)===name.trim());if(matches.length===1)return matches[0].id;for(const [id,re]of Object.entries(aliases))if(re.test(name)&&products.some(p=>p.id===id))return id;const candidates=products.filter(p=>name.trim().length>=4&&normalize(p.name).includes(name.trim()));return candidates.length===1?candidates[0].id:'';}
 function shift(date,n){const d=new Date(date+'T12:00:00');d.setDate(d.getDate()+n);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
 function clock(text){const m=text.match(/(?:^|\s)(\d{1,2})(?::(\d{2})|\s+час(?:а|ов)?\s+(\d{1,2})\s*мин(?:ут[а-я]*)?)?(?:\s|$)/);if(!m||+m[1]>23||+(m[2]||m[3]||0)>59)return '';let hour=+m[1];if(/вечер|дня/.test(text)&&hour<12)hour+=12;if(/ночи/.test(text)&&hour===12)hour=0;return `${String(hour).padStart(2,'0')}:${String(m[2]||m[3]||'00').padStart(2,'0')}`;}
 function parse(text,date,products=[]){
  const entries=[];let foodContext=false;
  // Commas between decimal digits remain decimal; each named portion becomes a separate item.
  const clauses=normalize(text).split(/[,;!\n]+|\.(?!\d)|\s+(?:затем|потом|также)\s+|\s+и\s+(?=(?:сегодня\s+)?(?:спал|спала|проснул|уснул|ел\s|ела\s|съел|съела|тренир|была\s))/).map(s=>s.trim()).filter(Boolean);
  for(const clause of clauses){const day=/позавчера/.test(clause)?shift(date,-2):/вчера/.test(clause)?shift(date,-1):date;
   const base={date:day,text:clause};
   if(/(?:^|\s)не\s+(?:ел|ела|съел|съела|спал|спала|тренир|пил|пила)|планир|завтра|хочу|буду|не\s+проснул|не\s+уснул/.test(clause)){entries.push({...base,kind:'note'});foodContext=false;continue;}
   if(/спал|спала|сон\s+с|уснул|заснул|проснул|пробудил/.test(clause)){
    foodContext=false;const range=clause.match(/(?:с|со)\s+(.+?)\s+(?:до|по)\s+(.+)/);
    if(range){const a=clock(range[1]),b=clock(range[2]);const ambiguous=![range[1],range[2]].every(s=>/утра|ночи|вечер|дня|\d{1,2}:\d{2}/.test(s)||Number(s.match(/\d+/)?.[0])>12||Number(s.match(/\d+/)?.[0])===0);let start='',end='';if(a&&b&&!ambiguous){end=day+'T'+b;start=(a>=b?shift(day,-1):day)+'T'+a;}entries.push({...base,kind:'sleep',start,end,type:/дневн/.test(clause)?'nap':'night',warning:ambiguous?'Уточни даты и время: 8 может означать 08:00 или 20:00. День записи — день пробуждения.':''});}
    else {const time=clock(clause);entries.push({...base,kind:'sleep-event',event:/проснул|пробудил/.test(clause)?'wake':'bed',at:time?day+'T'+time:'',warning:'Отдельная отметка не входит в среднее сна. Проверь время, включая утро или вечер.'});}continue;
   }
   if(/трениров|силов|бегал|бегала|йог[аойу]|пилатес|плавал|кардио|прогулк/.test(clause)){foodContext=false;const hours=clause.match(/(\d+(?:\.\d+)?)\s*час/);const mins=clause.match(/(\d+(?:\.\d+)?)\s*мин/);entries.push({...base,kind:'workout',name:clause,minutes:hours||mins?(+(hours?.[1]||0)*60+ +(mins?.[1]||0)):/(?:^|\s)час(?:\s|$)/.test(clause)?60:''});continue;}
   if(/(?:выпил|выпила|пил|пила|вод[ауы])/.test(clause)&&/\d+(?:\.\d+)?\s*(?:мл|миллилитр|литр)/.test(clause)){foodContext=false;const m=clause.match(/(\d+(?:\.\d+)?)\s*(мл|миллилитр|литр)/);entries.push({...base,kind:'water',ml:+m[1]*(m[2]==='литр'?1000:1)});continue;}
   const eating=/(?:^|\s)(?:ел|ела|съел|съела|кушал|кушала|завтрак|обед|ужин)(?:\s|:|$)/.test(clause);
   if(eating)foodContext=true;
   const portions=[...clause.matchAll(/([^0-9]+?)\s+(\d+(?:\.\d+)?)\s*(килограмм[а-я]*|кг|грамм[а-я]*|г)(?=\s|$)/g)];
   if(portions.length&&(foodContext||portions.some(m=>matchProduct(m[1],products)))){
    let tail=clause;for(const m of portions){const name=m[1].replace(/^(?:сегодня\s+|вчера\s+|на\s+обед\s+|я\s+|ел[а]?\s+|съел[а]?\s+|и\s+)+/g,'').trim();entries.push({...base,kind:'food',name,product:matchProduct(name,products),grams:+m[2]*(/кг|килограмм/.test(m[3])?1000:1)});tail=tail.replace(m[0],'');}if(tail.trim())entries.push({...base,kind:'note',section:'food',text:tail.trim()});continue;
   }
   entries.push({...base,kind:'note',section:foodContext?'food':'activity'});
  }
  return entries;
 }
 const api={parse,normalize};if(typeof module!=='undefined')module.exports=api;root.LunaCaptureParser=api;
})(typeof window!=='undefined'?window:globalThis);
