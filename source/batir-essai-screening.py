#!/usr/bin/env python3
"""THE SELF-SERVE TEST (screening/try.html, 4 November 2026): a visitor pastes company or vessel names and sees, in the
browser, which entries of the sanctions lists they resemble. Same look as the red instrument page, one more terminal.

WHAT RUNS WHERE. The matcher is the screening tool's own code, packed as it is by essai-screening/empaqueter.ts
(moteur.js) and carried in the page as an inline script. The data (essai-screening/donnees.json, built by
construire.ts) holds the companies and vessels of the lists whose terms allow republishing, the tool's pinned word
weights, the two thresholds measured by the tool, and a fixed set of names with the result the tool gave them. At load
the page hands both to a Web Worker built from its own text (worker-src blob:, assembler.py csp()), which indexes the
lists in the background, re-screens the fixed set and reports whether it got the tool's result; then it screens what
the visitor pastes, one name at a time, so the list of results grows as it runs.

WHAT THE PAGE CANNOT DO, and says: individuals are not on it (no natural person's name enters a published file), two
lists are left out (named, with the reason), a candidate is a name to check and never a match established, and nothing
leaves the page: no request after load (connect-src 'none'), which temoin-essai-navigateur.mjs measures in a real
browser.

EVERY FIGURE on the page comes from donnees.json: the counts, the dates, the thresholds, the rates, the commit.
"""
import hashlib
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))
from outil import OUTILS, barre_site, CSS_BARRE_SITE, pied_html, n_tests, SITE_URL  # noqa: E402
from style_instrument_screening import CSS  # noqa: E402  (the red instrument's look, shared)
from instrument_carte import CSS_NOIR  # noqa: E402  (the instruments' lower page: folds, columns, the open buttons)

ESSAI = BASE / "essai-screening"
D = json.loads((ESSAI / "donnees.json").read_text())
MOTEUR = (ESSAI / "moteur.js").read_text()
OFFRE = json.loads((BASE / "offre-screening.json").read_text())
EN_LETTRES = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
              10: "ten", 11: "eleven", 12: "twelve"}

if D["moteur"]["sha256"] != hashlib.sha256(MOTEUR.encode()).hexdigest():
    sys.exit("essai-screening/moteur.js is not the bundle donnees.json names: rerun node source/essai-screening/construire.ts")
if "—" in MOTEUR or "—" in json.dumps(D):
    sys.exit("un cadratin dans le moteur ou les donnees : la garde du site le refusera.")

N_COUVERTES = len(D["listes"])
N_OUTIL = D["listesDeLOutil"]
DATES = sorted(l["telechargeLe"][:10] for l in D["listes"])
SCEAU = hashlib.sha256((ESSAI / "donnees.json").read_bytes()).hexdigest()[:16]
POIDS_MO = (len(MOTEUR) + len(json.dumps(D, separators=(",", ":")))) / 1e6
COMMIT = D["moteur"]["commit"]


def n(x):
    return f"{x:,}"


def pc(c):
    return f"{c['taux'] * 100:.0f}% [{c['bas'] * 100:.0f}-{c['haut'] * 100:.0f}]"


def dates_lues():
    return DATES[0] if DATES[0] == DATES[-1] else f"between {DATES[0]} and {DATES[-1]}"


def table_listes():
    lignes = ""
    for l in D["listes"]:
        lic = l["licence"]
        mention = f'<br><code class="mention">{lic["mention"]}</code>' if lic["mention"] else ""
        lignes += (f'<tr><th scope="row">{l["source"]}<small>{l["titre"]}</small></th>'
                   f'<td>{l["telechargeLe"][:10]}</td>'
                   f'<td>{n(l["gardees"])}<small>of {n(l["entrees"])} entries</small></td>'
                   f'<td><a href="{lic["url"]}"><code class="mention">{lic["nom"]}</code></a>{mention}</td></tr>')
    return f'''<div class="e-tscroll"><table class="e-listes">
      <caption class="sr">The lists this page compares against, their download dates, what is kept of each, and the terms it is reused under</caption>
      <thead><tr><th scope="col">List</th><th scope="col">Downloaded</th><th scope="col">Companies and vessels kept</th><th scope="col">Reused under</th></tr></thead>
      <tbody>{lignes}</tbody></table></div>'''


def exclues():
    return "".join(f'<li><b>{e["source"]}, {e["titre"]}.</b> Left out: {e["raison"]}.</li>' for e in D["exclues"])


S = D["seuils"]
V = S["verdict"]
R = S["apprentissageReel"]

