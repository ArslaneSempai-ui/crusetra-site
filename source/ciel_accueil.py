"""THE NIGHT SKY OVER THE HOME (Arslane, 25/10): concept A "dive" of the chief's maquettes-accueil.py, built into the
real home. The home opens on the HUB's night sky (its base still, the aurora, the planets with no captions, the lit
robot, the Earth) with the Crusetra wordmark and one headline; as the visitor scrolls, the camera dives onto the Earth
through three veils and the dive ends in the home hero's own night, the home below unchanged.

Only the home carries it (batir_accueil in batir-hero.py); a deep link (a #fragment in the address) never shows it:
the head script marks the page "sans-ciel" before anything paints, and the sky is not displayed, nothing of it loads.
Nothing is computed in 3D: every picture is a HUB render (source/ciel/, made lighter by preparer-ciel.py), the motion
is CSS transforms driven by the scroll, the stars are a 2D canvas. First paint waits for no video: the loops start
after the load event, when the browser is idle, and stop once the sky has scrolled away. Under prefers-reduced-motion
the sky is one still screen (no loop, no travel, no twinkle) and the site follows.
Headline (Arslane: title 1, all white, « Blanc lumineux »): the three verbs carry a soft glow in the light of the
robot's lit visor, #f3fbf8, the mean of its brightest pixels (measured 25/10 on nuit-robot-eveil-fixe.webp).
"""
import json, pathlib, re

ICI = pathlib.Path(__file__).resolve().parent
CIEL = ICI / "ciel"
PREFIX = "ciel/"
BOX = json.loads((CIEL / "boites.json").read_text()); BOX.pop("_note", None)
LAYERS = ["ciel", "jupiter", "saturne", "neptune", "uranus", "mars", "lune", "station", "robot", "terre"]  # bottom to top
LOOPS = ["jupiter", "saturne", "neptune", "uranus", "mars", "lune", "station"]
FICHIERS = (["nuit-base-fixe.webp", "nuit-robot-eveil-fixe.webp"] + [f"nuit-{l}-fixe.webp" for l in LAYERS if l != "robot"]
            + [f"nuit-{l}.webm" for l in LOOPS])
for _f in FICHIERS:
    if not (CIEL / _f).exists():
        raise SystemExit(f"the home sky misses source/ciel/{_f}: run preparer-ciel.py")
TITRE = ('Compliance decisions you can <b>test</b>, <b>reproduce</b> and <b>inspect</b>.')
VISIERE = "#f3fbf8"

