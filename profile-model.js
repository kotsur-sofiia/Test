/* Calendar arithmetic and optional body metrics; no diagnosis or estimated device readings. */
(function(root){'use strict';
 function age(birthDate,asOf){if(!/^\d{4}-\d{2}-\d{2}$/.test(birthDate||'')||!/^\d{4}-\d{2}-\d{2}$/.test(asOf||''))return null;const [y,m,d]=birthDate.split('-').map(Number),date=new Date(Date.UTC(y,m-1,d));if(date.getUTCFullYear()!==y||date.getUTCMonth()!==m-1||date.getUTCDate()!==d||birthDate>asOf)return null;const [ay,am,ad]=asOf.split('-').map(Number);const years=ay-y-((am<m||am===m&&ad<d)?1:0);return years>=0&&years<=120?years:null;}
 const metrics={height:['Рост, см',30,250],weight:['Вес, кг',.1,500],boneMass:['Костная масса, кг',.1,20],fatPercent:['Жир, %',0,80],visceralFat:['Висцеральный жир — уровень по шкале прибора',0,100],muscleMass:['Мышечная масса, кг',.1,300],waterPercent:['Вода, %',0,100],basalMetabolism:['Основной обмен, ккал/сутки',1,10000],bodyAge:['Биологический возраст тела — по прибору',1,150]};
 function bmi(height,weight){return Number.isFinite(height)&&height>0&&Number.isFinite(weight)&&weight>0?Math.round(weight/(height/100)**2*10)/10:null;}
 const api={age,bmi,metrics};if(typeof module!=='undefined')module.exports=api;root.LunaProfileModel=Object.freeze(api);
})(typeof window!=='undefined'?window:globalThis);
