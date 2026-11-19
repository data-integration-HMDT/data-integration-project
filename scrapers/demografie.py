"""Demografie-Modul (D): Alters- und Haushaltsstruktur je Stadtteil – Forschungsfrage 3.

Trello: S-05 (Rohdaten), J-06 (Zuordnung), C-05 (fehlende Werte)

Schnittstelle (K-01, Abschnitt 6): run() gibt genau 86 Zeilen zurück,
erste Spalte stadtteil_id (Text), danach nur die SPALTEN dieses Moduls.
Einzeln testen:  python -m scrapers.demografie
"""
import logging

import pandas as pd

from config import settings
from scrapers.geo import auf_alle_stadtteile

log = logging.getLogger(__name__)

NAME = "demografie"
SPALTEN = ['einwohner_anz', 'alter_18_29_pct', 'haushalt_groesse_mittel', 'einpersonen_hh_pct']

# Auf True setzen, sobald _download, _parse und _aggregate fertig sind.
# Bis dahin liefert run() 86 Zeilen mit leeren Werten, damit die Pipeline schon läuft.
FERTIG = False


def _download(neu_laden: bool):
    """Rohdaten holen bzw. vorhandene Datei aus data/raw/demografie/ zurückgeben.

    Stadtteilinformationen der Stadt Köln (Offene Daten Köln) nach data/raw/demografie/ laden.
    neu_laden=False: vorhandene Rohdaten nutzen, nichts herunterladen.
    """
    raise NotImplementedError


def _parse(rohdaten):
    """Tabellen einlesen; Stadtteilnummer als Text übernehmen bzw. über geo.name_zu_id() zuordnen."""
    raise NotImplementedError


def _aggregate(daten) -> pd.DataFrame:
    """Ergebnis: eine Zeile je stadtteil_id mit den SPALTEN.

    Eine Zeile je stadtteil_id mit den SPALTEN; Anteile als 0–100.
    Ersatzgröße für Studierende (alter_18_29_pct) in docs/bereinigung.md begründen.
    """
    raise NotImplementedError


def run(neu_laden: bool = False) -> pd.DataFrame:
    if FERTIG:
        ergebnis = _aggregate(_parse(_download(neu_laden)))
    else:
        log.warning("%s: Platzhalter – liefert noch leere Werte", NAME)
        ergebnis = pd.DataFrame(columns=["stadtteil_id", *SPALTEN])

    df = auf_alle_stadtteile(ergebnis)[["stadtteil_id", *SPALTEN]]

    settings.INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.INTERIM / f"{NAME}.csv", index=False, encoding="utf-8")
    mit_werten = int(df[SPALTEN].notna().any(axis=1).sum())
    log.info("%s: %d von %d Stadtteilen mit Werten", NAME, mit_werten, len(df))
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    print(run().head())
