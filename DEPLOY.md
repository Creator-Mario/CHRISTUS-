# 🚀 CHRISTUS App v1.12 — Update deployen

## ⚠️ Warum hat das Update nicht funktioniert?

Das Update steckt im **Pull Request #6** und wurde noch **nicht** mit `main` zusammengeführt.
Der Deploy-Workflow läuft **nur** wenn Änderungen auf `main` landen.

---

## ✅ Ein Klick reicht: PR #6 mergen

👉 **https://github.com/Creator-Mario/CHRISTUS-/pull/6**

### So geht's:

1. Öffne den Link oben
2. Scrolle ganz nach unten zum grünen Button:
   ```
   [ Merge pull request ]
   ```
3. Klicke **"Confirm merge"**
4. ✅ Fertig! Der Deploy startet in ~30 Sekunden automatisch.

---

## 🔄 Alternative: Manuell deployen (nach dem Merge)

Falls der automatische Deploy nicht startet:

1. Öffne: https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/237480510
2. Klicke rechts auf **"Run workflow"**
3. Branch = `main` lassen
4. Grünen **"Run workflow"** Button klicken

---

## 📍 Live-URL nach dem Deploy

**https://creator-mario.github.io/CHRISTUS-/**

---

## 📦 Was in v1.12 neu ist

| Änderung | Details |
|----------|---------|
| 📴 **Offline-Modus** | App läuft vollständig ohne Internet |
| 📲 **Android/Desktop-Install** | Icons vorhanden, Manifest korrigiert |
| 🌍 **Nur DE & EN** | Spanisch & Portugiesisch entfernt |
| 🔤 **Vollständige EN-Übersetzung** | Gesamte App-Oberfläche übersetzt |
| `sw.js` | Neuer Root-Service-Worker (vollständiger Scope) |
| `app/translations.js` | Neue Übersetzungsdatei DE/EN |
| `app/icons/` | Neue App-Icons für PWA-Install |
