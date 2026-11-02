"""Full-width natural scenes, broad title, no export UI and safe local data."""
from playwright.sync_api import sync_playwright,expect
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8044/Test/').split('#')[0]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU')
 c.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-13'],sleep:[],meals:[],cycleLength:32,periodLength:5,water:[{id:'keep',date:'2026-11-02',ml:250}]}))")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL+'#cycle');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 original=page.evaluate('localStorage.getItem("luna-diary-v1")')
 for width in [320,390,768,1280]:
  page.set_viewport_size({'width':width,'height':900})
  main=page.locator('.layout main');box=main.bounding_box();assert box['x']==0 and abs(box['width']-width)<1
  assert main.evaluate('(e)=>getComputedStyle(e).borderRadius')=='0px'
  assert main.evaluate('(e)=>getComputedStyle(e).boxShadow')=='none'
  glyph=page.locator('#page-title').evaluate('(e)=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().width}')
  assert .88*width<=glyph<=.98*width,(width,glyph)
  assert int(page.locator('#page-title').evaluate('(e)=>getComputedStyle(e).fontWeight'))>=700
  for selector,asset in [('#diary-shell','dew-monstera.webp'),('.cycle-dial-card','sand-waterfall.webp'),('.cycle-recommendations','clay-grain.svg')]:
   item=page.locator(selector);style=item.evaluate('(e)=>{const s=getComputedStyle(e,"::before");return {image:s.backgroundImage,mask:s.maskImage}}')
   assert asset in style['image'] and 'gradient' not in style['image'] and style['mask']=='none',style
   rect=item.bounding_box();assert rect['x']==0 and abs(rect['width']-width)<1,(width,selector,rect)
  end=page.locator('.cycle-recommendations').bounding_box()
  assert abs(end['y']+end['height']-page.evaluate('document.documentElement.scrollHeight-scrollY'))<2
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert page.locator('footer,#export-data,#settings-export').count()==0
 # The glass components keep their own rounded shapes inside unframed scene backgrounds.
 assert float(page.locator('.glass-recommendation-body').evaluate('(e)=>getComputedStyle(e).borderRadius').replace('px',''))>=30
 for route in ['account','settings','library','friends','food','water','profile']:
  page.goto(URL+'#'+route);assert page.get_by_role('button',name='Скачать мои данные',exact=True).count()==0
  assert page.locator('#export-data,#settings-export').count()==0
 assert page.evaluate('localStorage.getItem("luna-diary-v1")')==original
 page.goto(URL+'#settings');page.evaluate('()=>{const e=new Event("beforeinstallprompt",{cancelable:true});e.prompt=async()=>{window.installed=true};window.dispatchEvent(e)}')
 expect(page.locator('#install')).to_be_visible();page.locator('#install').click();assert page.evaluate('installed') is True
 page.goto(URL+'#cycle');c.set_offline(True);page.reload();expect(page.locator('#cycle')).to_be_visible()
 assert page.evaluate('state.water[0].id')=='keep'
 assert page.evaluate('caches.match(new URL("./nature-editorial.css?v=43",location.href)).then(Boolean)')
 assert not errors,errors;b.close();print('PASS: full-width unframed scenes, no background fades, foliage/sand/clay, 92% bold title, removed download UI, retained install and unchanged local/offline records')
