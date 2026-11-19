"""Prüft, ob alle Module die Schnittstelle aus K-01 (Abschnitt 6) einhalten.

Aufruf im Hauptordner:  pytest
"""
import pandas as pd
import pytest

from config import settings
from scrapers import demografie, gruenflaechen, mieten, oepnv
from scrapers.geo import lade_schluessel, normalisiere_name

MODULE = [mieten, gruenflaechen, oepnv, demografie]


@pytest.fixture(scope="session")
def schluessel():
    return lade_schluessel(mit_varianten=True)


@pytest.fixture(scope="session")
def ergebnisse():
    return {m.NAME: m.run() for m in MODULE}


# --- Master-Schlüssel ---------------------------------------------------------

def test_schluessel_vollstaendig(schluessel):
    assert len(schluessel) == settings.ANZAHL_STADTTEILE
    assert schluessel.stadtteil_id.is_unique
    assert schluessel.stadtteil_id.str.fullmatch(r"[1-9]\d{2}").all()
    assert (schluessel.stadtteil_id.str[0] == schluessel.stadtbezirk_id).all()


def test_schluessel_namen_eindeutig_nach_normalisierung(schluessel):
    assert schluessel.stadtteil_name.map(normalisiere_name).is_unique


# --- Module -------------------------------------------------------------------

@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.NAME)
def test_modul_schnittstelle(modul, ergebnisse, schluessel):
    df = ergebnisse[modul.NAME]
    assert list(df.columns) == ["stadtteil_id", *modul.SPALTEN]
    assert len(df) == settings.ANZAHL_STADTTEILE
    assert df.stadtteil_id.is_unique
    assert df.stadtteil_id.map(type).eq(str).all(), "stadtteil_id muss Text sein"
    assert set(df.stadtteil_id) == set(schluessel.stadtteil_id)


@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.NAME)
def test_modul_keine_kodierungsfehler(modul, ergebnisse):
    text = ergebnisse[modul.NAME].astype(str)
    assert not text.apply(lambda s: s.str.contains("Ã", regex=False)).any().any()


@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.NAME)
def test_interim_datei_lesbar(modul, ergebnisse):
    pfad = settings.INTERIM / f"{modul.NAME}.csv"
    gelesen = pd.read_csv(pfad, dtype={"stadtteil_id": str}, encoding="utf-8")
    assert list(gelesen.stadtteil_id) == list(ergebnisse[modul.NAME].stadtteil_id)


def test_spaltennamen_projektweit_eindeutig(schluessel):
    alle = list(schluessel.columns) + [s for m in MODULE for s in m.SPALTEN]
    doppelt = {s for s in alle if alle.count(s) > 1}
    assert not doppelt, f"Doppelte Spaltennamen: {doppelt}"
