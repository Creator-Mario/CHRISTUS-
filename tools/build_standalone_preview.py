#!/usr/bin/env python3
"""
build_standalone_preview.py – Generate a fully self-contained Bible preview HTML.

The output file (preview/standalone.html) has ALL Bible data embedded as a
gzip-compressed, base64-encoded JSON blob.  It works without any server –
even when opened directly from a file:// URL or downloaded as a single file.

Usage:
    python3 tools/build_standalone_preview.py

Run from the repository root.
"""

import base64
import csv
import gzip
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "elberfelder_1905.csv")
PASSAGES_JSON = os.path.join(REPO_ROOT, "data", "key_passages.json")
OUTPUT_PATH = os.path.join(REPO_ROOT, "preview", "standalone.html")
PAKO_PATH = os.path.join(REPO_ROOT, "tools", "vendor", "pako_inflate.min.js")

# Cache paths for downloaded translations (not committed to git)
KJV_CACHE = os.path.join(REPO_ROOT, "data", "bible", "en_kjv.json")
ID_CACHE  = os.path.join(REPO_ROOT, "data", "bible", "id_bible.xml")

# ── Book name tables ──────────────────────────────────────────────────────────

EN_BOOK_NAMES = [
    "", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation",
]

ID_BOOK_NAMES = [
    "", "Kejadian", "Keluaran", "Imamat", "Bilangan", "Ulangan",
    "Yosua", "Hakim-Hakim", "Rut", "1 Samuel", "2 Samuel",
    "1 Raja-Raja", "2 Raja-Raja", "1 Tawarikh", "2 Tawarikh", "Ezra",
    "Nehemia", "Ester", "Ayub", "Mazmur", "Amsal",
    "Pengkhotbah", "Kidung Agung", "Yesaya", "Yeremia", "Ratapan",
    "Yehezkiel", "Daniel", "Hosea", "Yoel", "Amos",
    "Obaja", "Yunus", "Mikha", "Nahum", "Habakuk",
    "Zefanya", "Hagai", "Zakharia", "Maleakhi",
    "Matius", "Markus", "Lukas", "Yohanes", "Kisah Para Rasul",
    "Roma", "1 Korintus", "2 Korintus", "Galatia", "Efesus",
    "Filipi", "Kolose", "1 Tesalonika", "2 Tesalonika",
    "1 Timotius", "2 Timotius", "Titus", "Filemon", "Ibrani",
    "Yakobus", "1 Petrus", "2 Petrus", "1 Yohanes", "2 Yohanes", "3 Yohanes",
    "Yudas", "Wahyu",
]

# thiagobodruk/bible en_kjv.json book order matches books 1-66
KJV_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
# christos-c/bible-corpus Indonesian XML
ID_URL  = "https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/Indonesian.xml"

