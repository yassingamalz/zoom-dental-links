#!/usr/bin/env python3
"""Zoom Dental A5 flyer — BACK side.

Coordinates are reference px on the approved comp (1054 x 1492 = 148 x 210 mm trim).
The corner wedge is the FRONT's wedge asset, flipped horizontally, so the two sides meet
through the same physical corner when the sheet is turned over side to side.
"""
import base64, json, os, pathlib
from footer_parts import footer, nudge

ROOT = pathlib.Path(__file__).resolve().parent
A, F = ROOT / 'assets', ROOT / 'fonts'
REFW, REFH = 1054.0, 1492.0
TRIM_W, TRIM_H = 148.0, 210.0
KX, KY = TRIM_W / REFW, TRIM_H / REFH
TEAL, WHITE, NAVY = '#0A7183', '#FFFFFF', '#33475A'
TAGS = os.environ.get('TAGS', '1') == '1'          # placeholder tags, proof only
HDR = os.environ.get('HDR', 'honey')               # header layout: 'honey' (v5+), or older 'shift'/'left'/'center'
HEAD_LEFT = {'left': 37.0, 'center': 141.7, 'band': 0.0, 'band2': 0.0, 'shift': 147.0, 'honey': 0.0}[HDR]  # headline ink left edge
BAND_H = 150.0                                    # teal header band height (HDR='band')
HEAD_W = 675.0                                    # headline ink width at the enlarged size
GRID_TOP = {'band': 180.0, 'band2': 180.0, 'shift': 184.0}.get(HDR, 224.0)   # photo grid top
TOP_H = 202.0 if HDR in ('left', 'center') else round((609 - GRID_TOP - 14) / 2, 1)   # top-row photo height

# ---- honeycomb gallery (v5+): pointy-top regular hexagons, all the same orientation, so every pair of
# facing edges is parallel. Three sizes: the two lateral cells (left/right) are the largest and run past
# the page edges, the four diagonal cells are the smallest, and the centre sits between them,
# HC_RC = (HC_RL + HC_RS) / 2, which makes the gap between every lateral and diagonal cell exactly HC_GAP.
# Reference px; the top row runs past the top trim.
import math
HC_RL = 215.0                                    # lateral cells (left, right)
HC_RS = 130.0                                    # diagonal cells (four)
HC_RC = (HC_RL + HC_RS) / 2                      # centre, entrance
HC_GAP = 12.0
HC_CX, HC_BOTTOM = 527.0, 660.0
_ap = lambda r: r * 3 ** 0.5 / 2                 # apothem (centre to edge)
_dist = lambda r: _ap(HC_RC) + _ap(r) + HC_GAP   # centre-to-neighbour distance
HC_CY = HC_BOTTOM - HC_RS - _dist(HC_RS) * 3 ** 0.5 / 2
# neighbour direction (deg, screen axes, y down) -> (radius, photo)
_ring = [(240, HC_RS, 'hx_reception'), (300, HC_RS, 'hx_treatment'),
         (180, HC_RL, 'hx_doctor'), (0, HC_RL, 'hx_equipment'),
         (120, HC_RS, 'hx_waiting'), (60, HC_RS, 'hx_sterilisation')]
HC_CELLS = [(HC_CX, HC_CY, HC_RC, 'hx_entrance')] + [
    (HC_CX + _dist(r) * math.cos(math.radians(a)), HC_CY + _dist(r) * math.sin(math.radians(a)), r, n)
    for a, r, n in _ring]

FS = json.load(open(ROOT / 'fs.json'))
OFF = json.load(open(ROOT / 'off.json')) if (ROOT / 'off.json').exists() else {}


def b64(p, mime):
    return f"data:{mime};base64,{base64.b64encode(pathlib.Path(p).read_bytes()).decode()}"


def png(n):
    return b64(A / n, 'image/png')


