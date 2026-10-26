#!/usr/bin/env python3
"""LA TABLE DES OUTILS : ce qui change quand la page change d'outil, et rien d'autre.

Le site est le CATALOGUE de la marque (ARCHITECTURE-CATALOGUE.md) : la barre, le
pied, la nuit, le parchemin et les gardes sont partagés ; la couleur d'accent, le
robot, le relevé scellé, les textes et le sous-dossier sont PAR OUTIL, et ils
vivent tous ici. Un bâtisseur qui tape une de ces valeurs chez lui recrée la
divergence que cette table existe pour fermer.

LA PALETTE : le vert historique reste écrit sous ses noms (--vert-*) pour que la
page verte reste identique À L'OCTET ; le rubis introduit les variables
--accent-* et ALIASE les --vert-* dessus, si bien que tout le CSS partagé écrit
en var(--vert-*) rend rubis sans être touché. Le jour où une palette neutre est
voulue partout, le vert bascule sur le même mécanisme en un seul endroit : ici.
"""
import hashlib
import filecmp
import json
import pathlib
import re
import sys

_MAISON = pathlib.Path.home() / "Documents"

# THE HOUSE ADDRESSES, WRITTEN ONCE (Crusetra, waves 2 and 3, 6 October 2026). The domain was
# typed on 31 lines in 9 builders, and a rename always missed one. The builders, the assembler
# (BASE_URL, CNAME, robots, sitemap, security.txt) and the annexes read them here; the content
# JSON may type the address in prose, and garde-adresses.py refuses a served file that names any
# other address of ours: the old domain, an old repository name, or a foreign contact address.
DOMAINE = "crusetra.com"
SITE_URL = f"https://{DOMAINE}/"
CONTACT = f"contact@{DOMAINE}"
GITHUB = "https://github.com/ArslaneSempai-ui/"
# the repositories under their GitHub names; the local folders keep theirs (~/Documents/cascade...)
DEPOTS = {"routing": "crusetra-routing", "screening": "crusetra-screening",
          "monitoring": "crusetra-monitoring", "scoring": "crusetra-scoring",
          "dossier": "crusetra-dossier"}
DEPOT_SITE = "crusetra-site"   # the site's own repository, under its GitHub name (the local folder keeps cascade-site)
ORGANISATION = {"@type": "Organization", "@id": f"{SITE_URL}#org", "name": "Crusetra",
                "url": SITE_URL, "logo": f"{SITE_URL}og.png", "email": CONTACT}
# The films shown on the site, by file name in source/films (10 October 2026, Arslane: "vas y fais le").
# Routing, Dossier and Screening are re-voiced as Crusetra; Monitoring, Scoring and the Routing demo still say
# "Cascade" and stay hidden (unlinked) until they are remade. A demo shows only when "<tool>-demo" is listed.
FILMS_VISIBLES = frozenset({"routing", "dossier", "screening"})


def depot_url(outil_id):
    """The public repository of a tool, under its GitHub name."""
    return GITHUB + DEPOTS[outil_id]


def _canonique(x, racine=True):
    """Le JSON canonique de empreinteDuReleve (cascade-screening/src/empreinte.ts),
    porté en Python : clés triées, la clé `empreinte` exclue À LA RACINE seulement."""
    if isinstance(x, list):
        return [_canonique(v, False) for v in x]
    if isinstance(x, dict):
        return {k: _canonique(x[k], False) for k in sorted(x)
                if not (racine and k == "empreinte")}
    return x


def _stringify(x):
    """JSON.stringify, à l'octet : séparateurs compacts, unicode brut, et les
    nombres au format de JS (les floats de Python impriment pareil ; un float
    ENTIER comme 1.0 imprimerait « 1.0 » là où JS écrit « 1 » : converti)."""
    def entier(o):
        if isinstance(o, float) and o.is_integer():
            return int(o)
        if isinstance(o, list):
            return [entier(v) for v in o]
        if isinstance(o, dict):
            return {k: entier(v) for k, v in o.items()}
        return o
    return json.dumps(entier(x), separators=(",", ":"), ensure_ascii=False)


def empreinte_du_releve(releve):
    return hashlib.sha256(_stringify(_canonique(releve)).encode()).hexdigest()[:16]


def lire_releve_scelle(chemin):
    """Le relevé public d'un outil, REFUSÉ si absent ou si son scellé ment :
    une page bâtie sur un relevé retouché publierait des chiffres que personne
    n'a mesurés, avec l'autorité du site."""
    chemin = pathlib.Path(chemin)
    if not chemin.exists():
        sys.exit(f"{chemin} introuvable : les chiffres ne se tapent pas, ils se lisent")
    releve = json.loads(chemin.read_text())
    porte = releve.get("empreinte")
    if not isinstance(porte, str) or not porte:
        sys.exit(f"{chemin} ne porte aucun scellé : rien ne prouve que c'est le relevé mesuré")
    calcule = empreinte_du_releve(releve)
    if calcule != porte:
        sys.exit(f"{chemin} ne correspond plus à son scellé (porté {porte}, calculé {calcule}) : "
                 "le fichier a changé après scellement, rien ne se bâtit dessus")
    return releve


# ── la palette, en deux rendus ───────────────────────────────────────────────
# Le vert : la ligne HISTORIQUE, à l'octet — elle est comparée par les tests de
# non-régression de l'assemblage (docs/ inchangé). Le rubis : les --accent-*
# remplis, et les --vert-* aliasés dessus pour que le CSS partagé suive.
PALETTE_VERTE = "--vert-titre:#23543f;--vert-vif:#57b184;--vert-clair:#a5f7cb;"
PALETTE_RUBIS = ("--accent-titre:#7a1f2e;--accent-vif:#d64a5c;--accent-clair:#ffc2c9;"
                 "--vert-titre:var(--accent-titre);--vert-vif:var(--accent-vif);"
                 "--vert-clair:var(--accent-clair);")
