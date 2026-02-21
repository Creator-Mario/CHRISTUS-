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

GitHub Pages ist der kostenlose Hosting-Dienst für öffentliche Repositories.
Damit wird der Live-Link `creator-mario.github.io/CHRISTUS-/preview/` aktiv.

### Schritt 6 – Pages-Einstellungen öffnen

Öffne diesen Link:

```
https://github.com/Creator-Mario/CHRISTUS-/settings/pages
```

---

### Schritt 7 – Quelle auf „GitHub Actions" setzen

Du siehst unter **„Build and deployment"** die Option **„Source"**.

Klicke auf das Dropdown-Menü und wähle:

```
Source:  [ GitHub Actions ]   ← Das auswählen (nicht "Deploy from a branch")
```

Klicke **„Save"**.

---

### Schritt 8 – Workflow manuell starten

Öffne die Actions-Seite:

```
https://github.com/Creator-Mario/CHRISTUS-/actions
```

Auf der linken Seite siehst du:

```
Workflows
─────────────────────────────────
▶ Deploy Bible Preview to GitHub Pages   ← Hier klicken
```

Klicke auf diesen Workflow, dann oben rechts auf:

```
[ Run workflow ▼ ]
  Branch: main
  [ Run workflow ]   ← Grünen Knopf klicken
```

---

### Schritt 9 – Warten (~2 Minuten)

Der Workflow läuft jetzt. Du kannst den Fortschritt live beobachten.
Ein grünes ✅ bedeutet: Deployment erfolgreich.

---

## ✅ Fertig – Dein Live-Link

Nach dem erfolgreichen Deployment ist die App erreichbar unter:

```
https://creator-mario.github.io/CHRISTUS-/preview/
```

👉 **[Jetzt öffnen](https://creator-mario.github.io/CHRISTUS-/preview/)**

---

## Zusammenfassung aller Links

| Aktion | Link |
|---|---|
| Repository-Einstellungen | https://github.com/Creator-Mario/CHRISTUS-/settings |
| Sichtbarkeit ändern | https://github.com/Creator-Mario/CHRISTUS-/settings (Danger Zone) |
| Pages-Einstellungen | https://github.com/Creator-Mario/CHRISTUS-/settings/pages |
| Workflow starten | https://github.com/Creator-Mario/CHRISTUS-/actions |
| Live-Vorschau | https://creator-mario.github.io/CHRISTUS-/preview/ |

---

## Häufige Fragen

**❓ Warum ist das sicher?**  
Der gesamte Inhalt des Repositories ist öffentlich zugänglich gemacht werden
darf – der Bibel-Text (Elberfelder 1905) ist **Public Domain**.
Es gibt keine Passwörter, API-Keys oder private Daten im Repository.

**❓ Was passiert mit dem Repository, wenn ich es öffentlich mache?**  
Jeder im Internet kann den Code und die Dateien lesen. Niemand kann jedoch
ohne deine Erlaubnis Änderungen vornehmen.

**❓ Kann ich es wieder auf privat stellen?**  
Ja, jederzeit. Gehe wieder zu Settings → Danger Zone → Change visibility
→ Change to private.

**❓ Der Workflow schlägt fehl – was tun?**  
Öffne https://github.com/Creator-Mario/CHRISTUS-/actions, klicke auf den
fehlgeschlagenen Lauf und lies die roten Fehlermeldungen. Häufigste Ursache:
Pages wurde noch nicht aktiviert (Schritt 6–7 wiederholen).
