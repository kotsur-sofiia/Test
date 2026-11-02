"""Fill the three visible birth-date controls through the UI."""
def fill_birth_date(page,value):
 year,month,day=value.split('-')
 for part,text in [('Day',day),('Month',month),('Year',year)]:page.locator('#profile-birth'+part).fill(text)

def open_about(page):
 page.locator('.bottom-nav [data-view="profile"]').click()
 page.locator('#account [href="#profile"]').click()
 page.locator('#profile').wait_for(state='visible')
