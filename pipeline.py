"""Pipeline (verantwortlich: D): führt alle Module zu einem Datensatz zusammen.

Aufruf (im Hauptordner des Repos):
    python pipeline.py               # nutzt vorhandene Rohdaten
    python pipeline.py --neu-laden   # lädt bzw. scrapt alles neu

Ergebnis: data/processed/koeln_stadtteile.csv – eine Zeile je Stadtteil (86).
"""
import argparse
import logging

from config import settings
from scrapers import demografie, gruenflaechen, mieten, oepnv
from scrapers.geo import lade_schluessel

MODULE = [mieten, gruenflaechen, oepnv, demografie]
log = logging.getLogger("pipeline")


def main(neu_laden: bool = False):
    datensatz = lade_schluessel()  # stadtteil_id, Namen, Bezirk, rechtsrheinisch

    for modul in MODULE:
        df = modul.run(neu_laden=neu_laden)
        doppelt = (set(df.columns) & set(datensatz.columns)) - {"stadtteil_id"}
        if doppelt:
            raise ValueError(f"{modul.NAME}: Spalten gibt es schon: {sorted(doppelt)}")
        datensatz = datensatz.merge(df, on="stadtteil_id", how="left", validate="one_to_one")

    if len(datensatz) != settings.ANZAHL_STADTTEILE:
        raise ValueError(f"Erwartet {settings.ANZAHL_STADTTEILE} Zeilen, erhalten {len(datensatz)}")

    settings.PROCESSED.mkdir(parents=True, exist_ok=True)
    ziel = settings.PROCESSED / "koeln_stadtteile.csv"
    datensatz.to_csv(ziel, index=False, encoding="utf-8")

    kennzahlen = [s for m in MODULE for s in m.SPALTEN]
    fehlend = datensatz[kennzahlen].isna().sum()
    log.info("Fertig: %s (%d Zeilen, %d Spalten)", ziel.relative_to(settings.ROOT), *datensatz.shape)
    log.info("Fehlende Werte je Kennzahl:\n%s", fehlend.to_string())
    return datensatz


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kölner Mietpreise – Datensatz erzeugen")
    parser.add_argument("--neu-laden", action="store_true", help="Rohdaten neu herunterladen bzw. scrapen")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    main(neu_laden=parser.parse_args().neu_laden)
