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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "elberfelder_1905.csv")
PASSAGES_JSON = os.path.join(REPO_ROOT, "data", "key_passages.json")
OUTPUT_PATH = os.path.join(REPO_ROOT, "preview", "standalone.html")
PAKO_PATH = os.path.join(REPO_ROOT, "tools", "vendor", "pako_inflate.min.js")


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_header(reader):
    for row in reader:
        if any("Verse ID" in c for c in row) and any("Book Number" in c for c in row):
            return row
    raise RuntimeError("CSV header row not found")


def load_data(csv_path: str):
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


def build_payload(books: dict, verses: list) -> str:
    """Return base64-encoded gzip-compressed JSON payload."""
    payload = json.dumps(
        {"books": {str(k): v for k, v in sorted(books.items())}, "verses": verses},
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
      cursor: pointer; display: none; transition: background .15s;
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

    /* ── Theme grid ── */
    #theme-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
      gap: 10px; padding: 12px 12px 16px;
    }
    .theme-card {
      border-radius: 10px; padding: 14px 12px; cursor: pointer;
      display: flex; flex-direction: column; gap: 7px;
      color: #fff; min-height: 90px;
      box-shadow: 0 3px 8px rgba(0,0,0,.28);
      transition: transform .15s, box-shadow .15s;
    }
    .theme-card:hover { transform: translateY(-3px); box-shadow: 0 7px 18px rgba(0,0,0,.35); }
    .theme-icon  { font-size: 28px; }
    .theme-name  { font-size: 12px; font-weight: 700; line-height: 1.3;
      font-family: 'Segoe UI', Roboto, sans-serif; }
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

<!-- ── Splash cover ─────────────────────────────────────────── -->
<div id="splash">
  <div class="splash-icon">✝</div>
  <div class="splash-title">Buch des Dienstes zur Evangelisation</div>
  <div class="splash-subtitle">Elberfelder Bibel 1905</div>
  <div class="splash-divider"></div>
  <div class="splash-creator">von Mario Reiner Denzer</div>
  <div class="splash-copy">© 2025 Mario Reiner Denzer</div>
  <div class="splash-version">Version 1.0.0</div>
  <button class="splash-start" onclick="closeSplash()">✝ &nbsp;Zur Bibel</button>
  <button id="install-btn-splash">⬇ &nbsp;App installieren</button>
  <button id="save-btn-splash" onclick="saveOffline()" title="Als Datei speichern">💾 &nbsp;Offline speichern</button>
</div>

<!-- ── A2HS Install Guide Modal ────────────────────────────── -->
<div id="a2hs-overlay" role="dialog" aria-modal="true" aria-label="App installieren">
  <div id="a2hs-modal">
    <div class="a2hs-header">
      <span class="a2hs-title">📱 App zum Startbildschirm</span>
      <button class="a2hs-close" onclick="closeA2HS()" aria-label="Schließen">✕</button>
    </div>
    <div class="a2hs-tabs">
      <button class="a2hs-tab" id="tab-android" onclick="switchA2HS('android')"><span aria-hidden="true">🤖</span> Android</button>
      <button class="a2hs-tab" id="tab-iphone"  onclick="switchA2HS('iphone')"><span aria-hidden="true">🍎</span> iPhone</button>
      <button class="a2hs-tab" id="tab-desktop" onclick="switchA2HS('desktop')"><span aria-hidden="true">💻</span> Desktop</button>
    </div>

    <!-- Android -->
    <div class="a2hs-panel" id="panel-android">
      <div class="a2hs-step">
        <div class="a2hs-num">1</div>
        <div class="a2hs-step-text">Öffne diese Seite in <strong>Chrome</strong> (oder Samsung Internet) auf deinem Android-Gerät.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">2</div>
        <div class="a2hs-step-text">Tippe auf das <strong>Menü ⋮</strong> (drei Punkte oben rechts).</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">3</div>
        <div class="a2hs-step-text">Wähle <strong>„Zum Startbildschirm hinzufügen"</strong> aus der Liste.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">4</div>
        <div class="a2hs-step-text">Tippe auf <strong>„Hinzufügen"</strong> im Bestätigungsdialog.</div>
      </div>
      <div class="a2hs-step">
        <div class="a2hs-num">5</div>
        <div class="a2hs-step-text">✅ Das <strong>✝ BDE-Symbol</strong> erscheint auf deinem Startbildschirm – die App öffnet sich wie eine native App!</div>
      </div>
      <div class="a2hs-note">💡 Tipp: In Samsung Internet heißt es „Seite hinzufügen zu → Startbildschirm"</div>
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
  <span style="flex:1">🔄 Neue Version verfügbar!</span>
  <button id="update-reload" onclick="location.reload()">Jetzt aktualisieren</button>
