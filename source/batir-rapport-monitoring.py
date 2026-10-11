#!/usr/bin/env python3
"""THE SAMPLE REPORT on the Monitoring page (11/10, slice S3): the public example of cascade-monitoring (examples/amlworld,
the synthetic IBM AMLworld transactions mapped to constructed alerts, sealed record) rendered by the same renderer that
makes client reports (cascade-portes/outils/rapport-monitoring.py), so the sample is the product and nothing else.

usage: python3 batir-rapport-monitoring.py [--record <sealed record>] [--out <folder>] [--signe]
Writes <out>/rapports/monitoring-sample-report.{html,pdf,json} and <out>/rendus/rapport-monitoring.webp (page 1); <out>
defaults to this folder. The sidecar .json carries the record's seal, the date, the counts read from the record, and whether
the page is signed: the assembler refuses a sidecar whose seal no longer matches the record.

THE SEAL IS CHECKED FIRST, by cascade-monitoring's own `sceller.ts --check` (it never writes). A record whose seal does not
hold, whose kind or version is not the renderer's, or that is not there is refused in words and nothing is written. The whole
build happens in a temporary folder and is copied into <out> only when every step has passed, so a failure also leaves an
earlier good build in place.

WITHOUT --signe THE PAGE IS NOT SIGNED, and the sidecar says "signe": false. --signe signs it with the house key through
cascade-portes/outils/signer-rapport.mjs (the key is read there and never printed) and checks the result with
cascade-monitoring's verifier: that is Arslane's gesture, or his oui. This script never signs by itself."""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

BASE = pathlib.Path(__file__).parent
MAISON = pathlib.Path.home() / "Documents"
DEPOT = MAISON / "cascade-monitoring"
RECORD_DEFAUT = DEPOT / "examples" / "amlworld" / "amlworld-alerts-measured.json"
RENDU = MAISON / "cascade-portes" / "outils" / "rapport-monitoring.py"
SIGNEUR = MAISON / "cascade-portes" / "outils" / "signer-rapport.mjs"
CAPTURE = BASE / "capturer-rapport.mjs"
# what the page says about the data, under the title: the credit CDLA-Sharing 1.0 asks for (section 3.1) and what the alerts are
DATA = ("Sample on public data, not a client's file. The alerts were constructed by Crusetra from the synthetic IBM AMLworld transactions "
        "(Erik Altman and IBM, CDLA-Sharing 1.0, changed from the original): AMLworld labels transactions, and no monitoring system raised "
        "these alerts. Read \"your\" below as \"this file's\".")

argv = sys.argv[1:]
VALEUR = ("--record", "--out")
for i, a in enumerate(argv):
    if a.startswith("--") and a not in VALEUR + ("--signe",) and (i == 0 or argv[i - 1] not in VALEUR):
        sys.exit(f"unknown option {a}: this script accepts {', '.join(VALEUR + ('--signe',))}")
def option(nom, defaut=None):
    return argv[argv.index(nom) + 1] if nom in argv and argv.index(nom) + 1 < len(argv) else defaut
RECORD = pathlib.Path(option("--record", str(RECORD_DEFAUT)))
SORTIE = pathlib.Path(option("--out", str(BASE))).resolve()
SIGNER = "--signe" in argv
# the floor the report holds the recall to: the tool's own declared default, read from its source, never typed here
PLANCHER = re.search(r"^\s*recallFloor: ([0-9.]+),", (DEPOT / "src" / "assumptions.ts").read_text(), re.M).group(1)

if not RECORD.exists():
    sys.exit(f"{RECORD} does not exist: there is no record to build the sample from. Nothing was written.")
# 1. the seal, by the repository's own tool
verdict = subprocess.run(["node", str(DEPOT / "src" / "sceller.ts"), str(RECORD), "--check"], capture_output=True, text=True)
if verdict.returncode != 0:
    sys.exit(f"the seal of {RECORD.name} does not hold, so no sample is built from it.\n{(verdict.stdout + verdict.stderr).strip()}\nNothing was written.")
