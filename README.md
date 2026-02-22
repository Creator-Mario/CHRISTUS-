# Buch des Dienstes zur Evangelisation
*Creator & Copyright: Mario Reiner Denzer · © 2025 · Version 1.0.0*

---

## Inhaltsverzeichnis

1. [App herunterladen](#-app-herunterladen--sofort-kein-setup)
2. [App-Funktionen im Überblick](#-app-funktionen-im-überblick)
3. [Thematische Bibelstellen (24 Themen)](#-thematische-bibelstellen-24-themen)
4. [GitHub Pages einrichten](#-github-pages-einrichten)
5. [Datenbank lokal bauen](#-datenbank-lokal-bauen)
6. [Flutter App](#-flutter-app)
7. [Dateistruktur](#-dateistruktur)
8. [GitHub Actions Workflows](#-github-actions-workflows)
9. [🔍 Quellcode – Wo finde ich was?](#-quellcode--wo-finde-ich-was)

---

## 💾 App herunterladen – sofort, kein Setup

> **Eine einzige ~6 MB HTML-Datei – vollständig offline – Android · iPhone · Windows · Mac**

### ⬇️ Download-Link (immer aktuell)

👉 **[BDE-Bibel.html öffnen / herunterladen](https://creator-mario.github.io/CHRISTUS-/preview/standalone.html)**

*(Link öffnen → im Browser: Menü → „Seite speichern unter" → BDE-Bibel.html)*

oder direkt die **[App-Startseite öffnen](https://creator-mario.github.io/CHRISTUS-/)**

---

### 🤖 Android – Schritt für Schritt

1. Oben auf **„BDE-Bibel.html herunterladen"** tippen
2. Browser fragt: **Speichern** bestätigen → Datei landet im Ordner „Downloads"
3. **Datei-App** öffnen → Downloads → **BDE-Bibel.html** antippen → öffnet in Chrome
4. Chrome-Menü **⋮ → „Zum Startbildschirm hinzufügen"** → App-Symbol ✅
5. App öffnet sich wie eine native App – **komplett offline nutzbar**

### 💻 Windows / Mac – Schritt für Schritt

1. Oben auf **„BDE-Bibel.html herunterladen"** klicken → Datei speichern
2. **Doppelklick** auf `BDE-Bibel.html` → öffnet im Browser
3. Lesezeichen setzen oder als Desktop-Verknüpfung ablegen ✅

### 🍎 iPhone – Schritt für Schritt

1. Link in **Safari** öffnen
2. Teilen-Symbol **↑** unten antippen
3. **„Zum Home-Bildschirm"** → Hinzufügen ✅

> 📦 ~6 MB · 66 Bücher · 31 102 Verse · 24 Themen · 604 Bibelstellen · 3 Sprachen · komplett offline

---

## ✨ App-Funktionen im Überblick

| Funktion | Beschreibung |
|---|---|
| 🌍 **3 Sprachen** | Deutsch · English · Bahasa Indonesia – vollständige Bibeltexte in allen Sprachen |
| 📖 **Bibel-Browser** | 66 Bücher (AT / NT) als Schaltflächen → Kapitel → Verse |
| ✝ **24 Themen** | Thematisch geordnete Bibelstellen mit 604 Passagen |
| 🎵 **150 Psalmen** | Alle Psalmen einzeln im Themenbereich |
| 📖 **4 Evangelien** | Matthäus, Markus, Lukas, Johannes vollständig kapitelweise |
| 🔍 **Volltext-Suche** | FTS5-Suche über alle 31 102 Verse |
| 🟢🟡🔴 **Markierungen** | Ganze Verse oder einzelne Wörter farbig markieren (grün/gelb/rot) |
| 📝 **Notizen** | Kommentarfunktion unter jeder Bibelstelle |
| 📋 **Notizen-Übersicht** | Alle Kommentare thematisch geordnet in der Notizen-Registerkarte |
| 📤 **Export** | Alle Notizen als `.txt`-Datei herunterladen |
| 📵 **Offline** | Vollständig offline nutzbar (Service Worker, kein Internet nötig) |
| 📲 **PWA** | Als App auf dem Startbildschirm installierbar |
| 🔄 **Update** | Automatisches Update-Banner bei neuer Version |
| 🌐 **Sprachumschalter** | Sprache jederzeit ändern (🌐-Symbol oben) |

---

## 🗂 Thematische Bibelstellen (24 Themen)

### 📜 Altes Testament – Geschichte

| # | Thema | Passagen |
|---|---|---|
| 1 | Schöpfung und Ursprung | 13 |
| 2 | Die Erzväter und Mütter Israels | 26 |
| 3 | Der Auszug aus Ägypten und die Wüstenzeit | 22 |
| 4 | Gesetz und Bund | 14 |
| 5 | Einzug und Landnahme | 10 |
| 6 | Die Zeit der Richter | 11 |
| 7 | Könige und Prophetie in Israel | 23 |
| 8 | Die großen Propheten Elia und Elisa | 17 |

### 🎵 Psalmen & Prophetie

| # | Thema | Passagen |
|---|---|---|
| 9 | Psalmen: Gebete und Lieder (alle 150 Psalmen) | 155 |
| 10 | Prophetische Bücher und Botschaft | 26 |

### 📜 Bund

| # | Thema | Passagen |
|---|---|---|
| 23 | Der alte Bund | 22 |
| 24 | Der neue Bund | 18 |

### ✝ Jesus Christus

| # | Thema | Passagen |
|---|---|---|
| 11 | Jesus Christus: Geburt und Kindheit | 15 |
| 12 | Jesu Wirken: Taufe, Versuchung und Berufung | 16 |
| 13 | Die Bergpredigt | 15 |
| 14 | Gleichnisse Jesu | 24 |
| 15 | Wunder und Heilungen | 15 |
| 16 | Passion und Auferstehung Jesu | 21 |

### 📖 Die vier Evangelien (vollständig)

| # | Thema | Kapitel |
|---|---|---|
| 19 | Matthäus-Evangelium | 28 |
| 20 | Markus-Evangelium | 16 |
| 21 | Lukas-Evangelium | 24 |
| 22 | Johannes-Evangelium | 21 |

### 📬 Apostelgeschichte & Briefe

| # | Thema | Passagen |
|---|---|---|
| 17 | Die Apostelgeschichte und die Briefe | 39 |
| 18 | Die Offenbarung: Vollendung | 13 |

**Gesamt: 24 Themen · 604 Bibelstellen**

---

## 🌐 GitHub Pages einrichten

**Voraussetzung:** Repository muss öffentlich sein  
📖 [→ Ausführliche Anleitung (Deutsch)](docs/anleitung-repository-oeffentlich.md)

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
🤖 **Android (Chrome):** App öffnen → automatisches Banner erscheint nach 2 Sek. → „Hinzufügen"  
🍎 **iPhone (Safari):** Teilen ↑ → „Zum Home-Bildschirm"  
💻 **Desktop (Chrome/Edge):** ⊕-Symbol rechts in der Adressleiste

---

## 🛠 Datenbank lokal bauen

Das Repository enthält die **Elberfelder 1905** Bibel als CSV (`elberfelder_1905.csv`, gemeinfrei).  
Ein Python-Skript erzeugt daraus eine SQLite-Datenbank:

```bash
# Datenbank erzeugen
python3 tools/build_bible_db.py

# Thematische Bibelstellen-JSON erzeugen
python3 tools/generate_passages_json.py

# Selbständige HTML-App generieren (optional)
python3 tools/build_standalone_preview.py
```

### Datenbank-Schema

| Tabelle | Inhalt |
|---|---|
| `books` | 66 Bücher (id, name_de) |
| `bible_verses` | Alle Verse (book_id, chapter, verse, text), PK(book_id,chapter,verse) |
| `bible_verses_fts` | FTS5-Volltextsuche |
| `passage_themes` | 24 Themen (id, name) |
| `key_passages` | 604 thematische Bibelstellen |

> `assets/db/bible.sqlite` ist in `.gitignore` – muss lokal generiert werden.

---

## 📱 Flutter App

Das Repository enthält eine vollständige Flutter-App (Android/iOS).

```bash
# Einmalig: Platform-Dateien erzeugen
flutter create . --project-name bde_bibel --org com.example

# Abhängigkeiten installieren
flutter pub get

# Datenbank generieren (siehe oben)
python3 tools/build_bible_db.py

# App starten
flutter run
```

### App-Struktur (Flutter)

| Pfad | Inhalt |
|---|---|
| `lib/main.dart` | App-Einstieg & Material-Theme (Navy/Gold) |
| `lib/database/bible_db.dart` | SQLite-Helper (kopiert Asset beim ersten Start) |
| `lib/models/book.dart` | Buch-Datenklasse |
| `lib/models/verse.dart` | Vers-Datenklasse |
| `lib/screens/books_screen.dart` | Startseite – alle 66 Bücher |
| `lib/screens/chapters_screen.dart` | Kapitel-Raster für ein Buch |
| `lib/screens/verses_screen.dart` | Versliste für ein Kapitel |
| `lib/screens/search_screen.dart` | Globale FTS5-Suche |

---

## 📁 Dateistruktur

```
CHRISTUS-/
├── elberfelder_1905.csv          # Elberfelder 1905 Bibel (gemeinfrei)
├── index.html                    # Download-Startseite
├── .nojekyll                     # GitHub Pages: Jekyll deaktivieren
│
├── preview/
│   ├── standalone.html           # ★ Vollständige App (~6 MB, selbst enthaltend)
│   ├── manifest.json             # PWA Web App Manifest
│   ├── sw.js                     # Service Worker (Offline-Cache)
│   └── icons/
│       ├── icon-192.png          # App-Symbol 192×192
│       └── icon-512.png          # App-Symbol 512×512
│
├── data/
│   └── key_passages.json         # 24 Themen, 604 Bibelstellen
│
├── assets/
│   └── db/
│       ├── .gitkeep
│       └── bible.sqlite          # SQLite-DB (gitignored, lokal generieren)
│
├── schema/
│   └── bible_schema.sql          # Datenbankschema (books, verses, FTS5, themes)
│
├── tools/
│   ├── build_bible_db.py         # CSV → SQLite-DB
│   ├── generate_passages_json.py # Thematische Bibelstellen → JSON
│   ├── build_standalone_preview.py # Erzeugt standalone.html (3 Sprachen eingebettet)
│   └── vendor/
│       └── pako_inflate.min.js   # Pako-Bibliothek (gzip, alle Browser)
│
├── lib/                          # Flutter-App
│   ├── main.dart
│   ├── database/bible_db.dart
│   ├── models/
│   └── screens/
│
├── electron/                     # Electron Desktop-App (Windows/Mac/Linux)
│   ├── main.js
│   └── package.json
│
├── docs/
│   └── anleitung-repository-oeffentlich.md  # Schritt-für-Schritt-Anleitung
│
├── .github/workflows/
│   ├── deploy-preview.yml        # GitHub Pages: standalone.html deployen
│   ├── build-apk.yml             # Flutter Android APK bauen + Release
│   ├── build-electron.yml        # Electron Windows/Mac/Linux bauen + Release
│   └── release-html.yml          # BDE-Bibel.html als Release-Asset veröffentlichen
│
└── pubspec.yaml                  # Flutter-Projektdatei
```

---

## ⚙️ GitHub Actions Workflows

| Workflow | Auslöser | Ergebnis |
|---|---|---|
| `deploy-preview.yml` | Push auf `main` | `standalone.html` → GitHub Pages |
| `build-apk.yml` | Push auf `main` / manuell | Flutter Android APK → GitHub Release |
| `build-electron.yml` | Push auf `main` / manuell | Windows .exe · Mac .dmg · Linux .AppImage → GitHub Release |
| `release-html.yml` | Push auf `main` / manuell | `BDE-Bibel.html` → GitHub Release Asset |

> Workflows müssen einmalig durch einen Repository-Owner genehmigt werden  
> (GitHub blockiert Copilot-Workflow-Runs bis zur Freigabe).

---

## 📜 Lizenz & Bibeltext

- **App-Code:** siehe `LICENSE`
- **Bibeltext Elberfelder 1905:** gemeinfrei (Public Domain) – siehe CSV-Header
- **King James Version (KJV):** gemeinfrei (Public Domain)
- **Indonesischer Bibeltext:** christos-c/bible-corpus (Forschungskorpus)
- **Creator & Copyright App:** Mario Reiner Denzer © 2025

---

## 🔍 Quellcode – Wo finde ich was?

> **Der vollständige Quellcode** ist in diesem Repository öffentlich einsehbar.

### Haupt-Quellcode der Web-App

| Datei | Was steht drin? |
|-------|-----------------|
| **[`tools/build_standalone_preview.py`](tools/build_standalone_preview.py)** | 🎯 **Alles** – HTML-Gerüst, CSS (Design), komplettes JavaScript (Logik, Sprachen, Themen, Suche, Markierungen, Notizen, Install-Anleitung) |
| [`tools/generate_passages_json.py`](tools/generate_passages_json.py) | Definition aller 24 Themen + 604 Bibelstellen |
| [`tools/build_bible_db.py`](tools/build_bible_db.py) | Erstellt die SQLite-Datenbank aus CSV + JSON |
| [`schema/bible_schema.sql`](schema/bible_schema.sql) | SQLite-Tabellenstruktur |
| [`preview/sw.js`](preview/sw.js) | Service Worker (Offline-Cache, Update-Banner) |
| [`preview/manifest.json`](preview/manifest.json) | PWA-Manifest (App-Icon, Name, display-mode) |
| [`preview/standalone.html`](preview/standalone.html) | 📦 Generierte Datei (~5,8 MB) – enthält alles komprimiert |

### Flutter-App (Dart)

| Datei | Inhalt |
|-------|--------|
| [`lib/main.dart`](lib/main.dart) | Einstiegspunkt, Farbschema, Navigation |
| [`lib/database/bible_db.dart`](lib/database/bible_db.dart) | SQLite-Zugriff (sqflite) |
| [`lib/screens/`](lib/screens/) | Bücher-, Kapitel-, Vers-, Suchansicht |

### Vollständige Dokumentation

�� **[docs/quellcode.md](docs/quellcode.md)** – detaillierte Erklärung jeder Datei, jeder Funktion und des Build-Prozesses
