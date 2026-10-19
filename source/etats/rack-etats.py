#!/usr/bin/env python3
"""LE RACK DE SURVEILLANCE, AUX VRAIS CHIFFRES : les cinq états du plateau lapis.

  B=/Applications/Blender.app/Contents/MacOS/Blender
  "$B" -b -P rack-etats.py -- --etat 3 --qualite apercu --sortie /tmp/rack
  "$B" -b -P rack-etats.py -- --etat 3 --qualite livraison --sortie /tmp/rack
  python3 plumer.py /tmp/rack/rack-03.png ../rendus/etats/rack-03.webp

La thèse de l'objet (look-dev 2 tranché par Arslane le 8/09 sur une planche de six
formes, après le refus des bassins : equipe-cascade/lapis/lookdev2.py, forme 4) : le
plateau du bleu est LE PUPITRE DE SURVEILLANCE LUI-MÊME. Un châssis noir anodisé, huit
lames : sept scénarios et, la huitième, la vôtre. Sur chaque lame de scénario : une barre
lumineuse qui monte à la BORNE BASSE du rappel (ce qu'il retient à coup sûr, au seuil
commun), une matrice de diodes lapis (les 42 suspects écrits : allumée = retenu) et une
matrice d'ambre (les 42 sosies bénins : allumée = fausse alerte). D'un bord à l'autre,
gravée et remplie de laiton, la ligne du PLANCHER que la règle de l'outil exige (lu dans
src/assumptions.ts du bleu) : aucune barre ne l'atteint sur les cas écrits, et le relevé
le dit en toutes lettres.

AUCUN CHIFFRE TAPÉ : chaque diode, chaque hauteur de barre, est lue dans
~/Documents/cascade-monitoring/releve-public.json, dont le scellé est vérifié par
outil.lire_releve_scelle avant qu'un seul objet n'existe ; le plancher est lu dans le
code de l'outil. Sept mesures côte à côte, indépendantes, au seuil commun.

Les cinq états, un par finding (findings-monitoring.json) :
  1  amount : la lame du montant nu en avant (barre presque au plancher, matrice lapis
     presque pleine, sept diodes d'ambre : les achats expliqués)
  2  velocity : la lame du compte en avant (barre basse, la moitié des ambres allumées :
     la paie, la saison, l'épargne)
  3  le plancher : la ligne de laiton en avant, toutes les barres en dessous ; la meilleure
     (amount) en avant, ses deux diodes éteintes = les deux suspects qu'elle manque
  4  la même cellule, deux provenances : deux lames seules côte à côte, cas écrits (42
     diodes) et variantes fabriquées (126 diodes, plus petites), sous la même ligne :
     seule la barre des variantes la passe
  5  votre historique : la huitième lame, tirée du châssis, éteinte, une fiche d'ivoire
     glissée dedans (l'absence de mesure se voit : rien n'est allumé à sa place)
Les états 1, 2, 3, 5 partagent LA MÊME caméra (cadrée une fois sur une boîte fixe) ;
« en avant » = la lame éclairée à plein, les autres à demi.
"""
import argparse
import math
import os
import pathlib
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
ap.add_argument("--sortie", default="/tmp/rack")
ap.add_argument("--qualite", default="apercu", choices=["apercu", "livraison"])
ap.add_argument("--fond", default="ombre", choices=["papier", "ombre"])
# la façade des lames est en −y : la caméra se place DEVANT (azimut vers −90°), un peu
# à droite, pour lire les huit lames et non le flanc du châssis (à −22° on voyait le bout)
ap.add_argument("--azimut", type=float, default=-68.0)
ap.add_argument("--elevation", type=float, default=16.0)
ap.add_argument("--seuil", default="0.50", help="le seuil commun des sept cellules montrées")
ap.add_argument("--frontiere", default="none",
                help="la cellule que la règle de l'outil retient, palier:seuil ; « none » = ce que "
                     "`npm run measure` a imprimé (aucune ne tient le plancher). REFUSÉE si sa cellule ne tient pas.")
