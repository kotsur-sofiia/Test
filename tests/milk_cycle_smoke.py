"""Milk sand, centred day, conditional late luteal label and clean diary UI."""
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright,expect
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8045/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 c.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-01'],periodEnds:{'2026-10-01':'2026-10-06'},cycleLength:32,periodLength:5,sleep:[],meals:[],dayMap:{version:2,topicRailVersion:1,order:['cycle','food','skin','books'],notes:[{id:'kept',topic:'books',date:'2026-11-03',text:'Запись сохранена'}]}}))")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.clock.install(time=datetime(2026,11,3,12,tzinfo=timezone.utc));page.goto(URL+'#cycle');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.locator('#cycle-care-source,.cycle-date-row').count()==0
 assert page.locator('#cycle-dial-day').text_content()=='34'
 assert page.locator('#cycle-phase-name').text_content()=='ЛЮТЕИНОВАЯ'
 assert page.locator('#cycle-countdown-label').text_content()=='ЗАДЕРЖКА' and page.locator('#cycle-countdown-value').text_content()=='1 день'
 assert page.evaluate('WomanCycleModel.snapshot({date:localDate(),periods:state.periods,length:32,periodLength:5,predict:true}).phase') is None
 for width in [320,390,768,1280]:
  page.set_viewport_size({'width':width,'height':900});page.evaluate('document.fonts.ready')
  dial=page.locator('#cycle-dial').bounding_box();number=page.locator('#cycle-dial-day').bounding_box()
  assert abs(number['x']+number['width']/2-dial['x']-dial['width']/2)<1
  assert abs(number['y']+number['height']/2-dial['y']-dial['height']/2)<1
  assert page.locator('#cycle-dial-day').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=96
  assert page.locator('#cycle-pearl-marker image').get_attribute('href')=='./assets/reference-cycle-pearl.webp'
  assert page.locator('.sand-cycle-ring').get_attribute('src')=='./assets/natural-sand-trail.webp'
  assert page.locator('#cycle-phase-name').bounding_box()['y']<number['y']
  assert page.locator('.cycle-day-label').bounding_box()['y']>number['y']+number['height']
  assert 'shore-canvas.svg' in page.locator('body').evaluate('(e)=>getComputedStyle(e,"::before").backgroundImage')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 # Deactivation stays quiet on the diary and keeps personal notes.
 page.locator('#add-widget').click();page.locator('[data-topic=books] [role=switch]').click();page.locator('#widget-picker [data-close-dialog]').click()
 assert 'Тема выключена' not in page.locator('main').inner_text() and page.locator('#day-builder-status').inner_text()==''
 assert page.evaluate('state.dayMap.notes[0].id')=='kept'
 # The presentation remains luteal through another midnight; a real new start resets it.
 page.clock.fast_forward(24*60*60*1000);assert page.locator('#cycle-phase-name').text_content()=='ЛЮТЕИНОВАЯ'
 assert page.locator('#cycle-dial-day').text_content()=='35' and page.locator('#cycle-countdown-value').text_content()=='2 дня'
 page.locator('#cycle-start-action').click();page.locator('#period-start').fill('04.11.2026');page.locator('#period-end').fill('');page.locator('#cycle-form button').click()
 assert page.locator('#cycle-dial-day').text_content()=='1' and page.locator('#cycle-phase-name').text_content()=='МЕНСТРУАЛЬНАЯ'
 assert page.evaluate('state.periodEnds["2026-10-01"]')=='2026-10-06'
 page.locator('.bottom-nav [data-view=diary]').click();assert page.evaluate('location.hash')=='#home'
 c.set_offline(True);page.reload();expect(page.locator('#cycle')).to_be_visible()
 assert page.locator('#cycle-dial-day').text_content()=='1'
 assert page.evaluate('caches.match(new URL("./milk-sand.css?v=72",location.href)).then(Boolean)')
 assert not errors,errors;b.close();print('PASS: continuous milk sand, matching editorial heading, no obsolete labels, centred enlarged number, sand groove and warm pearl with contact shadow, quiet deactivation, conditional luteal delay, midnight/reset and offline')
