/**
 * Les briques de l'instrument ONYX, calculées par L'OUTIL, jamais recopiées.
 *
 * L'onyx n'a ni palier ni seuil : son relevé public est le Dossier de la suite —
 * quatre questions (routing, screening, monitoring, scoring) contre les cinq
 * contrôles du contrat, l'état atteint SANS TROU, la couverture, les réglages.
 * L'instrument montre cette table en direct ; ce script la vérifie avant.
 *
 * Trois refus avant d'émettre, parce qu'une page qui calculerait à côté de l'outil
 * vaudrait moins que pas de page :
 *   1. le scellé du relevé ne se vérifie pas : rien ne part d'un relevé retouché ;
 *   2. les contrôles du relevé ne sont pas ceux du contrat de l'outil (ordre compris) :
 *      la page décrirait un outil qui n'existe plus ;
 *   3. la recomposition : l'état de chaque question présente est refait depuis SES
 *      verdicts par la règle du contrat (le plus haut contrôle tenu sans trou), la
 *      couverture est recomptée depuis les questions ; un désaccord et rien ne part.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { depot } from "./depots.mjs";

const OUTIL = depot("dossier");
const ICI = fileURLToPath(new URL(".", import.meta.url));

const { scelleIntact } = await import(join(OUTIL, "src", "empreinte.ts"));
const { CONTROLES } = await import(join(OUTIL, "src", "controle.ts"));

const releve = JSON.parse(readFileSync(join(OUTIL, "releve-public.json"), "utf8"));

/* refus 1 : le scellé, avant toute lecture de chiffre */
if (!scelleIntact(releve)) {
  throw new Error("releve-public.json no longer matches its seal: nothing is emitted from a record that moved after sealing.");
}

/* refus 2 : les contrôles du relevé sont ceux du contrat, dans l'ordre */
if (JSON.stringify(releve.controles.presents) !== JSON.stringify(CONTROLES)) {
  throw new Error(`the record's controls (${releve.controles.presents.join(", ")}) are not the contract's `
    + `(${CONTROLES.join(", ")}): the page would describe a tool that no longer exists. `
    + `Re-run npm run measure -- --yes-overwrite in the tool.`);
}

/* refus 3 : la recomposition — l'état de chaque question, et la couverture */
let recomposes = 0;
for (const [nom, q] of Object.entries(releve.questions)) {
  if (!q.present) continue;
  const tenu = Object.fromEntries(q.verdicts.map((v) => [v.controle, v.tenu]));
  let etat = "none";
  for (const c of CONTROLES) {
    if (!(c in tenu) || !tenu[c]) break;
    etat = c;
  }
  if (etat !== q.etat) {
    throw new Error(`recomposition witness: question ${nom} reads state "${q.etat}" in the record, `
      + `"${etat}" recomposed from its own verdicts by the contract's no-gap rule. `
      + `This page can no longer redo the record's arithmetic: nothing is emitted.`);
  }
  recomposes++;
}
const nPresentes = Object.values(releve.questions).filter((q) => q.present).length;
if (nPresentes !== releve.couverture.n || Object.keys(releve.questions).length !== releve.couverture.sur) {
  throw new Error(`recomposition witness: coverage reads ${releve.couverture.n}/${releve.couverture.sur} `
    + `in the record, ${nPresentes}/${Object.keys(releve.questions).length} recounted from the questions.`);
}
if (recomposes < 1 || recomposes !== nPresentes) {
  throw new Error(`${recomposes} state(s) recomposed for ${nPresentes} present question(s): the witness did not cover what it claims.`);
}

const sortie = {
  provenance: {
    releve: "releve-public.json",
    empreinte: releve.empreinte,
    commit: releve.commit,
    date: releve.date,
    note: "every line below comes from the sealed public dossier of crusetra-dossier: each question's state was recomposed from its own verdicts by the contract's no-gap rule, and the coverage recounted, before this file was allowed to exist",
  },
  controles: releve.controles,
  questions: releve.questions,
  couverture: releve.couverture,
  reglages: releve.reglages,
};

/* Le fichier de données reprend les verdicts TELS QUE LE RELEVÉ SCELLÉ les écrit,
   cadratins compris (4 aujourd'hui) : une trace intermédiaire fidèle au sceau, comme
   les ancres de citations. Il n'est JAMAIS servi — le bâtisseur assainit la typographie
   au moment d'embarquer, et la garde de l'assembleur tient la frontière de docs/
   (aucun U+2014, brut ou échappé, quel que soit le fichier). */
writeFileSync(join(ICI, "instrument-dossier-donnees.json"), JSON.stringify(sortie, null, 1) + "\n");
console.log(`instrument-dossier-donnees.json: ${Object.keys(releve.questions).length} question(s), `
  + `${CONTROLES.length} controls, ${recomposes} state(s) recomposed, coverage ${releve.couverture.n}/${releve.couverture.sur}, `
  + `seal ${releve.empreinte} (commit ${releve.commit}).`);
