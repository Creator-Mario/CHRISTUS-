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


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Christus – Bibel</title>

  <!-- PWA: installable as app on Android/iOS/Desktop -->
  <link rel="manifest" href="manifest.json" />
  <meta name="theme-color" content="#1a237e" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="Christus" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="description" content="Elberfelder 1905 – Deutsche Bibel mit Volltextsuche und wichtigen Bibelstellen" />

  <style>
    :root {
      --primary: #1a237e;
      --primary-light: #534bae;
      --accent: #e8eaf6;
      --text: #212121;
      --text-secondary: #616161;
      --bg: #fafafa;
      --card: #fff;
      --border: #e0e0e0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Roboto, Arial, sans-serif;
           background: var(--bg); color: var(--text);
           max-width: 800px; margin: 0 auto; }

    #app-bar {
      background: var(--primary); color: #fff;
      padding: 12px 16px; display: flex; align-items: center; gap: 10px;
      position: sticky; top: 0; z-index: 10;
      box-shadow: 0 2px 4px rgba(0,0,0,.3);
    }
    #back-btn { background: none; border: none; color: #fff;
      font-size: 22px; cursor: pointer; padding: 4px 8px; display: none; }
    #app-title { flex: 1; font-size: 17px; font-weight: 600; }
    #search-toggle { background: none; border: none; color: #fff;
      font-size: 20px; cursor: pointer; padding: 4px 8px; }
    #books-toggle  { background: none; border: none; color: #fff;
      font-size: 20px; cursor: pointer; padding: 4px 8px; }
    #install-btn   { background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.5);
      color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
      padding: 4px 10px; border-radius: 14px; display: none; white-space: nowrap; }

    #search-bar { background: var(--primary); padding: 8px 12px; display: none; }
    #search-input { width: 100%; padding: 8px 12px; font-size: 15px;
      border: none; border-radius: 4px; outline: none; }

    .view { display: none; padding: 0; }
    .view.active { display: block; }

    /* ── Home: theme grid ── */
    .section-header { padding: 12px 16px 4px; font-weight: 700; font-size: 14px;
      color: var(--text-secondary); text-transform: uppercase; letter-spacing: .5px; }
    #theme-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 10px; padding: 10px 12px; }
    .theme-card {
      border-radius: 8px; padding: 14px 12px; cursor: pointer;
      display: flex; flex-direction: column; gap: 8px;
      color: #fff; min-height: 80px;
      box-shadow: 0 2px 6px rgba(0,0,0,.2);
      transition: transform .15s, box-shadow .15s; }
    .theme-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.25); }
    .theme-icon { font-size: 26px; }
    .theme-name { font-size: 12px; font-weight: 600; line-height: 1.3; }

    /* ── Passage list ── */
    .list-item { display: flex; align-items: center; padding: 12px 16px;
      border-bottom: 1px solid var(--border); background: var(--card);
      cursor: pointer; transition: background .15s; }
    .list-item:hover { background: var(--accent); }
    .avatar { width: 32px; height: 32px; border-radius: 50%;
      background: var(--primary); color: #fff;
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 600; flex-shrink: 0; margin-right: 12px; }
    .list-item-text { flex: 1; }
    .list-item-title { font-size: 15px; }
    .list-item-ref { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

    /* ── Passage text ── */
    .chapter-heading { padding: 12px 16px 4px; font-weight: 700;
      font-size: 15px; color: var(--primary); }
    .verse-row { padding: 8px 16px; border-bottom: 1px solid var(--border);
      background: var(--card); line-height: 1.65; }
    .verse-num { font-weight: 700; color: var(--primary); margin-right: 6px; }

    /* ── Books ── */
    #chapter-grid { display: grid;
      grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
      gap: 8px; padding: 12px; }
    .chapter-btn { padding: 12px 4px; background: var(--primary); color: #fff;
      border: none; border-radius: 6px; font-size: 15px; cursor: pointer;
      transition: background .15s; }
    .chapter-btn:hover { background: var(--primary-light); }

    /* ── Search ── */
    .result-item { padding: 12px 16px; border-bottom: 1px solid var(--border);
      background: var(--card); cursor: pointer; }
    .result-item:hover { background: var(--accent); }
    .result-ref { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
    mark { background: #fff176; border-radius: 2px; }

    #loading { text-align: center; padding: 60px 16px;
      color: var(--text-secondary); font-size: 15px; }
    .empty { text-align: center; padding: 40px 16px; color: var(--text-secondary); }
  </style>
</head>
<body>

<div id="app-bar">
  <button id="back-btn" onclick="goBack()">&#8592;</button>
  <span id="app-title">Christus – Bibel</span>
  <button id="install-btn" onclick="installApp()" title="App installieren">&#11015; App</button>
  <button id="books-toggle"  title="Alle Bücher" onclick="openAllBooks()">&#128214;</button>
  <button id="search-toggle" title="Suchen"      onclick="showSearch()">&#128269;</button>
</div>
<div id="search-bar">
  <input id="search-input" type="search" placeholder="Bibelstellen suchen …"
         oninput="onSearchInput(this.value)" />
</div>

<div id="loading">Daten werden geladen …</div>

<div id="view-home"     class="view">
  <div class="section-header">Wichtige Bibelstellen</div>
  <div id="theme-grid"></div>
</div>
<div id="view-passages" class="view"><div id="passage-list"></div></div>
<div id="view-text"     class="view"><div id="passage-text"></div></div>
<div id="view-books"    class="view"><div id="book-list"></div></div>
<div id="view-chapters" class="view"><div id="chapter-grid"></div></div>
<div id="view-verses"   class="view"><div id="verse-list"></div></div>
<div id="view-search"   class="view"><div id="search-results"></div></div>

<script>
// ── Embedded Bible data ────────────────────────────────────────────────────
const PAYLOAD_B64 = '%%PAYLOAD%%';
// ── Embedded passage data (themes + passages) ──────────────────────────────
const PASSAGE_DATA = %%PASSAGE_DATA%%;

// ── State ──────────────────────────────────────────────────────────────────
let BOOKS   = {};   // {bookId: name}
let VERSES  = [];   // [[bookId, chapter, verse, text], ...]
let IDX     = {};   // bookId → chapter → [verse rows]
let navHistory = [];
let searchTimer = null;
let currentThemeColor = '#1a237e';

const THEME_COLORS = [
  '#1a237e','#4a148c','#880e4f','#bf360c','#1b5e20','#006064',
  '#0d47a1','#37474f','#4e342e','#1a237e','#6a1b9a','#01579b',
  '#2e7d32','#e65100','#3e2723','#283593','#558b2f','#4527a0'
];

// ── Bootstrap ──────────────────────────────────────────────────────────────
(async function init() {
  try {
    const binStr = atob(PAYLOAD_B64);
    const bytes  = new Uint8Array(binStr.length);
    for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
    const ds = new DecompressionStream('gzip');
    const w  = ds.writable.getWriter(); w.write(bytes); w.close();
    const buf  = await new Response(ds.readable).arrayBuffer();
    const data = JSON.parse(new TextDecoder().decode(buf));
    BOOKS  = data.books;
    VERSES = data.verses;
    VERSES.forEach(row => {
      const [b, c] = row;
      if (!IDX[b]) IDX[b] = {};
      if (!IDX[b][c]) IDX[b][c] = [];
      IDX[b][c].push(row);
    });
    document.getElementById('loading').style.display = 'none';
    showView('view-home');
    renderHome();
  } catch (err) {
    document.getElementById('loading').innerHTML =
      '<b>Fehler:</b> ' + escHtml(err.message) +
      '<br><small>Bitte einen modernen Browser verwenden (Chrome 80+, Firefox 113+, Safari 16.4+).</small>';
  }
})();

// ── Navigation ─────────────────────────────────────────────────────────────
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const isRoot = (id === 'view-home');
  document.getElementById('back-btn').style.display     = isRoot ? 'none' : 'block';
  document.getElementById('books-toggle').style.display  = (id === 'view-search') ? 'none' : 'block';
  document.getElementById('search-toggle').style.display = (id === 'view-search') ? 'none' : 'block';
  document.getElementById('search-bar').style.display    = (id === 'view-search') ? 'block' : 'none';
}
function navigate(viewId) {
  navHistory.push(document.querySelector('.view.active').id);
  showView(viewId);
}
function goBack() {
  if (!navHistory.length) return;
  const prev = navHistory.pop();
  showView(prev);
  if (prev === 'view-home') document.getElementById('app-title').textContent = 'Christus – Bibel';
}

