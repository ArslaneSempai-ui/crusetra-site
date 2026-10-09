#!/usr/bin/env python3
"""L'annexe, version 3 : le chrome du nouveau monde, le corps ouvrable conservé.

CE QUI EST GARDÉ DE LA VERSION 2 (validée par Arslane le 31 août)
  · les titres de sections en liste OUVRABLE (<details> natifs) ;
  · le moyen de vérifier DANS chaque section, en petit terminal actionnable ;
  · l'objet 3D propre à chaque page, dans la tête ;
  · la lecture en deux colonnes au large.

CE QUI CHANGE (harmonisation du 4 septembre, appliquée aux 8 pages)
  · la palette et les fontes sont CELLES du héros (Literata + Roboto Mono) :
    les deux mondes avaient dérivé de quelques teintes ;
  · la manchette tete/tampon/œil disparaît : la barre FIXE des pages
    principales la remplace (marque, nav, sceau ; nuit en haut, parchemin
    posé après 40 px de défilement, exactement comme l'index) ;
  · la bande verte au tiers de page devient la TÊTE de page : nuit dès le
    premier pixel, « Appendix X » en mono vert, le titre à gauche, l'objet
    à droite — le squelette de la page instrument ;
  · le pied devient celui des pages principales (bande nuit, promesse,
    sceau), augmenté du rang des huit annexes.
"""
import importlib.util
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("bn", BASE / "batir-nav.py")
bn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bn)

from outil import SCEAU_ROUTING, barre_site, CSS_BARRE_SITE, pied_html, n_tests
SCEAU = SCEAU_ROUTING   # lu dans le relevé scellé du vert, jamais tapé (8/09)

# ── les six annexes : une lettre, une source, un objet, une sortie ───────────
# L'ordre suit bn.ANNEXES ; la lettre d'appendice en découle (A-F).
PAGES = [
    {
        "nav": "Method and reproducibility",
        "json": "annexe-methode.json",
        "html": "ANNEXE-METHODE.html",
        "titre_onglet": "Crusetra &#183; method",
        "objet": "rendus/etats/objet-methode.webp",
        "alt": "A matte aluminium balance with two pans at exactly the same "
               "height; the right pan is the site's deep green.",
    },
    {
        "nav": "Security and data handling",
        "json": "annexe-securite.json",
        "html": "ANNEXE-SECURITE.html",
        "titre_onglet": "Crusetra &#183; security",
        "objet": "rendus/etats/objet-securite.webp",
        "alt": "A matte aluminium padlock; its shackle, closed, is the same "
               "deep green as the site's accents.",
    },
    {
        "nav": "Questions",
        "json": "annexe-questions.json",
        "html": "ANNEXE-QUESTIONS.html",
        "titre_onglet": "Crusetra &#183; questions",
        "objet": "rendus/etats/objet-questions.webp",
        "alt": "A matte aluminium key lying across the frame; its bow is a "
               "fat green ring.",
    },
    {
        "nav": "Terms of engagement",
        "json": "annexe-terms.json",
        "html": "ANNEXE-TERMS.html",
        "titre_onglet": "Crusetra &#183; terms",
        "objet": "rendus/etats/objet-terms.webp",
        "alt": "A thick page with three lines of text, a green signature "
               "stroke, and a pen resting with its tip at the stroke's end.",
    },
    {
        "nav": "Privacy",
        "json": "annexe-privacy.json",
        "html": "ANNEXE-PRIVACY.html",
        "titre_onglet": "Crusetra &#183; privacy",
        "objet": "rendus/etats/objet-privacy.webp",
        "alt": "A folder ajar: cream paper showing inside, a green tab on "
               "the cover: nothing leaves it.",
    },
    {
        "nav": "Accessibility",
        "json": "annexe-accessibilite.json",
        "html": "ANNEXE-ACCESSIBILITE.html",
        "titre_onglet": "Crusetra &#183; accessibility",
        "objet": "rendus/etats/objet-accessibilite.webp",
        "alt": "A summit with two slopes: a green ramp rising on the left, "
               "gray steps on the right, arriving at the same platform.",
    },
]
LETTRES = "ABCDEF"

