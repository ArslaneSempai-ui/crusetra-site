/**
 * Les briques de l'instrument LAPIS, calculées par L'OUTIL, jamais recopiées.
 *
 * Copie adaptée de l'extracteur rouge (même contrat, mêmes refus) ; la seule règle
 * qui change : la cellule recommandée PEUT ÊTRE ABSENTE (aucune cellule ne tient le
 * plancher sur les cas écrits, et le relevé le dit) : ce n'est pas un refus, c'est
 * un fait à afficher — « none holds the floor », avec la plus forte borne.
 *
 * Ce script importe le code de cascade-screening (le registre des matchers, la grille de
 * seuils, l'intervalle de Wilson, le scellé) et lit son relevé public releve-public.json.
 * Il émet instrument-monitoring-donnees.json : pour chaque palier présent, la grille des
 * 51 seuils, rappel et fausses alertes avec n et bornes, sur les paires étiquetées ET la
 * moitié synthétique ; les paliers absents ; la provenance ; et la cellule que la règle
 * d'optimise retiendrait sous un rappel exigé de 0,90 à la borne BASSE.
 *
 * Trois refus avant d'émettre, parce qu'une page qui calculerait à côté de l'outil vaudrait
 * moins que pas de page :
 *   1. le scellé du relevé ne se vérifie pas : rien ne part d'un relevé retouché ;
 *   2. les paliers du relevé ne sont pas ceux du registre : la page décrirait un outil
 *      qui n'existe plus ;
 *   3. la recomposition : chaque cellule témoin (tous les paliers, trois seuils, les deux
 *      métriques, les deux moitiés) est recalculée avec le rate() de l'outil depuis ses
 *      comptes bruts, et doit reproduire taux, borne basse et borne haute à l'identique.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { depot } from "./depots.mjs";

const OUTIL = depot("monitoring");
const ICI = fileURLToPath(new URL(".", import.meta.url));

const { scelleIntact } = await import(join(OUTIL, "src", "empreinte.ts"));
const { rate } = await import(join(OUTIL, "src", "interval.ts"));
const { SEUILS, PALIERS } = await import(join(OUTIL, "src", "scenario.ts"));
// registreComplet : les sept paliers quand les poids de l'embedding sont là (le relevé
// public est mesuré avec) ; registre() reste les six qu'un client mesure sans réchauffer
const { registre } = await import(join(OUTIL, "src", "scenarios", "index.ts"));

const releve = JSON.parse(readFileSync(join(OUTIL, "releve-public.json"), "utf8"));

/* refus 1 : le scellé, avant toute lecture de chiffre */
if (!scelleIntact(releve)) {
  throw new Error("releve-public.json no longer matches its seal: nothing is emitted from a record that moved after sealing.");
}

/* refus 2 : les paliers du relevé sont ceux du registre, dans les deux sens */
const r = registre();
const duRegistre = [...r.keys()];
const duReleve = releve.paliers.presents;
if (JSON.stringify(duRegistre) !== JSON.stringify(duReleve)) {
  throw new Error(`the registry's scenarios (${duRegistre.join(", ")}) are not the record's (${duReleve.join(", ")}): the page would describe a tool that no longer exists. Re-run npm run measure -- --yes-overwrite in the tool.`);
}

/* refus 3 : la recomposition, cellule par cellule témoin */
const SEUILS_TEMOINS = ["0.50", "0.90", "1.00"];
let recomposees = 0;
for (const [nomMoitie, moitie] of [["authored", releve.authored], ["synthetic", releve.synthetic]]) {
  if ("absent" in moitie) continue;
  for (const [palier, grille] of Object.entries(moitie.tables)) {
    for (const seuil of SEUILS_TEMOINS) {
      for (const metrique of ["rappel", "fauxPositifs"]) {
        const c = grille[seuil][metrique];
        const relu = rate(c.succes, c.n);
        for (const [cle, attendu, recompose] of [
          ["taux", c.taux, relu.rate], ["bas", c.bas, relu.low], ["haut", c.haut, relu.high],
        ]) {
          if (attendu !== recompose) {
            throw new Error(`recomposition witness: ${nomMoitie}/${palier}/${seuil}/${metrique}.${cle} is ${attendu} in the record, ${recompose} recomposed by the tool's rate(${c.succes}, ${c.n}). This page can no longer redo the record's arithmetic: nothing is emitted.`);
          }
        }
        recomposees++;
      }
    }
  }
}
if (recomposees < duReleve.length * SEUILS_TEMOINS.length * 2) {
  throw new Error(`${recomposees} witness cell(s) recomposed: fewer than the labelled half alone (${duReleve.length * SEUILS_TEMOINS.length * 2}). The witness did not cover what it claims.`);
}

