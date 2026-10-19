#!/usr/bin/env python3
"""LE RAYONNAGE DES ARCHIVES, AUX VRAIS CHIFFRES : les cinq états du plateau améthyste.

  B=/Applications/Blender.app/Contents/MacOS/Blender
  "$B" -b -P rayonnage-etats.py -- --etat 3 --qualite apercu --sortie /tmp/rayonnage
  "$B" -b -P rayonnage-etats.py -- --etat 3 --qualite livraison --sortie /tmp/rayonnage
  python3 plumer.py --marge 40 /tmp/rayonnage/rayonnage-03.png ../rendus/etats/rayonnage-03.webp

La thèse (look-dev tranché par Arslane le 8/09 sur une planche de six formes :
equipe-cascade/amethyste/lookdev-amethyste.py, forme 5) : la salle des archives. Un rayonnage
de noyer à huit travées : sept FACTEURS de risque, et la huitième, la vôtre. Dans chaque
travée, les dossiers qu'un facteur sort au seuil commun : une pile de dossiers améthyste
(les clients escaladés qu'il retient, un dossier par client) et, dessus, une pile d'ivoire
(les clients maintenus qu'il alarme : les fausses alertes). D'un bord à l'autre, la tablette
de laiton du PLANCHER que la règle exige (recallFloor, lu dans src/assumptions.ts de
l'outil) : la pile améthyste d'une travée l'atteint quand la borne basse du rappel du
facteur atteint le plancher.

AUCUN CHIFFRE TAPÉ : chaque dossier de chaque pile est lu dans
~/Documents/cascade-scoring/releve-public.json (scellé, vérifié par outil.lire_releve_scelle) ;
le plancher est lu dans le code de l'outil. Sept mesures côte à côte, au seuil commun.
`--demo` n'existe QUE pour construire l'objet avant le relevé : il refuse d'écrire hors de
/tmp ou du scratchpad, et signe ses rendus d'un bandeau « DEMO ».

Les cinq états, un par finding (findings-scoring.json) :
  1  le facteur du finding 01 en avant (sa travée éclairée, sa pile tirée)
  2  le facteur du finding 02 en avant
  3  le plancher : la tablette de laiton vive, toutes les piles améthyste en dessous ;
     la meilleure travée en avant
  4  la même cellule, deux provenances : deux travées seules, cas écrits (dossiers épais)
     et variantes fabriquées (dossiers fins, plus nombreux), sous la même tablette
  5  votre historique : la huitième travée, une boîte d'archives d'ivoire posée dedans,
     vide de dossiers colorés (l'absence de mesure se voit)
Les états 1, 2, 3, 5 partagent LA MÊME caméra.
"""
import argparse
import math
import os
import pathlib
import random
import re
import sys

import bpy
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))          # source/ : outil.py
sys.path.insert(0, ICI)                           # etats/ : scene_commune.py
from outil import OUTILS, lire_releve_scelle      # noqa: E402
from scene_commune import Scene, matiere, boite, cylindre, boite_du_sujet  # noqa: E402, boite_des
from scene_commune import boite_des  # noqa: E402 — les cibles nommées (9/09)

DEPOT = str(OUTILS["scoring"]["outil_chemin"])   # depots.json / depots.local.json

ap = argparse.ArgumentParser()
ap.add_argument("--etat", type=int, required=True, choices=[1, 2, 3, 4, 5])
ap.add_argument("--sortie", default="/tmp/rayonnage")
ap.add_argument("--qualite", default="apercu", choices=["apercu", "livraison"])
ap.add_argument("--fond", default="ombre", choices=["papier", "ombre"])
ap.add_argument("--azimut", type=float, default=-74.0)
ap.add_argument("--elevation", type=float, default=12.0)
ap.add_argument("--seuil", default="0.50")
ap.add_argument("--frontiere", default="none", help="palier:seuil retenu par la règle ; « none » = aucune cellule ne tient")
ap.add_argument("--accents", default="geography,product",
                help="les facteurs des états 1 et 2 (findings 01 et 02 de findings-scoring.json : geography, product)")
