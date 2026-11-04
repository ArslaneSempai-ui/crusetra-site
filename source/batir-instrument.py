#!/usr/bin/env python3
"""L'INSTRUMENT EN DIRECT, direction TERMINALE, choisie le 3 septembre.

L'instrument parle comme l'outil : un terminal qui écrit tes lectures. Trois
commandes le structurent : `compose --live` (cliquer les cellules, lire coût et
justesse), `optimise --budget` (le curseur rejoue l'énumération des 16 807
routages avec le départage exact de l'outil), `verify --sealed` (la page refait
le témoin de l'extracteur à l'ouverture, sous les yeux du visiteur). Le robot
de la dernière scène du film veille à côté.

D'OÙ VIENNENT LES CHIFFRES
De instrument-donnees.json, émis par extraire-instrument.mjs : les briques sont
calculées par le code de l'outil lui-même (pricePerThousandExtractions aux
latences gelées du relevé de référence), jamais recopiées. L'extracteur refuse
d'émettre si la recomposition du routage publié ne reproduit pas le landing.

CE QUE LA PAGE NE FAIT PAS
Elle ne touche pas aux documents du visiteur : rien n'entre, rien ne sort
(connect-src 'none', aucune ressource tierce). Mesurer SES fichiers, c'est
l'outil, chez lui : le bouton du bas y mène.
"""
import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).parent

sys.path.insert(0, str(BASE))
from instrument_carte import CSS_NOIR, CSS_VERT, CARTE_VERT_HTML, PANNEAU_VERT_HTML, JS_VERT  # noqa: E402

r = subprocess.run(["node", str(BASE / "extraire-instrument.mjs")],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f"extraire-instrument a refusé :\n{r.stderr}")
print(" ", r.stdout.strip())
D = json.loads((BASE / "instrument-donnees.json").read_text())

FIELDS, TIERS = D["fields"], D["tiers"]
from outil import SCEAU_ROUTING
from outil import OUTILS, barre_site, CSS_BARRE_SITE, pied_html, n_tests, SITE_URL
SCEAU = SCEAU_ROUTING   # lu dans le relevé scellé du vert, jamais tapé (8/09)
DEPOT_URL = OUTILS["routing"]["depot"]   # the repository, written once in outil.py; None while private (DEPOTS_PRIVES)
OFFRE = json.loads((BASE / "offre-routing.json").read_text())
ESSAI = OFFRE["essai"]   # the free test by mail, the route that works while the repository is private


def aside_vos():
    """The side column: the four commands while the repository is public, the free test by mail while it is private."""
    if DEPOT_URL:
        return f'''<p><b>These are our readings. Now test them against yours.</b> The tool clones next to your
    files and measures them where they sit, so your CSV never moves and the report lands beside it.</p>
    </details>
  </div>
  <aside class="clone-col">
  <div class="vos" role="group" aria-label="The four commands that measure your own records">
    <span class="vos-t">The four commands, exactly as they run</span>
    <div class="term"><div class="term-bar"><i></i><i></i><i></i><span>run it yourself</span></div>
    <div class="term-corps">
      <code class="cmd">git clone {DEPOT_URL}</code>
      <code class="cmd">cd {DEPOT_URL.rsplit("/", 1)[1]}</code>
      <code class="cmd">npm ci --ignore-scripts</code>
      <code class="cmd">npm run measure:yours -- --cases=your-file.csv</code>
      <span class="sortie">nothing leaves your machine; cut the network and it still runs</span>
    </div></div>
  </div>
  <div class="ouvrir-ligne"><a class="ouvrir" href="{DEPOT_URL}">Run it on your records <span class="fl" aria-hidden="true">&#8594;</span></a>
    <a class="ouvrir tarif" href="ENGAGEMENT.html">See pricing <span class="fl" aria-hidden="true">&#8594;</span></a></div>
  </aside>'''
    sujet = "Extraction%20cost%20audit%2C%20free%20trial"
    return f'''<p><b>These are our readings. Now test them against yours.</b> Write to us: the free test measures up to
    {ESSAI["pages"]} labeled pages of one document type with the tool, and the one-page report comes back by email within
    {ESSAI["delai_heures"]} hours of the measured record, at no charge. No document comes to us.</p>
    </details>
  </div>
  <aside class="clone-col">
  <div class="vos" role="group" aria-label="The free test by email, on your own records">
    <span class="vos-t">The free test, exactly as it runs</span>
    <div class="term"><div class="term-bar"><i></i><i></i><i></i><span>send it to us</span></div>
    <div class="term-corps">
      <code class="cmd">to: {OFFRE["contact"]}</code>
      <code class="cmd">subject: Extraction cost audit, free trial</code>
      <code class="cmd">attach: nothing; the test runs on the record the tool measures, never on your documents</code>
      <span class="sortie">a one-page PDF by email within {ESSAI["delai_heures"]} hours of the record; the record carries a content hash, this report is not signed</span>
    </div></div>
  </div>
  <div class="ouvrir-ligne"><a class="ouvrir" href="mailto:{OFFRE["contact"]}?subject={sujet}">Try it free on {ESSAI["pages"]} of your pages <span class="fl" aria-hidden="true">&#8594;</span></a>
    <a class="ouvrir tarif" href="ENGAGEMENT.html">See pricing <span class="fl" aria-hidden="true">&#8594;</span></a></div>
  </aside>'''