# ── la production : adresses publiées et carte de partage ────────────────────
# L'URL de base est le dépôt Pages DÉDIÉ du site (choix du 31/08 : ne pas
# toucher au docs/ généré de crusetra-routing). Since 6 October it is written ONCE,
# in outil.py (SITE_URL), and every builder and the assembler read it from there.
from outil import SITE_URL as BASE_URL
PROD = {
    "ACCUEIL.html": "index.html",
    "HERO.html": "routing/index.html",
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

# le carré diagonal de la marque, en icône d'onglet
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E"
           "%3Cpath d='M16 0v16H0z' fill='%2323543f'/%3E%3C/svg%3E")


def og(titre, description, fichier):
    """La carte de partage : ce que Teams ou un mail interne montre du lien."""
    import html as _h
    d = _h.escape(description, quote=True)
    t = _h.escape(titre, quote=True)
    url = BASE_URL + PROD[fichier]
    return (f'<meta property="og:type" content="website">\n'
            f'<meta property="og:title" content="{t}">\n'
            f'<meta property="og:description" content="{d}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE_URL}og.png">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="description" content="{d}">')


# la barre se pose sur le parchemin après 40 px, comme sur l'index ; et
# l'impression ouvre les sections, puis les referme comme elles étaient
SCRIPT = """<script>
const barre = document.querySelector(".barre");
const poser = () => {
  barre.classList.toggle("posee", scrollY > 40);
  barre.classList.toggle("sur-nuit", scrollY <= 40);
};
addEventListener("scroll", poser, {passive: true}); poser();
addEventListener("beforeprint", () => {
  for (const d of document.querySelectorAll("details")) {
    d.dataset.avant = d.open ? "1" : ""; d.open = true; }});
addEventListener("afterprint", () => {
  for (const d of document.querySelectorAll("details")) {
    d.open = d.dataset.avant === "1"; }});
</script>"""