# OSIS-style book code → book number (for the christos-c XML)
ID_CODE_TO_NUM = {
    "GEN":1,"EXO":2,"LEV":3,"NUM":4,"DEU":5,"JOS":6,"JDG":7,"RUT":8,
    "1SA":9,"2SA":10,"1KI":11,"2KI":12,"1CH":13,"2CH":14,"EZR":15,
    "NEH":16,"EST":17,"JOB":18,"PSA":19,"PRO":20,"ECC":21,"SON":22,
    "ISA":23,"JER":24,"LAM":25,"EZE":26,"DAN":27,"HOS":28,"JOE":29,
    "AMO":30,"OBA":31,"JON":32,"MIC":33,"NAH":34,"HAB":35,"ZEP":36,
    "HAG":37,"ZEC":38,"MAL":39,"MAT":40,"MAR":41,"LUK":42,"JOH":43,
    "ACT":44,"ROM":45,"1CO":46,"2CO":47,"GAL":48,"EPH":49,"PHI":50,
    "COL":51,"1TH":52,"2TH":53,"1TI":54,"2TI":55,"TIT":56,"PHM":57,
    "HEB":58,"JAM":59,"1PE":60,"2PE":61,"1JO":62,"2JO":63,"3JO":64,
    "JUD":65,"REV":66,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch(url: str, cache_path: str) -> bytes:
    """Return raw bytes, using a local cache file to avoid repeat downloads."""
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()
    print(f"  Downloading {url} …", flush=True)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(cache_path, "wb") as f:
        f.write(data)
    return data


def find_header(reader):
    for row in reader:
        if any("Verse ID" in c for c in row) and any("Book Number" in c for c in row):
            return row
    raise RuntimeError("CSV header row not found")


def load_data(csv_path: str):
    """Load German Elberfelder 1905 from CSV."""
    books: dict[int, str] = {}
    verses: list[list] = []
    with open(csv_path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = find_header(reader)
        col = {name.strip().strip('"'): idx for idx, name in enumerate(header)}
        for row in reader:
            if not row:
                continue
            try:
                book_id = int(row[col["Book Number"]])
                chapter = int(row[col["Chapter"]])
                verse = int(row[col["Verse"]])
            except (ValueError, KeyError, IndexError):
                continue
            book_name = row[col["Book Name"]]
            text = row[col["Text"]]
            books[book_id] = book_name
            # Compact: [book_id, chapter, verse, text]
            verses.append([book_id, chapter, verse, text])
    return books, verses


def load_kjv() -> tuple[dict, list]:
    """Load English KJV from thiagobodruk/bible JSON (public domain)."""
    raw = _fetch(KJV_URL, KJV_CACHE)
    data = json.loads(raw.decode("utf-8-sig"))
    books: dict[int, str] = {}
    verses: list[list] = []
    for book_idx, book in enumerate(data):
        book_id = book_idx + 1  # 1-based
        books[book_id] = EN_BOOK_NAMES[book_id]
        for ch_idx, chapter in enumerate(book["chapters"]):
            chapter_num = ch_idx + 1
            for v_idx, text in enumerate(chapter):
                verse_num = v_idx + 1
                verses.append([book_id, chapter_num, verse_num, text])
    return books, verses


def load_indonesian() -> tuple[dict, list]:
    """Load Indonesian Bible from christos-c/bible-corpus XML.

    This translation uses combined versification: 1,416 verses are
    self-closing empty tags (<seg .../>) because their content was merged
    into the previous verse.  We fill those with a reference note so the
    app never shows a blank verse number.
    """
    raw = _fetch(ID_URL, ID_CACHE)
    root = ET.fromstring(raw.decode("utf-8"))
    books: dict[int, str] = {}
    verses: list[list] = []
    # Track last non-empty verse number per (book_id, chapter) for merge notes
    last_nonempty: dict[tuple, int] = {}
    for seg in root.iter("seg"):
        if seg.get("type") != "verse":
            continue
        sid = seg.get("id", "")   # e.g. "b.GEN.1.1"
        parts = sid.split(".")
        if len(parts) < 4:
            continue
        code = parts[1]
        book_id = ID_CODE_TO_NUM.get(code)
        if book_id is None:
            continue
        try:
            chapter = int(parts[2])
            verse   = int(parts[3])
        except ValueError:
            continue
        text = (seg.text or "").strip()
        if not text:
            # Empty verse: merged into previous verse in this translation.
            # Show an informative note instead of a blank line.
            prev = last_nonempty.get((book_id, chapter))
            if prev is not None:
                text = f"[Ayat ini tergabung dengan ayat {prev} dalam terjemahan ini]"
            else:
                text = "[Ayat ini tergabung dengan ayat sebelumnya dalam terjemahan ini]"
        else:
            last_nonempty[(book_id, chapter)] = verse
        books[book_id] = ID_BOOK_NAMES[book_id]
        verses.append([book_id, chapter, verse, text])
    return books, verses


def build_payload(books_de: dict, verses_de: list,
                  books_en: dict, verses_en: list,
                  books_id: dict, verses_id: list) -> str:
    """Return base64-encoded gzip-compressed multilingual JSON payload."""
    payload = json.dumps(
        {
            "books": {
                "de": {str(k): v for k, v in sorted(books_de.items())},
                "en": {str(k): v for k, v in sorted(books_en.items())},
                "id": {str(k): v for k, v in sorted(books_id.items())},
            },
            "verses": {
                "de": verses_de,
                "en": verses_en,
                "id": verses_id,
            },
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    compressed = gzip.compress(payload, compresslevel=9)
    return base64.b64encode(compressed).decode("ascii")


APP_VERSION = "1.0.0"
APP_YEAR    = "2025"
APP_AUTHOR  = "Mario Reiner Denzer"
APP_TITLE   = "Buch des Dienstes zur Evangelisation"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Buch des Dienstes zur Evangelisation</title>

  <!-- PWA -->
  <!-- Primary manifest: works on GitHub Pages where icons/icon-192.png is served -->
  <link rel="manifest" href="manifest.json" />
  <meta name="theme-color" content="#0d1b2a" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="BDE Bibel" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="description" content="Buch des Dienstes zur Evangelisation – Elberfelder 1905. Creator &amp; Copyright: Mario Reiner Denzer © 2025" />
  <!-- App icons – embedded base64 so they work from file:// and any URL -->
  <link rel="icon" type="image/png" sizes="192x192"
        href="data:image/png;base64,%%ICON192%%" />
  <link rel="apple-touch-icon" sizes="192x192"
        href="data:image/png;base64,%%ICON192%%" />

  <style>
    :root {
      --navy:    #0d1b2a;
      --navy2:   #1a2f45;
      --gold:    #c9a227;
      --gold-lt: #f4d160;
      --parch:   #f7f3e9;
      --parch-d: #ede4d0;
      --border:  #d9ccb0;
      --text:    #1a1208;
      --text2:   #5a4a2e;
      --card:    #fff;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: Georgia, 'Times New Roman', serif;
      background: var(--parch); color: var(--text);
      max-width: 800px; margin: 0 auto;
    }

    /* ── Splash screen ── */
    #splash {
      position: fixed; inset: 0; z-index: 1000;
      background: linear-gradient(160deg, #08121c 0%, #1a2f45 60%, #0d1b2a 100%);
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; padding: 32px 24px;
      text-align: center; gap: 10px;
    }
    .splash-icon {
      width: 100px; height: 100px; border-radius: 50%;
      background: linear-gradient(135deg, #c9a227, #f4d160);
      display: flex; align-items: center; justify-content: center;
      font-size: 52px; color: #0d1b2a;
      box-shadow: 0 0 40px rgba(201,162,39,.55); margin-bottom: 6px;
    }
    .splash-title {
      font-size: clamp(17px, 5vw, 25px); font-weight: 700;
      color: var(--gold-lt); line-height: 1.35;
      text-shadow: 0 2px 10px rgba(0,0,0,.6); max-width: 320px;
    }
    .splash-subtitle { font-size: 14px; color: #8ab0cc; font-style: italic; }
    .splash-divider  { width: 56px; height: 2px; background: var(--gold); opacity: .65; margin: 4px 0; }
    .splash-creator  { font-size: 14px; color: var(--gold); letter-spacing: .4px; }
    .splash-copy     { font-size: 12px; color: #6a8aaa; }
    .splash-version  { font-size: 11px; color: #4a6a8a; }
    .splash-start {
      margin-top: 18px; padding: 14px 38px;
      background: linear-gradient(135deg, #c9a227, #f4d160);
      color: #0d1b2a; font-size: 16px; font-weight: 700; font-family: Georgia, serif;
      border: none; border-radius: 32px; cursor: pointer;
      box-shadow: 0 4px 22px rgba(201,162,39,.45);
      transition: transform .15s, box-shadow .15s;
    }
    .splash-start:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(201,162,39,.55); }
    #install-btn-splash {
      margin-top: 6px; padding: 9px 22px;
      background: transparent; border: 1.5px solid rgba(201,162,39,.45);
      color: var(--gold-lt); font-size: 13px; border-radius: 24px;
      cursor: pointer; display: inline-block; transition: background .15s;
    }
    #install-btn-splash:hover { background: rgba(201,162,39,.12); }
    #save-btn-splash {
      margin-top: 4px; padding: 9px 22px;
      background: transparent; border: 1.5px solid rgba(201,162,39,.3);
      color: rgba(244,209,96,.7); font-size: 12px; border-radius: 24px;
      cursor: pointer; transition: background .15s;
    }
    #save-btn-splash:hover { background: rgba(201,162,39,.10); }

    /* ── Update banner ── */
    #update-bar {
      display: none; background: #4a3800; color: #fff;
      padding: 10px 16px; align-items: center; gap: 10px; font-size: 14px;
    }
    #update-bar.visible { display: flex; }
    #update-reload {
      background: var(--gold); color: #0d1b2a;
      border: none; border-radius: 12px; padding: 4px 14px;
      font-weight: 700; cursor: pointer; white-space: nowrap;
    }

    /* ── App bar ── */
    #app-bar {
      background: var(--navy); color: #fff;
      padding: 10px 12px; display: flex; align-items: center; gap: 8px;
      position: sticky; top: 0; z-index: 10;
      box-shadow: 0 2px 10px rgba(0,0,0,.5);
      border-bottom: 2px solid var(--gold);
    }
    #back-btn {
      background: none; border: none; color: var(--gold);
      font-size: 22px; cursor: pointer; padding: 4px 6px; display: none;
    }
    #app-icon-btn {
      background: none; border: none; cursor: pointer;
      font-size: 22px; color: var(--gold); padding: 2px 4px; flex-shrink: 0;
    }
    #app-title {
      flex: 1; font-size: 15px; font-weight: 700;
      color: var(--gold-lt); font-family: Georgia, serif;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .bar-btn {
      background: none; border: none; color: var(--gold-lt);
      font-size: 19px; cursor: pointer; padding: 4px 5px;
    }
    #install-btn {
      background: linear-gradient(135deg, #c9a227, #f4d160);
      border: none; color: #0d1b2a; font-size: 11px; font-weight: 700;
      cursor: pointer; padding: 5px 11px; border-radius: 16px;
      display: none; white-space: nowrap; flex-shrink: 0;
    }
    #update-btn {
      background: #c62828; border: none; color: #fff;
      font-size: 11px; font-weight: 700; cursor: pointer;
      padding: 5px 10px; border-radius: 16px;
      display: none; white-space: nowrap; flex-shrink: 0;
    }

    /* ── A2HS / Install guide modal ── */
    #a2hs-overlay {
      display: none; position: fixed; inset: 0; z-index: 9999;
      background: rgba(0,0,0,.82); align-items: flex-end;
      justify-content: center;
    }
    #a2hs-overlay.open { display: flex; }
    #a2hs-modal {
      background: #0d1b2a; border: 2px solid rgba(201,162,39,.55);
      border-radius: 20px 20px 0 0; width: 100%; max-width: 520px;
      padding: 24px 20px 32px; box-shadow: 0 -8px 40px rgba(0,0,0,.7);
      animation: slideUp .25s ease;
    }
    @keyframes slideUp {
      from { transform: translateY(120px); opacity: 0; }
      to   { transform: translateY(0);     opacity: 1; }
    }
    .a2hs-header {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 12px;
    }
    .a2hs-title {
      font-size: 17px; font-weight: 700; color: var(--gold-lt);
      font-family: Georgia, serif;
    }
    .a2hs-close {
      background: none; border: none; color: #6a8aaa;
      font-size: 22px; cursor: pointer; padding: 0 4px; line-height: 1;
    }
    .a2hs-tabs {
      display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap;
    }
    .a2hs-tab {
      padding: 6px 14px; border-radius: 20px; font-size: 13px;
      cursor: pointer; border: 1.5px solid rgba(201,162,39,.35);
      color: #8ab0cc; background: transparent; transition: all .15s;
    }
    .a2hs-tab.active {
      background: linear-gradient(135deg, #c9a227, #f4d160);
      color: #0d1b2a; border-color: transparent; font-weight: 700;
    }
    .a2hs-panel { display: none; }
    .a2hs-panel.active { display: block; }
    .a2hs-step {
      display: flex; align-items: flex-start; gap: 12px;
      margin-bottom: 14px; padding: 12px 14px;
      background: rgba(255,255,255,.04); border-radius: 12px;
      border-left: 3px solid rgba(201,162,39,.5);
    }
    .a2hs-num {
      min-width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, #c9a227, #f4d160);
      color: #0d1b2a; font-weight: 900; font-size: 14px;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    }
    .a2hs-step-text { font-size: 14px; color: #cdd8e3; line-height: 1.5; }
    .a2hs-step-text strong { color: var(--gold-lt); }
    .a2hs-note {
      font-size: 12px; color: #6a8aaa; text-align: center;
      margin-top: 8px; line-height: 1.5;
    }
    /* ── Offline badge ── */
    #offline-badge {
      display: none; align-items: center; gap: 5px;
      background: #333; color: #ffd; font-size: 11px;
      padding: 5px 12px; border-radius: 16px; white-space: nowrap; flex-shrink: 0;
    }
    #offline-badge.offline { display: flex; background: #8b0000; }
    #offline-badge.online  { display: flex; background: #1a5c1a; }

    /* ── Search bar ── */
    #search-bar { background: var(--navy2); padding: 8px 12px; display: none;
      border-bottom: 1px solid var(--gold); }
    #search-input {
      width: 100%; padding: 8px 14px; font-size: 15px;
      border: 1.5px solid var(--gold); border-radius: 20px;
      outline: none; background: var(--parch); color: var(--text);
      font-family: Georgia, serif;
    }

    /* ── Views ── */
    .view { display: none; }
    .view.active { display: block; }

    /* ── Section headers ── */
    .section-header {
      padding: 14px 16px 6px; font-weight: 700; font-size: 12px;
      color: var(--text2); text-transform: uppercase; letter-spacing: .8px;
      font-family: 'Segoe UI', Roboto, sans-serif;
      border-bottom: 1px solid var(--border);
    }

    /* ── Home header banner ── */
    #home-header {
      background: linear-gradient(160deg, var(--navy) 0%, var(--navy2) 100%);
      padding: 18px 20px 22px; text-align: center;
      border-bottom: 2px solid var(--gold);
    }
    .home-cross { font-size: 34px; color: var(--gold); margin-bottom: 6px; }
    .home-title { font-size: 17px; font-weight: 700; color: var(--gold-lt);
      line-height: 1.35; font-family: Georgia, serif; }
    .home-sub   { font-size: 12px; color: #6a8aaa; margin-top: 4px;
      font-family: 'Segoe UI', sans-serif; }

    /* ── Home tab bar ── */
    #home-tabs {
      display: flex; gap: 0;
      border-bottom: 2px solid var(--gold);
      background: var(--navy2);
    }
    .home-tab {
      flex: 1; padding: 14px 8px; border: none; cursor: pointer;
      font-size: 16px; font-weight: 700; font-family: Georgia, serif;
      background: transparent; color: var(--text2);
      border-bottom: 3px solid transparent;
      transition: color .15s, border-color .15s, background .15s;
      letter-spacing: .3px;
    }
    .home-tab.active {
      color: var(--gold);
      border-bottom: 3px solid var(--gold);
      background: rgba(201,162,39,.10);
    }
    .home-tab:hover:not(.active) { background: rgba(255,255,255,.06); color: var(--gold-lt); }
    .home-tab-panel { display: none; }
    .home-tab-panel.active { display: block; }

    /* ── Book button grid ── */
    .book-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
      gap: 8px; padding: 10px 10px 16px;
    }
    .book-btn {
      background: var(--navy2); border: 1px solid var(--gold);
      border-radius: 8px; padding: 8px 4px 7px; cursor: pointer;
      display: flex; flex-direction: column; align-items: center; gap: 2px;
      color: var(--text1); text-align: center;
      transition: background .12s, transform .1s;
    }
    .book-btn:hover, .book-btn:active { background: rgba(201,162,39,.18); transform: scale(1.04); }
    .book-btn-num  { font-size: 10px; color: var(--gold); font-weight: 700; }
    .book-btn-name { font-size: 11px; font-weight: 700; font-family: Georgia, serif;
                     color: var(--gold-lt); line-height: 1.25; word-break: break-word; }
    .book-btn-chs  { font-size: 10px; color: var(--text2); }

    /* ── Theme grid ── */
    #theme-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 12px; padding: 12px 12px 20px;
    }
    .theme-group-header {
      grid-column: 1 / -1;
      padding: 10px 4px 4px;
      font-size: 11px; font-weight: 700; letter-spacing: 1px;
      text-transform: uppercase; color: var(--gold);
      border-bottom: 1px solid var(--gold);
      font-family: 'Segoe UI', Roboto, sans-serif;
      margin-top: 6px;
    }
    .theme-group-header:first-child { margin-top: 0; }
    .theme-card {
      border-radius: 12px; padding: 16px 14px; cursor: pointer;
      display: flex; flex-direction: column; gap: 8px;
      color: #fff; min-height: 105px;
      box-shadow: 0 3px 10px rgba(0,0,0,.30);
      transition: transform .15s, box-shadow .15s;
      border-bottom: 3px solid rgba(201,162,39,.45);
    }
    .theme-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,.38); }
    .theme-icon  { width: 36px; height: 36px; flex-shrink: 0; }
    .theme-name  { font-size: 13px; font-weight: 700; line-height: 1.35;
      font-family: Georgia, serif; }
    .theme-count { font-size: 10px; opacity: .75; margin-top: auto;
      font-family: 'Segoe UI', sans-serif; }

    /* ── List items ── */
    .list-item {
      display: flex; align-items: center; padding: 12px 16px;
      border-bottom: 1px solid var(--border); background: var(--card);
      cursor: pointer; transition: background .15s;
    }
    .list-item:hover { background: var(--parch-d); }
    .avatar {
      width: 34px; height: 34px; border-radius: 50%;
      background: var(--navy); color: var(--gold);
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 700; flex-shrink: 0; margin-right: 12px;
      border: 1.5px solid var(--gold);
    }
    .list-item-text  { flex: 1; }
    .list-item-title { font-size: 15px; font-family: Georgia, serif; }
    .list-item-ref   { font-size: 11px; color: var(--text2); margin-top: 2px;
      font-family: 'Segoe UI', sans-serif; }

    /* ── Passage text ── */
    .chapter-heading {
      padding: 14px 18px 8px; font-weight: 700; font-size: 16px;
      color: var(--navy); font-family: Georgia, serif;
      border-bottom: 2px solid var(--gold); background: var(--parch-d);
    }
    .verse-row {
      padding: 8px 18px; border-bottom: 1px solid var(--border);
      background: var(--card); line-height: 1.85; font-family: Georgia, serif;
      font-size: 15px;
    }
    .verse-num {
      font-weight: 700; color: var(--gold); margin-right: 5px;
      font-size: 11px;
    }

    /* ── Chapter grid ── */
    #chapter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
      gap: 8px; padding: 12px; background: var(--parch);
    }
    .chapter-btn {
      padding: 12px 4px; background: var(--navy); color: var(--gold-lt);
      border: 1px solid var(--gold); border-radius: 6px;
      font-size: 15px; cursor: pointer; font-family: Georgia, serif;
      transition: background .15s, color .15s;
    }
    .chapter-btn:hover { background: var(--gold); color: var(--navy); }

    /* ── Search results ── */
    .result-item {
      padding: 12px 16px; border-bottom: 1px solid var(--border);
      background: var(--card); cursor: pointer;
      font-family: Georgia, serif; font-size: 15px; line-height: 1.75;
    }
    .result-item:hover { background: var(--parch-d); }
    .result-ref { font-size: 12px; color: var(--text2); margin-top: 4px;
      font-family: 'Segoe UI', sans-serif; }
    mark { background: #ffe57f; border-radius: 2px; padding: 0 1px; }

    /* ── Text highlighting ── */
    .verse-row { cursor: pointer; }
    .verse-row[data-hl="green"]  { background: rgba(34,197,94,.18) !important; border-left: 4px solid #22c55e; padding-left: 14px; }
    .verse-row[data-hl="yellow"] { background: rgba(234,179,8,.22)  !important; border-left: 4px solid #eab308; padding-left: 14px; }
    .verse-row[data-hl="red"]    { background: rgba(239,68,68,.18)  !important; border-left: 4px solid #ef4444; padding-left: 14px; }
    .verse-row.hl-selected       { outline: 2px solid var(--gold); outline-offset: -2px; }
    /* ── Merged-verse note (Indonesian translation) ── */
    .verse-merged { font-style: italic; opacity: 0.55; font-size: 0.88em; }

    /* ── Word-level highlighting ── */
    mark.hl-word-green  { background: rgba(34,197,94,.40);  border-radius: 2px; padding: 0 1px; color: inherit; }
    mark.hl-word-yellow { background: rgba(234,179,8,.55);  border-radius: 2px; padding: 0 1px; color: inherit; }
    mark.hl-word-red    { background: rgba(239,68,68,.40);  border-radius: 2px; padding: 0 1px; color: inherit; }

    /* ── Word-HL floating toolbar ── */
    #word-hl-bar {
      display: none; position: fixed; z-index: 900;
      background: #0d1b2a; border: 2px solid rgba(201,162,39,.8);
      border-radius: 40px; padding: 7px 14px;
      box-shadow: 0 6px 24px rgba(0,0,0,.7);
      align-items: center; gap: 10px;
      pointer-events: all;
    }
    #word-hl-bar.open { display: flex; }
    .whl-btn {
      width: 32px; height: 32px; border-radius: 50%;
      border: 2.5px solid rgba(255,255,255,.3);
      cursor: pointer; flex-shrink: 0; transition: transform .12s;
    }
    .whl-btn:active { transform: scale(.85); }
    .whl-green  { background: #22c55e; }
    .whl-yellow { background: #eab308; }
    .whl-red    { background: #ef4444; }
    .whl-clear  {
      background: none; border: 1.5px solid rgba(201,162,39,.5);
      color: #c9a227; border-radius: 20px; font-size: 12px;
      padding: 5px 11px; cursor: pointer; white-space: nowrap;
      font-family: 'Segoe UI', sans-serif;
    }
    .whl-clear:active { background: rgba(201,162,39,.15); }

    /* ── Highlight toolbar ── */
    #hl-toolbar {
      display: none; position: fixed; bottom: 28px; left: 50%;
      transform: translateX(-50%); z-index: 800;
      background: #0d1b2a; border: 2px solid rgba(201,162,39,.7);
      border-radius: 40px; padding: 8px 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,.7);
      align-items: center; gap: 10px; min-width: 270px;
      justify-content: center;
    }
    #hl-toolbar.open { display: flex; }
    .hl-label { font-size: 13px; color: #8ab0cc; font-family: 'Segoe UI', sans-serif; }
    .hl-divider { width: 1px; height: 24px; background: rgba(201,162,39,.35); flex-shrink: 0; }
    .hl-btn {
      width: 36px; height: 36px; border-radius: 50%;
      border: 2.5px solid rgba(255,255,255,.25);
      cursor: pointer; transition: transform .12s, border-color .15s; flex-shrink: 0;
    }
    .hl-btn:active  { transform: scale(.88); }
    .hl-btn.hl-green  { background: #22c55e; }
    .hl-btn.hl-yellow { background: #eab308; }
    .hl-btn.hl-red    { background: #ef4444; }
    .hl-clear {
      background: none; border: 1.5px solid rgba(201,162,39,.45);
      color: #c9a227; border-radius: 20px; font-size: 12px;
      padding: 6px 12px; cursor: pointer; white-space: nowrap;
      font-family: 'Segoe UI', sans-serif;
    }
    .hl-clear:active { background: rgba(201,162,39,.15); }

    /* ── Language picker ── */
    #lang-screen {
      position: fixed; inset: 0; z-index: 1001;
      background: linear-gradient(160deg, #08121c 0%, #1a2f45 60%, #0d1b2a 100%);
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; padding: 32px 24px; text-align: center; gap: 14px;
    }
    .lang-pick { font-size: 13px; color: #8ab0cc; }
    .lang-cards { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-top: 8px; }
    .lang-card {
      background: rgba(255,255,255,.06); border: 2px solid rgba(201,162,39,.3);
      border-radius: 14px; padding: 18px 22px; cursor: pointer; color: #fff;
      display: flex; flex-direction: column; align-items: center; gap: 6px;
      font-family: Georgia,serif; min-width: 100px;
      transition: border-color .15s, background .15s, transform .12s;
    }
    .lang-card:hover, .lang-card:focus { border-color: var(--gold); background: rgba(201,162,39,.12); transform: translateY(-2px); outline: none; }
    .lang-flag { font-size: 40px; }
    .lang-name { font-size: 14px; font-weight: 700; color: var(--gold-lt); }

    /* ── Notes / Comments area ── */
    #passage-notes {
      margin: 20px 16px 8px; background: rgba(201,162,39,.06);
      border: 1.5px solid rgba(201,162,39,.3); border-radius: 12px;
      padding: 14px 16px;
    }
    .notes-heading {
      font-family: Georgia, serif; font-size: 13px; font-weight: 700;
      color: var(--gold); letter-spacing: .04em; margin-bottom: 10px;
      display: flex; align-items: center; gap: 6px;
    }
    #notes-textarea {
      width: 100%; box-sizing: border-box;
      min-height: 110px; resize: vertical;
      background: rgba(255,255,255,.04); color: var(--parchment);
      border: 1px solid rgba(201,162,39,.35); border-radius: 8px;
      padding: 10px 12px; font-family: Georgia, serif; font-size: 14px;
      line-height: 1.6; outline: none;
    }
    #notes-textarea:focus { border-color: var(--gold); background: rgba(255,255,255,.07); }
    .notes-actions {
      display: flex; gap: 8px; margin-top: 10px; justify-content: flex-end;
    }
    .notes-btn {
      font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: 700;
      border-radius: 20px; padding: 6px 16px; cursor: pointer;
      border: 1.5px solid rgba(201,162,39,.5); transition: background .15s;
    }
    #notes-save-btn  { background: var(--gold); color: #0d1b2a; }
    #notes-save-btn:active { background: #a07c18; }
    #notes-clear-btn { background: none; color: var(--gold); }
    #notes-clear-btn:active { background: rgba(201,162,39,.15); }
    #notes-saved-indicator {
      font-size: 11px; color: #4ade80; align-self: center;
      opacity: 0; transition: opacity .4s;
    }
    #notes-saved-indicator.show { opacity: 1; }

    /* ── Misc ── */
    #loading { text-align: center; padding: 80px 16px;
      color: var(--text2); font-size: 16px; font-family: Georgia, serif; }
    .empty { text-align: center; padding: 40px 16px; color: var(--text2);
      font-family: Georgia, serif; font-style: italic; }

    /* ── Footer ── */
    #app-footer {
      text-align: center; padding: 22px 16px 36px;
      font-size: 11px; color: var(--text2);
      font-family: 'Segoe UI', sans-serif;
      border-top: 1px solid var(--border); line-height: 1.8;
    }
    #app-footer strong { color: var(--navy); }
  </style>
</head>
<body>

<!-- ── Language picker ──────────────────────────────────────── -->
<div id="lang-screen">
  <div class="splash-icon">✝</div>
  <div class="splash-title" data-i18n="app_title">Buch des Dienstes zur Evangelisation</div>
  <div class="lang-pick">Bitte wähle eine Sprache · Choose a language · Pilih bahasa</div>
  <div class="lang-cards">
    <button class="lang-card" onclick="setLang('de')">
      <span class="lang-flag" aria-hidden="true">🇩🇪</span>
      <span class="lang-name">Deutsch</span>
    </button>
    <button class="lang-card" onclick="setLang('en')">
      <span class="lang-flag" aria-hidden="true">🇬🇧</span>
      <span class="lang-name">English</span>
    </button>
    <button class="lang-card" onclick="setLang('id')">
      <span class="lang-flag" aria-hidden="true">🇮🇩</span>
      <span class="lang-name">Bahasa Indonesia</span>
    </button>
  </div>
</div>

<!-- ── Splash cover ─────────────────────────────────────────── -->
<div id="splash">
  <div class="splash-icon">✝</div>
  <div class="splash-title" data-i18n="app_title">Buch des Dienstes zur Evangelisation</div>
  <div class="splash-subtitle" data-i18n="splash_subtitle">Elberfelder Bibel 1905</div>
  <div class="splash-divider"></div>
  <div class="splash-creator" data-i18n="splash_creator">von Mario Reiner Denzer</div>
  <div class="splash-copy">© 2025 Mario Reiner Denzer</div>
  <div class="splash-version">Version 1.0.0</div>
  <button class="splash-start" onclick="closeSplash()" data-i18n="splash_start">✝ &nbsp;Zur Bibel</button>
  <button id="install-btn-splash" data-i18n="install_btn">⬇ &nbsp;App installieren</button>
  <button id="save-btn-splash" onclick="saveOffline()" title="Als Datei speichern" data-i18n="save_offline_btn">💾 &nbsp;Offline speichern</button>
</div>

<!-- ── A2HS Install Guide Modal ────────────────────────────── -->
<div id="a2hs-overlay" role="dialog" aria-modal="true" aria-label="App installieren">
  <div id="a2hs-modal">
    <div class="a2hs-header">
      <span class="a2hs-title" data-i18n="a2hs_title">📱 App zum Startbildschirm</span>
      <button class="a2hs-close" onclick="closeA2HS()" id="a2hs-close-btn" aria-label="Schließen">✕</button>
    </div>
    <div class="a2hs-tabs">
      <button class="a2hs-tab" id="tab-android" onclick="switchA2HS('android')"><span aria-hidden="true">🤖</span> Android</button>
      <button class="a2hs-tab" id="tab-iphone"  onclick="switchA2HS('iphone')"><span aria-hidden="true">🍎</span> iPhone</button>
      <button class="a2hs-tab" id="tab-desktop" onclick="switchA2HS('desktop')"><span aria-hidden="true">💻</span> Desktop</button>
    </div>

    <!-- Android -->
    <div class="a2hs-panel" id="panel-android">
      <div class="a2hs-step" id="a2hs-android-step0" style="display:none">
        <div class="a2hs-num">0</div>
        <div class="a2hs-step-text"><strong>Zuerst:</strong> Öffne die BDE-Bibel URL <strong>in Chrome</strong>:<br>
        <code style="font-size:11px;color:var(--gold-lt);word-break:break-all">https://creator-mario.github.io/CHRISTUS-/preview/standalone.html</code></div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num" id="a2hs-and-n1">1</div>
        <div class="a2hs-step-text">Seite in <strong>Chrome</strong> oder <strong>Samsung Internet</strong> öffnen (HTTPS-Link, nicht aus Datei).</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">2</div>
        <div class="a2hs-step-text">Chrome zeigt automatisch ein <strong>„Installieren"</strong>-Banner am unteren Rand – darauf tippen.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">3</div>
        <div class="a2hs-step-text"><em>Kein Banner?</em> Tippe auf das <strong>Menü ⋮</strong> (oben rechts) → <strong>„Zum Startbildschirm hinzufügen"</strong>.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">4</div>
        <div class="a2hs-step-text">Tippe auf <strong>„Hinzufügen"</strong> im Bestätigungsdialog.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">5</div>
        <div class="a2hs-step-text">✅ Das <strong>✝ BDE-Symbol</strong> erscheint auf deinem Startbildschirm – die App öffnet sich offline!</div>
      </div>
      <div class="a2hs-note" id="a2hs-and-note">💡 Samsung Internet: „Seite hinzufügen zu → Startbildschirm"</div>
    </div>

    <!-- iPhone -->
    <div class="a2hs-panel" id="panel-iphone">
      <div class="a2hs-step">
        <div class="a2hs-num">1</div>
        <div class="a2hs-step-text">Öffne diese Seite in <strong>Safari</strong> auf deinem iPhone oder iPad.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">2</div>
        <div class="a2hs-step-text">Tippe auf das <strong>Teilen-Symbol ⬆</strong> unten in der Mitte der Symbolleiste.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">3</div>
        <div class="a2hs-step-text">Scrolle nach unten und tippe auf <strong>„Zum Home-Bildschirm"</strong>.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">4</div>
        <div class="a2hs-step-text">Tippe rechts oben auf <strong>„Hinzufügen"</strong>.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">5</div>
        <div class="a2hs-step-text">✅ Das <strong>✝ BDE-Symbol</strong> erscheint auf deinem Home-Bildschirm!</div>
      </div>
      <div class="a2hs-note">⚠ Nur Safari unterstützt „Zum Home-Bildschirm" auf iPhone/iPad. Chrome iOS unterstützt diese Funktion nicht.</div>
    </div>

    <!-- Desktop -->
    <div class="a2hs-panel" id="panel-desktop">
      <div class="a2hs-step">
        <div class="a2hs-num">1</div>
        <div class="a2hs-step-text">Öffne diese Seite in <strong>Chrome oder Edge</strong> am Computer.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">2</div>
        <div class="a2hs-step-text">Klicke auf das <strong>Install-Symbol ⊕</strong> rechts in der Adressleiste (erscheint automatisch).</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">3</div>
        <div class="a2hs-step-text">Klicke auf <strong>„Installieren"</strong> im Popup-Dialog.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">4</div>
        <div class="a2hs-step-text">✅ Die App öffnet sich in einem <strong>eigenen Fenster</strong> ohne Browser-Leiste – wie ein Programm!</div>
      </div>
      <div class="a2hs-note">💡 Alternative: Datei <strong>BDE-Bibel.html</strong> herunterladen und direkt öffnen – funktioniert offline ohne Installation.</div>
    </div>
  </div>
</div>

<!-- ── Update banner ────────────────────────────────────────── -->
<div id="update-bar">
  <span style="flex:1" data-i18n="update_msg">🔄 Neue Version verfügbar!</span>
  <button id="update-reload" onclick="location.reload()" data-i18n="update_btn">Jetzt aktualisieren</button>
</div>

<!-- ── App bar ──────────────────────────────────────────────── -->
<div id="app-bar">
  <button id="back-btn" onclick="goBack()">&#8592;</button>
  <button id="app-icon-btn" onclick="goHome()" title="Startseite">✝</button>
  <span id="app-title">BDE – Bibel</span>
  <button id="update-btn"  onclick="location.reload()" title="Update verfügbar" data-i18n="update_btn_bar">↻ Update</button>
  <button id="install-btn" onclick="installApp()"      title="App installieren" data-i18n="install_bar">⬇ Installieren</button>
  <span   id="offline-badge" data-i18n="offline_badge">📵 Offline</span>
  <button class="bar-btn" id="lang-btn"     title="Sprache ändern" onclick="changeLang()">🌐</button>
  <button class="bar-btn" id="search-toggle" title="Suchen"      onclick="showSearch()">&#128269;</button>
</div>

<!-- ── Search bar ───────────────────────────────────────────── -->
<div id="search-bar">
  <input id="search-input" type="search" placeholder="Bibelstellen suchen …"
         data-i18n-placeholder="search_placeholder"
         oninput="onSearchInput(this.value)" />
</div>

<div id="loading">✝&ensp;Daten werden geladen …</div>

<!-- ── Views ────────────────────────────────────────────────── -->
<div id="view-home" class="view">
  <div id="home-header">
    <div class="home-cross">✝</div>
    <div class="home-title" data-i18n="app_title">Buch des Dienstes zur Evangelisation</div>
    <div class="home-sub" data-i18n="home_sub">Elberfelder 1905 · 66 Bücher · 31 102 Verse</div>
  </div>
  <!-- ── Big navigation tabs ── -->
  <div id="home-tabs">
    <button class="home-tab active" id="tab-btn-themes" onclick="switchHomeTab('themes')" data-i18n="tab_themes">✝ Themen</button>
    <button class="home-tab"        id="tab-btn-bible"  onclick="switchHomeTab('bible')"  data-i18n="tab_bible">📖 Bibel</button>
    <button class="home-tab"        id="tab-btn-notes"  onclick="switchHomeTab('notes')"  data-i18n="tab_notes">📝 Notizen</button>
  </div>
  <!-- Themes tab: theme grid (default) -->
  <div class="home-tab-panel active" id="panel-themes">
    <div id="theme-grid"></div>
  </div>
  <!-- Bible tab: book button grid -->
  <div class="home-tab-panel" id="panel-bible">
    <div id="home-book-list"></div>
  </div>
  <!-- Notes tab: all comments grouped by theme -->
  <div class="home-tab-panel" id="panel-notes">
    <div id="notes-overview"></div>
  </div>
  <div id="app-footer">
    <strong data-i18n="app_title">Buch des Dienstes zur Evangelisation</strong><br>
    <span data-i18n="footer_credit">Creator &amp; Copyright: Mario Reiner Denzer · © 2025 · Version 1.0.0</span><br>
    <span data-i18n="footer_bible">Bibeltext: Elberfelder 1905 (gemeinfrei)</span><br>
    <button id="save-footer-btn" onclick="saveOffline()" data-i18n="save_offline_btn" style="
      margin-top:10px; padding:8px 20px;
      background:linear-gradient(135deg,#c9a227,#f4d160);
      color:#0d1b2a; border:none; border-radius:20px;
      font-size:13px; font-family:Georgia,serif;
      font-weight:700; cursor:pointer;">
      💾 App als Datei speichern (offline)
    </button>
  </div>
</div>
<div id="view-passages" class="view"><div id="passage-list"></div></div>
<div id="view-text" class="view">
  <div id="passage-text"></div>
  <!-- ── Notes / Comments section ── -->
  <div id="passage-notes">
    <div class="notes-heading">✏️ <span data-i18n="notes_title">Mein Kommentar</span></div>
    <textarea id="notes-textarea" data-i18n-placeholder="notes_placeholder" placeholder="Kommentar, Gedanken oder Notizen zu dieser Bibelstelle …" aria-label="Kommentar"></textarea>
    <div class="notes-actions">
      <span id="notes-saved-indicator">✔ gespeichert</span>
      <button class="notes-btn" id="notes-clear-btn" onclick="clearNotes()" data-i18n="notes_clear">Löschen</button>
      <button class="notes-btn" id="notes-save-btn"  onclick="saveNotes()" data-i18n="notes_save">Speichern</button>
    </div>
  </div>
</div>
<div id="view-books"    class="view"><div id="book-list"></div></div>
<div id="view-chapters" class="view"><div id="chapter-grid"></div></div>
<div id="view-verses"   class="view"><div id="verse-list"></div></div>
<div id="view-search"   class="view"><div id="search-results"></div></div>

<!-- ── Highlight toolbar ───────────────────────────────────────── -->
<div id="hl-toolbar" role="toolbar" aria-label="Vers markieren">
  <span class="hl-label" aria-hidden="true">🎨</span>
  <span class="hl-divider"></span>
  <button class="hl-btn hl-green"  onclick="setHL('green')"  title="Grün markieren"   aria-label="Grün"></button>
  <button class="hl-btn hl-yellow" onclick="setHL('yellow')" title="Gelb markieren"   aria-label="Gelb"></button>
  <button class="hl-btn hl-red"    onclick="setHL('red')"    title="Rot markieren"    aria-label="Rot"></button>
  <span class="hl-divider"></span>
  <button class="hl-clear"         onclick="setHL(null)"                               aria-label="Markierung löschen">✕ löschen</button>
</div>

<!-- ── Word-level highlight toolbar (appears at selection) ────── -->
<div id="word-hl-bar" role="toolbar" aria-label="Wort markieren">
  <button class="whl-btn whl-green"  onclick="applyWordHL('green')"  title="Grün"  aria-label="Grün markieren"></button>
  <button class="whl-btn whl-yellow" onclick="applyWordHL('yellow')" title="Gelb"  aria-label="Gelb markieren"></button>
  <button class="whl-btn whl-red"    onclick="applyWordHL('red')"    title="Rot"   aria-label="Rot markieren"></button>
  <button class="whl-clear"          onclick="clearWordHLSel()"                    aria-label="Markierung löschen">✕</button>
</div>

<!-- pako inflate (ES5) – works on all Android/iOS/Desktop browsers -->
<script>%%PAKO%%</script>
<script>
// ── Embedded data ─────────────────────────────────────────────
const PAYLOAD_B64  = '%%PAYLOAD%%';
const PASSAGE_DATA = %%PASSAGE_DATA%%;

// ── State ─────────────────────────────────────────────────────
let ALL_DATA = null;  // full multilingual payload: {books:{de,en,id}, verses:{de,en,id}}
let BOOKS  = {};
let VERSES = [];
let IDX    = {};
let navHistory = [];
let searchTimer = null;
let currentThemeColor = '#0d1b2a';

const THEME_COLORS = [
  '#1a3a5c','#4a1060','#7b1a1a','#1a4a2e','#6b4500',
  '#005060','#2d4080','#3e3e1e','#5a2040','#00406a',
  '#1e4a3a','#6a2000','#2a2a70','#106040','#4a0060',
  '#802000','#004040','#600040'
];
// Must be declared before init() IIFE to avoid temporal dead zone
const APP_BAR_TITLE = 'BDE\u202fBibel';

// ── i18n ──────────────────────────────────────────────────────
const LANG = {
  de: {
    app_title:         'Buch des Dienstes zur Evangelisation',
    splash_subtitle:   'Elberfelder Bibel 1905',
    splash_creator:    'von Mario Reiner Denzer',
    footer_credit:     'Creator \u0026 Copyright: Mario Reiner Denzer \u00b7 \u00a9 2025 \u00b7 Version 1.0.0',
    footer_bible:      'Bibeltext: Elberfelder 1905 (gemeinfrei)',
    a2hs_title:        '\ud83d\udcf1 App zum Startbildschirm',
    a2hs_close_label:  'Schlie\xdfen',
    a2hs: {
      android: {
        steps: [
          'Öffne diese Seite in <strong>Chrome</strong> (oder Samsung Internet) auf deinem Android-Gerät.',
          'Tippe auf das <strong>Menü ⋮</strong> (drei Punkte oben rechts).',
          'Wähle <strong>„Zum Startbildschirm hinzufügen"</strong> aus der Liste.',
          'Tippe auf <strong>„Hinzufügen"</strong> im Bestätigungsdialog.',
          '✅ Das <strong>✝ BDE-Symbol</strong> erscheint auf deinem Startbildschirm \u2013 die App öffnet sich wie eine native App!'
        ],
        note: '💡 Tipp: In Samsung Internet heißt es „Seite hinzufügen zu → Startbildschirm"'
      },
      iphone: {
        steps: [
          'Öffne diese Seite in <strong>Safari</strong> auf deinem iPhone oder iPad.',
          'Tippe auf das <strong>Teilen-Symbol ⬆</strong> unten in der Mitte der Symbolleiste.',
          'Scrolle nach unten und tippe auf <strong>„Zum Home-Bildschirm"</strong>.',
          'Tippe rechts oben auf <strong>„Hinzufügen"</strong>.',
          '✅ Das <strong>✝ BDE-Symbol</strong> erscheint auf deinem Home-Bildschirm!'
        ],
        note: '⚠ Nur Safari unterstützt „Zum Home-Bildschirm" auf iPhone/iPad. Chrome iOS unterstützt diese Funktion nicht.'
      },
      desktop: {
        steps: [
          'Öffne diese Seite in <strong>Chrome oder Edge</strong> am Computer.',
          'Klicke auf das <strong>Install-Symbol ⊕</strong> rechts in der Adressleiste (erscheint automatisch).',
          'Klicke auf <strong>„Installieren"</strong> im Popup-Dialog.',
          '✅ Die App öffnet sich in einem <strong>eigenen Fenster</strong> ohne Browser-Leiste \u2013 wie ein Programm!'
        ],
        note: '💡 Alternative: Datei <strong>BDE-Bibel.html</strong> herunterladen und direkt öffnen \u2013 funktioniert offline ohne Installation.'
      }
    },
    splash_start:      '✝\u00a0\u00a0Zur Bibel',
    install_btn:       '⬇\u00a0\u00a0App installieren',
    save_offline_btn:  '💾\u00a0App als Datei speichern (offline)',
    update_msg:        '🔄 Neue Version verfügbar!',
    update_btn:        'Jetzt aktualisieren',
    update_btn_bar:    '↻ Update',
    install_bar:       '⬇ Installieren',
    offline_badge:     '📵 Offline',
    online_badge:      '✅ Online',
    search_placeholder:'Bibelstellen suchen \u2026',
    search_hint:       'Suchbegriff eingeben \u2026',
    no_results:        'Keine Ergebnisse gefunden.',
    loading:           '✝\u2005Daten werden geladen \u2026',
    all_books:         'Alle Bücher',
    tab_bible:         '📖 Bibel',
    tab_themes:        '✝ Themen',
    search_title:      'Suchen',
    at_label:          'Altes Testament (1\u201339)',
    nt_label:          'Neues Testament (40\u201366)',
    chapters_unit:     'Kapitel',
    verses_unit:       'Verse',
    passages_unit:     'Stellen',
    tg_ot:             'Altes Testament – Geschichte',
    tg_psalms:         'Psalmen & Prophetie',
    tg_bund:           'Bund',
    tg_jesus:          'Jesus Christus',
    tg_gospels:        'Die vier Evangelien',
    tg_nt:             'Apostelgeschichte & Briefe',
    thematic_header:   'Thematische Bibelstellen',
    home_sub:          'Elberfelder 1905 \u00b7 66 Bücher \u00b7 31\u202f102 Verse',
    passages:          'Passagen',
    notes_title:       'Mein Kommentar',
    notes_placeholder: 'Kommentar, Gedanken oder Notizen zu dieser Bibelstelle …',
    notes_save:        'Speichern',
    notes_clear:       'Löschen',
    notes_saved:       '✔ gespeichert',
    tab_notes:         '📝 Notizen',
    notes_overview_empty: 'Noch keine Notizen vorhanden.\nFüge Kommentare in den Themen hinzu.',
    notes_goto:        '→ Zur Stelle',
    notes_delete:      '🗑 Löschen',
    notes_export:      '📤 Alle Notizen exportieren',
    theme_names: {
      1:'Schöpfung und Ursprung',
      2:'Die Erzväter und Mütter Israels',
      3:'Der Auszug aus Ägypten und die Wüstenzeit',
      4:'Gesetz und Bund',
      5:'Einzug und Landnahme',
      6:'Die Zeit der Richter',
      7:'Könige und Prophetie in Israel',
      8:'Die großen Propheten Elia und Elisa',
      9:'Psalmen: Gebete und Lieder',
      10:'Prophetische Bücher und Botschaft',
      11:'Jesus Christus: Geburt und Kindheit',
      12:'Jesu Wirken: Taufe, Versuchung und Berufung',
      13:'Die Bergpredigt',
      14:'Gleichnisse Jesu',
      15:'Wunder und Heilungen',
      16:'Passion und Auferstehung Jesu',
      17:'Die Apostelgeschichte und die Briefe',
      18:'Die Offenbarung: Vollendung',
      19:'Matthäus-Evangelium',
      20:'Markus-Evangelium',
      21:'Lukas-Evangelium',
      22:'Johannes-Evangelium',
      23:'Der alte Bund',
      24:'Der neue Bund'
    }
  },
  en: {
    app_title:         'Book of Evangelical Service',
    splash_subtitle:   'Elberfeld Bible 1905',
    splash_creator:    'by Mario Reiner Denzer',
    footer_credit:     'Creator \u0026 Copyright: Mario Reiner Denzer \u00b7 \u00a9 2025 \u00b7 Version 1.0.0',
    footer_bible:      'Bible text: Elberfeld 1905 (public domain)',
    a2hs_title:        '\ud83d\udcf1 Add App to Home Screen',
    a2hs_close_label:  'Close',
    a2hs: {
      android: {
        steps: [
          'Open this page in <strong>Chrome</strong> (or Samsung Internet) on your Android device.',
          'Tap the <strong>Menu ⋮</strong> (three dots in the top right).',
          'Select <strong>"Add to Home Screen"</strong> from the list.',
          'Tap <strong>"Add"</strong> in the confirmation dialog.',
          '✅ The <strong>✝ BDE icon</strong> appears on your home screen \u2013 the app opens like a native app!'
        ],
        note: '💡 Tip: In Samsung Internet, it is called "Add page to \u2192 Home Screen"'
      },
      iphone: {
        steps: [
          'Open this page in <strong>Safari</strong> on your iPhone or iPad.',
          'Tap the <strong>Share icon ⬆</strong> in the center bottom of the toolbar.',
          'Scroll down and tap <strong>"Add to Home Screen"</strong>.',
          'Tap <strong>"Add"</strong> in the top right.',
          '✅ The <strong>✝ BDE icon</strong> appears on your Home Screen!'
        ],
        note: '⚠ Only Safari supports "Add to Home Screen" on iPhone/iPad. Chrome iOS does not support this feature.'
      },
      desktop: {
        steps: [
          'Open this page in <strong>Chrome or Edge</strong> on your computer.',
          'Click the <strong>Install icon ⊕</strong> on the right side of the address bar (appears automatically).',
          'Click <strong>"Install"</strong> in the popup dialog.',
          '✅ The app opens in its <strong>own window</strong> without a browser bar \u2013 just like a program!'
        ],
        note: '💡 Alternative: Download the file <strong>BDE-Bibel.html</strong> and open it directly \u2013 works offline without installation.'
      }
    },
    splash_start:      '✝\u00a0\u00a0Open the Bible',
    install_btn:       '⬇\u00a0\u00a0Install App',
    save_offline_btn:  '💾\u00a0Save App as File (offline)',
    update_msg:        '🔄 New version available!',
    update_btn:        'Update now',
    update_btn_bar:    '↻ Update',
    install_bar:       '⬇ Install',
    offline_badge:     '📵 Offline',
    online_badge:      '✅ Online',
    search_placeholder:'Search Bible passages \u2026',
    search_hint:       'Enter search term \u2026',
    no_results:        'No results found.',
    loading:           '✝\u2005Loading data \u2026',
    all_books:         'All Books',
    tab_bible:         '📖 Bible',
    tab_themes:        '✝ Themes',
    search_title:      'Search',
    at_label:          'Old Testament (1\u201339)',
    nt_label:          'New Testament (40\u201366)',
    chapters_unit:     'Chapters',
    verses_unit:       'Verses',
    passages_unit:     'Passages',
    tg_ot:             'Old Testament – History',
    tg_psalms:         'Psalms & Prophecy',
    tg_bund:           'Covenant',
    tg_jesus:          'Jesus Christ',
    tg_gospels:        'The Four Gospels',
    tg_nt:             'Acts & Letters',
    thematic_header:   'Thematic Bible Passages',
    home_sub:          'Elberfelder 1905 \u00b7 66 Books \u00b7 31,102 Verses',
    passages:          'Passages',
    notes_title:       'My Comment',
    notes_placeholder: 'Comment, thoughts or notes about this Bible passage …',
    notes_save:        'Save',
    notes_clear:       'Clear',
    notes_saved:       '✔ saved',
    tab_notes:         '📝 Notes',
    notes_overview_empty: 'No notes yet.\nAdd comments in the Themes tab.',
    notes_goto:        '→ Go to Passage',
    notes_delete:      '🗑 Delete',
    notes_export:      '📤 Export All Notes',
    theme_names: {
      1:'Creation and Origin',
      2:'Patriarchs and Matriarchs of Israel',
      3:'The Exodus and Wilderness',
      4:'Law and Covenant',
      5:'Entry and Conquest of the Land',
      6:'The Time of the Judges',
      7:'Kings and Prophecy in Israel',
      8:'The Great Prophets Elijah and Elisha',
      9:'Psalms: Prayers and Songs',
      10:'Prophetic Books and Message',
      11:'Jesus Christ: Birth and Childhood',
      12:"Jesus' Ministry: Baptism, Temptation and Calling",
      13:'The Sermon on the Mount',
      14:'Parables of Jesus',
      15:'Miracles and Healings',
      16:'Passion and Resurrection of Jesus',
      17:'Acts of the Apostles and the Epistles',
      18:'The Revelation: Fulfillment',
      19:'Gospel of Matthew',
      20:'Gospel of Mark',
      21:'Gospel of Luke',
      22:'Gospel of John',
      23:'The Old Covenant',
      24:'The New Covenant'
    },
    passage_titles: {
      1:'The Creation of the World',2:'The Garden of Eden',3:'The Fall of Man',4:'Cain and Abel',5:'The Flood and Noah\'s Covenant',
      6:'God\'s Covenant with Abraham',7:'God Promises Abraham a Son',8:'Hagar and Ishmael',9:'The Covenant of Circumcision',10:'Abraham\'s Intercession for Sodom',
      11:'Sodom and Gomorrah',12:'The Birth of Isaac',13:'The Sacrifice of Isaac',14:'Finding a Bride for Isaac',15:'Esau and Jacob',
      16:'Isaac Blesses Jacob',17:'Jacob\'s Ladder',18:'Jacob at Laban\'s House',19:'Jacob Wrestles at Jabbok',20:'Jacob Reconciles with Esau',
      21:'Joseph\'s Dreams',22:'Joseph Sold into Egypt',23:'Joseph and Potiphar\'s Wife',24:'Joseph Interprets Pharaoh\'s Dreams',25:'Joseph Reconciles with His Brothers',
      26:'Moses\' Birth and Calling',27:'The Ten Plagues',28:'The Passover and the Exodus',29:'Crossing the Red Sea',30:'Manna in the Wilderness',
      31:'Water from the Rock',32:'The Battle against Amalek',33:'Revelation at Sinai and the Ten Commandments',34:'The Book of the Covenant',35:'The Covenant at Sinai',
      36:'The Golden Calf',37:'The Tabernacle',38:'The Aaronic Blessing',39:'The Spies in Canaan',40:'Moses Cannot Enter the Promised Land',
      41:'The Year of Release',42:'The Social Law',43:'The Greatest Commandment',44:'Blessings and Curses',45:'The New Covenant',
      46:'The Calling of Joshua',47:'Crossing the Jordan',48:'The Conquest of Jericho',49:'The Covenant at Shechem',50:'Deborah and Barak',
      51:'The Calling of Gideon',52:'Samson\'s Birth and Calling',53:'Samson and Delilah',54:'Ruth and Naomi',55:'Everyone Did What Was Right in Their Own Eyes',
      56:'The Birth of Samuel',57:'The Calling of Samuel',58:'The Demand for a King',59:'The Anointing of Saul',60:'The Anointing of David',
      61:'David and Goliath',62:'David\'s Friendship with Jonathan',63:'David Spares Saul',64:'David\'s Repentance after Adultery',65:'Absalom\'s Revolt and Death',
      66:'Solomon Asks for Wisdom',67:'The Judgment of Solomon',68:'The Building of the Temple',69:'The Queen of Sheba',70:'The Division of the Kingdom',
      71:'Elijah at the Brook and the Widow',72:'The Contest on Mount Carmel',73:'Elijah at Mount Horeb',74:'Naboth\'s Vineyard',75:'Elijah\'s Ascension',
      76:'Elisha and the Widow',77:'Elisha and the Shunammite',78:'The Healing of Naaman',79:'Jonah Flees from God',80:'Jonah in Nineveh',
      231:'The Song of Hannah',232:'Jonah\'s Song of Thanksgiving',233:'The Magnificat of Mary',234:'The Benedictus of Zechariah',235:'The Nunc Dimittis of Simeon',
      236:'The Calling of Isaiah',237:'The Song of the Vineyard',238:'The Sign of Immanuel',239:'A Child Is Born to Us',240:'Peace in the Kingdom of Peace',
      241:'Comfort for God\'s People',242:'The Servant of God',243:'The Calling of Jeremiah',244:'The Potter\'s Clay',245:'Jeremiah\'s Temple Sermon',
      246:'The Vision of the Valley of Dry Bones',247:'Belshazzar\'s Feast',248:'Daniel in the Lions\' Den',249:'Swords into Plowshares',250:'What the LORD Requires',
      251:'The Genealogy of Jesus',252:'The Wise Men from the East',253:'The Flight to Egypt',254:'The Announcement of Jesus\' Birth',255:'Mary\'s Visit to Elizabeth',
      256:'The Magnificat of Mary',257:'The Birth of John the Baptist',258:'The Birth of Jesus in Bethlehem',259:'Circumcision and Presentation in the Temple',260:'The Twelve-Year-Old Jesus in the Temple',
      261:'John the Baptist',262:'The Baptism of Jesus',263:'The Temptation of Jesus',264:'The Calling of the First Disciples',265:'The Calling of Matthew',
      266:'The Sending Out of the Twelve',267:'The Wedding at Cana',268:'The Samaritan Woman at the Well',269:'Jesus in Nazareth',270:'The Centurion of Capernaum',
      271:'The Beatitudes',272:'Salt and Light',273:'Jesus and the Law',274:'On Marriage and Divorce',275:'On Love for Enemies',
      276:'On Giving and Prayer',277:'The Lord\'s Prayer',278:'On Heavenly Treasures and Worry',279:'On Judging',280:'The Golden Rule and the House Builders',
      281:'The Sower',282:'The Weeds among the Wheat',283:'The Mustard Seed and the Yeast',284:'The Hidden Treasure and the Pearl',285:'The Workers in the Vineyard',
      286:'The Unforgiving Servant',287:'The Wise and Foolish Virgins',288:'The Parable of the Talents',289:'The Final Judgment',290:'The Wicked Tenants',
      291:'The Good Samaritan',292:'The Rich Fool',293:'The Lost Sheep and the Lost Coin',294:'The Prodigal Son',295:'The Dishonest Manager',
      296:'The Rich Man and Poor Lazarus',297:'The Pharisee and the Tax Collector',298:'The Great Banquet',299:'The Barren Fig Tree',
      300:'Calming the Storm',301:'The Healing of the Paralytic',302:'The Feeding of the Five Thousand',303:'Jesus Walks on Water',304:'The Bleeding Woman and Jairus\' Daughter',
      305:'The Healing of the Man Born Blind',306:'The Raising of Lazarus',307:'The Healing of the Gerasene Demoniac',308:'The Centurion\'s Servant',309:'The Healing of the Crippled Woman',
      310:'The Entry into Jerusalem',311:'The Cleansing of the Temple',312:'The Last Supper',313:'The Washing of Feet',314:'Jesus in Gethsemane',
      315:'The Arrest and Denial',316:'Jesus before Pilate and Herod',317:'The Crucifixion and Death of Jesus',318:'The Burial of Jesus',319:'The Empty Tomb',
      320:'The Appearance to Mary Magdalene',321:'The Road to Emmaus',322:'The Appearance to Thomas',323:'The Great Commission',324:'The Ascension',
      325:'Pentecost – Outpouring of the Holy Spirit',326:'The First Church in Jerusalem',327:'The Healing of the Lame Man',328:'The Stoning of Stephen',329:'The Conversion of Saul',
      330:'Paul\'s Areopagus Speech',331:'Justification by Faith',332:'Abraham\'s Faith',333:'Peace with God',334:'The New Man in Christ',
      335:'Life in the Spirit',336:'The Hymn of Love',337:'The Resurrection of the Dead',338:'The Fruits of the Spirit',339:'The Praise of Grace',
      340:'The Armor of God',341:'The Philippian Hymn',342:'I Can Do All Things through Christ',343:'The Colossian Hymn',344:'The Appearing of Grace',
      345:'Jesus the High Priest',346:'The Cloud of Witnesses',347:'Faith and Works',348:'God Resists the Proud',349:'The Patience of Job',
      350:'The New Birth',351:'The Royal Priesthood',352:'God Is Light',353:'The Mystery of Godliness',354:'The Calling of Timothy',
      355:'The Son of Man',356:'The Seven Letters to the Churches',357:'The Throne of God and the Lamb',358:'The New Jerusalem',359:'The Call: Yes, I Am Coming Soon',
      544:'God\'s Covenant with Abraham (Gen 15)',545:'Covenant of Circumcision (Gen 17)',546:'The Revelation at Sinai (Ex 19)',547:'The Ten Commandments (Ex 20)',548:'The Covenant at Sinai (Ex 24)',
      549:'The Sabbath as Covenant Sign (Ex 31)',550:'Renewal of the Covenant (Ex 34)',551:'The Holiness Code (Lev 19)',552:'Blessings and Curses of the Covenant (Lev 26)',553:'The Great Commandment (Deut 6)',
      554:'The Covenant Renewed: Curses (Deut 27)',555:'Blessings and Curses (Deut 28)',556:'The Covenant in Moab (Deut 29)',557:'Return and Promise (Deut 30)',558:'Covenant at Shechem (Josh 24)',
      559:'God\'s Covenant with David (2 Sam 7)',560:'Ps 89: Faithfulness to the Davidic Covenant',561:'The Broken Covenant (Jer 11)',562:'The New Covenant Promised (Jer 31:31-34)',
      563:'A New Heart (Ezek 36:22-32)',564:'The Old Covenant Is Fading (Heb 8)',565:'The Blood of the Covenant (Heb 9)',
      566:'The Promise of the New Covenant (Jer 31)',567:'A New Heart and a New Spirit (Ezek 36)',568:'The Institution of the Lord\'s Supper (Mt 26)',569:'You Must Be Born Again (John 3)',
      570:'The Holy Spirit as Comforter (John 14)',571:'The Spirit of Truth (John 16)',572:'Outpouring of the Holy Spirit (Acts 2)',573:'Life in the Spirit (Rom 8)',574:'Ministers of the New Covenant (2 Cor 3)',
      575:'Sons of Abraham by Faith (Gal 3)',576:'The Two Covenants (Gal 4:21-31)',577:'The Fullness of Grace (Eph 1)',578:'A Better Covenant (Heb 8)',579:'The Blood of the New Covenant (Heb 9)',
      580:'The Law Written on the Heart (Heb 10)',581:'Mount Zion and the New City (Heb 12)',582:'The New Jerusalem (Rev 21)',583:'I Am Coming Soon (Rev 22)'
    }
  },
  id: {
    app_title:         'Buku Pelayanan Penginjilan',
    splash_subtitle:   'Alkitab Elberfeld 1905',
    splash_creator:    'oleh Mario Reiner Denzer',
    footer_credit:     'Pencipta \u0026 Hak Cipta: Mario Reiner Denzer \u00b7 \u00a9 2025 \u00b7 Versi 1.0.0',
    footer_bible:      'Teks Alkitab: Elberfeld 1905 (domain publik)',
    a2hs_title:        '\ud83d\udcf1 Tambah Aplikasi ke Layar Beranda',
    a2hs_close_label:  'Tutup',
    a2hs: {
      android: {
        steps: [
          'Buka halaman ini di <strong>Chrome</strong> (atau Samsung Internet) pada perangkat Android Anda.',
          'Ketuk <strong>Menu ⋮</strong> (tiga titik di kanan atas).',
          'Pilih <strong>"Tambahkan ke Layar Utama"</strong> dari daftar.',
          'Ketuk <strong>"Tambah"</strong> pada dialog konfirmasi.',
          '✅ Ikon <strong>✝ BDE</strong> muncul di layar beranda Anda \u2013 aplikasi terbuka seperti aplikasi asli!'
        ],
        note: '💡 Tips: Di Samsung Internet, namanya "Tambahkan halaman ke \u2192 Layar Utama"'
      },
      iphone: {
        steps: [
          'Buka halaman ini di <strong>Safari</strong> pada iPhone atau iPad Anda.',
          'Ketuk <strong>ikon Bagikan ⬆</strong> di bagian bawah tengah bilah alat.',
          'Gulir ke bawah dan ketuk <strong>"Tambahkan ke Layar Utama"</strong>.',
          'Ketuk <strong>"Tambah"</strong> di kanan atas.',
          '✅ Ikon <strong>✝ BDE</strong> muncul di Layar Utama Anda!'
        ],
        note: '⚠ Hanya Safari yang mendukung "Tambahkan ke Layar Utama" di iPhone/iPad. Chrome iOS tidak mendukung fitur ini.'
      },
      desktop: {
        steps: [
          'Buka halaman ini di <strong>Chrome atau Edge</strong> di komputer Anda.',
          'Klik <strong>ikon Install ⊕</strong> di sisi kanan bilah alamat (muncul secara otomatis).',
          'Klik <strong>"Instal"</strong> pada dialog popup.',
          '✅ Aplikasi terbuka di <strong>jendela sendiri</strong> tanpa bilah browser \u2013 seperti sebuah program!'
        ],
        note: '💡 Alternatif: Unduh file <strong>BDE-Bibel.html</strong> dan buka langsung \u2013 berfungsi offline tanpa instalasi.'
      }
    },
    splash_start:      '✝\u00a0\u00a0Buka Alkitab',
    install_btn:       '⬇\u00a0\u00a0Pasang Aplikasi',
    save_offline_btn:  '💾\u00a0Simpan Aplikasi sebagai File (offline)',
    update_msg:        '🔄 Versi baru tersedia!',
    update_btn:        'Perbarui sekarang',
    update_btn_bar:    '↻ Perbarui',
    install_bar:       '⬇ Pasang',
    offline_badge:     '📵 Offline',
    online_badge:      '✅ Online',
    search_placeholder:'Cari ayat Alkitab \u2026',
    search_hint:       'Masukkan kata pencarian \u2026',
    no_results:        'Tidak ada hasil ditemukan.',
    loading:           '✝\u2005Memuat data \u2026',
    all_books:         'Semua Kitab',
    tab_bible:         '📖 Alkitab',
    tab_themes:        '✝ Topik',
    search_title:      'Cari',
    at_label:          'Perjanjian Lama (1\u201339)',
    nt_label:          'Perjanjian Baru (40\u201366)',
    chapters_unit:     'Pasal',
    verses_unit:       'Ayat',
    passages_unit:     'Bagian',
    tg_ot:             'Perjanjian Lama – Sejarah',
    tg_psalms:         'Mazmur & Nubuat',
    tg_bund:           'Perjanjian',
    tg_jesus:          'Yesus Kristus',
    tg_gospels:        'Empat Injil',
    tg_nt:             'Kisah Para Rasul & Surat',
    thematic_header:   'Ayat-Ayat Alkitab Tematik',
    home_sub:          'Elberfelder 1905 \u00b7 66 Kitab \u00b7 31.102 Ayat',
    passages:          'Bagian',
    notes_title:       'Komentar Saya',
    notes_placeholder: 'Komentar, pikiran atau catatan tentang bagian Alkitab ini …',
    notes_save:        'Simpan',
    notes_clear:       'Hapus',
    notes_saved:       '✔ tersimpan',
    tab_notes:         '📝 Catatan',
    notes_overview_empty: 'Belum ada catatan.\nTambahkan komentar di tab Topik.',
    notes_goto:        '→ Buka',
    notes_delete:      '🗑 Hapus',
    notes_export:      '📤 Ekspor Semua Catatan',
    theme_names: {
      1:'Penciptaan dan Asal Usul',
      2:'Bapa dan Ibu Israel',
      3:'Keluaran dari Mesir dan Padang Gurun',
      4:'Hukum dan Perjanjian',
      5:'Masuk dan Penaklukan Tanah',
      6:'Zaman Para Hakim',
      7:'Raja-Raja dan Nubuat di Israel',
      8:'Nabi-Nabi Besar Elia dan Elisa',
      9:'Mazmur: Doa dan Nyanyian',
      10:'Kitab-Kitab Nabi dan Pesannya',
      11:'Yesus Kristus: Kelahiran dan Masa Kecil',
      12:'Pelayanan Yesus: Baptisan, Pencobaan dan Panggilan',
      13:'Khotbah di Bukit',
      14:'Perumpamaan Yesus',
      15:'Mujizat dan Penyembuhan',
      16:'Sengsara dan Kebangkitan Yesus',
      17:'Kisah Para Rasul dan Surat-Surat',
      18:'Kitab Wahyu: Penggenapan',
      19:'Injil Matius',
      20:'Injil Markus',
      21:'Injil Lukas',
      22:'Injil Yohanes',
      23:'Perjanjian Lama',
      24:'Perjanjian Baru'
    },
    passage_titles: {
      1:'Penciptaan Dunia',2:'Taman Eden',3:'Kejatuhan Manusia',4:'Kain dan Habel',5:'Banjir dan Perjanjian Nuh',
      6:'Perjanjian Allah dengan Abraham',7:'Allah Berjanji Memberi Abraham Seorang Anak',8:'Hagar dan Ismael',9:'Perjanjian Sunat',10:'Doa Syafaat Abraham untuk Sodom',
      11:'Sodom dan Gomora',12:'Kelahiran Ishak',13:'Pengorbanan Ishak',14:'Mencari Istri untuk Ishak',15:'Esau dan Yakub',
      16:'Ishak Memberkati Yakub',17:'Tangga Yakub',18:'Yakub di Rumah Laban',19:'Yakub Bergumul di Sungai Yabok',20:'Yakub Berdamai dengan Esau',
      21:'Mimpi Yusuf',22:'Yusuf Dijual ke Mesir',23:'Yusuf dan Istri Potifar',24:'Yusuf Menafsirkan Mimpi Firaun',25:'Yusuf Berdamai dengan Saudara-Saudaranya',
      26:'Kelahiran dan Panggilan Musa',27:'Sepuluh Tulah',28:'Paskah dan Keluaran dari Mesir',29:'Menyeberangi Laut Merah',30:'Manna di Padang Gurun',
      31:'Air dari Batu Karang',32:'Perang Melawan Amalek',33:'Wahyu di Sinai dan Sepuluh Perintah',34:'Kitab Perjanjian',35:'Perjanjian di Sinai',
      36:'Anak Lembu Emas',37:'Kemah Suci',38:'Berkat Harun',39:'Pengintai di Kanaan',40:'Musa Tidak Boleh Masuk Tanah Perjanjian',
      41:'Tahun Pembebasan',42:'Hukum Sosial',43:'Perintah Utama',44:'Berkat dan Kutuk',45:'Perjanjian Baru',
      46:'Panggilan Yosua',47:'Menyeberangi Sungai Yordan',48:'Penaklukan Yerikho',49:'Perjanjian di Sikhem',50:'Debora dan Barak',
      51:'Panggilan Gideon',52:'Kelahiran dan Panggilan Simson',53:'Simson dan Delila',54:'Rut dan Naomi',55:'Setiap Orang Melakukan yang Benar di Matanya',
      56:'Kelahiran Samuel',57:'Panggilan Samuel',58:'Permintaan Raja',59:'Pengurapan Saul',60:'Pengurapan Daud',
      61:'Daud dan Goliat',62:'Persahabatan Daud dan Yonatan',63:'Daud Mengampuni Saul',64:'Pertobatan Daud setelah Dosa',65:'Pemberontakan dan Kematian Absalom',
      66:'Salomo Meminta Hikmat',67:'Keadilan Salomo',68:'Pembangunan Bait Allah',69:'Ratu Syeba',70:'Perpecahan Kerajaan',
      71:'Elia di Tepi Sungai dan Janda Sarfat',72:'Pertandingan di Gunung Karmel',73:'Elia di Gunung Horeb',74:'Kebun Anggur Nabot',75:'Pengangkatan Elia',
      76:'Elisa dan Janda',77:'Elisa dan Perempuan Sunem',78:'Penyembuhan Naaman',79:'Yunus Melarikan Diri dari Allah',80:'Yunus di Niniwe',
      231:'Nyanyian Hana',232:'Nyanyian Syukur Yunus',233:'Magnificat Maria',234:'Benediktus Zakharia',235:'Nunc Dimittis Simeon',
      236:'Panggilan Yesaya',237:'Nyanyian Kebun Anggur',238:'Tanda Imanuel',239:'Seorang Anak Lahir bagi Kita',240:'Damai dalam Kerajaan Damai',
      241:'Penghiburan bagi Umat Allah',242:'Hamba Tuhan',243:'Panggilan Yeremia',244:'Tanah Liat di Tangan Penjunan',245:'Khotbah di Bait Allah',
      246:'Penglihatan Lembah Tulang-Belulang Kering',247:'Pesta Belsazar',248:'Daniel di Gua Singa',249:'Pedang menjadi Mata Bajak',250:'Apa yang Dikehendaki Tuhan',
      251:'Silsilah Yesus',252:'Orang Majus dari Timur',253:'Pengungsian ke Mesir',254:'Pengumuman Kelahiran Yesus',255:'Kunjungan Maria kepada Elisabet',
      256:'Magnificat Maria',257:'Kelahiran Yohanes Pembaptis',258:'Kelahiran Yesus di Betlehem',259:'Sunat dan Penyajian di Bait Allah',260:'Yesus yang Berusia Dua Belas Tahun di Bait Allah',
      261:'Yohanes Pembaptis',262:'Baptisan Yesus',263:'Pencobaan Yesus',264:'Panggilan Murid-Murid Pertama',265:'Panggilan Matius',
      266:'Pengutusan Dua Belas Murid',267:'Pernikahan di Kana',268:'Perempuan Samaria di Sumur',269:'Yesus di Nazaret',270:'Perwira di Kapernaum',
      271:'Ucapan Bahagia',272:'Garam dan Terang',273:'Yesus dan Hukum Taurat',274:'Tentang Perkawinan dan Perceraian',275:'Tentang Mengasihi Musuh',
      276:'Tentang Memberi dan Berdoa',277:'Doa Bapa Kami',278:'Tentang Harta Surgawi dan Kecemasan',279:'Tentang Menghakimi',280:'Aturan Emas dan Pembangunan Rumah',
      281:'Penabur',282:'Lalang di antara Gandum',283:'Biji Sesawi dan Ragi',284:'Harta Tersembunyi dan Mutiara Berharga',285:'Pekerja di Kebun Anggur',
      286:'Hamba yang Tidak Mengampuni',287:'Gadis-Gadis Bijaksana dan Bodoh',288:'Perumpamaan tentang Talenta',289:'Penghakiman Terakhir',290:'Penggarap-Penggarap yang Jahat',
      291:'Orang Samaria yang Baik Hati',292:'Orang Kaya yang Bodoh',293:'Domba yang Hilang dan Koin yang Hilang',294:'Anak yang Hilang',295:'Bendahara yang Tidak Jujur',
      296:'Orang Kaya dan Lazarus yang Miskin',297:'Orang Farisi dan Pemungut Cukai',298:'Perjamuan Besar',299:'Pohon Ara yang Tidak Berbuah',
      300:'Meredakan Angin Ribut',301:'Penyembuhan Orang Lumpuh',302:'Pemberian Makan Lima Ribu Orang',303:'Yesus Berjalan di atas Air',304:'Perempuan Sakit Pendarahan dan Anak Yairus',
      305:'Penyembuhan Orang yang Lahir Buta',306:'Kebangkitan Lazarus',307:'Penyembuhan Orang Kerasukan di Gerasa',308:'Penyembuhan Hamba Perwira',309:'Penyembuhan Perempuan yang Bungkuk',
      310:'Masuk ke Yerusalem',311:'Pembersihan Bait Allah',312:'Perjamuan Malam Terakhir',313:'Pembasuhan Kaki',314:'Yesus di Taman Getsemani',
      315:'Penangkapan dan Penyangkalan',316:'Yesus di Hadapan Pilatus dan Herodes',317:'Penyaliban dan Kematian Yesus',318:'Penguburan Yesus',319:'Kubur yang Kosong',
      320:'Penampakan kepada Maria Magdalena',321:'Perjalanan ke Emaus',322:'Penampakan kepada Tomas',323:'Amanat Agung',324:'Kenaikan ke Surga',
      325:'Pentakosta – Pencurahan Roh Kudus',326:'Jemaat Pertama di Yerusalem',327:'Penyembuhan Orang Lumpuh',328:'Penganiayaan Stefanus',329:'Pertobatan Saulus',
      330:'Pidato Paulus di Areopagus',331:'Pembenaran oleh Iman',332:'Iman Abraham',333:'Damai dengan Allah',334:'Manusia Baru dalam Kristus',
      335:'Hidup dalam Roh',336:'Hymne Kasih',337:'Kebangkitan Orang Mati',338:'Buah-Buah Roh',339:'Pujian atas Kasih Karunia',
      340:'Perlengkapan Senjata Allah',341:'Hymne Filipi',342:'Aku Dapat Menanggung Segala Sesuatu melalui Kristus',343:'Hymne Kolose',344:'Penampakan Kasih Karunia',
      345:'Yesus Imam Besar',346:'Awan Saksi-Saksi',347:'Iman dan Perbuatan',348:'Allah Menentang Orang yang Sombong',349:'Kesabaran Ayub',
      350:'Kelahiran Baru',351:'Imamat yang Rajani',352:'Allah adalah Terang',353:'Rahasia Kesalehan',354:'Panggilan Timotius',
      355:'Anak Manusia',356:'Tujuh Surat kepada Jemaat',357:'Takhta Allah dan Anak Domba',358:'Yerusalem Baru',359:'Seruan: Ya, Aku Datang Segera',
      544:'Perjanjian Allah dengan Abraham (Kej 15)',545:'Perjanjian Sunat (Kej 17)',546:'Wahyu di Sinai (Kel 19)',547:'Sepuluh Perintah (Kel 20)',548:'Perjanjian di Sinai (Kel 24)',
      549:'Sabat sebagai Tanda Perjanjian (Kel 31)',550:'Pembaruan Perjanjian (Kel 34)',551:'Hukum Kekudusan (Im 19)',552:'Berkat dan Kutuk Perjanjian (Im 26)',553:'Perintah Utama (Ul 6)',
      554:'Perjanjian Diperbarui: Kutuk (Ul 27)',555:'Berkat dan Kutuk (Ul 28)',556:'Perjanjian di Moab (Ul 29)',557:'Pertobatan dan Janji (Ul 30)',558:'Perjanjian di Sikhem (Yos 24)',
      559:'Perjanjian Allah dengan Daud (2 Sam 7)',560:'Maz 89: Kesetiaan pada Perjanjian Daud',561:'Perjanjian yang Dilanggar (Yer 11)',562:'Janji Perjanjian Baru (Yer 31:31-34)',
      563:'Hati yang Baru (Yeh 36:22-32)',564:'Perjanjian Lama Pudar (Ibr 8)',565:'Darah Perjanjian (Ibr 9)',
      566:'Janji Perjanjian Baru (Yer 31)',567:'Hati Baru dan Roh Baru (Yeh 36)',568:'Penetapan Perjamuan Tuhan (Mat 26)',569:'Kamu Harus Dilahirkan Kembali (Yoh 3)',
      570:'Roh Kudus sebagai Penghibur (Yoh 14)',571:'Roh Kebenaran (Yoh 16)',572:'Pencurahan Roh Kudus (Kis 2)',573:'Hidup dalam Roh (Rom 8)',574:'Pelayan Perjanjian Baru (2 Kor 3)',
      575:'Anak-Anak Abraham melalui Iman (Gal 3)',576:'Dua Perjanjian (Gal 4:21-31)',577:'Kelimpahan Kasih Karunia (Ef 1)',578:'Perjanjian yang Lebih Baik (Ibr 8)',579:'Darah Perjanjian Baru (Ibr 9)',
      580:'Hukum Tertulis di Hati (Ibr 10)',581:'Gunung Sion dan Kota Baru (Ibr 12)',582:'Yerusalem Baru (Why 21)',583:'Aku Datang Segera (Why 22)'
    }
  }
};

let CURRENT_LANG = 'de';
function t(key) {
  var lx = LANG[CURRENT_LANG] || LANG.de;
  return lx[key] !== undefined ? lx[key] : (LANG.de[key] || key);
}
function tTheme(id) {
  var lx = LANG[CURRENT_LANG] || LANG.de;
  return (lx.theme_names && lx.theme_names[id]) ||
         (LANG.de.theme_names && LANG.de.theme_names[id]) || '';
}
// Return a passage title in the current language.
// – Gospel chapter themes (19–22): generate dynamically from translated book name + chapter
// – Psalms (book 19, same chapter_from/to): "Psalm N" (EN) / "Mazmur N" (ID)
// – All others: look up passage_titles dict, fall back to German p.title
function tPassage(p) {
  if (p.theme_id >= 19 && p.theme_id <= 22) {
    return (BOOKS[p.book_id] || '') + '\u2002' + p.chapter_from;
  }
  if (p.book_id === 19 && p.chapter_from === p.chapter_to) {
    var n = p.chapter_from;
    if (CURRENT_LANG === 'id') return 'Mazmur ' + n;
    if (CURRENT_LANG === 'en') return 'Psalm ' + n;
    return p.title;
  }
  var lx = LANG[CURRENT_LANG] || LANG.de;
  return (lx.passage_titles && lx.passage_titles[p.id]) || p.title;
}
function applyLang() {
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });
  document.getElementById('loading').textContent = t('loading');
  renderA2HS();
}
function renderA2HS() {
  var lx = LANG[CURRENT_LANG] || LANG.de;
  var a2hs = lx.a2hs || LANG.de.a2hs;
  if (!a2hs) return;
  function buildPanel(id, data) {
    var el = document.getElementById(id);
    if (!el) return;
    var html = (data.steps || []).map(function(s, i) {
      return '<div class="a2hs-step"><div class="a2hs-num">'+(i+1)+'</div><div class="a2hs-step-text">'+s+'</div></div>';
    }).join('');
    if (data.note) html += '<div class="a2hs-note">'+data.note+'</div>';
    el.innerHTML = html;
  }
  buildPanel('panel-android', a2hs.android);
  buildPanel('panel-iphone',  a2hs.iphone);
  buildPanel('panel-desktop', a2hs.desktop);
  var titleEl = document.querySelector('.a2hs-title');
  if (titleEl) titleEl.textContent = t('a2hs_title');
  var closeBtn = document.getElementById('a2hs-close-btn');
  if (closeBtn) closeBtn.setAttribute('aria-label', t('a2hs_close_label'));
}
function setLang(lang) {
  CURRENT_LANG = lang;
  try { localStorage.setItem('bde_lang', lang); } catch(e) {}
  document.getElementById('lang-screen').style.display = 'none';
  applyLang();
  // Reload Bible data for the selected language and re-render home
  if (ALL_DATA) { loadLangData(lang); renderHome(); }
  // Go directly into the app — no second tap on "Zur Bibel" needed
  closeSplash();
}
function changeLang() {
  try { localStorage.removeItem('bde_lang'); } catch(e) {}
  document.getElementById('lang-screen').style.display = 'flex';
}

// ── Load per-language Bible data from the multilingual payload ────────────
function loadLangData(lang) {
  var langBooks  = (ALL_DATA.books  && ALL_DATA.books[lang])  || ALL_DATA.books  || {};
  var langVerses = (ALL_DATA.verses && ALL_DATA.verses[lang]) || ALL_DATA.verses || [];
  BOOKS  = langBooks;
  VERSES = langVerses;
  IDX    = {};
  VERSES.forEach(function(row) {
    var b = row[0], c = row[1];
    if (!IDX[b])    IDX[b]    = {};
    if (!IDX[b][c]) IDX[b][c] = [];
    IDX[b][c].push(row);
  });
}

// ── Splash ────────────────────────────────────────────────────
function closeSplash() {
  document.getElementById('splash').style.display = 'none';
  // Safety net: re-render themes in case DOM wasn't ready during init()
  renderHome();
}

// ── Theme groups ─────────────────────────────────────────────
// Must be declared BEFORE the init() IIFE to avoid temporal dead zone.
const THEME_GROUPS = [
  ['tg_ot',       [1,2,3,4,5,6,7,8]],
  ['tg_psalms',   [9,10]],
  ['tg_bund',     [23,24]],
  ['tg_jesus',    [11,12,13,14,15,16]],
  ['tg_gospels',  [19,20,21,22]],
  ['tg_nt',       [17,18]],
];

// ── Christian SVG icons for theme cards ──────────────────────
// Each value is a complete inline SVG (36×36 viewBox, gold stroke).
// Single Bible-book-with-cross icon used for all theme cards
const BIBLE_CROSS_SVG = '<svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="3" width="28" height="30" rx="3" stroke="#c9a227" stroke-width="2"/><line x1="4" y1="3" x2="4" y2="33" stroke="#c9a227" stroke-width="4" stroke-linecap="round"/><line x1="16" y1="11" x2="16" y2="25" stroke="#c9a227" stroke-width="2.2" stroke-linecap="round"/><line x1="10" y1="17" x2="22" y2="17" stroke="#c9a227" stroke-width="2.2" stroke-linecap="round"/></svg>';
function themeIcon(_key) {
  return BIBLE_CROSS_SVG;
}


// ── Bootstrap ─────────────────────────────────────────────────
(function init() {
  // Restore saved language; hide lang-screen if already chosen
  var savedLang = null;
  try { savedLang = localStorage.getItem('bde_lang'); } catch(e) {}
  var langAlreadySaved = !!(savedLang && LANG[savedLang]);
  if (langAlreadySaved) {
    CURRENT_LANG = savedLang;
    document.getElementById('lang-screen').style.display = 'none';
  }
  applyLang();
  try {
    const binStr = atob(PAYLOAD_B64);
    const bytes  = new Uint8Array(binStr.length);
    for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
    // pako.inflate works on ALL browsers (Android WebView, old Chrome, old Safari)
    const decompressed = pako.inflate(bytes);
    const data = JSON.parse(new TextDecoder().decode(decompressed));
    ALL_DATA = data;
    loadLangData(CURRENT_LANG);
    document.getElementById('loading').style.display = 'none';
    showView('view-home');
    renderHome();
    // If language was already saved (returning user or after SW update),
    // skip the splash screen entirely — go straight into the app.
    if (langAlreadySaved) { closeSplash(); }
  } catch (err) {
    var loadEl = document.getElementById('loading');
    loadEl.style.display = 'block';
    loadEl.innerHTML =
      '<b style="color:#c00">Fehler:</b> ' + escHtml(err.message) +
      '<br><small>Bitte die Seite neu laden. Bei Problemen: Browser-Cache leeren.</small>';
  }
})();

// ── Navigation ────────────────────────────────────────────────
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const isRoot = (id === 'view-home');
  document.getElementById('back-btn').style.display      = isRoot ? 'none' : 'block';
  document.getElementById('search-toggle').style.display = (id === 'view-search') ? 'none' : 'block';
  document.getElementById('search-bar').style.display    = (id === 'view-search') ? 'block' : 'none';
  if (isRoot) {
    document.getElementById('app-bar').style.background = '';
    document.getElementById('app-title').textContent = APP_BAR_TITLE;
  }
}
function navigate(viewId) {
  navHistory.push(document.querySelector('.view.active').id);
  showView(viewId);
}
function goBack() {
  if (!navHistory.length) return;
  showView(navHistory.pop());
}
function goHome() {
  navHistory = [];
  showView('view-home');
}

// ── Helpers ───────────────────────────────────────────────────
// Convert "#rrggbb" to "rgba(r,g,b,a)" – avoids 8-digit hex which
// isn't supported on old Android WebView / Samsung Internet.
function hexFade(hex, a) {
  a = a === undefined ? 0.75 : a;
  var r = parseInt(hex.slice(1,3),16);
  var g = parseInt(hex.slice(3,5),16);
  var b = parseInt(hex.slice(5,7),16);
  return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
}

// ── Home ──────────────────────────────────────────────────────
let _homeTab = 'themes';
function switchHomeTab(tab) {
  _homeTab = tab;
  document.getElementById('panel-bible').classList.toggle('active', tab === 'bible');
  document.getElementById('panel-themes').classList.toggle('active', tab === 'themes');
  document.getElementById('panel-notes').classList.toggle('active', tab === 'notes');
  document.getElementById('tab-btn-bible').classList.toggle('active', tab === 'bible');
  document.getElementById('tab-btn-themes').classList.toggle('active', tab === 'themes');
  document.getElementById('tab-btn-notes').classList.toggle('active', tab === 'notes');
  if (tab === 'notes') renderNotesTab();
}
function renderHome() {
  const grid = document.getElementById('theme-grid');
  if (!PASSAGE_DATA || !PASSAGE_DATA.themes || !PASSAGE_DATA.themes.length) {
    grid.innerHTML = '<p style="padding:20px;color:#888">Keine Themen verfügbar.</p>';
  } else {
    // Update home header sub-text with translated stats
    const homeSub = document.querySelector('.home-sub');
    if (homeSub) homeSub.textContent = t('home_sub');
    // Build a map: theme_id → theme object + color index
    const themeMap = {};
    PASSAGE_DATA.themes.forEach((th, i) => { themeMap[th.id] = {th, i}; });
    let html = '';
    THEME_GROUPS.forEach(([labelKey, ids]) => {
      html += `<div class="theme-group-header">${escHtml(t(labelKey))}</div>`;
      ids.forEach(tid => {
        const entry = themeMap[tid];
        if (!entry) return;
        const {th, i} = entry;
        const color = THEME_COLORS[i % THEME_COLORS.length];
        const count = PASSAGE_DATA.passages.filter(p => p.theme_id === th.id).length;
        const name  = tTheme(th.id) || escHtml(th.name);
        html += `<div class="theme-card" data-tid="${th.id}" data-color="${color}"
                      style="background:linear-gradient(135deg,${color},${hexFade(color)})">
                   <span class="theme-icon">${themeIcon(escHtml(th.icon))}</span>
                   <span class="theme-name">${escHtml(name)}</span>
                   <span class="theme-count">${count} ${t('passages_unit')}</span>
                 </div>`;
      });
    });
    grid.innerHTML = html;
    grid.onclick = e => {
      const el = e.target.closest('[data-tid]');
      if (el) openTheme(Number(el.dataset.tid), el.dataset.color);
    };
  }
  // Update tab labels
  const btnThemes = document.getElementById('tab-btn-themes');
  const btnBible  = document.getElementById('tab-btn-bible');
  const btnNotes  = document.getElementById('tab-btn-notes');
  if (btnThemes) btnThemes.textContent = t('tab_themes');
  if (btnBible)  btnBible.textContent  = t('tab_bible');
  if (btnNotes)  btnNotes.textContent  = t('tab_notes');
  // Render inline book list in Bible tab
  renderHomeBibleTab();
}
function renderHomeBibleTab() {
  const list = document.getElementById('home-book-list');
  if (!list || !BOOKS) return;
  const AT_LABEL = '<div class="section-header" style="grid-column:1/-1">' + escHtml(t('at_label')) + '</div>';
  const NT_LABEL = '<div class="section-header" style="grid-column:1/-1">' + escHtml(t('nt_label')) + '</div>';
  let html = '<div class="book-grid">' + AT_LABEL;
  Object.entries(BOOKS).forEach(([id, name]) => {
    const bookId = Number(id);
    const chs    = Object.keys(IDX[bookId] || {}).length;
    if (bookId === 40) html += NT_LABEL;
    html += `<button class="book-btn" data-book="${bookId}">
               <span class="book-btn-num">${bookId}</span>
               <span class="book-btn-name">${escHtml(name)}</span>
               <span class="book-btn-chs">${chs} ${t('chapters_unit')}</span>
             </button>`;
  });
  html += '</div>';
  list.innerHTML = html;
  list.onclick = e => {
    const el = e.target.closest('[data-book]');
    if (el) openBook(Number(el.dataset.book));
  };
}

// ── Notes overview ─────────────────────────────────────────────
function renderNotesTab() {
  const container = document.getElementById('notes-overview');
  if (!container) return;
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem('bde_notes_v1') || '{}'); } catch(e) {}
  const keys = Object.keys(stored).filter(k => stored[k] && stored[k].trim());
  if (!keys.length) {
    container.innerHTML = '<p style="padding:24px 16px;color:var(--gold);white-space:pre-line;text-align:center">'
      + escHtml(t('notes_overview_empty')) + '</p>';
    return;
  }
  // Group by theme
  const groups = {};
  keys.forEach(pid => {
    const p = PASSAGE_DATA.passages.find(pp => pp.id === Number(pid));
    if (!p) return;
    const th = PASSAGE_DATA.themes.find(t2 => t2.id === p.theme_id);
    const groupName = th ? (tTheme(th.id) || th.name) : '—';
    if (!groups[groupName]) groups[groupName] = [];
    groups[groupName].push({p, note: stored[pid]});
  });
  let html = '';
  // Export button
  html += `<div style="padding:12px 16px 4px">
    <button onclick="exportNotes()" style="background:rgba(201,162,39,.15);border:1px solid var(--gold);
      color:var(--gold);border-radius:8px;padding:8px 16px;font-size:13px;cursor:pointer">
      ${escHtml(t('notes_export'))}
    </button>
  </div>`;
  Object.entries(groups).forEach(([groupName, entries]) => {
    html += `<div class="section-header" style="margin:12px 0 4px">${escHtml(groupName)}</div>`;
    entries.forEach(({p, note}) => {
      const preview = note.length > 120 ? note.slice(0,120) + '…' : note;
      html += `<div class="list-item" style="align-items:flex-start;flex-direction:column;gap:6px;padding:12px 16px">
        <div style="font-weight:600;color:var(--gold);font-size:14px">${escHtml(tPassage(p))}</div>
        <div style="font-size:13px;color:#d4c9a0;white-space:pre-wrap;line-height:1.5">${escHtml(preview)}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button data-goto="${p.id}" style="background:var(--gold);color:var(--navy);
            border:none;border-radius:6px;padding:5px 12px;font-size:12px;cursor:pointer">
            ${escHtml(t('notes_goto'))}
          </button>
          <button data-delnote="${p.id}" style="background:transparent;border:1px solid #c04;
            color:#e06060;border-radius:6px;padding:5px 12px;font-size:12px;cursor:pointer">
            ${escHtml(t('notes_delete'))}
          </button>
        </div>
      </div>`;
    });
  });
  container.innerHTML = html;
  container.onclick = e => {
    const goBtn  = e.target.closest('[data-goto]');
    const delBtn = e.target.closest('[data-delnote]');
    if (goBtn)  { openPassage(Number(goBtn.dataset.goto)); }
    if (delBtn) {
      const pid = delBtn.dataset.delnote;
      try { const n = JSON.parse(localStorage.getItem('bde_notes_v1')||'{}'); delete n[pid]; localStorage.setItem('bde_notes_v1', JSON.stringify(n)); } catch(e2){}
      renderNotesTab();
    }
  };
}
function exportNotes() {
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem('bde_notes_v1') || '{}'); } catch(e) {}
  const lines = [];
  Object.keys(stored).forEach(pid => {
    if (!stored[pid] || !stored[pid].trim()) return;
    const p = PASSAGE_DATA.passages.find(pp => pp.id === Number(pid));
    const title = p ? tPassage(p) : 'Passage ' + pid;
    lines.push('[' + title + ']\\n' + stored[pid] + '\\n');
  });
  if (!lines.length) return;
  const blob = new Blob([lines.join('\\n')], {type:'text/plain;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'BDE-Notizen.txt';
  a.click();
  URL.revokeObjectURL(a.href);
}

// ── Passage list ──────────────────────────────────────────────
function openTheme(themeId, color) {
  currentThemeColor = color;
  const theme    = PASSAGE_DATA.themes.find(th => th.id === themeId);
  const passages = PASSAGE_DATA.passages.filter(p => p.theme_id === themeId);
  const themeName = tTheme(themeId) || (theme ? theme.name : t('passages'));
  document.getElementById('app-title').textContent =
    theme ? themeName : t('passages');
  document.getElementById('app-bar').style.background = color;
  const list = document.getElementById('passage-list');
  list.innerHTML = passages.map((p, i) =>
    `<div class="list-item" data-pid="${p.id}">
       <div class="avatar" style="background:${color};border-color:var(--gold)">${i + 1}</div>
       <div class="list-item-text">
         <div class="list-item-title">${escHtml(tPassage(p))}</div>
         <div class="list-item-ref">${escHtml(refString(p))}</div>
       </div>
       <span style="color:var(--gold)">›</span>
     </div>`
  ).join('');
  list.onclick = e => {
    const el = e.target.closest('[data-pid]');
    if (el) openPassage(Number(el.dataset.pid));
  };
  navigate('view-passages');
}

function refString(p) {
  const bName = BOOKS[p.book_id] || '?';
  return p.chapter_from === p.chapter_to
    ? `${bName} ${p.chapter_from},${p.verse_from}\u2013${p.verse_to}`
    : `${bName} ${p.chapter_from},${p.verse_from} \u2013 ${p.chapter_to},${p.verse_to}`;
}

// ── Passage text ──────────────────────────────────────────────
function openPassage(passageId) {
  const p = PASSAGE_DATA.passages.find(x => x.id === passageId);
  if (!p) return;
  document.getElementById('app-title').textContent = tPassage(p);
  let html = '', lastChap = null;
  versesForPassage(p).forEach(([b, c, v, t]) => {
    if (c !== lastChap) {
      html += `<div class="chapter-heading">${escHtml((BOOKS[b] || '?') + ' ' + c)}</div>`;
      lastChap = c;
    }
    html += `<div class="verse-row" data-vkey="${b}:${c}:${v}" onclick="hlTap(event,this)"><sup class="verse-num">${v}</sup><span class="vtext${t.startsWith('[Ayat') ? ' verse-merged' : ''}" data-plain="${escHtmlAttr(t)}">${escHtml(t)}</span></div>`;
  });
  const ptEl = document.getElementById('passage-text');
  ptEl.innerHTML = html || '<div class="empty">Keine Verse gefunden.</div>';
  applyStoredHL(ptEl);
  applyAllWordHL();
  loadNotes(passageId);
  navigate('view-text');
}

function versesForPassage(p) {
  const result = [];
  const { book_id: b, chapter_from: cf, verse_from: vf, chapter_to: ct, verse_to: vt } = p;
  VERSES.forEach(row => {
    const [rb, rc, rv] = row;
    if (rb !== b)          return;
    if (rc < cf || rc > ct) return;
    if (rc === cf && rv < vf) return;
    if (rc === ct && rv > vt) return;
    result.push(row);
  });
  return result;
}

// ── All books ─────────────────────────────────────────────────
function openAllBooks() {
  document.getElementById('app-bar').style.background = '';
  document.getElementById('app-title').textContent = t('all_books');
  const list     = document.getElementById('book-list');
  const AT_LABEL = '<div class="section-header">' + escHtml(t('at_label')) + '</div>';
  const NT_LABEL = '<div class="section-header">' + escHtml(t('nt_label')) + '</div>';
  list.innerHTML = AT_LABEL + Object.entries(BOOKS).map(([id, name]) => {
    const bookId = Number(id);
    const chs    = Object.keys(IDX[bookId] || {}).length;
    const vs     = Object.values(IDX[bookId] || {}).reduce((s, a) => s + a.length, 0);
    const divider = bookId === 40 ? NT_LABEL : '';
    return divider +
      `<div class="list-item" data-book="${id}">
         <div class="avatar">${id}</div>
         <div class="list-item-text">
           <div class="list-item-title">${escHtml(name)}</div>
           <div class="list-item-ref">${chs} ${t('chapters_unit')} \u00b7 ${vs} ${t('verses_unit')}</div>
         </div>
         <span style="color:var(--gold)">\u203a</span>
       </div>`;
  }).join('');
  list.onclick = e => {
    const el = e.target.closest('[data-book]');
    if (el) openBook(Number(el.dataset.book));
  };
  navigate('view-books');
}

function openBook(bookId) {
  const chapters = Object.keys(IDX[bookId] || {}).map(Number).sort((a, b) => a - b);
  const grid = document.getElementById('chapter-grid');
  grid.innerHTML =
    `<div class="section-header" style="grid-column:1/-1">` +
      `${escHtml(BOOKS[bookId] || '')} \u00b7 ${chapters.length} ${t('chapters_unit')}` +
    `</div>` +
    chapters.map(c => {
      const vs = (IDX[bookId][c] || []).length;
      return `<button class="chapter-btn" data-book="${bookId}" data-ch="${c}" title="${vs} ${t('verses_unit')}">${c}</button>`;
    }).join('');
  grid.onclick = e => {
    const el = e.target.closest('[data-ch]');
    if (el) openChapter(Number(el.dataset.book), Number(el.dataset.ch));
  };
  document.getElementById('app-title').textContent = BOOKS[bookId] || '';
  navigate('view-chapters');
}

// ── Verses ────────────────────────────────────────────────────
function openChapter(bookId, chapter) {
  const rows = (IDX[bookId] || {})[chapter] || [];
  const vlEl = document.getElementById('verse-list');
  vlEl.innerHTML = rows.map(([b, c, v, t]) =>
    `<div class="verse-row" data-vkey="${b}:${c}:${v}" onclick="hlTap(event,this)"><sup class="verse-num">${v}</sup><span class="vtext${t.startsWith('[Ayat') ? ' verse-merged' : ''}" data-plain="${escHtmlAttr(t)}">${escHtml(t)}</span></div>`
  ).join('');
  applyStoredHL(vlEl);
  applyAllWordHL();
  document.getElementById('app-title').textContent = `${BOOKS[bookId] || ''} ${chapter}`;
  navigate('view-verses');
}

// ── Search ────────────────────────────────────────────────────
function showSearch() {
  document.getElementById('app-bar').style.background = '';
  document.getElementById('app-title').textContent = t('search_title');
  navigate('view-search');
  document.getElementById('search-input').focus();
  document.getElementById('search-results').innerHTML =
    '<div class="empty">' + escHtml(t('search_hint')) + '</div>';
}
function onSearchInput(val) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => runSearch(val), 300);
}
function runSearch(raw) {
  const q = raw.trim();
  const container = document.getElementById('search-results');
  if (!q) { container.innerHTML = '<div class="empty">' + escHtml(t('search_hint')) + '</div>'; return; }
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  const results = [];
  for (const row of VERSES) {
    if (terms.every(term => row[3].toLowerCase().includes(term))) {
      results.push(row);
      if (results.length >= 60) break;
    }
  }
  if (!results.length) {
    container.innerHTML = '<div class="empty">' + escHtml(t('no_results')) + '</div>';
    return;
  }
  container.innerHTML = results.map(([b, c, v, text]) =>
    `<div class="result-item" data-book="${b}" data-ch="${c}">
       ${highlightTerms(text, terms)}
       <div class="result-ref">${escHtml(BOOKS[b] || '?')} ${c},${v}</div>
     </div>`
  ).join('');
  container.onclick = e => {
    const el = e.target.closest('[data-ch]');
    if (el) openChapter(Number(el.dataset.book), Number(el.dataset.ch));
  };
}

