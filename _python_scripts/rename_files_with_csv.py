import csv
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GREEK_MAP = {
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'i', 'θ': 'th',
    'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
    'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
    'Α': 'a', 'Β': 'b', 'Γ': 'g', 'Δ': 'd', 'Ε': 'e', 'Ζ': 'z', 'Η': 'i', 'Θ': 'th',
    'Ι': 'i', 'Κ': 'k', 'Λ': 'l', 'Μ': 'm', 'Ν': 'n', 'Ξ': 'x', 'Ο': 'o', 'Π': 'p',
    'Ρ': 'r', 'Σ': 's', 'Τ': 't', 'Υ': 'y', 'Φ': 'f', 'Χ': 'ch', 'Ψ': 'ps', 'Ω': 'o',
}


def transliterate(text: str) -> str:
    # First remove accents / tonos / diaeresis
    text = unicodedata.normalize("NFKD", text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))

    # Then transliterate Greek characters
    text = ''.join(GREEK_MAP.get(ch, ch) for ch in text)
    return text

def trim(s: str) -> str:
    return s.strip()


def remove_quotes(s: str) -> str:
    return re.sub(r"""["'`’“”]""", "", s)


def punctuation_to_space(s: str) -> str:
    return re.sub(r"[&:/\\(),.\[\]{}+=;!?#@]+", " ", s)


def collapse_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def replace_space_with_separator(s: str, separator: str = "-") -> str:
    return s.replace(" ", separator)


def strip_disallowed(s: str, separator: str = "-") -> str:
    allowed = rf"[^a-zA-Z0-9{re.escape(separator)}]"
    return re.sub(allowed, "", s)


def collapse_separators(s: str, separator: str = "-") -> str:
    return re.sub(rf"{re.escape(separator)}+", separator, s)


def lowercase(s: str) -> str:
    return s.lower()


def normalize_stem(stem: str, separator: str = "-") -> str:
    s = stem
    s = trim(s)
    s = transliterate(s)
    s = remove_quotes(s)
    s = punctuation_to_space(s)
    s = collapse_space(s)
    s = replace_space_with_separator(s, separator=separator)
    s = strip_disallowed(s, separator=separator)
    s = collapse_separators(s, separator=separator)
    s = lowercase(s)
    s = s.strip(separator)
    return s


def normalize_filename(name: str, separator: str = "-") -> str:
    path = Path(name)
    stem = normalize_stem(path.stem, separator=separator)
    ext = path.suffix.lower()
    return f"{stem}{ext}"


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def relative_str(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def batch_rename(folder: str, mapping_csv: str, apply: bool = False, separator: str = "-") -> None:
    root = Path(folder).resolve()
    mapping_path = Path(mapping_csv).resolve()

    rows = []
    rename_count = 0
    skip_count = 0
    unchanged_count = 0

    for path in iter_files(root):
        old_name = path.name
        new_name = normalize_filename(old_name, separator=separator)
        new_path = path.with_name(new_name)

        old_rel = relative_str(path, root)
        new_rel = relative_str(new_path, root)

        if old_name == new_name:
            status = "unchanged"
            unchanged_count += 1
        elif new_path.exists():
            status = "target-exists-skip"
            skip_count += 1
        else:
            status = "would-rename" if not apply else "renamed"
            rename_count += 1
            if apply:
                path.rename(new_path)

        rows.append({
            "old_path": old_rel,
            "new_path": new_rel,
            "old_name": old_name,
            "new_name": new_name,
            "status": status,
        })

        print(f"{old_rel} -> {new_rel} [{status}]")

    with mapping_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["old_path", "new_path", "old_name", "new_name", "status"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"CSV written to: {mapping_path}")
    print(f"Renamed:   {rename_count}")
    print(f"Skipped:   {skip_count}")
    print(f"Unchanged: {unchanged_count}")
    print(f"Mode:      {'APPLY' if apply else 'DRY RUN'}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print('  python rename_files_with_csv.py "F:\\path\\to\\folder" "F:\\path\\to\\mapping.csv"')
        print('  python rename_files_with_csv.py "F:\\path\\to\\folder" "F:\\path\\to\\mapping.csv" --apply')
        sys.exit(1)

    folder_arg = sys.argv[1]
    csv_arg = sys.argv[2]
    apply_flag = "--apply" in sys.argv
    batch_rename(folder_arg, csv_arg, apply=apply_flag)
