#!/usr/bin/env python3
"""List map labels that overlap each other, the pin, or leave the map card. Run after build_back.py."""
import pathlib, itertools
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1054, 'height': 1492})
    pg.goto('file://' + str(ROOT / 'back_plain.html')); pg.wait_for_timeout(1500)
    r = pg.evaluate("""() => { const svg=[...document.querySelectorAll('svg')].find(s=>s.querySelector('.lb'));
      const o=svg.getBoundingClientRect(), k=476/o.width;
      const lb=[...svg.querySelectorAll('.lb')].filter(e=>!e.parentElement.classList.contains('lb'));
      const pin=svg.querySelector("path[stroke-width='2.6']").getBoundingClientRect();
      const f=q=>[(q.left-o.left)*k,(q.top-o.top)*k,(q.right-o.left)*k,(q.bottom-o.top)*k];
      return {pin:f(pin), lb:lb.map(e=>[e.textContent, f(e.getBoundingClientRect())])}; }""")
    b.close()
bad = 0
def hit(a, c, m=1.0): return a[0] < c[2] - m and c[0] < a[2] - m and a[1] < c[3] - m and c[1] < a[3] - m
items = r['lb'] + [['PIN', r['pin']]]
for (n1, a), (n2, c) in itertools.combinations(items, 2):
    if hit(a, c): print('overlap:', n1, '|', n2); bad += 1
for n, a in r['lb']:
    if a[0] < 0 or a[1] < 0 or a[2] > 476 or a[3] > 216: print('outside:', n, [round(v) for v in a]); bad += 1
print(f'{len(r["lb"])} labels, {bad} problems')
