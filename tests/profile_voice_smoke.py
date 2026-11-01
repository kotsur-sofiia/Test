"""Profile autofill uses a mocked recognizer; actual microphone/provider is not tested."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8010/Test/')
MOCK='''window.__speech=[];class FakeSpeech{constructor(){window.__speech.push(this)}start(){queueMicrotask(()=>this.onstart?.())}stop(){}abort(){this.aborted=true}result(text){const r=[{transcript:text}];r.isFinal=true;this.onresult?.({results:[r]})}end(){this.onend?.()}}window.SpeechRecognition=FakeSpeech;window.webkitSpeechRecognition=undefined;'''
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1280,'height':1050},timezone_id='Europe/Podgorica');ctx.add_init_script(MOCK)
 ctx.add_init_script("""if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({profile:{name:'Прежнее имя',age:35,ageUnit:'years',weight:60,sex:'female',status:'none'},periods:['2026-10-10'],cycleLength:28,periodLength:5,sleep:[],meals:[],voiceNotes:[{id:'old-profile',section:'profile',date:'2026-10-01',text:'Прежняя заметка'}]}));""")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 assert page.locator('nav a').first.get_attribute('href')=='#profile'
 assert 'Обо мне' in page.locator('[data-menu="profile"] a').first.inner_text()
 assert page.locator('.bottom-nav a').first.inner_text()=='Профиль'
 assert page.locator('#profile-age-unit').count()==0
 assert page.get_by_label('Имя',exact=True).count()==1 and page.get_by_label('Имя или обращение',exact=True).count()==0
 assert page.locator('[data-voice-section="profile"]').count()==0
 root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true')
 assert root.locator('.voice-date').count()==0 and root.locator('.voice-history').count()==0
 before=page.evaluate('JSON.stringify(state.profile)')
 root.locator('.voice-start').click();assert page.locator('#profile-form button').is_disabled()
 page.evaluate("__speech.at(-1).result('Имя София, возраст 30 лет, не беременна, вес 42 килограмма')")
 assert page.locator('#profile-age').input_value()=='35', 'Autofill must wait for end of the whole utterance'
 root.locator('.voice-start').click();page.evaluate('__speech.at(-1).end()')
 for key,val in {'name':'София','age':'30','weight':'42','sex':'female','status':'none'}.items():assert page.locator('#profile-'+key).input_value()==val,key
 assert page.evaluate('JSON.stringify(state.profile)')==before
 assert not page.locator('#profile-form button').is_disabled()
 assert 'Сохранить профиль' in root.locator('.voice-status').inner_text()
 page.locator('#profile-form button').click()
 assert page.evaluate('state.profile.name')=='София' and page.evaluate('state.profile.age')==30 and page.evaluate('state.profile.ageUnit')=='years'
 assert page.evaluate('state.voiceNotes.length')==1,'Structured profile fill must not create general notes'
 # Partial labelled text does not clear omitted fields or infer sex from a name.
 page.locator('#profile-sex').select_option('male');page.locator('#profile-age').fill('41');page.locator('#profile-weight').fill('78')
 root.locator('.voice-editor').fill('Имя Павел');root.locator('.voice-save').click()
 assert page.locator('#profile-name').input_value()=='Павел' and page.locator('#profile-age').input_value()=='41'
 assert page.locator('#profile-weight').input_value()=='78' and page.locator('#profile-sex').input_value()=='male'
 root.locator('.voice-editor').fill('пол мужской, беременна, возраст 30 лет');root.locator('.voice-save').click()
 assert 'противоречат' in root.locator('.voice-profile-result').inner_text()
 assert page.locator('#profile-sex').input_value()=='male'
 root.locator('.voice-editor').fill('Имя Анна-Мария, мне тридцать пять лет, вешу сорок два целых пять десятых килограмма, готовлюсь к беременности');root.locator('.voice-save').click()
 assert page.locator('#profile-name').input_value()=='Анна-Мария'
 assert page.locator('#profile-weight').input_value()=='42.5' and page.locator('#profile-status').input_value()=='planning'
 root.locator('.voice-editor').fill('Имя Ирина, возраст 32 года, кормлю грудью, вес 60 килограммов');root.locator('.voice-save').click();page.locator('#profile-form button').click()
 assert page.evaluate('state.profile.status')=='lactating' and page.evaluate('reference("potassium").value')==2800
 # Manual changes made while the microphone is running take precedence over delayed speech.
 root.locator('.voice-editor').fill('');root.locator('.voice-start').click();page.locator('#profile-age').fill('34');page.locator('#profile-age').dispatch_event('change')
 page.evaluate("__speech.at(-1).result('Возраст 33 года, вес 61 килограмм');__speech.at(-1).end()")
 assert page.locator('#profile-age').input_value()=='34' and page.locator('#profile-weight').input_value()=='61'
 assert 'изменено вручную' in root.locator('.voice-profile-result').inner_text()
 assert page.evaluate('state.profile.age')==32,'Review still required after auto-insertion'
 print('PASS: user example autofill, spoken numbers, no implicit save, partial updates, no sex inference from names, conflicts, lactation, manual edits protected')
 # Legacy month-based profiles are never silently reinterpreted as years.
 page.evaluate("state.profile={name:'Ребёнок',age:7,ageUnit:'months',weight:7.5,sex:'female',status:'none'};save()")
 page.reload()
 assert page.locator('#profile-age').input_value()=='0'
 assert page.evaluate('reference("potassium")') is None
 assert 'Прежний возраст' in page.locator('#profile-age-hint').inner_text()
 page.locator('#profile-form button').click()
 assert page.evaluate('state.profile.ageUnit')=='years' and page.evaluate('state.profile.age')==0
 assert page.evaluate('state.profile.legacyAge.age')==7 and page.evaluate('reference("potassium")') is None
 assert page.evaluate('state.periods.length')==1 and page.evaluate('state.voiceNotes[0].id')=='old-profile'
 # Navigation destinations are distinct; the day link no longer points to the profile container.
 page.locator('.bottom-nav a[href="#home"]').click();assert page.evaluate('location.hash')=='#home'
 assert page.locator('#home').evaluate('(e)=>e.tagName')=='SECTION'
 page.locator('.bottom-nav a[href="#profile"]').click();assert page.evaluate('location.hash')=='#profile'
 page.wait_for_function('document.body.dataset.view==="profile"');assert page.locator('.bottom-nav a[href="#profile"]').evaluate('(e)=>e.classList.contains("active")')
 ctx.set_offline(True);page.reload();assert page.locator('#connection').inner_text()=='Без интернета'
 root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true');root.locator('.voice-editor').fill('Имя София, возраст 30 лет, не беременна, вес 42 килограмма');root.locator('.voice-save').click();page.locator('#profile-form button').click()
 assert page.evaluate('state.profile.age')==30 and page.evaluate('state.profile.weight')==42
 page.reload();assert page.locator('#profile-name').input_value()=='София'
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 assert not errors,errors
 ctx.close()
 # Speech unsupported: OS-keyboard dictation or pasted text can still be parsed locally.
 unsupported=browser.new_context();unsupported.add_init_script('window.SpeechRecognition=undefined;window.webkitSpeechRecognition=undefined;')
 page=unsupported.new_page();page.goto(URL);root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true')
 assert root.locator('.voice-start').is_disabled()
 root.locator('.voice-editor').fill('Имя София, возраст 30 лет, не беременна, вес 42 килограмма');root.locator('.voice-save').click()
 assert page.locator('#profile-age').input_value()=='30' and page.locator('#profile-weight').input_value()=='42'
 page.locator('#profile-form button').click();assert page.evaluate('state.profile.ageUnit')=='years'
 unsupported.close();browser.close()
 print('PASS: legacy age conversion and archive, under-one-year no guessed norms, profile/day menu anchors, offline parser + persistence, responsive UI, unsupported speech fallback')
