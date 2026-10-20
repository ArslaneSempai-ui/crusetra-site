#!/usr/bin/env python3
"""L'ESCALIER DES CINQ CONTRÔLES, AUX VRAIS ÉTATS : les cinq états du plateau onyx.

  B=/Applications/Blender.app/Contents/MacOS/Blender
  "$B" -b -P escalier-etats.py -- --etat 3 --qualite apercu --sortie /tmp/escalier
  python3 plumer.py --marge 40 /tmp/escalier/escalier-03.png ../rendus/etats/escalier-03.webp

La thèse (look-dev tranché et retouché par Arslane le 8/09 : equipe-cascade/onyx/lookdev-onyx.py,
forme 2) : cinq marches d'onyx à nez de laiton, une par contrôle (present → sealed → signed →
fresh → consistent), le nom gravé sur chaque contremarche, la cinquième marche DORÉE ;
une rampe à balustres des deux côtés ; chaque QUESTION de la suite (routing, screening,
monitoring, scoring) pose son galet, à la couleur de son outil et marqué d'un sceau, sur
la marche de l'état qu'elle a atteint. À part, sur son propre piédestal, le LUTRIN où la
pièce est ouverte : deux pages d'ivoire, les quatre cachets aux couleurs des outils.

AUCUN ÉTAT TAPÉ : les états, les jours depuis chaque mesure et le rythme déclaré sont lus
dans ~/Documents/cascade-dossier/releve-public.json (scellé, vérifié par
outil.lire_releve_scelle) : `questions[outil] = { etat, joursDepuis, … }`, `reglages`.
`--demo` n'existe QUE pour construire l'objet avant le relevé : il refuse d'écrire hors de
/tmp ou du scratchpad.

Les cinq états, un par finding (findings-dossier.json) :
  1  la couverture : les quatre galets sur leurs marches
  2  le sceau : la deuxième marche en avant (arête vive), les cachets du lutrin en avant
  3  la signature : la troisième marche en avant
  4  la fraîcheur : chaque galet porte son anneau : laiton (fresh), ambre (due), rouge (stale)
  5  votre dossier : un galet d'ivoire au pied de l'escalier, sans marche encore
Les cinq états partagent LA MÊME caméra (boîte fixe : l'escalier et le lutrin).
"""
import argparse
import math
import os
import sys

import bpy
import mathutils as mu
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
sys.path.insert(0, ICI)
from outil import OUTILS, lire_releve_scelle      # noqa: E402
from scene_commune import Scene, matiere, matiere_pierre, boite, cylindre, tore, trace, pose, boite_du_sujet  # noqa: E402, boite_des
from scene_commune import boite_des  # noqa: E402 — les cibles nommées (9/09)

ap = argparse.ArgumentParser()
ap.add_argument("--etat", type=int, required=True, choices=[1, 2, 3, 4, 5])
ap.add_argument("--sortie", default="/tmp/escalier")
ap.add_argument("--qualite", default="apercu", choices=["apercu", "livraison"])
ap.add_argument("--fond", default="ombre", choices=["papier", "ombre"])
ap.add_argument("--azimut", type=float, default=-58.0)
ap.add_argument("--elevation", type=float, default=34.0)
ap.add_argument("--demo", action="store_true")
ap.add_argument("--releve", default=None, help="le relevé scellé à lire ; défaut : OUTILS['dossier']['releve'] (outil.py)")
from scene_commune import options_sequence, rendre_sequence  # noqa: E402 — avant l'analyse des options
options_sequence(ap)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

APERCU = args.qualite == "apercu"
LARGE, HAUT = (916, 747) if APERCU else (1374, 1120)
CONTROLES = ["present", "sealed", "signed", "fresh", "consistent"]
NOMS = ["PRESENT", "SEALED", "SIGNED", "FRESH", "CONSISTENT"]
COULEURS = {"routing": ("#1b3229", "#2e9065", "#57b184"), "screening": ("#33191f", "#8e1626", "#d64a5c"),
            "monitoring": ("#16213a", "#1d4189", "#4f8ae0"), "scoring": ("#241a3a", "#4a2a86", "#9b6fe0")}

if args.demo:
    if not (args.sortie.startswith("/tmp") or "/scratchpad" in args.sortie):
        sys.exit("--demo n'écrit que sous /tmp ou le scratchpad")
    QUESTIONS = [dict(q="routing", etat=5, jours=12), dict(q="screening", etat=5, jours=3),
                 dict(q="monitoring", etat=4, jours=1), dict(q="scoring", etat=1, jours=None)]
    RYTHME, STALE = 90, 2
    print("[escalier] DEMO : jeu déclaré, aucune valeur mesurée ; interdit sur le site", flush=True)