FONTS = ''.join(
    f"@font-face{{font-family:Cairo;font-weight:{w};src:url({b64(F/f'Cairo-{w}.woff2','font/woff2')}) format('woff2');}}"
    for w in (500, 600, 700, 800, 900)) + ''.join(
    f"@font-face{{font-family:Mont;font-weight:{w};src:url({b64(F/f'Mont-{w}.woff2','font/woff2')}) format('woff2');}}"
    for w in (500, 600))

MARK = b64(A / 'zoom-logo-mark.svg', 'image/svg+xml')

# front wave, shifted down 137 px to where the back's band starts
FRONT_WAVE = [(0, 914), (100, 876), (200, 859), (300, 858), (400, 870), (500, 885),
              (600, 896), (700, 893), (800, 878), (900, 850), (1000, 822), (1054, 812)]
WAVE = [(x, y + 137) for x, y in FRONT_WAVE if x <= 900] + \
       [(955, 978), (995, 958), (1018, 920), (1030, 820), (1042, 795), (1054, 782)]

ADDRESS = 'ق٧٢٠٥ المجاورة السابعة- المعراج السفلي-المعادي-القاهرة'
HANDLE = 'zoom_dental_clinic_cairo'
PHONES = ['010 9241 9234', '010 1943 3676', '011 5222 5589', '012 2447 1397']


def catmull(pts):
    p = [pts[0]] + list(pts) + [pts[-1]]
    d = f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
    return d


# ---------------------------------------------------------------- icons ------
def ico(body, size, stroke=TEAL, sw=3.2, fill='none'):
    return (f"<svg viewBox='0 0 48 48' width='{size}' height='{size}' fill='{fill}' "
            f"stroke='{stroke}' stroke-width='{sw}' stroke-linecap='round' "
            f"stroke-linejoin='round'>{body}</svg>")


ICON_SHIELD = ("<path d='M24 5 L39 10.5 V22 C39 32 32.5 39.5 24 43.5 C15.5 39.5 9 32 9 22 V10.5 Z'/>"
               "<path d='M16.5 24 L22 29.5 L31.5 19'/>")
ICON_TOOTH = ("<path d='M16 7 C10.5 7 7.5 11.5 7.5 16.5 C7.5 22.5 10.8 25.5 12 31.5 "
              "C13.2 37.5 14 42.5 17 42.5 C20.2 42.5 20.3 36.5 21.3 32.5 C22 29.6 22.9 28.3 24 28.3 "
              "C25.1 28.3 26 29.6 26.7 32.5 C27.7 36.5 27.8 42.5 31 42.5 C34 42.5 34.8 37.5 36 31.5 "
              "C37.2 25.5 40.5 22.5 40.5 16.5 C40.5 11.5 37.5 7 32 7 C28.8 7 27 9 24 9 "
              "C21 9 19.2 7 16 7 Z'/>")
ICON_SEARCH = "<circle cx='20.5' cy='20.5' r='12.5'/><path d='M29.6 29.6 L41 41' stroke-width='4.6'/>"
ICON_PERSON = "<circle cx='24' cy='15.5' r='8.5'/><path d='M8.5 42 C8.5 33 15.5 27 24 27 C32.5 27 39.5 33 39.5 42'/>"


