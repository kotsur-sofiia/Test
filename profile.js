/* About-me form. Existing diary data and legacy profile fields are retained. */
'use strict';
(() => {
 const q=s=>document.querySelector(s),healthKeys=['menstrualStage','cyclePattern','cycleLength','periodLength','hormones','fertility','healthNotes'];
 const field=key=>q('#profile-'+key);let lastStatus=null;
 function syncBirthDate(){const day=field('birthDay').value.trim(),month=field('birthMonth').value.trim(),year=field('birthYear').value.trim();field('birthDate').value=/^\d{1,2}$/.test(day)&&/^\d{1,2}$/.test(month)&&/^\d{4}$/.test(year)?`${year}-${month.padStart(2,'0')}-${day.padStart(2,'0')}`:'';const m=Number(month),y=Number(year);const count=m>=1&&m<=12?new Date(Date.UTC(/^\d{4}$/.test(year)?y:2000,m,0)).getUTCDate():31;const picker=field('pickDay');if(picker.options.length!==count+1){picker.replaceChildren(new Option('⌄',''));for(let d=1;d<=count;d++)picker.add(new Option(String(d),String(d)));}}
 function loadBirthDate(value){const parts=(value||'').split('-');for(const [key,index]of [['birthDay',2],['birthMonth',1],['birthYear',0]])field(key).value=parts[index]||'';}
 function initBirthDate(){const months=['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];months.forEach((label,i)=>field('pickMonth').add(new Option(label,String(i+1))));const year=new Date().getFullYear();for(let y=year;y>=year-120;y--)field('pickYear').add(new Option(String(y),String(y)));for(const part of ['Day','Month','Year'])field('pick'+part).onchange=()=>{const picker=field('pick'+part);if(picker.value){field('birth'+part).value=part==='Year'?picker.value:picker.value.padStart(2,'0');picker.value='';update();}};}
 function update(){syncBirthDate();const birth=field('birthDate').value,years=LunaProfileModel.age(birth,localDate());const partial=['birthDay','birthMonth','birthYear'].some(k=>field(k).value);q('#profile-age-hint').textContent=birth?(years===null?'Проверь дату рождения.':`Возраст рассчитывается автоматически: ${years} лет.`):partial?'Укажи день, месяц и год полностью.':state.profile&&!state.profile.birthDate?'Раньше был указан только возраст. Введи дату рождения — она не восстанавливается из возраста.':'';q('#women-health-fields').hidden=field('sex').value==='male';if(lastStatus==='lactating'&&field('status').value!=='lactating')field('breastfeeding').checked=false;field('breastfeeding').disabled=field('status').value==='lactating';if(field('status').value==='lactating')field('breastfeeding').checked=true;lastStatus=field('status').value;field('status').closest('label').hidden=years!==null&&years<10;if(years!==null&&years<10){field('status').value='none';field('breastfeeding').checked=false;}
 const weight=Number(field('weight').value),height=Number(field('height').value);const value=LunaProfileModel.bmi(height,weight);q('#profile-bmi').textContent=value===null?'—':value.toLocaleString('ru');
 q('#profile-cycle-note').textContent='Календарная схема фаз не применяется при беременности, лактации, отсутствии или нерегулярности менструаций и использовании гормональных средств. История отметок сохраняется.';
 }
 function init(){
  initBirthDate();
  for(const [key,[label,min,max]]of Object.entries(LunaProfileModel.metrics)){const l=textEl('label',label),input=document.createElement('input');input.id='profile-'+key;input.type='number';input.inputMode='decimal';input.min=min;input.max=max;input.step='any';input.placeholder='Необязательно';l.append(input);q('#profile-body-fields').append(l);}
  const p=state.profile;if(p){for(const key of ['name','birthDate','sex','status'])if(p[key]!=null)field(key).value=p[key];for(const key of Object.keys(LunaProfileModel.metrics)){const value=p.body?.[key]??(key==='weight'?p.weight:null);if(value!=null)field(key).value=value;}
   for(const key of healthKeys)if(p.health?.[key]!=null)field(key).value=p.health[key];field('breastfeeding').checked=Boolean(p.health?.breastfeeding||p.status==='lactating');
  }
  loadBirthDate(field('birthDate').value);
  q('#profile-form').addEventListener('input',update);q('#profile-form').addEventListener('change',update);update();
  q('#profile-form').onsubmit=e=>{e.preventDefault();syncBirthDate();const old=state.profile;const birthDate=field('birthDate').value,age=LunaProfileModel.age(birthDate,localDate());const name=field('name').value.trim();let error='';if(!name||name.length>60||age===null)error='Проверь имя и дату рождения: дата не должна быть в будущем, возраст — не более 120 лет.';
   const body={...(old?.body||{})};for(const [key,[label,min,max]]of Object.entries(LunaProfileModel.metrics)){const raw=field(key).value;if(raw===''){delete body[key];continue;}const value=Number(raw);if(!Number.isFinite(value)||value<min||value>max)error=`Проверь показатель «${label}».`;else body[key]=value;}
   if(body.muscleMass!=null&&body.weight!=null&&body.muscleMass>body.weight)error='Мышечная масса не может превышать вес тела.';if(body.boneMass!=null&&body.weight!=null&&body.boneMass>body.weight)error='Костная масса не может превышать вес тела.';
   const health={...(old?.health||{})};for(const key of healthKeys){const raw=field(key).value;health[key]=['cycleLength','periodLength'].includes(key)?raw===''?null:Number(raw):raw.trim();}health.breastfeeding=field('breastfeeding').checked;
   if(health.cycleLength!==null&&(!Number.isInteger(health.cycleLength)||health.cycleLength<10||health.cycleLength>180))error='Проверь длину цикла.';if(health.periodLength!==null&&(!Number.isInteger(health.periodLength)||health.periodLength<1||health.periodLength>30))error='Проверь длительность менструации.';if(health.healthNotes.length>2000)error='Сократи заметку о здоровье до 2000 символов.';
   q('#profile-error').textContent=error;if(error)return;
   const sex=field('sex').value,status=sex==='male'?'none':field('status').value;const profile={...(old||{}),name,birthDate,age,ageUnit:'years',sex,status,body,health,updated:localDate()};delete profile.month;if(sex==='male')health.breastfeeding=false;if(body.weight!=null)profile.weight=body.weight;else delete profile.weight;
   if(old&&!old.birthDate&&!old.legacyAge)profile.legacyAge={age:old.age,ageUnit:old.ageUnit};
   const previousCycle={length:state.cycleLength,period:state.periodLength};if(sex==='female'&&health.cycleLength>=21&&health.cycleLength<=45)state.cycleLength=health.cycleLength;if(sex==='female'&&health.periodLength>=1&&health.periodLength<=10)state.periodLength=health.periodLength;
   state.profile=profile;if(!save()){state.profile=old;state.cycleLength=previousCycle.length;state.periodLength=previousCycle.period;render();q('#profile-error').textContent='Не удалось сохранить профиль. Введённые поля оставлены: попробуй ещё раз или скопируй значения.';return;}q('#cycle-length').value=state.cycleLength;q('#period-length').value=state.periodLength;q('#profile-summary').textContent='Профиль сохранён. '+profileLabel();
  };
 }
 function render(){
  const p=state.profile,age=profileAge();q('#profile-summary').textContent=p?profileLabel():'';
  q('#nutrition-profile-context').textContent=p?`${profileLabel()}. ${p.sex?'Ориентиры RDA/AI общего поступления из еды и БАДов. К дневнику любого дня применяется текущий профиль.':'Для персональных процентов укажи пол для справочных таблиц в профиле.'}`:'Без анкеты показываем количество нутриентов, без персональных процентов.';
  let advice='Для выбора БАДов и индивидуальных доз необходима консультация с врачом. Ориентиры питания не являются назначением.';
  if(p?.status==='pregnant'&&p.health?.breastfeeding)advice='Беременность и грудное вскармливание одновременно: автоматические ориентиры не выбираются. Необходима консультация с врачом для индивидуального рациона и добавок.';
  else if(p?.status==='pregnant')advice=age<14||age>50?'Для этого возраста беременности автоматические ориентиры не назначаются. Необходима консультация с врачом.':'Беременность: используются отдельные ориентиры общего питания. Необходима консультация с врачом; не подбирай дозы БАДов по процентам.';
  else if(p?.status==='lactating'||p?.health?.breastfeeding)advice=age<14||age>50?'Для этого возраста при лактации автоматические ориентиры не назначаются. Необходима консультация с врачом.':'Лактация: используются отдельные ориентиры общего питания. Необходима консультация с врачом при выборе рациона и БАДов.';
  else if(p?.status==='planning')advice='Подготовка к беременности: используются ориентиры для небеременных. Обсуди фолаты, йод и принимаемые добавки с врачом до беременности.';
  else if(p&&age<1)advice='Для ребёнка младше года автоматические нормы в этом формате не рассчитываются. Рацион и добавки необходимо обсуждать с педиатром.';
  else if(p&&age<19)advice='Используются возрастные ориентиры ребёнка или подростка. Рацион и добавки необходимо обсуждать с педиатром.';
  q('#profile-advice').textContent=advice;
 }
 window.LunaProfileUI=Object.freeze({init,update,render});
})();
