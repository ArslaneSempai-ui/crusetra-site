#!/bin/zsh
# LE TÉMOIN DE BOUT EN BOUT du site servi : assemblage, serveur, banc des tailles
# (29 pages × 12 largeurs), captures natives aux arrivées des scènes (bureau et
# téléphone), porte mécanique (controle.mjs du skill design-arslane s'il est là).
# Porté du scratchpad du chef (9/09) dans le dépôt, avec les leçons de la maison :
#   - AUCUN chemin absolu : le site est le parent de ce script (l'assembleur ancré
#     en absolu a rasé deux fois le checkout principal le 9/09) ;
#   - le serveur se lie à 127.0.0.1 explicitement (un aperçu a déjà servi la page
#     au wifi partagé pendant une heure et demie) ;
#   - Chrome 9222 absent → REFUS dit (code 3), jamais un vert qui n'a pas regardé ;
#   - controle.mjs absent → étape SAUTÉE en le disant (dépendance de machine).
# usage: zsh verif-final.sh [outils…]     (défaut : les cinq)
#        DRY=1 saute le banc ; PORT=8802 ; SORTIE=…/dossier (défaut .verif-final/)
set -u
SRC=${0:A:h}
SITE=${SRC:h}
SORTIE=${SORTIE:-$SITE/.verif-final}
PORT=${PORT:-8802}
CAP=$SRC/etats/capturer-cdp.mjs
CTL=$HOME/.claude/skills/design-arslane/scripts/controle.mjs
# zsh ne découpe pas un défaut dans ${@:-…} : sans argument les cinq noms devenaient
# UN élément (« routing screening … dossier/index.html : 000 », premier tir du 9/09)
if [ $# -gt 0 ]; then OUTILS=("$@"); else OUTILS=(routing screening monitoring scoring dossier); fi
mkdir -p $SORTIE

echo "=== chrome 9222 (le banc et les captures regardent par lui)"
curl -s --max-time 2 http://127.0.0.1:9222/json/version > /dev/null || {
  echo "REFUS : Chrome n'écoute pas sur 9222 — le lancer (headless, --remote-debugging-port=9222)" ;
  echo "        un témoin qui n'a pas regardé ne rend pas de vert" ; exit 3 ; }

cd $SRC || exit 1
echo "=== assemblage $(date +%H:%M:%S)"
python3 assembler.py > $SORTIE/assemblage.log 2>&1; code=$?
grep -E "non émis|cassé sur|BOUGÉES|Traceback" $SORTIE/assemblage.log | cut -c1-140
[ $code = 0 ] || { echo "assembleur : code $code, on s'arrête ($SORTIE/assemblage.log)"; exit 1; }
# le témoin de DÉBRANCHEMENT de la garde de voix : si l'assemblage vert ne porte plus la
# ligne de la garde, quelqu'un a retiré l'appel — un vert sans la voix ne part pas
grep -q "structure tenue" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage vert ne porte plus la ligne du témoin des tarifs — débranché" ; exit 5 ; }
grep -q "témoin de l'accueil" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage vert ne porte plus la ligne du témoin de l'accueil — débranché" ; exit 5 ; }
grep -q "voix tenue" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage est vert mais ne porte pas « voix tenue » — la garde de la voix" ;
  echo "        a été DÉBRANCHÉE de l'assembleur (ou muselée) ; rebrancher avant de servir" ; exit 5 ; }

grep -q "orthographe américaine tenue" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage vert ne porte plus la ligne de la garde d'orthographe américaine — débranchée" ; exit 5 ; }
# the address guard (6 October 2026, Crusetra): a green build without its line has lost the guard
grep -q "adresses tenues" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage vert ne porte plus la ligne de la garde des adresses (garde-adresses.py), débranchée" ; exit 5 ; }
# the list-count guard (Crusetra V4, 6 October 2026): same jaw
grep -q "listes tenues" $SORTIE/assemblage.log || {
  echo "REFUS : l'assemblage vert ne porte plus la ligne de la garde des listes (garde-listes.py), débranchée" ; exit 5 ; }
