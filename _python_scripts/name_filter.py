# -*- coding: utf-8 -*-
import sys
import re
import unicodedata
from pathlib import Path

try:
    sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    sys.stderr.reconfigure(encoding="utf-8", errors="strict")
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
    text = unicodedata.normalize("NFKD", text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = ''.join(GREEK_MAP.get(ch, ch) for ch in text)
    return text


def normalize_name(text: str, separator: str = "-") -> str:
    text = text.strip()
    text = transliterate(text)
    text = re.sub(r"""["'`’“”]""", "", text)
    text = re.sub(r"[&:/\\(),.\[\]{}+=;!?#@]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ", separator)
    text = re.sub(rf"[^a-zA-Z0-9{re.escape(separator)}]", "", text)
    text = re.sub(rf"{re.escape(separator)}+", separator, text)
    text = text.lower().strip(separator)
    return text


def normalize_filename(text: str, separator: str = "-") -> str:
    p = Path(text.strip())
    stem = normalize_name(p.stem, separator=separator)
    ext = p.suffix.lower()
    return f"{stem}{ext}" if ext else stem


def emit_mapping(lines, separator="|", mode="filename"):
    for raw in lines:
        #print(f"DEBUG raw={raw!r}", file=sys.stderr)
        original = raw.rstrip("\n")
        if not original.strip():
            continue
        converted = (
            normalize_filename(original)
            if mode == "filename"
            else normalize_name(original)
        )
        #print(f"DEBUG converted={converted!r}", file=sys.stderr)
        print(f"{original}{separator}{converted}")

def input_lines(paths):
    if not paths and sys.stdin.isatty():
        print("No input provided. Pipe data or pass files.", file=sys.stderr)
        sys.exit(1)
    if not paths:
        #print("Reading from stdin...", file=sys.stderr)
        for line in sys.stdin:
            yield line
    else:
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    yield line

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    args = sys.argv[1:]
    mode = "filename"
    sep = "|"
    files = []

    i = 0
    while i < len(args):
        if args[i] == "--plain":
            mode = "plain"
        elif args[i] == "--filename":
            mode = "filename"
        elif args[i] == "--sep":
            i += 1
            if i >= len(args):
                raise SystemExit("Missing value after --sep")
            sep = args[i]
        else:
            files.append(args[i])
        i += 1

    emit_mapping(input_lines(files), separator=sep, mode=mode)