"""Explicit leaf background, fresh online document, complete offline image and data."""
from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8022/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL+'#home');page.wait_for_function('navigator.serviceWorker.controller!==null')
 image=page.locator('.app-backdrop img');expect(image).to_be_visible();page.wait_for_function('document.querySelector(".app-backdrop img").naturalWidth>0')
 assert 'olive-leaves.webp' in image.get_attribute('src')
 assert page.locator('.app-backdrop').evaluate('(e)=>getComputedStyle(e).position')=='fixed'
 assert page.locator('body').evaluate('(e)=>getComputedStyle(e,"::before").display')=='none'
 page.evaluate("state.water.push({id:'background-test',date:localDate(),ml:200,container:'glass'});save()")
 # Simulate a stale cached HTML shell. Online navigation must still load the actual app.
 page.evaluate('''async()=>{const name=(await caches.keys()).find(k=>k==='luna-diary-v25');const cache=await caches.open(name);await cache.put(new URL('./index.html',location.href),new Response('<h1>Old cached page</h1>',{headers:{'Content-Type':'text/html'}}))}''')
 page.reload();expect(page.locator('.app-backdrop img')).to_be_visible();expect(page.locator('#home')).to_be_visible()
 page.wait_for_function('''async()=>{const r=await caches.match(new URL('./index.html',location.href));return r&&(await r.text()).includes('app-backdrop')}''')
 ctx.set_offline(True);page.reload();expect(page.locator('#home')).to_be_visible();page.wait_for_function('document.querySelector(".app-backdrop img").naturalWidth>0');assert page.evaluate('state.water.some(r=>r.id==="background-test")')
 for width,height in [(320,844),(390,844),(844,390),(1280,1000)]:
  page.set_viewport_size({'width':width,'height':height});box=page.locator('.app-backdrop').bounding_box();assert box['x']==0 and box['y']==0 and box['width']==width and box['height']==height
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':390,'height':844});page.evaluate('document.fonts.ready');page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/olive-background.png')
 assert not errors,errors;b.close();print('PASS: fixed visible leaf image, full viewport phone/landscape/desktop, stale HTML bypassed online, complete background offline, diary data preserved')
