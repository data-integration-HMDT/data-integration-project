"""ÖPNV-Modul (C): KVB-Haltestellen je Stadtteil – Forschungsfrage 2.

Trello: S-04 (Rohdaten), J-04 (Spatial Join), C-04 (Bereinigung); Rheinseite prüfen: J-05

Schnittstelle (K-01, Abschnitt 6): run() gibt genau 86 Zeilen zurück,
erste Spalte stadtteil_id (Text), danach nur die SPALTEN dieses Moduls.
Einzeln testen:  python -m scrapers.oepnv
"""
import logging

import pandas as pd

from config import settings
from scrapers.geo import auf_alle_stadtteile

log = logging.getLogger(__name__)

NAME = "oepnv"
SPALTEN = ['haltestellen_anz', 'haltestellen_pro_km2']

# Auf True setzen, sobald _download, _parse und _aggregate fertig sind.
# Bis dahin liefert run() 86 Zeilen mit leeren Werten, damit die Pipeline schon läuft.
FERTIG = False


def _download(neu_laden: bool):
    """Rohdaten holen bzw. vorhandene Datei aus data/raw/oepnv/ zurückgeben.

    GTFS-Daten der KVB bzw. Open-Data-Datei laden, stops.txt nach data/raw/oepnv/
    (Abrufdatum im Dateinamen).
    neu_laden=False: vorhandene Rohdaten nutzen, nichts herunterladen.
    """
    raise NotImplementedError


def _parse(rohdaten):
    """stops.txt einlesen; Punkte mit points_from_xy(stop_lon, stop_lat) – erst Länge, dann Breite –
    in settings.CRS_WGS84 anlegen und sofort .to_crs(settings.CRS). Gleise/Steige einer Haltestelle zusammenfassen."""
    raise NotImplementedError


def _aggregate(daten) -> pd.DataFrame:
    """Ergebnis: eine Zeile je stadtteil_id mit den SPALTEN.

    sjoin mit geo.load_stadtteile():
    haltestellen_anz     = Anzahl je Stadtteil (0 ist ein echter Wert!)
    haltestellen_pro_km2 = haltestellen_anz / flaeche_km2
    Die Rheinseite steht schon im Master-Schlüssel (rechtsrheinisch) – hier nicht doppelt ausgeben.
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
