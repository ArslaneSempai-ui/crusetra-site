"""THE LIVE CHART of the instrument pages that carry a matcher x threshold grid (screening,
monitoring, scoring). Chosen by Arslane on 9/09/2026 from a board of directions (« B3, une seule
carte », the animated one): the whole page in black, the tool's colour only in strokes and glows;
one chart, one curve per tier over a LINEAR threshold axis, the recall of each shown cell as a
point; ONE floor line you drag across the chart (the slider stays for the keyboard and follows);
what holds the floor at the Wilson LOWER BOUND lights up green and the held zone is tinted; the
hovered cell draws its interval and is read in a fixed side panel; the other half of the record
(authored / synthetic) stays as a dotted ghost when you switch. The grid table stays in the DOM,
painted by the same figures, for keyboard users and readers without a pointer.

The three builders are line-for-line copies of each other; this module holds what they share so
the chart is written once. Each figure comes from the tool's JSON; nothing is typed here."""

# ── the black page : overrides appended after each builder's own CSS ─────────────────────────
CSS_NOIR = '''
  /* THE BLACK PAGE (Arslane, 9/09) : the tool's night becomes near-black, its colour stays in
     strokes, figures and glows ; the parchment section turns black with paper ink, the clone
     terminal too. The variables are re-declared so each rule below inherits the change. */
  :root{--nuit-a:#1a1a1f;--nuit-b:#0e0e11;--nuit-c:#08080a;
    --papier:#0e0e11;--papier-haut:#121215;--encre:#e8e6df;--demi:#a5a39a;--pale:#8f8d84;
    --filet-clair:#2c2c33;--sur:#e8e6df;--sur-pale:#9a988f;--tenu:#7fd4a0}
  .tete{background:radial-gradient(120% 100% at 50% -20%,color-mix(in srgb,var(--accent-titre) 38%,#0e0e11),var(--nuit-b) 70%)}
  /* the lede : one wide line or two, never a three-line block (Arslane : « un bloc moche ») */
  .lede{max-width:none;text-wrap:pretty}
  .terminal{background:linear-gradient(180deg,#131316,#0b0b0d 120px);
    border-color:color-mix(in srgb,var(--accent-vif) 26%,transparent)}
  .terminal::after{background:none}
  .tm-barre{background:linear-gradient(180deg,#17171b,#101013)}
  .basse{border-top:1px solid #1e1e23}
  .basse li::before{background:var(--accent-vif)}
  .clone{background:linear-gradient(163deg,#141417,#0e0e11);box-shadow:none}
  .pied{border-top:1px solid #1e1e23}
  /* the robot keeps leaning over the RIGHT edge of the window, left of the panel's column
     (on the left it sat on the title and the lede, seen on the 9/09 capture) */
  /* the robot leans over the RIGHT edge of the window and is CUT by it (z below the terminal),
     looking down at the chart (pose « regarde », Arslane 9/09 : « faut que le robot regarde
     l'outil et qu'il soit crop correctement avec les bords de l'outil ») */
  .fen-robot{position:relative}
  /* over the window's right edge the robot sat on the title (the panel took the width) : it
     leans over the PANEL's card, at the far right, and looks left, at the chart */
  .pan-col{position:relative}
  /* 10/09 : le panneau descend d'un cran pour une visibilité entière, le robot descend avec lui
     (pose « regarde », la tête tournée vers la carte à sa gauche) */
  @media (min-width:981px){.pan{margin-top:120px}}
  .rb{right:-24px;left:auto;width:340px;top:-150px;z-index:2;
    filter:drop-shadow(0 26px 44px rgba(0,0,0,.85)) brightness(.92)}
  @media (max-width:980px){.rb{display:none}}
  /* as wide as the robot allows (three lines at 1440), never the old 52ch block */
  .lede{max-width:min(100%,800px);font-size:clamp(15px,1.15vw,16.5px)}

  /* THE LIVE CHART : the window becomes window + side panel ; the table stays for the keyboard */
  .dessus{width:min(100%,1180px)}
  /* minmax(0,1fr) : a long unbreakable line (the vert's routing line) must not widen the column
     (bench of the 9/09 : +394 px at 320 on the vert and the onyx) */
  .poste-grille{display:grid;grid-template-columns:minmax(0,1fr) 272px;gap:22px;align-items:start}
  @media (max-width:980px){.poste-grille{grid-template-columns:minmax(0,1fr)}.pan{position:static}}
  .tm-sortie,.tm-l,.tm-preuve,.carte-aide,.lect{overflow-wrap:anywhere}
  html.js .t-scroll{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  .carte{display:block;width:100%;height:auto;font-family:var(--mono);touch-action:none;
    user-select:none;-webkit-user-select:none;cursor:crosshair;margin:2px 0 10px}
  .carte .grille-h{stroke:#1c1c21;stroke-width:1}
  .carte .ordonnee{fill:var(--sur-pale);font-size:10px;text-anchor:end}
  .carte .seuil{fill:var(--sur-pale);font-size:10.5px;text-anchor:middle}
  .carte .seuil.axe{fill:var(--accent-clair)}
  .carte .zone-tenue{fill:var(--tenu);opacity:.06}
  .carte .courbe{fill:none;stroke:#3a3a42;stroke-width:1.4}
  .carte .courbe.axe{stroke:var(--sur);stroke-width:2}
  .carte .fantome{fill:none;stroke:var(--accent-vif);stroke-width:1;stroke-dasharray:3 3;opacity:.55}
  .carte .fantome-pt{fill:none;stroke:var(--accent-vif);stroke-width:1;opacity:.55}
  .carte .pt circle{fill:var(--nuit-c);stroke:#4a4a52;stroke-width:1.5}
  .carte .pt text{fill:var(--sur-pale);font-size:10.5px;text-anchor:middle}
  .carte .pt.tenu circle{fill:var(--tenu);stroke:var(--tenu)}
  .carte .pt.axe circle{stroke:var(--sur)} .carte .pt.axe text{fill:var(--sur)}
  .carte .pt.vise circle{fill:var(--accent-vif);stroke:var(--accent-clair);stroke-width:2}
  .carte .pt.vise text{fill:var(--accent-clair);font-size:13px;font-weight:500}
  .carte .pt.presse circle{stroke:var(--accent-clair);stroke-width:2.5}
  .carte .choix circle{fill:none;stroke:var(--accent-vif);stroke-width:2.5}
  .carte .choix text{fill:var(--accent-clair);font-size:10.5px;text-anchor:middle}
  .carte .intervalle{stroke:var(--accent-clair);stroke-width:2;opacity:.9}
  .carte .viseur{stroke:var(--accent-vif);stroke-width:1;opacity:.7}
  .carte .plancher-l{stroke:var(--accent-clair);stroke-width:1.5;cursor:ns-resize}
  .carte .plancher-prise{fill:transparent;cursor:ns-resize}
  .carte .plancher-poignee{fill:var(--nuit-c);stroke:var(--accent-clair);stroke-width:2;cursor:ns-resize}
  .carte .plancher-t{fill:var(--accent-clair);font-size:11px;text-anchor:end}
  .carte .legende text{font-size:11px;fill:var(--sur-pale)} .carte .legende text.axe{fill:var(--sur)}
  .carte .legende text.fantome-t{fill:var(--accent-vif);opacity:.8}
  /* under 700 px the chart keeps a readable width and scrolls sideways, as the grid did */
  .carte-boite{overflow-x:auto;margin:0 -6px;padding:0 6px}
  @media (max-width:700px){.carte{min-width:640px}}
  .carte-aide{font-family:var(--mono);font-size:11.5px;color:var(--sur-pale);margin:0 0 12px}
  .carte-aide b{color:var(--tenu);font-weight:500}

  .pan{position:sticky;top:20px;z-index:3;border:1px solid #232328;border-left:2px solid var(--accent-vif);
    border-radius:10px;background:#101013;padding:16px 18px 18px;font-family:var(--mono);min-height:300px}
  .pan .qui{font-size:11px;color:var(--sur-pale);letter-spacing:.08em;text-transform:uppercase}
  .pan .nom{font-family:var(--texte);font-size:23px;margin:6px 0 14px;color:var(--sur);line-height:1.15}
  .pan .nom small{color:var(--sur-pale);font-size:14px}
  .pan .gros{font-size:34px;line-height:1;color:var(--sur);margin:2px 0 4px}
  .pan .gros small{font-size:14px;color:var(--sur-pale)}
  .pan .leg{font-size:11.5px;color:var(--sur-pale);margin-bottom:14px;line-height:1.5}
  .pan .plancher{font-size:12px;padding-top:12px;border-top:1px solid #2c2c33;line-height:1.6;color:var(--sur-pale)}
  .pan .plancher b{color:var(--accent-clair);font-size:19px;font-weight:500}
  .pan .tenu{color:var(--tenu)} .pan .pas{color:var(--accent-clair)}
  @media (prefers-reduced-motion:reduce){.caret{animation:none}}

  /* LE BAS DE PAGE (Arslane, 10/09 : « le terminal en couleur à droite, sur toutes les couleurs ;
     la partie droite est trop vide, c'est un long scroll ; les trucs en liste ouvrable ») : deux
     colonnes, les listes deviennent des plis qui s'ouvrent au clic, le terminal des trois
     commandes tient la colonne de droite, collant, dans la couleur de l'outil */
  .basse-grille,.reserves-grille{display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:56px;align-items:start}
  @media (max-width:980px){.basse-grille,.reserves-grille{grid-template-columns:minmax(0,1fr)}}
  .plis{border-top:1px solid #232328}
  .pli{border-bottom:1px solid #232328}
  .pli summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:baseline;gap:16px;
    padding:20px 0;font-family:var(--texte);font-size:clamp(20px,2vw,26px);font-weight:600;letter-spacing:-.012em;color:var(--encre)}
  .pli summary::-webkit-details-marker{display:none}
  .pli summary::after{content:"+";font-family:var(--mono);font-size:22px;font-weight:400;color:var(--accent-vif);flex:none}
  .pli[open] summary::after{content:"−"}
  .pli summary:hover{color:var(--accent-clair)}
  .pli ul,.pli p{margin:0 0 22px}
  .clone-col{position:sticky;top:24px}
  .clone-col h2{margin:0 0 12px}
  .clone-col p{margin:0 0 18px}
  .clone-col .clone-t{margin-top:0}
  .basse .clone,.reserves .term{max-width:none;border-color:color-mix(in srgb,var(--accent-vif) 60%,transparent);
    background:linear-gradient(163deg,color-mix(in srgb,var(--accent-titre) 60%,#0e0e11),color-mix(in srgb,var(--accent-titre) 22%,#0e0e11));
    box-shadow:0 30px 70px rgba(0,0,0,.55),inset 0 1px 0 color-mix(in srgb,var(--accent-clair) 20%,transparent)}
  .basse .clone .ps,.reserves .term-corps .cmd::before{color:var(--accent-clair)}
  .basse .clone .note,.reserves .term-corps .sortie{color:color-mix(in srgb,var(--accent-clair) 70%,var(--sur-pale))}
  .reserves .term-bar{background:color-mix(in srgb,var(--accent-vif) 22%,transparent)}
  .reserves .ouvrir-ligne{justify-content:flex-start;margin-top:22px}
  /* sous les trois commandes : l'action, puis l'étape logique suivante, les tarifs (Arslane, 10/09) */
  .clone-col .ouvrir-ligne{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}
  .clone-col .ouvrir{display:inline-flex;align-items:baseline;gap:10px;font-family:var(--texte);font-weight:600;font-size:15px;
    padding:10px 18px;border:1px solid;border-radius:8px;text-decoration:none;transition:background .2s,color .2s}
  .clone-col .ouvrir.tarif{opacity:.85}
'''


