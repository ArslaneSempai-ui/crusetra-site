#!/usr/bin/env python3
"""Assemble le site : bâtit les pages, puis remplit docs/ et source/.

Lancé depuis source/, il se reconnaît et ne recopie pas la chaîne sur
elle-même. Ce qu'il produit :
  docs/    le site bâti, noms de production (index.html, security.html…),
           prêt pour n'importe quel hébergement statique ;
  source/  toute la chaîne de fabrication : bâtisseurs, contenus JSON, relevé,
           scripts Blender : pour que le site reste re-bâtissable.

Le branchement sur la publication N'EST PAS fait ici : docs/ du dépôt
crusetra-routing (dossier local ~/Documents/cascade) est GÉNÉRÉ par `npm run pages` et gardé par des tests
d'empreintes (.sources.json) : y verser ce site est une opération dans ce
dépôt-là, à décider séparément.

Contrôle de liens avec témoin positif : avant de croire « zéro lien cassé »,
le contrôle doit attraper un lien cassé planté exprès.
"""
import json
import pathlib
import re
import shutil
import sys

MAQ = pathlib.Path(__file__).parent
# LE SITE EST LE CHECKOUT QUI PORTE CE SCRIPT, jamais un chemin tapé. Le 9/09 à 03h46, lancé
# depuis un worktree, l'assembleur ancré sur ~/Documents/cascade-site a rasé la source et les
# docs/ du checkout PRINCIPAL (travail non commité du chef effacé, 124 pages servies vidées) :
# une racine absolue fait agir la commande sur un autre dépôt que celui où on la lance.
SITE = MAQ.parent
DOCS = SITE / "docs"
sys.path.insert(0, str(MAQ))
from outil import SITE_URL as BASE_URL, CONTACT, GITHUB, DEPOT_SITE, depot_url  # written once, in outil.py
# Le chemin sous lequel le site est servi se déduit de l'URL : « /cascade-site/ »
# aujourd'hui, « / » le jour du domaine propre. Trois usages en dépendent (la
# base de la 404, l'icône tactile, le contrôle de liens) : ils lisent tous ICI.
from urllib.parse import urlparse
PREFIXE = urlparse(BASE_URL).path

# Le sous-dossier de l'outil rouge : ces pages s'émettent QUAND leurs sources
# existent (les lots S2/S3 les écrivent) ; absentes, l'assembleur le DIT et
# continue : le vert ne dépend pas du rouge. Présentes, toutes les gardes
# s'appliquent, plus une : un commentaire « placeholder » refuse la production.
PROD_SCREENING = {
    "HERO-SCREENING.html": "screening/index.html",
    "INSTRUMENT-SCREENING.html": "screening/instrument.html",
    "ANNEXE-SCREENING-METHODE.html": "screening/method.html",
    "ANNEXE-SCREENING-SECURITE.html": "screening/security.html",
}
PROD_MONITORING = {
    "HERO-MONITORING.html": "monitoring/index.html",
    "INSTRUMENT-MONITORING.html": "monitoring/instrument.html",
    "ANNEXE-MONITORING-METHODE.html": "monitoring/method.html",
    "ANNEXE-MONITORING-SECURITE.html": "monitoring/security.html",
}
PROD_SCORING = {
    "HERO-SCORING.html": "scoring/index.html",
    "INSTRUMENT-SCORING.html": "scoring/instrument.html",
    "ANNEXE-SCORING-METHODE.html": "scoring/method.html",
    "ANNEXE-SCORING-SECURITE.html": "scoring/security.html",
}
PROD_DOSSIER = {
    "HERO-DOSSIER.html": "dossier/index.html",
    "INSTRUMENT-DOSSIER.html": "dossier/instrument.html",
    "ANNEXE-DOSSIER-METHODE.html": "dossier/method.html",
    "ANNEXE-DOSSIER-SECURITE.html": "dossier/security.html",
}

PROD = {
    "ACCUEIL.html": "index.html",           # la page de la MARQUE (décision A, 6/09)
    "HERO.html": "routing/index.html",      # l'outil vert, sous son dossier comme le rouge
    "INSTRUMENT.html": "instrument.html",
    "ENGAGEMENT.html": "engagement.html",
    "ANNEXE-METHODE.html": "method.html",
    "ANNEXE-SECURITE.html": "security.html",
    "ANNEXE-QUESTIONS.html": "questions.html",
    "ANNEXE-TERMS.html": "terms.html",
    "ANNEXE-PRIVACY.html": "privacy.html",
    "ANNEXE-ACCESSIBILITE.html": "accessibility.html",
    "CONTACT.html": "contact.html",
    "ANALYSE-OFAC-2026-07-14.html": "ofac-2026-07-14.html",   # 9/10: the first analysis, Arslane's yes
    "MENTIONS.html": "colophon.html",
    "404.html": "404.html",
}

# ── bâtir d'abord : les pages naissent à côté de ce script ───────────────────
# L'audit du 31/08 a montré l'inverse en danger : un rmtree AVANT de vérifier
# ses entrées détruisait docs/ puis plantait, puisque source/ ne portait pas
# les pages bâties. Ordre tenu : bâtir, vérifier, seulement ensuite effacer.
import datetime
import subprocess

# ── les pièces ne doivent pas bouger SOUS l'assemblage ───────────────────────
# Le 9/09, un pan de rideau vers HERO-SCORING est resté dans les pages émises alors
# que l'émission refusait le bloc : la définition de « prêt » (manques()) est bien
# unique, mais elle est LUE deux fois : par batir-hero au bâti, par la porte à
# l'émission : et entre les deux, une livraison d'états en cours l'a fait changer.
# Le contrôle de liens attrapait le symptôme (liens cassés) ; ceci nomme la cause.
import sys as _sys0
_sys0.path.insert(0, str(MAQ))
from outil import OUTILS as _OUTILS0, manques as _manques0

def photo_pieces():
    return {oid: tuple(_manques0(oid, MAQ)) for oid in _OUTILS0}

def verifier_pieces_stables(avant, apres):
    """Refus nommé si « prêt » a changé entre le bâti et l'émission : les deux
    lectures décriraient deux sites différents, et les pages émises porteraient
    des pans vers des blocs refusés (ou l'inverse). Relancer l'assemblage UNE
    FOIS les livraisons posées ; rien d'autre à corriger."""
    bouges = [oid for oid in avant if bool(avant[oid]) != bool(apres[oid])]
    if bouges:
        detail = "; ".join(f"{oid}: {len(avant[oid])} pièce(s) manquante(s) avant, "
                           f"{len(apres[oid])} après" for oid in bouges)
        sys.exit(f"PIÈCES BOUGÉES PENDANT L'ASSEMBLAGE ({detail}) : les rideaux bâtis et "
                 "la porte d'émission ne décrivent plus le même site : une livraison est "
                 "passée sous l'assemblage ; la poser entière, puis relancer")

_PIECES_AVANT = photo_pieces()

for batisseur in ("batir-hero.py", "batir-instrument.py", "batir-instrument-screening.py",
                  "batir-instrument-monitoring.py", "batir-instrument-scoring.py",
                  "batir-instrument-dossier.py",
                  "batir-offre.py", "batir-annexe.py", "batir-404.py"):
    subprocess.run([sys.executable, str(MAQ / batisseur)], check=True,
                   cwd=str(MAQ), capture_output=True)
manquants = [v for v in PROD if not (MAQ / v).exists()]
if manquants:
    sys.exit(f"pages absentes après bâtisse : {manquants} : rien n'est effacé")
if not (MAQ / "og.png").exists():
    sys.exit("og.png absent : le régénérer depuis og-card.html (capture 1200x630)")

# ── témoin d'abord (lot M-C1) : les gardes de séquences savent-elles encore rougir ? ─────
# manques() porte désormais les quatre gardes de séquences (identité, fraîcheur, poids,
# complétude). Avant de croire un manques() vide, on prouve que chacune voit encore son
# défaut : temoin-sequences.py mue un arbre factice défaut par défaut et exige le rouge.
# Un témoin cassé arrête l'émission AVANT le rmtree de docs/ (l'incident du 9/09 : la porte vivait après le vide, un témoin rouge laissait docs/ vide) : un zéro qui ne sait plus rougir ne garde rien.
_ts = subprocess.run([sys.executable, str(MAQ / "temoin-sequences.py")],
                     capture_output=True, text=True)
if _ts.returncode != 0:
    sys.exit(f"GARDE CASSÉE : un témoin des gardes de séquences ne rougit plus :\n{_ts.stdout}{_ts.stderr}")
# la garde « les étiquettes sur le crème » (Arslane, 9/09) : même preuve avant de croire manques()
_te = subprocess.run([sys.executable, str(MAQ / "temoin-etiquettes.py")], capture_output=True, text=True)
if _te.returncode != 0:
    sys.exit(f"GARDE CASSÉE : le témoin des étiquettes ne rougit plus :\n{_te.stdout}{_te.stderr}")

# ── docs/ : les pages, renommées, liens réécrits ─────────────────────────────
if DOCS.exists():
    shutil.rmtree(DOCS)
DOCS.mkdir(parents=True)

def csp(t):
    """La politique de sécurité de contenu, par empreintes : seuls NOS styles
    et NOS scripts, hachés sur leur contenu final, ont le droit de tourner.
    Tout le reste : connexions, cadres, formulaires, scripts étrangers : est
    refusé. GitHub Pages ne pose pas d'en-têtes ; la balise meta porte tout ce
    qu'une meta peut porter (frame-ancestors, lui, exige un en-tête)."""
    import base64
    import hashlib

    def h(s):
        e = base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
        return f"'sha256-{e}'"

    styles = re.findall(r"<style>(.*?)</style>", t, re.S)
    scripts = re.findall(r"<script>(.*?)</script>", t, re.S)
    style_src = "'self' " + " ".join(h(s) for s in styles)
    # les attributs style="…" (les drapeaux de l'instrument du héros) ne sont
    # pas couverts par les hachés d'éléments : CSP3 les admet un par un via
    # 'unsafe-hashes' : chaque VALEUR d'attribut est hachée, rien d'autre ne passe
    attributs = sorted(set(re.findall(r'style="([^"]*)"', t)))
    if attributs:
        style_src += " 'unsafe-hashes' " + " ".join(h(a) for a in attributs)
    script_src = " ".join(h(s) for s in scripts) if scripts else "'none'"
    regle = ("default-src 'none'; "
             f"style-src {style_src}; "
             f"script-src {script_src}; "
             "font-src 'self'; img-src 'self' data:; media-src 'self'; "
             "base-uri 'self'; "
             "form-action 'none'; connect-src 'none'")
    return t.replace(
        '<meta charset="utf-8">',
        f'<meta charset="utf-8">\n'
        f'<meta http-equiv="Content-Security-Policy" content="{regle}">\n'
        f'<meta name="referrer" content="no-referrer">', 1)