</div>

<!-- ── App bar ──────────────────────────────────────────────── -->
<div id="app-bar">
  <button id="back-btn" onclick="goBack()">&#8592;</button>
  <button id="app-icon-btn" onclick="goHome()" title="Startseite">✝</button>
  <span id="app-title">BDE – Bibel</span>
  <button id="update-btn"  onclick="location.reload()" title="Update verfügbar">↻ Update</button>
  <button id="install-btn" onclick="installApp()"      title="App installieren">⬇ Installieren</button>
  <span   id="offline-badge">📵 Offline</span>
  <button class="bar-btn" id="books-toggle"  title="Alle Bücher" onclick="openAllBooks()">&#128214;</button>
  <button class="bar-btn" id="search-toggle" title="Suchen"      onclick="showSearch()">&#128269;</button>
</div>

<!-- ── Search bar ───────────────────────────────────────────── -->
<div id="search-bar">
  <input id="search-input" type="search" placeholder="Bibelstellen suchen …"
         oninput="onSearchInput(this.value)" />
</div>

<div id="loading">✝&ensp;Daten werden geladen …</div>

<!-- ── Views ────────────────────────────────────────────────── -->
<div id="view-home" class="view">
  <div id="home-header">
    <div class="home-cross">✝</div>
    <div class="home-title">Buch des Dienstes zur Evangelisation</div>
    <div class="home-sub">Elberfelder 1905 · 66 Bücher · 31 102 Verse</div>
  </div>
  <div class="section-header">Thematische Bibelstellen</div>
  <div id="theme-grid"></div>
  <div id="app-footer">
    <strong>Buch des Dienstes zur Evangelisation</strong><br>
    Creator &amp; Copyright: Mario Reiner Denzer · © 2025 · Version 1.0.0<br>
    Bibeltext: Elberfelder 1905 (gemeinfrei)<br>
    <button id="save-footer-btn" onclick="saveOffline()" style="
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
<div id="view-text"     class="view"><div id="passage-text"></div></div>
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

// ── Splash ────────────────────────────────────────────────────
function closeSplash() {
  document.getElementById('splash').style.display = 'none';
  // Safety net: re-render themes in case DOM wasn't ready during init()
  renderHome();
}

