/**
 * Zoom Dental — patient reviews backend (Google Apps Script, bound to a Google Sheet).
 *
 * What it does
 *   POST  → appends one review row to the "Reviews" sheet (Approved = unchecked).
 *   GET   → returns only rows where the patient consented AND the clinic ticked Approved,
 *           plus averages over those rows, as JSON for the public /reviews wall.
 *
 * One-time setup (signed in as zoomdentalcliniccairo@gmail.com):
 *   1. Drive → Marketing/06_ADMIN → New → Google Sheets → name it "Zoom Dental — Reviews".
 *   2. In the sheet: Extensions → Apps Script → replace everything with this file → Save.
 *   3. Pick the function `setup` in the toolbar → Run → allow the permissions.
 *   4. Deploy → New deployment → type "Web app"
 *        Execute as: Me      Who has access: Anyone
 *      → Deploy → copy the Web app URL (ends in /exec).
 *   5. Paste that URL into CONFIG.endpoint in reviews/index.html.
 *   After editing this script later: Deploy → Manage deployments → Edit → Version: New version.
 *   (A new deployment gives a new URL; editing the existing one keeps the same URL.)
 */

const SHEET_NAME = 'Reviews';
const CACHE_KEY = 'public_reviews_v1';
const CACHE_SECONDS = 300;              // public wall refreshes at most every 5 min
const MAX_PUBLIC = 60;                  // newest approved reviews returned to the page

// Column order is the contract with the web page. Add new columns at the END only.
const HEADERS = [
  'Submitted at', 'ID', 'Source', 'Language', 'Name',
  'Overall', 'Doctor', 'Cleanliness', 'Waiting time', 'Reception & staff', 'Value for money',
  'Doctor seen', 'Treatment', 'Public comment', 'Private suggestion', 'Phone (optional)',
  'Consent to publish', 'Approved', 'Clinic reply (public)'
];
const COL = Object.fromEntries(HEADERS.map((h, i) => [h, i + 1]));   // 1-based
const ASPECTS = ['Doctor', 'Cleanliness', 'Waiting time', 'Reception & staff', 'Value for money'];
const ASPECT_KEYS = { 'Doctor': 'doctor', 'Cleanliness': 'clean', 'Waiting time': 'wait',
                      'Reception & staff': 'staff', 'Value for money': 'value' };

/* ───────────────────────── setup ───────────────────────── */

function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.getSheets()[0];
    sh.setName(SHEET_NAME);
  }
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS])
    .setFontWeight('bold').setBackground('#0A7183').setFontColor('#FFFFFF')
    .setVerticalAlignment('middle').setWrap(true);
  sh.setFrozenRows(1);
  sh.setRowHeight(1, 40);

  const rows = sh.getMaxRows() - 1;
  // Approved column → checkboxes the clinic ticks to publish a review.
  sh.getRange(2, COL['Approved'], rows, 1).insertCheckboxes();
  // Consent column is written by the form; show it as a read-only-looking checkbox too.
  sh.getRange(2, COL['Consent to publish'], rows, 1).insertCheckboxes();
  // Star columns: centred numbers, colour scale 1 (red) → 5 (green).
  const stars = sh.getRange(2, COL['Overall'], rows, 6);
  stars.setHorizontalAlignment('center').setNumberFormat('0');
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule()
      .setGradientMinpointWithValue('#F4C7C3', SpreadsheetApp.InterpolationType.NUMBER, '1')
      .setGradientMidpointWithValue('#FCE8B2', SpreadsheetApp.InterpolationType.NUMBER, '3')
      .setGradientMaxpointWithValue('#B7E1CD', SpreadsheetApp.InterpolationType.NUMBER, '5')
      .setRanges([stars]).build()
  ]);
  sh.getRange(2, COL['Submitted at'], rows, 1).setNumberFormat('yyyy-mm-dd hh:mm');
  sh.getRange(2, COL['Phone (optional)'], rows, 1).setNumberFormat('@');
  [COL['Public comment'], COL['Private suggestion'], COL['Clinic reply (public)']]
    .forEach(c => sh.setColumnWidth(c, 280));
  sh.getRange(2, COL['Public comment'], rows, 2).setWrap(true);
  sh.getRange(2, COL['Clinic reply (public)'], rows, 1).setWrap(true);
  sh.setColumnWidth(COL['ID'], 90);
  // Nobody needs to see the ID; it only links a row back to a submission.
  sh.hideColumns(COL['ID']);

  buildSummary_(ss);
  invalidate_();
  SpreadsheetApp.flush();
}