# LA NUIT suit l'outil aussi (Arslane, 6/09 : « pourquoi le terminal à droite n'est
# pas rouge aussi ? ») : sur la page rouge, le héros, le panneau des findings, la
# section instrument et le pied sont une nuit rubis, la même que l'instrument rouge
# et que le pan du rideau ; le parchemin, lui, reste celui de la maison.
NUIT_VERTE = "--nuit-a:#1b3229;--nuit-b:#14251e;--nuit-c:#0e1a15;--sur-vert:#e4ecdf;--sur-vert-pale:#a9bdaf;"
NUIT_RUBIS = "--nuit-a:#33191f;--nuit-b:#241217;--nuit-c:#180b0f;--sur-vert:#efe0e2;--sur-vert-pale:#c0a6ab;"
PALETTE_LAPIS = ("--accent-titre:#1f3f7a;--accent-vif:#4f8ae0;--accent-clair:#c3d8ff;"
                 "--vert-titre:var(--accent-titre);--vert-vif:var(--accent-vif);"
                 "--vert-clair:var(--accent-clair);")
NUIT_LAPIS = "--nuit-a:#16213a;--nuit-b:#101a30;--nuit-c:#0a111f;--sur-vert:#e6ecf7;--sur-vert-pale:#a8b7d4;"
PALETTE_AMETHYSTE = ("--accent-titre:#4b2a7a;--accent-vif:#9b6fe0;--accent-clair:#e2d3ff;"
                     "--vert-titre:var(--accent-titre);--vert-vif:var(--accent-vif);"
                     "--vert-clair:var(--accent-clair);")
NUIT_AMETHYSTE = "--nuit-a:#241a3a;--nuit-b:#1a1230;--nuit-c:#100b1f;--sur-vert:#ede6f7;--sur-vert-pale:#b9a9d4;"
PALETTE_ONYX = ("--accent-titre:#1c1c22;--accent-vif:#8a8a96;--accent-clair:#e8e6df;"
                "--vert-titre:var(--accent-titre);--vert-vif:var(--accent-vif);"
                "--vert-clair:var(--accent-clair);")
NUIT_ONYX = "--nuit-a:#121216;--nuit-b:#0c0c10;--nuit-c:#070709;--sur-vert:#efede6;--sur-vert-pale:#b8b6ad;"

