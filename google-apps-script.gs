/**
 * RSVP receiver for the Mahmoud & Nouran wedding invitation.
 *
 * Deploy this once, bound to whichever spreadsheet should collect the
 * replies, and paste the resulting /exec URL into SHEET_ENDPOINT in
 * index.html. See README.md for the click-by-click steps.
 *
 * It writes to the spreadsheet it is attached to, so the same code works
 * unchanged in any Google account — no ID to edit when the sheet moves.
 * SHEET_ID is only a fallback for running the script standalone.
 */

var SHEET_ID = '1DcRkaPC8yn6WQGuzwS3LfylKPvYGFkRDjbcukdgP0hU';
var SHEET_NAME = 'RSVPs';

var HEADERS = [
  'Timestamp',
  'Full Name',
  'Phone',
  'Attendance',
  'Number of Guests',
  'Song Requests',
  'Warm Blessings'
];

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = getSheet_();

    sheet.appendRow([
      new Date(),
      data.name || '',
      data.phone || '',
      data.attendance || '',
      data.guests || '',
      data.songs || '',
      data.notes || ''
    ]);

    return json_({ status: 'ok' });
  } catch (err) {
    // Logged to the script's execution log so a failure is diagnosable.
    console.error('RSVP write failed: ' + err);
    return json_({ status: 'error', message: String(err) });
  }
}

/** Lets you open the /exec URL in a browser to confirm it is live. */
function doGet() {
  return json_({ status: 'ok', message: 'Mahmoud & Nouran RSVP endpoint is running.' });
}

/** Returns the RSVP tab, creating it with a frozen header row if missing. */
function getSheet_() {
  // Prefer the spreadsheet this script is bound to; fall back to the ID only
  // when the script is running detached from one.
  var book = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById(SHEET_ID);
  var sheet = book.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = book.insertSheet(SHEET_NAME);
  }

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }

  return sheet;
}

function json_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor to create the header row and grant permissions. */
function setup() {
  getSheet_();
}
