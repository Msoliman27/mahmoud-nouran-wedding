# Mahmoud & Nouran — Wedding Invitation

An interactive wedding invitation for **Thursday, 24 September 2026**, Lavendula Hall,
Tiba Rose Hotel, Cairo.

## Contents

| Path | Purpose |
|------|---------|
| `index.html` | The whole invitation — markup, styles and script in one file |
| `assets/carry-you-home.mp3` | The couple's song, played locally (no YouTube embed) |

## Running it

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8000
```

Then visit http://localhost:8000.

> Serve it over HTTP rather than opening the file directly if you want the
> seek bar to work — dragging to a position needs HTTP range requests.

## Features

- Live countdown, pinned to Cairo time so it reads the same in every timezone
- Local audio player: starts at **2:17**, loops back to 2:17, default volume 35%
- Photo gallery with category filters, and an upload-your-own-photo keepsake canvas
- RSVP form saved to `localStorage`, viewable as a table and exportable to CSV
- AI story / wish / DJ / concierge features that fall back to built-in offline
  content, so every button works with no API key

## Optional: live AI replies

The AI features work offline out of the box. To route them through Gemini
instead, run this once in the browser console:

```js
localStorage.setItem('mn_gemini_key', 'YOUR_GEMINI_API_KEY')
```

Do not commit a key to this repository — it would be public.
