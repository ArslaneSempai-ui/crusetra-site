#!/usr/bin/env python3
"""LA PAGE D'ACCUEIL, refonte du 3 septembre : une seule page qui se scrolle.

CE QU'ARSLANE A ARRÊTÉ (maquette M1A, validée écran par écran)
  · le héros nuit : la question en Literata géant, le lede en deux lignes,
    le bloc commande centré, l'indication de scroll ;
  · la séquence : le rail-filmstrip à l'encre verte à gauche (vignettes des
    cinq états), le plateau 3D annoté au centre, la fiche en colonne à droite ;
    le design 3D garde sa taille et sa place, c'est l'intérieur qui change ;
  · le film : l'affiche du master en poster, lecture DANS la page (balise video), YouTube en lien secondaire ;
  · la couture papier au double filet entre les deux blocs nuit ;
  · l'instrument : la table de routage, le bouton fantôme en bas à droite ;
  · les annexes en tuiles, le pied nuit.

CE QUE CETTE PAGE REFUSE
  · le tiret cadratin, nulle part (assembler.py porte le refus mécanique) ;
  · un chiffre tapé : la table vient de landing.json de l'outil, l'hypothèse
    humaine de assumptions.ts, le compte de tests du README : si une source
    manque, la bâtisse s'arrête au lieu de recopier ;
  · une boîte de scène qui perd son ratio : les annotations (repère viewBox)
    et leurs chips (pour cent de la boîte) divergeraient : hauteur bornée par
    la place disponible, ratio 1.42 tenu ;
  · une page morte sans JavaScript : sans lui, la séquence se déplie en
    colonne statique, tout se lit.
"""
import html as html_mod
import hashlib
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).parent
OUTIL = pathlib.Path.home() / "Documents" / "cascade"

# ── les sources, avec témoins : pas de source, pas de page ───────────────────
if not (OUTIL / "landing.json").exists():
    sys.exit(f"landing.json introuvable dans {OUTIL} : la table ne se tape pas, elle se lit")
LANDING = json.loads((OUTIL / "landing.json").read_text())

_assomptions = (OUTIL / "src" / "assumptions.ts").read_text()
_m = re.search(r"humanAccuracy:\s*(0\.\d+),", _assomptions)
if not _m:
    sys.exit("l'hypothèse humanAccuracy est introuvable dans assumptions.ts : refus de l'inventer")
HUMAIN = float(_m.group(1)) * 100          # 85.0 : une hypothèse déclarée, jamais mesurée

_m = re.search(r"\*\*(\d+) tests\*\* across (\d+) files", (OUTIL / "README.md").read_text())
if not _m:
    sys.exit("le compte de tests est introuvable dans le README de l'outil : refus de le recopier")
N_TESTS, N_FICHIERS = _m.group(1), _m.group(2)

from outil import SCEAU_ROUTING, etiquette_sur_objet, SEUIL_OBJET, etiquettes_qui_se_recouvrent, barre_site, CSS_BARRE_SITE, CSS_PIED_SITE, OUTILS, pied_html, n_tests
from outil import SITE_URL, ORGANISATION   # the house address, written once in outil.py
from outil import FILMS_VISIBLES   # the films switch, written once in outil.py
from instrument_carte import (CSS_AFFICHE, affiche_html, CSS_ACCUEIL, eventail_html, methode_html,   # l'affiche (10/09), l'accueil (10/09)
                              _svg_courbes, _svg_paliers, _svg_horloge)
SCEAU = SCEAU_ROUTING   # lu dans le relevé scellé du vert, jamais tapé (8/09)
DEPOT_URL = OUTILS["routing"]["depot"]   # the repository, written once in outil.py


