/**
 * Zoom Dental — private patient feedback backend (Google Apps Script, bound to a Google Sheet).
 *
 * The page only WRITES. Nothing is ever read back or shown publicly: the Sheet is for the clinic only.
 *
 * One-time setup (signed in as zoomdentalcliniccairo@gmail.com):
 *   1. Drive → Marketing/06_ADMIN → New → Google Sheets → name it "Zoom Dental — Patient feedback".
 *   2. In the sheet: Extensions → Apps Script → replace everything with this file → Save.
 *   3. Pick the function `setup` in the toolbar → Run → allow the permissions.
 *   4. Deploy → New deployment → type "Web app"
 *        Execute as: Me      Who has access: Anyone
 *      → Deploy → copy the Web app URL (ends in /exec).
 *   5. Paste that URL into CONFIG.endpoint in reviews/index.html.
 *   After editing this script later: Deploy → Manage deployments → Edit → Version: New version
 *   (editing the existing deployment keeps the same URL).
 */

const SHEET_NAME = 'Feedback';

// Column order is the contract with the web page. Add new columns at the END only.
const ASPECTS = [
  ['doctor', 'الدكتور'], ['clean', 'النظافة'], ['wait', 'وقت الانتظار'],
  ['staff', 'الاستقبال والفريق'], ['value', 'السعر مقابل الخدمة']
];
const HEADERS = [
  'التاريخ', 'ID', 'المصدر', 'اللغة',
  'الاسم', 'الموبايل', 'عرفتنا منين', 'الدكتور المعالج', 'السبب من الزيارة',
  'التقييم العام', 'سبب التقييم العام'
].concat(...ASPECTS.map(([, ar]) => [ar, `${ar} — السبب`]))
 .concat(['مقترحات لتحسين الخدمة والمكان', 'ملاحظات العيادة']);
const COL = Object.fromEntries(HEADERS.map((h, i) => [h, i + 1]));   // 1-based

/* ───────────────────────── setup ───────────────────────── */

function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) { sh = ss.getSheets()[0]; sh.setName(SHEET_NAME); }
  sh.setRightToLeft(true);
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS])
    .setFontWeight('bold').setBackground('#0A7183').setFontColor('#FFFFFF')
    .setVerticalAlignment('middle').setWrap(true);
  sh.setFrozenRows(1);
  sh.setFrozenColumns(COL['الاسم']);
  sh.setRowHeight(1, 44);

  const rows = sh.getMaxRows() - 1;
  const starCols = [COL['التقييم العام']].concat(ASPECTS.map(([, ar]) => COL[ar]));
  const ranges = starCols.map(c => sh.getRange(2, c, rows, 1));
  ranges.forEach(r => r.setHorizontalAlignment('center').setNumberFormat('0'));
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule()
      .setGradientMinpointWithValue('#F4C7C3', SpreadsheetApp.InterpolationType.NUMBER, '1')
      .setGradientMidpointWithValue('#FCE8B2', SpreadsheetApp.InterpolationType.NUMBER, '3')
      .setGradientMaxpointWithValue('#B7E1CD', SpreadsheetApp.InterpolationType.NUMBER, '5')
      .setRanges(ranges).build()
  ]);
  sh.getRange(2, COL['التاريخ'], rows, 1).setNumberFormat('yyyy-mm-dd hh:mm');
  sh.getRange(2, COL['الموبايل'], rows, 1).setNumberFormat('@');
  HEADERS.forEach((h, i) => { if (/سبب|مقترحات|ملاحظات/.test(h)) sh.setColumnWidth(i + 1, 260); });
  sh.getRange(2, 1, rows, HEADERS.length).setWrap(true).setVerticalAlignment('top');
  sh.hideColumns(COL['ID']);

  buildSummary_(ss);
  SpreadsheetApp.flush();
}

