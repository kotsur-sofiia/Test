import assert from 'node:assert/strict';
import {createGuidanceServer} from '../server/cycle-guidance.mjs';
const origin='https://kotsur-sofiia.github.io';
let requests=[];
const mock=async(url,options)=>{requests.push({url,options});return new Response(JSON.stringify({output:[{content:[{type:'output_text',text:JSON.stringify({summary:'Мягкий ритм дня',tips:[{title:'Отдых',text:'Оставь время для пауз.'},{title:'Питание',text:'Ешь регулярно.'},{title:'Сон',text:'Замечай своё самочувствие.'}]})}]}]}),{status:200});};
const server=createGuidanceServer({apiKey:'test-secret',allowedOrigin:origin,fetchImpl:mock,dailyLimit:2});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url='http://127.0.0.1:'+server.address().port+'/api/cycle-guidance';
const input={cycleDay:21,cycleLength:28,periodLength:5,phase:'luteal'};
const call=(body=input,extra={})=>fetch(url,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json',...extra},body:JSON.stringify(body)});
try {
  assert.equal((await call(input,{Origin:'https://wrong.example'})).status,403);
  assert.equal((await call({...input,name:'Private name'})).status,400);
  assert.equal((await call({...input,phase:'menstrual'})).status,400);
  const response=await call();const data=await response.json();assert.equal(data.source,'ai');assert.equal(data.tips.length,3);
  assert.equal(response.headers.get('access-control-allow-origin'),origin);assert.equal(response.headers.get('cache-control'),'no-store');
  const provider=JSON.parse(requests[0].options.body);assert.deepEqual(JSON.parse(provider.input),input);assert.equal(provider.store,false);
  assert.equal(requests[0].options.headers.Authorization,'Bearer test-secret');assert.ok(!JSON.stringify(data).includes('test-secret'));
  assert.equal((await call()).status,200);assert.equal((await call()).status,429);
  assert.equal(requests.length,2);
} finally {await new Promise(resolve=>server.close(resolve));}
const failed=createGuidanceServer({apiKey:'test-secret',allowedOrigin:origin,fetchImpl:async()=>new Response('not JSON',{status:200})});
await new Promise(resolve=>failed.listen(0,'127.0.0.1',resolve));
try {
  const response=await fetch('http://127.0.0.1:'+failed.address().port+'/api/cycle-guidance',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify(input)});
  assert.equal(response.status,502);assert.deepEqual(await response.json(),{error:'AI service unavailable'});
} finally {await new Promise(resolve=>failed.close(resolve));}
console.log('PASS: optional AI server validates minimal context, origin, schema, quota and errors; provider secret stays server-side. Real provider not called.');