CSS_ESSAI = '''
  @media (prefers-reduced-motion:reduce){.caret{animation:none}}
  .e-label{display:block;font-family:var(--mono);font-size:12.5px;color:var(--sur-pale);margin:0 0 8px;line-height:1.6}
  .e-noms{display:block;width:100%;min-height:150px;resize:vertical;font:13.5px/1.7 var(--mono);color:var(--sur);
    background:color-mix(in srgb,var(--nuit-c) 80%,#000);border:1px solid color-mix(in srgb,var(--accent-vif) 35%,transparent);
    border-radius:8px;padding:12px 14px;caret-color:var(--accent-vif)}
  .e-noms:focus-visible{outline:3px solid var(--accent-vif);outline-offset:2px;border-color:var(--accent-vif)}
  .e-noms:disabled{opacity:.7}
  .regls{margin-top:14px}
  .regl:disabled{opacity:.55;cursor:not-allowed}
  .regl:focus-visible{outline:3px solid var(--accent-clair);outline-offset:3px}
  .e-etat{min-height:24px}
  .e-etat.e-rouge{color:#ffb3a8}
  .e-etat.e-rouge b{color:#ffd3cc}
  /* the progress bar: a track and a fill driven by width, from the worker's counts; nothing loops on its own */
  .e-barre{height:4px;border-radius:2px;background:color-mix(in srgb,var(--sur-pale) 18%,transparent);margin:0 0 14px;overflow:hidden}
  .e-barre i{display:block;height:100%;width:0;background:var(--accent-vif);transition:width .25s var(--montee)}
  @media (prefers-reduced-motion:reduce){.e-barre i{transition:none}}
  .e-resultats{list-style:none;padding:0;margin:0 0 14px;font-family:var(--mono);font-size:12.5px}
  .e-res{border-top:1px solid color-mix(in srgb,var(--sur-pale) 14%,transparent);padding:11px 0 10px}
  .e-res:last-child{border-bottom:1px solid color-mix(in srgb,var(--sur-pale) 14%,transparent)}
  .e-tete{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
  .e-pill{font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:3px 8px;border-radius:4px;
    border:1px solid color-mix(in srgb,var(--sur-pale) 40%,transparent);color:var(--sur-pale)}
  .e-strong .e-pill{color:var(--nuit-c);background:var(--accent-vif);border-color:var(--accent-vif)}
  .e-possible .e-pill{color:var(--accent-clair);border-color:var(--accent-vif)}
  .e-nom{color:var(--sur);font-weight:500;font-size:13.5px;overflow-wrap:anywhere}
  .e-n{color:var(--sur-pale)}
  .e-cands{list-style:none;padding:0;margin:8px 0 0 0}
  .e-cands li{display:grid;grid-template-columns:auto 1fr auto;gap:4px 12px;padding:5px 0 5px 12px;
    border-left:2px solid color-mix(in srgb,var(--accent-vif) 45%,transparent);margin:0 0 4px}
  .e-src{color:var(--accent-clair)}
  .e-liste{color:var(--sur);overflow-wrap:anywhere}
  .e-score{color:var(--sur);text-align:right}
  .e-meta{grid-column:2/4;color:var(--sur-pale);font-size:12px;line-height:1.6}
  .e-note{color:var(--sur-pale);font-size:12px;margin:6px 0 0;line-height:1.6}
  .e-avert{color:#ffb3a8;font-size:12px;margin:6px 0 0;line-height:1.6}
  @media (max-width:560px){.e-cands li{grid-template-columns:auto 1fr}.e-score{grid-column:1/3;text-align:left}.e-meta{grid-column:1/3}}
  .e-export{margin:0 0 18px}
  .e-export a{text-decoration:none;display:inline-block}
  /* the paper: the list of sources is a table, read by the auditor */
  .e-tscroll{overflow-x:auto;margin:10px 0 14px}
  .e-listes{border-collapse:collapse;font-size:13.5px;min-width:620px;color:var(--demi);line-height:1.5}
  .e-listes th,.e-listes td{text-align:left;vertical-align:top;padding:8px 12px 8px 0;border-bottom:1px solid var(--filet-clair)}
  .e-listes thead th{font:500 10.5px/1.4 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--accent-titre)}
  .e-listes tbody th{font-weight:600;color:var(--encre);white-space:nowrap}
  .e-listes small{display:block;font-weight:400;color:var(--demi);font-size:12px;white-space:normal;max-width:34ch}
  .e-listes a{color:var(--accent-titre)}
  code.mention{font:inherit;font-size:12.5px}
  .basse .e-cmd{display:inline-block;font:12.5px/1.6 var(--mono);background:var(--nuit-b);color:var(--sur);padding:2px 8px;border-radius:4px}
  .basse .clone-col h2{margin-top:0}
'''