// ── Helpers ───────────────────────────────────────────────────
function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function escHtmlAttr(s) {
  // Identical to escHtml — all five HTML special chars must be escaped in attribute values
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function escRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function highlightTerms(text, terms) {
  const ranges = [];
  terms.forEach(term => {
    const re = new RegExp(escRegex(term), 'gi');
    let m;
    while ((m = re.exec(text)) !== null) ranges.push([m.index, m.index + m[0].length]);
  });
  if (!ranges.length) return escHtml(text);
  ranges.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const merged = [ranges[0]];
  for (let i = 1; i < ranges.length; i++) {
    const last = merged[merged.length - 1];
    if (ranges[i][0] < last[1]) last[1] = Math.max(last[1], ranges[i][1]);
    else merged.push(ranges[i]);
  }
  let html = '', pos = 0;
  merged.forEach(([s, e]) => {
    html += escHtml(text.slice(pos, s));
    html += '<mark>' + escHtml(text.slice(s, e)) + '</mark>';
    pos = e;
  });
  return html + escHtml(text.slice(pos));
}

// ── Word-level Highlighting ───────────────────────────────────
const WORD_HL_KEY = 'bde_whl_v1';
let WORD_HL_STORE = {};
try { WORD_HL_STORE = JSON.parse(localStorage.getItem(WORD_HL_KEY) || '{}'); } catch(e) { WORD_HL_STORE = {}; }

function saveWordHL() {
  try { localStorage.setItem(WORD_HL_KEY, JSON.stringify(WORD_HL_STORE)); } catch(e) {}
}

/* Get character offset of (node, offset) within a root element's text */
function getTextOffset(root, targetNode, targetOffset) {
  let total = 0;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
  let node;
  while ((node = walker.nextNode())) {
    if (node === targetNode) return total + targetOffset;
    total += node.textContent.length;
  }
  return -1;
}

/* Re-render a .vtext span inserting <mark> tags for stored word highlights */
function reRenderVText(vtext, vkey) {
  const text = vtext.dataset.plain || vtext.textContent;
  const ranges = (WORD_HL_STORE[vkey] || []).slice().sort(function(a,b){ return a.start - b.start; });
  if (!ranges.length) { vtext.innerHTML = escHtml(text); return; }
  let result = '', pos = 0;
  for (let i = 0; i < ranges.length; i++) {
    const {start, end, color} = ranges[i];
    const s = Math.max(start, pos), e = Math.min(end, text.length);
    if (s >= e) continue;
    if (s > pos) result += escHtml(text.slice(pos, s));
    result += '<mark class="hl-word-' + color + '">' + escHtml(text.slice(s, e)) + '</mark>';
    pos = e;
  }
  result += escHtml(text.slice(pos));
  vtext.innerHTML = result;
}

/* Apply stored word highlights to all visible .vtext spans */
function applyAllWordHL() {
  document.querySelectorAll('.vtext[data-plain]').forEach(function(vtext) {
    const row = vtext.closest('[data-vkey]');
    if (!row) return;
    const vkey = row.dataset.vkey;
    if (WORD_HL_STORE[vkey] && WORD_HL_STORE[vkey].length) reRenderVText(vtext, vkey);
  });
}

/* Show word-hl bar at bounding rect of current selection */
let _whlSelVText = null;
function showWordHLBar(rect) {
  const bar = document.getElementById('word-hl-bar');
  bar.classList.add('open');
  const barW = 200; // approx
  let left = rect.left + window.scrollX + (rect.width / 2) - (barW / 2);
  left = Math.max(4, Math.min(left, window.innerWidth - barW - 4));
  let top  = rect.top + window.scrollY - 54;
  if (top < window.scrollY + 4) top = rect.bottom + window.scrollY + 8;
  bar.style.left = left + 'px';
  bar.style.top  = top  + 'px';
}
function hideWordHLBar() {
  document.getElementById('word-hl-bar').classList.remove('open');
  _whlSelVText = null;
}

/* Apply selected color to current text selection within a .vtext span */
function applyWordHL(color) {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) { hideWordHLBar(); return; }
  const range = sel.getRangeAt(0);
  let ancestor = range.commonAncestorContainer;
  if (ancestor.nodeType === Node.TEXT_NODE) ancestor = ancestor.parentNode;
  const vtext = ancestor.closest('.vtext') || (ancestor.classList && ancestor.classList.contains('vtext') ? ancestor : null);
  if (!vtext) { hideWordHLBar(); return; }
  const row = vtext.closest('[data-vkey]');
  if (!row) { hideWordHLBar(); return; }
  const vkey = row.dataset.vkey;
  const start = getTextOffset(vtext, range.startContainer, range.startOffset);
  const end   = getTextOffset(vtext, range.endContainer,   range.endOffset);
  if (start < 0 || end < 0 || start >= end) { hideWordHLBar(); return; }
  if (!WORD_HL_STORE[vkey]) WORD_HL_STORE[vkey] = [];
  // Remove any range that overlaps the new selection (fully or partially), then add new range
  WORD_HL_STORE[vkey] = WORD_HL_STORE[vkey].filter(function(r){ return r.end <= start || r.start >= end; });
  WORD_HL_STORE[vkey].push({start: start, end: end, color: color});
  saveWordHL();
  reRenderVText(vtext, vkey);
  sel.removeAllRanges();
  hideWordHLBar();
}

