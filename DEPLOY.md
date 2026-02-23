# 🚀 CHRISTUS App v1.10 — Deployment

Die App ist fertig und wartet nur noch auf diesen **einen Schritt** von dir.

---

## ✅ Alles was du tun musst: Den PR mergen

**Direktlink:** 👉 https://github.com/Creator-Mario/CHRISTUS-/pull/5

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
4. Fertig! ✨

---

## Was danach passiert (automatisch):

- GitHub Pages (bereits auf `main` gesetzt) zeigt sofort die neue App
- Der Deploy-Workflow läuft automatisch beim nächsten Push auf `main`
- Die App ist erreichbar unter: **https://creator-mario.github.io/CHRISTUS-/**

---

## Was in v1.10 enthalten ist:

| Datei | Funktion |
|-------|---------|
| `index.html` | Splash-Screen, SW-Registrierung, Session-Routing |
| `app/login.html` | Personalisierter Login (Name, kein PIN) |
| `app/home.html` | Dashboard mit Fortschrittsbalken |
| `app/learn.html` | 7 Kategorien × 42 Module Lernbereich |
| `app/settings.html` | Profil, Sprache, Offline-Status |
| `app/sw.js` | Service Worker für Offline-Betrieb |
| `app/manifest.json` | PWA-Manifest (installierbar) |