// "Summary" tab: averages and counts over all feedback.
function buildSummary_(ss) {
  let s = ss.getSheetByName('Summary');
  if (!s) s = ss.insertSheet('Summary');
  s.clear();
  s.setRightToLeft(true);
  const L = c => { let n = c, out = ''; while (n > 0) { const m = (n - 1) % 26; out = String.fromCharCode(65 + m) + out; n = Math.floor((n - 1) / 26); } return out; };
  const rng = h => `${SHEET_NAME}!${L(COL[h])}2:${L(COL[h])}`;
  const rows = [['المؤشر', 'القيمة']];
  rows.push(['عدد التقييمات', `=COUNTA(${rng('ID')})`]);
  rows.push(['متوسط التقييم العام', `=IFERROR(ROUND(AVERAGE(${rng('التقييم العام')}),2),"")`]);
  ASPECTS.forEach(([, ar]) => rows.push([`متوسط ${ar}`, `=IFERROR(ROUND(AVERAGE(${rng(ar)}),2),"")`]));
  rows.push(['تقييمات 1 أو 2 نجمة (محتاجة متابعة)', `=COUNTIF(${rng('التقييم العام')},"<=2")`]);
  s.getRange(1, 1, rows.length, 2).setValues(rows);
  s.getRange(1, 1, 1, 2).setFontWeight('bold').setBackground('#0A7183').setFontColor('#FFFFFF');
  s.setColumnWidth(1, 300); s.setColumnWidth(2, 120);
  s.getRange(2, 2, rows.length - 1, 1).setHorizontalAlignment('center');

  // Where patients heard about the clinic.
  s.getRange(rows.length + 2, 1).setValue('عرفتنا منين').setFontWeight('bold');
  s.getRange(rows.length + 3, 1).setFormula(
    `=IFERROR(QUERY(${rng('عرفتنا منين')},"select Col1, count(Col1) where Col1 is not null group by Col1 order by count(Col1) desc label count(Col1) ''",0),"")`);
}

/* ───────────────────────── write ───────────────────────── */

function doPost(e) {
  try {
    const body = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    // Spam traps: hidden field must be empty; a real person takes > 4 s to fill the form.
    if (body.website) return json_({ ok: true });
    if (typeof body.elapsedMs === 'number' && body.elapsedMs < 4000) return json_({ ok: true });

    const overall = star_(body.overall);
    const name = clean_(body.name, 60);
    if (!overall || !name) return json_({ ok: false, error: 'missing' });

    const src = clean_(body.src, 20) || 'web';
    // Soft limit for phones: one rating per device per 12 h (the clinic iPad is exempt).
    if (src !== 'ipad' && body.device) {
      const cache = CacheService.getScriptCache();
      const k = 'dev_' + clean_(body.device, 64);
      if (cache.get(k)) return json_({ ok: false, error: 'too_many' });
      cache.put(k, '1', 12 * 3600);
    }

    const a = body.aspects || {};
    const row = new Array(HEADERS.length).fill('');
    const set = (h, v) => { row[COL[h] - 1] = v; };
    set('التاريخ', new Date());
    set('ID', Utilities.getUuid().slice(0, 8));
    set('المصدر', src);
    set('اللغة', body.lang === 'en' ? 'en' : 'ar');
    set('الاسم', name);
    set('الموبايل', clean_(body.phone, 20).replace(/[^\d+ ]/g, ''));
    set('عرفتنا منين', clean_(body.heard, 120));
    set('الدكتور المعالج', clean_(body.doctor, 60));
    set('السبب من الزيارة', clean_(body.reason, 600));
    set('التقييم العام', overall);
    set('سبب التقييم العام', clean_(body.overallWhy, 800));
    ASPECTS.forEach(([k, ar]) => {
      const x = a[k] || {};
      set(ar, star_(x.stars) || '');
      set(`${ar} — السبب`, clean_(x.why, 500));
    });
    set('مقترحات لتحسين الخدمة والمكان', clean_(body.suggestion, 1000));

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try { sheet_().appendRow(row); } finally { lock.releaseLock(); }
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: 'server' });
  }
}

// Nothing is published. A GET only confirms the endpoint is alive.
function doGet() { return json_({ ok: true }); }

/* ───────────────────────── helpers ───────────────────────── */

function sheet_() {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sh) throw new Error('Run setup() first');
  return sh;
}

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

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
