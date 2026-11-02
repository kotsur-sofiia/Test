from profile_form import fill_birth_date, open_about
"""Bottom navigation, contextual profile menu and preservation of existing diary state."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8012/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1280,'height':1000})
 ctx.add_init_script("""window.__speech=[];window.SpeechRecognition=class{constructor(){__speech.push(this)}start(){queueMicrotask(()=>this.onstart?.())}stop(){}abort(){this.aborted=true}}""")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL.split('#')[0]+'#profile');page.wait_for_function('navigator.serviceWorker.controller!==null')
 bottom=page.get_by_role('navigation',name='Основная навигация',exact=True)
 assert bottom.evaluate('(e)=>getComputedStyle(e).position')=='fixed'
 assert page.locator('body').evaluate('(e)=>getComputedStyle(e).fontFamily').startswith('Nunito')
 assert bottom.get_by_role('link').all_text_contents()==['Профиль','Дневник','Голосовая запись','Библиотека','Друзья']
 assert page.locator('#profile').is_visible() and not page.locator('#sleep').is_visible()
 assert page.locator('[data-menu="profile"] a').all_text_contents()==['◉Аккаунт','⚙Настройки','◇Подписка','⌁Подключённые девайсы']
 page.locator('#profile-name').fill('Несохранённое имя');assert bottom.locator('[aria-current="page"]').inner_text()=='Дневник';bottom.get_by_role('link',name='Профиль',exact=True).click();expect(page.locator('#account')).to_be_visible()
 page.locator('[data-menu="profile"] a[href="#settings"]').click();expect(page.locator('#settings')).to_be_visible() and not page.locator('#profile').is_visible()
 assert bottom.locator('[aria-current="page"]').inner_text()=='Профиль'
 with page.expect_download() as d:page.locator('#settings-export').click()
 data=json.loads(Path(d.value.path()).read_text());assert 'meals' in data and 'sleep' in data
 page.locator('[data-menu="profile"] a[href="#account"]').click();expect(page.locator('#account')).to_be_visible();page.locator('[data-menu="profile"] a[href="#subscription"]').click();expect(page.locator('#subscription')).to_be_visible()
 open_about(page);assert page.locator('#profile-name').input_value()=='Несохранённое имя'
 # Save a profile and use a diary, then verify tab transitions retain both data and drafts.
 fill_birth_date(page,'1991-01-01');page.locator('#profile-sex').select_option('female');page.locator('#profile-weight').fill('60');page.locator('#profile-form button').click()
 bottom.get_by_role('link',name='Дневник',exact=True).click();expect(page.locator('#diary-shell')).to_be_visible() and not page.locator('#sleep').is_visible() and not page.locator('#profile').is_visible()
 assert page.locator('#diary-shell').is_visible() and not page.locator('[data-menu="profile"]').is_visible()
 page.evaluate('location.hash="food"');page.wait_for_function('document.querySelector("#food").hidden===false');page.locator('#food-product').select_option('oats');page.locator('#food-form button').click();assert page.locator('#food-calories').inner_text()=='379 ккал'
 page.evaluate('location.hash="sleep"');page.wait_for_function('document.querySelector("#sleep").hidden===false');voice=page.locator('[data-voice-section="sleep"]');voice.evaluate('(e)=>e.open=true');voice.locator('.voice-editor').fill('Черновик дневника сна')
 voice.locator('.voice-start').click();assert page.evaluate('__speech.at(-1).aborted') is None
 bottom.get_by_role('link',name='Библиотека',exact=True).click();expect(page.locator('#library')).to_be_visible() and not page.locator('#sleep').is_visible()
 assert page.evaluate('__speech.at(-1).aborted') is True
 bottom.get_by_role('link',name='Друзья',exact=True).click();expect(page.locator('#friends')).to_be_visible() and not page.locator('#library').is_visible()
 bottom.get_by_role('link',name='Дневник',exact=True).click();page.evaluate('location.hash="sleep"');page.wait_for_function('document.querySelector("#sleep").hidden===false');assert voice.locator('.voice-editor').input_value()=='Черновик дневника сна'
 assert page.locator('#food-calories').inner_text()=='379 ккал'
 open_about(page);assert page.locator('#profile-name').input_value()=='Несохранённое имя'
 # Clinical visibility survives routing: a male or lactating profile must not reveal cycle predictions.
 page.locator('#profile-sex').select_option('male');page.locator('#profile-form button').click();bottom.get_by_role('link',name='Дневник',exact=True).click()
 assert not page.locator('#cycle').is_visible() and not page.locator('[data-menu="diary"] a[href="#cycle"]').is_visible()
 page.evaluate('location.hash="sleep"');page.wait_for_function('document.querySelector("#sleep").hidden===false');expect(page.locator('#sleep')).to_be_visible()
 page.evaluate('location.hash="cycle"');page.wait_for_function('location.hash==="#cycle"')
 assert not page.locator('#cycle').is_visible()
 # Browser history and direct routes select the appropriate main area and contextual menu.
 bottom.get_by_role('link',name='Друзья',exact=True).click();bottom.get_by_role('link',name='Библиотека',exact=True).click()
 page.go_back();expect(page.locator('#friends')).to_be_visible()
 page.goto(URL.split('#')[0]+'#settings');expect(page.locator('#settings')).to_be_visible() and bottom.locator('[aria-current="page"]').inner_text()=='Профиль'
 ctx.set_offline(True);page.reload();expect(page.locator('#settings')).to_be_visible() and page.evaluate('navigator.onLine') is False
 bottom.get_by_role('link',name='Дневник',exact=True).click();assert page.locator('#food-calories').inner_text()=='379 ккал'
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  box=bottom.bounding_box();assert box and box['x']>=0 and box['x']+box['width']<=width+1
  for link in bottom.locator('a').all():assert link.is_visible()
  # Scroll to the end: fixed navigation must leave the last text above it.
  page.evaluate('window.scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})')
  nav_top=bottom.bounding_box()['y'];notice=page.locator('footer button:not([hidden])').last.bounding_box();assert notice['y']+notice['height']<=nav_top+1,(width,notice,nav_top)
 assert not errors,errors
 b.close();print('PASS: five main tabs, profile submenu, export settings, unsaved drafts and diary persistence, microphone cancellation, cycle restrictions, history/direct/offline routes, responsive safe bottom area')