/* Clear all word highlights from the verse under current selection */
function clearWordHLSel() {
  if (_whlSelVText) {
    const row = _whlSelVText.closest('[data-vkey]');
    if (row) {
      const vkey = row.dataset.vkey;
      delete WORD_HL_STORE[vkey];
      saveWordHL();
      const text = _whlSelVText.dataset.plain || _whlSelVText.textContent;
      _whlSelVText.innerHTML = escHtml(text);
    }
  }
  const selAfter = window.getSelection();
  if (selAfter) selAfter.removeAllRanges();
  hideWordHLBar();
}

/* selectionchange → show/hide word-hl bar */
document.addEventListener('selectionchange', function() {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0 || sel.toString().trim() === '') {
    // Don't hide immediately — let button clicks fire first
    return;
  }
  const range = sel.getRangeAt(0);
  let ancestor = range.commonAncestorContainer;
  if (ancestor.nodeType === Node.TEXT_NODE) ancestor = ancestor.parentNode;
  const vtext = ancestor.closest ? ancestor.closest('.vtext') : null;
  if (!vtext) { hideWordHLBar(); return; }
  _whlSelVText = vtext;
  showWordHLBar(range.getBoundingClientRect());
});

/* Clicking outside the bar and not in a verse closes it */
document.addEventListener('mousedown', function(e) {
  if (!document.getElementById('word-hl-bar').classList.contains('open')) return;
  if (e.target.closest('#word-hl-bar')) return; // clicks inside bar are fine
  hideWordHLBar();
});

