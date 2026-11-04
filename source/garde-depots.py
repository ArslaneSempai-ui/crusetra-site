#!/usr/bin/env python3
"""THE PRIVATE-REPOSITORY GUARD (4 November 2026).

crusetra-screening and crusetra-routing have been private since 29 October 2026 (Arslane's choice), so anonymous
GitHub answers 404. Six days later the served site still sent visitors there: « git clone » commands on two
instrument pages, « Run it on your records » and « View the public repository » links, the footer's « Repository »
link, the structured data's downloadUrl and its free-evaluation offer. A bank's risk officer who was told to try the
tool landed on a 404.

The guard refuses, in every served page and in the two text files that carry contacts (security.txt, releve.json),
any address of a repository that outil.py declares private (DEPOTS_PRIVES), any « git clone » or « cd <repo> » naming
it, and any structured-data block that does not parse or that downloads from it. The list of private repositories is
not typed here: it is read from outil.py, the one place that knows which tools are private.

With --live, it also asks GitHub, anonymously, that every repository the site still links to answers 200, and that
every private one answers 404 (a repository made public again would then be a declared private one wrongly hidden).

WAITING FOR A DECISION (EN_ATTENTE): a page that keeps a route to a private repository on purpose is listed here with
its reason, printed at every run, never silently. engagement.html's « Download and run » evaluation link was the one
entry until 5 November 2026, when Arslane made it a write-to-us button; the list is empty since.

Its own witness runs first: a planted page must be refused, a clean one must pass, or it exits 2. The assembler adds
the outer witness (a planted page in docs/ must turn it red).

  python3 garde-depots.py --docs ../docs [--live]      exit 0 clean, 1 refused, 2 broken guard
"""
import html
import json
import pathlib
import re
import sys
import tempfile
import urllib.request

ICI = pathlib.Path(__file__).parent
sys.path.insert(0, str(ICI))
from outil import DEPOTS, DEPOTS_PRIVES, GITHUB  # noqa: E402

PRIVES = {GITHUB + DEPOTS[k] for k in DEPOTS_PRIVES}
PUBLICS = {GITHUB + v for k, v in DEPOTS.items() if k not in DEPOTS_PRIVES}
NOMS_PRIVES = {DEPOTS[k] for k in DEPOTS_PRIVES}
# the pages that keep a route to a private repository on purpose, each with the reason and who decides
EN_ATTENTE: dict[str, str] = {}
TEXTES = (".well-known/security.txt", "releve.json")


def fautes_du_texte(texte):
    """The lines of one served text that lead to a private repository: (line number, what)."""
    fautes = []
    for i, ligne in enumerate(texte.splitlines(), 1):
        brut = html.unescape(ligne)
        for url in PRIVES:
            if url in brut:
                fautes.append((i, f"address of a private repository: {url}"))
                break
        else:
            for nom in NOMS_PRIVES:
                if re.search(r"\bgit clone\b[^<\n]*" + re.escape(nom) + r"\b", brut) or re.search(r"\bcd " + re.escape(nom) + r"\b", brut):
                    fautes.append((i, f"a command that needs the private repository {nom}"))
                    break
    return fautes


def fautes_des_donnees(texte):
    """Every <script type="application/ld+json"> of a page must parse, and download from no private repository."""
    fautes = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', texte, re.S):
        ligne = texte[:m.start()].count("\n") + 1
        try:
            d = json.loads(m.group(1))
        except ValueError as e:
            fautes.append((ligne, f"structured data does not parse: {e}"))
            continue
        for noeud in d.get("@graph", [d]):
            dl = noeud.get("downloadUrl")
            if dl and dl.rstrip("/") in PRIVES:
                fautes.append((ligne, f"structured data downloads from a private repository: {dl}"))
    return fautes


def relever(docs):
    """[(page, line, what)] over every served page and text; EN_ATTENTE pages are reported apart."""
    fautes, attendues = [], []
    pages = sorted(p for p in docs.rglob("*.html")) + [docs / t for t in TEXTES if (docs / t).exists()]
    for p in pages:
        rel = p.relative_to(docs).as_posix()
        texte = p.read_text(encoding="utf-8", errors="replace")
        trouvees = fautes_du_texte(texte) + (fautes_des_donnees(texte) if p.suffix == ".html" else [])
        for ligne, quoi in trouvees:
            (attendues if rel in EN_ATTENTE else fautes).append((rel, ligne, quoi))
    return fautes, attendues


def temoin():
    """A planted page must be refused on each of the three patterns; a clean page with a public link must pass."""
    with tempfile.TemporaryDirectory() as d:
        docs = pathlib.Path(d)
        prive = next(iter(PRIVES))
        nom = prive.rsplit("/", 1)[1]
        public = next(iter(PUBLICS))
        (docs / "a.html").write_text(f'<a href="{prive}">Run it</a>')
        (docs / "b.html").write_text(f'<code>$ git clone {prive}.git</code><code>$ cd {nom}</code>')
        (docs / "c.html").write_text('<script type="application/ld+json">{"@graph": [{"downloadUrl": "' + prive + '"}]}</script>')
        (docs / "d.html").write_text('<script type="application/ld+json">{not json</script>')
        (docs / "e.html").write_text(f'<a href="{public}">View the public repository</a><code>$ npm ci --ignore-scripts</code>')
        fautes, _ = relever(docs)
        pages = {f[0] for f in fautes}
        if pages != {"a.html", "b.html", "c.html", "d.html"}:
            return f"the witness expected a, b, c and d refused and e clean; got {sorted(pages)}"
        if sum(1 for f in fautes if f[0] == "b.html") != 1:
            return "the witness expected one refusal on the clone line of b.html"
    return None


def en_ligne():
    """GitHub, anonymously: every public repository answers 200, every private one 404."""
    fautes = []
    for url, attendu in [(u, 200) for u in sorted(PUBLICS)] + [(u, 404) for u in sorted(PRIVES)]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "crusetra-site garde-depots"}, method="HEAD")
            with urllib.request.urlopen(req, timeout=15) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:  # noqa: BLE001
            fautes.append(f"{url}: no answer ({e})")
            continue
        if code != attendu:
            fautes.append(f"{url}: answers {code}, expected {attendu} ({'private' if attendu == 404 else 'public'} in outil.py)")
    return fautes


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
    if "--live" in args:
        for f in en_ligne():
            print(f"  en ligne : {f}")
            fautes.append(("github", 0, f))
    n = len(list(docs.rglob("*.html")))
    if fautes:
        print(f"dépôts : {len(fautes)} refus sur {n} pages servies ({', '.join(sorted(NOMS_PRIVES))} private)")
        return 1
    print(f"dépôts tenus : 0 refus sur {n} pages servies ({', '.join(sorted(NOMS_PRIVES))} private, "
          f"{len(attendues)} route(s) waiting for a decision)")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
