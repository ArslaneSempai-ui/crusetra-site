#!/usr/bin/env python3
"""L'OFFRE, direction E1 choisie le 4 septembre : les colonnes de nuit.

Trois colonnes aux filets fins, sans cartes, chaque montant en corps d'affiche
(les références collectées avant de dessiner : Linear pour les colonnes,
Vercel pour les prix géants, rangées dans le skill design-arslane). L'ordre
est l'argument : l'évaluation d'abord, la campagne, la licence au-dessus.

CHAQUE CHIFFRE EST SOURCÉ : l'évaluation vient de LICENCES.md du dépôt public,
la campagne et la licence de LICENCE-COMMERCIALE.md (décisions des 25 et
27 août : 12 000 $ fixe ; 30 000 $/an, 30 %% à la signature, solde net 60,
plafond de renouvellement au plus bas de CPI-U et 5 %%). Aucun palier
intermédiaire n'est documenté ; aucun n'est affiché.
"""
import json
import sys
import pathlib

BASE = pathlib.Path(__file__).parent
from outil import SCEAU_ROUTING, OUTILS, pied_html, CSS_PIED_SITE, SITE_URL, CONTACT
# 04/10 (audit Routing) : la page des tarifs ne montrait pas les offres que la page Routing vend ; elles se lisent
# dans offre-routing.json (la grille choisie par Arslane le 29/09), jamais tapées ici
OFFRE_ROUTING = json.loads((BASE / "offre-routing.json").read_text())
# 05/10 (parcours client) : « See pricing » depuis la page Screening menait à une page sans offre Screening ; elle se lit
# dans offre-screening.json (la grille choisie par Arslane le 29/09, la conservation tranchée le 5/10), jamais tapée ici
OFFRE_SCREENING = json.loads((BASE / "offre-screening.json").read_text())
# 10/10: the yearly re-screen is ten months paid ("two months free"), printed as an amount derived from the monthly price
if OFFRE_SCREENING["annuel"] != "two months free":
    sys.exit("offre-screening.json: the yearly rule changed, so MOIS_PAYES_AN must be reviewed")
MOIS_PAYES_AN = 10
SCEAU = SCEAU_ROUTING   # lu dans le relevé scellé du vert, jamais tapé (8/09)
# la barre du site (10/09) : les cinq instruments dans l'ordre du rideau, lus dans OUTILS, jamais tapés
NAV = "".join(f'\n    <a href="{o["page_hero"]}">{o["nom"]}</a>' for o in OUTILS.values())
DEPOT_URL = OUTILS["routing"]["depot"]   # the repository, written once in outil.py