// ── Text Highlighting ─────────────────────────────────────────
const HL_KEY = 'bde_hl_v1';
let HL_STORE = {};
try { HL_STORE = JSON.parse(localStorage.getItem(HL_KEY) || '{}'); } catch(e) { HL_STORE = {}; }

let _hlRow  = null;
let _hlVKey = null;

function saveHL() {
  try { localStorage.setItem(HL_KEY, JSON.stringify(HL_STORE)); } catch(e) {}
}

function applyStoredHL(container) {
  container.querySelectorAll('[data-vkey]').forEach(function(row) {
    const color = HL_STORE[row.dataset.vkey];
    if (color) row.setAttribute('data-hl', color);
    else row.removeAttribute('data-hl');
  });
}

function hlTap(event, row) {
  event.stopPropagation();
  if (_hlRow && _hlRow !== row) _hlRow.classList.remove('hl-selected');
  if (_hlRow === row && document.getElementById('hl-toolbar').classList.contains('open')) {
    closeHLToolbar(); return;
  }
  _hlRow  = row;
  _hlVKey = row.dataset.vkey;
  row.classList.add('hl-selected');
  document.getElementById('hl-toolbar').classList.add('open');
}

function setHL(color) {
  if (!_hlRow || !_hlVKey) return;
  if (color) {
    HL_STORE[_hlVKey] = color;
    _hlRow.setAttribute('data-hl', color);
  } else {
    delete HL_STORE[_hlVKey];
    _hlRow.removeAttribute('data-hl');
  }
  saveHL();
  _hlRow.classList.remove('hl-selected');
  closeHLToolbar();
}

