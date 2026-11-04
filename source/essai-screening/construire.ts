/**
 * THE DATA OF THE SELF-SERVE TEST (screening/try.html), rebuilt from the screening tool in one command.
 *
 *   node source/essai-screening/construire.ts            rebuild donnees.json, moteur.js and the witness from the lists on disk
 *   node source/essai-screening/construire.ts --fetch    download the lists first (the tool's own `npm run listes -- --fetch`)
 *   node source/essai-screening/construire.ts --check    exit 1 when the data is older than FRAICHEUR_JOURS days
 *
 * WHAT GOES IN, AND WHAT STAYS OUT. The page compares a visitor's names with COMPANIES AND VESSELS only. No natural
 * person's name enters a published file: that is the rule of this site (privacy page, GDPR) and of every push. So an
 * entry typed "person" or "other" by the tool's parsers is dropped, the two sources whose entries cannot be typed or
 * republished are left out whole (named in donnees.json with the reason), and a company or vessel whose name is also
 * written as a person's name on any list is dropped as well, to be safe. The ship-owner and "linked to" parties a list
 * writes next to an entry are not shipped either: they may name people.
 *
 * SAME RESULT AS THE TOOL. The matcher is the tool's own code (empaqueter.ts). The word-weight table is the tool's
 * pinned table (src/frequences.ts, TABLE_GELEE), shipped whole so that every score is the tool's: the words that occur
 * in the shipped names travel in clear, every other word travels as a one-way hash with its count, so a visitor's word
 * that no company name carries still weighs what it weighs in the tool, and no word of a person's entry is readable.
 * The two thresholds are measured here exactly as src/cribler.ts measures them, on the tool's training sets, and
 * shipped with their date. Then temoin-noms.csv, a fixed set of names, is screened by the tool in this process against
 * the shipped entries, and the browser witness (temoin-navigateur.mjs) must get the same candidates and scores.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { empaqueter, MOTEUR } from "./empaqueter.ts";

const ICI = dirname(new URL(import.meta.url).pathname);
export const DONNEES = join(ICI, "donnees.json");
export const MOTEUR_JS = join(ICI, "moteur.js");
export const TEMOIN_NOMS = join(ICI, "temoin-noms.csv");
/** A list older than this is a compliance risk: the check goes red and the page is not to be served as it is. */
export const FRAICHEUR_JOURS = 14;
/** Dropped whole, with the reason the page prints. */
const EXCLUES: Record<string, string> = {
  CSL: "the Commerce and State lists do not type their entries (company or individual), so none can be shipped as a company",
  UN: "the United Nations terms of use allow download and copy but not redistribution of the list; the tool screens it on each user's machine and the page does not republish it",
};
const PAR_TYPE = new Set(["entity", "vessel"]);

const src = (m: string) => join(MOTEUR, "src", m);
const listes = await import(src("listes.ts")) as typeof import("../../../../cascade-screening/src/listes.ts");
type Src = typeof listes;
const entites = await import(src("entites.ts")) as typeof import("../../../../cascade-screening/src/entites.ts");
const frequences = await import(src("frequences.ts")) as typeof import("../../../../cascade-screening/src/frequences.ts");
const cribler = await import(src("cribler.ts")) as typeof import("../../../../cascade-screening/src/cribler.ts");

/* ─────────────────────────── the one-way hash of a word ─────────────────────────── */