CSS = '''
  :root{--noir:#0e0e11;--noir-b:#08080a;--noir-c:#121215;--filet:#26262c;--sur:#e8e6df;--sur-pale:#9a988f;
    --vert-titre:#23543f;--vert-vif:#57b184;--vert-clair:#a5f7cb;--papier:#dbd7c5;--encre:#1b1d18;
    --texte:"Literata",Georgia,serif;--mono:"Roboto Mono",ui-monospace,Menlo,monospace;--montee:cubic-bezier(.16,.84,.32,1)}
  *{box-sizing:border-box;margin:0}
  /* les attributs width/height des images sont des indications de PRÉSENTATION : sans
     cette ligne, la hauteur naturelle gagne sur l'aspect-ratio du CSS. Une vignette de
     60 px a rendu à 1083 px de haut en production le 13/09. */
  img{max-width:100%;height:auto}
  html{scroll-behavior:smooth;caret-color:var(--vert-vif);scrollbar-color:var(--vert-titre) var(--noir-b)}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{background:var(--noir);color:var(--sur);font-family:var(--texte);line-height:1.6;overflow-x:hidden;position:relative}
  ::selection{background:var(--vert-vif);color:var(--noir-b)}
  a{text-underline-offset:4px;color:inherit}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  :focus-visible{outline:3px solid var(--vert-vif);outline-offset:3px;border-radius:2px}
  .colonne{max-width:1180px;margin:0 auto;padding:0 48px;position:relative;z-index:2}
  /* the ground : a fine grid, and the light that follows the pointer (10/09, « effets de souris ») */
  .grille{position:fixed;inset:0;z-index:0;pointer-events:none;
    background-image:linear-gradient(color-mix(in srgb,var(--sur) 4%,transparent) 1px,transparent 1px),
      linear-gradient(90deg,color-mix(in srgb,var(--sur) 4%,transparent) 1px,transparent 1px);background-size:64px 64px;
    mask-image:radial-gradient(ellipse 70% 60% at 50% 20%,#000 30%,transparent 100%)}
  .lumiere{position:fixed;left:0;top:0;width:800px;height:800px;border-radius:50%;z-index:1;pointer-events:none;
    background:radial-gradient(circle,color-mix(in srgb,var(--vert-vif) 18%,transparent),transparent 62%);will-change:transform;filter:blur(10px)}
  html:not(.js) .lumiere{display:none}

  .barre{position:absolute;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;gap:28px;padding:14px 32px}
  .marque{font-weight:700;font-size:19px;letter-spacing:.01em;text-decoration:none;color:var(--sur)}
  .barre nav{display:flex;gap:16px;margin-left:auto}
  .barre nav a{font-size:14.5px;text-decoration:none;color:var(--sur-pale);padding:13px 6px}
  .barre nav a:hover{color:var(--sur);text-decoration:underline;text-decoration-color:var(--vert-vif);text-decoration-thickness:1.5px}
  .barre nav a[aria-current]{color:var(--sur);text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:7px;text-decoration-color:currentColor}

  .tete{padding:150px 0 20px}
  .h1{font-size:clamp(38px,5vw,66px);font-weight:600;letter-spacing:-.02em;line-height:1.04;text-wrap:balance}
  .lede{font-size:clamp(15px,1.3vw,18.5px);color:var(--sur-pale);max-width:72ch;line-height:1.65;margin-top:18px;text-wrap:balance}
  .lede b{color:var(--sur)}

  /* the three offers : cards that light where the cursor is ; the buttons pinned at the foot, one line */
  .cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin:150px 0 10px;align-items:stretch}
  .col{position:relative;display:flex;flex-direction:column;padding:126px 30px 26px;border-radius:16px;background:var(--noir-c);
    border:1px solid var(--filet);--mx:50%;--my:0%;transition:transform .35s var(--montee),border-color .3s}
  .col::before{content:"";position:absolute;inset:0;border-radius:16px;pointer-events:none;opacity:0;transition:opacity .35s;
    background:radial-gradient(460px circle at var(--mx) var(--my),color-mix(in srgb,var(--vert-vif) 14%,transparent),transparent 62%)}
  .col::after{content:"";position:absolute;inset:-1px;border-radius:17px;pointer-events:none;padding:1px;opacity:0;transition:opacity .35s;
    background:radial-gradient(340px circle at var(--mx) var(--my),var(--vert-clair),transparent 70%);
    -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
  .col:hover{transform:translateY(-4px)}
  .col:hover::before,.col:hover::after{opacity:1}
  .col.haute{border-color:color-mix(in srgb,var(--vert-vif) 45%,var(--filet))}
  .col.haute::after{opacity:.35}
  .col-robot{position:absolute;top:-96px;left:50%;height:190px;width:auto;transform:translateX(-50%);pointer-events:none;
    filter:drop-shadow(0 26px 40px rgba(0,0,0,.7));transition:transform .4s var(--montee)}
  .col.haute .col-robot{height:214px;top:-116px}
  .c-t{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--sur-pale)}
  .c-prix{font-weight:600;font-size:clamp(40px,4.4vw,64px);letter-spacing:-.02em;line-height:1.05;margin:14px 0 4px;font-variant-numeric:lining-nums tabular-nums}
  .c-prix small{font-size:.32em;font-weight:400;color:var(--sur-pale);letter-spacing:0;white-space:nowrap}
  .col.haute .c-prix{color:var(--vert-clair);text-shadow:0 0 26px color-mix(in srgb,var(--vert-vif) 40%,transparent)}
  .c-qui{font-size:14px;color:var(--sur-pale);min-height:3em;line-height:1.55;border-bottom:1px solid var(--filet);padding-bottom:16px;margin-bottom:16px}
  .c-plus{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:color-mix(in srgb,var(--sur-pale) 70%,transparent);margin-bottom:8px}
  .c-liste{list-style:none;padding:0;display:flex;flex-direction:column;gap:9px;font-size:13.5px;color:var(--sur-pale)}
  .c-liste li{padding-left:22px;position:relative;line-height:1.5}
  .c-liste li::before{content:"";position:absolute;left:0;top:.5em;width:12px;height:7px;border-left:2px solid var(--vert-vif);border-bottom:2px solid var(--vert-vif);transform:rotate(-45deg)}
  .c-liste b{color:var(--sur)}
  .cta{display:block;text-decoration:none;margin-top:auto;padding-top:26px;font-family:var(--texte);font-size:16px;font-weight:600;color:var(--vert-clair)}
  .cta .b{display:inline-flex;align-items:baseline;gap:12px;padding:13px 24px;border-radius:10px;border:1px solid color-mix(in srgb,var(--vert-vif) 45%,transparent);transition:background .2s,color .2s,border-color .2s}
  .cta:hover .b{background:var(--vert-vif);color:var(--noir-b);border-color:var(--vert-vif)}
  .col.haute .cta .b{background:var(--vert-vif);color:var(--noir-b);border-color:var(--vert-vif)}
  .cta .fl{transition:transform .2s var(--montee)}
  .cta:hover .fl{transform:translateX(4px)}
  .c-fin{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;color:color-mix(in srgb,var(--sur-pale) 70%,transparent);margin-top:14px;line-height:1.7;min-height:3.4em}

  /* 04/10 : the extraction cost audit (Routing), four cells under the three columns, same ground, smaller type */
  .ex{padding:26px 0 0}
  .ex-sur{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--sur-pale)}
  .ex-t{font-size:clamp(24px,2.4vw,32px);font-weight:600;letter-spacing:-.01em;line-height:1.15;margin-top:10px}
  .ex-l{font-size:17px;color:var(--sur-pale);line-height:1.6;margin-top:8px;max-width:none}
  .ex-l a{color:var(--sur);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--vert-clair) 50%,transparent)}
  .ex-grille{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:30px;align-items:stretch}
  .ex-c{display:flex;flex-direction:column;padding:24px 24px 22px;border-radius:16px;background:var(--noir-c);border:1px solid var(--filet)}
  .ex-c.haute{border-color:color-mix(in srgb,var(--vert-vif) 45%,var(--filet))}
  .ex-eti{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--sur-pale)}
  .ex-prix{font-weight:600;font-size:clamp(30px,3vw,42px);letter-spacing:-.02em;line-height:1.05;margin:12px 0 10px;font-variant-numeric:lining-nums tabular-nums}
  .ex-prix small{font-size:.38em;font-weight:400;color:var(--sur-pale);letter-spacing:0;white-space:nowrap}
  .ex-c.haute .ex-prix{color:var(--vert-clair)}
  .ex-q{font-size:14px;color:var(--sur-pale);line-height:1.55}
  .ex-fin{font-size:15px;line-height:1.65;color:var(--sur-pale);max-width:none;margin:26px 0 0;text-wrap:pretty}
  .ex-fin b{color:var(--sur);font-weight:600}
  @media (max-width:1080px){.ex-grille{grid-template-columns:1fr 1fr}}
  /* a cell's paragraph must keep 45 % of the screen at tablet width (temoin-effondrement) : one column from 800 px down */
  @media (max-width:800px){.ex-grille{grid-template-columns:1fr}}

  /* the days : three lanes to scale, the papers on their lane at their date, one line reads the day */
  .jours{padding:80px 0 30px}
  .jours-t{font-size:clamp(24px,2.4vw,32px);font-weight:600;letter-spacing:-.01em;line-height:1.15}
  .jours-l{font-size:17px;color:var(--sur-pale);line-height:1.6;margin-top:8px;max-width:none}
  .axe-boite{margin-top:34px;border:1px solid var(--filet);border-radius:16px;background:var(--noir-c);padding:36px 40px 30px;position:relative;overflow:hidden}
  .axe-defile{overflow-x:auto;overflow-y:hidden}
  .axe{position:relative;height:364px;--y:324px;min-width:820px;user-select:none;cursor:ew-resize;touch-action:pan-y}
  .regle{position:absolute;left:0;right:0;top:var(--y);height:2px;background:var(--filet)}
  .regle i{position:absolute;left:0;top:0;height:2px;width:calc(130/150*100%);background:linear-gradient(90deg,var(--vert-vif),var(--vert-clair))}
  .graduations span{position:absolute;left:calc(var(--d)/150*100%);top:calc(var(--y) + 10px);transform:translateX(-50%);font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;color:var(--sur-pale);text-align:center;line-height:1.4;white-space:nowrap}
  .graduations span i{display:block;width:1px;height:10px;background:var(--sur-pale);margin:-14px auto 4px}
  .graduations .coupure i{height:18px;width:12px;background:none;border-left:2px solid var(--sur-pale);border-right:2px solid var(--sur-pale);transform:skewX(-30deg);margin-top:-18px}
  .graduations span[style*="--d:0"]{transform:none;text-align:left}.graduations span[style*="--d:0"] i{margin-left:0}
  .graduations span[style*="--d:150"]{transform:translateX(-100%);text-align:right}.graduations span[style*="--d:150"] i{margin-right:0}
  .curseur{position:absolute;top:0;left:calc(12/150*100%);width:2px;height:calc(var(--y) + 8px);background:var(--vert-clair);transform:translateX(-50%);box-shadow:0 0 14px var(--vert-vif);z-index:5}
  .curseur::after{content:"";position:absolute;left:50%;bottom:-6px;width:12px;height:12px;border-radius:50%;background:var(--vert-clair);transform:translateX(-50%)}
  .curseur span{position:absolute;top:2px;left:10px;font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--vert-clair);white-space:nowrap;background:var(--noir-c);padding:2px 6px;border-radius:4px}
  html:not(.js) .curseur{display:none}
  .voies{position:absolute;left:0;right:0;top:34px}
  .voie{position:absolute;left:0;right:0;top:calc(var(--t)*92px);height:84px;border-bottom:1px solid color-mix(in srgb,var(--filet) 70%,transparent);transition:background .3s}
  .voie:hover{background:color-mix(in srgb,var(--vert-vif) 5%,transparent)}
  .v-nom{position:absolute;left:0;top:6px;font-family:var(--texte);font-size:15px;font-weight:600;color:var(--sur);z-index:2}
  .voie[data-l="eval"] .v-nom{left:112px}
  .barre-v{position:absolute;left:calc(var(--a)/150*100%);width:calc((var(--b) - var(--a))/150*100%);top:60px;height:6px;border-radius:3px;background:color-mix(in srgb,var(--vert-vif) 50%,transparent)}
  .barre-v.pointille{background:repeating-linear-gradient(90deg,color-mix(in srgb,var(--vert-vif) 50%,transparent) 0 6px,transparent 6px 10px)}
  .v-robot{position:absolute;left:-4px;top:-22px;height:98px;width:auto;filter:drop-shadow(0 16px 26px rgba(0,0,0,.65));z-index:1}
  .anneau{position:absolute;left:calc(30/150*100%);top:26px;width:40px;height:40px;transform:translateX(-50%);z-index:2}
  .anneau svg{width:40px;height:40px;transform:rotate(-90deg)}
  .anneau circle{fill:var(--noir-c);stroke:var(--filet);stroke-width:4}
  .anneau .plein{fill:none;stroke:var(--vert-clair);stroke-dasharray:100.5;stroke-dashoffset:100.5;transition:stroke-dashoffset .2s}
  html:not(.js) .anneau .plein{stroke-dashoffset:0}
  .pap{position:absolute;left:calc(var(--d)/150*100%);top:12px;transform:translateX(var(--tx));width:150px;background:linear-gradient(165deg,#f2edda,#ded8c3);color:var(--encre);border-radius:3px;
    padding:7px 9px;box-shadow:0 12px 24px rgba(0,0,0,.55);display:flex;flex-direction:column;gap:2px;opacity:.5;transition:opacity .3s}
  .pap.vu,html:not(.js) .pap{opacity:1}
  .pap>span{font-family:var(--mono);font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#55523f;border-bottom:1px solid #9d9a83;padding-bottom:3px}
  .pap b{font-size:12px;font-weight:600;line-height:1.2}
  .voie[data-l="eval"] .pap{top:14px}
  .etat{font-size:18px;line-height:1.5;color:var(--sur);margin:22px auto 0;max-width:80ch;text-align:center;text-wrap:balance;min-height:2.6em}
  .etat b{color:var(--vert-clair);font-weight:600}
  .commande-jour{display:flex;justify-content:center;gap:12px;align-items:center;margin-top:14px;font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--sur-pale)}
  .commande-jour button{font:inherit;letter-spacing:inherit;color:var(--vert-clair);background:none;border:1px solid color-mix(in srgb,var(--vert-vif) 45%,transparent);border-radius:8px;padding:8px 14px;cursor:pointer}
  .commande-jour button:hover{background:var(--vert-vif);color:var(--noir-b)}
  html:not(.js) .commande-jour{display:none}
  /* the closing paragraph runs the whole width of the column : never piled on the left (Arslane, 11/09) */
  .note-fin{font-size:17px;line-height:1.65;color:var(--sur-pale);max-width:none;margin:34px 0 90px;text-wrap:pretty}
  .note-fin a{color:var(--sur);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--vert-clair) 50%,transparent)}
  .note-fin b{color:var(--sur);font-weight:600}

  .pied{background:var(--noir-b);color:var(--sur);padding:52px 0;position:relative;z-index:2;border-top:1px solid var(--filet)}
  .pied-p{font-size:clamp(17px,1.8vw,23px);font-weight:600}

  @media (max-width:1080px){
    .colonne{padding:0 22px}
    .barre{padding:12px 18px;gap:14px}
    .barre nav{display:none}
    .tete{padding-top:100px}
    .cols{grid-template-columns:1fr;gap:110px;margin-top:130px}
    .axe-boite{padding:24px 18px}
  }
  /* the contact card (Arslane, 13/09 : « pas la peine de les emmener vers toute une autre page »,
     then « beaucoup plus pro et réactif avec la souris ») : a glass plate over the dimmed page.
     The light and the lit edge follow the pointer, the plate tilts toward it, grain gives it
     matter ; Escape, the cross or the backdrop close it ; reduced motion keeps it still */
  .carte-contact{background:transparent;border:0;padding:0;position:fixed;inset:0;margin:auto;width:min(700px,calc(100% - 24px));
    height:max-content;max-height:calc(100vh - 24px);overflow:visible;outline:0;color:var(--sur);perspective:1500px}
  .carte-contact::backdrop{background:rgba(3,5,4,.64);backdrop-filter:blur(12px) saturate(.85)}
  .cc-plaque{position:relative;isolation:isolate;overflow:hidden;outline:0;border-radius:20px;padding:48px 52px 46px;
    background:linear-gradient(160deg,rgba(26,29,31,.94),rgba(9,10,11,.98));box-shadow:0 50px 120px rgba(0,0,0,.65),inset 0 1px 0 rgba(255,255,255,.07);
    transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));transition:transform .16s ease-out;transform-style:preserve-3d}
  .cc-plaque::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;z-index:2;
    background:radial-gradient(280px circle at var(--mx,50%) var(--my,30%),color-mix(in srgb,var(--vert-clair) 95%,transparent),color-mix(in srgb,var(--vert-vif) 35%,transparent) 45%,rgba(255,255,255,.07) 75%);
    -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
  .cc-lueur{position:absolute;inset:0;pointer-events:none;background:radial-gradient(520px circle at var(--mx,50%) var(--my,30%),color-mix(in srgb,var(--vert-clair) 12%,transparent),transparent 62%)}
  .cc-grain{position:absolute;inset:0;pointer-events:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .09 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");mix-blend-mode:overlay;opacity:.6}
  .cc-corps{position:relative;transform:translateZ(28px)}
  .cc-sur{margin:0 0 16px;font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--vert-clair)}
  .cc-titre{margin:0 0 18px;font-size:34px;line-height:1.05;font-weight:600;letter-spacing:-.015em}
  .cc-mail-ligne{display:flex;align-items:baseline;gap:14px;margin:0 0 26px}
  .cc-mail{font-family:var(--mono);font-size:22px;font-weight:500;color:var(--sur);text-decoration:none;padding-bottom:6px;
    background:linear-gradient(var(--vert-clair),var(--vert-clair)) no-repeat 0 100%/0 1px;transition:background-size .4s var(--montee)}
  .cc-mail:hover,.cc-mail:focus-visible{background-size:100% 1px}
  .cc-copie{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--sur-pale);background:none;
    border:1px solid rgba(255,255,255,.12);border-radius:6px;padding:7px 9px;cursor:pointer;transition:color .2s,border-color .2s}
  .cc-copie:hover{color:var(--vert-clair);border-color:color-mix(in srgb,var(--vert-clair) 50%,transparent)} .cc-copie.fait{color:var(--vert-clair);border-color:var(--vert-clair)}
  .cc-liste{list-style:none;margin:0 0 30px;padding:0;display:grid;gap:12px;font-size:15.5px;line-height:1.5;color:color-mix(in srgb,var(--sur) 72%,transparent)}
  .cc-liste li{position:relative;padding-left:20px;transition:color .2s} .cc-liste li:hover{color:var(--sur)}
  .cc-liste li::before{content:"";position:absolute;left:0;top:.6em;width:6px;height:6px;border-radius:50%;background:var(--vert-vif);box-shadow:0 0 10px color-mix(in srgb,var(--vert-vif) 80%,transparent)}
  .cc-liste b{color:var(--sur);font-weight:600}
  .cc-actions{display:flex;gap:12px;flex-wrap:wrap}
  .cc-bt{display:inline-block;padding:13px 22px;border-radius:11px;background:linear-gradient(135deg,#72d3a4,#4ea779);color:var(--noir-b);font-size:14.5px;font-weight:600;
    text-decoration:none;box-shadow:0 6px 18px color-mix(in srgb,var(--vert-vif) 22%,transparent);transition:transform .18s,box-shadow .18s}
  .cc-bt:hover{transform:translateY(-2px);box-shadow:0 12px 30px color-mix(in srgb,var(--vert-vif) 42%,transparent)} .cc-bt:active{transform:translateY(0)}
  .cc-bt.cc-sec{background:rgba(255,255,255,.03);color:var(--vert-clair);border:1px solid color-mix(in srgb,var(--vert-clair) 35%,transparent);box-shadow:none}
  .cc-bt.cc-sec:hover{border-color:var(--vert-clair);background:color-mix(in srgb,var(--vert-clair) 7%,transparent)}
  .cc-fermer{position:absolute;top:18px;right:18px;z-index:3;width:38px;height:38px;border-radius:50%;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);
    color:var(--sur-pale);font:400 20px/1 var(--texte);cursor:pointer;transition:transform .25s,color .2s,border-color .2s}
  .cc-fermer:hover{color:var(--sur);border-color:var(--vert-clair);transform:rotate(90deg)}
  .carte-contact[open] .cc-plaque{animation:cc-ouvrir .48s var(--montee)}
  @keyframes cc-ouvrir{from{opacity:0;transform:translateY(28px) rotateX(9deg) scale(.985)}}
  @media (max-width:700px){.cc-plaque{padding:30px 22px 26px}.cc-titre{font-size:26px}.cc-mail{font-size:15px}.cc-liste{font-size:14px}}
  @media (prefers-reduced-motion:reduce){
    .carte-contact[open] .cc-plaque{animation:none}.cc-plaque{transform:none!important}
    *{transition-duration:.01ms!important;animation-duration:.01ms!important}.lumiere{display:none}}
'''

