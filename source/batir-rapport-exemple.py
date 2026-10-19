#!/usr/bin/env python3
"""THE SAMPLE REPORT on the Screening page (29/09): the public example of the screening tool (exemple/contreparties-exemple.csv,
30 invented counterparties of an invented forwarder) rendered by the same renderer that makes client reports, so the sample
is the product and nothing else.

05/10 (client journey audit): the PDF on the site is the RENDERING OF A FRESH RUN of that same file at the current matcher,
made with the client chain (rapport.py, then pieces/pdf.mjs, as rapport-essai.sh does). The committed example record of
cascade-screening is neither resealed nor re-signed by this script: `--record <fresh>.screening.json` names the fresh run,
which is copied beside the PDF (source/rapports/screening-sample-report.screening.json) so the seal the card names can be
checked, and the sidecar carries both seals. The fresh run must screen the same file (SHA-256) and give the same counts as
the committed record; otherwise the card would describe two different reports, and this script refuses.
Without --record, the committed record itself is rendered, as before.

Writes source/rapports/screening-sample-report.pdf, source/rapports/screening-sample-report.screening.json (the record the
PDF renders), the sidecar .json (both seals, dates, counts read from the records), and source/rendus/rapport-exemple.webp
(page 1). The assembler refuses a sidecar whose seals no longer match the records."""
import json, pathlib, shutil, subprocess, sys
BASE = pathlib.Path(__file__).parent
import depots
MAISON = pathlib.Path.home() / "Documents"   # the private tooling (portes, equipe), not a tool repo
RECORD = depots.chemin("screening") / "exemple" / "contreparties-exemple.screening.json"
RENDU = MAISON / "cascade-portes" / "outils" / "rapport.py"
PDF_MJS = MAISON / "equipe-cascade" / "pieces" / "pdf.mjs"
d = json.loads(RECORD.read_text())
FRAIS = pathlib.Path(sys.argv[sys.argv.index("--record") + 1]) if "--record" in sys.argv else RECORD
if not FRAIS.exists():
    sys.exit(f"{FRAIS} does not exist: run the screening into a scratch folder first (rapport-essai.sh's chain)")
fr = json.loads(FRAIS.read_text())
if fr["fichier"]["sha256"] != d["fichier"]["sha256"]:
    sys.exit(f"the fresh run screened another file ({fr['fichier']['nom']}, SHA-256 {fr['fichier']['sha256'][:16]}): the card would not describe the committed example")
if (fr["totaux"]["forts"], fr["totaux"]["possibles"], fr["totaux"]["sansCorrespondance"]) != (d["totaux"]["forts"], d["totaux"]["possibles"], d["totaux"]["sansCorrespondance"]):
    sys.exit(f"the fresh run counts {fr['totaux']} and the committed record {d['totaux']}: two different reports, refused; "
             "refresh the committed example in cascade-screening first (scripts/exemple.sh)")
(BASE / "rapports").mkdir(exist_ok=True); tmp = BASE / "rapports" / "_page.html"
subprocess.run([sys.executable, str(RENDU), str(FRAIS), str(tmp)], check=True, capture_output=True)
pdf, webp = BASE / "rapports" / "screening-sample-report.pdf", BASE / "rendus" / "rapport-exemple.webp"
# the PDF a client receives: the same pdf.mjs step as rapport-essai.sh; the page-1 image comes from the site's capture script
subprocess.run(["node", str(PDF_MJS), tmp.as_uri(), str(pdf)], check=True, capture_output=True)
tmp_pdf = BASE / "rapports" / "_page.pdf"
subprocess.run(["node", str(BASE / "capturer-rapport.mjs"), str(tmp), str(tmp_pdf), str(webp)], check=True, capture_output=True)
tmp.unlink(); tmp_pdf.unlink()
texte = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
# the count the renderer prints is the record's own (rapport.py, MOTS): seven lists before the sources-plus merge, ten
# after it. The check reads it from the rendered record, so a typed count cannot fall behind the tool.
EN_LETTRES = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}   # rapport.py's MOTS, digits beyond
for attendu in (f"{EN_LETTRES.get(len(fr['listes']), len(fr['listes']))} sanctions lists", "GLEIF"):
    if attendu not in texte:
        sys.exit(f"the rendered sample report does not say « {attendu} »: the rendering is not the current rapport.py")
if "separate author" in texte:
    sys.exit("the rendered sample report still says « separate author »: the rendering is not the current rapport.py")
shutil.copy(FRAIS, BASE / "rapports" / "screening-sample-report.screening.json")
t = d["totaux"]
side = {"sceau": d["empreinte"], "emis": d["emisLe"][:10], "client": d["client"], "lignes": t["lignes"], "forts": t["forts"],
        "possibles": t["possibles"], "sans": t["sansCorrespondance"], "commit": d["commit"],
        "listes": min(l["telechargeLe"][:10] for l in d["listes"]), "source": "cascade-screening/exemple/contreparties-exemple.screening.json",
        "rendu": {"empreinte": fr["empreinte"], "emis": fr["emisLe"][:10], "commit": fr["commit"],
                  "listes": sorted({l["telechargeLe"][:10] for l in fr["listes"]}),
                  "fichier": "rapports/screening-sample-report.screening.json",
                  "chaine": "rapport.py + pieces/pdf.mjs, the client chain of rapport-essai.sh"}}
(BASE / "rapports" / "screening-sample-report.json").write_text(json.dumps(side, indent=2) + "\n")
print("sample report:", pdf.stat().st_size // 1024, "KB pdf,", webp.stat().st_size // 1024, "KB page image, committed seal", side["sceau"],
      "| rendered run", fr["empreinte"], "at", fr["commit"], "of", side["rendu"]["emis"])