function closeHLToolbar() {
  document.getElementById('hl-toolbar').classList.remove('open');
  if (_hlRow) { _hlRow.classList.remove('hl-selected'); _hlRow = null; }
  _hlVKey = null;
}

document.addEventListener('click', function(e) {
  if (document.getElementById('hl-toolbar').classList.contains('open') &&
      !e.target.closest('#hl-toolbar') && !e.target.closest('[data-vkey]')) {
    closeHLToolbar();
  }
});

// ── Notes / Comments ──────────────────────────────────────────
const NOTES_KEY = 'bde_notes_v1';
let   _currentNotesPid = null;
let   _notesSaveTimer  = null;

function loadNotes(passageId) {
  _currentNotesPid = passageId;
  var ta = document.getElementById('notes-textarea');
  if (!ta) return;
  var store = {};
  try { store = JSON.parse(localStorage.getItem(NOTES_KEY) || '{}'); } catch(e) {}
  ta.value = store[passageId] || '';
  // Update placeholder and save-indicator from current lang
  ta.placeholder = t('notes_placeholder');
  var heading = document.querySelector('#passage-notes .notes-heading [data-i18n="notes_title"]');
  if (heading) heading.textContent = t('notes_title');
  var saveBtn  = document.getElementById('notes-save-btn');
  var clearBtn = document.getElementById('notes-clear-btn');
  if (saveBtn)  saveBtn.textContent  = t('notes_save');
  if (clearBtn) clearBtn.textContent = t('notes_clear');
  hideSavedIndicator();
}