def _dims(f):
    b = (CIEL / f).read_bytes()
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", f
    if b[12:16] == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    if b[12:16] == b"VP8 ":
        return int.from_bytes(b[26:28], "little") & 0x3fff, int.from_bytes(b[28:30], "little") & 0x3fff
    n = int.from_bytes(b[21:25], "little")
    return (n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1

def _layer(l):
    x, y, w, h = BOX[l]
    src = "nuit-robot-eveil-fixe.webp" if l == "robot" else f"nuit-{l}-fixe.webp"
    fw, fh = _dims(src)   # the HUB's box and its still agree within a pixel or two (Moon: 60x63 in a 60x62 box)
    assert abs(fw - w) <= 2 and abs(fh - h) <= 2, f"{src}: {fw}x{fh} is not its box {w}x{h}"
    vid = '<video class="cl-v" preload="none" muted playsinline loop hidden></video>' if l in LOOPS else ""
    return (f'<div class="cl-lay cl-{l}" data-l="{l}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<img src="{PREFIX}{src}" alt=""{' fetchpriority="high"' if l == "robot" else ''} width="{fw}" height="{fh}" decoding="async">{vid}</div>')

def ciel_html(logo_svg):
    svg = logo_svg.replace("<svg ", '<svg class="cl-logo-svg" aria-hidden="true" focusable="false" ', 1)
    assert svg.count("cl-logo-svg") == 1 and 'id="' not in svg
    bw, bh = _dims("nuit-base-fixe.webp")
    return f'''<section class="cl" aria-label="Crusetra">
  <div class="cl-piste"><div class="cl-etage">
    <div class="cl-monde" aria-hidden="true">
      <img class="cl-base" src="{PREFIX}nuit-base-fixe.webp" alt="" width="{bw}" height="{bh}" fetchpriority="high" decoding="async">
      <canvas class="cl-etoiles"></canvas>
      {"".join(_layer(l) for l in LAYERS)}
    </div>
    <div class="cl-voiles" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="cl-voile" aria-hidden="true"></div>
    <div class="cl-scrim" aria-hidden="true"></div>
    <div class="cl-pied" aria-hidden="true"></div>
    <div class="cl-texte">
      <div class="cl-logo" role="img" aria-label="Crusetra">{svg}</div>
      <h2 class="cl-titre">{TITRE}</h2>
    </div>
    <div class="cl-cue" aria-hidden="true"><i class="cl-fil"><b></b></i><span>Scroll</span></div>
  </div></div>
</section>'''

def tete_chargement():
    """The head of the home for a fast first paint: the two @font-face sheets inline (no render-blocking stylesheet; the
    urls are rewritten to resolve from the site root), the two woff2 the first screen uses (latin Literata, Roboto Mono)
    and the two pictures it needs first (the sky base, the lit robot) preloaded. Other pages keep linking the sheets."""
    css = ""
    for nom in ("literata.css", "roboto-mono.css"):
        t = (ICI / "fontes" / nom).read_text()
        assert "url(fontes/" not in t, nom   # the sheets hold bare file names
        css += t.replace("url(", "url(fontes/")
        assert "\u2014" not in css
    lat = "fontes/literata-02.woff2"   # the latin range of Literata: the only Literata file the first screen fetches
    for f in (lat, "fontes/roboto-mono.woff2"):
        assert (ICI / f).exists(), f
    return (f'<style>{css}</style>\n'
            f'<link rel="preload" href="{lat}" as="font" type="font/woff2" crossorigin>\n'
            f'<link rel="preload" href="fontes/roboto-mono.woff2" as="font" type="font/woff2" crossorigin>\n'
            f'<link rel="preload" href="{PREFIX}nuit-base-fixe.webp" as="image" type="image/webp" fetchpriority="high">\n'
            f'<link rel="preload" href="{PREFIX}nuit-robot-eveil-fixe.webp" as="image" type="image/webp" fetchpriority="high">')

# the hero's night, where the dive ends: the Earth fades into it and the hero starts from it (no band between)
_FIN = "var(--nuit-b)"
CSS_CIEL = f"""
  /* ===== the night sky over the home (ciel_accueil.py) ===== */
  html:not(.cl-vol) .cl{{display:none}}   /* a deep link, no script, or a copy of the page: the site at once */
  html.cl-vol .barre .marque{{opacity:0}}
  .cl{{position:relative;z-index:0;background:#04050a;color:#f5f8f7}}
  .cl-piste{{position:relative;height:100vh}}
  .cl-etage{{position:sticky;top:0;height:100vh;overflow:hidden;background:#04050a;contain:strict}}
  .cl-etage.cl-loin{{visibility:hidden}}
  /* the stage stays hidden (the night under it stays) until the base and the robot have decoded, then one short fade in
     (JS_CIEL sets cl-pret; JS_TETE sets it anyway after a timeout, so the sky can never stay hidden) */
  html.cl-vol .cl-etage{{transition:opacity .3s ease-out}}
  html.cl-vol:not(.cl-pret) .cl-etage{{opacity:0}}
  .cl-monde{{position:absolute;left:0;top:0;width:2400px;height:2200px;transform-origin:0 0;will-change:transform}}
  .cl-base{{position:absolute;left:0;top:0;width:2400px;height:2200px;max-width:none}}
  .cl-etoiles{{position:absolute;left:0;top:-800px;width:2400px;height:3800px;pointer-events:none}}
  .cl-lay{{position:absolute;transform-origin:50% 50%;will-change:transform}}
  .cl-lay img{{width:100%;height:100%;max-width:none;display:block}}
  .cl-lay video{{position:absolute;inset:0;width:100%;height:100%;display:block}}
  .cl-lay video[hidden]{{display:none}}
  .cl-ciel{{mix-blend-mode:plus-lighter}}
  /* the plate's top edge shows on narrow screens (the plate hangs from the bottom there): it fades into the night */
  @media (max-width:699px){{.cl-base,.cl-ciel img{{-webkit-mask-image:linear-gradient(transparent,#000 12%);mask-image:linear-gradient(transparent,#000 12%)}}}}
  .cl-pied{{display:none}}
  .cl-terre img{{-webkit-mask-image:linear-gradient(#000 58%,transparent 92%);mask-image:linear-gradient(#000 58%,transparent 92%)}}
  .cl-voiles{{position:absolute;inset:0;pointer-events:none;overflow:hidden}}
  .cl-voiles i{{position:absolute;left:38%;top:50%;width:130vw;height:52vh;margin:-26vh 0 0 -65vw;border-radius:50%;opacity:0;will-change:transform,opacity;
    background:radial-gradient(closest-side,rgba(188,210,255,.72),rgba(130,168,235,.28) 55%,transparent)}}
  .cl-voiles i:nth-child(2){{left:64%;width:150vw;height:58vh;margin:-29vh 0 0 -75vw;background:radial-gradient(closest-side,rgba(214,228,255,.66),rgba(130,168,235,.24) 60%,transparent)}}
  .cl-voiles i:nth-child(3){{left:50%;width:190vw;height:66vh;margin:-33vh 0 0 -95vw;background:radial-gradient(closest-side,rgba(228,236,223,.5),color-mix(in srgb,{_FIN} 75%,transparent) 70%,transparent)}}
  .cl-voile{{position:absolute;inset:0;pointer-events:none;opacity:0;will-change:opacity;
    background:linear-gradient(to bottom,transparent 22%,color-mix(in srgb,{_FIN} 85%,transparent) 60%,{_FIN} 80%)}}
  /* the bar reads on the bright aurora: a night scrim under it while the sky is behind */
  .cl-scrim{{position:absolute;left:0;right:0;top:0;height:150px;pointer-events:none;
    background:linear-gradient(to bottom,rgba(4,5,12,.72),rgba(4,5,12,.34) 60%,transparent)}}
  html.cl-vol .barre.sur-nuit nav a{{color:#e6e9f0}}
  html.cl-vol .barre.sur-nuit nav a:hover{{color:#fff}}
  /* the hero rises over the dive's last 60vh: the Earth fades straight into it, no empty screen, no band */
  html.cl-vol main{{position:relative;z-index:1;margin-top:-60vh}}
  html.cl-vol main::before{{content:"";position:absolute;left:0;right:0;top:-200px;height:200px;pointer-events:none;
    background:linear-gradient(to bottom,transparent,color-mix(in srgb,{_FIN} 55%,transparent) 55%,{_FIN})}}
  html.cl-vol main .hero{{background:linear-gradient(to bottom,{_FIN},transparent 260px),
    radial-gradient(120% 90% at 30% -10%,color-mix(in srgb,var(--vert-titre) 34%,#0e0e11),var(--nuit-b) 65%)}}
  .cl-texte{{position:absolute;left:48px;top:92px;max-width:min(50vw,800px);will-change:opacity}}
  .cl-logo{{display:block;color:#f5f8f7;transform-origin:0 0;will-change:transform}}
  .cl-logo-svg{{display:block;height:56px;width:auto}}
  .cl-titre{{margin:26px 0 0;font:600 clamp(40px,4.3vw,64px)/1.04 var(--texte);letter-spacing:-.025em;color:#f5f8f7;max-width:17ch;text-wrap:balance}}
  /* the aurora runs behind the words: a soft night under them keeps the white at 4.5:1 or more on its brightest part
     (measured 25/10 on the served page: 3.2:1 without it); it fades with the title */
  .cl-titre{{position:relative}}
  .cl-titre::before{{content:"";position:absolute;z-index:-1;inset:-90px -22% -200px -120px;pointer-events:none;
    background:radial-gradient(closest-side,rgba(4,6,16,.62),rgba(4,6,16,.44) 55%,rgba(4,6,16,.16) 82%,transparent)}}
  /* « Blanc lumineux »: the three verbs in the light of the robot's lit visor, a glow and no colour */
  .cl-titre b{{font-weight:inherit;color:#fff;text-shadow:0 0 2px color-mix(in srgb,{VISIERE} 70%,transparent),
    0 0 14px color-mix(in srgb,{VISIERE} 55%,transparent),0 0 34px color-mix(in srgb,{VISIERE} 28%,transparent)}}
  /* the scroll cue (Arslane, 25/10: « mieux fait »): centred at the foot of the first screen, a hairline down which a
     point of the visor's light glides, eased, every 1.6 s; the word under it, quiet; gone in the first 5% of the dive */
  .cl-cue{{position:absolute;left:50%;bottom:26px;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:11px;
    pointer-events:none;will-change:opacity}}
  .cl-fil{{position:relative;display:block;width:1px;height:46px;
    background:linear-gradient(transparent,color-mix(in srgb,{VISIERE} 38%,transparent) 25%,color-mix(in srgb,{VISIERE} 38%,transparent) 75%,transparent)}}
  .cl-fil b{{position:absolute;left:-2px;top:0;width:5px;height:5px;border-radius:50%;background:{VISIERE};
    box-shadow:0 0 6px {VISIERE},0 0 14px color-mix(in srgb,{VISIERE} 60%,transparent);animation:cl-glisse 1.6s cubic-bezier(.65,0,.35,1) infinite}}
  @keyframes cl-glisse{{0%{{transform:translateY(0);opacity:0}}18%{{opacity:1}}78%{{opacity:1}}100%{{transform:translateY(41px);opacity:0}}}}
  .cl-cue span{{font:500 10.5px/1 var(--mono);letter-spacing:.22em;text-transform:uppercase;color:{VISIERE};opacity:.62;padding-left:.22em}}
  @media (max-width:700px){{
    .cl-texte{{left:20px;right:20px;top:76px;max-width:none}}
    .cl-logo-svg{{height:38px}}.cl-titre::before{{inset:-170px -20px -150px -20px;background:linear-gradient(rgba(4,6,16,.5),rgba(4,6,16,.5) 62%,transparent)}}.cl-titre{{font-size:36px;margin-top:16px;max-width:none}}.cl-cue{{bottom:20px}}
  }}
  @media (prefers-reduced-motion:reduce){{
    html.cl-vol .cl-etage{{transition:none}}
    html.cl-vol main{{margin-top:0}}html.cl-vol main::before{{content:none}}
    .cl-fil b{{animation:none;transform:translateY(20px);opacity:1}}
    /* the still sky ends in the hero's night too: its last quarter fades into it, no edge */
    .cl-pied{{display:block;position:absolute;left:0;right:0;bottom:0;height:30vh;pointer-events:none;background:linear-gradient(transparent,{_FIN})}}
  }}
"""

# before anything paints: a deep link never gets the sky; otherwise the bar's mark waits for the flying logo
# the safety net: whatever happens to the main script or to an image, the sky shows 3 s after the navigation began
JS_TETE = ('var H=document.documentElement;H.classList.add(location.hash.length > 1 ? "sans-ciel" : "cl-vol");'
           'setTimeout(function(){H.classList.add("cl-pret")},Math.max(300,3000-performance.now()))')

JS_CIEL = r"""
(function () {
  const H = document.documentElement, sec = document.querySelector(".cl");
  if (!sec || !H.classList.contains("cl-vol")) return;
  const RED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ASSETS = "__PREFIX__", BOX = __BOX__, LOOPS = __LOOPS__;
  const BARRE = document.querySelector(".barre"), MARQUE = BARRE.querySelector(".marque");
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), lerp = (a, b, t) => a + (b - a) * t;
  const seg = (p, a, b) => clamp((p - a) / (b - a), 0, 1), easeOut = t => 1 - Math.pow(1 - t, 3), easeIn = t => t * t * t,
    easeInOut = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  // the frame: wide windows show the plate's band y 450..1550; narrow ones hang the plate from the bottom, centred on the robot
  function cadre() {
    const vw = innerWidth, vh = innerHeight;
    if (vw >= 700) { const s = Math.max(vw / 2400, vh / 1100); return { s, ox: vw / 2 - 1000 * s, oy: -450 * s, vw, vh }; }
    const s = vw / 1250; return { s, ox: vw / 2 - 1295 * s, oy: vh - 2200 * s, vw, vh };
  }
  function etoiles(cv) {  // 170 fixed points, drawn at ~11 fps; the base already carries the HUB's stars, these only twinkle
    const dpr = matchMedia("(min-resolution: 1.5dppx)").matches ? 1.5 : 1, W = 1200, Hh = 1900; cv.width = W * dpr; cv.height = Hh * dpr;
    const g = cv.getContext("2d"), pts = []; g.scale(dpr, dpr);
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < 170; i++) pts.push([rnd() * W, rnd() * Hh, .6 + rnd() * 1.2, rnd() * 6.28, .6 + rnd() * 1.4]);
    let last = -1;
    return (t) => { if (t - last < 90) return; last = t; g.clearRect(0, 0, W, Hh); g.fillStyle = "#e8eefc";
      for (const [x, y, r, ph, w] of pts) { g.globalAlpha = .25 + .75 * Math.abs(Math.sin(t / 1000 * w + ph)); g.beginPath(); g.arc(x, y, r, 0, 6.28); g.fill(); }
      g.globalAlpha = 1; };
  }
  const C = { piste: sec.querySelector(".cl-piste"), etage: sec.querySelector(".cl-etage"), monde: sec.querySelector(".cl-monde"), lay: {},
    voiles: [...sec.querySelectorAll(".cl-voiles i")], voile: sec.querySelector(".cl-voile"), logo: sec.querySelector(".cl-logo"),
    lede: sec.querySelector(".cl-titre"), cue: sec.querySelector(".cl-cue"), cv: sec.querySelector(".cl-etoiles") };
  for (const e of sec.querySelectorAll(".cl-lay")) C.lay[e.dataset.l] = e;
  const twinkle = RED ? () => {} : etoiles(C.cv);
  if (RED) C.cv.style.display = "none";
  let F = cadre(), M = null;
  // the loops: after the load event, when idle; a VP9 alpha the browser cannot draw (Safari paints it black) keeps the still
  const videos = [];
  function joue(v, l) {
    v.src = ASSETS + "nuit-" + l + ".webm"; videos.push(v);
    v.addEventListener("playing", () => { try {  // the box's corner pixel, at the video's own size (a 4 px thumbnail blended the planet into the corner: 6 of 7 failed)
      const c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight; const g = c.getContext("2d", { willReadFrequently: true });
      g.drawImage(v, 0, 0); if (g.getImageData(0, 0, 1, 1).data[3] !== 0) { v.pause(); v.removeAttribute("src"); v.load(); return; } v.hidden = false; } catch (e) {} }, { once: true });
    v.play().catch(() => {});
  }
  let enVue = true;
  let lances = false;
  function lancerBoucles() { if (RED || lances || !enVue) return; lances = true;
    // one decoder at a time, a quarter second apart: seven starting together cost a 133 ms frame once (measured 25/10)
    LOOPS.forEach((l, i) => setTimeout(() => { const v = C.lay[l] && C.lay[l].querySelector("video"), im = C.lay[l] && C.lay[l].querySelector("img"); if (!enVue) { lances = false; return; }
      if (v && !v.getAttribute("src") && im && im.complete && im.naturalWidth > 0) joue(v, l); }, i * 250)); }
  const auRepos = () => (window.requestIdleCallback ? requestIdleCallback(lancerBoucles, { timeout: 2500 }) : setTimeout(lancerBoucles, 1200));
  // the stills first (none is lazy: they are the first screen), the sky shows once they have decoded (the base and the robot
  // first of all), then the loops start, each one only if its own still is there
  const imgs = [...sec.querySelectorAll("img")];
  const decodees = imgs.map(i => i.decode ? i.decode().catch(() => {}) : new Promise(r => { if (i.complete) r(); else { i.addEventListener("load", r, { once: true }); i.addEventListener("error", r, { once: true }); } }));
  const montrer = () => H.classList.add("cl-pret");
  Promise.all(decodees).then(() => { montrer(); if (document.readyState === "complete") auRepos(); else addEventListener("load", auRepos, { once: true }); });
  const pose = (dx, dy, z, ax, ay) => { const { s, ox, oy } = F; const S = s * z, X = ox + ax * s - ax * S + dx * S, Y = oy + ay * s - ay * S + dy * S;
    C.monde.style.transform = `translate(${X.toFixed(1)}px,${Y.toFixed(1)}px) scale(${S.toFixed(5)})`; };
  const posLay = (l, dx, dy, sc) => { C.lay[l].style.transform = `translate(${dx.toFixed(1)}px,${dy.toFixed(1)}px) scale(${sc.toFixed(5)})`; };
  // the big logo flies into the bar's own mark (q 0 -> 1); until then the bar's mark is hidden
  const logoVol = (q) => { if (RED) q = q >= .5 ? 1 : 0;
    if (q >= 1) { MARQUE.style.opacity = "1"; C.logo.style.opacity = "0"; return; }
    MARQUE.style.opacity = "0"; C.logo.style.opacity = "1";
    if (q <= 0) { C.logo.style.transform = ""; return; }
    if (!M) { C.logo.style.transform = ""; const r = MARQUE.querySelector("svg").getBoundingClientRect(), b = C.logo.querySelector("svg").getBoundingClientRect();
      M = { k: r.height / b.height, dx: r.left - b.left, dy: r.top - b.top }; }
    const t = easeInOut(q); C.logo.style.transform = `translate(${(M.dx * t).toFixed(1)}px,${(M.dy * t).toFixed(1)}px) scale(${lerp(1, M.k, t).toFixed(4)})`; };
  const ANCH = [1900, 1460];  // the dive aims at the Earth, right of the robot: he slides out to the left as we pass him
  const EXTRA = { neptune: .55, jupiter: .8, saturne: 1.15, uranus: 1.0, lune: 1.35, mars: 1.4, station: 1.5, robot: 1.0, terre: 1.0, ciel: .7 };
  let T = 0, FIN = 0;
  function mesurer() { F = cadre(); M = null; T = RED ? 0 : Math.round(F.vh * 1.5); C.piste.style.height = (F.vh + T) + "px";
    FIN = RED ? 0 : T + Math.round(F.vh * .4); window.__finCiel = FIN; }
  // the bar stays on the night until the site has arrived; registered after the site's own handler, so it has the last word
  const barre = () => { const y = scrollY; BARRE.classList.toggle("posee", y > FIN + 40); BARRE.classList.toggle("sur-nuit", y <= FIN + 40); };
  addEventListener("scroll", barre, { passive: true });
  function frame(y) {
    const loin = y > FIN + F.vh * .7;   // the sky is covered by the site: stop compositing and drawing it, pause the loops
    C.etage.classList.toggle("cl-loin", loin);
    if (loin !== !enVue) { enVue = !loin; for (const v of videos) { if (loin) v.pause(); else if (v.getAttribute("src")) v.play().catch(() => {}); } if (enVue) lancerBoucles(); }
    C.cue.style.opacity = 1 - seg(y, 0, Math.max(1, (T || F.vh) * .05));   // the cue leaves in the first 5% of the dive
    logoVol(RED ? seg(y, F.vh * .3, F.vh * .3 + 1) : seg(T ? clamp(y / T, 0, 1) : 0, .22, .46));
    if (loin) return;
    const p = T ? clamp(y / T, 0, 1) : 0, z = 1 + 2.1 * easeIn(p);
    pose(0, 0, z, ANCH[0], ANCH[1]);
    for (const l in C.lay) { const [x, y0, w, h] = BOX[l], cx = x + w / 2, cy = y0 + h / 2, m = 1 + EXTRA[l] * (z - 1) / z;
      posLay(l, (cx - ANCH[0]) * (m - 1) + (l === "robot" ? -620 * easeOut(p) : 0), (cy - ANCH[1]) * (m - 1) + (l === "robot" ? 260 * p : 0), m); }
    C.cv.style.opacity = 1 - seg(p, .25, .6);
    for (let i = 0; i < 3; i++) { const a = [.30, .46, .62][i], q = seg(p, a, a + .38), v = C.voiles[i];
      v.style.opacity = q <= 0 || q >= 1 ? 0 : Math.sin(q * Math.PI) * (i === 2 ? 1 : .9); v.style.transform = `translateY(${(95 - 200 * q).toFixed(1)}vh) scale(${(1 + 1.2 * q).toFixed(3)})`; }
    C.voile.style.opacity = seg(p, .42, .8);
    C.lede.style.opacity = 1 - seg(p, 0, .18);
  }
  // one rAF loop: the pose is recomputed only when the scroll or the window changed; the stars twinkle on their own clock
  let dirty = true, calme = 0;   // the stars rest while the page moves: redrawing their canvas under a scroll costs frames
  // the loops rest too while the page moves: seven alpha decoders under the dive cost one frame in twenty (p95 33 ms
  // against 18 ms with them paused, headed Chrome 155, 1470 px, measured 25/10); they resume 350 ms after the scroll stops
  let reprise = 0;
  const reposer = () => { for (const v of videos) if (!v.paused) v.pause(); clearTimeout(reprise);
    reprise = setTimeout(() => { if (enVue) for (const v of videos) if (v.getAttribute("src")) v.play().catch(() => {}); }, 350); };
  addEventListener("scroll", () => { dirty = true; calme = performance.now() + 220; reposer(); }, { passive: true });
  addEventListener("resize", () => { mesurer(); barre(); dirty = true; }, { passive: true });
  mesurer(); frame(scrollY); barre();
  const tick = (t) => { if (dirty) { dirty = false; frame(scrollY); } if (enVue && t > calme) twinkle(t); requestAnimationFrame(tick); };
  if (!RED) requestAnimationFrame(tick);
  else addEventListener("scroll", () => frame(scrollY), { passive: true });
})();
""".replace("__PREFIX__", PREFIX).replace("__BOX__", json.dumps({l: BOX[l] for l in LAYERS}, separators=(",", ":"))).replace("__LOOPS__", json.dumps(LOOPS))

for _t in (CSS_CIEL, JS_CIEL, TITRE):
    assert "\u2014" not in _t and "\u2026" not in _t
