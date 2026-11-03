#!/usr/bin/env python3
"""Phase 0: turn a deliverable spec into generator dimensions and copy-paste prompts.

Print:
  python3 asset_plan.py --medium print --trim 148x210 \
      --el hero:tooth:60x75 \
      --el decor:corner-wedge:56x43 \
      --el icon:step-icons:21x21:3 \
      --el base:background:full

Digital:
  python3 asset_plan.py --medium digital --canvas 1080x1350 \
      --el hero:product:520x640 --el icon:feature-icons:96x96:4

Element syntax:  type:name:WxH[:count]
  type   hero | base | decor | icon
  W x H  placed size -- mm for print, px for digital ("full" = whole canvas + bleed)
  count  icons only, how many in the set

Add --multicolour NAME to split that element into one flat file per colour.
See reference/asset-prompts.md for why each rule is there.
"""
import argparse, math

DPI = 300
SAFETY = 2.0

UNIVERSAL = (
    "Output a PNG with a real alpha channel. No background, no text, no lettering, "
    "no watermark, no signature, no border, no frame, no mockup, no drop shadow "
    "outside the object itself. Fill the canvas edge to edge with no padding beyond "
    "what is described. Do not add any element that is not described above."
)


def round_up(px, step=100):
    return int(math.ceil(px / step) * step)


def required_px(size, medium, dpi=DPI, safety=SAFETY):
    """size in mm (print) or px (digital) -> (needed_at_placement, request_this)."""
    w, h = size
    if medium == 'print':
        nw, nh = w / 25.4 * dpi, h / 25.4 * dpi
    else:
        nw, nh = float(w), float(h)
    return (int(nw), int(nh)), (round_up(nw * safety), round_up(nh * safety))


def prompt_hero(name, req, desc=None):
    w, h = req
    return (
        f"Create a single {desc or name.replace('-', ' ')} as a premium, photorealistic "
        f"3D render, centred on a fully transparent background.\n\n"
        f"Canvas: {w} x {h} pixels.\n"
        f"Leave a clear margin between the object and the canvas edges.\n"
        f"Include the object's own soft contact shadow, rendered onto the transparent "
        f"layer beneath it, matching the object's lighting direction.\n"
        f"Clean studio lighting, no reflections of other objects, no environment.\n\n"
        f"{UNIVERSAL}"
    )


def prompt_base(name, req, desc=None):
    w, h = req
    return (
        f"Create a full-bleed background for {desc or name.replace('-', ' ')}.\n\n"
        f"Canvas: exactly {w} x {h} pixels, opaque, filled edge to edge.\n"
        f"Keep the central area visually quiet and low-contrast so text placed over it "
        f"stays readable. Detail and interest belong near the edges.\n"
        f"No text, no logo, no vignette, no border.\n\n"
        f"Output a PNG at exactly the stated dimensions. Do not add any element that is "
        f"not described above."
    )


def prompt_decor(name, req, desc=None, colour='#0A7183'):
    w, h = req
    return (
        f"Create a {desc or name.replace('-', ' ')} as a flat vector-style shape on a "
        f"fully transparent background.\n\n"
        f"Canvas: {w} x {h} pixels.\n"
        f"One single flat colour ({colour}) with no gradient, no shading, no glow, "
        f"no outline and no drop shadow. Crisp clean edges.\n"
        f"Position the shape exactly where it will sit in the layout -- anchored to its "
        f"corner or edge of the canvas, not centred.\n\n"
        f"{UNIVERSAL}"
    )


def prompt_icon(name, req, count, desc=None, colour='#0A7183'):
    w, h = req
    sheet_w = round_up(w * count * 1.4)
    return (
        f"Create {count} line icons for {desc or name.replace('-', ' ')}, arranged in a "
        f"single horizontal row on a fully transparent background.\n\n"
        f"Canvas: {sheet_w} x {h} pixels. Each icon roughly {w} x {h} pixels, "
        f"evenly spaced with a clear gap between them.\n"
        f"Outline/line style only, one single flat colour ({colour}), no fill, "
        f"no gradient, no shadow.\n"
        f"Identical stroke weight and identical optical size across all {count} icons -- "
        f"this must be consistent, do not vary the line thickness between icons.\n"
        f"No circles, rings or frames around the icons. No text labels.\n\n"
        f"{UNIVERSAL}"
    )