ap.add_argument("--demo", action="store_true", help="jeu déclaré, pour construire l'objet avant le relevé ; jamais pour le site")
ap.add_argument("--releve", default=None, help="le relevé scellé à lire ; défaut : OUTILS['scoring']['releve'] (outil.py)")
from scene_commune import options_sequence, rendre_sequence  # noqa: E402 — avant l'analyse des options
options_sequence(ap)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

APERCU = args.qualite == "apercu"
LARGE, HAUT = (916, 747) if APERCU else (1374, 1120)

# ── LES DONNÉES : lues, scellées, jamais tapées (sauf --demo, qui le crie) ──────
if args.demo:
    if not (args.sortie.startswith("/tmp") or "/scratchpad" in args.sortie):
        sys.exit("--demo n'écrit que sous /tmp ou le scratchpad : un rendu DEMO ne va jamais dans rendus/")
    PALIERS = ["geography", "activity", "product", "exposure", "structure", "behaviour", "tenure"]
    _bas = [0.31, 0.44, 0.52, 0.66, 0.73, 0.84, 0.38]
    _ret = [16, 21, 24, 30, 33, 37, 19]
    _faux = [9, 12, 7, 3, 5, 8, 14]
    D = [dict(p=p, bas=b, retenus=r, faux=f, n_esc=42, n_main=42) for p, b, r, f in zip(PALIERS, _bas, _ret, _faux)]
    SYNT_MEILLEUR = dict(retenus=118, faux=27, n_esc=126, n_main=126, bas=0.96)
    PLANCHER = 0.90
    print("[rayonnage] DEMO : jeu déclaré, aucune valeur mesurée ; interdit sur le site", flush=True)
else:
    chemin_releve = args.releve or (OUTILS["scoring"]["releve"] if "scoring" in OUTILS else os.path.join(DEPOT, "releve-public.json"))
    RELEVE = lire_releve_scelle(os.path.expanduser(str(chemin_releve)))
    AUTH, SYNT = RELEVE["authored"], RELEVE["synthetic"]
    PALIERS = RELEVE["paliers"]["presents"]

    def cellule(table, palier, seuil):
        if seuil not in table["tables"][palier]:
            sys.exit(f"le relevé n'a pas de cellule {palier}@{seuil}")
        c = table["tables"][palier][seuil]
        return dict(retenus=c["rappel"]["succes"], faux=c["fauxPositifs"]["succes"], bas=c["rappel"]["bas"],
                    n_esc=table["nEscalated"], n_main=table["nMaintained"])

    D = [dict(p=p, **cellule(AUTH, p, args.seuil)) for p in PALIERS]
    src = pathlib.Path(DEPOT, "src", "assumptions.ts")
    m = re.search(r"^\s*recallFloor:\s*([0-9.]+)\s*,", src.read_text(), re.M) if src.exists() else None
    if not m:
        sys.exit(f"recallFloor introuvable dans {src} : le plancher ne se tape pas")
    PLANCHER = float(m.group(1))
    MEILLEUR_P = max(D, key=lambda d: d["bas"])["p"]
    SYNT_MEILLEUR = cellule(SYNT, MEILLEUR_P, args.seuil)

MEILLEUR = max(range(len(D)), key=lambda i: D[i]["bas"])
TIENNENT = [d["p"] for d in D if d["bas"] >= PLANCHER]
if args.frontiere == "none":
    FRONTIERE = None
    if TIENNENT:
        sys.exit(f"« none » demandé, mais {TIENNENT} tiennent le plancher {PLANCHER} : la frontière se donne, elle ne se cache pas")