ap.add_argument("--accents", default="amount,velocity", help="les scénarios des états 1 et 2 (findings 01 et 02)")
# LA CHORÉGRAPHIE AU SCROLL (lot du 9/09, tranché par Arslane : séquence pré-rendue, scrubbée) :
# N images d'UNE transition de caméra, de --depart "azimut,elevation,marge" à la caméra de
# l'état demandé, adoucie aux deux bouts ; la dernière image EST le cadrage de l'état
# (les annotations posées sur l'état restent justes à l'arrivée). Sans --sequence : une image.
ap.add_argument("--sequence", type=int, default=0, help="nombre d'images de la transition ; 0 = l'état seul")
ap.add_argument("--depart", default="-20,34,1.45", help="caméra de départ de la transition : azimut,elevation,marge")
ap.add_argument("--via", default="", help="point de contrôle (azimut,elevation,marge) : la caméra s'en approche à mi-course "
                "(Bézier quadratique) — pour un aller-retour quand l'état d'arrivée garde la caméra du départ")
# LES CIBLES (tranché par Arslane le 9/09, 04h15 : « des travellings vers des parties de l'outil,
# avec les explications ») : la caméra se cadre sur la boîte d'UNE pièce, pas sur le rack entier.
#   tout            le rack entier (le cadrage historique)
#   lame:<scenario> une lame (amount, velocity, …) ; lame:8 = la vôtre, tirée à l'état 5
#   ligne           la ligne de laiton du plancher, sur toute la longueur
# La transition interpole la boîte du départ vers celle de l'arrivée : le travelling glisse
# d'une pièce à l'autre au lieu de tourner autour du tout.
ap.add_argument("--cible", default="tout", help="la pièce cadrée à l'arrivée (l'état) : tout | lame:<scenario> | lame:8 | ligne")
ap.add_argument("--cible-depart", default="", help="la pièce cadrée au départ de la transition ; défaut : la cible d'arrivée")
# LE COÛT (Arslane, 9/09 : « on a pas moyen de faire ça plus rapidement ? ») : les images de passage
# ne sont vues qu'en mouvement ; on peut les rendre avec moins d'échantillons et plus petites que
# l'état où l'on s'arrête. Ces deux réglages surchargent la qualité choisie, pour MESURER.
ap.add_argument("--echantillons", type=int, default=0, help="échantillons Cycles ; 0 = ceux de la qualité (48 aperçu, 256 livraison)")
ap.add_argument("--large", type=int, default=0, help="largeur de l'image ; 0 = celle de la qualité (916 aperçu, 1374 livraison)")
ap.add_argument("--echantillons-arrivee", type=int, default=0, help="échantillons de la DERNIÈRE image (l'état, où l'on s'arrête) ; 0 = comme les autres")
# LE CHANGEMENT DE FINDING SANS SAUT : à la coupe entre deux états, la lame qui était sortie rentre et
# la suivante sort d'un coup (vu sur la planche du 9/09). --avant-depart <scenario> : cette lame part
# sortie et rentre pendant les premiers 40 % des images, tandis que la lame en avant de l'état sort.
ap.add_argument("--avant-depart", default="", help="le scénario dont la lame était sortie à l'état précédent (glisse pendant la transition)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

APERCU = args.qualite == "apercu"
LARGE, HAUT = (916, 747) if APERCU else (1374, 1120)      # le cadre des états verts et rouges
if args.large:
    LARGE, HAUT = args.large, round(args.large * 1120 / 1374)
ECHANTILLONS = args.echantillons or (48 if APERCU else 256)
P_PAPIER = "#dbd7c5"

# ── LES DONNÉES : lues, scellées, jamais tapées ──────────────────────────────
RELEVE = lire_releve_scelle(os.path.expanduser(str(OUTILS["monitoring"]["releve"])))
AUTH = RELEVE["authored"]
SYNT = RELEVE["synthetic"]
SEUIL = args.seuil


def lire_plancher():
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
        sys.exit(f"le relevé n'a pas de cellule {palier}@{seuil}")
    c = table["tables"][palier][seuil]
    return dict(lapis=c["rappel"]["succes"], gris=c["fauxPositifs"]["succes"], bas=c["rappel"]["bas"],
                n_susp=table["nSuspicious"], n_ben=table["nBenign"])


PALIERS = RELEVE["paliers"]["presents"]           # l'ordre du registre de l'outil, lu
D = [dict(p=p, **cellule(AUTH, p, SEUIL)) for p in PALIERS]
MEILLEUR = max(D, key=lambda d: d["bas"])["p"]
TIENNENT = [d["p"] for d in D if d["bas"] >= PLANCHER]
if args.frontiere == "none":
    FRONTIERE = None
    if TIENNENT:
        sys.exit(f"« none » demandé, mais {TIENNENT} tiennent le plancher {PLANCHER} au seuil {SEUIL} : "
                 "la frontière se donne, elle ne se cache pas")
else:
    pf, sf = args.frontiere.split(":")
    if sf != SEUIL or pf not in PALIERS:
        sys.exit(f"la frontière {args.frontiere} n'est pas dans la colonne montrée ({SEUIL})")
    if cellule(AUTH, pf, sf)["bas"] < PLANCHER:
        sys.exit(f"la frontière {args.frontiere} ne tient pas le plancher {PLANCHER} : la règle ne la retiendrait pas")
    FRONTIERE = pf
ACCENTS = args.accents.split(",")
for a in ACCENTS:
    if a not in PALIERS:
        sys.exit(f"scénario d'accent inconnu du relevé : {a}")
AVANT = {1: ACCENTS[0], 2: ACCENTS[1], 3: MEILLEUR, 4: None, 5: None}[args.etat]
for d in D:
    print(f"[rack] {d['p']}@{SEUIL} : borne basse {d['bas']:.3f}, {d['lapis']}/{d['n_susp']} lapis, "
          f"{d['gris']}/{d['n_ben']} ambre", flush=True)
print(f"[rack] plancher {PLANCHER} : {'aucun scénario ne le tient' if not TIENNENT else TIENNENT} ; "
      f"meilleure borne {MEILLEUR}", flush=True)


# ── la scène ─────────────────────────────────────────────────────────────────
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
    c.adaptive_threshold = 0.005
    c.diffuse_bounces = 3
    c.glossy_bounces = 6
    c.max_bounces = 12
    c.sample_clamp_indirect = 8.0
    c.caustics_reflective = False
    c.caustics_refractive = False
    # le périphérique : METAL sur le Mac (défaut) ; CRUSETRA_GPU=OPTIX ou CUDA sur une machine louée (9/09 ; CASCADE_GPU, l'ancien nom, reste lu)
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = os.environ.get("CRUSETRA_GPU") or os.environ.get("CASCADE_GPU") or "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = (d.type != "CPU")
        c.device = "GPU"
    except Exception:
        c.device = "CPU"
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    sc.view_settings.look = "None"


def matiere(nom, base, rugosite=0.45, metal=0.0, emission=None, force=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb(base), 1)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    if emission:
        p.inputs["Emission Color"].default_value = (*srgb(emission), 1)
        p.inputs["Emission Strength"].default_value = force
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


def lampe_cle(position, energie=1400.0, taille=3.0, couleur="#fff4e2"):
    L = bpy.data.lights.new("cle", "AREA")
    L.energy = energie
    L.size = taille
    L.color = srgb(couleur)
    o = bpy.data.objects.new("cle", L)
    bpy.context.collection.objects.link(o)
    o.location = position
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(position)).to_track_quat("-Z", "Y").to_euler()
    return o