def table_html():
    tetes = "".join(
        f"<th scope='col'>{t}{'*' if t == 'human' else ''}</th>" for t in TIERS)
    lignes = ""
    for f in FIELDS:
        cells = ""
        for t in TIERS:
            v = D["acc"][t][f]
            s = f"{v:.1f}".rstrip("0").rstrip(".")
            cells += (f'<td><button class="cell" data-f="{f}" data-t="{t}" '
                      f'aria-pressed="false"><span class="c-acc">{s}<small>%</small></span>'
                      f'<span class="c-prix">${D["price"][t][f]:.2f}</span></button></td>')
        lignes += f"<tr><th scope='row'>{f}</th>{cells}</tr>"
    return f'''<div class="t-scroll"><table class="routage">
      <caption class="sr">Pick one tier per field, and each cell shows the measured accuracy and the price of a thousand extractions</caption>
      <thead><tr><th scope="col">field</th>{tetes}</tr></thead><tbody>{lignes}</tbody></table></div>'''


CSS = '''
  :root{--papier:#dbd7c5;--papier-haut:#e2ddcb;--papier-bas:#cdccb9;--encre:#1b1d18;
    --demi:#4a4739;--pale:#55523f;--filet:#9d9a83;
    --nuit-a:#1b3229;--nuit-b:#14251e;--nuit-c:#0e1a15;--sur-vert:#e4ecdf;--sur-vert-pale:#a9bdaf;
    --vert-titre:#23543f;--vert-vif:#57b184;--vert-clair:#a5f7cb;
    --texte:"Literata",Georgia,serif;--mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    --sans:ui-sans-serif,-apple-system,"Helvetica Neue",sans-serif;
    --montee:cubic-bezier(.16,.84,.32,1)}
  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth;caret-color:var(--vert-vif);
    scrollbar-color:var(--vert-titre) var(--nuit-c)}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{background:var(--nuit-b);color:var(--sur-vert);font-family:var(--texte);line-height:1.55}
  img{max-width:100%;height:auto;display:block}
  ::selection{background:var(--vert-vif);color:var(--nuit-c)}
  a{text-underline-offset:4px;color:inherit}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  :focus-visible{outline:3px solid var(--vert-vif);outline-offset:3px;border-radius:2px}
  .colonne{max-width:1240px;margin:0 auto;padding:0 48px}

  .barre{position:absolute;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;gap:28px;
    padding:14px 32px}
  .marque{font-weight:700;font-size:19px;letter-spacing:.01em;text-decoration:none;color:var(--sur-vert)}
  .barre nav{display:flex;gap:16px;margin-left:auto}
  .barre nav a{font-size:14.5px;text-decoration:none;color:var(--sur-vert-pale);padding:13px 6px}
  .barre nav a:hover{color:var(--sur-vert);text-decoration:underline;
    text-decoration-color:var(--vert-vif);text-decoration-thickness:1.5px}
  .barre nav a[aria-current]{color:var(--sur-vert)}

  .tete{padding:192px 0 30px;
    background:radial-gradient(120% 100% at 50% -20%,#0f231b,var(--nuit-b) 70%)}
  .h1{font-size:clamp(36px,4.6vw,62px);font-weight:600;letter-spacing:-.02em;line-height:1.05;
    text-wrap:balance;max-width:16ch}
  .lede{font-size:clamp(15px,1.25vw,18px);color:var(--sur-vert-pale);max-width:50ch;
    line-height:1.6;margin-top:16px;text-wrap:balance}
  .lede b{color:var(--sur-vert)}

  /* ── le poste : le robot penché derrière le bord du terminal, coupé net ── */
  .poste{position:relative;padding:44px 0 64px}
  .dessus{position:relative;width:min(100%,1020px);margin:0 auto}
  .rb{position:absolute;right:30px;top:-312px;width:340px;z-index:2;pointer-events:none;
    filter:drop-shadow(0 26px 44px rgba(0,0,0,.55))}
  .terminal{position:relative;z-index:3;
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-b) 55%,#000),color-mix(in srgb,var(--nuit-c) 92%,#000) 120px);
    border:1px solid color-mix(in srgb,var(--vert-vif) 30%,transparent);border-radius:14px;
    box-shadow:0 60px 140px rgba(0,0,0,.7),0 0 0 1px rgba(0,0,0,.4),
      inset 0 1px 0 color-mix(in srgb,var(--vert-clair) 22%,transparent);overflow:hidden}
  .terminal::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:14px;
    background:repeating-linear-gradient(to bottom,rgba(165,247,203,.016) 0 1px,transparent 1px 3px)}
  .caret{display:inline-block;width:7px;height:14px;vertical-align:-2px;background:var(--vert-clair);
    margin-left:6px;animation:caret 1.1s steps(1) infinite}
  @keyframes caret{50%{opacity:0}}
  .t-page-halo{position:absolute;left:50%;top:52%;width:min(1100px,92vw);height:min(700px,70vw);
    transform:translate(-50%,-50%);pointer-events:none;
    background:radial-gradient(50% 50% at 50% 50%,color-mix(in srgb,var(--vert-vif) 12%,transparent),transparent 70%)}
  .tm-barre{display:flex;align-items:center;gap:8px;padding:11px 16px;
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 55%,#000),color-mix(in srgb,var(--nuit-b) 75%,#000));
    border-bottom:1px solid color-mix(in srgb,var(--sur-vert-pale) 14%,transparent)}
  .tm-barre i{width:10px;height:10px;border-radius:50%;
    background:color-mix(in srgb,var(--sur-vert-pale) 30%,transparent)}
  .tm-barre i:first-child{background:var(--vert-vif);
    box-shadow:0 0 8px color-mix(in srgb,var(--vert-vif) 70%,transparent)}
  .tm-titre{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--sur-vert-pale);
    margin-left:8px}
  .tm-corps{padding:18px 22px 20px;font-family:var(--mono);font-size:12.5px;line-height:1.7}
  .tm-l{color:var(--sur-vert-pale)}
  .tm-l .ps{color:var(--vert-vif)}
  .tm-sortie{margin:10px 0 14px;color:var(--sur-vert)}
  .tm-sortie b{color:var(--vert-clair);font-weight:500}
  .tm-preuve{color:var(--sur-vert-pale);margin-top:10px}
  .tm-preuve .ok{color:var(--vert-vif)}
  .tm-preuve .ko{color:#d96b4a}
  .regl{font-family:var(--texte);font-size:13.5px;font-weight:600;background:none;
    border:1px solid color-mix(in srgb,var(--vert-vif) 40%,transparent);
    border-radius:8px;padding:8px 13px;cursor:pointer;color:var(--vert-clair);
    transition:background .2s,color .2s,border-color .2s}
  .regl:hover{border-color:var(--vert-vif)}
  .regl.actif{background:var(--vert-vif);color:var(--nuit-c);border-color:var(--vert-vif)}
  .tm-regl{display:flex;gap:10px;margin:12px 0 4px;flex-wrap:wrap}

  .terminal .t-scroll{overflow-x:auto;border:0;
    border-top:1px solid color-mix(in srgb,var(--sur-vert-pale) 12%,transparent);
    border-bottom:1px solid color-mix(in srgb,var(--sur-vert-pale) 12%,transparent)}
  .routage{width:100%;border-collapse:collapse;background:transparent;
    color:var(--sur-vert);font-family:var(--mono);font-size:13px;min-width:640px}
  .routage th{padding:11px 10px;text-align:center;font-size:11px;letter-spacing:.1em;
    text-transform:uppercase;color:var(--sur-vert-pale);
    border:1px solid color-mix(in srgb,var(--sur-vert-pale) 12%,transparent)}
  .routage tbody th{text-align:left;padding-left:16px}
  .routage td{padding:0;border:1px solid color-mix(in srgb,var(--sur-vert-pale) 12%,transparent)}
  .cell{display:flex;flex-direction:column;gap:2px;align-items:center;justify-content:center;
    width:100%;min-height:54px;padding:7px 10px;background:none;border:0;cursor:pointer;
    font-family:var(--mono);color:var(--sur-vert);transition:background .16s,box-shadow .16s}
  .cell:hover{background:color-mix(in srgb,var(--vert-vif) 12%,transparent);
    box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--vert-vif) 55%,transparent)}
  .cell[aria-pressed="true"]{background:color-mix(in srgb,var(--vert-vif) 18%,transparent);
    color:var(--vert-clair);box-shadow:inset 0 0 0 1.5px var(--vert-vif)}
  .c-acc{font-size:13px}
  .c-acc small{font-size:.7em;color:var(--sur-vert-pale)}
  .c-prix{font-size:10px;color:color-mix(in srgb,var(--sur-vert-pale) 80%,transparent);
    letter-spacing:.04em}
  .cell[aria-pressed="true"] .c-prix{color:var(--vert-clair)}

  .b-ligne{display:flex;gap:26px;align-items:center;flex-wrap:wrap;margin-top:8px}
  .b-curseur{flex:1;min-width:280px}
  input[type=range]{width:100%;accent-color:var(--vert-vif);height:30px}
  .b-grad{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10.5px;
    color:var(--sur-vert-pale);letter-spacing:.04em;margin-top:2px}
  .b-lecture{font-family:var(--mono);font-size:12.5px;color:var(--sur-vert-pale);min-width:280px}
  .b-lecture b{color:var(--vert-clair);font-weight:500;font-size:15px}
  .b-lecture .b-rout{display:block;margin-top:6px;line-height:1.6}

  /* ── les réserves, sur papier ── */
  .reserves{background:var(--papier);color:var(--encre);padding:64px 0 70px}
  .reserves h2{font-size:clamp(22px,2.4vw,32px);font-weight:600;letter-spacing:-.015em;
    margin-bottom:14px}
  .reserves p{font-size:15px;color:var(--demi);line-height:1.65;max-width:76ch;margin-bottom:10px}
  .reserves b{color:var(--encre)}
  /* le terminal des trois commandes : le composant « run it yourself » des
     annexes, posé sur le parchemin ; l'invite $ vit en ::before, elle ne part
     pas dans le presse-papier */
  .vos{margin-top:26px}
  .vos-t{font:500 10px/1.4 var(--mono);letter-spacing:.14em;text-transform:uppercase;
    color:var(--vert-titre);display:block;margin-bottom:8px}
  .term{max-width:62ch;background:linear-gradient(163deg,var(--nuit-a),var(--nuit-b));
    border:1px solid color-mix(in srgb,var(--vert-vif) 22%,transparent);
    border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(20,37,30,.22)}
  .term-bar{display:flex;gap:.32rem;align-items:center;padding:.42rem .6rem;
    background:rgba(0,0,0,.28)}
  .term-bar i{width:7px;height:7px;border-radius:50%;background:var(--sur-vert-pale);opacity:.45}
  .term-bar span{margin-left:auto;font:500 9px/1 var(--mono);letter-spacing:.14em;
    text-transform:uppercase;color:var(--sur-vert-pale)}
  .term-corps{padding:.7rem .9rem .8rem;font:400 12.5px/1.8 var(--mono);color:var(--sur-vert)}
  .term-corps .cmd{display:block;white-space:pre-wrap;overflow-wrap:break-word}
  .term-corps .cmd::before{content:"$ ";color:var(--vert-vif);font-weight:600}
  .term-corps .sortie{display:block;color:var(--sur-vert-pale);opacity:.9}
  .term-corps .sortie::before{content:"# "}
  .ouvrir-ligne{display:flex;justify-content:flex-end;gap:14px;flex-wrap:wrap;margin-top:26px}
  .ouvrir.tarif{opacity:.85}
  .ouvrir{display:inline-flex;align-items:baseline;gap:12px;background:transparent;
    color:var(--vert-titre);text-decoration:none;font-family:var(--texte);font-size:17px;font-weight:600;
    padding:14px 26px;border-radius:10px;border:1px solid color-mix(in srgb,var(--vert-titre) 55%,transparent);
    transition:background .2s,color .2s,border-color .2s}
  .ouvrir .fl{font-family:var(--sans);transition:transform .2s var(--montee)}
  .ouvrir:hover{background:var(--vert-titre);color:var(--sur-vert);border-color:var(--vert-titre)}
  .ouvrir:hover .fl{transform:translateX(4px)}

  .pied{background:var(--nuit-c);color:var(--sur-vert);padding:52px 0}
  .pied-p{font-size:clamp(17px,1.8vw,23px);font-weight:600}

  @media (max-width:1080px){
    .colonne{padding:0 22px}
    .barre{padding:12px 18px;gap:14px}
    .barre nav{display:none}
    .rb{display:none}
    .poste{padding-top:10px}
    .tete{padding-top:110px}
  }
  html:not(.js) .cell{cursor:default}
  html:not(.js) .tm-regl,html:not(.js) .b-ligne,html:not(.js) .tm-sortie,
  html:not(.js) .tm-l{display:none}
  html:not(.js) .tm-preuve{display:block}
  @media (prefers-reduced-motion:reduce){
    *{transition-duration:.01ms!important;animation-duration:.01ms!important}}
'''

