"""Manual/dropdown DOB, real date validation, profile menus, disabled profile dictation."""
from playwright.sync_api import sync_playwright, expect
from profile_form import fill_birth_date, open_about
from datetime import datetime,timezone
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8016/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,locale='ru-RU',timezone_id='Europe/Podgorica');ctx.add_init_script('window.micCalls=0;window.SpeechRecognition=class{constructor(){micCalls++}}')
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null')
 assert page.locator('#profile [type=date]').count()==0 and page.locator('[data-voice-section="profile-fill"]').count()==0
 assert page.locator('#profile .voice-start').count()==0 and page.evaluate('micCalls')==0
 menu=page.locator('[data-menu="profile"]');assert menu.locator('a span:not(.menu-icon)').all_text_contents()==['Аккаунт','Настройки','Подписка']
 page.locator('#profile-name').fill('София');fill_birth_date(page,'2000-02-29');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='2000-02-29' and page.evaluate('profileAge()')==26
 # Lists adapt to leap years and month length; changing a year does not silently fix a typed day.
 page.locator('#profile-pickYear').select_option('2001');assert page.locator('#profile-pickDay option[value="29"]').count()==0
 assert page.locator('#profile-birthDay').input_value()=='29';page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='2000-02-29'
 assert 'Проверь' in page.locator('#profile-age-hint').inner_text()
 page.locator('#profile-pickDay').select_option('28');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='2001-02-28'
 page.locator('#profile-pickYear').select_option('1996');page.locator('#profile-pickMonth').select_option('11');page.locator('#profile-pickDay').select_option('2');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='1996-11-02'
 fill_birth_date(page,'2026-11-03');page.locator('#profile-form>button').click();assert page.evaluate('state.profile.birthDate')=='1996-11-02'
 fill_birth_date(page,'1996-11-02');page.locator('#profile-name').fill('Черновик')
 page.locator('.bottom-nav [data-view="profile"]').click()
 for section in ['account','settings','subscription']:
  menu.locator(f'[href="#{section}"]').click();expect(page.locator('#'+section)).to_be_visible();assert page.locator('.bottom-nav [aria-current="page"]').inner_text()=='Профиль'
  assert menu.locator('[aria-current="page"]').get_attribute('href')=='#'+section
 open_about(page);assert page.locator('#profile-name').input_value()=='Черновик'
 # All profile items fit on small phones, inputs remain readable and picker controls tappable.
 for width in [320,375,390,430,844,1280]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  if width<500:
   for link in page.locator('[data-menu="diary"] [href="#profile"]').all():
    box=link.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width
   for part in ['Day','Month','Year']:
    assert page.locator('#profile-pick'+part).bounding_box()['width']>=44
    assert page.locator('#profile-birth'+part).evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
 page.set_viewport_size({'width':390,'height':844});page.locator('#profile-name').fill('София');page.locator('#profile-form>button').click();page.evaluate('document.activeElement.blur();scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/profile-birth-parts.png')
 ctx.set_offline(True);page.reload();assert page.locator('#profile-birthDay').input_value()=='02' and page.locator('#profile-birthMonth').input_value()=='11' and page.locator('#profile-birthYear').input_value()=='1996'
 page.locator('.bottom-nav [data-view="profile"]').click();expect(page.locator('#account')).to_be_visible();page.reload();expect(page.locator('#account')).to_be_visible()
 page.goto(URL+'#goals');expect(page.locator('#profile')).to_be_visible();assert page.evaluate('location.hash')=='#profile'
 assert not errors,errors;b.close();print('PASS: manual/dropdown date parts, leap-year/day lists, invalid/future dates, saved DOB hydration, three profile submenus and About me in Diary, drafts, phone controls, offline/direct/legacy routes, no profile microphone')
