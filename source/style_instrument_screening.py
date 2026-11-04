"""The look of the red instrument page (screening/instrument.html), read by its builder and by the self-serve test
page (batir-essai-screening.py), which keeps the same look and adds one terminal. Moved here on 4 November 2026 from
batir-instrument-screening.py, unchanged."""

CSS = '''
  :root{--nuit-a:#33191f;--nuit-b:#241217;--nuit-c:#180b0f;
    --sur:#efe0e2;--sur-pale:#c0a6ab;
    --papier:#dbd7c5;--papier-haut:#e2ddcb;--encre:#1b1d18;--demi:#4a4739;--pale:#55523f;
    --filet-clair:#bab7a0;
    --accent-titre:#7a1f2e;--accent-vif:#d64a5c;--accent-clair:#ffc2c9;
    --texte:"Literata",Georgia,serif;--mono:"Roboto Mono",ui-monospace,Menlo,monospace;
    --montee:cubic-bezier(.16,.84,.32,1)}
  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth;caret-color:var(--accent-vif);
    scrollbar-color:var(--accent-titre) var(--nuit-c)}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{background:var(--nuit-b);color:var(--sur);font-family:var(--texte);line-height:1.55}
  img{max-width:100%;height:auto;display:block}
  ::selection{background:var(--accent-vif);color:var(--nuit-c)}
  a{text-underline-offset:4px;color:inherit}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  :focus-visible{outline:3px solid var(--accent-vif);outline-offset:3px;border-radius:2px}
  .colonne{max-width:1240px;margin:0 auto;padding:0 48px}

  .barre{position:absolute;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;gap:28px;
    padding:14px 32px}
  .marque{font-weight:700;font-size:19px;letter-spacing:.01em;text-decoration:none;color:var(--sur)}
  .marque small{font-weight:500;color:var(--accent-clair)}
  .barre nav{display:flex;gap:16px;margin-left:auto}
  .barre nav a{font-size:14.5px;text-decoration:none;color:var(--sur-pale);padding:13px 6px}
  .barre nav a:hover{color:var(--sur);text-decoration:underline;
    text-decoration-color:var(--accent-vif);text-decoration-thickness:1.5px}
  .barre nav a[aria-current]{color:var(--sur)}

  .tete{padding:192px 0 30px;
    background:radial-gradient(120% 100% at 50% -20%,#26101a,var(--nuit-b) 70%)}
  .h1{font-size:clamp(36px,4.6vw,62px);font-weight:600;letter-spacing:-.02em;line-height:1.05;
    text-wrap:balance;max-width:18ch}
  .lede{font-size:clamp(15px,1.25vw,18px);color:var(--sur-pale);max-width:52ch;
    line-height:1.6;margin-top:16px;text-wrap:balance}
  .lede b{color:var(--sur)}

  /* le poste : le robot rubis penche derriere le bord du terminal, coupe net */
  .poste{position:relative;padding:44px 0 64px}
  .dessus{position:relative;width:min(100%,1020px);margin:0 auto}
  /* height:auto : les attributs width/height de l'img fixaient une hauteur de 765 px pour
     une largeur CSS de 340 px : le robot était ÉTIRÉ et sa tête passait sous le terminal
     (Arslane, 6/09 : « le robot sur le tableau est bug ») */
  .rb{position:absolute;right:30px;top:-312px;width:340px;height:auto;z-index:2;pointer-events:none;
    filter:drop-shadow(0 26px 44px rgba(0,0,0,.55))}
  .terminal{position:relative;z-index:3;
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-b) 55%,#000),color-mix(in srgb,var(--nuit-c) 92%,#000) 120px);
    border:1px solid color-mix(in srgb,var(--accent-vif) 30%,transparent);border-radius:14px;
    box-shadow:0 60px 140px rgba(0,0,0,.7),0 0 0 1px rgba(0,0,0,.4),
      inset 0 1px 0 color-mix(in srgb,var(--accent-clair) 22%,transparent);overflow:hidden}
  .terminal::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:14px;
    background:repeating-linear-gradient(to bottom,rgba(255,194,201,.016) 0 1px,transparent 1px 3px)}
  .caret{display:inline-block;width:7px;height:14px;vertical-align:-2px;background:var(--accent-clair);
    margin-left:6px;animation:caret 1.1s steps(1) infinite}
  @keyframes caret{50%{opacity:0}}
  .t-page-halo{position:absolute;left:50%;top:52%;width:min(1100px,92vw);height:min(700px,70vw);
    transform:translate(-50%,-50%);pointer-events:none;
    background:radial-gradient(50% 50% at 50% 50%,color-mix(in srgb,var(--accent-vif) 12%,transparent),transparent 70%)}
  .tm-barre{display:flex;align-items:center;gap:8px;padding:11px 16px;
    background:linear-gradient(180deg,color-mix(in srgb,var(--nuit-a) 55%,#000),color-mix(in srgb,var(--nuit-b) 75%,#000));
    border-bottom:1px solid color-mix(in srgb,var(--sur-pale) 14%,transparent)}
  .tm-barre i{width:10px;height:10px;border-radius:50%;
    background:color-mix(in srgb,var(--sur-pale) 30%,transparent)}
  .tm-barre i:first-child{background:var(--accent-vif);
    box-shadow:0 0 8px color-mix(in srgb,var(--accent-vif) 70%,transparent)}
  .tm-barre span{margin-left:6px;font-family:var(--mono);font-size:12px;color:var(--sur-pale)}
  .tm-corps{padding:22px 26px 26px;font-family:var(--mono);font-size:13.5px}
  .tm-l{color:var(--sur-pale);margin:0 0 10px}
  .tm-l .ps{color:var(--accent-vif)}
  .tm-sortie{color:var(--sur);margin:2px 0 14px;line-height:1.7}
  .tm-sortie b{color:var(--accent-clair);font-weight:500}
  .tm-preuve{font-size:12.5px;color:var(--sur-pale);line-height:1.7}
  .tm-preuve .ok{color:var(--accent-vif)}
  .tm-preuve .ko{color:#ff7b6e;font-weight:700}
  .regl{font-family:var(--mono);font-size:12.5px;background:transparent;
    border:1px solid color-mix(in srgb,var(--accent-vif) 40%,transparent);
    border-radius:8px;padding:8px 13px;cursor:pointer;color:var(--accent-clair)}
  .regl:hover{border-color:var(--accent-vif)}
  .regl.actif{background:var(--accent-vif);color:var(--nuit-c);border-color:var(--accent-vif)}
  .regls{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 14px}

  .t-scroll{overflow-x:auto;margin:6px 0 16px}
  table.grille{border-collapse:collapse;font-family:var(--mono);font-size:12.5px;min-width:760px}
  .grille caption{text-align:left}
  .grille th{color:var(--sur-pale);font-weight:500;padding:7px 9px;text-align:left;white-space:nowrap}
  .grille td{padding:0;border:1px solid color-mix(in srgb,var(--sur-pale) 12%,transparent)}
  .grille tr.absent td{padding:10px 12px;color:var(--sur-pale);font-size:12px;font-style:italic}
  .cell{display:flex;flex-direction:column;gap:2px;width:100%;padding:8px 10px;background:transparent;
    border:0;cursor:pointer;font:inherit;color:var(--sur);text-align:left}
  .cell:hover{background:color-mix(in srgb,var(--accent-vif) 12%,transparent);
    box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--accent-vif) 55%,transparent)}
  .cell[aria-pressed="true"]{background:color-mix(in srgb,var(--accent-vif) 18%,transparent);
    color:var(--accent-clair);box-shadow:inset 0 0 0 1.5px var(--accent-vif)}
  .c-rappel{font-size:13px}
  .c-fp{font-size:11px;color:var(--sur-pale)}
  .cell[aria-pressed="true"] .c-fp{color:var(--accent-clair)}

  .b-curseur{flex:1;min-width:280px}
  input[type=range]{width:100%;accent-color:var(--accent-vif)}
  .b-ligne{display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:4px 0 8px}
  .b-val{font-family:var(--mono);font-size:13px;color:var(--accent-clair);min-width:64px}
  .b-lecture{min-height:44px}
  .b-rout{display:block;margin-top:6px;font-size:12px;color:var(--sur-pale)}

  /* le bas de page : le PARCHEMIN de la maison, comme l'instrument vert (Arslane,
     6/09 : « trop de rouge : la partie what this rests on doit être en crème et rouge,
     le petit terminal peut rester rouge ») ; la nuit rubis reste au héros et au poste */
  .basse{background:var(--papier);color:var(--encre);padding:64px 0 70px}
  .basse h2{font-size:clamp(22px,2.4vw,32px);font-weight:600;letter-spacing:-.015em;
    margin:0 0 14px;color:var(--encre)}
  .basse h2+ul,.basse h2+p{margin-top:0}
  .basse ul+h2,.basse p+h2,.basse div+h2{margin-top:40px}
  .basse p{font-size:15px;color:var(--demi);max-width:76ch;line-height:1.65;margin:8px 0}
  .basse p b{color:var(--encre)}
  .basse ul{color:var(--demi);max-width:76ch;margin:8px 0;padding:0;list-style:none;font-size:15px;line-height:1.65}
  .basse li{margin:0 0 .5rem;padding-left:1.1rem;position:relative}
  .basse li::before{content:"";position:absolute;left:0;top:.72em;width:6px;height:1.5px;background:var(--accent-titre)}
  .basse li b{color:var(--encre)}
  .clone-t{font:500 10px/1.4 var(--mono);letter-spacing:.14em;text-transform:uppercase;
    color:var(--accent-titre);display:block;margin:22px 0 8px}
  /* le terminal des trois commandes reste en nuit rubis, posé sur le parchemin */
  .clone{max-width:62ch;background:linear-gradient(163deg,var(--nuit-a),var(--nuit-b));
    border:1px solid color-mix(in srgb,var(--accent-vif) 30%,transparent);border-radius:8px;
    padding:14px 18px 16px;font-family:var(--mono);font-size:12.5px;line-height:1.85;overflow-x:auto;
    color:var(--sur);box-shadow:0 6px 18px rgba(36,18,23,.22)}
  .clone .ps{color:var(--accent-vif);font-weight:600}
  .clone .note{color:var(--sur-pale);font-size:12px}
  .pied{background:var(--nuit-c);color:var(--sur);padding:52px 0}
  .pied-p{font-size:clamp(17px,1.8vw,23px);font-weight:600}

  /* la barre se replie comme celle du vert : sous 1080 la nav disparaît, le sceau
     garde sa place ; mesuré au banc des tailles : nav et sceau débordaient à 320-500 */
  @media (max-width:1080px){
    .barre{padding:12px 18px;gap:14px}
    .barre nav{display:none}
  }
  @media (max-width:900px){
    .colonne{padding:0 20px}
    .rb{width:220px;top:-200px;right:8px}
    .tete{padding:150px 0 18px}
  }
  /* Sous 700px le robot s'asseyait SUR la lede et cachait des mots, relu sur la capture
     375 : la lisibilite passe avant la mascotte, il se retire du telephone. */
  @media (max-width:700px){
    .rb{display:none}
  }
'''
