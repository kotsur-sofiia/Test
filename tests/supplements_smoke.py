"""Nutrient and supplement regressions with a real local browser and no external API."""
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime,timedelta
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8003/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=b.new_context(viewport={'width':1280,'height':950},timezone_id='Europe/Podgorica')
 ctx.add_init_script("""if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-10'],cycleLength:28,periodLength:5,sleep:[],meals:[],products:[],water:[{id:'old-water',date:'2026-10-01',ml:250,container:'glass'}]}));""")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 keys=page.evaluate('nutrients.map(n=>n[0])')
 assert len(keys)==33 and len(set(keys))==33
 expected={'fiber','d','iodine','iron','a','calcium','b1','e','b2','b3','b5','b6','folate','b12','k','magnesium','phosphorus','potassium','zinc','copper','manganese','selenium','choline','omega3','omega6','c','sodium','sulfur','chloride','fluoride','molybdenum','chromium','cobalt'}
 assert set(keys)==expected
 groups=page.evaluate('nutrientGroups')
 grouped=[key for group in groups for key in group['keys']]
 assert len(grouped)==len(set(grouped))==33 and set(grouped)==expected
 assert page.locator('#nutrients details').count()==6
 assert page.locator('#product-micros fieldset').count()==6
 assert page.locator('#supplement-nutrient optgroup').count()==6
 assert page.locator('#nutrients [data-group="trace-minerals"] [data-nutrient="fluoride"]').count()==1
 assert page.locator('#nutrients [data-group="macro-minerals"] [data-nutrient="phosphorus"]').count()==1
 for key in ['sulfur','cobalt']:
  assert '%' not in page.locator(f'#nutrients [data-nutrient="{key}"]').inner_text()
 # Collapsing one group must survive logging an entry, without hiding unrelated groups.
 page.locator('#nutrients [data-group="macro-minerals"] summary').click()

 assert page.locator('#product-micros input').count()==33
 assert page.evaluate('state.water[0].ml')==250
 assert page.evaluate('state.periods[0]')=='2026-10-10'
 def row(key):return page.locator(f'#nutrients [data-nutrient="{key}"]')
 def add(key,dose,unit,name='Моя добавка'):
  page.locator('#supplement-name').fill(name);page.locator('#supplement-nutrient').select_option(key);page.locator('#supplement-unit').select_option(unit);page.locator('#supplement-dose').fill(str(dose));page.locator('#supplement-form button').click()
 add('c',.1,'g','Витамин C')
 assert '100 / 75 мг · 133%' in row('c').inner_text()
 assert not page.locator('#nutrients [data-group="macro-minerals"]').evaluate('(e)=>e.open')
 page.locator('#nutrients [data-group="macro-minerals"] summary').click()
 add('d',600,'iu','Витамин D3')
 assert '15 / 15 мкг · 100%' in row('d').inner_text()
 add('iron',1000,'mcg','Железо')
 assert '1 / 18 мг · 6%' in row('iron').inner_text()
 add('omega3',1000,'mg','Омега-3')
 assert '1 г' in row('omega3').inner_text() and '%' not in row('omega3').inner_text()
 assert row('omega3').get_by_role('meter').count()==0
 add('a',500,'iu','Витамин A')
 assert 'без пересчёта: 1' in row('a').inner_text()
 assert '500 МЕ' in page.locator('#supplement-history').inner_text()
 add('folate',400,'folic-mcg','Фолиевая кислота')
 add('folate',200,'dfe','Фолат DFE')
 assert '200 / 400 мкг DFE · 50% + ?' in row('folate').inner_text()
 assert page.evaluate('state.supplements.length')==7
 add('c',0,'mg')
 assert page.evaluate('state.supplements.length')==7
 print('PASS: 33 unique nutrients, additive migration, g/mg/mcg conversions, D in IU, unsupported forms excluded, percentages above 100 and omega no target')
 # Custom product with a known micronutrient, optional extended data, and food/supplement split.
 for key,val in [('name','Тестовый продукт'),('kcal','50'),('protein','2'),('fat','1'),('carbs','5')]:page.locator('#product-'+key).fill(val)
 page.locator('#product-form details').evaluate('(e)=>e.open=true')
 page.locator('#product-c').fill('25');page.locator('#product-fiber').fill('3');page.locator('#product-d').fill('2')
 page.locator('#product-save').click();page.locator('#food-grams').fill('200');page.locator('#food-form button').click()
 assert '150 / 75 мг · 200%' in row('c').inner_text()
 assert 'Еда: 50 мг · БАДы: 100 мг' in row('c').inner_text()
 assert '6 / 25 г · 24%' in row('fiber').inner_text()
 assert '19 / 15 мкг · 127%' in row('d').inner_text()
 assert 'Нет данных' in row('k').inner_text()
 # Known supplement must remain visible when all food data for this nutrient are unknown.
 add('selenium',55,'mcg','Селен')
 assert '55 / 55 мкг · 100% + ?' in row('selenium').inner_text()
 today=page.evaluate('today');yesterday=(datetime.strptime(today,'%Y-%m-%d')-timedelta(days=1)).strftime('%Y-%m-%d')
 page.locator('#food-date').fill(yesterday);page.locator('#food-date').dispatch_event('change')
 assert page.locator('#supplement-history .record').count()==0
 add('c',75,'mg','Вчерашний C')
 assert '75 / 75 мг · 100%' in row('c').inner_text()
 page.locator('#food-date').fill(today);page.locator('#food-date').dispatch_event('change')
 assert page.locator('#supplement-history .record').count()==8
 assert '150 / 75 мг · 200%' in row('c').inner_text()
 with page.expect_download() as download:page.locator('#export-data').click()
 data=json.loads(Path(download.value.path()).read_text());assert len(data['supplements'])==9
 ctx.set_offline(True);page.reload()
 assert page.locator('#connection').inner_text()=='Без интернета'
 assert '150 / 75 мг · 200%' in row('c').inner_text()
 first=page.locator('#supplement-history .record').first;first.locator('button').click()
 assert '50 / 75 мг · 67%' in row('c').inner_text()
 page.reload();assert '50 / 75 мг · 67%' in row('c').inner_text()
 print('PASS: custom nutrient inputs, food + supplement sums and source split, incomplete food data, date isolation, JSON export, offline persistence and deletion')
 assert page.evaluate("fromOFF({code:'x',nutriments:{'vitamin-d_100g':.000015,'iodine_100g':.00015,'copper_100g':.0009,'omega-3-fat_100g':1.5,'fiber_100g':3}}).d")==15
 assert abs(page.evaluate("fromOFF({code:'x',nutriments:{'iodine_100g':.00015}}).iodine")-150)<1e-8
 assert page.evaluate("fromOFF({code:'x',nutriments:{'vitamin-a_100g':.0007}}).a") is None
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 page.locator('#supplements').screenshot(path='/tmp/luna-check/supplements.png')
 assert not errors,errors
 print('PASS: catalog unit conversions, unknown RAE handling, responsive layout, no browser errors')
 b.close()