OUTILS = {
    "routing": {
        "id": "routing",
        "nom": "Routing",
        # depuis le 6/09 (décision A d'Arslane), la racine est la page de la MARQUE ;
        # Routing vit sous routing/ comme Screening sous screening/
        "sous_dossier": "routing/",
        "prefixe_racine": "../",
        # 13/09 nuit : trois lecteurs sur cinq ne savaient pas ce qu'est un « model tier »
        # ni un « field » ; la question le dit en clair, le héros définit le terme ensuite.
        # LE RIDEAU TIENT DANS L'ÉCRAN (13/09, nuit) : à 1440x900 les cinq boutons « Open » doivent
        # rester au-dessus du pli ; une question de plus de quatre lignes les fait tomber dessous
        # (mesuré : neuf lignes sur le Dossier, boutons à 1005 px). Sept mots au plus par question,
        # trois lignes de pitch ; temoin-rideau.mjs le mesure.
        "question": "How much model does each field need?",
        "palette": PALETTE_VERTE,
        "favicon_accent": "%2323543f",
        "robots": ("robot-penche.webp", "robot-agrippe.webp"),
        "releve": _MAISON / "cascade" / "landing.json",     # pas de scellé : garde d'absence seule (historique)
        # le RELEVÉ SCELLÉ du vert (son relevé de référence, marqué et re-scellé le 8/09) : la
        # source unique du sceau que les pages vertes citent ; landing.json reste le fichier de chiffres
        "releve_scelle": _MAISON / "cascade" / "profiles-2026-08-20-coeur-rendu.json",
        "outil_chemin": _MAISON / "cascade",
        "depot": depot_url("routing"),
        # le rideau (deuxième écran) : ce que le pan de CET outil dit de lui, sur
        # TOUTE page ; ses teintes vivent ici parce que la page rubis aliase la
        # palette et que le pan vert doit y rester vert
        "page_hero": "HERO.html",
        "etiquette": "Routing &#183; identity-field extraction",
        "pitch": "A cheap script reads some identity fields well, while others need a model. Routing measures which fields still need one.",
        "robot_rideau": "robot-salut.webp",           # il salue (etats/robots-rideau.py)
        "vif": "#57b184",
        "nuit": ("#1b3229", "#14251e", "#0e1a15"),
    },
    "screening": {
        "id": "screening",
        "nom": "Screening",
        "sous_dossier": "screening/",
        "prefixe_racine": "../",
        # pas d'insécable ici : « which threshold? » d'un bloc déborde à 320 px (mesuré)
        # 13/09 : la question prend les mots de l'outil (décision d'Arslane) ; le moule
        # « Which X suffices, at which threshold? » se lisait comme un gabarit généré
        # 13/09 nuit, consigne A1 : « matcher » arrivait AVANT sa définition, et la
        # question du rideau se lit sur les 28 pages : elle dit la chose en clair
        "question": "Where should your matching bar sit?",
        "palette": PALETTE_RUBIS,
        "favicon_accent": "%237a1f2e",
        "robots": ("robot-rubis-penche.webp", "robot-rubis-agrippe.webp"),
        "releve": _MAISON / "cascade-screening" / "releve-public.json",  # scellé, vérifié par lire_releve_scelle
        # le relevé du matcher de sociétés et navires (releve-entites.json, scellé et signé dans l'outil) :
        # la section « Company and vessel names » de la page s'y branche par son scellé, comme le héros
        "releve_entites": _MAISON / "cascade-screening" / "releve-entites.json",
        "outil_chemin": _MAISON / "cascade-screening",
        "depot": depot_url("screening"),
        "page_hero": "HERO-SCREENING.html",
        "etiquette": "Screening &#183; name matching",
        "pitch": "Raise it and you miss real matches. Lower it and your analysts drown in alerts. Screening puts a number on each.",
        "robot_rideau": "robot-rubis-curieux.webp",   # il se penche, curieux (etats/robots-rideau.py)
        # l'affiche du film : la plaque 3D (etats/affiche-plaque.py) + la carte des deux
        # chiffres de la frontière lus dans le relevé (etats/affiche-composer.py)
        "affiche": "affiche-screening.jpg",
        "affiche_alt": "The ruby Crusetra robot, palms up, projecting the two rates of the "
                       "setting it picks: what it catches on the left, false alerts on the right.",
        "vif": "#d64a5c",
        "nuit": ("#33191f", "#241217", "#180b0f"),      # la nuit rubis de NUIT_RUBIS
    },
    "monitoring": {
        "id": "monitoring",
        "nom": "Monitoring",
        "sous_dossier": "monitoring/",
        "prefixe_racine": "../",
        # « earns its alerts » : lu comme un slogan par deux lecteurs, mal compris par trois
        "question": "Which scenarios catch real cases?",
        "palette": PALETTE_LAPIS,
        "favicon_accent": "%231f3f7a",
        "robots": ("robot-lapis-penche.webp", "robot-lapis-montre.webp"),
        "releve": _MAISON / "cascade-monitoring" / "releve-public.json",  # scellé, vérifié par lire_releve_scelle
        "outil_chemin": _MAISON / "cascade-monitoring",
        # le dépôt n'existe pas encore en ligne : lien mort jusqu'au push d'Arslane,
        # exactement comme le rouge avant le sien
        "depot": depot_url("monitoring"),
        "page_hero": "HERO-MONITORING.html",
        "etiquette": "Monitoring &#183; transaction monitoring",
        "pitch": "A scenario that fires a hundred times a week is cheap to write and expensive to work through. Monitoring weighs the two.",
        "robot_rideau": "robot-lapis-montre.webp",    # il montre (rendu du chef)
        # l'affiche : plaque lapis (affiche-plaque.py --accent lapis) + les deux chiffres
        # de la fiche 03 lus dans le relevé (ici deux BORNES BASSES, champ « bas » :
        # aucune cellule ne tient le plancher, l'affiche le dit avec les deux meilleures)
        "affiche": "affiche-monitoring.jpg",
        "affiche_alt": "The lapis Crusetra robot, palms up, projecting the two highest shares "
                       "any single scenario is sure of catching: amount on the left, "
                       "peer on the right, both under the 0.90 floor.",
        "vif": "#4f8ae0",
        "nuit": ("#16213a", "#101a30", "#0a111f"),      # la nuit lapis de NUIT_LAPIS
    },
    "scoring": {
        "id": "scoring",
        "nom": "Scoring",
        "sous_dossier": "scoring/",
        "prefixe_racine": "../",
        # « sort » : rang, classement, tri ? le lecteur devait deviner
        "question": "Which risk factors separate risky from quiet?",
        "palette": PALETTE_AMETHYSTE,
        "favicon_accent": "%234b2a7a",
        "robots": ("robot-amethyste-penche.webp", "robot-amethyste-pese.webp"),
        "releve": _MAISON / "cascade-scoring" / "releve-public.json",   # scellé par le lot A-L4 (à venir) : l'entrée reste gated par manques()
        "outil_chemin": _MAISON / "cascade-scoring",
        "depot": depot_url("scoring"),
        "page_hero": "HERO-SCORING.html",
        "etiquette": "Scoring &#183; risk rating",
        "pitch": "Risk weights come from policy, which writes them once and rarely tests them against what happened next. Scoring tests them.",
        "robot_rideau": "robot-amethyste-pese.webp",    # il pèse : sa pose à lui
        "affiche": "affiche-scoring.jpg",
        "affiche_alt": "The amethyst Crusetra robot, palms up, projecting the two shares the card "
                       "names: product on the left, behaviour on the right, both under the 0.90 floor.",
        "vif": "#9b6fe0",
        "nuit": ("#241a3a", "#1a1230", "#100b1f"),
    },
    "dossier": {
        "id": "dossier",
        "nom": "Dossier",
        "sous_dossier": "dossier/",
        "prefixe_racine": "../",
        # « signed » n'était expliqué nulle part sur les écrans (panel, 13/09 nuit)
        "question": "Does the whole chain still hold?",
        "palette": PALETTE_ONYX,
        "favicon_accent": "%231c1c22",
        "robots": ("robot-onyx-penche.webp", "robot-onyx-tient.webp"),
        "releve": _MAISON / "cascade-dossier" / "releve-public.json",   # scellé 2497928ec273023c (D1 lu + D2 mesuré)
        "outil_chemin": _MAISON / "cascade-dossier",
        "depot": depot_url("dossier"),
        "page_hero": "HERO-DOSSIER.html",
        "etiquette": "Dossier &#183; the audit dossier",
        "pitch": "Four reports, four tools. The Dossier checks each one and signs its answer, so that your reviewer can verify it.",
        "robot_rideau": "robot-onyx-tient.webp",        # il tient la pièce
        "affiche": "affiche-dossier.jpg",
        "affiche_encre": "#2a2a31",                    # le gris vif de l'onyx s'efface sur la plaque : l'encre projetée est plus sombre
        "affiche_alt": "The onyx Crusetra robot, palms up, projecting two counts from our public test set: "
                       "the questions holding the fresh control on the left, those not holding it on the right.",
        "vif": "#8a8a96",
        "nuit": ("#121216", "#0c0c10", "#070709"),
    },
}


# ── ce qu'il faut à un outil pour être MONTRÉ et ÉMIS : une seule définition,
#    consommée par le rideau (batir-hero) ET par la porte d'émission (assembler).
#    Deux définitions ont divergé en une heure le 7/09 : le rideau montrait un pan
#    vers une page que l'assembleur refusait d'émettre : liens morts sur tout le site.
ETATS_PREFIXE = {"routing": "objet", "screening": "tamis", "monitoring": "rack",
                 "scoring": "rayonnage", "dossier": "escalier"}   # rack, rayonnage, escalier : tranchés par Arslane sur planches
ICONES_PREFIXE = {"screening": "objet-screening", "monitoring": "objet-monitoring",
                  "scoring": "objet-scoring", "dossier": "objet-dossier"}
ICONES_NOMS = ("methode", "securite", "terms", "privacy", "accessibilite")


