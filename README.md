# Buch des Dienstes zur Evangelisation
*Creator & Copyright: Mario Reiner Denzer · © 2025 · Version 1.0.0*

---

## 💾 App sofort herunterladen (kein Setup nötig)

> **Eine einzige HTML-Datei – komplett offline – funktioniert auf jedem Gerät**

### Schritt 1 – Datei herunterladen

👉 **[HIER KLICKEN → BdE-Bibel.html herunterladen](https://raw.githubusercontent.com/Creator-Mario/CHRISTUS-/copilot/add-sqlite-bible-database/preview/standalone.html)**

*Rechtsklick auf den Link → „Speichern unter" → Speichern als `BdE-Bibel.html`*

### Schritt 2 – Datei öffnen

Doppelklick auf die heruntergeladene Datei `BdE-Bibel.html` → öffnet sich im Browser

✅ **Funktioniert sofort – komplett ohne Internet**

### Schritt 3 – Weitergeben

Datei per **WhatsApp · E-Mail · USB-Stick · Bluetooth** an andere senden

> 📦 ~2 MB · alle 31 102 Bibelverse · 18 Themen · 359 Bibelstellen

---

## 🌐 Als App im Browser / auf dem Handy (GitHub Pages)

**Voraussetzung:** Repository muss öffentlich sein  
📖 [→ Schritt-für-Schritt-Anleitung (Deutsch)](docs/anleitung-repository-oeffentlich.md)

### Schritt 1 – Repository öffentlich stellen

1. Öffne: **https://github.com/Creator-Mario/CHRISTUS-/settings**
2. Ganz nach unten scrollen bis **„Danger Zone"**
3. Klicke **„Change visibility"** → **„Change to public"**
4. Bestätige mit deinem GitHub-Passwort

### Schritt 2 – GitHub Pages aktivieren

1. Öffne: **https://github.com/Creator-Mario/CHRISTUS-/settings/pages**
2. Unter **„Build and deployment"** → **„Source"** → **„Deploy from a branch"** wählen
3. Branch: **`copilot/add-sqlite-bible-database`** · Folder: **`/ (root)`** → **Save** klicken
4. **1–2 Minuten warten** (GitHub baut die Seite)

### Schritt 3 – App aufrufen

👉 **https://creator-mario.github.io/CHRISTUS-/**

**Als App auf dem Handy installieren:**  
🤖 **Android (Chrome):** Menü ⋮ → „Zum Startbildschirm hinzufügen"  
🍎 **iPhone (Safari):** Teilen ↑ → „Zum Home-Bildschirm"  
💻 **Desktop (Chrome/Edge):** ⊕-Symbol rechts in der Adressleiste

---

## Bible Database

The repository includes the **Elberfelder 1905** German Bible translation as a
CSV file (`elberfelder_1905.csv`).  The text is in the **Public Domain** (see
the header of the CSV file).

A Python build script converts the CSV into a SQLite database
(`assets/db/bible.sqlite`) that is suitable for use in Flutter apps and
supports:

- Hierarchical Bible browsing (book → chapter → verses)
- Global full-text search via an **FTS5** virtual table

### Prerequisites

- Python 3.8 or later (no third-party packages required – uses the standard
  library only)

### Building the database

Run the following command from the **repository root**:

```bash
python3 tools/build_bible_db.py
```

The script will:

1. Read `elberfelder_1905.csv`
2. Apply the schema in `schema/bible_schema.sql`
3. Write `assets/db/bible.sqlite`

Progress and validation counts are printed to stdout.

### Browser preview (ohne Flutter)

Um die App im Browser zu testen, ohne Flutter installieren zu müssen:

```bash
# 1. Datenbank erstellen (einmalig)
python3 tools/build_bible_db.py

# 2. Lokalen HTTP-Server starten (Repository-Stammverzeichnis!)
python3 -m http.server 8000

# 3. Im Browser öffnen
#    http://localhost:8000/preview/
```

Die Vorschau (`preview/index.html`) lädt die SQLite-Datenbank direkt im
Browser über [sql.js](https://sql.js.org/) und bietet:

- 📖 Alle 66 Bücher, Kapitel und Verse
- 🔍 Volltext-Suche (FTS5) mit Treffer-Hervorhebung
- ← Zurück-Navigation

> **Hinweis:** Der lokale HTTP-Server ist notwendig, weil Browser das Laden
> lokaler Dateien über `file://` aus Sicherheitsgründen blockieren.

### Database schema

| Table | Purpose |
|---|---|
| `books` | One row per Bible book (id 1–66, German name) |
| `bible_verses` | All verses, primary key `(book_id, chapter, verse)` |
| `bible_verses_fts` | FTS5 virtual table for full-text search |

#### Example queries

```sql
-- List all books
SELECT id, name_de FROM books ORDER BY id;

-- Read Genesis chapter 1
SELECT verse, text
FROM   bible_verses
WHERE  book_id = 1 AND chapter = 1
ORDER  BY verse;

-- Full-text search
SELECT b.name_de, v.chapter, v.verse, v.text
FROM   bible_verses_fts f
JOIN   bible_verses v ON v.book_id = f.book_id
                     AND v.chapter = f.chapter
                     AND v.verse   = f.verse
JOIN   books b ON b.id = f.book_id
WHERE  bible_verses_fts MATCH 'Licht'
LIMIT  20;
```

> **Note:** `assets/db/bible.sqlite` is listed in `.gitignore` and must be
> regenerated locally after checkout.

---

## Flutter App

The repository contains a complete Flutter app that lets you browse the Bible
hierarchically (Book → Chapter → Verses) and perform a full-text search.

### Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) ≥ 3.0

### First-time setup

```bash
# 1. Generate platform-specific files (Android, iOS, …)
flutter create . --project-name christus --org com.example

# 2. Install Dart dependencies
flutter pub get

# 3. Build the database asset (see above)
python3 tools/build_bible_db.py
```

### Run the app

```bash
flutter run
```

### App structure

| Path | Purpose |
|---|---|
| `lib/main.dart` | App entry point & Material theme |
| `lib/database/bible_db.dart` | SQLite helper (copies asset on first launch) |
| `lib/models/` | `Book` and `Verse` data classes |
| `lib/screens/books_screen.dart` | Home – list of all 66 books |
| `lib/screens/chapters_screen.dart` | Chapter grid for a selected book |
| `lib/screens/verses_screen.dart` | Verse list for a selected chapter |
| `lib/screens/search_screen.dart` | Global FTS5 full-text search |

---

## GitHub Pages einrichten

Damit der Link **[https://creator-mario.github.io/CHRISTUS-/preview/](https://creator-mario.github.io/CHRISTUS-/preview/)** funktioniert, muss GitHub Pages **einmalig** im Repository aktiviert werden:

1. Gehe zu **Settings → Pages** im Repository  
   `https://github.com/Creator-Mario/CHRISTUS-/settings/pages`
2. Unter **Source** → **GitHub Actions** auswählen
3. Speichern – fertig!

Der Workflow (`.github/workflows/deploy-preview.yml`) läuft automatisch bei
jedem Push auf `main` und veröffentlicht die aktualisierte Vorschau.

Du kannst den Workflow auch manuell starten:  
**Actions → "Deploy Bible Preview to GitHub Pages" → Run workflow**