# ── LA MARQUE DESSINÉE (choisie le 6 octobre 2026) ──
#
# Le C de Jost coupé en cinq lignes, la ligne du milieu verte, et « crusetra » vectorisé :
# marque/logo.svg, construit par equipe-cascade/pieces/logo/final/sources/construire.mjs.
# Les lignes et le nom sont en currentColor : la couleur que .marque portait déjà (clair sur
# la nuit, encre sur le papier) les peint ; seule la ligne du milieu garde son vert.
_LOGO = (MAQ / "marque" / "logo.svg").read_text().strip()
_LOGO_INLINE = _LOGO.replace(
    "<svg ", '<svg aria-hidden="true" focusable="false" style="display:block;height:30px;width:auto" ', 1)
_ICONES = (f'<link rel="icon" href="{PREFIXE}favicon.svg" type="image/svg+xml">\n'
           f'<link rel="icon" href="{PREFIXE}favicon-32.png" sizes="32x32" type="image/png">')
_MARQUE_TEXTE = re.compile(r'(<a class="marque" href="[^"]*")>CRUSETRA</a>')
_ICONE = re.compile(r'<link rel="icon" href="[^"]*">')


def entete_prod(t, neuf):
    """Les métadonnées de production : canonique, couleur d'onglet, icône
    tactile, compléments de la carte de partage."""
    # la marque tapée devient la marque dessinée ; l'icône d'onglet devient le C, sur chaque
    # page. Une page qui garde « CRUSETRA » en texte ou une ancienne icône fait échouer la
    # construction : un remplacement qui ne trouve rien ne se tait plus.
    t = _MARQUE_TEXTE.sub(lambda m: f'{m.group(1)} aria-label="Crusetra">{_LOGO_INLINE}</a>', t)
    if ">CRUSETRA</a>" in t:
        sys.exit(f"{neuf} : une marque « CRUSETRA » en texte a échappé au logo dessiné")
    t, nb_icones = _ICONE.subn(lambda m: _ICONES, t, count=1)
    if nb_icones == 0:
        sys.exit(f"{neuf} : aucune icône d'onglet à remplacer par le C")
    if _ICONE.search(t.replace(_ICONES, "")):
        sys.exit(f"{neuf} : une seconde icône d'onglet reste après le C")
    # la racine et /index.html sont la même page : une seule adresse canonique,
    # la racine, sinon les moteurs comptent deux pages et partagent leur poids
    adresse = BASE_URL if neuf == "index.html" else BASE_URL + neuf
    if neuf.endswith("/index.html"):
        adresse = BASE_URL + neuf.removesuffix("index.html")
    # la couleur d'onglet suit la nuit de l'outil : rubis sous screening/, lapis sous monitoring/
    theme = ("#241217" if neuf.startswith("screening/")
             else "#101a30" if neuf.startswith("monitoring/")
             else "#1a1230" if neuf.startswith("scoring/")
             else "#0c0c10" if neuf.startswith("dossier/") else "#14251e")
    # Le fil d'Ariane se pose ICI et pas avant </head> : ces pages n'en ont pas. Elles sont
    # écrites en tête implicite (doctype, html, puis les métas), et une injection cherchant
    # </head> ne trouvait rien et se taisait. Ici, la ligne canonique est notre propre point
    # d'accroche, posé deux lignes plus haut, et csp() qui suit prend l'empreinte du bloc.
    fil = _fil_ariane(neuf, adresse)
    extra = (f'<link rel="canonical" href="{adresse}">\n'
             f'<link rel="apple-touch-icon" href="{PREFIXE}apple-touch-icon.png">\n'
             f'<meta name="theme-color" content="{theme}">'
             + (f'\n{fil}' if fil else ''))
    t = t.replace('<meta name="viewport" content="width=device-width,initial-scale=1">',
                  '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                  + extra, 1)
    # ── LA CARTE DE PARTAGE PORTE UNE IMAGE, ET SES VRAIES MESURES ──
    #
    # Deux défauts mesurés le 13/09. Les quatre pages d'instrument (screening, monitoring,
    # scoring, dossier) n'avaient PAS d'og:image : partagées, elles arrivaient en lien nu.
    # Et les dimensions étaient écrites en dur, 1200x630, sur toutes les pages : vraies pour
    # og.png, fausses dès qu'une autre image sert. Un chiffre tapé à côté d'un fichier finit
    # toujours par mentir sur le fichier.
    #
    # L'affiche de l'outil existe déjà, rendue et servie : c'est elle que reçoit sa page
    # d'instrument. Les mesures se lisent sur le fichier, comme celles des images de la page.
    image = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', t)
    if image is None and "/" in neuf:
        affiche = MAQ / "rendus" / f"affiche-{neuf.split('/', 1)[0]}.jpg"
        if affiche.exists():
            t = t.replace('<meta name="twitter:card"',
                          f'<meta property="og:image" content="{BASE_URL}rendus/{affiche.name}">\n'
                          '<meta name="twitter:card"', 1)
            image = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', t)
    mesures = ""
    if image:
        fichier = MAQ / image.group(1).removeprefix(BASE_URL)
        d = _dimensions(fichier)
        if d:
            mesures = (f'<meta property="og:image:width" content="{d[0]}">\n'
                       f'<meta property="og:image:height" content="{d[1]}">\n')
    t = t.replace('<meta name="twitter:card" content="summary_large_image">',
                  '<meta property="og:site_name" content="Crusetra">\n'
                  '<meta property="og:locale" content="en_US">\n'
                  + mesures
                  + '<meta name="twitter:card" content="summary_large_image">', 1)
    return t


# ── le fil d'Ariane des pages imbriquées ─────────────────────────────────────
#
# Vingt-deux des vingt-huit pages vivent sous un outil (screening/method.html), et un résultat
# de recherche les affichait comme une adresse nue. Un BreadcrumbList dit la place : Crusetra
# puis l'outil puis la page, et le moteur l'affiche à la place de l'URL.
#
# Les noms ne sont PAS retapés : le nom de l'outil se lit dans outils.json, le nom de la page
# dans son propre <title>, après le point médian. Une troisième copie d'un fait ment toujours
# la première, et un fil qui contredit le titre de la page est pire que pas de fil.
_NOM_OUTIL = {"routing": "Routing", "screening": "Screening", "monitoring": "Monitoring",
              "scoring": "Scoring", "dossier": "Dossier"}


def _fil_ariane(page, adresse):
    if "/" not in page:
        return None
    dossier = page.split("/", 1)[0]
    nom = _NOM_OUTIL.get(dossier)
    if not nom:
        return None
    elements = [{"@type": "ListItem", "position": 1, "name": "Crusetra", "item": BASE_URL},
                {"@type": "ListItem", "position": 2, "name": nom, "item": f"{BASE_URL}{dossier}/"}]
    if not page.endswith("/index.html"):
        feuille = {"method.html": "Method", "security.html": "Security",
                   "instrument.html": "Instrument"}.get(page.split("/", 1)[1])
        if not feuille:
            return None
        elements.append({"@type": "ListItem", "position": 3, "name": feuille, "item": adresse})
    bloc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}
    return ('<script type="application/ld+json">'
            + json.dumps(bloc, ensure_ascii=False, separators=(",", ":")) + "</script>")


SCREENING_EMISES = {v: n for v, n in PROD_SCREENING.items() if (MAQ / v).exists()}
for v in PROD_SCREENING:
    if v not in SCREENING_EMISES:
        print(f"  screening : {v} absent (lot S2/S3) : non émis, dit ici")
# Le sous-dossier bleu s'émet EN BLOC : ses quatre pages se référencent entre elles
# (nav, annexes), et une moitié publiée serait un site aux liens morts : le contrôle
# de liens le refuserait de toute façon : autant le dire AVANT, avec la liste.
# Le bleu s'émet EN BLOC, et « prêt » a UNE définition : outil.manques(), la même que
# le rideau consomme : deux définitions ont divergé en une heure (pan montré, page non
# émise : liens morts partout), une seule ne le peut pas.
import sys as _sys
_sys.path.insert(0, str(MAQ))
from outil import manques as _manques
verifier_pieces_stables(_PIECES_AVANT, photo_pieces())

# Le rouge aussi (9/09) : il s'émettait dès que ses pages existaient, sans passer par manques() ;
# depuis que ses états et ses séquences changent (chorégraphie), « prêt » a une seule définition
# pour lui comme pour les trois autres.
EN_BLOC = (("screening", PROD_SCREENING, "S2/S3"),
           ("monitoring", PROD_MONITORING, "L5/L5-textes"),
           ("scoring", PROD_SCORING, "A-L5"),
           ("dossier", PROD_DOSSIER, "D3/D4"))
