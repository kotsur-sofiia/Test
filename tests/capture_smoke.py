"""Unified dictation integration; speech API mocked, no actual microphone/provider."""
from playwright.sync_api import sync_playwright, expect
from datetime import datetime,timedelta
from pathlib import Path
import os,json
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8014/Test/')
MOCK="""window.__speech=[];window.SpeechRecognition=class{constructor(){__speech.push(this)}start(){this.onstart?.()}stop(){}abort(){this.aborted=true}result(t,final=true){const r=[{transcript:t}];r.isFinal=final;this.onresult?.({results:{0:r,length:1}})}end(){this.onend?.()}error(){this.onerror?.({error:'not-allowed'})}}"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
 ctx.add_init_script(MOCK);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL)
 page.wait_for_function('navigator.serviceWorker.controller!==null');nav=page.locator('.bottom-nav')
 assert nav.locator('a').all_text_contents()==['Профиль','Дневник','Голосовая запись','Библиотека','Друзья']
 nav.locator('[href="#capture"]').click();expect(page.locator('#capture')).to_be_visible();assert page.evaluate('__speech.length')==0
 root=page.locator('[data-voice-section="capture"]');editor=root.locator('.voice-editor');day=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d');root.locator('.voice-date').fill(day)
 root.locator('.voice-start').click();assert page.evaluate('__speech.at(-1).continuous') is False
 page.evaluate("__speech.at(-1).result('Ела лосось 300 грамм. Проснулась в 7:00. Силовая тренировка один час.',false);__speech.at(-1).end()")
 expect(page.locator('#capture-review')).to_be_visible();assert page.locator('.capture-item').count()==3
 assert page.evaluate('[state.meals.length,state.sleepEvents.length,state.workouts.length]')==[0,0,0]
 page.locator('#capture-review button[type=submit]').click();assert page.evaluate('[state.meals.length,state.sleepEvents.length,state.workouts.length]')==[1,1,1]
 assert page.evaluate('state.workouts[0].minutes')==60
 assert page.locator('#food-calories').inner_text()=='618 ккал'
 assert not page.locator('#capture-review').is_visible()
 page.get_by_role('link',name='Открыть сон',exact=True).click();expect(page.locator('#sleep')).to_be_visible();assert 'Пробуждение' in page.locator('#sleep-events').inner_text();assert page.locator('#sleep-average').inner_text()=='Нет записей'
 nav.locator('[href="#capture"]').click()
 def analyze(text):
  editor.fill(text);root.locator('.voice-save').click();expect(page.locator('#capture-review')).to_be_visible()
 def submit():page.locator('#capture-review button[type=submit]').click()
 analyze('Спала с восьми до шести');assert page.locator('[data-field="start"]').input_value()=='';submit();assert page.evaluate('state.sleep.length')==0
 page.locator('[data-field="start"]').fill(day+'T20:00');page.locator('[data-field="end"]').fill(day+'T23:00');submit();assert page.evaluate('state.sleep.length')==1;assert page.locator('#sleep-average').inner_text()=='3 ч 0 мин'
 # Overlaps are rejected atomically, including other entries in the same batch.
 analyze('Спала с 20:00 до 23:00. Ела рис 100 грамм');submit();assert 'пересекается' in page.locator('#capture-status').inner_text();assert page.evaluate('state.meals.length')==1
 analyze('съел рыбу 200 грамм, рис 100 грамм, овощи на пару, брокколи 100 грамм');assert page.locator('.capture-item').count()==4;submit()
 assert page.evaluate('state.meals.length')==3 and page.evaluate('state.voiceNotes.filter(n=>n.section==="food").length')==2
 assert page.locator('#food-calories').inner_text()=='783 ккал'
 # Stale review cannot be submitted after editing a transcript.
 analyze('Ела лосось 100 грамм');editor.fill('Не ела рыбу');assert not page.locator('#capture-review').is_visible()
 root.locator('.voice-save').click();assert page.locator('.capture-item h3').inner_text()=='Заметка';submit()
 assert page.evaluate('state.meals.length')==3
 analyze('Выпила воды 250 мл');submit();assert page.evaluate('state.water.at(-1).ml')==250
 # Storage failure rolls back every list and leaves the reviewed draft available.
 analyze('Ела лосось 100 грамм. Силовая тренировка 30 минут');before=page.evaluate('[state.meals.length,state.workouts.length]')
 page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("quota")}}');submit()
 assert page.evaluate('[state.meals.length,state.workouts.length]')==before and page.locator('#capture-review').is_visible()
 page.evaluate('()=>{Storage.prototype.setItem=realSet}');submit();assert page.evaluate('state.meals.length')==4
 # Navigation stops active capture and preserves its text. Late events cannot append.
 editor.fill('Черновик');root.locator('.voice-start').click();page.evaluate("__speech.at(-1).result('Новая фраза',false)")
 nav.locator('[href="#library"]').click();assert page.evaluate('__speech.at(-1).aborted') is True
 page.evaluate("__speech.at(-1).result('Поздний текст');__speech.at(-1).end()")
 nav.locator('[href="#capture"]').click();assert editor.input_value()=='Новая фраза'
 root.locator('.voice-start').click();page.evaluate('__speech.at(-1).error()');assert editor.input_value()=='Новая фраза'
 # Responsive targets, all five labels visible and no horizontal scroll.
 for width in [320,375,390,430,844]:
  page.set_viewport_size({'width':width,'height':844 if width<800 else 390});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  for link in nav.locator('a').all():assert link.bounding_box()['width']>=44 and link.bounding_box()['height']>=44
 page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/capture-mobile.png')
 ctx.set_offline(True);page.reload();expect(page.locator('#capture')).to_be_visible();assert page.evaluate('[state.meals.length,state.sleepEvents.length,state.workouts.length]')==[4,1,2]
 assert page.locator('#connection').inner_text()=='Без интернета'
 # Text-only export includes new record types.
 with page.expect_download() as download:page.locator('#export-data').click()
 data=json.loads(Path(download.value.path()).read_text());assert len(data['sleepEvents'])==1 and len(data['workouts'])==2
 assert not errors,errors
 b.close()
 print('PASS: five tabs, mixed interim speech, explicit review, meals/KBJU, standalone wake-up, sleep interval/overlap, workout minutes, water, unknown food notes, quota rollback, stale review, navigation cancellation, permission fallback, phone targets, offline persistence/export. Real speech not verified.')
