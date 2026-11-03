"""Shared phone pill + social row + address, used on both sides of the flyer.

Icons carry ids so the aligner can centre each one on its text's ink box; the
measured offsets live in icon_off.json and are applied as a relative `top` shift.
"""
import json, pathlib

TEAL = '#0A7183'
HANDLE = '@zoom_dental_clinic_cairo'
ADDRESS = 'ق٧٢٠٥ المجاورة السابعة- المعراج السفلي-المعادي-القاهرة'
PHONES = ['010 9241 9234', '010 1943 3676', '011 5222 5589', '012 2447 1397']
OFFF = pathlib.Path(__file__).resolve().parent / 'icon_off.json'


def icon_off():
    return json.loads(OFFF.read_text()) if OFFF.exists() else {}


def svg_whatsapp(size):
    return (f"<svg viewBox='0 0 32 32' width='{size}' height='{size}' style='display:block'>"
            f"<circle cx='16' cy='16' r='16' fill='{TEAL}'/>"
            f"<path fill='#fff' d='M16.02 6.6c-5.16 0-9.35 4.19-9.35 9.35 0 1.65.43 3.26 1.26 4.68L6.5 25.4l4.92-1.29a9.3 9.3 0 0 0 4.6 1.2h.01c5.16 0 9.35-4.19 9.35-9.35s-4.2-9.36-9.36-9.36zm0 17.15h-.01a7.77 7.77 0 0 1-3.96-1.08l-.28-.17-2.92.77.78-2.85-.19-.29a7.75 7.75 0 0 1-1.19-4.14c0-4.29 3.49-7.78 7.78-7.78 2.08 0 4.03.81 5.5 2.28a7.73 7.73 0 0 1 2.27 5.5c0 4.3-3.49 7.76-7.78 7.76zm4.27-5.82c-.23-.12-1.38-.68-1.6-.76-.21-.08-.37-.12-.52.12s-.6.76-.73.91c-.14.16-.27.18-.5.06a6.36 6.36 0 0 1-1.87-1.16 7.06 7.06 0 0 1-1.3-1.61c-.13-.23-.01-.36.1-.48.11-.11.24-.28.35-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.52-1.27-.72-1.73-.19-.46-.38-.4-.52-.4l-.45-.01c-.15 0-.4.06-.61.3-.21.23-.8.78-.8 1.91s.82 2.22.94 2.37c.12.16 1.62 2.47 3.92 3.46.55.24.97.38 1.3.48.55.18 1.05.15 1.44.09.44-.06 1.38-.56 1.57-1.1.19-.55.19-1.01.14-1.11-.06-.1-.21-.16-.44-.28z'/></svg>")


def _social(inner, size):
    """One family: rounded-square outline, glyph inside, white strokes."""
    return (f"<svg viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='#fff' "
            f"stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round' style='display:block'>"
            f"<rect x='2.6' y='2.6' width='18.8' height='18.8' rx='5.4'/>{inner}</svg>")


def svg_instagram(size):
    return _social("<circle cx='12' cy='12' r='4.4'/>"
                   "<circle cx='17.3' cy='6.7' r='1.1' fill='#fff' stroke='none'/>", size)


def svg_facebook(size):
    return _social("<path d='M15.6 7.4h-1.5a2.5 2.5 0 0 0-2.5 2.5v11.5'/><path d='M9.2 13h6'/>", size)


def svg_tiktok(size):
    return _social("<path d='M13.3 6.6v9a3.1 3.1 0 1 1-3.1-3.1'/>"
                   "<path d='M13.3 6.6c.4 1.9 1.8 3.2 3.8 3.4'/>", size)


def svg_pin(size, col='#fff'):
    return (f"<svg viewBox='0 0 24 24' width='{size}' height='{size}' style='display:block'><path fill='{col}' "
            f"d='M12 2.2c-3.9 0-7.05 3.15-7.05 7.05 0 5.05 6.3 12 6.57 12.3a.64.64 0 0 0 .96 0c.27-.3 "
            f"6.57-7.25 6.57-12.3C19.05 5.35 15.9 2.2 12 2.2zm0 10.4a3.36 3.36 0 1 1 0-6.72 3.36 3.36 0 0 1 0 6.72z'/></svg>")


def nudge(id_):
    return f"position:relative;top:{icon_off().get(id_, 0.0):.2f}px;"


def footer(box):
    seps = f"<span style='color:{TEAL};opacity:.35;margin:0 17px;font-weight:400'>|</span>"
    nums = seps.join(f"<span>{n}</span>" for n in PHONES)
    return [
        f"<div style='{box(36, 1329, 982, 67)}background:#fff;border-radius:33.5px'></div>",
        f"<div style='{box(36, 1329, 982, 67)}display:flex;align-items:center;justify-content:center;"
        f"gap:18px;font-family:Mont;font-weight:600;font-size:27px;color:{TEAL};letter-spacing:.2px'>"
        f"<span id='wa' style='display:flex;{nudge('wa')}'>{svg_whatsapp(40)}</span>"
        f"<span id='nums' style='white-space:nowrap'>{nums}</span></div>",
        # social row: Instagram, Facebook, TikTok, then the handle
        f"<div style='{box(75, 1424, 440, 40)}display:flex;align-items:center;"
        f"font-family:Mont;font-weight:500;font-size:19px;color:#fff'>"
        f"<span id='soc' style='display:flex;gap:8px;{nudge('soc')}'>"
        f"{svg_instagram(28)}{svg_facebook(28)}{svg_tiktok(28)}</span>"
        f"<span id='handle' style='margin-left:12px;white-space:nowrap'>{HANDLE}</span></div>",
        f"<div style='{box(440, 1420, 540, 44)}display:flex;align-items:center;justify-content:flex-end;"
        f"gap:12px;direction:ltr;font-family:Cairo;font-weight:500;font-size:19px;line-height:38px;color:#fff'>"
        f"<span id='fpin' style='display:flex;{nudge('fpin')}'>{svg_pin(32)}</span>"
        f"<span id='addr2' style='white-space:nowrap;direction:rtl'>{ADDRESS}</span></div>",
    ]
