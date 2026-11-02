"""Single dotted DOB, female defaults, exact health choices, legacy preservation."""
from playwright.sync_api import sync_playwright,expect
from profile_form import fill_birth_date,open_about
from datetime import datetime,timezone
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8038/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,locale='ru-RU',timezone_id='Europe/Podgorica');ctx.add_init_script('window.micCalls=0;window.SpeechRecognition=class{constructor(){micCalls++}}')
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL+'#profile');page.wait_for_function('navigator.serviceWorker.controller!==null')
 assert page.locator('#profile-sex,.birth-parts,.birth-help,[data-voice-section=profile-fill]').count()==0
 assert page.locator('#profile-birthDate').get_attribute('type')=='text' and page.locator('.profile-basics input').count()==2
 assert page.evaluate('micCalls')==0
 choices={
 'menstrualStage':['Не указывать','Менструации есть','Менструации ещё не начались','Менструаций сейчас нет','Перименопауза','Менопауза','Послеродовой период'],
 'cyclePattern':['Не указывать','Пока наблюдаю','Обычно регулярный','Нерегулярный','Сейчас неприменимо'],
 'status':['Не беременна','Подготовка к беременности','Беременность','Лактация — грудное вскармливание'],
 'hormones':['Не указывать','Не использую','Используется гормональная терапия'],
 'fertility':['Не указывать','Нет известных трудностей с зачатием','Пытаюсь забеременеть, пока без результата','Бесплодие диагностировано врачом','Прохожу лечение / использую ВРТ']}
 for key,labels in choices.items():assert page.locator('#profile-'+key+' option').all_text_contents()==labels,key
 page.locator('#profile-name').fill('София');fill_birth_date(page,'2000-02-29');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='2000-02-29' and page.evaluate('profileAge()')==26 and page.evaluate('state.profile.sex')=='female'
 for invalid in ['29.02.2001','31.04.2000','03.11.2026']:
  page.locator('#profile-birthDate').fill(invalid);page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='2000-02-29' and page.locator('#profile-error').inner_text()
 fill_birth_date(page,'1996-11-02');page.locator('#profile-form>button').click();expect(page.locator('#profile-birthDate')).to_have_value('02.11.1996');assert page.evaluate('reference("iron").value')==18
 assert page.locator('#profile-age-hint').inner_text()==''
 page.locator('#profile-cyclePattern').select_option('observing');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.health.cyclePattern')=='observing'
 page.locator('#profile-hormones').select_option('therapy');page.locator('#profile-form>button').click();assert page.evaluate('canPredictCycle(state.profile)') is False
 page.locator('#profile-hormones').select_option('none');page.locator('#profile-menstrualStage').select_option('menstruating');page.locator('#profile-form>button').click();assert page.evaluate('canPredictCycle(state.profile)') is True
 page.locator('#profile-name').fill('Черновик');page.locator('.bottom-nav [data-view=profile]').click()
 for section in ['account','settings','subscription','devices']:
  page.locator('[data-menu=profile] [href="#'+section+'"]').click();expect(page.locator('#'+section)).to_be_visible()
 open_about(page);assert page.locator('#profile-name').input_value()=='Черновик'
 for width in [320,375,390,430,844,1280]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  assert page.locator('#profile-birthDate').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
  assert page.locator('#profile-birthDate').bounding_box()['height']>=48
 page.locator('#profile-name').fill('София');page.locator('#profile-form>button').click();ctx.set_offline(True);page.reload();expect(page.locator('#profile-birthDate')).to_have_value('02.11.1996')
 assert page.evaluate('state.profile.birthDate')=='1996-11-02';page.goto(URL+'#goals');expect(page.locator('#profile')).to_be_visible();assert page.evaluate('location.hash')=='#profile'
 assert not errors,errors;ctx.close()
 legacy=b.new_context();legacy.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-20'],sleep:[],meals:[],profile:{name:'Прежний профиль',birthDate:'1996-01-01',age:30,ageUnit:'years',sex:'male',status:'none',health:{menstrualStage:'surgical',hormones:'combined',healthNotes:'Прежние сведения'}}}))")
 page=legacy.new_page();page.goto(URL+'#profile');page.locator('#profile-name').fill('Обновлённое имя');page.locator('#profile-form>button').click()
 assert page.evaluate('state.profile.sex')=='female' and page.evaluate('state.profile.legacySex')=='male'
 assert page.evaluate('state.profile.health.menstrualStage')=='surgical' and page.evaluate('state.profile.health.hormones')=='combined' and page.evaluate('canPredictCycle(state.profile)') is False
 page.locator('#profile-menstrualStage').select_option('menstruating');page.locator('#profile-hormones').select_option('none');page.locator('#profile-form>button').click();assert page.evaluate('canPredictCycle(state.profile)') is True and page.evaluate('state.profile.health.healthNotes')=='Прежние сведения'
 b.close();print('PASS: one dotted DOB field, strict dates/future/leap years, female defaults, exact health lists, prediction guards, legacy choices retained until changed, responsive/offline fields and drafts')
