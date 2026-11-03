import sys, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
from playwright.sync_api import sync_playwright
from PIL import Image
src=sys.argv[1] if len(sys.argv)>1 else 'back_plain.html'
with sync_playwright() as p:
    br=p.chromium.launch(args=['--no-sandbox'])
    pg=br.new_page(viewport={'width':600,'height':820}, device_scale_factor=3)
    pg.goto('file://'+str(ROOT/src)); pg.wait_for_timeout(1800)
    pg.screenshot(path=str(ROOT/'hi.png'), clip={'x':0,'y':0,'width':559.37,'height':793.7}); br.close()
im=Image.open(ROOT/'hi.png').resize((1054,1492), Image.LANCZOS); im.save(ROOT/'mine.png')
ref=Image.open(ROOT.parent/'reference'/'back_comp_chatgpt.png').convert('RGB')
c=Image.new('RGB',(1080,770),'white')
c.paste(ref.resize((527,746)),(6,12)); c.paste(im.convert('RGB').resize((527,746)),(547,12))
c.save(ROOT/'cmp_full.png')