CSS = """
  :root{--papier:#dbd7c5;--papier-haut:#e2ddcb;--papier-bas:#cdccb9;--encre:#1b1d18;
    --demi:#4a4739;--pale:#55523f;--filet:#9d9a83;--filet-clair:#bab7a0;
    --nuit-a:#1b3229;--nuit-b:#14251e;--nuit-c:#0e1a15;--sur-vert:#e4ecdf;--sur-vert-pale:#a9bdaf;
    --vert-titre:#23543f;--vert-vif:#57b184;--vert-clair:#a5f7cb;
    --texte:"Literata",Georgia,serif;--mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    --sans:ui-sans-serif,-apple-system,"Helvetica Neue",sans-serif;
    --montee:cubic-bezier(.16,.84,.32,1)}
  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth;overflow-x:clip;caret-color:var(--vert-vif);
    scrollbar-color:var(--vert-titre) var(--papier-bas)}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{background:var(--papier);color:var(--encre);font-family:var(--texte);line-height:1.55}
  img{max-width:100%;height:auto;display:block}
  ::selection{background:var(--vert-titre);color:var(--sur-vert)}
  a{text-underline-offset:4px;color:inherit}
  :focus-visible{outline:3px solid var(--vert-vif);outline-offset:3px;border-radius:2px}
  .colonne{max-width:1180px;margin:0 auto;padding:0 48px}

  /* ── la barre : celle des pages principales, à l'identique ──────────────── */
  .barre{position:fixed;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;gap:28px;
    padding:14px 32px;transition:background .3s,box-shadow .3s}
  .barre.posee{background:color-mix(in srgb,var(--papier-haut) 88%,transparent);
    backdrop-filter:blur(10px);box-shadow:0 1px 0 color-mix(in srgb,var(--filet) 55%,transparent)}
  .barre.sur-nuit .marque{color:var(--sur-vert)}
  .barre.sur-nuit nav a{color:var(--sur-vert-pale)}
  .barre.sur-nuit nav a:hover{color:var(--sur-vert)}
  .marque{font-weight:700;font-size:19px;letter-spacing:.01em;text-decoration:none;
    padding:10px 0;color:var(--encre)}
  .barre nav{display:flex;gap:16px;margin-left:auto}
  .barre nav a{font-size:14.5px;text-decoration:none;color:var(--demi);padding:13px 6px}
  .barre nav a:hover{color:var(--encre);text-decoration:underline;
    text-decoration-color:var(--vert-vif);text-decoration-thickness:1.5px}
  html:not(.js) .barre{position:absolute}
  html:not(.js) .barre .marque{color:var(--sur-vert)}
  html:not(.js) .barre nav a{color:var(--sur-vert-pale)}

  /* ── la tête : nuit dès le premier pixel, titre à gauche, objet à droite ── */
  .tete-nuit{position:relative;padding:132px 0 48px;color:var(--sur-vert);
    background:radial-gradient(120% 100% at 50% -20%,#0f231b,var(--nuit-b) 70%)}
  .tete-nuit .colonne{display:grid;grid-template-columns:minmax(0,1fr) auto;
    gap:18px 40px;align-items:center}
  .ariane{grid-column:1/-1;display:flex;align-items:baseline;gap:16px;flex-wrap:wrap}
  .ariane .fno{font-family:var(--mono);font-size:11.5px;letter-spacing:.15em;
    text-transform:uppercase;color:var(--vert-vif)}
  .ariane .fti{font-family:var(--mono);font-size:11.5px;letter-spacing:.15em;
    text-transform:uppercase;color:var(--sur-vert-pale)}
  .retour{margin-left:auto;font-family:var(--mono);font-size:12px;
    text-decoration:none;color:var(--sur-vert-pale);padding:4px 0}
  .retour:hover{color:var(--sur-vert);text-decoration:underline;
    text-decoration-color:var(--vert-vif)}
  h1{font-size:clamp(32px,4.2vw,56px);font-weight:600;letter-spacing:-.02em;
    line-height:1.06;text-wrap:balance;max-width:21ch}
  h1 .deux{color:var(--vert-vif)}
  .plaque{margin:0;width:min(24vw,300px);height:min(24vh,230px)}
  .plaque img{width:100%;height:100%;object-fit:contain;
    filter:drop-shadow(0 18px 34px rgba(0,0,0,.45))}

  /* ── le document : la liste ouvrable, telle que validée ─────────────────── */
  .doc{padding:38px 0 8px}
  .lede{margin:0 0 26px;font-style:italic;font-size:17px;line-height:1.55;
    color:var(--demi);max-width:88ch}
  details{border-top:1px solid var(--filet-clair)}
  details:last-of-type{border-bottom:1px solid var(--filet-clair)}
  summary{cursor:pointer;list-style:none;display:flex;gap:.8rem;align-items:baseline;
    padding:.95rem .2rem .95rem 0;
    font:500 11.5px/1.4 var(--mono);letter-spacing:.13em;
    text-transform:uppercase;color:var(--pale);
    transition:color .16s ease}
  summary::-webkit-details-marker{display:none}
  summary .cr{font:400 14px/1 var(--sans);color:var(--filet);flex:none;
    transition:transform .2s var(--montee),color .16s ease;width:1em}
  summary:hover{color:var(--encre)}
  summary:hover .cr{color:var(--encre)}
  details[open] summary{color:var(--encre)}
  details[open] summary .cr{transform:rotate(90deg);color:var(--vert-titre)}
  .sec-corps{padding:0 0 1.4rem 1.8rem;max-width:148ch}
  @media (min-width:1100px){
    .sec-corps{columns:2;column-gap:clamp(2.6rem,5vw,5.5rem)}
    .sec-corps p,.sec-corps ul,.sec-corps .ap{break-inside:avoid-column}
    .sec-corps > p:first-child{margin-top:0}
  }
  .sec-corps p{margin:0 0 .8rem;font-size:15.5px;line-height:1.65;color:var(--encre)}
  .sec-corps p:last-child{margin-bottom:0}
  .sec-corps b{font-weight:600}
  .sec-corps .v{color:var(--vert-titre);font-weight:600}
  ul{margin:.2rem 0 .8rem;padding:0;list-style:none;font-size:15.5px;line-height:1.65}
  li{padding-left:1.1rem;position:relative;margin-bottom:.25rem}
  li::before{content:"";position:absolute;left:0;top:.72em;width:6px;height:1.5px;
    background:var(--filet)}
  code{font:400 13.5px/1.5 var(--mono);background:rgba(27,29,24,.055);
    padding:.06rem .3rem}

  /* le moyen de vérifier : les commandes dans un petit écran de terminal :
     actionnables telles quelles : et les références de source EN DESSOUS, parce
     qu'un chemin de fichier ne se tape pas dans un shell. */
  .ap{margin:1rem 0 0;border-left:2px solid var(--vert-titre);padding:.15rem 0 .15rem .9rem}
  .ap-t{font:500 10px/1.4 var(--mono);letter-spacing:.14em;text-transform:uppercase;
    color:var(--vert-titre);display:block;margin-bottom:.3rem}
  .ap p{margin:0 0 .5rem;font:italic 400 13.5px/1.5 var(--texte);
    color:var(--demi)!important;font-size:13.5px!important}
  .term{max-width:44ch;background:linear-gradient(163deg,var(--nuit-a),var(--nuit-b));
    border:1px solid color-mix(in srgb,var(--vert-vif) 22%,transparent);
    border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(20,37,30,.22)}
  .term-bar{display:flex;gap:.32rem;align-items:center;padding:.42rem .6rem;
    background:rgba(0,0,0,.28)}
  .term-bar i{width:7px;height:7px;border-radius:50%;background:var(--sur-vert-pale);opacity:.45}
  .term-bar span{margin-left:auto;font:500 9px/1 var(--mono);letter-spacing:.14em;
    text-transform:uppercase;color:var(--sur-vert-pale)}
  .term-corps{padding:.65rem .8rem .75rem;font:400 12.5px/1.75 var(--mono);
    color:var(--sur-vert)}
  .term-corps .cmd{display:block;white-space:pre-wrap;overflow-wrap:break-word;
    background:none;padding:0}
  /* l'invite est un ::before : elle ne part pas dans le presse-papier */
  .term-corps .cmd::before{content:"$ ";color:var(--vert-vif);font-weight:600}
  .term-corps .sortie{display:block;color:var(--sur-vert-pale);opacity:.9}
  .term-corps .sortie::before{content:"# "}
  .ap p.refs{margin:.5rem 0 0;font:400 11.5px/1.5 var(--mono)!important;
    font-style:normal!important;color:var(--pale)!important}
  .refs b{font:600 9.5px/1.5 var(--mono);letter-spacing:.13em;
    text-transform:uppercase;color:var(--pale);margin-right:.5rem}

  /* ── la plomberie : colonne de lecture simple, filets fins, pas d'objet ──── */
  .pl-doc{max-width:78ch;padding:38px 0 8px}
  .pl-doc .lede{max-width:none}
  .pl-sec{border-top:1px solid var(--filet-clair);padding:1rem 0 1.3rem}
  .pl-sec:last-of-type{border-bottom:1px solid var(--filet-clair)}
  .pl-sec h2{margin:0 0 .55rem;font:500 11.5px/1.4 var(--mono);
    letter-spacing:.13em;text-transform:uppercase;color:var(--pale)}
  .pl-sec p{margin:0 0 .8rem;font-size:15.5px;line-height:1.65;color:var(--encre)}
  .pl-sec p:last-child{margin-bottom:0}
  .pl-sec b{font-weight:600}

  /* ── le pied : celui des pages principales, plus le rang des annexes ────── */
  .pied{background:var(--nuit-c);color:var(--sur-vert);padding:44px 0;margin-top:56px}
  .pied-p{font-size:clamp(17px,1.8vw,23px);font-weight:600}

  @media (prefers-reduced-motion:reduce){
    summary .cr,summary,.barre{transition:none}
  }
  /* ── 641-1080 : la fenêtre de bureau NON MAXIMISÉE ─────────────────────────
     On MAINTIENT la composition du large : l'objet reste à droite du titre,
     plus petit (constat d'Arslane, 31/08 : la mise en page téléphone agrandie
     donnait un objet géant dans une bande gonflée). */
  @media (max-width:1080px){
    .barre{padding:12px 18px;gap:14px}
    .barre nav{display:none}
    .tete-nuit{padding-top:104px}
    .colonne{padding:0 26px}
  }
  @media (min-width:641px) and (max-width:1080px){
    .plaque{width:min(28vw,260px);height:min(22vh,200px)}
  }
  @media (max-width:640px){
    .tete-nuit .colonne{display:block}
    .plaque{width:min(62vw,300px);height:min(26vh,190px);margin:20px auto 0}
    h1{max-width:none}
    .retour{margin-left:0}
    .sec-corps{padding-left:.2rem}
    .colonne{padding:0 22px}
  }

  /* ── l'impression : le mémo qu'un comité fait circuler ───────────────────── */
  @media print{
    body{background:#fff;color:#1b1d18}
    .barre,.plaque,.retour,.pied-liens,.pied-preuve{display:none}
    .tete-nuit{background:none;color:#1b1d18;padding:12px 0 4px}
    h1{color:#1b1d18;max-width:none;font-size:26pt}
    h1 .deux{color:#23543f}
    .ariane .fno{color:#23543f}
    .ariane .fti{color:#55523f}
    .pied{background:none;color:#1b1d18;margin-top:20px;padding:10px 0;
      border-top:1px solid #999}
    .pied-meta,.pied-meta b{color:#55523f}
    .sec-corps{columns:1;max-width:none}
    details,.pl-sec{break-inside:avoid}
    .term{box-shadow:none}
    summary .cr{display:none}
  }
"""

