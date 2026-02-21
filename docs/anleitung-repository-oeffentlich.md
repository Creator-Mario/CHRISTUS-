# 🔓 Anleitung: Repository von Privat auf Öffentlich umstellen

> Diese Anleitung erklärt Schritt für Schritt, wie du das Repository
> `Creator-Mario/CHRISTUS-` auf **öffentlich** stellst und danach
> GitHub Pages aktivierst, damit der Live-Link funktioniert.

---

## Teil 1 – Repository öffentlich machen

### Schritt 1 – Settings öffnen

Öffne diesen Link direkt im Browser:

```
https://github.com/Creator-Mario/CHRISTUS-/settings
```

Du musst mit dem GitHub-Account **Creator-Mario** eingeloggt sein.

---

### Schritt 2 – Zur „Danger Zone" scrollen

Scrolle auf der Settings-Seite **ganz nach unten**.
Du siehst dort einen rot markierten Abschnitt mit der Überschrift:

```
╔══════════════════════════════════════════╗
║           Danger Zone                   ║
╚══════════════════════════════════════════╝
```

---

### Schritt 3 – Sichtbarkeit ändern

In der Danger Zone findest du den Eintrag **„Change repository visibility"**.
Klicke den Knopf daneben:

```
[ Change visibility ]
```

---

### Schritt 4 – „Make public" wählen

Es öffnet sich ein Dialog-Fenster.
Wähle dort **„Change to public"** (oder „Make public"):

```
○ Change to private
● Change to public      ← Das hier auswählen
```

Klicke auf **„I want to make this repository public"**.

---

### Schritt 5 – Bestätigen

GitHub zeigt eine Warnung und fragt nach einer Bestätigung.
Tippe deinen **Repository-Namen** in das Eingabefeld:

```
Creator-Mario/CHRISTUS-
```

Klicke danach auf den roten Knopf:

```
[ I understand, make this repository public ]
```

✅ **Das Repository ist jetzt öffentlich!**

---

## Teil 2 – GitHub Pages aktivieren

GitHub Pages hostet die App kostenlos. Die App-Datei (`standalone.html`) ist
**bereits im Repository gespeichert** – es muss kein Workflow laufen!

### Schritt 6 – Pages-Einstellungen öffnen

Öffne diesen Link direkt:

```
https://github.com/Creator-Mario/CHRISTUS-/settings/pages
```

---

### Schritt 7 – Source auf „Deploy from a branch" setzen

Du siehst unter **„Build and deployment"** die Option **„Source"**.

Klicke auf das Dropdown und wähle:

```
Source:  [ Deploy from a branch ]   ← Das auswählen
```

---

### Schritt 8 – Branch und Ordner einstellen

Beim zweiten Dropdown-Menü:

```
Branch:  [ copilot/add-sqlite-bible-database ]    Folder: [ / (root) ]
```

> ℹ️ Wenn der PR bereits in `main` gemerged ist, stattdessen `main` wählen.

Klicke **„Save"**.

---

### Schritt 9 – Warten (~1–2 Minuten)

GitHub bereitet die Seite vor. Nach ca. 1–2 Minuten erscheint oben auf der
Pages-Seite ein grünes Banner mit dem Link.

---

## ✅ Fertig – Dein Live-Link

```
https://creator-mario.github.io/CHRISTUS-/
```

👉 **[Jetzt öffnen](https://creator-mario.github.io/CHRISTUS-/)**

Dieser Link leitet automatisch zur App weiter.

---

## 🔧 Workflows werden als „action_required" blockiert?

GitHub kann Workflows blockieren und eine manuelle Freigabe verlangen.

**So gibst du einen einzelnen Lauf frei:**
1. Öffne: https://github.com/Creator-Mario/CHRISTUS-/actions
2. Klicke auf den betroffenen Lauf (oranges ⚠️-Symbol)
3. Klicke auf **„Approve and run"**

**Oder dauerhaft für alle zulassen:**
- Settings → Actions → General
- „Fork pull request workflows from outside collaborators" → **„Allow all actions and reusable workflows"**
- **Save**

---

## Zusammenfassung aller Links

| Aktion | Link |
|---|---|
| Repository-Einstellungen | https://github.com/Creator-Mario/CHRISTUS-/settings |
| Sichtbarkeit ändern | https://github.com/Creator-Mario/CHRISTUS-/settings (Danger Zone) |
| Pages-Einstellungen | https://github.com/Creator-Mario/CHRISTUS-/settings/pages |
| Workflow-Freigabe | https://github.com/Creator-Mario/CHRISTUS-/actions |
| Live-App | https://creator-mario.github.io/CHRISTUS-/ |

---

## Häufige Fragen

**❓ Warum ist das sicher?**
Der gesamte Inhalt des Repositories darf öffentlich zugänglich sein –
der Bibel-Text (Elberfelder 1905) ist **Public Domain**.
Es gibt keine Passwörter, API-Keys oder private Daten im Repository.

**❓ Was passiert, wenn ich es wieder auf privat stelle?**
Der Live-Link hört auf zu funktionieren. Die heruntergeladene standalone.html
funktioniert weiterhin offline.

**❓ Der Link zeigt 404 – was tun?**
1. Überprüfe, ob das Repository öffentlich ist
2. Gehe zu Settings → Pages und prüfe, ob der Branch eingestellt ist
3. Warte 2–3 Minuten nach dem Speichern der Pages-Einstellungen
4. Seite im Browser neu laden (Strg+F5)
