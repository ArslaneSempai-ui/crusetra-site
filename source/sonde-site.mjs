// Sonde de débord horizontal : pages × largeurs, via CDP natif (jamais une capture
// étroite : headless recadre sous ~500 px et fait mentir l'image ; le scrollWidth, lui,
// ne ment pas). Portée du scratchpad du chef (9/09) avec deux duretés :
//   - PAGES est OBLIGATOIRE (la liste vient de docs/, jamais recopiée d'un vieux script :
//     la liste codée en dur avait 17 pages quand le site en servait 29) ;
//   - un chargement jamais signalé est un DÉFAUT dit (« INDÉTERMINÉ »), pas une page
//     sondée en plein bâti qui rendrait un zéro sans valeur.
// usage: PAGES=a.html,b/index.html [PORT=8802] node sonde-site.mjs
// Chrome doit tourner avec --remote-debugging-port=9222.
if (!process.env.PAGES) {
  console.error("PAGES absent : le banc ne devine pas la liste des pages — la lire de docs/ "
    + "(find . -name '*.html'), une liste recopiée vieillit sans le dire.");
  process.exit(2);
}
const PAGES = process.env.PAGES.split(",");
const LARGEURS = [320, 375, 500, 641, 768, 900, 1024, 1081, 1150, 1280, 1440, 1680];
// LE DEUXIÈME AXE, ET POURQUOI IL A FALLU LE CASSER POUR L'AJOUTER.
//
// Le 13 septembre 2026, des attributs width/height posés sur les images ont fait rendre les
// vignettes du rail à 1083 px de haut au lieu de 39 : le rail est passé de 618 à 5896 px et
// a peint PAR-DESSUS le rideau, puis sur toute la hauteur du site. Ce banc était vert. Il
// mesurait 348 combinaisons de LARGEUR et refusait le débord HORIZONTAL ; le défaut était
// vertical, et un élément 5000 px trop haut est passé devant lui sans un mot.
//
// La règle : un élément ne peint pas hors de SA section. Le seuil n'est pas deviné, il est
// MESURÉ des deux côtés : sur le site sain, 14 sortes d'éléments débordent, toutes entre 13
// et 115 px (les robots qui se penchent hors de leur cadre, les cellules d'un tableau qui
// défile) ; le défaut du 13/09 en faisait 2478. La borne est à 200 px, loin des deux, et le
// banc DIT le maximum observé à chaque passage pour qu'une dérive se voie avant de casser.
const HORS_SECTION = 200;
// LES DOCUMENTS À TAILLE FIXE (10/10/2026). Une page sans <meta name="viewport"> est posée par un
// téléphone sur 980 px puis réduite à l'écran, comme un PDF : pas de débord, on zoome. Le banc la
// mesurait en mode bureau (mobile: false) à 320 px et criait « DEBORD +496px » là où aucun
// téléphone n'en montre (vérifié sur crusetra.com en émulation mobile : 980 de mise en page,
// échelle 0,38, scrollWidth = innerWidth). Ces pages-là sont mesurées COMME UN TÉLÉPHONE, sous
// 1024 px. La liste est fermée et chaque entrée dit pourquoi : toute AUTRE page servie sans
// viewport est un défaut (« SANS-VIEWPORT »), parce qu'une page du site doit se lire sur un
// téléphone sans zoom.
const DOCUMENTS_FIXES = {
  "rapports/routing-sample-report.html": "page signée au format lettre (verifier-rapport.mjs) : la modifier casse sa signature",
};
const A_UN_VIEWPORT = `!!document.querySelector('meta[name="viewport"]')`;
const PROBE = `JSON.stringify((()=>{const w=innerWidth,d=document.documentElement;
const o={ov:d.scrollWidth-w,bad:[],haut:0,hors:[]};
for(const s of document.querySelectorAll('main > section, main > nav, body > section, body > nav, body > footer, body > header')){
  const rs=s.getBoundingClientRect(),ha=rs.top+scrollY,ba=rs.bottom+scrollY;
  for(const el of s.querySelectorAll('*')){
    const c=getComputedStyle(el);
    if(c.display==='none'||c.visibility==='hidden'||c.position==='fixed')continue;
    const r=el.getBoundingClientRect();
    if(!r.height)continue;
    const dep=Math.round(Math.max(ha-(r.top+scrollY),(r.bottom+scrollY)-ba));
    if(dep>o.haut)o.haut=dep;
    if(dep>${HORS_SECTION}&&o.hors.length<5)o.hors.push(((el.className||el.tagName).toString().split(' ')[0]).slice(0,28)
      +' dépasse de '+dep+'px (h='+Math.round(r.height)+') hors '+((s.className||s.tagName).toString().split(' ')[0]).slice(0,20));
  }
}
if(o.ov>1){for(const el of document.querySelectorAll('body *')){
  const r=el.getBoundingClientRect();
  if(r.width>2&&(r.right>w+1||r.left<-1)){
    let p=el.parentElement,c=false;
    while(p){const s=getComputedStyle(p);
      if(/(auto|scroll|hidden|clip)/.test(s.overflowX)){c=true;break}p=p.parentElement}
    if(!c){o.bad.push((el.className||el.tagName).toString().slice(0,30)
      +':'+Math.round(r.left)+'..'+Math.round(r.right));if(o.bad.length>4)break}}}}
return o})())`;

