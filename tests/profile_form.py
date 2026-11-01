"""Fill the three visible birth-date controls through the UI."""
def fill_birth_date(page,value):
 year,month,day=value.split('-')
 for part,text in [('Day',day),('Month',month),('Year',year)]:page.locator('#profile-birth'+part).fill(text)