# la nav du haut : celle des pages principales, avec la page courante marquée
def barre_html(courante):
    """Les pages de la maison : la barre du site seule (Arslane, 11/09), le lien courant marqué
    quand la page est dans la barre (Pricing, Contact)."""
    return barre_site(courant=courante)


def section(sec, ouvert=False):
    corps = "".join(sec["html"])
    ap = ""
    if sec.get("verif"):
        v = sec["verif"]
        lignes = "".join(
            f'<code class="cmd">{c["c"]}</code>'
            + (f'<span class="sortie">{c["n"]}</span>' if c.get("n") else "")
            for c in v.get("cmd", []))
        refs = (f'<p class="refs"><b>Where it lives</b>{v["refs"]}</p>'
                if v.get("refs") else "")
        ap = (f'<div class="ap"><span class="ap-t">{v["t"]}</span>'
              f'<p>{v["p"]}</p>'
              f'<div class="term"><div class="term-bar">'
              f'<i></i><i></i><i></i><span>run it yourself</span></div>'
              f'<div class="term-corps">{lignes}</div></div>{refs}</div>')
    dc = f' data-commun="{sec["commun"]}"' if sec.get("commun") else ""
    return (f'<details{" open" if ouvert else ""}{dc}>'
            f'<summary><span class="cr" aria-hidden="true">&#9656;</span>{sec["h2"]}'
            f'</summary><div class="sec-corps">{corps}{ap}</div></details>')


