"""Add a publication to _bibliography/papers.bib from its DOI.

python tools/add_paper.py 10.1109/TNS.2026.3700799
python tools/add_paper.py 10.1109/TNS.2026.3700799 --preview first_page.pdf --selected
python tools/add_paper.py 10.1109/TNS.2026.3700799 --dry-run

--preview accepts an image (png/jpg) or a PDF (first page, needs PyMuPDF: pip install pymupdf).
The preview is resized and saved as assets/img/publication_preview/<key>.png|jpg.
--bibtex-file uses a local BibTeX file instead of downloading from doi.org.
"""

import argparse
import datetime
import os
import re
import sys
import unicodedata
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from bib import parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "_bibliography", "papers.bib")
PREV = os.path.join(ROOT, "assets", "img", "publication_preview")

ORDER = ["title", "author", "journal", "booktitle", "series", "editor", "volume", "number", "pages",
         "year", "month", "publisher", "school", "issn", "isbn", "doi", "urldate", "preview",
         "selected", "bibtex_show", "html", "pdf", "arxiv", "langid"]
DROP = {"url"}
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()

ap = argparse.ArgumentParser()
ap.add_argument("doi")
ap.add_argument("--preview")
ap.add_argument("--selected", action="store_true")
ap.add_argument("--key")
ap.add_argument("--bibtex-file")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", a.doi.strip())
text = open(BIB, encoding="utf-8").read()
if any(e["fields"].get("doi", "").lower() == doi.lower() for e in parse(text)):
    sys.exit(f"DOI {doi} is already in papers.bib")

if a.bibtex_file:
    raw = open(a.bibtex_file, encoding="utf-8").read()
else:
    req = urllib.request.Request(f"https://doi.org/{doi}", headers={"Accept": "application/x-bibtex; charset=utf-8"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
e = parse(raw)[0]
f = {k: v for k, v in e["fields"].items() if k not in DROP}
f["doi"] = doi

# normalize
f["pages"] = re.sub(r"\s*[–—-]+\s*", "--", f["pages"]) if "pages" in f else None
f["title"] = re.sub(r"^\{(.*)\}$", r"\1", f["title"])
if f.get("month", "").lower()[:3] in MONTHS:
    f["month"] = f["month"].lower()[:3]
f = {k: v for k, v in f.items() if v}
f["urldate"] = datetime.date.today().isoformat()
f["html"] = f"https://doi.org/{doi}"
f["bibtex_show"] = "true"
f["selected"] = "true" if a.selected else "false"
f.setdefault("langid", "english")


def ascii_word(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


first = re.split(r",| and ", f["author"])[0].strip(" {}")
word = next((w for w in re.findall(r"[A-Za-z0-9]+", ascii_word(f["title"]))
             if w not in {"a", "an", "the", "on", "of", "for", "and", "in", "with", "to"}), "paper")
key = a.key or f"{ascii_word(first).split()[-1]}_{word}_{f.get('year', 'nd')}"
existing = {x["key"] for x in parse(text)}
base, n = key, 1
while key in existing:
    n += 1
    key = f"{base}{chr(96 + n)}"

if a.preview:
    from PIL import Image

    src = a.preview
    if src.lower().endswith(".pdf"):
        import pymupdf as fitz

        page = fitz.open(src)[0]
        pix = page.get_pixmap(dpi=110)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ext = ".png"
    else:
        img = Image.open(src)
        ext = ".jpg" if src.lower().endswith((".jpg", ".jpeg")) else ".png"
    img.thumbnail((800, 800), Image.LANCZOS)
    name = key + ext
    if not a.dry_run:
        img.convert("RGB").save(os.path.join(PREV, name), optimize=True, **({"quality": 85} if ext == ".jpg" else {}))
    f["preview"] = name

w = max(len(k) for k in f) + 1
lines = []
for k in sorted(f, key=lambda k: (ORDER.index(k) if k in ORDER else len(ORDER), k)):
    v = f[k] if k == "month" and f[k] in MONTHS else "{" + f[k] + "}"
    lines.append(f"  {k.ljust(w)}= {v},")
entry = f"@{e['type']}{{{key},\n" + "\n".join(lines) + "\n}\n"

print(entry)
if a.dry_run:
    sys.exit(0)
with open(BIB, "a", encoding="utf-8") as fh:
    fh.write(("\n" if not text.endswith("\n\n") else "") + entry)
print(f"added {key} to papers.bib" + (f", preview {f['preview']}" if "preview" in f else " (no preview: add one with --preview)"))
