# Git-Workflow

So arbeiten wir im Repo. Kurzfassung: **Eine Trello-Karte = ein Branch = ein Pull Request.** Niemand pusht direkt auf `main`.

---

## 1. Einmalig: Einrichten

```bash
git clone https://github.com/data-integration-HMDT/data-integration-project.git
cd data-integration-project

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
crawl4ai-setup                     # lädt den Browser für Crawl4AI

cp .env.example .env               # danach eigene API-Schlüssel eintragen
pytest                             # alles grün? Dann passt die Einrichtung
```

---

## 2. Für jede Trello-Karte

### Anfangen
1. Karte in Trello nach **„In Arbeit“** ziehen
2. Neuesten Stand holen und Branch anlegen:
   ```bash
   git checkout main
   git pull
   git checkout -b S-04-kvb-haltestellen     # <Karten-ID>-<kurze-beschreibung>
   ```

### Arbeiten
- Lieber oft kleine Commits als einen großen
- Commit-Nachricht beginnt mit der Karten-ID und sagt, **was** sich geändert hat:
  ```bash
  git add scrapers/oepnv.py
  git commit -m "S-04: stops.txt herunterladen und in data/raw speichern"
  ```
- `git add` gezielt für eure Dateien – nicht blind `git add .`, ohne vorher `git status` anzuschauen

### Abgeben
1. Tests laufen lassen und den neuesten `main` übernehmen:
   ```bash
   pytest
   git pull origin main      # holt Änderungen der anderen in euren Branch
   pytest                    # nach dem Pull noch einmal
   ```
2. Pushen:
   ```bash
   git push -u origin S-04-kvb-haltestellen
   ```
3. Auf GitHub **Pull Request** öffnen
   - Titel: `S-04: Rohdaten KVB-Haltestellen`
   - Vorlage ausfüllen (Checkliste erscheint automatisch)
   - Reviewer festlegen (siehe Abschnitt 3)
4. Karte in Trello nach **„Review“** ziehen

### Nach dem Merge
1. Auf GitHub **„Delete branch“** klicken
2. Lokal aufräumen:
   ```bash
   git checkout main
   git pull
   git branch -d S-04-kvb-haltestellen
   ```
3. Karte in Trello nach **„Fertig“** ziehen

---

## 3. Regeln

**`main` ist geschützt.** Änderungen nur per Pull Request mit 1 Review.

**Wer reviewt?**

| Geänderte Datei | Reviewer |
|---|---|
| Eigenes Modul (`scrapers/mieten.py` usw.) und eigene Tests | eine beliebige andere Person |
| `scrapers/base.py` | A |
| `scrapers/geo.py`, `config/settings.py`, `config/stadtteile.csv`, `pipeline.py`, `test/test_schnittstelle.py` | D |
| `.gitignore`, `requirements.txt` | D |

**Review innerhalb von 48 Stunden.** Wer Review-Anfragen nicht schafft, sagt kurz in der Gruppe Bescheid.

**Was reviewt wird:** Läuft `pytest`? Hält das Modul die Schnittstelle ein (86 Zeilen, `stadtteil_id` als Text)? Stehen neue Spalten im Data Dictionary? Sind Rohdaten, `.env` oder Schlüssel versehentlich dabei?

**Mergen:** „Squash and merge“ – dann steht pro Karte genau ein Commit in `main`.

**Nie committen:** `.env`, API-Schlüssel, Dateien aus `data/raw/` und `data/interim/`. Die `.gitignore` fängt das ab – trotzdem vor jedem Commit `git status` anschauen.

**Ab dem Stichtag 16.12.:** keine neuen Funktionen mehr, nur noch Fehlerbehebungen (Branch-Name `fix-<beschreibung>`).

---

## 4. Wenn etwas schiefgeht

**`git push` wird abgelehnt („rejected … fetch first“)**
Jemand anderes hat vorher gepusht → `git pull origin main`, dann erneut pushen.

**Konflikt beim `git pull`**
1. `git status` zeigt die betroffenen Dateien
2. In der Datei die Stellen zwischen `<<<<<<<` und `>>>>>>>` bereinigen (beide Versionen sinnvoll zusammenführen)
3. ```bash
   git add <datei>
   git commit
   pytest
   ```
Unsicher? Lieber in der Gruppe fragen, als eine Version der anderen zu überschreiben.

**Versehentlich `.env` oder einen API-Schlüssel gepusht**
Sofort in der Gruppe melden und den Schlüssel beim Anbieter **neu erzeugen**. Löschen aus dem Repo reicht nicht – er bleibt in der Git-Historie.

**Auf dem falschen Branch gearbeitet (noch nicht committet)**
```bash
git stash
git checkout -b <richtiger-branch>
git stash pop
```
