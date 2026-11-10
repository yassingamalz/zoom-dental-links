# Zoom Dental Clinic: A5 flyer, front and back

Print source for the two-sided A5 flyer (148 × 210 mm, 3 mm bleed, CMYK).
Everything here rebuilds from source with one command.

## Current version

| Side | Version | Status |
|---|---|---|
| Front | v6 | **Press-ready.** Doctors' 12-line services list (7.0 pt), social row (Instagram, Facebook, TikTok, @handle) |
| Back | v12 | **Proof only.** Honeycomb gallery; route map: Google Maps geometry + every landmark from the hand sketch, original map style, labels enlarged and de-overlapped; photos and QR still to confirm |

Final files: `release/front-v6_back-v12/` (previous: `release/front-v6_back-v11/`, `release/front-v6_back-v10/`, `release/front-v6_back-v9/`, `release/front-v6_back-v8/`, `release/front-v6_back-v7/`, `release/front-v6_back-v6/`, `release/front-v6_back-v5/`, `release/front-v5_back-v4/`)

| File | Use |
|---|---|
| `ZoomDental_Flyer_A5_v6_PRESS_cropmarks_CMYK.pdf` | front, send to the printer |
| `ZoomDental_Flyer_A5_v6_bleed_CMYK.pdf` | front, bleed only |
| `ZoomDental_Flyer_A5_v6_plain.pdf` / `_300dpi.png` | front, screen proof |
| `ZoomDental_Flyer_A5_BACK_v12_PROOF.pdf` / `_300dpi.png` | back, approval proof, not for print |
| `Zoom_Dental_Flyer_A5_Front_Back.pdf` | both sides, for WhatsApp approval |
| `COLOUR_SPEC_v6.txt` | printer spec and change log |

## Layout

```
src/
  build_all.py          one command: front press set + back proof + 2-page approval PDF
  front_base_v2.html    front v2, self-contained (fonts and art embedded); the front starts from this
  front_v3.py           swaps in the shared footer, builds the front bleed by edge extension
  front_services.py     fits the services list into the column (font size solved from line count)
  service_lists.json    the services list. First entry is the one that gets built
  footer_parts.py       phone pill + social row + address, shared by both sides
  build_back.py         the back, built from scratch (header, gallery, care section, map, band)
  fs.json, off.json, targets.json, icon_off.json   calibrated font sizes and offsets for the back
  align.py, align_icons.py   re-solve the back's text and icon positions after a change
  render.py             renders the back next to the ChatGPT comp for a visual diff
  assets/               corner wedge, sparkles, logo SVGs, placeholder photos (ph_*.png)
  fonts/                Cairo 400–900, Montserrat 500/600, Questrial (WOFF2)
  skill_scripts/        export + verification (CMYK, K-only crop marks, TAC, QR decode)
reference/              the ChatGPT comps both sides were measured against
release/<version>/      verified outputs, committed
out/                    build output (not committed)
```

## Rebuild

Needs Python 3 with `playwright` (Chromium), `pillow`, `numpy`, `opencv-python`, `fonttools`,
`brotli`, `pikepdf`, `pypdf`, plus `ghostscript` and `poppler-utils` on the system.

```
cd src
python3 build_all.py                                       # front press set + back proof
python3 build_all.py --front-version v7 --back-version v5  # name a new version
```

The front export runs the verification table automatically. All of these must PASS:
fonts embedded, ink TAC under 300%, crop marks K100 only, QR decodes to
`…workers.dev/?src=flyer`.

## Common edits

- **Services list:** edit the first entry in `src/service_lists.json`, rebuild. Size and spacing
  re-solve themselves; the list never gets wider than its column.
- **Phone numbers, handle, address:** `src/footer_parts.py`. Changes both sides.
- **Back text:** in `src/build_back.py`. After moving or resizing text, run `python3 align.py`
  then `python3 align_icons.py` so icons stay centred on their text.
- **Back header layout:** `HDR` in `build_back.py` (`shift` = approved white header).

## Finishing the back

Two things stop the back from going to print:

1. **Photos:** replace the honeycomb photos in `src/assets/` with real clinic photos, same file
   names, square, at least 1200 × 1200 px: `hx_entrance.jpg` (centre), `hx_reception.jpg`,
   `hx_treatment.jpg`, `hx_doctor.jpg`, `hx_equipment.jpg`, `hx_waiting.jpg`,
   `hx_sterilisation.jpg`, plus `ph_scan.png` (intraoral scanner). The current ones are AI images.
2. **QR:** needs the clinic's Google Maps share link. Replace the placeholder box in
   `build_back.py` (search "QR<br>Google Maps") with the generated QR, then add `qr_expect` to the
   back `verify` call in `build_all.py`.

The map (`map_svg()` in `build_back.py`) takes its geometry from Google Maps (`reference/google_maps_*.jpg`)
and its landmarks from the clinic's hand sketch: ش عبد الرسول from the Autostrad side (via ش الزهراء), clinic
at the bend opposite ماركت الفتح, then south-east past سور الجيش to the Carrefour El-Daery / مول 50 (Hub 50) road.
Schematic, not to scale. After moving a label, run `python3 check_map_labels.py` (lists overlaps; Cairo's
tall line box makes it flag near-misses too, so confirm on the render).

Then set `TAGS=0` (removes the PLACEHOLDER labels) and run
`python3 build_all.py --back-press --back-version v13`.

## Versioning

Never overwrite a released version. Bump the version, rebuild, copy the verified files into
a new `release/front-vX_back-vY/` folder, add a "changes in this version" block to the colour
spec, commit, and tag `flyer-a5/front-vX_back-vY`.

| Tag | Front | Back | Notes |
|---|---|---|---|
| `flyer-a5/front-v5_back-v4` | v5 | v4 | 11 services; back white header, taller gallery |
| `flyer-a5/front-v6_back-v5` | v6 | v5 | doctors' 12 services; honeycomb gallery |
| `flyer-a5/front-v6_back-v6` | v6 | v6 | route map redrawn from the clinic's hand sketch |
| `flyer-a5/front-v6_back-v7` | v6 | v7 | same map in the original map style |
| `flyer-a5/front-v6_back-v8` | v6 | v8 | map in the v4 composition: ش عبد الرسول, أمام أسواق الفتح |
| `flyer-a5/front-v6_back-v9` | v6 | v9 | map follows the hand sketch exactly, every landmark |
| `flyer-a5/front-v6_back-v10` | v6 | v10 | map geometry from Google Maps, landmarks from the sketch |
| `flyer-a5/front-v6_back-v11` | v6 | v11 | map labels larger, horizontal, no overlaps |
| `flyer-a5/front-v6_back-v12` | v6 | v12 | mall label مول 50, mall corner cleaned up |