// ── Home: theme grid ────────────────────────────────────────────────────────
function renderHome() {
  document.getElementById('app-title').textContent = 'Christus – Bibel';
  const grid = document.getElementById('theme-grid');
  grid.innerHTML = PASSAGE_DATA.themes.map((t, i) => {
    const color = THEME_COLORS[i % THEME_COLORS.length];
    return `<div class="theme-card" data-tid="${t.id}" data-color="${color}"
                 style="background:${color}">
              <span class="theme-icon">${escHtml(t.icon)}</span>
              <span class="theme-name">${escHtml(t.name)}</span>
            </div>`;
  }).join('');
  grid.onclick = e => {
    const el = e.target.closest('[data-tid]');
    if (el) openTheme(Number(el.dataset.tid), el.dataset.color);
  };
}

// ── Passage list ────────────────────────────────────────────────────────────
function openTheme(themeId, color) {
  currentThemeColor = color;
  const theme = PASSAGE_DATA.themes.find(t => t.id === themeId);
  const passages = PASSAGE_DATA.passages.filter(p => p.theme_id === themeId);
  document.getElementById('app-title').textContent =
    (theme ? theme.icon + '  ' + theme.name : 'Passagen');
  document.getElementById('app-bar').style.background = color;
  const list = document.getElementById('passage-list');
  list.innerHTML = passages.map((p, i) => {
    const ref = refString(p);
    return `<div class="list-item" data-pid="${p.id}">
              <div class="avatar" style="background:${color}">${i+1}</div>
              <div class="list-item-text">
                <div class="list-item-title">${escHtml(p.title)}</div>
                <div class="list-item-ref">${escHtml(ref)}</div>
              </div>
              <span style="color:#999">›</span>
            </div>`;
  }).join('');
  list.onclick = e => {
    const el = e.target.closest('[data-pid]');
    if (el) openPassage(Number(el.dataset.pid));
  };
  navigate('view-passages');
}

