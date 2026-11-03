"""Upper captions and both profile menus remain pinned while content scrolls."""
import os
from playwright.sync_api import sync_playwright, expect

URL = os.environ.get('LUNA_TEST_URL', 'http://127.0.0.1:8007/Test/').split('#')[0]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context()
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    selectors = 'main>header,.profile-tabs,.section-navigation,#diary-shell'
    for width in [320, 390, 768, 1280]:
        page.set_viewport_size({'width': width, 'height': 844})
        for route in ['cycle', 'profile', 'account', 'settings', 'devices', 'friends', 'library', 'capture']:
            page.goto(URL + '#' + route)
            page.evaluate('document.fonts.ready')
            page.wait_for_timeout(60)
            page.evaluate('scrollTo(0,0)')
            panels = [panel for panel in page.locator(selectors).all() if panel.is_visible()]
            positions = [panel.bounding_box()['y'] for panel in panels]
            for scroll in [128, 500, 100000]:
                page.evaluate('(y)=>scrollTo(0,y)', scroll)
                assert all(abs(panel.bounding_box()['y'] - y) < .1 for panel, y in zip(panels, positions)), (width, route)
            labels = page.locator('.profile-tabs a,.section-navigation nav a,#diary-shell .topic-label')
            visible = [label for label in labels.all() if label.is_visible()]
            if visible:
                bottom = max(label.bounding_box()['y'] + label.bounding_box()['height'] for label in visible)
                height = page.evaluate('parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--top-panel-height"))')
                assert abs(height - bottom - 12) < 1, (width, route, height, bottom)
                photo_height = page.evaluate('parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--shore-photo-height"))')
                assert photo_height * (.13 if width >= 768 else .165) >= bottom + 17, (width, route)
            assert page.locator('.top-panel-background').count()==0
            assert page.locator('.shore-fixed-layer').count()==1
            fade_start = page.evaluate('parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--shore-fade-start"))')
            header_bottom = page.locator('main>header').bounding_box()['height']
            title = page.locator('#page-title').bounding_box()
            title_bottom = title['y'] + title['height']
            expected_start = title_bottom + (header_bottom-title_bottom)/1.5 if visible else header_bottom
            assert abs(fade_start - expected_start) < 1, (width, route, fade_start, expected_start)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        print('PASS pinned heading/menus/captions and 12px lower edge at', width, flush=True)
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(URL + '#account')
    page.evaluate('scrollTo(0,100000)')
    page.locator('[data-menu=profile] [href="#settings"]').click()
    expect(page.locator('#settings')).to_be_visible()
    expect(page.locator('.profile-tabs')).to_be_visible()
    page.wait_for_function('navigator.serviceWorker.controller!==null')
    context.set_offline(True)
    page.reload()
    page.evaluate('scrollTo(0,100000)')
    page.locator('.profile-tabs [href="#friends"]').click()
    expect(page.locator('#friends')).to_be_visible()
    assert not errors, errors
    browser.close()
    print('PASS both profile menus remain usable after scrolling and offline reload')