def qte(v):
    """96.6 -> « 96.6 », 100.0 -> « 100 », 0 -> « 0 » : la valeur du relevé, sans zéro de traîne."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# ── la table de l'instrument : GÉNÉRÉE depuis landing.json, jamais tapée ─────
CHAMPS = LANDING["fields"]
_tiers = LANDING["tiers"]
PALIERS = [t["id"] for t in _tiers if t["id"] != "human"] + ["human*"]
ROUTAGE = {c: [t["id"] for t in _tiers].index(LANDING["routing"]["fields"][c]) for c in CHAMPS}
_n_socle = {t["n"] for t in _tiers[:3]}
_n_gen = {t["n"] for t in _tiers if t["id"].startswith("gen-")}
assert len(_n_socle) == 1 and len(_n_gen) == 1, "les n des paliers ne sont plus homogènes"
N_SOCLE, N_GEN = _n_socle.pop(), _n_gen.pop()
# 04/10 (audit Routing) : la longueur des dossiers du corpus, lue dans la réserve de landing.json, jamais tapée ;
# la page doit dire que le corpus est écrit par nous et que l'invite des paliers génératifs a été réglée sur la
# moitié tenue à l'écart (README, bloc fuite : « optimistic by an unknown amount »)
_m_long = re.search(r"(\d+) caractères", " ".join(LANDING.get("caveats", [])))
assert _m_long, "la longueur moyenne des dossiers n'est plus dans les réserves de landing.json"
LONGUEUR_DOSSIER = int(_m_long.group(1))
CAVEAT_CORPUS = (f"The records are a corpus we wrote, about {LONGUEUR_DOSSIER} characters each; the generative tiers' prompt "
                 "was tuned on the held-out half, so their figures are optimistic by an amount not yet measured.")


def table_html():
    tetes = "".join(f"<th scope='col'>{p}</th>" for p in PALIERS)
    lignes = ""
    for c in CHAMPS:
        cells = ""
        for j, t in enumerate(_tiers):
            if t["id"] == "human":
                v = qte(HUMAIN)
            else:
                v = qte(t["acc"][c]["accuracy"])
            choisi = " choisi" if ROUTAGE[c] == j else ""
            cells += f"<td class='cell{choisi}'><span>{v}<small>%</small></span></td>"
        lignes += f"<tr><th scope='row'>{c}</th>{cells}</tr>"
    return f'''<div class="t-scroll"><table class="routage">
      <caption class="sr">Accuracy of each tier on each field, measured on held-out records</caption>
      <thead><tr><th scope="col">field</th>{tetes}</tr></thead><tbody>{lignes}</tbody></table></div>
      <p class="t-note">Measured on {N_SOCLE:,} held-out records for the rules, small and large tiers, and
      {N_GEN} for the generative tiers. {CAVEAT_CORPUS} *Human accuracy is assumed at {qte(HUMAIN)}% until you measure
      your own reviewers with <code>npm run measure:humans</code>. Green cells mark the
      published routing.</p>'''


# ── le contenu de la séquence : les cinq trouvailles, mot pour mot du publié ─
SCENES = [
    dict(num="01", titre="94.4% per field, 76.7% per file",
         phrase="The same published routing reads 94.4% accuracy averaged per field and 76.7% as the per-file rate, 92 of 120 files, 17.7 points apart.",
         a="94.4<small>%</small>", b="76.7<small>%</small>", cote="17.7 points apart"),
    dict(num="02", titre="File-aimed routing: 3 files gained, none lost, of 120 files",
         phrase="Aiming at the file gains 3 files and loses none of the 120 files: too few to separate the two rates. The cost falls 3.5&#215; only if the large model is billed at an assumed price per call.",
         a="$191", b="$54", cote="on an assumed price"),
    dict(num="03", titre="Abstention: 85 wrong values removed, 12 correct values withheld",
         phrase="On 30 documents chosen for being hard, abstaining removes 85 values that were wrong and withholds 12 values that were right. Of the values still returned, 62.3% are right, against 30% before.",
         a="30<small>%</small>", b="62.3<small>%</small>", cote="after abstention"),
    dict(num="04", titre="Identical counts across two passes, and unstable durations withheld",
         phrase="Two passes produce identical counts. Durations vary, so they&#8217;re withheld.",
         a="identical", b="16&#8211;60<small>%</small>", cote="withheld"),
    dict(num="05", titre="All 16,807 routings computed, none sampled",
         phrase="The solver computes all 16,807 routings and prints the winner; the record carries the count. None is sampled.",
         a="16,807", b="120<small>&nbsp;files</small>", cote="the full span"),
]

LEGS = [
    ("mean accuracy over the five fields",
     "files with all five fields correct (92 of 120)"),
    ("Published routing, per 100,000 documents, with the large model at an assumed $1.60 per 1,000 calls.",
     "File-aimed routing, same volume and assumption. Priced at machine time, it is the dearer of the two."),
    ("Accuracy when each value is returned, right or wrong, on the 30 documents of the hard corpus.",
     "Accuracy of the values still returned after abstention; 97 of 150 values go to review."),
    ("Token counts match exactly across both runs.",
     "Durations moved between 16% and 60% from one run to the next, so they are withheld; a cost built on a duration carries that spread."),
    ("All 16,807 routings computed, end to end.",
     "The 120 records held out for scoring them, frozen with a content hash."),
]

# ── les annotations du plateau : géométrie vérifiée sur les rendus ───────────
# Rangée du fond = rules (2 zéros orange : name à gauche, address à droite, 3 verts
# publiés entre) ; vert gauche-centre = name vers large ; canal creux = l'humain.
# Chaque phrase sort du site ou de l'outil publiés, rien d'inventé.
APPELS = [
    [
        (0.830, 0.330, 0.814, 0.160, "published routing: 94.4% accuracy per field"),
        (0.470, 0.520, 0.343, 0.220, "per-file rate: 76.7%, 92 of 120 files"),
        (0.780, 0.250, 0.343, 0.052, "human tier: 85% assumed, not sampled"),
    ],
    [
        (0.440, 0.530, 0.500, 0.220, "file-aimed routing: cheaper only on an assumed price"),
        (0.270, 0.550, 0.108, 0.260, "published routing: the pick it replaces"),
        (0.720, 0.280, 0.696, 0.052, "a tier both routings share"),
    ],
    [
        (0.820, 0.520, 0.814, 0.220, "an emptied cell: a blank held for re-reading"),
        (0.480, 0.380, 0.343, 0.220, "abstention: 85 wrong values removed, 12 correct withheld"),
    ],
    [
        (0.520, 0.480, 0.500, 0.160, "two runs, identical counts"),
        (0.600, 0.350, 0.892, 0.780, "durations vary 16 to 60%, so withheld"),
    ],
    [
        (0.500, 0.450, 0.500, 0.160, "all 16,807 routings tested, none sampled"),
        (0.800, 0.520, 0.892, 0.780, "human tier: 85% assumed, not sampled"),
    ],
]

# l'image (1374x1120) posée en contain dans la boîte 1.42:1 (viewBox 1420x1000) ;
# la boîte DOIT garder ce ratio (height + aspect-ratio), sinon chips et lignes divergent
IH, IW = 1000.0, 1000.0 * (1374 / 1120)
MX = (1420 - IW) / 2


APPEL_MAX = 60   # caractères : deux lignes dans une chip .ap-eti, jamais trois (Arslane, 8/09 : « 2 lignes max »)


def verifier_appel(txt, ou):
    """Une explication en transparence sur un plateau tient en DEUX lignes, sur toutes les
    couleurs ; au-delà, la chip couvre l'objet qu'elle explique. La règle est mécanique :
    une étiquette trop longue ne se bâtit pas. Le maximum publié tenait en 59."""
    if len(txt) > APPEL_MAX:
        sys.exit(f"annotation trop longue ({len(txt)} > {APPEL_MAX}) sur {ou} : « {txt} » ; deux lignes max")
    if not txt.strip():
        sys.exit(f"annotation vide sur {ou}")
    return txt


def appels_html(i):
    lignes, etiquettes = "", ""
    # deux chips d'une même scène ne se recouvrent pas (9/09 : « a pick both routings share »
    # cachait « name changes reader… » sur la scène 2 servie) : même règle que les quatre outils
    for (a, b) in etiquettes_qui_se_recouvrent(APPELS[i]):
        sys.exit(f"routing, scène {i + 1} : les étiquettes « {APPELS[i][a][4]} » et « {APPELS[i][b][4]} » "
                 "se recouvrent : les écarter")
    for (ax, ay, lx, ly, txt) in APPELS[i]:
        verifier_appel(txt, f"routing, scène {i + 1}")
        # l'étiquette sur le crème, jamais sur l'objet (Arslane, 9/09) : même garde que les quatre outils
        image_v = BASE / "rendus" / "etats" / f"objet-0{i + 1}.webp"
        if image_v.exists() and (BASE / "rendus" / "sequences" / "objet" / "manifest.json").exists():
            part = etiquette_sur_objet(image_v, lx, ly)
            if part > SEUIL_OBJET:
                sys.exit(f"routing, scène {i + 1} : l'étiquette « {txt} » couvre l'objet ({part:.0%}) : la poser sur le crème")
        x1, y1 = MX + lx * IW, ly * IH
        x2, y2 = MX + ax * IW, ay * IH
        lignes += (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" pathLength="1"/>'
                   f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="4"/>')
        etiquettes += (f'<span class="ap-eti" style="left:{x1 / 14.20:.1f}%;top:{y1 / 10.0:.1f}%">{txt}</span>')
    return (f'<svg class="appels" viewBox="0 0 1420 1000" aria-hidden="true">{lignes}</svg>{etiquettes}')


def scene_html(i, s):
    return f'''
    <div class="scene{' actif' if i == 0 else ''}" id="scene-{i}" data-i="{i}">
      <img class="objet" src="rendus/etats/objet-{s['num']}.webp"
        alt="The measured relief, state {s['num']}: {s['titre']}">
      {appels_html(i)}
      <figure class="fiche">
        <figcaption class="fiche-t"><span>finding {s['num']}</span><span class="ft-cote">{s['cote']}</span></figcaption>
        <p class="fiche-phrase">{s['phrase']}</p>
        <div class="paire">
          <div class="val"><span class="chiffre pale-v">{s['a']}</span><span class="leg">{LEGS[i][0]}</span></div>
          <div class="val"><span class="chiffre vert-v">{s['b']}</span><span class="leg">{LEGS[i][1]}</span></div>
        </div>
      </figure>
    </div>'''


def rail_html():
    items = "".join(
        f'''<li><button class="jalon{' actif' if i == 0 else ''}" data-i="{i}" aria-label="Go to finding {s['num']}: {s['titre']}">
        <img class="j-vig" src="rendus/etats/objet-{s['num']}.webp" alt="">
        <span class="j-num">{s['num']}</span><span class="j-corps"><span class="j-titre">{s['titre']}</span>
        <span class="j-cote">{s['cote']}</span></span></button></li>''' for i, s in enumerate(SCENES))
    return f'<nav class="rail" aria-label="Findings"><span class="jauge" aria-hidden="true"><i></i></span><ul>{items}</ul></nav>'


MENUS = [
    ("methode", "Method &amp; reproducibility", "One method, no secrets. Run it twice, compare.", "ANNEXE-METHODE.html"),
    ("securite", "Security &amp; data handling", "Each place the tool touches.", "ANNEXE-SECURITE.html"),
    ("questions", "Questions", "Eight objections a bank's reviewers actually raise.", "ANNEXE-QUESTIONS.html"),
    ("terms", "Terms of engagement", "What the grant allows, for how long, and what a client buys.", "ANNEXE-TERMS.html"),
    ("privacy", "Privacy", "The tool collects no data. What you send us for a report, and how long it is kept.", "ANNEXE-PRIVACY.html"),
    ("accessibilite", "Accessibility", "Usable by keyboard, by screen reader, and with motion turned off.", "ANNEXE-ACCESSIBILITE.html"),
]


def menus_html():
    tuiles = "".join(f'''
      <a class="tuile" href="{href}">
        <span class="tuile-img"><img src="rendus/etats/objet-{cle}.webp" alt=""></span>
        <span class="tuile-corps"><span class="tuile-t">{titre}</span>
        <span class="tuile-d">{desc}</span></span>
        <span class="tuile-fl" aria-hidden="true">&#8594;</span>
      </a>''' for cle, titre, desc, href in MENUS)
    return f'''<nav class="menus" aria-label="Appendices"><div class="colonne">
      <h2 class="h2">Appendices</h2>
      <div class="grille">{tuiles}</div>
      <div class="rangee-fine">
        <a class="lien-fin" href="ENGAGEMENT.html">See pricing <span aria-hidden="true">&#8594;</span></a>
        <a class="lien-fin" href="CONTACT.html">Get in touch <span aria-hidden="true">&#8594;</span></a>
        <a class="lien-fin" href="MENTIONS.html">Read the fine print <span aria-hidden="true">&#8594;</span></a>
        <a class="lien-fin" href="{DEPOT_URL}">View the public repository <span aria-hidden="true">&#8594;</span></a>
      </div></div></nav>'''


# ── la mise en dépliage : partagée par le petit écran ET l'absence de script ─
# 30/09 : .theatre et .scenes y prennent toute la largeur. Sans elles, .scenes (conteneur de taille, largeur
# naturelle NULLE) et .theatre tombaient à 0 px dans la colonne centrée, et chaque fiche faisait 46 px sur
# téléphone (temoin-effondrement.mjs). Pas de commentaire CSS ICI : ce bloc est aussi préfixé pour le sans-script.
DEPLIE = '''
    .sequence{height:auto}
    .colle{position:static;height:auto;flex-direction:column;padding:60px 22px;gap:28px;align-items:stretch}
    .theatre{width:100%}
    .scenes{width:100%}
    .rail{width:100%}
    .rail ul{flex-direction:row;flex-wrap:wrap;gap:2px 14px}
    .jalon{padding:8px 0 8px 10px}
    .jalon .j-titre{font-size:15px}
    .j-vig{display:none}
    .appels,.ap-eti{display:none}
    .scenes{aspect-ratio:auto;height:auto;margin:0;position:static}
    .scene{position:static;opacity:1;transform:none;pointer-events:auto;margin-bottom:44px}
    .scene .objet{position:static;height:auto}
    .scene .fiche{position:static;transform:none;width:100%;margin:0}
'''

CSS = '''
  :root{--papier:#dbd7c5;--papier-haut:#e2ddcb;--papier-bas:#cdccb9;--encre:#1b1d18;
    --demi:#4a4739;--pale:#55523f;--filet:#9d9a83;--filet-clair:#bab7a0;
    --nuit-a:#1b3229;--nuit-b:#14251e;--nuit-c:#0e1a15;--sur-vert:#e4ecdf;--sur-vert-pale:#a9bdaf;
    --vert-titre:#23543f;--vert-vif:#57b184;--vert-clair:#a5f7cb;
    --texte:"Literata",Georgia,serif;--mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    --sans:ui-sans-serif,-apple-system,"Helvetica Neue",sans-serif;
    --montee:cubic-bezier(.16,.84,.32,1)}
  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{background:var(--papier);color:var(--encre);font-family:var(--texte);line-height:1.55}
  img{max-width:100%;height:auto;display:block}
  ::selection{background:var(--vert-titre);color:var(--sur-vert)}
  html{caret-color:var(--vert-vif);scrollbar-color:var(--vert-titre) var(--papier-bas)}
  a{text-underline-offset:4px;color:inherit}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  :focus-visible{outline:3px solid var(--vert-vif);outline-offset:3px;border-radius:2px}
  .colonne{max-width:1180px;margin:0 auto;padding:0 48px}
  .h2{font-size:clamp(28px,3.2vw,44px);font-weight:600;letter-spacing:-.015em;
    line-height:1.08;text-wrap:balance;margin:0 0 .8em}

  /* la barre */
  .barre{position:fixed;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;gap:28px;
    padding:14px 32px;transition:background .3s,box-shadow .3s}
  .barre.posee{background:color-mix(in srgb,var(--papier-haut) 88%,transparent);
    backdrop-filter:blur(10px);box-shadow:0 1px 0 color-mix(in srgb,var(--filet) 55%,transparent)}
  .barre.sur-nuit .marque{color:var(--sur-vert)}
  .barre.sur-nuit nav a{color:var(--sur-vert-pale)}
  .barre.sur-nuit nav a:hover{color:var(--sur-vert)}
  .marque{font-weight:700;font-size:19px;letter-spacing:.01em;text-decoration:none;padding:10px 0}
  .barre nav{display:flex;gap:16px;margin-left:auto}
  .barre nav a{font-size:14.5px;text-decoration:none;color:var(--demi);padding:13px 6px}
  .barre nav a:hover{color:var(--encre);text-decoration:underline;
    text-decoration-color:var(--vert-vif);text-decoration-thickness:1.5px}
  html:not(.js) .barre{position:absolute}
  html:not(.js) .barre .marque{color:var(--sur-vert)}
  html:not(.js) .barre nav a{color:var(--sur-vert-pale)}

  /* le héros */
  .hero{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;
    text-align:center;gap:26px;padding:120px 24px 130px;position:relative;color:var(--sur-vert);
    background:radial-gradient(130% 105% at 50% -18%,var(--nuit-a),var(--nuit-b) 50%,var(--nuit-c))}
  .hero .lede{color:var(--sur-vert-pale);margin-top:32px;max-width:87ch;text-wrap:wrap}
  .hero .lede b{color:var(--sur-vert)}
  .hero .commande{margin-top:34px;background:color-mix(in srgb,var(--nuit-a) 52%,transparent);
    border-color:color-mix(in srgb,var(--vert-vif) 34%,transparent);
    box-shadow:0 26px 70px rgba(0,0,0,.5)}
  .hero .cue{color:var(--sur-vert-pale)}
  /* la section des sociétés et navires (page Screening), forme M4F validée par Arslane le 28/09 : la nuit
     de l'outil, trois populations point par point (chaque marque une paire ou un nom, allumée quand le
     niveau fort la trouve), la grille se compte sous la souris, le pied aéré sous un filet pâle */
  .entites{padding:96px 0 136px;color:var(--sur-vert);background:linear-gradient(180deg,var(--nuit-a) 0%,var(--nuit-c) 100%);
    scroll-margin-top:77px}  /* l'ancre #companies se pose SOUS la barre fixe, comme #tools (Arslane, 28/09 : la barre mangeait le titre) */
  .entites .marque-h{color:var(--vert-clair);opacity:.9;margin-bottom:22px}
  .entites .h2{color:var(--sur-vert);font-size:clamp(34px,4.1vw,58px);margin:0}
  .entites .h2 br{display:none}@media(min-width:1100px){.entites .h2 br{display:inline}}
  .entites .pops{margin-top:84px;display:grid;gap:48px;padding-bottom:64px;
    border-bottom:1px solid color-mix(in srgb,var(--sur-vert) 16%,transparent)}
  .entites .pop{position:relative}
  .entites .tete{display:flex;justify-content:space-between;align-items:baseline;gap:24px;margin-bottom:12px}
  .entites .tete p{font-size:17px;color:var(--sur-vert-pale);max-width:none;padding-right:24px;margin:0}
  .entites .chiffre{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:40px;line-height:1;
    letter-spacing:-.03em;color:var(--vert-vif);white-space:nowrap}
  .entites .chiffre small{font-size:.4em;color:var(--sur-vert-pale);letter-spacing:0}
  .entites .grille{display:grid;grid-template-columns:repeat(100,1fr);gap:2px}
  .entites .grille i{display:block;aspect-ratio:1;border-radius:1px;background:color-mix(in srgb,var(--sur-vert) 18%,var(--nuit-b));
    transition:transform .2s var(--montee),background .2s,filter .2s}
  .entites .grille i.v{background:var(--vert-vif)}
  .entites .grille i.f{background:var(--vert-clair);box-shadow:0 0 10px var(--vert-clair)}
  .entites .grille i.p{background:var(--vert-vif)}
  .entites .grille i:hover{transform:scale(1.9);background:#fff}
  .entites .grille i.lu{filter:brightness(1.6)}
  .entites .grille i.lu:not(.v):not(.f):not(.p){background:color-mix(in srgb,var(--sur-vert) 38%,var(--nuit-b))}
  /* 30/09 (Arslane) : le compteur recouvrait la phrase et le grand chiffre ; il ferme désormais la ligne de légende */
  .entites .compteur{margin-left:auto;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
    text-transform:uppercase;color:var(--vert-clair);opacity:0;transition:opacity .2s;white-space:nowrap}
  .entites .pop.suivi .compteur{opacity:1}
  .entites .cle{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--sur-vert-pale);text-transform:uppercase;
    margin:10px 0 0;display:flex;gap:22px;flex-wrap:wrap}
  .entites .cle i{display:inline-block;width:10px;height:10px;vertical-align:-1px;margin-right:6px;border-radius:1px;
    background:color-mix(in srgb,var(--sur-vert) 18%,var(--nuit-b))}
  .entites .cle i.v{background:var(--vert-vif)}.entites .cle i.f{background:var(--vert-clair)}
  .entites .note{margin-top:48px;font-size:15px;line-height:1.65;color:var(--sur-vert-pale);max-width:none}
  .entites .liens{display:flex;gap:52px;flex-wrap:wrap;margin-top:44px}
  .entites .lien-e{color:var(--sur-vert);border-bottom:1px solid var(--sur-vert-pale);padding-bottom:4px;text-decoration:none;
    font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;transition:color .2s,border-color .2s}
  .entites .lien-e:hover{color:var(--vert-clair);border-color:var(--vert-clair)}
  .entites .lien-e span{display:inline-block;transition:transform .3s var(--montee)}.entites .lien-e:hover span{transform:translateX(4px)}
  .entites .sceau-l{display:block;margin-top:52px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--sur-vert-pale);opacity:.8}
  @media(max-width:700px){.entites .grille{grid-template-columns:repeat(50,1fr)}.entites .pops{margin-top:56px}}
  @media(prefers-reduced-motion:reduce){.entites .grille i,.entites .compteur,.entites .lien-e span{transition:none}}
  .marque-h{font-family:var(--mono);font-size:12px;letter-spacing:.22em;text-transform:uppercase;
    color:var(--sur-vert-pale)}
  /* depuis la copy (10/09) un titre de héros est une phrase entière : au-delà de 48 caractères
     il prend une taille plus basse et une mesure plus large, trois ou quatre lignes, pas cinq */
  .h1.h1-long{font-size:clamp(34px,4.6vw,64px);max-width:24ch}
  .h1{font-size:clamp(44px,7vw,92px);font-weight:600;letter-spacing:-.02em;line-height:1.02;
    text-wrap:balance;max-width:14ch}
  .lede{font-size:clamp(16px,1.35vw,19px);color:var(--demi);max-width:78ch;line-height:1.6;text-wrap:balance}
  .lede b{color:var(--encre)}
  .commande{background:var(--nuit-b);color:var(--sur-vert);border:1px solid color-mix(in srgb,var(--vert-vif) 40%,transparent);
    border-radius:10px;padding:18px 26px;text-align:left;font-family:var(--mono);font-size:12.5px;
    box-shadow:0 24px 60px rgba(14,26,21,.28);max-width:min(92vw,680px)}
  /* une commande longue se REPLIE au lieu de glisser sous un ascenseur invisible : la
     troisième ligne du bleu (deux fichiers) dépassait la boîte à 1440 sans aucun indice ;
     les commandes courtes du vert et du rouge tiennent sur leur ligne, rien ne bouge pour elles */
  .commande .ln{white-space:normal;overflow-wrap:anywhere;display:block;padding:2px 0}
  .commande .ln::before{content:"$ ";color:var(--vert-vif)}
  .commande .note{display:block;margin-top:8px;font-size:11px;color:var(--sur-vert-pale);text-align:center;
    font-family:var(--sans);letter-spacing:.02em}
  .entree{opacity:0;transform:translateY(18px);animation:lever .7s var(--montee) forwards}
  .entree:nth-child(2){animation-delay:.08s}.entree:nth-child(3){animation-delay:.16s}
  .entree:nth-child(4){animation-delay:.24s}
  @keyframes lever{to{opacity:1;transform:none}}
  html:not(.js) .entree{animation:none;opacity:1;transform:none}
  .cue{position:absolute;bottom:24px;left:50%;transform:translateX(-50%);display:flex;
    flex-direction:column;align-items:center;gap:10px;font-family:var(--mono);font-size:10.5px;
    letter-spacing:.22em;text-transform:uppercase;color:var(--pale)}
  .cue .fil{position:relative;width:1px;height:44px;overflow:hidden;
    background:color-mix(in srgb,currentColor 35%,transparent)}
  .cue .fil::after{content:"";position:absolute;left:-1px;top:-10px;width:3px;height:10px;
    border-radius:2px;background:var(--vert-vif);animation:cue 2.2s cubic-bezier(.4,0,.6,1) infinite}
  @keyframes cue{70%,100%{transform:translateY(54px)}}
  @media (prefers-reduced-motion:reduce){.entree{animation:none;opacity:1;transform:none}
    .cue .fil::after{animation:none;top:0}}

  /* le rideau : le deuxième écran, un pan par outil dans SES couleurs (posées en
     variables sur le pan, pas dans la palette de la page), le courant marqué */
  /* la traversée d'une page à l'autre est FONDUE (View Transitions, même origine) : ouvrir un
     outil depuis le rideau ne ressemble plus à un rafraîchissement (Arslane, 10/09) */
  @view-transition{navigation:auto}
  ::view-transition-old(root),::view-transition-new(root){animation-duration:.5s}
  @media (prefers-reduced-motion:reduce){::view-transition-old(root),::view-transition-new(root){animation:none}}
  /* le rideau porte un NOM de traversée : les deux pages le reconnaissent comme le même objet
     et il se déplace au lieu de disparaître puis reparaître. Avec l'ancre #tools, le robot
     choisi reste sous le curseur et c'est le dessous qui change (Arslane, 13/09). */
  .rideau{view-transition-name:rideau}
  .rideau-titre{view-transition-name:rideau-titre}
  .rideau{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));
    position:relative;color:var(--sur-vert)}
  /* cinq pierres : à 340 px de pan minimum, 1440 n'en range que quatre et le cinquième
     tombe seul sur une deuxième rangée (vu le 8/09 sur toutes les pages). Dès 1200 px les
     cinq tiennent sur une rangée à 240 px ; en dessous, trois puis deux (rangées entières). */
  @media (min-width:1200px){.rideau{grid-template-columns:repeat(auto-fit,minmax(min(100%,235px),1fr))}}
  /*
   * LE TITRE SE CENTRE DANS LA BANDE QU'ON VOIT, ET ELLE COMMENCE SOUS LA BARRE.
   *
   * Arslane le voulait « au milieu entre le bord haut et l'étiquette au-dessus des robots »
   * (08/09). Mesuré avant de bouger : la barre posée occupe les 77 premiers pixels et elle
   * est opaque sur le rideau, donc le titre ne peut pas monter plus haut sans disparaître
   * dessous. La bande réellement visible va de 77 à l'étiquette (150), et le titre fait 18 px :
   * son sommet se pose donc à 77 + (150 - 77 - 18) / 2 = 104.
   */
  /* UN TITRE, PAS UNE ÉTIQUETTE (relecture du 8/09 : « make the header larger and a different font
     to make it stand out from the 5 instruments »). Literata 22 px, comme les autres titres de la
     page. LA CAUSE DES TROIS RATÉS DU 13/09 (« trop bas », « trop haut », « toujours pas ») : le
     rideau réservait 77 px pour la barre posée, en haut. Juste quand on ARRIVE par un robot (la
     barre recouvre le haut du rideau), faux quand on y DESCEND en défilant : la barre ne recouvre
     rien, et ces 77 px sont du vide au-dessus du titre. Désormais le rideau ne réserve rien et
     l'ancre #tools se pose SOUS la barre (scroll-margin-top) : dans les deux cas la bande visible
     va du bord haut du rideau aux étiquettes (160), et le titre de 27 est au milieu :
     (160 - 27) / 2 = 66. Centré sur l'axe, il n'en bouge pas. */
  .rideau-titre{position:absolute;top:66px;left:0;right:0;z-index:2;text-align:center;padding:0 24px;
    font-family:var(--texte);font-size:22px;font-weight:600;letter-spacing:-.01em;line-height:1.2;
    color:var(--sur-vert)}
  /* les cinq boutons « Open… » sur UNE ligne : les pans partent du haut et le bouton est
     poussé en bas (Arslane, 10/09 : « mets-les à la même ligne, là c'est éparpillé ») */
  .pan{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;text-align:center;
    gap:16px;min-height:calc(100vh - 77px);padding:160px 40px 90px;text-decoration:none;color:inherit;outline-offset:-6px;
    background:radial-gradient(120% 100% at 50% -10%,var(--pan-a),var(--pan-b) 55%,var(--pan-c))}
  .pan img{height:clamp(150px,24vh,230px);width:auto;filter:drop-shadow(0 20px 36px rgba(0,0,0,.55));
    transition:transform .35s var(--montee)}
  .pan .p-eti{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
    color:var(--pan-vif)}
  .pan .p-h{font-size:clamp(28px,3.4vw,50px);font-weight:600;line-height:1.05;letter-spacing:-.02em;
    text-wrap:balance;max-width:14ch;display:flex;align-items:center;justify-content:center;min-height:3.2em}
  .pan .p-d{font-size:15px;color:var(--sur-vert-pale);max-width:38ch;line-height:1.5}
  .pan .p-ouvrir{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;
    margin-top:auto;padding:10px 16px;border-radius:8px;transition:background .2s,color .2s;
    border:1px solid color-mix(in srgb,var(--sur-vert) 30%,transparent)}
  a.pan:hover .p-ouvrir,a.pan:focus-visible .p-ouvrir{background:var(--sur-vert);color:var(--nuit-c)}
  /* LE RIDEAU DOIT TENIR DANS L'ÉCRAN, parce qu'on y ATTERRIT maintenant (l'ancre #tools,
     13/09). Sur un écran de 900 px de haut, le pan mesurait 1040 : les cinq boutons « Open »
     tombaient sous le pli, à moitié coupés, et c'était la première chose qu'on voyait en
     changeant d'outil. Vu en capture native à 1440x900, la taille du portable le plus courant.
     Le banc des largeurs ne l'aurait jamais dit : il mesure le débord horizontal.
     On resserre par la HAUTEUR, pas par la largeur : le robot et la question gardent leurs
     proportions, c'est l'air autour qui cède. */
  @media (max-height:960px){
    /* le haut reste à 150 : c'est lui qui donne sa bande au titre, et la mesure du 08/09
       montrait 56 px de marge inutilisée sous les boutons à 728 px de haut. On resserre donc
       le BAS et les tailles, jamais le haut. */
    .pan{padding:160px 32px 56px;gap:12px}
    .pan img{height:clamp(120px,19vh,190px)}
    .pan .p-h{font-size:clamp(24px,2.9vw,42px);min-height:2.8em}
    .pan .p-d{font-size:14px;line-height:1.45}}
  /* SOUS 700 PX DE HAUT, le haut se resserre quand même, et le titre suit sa bande : à 640
     les boutons dépassaient déjà de 12 px avant le 08/09, et rendre l'air aux étiquettes
     sans cette exception les aurait poussés à 38. On ne rend jamais pire ce qui était déjà
     juste. Le titre se recentre sur la nouvelle bande : 77 + (124 - 77 - 18) / 2 = 91. */
  /* Mesuré le 13/09 à 1440x700 : le pan faisait 776 (750 avant le titre) pour 700 d'écran, les boutons
     « Open » sous le pli. Le haut cède 10, le bas 12, le robot 28, la question 38 : 688, et tout se voit. */
  @media (max-height:700px){
    .pan{padding:120px 32px 30px}
    .pan img{height:clamp(100px,15vh,150px)}
    .pan .p-h{font-size:clamp(22px,2.4vw,34px);min-height:2.6em}
    .rideau-titre{top:46px}}   /* (120 - 27) / 2 ; le pan fait 621 pour 623 d'écran sous la barre */
  /* le titre du rideau ne remonte PAS avec le reste : la barre posée mesure 77 px, et à
     70 il passait dessous (vu en capture, 13/09). Il reste à 84. */
  .pan[aria-current] .p-ouvrir{border-style:dashed;color:var(--sur-vert-pale)}
  /* le survol d'un pan (Arslane, 6/09) : un halo de SA couleur qui suit la souris,
     le robot qui se soulève, la question qui monte d'un souffle, l'autre pan qui
     s'assombrit ; au clavier, le focus donne le même halo, centré */
  .pan{position:relative;isolation:isolate}
  .pan::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:0;z-index:0;
    transition:opacity .4s var(--montee);
    background:radial-gradient(560px 460px at var(--mx,50%) var(--my,42%),
      color-mix(in srgb,var(--pan-vif) 26%,transparent),transparent 70%)}
  .pan>*{position:relative;z-index:1}
  a.pan:hover::before,a.pan:focus-visible::before{opacity:1}
  a.pan:hover{box-shadow:inset 0 0 0 2px color-mix(in srgb,var(--pan-vif) 60%,transparent)}
  a.pan:hover img{transform:translateY(-12px) scale(1.04)}
  a.pan:hover .p-h{transform:translateY(-4px)}
  a.pan:hover .p-eti{text-shadow:0 0 18px color-mix(in srgb,var(--pan-vif) 80%,transparent)}
  /* l'autre pan s'assombrit (un filtre, pas une opacité : en transparence il
     laissait voir le parchemin et virait au gris délavé, vu sur capture) */
  .pan{transition:transform .8s var(--montee),opacity .8s var(--montee),filter .45s var(--montee)}
  .rideau:has(a.pan:hover) .pan:not(:hover){filter:brightness(.72) saturate(.85)}
  /* l'entrée et l'ouverture du rideau (Arslane, 6/09 : « le slide de l'écran 1 à 2
     n'a rien de spécial ») : les pans arrivent des deux côtés quand le rideau
     entre dans la vue, et s'écartent au clic avant d'ouvrir l'outil ; sans script,
     rien ne bouge et les pans sont des liens */
  .rideau{overflow:hidden;background:var(--ouverture,var(--papier))}   /* derrière les pans : la nuit de l'outil qu'on ouvre */
  /* l'ancre #tools se pose SOUS la barre posée (77 px), pas dessous : le rideau entier se voit en
     arrivant par un robot, comme en descendant depuis l'accueil ; sous 1080 la barre est dans le
     flux et ne recouvre rien, l'ancre reprend le bord */
  @media (min-width:1081px){.rideau{scroll-margin-top:77px}}
  .pan{transition:transform .8s var(--montee),opacity .8s var(--montee)}
  .rideau .p-h,.rideau img,.rideau .p-d,.rideau .p-ouvrir,.rideau .p-eti{transition:transform .9s var(--montee),opacity .9s}
  html.js .rideau:not(.vu) .cote-g{transform:translateX(-18%);opacity:0}
  html.js .rideau:not(.vu) .cote-d{transform:translateX(18%);opacity:0}
  html.js .rideau:not(.vu) .pan img{transform:translateY(28px);opacity:0}
  html.js .rideau.vu .pan img{transition-delay:.25s}
  .rideau.ouvre .cote-g{transform:translateX(-102%)}
  .rideau.ouvre .cote-d{transform:translateX(102%)}
  .rideau.ouvre .rideau-titre{opacity:0;transition:opacity .3s}

  /* la séquence : rail-filmstrip, plateau annoté, fiche colonne */
  .sequence{height:560vh;position:relative}
  /* L'OBJET PREND LA PLACE (Arslane, 9/09 : « agrandir l'objet dans le héros », comme le
     prototype de la chorégraphie où la scène faisait 56 vw) : le rail passe de 380 à 290 px (vignettes 60, titres 17),
     l'écart et les marges se resserrent, la scène monte à 62 vh ; la réserve de la formule
     ci-dessous = écart 32 + fiche 270 + marges 64 = 366 px, sur une largeur plafonnée à 1400. */
  .colle{position:sticky;top:0;height:100vh;display:flex;align-items:center;gap:min(3vw,32px);
    padding:80px 32px 40px;max-width:1400px;margin:0 auto}
  .rail{width:min(290px,22vw);flex:none;position:relative;padding-left:18px}
  .rail .jauge{position:absolute;left:0;top:6px;bottom:6px;width:3px;
    background:color-mix(in srgb,var(--vert-titre) 25%,transparent);border-radius:1px}
  .rail .jauge i{position:absolute;left:0;top:0;width:100%;height:0%;
    background:var(--vert-vif);border-radius:1px}
  .rail ul{list-style:none;padding:0;display:flex;flex-direction:column;gap:4px}
  .jalon{display:flex;gap:16px;align-items:center;width:100%;text-align:left;background:none;
    border:0;border-left:3px solid transparent;padding:12px 0 12px 16px;cursor:pointer;
    font-family:var(--texte);color:color-mix(in srgb,var(--vert-titre) 80%,var(--pale));
    transition:color .25s,border-color .25s,background .25s}
  .j-vig{display:block;width:60px;aspect-ratio:1.42/1;object-fit:contain;flex:none;align-self:center;
    filter:grayscale(.65) drop-shadow(0 4px 6px rgba(27,29,24,.18));opacity:.5;transform:scale(.94);
    transition:opacity .3s,filter .3s,transform .3s var(--montee)}
  .jalon.actif .j-vig{filter:drop-shadow(0 6px 10px rgba(27,29,24,.25));opacity:1;transform:scale(1.06)}
  .jalon .j-num{font-family:var(--mono);font-size:12px;letter-spacing:.1em;
    color:color-mix(in srgb,var(--vert-titre) 90%,transparent)}
  .jalon.actif .j-num{color:var(--vert-vif)}
  .jalon .j-titre{display:block;font-size:17px;font-weight:600;letter-spacing:-.01em;line-height:1.18}
  .jalon:hover{color:var(--vert-titre)}
  .jalon.actif{color:var(--vert-titre);border-left-color:var(--vert-vif);
    background:linear-gradient(90deg,color-mix(in srgb,var(--vert-vif) 12%,transparent),transparent 72%);
    border-radius:0 10px 10px 0}
  .j-cote{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
    text-transform:uppercase;color:var(--vert-vif);margin-top:6px;opacity:0;max-height:0;
    overflow:hidden;transition:opacity .3s,max-height .3s}
  /* 2em coupait « GEOGRAPHY: 0% BOTH SIDES » en plein mot dès que la ligne passait sur deux
     lignes (Arslane, 08/09, vu sur Scoring et sur le Dossier). La plus longue fait 24
     caractères ; 5em laisse la place à quatre lignes et ne prend AUCUNE hauteur de plus que
     le texte, puisque c'est un maximum. La transition reste animable. */
  .jalon.actif .j-cote{opacity:1;max-height:5em}
  .theatre{flex:1;min-width:0;position:relative;display:flex;flex-direction:column;gap:20px}
  .scenes{position:relative;aspect-ratio:1.42/1;width:auto;margin:0 auto 0 0;container-type:inline-size;
    height:min(62vh,calc((min(100vw,1400px) - min(290px,22vw) - 366px)/1.42))}
  .scene{position:absolute;inset:0;opacity:0;transform:translateY(14px);
    transition:opacity .45s var(--montee),transform .45s var(--montee);pointer-events:none}
  .scene.actif{opacity:1;transform:none;pointer-events:auto}
  .scene .objet{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
    filter:drop-shadow(0 30px 40px rgba(27,29,24,.22))}
  .scene .fiche{position:absolute;left:100%;top:50%;right:auto;bottom:auto;
    transform:translateY(-50%);margin-left:20px;width:250px}

  /* les annotations : lignes d'épure, chips vert translucide, 2 lignes max */
  .appels{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
  .appels line{stroke:color-mix(in srgb,var(--vert-vif) 70%,transparent);stroke-width:1.5;
    vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1;
    transition:stroke-dashoffset .7s .25s var(--montee)}
  .appels circle{fill:color-mix(in srgb,var(--vert-vif) 80%,transparent)}
  .scene.actif .appels line{stroke-dashoffset:0}
  /* LA CHIP SUIT LA SCÈNE (9/09) : 240 px fixes sur une scène qui rétrécit débordaient sur le rail
     aux petites fenêtres ; en pour cent de la scène (32,3 % = 240/744) et en cqi, son empreinte est
     constante en unités du viewBox, et la garde des étiquettes (outil.py) se calibre une fois. */
  .ap-eti{position:absolute;transform:translate(-50%,-50%);width:max-content;max-width:32.3%;
    text-wrap:balance;font-family:var(--mono);font-size:clamp(9.5px,1.55cqi,11.5px);line-height:1.45;
    color:var(--vert-titre);background:color-mix(in srgb,var(--vert-vif) 13%,transparent);
    backdrop-filter:blur(3px);padding:.45em .8em;
    border:1px solid color-mix(in srgb,var(--vert-vif) 32%,transparent);
    border-radius:6px;opacity:0;transition:opacity .4s .55s;pointer-events:none}
  .scene.actif .ap-eti{opacity:1}

  /* la fiche : Literata partout, une seule ligne mono */
  .fiche{background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-b) 96%,transparent),
      color-mix(in srgb,var(--nuit-a) 92%,transparent));
    border:1px solid color-mix(in srgb,var(--vert-vif) 42%,transparent);border-radius:12px;
    color:var(--sur-vert);padding:16px 22px 14px;box-shadow:0 18px 50px rgba(14,26,21,.32)}
  .fiche-t{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--sur-vert-pale);border-bottom:1px solid color-mix(in srgb,var(--sur-vert-pale) 25%,transparent);
    padding-bottom:8px;margin-bottom:12px;display:flex;flex-direction:column;gap:4px;align-items:flex-start}
  .ft-cote{color:var(--vert-clair)}
  .fiche-phrase{font-size:16.5px;font-style:italic;color:var(--sur-vert);line-height:1.4;
    margin:0 0 14px;text-wrap:balance}
  .paire{display:grid;grid-template-columns:1fr;gap:14px}
  .val{min-width:0}
  .chiffre{font-family:var(--texte);font-weight:600;font-size:clamp(26px,2.6vw,40px);display:block;
    font-variant-numeric:lining-nums tabular-nums;letter-spacing:-.01em}
  .chiffre small{font-size:.55em;font-weight:400}
  .pale-v{color:var(--sur-vert-pale)}
  .vert-v{color:var(--vert-clair);text-shadow:0 0 18px color-mix(in srgb,var(--vert-vif) 55%,transparent)}
  .fiche .leg{display:block;font-family:var(--texte);font-size:13px;color:var(--sur-vert-pale);
    margin-top:5px;line-height:1.5}

  /* le film */
  .film{padding:110px 0 120px;color:var(--sur-vert);
    background:linear-gradient(180deg,var(--nuit-a),var(--nuit-b))}
  .film .h2{color:var(--sur-vert)}
  .film-duree{text-align:center;font-family:var(--mono);font-size:12px;letter-spacing:.1em;color:var(--vert-clair);
    text-transform:uppercase;margin:-.4em 0 1.6em}
  .lecteur{position:relative;display:block;border-radius:16px;overflow:hidden;background:var(--nuit-c);
    border:1px solid color-mix(in srgb,var(--vert-vif) 30%,transparent);
    box-shadow:0 34px 90px rgba(0,0,0,.55)}
  .lecteur:not(.joue){cursor:pointer}
  /* la vidéo native est la boîte : 16/9 par ses attributs, l'affiche en poster ; à l'arrêt
     elle grossit au survol comme l'affiche d'avant, en lecture elle ne bouge plus */
  .lecteur video{display:block;width:100%;height:auto;aspect-ratio:16/9;background:#000;transition:transform .4s var(--montee)}
  .lecteur:not(.joue):hover video{transform:scale(1.02)}
  .lecteur .jouer{position:absolute;inset:0;margin:auto;width:92px;height:92px;border-radius:50%;padding:0;
    appearance:none;cursor:pointer;color:inherit;font:inherit;
    background:color-mix(in srgb,var(--nuit-c) 68%,transparent);backdrop-filter:blur(6px);
    border:1.5px solid var(--vert-clair);display:flex;align-items:center;justify-content:center;
    transition:transform .25s var(--montee),background .25s}
  .lecteur:hover .jouer{transform:scale(1.1);background:color-mix(in srgb,var(--vert-titre) 70%,transparent)}
  .lecteur .jouer svg{margin-left:6px}
  .lecteur .duree{position:absolute;right:16px;bottom:14px;font-family:var(--mono);font-size:12px;
    letter-spacing:.08em;color:var(--sur-vert);background:color-mix(in srgb,var(--nuit-c) 72%,transparent);
    padding:5px 10px;border-radius:6px}
  /* en lecture : le bouton, la durée et l'affiche composée s'effacent, les commandes natives restent */
  .lecteur.joue .jouer,.lecteur.joue .duree,.lecteur.joue .affiche{display:none}
  /* 29/09 : sous le lecteur, les cartes des films (Screening : le film et la démo) ; la carte active porte le trait clair */
  .liste{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}
  .carte-film{display:grid;grid-template-columns:132px 1fr auto;gap:0 14px;align-items:center;padding:10px 14px 10px 10px;border-radius:12px;
    border:1px solid color-mix(in srgb,var(--vert-clair) 18%,transparent);background:color-mix(in srgb,var(--nuit-c) 60%,transparent);
    color:inherit;text-decoration:none;transition:border-color .3s var(--montee),background .3s var(--montee)}
  .carte-film:hover{border-color:color-mix(in srgb,var(--vert-clair) 55%,transparent)}
  .carte-film.est-actif{border-color:var(--vert-clair);background:color-mix(in srgb,var(--vert-clair) 9%,var(--nuit-c))}
  .carte-film img{width:132px;height:74px;object-fit:cover;border-radius:7px;display:block}
  .carte-film .cf-corps{display:flex;flex-direction:column;gap:3px;min-width:0}
  .carte-film .cf-e{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--vert-clair)}
  .carte-film .cf-t{font-size:15px;line-height:1.3}
  .carte-film .cf-d{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--vert-clair)}
  @media (max-width:700px){.liste{grid-template-columns:1fr}.carte-film{grid-template-columns:96px 1fr auto}.carte-film img{width:96px;height:54px}}
  .film-note{display:flex;justify-content:flex-end;gap:16px;flex-wrap:wrap;margin-top:16px;
    font-size:14px;color:var(--sur-vert-pale)}
  .film-note .ou{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:inherit;text-decoration:none}
  .film-note .ou:hover{color:var(--sur-vert)}
  /* l'affiche composée : la place du film d'un outil AVANT que sa vidéo existe
     (Arslane, 6/09 : « une partie pour mettre une vidéo sur toutes les couleurs »).
     Le robot penché de l'outil, sa question, sa nuit ; le jour venu, l'affiche
     rendue remplace la composition, le lecteur et la note ne bougent pas. */
  .lecteur .affiche{position:absolute;inset:0;overflow:hidden;
    background:radial-gradient(120% 120% at 82% 105%,var(--nuit-a),var(--nuit-c) 70%)}
  .lecteur .affiche img{position:absolute;right:5%;bottom:-9%;width:34%;height:auto;
    filter:drop-shadow(0 30px 60px rgba(0,0,0,.6))}
  .affiche .af-t{position:absolute;left:6%;top:14%;max-width:54%;color:var(--sur-vert)}
  .affiche .af-eti{display:block;font-family:var(--mono);font-size:clamp(10px,1vw,13px);
    letter-spacing:.2em;text-transform:uppercase;color:var(--vert-vif);margin-bottom:.9em}
  .affiche .af-q{display:block;font-size:clamp(20px,3.3vw,48px);font-weight:600;line-height:1.05;
    letter-spacing:-.02em;text-wrap:balance}
  /* sur l'affiche composée le bouton quitte le centre (il couvrait la question au
     téléphone, relu sur capture 375) : en bas à gauche, dans l'air sous le titre */
  .lecteur .affiche~.jouer{inset:auto auto 9% 6%;margin:0}
  /* au téléphone, 92 px couvraient le visage du robot (capture 375 du 27/09) : 64, cible encore large */
  @media (max-width:700px){.lecteur .jouer{width:64px;height:64px}
    .lecteur .jouer svg{width:20px;height:23px;margin-left:4px}}
  @media (max-width:700px){.lecteur .affiche~.jouer{width:56px;height:56px}
    .lecteur .affiche~.jouer svg{width:18px;height:20px;margin-left:4px}}

  /* la couture : une bande de papier au double filet entre les deux blocs nuit */
  .couture{background:var(--papier);padding:56px 0}
  .couture .colonne{display:flex;align-items:center;gap:18px}
  .couture .filet{flex:1;border-top:3px double var(--filet)}
  .couture .sceau-c{font-family:var(--mono);font-size:11px;letter-spacing:.14em;
    text-transform:uppercase;color:var(--pale);white-space:nowrap}

  /* l'instrument */
  .instrument{padding:110px 0 120px;color:var(--sur-vert);
    background:linear-gradient(180deg,var(--nuit-b) 0%,var(--nuit-c) 100%)}
  .instrument .h2{color:var(--sur-vert)}
  .instrument .t-note{color:var(--sur-vert-pale)}
  .t-scroll{overflow-x:auto;border-radius:14px;box-shadow:0 30px 80px rgba(0,0,0,.5);
    border:1px solid color-mix(in srgb,var(--vert-vif) 26%,transparent)}
  .routage{width:100%;border-collapse:collapse;background:color-mix(in srgb,var(--nuit-a) 72%,var(--nuit-b));
    color:var(--sur-vert);font-family:var(--mono);font-size:13px;min-width:720px}
  .routage th,.routage td{padding:12px 14px;text-align:center;
    border:1px solid color-mix(in srgb,var(--sur-vert-pale) 14%,transparent)}
  .routage thead th{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--sur-vert-pale)}
  .routage tbody th{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--sur-vert-pale)}
  .cell{transition:background .16s,box-shadow .16s}
  .cell:hover{background:color-mix(in srgb,var(--vert-vif) 12%,transparent);
    box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--vert-vif) 55%,transparent)}
  .cell.choisi{background:color-mix(in srgb,var(--vert-vif) 18%,transparent);color:var(--vert-clair);
    box-shadow:inset 0 0 0 1.5px var(--vert-vif)}
  .cell small{font-size:.7em;color:var(--sur-vert-pale)}
  .t-note{font-size:12.5px;color:var(--pale);margin-top:14px;max-width:none;line-height:1.55}
  /* le rapport de criblage en service (page Screening, 29/09) : la feuille réelle du rapport exemple posée sur la
     nuit de l'outil, qui s'incline sous la souris ; en dessous l'offre dans la langue de la page des tarifs
     (retouche d'Arslane, 29/09 : « comme notre page pricing, faut que ça soit travaillé ») : deux colonnes au halo
     qui suit la souris, un robot rubis au-dessus de chacune, le montant qui se compte à l'arrivée, puis le curseur
     de la taille de la liste qui déplace le prix entre les paliers de offre-screening.json ; mouvement réduit :
     montants posés, rien ne bouge */
  .rapport{padding:112px 0 124px;color:var(--sur-vert);background:linear-gradient(180deg,var(--nuit-c) 0%,var(--nuit-b) 100%);
    scroll-margin-top:77px}
  .rapport .r-grille{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,430px);gap:80px;align-items:start}
  .rapport .marque-h{color:var(--vert-clair);opacity:.9;margin-bottom:22px}
  .rapport .h2{color:var(--sur-vert);font-size:clamp(28px,2.9vw,42px);line-height:1.14;margin:0;text-wrap:balance}
  .rapport .r-pas{list-style:none;counter-reset:pas;padding:0;margin:48px 0 0;display:grid;gap:20px}
  .rapport .r-pas li{counter-increment:pas;display:grid;grid-template-columns:46px minmax(0,1fr);font-size:16.5px;line-height:1.62;
    color:var(--sur-vert-pale);max-width:62ch}
  .rapport .r-pas li::before{content:counter(pas,decimal-leading-zero);font-family:var(--mono);font-size:12px;letter-spacing:.1em;
    color:var(--vert-vif);padding-top:5px}
  .rapport .r-pas b{color:var(--sur-vert);font-weight:600}
  .rapport .r-feuille{margin:6px 0 0;position:sticky;top:112px;perspective:1400px}
  .rapport .r-feuille a{display:block;border-radius:3px;transform-style:preserve-3d;
    transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(var(--ty,0px));
    box-shadow:0 44px 96px rgba(0,0,0,.58),0 0 0 1px color-mix(in srgb,var(--sur-vert) 10%,transparent);
    transition:transform .5s var(--montee),box-shadow .5s var(--montee)}
  .rapport .r-feuille a.suit{transition:box-shadow .5s var(--montee)}
  .rapport .r-feuille img{display:block;width:100%;height:auto;border-radius:3px}
  .rapport .r-feuille a:hover,.rapport .r-feuille a:focus-visible{--ty:-6px;
    box-shadow:0 60px 120px rgba(0,0,0,.62),0 0 0 1px color-mix(in srgb,var(--vert-vif) 46%,transparent)}
  .rapport .r-feuille figcaption{margin-top:20px;font-family:var(--mono);font-size:11px;line-height:1.7;letter-spacing:.14em;
    text-transform:uppercase;color:var(--sur-vert-pale);opacity:.85}
  .rapport .r-offre{margin-top:150px}
  .rapport .r-cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px;align-items:stretch}
  .rapport .r-cols.trois{grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
  @media (max-width:1060px){.rapport .r-cols.trois{grid-template-columns:minmax(0,1fr);gap:108px;max-width:560px;margin-inline:auto}}
  .rapport .r-col{position:relative;isolation:isolate;padding:124px 38px 36px;border-radius:18px;
    border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 64%,transparent),color-mix(in srgb,var(--nuit-c) 86%,transparent));
    transition:opacity .45s var(--montee),border-color .3s,transform .45s var(--montee),box-shadow .45s var(--montee)}
  .rapport .r-col::before{content:"";position:absolute;inset:0;z-index:-1;border-radius:inherit;opacity:0;transition:opacity .4s;
    background:radial-gradient(420px 300px at var(--mx,50%) var(--my,30%),color-mix(in srgb,var(--vert-vif) 15%,transparent),transparent 70%)}
  .rapport .r-col:hover::before{opacity:1}
  .rapport .r-col:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--vert-vif) 46%,transparent);
    box-shadow:0 26px 70px rgba(0,0,0,.42)}
  .rapport .r-col.haute{border-color:color-mix(in srgb,var(--vert-vif) 36%,transparent)}
  .rapport .r-robot{position:absolute;top:-80px;left:50%;height:172px;width:auto;transform:translateX(-50%);pointer-events:none;
    filter:drop-shadow(0 26px 30px rgba(0,0,0,.55));transition:transform .6s var(--montee)}
  .rapport .r-col:hover .r-robot{transform:translateX(-50%) translateY(-8px) rotate(-2deg)}
  .rapport .r-eti{margin:0;font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--vert-clair)}
  .rapport .r-montant{margin:14px 0 8px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
  .rapport .r-n{font-weight:600;font-size:clamp(46px,5vw,72px);letter-spacing:-.02em;line-height:1.02;
    font-variant-numeric:lining-nums tabular-nums;color:var(--sur-vert)}
  .rapport .r-n.mot{font-size:clamp(30px,3vw,42px)}
  .rapport .r-col.haute .r-n{color:var(--vert-clair);text-shadow:0 0 26px color-mix(in srgb,var(--vert-vif) 42%,transparent)}
  .rapport .r-montant small{font-size:14px;color:var(--sur-vert-pale)}
  .rapport .r-sous{margin:0 0 22px;font-size:15.5px;line-height:1.6;color:var(--sur-vert-pale);max-width:46ch}
  .rapport .r-inclus{list-style:none;margin:0;padding:20px 0 0;display:grid;gap:11px;
    border-top:1px solid color-mix(in srgb,var(--sur-vert) 14%,transparent)}
  .rapport .r-inclus li{position:relative;padding-left:28px;font-size:15px;line-height:1.55;color:var(--sur-vert-pale)}
  .rapport .r-inclus li::before{content:"";position:absolute;left:3px;top:.42em;width:11px;height:6px;
    border-left:1.5px solid var(--vert-vif);border-bottom:1.5px solid var(--vert-vif);transform:rotate(-45deg)}
  .rapport .r-inclus b{color:var(--sur-vert);font-weight:600}
  /* 04/10 : the receipts-first entry and the five steps of the free test ; paragraphs run the full column width */
  .rapport .r-recus{margin-top:64px;padding:30px 34px;border-radius:18px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);background:color-mix(in srgb,var(--nuit-c) 72%,transparent)}
  .rapport .r-recus p{margin:0 0 14px;font-size:15.5px;line-height:1.6;color:var(--sur-vert-pale);max-width:none}
  .rapport .r-recus p:last-child{margin-bottom:0}
  .rapport .r-recus .marque-h{margin-bottom:14px}
  .rapport .r-cmd{display:block;margin:0 0 16px;padding:14px 18px;border-radius:10px;background:var(--nuit-b);border:1px solid color-mix(in srgb,var(--vert-vif) 40%,transparent);
    font-family:var(--mono);font-size:12.5px;line-height:1.7;color:var(--sur-vert);white-space:pre-wrap;overflow-wrap:anywhere}
  .rapport .r-cmd b{color:var(--vert-vif);font-weight:400}
  .rapport .r-essai{margin-top:64px}
  .rapport .r-essai .r-pas{margin-top:20px}
  .rapport .r-essai .r-pas li{max-width:none}
  .rapport .r-essai code{font-family:var(--mono);font-size:12.5px;color:var(--sur-vert);background:color-mix(in srgb,var(--nuit-b) 80%,transparent);padding:1px 6px;border-radius:5px;overflow-wrap:anywhere}
  .rapport .r-col.hors{opacity:.4}
  .rapport .r-au-dela{margin:20px 0 0;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--vert-clair)}
  .rapport .r-taille{margin-top:28px;padding:30px 38px 30px;border-radius:18px;
    border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);background:color-mix(in srgb,var(--nuit-c) 72%,transparent)}
  .rapport .r-taille-tete{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
  .rapport .r-taille label{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--sur-vert-pale)}
  .rapport .r-noms-v{font-family:var(--mono);font-size:28px;letter-spacing:-.02em;color:var(--sur-vert);font-variant-numeric:tabular-nums}
  .rapport .r-bascule{margin-left:auto;display:inline-flex;padding:3px;border-radius:999px;
    border:1px solid color-mix(in srgb,var(--sur-vert) 18%,transparent)}
  .rapport .r-bascule button{font:inherit;font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
    background:none;border:0;color:var(--sur-vert-pale);padding:9px 16px;border-radius:999px;cursor:pointer;transition:background .25s,color .25s}
  .rapport .r-bascule button[aria-pressed="true"]{background:color-mix(in srgb,var(--vert-vif) 24%,transparent);color:var(--sur-vert)}
  .rapport .r-bascule button:hover{color:var(--sur-vert)}
  .rapport .r-piste{position:relative;margin:22px 0 62px;--f:0}
  .rapport .r-piste input{display:block;width:100%;height:40px;margin:0;background:transparent;-webkit-appearance:none;appearance:none;cursor:grab;
    position:relative;z-index:2}
  .rapport .r-piste input:active{cursor:grabbing}
  .rapport .r-piste input::-webkit-slider-runnable-track{height:2px;border-radius:2px;
    background:linear-gradient(90deg,var(--vert-vif) calc(var(--f)*100%),color-mix(in srgb,var(--sur-vert) 20%,transparent) calc(var(--f)*100%))}
  .rapport .r-piste input::-moz-range-track{height:2px;border-radius:2px;background:color-mix(in srgb,var(--sur-vert) 20%,transparent)}
  .rapport .r-piste input::-moz-range-progress{height:2px;background:var(--vert-vif)}
  .rapport .r-piste input::-webkit-slider-thumb{-webkit-appearance:none;width:24px;height:24px;margin-top:-11px;border-radius:50%;
    background:var(--vert-clair);border:5px solid var(--nuit-b);box-shadow:0 0 0 1px var(--vert-vif),0 0 24px color-mix(in srgb,var(--vert-vif) 60%,transparent);
    transition:transform .2s var(--montee)}
  .rapport .r-piste input::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:var(--vert-clair);border:5px solid var(--nuit-b);
    box-shadow:0 0 0 1px var(--vert-vif),0 0 24px color-mix(in srgb,var(--vert-vif) 60%,transparent)}
  .rapport .r-piste input:hover::-webkit-slider-thumb,.rapport .r-piste input:focus-visible::-webkit-slider-thumb{transform:scale(1.18)}
  .rapport .r-reperes{position:absolute;left:12px;right:12px;top:0;height:100%;pointer-events:none}
  .rapport .r-reperes span{position:absolute;left:calc(var(--p)*100%);top:30px;transform:translateX(-50%);display:grid;justify-items:center;gap:2px;
    font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;color:var(--sur-vert-pale);white-space:nowrap;transition:color .25s}
  .rapport .r-reperes span::before{content:"";width:1px;height:8px;background:currentColor;opacity:.7;margin-bottom:3px}
  .rapport .r-reperes span b{font-size:12.5px;font-weight:500;color:var(--sur-vert)}
  .rapport .r-reperes span.on{color:var(--vert-clair)}.rapport .r-reperes span.on b{color:var(--vert-clair)}
  .rapport .r-phrase{margin:0;font-size:17px;line-height:1.62;color:var(--sur-vert);max-width:none}
  .rapport .r-phrase b{color:var(--vert-clair);font-weight:600}
  html:not(.js) .rapport .r-piste,html:not(.js) .rapport .r-bascule{display:none}
  .rapport .r-note{margin-top:34px;font-size:14.5px;line-height:1.68;color:var(--sur-vert-pale);max-width:none}
  .rapport .ouvrir-ligne{margin-top:56px}.rapport .ouvrir-s{max-width:none}
  .rapport .liens{display:flex;gap:52px;flex-wrap:wrap;margin-top:34px}
  .rapport .lien-e{color:var(--sur-vert);border-bottom:1px solid var(--sur-vert-pale);padding-bottom:4px;text-decoration:none;
    font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;transition:color .2s,border-color .2s}
  .rapport .lien-e:hover{color:var(--vert-clair);border-color:var(--vert-clair)}
  .rapport .lien-e span{display:inline-block;transition:transform .3s var(--montee)}.rapport .lien-e:hover span{transform:translateX(4px)}
  .hero .vers-rapport{margin-top:6px;font-family:var(--mono);font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;
    color:var(--sur-vert);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--vert-vif) 55%,transparent);padding-bottom:5px;
    transition:color .2s,border-color .2s}
  .hero .vers-rapport:hover,.hero .vers-rapport:focus-visible{color:var(--vert-clair);border-color:var(--vert-clair)}
  .hero .vers-rapport span{display:inline-block;transition:transform .3s var(--montee)}.hero .vers-rapport:hover span{transform:translateY(3px)}
  @media (max-width:980px){.rapport .r-grille{grid-template-columns:minmax(0,1fr) minmax(0,300px);gap:44px}}
  @media (max-width:760px){.rapport{padding:84px 0 96px}
    .rapport .r-grille{grid-template-columns:minmax(0,1fr);gap:56px}
    .rapport .r-feuille{position:static;max-width:420px;margin:0 auto}
    .rapport .r-offre{margin-top:130px}
    .rapport .r-cols{grid-template-columns:minmax(0,1fr);gap:108px}
    .rapport .r-col{padding:108px 24px 28px}.rapport .r-robot{height:146px;top:-68px}
    .rapport .r-taille{padding:24px 20px 24px}.rapport .r-bascule{margin-left:0}
    .rapport .liens{gap:26px}}
  @media (prefers-reduced-motion:reduce){.rapport .r-feuille a,.rapport .r-col,.rapport .r-robot{transition:none;transform:none}
    .rapport .r-col:hover .r-robot{transform:translateX(-50%)}}
  /* le bandeau qui ouvre l'instrument, sous la vidéo (Arslane, 6/09 : « impressionnant,
     effet souris, sur chaque couleur ») : large, la couleur de l'outil en halo qui suit la
     souris, un éclat qui balaie, la flèche qui glisse dans son disque, la lueur qui monte ;
     au clavier le focus donne le même état, centré ; mouvement réduit : halo fixe */
  .ouvrir-ligne{display:flex;margin-top:40px}
  .ouvrir{position:relative;isolation:isolate;overflow:hidden;display:flex;align-items:center;gap:28px;
    width:100%;min-height:104px;padding:24px 28px 24px 34px;border-radius:16px;text-decoration:none;
    color:var(--sur-vert);font-family:var(--texte);
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 72%,var(--nuit-b)),var(--nuit-b));
    border:1px solid color-mix(in srgb,var(--vert-vif) 42%,transparent);
    transition:transform .4s var(--montee),border-color .3s,box-shadow .4s var(--montee)}
  .ouvrir::before{content:"";position:absolute;inset:0;z-index:0;opacity:0;transition:opacity .4s;
    background:radial-gradient(460px 280px at var(--mx,18%) var(--my,50%),
      color-mix(in srgb,var(--vert-vif) 16%,transparent),transparent 70%)}
  .ouvrir::after{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;
    background:linear-gradient(105deg,transparent 42%,color-mix(in srgb,var(--sur-vert) 5%,transparent) 50%,transparent 58%);
    transform:translateX(-130%)}
  .ouvrir>*{position:relative;z-index:1}
  .ouvrir-eti{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
    color:var(--vert-vif);margin-bottom:8px}
  .ouvrir-t{display:block;font-size:clamp(21px,2.3vw,30px);font-weight:600;letter-spacing:-.012em;line-height:1.12}
  .ouvrir-s{display:block;margin-top:7px;font-size:14.5px;color:var(--sur-vert-pale);max-width:60ch}
  .ouvrir .fl{margin-left:auto;flex:none;width:68px;height:68px;border-radius:50%;display:grid;place-items:center;
    font-family:var(--sans);font-size:34px;line-height:1;color:var(--vert-clair);
    border:1px solid color-mix(in srgb,var(--vert-vif) 50%,transparent);
    transition:transform .4s var(--montee),background .3s,color .3s,border-color .3s}
  /* sobre (Arslane, 7/09 : « c'est moche, plus sobre pour toutes les couleurs ») : pas de
     disque plein ni de flèche qui tourne ; l'anneau s'éclaire, la flèche glisse, c'est tout */
  .ouvrir:hover,.ouvrir:focus-visible{transform:translateY(-2px);
    border-color:color-mix(in srgb,var(--vert-vif) 70%,transparent);
    box-shadow:0 22px 56px color-mix(in srgb,var(--vert-vif) 14%,transparent)}
  .ouvrir:hover::before,.ouvrir:focus-visible::before{opacity:1}
  .ouvrir:hover::after{transform:translateX(130%);transition:transform 1.1s var(--montee)}
  .ouvrir:hover .fl,.ouvrir:focus-visible .fl{transform:translateX(8px);
    border-color:var(--vert-vif);background:color-mix(in srgb,var(--vert-vif) 12%,transparent)}
  @media (max-width:700px){.ouvrir{gap:16px;padding:20px 20px 20px 22px}.ouvrir .fl{width:52px;height:52px;font-size:26px}
    .ouvrir-s{display:none}}

''' + CSS_AFFICHE + '''
  /* les annexes en tuiles */
  .menus{padding:110px 0 90px;background:var(--papier)}
  /* With the films hidden, the seam sits right on the appendices: drop their top padding so the seam keeps 56px of air on both sides */
  .couture+.menus{padding-top:0}
  .grille{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
  .tuile{display:flex;flex-direction:column;gap:0;background:var(--papier-haut);
    border:1px solid color-mix(in srgb,var(--filet) 55%,transparent);border-radius:14px;
    text-decoration:none;overflow:hidden;position:relative;
    transition:transform .2s var(--montee),border-color .2s,background .2s}
  .tuile:hover{transform:translateY(-2px);border-color:var(--vert-titre);
    background:color-mix(in srgb,var(--papier-haut) 60%,#fff)}
  .tuile-img{display:block;height:150px;overflow:hidden;
    background:radial-gradient(120% 90% at 50% 8%,#fff 0%,var(--papier-haut) 70%)}
  .tuile-img img{height:100%;width:100%;object-fit:contain;padding:14px;
    transition:transform .3s var(--montee)}
  .tuile:hover .tuile-img img{transform:scale(1.06)}
  .tuile-corps{padding:16px 18px 20px}
  .tuile-t{display:block;font-size:18px;font-weight:600;letter-spacing:-.01em}
  .tuile-d{display:block;font-size:13.5px;color:var(--demi);margin-top:6px;line-height:1.55}
  .tuile-fl{position:absolute;right:16px;bottom:14px;font-family:var(--sans);font-size:18px;
    color:var(--vert-titre);opacity:0;transform:translateX(-8px);
    transition:opacity .22s,transform .22s var(--montee)}
  .tuile:hover .tuile-fl{opacity:1;transform:none}
  .rangee-fine{display:flex;gap:14px;margin-top:18px;flex-wrap:wrap}
  .lien-fin{flex:1;min-width:180px;display:flex;justify-content:space-between;align-items:center;
    font-size:15px;text-decoration:none;color:var(--demi);
    border:1px solid color-mix(in srgb,var(--filet) 55%,transparent);border-radius:10px;
    padding:14px 18px;transition:border-color .2s,color .2s}
  .lien-fin:hover{border-color:var(--vert-titre);color:var(--encre)}

  /* le pied */
  .pied{background:var(--nuit-c);color:var(--sur-vert);padding:64px 0}
  .pied-p{font-size:clamp(18px,2vw,26px);font-weight:600;letter-spacing:-.01em}

  @media (max-width:960px){
    .colonne{padding:0 22px}
    .barre{padding:12px 18px;gap:14px}
    .barre nav{display:none}
    .pan{min-height:62vh;padding:130px 24px 56px}
    .rideau-titre{top:51px}     /* (130 - 27) / 2 : la barre est dans le flux, la bande part du bord */
  }
  /* sous 700 px les pans s'empilent : seul le premier laisse la place au titre */
  @media (max-width:700px){
    .rideau{grid-template-columns:1fr}
    .pan{padding-top:84px}
    .rideau-titre{top:39px;font-size:19px}   /* deux lignes de 23 (46) dans 124 : 39 dessus, 39 dessous */
    .rideau-titre+.pan{padding-top:124px}
    /* au téléphone, une commande coupée par un ascenseur horizontal se lit
       comme une commande cassée : elle se replie, entière */
    .commande .ln{white-space:normal;overflow-wrap:anywhere}
    .grille{grid-template-columns:1fr}
    .couture .sceau-c{white-space:normal;text-align:center}
  }
  /* fenêtre réduite (641-1080) : le théâtre colle n'a pas la place d'être digne,
     la séquence se déplie en colonne, comme au téléphone et sans script */
  @media (max-width:1080px){''' + DEPLIE + '''
  }
  /* entre 1081 et 1220, le plateau est trop petit pour porter ses annotations */
  @media (max-width:1220px){
    .appels,.ap-eti{display:none!important}
  }
NOJS
  @media (prefers-reduced-motion:reduce){
    *{transition-duration:.01ms!important;animation-duration:.01ms!important}}
'''


def _prefixe_nojs(css):
    """Chaque sélecteur du dépliage préfixé html:not(.js) : sans script, la page se déplie.
    30/09 : l'ancienne version ne préfixait que la PREMIÈRE règle d'une ligne (« .a{}.b{} » laissait .b
    appliquée partout, et la fiche du bureau est partie 238 px hors de l'écran) et lisait un commentaire comme
    un sélecteur. Désormais : commentaires retirés, chaque règle préfixée, où qu'elle soit ; un @ refusé
    (le dépliage est plat, une règle imbriquée n'y a pas sa place)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if "@" in css:
        sys.exit("DEPLIE contient une règle @ : le préfixe sans-script ne sait pas l'imbriquer")
    blocs = css.split("}")
    out = []
    for bloc in blocs[:-1]:
        sel, decl = bloc.split("{", 1)
        out.append("\n    " + ",".join("html:not(.js) " + s.strip() for s in sel.split(",") if s.strip()) + "{" + decl)
    return "}".join(out) + "}" + blocs[-1]


CSS = CSS.replace("NOJS", _prefixe_nojs(DEPLIE))

JS = '''
  const reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const barre = document.querySelector(".barre");
  function poserBarre() {
    barre.classList.toggle("posee", scrollY > 40);
    barre.classList.toggle("sur-nuit", scrollY <= 40);
  }
  addEventListener("scroll", poserBarre, {passive: true});
  poserBarre();

  // le halo qui suit la souris : sur les pans du rideau et sur le bandeau de l'instrument
  // (mouvement réduit : le halo reste centré, rien ne suit)
  if (!reduit) {
    document.querySelectorAll("a.pan, .ouvrir").forEach((el) => el.addEventListener("pointermove", (ev) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", (ev.clientX - r.left) + "px");
      el.style.setProperty("--my", (ev.clientY - r.top) + "px");
    }, {passive: true}));
  }

  // le rideau : les pans entrent quand il arrive dans la vue ; au clic sur un pan,
  // le rideau s'écarte puis l'outil s'ouvre sur sa page (mouvement réduit : lien nu)
  const rideau = document.querySelector(".rideau");
  if (rideau) {
    /*
     * L'ATTERRISSAGE SUR LE RIDEAU EST INSTANTANÉ, ET C'EST TOUT L'INTÉRÊT DE L'ANCRE.
     *
     * `html` porte `scroll-behavior:smooth` pour les ancres de la page. Au CHARGEMENT, ce
     * même réglage anime le saut vers `#tools` : la page s'ouvre en haut, puis descend toute
     * seule. Deux défauts d'un coup : on voit le héros qu'on ne voulait pas revoir, et la
     * traversée fondue prend son instantané pendant que ça bouge encore. Mesuré le 13/09.
     *
     * On force donc le comportement immédiat pour ce seul saut, puis on le rend. La page
     * s'ouvre AU RIDEAU, les robots sont déjà à leur place, et seul le dessous a changé.
     */
    // 30/09 (Arslane) : un pan mène désormais à la SÉQUENCE 3D de l'outil choisi (#findings), sous le
    // rideau ; pour changer d'outil, on remonte au rideau. Même atterrissage immédiat pour les deux ancres.
    const cibleAncre = (location.hash === "#tools" || location.hash === "#findings") ? document.querySelector(location.hash) : null;
    if (cibleAncre) {
      const avant = document.documentElement.style.scrollBehavior;
      document.documentElement.style.scrollBehavior = "auto";
      cibleAncre.scrollIntoView({block: "start"});
      document.documentElement.style.scrollBehavior = avant;
    }
    if (!reduit && "IntersectionObserver" in window) {
      const io = new IntersectionObserver((entrees) => {
        if (entrees.some((e) => e.isIntersecting)) { rideau.classList.add("vu"); io.disconnect(); }
      }, {threshold: 0.18});
      io.observe(rideau);
    } else {
      rideau.classList.add("vu");
    }
    rideau.querySelectorAll("a.pan").forEach((pan) => pan.addEventListener("click", (ev) => {
      if (reduit || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      ev.preventDefault();
      // le rideau s'écarte sur la nuit de l'outil choisi : la page qui suit commence dans cette nuit
      rideau.style.setProperty("--ouverture", getComputedStyle(pan).getPropertyValue("--pan-b"));
      rideau.classList.add("ouvre");
      // 380 ms d'écart, puis la page de l'outil OUVERTE SUR SA SÉQUENCE 3D (#findings, décision du 30/09 ;
      // avant : sur son rideau, #tools, décision du 13/09).
      //
      // L'ancre avait été retirée le 10/09 au profit du seul fondu, et l'outil suivant s'ouvrait
      // sur son héros : on repartait donc du haut à chaque choix de robot. « ça nous remet tout
      // au-dessus, ce n'est pas pratique » (Arslane, 13/09). Elle revient : les pans s'écartent,
      // la page suivante s'ouvre au même endroit de l'écran, les robots reviennent à leur place
      // et SEUL LE DESSOUS a changé. La docstring de choix_outils() promettait déjà cette ancre
      // pendant que le code ne la posait plus.
      setTimeout(() => { location.href = pan.href; }, 380);
    }));
  }

  const seq = document.querySelector(".sequence");
  const scenes = [...document.querySelectorAll(".scene")];
  const jalons = [...document.querySelectorAll(".jalon")];
  const jauge = document.querySelector(".jauge i");
  let courant = -1;
  function poser(i) {
    if (i === courant) return;
    courant = i;
    scenes.forEach((s, k) => { s.classList.toggle("actif", k === i); s.setAttribute("aria-hidden", k === i ? "false" : "true"); });
    jalons.forEach((j, k) => j.classList.toggle("actif", k === i));
  }
  function surScroll() {
    if (innerWidth <= 1080) return;
    const r = seq.getBoundingClientRect();
    const total = r.height - innerHeight;
    const p = Math.min(1, Math.max(0, -r.top / total));
    if (jauge) jauge.style.height = (p * 100).toFixed(1) + "%";
    poser(Math.min(scenes.length - 1, Math.floor(p * scenes.length)));
  }
  addEventListener("scroll", surScroll, {passive: true});
  jalons.forEach((j, k) => j.addEventListener("click", () => {
    // le milieu du palier d'arrivée (le scrub tient la dernière image sur la seconde moitié)
    const r = seq.offsetTop + (seq.offsetHeight - innerHeight) * ((k + 0.75) / scenes.length);
    scrollTo({top: innerWidth <= 1080 ? scenes[k].offsetTop - 90 : r,
              behavior: reduit ? "auto" : "smooth"});
  }));
  poser(0); surScroll();
'''
# the player script ships only with the films (FILMS_VISIBLES, outil.py)
JS_LECTEUR = '''  // LE LECTEUR DU FILM (27/09) : sans script la vidéo porte ses commandes natives d'emblée ;
  // avec, l'affiche reste nue sous le bouton rond et les commandes viennent au premier clic,
  // n'importe où sur l'affiche. Le bouton est un vrai bouton (clavier), et la vidéo reçoit
  // le focus quand elle démarre. Si play() est refusé, les commandes natives restent : second essai.
  for (const lecteur of document.querySelectorAll(".lecteur[data-film]")) {
    const video = lecteur.querySelector("video");
    video.removeAttribute("controls");
    lecteur.addEventListener("click", () => {
      if (lecteur.classList.contains("joue")) return;
      lecteur.classList.add("joue");
      video.setAttribute("controls", "");
      video.focus();
      video.play().catch(() => {});
    });
    // 29/09 : les cartes sous le lecteur (Screening) : la carte cliquée devient le film du lecteur ; l'affiche
    // et le bouton reviennent, la durée et les libellés suivent, la note YouTube ne reste que si le film en a une
    const liste = lecteur.parentElement.querySelector(".liste"); const note = lecteur.parentElement.querySelector(".film-note");
    if (liste) for (const carte of liste.querySelectorAll(".carte-film")) carte.addEventListener("click", (e) => {
      e.preventDefault(); if (carte.classList.contains("est-actif")) return;
      video.pause(); lecteur.classList.remove("joue"); video.removeAttribute("controls");
      video.querySelector("source").setAttribute("src", carte.dataset.src); video.setAttribute("poster", carte.dataset.poster); video.load();
      lecteur.querySelector(".duree").textContent = carte.dataset.duree;
      const nom = "The " + carte.dataset.genre + " of Crusetra " + liste.dataset.nom + ", " + carte.dataset.dite;   // 04/10 : le nom de l'outil vient de la liste (Routing a aussi sa démo)
      video.setAttribute("aria-label", nom); lecteur.querySelector(".jouer").setAttribute("aria-label", "Play " + nom.charAt(0).toLowerCase() + nom.slice(1));
      for (const c of liste.querySelectorAll(".carte-film")) { c.classList.toggle("est-actif", c === carte); if (c === carte) c.setAttribute("aria-current", "true"); else c.removeAttribute("aria-current"); }
      // 30/09 : le lien « also on YouTube » suit le film choisi (il gardait l'adresse du premier)
      if (note) { note.style.display = carte.dataset.yt ? "" : "none"; const ou = note.querySelector("a"); if (ou && carte.dataset.yt) ou.href = carte.dataset.yt; }
    });
  }
'''
JS += JS_LECTEUR if FILMS_VISIBLES else ""

scenes = "".join(scene_html(i, s) for i, s in enumerate(SCENES))

# ── les données structurées : ce que les moteurs lisent, RIEN d'inventé ──────
# La description est la meta description, mot pour mot : une seule voix.
# L'offre à 0 est la seule vraie : le grant d'évaluation de trente jours,
# écrit dans la licence publique. Aucune note, aucun avis, aucun prix payant
# ici : les prix de l'engagement vivent sur leur page, en clair (assembler.py
# porte les refus). L'OS reprend le README de l'outil : macOS ou Linux ;
# Windows non testé, donc non affirmé.
DONNEES_STRUCTUREES = json.dumps({
    "@context": "https://schema.org",
    "@graph": [
        ORGANISATION,
        {"@type": "SoftwareApplication", "name": "Crusetra Routing",
         "url": f"{SITE_URL}routing/",
         "applicationCategory": "DeveloperApplication",
         "operatingSystem": "macOS, Linux (Node 24+)",
         "downloadUrl": DEPOT_URL,
         "description": "A routing audit for KYC extraction: measured on sealed "
                        "records, rerun on your machine. On your records, on "
                        "your machine: nothing leaves the network.",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "description": "Thirty-day evaluation on your own records, "
                                   "granted in the public license."},
         "publisher": {"@id": ORGANISATION["@id"]}},
    ],
}, ensure_ascii=True)

from outil import (OUTILS, PALETTE_VERTE, PALETTE_RUBIS, PALETTE_LAPIS, PALETTE_ONYX,
                   PALETTE_AMETHYSTE, NUIT_AMETHYSTE,
                   NUIT_VERTE, NUIT_RUBIS, NUIT_LAPIS, NUIT_ONYX,
                   lire_releve_scelle, lien, manques, ETATS_PREFIXE, ICONES_PREFIXE)


ICONES_COULEUR = {"screening": "rubis", "monitoring": "lapis", "scoring": "amethyste", "dossier": "onyx"}


def outils_vivants():
    """Les outils que les pages MONTRENT : un pan de rideau, une entrée de nav ou un
    nœud de graphe qui pointe vers une page ou un robot absents casserait tout le
    site pour un outil pas prêt. Routing et Screening sont en ligne ; un outil
    suivant entre TOUT SEUL le jour où ses findings ET son robot de rideau existent
    — la promesse « le rideau gagne le pan tout seul », tenue par un test
    d'existence plutôt que par une liste à retoucher."""
    # AUCUN cas particulier « en ligne » : le rouge en avait un ici (« ses pièces
    # sont commitées ») pendant que l'assembleur le faisait passer par manques() —
    # le pan du rouge restait au rideau quand son bloc tombait (étiquettes E-C1 en
    # cours), et l'assemblage finissait sur LIENS CASSÉS. La loi vaut pour tous,
    # le vert compris : un outil dont les pièces manquent perd son pan, et le dit.
    vivants = []
    for o in OUTILS.values():
        m = manques(o["id"], BASE)
        if not m:
            vivants.append(o)
        else:
            print(f"  rideau : {o['id']} pas encore prêt ({len(m)} pièce(s) : "
                  f"{', '.join(m[:3])}{'…' if len(m) > 3 else ''}) : pan non montré")
    return vivants

NOMBRES = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def choix_outils(outil):
    """LE RIDEAU : le deuxième écran, tranché par Arslane le 6/09 sur une planche de
    trois formes, puis précisé le même soir (décision A) : sur la page de la MARQUE
    (outil=None) les pans sont tous FERMÉS, aucun n'est « ouvert d'office » ; sur la
    page d'un outil, son pan est marqué aria-current. Un pan par outil de la table,
    chacun dans SES couleurs (posées en variables sur le pan : la page rubis aliase
    la palette, et le pan vert doit y rester vert), avec son robot, sa question et
    « Open X ». Cliquer un pan mène à SA page, ancrée sur sa séquence 3D (#findings, 30/09).
    Le script (JS) ajoute l'entrée des pans au défilement et l'ouverture du rideau au
    clic ; sans script, ce sont des liens. Grille auto-fit : un troisième robot
    prendra sa place sans qu'on touche ici. Les classes cote-g / cote-d disent de
    quel côté un pan glisse : la première moitié à gauche, la seconde à droite."""
    pans = ""
    outils = outils_vivants()
    for i, o in enumerate(outils):
        cote = "cote-g" if i < len(outils) / 2 else "cote-d"
        style = (f'--pan-vif:{o["vif"]};--pan-a:{o["nuit"][0]};'
                 f'--pan-b:{o["nuit"][1]};--pan-c:{o["nuit"][2]}')
        prefixe = outil["prefixe_racine"] if outil else ""
        # une NOUVELLE LIGNE entre les spans : le pan est un flex en colonne, donc
        # l'espace ne change rien à l'écran, mais sans lui l'étiquette, la question et
        # le pitch se collent (« …pattern?Some identity fields… ») et tout relevé de
        # prose lit UNE phrase de trente-sept mots là où le lecteur en voit trois.
        corps = (f'<span class="p-eti">{o["etiquette"]}</span>\n'
                 f'<img src="{prefixe}rendus/{o["robot_rideau"]}" alt="">\n'
                 f'<span class="p-h">{o["question"]}</span>\n'
                 f'<span class="p-d">{o["pitch"]}</span>\n')
        if outil is not None and o["id"] == outil["id"]:
            pans += (f'\n  <div class="pan {cote}" style="{style}" aria-current="page">{corps}'
                     f'<span class="p-ouvrir">You are here &#183; {o["nom"]}</span></div>')
        else:
            pans += (f'\n  <a class="pan {cote}" style="{style}" href="{prefixe}{o["page_hero"]}#findings">{corps}'
                     f'<span class="p-ouvrir">Open {o["nom"]} <span aria-hidden="true">&#8594;</span></span></a>')
    n = NOMBRES.get(len(outils), str(len(outils)))
    return (f'<nav class="rideau" id="tools" aria-label="The instruments">'
            f'\n  <span class="rideau-titre">Crusetra &#183; {n} instruments, one method</span>'
            f'{pans}\n</nav>')


# 27/09 : LES FILMS EN LIGNE, chaîne YouTube « HS Industries LLC ». Durée = celle qu'affiche YouTube
# (arrondie à la seconde supérieure) du fichier livré films-rendus/<outil>-livraison.mp4, mesuré au ffprobe :
# routing 78,50 s, dossier 92,97, screening 87,87, monitoring 94,63, scoring 90,17.
# 10/10 : les films Crusetra (source/films, ffprobe) : routing 89,57 s, dossier 97,40, screening 92,57. Leurs anciens
# liens YouTube montraient les films « Cascade » (passés en privé) ; les nouveaux sont publiés le 10/10.
FILMS = {"routing":    ("https://youtu.be/Usym93fV3ZY", "1:30", "1 minute 30"),
         "dossier":    ("https://youtu.be/KntYNO-j_Xs", "1:38", "1 minute 38"),
         "screening":  ("https://youtu.be/3fy9XWqeDoU", "1:33", "1 minute 33"),
         "monitoring": ("https://youtu.be/xx_1lFJsw9E", "1:35", "1 minute 35"),
         "scoring":    ("https://youtu.be/mCybN-xq4jA", "1:31", "1 minute 31"),
         # 29/09 : la DÉMO Screening (Dana, son fichier, la passe, le rapport, le registre), 85,06 s ; validée « parfait »
         "screening-demo": ("https://youtu.be/mTlpC9yXnXo", "1:26", "1 minute 26"),   # 30/09 : publiée, durée affichée par YouTube
         # 04/10 : la DÉMO Routing (le prix, l'arbre des reçus, le routage par champ, le rapport), 30,13 s, validée
         # « la vidéo est parfaite » ; film vertical 4:5 joué dans le lecteur 16:9, bandes noires ; pas encore sur YouTube
         "routing-demo": (None, "0:30", "30 seconds")}
# 04/10 : les outils qui ont une démo en plus de leur film : (le titre de la carte du film, le titre de la carte de la démo)
# 05/10 (parcours client) : la démo Screening (85 s) dit « five sanctions lists », « OFAC, BIS, UN and EU » et « measured
# blind … 332 of 400 » : sa carte quitte la page jusqu'à ce que le chef la refasse. Le fichier source/films/screening-demo.mp4
# et l'entrée FILMS restent (rien n'est effacé) ; sans entrée ici, la page n'a ni carte ni texte qui y mène.
DEMOS = {"routing":   ("The five Routing findings", "The price, the receipts, the routing, the report")}
DEMOS = {k: v for k, v in DEMOS.items() if f"{k}-demo" in FILMS_VISIBLES}   # 10/10 : la démo Routing dit encore « Cascade » : pas de carte tant qu'elle n'est pas refaite


def lecteur_html(oid, nom, prefixe, affiche=None, visuel="", genre="film"):
    """LE LECTEUR (27/09, Arslane : « redirigé vers YouTube, c'est pas très pro ») : le film
    joue DANS la page, par une balise video native et rien d'autre. L'affiche est son poster,
    le bouton rond reste par-dessus, les commandes natives viennent au premier clic (sans
    script elles sont là d'emblée : l'attribut controls est écrit, le script le retire).
    Le fichier est films/<outil>.mp4, encodé pour le web dans source/films/ (moov en tête,
    sous 25 Mo : gardes de l'assembleur, qui refuse aussi un lecteur sans film). YouTube
    reste un lien secondaire, pour qui veut partager. Sans affiche rendue, `visuel` est
    l'affiche COMPOSÉE, posée sur la vidéo et retirée à la lecture."""
    url, duree, duree_dite = FILMS[oid]
    src = f"{prefixe}films/{oid}.mp4"
    poster = f' poster="{prefixe}rendus/{affiche}"' if affiche else ""
    note = f"""
  <div class="film-note">
    <a class="ou" href="{url}" rel="noopener">also on YouTube <span aria-hidden="true">&#8594;</span></a>
  </div>""" if url else ""
    return f"""<div class="lecteur" data-film="{oid}">
    <video{poster} preload="none" playsinline controls width="1920" height="1080" aria-label="The {genre} of Crusetra {nom}, {duree_dite}">
      <source src="{src}" type="video/mp4">
      <a href="{src}">Download the {genre} of Crusetra {nom} (mp4).</a>
    </video>
    {visuel}<button class="jouer" type="button" aria-label="Play the {genre} of Crusetra {nom}, {duree_dite}"><svg width="30" height="34" viewBox="0 0 30 34" fill="none" aria-hidden="true"><path d="M2 2l26 15L2 32V2z" fill="#e4ecdf"/></svg></button>
    <span class="duree" aria-hidden="true">{duree}</span>
  </div>{note}"""


def liste_films(oid, pr, affiche_film):
    """LES DEUX CARTES sous le lecteur, le film des findings et la démo, pour un outil de DEMOS (sinon rien)."""
    # 29/09 : sur Screening, UN lecteur et deux cartes dessous, le film des findings et la démo ; une carte cliquée
    # change le film du lecteur (script), et sans script chaque carte est un lien vers son mp4 ; 04/10 : Routing aussi
    titre_film, titre_demo = DEMOS.get(oid, ("", ""))
    return f"""
  <div class="liste" role="list" aria-label="Two films" data-nom="{oid.capitalize()}">
    <a class="carte-film est-actif" role="listitem" aria-current="true" href="{pr}films/{oid}.mp4" data-src="{pr}films/{oid}.mp4" data-poster="{pr}rendus/{affiche_film}" data-duree="{FILMS[oid][1]}" data-dite="{FILMS[oid][2]}" data-genre="film" data-yt="{FILMS[oid][0] or ""}">
      <img src="{pr}rendus/{affiche_film}" alt="" width="1920" height="1080"><span class="cf-corps"><span class="cf-e">The film</span><span class="cf-t">{titre_film}</span></span><span class="cf-d">{FILMS[oid][1]}</span></a>
    <a class="carte-film" role="listitem" href="{pr}films/{oid}-demo.mp4" data-src="{pr}films/{oid}-demo.mp4" data-poster="{pr}rendus/affiche-{oid}-demo.jpg" data-duree="{FILMS[oid + "-demo"][1]}" data-dite="{FILMS[oid + "-demo"][2]}" data-genre="demo" data-yt="{FILMS[oid + "-demo"][0] or ""}">
      <img src="{pr}rendus/affiche-{oid}-demo.jpg" alt="" width="1920" height="1080"><span class="cf-corps"><span class="cf-e">The demo</span><span class="cf-t">{titre_demo}</span></span><span class="cf-d">{FILMS[oid + "-demo"][1]}</span></a>
  </div>""" if oid in DEMOS else ""


def film_html(outil):
    """LA PLACE DU FILM d'un outil, la même sur chaque couleur : le titre, le lecteur
    natif et sa durée (table FILMS, 27/09 : les cinq films sont en ligne). Sans affiche
    rendue, l'affiche est COMPOSÉE (nuit de l'outil, robot penché, question)."""
    if outil["id"] not in FILMS_VISIBLES:
        return ""
    if outil.get("affiche"):
        # l'affiche RENDUE, comme le vert : le robot de la couleur, paumes ouvertes,
        # projetant deux chiffres du relevé (etats/affiche-plaque.py + affiche-composer.py)
        affiche, visuel = outil["affiche"], ""
    else:
        affiche = None
        visuel = (f'<span class="affiche" role="img" aria-label="The {outil["nom"]} robot, leaning in, beside the question the film answers">'
                  f'<span class="af-t"><span class="af-eti">Crusetra &#183; {outil["nom"]}</span><span class="af-q">{outil["question"]}</span></span>'
                  f'<img src="{lien(outil, "rendus/" + outil["robots"][0])}" alt=""></span>\n    ')
    pr = outil["prefixe_racine"]
    liste = liste_films(outil["id"], pr, outil.get("affiche") or "affiche-film.jpg")
    return f"""
<section class="film"><div class="colonne">
  <h2 class="h2">Crusetra, explained.</h2>
  <p class="film-duree">{"The film, and the demo" if outil["id"] in DEMOS else "The five " + outil["nom"] + " findings"}</p>
  {lecteur_html(outil["id"], outil["nom"], outil["prefixe_racine"], affiche, visuel)}{liste}
</div></section>
"""


# ═══════════════════ LA CHORÉGRAPHIE AU SCROLL (lot P-C1) ═══════════════════
# Quand rendus/sequences/<prefixe>/manifest.json existe, la page gagne un canevas
# sous les scènes et le script du scrub ; SANS manifeste, les trois morceaux sont
# vides et la page d'aujourd'hui sort octet pour octet — un outil sans séquence
# n'est pas un outil cassé. Le mouvement est validé par Arslane sur le prototype
# du rack (9/09) ; les gardes des séquences (identité, fraîcheur, poids,
# complétude) sont le lot M-C1, dans l'assembleur.

CSS_SCRUB = """
  canvas.scrub{position:absolute;inset:0;width:100%;height:100%;z-index:0}
  .colle.scrub .scene .objet{visibility:hidden}
  /* pendant le mouvement, la fiche et le jalon restent ; les étiquettes et leurs lignes attendent
     que l'objet soit posé (elles pointent des pièces de l'état d'arrivée) */
  .colle.mouv .scene .ap-eti{opacity:0;transition:none}
  .colle.mouv .scene .appels line{stroke-dashoffset:1;transition:none}
  /* les aimants : un point d'accroche au milieu de chaque palier d'arrivée ; « proximity »
     ramène le défilement dessus quand il s'arrête près, et laisse filer sinon */
  html.js{scroll-snap-type:y proximity}
  .sequence .aimant{position:absolute;left:0;width:1px;height:1px;scroll-snap-align:start;pointer-events:none}
  @media (max-width:1080px),(prefers-reduced-motion:reduce){html.js{scroll-snap-type:none}}
  @media (max-width:1080px){canvas.scrub{display:none}}
"""

# Le contrat du geste : p vient du même calcul que surScroll ; k = floor(p·5),
# q = p·5 − k, t = min(1, q / mouvement), image = round(t·(n−1)). La scène k est active
# (fiche, jalon) sur TOUT le palier k ; ses annotations n'apparaissent qu'à l'arrêt
# (q ≥ mouvement), quand l'objet est posé là où elles pointent. Avant le 13/09, rien
# n'était actif pendant le mouvement : 12 positions sur 51 sans fiche ni jalon, mesuré
# au défilement seul, et la relecture disait « sometimes the findings don't appear ».
# Une lecture par image d'animation (rAF), jamais une par événement ; la transition 0
# entière avant le premier dessin, les suivantes derrière, dans l'ordre ; une image
# manquante prend la voisine ; tout échec de la transition 0 rend la page d'aujourd'hui,
# sans erreur en console. Le script tourne APRÈS le JS commun : ses classes gagnent
# dans la même image d'animation (rAF après les écouteurs de scroll, avant la peinture).
JS_SCRUB = """
(() => {
  const M = JSON.parse(document.getElementById("seq-manifeste").textContent);
  const colle = document.querySelector(".colle");
  const seqEl = document.querySelector(".sequence");
  const canevas = document.querySelector("canvas.scrub");
  const scenesS = [...document.querySelectorAll(".scene")];
  const jalonsS = [...document.querySelectorAll(".jalon")];
  if (!colle || !seqEl || !canevas || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const ctx = canevas.getContext("2d");
  // Le palier d'arrivée : la moitié de chaque scène tient la dernière image avec sa fiche
  // (le manifeste dit 0.66 de mouvement ; à l'écran c'était trop court pour « tomber sur la
  // bonne image », Arslane 10/09). Les aimants : un point d'accroche au milieu de chaque
  // palier, le navigateur y ramène le défilement quand il s'arrête à proximité.
  const MOUV = Math.min(M.mouvement, 0.5);
  for (let k = 0; k < M.transitions; k++) {
    const aimant = document.createElement("div");
    aimant.className = "aimant"; aimant.setAttribute("aria-hidden", "true");
    aimant.style.top = "calc(" + ((k + (MOUV + 1) / 2) / M.transitions).toFixed(4) + " * (100% - 100vh))";
    seqEl.appendChild(aimant);
  }
  const nom = (k, i) => M.chemin + M.prefixe + "-seq-0" + (k + 1) + "-" + String(i).padStart(3, "0") + M.ext;
  const T = [];
  let pret = false, mort = false, demande = false, dernier = "";
  const charge = (k, i) => new Promise((r) => {
    const im = new Image();
    im.onload = () => r(im);
    im.onerror = () => r(null);
    im.src = nom(k, i);
  });
  const chargeTransition = async (k) => {
    T[k] = await Promise.all(Array.from({ length: M.n }, (_, i) => charge(k, i)));
    return T[k].some((im) => im !== null);
  };
  const voisine = (k, i) => {
    const t = T[k];
    if (!t) return null;
    for (let d = 0; d < M.n; d++) {
      if (t[i - d]) return t[i - d];
      if (t[i + d]) return t[i + d];
    }
    return null;
  };
  function peindre(force) {
    if (mort || !pret) return;
    if (innerWidth <= 1080) { colle.classList.remove("scrub"); dernier = ""; return; }
    const r = seqEl.getBoundingClientRect();
    const total = r.height - innerHeight;
    const p = Math.min(1, Math.max(0, -r.top / total));
    const brut = Math.min(M.transitions - 1e-9, p * M.transitions);
    const k = Math.floor(brut), q = brut - k;
    const t = Math.min(1, q / MOUV);
    const i = Math.round(t * (M.n - 1));
    const arret = q >= MOUV;
    scenesS.forEach((s, x) => {
      const a = x === k;
      s.classList.toggle("actif", a);
      s.setAttribute("aria-hidden", a ? "false" : "true");
    });
    jalonsS.forEach((j, x) => j.classList.toggle("actif", x === k));
    colle.classList.toggle("mouv", !arret);
    /*
     * UNE TRANSITION QUI N'EST PAS ENCORE ARRIVÉE NE FIGE PLUS L'OBJET.
     *
     * Avant : `if (!im) return` sortait sans rien peindre, et le canevas gardait l'image du
     * palier PRÉCÉDENT. On défilait, le texte changeait, l'objet restait immobile, et rien
     * ne disait pourquoi. Mesuré le 08/09 à 5 Mbit/s, un débit de bureau ordinaire : la
     * deuxième transition arrive à 9 s sur routing, et 48 images sur 120 seulement sont là
     * au bout de douze secondes. C'est là tout le « le scroll n'est pas pratique », et il
     * est d'autant plus long que le jeu d'images est lourd (13 Mo sur routing, 8 sur scoring).
     *
     * Maintenant : on rend la main à l'IMAGE FIXE de la scène, qui existe déjà dans la page
     * et que `.colle.scrub .scene .objet{visibility:hidden}` cachait. On voit donc toujours
     * le bon objet du bon palier, immobile mais juste, et le calcul reprend dès que ses
     * images sont là.
     */
    const im = voisine(k, i);
    if (!im) { colle.classList.remove("scrub"); dernier = ""; return; }
    const cle = k + ":" + i + ":" + canevas.clientWidth;
    if (!force && cle === dernier) return;
    dernier = cle;
    colle.classList.add("scrub");
    const dpr = Math.min(2, devicePixelRatio || 1);
    const lw = Math.round(canevas.clientWidth * dpr), lh = Math.round(canevas.clientHeight * dpr);
    if (canevas.width !== lw || canevas.height !== lh) { canevas.width = lw; canevas.height = lh; }
    const e = Math.min(canevas.width / im.naturalWidth, canevas.height / im.naturalHeight);
    const w = im.naturalWidth * e, h = im.naturalHeight * e;
    ctx.clearRect(0, 0, canevas.width, canevas.height);
    ctx.drawImage(im, (canevas.width - w) / 2, (canevas.height - h) / 2, w, h);
  }
  const auCadre = () => {
    if (demande) return;
    demande = true;
    requestAnimationFrame(() => { demande = false; peindre(false); });
  };
  addEventListener("scroll", auCadre, { passive: true });
  addEventListener("resize", auCadre);
  /*
   * LES TRANSITIONS ARRIVENT PAR PROXIMITÉ AVEC LÀ OÙ ON LIT, pas dans l'ordre des fichiers.
   *
   * L'ordre naïf 1,2,3,4 fait attendre la transition qu'on REGARDE derrière celles qu'on a
   * déjà dépassées : quelqu'un qui descend vite jusqu'au quatrième palier attendait le
   * chargement des deuxième et troisième avant la sienne. On choisit donc à chaque fois la
   * plus proche de la position de lecture, et on repeint dès qu'elle est là.
   */
  const prochaine = () => {
    const r = seqEl.getBoundingClientRect();
    const total = r.height - innerHeight;
    const p = Math.min(1, Math.max(0, -r.top / total));
    const ici = Math.min(M.transitions - 1, Math.floor(p * M.transitions));
    let choix = -1, plusPres = Infinity;
    for (let k = 1; k < M.transitions; k++) {
      if (T[k]) continue;
      const d = Math.abs(k - ici);
      if (d < plusPres) { plusPres = d; choix = k; }
    }
    return choix;
  };
  (async () => {
    if (!(await chargeTransition(0))) { mort = true; return; }
    pret = true;
    peindre(true);
    for (let k = prochaine(); k >= 0; k = prochaine()) {
      await chargeTransition(k);
      peindre(true);
    }
  })();
})();
"""


def sequence_scrub(prefixe):
    """Les trois morceaux du scrub (canevas, CSS, script) quand le manifeste des
    séquences de l'outil existe ; trois chaînes vides sinon — le repli est
    l'ABSENCE des morceaux, pas un script qui se tait, pour que la page sans
    séquence reste celle d'aujourd'hui octet pour octet (témoin cmp du rouge)."""
    chemin = BASE / "rendus" / "sequences" / prefixe / "manifest.json"
    if not chemin.exists():
        return "", "", ""
    m = json.loads(chemin.read_text())
    for cle in ("prefixe", "n", "transitions", "ext", "large", "haut", "mouvement"):
        if cle not in m:
            sys.exit(f"manifest.json de {prefixe} : clé « {cle} » absente ; le scrub ne devine rien")
    if m["prefixe"] != prefixe:
        sys.exit(f"manifest.json : prefixe « {m['prefixe']} » sous le dossier {prefixe}/ : les séquences d'un autre plateau")
    donnees = json.dumps({"prefixe": m["prefixe"], "n": m["n"], "transitions": m["transitions"],
                          "ext": m["ext"], "mouvement": m["mouvement"],
                          "chemin": f"../rendus/sequences/{prefixe}/"}, ensure_ascii=True)
    canevas = f'<canvas class="scrub" width="{m["large"]}" height="{m["haut"]}" aria-hidden="true"></canvas>'
    script = (f'\n<script type="application/json" id="seq-manifeste">{donnees}</script>'
              f'\n<script>{JS_SCRUB}</script>')
    return canevas, CSS_SCRUB, script


_CANEVAS_V, _CSS_SCRUB_V, _SCRUB_V = sequence_scrub(ETATS_PREFIXE["routing"])


def _section_rapport_routing():
    """L'audit du coût d'extraction en service (Routing, produit à prix fixe), page Routing, 30/09 : l'offre lue dans
    offre-routing.json (grille choisie par Arslane le 29/09), la feuille lue dans le rapport exemple rendu par
    batir-rapport-routing.py depuis le relevé réel CORD ; refusé si le scellé du rapport exemple n'est plus celui du
    relevé, ou si un prix du JSON ne se lit pas dans la section."""
    off = json.loads((BASE / "offre-routing.json").read_text())
    ex = json.loads((BASE / "rapports" / "routing-sample-report.json").read_text())
    pub = pathlib.Path.home() / "Documents" / ex["source"]
    rec_p = pub if pub.exists() else pathlib.Path.home() / "Documents" / "cascade-portes" / "routing" / "cord-labels-grouped-measured.json"
    rec = json.loads(rec_p.read_text())
    if rec["empreinte"] != ex["sceau"]:
        sys.exit(f"le rapport exemple Routing porte le scellé {ex['sceau']} mais le relevé porte {rec['empreinte']} : relancer batir-rapport-routing.py")
    if rec["audit"]["cost"]["annual"]["saving"] != ex["economie"] or rec["audit"]["routing"] != ex["routage"]:
        sys.exit("le rapport exemple Routing ne se recompte pas sur son relevé : refusé")
    for f in ("rapports/routing-sample-report.pdf", "rendus/rapport-routing.webp", "rendus/robot-vert-montre.webp",
              "rendus/robot-vert-pese.webp", "rendus/robot-vert-tient.webp"):
        if not (BASE / f).exists():
            sys.exit(f"{f} absent : la section du rapport Routing aurait un trou")
    usd = lambda n: f"${n:,}"
    es, sn, au, tr = off["essai"], off["snapshot"], off["audit"], off["audit_trimestriel"]
    pick = sorted(set(ex["routage"].values()))
    pdf, img = "../rapports/routing-sample-report.pdf", "../rendus/rapport-routing.webp"
    signe = "../rapports/routing-sample-report.html"
    if not ex.get("signe"):
        sys.exit("le rapport exemple Routing n'est pas signé : relancer batir-rapport-routing.py")
    releve = f"{DEPOT_URL}/blob/main/examples/cord-receipts/cord-labels-grouped-measured.json"
    exemple = f"{DEPOT_URL}/tree/main/examples/cord-receipts"
    sujet = "Extraction%20cost%20audit%2C%20free%20trial"
    # 04/10 (audit Routing) : l'entrée « reçus d'abord » et les cinq pas de l'essai gratuit. Chaque chiffre
    # vient du relevé scellé CORD (rec) ou de l'offre (off) ; aucun n'est tapé ici.
    srcs = rec["audit"]["fields"]["total"]["sources"]
    pc = lambda n: f"{srcs[n]['accuracy'] * 100:.1f}%"
    courant, meilleur = rec["audit"]["cost"]["current"]["chain"], pick[0]
    ecart_pts = f"{abs(srcs[meilleur]['accuracy'] - srcs[courant]['accuracy']) * 100:.1f}"
    insep_total = [x for x in rec["audit"]["inseparable"] if x["field"] == "total" and {x["source"], x["against"]} == {courant, meilleur}]
    cmd_grade = (f"npm run grade -- --cases=examples/cord-receipts/cord-labels-grouped.csv --name={courant} "
                 f"--values=examples/cord-receipts/cord-google-values.json --price-per-thousand-documents=100 --out=/tmp/{courant}.json")
    recus = f"""<div class="r-recus">
    <p class="marque-h">Start with receipts</p>
    <p>The public run grades two vendors and our local tiers on {ex["cas"]} real receipts. Grade one vendor's outputs against the labels yourself, with nothing downloaded:</p>
    <code class="r-cmd"><b>$ </b>git clone {DEPOT_URL}
<b>$ </b>cd {DEPOT_URL.rsplit('/', 1)[1]} &amp;&amp; npm ci --ignore-scripts
<b>$ </b>{cmd_grade}</code>
    <p>On those receipts, {meilleur} reads {pc(meilleur)} of totals right and {courant} {pc(courant)}. Our two encoder tiers read {pc("small")} and {pc("large")}; the local tier that competes, gen-4b, reads {pc("gen-4b")}, and it needs Ollama. The local tiers read a text that our macOS OCR produced from the images, so their rates include that OCR's errors.</p>
  </div>"""
    # 05/10 (parcours client) : les cinq pas disent ce que la commande fait vraiment : l'en-tête avec les types de champ (sans
    # type la comparaison est le texte exact, et l'outil refuse une colonne qui ressemble à des montants ou des dates sans
    # --exact), le fichier -with-text.csv que les outils de texte écrivent, tessdata -- --prime une fois (tailles lues dans le
    # manifeste du dépôt, src/tessdata.ts, jamais tapées), la voie des exports bruts, Node 24, la liste à virgules, et « not
    # signed » (le relevé porte une empreinte de contenu ; c'est la page du rapport qui n'est pas signée).
    _tess = (pathlib.Path.home() / "Documents" / "cascade" / "src" / "tessdata.ts").read_text()
    _octets = [int(x.replace("_", "")) for x in re.findall(r"octets:\s*([\d_]+)", _tess)]
    if len(_octets) < 2:
        sys.exit("src/tessdata.ts du dépôt cascade ne porte plus les tailles des deux fichiers de langue : le pas 1 ne peut pas les citer")
    tess_mb = f"{sum(_octets) / 1e6:.1f}"
    essai = f"""<div class="r-essai">
    <p class="marque-h">How the free test goes</p>
    <ol class="r-pas">
      <li><span><b>Label {es["pages"]} pages</b> of one document type in a CSV: an id, the text, then one column per field, each named with its type, as in <code>id,text,total:amount,date:date,vendor:free-text</code>. Without a type the comparison is exact text, so "$1,234.50" and "1234.50" count as different; the tool refuses such a column unless you pass <code>--exact</code>. Write a dash where a document has no such line, and leave the cell empty when you do not know the value. For the text, take what your vendor already returns, <code>npm run text-from-exports -- --cases=your.csv --vendor=&lt;textract|documentai|azure&gt; --exports=&lt;folder&gt;</code>, or read your images offline: once, <code>npm run tessdata -- --prime</code> ({tess_mb} MB of language files), then <code>npm run text-from-images -- --cases=your.csv --images=&lt;folder&gt; --ocr=tesseract --lang=eng</code>. Either one writes <code>your-with-text.csv</code>: use that file in steps 2 and 3. Node 24 or newer. Up to {es["extracteurs"]} extractors.</span></li>
      <li><span><b>Grade each extractor</b> you use or want to compare. We call no vendor: you run each one on your pages, then grade its outputs here. From a JSON of values, <code>{{ "&lt;id&gt;": {{ "&lt;field&gt;": "&lt;value&gt;" }} }}</code>: <code>npm run grade -- --cases=your-with-text.csv --name=&lt;vendor&gt; --values=&lt;its outputs&gt; --price-per-thousand-pages=&lt;your price&gt; --out=&lt;vendor&gt;.json</code>. From raw Textract, Document AI or Azure exports: <code>--vendor=&lt;textract|documentai|azure&gt; --exports=&lt;folder&gt; --mapping=mapping.json</code> in place of <code>--values</code>. The file it writes holds verdicts, no value.</span></li>
      <li><span><b>Measure, with the margin you accept</b>: <code>npm run measure:yours -- --cases=your-with-text.csv --sorties=&lt;vendor&gt;.json,&lt;vendor&gt;.json --current=&lt;the one you run today&gt; --margin=2 --pages-per-year=&lt;your volume&gt;</code>, one <code>--sorties</code> per file or a comma list. Add <code>--no-encoders</code> to compare vendors only, with no download; without it, our local models download once.</span></li>
      <li><span><b>Email the record</b>, the file ending in <code>-measured.json</code> beside your CSV, to {off["contact"]}. It holds counts, a right, wrong or blank verdict per case and field, your file's name and its hash, and the prices you declared: no document, no value. It is the one file you may attach; a price under a vendor contract can be replaced with a list price before you send it.</span></li>
      <li><span><b>You get a one-page PDF back</b> by email within {es["delai_heures"]} hours, from that record. The record carries a content hash; this report is not signed, and the free test stays an internal evaluation under the thirty-day grant. The Snapshot and the Audit come back signed, and include the right to act on the recommendation in your own operations. On our {ex["cas"]}-receipt sample, two vendors {ecart_pts} points apart on totals could not be told apart{(" (" + str(insep_total[0]["discordant"]) + " disagreements, p = " + f"{insep_total[0]['p']:.2f}" + ")") if insep_total else ""}: {es["pages"]} pages separate vendors far apart, and the paid tiers size the sample for close ones.</span></li>
    </ol>
  </div>"""
    html = f"""<section class="rapport" id="report"><div class="colonne">
  <div class="r-grille">
  <div class="r-texte">
    <p class="marque-h">The extraction cost audit</p>
    <h2 class="h2">Find the cheapest extractor for each field of your documents, measured on your own pages.</h2>
    <ol class="r-pas">
      <li><span><b>You label</b> a sample of your own documents: for each field, the value it should read, or a dash when the document has no such line.</span></li>
      <li><span><b>You run the audit</b> on your machine. Your current extractor, the ones you want to compare, and our local models read the same pages. The local models read them as text: the text your current vendor already returns, or an OCR you run.</span></li>
      <li><span><b>You receive</b> a sealed record and a signed report: for each field, the cheapest source that stays within the margin you declare of the best, and the saving at your volume. Sealed means the record carries a content hash, so an edit made after sealing shows. Signed means the report page carries a signature your audit team checks against our public key with <code>node src/verifier-rapport.mjs</code>, like the sample below.</span></li>
    </ol>
  </div>
  <figure class="r-feuille">
    <a href="{pdf}" download><img src="{img}" width="1224" height="1584" loading="lazy" decoding="async"
      alt="First page of the sample report: {ex["cas"]} real receipts, {ex["sources"]} sources on {len(ex["champs"])} fields, all routed to {", ".join(pick)}, saving {usd(ex["economie"])} a year at {ex["volume"]:,} documents."></a>
    <figcaption>sample report &#183; {ex["cas"]} real receipts &#183; sealed {ex["mesure"]} &#183; record {ex["sceau"]} &#183; signed page beside the PDF</figcaption>
  </figure>
  </div>
  {recus}
  <div class="r-offre">
    <div class="r-cols trois">
      <article class="r-col" data-col="snapshot">
        <img class="r-robot" src="../rendus/robot-vert-montre.webp" width="916" height="940" alt="" loading="lazy" decoding="async">
        <p class="r-eti">Snapshot</p>
        <p class="r-montant"><span class="r-n">{usd(sn["prix_usd"])}</span><small>up to {sn["pages"]:,} pages</small></p>
        <p class="r-sous">One document type, measured once and sealed, back within {sn["delai_heures"]} hours.</p>
        <ul class="r-inclus"><li>Up to {sn["champs"]} fields and {sn["extracteurs"]} extractors</li><li>The routing for each field, and the saving at your volume</li><li>What the sample is too small to decide</li><li>Paid in two halves, on signature and on delivery</li></ul>
      </article>
      <article class="r-col haute" data-col="audit">
        <img class="r-robot" src="../rendus/robot-vert-pese.webp" width="1061" height="968" alt="" loading="lazy" decoding="async">
        <p class="r-eti">Audit</p>
        <p class="r-montant"><span class="r-n">{usd(au["prix_usd"])}</span><small>up to {au["pages"]:,} pages</small></p>
        <p class="r-sous">Up to {au["types_document"]} document types, sealed, back within {au["delai_heures"]} hours.</p>
        <ul class="r-inclus"><li>Up to {au["champs"]} fields and {au["extracteurs"]} extractors</li><li>A sample sized to separate sources a few points apart, when they are</li><li>The signed report, its PDF, and the sealed record</li><li>Paid in two halves, on signature and on delivery</li></ul>
      </article>
      <article class="r-col" data-col="trimestriel">
        <img class="r-robot" src="../rendus/robot-vert-tient.webp" width="926" height="963" alt="" loading="lazy" decoding="async">
        <p class="r-eti">Quarterly audit</p>
        <p class="r-montant"><span class="r-n">{usd(tr["prix_usd_an"])}</span><small>a year</small></p>
        <p class="r-sous">The audit measured again {tr["remesures_par_an"]} times a year, as vendors change their models and prices.</p>
        <ul class="r-inclus"><li>{tr["remesures_par_an"]} sealed reports a year</li><li>Each one says what moved since the last</li><li>Paid a year in advance; if you stop, it runs to the end of the year paid, no refund</li></ul>
      </article>
    </div>
  </div>
  <p class="r-note">{off["donnees"]} {off["frais_fournisseurs"]}</p>
  <div class="ouvrir-ligne"><a class="ouvrir" href="mailto:{off["contact"]}?subject={sujet}"><span><span class="ouvrir-t">Try it free on {es["pages"]} of your pages</span>
    <span class="ouvrir-s">One document type and up to {es["extracteurs"]} extractors. Write to {off["contact"]}.</span></span>
    <span class="fl" aria-hidden="true">&#8594;</span></a></div>
  {essai}
  <p class="liens"><a class="lien-e" href="{pdf}" download>Download the sample report <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{signe}">Verify the signed report <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{exemple}">See the labels, the OCR text and the vendor outputs <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{releve}">Open the sealed record <span aria-hidden="true">&#8594;</span></a></p>
</div></section>
<script>
(() => {{
  const f = document.querySelector('.rapport .r-feuille a');
  if (!f || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  f.addEventListener('pointermove', (e) => {{
    const r = f.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
    f.classList.add('suit'); f.style.setProperty('--ry', (x * 7).toFixed(2) + 'deg'); f.style.setProperty('--rx', (-y * 5).toFixed(2) + 'deg');
  }});
  f.addEventListener('pointerleave', () => {{ f.classList.remove('suit'); f.style.removeProperty('--rx'); f.style.removeProperty('--ry'); }});
  for (const c of document.querySelectorAll('.rapport .r-col')) c.addEventListener('pointermove', (e) => {{
    const r = c.getBoundingClientRect(); c.style.setProperty('--mx', (e.clientX - r.left) + 'px'); c.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }});
}})();
</script>"""
    assert "—" not in html, "un cadratin s'est glissé dans la section du rapport Routing"
    for attendu in (usd(sn["prix_usd"]), usd(au["prix_usd"]), usd(tr["prix_usd_an"]), ex["sceau"], off["donnees"], off["frais_fournisseurs"]):
        if attendu not in html:
            sys.exit(f"la section du rapport Routing n'affiche pas « {attendu} » : refusé")
    return html


_SECTION_RAPPORT_ROUTING = _section_rapport_routing()

# the Routing film section, empty while its film is hidden (FILMS_VISIBLES, outil.py)
_SECTION_FILM_ROUTING = f'''<section class="film"><div class="colonne">
  <h2 class="h2">Crusetra, proven in 90 seconds.</h2>
  <p class="film-duree">{"The film, and the demo" if "routing" in DEMOS else "The five Routing findings"}</p>
  {lecteur_html("routing", "Routing", "", "affiche-film.jpg")}{liste_films("routing", "", "affiche-film.jpg")}
</div></section>
''' if "routing" in FILMS_VISIBLES else ""

PAGE = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra &#183; Routing, the extraction cost audit</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra: Routing, the extraction cost audit">
<meta property="og:description" content="Which engine each field of your documents needs: measured on our public test set and on 100 real receipts, rerun on your machine. Nothing reaches us unless you send it.">
<meta property="og:url" content="{SITE_URL}routing/">
<meta property="og:image" content="{SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="Which engine each field of your documents needs: measured on our public test set and on 100 real receipts, rerun on your machine. Nothing reaches us unless you send it.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E%3Cpath d='M16 0v16H0z' fill='%2323543f'/%3E%3C/svg%3E">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">
<script type="application/ld+json">{DONNEES_STRUCTUREES}</script>
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{_CSS_SCRUB_V}{CSS_BARRE_SITE}</style>
{barre_site(courant="HERO.html")}

<main>
<section class="hero">
  <h1 class="h1 entree">See which engine each field of your documents actually needs.</h1>
  <p class="lede entree">A model tier is the size of model a field is sent to, from a plain text pattern up to the largest.<br>
    On our identity-record test set, three of the five fields are read by a text pattern alone, at no cost.</p>
  <div class="commande entree" role="group" aria-label="The first measurement, before any install">
    <code class="ln">git clone {DEPOT_URL}</code>
    <code class="ln">cd {DEPOT_URL.rsplit("/", 1)[1]}</code>
    <code class="ln">node src/premiere-reponse.mjs</code>
    <span class="note">Prints the receipts result from the signed CORD record, then our KYC corpus. Under one second, before npm install.</span>
  </div>
  <div class="cue" aria-hidden="true"><span>scroll</span><span class="fil"></span></div>
</section>

{choix_outils(OUTILS["routing"])}

<section class="sequence" id="findings" aria-label="The five findings">
  <div class="colle">
    {rail_html()}
    <div class="theatre">
      <div class="scenes">{_CANEVAS_V}{scenes}</div>
    </div>
  </div>
</section>
{_SECTION_RAPPORT_ROUTING}

<section class="instrument" data-commun="instrument"><div class="colonne">
  <h2 class="h2">Try the Routing instrument on our public test set.</h2>
  {affiche_html("paliers", LANDING, [], "INSTRUMENT.html", "Crusetra &#183; Routing",
                "See every field, tier, accuracy and cost, live from our public test set. Set the budget and watch the tool choose.",
                "rendus/robot-vert-regarde.webp",
                note=f"Measured on {N_SOCLE:,} held-out records for the rules, small and large tiers, and {N_GEN} for the generative tiers, "
                     "with a ring on the published routing of each field. "
                     f"{CAVEAT_CORPUS} "
                     f"Human accuracy is assumed at {qte(HUMAIN)} % until you measure your own reviewers.", tarif="ENGAGEMENT.html")}
</div></section>

<div class="couture" aria-hidden="true"><div class="colonne">
  <span class="filet"></span>
  <span class="sceau-c">measured, then frozen &#183; content hash {SCEAU}</span>
  <span class="filet"></span>
</div></div>

{_SECTION_FILM_ROUTING}
{menus_html()}
</main>

{pied_html(outil=OUTILS["routing"], sceau=SCEAU, tests=N_TESTS)}

<script>{JS}</script>{_SCRUB_V}
'''

# Routing vit sous routing/ (décision A du 6/09) : chaque lien relatif de la page
# sort du sous-dossier par ../ ; ceux qui le portent déjà (le rideau, via la table)
# ne le reçoivent pas deux fois ; les absolus, les ancres et les data: sont laissés
PAGE = re.sub(r'(href|src|poster)="(?!(?:https?:|#|data:|mailto:|\.\./))([^"]+)"', r'\1="../\2"', PAGE)   # poster : l'affiche du lecteur (27/09)
assert "—" not in PAGE, "un cadratin s'est glissé dans la page"
(BASE / "HERO.html").write_text(PAGE, encoding="utf-8")
print("HERO.html", f"{len(PAGE) / 1e3:.0f} ko")


def batir_accueil():
    """LA PAGE DE LA MARQUE, à la racine (décision A d'Arslane, 6/09) : un héros court
    qui pose la question commune aux instruments, puis le rideau à pans FERMÉS, puis
    les portes de la maison et le pied. Aucun chiffre : les chiffres vivent chez les
    outils, chacun sous son sceau."""
    vivants = outils_vivants()
    n = NOMBRES.get(len(vivants), str(len(vivants)))
    graphe = [ORGANISATION]
    for o in vivants:
        graphe.append({"@type": "SoftwareApplication", "name": f"Crusetra {o['nom']}",
                       "url": f"{SITE_URL}{o['sous_dossier']}",
                       "applicationCategory": "DeveloperApplication",
                       "operatingSystem": "macOS, Linux (Node 24+)",
                       "downloadUrl": o["depot"],
                       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                                  "description": "Thirty-day evaluation on your own records, "
                                                 "granted in the public license."},
                       "publisher": {"@id": ORGANISATION["@id"]}})
    donnees = json.dumps({"@context": "https://schema.org", "@graph": graphe}, ensure_ascii=True)
    # L'ÉVENTAIL (Arslane, 10/09) : les cinq cartes des instruments, les vraies courbes de chaque
    # relevé scellé, dans l'ordre du rideau ; la dernière du paquet est au-dessus
    cartes = []
    for o in vivants:
        if o["id"] == "routing":
            svg = _svg_paliers(LANDING)
        else:
            releve_o = lire_releve_scelle(o["releve"])
            if o["id"] == "dossier":
                svg = _svg_horloge(releve_o)
            else:
                fj = json.loads((BASE / f"findings-{o['id']}.json").read_text())
                svg = _svg_courbes(releve_o, fj["findings"] if isinstance(fj, dict) else fj)
        cartes.append((o["page_hero"], svg, o["etiquette"], o["nom"], o["vif"],
                       {"routing": "#a5f7cb", "screening": "#ffc2c9", "monitoring": "#c3d8ff",
                        "scoring": "#e2d3ff", "dossier": "#e8e6df"}[o["id"]], o["nuit"]))
    # LA MÉTHODE : quatre stations, chaque chiffre lu dans un relevé
    dossier_r = lire_releve_scelle(OUTILS["dossier"]["releve"])
    # the RERUN terminal's commands, written once: the station counts them, the terminal prints them (V4, 6 October
    # 2026: the cd after the clone made three commands four, and a typed « 3 commands » would have stayed)
    depot_routing = OUTILS["routing"]["depot"]
    cmd_accueil = [f"git clone {depot_routing}", f"cd {depot_routing.rsplit('/', 1)[1]}", "npm ci --ignore-scripts",
                   "npm run measure:yours -- --cases=your-file.csv"]
    stations = [
        ("01 · MEASURE", "On our public test set",
         ["Each tool measures every tier on the", "tool&#8217;s own public test set: 1,000", "held-out records for the reader, 60 + 60 pairs,", "42 + 42 cases, 84 files. Each rate carries its confidence interval."],
         f"{N_SOCLE:,} records · {N_GEN} for the generative tiers"),
        ("02 · SEAL", "Hashed, then frozen",
         ["Each record carries its content hash.", "A page checks it before a figure is shown.", "A record that changed after sealing", "is not used."],
         f"content hash {SCEAU_ROUTING[:8]}… (reader)"),
        ("03 · RERUN", "On your own files, on your machine",
         ["One command reruns the whole sweep on", "your records. The report is written next", "to your file, and no data leaves the", "network."],
         f"{len(cmd_accueil)} commands, no account, no upload"),
        ("04 · DOSSIER", "Signed, current, verifiable",
         ["Four reports against five controls:", "present, frozen, signed with a key, fresh,", "and consistent. A reviewer checks the dossier", "from the hashes and signatures alone."],
         f"{dossier_r['couverture']['n']} of {dossier_r['couverture']['sur']} reports · {len(dossier_r['controles']['presents'])} controls"),
    ]
    # LA SCÈNE DE LA MÉTHODE : le gros plan 01 du dossier avec ses étiquettes PUBLIÉES (les mêmes
    # que la page outil, même géométrie, même garde), sur le papier de la maison
    f_dossier = json.loads((BASE / "findings-dossier.json").read_text())["findings"][0]
    img_dossier = BASE / "rendus" / "etats" / f"{SPECS['dossier']['etats']}-01.webp"
    assert img_dossier.exists(), f"gros plan du dossier absent : {img_dossier}"
    lignes, etiquettes = "", ""
    for (ax, ay, lx, ly, txt) in f_dossier["annotations"]:
        verifier_appel(txt, "accueil, méthode, dossier finding 01")
        x1, y1, x2, y2 = MX + lx * IW, ly * IH, MX + ax * IW, ay * IH
        lignes += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" pathLength="1"/><circle cx="{x2:.0f}" cy="{y2:.0f}" r="4"/>'
        etiquettes += f'<span class="ap-eti" style="left:{x1 / 14.20:.1f}%;top:{y1 / 10.0:.1f}%">{txt}</span>'
    scene = (f'<div class="scene actif"><img class="objet" src="rendus/etats/{img_dossier.name}" '
             f'alt="{SPECS["dossier"]["alt_plateau"]}, state {f_dossier["num"]}: {f_dossier["titre"]}">'
             f'<svg class="appels" viewBox="0 0 1420 1000" aria-hidden="true">{lignes}</svg>{etiquettes}</div>')
    terminal = f'''<div class="methode-term" role="group" aria-label="The {({3: 'three', 4: 'four', 5: 'five'})[len(cmd_accueil)]} commands that measure your own records">
        <div class="tb"><i></i><i></i><i></i><span>run it yourself</span></div>
        <div class="tc">{"".join(f"<code>{c}</code>" for c in cmd_accueil)}
          <span class="note">the report is written next to your file, and nowhere else</span></div>
      </div>'''
    # the black page redefines the paper tokens ; the method section gets the REAL paper back,
    # read from the site's own :root block (never retyped, so it cannot drift)
    tokens_papier = re.search(r":root\{(.*?)\}", CSS, re.S).group(1)
    # LE GRAND LIVRE du premier écran (Arslane, 10/09, D1) : les chiffres sont ceux des scènes du
    # routing (SCENES, vérifiées contre l'outil par l'assembleur), le compte du socle et le sceau
    acc_champ = re.sub(r"<[^>]+>", "", SCENES[0]["a"])
    acc_fichier = re.sub(r"<[^>]+>", "", SCENES[0]["b"])
    moins_cher = re.sub(r"<[^>]+>", "", SCENES[1]["b"])   # 04/10 : le chiffre, avec son hypothèse dans le dt ; la cote dit l'hypothèse
    description = ("Crusetra: five instruments, one method. Each tier measured on our public test set, "
                   "the best trade-off read with its interval, rerun on your machine.")
    page = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra &#183; measured instruments for compliance</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra: {n} instruments, one method">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="{description}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E%3Cpath d='M16 0v16H0z' fill='%2323543f'/%3E%3C/svg%3E">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">
<script type="application/ld+json">{donnees}</script>
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_ACCUEIL}{CSS_PIED_SITE}.methode{{{tokens_papier}}}</style>
<header class="barre sur-nuit">
  <a class="marque" href="ACCUEIL.html">CRUSETRA</a>
  <nav aria-label="Site">
    {chr(10).join(f'    <a href="{o["page_hero"]}">{o["nom"]}</a>' for o in vivants).lstrip()}
    <a href="ENGAGEMENT.html">Pricing</a>
    <a href="CONTACT.html">Contact</a>
  </nav>
</header>

<main>
<section class="hero">
  <div class="hero-grille">
    <div class="hero-texte">
      <h1 class="h1 entree">Compliance decisions you can prove.</h1>
      <p class="lede entree">Crusetra turns compliance decisions into measurable evidence: tested against our public test set, reproducible on your own data, and open to inspection.</p>
      <dl class="ledger entree" aria-label="The routing instrument, in figures">
        <div><dt><i class="pt" aria-hidden="true"></i>routing, mean accuracy per field</dt><dd>{acc_champ}</dd></div>
        <div><dt>accuracy per file</dt><dd>{acc_fichier}</dd></div>
        <div><dt>records in our public test set</dt><dd>{N_SOCLE:,}</dd></div>
        <div><dt>file-aimed routing per 100,000 documents, on an assumed price</dt><dd>{moins_cher}</dd></div>
        <div><dt>content hash</dt><dd>{SCEAU_ROUTING}</dd></div>
        <div class="cmd"><dt>rerun on your own files</dt><dd class="c1">node src/premiere-reponse.mjs</dd>
          <small class="c2">{cmd_accueil[0]}</small><small class="c2">{cmd_accueil[1]}</small></div>
      </dl>
    </div>
    {eventail_html(cartes)}
  </div>
</section>

{choix_outils(None)}

<section class="methode" id="method">
  <div class="colonne">
  <h2 class="h2">One method, shared across the tools.</h2>
  <div class="methode-grille">
    {methode_html(stations, extra={"03 · RERUN": terminal})}
    <div>
      <div class="methode-scene">{scene}</div>
      <p class="methode-note">{f_dossier['phrase']}</p>
    </div>
  </div>
  </div>
</section>
</main>

{pied_html()}

<script>{JS}</script>
'''
    assert "—" not in page, "un cadratin s'est glissé dans la page de la marque"
    (BASE / "ACCUEIL.html").write_text(page, encoding="utf-8")
    print("ACCUEIL.html", f"{len(page) / 1e3:.0f} ko")




# ═════════════════════════ LE CATALOGUE : bâtir(outil) ═════════════════════════
# Le vert ci-dessus est la page historique ; depuis la décision du rideau (6/09)
# il porte le deuxième écran comme le rubis, par la même fonction choix_outils.
# Le rubis se bâtit ICI, par la même structure d'écrans, avec les paramètres de
# source/outil.py et les textes du lot S3 (findings-screening.json). Une page
# rouge sans ses données ne se bâtit pas : l'absence est DITE, jamais improvisée.

RUBIS = OUTILS["screening"]
LAPIS = OUTILS["monitoring"]

# ── LES SPÉCIFICITÉS PAR OUTIL de la page héros : tout ce qui n'est ni structure ni
# table d'outil vit ici, pour que le troisième outil soit une ENTRÉE et non une
# quatrième copie de la fonction (la divergence des copies est la maladie que le
# catalogue existe pour fermer). Le rubis garde ses textes À L'OCTET : témoin cmp.
def _refaire_dossier(releve, src, o):
    """Les chiffres de l'onyx, refaits depuis le relevé scellé du Dossier, dans la
    grammaire d'adresses que findings-dossier.json déclare lui-même (lot D3, d950517) :
    {cle, champ} lit releve[cle][champ] (mesure "longueur" en prend la taille) ;
    {compte-verdicts: {controle, tenu}} compte les verdicts de ce contrôle et de ce
    tenu à travers les questions ; {compte-questions: {etat}} compte les questions à
    cet état ; {question, champ} lit releve["questions"][question][champ], le champ
    d'UNE question (lot D3 post-signatures, 9d62c47 : « 16 days since the oldest
    measurement, routing » est questions.routing.joursDepuis, pas un compte).
    Une adresse inconnue est un refus nommé, jamais un zéro silencieux."""
    if "cle" in src:
        v = releve[src["cle"]][src["champ"]]
        if src.get("mesure") == "longueur":
            v = len(v)
        return [str(v)]
    if "question" in src:
        q = releve["questions"].get(src["question"])
        if q is None or src["champ"] not in q:
            sys.exit(f"findings-dossier.json : {src} n'existe pas dans le relevé scellé du Dossier "
                     f"(questions : {', '.join(releve['questions'])}) ; la fiche cite un chiffre "
                     "que le relevé ne porte pas")
        return [str(q[src["champ"]])]
    if "compte-verdicts" in src:
        c = src["compte-verdicts"]
        return [str(sum(1 for q in releve["questions"].values()
                        for verd in q.get("verdicts") or []
                        if verd["controle"] == c["controle"] and verd["tenu"] is c["tenu"]))]
    if "compte-questions" in src:
        e = src["compte-questions"]
        return [str(sum(1 for q in releve["questions"].values() if q.get("etat") == e["etat"]))]
    sys.exit(f"findings-dossier.json : adresse inconnue {src} ; la grammaire du fichier "
             "connaît cle/champ, compte-verdicts et compte-questions")


def _table_dossier(spec, releve, findings):
    """La table du héros onyx : les questions de la chaîne contre les cinq contrôles du
    contrat, lues du relevé scellé. Pas de palier ni de seuil ici : la cellule marquée
    d'une ligne est l'état atteint SANS TROU dans l'ordre du contrat ; une ligne sans
    relevé public est dite non jugée, jamais devinée."""
    ordre = releve["controles"]["presents"]
    tetes = "".join(f"<th scope='col'>{c}</th>" for c in ordre)
    lignes = ""
    for nom_q, q in releve["questions"].items():
        if not q.get("present"):
            lignes += (f"<tr><th scope='row'>{nom_q}</th><td class='cell' colspan='{len(ordre)}'>"
                       f"<small>no public test set yet: nothing judged, and said</small></td></tr>")
            continue
        verd = {v["controle"]: v["tenu"] for v in q.get("verdicts", [])}
        etat = q.get("etat")
        cells = ""
        for c in ordre:
            if c not in verd:
                cells += "<td class='cell'><small>not judged</small></td>"
            elif verd[c]:
                marque = " choisi" if c == etat else ""
                cells += f"<td class='cell{marque}'><span>&#10003;</span><br><small>held</small></td>"
            else:
                cells += "<td class='cell'><span>&#215;</span><br><small>not held</small></td>"
        lignes += f"<tr><th scope='row'>{nom_q}</th>{cells}</tr>"
    cv, rg = releve["couverture"], releve["reglages"]
    note = (f"{cv['n']} of the {cv['sur']} questions carry a public test set. In each row the "
            "marked cell is the state reached with no gap in the contract&#8217;s order; a row "
            "without one reaches none, and the record states this. The declared validity period is "
            f"{rg['rythmeJours']} days, as of {rg['auJour']}.")
    return f'''<div class="t-scroll"><table class="routage">
      <caption class="sr">{spec["table_caption"]}</caption>
      <thead><tr><th scope="col">{spec["table_ligne"]}</th>{tetes}</tr></thead><tbody>{lignes}</tbody></table></div>
      <p class="t-note">{note}</p>'''


# le nom courant du jeu de chaque outil : « generated pairs / cases / files », pour que
# la note d'affiche ne soit pas la même phrase sur trois pages (panel, 13/09)
_NOM_JEU = {"matcher": "pairs", "scenario": "cases", "factor": "files", "question": "reports"}

SPECS = {
    "screening": dict(
        lot="S3",
        etats=ETATS_PREFIXE["screening"],
        alt_plateau="The sieve tower",
        palette=PALETTE_RUBIS, nuit=NUIT_RUBIS,
        titre="Crusetra Screening &#183; sanctions screening audit",
        og_titre="Crusetra Screening: which way of comparing names, and where to set the bar",
        description="A sanctions-screening audit: which way of comparing names, and where you set "
                    "the bar, measured on your own alert history.",
        app="Crusetra Screening",
        app_desc="A sanctions-screening audit: which way of comparing names, and where you "
                 "set the bar, measured on your own alert history. ",
        offre="Thirty-day evaluation on your own alert history, granted in the public license.",
        h1="See what your screening catches, and what it flags incorrectly.",
        lede="A screening threshold is the score above which two names count as a match.<br>\n    Crusetra Screening compares names seven ways, at every threshold, over alerts your analysts already closed.",
        aria_commande="The measurement on your own alert history",
        commandes=["npm ci --ignore-scripts", "npm run measure:yours -- --alerts=your-alerts.csv"],
        note_commande="Your alert history, measured on your machine.",
        instrument_h2="See what each threshold costs you.",
        instrument_page="INSTRUMENT-SCREENING.html",
        instrument_eti="Crusetra &#183; Screening",
        instrument_sub="Each way of comparing names, at each threshold: the real matches it catches, and the false alerts it raises. A false alert is a name flagged as a match that is not one, and each one costs an analyst the time to close it. Live from our public test set.",
        annexe_methode=("Method &amp; what is measured", "What the method measures, and what it does not.",
                        "ANNEXE-SCREENING-METHODE.html"),
        annexe_securite=("Security &amp; data handling", "The lists, the checksum, and what stays on your machine.",
                         "ANNEXE-SCREENING-SECURITE.html"),
        icone_prefixe="objet-screening",
        table_ligne="matcher",
        table_ligne_nom="way of comparing names",
        table_caption="What each way of comparing names catches, over false alerts, at each threshold, on the pairs an AI agent wrote for us",
        table_note_unites='Measured on {nMatch} matching pairs and {nDifferent} near-matches\n      an AI agent wrote for us',
    ),
    "monitoring": dict(
        lot="L5-textes",
        etats=ETATS_PREFIXE["monitoring"],   # UNE source : outil.py (la divergence bassins/rack a failli faire attendre manques() pour toujours)
        alt_plateau="The surveillance rack",
        palette=PALETTE_LAPIS, nuit=NUIT_LAPIS,
        titre="Crusetra Monitoring &#183; transaction monitoring audit",
        og_titre="Crusetra Monitoring: which scenarios catch real cases",
        description="A transaction-monitoring audit: which scenarios catch real cases and which "
                    "only make work, measured on the cases your analysts already closed.",
        app="Crusetra Monitoring",
        app_desc="A transaction-monitoring audit: which scenarios catch real cases and which "
                 "only make work, measured on the cases your analysts already closed. ",
        offre="Thirty-day evaluation on your own dispositioned alerts, granted in the public license.",
        h1="See what your scenarios catch, and what they flag incorrectly.",
        lede="A scenario's threshold is the score above which it raises an alert.<br>\n    Crusetra Monitoring runs seven scenarios at every threshold, over the alerts your analysts already closed.",
        aria_commande="The measurement on your own dispositioned alerts",
        commandes=["npm ci --ignore-scripts",
                   "npm run measure:yours -- --alerts=your-alerts.csv --transactions=your-transactions.csv"],
        note_commande="Your dispositioned alerts, measured on your machine.",
        instrument_h2="Read what a threshold change costs.",
        instrument_page="INSTRUMENT-MONITORING.html",
        instrument_eti="Crusetra &#183; Monitoring",
        instrument_sub="Each scenario at each threshold: the suspicious cases it catches, and the false alerts it raises. A false alert is a case flagged that turns out to be nothing, and each one costs an analyst the time to close it. Live from our public test set.",
        annexe_methode=("Method &amp; what is measured", "What the method measures, and what it does not.",
                        "ANNEXE-MONITORING-METHODE.html"),
        annexe_securite=("Security &amp; data handling", "What is rebuilt, what is assumed, and what stays on your machine.",
                         "ANNEXE-MONITORING-SECURITE.html"),
        icone_prefixe="objet-monitoring",
        table_ligne="scenario",
        table_ligne_nom="scenario",
        table_caption="What each scenario catches, over false alerts, at each threshold, on the cases we wrote",
        table_note_unites='Measured on {nMatch} suspicious cases and {nDifferent} benign cases\n      we wrote',
    ),
    "scoring": dict(
        lot="A-L5-textes",
        etats=ETATS_PREFIXE["scoring"],
        alt_plateau="The shelving of weights",
        palette=PALETTE_AMETHYSTE, nuit=NUIT_AMETHYSTE,
        titre="Crusetra Scoring &#183; customer risk rating audit",
        og_titre="Crusetra Scoring: which risk factors separate risky from quiet",
        description="A customer risk-rating audit: which risk factors separate a risky customer "
                    "from a quiet one, measured on your own periodic-review outcomes.",
        app="Crusetra Scoring",
        app_desc="A customer risk-rating audit: which risk factors separate a risky customer "
                 "from a quiet one, measured on your own periodic-review outcomes. ",
        offre="Thirty-day evaluation on your own review outcomes, granted in the public license.",
        h1="See which risk factors separate a risky customer from a quiet one.",
        lede="A factor's threshold is the score above which it pushes a customer up a rating.<br>\n    Crusetra Scoring runs seven factors at every threshold, over the reviews your analysts already decided.",
        aria_commande="The measurement on your own periodic-review outcomes",
        commandes=["npm ci --ignore-scripts",
                   "npm run measure:yours -- --customers=your-customers.csv --reviews=your-reviews.csv"],
        note_commande="Your review outcomes, measured on your machine.",
        instrument_h2="See what each factor and threshold gives you.",
        instrument_page="INSTRUMENT-SCORING.html",
        instrument_eti="Crusetra &#183; Scoring",
        instrument_sub="Each risk factor at each threshold: the risky customers it catches, and the quiet ones it flags. Each quiet customer flagged costs a reviewer the time of an extra review. Live from our public test set.",
        annexe_methode=("Method &amp; what is measured", "What the method measures, and what it does not.",
                        "ANNEXE-SCORING-METHODE.html"),
        annexe_securite=("Security &amp; data handling", "The tables, the checksum, and what stays on your machine.",
                         "ANNEXE-SCORING-SECURITE.html"),
        icone_prefixe=ICONES_PREFIXE["scoring"],
        table_ligne="factor",
        table_ligne_nom="risk factor",
        table_caption="What each risk factor catches, over false alerts, at each threshold, on the files we wrote",
        table_note_unites='Measured on {nMatch} escalated files and {nDifferent} files kept at their\n      rating, all written by us',
    ),
    "dossier": dict(
        lot="D3",
        etats=ETATS_PREFIXE["dossier"],
        alt_plateau="The five checks",
        palette=PALETTE_ONYX, nuit=NUIT_ONYX,
        titre="Crusetra Dossier &#183; the assembled audit trail",
        og_titre="Crusetra Dossier: is the whole chain measured, sealed and fresh",
        description="One dossier over the suite&#8217;s four sealed answers: coverage, seals, "
                    "signatures, freshness and coherence, verified on your machine. ",
        app="Crusetra Dossier",
        app_desc="One dossier over the suite&#8217;s four sealed answers: coverage, "
                 "seals, signatures, freshness and coherence, verified on your "
                 "machine.",
        offre="Thirty-day evaluation on your own signed reports, granted in the public license.",
        h1="Check each report: present, sealed, signed, fresh, consistent.",
        lede="A reviewer asks whether the whole chain still holds.<br>\n    The Dossier reads the four reports and checks that each one is present, frozen, fresh, signed with a key you can check, and consistent with the others.",
        aria_commande="The dossier over your own signed reports",
        commandes=["npm ci --ignore-scripts",
                   "npm run dossier -- --reports=a-measured.json,b-measured.json"],
        note_commande="Your signed reports, read on your machine.",
        instrument_h2="Read the whole chain in one table.",
        instrument_page="INSTRUMENT-DOSSIER.html",
        instrument_eti="Crusetra &#183; Dossier",
        instrument_sub="The four questions against the five controls, with their states, signatures and dates, live from our public test set.",
        annexe_methode=("Method &amp; what is verified", "What the five controls hold, and what a gap means.",
                        "ANNEXE-DOSSIER-METHODE.html"),
        annexe_securite=("Security &amp; data handling", "What is read, what is derived, and what stays on your machine.",
                         "ANNEXE-DOSSIER-SECURITE.html"),
        icone_prefixe=ICONES_PREFIXE["dossier"],
        table_ligne="question",
        table_caption="State reached by each question of the chain under the contract&#8217;s five controls, on our public test sets",
        table=_table_dossier,
        refaire=_refaire_dossier,
    ),
}


def _etats_dispo(spec):
    """Les cinq états du plateau de l'outil, fournis par le chef. Tant qu'ils manquent,
    la page se bâtit sur l'image verte AVEC un commentaire « placeholder » que
    l'assembleur refuse en production : la garde d'abord, l'image ensuite."""
    return all((BASE / "rendus" / "etats" / f"{spec['etats']}-0{i}.webp").exists() for i in range(1, 6))


def _image_etat_outil(o, spec, i):
    if _etats_dispo(spec):
        return lien(o, f"rendus/etats/{spec['etats']}-0{i}.webp"), ""
    return (lien(o, f"rendus/etats/objet-0{i}.webp"),
            f"<!-- placeholder: {spec['etats']}-0{i}.webp pending, green plateau shown -->")


def _icone_tuile(o, spec, nom):
    """L'icône 3D d'une tuile, dans l'accent de l'outil ; absente, l'icône VERTE du
    même objet la remplace avec le marqueur que l'assembleur refuse en prod."""
    voulu = BASE / "rendus" / "etats" / f"{spec['icone_prefixe']}-{nom}.webp"
    if voulu.exists():
        return lien(o, f"rendus/etats/{spec['icone_prefixe']}-{nom}.webp"), ""
    return (lien(o, f"rendus/etats/objet-{nom}.webp"),
            f"<!-- placeholder: {spec['icone_prefixe']}-{nom}.webp pending, green icon shown -->")


def _scene_outil(o, spec, i, f):
    """La scène d'un outil du catalogue : même squelette que scene_html, données du lot des textes."""
    lignes, etiquettes = "", ""
    appels_f = f.get("annotations", [])
    if len(appels_f) < 2:
        sys.exit(f"{o['id']}, finding {f.get('num', i + 1)} : {len(appels_f)} annotation(s) ; chaque plateau porte "
                 "ses explications en transparence, sur toutes les couleurs (deux au moins)")
    for (ax, ay, lx, ly, txt) in appels_f:
        verifier_appel(txt, f"{o['id']}, finding {f.get('num', i + 1)}")
        x1, y1 = MX + lx * IW, ly * IH
        x2, y2 = MX + ax * IW, ay * IH
        lignes += (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" pathLength="1"/>'
                   f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="4"/>')
        etiquettes += f'<span class="ap-eti" style="left:{x1 / 14.20:.1f}%;top:{y1 / 10.0:.1f}%">{txt}</span>'
    appels = f'<svg class="appels" viewBox="0 0 1420 1000" aria-hidden="true">{lignes}</svg>{etiquettes}'
    img, marque = _image_etat_outil(o, spec, i + 1)
    return f"""
    <div class="scene{' actif' if i == 0 else ''}" id="scene-{i}" data-i="{i}">{marque}
      <img class="objet" src="{img}"
        alt="{spec['alt_plateau']}, state {f['num']}: {f['titre']}">
      {appels}
      <figure class="fiche">
        <figcaption class="fiche-t"><span>finding {f['num']}</span><span class="ft-cote">{f['cote']}</span></figcaption>
        <p class="fiche-phrase">{f['phrase']}</p>
        <div class="paire">
          <div class="val"><span class="chiffre pale-v">{f['a']}</span><span class="leg">{f['leg_a']}</span></div>
          <div class="val"><span class="chiffre vert-v">{f['b']}</span><span class="leg">{f['leg_b']}</span></div>
        </div>
      </figure>
    </div>"""


def _rail_outil(o, spec, findings):
    items = "".join(
        f"""<li><button class="jalon{' actif' if i == 0 else ''}" data-i="{i}" aria-label="Go to finding {f['num']}: {f['titre']}">
        <img class="j-vig" src="{_image_etat_outil(o, spec, i + 1)[0]}" alt="">
        <span class="j-num">{f['num']}</span><span class="j-corps"><span class="j-titre">{f.get("rail", f["titre"])}</span>
        <span class="j-cote">{f['cote']}</span></span></button></li>""" for i, f in enumerate(findings))
    return f'<nav class="rail" aria-label="Findings"><span class="jauge" aria-hidden="true"><i></i></span><ul>{items}</ul></nav>'


def _note_outil(spec, releve, findings):
    """La base de la mesure sous l'affiche (la grille la portait ; l'affiche la garde, sinon la
    page ne dit plus sur combien de paires les chiffres tiennent) : les effectifs du relevé, la
    cellule retenue par la règle de l'outil quand elle existe."""
    src = findings[2].get("source", {}).get("a") or {} if len(findings) > 2 else {}
    palier_f, seuil_f = src.get("palier"), src.get("seuil")
    auth = releve["authored"]
    unites = spec["table_note_unites"].format(
        nMatch=auth.get("nMatch", auth.get("nSuspicious", auth.get("nEscalated"))),
        nDifferent=auth.get("nDifferent", auth.get("nBenign", auth.get("nMaintained"))))
    champ_cite = src.get("champ", "taux")
    # deux phrases au plus, sur toute la largeur de l'affiche (Arslane, 13/09)
    if palier_f and champ_cite == "taux":
        choix = f"with a ring on the cell the tool picks by default, {palier_f} at {seuil_f}"
    elif palier_f:
        choix = f"and the marked cell, {palier_f} at {seuil_f}, comes closest to the 90% floor we set, which none reaches"
    else:
        choix = "and no setting reaches the 90% floor we set"
    return (f"{unites}, at every threshold, {choix}. "
            f"Generated {_NOM_JEU[spec['table_ligne']]} are counted on their own, and the live instrument shows them.")


def _table_outil(spec, releve, findings):
    """La grille de l'outil sur son héros, comme le vert montre la sienne : chaque palier
    présent, à sept seuils dont celui de la frontière quand elle EXISTE, rappel sur
    fausses alertes, tout lu dans le relevé scellé. La cellule de la frontière vient du
    finding 03 (source.a) quand il en cite une ; la règle de l'outil peut n'en retenir
    AUCUNE (le bleu à 0,90 sur les cas écrits) — alors aucune cellule n'est marquée, et
    la note le dit au lieu de laisser deviner."""
    src = findings[2].get("source", {}).get("a") or {}
    palier_f, seuil_f = src.get("palier"), src.get("seuil")
    seuils = sorted({"0.50", "0.60", "0.70", "0.80", "0.90", "1.00"} | ({seuil_f} if seuil_f else set()), key=float)
    auth = releve["authored"]
    tetes = "".join(f"<th scope='col'>{s}</th>" for s in seuils)
    lignes = ""
    for p in releve["paliers"]["presents"]:
        cells = ""
        for s in seuils:
            c = auth["tables"][p][s]
            choisi = " choisi" if (palier_f and (p, s) == (palier_f, seuil_f)) else ""
            cells += (f"<td class='cell{choisi}'><span>{c['rappel']['taux'] * 100:.0f}<small>%</small></span>"
                      f"<br><small>{c['fauxPositifs']['taux'] * 100:.0f}<small>%</small></small></td>")
        lignes += f"<tr><th scope='row'>{p}</th>{cells}</tr>"
    unites = spec["table_note_unites"].format(
        nMatch=auth.get("nMatch", auth.get("nSuspicious", auth.get("nEscalated"))),
        nDifferent=auth.get("nDifferent", auth.get("nBenign", auth.get("nMaintained"))))
    champ_cite = (findings[2].get("source", {}).get("a") or {}).get("champ", "taux")
    if palier_f and champ_cite == "taux":
        frontiere = (f"The marked cell is the tool&#8217;s best trade-off under its\n      default rule, {palier_f} at {seuil_f}.")
    elif palier_f:
        # la fiche 03 cite une BORNE (champ « bas ») : la cellule marquée est la plus forte
        # borne basse, pas un meilleur compromis : la règle de l'outil ne retient rien au plancher
        frontiere = (f"The marked cell, {palier_f} at {seuil_f}, is the surest of the seven."
                     "\n      Under its default rule the tool keeps no cell at the 90% floor on these"
                     "\n      cases, and the live instrument shows the same reading.")
    else:
        frontiere = ("Under its default rule, the tool keeps no cell at the 90% floor on these"
                     "\n      cases, and the live instrument shows the surest one instead.")
    return f'''<div class="t-scroll"><table class="routage">
      <caption class="sr">{spec["table_caption"]}</caption>
      <thead><tr><th scope="col">{spec["table_ligne"]}</th>{tetes}</tr></thead><tbody>{lignes}</tbody></table></div>
      <p class="t-note">{unites}: what each {spec.get("table_ligne_nom", spec["table_ligne"])} catches on top, and false alerts below. {frontiere} Generated {_NOM_JEU[spec["table_ligne"]]} are counted on their own, and the live instrument shows them.</p>'''



def _section_entites(o):
    """La section « Company and vessel names » de la page Screening, forme M4F validée par Arslane le 28/09 :
    trois populations lues dans le relevé scellé des entités (releve-entites.json, scellé ET signé dans l'outil),
    chaque compte refait depuis sa cellule et refusé s'il ne se refait pas ; la date, le commit et le scellé
    viennent du relevé ; les liens mènent au registre des verdicts et au relevé dans le dépôt public."""
    if "releve_entites" not in o:
        return ""
    f = json.loads((BASE / "findings-entites.json").read_text())
    R = lire_releve_scelle(o["releve_entites"])
    if f.get("sceau") != R["empreinte"]:
        sys.exit(f"findings-entites.json cite le scellé {f.get('sceau')} mais releve-entites.json porte "
                 f"{R['empreinte']} : les textes ont dérivé du relevé, section à resceller")
    # LE RÉSULTAT DE TÊTE EST LE VERDICT SUR DE VRAIS NOMS (registre GLEIF), pas le jeu écrit par un agent : ses comptes se
    # lisent dans la sortie du verdict, telle que l'outil l'a écrite, à l'empreinte que findings-entites.json cite ; une
    # sortie qui a bougé, ou une ligne qui ne se relit pas, refuse la page.
    g = f["gleif"]
    brut = (o["outil_chemin"] / g["fichier"]).read_bytes()
    if hashlib.sha256(brut).hexdigest() != g["sha256"]:
        sys.exit(f"findings-entites.json cite {g['fichier']} à l'empreinte {g['sha256'][:12]}… mais le fichier de l'outil en porte une autre : section à relire")
    def ligne_du_verdict(etiquette):
        m = re.search(r"^\s*" + re.escape(etiquette) + r"\s+strong\s+(\d+)/(\d+)\s+[\d.]+ % \[([\d.]+)-([\d.]+) %\]\s+possible\s+(\d+)/(\d+)\s+[\d.]+ % \[([\d.]+)-([\d.]+) %\]\s*$",
                      brut.decode("utf-8"), re.M)
        if not m:
            sys.exit(f"{g['fichier']} n'a pas de ligne « {etiquette} » lisible : refusé")
        fn, fs, fb, fh, pn, ps, pb, ph = m.groups()
        if fs != ps:
            sys.exit(f"{g['fichier']}, ligne « {etiquette} » : deux dénominateurs")
        return int(fn), int(pn), int(fs), (fb, fh), (pb, ph)
    vf, vp, sur_v, iv_f, iv_p = ligne_du_verdict("same-name")
    ff, fp, sur_f, if_f, if_p = ligne_du_verdict("TOTAL different")
    ia = R["verdictRealiste"]["fort"]  # le jeu écrit par un agent, plus bas dans la note
    livre = R["livres"][1]
    forts, possibles, lignes = livre["forts"], livre["possibles"], livre["lignes"]
    sans = livre["sansCorrespondance"]
    if forts + possibles + sans != lignes:
        sys.exit("le livre ne se recompte pas : forts + possibles + sans candidat != lignes")
    # Crusetra V4, 6 October 2026: the book was screened on the lists of ITS day (seven on 4 October), while the report
    # section of the same page names the ten of today. The sentence reads the count and the day from the book's own
    # sealed record, so it stays true when the book is screened again on more lists.
    rec_livre = lire_releve_scelle(o["outil_chemin"] / livre["releve"])
    if rec_livre["empreinte"] != livre["sceau"]:
        sys.exit(f"releve-entites.json cite le livre {livre['sceau']} mais {livre['releve']} porte {rec_livre['empreinte']} : refusé")
    EN_LETTRES_L = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    n_l = len(rec_livre["listes"])
    listes_livre = EN_LETTRES_L.get(n_l, str(n_l))
    a_m_j = [int(x) for x in rec_livre["emisLe"][:10].split("-")]
    jour_livre = f"{a_m_j[2]} " + ("January February March April May June July August September October November "
                                   "December").split()[a_m_j[1] - 1]
    pct = lambda n, d: f"{100 * n / d:.0f}"
    def grille(n, classe):
        return '<div class="grille" aria-hidden="true">' + "".join(f'<i class="{classe(k)}"></i>' for k in range(n)) + "</div>"
    pops = [
        (f["populations"][0].format(sur=sur_v), f"{pct(vf, sur_v)}<small>%</small>",
         grille(sur_v, lambda k: "f" if k < vf else ("p" if k < vp else "")),
         f'<span><i class="f"></i>{vf} found at the strong level, {pct(vf, sur_v)} % [{iv_f[0]}-{iv_f[1]}]</span>'
         f'<span><i class="v"></i>{vp - vf} more at the possible level, {vp} in all, {pct(vp, sur_v)} % [{iv_p[0]}-{iv_p[1]}]</span>'
         f'<span><i></i>{sur_v - vp} missed at both levels</span>'),
        (f["populations"][1].format(sur=f"{sur_f:,}"), f"{ff}",
         grille(sur_f, lambda k: "f" if k < ff else ("p" if k < fp else "")),
         f'<span><i class="f"></i>{ff} of {sur_f:,} raised a strong alert [{if_f[0]}-{if_f[1]} %]</span>'
         f'<span><i class="v"></i>{fp} raised a possible alert [{if_p[0]}-{if_p[1]} %]</span>'),
        (f["populations"][2].format(lignes=f"{lignes:,}", listes=listes_livre, jour=jour_livre), f"{forts + possibles}<small>/{lignes}</small>",
         grille(lignes, lambda k: "f" if k < forts else ("p" if k < forts + possibles else "")),
         f'<span><i class="f"></i>{forts} strong</span><span><i class="v"></i>{possibles} possible</span><span><i></i>{sans} with no candidate</span>'),
    ]
    note = f["note"].format(date_gleif=g["date"], manques=sur_v - vp, sur=sur_v, tiers=pct(sur_v - vp, sur_v),
                            ia_trouves=ia["trouves"]["n"], ia_sur=ia["trouves"]["sur"], ia_fausses=ia["fausses"]["n"], ia_sur_f=ia["fausses"]["sur"])
    blocs = "".join(f'''<div class="pop">
    <div class="tete"><p>{texte}</p><span class="chiffre">{chiffre}</span></div>{g}<p class="cle">{cle}<span class="compteur" aria-live="polite"></span></p></div>'''
                    for texte, chiffre, g, cle in pops)
    depot = o["depot"].rstrip("/")
    html = f'''<section class="entites" id="companies"><div class="colonne">
  <p class="marque-h">Company and vessel names</p>
  <h2 class="h2">{f["titre"]}</h2>
  <div class="pops">{blocs}</div>
  <p class="note">{note}</p>
  <p class="liens"><a class="lien-e" href="{depot}/blob/main/verification/GLEIF.md">Read the four verdicts on real names <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{depot}/blob/main/releve-entites.json">Open the sealed record <span aria-hidden="true">&#8594;</span></a></p>
  <span class="sceau-l">measured {R["date"]} at commit {R["commit"]} &#183; sealed and signed &#183; content hash {R["empreinte"]}</span>
</div></section>
<script>
for (const pop of document.querySelectorAll('.entites .pop')) {{
  const g = pop.querySelector('.grille'), c = pop.querySelector('.compteur'), marks = [...g.children], total = marks.length;
  g.addEventListener('pointermove', (e) => {{
    const cible = e.target.closest('i'); if (!cible) return;
    const n = marks.indexOf(cible) + 1;
    marks.forEach((m, i) => m.classList.toggle('lu', i < n));
    const lit = marks.slice(0, n).filter((m) => m.classList.contains('v') || m.classList.contains('f') || m.classList.contains('p')).length;
    c.textContent = n + ' of ' + total + ' counted \u00b7 ' + lit + ' lit';
    pop.classList.add('suivi');
  }});
  g.addEventListener('pointerleave', () => {{ marks.forEach((m) => m.classList.remove('lu')); pop.classList.remove('suivi'); }});
}}
</script>
<div class="couture" aria-hidden="true"><div class="colonne">
  <span class="filet"></span>
  <span class="sceau-c">company and vessel names &#183; measured, then frozen &#183; content hash {R["empreinte"]}</span>
  <span class="filet"></span>
</div></div>'''
    assert "\u2014" not in html, "un cadratin s'est glissé dans la section des entités"
    for attendu in (f"{pct(vf, sur_v)}<small>%</small>", f">{ff}<", f"{forts + possibles}<small>/{lignes}</small>", f"{vf} found at the strong level",
                    f"{vp} in all", f"{sur_v - vp} missed at both levels", f"{fp} raised a possible alert", f"{sans} with no candidate",
                    f"{ia['trouves']['n']} of {ia['trouves']['sur']} true pairs", g["date"]):
        if attendu not in html:
            sys.exit(f"la section des entités n'affiche pas le chiffre refait « {attendu} » : refusé")
    return html


def _section_rapport(o):
    """Le rapport de criblage en service (produit A), page Screening, 29/09 : l'offre lue dans offre-screening.json
    (grille B choisie par Arslane le 29/09), la feuille lue dans le rapport exemple rendu par batir-rapport-exemple.py
    depuis le relevé PUBLIC de l'outil ; refusé si le scellé du rapport exemple n'est plus celui du relevé.
    Les prix, dans la langue de la page des tarifs (retouche du 29/09) : deux colonnes, puis le curseur de la taille
    de la liste. Les constantes du script sont écrites depuis le JSON ; l'état au repos (500 noms, au mois) est
    calculé ici par la même règle, et chaque montant du JSON doit se lire dans la page servie."""
    if o["id"] != "screening":
        return ""
    off = json.loads((BASE / "offre-screening.json").read_text())
    ex = json.loads((BASE / "rapports" / "screening-sample-report.json").read_text())
    rec = json.loads((pathlib.Path.home() / "Documents" / ex["source"]).read_text())
    if rec["empreinte"] != ex["sceau"]:
        sys.exit(f"le rapport exemple porte le scellé {ex['sceau']} mais le relevé public porte {rec['empreinte']} : "
                 "relancer batir-rapport-exemple.py")
    if (ex["forts"], ex["possibles"], ex["sans"]) != (rec["totaux"]["forts"], rec["totaux"]["possibles"], rec["totaux"]["sansCorrespondance"]):
        sys.exit("le rapport exemple ne se recompte pas sur son relevé : refusé")
    # 05/10 (parcours client) : le PDF servi est le RENDU D'UNE PASSE FRAÎCHE du même fichier au matcher courant (le relevé
    # commité n'est ni rescellé ni re-signé). La fiche nomme les deux scellés, et le relevé rendu est servi à côté du PDF
    # pour que le scellé nommé se vérifie. Même fichier (SHA-256) et mêmes comptes, sinon la fiche décrirait deux rapports.
    rendu = ex.get("rendu")
    if not rendu:
        sys.exit("le rapport exemple n'a pas de passe fraîche (clé « rendu ») : relancer batir-rapport-exemple.py --record <passe>.screening.json")
    frais = json.loads((BASE / "rapports" / "screening-sample-report.screening.json").read_text())
    if frais["empreinte"] != rendu["empreinte"] or frais["fichier"]["sha256"] != rec["fichier"]["sha256"]:
        sys.exit("le relevé rendu à côté du PDF n'est pas celui que la fiche nomme, ou ne crible pas le même fichier : refusé")
    if (frais["totaux"]["forts"], frais["totaux"]["possibles"], frais["totaux"]["sansCorrespondance"]) != (ex["forts"], ex["possibles"], ex["sans"]):
        sys.exit("la passe fraîche ne recompte pas le relevé commité : la fiche nommerait deux rapports différents : refusé")
    for f in ("rapports/screening-sample-report.pdf", "rapports/screening-sample-report.screening.json", "rendus/rapport-exemple.webp", "rendus/robot-rubis-curieux.webp", "rendus/robot-rubis-penche.webp"):
        if not (BASE / f).exists():
            sys.exit(f"{f} absent : la section du rapport aurait un trou")
    if off["annuel"] != "two months free":
        sys.exit("offre-screening.json : la règle annuelle a changé, le calcul « dix mois payés » du curseur est à revoir")
    MOIS_PAYES, SEMAINES = 10, 52      # « two months free » : douze mois moins deux ; un rapport par semaine
    EN_LETTRES = {5: "five", 10: "ten", 20: "twenty"}
    usd = lambda n: f"${n:,}"
    r0, rc = off["rapport"], off["recriblage"]
    PAS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
    for x in [r0["noms"]] + [x["noms"] for x in rc]:
        if x not in PAS:
            sys.exit(f"le palier de {x} noms n'est pas un cran du curseur : ajouter le cran")
    defaut = PAS.index(r0["noms"])
    def phrase(n, periode):
        pal = next((x for x in rc if n <= x["noms"]), None)
        if pal is None:
            return f"A list above {rc[-1]['noms']:,} names: write to {off['contact']} for a price."
        m = pal["prix_usd_mois"]; a = m * MOIS_PAYES; par = round(a / SEMAINES)
        abo = (f"<b>{usd(m)} a month</b> to have it screened again each week" if periode == "mois"
               else f"<b>{usd(a)} paid yearly</b> for {SEMAINES} weekly reports, about {usd(par)} each")
        if n <= r0["noms"]:
            return f"A list of {n:,} names: <b>{usd(r0['prix_usd'])}</b> for one report, or {abo}."
        return f"A list of {n:,} names is longer than one report covers, so start with the weekly re-screen: {abo}."
    data = html_mod.escape(json.dumps({"rapport": r0, "paliers": rc, "moisPayes": MOIS_PAYES, "semaines": SEMAINES,
                                       "pas": PAS, "contact": off["contact"]}), quote=True)
    reperes = "".join(f'<span class="{"on" if x["noms"] == r0["noms"] else ""}" style="--p:{PAS.index(x["noms"]) / (len(PAS) - 1):.4f}" data-noms="{x["noms"]}"><b>{usd(x["prix_usd_mois"])}</b>{x["noms"]:,}</span>' for x in rc)
    sujet = "Ten%20names%20to%20screen"
    pdf, img = "../rapports/screening-sample-report.pdf", "../rendus/rapport-exemple.webp"
    depot = o["depot"].rstrip("/")
    html = f"""<section class="rapport" id="report"><div class="colonne">
  <div class="r-grille">
  <div class="r-texte">
    <p class="marque-h">The screening report</p>
    <h2 class="h2">Send us your list, and within {off["delai_heures"]} hours it comes back screened and sealed.</h2>
    <ol class="r-pas">
      <li><span><b>You send</b> a CSV or a spreadsheet with a column of company and vessel names, and the IMO number of a vessel when you have it.</span></li>
      <li><span><b>We screen</b> each name against ten public sources: OFAC SDN, the OFAC consolidated (non-SDN) lists, the US Consolidated Screening List (its Commerce and State lists), the UN Security Council list, the EU financial sanctions list, the UK Sanctions List, the vessels the EU designates in Annex XLII of Regulation 833/2014, Australia's DFAT Consolidated List, the Consolidated Canadian Autonomous Sanctions List and New Zealand's Russia Sanctions Register, each as downloaded on the date the report states.</span></li>
      <li><span><b>You receive</b> a PDF, a spreadsheet and the sealed record: each candidate with its list entry and the words that matched, the dates of the lists, and a seal anyone can check with one command, <code>npm run sceller -- &lt;record&gt;.screening.json --check</code>.</span></li>
    </ol>
  </div>
  <figure class="r-feuille">
    <a href="{pdf}" download><img src="{img}" width="1224" height="1584" loading="lazy" decoding="async"
      alt="First page of the sample report: {ex["lignes"]} invented counterparties, {ex["forts"]} strong candidates, {ex["possibles"]} possible, {ex["sans"]} with no candidate."></a>
    <figcaption>sample report &#183; {ex["lignes"]} invented counterparties &#183; a fresh run of {rendu["emis"]} at commit {rendu["commit"]}, record {rendu["empreinte"]} &#183; the committed record of the same file is {ex["sceau"]} ({ex["emis"]})</figcaption>
  </figure>
  </div>
  <div class="r-offre" data-offre="{data}">
    <div class="r-cols">
      <article class="r-col" data-col="rapport">
        <img class="r-robot" src="../rendus/robot-rubis-curieux.webp" width="1023" height="961" alt="" loading="lazy" decoding="async">
        <p class="r-eti">One report</p>
        <p class="r-montant"><span class="r-n" data-v="{r0["prix_usd"]}">{usd(r0["prix_usd"])}</span><small>up to {r0["noms"]:,} names</small></p>
        <p class="r-sous">Your list, screened once and sealed, back within {off["delai_heures"]} hours.</p>
        <ul class="r-inclus"><li>The report as a PDF and as a spreadsheet</li><li>Each candidate with its list entry and the words that matched</li><li>The dates of the ten sources, and a seal anyone can check</li></ul>
        <p class="r-au-dela" hidden>Stops at {r0["noms"]:,} names</p>
      </article>
      <article class="r-col haute" data-col="abo">
        <img class="r-robot" src="../rendus/robot-rubis-penche.webp" width="726" height="865" alt="" loading="lazy" decoding="async">
        <p class="r-eti">Weekly re-screen</p>
        <p class="r-montant"><span class="r-n" data-v="{rc[0]["prix_usd_mois"]}">{usd(rc[0]["prix_usd_mois"])}</span><small class="r-unite">a month, up to {rc[0]["noms"]:,} names</small></p>
        <p class="r-sous">The same list, screened again each week against the lists of that week.</p>
        <ul class="r-inclus"><li><b>{SEMAINES}</b> sealed reports a year</li><li>Each report opens with what changed since the last one</li><li>Billed monthly, or yearly with {off["annuel"]}</li><li>Stop any time: it runs to the end of the month or year paid, no refund</li></ul>
      </article>
    </div>
    <div class="r-taille">
      <div class="r-taille-tete"><label for="r-noms">Names on your list</label><output class="r-noms-v" for="r-noms">{r0["noms"]:,}</output>
        <div class="r-bascule" role="group" aria-label="Billing period"><button type="button" aria-pressed="true" data-p="mois">monthly</button><button type="button" aria-pressed="false" data-p="an">paid yearly</button></div></div>
      <div class="r-piste" style="--f:{defaut / (len(PAS) - 1):.4f}">
        <input type="range" id="r-noms" min="0" max="{len(PAS) - 1}" step="1" value="{defaut}" aria-valuetext="{r0["noms"]:,} names">
        <div class="r-reperes" aria-hidden="true">{reperes}</div>
      </div>
      <p class="r-phrase" aria-live="polite">{phrase(r0["noms"], "mois")}</p>
    </div>
  </div>
  <p class="r-note">{off["conservation"]} A candidate is a name for your compliance officer to check: the report does not decide, does not screen ownership, and is not legal advice.</p>
  <div class="ouvrir-ligne"><a class="ouvrir" href="mailto:{off["contact"]}?subject={sujet}"><span><span class="ouvrir-t">Try it on {EN_LETTRES.get(off["essai_noms"], off["essai_noms"])} of your names</span>
    <span class="ouvrir-s">Email them to {off["contact"]}. The report comes back within {off["delai_heures"]} hours, at no charge.</span></span>
    <span class="fl" aria-hidden="true">&#8594;</span></a></div>
  <p class="liens"><a class="lien-e" href="{pdf}" download>Download the sample report <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="../rapports/screening-sample-report.screening.json">Open the record this PDF renders <span aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{depot}/blob/main/exemple/contreparties-exemple.screening.json">Open the committed example record <span aria-hidden="true">&#8594;</span></a></p>
</div></section>
<script>
(() => {{
  const calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const f = document.querySelector('.rapport .r-feuille a');
  if (f && !calme) {{
    f.addEventListener('pointermove', (e) => {{
      const r = f.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      f.classList.add('suit'); f.style.setProperty('--ry', (x * 7).toFixed(2) + 'deg'); f.style.setProperty('--rx', (-y * 5).toFixed(2) + 'deg');
    }});
    f.addEventListener('pointerleave', () => {{ f.classList.remove('suit'); f.style.removeProperty('--rx'); f.style.removeProperty('--ry'); }});
  }}
  const bloc = document.querySelector('.rapport .r-offre'); if (!bloc) return;
  const O = JSON.parse(bloc.dataset.offre), fmt = (n) => n.toLocaleString('en-US'), usd = (n) => '$' + fmt(n);
  for (const c of bloc.querySelectorAll('.r-col')) c.addEventListener('pointermove', (e) => {{
    const r = c.getBoundingClientRect(); c.style.setProperty('--mx', (e.clientX - r.left) + 'px'); c.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }});
  const colR = bloc.querySelector('[data-col="rapport"]'), colA = bloc.querySelector('[data-col="abo"]');
  const nA = colA.querySelector('.r-n'), uA = colA.querySelector('.r-unite'), nR = colR.querySelector('.r-n');
  const curseur = bloc.querySelector('#r-noms'), piste = bloc.querySelector('.r-piste'), sortie = bloc.querySelector('.r-noms-v');
  const phraseEl = bloc.querySelector('.r-phrase'), reperes = [...bloc.querySelectorAll('.r-reperes span')], auDela = colR.querySelector('.r-au-dela');
  let periode = 'mois';
  const compter = (el, vers, texte) => {{
    const de = Number(el.dataset.v) || 0; el.dataset.v = vers;
    if (calme || de === vers) {{ el.textContent = texte(vers); return; }}
    const t0 = performance.now(), duree = 450;
    const pas = (t) => {{ const k = Math.min(1, (t - t0) / duree), e = 1 - Math.pow(1 - k, 3);
      el.textContent = texte(Math.round(de + (vers - de) * e)); if (k < 1) requestAnimationFrame(pas); }};
    requestAnimationFrame(pas);
  }};
  const phrase = (n) => {{
    const pal = O.paliers.find((x) => n <= x.noms);
    if (!pal) return 'A list above ' + fmt(O.paliers[O.paliers.length - 1].noms) + ' names: write to ' + O.contact + ' for a price.';
    const m = pal.prix_usd_mois, a = m * O.moisPayes, par = Math.round(a / O.semaines);
    const abo = periode === 'mois' ? '<b>' + usd(m) + ' a month</b> to have it screened again each week'
                                   : '<b>' + usd(a) + ' paid yearly</b> for ' + O.semaines + ' weekly reports, about ' + usd(par) + ' each';
    if (n <= O.rapport.noms) return 'A list of ' + fmt(n) + ' names: <b>' + usd(O.rapport.prix_usd) + '</b> for one report, or ' + abo + '.';
    return 'A list of ' + fmt(n) + ' names is longer than one report covers, so start with the weekly re-screen: ' + abo + '.';
  }};
  const poser = () => {{
    const i = Number(curseur.value), n = O.pas[i], pal = O.paliers.find((x) => n <= x.noms);
    piste.style.setProperty('--f', (i / (O.pas.length - 1)).toFixed(4));
    const plafond = O.paliers[O.paliers.length - 1].noms;
    sortie.textContent = n > plafond ? fmt(plafond) + '+' : fmt(n);
    curseur.setAttribute('aria-valuetext', n > plafond ? 'more than ' + fmt(plafond) + ' names' : fmt(n) + ' names');
    colR.classList.toggle('hors', n > O.rapport.noms); auDela.hidden = n <= O.rapport.noms;
    reperes.forEach((s) => s.classList.toggle('on', pal && Number(s.dataset.noms) === pal.noms));
    if (pal) {{
      nA.classList.remove('mot');
      const v = periode === 'mois' ? pal.prix_usd_mois : pal.prix_usd_mois * O.moisPayes;
      compter(nA, v, usd);
      uA.textContent = (periode === 'mois' ? 'a month' : 'a year') + ', up to ' + fmt(pal.noms) + ' names';
    }} else {{ nA.dataset.v = 0; nA.classList.add('mot'); nA.textContent = 'on request'; uA.textContent = 'above ' + fmt(O.paliers[O.paliers.length - 1].noms) + ' names'; }}
    phraseEl.innerHTML = phrase(n);
  }};
  curseur.addEventListener('input', poser);
  for (const b of bloc.querySelectorAll('.r-bascule button')) b.addEventListener('click', () => {{
    periode = b.dataset.p; bloc.querySelectorAll('.r-bascule button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); poser();
  }});
  // à l'arrivée, les deux montants se comptent depuis zéro et retombent sur l'écrit
  if (!calme && 'IntersectionObserver' in window) {{
    const io = new IntersectionObserver((es) => {{ if (!es.some((e) => e.isIntersecting)) return; io.disconnect();
      for (const el of [nR, nA]) {{ const v = Number(el.dataset.v); el.dataset.v = 0; compter(el, v, usd); }} }}, {{ threshold: .4 }});
    io.observe(bloc.querySelector('.r-cols'));
  }}
}})();
</script>"""
    assert "—" not in html, "un cadratin s'est glissé dans la section du rapport"
    for attendu in (usd(r0["prix_usd"]), *(usd(x["prix_usd_mois"]) for x in rc), ex["sceau"], off["conservation"]):
        if attendu not in html:
            sys.exit(f"la section du rapport n'affiche pas « {attendu} » : refusé")
    return html

def batir_outil_catalogue(o, spec):
    # UNE définition de « prêt » : manques(), la même que le rideau et l'assembleur.
    # Elle couvre l'absence, le pret:false et la dérive de sceau (un relevé re-scellé
    # après la dérivation des textes) : toutes des absences DITES, pas des pannes —
    # le 9/09, la dérive post-A-L4 faisait sys.exit ici et cassait l'assemblage entier
    m = manques(o["id"], BASE)
    if any(f"findings-{o['id']}.json" in x for x in m):
        print(f"{o['page_hero']} non bâti : {[x for x in m if 'findings' in x][0]} "
              f"(lot {spec['lot']}) : l'absence est dite, rien n'est improvisé")
        return False
    findings_chemin = BASE / f"findings-{o['id']}.json"
    RELEVE = lire_releve_scelle(o["releve"])
    SCEAU_O = RELEVE["empreinte"]
    _f = json.loads(findings_chemin.read_text())
    if not _f.get("pret", True):
        print(f"{o['page_hero']} non bâti : findings-{o['id']}.json porte pret:false "
              f"(lot {spec['lot']}, chiffres en attente de leur sceau) : l'absence est dite")
        return False
    if _f.get("sceau") != SCEAU_O:
        sys.exit(f"findings-{o['id']}.json cite le scellé {_f.get('sceau')} mais le relevé "
                 f"public porte {SCEAU_O} : les textes ont dérivé du relevé, lot {spec['lot']} à resceller")
    FINDINGS = _f["findings"]
    if len(FINDINGS) != 5:
        sys.exit(f"findings-{o['id']}.json porte {len(FINDINGS)} findings : la séquence en veut 5")

    # AUCUN CHIFFRE TAPÉ : chaque valeur affichée d'une fiche à `source` est REFAITE depuis
    # le relevé scellé : cellule[mesure][champ ou « taux »], ou le compte nommé : et le
    # nombre refait doit apparaître dans le HTML affiché (à une ou zéro décimale, les deux
    # écritures de la maison). Un chiffre qui ne se refait pas ne se publie pas.
    def _refaire_grille(src):
        moitie = RELEVE[src["table"]]
        if "compte" in src:
            return [str(moitie[src["compte"]])]
        c = moitie["tables"][src["palier"]][src["seuil"]][src["mesure"]]
        v = c[src.get("champ", "taux")]
        return [f"{v * 100:.1f}", f"{v * 100:.0f}"]
    # l'onyx n'a ni palier ni seuil : ses adresses parlent le contrat, et son refaire
    # vit dans le spec — le crochet, pas une quatrième copie de la boucle de garde
    _refaire = (lambda src: spec["refaire"](RELEVE, src, o)) if "refaire" in spec else _refaire_grille
    for num_f, f in enumerate(FINDINGS, 1):
        for cote_nom in ("a", "b"):
            src = (f.get("source") or {}).get(cote_nom)
            if not src:
                continue
            affiche = re.sub(r"<[^>]+>", "", f[cote_nom])
            attendus = _refaire(src)
            if not any(x in affiche for x in attendus):
                sys.exit(f"findings-{o['id']}.json, fiche {num_f}, côté {cote_nom} : "
                         f"« {affiche} » ne contient aucune écriture du chiffre refait depuis le "
                         f"relevé ({', '.join(attendus)}) : le chiffre affiché a dérivé de sa cellule")

    n_tests_o = n_tests(o)

    canevas_o, css_scrub_o, scrub_o = sequence_scrub(spec["etats"])
    css_o = CSS.replace(PALETTE_VERTE, spec["palette"])
    assert css_o != CSS, "la palette verte n'a pas été trouvée dans le CSS : l'alias n'a rien remplacé"
    css_n = css_o.replace(NUIT_VERTE, spec["nuit"])
    assert css_n != css_o, "la nuit verte n'a pas été trouvée dans le CSS : la page garderait une nuit verte"
    css_o = css_n
    p = o["prefixe_racine"]

    donnees = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            ORGANISATION,
            {"@type": "SoftwareApplication", "name": spec["app"],
             "url": f"{SITE_URL}{o['sous_dossier']}",
             "applicationCategory": "DeveloperApplication",
             "operatingSystem": "macOS, Linux (Node 24+)",
             "downloadUrl": o["depot"],
             "description": spec["app_desc"],
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                        "description": spec["offre"]},
             "publisher": {"@id": ORGANISATION["@id"]}},
        ],
    }, ensure_ascii=True)

    scenes_o = "".join(_scene_outil(o, spec, i, f) for i, f in enumerate(FINDINGS))
    im, iq = _icone_tuile(o, spec, "methode")
    is_, iq2 = _icone_tuile(o, spec, "securite")
    tuiles = [
        (*spec["annexe_methode"], im + iq),
        (*spec["annexe_securite"], is_ + iq2),
        ("Terms of engagement", "What the grant allows, for how long, and what a client buys.",
         lien(o, "ANNEXE-TERMS.html"), _icone_tuile(o, spec, "terms")[0] + _icone_tuile(o, spec, "terms")[1]),
        ("Privacy", "The tool collects no data. What you send us for a report, and how long it is kept.",
         lien(o, "ANNEXE-PRIVACY.html"), _icone_tuile(o, spec, "privacy")[0] + _icone_tuile(o, spec, "privacy")[1]),
        ("Accessibility", "Usable by keyboard, by screen reader, and with motion turned off.",
         lien(o, "ANNEXE-ACCESSIBILITE.html"), _icone_tuile(o, spec, "accessibilite")[0] + _icone_tuile(o, spec, "accessibilite")[1]),
    ]
    def tuile_html(titre, desc, href, img_et_marque):
        # le marqueur placeholder éventuel est ACCOLÉ au chemin par _icone_tuile : on les sépare
        img, _, marque = img_et_marque.partition("<!--")
        marque = ("<!--" + marque) if marque else ""
        return f"""
      <a class="tuile" href="{href}">{marque}
        <span class="tuile-img"><img src="{img}" alt=""></span>
        <span class="tuile-corps"><span class="tuile-t">{titre}</span>
        <span class="tuile-d">{desc}</span></span>
        <span class="tuile-fl" aria-hidden="true">&#8594;</span>
      </a>"""
    tuiles_html = "".join(tuile_html(*t) for t in tuiles)
    vers_rapport = ('\n  <a class="vers-rapport entree" href="#report">Send us your list for a sealed report within '
                    f'{json.loads((BASE / "offre-screening.json").read_text())["delai_heures"]} hours '
                    '<span aria-hidden="true">&#8595;</span></a>') if o["id"] == "screening" else ""
    commandes_html = "".join(f'<code class="ln">{c}</code>\n    ' for c in
                             ([f"git clone {o['depot']}", f"cd {o['depot'].rstrip('/').rsplit('/', 1)[1]}"] + spec["commandes"]))

    page = f"""<!doctype html><html lang="en">
<meta charset="utf-8"><title>{spec["titre"]}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="{spec["og_titre"]}">
<meta property="og:description" content="{spec["description"]}">
<meta property="og:url" content="{SITE_URL}{o["sous_dossier"]}">
<meta property="og:image" content="{SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="{spec["description"]}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E%3Cpath d='M16 0v16H0z' fill='{o["favicon_accent"]}'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{p}fontes/literata.css">
<link rel="stylesheet" href="{p}fontes/roboto-mono.css">
<script type="application/ld+json">{donnees}</script>
<script>document.documentElement.classList.add("js")</script>
<style>{css_o}{css_scrub_o}{CSS_BARRE_SITE}</style>
{barre_site(courant=o["page_hero"], racine=o["prefixe_racine"])}

<main>
<section class="hero">
  <h1 class="h1 entree{" h1-long" if len(spec["h1"]) > 48 else ""}">{spec["h1"]}</h1>
  <p class="lede entree">{spec["lede"]}</p>
  <div class="commande entree" role="group" aria-label="{spec["aria_commande"]}">
    {commandes_html}
  </div>{vers_rapport}
  <div class="cue" aria-hidden="true"><span>scroll</span><span class="fil"></span></div>
</section>

{choix_outils(o)}

<section class="sequence" id="findings" aria-label="The five findings">
  <div class="colle">
    {_rail_outil(o, spec, FINDINGS)}
    <div class="theatre">
      <div class="scenes">{canevas_o}{scenes_o}</div>
    </div>
  </div>
</section>
{_section_entites(o)}
{_section_rapport(o)}
<section class="instrument" data-commun="instrument"><div class="colonne">
  <h2 class="h2">Try the {o["nom"]} instrument on our public test set.</h2>
  {affiche_html("horloge" if o["id"] == "dossier" else "courbes", RELEVE, FINDINGS, spec["instrument_page"],
                spec["instrument_eti"], spec["instrument_sub"], "../rendus/robot-" + ICONES_COULEUR[o["id"]] + "-regarde.webp",
                note="" if o["id"] == "dossier" else _note_outil(spec, RELEVE, FINDINGS), tarif=lien(o, "ENGAGEMENT.html"))}
</div></section>

<div class="couture" aria-hidden="true"><div class="colonne">
  <span class="filet"></span>
  <span class="sceau-c">measured, then frozen &#183; content hash {SCEAU_O}</span>
  <span class="filet"></span>
</div></div>
{film_html(o)}
<nav class="menus" aria-label="Appendices"><div class="colonne">
  <h2 class="h2">Appendices</h2>
  <div class="grille">{tuiles_html}</div>
  <div class="rangee-fine">
    <a class="lien-fin" href="{lien(o, 'ENGAGEMENT.html')}">See pricing <span aria-hidden="true">&#8594;</span></a>
    <a class="lien-fin" href="{lien(o, 'CONTACT.html')}">Get in touch <span aria-hidden="true">&#8594;</span></a>
    <a class="lien-fin" href="{lien(o, 'MENTIONS.html')}">Read the fine print <span aria-hidden="true">&#8594;</span></a>
    <a class="lien-fin" href="{o["depot"]}">View the public repository <span aria-hidden="true">&#8594;</span></a>
  </div></div></nav>
</main>

{pied_html(outil=o, sceau=SCEAU_O, tests=n_tests_o)}

<script>{JS}</script>{scrub_o}
"""
    assert "\u2014" not in page, "un cadratin s'est glissé dans la page"
    (BASE / o["page_hero"]).write_text(page, encoding="utf-8")
    etat = f"états {spec['etats']}" if _etats_dispo(spec) else "PLACEHOLDERS (plateau vert) : refusé en prod"
    print(o["page_hero"], f"{len(page) / 1e3:.0f} ko", "·", etat)
    return True


def batir(outil_id):
    """Le point d'entrée du catalogue : « routing » est déjà émis à l'import
    (le chemin historique) ; les outils du catalogue s'émettent ici."""
    if outil_id == "routing":
        return True
    if outil_id in SPECS:
        return batir_outil_catalogue(OUTILS[outil_id], SPECS[outil_id])
    sys.exit(f"outil inconnu : {outil_id}")


batir("screening")
batir("monitoring")
batir("scoring")
batir("dossier")
batir_accueil()   # last : it reads SPECS and links the five pages
