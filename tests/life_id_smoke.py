"""Life ID identity, calendar rotation, legacy diary persistence and devices routing."""
from playwright.sync_api import sync_playwright,expect
from datetime import datetime,timezone
from pathlib import Path
import os
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8020/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,timezone_id='Europe/Podgorica',locale='ru-RU')
 ctx.add_init_script("if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-20'],cycleLength:28,periodLength:5,sleep:[],meals:[{id:'old',date:'2026-11-02',product:'oats',grams:100}],profile:{name:'София',birthDate:'1996-11-02',age:30,ageUnit:'years',sex:'female',status:'none'}}))")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime(2026,11,2,22,58,0,tzinfo=timezone.utc));page.goto(URL+'#home');page.wait_for_function('navigator.serviceWorker.controller!==null');page.evaluate('document.fonts.ready')
 assert page.title()=='Life ID — подари внимание себе' and page.locator('.logo').text_content()=='Life ID'
 manifest=page.evaluate('fetch("./manifest.webmanifest").then(r=>r.json())');assert manifest['name']=='Life ID' and manifest['short_name']=='Life ID' and manifest['id']=='./'
 assert page.locator('#home .eyebrow').text_content()=='Подари внимание себе'
 assert page.locator('#affirmation-date').count()==0 and page.locator('#today').is_visible()
 assert page.locator('#today').inner_text()=='Понедельник, 2 ноября 2026'
 assert 'Твой ритм' not in page.locator('#home').inner_text() and 'Немного внимания' not in page.locator('#home').inner_text()
 first=page.locator('#daily-affirmation').inner_text();assert first and page.locator('#daily-affirmation').get_attribute('data-date')=='2026-11-02'
 # Midnight updates an already open app; no refresh, random reroll or storage writes.
 before=page.evaluate('localStorage.getItem("luna-diary-v1")');page.clock.pause_at(datetime(2026,11,2,22,59,59,tzinfo=timezone.utc));page.clock.run_for(2000)
 second=page.locator('#daily-affirmation').inner_text();assert first!=second and page.locator('#daily-affirmation').get_attribute('data-date')=='2026-11-03'
 assert page.locator('#today').inner_text()=='Вторник, 3 ноября 2026'
 assert before==page.evaluate('localStorage.getItem("luna-diary-v1")')
 page.reload();assert page.locator('#daily-affirmation').inner_text()==second
 # Calendar mapping remains deterministic through DST changes, month/year boundaries and leap day.
 assert page.evaluate('''()=>{const dates=['2026-12-31','2027-01-01','2028-02-28','2028-02-29','2028-03-01','2026-03-28','2026-03-29','2026-03-30'];return dates.every((s,i)=>{const d=new Date(s+'T12:00:00');return LifeAffirmation.forDate(d)===LifeAffirmation.forDate(new Date(s+'T22:00:00'))&&(!i||LifeAffirmation.forDate(d)!==LifeAffirmation.forDate(new Date(dates[i-1]+'T12:00:00')))})}''')
 page.locator('.bottom-nav [data-view="profile"]').click();page.locator('[data-menu="profile"] [href="#devices"]').click();expect(page.locator('#devices')).to_be_visible()
 assert page.locator('.bottom-nav [aria-current="page"]').inner_text()=='Профиль' and 'пока не доступно' in page.locator('#devices').inner_text()
 ctx.set_offline(True);page.reload();expect(page.locator('#devices')).to_be_visible();page.locator('.bottom-nav [data-view="diary"]').click();expect(page.locator('#home')).to_be_visible();assert page.locator('#daily-affirmation').inner_text()==second
 assert page.evaluate('state.meals[0].id')=='old' and page.evaluate('state.profile.name')=='София'
 for width in [320,375,390,430,844,1280]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path='/tmp/luna-check/life-id-home.png')
 page.locator('.bottom-nav [data-view="profile"]').click();page.locator('[data-menu="profile"] [href="#devices"]').click();page.screenshot(path='/tmp/luna-check/life-id-devices.png')
 assert not errors,errors;b.close();print('PASS: Life ID branding/manifest, daily stable affirmation, live local midnight, month/year/leap/DST dates, devices navigation and offline route, unchanged legacy data, responsive typography')
