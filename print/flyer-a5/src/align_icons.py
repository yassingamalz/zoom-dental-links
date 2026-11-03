"""Centre each icon vertically on its text's ink box. Measures nested elements in isolation."""
import json, subprocess, sys, pathlib, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent
CSSW=148*96/25.4; CSSH=210*96/25.4; DPR=3; S=CSSW*DPR/1054.0

def ink_boxes(html, ids):
    out={}
    with sync_playwright() as p:
        br=p.chromium.launch(args=['--no-sandbox']); pg=br.new_page(viewport={'width':600,'height':820},device_scale_factor=DPR)
        pg.goto('file://'+str(html)); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{for(const e of [document.documentElement,document.body,document.getElementById('page'),document.getElementById('stage')])e.style.background='transparent'}")
        for k in ids:
            pg.evaluate("""(k)=>{for(const c of document.getElementById('stage').querySelectorAll('*')) c.style.visibility='hidden';
                 const t=document.getElementById(k); t.style.visibility='visible';
                 for(const c of t.querySelectorAll('*')) c.style.visibility='visible';}""",k)
            pg.screenshot(path='/tmp/_iso.png',clip={'x':0,'y':0,'width':CSSW,'height':CSSH},omit_background=True)
            a=np.array(Image.open('/tmp/_iso.png'))[...,3]>110
            ys=np.where(a.any(1))[0]; xs=np.where(a.any(0))[0]
            rc=a.sum(1); core=np.where(rc>=0.35*rc.max())[0]   # dense rows = the letters' body
            out[k]=[xs.min()/S,ys.min()/S,xs.max()/S,ys.max()/S,(core.min()+core.max())/2/S] if len(xs) else None
        br.close()
    return out

def run(build_cmd, html, pairs, offfile):
    off=json.loads(pathlib.Path(offfile).read_text()) if pathlib.Path(offfile).exists() else {}
    for it in range(3):
        if build_cmd: subprocess.run(build_cmd,check=True,capture_output=True)
        ids=[i for pr in pairs for i in pr]
        b=ink_boxes(html, ids); worst=0
        for icon,txt in pairs:
            ci=(b[icon][1]+b[icon][3])/2; ct=b[txt][4]
            d=ct-ci; off[icon]=round(off.get(icon,0)+d,2); worst=max(worst,abs(d))
            if it==0: print(f'  {icon:5s} vs {txt:7s}: icon centre {ci:7.1f}  text centre {ct:7.1f}  -> shift {d:+.1f}')
        pathlib.Path(offfile).write_text(json.dumps(off,indent=1))
        if worst<0.4: break
    if build_cmd: subprocess.run(build_cmd,check=True,capture_output=True)
    b=ink_boxes(html, [i for pr in pairs for i in pr])
    for icon,txt in pairs:
        print(f'  final {icon:5s}: centre offset {b[txt][4]-(b[icon][1]+b[icon][3])/2:+.2f} px  | gap icon->text {b[txt][0]-b[icon][2] if b[txt][0]>b[icon][2] else b[icon][0]-b[txt][2]:.1f} px')
    return b

if __name__=='__main__':
    run(['python3',str(ROOT/'build_back.py')], ROOT/'back_plain.html',
        [('wa','nums'),('soc','handle'),('fpin','addr2'),('bpin','band')], ROOT/'icon_off.json')