def manques(outil_id, base):
    """La liste de ce qui MANQUE à un outil du catalogue pour être prêt : vide = prêt.
    Routing et Screening sont en ligne et leurs pièces sont commitées : liste vide par
    construction ; le test reste exécuté pour eux, pour qu'une pièce retirée se voie."""
    base = pathlib.Path(base)
    o = OUTILS[outil_id]
    m = []
    if outil_id != "routing":
        chemin_f = base / f"findings-{outil_id}.json"
        if not chemin_f.exists():
            m.append(f"findings-{outil_id}.json")
        else:
            # un fichier de findings livré AVANT le scellé de son relevé porte pret:false
            # (le lot des textes refuse de deviner les chiffres) : il compte comme absent,
            # en le disant — sinon le rideau montrerait un pan dont le héros refuse de se bâtir
            try:
                f = json.loads(chemin_f.read_text())
            except ValueError:
                f = {"pret": False}
            if not f.get("pret", True):
                m.append(f"findings-{outil_id}.json (pret: false : les chiffres attendent leur sceau)")
            elif "sceau" in f and f["sceau"] != lire_releve_scelle(o["releve"])["empreinte"]:
                # le relevé a été re-scellé depuis que les textes ont dérivé leurs chiffres
                # (une re-mesure post-A-L4, par exemple) : le héros refuserait de se bâtir,
                # et le rideau montrerait un pan mort — LA définition de « prêt » doit le
                # voir AVANT, sinon les deux divergent exactement comme bassins/rack
                m.append(f"findings-{outil_id}.json (sceau {f['sceau']} : le relevé porte "
                         f"{lire_releve_scelle(o['releve'])['empreinte']}, à re-dériver)")
        # les SOURCES des deux annexes comptent parmi les pièces : le 9/09, le pan
        # scoring s'est montré sur quatre pages pendant que la porte d'émission disait
        # « il manque ANNEXE-SCORING-*.html » — six liens morts ; la même définition
        # de « prêt » doit couvrir TOUT ce que le bloc émet
        for piece in (f"annexe-{outil_id}-methode.json", f"annexe-{outil_id}-securite.json"):
            if not (base / piece).exists():
                m.append(piece)
    if not (base / "rendus" / o["robot_rideau"]).exists():
        m.append(f"rendus/{o['robot_rideau']}")
    prefixe = ETATS_PREFIXE[outil_id]
    m += [f"rendus/etats/{prefixe}-0{i}.webp" for i in range(1, 6)
          if not (base / "rendus" / "etats" / f"{prefixe}-0{i}.webp").exists()]
    if outil_id in ICONES_PREFIXE:
        m += [f"rendus/etats/{ICONES_PREFIXE[outil_id]}-{n}.webp" for n in ICONES_NOMS
              if not (base / "rendus" / "etats" / f"{ICONES_PREFIXE[outil_id]}-{n}.webp").exists()]
    m += manques_sequences(outil_id, base)
    m += manques_etiquettes(outil_id, base)
    return m


# Le sceau du vert, LU dans son relevé scellé et vérifié : cinq bâtisseurs le tapaient à la main
# (1151f5a1cfaae0c0) et le relevé a été re-scellé le 8/09 (marques kind/version) : un sceau
# recopié rouille ; celui-ci suit le fichier.
# ── les gardes des séquences (lot M-C1) ─────────────────────────────────────────
#
# Quatre gardes, DANS manques() — la même définition de « prêt » que le rideau, le héros
# et l'assembleur (la divergence bassins/rack a coûté des liens morts sur tout le site) :
#   identité    l'état k EST la dernière image de sa transition, octet pour octet — sinon
#               l'arrêt du mouvement montrerait une autre image que celle qui porte les
#               annotations d'Écriture ;
#   fraîcheur   manifest.sceau == le sceau du relevé public de l'outil — des séquences
#               rendues sur un relevé re-scellé montreraient les chiffres d'avant ;
#   poids       la somme des images d'une page ≤ BUDGET_SEQUENCE_KO, constante déclarée —
#               dépasser n'est pas interdit, dépasser en silence l'est ;
#   complétude  n × 5 fichiers présents, aux pixels du manifeste — une image manquante est
#               un refus côté bâtisseur ; la voisine, c'est le repli du NAVIGATEUR en
#               direct, jamais une émission silencieusement trouée.
# Un outil SANS séquence n'est pas un outil cassé : sans manifeste, aucune garde ne parle.

# Le budget d'une page de séquences, en kilo-octets. AUCUN chiffre non mesuré : le chef le
# pose après le premier rendu de livraison (mesure + date dans ce commentaire-là). Tant
# qu'il vaut None, des séquences livrées sont REFUSÉES : un budget non écrit est une
# intention, et une intention ne se dépasse jamais.
# MESURÉ le 9/09/2026 sur les deux premières livraisons : le rack, 5 × 24 images webp q92 = 10156 ko ;
# le tamis (maille, jetons : deux fois plus de détail) = 17 712 ko à q92, 13256 ko replumé à q80, la
# qualité des images de passage désormais (plumer --q 80). Le budget est la plus lourde plus 8 %,
# arrondi au demi-millier ; une page au-dessus refuse d'être assemblée (garde « poids », M-C1).
# Piste si l'on veut plus léger : rendre les images de passage à 1100 px (le contrat des tailles
# uniques est à revoir avec Mesure et Portfolio d'abord).
BUDGET_SEQUENCE_KO = 14500

def taille_webp(chemin):
    """(largeur, hauteur) d'un webp, lues dans l'en-tête (VP8X / VP8L / VP8), sans
    dépendance. Un fichier illisible rend None : la garde le dira, elle ne plantera pas."""
    try:
        d = pathlib.Path(chemin).read_bytes()[:30]
    except OSError:
        return None
    if len(d) < 30 or d[:4] != b"RIFF" or d[8:12] != b"WEBP":
        return None
    quatre = d[12:16]
    if quatre == b"VP8X":
        return (int.from_bytes(d[24:27], "little") + 1, int.from_bytes(d[27:30], "little") + 1)
    if quatre == b"VP8L":
        if d[20] != 0x2F:
            return None
        bits = int.from_bytes(d[21:25], "little")
        return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    if quatre == b"VP8 ":
        if d[23:26] != b"\x9d\x01\x2a":
            return None
        return (int.from_bytes(d[26:28], "little") & 0x3FFF, int.from_bytes(d[28:30], "little") & 0x3FFF)
    return None


def sceau_du_releve(outil_id):
    """Le sceau du relevé public d'un outil — le vert par son relevé scellé historique
    (landing.json n'en porte pas), les quatre autres par leur releve-public.json."""
    o = OUTILS[outil_id]
    chemin = o["releve_scelle"] if outil_id == "routing" else o["releve"]
    return lire_releve_scelle(chemin)["empreinte"]