# ── the worker and the page, one script ──────────────────────────────────────────────────────────────────────────
# `ouvrier(port)` is written once and runs in two places: inside a Web Worker built from the page's own text (the
# normal case), or on the page's thread when the browser gives no worker (the port is then a pair of functions).
JS = r'''
  const $ = (s) => document.querySelector(s);
  const D = JSON.parse($("#donnees").textContent);
  const SOURCES = D.listes.map((l) => l.source);
  const PLAFOND = 500;

  /* ──── the worker: index the lists once, then screen what it is sent; same code on the page thread as a fallback ──── */
  function ouvrier(port) {
    const M = globalThis.CrusetraMoteur;
    const cribler = M.require("./cribler.ts");
    const hacher = (mot) => {
      const un = (base) => { let h = base >>> 0; for (let i = 0; i < mot.length; i++) { h ^= mot.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return h.toString(16).padStart(8, "0"); };
      return un(2166136261) + un(0x9747b28c);
    };
    /* the tool's word table: words of the shipped names in clear, every other word by its hash */
    class Table extends Map {
      constructor(df, dfh) { super(df); this.h = new Map(dfh); }
      get(k) { const v = super.get(k); return v !== undefined ? v : this.h.get(hacher(k)); }
      has(k) { return super.has(k) || this.h.has(hacher(k)); }
    }
    const vers = (e) => ({ source: e.s, id: e.id, nom: e.n, alias: e.a, type: e.t,
      ...(e.f ? { aliasFaibles: e.f.map((i) => e.a[i]) } : {}), ...(e.imo ? { imo: e.imo } : {}), ...(e.ai ? { autresImo: e.ai } : {}),
      ...(e.p ? { programme: e.p } : {}), ...(e.d ? { designation: { date: e.d, champ: "" } } : {}) });
    let d = null, f = null, index = [], seuils = null, PLAFOND = 0;
    /* the tool's order of candidates (src/cribler.ts), applied to the union of the per-list results */
    const ordre = (a, b) => b.score - a.score || a.nomListe.localeCompare(b.nomListe) || a.source.localeCompare(b.source) || a.ids[0].localeCompare(b.ids[0]);
    const MONTRES = cribler.CANDIDATS_MONTRES;
    function criblerUn(c) {
      const parts = index.map((ix) => cribler.cribler(c, ix, seuils));
      const tous = parts.flatMap((p) => p.candidats).sort(ordre);
      const total = parts.reduce((s, p) => s + p.candidats.length + p.autres, 0);
      const { candidats, autres, statut, ecartesParImo, ...reste } = parts[0];
      return { ...reste, statut: total === 0 ? "no-match" : tous[0].score >= seuils.fort ? "strong" : "possible",
        candidats: tous.slice(0, MONTRES), autres: Math.max(0, total - MONTRES), ecartesParImo: parts.flatMap((p) => p.ecartesParImo) };
    }
    function lignesDe(texte) {
      const t = texte.replace(/\r\n?/g, "\n").trim();
      if (/^\s*"?name"?\s*(,|$)/i.test(t.split("\n")[0])) return cribler.lireContreparties(t);
      const csv = ["name,imo"];
      for (const l of t.split("\n")) {
        const brut = l.trim(); if (!brut) continue;
        const m = brut.match(/^(.*?)[,;]\s*(?:IMO\s*)?(\d{7})\s*$/i);
        const nom = (m ? m[1] : brut).trim().replace(/"/g, "");
        if (nom) csv.push(`"${nom}",${m ? m[2] : ""}`);
      }
      return cribler.lireContreparties(csv.join("\n") + "\n");
    }
    port.onmessage = (ev) => {
      const m = ev.data;
      try {
        if (m.type === "init") {
          PLAFOND = m.plafond;
          d = JSON.parse(m.donnees);
          f = { entrees: d.poids.entrees, df: new Table(d.poids.df, d.poids.dfh) };
          seuils = { fort: d.seuils.fort, possible: d.seuils.possible };
          const sources = d.listes.map((l) => l.source);
          let fait = 0;
          for (const s of sources) {
            const part = d.entrees.filter((e) => e.s === s).map(vers);
            index.push(new cribler.Index(f, part, seuils.possible));
            fait += part.length;
            port.postMessage({ type: "progres", source: s, i: index.length, n: sources.length, entrees: fait });
          }
          port.postMessage({ type: "pret", entrees: fait });
        } else if (m.type === "cribler") {
          const { lignes, avertissements } = lignesDe(m.texte);
          if (lignes.length === 0) { port.postMessage({ type: "vide", id: m.id }); return; }
          if (lignes.length > PLAFOND) { port.postMessage({ type: "trop", id: m.id, n: lignes.length }); return; }
          port.postMessage({ type: "depart", id: m.id, n: lignes.length, avertissements });
          lignes.forEach((c, i) => port.postMessage({ type: "resultat", id: m.id, i: i + 1, n: lignes.length, resultat: criblerUn(c) }));
          port.postMessage({ type: "fini", id: m.id, n: lignes.length });
        }
      } catch (e) {
        port.postMessage({ type: "erreur", id: m.id, message: String(e && e.message || e) });
      }
    };
  }

  /* ──── the page ──── */
  const etat = $("#e-etat"), barre = $("#e-barre"), liste = $("#e-resultats"), zone = $("#e-noms");
  const lancer = $("#e-lancer"), exemple = $("#e-exemple"), vider = $("#e-vider"), exportZone = $("#e-export"), preuve = $("#tm-preuve");
  const nb = (x) => x.toLocaleString("en-US");
  let pret = false, enCours = null, enAttente = null, idSuivant = 1, t0 = performance.now(), prepareEn = null, echec = false;
  const dire = (html, rouge) => { etat.innerHTML = html; etat.classList.toggle("e-rouge", !!rouge); };
  const progres = (p) => { barre.hidden = false; barre.firstElementChild.style.width = Math.round(p * 100) + "%"; };

  let canal;
  function ouvrirCanal() {
    const code = $("#moteur").textContent + "\n(" + ouvrier.toString() + ")(self);";
    try {
      if (typeof Worker === "undefined") throw new Error("no Worker");
      const w = new Worker(URL.createObjectURL(new Blob([code], { type: "text/javascript" })));
      let vivant = false;
      w.onmessage = (ev) => { vivant = true; recevoir(ev.data); };
      w.onerror = (ev) => {
        if (!vivant) { w.terminate(); canal = enLigne(); return; }
        recevoir({ type: "erreur", id: enCours && enCours.id, message: ev.message || "the worker stopped" });
      };
      return { envoyer: (m) => w.postMessage(m), fond: true };
    } catch (e) { return enLigne(); }
  }
  /* no worker: the same function on the page thread; the page pauses while the lists are indexed */
  function enLigne() {
    const port = { onmessage: null, postMessage: (m) => recevoir(m) };
    ouvrier(port);
    return { envoyer: (m) => setTimeout(() => port.onmessage({ data: m }), 30), fond: false };
  }

  const SRC = (c) => c.source;
  const quand = (c) => c.designation && c.designation.date ? (c.designation.date.startsWith("not ") ? "date listed: " + c.designation.date : "listed on " + c.designation.date) : "";
  function ligneCandidat(c) {
    const meta = [];
    if (c.alias) meta.push("found by the alias " + c.alias + (c.aliasFaible ? " (a weak alias: this candidate is to be read, never strong)" : ""));
    if (c.par === "imo") meta.push("found by its IMO number " + (c.imo || "") + (c.renomme ? "; the list knows this hull as " + c.renomme.nomsListes.join(", ") : ""));
    else if (c.imo) meta.push("IMO " + c.imo + (c.autresImo && c.autresImo.length ? " (also " + c.autresImo.join(", ") + ")" : ""));
    if (c.liste) meta.push("list: " + c.liste);
    const q = quand(c); if (q) meta.push(q);
    return `<li><span class="e-src">${SRC(c)}</span><span class="e-liste">${texte(c.nomListe)}</span><span class="e-score">${c.score.toFixed(3)}</span>`
      + (meta.length ? `<span class="e-meta">${texte(meta.join(". "))}</span>` : "") + "</li>";
  }
  const texte = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  function ajouterResultat(r) {
    const li = document.createElement("li");
    const classe = r.statut === "strong" ? "e-strong" : r.statut === "possible" ? "e-possible" : "e-aucun";
    li.className = "e-res " + classe;
    const compte = r.candidats.length + r.autres;
    const etiquette = r.statut === "no-match" ? "no candidate" : r.statut;
    let html = `<div class="e-tete"><span class="e-pill">${etiquette}</span><b class="e-nom">${texte(r.nom)}</b>`
      + (r.imo ? `<span class="e-n">IMO ${texte(r.imo)}</span>` : "")
      + `<span class="e-n">${compte === 0 ? "no entry at the possible level" : compte === 1 ? "1 candidate" : compte + " candidates"}</span></div>`;
    if (r.candidats.length) html += `<ul class="e-cands">${r.candidats.map(ligneCandidat).join("")}</ul>`;
    if (r.autres > 0) html += `<p class="e-note">and ${r.autres} more at the possible level, not shown</p>`;
    if (r.ecartesParImo && r.ecartesParImo.length) html += `<p class="e-note">set aside, a different hull: ${texte(r.ecartesParImo.map((x) => x.nomListe + " (IMO " + x.imo + ")").join(", "))}</p>`;
    if (r.imoInvalide) html += `<p class="e-avert">the IMO number given does not pass its check digit; it was used as typed</p>`;
    li.innerHTML = html;
    liste.appendChild(li);
  }
  function csvDe(resultats) {
    const q = (s) => '"' + String(s == null ? "" : s).replace(/"/g, '""') + '"';
    const lignes = [["name", "imo", "status", "candidates", "source", "list entry", "alias", "score", "found by", "ids", "list", "designation"].map(q).join(",")];
    for (const r of resultats) {
      if (r.candidats.length === 0) lignes.push([r.nom, r.imo, r.statut, 0, "", "", "", "", "", "", "", ""].map(q).join(","));
      for (const c of r.candidats) lignes.push([r.nom, r.imo, r.statut, r.candidats.length + r.autres, c.source, c.nomListe, c.alias, c.score.toFixed(3), c.par, c.ids.join(" "), c.liste, c.designation && c.designation.date].map(q).join(","));
    }
    return lignes.join("\n") + "\n";
  }
  let urlCsv = null;
  function offrirCsv(resultats) {
    if (urlCsv) URL.revokeObjectURL(urlCsv);
    urlCsv = URL.createObjectURL(new Blob([csvDe(resultats)], { type: "text/csv;charset=utf-8" }));
    $("#e-csv").href = urlCsv;
    exportZone.hidden = false;
  }

  /* the fixed set: the page re-screens it and must get the tool's result (ties ordered the same way on both sides) */
  const cle = (a) => JSON.stringify(a.candidats.map((c) => [c.source, c.ids.join(" "), c.nomListe, c.alias || "", c.score, c.par]).sort((x, y) => (y[4] - x[4]) || (x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0) || (x[1] < y[1] ? -1 : 1)))
    + "|" + a.statut + "|" + a.autres;
  let temoinRecu = [];
  function verifierTemoin() {
    const attendu = D.temoin.attendu;
    const ecarts = attendu.filter((a, i) => !temoinRecu[i] || cle(a) !== cle(temoinRecu[i]));
    const secondes = (prepareEn / 1000).toFixed(1);
    if (ecarts.length === 0 && temoinRecu.length === attendu.length) {
      preuve.innerHTML = `self-check <span class="ok">passed</span>: this page re-screened the ${attendu.length} fixed names of ${D.temoin.fichier} and got the tool’s candidates and scores (record of ${D.genereLe.slice(0, 10)}, tool commit ${COMMIT_MOTEUR}) · lists prepared in ${secondes} s${canal.fond ? "" : ", on the page thread: this browser gives no background worker"}`;
    } else {
      preuve.innerHTML = `self-check <span class="ko">FAILED</span>: ${ecarts.length} of ${attendu.length} fixed names differ from the tool’s record; do not trust this page’s results`;
    }
  }
  const COMMIT_MOTEUR = D.moteur.commit;

  let resultats = [];
  function recevoir(m) {
    if (m.type === "progres") {
      progres(m.i / m.n);
      dire(`Preparing the lists in the background: <b>${m.i} of ${m.n}</b>, ${nb(m.entrees)} companies and vessels so far` + (enAttente ? `; then your names` : ""));
    } else if (m.type === "pret") {
      pret = true; prepareEn = performance.now() - t0; barre.hidden = true;
      dire(`Ready: <b>${nb(m.entrees)} companies and vessels</b> from ${EN_LETTRES[SOURCES.length]} of the tool’s ${EN_LETTRES[D.listesDeLOutil]} lists, downloaded ${DATES_LUES}. Paste your names above.`);
      lancer.disabled = false;
      canal.envoyer({ type: "cribler", id: 0, texte: D.temoin.csv });
      if (enAttente) { const t = enAttente; enAttente = null; demarrer(t); }
    } else if (m.type === "vide") {
      if (m.id === 0) return;
      enCours = null; lancer.disabled = false; zone.disabled = false;
      dire("Paste at least one name above.", true); zone.focus();
    } else if (m.type === "trop") {
      if (m.id === 0) return;
      enCours = null; lancer.disabled = false; zone.disabled = false;
      dire(`Up to ${PLAFOND} names per run on this page (${nb(m.n)} pasted): split the list, or send it for the report.`, true);
    } else if (m.type === "depart") {
      if (m.id === 0) return;
      liste.innerHTML = ""; resultats = []; exportZone.hidden = true;
      enCours.n = m.n; enCours.avertissements = m.avertissements;
      progres(0); dire(`Screening <b>0 of ${m.n}</b>`);
    } else if (m.type === "resultat") {
      if (m.id === 0) { temoinRecu[m.i - 1] = m.resultat; return; }
      resultats.push(m.resultat); ajouterResultat(m.resultat); enCours.fait = m.i;
      progres(m.i / m.n); dire(`Screening <b>${m.i} of ${m.n}</b>`);
    } else if (m.type === "fini") {
      if (m.id === 0) { verifierTemoin(); return; }
      const forts = resultats.filter((r) => r.statut === "strong").length, possibles = resultats.filter((r) => r.statut === "possible").length;
      const avert = enCours.avertissements && enCours.avertissements.length ? ` <span class="e-n">Read: ${texte(enCours.avertissements.join(" "))}</span>` : "";
      barre.hidden = true;
      dire(`<b>${m.n} name${m.n > 1 ? "s" : ""} screened</b>: ${forts} strong, ${possibles} possible, ${m.n - forts - possibles} with no candidate. Nothing you typed left this page.${avert}`);
      offrirCsv(resultats);
      enCours = null; lancer.disabled = false; zone.disabled = false;
    } else if (m.type === "erreur") {
      barre.hidden = true;
      if (!pret) {
        echec = true; lancer.disabled = true;
        dire(`This page could not start the comparison in your browser (${texte(m.message)}). Your names were not sent anywhere. Write to ${CONTACT}, or open the page in another browser.`, true);
        preuve.innerHTML = 'self-check <span class="ko">not run</span>: the lists could not be prepared in this browser';
        return;
      }
      if (m.id === 0) { preuve.innerHTML = `self-check <span class="ko">FAILED</span>: ${texte(m.message)}`; return; }
      const fait = (enCours && enCours.fait) || 0, n = (enCours && enCours.n) || 0;
      if (n === 0) dire(`These names could not be screened: ${texte(m.message)}. Nothing you typed left this page.`, true);
      else dire(`<b>Stopped at ${fait} of ${n}</b>: ${texte(m.message)}. The ${fait} result${fait === 1 ? "" : "s"} above ${fait === 1 ? "is" : "are"} complete; the other ${n - fait} were not compared.`, true);
      if (resultats.length) offrirCsv(resultats);
      enCours = null; lancer.disabled = false; zone.disabled = false;
    }
  }

  function demarrer(texteNoms) {
    enCours = { id: idSuivant++, fait: 0, n: 0 };
    lancer.disabled = true; zone.disabled = true;
    canal.envoyer({ type: "cribler", id: enCours.id, texte: texteNoms });
  }
  lancer.addEventListener("click", () => {
    if (echec || enCours) return;
    const t = zone.value;
    if (!t.trim()) { dire("Paste at least one name above.", true); zone.focus(); return; }
    if (!pret) { enAttente = t; lancer.disabled = true; dire(`Your names run as soon as the lists are prepared.`); return; }
    demarrer(t);
  });
  exemple.addEventListener("click", () => {
    zone.value = EXEMPLES.join("\n"); zone.focus();
    dire(`${EXEMPLES.length} sample names loaded, from the fixed set this page checks itself with.`);
  });
  vider.addEventListener("click", () => {
    zone.value = ""; liste.innerHTML = ""; resultats = []; exportZone.hidden = true; barre.hidden = true;
    dire(pret ? "Cleared. Paste your names above." : "Cleared."); zone.focus();
  });
  zone.addEventListener("keydown", (ev) => { if ((ev.metaKey || ev.ctrlKey) && ev.key === "Enter") lancer.click(); });

  lancer.disabled = true;
  dire("Preparing the lists in the background");
  progres(0);
  canal = ouvrirCanal();
  canal.envoyer({ type: "init", donnees: $("#donnees").textContent, plafond: PLAFOND });
'''

