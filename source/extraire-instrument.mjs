/**
 * Les briques de l'instrument, calculées par L'OUTIL, jamais recopiées.
 *
 * Ce script importe le code de cascade (assumptions.ts, la constante du relevé de
 * référence) et le relevé gelé, puis émet instrument-donnees.json : le prix et la
 * justesse de chaque cellule palier x champ, tels que l'outil les facture.
 *
 * Deux témoins avant d'émettre : recomposer le routage PUBLIÉ avec ces briques doit
 * reproduire son coût et sa justesse du landing.json. Sinon, refus : une page qui
 * calculerait à côté de l'outil vaudrait moins que pas de page.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { depot } from "./depots.mjs";

const OUTIL = depot("routing");
const ICI = fileURLToPath(new URL(".", import.meta.url));

const { ASSUMPTIONS, pricePerThousandExtractions } = await import(join(OUTIL, "src", "assumptions.ts"));
const { RELEVE_DE_REFERENCE } = await import(join(OUTIL, "src", "measure.ts"));

const profil = JSON.parse(readFileSync(join(OUTIL, RELEVE_DE_REFERENCE), "utf8"));
const landing = JSON.parse(readFileSync(join(OUTIL, "landing.json"), "utf8"));

const FIELDS = landing.fields;
const TIERS = landing.tiers.map((t) => t.id);

/* la brique : $ pour 1000 extractions de CE champ par CE palier, à la latence gelée */
const price = {};
const acc = {};
for (const t of TIERS) {
  price[t] = {}; acc[t] = {};
  for (const f of FIELDS) {
    const cell = profil.extraction[t]?.[f];
    if (t === "human") {
      price[t][f] = pricePerThousandExtractions(t, ASSUMPTIONS);
      acc[t][f] = ASSUMPTIONS.humanAccuracy * 100;
    } else {
      if (!cell) throw new Error(`the reference record carries no ${t}/${f} cell`);
      price[t][f] = pricePerThousandExtractions(t, ASSUMPTIONS, cell.latency);
      const officielle = landing.tiers.find((x) => x.id === t).acc[f].accuracy;
      const relue = cell.accuracy * 100;
      if (Math.abs(officielle - relue) > 0.06) {
        throw new Error(`accuracy diverges on ${t}/${f}: landing ${officielle} vs record ${relue}`);
      }
      acc[t][f] = officielle;
    }
  }
}

/* témoin 1 : le coût du routage publié, recomposé brique à brique */
const publie = landing.routing;
const coutRecompose = FIELDS.reduce((s, f) => s + price[publie.fields[f]][f], 0);
/* le landing publie un arrondi à 4 décimales ; le point scellé de exposition.json
   (190.6581124999987 / 100) confirme la recomposition exacte : tolérance = l'arrondi */
if (Math.abs(coutRecompose - publie.costPerThousandDocuments) > 1e-4) {
  throw new Error(`témoin coût : recomposé ${coutRecompose} vs publié ${publie.costPerThousandDocuments}`);
}
/* témoin 2 : sa justesse moyenne par champ */
const justesseRecomposee = FIELDS.reduce((s, f) => s + acc[publie.fields[f]][f], 0) / FIELDS.length;
if (Math.abs(justesseRecomposee - publie.accuracy) > 0.05) {
  throw new Error(`témoin justesse : recomposée ${justesseRecomposee} vs publiée ${publie.accuracy}`);
}

/* le routage visé fichier, publié par la trouvaille 02 : name passe de large à gen-4b */
const vise = { ...publie.fields, name: "gen-4b" };
const coutVise = FIELDS.reduce((s, f) => s + price[vise[f]][f], 0);

writeFileSync(join(ICI, "instrument-donnees.json"), JSON.stringify({
  provenance: {
    profil: RELEVE_DE_REFERENCE,
    landingMeasuredAt: landing.generatedFrom.measuredAt,
    commit: landing.generatedFrom.commit,
    note: "prices computed by the tool's own pricePerThousandExtractions at the frozen per-field latencies; accuracies from landing.json; human tier assumed until measured with measure:humans",
  },
  fields: FIELDS,
  tiers: TIERS,
  price, acc,
  humanAccuracy: ASSUMPTIONS.humanAccuracy * 100,
  assumed: {
    pricePerThousandSmall: ASSUMPTIONS.pricePerThousandSmall,
    pricePerThousandLarge: ASSUMPTIONS.pricePerThousandLarge,
    machineHourlyCost: ASSUMPTIONS.machineHourlyCost,
  },
  publie: { routage: publie.fields, cout: publie.costPerThousandDocuments, justesse: publie.accuracy },
  vise: { routage: vise, cout: coutVise },
}, null, 1));
console.log(`instrument-donnees.json : ${TIERS.length} paliers x ${FIELDS.length} champs, `
  + `témoins verts (publié ${coutRecompose.toFixed(4)} $/1000 docs, ${justesseRecomposee.toFixed(1)} %)`);