TETE_COMMUNE = ('<meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">')


def _texte(fragment):
    """Le texte nu d'un fragment : balises retirées, entités résolues."""
    import html as _h
    import re as _re
    return " ".join(_h.unescape(_re.sub(r"<[^>]+>", "", fragment)).split())


def faq_ld(sections):
    """La FAQ lisible par les moteurs, générée des MÊMES sections que la page :
    une seule source, donc pas de dérive possible entre ce que lit un visiteur
    et ce que lit un moteur (assembler.py compare quand même, question par
    question). Les réponses sont le texte des paragraphes, sans le bloc de
    vérification (une commande shell n'est pas une réponse) ; les guillemets
    typographiques des titres restent dans la page, pas dans la question nue."""
    import json as _json
    entrees = []
    for sec in sections:
        q = _texte(sec["h2"]).strip("“” ")
        r = " ".join(_texte(p) for p in sec["html"])
        entrees.append({"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": r}})
    bloc = _json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                        "mainEntity": entrees}, ensure_ascii=True)
    return f'\n<script type="application/ld+json">{bloc}</script>'

for lettre, page in zip(LETTRES, PAGES):
    faits = json.loads((BASE / page["json"]).read_text())
    sections = "".join(section(x, i == 0) for i, x in enumerate(faits["sections"]))
    donnees = faq_ld(faits["sections"]) if page["html"] == "ANNEXE-QUESTIONS.html" else ""

    (BASE / page["html"]).write_text(f"""<!doctype html><html lang="en">
<meta charset="utf-8"><title>{page["titre_onglet"]}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
{og(page["titre_onglet"], faits.get("description", faits["lede"]), page["html"])}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">{donnees}
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_BARRE_SITE}</style>
{barre_html(page["html"])}

<main>
<section class="tete-nuit"><div class="colonne">
  <div class="ariane">
    <span class="fno">Appendix {lettre}</span>
    <span class="fti">{page["nav"]}</span>
    <a class="retour" href="HERO.html">&#8592; Back to the findings</a>
  </div>
  <h1>{faits["titre"]}</h1>
  <figure class="plaque"><img src="{page["objet"]}" alt="{page["alt"]}"></figure>
</div></section>

<div class="colonne"><div class="doc">
  <p class="lede">{faits["lede"]}</p>
  {sections}
</div></div>
</main>

{pied_html(sceau=SCEAU, courante=page["html"])}
""" + SCRIPT + "\n", encoding="utf-8")
    print(f"  {page['html']}")

