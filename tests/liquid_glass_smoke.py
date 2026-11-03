"""Compact glass editor, five-slot rail, real horizontal touch and safe upgrades."""
from playwright.sync_api import sync_playwright,expect
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8043/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU')
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL+'#cycle');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 def ids():return page.locator('#day-widgets>.day-widget:not([hidden])').evaluate_all('(es)=>es.map(e=>e.dataset.widgetId)')
 def row(id):return page.locator('#widget-options [data-topic="'+id+'"]')
 assert ids()==['cycle','food','skin','books']
 assert page.locator('.topic-strip>#add-widget').count()==1
 assert page.locator('#add-widget .topic-label').text_content()=='РЕДАКТИРОВАТЬ'
 page.locator('#add-widget').click()
 assert page.locator('#widget-options small,#widget-options .widget-choice-icon').count()==0
 titles=page.locator('.topic-editor-description strong').all_text_contents()
 assert all(t==t.upper() for t in titles) and 'АКТИВНОСТЬ' in titles
 for width in [320,390,768,1280]:
  page.set_viewport_size({'width':width,'height':844})
  for id in ['cycle','food','skin','books','affirmation','activity']:
   item=row(id);assert item.bounding_box()['height']<=66,(width,id)
   title=item.locator('strong').bounding_box();switch=item.locator('[role=switch]').bounding_box()
   assert abs(title['y']+title['height']/2-switch['y']-switch['height']/2)<2,(width,id)
   assert title['x']+title['width']<=switch['x']
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':844})
 row('water').locator('[role=switch]').click();row('affirmation').locator('[role=switch]').click()
 on=row('water').locator('[role=switch]');assert on.get_attribute('aria-checked')=='true'
 assert 'gradient' in on.locator('.switch-track').evaluate('(e)=>getComputedStyle(e).backgroundImage')
 assert 'blur' in on.locator('.switch-track').evaluate('(e)=>getComputedStyle(e).backdropFilter')
 page.locator('#widget-picker [data-close-dialog]').click()
 # Every topic is on the same y coordinate; only the first four slots are visible initially.
 rail=page.locator('#day-widgets');rail.evaluate('(e)=>e.scrollLeft=0')
 ys=page.locator('#day-widgets .day-widget:not([hidden]) .topic-orb').evaluate_all('(es)=>es.map(e=>e.getBoundingClientRect().y)')
 assert max(ys)-min(ys)<1
 assert rail.evaluate('(e)=>e.scrollWidth>e.clientWidth')
 cdp=c.new_cdp_session(page);box=rail.bounding_box();y=box['y']+28;start=box['x']+box['width']*.85;end=box['x']+box['width']*.15
 def touch(kind,x=None):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':[] if x is None else [{'x':x,'y':y}]})
 touch('touchStart',start)
 for i in range(1,9):touch('touchMove',start+(end-start)*i/8);page.wait_for_timeout(22)
 touch('touchEnd');page.wait_for_timeout(350)
 assert rail.evaluate('(e)=>e.scrollLeft')>40
 expect(page.locator('#add-widget')).to_be_in_viewport()
 assert page.locator('#cycle-start-action').evaluate('(e)=>getComputedStyle(e).backgroundImage')!='none'
 assert 'blur' in page.locator('.glass-recommendation-body').evaluate('(e)=>getComputedStyle(e).backdropFilter')
 expected=ids();c.set_offline(True);page.reload();assert ids()==expected
 assert page.evaluate('caches.match(new URL("./liquid-glass.css?v=44",location.href)).then(Boolean)')
 assert not errors,errors;c.close()
 # The previous default updates to four without losing old water/notes; custom layouts stay personal.
 for order,expected in [(['cycle','food','water','skin','activity'],['cycle','food','skin','books']),(['skin','books','water'],['skin','books','water'])]:
  c=b.new_context();c.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:[],sleep:[],meals:[],water:[{id:'kept',date:'2026-11-02',ml:250}],dayMap:{version:2,order:"+str(order).replace("'",'"')+",notes:[{id:'note',topic:'water',date:'2026-11-02',text:'kept'}]}}))")
  page=c.new_page();page.goto(URL);assert ids()==expected
  assert page.evaluate('state.water[0].ml')==250 and page.evaluate('state.dayMap.notes[0].text')=='kept';c.close()
 b.close();print('PASS: four default topics plus fixed Edit, one-row uppercase editor, aligned glass switches, real horizontal touch, rounded translucent controls/recommendations, offline and non-destructive map upgrades')
