# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Flask web app that generates Word documents for scaffolding (леса) construction
work — "акт выполненных работ" (work-completion act) and "табель" (worker
timesheet). A user fills a single HTML form; the server renders a `.docx`
template with `docxtpl` and streams the file back as a download. The domain and
all UI text are in Russian.

## Commands

```bash
pip install -r requirements.txt        # install deps
python app.py                          # run dev server (Flask debug, port 5000)
gunicorn --bind 127.0.0.1:5000 --workers 3 app:app   # run as in production

python analyze_template.py             # list undeclared Jinja vars in docact.docx
python analyze_docx_xml.py             # dump docact.docx's word/document.xml to document_xml.txt
```

There are no tests and no lint configuration.

### Deployment

Production runs on `46.19.65.232` at `/var/www/act` behind nginx, served by
gunicorn. `deploy.sh` (runs on the server) pulls `main`, reinstalls deps,
restarts gunicorn, and reloads nginx. See `manual_deploy_instructions.md`.

## Architecture

The whole app is three pieces:

- **`app.py`** — Flask app with two POST routes, `/generate_tabel` and
  `/generate_actdoc`. Each route reads form fields, builds a context dict, calls
  `DocxTemplate(...).render(context)`, and returns the result via an in-memory
  `io.BytesIO` stream — nothing is written to disk.
- **`templates/actdoc.html`** — the single served page (`GET /`). It is a
  ~1500-line file with all CSS and JavaScript inline; there is no `static/`
  directory and no separate JS modules.
- **`*.docx` files** — `docxtpl` Jinja-style templates. `docact.docx` backs
  `/generate_actdoc`; `tabel.docx` backs `/generate_tabel`. `template.docx` is
  legacy/unused.

### Word-template rendering details

- **Worker pagination is hardcoded.** The act fits 64 workers as 4 columns of
  16; the timesheet fits 80 as 4 columns of 20. `app.py` splits the flat
  `worker_name[]`/`worker_hour[]` lists into fixed-size groups, **pads each
  group with empty dicts** so the template always has full-length lists, then
  zips them into `left`/`right` pairs. Changing capacity means changing both
  these slice/pad sizes and the table layout in the `.docx`.
- **Circled work-type numbers.** `WORK_TYPE_TO_NUMBER` maps a work type to
  1–20; the selected number is rendered as a bold circled glyph (`CIRCLED_NUMBERS`)
  via a `docxtpl` `RichText`, the rest as plain strings, all keyed in
  `work_type_circles`. Selecting "другие" forces number 20.
- **Checkbox fields** are passed as the string `'✓'` or `' '` (montaj/demontaj/
  modifikaciya, and scaffold `les_type` 1.1 / 2.1 / 4).

### Client-side calculation logic (in `actdoc.html`)

The form does live calculations before submit; the server only renders what the
form sends. Key pieces:

- **`COEFS` table + `CoefUtils.specialCoefficient`** — looks up a coefficient by
  scaffold type (`1.1` / `2.1` / `4`), height band, and work type
  (montaj/demontaj/total). Wrapped in an IIFE and also exported for CommonJS.
- **`updateCalculations`** — computes volume/area from length×width×height per
  scaffold type (`1.1` → a·b·h volume; `2.1` → a·h; `4` → a·b) and feeds the
  hidden `actVem` base.
- **`updateNormHours` / `updateVyrobotka`** — norm hours = `actVem` × special
  coefficient; productivity (выработка) = norm hours × 100 / actual hours.
- **`parseAutoFill`** — heuristically extracts object, position, dimensions,
  scaffold type, hours, and act number from free-form pasted text.
- **`FormCache`** — caches the whole form in `localStorage` (key
  `actdoc_form_cache`, 24h expiry) for auto-save/restore.

Numbers use a comma decimal separator in the UI; conversion to `.` happens at
parse points — keep that consistent when touching calculation code.
