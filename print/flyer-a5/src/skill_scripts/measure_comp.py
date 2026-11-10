#!/usr/bin/env python3
"""Measure a reference comp: ink boxes, row/column runs, colours, curve edges.

All coordinates are in the comp's own pixel space ("reference px").

  --sample X,Y ...            print RGB at points
  --bbox X0 Y0 X1 Y1          ink bbox inside a window
  --rows Y0 Y1                row runs (gap analysis) -- use this to find clean bands
  --cols Y0 Y1                column runs (per-glyph widths)
  --curve Y0 Y1               top edge of a filled shape, sampled across x
  --xband X0 X1               x limits for --rows / --cols / --curve
  --mask ink|white|teal       which population to measure (default ink)

Row runs are the safest primitive: they show the gaps that prove a window is clean.
See reference/measuring.md for the contamination trap this exists to avoid.
"""
import argparse
import numpy as np
from PIL import Image


def masks(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return {
        'ink':   (r < 200) & (b > 60),                                    # teal type on light
        'white': (r > 200) & (g > 200) & (b > 200),                       # white type on teal
        'teal':  (r < 70) & (g > 70) & (g < 150) & (b > 80) & (b < 170),  # brand fills
    }


def runs(flags, offset, minlen=1):
    out, start = [], None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= minlen:
                out.append((offset + start, offset + i - 1))
            start = None
    if start is not None:
        out.append((offset + start, offset + len(flags) - 1))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('image')
    p.add_argument('--mask', default='ink', choices=['ink', 'white', 'teal'])
    p.add_argument('--sample', nargs='*', default=[])
    p.add_argument('--bbox', nargs=4, type=int, metavar=('X0', 'Y0', 'X1', 'Y1'))
    p.add_argument('--rows', nargs=2, type=int, metavar=('Y0', 'Y1'))
    p.add_argument('--cols', nargs=2, type=int, metavar=('Y0', 'Y1'))
    p.add_argument('--curve', nargs=2, type=int, metavar=('Y0', 'Y1'))
    p.add_argument('--xband', nargs=2, type=int, default=None)
    p.add_argument('--minlen', type=int, default=3)
    args = p.parse_args()

    im = Image.open(args.image).convert('RGB')
    a = np.array(im).astype(int)
    H, W, _ = a.shape
    m = masks(a)[args.mask]
    x0, x1 = args.xband if args.xband else (0, W)
    print(f'# {args.image}  {W} x {H}  mask={args.mask}')

    for s in args.sample:
        sx, sy = (int(v) for v in s.split(','))
        print(f'  sample ({sx},{sy}) = {tuple(a[sy, sx])}')

    if args.bbox:
        bx0, by0, bx1, by1 = args.bbox
        w = m[by0:by1, bx0:bx1]
        ys, xs = np.where(w.any(1))[0], np.where(w.any(0))[0]
        if len(ys):
            print(f'  bbox  x {bx0+xs.min()}-{bx0+xs.max()}  y {by0+ys.min()}-{by0+ys.max()}'
                  f'  w {xs.max()-xs.min()+1}  h {ys.max()-ys.min()+1}')
        else:
            print('  bbox  EMPTY')

    if args.rows:
        ry0, ry1 = args.rows
        rr = runs(m[ry0:ry1, x0:x1].any(1), ry0, args.minlen)
        print(f'  row runs y{ry0}-{ry1} x{x0}-{x1}:')
        for a0, a1 in rr:
            band = m[a0:a1 + 1, x0:x1]
            xs = np.where(band.any(0))[0]
            print(f'    y {a0}-{a1}  h {a1-a0+1:3d}   x {x0+xs.min()}-{x0+xs.max()}'
                  f'  w {xs.max()-xs.min()+1}')
        gaps = [(rr[i][1], rr[i+1][0]) for i in range(len(rr) - 1)]
        print(f'    gaps: {gaps}   <- a clean band has a gap on both sides')

    if args.cols:
        cy0, cy1 = args.cols
        cr = runs(m[cy0:cy1, x0:x1].any(0), x0, args.minlen)
        print(f'  column runs y{cy0}-{cy1}: ' +
              str([(s, e - s + 1) for s, e in cr]) + '   (start, width)')

    if args.curve:
        gy0, gy1 = args.curve
        pts = []
        for xr in range(x0, x1, max(1, (x1 - x0) // 14)):
            col = np.where(m[gy0:gy1, xr])[0]
            pts.append((xr, int(col.min() + gy0) if len(col) else None))
        print('  curve top edge:', pts)
        print('    None = the edge is covered by a foreground element; interpolate it')


if __name__ == '__main__':
    main()