const target = await fetch("http://127.0.0.1:9222/json/new?about:blank", { method: "PUT" }).then((r) => r.json());
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pend = new Map();
const events = [];
const send = (method, params = {}) => new Promise((res, rej) => {
  const mid = ++id;
  pend.set(mid, { res, rej });
  ws.send(JSON.stringify({ id: mid, method, params }));
});
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pend.has(d.id)) { const p = pend.get(d.id); pend.delete(d.id); d.error ? p.rej(new Error(JSON.stringify(d.error))) : p.res(d.result); }
  else if (d.method) events.push(d.method);
};
await new Promise((r) => { ws.onopen = r; });
await send("Page.enable");
await send("Runtime.enable");
await send("Network.enable");
await send("Network.setCacheDisabled", { cacheDisabled: true });

// LE TÉMOIN TOURNE D'ABORD, sur deux pages fabriquées : l'une porte exactement le défaut du
// 13/09 (un <img> avec width/height et une règle qui ne fixe que la largeur, donc la hauteur
// naturelle gagne), l'autre la même page avec `img{height:auto}`. Si la sonde ne voit plus la
// première, ou refuse la seconde, elle ne rend RIEN : un zéro sans témoin ne prouve rien, et
// c'est précisément un banc vert qui a laissé passer ce défaut en production.
const PIXEL = "data:image/gif;base64,R0lGODlhZABkAIAAAP///wAAACH5BAEAAAAALAAAAABkAGQAAAIrhI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKBwUAOw==";
const temoin = (avecRegle) => "data:text/html," + encodeURIComponent(
  "<!doctype html><meta charset=utf-8><style>*{margin:0}"
  + (avecRegle ? "img{height:auto}" : "")
  + ".v{width:60px;aspect-ratio:1.42/1}section{height:400px;overflow:visible}</style>"
  + "<main><section><img class=v width=1600 height=1152 src='" + PIXEL + "'></section></main>");
