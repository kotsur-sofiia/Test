"""One document beach canvas, stable ground on scroll, long pages and offline data."""
from playwright.sync_api import sync_playwright,expect
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageChops,ImageStat
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8022/Test/')
def same_ground(before,after):
 # Allow subpixel antialiasing differences when Chromium repaints a taller SVG.
 diff=ImageChops.difference(Image.open(BytesIO(before)),Image.open(BytesIO(after)))
 return max(ImageStat.Stat(diff).mean)<.3 and max(high for low,high in diff.getextrema())<24
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL+'#home');page.wait_for_function('navigator.serviceWorker.controller!==null')
 assert page.locator('.app-backdrop,#today').count()==0
 assert 'shore-canvas.svg' in page.locator('body').evaluate('(e)=>getComputedStyle(e,"::before").backgroundImage')
 assert page.locator('body').evaluate('(e)=>getComputedStyle(e,"::before").display')=='block'
 page.evaluate("state.water.push({id:'background-test',date:localDate(),ml:200,container:'glass'});save()")
 # Simulate a stale cached HTML shell. Online navigation must still load the actual app.
 page.evaluate('''async()=>{const name=(await caches.keys()).find(k=>k==='luna-diary-v71');const cache=await caches.open(name);await cache.put(new URL('./index.html',location.href),new Response('<h1>Old cached page</h1>',{headers:{'Content-Type':'text/html'}}))}''')
 page.reload();assert page.locator('.app-backdrop').count()==0;expect(page.locator('#diary-shell')).to_be_visible()
 page.wait_for_function('''async()=>{const r=await caches.match(new URL('./index.html',location.href));return r&&(await r.text()).includes('page-title')}''')
 ctx.set_offline(True);page.reload();expect(page.locator('#diary-shell')).to_be_visible();assert page.evaluate('state.water.some(r=>r.id==="background-test")')
 for width,height in [(320,844),(390,844),(844,390),(1280,1000)]:
  page.set_viewport_size({'width':width,'height':height});assert page.locator('.app-backdrop').count()==0
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':390,'height':844});page.evaluate('document.fonts.ready');page.evaluate('scrollTo({top:0,behavior:"instant"})')
 # Growing a section must not rescale the sea, sand or decorations already visible.
 page.evaluate('''()=>new Promise(resolve=>{const image=new Image();image.onload=resolve;image.src='./assets/shore-canvas.svg?v=64'})''')
 before=page.screenshot(animations='disabled')
 page.evaluate('''()=>{const extra=document.createElement('div');extra.id='long-page-check';extra.style.height='6000px';document.body.append(extra)}''')
 assert same_ground(before,page.screenshot(animations='disabled')),'beach rescaled when the document became longer'
 page.locator('#long-page-check').evaluate('(e)=>e.remove()')
 # The same patch of sand must stay beneath the dial after real page scrolling.
 dial=page.locator('#cycle-dial');before=dial.screenshot()
 page.evaluate('scrollTo({top:128,behavior:"instant"})')
 assert page.evaluate('scrollY')==128
 assert same_ground(before,dial.screenshot()),'dial slipped across its background on scroll'
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/olive-background.png')
 assert not errors,errors;b.close();print('PASS: one document beach canvas, stable dial ground on scroll, no rescale with 6000px added content, phone/landscape/desktop, stale HTML bypassed online, offline assets and diary data preserved')
