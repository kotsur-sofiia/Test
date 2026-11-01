"""Speech UI tests with a simulated browser recognizer; no real audio is captured."""
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime,timedelta
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8009/Test/')
MOCK='''window.__speech=[];class FakeSpeech{
 constructor(){window.__speech.push(this)}
 start(){this.started=true;queueMicrotask(()=>this.onstart?.())}
 stop(){this.stopped=true}abort(){this.aborted=true;this.abortCalls=(this.abortCalls||0)+1}
 result(parts){this.onresult?.({resultIndex:0,results:parts.map(p=>{const r=[{transcript:p.text}];r.isFinal=p.final;return r})})}
 end(){this.onend?.()}error(code){this.onerror?.({error:code})}
};window.SpeechRecognition=FakeSpeech;window.webkitSpeechRecognition=undefined;window.__FakeSpeech=FakeSpeech;'''
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1280,'height':1000},timezone_id='Europe/Podgorica');ctx.add_init_script(MOCK)
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 requests=[];page.on('request',lambda r:requests.append(r.url))
 page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 def widget(section):
  page.evaluate('(hash)=>location.hash=hash', 'sleep' if section=='sleep' else 'cycle' if section=='cycle' else 'food');page.wait_for_function('document.body.dataset.view==="diary"')
  root=page.locator(f'[data-voice-section="{section}"]');root.evaluate('(d)=>d.open=true');return root
 def emit(parts):page.evaluate('(parts)=>window.__speech.at(-1).result(parts)',parts)
 def end():page.evaluate('window.__speech.at(-1).end()')
 def phrase(root,text):
  root.locator('.voice-start').click();emit([{'text':text,'final':True}]);end()
 assert page.locator('.voice-card').count()==8
 assert page.evaluate('__speech.length')==0,'Microphone must never start automatically'
 sleep=widget('sleep');sleep.locator('.voice-editor').fill('Сегодня')
 sleep.locator('.voice-start').click()
 assert sleep.locator('.voice-start').get_attribute('aria-pressed')=='true'
 assert sleep.locator('.voice-save').is_disabled()
 assert page.locator('[data-voice-section="food"] .voice-start').is_disabled()
 emit([{'text':'спала спокойно','final':False}])
 assert sleep.locator('.voice-editor').input_value()=='Сегодня'
 assert 'Слышу' in sleep.locator('.voice-interim').inner_text()
 emit([{'text':'спала спокойно','final':True}]);emit([{'text':'спала спокойно','final':True}])
 assert sleep.locator('.voice-editor').input_value()=='Сегодня спала спокойно'
 sleep.locator('.voice-start').click()
 emit([{'text':'спала спокойно','final':True},{'text':'и хорошо отдохнула','final':True}]);end()
 assert sleep.locator('.voice-editor').input_value()=='Сегодня спала спокойно и хорошо отдохнула'
 assert page.evaluate('state.voiceNotes.length')==0
 sleep.locator('.voice-save').click();assert sleep.locator('.voice-note').count()==1
 assert page.evaluate('state.sleep.length')==0,'Free text must not create structured sleep records'
 original_id=page.evaluate('state.voiceNotes[0].id')
 sleep.get_by_role('button',name=f'Изменить заметку {original_id}',exact=True).click();phrase(sleep,'Дополнение');sleep.locator('.voice-save').click()
 assert page.evaluate('state.voiceNotes.length')==1 and page.evaluate('state.voiceNotes[0].id')==original_id
 assert 'Дополнение' in sleep.locator('.voice-history').inner_text()
 print('PASS: no automatic microphone use, interim/final speech, duplicate prevention, late final result on stop, explicit save, edit without duplicate, no guessed sleep data')
 # Existing text fields are filled, but their forms are never submitted.
 for section,target,text in [('food','local-product-search','овсяные'),('products','product-name','Творог'),('catalog','catalog-query','йогурт'),('supplements','supplement-name','Витамин D')]:
  root=widget(section);root.locator('.voice-target').select_option(target);phrase(root,text)
  assert page.locator('#'+target).input_value()==text
 assert page.locator('#food-product option').count()==1
 assert page.evaluate('state.meals.length')==0 and page.evaluate('state.products.length')==0 and page.evaluate('state.supplements.length')==0
 assert not any('world.openfoodfacts.org' in r for r in requests),'Dictation must not submit catalog searches'
 # Transcript content is plain text, never HTML.
 profile=widget('products');profile.locator('.voice-target').select_option('note');phrase(profile,'<img src=x onerror="window.__unsafe=true">');profile.locator('.voice-save').click()
 assert profile.locator('.voice-note img').count()==0
 assert '<img' in profile.locator('.voice-history').inner_text() and page.evaluate('window.__unsafe===undefined')
 cycle=widget('cycle');phrase(cycle,'Запись о самочувствии');cycle.locator('.voice-save').click();assert page.evaluate('state.periods.length')==0
 water=widget('water');phrase(water,'Выпила стакан воды');water.locator('.voice-save').click();assert page.evaluate('state.water.length')==0
 print('PASS: dictation to text fields in every form, no automatic catalog request or health calculation, plain-text rendering, separate section notes')
 # Errors recover without losing draft text. Late events from a failed recognizer are ignored.
 water.locator('.voice-editor').fill('Сохрани этот текст');water.locator('.voice-start').click();page.evaluate("window.__failedSpeech=__speech.at(-1);__failedSpeech.error('not-allowed')")
 assert 'не разрешён' in water.locator('.voice-status').inner_text()
 assert water.locator('.voice-editor').input_value()=='Сохрани этот текст' and not water.locator('.voice-start').is_disabled()
 page.evaluate("__failedSpeech.result([{text:'поздний чужой текст',final:true}])")
 assert water.locator('.voice-editor').input_value()=='Сохрани этот текст'
 water.locator('.voice-start').click();page.evaluate("__speech.at(-1).error('network')")
 assert 'интернет' in water.locator('.voice-status').inner_text()
 # Closing a section stops recording; reopening permits a clean new session.
 water.locator('.voice-start').click();water.evaluate('(d)=>d.open=false');page.wait_for_function('window.__speech.at(-1).aborted===true')
 water=widget('water');assert not water.locator('.voice-start').is_disabled()
 # A delayed permission grant after cancellation must not leave the microphone running.
 page.evaluate('()=>{window.__originalSpeechStart=__FakeSpeech.prototype.start;__FakeSpeech.prototype.start=function(){this.started=true}}')
 water.locator('.voice-start').click();water.locator('.voice-start').click()
 page.evaluate('__speech.at(-1).onstart()')
 assert page.evaluate('__speech.at(-1).abortCalls')==2
 page.evaluate('()=>{__FakeSpeech.prototype.start=window.__originalSpeechStart}')
 # Local storage errors must not falsely report successful save or discard the draft.
 before=page.evaluate('state.voiceNotes.length')
 page.evaluate("()=>{window.__originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}}")
 water.locator('.voice-save').click()
 assert 'Не удалось сохранить' in water.locator('.voice-status').inner_text()
 assert water.locator('.voice-editor').input_value()=='Сохрани этот текст' and page.evaluate('state.voiceNotes.length')==before
 page.evaluate('()=>{Storage.prototype.setItem=window.__originalSet}');water.locator('.voice-save').click();assert page.evaluate('state.voiceNotes.length')==before+1
 assert page.locator('#notice').inner_text()==''
 print('PASS: permission/network errors, ignored stale results, stop on collapse, persistence error rollback with draft intact')
 # A changed parent diary day must not silently redate a pending draft.
 food=widget('food');food.locator('.voice-target').select_option('note');food.locator('.voice-editor').fill('Черновик за прежний день')
 today=page.evaluate('today');yesterday=(datetime.strptime(today,'%Y-%m-%d')-timedelta(days=1)).strftime('%Y-%m-%d')
 page.locator('#food-date').fill(yesterday);page.locator('#food-date').dispatch_event('change')
 assert food.locator('.voice-date').input_value()==today
 assert 'прежняя дата' in food.locator('.voice-status').inner_text()
 food.locator('.voice-save').click();assert page.evaluate("state.voiceNotes.find(n=>n.section==='food').date")==today
 food.locator('.voice-date').fill(yesterday);food.locator('.voice-date').dispatch_event('change');food.locator('.voice-start').click()
 page.locator('#food-date').fill(today);page.locator('#food-date').dispatch_event('change')
 assert page.evaluate('__speech.at(-1).aborted') is True
 emit([{'text':'этот поздний результат не нужен','final':True}]);assert food.locator('.voice-editor').input_value()==''
 assert food.locator('.voice-date').input_value()==yesterday
 # Changing profile to hide the cycle also stops its microphone.
 cycle.locator('.voice-start').click();page.evaluate("state.profile={name:'Тест',sex:'male',age:35,ageUnit:'years',weight:70,status:'none'};save()")
 assert page.evaluate('__speech.at(-1).aborted') is True
 assert not page.locator('#cycle').is_visible()
 print('PASS: explicit note dates, draft date retained across diary navigation, stale date results ignored, microphone stopped when a section is hidden')
 with page.expect_download() as download:page.locator('#export-data').click()
 data=json.loads(Path(download.value.path()).read_text());assert len(data['voiceNotes'])==before+2
 assert all(isinstance(n['text'],str) and 'audio' not in n for n in data['voiceNotes'])
 ctx.set_offline(True);page.reload()
 assert page.locator('.voice-card').count()==8 and page.locator('#connection').inner_text()=='Без интернета'
 sleep=widget('sleep');assert 'Дополнение' in sleep.locator('.voice-history').inner_text()
 note_id=page.evaluate("state.voiceNotes.find(n=>n.section==='sleep').id")
 sleep.get_by_role('button',name=f'Удалить заметку {note_id}',exact=True).click();page.reload();sleep=widget('sleep');assert sleep.locator('.voice-note').count()==0
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 assert not errors,errors
 print('PASS: JSON text-only export, offline voice module, saved notes, deletion persistence, responsive layouts, no browser errors')
 ctx.close()
 # Unsupported browser: readable fallback, no microphone request, keyboard text still saved.
 unsupported=browser.new_context();unsupported.add_init_script('window.SpeechRecognition=undefined;window.webkitSpeechRecognition=undefined;')
 page=unsupported.new_page();page.goto(URL.split('#')[0]+'#sleep');root=page.locator('[data-voice-section="sleep"]');root.evaluate('(d)=>d.open=true')
 assert root.locator('.voice-start').is_disabled() and 'клавиатуры' in root.locator('.voice-status').inner_text()
 root.locator('.voice-editor').fill('Текст с клавиатуры');root.locator('.voice-save').click();assert root.locator('.voice-note').count()==1
 unsupported.close()
 # Safari-style prefixed API path and synchronous start denial.
 prefixed=browser.new_context();prefixed.add_init_script(MOCK+'window.webkitSpeechRecognition=FakeSpeech;window.SpeechRecognition=undefined;')
 page=prefixed.new_page();page.goto(URL.split('#')[0]+'#sleep');root=page.locator('[data-voice-section="sleep"]');root.evaluate('(d)=>d.open=true');root.locator('.voice-start').click()
 page.evaluate("__speech.at(-1).result([{text:'Проверка префикса',final:true}]);__speech.at(-1).end()")
 assert root.locator('.voice-editor').input_value()=='Проверка префикса'
 page.evaluate("()=>{window.__FakeSpeech.prototype.start=function(){throw new DOMException('denied','NotAllowedError')}}")
 root.locator('.voice-start').click();assert 'не разрешён' in root.locator('.voice-status').inner_text() and not root.locator('.voice-start').is_disabled()
 prefixed.close();browser.close()
 print('PASS: unsupported-browser keyboard fallback, webkit API, synchronous microphone denial. Real microphone/provider recognition NOT verified.')
