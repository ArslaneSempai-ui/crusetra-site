"""THE MONITORING SAMPLE REPORT, READ AND CHECKED IN ONE PLACE (slice S4, 11/10).

batir-rapport-monitoring.py (slice S3) writes rapports/monitoring-sample-report.{html,pdf,json} from the sealed record of
cascade-monitoring examples/amlworld. Two readers depend on that sidecar: the Monitoring page's report section
(batir-hero.py) and the assembler. Both call verifier() below, so the guard is one function, not two copies that drift.

verifier() refuses, in words and before anything is built or any docs/ is touched:
  - a record that is not there;
  - a record that does not match its own seal, checked by cascade-monitoring's own `sceller.ts --check`, so an edit made after
    sealing is seen even when the sidecar still quotes the seal the record carries;
  - a sidecar whose seal is not the record's;
  - a sidecar whose counts do not recount on the record.
Each refusal says "Monitoring sample report" and what to run. Nothing here signs or serves anything."""
import json
import pathlib
import subprocess
import sys

from outil import OUTILS

COTE = pathlib.Path("rapports") / "monitoring-sample-report.json"
RECORD_DANS_LE_DEPOT = "examples/amlworld/amlworld-alerts-measured.json"


def verifier(base):
    """The sidecar and its record, once the seal and the counts have been checked; exits in words otherwise."""
    base = pathlib.Path(base)
    chemin = base / COTE
    if not chemin.exists():
        sys.exit(f"Monitoring sample report: source/{COTE} is not there: run batir-rapport-monitoring.py. Nothing was assembled.")
    ex = json.loads(chemin.read_text(encoding="utf-8"))
    rec_p = pathlib.Path.home() / "Documents" / ex["source"]
    if not rec_p.exists():
        sys.exit(f"Monitoring sample report: the record {ex['source']} is not there, so the sample cannot be checked. Nothing was assembled.")
    depot = OUTILS["monitoring"]["outil_chemin"]
    v = subprocess.run(["node", str(depot / "src" / "sceller.ts"), str(rec_p), "--check"], capture_output=True, text=True)
    if v.returncode != 0:
        sys.exit(f"Monitoring sample report: the record {rec_p.name} does not match its seal (sceller --check), so no sample is built "
                 f"on it:\n{(v.stdout + v.stderr).strip()}\nNothing was assembled.")
    rec = json.loads(rec_p.read_text(encoding="utf-8"))
    if rec["empreinte"] != ex["sceau"]:
        sys.exit(f"Monitoring sample report: the sidecar carries the seal {ex['sceau']} but the record carries {rec['empreinte']}: "
                 "run batir-rapport-monitoring.py again. Nothing was assembled.")
    if (ex["alertes"], ex["suspects"], ex["benins"]) != (rec["source"]["alerts"], rec["source"]["suspicious"], rec["source"]["benign"]):
        sys.exit("Monitoring sample report: the sidecar's counts do not recount on its record: run batir-rapport-monitoring.py again. "
                 "Nothing was assembled.")
    return ex, rec


def exemple_publie(depot):
    """True when cascade-monitoring's origin/main holds the sample's record, so a link to it or a command that clones the repository
    and runs the example would work. A LOCAL check, no fetch: `git cat-file -e origin/main:<record>` on the checkout. Until the example is
    merged and fetched, the section drops those links and commands rather than publish ones that 404."""
    r = subprocess.run(["git", "-C", str(depot), "cat-file", "-e", f"origin/main:{RECORD_DANS_LE_DEPOT}"], capture_output=True, text=True)
    return r.returncode == 0
