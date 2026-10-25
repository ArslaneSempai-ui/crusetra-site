#!/usr/bin/env python3
"""Prepare the home's night sky (Arslane, 25/10, concept A "dive" of maquettes-accueil.py) into source/ciel/.

Usage: python3 preparer-ciel.py [HUB layer folder]
  default folder: equipe-cascade/tableau-de-bord/images/accueil/couches (the HUB's night set of 2026-10-18)

Run once when the HUB's pictures change; the site build (batir-hero.py, assembler.py) only reads source/ciel/ and
never the HUB. Every picture is a HUB render; nothing new is drawn here, only made lighter:
  - stills: lossy WebP (the HUB ships several lossless, the Earth alone 1.08 MB); alpha kept lossless so the limbs
    stay clean (measured 25/10: Earth 1,083,294 -> 82,990 bytes at q80, no visible change on black);
  - the awake robot: the HUB's awake night SCENE (nuit-eveil-fixe.webp) cut to the robot box with the night robot
    layer's alpha, as the mockup did (the HUB has no awake night layer);
  - loops: the HUB's VP9-with-alpha webm re-encoded at CRF 42 (station 381,077 -> 130,369 bytes, same look at 3x);
  - boites.json: the HUB's plate boxes, Uranus moved down and left as in the mockup (the headline column stays clear).
Every step asserts its output exists and is smaller than its source, or the script stops.
"""
import json, pathlib, shutil, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
HUB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ICI.parents[1] / "equipe-cascade/tableau-de-bord/images/accueil/couches"
OUT = ICI / "ciel"
if not HUB.is_dir():
    sys.exit(f"no HUB layer folder at {HUB}")
for outil in ("cwebp", "ffmpeg"):
    if not shutil.which(outil):
        sys.exit(f"{outil} is needed")
OUT.mkdir(exist_ok=True)

STILLS = ["ciel", "jupiter", "saturne", "neptune", "uranus", "mars", "lune", "station", "terre"]
LOOPS = ["jupiter", "saturne", "neptune", "uranus", "mars", "lune", "station"]

def run(*a):
    subprocess.run(a, check=True, capture_output=True)

def plus_leger(src, dst):
    if not dst.exists() or dst.stat().st_size == 0:
        sys.exit(f"{dst.name}: not written")
    if dst.stat().st_size >= src.stat().st_size:
        sys.exit(f"{dst.name}: {dst.stat().st_size} bytes, not lighter than {src.name} ({src.stat().st_size})")
    print(f"  {dst.name:28} {src.stat().st_size:>9,} -> {dst.stat().st_size:>8,} bytes")

base = HUB / "nuit-base-fixe.webp"
run("cwebp", "-quiet", "-q", "76", "-m", "6", str(base), "-o", str(OUT / base.name)); plus_leger(base, OUT / base.name)
for l in STILLS:
    src = HUB / f"nuit-{l}-fixe.webp"
    run("cwebp", "-quiet", "-q", "80", "-alpha_q", "100", "-m", "6", "-sharp_yuv", "-exact", str(src), "-o", str(OUT / src.name))
    if (OUT / src.name).stat().st_size >= src.stat().st_size:   # a tiny lossless still can beat lossy: keep the HUB's own
        shutil.copyfile(src, OUT / src.name); print(f"  {src.name:28} kept as shipped ({src.stat().st_size:,} bytes)")
    else:
        plus_leger(src, OUT / src.name)

box = json.loads((HUB / "boites.json").read_text())
note = box.pop("_note", "")
box["ciel"] = [0, 0, 2400, 1700]
box["uranus"] = [300, 1130, 204, 103]
rx, ry, rw, rh = box["robot"]
eveil = HUB.parent / "nuit-eveil-fixe.webp"
png = OUT / "robot-eveil.tmp.png"
run("ffmpeg", "-v", "error", "-y", "-i", str(eveil), "-i", str(HUB / "nuit-robot-fixe.webp"), "-filter_complex",
    f"[0]format=rgba,crop={rw}:{rh}:{rx}:{ry}:exact=1[c];[1]format=rgba,alphaextract[a];[c][a]alphamerge", str(png))
run("cwebp", "-quiet", "-q", "86", "-alpha_q", "100", "-m", "6", "-sharp_yuv", "-exact", str(png), "-o", str(OUT / "nuit-robot-eveil-fixe.webp"))
png.unlink()   # an intermediate this script wrote itself, in its own output folder
plus_leger(HUB / "nuit-robot-fixe.webp", OUT / "nuit-robot-eveil-fixe.webp")

for l in LOOPS:
    src, dst = HUB / f"nuit-{l}.webm", OUT / f"nuit-{l}.webm"
    run("ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-i", str(src), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        "-b:v", "0", "-crf", "42", "-deadline", "good", "-cpu-used", "2", "-row-mt", "1", "-an", str(dst))
    alpha = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream_tags=alpha_mode", "-of", "csv=p=0", str(dst)],
                           capture_output=True, text=True).stdout.strip()
    if alpha != "1":
        sys.exit(f"{dst.name}: the alpha channel was lost")
    plus_leger(src, dst)

(OUT / "boites.json").write_text(json.dumps({"_note": note + "; Uranus moved to [300,1130] for the home (25/10)", **box},
                                            separators=(",", ":")) + "\n")
total = sum(f.stat().st_size for f in OUT.iterdir() if f.suffix in (".webp", ".webm"))
print(f"source/ciel: {len(list(OUT.glob('*.web*')))} files, {total:,} bytes")
