# 🚀 CHRISTUS App v1.15 — Deploy-Status

## 📍 Live-URL

**https://creator-mario.github.io/CHRISTUS-/**

---

## ✅ Automatischer Deploy

Der Deploy-Workflow läuft automatisch bei jedem Push auf:
- `main`
- `copilot/update-sende`

Das heißt: Sobald ein Commit auf einem dieser Branches landet, wird die App
automatisch auf GitHub Pages aktualisiert (~30 Sekunden).

---

## 🔄 Manuell deployen

Falls nötig:

1. Öffne: https://github.com/Creator-Mario/CHRISTUS-/actions/workflows/deploy.yml
2. Klicke rechts auf **"Run workflow"**
3. Branch wählen (`main` oder `copilot/update-sende`)
4. Grünen **"Run workflow"** Button klicken

---

## 📦 Was in v1.15 neu ist

| Änderung | Details |
|----------|---------|
| 🔢 **Version 1.15** | Alle Seiten auf v1.15 aktualisiert |
| 🔔 **Update-Banner** | Sichtbar auf ALLEN App-Seiten (Home, Lernen, Bibel, Themen, Einstellungen) |
| 🛠️ **Update-Mechanismus** | SW wartet jetzt korrekt im `waiting`-Zustand – Banner erscheint zuverlässig |
| 📖 **Bibel AT/NT** | Altes und Neues Testament als Unterbereiche |
| 🗂️ **Themen-Akkordeon** | Hierarchische Darstellung mit AT/NT-Trennern |
| 🔐 **E-Mail-Auth** | Vorname/Nachname/E-Mail-Registrierung, OTP, Passwort-Änderung |
