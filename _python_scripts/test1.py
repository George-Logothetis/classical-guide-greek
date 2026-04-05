# -*- coding: utf-8 -*-
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def input_lines(paths):
    if not paths:
        for line in sys.stdin:
            yield line
    else:
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    yield line

if __name__ == "__main__":
    args = sys.argv[1:]
    files = []

    for a in args:
        files.append(a)

    for raw in input_lines(files):
        original = raw.rstrip("\n")
        if not original.strip():
            continue
        print(f"{original}|{original.lower()}")