def sol_papier(z):
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, z - 0.002))
    o = bpy.context.object
    o.name = "sol_papier"
    pose(o, matiere("m_papier", P_PAPIER, rugosite=0.94))
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


def camera(azimut, elevation, boite, focale=60, marge=1.17, ouverture=0.0, r=10.0):
    """Cadrée sur une boîte DONNÉE : les états qui partagent la boîte partagent la caméra.
    marge 1.17 : plumer.py refuse un objet opaque dans ses 90 px de bord."""
    from bpy_extras.object_utils import world_to_camera_view
    mn, mx = boite
    centre = (mn + mx) / 2
    az, el = math.radians(azimut), math.radians(elevation)
    position = centre + Vector((math.cos(el) * math.cos(az) * r, math.cos(el) * math.sin(az) * r, math.sin(el) * r))
    cam = bpy.data.cameras.new("cam")
    cam.lens = focale
    o = bpy.data.objects.new("cam", cam)
    bpy.context.collection.objects.link(o)
    o.location = position
    bpy.context.scene.camera = o
    direction = centre - position
    o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    axe = -direction.normalized()
    coins = [Vector((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    for _ in range(240):
        bpy.context.view_layer.update()
        uv = [world_to_camera_view(bpy.context.scene, o, p) for p in coins]
        u = max(max(abs(v.x - .5), abs(v.y - .5)) * 2 for v in uv)
        if u * marge > 1.0:
            o.location = Vector(o.location) + axe * 0.1
        elif u * marge < 0.95:
            o.location = Vector(o.location) - axe * 0.1
        else:
            break
    if ouverture:
        cam.dof.use_dof = True
        cam.dof.focus_distance = (Vector(o.location) - centre).length
        cam.dof.aperture_fstop = ouverture
    return o


def chanfrein(o, part=0.010, n=3, plancher=0.004):
    bpy.context.view_layer.update()
    petit = min(d for d in o.dimensions if d > 1e-6)
    m = o.modifiers.new("chanfrein", "BEVEL")
    m.width, m.segments = max(plancher, petit * part), n
    m.harden_normals = True
    bpy.ops.object.shade_smooth()
    return o


def boite(nom, dims, pos, mat, biseau=0.02, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos, rotation=rot)
    o = bpy.context.object
    o.name = nom
    o.scale = dims
    pose(o, mat)
    bpy.ops.object.transform_apply(scale=True)
    chanfrein(o, biseau)
    return o


def cylindre(nom, r, h, pos, mat, verts=32, rot=(0, 0, 0), biseau=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=pos, rotation=rot)
    o = bpy.context.object
    o.name = nom
    pose(o, mat)
    if biseau:
        chanfrein(o, biseau)
    else:
        bpy.ops.object.shade_smooth()
    return o


# ── LA PALETTE : noir anodisé, laiton, lapis lumineux, ambre ; l'ivoire pour ce qui est à vous ──
def matieres():
    return {
        "anodise":       matiere("m_anodise", "#141517", rugosite=0.52, metal=0.6),
        "anodise_clair": matiere("m_anodise_clair", "#4a4d55", rugosite=0.46, metal=0.6),   # la lame en avant : gris canon, nettement plus clair
        "acier_sombre":  matiere("m_acier_sombre", "#2b2d31", rugosite=0.48, metal=0.85),
        "laiton":        matiere("m_laiton", "#c9a24a", rugosite=0.44, metal=1.0),
        "laiton_vif":    matiere("m_laiton_vif", "#d8b15a", rugosite=0.4, metal=1.0, emission="#e0b455", force=1.4),
        "ivoire":        matiere("m_ivoire", "#ece5d2", rugosite=0.7),
        "led_lapis":     matiere("m_led_lapis", "#4f8ae0", rugosite=0.4, emission="#5c9cff", force=6.0),
        "led_lapis_demi": matiere("m_led_lapis_demi", "#3f6fb8", rugosite=0.4, emission="#5c9cff", force=1.1),
        "led_ambre":     matiere("m_led_ambre", "#ffb347", rugosite=0.4, emission="#ffb03a", force=6.0),
        "led_ambre_demi": matiere("m_led_ambre_demi", "#b8803a", rugosite=0.4, emission="#ffb03a", force=1.1),
        "led_eteinte":   matiere("m_led_eteinte", "#26282d", rugosite=0.4),
        "led_petite_lapis": matiere("m_led_petite", "#4f8ae0", rugosite=0.4, emission="#5c9cff", force=5.0),
    }


# ── LE SUJET ─────────────────────────────────────────────────────────────────
LAME_L, PAS = 0.44, 0.5
N_LAMES = len(D) + 1                     # sept scénarios, et la vôtre
L = PAS * (N_LAMES - 1) + LAME_L + 0.5
P, H = 0.72, 0.95
ZB, HB = 0.12, 0.62                      # le pied et la hauteur d'une barre (borne 1,0)
YF = -P / 2 - 0.02


def chassis(M, longueur=L):
    boite("chassis", (longueur, P, H), (0, 0, H / 2), M["anodise"], 0.03)
    boite("facade", (longueur - 0.12, 0.02, H - 0.12), (0, -P / 2 - 0.005, H / 2), M["acier_sombre"], 0.01)
    for sx in (1, -1):
        for sy in (1, -1):
            cylindre(f"pied_{sx}{sy}", 0.05, 0.06, (sx * (longueur / 2 - 0.2), sy * (P / 2 - 0.2), -0.03), M["acier_sombre"], verts=24)


def matrice(nom, x, z, compte, total, allumee, eteinte, M, colonnes=6, pas=0.034, r=0.012, cote=1):
    """Une matrice de diodes : les `compte` premières allumées, les autres éteintes."""
    for k in range(total):
        col, rang = k % colonnes, k // colonnes
        lx = x + (col - (colonnes - 1) / 2) * pas * cote
        lz = z + rang * pas
        cylindre(f"{nom}_{k}", r, 0.012, (lx, YF - 0.02, lz), allumee if k < compte else eteinte,
                 verts=12, rot=(math.pi / 2, 0, 0))


def lame(i, x, d, M, avant=False, demi=False, frontiere=False, tiree=0.0):
    """Une lame de scénario : le panneau, la rainure et sa barre à la borne basse, les deux
    matrices. `demi` : les diodes à demi-intensité (les autres lames quand une est en avant)."""
    y = YF - 0.006 - tiree
    boite(f"lame_{i}", (LAME_L, 0.02, HB + 0.16), (x, y, ZB + (HB + 0.16) / 2 - 0.04),
          M["anodise_clair"] if avant else M["anodise"], 0.006)
    boite(f"rainure_{i}", (0.05, 0.02, HB), (x, y - 0.008, ZB + HB / 2), M["led_eteinte"], 0.003)
    if d is None:
        return
    h = max(0.02, d["bas"] * HB)
    lapis = M["led_lapis_demi"] if demi else M["led_lapis"]
    ambre = M["led_ambre_demi"] if demi else M["led_ambre"]
    boite(f"barre_{i}", (0.036, 0.02, h), (x, y - 0.014, ZB + h / 2), M["laiton_vif"] if frontiere else lapis, 0.002)
    matrice(f"led_{i}_s", x - 0.185, ZB + 0.05, d["lapis"], d["n_susp"], lapis, M["led_eteinte"], M, cote=-1)
    matrice(f"led_{i}_b", x + 0.185, ZB + 0.05, d["gris"], d["n_ben"], ambre, M["led_eteinte"], M, cote=1)


def ligne_plancher(M, longueur=L, avant=False):
    zp = ZB + PLANCHER * HB
    boite("gravure", (longueur - 0.2, 0.03, 0.016 if avant else 0.014), (0, YF - 0.018, zp),
          M["laiton_vif"] if avant else M["laiton"], 0.002)


def fiche_ivoire(M, x, tiree):
    """La fiche du client, glissée dans la huitième lame : votre export, pas encore mesuré."""
    boite("fiche", (LAME_L - 0.14, 0.012, HB + 0.12), (x, YF - 0.006 - tiree - 0.02, ZB + (HB + 0.12) / 2 + 0.06), M["ivoire"], 0.003)


def le_rack(M):
    chassis(M)
    for i, d in enumerate(D):
        x = -PAS * (N_LAMES - 1) / 2 + i * PAS
        avant = (AVANT == d["p"])
        # la lame en avant SORT du châssis de quelques centimètres : le regard la trouve
        # avant de lire ; les autres restent à demi-intensité
        lame(i, x, d, M, avant=avant, demi=(AVANT is not None and not avant),
             frontiere=(FRONTIERE == d["p"]), tiree=0.06 if avant else 0.0)
    x8 = -PAS * (N_LAMES - 1) / 2 + len(D) * PAS
    tiree = 0.16 if args.etat == 5 else 0.0
    lame(len(D), x8, None, M, tiree=tiree)
    if args.etat == 5:
        fiche_ivoire(M, x8, tiree)
    ligne_plancher(M, avant=(args.etat == 3))


def deux_lames(M):
    """Finding 04 : la même cellule (la meilleure borne), deux provenances côte à côte ;
    à gauche les cas écrits (42 diodes), à droite les variantes fabriquées (126 diodes,
    plus petites, plus serrées), sous la même ligne du plancher."""
    longueur = PAS * 1 + LAME_L + 0.5
    chassis(M, longueur)
    a = cellule(AUTH, MEILLEUR, SEUIL)
    s = cellule(SYNT, MEILLEUR, SEUIL)
    xa, xs = -PAS / 2, PAS / 2
    lame(0, xa, a, M, avant=True)
    # la lame des variantes : les matrices sont refaites à leur taille (126 = 9 × 14)
    y = YF - 0.006
    boite("lame_1", (LAME_L, 0.02, HB + 0.16), (xs, y, ZB + (HB + 0.16) / 2 - 0.04), M["anodise"], 0.006)
    boite("rainure_1", (0.05, 0.02, HB), (xs, y - 0.008, ZB + HB / 2), M["led_eteinte"], 0.003)
    h = max(0.02, s["bas"] * HB)
    boite("barre_1", (0.036, 0.02, h), (xs, y - 0.014, ZB + h / 2), M["led_lapis"], 0.002)
    matrice("led_1_s", xs - 0.185, ZB + 0.04, s["lapis"], s["n_susp"], M["led_petite_lapis"], M["led_eteinte"], M,
            colonnes=9, pas=0.02, r=0.007, cote=-1)
    matrice("led_1_b", xs + 0.185, ZB + 0.04, s["gris"], s["n_ben"], M["led_ambre"], M["led_eteinte"], M,
            colonnes=9, pas=0.02, r=0.007, cote=1)
    ligne_plancher(M, longueur, avant=True)
    print(f"[rack] état 4 : écrits {a['lapis']}/{a['n_susp']} borne {a['bas']:.3f} ({'tient' if a['bas'] >= PLANCHER else 'ne tient pas'}) ; "
          f"variantes {s['lapis']}/{s['n_susp']} borne {s['bas']:.3f} ({'tient' if s['bas'] >= PLANCHER else 'ne tient pas'})", flush=True)


def rendre():
    table_rase()
    monde_hdri("contraste.hdr", force=1.0, rotation=math.pi * 0.35)
    M = matieres()
    if args.etat == 4:
        deux_lames(M)
        az, el, focale = -78.0, 14.0, 60          # presque de face : la paire, pas le flanc
    else:
        le_rack(M)
        az, el, focale = args.azimut, args.elevation, 60
    # la boîte COMMUNE des états du rack : la lame tirée et sa fiche (état 5) comptent
    # dans tous, pour une seule caméra
    mn, mx = boite_du_sujet()
    if args.etat != 4:
        mn = Vector((mn.x, min(mn.y, YF - 0.006 - 0.22 - 0.03), mn.z))
        mx = Vector((mx.x, mx.y, max(mx.z, ZB + (HB + 0.28) + 0.02)))
    lampe_cle((-3.5, -4.0, 5.0))
    sol_papier(-0.06)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = LARGE, HAUT
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.film_transparent = (args.fond != "papier")
    os.makedirs(args.sortie, exist_ok=True)
    # marge 1.07 : le rack remplit le cadre (à 1.17 les diodes étaient des points) ; plumer.py
    # se lance alors avec --marge 40, la rampe suffit à effacer le voile du capteur d'ombre
    ouverture = 0.0 if APERCU else 9.0
    # ── les boîtes des cibles : calculées de la même géométrie que les objets ──
    def boite_cible(nom):
        if nom == "tout" or args.etat == 4:
            return (Vector(mn), Vector(mx))
        air = 0.10
        if nom == "ligne":
            # la ligne sur toute la longueur ferait reculer la caméra (le rack redevenait petit,
            # vu le 9/09) : le gros plan cadre les trois lames du milieu que la ligne traverse
            zp = ZB + PLANCHER * HB
            # les trois lames de GAUCHE (amount, velocity, structuring) : la plus haute barre est
            # celle du montant, et le finding la nomme ; la ligne les traverse toutes
            x0 = -PAS * (N_LAMES - 1) / 2
            return (Vector((x0 - LAME_L / 2 - 0.08, YF - 0.30, zp - 0.20)), Vector((x0 + 2 * PAS + LAME_L / 2 + 0.08, mx.y, zp + 0.20)))
        if nom.startswith("lame:"):
            quoi = nom.split(":", 1)[1]
            if quoi == "8":
                i = len(D)
            else:
                i = next((k for k, d in enumerate(D) if d["p"] == quoi), None)
                if i is None:
                    sys.exit(f"[rack] cible inconnue : {nom} (scénarios : {', '.join(d['p'] for d in D)}, 8)")
            x = -PAS * (N_LAMES - 1) / 2 + i * PAS
            tiree = 0.16 if (i == len(D) and args.etat == 5) else (0.06 if (i < len(D) and AVANT == D[i]["p"]) else 0.0)
            return (Vector((x - LAME_L / 2 - air, YF - 0.30 - tiree, -0.05)), Vector((x + LAME_L / 2 + air, mx.y, H + 0.10)))
        sys.exit(f"[rack] cible inconnue : {nom}")
    arrivee_boite = boite_cible(args.cible)
    if not args.sequence:
        camera(az, el, arrivee_boite, focale=focale, marge=1.07 if args.cible == "tout" else 1.0, ouverture=ouverture)
        sc.render.filepath = os.path.join(args.sortie, f"rack-0{args.etat}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[rack] rendu → {sc.render.filepath}\n[rack] Le code de sortie 0 ne prouve rien : ouvrir l'image et la regarder.")
        return
    # la transition : la scène est bâtie une fois, la caméra se replace à chaque image ; le
    # cadrage se recalcule sur la même boîte (camera() ajuste la distance à la marge), donc
    # l'objet ne saute pas d'une image à l'autre. Adoucie aux deux bouts (cosinus) : un
    # scroll qui s'arrête n'arrive jamais en plein élan. --via = point de contrôle (Bézier).
    az0, el0, marge0 = (float(x) for x in args.depart.split(","))
    arrivee = (az, el, 1.07 if args.cible == "tout" else 1.0)
    depart_boite = boite_cible(args.cible_depart or args.cible)
    via = tuple(float(x) for x in args.via.split(",")) if args.via else None
    def chemin(t, k):
        a, b = (az0, el0, marge0)[k], arrivee[k]
        if via is None:
            return a + (b - a) * t
        c = via[k]                                    # Bézier quadratique : passe PRÈS du via
        return (1 - t) ** 2 * a + 2 * (1 - t) * t * c + t ** 2 * b
    n = max(2, args.sequence)
    # les lames qui glissent : celle de l'état précédent (sortie → rentrée) et celle de l'état (rentrée → sortie)
    def objets_de_lame(i):
        pref = (f"lame_{i}", f"rainure_{i}", f"barre_{i}", f"led_{i}_")
        return [o for o in bpy.context.scene.objects if o.name.startswith(pref)]
    glissent = []
    if args.avant_depart and args.etat != 4:
        i_av = next((k for k, d in enumerate(D) if d["p"] == args.avant_depart), None)
        if i_av is None:
            sys.exit(f"[rack] --avant-depart inconnu : {args.avant_depart}")
        i_nouv = next((k for k, d in enumerate(D) if d["p"] == AVANT), None) if AVANT is not None else None
        objs = objets_de_lame(i_av)
        glissent.append((objs, [o.location.y for o in objs], +1))
        if i_nouv is not None and i_nouv != i_av:
            objs = objets_de_lame(i_nouv)
            glissent.append((objs, [o.location.y for o in objs], -1))
    def glisser(t):
        # u : 1 → 0 sur les premiers 40 % de la course. Les objets sont bâtis à leur place D'ÉTAT : la lame
        # d'avant y est rentrée (on la sort de 0,06·u), la nouvelle y est sortie (on la rentre de 0,06·u)
        u = 1.0 - min(1.0, t / 0.4)
        for objs, y0, sens in glissent:
            for o, y in zip(objs, y0):
                o.location.y = y - 0.06 * u if sens == +1 else y + 0.06 * u
    for i in range(n):
        t = 0.5 - 0.5 * math.cos(math.pi * i / (n - 1))
        glisser(t)
        boite_t = (depart_boite[0].lerp(arrivee_boite[0], t), depart_boite[1].lerp(arrivee_boite[1], t))
        cam = camera(chemin(t, 0), chemin(t, 1), boite_t, focale=focale, marge=chemin(t, 2), ouverture=ouverture)
        # l'image d'arrêt porte l'annotation : elle seule mérite la qualité pleine
        sc.cycles.samples = (args.echantillons_arrivee or ECHANTILLONS) if i == n - 1 else ECHANTILLONS
        sc.render.filepath = os.path.join(args.sortie, f"rack-seq-0{args.etat}-{i:03d}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam, do_unlink=True)
    print(f"[rack] séquence : {n} images vers l'état {args.etat} dans {args.sortie} (la dernière = le cadrage de l'état)")


rendre()
