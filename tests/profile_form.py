"""Fill the single dotted birth-date field through the UI."""
def fill_birth_date(page,value):
 year,month,day=value.split('-')
 page.locator('#profile-birthDate').fill(day+'.'+month+'.'+year)

def move_topic(page,topic,direction):
 control=page.locator(f'#widget-options [data-topic="{topic}"] [data-action=reorder]')
 control.focus();control.press('Space');control.press('ArrowUp' if direction<0 else 'ArrowDown');control.press('Enter')

def open_about(page):
 page.locator('.bottom-nav [data-view="profile"]').click()
 page.locator('#account [href="#profile"]').click()
 page.locator('#profile').wait_for(state='visible')


def open_period_editor(page):
 if not page.locator("#period-dialog").evaluate("(e)=>e.open"):
  page.locator("#cycle-start-action").click()
