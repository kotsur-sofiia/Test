"""Title-led navigation and a transactional, dates-only native dialog."""
from playwright.sync_api import sync_playwright, expect
from datetime import datetime,timezone
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8042/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 c.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({sleep:[],meals:[],periods:['2026-10-13'],cycleLength:32,periodLength:6,extra:'keep'}))")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL+'#cycle');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.locator('.app-backdrop,#today,#cycle-dial-date,#cycle-length,#period-length').count()==0
 expect(page.locator('#period-dialog')).not_to_be_visible()
 expect(page.locator('#cycle-start-action')).to_be_visible()
 assert page.locator('.cycle-recommendations h2').inner_text()=='Рекомендации'
 before=page.evaluate('JSON.stringify(state)')
 page.locator('#cycle-start-action').click();expect(page.locator('#period-dialog')).to_be_visible()
 assert page.locator('#period-dialog input[type=text]').count()==2
 assert page.locator('#period-dialog input[type=number]').count()==0
 page.locator('#period-end').fill('31.04.2026');page.locator('#cycle-form button').click()
 expect(page.locator('#period-dialog')).to_be_visible();assert page.locator('#period-form-error').inner_text();assert page.evaluate('JSON.stringify(state)')==before
 page.locator('#period-end').fill('18.10.2026');page.locator('#period-dialog-close').click()
 assert page.evaluate('JSON.stringify(state)')==before
 page.locator('#cycle-start-action').click();expect(page.locator('#period-end')).to_have_value('18.10.2026')
 page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("full")}}')
 page.locator('#cycle-form button').click();expect(page.locator('#period-dialog')).to_be_visible()
 assert 'Не удалось' in page.locator('#period-form-error').inner_text() and page.evaluate('JSON.stringify(state)')==before
 page.evaluate('()=>{Storage.prototype.setItem=realSet}');page.locator('#cycle-form button').click();expect(page.locator('#period-dialog')).not_to_be_visible()
 assert page.evaluate('state.periodEnds["2026-10-13"]')=='2026-10-18'
 assert page.evaluate('[state.cycleLength,state.periodLength,state.extra]')==[32,6,'keep']
 page.locator('#cycle-start-action').click();page.keyboard.press('Escape');expect(page.locator('#period-dialog')).not_to_be_visible()
 for width in [320,390,768,1280]:
  page.set_viewport_size({'width':width,'height':844})
  for route,title in [('account','Профиль'),('settings','Настройки'),('library','Библиотека'),('friends','Друзья'),('capture','Голосовая запись'),('cycle','Дневник')]:
   page.goto(URL+'#'+route);expect(page.locator('#page-title')).to_have_text(title)
   assert page.locator('#page-title').bounding_box()['y']<80 and page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route)
  gap=page.locator('#cycle-dial').bounding_box()['y']-sum(page.locator('#diary-shell').bounding_box()[key] for key in ['y','height'])
  assert gap<=90,(width,gap)
  page.locator('#cycle-start-action').click();box=page.locator('#period-dialog').bounding_box();assert box['x']>=0 and box['width']<=width and box['height']<=844
  page.evaluate('location.hash="library"');expect(page.locator('#period-dialog')).not_to_be_visible()
 page.goto(URL+'#cycle-form');expect(page.locator('#period-dialog')).to_be_visible();page.locator('#period-dialog-close').click()
 page.goto(URL+'#cycle');c.set_offline(True);page.reload();page.locator('#cycle-start-action').click();expect(page.locator('#period-dialog')).to_be_visible()
 assert page.evaluate('state.periodEnds["2026-10-13"]')=='2026-10-18'
 assert not errors,errors;b.close();print('PASS: title-led routes, no decorative dates/global foliage, compact spacing, dates-only modal, close/Escape/navigation, drafts, validation, quota rollback, unchanged cycle lengths and offline persistence')
