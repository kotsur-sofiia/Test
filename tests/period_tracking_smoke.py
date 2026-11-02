from profile_form import open_period_editor
"""Start/end dates, continued delay, revised cycle presentation and natural image tiles."""
from playwright.sync_api import sync_playwright,expect
from datetime import datetime,timezone
from pathlib import Path
import os,json
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8037/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-01'],cycleLength:32,periodLength:5,sleep:[],meals:[],legacyExtra:'keep',voiceNotes:[{id:'old-cycle-note',section:'cycle',date:'2026-10-01',text:'Прежняя заметка'}]}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,4,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.locator('#calendar,.cycle-calendar-area,#cycle .voice-card,#selected-date,.privacy-details,footer>span').count()==0
 assert page.locator('.voice-card').count()==7
 assert page.locator('#cycle-dial-day').inner_text()=='35'
 assert page.locator('.cycle-day-label').inner_text()=='день цикла'
 assert page.locator('#cycle-countdown-label').inner_text()=='ЗАДЕРЖКА' and page.locator('#cycle-countdown-value').inner_text()=='2 дня'
 assert page.evaluate('state.periodEnds')=={}
 open_period_editor(page)
 assert page.locator('#period-start').input_value()=='01.10.2026'
 def save():
  page.locator('#cycle-form button[type=submit]').click();open_period_editor(page)
 for value in ['31.04.2026','30.09.2026','05.11.2026']:
  page.locator('#period-end').fill(value);save();assert page.locator('#period-form-error').inner_text();assert page.evaluate('state.periodEnds')=={}
 page.locator('#period-end').fill('05102026');save();assert page.locator('#period-end').input_value()=='05.10.2026'
 assert page.evaluate('state.periodEnds["2026-10-01"]')=='2026-10-05' and page.locator('#cycle-countdown-value').inner_text()=='2 дня'
 page.locator('#period-end-calendar').fill('2026-10-06');page.locator('#period-end-calendar').dispatch_event('change');assert page.locator('#period-end').input_value()=='06.10.2026';save();assert page.evaluate('state.periods.length')==1
 page.locator('#period-end').fill('');page.locator('#period-start').fill('20.10.2026');save();assert page.locator('#period-form-error').inner_text()==''
 assert page.evaluate('state.periods.length')==2 and page.evaluate('state.periodEnds["2026-10-20"]??null') is None
 assert page.locator('#cycle-dial-day').inner_text()=='16' and page.locator('#cycle-countdown-label').inner_text()=='до менструации'
 page.locator('#period-end').fill('25.10.2026');save()
 page.get_by_role('button',name='Изменить даты 01.10.2026',exact=True).click();assert page.locator('#period-end').input_value()=='06.10.2026'
 page.locator('#period-end').fill('22.10.2026');save();assert 'пересекаются' in page.locator('#period-form-error').inner_text()
 assert page.evaluate('state.periodEnds["2026-10-01"]')=='2026-10-06'
 before=page.evaluate('JSON.stringify([state.periods,state.periodEnds,state.cycleLength])');page.locator('#period-end').fill('08.10.2026')
 page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("full")}}');save();assert page.evaluate('JSON.stringify([state.periods,state.periodEnds,state.cycleLength])')==before;assert page.locator('#period-end').input_value()=='08.10.2026';assert 'Не удалось' in page.locator('#period-form-error').inner_text()
 page.evaluate('()=>{Storage.prototype.setItem=realSet}');save();assert page.evaluate('state.periodEnds["2026-10-01"]')=='2026-10-08'
 page.get_by_role('button',name='Удалить отметку 2026-10-20',exact=True).click();assert page.evaluate('state.periodEnds["2026-10-20"]??null') is None;assert page.locator('#cycle-dial-day').inner_text()=='35' and page.locator('#cycle-countdown-value').inner_text()=='2 дня'
 page.locator('#period-end').fill('');page.locator('#period-start').fill('04.11.2026');save();assert page.locator('#cycle-dial-day').inner_text()=='1';assert page.locator('#cycle-countdown-label').inner_text()=='до менструации'
 assert page.locator('#cycle-phase-name').inner_text()=='МЕНСТРУАЛЬНАЯ' and page.locator('#cycle-phase-word').inner_text()=='фаза'
 assert page.evaluate('state.periodEnds["2026-11-04"]??null') is None
 page.locator('#period-dialog-close').click()
 assert page.locator('.mini .nature-topic-image').count()>=11
 first=page.locator('[data-widget-id=cycle] .nature-topic-image');assert 'nature-topics.webp' in first.evaluate('(e)=>getComputedStyle(e).backgroundImage')
 for width in [320,375,390,430,768,1280]:
  page.set_viewport_size({'width':width,'height':1000});page.evaluate('document.fonts.ready');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  assert page.locator('#cycle-phase-name').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),width
  assert page.locator('.layout main').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgba(0, 0, 0, 0)'
  cards=[page.locator('#diary-shell'),page.locator('.cycle-dial-card'),page.locator('.cycle-recommendations')]
  for previous,next_card in zip(cards,cards[1:]):assert abs(next_card.bounding_box()['y']-previous.bounding_box()['y']-previous.bounding_box()['height'])<2,width
  for field in page.locator('#cycle-form input').all():assert field.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
  assert float(page.locator('.bottom-nav').evaluate('(e)=>getComputedStyle(e).borderTopLeftRadius').replace('px',''))>=38
 with page.expect_download() as download:page.locator('#export-data').click()
 data=json.loads(Path(download.value.path()).read_text());assert data['periodEnds']['2026-10-01']=='2026-10-08' and data['legacyExtra']=='keep' and data['voiceNotes'][0]['id']=='old-cycle-note'
 ctx.set_offline(True);page.reload();expect(page.locator('#cycle')).to_be_visible();assert page.evaluate('caches.match(new URL("./assets/nature-topics.webp",location.href)).then(Boolean)')
 assert page.evaluate('state.periodEnds["2026-10-01"]')=='2026-10-08'
 page.clock.fast_forward(17*24*60*60*1000);page.clock.fast_forward(17*24*60*60*1000);assert page.locator('#cycle-dial-day').inner_text()=='35' and page.locator('#cycle-countdown-label').inner_text()=='ЗАДЕРЖКА' and page.locator('#cycle-countdown-value').inner_text()=='2 дня'
 assert not errors,errors;b.close();print('PASS: separate start/end dates, manual and native date entry, validation/overlap/rollback, no invented end, 32-day delay and reset, no cycle dictation/calendar, photo tiles, continuous chapter transitions, responsive surfaces, export/offline/midnight')