_BUDGET_DECLARE = object()   # sentinelle : « lis la constante » ; un témoin injecte la sienne

def manques_sequences(outil_id, base, budget_ko=_BUDGET_DECLARE, sceau_attendu=None):
    """Ce qui manque aux SÉQUENCES d'un outil pour être prêtes : vide = prêtes, ou pas de
    séquences du tout. budget_ko et sceau_attendu sont injectables pour les témoins ; la
    production passe par les défauts (BUDGET_SEQUENCE_KO, sceau_du_releve)."""
    base = pathlib.Path(base)
    prefixe = ETATS_PREFIXE[outil_id]
    dossier = base / "rendus" / "sequences" / prefixe
    ou = f"rendus/sequences/{prefixe}"
    if not (dossier / "manifest.json").exists():
        return []
    m = []
    try:
        man = json.loads((dossier / "manifest.json").read_text())
    except ValueError as e:
        return [f"{ou}/manifest.json (illisible : {e})"]
    absentes = [k for k in ("prefixe", "n", "transitions", "ext", "large", "haut", "mouvement", "sceau")
                if k not in man]
    if absentes:
        return [f"{ou}/manifest.json (clé(s) absente(s) : {', '.join(absentes)})"]

    # fraîcheur : des séquences rendues sur un relevé re-scellé montrent les chiffres d'avant
    attendu = sceau_attendu if sceau_attendu is not None else sceau_du_releve(outil_id)
    if man["sceau"] != attendu:
        m.append(f"{ou} (sceau {man['sceau']} : le relevé porte {attendu} — séquences rendues "
                 f"sur un autre relevé, à re-rendre)")

    # complétude : n × transitions fichiers, aux pixels du manifeste
    defauts = []
    octets = 0
    for k in range(1, man["transitions"] + 1):
        for i in range(man["n"]):
            f = dossier / f"{man['prefixe']}-seq-0{k}-{i:03d}{man['ext']}"
            if not f.exists():
                defauts.append(f"{ou}/{f.name} (image manquante : pas de voisine servie en silence)")
                continue
            octets += f.stat().st_size
            t = taille_webp(f)
            if t != (man["large"], man["haut"]):
                lue = f"{t[0]}×{t[1]}" if t else "en-tête illisible"
                defauts.append(f"{ou}/{f.name} ({lue} : le manifeste dit {man['large']}×{man['haut']})")
    m += defauts[:6]
    if len(defauts) > 6:
        m.append(f"{ou} (… et {len(defauts) - 6} autre(s) défaut(s) de complétude)")

    # identité : l'état k EST la dernière image de sa transition, octet pour octet
    for k in range(1, man["transitions"] + 1):
        etat = base / "rendus" / "etats" / f"{prefixe}-0{k}.webp"
        derniere = dossier / f"{man['prefixe']}-seq-0{k}-{man['n'] - 1:03d}{man['ext']}"
        if etat.exists() and derniere.exists() and not filecmp.cmp(etat, derniere, shallow=False):
            m.append(f"rendus/etats/{prefixe}-0{k}.webp (n'est pas la dernière image de sa "
                     f"transition : l'arrêt du mouvement montrerait une autre image que "
                     f"l'état annoté)")

    # poids : un budget non écrit est une intention, et une intention ne se dépasse jamais
    budget = BUDGET_SEQUENCE_KO if budget_ko is _BUDGET_DECLARE else budget_ko
    if budget is None:
        m.append(f"{ou} (BUDGET_SEQUENCE_KO non déclaré dans outil.py : le chef le pose, "
                 f"mesure et date à l'appui, après le premier rendu de livraison)")
    elif octets / 1000 > budget:
        m.append(f"{ou} ({octets / 1000:.0f} Ko de séquences : le budget déclaré est "
                 f"{budget} Ko — dépasser se dit, il ne se constate pas en production)")
    return m


SCEAU_ROUTING = lire_releve_scelle(OUTILS["routing"]["releve_scelle"])["empreinte"]

def lien(outil, cible):
    """Le lien d'une page de CET outil vers une cible de la MAISON (nom source,
    ex. « ENGAGEMENT.html », « rendus/x.webp ») : préfixé pour sortir du
    sous-dossier quand il y en a un. Les liens entre pages d'un même outil ne
    passent pas ici : ils restent nus, sœurs de dossier."""
    return outil["prefixe_racine"] + cible


# ── LE PIED, UNE SEULE FOIS (Arslane, 13/09) ─────────────────────────────────────────────
# Onze pieds écrits à la main dans huit bâtisseurs, sept feuilles de style, et un lien souligné
# qu'il a trouvé « dégueulasse » deux fois de suite. Six maquettes plus tard il a choisi : la
# promesse et son bouton de preuve à gauche, le compte de tests et l'empreinte à droite, puis
# le rang des pages sous un filet, SANS répéter le bouton dedans (« pour pas l'avoir deux
# fois »). Une fonction, une feuille : les bâtisseurs l'appellent et n'en dessinent plus.
# 04/10 (Arslane) : une seule phrase sur les 29 pages, vraie partout : les outils tournent chez le client, rien ne nous
# parvient sauf ce qu'il envoie (le relevé scellé de l'audit) ; les appels aux fournisseurs du client partent chez eux,
# sous ses clés, jamais chez nous ; aucune télémétrie (la page Privacy le tient par un test).
PIED_PROMESSE = "The tools run on your machine. Nothing reaches us unless you send it."

# les pages de la maison, dans l'ordre où un relecteur les cherche. Ce sont des NOMS de pages,
# pas des actions (le motif 8 de garde-voix vise les liens d'action) ; « Pricing » n'y est pas :
# la barre du haut le porte déjà sur chaque page.
LIENS_MAISON = [("ANNEXE-METHODE.html", "Method"), ("ANNEXE-SECURITE.html", "Security"),
                ("ANNEXE-QUESTIONS.html", "Questions"), ("ANNEXE-TERMS.html", "Terms"),
                ("ANNEXE-PRIVACY.html", "Privacy"), ("ANNEXE-ACCESSIBILITE.html", "Accessibility"),
                ("CONTACT.html", "Contact"), ("MENTIONS.html", "The fine print")]
_PROPRES_A_L_OUTIL = {"ANNEXE-METHODE.html", "ANNEXE-SECURITE.html", "ANNEXE-QUESTIONS.html"}