# 04/10 (audit Routing) : la page des conditions porte les quatre offres de Routing et la société qui contracte ;
# ses chiffres sont ceux de offre-routing.json, et la garde les recompare
_OFF = json.loads((BASE / "offre-routing.json").read_text())
_TERMS = (BASE / "ANNEXE-TERMS.html").read_text()
for _attendu in (f"${_OFF['snapshot']['prix_usd']:,}", f"${_OFF['audit']['prix_usd']:,}", f"${_OFF['audit_trimestriel']['prix_usd_an']:,}",
                 f"{_OFF['snapshot']['delai_heures']} hours", f"{_OFF['audit']['delai_heures']} hours", f"within {_OFF['essai']['delai_heures']} hours", "HS Industries LLC", "right to act on the recommendation"):
    if _attendu not in _TERMS:
        sys.exit(f"ANNEXE-TERMS.html n'affiche pas « {_attendu} » : les conditions ne portent plus l'offre Routing")
# 05/10 (parcours client) : la page des conditions porte aussi l'offre Screening et la promesse de conservation tranchée le
# 5/10 ; chaque montant se relit dans offre-screening.json
_OFS = json.loads((BASE / "offre-screening.json").read_text())
for _attendu in (f"${_OFS['rapport']['prix_usd']:,}", *(f"${x['prix_usd_mois']:,}" for x in _OFS["recriblage"]),
                 f"up to {_OFS['rapport']['noms']:,} names", f"{_OFS['essai_noms']} names", f"within {_OFS['delai_heures']} hours",
                 "HS Industries LLC", _OFS["conservation"]):
    if _attendu not in _TERMS:
        sys.exit(f"ANNEXE-TERMS.html n'affiche pas « {_attendu} » : les conditions ne portent plus l'offre Screening")

# ── la plomberie : contact et colophon : colonne simple, sans objet ──────────
PLOMBERIE = json.loads((BASE / "plomberie.json").read_text())
for page in PLOMBERIE["pages"]:
    sections = "".join(
        f'<div class="pl-sec"><h2>{s["h2"]}</h2>{"".join(s["html"])}</div>'
        for s in page["sections"])

    (BASE / page["html"]).write_text(f"""<!doctype html><html lang="en">
<meta charset="utf-8"><title>{page["titre_onglet"]}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
{og(page["titre_onglet"], page.get("description", page["lede"]), page["html"])}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_BARRE_SITE}</style>
{barre_html(page["html"])}

<main>
<section class="tete-nuit"><div class="colonne">
  <div class="ariane">
    <span class="fno">{page["fno"]}</span>
    <a class="retour" href="{page.get("retour_href", "HERO.html")}">{page.get("retour_texte", "&#8592; Back to the findings")}</a>
  </div>
  <h1>{page["titre"]}</h1>
</div></section>

<div class="colonne"><div class="pl-doc">
  <p class="lede">{page["lede"]}</p>
  {sections}
</div></div>
</main>

{pied_html(sceau=SCEAU, courante=page["html"])}
""" + SCRIPT + "\n", encoding="utf-8")
    print(f"  {page['html']}")

# ── les annexes du ROUGE : mêmes gabarits, palette rubis, sous-dossier screening/ ──
# Les deux JSON du lot S3 ont le format des annexes vertes ; les pages naissent
# quand ils existent (l'absence est dite, jamais improvisée), avec la barre et
# le pied de l'outil rouge : les liens vers les pages de la MAISON sortent du
# sous-dossier par outil.lien, les liens entre pages rouges restent nus.
# L'objet 3D de chaque annexe rouge est le même objet que le vert, rendu par
# etats/objets_v2.py avec --accent "#a3182b" (la pierre polie du robot rouge) :
# seule la couleur de l'idée change avec l'outil, le monde reste celui de la maison.
from outil import (OUTILS, PALETTE_VERTE, PALETTE_RUBIS, PALETTE_LAPIS, PALETTE_ONYX, PALETTE_AMETHYSTE,
                   NUIT_VERTE, NUIT_RUBIS, NUIT_LAPIS, NUIT_ONYX, NUIT_AMETHYSTE, lire_releve_scelle, lien)