def carte_html(x_titre, y_titre, rangee="setting"):
    """The chart and its side panel, empty : the JS draws both from the embedded record."""
    return f'''<p class="carte-aide" data-commun="instrument">each point is one {rangee} at one threshold, from our public test set. <b>Pull the floor line</b> or the slider, and the {rangee}s that stay above it, confidence interval included, turn green</p>
          <div class="carte-boite"><svg class="carte" id="carte" viewBox="0 0 900 400" role="img" aria-label="{y_titre} of each row at each {x_titre} of our public test set, with the floor as a line"></svg></div>'''


PANNEAU_HTML = '''<aside class="pan" id="pan" aria-live="polite">
        <div class="qui">the cell under the pointer</div>
        <div class="nom" id="pan-nom">hover a point</div>
        <div class="gros" id="pan-g1"></div><div class="leg" id="pan-l1"></div>
        <div class="gros" id="pan-g2"></div><div class="leg" id="pan-l2"></div>
        <div class="plancher" id="pan-plancher"></div>
      </aside>'''


def js_carte(mot_x, mot_y, mot_fp):
    """The drawing and the hand. `mot_x` names the axis (threshold), `mot_y` the first figure
    (recall), `mot_fp` the second (false alerts), in the tool's own words."""
    return '''
  /* THE LIVE CHART : one curve per tier over a linear ''' + mot_x + ''' axis, the floor as a line you drag. */
  const carte = $("#carte");
  const NS = "http://www.w3.org/2000/svg";
  const CW = 900, CH = 400, CL = 56, CR = 118, CT = 22, CB = 34;
  const XMIN = Math.min(...D.seuilsMontres), XMAX = Math.max(...D.seuilsMontres);
  const cx = (s) => CL + (s - XMIN) / (XMAX - XMIN) * (CW - CL - CR);
  const cy = (t) => (CH - CB) - t * (CH - CB - CT);
  const pcv = (x) => { const s = (x * 100).toFixed(1); return s.endsWith(".0") ? s.slice(0, -2) : s; };
  let vise = null;                       // {p, s} under the pointer, or the pressed cell
  let plancher = D.recommandee.plancher; // the floor, shared with the slider
  const autre = () => (moitie === "authored" ? "synthetic" : "authored");
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function dessiner() {
    const g = D[moitie].grille, g2 = D[autre()].grille;
    const presse = cells.find((x) => x.getAttribute("aria-pressed") === "true");
    const cible = vise || (presse ? { p: presse.dataset.p, s: presse.dataset.s } : null);
    let h = "";
    for (const v of [0, .25, .5, .75, 1]) h += '<line class="grille-h" x1="' + CL + '" x2="' + (CW - CR) + '" y1="' + cy(v) + '" y2="' + cy(v) + '"/><text class="ordonnee" x="' + (CL - 8) + '" y="' + (cy(v) + 4) + '">' + Math.round(v * 100) + '</text>';
    h += '<rect class="zone-tenue" x="' + CL + '" y="' + CT + '" width="' + (CW - CL - CR) + '" height="' + Math.max(0, cy(plancher) - CT) + '"/>';
    for (const [p, ligne] of Object.entries(g2)) {
      h += '<polyline class="fantome" points="' + MONTRES.map((s) => cx(+s) + "," + cy(ligne[s].rappel.taux)).join(" ") + '"/>';
      for (const s of MONTRES) h += '<circle class="fantome-pt" cx="' + cx(+s) + '" cy="' + cy(ligne[s].rappel.taux) + '" r="2.5"/>';
    }
    for (const [p, ligne] of Object.entries(g)) {
      const axe = cible && cible.p === p;
      h += '<polyline class="courbe' + (axe ? " axe" : "") + '" points="' + MONTRES.map((s) => cx(+s) + "," + cy(ligne[s].rappel.taux)).join(" ") + '"/>';
    }
    /* the labels of the hovered COLUMN sit left of their point and are pushed apart when two
       curves cross the column at the same height (48.3 over 46.7 on the 9/09 capture) */
    const colonne = [];
    if (cible) {
      for (const [p, ligne] of Object.entries(g)) if (p !== cible.p) colonne.push([cy(ligne[cible.s].rappel.taux), p]);
      colonne.sort((a, b) => a[0] - b[0]);
      let dernier = -99;
      for (const e of colonne) { e[2] = Math.max(e[0], dernier + 12); dernier = e[2]; }
      const depasse = dernier - (CH - CB - 6);          /* zeros stacked under the axis : slide up */
      if (depasse > 0) for (const e of colonne) e[2] -= depasse;
    }
    const yLabel = Object.fromEntries(colonne.map(([y0, p, y]) => [p, y]));
    for (const [p, ligne] of Object.entries(g)) {
      for (const s of MONTRES) {
        const c = ligne[s], t = c.rappel.taux, x = cx(+s), y = cy(t);
        const estVise = cible && cible.p === p && cible.s === s;
        const axe = cible && (cible.p === p || cible.s === s);
        let k = "pt" + (estVise ? " vise" : axe ? " axe" : "") + (c.rappel.bas >= plancher ? " tenu" : "");
        if (presse && presse.dataset.p === p && presse.dataset.s === s) k += " presse";
        let label = "";
        if (estVise || (cible && cible.p === p)) label = '<text x="' + x + '" y="' + (y - 9) + '">' + pcv(t) + '</text>';
        else if (axe) label = '<text x="' + (x - 8) + '" y="' + (yLabel[p] + 4) + '" style="text-anchor:end">' + pcv(t) + '</text>';
        h += '<g class="' + k + '" data-p="' + esc(p) + '" data-s="' + s + '"><circle cx="' + x + '" cy="' + y + '" r="' + (estVise ? 5 : 3) + '"/>' + label + '</g>';
        if (estVise) h += '<line class="intervalle" x1="' + x + '" x2="' + x + '" y1="' + cy(c.rappel.haut) + '" y2="' + cy(c.rappel.bas) + '"/>';
      }
    }
    /* the tool's own pick at this floor, on the authored half and all 51 thresholds : a ring at its true ''' + mot_x + ''' */
    const choix = retenir(plancher);
    if (choix && moitie === "authored" && choix.seuil >= XMIN && choix.seuil <= XMAX) {
      h += '<g class="choix"><circle cx="' + cx(choix.seuil) + '" cy="' + cy(choix.rappel.taux) + '" r="8"/><text x="' + (cx(choix.seuil) + 13) + '" y="' + (cy(choix.rappel.taux) + 4) + '" style="text-anchor:start">the tool\\u2019s pick \\u00b7 ' + esc(choix.palier) + " at " + choix.seuil.toFixed(2) + '</text></g>';
    }
    if (cible) h += '<line class="viseur" x1="' + cx(+cible.s) + '" x2="' + cx(+cible.s) + '" y1="' + CT + '" y2="' + (CH - CB) + '"/>';
    const yf = cy(plancher);
    h += '<rect class="plancher-prise" x="' + CL + '" y="' + (yf - 9) + '" width="' + (CW - CL - CR) + '" height="18"/>'
       + '<line class="plancher-l" x1="' + CL + '" x2="' + (CW - CR) + '" y1="' + yf + '" y2="' + yf + '"/>'
       + '<rect class="plancher-poignee" x="' + (CW - CR - 7) + '" y="' + (yf - 7) + '" width="14" height="14" rx="3"/>'
       + '<text class="plancher-t" x="' + (CW - CR - 12) + '" y="' + (yf - 6) + '">floor ' + plancher.toFixed(2) + '</text>';
    for (const s of MONTRES) h += '<text class="seuil' + (cible && cible.s === s ? " axe" : "") + '" x="' + cx(+s) + '" y="' + (CH - 8) + '">' + s + '</text>';
    /* the names at the right end of their curve, pushed apart when curves end on the same value */
    const fins = Object.entries(g).map(([p, ligne]) => [cy(ligne[MONTRES[MONTRES.length - 1]].rappel.taux), p]).sort((a, b) => a[0] - b[0]);
    let dernier = -99; const ys = [];
    for (const [y0, p] of fins) { const y = Math.max(y0, dernier + 13); dernier = y; ys.push(y); }
    /* curves that end at zero pushed the stack under the axis (monitoring, 9/09) : it slides back up */
    const depasse = dernier - (CH - CB - 4);
    fins.forEach(([y0, p], i) => {
      const y = ys[i] - Math.max(0, depasse);
      h += '<g class="legende"><text x="' + (CW - CR + 8) + '" y="' + (y + 4) + '" class="' + (cible && cible.p === p ? "axe" : "") + '">' + esc(p) + '</text></g>';
    });
    h += '<g class="legende"><text class="fantome-t" x="' + (CW - CR + 8) + '" y="' + (CT + 8) + '">dotted: ' + autre() + '</text></g>';
    carte.innerHTML = h;
  }

  function peindrePanneau() {
    const presse = cells.find((x) => x.getAttribute("aria-pressed") === "true");
    const cible = vise || (presse ? { p: presse.dataset.p, s: presse.dataset.s } : null);
    if (!cible) { $("#pan-nom").textContent = "hover a point"; ["#pan-g1", "#pan-l1", "#pan-g2", "#pan-l2"].forEach((id) => { $(id).textContent = ""; }); }
    else {
      const c = D[moitie].grille[cible.p][cible.s];
      $("#pan-nom").innerHTML = esc(cible.p) + " <small>at " + cible.s + "</small>";
      $("#pan-g1").innerHTML = pcv(c.rappel.taux) + "<small>%</small>";
      $("#pan-l1").textContent = "''' + mot_y + ''', interval " + iv(c.rappel) + ", " + c.rappel.succes + " of " + c.rappel.n;
      $("#pan-g2").innerHTML = pcv(c.fauxPositifs.taux) + "<small>%</small>";
      $("#pan-l2").textContent = "''' + mot_fp + ''', interval " + iv(c.fauxPositifs) + ", " + c.fauxPositifs.succes + " of " + c.fauxPositifs.n;
    }
    const tenues = MONTRES.reduce((n, s) => n + Object.values(D[moitie].grille).filter((l) => l[s].rappel.bas >= plancher).length, 0);
    const total = Object.keys(D[moitie].grille).length * MONTRES.length;
    const c = cible ? D[moitie].grille[cible.p][cible.s] : null;
    $("#pan-plancher").innerHTML = "floor <b>" + plancher.toFixed(2) + "</b> \\u00b7 " + tenues + " of " + total + " shown cells hold the lower bound"
      + (c ? " \\u00b7 this one <span class=\\"" + (c.rappel.bas >= plancher ? "tenu" : "pas") + "\\">" + (c.rappel.bas >= plancher ? "holds" : "does not hold") + "</span> (" + Math.round(c.rappel.bas * 100) + " %)" : "");
  }

  /* the hand : hover the nearest point of the column, click to keep it, pull the floor */
  const pointDe = (ev) => {
    const r = carte.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width * CW, y = (ev.clientY - r.top) / r.height * CH;
    let best = null, d0 = 1e9;
    for (const [p, ligne] of Object.entries(D[moitie].grille)) for (const s of MONTRES) {
      const d = Math.hypot(cx(+s) - x, cy(ligne[s].rappel.taux) - y);
      if (d < d0) { d0 = d; best = { p, s }; }
    }
    return d0 < 28 ? best : null;
  };
  let tire = false;
  carte.addEventListener("pointerdown", (ev) => {
    const r = carte.getBoundingClientRect();
    const y = (ev.clientY - r.top) / r.height * CH;
    if (Math.abs(y - cy(plancher)) < 12 || ev.target.classList.contains("plancher-poignee")) { tire = true; carte.setPointerCapture(ev.pointerId); ev.preventDefault(); }
  });
  carte.addEventListener("pointermove", (ev) => {
    if (tire) {
      const r = carte.getBoundingClientRect();
      const y = (ev.clientY - r.top) / r.height * CH;
      const v = Math.min(1, Math.max(0.5, ((CH - CB) - y) / (CH - CB - CT)));
      plancher = Math.round(v * 100) / 100; curseur.value = plancher; rejouer(); return;
    }
    const pt = pointDe(ev);
    if ((pt && (!vise || pt.p !== vise.p || pt.s !== vise.s)) || (!pt && vise)) { vise = pt; dessiner(); peindrePanneau(); }
  });
  carte.addEventListener("pointerup", () => { tire = false; });
  carte.addEventListener("pointerleave", () => { if (!tire) { vise = null; dessiner(); peindrePanneau(); } });
  carte.addEventListener("click", (ev) => {
    if (tire) return;
    const pt = pointDe(ev);
    if (!pt) return;
    const c = cells.find((x) => x.dataset.p === pt.p && x.dataset.s === pt.s);
    if (c) lire(c);
  });
'''


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE TWO INSTRUMENTS WITHOUT A THRESHOLD GRID, same language (Arslane, 9/09 : « oui, les deux
# comme ça ») : one chart, one line you drag, what holds lights up, a side panel reads the thing
# under the pointer.
#   VERT : each routing of the fields over the tiers (7^5 = 16 807, the ones optimise
#          enumerates) as a cloud of cost x accuracy, the best trade-off drawn, the BUDGET a vertical
#          line you drag ; the best routing under it lights up and the panel names it field by
#          field ; hovering a frontier point reads its routing, clicking it composes it.
#   ONYX : the questions' seals on a time axis (days since measured), the declared VALIDITY
#          vertical line you drag (a what-if, said as such) ; a seal past it would lose « fresh »
#          and the --next lines say so ; the panel reads the five sealed verdicts of the
#          question under the pointer.
# ═══════════════════════════════════════════════════════════════════════════════════════════

CSS_VERT = '''
  /* the vert names its colours differently : aliased so the shared chart rules apply */
  :root{--accent-titre:var(--vert-titre);--accent-vif:var(--vert-vif);--accent-clair:var(--vert-clair);
    --sur-vert:#e8e6df;--sur-vert-pale:#9a988f;--sur:#e8e6df;--sur-pale:#9a988f}
  .reserves{background:var(--nuit-b);color:var(--sur-vert);border-top:1px solid #1e1e23}
  .reserves p{color:var(--sur-vert-pale)} .reserves b,.reserves code{color:var(--sur-vert)}
  .vos-t{color:var(--vert-vif)}
  .term{background:linear-gradient(163deg,#141417,#0e0e11);box-shadow:none}
  .ouvrir{color:var(--vert-clair);border-color:color-mix(in srgb,var(--vert-vif) 55%,transparent)}
  .ouvrir:hover{background:var(--vert-vif);color:var(--nuit-c);border-color:var(--vert-vif)}
  .pan .plancher b{font-size:12.5px}          /* the field → tier list, not a big figure */
  .carte .nuage circle{fill:#26262c}
  .carte .front{fill:none;stroke:#6a6a72;stroke-width:1.2}
  .carte .pt-front circle{fill:var(--nuit-c);stroke:#8a8a92;stroke-width:1.2}
  .carte .pt-front.tenu circle{fill:var(--tenu);stroke:var(--tenu)}
  .carte .pt-front.vise circle{fill:var(--accent-vif);stroke:var(--accent-clair);stroke-width:2}
  .carte .repere circle{fill:none;stroke:var(--accent-clair);stroke-width:1.5;stroke-dasharray:2 2}
  .carte .repere text{fill:var(--sur-pale);font-size:10.5px}
  .carte .choix-t{fill:var(--accent-clair);font-size:11px}
  .carte .ligne-l{stroke:var(--accent-clair);stroke-width:1.5;cursor:ew-resize}
  .carte .ligne-prise{fill:transparent;cursor:ew-resize}
  .carte .ligne-poignee{fill:var(--nuit-c);stroke:var(--accent-clair);stroke-width:2;cursor:ew-resize}
  .carte .ligne-t{fill:var(--accent-clair);font-size:11px;text-anchor:middle}
  .carte .abscisse{fill:var(--sur-pale);font-size:10.5px;text-anchor:middle}
'''

CSS_ONYX = '''
  .carte .piste{stroke:#232328;stroke-width:1}
  .carte .nomq{fill:var(--sur-pale);font-size:12px} .carte .nomq.axe{fill:var(--accent-clair)}
  .carte .pierre circle{fill:var(--nuit-c);stroke:var(--sur);stroke-width:2}
  .carte .pierre.tenu circle{fill:var(--tenu);stroke:var(--tenu)}
  .carte .pierre.pas circle{fill:var(--nuit-c);stroke:var(--accent-clair);stroke-width:2;stroke-dasharray:3 2}
  .carte .pierre text{fill:var(--sur);font-size:10.5px;text-anchor:middle}
  .carte .pierre.vise circle{stroke:var(--accent-clair);stroke-width:3.5}
  .carte .rythme{stroke:#2c2c33;stroke-width:1;stroke-dasharray:2 4}
  .carte .abscisse{fill:var(--sur-pale);font-size:10.5px;text-anchor:middle}
  .carte .ligne-l{stroke:var(--accent-clair);stroke-width:1.5;cursor:ew-resize}
  .carte .ligne-prise{fill:transparent;cursor:ew-resize}
  .carte .ligne-poignee{fill:var(--nuit-c);stroke:var(--accent-clair);stroke-width:2;cursor:ew-resize}
  .carte .ligne-t{fill:var(--accent-clair);font-size:11px;text-anchor:middle}
  .pan .verdicts{font-size:12px;line-height:1.7;color:var(--sur-pale);padding-top:12px;border-top:1px solid #2c2c33}
  .pan .verdicts b{color:var(--sur);font-weight:500}
'''

CARTE_VERT_HTML = '''<p class="carte-aide" data-commun="instrument">each dot is one routing of the five fields, priced and scored from our frozen readings. The line through the bright dots is the best trade-off no routing beats · <b>pull the budget line</b> (or the slider below), the best routing under it lights up · hover a frontier dot to read it, click it to compose it</p>
          <div class="carte-boite"><svg class="carte" id="carte" viewBox="0 0 900 400" role="img" aria-label="Each routing as cost against accuracy, the best trade-off, and the budget as a line"><g id="carte-nuage"></g><g id="carte-vif"></g></svg></div>'''

PANNEAU_VERT_HTML = '''<aside class="pan" id="pan" aria-live="polite">
        <div class="qui">the routing under the pointer</div>
        <div class="nom" id="pan-nom"></div>
        <div class="gros" id="pan-g1"></div><div class="leg" id="pan-l1"></div>
        <div class="gros" id="pan-g2"></div><div class="leg" id="pan-l2"></div>
        <div class="plancher" id="pan-plancher"></div>
      </aside>'''

CARTE_ONYX_HTML = '''<p class="carte-aide" data-commun="instrument">each dot is one question from our public test set, placed at its age in days · <b>pull the validity line</b> to ask what a shorter or longer validity period would change : a dot past it would lose its « fresh » control, and the --next lines state it · hover a dot to read its five verdicts</p>
          <div class="carte-boite"><svg class="carte" id="carte" viewBox="0 0 900 300" role="img" aria-label="The questions' seals on a time axis, with the declared validity period as a line"></svg></div>'''

PANNEAU_ONYX_HTML = '''<aside class="pan" id="pan" aria-live="polite">
        <div class="qui">the question under the pointer</div>
        <div class="nom" id="pan-nom">hover a stone</div>
        <div class="gros" id="pan-g1"></div><div class="leg" id="pan-l1"></div>
        <div class="verdicts" id="pan-verdicts"></div>
      </aside>'''


JS_VERT = '''
  /* THE LIVE CHART OF THE VERT : the cloud of routings, the best trade-off, the budget line you drag. */
  const carte = $("#carte"), nuageG = $("#carte-nuage"), vifG = $("#carte-vif");
  const CW = 900, CH = 400, CL = 56, CR = 30, CT = 26, CB = 34;
  const xl = (cout) => CL + Math.log10(Math.max(cout * 100, 1)) / 5 * (CW - CL - CR);   /* $ per 100k, log 1..100k */
  const yl = (just) => (CH - CB) - just / 100 * (CH - CB - CT);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  let viseV = null;                          /* the best trade-off point under the pointer */
  const budgetDe = () => Math.pow(10, parseFloat(curseur.value)) / 100;
  /* the cloud, drawn ONCE : each routing, thinned to one in three (the eye cannot tell) */
  (() => {
    let h = ""; let i = 0;
    const marche = (k, r, cout, just) => {
      if (k === F.length) { if (i++ % 3 === 0) h += '<circle cx="' + xl(cout).toFixed(0) + '" cy="' + yl(just / F.length).toFixed(0) + '" r="1.2"/>'; return; }
      for (const t of T) marche(k + 1, r, cout + D.price[t][F[k]], just + D.acc[t][F[k]]);
    };
    marche(0, {}, 0, 0);
    nuageG.innerHTML = '<g class="nuage">' + h + "</g>";
  })();
  const memeR = (a, b) => F.every((f) => a[f] === b[f]);
  function dessinerV() {
    const budget = budgetDe();
    let h = "";
    for (const v of [0, 25, 50, 75, 100]) h += '<line class="grille-h" x1="' + CL + '" x2="' + (CW - CR) + '" y1="' + yl(v) + '" y2="' + yl(v) + '"/><text class="ordonnee" x="' + (CL - 8) + '" y="' + (yl(v) + 4) + '">' + v + '</text>';
    ["$1", "$10", "$100", "$1k", "$10k", "$100k"].forEach((lab, k) => { h += '<text class="abscisse" x="' + (CL + k / 5 * (CW - CL - CR)).toFixed(0) + '" y="' + (CH - 8) + '">' + lab + '</text>'; });
    h += '<rect class="zone-tenue" x="' + CL + '" y="' + CT + '" width="' + Math.max(0, xl(budget) - CL).toFixed(0) + '" height="' + (CH - CB - CT) + '"/>';
    h += '<polyline class="front" points="' + frontiere.map((p) => xl(p.cout).toFixed(0) + "," + yl(p.just).toFixed(0)).join(" ") + '"/>';
    let best = null;
    for (const p of frontiere) { if (p.cout <= budget) best = p; else break; }
    for (const p of frontiere) {
      const k = "pt-front" + (p.cout <= budget ? " tenu" : "") + (viseV === p ? " vise" : "");
      h += '<g class="' + k + '"><circle cx="' + xl(p.cout).toFixed(0) + '" cy="' + yl(p.just).toFixed(0) + '" r="' + (viseV === p ? 5 : 3.2) + '"/></g>';
    }
    const pub = lire(D.publie.routage), vis = lire(D.vise.routage);
    for (const [c, nom] of [[pub, "published \\u00b7 " + fmtC(pub.cout)], [vis, "file-aimed \\u00b7 " + fmtC(vis.cout)]]) {
      h += '<g class="repere"><circle cx="' + xl(c.cout).toFixed(0) + '" cy="' + yl(c.just).toFixed(0) + '" r="7"/><text x="' + (xl(c.cout) + 11).toFixed(0) + '" y="' + (yl(c.just) + 16).toFixed(0) + '">' + nom + '</text></g>';
    }
    /* the routing composed right now (the grid, the chips, or the budget) : a ring */
    const cur = lire(routage);
    h += '<g class="choix"><circle cx="' + xl(cur.cout).toFixed(0) + '" cy="' + yl(cur.just).toFixed(0) + '" r="9"/><text class="choix-t" x="' + (xl(cur.cout) + 13).toFixed(0) + '" y="' + (yl(cur.just) - 8).toFixed(0) + '">your routing \\u00b7 ' + cur.just.toFixed(1) + " % at " + fmtC(cur.cout) + '</text></g>';
    const xb = xl(budget);
    h += '<rect class="ligne-prise" x="' + (xb - 9).toFixed(0) + '" y="' + CT + '" width="18" height="' + (CH - CB - CT) + '"/>'
       + '<line class="ligne-l" x1="' + xb.toFixed(0) + '" x2="' + xb.toFixed(0) + '" y1="' + CT + '" y2="' + (CH - CB) + '"/>'
       + '<rect class="ligne-poignee" x="' + (xb - 7).toFixed(0) + '" y="' + (CT - 8) + '" width="14" height="14" rx="3"/>'
       + '<text class="ligne-t" x="' + xb.toFixed(0) + '" y="' + (CT - 12) + '">budget ' + fmtC(budget) + ' /100k docs</text>';
    vifG.innerHTML = h;
  }
  function peindrePanneauV() {
    const p = viseV || { r: routage, ...lire(routage) };
    const pub = lire(D.publie.routage);
    $("#pan-nom").innerHTML = viseV ? "a frontier routing" : (memeR(routage, D.publie.routage) ? "the published routing" : memeR(routage, D.vise.routage) ? "the file-aimed routing" : "your routing");
    $("#pan-g1").innerHTML = p.just.toFixed(1) + "<small>%</small>";
    $("#pan-l1").textContent = "per-field mean accuracy, no interval (the tool\\u2019s own figure)";
    $("#pan-g2").textContent = fmtC(p.cout);
    $("#pan-l2").textContent = "per 100 000 documents, assumed prices";
    const dj = p.just - pub.just, dc = (p.cout - pub.cout) * 100;
    $("#pan-plancher").innerHTML = F.map((f) => esc(f) + " \\u2192 <b>" + esc(p.r[f]) + "</b>").join("<br>")
      + "<br><span class=\\"" + (memeR(p.r, D.publie.routage) ? "tenu" : "pas") + "\\">" + (memeR(p.r, D.publie.routage) ? "this is the published routing" : "vs published " + (dj >= 0 ? "+" : "\\u2212") + Math.abs(dj).toFixed(1) + " pt, " + (dc >= 0 ? "+" : "\\u2212") + "$" + Math.abs(dc).toFixed(0)) + "</span>";
  }
  const pointV = (ev) => {
    const r = carte.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width * CW, y = (ev.clientY - r.top) / r.height * CH;
    let best = null, d0 = 1e9;
    for (const p of frontiere) { const d = Math.hypot(xl(p.cout) - x, yl(p.just) - y); if (d < d0) { d0 = d; best = p; } }
    return d0 < 24 ? best : null;
  };
  let tireV = false;
  carte.addEventListener("pointerdown", (ev) => {
    const r = carte.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width * CW;
    if (Math.abs(x - xl(budgetDe())) < 12 || ev.target.classList.contains("ligne-poignee")) { tireV = true; try { carte.setPointerCapture(ev.pointerId); } catch (e) {} ev.preventDefault(); }
  });
  carte.addEventListener("pointermove", (ev) => {
    if (tireV) {
      const r = carte.getBoundingClientRect();
      const x = (ev.clientX - r.left) / r.width * CW;
      const v = Math.min(5, Math.max(0, (x - CL) / (CW - CL - CR) * 5));
      curseur.value = v.toFixed(2); curseur.dispatchEvent(new Event("input")); return;
    }
    const p = pointV(ev);
    if (p !== viseV) { viseV = p; dessinerV(); peindrePanneauV(); }
  });
  carte.addEventListener("pointerup", () => { tireV = false; });
  carte.addEventListener("pointerleave", () => { if (!tireV) { viseV = null; dessinerV(); peindrePanneauV(); } });
  carte.addEventListener("click", (ev) => { if (tireV) return; const p = pointV(ev); if (p) { routage = { ...p.r }; peindre(); } });
'''

JS_ONYX = '''
  /* THE LIVE CHART OF THE ONYX : the seals on the clock, the validity period line you drag (a what-if). */
  const carte = $("#carte");
  const CW = 900, CH = 300, CL = 100, CR = 40, CT = 30, CB = 34, XMAX = 180;
  const noms = Object.keys(D.questions).filter((q) => D.questions[q].present);
  const HR = (CH - CT - CB) / Math.max(1, noms.length);
  const xd = (d) => CL + Math.min(d, XMAX) / XMAX * (CW - CL - CR);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  let rythme = D.reglages.rythmeJours, viseQ = null;
  const frais = (q) => D.questions[q].joursDepuis <= rythme;
  function dessinerO() {
    let h = '<rect class="zone-tenue" x="' + CL + '" y="' + CT + '" width="' + (xd(rythme) - CL).toFixed(0) + '" height="' + (CH - CT - CB) + '"/>';
    for (let k = 0; k <= XMAX; k += 30) h += '<text class="abscisse" x="' + xd(k).toFixed(0) + '" y="' + (CH - 8) + '">' + k + ' d</text><line class="rythme" x1="' + xd(k).toFixed(0) + '" x2="' + xd(k).toFixed(0) + '" y1="' + CT + '" y2="' + (CH - CB) + '"/>';
    noms.forEach((q, i) => {
      const y = CT + (i + .5) * HR, d = D.questions[q].joursDepuis;
      h += '<text class="nomq' + (q === viseQ ? " axe" : "") + '" x="0" y="' + (y + 4).toFixed(0) + '">' + esc(q) + '</text><line class="piste" x1="' + CL + '" x2="' + (CW - CR) + '" y1="' + y.toFixed(0) + '" y2="' + y.toFixed(0) + '"/>';
      h += '<g class="pierre ' + (frais(q) ? "tenu" : "pas") + (q === viseQ ? " vise" : "") + '"><circle cx="' + xd(d).toFixed(0) + '" cy="' + y.toFixed(0) + '" r="7"/><text x="' + xd(d).toFixed(0) + '" y="' + (y - 13).toFixed(0) + '">' + d + ' d \\u00b7 ' + esc(D.questions[q].etat) + '</text></g>';
    });
    const xs = xd(rythme);
    h += '<rect class="ligne-prise" x="' + (xs - 9).toFixed(0) + '" y="' + CT + '" width="18" height="' + (CH - CT - CB) + '"/>'
       + '<line class="ligne-l" x1="' + xs.toFixed(0) + '" x2="' + xs.toFixed(0) + '" y1="' + CT + '" y2="' + (CH - CB) + '"/>'
       + '<rect class="ligne-poignee" x="' + (xs - 7).toFixed(0) + '" y="' + (CT - 8) + '" width="14" height="14" rx="3"/>'
       + '<text class="ligne-t" x="' + xs.toFixed(0) + '" y="' + (CT - 12) + '">' + (rythme === D.reglages.rythmeJours ? "declared validity period " + rythme + " days" : "if the validity period were " + rythme + " days (declared: " + D.reglages.rythmeJours + ")") + '</text>';
    carte.innerHTML = h;
  }
  function peindrePanneauO() {
    if (!viseQ) { $("#pan-nom").textContent = "hover a stone"; $("#pan-g1").textContent = ""; $("#pan-l1").textContent = ""; $("#pan-verdicts").innerHTML = "<b>" + noms.filter(frais).length + "</b> of " + noms.length + " fresh within " + rythme + " days" + (rythme === D.reglages.rythmeJours ? "" : " (what-if : the sealed verdicts below keep the declared validity period)"); return; }
    const d = D.questions[viseQ];
    $("#pan-nom").innerHTML = esc(viseQ) + " <small>" + esc(d.etat) + "</small>";
    $("#pan-g1").innerHTML = d.joursDepuis + "<small> days</small>";
    $("#pan-l1").textContent = "since its record was measured \\u00b7 seal " + String(d.sceau).slice(0, 8) + "\\u2026 \\u00b7 " + String(d.fichier).slice(0, 36);
    $("#pan-verdicts").innerHTML = (d.verdicts || []).map((v) => esc(v.controle) + " <b class=\\"" + (v.tenu ? "tenu" : "pas") + "\\">" + (v.tenu ? "held" : "not held") + "</b>").join("<br>")
      + "<br><span class=\\"" + (frais(viseQ) ? "tenu" : "pas") + "\\">" + (frais(viseQ) ? "fresh within " + rythme + " days" : "would fall out of a " + rythme + "-day validity period") + "</span>";
  }
  function suivantesO() {
    const lignes = [];
    for (const [q, d] of Object.entries(D.questions)) {
      if (!d.present) { lignes.push("<b>" + esc(q) + "</b>: no sealed public record yet \\u00b7 nothing judged"); continue; }
      const tenu = Object.fromEntries((d.verdicts || []).map((v) => [v.controle, v.tenu]));
      const suivant = ORDRE.find((c) => !(c in tenu) || !tenu[c]);
      const jours = typeof d.joursDepuis === "number" ? " \\u00b7 measured " + d.joursDepuis + " day(s) ago" : "";
      const echeance = typeof d.joursDepuis === "number" ? (d.joursDepuis <= rythme ? " \\u00b7 due in " + (rythme - d.joursDepuis) + " day(s)" : " \\u00b7 <b>past a " + rythme + "-day validity period</b>") : "";
      if (suivant === undefined) lignes.push("<b>" + esc(q) + "</b>: each control held" + jours + echeance);
      else { const v = verdictDe(q, suivant); lignes.push("<b>" + esc(q) + "</b>: state reached <b>" + esc(d.etat) + "</b>" + jours + " \\u00b7 next, <b>" + esc(suivant) + "</b>: " + (v ? esc(v.detail) : "not judged by the record")); }
    }
    $("#g-suivant").innerHTML = lignes.join("<br>") + (rythme === D.reglages.rythmeJours ? "" : "<br><span class=\\"tm-l\\">what-if at " + rythme + " days ; the dossier's declared validity period is " + D.reglages.rythmeJours + "</span>");
  }
  const pierreDe = (ev) => {
    const r = carte.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width * CW, y = (ev.clientY - r.top) / r.height * CH;
    let best = null, d0 = 1e9;
    noms.forEach((q, i) => { const d = Math.hypot(xd(D.questions[q].joursDepuis) - x, CT + (i + .5) * HR - y); if (d < d0) { d0 = d; best = q; } });
    return d0 < 22 ? best : null;
  };
  let tireO = false;
  carte.addEventListener("pointerdown", (ev) => {
    const r = carte.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width * CW;
    if (Math.abs(x - xd(rythme)) < 12 || ev.target.classList.contains("ligne-poignee")) { tireO = true; try { carte.setPointerCapture(ev.pointerId); } catch (e) {} ev.preventDefault(); }
  });
  carte.addEventListener("pointermove", (ev) => {
    if (tireO) {
      const r = carte.getBoundingClientRect();
      const x = (ev.clientX - r.left) / r.width * CW;
      rythme = Math.round(Math.min(XMAX, Math.max(1, (x - CL) / (CW - CL - CR) * XMAX)));
      dessinerO(); peindrePanneauO(); suivantesO(); return;
    }
    const q = pierreDe(ev);
    if (q !== viseQ) { viseQ = q; dessinerO(); peindrePanneauO(); }
  });
  carte.addEventListener("pointerup", () => { tireO = false; });
  carte.addEventListener("pointerleave", () => { if (!tireO) { viseQ = null; dessinerO(); peindrePanneauO(); } });
  carte.addEventListener("dblclick", () => { rythme = D.reglages.rythmeJours; dessinerO(); peindrePanneauO(); suivantesO(); });
  carte.addEventListener("click", (ev) => { if (tireO) return; const q = pierreDe(ev); if (!q) return; const cel = cells.find((x) => x.dataset.q === q && x.dataset.c === "fresh") || cells.find((x) => x.dataset.q === q); if (cel) lire(cel); });
  dessinerO(); peindrePanneauO(); suivantesO();
'''


# ═══════════════════════════════════════════════════════════════════════════════════════════
# L'AFFICHE DE L'INSTRUMENT sur les héros (Arslane, 10/09 : « la liste en bloc est imposante
# mais ne sert pas à grand-chose ; notre outil est plus beau que son affiche »). La grille
# palier × seuil quitte le héros ; à sa place, une affiche qui ressemble à l'outil : la même
# carte que l'instrument, STATIQUE, dessinée par Python depuis le relevé scellé (aucun chiffre
# tapé), le robot de la couleur penché sur son bord, le bouton « Open the live instrument » en
# valeur. Les nombres exacts restent sur l'instrument ; l'affiche donne la forme.
# ═══════════════════════════════════════════════════════════════════════════════════════════

CSS_AFFICHE = '''
  .affiche-tarif{display:inline-block;margin-top:16px;font-family:var(--mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;
    color:var(--sur-vert-pale);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--sur-vert-pale) 40%,transparent);padding:6px 0 4px}   /* 29 px de haut : la cible faisait 23 (ergonomie.mjs, 13/09) */
  .affiche-tarif:hover{color:var(--vert-clair);border-color:var(--vert-clair)}
  .instrument .h2{max-width:22ch}     /* le titre reste à gauche du robot qui penche sur l'affiche */
  .affiche-col{position:relative;margin-top:36px}
  .affiche-robot{position:absolute;right:26px;top:-206px;width:300px;height:auto;z-index:1;pointer-events:none;
    filter:drop-shadow(0 26px 44px rgba(0,0,0,.7)) brightness(.94)}
  .affiche{position:relative;z-index:2;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(280px,.85fr);
    gap:36px;align-items:end;padding:30px 36px 34px;border-radius:18px;text-decoration:none;color:var(--sur-vert);
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 72%,var(--nuit-b)),var(--nuit-b));
    border:1px solid color-mix(in srgb,var(--vert-vif) 42%,transparent);
    box-shadow:0 40px 100px rgba(0,0,0,.55);transition:transform .4s var(--montee),border-color .3s,box-shadow .4s var(--montee)}
  .affiche:hover,.affiche:focus-visible{transform:translateY(-3px);border-color:color-mix(in srgb,var(--vert-vif) 75%,transparent);
    box-shadow:0 50px 120px color-mix(in srgb,var(--vert-vif) 16%,transparent)}
  .affiche-carte{min-width:0}
  .affiche-carte svg{display:block;width:100%;height:auto;font-family:var(--mono)}
  .affiche-carte .ax{fill:var(--sur-vert-pale);font-size:10.5px}
  .affiche-carte .gr{stroke:color-mix(in srgb,var(--sur-vert) 10%,transparent);stroke-width:1}
  .affiche-carte .cb{fill:none;stroke:color-mix(in srgb,var(--sur-vert) 32%,transparent);stroke-width:1.3}
  .affiche-carte .cb.fort{stroke:var(--sur-vert);stroke-width:2}
  .affiche-carte .pt{fill:var(--nuit-c);stroke:color-mix(in srgb,var(--sur-vert) 45%,transparent);stroke-width:1.2}
  .affiche-carte .pt.fort{fill:var(--vert-vif);stroke:var(--vert-clair);stroke-width:2}
  .affiche-carte .anneau{fill:none;stroke:var(--vert-vif);stroke-width:2.5}
  .affiche-carte .ligne{stroke:var(--vert-clair);stroke-width:1.5}
  .affiche-carte .zone{fill:var(--vert-vif);opacity:.07}
  .affiche-carte .eti{fill:var(--vert-clair);font-size:11px}
  .affiche-carte .nom{fill:var(--sur-vert-pale);font-size:11px}
  .affiche-carte .nom.fort{fill:var(--sur-vert)}
  .affiche-carte .pierre{fill:var(--vert-vif);stroke:var(--vert-clair);stroke-width:2}
  .affiche-col .t-note{margin:18px 4px 0;max-width:none}   /* toute la largeur de l'affiche, jamais un bloc à gauche (Arslane, 13/09) */
  .affiche-texte{display:flex;flex-direction:column;align-items:flex-start;gap:8px}
  .affiche-texte .ouvrir-t{font-size:clamp(24px,2.6vw,36px)}
  /* LE BOUTON DE L'AFFICHE (Arslane, 10/09 : « juste la flèche c'est trop simple » ; 13/09 : un
     rectangle, animé, et rien d'autre ne bouge sur l'affiche). Une touche sombre, à la place
     exacte du rond fléché (même marge, même alignement) ; un filet de lumière qui fait le tour de
     son bord en continu, parce que l'instrument est vivant avant qu'on le touche ; le libellé et
     la flèche. Au survol le bord s'allume en entier, l'intérieur se teinte, la flèche glisse ; à
     l'appui la touche s'enfonce. Mouvement réduit : le filet ne tourne pas, le bord reste posé.
     26 + 60 = 14 + 72 : la touche occupe la hauteur exacte du rond, l'affiche garde ses 356 px.
     Le filet : un carré en dégradé conique (::before) qui tourne sous une plaque sombre (::after)
     posée à 1 px du bord : seul l'anneau de 1 px laisse passer la lumière. Transform seul :
     rien ne refait la mise en page. Le bouton est aria-hidden : l'affiche entière est le lien. */
  .affiche-texte .bt{position:relative;isolation:isolate;overflow:hidden;margin:26px 0 0;align-self:flex-start;
    display:inline-flex;align-items:center;justify-content:space-between;gap:22px;min-width:236px;height:60px;
    padding:0 20px 0 22px;border-radius:10px;font-family:var(--mono);font-size:11.5px;letter-spacing:.2em;
    text-transform:uppercase;white-space:nowrap;color:var(--vert-clair);
    background:color-mix(in srgb,var(--vert-vif) 34%,transparent);
    box-shadow:0 1px 0 rgba(0,0,0,.55),0 14px 30px rgba(0,0,0,.35);
    transition:transform .3s var(--montee),color .3s,background .3s,box-shadow .3s var(--montee)}
  .affiche-texte .bt::before{content:"";position:absolute;left:50%;top:50%;width:620px;height:620px;z-index:-2;
    transform:translate(-50%,-50%) rotate(0deg);
    background:conic-gradient(from 0deg,transparent 0 62%,color-mix(in srgb,var(--vert-clair) 55%,transparent) 84%,var(--vert-clair) 96%,transparent 100%)}
  .affiche-texte .bt::after{content:"";position:absolute;inset:1px;z-index:-1;border-radius:9px;
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 60%,var(--nuit-c)),var(--nuit-c));
    box-shadow:inset 0 1px 0 color-mix(in srgb,var(--sur-vert) 9%,transparent);transition:background .3s}
  .affiche-texte .bt-f{font-family:var(--sans);font-size:20px;line-height:1;letter-spacing:0;transition:transform .35s var(--montee)}
  @media (prefers-reduced-motion:no-preference){
    .affiche-texte .bt::before{animation:bt-tour 3.6s linear infinite}
    @keyframes bt-tour{to{transform:translate(-50%,-50%) rotate(360deg)}}}
  .affiche:hover .bt,.affiche:focus-visible .bt{color:var(--sur-vert);background:var(--vert-vif);transform:translateY(-1px);
    box-shadow:0 2px 0 rgba(0,0,0,.55),0 18px 40px color-mix(in srgb,var(--vert-vif) 28%,transparent)}
  .affiche:hover .bt::before,.affiche:focus-visible .bt::before{animation-play-state:paused;opacity:0}
  .affiche:hover .bt::after,.affiche:focus-visible .bt::after{background:linear-gradient(180deg,color-mix(in srgb,var(--vert-vif) 22%,var(--nuit-b)),color-mix(in srgb,var(--vert-vif) 12%,var(--nuit-c)))}
  .affiche:hover .bt-f,.affiche:focus-visible .bt-f{transform:translateX(6px)}
  .affiche:active .bt{transform:translateY(1px);box-shadow:0 0 0 rgba(0,0,0,.55),0 6px 16px rgba(0,0,0,.35);transition-duration:.08s}
  @media (max-width:980px){.affiche{grid-template-columns:minmax(0,1fr)}.affiche-robot{display:none}}
'''


def _svg_courbes(releve, findings):
    """Les courbes rappel × seuil des paliers présents, lues dans le relevé scellé ; la cellule
    de la frontière (finding 03, source.a) en anneau quand elle existe."""
    seuils = ["0.50", "0.60", "0.70", "0.80", "0.85", "0.90", "0.95", "1.00"]
    tables = releve["authored"]["tables"]
    paliers = [p for p in releve["paliers"]["presents"] if p in tables]
    src = (findings[2].get("source", {}) or {}).get("a") or {} if len(findings) > 2 else {}
    W, H, L, R, T, B = 720, 300, 40, 90, 18, 28
    x = lambda s: L + (float(s) - 0.5) / 0.5 * (W - L - R)
    y = lambda t: (H - B) - t * (H - B - T)
    fort = src.get("palier")
    out = ""
    for v in (0, .5, 1):
        out += f'<line class="gr" x1="{L}" x2="{W - R}" y1="{y(v):.0f}" y2="{y(v):.0f}"/><text class="ax" x="{L - 6}" y="{y(v) + 4:.0f}" text-anchor="end">{int(v * 100)}</text>'
    for p in paliers:
        pts = " ".join(f"{x(s):.0f},{y(tables[p][s]['rappel']['taux']):.0f}" for s in seuils if s in tables[p])
        out += f'<polyline class="cb{" fort" if p == fort else ""}" points="{pts}"/>'
    for p in paliers:
        for s in seuils:
            if s in tables[p]:
                out += f'<circle class="pt{" fort" if p == fort else ""}" cx="{x(s):.0f}" cy="{y(tables[p][s]["rappel"]["taux"]):.0f}" r="{3.2 if p == fort else 2.4}"/>'
    for s in seuils:
        out += f'<text class="ax" x="{x(s):.0f}" y="{H - 8}" text-anchor="middle">{s}</text>'
    fins = sorted((y(tables[p]["1.00"]["rappel"]["taux"]), p) for p in paliers if "1.00" in tables[p])
    d = -99
    for y0, p in fins:
        yy = max(y0, d + 12); d = yy
        out += f'<text class="nom{" fort" if p == fort else ""}" x="{W - R + 8}" y="{yy + 4:.0f}">{p}</text>'
    if fort and src.get("seuil") is not None:
        s = f"{float(src['seuil']):.2f}"
        if s in tables.get(fort, {}):
            out += f'<circle class="anneau" cx="{x(s):.0f}" cy="{y(tables[fort][s]["rappel"]["taux"]):.0f}" r="8"/>'
            out += f'<text class="eti" x="{x(s) + 12:.0f}" y="{y(tables[fort][s]["rappel"]["taux"]) - 10:.0f}">the tool’s pick · {fort} at {s}</text>'
    return f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">{out}</svg>'


def _svg_paliers(landing):
    """Le vert : une courbe par champ sur l'axe des paliers (dans l'ordre du relevé), la
    justesse en ordonnée, le palier publié de chaque champ en anneau. Aucun prix : le
    landing ne les porte pas par champ, l'instrument les calcule."""
    F, tiers = list(landing["fields"]), [t["id"] for t in landing["tiers"]]
    pub = landing["routing"]["fields"]
    # T à 36, pas 18 : à 18 l'étiquette « the published routing… » (posée 4 px au-dessus du tracé)
    # traversait l'anneau de la première colonne, dont le rayon monte à 8 px au-dessus de 100
    # (vu par la relecture du 8/09). Le tracé commence 18 px plus bas ; la boîte ne change pas.
    W, H, L, R, T, B = 720, 300, 40, 20, 36, 28
    x = lambda i: L + i / max(1, len(tiers) - 1) * (W - L - R)
    y = lambda v: (H - B) - v / 100 * (H - B - T)
    out = ""
    for v in (0, 50, 100):
        out += f'<line class="gr" x1="{L}" x2="{W - R}" y1="{y(v):.0f}" y2="{y(v):.0f}"/><text class="ax" x="{L - 6}" y="{y(v) + 4:.0f}" text-anchor="end">{v}</text>'
    acc = {t["id"]: t["acc"] for t in landing["tiers"]}
    for f in F:
        pts = " ".join(f"{x(i):.0f},{y(acc[t][f]['accuracy']):.0f}" for i, t in enumerate(tiers) if acc[t][f].get("accuracy") is not None)
        out += f'<polyline class="cb" points="{pts}"/>'
    for f in F:
        for i, t in enumerate(tiers):
            a = acc[t][f].get("accuracy")
            if a is None:
                continue
            k = "pt fort" if pub.get(f) == t else "pt"
            out += f'<circle class="{k}" cx="{x(i):.0f}" cy="{y(a):.0f}" r="{4 if pub.get(f) == t else 2.4}"/>'
            if pub.get(f) == t:
                out += f'<circle class="anneau" cx="{x(i):.0f}" cy="{y(a):.0f}" r="8"/>'
    for i, t in enumerate(tiers):
        out += f'<text class="ax" x="{x(i):.0f}" y="{H - 8}" text-anchor="middle">{t}</text>'
    out += f'<text class="eti" x="{L}" y="{T - 20}">the published routing, one ring per field · {landing["routing"]["accuracy"]} % mean accuracy</text>'
    return f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">{out}</svg>'


def _svg_horloge(releve):
    """L'onyx : les sceaux des questions sur l'axe des jours, la ligne du rythme déclaré."""
    Q = {q: d for q, d in (releve.get("questions") or {}).items() if d.get("present")}
    rythme = (releve.get("reglages") or {}).get("rythmeJours", 90)
    W, H, L, R, T, B = 720, 300, 100, 30, 26, 28
    XMAX = 180
    x = lambda d: L + min(d, XMAX) / XMAX * (W - L - R)
    noms = list(Q)
    HR = (H - T - B) / max(1, len(noms))
    out = f'<rect class="zone" x="{L}" y="{T}" width="{x(rythme) - L:.0f}" height="{H - T - B}"/>'
    for k in range(0, XMAX + 1, 30):
        out += f'<text class="ax" x="{x(k):.0f}" y="{H - 8}" text-anchor="middle">{k} d</text><line class="gr" x1="{x(k):.0f}" x2="{x(k):.0f}" y1="{T}" y2="{H - B}"/>'
    for i, q in enumerate(noms):
        yy = T + (i + .5) * HR; d = Q[q].get("joursDepuis", 0)
        out += f'<text class="nom" x="0" y="{yy + 4:.0f}">{q}</text><line class="gr" x1="{L}" x2="{W - R}" y1="{yy:.0f}" y2="{yy:.0f}"/>'
        out += f'<circle class="pierre" cx="{x(d):.0f}" cy="{yy:.0f}" r="7"/><text class="ax" x="{x(d):.0f}" y="{yy - 12:.0f}" text-anchor="middle">{d} d · {Q[q].get("etat", "")}</text>'
    out += f'<line class="ligne" x1="{x(rythme):.0f}" x2="{x(rythme):.0f}" y1="{T}" y2="{H - B}"/><text class="eti" x="{x(rythme):.0f}" y="{T - 8}" text-anchor="middle">declared validity period {rythme} days</text>'
    return f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">{out}</svg>'


def affiche_html(sorte, donnees, findings, page, eti, sous, robot, note="", tarif=""):
    """L'affiche : la carte statique de l'outil (sorte : courbes | paliers | horloge), le robot
    de la couleur penché sur son bord, le bouton en valeur. `robot` est le chemin de l'image."""
    svg = {"courbes": lambda: _svg_courbes(donnees, findings),
           "paliers": lambda: _svg_paliers(donnees),
           "horloge": lambda: _svg_horloge(donnees)}[sorte]()
    return f'''<div class="affiche-col">
    <img class="affiche-robot" src="{robot}" alt="">
    <a class="affiche" href="{page}">
      <div class="affiche-carte">{svg}</div>
      <div class="affiche-texte"><span class="ouvrir-eti">{eti}</span><span class="ouvrir-t">Open the live instrument</span>
        <span class="ouvrir-s">{sous}</span><span class="bt" aria-hidden="true"><span class="bt-l">Open the instrument</span><span class="bt-f">&#8594;</span></span></div>
    </a>
    {f'<a class="affiche-tarif" href="{tarif}">See pricing <span aria-hidden="true">&#8594;</span></a>' if tarif else ""}
    {f'<p class="t-note">{note}</p>' if note else ""}
  </div>'''


# ═══════════════════════════════════════════════════════════════════════════════════════════
# L'ACCUEIL (Arslane, 10/09) : noir comme les instruments ; au premier écran, à droite de la
# première ligne, les cinq cartes des instruments EN ÉVENTAIL (les vraies courbes du relevé,
# statiques : le langage des affiches) ; survoler une carte la sort du paquet, cliquer ouvre
# l'outil ; après le rideau, UNE figure de la méthode + le terminal des trois commandes + les
# annexes en une ligne ; deux robots, positionnés avec Arslane.
# ═══════════════════════════════════════════════════════════════════════════════════════════

CSS_ACCUEIL = '''
  /* la page de la marque en noir : les nuits de la maison deviennent le noir des instruments */
  :root{--nuit-a:#1a1a1f;--nuit-b:#0e0e11;--nuit-c:#08080a;--sur-vert:#e8e6df;--sur-vert-pale:#9a988f;
    --papier:#0e0e11;--papier-haut:#121215;--encre:#e8e6df;--demi:#a5a39a;--pale:#8f8d84;--filet-clair:#2c2c33}
  body{background:var(--nuit-b)}
  .hero{background:radial-gradient(120% 90% at 30% -10%,color-mix(in srgb,var(--vert-titre) 34%,#0e0e11),var(--nuit-b) 65%);
    min-height:auto;padding:150px 0 80px}
  /* la grille du premier écran, SYMÉTRIQUE (Arslane, 10/09) : deux colonnes de largeur connue, centrées
     ensemble, un gouffre entre elles plus large que tout espace interne ; les marges extérieures se valent */
  /* 25/10: the fan column keeps 38vw (up to 520px) of its own; with a bare 0 minimum the wide text column took 700px
     and the fanned cards ran 43 to 75px past the screen at 1150 and 1280 (verif-final, sonde-site.mjs) */
  .hero-grille{display:grid;grid-template-columns:minmax(480px,700px) minmax(min(520px,38vw),540px);gap:clamp(48px,7.4vw,106px);
    align-items:start;justify-content:center;max-width:none;margin:0 auto;padding:0 65px 0 48px;position:relative;text-align:left}
  /* LE GRAND LIVRE (Arslane, 10/09, D1) : un titre court, six lignes libellé / valeur au poids des
     grilles des cartes, la commande en dernière ; le bloc pend du haut de l'éventail (le panel des
     cinq regards : un bloc centré à côté d'un objet est le héros de gabarit) */
  .hero-grille .h1{text-align:left;margin:0;max-width:none;font-size:clamp(46px,4.9vw,72px);line-height:1;letter-spacing:-.025em}
  /* the poster title (Arslane, 25/10): two giant lines, the answer in green */
  .hero-grille .h1 em{font-style:normal;color:var(--vert-vif)}
  /* le titre monte (Arslane, 08/09). Mesuré avant de bouger : la barre finit à 77, l'éventail
     commence à 96, et le titre tombait à 168 parce que la colonne de texte s'enfonçait de 72.
     À 36, il se pose à 132 : trente-six pixels plus haut, toujours quarante-cinq sous la
     barre, et il reste plus bas que le haut de l'éventail, qui garde la main. */
  .hero-texte{padding-top:36px}
  /* le sous-titre (relecture du 8/09, rouvert par Arslane le 13/09 : le lede revient sous le titre) :
     aligné à gauche comme le grand livre, 44 caractères de large, une couleur en retrait */
  .hero-grille .lede{margin:16px 0 0;max-width:62ch;font-size:20px;line-height:1.45;color:var(--sur-vert-pale);text-align:left;text-wrap:pretty}
  .ledger{margin:26px 0 0}
  .ledger div{display:flex;justify-content:space-between;align-items:baseline;gap:16px;min-height:38px;padding:9px 0;
    border-bottom:1px solid color-mix(in srgb,var(--sur-vert) 10%,transparent)}
  .ledger div:first-child{border-top:1px solid color-mix(in srgb,var(--sur-vert) 10%,transparent)}
  .ledger dt{font-family:var(--mono);font-size:12px;color:var(--sur-vert-pale);letter-spacing:.02em}
  .ledger .pt{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;background:var(--vert-vif)}
  .ledger dd{margin:0;font-family:var(--mono);font-size:13px;color:var(--sur-vert);font-variant-numeric:tabular-nums;white-space:nowrap;text-align:right}
  .ledger .cmd{flex-wrap:wrap;row-gap:4px}
  .ledger .cmd .c1::before{content:"$ ";color:var(--sur-vert-pale)}
  .ledger .cmd .c2{flex-basis:100%;font-family:var(--mono);font-size:11px;color:var(--sur-vert-pale);overflow-wrap:anywhere}
  .ledger .cmd .c2::before{content:"$ "}
  @media (max-width:560px){.ledger div{flex-wrap:wrap}.ledger dd{white-space:normal;text-align:left;overflow-wrap:anywhere}}
  .hero{min-height:0;padding:96px 24px 64px}
  .hero-texte{position:relative;z-index:2}

  /* l'éventail : cinq cartes empilées, chacune dans SES couleurs, la survolée sort du paquet */
  .eventail{position:relative;height:min(480px,34vw);perspective:1600px}
  .carte-ev{position:absolute;left:50%;top:calc(50% - 20px);width:min(420px,30vw);aspect-ratio:1.5/1;margin:0;
    display:block;border-radius:14px;overflow:hidden;text-decoration:none;color:var(--sur-vert);
    background:linear-gradient(180deg,color-mix(in srgb,var(--ev-nuit-a) 80%,#000),color-mix(in srgb,var(--ev-nuit-c) 92%,#000));
    border:1px solid color-mix(in srgb,var(--ev-vif) 45%,transparent);
    box-shadow:0 30px 70px rgba(0,0,0,.6),inset 0 1px 0 color-mix(in srgb,var(--ev-vif) 25%,transparent);
    transform:translate(calc(var(--dx) - 50%),calc(var(--dy) - 50%)) rotate(var(--rot));transform-origin:50% 120%;
    transition:transform .5s var(--montee),box-shadow .5s var(--montee),border-color .3s;z-index:var(--z)}
  .carte-ev:hover,.carte-ev:focus-visible{transform:translate(calc(var(--dx) - 50%),calc(var(--dy) - 50% - 36px)) rotate(0deg) scale(1.04);
    z-index:10;border-color:var(--ev-vif);box-shadow:0 50px 110px rgba(0,0,0,.7),0 0 0 1px var(--ev-vif)}
  .carte-ev .ev-svg{padding:14px 16px 4px}
  .carte-ev svg{display:block;width:100%;height:auto;font-family:var(--mono)}
  .carte-ev .ax{fill:var(--sur-vert-pale);font-size:11px}
  .carte-ev .gr{stroke:color-mix(in srgb,var(--sur-vert) 10%,transparent);stroke-width:1}
  .carte-ev .cb{fill:none;stroke:color-mix(in srgb,var(--sur-vert) 30%,transparent);stroke-width:1.3}
  .carte-ev .cb.fort{stroke:var(--sur-vert);stroke-width:2}
  .carte-ev .pt{fill:var(--nuit-c);stroke:color-mix(in srgb,var(--sur-vert) 45%,transparent);stroke-width:1.2}
  .carte-ev .pt.fort{fill:var(--ev-vif);stroke:var(--ev-clair);stroke-width:2}
  .carte-ev .anneau{fill:none;stroke:var(--ev-vif);stroke-width:2.5}
  .carte-ev .ligne{stroke:var(--ev-clair);stroke-width:1.5}
  .carte-ev .zone{fill:var(--ev-vif);opacity:.08}
  .carte-ev .eti{fill:var(--ev-clair);font-size:11.5px}
  .carte-ev .nom{fill:var(--sur-vert-pale);font-size:11px} .carte-ev .nom.fort{fill:var(--sur-vert)}
  .carte-ev .pierre{fill:var(--ev-vif);stroke:var(--ev-clair);stroke-width:2}
  .carte-ev .ev-pied{display:flex;justify-content:space-between;align-items:baseline;padding:6px 16px 14px;
    font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ev-vif)}
  .carte-ev .ev-pied b{font-weight:500;color:var(--sur-vert);letter-spacing:.06em;text-transform:none;font-size:12.5px;white-space:nowrap}
  @media (max-width:1100px){.hero-grille{grid-template-columns:minmax(0,1fr);padding:0 8px}.hero-texte{padding-top:0}.eventail{height:auto;padding:24px 0}
    .carte-ev{position:relative;left:auto;top:auto;margin:0 0 14px;width:100%;transform:none;aspect-ratio:auto}
    .carte-ev:hover{transform:none}.carte-ev .ev-pied{flex-wrap:wrap;gap:6px 14px}.carte-ev .ev-pied b{white-space:nowrap;margin-left:auto}}

  /* LA MÉTHODE SUR PAPIER (Arslane, 10/09 : « dans notre style, pas tout noir ») : le rail des quatre
     stations à gauche, comme le rail des findings des pages outils ; à droite le gros plan du dossier
     avec ses étiquettes publiées sur le crème ; les trois commandes vivent dans la station 03. */
  .methode{padding:96px 0 84px;background:var(--papier);color:var(--encre);position:relative;
    border-top:3px double var(--encre)}
  .methode .h2{color:var(--encre);max-width:22ch}
  .methode-grille{display:grid;grid-template-columns:minmax(300px,.9fr) minmax(0,1.1fr);gap:56px;align-items:start;margin-top:40px}
  .stations{margin:0;padding:0;list-style:none;border-left:2px solid var(--filet-clair)}
  .stations li{position:relative;padding:18px 0 22px 26px;display:flex;flex-direction:column;gap:8px}
  .stations li::before{content:"";position:absolute;left:-7px;top:26px;width:12px;height:12px;border-radius:50%;
    background:var(--papier);border:2px solid var(--vert-titre)}
  .stations li:first-child::before{background:var(--vert-vif);border-color:var(--vert-vif)}
  .stations .num{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--vert-titre)}
  .stations h3{margin:0;font-size:19px;font-weight:600;color:var(--encre);line-height:1.18;letter-spacing:-.01em}
  .stations p{margin:0;font-size:15px;line-height:1.55;color:var(--demi);max-width:44ch}
  .stations b{font-family:var(--mono);font-size:11.5px;font-weight:500;color:var(--vert-titre);letter-spacing:.04em}
  .stations .methode-term{margin-top:8px;max-width:520px}
  .methode-grille>div:last-child{position:sticky;top:96px}
  .methode-scene{position:relative;aspect-ratio:1374/1120;container-type:inline-size;margin-top:6px}
  .methode-scene .scene{position:absolute;inset:0}
  .methode-scene .objet{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
    filter:drop-shadow(0 30px 40px rgba(27,29,24,.22))}
  .methode-note{font-size:13px;color:var(--pale);margin-top:14px;max-width:60ch;line-height:1.5}
  .methode-term{border:1px solid color-mix(in srgb,var(--vert-vif) 55%,transparent);border-radius:10px;overflow:hidden;
    background:linear-gradient(163deg,color-mix(in srgb,var(--vert-titre) 55%,#0e0e11),color-mix(in srgb,var(--vert-titre) 20%,#0e0e11));
    box-shadow:0 24px 50px rgba(27,29,24,.28)}
  .methode-term .tb{display:flex;gap:6px;align-items:center;padding:9px 14px;background:color-mix(in srgb,var(--vert-vif) 18%,transparent);
    font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--sur-vert-pale)}
  .methode-term .tb i{width:8px;height:8px;border-radius:50%;background:var(--sur-vert-pale);opacity:.5}
  .methode-term .tb span{margin-left:auto}
  .methode-term .tc{padding:14px 18px 16px;font-family:var(--mono);font-size:12.5px;line-height:1.85;color:var(--sur-vert)}
  .methode-term .tc code{display:block;white-space:pre-wrap;overflow-wrap:anywhere}
  .methode-term .tc code::before{content:"$ ";color:var(--vert-clair);font-weight:600}
  .methode-term .tc .note{display:block;color:var(--sur-vert-pale);font-size:11.5px;margin-top:6px}
  .methode-liens{display:flex;flex-wrap:wrap;gap:10px 26px;margin-top:48px;padding-top:22px;border-top:1px solid var(--filet);font-size:14.5px}
  .methode-liens a{color:var(--demi);text-decoration:none;border-bottom:1px solid var(--filet-clair);padding-bottom:3px}
  .methode-liens a:hover{color:var(--encre);border-color:var(--vert-vif)}
  @media (max-width:980px){.methode-grille{grid-template-columns:minmax(0,1fr)}.methode-scene{max-width:640px}}
'''


def eventail_html(cartes):
    """`cartes` : liste de (href, svg, etiquette, nom, vif, clair, nuits) dans l'ordre du paquet ;
    la dernière est au-dessus. Les décalages et rotations donnent l'éventail."""
    n = len(cartes); out = ""
    for k, (href, svg, eti, nom, vif, clair, nuits) in enumerate(cartes):
        c = k - (n - 1) / 2
        style = (f"--z:{k + 1};--rot:{c * 5:.1f}deg;--dx:{c * 26:.0f}px;--dy:{abs(c) * 10:.0f}px;"
                 f"--ev-vif:{vif};--ev-clair:{clair};--ev-nuit-a:{nuits[0]};--ev-nuit-c:{nuits[2]}")
        out += (f'<a class="carte-ev" href="{href}" style="{style}" aria-label="Open {nom}">'
                f'<div class="ev-svg">{svg}</div>'
                f'<div class="ev-pied"><span>{eti}</span><b>Open {nom} &#8594;</b></div></a>')
    return f'<div class="eventail" aria-label="The five instruments">{out}</div>'


def methode_html(stations, extra=None):
    """Les quatre stations de la méthode, en rail (le papier des pages outils) : numéro, titre,
    phrase, chiffre ; les chiffres viennent des relevés, par l'appelant. `extra` : du HTML posé
    dans une station, par son numéro (les trois commandes vivent dans « 03 · RERUN »)."""
    out = ""
    for num, titre, texte, chiffre in stations:
        out += (f'<li><span class="num">{num}</span><h3>{titre}</h3><p>{" ".join(texte)}</p>'
                f'{(extra or {}).get(num, "")}<b>{chiffre}</b></li>')
    return f'<ol class="stations">{out}</ol>'


def methode_svg(stations):
    """La figure de la méthode : quatre stations reliées, chacune avec son numéro, son titre, sa
    phrase et son chiffre (lus dans les relevés par l'appelant, jamais tapés ici)."""
    W, H = 900, 250; n = len(stations); lw = (W - 40 - (n - 1) * 28) / n
    out = ('<defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
           '<path class="fl" d="M0,0 L10,5 L0,10 z"/></marker></defs>')
    for i, (num, titre, texte, chiffre) in enumerate(stations):
        x = 20 + i * (lw + 28)
        out += f'<rect class="st-fond" x="{x:.0f}" y="30" width="{lw:.0f}" height="190" rx="10"/>'
        out += f'<text class="num" x="{x + 16:.0f}" y="58">{num}</text>'
        out += f'<text class="titre" x="{x + 16:.0f}" y="88">{titre}</text>'
        for j, ligne in enumerate(texte):
            out += f'<text class="texte" x="{x + 16:.0f}" y="{114 + j * 17}">{ligne}</text>'
        out += f'<text class="chiffre" x="{x + 16:.0f}" y="200">{chiffre}</text>'
        if i < n - 1:
            out += f'<path class="fleche" d="M{x + lw + 4:.0f},125 L{x + lw + 24:.0f},125"/>'
    return f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">{out}</svg>'