def n_tests(outil):
    """Le compte de tests d'un outil, lu dans SON README (« **N tests** across F files »), jamais
    tapé : la garde de dérive de l'assembleur le recompare au dépôt page par page."""
    m = re.search(r"\*\*(\d+) tests\*\*", (outil["outil_chemin"] / "README.md").read_text())
    if not m:
        sys.exit(f"le compte de tests est introuvable dans le README de "
                 f"{outil['outil_chemin'].name} : refus de le recopier")
    return m.group(1)


def pied_html(outil=None, sceau=None, tests=None, courante=None, prefixe=None):
    """Le pied du site, identique partout.
    `outil` : l'outil dont la page fait partie (ses Method/Security propres, son dépôt) ; None
    pour une page de la maison (accueil, tarifs, annexes de la maison). Routing EST la maison :
    ses annexes sont les annexes de la maison, seul son dépôt s'ajoute.
    `sceau` : l'empreinte servie ; `tests` : le compte de tests, lu par n_tests() ; l'un ou
    l'autre absent, la ligne n'est pas émise (un vide se lirait comme un chiffre).
    `courante` : le nom source de la page, pour marquer son propre lien dans le rang.
    `prefixe` : d'ordinaire celui de l'outil (« ../ » sous son dossier) ; l'instrument du
    routing, servi à la racine, passe « » explicitement.
    Sur la page Privacy, la phrase reste seule : le bouton mènerait ici."""
    if prefixe is None:
        prefixe = outil["prefixe_racine"] if outil else ""
    if outil and outil["id"] != "routing":
        ident = outil["id"].upper()
        liens = [(f"ANNEXE-{ident}-METHODE.html", "Method"), (f"ANNEXE-{ident}-SECURITE.html", "Security")]
        liens += [(prefixe + h, n) for h, n in LIENS_MAISON if h not in _PROPRES_A_L_OUTIL]
    else:
        liens = [(prefixe + h, n) for h, n in LIENS_MAISON]
    if outil:
        liens.append((outil["depot"], "Repository"))
    rang = "".join(f'<a href="{h}"' + (' aria-current="true"' if h == courante else "") + f'>{n}</a>'
                   for h, n in liens)
    preuve = "" if courante == "ANNEXE-PRIVACY.html" else (
        f'\n      <a class="pied-preuve" href="{prefixe}ANNEXE-PRIVACY.html">See how we prove it '
        f'<span aria-hidden="true">&#8594;</span></a>')
    forte = f"{tests} tests" if tests else "measured, then frozen"
    faible = f"content hash {sceau}" if sceau else ""
    promesse = PIED_PROMESSE
    return (f'<footer class="pied"><div class="colonne">\n'
            f'  <div class="pied-h">\n'
            f'    <div class="pied-g"><p class="pied-p">{promesse}</p>{preuve}</div>\n'
            f'    <p class="pied-meta"><b>{forte}</b>{faible}</p>\n'
            f'  </div>\n'
            f'  <nav class="pied-liens" aria-label="Pages">{rang}</nav>\n'
            f'</div></footer>')


# La feuille du pied. Les couleurs passent par currentColor et par des variables à repli
# (--sur-vert chez le vert, --sur chez le rubis, le lapis, l'onyx, l'améthyste et les tarifs) :
# la même règle tient sur les cinq palettes sans qu'un bâtisseur la redessine. Les bâtisseurs
# gardent .pied (fond, couleur, marges) et la taille de .pied-p ; tout le reste est ici.
CSS_PIED_SITE = '''
  /* the footer, drawn once for every builder (Arslane, 13/09: the promise and its proof button
     on the left, the count and the hash on the right, the pages in a row under a hairline) */
  footer.pied .colonne{display:block}
  footer.pied .pied-h{display:flex;align-items:center;justify-content:space-between;gap:22px 32px;flex-wrap:wrap}
  footer.pied .pied-g{display:flex;align-items:center;gap:28px;flex-wrap:wrap}
  footer.pied .pied-p,footer.pied .pied-meta{margin:0}
  .pied-preuve{display:inline-block;font:400 11px/1 var(--mono,ui-monospace,monospace);letter-spacing:.16em;
    text-transform:uppercase;color:inherit;text-decoration:none;white-space:nowrap;padding:12px 18px;border-radius:8px;
    border:1px solid color-mix(in srgb,currentColor 30%,transparent);transition:background .2s,color .2s,border-color .2s}
  .pied-preuve:hover,.pied-preuve:focus-visible{background:var(--sur-vert,var(--sur,#e4ecdf));
    color:var(--nuit-c,var(--noir-b,#0e1a15));border-color:transparent}
  .pied-meta{text-align:right;font:400 11px/1.9 var(--mono,ui-monospace,monospace);letter-spacing:.04em;
    color:var(--sur-vert-pale,var(--sur-pale,#a9bdaf))}
  .pied-meta b{display:block;font-weight:400;letter-spacing:.16em;text-transform:uppercase;color:var(--sur-vert,var(--sur,#e4ecdf))}
  .pied-liens{display:flex;align-items:baseline;gap:6px 22px;flex-wrap:wrap;margin-top:28px;padding-top:16px;
    border-top:1px solid color-mix(in srgb,currentColor 14%,transparent);
    font:400 11px/1 var(--mono,ui-monospace,monospace);letter-spacing:.14em;text-transform:uppercase}
  .pied-liens a{color:var(--sur-vert-pale,var(--sur-pale,#a9bdaf));text-decoration:none;padding:7px 0;transition:color .2s}
  .pied-liens a:hover,.pied-liens a:focus-visible{color:var(--sur-vert,var(--sur,#e4ecdf))}
  .pied-liens a[aria-current]{color:var(--sur-vert,var(--sur,#e4ecdf));box-shadow:0 1.5px 0 currentColor}
  @media (max-width:700px){
    footer.pied .pied-h,footer.pied .pied-g{flex-direction:column;align-items:flex-start}
    footer.pied .pied-g{gap:18px}
    .pied-meta{text-align:left}
    /* on a phone the row wraps on three lines : each link becomes a 36 px target, and the
       rows no longer add their own gap on top of it */
    .pied-liens{gap:0 22px;padding-top:6px}
    .pied-liens a{padding:12px 0}
  }
'''


