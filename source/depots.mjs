// The tool repositories the site reads, from depots.json and the optional depots.local.json
// (see depots.py, which does the same in Python). The checkout's HEAD must equal its configured
// ref or this refuses by name; refs are only read, never fetched.
import { readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";
import { isAbsolute, join } from "node:path";

const ICI = fileURLToPath(new URL(".", import.meta.url));

function git(depot, ...args) {
  try {
    return execFileSync("git", ["-C", depot, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    return null;
  }
}

export function depot(outil) {
  const cfg = JSON.parse(readFileSync(join(ICI, "depots.json"), "utf8"));
  const local = process.env.DEPOTS_LOCAL || join(ICI, "depots.local.json");
  const surcharge = existsSync(local) ? JSON.parse(readFileSync(local, "utf8")) : {};
  const v = { ...cfg[outil], ...(surcharge[outil] || {}) };
  if (!cfg[outil]) throw new Error(`depots: unknown tool ${outil}`);
  const chemin = isAbsolute(v.chemin) ? v.chemin : join(homedir(), v.chemin);
  const tete = git(chemin, "rev-parse", "HEAD");
  if (tete === null) throw new Error(`${outil} at ${chemin} is not a git checkout: point depots.local.json at a checkout of ${v.ref}`);
  const branche = git(chemin, "rev-parse", "--abbrev-ref", "HEAD");
  const cible = git(chemin, "rev-parse", "--verify", "--quiet", `${v.ref}^{commit}`);
  if (cible === null) throw new Error(`${outil} at ${chemin} has no ref ${v.ref}: point depots.local.json at a checkout of ${v.ref}`);
  if (tete !== cible) {
    const quoi = !branche || branche === "HEAD" ? tete.slice(0, 9) : branche;
    throw new Error(`${outil} at ${chemin} is on ${quoi}, not ${v.ref}: point depots.local.json at a checkout of ${v.ref}`);
  }
  return chemin;
}
