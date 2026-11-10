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

# ---- honeycomb gallery (v5+): a regular honeycomb of identical pointy-top cells with an even gap,
# centred on the entrance. HC_STYLE picks the variant:
#   A  centre cell enlarged HC_FEATURE x and drawn on top of the grid; sides filled with brand tints
#   B  all cells the same size; centre marked by a thicker frame; sides filled with brand tints
#   C  as A, but the two left side cells carry the lounge and office photos
# Reference px; the top row runs past the top trim.
import math
HC_STYLE = os.environ.get('HC_STYLE', 'A')
HC_R = 134.0                                     # every grid cell
HC_GAP = 10.0
HC_FEATURE = 1.28                                # centre scale in A and C
HC_CX, HC_BOTTOM = 527.0, 628.0                  # bottom row ends ~60 px above the care title
HC_D = 3 ** 0.5 * HC_R + HC_GAP                  # centre-to-centre, same row
HC_DY = HC_D * 3 ** 0.5 / 2                      # row pitch
HC_CY = HC_BOTTOM - HC_R - HC_DY
TINT, TINT2 = '#D7E9EC', '#0A7183'


def _cell(col, row):
    """Grid position: row 0 = entrance row; odd rows are offset half a cell."""
    return HC_CX + (col + (0.5 if row % 2 else 0)) * HC_D, HC_CY + row * HC_DY


_photos = {(0, 0): 'hx_entrance', (-1, -1): 'hx_reception', (0, -1): 'hx_treatment',
           (-1, 0): 'hx_doctor', (1, 0): 'hx_equipment', (-1, 1): 'hx_waiting', (0, 1): 'hx_sterilisation'}
_side = {(-2, -1): 'tint', (-2, 0): 'tint', (2, 0): 'teal', (-2, 1): 'teal-logo', (1, 1): 'tint',
         (-3, -1): 'tint', (-3, 1): 'tint', (2, 1): 'tint', (2, -1): 'tint', (1, -1): 'tint'}
if HC_STYLE == 'C':
    _side[(-2, -1)] = 'hx_lounge'
    _side[(-2, 1)] = 'hx_office'
# (x, y, radius, kind) — kind is a photo asset name, 'tint', 'teal' or 'teal-logo'; drawn in order
HC_CELLS = [(*_cell(c, r), HC_R, k) for (c, r), k in _side.items()] + \
           [(*_cell(c, r), HC_R, k) for (c, r), k in _photos.items() if (c, r) != (0, 0)] + \
           [(*_cell(0, 0), HC_R * (1 if HC_STYLE == 'B' else HC_FEATURE), 'hx_entrance')]

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
        P.append(honeycomb(OX, OY, PW, PH))      # no corner wedge in the honeycomb layout
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
    """Photo cells: teal outline, white ring, photo clipped to the hexagon (cover crop).
    Tint cells: flat brand colour, no photo. The entrance gets a heavier frame."""
    defs, out = [], []
    mark_w = b64(A / 'zoom-logo-mark-white.svg', 'image/svg+xml')
    for i, (cx, cy, R, kind) in enumerate(HC_CELLS):
        if kind in ('tint', 'teal', 'teal-logo'):
            fill = TINT if kind == 'tint' else TINT2
            out.append(f"<polygon points='{hex_pts(cx, cy, R)}' fill='{fill}'/>")
            if kind == 'teal-logo':
                s = R * 0.95
                out.append(f"<image href='{mark_w}' x='{cx - s/2:.2f}' y='{cy - s/2:.2f}' width='{s:.2f}' height='{s:.2f}'/>")
            continue
        centre = kind == 'hx_entrance'
        ring = 11.0 if centre else 7.0
        rin = R - ring
        defs.append(f"<clipPath id='hx{i}'><polygon points='{hex_pts(cx, cy, rin)}'/></clipPath>")
        side = 2 * rin
        out.append(f"<polygon points='{hex_pts(cx, cy, R)}' fill='#fff' stroke='{TEAL}' "
                   f"stroke-width='{5 if centre else 3}'/>"
                   f"<image href='{b64(A / (kind + '.jpg'), 'image/jpeg')}' x='{cx - side/2:.2f}' "
                   f"y='{cy - side/2:.2f}' width='{side:.2f}' height='{side:.2f}' "
                   f"preserveAspectRatio='xMidYMid slice' clip-path='url(#hx{i})'/>")
    return (f"<svg style='position:absolute;left:0;top:0;overflow:visible' width='{PW:.2f}' height='{PH:.2f}'>"
            f"<defs>{''.join(defs)}</defs><g transform='translate({OX:.2f},{OY:.2f})'>"
            f"{''.join(out)}</g></svg>")


