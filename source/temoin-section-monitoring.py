#!/usr/bin/env python3
"""WITNESS OF THE MONITORING REPORT SECTION AND OF THE ASSEMBLER'S GUARD ON ITS SAMPLE (slice S4, 11/10).

The Monitoring page carries a report section modelled on Routing's (the sample sheet, its PDF, the way to start). The
sample is the one slice S3 built: batir-rapport-monitoring.py wrote rapports/monitoring-sample-report.{html,pdf,json} and
rendus/rapport-monitoring.webp from the sealed record of cascade-monitoring examples/amlworld. This witness runs the real
builders and the real assembler on a COPY of the site (the assembler is anchored on the checkout that carries it, so the
copy's docs/ is the only one written; the real docs/ is never touched) and requires:

  - a sidecar whose seal differs from the sample's record refuses the assembly, in words, before anything is built;
  - a sidecar whose counts differ, a record edited after it was sealed (the sidecar still quoting the old seal), a sidecar
    that says the page is signed while the page is not: each refused;
  - the real sample passes: its PDF and image are served, the section is on the Monitoring page with the seal it was built
    from, the page that is not signed is not served and the section says nothing about a signature;
  - the offer part appears ONLY when source/offre-monitoring.json exists and shows every price read from it; a file that carries
    ANY statut (proposal, brouillon, draft, empty) refuses the build, because a chosen offer carries none (offre-routing.json and
    offre-screening.json carry none): no price is typed anywhere, no price leaves the house before it is chosen;
  - the links to the example folder and to the sealed record, and the commands that clone the repository and run the example,
    exist only when cascade-monitoring's origin/main holds the record (a local check, no fetch): until the example is merged
    they would 404, so the section drops them and keeps the sample, its PDF and the credit;
  - step 3 says "a sealed record and a report beside your file" without an offer, and "a one-page PDF" only with one;
  - the finding "no cell holds the declared recall floor" is followed by the sentence that the zscore and peer scenarios score
    nothing on the alerts that have no history, with the figure READ from the sidecar (sans_historique): the sample's own figure
    in the built page, another figure when the sidecar is planted with another, no sentence when the sidecar says none, and a
    sidecar without the field refused in words; the sentence is in both versions of the paragraph (example published or not).

The assembler may later stop on something that has nothing to do with Monitoring (another tool's citations, say); this
witness reads what the assembler did about Monitoring and says so when it stops elsewhere.
usage: python3 temoin-section-monitoring.py [--keep]     (exit 0 when every case holds)
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
RECORD = MAISON / "cascade-monitoring" / "examples" / "amlworld" / "amlworld-alerts-measured.json"
COTE = "rapports/monitoring-sample-report.json"
REL_RECORD = "examples/amlworld/amlworld-alerts-measured.json"
DEPOT = MAISON / "cascade-monitoring"
rouge = 0


def dire(ok, quoi):
    global rouge
    print(("  vert  " if ok else "  ROUGE ") + quoi)
    if not ok:
        rouge = 1


def lancer(src, script, *args):
    return subprocess.run([sys.executable, str(src / script), *args], cwd=src, capture_output=True, text=True)


def dits(r):
    return r.stdout + r.stderr


# The sentence about the alerts that have no history, in the two forms the page can print: "All N alerts ..." when every alert
# lacks history, "K of the N alerts ..." otherwise. The figures are read back from the HTML so that the witness compares what
# the page says with what the sidecar holds, never with a number typed here.
SANS_HISTORIQUE = re.compile(r"(?:All (\d+)|(\d+) of the (\d+)) alerts have no transaction before their window, "
                             r"so the zscore and peer scenarios[^<.]*\.")


def sans_historique_dit(html):
    """(K, N) the page states, or None when the sentence is absent: K alerts without history out of N."""
    m = SANS_HISTORIQUE.search(html)
    if not m:
        return None
    tous, k, n = m.groups()
    return (int(tous), int(tous)) if tous else (int(k), int(n))


def section_de(html):
    m = re.search(r'<section class="rapport" id="report">.*?</section>', html, re.S)
    return m.group(0) if m else ""


def refuse(r, *mots):
    """The run was refused, in the words asked for, with no traceback and WITHOUT the line the assembler prints when the sample
    passes: the assembler may stop later on something unrelated (so a nonzero exit alone proves nothing)."""
    t = dits(r)
    return r.returncode != 0 and all(m in t for m in mots) and "Traceback" not in t and "holds (record checked" not in t


class Copie:
    """A copy of source/ in a temporary folder: the builders and the assembler run there, never on the real tree."""

    def __init__(self, racine):
        self.site = racine / "site"
        self.src = self.site / "source"
        shutil.copytree(BASE, self.src, ignore=shutil.ignore_patterns("__pycache__", "*.avant-*", ".verif-final", "zz-*"))
        shutil.copy(BASE.parent / "README.md", self.site / "README.md")

    def sidecar(self, modifier=None):
        chemin = self.src / COTE
        d = json.loads(chemin.read_text(encoding="utf-8"))
        if modifier:
            modifier(d)
            chemin.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return d

    def remettre(self, octets_sidecar):
        (self.src / COTE).write_bytes(octets_sidecar)

    def docs(self, chemin):
        return self.site / "docs" / chemin

    def pointer_le_depot(self, depot):
        """Point the COPY's monitoring tool path at another checkout (outil.py names it once): the seam that lets the witness
        plant the state of origin/main without touching the real repository."""
        outil = self.src / "outil.py"
        t = outil.read_text(encoding="utf-8")
        a = '"outil_chemin": _MAISON / "cascade-monitoring",'
        assert t.count(a) == 1, "outil.py no longer names the monitoring checkout once: the witness cannot point the copy at a clone"
        outil.write_text(t.replace(a, f'"outil_chemin": __import__("pathlib").Path({str(depot)!r}),'), encoding="utf-8")


def main():
    garder = "--keep" in sys.argv
    if not (BASE / COTE).exists() or not RECORD.exists():
        print("  ROUGE the sample or its record is missing: nothing to witness")
        return 1
    racine = pathlib.Path(tempfile.mkdtemp(prefix="temoin-section-monitoring-"))
    try:
        c = Copie(racine)
        original = (c.src / COTE).read_bytes()
        side = json.loads(original)
        rec = json.loads(RECORD.read_text(encoding="utf-8"))

        # 1. the sidecar that does not match its record: refused, in words, before anything is built
        autre = ("0" if side["sceau"][0] != "0" else "1") + side["sceau"][1:]
        c.sidecar(lambda d: d.__setitem__("sceau", autre))
        r = lancer(c.src, "assembler.py")
        t = dits(r)
        dire(refuse(r, "Monitoring sample report", autre, side["sceau"]),
             "a sidecar whose seal differs from the sample's record refuses the assembly, in words, naming both seals")
        dire(not (c.site / "docs").exists(), "and the refusal comes before docs/ is touched")
        c.remettre(original)

        # 2. counts that do not recount, a record edited after sealing, a sidecar that claims a signature the page does not carry
        c.sidecar(lambda d: d.__setitem__("suspects", d["suspects"] + 1))
        r = lancer(c.src, "assembler.py")
        dire(refuse(r, "Monitoring sample report", "do not recount"),
             "a sidecar whose counts do not recount on the record is refused in words")
        c.remettre(original)
        edite = racine / "record-edite.json"
        e = json.loads(json.dumps(rec))
        e["source"]["suspicious"] += 1                 # content moved, the seal field untouched: the sidecar still quotes it
        edite.write_text(json.dumps(e, indent=2), encoding="utf-8")
        c.sidecar(lambda d: d.__setitem__("source", os.path.relpath(edite, MAISON)))
        r = lancer(c.src, "assembler.py")
        dire(refuse(r, "Monitoring sample report", "does not match its seal"),
             "a record edited after it was sealed is refused even when the sidecar quotes the seal it still carries")
        c.remettre(original)
        c.sidecar(lambda d: d.__setitem__("signe", True))
        r = lancer(c.src, "assembler.py")
        dire(r.returncode != 0 and "does not verify" in dits(r) and "Monitoring" in dits(r) and "Traceback" not in dits(r),
             "a sidecar that says the page is signed, over a page that is not, is refused by the verifier")
        c.remettre(original)

        # 3. the real sample: served, in the page, with the seal it was built from, unsigned and saying nothing about a signature
        r = lancer(c.src, "assembler.py")
        t = dits(r)
        dire(f"Monitoring sample report: seal {side['sceau']} holds" in t, "the real sample passes the assembler's guard, which says so")
        pdf, webp = c.docs("rapports/monitoring-sample-report.pdf"), c.docs("rendus/rapport-monitoring.webp")
        dire(pdf.exists() and pdf.read_bytes()[:5] == b"%PDF-" and webp.exists() and webp.read_bytes()[8:12] == b"WEBP",
             "the sample's PDF and page image are served")
        dire(pdf.exists() and not c.docs("rapports/monitoring-sample-report.html").exists(),
             "the sample page is NOT served while the sidecar says it is not signed (signe false)")
        page = c.docs("monitoring/index.html")
        html = page.read_text(encoding="utf-8") if page.exists() else ""
        m = re.search(r'<section class="rapport" id="report">.*?</section>', html, re.S)
        section = m.group(0) if m else ""
        dire(bool(section), "the Monitoring page carries the report section")
        dire("../rapports/monitoring-sample-report.pdf" in section and "../rendus/rapport-monitoring.webp" in section
             and side["sceau"] in section, "the section links the PDF and the image and names the seal the sample was built from")
        dire(rec["empreinte"] == side["sceau"] and f"{side['alertes']} constructed alerts" in section,
             "the figures in the section are read from the sidecar and its record")
        dire(sans_historique_dit(section) == (side["sans_historique"], side["alertes"]),
             "the section says the zscore and peer scenarios score nothing on the alerts without history, with the sidecar's own figure")
        dire(bool(section) and "signed" not in section.lower() and "verify" not in section.lower(),
             "the section says nothing about a signature while the sample is not signed")
        dire(bool(section) and not re.search(r"\$\d", section) and 'class="r-offre"' not in section,
             "no price and no offer block while source/offre-monitoring.json does not exist")
        dire(bool(section) and chr(0x2014) not in section, "no em dash in the section")
        if r.returncode != 0:
            print("  note  the assembler later stopped on something else; last lines:")
            for ligne in t.strip().splitlines()[-3:]:
                print("        " + ligne[:150])

        # 3b. the figure of the no-history sentence is READ from the sidecar: another figure changes it, none removes it, and a
        #     sidecar without the field or with an impossible one is refused in words (the builder is run alone, on the copy)
        plante = 777
        assert side["sans_historique"] != plante, "the planted figure equals the real one: the case below would prove nothing"
        c.sidecar(lambda d: d.__setitem__("sans_historique", plante))
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        dire(r.returncode == 0 and sans_historique_dit(section_de(h)) == (plante, side["alertes"]),
             f"a sidecar planted with another figure ({plante}) changes the sentence: it is read from the sidecar, not typed")
        c.sidecar(lambda d: d.__setitem__("sans_historique", 0))
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        dire(r.returncode == 0 and bool(section_de(h)) and "have no transaction before their window" not in section_de(h),
             "a sidecar that says no alert lacks history carries no such sentence")
        c.sidecar(lambda d: d.pop("sans_historique"))
        r = lancer(c.src, "batir-hero.py")
        dire(refuse(r, "Monitoring sample report", "sans_historique"),
             "a sidecar without sans_historique is refused in words, not with a traceback")
        c.sidecar(lambda d: d.__setitem__("sans_historique", d["alertes"] + 1))
        r = lancer(c.src, "batir-hero.py")
        dire(refuse(r, "Monitoring sample report", "sans_historique"),
             "a sidecar that counts more alerts without history than alerts is refused in words")
        c.remettre(original)

        # 4. the offer part: only when the offer file exists, every price read from it, and never with a statut
        offre = {"essai": {"alertes": 111, "delai_heures": 13},          # a chosen offer carries no statut, like offre-routing.json
                 "snapshot": {"alertes": 2222, "fenetres": 1, "delai_heures": 14, "prix_usd": 1234},
                 "audit": {"alertes": 33333, "fenetres": 3, "delai_heures": 15, "prix_usd": 5678},
                 "audit_trimestriel": {"remesures_par_an": 6, "prix_usd_an": 9012},
                 "contact": "contact@crusetra.com", "donnees": "A planted sentence about the data.",
                 "frais_fournisseurs": "A planted sentence about the fees."}
        chemin = c.src / "offre-monitoring.json"
        chemin.write_text(json.dumps(offre), encoding="utf-8")
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        dire(r.returncode == 0 and 'class="r-offre"' in h and all(x in h for x in ("$1,234", "$5,678", "$9,012")),
             "with an offer file that carries no statut, the offer part appears and shows every price read from it")
        dire("A planted sentence about the data." in h and "A planted sentence about the fees." in h,
             "the notes under the prices are read from the offer file too")
        dire("a sealed record and a one-page PDF" in h and "a sealed record and a report beside your file" not in h,
             "with an offer, step 3 promises the one-page PDF")
        for statut in ("proposal", "brouillon", "DRAFT, not chosen: a proposal", "", "decided"):
            chemin.write_text(json.dumps({**offre, "statut": statut}), encoding="utf-8")
            r = lancer(c.src, "batir-hero.py")
            dire(r.returncode != 0 and "offre-monitoring.json" in dits(r) and "statut" in dits(r) and "Traceback" not in dits(r),
                 f"an offer file that carries the statut {statut!r} refuses the build, in words: a chosen offer carries none")
        chemin.unlink()
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        dire(r.returncode == 0 and 'class="rapport" id="report"' in h and 'class="r-offre"' not in h,
             "without the offer file the report section is still there and the offer part is gone again")
        dire("a sealed record and a report beside your file" in h and "one-page" not in h,
             "without an offer, step 3 says a sealed record and a report beside your file, and promises no one-page PDF")

        # 5. the links to the example and the commands that run it: only when origin/main holds the record (planted in a clone)
        clone = racine / "monitoring-clone"
        tete = subprocess.run(["git", "-C", str(DEPOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(DEPOT), str(clone)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(clone), "checkout", "--quiet", tete], check=True, capture_output=True)
        git = lambda *a: subprocess.run(["git", "-C", str(clone), *a], capture_output=True, text=True)
        git("update-ref", "-d", "refs/remotes/origin/main")                 # the state to plant: origin/main without the record
        dire(git("cat-file", "-e", f"origin/main:{REL_RECORD}").returncode != 0 and git("cat-file", "-e", f"HEAD:{REL_RECORD}").returncode == 0,
             "the clone holds the record on its HEAD and not on origin/main: the state to plant is the one planted")
        c.pointer_le_depot(clone)
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        sec = (re.search(r'<section class="rapport" id="report">.*?</section>', h, re.S) or [""])[0]
        dire(r.returncode == 0 and bool(sec) and "examples/amlworld" not in sec and "map-alerts" not in sec and "git clone" not in sec,
             "while origin/main lacks the record, the section has no link to the example folder or the record and no command that runs it")
        dire(bool(sec) and "../rapports/monitoring-sample-report.pdf" in sec and "Altman" in sec and "https://cdla.dev/sharing-1-0/" in sec,
             "and it still shows the sample, its PDF and the credit to the provider with the licence link")
        dire("About the sample" in sec and sans_historique_dit(sec) == (side["sans_historique"], side["alertes"]),
             "in that version of the paragraph too, the no-history sentence is there with the sidecar's figure")
        git("update-ref", "refs/remotes/origin/main", tete)                 # the record is now on origin/main (planted, no fetch)
        r = lancer(c.src, "batir-hero.py")
        h = (c.src / "HERO-MONITORING.html").read_text(encoding="utf-8")
        sec = (re.search(r'<section class="rapport" id="report">.*?</section>', h, re.S) or [""])[0]
        dire(r.returncode == 0 and "/blob/main/examples/amlworld/amlworld-alerts-measured.json" in sec and "/tree/main/examples/amlworld" in sec
             and "map-alerts.ts" in sec, "once origin/main holds the record, the links and the commands are there")
        dire("Start with public data" in sec and sans_historique_dit(sec) == (side["sans_historique"], side["alertes"]),
             "and in that version of the paragraph too, the no-history sentence is there with the sidecar's figure")
    finally:
        if garder:
            print(f"  copy kept: {racine}")
        else:
            shutil.rmtree(racine, ignore_errors=True)
    return rouge


if __name__ == "__main__":
    sys.exit(main())
