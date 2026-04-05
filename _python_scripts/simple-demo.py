# -*- coding: utf-8 -*-
import re
import unicodedata
from pathlib import Path

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def transliterate(text: str) -> str:
    GREEK_MAP = {
        'α':'a','β':'b','γ':'g','δ':'d','ε':'e','ζ':'z','η':'i','θ':'th',
        'ι':'i','κ':'k','λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p',
        'ρ':'r','σ':'s','ς':'s','τ':'t','υ':'y','φ':'f','χ':'ch','ψ':'ps','ω':'o',
        'Α':'a','Β':'b','Γ':'g','Δ':'d','Ε':'e','Ζ':'z','Η':'i','Θ':'th',
        'Ι':'i','Κ':'k','Λ':'l','Μ':'m','Ν':'n','Ξ':'x','Ο':'o','Π':'p',
        'Ρ':'r','Σ':'s','Τ':'t','Υ':'y','Φ':'f','Χ':'ch','Ψ':'ps','Ω':'o',
    }
    # First remove accents / tonos / diaeresis
    text = unicodedata.normalize("NFKD", text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))

    # Then transliterate Greek characters
    text = ''.join(GREEK_MAP.get(ch, ch) for ch in text)
    return text

def normalize_filename(name: str, separator: str = "-") -> str:
    p = Path(name)
    stem = p.stem
    ext = p.suffix.lower()

    stem = stem.strip()
    stem = transliterate(stem)

    # Replace apostrophes and quotes with nothing
    stem = re.sub(r"[\"'`’“”]", "", stem)

    # Replace separators/punctuation with spaces
    stem = re.sub(r"[&:/\\(),.\[\]{}]+", " ", stem)

    # Collapse whitespace
    stem = re.sub(r"\s+", " ", stem).strip()

    # Replace spaces with chosen separator
    stem = stem.replace(" ", separator)

    # Remove anything not alnum, separator
    allowed = rf"[^a-zA-Z0-9{re.escape(separator)}]"
    stem = re.sub(allowed, "", stem)

    # Collapse repeated separators
    stem = re.sub(rf"{re.escape(separator)}+", separator, stem)

    # Lowercase
    stem = stem.lower().strip(separator)

    return f"{stem}{ext}"

if __name__ == "__main__":
    samples = [
        "Schubert Trout 4th movement.mp3",
        "Beethoven: Sym. 6, Op.68 (Pastoral) - II.mp3",
        " Χατζιδάκις   - Όρνιθες - 05 Πάροδος.mp3 ",
        "Dvořák_ Humoresque in Gb, Op 101 7.mp3",
        "Granados_ Danzas Españolas, Op 37 - 1 Allegro, Andante.mp3",
    ]
    for s in samples:
        print(s, "->", normalize_filename(s))
