#!/usr/bin/env python3
"""L'INSTRUMENT ROUGE EN DIRECT, sur la forme terminale du vert.

Trois commandes le structurent : `crusetra screen --live` (la grille palier x seuil
du releve public, cliquer une cellule lit rappel et fausses alertes avec n et
intervalle), `optimise --recall` (le curseur de rappel exige rejoue la selection
de l'outil a la borne BASSE de Wilson sur les 51 seuils, et nomme la cellule ou
dit qu'aucune ne tient), `verify --sealed` (a l'ouverture, la page reapplique la
regle de selection aux donnees embarquees et refuse de se croire si elle ne
retombe pas sur la cellule emise ; l'empreinte du scelle s'affiche).

D'OU VIENNENT LES CHIFFRES
De instrument-screening-donnees.json, emis par extraire-instrument-screening.mjs :
le releve public scelle de cascade-screening, verifie puis recompose cellule par
cellule temoin avec le rate() de l'outil avant d'avoir le droit d'exister. Les
paires sont ECRITES PAR LE DEPOT (60 match, 60 negatifs durs), la moitie
synthetique est declaree et tenue a part ; aucune donnee client n'existe ici.

CE QUE LA PAGE NE FAIT PAS
Rien n'entre, rien ne sort (connect-src 'none', aucune ressource tierce). Mesurer
l'historique d'alertes du lecteur, c'est l'outil, chez lui : le terminal du bas
donne les trois vraies commandes.
"""
import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))
from instrument_carte import CSS_NOIR, carte_html, PANNEAU_HTML, js_carte  # noqa: E402  (the live chart, shared)
from outil import OUTILS, barre_site, CSS_BARRE_SITE, pied_html, n_tests, SITE_URL

r = subprocess.run(["node", str(BASE / "extraire-instrument-screening.mjs")],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f"extraire-instrument-screening a refuse :\n{r.stderr}")
print(" ", r.stdout.strip())
D = json.loads((BASE / "instrument-screening-donnees.json").read_text())

PALIERS = [p["id"] for p in D["paliers"]]
MONTRES = D["seuilsMontres"]
DEPOT_URL = OUTILS["screening"]["depot"]   # the repository, written once in outil.py; None while private (DEPOTS_PRIVES)
# the self-serve test's data (essai-screening/donnees.json): what the side column says it covers is read there
_ESSAI = json.loads((BASE / "essai-screening" / "donnees.json").read_text())
N_ESSAI_LISTES, N_ESSAI_OUTIL = len(_ESSAI["listes"]), _ESSAI["listesDeLOutil"]
_DATES = sorted(l["telechargeLe"][:10] for l in _ESSAI["listes"])
ESSAI_DATE = _DATES[0] if _DATES[0] == _DATES[-1] else f"{_DATES[0]} to {_DATES[-1]}"
EN_LETTRES = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def pc(x):
    s = f"{x * 100:.0f}"
    return s


def table_html():
    """La grille palier x seuil des huit colonnes du releve, moitie etiquetee au depart.
    Les cellules ne portent AUCUN chiffre en dur : le JS les peint depuis D, et les
    repeint quand on bascule sur la moitie synthetique."""
    tetes = "".join(f"<th scope='col'>{s:.2f}</th>" for s in MONTRES)
    lignes = ""
    for p in PALIERS:
        cells = "".join(
            f'<td><button class="cell" data-p="{p}" data-s="{s:.2f}" aria-pressed="false">'
            f'<span class="c-rappel"></span><span class="c-fp"></span></button></td>'
            for s in MONTRES)
        lignes += f"<tr><th scope='row'>{p}</th>{cells}</tr>"
    absents = "".join(
        f"<tr class='absent'><th scope='row'>{a}</th>"
        f"<td colspan='{len(MONTRES)}'>not in tonight's registry: measured when it ships, absent rather than faked</td></tr>"
        for a in D["absents"])
    return f'''<div class="t-scroll"><table class="grille">
      <caption class="sr">Pick a cell: each shows what it catches on confirmed matches, over its false alerts on near-matches, at that threshold</caption>
      <thead><tr><th scope="col">matcher \\ threshold</th>{tetes}</tr></thead>
      <tbody>{lignes}{absents}</tbody></table></div>'''


from style_instrument_screening import CSS  # noqa: E402  (the instrument's look, shared with the self-serve test)

