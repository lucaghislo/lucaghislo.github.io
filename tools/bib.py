"""Minimal BibTeX reader shared by add_paper.py and check_bib.py (stdlib only)."""

import re


def _braced(s, i):
    # s[i] == '{' ; return (content, index after closing brace)
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
        j += 1
    raise ValueError("unbalanced braces")


def parse(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{", text):
        etype = m.group(1).lower()
        body, end = _braced(text, m.end() - 1)
        if etype in ("string", "comment", "preamble"):
            continue
        key, _, rest = body.partition(",")
        fields, i = {}, 0
        while True:
            f = re.compile(r"\s*([\w-]+)\s*=\s*").match(rest, i)
            if not f:
                break
            name, i = f.group(1).lower(), f.end()
            if rest[i] == "{":
                val, i = _braced(rest, i)
            elif rest[i] == '"':
                j = rest.index('"', i + 1)
                val, i = rest[i + 1 : j], j + 1
            else:
                v = re.compile(r"[^,}\s]+").match(rest, i)
                val, i = v.group(0), v.end()
            fields[name] = " ".join(val.split())
            c = re.compile(r"\s*,?").match(rest, i)
            i = c.end()
        entries.append({"type": etype, "key": key.strip(), "fields": fields, "start": m.start()})
    return entries
