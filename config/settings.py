"""Zentrale Einstellungen für alle Module.

Werte werden hier geändert, nicht in den einzelnen Modulen.
Pfade immer über diese Konstanten bauen, nie absolut (C:\\Users\\... oder /Users/...).
"""
from pathlib import Path

# --- Pfade -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"              # unveränderte Downloads (nicht in Git)
INTERIM = DATA / "interim"      # Ergebnis je Modul (nicht in Git)
PROCESSED = DATA / "processed"  # Endergebnis (in Git)
DOCS = ROOT / "docs"

STADTTEILE = CONFIG / "stadtteile.csv"   # Master-Schlüssel
ANZAHL_STADTTEILE = 86

# --- Koordinatensysteme --------------------------------------------------------
CRS = "EPSG:25832"         # Meter-basiert – für alle Flächen und Distanzen
CRS_WGS84 = "EPSG:4326"    # Längen-/Breitengrad – so kommen OSM- und GTFS-Daten

# --- Web-Anfragen (wird von scrapers/base.py genutzt) --------------------------
PAUSE_SEKUNDEN = 2.0       # Pause zwischen zwei Anfragen an dieselbe Website
TIMEOUT_SEKUNDEN = 30
MAX_VERSUCHE = 3           # Wiederholungen bei Fehlern, mit wachsender Wartezeit
USER_AGENT = "TH-Koeln-Studienprojekt-Mietpreise/0.1 (nicht-kommerziell, Lehrveranstaltung DIS 3.3)"