else:
    pf, sf = args.frontiere.split(":")
    if sf != args.seuil or pf not in PALIERS or D[PALIERS.index(pf)]["bas"] < PLANCHER:
        sys.exit(f"la frontière {args.frontiere} n'est pas une cellule montrée qui tient le plancher")
    FRONTIERE = PALIERS.index(pf)
ACCENTS = args.accents.split(",")
for a in ACCENTS:
    if a not in PALIERS:
        sys.exit(f"facteur d'accent inconnu : {a}")
AVANT = {1: PALIERS.index(ACCENTS[0]), 2: PALIERS.index(ACCENTS[1]), 3: MEILLEUR, 4: None, 5: None}[args.etat]
for d in D:
    print(f"[rayonnage] {d['p']}@{args.seuil} : borne basse {d['bas']:.3f}, {d['retenus']}/{d['n_esc']} améthyste, {d['faux']}/{d['n_main']} ivoire", flush=True)
print(f"[rayonnage] plancher {PLANCHER} : {'aucun facteur ne le tient' if not TIENNENT else TIENNENT}", flush=True)


def matieres():
    return {
        "noyer":        matiere("m_noyer", "#4a3222", rugosite=0.6),
        "noyer_clair":  matiere("m_noyer_clair", "#7a5a3e", rugosite=0.55),       # la travée en avant
        "ardoise":      matiere("m_ardoise", "#23252a", rugosite=0.82),
        "laiton":       matiere("m_laiton", "#c9a24a", rugosite=0.44, metal=1.0),
        "laiton_vif":   matiere("m_laiton_vif", "#d8b15a", rugosite=0.4, metal=1.0, emission="#e0b455", force=1.4),
        "ivoire":       matiere("m_ivoire", "#ece5d2", rugosite=0.7),
        "ivoire_boite": matiere("m_ivoire_boite", "#f1ecdc", rugosite=0.85),
        "amethyste":    matiere("m_amethyste", "#5b34a3", rugosite=0.32, metal=0.1),
        "amethyste_poli": matiere("m_amethyste_poli", "#6a3fb5", rugosite=0.16, metal=0.2),
        "amethyste_demi": matiere("m_amethyste_demi", "#3f2a66", rugosite=0.4),
        "ivoire_demi":  matiere("m_ivoire_demi", "#bdb6a4", rugosite=0.75),
    }


# ── LE SUJET ─────────────────────────────────────────────────────────────────
N_TRAVEES = len(D) + 1
PAS = 0.58
L = PAS * N_TRAVEES + 0.16
P, H = 0.7, 2.05
E = 0.04                              # l'épaisseur d'un dossier écrit
E_FIN = 0.014                         # celle d'une variante fabriquée
Z_PLATEAU = 0.125


def meuble(M, longueur=L, n_travees=N_TRAVEES, hauteur=H):
    for s in (1, -1):
        boite(f"montant_{s}", (0.08, P, hauteur), (s * (longueur / 2 - 0.04), 0, hauteur / 2), M["noyer"], 0.006)
    boite("plateau_bas", (longueur, P, 0.05), (0, 0, 0.1), M["noyer"], 0.005)
    boite("plateau_haut", (longueur, P, 0.05), (0, 0, hauteur - 0.05), M["noyer"], 0.005)
    boite("fond", (longueur, 0.03, hauteur), (0, P / 2 - 0.015, hauteur / 2), M["ardoise"], 0.0)
    pas = (longueur - 0.16) / n_travees
    for i in range(1, n_travees):
        boite(f"cloison_{i}", (0.03, P, hauteur - 0.2), (-(longueur - 0.16) / 2 + i * pas, 0, hauteur / 2), M["noyer"], 0.003)
    return pas


