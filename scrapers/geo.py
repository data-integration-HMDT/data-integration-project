import re, unicodedata

ERSETZUNG = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

def normalisiere_name(name: str) -> str:
    s = unicodedata.normalize("NFC", str(name)).strip().lower().translate(ERSETZUNG)
    s = re.sub(r"^koeln[\s\-–]+", "", s)     # "Köln-Sülz" → "suelz"
    s = re.sub(r"[/\-–]", " ", s)            # "Altstadt/Süd" → "altstadt sued"
    return re.sub(r"\s+", " ", s).strip()