d = json.loads(RECORD.read_text(encoding="utf-8"))

with tempfile.TemporaryDirectory(prefix="batir-rapport-monitoring-") as tmpdir:
    # 2. a copy of the served layout (the page links ../fontes), so the page and its capture are the ones the site serves
    t = pathlib.Path(tmpdir)
    (t / "rapports").mkdir()
    (t / "rendus").mkdir()
    os.symlink(BASE / "fontes", t / "fontes")
    nu = t / "rapports" / "_page.html"
    html, pdf, webp, cote = (t / "rapports" / "monitoring-sample-report.html", t / "rapports" / "monitoring-sample-report.pdf",
                             t / "rendus" / "rapport-monitoring.webp", t / "rapports" / "monitoring-sample-report.json")
    r = subprocess.run([sys.executable, str(RENDU), str(RECORD), str(nu), "--recall", PLANCHER, "--data", DATA, "--fontes", "../fontes",
                        "--client", f"Sample: {d['source']['alerts']} constructed alerts from IBM AMLworld"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"the renderer refused {RECORD.name}:\n{(r.stdout + r.stderr).strip()}\nNothing was written.")
    bloc = json.loads(re.search(r'<script type="application/json" id="rapport">(.*?)</script>', nu.read_text(encoding="utf-8"), re.S).group(1))

    # 3. unsigned by default; signed only on --signe, then read back by the repository's verifier
    verifie = None
    if SIGNER:
        s = subprocess.run(["node", str(SIGNEUR), str(nu), str(html)], capture_output=True, text=True)
        if s.returncode != 0:
            sys.exit(f"the house signer refused:\n{(s.stdout + s.stderr).strip()}\nNothing was written.")
        v = subprocess.run(["node", str(DEPOT / "src" / "verifier-rapport.mjs"), str(html)], capture_output=True, text=True)
        if v.returncode != 0 or "Signature valid" not in v.stdout:
            sys.exit(f"the signed sample report does not verify:\n{(v.stdout + v.stderr).strip()}\nNothing was written.")
        verifie = v.stdout.strip().splitlines()[0].strip()
    else:
        nu.rename(html)
    c = subprocess.run(["node", str(CAPTURE), str(html), str(pdf), str(webp)], capture_output=True, text=True)
    if c.returncode != 0:
        sys.exit(f"the capture failed:\n{(c.stdout + c.stderr).strip()[-400:]}\nNothing was written.")

    side = {"sceau": d["empreinte"], "mesure": d["measuredAt"][:10], "commit": d["code"]["commit"],
            "alertes": d["source"]["alerts"], "suspects": d["source"]["suspicious"], "benins": d["source"]["benign"],
            "sans_historique": d["source"]["sansHistorique"], "plancher": float(PLANCHER), "recommandation": bloc["recommendation"],
            "signe": SIGNER, "verifie": verifie, "licence_des_donnees": "CDLA-Sharing-1.0",
            "source": "cascade-monitoring/examples/amlworld/amlworld-alerts-measured.json"}
    cote.write_text(json.dumps(side, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 4. every step passed: only now does anything reach <out>
    (SORTIE / "rapports").mkdir(parents=True, exist_ok=True)
    (SORTIE / "rendus").mkdir(parents=True, exist_ok=True)
    for src in (html, pdf, cote):
        shutil.copy2(src, SORTIE / "rapports" / src.name)
    shutil.copy2(webp, SORTIE / "rendus" / webp.name)
    print("monitoring sample report:", pdf.stat().st_size // 1024, "KB pdf,", webp.stat().st_size // 1024, "KB page image, seal", side["sceau"],
          "|", ("signed, " + verifie) if SIGNER else "NOT signed (run with --signe on Arslane's oui)")
