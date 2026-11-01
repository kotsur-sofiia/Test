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
 assert len(keys)==50 and len(set(keys))==50
 expected={'fiber','d','iodine','iron','a','calcium','b1','e','b2','b3','b5','b6','folate','b12','k','magnesium','phosphorus','potassium','zinc','copper','manganese','selenium','choline','omega3','omega6','c','sodium','sulfur','chloride','fluoride','molybdenum','chromium','cobalt','unsaturated','ala','epa','dha','inositol','biotin','betaCarotene','carnitine','sugars','addedSugars','starch','polyols','saturated','monounsaturated','polyunsaturated','trans','cholesterol'}
 assert set(keys)==expected
 groups=page.evaluate('nutrientGroups')
 grouped=[key for group in groups for key in group['keys']]
 assert len(grouped)==len(set(grouped))==50 and set(grouped)==expected
 assert page.locator('#nutrients details').count()==5
 assert page.locator('#product-micros fieldset').count()==5
 assert page.locator('#supplement-nutrient optgroup').count()==5
 assert page.locator('#nutrients [data-group="minerals"] [data-nutrient="fluoride"]').count()==1
 assert page.locator('#nutrients [data-group="minerals"] [data-nutrient="phosphorus"]').count()==1
 for key in ['sulfur','cobalt']:
  assert '%' not in page.locator(f'#nutrients [data-nutrient="{key}"]').inner_text()
 # Collapsing one group must survive logging an entry, without hiding unrelated groups.
 page.locator('#nutrients [data-group="minerals"] summary').click()

 assert page.locator('#product-micros input').count()==50
 assert page.evaluate('state.water[0].ml')==250
 assert page.evaluate('state.periods[0]')=='2026-10-10'
 def row(key):return page.locator(f'#nutrients [data-nutrient="{key}"]')
 def add(key,dose,unit,name='Моя добавка'):
  page.locator('#supplement-name').fill(name);page.locator('#supplement-nutrient').select_option(key);page.locator('#supplement-unit').select_option(unit);page.locator('#supplement-dose').fill(str(dose));page.locator('#supplement-form button').click()
 add('c',.1,'g','Витамин C')
 assert '100 / 75 мг · 133%' in row('c').inner_text()
 assert not page.locator('#nutrients [data-group="minerals"]').evaluate('(e)=>e.open')
 page.locator('#nutrients [data-group="minerals"] summary').click()
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
 print('PASS: 50 unique nutrients, additive migration, g/mg/mcg conversions, D in IU, unsupported forms excluded, percentages above 100 and omega no target')
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
 # Omega-3 totals and constituent acids are independent; never add EPA/DHA again to total.
 add('omega3',1000,'mg','Омега-3, общая масса')
 add('epa',180,'mg','ЭПК в том же комплексе')
 add('dha',120,'mg','ДГК в том же комплексе')
 add('ala',500,'mg','АЛК')
 add('unsaturated',3,'g','Ненасыщенные жиры')
 assert '2 г' in row('omega3').inner_text()
 assert '180 мг' in row('epa').inner_text()
 assert '120 мг' in row('dha').inner_text()
 assert '0,5 / 1.1 г · 45%' in row('ala').inner_text()
 assert '3 г' in row('unsaturated').inner_text()
 assert row('epa').get_by_role('meter').count()==0 and row('dha').get_by_role('meter').count()==0
 off=page.evaluate("fromOFF({code:'test',nutriments:{'monounsaturated-fat_100g':4,'polyunsaturated-fat_100g':2,'eicosapentaenoic-acid_100g':.18,'docosahexaenoic-acid_100g':.12,'alpha-linolenic-acid_100g':.5}})")
 assert off['unsaturated']==6 and off['epa']==180 and off['dha']==120 and off['ala']==.5
 assert off['omega3'] is None, 'Do not fabricate total omega-3 from a subset of acids'
 assert page.evaluate("fromOFF({code:'test',nutriments:{'monounsaturated-fat_100g':4}}).unsaturated") is None
 assert page.evaluate('nutrientGroups.map(g=>g.name)')==['Минералы','Витамины','Жиры и жирные кислоты','Углеводы и клетчатка','Другие нутриенты']
 assert not page.get_by_text('Микронутриенты — необязательно',exact=True).count()
 print('PASS: simplified taxonomy, independent omega-3/EPA/DHA/ALA accounting, EPA/DHA mg, and qualified unsaturated fat import')
 # OFF legacy API mass fields are normalized to grams; UI converts to each nutrient's unit.
 imported=page.evaluate("fromOFF({code:'expanded',nutriments:{'inositol_100g':.35,'biotin_100g':.00003,'beta-carotene_100g':.002,'carnitine_100g':.02,'cholesterol_100g':.055,'sugars_100g':10,'added-sugars_100g':3,'starch_100g':4,'polyols_100g':1,'saturated-fat_100g':2,'monounsaturated-fat_100g':3,'polyunsaturated-fat_100g':2,'trans-fat_100g':0}})")
 for key,value in {'inositol':350,'biotin':30,'betaCarotene':2000,'carnitine':20,'cholesterol':55,'sugars':10,'addedSugars':3,'starch':4,'polyols':1,'saturated':2,'monounsaturated':3,'polyunsaturated':2,'trans':0,'unsaturated':5}.items():
  assert abs(imported[key]-value)<1e-8,(key,imported[key])
 absent=page.evaluate("fromOFF({code:'no-data',nutriments:{}})")
 assert all(absent[k] is None for k in ['inositol','biotin','betaCarotene','carnitine','cholesterol','addedSugars'])
 for key,val in [('name','Расширенный тестовый продукт'),('kcal','100'),('protein','1'),('fat','3'),('carbs','8')]:page.locator('#product-'+key).fill(val)
 page.locator('#product-form details').evaluate('(e)=>e.open=true')
 page.locator('#product-inositol').fill('25');page.locator('#product-biotin').fill('10');page.locator('#product-sugars').fill('2');page.locator('#product-addedSugars').fill('1')
 page.locator('#product-save').click();page.locator('#food-grams').fill('100');page.locator('#food-form button').click()
 macros_before=page.locator('#macros').inner_text()
 add('inositol',.5,'g','Инозитол')
 add('biotin',.03,'mg','Биотин')
 assert '525 мг' in row('inositol').inner_text() and '%' not in row('inositol').inner_text()
 assert row('inositol').get_by_role('meter').count()==0
 assert '40 / 30 мкг · 133%' in row('biotin').inner_text()
 assert page.locator('#macros').inner_text()==macros_before
 assert '2 г' in row('sugars').inner_text() and '1 г' in row('addedSugars').inner_text()
 for key in ['cholesterol','saturated','trans','betaCarotene','carnitine','sugars','addedSugars','polyols','starch']:
  assert row(key).get_by_role('meter').count()==0
 page.reload()
 assert '525 мг' in row('inositol').inner_text() and '40 / 30 мкг · 133%' in row('biotin').inner_text()
 assert page.locator('#macros').inner_text()==macros_before
 print('PASS: expanded catalog mapping, unknown data, inositol without invented target, biotin AI, food + supplements, no duplicate macro accounting, offline persistence')
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 page.locator('#supplements').screenshot(path='/tmp/luna-check/supplements.png')
 assert not errors,errors
 print('PASS: catalog unit conversions, unknown RAE handling, responsive layout, no browser errors')
 b.close()