EXEMPLES = ([a["nom"] for a in D["temoin"]["attendu"] if a["statut"] != "no-match"][:3]
            + [a["nom"] for a in D["temoin"]["attendu"] if a["statut"] == "no-match"][:2])
PLAFOND = 500   # names per run on the page: enough for a client file's sample, small enough to answer in seconds
JS = (JS.replace("const PLAFOND = 500;", f"const PLAFOND = {PLAFOND};").replace("EN_LETTRES[", "EN_LETTRES_JS[")
      .replace("const $ = (s)", f"const EN_LETTRES_JS = {json.dumps(EN_LETTRES)};\n  const DATES_LUES = {json.dumps(dates_lues())};\n"
                                f"  const CONTACT = {json.dumps(OFFRE['contact'])};\n  const EXEMPLES = {json.dumps(EXEMPLES)};\n  const $ = (s)", 1))

SUJET = "Ten%20names%20to%20screen"
DESCRIPTION = ("Paste company or vessel names and see which entries of eight sanctions lists they resemble, "
               "computed in your browser with the tool's own code: nothing you type leaves the page.")

PAGE = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra Screening &#183; try it on your names</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra Screening: try it on your own names, in your browser">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:url" content="{SITE_URL}screening/try.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="{DESCRIPTION}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%23180b0f'/%3E%3Cpath d='M16 0v16H0z' fill='%237a1f2e'/%3E%3C/svg%3E">
<link rel="stylesheet" href="../fontes/literata.css">
<link rel="stylesheet" href="../fontes/roboto-mono.css">
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_NOIR}{CSS_ESSAI}{CSS_BARRE_SITE}</style>
{barre_site(courant=OUTILS["screening"]["page_hero"], racine="../")}

