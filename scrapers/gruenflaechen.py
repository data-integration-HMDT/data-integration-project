"""Grünflächen-Modul (B): Grünanteil und Distanz zum nächsten Park – Forschungsfrage 1.

Trello: S-03 (Rohdaten), J-02/J-03 (Spatial Join), C-03 (Bereinigung)

Schnittstelle (K-01, Abschnitt 6): run() gibt genau 86 Zeilen zurück,
erste Spalte stadtteil_id (Text), danach nur die SPALTEN dieses Moduls.
Einzeln testen:  python -m scrapers.gruenflaechen
"""
import logging

import pandas as pd

from config import settings
from scrapers.geo import auf_alle_stadtteile

log = logging.getLogger(__name__)

NAME = "gruenflaechen"
SPALTEN = ['gruen_anteil_pct', 'park_distanz_m']

# Auf True setzen, sobald _download, _parse und _aggregate fertig sind.
# Bis dahin liefert run() 86 Zeilen mit leeren Werten, damit die Pipeline schon läuft.
FERTIG = False


def _download(neu_laden: bool):
    """Rohdaten holen bzw. vorhandene Datei aus data/raw/gruenflaechen/ zurückgeben.

    Parks/Grünflächen über die Overpass-API bzw. Offene Daten Köln als GeoJSON
    nach data/raw/gruen/ laden (Abrufdatum im Dateinamen).
    neu_laden=False: vorhandene Rohdaten nutzen, nichts herunterladen.
    """
    raise NotImplementedError


def _parse(rohdaten):
    """GeoJSON mit geopandas einlesen und sofort .to_crs(settings.CRS); Kategorien filtern (park, garden, …)."""
    raise NotImplementedError


def _aggregate(daten) -> pd.DataFrame:
    """Ergebnis: eine Zeile je stadtteil_id mit den SPALTEN.

    Mit geo.load_stadtteile() verschneiden (überlappende Polygone vorher vereinigen):
    gruen_anteil_pct = Grünfläche / Stadtteilfläche * 100 (0–100)
    park_distanz_m   = mittlere Distanz zum nächsten Park in Metern
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
