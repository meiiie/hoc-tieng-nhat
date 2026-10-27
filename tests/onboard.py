"""Shared first-run helper: walks the five-step onboarding wizard like a learner."""
def onboard(pg,start='n5',name='',goal=None,style=None):
 pg.wait_for_selector('#nm');pg.fill('#nm',name);pg.click('#nx')
 for key,val in [('start',start),('goal',goal),('style',style)]:
  pg.wait_for_selector('[data-%s]'%key)
  if val is not None:pg.click('[data-%s="%s"]'%(key,val))
  pg.click('#nx')
 pg.wait_for_selector('.plan');pg.click('#nx')