def svg_whatsapp(size):
    return (f"<svg viewBox='0 0 32 32' width='{size}' height='{size}'>"
            f"<circle cx='16' cy='16' r='16' fill='{TEAL}'/>"
            f"<path fill='#fff' d='M16.02 6.6c-5.16 0-9.35 4.19-9.35 9.35 0 1.65.43 3.26 1.26 4.68L6.5 25.4l4.92-1.29a9.3 9.3 0 0 0 4.6 1.2h.01c5.16 0 9.35-4.19 9.35-9.35s-4.2-9.36-9.36-9.36zm0 17.15h-.01a7.77 7.77 0 0 1-3.96-1.08l-.28-.17-2.92.77.78-2.85-.19-.29a7.75 7.75 0 0 1-1.19-4.14c0-4.29 3.49-7.78 7.78-7.78 2.08 0 4.03.81 5.5 2.28a7.73 7.73 0 0 1 2.27 5.5c0 4.3-3.49 7.76-7.78 7.76zm4.27-5.82c-.23-.12-1.38-.68-1.6-.76-.21-.08-.37-.12-.52.12s-.6.76-.73.91c-.14.16-.27.18-.5.06a6.36 6.36 0 0 1-1.87-1.16 7.06 7.06 0 0 1-1.3-1.61c-.13-.23-.01-.36.1-.48.11-.11.24-.28.35-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.52-1.27-.72-1.73-.19-.46-.38-.4-.52-.4l-.45-.01c-.15 0-.4.06-.61.3-.21.23-.8.78-.8 1.91s.82 2.22.94 2.37c.12.16 1.62 2.47 3.92 3.46.55.24.97.38 1.3.48.55.18 1.05.15 1.44.09.44-.06 1.38-.56 1.57-1.1.19-.55.19-1.01.14-1.11-.06-.1-.21-.16-.44-.28z'/></svg>")


def svg_instagram(size):
    return (f"<svg viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='#fff' stroke-width='1.7'>"
            f"<rect x='2.6' y='2.6' width='18.8' height='18.8' rx='5.4'/><circle cx='12' cy='12' r='4.6'/>"
            f"<circle cx='17.4' cy='6.6' r='1.15' fill='#fff' stroke='none'/></svg>")


def svg_pin(size, col='#fff'):
    return (f"<svg viewBox='0 0 24 24' width='{size}' height='{size}'><path fill='{col}' "
            f"d='M12 2.2c-3.9 0-7.05 3.15-7.05 7.05 0 5.05 6.3 12 6.57 12.3a.64.64 0 0 0 .96 0c.27-.3 "
            f"6.57-7.25 6.57-12.3C19.05 5.35 15.9 2.2 12 2.2zm0 10.4a3.36 3.36 0 1 1 0-6.72 3.36 3.36 0 0 1 0 6.72z'/></svg>")


