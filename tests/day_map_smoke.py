"""Personal day map: real UI, persistence, existing diaries, notes and failed saves."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from datetime import datetime, timezone
import json, os

URL = os.environ.get('LUNA_TEST_URL','http://127.0.0.1:8034/Test/').split('#')[0]
Path('/tmp/luna-check').mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True, locale='ru-RU', timezone_id='Europe/Podgorica')
    context.add_init_script("""if(!localStorage.getItem('luna-diary-v1'))localStorage.setItem('luna-diary-v1',JSON.stringify({periods:['2026-10-20'],cycleLength:28,periodLength:5,sleep:[],meals:[{id:'legacy-meal',date:'2026-11-02',product:'oats',grams:100}],water:[{id:'legacy-water',date:'2026-11-02',ml:200,container:'glass'}]}));""")
    page = context.new_page(); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
    page.clock.install(time=datetime(2026,11,2,12,tzinfo=timezone.utc))
    page.goto(URL); page.wait_for_function('navigator.serviceWorker.controller!==null'); page.evaluate('document.fonts.ready')
    expect(page.locator('#home')).to_be_visible()
    assert page.locator('[data-main-view]:visible').count()==1
    assert page.locator('[data-widget-id=water] strong').inner_text()=='200 мл'
    assert page.locator('[data-widget-id=food] strong').inner_text()=='Продуктов сегодня: 1'
    assert page.locator('[data-widget-id=cycle] strong').inner_text()=='День 14 цикла'
    assert page.locator('#home h1').evaluate('(e)=>getComputedStyle(e).fontFamily').startswith('Comfortaa')

    def order(): return page.locator('#day-widgets>.day-widget:not([hidden])').evaluate_all('(els)=>els.map(e=>e.dataset.widgetId)')
    def choose(topic):
        page.locator('#add-widget-top').click()
        page.locator(f'#widget-options [data-topic="{topic}"]').click()
        assert page.locator(f'#widget-options [data-topic="{topic}"]').is_disabled()
        page.locator('#widget-picker [data-close-dialog]').click()
    def notes(topic,text,date=None):
        page.locator(f'[data-widget-id="{topic}"] .mini').click()
        if date:
            page.locator('#widget-note-date').fill(date);page.locator('#widget-note-date').dispatch_event('change')
        page.locator('#widget-note-text').fill(text);page.locator('#widget-note-form button').click()
        expect(page.locator('#widget-note-text')).to_have_value('')
        page.locator('#widget-notes [data-close-dialog]').click()

    assert order()==['affirmation','cycle','sleep','food','water']
    choose('skin'); choose('books')
    notes('skin','Мягкий уход, кожа спокойная.')
    notes('books','Маленький принц · 15 страниц')
    assert page.locator('[data-widget-id=skin] strong').inner_text()=='Мягкий уход, кожа спокойная.'
    notes('skin','Вчера была сухость','2026-11-01')
    assert page.locator('[data-widget-id=skin] strong').inner_text()=='Мягкий уход, кожа спокойная.'
    page.locator('[data-widget-id=skin] .mini').click()
    page.locator('#widget-note-date').fill('2026-11-02');page.locator('#widget-note-date').dispatch_event('change')
    assert 'Вчера' not in page.locator('#widget-note-history').inner_text()
    page.locator('#widget-note-text').fill('Несохранённый черновик')
    page.locator('#widget-notes [data-close-dialog]').click()
    page.locator('[data-widget-id=skin] .mini').click();expect(page.locator('#widget-note-text')).to_have_value('Несохранённый черновик')
    # Escape and route changes close the modal without saving the draft.
    page.keyboard.press('Escape');expect(page.locator('#widget-notes')).not_to_be_visible()
    page.locator('#add-widget-top').click();page.evaluate('location.hash="sleep"');expect(page.locator('#widget-picker')).not_to_be_visible()
    page.locator('.bottom-nav [href="#home"]').click()

    page.locator('#add-widget-top').click()
    custom_title='<img src=x> Творчество'
    page.locator('#custom-widget-title').fill(custom_title);page.locator('#custom-widget-form button').click()
    custom_id=page.evaluate('state.dayMap.custom[0].id')
    assert page.locator('#widget-picker img').count()==0
    page.locator('#widget-picker [data-close-dialog]').click()
    notes(custom_id,'Акварель, 20 минут')
    page.locator('#edit-day').click()
    before=order();page.locator(f'[data-widget-id="{custom_id}"] [data-action=up]').click()
    assert order()[-2:]==[custom_id,'books']
    page.locator('[data-widget-id=skin] [data-action=remove]').click()
    assert 'skin' not in order() and page.evaluate('state.dayMap.notes.filter(n=>n.topic==="skin").length')==2
    page.locator('#edit-day').click();choose('skin')
    assert page.locator('[data-widget-id=skin] strong').inner_text()=='Мягкий уход, кожа спокойная.'
    expected_order=order();page.reload();assert order()==expected_order
    assert page.evaluate('state.meals[0].id')=='legacy-meal' and page.evaluate('state.periods[0]')=='2026-10-20'
    # A previous worker may still cache the old, unversioned scripts on first upgrade.
    # The new HTML must request a different URL, including when loaded offline later.
    page.evaluate('''async()=>{const cache=await caches.open('luna-diary-v34');await cache.put(new URL('./app.js',location.href),new Response('throw Error("Old app script was loaded")',{headers:{'Content-Type':'text/javascript'}}))}''')
    page.reload();expect(page.locator('#home')).to_be_visible();assert order()==expected_order

    # Failed saves restore the previous layout and leave the entered note untouched.
    old=page.evaluate('JSON.stringify(state.dayMap)')
    page.evaluate('()=>{window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException("full","QuotaExceededError")}}')
    page.locator('#add-widget-top').click();page.locator('#custom-widget-title').fill('Не сохранённая тема');page.locator('#custom-widget-form button').click()
    assert page.evaluate('JSON.stringify(state.dayMap)')==old
    assert page.locator('#day-widgets>.day-widget:not([hidden])').count()==len(expected_order)
    expect(page.locator('#custom-widget-title')).to_have_value('Не сохранённая тема')
    assert 'Не удалось' in page.locator('#widget-picker-status').inner_text()
    page.locator('#widget-picker [data-close-dialog]').click()
    page.locator('[data-widget-id=books] .mini').click();page.locator('#widget-note-text').fill('Текст при переполнении')
    page.locator('#widget-note-form button').click()
    assert page.evaluate('JSON.stringify(state.dayMap)')==old
    expect(page.locator('#widget-note-text')).to_have_value('Текст при переполнении')
    page.evaluate('()=>{Storage.prototype.setItem=realSet}');page.locator('#widget-note-form button').click()
    page.locator('#widget-notes [data-close-dialog]').click()

    # Existing diaries remain the source of the live card values.
    page.locator('[data-widget-id=water] a').click();expect(page.locator('#water-form')).to_be_visible()
    page.locator('#water-volume').fill('300');page.locator('#water-form button').click()
    page.locator('.bottom-nav [href="#home"]').click()
    assert page.locator('[data-widget-id=water] strong').inner_text()=='500 мл'
    # Removing every card is intentional and must survive a reload; notes and diaries remain.
    page.locator('#edit-day').click()
    for topic in list(order()):page.locator(f'[data-widget-id="{topic}"] [data-action=remove]').click()
    expect(page.locator('#day-empty')).to_be_visible();page.reload()
    assert order()==[] and page.evaluate('state.dayMap.notes.length')==5
    choose('books');assert page.locator('[data-widget-id=books] strong').inner_text()=='Текст при переполнении'
    choose('affirmation');choose('water')

    for width,height in [(320,844),(375,844),(390,844),(430,844),(768,1000),(1280,1000),(844,390)]:
        page.set_viewport_size({'width':width,'height':height});page.evaluate('document.fonts.ready')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,height)
        assert page.locator('[data-main-view]:visible').count()==1
        page.locator('#add-widget-top').click()
        box=page.locator('#widget-picker').bounding_box()
        assert box['x']>=0 and box['x']+box['width']<=width+1 and box['y']>=0 and box['y']+box['height']<=height+1,(width,height,box)
        for field in page.locator('#widget-picker input').all():assert field.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>=16
        assert page.locator('#widget-picker [data-close-dialog]').bounding_box()['height']>=44
        page.locator('#widget-picker [data-close-dialog]').click()

    # Profile restrictions still apply to the catalog and cannot be bypassed by old map settings.
    page.evaluate('state.profile={name:"Тест",age:35,ageUnit:"years",sex:"male",status:"none"};save()')
    page.locator('#add-widget-top').click();assert page.locator('[data-topic=cycle]').is_disabled()
    page.locator('#widget-picker [data-close-dialog]').click()
    page.evaluate('location.hash="cycle"');expect(page.locator('#cycle')).not_to_be_visible()
    page.locator('.bottom-nav [href="#home"]').click()
    with page.expect_download() as download:page.locator('#export-data').click()
    exported=json.loads(Path(download.value.path()).read_text())
    assert len(exported['dayMap']['notes'])==5 and exported['water'][0]['id']=='legacy-water'
    context.set_offline(True);page.reload();expect(page.locator('#home')).to_be_visible()
    assert page.locator('[data-widget-id=water] strong').inner_text()=='500 мл'
    choose('skin');assert page.locator('[data-widget-id=skin] strong').inner_text()=='Мягкий уход, кожа спокойная.'
    assert page.evaluate('document.fonts.check("600 24px Comfortaa","Мой день")')
    page.clock.fast_forward(13*60*60*1000)
    assert page.locator('#today').get_attribute('datetime')=='2026-11-03'
    assert page.locator('[data-widget-id=water] strong').inner_text()=='0 мл'
    assert page.locator('[data-widget-id=skin] strong').inner_text()=='Уход и твои наблюдения'
    page.locator('[data-widget-id=skin] .mini').click()
    page.locator('#widget-note-date').fill('2026-11-02');page.locator('#widget-note-date').dispatch_event('change')
    assert 'Мягкий уход' in page.locator('#widget-note-history').inner_text()
    assert not errors,errors
    # Ignore unknown card ids and duplicates in imported/older state without replacing diaries.
    clean=browser.new_context()
    clean.add_init_script("""localStorage.setItem('luna-diary-v1',JSON.stringify({periods:[],sleep:[],meals:[],dayMap:{version:1,order:['water','water','unknown'],custom:[],notes:[],futureField:'keep'}}))""")
    another=clean.new_page();another.goto(URL+'#home')
    assert another.locator('#day-widgets>.day-widget:not([hidden])').count()==1
    another.locator('#add-widget-top').click();another.locator('[data-topic=books]').click()
    assert another.evaluate('state.dayMap.futureField')=='keep'
    clean.close()
    browser.close()
    print('PASS: customizable map, own topics, add/remove/reorder, daily notes and drafts, rollback on full storage, empty layout, live diary totals, profile restrictions, responsive sheets, export and offline persistence')