<section class="tete">
  <div class="colonne">
    <h1 class="h1">Test your own names here, in your browser.</h1>
    <p class="lede">Paste company or vessel names, one per line. This page compares each one with the companies and
      vessels of {EN_LETTRES[N_COUVERTES]} of the tool&#8217;s {EN_LETTRES[N_OUTIL]} sanctions lists, with the tool&#8217;s own code,
      and nothing you type leaves it. <b>A candidate is a name to check, not a match established.</b> Individuals are
      not covered on this page.</p>
  </div>
</section>

<section class="poste">
  <div class="colonne">
    <div class="dessus">
      <div class="t-page-halo" aria-hidden="true"></div>
      <div class="terminal">
        <div class="tm-barre"><i></i><i></i><i></i><span>crusetra screening &#183; your names, in your browser</span></div>
        <div class="tm-corps">
          <p class="tm-l"><span class="ps">$</span> crusetra screen --names your-list.csv<span class="caret" aria-hidden="true"></span></p>
          <label class="e-label" for="e-noms">Company or vessel names, one per line. For a vessel, add its IMO number after a comma.</label>
          <textarea id="e-noms" class="e-noms" rows="7" spellcheck="false" autocomplete="off" autocapitalize="off"></textarea>
          <div class="regls">
            <button class="regl actif" id="e-lancer" type="button">Screen these names</button>
            <button class="regl" id="e-exemple" type="button">Load {EN_LETTRES[len(EXEMPLES)]} sample names</button>
            <button class="regl" id="e-vider" type="button">Clear</button>
          </div>
          <p class="tm-sortie e-etat" id="e-etat" role="status" aria-live="polite">Preparing the lists</p>
          <div class="e-barre" id="e-barre" aria-hidden="true"><i></i></div>
          <ol class="e-resultats" id="e-resultats" aria-label="Results, one per name, in the order pasted"></ol>
          <div class="regls e-export" id="e-export" hidden>
            <a class="regl" id="e-csv" href="#" download="screening-try.csv">Download these results as CSV</a>
          </div>
          <p class="tm-l" style="margin-top:14px"><span class="ps">$</span> crusetra verify --self-check</p>
          <p class="tm-preuve" id="tm-preuve">waiting for the lists</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="basse">
  <div class="colonne basse-grille">
    <div class="plis">
      <details class="pli"><summary>What this page compares against, with its terms of reuse</summary>
    <p>The companies and vessels of {EN_LETTRES[N_COUVERTES]} of the tool&#8217;s {EN_LETTRES[N_OUTIL]} lists, as downloaded {dates_lues()}:
      <b>{n(D["totaux"]["entrees"])} entries</b>, {n(D["totaux"]["societes"])} companies and {n(D["totaux"]["navires"])} vessels, about {POIDS_MO:.1f} MB loaded once with the page.
      Each list is reused under the terms its publisher states, read at the address given:</p>
    {table_listes()}
    <ul>
      {exclues()}
      <li><b>Individuals.</b> Every entry the lists type as a person, or leave untyped, stays out of this page, and so do the
        {D["retires"]["homonymesDePersonnes"]} companies whose name is also written as a person&#8217;s name on a list, and the owners and
        linked parties a list writes beside an entry. No natural person&#8217;s name is in this page&#8217;s data.</li>
      <li><b>As the lists write them.</b> Names, aliases and programs are the lists&#8217; own text, with one change: the
        {D["cadratinsRemplaces"]} names a list writes with an em dash carry a hyphen here, which the tool reads the same way.</li>
      <li><b>Freshness.</b> The dates above are the download dates. One command rebuilds the data from the lists,
        <span class="e-cmd">node source/essai-screening/construire.ts --fetch</span>, and a check turns red once a list is
        more than {D["fraicheurJours"]} days old (data of {D["genereLe"][:10]}, content hash {SCEAU}).</li>
    </ul>
      </details>
      <details class="pli"><summary>How a name is scored, and what the figures are</summary>
    <ul>
      <li><b>The tool&#8217;s own code.</b> The {D["moteur"]["modules"]} modules of the matcher at commit {COMMIT}, carried as they are:
        words aligned in any order and weighed by their rarity on the lists, typos and romanization variants tolerated, vessel
        numbers that must agree, a listed name found inside a longer one read as a possible match.</li>
      <li><b>The weights.</b> A word weighs by its rarity in the tool&#8217;s pinned table of {n(D["poids"]["entrees"])} entries, counted
        on {D["poids"]["compteeLe"]}. The words of the names on this page travel in clear, every other word as a one-way hash with
        its count, so a word of yours weighs here what it weighs in the tool.</li>
      <li><b>The two levels.</b> Strong at <b>{S["fort"]:.2f}</b>, possible at <b>{S["possible"]:.2f}</b>, measured on {S["mesureLe"]} on the tool&#8217;s
        training sets, the same way the report measures them. On the held-out verdict set ({n(V["jeu"]["match"])} pairs that match,
        {n(V["jeu"]["different"])} that differ, written by another hand and used for no choice), the strong level finds
        <b>{pc(V["fort"]["rappel"])}</b> of the matches with <b>{pc(V["fort"]["fauxPositifs"])}</b> false alerts; the possible level finds
        {pc(V["possible"]["rappel"])} with {pc(V["possible"]["fauxPositifs"])}. On {n(R["jeu"]["different"])} real, distinct companies that share a word,
        the strong level raises {pc(R["fort"]["fauxPositifs"])} false alerts.</li>
      <li><b>Self-check.</b> At load, the page re-screens {len(D["temoin"]["attendu"])} fixed names ({D["temoin"]["fichier"]}) and compares with the
        candidates and scores the tool gave them; the terminal prints the verdict.</li>
    </ul>
      </details>
      <details class="pli"><summary>What this page cannot do</summary>
    <ul>
      <li><b>Find a person.</b> Individuals are not on this page. The report screens them.</li>
      <li><b>Replace the report.</b> The lists left out above, the Official Journal supplement, the weekly re-screening
        and the record with its content hash come with the report, on the tool&#8217;s {EN_LETTRES[N_OUTIL]} lists.</li>
      <li><b>Decide.</b> A candidate is a name for your compliance officer to confirm or set aside. This page gives no
        legal advice, and a name with no candidate here is a name this page found no entry for, on these lists, at these dates.</li>
      <li><b>Read your file.</b> Up to {PLAFOND} names per run, pasted by hand; nothing is uploaded.</li>
    </ul>
      </details>
      <details class="pli"><summary>Why nothing leaves this page</summary>
    <ul>
      <li><b>The browser forbids it.</b> The page&#8217;s security policy allows no connection (connect-src &#8217;none&#8217;) and
        no script but its own; the comparison runs in a background worker built from the page&#8217;s own text.</li>
      <li><b>A check watches it.</b> The site&#8217;s check loads this page in a real browser, screens the fixed set, and counts
        the requests after load: zero, and a planted request must turn the check red.</li>
    </ul>
      </details>
    </div>
    <aside class="clone-col">
    <h2>The report, on all {EN_LETTRES[N_OUTIL]} lists</h2>
    <p>The Screening report screens your list against the tool&#8217;s {EN_LETTRES[N_OUTIL]} lists, individuals included, and comes back with
      its record and content hash.</p>
    <div class="ouvrir-ligne"><a class="ouvrir" href="mailto:{OFFRE["contact"]}?subject={SUJET}">Try it on {EN_LETTRES.get(OFFRE["essai_noms"], OFFRE["essai_noms"])} of your names <span class="fl" aria-hidden="true">&#8594;</span></a>
      <a class="ouvrir tarif" href="../ENGAGEMENT.html">See pricing <span class="fl" aria-hidden="true">&#8594;</span></a></div>
    </aside>
  </div>