def pile(nom, x, retenus, faux, M, e=E, demi=False, tiree=0.0, largeur=PAS - 0.16, graine=0):
    """Deux piles côte à côte dans la travée : DEVANT les dossiers améthyste (retenus), dont
    la hauteur se compare à la tablette du plancher ; DERRIÈRE les ivoire (fausses alertes),
    qui partent du même plateau : une fausse alerte ne fait jamais « monter » un facteur."""
    rnd = random.Random(graine)
    la, lf = largeur * 0.56, largeur * 0.38          # côte à côte dans la travée : améthyste à gauche, ivoire à droite
    xa, xf = x - largeur / 2 + la / 2, x + largeur / 2 - lf / 2
    z = Z_PLATEAU
    for k in range(retenus):
        mat = M["amethyste_demi"] if demi else (M["amethyste_poli"] if k % 4 == 0 else M["amethyste"])
        boite(f"{nom}_a_{k}", (la, P - 0.14, e * 0.9), (xa + rnd.uniform(-0.006, 0.006), 0.02 - tiree, z + e / 2), mat, 0.003)
        z += e
    z2 = Z_PLATEAU
    for k in range(faux):
        boite(f"{nom}_f_{k}", (lf, P - 0.2, e * 0.9), (xf + rnd.uniform(-0.006, 0.006), 0.0, z2 + e / 2),
              M["ivoire_demi"] if demi else M["ivoire"], 0.003)
        z2 += e
    return max(z, z2)


def tablette_plancher(M, longueur, vif=False):
    """La tablette de laiton du plancher : à la hauteur qu'une pile de dossiers écrits
    atteindrait si la borne basse valait le plancher (n_escalated × plancher dossiers)."""
    zp = Z_PLATEAU + PLANCHER * D[0]["n_esc"] * E
    boite("tablette", (longueur - 0.16, 0.06, 0.02), (0, -P / 2 - 0.02, zp), M["laiton_vif"] if vif else M["laiton"], 0.004)
    return zp


def rayonnage(M):
    pas = meuble(M)
    for i, d in enumerate(D):
        x = -(L - 0.16) / 2 + pas * (i + 0.5)
        avant = (AVANT == i)
        if avant:
            boite(f"eclairage_{i}", (pas - 0.06, 0.02, H - 0.3), (x, P / 2 - 0.04, H / 2), M["noyer_clair"], 0.0)
        # la hauteur : la BORNE BASSE en dossiers écrits, puis les fausses alertes comptées
        n_am = round(d["bas"] * d["n_esc"])
        pile(f"pile_{i}", x, n_am, d["faux"], M, demi=(AVANT is not None and not avant), tiree=0.16 if avant else 0.0, graine=10 + i)
    # la huitième travée : la vôtre
    x8 = -(L - 0.16) / 2 + pas * (len(D) + 0.5)
    if args.etat == 5:
        boite("boite_archives", (pas - 0.2, P - 0.2, 0.9), (x8, -0.02, Z_PLATEAU + 0.45), M["ivoire_boite"], 0.01)
        boite("etiquette", (pas - 0.36, 0.01, 0.16), (x8, -P / 2 + 0.11, Z_PLATEAU + 0.62), M["ivoire"], 0.002)
    tablette_plancher(M, L, vif=(args.etat == 3))


def deux_travees(M):
    """Finding 04 : la même cellule, deux provenances : à gauche les cas écrits (dossiers
    épais), à droite les variantes (dossiers fins, plus nombreux), sous la même tablette."""
    longueur = PAS * 2 + 0.16 + 0.4
    hauteur = H + 0.3
    pas = meuble(M, longueur, 2, hauteur)
    a = D[MEILLEUR]
    xa = -(longueur - 0.16) / 2 + pas * 0.5
    xs = -(longueur - 0.16) / 2 + pas * 1.5
    boite("eclairage_a", (pas - 0.06, 0.02, hauteur - 0.3), (xa, P / 2 - 0.04, hauteur / 2), M["noyer_clair"], 0.0)
    pile("ecrits", xa, round(a["bas"] * a["n_esc"]), a["faux"], M, largeur=pas - 0.16, graine=40)
    s = SYNT_MEILLEUR
    # l'épaisseur d'une variante : telle qu'une pile à la MÊME borne ait la MÊME hauteur
    # que la pile des cas écrits ; ce qui dépasse est la borne, pas le nombre
    e_fin = E * a["n_esc"] / s["n_esc"]
    pile("variantes", xs, round(s["bas"] * s["n_esc"]), s["faux"], M, e=e_fin, largeur=pas - 0.16, graine=41)
    tablette_plancher(M, longueur, vif=True)
    print(f"[rayonnage] état 4 : écrits borne {a['bas']:.3f} ({'tient' if a['bas'] >= PLANCHER else 'ne tient pas'}) ; "
          f"variantes borne {s['bas']:.3f} ({'tient' if s['bas'] >= PLANCHER else 'ne tient pas'})", flush=True)


