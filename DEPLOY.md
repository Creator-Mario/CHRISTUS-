# 🚀 Anleitung: App veröffentlichen (PR mergen + GitHub Pages aktivieren)

Diese Anleitung erklärt Schritt für Schritt, wie du die fertige App über GitHub Pages
für alle Nutzer erreichbar machst.

---

## Schritt 1 – Den Pull Request mergen

Der gesamte Code liegt im Branch `copilot/add-learning-modules` und muss in `main` gemergt werden.

### 1a. Gehe zum Pull Request

Öffne diesen Link direkt im Browser:

```
https://github.com/Creator-Mario/CHRISTUS-/pull/5
```

Du siehst eine Seite mit grünem Titel **„CHRISTUS v1.10: PWA with login…"**

### 1b. Nach unten scrollen

Scrolle ganz nach unten auf der Seite bis du einen großen grünen Button siehst:

```
[ Merge pull request ]
```

### 1c. Merge bestätigen

1. Klicke auf **„Merge pull request"** (grüner Button)
2. Es erscheint ein Bestätigungsdialog – klicke auf **„Confirm merge"**
3. ✅ Fertig – der Code ist jetzt in `main`!

---

## Schritt 2 – GitHub Pages aktivieren

Damit die App unter einer URL erreichbar ist, muss GitHub Pages einmalig eingerichtet werden.

### 2a. Repository-Einstellungen öffnen

Gehe zu deinem Repository:
```
https://github.com/Creator-Mario/CHRISTUS-
```

Klicke oben auf den Tab **„Settings"** (Zahnrad-Symbol, ganz rechts in der Tab-Leiste).

### 2b. Pages-Einstellungen finden

Im linken Menü unter **„Code and automation"** klicke auf **„Pages"**.

### 2c. GitHub Pages einrichten

Stelle folgendes ein:

| Feld | Wert |
|------|------|
| Source | **Deploy from a branch** |
| Branch | **main** |
| Folder | **/ (root)** |

Klicke auf **„Save"**.

### 2d. Warte 1–2 Minuten

GitHub baut die Seite automatisch. Du siehst oben eine grüne Box:

```
✅  Your site is live at https://creator-mario.github.io/CHRISTUS-/
```

---

## 🌐 Die App-URL

Nach der Aktivierung ist die App dauerhaft erreichbar unter:

```
https://creator-mario.github.io/CHRISTUS-/
```

---

## 📱 App auf dem Smartphone installieren (optional)

Die App unterstützt PWA – sie kann wie eine echte App installiert werden:

**Android (Chrome):**
1. App-URL im Browser öffnen
2. Menü (drei Punkte oben rechts) → **„Zum Startbildschirm hinzufügen"**

**iPhone (Safari):**
1. App-URL in Safari öffnen
2. Teilen-Symbol (Quadrat mit Pfeil nach oben) → **„Zum Home-Bildschirm"**

---

## 🔄 Zukünftige Updates

Wenn du in Zukunft Änderungen machst:
1. Änderungen werden automatisch per Pull Request eingereicht
2. Du mergst den PR wie in Schritt 1 beschrieben
3. Alle Nutzer erhalten das Update automatisch beim nächsten App-Start
