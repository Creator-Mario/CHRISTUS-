# 🚀 Anleitung: App veröffentlichen – 3 Schritte

---

## ⚠️ WARUM DIE APP NOCH ALT IST

Der Pull Request (PR) ist noch im **Draft-Modus** (Entwurf).
Im Draft-Modus ist der grüne „Merge"-Button **ausgeblendet**.
Du musst zuerst den Draft-Modus deaktivieren.

---

## Schritt 1 – Draft-Modus deaktivieren

### 1a. Öffne diesen Link:
```
https://github.com/Creator-Mario/CHRISTUS-/pull/5
```

### 1b. Scrolle ganz nach UNTEN auf der Seite

Am Ende der Seite siehst du NICHT den grünen Merge-Button,
sondern stattdessen einen **grauen Button** mit der Aufschrift:

```
┌─────────────────────────────────┐
│  Ready for review               │  ← DIESEN BUTTON KLICKEN
└─────────────────────────────────┘
```

Er befindet sich links neben dem Merge-Bereich und sieht so aus:
- Grauer/weißer Hintergrund
- Kleines Stift-Symbol davor
- Text: **"Ready for review"**

### 1c. Bestätige den Dialog

Nach dem Klick erscheint ein kleines Popup:
```
┌────────────────────────────────────────────┐
│  This pull request is still a work in      │
│  progress. Do you want to mark it ready    │
│  for review?                               │
│                                            │
│  [Cancel]  [Ready for review]              │ ← KLICK
└────────────────────────────────────────────┘
```

Klicke auf **„Ready for review"** (grüner Button im Dialog).

---

## Schritt 2 – PR mergen

Jetzt erscheint der grüne Merge-Button:

```
┌─────────────────────────────────┐
│  ✓ Merge pull request           │  ← KLICKEN
└─────────────────────────────────┘
```

Danach:
```
┌─────────────────────────────────┐
│  Confirm merge                  │  ← KLICKEN
└─────────────────────────────────┘
```

✅ Fertig! Der Code ist jetzt in `main`.

---

## Schritt 3 – GitHub Pages auf GitHub Actions umstellen

### 3a. Öffne diesen Link direkt:
```
https://github.com/Creator-Mario/CHRISTUS-/settings/pages
```

### 3b. Ändere die Source

Du siehst:
```
Build and deployment
Source: [Deploy from a branch ▼]
```

Klicke auf das Dropdown **„Deploy from a branch"** und wähle:
```
→ GitHub Actions
```

Klicke **Save**.

### 3c. Warte 2 Minuten

GitHub deployt automatisch. Du siehst dann:
```
✅ Your site is live at https://creator-mario.github.io/CHRISTUS-/
```

---

## 🌐 Die App ist dann erreichbar unter:

```
https://creator-mario.github.io/CHRISTUS-/
```

---

## 📱 App auf Smartphone installieren

**Android (Chrome):** Menü (⋮) → „Zum Startbildschirm hinzufügen"

**iPhone (Safari):** Teilen (□↑) → „Zum Home-Bildschirm"

---

## 🔄 Zukünftige Updates

Nach dem ersten Merge laufen alle zukünftigen Updates automatisch —
du musst nur den PR mergen und GitHub Pages deployt von selbst.
