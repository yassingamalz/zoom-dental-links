#!/usr/bin/env python3
"""Export and verify a print-ready set: plain / bleed / press-with-crop-marks.

    from export_print import export_set, verify
    export_set(html={'plain':'flyer_plain.html','bleed':'flyer_bleed.html'},
               trim=(148,210), bleed=3, marks=5, stem='ZoomDental_Flyer_A5_v2',
               outdir='out')
    verify('out/ZoomDental_Flyer_A5_v2_PRESS_cropmarks_CMYK.pdf',
           qr_expect='https://…/?src=flyer', qr_window=(750,1045,966,1255),
           ref=(1054,1492), trim=(148,210), bleed=3, marks=5)

See reference/print-output.md. Crop marks are built as a K-only pikepdf layer because
Ghostscript converts RGB black to rich black (~291% TAC) and ReportLab writes a
non-embedded Helvetica even when no text is drawn.
"""
import subprocess, pathlib
import numpy as np
from PIL import Image

MM = 72 / 25.4
GS = ['gs', '-dBATCH', '-dNOPAUSE', '-dSAFER', '-dQUIET']


def render_pdfs(html, trim, bleed, marks, outdir):
    from playwright.sync_api import sync_playwright
    sizes = {'plain': trim,
             'bleed': (trim[0] + 2 * bleed, trim[1] + 2 * bleed)}
    out = {}
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--no-sandbox'])
        pg = br.new_page()
        for name, path in html.items():
            w, h = sizes[name]
            dst = f'{outdir}/_{name}.pdf'
            pg.goto('file://' + str(pathlib.Path(path).resolve()))
            pg.wait_for_timeout(1900)
            pg.pdf(path=dst, width=f'{w}mm', height=f'{h}mm', print_background=True,
                   prefer_css_page_size=True,
                   margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
            out[name] = dst
        br.close()
    return out


def to_cmyk(src, dst):
    subprocess.run(GS + [
        '-sDEVICE=pdfwrite', '-dProcessColorModel=/DeviceCMYK',
        '-sColorConversionStrategy=CMYK', '-dAutoFilterColorImages=false',
        '-dColorImageFilter=/FlateEncode', '-dDownsampleColorImages=false',
        '-dEmbedAllFonts=true', '-dSubsetFonts=true', '-dPDFSETTINGS=/prepress',
        f'-sOutputFile={dst}', src], check=True)
    return dst


def press_file(bleed_cmyk, dst, trim, bleed, marks, mark_len=4, mark_off=4, lw=0.25):
    """Merge the bleed artwork onto a K-only crop-mark layer."""
    import pikepdf
    from pypdf import PdfReader, PdfWriter, Transformation
    tw, th = trim[0] * MM, trim[1] * MM
    off, bl = marks * MM, bleed * MM
    pw, ph = tw + 2 * bl + 2 * off, th + 2 * bl + 2 * off
    L, R = off + bl, off + bl + tw
    B, T = off + bl, off + bl + th
    mo, ml = mark_off * MM, mark_len * MM

    ops = ['0 0 0 1 K', f'{lw} w']
    for x, sx in ((L, -1), (R, 1)):
        for y in (B, T):
            ops.append(f'{x+sx*mo:.3f} {y:.3f} m {x+sx*(mo+ml):.3f} {y:.3f} l S')
    for y, sy in ((B, -1), (T, 1)):
        for x in (L, R):
            ops.append(f'{x:.3f} {y+sy*mo:.3f} m {x:.3f} {y+sy*(mo+ml):.3f} l S')

    tmp = pikepdf.Pdf.new()
    page = tmp.add_blank_page(page_size=(pw, ph))
    page.Contents = tmp.make_stream('\n'.join(ops).encode())
    page.Resources = pikepdf.Dictionary()          # no font resource at all
    tmp.save('/tmp/_marks.pdf')

    base = PdfReader('/tmp/_marks.pdf').pages[0]
    art = PdfReader(bleed_cmyk).pages[0]
    base.merge_transformed_page(art, Transformation().translate(off, off))
    w = PdfWriter(); w.add_page(base)
    with open(dst, 'wb') as f:
        w.write(f)
    return dst


def export_set(html, trim, bleed, marks, stem, outdir='out'):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    pdfs = render_pdfs(html, trim, bleed, marks, outdir)
    out = {'plain': f'{outdir}/{stem}_plain.pdf'}
    pathlib.Path(pdfs['plain']).rename(out['plain'])
    out['bleed'] = to_cmyk(pdfs['bleed'], f'{outdir}/{stem}_bleed_CMYK.pdf')
    out['press'] = press_file(out['bleed'],
                              f'{outdir}/{stem}_PRESS_cropmarks_CMYK.pdf',
                              trim, bleed, marks)
    subprocess.run(['pdftoppm', '-png', '-r', '300', '-singlefile',
                    out['plain'], f'{outdir}/_proof'], check=True)
    Image.open(f'{outdir}/_proof.png').save(f'{outdir}/{stem}_300dpi.png', dpi=(300, 300))
    out['proof'] = f'{outdir}/{stem}_300dpi.png'
    return out


def verify(press, qr_expect=None, qr_window=None, ref=None, trim=None,
           bleed=3, marks=5, tac_limit=300):
    """qr_window is (x0,y0,x1,y1) in reference px on the trim."""
    rows = []
    info = subprocess.run(['pdfinfo', press], capture_output=True, text=True).stdout
    pages = [l for l in info.splitlines() if l.startswith('Pages')]
    size = [l for l in info.splitlines() if l.startswith('Page size')]
    rows.append(('pages / size', f'{pages[0].split()[-1]} page(s), '
                                 f'{size[0].split(":",1)[1].strip()}', '—'))

    fonts = subprocess.run(['pdffonts', press], capture_output=True, text=True).stdout
    missing = [l for l in fonts.splitlines() if 'no  no' in l]
    rows.append(('fonts embedded', 'all embedded' if not missing
                 else f'{len(missing)} NOT embedded', 'PASS' if not missing else 'FAIL'))

    subprocess.run(GS + ['-sDEVICE=tiff32nc', '-r150',
                         '-sOutputFile=/tmp/_tac.tif', press], check=True)
    a = np.array(Image.open('/tmp/_tac.tif')).astype(np.float32)
    tac = a.sum(2) / 255 * 100
    over = int((tac > tac_limit).sum())
    rows.append(('ink TAC', f'peak {tac.max():.0f}%, {over} px over {tac_limit}%',
                 'PASS' if over == 0 else 'FAIL'))

    h, w, _ = a.shape
    s = 150 / 25.4
    ph_mm = trim[1] + 2 * bleed + 2 * marks
    ok = True
    for xmm, ymm in ((2, marks + bleed), (trim[0] + 2 * bleed + 2 * marks - 2,
                                          ph_mm - marks - bleed)):
        x, y = int(xmm * s), int((ph_mm - ymm) * s)
        box = (a[max(0, y-5):y+5, max(0, x-5):x+5] / 255 * 100).reshape(-1, 4)
        px = box[np.argmax(box.sum(1))]
        ok &= bool(px[0] < 1 and px[1] < 1 and px[2] < 1 and px[3] > 95)
    rows.append(('crop marks', 'K100 only' if ok else 'NOT K-only',
                 'PASS' if ok else 'FAIL'))

    if qr_expect and qr_window and ref and trim:
        import cv2
        subprocess.run(['pdftoppm', '-png', '-r', '300', '-singlefile',
                        press, '/tmp/_press'], check=True)
        img = cv2.imread('/tmp/_press.png')
        sc = 300 / 25.4
        ox = oy = (bleed + marks) * sc
        kx, ky = trim[0] / ref[0], trim[1] / ref[1]
        x0, y0, x1, y1 = qr_window
        crop = img[int(oy + y0 * ky * sc):int(oy + y1 * ky * sc),
                   int(ox + x0 * kx * sc):int(ox + x1 * kx * sc)]
        cv2.imwrite('/tmp/_qrcrop.png', crop)   # inspect this if the decode is empty
        val, _, _ = cv2.QRCodeDetector().detectAndDecode(crop)
        rows.append(('QR decode', val or 'EMPTY -- check /tmp/_qrcrop.png first',
                     'PASS' if val == qr_expect else 'FAIL'))

    width = max(len(r[0]) for r in rows)
    for k, v, st in rows:
        print(f'{k:<{width}}  {v}   {st}')
    return rows


if __name__ == '__main__':
    print(__doc__)
