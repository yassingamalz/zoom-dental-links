#!/usr/bin/env python3
"""Solve font sizes and letter-spacing so rendered ink matches measured targets.

Two entry points:

  isolated_metrics(font_files, items)
      Render each string alone at 100 px and return its ink width and height.
      This is the reliable route -- no contamination from neighbouring elements.
      Use it to derive font sizes directly:  fs = target_w / (ink_w_at_100 / 100)

  solve_tracking(html_path, element_id, target_w, scale, build_fn)
      Two-point linear solve for letter-spacing against a live page.

Read reference/calibrating.md first. The two mistakes that waste the most time are
measuring wrapped text (always set white-space:nowrap) and mixing DOM range widths
(n tracking slots) with ink bounding boxes (n-1 gaps).
"""
import base64
import pathlib
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


def _face(path, family, weight=400):
    b64 = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    fmt = 'woff2' if str(path).endswith('.woff2') else 'truetype'
    return (f"@font-face{{font-family:{family};font-weight:{weight};"
            f"src:url(data:font/{fmt};base64,{b64}) format('{fmt}');}}")


def isolated_metrics(faces, items, size=100, out='/tmp/_cal.png'):
    """faces: [(path, family, weight)].  items: [(id, family, weight, text, rtl)].

    Returns {id: {'w': ink_width, 'h': ink_height, 'range_w': dom_width}} at `size` px.
    """
    css = ''.join(_face(p, f, w) for p, f, w in faces)
    rows = ''.join(
        f"<div style=\"margin:0;padding:30px 0\"><span id='{i}' style=\""
        f"font-family:{fam};font-weight:{w};font-size:{size}px;"
        f"{'direction:rtl;' if rtl else ''}white-space:nowrap;"
        f"display:inline-block;color:#000\">{t}</span></div>"
        for i, fam, w, t, rtl in items)
    html = (f"<!doctype html><meta charset=utf-8><style>{css}"
            f"body{{margin:0;background:#fff}}</style>{rows}")
    pathlib.Path('/tmp/_cal.html').write_text(html, encoding='utf-8')

    with sync_playwright() as p:
        br = p.chromium.launch(args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': 2600, 'height': 260 * len(items)})
        pg.goto('file:///tmp/_cal.html')
        pg.wait_for_timeout(1400)
        boxes = pg.evaluate(
            """(ids)=>{const o={};for(const id of ids){const e=document.getElementById(id);
               const r=document.createRange();r.selectNodeContents(e);
               const b=r.getBoundingClientRect();o[id]=[b.width,b.top,b.bottom];}return o}""",
            [i for i, *_ in items])
        pg.screenshot(path=out, full_page=True)
        br.close()

    a = np.array(Image.open(out).convert('L'))
    dark = a < 128
    res = {}
    for i, *_ in items:
        w_dom, top, bot = boxes[i]
        band = dark[max(0, int(top) - 6):int(bot) + 6]
        ys, xs = np.where(band.any(1))[0], np.where(band.any(0))[0]
        res[i] = {'w': int(xs.max() - xs.min() + 1) if len(xs) else 0,
                  'h': int(ys.max() - ys.min() + 1) if len(ys) else 0,
                  'range_w': w_dom}
    return res


def size_for_width(metric, target_w, probe=100):
    """fs that renders `metric['w']` (measured at `probe` px) at `target_w`."""
    return round(target_w / (metric['w'] / probe), 3)


def size_for_height(metric, target_h, probe=100):
    """fs that renders `metric['h']` (measured at `probe` px) at `target_h`.

    Use this for LETTERSPACED text (wordmarks): size from ink height first, then solve
    tracking for width. Sizing a tracked block from width instead folds the tracking into
    the glyphs and comes out too large -- e.g. ZOOM solves to 97 px from width but 87 px
    from height, and 87 + 9.8 px tracking is the correct answer.
    """
    return round(target_h / (metric['h'] / probe), 3)


def solve_tracking(build_fn, measure_fn, target_w, set_ls, probes=(0.0, 10.0)):
    """Linear two-point solve. `measure_fn` must return the SAME basis as `target_w`
    (both ink widths, or both DOM range widths -- never one of each)."""
    w = {}
    for pr in probes:
        set_ls(pr)
        build_fn()
        w[pr] = measure_fn()
    lo, hi = probes
    slope = (w[hi] - w[lo]) / (hi - lo)
    if abs(slope) < 1e-9:
        raise RuntimeError('tracking has no effect on the measurement -- wrong element?')
    return round((target_w - w[lo]) / slope, 3)


def check_convergence(history, label=''):
    """Raise if error is growing -- that means a contaminated measurement window."""
    if len(history) >= 3 and history[-1] > history[-2] > history[-3]:
        raise RuntimeError(
            f'{label}: error growing ({history[-3]:.3f} -> {history[-2]:.3f} -> '
            f'{history[-1]:.3f}). The measurement window is contaminated by a '
            f'neighbouring element. Re-measure in isolation instead of iterating.')


if __name__ == '__main__':
    print(__doc__)