def map_svg():
    """Route map drawn from the clinic's hand sketch (two sheets, Nov 2026).

    One main street, ش عبد الرسول, runs across the card. Its west end comes down from
    the Autostrad along ش الزهراء; its east end meets the road between Carrefour
    El-Daery and El-Haramain mall. The clinic sits on the south side, opposite
    ماركت الفتح, just west of where سور الجيش begins. Two dashed routes, one from
    each end, lead to the pin. Schematic, not to scale; no north arrow (the sketch has none).
    """
    MARK_W = b64(A / 'zoom-logo-mark-white.svg', 'image/svg+xml')
    T = TEAL
    lab = f"font-family='Cairo' font-weight='700' fill='{T}' text-anchor='middle'"

    def L(x, y, t, fs=12, extra=''):
        return f"<text x='{x}' y='{y}' {lab} font-size='{fs}' {extra}>{t}</text>"

    def pill(x, y, t, w, fs=11.5):
        return (f"<rect x='{x - w/2}' y='{y - 11}' width='{w}' height='20' rx='10' fill='#fff' "
                f"stroke='{T}' stroke-width='1.6'/>" + L(x, y + 4, t, fs))

    # pin: tip on the clinic's frontage (south side of the street)
    px, py, R, tip = 222, 94, 26, 147
    k = (tip - py) / R
    pin = (f"M {px} {tip} C {px - .38*R:.1f} {py + (k - .55)*R:.1f} {px - R} {py + .8*R:.1f} "
           f"{px - R} {py} A {R} {R} 0 0 1 {px + R} {py} "
           f"C {px + R} {py + .8*R:.1f} {px + .38*R:.1f} {py + (k - .55)*R:.1f} {px} {tip} Z")

    route = f"fill='none' stroke='{T}' stroke-width='3.4' stroke-dasharray='9 6' stroke-linecap='round' stroke-linejoin='round'"
    return (f"<svg viewBox='0 0 476 216' width='476' height='216' style='display:block'>"
            f"<rect width='476' height='216' fill='#DFECEE'/>"
            # streets (white)
            f"<g fill='none' stroke='#fff' stroke-linecap='butt' stroke-linejoin='round'>"
            f"<path d='M 43 18 L 43 98 Q 43 121 66 121 L 438 121' stroke-width='26'/>"   # ش الزهراء + ش عبد الرسول
            f"<path d='M 438 -4 L 438 220' stroke-width='22'/>"                          # Carrefour - mall road
            f"<path d='M 318 -4 L 318 110' stroke-width='12'/>"                          # ش الإسراء
            f"</g>"
            # Autostrad (teal band, top-left)
            f"<rect x='-4' y='0' width='214' height='20' fill='{T}'/>"
            f"<text x='128' y='15' font-family='Cairo' font-weight='800' font-size='13' fill='#fff' text-anchor='middle'>الأوتوستراد</text>"
            # army wall
            f"<rect x='262' y='141' width='160' height='7' rx='2' fill='#9CC4CB'/>"
            # landmarks
            + L(84, 38, 'بنزينة', 11) +
            f"<rect x='78' y='50' width='78' height='26' rx='5' fill='#fff' stroke='{T}' stroke-width='1.6'/>"
            + L(117, 68, 'مسجد الزهراء', 11.5) +
            L(64, 64, 'ش الزهراء', 11, "transform='rotate(-90 64 64)'") +
            L(96, 160, 'ماركت المصطفى', 11.5) +
            L(160, 100, 'ماركت الفتح', 12.5) +
            f"<rect x='336' y='38' width='76' height='26' rx='5' fill='#fff' stroke='{T}' stroke-width='1.6'/>"
            + L(374, 56, 'مسجد المعراج', 11.5) +
            L(304, 60, 'ش الإسراء', 10.5, "transform='rotate(-90 304 60)'") +
            L(385, 99, 'كنتاكي ومؤمن', 11.5) +
            L(310, 166, 'سور الجيش', 11.5) +
            L(390, 168, 'النصر للملابس', 11) +
            pill(376, 16, 'كارفور الدائري', 84) +
            pill(380, 204, 'مول الحرمين', 74) +
            # street name, above the route line
            L(300, 120, 'ش عبد الرسول', 12.5, "fill-opacity='.9'") +
            # routes: from the Autostrad (west) and from Carrefour (east)
            f"<path d='M 43 24 L 43 98 Q 43 128 70 128 L 196 128' {route}/>"
            f"<path d='M 196 128 l -7 -4.5 l 0 9 Z' fill='{T}'/>"
            f"<path d='M 438 30 L 438 116 Q 438 128 426 128 L 250 128' {route}/>"
            f"<path d='M 248 128 l 7 -4.5 l 0 9 Z' fill='{T}'/>"
            # clinic pin
            f"<path d='{pin}' fill='{T}'/>"
            f"<image href='{MARK_W}' x='{px - 24}' y='{py - 24}' width='48' height='48'/>"
            + L(222, 172, 'عيادة زووم', 13.5, "font-weight='800'") +
            f"</svg>")


if __name__ == '__main__':
    for name, (b, m) in {'plain': (0.0, 0.0), 'bleed': (3.0, 0.0)}.items():
        (ROOT / f'back_{name}.html').write_text(build(b, m), encoding='utf-8')
    print('built')