# ── LES ÉTIQUETTES SUR LE CRÈME, JAMAIS SUR L'OBJET (Arslane, 9/09 : « les infos directement
# sur le modèle, ça les rend illisibles ; mets-les toujours sur le fond crème ») ──────────
# Une annotation est une pointe (ax, ay) SUR l'objet et une étiquette (lx, ly) à côté. Depuis
# les gros plans, l'objet remplit l'image et une étiquette posée au hasard tombe dessus. La
# règle est mécanique : l'alpha de l'image d'état est lu sous la boîte de l'étiquette ; plus
# d'un dixième de pixels d'objet, et le bloc de l'outil n'est pas prêt (manques()).
# Géométrie du héros (batir-hero.py) : viewBox 1420×1000, l'image (rapport 1374/1120) centrée ;
# une chip .ap-eti fait au plus 240 px sur 2 lignes dans une scène de ~744 px pour 1420 unités.
IW_ANNOT = 1000.0 * (1374 / 1120)
MX_ANNOT = (1420 - IW_ANNOT) / 2
# La chip fait 240 px FIXES (max-width) sur ~44 px de haut pour deux lignes, mais la scène rétrécit
# avec la fenêtre : 744 px à 1440, ~477 px à 1081 (la plus petite fenêtre encore annotée, avant
# le @media ≤ 1080 qui empile). Son empreinte en unités du viewBox est donc la plus grande sur la
# plus PETITE scène : 240/477 × 1420 = 714 de large, 44/336 × 1000 = 131 de haut. La garde se
# calibre là (relecture de Mesure, 9/09) : une étiquette qui passe ici passe à toutes les tailles.
# Depuis le 9/09 (15h40) la chip est en POUR CENT de la scène (32,3 % de large, police en cqi) : son
# empreinte est la même en unités du viewBox à toutes les fenêtres, 240×44 px sur la scène de 744 px.
CHIP_DEMI = (round(240 / 744 * 1420 / 2), round(44 / (744 / 1.42) * 1000 / 2))   # (229, 42)
SEUIL_OBJET = 0.10             # part de pixels d'objet tolérée sous l'étiquette
_ALPHAS = {}


def alpha_webp(chemin):
    """(W, H, alpha) d'un webp, par dwebp (libwebp) ; mis en cache par chemin."""
    import subprocess
    chemin = str(chemin)
    if chemin in _ALPHAS:
        return _ALPHAS[chemin]
    try:
        brut = subprocess.run(["dwebp", chemin, "-pam", "-o", "-"], capture_output=True, check=True).stdout
    except FileNotFoundError:
        raise SystemExit("dwebp absent (brew install webp) : la garde des étiquettes ne peut pas lire l'alpha des états ; refus, pas de vert par absence")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"dwebp refuse {chemin} : {e.stderr.decode(errors='replace')[:200]}")
    fin = brut.index(b"ENDHDR\n") + 7
    tete = dict(l.split(" ", 1) for l in brut[:fin].decode().splitlines() if " " in l)
    W, H, prof = int(tete["WIDTH"]), int(tete["HEIGHT"]), int(tete["DEPTH"])
    px = brut[fin:]
    alpha = px[prof - 1::prof] if prof == 4 else bytes([255]) * (W * H)
    _ALPHAS[chemin] = (W, H, alpha)
    return _ALPHAS[chemin]


def etiquette_sur_objet(image, lx, ly, demi=CHIP_DEMI):
    """La part de pixels d'OBJET (alpha > 40) sous la boîte de l'étiquette centrée en (lx, ly),
    coordonnées relatives à l'image comme dans findings-*.json. Hors de l'image = du crème."""
    W, H, alpha = alpha_webp(image)
    cx, cy = MX_ANNOT + lx * IW_ANNOT, ly * 1000.0
    ex = W / IW_ANNOT
    x0, x1 = int((cx - demi[0] - MX_ANNOT) * ex), int((cx + demi[0] - MX_ANNOT) * ex)
    y0, y1 = int((cy - demi[1]) * H / 1000.0), int((cy + demi[1]) * H / 1000.0)
    total = max(1, (x1 - x0) * (y1 - y0))
    objet = 0
    for y in range(max(0, y0), min(H, y1)):
        ligne = alpha[y * W + max(0, x0): y * W + min(W, x1)]
        objet += sum(1 for a in ligne if a > 40)
    return objet / total


def etiquette_dans_scene(lx, ly, demi=CHIP_DEMI, tolerance=8):
    """La boîte de l'étiquette tient dans la scène (viewBox 1420×1000) : au-delà elle couvre le rail
    ou la fiche, et le lecteur perd l'un ou l'autre."""
    cx, cy = MX_ANNOT + lx * IW_ANNOT, ly * 1000.0
    return (cx - demi[0] >= -tolerance and cx + demi[0] <= 1420 + tolerance
            and cy - demi[1] >= -tolerance and cy + demi[1] <= 1000 + tolerance)


# La boîte d'une chip, en unités du viewBox, ESTIMÉE sur son texte : la chip est en monospace à
# 1,55 % de la largeur de scène (≈ 22 unités par em, ≈ 13,2 par caractère), padding .8em de chaque
# côté, plafonnée à 2 × CHIP_DEMI[0] de large (32,3 % de la scène) ; au-delà elle passe sur deux
# lignes. Une étiquette courte est donc plus étroite que la boîte maximale de la garde d'objet.
UNITES_PAR_CARACTERE = 13.2
def boite_etiquette(txt, demi=CHIP_DEMI):
    largeur = UNITES_PAR_CARACTERE * len(txt) + 36
    if largeur > 2 * demi[0]:
        return 2 * demi[0], 2 * demi[1]          # deux lignes : la boîte maximale
    return largeur, 50                           # une ligne