EMISES_EN_BLOC = {}
for _oid, _prod, _lots in EN_BLOC:
    _absentes = [v for v in _prod if not (MAQ / v).exists()]
    _mq = _manques(_oid, MAQ)
    if _absentes and not _mq:
        # manques() est vide : le rideau MONTRE le pan de cet outil sur toutes les
        # pages : et une page de production manque quand même. C'est toujours un
        # bâtisseur non enregistré (PAGES_* de batir-annexe, liste des bâtisseurs
        # ci-dessus, SPECS du héros) : publier ferait des liens morts, et l'a fait
        # (six vers HERO-SCORING le 9/09). Refus nommé, plus une absence dite.
        sys.exit(f"DIVERGENCE {_oid} : manques() est vide (le pan se montre) mais "
                 f"{_absentes} manquent à l'émission : un bâtisseur n'est pas "
                 "enregistré : l'enregistrer, pas publier")
    if _absentes or _mq:
        if _absentes:
            print(f"  {_oid} : non émis en bloc, il manque {_absentes} (lots {_lots})")
        if _mq:
            print(f"  {_oid} : non émis, {len(_mq)} pièce(s) en attente "
                  f"({', '.join(_mq[:4])}{'…' if len(_mq) > 4 else ''})")
    else:
        EMISES_EN_BLOC.update(_prod)
SOUS_DOSSIER_EMISES = {**EMISES_EN_BLOC}      # le rouge y entre par EN_BLOC, comme les autres


def renommer_liens(t, page_sous_dossier):
    """Les noms SOURCE deviennent les noms de production. Dans une page du
    sous-dossier, une sœur rouge se lie par son nom NU (même dossier) ; depuis
    la racine, par son chemin complet. Les noms rouges se remplacent d'abord :
    plus longs, ils contiennent des fragments qui ressemblent aux verts."""
    for v, n in SOUS_DOSSIER_EMISES.items():
        # dans une page d'un sous-dossier, une sœur du MÊME dossier se lie par son nom nu ;
        # tout autre nom (l'autre outil compris) garde son chemin complet, que le ../ de la
        # source fait sortir correctement
        local = page_sous_dossier and n.startswith(page_sous_dossier)
        t = t.replace(v, n.split("/", 1)[1] if local else n)
    for v, n in PROD.items():
        t = t.replace(v, n)
    return t


# « sealed » nomme l'opération (hashed, then frozen) ; content hash le nombre, signature
# la signature (VOIX, tranché le 10/09). À sa PREMIÈRE apparition sur chaque page, une
# incise le définit une fois ; ensuite le mot nu.
_SCELLE_DEF = " (hashed, then frozen: its content hash is checked before a figure is shown)"
_SCELLE_TERMES = ("sealed public records", "sealed public record", "sealed public dossiers",
                  "sealed public dossier", "sealed records", "sealed record")
# les zones où « sealed » ne se définit PAS : le HÉROS et son lede (l'accroche reste
# légère : le chef, 10/09), le rideau et ses pans, la nav, le pied, les boutons, les
# étiquettes : la définition se pose sur la première mention APRÈS le héros, dans la prose.
_SCELLE_SAUT_TAGS = {"nav", "footer", "button"}
_SCELLE_SAUT_CLS = ("hero", "lede", "rideau", "pan", "ap-eti", "j-titre", "j-cote", "j-num",
                    "note", "cue", "marque", "sceau", "rail", "affiche")
_VOID = {"img", "br", "input", "meta", "link", "hr", "source", "path", "circle", "line", "use", "col"}
# les ÉCRANS retravaillés à la voix (Arslane, 13/09) : ils disent « our public test set »,
# pas « sealed public record », donc l'incise n'a plus rien à y définir. Les annexes de
# méthode et de sécurité gardent le mot ET sa définition, qui est leur place.
_SCELLE_ECRANS = frozenset({
    "index.html", "engagement.html", "contact.html", "404.html", "instrument.html",
    "routing/index.html", "screening/index.html", "monitoring/index.html",
    "scoring/index.html", "dossier/index.html",
    "screening/instrument.html", "monitoring/instrument.html",
    "scoring/instrument.html", "dossier/instrument.html",
})
def definir_sealed(t, page=None):
    """Insère l'incise à la PREMIÈRE mention d'un terme scellé qui vit dans la PROSE DU
    CORPS : dans un <p>, hors rideau/pan, hors nav/pied, hors boutons, titres et étiquettes
    (le chef, 10/09 : jamais dans un titre, une carte, un pied, un lien). Depuis le 13/09,
    rien ne se définit sur un écran retravaillé (_SCELLE_ECRANS)."""
    if page in _SCELLE_ECRANS:
        return t
    saut = 0      # profondeur dans une zone sautée (rideau, nav, pied, bouton, étiquette)
    pp = 0        # profondeur de <p> : on ne définit que dans un paragraphe
    for m in re.finditer(r'<[^>]+>|[^<]+', t):
        frag = m.group(0)
        if frag.startswith("<"):
            if frag.startswith("</"):
                nom = re.match(r'</\s*([a-zA-Z0-9]+)', frag)
                nom = nom.group(1).lower() if nom else ""
                if nom == "p" and pp > 0:
                    pp -= 1
                if saut > 0:
                    saut -= 1
            elif not frag.endswith("/>"):
                nom = re.match(r'<\s*([a-zA-Z0-9]+)', frag)
                nom = nom.group(1).lower() if nom else ""
                if nom in _VOID:
                    continue
                cls = re.search(r'class\s*=\s*"([^"]*)"', frag)
                cls = cls.group(1) if cls else ""
                skip = nom in _SCELLE_SAUT_TAGS or any(c in cls.split() for c in _SCELLE_SAUT_CLS)
                saut += 1 if (skip or saut > 0) else 0
                if nom == "p":
                    pp += 1
            continue
        if saut or pp == 0:
            continue
        for terme in _SCELLE_TERMES:
            k = frag.find(terme)
            if k != -1:
                pos = m.start() + k + len(terme)
                return t[:pos] + _SCELLE_DEF + t[pos:]
    return t