scene = Scene(fond=args.fond, apercu=APERCU)
scene.table_rase()
scene.monde_hdri()
M = matieres()
if args.etat == 4:
    deux_travees(M)
    az, el = -80.0, 10.0
    cadre = boite_du_sujet()
else:
    rayonnage(M)
    az, el = args.azimut, args.elevation
    cadre = boite_du_sujet()
scene.lampe_cle()
scene.sol_papier(0.0)
OUVERTURE = 0.0 if APERCU else 9.0
# ── les cibles (9/09) : tout | travee:<palier> | tablette | archives ──
def boite_cible(nom):
    if nom == "tout" or args.etat == 4:
        return cadre
    # une travée se cadre par la GÉOMÉTRIE du meuble, pas par ses dossiers : la travée de geography
    # est vide (le facteur ne retient rien), et une boîte d'objets n'y désignerait rien
    pas_t = (L - 0.16) / N_TRAVEES
    def travee(i):
        x = -(L - 0.16) / 2 + pas_t * (i + 0.5)
        return (Vector((x - pas_t / 2 - 0.1, cadre[0].y - 0.3, -0.05)), Vector((x + pas_t / 2 + 0.1, cadre[1].y, H + 0.1)))
    if nom.startswith("travee:"):
        palier = nom.split(":", 1)[1]
        if palier not in PALIERS:
            sys.exit(f"[rayonnage] cible inconnue : {nom} (paliers : {', '.join(PALIERS)})")
        return travee(PALIERS.index(palier))
    if nom == "tablette":
        # la tablette sur trois travées (toute sa longueur ferait reculer la caméra)
        t = boite_des(["tablette"]); a, c = travee(0), travee(2)
        return (Vector((a[0].x, t[0].y - 0.3, t[0].z - 0.3)), Vector((c[1].x, cadre[1].y, t[1].z + 0.3)))
    if nom == "archives":
        return boite_des(["boite_archives", "etiquette"], air=(0.15, 0.3, 0.15))
    sys.exit(f"[rayonnage] cible inconnue : {nom}")
arrivee_boite = boite_cible(args.cible)
MARGE_ARRIVEE = 1.07 if args.cible == "tout" or args.etat == 4 else 1.0
if args.sequence:
    rendre_sequence(args, (az, el, MARGE_ARRIVEE),
                    lambda a, e, m, b: scene.camera(a, e, focale=60, marge=m, ouverture=OUVERTURE, boite=b),
                    lambda chemin: scene.rendre(chemin, LARGE, HAUT), "rayonnage",
                    boite_depart=boite_cible(args.cible_depart or args.cible), boite_arrivee=arrivee_boite)
else:
    scene.camera(az, el, focale=60, marge=MARGE_ARRIVEE, ouverture=OUVERTURE, boite=arrivee_boite)
    chemin = os.path.join(args.sortie, f"rayonnage-0{args.etat}.png")
    scene.rendre(chemin, LARGE, HAUT)
    print(f"[rayonnage] rendu → {chemin}\n[rayonnage] Le code de sortie 0 ne prouve rien : ouvrir l'image et la regarder.")
