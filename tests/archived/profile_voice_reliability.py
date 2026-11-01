"""Regression tests for Safari-like speech events, recovery and short field dictation."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8011/Test/')
MOCK='''window.__speech=[];class Speech{constructor(){__speech.push(this)}start(){queueMicrotask(()=>this.onstart?.())}stop(){}abort(){this.aborted=true}emit(text,final=true){const r=[{transcript:text}];r.isFinal=final;this.onresult?.({results:{0:r,length:1}})}end(){this.onend?.()}error(code){this.onerror?.({error:code})}}window.webkitSpeechRecognition=Speech;window.SpeechRecognition=undefined;'''
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1280,'height':1050});ctx.add_init_script(MOCK)
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true')
 def emit(text,final=True):page.evaluate('(p)=>__speech.at(-1).emit(p.text,p.final)',{'text':text,'final':final})
 def end():page.evaluate('__speech.at(-1).end()')
 root.locator('.voice-start').click();assert page.evaluate('__speech.at(-1).continuous') is False
 emit('Имя София, дата рождения 2 ноября 1996, 42 килограмма, не беременна',False)
 assert page.locator('#profile-birthDate').input_value()==''
 end()
 assert page.locator('#profile-name').input_value()=='София' and page.locator('#profile-birthDate').input_value()=='1996-11-02'
 assert page.locator('#profile-weight').input_value()=='42' and page.locator('#profile-status').input_value()=='none'
 assert 'не подтвердил' in root.locator('.voice-profile-result').inner_text()
 assert page.evaluate('typeof state.profile==="undefined" || state.profile===null')
 # A retry replaces the bad old phrase, with an explicit restore action.
 first=root.locator('.voice-editor').input_value();root.locator('.voice-start').click();assert root.locator('.voice-editor').input_value()==''
 emit('Дата рождения 2 ноября 1995');end();assert page.locator('#profile-birthDate').input_value()=='1995-11-02'
 assert root.locator('.voice-editor').input_value()=='Дата рождения 2 ноября 1995'
 root.locator('.voice-restore').click();assert root.locator('.voice-editor').input_value()==first
 # Some engines replace a final slot instead of extending the result list.
 root.locator('.voice-start').click();emit('Дата рождения 2 ноября 1996');emit('Дата рождения 2 ноября 1994');end()
 assert page.locator('#profile-birthDate').input_value()=='1994-11-02'
 assert root.locator('.voice-editor').input_value()=='Дата рождения 2 ноября 1994'
 # Stop without onend: watchdog must still use the captured text and fill the form.
 root.locator('.voice-start').click();emit('вес 43 килограмма');root.locator('.voice-start').click()
 page.wait_for_function('document.querySelector("#profile-weight").value==="43"')
 end();assert page.locator('#profile-weight').input_value()=='43'
 print('PASS: prefixed/non-iterable result list, single phrase, interim-only completion, replacement results, retry without mixing and stop watchdog fills fields')
 for field,spoken,expected in [('name','Ольга','Ольга'),('birthDate','2 ноября 1991','1991-11-02'),('weight','Сорок два с половиной','42.5'),('sex','Женский','female'),('status','Кормлю грудью','lactating')]:
  root.locator('.voice-profile-field').select_option(field);root.locator('.voice-start').click();emit(spoken);end()
  assert page.locator('#profile-'+field).input_value()==expected,field
 assert 'Возраст: 35' not in root.locator('.voice-profile-result').inner_text(), 'Only the selected field should be updated'
 assert page.locator('#profile-birthDate').input_value()=='1991-11-02'
 assert page.locator('#profile-weight').input_value()=='42.5'
 # API/network errors preserve a useful partial transcript without auto-applying it.
 root.locator('.voice-profile-field').select_option('weight');root.locator('.voice-start').click();emit('сорок четыре',False);page.evaluate("__speech.at(-1).error('network')")
 assert root.locator('.voice-editor').input_value()=='сорок четыре'
 assert page.locator('#profile-weight').input_value()=='42.5'
 root.locator('.voice-save').click();assert page.locator('#profile-weight').input_value()=='44'
 # A denied new attempt must restore the previous transcript rather than erase it.
 previous=root.locator('.voice-editor').input_value();page.evaluate("()=>{window.__originalStart=webkitSpeechRecognition.prototype.start;webkitSpeechRecognition.prototype.start=function(){throw new DOMException('denied','NotAllowedError')}}")
 root.locator('.voice-start').click();assert root.locator('.voice-editor').input_value()==previous
 assert 'не разрешён' in root.locator('.voice-status').inner_text()
 root.locator('.voice-keyboard').click();assert root.locator('.voice-editor').evaluate('(e)=>e===document.activeElement')
 page.evaluate('()=>{webkitSpeechRecognition.prototype.start=window.__originalStart}')
 page.locator('#profile-form button').click();assert page.evaluate('state.profile.weight')==44 and page.evaluate('state.profile.status')=='lactating'
 # A recognizer may emit results before it ever reports onstart.
 page.evaluate('()=>{window.__savedStart=webkitSpeechRecognition.prototype.start;webkitSpeechRecognition.prototype.start=function(){}}')
 root.locator('.voice-profile-field').select_option('weight');root.locator('.voice-start').click();emit('сорок пять')
 assert root.locator('.voice-start span').inner_text()=='Остановить'
 root.locator('.voice-start').click();page.wait_for_function('document.querySelector("#profile-weight").value==="45"')
 page.evaluate('()=>{webkitSpeechRecognition.prototype.start=window.__savedStart}')
 # Continuation is opt-in, not an accidental mixture with the previous recording.
 root.locator('.voice-profile-field').select_option('all');root.locator('.voice-editor').fill('Имя Ольга');root.locator('.voice-continue').check()
 root.locator('.voice-start').click();emit('дата рождения 2 ноября 1990');end()
 assert root.locator('.voice-editor').input_value()=='Имя Ольга дата рождения 2 ноября 1990'
 assert page.locator('#profile-birthDate').input_value()=='1990-11-02'
 ctx.set_offline(True);page.reload();assert page.locator('#connection').inner_text()=='Без интернета'
 root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true');root.locator('.voice-profile-field').select_option('weight');root.locator('.voice-editor').fill('45');root.locator('.voice-save').click();assert page.locator('#profile-weight').input_value()=='45'
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 root.screenshot(path='/tmp/luna-check/profile-voice-improved.png')
 assert not errors,errors
 b.close()
 print('PASS: individual fields, network/permission recovery, keyboard focus fallback, opt-in continuation, explicit profile save, offline parsing, responsive UI. Real audio not verified.')