RUBIS = OUTILS["screening"]
LAPIS = OUTILS["monitoring"]

# Les pages d'annexes PAR OUTIL du catalogue : le rouge d'abord, le bleu par la même
# fonction — une entrée de table, pas une copie. Les teintes d'impression et de tête
# écrites en dur côté vert sont remplacées par celles de l'outil (spec_css).
PAGES_ROUGES = [
    {"nav": "Method and reproducibility", "json": "annexe-screening-methode.json",
     "html": "ANNEXE-SCREENING-METHODE.html", "prod": "screening/method.html",
     "titre_onglet": "Crusetra Screening &#183; method",
     "objet": "rendus/etats/objet-screening-methode.webp",
     "alt": "A matte aluminium balance with two pans at exactly the same height; "
            "the right pan is the tool's deep ruby."},
    {"nav": "Security and data handling", "json": "annexe-screening-securite.json",
     "html": "ANNEXE-SCREENING-SECURITE.html", "prod": "screening/security.html",
     "titre_onglet": "Crusetra Screening &#183; security",
     "objet": "rendus/etats/objet-screening-securite.webp",
     "alt": "A matte aluminium padlock; its shackle, closed, is the same deep ruby "
            "as the tool's accents."},
]
PAGES_LAPIS = [
    {"nav": "Method and reproducibility", "json": "annexe-monitoring-methode.json",
     "html": "ANNEXE-MONITORING-METHODE.html", "prod": "monitoring/method.html",
     "titre_onglet": "Crusetra Monitoring &#183; method",
     "objet": "rendus/etats/objet-monitoring-methode.webp",
     "alt": "A matte aluminium balance with two pans at exactly the same height; "
            "the right pan is the tool's deep lapis blue."},
    {"nav": "Security and data handling", "json": "annexe-monitoring-securite.json",
     "html": "ANNEXE-MONITORING-SECURITE.html", "prod": "monitoring/security.html",
     "titre_onglet": "Crusetra Monitoring &#183; security",
     "objet": "rendus/etats/objet-monitoring-securite.webp",
     "alt": "A matte aluminium padlock; its shackle, closed, is the same deep lapis "
            "blue as the tool's accents."},
]


PAGES_AMETHYSTE = [
    {"nav": "Method and reproducibility", "json": "annexe-scoring-methode.json",
     "html": "ANNEXE-SCORING-METHODE.html", "prod": "scoring/method.html",
     "titre_onglet": "Crusetra Scoring &#183; method",
     "objet": "rendus/etats/objet-scoring-methode.webp",
     "alt": "A matte aluminium balance with two pans at exactly the same height; "
            "the right pan is the tool's deep amethyst."},
    {"nav": "Security and data handling", "json": "annexe-scoring-securite.json",
     "html": "ANNEXE-SCORING-SECURITE.html", "prod": "scoring/security.html",
     "titre_onglet": "Crusetra Scoring &#183; security",
     "objet": "rendus/etats/objet-scoring-securite.webp",
     "alt": "A matte aluminium padlock; its shackle, closed, is the same deep amethyst "
            "as the tool's accents."},
]


PAGES_ONYX = [
    {"nav": "Method and reproducibility", "json": "annexe-dossier-methode.json",
     "html": "ANNEXE-DOSSIER-METHODE.html", "prod": "dossier/method.html",
     "titre_onglet": "Crusetra Dossier &#183; method",
     "objet": "rendus/etats/objet-dossier-methode.webp",
     "alt": "A matte aluminium balance with two pans at exactly the same height; "
            "the right pan is the tool's polished onyx."},
    {"nav": "Security and data handling", "json": "annexe-dossier-securite.json",
     "html": "ANNEXE-DOSSIER-SECURITE.html", "prod": "dossier/security.html",
     "titre_onglet": "Crusetra Dossier &#183; security",
     "objet": "rendus/etats/objet-dossier-securite.webp",
     "alt": "A matte aluminium padlock; its shackle, closed, is the same polished "
            "onyx as the tool's accents."},
]


