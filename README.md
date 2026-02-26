# CHRISTUS – App

[![Deploy to GitHub Pages](https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/deploy.yml/badge.svg)](https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/deploy.yml)

**Dein täglicher Begleiter im Glauben** – Bibelstellen, Lernmodule und Themenaufgaben als Progressive Web App (PWA).

🌐 **Online-Version:** <https://creator-mario.github.io/CHRISTUS->

---

## 📥 Dateien herunterladen (für Entwickler)

### Option 1 – Repository klonen (empfohlen)

```bash
git clone https://github.com/Creator-Mario/CHRISTUS-.git
cd CHRISTUS-
```

Danach sind alle App-Dateien lokal auf deinem Rechner verfügbar.

### Option 2 – ZIP herunterladen (ohne Git)

1. Oben auf der GitHub-Seite auf den grünen Button **"Code"** klicken
2. **"Download ZIP"** wählen
3. ZIP entpacken – fertig

### Option 3 – Fertiges Offline-Paket (ohne Git oder Build-Tools)

Ein vorkompiliertes ZIP mit Startskript wird automatisch bei jedem Push gebaut:

1. [**Actions → Build Offline Web ZIP**](https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/build-web-offline.yml) öffnen
2. Den letzten erfolgreichen Lauf anklicken
3. Artefakt **`christus-offline-web`** herunterladen
4. ZIP entpacken und `start-local.bat` (Windows) oder `sh start-local.sh` (Mac/Linux) ausführen

---

## 📁 Ordnerstruktur

```
CHRISTUS-/
├── index.html                  # Startseite / Einstiegspunkt
├── language_selection.html     # Sprachauswahl
├── sw.js                       # Service Worker (Offline-Unterstützung)
├── elberfelder_1905.csv        # Bibeltext Deutsch (Elberfelder 1905)
├── kjv_1769.csv                # Bibeltext Englisch (KJV 1769)
├── Lernprogramm_Bibel.csv      # Lernmodule / Kursdaten
│
├── app/                        # ← Haupt-App-Dateien
│   ├── home.html               # Startbildschirm
│   ├── learn.html              # Lernbereich
│   ├── bible.html              # Bibelleser
│   ├── themen.html             # Themenaufgaben
│   ├── settings.html           # Einstellungen
│   ├── install.html            # App weitergeben / installieren
│   ├── login.html              # Anmeldung / Registrierung
│   ├── translations.js         # DE/EN Übersetzungen
│   ├── manifest.json           # PWA-Manifest
│   └── icons/                  # App-Icons
│
├── desktop-electron/           # Windows Desktop (Electron)
├── mobile-capacitor/           # Android (Capacitor)
├── preview/                    # Screenshots / Vorschaubilder
│
├── STANDALONE_BUILD.md         # Build-Anleitung für Electron + Android
└── DEPLOY.md                   # Deployment-Hinweise
```

---

## ▶️ Lokal ausführen

Alle Dateien sind statisches HTML/CSS/JS – es wird **kein Build-Schritt** benötigt.

```bash
# Python 3 (meistens vorinstalliert)
python3 -m http.server 8080

# oder Node.js (npx serve, ebenfalls auf Port 8080)
npx serve . --listen 8080
```

Dann Browser auf **<http://localhost:8080>** öffnen.

> **Hinweis:** Ohne lokalen Server können einige Browser-Sicherheitsrichtlinien
> das Laden von Ressourcen per `file://` blockieren. Ein einfacher HTTP-Server
> (s. o.) löst das.

---

## 🔨 Weiterführende Build-Anleitungen

| Ziel | Anleitung |
|------|-----------|
| Windows EXE / Installer | [STANDALONE_BUILD.md → Electron](STANDALONE_BUILD.md#windows-desktop-build-electron) |
| Android APK / AAB | [STANDALONE_BUILD.md → Android](STANDALONE_BUILD.md#android-build-capacitor) |
| GitHub Pages Deployment | [DEPLOY.md](DEPLOY.md) |
| CI / GitHub Actions | [.github/workflows/](.github/workflows/) |

---

## 📄 Lizenz

Siehe [LICENSE](LICENSE).