# ── les images servies : dimensions déclarées, chargement différé ────────────
#
# Relevé du 13/09 sur les pages servies : 23 balises <img> par page d'outil, AUCUNE avec
# width/height, AUCUNE avec loading. Conséquences mesurées :
#   - 1,5 Mo d'images tirées d'un coup à l'ouverture, dont la moitié à trois écrans plus bas ;
#   - la place de chaque image inconnue avant son arrivée, donc la page saute pendant qu'elle
#     se remplit (le décalage cumulé, que Google mesure et compte).
#
# La règle : toute image sert avec ses dimensions RÉELLES, lues sur le fichier, jamais tapées.
# Les images du premier et du deuxième écran (le héros, le rideau, l'éventail) se chargent
# tout de suite, parce qu'on ATTERRIT sur le rideau depuis le 13/09 ; tout le reste attend
# d'approcher. `decoding="async"` partout : décoder une image ne doit pas retenir le texte.
def _dimensions(chemin):
    """La taille en pixels, lue dans l'en-tête du fichier. webp, png et jpeg suffisent ici."""
    try:
        b = chemin.read_bytes()
    except OSError:
        return None
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        f = b[12:16]
        if f == b"VP8X":
            return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
        if f == b"VP8 ":
            return (int.from_bytes(b[26:28], "little") & 0x3fff, int.from_bytes(b[28:30], "little") & 0x3fff)
        if f == b"VP8L":
            n = int.from_bytes(b[21:25], "little")
            return ((n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1)
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return (int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big"))
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return (int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big"))
            if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
        return None
    return None


def _etendue(t, ouverture, balise):
    """Le début et la fin d'un conteneur, par comptage de balises : pas d'analyseur HTML
    pour trois conteneurs connus, mais pas de regex naïve non plus (elle s'arrêterait au
    premier </section> imbriqué et la moitié du héros deviendrait paresseuse)."""
    d = t.find(ouverture)
    if d < 0:
        return None
    i, profondeur = d + len(ouverture), 1
    while profondeur and i < len(t):
        o, f = t.find(f"<{balise}", i), t.find(f"</{balise}", i)
        if f < 0:
            return None
        if 0 <= o < f:
            profondeur += 1
            i = o + 1
        else:
            profondeur -= 1
            i = f + len(balise) + 3
    return (d, i)


_EAGER = (('<section class="hero"', "section"), ('<nav class="rideau"', "nav"),
          ('<div class="eventail"', "div"))


# LA RÈGLE QUI DOIT ACCOMPAGNER LES DIMENSIONS, ET SANS LAQUELLE ELLES CASSENT LA PAGE.
#
# `width` et `height` sur un <img> sont des INDICATIONS DE PRÉSENTATION : elles posent
# `height: 1152px` dans la feuille de l'agent. Une règle qui ne fixe que la largeur, comme
# `.j-vig{width:60px;aspect-ratio:1.42/1}`, laisse donc la hauteur naturelle gagner, et
# l'aspect-ratio est ignoré puisque aucune dimension n'est plus automatique.
#
# Mesuré le 13/09, en production, sur les vignettes du rail : 56x1083 au lieu de 56x39. Le
# rail passait de 618 px à 5896 et débordait par le HAUT sur le rideau, puis sur toute la
# hauteur du site. Le banc ne l'a pas vu : il mesure le débord horizontal.
#
# `img{height:auto}` a la spécificité (0,0,1) : elle bat l'indication de présentation et perd
# contre toute règle de composant. C'est la seule ligne qui rend les dimensions sûres, et la
# passe REFUSE de tourner sans elle plutôt que de casser une page en silence.
def _regle_hauteur_auto(t):
    import re as _re
    for m in _re.finditer(r"<style[^>]*>(.*?)</style>", t, _re.S):
        # en DÉBUT DE LIGNE : c'est la forme de la règle de base dans ces feuilles, et cela
        # écarte `.pan img{...}` qui est un composant. Première version : elle exigeait `}` ou
        # `,` avant, et ne trouvait plus la règle dès qu'un commentaire la précédait.
        if _re.search(r"^\s*img\s*\{[^}]*height\s*:\s*auto", m.group(1), _re.M):
            return True
    return False


def images_pretes(t, page):
    """Chaque <img> servie reçoit sa taille réelle, son décodage asynchrone et son mode de
    chargement. Rend le texte et le compte des images vues, pour que l'appelant refuse un
    balayage qui n'a rien fait."""
    tot = [0, 0]                                    # [dimensionnées, différées]
    if not _regle_hauteur_auto(t):
        sys.exit(f"{page} : pas de règle `img{{height:auto}}` dans sa feuille.\n"
                 "  Poser des attributs width/height sans elle laisse la HAUTEUR NATURELLE de\n"
                 "  l'image gagner sur l'aspect-ratio du CSS : une vignette de 60 px a rendu à\n"
                 "  1083 px de haut en production le 13/09, et le rail a débordé sur tout le site.\n"
                 "  Ajouter `height:auto` à la règle `img` de base du bâtisseur de cette page.")
    zones = [z for z in (_etendue(t, o, b) for o, b in _EAGER) if z]
    # Les fichiers ne sont copiés dans docs/ qu'APRÈS cette passe : on résout l'adresse
    # servie, puis on va lire l'octet dans l'arbre SOURCE. Première version : elle lisait
    # docs/ et ne trouvait rien, et son refus l'a dit tout de suite.
    base = (DOCS / page).parent

    def une(m):
        balise, deb = m.group(0), m.start()
        if "width=" in balise and "height=" in balise:
            return balise
        src = re.search(r'src="([^"]+)"', balise)
        if not src or src.group(1).startswith(("data:", "http")):
            return balise
        servie = (base / src.group(1)).resolve()
        try:
            d = _dimensions(MAQ / servie.relative_to(DOCS.resolve()))
        except ValueError:
            return balise
        if not d:
            return balise
        tot[0] += 1
        # La PREMIÈRE image d'une page ne se diffère jamais : sur les pages sans héros ni
        # rideau (les tarifs, un instrument), c'est elle qu'on voit d'abord, et c'est donc
        # elle que Google chronomètre. Mesuré le 13/09 : deux pages la donnaient en paresseuse.
        tot_haut = tot[0] == 1 or any(a <= deb < b for a, b in zones)
        ajouts = f' width="{d[0]}" height="{d[1]}" decoding="async"'
        if not tot_haut:
            ajouts += ' loading="lazy"'
            tot[1] += 1
        return balise[:-1].rstrip() + ajouts + ">"

    return re.sub(r"<img\b[^>]*>", une, t), tot


_vues, _differees = 0, 0
for vieux, neuf in {**PROD, **SOUS_DOSSIER_EMISES}.items():
    t = (MAQ / vieux).read_text()
    t = definir_sealed(t, neuf)
    t = renommer_liens(t, neuf.split("/", 1)[0] + "/" if "/" in neuf else None)
    (DOCS / neuf).parent.mkdir(parents=True, exist_ok=True)
    if neuf == "404.html":
        # servie pour N'IMPORTE QUEL chemin manquant : ses liens relatifs
        # doivent se résoudre depuis la racine du site, pas depuis le chemin raté
        t = t.replace('<meta charset="utf-8">',
                      f'<meta charset="utf-8"><base href="{PREFIXE}">', 1)
    t, _compte = images_pretes(t, neuf)
    _vues += _compte[0]
    _differees += _compte[1]
    (DOCS / neuf).write_text(csp(entete_prod(t, neuf)))

if _vues < 100 or _differees < 40 or _differees >= _vues:
    sys.exit(f"LA PASSE DES IMAGES N'A PAS FAIT SON TRAVAIL : {_vues} dimensionnée(s), "
             f"{_differees} différée(s).\n  Elle doit voir toutes les images servies, en "
             "différer une bonne part, et en garder d'urgentes (héros, rideau, éventail).\n"
             "  Un de ces trois comptes qui s'effondre veut dire que le balayage a raté les "
             "conteneurs ou les fichiers.")
print(f"  images servies : {_vues} dimensionnées sur leur fichier, {_differees} différées "
      f"(héros, rideau et éventail restent immédiats)")

# ── le refus du « placeholder » en production, témoin d'abord ────────────────
# Une page rouge bâtie sur le plateau vert porte un commentaire « placeholder » ;
# la production la refuse : un brouillon qui ressemble à une page finie se
# publie par accident, jamais par décision.
# Le MARQUEUR « <!-- placeholder: » et jamais le mot nu : la prose légitime du
# site dit « replaced by a placeholder » (Security, Privacy), et une garde qui
# rougit sur la prose se fait retirer : première passe rouge, mesurée ce soir.
def _pages_placeholder(dossier):
    return [str(p.relative_to(dossier)) for p in sorted(dossier.rglob("*.html"))
            if "<!-- placeholder:" in p.read_text()]

_tp = DOCS / "zz-temoin-placeholder.html"
_tp.write_text("<!-- placeholder: temoin -->")
if not _pages_placeholder(DOCS):
    sys.exit("GARDE CASSÉE : le témoin « placeholder » planté n'a pas été vu")
_tp.unlink()
brouillons = _pages_placeholder(DOCS)
if brouillons:
    sys.exit(f"PLACEHOLDER en production : {brouillons} : la page attend ses vrais "
             "rendus (tamis-0*.webp) : elle ne part pas comme ça")

# ── le refus du cadratin : décision du 3 septembre, élargie le 13 ──────────────
# Élargi après le fait mesuré du 13/09 : « counts \\u2014 term frequency only » vivait
# dans les DONNÉES JS de l'instrument rouge — un cadratin ÉCHAPPÉ, dans un blob, que ni
# ce refus (html + formes brutes) ni la garde de voix (la prose) ne lisaient. La règle
# devient : aucun U+2014, brut, échappé (\\u2014) ou en entité, dans docs/ quel que soit
# le fichier servi. Témoin planté d'abord : un zéro qui n'a pas vu le témoin ne vaut rien.
_FORMES_CADRATIN = ("\u2014", "\\u2014", "&#8212;", "&mdash;")

def _cadratins(dossier):
    fautives = []
    for p in sorted(dossier.rglob("*")):
        if not p.is_file() or p.suffix not in (".html", ".js", ".json", ".xml", ".txt", ".css", ".svg"):
            continue
        t = p.read_text(errors="replace")
        for forme in _FORMES_CADRATIN:
            if forme in t:
                fautives.append(f"{p.relative_to(dossier)} ({forme!r})")
                break
    return fautives

_tc = DOCS / "zz-temoin-cadratin.js"
_tc.write_text('const x = "counts \\u2014 term frequency only";')
if not _cadratins(DOCS):
    sys.exit("GARDE CASSÉE : le cadratin échappé planté n'a pas été vu — zéro sans valeur")
_tc.unlink()
fautives = _cadratins(DOCS)
if fautives:
    sys.exit(f"CADRATIN dans docs/ (brut, échappé ou entité) : {fautives} : réécrire la source, pas la page")

# ── les données structurées : lisibles, exactes, sans mensonge SEO ───────────
# Trois refus : un bloc ld+json qui ne parse pas ; une clé de notation
# (aggregateRating, review…) qui n'aurait aucune mesure derrière elle ; un prix
# autre que le 0 du grant d'évaluation (les prix payants vivent en clair sur la
# page engagement, jamais dans le balisage). Et la couture source → moteur :
# la FAQ émise est comparée à SA SOURCE (annexe-questions.json), question par
# question, même normalisation que l'émission.
import html as _html
import json as _json

def _nu(fragment):
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())

def _cles(o):
    if isinstance(o, dict):
        yield from o
        for v in o.values():
            yield from _cles(v)
    elif isinstance(o, list):
        for v in o:
            yield from _cles(v)

INTERDITES = {"aggregateRating", "review", "ratingValue", "reviewCount",
              "bestRating", "worstRating"}
blocs_vus = {}
for page in sorted(DOCS.rglob("*.html")):
    for brut in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                           page.read_text(), re.S):
        try:
            donnees = _json.loads(brut)
        except ValueError as e:
            sys.exit(f"JSON-LD invalide dans {page.name} : {e}")
        mauvaises = INTERDITES & set(_cles(donnees))
        if mauvaises:
            sys.exit(f"JSON-LD de {page.name} : {sorted(mauvaises)} : "
                     "aucune mesure derrière : retirer")
        for prix in re.findall(r'"price"\s*:\s*"?([^",}]*)', brut):
            if prix.strip() != "0":
                sys.exit(f"JSON-LD de {page.name} : price={prix} : les prix "
                         "vivent en clair sur la page engagement, pas ici")
        blocs_vus.setdefault(str(page.relative_to(DOCS)), []).append(donnees)

# Le socle se cherche PARMI les blocs de la page, jamais dans « le premier ».
# Le fil d'Ariane s'insère près de la ligne canonique, donc avant lui, et la garde qui lisait
# blocs_vus[page][0] a aussitôt vu un BreadcrumbList sans @graph et déclaré le socle absent
# (13/09). Une garde qui dépend de l'ordre des blocs se casse au premier bloc ajouté.
def _types_du_graphe(page):
    return {n.get("@type") for b in blocs_vus.get(page, []) for n in b.get("@graph", [])}


types_index = _types_du_graphe("index.html")
if not {"Organization", "SoftwareApplication"} <= types_index:
    sys.exit(f"index.html : Organization + SoftwareApplication attendus dans le "
             f"@graph, vu {sorted(t for t in types_index if t)}")

source_q = _json.loads((MAQ / "annexe-questions.json").read_text())
attendues = [_nu(s["h2"]).strip("“” ") for s in source_q["sections"]]
faq = next((b for b in blocs_vus.get("questions.html", [])
            if b.get("@type") == "FAQPage"), None)
if faq is None:
    sys.exit("questions.html : FAQPage absent des données structurées")
publiees = [e["name"] for e in faq.get("mainEntity", [])]
if publiees != attendues:
    sys.exit("FAQPage : les questions émises ne recomposent pas la source : "
             f"{sorted(set(attendues) ^ set(publiees))}")

# le héros vert, sous routing/, porte le même socle de graphe que la racine
types_v = _types_du_graphe("routing/index.html")
if not {"Organization", "SoftwareApplication"} <= types_v:
    sys.exit(f"routing/index.html : Organization + SoftwareApplication attendus, "
             f"vu {sorted(x for x in types_v if x)}")
# le héros rouge, quand il est émis, porte le même socle de graphe que le vert
for sous_index in ("screening/index.html", "monitoring/index.html"):
    if sous_index in blocs_vus:
        types_r = _types_du_graphe(sous_index)
        if not {"Organization", "SoftwareApplication"} <= types_r:
            sys.exit(f"{sous_index} : Organization + SoftwareApplication attendus, "
                     f"vu {sorted(x for x in types_r if x)}")
print(f"  données structurées : "
      f"{sum(len(v) for v in blocs_vus.values())} blocs valides sur "
      f"{len(blocs_vus)} pages ; FAQ recomposée : {len(publiees)} questions")

# ── les ressources réellement référencées ────────────────────────────────────
refs = set()
for page in DOCS.rglob("*.html"):
    for m in re.finditer(r'(?:href|src|poster)="([^"]+)"', page.read_text()):
        u = m.group(1)
        if u.startswith(("http", "#", "data:", "mailto:")):
            continue
        refs.add(str((page.parent / u.split("#")[0]).resolve().relative_to(DOCS.resolve()))
                 if not u.startswith("/") else u.split("#")[0])

(DOCS / "fontes").mkdir()
shutil.copy(MAQ / "fontes" / "literata.css", DOCS / "fontes" / "literata.css")
for w in (MAQ / "fontes").glob("literata-*.woff2"):
    shutil.copy(w, DOCS / "fontes" / w.name)
shutil.copy(MAQ / "fontes" / "roboto-mono.css", DOCS / "fontes" / "roboto-mono.css")
shutil.copy(MAQ / "fontes" / "roboto-mono.woff2", DOCS / "fontes" / "roboto-mono.woff2")
(DOCS / "rendus" / "etats").mkdir(parents=True)
for w in (MAQ / "rendus" / "etats").glob("objet-*.webp"):
    shutil.copy(w, DOCS / "rendus" / "etats" / w.name)
for aff in (MAQ / "rendus").glob("affiche-*.jpg"):        # une affiche par outil filmé
    shutil.copy(aff, DOCS / "rendus" / aff.name)
for rb in (MAQ / "rendus").glob("robot-*.webp"):          # les robots de toutes les couleurs et poses
    shutil.copy(rb, DOCS / "rendus" / rb.name)
# le rapport exemple de la page Screening (29/09) : le PDF et l'image de sa première page, rendus par
# batir-rapport-exemple.py depuis le relevé public ; un PDF qui n'en est pas un, ou trop lourd, ne part pas
# et, depuis le 30/09, celui de la page Routing (batir-rapport-routing.py, le relevé réel CORD) : même contrôle
(DOCS / "rapports").mkdir(exist_ok=True)
for _pdf, _img, _bat in ((MAQ / "rapports" / "screening-sample-report.pdf", MAQ / "rendus" / "rapport-exemple.webp", "batir-rapport-exemple.py"),
                         (MAQ / "rapports" / "routing-sample-report.pdf", MAQ / "rendus" / "rapport-routing.webp", "batir-rapport-routing.py")):
    if not _pdf.exists() or _pdf.read_bytes()[:5] != b"%PDF-":
        sys.exit(f"source/rapports/{_pdf.name} absent ou illisible : relancer {_bat}")
    if _pdf.stat().st_size > 2 * 1048576:
        sys.exit(f"le rapport exemple {_pdf.name} pèse {_pdf.stat().st_size // 1024} Ko, au-dessus de 2 Mo : refusé")
    if not _img.exists() or _img.read_bytes()[8:12] != b"WEBP":
        sys.exit(f"source/rendus/{_img.name} absent ou pas en webp : relancer {_bat}")
    shutil.copy(_pdf, DOCS / "rapports" / _pdf.name)
    shutil.copy(_img, DOCS / "rendus" / _img.name)
# 05/10 (parcours client) : le PDF Screening rend une PASSE FRAÎCHE du fichier d'exemple ; son relevé est servi à côté du
# PDF, puisque la fiche en nomme le scellé et qu'un scellé nommé doit pouvoir se vérifier
_frais = MAQ / "rapports" / "screening-sample-report.screening.json"
if not _frais.exists():
    sys.exit("source/rapports/screening-sample-report.screening.json absent : relancer batir-rapport-exemple.py --record <passe>.screening.json")
shutil.copy(_frais, DOCS / "rapports" / _frais.name)
# 04/10 : the Routing sample is a signed page served beside its PDF ; the served copy must pass cascade's public verifier
_signe = MAQ / "rapports" / "routing-sample-report.html"
if not _signe.exists():
    sys.exit("source/rapports/routing-sample-report.html absent : relancer batir-rapport-routing.py (la page signée)")
shutil.copy(_signe, DOCS / "rapports" / _signe.name)
_v = subprocess.run(["node", str(pathlib.Path.home() / "Documents" / "cascade" / "src" / "verifier-rapport.mjs"), str(DOCS / "rapports" / _signe.name)],
                    capture_output=True, text=True)
if _v.returncode != 0 or "Signature valid" not in _v.stdout:
    sys.exit(f"la page signée SERVIE ne vérifie pas :\n{_v.stdout}{_v.stderr}")
# 04/10 (le chef) : une page signée dont le vérificateur imprime « ? » sur Issued / For / Corpus / Tool porte un bloc de
# données incomplet ; elle vérifie, mais elle ne dit pas à qui ni sur quoi. Refusée, en nommant les lignes.
def _lignes_incompletes(sortie):
    return [l.strip() for l in sortie.splitlines()
            if l.strip().startswith(("Issued", "For ", "Corpus", "Tool")) and "?" in l]
_inc = _lignes_incompletes(_v.stdout)
if _inc:
    sys.exit("la page signée SERVIE porte un bloc de données incomplet (le vérificateur imprime « ? ») :\n  "
             + "\n  ".join(_inc) + "\n  → compléter emisLe, client, corpus.empreinte, corpus.dossiers, outil.commit dans le rendu, re-signer")
print("  " + _v.stdout.strip().splitlines()[0].strip() + " (routing-sample-report.html, servie ; "
      + ", ".join(l.strip() for l in _v.stdout.splitlines() if l.strip().startswith(("Issued", "For ", "Corpus", "Tool"))) + ")")
# Crusetra V4, 6 October 2026: a page that says WHOSE corpus the signed example of the Routing repository was issued on
# quotes that signed file, never a renamed version of it. rapport-exemple.html was signed on 3 September and says
# « cascade's own held-out corpus »; the FAQ had turned it into « Crusetra's ». The signed file cannot be re-signed to
# follow the brand, so the page follows the file (or says « our own », which names nobody).
_exemple_signe = (pathlib.Path.home() / "Documents" / "cascade" / "rapport-exemple.html").read_text()
def _corpus_mal_cite(texte):
    import html as _h
    return [m.group(0) for m in re.finditer(r"\b[A-Z][\w-]*['\u2019]s own (?:synthetic )?held-out corpus", _h.unescape(texte))
            if m.group(0).replace("\u2019", "'") not in _exemple_signe]
def _pages_mal_citees():
    return [f"{pg.relative_to(DOCS)} : « {c} »" for pg in sorted(DOCS.rglob("*.html")) for c in _corpus_mal_cite(pg.read_text())]
# same jaw as the other guards: the matcher on a true and a false sentence, then a planted page the scan must find
if not _corpus_mal_cite("<p>It was issued on Crusetra's own held-out corpus.</p>") or _corpus_mal_cite("<p>on our own held-out corpus</p>"):
    sys.exit("GARDE CASSÉE : la citation du corpus de l'exemple signé ne mord plus (témoin)")
_zzc = DOCS / "zz-temoin-corpus.html"
_zzc.write_text("<p>It was issued with that key on Crusetra&#39;s own held-out corpus.</p>")
if not any(x.startswith("zz-temoin-corpus.html") for x in _pages_mal_citees()):
    sys.exit("GARDE CASSÉE : la citation de l'exemple signé n'a pas vu la page témoin plantée : son zéro ne vaut rien")
_zzc.unlink()
_mal_cites = _pages_mal_citees()
if _mal_cites:
    sys.exit("UNE PAGE CITE MAL L'EXEMPLE SIGNÉ (rapport-exemple.html de crusetra-routing) :\n  " + "\n  ".join(_mal_cites))
print("  exemple signé cité tel quel : aucune page ne lui prête un autre corpus (témoin mordu)")
# les robots de toutes les couleurs partent déjà par le glob ci-dessus (le rideau
# les montre sur toutes les pages) ; seuls les ÉTATS du plateau bleu sont conditionnels
# le PRÉFIXE des états vit dans outil.py seul (ETATS_PREFIXE) : le 8/09, « bassins » ici
# quand le héros disait « rack » a publié cinq liens morts, attrapés par le contrôle
from outil import ETATS_PREFIXE  # noqa: E402
_outils_emis = {n.split("/", 1)[0] for n in EMISES_EN_BLOC.values()}
for _oid in sorted(_outils_emis | {"routing"}):
    for w in (MAQ / "rendus" / "etats").glob(f"{ETATS_PREFIXE[_oid]}-*.webp"):
        shutil.copy(w, DOCS / "rendus" / "etats" / w.name)
    # les séquences de la chorégraphie (lot P-C1) suivent les états : copiées quand
    # l'outil s'émet ET que son dossier existe ; sans séquences, rien : la page bâtie
    # sans manifeste n'y fait de toute façon aucune référence
    _seq = MAQ / "rendus" / "sequences" / ETATS_PREFIXE[_oid]
    if _seq.exists():
        shutil.copytree(_seq, DOCS / "rendus" / "sequences" / ETATS_PREFIXE[_oid])
# LES FILMS (27/09, Arslane : « redirigés vers YouTube, c'est pas très pro ») : joués DANS
# la page par une balise video, servis d'ici. Chaque outil émis doit avoir son
# source/films/<id>.mp4 encodé pour le web : moov EN TÊTE (sinon le navigateur tire tout le
# fichier avant la première image et la recherche dans le film ne marche pas), et sous 25 Mo
# (GitHub Pages refuse à 100 ; au-delà de 25 c'est l'encodage qui a dérivé, pas le film :
# les cinq tiennent entre 13 et 21). Le témoin d'abord : un mp4 où mdat précède moov doit
# être refusé, sinon la garde est un vert vide.
def _moov_en_tete(chemin):
    """Vrai si l'atome moov précède mdat à la racine du mp4 (fichier « faststart »)."""
    with chemin.open("rb") as h:
        pos = 0
        while True:
            h.seek(pos)
            en_tete = h.read(8)
            if len(en_tete) < 8:
                return False
            taille, genre = int.from_bytes(en_tete[:4], "big"), en_tete[4:8]
            if genre == b"moov":
                return True
            if genre == b"mdat":
                return False
            if taille == 1:                                  # taille étendue sur 8 octets
                taille = int.from_bytes(h.read(8), "big")
            if taille < 8:
                return False
            pos += taille


def _atome(genre, corps=b""):
    return (8 + len(corps)).to_bytes(4, "big") + genre + corps


_temoin_film = DOCS / "zz-temoin.mp4"
_temoin_film.write_bytes(_atome(b"ftyp", b"isom") + _atome(b"mdat", b"\0" * 16) + _atome(b"moov", b"\0" * 8))
if _moov_en_tete(_temoin_film):
    sys.exit("CONTRÔLE CASSÉ : un mp4 témoin avec moov APRÈS mdat est passé pour faststart")
_temoin_film.write_bytes(_atome(b"ftyp", b"isom") + _atome(b"moov", b"\0" * 8) + _atome(b"mdat", b"\0" * 16))
if not _moov_en_tete(_temoin_film):
    sys.exit("CONTRÔLE CASSÉ : un mp4 témoin faststart a été refusé")
_temoin_film.unlink()

FILM_MAX = 25 * 1024 * 1024
(DOCS / "films").mkdir()
# 29/09 : la démo Screening est un film de plus sur la page Screening, mêmes gardes (poids, moov)
# 04/10 : la démo Routing aussi (Routing est toujours émis)
# 05/10 (Arslane : « retire-le ») : la démo Screening dit « five sanctions lists » et « measured blind » ; elle n'est plus
# servie, même par lien direct, jusqu'à ce que le chef la refasse. source/films/screening-demo.mp4 reste, rien n'est effacé.
# 07/10: this copy runs whatever FILMS_VISIBLES says, so docs/films keeps its six files byte for byte while no page links them.
for _oid in sorted(_outils_emis | {"routing"}) + ["routing-demo"]:
    film = MAQ / "films" / f"{_oid}.mp4"
    if not film.exists():
        sys.exit(f"source/films/{_oid}.mp4 absent : la page de {_oid} aurait un lecteur sans film")
    if film.stat().st_size > FILM_MAX:
        sys.exit(f"source/films/{_oid}.mp4 : {film.stat().st_size // 1048576} Mo, au-dessus des 25 : ré-encoder (crf 26, preset slow)")
    if not _moov_en_tete(film):
        sys.exit(f"source/films/{_oid}.mp4 : moov après mdat : ré-encoder avec -movflags +faststart")
    shutil.copy(film, DOCS / "films" / film.name)
shutil.copy(MAQ / "releve.json", DOCS / "releve.json")
shutil.copy(MAQ / "og.png", DOCS / "og.png")
(DOCS / ".nojekyll").write_text("")

# Le fichier CNAME : c'est LUI qui déclare le domaine propre à GitHub Pages, et
# docs/ est régénéré à chaque assemblage : s'il n'était pas émis ici, la
# première reconstruction après la bascule ferait tomber le domaine.
HOTE = urlparse(BASE_URL).hostname
if not HOTE.endswith(".github.io"):
    (DOCS / "CNAME").write_text(HOTE + "\n")

# ── robots, plan du site, security.txt : les portes d'entrée normées ─────────
(DOCS / "robots.txt").write_text(
    f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n")
(DOCS / ".well-known").mkdir()
(DOCS / ".well-known" / "security.txt").write_text(
    f"Contact: mailto:{CONTACT}\n"
    f"Contact: {GITHUB}{DEPOT_SITE}/issues\n"
    f"Contact: {depot_url('routing')}/issues\n"
    "Expires: 2027-08-31T00:00:00.000Z\n"
    "Preferred-Languages: en, fr\n"
    f"Canonical: {BASE_URL}.well-known/security.txt\n")
# the site's repository is named once (DEPOT_SITE, outil.py): security.txt above reads it, and the README's title must
# say the same name (V4, 6 October 2026: the repository becomes crusetra-site, and « # cascade-site » would have stayed)
_titre_readme = (SITE / "README.md").read_text().splitlines()[0]
if _titre_readme != f"# {DEPOT_SITE}":
    sys.exit(f"README.md:1 dit « {_titre_readme} », le dépôt du site est {DEPOT_SITE} (outil.py) : corriger le titre")
shutil.copy(MAQ / "apple-touch-icon.png", DOCS / "apple-touch-icon.png")
shutil.copy(MAQ / "marque" / "favicon.svg", DOCS / "favicon.svg")
shutil.copy(MAQ / "marque" / "favicon-32.png", DOCS / "favicon-32.png")
publiques = ([n for n in PROD.values() if n != "404.html"]
             + [n for n in SOUS_DOSSIER_EMISES.values()])
# ── le sitemap porte une DATE, et c'est celle du dépôt ───────────────────────
#
# Sans <lastmod>, un robot doit redemander les vingt-huit pages pour savoir laquelle a bougé.
# La date se LIT dans git, jamais « aujourd'hui » : dater du jour vingt-huit pages dont deux
# ont changé est un chiffre faux, et un sitemap qui ment sur ses dates finit ignoré. Un
# fichier modifié mais pas encore commité rend la date de son dernier commit : en retard,
# jamais en avance, ce qui est le sens sûr.
# La date se lit sur la PAGE SERVIE, pas sur son intermédiaire : les HERO-*.html et
# ANNEXE-*.html sont engendrés et gitignorés, ils n'ont pas d'histoire. docs/ en a une, et
# c'est justement celle que <lastmod> décrit. Si les octets bâtis à l'instant diffèrent de
# ceux du dernier commit, la page change AUJOURD'HUI et le dit ; sinon elle garde la date de
# son dernier vrai changement. Aucune date n'est donc inventée ni avancée.
def _git(args):
    try:
        r = subprocess.run(["git"] + args, cwd=str(MAQ.parent), capture_output=True, check=True)
        return r.stdout
    except Exception:
        return None


def _date_de(page, aujourdhui):
    chemin = f"docs/{page}"
    engagee = _git(["show", f"HEAD:{chemin}"])
    if engagee is None:
        return aujourdhui                      # page neuve : elle paraît aujourd'hui
    if engagee != (DOCS / page).read_bytes():
        return aujourdhui
    d = _git(["log", "-1", "--format=%cI", "--", chemin])
    jour = (d or b"").decode(errors="replace").strip().split("T")[0]
    return jour or aujourdhui


_AUJOURDHUI = datetime.date.today().isoformat()
_lignes, _datees = [], 0
for n in publiques:
    url = BASE_URL + ('' if n == 'index.html'
                      else n.removesuffix('index.html') if n.endswith('/index.html') else n)
    d = _date_de(n, _AUJOURDHUI)
    if d:
        _datees += 1
        _lignes.append(f"  <url><loc>{url}</loc><lastmod>{d}</lastmod></url>\n")
    else:
        _lignes.append(f"  <url><loc>{url}</loc></url>\n")
if _datees < len(publiques):
    sys.exit(f"SITEMAP SANS DATE sur {len(publiques) - _datees} page(s) : la date se lit dans "
             "git,\n  et une page dont la source n'est pas suivie n'en a pas. Inscrire la "
             "source, ou dire ici pourquoi elle n'en a pas.")
(DOCS / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(_lignes)
    + "</urlset>\n")
print(f"  sitemap : {len(publiques)} pages, {_datees} datées sur leur dernier commit")

# ── la garde de dérive : le compte de tests que le site PUBLIE ───────────────
# Le 31 août, le dépôt est passé de 584/65 à 595/66 en une heure et le site a
# continué d'afficher l'ancien : sur la page même qui promet qu'un tel chiffre
# « cannot silently rot ». La règle vérifiable devient donc un refus.
# Elle dit AUSSI quand elle n'a pas pu regarder : un silence se lirait comme un
# accord, et c'est exactement le vert vide qu'on cherche à éviter.
# Chaque OUTIL est vérifié contre SON dépôt : le compte du rouge sur une page
# rouge, celui du vert sur une page verte. Croiser les deux ferait rougir un
# site juste : les deux dépôts n'ont pas le même compte, et c'est normal.
def verifier_comptes(pages, depot, etiquette):
    publie = set()
    for page in pages:
        publie |= set(re.findall(r"(\d+) tests(?: across (\d+) files)?",
                                 page.read_text()))
    if not publie:
        return
    comptes = {n for n, _ in publie}
    fichiers = {f for _, f in publie if f}
    if not depot.exists():
        print(f"  ! compte de tests {etiquette} NON VÉRIFIÉ : {depot} absent : "
              f"le site publie {sorted(comptes)} / {sorted(fichiers)}")
        return
    m = re.search(r"\*\*(\d+) tests\*\*(?: across (\d+) files)?", depot.read_text())
    if not m:
        sys.exit(f"la phrase des tests est introuvable dans {depot} : "
                 f"garde cassée, son silence ne vaut rien")
    vrai_n, vrai_f = m.group(1), m.group(2)
    if comptes - {vrai_n} or (vrai_f and fichiers - {vrai_f}):
        sys.exit(f"DÉRIVE DU COMPTE DE TESTS ({etiquette}) : le dépôt dit {vrai_n} / "
                 f"{vrai_f}, le site publie {sorted(comptes)} / {sorted(fichiers)} "
                 f"— corriger les JSON avant d'assembler")
    print(f"  compte de tests {etiquette} vérifié : {vrai_n} tests")

verifier_comptes(sorted(DOCS.glob("*.html")) + sorted((DOCS / "routing").glob("*.html")),
                 pathlib.Path.home() / "Documents" / "cascade" / "README.md", "routing")
verifier_comptes(sorted((DOCS / "screening").glob("*.html")) if (DOCS / "screening").exists() else [],
                 pathlib.Path.home() / "Documents" / "cascade-screening" / "README.md", "screening")
verifier_comptes(sorted((DOCS / "monitoring").glob("*.html")) if (DOCS / "monitoring").exists() else [],
                 pathlib.Path.home() / "Documents" / "cascade-monitoring" / "README.md", "monitoring")
verifier_comptes(sorted((DOCS / "scoring").glob("*.html")) if (DOCS / "scoring").exists() else [],
                 pathlib.Path.home() / "Documents" / "cascade-scoring" / "README.md", "scoring")
verifier_comptes(sorted((DOCS / "dossier").glob("*.html")) if (DOCS / "dossier").exists() else [],
                 pathlib.Path.home() / "Documents" / "cascade-dossier" / "README.md", "dossier")

# ── la garde des citations : « Where it lives » doit encore dire vrai ────────
# Le site invite un relecteur bancaire à OUVRIR chaque chemin. Une citation qui
# a glissé de vingt lignes le fait tomber sur autre chose, et c'est pire qu'une
# absence de citation. Mesuré le 31/08 : le durcissement de l'outil a déplacé 7
# des 38 citations : un contrôle de bornes serait passé, elles pointaient toutes
# dans un fichier de la bonne taille. On vérifie donc le CONTENU de la ligne.
# Chaque OUTIL contre SON dépôt et SON fichier d'ancres (ancrer-citations.py les
# régénère) : les pages rouges citent cascade-screening, les vertes cascade.
def verifier_citations(pages, ancres_fichier, outil, etiquette):
    citees = set()
    for page in pages:
        citees |= set(re.findall(r"[A-Za-z0-9_./-]+\.(?:ts|mjs|json|md|js):\d+",
                                 page.read_text()))
    if not citees:
        return
    if not ancres_fichier.exists():
        print(f"  ! citations {etiquette} NON VÉRIFIÉES : {ancres_fichier.name} absent : "
              f"{len(citees)} citées")
        return
    if not outil.exists():
        print(f"  ! citations {etiquette} NON VÉRIFIÉES : {outil} absent : {len(citees)} citées")
        return
    ancres = _json.loads(ancres_fichier.read_text())["ancres"]
    fautes = []
    for c in sorted(citees):
        if c not in ancres:
            fautes.append(f"{c} : aucune ancre déclarée"); continue
        chemin, n = c.rsplit(":", 1)
        f = outil / chemin
        if not f.exists():
            fautes.append(f"{c} : fichier absent de l'outil"); continue
        lignes = f.read_text(errors="replace").splitlines()
        n = int(n)
        if n > len(lignes):
            fautes.append(f"{c} : au-delà de la fin ({len(lignes)} lignes)"); continue
        if lignes[n - 1].strip() != ancres[c]:
            ou = [i + 1 for i, x in enumerate(lignes) if x.strip() == ancres[c]]
            fautes.append(f"{c} : la ligne a changé"
                          + (f", le contenu est en {chemin}:{ou[0]}" if len(ou) == 1
                             else ", contenu introuvable"))
    if fautes:
        sys.exit(f"CITATIONS {etiquette.upper()} QUI NE DISENT PLUS VRAI :\n  " + "\n  ".join(fautes)
                 + f"\n  corriger les JSON, puis régénérer {ancres_fichier.name} (ancrer-citations.py)")
    print(f"  citations {etiquette} vérifiées ligne à ligne contre l'outil : {len(citees)}")

verifier_citations(sorted(DOCS.glob("*.html")) + sorted((DOCS / "routing").glob("*.html")),
                   MAQ / "ancres-citations.json",
                   pathlib.Path.home() / "Documents" / "cascade", "routing")
verifier_citations(sorted((DOCS / "screening").glob("*.html")) if (DOCS / "screening").exists() else [],
                   MAQ / "ancres-citations-screening.json",
                   pathlib.Path.home() / "Documents" / "cascade-screening", "screening")
verifier_citations(sorted((DOCS / "monitoring").glob("*.html")) if (DOCS / "monitoring").exists() else [],
                   MAQ / "ancres-citations-monitoring.json",
                   pathlib.Path.home() / "Documents" / "cascade-monitoring", "monitoring")
verifier_citations(sorted((DOCS / "scoring").glob("*.html")) if (DOCS / "scoring").exists() else [],
                   MAQ / "ancres-citations-scoring.json",
                   pathlib.Path.home() / "Documents" / "cascade-scoring", "scoring")
verifier_citations(sorted((DOCS / "dossier").glob("*.html")) if (DOCS / "dossier").exists() else [],
                   MAQ / "ancres-citations-dossier.json",
                   pathlib.Path.home() / "Documents" / "cascade-dossier", "dossier")

# ── la garde de la voix (VOIX.md) : la copy SERVIE, motif par motif ──────────
# Témoin planté d'abord, comme pour les liens : une page zz aux restes bannis DOIT
# rougir avant qu'un zéro soit cru ; puis la vraie passe, et un refus arrête
# l'assemblage en nommant page et ligne. garde-voix.py joue en plus son propre
# témoin interne (fixtures fautive/saine) à chaque lancement : code 2 = garde cassée.
_zzv = DOCS / "zz-temoin-voix.html"
_zzv.write_text("<p>The benign twins say so before your eyes.</p>")
_gv = subprocess.run([sys.executable, str(MAQ / "garde-voix.py"), "--docs", str(DOCS)],
                     capture_output=True, text=True)
if _gv.returncode == 0:
    sys.exit("GARDE CASSÉE : la garde de la voix n'a pas vu la page témoin plantée : "
             "son zéro ne vaut rien")
_zzv.unlink()
_gv = subprocess.run([sys.executable, str(MAQ / "garde-voix.py"), "--docs", str(DOCS)],
                     capture_output=True, text=True)
if _gv.returncode != 0:
    sys.exit("LA VOIX N'EST PAS TENUE (garde-voix, VOIX.md) :\n" + _gv.stdout[-2400:])
print("  " + next(l.strip() for l in _gv.stdout.splitlines() if "voix tenue" in l))

# ── l'orthographe américaine (30/09, Arslane : « c'est plus américain », décision : tout le site) ──
# Même mâchoire que la voix : une page plantée doit la faire rougir avant que son zéro soit cru.
_zzo = DOCS / "zz-temoin-orthographe.html"
_zzo.write_text("<p>The licence of the organisation.</p>")
_go = subprocess.run([sys.executable, str(MAQ / "garde-orthographe.py"), "--docs", str(DOCS)], capture_output=True, text=True)
if _go.returncode == 0:
    sys.exit("GARDE CASSÉE : la garde de l'orthographe n'a pas vu la page témoin plantée : son zéro ne vaut rien")
_zzo.unlink()
_go = subprocess.run([sys.executable, str(MAQ / "garde-orthographe.py"), "--docs", str(DOCS)], capture_output=True, text=True)
if _go.returncode != 0:
    sys.exit("L'ORTHOGRAPHE N'EST PAS AMÉRICAINE (garde-orthographe) :\n" + _go.stdout[-2400:] + _go.stderr[-400:])
print("  " + next(l.strip() for l in _go.stdout.splitlines() if "orthographe" in l))

# ── the addresses (Crusetra, 6 October 2026): one domain, one contact address, the repositories ──
# under their GitHub names, all read from outil.py. Same jaw as the voice: a planted page must turn
# it red before its zero is believed; garde-adresses.py also runs its own witness (exit 2 = broken).
_zza = DOCS / "zz-temoin-adresses.html"
_zza.write_text('<a href="mailto:contact@cascade-routing.com">contact@cascade-routing.com</a>')
_ga = subprocess.run([sys.executable, str(MAQ / "garde-adresses.py"), "--docs", str(DOCS)], capture_output=True, text=True)
if _ga.returncode == 2:
    # its inner witness refused: a rule no longer bites, or a constant of outil.py makes the clean text faulty
    sys.exit("GARDE CASSÉE (garde-adresses, son témoin interne) :\n" + _ga.stdout[-1200:] + _ga.stderr[-400:])
if _ga.returncode != 1 or "zz-temoin-adresses.html" not in _ga.stdout:
    sys.exit("GARDE CASSÉE : la garde des adresses n'a pas vu la page témoin plantée : son zéro ne vaut rien\n"
             + _ga.stdout[-1200:] + _ga.stderr[-400:])
_zza.unlink()
_ga = subprocess.run([sys.executable, str(MAQ / "garde-adresses.py"), "--docs", str(DOCS)], capture_output=True, text=True)
if _ga.returncode != 0:
    sys.exit("LES ADRESSES NE SONT PAS CELLES DE LA MAISON (garde-adresses, outil.py) :\n"
             + _ga.stdout[-2400:] + _ga.stderr[-400:])
print("  " + next(l.strip() for l in _ga.stdout.splitlines() if "adresses tenues" in l))

# ── the list count (Crusetra V4, 6 October 2026): Screening reads the lists of its committed manifest, ten ──
# since the sources-plus merge; a served sentence that counts them otherwise is refused. Same jaw: a planted
# page must turn it red first, and garde-listes.py runs its own witness (exit 2 = broken).
_zzl = DOCS / "zz-temoin-listes.html"
_zzl.write_text("<h2>Your list of names, screened against seven sanctions lists.</h2>")
# and one on another tool's page: until 7 October 2026 routing/ was skipped whole, and this sentence passed
_zzr = DOCS / "routing" / "zz-temoin-listes.html"
_zzr.write_text("<p>Crusetra Screening reads seven sanctions lists.</p>")
_gl = subprocess.run([sys.executable, str(MAQ / "garde-listes.py"), "--docs", str(DOCS)], capture_output=True, text=True)
_zzr.unlink()
if _gl.returncode == 2:
    sys.exit("GARDE CASSÉE (garde-listes, son témoin interne) :\n" + _gl.stdout[-1200:] + _gl.stderr[-400:])
if _gl.returncode != 1 or "  zz-temoin-listes.html:" not in _gl.stdout or "routing/zz-temoin-listes.html:" not in _gl.stdout:
    sys.exit("GARDE CASSÉE : la garde des listes n'a pas vu les pages témoins plantées : son zéro ne vaut rien\n"
             + _gl.stdout[-1200:] + _gl.stderr[-400:])
_zzl.unlink()
_gl = subprocess.run([sys.executable, str(MAQ / "garde-listes.py"), "--docs", str(DOCS)], capture_output=True, text=True)
if _gl.returncode != 0:
    sys.exit("LE COMPTE DES LISTES N'EST PAS CELUI DE L'OUTIL (garde-listes, listes-manifest.json) :\n"
             + _gl.stdout[-2400:] + _gl.stderr[-400:])
print("  " + next(l.strip() for l in _gl.stdout.splitlines() if "listes tenues" in l))

# ── le témoin de l'accueil : le grand livre, l'éventail, la méthode ──────────
# Statique et auto-témoigné par mutation (quatre mues doivent rougir avant que le
# vert soit cru) ; un accueil dont le sceau, les cartes ou les citations dérivent
# ne s'émet pas. verif-final tient la mâchoire du débranchement sur sa ligne.
_ta = subprocess.run([sys.executable, str(MAQ / "temoin-accueil.py"), "--docs", str(DOCS)],
                     capture_output=True, text=True)
if _ta.returncode != 0:
    sys.exit("L'ACCUEIL NE TIENT PAS SES AFFIRMATIONS (temoin-accueil) :\n" + _ta.stdout[-2000:] + _ta.stderr[-400:])
print("  " + _ta.stdout.strip().splitlines()[-1])

# ── le témoin des tarifs, moitié statique (la moitié navigateur vit au banc) ─
_tt = subprocess.run([sys.executable, str(MAQ / "temoin-tarifs.py"), "--statique", "--docs", str(DOCS)],
                     capture_output=True, text=True)
if _tt.returncode != 0:
    sys.exit("LES TARIFS NE TIENNENT PAS LEUR STRUCTURE (temoin-tarifs) :\n" + _tt.stdout[-2000:] + _tt.stderr[-400:])
print("  " + _tt.stdout.strip().splitlines()[0].strip())

# ── the films switch (FILMS_VISIBLES, outil.py), 7 October 2026 ──────────────
# The six films and their YouTube uploads still say the old brand name. Hidden, no served file may carry a
# player, a film card, a YouTube link or a link to films/*.mp4 (the mp4 files stay in docs/films, unlinked, so
# the switch turns back without a re-encode); shown, each emitted tool page must carry its own film, as before.
# Same jaw as the other guards: a planted page must turn the hidden scan red, and a page without its film must
# turn the shown check red, before either green is believed.
from outil import FILMS_VISIBLES  # noqa: E402
_TRACE_FILM = re.compile(r'<video\b|films/[\w.-]+\.mp4|youtu\.be/|youtube\.com/|class="film"|class="carte-film|data-film=|data-yt=',
                         re.I)


def _traces_de_film(dossier):
    return [f"{f.relative_to(dossier)} : {m.group(0)}" for f in sorted(dossier.rglob("*"))
            if f.is_file() and f.suffix in (".html", ".xml", ".txt", ".json")
            for m in _TRACE_FILM.finditer(f.read_text(errors="replace"))]


def _film_absent(texte, oid):
    return '<section class="film">' not in texte or f"films/{oid}.mp4" not in texte


_pages_outils = {"routing": "routing/index.html"} | {n.split("/", 1)[0]: n for n in EMISES_EN_BLOC.values()
                                                     if n.endswith("/index.html")}
# 10/10: FILMS_VISIBLES is a set of film names (outil.py). A tool whose film is listed must carry it on its page;
# every other film (Monitoring, Scoring, the demos: still "Cascade") must be linked from NO served file, and the
# old YouTube uploads (the "Cascade" cuts) neither. Each half bites its witness before its green is believed.
_YT_CASCADE = ("SXxViU7rhU8", "aNZ5uks7ibE", "AoINd6J2XMI", "xx_1lFJsw9E", "mCybN-xq4jA", "mTlpC9yXnXo")


def _traces_cachees(dossier):
    """Every served trace of a film that is not shown: a link to its mp4, or an old "Cascade" YouTube upload."""
    return [t for t in _traces_de_film(dossier)
            if (re.search(r'films/([\w-]+)\.mp4', t) and re.search(r'films/([\w-]+)\.mp4', t).group(1) not in FILMS_VISIBLES)
            or any(y in t for y in _YT_CASCADE)] + [
            f"{f.relative_to(dossier)} : {y}" for f in sorted(dossier.rglob("*.html")) for y in _YT_CASCADE if y in f.read_text(errors="replace")]


if not _film_absent("<main></main>", "routing") or _film_absent(
        '<section class="film"><video><source src="../films/routing.mp4"></video></section>', "routing"):
    sys.exit("BROKEN GUARD: the shown-films check no longer tells a page with its film from one without")
_zzf = DOCS / "zz-temoin-films.html"
_zzf.write_text('<video><source src="films/monitoring.mp4"></video><a href="https://youtu.be/SXxViU7rhU8">YouTube</a>')
_vu = any(x.startswith("zz-temoin-films.html") for x in _traces_cachees(DOCS))
_zzf.unlink()
if not _vu:
    sys.exit("BROKEN GUARD: the hidden-films scan did not see the planted page: its zero is worth nothing")
_sans_film = [n for oid, n in sorted(_pages_outils.items()) if oid in FILMS_VISIBLES and _film_absent((DOCS / n).read_text(), oid)]
if _sans_film:
    sys.exit(f"these tool pages should carry their film (FILMS_VISIBLES) and do not: {_sans_film}")
_pages_cachees = [(oid, n) for oid, n in sorted(_pages_outils.items()) if oid not in FILMS_VISIBLES]
_traces = [f"{n} : {m.group(0)}" for oid, n in _pages_cachees for m in _TRACE_FILM.finditer((DOCS / n).read_text())] + _traces_cachees(DOCS)
if _traces:
    sys.exit("a hidden film is still linked from the served files:\n  " + "\n  ".join(sorted(set(_traces))))
print(f"  films guard held: {sum(1 for o in _pages_outils if o in FILMS_VISIBLES)} tool pages carry their film "
      f"({', '.join(sorted(o for o in _pages_outils if o in FILMS_VISIBLES))}), {len(_pages_cachees)} without "
      f"({', '.join(o for o, _ in _pages_cachees)}), 0 link to a hidden film or an old upload (witnesses bitten)")

# ── le contrôle de liens, témoin d'abord ─────────────────────────────────────
def liens_casses(dossier):
    casses = []
    for page in sorted(dossier.rglob("*.html")):
        for m in re.finditer(r'(?:href|src|poster)="([^"]+)"', page.read_text()):
            u = m.group(1).split("#")[0]
            if u.startswith(("http", "data:", "mailto:")) or not u:
                continue
            # racine-relatif sous le préfixe du site : {PREFIXE}x → x ; sinon
            # RELATIF AU RÉPERTOIRE DE LA PAGE (../x depuis screening/), et un
            # répertoire se sert comme son index.html
            if u.startswith(PREFIXE):
                cible = dossier / (u.removeprefix(PREFIXE) or "index.html")
            elif u.startswith("/"):
                casses.append(f"{page.relative_to(dossier)} → {m.group(1)} (racine hors préfixe)")
                continue
            else:
                cible = (page.parent / u).resolve()
                d = dossier.resolve()
                if d != cible and d not in cible.parents:
                    casses.append(f"{page.relative_to(dossier)} → {m.group(1)} (sort du site)")
                    continue
            if cible.is_dir():
                cible = cible / "index.html"
            if not cible.exists():
                casses.append(f"{page.relative_to(dossier)} → {m.group(1)}")
    return casses

temoin = DOCS / "zz-temoin.html"
temoin.write_text('<a href="fantome-inexistant.css">x</a>')
if not any("fantome-inexistant" in c for c in liens_casses(DOCS)):
    sys.exit("CONTRÔLE CASSÉ : le témoin planté n'a pas été trouvé : zéro sans valeur")
temoin.unlink()

casses = liens_casses(DOCS)
if casses:
    sys.exit("LIENS CASSÉS :\n  " + "\n  ".join(casses))

# ── source/ : la chaîne de fabrication, sans les déchets ─────────────────────
SRC = SITE / "source"
if MAQ.resolve() == SRC.resolve():
    # lancé depuis source/ : la chaîne est déjà là, rien à recopier
    print(f"docs/ : {len(PROD)} pages + ressources ; témoin retrouvé, "
          f"0 lien cassé sur {len(refs)} référencés")
    sys.exit(0)
if SRC.exists():
    shutil.rmtree(SRC)
SRC.mkdir()
for f in MAQ.iterdir():
    if f.name in PROD or f.name in {"__pycache__", "apercu", "directions",
                                    "refonte", "controle", "PARCOURS.html"}:
        continue
    if f.name.startswith("U") and f.suffix == ".html":
        continue
    if f.is_dir():
        if f.name == "fontes":
            (SRC / "fontes").mkdir()
            for w in f.iterdir():
                if w.name.startswith("literata"):
                    shutil.copy(w, SRC / "fontes" / w.name)
        else:
            shutil.copytree(f, SRC / f.name,
                            ignore=shutil.ignore_patterns("__pycache__"))
    else:
        shutil.copy(f, SRC / f.name)

nb_docs = len(list(DOCS.rglob("*")))
nb_src = len(list(SRC.rglob("*")))
print(f"docs/ : {len(PROD)} pages + ressources, {nb_docs} entrées ; "
      f"témoin retrouvé, 0 lien cassé sur {len(refs)} référencés")
print(f"source/ : {nb_src} entrées")