// "Summary" tab: averages over ALL reviews (internal view, includes unpublished ones).
function buildSummary_(ss) {
  let s = ss.getSheetByName('Summary');
  if (!s) s = ss.insertSheet('Summary');
  s.clear();
  const R = `${SHEET_NAME}!`;
  const colLetter = c => String.fromCharCode(64 + c);
  const rows = [['Metric', 'All reviews', 'Published only']];
  rows.push(['Number of reviews',
    `=COUNTA(${R}${colLetter(COL['ID'])}2:${colLetter(COL['ID'])})`,
    `=COUNTIFS(${R}${colLetter(COL['Approved'])}2:${colLetter(COL['Approved'])},TRUE,${R}${colLetter(COL['Consent to publish'])}2:${colLetter(COL['Consent to publish'])},TRUE)`]);
  ['Overall'].concat(ASPECTS).forEach(h => {
    const c = colLetter(COL[h]);
    rows.push([`Average — ${h}`,
      `=IFERROR(ROUND(AVERAGE(${R}${c}2:${c}),2),"")`,
      `=IFERROR(ROUND(AVERAGEIFS(${R}${c}2:${c},${R}${colLetter(COL['Approved'])}2:${colLetter(COL['Approved'])},TRUE,${R}${colLetter(COL['Consent to publish'])}2:${colLetter(COL['Consent to publish'])},TRUE),2),"")`]);
  });
  rows.push(['Waiting for review (not approved yet)',
    `=COUNTIFS(${R}${colLetter(COL['Approved'])}2:${colLetter(COL['Approved'])},FALSE,${R}${colLetter(COL['ID'])}2:${colLetter(COL['ID'])},"<>")`, '']);
  s.getRange(1, 1, rows.length, 3).setValues(rows);
  s.getRange(1, 1, 1, 3).setFontWeight('bold').setBackground('#0A7183').setFontColor('#FFFFFF');
  s.setColumnWidth(1, 300); s.setColumnWidth(2, 120); s.setColumnWidth(3, 130);
  s.getRange(2, 2, rows.length - 1, 2).setHorizontalAlignment('center');
}

/* ───────────────────────── write ───────────────────────── */

function doPost(e) {
  try {
    const body = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    // Spam traps: hidden field must be empty; a real person takes > 4 s to fill the form.
    if (body.website) return json_({ ok: true });
    if (typeof body.elapsedMs === 'number' && body.elapsedMs < 4000) return json_({ ok: true });

    const overall = star_(body.overall);
    if (!overall) return json_({ ok: false, error: 'overall_required' });

    const src = clean_(body.src, 20) || 'web';
    // Soft limit for the public QR: one review per device per 12 h (the iPad is exempt).
    if (src !== 'ipad' && body.device) {
      const cache = CacheService.getScriptCache();
      const k = 'dev_' + clean_(body.device, 64);
      if (cache.get(k)) return json_({ ok: false, error: 'too_many' });
      cache.put(k, '1', 12 * 3600);
    }

    const a = body.aspects || {};
    const row = new Array(HEADERS.length).fill('');
    row[COL['Submitted at'] - 1] = new Date();
    row[COL['ID'] - 1] = Utilities.getUuid().slice(0, 8);
    row[COL['Source'] - 1] = src;
    row[COL['Language'] - 1] = body.lang === 'en' ? 'en' : 'ar';
    row[COL['Name'] - 1] = clean_(body.name, 60);
    row[COL['Overall'] - 1] = overall;
    ASPECTS.forEach(h => { row[COL[h] - 1] = star_(a[ASPECT_KEYS[h]]) || ''; });
    row[COL['Doctor seen'] - 1] = clean_(body.doctorSeen, 60);
    row[COL['Treatment'] - 1] = clean_(body.treatment, 60);
    row[COL['Public comment'] - 1] = clean_(body.comment, 1000);
    row[COL['Private suggestion'] - 1] = clean_(body.suggestion, 1000);
    row[COL['Phone (optional)'] - 1] = clean_(body.phone, 20).replace(/[^\d+ ]/g, '');
    row[COL['Consent to publish'] - 1] = body.consent === true;
    row[COL['Approved'] - 1] = false;

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const sh = sheet_();
      // Write at the first empty row so the pre-inserted checkboxes are reused.
      const next = lastDataRow_(sh) + 1;
      sh.getRange(next, 1, 1, row.length).setValues([row]);
      sh.getRange(next, COL['Approved']).insertCheckboxes();
      sh.getRange(next, COL['Consent to publish']).insertCheckboxes()
        .setValue(row[COL['Consent to publish'] - 1]);
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: 'server' });
  }
}