else:
    chemin_releve = args.releve or (OUTILS["dossier"]["releve"] if "dossier" in OUTILS else
                                    os.path.join(OUTILS["dossier"]["outil_chemin"], "releve-public.json"))
    R = lire_releve_scelle(os.path.expanduser(str(chemin_releve)))
    # le relevé du Dossier (lot D2) écrit l'état atteint par son NOM : « none » quand aucun
    # contrôle ne tient, sinon le plus haut tenu sans trou ; une question sans rapport n'a
    # pas d'état du tout. L'escalier compte les marches : none = 0, present = 1, … consistent = 5.
    ETATS = ["none"] + CONTROLES
    QUESTIONS = []
    for q, v in R["questions"].items():
        nom = v.get("etat", "none") if v.get("present") else "none"
        if nom not in ETATS:
            sys.exit(f"état inconnu dans le relevé pour {q} : {nom!r} (attendu : {ETATS})")
        QUESTIONS.append(dict(q=q, etat=ETATS.index(nom), jours=v.get("joursDepuis")))
    ORDRE = ["routing", "screening", "monitoring", "scoring"]        # l'ordre de la chaîne, pas celui du JSON
    QUESTIONS.sort(key=lambda d: ORDRE.index(d["q"]) if d["q"] in ORDRE else 99)
    RYTHME, STALE = int(R["reglages"]["rythmeJours"]), float(R["reglages"]["staleApres"])
for qd in QUESTIONS:
    if qd["q"] not in COULEURS:
        sys.exit(f"question inconnue du plateau : {qd['q']}")
    if not 0 <= qd["etat"] <= 5:
        sys.exit(f"état hors de 0..5 pour {qd['q']} : {qd['etat']}")
    print(f"[escalier] {qd['q']} : état {qd['etat']} ({CONTROLES[qd['etat'] - 1] if qd['etat'] else 'absent'}), jours {qd['jours']}", flush=True)


def fraicheur(jours):
    if jours is None:
        return None
    if jours < RYTHME:
        return "fresh"
    if jours < RYTHME * STALE:
        return "due"
    return "stale"


def matieres():
    M = {
        "onyx":        matiere_pierre("m_onyx", "#0b0b0e", "#141418", "#1f1f25", paillette=None, polie=True, echelle=40.0),
        "onyx_mat":    matiere("m_onyx_mat", "#141418", rugosite=0.55, metal=0.3),
        "laiton":      matiere("m_laiton", "#c9a24a", rugosite=0.44, metal=1.0),
        "laiton_vif":  matiere("m_laiton_vif", "#d8b15a", rugosite=0.4, metal=1.0, emission="#e0b455", force=1.2),
        "acier_sombre": matiere("m_acier_sombre", "#2b2d31", rugosite=0.48, metal=0.85),
        "ivoire":      matiere("m_ivoire", "#ece5d2", rugosite=0.7),
        "ivoire_papier": matiere("m_ivoire_papier", "#f1ecdc", rugosite=0.95),
        "stale":       matiere("m_stale", "#9a3b3b", rugosite=0.5, emission="#c04a4a", force=0.6),
        "due":         matiere("m_due", "#c9a24a", rugosite=0.5, emission="#e0b455", force=0.3),
    }
    for q, (sombre, moyen, vif) in COULEURS.items():
        M[f"pierre_{q}"] = matiere_pierre(f"m_pierre_{q}", sombre, moyen, vif, paillette=None, polie=True, echelle=80.0)
        M[f"cire_{q}"] = matiere(f"m_cire_{q}", moyen, rugosite=0.42, transmission=0.2)
        M[f"cire_vive_{q}"] = matiere(f"m_cire_vive_{q}", vif, rugosite=0.4, emission=vif, force=0.8)
    return M


def gravure(texte, pos, mat, taille=0.085, rot=(math.pi / 2, 0, 0), extrusion=0.006):
    bpy.ops.object.text_add(location=pos, rotation=rot)
    t = bpy.context.object
    t.data.body = texte
    t.data.size = taille
    t.data.extrude = extrusion
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.space_character = 1.15
    pose(t, mat)
    return t


L, PROF, MARCHE = 3.4, 0.62, 0.2
Y0 = PROF * 5 / 2


