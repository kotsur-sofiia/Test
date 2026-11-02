"""Circular diary shell and cycle clock, truthful reference/AI states and stale requests."""
from playwright.sync_api import sync_playwright, expect
from datetime import datetime,timezone
import os,json
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8035/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 c.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-13'],cycleLength:28,periodLength:5,sleep:[],meals:[],profile:{name:'Private name',age:35,ageUnit:'years',sex:'female',status:'none',health:{healthNotes:'Private notes'}}}))")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 expect(page.locator('#cycle')).to_be_visible();assert page.locator('#diary-shell h1').text_content()=='Дневник'
 assert page.locator('#cycle-dial-day').inner_text()=='21' and page.locator('#cycle-dial-phase').inner_text()=='Лютеиновая фаза'
 assert '8 дней' in page.locator('#cycle-dial-countdown').inner_text()
 assert page.locator('#cycle-care-source').inner_text()=='Справочные' and page.locator('#cycle-ai-request').is_hidden()
 assert 'ИИ пока не подключён' in page.locator('#cycle-ai-status').inner_text()
 assert page.locator('#cycle-dial-ticks line').count()==28
 assert page.locator('#cycle-dial svg text').count()==0
 marker=page.locator('#cycle-dial-marker');assert float(marker.get_attribute('cx'))<160
 page.evaluate("selected='2026-10-13';renderCycle()")
 assert page.locator('#cycle-dial-day').inner_text()=='1';assert abs(float(marker.get_attribute('cx'))-160)<.01 and float(marker.get_attribute('cy'))==21
 page.locator('#period-start').fill('2026-10-13');page.locator('#cycle-form button').click();assert page.locator('#cycle-dial-day').inner_text()=='21'
 page.evaluate("selected='2026-11-10';renderCycle()")
 assert page.locator('#cycle-dial-day').inner_text()=='29' and page.locator('#cycle-dial').get_attribute('data-status')=='awaiting'
 assert page.locator('#cycle-dial-phase').inner_text()=='Фаза не определена'
 page.evaluate("selected='2026-11-02';renderCycle()")
 before=page.evaluate('JSON.stringify(state.periods)');page.evaluate('()=>{window.originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("full")}}');page.locator('#period-start').fill('2026-10-14');page.locator('#cycle-form button').click();assert page.evaluate('JSON.stringify(state.periods)')==before and page.locator('#cycle-dial-day').inner_text()=='21';page.evaluate('()=>{Storage.prototype.setItem=originalSet}')
 page.locator('[data-widget-id=food] a').click();expect(page.locator('#food')).to_be_visible();expect(page.locator('#diary-shell')).to_be_visible();assert not page.locator('#cycle').is_visible()
 page.locator('[data-widget-id=water] a').click();expect(page.locator('#water')).to_be_visible();assert not page.locator('#food').is_visible()
 page.locator('[data-widget-id=cycle] a').click();assert page.locator('[data-widget-id=cycle] a').get_attribute('aria-current')=='page'
 for width in [320,375,390,430,768,1280]:
  page.set_viewport_size({'width':width,'height':1000});page.evaluate('document.fonts.ready');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  box=page.locator('#cycle-dial').bounding_box();assert box['x']>=0 and box['x']+box['width']<=width
  bounds=page.locator('.cycle-dial-copy').bounding_box()
  for field in ['cycle-dial-phase','cycle-dial-day','cycle-dial-countdown']:
   e=page.locator('#'+field);assert e.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),(width,field)
   assert e.bounding_box()['y']>=box['y'] and e.bounding_box()['y']+e.bounding_box()['height']<=box['y']+box['height']
 # A configured future service gets only minimal context after an explicit click.
 requests=[];answer={'source':'ai','summary':'ИИ: спокойный ритм дня','tips':[{'title':'<img src=x>','text':'Оставь время для пауз.'},{'title':'Питание','text':'Ешь регулярно.'},{'title':'Отдых','text':'Замечай ощущения.'}]}
 page.route('https://guidance.example/**',lambda route:(requests.append(route.request.post_data_json),route.fulfill(status=200,content_type='application/json',body=json.dumps(answer))))
 page.evaluate("window.WOMAN_CONFIG={cycleGuidanceUrl:'https://guidance.example/api/cycle-guidance'};WomanCycleCare.refresh()")
 assert requests==[];page.locator('#cycle-ai-request').click();expect(page.locator('#cycle-care-source')).to_have_text('ИИ')
 assert requests==[{'cycleDay':21,'cycleLength':28,'periodLength':5,'phase':'luteal'}]
 assert page.locator('#phase-tips img').count()==0 and '<img' in page.locator('#phase-tips').inner_text()
 page.evaluate('()=>{window.fetch=async()=>new Response("failed",{status:503})}');page.locator('#cycle-ai-request').click();expect(page.locator('#cycle-care-source')).to_have_text('Справочные')
 # A slow result from a previous date must not paint a new day's recommendations.
 page.evaluate('''()=>{window.fetch=()=>new Promise(resolve=>{window.deliver=()=>resolve(new Response(JSON.stringify({source:'ai',summary:'Stale reply',tips:[{title:'A',text:'A'},{title:'B',text:'B'},{title:'C',text:'C'}]}),{headers:{'Content-Type':'application/json'}}))})}''')
 page.locator('#cycle-ai-request').click();page.evaluate("selected='2026-10-14';renderCycle();deliver()")
 expect(page.locator('#cycle-care-source')).to_have_text('Справочные');assert 'Stale' not in page.locator('#phase-description').inner_text()
 page.evaluate('()=>{window.fetch=async()=>new Response("failed",{status:503})}')
 page.locator('#cycle-ai-request').click();expect(page.locator('#cycle-ai-status')).to_contain_text('Не удалось');assert page.locator('#cycle-care-source').inner_text()=='Справочные'
 page.evaluate("state.profile.health.cyclePattern='irregular';save()")
 assert page.locator('#cycle-dial').get_attribute('data-status')=='unavailable' and page.locator('#cycle-ai-request').is_hidden()
 c.set_offline(True);page.reload();expect(page.locator('#diary-shell')).to_be_visible();assert page.locator('#cycle-care-source').inner_text()=='Справочные'
 assert not errors,errors;b.close();print('PASS: diary title/circles, inline topics, clockwise cycle dial and boundaries, unknown phases, responsive content, honest reference/AI labels, minimal AI payload, safe text, stale/error responses and offline')
