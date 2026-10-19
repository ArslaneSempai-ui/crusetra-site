#!/usr/bin/env python3
"""LES BASSINS EN CASCADE, AUX VRAIS CHIFFRES : les cinq états du plateau lapis.

  B=/Applications/Blender.app/Contents/MacOS/Blender
  "$B" -b -P bassins-etats.py -- --etat 3 --qualite apercu --sortie /tmp/bassins
  "$B" -b -P bassins-etats.py -- --etat 3 --qualite livraison --sortie /tmp/bassins
  python3 plumer.py /tmp/bassins/bassins-03.png ../rendus/etats/bassins-03.webp

La thèse de l'objet (look-dev tranché par Arslane le 7/09 sur trois formes :
equipe-cascade/lapis/plateau-lookdev.py, forme B) : un SCÉNARIO est un bassin. Sept
bassins en terrasses ; chacun retient ce que son scénario retient, au seuil commun,
sur les 84 cas écrits du relevé public : un jeton lapis par vrai suspect retenu, un
jeton gris par fausse alerte retenue. Le déversoir de chaque bassin monte à la hauteur
de la BORNE BASSE DU RAPPEL de son scénario (ce qu'il retient à coup sûr) ; le plancher
que la règle de l'outil exige (recallFloor, lu dans src/assumptions.ts du bleu) est un
filet lapis poli au-dessus : un déversoir qui l'atteindrait serait retenu. Sur les cas
écrits, aucun ne l'atteint : le relevé le dit en toutes lettres, le plateau le montre.
Les bassins descendent dans l'ordre de leur borne basse : le plus haut retient le plus.

AUCUN CHIFFRE TAPÉ : chaque compte de jetons, chaque hauteur, est lu dans
~/Documents/cascade-monitoring/releve-public.json, dont le scellé est vérifié par
outil.lire_releve_scelle avant qu'un seul objet n'existe ; le plancher est lu dans le
code de l'outil. Le relevé mesure chaque cellule sur les 84 cas, indépendamment : la
cascade montre sept mesures côte à côte, pas une eau qui coulerait d'un bassin au
suivant.

Les cinq états, un par finding (findings-monitoring.json) :
  1  amount : le bassin du haut, presque tous les suspects, et la paie avec
  2  velocity : un compte n'est pas un signal (le bassin en cadre clair)
  3  le plancher : le filet lapis que personne n'atteint ; la borne la plus haute en
     cadre clair, et les suspects qu'elle manque au pied de la cascade
  4  la même cellule, deux provenances : deux bassins côte à côte, cas écrits (gros
     jetons) et variantes fabriquées (petits jetons), jamais mêlés ; le filet au-dessus
     des deux dit lequel des deux passerait le plancher
  5  votre historique : la cascade, et une feuille au pied avec des jetons pâles, non
     mesurés (l'absence de mesure se voit : rien n'est coloré à leur place)
Les états 1, 2, 3, 5 partagent LA MÊME caméra (cadrée une fois sur une boîte fixe).
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
from outil import OUTILS, lire_releve_scelle      # noqa: E402

SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "design-arslane")
HDRI = os.path.join(SKILL, "assets", "hdri")
DEPOT_BLEU = str(OUTILS["monitoring"]["outil_chemin"])   # depots.json / depots.local.json

ap = argparse.ArgumentParser()
ap.add_argument("--etat", type=int, required=True, choices=[1, 2, 3, 4, 5])
ap.add_argument("--sortie", default="/tmp/bassins")
ap.add_argument("--qualite", default="apercu", choices=["apercu", "livraison"])
ap.add_argument("--fond", default="ombre", choices=["papier", "ombre"])
ap.add_argument("--azimut", type=float, default=-48.0)
ap.add_argument("--elevation", type=float, default=34.0)
ap.add_argument("--seuil", default="0.50",
                help="le seuil commun des sept cellules montrées (une colonne du relevé)")
ap.add_argument("--frontiere", default="none",
                help="la cellule que la règle de l'outil retient, palier:seuil ; « none » = "
                     "ce que `npm run measure` a imprimé sur les cas écrits (aucune ne tient "
                     "le plancher). Une frontière donnée est REFUSÉE si sa cellule ne tient pas.")
ap.add_argument("--accents", default="amount,velocity",
                help="les scénarios des états 1 et 2 (findings 01 et 02), dans cet ordre")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

APERCU = args.qualite == "apercu"
LARGE, HAUT = (916, 747) if APERCU else (1374, 1120)      # le cadre des états verts et rouges
ECHANTILLONS = 32 if APERCU else 240
P_PAPIER = "#dbd7c5"

# ── LES DONNÉES : lues, scellées, jamais tapées ──────────────────────────────
CHEMIN_RELEVE = OUTILS.get("monitoring", {}).get("releve") or os.path.join(DEPOT_BLEU, "releve-public.json")
RELEVE = lire_releve_scelle(os.path.expanduser(CHEMIN_RELEVE))
AUTH = RELEVE["authored"]
SYNT = RELEVE["synthetic"]
SEUIL = args.seuil


def lire_plancher():
    """recallFloor, dans le code du bleu : l'hypothèse déclarée que la règle applique.
    Lu à la source, pas recopié : un plancher tapé ici parlerait pour deux dépôts."""
    src = pathlib.Path(DEPOT_BLEU, "src", "assumptions.ts")
    if not src.exists():
        sys.exit(f"{src} introuvable : le plancher se lit dans le code de l'outil, il ne se tape pas")
    m = re.search(r"^\s*recallFloor:\s*([0-9.]+)\s*,", src.read_text(), re.M)
    if not m:
        sys.exit(f"recallFloor introuvable dans {src} : rien ne se bâtit sur un plancher deviné")
    return float(m.group(1))


PLANCHER = lire_plancher()


def cellule(table, palier, seuil):
    if seuil not in table["tables"][palier]:
        sys.exit(f"le relevé n'a pas de cellule {palier}@{seuil} : la colonne se choisit parmi les siennes")
    c = table["tables"][palier][seuil]
    return c["rappel"]["succes"], c["fauxPositifs"]["succes"], c["rappel"]["bas"]


PALIERS = RELEVE["paliers"]["presents"]
# du bassin qui retient le plus (haut) à celui qui retient le moins (bas) : la borne
# basse du rappel ordonne les terrasses ; l'ordre est LU, pas écrit
ORDRE = sorted(PALIERS, key=lambda p: -cellule(AUTH, p, SEUIL)[2])
COMPTES = [cellule(AUTH, p, SEUIL) for p in ORDRE]           # (lapis, gris, borne basse) par bassin
MEILLEUR = ORDRE[0]
TIENNENT = [p for p, (_, _, bas) in zip(ORDRE, COMPTES) if bas >= PLANCHER]

if args.frontiere == "none":
    I_FRONTIERE = None
    if TIENNENT:
        sys.exit(f"« none » demandé, mais {TIENNENT} tiennent le plancher {PLANCHER} au seuil {SEUIL} : "
                 "la frontière se donne, elle ne se cache pas")
else:
    palier_f, seuil_f = args.frontiere.split(":")
    if seuil_f != SEUIL:
        sys.exit(f"la frontière {args.frontiere} n'est pas dans la colonne montrée ({SEUIL})")
    if cellule(AUTH, palier_f, seuil_f)[2] < PLANCHER:
        sys.exit(f"la frontière {args.frontiere} ne tient pas le plancher {PLANCHER} : "
                 "la règle de l'outil ne la retiendrait pas, le plateau non plus")
    I_FRONTIERE = ORDRE.index(palier_f)

ACCENTS = args.accents.split(",")
for a in ACCENTS:
    if a not in ORDRE:
        sys.exit(f"scénario d'accent inconnu du relevé : {a}")
I_ACCENT = {1: ORDRE.index(ACCENTS[0]), 2: ORDRE.index(ACCENTS[1]), 3: 0, 4: None, 5: None}[args.etat]
LAPIS_MEILLEUR, _, BAS_MEILLEUR = COMPTES[0]
RATES = AUTH["nSuspicious"] - LAPIS_MEILLEUR                # les suspects que la meilleure borne manque

for p, (lapis, gris, bas) in zip(ORDRE, COMPTES):
    print(f"[bassins] {p}@{SEUIL} : {lapis} lapis / {AUTH['nSuspicious']}, {gris} gris / {AUTH['nBenign']}, "
          f"borne basse {bas:.3f}", flush=True)
print(f"[bassins] plancher {PLANCHER} : {'aucun scénario ne le tient' if not TIENNENT else TIENNENT} ; "
      f"la meilleure borne ({MEILLEUR}) manque {RATES} suspects", flush=True)


# ── outils de scène (ceux du look-dev lapis, éprouvés dans Blender 5.2) ──────
def srgb(hexa):
    h = hexa.lstrip("#")
    out = []
    for k in (0, 2, 4):
        c = int(h[k:k + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def table_rase():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.samples = ECHANTILLONS
    c.use_denoising = True
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.006
    c.transmission_bounces = 4
    c.diffuse_bounces = 2
    c.glossy_bounces = 4
    c.max_bounces = 8
    c.sample_clamp_indirect = 10.0
    try:
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "METAL"
        c.device = "GPU"
    except Exception:
        c.device = "CPU"
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    sc.view_settings.look = "None"


def matiere(nom, base, rugosite=0.4, metal=0.0, transmission=0.0, ior=1.33, alpha=1.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
        p.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
    return m


def pose(obj, mat):
    obj.data.materials.append(mat)
    return obj


def monde_hdri(fichier, force=1.0, rotation=0.0):
    chemin = os.path.join(HDRI, fichier)
    if not os.path.exists(chemin):
        sys.exit(f"HDRI absent : {chemin}")
    w = bpy.data.worlds.new("monde")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    sortie = nt.nodes.new("ShaderNodeOutputWorld")
    fond = nt.nodes.new("ShaderNodeBackground")
    fond.inputs["Strength"].default_value = force
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(chemin)
    map_ = nt.nodes.new("ShaderNodeMapping")
    map_.inputs["Rotation"].default_value[2] = rotation
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Generated"], map_.inputs["Vector"])
    nt.links.new(map_.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], fond.inputs["Color"])
    if args.fond == "ombre":
        nt.links.new(fond.outputs["Background"], sortie.inputs["Surface"])
        bpy.context.scene.render.film_transparent = True
        return
    fond_uni = nt.nodes.new("ShaderNodeBackground")
    fond_uni.inputs["Color"].default_value = (*srgb(P_PAPIER), 1)
    chemin_l = nt.nodes.new("ShaderNodeLightPath")
    melange = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(chemin_l.outputs["Is Camera Ray"], melange.inputs["Fac"])
    nt.links.new(fond.outputs["Background"], melange.inputs[1])
    nt.links.new(fond_uni.outputs["Background"], melange.inputs[2])
    nt.links.new(melange.outputs["Shader"], sortie.inputs["Surface"])


def sol_papier(z):
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, z - 0.002))
    o = bpy.context.object
    o.name = "sol_papier"
    pose(o, matiere("m_papier", srgb(P_PAPIER), rugosite=0.94))
    if args.fond == "ombre":
        o.is_shadow_catcher = True


def boite_du_sujet():
    mn, mx = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.name.startswith("sol"):
            continue
        for coin in o.bound_box:
            p = o.matrix_world @ Vector(coin)
            mn = Vector((min(mn[i], p[i]) for i in range(3)))
            mx = Vector((max(mx[i], p[i]) for i in range(3)))
    return mn, mx


def camera(position, boite, focale=72, ouverture=0.0, marge=1.12):
    """Cadrée sur une boîte DONNÉE (pas sur ce qui est dans la scène) : les quatre
    états de la cascade partagent la boîte, donc la caméra."""
    from bpy_extras.object_utils import world_to_camera_view
    mn, mx = boite
    centre = (mn + mx) / 2
    cam = bpy.data.cameras.new("cam")
    cam.lens = focale
    if ouverture:
        cam.dof.use_dof = True
        cam.dof.focus_distance = (Vector(position) - centre).length
        cam.dof.aperture_fstop = ouverture
    o = bpy.data.objects.new("cam", cam)
    bpy.context.collection.objects.link(o)
    o.location = Vector(position)
    bpy.context.scene.camera = o
    direction = centre - Vector(position)
    o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    axe = -direction.normalized()
    coins = [Vector((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    for _ in range(160):
        bpy.context.view_layer.update()
        uv = [world_to_camera_view(bpy.context.scene, o, p) for p in coins]
        u = max(max(abs(v.x - .5), abs(v.y - .5)) * 2 for v in uv)
        if u * marge <= 1.0:
            break
        o.location = Vector(o.location) + axe * 0.20
        if ouverture:
            cam.dof.focus_distance = (Vector(o.location) - centre).length
    return o


def chanfrein(o, part=0.010, n=2, plancher=0.006):
    bpy.context.view_layer.update()
    petit = min(d for d in o.dimensions if d > 1e-6)
    m = o.modifiers.new("chanfrein", "BEVEL")
    m.width, m.segments = max(plancher, petit * part), n
    m.harden_normals = True
    bpy.ops.object.shade_smooth()
    return o


def boite(nom, dims, pos, mat, biseau=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object
    o.name = nom
    o.scale = dims
    pose(o, mat)
    bpy.ops.object.transform_apply(scale=True)
    chanfrein(o, biseau)
    return o


def cylindre(nom, r, h, pos, mat, verts=64, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=pos, rotation=rot)
    o = bpy.context.object
    o.name = nom
    pose(o, mat)
    chanfrein(o, 0.02)
    return o


# ── LA PALETTE : celle du plateau vert, le lapis à la place du vert ──────────
def matieres():
    return {
        "cadre":       matiere("m_cadre", srgb("#8a8378"), rugosite=0.62, metal=0.18),
        "lapis_poli":  matiere("m_lapis_poli", srgb("#1d4189"), rugosite=0.14, metal=0.62),
        "lapis":       matiere("m_lapis", srgb("#16346f"), rugosite=0.30, metal=0.70),
        "gris":        matiere("m_gris", srgb("#9aa2ad"), rugosite=0.26, metal=0.88),
        "gris_poli":   matiere("m_gris_poli", srgb("#b9c1cc"), rugosite=0.11, metal=0.92),
        "acier":       matiere("m_acier", srgb("#6f727a"), rugosite=0.40, metal=0.80),
        # l'eau : plus claire et moins miroir que celle du look-dev, qui renvoyait le ciel
        # sombre du HDRI et noyait les jetons lapis dans du gris
        "eau":         matiere("m_eau", srgb("#c9dcf2"), rugosite=0.12, transmission=0.5, ior=1.33, alpha=0.62),
        "beton":       matiere("m_beton", srgb("#b5b0a3"), rugosite=0.85),
        "beton_clair": matiere("m_beton_clair", srgb("#efe9db"), rugosite=0.75),   # le bassin du finding : éclairé
        "papier":      matiere("m_feuille", srgb("#efe9d8"), rugosite=0.9),
        "inconnu":     matiere("m_inconnu", srgb("#cfc9bb"), rugosite=0.7, metal=0.1),  # non mesuré : pâle
    }


# ── LE SUJET ─────────────────────────────────────────────────────────────────
N = len(ORDRE)
W, D = 4.6, 1.55                 # largeur, profondeur d'un bassin : 84 jetons doivent tenir
MARCHE = 0.34                    # la chute entre deux terrasses
JETON_R, JETON_E = 0.085, 0.045  # un cas écrit
PETIT_R, PETIT_E = 0.05, 0.03    # une variante fabriquée : plus petite, à part
H_DEVERSOIR = 0.55               # la hauteur d'un déversoir qui retiendrait tout (borne basse 1,0)
SOCLE = 0.30


def hauteur(bas):
    return 0.10 + bas * H_DEVERSOIR


def semer(centre, n_lapis, n_gris, M, graine, rayon_x, rayon_y, z, r=JETON_R, e=JETON_E):
    """Des jetons posés sans se chevaucher dans un rectangle, lapis d'abord ; refuse
    de tricher si le bassin est trop petit (un jeton caché serait un cas caché)."""
    rnd = random.Random(graine)
    places = []
    pas = r * 2.3
    nx, ny = int(rayon_x * 2 / pas), int(rayon_y * 2 / pas)
    for i in range(nx):
        for j in range(ny):
            x = -rayon_x + pas / 2 + i * pas + rnd.uniform(-0.02, 0.02)
            y = -rayon_y + pas / 2 + j * pas + rnd.uniform(-0.02, 0.02)
            places.append((x, y))
    rnd.shuffle(places)
    if len(places) < n_lapis + n_gris:
        sys.exit(f"bassin trop petit : {n_lapis + n_gris} jetons pour {len(places)} places")
    for k in range(n_lapis + n_gris):
        x, y = places[k]
        m = M["lapis_poli" if k % 3 == 0 else "lapis"] if k < n_lapis else M["gris" if k % 3 == 0 else "gris_poli"]
        cylindre("jeton", r, e, (centre[0] + x, centre[1] + y, z + e / 2), m, verts=32)


def bassin(i, x, y, z0, lapis, gris, bas, M, accent=False, frontiere=False, filet=False,
           r=JETON_R, e=JETON_E, graine=200):
    """Un bassin : la cuve, l'eau, le déversoir à la hauteur de la borne basse, les
    jetons retenus ; le filet lapis poli au-dessus du déversoir = le plancher exigé."""
    boite(f"bassin_{i}", (W, D, 0.22), (x, y, z0 + 0.11), M["beton_clair"] if accent else M["beton"], 0.01)
    boite(f"eau_{i}", (W - 0.3, D - 0.3, 0.06), (x, y, z0 + 0.25), M["eau"], 0.004)
    h = hauteur(bas)
    y_d = y - D / 2 + 0.15
    boite(f"deversoir_{i}", (W - 0.3, 0.07, h), (x, y_d, z0 + 0.22 + h / 2),
          M["lapis_poli"] if frontiere else M["acier"], 0.006)
    if filet:
        # le filet flotte au-dessus de l'EAU, en retrait du déversoir : un niveau à
        # atteindre, pas une rallonge du mur (collé au mur, il se lisait comme un mur plus haut)
        hp = hauteur(PLANCHER)
        y_f = y_d + 0.22
        boite(f"plancher_{i}", (W - 0.3, 0.03, 0.03), (x, y_f, z0 + 0.22 + hp), M["lapis_poli"], 0.004)
        for s in (1, -1):   # deux montants fins qui le tiennent : il flotte, il n'est pas posé
            cylindre(f"montant_{i}_{s}", 0.016, hp, (x + s * (W / 2 - 0.15), y_f, z0 + 0.22 + hp / 2),
                     M["acier"], verts=16)
    semer((x, y + 0.10), lapis, gris, M, graine + i, rayon_x=W * 0.44, rayon_y=D * 0.34, z=z0 + 0.28, r=r, e=e)


def cascade(M, accent=None, filet=False):
    for i, (p, (lapis, gris, bas)) in enumerate(zip(ORDRE, COMPTES)):
        bassin(i, 0, -i * D, (N - 1 - i) * MARCHE, lapis, gris, bas, M,
               accent=(accent is not None and i == accent), frontiere=(I_FRONTIERE == i), filet=filet)
    boite("socle", (W + 1.0, N * D + 1.0, SOCLE), (0, -(N - 1) * D / 2, -SOCLE / 2), M["cadre"], 0.012)


def rates_au_pied(M):
    """Les suspects que la meilleure borne manque : au pied de la cascade, devant le
    dernier bassin, à gauche (la feuille de l'état 5 occupe la droite)."""
    y0 = -(N - 1) * D - D / 2 - 0.28          # sur le socle, juste devant le dernier bassin
    for k in range(RATES):
        cylindre("rate", JETON_R, JETON_E, (-W / 2 + 0.45 + k * 0.30, y0 - (k % 2) * 0.22, JETON_E / 2), M["lapis"], verts=32)


def feuille(M):
    """L'export du client, au pied : une feuille, et dessus des jetons qui n'ont pas de
    couleur parce qu'ils n'ont pas de mesure."""
    y0 = -(N - 1) * D - D / 2 - 1.05
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.9, y0, 0.011))
    f = bpy.context.object
    f.name = "feuille"
    f.scale = (2.3, 1.55, 0.022)
    f.rotation_euler[2] = math.radians(-9)
    pose(f, M["papier"])
    rnd = random.Random(7)
    for k in range(10):
        gx, gy = (k % 5 - 2) * 0.40, (k // 5 - 0.5) * 0.50
        x, y = 0.9 + gx + rnd.uniform(-0.05, 0.05), y0 + gy + rnd.uniform(-0.05, 0.05)
        cylindre("inconnu", JETON_R, JETON_E, (x, y, 0.022 + JETON_E / 2), M["inconnu"], verts=32)


def deux_bassins(M):
    """Finding 04 : la MÊME cellule (la meilleure borne), deux provenances côte à côte.
    À gauche les cas écrits, gros jetons ; à droite les variantes fabriquées, petits
    jetons : jamais mêlés. Le filet du plancher au-dessus des deux : la borne des
    variantes le passe, celle des cas écrits non, et c'est tout le finding."""
    ecart = W / 2 + 0.55
    for x, table, r, e, graine in ((-ecart, AUTH, JETON_R, JETON_E, 300), (+ecart, SYNT, PETIT_R, PETIT_E, 301)):
        lapis, gris, bas = cellule(table, MEILLEUR, SEUIL)
        bassin(int(x > 0), x, 0, 0, lapis, gris, bas, M, accent=(x < 0), filet=True, r=r, e=e, graine=graine)
        boite(f"socle_{int(x > 0)}", (W + 0.6, D + 0.8, SOCLE * 0.8), (x, 0, -SOCLE * 0.4), M["cadre"], 0.012)
        print(f"[bassins] état 4, {table.get('provenance', 'table')} x={x:+.1f} : {lapis} lapis, {gris} gris, "
              f"borne basse {bas:.3f} ({'tient' if bas >= PLANCHER else 'ne tient pas'} le plancher)", flush=True)


def rendre():
    table_rase()
    monde_hdri("contraste.hdr", force=1.15, rotation=math.pi * 0.35)
    M = matieres()
    r = 12.0
    # les deux bassins de l'état 4 sont côte à côte sur x : vus presque de face, plus haut,
    # pour que la paire se lise comme une paire et que leur contenu se compte
    az = math.radians(args.azimut if args.etat != 4 else -80.0)
    el = math.radians(args.elevation if args.etat != 4 else 48.0)   # assez haut pour voir derrière le déversoir
    position = (math.cos(el) * math.cos(az) * r, math.cos(el) * math.sin(az) * r, math.sin(el) * r)
    if args.etat == 4:
        deux_bassins(M)
        cadre = boite_du_sujet()
    else:
        cascade(M, accent=I_ACCENT, filet=(args.etat == 3))
        # la boîte COMMUNE : la cascade, plus la place du pied (ratés de l'état 3, feuille
        # de l'état 5) et celle du filet de l'état 3, pour une seule caméra
        mn, mx = boite_du_sujet()
        cadre = (Vector((mn.x, mn.y - 1.95, mn.z)), Vector((mx.x, mx.y, max(mx.z, (N - 1) * MARCHE + 0.22 + hauteur(PLANCHER) + 0.05))))
        if args.etat == 3:
            rates_au_pied(M)
        if args.etat == 5:
            feuille(M)
    sol_papier(-SOCLE if args.etat != 4 else -SOCLE * 0.8)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = LARGE, HAUT
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.film_transparent = (args.fond != "papier")
    os.makedirs(args.sortie, exist_ok=True)
    # marge 1.17 : plumer.py refuse un objet opaque dans ses 90 px de bord, et le socle
    # de la cascade remplit la boîte en largeur (à 1.08, 30 px d'objet dans la marge : refusé)
    camera(position, cadre, focale=72, ouverture=0.0 if APERCU else 11.0, marge=1.17)
    sc.render.filepath = os.path.join(args.sortie, f"bassins-0{args.etat}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[bassins] rendu → {sc.render.filepath}\n[bassins] Le code de sortie 0 ne prouve rien : ouvrir l'image et la regarder.")


rendre()