JS = '''
  const $ = (s) => document.querySelector(s);
  const D = JSON.parse(document.getElementById("donnees").textContent);
  const MONTRES = D.seuilsMontres.map((s) => s.toFixed(2));
  let moitie = "authored";

  const pc = (x) => (x * 100).toFixed(0) + "%";
  const pc1 = (x) => (x * 100).toFixed(1) + "%";
  const iv = (c) => "[" + (c.bas * 100).toFixed(0) + "\\u2013" + (c.haut * 100).toFixed(0) + "]";

  const cells = [...document.querySelectorAll(".cell")];
  function peindreGrille() {
    const g = D[moitie].grille;
    for (const c of cells) {
      const cel = g[c.dataset.p][c.dataset.s];
      c.querySelector(".c-rappel").textContent = pc(cel.rappel.taux);
      c.querySelector(".c-fp").textContent = pc(cel.fauxPositifs.taux);
    }
    $("#g-quoi").innerHTML = moitie === "authored"
      ? "written pairs: <b>" + D.authored.nMatch + " match</b>, <b>" + D.authored.nDifferent + " near-matches</b>"
      : "generated, declared and counted on their own: <b>" + D.synthetic.nMatch + " match</b>, <b>" + D.synthetic.nDifferent + " different</b>";
  }
  function lire(c) {
    cells.forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
    const cel = D[moitie].grille[c.dataset.p][c.dataset.s];
    $("#g-lecture").innerHTML = "<b>" + c.dataset.p + "</b> at threshold <b>" + c.dataset.s + "</b>: "
      + "recall on confirmed matches <b>" + pc1(cel.rappel.taux) + "</b> " + iv(cel.rappel) + ", n=" + cel.rappel.n
      + " \\u00b7 false alerts <b>" + pc1(cel.fauxPositifs.taux) + "</b> " + iv(cel.fauxPositifs) + ", n=" + cel.fauxPositifs.n;
    vise = null; dessiner(); peindrePanneau();
  }
  cells.forEach((c) => c.addEventListener("click", () => lire(c)));
  $("#m-auth").addEventListener("click", () => { moitie = "authored"; basculer(); });
  $("#m-synth").addEventListener("click", () => { moitie = "synthetic"; basculer(); });
  function basculer() {
    $("#m-auth").classList.toggle("actif", moitie === "authored");
    $("#m-synth").classList.toggle("actif", moitie === "synthetic");
    peindreGrille();
    const presse = cells.find((x) => x.getAttribute("aria-pressed") === "true");
    if (presse) lire(presse);
    dessiner(); peindrePanneau();
  }

  /* LA MEME REGLE QUE L'OUTIL, reappliquee ici : borne basse du rappel au plancher,
     puis le moins de fausses alertes, puis le palier le moins cher, puis le seuil haut. */
  const rangs = Object.fromEntries(D.paliers.map((p) => [p.id, p.rang]));
  function retenir(plancher) {
    let best = null;
    for (const [palier, grille] of Object.entries(D.authored.grille)) {
      for (const [seuil, cel] of Object.entries(grille)) {
        if (cel.rappel.bas < plancher) continue;
        const cand = { palier, seuil: Number(seuil), rang: rangs[palier], rappel: cel.rappel, fauxPositifs: cel.fauxPositifs };
        if (best === null
          || cand.fauxPositifs.taux < best.fauxPositifs.taux
          || (cand.fauxPositifs.taux === best.fauxPositifs.taux && (cand.rang < best.rang
          || (cand.rang === best.rang && cand.seuil > best.seuil)))) best = cand;
      }
    }
    return best;
  }
  const curseur = $("#b-curseur");
  function rejouer() {
    plancher = parseFloat(curseur.value);      /* the slider and the floor line are ONE value */
    $("#b-val").textContent = plancher.toFixed(2);
    const c = retenir(plancher);
    const sortie = $("#b-lecture");
    if (!c) {
      sortie.innerHTML = "no cell holds a recall LOWER BOUND of <b>" + plancher.toFixed(2)
        + "</b> on our public test set \\u00b7 the tool would say the same, and name the strongest bound available";
    } else {
      sortie.innerHTML = "under a recall floor of <b>" + plancher.toFixed(2) + "</b> (lower bound, the tool's rule): "
        + "<b>" + c.palier + "</b> at threshold <b>" + c.seuil.toFixed(2) + "</b>"
        + '<span class="b-rout">recall ' + pc1(c.rappel.taux) + " " + iv(c.rappel) + ", n=" + c.rappel.n
        + " \\u00b7 false alerts " + pc1(c.fauxPositifs.taux) + " " + iv(c.fauxPositifs) + ", n=" + c.fauxPositifs.n + "</span>";
    }
    dessiner(); peindrePanneau();
  }
  curseur.addEventListener("input", rejouer);

  /* verify --sealed : la page reapplique la regle et doit retomber sur la cellule emise */
  (() => {
    const relu = retenir(D.recommandee.plancher);
    const el = $("#tm-preuve");
    const ok = relu !== null && relu.palier === D.recommandee.palier && relu.seuil === D.recommandee.seuil;
    if (ok) {
      el.innerHTML = 'self-check <span class="ok">passed</span>: this page reapplies the tool\\u2019s selection rule to the shipped grid and lands on the same cell the extractor sealed \\u00b7 record '
        + D.provenance.empreinte + ", " + D.provenance.date + " (commit " + D.provenance.commit + ")";
    } else {
      el.innerHTML = 'self-check <span class="ko">FAILED</span>: this page no longer reproduces the sealed selection; do not trust its figures';
    }
  })();

''' + js_carte("threshold", "recall", "false alerts") + '''
  peindreGrille();
  curseur.value = D.recommandee.plancher;
  rejouer();
  dessiner(); peindrePanneau();
'''

