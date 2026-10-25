# Witness of the hero-button guard (_garde_action in batir-hero.py, 25/10): green on the built pages, red on each
# weakened copy (a figure the page does not state, a target it does not carry, two buttons, none). Run after
# batir-hero.py: python3 temoin-bouton-hero.py
import ast, re, sys, html as html_mod, pathlib
S = pathlib.Path(__file__).resolve().parent
src = (S / "batir-hero.py").read_text()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_garde_action")
ns = {"re": re, "sys": sys, "html_mod": html_mod}; exec(ast.get_source_segment(src, fn), ns); g = ns["_garde_action"]
def essai(nom, page, attendu):
    try: g(page, nom); res = "vert"
    except SystemExit as e: res = "rouge: " + str(e)
    ok = res.startswith(attendu); print(("OK  " if ok else "FAUX"), nom, "->", res[:120]); return ok
sc = (S / "HERO-SCREENING.html").read_text(); rt = (S / "HERO.html").read_text(); mo = (S / "HERO-MONITORING.html").read_text()
r = [essai("screening intact", sc, "vert"), essai("routing intact", rt, "vert"), essai("monitoring intact", mo, "vert"),
     essai("screening 48 -> 24", sc.replace("within 48 hours <span class=\"fl\"", "within 24 hours <span class=\"fl\""), "rouge"),
     essai("screening #report -> #nowhere", sc.replace('<a class="cta" href="#report">', '<a class="cta" href="#nowhere">'), "rouge"),
     essai("routing href changed", rt.replace('<a class="cta" href="mailto:', '<a class="cta" href="mailto:x', 1), "rouge"),
     essai("monitoring two buttons", mo.replace('<a class="cta"', '<a class="cta" href="../ENGAGEMENT.html"><span class="b">See pricing <span class="fl">x</span></span></a><a class="cta"', 1), "rouge"),
     essai("monitoring no button", mo.replace('<a class="cta"', '<a class="xcta"'), "rouge")]
sys.exit(0 if all(r) else 1)
