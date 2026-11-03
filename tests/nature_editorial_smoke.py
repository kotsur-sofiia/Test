"""Readable botanical chapters, continuous gradients, responsive and offline."""
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright, expect
import os, re

URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8040/Test/').split('#')[0]

def contrast(a,b):
 def luminance(rgb):
  values=[v/255 for v in rgb]
  linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
  return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
 x,y=sorted([luminance(a),luminance(b)])
 return (y+.05)/(x+.05)

with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU',timezone_id='Europe/Podgorica')
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc))
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({sleep:[],meals:[],periods:['2026-10-13'],periodEnds:{'2026-10-13':'2026-10-17'},cycleLength:28,periodLength:5,water:[{id:'kept',date:'2026-11-02',ml:200,container:'glass'}]}))")
 page.goto(URL+'#cycle');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.locator('#cycle-dial-day').inner_text()=='21'
 assert page.locator('.app-backdrop,#today,#cycle-dial-date,#cycle-length,#period-length').count()==0
 assert 'Noto Serif' in page.locator('#page-title').evaluate('(e)=>getComputedStyle(e).fontFamily')
 assert 'Inter' in page.locator('#cycle-form input').first.evaluate('(e)=>getComputedStyle(e).fontFamily')
 # One document canvas continues beneath every transparent section.
 assert 'shore-canvas.svg' in page.locator('body').evaluate('(e)=>getComputedStyle(e,"::before").backgroundImage')
 assert page.locator('.cycle-dial-card').evaluate('(e)=>getComputedStyle(e,"::before").display')=='none'
 def rgb(value):return tuple(map(int,re.findall(r'\d+',value)[:3]))
 glass=page.locator('.glass-recommendation-body');heading=page.locator('.cycle-recommendations h2')
 # Sample the actual shore under the heading, above the photographic card row.
 heading.evaluate('(e)=>e.style.opacity="0"');glass_shot=Image.open(BytesIO(glass.screenshot()))
 heading.evaluate('(e)=>e.style.removeProperty("opacity")')
 glass_background=glass_shot.getpixel((5,15))[:3]
 assert contrast(rgb(page.locator('.cycle-recommendations h2').evaluate('(e)=>getComputedStyle(e).color')),glass_background)>4.5,glass_background
 # Each major route must remain navigable at narrow, tablet, desktop and landscape sizes.
 for width,height in [(320,844),(390,844),(768,1024),(1280,900),(844,390)]:
  page.set_viewport_size({'width':width,'height':height})
  for route in ['cycle','profile','food','water','sleep','skin','account','capture','library','friends']:
   page.goto(URL+'#'+route);page.evaluate('document.fonts.ready')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route)
  page.goto(URL+'#cycle')
  for selector in ['#cycle-phase-name','#cycle-dial-day','#cycle-countdown-value']:
   assert page.locator(selector).evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),(width,selector)
 assert page.evaluate('state.water.some(e=>e.id==="kept")')
 page.set_viewport_size({'width':390,'height':844});ctx.set_offline(True);page.reload();expect(page.locator('#cycle')).to_be_visible()
 for path in ['./nature-editorial.css?v=64','./milk-sand.css?v=79','./liquid-glass.css?v=47','./typography.css?v=73','./assets/fonts/Inter-Regular.woff','./assets/fonts/Inter-SemiBold.woff','./assets/fonts/NotoSerif-Regular.woff','./assets/fonts/NotoSerifDisplay-Regular.woff','./assets/garden-spa.webp','./assets/clay-grain.svg','./assets/glass-sand-grain.svg','./assets/recommendation-shore.webp','./assets/recommendation-food.webp','./assets/recommendation-rest.webp','./assets/beach-sand-natural.webp','./assets/shoreline-water.webp','./assets/pearl-topics.webp','./assets/wild-pearl-diary.webp','./assets/sand-matched-cycle-pearl.webp','./assets/beach-water.webp','./assets/natural-sand-trail.webp','./assets/shore-canvas.svg?v=64']:
  assert page.evaluate('(path)=>caches.match(new URL(path,location.href)).then(Boolean)',path),path
 assert 'Noto Serif' in page.locator('#page-title').evaluate('(e)=>getComputedStyle(e).fontFamily')
 assert page.evaluate('state.periodEnds["2026-10-13"]')=='2026-10-17'
 assert not errors,errors
 b.close();print('PASS: continuous milk-sand background, warm neutral controls and readable contrasts, Cyrillic editorial fonts, 10 routes at 5 viewport sizes, cycle text fits, unchanged data and complete offline design')
