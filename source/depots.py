"""THE TOOL REPOSITORIES THE SITE READS, WRITTEN ONCE.

The builders used to read the tool repos at fixed paths and took test counts and cited lines
from whatever branch happened to be checked out there (19 October 2026: the site published the
test count of an unpublished local branch). Now:

  - depots.json (tracked) names each tool, its default path relative to the home folder
    and the ref the site must be built from ("origin/main");
  - depots.local.json (gitignored, optional) overrides the paths on this machine, e.g. to point at a
    clean worktree of origin/main. A path there may be home-relative or absolute;
  - garder() refuses, by name, a repo whose HEAD is not its configured ref, or whose cited
    files are dirty. It only reads refs: it never fetches, never falls back silently.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
DEFAUT = ICI / "depots.json"
# DEPOTS_LOCAL points the override file elsewhere (the witness uses it); unset, it is depots.local.json
LOCAL = pathlib.Path(os.environ.get("DEPOTS_LOCAL") or ICI / "depots.local.json")


def charger(defaut=DEFAUT, local=LOCAL):
    """tool -> {"chemin": Path, "ref": str}, the local file overriding the tracked one."""
    cfg = json.loads(pathlib.Path(defaut).read_text())
    cfg = {k: dict(v) for k, v in cfg.items() if not k.startswith("_")}
    local = pathlib.Path(local)
    if local.exists():
        for k, v in json.loads(local.read_text()).items():
            if k.startswith("_"):
                continue
            if k not in cfg:
                sys.exit(f"{local.name} names {k!r}, which {pathlib.Path(defaut).name} does not know")
            cfg[k].update(v)
    for v in cfg.values():
        p = pathlib.Path(v["chemin"])
        v["chemin"] = p if p.is_absolute() else pathlib.Path.home() / p
    return cfg


def _git(depot, *args):
    r = subprocess.run(["git", "-C", str(depot), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def garder(outil, fichiers=(), config=None):
    """Return the repo path of `outil` after proving it is on its configured ref and that the
    `fichiers` (relative paths it will read) are not modified. Refuses with a named message."""
    cfg = config if config is not None else charger()
    if outil not in cfg:
        sys.exit(f"depots: unknown tool {outil!r}")
    depot, ref = cfg[outil]["chemin"], cfg[outil]["ref"]
    code, tete = _git(depot, "rev-parse", "HEAD")
    if code != 0:
        sys.exit(f"{outil} at {depot} is not a git checkout: point depots.local.json at a checkout of {ref}")
    _, branche = _git(depot, "rev-parse", "--abbrev-ref", "HEAD")
    quoi = tete[:9] if branche in ("", "HEAD") else branche
    rc, cible = _git(depot, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if rc != 0:
        sys.exit(f"{outil} at {depot} has no ref {ref}: point depots.local.json at a checkout of {ref}")
    if tete != cible:
        sys.exit(f"{outil} at {depot} is on {quoi}, not {ref}: "
                 f"point depots.local.json at a checkout of {ref}")
    if fichiers:
        _, sale = _git(depot, "status", "--porcelain", "--untracked-files=no", "--", *map(str, fichiers))
        if sale:
            sys.exit(f"{outil} at {depot} has modified files it is cited for ({sale.splitlines()[0][3:]}"
                     f"{', ...' if len(sale.splitlines()) > 1 else ''}): "
                     f"point depots.local.json at a clean checkout of {ref}")
    return depot


def chemin(outil, config=None):
    """The guarded repo path of a tool (HEAD on its ref)."""
    return garder(outil, (), config)


def resoudre(relatif, config=None):
    """A path written relative to the home Documents folder ("cascade-screening/x.json"): when its
    first segment is a configured tool repo, read it through the guard; otherwise as is."""
    cfg = config if config is not None else charger()
    premier, _, reste = relatif.partition("/")
    par_dossier = {pathlib.Path(v["chemin"]).name: k
                   for k, v in json.loads(DEFAUT.read_text()).items() if not k.startswith("_")}
    if premier in par_dossier:
        return garder(par_dossier[premier], (), cfg) / reste
    return pathlib.Path.home() / "Documents" / relatif


def compte_tests(outil, config=None):
    """(tests, files or None) as the tool's README states them, read through the guard."""
    depot = garder(outil, ("README.md",), config)
    m = re.search(r"\*\*(\d+) tests\*\*(?: across (\d+) files)?", (depot / "README.md").read_text())
    if not m:
        sys.exit(f"the test sentence is not in {depot / 'README.md'}")
    return m.group(1), m.group(2)


def garder_tous(config=None):
    """Guard every configured tool repo that exists on this machine, before anything is read."""
    cfg = config if config is not None else charger()
    for outil, v in cfg.items():
        if v["chemin"].exists():
            garder(outil, (), cfg)
    return cfg
