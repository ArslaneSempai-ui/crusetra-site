#!/usr/bin/env python3
"""LA GARDE DE L'ORTHOGRAPHE AMÉRICAINE (30/09, Arslane : « c'est plus américain » ; décision : tout le site).

Refuse, dans ce que le lecteur voit (le corps des pages, les attributs alt / aria-label / title / content,
les chaînes des scripts de page), toute orthographe britannique des mots listés ci-dessous. Nos acheteurs
sont américains : license, organization, color, behavior, labeled, optimizer...

Quatre exceptions, chacune pour une raison écrite :
  1. le code, les commandes et les chemins (<code>, <pre>, lignes de terminal .tm-l, « src/optimise.ts ») :
     ce sont des NOMS, la commande de l'outil s'appelle optimise ;
  2. les données citées d'un outil (<script type="application/json" id="donnees">), qui portent le scellé
     de leur relevé : les changer ici mentirait sur l'outil ;
  3. le facteur « behaviour » de Scoring, nom scellé dans ses relevés, reconnu à son voisinage (un autre
     facteur de Scoring à moins de 60 caractères, ou « behaviour: » / « behaviour at 0. »). En prose
     (« keyboard behaviour »), il est refusé ;
  4. le code de l'outil Screening embarqué dans la page d'essai (<script id="moteur">, screening/try.html, 4 novembre
     2026) : ses messages et ses noms de commande (« optimise », « licence ») sont les siens, portés tels quels.

LE TÉMOIN TOURNE D'ABORD : une page fautive doit déclencher chaque mot de la liste, une page saine aucun,
et les quatre exceptions doivent passer. Un mot muet = garde cassée (code 2).
usage: python3 garde-orthographe.py --docs DIR
"""
import html, pathlib, re, sys

MOTS = {  # britannique -> américain (le message dit quoi écrire)
    "licence": "license", "licences": "licenses", "licenced": "licensed", "organisation": "organization",
    "organisations": "organizations", "organise": "organize", "organised": "organized", "colour": "color",
    "colours": "colors", "coloured": "colored", "behaviour": "behavior", "behaviours": "behaviors",
    "behavioural": "behavioral", "neighbour": "neighbor", "neighbours": "neighbors", "neighbourhood": "neighborhood",
    "favour": "favor", "favours": "favors", "favouring": "favoring", "favourite": "favorite", "labelled": "labeled",
    "labelling": "labeling", "modelled": "modeled", "modelling": "modeling", "travelled": "traveled",
    "cancelled": "canceled", "optimiser": "optimizer", "optimise": "optimize", "optimised": "optimized",
    "optimising": "optimizing", "recognise": "recognize", "recognised": "recognized", "analyse": "analyze",
    "analysed": "analyzed", "summarise": "summarize", "summarised": "summarized", "programme": "program",
    "programmes": "programs", "centre": "center", "catalogue": "catalog", "defence": "defense",
    "judgement": "judgment", "grey": "gray", "cheque": "check", "artefact": "artifact", "artefacts": "artifacts",
}
MOT = re.compile(r"(?<![/\w.-])(" + "|".join(sorted(MOTS, key=len, reverse=True)) + r")(?!\w|\.[a-z])", re.I)
FACTEURS = re.compile(r"\b(activity|exposure|geography|product|structure|tenure)\b", re.I)


def segments(page):
    """(sorte, texte) de tout ce que le lecteur voit ; code, chemins de terminal et données d'outil exclus."""
    s = re.sub(r"<!--.*?-->", " ", page, flags=re.S)
    out = []
    for attrs, corps in re.findall(r"<script([^>]*)>(.*?)</script>", s, flags=re.S):
        if "application/json" in attrs or "ld+json" in attrs:
            continue                          # exception 2 (données d'outil) ; le JSON-LD a sa propre garde
        if 'id="moteur"' in attrs:
            continue                          # exception 4 (le code de l'outil, porté tel quel)
        for a, b, c in re.findall(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`([^`]*)`", corps):
            out.append(("script", a or b or c))
    corps = re.sub(r"<script.*?</script>|<style.*?</style>|<code[^>]*>.*?</code>|<pre[^>]*>.*?</pre>"
                   r"|<p class=\"tm-l\">.*?</p>", " ", s, flags=re.S)      # exception 1
    for v in re.findall(r'\s(?:alt|aria-label|title|content)="([^"]*)"', corps):
        out.append(("attribut", html.unescape(v)))
    out.append(("texte", re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps)))))
    return out


def refus(page):
    r = []
    for sorte, t in segments(page):
        for m in MOT.finditer(t):
            mot = m.group(1)
            if mot.lower() == "behaviour":
                fen = t[max(0, m.start() - 60): m.end() + 60]
                apres = t[m.end(): m.end() + 6]
                if FACTEURS.search(fen) or apres.startswith(":") or apres.startswith(" at 0."):
                    continue                  # exception 3 : le facteur de Scoring
            r.append((mot, MOTS[mot.lower()], sorte, t[max(0, m.start() - 50): m.end() + 40]))
    return r


def temoin():
    fautive = "<p>" + " ".join(MOTS) + "</p><p>The keyboard behaviour.</p>"
    vus = {m.lower() for m, *_ in refus(fautive)}
    muets = set(MOTS) - vus
    if muets:
        sys.exit(f"GARDE CASSÉE : la page fautive du témoin ne déclenche pas {sorted(muets)} (code 2)")
    saine = ('<p>The license, the organization, the color, the behavior.</p><code>npm run optimise</code>'
             '<p class="tm-l">$ crusetra optimise --recall</p><p>Where it lives src/optimise.ts:379 · LICENCES.md</p>'
             '<p>activity behaviour exposure</p><p>behaviour: 51.6%</p>'
             '<script type="application/json" id="donnees">{"d": "string similarity favouring the prefix"}</script>'
             '<script id="moteur">const aide = "npm run optimise -- --recall; no licence recorded";</script>')
    if refus(saine):
        sys.exit(f"GARDE CASSÉE : la page saine du témoin est refusée : {refus(saine)} (code 2)")


def main():
    args = sys.argv[1:]
    docs = pathlib.Path(args[args.index("--docs") + 1]) if "--docs" in args else pathlib.Path(__file__).parent.parent / "docs"
    temoin()
    pages = sorted(p for p in docs.rglob("*.html"))
    tous = [(p.relative_to(docs), *x) for p in pages for x in refus(p.read_text(encoding="utf-8"))]
    if tous:
        for p, mot, us, sorte, ctx in tous:
            print(f"  {p} · {sorte} · « {mot} » → {us} · …{ctx}…")
        print(f"orthographe : {len(tous)} refus sur {len(pages)} pages")
        sys.exit(1)
    print(f"  orthographe américaine tenue : 0 refus sur {len(pages)} pages (le témoin a prouvé que les {len(MOTS)} mots mordent)")


if __name__ == "__main__":
    main()