</section>

{pied_html(outil=OUTILS["screening"], sceau=SCEAU, tests=n_tests(OUTILS["screening"]))}

<script type="application/json" id="donnees">{json.dumps(D, separators=(",", ":"))}</script>
<script id="moteur">{MOTEUR}</script>
<script>{JS}</script>
'''

PAGE = PAGE.replace("&#8212;", "&#183;")
if "—" in PAGE:
    sys.exit("un cadratin s'est glisse dans la page : la garde du site le refusera.")
# no trailing ellipsis in anything a visitor reads (Arslane, 19/10): checked on the page's own text, the tool's code
# and the JSON data apart (a spread `...x` in code is not a dot of suspension)
_VISIBLE = PAGE.replace(MOTEUR, "").replace(json.dumps(D, separators=(",", ":")), "")
if "…" in _VISIBLE or "...<" in _VISIBLE or "...\n" in _VISIBLE or '..."' in _VISIBLE or "...`" in _VISIBLE:
    sys.exit("des points de suspension dans la page : refuses (19/10).")

(BASE / "ESSAI-SCREENING.html").write_text(PAGE, encoding="utf-8")
print(f"ESSAI-SCREENING.html {len(PAGE) / 1e6:.1f} Mo ({n(D['totaux']['entrees'])} entries, {N_COUVERTES} of {N_OUTIL} lists, tool {COMMIT})")