/*
 * La cellule recommandée sous un rappel exigé, à la borne BASSE : la même lecture de la
 * grille que l'outil (le point ne suffit jamais, optimise.ts filtre sur rappel.low). La
 * règle, déclarée : parmi les cellules dont la borne basse du rappel tient le plancher,
 * le moins de fausses alertes d'abord, puis le palier le moins cher (rang), puis le seuil
 * le plus haut. Elle est émise avec la cellule, et la page la réapplique à l'ouverture.
 */
export function celluleRecommandee(tables, ordreDesRangs, plancher) {
  const candidates = [];
  for (const [palier, grille] of Object.entries(tables)) {
    for (const [seuil, c] of Object.entries(grille)) {
      if (c.rappel.bas >= plancher) {
        candidates.push({ palier, seuil: Number(seuil), rang: ordreDesRangs[palier], rappel: c.rappel, fauxPositifs: c.fauxPositifs });
      }
    }
  }
  candidates.sort((a, b) => a.fauxPositifs.taux - b.fauxPositifs.taux || a.rang - b.rang || b.seuil - a.seuil);
  return candidates[0] ?? null;
}

const PLANCHER = 0.90;
const rangs = Object.fromEntries([...r.values()].map((m) => [m.id, m.rang]));
const retenue = celluleRecommandee(releve.authored.tables, rangs, PLANCHER);
/* Sur les cas écrits du bleu, AUCUNE cellule ne tient 0,90 à la borne basse : le relevé
   le dit, la page doit le dire, pas le taire ni planter. La plus forte borne accompagne
   l'absence, pour que la page nomme ce qui est atteignable. */
const plusForteBorne = Math.max(...Object.values(releve.authored.tables)
  .flatMap((g) => Object.values(g).map((c) => c.rappel.bas)));
const recommandee = retenue !== null
  ? { plancher: PLANCHER, ...retenue }
  : { plancher: PLANCHER, absente: true, plusForteBorne };

const sortie = {
  provenance: {
    releve: "releve-public.json",
    empreinte: releve.empreinte,
    commit: releve.commit,
    date: releve.date,
    note: "every figure below comes from the sealed public record of crusetra-monitoring, recomposed with the tool's own rate() before this file was allowed to exist; the recommended cell applies the tool's rule: recall LOWER BOUND holds the floor, then fewest false alerts, then the cheaper scenario, then the higher threshold",
  },
  seuils: SEUILS,
  seuilsMontres: [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00],
  paliers: [...r.values()].map((m) => ({ id: m.id, description: m.description, rang: m.rang })),
  absents: PALIERS.filter((p) => !r.has(p)),
  authored: {
    nSuspicious: releve.authored.nSuspicious,
    nBenign: releve.authored.nBenign,
    natures: releve.authored.natures,
    grille: releve.authored.tables,
  },
  synthetic: "absent" in releve.synthetic
    ? { absent: releve.synthetic.absent }
    : { nSuspicious: releve.synthetic.nSuspicious, nBenign: releve.synthetic.nBenign, grille: releve.synthetic.tables },
  recommandee,
};

writeFileSync(join(ICI, "instrument-monitoring-donnees.json"), JSON.stringify(sortie, null, 1) + "\n");
console.log(`instrument-monitoring-donnees.json: ${duReleve.length} scenario(s), ${SEUILS.length} thresholds, `
  + `${recomposees} witness cell(s) recomposed, seal ${releve.empreinte} (commit ${releve.commit}).`);
console.log(recommandee.absente
  ? `no cell holds recall >= ${PLANCHER} at the lower bound on the written cases (strongest bound ${(recommandee.plusForteBorne * 100).toFixed(0)} %): said, not silenced.`
  : `recommended under recall >= ${PLANCHER} (lower bound): ${recommandee.palier} at threshold ${recommandee.seuil.toFixed(2)}.`);