def build(bleed_mm=0.0, marks_mm=0.0):
    B, BY = bleed_mm / KX, bleed_mm / KY
    M, MY = marks_mm / KX, marks_mm / KY
    OX, OY = B + M, BY + MY
    PW, PH = REFW + 2 * OX, REFH + 2 * OY
    page_w = TRIM_W + 2 * bleed_mm + 2 * marks_mm
    page_h = TRIM_H + 2 * bleed_mm + 2 * marks_mm

    def X(v): return v + OX
    def Y(v): return v + OY

    def box(x, y, w=None, h=None, extra=''):
        s = f"position:absolute;left:{X(x):.2f}px;top:{Y(y):.2f}px;"
        if w is not None: s += f"width:{w:.2f}px;"
        if h is not None: s += f"height:{h:.2f}px;"
        return s + extra

    def text(id_, x, y, txt, fam, wt, size, col, align='c', rtl=True, ls=None):
        """Anchor x is the centre (c), right edge (r) or left edge (l) of the line."""
        dx, dy = OFF.get(id_, (0.0, 0.0))
        tx = {'c': '-50%', 'r': '-100%', 'l': '0'}[align]
        return (f"<div id='{id_}' style='{box(x + dx, y + dy)}transform:translateX({tx});"
                f"white-space:nowrap;font-family:{fam};font-weight:{wt};font-size:{size:.2f}px;"
                f"line-height:{size*1.25:.2f}px;color:{col};{'direction:rtl;' if rtl else ''}"
                f"{f'letter-spacing:{ls}px;' if ls else ''}'>{txt}</div>")

    def tag(x, y, label='PLACEHOLDER'):
        if not TAGS:
            return ''
        return (f"<div style='{box(x, y)}background:{NAVY};color:#fff;font-family:Mont;font-weight:600;"
                f"font-size:11px;letter-spacing:1px;padding:3px 8px;border-radius:4px;z-index:9'>{label}</div>")

    P = [f"<div style='position:absolute;inset:0;background:{WHITE}'></div>"]

    # --- corner wedge: the front's asset, mirrored, anchored to the top-right page corner
    if HDR == 'band2':
        # --- teal band, headline right-aligned to the grid, white sparkles on the left
        P.append(f"<div style='position:absolute;left:0;top:0;width:{PW:.2f}px;height:{Y(BAND_H):.2f}px;"
                 f"background:{TEAL}'></div>")
        # white sparkles at the headline's left end, front orientation
        P.append(f"<img src='{png('sparkles_white.png')}' style='{box(1017 - HEAD_W - 26 - 88, 22, 88, 72)}'>")
        P.append(text('head', 1017, 0, 'اتعرّف على عيادتنا', 'Cairo', 900, FS['head'], WHITE, 'r'))
    elif HDR == 'band':
        # --- header as a full-bleed teal band, white headline flanked by thin rules
        P.append(f"<div style='position:absolute;left:0;top:0;width:{PW:.2f}px;height:{Y(BAND_H):.2f}px;"
                 f"background:{TEAL}'></div>")
        for x in (527 - HEAD_W / 2 - 24 - 92, 527 + HEAD_W / 2 + 24):
            P.append(f"<div style='{box(x, BAND_H / 2 - 1.5, 92, 3)}background:#fff;border-radius:2px'></div>")
        P.append(text('head', 527, 0, 'اتعرّف على عيادتنا', 'Cairo', 900, FS['head'], WHITE, 'c'))
    elif HDR == 'honey':
        P.append(f"<img src='{png('wedge.png')}' style='{box(REFW - 399, -OY - 3, 402 + OX, 309 + OY)}"
                 f"transform:scaleX(-1)'>")
        P.append(honeycomb(OX, OY, PW, PH))
    else:
        P.append(f"<img src='{png('wedge.png')}' style='{box(REFW - 399, -OY - 3, 402 + OX, 309 + OY)}"
                 f"transform:scaleX(-1)'>")
        if HDR == 'shift':   # sparkles at the headline's left end, front orientation
            P.append(f"<img src='{png('sparkles.png')}' style='{box(HEAD_LEFT - 104, 22, 98, 80)}'>")
        else:
            P.append(f"<img src='{png('sparkles.png')}' style='{box(HEAD_LEFT + HEAD_W + 6, 30, 98, 80)}transform:scaleX(-1)'>")
        P.append(text('head', 689, 0, 'اتعرّف على عيادتنا', 'Cairo', 900, FS['head'], TEAL, 'r'))

    # --- photo grid (older header layouts only)
    G = GRID_TOP
    if HDR == 'honey':
        photos, pills = [], []
    else:
        photos = None
    photos = photos if photos is not None else [('ph_large', 37, G, 476, 609 - G), ('ph_tmid', 527, G, 246, TOP_H),
              ('ph_tright', 787, G, 230, TOP_H), ('ph_bwide', 527, G + TOP_H + 14, 490, 609 - G - TOP_H - 14)]
    for n, x, y, w, h in photos:
        P.append(f"<div style='{box(x, y, w, h)}border-radius:22px;overflow:hidden;"
                 f"background:url({png(n + '.png')}) center/cover no-repeat'></div>")
        P.append(tag(x + 14, y + 12))
    pills = pills if HDR == 'honey' else [('pl', 139, 566, 242, 42, 'منطقة الاستقبال', FS['pl']),
             ('pm', 533, GRID_TOP + TOP_H - 34, 178, 34, 'غرفة العلاج', FS['psm']),
             ('pr', 795, GRID_TOP + TOP_H - 34, 190, 34, 'أحدث الأجهزة', FS['psm']),
             ('pb', 541, 572, 186, 37, 'تعقيم الأدوات', FS['psm'])]
    for id_, x, y, w, h, t, s in pills:
        P.append(f"<div style='{box(x, y, w, h)}background:{TEAL};border-radius:{h/2:.1f}px'></div>")
        P.append(text(id_, x + w / 2, y + h / 2 - s * 0.66, t, 'Cairo', 700, s, WHITE, 'c'))

    # --- divider with centre notch
    dv = (f"M {X(39):.2f} {Y(632):.2f} L {X(505):.2f} {Y(632):.2f} L {X(521.5):.2f} {Y(646):.2f}"
          f" L {X(538):.2f} {Y(632):.2f} L {X(1014):.2f} {Y(632):.2f}")
    if HDR != 'honey':
        P.append(f"<svg style='position:absolute;left:0;top:0' width='{PW:.2f}' height='{PH:.2f}'>"
                 f"<path d='{dv}' fill='none' stroke='{TEAL}' stroke-width='3.2' stroke-linejoin='round' "
                 f"stroke-linecap='round'/></svg>")

    # --- care section
    P.append(f"<img src='{png('sparkles.png')}' style='{box(45, 660, 50, 41)}'>")
    P.append(text('title', 689, 0, ('رعاية دقيقة بالتقنيات الحديثة' if HDR == 'honey' else 'رعاية دقيقة وتقنيات حديثة'), 'Cairo', 900, FS['title'] * (0.905 if HDR == 'honey' else 1), TEAL, 'r'))
    P.append(text('para1', 374, 0, 'نحرص على راحتك واهتمامك، ونستخدم التقنيات المناسبة',
                  'Cairo', 500, FS['para'], TEAL, 'c'))
    P.append(text('para2', 382.5, 0, 'لتشخيص دقيق وخطة علاج تناسب احتياجاتك.',
                  'Cairo', 500, FS['para'], TEAL, 'c'))
    cols = [(94, ICON_SHIELD, 'تعقيم', 'وأمان'), (254, ICON_TOOTH, 'خطة علاج', 'مناسبة ليك'),
            (418, ICON_SEARCH, 'تشخيص دقيق', 'ومبكر'), (594.5, ICON_PERSON, 'راحة واهتمام', 'بكل تفصيلة')]
    D = 103.0
    for i, (cx, body, l1, l2) in enumerate(cols):
        P.append(f"<div style='{box(cx - D/2, 822, D, D)}border:2.6px solid {TEAL};border-radius:50%;"
                 f"box-sizing:border-box'></div>")
        P.append(f"<div style='{box(cx - 34, 873.5 - 34, 68, 68)}'>{ico(body, 68, sw=3.3)}</div>")
        P.append(text(f'lab{i}a', cx, 0, l1, 'Cairo', 800, FS['lab'], TEAL, 'c'))
        P.append(text(f'lab{i}b', cx, 0, l2, 'Cairo', 800, FS['lab'], TEAL, 'c'))
    for x in (175, 335, 508):
        P.append(f"<div style='{box(x - 1, 843, 2, 140)}background:{TEAL};opacity:.45'></div>")
    P.append(f"<div style='{box(709, 663, 308, 324)}border-radius:22px 22px 56px 22px;overflow:hidden;"
             f"background:url({png('ph_scan.png')}) center/cover no-repeat'></div>")
    P.append(tag(723, 675))

    # --- location band (front wave shape), spans the full sheet incl. bleed
    wpts = [(x / REFW * PW, Y(y)) for x, y in WAVE]
    band = f"{catmull(wpts)} L {PW:.2f} {PH:.2f} L 0 {PH:.2f} Z"
    P.append(f"<svg style='position:absolute;left:0;top:0' width='{PW:.2f}' height='{PH:.2f}'>"
             f"<path d='{band}' fill='{TEAL}'/></svg>")

    bp = nudge('bpin')
    P.append(f"<div style='{box(151, 1031, 58, 58)}'><div id='bpin' style='{bp}'>{svg_pin(58)}</div></div>")
    P.append(text('band', 451, 0, 'إزاي توصلنا؟', 'Cairo', 900, FS['band'], WHITE, 'r'))

    # map card — schematic placeholder until the real location is drawn
    P.append(f"<div style='{box(51, 1095, 476, 216)}background:#fff;border-radius:18px;overflow:hidden'>"
             f"{map_svg()}</div>")
    P.append(tag(372, 1105, 'MAP PLACEHOLDER'))

    P.append(f"<div style='{box(545, 1067, 2, 243)}background:#fff;opacity:.55'></div>")

    # QR card
    P.append(f"<div style='{box(576, 1060, 221, 251)}border:2.4px dashed rgba(255,255,255,.85);"
             f"border-radius:20px;box-sizing:border-box'></div>")
    P.append(text('qr1', 686, 0, 'امسح الكود للوصول إلينا', 'Cairo', 600, FS['qr'], WHITE, 'c'))
    P.append(text('qr2', 686, 0, 'على Google Maps', 'Cairo', 600, FS['qr'], WHITE, 'c'))
    P.append(f"<div style='{box(606, 1134, 160, 158)}background:#fff;border-radius:9px;"
             f"display:flex;align-items:center;justify-content:center'>"
             f"<div style='width:126px;height:126px;border:2px dashed {TEAL};border-radius:6px;"
             f"display:flex;align-items:center;justify-content:center;text-align:center;"
             f"font-family:Mont;font-weight:600;font-size:13px;line-height:18px;color:{TEAL}'>"
             f"QR<br>Google Maps<br>link needed</div></div>")

    # right column (draft 1 structure): small pin + dot, dashed S-route, big pin, ticks, text, swoosh
    def pin_path(cx, top, tip, R):
        cy = top + R; k = (tip - cy) / R
        return (f"M {cx:.1f} {tip:.1f} C {cx - .38*R:.1f} {cy + (k - .55)*R:.1f} {cx - R:.1f} {cy + .8*R:.1f} "
                f"{cx - R:.1f} {cy:.1f} A {R:.1f} {R:.1f} 0 0 1 {cx + R:.1f} {cy:.1f} "
                f"C {cx + R:.1f} {cy + .8*R:.1f} {cx + .38*R:.1f} {cy + (k - .55)*R:.1f} {cx:.1f} {tip:.1f} Z")
    sv = [f"<path d='{pin_path(859, 1114, 1162, 18.5)}'/>",
          "<circle cx='859' cy='1132' r='8.2'/>",
          "<circle cx='859' cy='1176' r='6' fill='#fff' stroke='none'/>",
          "<path d='M 870 1185 C 892 1192 909 1183 907 1167 C 905 1153 893 1151 896 1141 "
          "C 899 1132 912 1129 927 1130' stroke-dasharray='9 7' stroke-width='3.4'/>",
          f"<path d='{pin_path(961, 1091, 1160, 25)}'/>",
          "<circle cx='961' cy='1116' r='11'/>",
          "<path d='M 972 1183 L 970 1201 M 996 1183 L 986 1203' stroke-width='4.4'/>"]
    P.append(f"<svg style='position:absolute;left:0;top:0;overflow:visible' width='{PW:.2f}' height='{PH:.2f}'>"
             f"<g transform='translate({OX:.2f},{OY:.2f})' fill='none' stroke='#fff' stroke-width='3.6' "
             f"stroke-linecap='round' stroke-linejoin='round'>{''.join(sv)}</g></svg>")
    P.append(text('wait', 920, 0, 'مستنيين زيارتك', 'Cairo', 900, FS['wait'], WHITE, 'c'))
    P.append(f"<svg style='{box(846, 1266, 148, 26)}' viewBox='0 0 148 26'>"
             f"<path d='M 2 24 C 42 10 96 3 146 2 C 98 8 46 16 5 26 Z' fill='#fff'/></svg>")

    # --- phone pill + social row + address: shared module, identical on both sides
    P.extend(footer(box))

    body = '\n'.join(p for p in P if p)
    css_w, css_h = page_w * 96 / 25.4, page_h * 96 / 25.4
    sx, sy = css_w / PW, css_h / PH
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS}
@page{{size:{page_w}mm {page_h}mm;margin:0}}
*{{margin:0;padding:0;box-sizing:content-box}}
html,body{{width:{page_w}mm;height:{page_h}mm;background:#fff;overflow:hidden;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
#page{{position:relative;width:{page_w}mm;height:{page_h}mm;overflow:hidden;background:#fff;
  page-break-inside:avoid;break-inside:avoid}}