JS = '''
  const D = DONNEES;
  const F = D.fields, T = D.tiers;
  const $ = (s) => document.querySelector(s);
  const cells = new Map();
  document.querySelectorAll(".cell").forEach((c) => cells.set(c.dataset.f + "/" + c.dataset.t, c));
  const fmtC = (c) => { const v = c * 100;
    return v >= 995 ? "$" + Math.round(v).toLocaleString("en-US")
         : v >= 99.5 ? "$" + v.toFixed(0) : "$" + v.toFixed(1); };
  let routage = { ...D.publie.routage };
  const lire = (r) => ({
    cout: F.reduce((s, f) => s + D.price[r[f]][f], 0),
    just: F.reduce((s, f) => s + D.acc[r[f]][f], 0) / F.length });
  function peindre() {
    for (const [cle, c] of cells) {
      const [f, t] = cle.split("/");
      c.setAttribute("aria-pressed", routage[f] === t ? "true" : "false");
    }
    const { cout, just } = lire(routage);
    const { cout: cp, just: jp } = lire(D.publie.routage);
    $("#tm-rout").textContent = F.map((f) => f + ":" + routage[f]).join(" \u00b7 ");
    $("#tm-cout").textContent = fmtC(cout);
    $("#tm-just").textContent = just.toFixed(1) + "%";
    const dc = (cout - cp) * 100, dj = just - jp;
    $("#tm-delta").innerHTML = "vs published  "
      + (dc >= 0 ? "+" : "&#8722;") + "$" + Math.abs(dc).toFixed(Math.abs(dc) < 99.5 ? 1 : 0)
      + " &#183; " + (dj >= 0 ? "+" : "&#8722;") + Math.abs(dj).toFixed(1) + "&nbsp;pt";
    const memePub = F.every((f) => routage[f] === D.publie.routage[f]);
    const memeVise = F.every((f) => routage[f] === D.vise.routage[f]);
    $("#r-pub").classList.toggle("actif", memePub);
    $("#r-vise").classList.toggle("actif", memeVise);
    viseV = null; dessinerV(); peindrePanneauV();     /* a change of routing reads the routing, not a stale hover */
  }
  cells.forEach((c) => c.addEventListener("click", () => {
    routage[c.dataset.f] = c.dataset.t; peindre(); }));
  $("#r-pub").addEventListener("click", () => { routage = { ...D.publie.routage }; peindre(); });
  $("#r-vise").addEventListener("click", () => { routage = { ...D.vise.routage }; peindre(); });

  /* l'espace entier des routages, comme l'outil : justesse d'abord, le coût départage */
  const frontiere = (() => {
    const pts = [];
    const marche = (i, r, cout, just) => {
      if (i === F.length) { pts.push({ r: { ...r }, cout, just: just / F.length }); return; }
      for (const t of T) { r[F[i]] = t;
        marche(i + 1, r, cout + D.price[t][F[i]], just + D.acc[t][F[i]]); }
    };
    marche(0, {}, 0, 0);
    pts.sort((a, b) => a.cout - b.cout || b.just - a.just);
    const front = []; let m = -1;
    for (const p of pts) if (p.just > m) { front.push(p); m = p.just; }
    return front;
  })();
  const curseur = $("#b-curseur");
  curseur.addEventListener("input", () => {
    const budget = Math.pow(10, parseFloat(curseur.value)) / 100;
    let best = null;
    for (const p of frontiere) { if (p.cout <= budget) best = p; else break; }
    const sortie = $("#b-lecture");
    if (!best) { sortie.innerHTML = "under <b>" + fmtC(budget) + "</b>: nothing fits"; return; }
    sortie.innerHTML = "under <b>" + fmtC(budget) + "</b>: best reads <b>" + best.just.toFixed(1)
      + "%</b> for <b>" + fmtC(best.cout) + "</b>"
      + '<span class="b-rout">' + F.map((f) => f + " &#8594; " + best.r[f]).join(" &#183; ") + "</span>";
    routage = { ...best.r }; peindre();
  });

  /* verify --sealed : la page refait le témoin de l'extracteur, sous les yeux du visiteur */
  (() => {
    const { cout, just } = lire(D.publie.routage);
    const okC = Math.abs(cout - D.publie.cout) <= 1e-4;
    const okJ = Math.abs(just - D.publie.justesse) <= 0.05;
    const el = $("#tm-preuve");
    if (okC && okJ) {
      el.innerHTML = 'self-check <span class="ok">passed</span>: these bricks recompose the published routing at '
        + fmtC(cout) + " /100k and " + just.toFixed(1) + "%, as sealed on "
        + D.provenance.landingMeasuredAt.slice(0, 10) + " (commit " + D.provenance.commit + ")";
    } else {
      el.innerHTML = 'self-check <span class="ko">FAILED</span>: this page no longer reproduces the sealed routing; do not trust its figures';
    }
  })();
''' + JS_VERT + '''
  peindre();
'''