def escalier(M):
    for k in range(5):
        y_front = Y0 - PROF * (5 - k)
        avant = (args.etat in (2, 3) and k == args.etat - 1)
        boite(f"marche_{k}", (L, PROF * (5 - k), MARCHE), (0, Y0 - PROF * (5 - k) / 2, MARCHE / 2 + k * MARCHE),
              M["laiton"] if k == 4 else M["onyx"], 0.01)
        boite(f"nez_{k}", (L + 0.01, 0.035, 0.02), (0, y_front + 0.017, MARCHE * (k + 1) - 0.01),
              M["laiton_vif"] if avant else M["laiton"], 0.003)
        if avant:
            # la marche du finding : son giron entier en laiton vif, pas seulement le nez
            boite(f"giron_{k}", (L - 0.3, PROF - 0.08, 0.012), (0, y_front + PROF / 2, MARCHE * (k + 1) + 0.006), M["laiton_vif"], 0.002)
        gravure(NOMS[k], (0.0, y_front - 0.004, MARCHE * k + MARCHE * 0.5), M["ivoire"] if k < 4 else M["onyx_mat"])
    for s in (1, -1):
        sommets = []
        for k in range(5):
            y = Y0 - PROF * (5 - k) + PROF / 2
            z = MARCHE * (k + 1)
            xb = s * (L / 2 - 0.12)
            cylindre(f"balustre_{s}_{k}", 0.016, 0.5, (xb, y, z + 0.25), M["laiton"], verts=16, biseau=0.0)
            sommets.append((xb, y, z + 0.5))
        sommets = [(sommets[0][0], sommets[0][1] - 0.2, sommets[0][2])] + sommets + [(sommets[-1][0], sommets[-1][1] + 0.2, sommets[-1][2])]
        trace(f"main_courante_{s}", sommets, M["laiton"], rayon=0.026)
    pas = (L - 0.9) / (len(QUESTIONS) - 1)
    for i, qd in enumerate(QUESTIONS):
        x = -(L - 0.9) / 2 + i * pas
        k = qd["etat"] - 1
        if k < 0:
            cylindre(f"galet_{i}", 0.2, 0.08, (x, Y0 - PROF * 5 - 0.4, 0.04), M["onyx_mat"], verts=64, biseau=0.35)
            continue
        y = Y0 - PROF * (5 - k) + PROF / 2
        z = MARCHE * (k + 1)
        cylindre(f"galet_{i}", 0.2, 0.08, (x, y, z + 0.04), M[f"pierre_{qd['q']}"], verts=64, biseau=0.35)
        tore(f"sceau_{i}", 0.1, 0.008, (x, y, z + 0.082), M["laiton"])
        if args.etat == 4:
            f = fraicheur(qd["jours"])
            if f:
                tore(f"anneau_{i}", 0.29, 0.03, (x, y, z + 0.025), M["laiton_vif"] if f == "fresh" else M[f])
    if args.etat == 5:
        cylindre("votre", 0.2, 0.08, (0.0, Y0 - PROF * 5 - 0.75, 0.04), M["ivoire"], verts=64, biseau=0.35)
        tore("votre_sceau", 0.1, 0.008, (0.0, Y0 - PROF * 5 - 0.75, 0.082), M["laiton"])