def barre_outil(o, pages, instrument, courante, sceau):
    """Les pages d'un outil : la barre du site, l'outil courant marqué, son empreinte dans le sceau."""
    return barre_site(courant=o["page_hero"], racine=o["prefixe_racine"])


def batir_annexes_outil(o, pages, palette, nuit, tete_sombre, accent, lot, instrument, hero, nom):
    absentes = [p["json"] for p in pages if not (BASE / p["json"]).exists()]
    if absentes:
        print(f"  annexes {o['id']} non bâties : {absentes} absents (lot {lot}) : l'absence est dite")
        return
    sceau_o = lire_releve_scelle(o["releve"])["empreinte"]
    css_o = CSS.replace(PALETTE_VERTE, palette)
    assert css_o != CSS, "la palette verte n'a pas été trouvée dans le CSS des annexes"
    css_n = css_o.replace(NUIT_VERTE, nuit)
    assert css_n != css_o, "la nuit verte n'a pas été trouvée dans le CSS des annexes"
    # le premier ton de la tête et les teintes d'impression sont écrits en dur côté vert
    css_o = css_n.replace("#0f231b", tete_sombre).replace("#23543f", accent)
    favicon_o = FAVICON.replace("%2323543f", o["favicon_accent"])
    for lettre, page in zip("AB", pages):
        PROD[page["html"]] = page["prod"]
        faits = json.loads((BASE / page["json"]).read_text())
        sections = "".join(section(x, i == 0) for i, x in enumerate(faits["sections"]))
        (BASE / page["html"]).write_text(f"""<!doctype html><html lang="en">
<meta charset="utf-8"><title>{page["titre_onglet"]}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
{og(page["titre_onglet"], faits.get("description", faits["lede"]), page["html"])}
<link rel="icon" href="{favicon_o}">
<link rel="stylesheet" href="{lien(o, "fontes/literata.css")}">
<link rel="stylesheet" href="{lien(o, "fontes/roboto-mono.css")}">
<script>document.documentElement.classList.add("js")</script>
<style>{css_o}{CSS_BARRE_SITE}</style>
{barre_outil(o, pages, instrument, page["html"], sceau_o)}

<main>
<section class="tete-nuit"><div class="colonne">
  <div class="ariane">
    <span class="fno">Appendix {lettre} &#183; {nom}</span>
    <span class="fti">{page["nav"]}</span>
    <a class="retour" href="{hero}">&#8592; Back to the findings</a>
  </div>
  <h1>{faits["titre"]}</h1>
  <figure class="plaque"><img src="{lien(o, page["objet"])}" alt="{page["alt"]}"></figure>
</div></section>

<div class="colonne"><div class="doc">
  <p class="lede">{faits["lede"]}</p>
  {sections}
</div></div>
</main>

{pied_html(outil=o, sceau=sceau_o, tests=n_tests(o), courante=page["html"])}
""" + SCRIPT + "\n", encoding="utf-8")
        assert "\u2014" not in (BASE / page["html"]).read_text(), f"cadratin dans {page['html']}"
        print(f"  {page['html']} ({o['id']})")


batir_annexes_outil(RUBIS, PAGES_ROUGES, PALETTE_RUBIS, NUIT_RUBIS, "#2a1219", "#7a1f2e",
                    "S3", "INSTRUMENT-SCREENING.html", "HERO-SCREENING.html", "Screening")
batir_annexes_outil(LAPIS, PAGES_LAPIS, PALETTE_LAPIS, NUIT_LAPIS, "#131c31", "#1f3f7a",
                    "L5-textes", "INSTRUMENT-MONITORING.html", "HERO-MONITORING.html", "Monitoring")
batir_annexes_outil(OUTILS["scoring"], PAGES_AMETHYSTE, PALETTE_AMETHYSTE, NUIT_AMETHYSTE, "#1a1230", "#4b2a7a",
                    "A-L5-textes", "INSTRUMENT-SCORING.html", "HERO-SCORING.html", "Scoring")
batir_annexes_outil(OUTILS["dossier"], PAGES_ONYX, PALETTE_ONYX, NUIT_ONYX, "#0e0e12", "#1c1c22",
                    "D3", "INSTRUMENT-DOSSIER.html", "HERO-DOSSIER.html", "Dossier")
