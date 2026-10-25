#!/usr/bin/env python3
"""LE TÉMOIN DE L'ACCUEIL (l'éventail, le grand livre, la méthode sur papier — 11/09).

Il lit la page SERVIE (docs/index.html) et tient les affirmations du premier écran :

  A. le grand livre : six lignes libellé/valeur ; le content hash EST l'empreinte
     recomposée du relevé scellé du routage (jamais crue sur parole) ; chaque chiffre
     du livre se retrouve sur la page du héros routing (même source, même chaîne de
     gardes : un chiffre tapé à la main sur l'accueil divergerait du héros au premier
     re-scellement) ; la ligne de commande porte premiere-reponse et le git clone ;
  B. l'éventail : cinq cartes vivantes, une par outil, dans l'ordre du rideau
     (OUTILS d'outil.py, jamais une liste retapée), chacune portant son SVG ;
  C. la méthode : quatre stations numérotées, la station 03 porte le terminal aux
     QUATRE commandes (le cd depuis le 6/10), la station 02 explique le scellé par son content hash ;
  D. la scène : l'escalier-01 avec DEUX annotations dont les textes sont ceux
     PUBLIÉS de findings-dossier.json (fiche 01), et la note est la phrase de la
     fiche — l'accueil cite le dossier, il ne le paraphrase pas ;
  E. la méthode ne porte plus sa rangée de liens (le pied la porte, Arslane 13/09) ;
  F. le premier écran : UN lede sous le titre (rouvert le 13/09 : la relecture du 8/09 le
     propose, Arslane le reprend), sans cadratin ; ni hero-cue, ni robot avant le rideau.

LE TÉMOIN SE PROUVE PAR MUTATION à chaque lancement : la page réelle, altérée
(sceau changé, carte retirée, annotation réécrite, chiffre déplacé), doit rougir
sur la bonne affirmation ; la page intacte doit passer. Sinon : garde cassée,
aucun relevé (code 2). Statique : aucun navigateur requis.

usage: python3 temoin-accueil.py [--docs DIR]     0 = tenu ; 1 = refus ; 2 = garde cassée
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))
import outil  # noqa: E402  (OUTILS, lire_releve_scelle : l'ordre du rideau et le sceau)


def _nu(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()


def relever(html, hero_routing, findings_dossier):
    fautes = []

    def dire(quoi):
        fautes.append(quoi)

    # A. le grand livre
    m = re.search(r'<dl class="ledger[^"]*"[^>]*>(.*?)</dl>', html, re.S)
    if not m:
        return ["le grand livre (dl.ledger) est absent du premier écran"]
    lignes = re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", m.group(1), re.S)
    if len(lignes) != 6:
        dire(f"le grand livre porte {len(lignes)} lignes, la décision en veut six")
    paires = [(_nu(dt), _nu(dd)) for dt, dd in lignes]
    sceau_vrai = outil.lire_releve_scelle(outil.OUTILS["routing"]["releve_scelle"])["empreinte"]
    dd_hash = next((dd for dt, dd in paires if "hash" in dt.lower()), None)
    if dd_hash is None:
        dire("aucune ligne « content hash » dans le grand livre")
    elif dd_hash != sceau_vrai:
        dire(f"le content hash du grand livre ({dd_hash}) n'est pas l'empreinte recomposée "
             f"du relevé scellé ({sceau_vrai})")
    for dt, dd in paires:
        if "hash" in dt.lower() or "rerun" in dt.lower():
            continue
        for nombre in re.findall(r"\d[\d,.]*", dd):
            if nombre not in hero_routing:
                dire(f"le chiffre « {nombre} » ({dt}) ne se retrouve pas sur le héros routing : "
                     "les deux pages lisent la même source, l'un des deux a dérivé")
    if "premiere-reponse" not in m.group(1):
        dire("la ligne de commande du grand livre ne porte pas premiere-reponse")
    if "git clone" not in m.group(1):
        dire("la ligne de commande du grand livre ne porte pas le git clone")

    # B. l'éventail, dans l'ordre du rideau
    cartes = re.findall(r'<a class="carte-ev[^"]*" href="([^"]+)"(.*?)</a>', html, re.S)
    attendu = [("index.html" if o["sous_dossier"] == "" else o["sous_dossier"] + "index.html")
               if o["id"] != "routing" else "routing/index.html"
               for o in outil.OUTILS.values()]
    if [h for h, _ in cartes] != attendu:
        dire(f"l'éventail sert {[h for h, _ in cartes]} ; l'ordre du rideau (OUTILS) est {attendu}")
    for h, corps in cartes:
        if "<svg" not in corps:
            dire(f"la carte {h} ne porte pas son SVG du relevé : une carte morte dans l'éventail")

    # C. les stations
    st = re.search(r'<ol class="stations"[^>]*>(.*?)</ol>', html, re.S)
    if not st:
        dire("le rail des stations (ol.stations) est absent")
    else:
        lis = re.findall(r"<li\b.*?</li>", st.group(1), re.S)
        if len(lis) != 4:
            dire(f"{len(lis)} stations, la méthode en compte quatre")
        for i, li in enumerate(lis, 1):
            if f"0{i}" not in li:
                dire(f"la station {i} ne porte pas son numéro 0{i}")
        if lis and "methode-term" not in lis[2]:
            dire("la station 03 (RERUN) ne porte pas le terminal des commandes")
        n_cmd = len(re.findall(r"<code[^>]*>", lis[2])) if len(lis) >= 3 else 0
        if n_cmd != 4:
            # trois jusqu'au 6/10 ; le cd entre le clone et npm ci (Crusetra V4, demandé par le chef) en fait quatre
            dire(f"le terminal de la station 03 porte {n_cmd} commandes, la maison en montre quatre")
        # 13/09 : « sealed public record » a quitté les ÉCRANS (décision d'Arslane) ; la
        # station 01 dit « our public test set ». Le scellé se DÉFINIT désormais à la
        # station 02 (« SEAL · Hashed, then frozen »), et c'est elle qu'on garde : l'accueil
        # doit toujours EXPLIQUER le scellé, pas seulement en porter le mot.
        if len(lis) >= 2 and "content hash" not in _nu(lis[1]):
            dire("la station 02 (SEAL) n'explique pas le scellé par son content hash")

    # D. la scène de l'escalier et ses annotations PUBLIÉES
    if not re.search(r'class="objet"[^>]*src="[^"]*escalier-01\.webp"', html):
        dire("la scène de la méthode ne montre pas escalier-01.webp")
    sc = re.search(r'class="methode-scene"(.*?)class="methode-note"', html, re.S)
    etis = re.findall(r'<span class="ap-eti"[^>]*>(.*?)</span>', sc.group(1)) if sc else []
    f01 = findings_dossier["findings"][0]
    publiees = [str(a[4]).strip() for a in f01.get("annotations", [])]
    if sorted(_nu(e) for e in etis) != sorted(publiees):
        dire(f"les annotations de la scène {sorted(_nu(e) for e in etis)} ne sont pas celles "
             f"publiées de la fiche 01 du dossier {sorted(publiees)}")
    note = re.search(r'<p class="methode-note">(.*?)</p>', html, re.S)
    if not note or _nu(note.group(1)) != _nu(f01["phrase"]):
        dire("la note de la méthode n'est pas la phrase publiée de la fiche 01 : "
             "l'accueil cite le dossier, il ne le paraphrase pas")

    # E. la rangée de liens de la méthode a disparu (Arslane, 13/09 : « c'est bizarre d'avoir
    # les mêmes boutons » ; le rang du pied porte les pages, une fois)
    if re.search(r'<nav class="methode-liens"', html):
        dire("la méthode porte encore sa rangée de liens : le pied la porte depuis le 13/09")

    # F. le premier écran : un lede, et lui seul
    avant_rideau = html.split('class="rideau"')[0]
    ledes = re.findall(r'<p class="lede[^"]*"[^>]*>(.*?)</p>', avant_rideau, re.S)
    if len(ledes) != 1:
        dire(f"le premier écran porte {len(ledes)} lede(s), la décision du 13/09 en met un sous le titre")
    elif "\u2014" in ledes[0]:
        dire("le lede porte un cadratin")
    if "hero-cue" in avant_rideau:
        dire("le hero-cue vit encore sur le premier écran")
    # the hero itself carries no robot; the lit robot of the night sky above it is Arslane's decision of 25/10 (G)
    hero_sec = avant_rideau[avant_rideau.find('<section class="hero"'):]
    if re.search(r'<img[^>]*robot-[a-z-]+\.webp', hero_sec):
        dire("un robot vit sur le héros de l'accueil : la décision n'y en met aucun")

    # G. the night sky (Arslane, 25/10, concept A "dive"): once, above the hero, on the home only; its headline is
    # title 1 word for word, all white, the three verbs lit by a glow and by no colour
    ciels = re.findall(r'<section class="cl"', html)
    if len(ciels) != 1 or html.find('<section class="cl"') > html.find("<main>"):
        dire(f"ciel : {len(ciels)} night sky section(s) above the hero, one expected")
    titre = re.search(r'<h2 class="cl-titre">(.*?)</h2>', html, re.S)
    if not titre or re.sub(r"<[^>]+>", "", titre.group(1)).strip() != "Compliance decisions you can test, reproduce and inspect.":
        dire("ciel : the headline is not title 1, « Compliance decisions you can test, reproduce and inspect. »")
    elif re.findall(r"<(\w+)", titre.group(1)) != ["b", "b", "b"] or [_nu(x) for x in re.findall(r"<b>(.*?)</b>", titre.group(1))] != ["test", "reproduce", "inspect"]:
        dire("ciel : the headline's highlights are not the three verbs test, reproduce, inspect")
    regle = re.search(r"\.cl-titre b\{([^}]*)\}", html)
    if not regle or re.search(r"vert|#57b184|#a5f7cb", regle.group(1)) or "color:#fff" not in regle.group(1) or "text-shadow" not in regle.group(1):
        dire("ciel : the three verbs are not white with a glow (pas en vert, Arslane 25/10)")
    if 'class="cl"' in hero_routing or "cl-vol" in hero_routing:
        dire("ciel : a tool page carries the night sky, only the home does")
    return fautes


def temoin(html, hero, fd):
    """La page réelle, mutée six fois : chaque mutation doit rougir sur la bonne
    affirmation, et la page intacte doit passer."""
    intacte = relever(html, hero, fd)
    if intacte:
        return intacte      # la vraie page a de vraies fautes : ce n'est pas le témoin qui casse
    sceau = outil.lire_releve_scelle(outil.OUTILS["routing"]["releve_scelle"])["empreinte"]
    mutations = [
        (html.replace(sceau, "0" * len(sceau)), "content hash", "le sceau mué"),
        (html.replace('<a class="carte-ev', '<b class="carte-xx', 1), "éventail", "la carte retirée"),
        (re.sub(r'(<span class="ap-eti"[^>]*>)[^<]*', r"\1mensonge", html, count=1), "annotations", "l'annotation réécrite"),
        (html.replace("94.4", "93.4") if "94.4" in html else html.replace("1,000", "9,999"),
         "ne se retrouve pas sur le héros routing", "le chiffre déplacé"),
        (re.sub(r'<p class="lede[^"]*"[^>]*>.*?</p>', "", html, count=1, flags=re.S), "lede", "le lede retiré"),
        (html.replace("</main>", '<nav class="methode-liens"><a href="x">x</a></nav></main>', 1), "rangée de liens", "la rangée remise"),
        (html.replace('<section class="hero">', '<section class="hero"><img src="rendus/robot-x.webp" alt="">', 1), "un robot vit", "un robot sur le héros"),
        (html.replace('<section class="cl"', '<section class="cx"', 1), "ciel :", "le ciel retiré"),
        (html.replace("<b>reproduce</b>", "<b>rerun</b>", 1), "ciel :", "le titre réécrit"),
        (html.replace("<b>inspect</b>", "inspect", 1), "ciel :", "un verbe éteint"),
        (html.replace(".cl-titre b{", ".cl-titre b{color:var(--vert-vif);", 1).replace("color:#fff;text-shadow", "text-shadow", 1), "ciel :", "les verbes en vert"),
    ]
    mutations.append((html, "ciel :", "le ciel sur une page outil", hero + '<section class="cl"></section>'))
    for mue, attendu, nom, *h in mutations:
        fautes = relever(mue, h[0] if h else hero, fd)
        if not any(attendu in f for f in fautes):
            sys.exit(f"GARDE CASSÉE : {nom} ne rougit plus (aucune faute ne parle de "
                     f"« {attendu} ») — aucun relevé n'est rendu (code 2)")
    return []


if __name__ == "__main__":
    docs = pathlib.Path(sys.argv[sys.argv.index("--docs") + 1]) if "--docs" in sys.argv else BASE.parent / "docs"
    html = (docs / "index.html").read_text(encoding="utf-8")
    hero = (docs / "routing" / "index.html").read_text(encoding="utf-8")
    fd = json.loads((BASE / "findings-dossier.json").read_text())
    fautes = temoin(html, hero, fd)
    if fautes:
        for f in fautes:
            print("  ROUGE", f)
        sys.exit(f"{len(fautes)} refus : l'accueil ne tient pas ses affirmations")
    print("témoin de l'accueil : le grand livre recompose son sceau, l'éventail suit le rideau, "
          "la méthode cite le dossier, le ciel tient son titre blanc, et les douze mutations rougissent encore")
