/* Strict calendar dates for both dotted manual entry and the native picker. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WomanPeriodDates=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
  'use strict';
  function validISO(value) {
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value)||Number(value.slice(0,4))<1000)return false;
    const stamp=Date.parse(value+'T12:00:00Z');
    return Number.isFinite(stamp)&&new Date(stamp).toISOString().slice(0,10)===value;
  }
  function parse(value) {
    if(typeof value!=='string')return null;
    const text=value.trim();if(validISO(text))return text;
    const m=/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/.exec(text)||/^(\d{2})(\d{2})(\d{4})$/.exec(text);
    if(!m)return null;const iso=m[3]+'-'+m[2].padStart(2,'0')+'-'+m[1].padStart(2,'0');
    return validISO(iso)?iso:null;
  }
  function format(iso) { return validISO(iso)?iso.slice(8,10)+'.'+iso.slice(5,7)+'.'+iso.slice(0,4):''; }
  function days(start,end) { return Math.round((Date.parse(end+'T12:00:00Z')-Date.parse(start+'T12:00:00Z'))/86400000)+1; }
  function validate({start,end,periods=[],ends={},today}) {
    if(!validISO(start)||!validISO(today)||start>today)return 'Проверь дату начала: укажи ДД.ММ.ГГГГ, не позднее сегодняшнего дня.';
    if(end&&(!validISO(end)||end>today))return 'Проверь дату окончания: укажи ДД.ММ.ГГГГ, не позднее сегодняшнего дня.';
    if(end&&end<start)return 'Окончание менструации не может быть раньше начала.';
    if(periods.some(other=>other!==start&&validISO(other)&&((other>start&&end&&other<=end)||(other<start&&validISO(ends[other])&&ends[other]>=start))))return 'Эти даты пересекаются с другой записью. Проверь начало и окончание.';
    return '';
  }
  return Object.freeze({validISO,parse,format,days,validate});
});