function refString(p) {
  const bName = BOOKS[p.book_id] || '?';
  if (p.chapter_from === p.chapter_to) {
    return `${bName} ${p.chapter_from},${p.verse_from}–${p.verse_to}`;
  }
  return `${bName} ${p.chapter_from},${p.verse_from} – ${p.chapter_to},${p.verse_to}`;
}

// ── Passage text ────────────────────────────────────────────────────────────
function openPassage(passageId) {
  const p = PASSAGE_DATA.passages.find(x => x.id === passageId);
  if (!p) return;
  const rows = versesForPassage(p);
  document.getElementById('app-title').textContent = p.title;

  let html = '', lastChap = null;
  rows.forEach(([b, c, v, t]) => {
    if (c !== lastChap) {
      const bName = BOOKS[b] || '?';
      html += `<div class="chapter-heading" style="color:${currentThemeColor}">` +
              escHtml(`${bName} ${c}`) + '</div>';
      lastChap = c;
    }
    html += `<div class="verse-row"><span class="verse-num"
              style="color:${currentThemeColor}">${v}</span>${escHtml(t)}</div>`;
  });

  if (!html) html = '<div class="empty">Keine Verse gefunden.</div>';
  document.getElementById('passage-text').innerHTML = html;
  navigate('view-text');
}

function versesForPassage(p) {
  const result = [];
  const b = p.book_id;
  const cf = p.chapter_from, vf = p.verse_from;
  const ct = p.chapter_to,   vt = p.verse_to;
  (VERSES).forEach(row => {
    const [rb, rc, rv] = row;
    if (rb !== b) return;
    if (rc < cf || rc > ct) return;
    if (rc === cf && rv < vf) return;
    if (rc === ct && rv > vt) return;
    result.push(row);
  });
  return result;
}

// ── All books ───────────────────────────────────────────────────────────────
function openAllBooks() {
  document.getElementById('app-bar').style.background = '#1a237e';
  document.getElementById('app-title').textContent = 'Alle Bücher';
  const list = document.getElementById('book-list');
  list.innerHTML = Object.entries(BOOKS).map(([id, name]) =>
    `<div class="list-item" data-book="${id}">
       <div class="avatar">${id}</div>
       <div class="list-item-text">
         <div class="list-item-title">${escHtml(name)}</div>
       </div>
       <span style="color:#999">›</span>
     </div>`
  ).join('');
  list.onclick = e => {
    const el = e.target.closest('[data-book]');
    if (el) openBook(Number(el.dataset.book));
  };
  navigate('view-books');
}

