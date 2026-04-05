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

def batch_rename(folder: str, dry_run: bool = True) -> None:
    root = Path(folder)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        new_name = normalize_filename(path.name)
        new_path = path.with_name(new_name)

        if path == new_path:
            continue

        print(f"{path.name} -> {new_name}")
        if not dry_run:
            if new_path.exists():
                print(f"  SKIP: target exists: {new_name}")
                continue
            path.rename(new_path)

if __name__ == "__main__":
    folder = sys.argv[1]
    dry_run = "--apply" not in sys.argv
    batch_rename(folder, dry_run=dry_run)