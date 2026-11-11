#!/usr/bin/env python3
"""THE BRACKETED-PLACEHOLDER GUARD (11 November 2026).

On 20 October 2026 an editing pass took a person's name out of the OFAC 14 July article and left « [name removed] »
in the body of the live page (commit 89c50a6 fixed it on a branch that never reached main), while the meta
description and the og description still named the network after that person. A visitor read a redaction mark.

The guard refuses, in every served page and text, a bracketed placeholder: [name removed], [redacted], [removed],
[REDACTED], [TODO], [TBD], [placeholder], [insert ...], [xxx]. It reads the whole file (visible text, meta, og,
structured data, scripts), because a placeholder in an attribute is as public as one in a paragraph.

WAITING FOR A DECISION (EN_ATTENTE): screening/try.html packs the tool's matcher as it is; the tool's Burmese
syllable list holds a token that is literally « [name removed] » (src/birman.ts in the tool, since 28 September
2026). It is data the visitor never sees; the fix is in the tool, then the page is repacked. It is listed here, printed
at every run, never silently.

Its own witness runs first: a planted page must be refused, a clean one must pass, or it exits 2. The assembler adds
the outer witness (a planted page in docs/ must turn it red).

  python3 garde-crochets.py --docs ../docs      exit 0 clean, 1 refused, 2 broken guard
"""
import html
import pathlib
import re
import sys
import tempfile

ICI = pathlib.Path(__file__).parent
# a bracketed word that marks missing content; ordinary brackets ([1], [sic], array literals) are not touched
MOTIF = re.compile(
    r"\[\s*(?:(?:[a-z ]{0,30}\b(?:removed|redacted|withheld|omitted)\b[a-z ]{0,30})"
    r"|todo|tbd|placeholder|lorem[a-z ]{0,20}|insert\b[^\]\n]{0,60}|x{3,})\s*\]",
    re.I)
TEXTES = (".well-known/security.txt", "releve.json")
# pages that carry one on purpose (never visible), with the reason and where the fix lives
EN_ATTENTE = {
    "screening/try.html": "the packed matcher holds the token from the tool's src/birman.ts; fix it there, then repack",
}


def fautes_du_texte(texte):
    """(line, what) for each bracketed placeholder in one served text."""
    fautes = []
    for i, ligne in enumerate(texte.splitlines(), 1):
        for m in MOTIF.finditer(html.unescape(ligne)):
            fautes.append((i, f"bracketed placeholder {m.group(0)!r}"))
    return fautes


def relever(docs):
    """[(page, line, what)] over every served page and text; EN_ATTENTE pages are reported apart."""
    fautes, attendues = [], []
    pages = sorted(docs.rglob("*.html")) + [docs / t for t in TEXTES if (docs / t).exists()]
    for p in pages:
        rel = p.relative_to(docs).as_posix()
        texte = p.read_text(encoding="utf-8", errors="replace")
        for ligne, quoi in fautes_du_texte(texte):
            (attendues if rel in EN_ATTENTE else fautes).append((rel, ligne, quoi))
    return fautes, attendues


def temoin():
    """Planted placeholders (body, meta, og, text file) must be refused; ordinary brackets must pass."""
    with tempfile.TemporaryDirectory() as d:
        docs = pathlib.Path(d)
        (docs / "a.html").write_text("<p>ties them to the network of [name removed], which</p>")
        (docs / "b.html").write_text('<meta property="og:description" content="by [REDACTED] and [TODO]">')
        (docs / "c.html").write_text("<p>see [1] and [sic]; <code>const a = [0, 1]</code> and a list [A, B]</p>")
        (docs / "releve.json").write_text('{"note": "[placeholder]"}')
        fautes, _ = relever(docs)
        pages = {f[0] for f in fautes}
        if pages != {"a.html", "b.html", "releve.json"}:
            return f"the witness expected a, b and releve.json refused and c clean; got {sorted(pages)}"
        if sum(1 for f in fautes if f[0] == "b.html") != 2:
            return "the witness expected two refusals on b.html"
    return None


def principal():
    args = sys.argv[1:]
    docs = ICI.parent / "docs"
    if "--docs" in args:
        docs = pathlib.Path(args[args.index("--docs") + 1])
    casse = temoin()
    if casse:
        print(f"GARDE CASSÉE : {casse}")
        return 2
    fautes, attendues = relever(docs)
    for rel, ligne, quoi in attendues:
        print(f"  en attente {rel}:{ligne}: {quoi} ({EN_ATTENTE[rel]})")
    for rel, ligne, quoi in fautes:
        print(f"  {rel}:{ligne}: {quoi}")
    n = len(list(docs.rglob("*.html")))
    if fautes:
        print(f"crochets : {len(fautes)} refus sur {n} pages servies")
        return 1
    print(f"crochets tenus : 0 refus sur {n} pages servies ({len(attendues)} en attente d'une décision)")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
