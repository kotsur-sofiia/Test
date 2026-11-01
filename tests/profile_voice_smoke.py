"""Profile DOB autofill and legacy migration; recognition is mocked."""
from playwright.sync_api import sync_playwright
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8015/Test/')
MOCK="""window.__speech=[];window.SpeechRecognition=class{constructor(){__speech.push(this)}start(){this.onstart?.()}stop(){}abort(){}result(t){const r=[{transcript:t}];r.isFinal=true;this.onresult?.({results:[r]})}end(){this.onend?.()}}"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1280,'height':1050});ctx.add_init_script(MOCK)
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-10'],sleep:[],meals:[],profile:{name:'Прежнее имя',age:35,ageUnit:'years',sex:'female',weight:64,status:'none'}}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null')
 assert page.locator('#profile-birthDate').input_value()=='' and page.locator('#profile-weight').input_value()=='64'
 assert page.locator('#profile-age').count()==0
 root=page.locator('[data-voice-section="profile-fill"]');root.evaluate('(d)=>d.open=true')
 before=page.evaluate('JSON.stringify(state.profile)');root.locator('.voice-start').click();assert page.locator('#profile-form button').is_disabled()
 page.evaluate("__speech.at(-1).result('Имя София, дата рождения 2 ноября 1996, не беременна, вес 42 килограмма')")
 assert page.locator('#profile-birthDate').input_value()==''
 page.evaluate('__speech.at(-1).end()');assert page.locator('#profile-birthDate').input_value()=='1996-11-02' and page.locator('#profile-weight').input_value()=='42'
 assert page.evaluate('JSON.stringify(state.profile)')==before
 page.locator('#profile-form button').click();assert page.evaluate('state.profile.birthDate')=='1996-11-02' and page.evaluate('state.profile.legacyAge.age')==35
 root.locator('.voice-editor').fill('Возраст 30 лет');root.locator('.voice-save').click();assert page.locator('#profile-birthDate').input_value()=='1996-11-02';assert 'не вычисляется' in root.locator('.voice-profile-result').inner_text()
 # Protect a birth date manually changed during speech.
 root.locator('.voice-start').click();page.locator('#profile-birthDate').fill('1990-01-01');page.evaluate("__speech.at(-1).result('Дата рождения 2 ноября 1995, вес 61 килограмм');__speech.at(-1).end()")
 assert page.locator('#profile-birthDate').input_value()=='1990-01-01' and page.locator('#profile-weight').input_value()=='61'
 assert 'изменено вручную' in root.locator('.voice-profile-result').inner_text()
 root.locator('.voice-profile-field').select_option('birthDate');root.locator('.voice-editor').fill('29 февраля 2000');root.locator('.voice-save').click();assert page.locator('#profile-birthDate').input_value()=='2000-02-29'
 root.locator('.voice-editor').fill('31 февраля 2000');root.locator('.voice-save').click();assert page.locator('#profile-birthDate').input_value()=='2000-02-29'
 page.locator('#profile-form button').click();ctx.set_offline(True);page.reload();assert page.locator('#profile-birthDate').input_value()=='2000-02-29' and page.evaluate('state.periods.length')==1
 assert not errors,errors;b.close()
 print('PASS: DOB dictation, no guessed birthday from old age, explicit save, legacy archive, manual edit protection, individual date field, invalid calendar date, offline persistence')
