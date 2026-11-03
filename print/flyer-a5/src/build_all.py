#!/usr/bin/env python3
"""Rebuild the A5 flyer, front and back, from source.

    python3 build_all.py                 # front press set + back proof + 2-page approval PDF
    python3 build_all.py --back-press    # also the back press set (only once real photos,
                                         # map and QR are in place, see README)

Outputs go to ../out/ (not committed). Copy a verified set into ../release/<version>/.
"""
import argparse, json, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / 'out'
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'skill_scripts'))

TRIM, BLEED, MARKS = (148, 210), 3, 5
QR_FRONT = 'https://zoom-dental-links.zoomdentalcliniccairo.workers.dev/?src=flyer'


def pdf(html, dst, w, h):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--no-sandbox']); pg = br.new_page()
        pg.goto('file://' + str(html)); pg.wait_for_timeout(2000)
        pg.pdf(path=str(dst), width=f'{w}mm', height=f'{h}mm', print_background=True,
               prefer_css_page_size=True, margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
        br.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--front-version', default='v6')
    ap.add_argument('--back-version', default='v4')
    ap.add_argument('--back-press', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    from export_print import export_set, verify
    from front_v3 import bleed_html, edge_runs
    import front_services

    # ---- front: services list from service_lists.json (first entry) --------------------
    name, items = next(iter(json.loads((ROOT / 'service_lists.json').read_text()).items()))
    plain = front_services.make(items, name)
    trim_pdf = OUT / '_front_trim.pdf'
    pdf(plain, trim_pdf, *TRIM)
    subprocess.run(['pdftoppm', '-png', '-r', '300', '-singlefile', str(trim_pdf), str(OUT / '_front_trim')], check=True)
    bleed = plain.parent / 'front_bleed.html'
    bleed.write_text(bleed_html(plain.read_text(encoding='utf-8'), edge_runs(OUT / '_front_trim.png')), encoding='utf-8')
    fstem = f'ZoomDental_Flyer_A5_{a.front_version}'
    fo = export_set(html={'plain': str(plain), 'bleed': str(bleed)}, trim=TRIM, bleed=BLEED, marks=MARKS,
                    stem=fstem, outdir=str(OUT))
    print('\nFRONT', fstem)
    verify(fo['press'], qr_expect=QR_FRONT, qr_window=(750, 1045, 966, 1255), ref=(1054, 1492),
           trim=TRIM, bleed=BLEED, marks=MARKS)

    # ---- back ---------------------------------------------------------------------------
    subprocess.run([sys.executable, str(ROOT / 'build_back.py')], check=True)
    bstem = f'ZoomDental_Flyer_A5_BACK_{a.back_version}'
    if a.back_press:
        bo = export_set(html={'plain': str(ROOT / 'back_plain.html'), 'bleed': str(ROOT / 'back_bleed.html')},
                        trim=TRIM, bleed=BLEED, marks=MARKS, stem=bstem, outdir=str(OUT))
        print('\nBACK', bstem)
        verify(bo['press'], trim=TRIM, bleed=BLEED, marks=MARKS)   # add qr_expect once the Maps QR exists
        back_plain = bo['plain']
    else:
        back_plain = OUT / f'{bstem}_PROOF.pdf'
        pdf(ROOT / 'back_plain.html', back_plain, *TRIM)
        print('\nBACK proof only:', back_plain.name, '(placeholders: photos, map, QR)')

    # ---- 2-page approval PDF -------------------------------------------------------------
    from pypdf import PdfWriter
    w = PdfWriter()
    for f in (fo['plain'], back_plain):
        w.append(str(f))
    pair = OUT / 'Zoom_Dental_Flyer_A5_Front_Back.pdf'
    with open(pair, 'wb') as fh:
        w.write(fh)
    print('\napproval PDF:', pair.name)


if __name__ == '__main__':
    main()
