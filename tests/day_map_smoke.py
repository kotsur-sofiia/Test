from profile_form import move_topic
"""Editable circular diary topics, inline notes, preservation and offline state."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from datetime import datetime, timezone
import json, os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8035/Test/').split('#')[0]
Path('/tmp/luna-check').mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({dayMap:{version:2,topicRailVersion:1,order:['cycle','food','water','skin','activity']},periods:['2026-10-20'],cycleLength:28,periodLength:5,sleep:[],meals:[{id:'legacy-meal',date:'2026-11-02',product:'oats',grams:100}],water:[{id:'legacy-water',date:'2026-11-02',ml:200,container:'glass'}]}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 expect(page.locator('#cycle')).to_be_visible();assert page.locator('#page-title').text_content()=='Дневник'
 assert page.locator('#edit-day,#connection').count()==0
 assert page.locator('[data-main-view]:visible').count()==1
 def order():return page.locator('#day-widgets>.day-widget:not([hidden])').evaluate_all('(els)=>els.map(e=>e.dataset.widgetId)')
 def topic(name):page.locator(f'[data-widget-id="{name}"] a').click();page.wait_for_function('(id)=>document.body.dataset.topic===id',arg=name)
 def choose(name):
  page.locator('#add-widget').click();page.locator(f'#widget-options [data-topic="{name}"] [data-action=toggle]').click();assert page.locator(f'#widget-options [data-topic="{name}"] [data-action=toggle]').get_attribute('aria-checked')=='true';page.locator('#widget-picker [data-close-dialog]').click()
 def note(name,text,date=None):
  topic(name)
  if date:page.locator('#widget-note-date').fill(date);page.locator('#widget-note-date').dispatch_event('change')
  page.locator('#widget-note-text').fill(text);page.locator('#widget-note-form button').click();expect(page.locator('#widget-note-text')).to_have_value('')
 assert order()==['cycle','food','water','skin','activity']
 for orb in page.locator('.mini .topic-orb').all():
  if orb.is_visible():
   box=orb.bounding_box();assert box['width']==box['height'] and box['width']>=44
 assert page.locator('[data-widget-id=water] strong').text_content()=='200 мл'
 choose('books');choose('sleep');choose('affirmation')
 note('skin','Мягкий уход, кожа спокойная.');note('books','Маленький принц · 15 страниц');note('skin','Вчера была сухость','2026-11-01')
 page.locator('#widget-note-date').fill('2026-11-02');page.locator('#widget-note-date').dispatch_event('change');assert 'Вчера' not in page.locator('#widget-note-history').inner_text()
 page.locator('#widget-note-text').fill('Черновик');topic('cycle');topic('skin');expect(page.locator('#widget-note-text')).to_have_value('Черновик')
 page.locator('#add-widget').click();page.keyboard.press('Escape');expect(page.locator('#widget-picker')).not_to_be_visible()
 page.locator('#add-widget').click();page.locator('#show-custom-widget').click();title='<img src=x> Творчество';page.locator('#custom-widget-title').fill(title);page.locator('#custom-widget-form button[type=submit]').click();custom=page.evaluate('state.dayMap.custom[0].id');assert page.locator('#widget-picker img').count()==0;page.locator('#widget-picker [data-close-dialog]').click()
 note(custom,'Акварель, 20 минут')
 page.locator('#add-widget').click();previous=order();move_topic(page,custom,-1);assert order()[-2:]==[custom,'affirmation']
 page.locator('#widget-options [data-topic=skin] [data-action=toggle]').click();assert 'skin' not in order();assert page.evaluate('state.dayMap.notes.filter(n=>n.topic==="skin").length')==2
 page.locator('#widget-picker [data-close-dialog]').click();choose('skin');topic('skin');assert 'Мягкий уход' in page.locator('#widget-note-history').inner_text()
 expected=order();page.reload();assert order()==expected
 page.evaluate('''async()=>{const c=await caches.open('luna-diary-v75');await c.put(new URL('./app.js',location.href),new Response('throw Error("Old script loaded")',{headers:{'Content-Type':'text/javascript'}}))}''');page.reload();expect(page.locator('#diary-shell')).to_be_visible()
 old=page.evaluate('JSON.stringify(state.dayMap)');page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException("full","QuotaExceededError")}}')
 page.locator('#add-widget').click();page.locator('#show-custom-widget').click();page.locator('#custom-widget-title').fill('Не сохранённая тема');page.locator('#custom-widget-form button[type=submit]').click();assert page.evaluate('JSON.stringify(state.dayMap)')==old;assert len(order())==len(expected);expect(page.locator('#custom-widget-title')).to_have_value('Не сохранённая тема');page.locator('#widget-picker [data-close-dialog]').click()
 topic('books');page.locator('#widget-note-text').fill('Текст при переполнении');page.locator('#widget-note-form button').click();assert page.evaluate('JSON.stringify(state.dayMap)')==old;expect(page.locator('#widget-note-text')).to_have_value('Текст при переполнении')
 page.evaluate('()=>{Storage.prototype.setItem=realSet}');page.locator('#widget-note-form button').click()
 topic('water');expect(page.locator('#water-form')).to_be_visible();assert not page.locator('#food').is_visible();page.locator('#water-volume').fill('300');page.locator('#water-form button').click();assert page.locator('[data-widget-id=water] strong').text_content()=='500 мл'
 page.locator('#add-widget').click()
 for name in list(order()):page.locator(f'#widget-options [data-topic="{name}"] [data-action=toggle]').click()
 expect(page.locator('#day-empty')).to_be_visible();page.reload();assert order()==[] and page.evaluate('state.dayMap.notes.length')==5
 choose('books');topic('books');assert 'Текст при переполнении' in page.locator('#widget-note-history').inner_text();choose('affirmation');choose('water')
 for width,height in [(320,844),(375,844),(390,844),(430,844),(768,1000),(1280,1000),(844,390)]:
  page.set_viewport_size({'width':width,'height':height});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,height)
  assert page.locator('[data-main-view]:visible').count()==1
  page.locator('#add-widget').click();box=page.locator('#widget-picker').bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1 and box['y']>=0 and box['y']+box['height']<=height+1,(width,height,box)
  page.locator('#widget-picker [data-close-dialog]').click()
 page.evaluate('state.profile={name:"Тест",age:35,ageUnit:"years",sex:"male",status:"none"};save()');page.locator('#add-widget').click();assert page.locator('#widget-options [data-topic=cycle] [data-action=toggle]').is_disabled();page.locator('#widget-picker [data-close-dialog]').click()
 data=page.evaluate('JSON.parse(JSON.stringify(state))');assert len(data['dayMap']['notes'])==5 and data['meals'][0]['id']=='legacy-meal'
 ctx.set_offline(True);page.reload();expect(page.locator('#diary-shell')).to_be_visible();topic('water');assert page.locator('#water-total').inner_text()=='500 мл';choose('skin');topic('skin');assert 'Мягкий уход' in page.locator('#widget-note-history').inner_text()
 page.clock.fast_forward(13*60*60*1000);assert page.locator('#today').count()==0;assert page.locator('[data-widget-id=water] strong').text_content()=='0 мл'
 assert not errors,errors
 # Existing selections keep their order; unknown/duplicate ids are ignored without losing metadata.
 clean=b.new_context();clean.add_init_script("localStorage.setItem('luna-diary-v1',JSON.stringify({periods:[],sleep:[],meals:[],dayMap:{version:1,order:['water','water','unknown'],custom:[],notes:[],futureField:'keep'}}))");other=clean.new_page();other.goto(URL+'#home');assert other.locator('#day-widgets>.day-widget:not([hidden])').count()==1
 other.locator('#add-widget').click();other.locator('#widget-options [data-topic=books] [data-action=toggle]').click();assert other.evaluate('state.dayMap.futureField')=='keep';clean.close();b.close()
 print('PASS: circular topics, inline notes, editable order and empty diary, old data, quotas/drafts, independent water, responsive picker, stored records, offline and midnight')
