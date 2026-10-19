#!/usr/bin/env python3
"""Régénère le fichier d'ancres d'un outil : pour chaque citation « fichier:ligne »
que les pages bâties portent (« Where it lives »), le contenu EXACT de la ligne
visée dans le dépôt de l'outil. La garde de assembler.py compare ensuite chaque
citation à cette ancre, ligne à ligne.

  python3 ancrer-citations.py routing      # pages vertes  → ancres-citations.json
  python3 ancrer-citations.py screening    # pages rouges  → ancres-citations-screening.json

À lancer APRÈS un changement VOULU de l'outil ou des JSON, jamais pour faire
taire la garde : une citation qui pointe au-delà du fichier, ou sur un fichier
absent, REFUSE ici même ; le fichier d'ancres n'est pas écrit.
"""
import json
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).parent
sys.path.insert(0, str(ICI))
from outil import OUTILS  # noqa: E402

CITATION = re.compile(r"[A-Za-z0-9_./-]+\.(?:ts|mjs|json|md|js):\d+")
PAGES = {
    "routing": ["ACCUEIL.html", "HERO.html", "INSTRUMENT.html", "ENGAGEMENT.html", "ANNEXE-METHODE.html",
                "ANNEXE-SECURITE.html", "ANNEXE-QUESTIONS.html", "ANNEXE-TERMS.html",
                "ANNEXE-PRIVACY.html", "ANNEXE-ACCESSIBILITE.html", "CONTACT.html", "MENTIONS.html"],
    "screening": ["HERO-SCREENING.html", "INSTRUMENT-SCREENING.html",
                  "ANNEXE-SCREENING-METHODE.html", "ANNEXE-SCREENING-SECURITE.html"],
    "monitoring": ["HERO-MONITORING.html", "INSTRUMENT-MONITORING.html",
                   "ANNEXE-MONITORING-METHODE.html", "ANNEXE-MONITORING-SECURITE.html"],
    "scoring": ["HERO-SCORING.html", "INSTRUMENT-SCORING.html",
                "ANNEXE-SCORING-METHODE.html", "ANNEXE-SCORING-SECURITE.html"],
    "dossier": ["HERO-DOSSIER.html", "INSTRUMENT-DOSSIER.html",
                "ANNEXE-DOSSIER-METHODE.html", "ANNEXE-DOSSIER-SECURITE.html"],
}
SORTIE = {"routing": "ancres-citations.json", "screening": "ancres-citations-screening.json",
          "monitoring": "ancres-citations-monitoring.json", "scoring": "ancres-citations-scoring.json",
          "dossier": "ancres-citations-dossier.json"}

outil_id = sys.argv[1] if len(sys.argv) > 1 else ""
if outil_id not in PAGES:
    sys.exit(f"usage : ancrer-citations.py {'|'.join(PAGES)}")
depot = OUTILS[outil_id]["outil_chemin"]

citees = set()
for nom in PAGES[outil_id]:
    p = ICI / nom
    if not p.exists():
        sys.exit(f"{nom} absent : bâtir les pages avant d'ancrer")
    citees |= set(CITATION.findall(p.read_text()))

ancres, fautes = {}, []
for c in sorted(citees):
    chemin, n = c.rsplit(":", 1)
    f = depot / chemin
    if not f.exists():
        fautes.append(f"{c} : fichier absent de {depot}")
        continue
    lignes = f.read_text(errors="replace").splitlines()
    n = int(n)
    if n < 1 or n > len(lignes):
        fautes.append(f"{c} : au-delà de la fin ({len(lignes)} lignes)")
        continue
    if not lignes[n - 1].strip():
        fautes.append(f"{c} : la ligne visée est vide, la citation ne désigne rien")
        continue
    ancres[c] = lignes[n - 1].strip()

if fautes:
    sys.exit("CITATIONS QUI NE DÉSIGNENT RIEN (corriger les JSON, pas les ancres) :\n  "
             + "\n  ".join(fautes))

# le dépôt s'écrit relatif à la maison (~) : le site promet le caviardage des chemins
# locaux et sa garde de poussée refuse un /Users/… dans un fichier publié
# the tracked default path (depots.json), not the machine's override: the published text must not change with depots.local.json
import depots  # noqa: E402
depot_public = "~/" + json.loads(depots.DEFAUT.read_text())[outil_id]["chemin"]
(ICI / SORTIE[outil_id]).write_text(json.dumps({
    "_": (f"Pour chaque « Where it lives » des pages {outil_id} : le contenu EXACT de la "
          f"ligne visée dans {depot_public}. La garde de assembler.py refuse de bâtir si une "
          "citation ne pointe plus dessus. Régénérer avec ancrer-citations.py APRÈS un "
          "changement volontaire de l'outil, jamais pour faire taire la garde."),
    "ancres": ancres,
}, ensure_ascii=False, indent=2) + "\n")
print(f"{SORTIE[outil_id]} : {len(ancres)} ancres, {len(PAGES[outil_id])} pages, dépôt {depot}")
