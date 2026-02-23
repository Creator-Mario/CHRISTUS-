# 🚀 CHRISTUS App v1.12 — Update senden / Deployment

Das Update ist fertig! Führe **einen** der folgenden Schritte aus:

---

## ✅ Option 1 (empfohlen): Den PR mergen → App wird sofort live

**Direktlink:** 👉 https://github.com/Creator-Mario/CHRISTUS-/pull/6

### Schritt-für-Schritt:

1. Öffne den obigen Link
2. Scrolle ganz nach unten bis du den **grünen Button** siehst:

```
┌─────────────────────────────────────────────────────┐
│  ✅ This branch has no conflicts with the base branch │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [  Merge pull request  ]   ← Diesen Button klicken  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

3. Klicke dann **"Confirm merge"**
4. Fertig! ✨ — Deploy läuft automatisch in ~1 Minute

---

## ✅ Option 2: Manueller Deploy-Trigger

1. Öffne: https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/237480510
2. Klicke **"Run workflow"** (oben rechts)
3. Wähle Branch: `main`
4. Klicke den grünen **"Run workflow"** Button

---

## Was danach passiert (automatisch):

- GitHub Pages zeigt sofort die neue App v1.12
- Der Deploy-Workflow läuft automatisch beim nächsten Push auf `main`
- Die App ist erreichbar unter: **https://creator-mario.github.io/CHRISTUS-/**

---

## Was in v1.12 enthalten ist:

| Datei | Funktion |
|-------|---------|
| `index.html` | Splash-Screen, SW-Registrierung |
| `sw.js` | **NEU** Root-Service-Worker (vollständige Offline-Unterstützung) |
| `app/login.html` | Login – DE/EN übersetzt |
| `app/home.html` | Dashboard mit Fortschrittsbalken – DE/EN übersetzt |
| `app/learn.html` | 7 Kategorien × 42 Module – DE/EN übersetzt |
| `app/settings.html` | Profil, Sprache (nur DE/EN) |
| `app/translations.js` | **NEU** Shared DE/EN Übersetzungen |
| `app/manifest.json` | PWA-Manifest (installierbar) – korrekte start_url |
| `app/icons/icon-192.png` | **NEU** App-Icon 192×192 (Android/Desktop) |
| `app/icons/icon-512.png` | **NEU** App-Icon 512×512 (Android/Desktop) |

### Wichtigste Verbesserungen:
- 📴 **Offline-Modus funktioniert** – App läuft komplett ohne Internet
- 📲 **Android/Desktop-Download (PWA) funktioniert** – Icons vorhanden, Manifest korrigiert
- 🌍 **Nur Deutsch & Englisch** – Spanisch & Portugiesisch entfernt
- 🔤 **Vollständige Übersetzung** – gesamte App-Oberfläche auf Englisch bei Auswahl EN