JS = r'''<script>
(function(){
  const reduit = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const carte = document.getElementById('contact');
  if (carte && carte.showModal) {
    document.querySelectorAll('a[data-contact]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); carte.showModal(); }));
    carte.addEventListener('click', e => { if (e.target === carte) carte.close(); });
    const pl = carte.querySelector('.cc-plaque');
    pl.addEventListener('pointermove', e => { const b = pl.getBoundingClientRect(); const px = (e.clientX - b.left) / b.width, py = (e.clientY - b.top) / b.height;
      pl.style.setProperty('--mx', (px * 100) + '%'); pl.style.setProperty('--my', (py * 100) + '%');
      if (!reduit) { pl.style.setProperty('--rx', ((.5 - py) * 8) + 'deg'); pl.style.setProperty('--ry', ((px - .5) * 10) + 'deg'); } });
    pl.addEventListener('pointerleave', () => { pl.style.setProperty('--rx', '0deg'); pl.style.setProperty('--ry', '0deg'); });
    carte.querySelectorAll('[data-copie]').forEach(b => b.addEventListener('click', () => { if (navigator.clipboard) navigator.clipboard.writeText(b.dataset.copie);
      b.textContent = 'copied'; b.classList.add('fait'); setTimeout(() => { b.textContent = 'copy'; b.classList.remove('fait'); }, 1600); }));
  }
  const l = document.querySelector('.lumiere'); let tx = innerWidth * .6, ty = 320, x = tx, y = ty;
  addEventListener('pointermove', e => { tx = e.clientX; ty = e.clientY; }, {passive: true});
  if (!reduit) (function pas(){ x += (tx - x) * .07; y += (ty - y) * .07; l.style.transform = 'translate(' + (x - 400) + 'px,' + (y - 400) + 'px)'; requestAnimationFrame(pas); })();
  document.querySelectorAll('.col').forEach(c => { const r = c.querySelector('.col-robot');
    c.addEventListener('pointermove', e => { const b = c.getBoundingClientRect(); const px = (e.clientX - b.left) / b.width, py = (e.clientY - b.top) / b.height;
      c.style.setProperty('--mx', (px * 100) + '%'); c.style.setProperty('--my', (py * 100) + '%');
      if (r && !reduit) r.style.transform = 'translateX(-50%) translateY(-10px) rotate(' + ((px - .5) * 8) + 'deg)'; });
    c.addEventListener('pointerleave', () => { if (r) r.style.transform = ''; }); });
  const fmt = n => '$' + n.toLocaleString('en-US');
  const io = new IntersectionObserver(es => es.forEach(en => { if (!en.isIntersecting) return; io.unobserve(en.target);
    const txt = en.target.childNodes[0]; const m = /\$([\d,]+)/.exec(txt.textContent); if (!m) return;
    const fin = parseInt(m[1].replace(/,/g, ''), 10); if (!fin || reduit) return; const t0 = performance.now(), d = 1100;
    (function tick(t){ const p = Math.min(1, (t - t0) / d), e = 1 - Math.pow(1 - p, 3); txt.textContent = fmt(Math.round(fin * e)); if (p < 1) requestAnimationFrame(tick); })(t0);
  }), {threshold: .4});
  document.querySelectorAll('.c-prix').forEach(c => io.observe(c));
  // the days : the axis, the cursor, the lanes, one line that reads the day
  const axe = document.getElementById('axe'), cur = document.getElementById('curseur'), lab = document.getElementById('jour'), etat = document.getElementById('etat');
  if (!axe) return;
  const LIC = 30000, PART = 0.30, CAMP = 12000;        // the documented terms ; the amounts below are computed, never typed
  const ECHELLE = 150, versJour = u => u <= 130 ? Math.round(u) : Math.round(130 + (u - 130) / 20 * 235);
  let u = 12, actif = false;
  const poser = v => { u = Math.max(0, Math.min(ECHELLE, v)); cur.style.left = (u / ECHELLE * 100) + '%'; const j = versJour(u);
    lab.textContent = 'Day ' + j; cur.setAttribute('aria-valuenow', j);
    document.querySelectorAll('.pap').forEach(p => { const d = parseFloat(p.style.getPropertyValue('--d')); p.classList.toggle('vu', u >= d - 0.5); });
    const pl = document.querySelector('.anneau .plein'); if (pl) pl.style.strokeDashoffset = 100.5 * (1 - Math.min(30, j) / 30);
    let s;
    if (j <= 30) s = '<b>Day ' + j + ' of the thirty.</b> The counter runs on your machine and results stay internal. No data has reached us, and nothing is owed.';
    else if (j < 45) s = '<b>Day ' + j + '.</b> The thirty days have run. Nothing is owed until you sign; your legal team can read the papers now.';
    else if (j < 105) s = '<b>Day ' + j + '.</b> Signed ' + (j - 45 === 0 ? 'today' : (j - 45) + ' days ago') + '. Campaign: the invoice (' + fmt(CAMP) + ', fixed) is settled and the sealed report is on your machine. License: 30% paid (' + fmt(LIC * PART) + '); the balance (' + fmt(LIC * (1 - PART)) + ') falls due in ' + (105 - j) + ' days.';
    else if (j < 365) s = '<b>Day ' + j + '.</b> The balance is settled. The license year runs on all five instruments, updates included, with recertification on fresh records over the period you declare.';
    else s = '<b>The twelfth month.</b> Renewal capped at the lower of CPI-U and 5% above this year.';
    etat.innerHTML = s; };
  const depuis = e => { const b = axe.getBoundingClientRect(); return (e.clientX - b.left) / b.width * ECHELLE; };
  axe.addEventListener('pointerdown', e => { actif = true; axe.setPointerCapture(e.pointerId); poser(depuis(e)); });
  axe.addEventListener('pointermove', e => { if (actif) poser(depuis(e)); });
  axe.addEventListener('pointerup', () => actif = false); axe.addEventListener('pointercancel', () => actif = false);
  cur.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { poser(u + 2); e.preventDefault(); } if (e.key === 'ArrowLeft') { poser(u - 2); e.preventDefault(); } });
  document.getElementById('courir').addEventListener('click', () => { if (reduit) { poser(ECHELLE); return; }
    const t0 = performance.now(), d = 6000; actif = false; (function pas(t){ const p = Math.min(1, (t - t0) / d); poser(p * ECHELLE); if (p < 1 && !actif) requestAnimationFrame(pas); })(t0); });
  poser(u);
})();
</script>
'''