for (const [avecRegle, doitVoir] of [[false, true], [true, false]]) {
  await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await send("Page.navigate", { url: temoin(avecRegle) });
  await new Promise((r) => setTimeout(r, 400));
  const o = JSON.parse((await send("Runtime.evaluate", { expression: PROBE, returnByValue: true })).result.value);
  const vu = o.hors.length > 0;
  if (vu !== doitVoir) {
    console.error(`GARDE CASSÉE : sur la page témoin ${avecRegle ? "SAINE" : "FAUTIVE"}, la sonde `
      + `${vu ? "a vu" : "n'a rien vu"} (dépassement max ${o.haut}px).\n`
      + "  La sonde du deuxième axe ne mesure plus ce qu'elle annonce ; son zéro ne vaudrait rien.");
    process.exit(2);
  }
}
// le témoin du viewport : la page témoin n'en a pas, la même avec la balise en a un ; et un document
// sans viewport, mesuré en téléphone à 320 px, doit être posé sur 980 (sinon l'émulation ne fait pas
// ce que le banc lui prête, et la mesure des documents ne vaudrait rien)
for (const [html, attendu] of [[temoin(true), false], [temoin(true).replace(encodeURIComponent("<meta charset=utf-8>"),
    encodeURIComponent('<meta charset=utf-8><meta name="viewport" content="width=device-width,initial-scale=1">')), true]]) {
  await send("Page.navigate", { url: html });
  await new Promise((r) => setTimeout(r, 300));
  if ((await send("Runtime.evaluate", { expression: A_UN_VIEWPORT, returnByValue: true })).result.value !== attendu) {
    console.error(`GARDE CASSÉE : la détection du viewport ne distingue plus une page ${attendu ? "qui en a un" : "sans"}.`);
    process.exit(2);
  }
}
await send("Emulation.setDeviceMetricsOverride", { width: 320, height: 900, deviceScaleFactor: 1, mobile: true });
await send("Page.navigate", { url: temoin(true) });
await new Promise((r) => setTimeout(r, 300));
const _l = (await send("Runtime.evaluate", { expression: "innerWidth", returnByValue: true })).result.value;
if (_l !== 980) {
  console.error(`GARDE CASSÉE : en téléphone à 320 px, une page sans viewport est posée sur ${_l} px et non 980 ; `
    + "les documents à taille fixe ne seraient plus mesurés comme un téléphone les montre.");
  process.exit(2);
}

let defauts = 0;
let hautMax = 0;
for (const page of PAGES) {
  for (const larg of LARGEURS) {
    const telephone = page in DOCUMENTS_FIXES && larg < 1024;
    await send("Emulation.setDeviceMetricsOverride", { width: larg, height: 900, deviceScaleFactor: 1, mobile: telephone });
    events.length = 0;
    await send("Page.navigate", { url: `http://127.0.0.1:${process.env.PORT || 8802}/${page}` });
    const charge = await new Promise((r) => {
      const t = setInterval(() => { if (events.includes("Page.loadEventFired")) { clearInterval(t); r(true); } }, 30);
      setTimeout(() => { clearInterval(t); r(false); }, 6000);
    });
    if (!charge) {
      defauts++;
      console.log(`INDÉTERMINÉ ${page} @${larg} : chargement jamais signalé en 6 s — rien de sondé, dit`);
      continue;
    }
    await new Promise((r) => setTimeout(r, 250));
    const res = await send("Runtime.evaluate", { expression: PROBE, returnByValue: true });
    const o = JSON.parse(res.result.value);
    if (larg === LARGEURS[0]) {
      const vp = (await send("Runtime.evaluate", { expression: A_UN_VIEWPORT, returnByValue: true })).result.value;
      if (!vp && !(page in DOCUMENTS_FIXES)) { defauts++; console.log(`SANS-VIEWPORT ${page} : pas de <meta name="viewport"> ; un téléphone la montre réduite, illisible sans zoom`); }
      if (vp && page in DOCUMENTS_FIXES) console.log(`note ${page} : a maintenant un viewport, l'entrée de DOCUMENTS_FIXES peut partir`);
    }
    if (o.ov > 1) { defauts++; console.log(`DEBORD ${page} @${larg} : +${o.ov}px ${o.bad.join(" | ")}`); }
    if (o.haut > hautMax) hautMax = o.haut;
    if (o.hors.length) { defauts++; console.log(`HORS-SECTION ${page} @${larg} : ${o.hors.join(" | ")}`); }
  }
  console.log(`ok ${page} (${LARGEURS.length} largeurs${page in DOCUMENTS_FIXES ? ", mesurée comme un téléphone sous 1024 px : " + DOCUMENTS_FIXES[page] : ""})`);
}
console.log(defauts ? `${defauts} DÉFAUTS`
  : `ZÉRO débord sur ${PAGES.length * LARGEURS.length} combos, dans les DEUX axes `
    + `(hors-section maximum observé : ${hautMax}px, borne ${HORS_SECTION}px)`);
ws.close();
await fetch(`http://127.0.0.1:9222/json/close/${target.id}`);
process.exit(defauts ? 1 : 0);
