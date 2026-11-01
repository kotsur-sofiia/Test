"""Profile, DRI, salt, archived-data and composite omega-3 browser regressions."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8007/Test/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=b.new_context(viewport={'width':1280,'height':1050},timezone_id='Europe/Podgorica')
 ctx.add_init_script("""if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-10'],cycleLength:28,periodLength:5,sleep:[],meals:[],products:[{id:'custom-archived',name:'Прежний продукт',kcal:100,protein:1,fat:2,carbs:3,sugars:2,inositol:20}],water:[{id:'old-water',date:'2026-10-01',ml:250,container:'glass'}],supplements:[{id:'old-omega6',name:'Прежняя запись',date:'2026-10-01',nutrient:'omega6',dose:100,unit:'mg'}]}));""")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 def row(key):return page.locator(f'#nutrients [data-nutrient="{key}"]')
 assert page.locator('#profile-form').is_visible()
 assert 'Без профиля' in page.locator('#profile-summary').inner_text()
 assert '%' not in row('potassium').inner_text()
 keys=page.evaluate('nutrients.map(n=>n[0])')
 assert len(keys)==len(set(keys))==33
 assert set(keys)==set(page.evaluate('LunaDRI.keys'))|{'inositol'}
 grouped=page.evaluate('nutrientGroups.flatMap(g=>g.keys)')
 assert len(grouped)==len(set(grouped))==33 and set(grouped)==set(keys)
 assert page.locator('#nutrients [data-group="electrolytes"] .salt-block [data-nutrient="sodium"]').count()==1
 assert page.locator('#nutrients [data-group="electrolytes"] .salt-block [data-nutrient="chloride"]').count()==1
 assert page.locator('#nutrients [data-group="minerals"] [data-nutrient="phosphorus"]').count()==1
 for key in ['vanadium','sulfur','cobalt','carnitine','sugars','cholesterol','omega6','epa','dha']:
  assert row(key).count()==0
 for key in ['ala','la','omega6','epa','dha']:
  assert page.locator(f'#supplement-nutrient option[value="{key}"]').count()==0
 assert page.locator('#supplement-nutrient option[value="omega3"]').count()==1
 assert page.locator('#profile-month').count()==0
 page.evaluate("state.profile={name:'Прежний профиль',sex:'female',age:35,ageUnit:'years',weight:64,status:'pregnant',month:3};save()")
 page.reload()
 assert page.locator('#profile-status').input_value()=='pregnant'
 assert page.locator('#profile-weight').input_value()=='64'
 assert 'месяц' not in page.locator('#profile-summary').inner_text()
 assert page.locator('#profile-month').count()==0
 def profile(age,sex='female',status='none',unit='years'):
  page.locator('#profile-name').fill('Тестовый профиль');page.locator('#profile-age-unit').select_option(unit);page.locator('#profile-age').fill(str(age));page.locator('#profile-age').dispatch_event('change');page.locator('#profile-sex').select_option(sex);page.locator('#profile-weight').fill('60' if unit=='years' else '7.5')
  if sex=='female' and unit=='years' and age>=10:
   page.locator('#profile-status').select_option(status)
  page.locator('#profile-form button').click()
 def norm(key):return page.evaluate('(key)=>reference(key)?.value??null',key)
 profile(35)
 assert norm('potassium')==2600 and norm('phosphorus')==700 and norm('iron')==18
 assert 'консультация' in page.locator('#profile-advice').inner_text()
 page.locator('#food-product').select_option('oats');page.locator('#food-form button').click()
 assert '362 / 2600 мг · 14%' in row('potassium').inner_text()
 assert '410 / 700 мг · 59%' in row('phosphorus').inner_text()
 profile(35,'male');assert norm('potassium')==3400 and norm('iron')==8
 assert not page.locator('#cycle').is_visible()
 profile(35,status='planning');assert norm('folate')==400
 assert 'до беременности' in page.locator('#profile-advice').inner_text()
 profile(35,status='pregnant')
 assert norm('potassium')==2900 and norm('magnesium')==360 and norm('iron')==27 and norm('folate')==600
 assert not page.locator('#cycle').is_visible() and page.evaluate('phaseAt(today)') is None
 assert page.evaluate('!Object.hasOwn(state.profile,"month")')
 profile(35,status='lactating')
 assert norm('potassium')==2800 and norm('iron')==9 and norm('iodine')==290 and norm('choline')==550 and norm('folate')==500
 assert 'Лактация' in page.locator('#profile-advice').inner_text() and 'консультация' in page.locator('#profile-advice').inner_text()
 assert not page.locator('#cycle').is_visible() and page.evaluate('phaseAt(today)') is None
 assert page.locator('#profile-month').count()==0
 page.reload()
 assert page.locator('#profile-status').input_value()=='lactating' and norm('potassium')==2800
 profile(17,status='lactating')
 assert norm('potassium')==2500 and norm('calcium')==1300 and norm('iron')==10
 profile(13,status='lactating')
 assert norm('iron') is None and 'не назначаются' in page.locator('#profile-advice').inner_text()
 profile(35,'male')
 assert not page.locator('#profile-status-label').is_visible() and page.evaluate('state.profile.status')=='none'

 profile(17,status='pregnant')
 assert norm('phosphorus')==1250 and norm('calcium')==1300 and norm('magnesium')==400
 profile(13,status='pregnant')
 assert norm('iron') is None and 'не назначаются' in page.locator('#profile-advice').inner_text()
 profile(5);assert norm('potassium')==2300 and norm('phosphorus')==500 and norm('sodium')==1000
 assert not page.locator('#profile-status-label').is_visible()
 profile(7,unit='months');assert norm('potassium')==860 and norm('phosphorus')==275 and norm('fiber') is None
 assert '%' not in row('fiber').inner_text()
 assert 'Взрослый предел' in page.locator('#salt-summary').inner_text()
 profile(71);assert norm('d')==20 and norm('calcium')==1200
 profile(35)
 print('PASS: profile questionnaire, child/infant/teen/adult/elderly/pregnancy references, planning, lactation, legacy profile migration, removed month field, unsupported states, cycle suppression')
 # Archive fields must remain stored when editing a product under the new filtered schema.
 page.get_by_role('button',name='Изменить Прежний продукт',exact=True).click();page.locator('#product-name').fill('Прежний продукт — обновлён');page.locator('#product-save').click()
 assert page.evaluate('state.products[0].sugars')==2
 for key,val in [('name','Электролиты — тест'),('kcal','0'),('protein','0'),('fat','0'),('carbs','0')]:page.locator('#product-'+key).fill(val)
 page.locator('#product-form details').evaluate('(e)=>e.open=true')
 for key,val in [('sodium','400'),('chloride','2000'),('potassium','200'),('phosphorus','100')]:page.locator('#product-'+key).fill(val)
 page.locator('#product-save').click();page.locator('#food-grams').fill('100');page.locator('#food-form button').click()
 assert '562 / 2600 мг · 22%' in row('potassium').inner_text()
 assert '510 / 700 мг · 73%' in row('phosphorus').inner_text()
 assert '1 г' in page.locator('#salt-summary').inner_text()
 assert '400 / 1500 мг · 27%' in row('sodium').inner_text()
 assert page.evaluate("fromOFF({code:'salt',nutriments:{salt_100g:1}}).sodium")==400
 assert page.evaluate("fromOFF({code:'salt',nutriments:{salt_100g:1}}).chloride") is None
 assert page.evaluate("fromOFF({code:'zero',nutriments:{salt_100g:1,sodium_100g:0}}).sodium")==0
 print('PASS: potassium/phosphorus food quantities, isolated salt equivalent, sodium/Cl not added, no inferred chloride, preservation of archive product fields')
 page.locator('#supplement-name').fill('Тестовый комплекс омега-3');page.locator('#supplement-nutrient').select_option('omega3')
 assert page.locator('#omega3-composition').is_visible() and not page.locator('#supplement-dose').is_visible()
 for key,val in [('total','1000'),('ala','100'),('epa','300'),('dha','200')]:page.locator('#omega3-'+key).fill(val)
 page.locator('#supplement-form button').click()
 assert page.locator('#supplement-history .record').count()==1
 assert 'АЛК: 100 мг' in page.locator('#supplement-history').inner_text()
 assert 'ЭПК: 300 мг' in page.locator('#supplement-history').inner_text()
 assert 'ДГК: 200 мг' in page.locator('#supplement-history').inner_text()
 assert '0,1 / 1.1 г · 9%' in row('ala').inner_text()
 assert page.evaluate('state.supplements.at(-1).kind')=='omega3-complex'
 page.locator('#omega3-total').fill('100');page.locator('#omega3-epa').fill('300');page.locator('#supplement-form button').click()
 assert 'превышает' in page.locator('#supplement-message').inner_text()
 assert page.locator('#supplement-history .record').count()==1
 page.locator('#omega3-total').fill('');page.locator('#omega3-epa').fill('');page.locator('#omega3-dha').fill('120');page.locator('#supplement-form button').click()
 assert page.locator('#supplement-history .record').count()==2
 assert page.evaluate('state.supplements.at(-1).totalMg') is None
 assert 'общая омега-3 1000 мг' in page.locator('#omega3-day-summary').inner_text().replace('\xa0','').replace('\u202f','')
 assert 'ДГК 320 мг' in page.locator('#omega3-day-summary').inner_text()
 assert '0,1 / 1.1 г · 9%' in row('ala').inner_text()
 # Normal supplement units still work; compound entry is one record, not three.
 page.locator('#supplement-nutrient').select_option('d');page.locator('#supplement-dose').fill('600');page.locator('#supplement-unit').select_option('iu');page.locator('#supplement-form button').click()
 assert '15 / 15 мкг · 100%' in row('d').inner_text()
 assert page.locator('#supplement-history .record').count()==3
 profile(35,status='lactating')
 with page.expect_download() as download:page.locator('#export-data').click()
 data=json.loads(Path(download.value.path()).read_text())
 assert data['profile']['age']==35 and data['profile']['status']=='lactating' and 'month' not in data['profile'] and len(data['supplements'])==4
 assert data['supplements'][0]['id']=='old-omega6'
 ctx.set_offline(True);page.reload()
 assert page.locator('#connection').inner_text()=='Без интернета'
 assert norm('potassium')==2800 and page.locator('#profile-status').input_value()=='lactating' and page.locator('#profile-name').input_value()=='Тестовый профиль'
 assert page.locator('#supplement-history .record').count()==3
 page.locator('#supplement-history .record').first.locator('button').click()
 assert '0 / 1.1 г' in row('ala').inner_text() or 'Нет данных' in row('ala').inner_text()
 assert page.evaluate('state.supplements.some(s=>s.id===\'old-omega6\')')
 page.reload();assert page.locator('#supplement-history .record').count()==2
 assert page.evaluate('state.water[0].ml')==250 and page.evaluate('state.periods[0]')=='2026-10-10'
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 page.locator('#supplements').screenshot(path='/tmp/luna-check/supplements.png')
 assert not errors,errors
 print('PASS: single omega-3 record, optional/validated components, no double counting, no omega-6 options, old logs preserved, vitamin D IU, export, offline profile/norms, deletion, responsive UI')
 b.close()