// ── Bootstrap ─────────────────────────────────────────────────
(function init() {
  try {
    const binStr = atob(PAYLOAD_B64);
    const bytes  = new Uint8Array(binStr.length);
    for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
    // pako.inflate works on ALL browsers (Android WebView, old Chrome, old Safari)
    const decompressed = pako.inflate(bytes);
    const data = JSON.parse(new TextDecoder().decode(decompressed));
    BOOKS  = data.books;
    VERSES = data.verses;
    VERSES.forEach(function(row) {
      var b = row[0], c = row[1];
      if (!IDX[b])    IDX[b]    = {};
      if (!IDX[b][c]) IDX[b][c] = [];
      IDX[b][c].push(row);
    });
    document.getElementById('loading').style.display = 'none';
    showView('view-home');
    renderHome();
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
  document.getElementById('books-toggle').style.display  = (id === 'view-search') ? 'none' : 'block';
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
function renderHome() {
  const grid = document.getElementById('theme-grid');
  if (!PASSAGE_DATA || !PASSAGE_DATA.themes || !PASSAGE_DATA.themes.length) {
    grid.innerHTML = '<p style="padding:20px;color:#888">Keine Themen verfügbar.</p>';
    return;
  }
  grid.innerHTML = PASSAGE_DATA.themes.map((t, i) => {
    const color = THEME_COLORS[i % THEME_COLORS.length];
    const count = PASSAGE_DATA.passages.filter(p => p.theme_id === t.id).length;
    return `<div class="theme-card" data-tid="${t.id}" data-color="${color}"
                 style="background:linear-gradient(135deg,${color},${hexFade(color)})">
              <span class="theme-icon">${escHtml(t.icon)}</span>
              <span class="theme-name">${escHtml(t.name)}</span>
              <span class="theme-count">${count} Stellen</span>
            </div>`;
  }).join('');
  grid.onclick = e => {
    const el = e.target.closest('[data-tid]');
    if (el) openTheme(Number(el.dataset.tid), el.dataset.color);
  };
}

// ── Passage list ──────────────────────────────────────────────
function openTheme(themeId, color) {
  currentThemeColor = color;
  const theme    = PASSAGE_DATA.themes.find(t => t.id === themeId);
  const passages = PASSAGE_DATA.passages.filter(p => p.theme_id === themeId);
  document.getElementById('app-title').textContent =
    theme ? theme.icon + '\u2002' + theme.name : 'Passagen';
  document.getElementById('app-bar').style.background = color;
  const list = document.getElementById('passage-list');
  list.innerHTML = passages.map((p, i) =>
    `<div class="list-item" data-pid="${p.id}">
       <div class="avatar" style="background:${color};border-color:var(--gold)">${i + 1}</div>
       <div class="list-item-text">
         <div class="list-item-title">${escHtml(p.title)}</div>
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
  document.getElementById('app-title').textContent = p.title;
  let html = '', lastChap = null;
  versesForPassage(p).forEach(([b, c, v, t]) => {
    if (c !== lastChap) {
      html += `<div class="chapter-heading">${escHtml((BOOKS[b] || '?') + ' ' + c)}</div>`;
      lastChap = c;
    }
    html += `<div class="verse-row" data-vkey="${b}:${c}:${v}" onclick="hlTap(event,this)"><sup class="verse-num">${v}</sup><span class="vtext" data-plain="${escHtmlAttr(t)}">${escHtml(t)}</span></div>`;
  });
  const ptEl = document.getElementById('passage-text');
  ptEl.innerHTML = html || '<div class="empty">Keine Verse gefunden.</div>';
  applyStoredHL(ptEl);
  applyAllWordHL();
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
  document.getElementById('app-title').textContent = 'Alle B\u00fccher';
  const list     = document.getElementById('book-list');
  const AT_LABEL = '<div class="section-header">Altes Testament (1\u201339)</div>';
  const NT_LABEL = '<div class="section-header">Neues Testament (40\u201366)</div>';
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
           <div class="list-item-ref">${chs} Kapitel \u00b7 ${vs} Verse</div>
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
      `${escHtml(BOOKS[bookId] || '')} \u00b7 ${chapters.length} Kapitel` +
    `</div>` +
    chapters.map(c => {
      const vs = (IDX[bookId][c] || []).length;
      return `<button class="chapter-btn" data-book="${bookId}" data-ch="${c}" title="${vs} Verse">${c}</button>`;
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
    `<div class="verse-row" data-vkey="${b}:${c}:${v}" onclick="hlTap(event,this)"><sup class="verse-num">${v}</sup><span class="vtext" data-plain="${escHtmlAttr(t)}">${escHtml(t)}</span></div>`
  ).join('');
  applyStoredHL(vlEl);
  applyAllWordHL();
  document.getElementById('app-title').textContent = `${BOOKS[bookId] || ''} ${chapter}`;
  navigate('view-verses');
}

// ── Search ────────────────────────────────────────────────────
function showSearch() {
  document.getElementById('app-bar').style.background = '';
  document.getElementById('app-title').textContent = 'Suchen';
  navigate('view-search');
  document.getElementById('search-input').focus();
  document.getElementById('search-results').innerHTML =
    '<div class="empty">Suchbegriff eingeben \u2026</div>';
}
function onSearchInput(val) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => runSearch(val), 300);
}
function runSearch(raw) {
  const q = raw.trim();
  const container = document.getElementById('search-results');
  if (!q) { container.innerHTML = '<div class="empty">Suchbegriff eingeben \u2026</div>'; return; }
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  const results = [];
  for (const row of VERSES) {
    if (terms.every(t => row[3].toLowerCase().includes(t))) {
      results.push(row);
      if (results.length >= 60) break;
    }
  }
  if (!results.length) {
    container.innerHTML = '<div class="empty">Keine Ergebnisse gefunden.</div>';
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

// ── PWA: Service Worker + Install + Update ────────────────────
let _installPrompt = null;

// ── Offline indicator ─────────────────────────────────────────
function updateOfflineBadge() {
  const badge = document.getElementById('offline-badge');
  if (!navigator.onLine) {
    badge.textContent = '📵 Offline';
    badge.className = 'offline';
  } else {
    badge.textContent = '✅ Online';
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
if (window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true) {
  hideSaveButtons();
}

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  _installPrompt = e;
  document.getElementById('install-btn').style.display = 'block';
  document.getElementById('install-btn-splash').style.display = 'block';
});
window.addEventListener('appinstalled', () => {
  document.getElementById('install-btn').style.display = 'none';
  document.getElementById('install-btn-splash').style.display = 'none';
  hideSaveButtons();
  _installPrompt = null;
});
document.getElementById('install-btn-splash').addEventListener('click', installApp);

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
  switchA2HS(detectPlatform());
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
    print("Reading CSV …", flush=True)
    books, verses = load_data(csv_path)
    print(f"  {len(books)} books, {len(verses)} verses", flush=True)

    print("Compressing Bible data …", flush=True)
    payload = build_payload(books, verses)
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
