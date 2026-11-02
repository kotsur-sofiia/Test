"""Real Chromium touch input: long press, scroll, auto-scroll, keyboard and rollback."""
from playwright.sync_api import sync_playwright,expect
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8038/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU')
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:[],sleep:[],meals:[],dayMap:{version:2,topicRailVersion:1,order:['cycle','food','water','skin','activity']}}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready');page.locator('#add-widget').click()
 assert page.locator('#add-widget .topic-label').text_content()=='РЕДАКТИРОВАТЬ'
 assert page.locator('#widget-options [data-action=up],#widget-options [data-action=down]').count()==0
 def row(id):return page.locator('#widget-options [data-topic="'+id+'"]')
 toggle=row('skin').locator('[data-action=toggle]');assert toggle.get_attribute('aria-checked')=='true'
 assert toggle.locator('.switch-track').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(109, 134, 83)'
 assert '24' in toggle.locator('.switch-knob').evaluate('(e)=>getComputedStyle(e).transform')
 toggle.click();toggle=row('skin').locator('[data-action=toggle]');assert toggle.get_attribute('aria-checked')=='false' and toggle.locator('.switch-track').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(213, 214, 201)';toggle.click()
 page.evaluate('()=>{window.writes=0;window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(...args){if(args[0]==="luna-diary-v1")writes++;return realSet.apply(this,args)}}')
 page.locator('#widget-picker').evaluate('(e)=>e.scrollTop=0')
 cdp=ctx.new_cdp_session(page)
 def touch(type,x=None,y=None):cdp.send('Input.dispatchTouchEvent',{'type':type,'touchPoints':[] if x is None else [{'x':x,'y':y}]})
 source=row('food').bounding_box();target=row('water').bounding_box();x=source['x']+100;y=source['y']+35
 before=page.evaluate('JSON.stringify(state.dayMap)');touch('touchStart',x,y);page.wait_for_timeout(470);assert page.locator('.topic-drag-ghost').count()==1
 for i in range(1,7):touch('touchMove',x,y+(target['y']+target['height']*.75-y)*i/6);page.wait_for_timeout(25)
 assert page.evaluate('JSON.stringify(state.dayMap)')==before and page.evaluate('writes')==0
 touch('touchEnd');page.wait_for_timeout(80);assert page.evaluate('state.dayMap.order')==['cycle','water','food','activity','skin'] and page.evaluate('writes')==1
 assert page.locator('.topic-drag-ghost').count()==0
 # Movement before the hold threshold must scroll, without changing the order.
 page.locator('#widget-picker').evaluate('(e)=>e.scrollTop=0');source=row('food').bounding_box();before=page.evaluate('JSON.stringify(state.dayMap.order)');count=page.evaluate('writes');touch('touchStart',x,source['y']+35);touch('touchMove',x,source['y']-50);touch('touchEnd');page.wait_for_timeout(100)
 assert page.evaluate('JSON.stringify(state.dayMap.order)')==before and page.evaluate('writes')==count and page.locator('.topic-drag-ghost').count()==0
 # The keyboard can grab, preview, cancel or drop, without visible arrow controls.
 grip=row('water').locator('[data-action=reorder]');grip.focus();grip.press('Space');grip.press('ArrowDown');assert page.evaluate('JSON.stringify(state.dayMap.order)')==before;grip.press('Escape');assert page.evaluate('writes')==count
 grip.focus();grip.press('Space');grip.press('ArrowDown');grip.press('Enter');assert page.evaluate('state.dayMap.order[1]')=='food'
 # A failed drop restores the stored order.
 before=page.evaluate('JSON.stringify(state.dayMap.order)');page.evaluate('()=>{Storage.prototype.setItem=function(){throw Error("full")}}');grip=row('food').locator('[data-action=reorder]');grip.focus();grip.press('Space');grip.press('ArrowDown');grip.press('Enter');assert page.evaluate('JSON.stringify(state.dayMap.order)')==before
 assert 'Не удалось' in page.locator('#widget-picker-status').inner_text();page.evaluate('()=>{Storage.prototype.setItem=realSet}')
 # Auto-scroll keeps all enabled rows reachable while a finger is held near the edge.
 for id in ['books','meditation','drawing','sleep','affirmation']:
  row(id).locator('[data-action=toggle]').click()
 page.locator('#widget-picker').evaluate('(e)=>e.scrollTop=0');source=row('cycle').bounding_box();x=source['x']+100;y=source['y']+35;touch('touchStart',x,y);page.wait_for_timeout(450)
 for i in range(1,9):touch('touchMove',x,y+(825-y)*i/8);page.wait_for_timeout(25)
 page.wait_for_timeout(750);assert page.locator('#widget-picker').evaluate('(e)=>e.scrollTop')>100
 touch('touchEnd');page.wait_for_timeout(80);assert page.evaluate('state.dayMap.order.indexOf("cycle")')>1
 assert page.locator('.topic-drag-ghost').count()==0
 expected=page.evaluate('JSON.stringify(state.dayMap.order)');page.locator('#widget-picker [data-close-dialog]').click();page.reload();assert page.evaluate('JSON.stringify(state.dayMap.order)')==expected
 assert not errors,errors;b.close();print('PASS: green/gray thumb switches, real touch long-press, no save during preview, one save on drop, normal scrolling, keyboard cancel/drop, rollback, auto-scroll and persisted order')
