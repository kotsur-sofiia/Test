"""Woman identity, compact daily phrases and responsive navigation."""
from playwright.sync_api import sync_playwright,expect
import os,json
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8024/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL+'#affirmation');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.title()=='Woman — подари внимание себе'
 assert page.locator('.sidebar,.logo').count()==0
 for link in page.locator('#day-widgets .day-widget:not([hidden]) a').all():
  assert link.bounding_box()['width']>=44 and link.bounding_box()['height']>=44
  assert link.locator('.topic-label').evaluate('(e)=>getComputedStyle(e).display')!='none'
 assert page.evaluate('fetch("./manifest.webmanifest").then(r=>r.json()).then(m=>m.name==="Woman"&&m.short_name==="Woman"&&m.id==="./")')
 assert page.locator('[href*=wet-glass]').count()==0
 styles=page.evaluate('''()=>{const header=getComputedStyle(document.querySelector('main>header')),text=getComputedStyle(document.querySelector('#daily-affirmation')),date=getComputedStyle(document.querySelector('#today'));return {headerBg:header.backgroundColor,textShadow:text.textShadow,dateShadow:date.textShadow,color:text.color,dateColor:date.color,drop:getComputedStyle(document.body,'::after').content}}''')
 assert styles['headerBg']=='rgb(53, 67, 41)',styles
 assert styles['textShadow']=='none' and styles['dateShadow']=='none'
 assert styles['drop'] in ['none','normal']
 original=page.locator('#daily-affirmation').inner_text()
 for width in [320,375,390,430,768,1280]:
  page.set_viewport_size({'width':width,'height':900});page.evaluate('document.fonts.ready')
  failures=page.evaluate('''()=>{const e=document.getElementById('daily-affirmation'),bad=[];for(let i=1;i<=31;i++){e.textContent=LifeAffirmation.forDate(new Date(2026,0,i,12));const h=parseFloat(getComputedStyle(e).lineHeight);if(e.getBoundingClientRect().height>h*2+2||e.scrollWidth>e.clientWidth+1)bad.push(e.textContent)}return bad}''')
  assert not failures,(width,failures)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  assert page.evaluate('getComputedStyle(document.body,"::after").display==="none"')
 page.locator('#daily-affirmation').evaluate('(e,t)=>e.textContent=t',original)
 page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/woman-mobile.png')
 page.locator('.bottom-nav [data-view="profile"]').click();expect(page.locator('#account')).to_be_visible();assert page.locator('[data-menu="profile"] a span:not(.menu-icon)').all_text_contents()==['Аккаунт','Настройки','Подписка','Подключённые девайсы']
 ctx.set_offline(True);page.reload();assert page.evaluate('caches.match(new URL("./assets/dew-monstera.webp",location.href)).then(Boolean)');expect(page.locator('#account')).to_be_visible();page.locator('.bottom-nav [data-view="diary"]').click();expect(page.locator('#diary-shell')).to_be_visible();assert page.title().startswith('Woman')
 assert not errors,errors;b.close();print('PASS: Woman identity, original PWA id, no droplets, no sidebar, botanical editorial surfaces and leaf-green controls without glow, all 31 affirmations fit within two lines at 320–1280 px, offline/profile navigation')