#stage{{position:absolute;left:0;top:0;width:{PW:.2f}px;height:{PH:.2f}px;
  transform:scale({sx:.6f},{sy:.6f});transform-origin:0 0;background:#fff}}
img{{display:block}}
</style></head><body><div id="page"><div id="stage">{body}</div></div></body></html>"""


def hex_pts(cx, cy, r):
    import math
    return ' '.join(f"{cx + r * math.cos(math.radians(a)):.2f},{cy + r * math.sin(math.radians(a)):.2f}"
                    for a in (-90, -30, 30, 90, 150, 210))


def honeycomb(OX, OY, PW, PH):
    """Photo cells: teal outline, thin white ring, photo clipped to the hexagon (cover crop).
    Decorative cells: pale teal tint with a teal outline, drawn first so photos sit on top."""
    defs, deco, cells = [], [], []
    for i, (cx, cy, R, asset) in enumerate(HC_CELLS):
        rin = R - 7.0                                 # photo hexagon inside the white ring
        if asset is None:
            deco.append(f"<polygon points='{hex_pts(cx, cy, R)}' fill='none' "
                        f"stroke='{TEAL}' stroke-width='2.4' stroke-opacity='.35'/>")
            continue
        defs.append(f"<clipPath id='hx{i}'><polygon points='{hex_pts(cx, cy, rin)}'/></clipPath>")
        side = 2 * rin
        cells.append(f"<polygon points='{hex_pts(cx, cy, R)}' fill='#fff' stroke='{TEAL}' stroke-width='3'/>"
                     f"<image href='{b64(A / (asset + '.jpg'), 'image/jpeg')}' x='{cx - side/2:.2f}' "
                     f"y='{cy - side/2:.2f}' width='{side:.2f}' height='{side:.2f}' "
                     f"preserveAspectRatio='xMidYMid slice' clip-path='url(#hx{i})'/>")
    return (f"<svg style='position:absolute;left:0;top:0;overflow:visible' width='{PW:.2f}' height='{PH:.2f}'>"
            f"<defs>{''.join(defs)}</defs><g transform='translate({OX:.2f},{OY:.2f})'>"
            f"{''.join(deco)}{''.join(cells)}</g></svg>")


def map_svg():
    """Schematic map in draft 1's structure: tinted blocks with white streets, teal main
    road, dashed route ending at a teal pin with the white mark. Placeholder geometry."""
    t = 'rgba(10,113,131,'
    MARK_W = b64(A / 'zoom-logo-mark-white.svg', 'image/svg+xml')
    streets = ''.join(f"<path d='{d}'/>" for d in [
        'M -10 150 L 486 68', 'M -10 214 L 486 132',
        'M 70 0 L 92 216', 'M 150 36 L 168 216', 'M 246 20 L 256 216',
        'M 336 0 L 350 216', 'M 420 0 L 438 216', 'M -10 168 L 300 232',
        'M 20 0 L 40 216', 'M 196 30 L 210 216', 'M 292 10 L 304 216', 'M 380 0 L 392 216',
        'M -10 120 L 120 98', 'M 300 112 L 486 82', 'M 240 186 L 486 160'])
    parks = (f"<rect x='340' y='128' width='50' height='46' rx='4' fill='#C4DDE1'/>"
             f"<rect x='428' y='62' width='44' height='30' rx='4' fill='#C4DDE1'/>"
             f"<rect x='12' y='136' width='34' height='20' rx='4' fill='#C4DDE1'/>")
    pin_cx, pin_cy, R, tip = 282, 92, 32, 156
    k = (tip - pin_cy) / R
    pin = (f"M {pin_cx} {tip} C {pin_cx - .38*R:.1f} {pin_cy + (k - .55)*R:.1f} {pin_cx - R} {pin_cy + .8*R:.1f} "
           f"{pin_cx - R} {pin_cy} A {R} {R} 0 0 1 {pin_cx + R} {pin_cy} "
           f"C {pin_cx + R} {pin_cy + .8*R:.1f} {pin_cx + .38*R:.1f} {pin_cy + (k - .55)*R:.1f} {pin_cx} {tip} Z")
    lab = f"font-family='Cairo' font-weight='800' font-size='15' fill='{TEAL}' text-anchor='middle'"
    return (f"<svg viewBox='0 0 476 216' width='476' height='216' style='display:block'>"
            f"<rect width='476' height='216' fill='#DFECEE'/>"
            f"<g stroke='#fff' stroke-width='9' stroke-linecap='round' fill='none'>{streets}</g>"
            f"{parks}"
            f"<path d='M -10 72 L 486 -10 L 486 14 L -10 96 Z' fill='{TEAL}'/>"
            f"<text x='222' y='46' font-family='Cairo' font-weight='800' font-size='17' fill='#fff' "
            f"text-anchor='middle' transform='rotate(-9.4 222 46)'>الطريق الرئيسي</text>"
            f"<path d='M 110 66 L 82 71 M 82 71 L 89 65.5 M 82 71 L 90 75' stroke='#fff' stroke-width='2.4' "
            f"fill='none' stroke-linecap='round' stroke-linejoin='round'/>"
            f"<path d='M 199 60 L 195 67 L 161 76 L 185 140 L 228 124 L 280 182 L 296 176 L 291 160' "
            f"fill='none' stroke='{TEAL}' stroke-width='4.2' stroke-dasharray='11 7' stroke-linejoin='round'/>"
            f"<path d='{pin}' fill='{TEAL}'/>"
            f"<image href='{MARK_W}' x='{pin_cx - 32}' y='{pin_cy - 32}' width='64' height='64'/>"
            f"<path d='M 26 12 L 34 33 L 26 28 L 18 33 Z' fill='{TEAL}'/>"
            f"<text x='26' y='52' font-family='Mont' font-weight='600' font-size='14' fill='{TEAL}' text-anchor='middle'>N</text>"
            f"<g transform='translate(78,116)' stroke='{TEAL}' stroke-width='2.6' fill='none' "
            f"stroke-linejoin='round' stroke-linecap='round'>"
            f"<rect x='-13' y='-6' width='26' height='24' rx='3'/><path d='M -6 -6 C -6 -16 6 -16 6 -6'/>"
            f"<path d='M -5 5 C -2 9 2 9 5 5'/></g>"
            f"<text x='78' y='160' {lab}>منطقة قريبة</text>"
            f"<text x='78' y='181' {lab}>معروفة</text>"
            f"<text x='190' y='198' {lab} transform='rotate(9 190 198)'>المعراج السفلي</text>"
            f"<text x='372' y='202' {lab}>المجاورة السابعة</text>"
            f"</svg>")


if __name__ == '__main__':
    for name, (b, m) in {'plain': (0.0, 0.0), 'bleed': (3.0, 0.0)}.items():
        (ROOT / f'back_{name}.html').write_text(build(b, m), encoding='utf-8')
    print('built')
