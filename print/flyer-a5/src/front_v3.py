#!/usr/bin/env python3
"""Front v3 = front v2 with the shared social footer, plus a bleed variant built by
edge extension (the trim artwork is kept bit-for-bit; bleed strips repeat the colour
found on each trim edge)."""
import pathlib, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from footer_parts import footer

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(__file__).resolve().parent / 'front_base_v2.html'   # front v2, self-contained
REFW, REFH, TRIM_W, TRIM_H = 1054.0, 1492.0, 148.0, 210.0
KX, KY = TRIM_W / REFW, TRIM_H / REFH
TEAL = '#0A7183'


def box(x, y, w=None, h=None, extra=''):
    s = f"position:absolute;left:{x:.2f}px;top:{y:.2f}px;"
    if w is not None: s += f"width:{w:.2f}px;"
    if h is not None: s += f"height:{h:.2f}px;"
    return s + extra


def plain_html():
    s = SRC.read_text(encoding='utf-8')
    i = s.find("left:36.00px;top:1329.00px")
    st = s.rfind("<div", 0, i)
    j = s.find("ق٧٢٠٥", i)
    e = s.find("</div>", j) + len("</div>")
    assert st > 0 and e > st
    return s[:st] + '\n'.join(footer(box)) + s[e:]


def edge_runs(png, thr=40):
    """Teal runs along each trim edge, in reference px. png must be the trim render."""
    a = np.array(Image.open(png).convert('RGB')).astype(int)
    H, W, _ = a.shape
    sx, sy = W / REFW, H / REFH
    d = np.abs(a - np.array([10, 113, 131])).sum(2) < thr

    def runs(v):
        out, s0 = [], None
        for k, f in enumerate(v):
            if f and s0 is None: s0 = k
            if not f and s0 is not None: out.append((s0, k - 1)); s0 = None
        if s0 is not None: out.append((s0, len(v) - 1))
        return out
    k0, k1 = 1, 6   # top/left: the edge row itself; right/bottom: clear of pdftoppm's ~2 px sliver
    def clamp(rr, lim):
        return [(a0, lim if b0 >= lim - 3 else b0) for a0, b0 in rr]
    return {'top':    clamp([(a0 / sx, (b0 + 1) / sx) for a0, b0 in runs(d[k0, :])], REFW),
            'bottom': clamp([(a0 / sx, (b0 + 1) / sx) for a0, b0 in runs(d[H - 1 - k1, :])], REFW),
            'left':   clamp([(a0 / sy, (b0 + 1) / sy) for a0, b0 in runs(d[:, k0])], REFH),
            'right':  clamp([(a0 / sy, (b0 + 1) / sy) for a0, b0 in runs(d[:, W - 1 - k1])], REFH)}


def bleed_html(plain, runs, bleed_mm=3.0):
    B, BY = bleed_mm / KX, bleed_mm / KY
    PW, PH = REFW + 2 * B, REFH + 2 * BY
    page_w, page_h = TRIM_W + 2 * bleed_mm, TRIM_H + 2 * bleed_mm
    css_w, css_h = page_w * 96 / 25.4, page_h * 96 / 25.4
    strips = []
    def r(x, y, w, h):
        strips.append(f"<div style='position:absolute;left:{x:.2f}px;top:{y:.2f}px;width:{w:.2f}px;"
                      f"height:{h:.2f}px;background:{TEAL}'></div>")
    O = 2.0   # strips overlap the trim by 2 ref px (0.28 mm) and sit on top, so no seam
    for a0, a1 in runs['top']:    r(B + a0, 0, a1 - a0, BY + O)
    for a0, a1 in runs['bottom']: r(B + a0, BY + REFH - O, a1 - a0, BY + O)
    for a0, a1 in runs['left']:   r(0, BY + a0, B + O, a1 - a0)
    for a0, a1 in runs['right']:  r(B + REFW - O, BY + a0, B + O, a1 - a0)
    # corners: fill when both adjoining edges are teal at that corner
    def at(edge, pos, lim): return any(x0 <= pos <= x1 for x0, x1 in runs[edge])
    if at('top', 0.5, 0) and at('left', 0.5, 0): r(0, 0, B + 1, BY + 1)
    if at('top', REFW - .5, 0) and at('right', 0.5, 0): r(B + REFW - 1, 0, B + 1, BY + 1)
    if at('bottom', 0.5, 0) and at('left', REFH - .5, 0): r(0, BY + REFH - 1, B + 1, BY + 1)
    if at('bottom', REFW - .5, 0) and at('right', REFH - .5, 0): r(B + REFW - 1, BY + REFH - 1, B + 1, BY + 1)

    head, rest = plain.split('<body>', 1)
    stage_inner = rest.split('<div id="stage">', 1)[1].rsplit('</div></div></body>', 1)[0]
    head = re.sub(r'@page\{size:[^}]*\}', f'@page{{size:{page_w}mm {page_h}mm;margin:0}}', head)
    head = re.sub(r'html,body\{width:[^;]*;height:[^;]*;', f'html,body{{width:{page_w}mm;height:{page_h}mm;', head)
    head = re.sub(r'#page\{position:relative;width:[^;]*;height:[^;]*;',
                  f'#page{{position:relative;width:{page_w}mm;height:{page_h}mm;', head)
    head = re.sub(r'#stage\{[^}]*\}',
                  f'#stage{{position:absolute;left:0;top:0;width:{PW:.2f}px;height:{PH:.2f}px;'
                  f'transform:scale({css_w/PW:.6f},{css_h/PH:.6f});transform-origin:0 0;background:#fff}}', head)
    return (head + '<body><div id="page"><div id="stage">' +
            f"<div style='position:absolute;left:{B:.2f}px;top:{BY:.2f}px;width:{REFW}px;height:{REFH}px;"
            f"overflow:hidden'>" + stage_inner + '</div>' + ''.join(strips) + '</div></div></body></html>')


if __name__ == '__main__':
    out = ROOT / 'front'
    out.mkdir(exist_ok=True)
    (out / 'front_plain.html').write_text(plain_html(), encoding='utf-8')
    print('front_plain.html written')
