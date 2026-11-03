#!/usr/bin/env python3
"""Front v4: replace the 6-line services list with a longer one, fitted into the same column.

The column keeps its x position, its check bullets and its divider. What changes:
the heading moves up a little, the list runs from just under the heading to just above
the phone pill, and the row pitch and font size are solved from the number of lines and
the longest line, so the column never gets wider.
"""
import json, pathlib, subprocess, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'skill_scripts'))
from front_v3 import plain_html, bleed_html, edge_runs
from calibrate import isolated_metrics

TEXT_X, TEXT_MAX_W = 114.0, 252.0       # text left edge; must stay clear of the divider at x 379
CHECK_X = 76.0
LIST_TOP, LIST_BOTTOM = 958.0, 1308.0   # pill starts at 1329
HEAD_DY = -12.0                         # heading block moves up this much
FS_MAX = 24.83                          # never larger than the v3 list
CHECK = (ROOT / 'check.svg').read_text()


def solve(items):
    m = isolated_metrics([(str(ROOT / 'fonts/Cairo-600.woff2'), 'Cairo', 600)],
                         [(f's{i}', 'Cairo', 600, t, True) for i, t in enumerate(items)])
    widest = max(v['w'] for v in m.values())
    pitch = (LIST_BOTTOM - LIST_TOP) / len(items)
    fs = min(FS_MAX, TEXT_MAX_W / (widest / 100), pitch * 0.70)
    return round(fs, 2), pitch, widest


def block(items, fs, pitch, check_dy=None):
    check_dy = check_dy or [0.0] * len(items)
    cs = round(min(25.0, fs * 1.0), 1)          # check scales with the text
    lh = fs * 1.69
    out = []
    for i, t in enumerate(items):
        cy = LIST_TOP + pitch * (i + 0.5)
        svg = CHECK.replace("width='25' height='25'", f"width='{cs}' height='{cs}'")
        out.append(f"<div id='chk{i}' style='position:absolute;left:{CHECK_X:.2f}px;"
                   f"top:{cy - cs/2 + check_dy[i]:.2f}px;width:{cs}px;height:{cs}px;'>{svg}</div>")
        out.append(f"<div style='position:absolute;left:{TEXT_X:.2f}px;top:{cy - lh/2:.2f}px;width:300px;"
                   f"text-align:left;direction:rtl;font-family:Cairo;font-weight:600;font-size:{fs}px;"
                   f"line-height:{lh:.2f}px;color:#FFFFFF;white-space:nowrap'>"
                   f"<span id='svc{i}'>{t}</span></div>")
    return '\n'.join(out)


def build_html(items, fs, pitch, check_dy=None):
    s = plain_html()
    # heading block: two rules + the heading, shifted up
    for old in ("left:75.00px;top:939.50px", "left:270.00px;top:939.50px"):
        assert s.count(old) == 1
        s = s.replace(old, old.replace('939.50', f'{939.5 + HEAD_DY:.2f}'))
    old = "left:155.00px;top:911.00px"
    assert s.count(old) == 1
    s = s.replace(old, f"left:155.00px;top:{911 + HEAD_DY:.2f}px")
    # list
    st = s.find("left:76.00px;top:981.00px"); st = s.rfind("<div", 0, st)
    j = s.find("id='svc5'"); en = s.find("</div>", j) + len("</div>")
    assert 0 < st < en
    s = s[:st] + block(items, fs, pitch, check_dy) + s[en:]
    # divider follows the list
    old = "left:379.00px;top:960.00px;width:2.00px;height:330.00px"
    assert s.count(old) == 1
    s = s.replace(old, f"left:379.00px;top:{LIST_TOP:.2f}px;width:2.00px;height:{LIST_BOTTOM - LIST_TOP:.2f}px")
    return s


def centres(html_path, n):
    """Ink centre of each check and the body centre of each line, measured in isolation."""
    from align_icons import ink_boxes
    ids = [f'chk{i}' for i in range(n)] + [f'svc{i}' for i in range(n)]
    b = ink_boxes(html_path, ids)
    return ([(b[f'chk{i}'][1] + b[f'chk{i}'][3]) / 2 for i in range(n)],
            [b[f'svc{i}'][4] for i in range(n)], b)


def make(items, name):
    fs, pitch, widest = solve(items)
    out = ROOT / 'front' / name
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'front_plain.html'
    p.write_text(build_html(items, fs, pitch), encoding='utf-8')
    ck, tx, _ = centres(p, len(items))
    dy = [t - c for c, t in zip(ck, tx)]
    p.write_text(build_html(items, fs, pitch, dy), encoding='utf-8')
    ck, tx, b = centres(p, len(items))
    right = max(b[f'svc{i}'][2] for i in range(len(items)))
    print(f'{name}: {len(items)} lines  font {fs}px (= {fs * 148 / 1054 / 0.3528:.1f} pt)  pitch {pitch:.1f}px  '
          f'widest line ends at x {right:.0f} (divider 379)  check offset max {max(abs(t - c) for c, t in zip(ck, tx)):.2f}px')
    return p


if __name__ == '__main__':
    lists = json.loads((ROOT / 'service_lists.json').read_text())
    for name, items in lists.items():
        make(items, name)