# the films switch guard (7 October 2026, FILMS_VISIBLES in outil.py): same jaw
grep -q "films guard held" $SORTIE/assemblage.log || {
  echo "REFUS : the green build no longer carries the films guard line (assembler.py), unplugged" ; exit 5 ; }
# the releve.json citation witness (12 October 2026): a green build without its line has lost the guard
grep -q "témoin des citations de releve.json" $SORTIE/assemblage.log || {
  echo "REFUS : the green build no longer carries the releve.json citation witness line (assembler.py), unplugged" ; exit 5 ; }

echo "=== serveur $PORT (127.0.0.1 seulement)"
# un serveur déjà debout ne se réutilise que s'il sert CE docs/ : la page servie n'est
# pas la page locale (le 9/09, le 8802 du principal a failli faire capturer un autre
# site depuis un worktree) — l'identité se vérifie au byte, elle ne se suppose pas
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/index.html | grep -q 200; then
  curl -s http://127.0.0.1:$PORT/index.html | cmp -s - $SITE/docs/index.html || {
    echo "REFUS : le port $PORT sert un AUTRE site que $SITE/docs (page servie ≠ page locale)" ;
    echo "        relancer avec PORT=<libre>, ou arrêter ce serveur-là" ; exit 4 ; }
else
  (nohup python3 -m http.server $PORT --bind 127.0.0.1 -d $SITE/docs >/dev/null 2>&1 &) ; sleep 1
fi
for t in $OUTILS; do curl -s -o /dev/null -w "$t/index.html : %{http_code}\n" http://127.0.0.1:$PORT/$t/index.html; done

if [ -z "${DRY:-}" ]; then
  echo "=== banc des tailles $(date +%H:%M:%S)"
  # chaque page réellement servie, lue de docs/ : une liste recopiée vieillit sans le dire
  PAGES=$(cd $SITE/docs && find . -name '*.html' | sed 's#^\./##' | sort | paste -sd, -)
  echo "  $(echo $PAGES | tr ',' '\n' | wc -l | tr -d ' ') pages × 12 largeurs"
  PAGES=$PAGES PORT=$PORT node $SRC/sonde-site.mjs > $SORTIE/banc.log 2>&1; code=$?
  grep -E "^DEBORD|^INDÉTERMINÉ" $SORTIE/banc.log | head -8 | cut -c1-160
  echo "  banc : code $code ; $(tail -1 $SORTIE/banc.log | cut -c1-120)"
  [ $code = 0 ] || echo "  → le détail vit dans $SORTIE/banc.log"
fi

echo "=== le pli du rideau (temoin-rideau.mjs) $(date +%H:%M:%S)"
# on atterrit sur le rideau : ses cinq boutons doivent être dans l'écran à 900 et à 700 de haut (13/09)
node $SRC/temoin-rideau.mjs "http://127.0.0.1:$PORT/routing/index.html#tools" || { echo "REFUS : les boutons du rideau passent sous le pli" ; exit 6 ; }

echo "=== l'effondrement des blocs de texte (temoin-effondrement.mjs) $(date +%H:%M:%S)"
# 30/09 : les fiches des trouvailles faisaient 46 px sur téléphone, en ligne, sans qu'aucune garde le dise ;
# every served page, at each width the probe reads by default (its largeurs list): any paragraph of at least fifteen words is at least 45 % of the screen wide
EPAGES=(); for f in $(cd $SITE/docs && find . -name '*.html' | sed 's#^\./##' | sort); do EPAGES+=("http://127.0.0.1:$PORT/$f"); done
node $SRC/temoin-effondrement.mjs "${EPAGES[@]}" > $SORTIE/effondrement.log 2>&1 || { tail -4 $SORTIE/effondrement.log | cut -c1-200 ; echo "REFUS : un bloc de texte est écrasé ($SORTIE/effondrement.log)" ; exit 6 ; }
echo "  $(tail -1 $SORTIE/effondrement.log)"

