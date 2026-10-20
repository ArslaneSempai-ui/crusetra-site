#!/usr/bin/env python3
"""THE WITNESS OF THE TOOL REPOSITORIES (depots.py, depots.json, depots.local.json).

  A. a repo configured on a branch other than its ref is REFUSED, by name, by the assembler
     itself (it must fail in seconds, before any build) and by depots.garder; a modified cited
     file is refused too;
  B. with this machine's depots.local.json (the checkouts of origin/main), the test counts read
     are the published ones: routing 880 / 103, monitoring 131 / 20, scoring 127 / 19;
  C. proof by removal: with the HEAD check removed from a copy of depots.py, A turns RED.

usage: python3 temoin-depots.py        0 = held ; 1 = refused
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ICI = pathlib.Path(__file__).resolve().parent
ATTENDU = {"routing": ("880", "103"), "monitoring": ("131", "20"), "scoring": ("127", "19")}
fautes = []


def git(depot, *args):
    subprocess.run(["git", "-C", str(depot), "-c", "user.name=t", "-c", "user.email=t@t.t", *args],
                   check=True, capture_output=True)


def depot_sur_autre_branche(racine):
    """A repo whose ref `main` is one commit behind HEAD, which sits on branch `feature`."""
    d = racine / "outil"
    d.mkdir()
    git(d, "init", "-q", "-b", "main")
    (d / "README.md").write_text("**1 tests** across 1 files\n")
    git(d, "add", "."); git(d, "commit", "-q", "-m", "one")
    git(d, "checkout", "-q", "-b", "feature")
    (d / "README.md").write_text("**2 tests** across 1 files\n")
    git(d, "commit", "-q", "-am", "two")
    return d


def config_locale(racine, depot):
    f = racine / "depots.local.json"
    f.write_text(json.dumps({"routing": {"chemin": str(depot), "ref": "main"}}))
    return f


def garde_refuse(dossier_source, local):
    """Run depots.garder("routing") from `dossier_source`; (code, output)."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import depots; "
            "depots.garder('routing'); print('READ')")
    r = subprocess.run([sys.executable, "-c", code, str(dossier_source)],
                       env={**os.environ, "DEPOTS_LOCAL": str(local)}, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    depot = depot_sur_autre_branche(t)
    local = config_locale(t, depot)
    MSG = "routing at %s is on feature, not main: point depots.local.json at a checkout of main" % depot

    # A1. the assembler refuses before building anything
    try:
        r = subprocess.run([sys.executable, str(ICI / "assembler.py")], capture_output=True, text=True,
                           env={**os.environ, "DEPOTS_LOCAL": str(local)}, timeout=90, cwd=str(ICI))
        sortie, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        sortie, rc = "assembler kept building: it read the wrong branch without a word", 0
    if rc == 0 or MSG not in sortie:
        fautes.append("A1 the assembler did not refuse a repo on another branch by name")

    # A2. the guard alone
    rc, sortie = garde_refuse(ICI, local)
    if rc == 0 or MSG not in sortie:
        fautes.append("A2 depots.garder did not refuse a repo on another branch by name")

    # A3. a modified cited file is refused on the right ref
    git(depot, "checkout", "-q", "main")
    (depot / "README.md").write_text("**999 tests** across 9 files\n")
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import depots; "
            "depots.garder('routing', ('README.md',)); print('READ')")
    r = subprocess.run([sys.executable, "-c", code, str(ICI)],
                       env={**os.environ, "DEPOTS_LOCAL": str(local)}, capture_output=True, text=True)
    if r.returncode == 0 or "modified files" not in (r.stdout + r.stderr):
        fautes.append("A3 a modified cited file was not refused")

    # C. proof by removal: the same check against a copy whose HEAD check is cut out
    git(depot, "checkout", "-q", "--", "README.md")
    git(depot, "checkout", "-q", "feature")
    copie = t / "copie"
    copie.mkdir()
    shutil.copy(ICI / "depots.json", copie / "depots.json")
    src = (ICI / "depots.py").read_text()
    coupe = re.sub(r"    if tete != cible:\n(?:        .*\n)+", "", src)
    if coupe == src:
        fautes.append("C the HEAD check could not be located in depots.py: the removal proof is void")
    (copie / "depots.py").write_text(coupe)
    rc, sortie = garde_refuse(copie, local)
    if rc != 0 or "READ" not in sortie:
        fautes.append("C with the HEAD check removed, A2 did not turn RED: the witness proves nothing")

# B. the counts of the origin/main checkouts named by this machine's depots.local.json
sys.path.insert(0, str(ICI))
try:
    import depots
except ImportError as e:
    fautes.append(f"B depots.py cannot be imported ({e})")
else:
    if not depots.LOCAL.exists() or "DEPOTS_LOCAL" in os.environ:
        fautes.append("B this machine has no depots.local.json: create it, pointing at checkouts of origin/main")
    else:
        for outil, attendu in ATTENDU.items():
            lu = depots.compte_tests(outil)
            if lu != attendu:
                fautes.append(f"B {outil}: read {lu}, expected {attendu}")

if fautes:
    print("TEMOIN DEPOTS REFUSE:\n  " + "\n  ".join(fautes))
    sys.exit(1)
print("depots witness held: other branch refused, dirty file refused, counts read, removal proof red")
