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
from ciel_accueil import CSS_CIEL, JS_CIEL, JS_TETE, ciel_html   # the home's night sky (25/10)
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
    ("privacy", "Privacy", "What you send us for a report, what we keep, and for how long.", "ANNEXE-PRIVACY.html"),
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
  /* two wide lines instead of four (Arslane, 25/10, retouch pin 1 on Routing), the answer in green */
  .h1.h1-deux{font-size:clamp(40px,4.2vw,62px);max-width:24ch;line-height:1.05}
  .h1-deux em{font-style:normal;color:var(--vert-vif)}
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
  /* edge to edge with a hairline in the middle (Arslane, 25/10, retouch pin 4): the same mono voice as the
     columns' labels, so the title belongs to what sits under it */
  .rideau-titre{position:absolute;top:66px;left:0;right:0;z-index:2;display:flex;align-items:center;gap:24px;
    padding:0 48px;font-family:var(--mono,ui-monospace,monospace);font-size:12px;font-weight:400;
    letter-spacing:.14em;text-transform:uppercase;line-height:1.2;color:var(--sur-vert-pale)}
  /* five dots in place of the hairline (Arslane, 25/10, pinned note on /monitoring/): one per instrument, in card
     order, each in its card ring colour (--pan-vif); the current tool's dot a little larger. Decorative. */
  .rideau-points{flex:1;display:flex;justify-content:center;align-items:center;gap:10px}
  .rideau-points i{display:block;width:6px;height:6px;border-radius:50%;background:var(--c);
    box-shadow:0 0 8px color-mix(in srgb,var(--c) 55%,transparent)}
  .rideau-points i.ici{width:9px;height:9px;box-shadow:0 0 12px color-mix(in srgb,var(--c) 75%,transparent)}
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
  /* THE CURRENT TOOL (Arslane, 25/10: not everyone can read "you are here"). Its card wears a 3 px ring of
     its own colour (--pan-vif, the tool's --accent-vif) with a soft glow of the same colour, its robot is
     raised and lit, and a filled dot takes the place of the "Open" button. Colour is never the only cue:
     the ring, the raised robot and the dot are shapes. Ring against the pans' nights, measured 25/10:
     3.25:1 at worst (rubis on the rubis night). */
  .pan[aria-current]{box-shadow:inset 0 0 0 3px var(--pan-vif),
      inset 0 0 44px 4px color-mix(in srgb,var(--pan-vif) 34%,transparent)}
  .pan[aria-current]::before{opacity:.85}
  .rideau.vu .pan[aria-current] img,.rideau:not(.vu) .pan[aria-current] img{transform:translateY(-12px) scale(1.04);
    filter:drop-shadow(0 20px 36px rgba(0,0,0,.55)) drop-shadow(0 0 22px color-mix(in srgb,var(--pan-vif) 55%,transparent))}
  .pan[aria-current] .p-eti{text-shadow:0 0 18px color-mix(in srgb,var(--pan-vif) 80%,transparent)}
  .pan .p-ici{border:0;padding:10px 0;display:flex;align-items:center;justify-content:center}
  .p-point{display:block;width:14px;height:14px;border-radius:50%;background:var(--pan-vif);
    box-shadow:0 0 0 4px color-mix(in srgb,var(--pan-vif) 28%,transparent),0 0 16px 2px color-mix(in srgb,var(--pan-vif) 60%,transparent)}
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
  .rideau{overflow:hidden;overflow:clip;background:var(--ouverture,var(--papier))}   /* clip (25/10): a.pan.cote-d slid past 390 px while it animated */
    /* derrière les pans : la nuit de l'outil qu'on ouvre */
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
  /* 25/10 (Arslane, look C kept in the retouch session): no cream band; the seam's line repeated in a slow ticker
     with faded edges between two hairlines, on the page's own night; still under prefers-reduced-motion */
  .couture.defile{background:linear-gradient(180deg,var(--nuit-c),color-mix(in srgb,var(--nuit-a) 70%,var(--nuit-c)));padding:0}
  .couture.defile .colonne{display:block;max-width:none;padding:0}
  .cz3{overflow:hidden;border-top:1px solid color-mix(in srgb,var(--sur-vert) 14%,transparent);border-bottom:1px solid color-mix(in srgb,var(--sur-vert) 14%,transparent);
    padding:18px 0;-webkit-mask:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
  .cz3 div{display:inline-block;white-space:nowrap;font:500 12px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;
    color:var(--sur-vert-pale);animation:cz3 60s linear infinite}
  .cz3 em{font-style:normal;color:var(--vert-clair)}
  @keyframes cz3{to{transform:translateX(-50%)}}
  @media (prefers-reduced-motion:reduce){.cz3 div{animation:none}}

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
    .rideau-titre{top:39px;padding:0 20px;gap:14px}
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
      // 25/10 (Arslane): "can it bring us back to the top so we see the hero screens?" The link now carries
      // no fragment: the next page opens at its top, on its living hero.
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
  // the home has no .sequence: surScroll threw on every scroll above 1080 px (measured 25/10, console)
  if (seq) addEventListener("scroll", surScroll, {passive: true});
  jalons.forEach((j, k) => j.addEventListener("click", () => {
    // le milieu du palier d'arrivée (le scrub tient la dernière image sur la seconde moitié)
    const r = seq.offsetTop + (seq.offsetHeight - innerHeight) * ((k + 0.75) / scenes.length);
    scrollTo({top: innerWidth <= 1080 ? scenes[k].offsetTop - 90 : r,
              behavior: reduit ? "auto" : "smooth"});
  }));
  poser(0); if (seq) surScroll();
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
    « Open X ». Cliquer un pan mène à SA page, EN HAUT, sur son héros vivant (Arslane, 25/10 ;
    du 30/09 au 25/10 le lien portait #findings et la page s'ouvrait sur sa séquence 3D).
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
                     # 25/10 (Arslane): the current tool is told by its ring, its lit robot and a filled
                     # dot, not by words few people read; the words stay for screen readers only.
                     f'<span class="p-ouvrir p-ici"><span class="p-point" aria-hidden="true"></span>'
                     f'<span class="sr">You are here &#183; {o["nom"]}</span></span></div>')
        else:
            pans += (f'\n  <a class="pan {cote}" style="{style}" href="{prefixe}{o["page_hero"]}">{corps}'
                     f'<span class="p-ouvrir">Open {o["nom"]} <span aria-hidden="true">&#8594;</span></span></a>')
    n = NOMBRES.get(len(outils), str(len(outils)))
    points = "".join(f'<i{" class=\"ici\"" if outil is not None and o["id"] == outil["id"] else ""} style="--c:{o["vif"]}"></i>'
                     for o in outils)
    return (f'<nav class="rideau" id="tools" aria-label="The instruments">'
            f'\n  <span class="rideau-titre"><span>{n} instruments</span>'
            f'<span class="rideau-points" aria-hidden="true">{points}</span><span>One method</span></span>'
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


# 25/10 (Arslane, look A kept in the retouch session): the three audit steps as a living sample page
# 25/10 (Arslane, look B kept in the retouch session): the data-and-limits note as three cards with a drawn icon each.
_RNOTE_CSS = "<style>#report p.r-note{max-width:none;font-size:inherit;line-height:inherit;color:inherit}#report .rn2{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}#report .rn2>span{display:flex;flex-direction:column;gap:10px;padding:20px;border-radius:14px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);background:linear-gradient(180deg,color-mix(in srgb,var(--pan-a,#33191f) 64%,transparent),color-mix(in srgb,var(--pan-b,#241217) 80%,transparent))}\n#report .rn2 svg{width:30px;height:30px;color:var(--pan-vif,#d64a5c)}#report .rn2 b{font:600 18px/1.2 \"Literata\",Georgia,serif;color:var(--sur-vert)}#report .rn2 i{font:400 13.5px/1.55 \"Literata\",Georgia,serif;font-style:normal;color:var(--sur-vert-pale)}\n@media (max-width:900px){#report .rn2{grid-template-columns:1fr}}</style>"
_RNOTE_ICONES = ["<path d=\"M9 9h18l-2 20H11z M7 9h22 M14 9V6h8v3\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\"/>", "<path d=\"M28 18a10 10 0 1 1-3-7 M28 7v5h-5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\"/>", "<circle cx=\"18\" cy=\"14\" r=\"5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\"/><path d=\"M8 29c1-6 5-9 10-9s9 3 10 9\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\"/>"]
def _rnote_cartes(conservation):
    # the offer's retention text holds two sentences (the file, then the re-screen list); one card each, the limits third
    phrases = [x.strip() for x in re.split(r"(?<=\.)\s+", conservation.strip()) if x.strip()]
    if len(phrases) != 2:
        sys.exit(f"offre screening : « conservation » devait porter deux phrases, elle en porte {len(phrases)} : revoir _rnote_cartes")
    cartes = [("Your file", phrases[0]), ("Re-screen", phrases[1]),
              ("Candidates", "A candidate is a name for your compliance officer to check: the report does not decide, does not screen ownership, and is not legal advice.")]
    return _RNOTE_CSS + '<span class="rn2">' + "".join(
        f"<span><svg viewBox='0 0 36 36' aria-hidden='true'>{ic}</svg><b>{t}</b><i>{d}</i></span>" for (t, d), ic in zip(cartes, _RNOTE_ICONES)) + "</span>"

# 25/10 (Arslane, look C kept in the retouch session): the measurement line between two hairlines with a lit point.
_SCEAUL_CSS = ".entites .sceau-l.sl3{display:flex;align-items:center;gap:18px;letter-spacing:0;text-transform:none}.entites .sl3>i{flex:1;height:1px;background:linear-gradient(90deg,transparent,color-mix(in srgb,var(--sur-vert) 14%,transparent))}.entites .sl3>i:last-child{background:linear-gradient(90deg,color-mix(in srgb,var(--sur-vert) 14%,transparent),transparent)}.entites .sl3>span{display:flex;align-items:center;gap:12px;font:500 11px/1.4 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--sur-vert-pale);text-align:center}.entites .sl3 b{flex:none;width:8px;height:8px;border-radius:50%;background:var(--pan-vif,#d64a5c);box-shadow:0 0 14px var(--pan-vif,#d64a5c);animation:sl3 2.4s ease-in-out infinite}@keyframes sl3{50%{opacity:.4}}@media (prefers-reduced-motion:reduce){.entites .sl3 b{animation:none}}"
# 25/10 (Arslane, look kept in the retouch session): section#companies as look A, the title on top, then the three
# populations as three panels side by side (figure, sentence, dots, key); the dots keep their pointer script and hover.
_ENTITES_PANNEAUX_CSS = ".entites .ca-k{display:block;margin:0 0 10px;font:500 11px/1.4 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--pan-vif,#d64a5c)}.entites .ca-t{margin:0;font:600 34px/1.12 \"Literata\",Georgia,serif;letter-spacing:-.01em;color:var(--sur-vert);text-wrap:balance;max-width:none}.entites .ca-t span{display:block}.entites .ca-t span+span{color:var(--sur-vert-pale)}.entites .ca-n{font:500 52px/.95 \"Literata\",Georgia,serif;letter-spacing:-.02em;color:var(--sur-vert);font-variant-numeric:lining-nums;white-space:nowrap}.entites .ca-n small{font-size:.4em;letter-spacing:0;color:var(--pan-vif,#d64a5c)}.entites .ca-d{margin:0;max-width:none;font:400 13.5px/1.55 \"Literata\",Georgia,serif;color:var(--sur-vert-pale)}.entites .ca-g{display:grid;gap:1px}.entites .ca-g i{display:block;aspect-ratio:1;border-radius:1px;background:color-mix(in srgb,var(--sur-vert) 13%,transparent)}.entites .ca-g i.f{background:var(--vert-clair);box-shadow:0 0 6px var(--vert-clair)}.entites .ca-g i.p,.entites .ca-g i.v{background:var(--vert-vif)}.entites .ca-c{margin:0;max-width:none;display:flex;flex-direction:column;gap:5px;font:500 10.5px/1.45 var(--mono);letter-spacing:.06em;color:var(--sur-vert-pale)}.entites .ca-c>span{display:flex;align-items:baseline;gap:8px}.entites .ca-c i{flex:none;width:7px;height:7px;border-radius:1px;background:color-mix(in srgb,var(--sur-vert) 22%,transparent)}.entites .ca-c b.nw{font-weight:inherit;white-space:nowrap}.entites .ca-c i.f{background:var(--vert-clair)}.entites .ca-c i.v{background:var(--vert-vif)}.entites .ca-top{display:block;margin-bottom:26px}.entites .ca-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.entites .ca-p{display:flex;flex-direction:column;gap:14px;padding:20px 20px 18px;border-radius:14px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);background:linear-gradient(180deg,color-mix(in srgb,var(--pan-a,#33191f) 64%,transparent),color-mix(in srgb,var(--pan-b,#241217) 80%,transparent))}.entites .ca-h{display:flex;flex-direction:column;gap:10px}.entites .ca-g{grid-template-columns:repeat(69,1fr);margin-top:auto}@media (max-width:900px){.entites .ca-row{grid-template-columns:1fr}}.entites .grille i:hover{transform:scale(1.9);background:#fff}"
# 25/10 (Arslane, look kept in the retouch session): the note under the panels as look B, a band of large figures in two
# groups (the real-name measure, the easier set) and the two closing sentences of the note under it.
_ENTITES_NOTE_CSS = ".entites .note{max-width:none;font-size:inherit;line-height:inherit;color:inherit}.entites .note .nc2{display:block}.entites .note .nc2 .band{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0;border-top:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);border-bottom:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent)}.entites .note .nc2 .g{display:flex;flex-direction:column;gap:14px;padding:20px 28px 22px 0}.entites .note .nc2 .g+.g{padding-left:28px;border-left:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent)}.entites .note .nc2 .h{min-height:3em;font:400 13px/1.5 \"Literata\",Georgia,serif;font-style:italic;color:var(--sur-vert-pale)}.entites .note .nc2 .fs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;margin-top:auto}.entites .note .nc2 .f{display:flex;flex-direction:column;gap:8px}.entites .note .nc2 .n{font:500 52px/1 \"Literata\",Georgia,serif;letter-spacing:-.02em;color:var(--sur-vert);font-variant-numeric:lining-nums}.entites .note .nc2 .n i{font-style:normal;font-size:20px;letter-spacing:0;color:var(--pan-vif,#d64a5c)}.entites .note .nc2 .m{font:500 10.5px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--sur-vert-pale)}.entites .note .nc2 .c{display:block;margin-top:14px;font:400 13.5px/1.6 \"Literata\",Georgia,serif;color:var(--sur-vert-pale)}@media (max-width:900px){.entites .note .nc2 .band{grid-template-columns:1fr}.entites .note .nc2 .g+.g{padding-left:0;border-left:0;border-top:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent)}}"
# (labels appear, a scan passes, the seal lands), on a 9 s loop; still under prefers-reduced-motion.
_AUDIT_VIVANT = "<p class=\"marque-h\">The extraction cost audit</p><h2 class=\"h2\" style=\"font-size:clamp(24px,2vw,30px);line-height:1.2;max-width:28ch\">Find the cheapest extractor for each field, measured on your own pages.</h2><style>\n.lk1{margin-top:30px;display:grid;grid-template-columns:minmax(0,1fr) 150px;gap:26px;align-items:center}\n.lk1 .pg{position:relative;padding:18px 20px 20px;border-radius:4px;color:var(--encre);\n  background:linear-gradient(170deg,var(--papier-haut),var(--papier-bas));box-shadow:0 28px 60px rgba(0,0,0,.45),0 1px 0 rgba(255,255,255,.5) inset;transform:rotate(-1deg)}\n.lk1 .hd{display:flex;justify-content:space-between;font:500 10px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--demi);padding-bottom:10px;border-bottom:1px solid var(--filet-clair)}\n.lk1 .rw{position:relative;display:grid;grid-template-columns:132px 1fr 52px;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(27,29,24,.1)}\n.lk1 .rw span{font:500 12px/1 \"Literata\",Georgia,serif;white-space:nowrap}\n.lk1 .rw i{height:7px;border-radius:4px;background:rgba(27,29,24,.18)}\n.lk1 .rw em{justify-self:end;font:600 9px/1 var(--mono);letter-spacing:.12em;font-style:normal;padding:4px 6px;border-radius:3px;background:#1d6b47;color:#e8f6ee;opacity:0;transform:translateX(8px);animation:lk1t 9s infinite}\n.lk1 .sc{position:absolute;left:0;right:0;height:26px;top:34px;background:linear-gradient(180deg,transparent,rgba(87,177,132,.35),transparent);opacity:0;animation:lk1s 9s infinite}\n.lk1 .st{position:absolute;right:-14px;bottom:-18px;width:96px;height:96px;opacity:0;animation:lk1x 9s infinite}\n.lk1 ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:18px}\n.lk1 li{position:relative;padding-left:14px;color:var(--sur-vert);opacity:.4;animation:lk1l 9s infinite}\n.lk1 li:before{content:\"\";position:absolute;left:0;top:2px;bottom:2px;width:2px;background:var(--vert-vif)}\n.lk1 li b{display:block;font:600 17px/1.2 \"Literata\",Georgia,serif}.lk1 li small{display:block;margin-top:5px;font:400 11.5px/1.45 var(--mono);opacity:.8}\n.lk1 li:nth-child(2){animation-delay:3s}.lk1 li:nth-child(3){animation-delay:6s}\n@keyframes lk1l{0%,2%{opacity:.4}5%,30%{opacity:1}34%,100%{opacity:.4}}\n@keyframes lk1t{0%,3%{opacity:0;transform:translateX(8px)}10%,90%{opacity:1;transform:none}96%,100%{opacity:0}}\n@keyframes lk1s{0%,33%{opacity:0;top:34px}36%{opacity:1;top:34px}60%{opacity:1;top:calc(100% - 40px)}64%,100%{opacity:0;top:calc(100% - 40px)}}\n@keyframes lk1x{0%,66%{opacity:0;transform:scale(1.6) rotate(-30deg)}71%{opacity:1;transform:scale(.94) rotate(-8deg)}74%,94%{opacity:1;transform:scale(1) rotate(-8deg)}100%{opacity:0;transform:scale(1) rotate(-8deg)}}\n@media (max-width:900px){.lk1{grid-template-columns:1fr}}\n@media (max-width:700px){.lk1 .st{right:6px;width:84px;height:84px;animation-name:lk1xm}}\n@keyframes lk1xm{0%,66%{opacity:0;transform:scale(1.12) rotate(-30deg)}71%{opacity:1;transform:scale(.94) rotate(-8deg)}74%,94%{opacity:1;transform:scale(1) rotate(-8deg)}100%{opacity:0;transform:scale(1) rotate(-8deg)}}\n@media (prefers-reduced-motion:reduce){.lk1 *{animation:none!important}}</style><div class=\"lk1\"><div class=\"pg\" aria-hidden=\"true\"><div class=\"hd\"><span>Your sample · page 1</span><span>5 fields</span></div><div class=\"rw\"><span>Name</span><i style=\"width:62%\"></i><em style=\"animation-delay:0.0s\">LABEL</em></div><div class=\"rw\"><span>Date of birth</span><i style=\"width:40%\"></i><em style=\"animation-delay:0.25s\">LABEL</em></div><div class=\"rw\"><span>Document number</span><i style=\"width:74%\"></i><em style=\"animation-delay:0.5s\">LABEL</em></div><div class=\"rw\"><span>Country</span><i style=\"width:34%\"></i><em style=\"animation-delay:0.75s\">LABEL</em></div><div class=\"rw\"><span>Address</span><i style=\"width:88%\"></i><em style=\"animation-delay:1.0s\">LABEL</em></div><div class=\"sc\"></div><svg class=\"st\" viewBox=\"0 0 100 100\" aria-hidden=\"true\"><defs><radialGradient id=\"lk1g\" cx=\"40%\" cy=\"35%\"><stop offset=\"0\" stop-color=\"#2f9a68\"/><stop offset=\"1\" stop-color=\"#145036\"/></radialGradient><path id=\"lk1c\" d=\"M50,50 m-33,0 a33,33 0 1,1 66,0 a33,33 0 1,1 -66,0\"/></defs><circle cx=\"50\" cy=\"50\" r=\"46\" fill=\"url(#lk1g)\"/><circle cx=\"50\" cy=\"50\" r=\"40\" fill=\"none\" stroke=\"#c9f2dc\" stroke-width=\".7\" opacity=\".7\"/><text font-family=\"Roboto Mono,ui-monospace\" font-size=\"7.4\" letter-spacing=\"1.6\" fill=\"#e3f7ec\"><textPath href=\"#lk1c\">SEALED · SIGNED · CRUSETRA · SEALED ·</textPath></text><text x=\"50\" y=\"53\" text-anchor=\"middle\" font-family=\"Roboto Mono,ui-monospace\" font-size=\"7.5\" fill=\"#fff\">__SCEAU8__</text></svg></div><ol><li><b>You label</b><small>a sample of your own documents, field by field.</small></li><li><b>You run</b><small>the audit on your machine: your extractor, the ones you compare, our local models.</small></li><li><b>You receive</b><small>a sealed record and a signed report: the cheapest source per field, the saving at your volume. Check the signature with <code>node src/verifier-rapport.mjs</code>.</small></li></ol></div>"
_RECUS_CSS = "<style>#report .r-recus{position:relative;overflow:hidden;border:0;border-top:1px solid rgba(236,233,223,.12);border-bottom:1px solid rgba(236,233,223,.12);border-radius:0;padding:44px 40px;\nbackground:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .07 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\"),#0a0c0b}\n#report .r-recus:before{content:\"\";position:absolute;inset:-40px 0;pointer-events:none;background:repeating-linear-gradient(180deg,rgba(236,233,223,.025) 0 1px,transparent 1px 4px);animation:rk3s 14s linear infinite}\n@keyframes rk3s{to{transform:translateY(40px)}}\n#report .rk3{position:relative}#report .rk3 .top{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;align-items:end}\n#report .rk3 .mh{font:500 11px/1 var(--mono);letter-spacing:.22em;text-transform:uppercase;color:#8f938c}\n#report .rk3 h3{margin:12px 0 0;font:600 40px/1.05 \"Literata\",Georgia,serif;color:#ece9df;letter-spacing:-.02em}\n#report .rk3 .in{margin:0;font:400 15px/1.6 \"Literata\",Georgia,serif;color:#8f938c}\n#report .rk3 code{display:block;margin-top:26px;padding:14px 0;border-top:1px solid rgba(236,233,223,.12);border-bottom:1px solid rgba(236,233,223,.12);font:400 12px/1.8 var(--mono);color:#ece9df;white-space:pre;overflow-x:auto}\n#report .rk3 code b{color:#8f938c;font-weight:400}\n#report .rk3 .s{display:grid;grid-template-columns:repeat(5,1fr);margin-top:30px}#report .rk3 .s div{padding:4px 18px 0;border-left:1px solid rgba(236,233,223,.12)}#report .rk3 .s div:first-child{border-left:0;padding-left:0}\n#report .rk3 .s b{display:block;font:500 46px/1 \"Literata\",Georgia,serif;color:#ece9df;letter-spacing:-.03em;font-variant-numeric:tabular-nums}#report .rk3 .s b small{font-size:20px;color:#8f938c}\n#report .rk3 .s .o b{color:#8f938c}#report .rk3 .s span{display:block;margin-top:10px;font:400 12px/1.4 var(--mono);color:#ece9df}#report .rk3 .s span i{display:block;font-style:normal;color:#8f938c}\n#report .rk3 .nt{letter-spacing:0;text-transform:none;margin-top:22px;font:400 11px/1.6 var(--mono);color:#8f938c}\n@media (max-width:800px){#report .rk3 .s{grid-template-columns:1fr 1fr}#report .rk3 .top{grid-template-columns:minmax(0,1fr);gap:18px}}@media (prefers-reduced-motion:reduce){#report .r-recus, *{animation:none!important}}</style>"
# 25/10 (Arslane, look C kept): the sample-report caption as the same green seal set on the page's corner.
_LEGENDE_SCEAU = "<style>.cp3{position:relative;display:grid;grid-template-columns:clamp(84px,34%,132px) minmax(0,1fr);gap:18px;align-items:center;margin-top:-66px;text-transform:none;letter-spacing:0}\n.cp3 svg{width:100%;height:auto;aspect-ratio:1;transform:rotate(-8deg);filter:drop-shadow(0 14px 24px rgba(0,0,0,.55));animation:cp3s 7s ease-in-out infinite}\n@keyframes cp3s{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(-2deg) scale(1.03)}}\n.cp3 .t{padding-top:66px;min-width:0;overflow-wrap:anywhere}.cp3 b{display:block;font:600 22px/1.1 \"Literata\",Georgia,serif;color:var(--sur-vert)}\n.cp3 small{display:block;margin-top:6px;font:400 11px/1.5 var(--mono);color:var(--sur-vert);opacity:.72}\n.cp3 a{display:inline-block;margin-top:12px;font:600 12px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--vert-vif);text-decoration:none;border-bottom:1px solid var(--vert-vif);padding-bottom:4px}\n@media (prefers-reduced-motion:reduce){.cp3,.cp3 *{animation:none!important}}</style>\n<div class=\"cp3\"><svg viewBox=\"0 0 100 100\" aria-hidden=\"true\"><defs><radialGradient id=\"cp3g\" cx=\"40%\" cy=\"35%\"><stop offset=\"0\" stop-color=\"#2f9a68\"/><stop offset=\"1\" stop-color=\"#145036\"/></radialGradient>\n<path id=\"cp3c\" d=\"M50,50 m-35,0 a35,35 0 1,1 70,0 a35,35 0 1,1 -70,0\"/></defs><circle cx=\"50\" cy=\"50\" r=\"47\" fill=\"url(#cp3g)\"/>\n<circle cx=\"50\" cy=\"50\" r=\"42\" fill=\"none\" stroke=\"#c9f2dc\" stroke-width=\".7\" opacity=\".7\"/><circle cx=\"50\" cy=\"50\" r=\"27\" fill=\"none\" stroke=\"#c9f2dc\" stroke-width=\".5\" opacity=\".6\"/>\n<text font-family=\"Roboto Mono,ui-monospace\" font-size=\"6.6\" letter-spacing=\"1.3\" fill=\"#e3f7ec\"><textPath href=\"#cp3c\">SEALED __D__ &#183; SIGNED &#183; CRUSETRA &#183;</textPath></text>\n<text x=\"50\" y=\"49\" text-anchor=\"middle\" font-family=\"Literata,Georgia,serif\" font-size=\"9\" font-weight=\"600\" fill=\"#fff\">Sealed</text>\n<text x=\"50\" y=\"59\" text-anchor=\"middle\" font-family=\"Roboto Mono,ui-monospace\" font-size=\"5.6\" fill=\"#d8f5e6\">__H8__</text></svg>\n<div class=\"t\"><b>__N__ real receipts</b><small>record __H__<br>signed page beside the PDF</small><a href=\"__PDF__\" download>Download the sample &#8595;</a></div></div>"
# 25/10 (Arslane, look B kept in the retouch session)
# The free test as a travelling file (CSV, graded, measured JSON, email, PDF) on a 12.5 s loop beside five clickable
# steps (CSS radios); the chosen step shows its labelled rows and its numbered commands. The four links under it become
# tiles (scoped by .r-essai+.liens, which only the Routing report has). Under prefers-reduced-motion the chosen step's
# frame stands still.
_ESSAI_CSS = r"""<style>#report .r-essai .gd-h{margin:10px 0 0}
#report .gd{margin-top:30px;padding:34px;border-radius:18px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 64%,transparent),color-mix(in srgb,var(--nuit-b) 80%,transparent))}#report .gd input{position:absolute;opacity:0;pointer-events:none}
#report .gd .top{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:34px;align-items:center}
#report .gd .stage{position:relative;height:300px;border-radius:12px;background:radial-gradient(120% 90% at 50% 40%,color-mix(in srgb,var(--nuit-a) 90%,#fff 4%),var(--nuit-c));overflow:hidden}
#report .gd .stage:after{content:"";position:absolute;left:0;bottom:0;height:2px;width:100%;background:var(--vert-clair);transform-origin:left;animation:gdp 2.5s linear infinite;opacity:.7}
@keyframes gdp{from{transform:scaleX(0)}to{transform:scaleX(1)}}
#report .gd .fr{position:absolute;inset:0;display:grid;place-items:center;opacity:0;animation:gbf 12.5s infinite}
@keyframes gbf{0%{opacity:0;transform:translateY(14px) scale(.97)}3%,17%{opacity:1;transform:none}20%,100%{opacity:0;transform:translateY(-10px) scale(.98)}}
#report .gd .sh,#report .gd .pdf{width:min(340px,80%);padding:16px 18px 18px;border-radius:4px;color:var(--encre);background:linear-gradient(170deg,var(--papier-haut),var(--papier-bas));box-shadow:0 24px 50px rgba(0,0,0,.45);transform:rotate(-1.2deg)}
#report .gd .pdf{width:200px;transform:rotate(2deg)}
#report .gd .stage p{margin:0}#report .gd .fn{font:600 11px/1 var(--mono);letter-spacing:.06em;color:var(--demi);padding-bottom:10px;border-bottom:1px solid var(--filet-clair);margin-bottom:8px;overflow-wrap:anywhere;line-height:1.3}
#report .gd .hdr{font:500 10px/1.4 var(--mono);color:#1d6b47;margin-bottom:6px;word-break:break-all}
#report .gd .ln{display:flex;align-items:center;gap:8px;height:20px;border-bottom:1px solid rgba(27,29,24,.08)}#report .gd .ln i{display:block;height:6px;border-radius:3px;background:rgba(27,29,24,.18)}
#report .gd .ln u{display:block;width:9px;height:9px;border-radius:50%;background:#2f9a68;opacity:.85;margin-left:auto}#report .gd .ln u+u{margin-left:0;opacity:.55}#report .gd .ln u+u+u{opacity:.3}
#report .gd .cap{margin-top:10px;font:400 10.5px/1.4 var(--mono);color:var(--demi)}
#report .gd .fi,#report .gd .env{width:min(320px,80%);padding:20px;border-radius:10px;border:1px solid color-mix(in srgb,var(--vert-vif) 45%,transparent);background:color-mix(in srgb,var(--nuit-c) 85%,transparent);box-shadow:0 0 30px color-mix(in srgb,var(--vert-vif) 18%,transparent)}
#report .gd .fi .fn,#report .gd .env .fn{color:var(--sur-vert);border-color:color-mix(in srgb,var(--sur-vert) 12%,transparent)}#report .gd .fi .cap,#report .gd .env .cap{color:var(--sur-vert-pale)}
#report .gd .bar{margin-top:14px;height:3px;border-radius:2px;background:color-mix(in srgb,var(--sur-vert) 12%,transparent);overflow:hidden}#report .gd .bar i{display:block;height:100%;background:var(--vert-clair)}
#report .gd .env{position:relative;padding-top:48px}#report .gd .env:before{content:"";position:absolute;left:20px;right:20px;top:14px;height:26px;border:1px solid color-mix(in srgb,var(--sur-vert) 35%,transparent);border-top:0;clip-path:polygon(0 0,50% 100%,100% 0)}
#report .gd .sts{display:flex;flex-direction:column}
#report .gd .st{position:relative;cursor:pointer;display:grid;grid-template-columns:40px 1fr;align-items:baseline;padding:11px 14px 11px 12px;border-radius:10px;opacity:.45;animation:gbl 12.5s infinite;transition:background .25s}
@keyframes gbl{0%{opacity:.45}2%,18%{opacity:1}21%,100%{opacity:.45}}
#report .gd .st:hover{background:color-mix(in srgb,var(--sur-vert) 5%,transparent);opacity:1}
#report .gd .st b{font:500 26px/1 "Literata",Georgia,serif;color:var(--vert-clair)}#report .gd .st em{display:block;font:600 19px/1.15 "Literata",Georgia,serif;font-style:normal;color:var(--sur-vert)}
#report .gd .st small{display:block;margin-top:3px;font:400 13px/1.4 "Literata",Georgia,serif;color:var(--sur-vert-pale)}
#report .gd #gd0:checked~.top .sts .st:nth-of-type(1),#report .gd #gd1:checked~.top .sts .st:nth-of-type(2),#report .gd #gd2:checked~.top .sts .st:nth-of-type(3),#report .gd #gd3:checked~.top .sts .st:nth-of-type(4),#report .gd #gd4:checked~.top .sts .st:nth-of-type(5){opacity:1;animation:none;background:color-mix(in srgb,var(--vert-vif) 12%,transparent);box-shadow:inset 2px 0 0 var(--vert-clair)}
#report .gd #gd0:focus-visible~.top .sts .st:nth-of-type(1),#report .gd #gd1:focus-visible~.top .sts .st:nth-of-type(2),#report .gd #gd2:focus-visible~.top .sts .st:nth-of-type(3),#report .gd #gd3:focus-visible~.top .sts .st:nth-of-type(4),#report .gd #gd4:focus-visible~.top .sts .st:nth-of-type(5){outline:2px solid var(--vert-clair);outline-offset:2px}
#report .gd .ps{margin-top:26px;padding-top:24px;border-top:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent)}#report .gd .p{display:none}
#report .gd #gd0:checked~.ps .p0,#report .gd #gd1:checked~.ps .p1,#report .gd #gd2:checked~.ps .p2,#report .gd #gd3:checked~.ps .p3,#report .gd #gd4:checked~.ps .p4{display:grid;animation:gdi .4s var(--montee)}@keyframes gdi{from{opacity:0;transform:translateY(5px)}}
#report .gd .p.two{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start}
#report .gd .pr{margin:0;max-width:none}#report .gd .rw{display:grid;grid-template-columns:118px 1fr;gap:16px;padding:9px 0;border-top:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent)}#report .gd .rw:first-child{border-top:0;padding-top:0}
#report .gd dt{font:500 10.5px/1.6 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--vert-clair)}#report .gd dd{margin:0;font:400 14.5px/1.55 "Literata",Georgia,serif;color:var(--sur-vert-pale)}
#report .gd dd code{font:400 11.5px/1.6 var(--mono);color:var(--sur-vert);background:color-mix(in srgb,var(--nuit-c) 80%,transparent);border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);border-radius:5px;padding:1px 6px;overflow-wrap:anywhere}
#report .gd .mk{display:inline-grid;place-items:center;width:17px;height:17px;margin:0 2px;border-radius:50%;background:var(--vert-vif);color:var(--nuit-c);font:600 10px/1 var(--mono);vertical-align:2px}
#report .gd .tm{margin:0;padding:16px 18px;border-radius:10px;background:color-mix(in srgb,var(--nuit-c) 90%,transparent);border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);font:400 12px/1.85 var(--mono);color:var(--sur-vert);white-space:pre-wrap;word-break:break-all}
#report .gd .tm b{color:var(--sur-vert-pale);font-weight:400}#report .gd .tm .n{display:inline-grid;place-items:center;width:17px;height:17px;margin-right:8px;border-radius:50%;background:var(--vert-vif);color:var(--nuit-c);font:600 10px/1 var(--mono)}
#report .r-essai+.liens{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:16px}
#report .r-essai+.liens .lien-e{position:relative;display:flex;flex-direction:column;justify-content:flex-start;gap:8px;min-height:118px;padding:18px 58px 18px 20px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);border-radius:14px;
background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 64%,transparent),color-mix(in srgb,var(--nuit-b) 80%,transparent));letter-spacing:0;text-transform:none;color:var(--sur-vert);text-decoration:none;
transition:border-color .3s,transform .3s var(--montee),box-shadow .3s}
#report .r-essai+.liens .lien-e .lv{display:block;font:500 10.5px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--vert-clair)}
#report .r-essai+.liens .lien-e .lt{display:block;font:600 18px/1.25 "Literata",Georgia,serif;color:var(--sur-vert)}
#report .r-essai+.liens .lien-e:hover .lv,#report .r-essai+.liens .lien-e:hover .lt{transform:none}
#report .r-essai+.liens .lien-e .la{position:absolute;right:16px;bottom:16px;display:grid;place-items:center;width:32px;height:32px;border-radius:50%;border:1px solid color-mix(in srgb,var(--sur-vert) 30%,transparent);font:400 14px/1 var(--mono);transition:all .3s}
#report .r-essai+.liens .lien-e:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--vert-vif) 55%,transparent);box-shadow:0 16px 34px rgba(0,0,0,.3)}
#report .r-essai+.liens .lien-e:hover .la{transform:none;background:var(--vert-clair);border-color:var(--vert-clair);color:var(--nuit-c)}
#report .r-essai+.liens .lien-e:focus-visible{outline:2px solid var(--vert-clair);outline-offset:3px}
@media (max-width:900px){#report .gd{padding:24px}#report .gd .top,#report .gd .p.two{grid-template-columns:1fr}#report .gd .top{gap:18px}#report .gd .stage{height:240px}#report .r-essai+.liens{grid-template-columns:1fr 1fr}}
@media (max-width:560px){#report .gd{padding:18px 14px}#report .gd .st{padding:9px 10px;grid-template-columns:32px 1fr}#report .gd .st b{font-size:22px}#report .gd .st em{font-size:17px}
#report .gd .rw{grid-template-columns:1fr;gap:4px}#report .gd .tm{padding:12px 12px;font-size:11px}#report .r-essai+.liens{grid-template-columns:1fr}#report .r-essai+.liens .lien-e{min-height:0;padding:16px 58px 16px 18px}}
@media (prefers-reduced-motion:reduce){#report .r-essai *,#report .r-essai+.liens .lien-e,#report .r-essai+.liens .lien-e *{animation:none!important;transition:none!important}#report .gd .stage:after{display:none}
#report .gd .st{opacity:.7}#report .gd #gd0:checked~.top .stage .fr:nth-child(1),#report .gd #gd1:checked~.top .stage .fr:nth-child(2),#report .gd #gd2:checked~.top .stage .fr:nth-child(3),#report .gd #gd3:checked~.top .stage .fr:nth-child(4),#report .gd #gd4:checked~.top .stage .fr:nth-child(5){opacity:1}#report .r-essai+.liens .lien-e:hover{transform:none}}</style>"""

# 25/10 (Arslane, look C kept in the retouch session): under the instrument card, the pricing link as a tile like the
# report's link tiles (small verb, title, arrow) and the measurement note as numbered, labelled footnotes in two
# columns. Real markup in place of the old link and paragraph; the tile keeps the class affiche-tarif (garde-voix reads
# its verb) and the href it had. Every figure in a footnote comes from the caller's variables.
_TARIF_CSS = """<style>.tn3{display:grid;grid-template-columns:240px minmax(0,1fr);gap:34px;align-items:start;margin:18px 4px 0}
.tn3 a.affiche-tarif{position:relative;display:flex;flex-direction:column;gap:8px;min-height:118px;margin:0;padding:18px 58px 18px 20px;border-radius:14px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);
background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 64%,transparent),color-mix(in srgb,var(--nuit-b) 80%,transparent));color:var(--sur-vert);font-family:inherit;font-size:inherit;letter-spacing:0;text-transform:none;text-decoration:none;transition:transform .3s var(--montee),border-color .3s}
.tn3 a small{font:500 10.5px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--vert-clair)}.tn3 a b{font:600 22px/1.2 "Literata",Georgia,serif}
.tn3 a i{position:absolute;right:16px;bottom:16px;display:grid;place-items:center;width:32px;height:32px;border-radius:50%;border:1px solid color-mix(in srgb,var(--sur-vert) 30%,transparent);font-style:normal;transition:all .3s}
.tn3 a.affiche-tarif:hover{color:var(--sur-vert);transform:translateY(-3px);border-color:color-mix(in srgb,var(--vert-vif) 55%,transparent)}.tn3 a:hover i{background:var(--vert-clair);color:var(--nuit-c)}
.tn3 a.affiche-tarif:focus-visible{outline:2px solid var(--vert-clair);outline-offset:3px}
.tn3 ol{margin:0;padding:0;list-style:none;columns:2;column-gap:34px;counter-reset:n}
.tn3 li{break-inside:avoid;counter-increment:n;display:grid;grid-template-columns:22px 1fr;margin:0 0 14px;font:400 13px/1.55 "Literata",Georgia,serif;color:var(--sur-vert-pale)}
.tn3 li:before{content:counter(n);font:500 11px/1.8 var(--mono);color:var(--vert-clair)}.tn3 li b{color:var(--sur-vert);font-weight:600}
@media (max-width:900px){.tn3{grid-template-columns:1fr}.tn3 ol{columns:1}}
@media (prefers-reduced-motion:reduce){.tn3 a.affiche-tarif,.tn3 a i{transition:none}.tn3 a.affiche-tarif:hover{transform:none}}</style>"""


def _tarif_et_notes(affiche, href, notes):
    """The instrument card (affiche_html, built without its link and note) with the pricing tile and the numbered
    footnotes set inside its column, after the card. `notes` is a list of (label, text)."""
    fin = affiche.rstrip()
    if not fin.endswith("</div>") or 'class="affiche-tarif"' in fin or 'class="t-note"' in fin:
        sys.exit("affiche_html a changé de forme : la tuile des tarifs ne sait plus où se poser")
    bloc = (f'{_TARIF_CSS}<div class="tn3"><a class="affiche-tarif" href="{href}"><small>See</small> <b>Pricing</b><i aria-hidden="true">&#8594;</i></a>'
            '<ol>' + "".join(f"<li><span><b>{t}.</b> {d}</span></li>" for t, d in notes) + "</ol></div>")
    return fin[:-len("</div>")] + bloc + "\n  </div>"


def couture_defile(texte, empreinte, fois=8):
    """The seam (25/10, look C kept): `texte` then the content hash, repeated `fois` times (an even number, so the
    -50% loop of the ticker lands on its own start); the hash comes from the caller's sealed record."""
    if fois % 2:
        sys.exit("la couture défile sur la moitié de sa ligne : il lui faut un nombre pair de répétitions")
    morceau = f"{texte} &#183; content hash <em>{empreinte}</em> &#183; "
    return f'<div class="couture defile" aria-hidden="true"><div class="colonne"><div class="cz3"><div>{morceau * fois}</div></div></div></div>'


# 25/10: the Routing retouches carried to the Screening page, in its own accent. The green that the kept looks wrote as
# hex inside their SVG becomes the Screening tool's colours, read from PALETTE_RUBIS (outil.py), never typed here.
_ACCENT_RUBIS = dict(re.findall(r"--accent-(titre|vif|clair):(#[0-9a-f]{6})", PALETTE_RUBIS))


def _en_rubis(s):
    for vert, nom in (("#2f9a68", "vif"), ("#145036", "titre"), ("#c9f2dc", "clair"), ("#e3f7ec", "clair"), ("#d8f5e6", "clair")):
        if vert not in s:
            sys.exit(f"le vert {vert} n'est plus dans le look : la passe rubis ne sait plus quoi remplacer")
        s = s.replace(vert, _ACCENT_RUBIS[nom])
    return s


# The symmetric link tiles of the Routing report (look B kept on 25/10), for any row of links: .liens.tuiles, one column
# per link (--n). Each link holds a small verb (.lv), a title (.lt) and the arrow (.la).
_TUILES_CSS = """<style>.liens.tuiles{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:12px;margin-top:34px}
.liens.tuiles .lien-e{position:relative;display:flex;flex-direction:column;justify-content:flex-start;gap:8px;min-height:118px;padding:18px 58px 18px 20px;border:1px solid color-mix(in srgb,var(--sur-vert) 12%,transparent);border-radius:14px;
background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 64%,transparent),color-mix(in srgb,var(--nuit-b) 80%,transparent));letter-spacing:0;text-transform:none;color:var(--sur-vert);text-decoration:none;
transition:border-color .3s,transform .3s var(--montee),box-shadow .3s}
.liens.tuiles .lien-e .lv{display:block;font:500 10.5px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--vert-clair)}
.liens.tuiles .lien-e .lt{display:block;font:600 18px/1.25 "Literata",Georgia,serif;color:var(--sur-vert)}
.liens.tuiles .lien-e:hover .lv,.liens.tuiles .lien-e:hover .lt{transform:none}
.liens.tuiles .lien-e .la{position:absolute;right:16px;bottom:16px;display:grid;place-items:center;width:32px;height:32px;border-radius:50%;border:1px solid color-mix(in srgb,var(--sur-vert) 30%,transparent);font:400 14px/1 var(--mono);transition:all .3s}
.liens.tuiles .lien-e:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--vert-vif) 55%,transparent);box-shadow:0 16px 34px rgba(0,0,0,.3)}
.liens.tuiles .lien-e:hover .la{transform:none;background:var(--vert-clair);border-color:var(--vert-clair);color:var(--nuit-c)}
.liens.tuiles .lien-e:focus-visible{outline:2px solid var(--vert-clair);outline-offset:3px}
@media (max-width:760px){.liens.tuiles{grid-template-columns:1fr}.liens.tuiles .lien-e{min-height:0;padding:16px 58px 16px 18px}}
@media (prefers-reduced-motion:reduce){.liens.tuiles .lien-e,.liens.tuiles .lien-e *{transition:none!important}.liens.tuiles .lien-e:hover{transform:none}}</style>"""


def liens_tuiles(liens):
    """liens: (href, verb, title, extra attributes). The row of links as symmetric tiles."""
    return (f'{_TUILES_CSS}<p class="liens tuiles" style="--n:{len(liens)}">'
            + "".join(f'<a class="lien-e" href="{h}"{x}><span class="lv">{v}</span><span class="lt">{t}</span><span class="la" aria-hidden="true">&#8594;</span></a>'
                      for h, v, t, x in liens) + "</p>")


# 25/10 (Arslane, look A kept on Routing, carried to Screening): the report's three steps beside a living sample page.
# The page is the committed sample list (invented counterparties): five of its rows, read from the sealed record, take
# the verdict the record gives them as the scan passes (step 2), then the seal lands (step 3). Colours from the page's
# own variables (rubis here). The steps are long on this page, so they run under the page rather than in a side column.
_LISTE_VIVANTE_CSS = """<style>
.sk1{margin-top:30px;display:grid;grid-template-columns:minmax(0,1fr);gap:34px}
.sk1 .pg{position:relative;padding:18px 20px 64px;border-radius:4px;color:var(--encre);max-width:520px;
  background:linear-gradient(170deg,var(--papier-haut),var(--papier-bas));box-shadow:0 28px 60px rgba(0,0,0,.45),0 1px 0 rgba(255,255,255,.5) inset;transform:rotate(-1deg)}
.sk1 .hd{display:flex;justify-content:space-between;gap:12px;font:500 10px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--demi);padding-bottom:10px;border-bottom:1px solid var(--filet-clair)}
.sk1 .rw{position:relative;display:grid;grid-template-columns:48px minmax(0,1fr) auto;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(27,29,24,.1);animation:sk1r 9s infinite}
.sk1 .rw code{font:500 10px/1 var(--mono);color:var(--demi);letter-spacing:.06em}
.sk1 .rw span{font:500 12.5px/1.2 "Literata",Georgia,serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sk1 .rw em{justify-self:end;font:600 9px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;font-style:normal;padding:4px 6px;border-radius:3px;white-space:nowrap;opacity:0;transform:translateX(8px);animation:sk1t 9s infinite}
.sk1 .rw em.s{background:var(--vert-titre);color:#fff}
.sk1 .rw em.p{box-shadow:inset 0 0 0 1px var(--vert-vif);color:var(--vert-titre)}
.sk1 .rw em.n{background:rgba(27,29,24,.1);color:var(--demi)}
.sk1 .sc{position:absolute;left:0;right:0;height:26px;top:34px;background:linear-gradient(180deg,transparent,color-mix(in srgb,var(--vert-vif) 35%,transparent),transparent);opacity:0;animation:sk1s 9s infinite}
.sk1 .ft{position:absolute;left:20px;bottom:24px;margin:0;font:500 10px/1 var(--mono);letter-spacing:.12em;color:var(--demi)}
.sk1 .st{position:absolute;right:-14px;bottom:-30px;width:96px;height:96px;opacity:0;animation:sk1x 9s infinite}
.sk1 .st .g0{stop-color:var(--vert-vif)}.sk1 .st .g1{stop-color:var(--vert-titre)}
.sk1 .st .an{fill:none;stroke:var(--vert-clair);stroke-width:.7;opacity:.7}.sk1 .st .tx{fill:var(--vert-clair)}.sk1 .st .ce{fill:#fff}
.sk1 ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:18px}
.sk1 li{position:relative;padding-left:14px;color:var(--sur-vert);opacity:.5;animation:sk1l 9s infinite}
.sk1 li:before{content:"";position:absolute;left:0;top:2px;bottom:2px;width:2px;background:var(--vert-vif)}
.sk1 li b{display:block;font:600 17px/1.2 "Literata",Georgia,serif}.sk1 li small{display:block;margin-top:5px;font:400 14px/1.55 "Literata",Georgia,serif;opacity:.85}
.sk1 li code{font:400 12px/1.5 var(--mono);overflow-wrap:break-word}
.sk1 li:nth-child(2){animation-delay:3s}.sk1 li:nth-child(3){animation-delay:6s}
@keyframes sk1l{0%,2%{opacity:.5}5%,30%{opacity:1}34%,100%{opacity:.5}}
@keyframes sk1r{0%{opacity:.35;transform:translateX(-6px)}6%,96%{opacity:1;transform:none}100%{opacity:.35}}
@keyframes sk1t{0%,36%{opacity:0;transform:translateX(8px)}44%,92%{opacity:1;transform:none}97%,100%{opacity:0}}
@keyframes sk1s{0%,33%{opacity:0;top:34px}36%{opacity:1;top:34px}60%{opacity:1;top:calc(100% - 40px)}64%,100%{opacity:0;top:calc(100% - 40px)}}
@keyframes sk1x{0%,66%{opacity:0;transform:scale(1.6) rotate(-30deg)}71%{opacity:1;transform:scale(.94) rotate(-8deg)}74%,94%{opacity:1;transform:scale(1) rotate(-8deg)}100%{opacity:0;transform:scale(1) rotate(-8deg)}}
@keyframes sk1xm{0%,66%{opacity:0;transform:scale(1.12) rotate(-30deg)}71%{opacity:1;transform:scale(.94) rotate(-8deg)}74%,94%{opacity:1;transform:scale(1) rotate(-8deg)}100%{opacity:0;transform:scale(1) rotate(-8deg)}}
@media (max-width:700px){.sk1 .st{right:6px;width:84px;height:84px;animation-name:sk1xm}.sk1 .rw{grid-template-columns:40px minmax(0,1fr) auto}}
@media (prefers-reduced-motion:reduce){.sk1 *{animation:none!important}.sk1 .rw em{opacity:1;transform:none}.sk1 .st{opacity:1;transform:rotate(-8deg)}.sk1 li{opacity:1}}</style>"""


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
    # 25/10 (Arslane, look C kept): a dark textured band, the run on top, the five rates on one line. Values from rec.
    _taux = [(meilleur, "vendor"), (courant, "vendor"), ("gen-4b", "ours, local, needs Ollama"), ("large", "ours, large encoder"), ("small", "ours, small encoder")]
    _bande = "".join(f'<div class="{"o" if w.startswith("ours") else ""}"><b>{pc(n)[:-1]}<small>%</small></b><span>{n}<i>{w}</i></span></div>' for n, w in _taux)
    recus = f"""<div class="r-recus">{_RECUS_CSS}
    <div class="rk3"><div class="top"><div><p class="mh">Start with receipts</p><h3>{ex["cas"]} real receipts,<br>graded in the open.</h3></div>
    <p class="in">The public run grades two vendors and our local tiers on {ex["cas"]} real receipts. Grade one vendor's outputs against the labels yourself, with nothing downloaded:</p></div>
    <code><b>$ </b>git clone {DEPOT_URL}
<b>$ </b>cd {DEPOT_URL.rsplit('/', 1)[1]} &amp;&amp; npm ci --ignore-scripts
<b>$ </b>{cmd_grade}</code>
    <div class="s">{_bande}</div>
    <p class="nt">Share of totals read right. The local tiers read a text that our macOS OCR produced from the images, so their rates include that OCR's errors.</p></div>
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
    # 25/10 (Arslane, look B kept in the retouch session): the same five steps, each fact of the old list kept in the
    # labelled rows of its step, its commands numbered beside them. Every figure from es, off, ex, rec or tessdata.ts.
    _C = lambda x: f"<code>{x}</code>"
    _M = lambda n: f'<sup class="mk">{n}</sup>'
    _hdr = "id,text,total:amount,date:date,vendor:free-text"
    _vend = "--vendor=&lt;textract|documentai|azure&gt;"
    _cmds = [
        [f"npm run text-from-exports -- --cases=your.csv {_vend} --exports=&lt;folder&gt;",
         "npm run tessdata -- --prime",
         "npm run text-from-images -- --cases=your.csv --images=&lt;folder&gt; --ocr=tesseract --lang=eng"],
        ["npm run grade -- --cases=your-with-text.csv --name=&lt;vendor&gt; --values=&lt;its outputs&gt; --price-per-thousand-pages=&lt;your price&gt; --out=&lt;vendor&gt;.json"],
        ["npm run measure:yours -- --cases=your-with-text.csv --sorties=&lt;vendor&gt;.json,&lt;vendor&gt;.json --current=&lt;the one you run today&gt; --margin=2 --pages-per-year=&lt;your volume&gt;"],
        [], []]
    _insep = (f' ({insep_total[0]["discordant"]} disagreements, p = {insep_total[0]["p"]:.2f})') if insep_total else ""
    _court = [("Label", f'{es["pages"]} pages of one document type, one typed column per field.'),
              ("Grade", "each extractor on your own pages. We call no vendor."),
              ("Measure", "every field, with the margin you accept."),
              ("Email", "one record: counts and verdicts, no document, no value."),
              ("Receive", f'a one-page PDF by email within {es["delai_heures"]} hours.')]
    _rangs = [
        [("Format", f"A CSV: an id, the text, then one column per field, named with its type: {_C(_hdr)}"),
         ("No type", f'Exact text: "$1,234.50" and "1234.50" differ. Such a column is refused unless you pass {_C("--exact")}.'),
         ("Blanks", "A dash where a document has no such line. Empty when you do not know the value."),
         ("Text", f"What your vendor already returns {_M(1)}, or your images read offline: once {_M(2)} ({tess_mb} MB of language files), then {_M(3)}."),
         ("Output", f'Either one writes {_C("your-with-text.csv")}, used in steps 2 and 3.'),
         ("Needs", f'Node 24 or newer. Up to {es["extracteurs"]} extractors.')],
        [("No vendor call", "You run each extractor you use or want to compare on your pages, then grade its outputs here."),
         ("From values", f'A JSON {_C("{ &quot;&lt;id&gt;&quot;: { &quot;&lt;field&gt;&quot;: &quot;&lt;value&gt;&quot; } }")} {_M(1)}'),
         ("From exports", f'Raw Textract, Document AI or Azure: {_C(_vend + " --exports=&lt;folder&gt; --mapping=mapping.json")} in place of {_C("--values")}.'),
         ("Output", "Verdicts only, no value.")],
        [("Margin", f"The one you accept, {_M(1)}."),
         ("Files", f'One {_C("--sorties")} per file, or a comma list.'),
         ("Vendors only", f'Add {_C("--no-encoders")}: nothing downloaded. Without it, our local models download once.')],
        [("Send", f'The file ending in {_C("-measured.json")} beside your CSV, to {off["contact"]}.'),
         ("It holds", "Counts, a right, wrong or blank verdict per case and field, your file's name and its hash, the prices you declared."),
         ("Never", "No document, no value. It is the one file you may attach."),
         ("Contract price", "A price under a vendor contract can be replaced with a list price before you send it.")],
        [("Back", f'A one-page PDF by email within {es["delai_heures"]} hours, from that record. The record carries a content hash.'),
         ("Free test", "This report is not signed: the free test stays an internal evaluation under the thirty-day grant."),
         ("Paid tiers", "The Snapshot and the Audit come back signed, and include the right to act on the recommendation in your own operations."),
         ("Sample size", f'On our {ex["cas"]}-receipt sample, two vendors {ecart_pts} points apart on totals could not be told apart{_insep}. {es["pages"]} pages separate vendors far apart; the paid tiers size the sample for close ones.')]]
    _cadres = [
        '<div class="sh"><p class="fn">your.csv</p><p class="hdr">' + _hdr + '</p>' + "".join(f'<p class="ln"><i style="width:{w}%"></i></p>' for w in (78, 64, 86, 58, 72)) + '</div>',
        '<div class="sh"><p class="fn">your-with-text.csv &#183; graded</p>' + "".join(f'<p class="ln g"><i style="width:{w}%"></i><u></u><u></u><u></u></p>' for w in (60, 48, 66, 44, 56)) + '<p class="cap">verdicts, no value</p></div>',
        '<div class="fi"><p class="fn">your-with-text-measured.json</p><p class="cap">counts &#183; a verdict per case and field &#183; your file\'s hash</p><p class="bar"><i></i></p></div>',
        f'<div class="env"><p class="fn">to {off["contact"]}</p><p class="cap">one file attached, no document</p></div>',
        f'<div class="pdf"><p class="fn">one-page PDF</p><p class="cap">by email within {es["delai_heures"]} hours</p>' + "".join(f'<p class="ln"><i style="width:{w}%"></i></p>' for w in (80, 62, 70)) + '</div>']
    _pas = lambda k: (f'<div class="p p{k}{" two" if _cmds[k] else ""}"><dl class="pr">'
                      + "".join(f'<div class="rw"><dt>{t}</dt><dd>{d}</dd></div>' for t, d in _rangs[k]) + "</dl>"
                      + (('<pre class="tm">' + "\n".join(f'<span class="n">{n + 1}</span><b>$ </b>{c}' for n, c in enumerate(_cmds[k])) + "</pre>") if _cmds[k] else "")
                      + "</div>")
    for k, r in enumerate(_rangs):
        if "".join(d for _, d in r).count('class="mk"') != len(_cmds[k]):
            sys.exit(f"pas {k + 1} de l'essai : les renvois numérotés ne correspondent plus à ses commandes")
    essai = (f'<div class="r-essai">{_ESSAI_CSS}<p class="marque-h">How the free test goes</p><h3 class="gd-h">Five steps, all on your machine.</h3>'
             '<div class="gd">' + "".join(f'<input type="radio" name="gd" id="gd{k}"{" checked" if k == 0 else ""}>' for k in range(5))
             + '<div class="top"><div class="stage" aria-hidden="true">'
             + "".join(f'<div class="fr" style="animation-delay:{k * 2.5}s">{f}</div>' for k, f in enumerate(_cadres))
             + '</div><div class="sts">'
             + "".join(f'<label for="gd{k}" class="st" style="animation-delay:{k * 2.5}s"><b>{k + 1}</b><span><em>{t}</em><small>{d}</small></span></label>' for k, (t, d) in enumerate(_court))
             + '</div></div><div class="ps">' + "".join(_pas(k) for k in range(5)) + "</div></div></div>")
    html = f"""<section class="rapport" id="report"><div class="colonne">
  <div class="r-grille">
  <div class="r-texte">
    {_AUDIT_VIVANT.replace("__SCEAU8__", ex["sceau"][:8])}
  </div>
  <figure class="r-feuille">
    <a href="{pdf}" download><img src="{img}" width="1224" height="1584" loading="lazy" decoding="async"
      alt="First page of the sample report: {ex["cas"]} real receipts, {ex["sources"]} sources on {len(ex["champs"])} fields, all routed to {", ".join(pick)}, saving {usd(ex["economie"])} a year at {ex["volume"]:,} documents."></a>
    <figcaption style="text-transform:none;letter-spacing:0;opacity:1">{_LEGENDE_SCEAU.replace("__H__", ex["sceau"]).replace("__H8__", ex["sceau"][:8]).replace("__D__", ex["mesure"]).replace("__N__", str(ex["cas"])).replace("__PDF__", pdf)}</figcaption>
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
  <p class="liens"><a class="lien-e" href="{pdf}" download><span class="lv">Download</span><span class="lt">The sample report</span><span class="la" aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{signe}"><span class="lv">Verify</span><span class="lt">The signed report</span><span class="la" aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{exemple}"><span class="lv">See</span><span class="lt">Labels, OCR text, vendor outputs</span><span class="la" aria-hidden="true">&#8594;</span></a><a class="lien-e" href="{releve}"><span class="lv">Open</span><span class="lt">The sealed record</span><span class="la" aria-hidden="true">&#8594;</span></a></p>
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
# THE FIVE FIELDS UNDER THE MOUSE (Arslane, 25/10, retouch pin 1 on Routing: "no life on the screen").
# One card per field of the published routing, every figure read from instrument-donnees.json at build time:
# the engine and its measured accuracy (acc), and its price per 1,000 documents at the assumed prices.
_DONNEES_CHAMPS = json.loads((BASE / "instrument-donnees.json").read_text())
# THE FLOW, the living Routing hero (Arslane picked and approved it on 25/10, mockup docs/maquette-flux.html).
# A full-bleed canvas: a still stack of identity records, one lane per field in gate order, one gate per engine.
# Every figure (routing, accuracy, price, total, mean accuracy) is read here from instrument-donnees.json at
# build time, the way maquette-flux.py does it; none is typed. All CSS is scoped under .flux-hero.
_FX_ROUTE = _DONNEES_CHAMPS["publie"]["routage"]
_FX_CHAMPS = _DONNEES_CHAMPS["fields"]
_FX_DATA = {
    "fields": _FX_CHAMPS,
    "route": _FX_ROUTE,
    "acc": {f: _DONNEES_CHAMPS["acc"][_FX_ROUTE[f]][f] for f in _FX_CHAMPS},
    "price": {f: _DONNEES_CHAMPS["price"][_FX_ROUTE[f]][f] for f in _FX_CHAMPS},
    "total": sum(_DONNEES_CHAMPS["price"][_FX_ROUTE[f]][f] for f in _FX_CHAMPS),
    "justesse": _DONNEES_CHAMPS["publie"]["justesse"],
}
_FX_NOMS = {"name": "name", "birth": "date of birth", "document": "document number", "country": "country",
            "address": "address"}
_FX_MOTS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
_fx_libres = [_FX_NOMS[f] for f in _FX_CHAMPS if _FX_DATA["price"][f] == 0]
_fx_payants = [_FX_NOMS[f] for f in _FX_CHAMPS if _FX_DATA["price"][f] > 0]
_fx_tout_grand = sum(_DONNEES_CHAMPS["price"]["large"][f] for f in _FX_CHAMPS)
# the lede, variant C (three short airy paragraphs), built from the same figures as the canvas
_FX_LEDE = (f'{_FX_MOTS[len(_fx_libres)]} of the {_FX_MOTS[len(_FX_CHAMPS)].lower()} fields need no model at all. '
            f'A text pattern reads them, free.'
            f'<span class="fx-p">The {" and the ".join(_fx_payants)} go to a model, each to the smallest one that holds up.</span>'
            f'<span class="fx-p fx-prix"><b>${_FX_DATA["total"]:.2f}</b> per 1,000 documents, not ${_fx_tout_grand:.2f}.</span>')

CSS_FLUX = r"""
  .flux-hero{--fx-fond:#07100c;--fx-sur:#ece9df;--fx-pale:#9fa79f;--fx-vert:#57b184;--fx-ambre:#e3b062;
    --fx-texte:"Literata",Georgia,serif;--fx-mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    position:relative;height:100vh;min-height:680px;overflow:hidden;isolation:isolate;color:var(--fx-sur);
    font-family:var(--fx-texte);background:radial-gradient(75% 75% at 62% 48%,#10231a,#0a1712 55%,#050b08)}
  .flux-hero canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
  .flux-hero .fx-grain{position:absolute;inset:0;pointer-events:none;opacity:.09;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
  .flux-hero .fx-vignette{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 90% at 55% 45%,transparent 45%,rgba(0,0,0,.55) 100%)}
  .flux-hero .fx-texte{position:absolute;left:clamp(24px,5vw,80px);top:clamp(90px,13vh,140px);max-width:min(560px,44vw);pointer-events:none}
  .flux-hero .fx-kicker{font:500 12px/1 var(--fx-mono);letter-spacing:.2em;text-transform:uppercase;color:var(--fx-vert);display:flex;align-items:center;gap:10px}
  .flux-hero .fx-kicker i{width:7px;height:7px;border-radius:50%;background:var(--fx-vert);box-shadow:0 0 12px var(--fx-vert);animation:fx-pouls 1.6s ease-in-out infinite}
  @keyframes fx-pouls{50%{opacity:.35}}
  .flux-hero h1{margin:18px 0 0;font-size:clamp(38px,3.9vw,60px);line-height:1.04;font-weight:600;letter-spacing:-.02em;color:var(--fx-sur)}
  .flux-hero h1 em{font-style:normal;color:var(--fx-vert)}
  .flux-hero .fx-lede{margin:18px 0 0;font-size:17px;line-height:1.55;color:var(--fx-pale);max-width:44ch}
  .flux-hero .fx-lede .fx-p{display:block;margin-top:14px}
  .flux-hero .fx-lede .fx-prix{color:var(--fx-sur)}
  .flux-hero .fx-lede b{color:var(--fx-vert);font-weight:500}
  .flux-hero .fx-bande{display:none}
  .flux-hero .fx-compteurs{position:absolute;left:clamp(24px,5vw,80px);bottom:clamp(28px,6vh,56px);display:flex;gap:48px;pointer-events:none}
  .flux-hero .fx-compteurs div{display:flex;flex-direction:column;gap:6px}
  .flux-hero .fx-compteurs strong{font:600 38px/1 var(--fx-texte);font-variant-numeric:tabular-nums;color:var(--fx-sur)}
  .flux-hero .fx-compteurs strong.fx-v{color:var(--fx-vert)}
  .flux-hero .fx-compteurs span{font:400 11px/1 var(--fx-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--fx-pale)}
  .flux-hero .fx-etiquettes{position:absolute;inset:0;pointer-events:none}
  .flux-hero .fx-lf,.flux-hero .fx-lg{position:absolute;transition:opacity .25s ease}
  .flux-hero .fx-lf{transform:translate(-100%,-50%);text-align:right;display:flex;flex-direction:column;gap:3px;
    padding:6px 10px;border-radius:8px;background:rgba(7,16,12,.62);backdrop-filter:blur(6px)}
  .flux-hero .fx-lf b{font:500 15px/1.1 var(--fx-texte);color:var(--fx-sur)}
  .flux-hero .fx-lf span{font:400 11px/1 var(--fx-mono);letter-spacing:.04em;color:var(--fx-sur);opacity:.7;font-variant-numeric:tabular-nums}
  .flux-hero .fx-lf.fx-libre span{color:var(--fx-vert);opacity:1}.flux-hero .fx-lf.fx-cher span{color:var(--fx-ambre);opacity:1}
  .flux-hero .fx-lg{transform:translateY(-50%);display:flex;flex-direction:column;gap:6px;max-width:260px}
  .flux-hero .fx-lg i{font:500 11px/1 var(--fx-mono);font-style:normal;letter-spacing:.18em;text-transform:uppercase;color:var(--fx-sur);opacity:.75}
  .flux-hero .fx-lg.fx-libre i{color:var(--fx-vert);opacity:1}.flux-hero .fx-lg.fx-cher i{color:var(--fx-ambre);opacity:1}
  .flux-hero .fx-lg b{font:600 28px/1.05 var(--fx-texte);letter-spacing:-.01em;color:var(--fx-sur)}
  .flux-hero .fx-lg span{font:400 12px/1.4 var(--fx-mono);color:var(--fx-pale)}
  .flux-hero .fx-lg em{font:400 12px/1.4 var(--fx-mono);font-style:normal;color:var(--fx-sur);max-height:0;overflow:hidden;opacity:0;transition:max-height .3s ease,opacity .25s ease}
  .flux-hero .fx-lg.fx-on em{max-height:60px;opacity:1}
  .flux-hero .fx-off{opacity:.28}
  /* below 1080px the site bar sits in the page, above the hero, not over it */
  @media (max-width:1080px){.flux-hero{height:calc(100vh - 70px)}}
  /* phone and narrow screens: the text, then a band where the flow runs, then the counters */
  @media (max-width:899px){
    .flux-hero{height:auto;min-height:0;display:flex;flex-direction:column;padding:40px 0 32px}
    .flux-hero .fx-texte{position:relative;left:auto;top:auto;max-width:none;padding:0 24px}
    .flux-hero h1{font-size:34px}
    .flux-hero .fx-lede{font-size:16px}
    .flux-hero .fx-bande{display:block;height:440px}
    .flux-hero .fx-compteurs{position:relative;left:auto;bottom:auto;padding:0 24px;gap:20px}
    .flux-hero .fx-compteurs div{flex:1 1 0;min-width:0}
    .flux-hero .fx-compteurs strong{font-size:26px}
    .flux-hero .fx-compteurs span{font-size:10px;line-height:1.35;letter-spacing:.12em}
    .flux-hero .fx-lf{padding:4px 7px;gap:2px}
    .flux-hero .fx-lf b{font-size:12.5px}
    .flux-hero .fx-lf span{font-size:10px}
    .flux-hero .fx-lg{gap:4px}
    .flux-hero .fx-lg i{font-size:9.5px;letter-spacing:.14em}
    .flux-hero .fx-lg b{font-size:18px}
    .flux-hero .fx-lg span,.flux-hero .fx-lg em{font-size:10.5px;line-height:1.35}
  }
  @media (prefers-reduced-motion:reduce){.flux-hero .fx-kicker i{animation:none}}
"""

JS_FLUX = r"""
(function(){
const D = __DATA__;
const hero = document.querySelector(".flux-hero"); if (!hero) return;
const NOM = {name:"Name",birth:"Date of birth",document:"Document number",country:"Country",address:"Address"};
const MOT = {rules:"Text pattern",large:"Large model","gen-4b":"4B model",small:"Small model","gen-0.6b":"0.6B model","gen-8b":"8B model"};
const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
const engines = [...new Set(D.fields.map(f=>D.route[f]))].sort((a,b)=>{
  const pa = D.fields.filter(f=>D.route[f]===a).reduce((s,f)=>s+D.price[f],0), pb = D.fields.filter(f=>D.route[f]===b).reduce((s,f)=>s+D.price[f],0); return pa-pb; });
const ORDRE = engines.flatMap(e=>D.fields.filter(f=>D.route[f]===e));   // fields in gate order: parallel lanes
const eFree = e => D.fields.filter(f=>D.route[f]===e).every(f=>D.price[f]===0);
const RGB = {free:[87,177,132], mid:[236,233,223], dear:[227,176,98]};
const tint = e => eFree(e) ? RGB.free : (engines.indexOf(e)===engines.length-1 ? RGB.dear : RGB.mid);
const cout = p => p===0 ? "free" : "$"+p.toFixed(2);

const cv = hero.querySelector("canvas"), ctx = cv.getContext("2d"), bande = hero.querySelector(".fx-bande");
let W=0,H=0,R=1, mx=-9999, my=-9999, inside=false, visible=true;
const sprites = {};
function sprite(rgb, r){ const k = rgb.join()+r; if (sprites[k]) return sprites[k];
  const c = document.createElement("canvas"), s = r*6*R; c.width=c.height=s; const g = c.getContext("2d");
  const gr = g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.18,`rgba(${rgb},.85)`); gr.addColorStop(.45,`rgba(${rgb},.18)`); gr.addColorStop(1,`rgba(${rgb},0)`);
  g.fillStyle=gr; g.fillRect(0,0,s,s); return sprites[k]=c; }
function fit(){ R = Math.min(2, devicePixelRatio||1); W = cv.clientWidth; H = cv.clientHeight; cv.width=W*R; cv.height=H*R; ctx.setTransform(R,0,0,R,0,0); for (const k in sprites) delete sprites[k]; geo(); }
let G = {};
function geo(){
  const narrow = W < 900;
  let srcX, srcY, splitX, gateX, fy, gy;
  if (narrow){   // the flow runs in its own band under the text; the stream enters from the left edge
    const top = bande.offsetTop, h = bande.offsetHeight;
    srcX = -24; srcY = top + h/2; splitX = Math.round(W*.385); gateX = Math.round(W*.64);
    fy = D.fields.map(f=> srcY + (ORDRE.indexOf(f)-2)*Math.min(76, h*.17));
    gy = engines.map((e,i)=> srcY + (i-(engines.length-1)/2)*Math.min(150, h*.3));
  } else {
    srcX = W*.53; srcY = H*.52; splitX = W*.66; gateX = Math.min(W*.8, W-300);
    fy = D.fields.map(f=> srcY + (ORDRE.indexOf(f)-2)*Math.min(84, H*.11));
    gy = engines.map((e,i)=> srcY + (i-(engines.length-1)/2)*Math.min(170, H*.22));
  }
  G = {narrow, srcX, srcY, splitX, gateX, fy, gy};
  D.fields.forEach((f,i)=>{ const el = LF[i]; el.style.left = (splitX-(narrow?12:16))+"px"; el.style.top = fy[i]+"px"; });
  engines.forEach((e,i)=>{ const el = LG[i], x = gateX+(narrow?18:30); el.style.left = x+"px"; el.style.top = gy[i]+"px";
    el.style.maxWidth = narrow ? (W-x-12)+"px" : ""; });
}
const couche = hero.querySelector(".fx-etiquettes");
const LF = D.fields.map(f=>{ const el=document.createElement("div"); el.className="fx-lf"+(D.price[f]===0?" fx-libre":(engines.indexOf(D.route[f])===engines.length-1?" fx-cher":""));
  el.innerHTML=`<b>${NOM[f]}</b><span>${D.acc[f]}% · ${cout(D.price[f])}</span>`; couche.appendChild(el); return el; });
const LG = engines.map(e=>{ const fs=D.fields.filter(f=>D.route[f]===e), el=document.createElement("div");
  el.className="fx-lg"+(eFree(e)?" fx-libre":(engines.indexOf(e)===engines.length-1?" fx-cher":""));
  el.innerHTML=`<i>${eFree(e)?"Free · ":""}${fs.length} field${fs.length>1?"s":""}</i><b>${MOT[e]}</b><span>${fs.map(f=>NOM[f].toLowerCase()).join(" · ")}</span>`
    + `<em>${cout(fs.reduce((s,f)=>s+D.price[f],0))} per 1,000 documents · ${fs.map(f=>D.acc[f]+"%").join(" / ")} accurate</em>`;
  couche.appendChild(el); return el; });
new ResizeObserver(fit).observe(cv);
addEventListener("pointermove", e=>{ const b=cv.getBoundingClientRect(); mx=e.clientX-b.left; my=e.clientY-b.top; inside = my>=0 && my<=b.height; }, {passive:true});
new IntersectionObserver(([e])=>visible=e.isIntersecting).observe(cv);

// path of a field: source -> its split node -> its gate (two cubic segments)
function pos(p, u){
  const {srcX,srcY,splitX,gateX,fy,gy} = G, k = engines.indexOf(D.route[p.f]), i = p.i;
  const a = .38;
  if (u < a){ const t=u/a, s=1-t;
    const x0=srcX, y0=srcY+p.j*.3, x3=splitX, y3=fy[i]+p.j*.25;
    return [s*s*s*x0+3*s*s*t*(x0+(x3-x0)*.55)+3*s*t*t*(x3-(x3-x0)*.35)+t*t*t*x3, s*s*s*y0+3*s*s*t*y0+3*s*t*t*y3+t*t*t*y3]; }
  const t=(u-a)/(1-a), s=1-t, x0=splitX, y0=fy[i]+p.j*.25, x3=gateX-8, y3=gy[k]+p.j*.18;
  return [s*s*s*x0+3*s*s*t*(x0+(x3-x0)*.5)+3*s*t*t*(x3-(x3-x0)*.45)+t*t*t*x3, s*s*s*y0+3*s*s*t*y0+3*s*t*t*y3+t*t*t*y3];
}
let parts=[], docs=0, spawn=0, spent=0, glow=engines.map(()=>0), hover=-1, t=0;
const nDocs=hero.querySelector(".fx-n-docs"), nCout=hero.querySelector(".fx-n-cout");
// reduced motion: a still frame, particles laid along each lane and left there; the counters keep the
// figures the page was built with (1,000 documents and their cost)
if (calme) D.fields.forEach((f,i)=>{ for (let k=0;k<14;k++) parts.push({f,i,u:(k+.5)/14,s:0,j:(Math.random()-.5)*16,ox:0,oy:0,vx:0,vy:0,r:1.6+Math.random()*1.4}); });

function lanes(){ // soft ribbons under the particles
  D.fields.forEach((f,i)=>{ const rgb = tint(D.route[f]), on = hover<0 || hover===i;
    ctx.strokeStyle=`rgba(${rgb},${on?.10:.03})`; ctx.lineWidth=on&&hover===i?10:6; ctx.lineCap="round";
    ctx.beginPath(); for (let u=0; u<=1.0001; u+=.02){ const [x,y]=pos({f,i,j:0},u); u?ctx.lineTo(x,y):ctx.moveTo(x,y);} ctx.stroke(); });
}
function source(){ // a small stack of identity records the stream comes out of; it stays still
  if (G.narrow) return;
  const {srcX,srcY} = G, w=86, h=112;
  for (let k=3;k>=0;k--){ const o=k*6;
    ctx.save(); ctx.translate(srcX-w-18+o*.6, srcY-h/2-o);
    ctx.shadowColor="rgba(0,0,0,.6)"; ctx.shadowBlur=24; ctx.shadowOffsetY=10;
    ctx.fillStyle = k===0 ? "#17291f" : `rgba(23,41,31,${.9-k*.18})`; ctx.beginPath(); ctx.roundRect(0,0,w,h,9); ctx.fill(); ctx.shadowColor="transparent";
    ctx.strokeStyle="rgba(165,247,203,.16)"; ctx.lineWidth=1; ctx.stroke();
    if (k===0){ ctx.fillStyle="rgba(236,233,223,.16)"; ctx.beginPath(); ctx.roundRect(10,12,24,30,4); ctx.fill();
      for (let r=0;r<5;r++){ ctx.fillStyle=`rgba(236,233,223,${.12+.05*r})`; ctx.beginPath(); ctx.roundRect(10, 52+r*11, 30+((r*29)%40), 4, 2); ctx.fill(); } }
    ctx.restore(); }
}
function gates(){
  const {gateX, gy} = G; hover = -1; let hoverGate=-1;
  engines.forEach((e,i)=>{ const rgb=tint(e), fs=D.fields.filter(f=>D.route[f]===e), g=glow[i];
    const y=gy[i], hgt=58+fs.length*16;
    if (inside && mx>gateX-40 && Math.abs(my-y)<hgt/2+10) hoverGate=i;
    const hal = ctx.createRadialGradient(gateX,y,0,gateX,y,90+g*30); hal.addColorStop(0,`rgba(${rgb},${.16+g*.22})`); hal.addColorStop(1,`rgba(${rgb},0)`);
    ctx.fillStyle=hal; ctx.fillRect(gateX-140,y-140,280,280);
    const gr = ctx.createLinearGradient(gateX-6,0,gateX+6,0); gr.addColorStop(0,`rgba(${rgb},.55)`); gr.addColorStop(.5,`rgba(${rgb},1)`); gr.addColorStop(1,`rgba(${rgb},.55)`);
    ctx.fillStyle=gr; ctx.beginPath(); ctx.roundRect(gateX-5,y-hgt/2,10,hgt,5); ctx.fill();
  });
  LG.forEach((el,i)=>{ el.classList.toggle("fx-on", hoverGate===i); el.classList.toggle("fx-off", hoverGate>=0 && hoverGate!==i); });
  if (hoverGate>=0) hover = D.fields.findIndex(f=>D.route[f]===engines[hoverGate]);
  if (hoverGate<0 && inside) D.fields.forEach((f,i)=>{ if (Math.abs(mx-G.splitX)<90 && Math.abs(my-G.fy[i])<20) hover=i; });
  return hoverGate;
}
function splits(hg){
  D.fields.forEach((f,i)=>{ const rgb=tint(D.route[f]), x=G.splitX, y=G.fy[i];
    const on = hg>=0 ? D.route[f]===engines[hg] : (hover<0||hover===i);
    ctx.globalAlpha = on?1:.35;
    ctx.fillStyle=`rgba(${rgb},1)`; ctx.beginPath(); ctx.arc(x,y,4,0,7); ctx.fill();
    ctx.strokeStyle=`rgba(${rgb},.35)`; ctx.lineWidth=6; ctx.beginPath(); ctx.arc(x,y,9,0,7); ctx.stroke();
    ctx.globalAlpha=1; LF[i].classList.toggle("fx-off", !on); });
}
function frame(now){
  requestAnimationFrame(frame); if (!visible || document.hidden) return;
  const dt = Math.min(.05, (now-(frame.l||now))/1000); frame.l = now; t += dt;
  // background: deep field + faint ruled grid that drifts with the pointer
  ctx.globalCompositeOperation="source-over";
  const bg = ctx.createRadialGradient(W*.62,H*.48,0,W*.62,H*.48,Math.max(W,H)*.75);
  bg.addColorStop(0,"#10231a"); bg.addColorStop(.55,"#0a1712"); bg.addColorStop(1,"#050b08");
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);
  const px = inside && !calme ? (mx/W-.5)*14 : 0, py = inside && !calme ? (my/H-.5)*10 : 0;
  ctx.strokeStyle="rgba(165,247,203,.035)"; ctx.lineWidth=1; ctx.beginPath();
  for (let x=(px%48)-48; x<W; x+=48){ ctx.moveTo(x,0); ctx.lineTo(x,H); }
  for (let y=(py%48)-48; y<H; y+=48){ ctx.moveTo(0,y); ctx.lineTo(W,y); } ctx.stroke();
  lanes(); source();
  if (!calme){ spawn += dt*7;
    while (spawn>1){ spawn-=1; docs++; spent += D.total/1000;
      D.fields.forEach((f,i)=>parts.push({f,i,u:0,s:.16+Math.random()*.07,j:(Math.random()-.5)*16,ox:0,oy:0,vx:0,vy:0,r:1.6+Math.random()*1.4})); } }
  ctx.globalCompositeOperation="lighter";
  const keep=[];
  for (const p of parts){ p.u += dt*p.s; if (p.u>=1){ glow[engines.indexOf(D.route[p.f])] += .05; continue; } keep.push(p);
    let [x,y] = pos(p,p.u);
    if (inside && !calme){ const dx=x+p.ox-mx, dy=y+p.oy-my, d2=dx*dx+dy*dy; if (d2<140*140){ const d=Math.sqrt(d2)+1, k=(1-d/140)*2.2; p.vx+=dx/d*k; p.vy+=dy/d*k; } }
    p.vx*=.88; p.vy*=.88; p.ox=(p.ox+p.vx)*.96; p.oy=(p.oy+p.vy)*.96;
    const dim = hover>=0 && hover!==p.i && D.route[D.fields[hover]]!==D.route[p.f] ? .25 : 1;
    const sp = sprite(tint(D.route[p.f]), p.r), s=p.r*6;
    ctx.globalAlpha = dim*Math.min(1, p.u*8, (1-p.u)*10);
    ctx.drawImage(sp, x+p.ox-s/2, y+p.oy-s/2, s, s); }
  parts = keep; ctx.globalAlpha=1; ctx.globalCompositeOperation="source-over";
  glow = glow.map(g=>Math.min(1,g)*.94);
  const hg = gates(); splits(hg);
  if (!calme){ nDocs.textContent = docs.toLocaleString("en-US"); nCout.textContent = "$"+spent.toFixed(2); }
}
(document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{ fit(); requestAnimationFrame(frame); });
})();
""".replace("__DATA__", json.dumps(_FX_DATA))

# without script the canvas stays empty and the section keeps its dark ground: the text reads, and the
# counters show the figures for 1,000 documents rather than a stream that never starts
_HERO_FLUX = f'''<section class="flux-hero" aria-label="Routing, live">
  <canvas aria-hidden="true"></canvas>
  <div class="fx-grain"></div><div class="fx-vignette"></div><div class="fx-etiquettes" aria-hidden="true"></div>
  <div class="fx-texte">
    <div class="fx-kicker"><i></i>Routing &#183; measured live</div>
    <h1>See which engine each field of your documents <em>actually needs.</em></h1>
    <p class="fx-lede">{_FX_LEDE}</p>
  </div>
  <div class="fx-bande" aria-hidden="true"></div>
  <div class="fx-compteurs" aria-live="off">
    <div><strong class="fx-n-docs">1,000</strong><span>documents routed</span></div>
    <div><strong class="fx-v fx-n-cout">${_FX_DATA["total"]:.2f}</strong><span>spent, assumed prices</span></div>
    <div><strong>{_FX_DATA["justesse"]:g}%</strong><span>mean accuracy per field</span></div>
  </div>
</section>
<script>{JS_FLUX}</script>'''

# ── THE FOUR LIVING HEROES of the catalogue pages (Arslane picked them on 25/10 from the five-concept mockups in
# sessions/chef/maquettes-site-2510): Screening "the sphere" (maquettes-screening-2.py, n=2), Scoring "the seven
# lamps" (maquettes-scoring.py, n=4), Dossier "the board" (maquettes-dossier.py, n=2), Monitoring "the skyline"
# (maquettes-monitoring.py, n=5, with his fix: the tower signs no longer collide). Each is built like _HERO_FLUX:
# one section scoped under its own class, its tokens defined on that class only, every figure read here from the
# same instrument-*-donnees.json file the mockup generator reads, with the same derivations; none is typed.
# Each hero: a still frame under prefers-reduced-motion, the animation loop stopped while the canvas is off screen
# or the tab hidden, and below 900px a column layout (text, a band where the scene runs, the counters).
import math
_HV_MOTS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}

# the shared ground of the four heroes: the layout the Routing hero uses, under a per-hero class and prefix
def _hv_css(c, p, toks, fond, kicker, accent, n_cpt):
    s = c + " ." + p
    grille_cpt = ("grid-template-columns:repeat(2,minmax(0,1fr));display:grid;gap:18px 20px" if n_cpt == 4
                  else "gap:20px")
    return ("""
  @C@{@TOKS@;--@P@-texte:"Literata",Georgia,serif;--@P@-mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    position:relative;height:100vh;min-height:680px;overflow:hidden;isolation:isolate;color:var(--@P@-sur);
    font-family:var(--@P@-texte);background:@FOND@}
  @C@ canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
  @S@-grain{position:absolute;inset:0;pointer-events:none;opacity:.09;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
  @S@-vignette{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 90% at 60% 45%,transparent 48%,rgba(0,0,0,.55) 100%)}
  @S@-texte{position:absolute;left:clamp(24px,5vw,80px);top:clamp(90px,13vh,140px);max-width:min(560px,44vw);pointer-events:none;z-index:2}
  @S@-kicker{font:500 12px/1 var(--@P@-mono);letter-spacing:.2em;text-transform:uppercase;color:@KICK@;display:flex;align-items:center;gap:10px}
  @S@-kicker i{width:7px;height:7px;border-radius:50%;background:@ACC@;box-shadow:0 0 12px @ACC@;animation:@P@-pouls 1.6s ease-in-out infinite}
  @keyframes @P@-pouls{50%{opacity:.35}}
  @C@ h1{margin:18px 0 0;font-size:clamp(38px,3.9vw,60px);line-height:1.04;font-weight:600;letter-spacing:-.02em;color:var(--@P@-sur)}
  @S@-lede{margin:18px 0 0;font-size:17px;line-height:1.55;color:var(--@P@-pale);max-width:44ch}
  @S@-lede>span{display:block;margin-top:14px}
  @S@-etiquettes{position:absolute;inset:0;pointer-events:none;z-index:2}
  @S@-bande{display:none}
  @S@-cpt{position:absolute;left:clamp(24px,5vw,80px);bottom:clamp(28px,6vh,56px);display:flex;gap:44px;pointer-events:none;z-index:2}
  @S@-cpt div{display:flex;flex-direction:column;gap:6px}
  @S@-cpt strong{font:600 38px/1 var(--@P@-texte);font-variant-numeric:tabular-nums;color:var(--@P@-sur)}
  @S@-cpt strong small{font-size:16px;color:var(--@P@-pale);font-weight:400}
  @S@-cpt span{font:400 11px/1 var(--@P@-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--@P@-pale)}
  @media (max-width:1080px){@C@{height:calc(100vh - 70px)}}
  @media (max-width:899px){
    @C@{height:auto;min-height:0;display:flex;flex-direction:column;padding:40px 0 32px}
    @S@-texte{position:relative;left:auto;top:auto;max-width:none;padding:0 24px}
    @C@ h1{font-size:34px}
    @S@-lede{font-size:16px}
    @S@-bande{display:block}
    @S@-cpt{position:relative;left:auto;bottom:auto;padding:0 24px;@GRILLE@}
    @S@-cpt div{flex:1 1 0;min-width:0}
    @S@-cpt strong{font-size:26px}
    @S@-cpt strong small{font-size:13px}
    @S@-cpt span{font-size:10px;line-height:1.35;letter-spacing:.12em}
  }
  @media (prefers-reduced-motion:reduce){@S@-kicker i{animation:none}}
""".replace("@S@", s).replace("@C@", c).replace("@TOKS@", toks).replace("@FOND@", fond).replace("@KICK@", kicker)
       .replace("@ACC@", accent).replace("@GRILLE@", grille_cpt).replace("@P@", p))


def _hv_boucle(p):
    """The loop every hero shares: it runs only while its canvas is on screen and the tab visible, and stops
    (no frame requested at all) otherwise; `pas(dt_seconds, now)` draws one frame."""
    return r"""
  let P_vu=false, P_roule=false, P_der=0, P_pret=false;   // P_pret: set once the first fit() has laid the scene out
  function P_boucle(now){ if (!P_vu || document.hidden){ P_roule=false; return; }
    requestAnimationFrame(P_boucle); const dt=P_der?Math.min(.05,(now-P_der)/1000):.016; P_der=now; pas(dt, now); }
  function P_lancer(){ if (calme || !P_pret || P_roule || !P_vu || document.hidden) return; P_roule=true; P_der=0; requestAnimationFrame(P_boucle); }
  new IntersectionObserver(([e])=>{ P_vu=e.isIntersecting; P_lancer(); }, {threshold:.1}).observe(cv);
  document.addEventListener("visibilitychange", P_lancer);
""".replace("P_", p + "_")


# ── 1 · SCREENING, THE SPHERE (maquettes-screening-2.py, concept 2). 120 pairs become 1,440 points on a slowly
# turning globe, latitude = score (the pole = identical). The bar is a glowing latitude plane cutting the globe:
# above it is flagged (green real matches, rose false alerts), below it let through (amber missed, grey cleared).
# DERIVED, as in the generator: a pair's score is the highest threshold at which it is still counted (from the
# cumulative counts of the sealed grid); a pair never flagged sits at 0.44. Only the recommended method is shipped.
_SP_SRC = json.loads((BASE / "instrument-screening-donnees.json").read_text())
_SP_A, _SP_REC = _SP_SRC["authored"], _SP_SRC["recommandee"]
def _sp_scores(cle, n):
    g = _SP_A["grille"][_SP_REC["palier"]]; ts = sorted(g, key=float); out = []
    for i in range(n):
        s = [float(t) for t in ts if g[t][cle]["succes"] > i]
        out.append(max(s) if s else 0.44)
    return out
_SP_DATA = {"nM": _SP_A["nMatch"], "nD": _SP_A["nDifferent"],
            "m": _sp_scores("rappel", _SP_A["nMatch"]), "f": _sp_scores("fauxPositifs", _SP_A["nDifferent"]),
            "grid": {t: [c["rappel"]["succes"], c["fauxPositifs"]["succes"]] for t, c in _SP_A["grille"][_SP_REC["palier"]].items()}}
_SP_DEPART = _SP_DATA["grid"]["0.75"]   # the bar starts at 0.75 (the middle of its breath), the still frame keeps it
CSS_SPHERE = _hv_css(".sphere-hero", "sp", "--sp-sur:#f1e6e4;--sp-pale:#b59a9c;--sp-rubis:#d64a5c;--sp-rose:#ff8a98;--sp-vert:#7fd6a6;--sp-ambre:#e3b062",
                     "radial-gradient(75% 75% at 70% 51%,#33191f,#241217 50%,#120709)", "var(--sp-rose)", "var(--sp-rubis)", 4) + r"""
  .sphere-hero .sp-texte{max-width:min(520px,40vw)}
  .sphere-hero h1{font-size:clamp(36px,3.6vw,56px);line-height:1.05}
  .sphere-hero h1 em{font-style:normal;color:var(--sp-rose)}
  .sphere-hero .sp-lede>span{margin-top:12px}
  .sphere-hero .sp-lede b{color:var(--sp-sur);font-weight:500}
  .sphere-hero .sp-cpt{gap:40px}
  .sphere-hero .sp-cpt strong{font-size:36px}
  .sphere-hero .sp-cpt .sp-v{color:var(--sp-vert)}.sphere-hero .sp-cpt .sp-r{color:var(--sp-rose)}.sphere-hero .sp-cpt .sp-o{color:var(--sp-ambre)}
  .sphere-hero .sp-lab{position:absolute;font:500 11px/1 var(--sp-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--sp-sur);white-space:nowrap;padding:5px 8px;border-radius:6px;background:rgba(24,11,15,.6)}
  .sphere-hero .sp-lab em{font-style:normal;color:var(--sp-rose)}
  @media (max-width:899px){
    .sphere-hero .sp-texte{max-width:none}
    .sphere-hero h1{font-size:34px}
    .sphere-hero .sp-bande{height:380px}
    .sphere-hero .sp-cpt{gap:18px 20px}
    .sphere-hero .sp-cpt strong{font-size:26px}
  }
"""
JS_SPHERE = (r"""
(function(){
const D = __DATA__;
const hero = document.querySelector(".sphere-hero"); if (!hero) return;
const cv = hero.querySelector("canvas"), x = cv.getContext("2d"), bande = hero.querySelector(".sp-bande"), couche = hero.querySelector(".sp-etiquettes");
const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
const tk = t=>Math.round(Math.min(1,Math.max(.5,t))*100)/100;
const cls = (p,t)=>p.v>=tk(t)-1e-9?(p.m?"caught":"fals"):(p.m?"missed":"clear");
const norm = v=>(Math.min(1,Math.max(.44,v))-.44)/.56;              // 0.44 (never flagged) -> 0, 1.00 -> 1
const breath = ts=>.75+Math.sin(ts/5200)*.15;                        // the bar breathes between 0.60 and 0.90
const spread = u=>Math.pow(Math.max(0,u),2.5), unspread = u=>Math.pow(Math.max(0,u),.4);
const RGB = {caught:[127,214,166],fals:[255,138,152],missed:[227,176,98],clear:[150,120,124],neutre:[241,230,228]};
const ON = c=>c==="caught"||c==="fals";
let rnd = (s=>()=>(s=(s*16807)%2147483647)/2147483647)(7);
const gauss = ()=>Math.sqrt(-2*Math.log(1-rnd()))*Math.cos(6.283*rnd());
let W=0, H=0, R=1;
const SP = {};
function spr(rgb,r){ r=Math.max(.125,Math.round(r*8)/8); const k=rgb+"|"+r; if (SP[k]) return SP[k];   // radius rounded to 1/8 px: the cache stays bounded
  const c=document.createElement("canvas"), z=Math.ceil(r*6*2); c.width=c.height=z; const g=c.getContext("2d"), gr=g.createRadialGradient(z/2,z/2,0,z/2,z/2,z/2);
  gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.18,`rgba(${rgb},.85)`); gr.addColorStop(.45,`rgba(${rgb},.18)`); gr.addColorStop(1,`rgba(${rgb},0)`);
  g.fillStyle=gr; g.fillRect(0,0,z,z); return SP[k]=c; }
const dot = (sp,px,py,r)=>x.drawImage(sp,px-r*3,py-r*3,r*6,r*6);
function bg(cx,cy){ const g=x.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.72); g.addColorStop(0,"#33191f"); g.addColorStop(.5,"#241217"); g.addColorStop(1,"#120709");
  x.globalCompositeOperation="source-over"; x.fillStyle=g; x.fillRect(0,0,W,H); }
const M = {x:null, y:null};
hero.addEventListener("pointermove", e=>{ const b=hero.getBoundingClientRect(); M.x=e.clientX-b.left; M.y=e.clientY-b.top; }, {passive:true});
hero.addEventListener("pointerleave", ()=>{ M.x=M.y=null; });
const L = document.createElement("div"); L.className="sp-lab"; couche.appendChild(L);
const N = [0,1,2,3].map(i=>hero.querySelector(".sp-n"+i));
const P = [...D.m.map(v=>({v,m:1})), ...D.f.map(v=>({v,m:0}))], pts=[], tilt=.46;
P.forEach(p=>{ const ly=spread(norm(p.v))*1.7-.85, lon0=rnd()*6.283;
  for (let k=0;k<12;k++){ const y=Math.max(-.9,Math.min(.9,ly+gauss()*.018)), lon=lon0+gauss()*.22; pts.push({p,y,lon,rr:Math.sqrt(1-y*y),r:1.1+rnd()*1.2}); } });
const latY = t=>spread(norm(t))*1.7-.85; let t=.75, spin=0;
// wide: the globe right of the text; narrow: centred in its own band under the text
function geo(){ if (W<900){ const top=bande.offsetTop, h=bande.offsetHeight; return [W/2, top+h/2, Math.min(W*.4,h*.44)]; }
  return [W*.705, H*.51, Math.min(W*.25,H*.39)]; }
function frame(ts,dt){ const [cx,cy,Rs]=geo(), ct=Math.cos(tilt), st=Math.sin(tilt); spin+=dt*.00024; bg(cx,cy);
  const inS = M.x!=null && Math.hypot(M.x-cx,M.y-cy)<Rs*1.2;
  const tg = inS ? .44+unspread((cy+.85*Rs*ct-M.y)/(1.7*Rs*ct))*.56 : breath(ts); t += (Math.min(.98,Math.max(.5,tg))-t)*.06;
  const yb=latY(t), rb=Math.sqrt(1-yb*yb), ey=cy-yb*ct*Rs;
  // core glow and faint wire
  x.globalCompositeOperation="lighter"; const core=x.createRadialGradient(cx,cy,0,cx,cy,Rs*1.05); core.addColorStop(0,"rgba(214,74,92,.16)"); core.addColorStop(.7,"rgba(214,74,92,.05)"); core.addColorStop(1,"rgba(214,74,92,0)");
  x.fillStyle=core; x.fillRect(cx-Rs*1.1,cy-Rs*1.1,Rs*2.2,Rs*2.2);
  x.globalCompositeOperation="source-over"; x.strokeStyle="rgba(255,138,152,.07)"; x.lineWidth=1;
  for (const y of [-.6,-.3,0,.3,.6]){ const r=Math.sqrt(1-y*y); x.beginPath(); x.ellipse(cx,cy-y*ct*Rs,r*Rs,r*Rs*st,0,0,7); x.stroke(); }
  x.beginPath(); x.arc(cx,cy,Rs,0,7); x.stroke();
  // the plane, back half
  x.strokeStyle="rgba(255,138,152,.35)"; x.lineWidth=1.2; x.beginPath(); x.ellipse(cx,ey,rb*Rs,rb*Rs*st,0,Math.PI,2*Math.PI); x.stroke();
  const pl=x.createRadialGradient(cx,ey,0,cx,ey,rb*Rs); pl.addColorStop(0,"rgba(214,74,92,.22)"); pl.addColorStop(1,"rgba(214,74,92,.04)"); x.fillStyle=pl; x.beginPath(); x.ellipse(cx,ey,rb*Rs,rb*Rs*st,0,0,7); x.fill();
  // points, back to front
  for (const q of pts){ const a=q.lon+spin, X=q.rr*Math.cos(a), Z=q.rr*Math.sin(a); q.Z=q.y*st+Z*ct; q.sx=cx+X*Rs; q.sy=cy-(q.y*ct-Z*st)*Rs; }
  pts.sort((a,b)=>a.Z-b.Z); x.globalCompositeOperation="lighter";
  for (const q of pts){ const c=cls(q.p,t), on=ON(c), dep=(q.Z+1)/2, near=Math.abs(q.y-yb)<.03; const rgb=near&&on?RGB.neutre:RGB[c];
    x.globalAlpha=(.25+.75*dep)*(on?1:(c==="missed"?.7:.3)); const r=q.r*(on?1.25:.9)*(.7+.5*dep); dot(spr(rgb,r),q.sx,q.sy,r); }
  x.globalAlpha=1;
  // the plane, front half
  x.globalCompositeOperation="source-over"; x.strokeStyle="#ffd5da"; x.lineWidth=1.6; x.beginPath(); x.ellipse(cx,ey,rb*Rs,rb*Rs*st,0,0,Math.PI); x.stroke();
  x.globalCompositeOperation="lighter"; x.strokeStyle="rgba(214,74,92,.5)"; x.lineWidth=7; x.beginPath(); x.ellipse(cx,ey,rb*Rs,rb*Rs*st,0,0,Math.PI); x.stroke();
  x.globalCompositeOperation="source-over";
  L.style.left=Math.min(W-96,cx+rb*Rs+12)+"px"; L.style.top=(ey-11)+"px"; L.innerHTML=`<em>bar ${tk(t).toFixed(2)}</em>`;
  const g=D.grid[tk(t).toFixed(2)]; N[0].textContent=tk(t).toFixed(2); N[1].innerHTML=g[0]+" <small>/ "+D.nM+"</small>";
  N[2].innerHTML=g[1]+" <small>/ "+D.nD+"</small>"; N[3].textContent=D.nM-g[0]; }
function fit(){ R=Math.min(1.5,devicePixelRatio||1); W=cv.clientWidth; H=cv.clientHeight; cv.width=W*R; cv.height=H*R; x.setTransform(R,0,0,R,0,0);
  if (calme) frame(0,16); }   // reduced motion: one still frame, the bar at 0.75, redrawn on resize
const pas = (dt,now)=>frame(now, dt*1000);
""" + _hv_boucle("sp") + r"""
(document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{ fit(); new ResizeObserver(fit).observe(cv); sp_pret=true; sp_lancer(); });
})();
""").replace("__DATA__", json.dumps(_SP_DATA, separators=(",", ":")))
_HERO_SPHERE = f'''<section class="sphere-hero" aria-label="Screening, live">
  <canvas aria-hidden="true"></canvas>
  <div class="sp-grain"></div><div class="sp-vignette"></div><div class="sp-etiquettes" aria-hidden="true"></div>
  <div class="sp-texte">
    <div class="sp-kicker"><i></i>Screening &#183; measured live</div>
    <h1>See what your screening catches, and what it <em>flags incorrectly.</em></h1>
    <p class="sp-lede">A threshold is the score above which two names count as a match.<span>The bar moves on its own; take it: <b>point at the globe, higher or lower, the plane follows.</b></span></p>
  </div>
  <div class="sp-bande" aria-hidden="true"></div>
  <div class="sp-cpt" aria-live="off">
    <div><strong class="sp-n0">0.75</strong><span>the bar</span></div>
    <div><strong class="sp-v sp-n1">{_SP_DEPART[0]} <small>/ {_SP_DATA["nM"]}</small></strong><span>real matches caught</span></div>
    <div><strong class="sp-r sp-n2">{_SP_DEPART[1]} <small>/ {_SP_DATA["nD"]}</small></strong><span>false alerts</span></div>
    <div><strong class="sp-o sp-n3">{_SP_DATA["nM"] - _SP_DEPART[0]}</strong><span>matches missed</span></div>
  </div>
</section>
<script>{JS_SPHERE}</script>'''


# ── 2 · SCORING, THE SEVEN LAMPS (maquettes-scoring.py, concept 4). Seven lamps in a row, one per factor; the
# threshold is a cursor on a long ruler, rising from 0.50 to 1.00. Each lamp burns with the number of risky customers
# it still catches: the 42 are its filaments, the caught ones orbit tight in the light, the missed ones drift out
# into the dark; amber at the rim, the quiet customers it pushes up. The page gets counts, not rates, as in the mockup.
_LP_SRC = json.loads((BASE / "instrument-scoring-donnees.json").read_text())
_LP_CLES = ["%.2f" % s for s in _LP_SRC["seuils"]]
_LP_G = _LP_SRC["authored"]["grille"]
_LP_F = [p["id"] for p in sorted(_LP_SRC["paliers"], key=lambda p: p["rang"])]
_LP_DATA = {"seuils": _LP_SRC["seuils"], "montres": _LP_SRC["seuilsMontres"], "paliers": _LP_F,
            "n": {"esc": _LP_SRC["authored"]["nEscalated"], "main": _LP_SRC["authored"]["nMaintained"]},
            "caught": {f: [_LP_G[f][k]["rappel"]["succes"] for k in _LP_CLES] for f in _LP_F},
            "faux": {f: [_LP_G[f][k]["fauxPositifs"]["succes"] for k in _LP_CLES] for f in _LP_F}}
# shipped as tool data in an application/json block (exception 2 of garde-orthographe): it carries the sealed
# factor name "behaviour", which the American-spelling guard would refuse as a script string
for _f in _LP_F:   # the lamps assume the counts never grow with the threshold (the generator asserts the same)
    _c, _x = _LP_DATA["caught"][_f], _LP_DATA["faux"][_f]
    if not (all(_c[i] >= _c[i + 1] for i in range(len(_c) - 1)) and all(_x[i] >= _x[i + 1] for i in range(len(_x) - 1))):
        sys.exit(f"instrument-scoring-donnees.json : the counts of {_f} grow with the threshold; the lamps would lie")
_LP_REC = _LP_SRC["recommandee"]
_LP_ALLUMES = sum(1 for f in _LP_F if _LP_DATA["caught"][f][0] > 0)        # the counters without script: at 0.50
_LP_MEILLEUR = max(_LP_DATA["caught"][f][0] for f in _LP_F)
CSS_LAMPES = _hv_css(".lampes-hero", "lp", "--lp-sur:#ede6f7;--lp-pale:#b9a9d4;--lp-vif:#9b6fe0;--lp-clair:#e2d3ff;--lp-ambre:#e3b062",
                     "radial-gradient(78% 78% at 72% 50%,#1f1538,#140d28 50%,#080513)", "var(--lp-vif)", "var(--lp-vif)", 3) + r"""
  .lampes-hero h1 em{font-style:normal;color:var(--lp-vif)}
  .lampes-hero .lp-lede .lp-clair{color:var(--lp-sur)}
  .lampes-hero .lp-lede b{color:var(--lp-vif);font-weight:600}
  .lampes-hero .lp-cpt{gap:48px}
  .lampes-hero .lp-cpt strong.lp-v{color:var(--lp-vif)}
  .lampes-hero .lp-eti{position:absolute;display:flex;flex-direction:column;gap:4px;white-space:nowrap;transition:opacity .25s ease;transform:translateX(-50%);align-items:center;text-align:center}
  .lampes-hero .lp-eti b{font:500 14px/1.1 var(--lp-texte);color:var(--lp-sur)}
  .lampes-hero .lp-eti span{font:400 11px/1 var(--lp-mono);letter-spacing:.06em;color:var(--lp-pale);font-variant-numeric:tabular-nums}
  .lampes-hero .lp-eti span.lp-on{color:var(--lp-clair)}
  .lampes-hero .lp-eti em{font:400 11px/1 var(--lp-mono);font-style:normal;color:var(--lp-ambre);letter-spacing:.06em}
  .lampes-hero .lp-eti.lp-off{opacity:.3}
  .lampes-hero .lp-lecture{position:absolute;display:flex;flex-direction:column;align-items:center;gap:6px;transform:translate(-50%,-50%)}
  .lampes-hero .lp-lecture b{font:500 clamp(26px,2.4vw,40px)/1 var(--lp-mono);letter-spacing:-.02em;color:var(--lp-sur);font-variant-numeric:tabular-nums}
  .lampes-hero .lp-lecture span{font:400 10.5px/1 var(--lp-mono);letter-spacing:.2em;text-transform:uppercase;color:var(--lp-pale)}
  .lampes-hero .lp-tick{position:absolute;font:400 10.5px/1 var(--lp-mono);color:var(--lp-pale);transform:translate(-50%,-50%);font-variant-numeric:tabular-nums}
  @media (max-width:899px){
    .lampes-hero .lp-bande{height:380px}
    .lampes-hero .lp-cpt{gap:20px}
    .lampes-hero .lp-eti b{font-size:12px}
    .lampes-hero .lp-eti span,.lampes-hero .lp-eti em{font-size:10px}
    .lampes-hero .lp-tick{font-size:9.5px}
  }
  @media (prefers-reduced-motion:reduce){.lampes-hero .lp-eti{transition:none}}
"""
JS_LAMPES = (r"""
(function(){
const hero = document.querySelector(".lampes-hero"); if (!hero) return;
const D = JSON.parse(hero.querySelector(".lp-donnees").textContent);
const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
const T = D.seuils, NT = T.length, F = D.paliers, NF = F.length;
const NOM = {geography:"Geography",activity:"Activity",product:"Product",exposure:"Exposure",structure:"Structure",behaviour:"Behavior",tenure:"Tenure"};
const C = {vif:[155,111,224], clair:[226,211,255], pale:[185,169,212], ambre:[227,176,98], blanc:[255,255,255]};
const fmt = t => t.toFixed(2);
// nearest measured threshold for a continuous value: the page never shows a figure between two cells
const idx = t => Math.max(0, Math.min(NT-1, Math.round((t-T[0])/(T[NT-1]-T[0])*(NT-1))));
const lerp = (a,b,k) => a+(b-a)*k, clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const cv = hero.querySelector("canvas"), ctx = cv.getContext("2d"), lab = hero.querySelector(".lp-etiquettes"), bande = hero.querySelector(".lp-bande");
const K = {t:hero.querySelector(".lp-k-t"), l:hero.querySelector(".lp-k-l"), c:hero.querySelector(".lp-k-c")};
let W=0, H=0, R=1, t=0, pret_=false;
const ptr = {x:-9999, y:-9999, in:false}, sprites = {};
const S = {
  sprite(rgb, r, dur){ r = Math.max(.125, Math.round(r*8)/8);   // rounded to 1/8 px so the cache stays bounded
    const k = rgb.join()+r+(dur?"d":""); if (sprites[k]) return sprites[k];
    const c = document.createElement("canvas"), s = Math.ceil(r*6*R); c.width = c.height = s; const g = c.getContext("2d");
    const gr = g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
    if (dur){ gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.3,`rgba(${rgb},.95)`); gr.addColorStop(.42,`rgba(${rgb},.25)`); gr.addColorStop(1,`rgba(${rgb},0)`); }
    else { gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.18,`rgba(${rgb},.85)`); gr.addColorStop(.45,`rgba(${rgb},.18)`); gr.addColorStop(1,`rgba(${rgb},0)`); }
    g.fillStyle = gr; g.fillRect(0,0,s,s); return sprites[k] = c; },
  point(rgb, x, y, r, a, dur){ const sp = S.sprite(rgb, r, dur), s = r*6; ctx.globalAlpha = a; ctx.drawImage(sp, x-s/2, y-s/2, s, s); },
  fond(cx, cy, drift){ ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    const bg = ctx.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.78);
    bg.addColorStop(0,"#1f1538"); bg.addColorStop(.5,"#140d28"); bg.addColorStop(1,"#080513");
    ctx.fillStyle = bg; ctx.fillRect(0,0,W,H);
    const px = ((drift*5) % 48 + (ptr.in ? (ptr.x/W-.5)*14 : 0)), py = (ptr.in ? (ptr.y/H-.5)*10 : 0);
    ctx.strokeStyle = "rgba(226,211,255,.035)"; ctx.lineWidth = 1; ctx.beginPath();
    for (let x=(px%48)-48; x<W; x+=48){ ctx.moveTo(x,0); ctx.lineTo(x,H); }
    for (let y=(py%48)-48; y<H; y+=48){ ctx.moveTo(0,y); ctx.lineTo(W,y); } ctx.stroke(); },
  el(cls, html){ const el = document.createElement("div"); el.className = cls; el.innerHTML = html; lab.appendChild(el); return el; },
  place(el, x, y){ el.style.left = x+"px"; el.style.top = y+"px"; },
};
// the seven lamps (concept 4 of the mockup, unchanged but for the narrow band and the staggered names)
let G = {}, thr = .5, eti = [], curseur, ticks = [], lamps = [];
const sDe = x => clamp(T[0] + (x-G.x0)/(G.x1-G.x0)*(T[NT-1]-T[0]), T[0], T[NT-1]);
const xDe = s => G.x0 + (s-T[0])/(T[NT-1]-T[0])*(G.x1-G.x0);
const FIXE = 5.0;
function geo(){ const etroit = W < 900; let x0, x1, cy, ry;
  if (etroit){ const top = bande.offsetTop, h = bande.offsetHeight; x0 = 20; x1 = W-20; cy = top+82; ry = top+h-58; }
  else { x0 = Math.max(W*.49, W-760); x1 = W*.95; cy = H*.42; ry = H*.72; }
  const pas = (x1-x0)/NF; G = {x0, x1, pas, cy, ry, rmax: Math.min(64, pas*.5)};
  G.cx = F.map((f,k)=> x0 + (k+.5)*pas);
  if (!eti.length){ eti = F.map(f=> S.el("lp-eti", `<b>${NOM[f]}</b><span></span><em></em>`)); curseur = S.el("lp-lecture", "<b></b><span>threshold</span>"); ticks = D.montres.map(m=> S.el("lp-tick", fmt(m)));
    lamps = F.map(()=>({L:0, fil: Array.from({length:D.n.esc}, (_,k)=>({a:Math.random()*7, r:1, v:.7+Math.random()*.9, s:Math.random()<.5?1:-1, e:Math.random()})),
      amb: Array.from({length:D.n.main}, ()=>({a:Math.random()*7, v:.5+Math.random()*.6})) })); }
  // the names under the lamps: one row while they fit (the mockup, wide screens), two alternating rows when the lamps close up
  const etage = pas < 90;
  eti.forEach((el,k)=> S.place(el, G.cx[k], G.cy + G.rmax + (etage ? 40 : 70) + (etage && k%2 ? 44 : 0)));
  ticks.forEach((el,j)=> S.place(el, xDe(D.montres[j]), G.ry + 24));
}
function frame(dt, t){
  const dedans = ptr.in && ptr.x > G.x0-20 && ptr.x < G.x1+20 && ptr.y > G.ry-60 && ptr.y < G.ry+60;
  let cible; if (dedans) cible = sDe(ptr.x); else { const u = (t % 16)/16; cible = u < .8 ? T[0] + (T[NT-1]-T[0])*(u/.8) : T[NT-1] - (T[NT-1]-T[0])*((u-.8)/.2); }
  thr = lerp(thr, cible, Math.min(1, dt*(dedans?6:2.5))); const i = idx(thr), xC = xDe(thr);
  S.fond(W*.72, H*.5, t);
  ctx.globalCompositeOperation = "lighter";
  let lit = 0, bestC = -1;
  F.forEach((f,k)=>{ const c = D.caught[f][i], x = D.faux[f][i], lamp = lamps[k], cx = G.cx[k], cy = G.cy + Math.sin(t*.4+k)*4;
    lamp.L = lerp(lamp.L, c/D.n.esc, Math.min(1, dt*3)); const L = lamp.L; if (c > 0) lit++; if (c > bestC) bestC = c;
    const rc = 14 + G.rmax*.86*L, kh = Math.min(1, G.pas/90);   // kh: the halos shrink with the pitch, so close lamps stay seven
    // halo, core, and the pool of light on the floor beneath
    S.point(C.vif, cx, cy, rc*2.3*kh, .25+.55*L);
    S.point(C.vif, cx, cy, rc*1.3*kh, .3+.5*L);
    S.point(C.clair, cx, cy, rc*.8, .4+.55*L, true);
    S.point(C.blanc, cx, cy, Math.max(3, rc*.26), .55+.4*L);
    ctx.save(); ctx.translate(cx, G.ry-6); ctx.scale(1, .18); S.point(C.vif, 0, 0, rc*2.2, .12+.35*L); ctx.restore();
    // the filaments: index below the catch orbits in the light, the rest drifts out
    lamp.fil.forEach((p,j)=>{ const dedansL = j < c; const rt = dedansL ? 6 + (rc-4)*p.e : G.rmax*1.25 + 26*p.e + 10*Math.sin(t*.7+p.a);
      p.r = lerp(p.r, rt, Math.min(1, dt*2.2)); p.a += dt*p.v*p.s*(dedansL ? 1.6 : .25);
      const px = cx + Math.cos(p.a)*p.r, py = cy + Math.sin(p.a)*p.r*.78;
      dedansL ? S.point(C.clair, px, py, 2, .95) : S.point(C.pale, px, py, 1.8, .4); });
    // the quiet customers it pushes up: amber at the rim
    for (let j=0;j<x;j++){ const p = lamp.amb[j]; p.a += dt*p.v; const r = rc + 14 + 6*Math.sin(t+p.a);
      S.point(C.ambre, cx + Math.cos(p.a)*r, cy + Math.sin(p.a)*r*.8, 2.4, .95); }
    eti[k].children[1].textContent = `${c} / ${D.n.esc}`; eti[k].children[1].className = c ? "lp-on" : ""; eti[k].children[2].textContent = x ? `${x} false` : "";
    eti[k].classList.toggle("lp-off", c===0); });
  // the ruler
  ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
  ctx.strokeStyle = "rgba(226,211,255,.14)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(G.x0, G.ry); ctx.lineTo(G.x1, G.ry); ctx.stroke();
  ctx.strokeStyle = "rgba(226,211,255,.3)"; D.montres.forEach(m=>{ const x = xDe(m); ctx.beginPath(); ctx.moveTo(x, G.ry-5); ctx.lineTo(x, G.ry+5); ctx.stroke(); });
  ctx.globalCompositeOperation = "lighter";
  const lit_ = ctx.createLinearGradient(G.x0, 0, xC, 0); lit_.addColorStop(0,"rgba(155,111,224,.05)"); lit_.addColorStop(1,"rgba(155,111,224,.6)");
  ctx.fillStyle = lit_; ctx.fillRect(G.x0, G.ry-1.5, xC-G.x0, 3);
  S.point(C.clair, xC, G.ry, 7, .95); S.point(C.vif, xC, G.ry, 22, .5);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
  S.place(curseur, xC, G.ry - 44); curseur.firstChild.textContent = fmt(T[i]);
  K.t.textContent = fmt(T[i]); K.l.textContent = `${lit} / ${NF}`; K.c.textContent = bestC;
}
function fixe(){ for (let i=0;i<240;i++) frame(1/60, FIXE + i/60); }   // reduced motion: the scene settles for a few seconds off screen, then one frame stays
function fit(){ R = Math.min(1.5, devicePixelRatio||1); W = cv.clientWidth; H = cv.clientHeight; cv.width = W*R; cv.height = H*R;
  ctx.setTransform(R,0,0,R,0,0); for (const k in sprites) delete sprites[k]; geo(); if (calme && pret_) fixe(); }
hero.addEventListener("pointermove", e=>{ const b = cv.getBoundingClientRect(); ptr.x = e.clientX-b.left; ptr.y = e.clientY-b.top; ptr.in = true; }, {passive:true});
hero.addEventListener("pointerleave", ()=>{ ptr.in = false; ptr.x = ptr.y = -9999; });
const pas = dt=>{ t += dt; frame(dt, t); };
""" + _hv_boucle("lp") + r"""
(document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{ pret_ = true; fit(); new ResizeObserver(fit).observe(cv); if (calme) fixe(); else { lp_pret=true; lp_lancer(); } });
})();
""")
_HERO_LAMPES = f'''<section class="lampes-hero" aria-label="Scoring, live">
  <canvas aria-hidden="true"></canvas>
  <div class="lp-grain"></div><div class="lp-vignette"></div><div class="lp-etiquettes" aria-hidden="true"></div>
  <div class="lp-texte">
    <div class="lp-kicker"><i></i>Scoring &#183; measured live</div>
    <h1>See which risk factors separate a risky customer <em>from a quiet one.</em></h1>
    <p class="lp-lede">A factor's threshold is the score above which it pushes a customer up a rating.<span>{_HV_MOTS[len(_LP_F)]} factors, run at every threshold from {_LP_DATA["seuils"][0]:.2f} to {_LP_DATA["seuils"][-1]:.2f}, over the {_LP_DATA["n"]["esc"] + _LP_DATA["n"]["main"]} reviews your analysts already decided.</span><span class="lp-clair"><b>{_LP_REC["plusForteBorne"]:.2f}</b> is the strongest recall lower bound a single factor reaches. The floor is {_LP_REC["plancher"]:.2f}.</span></p>
  </div>
  <div class="lp-bande" aria-hidden="true"></div>
  <div class="lp-cpt" aria-live="off">
    <div><strong class="lp-v lp-k-t">{_LP_DATA["seuils"][0]:.2f}</strong><span>threshold</span></div>
    <div><strong class="lp-k-l">{_LP_ALLUMES} / {len(_LP_F)}</strong><span>factors still lit</span></div>
    <div><strong class="lp-k-c">{_LP_MEILLEUR}</strong><span>risky caught, brightest</span></div>
  </div>
  <script type="application/json" class="lp-donnees">{json.dumps(_LP_DATA, separators=(",", ":"))}</script>
</section>
<script>{JS_LAMPES}</script>'''


# ── 3 · DOSSIER, THE BOARD (maquettes-dossier.py, concept 2). Each seal recomputed in public: five rows of sixteen
# split-flap tiles (the four reports, then the dossier's own fingerprint). A read head crosses a row; the tiles ahead
# flutter through hex, the ones behind settle on the seal's character and glow; when the row is done its five
# controls light one after the other. Read from the sealed public dossier, with the generator's derivations: the
# checks held = the verdicts with tenu=true; the oldest report's age = the largest joursDepuis.
_TB_SRC = json.loads((BASE / "instrument-dossier-donnees.json").read_text())
_TB_RAPPORTS = [{"q": k, "fichier": q["fichier"], "sceau": q["sceau"],
                 "verdicts": [{"c": v["controle"], "ok": v["tenu"]} for v in q["verdicts"]]}
                for k, q in _TB_SRC["questions"].items()]
_TB_TENUS = sum(1 for r in _TB_RAPPORTS for v in r["verdicts"] if v["ok"])
_TB_DATA = {"reports": _TB_RAPPORTS, "controls": _TB_SRC["controles"]["presents"], "auJour": _TB_SRC["reglages"]["auJour"],
            "held": _TB_TENUS, "empreinte": _TB_SRC["provenance"]["empreinte"]}
_TB_TOTAL = len(_TB_RAPPORTS) * len(_TB_DATA["controls"])
_TB_DOYEN = max(q["joursDepuis"] for q in _TB_SRC["questions"].values())
for _r in _TB_RAPPORTS + [{"q": "dossier", "sceau": _TB_DATA["empreinte"]}]:
    if len(_r["sceau"]) < 16:
        sys.exit(f"instrument-dossier-donnees.json : the seal of {_r['q']} has fewer than the board's sixteen tiles")
CSS_TABLEAU = _hv_css(".tableau-hero", "tb", "--tb-sur:#efede6;--tb-pale:#b8b6ad;--tb-gra:#8a8a96;--tb-arg:#e8e6df;--tb-vert:#57b184;--tb-vclair:#a5f7cb",
                      "radial-gradient(120% 95% at 68% 45%,#121216,#0c0c10 55%,#070709)", "var(--tb-gra)", "var(--tb-arg)", 3) + r"""
  .tableau-hero h1{font-size:clamp(36px,3.7vw,56px);line-height:1.05}
  .tableau-hero h1 em{font-style:normal;color:var(--tb-gra)}
  .tableau-hero .tb-lede{max-width:46ch}
  .tableau-hero .tb-lede>span{margin-top:12px}
  .tableau-hero .tb-lede b{color:var(--tb-sur);font-weight:500}
  .tableau-hero .tb-lede .tb-fig{color:var(--tb-sur)}.tableau-hero .tb-lede .tb-fig b:first-child{color:var(--tb-vert)}
  .tableau-hero .tb-cpt strong small{font-size:18px;font-weight:500}
  .tableau-hero .tb-cpt .tb-v{color:var(--tb-vert)}
  .tableau-hero .tb-row{position:absolute;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;column-gap:16px;row-gap:6px;white-space:nowrap;transform:translateY(-100%)}
  .tableau-hero .tb-row b{font:500 12px/1 var(--tb-mono);color:var(--tb-sur);letter-spacing:.02em}
  .tableau-hero .tb-row b small{color:var(--tb-pale);margin-left:10px;letter-spacing:.1em;text-transform:uppercase;font-size:10.5px}
  .tableau-hero .tb-row em{display:flex;gap:7px;font-style:normal}
  .tableau-hero .tb-row em s{text-decoration:none;font:500 10px/1 var(--tb-mono);letter-spacing:.14em;text-transform:uppercase;color:rgba(138,138,150,.45);transition:color .25s,text-shadow .5s}
  .tableau-hero .tb-row em s.tb-on{color:var(--tb-vclair);text-shadow:0 0 12px rgba(165,247,203,.7)}
  @media (max-width:899px){
    .tableau-hero h1{font-size:34px}
    .tableau-hero .tb-lede{max-width:none}
    .tableau-hero .tb-bande{height:460px}
    .tableau-hero .tb-cpt strong small{font-size:13px}
    .tableau-hero .tb-row b{font-size:10px}
    .tableau-hero .tb-row b small{font-size:9px;margin-left:8px}
    .tableau-hero .tb-row em{gap:5px}
    .tableau-hero .tb-row em s{font-size:9px;letter-spacing:.1em}
  }
  @media (prefers-reduced-motion:reduce){.tableau-hero .tb-row em s{transition:none}}
"""
JS_TABLEAU = (r"""
(function(){
const D = __DATA__;
const hero = document.querySelector(".tableau-hero"); if (!hero) return;
const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
const MONO = '"Roboto Mono",ui-monospace,Menlo,monospace';
const ARG = [232,230,223], VCL = [165,247,203];
const NOM = {routing:"Routing",screening:"Screening",monitoring:"Monitoring",scoring:"Scoring"};
const SP = {};
function spr(rgb,r){ r=Math.max(.125,Math.round(r*8)/8); const k=rgb+"|"+r; if (SP[k]) return SP[k];   // radius rounded to 1/8 px: the cache stays bounded
  const c=document.createElement("canvas"), z=Math.ceil(r*6*2); c.width=c.height=z; const g=c.getContext("2d"), gr=g.createRadialGradient(z/2,z/2,0,z/2,z/2,z/2);
  gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.18,`rgba(${rgb},.85)`); gr.addColorStop(.45,`rgba(${rgb},.18)`); gr.addColorStop(1,`rgba(${rgb},0)`);
  g.fillStyle=gr; g.fillRect(0,0,z,z); return SP[k]=c; }
function glow(x,rgb,cx,cy,r,a){ const s=spr(rgb,r), z=r*6; x.globalAlpha=a; x.drawImage(s,cx-z/2,cy-z/2,z,z); x.globalAlpha=1; }
let rnd = (s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);
const HEX = "0123456789abcdef";
const cv = hero.querySelector("canvas"), x = cv.getContext("2d"), lab = hero.querySelector(".tb-etiquettes"), bande = hero.querySelector(".tb-bande");
const S = {W:0, H:0, t:0, mx:null, my:null, held:0, cnt:hero.querySelector(".tb-n-held")};
S.tick = n=>{ S.held+=n; S.cnt.textContent=S.held.toLocaleString("en-US"); };
function fond(cx,cy){ const {W,H}=S; x.globalCompositeOperation="source-over"; const bg=x.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.75);
  bg.addColorStop(0,"#17171c"); bg.addColorStop(.55,"#0d0d11"); bg.addColorStop(1,"#060608"); x.fillStyle=bg; x.fillRect(0,0,W,H);
  const px=S.mx!=null?(S.mx/W-.5)*14:0, py=S.my!=null?(S.my/H-.5)*10:0; x.strokeStyle="rgba(232,230,223,.035)"; x.lineWidth=1; x.beginPath();
  for (let a=(px%48)-48;a<W;a+=48){ x.moveTo(a,0); x.lineTo(a,H); } for (let a=(py%48)-48;a<H;a+=48){ x.moveTo(0,a); x.lineTo(W,a); } x.stroke(); }
const ROWS = [...D.reports.map(r=>({seal:r.sceau, titre:r.fichier, sous:NOM[r.q], ctl:r.verdicts})),
  {seal:D.empreinte, titre:"dossier fingerprint", sous:"the Dossier, "+D.auJour, ctl:D.controls.map(c=>({c, ok:D.reports.every(r=>r.verdicts.find(v=>v.c===c&&v.ok))}))}];
const N = 16, T = ROWS.map(r=>Array.from({length:N},()=>({ch:HEX[Math.floor(rnd()*16)], set:0, flip:0, glow:0})));
const RW = ROWS.map(r=>{ const e=document.createElement("div"); e.className="tb-row"; e.innerHTML=`<b>${r.titre}<small>${r.sous}</small></b><em>${r.ctl.map(v=>`<s>${v.c}</s>`).join("")}</em>`; lab.appendChild(e); return e; });
let row=0, head=-1.5, pause=0, scr=0;
// reduced motion: the board as it stands once every row has been read, each seal set and every control that holds lit
if (calme){ T.forEach((R,r)=>R.forEach((c,k)=>{ c.set=1; c.ch=ROWS[r].seal[k]; })); row=ROWS.length-1; head=N+3; scr=Infinity; }
function draw(dt){ const {W,H}=S, nar=W<900; fond(W*.72,H*.5);
  const s=nar?Math.min(W*.86/N*.84,36):Math.min(H*.078,(W*.46)/N*.84), pitch=s*1.19, bw=N*pitch-(pitch-s), x0=nar?(W-bw)/2:W-28-bw;
  // the row pitch follows its label: one line (wide screens) gives the mockup's s+42; a label wrapped on two lines gets its room
  const cle=W+"x"+H; if (cle!==S.cle){ S.cle=cle; RW.forEach(e=>{ e.style.width=bw+"px"; }); S.haut=Math.max(12,...RW.map(e=>e.offsetHeight)); }
  const rowH=s+30+S.haut;
  const mid = nar ? bande.offsetTop+bande.offsetHeight/2 : H*.5, y0=mid-(ROWS.length*rowH)/2+10;
  // the pass: head crosses the current row; then a short pause; then the next row; after the last, the board scrambles again
  if (pause>0){ pause-=dt; } else if (scr>0){ scr-=dt; if (scr<=0){ row=0; head=-1.5; } } else { head+=dt*7.5;
    if (head>N+2.5){ row++; pause=.35; head=-1.5; if (row>=ROWS.length){ row=ROWS.length-1; head=N+3; scr=1.6; T.forEach(R=>R.forEach(c=>{ c.set=0; })); } } }
  const hov=S.mx!=null?Math.floor((S.my-y0)/rowH):-1;
  ROWS.forEach((R,r)=>{ const ry=y0+r*rowH+30, cells=T[r], active=r===row&&scr<=0, ahead=active?head:(r<row?N+9:-9);
    RW[r].style.left=x0+"px"; RW[r].style.top=(ry-12)+"px"; RW[r].style.width=bw+"px";
    for (let k=0;k<N;k++){ const c=cells[k], tx=x0+k*pitch, dist=k-ahead;
      if (dist<0&&!c.set){ c.set=1; c.ch=R.seal[k]; c.glow=1; c.flip=1; S.tick(0); }
      if (!c.set){ const near=dist<4; if (near||rnd()<dt*1.2){ c.flip=1; if (rnd()<(near?.6:1)) c.ch=HEX[Math.floor(rnd()*16)]; } }
      c.flip=Math.max(0,c.flip-dt*(c.set?5:9)); c.glow=Math.max(0,c.glow-dt*.55);
      x.globalCompositeOperation="source-over"; const pl=x.createLinearGradient(0,ry,0,ry+s);
      pl.addColorStop(0,c.set?"#2a2a31":"#1c1c21"); pl.addColorStop(.5,c.set?"#1f1f25":"#15151a"); pl.addColorStop(.5,c.set?"#1a1a1f":"#111115"); pl.addColorStop(1,c.set?"#232329":"#17171c");
      x.fillStyle=pl; x.beginPath(); x.roundRect(tx,ry,s,s,4); x.fill(); x.fillStyle="rgba(0,0,0,.55)"; x.fillRect(tx,ry+s/2-.5,s,1);
      // the glyph, split at the middle like a flap; a flipping tile shows its upper half squashed
      x.save(); x.beginPath(); x.rect(tx,ry,s,s); x.clip(); x.font=`500 ${s*.62}px ${MONO}`; x.textAlign="center"; x.textBaseline="middle";
      const sq=c.flip>0?Math.abs(Math.cos(c.flip*Math.PI*2.5)):1; x.translate(tx+s/2,ry+s/2); x.scale(1,Math.max(.08,sq));
      x.fillStyle=c.set?`rgba(232,230,223,${.78+c.glow*.22})`:`rgba(138,138,150,${.35+(dist<4&&dist>=0?.35:0)})`; x.fillText(c.ch,0,1); x.restore();
      if (c.set&&c.glow>0){ x.globalCompositeOperation="lighter"; glow(x,ARG,tx+s/2,ry+s/2,s*.7,c.glow*.55); }
      if (hov===r&&S.mx>x0&&S.mx<x0+bw){ x.globalCompositeOperation="lighter"; x.fillStyle="rgba(232,230,223,.05)"; x.beginPath(); x.roundRect(tx,ry,s,s,4); x.fill(); } }
    // the head: a bright vertical bar with a halo, only on the active row
    if (active&&head>-1&&head<N+1){ const hx=x0+head*pitch; x.globalCompositeOperation="lighter"; const hg=x.createLinearGradient(hx-s*2.5,0,hx+s*.3,0);
      hg.addColorStop(0,"rgba(232,230,223,0)"); hg.addColorStop(1,"rgba(232,230,223,.22)"); x.fillStyle=hg; x.fillRect(hx-s*2.5,ry-6,s*2.8,s+12);
      x.fillStyle="rgba(232,230,223,.95)"; x.fillRect(hx-1,ry-8,2,s+16); glow(x,ARG,hx,ry+s/2,s*.9,.7); }
    // controls light one by one as the head crosses fifths of the row; stay lit once the row is done
    const done=r<row||(r===row&&head>N+1)||scr>0;
    R.ctl.forEach((v,k)=>{ const on=v.ok&&(done||(active&&head>(k+1)/R.ctl.length*N)); const el=RW[r].children[1].children[k];
      if (on&&!el.classList.contains("tb-on")&&scr<=0) S.tick(1); el.classList.toggle("tb-on",on); });
    if (done){ x.globalCompositeOperation="lighter"; x.fillStyle="rgba(165,247,203,.55)"; x.fillRect(x0-14,ry+2,3,s-4); glow(x,VCL,x0-13,ry+s/2,s*.4,.35); } });
  // the board's own frame
  x.globalCompositeOperation="source-over"; x.strokeStyle="rgba(232,230,223,.08)"; x.lineWidth=1; x.strokeRect(x0-24,y0-14,bw+48,ROWS.length*rowH+8); }
function fit(){ const r=Math.min(1.5,devicePixelRatio||1); S.W=cv.clientWidth; S.H=cv.clientHeight; cv.width=S.W*r; cv.height=S.H*r; x.setTransform(r,0,0,r,0,0);
  for (const k in SP) delete SP[k]; if (calme){ draw(0); S.held=D.held; S.cnt.textContent=String(D.held); } }
hero.addEventListener("pointermove", e=>{ const r=hero.getBoundingClientRect(); S.mx=e.clientX-r.left; S.my=e.clientY-r.top; }, {passive:true});
hero.addEventListener("pointerleave", ()=>{ S.mx=S.my=null; });
const pas = dt=>{ S.t+=dt; draw(dt); };
if (!calme) S.cnt.textContent = "0";   // the live count starts from nothing; without script, or still, it shows today's figure
""" + _hv_boucle("tb") + r"""
(document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{ fit(); new ResizeObserver(fit).observe(cv); tb_pret=true; tb_lancer(); });
})();
""").replace("__DATA__", json.dumps(_TB_DATA, separators=(",", ":")))
_HERO_TABLEAU = f'''<section class="tableau-hero" aria-label="Dossier, live">
  <canvas aria-hidden="true"></canvas>
  <div class="tb-grain"></div><div class="tb-vignette"></div><div class="tb-etiquettes" aria-hidden="true"></div>
  <div class="tb-texte">
    <div class="tb-kicker"><i></i>Dossier &#183; verified live</div>
    <h1>Check each report: present, sealed, signed, <em>fresh, consistent.</em></h1>
    <p class="tb-lede">A reviewer asks whether the whole chain still holds.<span>The Dossier reads the four reports and checks that each one is present, frozen, fresh, signed with a key you can check, and consistent with the others.</span><span class="tb-fig"><b>{_TB_TENUS} of {_TB_TOTAL}</b> checks hold today, across <b>{_TB_SRC["couverture"]["n"]} of {_TB_SRC["couverture"]["sur"]}</b> reports.</span></p>
  </div>
  <div class="tb-bande" aria-hidden="true"></div>
  <div class="tb-cpt" aria-live="off">
    <div><strong class="tb-v tb-n-held">{_TB_TENUS}</strong><span>checks held, live</span></div>
    <div><strong>{_TB_SRC["couverture"]["n"]}<small>/{_TB_SRC["couverture"]["sur"]}</small></strong><span>reports present</span></div>
    <div><strong>{_TB_DOYEN}<small> d</small></strong><span>oldest report, of {_TB_SRC["reglages"]["rythmeJours"]}</span></div>
  </div>
</section>
<script>{JS_TABLEAU}</script>'''


# ── 4 · MONITORING, THE SKYLINE (maquettes-monitoring.py, concept 5). Seven towers, one per scenario, the closed
# alerts as windows: the windows a scenario would light over the closed book at the threshold, blue for the
# suspicious cases it catches, amber for the benign ones it alerts; the generated set glows as the far city, and
# the wet ground reflects it all. THE DERIVATION, as in the generator: case k of a population is alerted at
# threshold t exactly when the record's count at t exceeds k (counts non-increasing in t, checked here), so each
# threshold shows precisely the record's count; which window is case k is a layout choice.
# ARSLANE'S FIX (25/10, "the words on the buildings collide"): the towers keep the mockup's look, but their overlap
# now shrinks with the window pitch (the mockup's fixed 60 px stacked towers on top of each other below ~1400 px),
# and each tower's sign is measured and lifted until it meets no other label: no two labels intersect, 390 to 1920 px.
# The mockup's top-right concept line (one per concept, beside its tag) is a mockup annotation and stays out.
_HZ_SRC = json.loads((BASE / "instrument-monitoring-donnees.json").read_text())
_HZ_SEUILS = _HZ_SRC["seuils"]
_HZ_SCEN = [{"id": p["id"], "desc": p["description"]} for p in sorted(_HZ_SRC["paliers"], key=lambda p: p["rang"])]
def _hz_grille(pop):
    g, out = _HZ_SRC[pop]["grille"], {}
    for s in _HZ_SCEN:
        c = g[s["id"]]
        r = [c["%.2f" % t]["rappel"]["succes"] for t in _HZ_SEUILS]
        f = [c["%.2f" % t]["fauxPositifs"]["succes"] for t in _HZ_SEUILS]
        if not (all(r[i] >= r[i + 1] for i in range(len(r) - 1)) and all(f[i] >= f[i + 1] for i in range(len(f) - 1))):
            sys.exit(f"instrument-monitoring-donnees.json : the counts of {pop}/{s['id']} grow with the threshold; the windows would lie")
        out[s["id"]] = {"r": r, "f": f}
    return out
_HZ_DATA = {"scen": _HZ_SCEN, "nS": _HZ_SRC["authored"]["nSuspicious"], "nB": _HZ_SRC["authored"]["nBenign"],
            "nSs": _HZ_SRC["synthetic"]["nSuspicious"], "nBs": _HZ_SRC["synthetic"]["nBenign"],
            "A": _hz_grille("authored"), "S": _hz_grille("synthetic")}
if not (len(_HZ_SEUILS) == 51 and _HZ_SEUILS[0] == 0.5 and _HZ_SEUILS[-1] == 1):
    sys.exit("instrument-monitoring-donnees.json : the skyline reads 51 thresholds from 0.50 to 1.00 (idx = round((t-.5)*100))")
_HZ_REC = _HZ_SRC["recommandee"]
_HZ_CAS = _HZ_DATA["nS"] + _HZ_DATA["nB"]
# the counters without script: the still frame's state (t = 6.3 s of the schedule, the tower catching most)
_hz_u = (6.3 - 4) / 10
_HZ_IDX = max(0, min(50, round((.5 + .5 * (.5 - .5 * math.cos(2 * math.pi * _hz_u)) - .5) * 100)))
_hz_best = max(_HZ_SCEN, key=lambda s: (_HZ_DATA["A"][s["id"]]["r"][_HZ_IDX], -_HZ_SCEN.index(s)))["id"]
_HZ_DEPART = (_HZ_SEUILS[_HZ_IDX], _HZ_DATA["A"][_hz_best]["r"][_HZ_IDX], _HZ_DATA["A"][_hz_best]["f"][_HZ_IDX], _hz_best)
CSS_HORIZON = _hv_css(".horizon-hero", "hz", "--hz-sur:#e6ecf7;--hz-pale:#a8b7d4;--hz-bleu:#4f8ae0;--hz-glace:#c3d8ff;--hz-ambre:#e3b062",
                      "radial-gradient(110% 90% at 70% 45%,#16213a,#101a30 55%,#0a111f)", "var(--hz-bleu)", "var(--hz-bleu)", 4) + r"""
  .horizon-hero .hz-vignette{background:radial-gradient(120% 90% at 60% 45%,transparent 50%,rgba(0,0,0,.5) 100%)}
  .horizon-hero h1 em{font-style:normal;color:var(--hz-glace)}
  .horizon-hero .hz-lede b{color:var(--hz-sur);font-weight:500}.horizon-hero .hz-lede .hz-val{color:var(--hz-sur)}.horizon-hero .hz-lede .hz-val b{color:var(--hz-bleu)}
  .horizon-hero .hz-cpt strong.hz-v{color:var(--hz-bleu)}.horizon-hero .hz-cpt strong.hz-a{color:var(--hz-ambre)}.horizon-hero .hz-cpt strong.hz-m{font-size:28px;line-height:38px}
  .horizon-hero .hz-lg{position:absolute;display:flex;flex-direction:column;gap:5px;max-width:250px;transition:opacity .3s ease;transform:translateX(-50%);align-items:center;text-align:center}
  .horizon-hero .hz-lg i{font:500 11px/1 var(--hz-mono);font-style:normal;letter-spacing:.18em;text-transform:uppercase;color:var(--hz-pale);font-variant-numeric:tabular-nums}
  .horizon-hero .hz-lg i b{color:var(--hz-bleu);font-weight:500}.horizon-hero .hz-lg i em{color:var(--hz-ambre);font-style:normal}
  .horizon-hero .hz-lg b.hz-nom{font:600 17px/1.05 var(--hz-texte);letter-spacing:-.01em;color:var(--hz-sur)}
  .horizon-hero .hz-lg span{font:400 12px/1.4 var(--hz-mono);color:var(--hz-pale);max-height:0;overflow:hidden;opacity:0;transition:max-height .35s ease,opacity .3s ease}
  .horizon-hero .hz-lg.hz-on span{max-height:90px;opacity:1}
  .horizon-hero .hz-base{position:absolute;transform:translateX(-50%);font:500 10px/1 var(--hz-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--hz-pale);white-space:nowrap;transition:opacity .2s ease}
  @media (max-width:899px){
    .horizon-hero .hz-bande{height:360px}
    .horizon-hero .hz-cpt strong.hz-m{font-size:20px;line-height:26px;overflow-wrap:anywhere}
    .horizon-hero .hz-base{font-size:9px;letter-spacing:.1em}
    .horizon-hero .hz-lg{max-width:220px}
    .horizon-hero .hz-lg span{font-size:11px}
  }
  @media (prefers-reduced-motion:reduce){.horizon-hero .hz-lg,.horizon-hero .hz-lg span,.horizon-hero .hz-base{transition:none}}
"""
JS_HORIZON = (r"""
(function(){
const D = __DATA__;
const hero = document.querySelector(".horizon-hero"); if (!hero) return;
const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;
const BLUE=[79,138,224], AMBER=[227,176,98], SLATE=[150,170,210];
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
function prng(seed){ let a=seed>>>0; return ()=>{ a=(a+0x6D2B79F5)|0; let t=Math.imul(a^(a>>>15),1|a); t=(t+Math.imul(t^(t>>>7),61|t))^t; return ((t^(t>>>14))>>>0)/4294967296; }; }
function shuffle(arr,rnd){ for (let i=arr.length-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [arr[i],arr[j]]=[arr[j],arr[i]]; } return arr; }
const range=n=>Array.from({length:n},(_,i)=>i);
const idx=thr=>clamp(Math.round((thr-.5)*100),0,50);   // threshold -> index in the 51 thresholds (0.50 .. 1.00 by 0.01)
const alerted=(arr,thr,k)=>arr[idx(thr)]>k;            // THE DERIVATION: case k is alerted at t iff the record's count at t exceeds k
// the schedule: 10 s per scenario, the threshold breathes 0.50 -> 1.00 -> 0.50 and the scenario changes at the peak
const PER=10, T0=-4;
function horaire(t){ const u=(t+T0)/PER; const thr=.5+.5*(.5-.5*Math.cos(2*Math.PI*u)); const sc=((Math.floor(u+.5)%D.scen.length)+D.scen.length)%D.scen.length; return {thr,sc}; }
const fmt=n=>n.toLocaleString("en-US");
const cv=hero.querySelector("canvas"), ctx=cv.getContext("2d"), bande=hero.querySelector(".hz-bande");
const S={cv,ctx,W:0,H:0,R:1,mx:-1e4,my:-1e4,inside:false,seen:false,t:0,thr:horaire(0).thr,sc:0,hover:false,sprites:{},lab:hero.querySelector(".hz-etiquettes"),
  cpt:Object.fromEntries([...hero.querySelectorAll("[data-c]")].map(e=>[e.dataset.c,e]))};
S.sprite=(rgb,r)=>{ r=Math.max(.125,Math.round(r*8)/8);   // rounded to 1/8 px so the cache stays bounded
  const k=rgb.join()+"/"+r; if (S.sprites[k]) return S.sprites[k];
  const c=document.createElement("canvas"), s=Math.ceil(r*6*S.R); c.width=c.height=s; const g=c.getContext("2d");
  const gr=g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  gr.addColorStop(0,`rgba(${rgb},1)`); gr.addColorStop(.16,`rgba(${rgb},.85)`); gr.addColorStop(.42,`rgba(${rgb},.18)`); gr.addColorStop(1,`rgba(${rgb},0)`);
  g.fillStyle=gr; g.fillRect(0,0,s,s); return S.sprites[k]=c; };
S.glow=(rgb,x,y,r,a=1)=>{ const sp=S.sprite(rgb,r), s=r*6; const o=ctx.globalAlpha; ctx.globalAlpha=o*a; ctx.drawImage(sp,x-s/2,y-s/2,s,s); ctx.globalAlpha=o; };
S.mk=(cls,html)=>{ const el=document.createElement("div"); el.className=cls; el.innerHTML=html; S.lab.appendChild(el); return el; };
S.put=(el,x,y)=>{ el.style.left=Math.round(x)+"px"; el.style.top=Math.round(y)+"px"; };
S.fond=()=>{ const {W,H}=S; ctx.globalCompositeOperation="source-over"; ctx.globalAlpha=1;
  const bg=ctx.createRadialGradient(W*.7,H*.45,0,W*.7,H*.45,Math.max(W,H)*.78); bg.addColorStop(0,"#16213a"); bg.addColorStop(.55,"#101a30"); bg.addColorStop(1,"#070c18");
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);
  // the faint ruled grid drifts on its own (and a little with the pointer)
  const px=(S.t*4+(S.inside?(S.mx/W-.5)*14:0))%48, py=(S.t*2.4+(S.inside?(S.my/H-.5)*10:0))%48;
  ctx.strokeStyle="rgba(195,216,255,.035)"; ctx.lineWidth=1; ctx.beginPath();
  for (let x=px-48;x<W;x+=48){ ctx.moveTo(x,0); ctx.lineTo(x,H); } for (let y=py-48;y<H;y+=48){ ctx.moveTo(0,y); ctx.lineTo(W,y); } ctx.stroke(); };
const inter=(a,b,m)=>a.l<b.r+m && b.l<a.r+m && a.t<b.b+m && b.t<a.b+m;
// the skyline (concept 5 of the mockup)
const sky={
  init(S){ const rnd=prng(71), n=D.nS+D.nB;
    // each tower holds the closed cases as windows; its shape is a layout choice (cols x floors = 84)
    const shapes=[[7,12],[6,14],[12,7],[4,21],[7,12],[6,14],[12,7]];
    S.towers=D.scen.map((s,i)=>({s,i,cols:shapes[i][0],floors:shapes[i][1],perm:shuffle(range(n),rnd),back:i%2===1,fl:range(n).map(()=>rnd()*7),
      el:S.mk("hz-lg","<i></i><b class=hz-nom>"+s.id+"</b><span>"+s.desc+"</span>"),sign:S.mk("hz-base",s.id),hi:0}));
    S.far=range(D.nSs+D.nBs).map(k=>({k,sus:k<D.nSs,kk:k<D.nSs?k:k-D.nSs,ux:rnd(),uy:rnd()})); S.off=document.createElement("canvas"); },
  geo(S){ const {W,H}=S, etroit=W<900;
    let x0, x1, yg, haut, bas;
    if (etroit){ const top=bande.offsetTop, h=bande.offsetHeight; x0=16; x1=W-16; yg=top+h*.8; haut=top; bas=top+h; }
    else { x0=W*.475; x1=W*.99; yg=H*.82; haut=yg-H*.62; bas=H; }
    // the window pitch, at most the mockup's 18 px; the towers overlap by 60 px at that pitch and proportionally below it
    // (the mockup kept 60 px at every pitch, which piled the towers on one another below ~1400 px)
    const sc=t=>t.back?.84:1, sCols=S.towers.reduce((a,t)=>a+t.cols*sc(t),0), sSc=S.towers.reduce((a,t)=>a+sc(t),0), nO=S.towers.length-1;
    const pitch=Math.min(18,(x1-x0-16*sSc)/(sCols-nO*60/18)), over=60*pitch/18;
    S.g={x0,x1,yg,pitch,win:[pitch*.6,pitch*.62],ph:pitch*1.12,haut,bas}; let x=x0;
    for (const t of S.towers){ const k=sc(t), w=(t.cols*pitch+16)*k; t.x=x; t.w=w; t.h=(t.floors*S.g.ph+26)*k; t.sc=k; x+=w-over; }
    S.g.xEnd=x+over; S.off.width=Math.ceil(W*S.R); S.off.height=Math.ceil(H*S.R);
    // THE FIX: each sign sits 16 px above its roof, then rises by its own height plus a gap until it meets no sign
    // already placed (front towers first, then the ones behind); measured boxes, not guesses
    const placed=[];
    for (const t of [...S.towers.filter(t=>!t.back), ...S.towers.filter(t=>t.back)]){
      const w=t.sign.offsetWidth, h=t.sign.offsetHeight, cx=t.x+t.w/2; let y=yg-t.h-16-(etroit?4:0);
      const box=()=>({l:cx-w/2,r:cx+w/2,t:y,b:y+h});
      while (placed.some(b=>inter(b,box(),8))) y-=h+5;   // at least 8 px between any two signs
      t.sy=y; placed.push(box()); S.put(t.sign,cx,y); }
  },
  zone(S){ const {x0,xEnd,yg,haut}=S.g; return [x0,xEnd,haut,yg+40]; },
  draw(S){ const {ctx,W,H,thr}=S; S.fond(); const {yg,pitch,win,ph,x0,x1,bas}=S.g;
    // sky glow over the horizon and the far lights (the generated set, lit by the same record)
    ctx.globalCompositeOperation="lighter"; const sky=ctx.createLinearGradient(0,yg-220,0,yg); sky.addColorStop(0,"rgba(79,138,224,0)"); sky.addColorStop(1,"rgba(79,138,224,.14)"); ctx.fillStyle=sky; ctx.fillRect(x0-80,yg-220,x1-x0+160,220);
    const best=S.towers.reduce((b,t)=>{ const n=D.A[t.s.id].r[idx(thr)]; return n>b.n?{n,t}:b; },{n:-1,t:null}).t;
    const far=D.S[best.s.id]; for (const p of S.far){ const lit=alerted(p.sus?far.r:far.f,thr,p.kk); const x=x0-40+p.ux*(x1-x0+80), y=yg-6-p.uy*34; if (lit) S.glow(p.sus?BLUE:AMBER,x,y,1.6,.55); else { ctx.globalAlpha=.25; ctx.fillStyle=`rgba(${SLATE})`; ctx.fillRect(x,y,1.2,1.2); ctx.globalAlpha=1; } }
    // towers to an offscreen layer (so the water can reflect them)
    const o=S.off.getContext("2d"); o.setTransform(S.R,0,0,S.R,0,0); o.clearRect(0,0,W,H);
    let hov=-1; if (S.inside) S.towers.forEach(t=>{ if (S.mx>=t.x&&S.mx<=t.x+t.w&&S.my>=yg-t.h&&S.my<=yg) hov=t.i; });
    const draw=(t)=>{ const r=D.A[t.s.id].r, f=D.A[t.s.id].f; let nC=0,nF=0; const top=yg-t.h, dim=t.back?.72:1, hdim=hov>=0?(hov===t.i?1:.5):1;
      o.globalCompositeOperation="source-over"; o.globalAlpha=1; o.shadowColor="rgba(0,0,0,.6)"; o.shadowBlur=24; o.shadowOffsetX=t.back?-6:6;
      const wall=o.createLinearGradient(t.x,0,t.x+t.w,0); wall.addColorStop(0,t.back?"#0c1526":"#101c34"); wall.addColorStop(.5,t.back?"#111d35":"#182a4c"); wall.addColorStop(1,t.back?"#0a1222":"#0e192e");
      o.fillStyle=wall; o.beginPath(); o.roundRect(t.x,top,t.w,t.h+20,3); o.fill(); o.shadowColor="transparent";
      o.fillStyle="rgba(195,216,255,.25)"; o.fillRect(t.x+6*t.sc,top,t.w-12*t.sc,1.5);
      for (let j=0;j<t.perm.length;j++){ const c=t.perm[j], sus=c<D.nS, k=sus?c:c-D.nS, lit=alerted(sus?r:f,thr,k); if (lit){ if (sus) nC++; else nF++; }
        const col=j%t.cols, row=Math.floor(j/t.cols); const x=t.x+8*t.sc+col*pitch*t.sc+(pitch*t.sc-win[0]*t.sc)/2, y=top+14*t.sc+row*ph*t.sc, w=win[0]*t.sc, h=win[1]*t.sc;
        o.globalCompositeOperation="source-over"; o.globalAlpha=dim*hdim;
        o.fillStyle= lit ? (sus?"rgba(205,224,255,.98)":"rgba(255,222,165,.98)") : "rgba(195,216,255,.07)"; o.fillRect(x,y,w,h);
        if (lit){ o.globalCompositeOperation="lighter"; const fl=.75+.25*Math.sin(S.t*3+t.fl[j]); const sp=S.sprite(sus?BLUE:AMBER,w*1.1), sz=w*1.1*6; o.globalAlpha=dim*hdim*fl*.9; o.drawImage(sp,x+w/2-sz/2,y+h/2-sz/2,sz,sz); } }
      o.globalAlpha=1; t.n=[nC,nF]; t.el.firstChild.innerHTML=`<b>${nC}</b> caught · <em>${nF}</em> false`; };
    S.towers.filter(t=>t.back).forEach(draw); S.towers.filter(t=>!t.back).forEach(draw);
    // the pointed tower's card: over its roof, kept inside the frame; the signs it would cover step aside while it shows
    if (hov!==S.hovPrec){ S.hovPrec=hov; S.towers.forEach(t=>{ t.el.classList.toggle("hz-on",hov===t.i); t.el.style.opacity=hov===t.i?1:0; });
      if (hov>=0){ const t=S.towers[hov], w=t.el.offsetWidth; S.put(t.el,clamp(t.x+t.w/2,w/2+8,W-w/2-8),Math.max(S.g.haut+4,yg-t.h-96)); }
      S.cache=hov>=0; }
    if (hov>=0){ const c=S.towers[hov].el.getBoundingClientRect(), b0=hero.getBoundingClientRect(), card={l:c.left-b0.left,r:c.right-b0.left,t:c.top-b0.top,b:c.bottom-b0.top};
      S.towers.forEach(t=>{ const s=t.sign; t.sign.style.opacity=(t.i===hov||inter(card,{l:s.offsetLeft-s.offsetWidth/2,r:s.offsetLeft+s.offsetWidth/2,t:s.offsetTop,b:s.offsetTop+s.offsetHeight},3))?0:1; }); }
    else if (S.cache){ S.cache=false; S.towers.forEach(t=>{ t.sign.style.opacity=1; }); }
    ctx.globalCompositeOperation="source-over"; ctx.drawImage(S.off,0,0,W,H);
    // the wet ground: the layer flipped, in slices that ripple (down to the bottom of its band on narrow screens)
    ctx.save(); ctx.beginPath(); ctx.rect(0,yg,W,bas-yg); ctx.clip(); ctx.globalAlpha=.42;
    for (let y=0;y<bas-yg;y+=3){ const src=yg-y*1.5, sh=Math.sin(y*.11+S.t*1.6)*(1.5+y*.05); if (src<0) break; ctx.drawImage(S.off,0,src*S.R,W*S.R,3*S.R,sh,yg+y,W,3); }
    ctx.globalAlpha=1; const fade=ctx.createLinearGradient(0,yg,0,bas); fade.addColorStop(0,"rgba(10,17,31,.15)"); fade.addColorStop(1,"rgba(10,17,31,1)"); ctx.fillStyle=fade; ctx.fillRect(0,yg,W,bas-yg); ctx.restore();
    ctx.fillStyle="rgba(195,216,255,.18)"; ctx.fillRect(x0-60,yg,x1-x0+120,1);
    const b=hov>=0?S.towers[hov]:best; S.cpt.caught.textContent=fmt(b.n[0]); S.cpt.false.textContent=fmt(b.n[1]); S.cpt.scen.textContent=b.s.id;
    S.cpt.scenL.textContent=hov>=0?"tower pointed":"tower catching most"; }
};
let frozen=null;
function avancer(dt){ const h=horaire(S.t); let target=h.thr; S.hover=false; const z=sky.zone(S);
  if (S.inside && S.mx>=z[0]&&S.mx<=z[1]&&S.my>=z[2]&&S.my<=z[3]){ target=.5+.5*clamp((S.mx-z[0])/(z[1]-z[0]),0,1); if (frozen==null) frozen=h.sc; S.hover=true; } else frozen=null;
  S.sc=frozen??h.sc; S.thr+=(target-S.thr)*Math.min(1,dt*(S.hover?9:6)); }
function dessiner(){ sky.draw(S); S.cpt.thr.textContent=S.thr.toFixed(2); }
function fit(){ S.R=Math.min(1.5,devicePixelRatio||1); S.W=cv.clientWidth; S.H=cv.clientHeight; cv.width=S.W*S.R; cv.height=S.H*S.R; ctx.setTransform(S.R,0,0,S.R,0,0); S.sprites={}; S.hovPrec=undefined; sky.geo(S); if (calme) dessiner(); }
hero.addEventListener("pointermove", e=>{ const b=cv.getBoundingClientRect(); S.mx=e.clientX-b.left; S.my=e.clientY-b.top; S.inside=true; }, {passive:true});
hero.addEventListener("pointerleave", ()=>{ S.inside=false; });
sky.init(S);
const pas = dt=>{ if (!S.seen){ S.seen=true; S.t=0; } S.t+=dt; avancer(dt); dessiner(); };
""" + _hv_boucle("hz") + r"""
(document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{
  if (calme){ S.t=6.3; S.thr=horaire(S.t).thr; S.sc=horaire(S.t).sc; }   // reduced motion: the frame at 6.3 s of the schedule stays
  fit(); new ResizeObserver(fit).observe(cv); hz_pret=true; hz_lancer(); });
})();
""").replace("__DATA__", json.dumps(_HZ_DATA, separators=(",", ":")))
_HERO_HORIZON = f'''<section class="horizon-hero" aria-label="Monitoring, live">
  <canvas aria-hidden="true"></canvas>
  <div class="hz-grain"></div><div class="hz-vignette"></div><div class="hz-etiquettes" aria-hidden="true"></div>
  <div class="hz-texte">
    <div class="hz-kicker"><i></i>Monitoring &#183; measured live</div>
    <h1>See what your scenarios catch, and what they <em>flag incorrectly.</em></h1>
    <p class="hz-lede">A scenario's threshold is the score above which it raises an alert.<span>Crusetra Monitoring runs <b>{len(_HZ_SCEN)} scenarios</b> at <b>{len(_HZ_SEUILS)} thresholds</b> over the <b>{_HZ_CAS} alerts</b> your analysts already closed.</span><span class="hz-val"><b>{_HZ_REC["plusForteBorne"] * 100:.1f}%</b> is the strongest lower bound any scenario reaches: none is sure of the {round(_HZ_REC["plancher"] * 100)}% floor.</span></p>
  </div>
  <div class="hz-bande" aria-hidden="true"></div>
  <div class="hz-cpt" aria-live="off">
    <div><strong data-c="thr">{_HZ_DEPART[0]:.2f}</strong><span>threshold</span></div>
    <div><strong class="hz-v" data-c="caught">{_HZ_DEPART[1]}</strong><span data-c="caughtL">suspicious caught</span></div>
    <div><strong class="hz-a" data-c="false">{_HZ_DEPART[2]}</strong><span data-c="falseL">benign alerted</span></div>
    <div><strong class="hz-m" data-c="scen">{_HZ_DEPART[3]}</strong><span data-c="scenL">tower catching most</span></div>
  </div>
</section>
<script>{JS_HORIZON}</script>'''

# the hero of each catalogue page, with its CSS: a page whose id is missing here keeps the plain hero
HEROS_VIVANTS = {"screening": (CSS_SPHERE, _HERO_SPHERE), "scoring": (CSS_LAMPES, _HERO_LAMPES),
                 "dossier": (CSS_TABLEAU, _HERO_TABLEAU), "monitoring": (CSS_HORIZON, _HERO_HORIZON)}
for _id, (_css, _html) in HEROS_VIVANTS.items():
    if "\u2014" in _css + _html or "\u2026" in _html:
        sys.exit(f"the {_id} hero carries an em dash or an ellipsis")

# \u2500\u2500 ONE ACTION BUTTON PER HERO (Arslane, 25/10, "Un bouton par page"). Under the hero text of each of the five
# tool pages, one button, the same component everywhere: the markup of the pricing page's .cta / .b / .fl
# (batir-offre.py), drawn since 25/10 evening as design 3 "Readout" of maquettes-bouton.py (Arslane's pick): a lit point
# and brackets in the hero's mono small caps, no fill. Its label and target are READ from a call to action the page already carries further
# down, never typed here: Routing, the "Try it free" link of its #report section; Screening, the link to its #report
# that the plain hero carried (commit d6aa49d), whose delay is the offer's, stated again in that section's title;
# Monitoring, Scoring and Dossier, their "See pricing" link. The label is the hero's text colour on its ground and the
# focus ring the same colour (14.6:1 or more, computed 25/10); the point, brackets and arrow use the hero's accent,
# 4.5:1 or more on the lightest point of each ground (asserted by maquettes-bouton.py).
_m_essai = re.search(r'<a class="ouvrir" href="([^"]+)"><span><span class="ouvrir-t">([^<]+)</span>', _SECTION_RAPPORT_ROUTING)
if not _m_essai:
    sys.exit("the Routing #report section no longer carries its 'Try it' link: the hero button has no source")
_ACTIONS = {
    "routing": (_m_essai.group(1), _m_essai.group(2), "&#8594;"),
    "screening": ("#report", "Send us your list for a sealed report within "
                  f'{json.loads((BASE / "offre-screening.json").read_text())["delai_heures"]} hours', "&#8595;"),
    "monitoring": (lien(OUTILS["monitoring"], "ENGAGEMENT.html"), "See pricing", "&#8594;"),
    "scoring": (lien(OUTILS["scoring"], "ENGAGEMENT.html"), "See pricing", "&#8594;"),
    "dossier": (lien(OUTILS["dossier"], "ENGAGEMENT.html"), "See pricing", "&#8594;"),
}
_ACTION_PALETTE = {   # (section class, text-block prefix, accent of the point and brackets, its glow, the label's colour)
    # design 3 "Readout" (Arslane, 25/10, maquettes-bouton.py n=3): the accent and glow are the variables the mockup read
    # from each hero (FILL and GLOW there); the label is the hero's text colour. Accent on the lightest point of each
    # ground was asserted 4.5:1 or more by the mockup; the brackets and the arrow are decorative (aria-hidden or silent).
    "routing": (".flux-hero", "fx", "var(--fx-vert)", "var(--fx-vert)", "var(--fx-sur)"),
    "screening": (".sphere-hero", "sp", "var(--sp-rose)", "var(--sp-rubis)", "var(--sp-sur)"),
    "monitoring": (".horizon-hero", "hz", "var(--hz-glace)", "var(--hz-bleu)", "var(--hz-sur)"),
    "scoring": (".lampes-hero", "lp", "var(--lp-clair)", "var(--lp-vif)", "var(--lp-sur)"),
    "dossier": (".tableau-hero", "tb", "var(--tb-arg)", "var(--tb-vert)", "var(--tb-sur)"),
}

def _action_css(c, acc, glow, sur):
    """Design 3, "Readout", ported from maquettes-bouton.py (.act.a3) onto the button's existing markup (.cta > .b > .fl,
    which _garde_action and the mockup generator both read): the lit point is .cta::before, the opening bracket
    .b::before, the closing bracket .fl::before (it travels with the arrow, as in the mockup where both move 5px).
    The brackets' text is silent to assistive tech (content alt text "")."""
    mono = '"Roboto Mono",ui-monospace,Menlo,monospace'
    return (f"""
  {c} .cta{{display:inline-flex;align-items:center;max-width:100%;margin-top:30px;padding:6px 0;text-decoration:none;
    pointer-events:auto;color:{sur};font:500 11.5px/1.9 {mono};letter-spacing:.12em;text-transform:uppercase;
    cursor:pointer;-webkit-tap-highlight-color:transparent}}
  {c} .cta::before{{content:"";flex:none;width:7px;height:7px;border-radius:50%;background:{acc};box-shadow:0 0 10px {glow};
    margin-right:14px;transition:transform .25s,box-shadow .25s}}
  {c} .cta .b{{flex:1 1 auto;min-width:0;text-wrap:pretty}}
  {c} .cta .b::before,{c} .cta .fl::before{{display:inline-block;font:400 11.5px/1 {mono};letter-spacing:.12em;color:{acc};
    transition:transform .22s cubic-bezier(.2,.7,.2,1)}}
  {c} .cta .b::before{{content:"[";content:"[" / "";margin-right:.6em}}
  {c} .cta .fl{{display:inline-block;margin-left:-1.4px;color:{acc};font-family:"Literata",Georgia,serif;font-size:15px;
    line-height:1;letter-spacing:0;transition:transform .22s cubic-bezier(.2,.7,.2,1)}}
  {c} .cta .fl::before{{content:"]";content:"]" / "";margin-right:14.3px}}
  {c} .cta:hover .b::before{{transform:translateX(-5px)}}
  {c} .cta:hover .fl{{transform:translateX(5px)}}
  {c} .cta[href^="#"]:hover .fl{{transform:translateY(3px)}}
  {c} .cta[href^="#"]:hover .fl::before{{transform:translate(5px,-3px)}}
  {c} .cta:hover::before{{transform:scale(1.4);box-shadow:0 0 18px {glow},0 0 4px {sur}}}
  {c} .cta:active .b::before{{transform:translateX(0)}}
  {c} .cta:active .fl{{transform:none}}{c} .cta:active .fl::before{{transform:none}}
  {c} .cta:focus{{outline:none}}
  {c} .cta:focus-visible{{outline:2px solid {sur};outline-offset:5px}}
  @media (max-width:599px){{{c} .cta{{margin-top:22px;font-size:11px;letter-spacing:.1em;align-items:flex-start}}
    {c} .cta::before{{margin-top:7px}}{c} .cta .b::before,{c} .cta .fl::before{{font-size:11px;letter-spacing:.1em}}}}
  @media (prefers-reduced-motion:reduce){{{c} .cta::before,{c} .cta .b::before,{c} .cta .fl,{c} .cta .fl::before{{transition:none!important}}
    {c} .cta:hover::before{{transform:none}}}}
""")

def _avec_action(oid, css, html):
    """Puts the action button under the hero text: exactly once, after the lede, or the build stops."""
    href, label, fleche = _ACTIONS[oid]
    c, p, acc, glow, sur = _ACTION_PALETTE[oid]
    ancre = f'</p>\n  </div>\n  <div class="{p}-bande"'
    if html.count(ancre) != 1:
        sys.exit(f"the {oid} hero no longer ends its text block where the action button goes ({html.count(ancre)} places)")
    bouton = f'</p>\n    <a class="cta" href="{href}"><span class="b">{label} <span class="fl" aria-hidden="true">{fleche}</span></span></a>'
    return css + _action_css(c, acc, glow, sur), html.replace(ancre, bouton + ancre[4:])

CSS_FLUX, _HERO_FLUX = _avec_action("routing", CSS_FLUX, _HERO_FLUX)
HEROS_VIVANTS = {k: _avec_action(k, *v) for k, v in HEROS_VIVANTS.items()}

def _garde_action(page, nom):
    """The hero button promises nothing the page does not already state: one button in the hero, its target is a
    target the page carries elsewhere (an id, or the same link further down), every figure of its label is said
    again on the page outside the hero. Refuses otherwise."""
    m_h = re.search(r'<section class="[a-z]+-hero".*?</section>', page, re.S)
    if not m_h:
        sys.exit(f"{nom}: no living hero found for the action-button guard")
    hero, reste = m_h.group(0), page[:m_h.start()] + page[m_h.end():]
    boutons = re.findall(r'<a class="cta" href="([^"]+)"><span class="b">([^<]+?) <span class="fl"', hero)
    if len(boutons) != 1:
        sys.exit(f"{nom}: the hero carries {len(boutons)} action buttons, one expected")
    href, label = boutons[0]
    if href.startswith("#"):
        if f'id="{href[1:]}"' not in reste:
            sys.exit(f"{nom}: the hero button points to {href}, which the page does not carry")
    elif f'href="{href}"' not in reste:
        sys.exit(f"{nom}: the hero button points to {href}, a target no other call to action of the page uses")
    texte = re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(style|script)\b.*?</\1>", " ", reste, flags=re.S))))
    # a figure is checked with the word it counts ("48 hours", "100 of"): a bare 24 is somewhere on any page
    if re.search(r"\d(?![\d,.]*\s+\w)", label):
        sys.exit(f"{nom}: a figure of the hero button carries no word after it, so it cannot be checked")
    for n, mot in re.findall(r"(\d[\d,.]*)\s+(\w+)", label):
        if not re.search(rf"(?<![\d.,]){re.escape(n)}\s+{re.escape(mot)}\b", texte):
            sys.exit(f"{nom}: the hero button says {n} {mot}, which the page does not state elsewhere")
    return href, label

CSS_CHAMPS = """
  .champs{list-style:none;margin:44px auto 0;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));
    gap:14px;max-width:1040px;perspective:900px}
  .champ{display:flex;flex-direction:column;gap:10px;text-align:left;padding:18px 18px 16px;border-radius:14px;
    border:1px solid color-mix(in srgb,var(--sur-vert) 16%,transparent);
    background:color-mix(in srgb,var(--sur-vert) 4%,transparent);outline:none;
    transform:translate3d(var(--dx,0px),var(--dy,0px),0) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
    transition:transform .45s cubic-bezier(.2,.7,.2,1),border-color .2s,background .2s,box-shadow .2s}
  .champ:hover,.champ:focus-visible{border-color:var(--vert-vif);background:color-mix(in srgb,var(--vert-vif) 12%,transparent);
    box-shadow:0 18px 40px -18px color-mix(in srgb,var(--vert-vif) 60%,transparent)}
  .c-nom{font-size:15px;color:var(--sur-vert)}
  .c-moteur{font:400 11px/1 var(--mono,ui-monospace,monospace);letter-spacing:.12em;text-transform:uppercase;
    color:var(--sur-vert-pale)}
  .champ.gratuit .c-moteur{color:var(--vert-vif)}
  .c-acc{font-size:34px;line-height:1;font-weight:600;color:var(--sur-vert);margin-top:6px}
  .c-acc small{font-size:16px;margin-left:2px;color:var(--sur-vert-pale)}
  .c-cout{font:400 12px/1.3 var(--mono,ui-monospace,monospace);color:var(--sur-vert-pale)}
  .champ.gratuit .c-cout{color:var(--vert-vif)}
  .champs-note{margin:14px auto 0;max-width:72ch;font-size:13px;color:var(--sur-vert-pale)}
  @media (max-width:900px){.champs{grid-template-columns:repeat(2,minmax(0,1fr))}.champ:last-child{grid-column:1/-1}}
  @media (prefers-reduced-motion:reduce){.champ{transform:none!important;transition:border-color .2s,background .2s}}
"""
JS_CHAMPS = """
(function(){var ul=document.querySelector('.champs');if(!ul||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var cs=[].slice.call(ul.children);
addEventListener('pointermove',function(e){cs.forEach(function(c){var r=c.getBoundingClientRect(),
x=(e.clientX-(r.left+r.width/2))/innerWidth,y=(e.clientY-(r.top+r.height/2))/innerHeight;
c.style.setProperty('--dx',(-x*10).toFixed(1)+'px');c.style.setProperty('--dy',(-y*8).toFixed(1)+'px');
c.style.setProperty('--ry',(x*10).toFixed(2)+'deg');c.style.setProperty('--rx',(-y*8).toFixed(2)+'deg');});},{passive:true});
})();
"""


_SECTION_FILM_ROUTING = f'''<section class="film"><div class="colonne">
  <h2 class="h2">Crusetra, proven in 90 seconds.</h2>
  <p class="film-duree">{"The film, and the demo" if "routing" in DEMOS else "The five Routing findings"}</p>
  {lecteur_html("routing", "Routing", "", "affiche-film.jpg")}{liste_films("routing", "", "affiche-film.jpg")}
</div></section>
''' if "routing" in FILMS_VISIBLES else ""

# 25/10 (Arslane, look C kept in the retouch session): the measurement note under the Routing card as four labelled
# footnotes; each figure is the variable the paragraph used (N_SOCLE, N_GEN, LONGUEUR_DOSSIER, HUMAIN).
_NOTES_ROUTING = [
    ("Measured on", f"{N_SOCLE:,} held-out records for the rules, small and large tiers; {N_GEN} for the generative tiers. "
                    "A ring marks the published routing of each field."),
    ("Corpus", f"Records we wrote, about {LONGUEUR_DOSSIER} characters each."),
    ("Caveat", "The generative tiers' prompt was tuned on the held-out half: their figures are optimistic, by an amount not yet measured."),
    ("Human", f"Accuracy assumed at {qte(HUMAIN)} % until you measure your own reviewers."),
]

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
<style>{CSS}{_CSS_SCRUB_V}{CSS_BARRE_SITE}{CSS_CHAMPS}{CSS_FLUX}</style>
{barre_site(courant="HERO.html")}

<main>
{_HERO_FLUX}

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
  {_tarif_et_notes(affiche_html("paliers", LANDING, [], "INSTRUMENT.html", "Crusetra &#183; Routing",
                "See every field, tier, accuracy and cost, live from our public test set. Set the budget and watch the tool choose.",
                "rendus/robot-vert-regarde.webp"), "ENGAGEMENT.html", _NOTES_ROUTING)}
</div></section>

{couture_defile("measured, then frozen", SCEAU)}

{_SECTION_FILM_ROUTING}
{menus_html()}
</main>

{pied_html(outil=OUTILS["routing"], sceau=SCEAU, tests=N_TESTS)}

<script>{JS}</script><script>{JS_CHAMPS}</script>{_SCRUB_V}
'''

# Routing vit sous routing/ (décision A du 6/09) : chaque lien relatif de la page
# sort du sous-dossier par ../ ; ceux qui le portent déjà (le rideau, via la table)
# ne le reçoivent pas deux fois ; les absolus, les ancres et les data: sont laissés
PAGE = re.sub(r'(href|src|poster)="(?!(?:https?:|#|data:|mailto:|\.\./))([^"]+)"', r'\1="../\2"', PAGE)   # poster : l'affiche du lecteur (27/09)
assert "—" not in PAGE, "un cadratin s'est glissé dans la page"
print("HERO.html · hero button held:", " → ".join(_garde_action(PAGE, "HERO.html")[::-1]))
(BASE / "HERO.html").write_text(PAGE, encoding="utf-8")
print("HERO.html", f"{len(PAGE) / 1e3:.0f} ko")


# the home's wordmark in the sky: the same drawn mark the assembler puts in the bar (marque/logo.svg)
_LOGO_CIEL = (BASE / "marque" / "logo.svg").read_text().strip()

def _rideau_paresseux(html):
    """On the home the strip of tools sits under the sky and the hero, well below the first viewport: its robots wait
    to be near (the assembler keeps the strip eager on the tool pages, where it is the second screen)."""
    n = html.count('<img src="')
    if n < 2:
        sys.exit(f"the home strip carries {n} robots: the lazy rewrite has nothing to do")
    return html.replace('<img src="', '<img loading="lazy" src="')

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
<script>{JS_TETE}</script>
<style>{CSS}{CSS_ACCUEIL}{CSS_PIED_SITE}.methode{{{tokens_papier}}}{CSS_CIEL}</style>
<header class="barre sur-nuit">
  <a class="marque" href="ACCUEIL.html">CRUSETRA</a>
  <nav aria-label="Site">
    {chr(10).join(f'    <a href="{o["page_hero"]}">{o["nom"]}</a>' for o in vivants).lstrip()}
    <a href="ENGAGEMENT.html">Pricing</a>
    <a href="CONTACT.html">Contact</a>
  </nav>
</header>

{ciel_html(_LOGO_CIEL)}


<main>
<section class="hero">
  <div class="hero-grille">
    <div class="hero-texte">
      <h1 class="h1 entree">Don’t trust compliance tools.<br><em>Test them.</em></h1>
      <p class="lede entree">Compliance decisions you can <b>test</b>, <b>reproduce</b> and <b>inspect</b>.</p>
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

{_rideau_paresseux(choix_outils(None))}

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
<script>{JS_CIEL}</script>
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


def _notes_outil(spec, releve, findings):
    """The note of _note_outil as labelled footnotes (25/10, the Routing look carried to Screening): the same counts
    from the record, the same cell from the third finding, the same closing fact; nothing added, nothing typed."""
    src = findings[2].get("source", {}).get("a") or {} if len(findings) > 2 else {}
    palier_f, seuil_f = src.get("palier"), src.get("seuil")
    auth = releve["authored"]
    unites = spec["table_note_unites"].format(
        nMatch=auth.get("nMatch", auth.get("nSuspicious", auth.get("nEscalated"))),
        nDifferent=auth.get("nDifferent", auth.get("nBenign", auth.get("nMaintained"))))
    if not unites.startswith("Measured on "):
        sys.exit("table_note_unites ne commence plus par « Measured on » : la première note ne sait plus se poser")
    champ_cite = src.get("champ", "taux")
    if palier_f and champ_cite == "taux":
        choix = ("Default cell", f"A ring marks the cell the tool picks by default, {palier_f} at {seuil_f}.")
    elif palier_f:
        choix = ("Marked cell", f"The marked cell, {palier_f} at {seuil_f}, comes closest to the 90% floor we set, which none reaches.")
    else:
        choix = ("Floor", "No setting reaches the 90% floor we set.")
    jeu = _NOM_JEU[spec["table_ligne"]]
    return [("Measured on", " ".join(unites[len("Measured on "):].split()) + ", at every threshold."), choix,
            (f"Generated {jeu}", "Counted on their own, and the live instrument shows them.")]


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
        return '<div class="ca-g grille" aria-hidden="true">' + "".join(f'<i class="{classe(k)}"></i>' for k in range(n)) + "</div>"
    # 25/10 (Arslane, look kept in the retouch session): look A, three panels side by side. Each key is (swatch, text);
    # a bracketed interval is kept on one line, the text itself unchanged.
    pops = [
        (f["populations"][0].format(sur=sur_v), f"{pct(vf, sur_v)}<small>%</small>",
         grille(sur_v, lambda k: "f" if k < vf else ("p" if k < vp else "")),
         [("f", f"{vf} found at the strong level, {pct(vf, sur_v)} % [{iv_f[0]}-{iv_f[1]}]"),
          ("v", f"{vp - vf} more at the possible level, {vp} in all, {pct(vp, sur_v)} % [{iv_p[0]}-{iv_p[1]}]"),
          ("", f"{sur_v - vp} missed at both levels")]),
        (f["populations"][1].format(sur=f"{sur_f:,}"), f"{ff}",
         grille(sur_f, lambda k: "f" if k < ff else ("p" if k < fp else "")),
         [("f", f"{ff} of {sur_f:,} raised a strong alert [{if_f[0]}-{if_f[1]} %]"),
          ("v", f"{fp} raised a possible alert [{if_p[0]}-{if_p[1]} %]")]),
        (f["populations"][2].format(lignes=f"{lignes:,}", listes=listes_livre, jour=jour_livre), f"{forts + possibles}<small>/{lignes}</small>",
         grille(lignes, lambda k: "f" if k < forts else ("p" if k < forts + possibles else "")),
         [("f", f"{forts} strong"), ("v", f"{possibles} possible"), ("", f"{sans} with no candidate")]),
    ]
    nw = lambda t: re.sub(r"(\[[^\]]+\])", r'<b class="nw">\1</b>', t)
    blocs = "".join(f'''<div class="ca-p pop"><div class="ca-h"><span class="ca-n">{chiffre}</span><p class="ca-d">{texte}</p></div>{gr}<p class="ca-c">'''
                    + "".join(f'<span><i class="{c}"></i><span>{nw(t)}</span></span>' if c else f'<span><i></i><span>{nw(t)}</span></span>' for c, t in cle)
                    + '<span class="compteur" aria-live="polite"></span></p></div>'
                    for texte, chiffre, gr, cle in pops)
    titre = [x.strip() for x in f["titre"].split("<br>")]
    if len(titre) != 2 or not all(titre):
        sys.exit("findings-entites.json : le titre devait porter deux phrases séparées par <br>, le panneau A pose une ligne chacune : refusé")
    # 25/10 (Arslane, look kept in the retouch session): the note as look B, a band of large figures. Every figure and date
    # comes from the same variables the paragraph used; the easier set's date and the two closing sentences are read from
    # the note of findings-entites.json, so the band and the note cannot drift apart.
    note = f["note"].format(date_gleif=g["date"], manques=sur_v - vp, sur=sur_v, tiers=pct(sur_v - vp, sur_v),
                            ia_trouves=ia["trouves"]["n"], ia_sur=ia["trouves"]["sur"], ia_fausses=ia["fausses"]["n"], ia_sur_f=ia["fausses"]["sur"])
    m_ia = re.search(r"\((\d{1,2} [A-Z][a-z]+ \d{4}), before the tool was recalibrated on real names\)", note)
    if not m_ia:
        sys.exit("findings-entites.json : la note ne date plus le jeu plus facile « (<date>, before the tool was recalibrated on real names) » : la bande ne se pose pas")
    date_ia = m_ia.group(1)
    phrases_note = [x.strip() for x in re.split(r"(?<=[.)])\s+(?=[A-Z0-9])", note) if x.strip()]
    fin_note = [next((x for x in phrases_note if x.startswith(debut)), None) for debut in ("A candidate is", "The counterparty book")]
    if None in fin_note:
        sys.exit("findings-entites.json : la note n'a plus sa phrase « A candidate is » ou « The counterparty book » : la bande ne se pose pas")
    bande = [(f"Measured once, {g['date']}, on names the tool had never seen",
              [(f"{sur_v - vp}<i> of {sur_v}</i>", "spelling variants missed even at the possible level"),
               (f"{pct(sur_v - vp, sur_v)} %", "about a third: a name written very differently can get through")]),
             (f"Easier set, {date_ia}, written by a separate AI agent that never saw the matcher, before the tool was recalibrated on real names",
              [(f"{ia['trouves']['n']}<i> of {ia['trouves']['sur']}</i>", "true pairs came back strong"),
               (f"{ia['fausses']['n']}<i> of {ia['fausses']['sur']}</i>", "neighbors came back strong")])]
    note_b = (f"<style>{_ENTITES_NOTE_CSS}</style>" + '<span class="nc2"><span class="band">'
              + "".join("<span class='g'><span class='h'>" + tete + "</span><span class='fs'>"
                        + "".join(f"<span class='f'><span class='n'>{n}</span><span class='m'>{m}</span></span>" for n, m in chiffres)
                        + "</span></span>" for tete, chiffres in bande)
              + f"</span><span class='c'>{fin_note[0]} {fin_note[1]}</span></span>")
    depot = o["depot"].rstrip("/")
    html = f'''<section class="entites" id="companies"><div class="colonne">
  <style>{_ENTITES_PANNEAUX_CSS}</style>
  <div class="ca-top"><p class="ca-k">Company and vessel names</p><h2 class="ca-t"><span>{titre[0]}</span> <span>{titre[1]}</span></h2></div>
  <div class="ca-row">{blocs}</div>
  <p class="note">{note_b}</p>
  {liens_tuiles([(f"{depot}/blob/main/verification/GLEIF.md", "Read", "The four verdicts on real names", ""),
                 (f"{depot}/blob/main/releve-entites.json", "Open", "The sealed record", "")])}
  <style>{_SCEAUL_CSS}</style>
  <span class="sceau-l sl3"><i></i><span><b></b>measured {R["date"]} at commit {R["commit"]} &#183; sealed and signed &#183; content hash {R["empreinte"]}</span><i></i></span>
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
{couture_defile("company and vessel names &#183; measured, then frozen", R["empreinte"])}'''
    assert "\u2014" not in html, "un cadratin s'est glissé dans la section des entités"
    for attendu in (f"{pct(vf, sur_v)}<small>%</small>", f">{ff}<", f"{forts + possibles}<small>/{lignes}</small>", f"{vf} found at the strong level",
                    f"{vp} in all", f"{sur_v - vp} missed at both levels", f"{fp} raised a possible alert", f"{sans} with no candidate",
                    # the note's sentence « {ia} of {sur} true pairs » is now split in the band: each piece is checked
                    f"<span class='n'>{ia['trouves']['n']}<i> of {ia['trouves']['sur']}</i></span><span class='m'>true pairs came back strong</span>",
                    f"<span class='n'>{ia['fausses']['n']}<i> of {ia['fausses']['sur']}</i></span><span class='m'>neighbors came back strong</span>",
                    f"<span class='n'>{sur_v - vp}<i> of {sur_v}</i></span>", f"<span class='n'>{pct(sur_v - vp, sur_v)} %</span>",
                    f"Measured once, {g['date']},", f"Easier set, {date_ia},", fin_note[0], fin_note[1],
                    f"<span>{titre[0]}</span> <span>{titre[1]}</span>", g["date"]):
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
    # 25/10 (Arslane, the Routing looks carried to Screening): five rows of the committed sample list, one per kind of
    # verdict the record gives (an entity with no candidate, a possible one, a strong one; a strong vessel, a clear one),
    # in the record's own order; names, refs and verdicts read from rec, the count of names from ex.
    _rangs = []
    for statut, genre in (("no-match", "entity"), ("possible", "entity"), ("strong", "entity"), ("strong", "vessel"), ("no-match", "vessel")):
        x = next((r for r in rec["resultats"] if r["statut"] == statut and r["type"] == genre), None)
        if x is None:
            sys.exit(f"le relevé exemple n'a plus de ligne {genre} « {statut} » : la page vivante du rapport perd une rangée")
        _rangs.append(x)
    _rangs.sort(key=lambda r: r["ligne"])
    _VERDICT = {"strong": ("s", "strong"), "possible": ("p", "possible"), "no-match": ("n", "no candidate")}
    _h8 = rendu["empreinte"][:8]
    page_vivante = ('<div class="pg" aria-hidden="true"><div class="hd"><span>Sample list &#183; invented</span>'
                    f'<span>{ex["lignes"]} names</span></div>'
                    + "".join(f'<div class="rw" style="animation-delay:{k * .12:.2f}s"><code>{html_mod.escape(r["ref"])}</code><span>{html_mod.escape(r["nom"])}</span>'
                              f'<em class="{_VERDICT[r["statut"]][0]}" style="animation-delay:{k * .25:.2f}s">{_VERDICT[r["statut"]][1]}</em></div>'
                              for k, r in enumerate(_rangs))
                    + f'<p class="ft">record {rendu["empreinte"]}</p><div class="sc"></div><svg class="st" viewBox="0 0 100 100" aria-hidden="true"><defs><radialGradient id="sk1g" cx="40%" cy="35%">'
                      '<stop offset="0" class="g0"/><stop offset="1" class="g1"/></radialGradient><path id="sk1c" d="M50,50 m-33,0 a33,33 0 1,1 66,0 a33,33 0 1,1 -66,0"/></defs>'
                      '<circle cx="50" cy="50" r="46" fill="url(#sk1g)"/><circle class="an" cx="50" cy="50" r="40"/>'
                      '<text class="tx" font-family="Roboto Mono,ui-monospace" font-size="7.4" letter-spacing="1.6"><textPath href="#sk1c">SEALED &#183; SCREENED &#183; CRUSETRA &#183; SEALED &#183;</textPath></text>'
                      f'<text class="ce" x="50" y="53" text-anchor="middle" font-family="Roboto Mono,ui-monospace" font-size="7.5">{_h8}</text></svg></div>')
    # the sample-report caption as the seal on the page corner (_LEGENDE_SCEAU, look C kept on Routing), in rubis; the
    # Screening sample is not a signed page, so the ring says SCREENED where Routing's says SIGNED. Every fact of the old
    # caption stays: the count, the fresh run's date, commit and record, the committed record and its date.
    _leg = _en_rubis(_LEGENDE_SCEAU)
    for vieux, neuf in (("SEALED __D__ &#183; SIGNED &#183; CRUSETRA &#183;", "SEALED __D__ &#183; SCREENED &#183; CRUSETRA &#183;"),
                        ("<b>__N__ real receipts</b><small>record __H__<br>signed page beside the PDF</small>",
                         "<b>__N__ invented counterparties</b><small>sample report &#183; a fresh run of __E__ at commit __C__<br>"
                         "record __H__<br>the committed record of the same file is __S__ (__SE__)</small>")):
        if _leg.count(vieux) != 1:
            sys.exit(f"_LEGENDE_SCEAU a changé : « {vieux[:40]} » ne s'y lit plus, la légende Screening ne se pose pas")
        _leg = _leg.replace(vieux, neuf)
    legende = (_leg.replace("__H8__", _h8).replace("__H__", rendu["empreinte"]).replace("__D__", rendu["emis"])
               .replace("__N__", str(ex["lignes"])).replace("__PDF__", pdf).replace("__E__", rendu["emis"])
               .replace("__C__", rendu["commit"]).replace("__SE__", ex["emis"]).replace("__S__", ex["sceau"]))
    if "__" in legende:
        sys.exit("la légende Screening garde un marqueur non remplacé")
    html = f"""<section class="rapport" id="report"><div class="colonne">
  <div class="r-grille">
  <div class="r-texte">
    <p class="marque-h">The screening report</p>
    <h2 class="h2" style="font-size:clamp(24px,2vw,30px);line-height:1.2;max-width:28ch">Send us your list, and within {off["delai_heures"]} hours it comes back screened and sealed.</h2>{_LISTE_VIVANTE_CSS}
    <div class="sk1">{page_vivante}
    <ol>
      <li><b>You send</b><small>a CSV or a spreadsheet with a column of company and vessel names, and the IMO number of a vessel when you have it.</small></li>
      <li><b>We screen</b><small>each name against ten public sources: OFAC SDN, the OFAC consolidated (non-SDN) lists, the US Consolidated Screening List (its Commerce and State lists), the UN Security Council list, the EU financial sanctions list, the UK Sanctions List, the vessels the EU designates in Annex XLII of Regulation 833/2014, Australia's DFAT Consolidated List, the Consolidated Canadian Autonomous Sanctions List and New Zealand's Russia Sanctions Register, each as downloaded on the date the report states. Crusetra is not affiliated with or endorsed by any of their publishers.</small></li>
      <li><b>You receive</b><small>a PDF, a spreadsheet and the sealed record: each candidate with its list entry and the words that matched, the dates of the lists, and a seal anyone can check with one command, <code>npm run sceller -- &lt;record&gt;.screening.json --check</code>.</small></li>
    </ol></div>
  </div>
  <figure class="r-feuille">
    <a href="{pdf}" download><img src="{img}" width="1224" height="1584" loading="lazy" decoding="async"
      alt="First page of the sample report: {ex["lignes"]} invented counterparties, {ex["forts"]} strong candidates, {ex["possibles"]} possible, {ex["sans"]} with no candidate."></a>
    <figcaption style="text-transform:none;letter-spacing:0;opacity:1">{legende}</figcaption>
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
        <ul class="r-inclus"><li><b>{SEMAINES}</b> sealed reports a year</li><li>Each report opens with what changed since the last one</li><li>Billed monthly, or yearly with {off["annuel"]}</li><li>Stop any time: it runs to the end of the period paid, no refund</li></ul>
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
  <p class="r-note">{_rnote_cartes(off["conservation"])}</p>
  <div class="ouvrir-ligne"><a class="ouvrir" href="mailto:{off["contact"]}?subject={sujet}"><span><span class="ouvrir-t">Try it on {EN_LETTRES.get(off["essai_noms"], off["essai_noms"])} of your names</span>
    <span class="ouvrir-s">Email them to {off["contact"]}. The report comes back within {off["delai_heures"]} hours, at no charge.</span></span>
    <span class="fl" aria-hidden="true">&#8594;</span></a></div>
  {liens_tuiles([(pdf, "Download", "The sample report", " download"),
                 ("../rapports/screening-sample-report.screening.json", "Open", "The record this PDF renders", ""),
                 (f"{depot}/blob/main/exemple/contreparties-exemple.screening.json", "Open", "The committed example record", "")])}
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
    for attendu in (usd(r0["prix_usd"]), *(usd(x["prix_usd_mois"]) for x in rc), ex["sceau"], *re.split(r"(?<=\.)\s+", off["conservation"].strip())):   # 25/10: the retention text now spans two cards, each sentence must show
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
        ("Privacy", "What you send us for a report, what we keep, and for how long.",
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
    # 25/10: on Screening, the Routing retouches carried over (pricing tile and numbered footnotes, the seam as a ticker);
    # the other tools keep their card and seam as they were.
    _sorte = "horloge" if o["id"] == "dossier" else "courbes"
    _robot = "../rendus/robot-" + ICONES_COULEUR[o["id"]] + "-regarde.webp"
    if o["id"] == "screening":
        instrument_affiche = _tarif_et_notes(affiche_html(_sorte, RELEVE, FINDINGS, spec["instrument_page"], spec["instrument_eti"],
                                                          spec["instrument_sub"], _robot),
                                             lien(o, "ENGAGEMENT.html"), _notes_outil(spec, RELEVE, FINDINGS))
        couture_html = couture_defile("measured, then frozen", SCEAU_O)
    else:
        instrument_affiche = affiche_html(_sorte, RELEVE, FINDINGS, spec["instrument_page"], spec["instrument_eti"], spec["instrument_sub"], _robot,
                                          note="" if o["id"] == "dossier" else _note_outil(spec, RELEVE, FINDINGS), tarif=lien(o, "ENGAGEMENT.html"))
        # 25/10 evening (Arslane): the ticker replaces the paper seam on every tool page, not on Screening only
        couture_html = couture_defile("measured, then frozen", SCEAU_O)
    # 25/10: the four catalogue pages open on the living hero Arslane picked (HEROS_VIVANTS); a tool without one
    # keeps the plain hero with its commands
    hero_css, hero_html = HEROS_VIVANTS.get(o["id"], ("", None))
    commandes_html = "".join(f'<code class="ln">{c}</code>\n    ' for c in
                             ([f"git clone {o['depot']}", f"cd {o['depot'].rstrip('/').rsplit('/', 1)[1]}"] + spec["commandes"]))

    if hero_html is None:
        hero_html = f'''<section class="hero">
  <h1 class="h1 entree{" h1-long" if len(spec["h1"]) > 48 else ""}">{spec["h1"]}</h1>
  <p class="lede entree">{spec["lede"]}</p>
  <div class="commande entree" role="group" aria-label="{spec["aria_commande"]}">
    {commandes_html}
  </div>{vers_rapport}
  <div class="cue" aria-hidden="true"><span>scroll</span><span class="fil"></span></div>
</section>'''
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
<style>{css_o}{css_scrub_o}{CSS_BARRE_SITE}{hero_css}</style>
{barre_site(courant=o["page_hero"], racine=o["prefixe_racine"])}

<main>
{hero_html}

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
  {instrument_affiche}
</div></section>

{couture_html}
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
    if o["id"] in HEROS_VIVANTS:
        print(o["page_hero"], "· hero button held:", " → ".join(_garde_action(page, o["page_hero"])[::-1]))
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