ABSENTS = ", ".join(D["absents"]) if D["absents"] else ""
# la phrase suit l'état du registre : des parenthèses vides « () » se sont affichées
# le soir où le septième palier est arrivé (relu sur capture)
PHRASE_ABSENTS = (
    f"a matcher missing from that list ({ABSENTS}) shows as a labeled blank"
    if ABSENTS else
    "Each matcher the tool ships with appears in our test set, and if one were ever missing "
    "it would show as a "
    "labeled blank")

PAGE = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra Screening &#183; live instrument</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra Screening: the live instrument">
<meta property="og:description" content="Matcher by matcher and threshold by threshold, on our public test set: what each one catches, what it flags incorrectly, and where it cannot say.">
<meta property="og:url" content="{SITE_URL}screening/instrument.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="Matcher by matcher and threshold by threshold, on our public test set: what each one catches, what it flags incorrectly, and where it cannot say.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%23180b0f'/%3E%3Cpath d='M16 0v16H0z' fill='%237a1f2e'/%3E%3C/svg%3E">
<link rel="stylesheet" href="../fontes/literata.css">
<link rel="stylesheet" href="../fontes/roboto-mono.css">
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_NOIR}{CSS_BARRE_SITE}</style>
{barre_site(courant=OUTILS["screening"]["page_hero"], racine="../")}

<section class="tete">
  <div class="colonne">
    <h1 class="h1">See what each way of comparing names costs you, live.</h1>
    <p class="lede">A threshold is the score above which two names count as a match. The figures
      here come from <b>our public test set</b>: name pairs an AI agent wrote for this repository,
      including near-matches that look similar but are different people. Nothing on this page comes from a
      customer, and the figures are recomputed as the page loads.</p>
  </div>
</section>

<section class="poste" data-commun="instrument">
  <div class="colonne">
    <div class="dessus">
      <div class="t-page-halo" aria-hidden="true"></div>
      <div class="poste-grille">
      <div class="fen-robot">
      <div class="terminal">
        <div class="tm-barre"><i></i><i></i><i></i><span>crusetra screening &#183; our public test set, live</span></div>
        <div class="tm-corps">
          <p class="tm-l"><span class="ps">$</span> crusetra screen --live<span class="caret" aria-hidden="true"></span></p>
          <div class="regls" role="group" aria-label="Which half of the record">
            <button class="regl actif" id="m-auth">written pairs</button>
            <button class="regl" id="m-synth">generated pairs</button>
          </div>
          <p class="tm-sortie" id="g-quoi"></p>
          {carte_html("threshold", "recall", "matcher")}
          {table_html()}
          <p class="tm-sortie" id="g-lecture" data-commun="instrument">pick a cell: what it catches over what it flags incorrectly, with the number of pairs and the interval</p>

          <p class="tm-l"><span class="ps">$</span> crusetra optimise --recall</p>
          <div class="b-ligne">
            <span class="b-val" id="b-val"></span>
            <div class="b-curseur"><input type="range" id="b-curseur" min="0.50" max="1.00" step="0.01"
              aria-label="Required floor, held at the low end of the interval"></div>
          </div>
          <p class="tm-sortie b-lecture" id="b-lecture"></p>

          <p class="tm-l" style="margin-top:14px"><span class="ps">$</span> crusetra verify --sealed</p>
          <p class="tm-preuve" id="tm-preuve">checking&#8230;</p>
        </div>
      </div>
      </div>
      <div class="pan-col">
      <img class="rb" src="../rendus/robot-rubis-regarde.webp" alt="">
      {PANNEAU_HTML}
      </div>
      </div>
    </div>
  </div>