def prompt_multicolour(name, req, layers):
    w, h = req
    out = []
    for i, col in enumerate(layers, 1):
        out.append(
            f"[file {i} of {len(layers)}: {name}-layer{i}-{col.lstrip('#')}.png]\n"
            f"Create ONLY the {col} parts of the {name.replace('-', ' ')}, as flat solid "
            f"{col} shapes on a fully transparent background. Everything that is not "
            f"{col} in the final artwork must be fully transparent here.\n"
            f"Canvas: exactly {w} x {h} pixels. Keep every shape in exactly the same "
            f"position it occupies in the complete artwork, so the files stack precisely.\n\n"
            f"{UNIVERSAL}")
    return "\n\n---\n\n".join(out)


BUILDERS = {'hero': prompt_hero, 'base': prompt_base,
            'decor': prompt_decor, 'icon': prompt_icon}


def parse_el(s):
    parts = s.split(':')
    kind, name, size = parts[0], parts[1], parts[2]
    count = int(parts[3]) if len(parts) > 3 else None
    if size == 'full':
        return kind, name, 'full', count
    w, h = (float(v) for v in size.lower().split('x'))
    return kind, name, (w, h), count


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--medium', required=True, choices=['print', 'digital'])
    p.add_argument('--trim', help='WxH in mm, print only')
    p.add_argument('--canvas', help='WxH in px, digital only')
    p.add_argument('--bleed', type=float, default=3.0)
    p.add_argument('--dpi', type=int, default=DPI)
    p.add_argument('--safety', type=float, default=SAFETY)
    p.add_argument('--colour', default='#0A7183')
    p.add_argument('--el', action='append', default=[], help='type:name:WxH[:count]')
    p.add_argument('--multicolour', action='append', default=[],
                   help='NAME=#hex,#hex  -- split into one flat file per colour')
    a = p.parse_args()

    if a.medium == 'print':
        tw, th = (float(v) for v in a.trim.lower().split('x'))
        full = (tw + 2 * a.bleed, th + 2 * a.bleed)
        print(f'# Print · trim {tw:g} x {th:g} mm · bleed {a.bleed:g} mm '
              f'· artwork {full[0]:g} x {full[1]:g} mm · {a.dpi} dpi\n')
    else:
        cw, ch = (int(v) for v in a.canvas.lower().split('x'))
        full = (cw, ch)
        print(f'# Digital · canvas {cw} x {ch} px\n')

    multi = {}
    for m in a.multicolour:
        k, v = m.split('=')
        multi[k] = [c.strip() for c in v.split(',')]

    rows, prompts = [], []
    for spec in a.el:
        kind, name, size, count = parse_el(spec)
        size = full if size == 'full' else size
        need, req = required_px(size, a.medium, a.dpi, a.safety)
        unit = 'mm' if a.medium == 'print' else 'px'
        rows.append((name, kind, f'{size[0]:g}x{size[1]:g} {unit}',
                     f'{need[0]}x{need[1]}', f'{req[0]}x{req[1]}'))
        if name in multi:
            body = prompt_multicolour(name, req, multi[name])
        elif kind == 'icon':
            body = prompt_icon(name, req, count or 3, colour=a.colour)
        elif kind == 'decor':
            body = prompt_decor(name, req, colour=a.colour)
        else:
            body = BUILDERS[kind](name, req)
        prompts.append((name, kind, body))

    w0 = max(len(r[0]) for r in rows) if rows else 4
    print(f'{"asset":<{w0}}  {"type":<6}  {"placed":<14}  {"needed":<12}  ask for')
    for n, k, pl, nd, rq in rows:
        print(f'{n:<{w0}}  {k:<6}  {pl:<14}  {nd:<12}  {rq}')
    print('\n' + '=' * 70)
    for n, k, body in prompts:
        print(f'\n### {n}.png  ({k})\n\n{body}\n\n' + '-' * 70)


if __name__ == '__main__':
    main()
