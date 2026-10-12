# /reviews — patient reviews

- `index.html` — public review wall + rating form, AR/EN, one self-contained page.
- `apps-script/Code.gs` — backend. Lives in a Google Sheet in the clinic's Drive; the clinic ticks **Approved** to publish a review.

## Opening modes

| URL | Opens on | Used for |
|---|---|---|
| `/reviews` | Review wall | Link from the landing page |
| `/reviews?src=qr` | Form | QR code at reception / on the prescription pad |
| `/reviews?src=ipad` | Form, big buttons, resets after 45 s, shows the Google review QR | Clinic iPad |

## Setup (sign in as zoomdentalcliniccairo@gmail.com)

1. Drive → `Marketing/06_ADMIN` → New → Google Sheets → name it `Zoom Dental — Reviews`.
2. Extensions → Apps Script → paste `apps-script/Code.gs` → Save.
3. Choose `setup` in the toolbar → Run → allow permissions. This builds the columns, the Approved checkboxes and a Summary tab.
4. Deploy → New deployment → Web app. Execute as **Me**, access **Anyone** → Deploy → copy the `/exec` URL.
5. Paste it into `CONFIG.endpoint` in `index.html`, then deploy the site.

## Publishing rule

A review shows on the wall only when the patient ticked consent **and** the clinic ticked Approved.
Approve or reject for spam, insults or personal data — not for the star rating.
The **Private suggestion** and **Phone** columns are never sent to the public page.

## Before going live

- Confirm the spelling of Dr. Muhammad Abu El-Yazid's name in `CONFIG.doctors`.
- The live landing page (EN/عربي redesign) is not in this repo. Add a "Reviews" link to it by hand, and copy this folder into whatever the Worker actually deploys from.
