"""Align every text block's ink box to its comp target, measuring each block in isolation."""
import json, subprocess, pathlib, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent
T=json.load(open(ROOT/'targets.json'))
import os
MODE={'head':tuple(os.environ.get('HEADMODE','r,c').split(',')),'title':('r','c'),'ig':('l','c'),'addr':('r','c')}   # default ('c','c')
CSSW=148*96/25.4; DPR=3; S=CSSW*DPR/1054.0
def measure():
    subprocess.run(['python3',str(ROOT/'build_back.py')],check=True,capture_output=True)
    out={}
    with sync_playwright() as p:
        br=p.chromium.launch(args=['--no-sandbox']); pg=br.new_page(viewport={'width':600,'height':820},device_scale_factor=DPR)
        pg.goto('file://'+str(ROOT/'back_plain.html')); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{for(const e of [document.documentElement,document.body,document.getElementById('page'),document.getElementById('stage')])e.style.background='transparent'}")
        for k in T:
            pg.evaluate("""(k)=>{for(const c of document.getElementById('stage').children)
                 c.style.visibility=(c.id===k)?'visible':'hidden'}""",k)
            pg.screenshot(path='/tmp/_iso.png',clip={'x':0,'y':0,'width':CSSW,'height':210*96/25.4},omit_background=True)
            a=np.array(Image.open('/tmp/_iso.png'))[...,3]>110
            ys=np.where(a.any(1))[0]; xs=np.where(a.any(0))[0]
            out[k]=[xs.min()/S,ys.min()/S,xs.max()/S,ys.max()/S] if len(xs) else None
        br.close()
    return out
off=json.load(open(ROOT/'off.json')) if (ROOT/'off.json').exists() else {}
for it in range(3):
    got=measure(); worst=0
    for k,t in T.items():
        g=got[k]
        if g is None: print('MISSING',k); continue
        hx,vy=MODE.get(k,('c','c'))
        ex={'c':(t[0]+t[2])/2-(g[0]+g[2])/2,'r':t[2]-g[2],'l':t[0]-g[0]}[hx]
        ey={'c':(t[1]+t[3])/2-(g[1]+g[3])/2,'b':t[3]-g[3]}[vy]
        o=off.get(k,[0,0]); off[k]=[round(o[0]+ex,2),round(o[1]+ey,2)]
        if k=="head": print("  head got",[round(v,1) for v in g],"off->",off[k])
        worst=max(worst,abs(ex),abs(ey))
    json.dump(off,open(ROOT/'off.json','w'),indent=1)
    print(f'iter {it}: worst correction {worst:.2f} px')
    if worst<0.6: break
got=measure()
print(f"{'id':7s} {'target w':>8s} {'got w':>6s}   {'target h':>8s} {'got h':>6s}")
for k,t in T.items():
    g=got[k]; print(f"{k:7s} {t[2]-t[0]+1:8.0f} {g[2]-g[0]:6.1f}   {t[3]-t[1]+1:8.0f} {g[3]-g[1]:6.1f}")
