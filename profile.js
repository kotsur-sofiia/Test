/* About-me form. Existing diary data and legacy profile fields are retained. */
'use strict';
(() => {
 const q=s=>document.querySelector(s),healthKeys=['menstrualStage','cyclePattern','cycleLength','periodLength','hormones','fertility','healthNotes'];
 const field=key=>q('#profile-'+key);let lastStatus=null;
 const preservedChoices=new Map();
 function birthISO(){return WomanPeriodDates.parse(field('birthDate').value);}
 function loadChoice(key,value){const select=field(key);if([...select.options].some(o=>o.value===value))select.value=value;else if(value!=null){preservedChoices.set(key,value);select.value=key==='hormones'&&['combined','progestin','iud','other'].includes(value)?'therapy':'unspecified';}}
 function update(){const birth=birthISO(),years=LunaProfileModel.age(birth,localDate());q('#profile-age-hint').textContent=field('birthDate').value.trim()&&years===null?'Проверь дату рождения: ДД.ММ.ГГГГ.':'';q('#women-health-fields').hidden=false;if(lastStatus==='lactating'&&field('status').value!=='lactating')field('breastfeeding').checked=false;field('breastfeeding').disabled=field('status').value==='lactating';if(field('status').value==='lactating')field('breastfeeding').checked=true;lastStatus=field('status').value;field('status').closest('label').hidden=years!==null&&years<10;if(years!==null&&years<10){field('status').value='none';field('breastfeeding').checked=false;}
 const weight=Number(field('weight').value),height=Number(field('height').value);const value=LunaProfileModel.bmi(height,weight);q('#profile-bmi').textContent=value===null?'—':value.toLocaleString('ru');
 q('#profile-cycle-note').textContent='Календарная схема фаз не применяется при беременности, лактации, отсутствии или нерегулярности менструаций и использовании гормональных средств. История отметок сохраняется.';
 }
 function init(){
  field('birthDate').addEventListener('blur',()=>{const iso=birthISO();if(iso)field('birthDate').value=WomanPeriodDates.format(iso);});
  for(const key of healthKeys.filter(key=>field(key).tagName==='SELECT'))field(key).addEventListener('change',()=>preservedChoices.delete(key));
  for(const [key,[label,min,max]]of Object.entries(LunaProfileModel.metrics)){const l=textEl('label',label),input=document.createElement('input');input.id='profile-'+key;input.type='number';input.inputMode='decimal';input.min=min;input.max=max;input.step='any';input.placeholder='Необязательно';l.append(input);q('#profile-body-fields').append(l);}
  const p=state.profile;if(p){for(const key of ['name','status'])if(p[key]!=null)field(key).value=p[key];field('birthDate').value=WomanPeriodDates.format(p.birthDate);for(const key of Object.keys(LunaProfileModel.metrics)){const value=p.body?.[key]??(key==='weight'?p.weight:null);if(value!=null)field(key).value=value;}
   for(const key of healthKeys)if(p.health?.[key]!=null){if(field(key).tagName==='SELECT')loadChoice(key,p.health[key]);else field(key).value=p.health[key];}field('breastfeeding').checked=Boolean(p.health?.breastfeeding||p.status==='lactating');
  }
  q('#profile-form').addEventListener('input',update);q('#profile-form').addEventListener('change',update);update();
  q('#profile-form').onsubmit=e=>{e.preventDefault();const old=state.profile;const birthDate=birthISO(),age=LunaProfileModel.age(birthDate,localDate());const name=field('name').value.trim();let error='';if(!name||name.length>60||age===null)error='Проверь имя и дату рождения: дата не должна быть в будущем, возраст — не более 120 лет.';
   const body={...(old?.body||{})};for(const [key,[label,min,max]]of Object.entries(LunaProfileModel.metrics)){const raw=field(key).value;if(raw===''){delete body[key];continue;}const value=Number(raw);if(!Number.isFinite(value)||value<min||value>max)error=`Проверь показатель «${label}».`;else body[key]=value;}
   if(body.muscleMass!=null&&body.weight!=null&&body.muscleMass>body.weight)error='Мышечная масса не может превышать вес тела.';if(body.boneMass!=null&&body.weight!=null&&body.boneMass>body.weight)error='Костная масса не может превышать вес тела.';
   const health={...(old?.health||{})};for(const key of healthKeys){const raw=field(key).value;health[key]=preservedChoices.has(key)?preservedChoices.get(key):['cycleLength','periodLength'].includes(key)?raw===''?null:Number(raw):raw.trim();}health.breastfeeding=field('breastfeeding').checked;
   if(health.cycleLength!==null&&(!Number.isInteger(health.cycleLength)||health.cycleLength<10||health.cycleLength>180))error='Проверь длину цикла.';if(health.periodLength!==null&&(!Number.isInteger(health.periodLength)||health.periodLength<1||health.periodLength>30))error='Проверь длительность менструации.';if(health.healthNotes.length>2000)error='Сократи заметку о здоровье до 2000 символов.';
   q('#profile-error').textContent=error;if(error)return;
   const sex='female',status=field('status').value;const profile={...(old||{}),name,birthDate,age,ageUnit:'years',sex,status,body,health,updated:localDate()};delete profile.month;if(old?.sex&&old.sex!=='female'&&!profile.legacySex)profile.legacySex=old.sex;if(body.weight!=null)profile.weight=body.weight;else delete profile.weight;
   if(old&&!old.birthDate&&!old.legacyAge)profile.legacyAge={age:old.age,ageUnit:old.ageUnit};
   const previousCycle={length:state.cycleLength,period:state.periodLength};if(sex==='female'&&health.cycleLength>=21&&health.cycleLength<=45)state.cycleLength=health.cycleLength;if(sex==='female'&&health.periodLength>=1&&health.periodLength<=10)state.periodLength=health.periodLength;
   state.profile=profile;if(!save()){state.profile=old;state.cycleLength=previousCycle.length;state.periodLength=previousCycle.period;render();q('#profile-error').textContent='Не удалось сохранить профиль. Введённые поля оставлены: попробуй ещё раз или скопируй значения.';return;}q('#cycle-length').value=state.cycleLength;q('#period-length').value=state.periodLength;field('birthDate').value=WomanPeriodDates.format(birthDate);q('#profile-summary').textContent='Профиль сохранён. '+profileLabel();
  };
 }
 function render(){
  const p=state.profile,age=profileAge();q('#profile-summary').textContent=p?profileLabel():'';
  q('#nutrition-profile-context').textContent=p?`${profileLabel()}. Ориентиры RDA/AI общего поступления из еды и БАДов. К дневнику любого дня применяется текущий профиль.`:'Без анкеты показываем количество нутриентов, без персональных процентов.';
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