def lutrin(M):
    xl, yl = L / 2 + 1.05, Y0 - PROF * 2.2
    boite("lutrin_socle", (0.9, 0.9, 0.36), (xl, yl, 0.18), M["onyx"], 0.012)
    boite("lutrin_socle_filet", (0.94, 0.94, 0.02), (xl, yl, 0.35), M["laiton"], 0.003)
    cylindre("lutrin_pied", 0.2, 0.03, (xl, yl, 0.375), M["laiton"], verts=48, biseau=0.05)
    cylindre("lutrin_fut", 0.04, 0.9, (xl, yl, 0.36 + 0.45), M["laiton"], verts=32, biseau=0.0)
    incl, tourne = math.radians(30), math.radians(-35)
    zt = 0.36 + 0.9
    rot = (incl, 0, tourne)
    Rm = mu.Euler(rot).to_matrix()

    def sur(u, v, w):
        p = Rm @ mu.Vector((u, v, w))
        return (xl + p.x, yl + p.y, zt + p.z)

    boite("pupitre", (1.0, 0.64, 0.03), (xl, yl, zt), M["onyx"], 0.006, rot=rot)
    boite("page_g", (0.44, 0.56, 0.012), sur(-0.24, 0.0, 0.022), M["ivoire_papier"], 0.002, rot=rot)
    boite("page_d", (0.44, 0.56, 0.012), sur(0.24, 0.0, 0.022), M["ivoire_papier"], 0.002, rot=rot)
    boite("reliure", (0.03, 0.58, 0.02), sur(0.0, 0.0, 0.026), M["onyx_mat"], 0.002, rot=rot)
    for i, qd in enumerate(QUESTIONS):
        v = 0.18 - i * 0.12
        # le cachet d'une question sans rapport reste une place vide ; à l'état 2 les cachets sont vifs
        if qd["etat"] >= 1:
            mat = M[f"cire_vive_{qd['q']}"] if args.etat == 2 else M[f"cire_{qd['q']}"]
            cylindre(f"cachet_{i}", 0.045, 0.014, sur(0.32, v, 0.036), mat, verts=32, rot=rot, biseau=0.2)
        else:
            tore(f"cachet_vide_{i}", 0.04, 0.005, sur(0.32, v, 0.03), M["onyx_mat"], rot=rot)
        boite(f"ligne_{i}", (0.18, 0.012, 0.004), sur(0.14, v, 0.03), M["onyx_mat"], 0.0, rot=rot)
    for k in range(5):
        boite(f"ligne_g_{k}", (0.3, 0.012, 0.004), sur(-0.24, 0.2 - k * 0.1, 0.03), M["onyx_mat"], 0.0, rot=rot)


def socle(M):
    boite("socle", (L + 2.0, PROF * 5 + 1.2, 0.12), (0.75, -0.3, -0.06), M["onyx_mat"], 0.015)
    boite("cercle_socle", (L + 2.04, PROF * 5 + 1.24, 0.02), (0.75, -0.3, -0.11), M["laiton"], 0.004)


scene = Scene(fond=args.fond, apercu=APERCU)
scene.table_rase()
scene.monde_hdri()
M = matieres()
escalier(M)
lutrin(M)
socle(M)
scene.lampe_cle()
scene.sol_papier(-0.12)
# la boîte commune : le socle porte tout, y compris la place du galet d'ivoire de l'état 5
OUVERTURE = 0.0 if APERCU else 9.0
BOITE = boite_du_sujet()
# ── les cibles (9/09) : tout | marche:<k> (0..4) | lutrin ──
def boite_cible(nom):
    if nom == "tout":
        return BOITE
    if nom.startswith("marche:"):
        k = int(nom.split(":", 1)[1])
        if not 0 <= k <= 4:
            sys.exit(f"[escalier] cible inconnue : {nom} (marches 0..4)")
        b = boite_des([f"marche_{k}", f"nez_{k}", f"giron_{k}"], air=(0.15, 0.2, 0.05))
        # les galets posés sur la marche : de l'air au-dessus
        return (b[0], Vector((b[1].x, b[1].y, b[1].z + 0.35)))
    if nom == "lutrin":
        return boite_des(["lutrin_", "pupitre", "page_", "reliure", "ligne_"], air=(0.2, 0.2, 0.15))
    if nom == "votre":
        # le galet d'ivoire au pied de l'escalier (état 5) : votre chaîne, pas encore mesurée
        return boite_des(["votre"], air=(0.35, 0.35, 0.3))
    sys.exit(f"[escalier] cible inconnue : {nom}")
arrivee_boite = boite_cible(args.cible)
MARGE_ARRIVEE = 1.07 if args.cible == "tout" else 1.0
if args.sequence:
    rendre_sequence(args, (args.azimut, args.elevation, MARGE_ARRIVEE),
                    lambda a, e, m, b: scene.camera(a, e, focale=60, marge=m, ouverture=OUVERTURE, boite=b),
                    lambda chemin: scene.rendre(chemin, LARGE, HAUT), "escalier",
                    boite_depart=boite_cible(args.cible_depart or args.cible), boite_arrivee=arrivee_boite)
else:
    scene.camera(args.azimut, args.elevation, focale=60, marge=MARGE_ARRIVEE, ouverture=OUVERTURE, boite=arrivee_boite)
    chemin = os.path.join(args.sortie, f"escalier-0{args.etat}.png")
    scene.rendre(chemin, LARGE, HAUT)
    print(f"[escalier] rendu → {chemin}\n[escalier] Le code de sortie 0 ne prouve rien : ouvrir l'image et la regarder.")