PAGE = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra &#183; live instrument</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra: the live instrument">
<meta property="og:description" content="Compose a routing cell by cell, or let the budget decide: the same bricks the tool bills, frozen and self-checked in your browser.">
<meta property="og:url" content="{SITE_URL}instrument.html">
<meta property="og:image" content="{SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="Compose a routing cell by cell, or let the budget decide: the same bricks the tool bills, frozen and self-checked in your browser.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E%3Cpath d='M16 0v16H0z' fill='%2323543f'/%3E%3C/svg%3E">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_NOIR}{CSS_VERT}{CSS_BARRE_SITE}</style>
{barre_site(courant=OUTILS["routing"]["page_hero"], racine="")}

<main>
<section class="tete"><div class="colonne">
  <h1 class="h1">Test the routing on our public test set, live.</h1>
  <p class="lede">One model tier per field, which is the size of model that field is sent to.
    Click any cell to see what that routing costs and how often it gets the field right, or set
    your budget and let the tool choose, the way it does on your machine: <b>highest accuracy
    first, lower cost when two tie</b>.</p>
</div></section>

<section aria-label="The live instrument"><div class="colonne">
  <div class="poste">
    <span class="t-page-halo" aria-hidden="true"></span>
    <div class="dessus">
    <div class="poste-grille">
    <div class="fen-robot">
    <div class="terminal">
      <div class="tm-barre"><i></i><i></i><i></i><span class="tm-titre">crusetra &#183; live instrument</span></div>
      <div class="tm-corps">
        <p class="tm-l"><span class="ps">$</span> crusetra compose --live<span class="caret" aria-hidden="true"></span></p>
        <p class="tm-sortie">your routing &#160;<span id="tm-rout">name:large &#183; birth:rules &#183; document:rules &#183; country:rules &#183; address:gen-4b</span><br>
          cost &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;<b id="tm-cout">$191</b> /100k docs &#183; assumed prices<br>
          accuracy &#160;&#160;&#160;&#160;<b id="tm-just">94.4%</b> per-field mean &#183; no interval<br>
          <span id="tm-delta" class="tm-l">vs published  +$0 &#183; +0.0&nbsp;pt</span></p>
        <div class="tm-regl">
          <button class="regl actif" id="r-pub">published &#183; $191</button>
          <button class="regl" id="r-vise">file-aimed &#183; $54</button>
        </div>
        {CARTE_VERT_HTML}
      </div>
      {table_html()}
      <div class="tm-corps">
        <p class="tm-l"><span class="ps">$</span> crusetra optimise --budget</p>
        <div class="b-ligne">
          <div class="b-curseur">
            <label class="sr" for="b-curseur">Budget, dollars per hundred thousand documents, logarithmic</label>
            <input type="range" id="b-curseur" min="0" max="5" step="0.01" value="2.3">
            <div class="b-grad" aria-hidden="true"><span>$1</span><span>$10</span><span>$100</span><span>$1k</span><span>$10k</span><span>$100k</span></div>
          </div>
          <p class="b-lecture" id="b-lecture">slide to read the best routing under your budget</p>
        </div>
        <p class="tm-l" style="margin-top:14px"><span class="ps">$</span> crusetra verify --sealed</p>
        <p class="tm-preuve" id="tm-preuve">self-check requires JavaScript. The figures above are still our frozen readings.</p>
      </div>
    </div>
    </div>
    <div class="pan-col">
    <img class="rb" src="rendus/robot-vert-regarde.webp" alt="">
    {PANNEAU_VERT_HTML}
    </div>
    </div>
    </div>
  </div>
