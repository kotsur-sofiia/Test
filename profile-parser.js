/* Conservative, local parsing of labelled Russian profile dictation. No network calls. */
'use strict';
(() => {
 const digits={ноль:0,нуль:0,один:1,одна:1,одно:1,два:2,две:2,три:3,четыре:4,пять:5,шесть:6,семь:7,восемь:8,девять:9,десять:10,одиннадцать:11,двенадцать:12,тринадцать:13,четырнадцать:14,пятнадцать:15,шестнадцать:16,семнадцать:17,восемнадцать:18,девятнадцать:19,двадцать:20,тридцать:30,сорок:40,пятьдесят:50,шестьдесят:60,семьдесят:70,восемьдесят:80,девяносто:90,сто:100,двести:200,триста:300,четыреста:400,пятьсот:500};
 const word=(text,pattern)=>new RegExp(`(?:^|[^\\p{L}])(?:${pattern})(?=$|[^\\p{L}])`,'u').test(text);
 function integerWords(text){const tokens=text.trim().split(/\s+/);const nums=tokens.map(t=>digits[t]);if(nums.some(n=>n===undefined)||!nums.length)return null;let i=0,total=0;if(nums[i]>=100){total+=nums[i++];if(i===nums.length)return total;}if(nums[i]<20){if(i!==nums.length-1)return null;return total+nums[i];}if(nums[i]<100){total+=nums[i++];if(i===nums.length)return total;if(nums[i]>0&&nums[i]<10&&i===nums.length-1)return total+nums[i];}return null;}

 function number(raw,key){let value=raw.toLowerCase().replaceAll('ё','е').trim();
  if(key==='weight'&&word(value,'грамм|грамма|граммов|гр|фунт|фунта|фунтов|lb|lbs'))return null;
  const unit=key==='age'?/^(.*?)(?:\s*(?:лет|года|год)(?=$|[^\p{L}]))/u:/^(.*?)(?:\s*(?:килограммов|килограмма|килограмм|килограммы|кило|кг)(?=$|[^\p{L}]))/u;
  const match=value.match(unit);if(match)value=match[1].trim();else if(key==='age'&&word(value,'месяц|месяца|месяцев|месяцы|мес'))return null;else value=value.split(/[;.!?\n]/)[0].replace(/,\s*(?:не\s+беременна|беременна|планирую|кормлю).*$/u,'').trim();
  if(word(value,'или|примерно|около|наверное|кажется|точнее'))return null;
  if(/^\d+(?:[.,]\d+)?$/u.test(value))return Number(value.replace(',','.'));
  if(/\sс\sполовиной$/u.test(value)){const n=integerWords(value.replace(/\sс\sполовиной$/u,''));return n===null?null:n+.5;}
  const decimal=value.split(/\s+(?:запятая|точка|целых|целая)\s+/u);
  if(decimal.length===2){const whole=integerWords(decimal[0]);let fraction=decimal[1].replace(/\s+(?:десятых|сотых)$/u,'');const places=/сотых$/u.test(decimal[1])?2:/десятых$/u.test(decimal[1])?1:null;const n=integerWords(fraction);if(whole===null||n===null)return null;const divisor=places?10**places:n<10?10:100;if(n>=divisor)return null;return whole+n/divisor;}
  return integerWords(value);
 }
 function parse(text){const raw=String(text||'').trim();const lower=raw.toLowerCase().replaceAll('ё','е');const values={},warnings=[],found={};
  const fields=/(^|[\s,;.!?])(меня\s+зовут|имя|возраст|мне|вес|вешу|пол)(?=\s|[:—-]|\d|$)\s*[:—-]?\s*/giu;
  const markers=[...raw.matchAll(fields)];
  function candidate(key,value){if(value===null||value===undefined)return;(found[key]??=[]).push(value);}
  for(let i=0;i<markers.length;i++){const m=markers[i];const label=m[2].toLowerCase();const chunk=raw.slice(m.index+m[0].length,i+1<markers.length?markers[i+1].index:raw.length).trim().replace(/[,;.!?]+$/u,'').trim();
   if(label==='имя'||label.startsWith('меня')){const name=chunk.match(/^[\p{L}]+(?:[-'’][\p{L}]+)*/u)?.[0];if(name&&name.length<=60&&!word(name.toLowerCase(),'не|беременна|женский|мужской'))candidate('name',name.split('-').map(s=>s.charAt(0).toLocaleUpperCase('ru')+s.slice(1).toLocaleLowerCase('ru')).join('-'));else warnings.push('Не удалось уверенно распознать имя.');}
   else if(label==='возраст'||label==='мне'){const n=number(chunk,'age');if(n!==null&&Number.isInteger(n)&&n>=0&&n<=120)candidate('age',n);else warnings.push('Возраст не заполнен: укажи целое число полных лет от 0 до 120.');}
   else if(label==='вес'||label==='вешу'){const n=number(chunk,'weight');if(n!==null&&Number.isFinite(n)&&n>=.1&&n<=500&&Math.abs(n*10-Math.round(n*10))<1e-8)candidate('weight',n);else warnings.push('Вес не заполнен: укажи число килограммов от 0,1 до 500.');}
   else if(label==='пол'){const sexText=chunk.toLowerCase().replace(/не\s+(?:женский|мужской|женщина|мужчина)/gu,'');if(word(sexText,'женский|женщина'))candidate('sex','female');if(word(sexText,'мужской|мужчина'))candidate('sex','male');}
  }
  const sexText=lower.replace(/не\s+(?:женский|мужской|женщина|мужчина)/gu,'');
  if(word(sexText,'я +женщина|женский +пол'))candidate('sex','female');if(word(sexText,'я +мужчина|мужской +пол'))candidate('sex','male');
  const statusText=lower.replace(/не\s+планирую\s+беременность|беременность\s+не\s+планирую/gu,' ');
  const none=/(?:^|[^\p{L}])(?:не\s*беременна|не\s+беременная|беременности\s+нет|нет\s+беременности)(?=$|[^\p{L}])/gu;
  const planning=/(?:^|[^\p{L}])(?:планирую\s+беременность|планирование\s+беременности|готовлюсь\s+к\s+беременности|хочу\s+забеременеть)(?=$|[^\p{L}])/gu;
  const lactation=/(?:^|[^\p{L}])(?:лактация|грудное\s+вскармливание|кормлю\s+грудью|кормлю\s+грудным\s+молоком)(?=$|[^\p{L}])/gu;
  const hasNone=none.test(statusText);none.lastIndex=0;let remaining=statusText.replace(none,' ').replace(planning,' ');
  planning.lastIndex=0;const hasPlanning=planning.test(statusText);let hasLactation=false;for(const m of lower.matchAll(lactation)){if(!/(?:^|\s)не\s*$/u.test(lower.slice(0,m.index+1).trimEnd()))hasLactation=true;}
  const hasPregnancy=word(remaining,'беременна|беременная')||remaining.split(/[,;.!?\n]/u).some(part=>/^(?:у\s+меня\s+|(?:физиологическое\s+)?состояние\s+|статус\s+)?беременность$/u.test(part.trim()));const uncertain=word(lower,'возможно|наверное|кажется|подозреваю')&&word(lower,'беременна|беременность')||/беременна\s+ли|ли\s+я\s+беременна/u.test(lower);
  let status=null;const positives=[hasPlanning&&'planning',hasLactation&&'lactating',hasPregnancy&&'pregnant'].filter(Boolean);
  if(uncertain)warnings.push('Физиологическое состояние не заполнено: в речи есть неопределённость.');
  else if(positives.length>1||hasPregnancy&&hasNone)warnings.push('Физиологическое состояние неоднозначно. Выбери одно состояние вручную.');
  else status=positives[0]||(hasNone?'none':null);
  for(const [key,list]of Object.entries(found)){const unique=[...new Set(list)];if(unique.length===1)values[key]=unique[0];else warnings.push(`Поле «${{name:'Имя',age:'Возраст',weight:'Вес',sex:'Пол'}[key]}» указано несколько раз по-разному — проверь его вручную.`);}
  if(status!==null){if(values.sex==='male'){delete values.sex;warnings.push('Пол и физиологическое состояние противоречат друг другу. Эти поля не изменены.');}else if(found.sex&&new Set(found.sex).size>1){warnings.push('Состояние не применено из-за неоднозначного пола.');}else{values.status=status;if(!found.sex)values.sex='female';}}
  return {values,warnings:[...new Set(warnings)]};
 }
 globalThis.LunaProfileParser=Object.freeze({parse});
})();