function saveNotes() {
  if (_currentNotesPid === null) return;
  var ta = document.getElementById('notes-textarea');
  if (!ta) return;
  var store = {};
  try { store = JSON.parse(localStorage.getItem(NOTES_KEY) || '{}'); } catch(e) {}
  var text = ta.value.trim();
  if (text) { store[_currentNotesPid] = ta.value; }
  else      { delete store[_currentNotesPid]; }
  try { localStorage.setItem(NOTES_KEY, JSON.stringify(store)); } catch(e) {}
  showSavedIndicator();
}

function clearNotes() {
  if (_currentNotesPid === null) return;
  var ta = document.getElementById('notes-textarea');
  if (ta) ta.value = '';
  var store = {};
  try { store = JSON.parse(localStorage.getItem(NOTES_KEY) || '{}'); } catch(e) {}
  delete store[_currentNotesPid];
  try { localStorage.setItem(NOTES_KEY, JSON.stringify(store)); } catch(e) {}
  hideSavedIndicator();
}

function showSavedIndicator() {
  var ind = document.getElementById('notes-saved-indicator');
  if (!ind) return;
  ind.textContent = t('notes_saved');
  ind.classList.add('show');
  clearTimeout(_notesSaveTimer);
  _notesSaveTimer = setTimeout(function() { ind.classList.remove('show'); }, 2500);
}
function hideSavedIndicator() {
  var ind = document.getElementById('notes-saved-indicator');
  if (ind) ind.classList.remove('show');
}
// Auto-save on blur (user taps away from textarea)
document.addEventListener('focusout', function(e) {
  if (e.target && e.target.id === 'notes-textarea' && _currentNotesPid !== null) {
    saveNotes();
  }
});

