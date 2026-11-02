/* Optional Node 20+ service. No diary/profile text or provider key reaches the browser. */
import {createServer} from 'node:http';
import {pathToFileURL} from 'node:url';

const schema = {
  type:'object', additionalProperties:false, required:['summary','tips'], properties:{
    summary:{type:'string'}, tips:{type:'array',minItems:3,maxItems:3,items:{
      type:'object',additionalProperties:false,required:['title','text'],properties:{title:{type:'string'},text:{type:'string'}}
    }}
  }
};
function validInput(value) {
  if (!value || Object.keys(value).some(k=>!['cycleDay','cycleLength','periodLength','phase'].includes(k))) return false;
  const {cycleDay:day,cycleLength:length,periodLength:bleeding,phase}=value;
  if (![day,length,bleeding].every(Number.isInteger)||length<21||length>45||bleeding<1||bleeding>10||day<1||day>length) return false;
  const ov=Math.max(bleeding+2,length-14);
  return phase===(day<=bleeding?'menstrual':day<ov-1?'follicular':day<=ov+1?'ovulation':'luteal');
}
function validAnswer(data) {
  return typeof data?.summary==='string'&&data.summary.length>0&&data.summary.length<=1200&&Array.isArray(data.tips)&&data.tips.length===3&&data.tips.every(t=>typeof t.title==='string'&&t.title.length>0&&t.title.length<=120&&typeof t.text==='string'&&t.text.length>0&&t.text.length<=1600);
}
export function createGuidanceServer({apiKey,allowedOrigin,model='gpt-4.1-mini',fetchImpl=fetch,dailyLimit=50,perMinute=5}={}) {
  if (!apiKey||!allowedOrigin) throw new Error('Set OPENAI_API_KEY and WOMAN_ALLOWED_ORIGIN on the server.');
  const allowed=new URL(allowedOrigin).origin;
  const clients=new Map();let day='',count=0;
  return createServer(async(req,res)=>{
    const send=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...(req.headers.origin===allowed?{'Access-Control-Allow-Origin':allowed,'Vary':'Origin'}:{})});res.end(JSON.stringify(data));};
    if (req.url!=='/api/cycle-guidance') return send(404,{error:'Not found'});
    if (req.headers.origin!==allowed) return send(403,{error:'Origin not allowed'});
    if (req.method==='OPTIONS') {res.writeHead(204,{'Access-Control-Allow-Origin':allowed,'Access-Control-Allow-Methods':'POST','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600','Vary':'Origin'});return res.end();}
    if (req.method!=='POST') return send(405,{error:'Use POST'});
    if (!req.headers['content-type']?.toLowerCase().startsWith('application/json')) return send(415,{error:'Use JSON'});
    if (Number(req.headers['content-length'])>4096) return send(413,{error:'Request too large'});
    try {
      let raw='';for await (const chunk of req) {raw+=chunk;if(Buffer.byteLength(raw)>4096)return send(413,{error:'Request too large'});}
      let input;try{input=JSON.parse(raw);}catch{return send(400,{error:'Invalid JSON'});}
      if (!validInput(input)) return send(400,{error:'Invalid cycle context'});
      const now=Date.now(),today=new Date(now).toISOString().slice(0,10);
      if (day!==today){day=today;count=0;clients.clear();}
      for (const [ip,hits] of clients) if (!hits.some(t=>now-t<60000)) clients.delete(ip);
      const ip=req.socket.remoteAddress||'unknown',hits=(clients.get(ip)||[]).filter(t=>now-t<60000);
      if (count>=dailyLimit||hits.length>=perMinute) return send(429,{error:'Please try later'});
      hits.push(now);clients.set(ip,hits);count++;
      const upstream=await fetchImpl('https://api.openai.com/v1/responses',{
        method:'POST',headers:{'Authorization':'Bearer '+apiKey,'Content-Type':'application/json'},signal:AbortSignal.timeout(12000),
        body:JSON.stringify({model,store:false,max_output_tokens:900,
          instructions:'Ты помогаешь с дневником заботы о себе. Ответь по-русски, мягко, кратко. Данные — календарная оценка, а не подтверждённая фаза. Учитывай конкретный день, предполагаемую фазу и обычную длину цикла. Дай 3 практичные подсказки: повседневный ритм/активность, обычное питание/вода, сон/самонаблюдение. Не ставь диагноз, не назначай лечение, БАДы, дозы, ограничения калорий или специальную диету по фазам. Не предсказывай фертильность/безопасные дни, не утверждай гормональные изменения как факт. Не гарантируй состояние кожи, настроение или энергию по дню цикла. При выраженных симптомах советуй обратиться к врачу. Не придумывай персональные сведения. summary — до 450 символов, каждое title — до 60, text — до 500.',
          input:JSON.stringify(input),text:{format:{type:'json_schema',name:'cycle_care',strict:true,schema}}
        })
      });
      if (!upstream.ok) return send(502,{error:'AI service unavailable'});
      const output=await upstream.json();
      const text=(output.output||[]).flatMap(item=>item.content||[]).filter(item=>item.type==='output_text').map(item=>item.text).join('');
      let answer;try{answer=JSON.parse(text);}catch{return send(502,{error:'Invalid AI response'});}
      if (!validAnswer(answer)) return send(502,{error:'Invalid AI response'});
      send(200,{source:'ai',summary:answer.summary,tips:answer.tips});
    } catch {if(!res.headersSent)send(502,{error:'AI service unavailable'});}
  });
}
if (process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href) {
  const dailyLimit=Number(process.env.WOMAN_AI_DAILY_LIMIT||50);
  if(!Number.isInteger(dailyLimit)||dailyLimit<1||dailyLimit>1000)throw new Error('WOMAN_AI_DAILY_LIMIT must be 1–1000.');
  const server=createGuidanceServer({apiKey:process.env.OPENAI_API_KEY,allowedOrigin:process.env.WOMAN_ALLOWED_ORIGIN,model:process.env.OPENAI_MODEL||'gpt-4.1-mini',dailyLimit});
  server.listen(Number(process.env.PORT||8787),process.env.HOST||'127.0.0.1',()=>console.log('Woman cycle guidance service is listening.'));
}
