#!/usr/bin/env python3
"""THE SAMPLE REPORT on the Routing page (30/09): the public real run of the extraction cost audit (the 100 receipts of
CORD v2's test split, cascade-routing examples/cord-receipts, sealed record ac7d0adbe4907caf) rendered by the same
renderer that makes client reports, so the sample is the product and nothing else.
Writes source/rapports/routing-sample-report.pdf, its sidecar .json (seal, date, routing and figures read from the
record), and source/rendus/rapport-routing.webp (page 1). The assembler refuses a sidecar whose seal no longer matches
the record."""
import json, pathlib, subprocess, sys
BASE = pathlib.Path(__file__).parent
import depots
MAISON = pathlib.Path.home() / "Documents"   # the private tooling (portes), not a tool repo
ROUTING = depots.chemin("routing")   # HEAD on its configured ref (depots.json)
# the public copy once PR #10 is merged into main; until then, the identical private copy (same seal, checked below)
PUBLIC = ROUTING / "examples" / "cord-receipts" / "cord-labels-grouped-measured.json"
PRIVE = MAISON / "cascade-portes" / "routing" / "cord-labels-grouped-measured.json"
RECORD = PUBLIC if PUBLIC.exists() else PRIVE
RENDU = MAISON / "cascade-portes" / "outils" / "rapport-routing.py"
DATA = ("The 100 real receipts of the CORD v2 test split (Clova AI, CC BY 4.0), with CORD's own labels; the split has been public "
        "since 2022, so the vendors' models may have seen it. Both vendor prices were declared by Crusetra for this sample.")
d = json.loads(RECORD.read_text()); a = d["audit"]
(BASE / "rapports").mkdir(exist_ok=True); tmp = BASE / "rapports" / "_page-routing.html"
# 04/10 (Arslane) : the sample is SIGNED. The page is rendered with the site's own fonts folder (../fontes, which
# exists under source/ and under docs/), signed with the private key through the house signer (never printed), re-read
# by cascade's public verifier, and only then rendered to PDF; the signed page ships beside the PDF.
subprocess.run([sys.executable, str(RENDU), str(RECORD), str(tmp), "--data", DATA, "--declared-by", "Crusetra, for this sample",
                "--fontes", "../fontes", "--client", f"Sample: {json.loads(RECORD.read_text())['source']['cases']} receipts of the CORD v2 test split"], check=True, capture_output=True)
SIGNE = BASE / "rapports" / "routing-sample-report.html"
subprocess.run(["node", str(MAISON / "cascade-portes" / "outils" / "signer-rapport.mjs"), str(tmp), str(SIGNE)], check=True)
VERIF = subprocess.run(["node", str(ROUTING / "src" / "verifier-rapport.mjs"), str(SIGNE)], capture_output=True, text=True)
if VERIF.returncode != 0 or "Signature valid" not in VERIF.stdout:
    sys.exit(f"the signed sample report does not verify:\n{VERIF.stdout}{VERIF.stderr}")
pdf, webp = BASE / "rapports" / "routing-sample-report.pdf", BASE / "rendus" / "rapport-routing.webp"
subprocess.run(["node", str(BASE / "capturer-rapport.mjs"), str(SIGNE), str(pdf), str(webp)], check=True)
tmp.unlink()
F = list(a["fields"]); pick = a["routing"]
side = {"sceau": d["empreinte"], "mesure": d["measuredAt"][:10], "commit": d["code"]["commit"], "cas": d["source"]["cases"], "signe": True, "verifie": VERIF.stdout.strip().splitlines()[0].strip(),
        "champs": F, "routage": pick, "sources": len(a["fields"][F[0]]["sources"]),
        "economie": a["cost"]["annual"]["saving"], "volume": a["cost"]["annual"]["pagesPerYear"],
        "juste": {f: round(a["fields"][f]["sources"][pick[f]]["accuracy"] * 100, 1) for f in F},
        "source": "cascade/examples/cord-receipts/cord-labels-grouped-measured.json",
        "lu_depuis": "public" if RECORD == PUBLIC else "copie privée identique, en attendant la fusion de la PR #10"}
(BASE / "rapports" / "routing-sample-report.json").write_text(json.dumps(side, indent=2, ensure_ascii=False) + "\n")
print("routing sample report:", pdf.stat().st_size // 1024, "KB pdf,", webp.stat().st_size // 1024, "KB page image, seal", side["sceau"],
      "| read from", side["lu_depuis"])