PAGE = f'''<!doctype html><html lang="en">
<meta charset="utf-8"><title>Crusetra &#183; pricing</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="Crusetra: what an engagement buys">
<meta property="og:description" content="Evaluate free for thirty days on your own records. Then one sealed measurement campaign at a fixed price, or the annual license for the suite.">
<meta property="og:url" content="{SITE_URL}engagement.html">
<meta property="og:image" content="{SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="description" content="Evaluate free for thirty days on your own records. Then one sealed measurement campaign at a fixed price, or the annual license for the suite.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M0 0h16L0 16z' fill='%2314251e'/%3E%3Cpath d='M16 0v16H0z' fill='%2323543f'/%3E%3C/svg%3E">
<link rel="stylesheet" href="fontes/literata.css">
<link rel="stylesheet" href="fontes/roboto-mono.css">
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}{CSS_PIED_SITE}</style>
<div class="grille" aria-hidden="true"></div><div class="lumiere" aria-hidden="true"></div>
<header class="barre">
  <a class="marque" href="ACCUEIL.html">CRUSETRA</a>
  <nav aria-label="Site">{NAV}
    <a href="ENGAGEMENT.html" aria-current="page">Pricing</a>
    <a href="CONTACT.html">Contact</a>
  </nav>
</header>

<main>
<section class="tete"><div class="colonne">
  <h1 class="h1">What you get, and what it costs.</h1>
  <p class="lede"><b>Test any of the five tools for thirty days on your own records.</b><br>
    When you are ready, we run one measurement on your data and hand you a report signed with a key your audit team can check, which you can then license for the year.</p>
</div></section>

<section aria-label="The three steps"><div class="colonne">
  <div class="cols">
    <div class="col">
      <img class="col-robot" src="rendus/robot-salut.webp" alt="">
      <p class="c-t">the evaluation</p>
      <p class="c-prix">$0<small> &#183; 30 days</small></p>
      <p class="c-qui">Thirty days on your own records, with nothing to sign.</p>
      <ul class="c-liste">
        <li>The whole of each tool, on your own records: <b>Routing</b>, <b>Screening</b>, <b>Monitoring</b>, <b>Scoring</b>, and the <b>Dossier</b> that reads all four</li>
        <li>Your thirty days start the first time you run the tool. Downloading it does not start the clock</li>
        <li>Results stay internal, and you may not use them in live operations</li>
      </ul>
      <a class="cta" href="{DEPOT_URL}"><span class="b">Download and run <span class="fl" aria-hidden="true">&#8594;</span></span></a>
      <p class="c-fin">These thirty days are written into the public license, which ships with the code</p>
    </div>
    <div class="col">
      <img class="col-robot" src="rendus/robot-penche.webp" alt="">
      <p class="c-t">the campaign</p>
      <p class="c-prix">$12,000<small> fixed</small></p>
      <p class="c-qui">A signed report that says, for each control, which setting to use and what it catches on your own records.</p>
      <p class="c-plus">everything in the evaluation, plus</p>
      <ul class="c-liste">
        <li><b>The setting each tool recommends</b>, and what it costs you: which model reads each identity field, where to set the screening bar, which scenarios to keep, and which risk factors carry weight</li>
        <li>Each rate with the range it could reasonably be in, its confidence interval. Under twenty cases we quote no rate at all, because a rate on so few cases would mislead you</li>
        <li>A <b>signed report</b> your audit team can check on its own</li>
        <li>The tool runs on your machine, so your records never reach us</li>
      </ul>
      <a class="cta" href="CONTACT.html" data-contact><span class="b">Contact us <span class="fl" aria-hidden="true">&#8594;</span></span></a>
      <p class="c-fin">one campaign &#183; one signed deliverable</p>
    </div>
    <div class="col haute">
      <img class="col-robot" src="rendus/robot-vert-tient.webp" alt="">
      <p class="c-t">the license</p>
      <p class="c-prix">$30,000<small> a year</small></p>
      <p class="c-qui">For using it in your own operations. Commercial use, updates included.</p>
      <p class="c-plus">everything in the campaign, plus</p>
      <ul class="c-liste">
        <li>Commercial use for your own business</li>
        <li>One license covers <b>Routing</b>, <b>Screening</b>, <b>Monitoring</b> and <b>Scoring</b></li>
        <li>The <b>Dossier</b>, which reports on all four tools in one file your reviewers can check</li>
        <li>The <b>licensed component</b>: the part that plugs into your own pipeline and changes what reaches production, not only what you know about it. It is not in the public repository</li>
        <li>Updates included for each paid term</li>
        <li><b>Re-measure</b> on fresh records on the schedule you set, and the report is signed again</li>
        <li>One legal entity signs, and every affiliate it covers is named</li>
      </ul>
      <a class="cta" href="CONTACT.html" data-contact><span class="b">Ask about the license <span class="fl" aria-hidden="true">&#8594;</span></span></a>
      <p class="c-fin">30% on signature &#183; net 60 &#183; renewal capped at the lower of CPI&#8209;U and 5%</p>
    </div>
  </div>
</div></section>

<section class="ex" aria-label="The extraction cost audit, by the tier"><div class="colonne">
  <p class="ex-sur">Routing &#183; the extraction cost audit</p>
  <h2 class="ex-t">One document type, measured on your own pages, at a fixed price.</h2>
  <p class="ex-l">You already pay a document extractor. The audit grades it and its challengers on a labeled sample of your pages, on your machine, and names for each field the cheapest source that stays within the margin you declare. <a href="HERO.html#report">See how it runs on 100 real receipts</a>.</p>
  <div class="ex-grille">
    <div class="ex-c"><p class="ex-eti">Free test</p><p class="ex-prix">$0<small> &#183; {OFFRE_ROUTING["essai"]["pages"]} pages</small></p><p class="ex-q">One document type, up to {OFFRE_ROUTING["essai"]["extracteurs"]} extractors. You run it, you email us the record, you get a one-page PDF back within {OFFRE_ROUTING["essai"]["delai_heures"]} hours. An internal evaluation, like the thirty days. The record carries a content hash; the report is not signed.</p></div>
    <div class="ex-c"><p class="ex-eti">Snapshot</p><p class="ex-prix">${OFFRE_ROUTING["snapshot"]["prix_usd"]:,}<small> &#183; up to {OFFRE_ROUTING["snapshot"]["pages"]:,} pages</small></p><p class="ex-q">One document type, up to {OFFRE_ROUTING["snapshot"]["champs"]} fields and {OFFRE_ROUTING["snapshot"]["extracteurs"]} extractors. The signed report, its PDF and the sealed record, back within {OFFRE_ROUTING["snapshot"]["delai_heures"]} hours, with the right to act on the recommendation in your own operations. Paid in two halves, on signature and on delivery.</p></div>
    <div class="ex-c haute"><p class="ex-eti">Audit</p><p class="ex-prix">${OFFRE_ROUTING["audit"]["prix_usd"]:,}<small> &#183; up to {OFFRE_ROUTING["audit"]["pages"]:,} pages</small></p><p class="ex-q">Up to {OFFRE_ROUTING["audit"]["types_document"]} document types, {OFFRE_ROUTING["audit"]["champs"]} fields and {OFFRE_ROUTING["audit"]["extracteurs"]} extractors. The signed report, its PDF and the sealed record, back within {OFFRE_ROUTING["audit"]["delai_heures"]} hours, with the same right to act on the recommendation. Paid in two halves, on signature and on delivery.</p></div>
    <div class="ex-c"><p class="ex-eti">Quarterly audit</p><p class="ex-prix">${OFFRE_ROUTING["audit_trimestriel"]["prix_usd_an"]:,}<small> a year</small></p><p class="ex-q">The Audit measured again {OFFRE_ROUTING["audit_trimestriel"]["remesures_par_an"]} times a year, each report saying what moved since the last. Paid a year in advance. Stop at any time: it runs to the end of the year paid, with no refund.</p></div>
  </div>
  <p class="ex-fin">Prices are in US dollars. Each engagement is contracted and invoiced by <b>HS Industries LLC</b>: the Snapshot and the Audit under an engagement letter written before signature, the Quarterly audit as a subscription. Vendor fees for the pages you run through cloud extractors are billed to you by those vendors, on your own keys. Sealed means the record carries a content hash, which shows an edit made after sealing; a content hash is not a signature.</p>
</div></section>

<section class="ex" aria-label="The screening report, by the tier"><div class="colonne">
  <p class="ex-sur">Screening &#183; the screening report</p>
  <h2 class="ex-t">Your list of names, screened against ten sanctions lists, at a fixed price.</h2>
  <p class="ex-l">You email a list of company and vessel names. We screen it against ten public sources and send back a PDF, a spreadsheet and the sealed record, each candidate with its list entry and the words that matched. <a href="HERO-SCREENING.html#report">See what a report holds</a>.</p>
  <div class="ex-grille">
    <div class="ex-c"><p class="ex-eti">Free test</p><p class="ex-prix">$0<small> &#183; {OFFRE_SCREENING["essai_noms"]} names</small></p><p class="ex-q">Email {OFFRE_SCREENING["essai_noms"]} of your names. The report comes back within {OFFRE_SCREENING["delai_heures"]} hours, at no charge.</p></div>
    <div class="ex-c haute"><p class="ex-eti">One report</p><p class="ex-prix">${OFFRE_SCREENING["rapport"]["prix_usd"]:,}<small> &#183; up to {OFFRE_SCREENING["rapport"]["noms"]:,} names</small></p><p class="ex-q">Your list, screened once and sealed, back within {OFFRE_SCREENING["delai_heures"]} hours: the PDF, the spreadsheet and the sealed record.</p></div>
    <div class="ex-c"><p class="ex-eti">Weekly re-screen</p><p class="ex-prix">${OFFRE_SCREENING["recriblage"][0]["prix_usd_mois"]:,}<small> a month &#183; up to {OFFRE_SCREENING["recriblage"][0]["noms"]:,} names</small></p><p class="ex-q">The same list, screened again each week; each report opens with what changed since the last one. ${OFFRE_SCREENING["recriblage"][0]["prix_usd_mois"]:,} a month, or ${OFFRE_SCREENING["recriblage"][0]["prix_usd_mois"] * MOIS_PAYES_AN:,} a year with {OFFRE_SCREENING["annuel"]}. Stop at any time: it runs to the end of the month or year paid, with no refund.</p></div>
    <div class="ex-c"><p class="ex-eti">Longer lists</p><p class="ex-prix">${OFFRE_SCREENING["recriblage"][1]["prix_usd_mois"]:,}<small> a month &#183; up to {OFFRE_SCREENING["recriblage"][1]["noms"]:,} names</small></p><p class="ex-q">The weekly re-screen for a longer list: ${OFFRE_SCREENING["recriblage"][2]["prix_usd_mois"]:,} a month up to {OFFRE_SCREENING["recriblage"][2]["noms"]:,} names. Yearly: ${OFFRE_SCREENING["recriblage"][1]["prix_usd_mois"] * MOIS_PAYES_AN:,} and ${OFFRE_SCREENING["recriblage"][2]["prix_usd_mois"] * MOIS_PAYES_AN:,}, on the same terms. Above that, write to us for a price.</p></div>
  </div>
  <p class="ex-fin">Prices are in US dollars. Each report is contracted and invoiced by <b>HS Industries LLC</b>. {OFFRE_SCREENING["conservation"]} A candidate is a name for your compliance officer to check: the report does not decide, does not screen ownership, and is not legal advice.</p>
</div></section>

<section class="jours" aria-label="The days"><div class="colonne">
  <p class="jours-t">From trial to license.</p>
  <p class="jours-l">You decide during the thirty days. If you sign, the license year starts that day, and the balance falls due sixty days later.</p>
  <div class="axe-boite"><div class="axe-defile">
    <div class="axe" id="axe">
      <div class="voies">
        <div class="voie" style="--t:0" data-l="eval"><span class="v-nom">The evaluation</span>
          <i class="barre-v" style="--a:0;--b:30"></i>
          <img class="v-robot" src="rendus/robot-salut.webp" alt="">
          <span class="anneau" aria-hidden="true"><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="16"/><circle cx="20" cy="20" r="16" class="plein"/></svg></span>
          <span class="pap" style="--d:30;--tx:34px"><span>thirty days</span><b>granted in the public license</b></span>
        </div>
        <div class="voie" style="--t:1" data-l="camp"><span class="v-nom">The campaign</span>
          <i class="barre-v pointille" style="--a:45;--b:76"></i>
          <span class="pap" style="--d:45;--tx:0"><span>engagement letter</span><b>$12,000 fixed</b></span>
          <span class="pap" style="--d:76;--tx:12px"><span>signed report</span><b>on your machine, yours to check</b></span>
        </div>
        <div class="voie" style="--t:2" data-l="lic"><span class="v-nom">The license</span>
          <i class="barre-v" style="--a:45;--b:150"></i>
          <span class="pap" style="--d:45;--tx:0"><span>commercial license</span><b>30% on signature</b></span>
          <span class="pap" style="--d:105;--tx:-50%"><span>balance</span><b>net 60 days</b></span>
          <span class="pap" style="--d:150;--tx:-100%"><span>the twelfth month</span><b>renewal capped, the lower of CPI-U and 5%</b></span>
        </div>
      </div>
      <div class="graduations">
        <span style="--d:0"><i></i>Day 0<br>first use</span><span style="--d:30"><i></i>Day 30</span><span style="--d:45"><i></i>Signature</span>
        <span style="--d:105"><i></i>+ 60 days</span><span class="coupure" style="--d:130"><i></i></span><span style="--d:150"><i></i>Twelfth month</span>
      </div>
      <div class="regle"><i></i></div>
      <div class="curseur" id="curseur" role="slider" aria-valuemin="0" aria-valuemax="365" aria-valuenow="12" tabindex="0" aria-label="Day"><span id="jour">Day 12</span></div>
    </div>
  </div>
    <p class="etat" id="etat">What you buy afterwards is delivered on your machine, where you can check it yourself.</p>
    <div class="commande-jour"><span>drag the day, or</span><button type="button" id="courir">show the whole year</button></div>
  </div>
  <p class="note-fin">Write to <a href="mailto:{CONTACT}">{CONTACT}</a>. Your vendor onboarding can run during the thirty days, since nothing is signed until you decide. <b>The report certifies only what was measured</b>, and you may not publish the results of an engagement outside your own institution. The full terms are on <a href="ANNEXE-TERMS.html">the terms page</a>, which repeats the license word for word.</p>
</div></section>
</main>

<dialog class="carte-contact" id="contact" aria-labelledby="contact-titre"><div class="cc-plaque" tabindex="-1" autofocus>
  <div class="cc-lueur"></div><div class="cc-grain"></div>
  <div class="cc-corps">
    <p class="cc-sur">Crusetra &#183; Contact</p>
    <h2 class="cc-titre" id="contact-titre">Get in touch.</h2>
    <div class="cc-mail-ligne"><a class="cc-mail" href="mailto:{CONTACT}">{CONTACT}</a><button type="button" class="cc-copie" data-copie="{CONTACT}">copy</button></div>
    <ul class="cc-liste">
      <li><b>Write about a figure or an engagement.</b> Name the page and the figure, so we start from the same source.</li>
      <li><b>Anything worth deciding in the open</b> goes to a public issue on GitHub, with no client names and no records.</li>
      <li><b>Attach no file</b>, except the list you send for a Screening report, or the measured record of a Routing free test. A channel for other records is opened in the engagement letter, before signature.</li>
      <li><b>We answer within one business day.</b></li>
    </ul>
    <div class="cc-actions"><a class="cc-bt" href="mailto:{CONTACT}">Write to us <span aria-hidden="true">&#8594;</span></a><a class="cc-bt cc-sec" href="{DEPOT_URL}/issues">Open an issue <span aria-hidden="true">&#8594;</span></a></div>
  </div>
  <form method="dialog"><button class="cc-fermer" aria-label="Close">&#215;</button></form>
</div></dialog>

{pied_html(sceau=SCEAU)}
{JS}
'''

assert "—" not in PAGE, "un cadratin s'est glissé dans la page"
for _attendu in (f"${OFFRE_ROUTING['snapshot']['prix_usd']:,}", f"${OFFRE_ROUTING['audit']['prix_usd']:,}", f"${OFFRE_ROUTING['audit_trimestriel']['prix_usd_an']:,}", "HS Industries LLC",
                 f"within {OFFRE_ROUTING['essai']['delai_heures']} hours", "right to act on the recommendation",
                 # 05/10 : l'offre Screening, chaque montant et la promesse de conservation lus dans offre-screening.json
                 f"${OFFRE_SCREENING['rapport']['prix_usd']:,}", *(f"${x['prix_usd_mois']:,}" for x in OFFRE_SCREENING["recriblage"]),
                 f"up to {OFFRE_SCREENING['rapport']['noms']:,} names", f"within {OFFRE_SCREENING['delai_heures']} hours", OFFRE_SCREENING["conservation"]):
    assert _attendu in PAGE, f"la page des tarifs n'affiche pas « {_attendu} » : refusé"
(BASE / "ENGAGEMENT.html").write_text(PAGE, encoding="utf-8")
print(f"ENGAGEMENT.html {len(PAGE) / 1e3:.0f} ko")