function openBook(bookId) {
  const chapters = Object.keys(IDX[bookId] || {}).map(Number).sort((a,b)=>a-b);
  const grid = document.getElementById('chapter-grid');
  grid.innerHTML = chapters.map(c =>
    `<button class="chapter-btn" data-book="${bookId}" data-ch="${c}">${c}</button>`
  ).join('');
  grid.onclick = e => {
    const el = e.target.closest('[data-ch]');
    if (el) openChapter(Number(el.dataset.book), Number(el.dataset.ch));
  };
  document.getElementById('app-title').textContent = BOOKS[bookId] || '';
  navigate('view-chapters');
}

// ── Verses ──────────────────────────────────────────────────────────────────
function openChapter(bookId, chapter) {
  const rows = (IDX[bookId] || {})[chapter] || [];
  document.getElementById('verse-list').innerHTML = rows.map(([,, v, t]) =>
    `<div class="verse-row"><span class="verse-num">${v}</span>${escHtml(t)}</div>`
  ).join('');
  document.getElementById('app-title').textContent =
    `${BOOKS[bookId] || ''} ${chapter}`;
  navigate('view-verses');
}

// ── Search ───────────────────────────────────────────────────────────────────
function showSearch() {
  document.getElementById('app-bar').style.background = '#1a237e';
  document.getElementById('app-title').textContent = 'Suchen';
  navigate('view-search');
  document.getElementById('search-input').focus();
  document.getElementById('search-results').innerHTML =
    '<div class="empty">Suchbegriff eingeben …</div>';
}
function onSearchInput(val) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => runSearch(val), 300);
}
function runSearch(raw) {
  const q = raw.trim();
  const container = document.getElementById('search-results');
  if (!q) { container.innerHTML = '<div class="empty">Suchbegriff eingeben …</div>'; return; }
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
  const div = document.getElementById('search-results');
  div.innerHTML = results.map(([b, c, v, text]) =>
    `<div class="result-item" data-book="${b}" data-ch="${c}">
       ${highlightTerms(text, terms)}
       <div class="result-ref">${escHtml(BOOKS[b] || '?')} ${c},${v}</div>
     </div>`
  ).join('');
  div.onclick = e => {
    const el = e.target.closest('[data-ch]');
    if (el) openChapter(Number(el.dataset.book), Number(el.dataset.ch));
  };
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
                  .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
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

// ── PWA: Service Worker + Install prompt ──────────────────────────────────
let _installPrompt = null;

// Register SW (only works when served via HTTPS/localhost, not file://)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(err =>
      console.debug('SW registration failed (expected on file://):', err)
    );
  });
}

// Capture the browser's "beforeinstallprompt" event
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  _installPrompt = e;
  document.getElementById('install-btn').style.display = 'block';
});

// Hide install button once app is installed
window.addEventListener('appinstalled', () => {
  document.getElementById('install-btn').style.display = 'none';
  _installPrompt = null;
});

function installApp() {
  if (_installPrompt) {
    _installPrompt.prompt();
    _installPrompt.userChoice
      .then(() => { _installPrompt = null; })
      .catch(() => { _installPrompt = null; });
  } else {
    // Fallback: guide user
    alert(
      'So installierst du die App:\n\n' +
      '📱 Android Chrome: Menü (⋮) → "Zum Startbildschirm hinzufügen"\n' +
      '🍎 iPhone Safari: Teilen (↑) → "Zum Home-Bildschirm"\n' +
      '💻 Desktop Chrome/Edge: Adressleiste → Install-Symbol (⊕)'
    );
  }
}
</script>
</body>
</html>
"""


def build(csv_path: str, output_path: str,
          passages_json: str = PASSAGES_JSON) -> None:
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

    html = (HTML_TEMPLATE
            .replace("'%%PAYLOAD%%'", f"'{payload}'")
            .replace("%%PASSAGE_DATA%%", passage_data_js))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Written: {output_path}  ({size_kb:.0f} KB)", flush=True)


if __name__ == "__main__":
    print(f"CSV:      {CSV_PATH}")
    print(f"Passages: {PASSAGES_JSON}")
    print(f"Output:   {OUTPUT_PATH}")
    build(CSV_PATH, OUTPUT_PATH)
    print("Done.")
