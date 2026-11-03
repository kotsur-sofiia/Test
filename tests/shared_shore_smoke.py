"""Primary pages share sea geometry, headline offsets and caption-aligned fade."""
import os
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright

URL = os.environ.get('LUNA_TEST_URL', 'http://127.0.0.1:8007/Test/').split('#')[0]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context()
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width in [320, 390, 768, 1280]:
        page.set_viewport_size({'width': width, 'height': 844})
        reference = None
        for route in ['account', 'cycle', 'capture', 'library']:
            page.goto(URL + '#' + route)
            page.evaluate('document.fonts.ready')
            page.wait_for_timeout(80)
            geometry = page.evaluate('''()=>{
                const style=getComputedStyle(document.documentElement);
                const title=document.querySelector('#page-title').getBoundingClientRect();
                const sea=document.querySelector('.shore-fixed-layer');
                return {top:title.top,font:getComputedStyle(document.querySelector('#page-title')).fontSize,
                    height:parseFloat(style.getPropertyValue('--shore-photo-height')),
                    start:parseFloat(style.getPropertyValue('--shore-fade-start')),
                    end:parseFloat(style.getPropertyValue('--shore-fade-end')),
                    image:getComputedStyle(sea).backgroundImage};
            }''')
            if reference is None:
                reference = geometry
            for key in ['top', 'height', 'start', 'end']:
                assert abs(geometry[key] - reference[key]) < 1, (width, route, key, geometry, reference)
            assert geometry['font'] == reference['font']
            assert geometry['image'] == reference['image']
            content=page.locator('main>section[data-main-view]:not([hidden])').first
            assert content.bounding_box()['y'] >= geometry['end'], (width, route, 'content covered by fixed sea')
            labels = [e for e in page.locator('.profile-tabs a,.section-navigation nav a,#diary-shell .topic-label').all() if e.is_visible()]
            if labels:
                bottom = max(e.bounding_box()['y'] + e.bounding_box()['height'] for e in labels)
                assert abs(geometry['start'] - bottom) < 1, (width, route, geometry, bottom)
                first = next(e for e in page.locator('.profile-tabs,.section-navigation,#diary-shell').all() if e.is_visible())
                title = page.locator('#page-title').bounding_box()
                assert abs(first.bounding_box()['y'] - title['y'] - title['height'] - 16) < 1
            before = page.locator('.shore-fixed-layer').bounding_box()
            page.evaluate('scrollTo(0,100000)')
            assert page.locator('.shore-fixed-layer').bounding_box() == before
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        print('PASS identical sea and fade, title top and 16px controls gap across four pages at', width, flush=True)
    page.set_viewport_size({'width':390,'height':844})
    page.goto(URL+'#cycle')
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(80)
    start,end=page.evaluate('["--shore-fade-start","--shore-fade-end"].map(k=>parseFloat(getComputedStyle(document.documentElement).getPropertyValue(k)))')
    page.add_style_tag(content='html,body{background:transparent!important}body::before{display:none!important}.layout,.bottom-nav{visibility:hidden!important}')
    pixels=Image.open(BytesIO(page.screenshot(omit_background=True))).convert('RGBA')
    alpha=[pixels.getpixel((195,int(y)))[3] for y in [start-3,(start+end)/2,end+8]]
    assert alpha[0]>=250 and 20<alpha[1]<220 and alpha[2]==0,alpha
    assert not errors,errors
    browser.close()
    print('PASS sea opaque through captions, fades below them and reaches full transparency:',alpha)