// ── PWA: Service Worker + Install + Update ────────────────────
let _installPrompt = null;

// ── Offline indicator ─────────────────────────────────────────
function updateOfflineBadge() {
  const badge = document.getElementById('offline-badge');
  if (!navigator.onLine) {
    badge.textContent = t('offline_badge');
    badge.className = 'offline';
  } else {
    badge.textContent = t('online_badge');
    badge.className = 'online';
    // hide after 3 s once back online
    setTimeout(() => { badge.className = ''; }, 3000);
  }
}
window.addEventListener('online',  updateOfflineBadge);
window.addEventListener('offline', updateOfflineBadge);
// On load: only show if already offline
if (!navigator.onLine) updateOfflineBadge();

// ── Save for offline ──────────────────────────────────────────
function saveOffline() {
  const a = document.createElement('a');
  a.href = location.href;
  a.download = 'BDE-Bibel-offline.html';
  // If we're on file://, just show instructions
  if (location.protocol === 'file:') {
    alert('Du verwendest die Datei bereits lokal.\n\nDiese Datei einfach weiter teilen – sie funktioniert überall ohne Internet!');
    return;
  }
  // Fetch this page and trigger download
  fetch(location.href)
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      a.href = url;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    })
    .catch(() => {
      // Fallback: just link to current URL with download attribute
      a.click();
    });
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => {
        reg.addEventListener('updatefound', () => {
          const newSW = reg.installing;
          if (!newSW) return;
          newSW.addEventListener('statechange', () => {
            if (newSW.state === 'installed' && navigator.serviceWorker.controller) {
              showUpdateNotice();
            }
          });
        });
      })
      .catch(err => console.debug('SW not available (file://):', err));

    navigator.serviceWorker.addEventListener('message', e => {
      if (e.data && e.data.type === 'SW_UPDATED') showUpdateNotice();
    });
  });
}

function showUpdateNotice() {
  document.getElementById('update-bar').classList.add('visible');
  document.getElementById('update-btn').style.display = 'block';
}

// Hide "Als Datei speichern" buttons when the app is installed (runs as standalone)
function hideSaveButtons() {
  var fb = document.getElementById('save-footer-btn');
  var sb = document.getElementById('save-btn-splash');
  if (fb) fb.style.display = 'none';
  if (sb) sb.style.display = 'none';
}
// Detect if already running as installed PWA (standalone mode)
var IS_STANDALONE = window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;
if (IS_STANDALONE) {
  hideSaveButtons();
  // Hide install button – app is already installed
  document.getElementById('install-btn').style.display = 'none';
  document.getElementById('install-btn-splash').style.display = 'none';
}

window.addEventListener('beforeinstallprompt', e => {
  // HTTPS + Chrome/Edge: immediately trigger the native install prompt banner
  e.preventDefault();
  _installPrompt = e;
  // Show install buttons in bar + splash
  document.getElementById('install-btn').style.display = 'block';
  document.getElementById('install-btn-splash').style.display = 'block';
  // Auto-prompt after 2s if user has not already installed or dismissed
  if (!localStorage.getItem('bde_install_dismissed')) {
    setTimeout(() => {
      if (_installPrompt) {
        _installPrompt.prompt();
        _installPrompt.userChoice.then(choice => {
          if (choice.outcome === 'dismissed') {
            localStorage.setItem('bde_install_dismissed', '1');
          }
          _installPrompt = null;
        }).catch(() => { _installPrompt = null; });
      }
    }, 2000);
  }
});
window.addEventListener('appinstalled', () => {
  document.getElementById('install-btn').style.display = 'none';
  document.getElementById('install-btn-splash').style.display = 'none';
  hideSaveButtons();
  _installPrompt = null;
  localStorage.setItem('bde_install_dismissed', '1');
});
document.getElementById('install-btn-splash').addEventListener('click', installApp);

// Auto-show A2HS guide on first visit when NOT standalone and NOT on HTTPS
// (e.g. file:// or unsupported browser) – guides user to install
(function autoShowInstallGuide() {
  if (IS_STANDALONE) return;
  if (localStorage.getItem('bde_a2hs_shown')) return;
  // Only auto-show if we are not on HTTPS (no native prompt will fire)
  if (location.protocol === 'https:') return;
  // On file:// or http:// – show after 3 seconds
  setTimeout(function() {
    if (!IS_STANDALONE && !document.getElementById('a2hs-overlay').classList.contains('open')) {
      localStorage.setItem('bde_a2hs_shown', '1');
      showA2HS();
    }
  }, 3000);
})();

function detectPlatform() {
  const ua = navigator.userAgent.toLowerCase();
  if (/iphone|ipad|ipod/.test(ua)) return 'iphone';
  if (/android/.test(ua)) return 'android';
  return 'desktop';
}
function switchA2HS(platform) {
  ['android','iphone','desktop'].forEach(p => {
    document.getElementById('panel-' + p).classList.toggle('active', p === platform);
    document.getElementById('tab-' + p).classList.toggle('active', p === platform);
  });
}
function showA2HS() {
  var platform = detectPlatform();
  switchA2HS(platform);
  // Show the "open URL first" step 0 only when running from file://
  var step0 = document.getElementById('a2hs-android-step0');
  if (step0) step0.style.display = (location.protocol !== 'https:' && platform === 'android') ? 'flex' : 'none';
  document.getElementById('a2hs-overlay').classList.add('open');
}
function closeA2HS() {
  document.getElementById('a2hs-overlay').classList.remove('open');
}
document.getElementById('a2hs-overlay').addEventListener('click', function(e) {
  if (e.target === this) closeA2HS();
});

function installApp() {
  if (_installPrompt) {
    _installPrompt.prompt();
    _installPrompt.userChoice
      .then(() => { _installPrompt = null; })
      .catch(() => { _installPrompt = null; });
  } else {
    showA2HS();
  }
}
</script>
</body>
</html>
"""


def build(csv_path: str, output_path: str,
          passages_json: str = PASSAGES_JSON,
          pako_path: str = PAKO_PATH) -> None:
    print("Reading German CSV (Elberfelder 1905) …", flush=True)
    books_de, verses_de = load_data(csv_path)
    print(f"  {len(books_de)} books, {len(verses_de)} verses", flush=True)

    print("Loading English KJV …", flush=True)
    try:
        books_en, verses_en = load_kjv()
        print(f"  {len(books_en)} books, {len(verses_en)} verses", flush=True)
    except Exception as e:
        print(f"  WARNING: KJV unavailable ({e}), falling back to German", flush=True)
        books_en, verses_en = books_de, verses_de

    print("Loading Indonesian Bible …", flush=True)
    try:
        books_id, verses_id = load_indonesian()
        print(f"  {len(books_id)} books, {len(verses_id)} verses", flush=True)
    except Exception as e:
        print(f"  WARNING: Indonesian unavailable ({e}), falling back to German", flush=True)
        books_id, verses_id = books_de, verses_de

    print("Compressing multilingual Bible data …", flush=True)
    payload = build_payload(books_de, verses_de, books_en, verses_en, books_id, verses_id)
    print(f"  Payload size: {len(payload) / 1024:.0f} KB (base64)", flush=True)

    # Load passage data (small – embed as plain JSON, not base64)
    passage_data_js = "{}"
    if os.path.exists(passages_json):
        with open(passages_json, encoding="utf-8") as f:
            raw = json.load(f)
        passage_data_js = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
        print(f"  Passage data: {len(raw['passages'])} passages, "
              f"{len(raw['themes'])} themes", flush=True)
    else:
        print(f"  (Passage data not found at {passages_json})", flush=True)

    # Read pako inflate library (ES5, works on all Android/iOS/Desktop)
    pako_src = ""
    if os.path.exists(pako_path):
        with open(pako_path, encoding="utf-8") as f:
            pako_src = f.read()
        print(f"  pako inflate: {len(pako_src):,} bytes", flush=True)
    else:
        print(f"  WARNING: pako not found at {pako_path}", flush=True)

    # Embed app icon as base64 so it works from any URL (file://, GitHub Pages, shared link)
    icon192_b64 = ""
    icon_path = os.path.join(REPO_ROOT, "preview", "icons", "icon-192.png")
    if os.path.exists(icon_path):
        with open(icon_path, "rb") as f:
            icon192_b64 = base64.b64encode(f.read()).decode()
        print(f"  Icon 192x192: {len(icon192_b64):,} chars base64", flush=True)
    else:
        print(f"  WARNING: icon not found at {icon_path}", flush=True)

    html = (HTML_TEMPLATE
            .replace("'%%PAYLOAD%%'", f"'{payload}'")
            .replace("%%PASSAGE_DATA%%", passage_data_js)
            .replace("%%PAKO%%", pako_src)
            .replace("%%ICON192%%", icon192_b64))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Written: {output_path}  ({size_kb:.0f} KB)", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build self-contained Bible HTML")
    parser.add_argument("--out", default=OUTPUT_PATH,
                        help="Output HTML path (default: preview/standalone.html)")
    args = parser.parse_args()
    out = args.out
    print(f"CSV:      {CSV_PATH}")
    print(f"Passages: {PASSAGES_JSON}")
    print(f"Output:   {out}")
    build(CSV_PATH, out)
    print("Done.")
