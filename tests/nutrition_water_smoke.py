"""Run against a local server. External catalog responses are fixtures, not live API verification."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os,json
Path('/tmp/luna-check').mkdir(exist_ok=True)
URL=os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8002/Test/')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1280,'height':950},timezone_id='Europe/Podgorica')
 # Existing v1 user records must survive the additive migration.
 ctx.add_init_script("""if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({profile:{name:'Тест',sex:'female',age:35,ageUnit:'years',weight:60,status:'none',month:null},periods:['2026-10-10'],cycleLength:28,periodLength:5,sleep:[],meals:[{id:'legacy',date:new Date().toLocaleDateString('en-CA'),product:'oats',grams:100}]}));""")
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL);page.wait_for_function('navigator.serviceWorker.controller !== null')
 assert page.locator('#food-calories').inner_text()=='379 ккал'
 assert '13,2' in page.locator('#macros').inner_text()
 assert page.locator('#period-history .record').count()==1
 for key,val in [('name','Мой творог'),('kcal','120'),('protein','10'),('fat','4'),('carbs','10')]:page.locator('#product-'+key).fill(val)
 page.locator('#product-save').click();page.locator('#food-grams').fill('200');page.locator('#food-form button').click()
 assert page.locator('#food-calories').inner_text()=='619 ккал'
 assert '33,2' in page.locator('#macros').inner_text()
 assert '+ ?' in page.locator('#nutrients').inner_text()
 assert page.locator('#custom-products .record').count()==1
 page.get_by_role('button',name='Изменить Мой творог',exact=True).click();page.locator('#product-kcal').fill('150');page.locator('#product-save').click()
 assert page.locator('#food-calories').inner_text()=='619 ккал', 'Past meals must retain original snapshot'
 page.get_by_role('button',name='Удалить из базы Мой творог',exact=True).click()
 assert page.locator('#food-calories').inner_text()=='619 ккал'
 page.reload();assert page.locator('#food-calories').inner_text()=='619 ккал'
 print('PASS: v1 migration, gram-scaled KBJU, custom create/edit/delete, historical snapshot preservation, unknown micronutrients')
 page.locator('#water-form button').click();assert page.locator('#water-total').inner_text()=='250 мл'
 page.locator('#water-container').select_option('bottle');assert page.locator('#water-volume').input_value()=='500'
 page.locator('#water-presets').get_by_role('button',name='300 мл',exact=True).click();page.locator('#water-form button').click()
 page.locator('#water-container').select_option('glass');assert page.locator('#water-volume').input_value()=='250'
 page.locator('#water-volume').fill('330');page.locator('#water-form button').click();assert page.locator('#water-total').inner_text()=='880 мл'
 page.reload();assert page.locator('#water-volume').input_value()=='330';assert page.locator('#water-total').inner_text()=='880 мл'
 page.locator('#food-date').fill('2026-09-01');page.locator('#food-date').dispatch_event('change');assert page.locator('#water-total').inner_text()=='0 мл'
 page.locator('#water-form button').click();assert page.locator('#water-total').inner_text()=='330 мл'
 page.locator('#water-history button').click();assert page.locator('#water-total').inner_text()=='0 мл'
 print('PASS: water presets, arbitrary amount, independent glass/bottle settings, daily totals, deletion, persistence')
 fixture={'status':1,'product':{'code':'1234567890123','product_name':'Тестовый йогурт','brands':'Fixture','nutriments':{'energy-kcal_100g':100,'proteins_100g':5,'fat_100g':4,'carbohydrates_100g':11,'iron_100g':.002,'vitamin-b12_100g':.000002}}}
 page.route('https://world.openfoodfacts.org/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(fixture)))
 page.locator('#catalog-query').fill('1234567890123');page.locator('#catalog-submit').click();page.get_by_role('button',name='Сохранить в мою базу',exact=True).wait_for();page.get_by_role('button',name='Сохранить в мою базу',exact=True).click()
 page.locator('#food-grams').fill('100');page.locator('#food-form button').click()
 assert page.locator('#food-calories').inner_text()=='100 ккал'
 assert '2 / 18 мг · 11%' in page.locator('#nutrients').inner_text()
 assert '2 / 2,4 мкг · 83%' in page.locator('#nutrients').inner_text() or '2 / 2.4 мкг · 83%' in page.locator('#nutrients').inner_text()
 assert 'Нет данных' in page.locator('#nutrients').inner_text()
 assert page.evaluate('state.products[0].folate') is None
 print('PASS: fixture-based barcode import, grams-to-mg/mcg conversion, absent micro data and DFE kept unknown')
 page.unroute('https://world.openfoodfacts.org/**')
 partial={'products':[{'code':'9999999999999','product_name':'Продукт с неполной этикеткой','nutriments':{'proteins_100g':3}}]}
 page.route('https://world.openfoodfacts.org/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(partial)))
 page.evaluate('lastCatalogRequest=0');page.locator('#catalog-query').fill('этикетка');page.locator('#catalog-submit').click();page.get_by_role('button',name='Сохранить в мою базу',exact=True).wait_for();page.get_by_role('button',name='Сохранить в мою базу',exact=True).click();page.locator('#food-form button').click()
 assert '+ ?' in page.locator('#food-calories').inner_text()
 assert 'Нет данных' in page.locator('#nutrients').inner_text()
 print('PASS: fixture-based keyword search and partial macro totals are not presented as complete')
 page.unroute('https://world.openfoodfacts.org/**');page.route('https://world.openfoodfacts.org/**',lambda route:route.abort())
 page.evaluate('lastCatalogRequest=0');page.locator('#catalog-query').fill('неизвестный');page.locator('#catalog-submit').click();page.wait_for_function("document.querySelector('#catalog-status').textContent.includes('недоступен')")
 ctx.set_offline(True);page.reload();assert page.locator('#connection').inner_text()=='Без интернета'
 # Selected diary day resets to today, preserving all logged historical dates.
 assert page.locator('#food-calories').inner_text()=='619 ккал'
 page.locator('#local-product-search').fill('Тестовый');assert page.locator('#food-product option').count()==1
 page.locator('#catalog-query').fill('йогурт');page.locator('#catalog-submit').click();assert 'нет интернета' in page.locator('#catalog-status').inner_text()
 assert page.evaluate('state.meals.length')==4
 print('PASS: catalog errors, saved products offline, no silent data loss')
 ctx.set_offline(False);page.locator('#local-product-search').fill('');page.locator('#food').scroll_into_view_if_needed()
 page.screenshot(path='/tmp/luna-check/nutrition-desktop.png',full_page=True)
 for width in [390,768,1024]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),width
 page.screenshot(path='/tmp/luna-check/nutrition-mobile.png',full_page=True)
 assert not errors,errors
 print('PASS: responsive layouts and no browser errors. Live Open Food Facts access NOT verified.')
 browser.close()
