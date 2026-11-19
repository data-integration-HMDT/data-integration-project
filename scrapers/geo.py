"""Gemeinsame Helfer rund um die Stadtteile (verantwortlich: D).

- lade_schluessel()      Master-Schlüssel aus config/stadtteile.csv
- auf_alle_stadtteile()  bringt jedes Modul-Ergebnis auf genau 86 Zeilen
- normalisiere_name()    vergleicht Stadtteilnamen unabhängig von Umlauten/Schreibweise
- name_zu_id()           Wörterbuch Name/Schreibvariante -> stadtteil_id (für A, J-01)
- load_stadtteile()      Stadtteilgrenzen als GeoDataFrame (K-03, noch offen)
"""
import re
import unicodedata

import pandas as pd

from config import settings

_ERSETZUNG = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def normalisiere_name(name) -> str:
    """'Köln-Altstadt-Süd', 'Altstadt/Süd', 'ALTSTADT SUED' -> 'altstadt sued'."""
    s = unicodedata.normalize("NFC", str(name)).strip().lower().translate(_ERSETZUNG)
    s = re.sub(r"^koeln[\s\-–]+", "", s)
    s = re.sub(r"[/\-–]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def lade_schluessel(mit_varianten: bool = False) -> pd.DataFrame:
    """Master-Schlüssel: stadtteil_id, stadtteil_name, stadtbezirk_id, stadtbezirk_name, rechtsrheinisch."""
    df = pd.read_csv(
        settings.STADTTEILE,
        dtype={"stadtteil_id": str, "stadtbezirk_id": str},
        encoding="utf-8",
    )
    if not mit_varianten:
        df = df.drop(columns=["schreibvarianten"])
    return df


def name_zu_id() -> dict:
    """Normalisierter Name bzw. Schreibvariante -> stadtteil_id."""
    df = lade_schluessel(mit_varianten=True)
    zuordnung = {}
    for sid, name, varianten in zip(df.stadtteil_id, df.stadtteil_name, df.schreibvarianten.fillna("")):
        for n in [name, *varianten.split("|")]:
            if n:
                zuordnung[normalisiere_name(n)] = sid
    return zuordnung


def auf_alle_stadtteile(df: pd.DataFrame) -> pd.DataFrame:
    """Hängt ein Modul-Ergebnis an den Master-Schlüssel an.

    Ergebnis: genau 86 Zeilen; Stadtteile ohne Daten bekommen NaN.
    Bricht ab bei fehlender ID-Spalte, unbekannten IDs oder doppelten IDs.
    """
    if "stadtteil_id" not in df.columns:
        raise ValueError("Spalte 'stadtteil_id' fehlt im Modul-Ergebnis.")
    df = df.copy()
    df["stadtteil_id"] = df["stadtteil_id"].astype(str)
    basis = lade_schluessel()[["stadtteil_id"]]
    unbekannt = sorted(set(df["stadtteil_id"]) - set(basis["stadtteil_id"]))
    if unbekannt:
        raise ValueError(f"Unbekannte stadtteil_id(s): {unbekannt[:10]}")
    return basis.merge(df, on="stadtteil_id", how="left", validate="one_to_one")


def load_stadtteile():
    """Stadtteilgrenzen als GeoDataFrame in settings.CRS (EPSG:25832) mit Spalte flaeche_km2.

    TODO (D, K-03): Geodatei nach data/raw/geo/ laden, nach settings.CRS umwandeln,
    stadtteil_id als Text, flaeche_km2 = gdf.area / 1_000_000.
    """
    raise NotImplementedError("K-03: Stadtteilgrenzen sind noch nicht hinterlegt (data/raw/geo/).")
