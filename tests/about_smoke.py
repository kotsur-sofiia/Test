from profile_form import fill_birth_date, open_about
"""About-me structure, DOB-derived norms, health context, optional device readings and persistence."""
from playwright.sync_api import sync_playwright, expect
from datetime import datetime,timezone
from pathlib import Path
import os,json
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8015/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,timezone_id='Europe/Podgorica',locale='ru-RU');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('Promise.all([document.fonts.ready,document.fonts.load("italic 400 39px Cormorant Garamond","Обо мне"),document.fonts.load("500 26px Caveat","Немного внимания к себе")])');assert page.evaluate('document.fonts.check("400 16px Nunito","Женское здоровье") && document.fonts.check("italic 400 39px Cormorant Garamond","Обо мне") && document.fonts.check("500 26px Caveat","Немного внимания к себе")')
 assert page.locator('#today').is_visible() and page.locator('#today').inner_text()=='Понедельник, 2 ноября'
 assert page.locator('#profile h1').inner_text()=='Обо мне'
 assert page.locator('.bottom-nav [aria-current="page"]').inner_text()=='Дневник'
 assert not page.locator('#home').is_visible() and not page.locator('#sleep').is_visible()
 assert 'Общие данные' not in page.locator('#profile').inner_text() and 'Дополнительные данные' not in page.locator('#profile').inner_text()
 styles=page.locator('#profile .about-label,#profile .profile-group>legend').evaluate_all('(els)=>els.map(e=>{const s=getComputedStyle(e);return [s.fontFamily,s.fontSize,s.fontWeight].join("|")})')
 assert len(styles)==4 and len(set(styles))==1,styles
 assert 'НАЧНЁМ' not in page.locator('#profile').inner_text() and 'Справочные ориентиры учитывают возраст' not in page.locator('#profile').inner_text()
 assert page.locator('#profile-age').count()==0
 assert page.locator('.profile-basics input:not([type=hidden])').count()==4
 assert page.locator('#profile-form fieldset legend').all_text_contents()==['Женское здоровье','Тело']
 page.locator('#profile-name').fill('София');fill_birth_date(page,'1996-11-02')
 def save():page.locator('#profile-form>button').click()
 save();assert page.evaluate('state.profile.age')==30 and page.evaluate('reference("iron")') is None
 assert page.evaluate('Object.keys(state.profile.body).length')==0
 page.locator('#profile-sex').select_option('female')
 metrics={'height':'165','weight':'60','boneMass':'2.5','fatPercent':'23','visceralFat':'5','muscleMass':'40','waterPercent':'55','basalMetabolism':'1450','bodyAge':'28'}
 for key,val in metrics.items():page.locator('#profile-'+key).fill(val)
 assert page.locator('#profile-bmi').inner_text()=='22'
 page.locator('#profile-menstrualStage').select_option('menstruating');page.locator('#profile-cyclePattern').select_option('regular');page.locator('#profile-cycleLength').fill('29');page.locator('#profile-periodLength').fill('5');page.locator('#profile-fertility').select_option('trying');page.locator('#profile-healthNotes').fill('Личная заметка');save()
 assert page.evaluate('state.cycleLength')==29 and page.evaluate('reference("iron").value')==18
 assert page.evaluate('state.profile.body.muscleMass')==40 and page.evaluate('state.profile.health.fertility')=='trying'
 page.evaluate("state.periods=['2026-10-20'];save()")
 assert page.evaluate('phaseAt(today)') is not None
 page.locator('.bottom-nav [href="#home"]').click();page.locator('[data-menu="diary"] [href="#cycle"]').click()
 page.locator('#period-start').fill('2026-10-20');page.locator('#cycle-length').fill('30');page.locator('#cycle-form button').click()
 open_about(page);assert page.locator('#profile-cycleLength').input_value()=='30' and page.evaluate('state.profile.health.cycleLength')==30
 for key,value in [('cyclePattern','irregular'),('menstrualStage','menopause'),('hormones','combined')]:
  page.locator('#profile-'+key).select_option(value);save();assert page.evaluate('phaseAt(today)') is None
  page.locator('#profile-'+key).select_option({'cyclePattern':'regular','menstrualStage':'menstruating','hormones':'none'}[key]);save()
  assert page.evaluate('state.periods.length')==1
 page.locator('#profile-status').select_option('pregnant');save();assert page.evaluate('reference("iron").value')==27
 page.locator('#profile-breastfeeding').check();save();assert page.evaluate('reference("iron")') is None;assert 'одновременно' in page.locator('#profile-advice').inner_text()
 page.locator('#profile-status').select_option('lactating');save();assert page.evaluate('reference("iron").value')==9
 page.locator('#profile-status').select_option('none');save();assert page.evaluate('reference("iron").value')==18
 # Optional fields can be cleared, and historical diary records remain intact.
 page.locator('#profile-boneMass').fill('');save();assert page.evaluate('Object.hasOwn(state.profile.body,"boneMass")') is False
 page.locator('#profile-muscleMass').fill('90');save();assert 'не может превышать' in page.locator('#profile-error').inner_text();assert page.evaluate('state.profile.body.muscleMass')==40
 page.locator('#profile-muscleMass').fill('40')
 page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("quota")}}');page.locator('#profile-name').fill('Черновик');save()
 assert page.evaluate('state.profile.name')=='София' and page.locator('#profile-name').input_value()=='Черновик'
 page.evaluate('()=>{Storage.prototype.setItem=realSet}');page.locator('#profile-name').fill('София');save()
 for width in [320,375,390,430,844,1280]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  for field in page.locator('#profile-form input,#profile-form select').all():
   if field.is_visible() and field.get_attribute('type')!='checkbox':assert field.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
 page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/about-me-mobile.png')
 page.locator('#profile-body-fields').scroll_into_view_if_needed();page.screenshot(path='/tmp/luna-check/body-mobile.png')
 ctx.set_offline(True);page.reload();page.evaluate('Promise.all([document.fonts.ready,document.fonts.load("italic 400 39px Cormorant Garamond","Обо мне"),document.fonts.load("500 26px Caveat","Немного внимания к себе")])');assert page.evaluate('document.fonts.check("400 16px Nunito","Женское здоровье") && document.fonts.check("italic 400 39px Cormorant Garamond","Обо мне") && document.fonts.check("500 26px Caveat","Немного внимания к себе")');assert page.locator('#profile-birthDate').input_value()=='1996-11-02' and page.locator('#profile-waterPercent').input_value()=='55'
 assert page.locator('#profile-healthNotes').input_value()=='Личная заметка' and page.evaluate('state.periods.length')==1
 with page.expect_download() as d:page.locator('#export-data').click()
 data=json.loads(Path(d.value.path()).read_text());assert data['profile']['body']['basalMetabolism']==1450 and data['profile']['birthDate']=='1996-11-02'
 assert not errors,errors;ctx.close()
 # Migration keeps the prior known age for references, without fabricating a birthday.
 ctx=b.new_context();ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:[],sleep:[],meals:[],profile:{name:'Прежний профиль',age:7,ageUnit:'months',weight:7.5,sex:'female',status:'none'}}))")
 page=ctx.new_page();page.goto(URL);assert page.locator('#profile-birthDate').input_value()=='' and page.locator('#profile-weight').input_value()=='7.5' and page.evaluate('reference("iron")') is None
 fill_birth_date(page,page.evaluate('localDate()'));page.locator('#profile-form>button').click();assert page.evaluate('state.profile.legacyAge.age')==7 and page.evaluate('profileAge()')==0
 b.close();print('PASS: mobile About me/date/sections, DOB age and nutrition, optional body metrics/BMI, health states and cycle suppression, pregnancy/lactation, no inferred fertility, legacy preservation, validation/quota rollback, responsive inputs, offline/export')
