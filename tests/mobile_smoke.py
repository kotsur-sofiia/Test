from profile_form import fill_birth_date, open_about
"""Phone navigation, touch forms, rotation, data retention and offline styles."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from datetime import datetime, timedelta
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8013/Test/')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 ctx.add_init_script("window.SpeechRecognition=class{start(){this.onstart?.()}abort(){window.micAborted=true}stop(){}}")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL)
 page.wait_for_function('navigator.serviceWorker.controller!==null')
 nav=page.locator('.bottom-nav')
 def diary(section):
  page.locator(f'[data-menu="diary"] a[href="#{section}"]').click()
  expect(page.locator('#'+section)).to_be_visible()
  for other in ['home','cycle','sleep','food']:
   if other!=section:assert not page.locator('#'+other).is_visible(),other
 def layout():
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert nav.evaluate('(e)=>getComputedStyle(e).position')=='fixed'
  for link in nav.locator('a').all():
   box=link.bounding_box();assert box['height']>=44 and box['width']>=44
  for field in page.locator('input:not([type=checkbox]),select,textarea').all():
   if field.is_visible():assert field.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
 for width in [320,375,390,430]:
  page.set_viewport_size({'width':width,'height':844});layout()
  assert page.locator('#profile-birthDay').bounding_box()['y']>page.locator('#profile-name').bounding_box()['y']
 page.set_viewport_size({'width':390,'height':844})
 page.locator('#profile-name').fill('София');page.locator('#profile-sex').select_option('female')
 fill_birth_date(page,'1996-01-01');page.locator('#profile-weight').fill('60');page.locator('#profile-form button').click()
 nav.locator('[href="#home"]').click();expect(page.locator('#home')).to_be_visible();assert not page.locator('#food').is_visible()
 diary('sleep');page.locator('#sleep-start').fill((datetime.now()-timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M'))
 page.locator('#sleep-end').fill(datetime.now().strftime('%Y-%m-%dT%H:%M'));page.locator('#sleep-form button').click()
 assert page.locator('#sleep-average').inner_text()=='8 ч 0 мин'
 voice=page.locator('[data-voice-section="sleep"]');voice.evaluate('(e)=>e.open=true');voice.locator('.voice-editor').fill('Телефонный черновик');voice.locator('.voice-start').click()
 diary('food');assert page.evaluate('window.micAborted') is True
 page.locator('#food-product').select_option('oats');page.locator('#food-grams').fill('100');page.locator('#food-form button').click()
 assert page.locator('#food-calories').inner_text()=='379 ккал'
 groups=page.locator('#nutrients details');assert groups.count()>0
 assert not groups.evaluate_all('(els)=>els.some(e=>e.open)')
 groups.first.locator('summary').click();assert groups.first.evaluate('(e)=>e.open')
 assert page.locator('#nutrients').evaluate('(e)=>getComputedStyle(e).maxHeight')=='none'
 page.locator('#water-volume').fill('300');page.locator('#water-form button').click();assert page.locator('#water-total').inner_text()=='300 мл'
 page.locator('#food-grams').fill('175')
 for width in [320,375,390,430]:
  page.set_viewport_size({'width':width,'height':844});layout()
  page.screenshot(path=f'/tmp/luna-check/mobile-food-{width}.png')
 diary('cycle');layout();assert page.locator('.day').first.bounding_box()['height']>=44
 diary('sleep');assert voice.locator('.voice-editor').input_value()=='Телефонный черновик'
 diary('food');assert page.locator('#food-grams').input_value()=='175'
 # Touch landscape remains a single-screen diary; desktop expands without losing inputs.
 page.set_viewport_size({'width':844,'height':390});layout();assert not page.locator('#sleep').is_visible()
 page.set_viewport_size({'width':1280,'height':1000});expect(page.locator('#sleep')).to_be_visible()
 assert page.locator('#food-grams').input_value()=='175'
 page.set_viewport_size({'width':390,'height':844});expect(page.locator('#sleep')).not_to_be_visible()
 page.evaluate('scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})')
 privacy=page.locator('.privacy-details>summary').bounding_box();assert privacy['y']+privacy['height']<=nav.bounding_box()['y']
 ctx.set_offline(True);page.reload();expect(page.locator('#food')).to_be_visible();layout()
 assert page.locator('#food-calories').inner_text()=='379 ккал' and page.locator('#water-total').inner_text()=='300 мл'
 open_about(page);assert page.locator('#profile-name').input_value()=='София'
 assert not errors,errors
 browser.close()
 print('PASS: phone widths 320/375/390/430, touch landscape, large controls, single-section diary, saved sleep/food/water, drafts, microphone cancellation, desktop resize, offline mobile styles')
