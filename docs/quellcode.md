# 🔍 Quellcode – Wo finde ich was?

## Überblick

Die App besteht aus zwei Teilen:

| Teil | Beschreibung |
|------|-------------|
| **Web-App** (primär) | `preview/standalone.html` – eine einzige HTML-Datei mit der kompletten App, allen Bibeltexten und der Benutzeroberfläche. Funktioniert offline, ist ~5,8 MB groß. |
| **Flutter-App** (sekundär) | `lib/` – Dart-Quellcode für eine native Android/iOS-App (derzeit Gerüst). |

---

## Web-App: Wo ist der Quellcode?

Die `preview/standalone.html` wird **automatisch generiert** – du bearbeitest nicht die HTML-Datei direkt, sondern die Python-Quelldateien:

### 1. Haupt-Generator
**`tools/build_standalone_preview.py`** ← **Hier ist der komplette App-Quellcode**

Diese Datei enthält:
- Das gesamte **HTML-Gerüst** (Templates)
- Das gesamte **CSS** (spiritual design: navy/gold, Karten, Tabs, Modale)
- Das gesamte **JavaScript** der App:
  - `init()` – App-Start, Daten laden, Sprache erkennen
  - `renderHome()` – Startseite mit Themen-/Bibel-/Notizen-Tabs
  - `renderHomeBibleTab()` – 66 Bücher als Kacheln (AT/NT getrennt)
  - `renderHomeThemesTab()` – 24 Themen in 6 Gruppen
  - `renderNotesTab()` – alle Notizen nach Thema geordnet
  - `openTheme(id)` – Liste der Bibelstellen eines Themas
  - `openPassage(p)` – Verse + Notizen-Bereich
  - `openBook(bookId)` – Kapitelauswahl
  - `openChapter(bookId, ch)` – Verse eines Kapitels
  - `showSearch()` / `runSearch(q)` – Volltextsuche (FTS5)
  - `hlTap(vkey)` – Vers-Markierung (grün/gelb/rot)
  - `applyWordHL(color)` – Wort-Markierung nach Selektion
  - `showA2HS()` / `renderA2HS()` – Install-Anleitung (Android/iPhone/Desktop)
  - `setLang(lang)` / `applyLang()` – Sprachwechsel (DE/EN/ID)
  - `saveNotes(pid)` / `loadNotes(pid)` – Notizen speichern/laden
  - `exportNotes()` – Notizen als .txt exportieren
  - `saveOffline()` – App als Datei herunterladen
  - **LANG dict** – alle UI-Texte in DE/EN/ID
  - **THEME_GROUPS** – Gruppierung der 24 Themen in 6 Abschnitte

**So baust du die App neu:**
```bash
cd /pfad/zum/repo
python3 tools/build_standalone_preview.py
# → preview/standalone.html wird neu erstellt (~5,8 MB)
```

---

### 2. Bibeldaten und Themen
| Datei | Inhalt |
|-------|--------|
| `tools/generate_passages_json.py` | Definition aller 24 Themen + 604 Bibelstellen (Buch, Kapitel, Verse) |
| `data/key_passages.json` | Generierte JSON-Datei (aus generate_passages_json.py) |
| `elberfelder_1905.csv` | Rohdaten der Elberfelder Bibel 1905 (CSV, gemeinfrei) |
| `tools/build_bible_db.py` | Erstellt `assets/db/bible.sqlite` aus der CSV + JSON |
| `schema/bible_schema.sql` | SQLite-Schema (Tabellen: books, bible_verses, key_passages, …) |

**Bibeldatenbank neu bauen:**
```bash
python3 tools/generate_passages_json.py    # JSON erneuern
python3 tools/build_bible_db.py            # SQLite erneuern
python3 tools/build_standalone_preview.py  # HTML erneuern
```

---

### 3. Serviceworker (Offline-Cache)
**`preview/sw.js`** – der Service Worker:
- Cacht die App beim ersten Besuch
- Sendet `SW_UPDATED`-Nachricht wenn eine neue Version verfügbar ist
- Zeigt dadurch den „Jetzt aktualisieren"-Banner in der App

---

### 4. PWA-Manifest (App-Icon)
**`preview/manifest.json`** – definiert:
- App-Name, Kurz-Name
- Icons (192×192 + 512×512 PNG in `preview/icons/`)
- `display: standalone` → App öffnet ohne Browser-Leiste

---

## Flutter-App (Dart-Quellcode)

| Datei | Inhalt |
|-------|--------|
| `lib/main.dart` | App-Einstiegspunkt, MaterialApp, Farbschema |
| `lib/database/bible_db.dart` | SQLite-Datenbankzugriff (sqflite) |
| `lib/models/book.dart` | Datenmodell: Buch |
| `lib/models/verse.dart` | Datenmodell: Vers |
| `lib/screens/books_screen.dart` | Bücherliste |
| `lib/screens/chapters_screen.dart` | Kapitelauswahl |
| `lib/screens/verses_screen.dart` | Versanzeige |
| `lib/screens/search_screen.dart` | Volltextsuche |
| `pubspec.yaml` | Flutter-Abhängigkeiten |

---

## GitHub Actions (CI/CD)

| Workflow-Datei | Was passiert? |
|----------------|--------------|
| `.github/workflows/deploy-preview.yml` | Baut DB + HTML und deployt auf GitHub Pages |
| `.github/workflows/build-apk.yml` | Baut Android APK mit Flutter |
| `.github/workflows/build-electron.yml` | Baut Desktop-App (Windows/Mac/Linux) |
| `.github/workflows/release-html.yml` | Veröffentlicht HTML als GitHub-Release-Asset |

---

## GitHub-Links zum Quellcode

Alle Quelldateien sind direkt auf GitHub einsehbar:

| Datei | GitHub-Link |
|-------|-------------|
| App-Generator (Haupt-Quellcode) | [tools/build_standalone_preview.py](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/tools/build_standalone_preview.py) |
| Themen-Definition | [tools/generate_passages_json.py](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/tools/generate_passages_json.py) |
| DB-Builder | [tools/build_bible_db.py](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/tools/build_bible_db.py) |
| SQLite-Schema | [schema/bible_schema.sql](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/schema/bible_schema.sql) |
| Serviceworker | [preview/sw.js](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/preview/sw.js) |
| PWA-Manifest | [preview/manifest.json](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/preview/manifest.json) |
| Flutter main.dart | [lib/main.dart](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/lib/main.dart) |
| Generierte App (HTML) | [preview/standalone.html](https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/preview/standalone.html) |

> **Tipp:** Auf GitHub kannst du jede Datei mit dem Bleistift-Symbol ✏️ direkt im Browser bearbeiten.

---

## Die generierte HTML-Datei lesen

`preview/standalone.html` ist sehr groß (~5,8 MB), weil sie alle Bibeldaten eingebettet hat. Um den JavaScript-Teil zu lesen:

1. Öffne die Datei in einem Editor (z.B. VS Code)
2. Gehe zu Zeile ~1000 (nach dem `<script>` Tag)
3. Alles vor `const PAYLOAD_B64` = CSS + HTML-Template
4. `const PAYLOAD_B64` = gzip-komprimierte Bibeldaten (base64)
5. Danach: JavaScript-Logik (LANG dict, THEME_GROUPS, init(), renderHome(), …)

---

*Erstellt von Mario Reiner Denzer · © 2025 · Version 1.0.0*