/* ───────────────────────── read ───────────────────────── */

function doGet() {
  const cache = CacheService.getScriptCache();
  const hit = cache.get(CACHE_KEY);
  if (hit) return ContentService.createTextOutput(hit).setMimeType(ContentService.MimeType.JSON);

  const sh = sheet_();
  const last = lastDataRow_(sh);
  const values = last < 2 ? [] : sh.getRange(2, 1, last - 1, HEADERS.length).getValues();

  const published = values.filter(r =>
    r[COL['Approved'] - 1] === true && r[COL['Consent to publish'] - 1] === true && r[COL['Overall'] - 1]);

  const avg = col => {
    const xs = published.map(r => Number(r[col - 1])).filter(n => n >= 1 && n <= 5);
    return xs.length ? Math.round((xs.reduce((s, n) => s + n, 0) / xs.length) * 10) / 10 : null;
  };
  const dist = [1, 2, 3, 4, 5].map(n => published.filter(r => Number(r[COL['Overall'] - 1]) === n).length);

  const reviews = published
    .sort((x, y) => new Date(y[0]) - new Date(x[0]))
    .slice(0, MAX_PUBLIC)
    .map(r => ({
      date: Utilities.formatDate(new Date(r[0]), 'Africa/Cairo', 'yyyy-MM'),
      name: publicName_(r[COL['Name'] - 1]),
      lang: r[COL['Language'] - 1],
      overall: Number(r[COL['Overall'] - 1]),
      treatment: r[COL['Treatment'] - 1] || '',
      doctorSeen: r[COL['Doctor seen'] - 1] || '',
      comment: r[COL['Public comment'] - 1] || '',
      reply: r[COL['Clinic reply (public)'] - 1] || ''
    }));

  const out = JSON.stringify({
    ok: true,
    count: published.length,
    average: avg(COL['Overall']),
    distribution: dist,
    aspects: Object.fromEntries(ASPECTS.map(h => [ASPECT_KEYS[h], avg(COL[h])])),
    reviews
  });
  cache.put(CACHE_KEY, out, CACHE_SECONDS);
  return ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
}

// Simple trigger: ticking/unticking Approved or editing a reply refreshes the public wall at once.
function onEdit(e) {
  if (e && e.range && e.range.getSheet().getName() === SHEET_NAME) invalidate_();
}

/* ───────────────────────── helpers ───────────────────────── */

function sheet_() {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sh) throw new Error('Run setup() first');
  return sh;
}

// Last row that actually has a submission (checkbox columns make getLastRow() useless).
function lastDataRow_(sh) {
  const ids = sh.getRange(2, COL['ID'], Math.max(sh.getMaxRows() - 1, 1), 1).getValues();
  for (let i = ids.length - 1; i >= 0; i--) if (ids[i][0] !== '') return i + 2;
  return 1;
}

function invalidate_() { CacheService.getScriptCache().remove(CACHE_KEY); }

function star_(v) {
  const n = Math.round(Number(v));
  return n >= 1 && n <= 5 ? n : 0;
}

// Trim, cap length, and neutralise spreadsheet formula injection (=, +, -, @ at the start).
function clean_(v, max) {
  let s = String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

// "Ahmed Mohamed Ali" → "Ahmed M." ; empty → "" (the page shows "Patient").
function publicName_(full) {
  const parts = String(full || '').replace(/^'/, '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '';
  return parts.length === 1 ? parts[0] : parts[0] + ' ' + parts[1].charAt(0) + '.';
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