/** FNV-1a, 32 bits, twice with two offset bases, as the page computes it (the same function, character for character). */
export function hacher(mot: string): string {
  const un = (base: number) => {
    let h = base >>> 0;
    for (let i = 0; i < mot.length; i++) { h ^= mot.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h.toString(16).padStart(8, "0");
  };
  return un(2166136261) + un(0x9747b28c);
}

/* ─────────────────────────── the entries ─────────────────────────── */

export type Entree = {
  s: string; id: string; n: string; a: string[]; t: "entity" | "vessel";
  /** indexes into `a` of the aliases the list calls weak */
  f?: number[]; imo?: string; ai?: string[]; p?: string; d?: string;
};

function nettoyer(x: string): string { return x.trim().toLowerCase().replace(/\s+/g, " "); }

/** THE SITE SERVES NO EM DASH (U+2014, assembler.py). A few list names carry one (« PFLP — General Command »); it is
 *  written as a hyphen on the page. The tool reads both as a word separator (measured on 4 November 2026: the same
 *  tokens, the same score, src/preparation.ts jetonsEntite), so no score moves; the count is published. */
let cadratins = 0;
function sansCadratin(x: string): string {
  if (!x.includes("—")) return x;
  cadratins++;
  return x.replaceAll("—", "-");
}

export function extraire(m: NonNullable<ReturnType<Src["lireManifeste"]>>) {
  const personnes = new Set<string>();
  const brutes: { s: typeof listes.SOURCES[number]; l: (typeof m.listes)[number]; e: ReturnType<Src["lireListe"]> }[] = [];
  for (const s of listes.SOURCES) {
    const l = m.listes.find((x) => x.source === s.source);
    if (!l || !l.disponible) continue;
    const e = listes.lireListe(s.source, MOTEUR);
    for (const x of e) if (x.type === "person") { personnes.add(nettoyer(x.nom)); for (const a of x.alias) personnes.add(nettoyer(a)); }
    brutes.push({ s, l, e });
  }
  const gardees: Entree[] = [];
  const couvertes = [];
  const exclues = [];
  let homonymes = 0;
  for (const { s, l, e } of brutes) {
    if (s.source in EXCLUES) { exclues.push({ source: s.source, titre: s.titre, raison: EXCLUES[s.source] }); continue; }
    let n = 0;
    for (const x of e) {
      if (!PAR_TYPE.has(x.type)) continue;
      if (personnes.has(nettoyer(x.nom)) || x.alias.some((a) => personnes.has(nettoyer(a)))) { homonymes++; continue; }
      const faibles = (x.aliasFaibles ?? []).map((a) => x.alias.indexOf(a)).filter((i) => i >= 0);
      gardees.push({ s: x.source, id: x.id, n: sansCadratin(x.nom), a: x.alias.map(sansCadratin), t: x.type as "entity" | "vessel",
        ...(faibles.length ? { f: faibles } : {}), ...(x.imo ? { imo: x.imo } : {}), ...(x.autresImo?.length ? { ai: x.autresImo } : {}),
        ...(x.programme ? { p: sansCadratin(x.programme) } : {}), ...(x.designation ? { d: x.designation.date } : {}) });
      n++;
    }
    couvertes.push({ source: s.source, titre: s.titre, url: listes.urlSansJeton(s.url), telechargeLe: l.telechargeLe, sha256: l.sha256,
      entrees: l.entrees, gardees: n, licence: s.licence });
  }
  return { gardees, couvertes, exclues, homonymes };
}

/** The tool's EntreeListe, rebuilt from a shipped entry: what the index reads, nothing more. */
export function versEntreeListe(e: Entree) {
  return { source: e.s as "OFAC", id: e.id, nom: e.n, alias: e.a, type: e.t,
    ...(e.f ? { aliasFaibles: e.f.map((i) => e.a[i]!) } : {}), ...(e.imo ? { imo: e.imo } : {}), ...(e.ai ? { autresImo: e.ai } : {}),
    ...(e.p ? { programme: e.p } : {}), ...(e.d ? { designation: { date: e.d, champ: "" } } : {}) };
}

/* ─────────────────────────── the weights, the thresholds ─────────────────────────── */

export function tablePoids(f: { entrees: number; df: ReadonlyMap<string, number> }, gardees: Entree[]) {
  const clair = new Set<string>();
  for (const e of gardees) for (const nom of [e.n, ...e.a]) for (const j of entites.jetonsEntite(nom)) clair.add(j);
  const df: [string, number][] = [];
  const dfh: [string, number][] = [];
  const vus = new Set<string>();
  for (const [mot, n] of f.df) {
    if (clair.has(mot)) df.push([mot, n]);
    else {
      const h = hacher(mot);
      if (vus.has(h)) throw new Error(`two words of the table hash alike (${h}): change the hash.`);
      vus.add(h);
      dfh.push([h, n]);
    }
  }
  df.sort((a, b) => (a[0] < b[0] ? -1 : 1));
  dfh.sort((a, b) => (a[0] < b[0] ? -1 : 1));
  return { entrees: f.entrees, df, dfh };
}

function cellule(table: Record<string, { rappel: unknown; fauxPositifs: unknown }>, seuil: number) {
  const k = Object.keys(table).find((s) => Math.abs(Number(s) - seuil) < 1e-9);
  if (!k) throw new Error(`no cell at ${seuil} in the measured table.`);
  return table[k]!;
}

/** The two thresholds exactly as src/cribler.ts executer() measures them, and the held-out verdict rates at each. */
export function mesurerSeuils(f: { entrees: number; df: ReadonlyMap<string, number> }) {
  const bruts = entites.CHEMINS_APPRENTISSAGE.map((u) => {
    const b = entites.lireJeu(u);
    if (b === null) throw new Error(`training set ${u.pathname} missing in the tool.`);
    return b;
  });
  const apprentissage = entites.mesurerJeux(f, bruts);
  const brutReel = entites.lireJeu(entites.CHEMIN_APPRENTISSAGE_REEL);
  if (brutReel === null) throw new Error("the real training sample is missing in the tool.");
  const reel = entites.mesurerReel(f, brutReel);
  const reglage = entites.choisirSeuils(apprentissage.table, reel.table);
  const brutVerdict = entites.lireJeu(entites.CHEMIN_VERDICT);
  if (brutVerdict === null) throw new Error("the held-out verdict set is missing in the tool: the page would cite training rates only.");
  const verdict = entites.mesurerJeux(f, [brutVerdict]);
  const seuils = { fort: reglage.fort.seuil, possible: reglage.possible.seuil };
  return {
    ...seuils, tientLePlancher: reglage.tientLePlancher, rappelMin: entites.RAPPEL_MIN,
    verdict: { jeu: verdict.jeux[0]!, fort: cellule(verdict.table, seuils.fort), possible: cellule(verdict.table, seuils.possible) },
    apprentissageReel: { jeu: reel.jeux[0]!, fort: cellule(reel.table, seuils.fort), possible: cellule(reel.table, seuils.possible) },
  };
}

/* ─────────────────────────── the witness ─────────────────────────── */

/** The fixed set: written once from the shipped entries, then kept as a committed file. Every name is a company or a
 *  vessel of the lists, bent the way client files bend them (legal form, order, a letter, a number), plus names that
 *  match nothing. */
function ecrireTemoinSiAbsent(gardees: Entree[]): void {
  if (existsSync(TEMOIN_NOMS)) return;
  const lignes = ["name,ref,imo"];
  const pas = Math.floor(gardees.length / 24);
  const bends = [
    (n: string) => n, (n: string) => n.toLowerCase(), (n: string) => n.replace(/\bLTD\.?\b/i, "Limited").replace(/\bCO\.,?\b/i, "Company"),
    (n: string) => n.split(" ").reverse().join(" "), (n: string) => n.length > 6 ? n.slice(0, 3) + n.slice(4) : n,
    (n: string) => n + " Trading", (n: string) => n.replace(/\s+/g, "-"),
  ];
  let k = 0;
  for (let i = 0; i < gardees.length && lignes.length < 25; i += pas) {
    const e = gardees[i]!;
    const nom = bends[k++ % bends.length]!(e.n).replaceAll('"', "");
    lignes.push(`"${nom}","${e.s}-${e.id.replaceAll('"', "")}",${e.t === "vessel" && e.imo ? e.imo : ""}`);
  }
  for (const n of ["Totally Unrelated GmbH", "Boulangerie du Port", "Harbour Freight Forwarding Pte Ltd", "Hong Da 8", "Hong Da 1"]) lignes.push(`"${n}",,`);
  writeFileSync(TEMOIN_NOMS, lignes.join("\n") + "\n");
}

export type Attendu = { nom: string; statut: string; candidats: { source: string; ids: string[]; nomListe: string; alias?: string; score: number; par: string }[]; autres: number };

export function criblerTemoin(f: { entrees: number; df: ReadonlyMap<string, number> }, gardees: Entree[], seuils: { fort: number; possible: number }): Attendu[] {
  const index = new cribler.Index(f, gardees.map(versEntreeListe), seuils.possible);
  const { lignes } = cribler.lireContreparties(readFileSync(TEMOIN_NOMS, "utf8"));
  return lignes.map((c) => {
    const r = cribler.cribler(c, index, seuils);
    return { nom: c.nom, statut: r.statut, autres: r.autres,
      candidats: r.candidats.map((x) => ({ source: x.source, ids: x.ids, nomListe: x.nomListe, ...(x.alias ? { alias: x.alias } : {}), score: x.score, par: x.par })) };
  });
}

/* ─────────────────────────── the command ─────────────────────────── */

function jours(iso: string, maintenant: Date): number { return (maintenant.getTime() - new Date(iso).getTime()) / 86400000; }

export function verifierFraicheur(maintenant = new Date()): string[] {
  if (!existsSync(DONNEES)) return ["donnees.json is missing: run node source/essai-screening/construire.ts"];
  const d = JSON.parse(readFileSync(DONNEES, "utf8")) as { listes: { source: string; telechargeLe: string }[] };
  return d.listes.filter((l) => jours(l.telechargeLe, maintenant) > FRAICHEUR_JOURS)
    .map((l) => `${l.source}: downloaded ${l.telechargeLe.slice(0, 10)}, ${Math.floor(jours(l.telechargeLe, maintenant))} days ago, over ${FRAICHEUR_JOURS}`);
}

function principal(): void {
  const args = process.argv.slice(2);
  for (const a of args) if (!["--fetch", "--check"].includes(a)) { console.error(`unknown flag ${a}`); process.exit(2); }
  if (args.includes("--check")) {
    const rouges = verifierFraicheur();
    if (rouges.length) { console.error(`STALE DATA (over ${FRAICHEUR_JOURS} days):\n  ${rouges.join("\n  ")}\n  → node source/essai-screening/construire.ts --fetch, then the assembler`); process.exit(1); }
    console.log(`fresh: every covered list downloaded within ${FRAICHEUR_JOURS} days`);
    return;
  }
  if (args.includes("--fetch")) {
    console.log("fetching the lists with the tool (npm run listes -- --fetch)");
    execFileSync("npm", ["run", "listes", "--", "--fetch"], { cwd: MOTEUR, stdio: "inherit" });
  }
  const m = listes.lireManifeste(MOTEUR);
  if (!m) throw new Error("the tool has no listes-manifest.json: run with --fetch.");
  const { gardees, couvertes, exclues, homonymes } = extraire(m);
  const f = frequences.frequencesDesListes();
  const poids = tablePoids(f, gardees);
  const seuils = mesurerSeuils(f);
  ecrireTemoinSiAbsent(gardees);
  const attendu = criblerTemoin(f, gardees, seuils);
  const paquet = empaqueter(MOTEUR);
  writeFileSync(MOTEUR_JS, paquet.js);
  const donnees = {
    genereLe: new Date().toISOString(), moteur: { commit: paquet.commit, modules: paquet.modules.length, sha256: paquet.sha256 },
    fraicheurJours: FRAICHEUR_JOURS,
    /** how many lists the tool itself reads (its manifest): the page says "eight of the tool's ten lists", never a typed ten */
    listesDeLOutil: m.listes.filter((l) => l.disponible).length,
    listes: couvertes, exclues, retires: { personnesEtAutres: "every entry typed person or other", homonymesDePersonnes: homonymes },
    /** names where a list's em dash is written as a hyphen (the site serves none); the tool scores both alike */
    cadratinsRemplaces: cadratins,
    totaux: { entrees: gardees.length, societes: gardees.filter((e) => e.t === "entity").length, navires: gardees.filter((e) => e.t === "vessel").length },
    poids: { ...poids, table: frequences.TABLE_GELEE.fichier, sha256: frequences.TABLE_GELEE.sha256, compteeLe: frequences.TABLE_GELEE.compteeLe },
    seuils: { ...seuils, mesureLe: new Date().toISOString().slice(0, 10), commit: paquet.commit },
    /** the fixed set itself travels with the page: its self-check re-screens it in the browser and must get `attendu` */
    temoin: { fichier: "temoin-noms.csv", sha256: createHash("sha256").update(readFileSync(TEMOIN_NOMS)).digest("hex"),
      csv: readFileSync(TEMOIN_NOMS, "utf8"), attendu },
    entrees: gardees,
  };
  writeFileSync(DONNEES, JSON.stringify(donnees));
  const taille = (n: number) => `${(n / 1e6).toFixed(2)} MB`;
  console.log(`donnees.json: ${gardees.length} entries (${donnees.totaux.societes} companies, ${donnees.totaux.navires} vessels) from ${couvertes.map((c) => c.source).join(", ")}; `
    + `${exclues.length} source(s) left out; ${homonymes} dropped as a person's homonym; weights ${poids.df.length} in clear + ${poids.dfh.length} hashed; `
    + `thresholds strong ${seuils.fort}, possible ${seuils.possible}; ${taille(JSON.stringify(donnees).length)}`);
  console.log(`moteur.js: ${paquet.modules.length} modules at ${paquet.commit}, ${taille(paquet.js.length)}`);
  console.log(`witness: ${attendu.length} names, ${attendu.filter((a) => a.statut !== "no-match").length} with a candidate`);
}

if (process.argv[1] && process.argv[1].endsWith("construire.ts")) principal();
