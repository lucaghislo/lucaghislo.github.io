"""Sanity checks on _bibliography/papers.bib. Exit code 1 on errors.

python tools/check_bib.py
"""

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from bib import parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "_bibliography", "papers.bib")
PREV = os.path.join(ROOT, "assets", "img", "publication_preview")

entries = parse(open(BIB, encoding="utf-8").read())
previews = set(os.listdir(PREV))
errors, warnings = [], []

for k, n in Counter(e["key"] for e in entries).items():
    if n > 1:
        errors.append(f"duplicate key: {k}")
for d, n in Counter(e["fields"]["doi"].lower() for e in entries if "doi" in e["fields"]).items():
    if n > 1:
        errors.append(f"duplicate doi: {d}")

for e in entries:
    k, f = e["key"], e["fields"]
    for req in ("title", "author", "year"):
        if req not in f:
            errors.append(f"{k}: missing {req}")
    p = f.get("preview")
    if p and p not in previews:
        errors.append(f"{k}: preview file not found: {p}")
    if not p:
        warnings.append(f"{k}: no preview")
    if not ({"doi", "html", "url"} & f.keys()):
        warnings.append(f"{k}: no doi/html link")

used = {e["fields"].get("preview") for e in entries}
for p in sorted(previews - used):
    warnings.append(f"unused preview image: {p}")

for w in warnings:
    print("warning:", w)
for x in errors:
    print("ERROR:", x)
print(f"{len(entries)} entries, {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
