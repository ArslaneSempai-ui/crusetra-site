// THE BROWSER WITNESS OF THE SELF-SERVE TEST (screening/try.html), on a real Chrome (CDP, port 9222, like the
// site's other witnesses). It loads the served page, then:
//   1. counts every network request after the load event: it must be zero (nothing typed leaves the page, and
//      nothing is fetched afterwards); with TEMOIN_REQUETE=1 it plants one same-origin image request after load,
//      and the witness must then go red, or its zero is worth nothing;
//   2. reads the page's policy: connect-src 'none' and the worker allowance, and no uncaught exception;
//   3. waits for the page's own self-check line (the page re-screens its fixed set in the worker);
//   4. independently: pastes the fixed set into the field, runs it through the page's own button, reads the rendered
//      results from the DOM and compares statuses, candidates and scores with what the tool computed
//      (donnees.json, temoin.attendu), order of equal scores aside.
// usage: node temoin-navigateur.mjs <url of screening/try.html>     exit 0 green, 1 red, 2 witness broken
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";

const url = process.argv[2];
if (!url) { console.error("usage: node temoin-navigateur.mjs <url>"); process.exit(2); }
const ICI = dirname(new URL(import.meta.url).pathname);
const D = JSON.parse(readFileSync(join(ICI, "donnees.json"), "utf8"));
const planter = process.env.TEMOIN_REQUETE === "1";

const t = await fetch("http://127.0.0.1:9222/json/new?about:blank", { method: "PUT" }).then((r) => r.json());
const ws = new WebSocket(t.webSocketDebuggerUrl);
let id = 0; const pend = new Map(); const ecoute = [];
const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); }
  else if (d.method) for (const f of ecoute) f(d.method, d.params);
};
await new Promise((r) => (ws.onopen = r));
await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable"); await send("Network.setCacheDisabled", { cacheDisabled: true });

let charge = false; const apres = []; const exceptions = [];
ecoute.push((m, p) => {
  if (m === "Page.loadEventFired") charge = true;
  if (m === "Network.requestWillBeSent" && charge) apres.push(p.request.url);
  if (m === "Runtime.exceptionThrown") exceptions.push(p.exceptionDetails.text + " " + (p.exceptionDetails.exception?.description ?? ""));
});
const evaluer = async (expression) => (await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true })).result.value;
const attendre = async (expression, delaiMs, quoi) => {
  const fin = Date.now() + delaiMs;
  while (Date.now() < fin) { if (await evaluer(expression)) return; await new Promise((r) => setTimeout(r, 250)); }
  throw new Error(`timed out waiting for ${quoi}`);
};

const fautes = [];
try {
  await send("Page.navigate", { url });
  await attendre("document.readyState === 'complete'", 30000, "the page to load");
  charge = true;
  const politique = (await evaluer(`document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content`)) ?? "";
  if (!politique.includes("connect-src 'none'")) fautes.push("the policy does not forbid connections (connect-src 'none')");
  if (!politique.includes("worker-src blob:")) fautes.push("the policy does not allow the page's own worker (worker-src blob:)");
  if (planter) await evaluer(`new Promise((r) => { const i = new Image(); i.onload = i.onerror = () => r(1); i.src = "../favicon-32.png?temoin=" + Date.now(); })`);

  // 3. the page's own self-check
  await attendre(`!/waiting|checking/.test(document.getElementById("tm-preuve").textContent)`, 120000, "the self-check");
  const preuve = await evaluer(`document.getElementById("tm-preuve").textContent`);
  if (!preuve.includes("passed")) fautes.push(`the page's self-check did not pass: ${preuve}`);

  // 4. the fixed set, through the page's own field and button, read back from the DOM
  await evaluer(`(() => { const z = document.getElementById("e-noms"); z.value = ${JSON.stringify(D.temoin.csv)}; document.getElementById("e-lancer").click(); return 1; })()`);
  await attendre(`/screened|Stopped|could not/.test(document.getElementById("e-etat").textContent)`, 120000, "the run to finish");
  const etat = await evaluer(`document.getElementById("e-etat").textContent`);
  const rendus = await evaluer(`[...document.querySelectorAll("#e-resultats > li")].map((li) => ({
    statut: li.querySelector(".e-pill").textContent.trim(), nom: li.querySelector(".e-nom").textContent,
    candidats: [...li.querySelectorAll(".e-cands > li")].map((c) => ({ source: c.querySelector(".e-src").textContent, nomListe: c.querySelector(".e-liste").textContent, score: Number(c.querySelector(".e-score").textContent) })),
    autres: (li.querySelector(".e-note") && li.querySelector(".e-note").textContent.match(/and (\\d+) more/) || [0, 0])[1] * 1 }))`);
  const attendu = D.temoin.attendu;
  if (rendus.length !== attendu.length) fautes.push(`${rendus.length} results rendered for ${attendu.length} fixed names (${etat})`);
  const cle = (r) => JSON.stringify(r.candidats.map((c) => [c.source, c.nomListe, Math.round(c.score * 1000)]).sort((a, b) => b[2] - a[2] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0) || (a[1] < b[1] ? -1 : 1)));
  attendu.forEach((a, i) => {
    const r = rendus[i]; if (!r) return;
    const statut = a.statut === "no-match" ? "no candidate" : a.statut;
    if (r.statut !== statut) fautes.push(`${a.nom}: status ${r.statut} on the page, ${a.statut} for the tool`);
    if (cle(r) !== cle(a)) fautes.push(`${a.nom}: candidates differ: page ${cle(r)} tool ${cle(a)}`);
    if (Number(r.autres) !== a.autres) fautes.push(`${a.nom}: ${r.autres} more on the page, ${a.autres} for the tool`);
  });

  // 1. nothing left the page: the only requests the browser may send after load are the page's own icons, declared in
  //    its head (<link rel="icon">), which Chrome fetches once the document is loaded; anything else is a fault
  await new Promise((r) => setTimeout(r, 1500));
  const icones = await evaluer(`[...document.querySelectorAll('link[rel="icon"]')].map((l) => l.href)`);
  const etrangeres = apres.filter((u) => !icones.includes(u));
  if (etrangeres.length) fautes.push(`${etrangeres.length} request(s) after load: ${etrangeres.slice(0, 3).join(", ")}`);
  if (exceptions.length) fautes.push(`${exceptions.length} uncaught exception(s): ${exceptions[0].slice(0, 200)}`);
  console.log(`self-check: ${preuve}`);
  console.log(`run: ${etat.replace(/\s+/g, " ").trim()}`);
} catch (e) {
  fautes.push(`witness broken: ${e.message}`);
  ws.close(); await fetch(`http://127.0.0.1:9222/json/close/${t.id}`);
  console.log(fautes.join("\n")); process.exit(2);
}
ws.close(); await fetch(`http://127.0.0.1:9222/json/close/${t.id}`);
if (planter) {
  const vu = fautes.some((f) => f.includes("request(s) after load"));
  console.log(vu ? "planted request seen: the witness can say no" : "PLANTED REQUEST NOT SEEN: the witness is blind");
  process.exit(vu ? 0 : 2);
}
if (fautes.length) { console.log("RED\n  " + fautes.join("\n  ")); process.exit(1); }
console.log(`GREEN: no request after load, policy held, ${D.temoin.attendu.length} fixed names match the tool's record on the page`);
