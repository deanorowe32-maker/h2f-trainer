"""Exercise progressions and regressions on the info card. Server on :8765."""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def phone():
        ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
        return pg
    try:
        A = phone(); E = A.evaluate
        # ---------- Task 1 ----------
        check('T1 chain ids exist', E("LAD_CHAINS.flat().filter(id=>!EX[id])").__len__() == 0)
        check('T1 new exercises', E("['ipu','kpu','bapu','npu','spsq'].every(id=>EX[id]&&EX[id].steps.length>=3)"))
        check('T1 pu built-in', E("JSON.stringify(ladFor('pu'))") == '{"e":["kpu"],"h":["hrpu"]}')
        check('T1 researched order', E("ladFor('pull').e.join()") == 'npu,bapu' and E("ladFor('ipu').e.join()") == 'plank' and E("ladFor('bws').h[0]") == 'lm_gsq' and E("ladFor('kbdl').h.includes('bb_rackpull')") and E("ladFor('rlng').e.join()") == 'spsq')
        check('C coverage', E("(()=>{const inC=new Set(LAD_CHAINS.flat());return Object.values(EX).filter(e=>!e.custom&&inC.has(e.id)).length})()") >= 230)
        check('C examples', E("ladFor('tgu').e.includes('kbwin')") and E("ladFor('kbcl').h.includes('kbsn')") and E("ladFor('tbdl').h.includes('dl')") and E("ladFor('lm_press').e.includes('lm_hkp')") and E("ladFor('er90').e.includes('ier')") and E("ladFor('dbote').e.includes('dblte')"))
        check('C no exercise is its own neighbor or in a loop', E("LAD_CHAINS.every(c=>new Set(c).size===c.length)") and E("(()=>{const h={};LAD_CHAINS.forEach(c=>c.forEach((x,i)=>{if(i<c.length-1)(h[x]=h[x]||new Set).add(c[i+1])}));const seen={},bad=[];const dfs=(x,st)=>{if(st.has(x)){bad.push(x);return}if(seen[x])return;seen[x]=1;st.add(x);(h[x]||[]).forEach(y=>dfs(y,st));st.delete(x)};Object.keys(h).forEach(x=>dfs(x,new Set()));return bad.length===0})()"))
        check('C hang power clean both ways', E("ladFor('hpc').e.length>0&&ladFor('hpc').h.includes('pcl')") and E("ladFor('hpc').e.includes('hhp')"))
        check('C wide-grip bench both ways', E("ladFor('bb_widebp').e.length>0&&ladFor('bb_widebp').h.length>0"))
        NEW = ['tb_rdl','tb_bst','tb_row','tb_hkp','tb_floor','tb_carry','tb_suit','tb_shrug','tb_ss','bb_fsq','bb_gm','bb_pend','bb_curl','bb_skull','bb_cgbp','bb_box','bb_shrug','bb_suitdl','db_arnold','db_hammer','db_conc','db_kick','db_shrug','db_floor','db_csrow','db_snatch']
        check('N new exercises exist with steps', E(f"{json.dumps(NEW)}.every(id=>EX[id]&&EX[id].steps.length>=3&&EX[id].cue.length>5)"))
        check('N every new exercise has a ladder', E(f"{json.dumps(NEW)}.every(id=>{{const L=ladFor(id);return L.e.length+L.h.length>0}})"))
        check('N front squat between goblet and back squat', E("ladFor('bb_fsq').e.includes('gsq')&&ladFor('bb_fsq').h.includes('bsq')"))
        check('H hex bar category', E("CATS.hexbar")=='Hex bar' and E("Object.values(EX).filter(e=>e.cat==='hexbar').length") == 11 and E("Object.values(EX).filter(e=>/trap bar/i.test(e.name)).length") == 0)
        E("S.tab='lib';render()"); A.wait_for_timeout(100)
        check('H library chip', E("!!document.querySelector('#view [data-a=libcat][data-v=hexbar]')"))
        SWD = ['ipu','kpu','bapu','npu','spsq','pcl','bb_fsq','bb_pend','bb_gm','bb_box','bb_skull','bb_curl','db_hammer','db_conc','db_arnold','db_floor','db_snatch','tb_shrug','bb_shrug','db_shrug','db_kick']
        check('D SmartWorkout demos for new exercises', E(f"{json.dumps(SWD)}.every(id=>DEMO[id]&&demoLink(id).includes('Watch demo on SmartWorkout'))"))
        check('T1 merges chains', len(E("ladFor('bws').h")) >= 2)
        E("S.prog=prBlank('x',mkey(0));S.prog.ld={pu:{e:['ipu'],h:[]}}")
        check('T1 program wins over built-in', E("ladFor('pu').e.join()") == 'ipu')
        E("S.lad={pu:{e:['chsq'],h:['pplu']}}")
        check('T1 own edit wins', E("JSON.stringify(ladFor('pu'))") == '{"e":["chsq"],"h":["pplu"]}')
        check('T1 clean', E("JSON.stringify(ladClean({pu:{e:['zzz','pu','kpu','ipu','chsq','bws'],h:'x'},zzz:{e:['pu']}}))") == '{"pu":{"e":["kpu","ipu","chsq"],"h":[]}}')
        E("S.prog=null")
        check('T1 backup', E("JSON.stringify(cleanBackup(makeBackup()).lad)") == '{"pu":{"e":["chsq"],"h":["pplu"]}}')
        E("save()"); A.reload(); A.wait_for_timeout(900)
        check('T1 reopen', E("BOOTED") == True and E("S.lad.pu.h[0]") == 'pplu')
        # ---------- Task 2: card ----------
        E("S.lad={};S.prog=null;openInfo('pu')"); A.wait_for_timeout(100)
        t = A.locator('#infoBody').text_content()
        check('T2 card lines', 'Easier' in t and 'Knee Push-Up' in t and 'Harder' in t and 'Hand-Release Push-Up' in t)
        E("document.querySelector('#infoBody .lad [data-a=info][data-v=kpu]').click()"); A.wait_for_timeout(100)
        check('T2 tap opens card', 'Knee Push-Up' in A.locator('#infoBody h2').text_content())
        E("openInfo('pu');document.querySelector('#infoBody [data-a=ladedit]').click()"); A.wait_for_timeout(100)
        E("document.querySelector('#infoBody [data-a=ladadd][data-k=e]').click()"); A.wait_for_timeout(150)
        check('T2 picker open', not E("document.getElementById('pickSheet').hidden"))
        E("document.querySelector('#pickList [data-a=pick][data-v=ipu]').click()"); A.wait_for_timeout(150)
        check('T2 added own', E("JSON.stringify(S.lad.pu)") == '{"e":["kpu","ipu"],"h":["hrpu"]}' and E("document.getElementById('pickSheet').hidden") and 'Incline Push-Up' in A.locator('#infoBody').text_content())
        E("document.querySelector('#infoBody [data-a=ladrm][data-k=h][data-v=hrpu]').click()"); A.wait_for_timeout(100)
        check('T2 removed', E("S.lad.pu.h.length") == 0)
        check('T2 your version label', 'Your version' in A.locator('#infoBody').text_content())
        E("document.querySelector('#infoBody [data-a=ladreset]').click()"); A.wait_for_timeout(100)
        check('T2 reset', E("!S.lad.pu") and 'Hand-Release Push-Up' in A.locator('#infoBody').text_content())
        E("document.querySelector('#infoBody [data-a=laddone]').click();openInfo('pig')"); A.wait_for_timeout(100)
        t = A.locator('#infoBody').text_content()
        check('T2 no ladder hides lines', 'Easier' not in t and A.locator('#infoBody [data-a=ladedit]').count() == 1)
        # ---------- Task 3: ladders travel ----------
        E("S.lad={pu:{e:['ipu'],h:['pplu']}};S.prog=prBlank('x',mkey(0));S.squad.name='SGT Rowe'")
        code = E("prCode()")
        check('T3 code carries ladders', E("JSON.stringify(prParse(prCode()).prog.ld.pu)") == '{"e":["ipu"],"h":["pplu"]}')
        check('T3 cap 40', E("(()=>{const o=prBlank('x',mkey(0));o.ld={};Object.keys(EX).slice(0,60).forEach(k=>o.ld[k]={e:[],h:[]});return Object.keys(prClean(o).ld).length})()") == 40)
        Bp = phone(); F = Bp.evaluate
        F("S.lad={}"); r = F(f"(()=>{{const r=prParse({json.dumps(code)});prApply(r.prog,r.cu);return JSON.stringify(ladFor('pu'))}})()")
        check('T3 soldier sees leader ladder', r == '{"e":["ipu"],"h":["pplu"]}')
        F("S.lad={pu:{e:['chsq'],h:[]}}")
        check('T3 soldier own edit still wins', F("ladFor('pu').e[0]") == 'chsq')
        # custom exercise share carries links
        E("S.custom=S.custom||[];S.custom.push({id:'c_box1',name:'Box Step Push-Up',cat:'bodyweight',sec:'M',eq:'Box',steps:['Do it'],cue:'',link:''});EX.c_box1=Object.assign({},S.custom[S.custom.length-1],{custom:true});S.lad.c_box1={e:['kpu'],h:['pu','zzz']}")
        msg = E("xsMsg([EX.c_box1])")
        F("S.lad={}")
        F(f"xsLoad(xsParse({json.dumps(msg)}));document.querySelector('#cmBody [data-a=xsadd]').click()"); Bp.wait_for_timeout(150)
        nid = F("S.custom.find(c=>c.name==='Box Step Push-Up').id")
        check('T3 shared custom links arrive', F(f"JSON.stringify(S.lad['{nid}'])") == '{"e":["kpu"],"h":["pu"]}')
        Bp.close()
        # ---------- Review fix: picker stacking ----------
        E("S.lad={};openInfo('pu');document.querySelector('#infoBody [data-a=ladedit]').click()"); A.wait_for_timeout(100)
        E("document.querySelector('#infoBody [data-a=ladadd][data-k=h]').click()"); A.wait_for_timeout(100)
        E("document.querySelector('#pickBody [data-a=closepick]').click()"); A.wait_for_timeout(100)
        check('F cancel returns to card', not E("document.getElementById('infoSheet').hidden") and E("document.getElementById('pickSheet').hidden"))
        E("document.querySelector('#infoBody [data-a=laddone]').click();document.querySelector('#infoBody [data-a=closeinfo]').click();openPick('train','M')"); A.wait_for_timeout(100)
        E("document.querySelector('#pickList [data-a=info]').click()"); A.wait_for_timeout(100)
        zi = E("[+getComputedStyle(document.getElementById('infoSheet')).zIndex,+getComputedStyle(document.getElementById('pickSheet')).zIndex]")
        check('F info card shows above normal picker', zi[0] > zi[1])
        check('no page errors', not errs)
    except Exception as e:
        check('exception: ' + str(e)[:300], False)
    print(errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL ' + str(len(fails))))
sys.exit(1 if fails else 0)
