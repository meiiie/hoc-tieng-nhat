"""Shared first-run helper: walks the five-step onboarding wizard like a learner."""
def onboard(pg,start='n5',name='',goal=None,style=None):
 pg.wait_for_selector('#nm');pg.fill('#nm',name);pg.click('#nx')
 for key,val in [('start',start),('goal',goal),('style',style)]:
  pg.wait_for_selector('[data-%s]'%key)
  if val is not None:pg.click('[data-%s="%s"]'%(key,val))
  pg.click('#nx')
 pg.wait_for_selector('.plan');pg.click('#nx')
 # The onboarding wizard itself has .v-home at the root URL. Wait for the
 # completed screen, which is shown only after its awaited progress save.
 pg.wait_for_selector('.kana-grid' if start=='kana' else '.v-home .ja-levels')


def main():
 """Standalone gate as well as the shared helper; uses fresh browser storage."""
 import json,os,sys
 from pathlib import Path
 from playwright.sync_api import sync_playwright
 base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8931/'
 result={'url':base,'engines':{}}
 with sync_playwright() as p:
  for engine in ['chromium','webkit']:
   browser=getattr(p,engine).launch();checks=[]
   for start in ['kana','n5','n4','n3']:
    ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
    pg=ctx.new_page();pg.goto(base);pg.wait_for_selector('#nm')
    assert pg.get_attribute('[role=progressbar]','aria-valuenow')=='1'
    pg.fill('#nm','Minh');pg.click('#nx');pg.wait_for_selector('[data-start]')
    pg.click('[data-start="%s"]'%start);pg.click('#nx');pg.wait_for_selector('[data-goal]')
    pg.locator('[data-goal]').last.click();goal=pg.locator('[data-goal][aria-checked=true]').get_attribute('data-goal')
    pg.click('#back');pg.wait_for_selector('[data-start]');assert pg.locator('[data-start][aria-checked=true]').get_attribute('data-start')==start
    pg.click('#nx');pg.wait_for_selector('[data-goal]');assert pg.locator('[data-goal][aria-checked=true]').get_attribute('data-goal')==goal
    pg.click('#nx');pg.wait_for_selector('[data-style]');pg.locator('[data-style]').last.click()
    style=pg.locator('[data-style][aria-checked=true]').get_attribute('data-style')
    pg.click('#nx');pg.wait_for_selector('.plan');assert pg.get_attribute('[role=progressbar]','aria-valuenow')=='5'
    assert not pg.evaluate('!!S.user?.done');pg.click('#nx');pg.wait_for_selector('.kana-grid' if start=='kana' else '.v-home .ja-levels')
    user=pg.evaluate('S.user');assert all(user[k]==v for k,v in {'name':'Minh','start':start,'goal':goal,'style':style,'done':True}.items())
    level=3 if start=='n3' else 4 if start=='n4' else 5
    assert pg.evaluate('S.set.f.cefr')=='N'+str(level)
    assert pg.evaluate('(n)=>Object.keys(S.jaUnlocked).filter(k=>S.jaUnlocked[k]).map(Number).sort().join()===Array.from({length:6-n},(_,i)=>i+n).join()',level)
    pg.reload();pg.wait_for_selector('.view');assert pg.locator('#nm').count()==0;assert pg.evaluate('S.user')==user
    checks.append(start+': five steps, back preserves choices, plan, unlock and reload');ctx.close()
   ctx=browser.new_context();pg=ctx.new_page();pg.goto(base);pg.wait_for_selector('#sk');pg.click('#sk')
   for selector in ['[data-start]','[data-goal]','[data-style]','.plan']:
    pg.wait_for_selector(selector);pg.click('#nx')
   pg.wait_for_selector('.kana-grid');assert pg.evaluate('S.user.name')=='';assert pg.evaluate('S.user.goal')=='5';assert pg.evaluate('S.user.style')=='cards'
   checks.append('skip name and defaults');ctx.close();browser.close()
   result['engines'][engine]={'passed':len(checks),'checks':checks}
   print(engine,len(checks),'onboarding checks passed',flush=True)
 out=Path(os.environ.get('REPORT_DIR',Path(__file__).resolve().parents[2]/'reports'));out.mkdir(parents=True,exist_ok=True)
 (out/(os.environ.get('REPORT_PREFIX','')+'onboard.json')).write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
