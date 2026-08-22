# Mahmoud & Nouran — Wedding Invitation

An interactive wedding invitation for **Thursday, 24 September 2026**, Lavendula Hall,
Tiba Rose Hotel, Cairo.

## Contents

| Path | Purpose |
|------|---------|
| `index.html` | The whole invitation — markup, styles and script in one file |
| `ar/index.html` | The Arabic (RTL) edition — generated, do not hand-edit |
| `tools/make_ar.py` | Builds `ar/index.html` from `index.html` |
| `assets/background-music.mp3` | The instrumental that plays quietly under the page |
| `assets/photos/` | The couple's own photos used in the gallery |
| `google-apps-script.gs` | Receives RSVPs and appends them to the Google Sheet |

## The Arabic edition

`ar/index.html` is the same invitation with no English in it: right-to-left, Arabic
type (Aref Ruqaa, Amiri, Tajawal) and Arabic-Indic numerals. Its gallery is cut
down to the two childhood photographs, with no filter tabs, and it opens on
Ar-Rum 30:21 set in Amiri Quran. That verse is stored in the generator as escaped
codepoints so its Uthmani marks cannot be mangled in transit — do not retype it.
It is also silent: no background music, and none of the autoplay handling.
It is **generated**, so edit `index.html` and rebuild rather than editing it directly:

```bash
python tools/make_ar.py index.html ar/index.html
```

The script fails loudly if a phrase it expects has changed, which is the signal to
add the new wording to its translation table.

Both editions post to the same Google Sheet, so RSVPs land in one list. The Arabic
edition sends Arabic values for attendance (`نعم` / `ربما` / `معتذر`).

## Running it

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8000
```

Then visit http://localhost:8000.

## Features

- Live countdown, pinned to Cairo time so it reads the same in every timezone
- Ambient background music: no controls, no track name, volume 18%, looping.
  Browsers block unprompted audio, so if autoplay is refused the track starts
  on the guest's first tap, scroll or key press.
- Photo gallery with category filters; captions sit over the photos and the
  frames are aspect-ratio based, so they scale on phones as well as desktops
- RSVP form that posts to a Google Sheet, with a local backup on the guest's device
- AI story and concierge features that fall back to built-in offline content,
  so every button works with no API key

## Connecting the RSVP form to Google Sheets

A static page can't write to Sheets on its own, so a small Apps Script bound to
the spreadsheet does it. This is a **one-time, five-minute setup**.

1. Open the RSVP spreadsheet:
   https://docs.google.com/spreadsheets/d/1DcRkaPC8yn6WQGuzwS3LfylKPvYGFkRDjbcukdgP0hU/edit
2. **Extensions → Apps Script**. Delete whatever is in `Code.gs`, then paste in
   the entire contents of `google-apps-script.gs` from this repo. Save.
3. Pick the `setup` function in the toolbar dropdown and press **Run** once.
   Approve the permission prompt — this creates the `RSVPs` tab and its headers.
   (Google will warn the app "isn't verified"; choose *Advanced → Go to project*.)
4. **Deploy → New deployment → ⚙ → Web app**, then set:
   - *Execute as*: **Me**
   - *Who has access*: **Anyone**
   
   Press **Deploy** and copy the **Web app URL** (it ends in `/exec`).
5. In `index.html`, paste that URL into the `SHEET_ENDPOINT` constant:
   ```js
   const SHEET_ENDPOINT = "https://script.google.com/macros/s/AKfy.../exec";
   ```
6. Commit and push. Submit a test RSVP and confirm the row lands in the sheet.

Until step 5 is done, RSVPs are still captured — they're stored on the guest's
device and are re-sent automatically the next time that guest opens the page
with a working endpoint.

> *Who has access: Anyone* is required: guests submit without signing in. The
> script only ever appends rows — it never reads or returns your data.

## Seeing the responses

Responses live in the Google Sheet. The page deliberately shows guests no list
of who is attending. For a local backup copy of anything submitted on your own
device, open the invitation with `?admin=1`:

```
https://msoliman27.github.io/mahmoud-nouran-wedding/?admin=1
```

## Optional: live AI replies

The AI features work offline out of the box. To route them through Gemini
instead, run this once in the browser console:

```js
localStorage.setItem('mn_gemini_key', 'YOUR_GEMINI_API_KEY')
```

Do not commit a key to this repository — it would be public.