</div></section>
</main>

<section class="reserves"><div class="colonne reserves-grille">
  <div class="plis">
    <details class="pli" open><summary>What this instrument rests on, and what it cannot do.</summary>
  <p><b>The prices are assumed, and the page labels them as such.</b> The small and large tiers use assumed per-call
    rates. The generative tiers use their measured latency against an assumed machine cost. The
    human tier uses an assumed pace and salary. <b>Change the assumptions and the dollars move.
    The accuracies do not.</b></p>
  <p><b>The human column is the one exception, an assumption until you measure it.</b>
    We assume {D["humanAccuracy"]:.0f}% on each field, which the tool declares in its own source. Each other accuracy shown here was measured. <code>npm run measure:humans -- --cases=your-file.csv</code>
    grades your own reviewers: accuracy per field with intervals, agreement between reviewers,
    seconds per record. Pass the sealed result to <code>optimise</code> with <code>--humans</code>
    and the optimizer reads your measurement instead of the assumption.</p>
  <p><b>Your documents never touch this page,</b> because nothing is uploaded and nothing is
    fetched: the browser's own security rules refuse each network call.</p>
  {aside_vos()}
</div></section>

{pied_html(outil=OUTILS["routing"], sceau=SCEAU, tests=n_tests(OUTILS["routing"]), prefixe="")}

<script>
const DONNEES = {json.dumps({k: D[k] for k in ("fields", "tiers", "price", "acc", "publie", "vise", "provenance")})};
{JS}</script>
'''

assert "—" not in PAGE, "un cadratin s'est glissé dans la page"
(BASE / "INSTRUMENT.html").write_text(PAGE, encoding="utf-8")
print(f"INSTRUMENT.html {len(PAGE) / 1e3:.0f} ko")
