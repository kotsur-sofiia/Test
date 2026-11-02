from profile_form import open_period_editor
from playwright.sync_api import sync_playwright
from datetime import datetime,timedelta
import os
from pathlib import Path
Path("/tmp/luna-check").mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1440,'height':1050},timezone_id='Europe/Podgorica')
 page=ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.environ.get('LUNA_TEST_URL', 'http://127.0.0.1:8001/Test/'));page.wait_for_function('navigator.serviceWorker.controller !== null')
 page.evaluate("state.profile={name:'Тест',sex:'female',age:35,ageUnit:'years',weight:60,status:'none',month:null};save()")
 assert page.locator('#cycle-summary').inner_text()=='Познакомимся?'
 today=datetime.strptime(page.evaluate('today'),'%Y-%m-%d')
 day=lambda n:(today+timedelta(days=n)).strftime('%Y-%m-%d')
 page.evaluate('location.hash="cycle"');page.wait_for_function('document.body.dataset.view==="diary"')
 open_period_editor(page);page.locator('#period-start').fill(day(-20));page.get_by_role('button',name='Сохранить даты',exact=True).click()
 assert page.locator('#cycle-summary').inner_text()=='День 21 цикла'
 for offset,key in [(0,'menstrual'),(5,'follicular'),(13,'ovulation'),(20,'luteal'),(28,'menstrual')]:
  assert page.evaluate(f'phaseAt("{day(-20+offset)}").key')==key
 assert page.evaluate(f'phaseAt("{day(-21)}")') is None
 page.reload();assert page.locator('#cycle-summary').inner_text()=='День 21 цикла'
 print('PASS: period history, four estimated phases, repeated-cycle prediction, no pre-history prediction, persistence')
 page.evaluate('location.hash="sleep"');page.wait_for_function('document.querySelector("#sleep").hidden===false')
 def sleep(start,end,kind='night'):
  page.locator('#sleep-start').fill(start);page.locator('#sleep-end').fill(end);page.locator('#sleep-type').select_option(kind);page.locator('#sleep-form button').click()
 sleep(day(-2)+'T22:00',day(-1)+'T06:00')
 sleep(day(-1)+'T14:00',day(-1)+'T15:00','nap')
 sleep(day(-3)+'T22:00',day(-2)+'T05:00')
 assert page.locator('#sleep-average').inner_text()=='8 ч 0 мин'
 sleep(day(-1)+'T14:30',day(-1)+'T16:00','nap')
 assert 'пересекается' in page.locator('#sleep-error').inner_text()
 assert page.locator('#sleep-average').inner_text()=='8 ч 0 мин'
 sleep(day(-1)+'T12:00',day(-1)+'T11:00')
 assert 'позже' in page.locator('#sleep-error').inner_text()
 for period in ['30','365']:
  page.locator('#sleep-range').select_option(period);assert page.locator('#sleep-average').inner_text()=='8 ч 0 мин'
 page.evaluate('location.hash="food"');page.wait_for_function('document.querySelector("#food").hidden===false');page.locator('#food-product').select_option('oats');page.locator('#food-grams').fill('200');page.locator('#food-form button').click()
 assert page.locator('#food-calories').inner_text()=='758 ккал'
 assert '8,5 / 18 мг · 47%' in page.locator('#nutrients').inner_text()
 page.locator('#food-date').fill(day(-1));page.locator('#food-date').dispatch_event('change');assert page.locator('#food-calories').inner_text()=='0 ккал'
 page.locator('#food-date').fill(day(0));page.locator('#food-date').dispatch_event('change');assert page.locator('#food-calories').inner_text()=='758 ккал'
 print('PASS: overnight sleep, naps, mean by recorded days, overlap and invalid-range rejection, 7/30/365 days, food gram scaling and daily isolation')
 with page.expect_download() as d:page.locator('#export-data').click()
 assert d.value.suggested_filename.startswith('woman-diary-')
 ctx.set_offline(True);page.reload();assert page.evaluate('navigator.onLine') is False;assert page.locator('#sleep-average').inner_text()=='8 ч 0 мин';assert page.locator('#food-calories').inner_text()=='758 ккал'
 page.locator('#food-history button').click();assert page.locator('#food-calories').inner_text()=='0 ккал';page.reload();assert page.locator('#food-calories').inner_text()=='0 ккал'
 ctx.set_offline(False)
 print('PASS: backup export, offline reload, offline deletion and persistence')
 page.evaluate('scrollTo(0,0)');page.screenshot(path='/tmp/luna-check/desktop.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.reload();assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.screenshot(path='/tmp/luna-check/mobile.png',full_page=True)
 for width in [768,1024]:
  page.set_viewport_size({'width':width,'height':1024});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 assert not errors,errors
 print('PASS: responsive layouts at 390/768/1024, no browser script errors')
 browser.close()
