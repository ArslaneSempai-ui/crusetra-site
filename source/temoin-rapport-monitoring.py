#!/usr/bin/env python3
"""WITNESS OF THE MONITORING SAMPLE REPORT BUILDER (slice S3, 11/10): batir-rapport-monitoring.py reads the sealed
example record of cascade-monitoring (examples/amlworld), renders it with cascade-portes/outils/rapport-monitoring.py and
writes rapports/monitoring-sample-report.{html,pdf,json} and rendus/rapport-monitoring.webp.

It must REFUSE a record whose seal does not match, in words and with nothing written; it must build the real record into
one page whose sidecar carries that record's seal and says plainly that the page is not signed yet.

Nothing here touches the house key: the builder is run without --signe, and the tools that read a home folder run with a
home of their own.
usage: python3 temoin-rapport-monitoring.py [--keep]     (exit 0 when every case holds; --keep leaves the output folder)
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

BASE = pathlib.Path(__file__).parent
MAISON = pathlib.Path.home() / "Documents"
DEPOT = MAISON / "cascade-monitoring"
RECORD = DEPOT / "examples" / "amlworld" / "amlworld-alerts-measured.json"
BATISSEUR = BASE / "batir-rapport-monitoring.py"

rouge = 0


def dire(ok, quoi):
    global rouge
    print(("  vert  " if ok else "  ROUGE ") + quoi)
    if not ok:
        rouge = 1


def lancer(args, home=None):
    env = dict(os.environ)
    if home:
        env["HOME"] = str(home)
    return subprocess.run([sys.executable, str(BATISSEUR), *args], capture_output=True, text=True, env=env)


def vide(dossier):
    return not any(pathlib.Path(dossier).rglob("*"))


def main():
    garder = "--keep" in sys.argv
    if len(sys.argv) > 1 and sys.argv[1:] != ["--keep"]:
        sys.exit("usage: python3 temoin-rapport-monitoring.py [--keep]")
    if not BATISSEUR.exists():
        print(f"  ROUGE {BATISSEUR.name} does not exist: nothing to witness")
        return 1
    if not RECORD.exists():
        print(f"  ROUGE the example record is missing ({RECORD}): nothing to build from")
        return 1
    sortie = pathlib.Path(tempfile.mkdtemp(prefix="temoin-rapport-monitoring-"))
    try:
        maison = sortie / "maison"          # the monitoring tools write a first-use marker under HOME
        maison.mkdir()
        d = json.loads(RECORD.read_text(encoding="utf-8"))

        def variante(nom, modifier, resceller=False):
            e = json.loads(json.dumps(d))
            modifier(e)
            chemin = sortie / f"{nom}.json"
            chemin.write_text(json.dumps(e, indent=2), encoding="utf-8")
            if resceller:       # sealed again by the repository's own tool: the seal holds, the content is wrong
                subprocess.run(["node", str(DEPOT / "src" / "sceller.ts"), str(chemin)], capture_output=True,
                               env={**os.environ, "HOME": str(maison)}, check=True)
            return chemin

        def refus(nom, args, mot, quoi):
            out = sortie / f"out-{nom}"
            out.mkdir()
            r = lancer([*args, "--out", str(out)])
            dits = r.stdout + r.stderr
            if r.returncode == 0:
                dire(False, f"{nom}: {quoi} was built")
            elif "Traceback" in dits:
                dire(False, f"{nom}: {quoi} was refused with a traceback, not in words: {dits.strip().splitlines()[-1]}")
            elif not vide(out):
                dire(False, f"{nom}: {quoi} was refused but files were left behind: {[p.name for p in out.rglob('*')][:4]}")
            elif mot.lower() not in dits.lower():
                dire(False, f"{nom}: {quoi} was refused without saying why (\"{mot}\" absent): {dits.strip()[:160]}")
            else:
                dire(True, f"{nom}: {quoi} is refused in words, nothing written")

        # 1. a record that does not hold: edited after sealing, a seal altered, no seal, another kind, another version
        refus("modifie", ["--record", str(variante("modifie", lambda e: e["source"].__setitem__("suspicious", e["source"]["suspicious"] + 1)))],
              "does not match", "a record edited after it was sealed")
        refus("sceau", ["--record", str(variante("sceau", lambda e: e.__setitem__("empreinte", ("0" if e["empreinte"][0] != "0" else "1") + e["empreinte"][1:])))],
              "does not match", "a record whose seal was altered")
        refus("sans-sceau", ["--record", str(variante("sans-sceau", lambda e: e.pop("empreinte")))],
              "not sealed", "a record with no seal")
        refus("genre", ["--record", str(variante("genre", lambda e: e.__setitem__("kind", "crusetra-client-record"), resceller=True))],
              "not a monitoring record", "a record of another kind, validly sealed")
        refus("version", ["--record", str(variante("version", lambda e: e.__setitem__("version", 2), resceller=True))],
              "version", "a record of another version, validly sealed")
        refus("absent", ["--record", str(sortie / "n-existe-pas.json")], "does not exist", "a record that is not there")
        refus("option", ["--record", str(RECORD), "--nope"], "unknown option", "an unknown option")

        # 2. the real record builds: one page, the record's own seal in the sidecar, not signed, credit on the page
        out = sortie / "out-vrai"
        out.mkdir()
        r = lancer(["--record", str(RECORD), "--out", str(out)], home=None)
        if r.returncode != 0:
            dire(False, f"the real record was refused: {(r.stdout + r.stderr).strip()[-300:]}")
        else:
            html = out / "rapports" / "monitoring-sample-report.html"
            pdf = out / "rapports" / "monitoring-sample-report.pdf"
            side = out / "rapports" / "monitoring-sample-report.json"
            webp = out / "rendus" / "rapport-monitoring.webp"
            presents = all(p.exists() and p.stat().st_size > 0 for p in (html, pdf, side, webp))
            dire(presents, "the real record writes the page, the PDF, the sidecar and the page image")
            if presents:
                pages = re.search(r"^Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout, re.M)
                dire(bool(pages) and pages.group(1) == "1", f"the PDF is one page (pdfinfo: {pages.group(1) if pages else 'unreadable'})")
                s = json.loads(side.read_text(encoding="utf-8"))
                page = html.read_text(encoding="utf-8")
                dire(s.get("sceau") == d["empreinte"], "the sidecar carries the seal of the record it was built from")
                dire(s.get("signe") is False and 'id="signature"' not in page,
                     "the page is not signed and the sidecar says so (signing is Arslane's, with the house key)")
                dire(s.get("alertes") == d["source"]["alerts"] and s.get("suspects") == d["source"]["suspicious"]
                     and s.get("benins") == d["source"]["benign"], "the counts of the sidecar are read from the record")
                dire('id="rapport"' in page, "the page carries the id=\"rapport\" block that npm run verify reads")
                dire("Altman" in page and "CDLA-Sharing" in page,
                     "the page credits the data provider and names the licence (CDLA-Sharing 1.0, section 3.1)")
                dire("constructed" in page.lower(), "the page says the alerts are constructed, not raised by a system")
                dire("—" not in page and "—" not in json.dumps(s, ensure_ascii=False), "no em dash on the page or in the sidecar")
                dire(not any(x in page for x in ("/Users/", "arslanechr")), "no local path on the page")
        # 3. the detector of "nothing written" sees a planted file, or its zero would prove nothing
        plante = sortie / "out-plante"
        (plante / "rapports").mkdir(parents=True)
        (plante / "rapports" / "x.html").write_text("x")
        dire(not vide(plante) and vide(sortie / "out-modifie"), "the emptiness check sees a planted file, and the refused builds left none")
    finally:
        if garder:
            print(f"  output kept: {sortie}")
        else:
            shutil.rmtree(sortie, ignore_errors=True)
    return rouge


if __name__ == "__main__":
    sys.exit(main())
