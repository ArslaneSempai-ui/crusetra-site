// LE TÉMOIN DE L'EFFONDREMENT (30/09) : sur téléphone, les fiches des trouvailles des pages d'outil
// mesuraient 46 px de large, un mot par ligne, EN LIGNE depuis des semaines sans qu'aucune garde le dise :
// le banc des tailles mesure le débord horizontal, pas un bloc écrasé. Cause : en dépliage (≤ 1080 px) la
// colonne .colle centre ses enfants (align-items:center) et .scenes est un conteneur de taille
// (container-type:inline-size), dont la largeur naturelle est nulle : .theatre, .scenes et .scene tombent
// à 0 px, et la fiche (width:100%) se réduit à son plus long mot.
// Règle : à chaque largeur, tout bloc de texte visible d'au moins QUINZE mots (un paragraphe ; les puces du rail en font moins) doit faire au moins 45 % de la
// largeur de l'écran (et 150 px). usage: node temoin-effondrement.mjs <url>…   (Chrome sur 9222)
// code 1 si un bloc est écrasé ; TEMOIN_EFFONDRE=1 plante une fiche écrasée : le témoin doit rougir.
const urls = process.argv.slice(2);
// 1000 and 1060 are the widths where the two-column sample-sheet grid squeezed its text column (11 October 2026)
const largeurs = (process.env.TEMOIN_LARGEURS || "375,768,1000,1060").split(",").map(Number);
const mesure = async (url, w) => {
  const t = await fetch("http://127.0.0.1:9222/json/new?about:blank", {method: "PUT"}).then(r => r.json());
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const pend = new Map();
  const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, {res, rej}); ws.send(JSON.stringify({id: i, method: m, params: p})); });
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); } };
  await new Promise(r => ws.onopen = r);
  // Network.enable first, as the other probes do: without it the cache switch is ignored and a rebuilt page is read from the cache
  await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable"); await send("Network.setCacheDisabled", {cacheDisabled: true});
  await send("Emulation.setDeviceMetricsOverride", {width: w, height: 812, deviceScaleFactor: 1, mobile: w < 700});
  await send("Page.navigate", {url});
  await new Promise(r => setTimeout(r, 2500));
  const planter = process.env.TEMOIN_EFFONDRE ? `const f=document.querySelector('.scene .fiche')||document.querySelector('main p'); if(f){f.style.cssText+=';width:46px!important;display:block';}` : "";
  const r = await send("Runtime.evaluate", {returnByValue: true, expression: `(()=>{${planter}
    const W = innerWidth, seuil = Math.max(150, 0.45 * W), out = [];
    for (const el of document.querySelectorAll('main p, main li, main h1, main h2, main h3, main .fiche')) {
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const txt = (el.innerText || '').trim(); const mots = txt.split(/\\s+/).filter(Boolean).length;
      const rw = el.getBoundingClientRect().width; if (!rw || mots < 15) continue;
      let cache = false; for (let a = el; a; a = a.parentElement) { const s = getComputedStyle(a); if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') { cache = true; break; } }
      if (cache) continue;
      if (rw < seuil) out.push({w: Math.round(rw), mots, classe: el.className || el.tagName, debut: txt.slice(0, 50)});
    }
    return out; })()`});
  ws.close(); await fetch(`http://127.0.0.1:9222/json/close/${t.id}`);
  return r.result.value;
};
let fautes = 0;
for (const url of urls) for (const w of largeurs) {
  const ecrases = await mesure(url, w);
  if (ecrases.length) { fautes += ecrases.length; console.log(`ÉCRASÉ ${url} @${w}px : ${ecrases.length} bloc(s), ex. ${JSON.stringify(ecrases.slice(0, 2))}`); }
}
console.log(fautes ? `effondrement : ${fautes} bloc(s) écrasé(s)` : `effondrement : aucun bloc écrasé sur ${urls.length} page(s) × ${largeurs.length} largeurs`);
process.exit(fautes ? 1 : 0);
