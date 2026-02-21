# CHRISTUS-
Bibelstellen

## ⚠️ EINE EINMALIGE AKTION NÖTIG – GitHub Pages aktivieren

Der Deployment-Workflow hat bereits gestartet. Du musst **einmalig** folgendes tun:

### 👉 Jetzt hier klicken:
**https://github.com/Creator-Mario/CHRISTUS-/settings/pages**

Dann:
1. Unter **"Source"** → **"GitHub Actions"** auswählen (nicht "Deploy from a branch"!)
2. Auf **"Save"** klicken
3. Zurück zur Actions-Seite gehen und den Workflow erneut starten:  
   **https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/deploy-preview.yml**  
   → **"Run workflow"** → **"Run workflow"** (grüner Button)
4. ~2 Minuten warten
5. ✅ Link ist live: **https://creator-mario.github.io/CHRISTUS-/**

---

## 📥 Sofort-Link – Jetzt herunterladen & öffnen (kein Setup nötig)

**Kein Server, kein Flutter, kein Setup nötig!**

### 👉 Direkter Download-Link (funktioniert sofort):

**[Hier klicken → Raw-Datei speichern](https://raw.githubusercontent.com/Creator-Mario/CHRISTUS-/copilot/add-sqlite-bible-database/preview/standalone.html)**

Oder über GitHub:  
**https://github.com/Creator-Mario/CHRISTUS-/blob/copilot/add-sqlite-bible-database/preview/standalone.html**
→ Dann oben rechts auf **„Raw"** klicken → Rechtsklick → **„Speichern unter"** → Doppelklick auf die gespeicherte Datei

✅ Alle 31.102 Verse, 66 Bücher und Volltextsuche – komplett offline, ohne Server!

---

## 🌐 Live-Vorschau (nach GitHub Pages Aktivierung)


**👉 [https://creator-mario.github.io/CHRISTUS-/preview/](https://creator-mario.github.io/CHRISTUS-/preview/)**

> Die Vorschau wird automatisch per GitHub Actions aktualisiert, sobald
> Änderungen auf `main` gepusht werden.  
> GitHub Pages muss einmalig im Repository aktiviert werden – siehe [Einrichtung](#github-pages-einrichten).

---

## 🔓 Repository öffentlich machen

Damit GitHub Pages (kostenlos) und der Live-Link funktionieren, muss das
Repository auf **öffentlich** gestellt werden.

📖 **[→ Detaillierte Schritt-für-Schritt-Anleitung](docs/anleitung-repository-oeffentlich.md)**

### Kurzfassung (5 Schritte)

| # | Was | Wo |
|---|---|---|
| 1 | Repository-Einstellungen öffnen | [github.com/Creator-Mario/CHRISTUS-/settings](https://github.com/Creator-Mario/CHRISTUS-/settings) |
| 2 | Ganz nach unten scrollen → **Danger Zone** | auf der Settings-Seite |
| 3 | **„Change visibility"** → **„Change to public"** klicken | in der Danger Zone |
| 4 | Repository-Namen `Creator-Mario/CHRISTUS-` eintippen und bestätigen | im Bestätigungs-Dialog |
| 5 | Pages aktivieren: **Settings → Pages → Source → GitHub Actions → Save** | [github.com/Creator-Mario/CHRISTUS-/settings/pages](https://github.com/Creator-Mario/CHRISTUS-/settings/pages) |

Danach den Workflow starten:  
👉 [Actions → „Deploy Bible Preview to GitHub Pages" → „Run workflow"](https://github.com/Creator-Mario/CHRISTUS-/actions)

Nach ~2 Minuten ist der Link **https://creator-mario.github.io/CHRISTUS-/preview/** live. ✅

> **Sicher?** Ja – der Bibel-Text (Elberfelder 1905) ist Public Domain.
> Es gibt keine Passwörter oder private Daten im Repository.

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