def etiquettes_qui_se_recouvrent(annotations, ecart=8):
    """Deux chips d'une MÊME scène ne doivent pas se recouvrir ni se toucher : le 9/09, sur le vert,
    « a pick both routings share » cachait la moitié de « name changes reader… » et la garde
    d'objet, qui juge chaque étiquette seule, laissait passer. Rend les paires fautives (a, b)
    d'indices dans la liste (ax, ay, lx, ly, txt), avec un écart minimal exigé entre les boîtes."""
    boites = []
    for (ax, ay, lx, ly, txt) in annotations:
        l, h = boite_etiquette(txt)
        boites.append((MX_ANNOT + lx * IW_ANNOT, ly * 1000.0, l, h))
    paires = []
    for a in range(len(boites)):
        for b in range(a + 1, len(boites)):
            xa, ya, la, ha = boites[a]
            xb, yb, lb, hb = boites[b]
            if abs(xa - xb) < (la + lb) / 2 + ecart and abs(ya - yb) < (ha + hb) / 2 + ecart:
                paires.append((a, b))
    return paires


def manques_etiquettes(outil_id, base, seuil=SEUIL_OBJET):
    """Chaque étiquette de findings-<outil>.json doit être sur le crème de SON image d'état."""
    base = pathlib.Path(base)
    chemin_f = base / f"findings-{outil_id}.json"
    if outil_id == "routing" or not chemin_f.exists():
        return []
    try:
        f = json.loads(chemin_f.read_text())
    except ValueError:
        return []
    findings = f["findings"] if isinstance(f, dict) and "findings" in f else f
    prefixe = ETATS_PREFIXE[outil_id]
    # La règle vaut pour les états CHORÉGRAPHIÉS (gros plans) : un plateau qui n'a pas encore ses
    # séquences garde ses états larges d'aujourd'hui, validés et en ligne, jusqu'à sa livraison ;
    # le juger maintenant ferait tomber trois blocs (et les liens du rideau) pour des étiquettes
    # que la livraison remplace de toute façon. Le manifeste est le signe de la livraison.
    if not (base / "rendus" / "sequences" / prefixe / "manifest.json").exists():
        return []
    m = []
    for i, fd in enumerate(findings if isinstance(findings, list) else []):
        image = base / "rendus" / "etats" / f"{prefixe}-0{i + 1}.webp"
        if not image.exists():
            continue
        for (ax, ay, lx, ly, txt) in fd.get("annotations", []):
            if not etiquette_dans_scene(lx, ly):
                m.append(f"findings-{outil_id}.json, finding {fd.get('num', i + 1)} : l'étiquette « {txt[:38]}… » "
                         "déborde de la scène (sur le rail ou la fiche) : la rentrer")
                continue
            part = etiquette_sur_objet(image, lx, ly)
            if part > seuil:
                m.append(f"findings-{outil_id}.json, finding {fd.get('num', i + 1)} : l'étiquette « {txt[:38]}… » "
                         f"couvre l'objet ({part:.0%} de pixels d'objet sous elle) : à poser sur le crème")
        annotations = fd.get("annotations", [])
        for (a, b) in etiquettes_qui_se_recouvrent(annotations):
            m.append(f"findings-{outil_id}.json, finding {fd.get('num', i + 1)} : les étiquettes « {annotations[a][4][:30]}… » "
                     f"et « {annotations[b][4][:30]}… » se recouvrent : les écarter")
    return m


# ── UNE SEULE BARRE, PARTOUT (Arslane, 11/09) ─────────────────────────────────────────────────
# La barre du site, identique sur toutes les pages : les cinq instruments dans l'ordre du rideau,
# Pricing, Contact ; l'outil courant marqué. Il a vu la version à deux niveaux (barre du site puis
# ligne de l'outil) et l'a refusée : « absolument partout qu'une seule barre ». Une fonction, huit
# en-têtes.
NAV_SITE = [(o["page_hero"], o["nom"]) for o in OUTILS.values()] + [("ENGAGEMENT.html", "Pricing"), ("CONTACT.html", "Contact")]


def barre_site(courant=None, racine="", nuit=True):
    """`racine` : « ../ » depuis un sous-dossier ; `courant` marque le lien du site (la page d'outil
    courante, Pricing ou Contact). L'empreinte n'est plus dans la barre (Arslane, 13/09 : « enlève
    le content hash en haut à droite ») : le pied la porte, une fois, sur chaque page."""
    nav = "".join(f'<a href="{racine + c}"' + (' aria-current="page"' if c == courant else "") + f'>{n}</a>'
                  for c, n in NAV_SITE)
    # « measured, then frozen » N'EST PLUS DANS LA BARRE (Arslane, 08/09 : « il n'a rien à
    # faire avec la barre d'accueil »). Il vit en bas à droite, dans le pied, où il était
    # déjà : la barre le répétait. Ce qui reste ici est l'empreinte, qui identifie la
    # version servie et n'a pas d'autre endroit. Sans empreinte, pas de span du tout : un
    # élément vide laisse sa gouttière et se voit.
    return (f'<header class="barre{" sur-nuit" if nuit else ""}">\n  <a class="marque" href="{racine}ACCUEIL.html">CRUSETRA</a>\n'
            f'  <nav aria-label="Site">{nav}</nav>\n'
            + '</header>')


CSS_BARRE_SITE = '''
  /* the current link, marked the same way on every page (the heroes had no rule, the instruments
     only brightened it, the house pages only weighted it) */
  /* marked by colour and a rule, never by weight : a bold link widens and shifts its neighbours
     from one page to the next (Arslane, 13/09 : « les titres changent de place et de taille ») */
  .barre nav a[aria-current]{color:var(--sur,var(--sur-vert,#e4ecdf));text-decoration:underline;
    text-decoration-thickness:1.5px;text-underline-offset:7px;text-decoration-color:currentColor}
  /* posée (beige), la barre gardait le lien courant en clair : illisible (relecture du 8/09).
     Il prend la couleur de titre de SA page : vert routing, rubis screening, lapis, améthyste, onyx. */
  .barre.posee nav a[aria-current]{color:var(--vert-titre,#23543f)}
  /* under 1080 px the bar leaves the fixed layer and takes its place in the flow, in the night
     colors, the seal on its own line ; no title hides under it, and the pages' top padding shrinks */
  @media (max-width:1080px){
    .barre{position:static;padding:12px 18px 8px;flex-wrap:wrap}
    html:not(.js) .barre{position:static}
    .barre.sur-nuit,.barre.sur-nuit.posee{background:var(--nuit-c,#0e1a15);box-shadow:none;backdrop-filter:none}
    .barre.sur-nuit .marque{color:var(--sur-vert,#e4ecdf)}
    .tete{padding-top:36px}.hero{padding-top:40px}
  }
''' + CSS_PIED_SITE