</section>

<section class="basse" data-commun="instrument">
  <div class="colonne basse-grille">
    <div class="plis">
      <details class="pli"><summary>What this rests on, for your IT auditor</summary>
    <ul>
      <li><b>Our public test set.</b> releve-public.json in the repository, with a content hash (a checksum) of
        <b>{D["provenance"]["empreinte"]}</b>, measured at commit <b>{D["provenance"]["commit"]}</b>
        on {D["provenance"]["date"]}. The script that builds it checks that hash, rebuilds every
        figure with the tool&#8217;s own code, and publishes nothing if one of them
        disagrees.</li>
      <li><b>The written pairs.</b> The labeled half was written for this repository by an AI agent
        (commit 474ffbd): true matches, where the same name is transliterated, reordered, abbreviated
        or mistyped, and near-matches, which are siblings and partial homonyms that are not the same
        person. Where a label is debatable, the reason is written beside it.</li>
      <li><b>The generated half.</b> Generated from list-entry names, one kind of change at a
        time, and counted on their own, because a generated one is not as hard: the toggle
        above switches the whole grid.</li>
      <li data-commun="instrument"><b>How the tool picks.</b> The slider sets the share of true matches you want
        caught. A setting counts only if the low end of its confidence interval clears that share, because a rate measured on few cases can flatter. The tool then takes the setting with the fewest false alerts.</li>
    </ul>
      </details>
      <details class="pli"><summary>What this page cannot do</summary>
    <ul>
      <li><b>Your data.</b> This page cannot read it: no network request leaves it
        (the browser&#8217;s own security rules forbid them), nothing is loaded from elsewhere, and there is no input
        field to paste a name into.</li>
      <li><b>It cannot show a rate without the number of pairs behind it.</b> Each cell carries that number and its 95% confidence interval. {PHRASE_ABSENTS}.</li>
    </ul>
      </details>
    </div>
    <aside class="clone-col">
    <h2>Test your own names, on the next page</h2>
    <p>The page above shows our own measurement. The next one runs the same code on names you paste, in your browser:
      nothing is sent anywhere.</p>
    <span class="clone-t">What the self-serve test covers</span>
    <div class="clone" role="group" aria-label="What the self-serve test covers">
      <div><span class="ps">$</span> crusetra screen --names your-list.csv</div>
      <div class="note">the companies and vessels of {EN_LETTRES[N_ESSAI_LISTES]} of the tool&#8217;s {EN_LETTRES[N_ESSAI_OUTIL]} lists, as of {ESSAI_DATE};
        individuals are not covered; a candidate is a name to check</div>
    </div>
    <div class="ouvrir-ligne"><a class="ouvrir" href="ESSAI-SCREENING.html">Try it on your names <span class="fl" aria-hidden="true">&#8594;</span></a>
      <a class="ouvrir tarif" href="../ENGAGEMENT.html">See pricing <span class="fl" aria-hidden="true">&#8594;</span></a></div>
    </aside>
  </div>
</section>

{pied_html(outil=OUTILS["screening"], sceau=D["provenance"]["empreinte"], tests=n_tests(OUTILS["screening"]))}

<script type="application/json" id="donnees">{json.dumps(D)}</script>
<script>{JS}</script>
'''

# le cadratin est interdit sur le site : la garde de l'assembleur le refuse, on se
# l'applique avant lui (l'entite &#8212; du pied est volontairement REMPLACEE ici)
PAGE = PAGE.replace("&#8212;", "&#183;")
if "—" in PAGE:
    sys.exit("un cadratin s'est glisse dans la page : la garde du site le refusera.")

(BASE / "INSTRUMENT-SCREENING.html").write_text(PAGE, encoding="utf-8")
print(f"INSTRUMENT-SCREENING.html {len(PAGE) / 1e3:.0f} ko")
