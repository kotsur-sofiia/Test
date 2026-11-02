"""Single topic editor, centered header, larger date, upgrades and disabled data."""
from playwright.sync_api import sync_playwright,expect
from datetime import datetime,timezone
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8036/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-20'],cycleLength:28,periodLength:5,sleep:[],meals:[],dayMap:{version:1,order:['books','water','cycle'],custom:[],notes:[{id:'old-note',topic:'books',date:'2026-11-02',text:'Прежняя запись о книге'}],futureField:'keep'}}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 def order():return page.locator('#day-widgets>.day-widget:not([hidden])').evaluate_all('(els)=>els.map(e=>e.dataset.widgetId)')
 def row(id):return page.locator('#widget-options [data-topic="'+id+'"]')
 def open_editor():page.locator('#add-widget').click();expect(page.locator('#widget-picker')).to_be_visible()
 def close_editor():page.locator('#widget-picker [data-close-dialog]').click()
 assert order()==['cycle','books','water']
 assert page.locator('#edit-day,#connection').count()==0
 expect(page.locator('#today')).to_have_text('Понедельник, 2 ноября 2026 год')
 open_editor();assert page.locator('#widget-picker-title').inner_text()=='Редактирование'
 assert 'Выбери темы, актуальные именно тебе.' in page.locator('#widget-picker').inner_text()
 titles=page.locator('.topic-editor-description strong').all_text_contents()
 for title in ['Подписка','Цикл','Питание','Гидратация','Кожа','Аффирмации','Медитация','Книги','Физическая активность','Рисование']:assert title in titles,title
 assert page.locator('#custom-widget-form').is_hidden() and page.locator('#show-custom-widget').inner_text()=='＋ Добавить свою'
 before=order();page.evaluate('()=>{window.originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("full")}}');row('cycle').locator('[data-action=toggle]').click();assert order()==before;assert page.locator('#cycle').is_visible();page.evaluate('()=>{Storage.prototype.setItem=originalSet}')
 row('books').locator('[data-action=toggle]').click();assert row('books').locator('[data-action=toggle]').get_attribute('aria-checked')=='false'
 assert page.evaluate('state.dayMap.notes[0].text')=='Прежняя запись о книге'
 row('meditation').locator('[data-action=toggle]').click();row('drawing').locator('[data-action=toggle]').click();row('membership').locator('[data-action=toggle]').click()
 row('membership').locator('[data-action=up]').click();expected=order();close_editor();page.reload();assert order()==expected
 open_editor();row('books').locator('[data-action=toggle]').click();close_editor();page.locator('[data-widget-id=books] a').click();assert 'Прежняя запись' in page.locator('#widget-note-history').inner_text()
 for id,text in [('meditation','Десять минут спокойного дыхания'),('drawing','Идея акварели')]:
  page.locator('[data-widget-id='+id+'] a').click();expect(page.locator('#topic-notes')).to_be_visible();page.locator('#widget-note-text').fill(text);page.locator('#widget-note-form button').click();assert text in page.locator('#widget-note-history').inner_text()
 page.locator('[data-widget-id=membership] a').click();expect(page.locator('#membership')).to_be_visible();assert page.locator('.bottom-nav [aria-current=page]').inner_text()=='Дневник'
 for width,height in [(320,844),(375,844),(390,844),(430,844),(768,1000),(1280,1000),(844,390)]:
  page.set_viewport_size({'width':width,'height':height});page.evaluate('document.fonts.ready');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  h=page.locator('#diary-shell h1');parent=h.locator('..').bounding_box();box=h.bounding_box();assert abs(box['x']+box['width']/2-(parent['x']+parent['width']/2))<1
  assert h.evaluate('(e)=>getComputedStyle(e).textAlign')=='center'
  assert page.locator('#today').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=18
  open_editor();box=page.locator('#widget-picker').bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1
  for control in row('cycle').locator('button').all():
   bounds=control.bounding_box();assert bounds['width']>=44 and bounds['height']>=44
  assert page.locator('#widget-picker').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),width
  close_editor()
 # No connection label on any main area, including while the browser is offline.
 for view in ['profile','diary','capture','library','friends']:
  page.locator('.bottom-nav [data-view='+view+']').click();assert page.locator('#connection').count()==0
 ctx.set_offline(True);page.locator('.bottom-nav [data-view=diary]').click();page.reload();open_editor();assert row('meditation').locator('[data-action=toggle]').get_attribute('aria-checked')=='true';close_editor()
 assert page.evaluate('state.dayMap.version')==2 and page.evaluate('state.dayMap.futureField')=='keep'
 assert not errors,errors;b.close();print('PASS: centered diary/date, no connection/edit button, cycle-first upgrade, one editor, full catalog, reorder, deactivate/reactivate without loss, new topic notes, phone controls and offline persistence')