echo "=== captures natives $(date +%H:%M:%S)"
sc() { echo "(()=>{const s=document.querySelector('.colle').parentElement; window.scrollTo(0, s.offsetTop + $1*s.offsetHeight)})()"; }
cap() { node $CAP "http://127.0.0.1:$PORT/$1" $2 $3 "$4" "$SORTIE/$5" 2>&1 | tail -1 | grep -q "$SORTIE" || echo "  capture indéterminée : $5"; }
for t in $OUTILS; do
  cap $t/index.html 1440 900 - $t-hero-1440.png
  for f in 0.30 0.50 0.70; do cap $t/index.html 1440 900 "$(sc $f)" $t-scene-$f-1440.png; done
  cap $t/index.html 375 812 - $t-hero-375.png
  cap $t/index.html 375 812 "$(sc 0.30)" $t-scene-0.30-375.png
  if command -v ffmpeg > /dev/null; then
    ffmpeg -y -loglevel error -i $SORTIE/$t-hero-1440.png -i $SORTIE/$t-scene-0.30-1440.png \
      -i $SORTIE/$t-scene-0.50-1440.png -i $SORTIE/$t-scene-0.70-1440.png \
      -filter_complex "[0][1][2][3]hstack=4,scale=2400:-1" $SORTIE/$t-bande.png
    echo "$t : 6 captures, bande $t-bande.png"
  else
    echo "$t : 6 captures (ffmpeg absent : pas de bande, dit)"
  fi
done

echo "=== les cinq instruments vivants (temoin-instrument.py) $(date +%H:%M:%S)"
# le trou du 10/09 : F.every devenu F.each dans deux bâtisseurs, cinq panneaux morts,
# assembleur et gardes aveugles — une page qui ne TOURNE plus ne doit pas s'émettre
python3 $SRC/temoin-instrument.py > $SORTIE/instruments.log 2>&1; code=$?
tail -2 $SORTIE/instruments.log | cut -c1-160
[ $code = 0 ] || { echo "REFUS : un instrument vivant ne tourne plus ($SORTIE/instruments.log)"; exit 6; }

echo "=== les tarifs au navigateur (temoin-tarifs.py) $(date +%H:%M:%S)"
python3 $SRC/temoin-tarifs.py --docs $SITE/docs > $SORTIE/tarifs.log 2>&1; code=$?
tail -2 $SORTIE/tarifs.log | cut -c1-160
[ $code = 0 ] || { echo "REFUS : la page des tarifs ne tient pas ($SORTIE/tarifs.log)"; exit 6; }

echo "=== porte mécanique (controle.mjs) $(date +%H:%M:%S)"
if [ -f $CTL ]; then
  for t in $OUTILS; do
    node $CTL "http://127.0.0.1:$PORT/$t/index.html" --sortie $SORTIE/ctl-$t > $SORTIE/ctl-$t.log 2>&1; code=$?
    echo "$t : controle code $code $(grep -iE "débord|exception|manquante|contraste|morte|propre" $SORTIE/ctl-$t.log | head -2 | tr '\n' ' ' | cut -c1-160)"
    # a gate that crashed before looking (missing module, dead symlink) prints no verdict:
    # that was a silent green from 13/09 to 27/09, so it refuses now, like a real defect
    grep -q "Mécanique propre" $SORTIE/ctl-$t.log || { grep -qiE "débord|exception|manquante|contraste|morte" $SORTIE/ctl-$t.log \
      && echo "REFUS : défaut mécanique sur $t ($SORTIE/ctl-$t.log)" \
      || echo "REFUS : la porte mécanique n'a pas regardé $t ($SORTIE/ctl-$t.log)"; exit 7; }
  done
else
  echo "SAUTÉE, dit : controle.mjs absent de cette machine ($CTL) — la porte mécanique n'a pas regardé"
fi
echo "=== fin $(date +%H:%M:%S) · sorties dans $SORTIE"
