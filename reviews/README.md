# /reviews — private patient feedback

Rebuilt on 2026-11-03 from the doctor-signed notes of 15 Oct 2026. The page is private to the clinic:
no public review wall, no consent-to-publish, no approval column. Everything goes to one Google Sheet.

- `index.html` — feedback form, AR/EN, one self-contained page.
- `apps-script/Code.gs` — backend. Lives in a Google Sheet in the clinic's Drive. Write-only.

## Form order

1. Patient details: name (required), mobile (optional), how did you hear about us (+ Other)
2. Visit: doctor (Abu El-Yazid, Omniya, Omar, Ziad, not sure), السبب من الزيارة — the 12 flyer services in flyer order, multi-choice, + أخرى
3. Rating: labelled 1–5 scale. Overall stars are required; every rating opens a "why" box
4. مقترحاتك لتحسين الخدمة والمكان

## Opening modes

| URL | Used for |
|---|---|
| `/reviews` or `/reviews?src=qr` | Patient's own phone (QR) |
| `/reviews?src=ipad` | Clinic iPad: bigger controls, resets after 45 s, shows the Google review QR |

`CONFIG.askGoogle` turns the "review us on Google" step on the thank-you screen on or off.

## Setup (sign in as zoomdentalcliniccairo@gmail.com)

1. Drive → `Marketing/06_ADMIN` → New → Google Sheets → `Zoom Dental — Patient feedback`.
2. Extensions → Apps Script → paste `apps-script/Code.gs` → Save.
3. Run `setup` → allow permissions. Builds the columns, colours and a Summary tab.
4. Deploy → New deployment → Web app. Execute as **Me**, access **Anyone** → copy the `/exec` URL.
5. Paste it into `CONFIG.endpoint` in `index.html`, then deploy the site.

## Before going live

- Confirm the spelling of Dr. Muhammad Abu El-Yazid and Dr. Omniya in `CONFIG.doctors`.
- The live landing page is not in this repo. Copy this folder into whatever the Worker deploys from.
