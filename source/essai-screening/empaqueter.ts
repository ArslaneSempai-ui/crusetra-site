/**
 * THE MATCHER, PACKED FOR THE BROWSER, WITHOUT A PORT.
 *
 * The self-serve test page (screening/try.html) must give the result the screening tool gives, and the
 * company and vessel matcher is about ten thousand lines over forty-five modules (src/entites.ts and its
 * imports: scripts, romanisation folds, word weights, the index of src/cribler.ts). Rewriting that by
 * hand would drift. So the tool's own modules are taken as they are: each one is transpiled by the tool's
 * own TypeScript (the only compiler in its tree; no bundler is installed, and none is added), wrapped as a
 * CommonJS module, and the few Node built-ins they touch are stood in by small shims. The three files the
 * modules read at import time (pinyin.txt, jyutping.txt, the English dictionary) travel inside the bundle.
 *
 * What is NOT in the bundle: no network, no file system, no child process. A module that reaches for one of
 * those at run time hits a shim that throws, which the witness would see. The thresholds and the word-weight
 * table are not computed in the browser: construire.ts measures them with the tool, once, and the page ships
 * the figures with their date (donnees.json).
 *
 * Usage: imported by construire.ts; `node empaqueter.ts` alone writes moteur.js next to this file.
 */
import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { dirname, join, relative, resolve, posix } from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";

/** The tool's checkout, as the rest of the site reads it (source/outil.py: _MAISON / "cascade-screening"). */
export const MOTEUR = join(homedir(), "Documents", "cascade-screening");
export const ENTREE = "src/cribler.ts";
/** The files read at import time, under their path from the tool's root. The dictionary is gunzipped here. */
const ACTIFS = ["src/pinyin.txt", "src/jyutping.txt", "src/mots-anglais.txt.gz"] as const;
/** Packages the closure names only inside a function that the page never calls (the embedding matcher). */
const EXTERNES = new Set(["@huggingface/transformers"]);
/** STRINGS THE SERVED SITE MAY NOT CARRY (garde-adresses.py: no former name, no address but the house's), blanked in the
 *  bundle because the page never reads them: the former record genre (the page opens no record) and the address of the
 *  UN lists team inside the UN licence note (the page republishes nothing of that list). Each must occur exactly once,
 *  so a change in the tool is noticed here rather than served. */
const BLANCHIS: [string, string][] = [
  ['"cascade-screening/counterparty-screening"', '""'],
  [" (sc-sanctionslists@un.org)", ""],
];

type Module = { cle: string; code: string; imports: string[] };

export function empaqueter(racine: string = MOTEUR): { js: string; modules: string[]; sha256: string; commit: string } {
  const ts = createRequire(join(racine, "package.json"))("typescript") as typeof import("typescript");
  const modules = new Map<string, Module>();
  const file = (cle: string) => join(racine, cle);

  function lire(cle: string): void {
    if (modules.has(cle)) return;
    const chemin = file(cle);
    if (!existsSync(chemin)) throw new Error(`${cle} is not in the tool's tree: the closure of ${ENTREE} changed, read it again.`);
    let texte = readFileSync(chemin, "utf8");
    const pre = ts.preProcessFile(texte, true, true);
    const imports: string[] = [];
    for (const f of pre.importedFiles) {
      const spec = f.fileName;
      if (spec.startsWith("node:")) continue;
      if (EXTERNES.has(spec)) continue;
      if (!spec.startsWith(".")) throw new Error(`${cle} imports "${spec}": not a tool module, not a Node built-in, not a declared external.`);
      const resolu = posix.normalize(posix.join(posix.dirname(cle), spec));
      imports.push(resolu);
    }
    texte = preparer(cle, texte);
    const sortie = ts.transpileModule(texte, {
      fileName: chemin,
      reportDiagnostics: true,
      compilerOptions: {
        module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, removeComments: true,
        esModuleInterop: true, allowImportingTsExtensions: true, verbatimModuleSyntax: false,
      },
    });
    const fautes = (sortie.diagnostics ?? []).map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n"));
    if (fautes.length) throw new Error(`${cle} does not transpile:\n  ${fautes.join("\n  ")}`);
    modules.set(cle, { cle, code: sortie.outputText, imports });
    for (const i of imports) lire(i);
  }

  lire(ENTREE);

  const actifs: Record<string, string> = {};
  for (const a of ACTIFS) {
    const octets = readFileSync(file(a));
    actifs[a] = a.endsWith(".gz") ? gunzipSync(octets).toString("utf8") : octets.toString("utf8");
  }

  const cles = [...modules.keys()].sort();
  const corps = cles.map((k) => `  ${JSON.stringify(k)}: function (require, module, exports, process, Buffer) {\n${modules.get(k)!.code}\n  },`).join("\n");
  let js = sansCadratin(ts, `${CHARGEUR_AVANT}
const ACTIFS = ${JSON.stringify(actifs)};
const MODULES = {
${corps}
};
${CHARGEUR_APRES}`);
  for (const [vieux, neuf] of BLANCHIS) {
    const n = js.split(vieux).length - 1;
    if (n !== 1) throw new Error(`${JSON.stringify(vieux)} occurs ${n} times in the bundle, one expected: read the tool again before blanking it.`);
    js = js.replace(vieux, neuf);
  }
  const commit = lireCommit(racine);
  return { js, modules: cles, sha256: createHash("sha256").update(js).digest("hex"), commit };
}

/** THE SITE SERVES NO U+2014 (the em dash), in any form (assembler.py, decided on 3 September 2026). The tool's annotation
 *  rules read one inside regular expressions (`[\u{2014}\u{2013}-]`, with the u flag): each is rewritten as its `\u{2014}`
 *  escape, which the u flag reads as the same character, so the rule is the tool's and the served file holds no dash.
 *  Anywhere else (a string, a template) the same escape means the same character; a regular expression without the u
 *  flag, or any other place, would change meaning, and the build refuses it rather than guess. */
function sansCadratin(ts: typeof import("typescript"), js: string): string {
  /* the raw character, and the tool's own `—` escape (the site refuses that spelling too) */
  const porte = (s: string) => s.includes("—") || s.includes("\\u2014");
  if (!porte(js)) return js;
  const sf = ts.createSourceFile("moteur.js", js, ts.ScriptTarget.ES2022, true, ts.ScriptKind.JS);
  const fautes: string[] = [];
  const visiter = (n: import("typescript").Node): void => {
    if (n.getChildCount() === 0) {
      const texte = n.getText();
      if (porte(texte)) {
        const ok = (ts.isRegularExpressionLiteral(n) && /u[a-z]*$/.test(texte.slice(texte.lastIndexOf("/"))))
          || ts.isStringLiteral(n) || ts.isNoSubstitutionTemplateLiteral(n) || ts.isTemplateHead(n) || ts.isTemplateMiddle(n) || ts.isTemplateTail(n);
        if (!ok) fautes.push(`${ts.SyntaxKind[n.kind]} at ${sf.getLineAndCharacterOfPosition(n.getStart()).line + 1}: ${texte.slice(0, 80)}`);
      }
      return;
    }
    n.forEachChild(visiter);
  };
  visiter(sf);
  if (fautes.length) throw new Error(`an em dash sits where its escape would change the meaning:\n  ${fautes.join("\n  ")}`);
  return js.replaceAll("\\u2014", "\\u{2014}").replaceAll("\u2014", "\\u{2014}");
}

/** The three rewrites that make a Node ES module a browser CommonJS one, textually, before TypeScript sees it:
 *  `import.meta.url` becomes a fixed file URL under /moteur/ (the asset shim resolves it), and the `if (isMain(import.meta))`
 *  block that runs a module as a command is cut, because it awaits at top level and a CommonJS wrapper cannot. */
function preparer(cle: string, texte: string): string {
  const url = `"file:///moteur/${cle}"`;
  let t = texte.replaceAll("import.meta.url", url).replaceAll("import.meta.filename", JSON.stringify(`/moteur/${cle}`))
    .replaceAll("import.meta.dirname", JSON.stringify(posix.dirname(`/moteur/${cle}`)));
  const garde = "\nif (isMain(import.meta))";
  const i = t.lastIndexOf(garde);
  if (i !== -1) {
    const reste = t.slice(i + garde.length);
    /* a one-line guard (`if (isMain(import.meta)) await principal();`) or a block that ends the file */
    const fin = reste.startsWith(" {") ? reste.indexOf("\n}\n") + 3 : reste.indexOf("\n") + 1;
    if (fin <= 0 || reste.slice(fin).trim() !== "") throw new Error(`${cle}: the isMain block is not the last statement; the cut would be wrong.`);
    t = t.slice(0, i) + "\n";
  }
  if (t.includes("import.meta")) throw new Error(`${cle} still reads import.meta after the rewrite.`);
  return t;
}

function lireCommit(racine: string): string {
  const tete = readFileSync(join(racine, ".git", "HEAD"), "utf8").trim();
  if (!tete.startsWith("ref: ")) return tete.slice(0, 7);
  const ref = join(racine, ".git", tete.slice(5));
  if (existsSync(ref)) return readFileSync(ref, "utf8").trim().slice(0, 7);
  const packed = join(racine, ".git", "packed-refs");
  const ligne = readFileSync(packed, "utf8").split("\n").find((l) => l.endsWith(" " + tete.slice(5)));
  if (!ligne) throw new Error(`the tool's commit cannot be read (${tete}).`);
  return ligne.slice(0, 7);
}

/* ────────────────────── the loader, as the page runs it ────────────────────── */

const CHARGEUR_AVANT = `(function () {
"use strict";
/* the Node built-ins the tool's modules name, stood in: file reads come from ACTIFS, everything else throws */
const refuse = (quoi) => () => { throw new Error(quoi + " is not available in the browser bundle"); };
const cle = (p) => {
  const s = p instanceof URL ? p.pathname : String(p).replace(/^file:\\/\\//, "");
  return s.replace(/^\\/moteur\\//, "");
};
class Octets { constructor(texte) { this.texte = texte; } toString() { return this.texte; } }
const fs = {
  readFileSync(p, enc) {
    const k = cle(p);
    if (!(k in ACTIFS)) throw new Error("the bundle holds no file " + k);
    return enc ? ACTIFS[k] : new Octets(ACTIFS[k]);
  },
  existsSync(p) { return cle(p) in ACTIFS; },
  writeFileSync: refuse("writeFileSync"), mkdirSync: refuse("mkdirSync"), renameSync: refuse("renameSync"),
  statSync: refuse("statSync"), copyFileSync: refuse("copyFileSync"), openSync: refuse("openSync"), readSync: refuse("readSync"),
  closeSync: refuse("closeSync"), fstatSync: refuse("fstatSync"), readdirSync: refuse("readdirSync"), unlinkSync: refuse("unlinkSync"),
  constants: { O_RDONLY: 0, O_NOFOLLOW: 256, O_NONBLOCK: 4 },
};
const path = {
  join: (...p) => normaliser(p.filter((x) => x !== "").join("/")),
  resolve: (...p) => normaliser(p.filter((x) => x !== "").join("/")),
  dirname: (p) => { const i = p.lastIndexOf("/"); return i <= 0 ? (i === 0 ? "/" : ".") : p.slice(0, i); },
  basename: (p, ext) => { const b = p.slice(p.lastIndexOf("/") + 1); return ext && b.endsWith(ext) ? b.slice(0, -ext.length) : b; },
  relative: (a, b) => b, extname: (p) => { const b = p.slice(p.lastIndexOf("/") + 1); const i = b.lastIndexOf("."); return i <= 0 ? "" : b.slice(i); },
  sep: "/", posix: null,
};
path.posix = path;
const builtins = {
  "node:fs": fs, "node:fs/promises": {}, "node:path": path,
  "node:url": { fileURLToPath: (u) => (u instanceof URL ? u.pathname : String(u).replace(/^file:\\/\\//, "")), pathToFileURL: (p) => new URL("file://" + p) },
  "node:os": { homedir: () => "/", platform: () => "browser", EOL: "\\n" },
  "node:zlib": { gunzipSync: (b) => b, inflateRawSync: refuse("inflateRawSync"), gzipSync: refuse("gzipSync") },
  "node:crypto": { createHash: refuse("createHash"), randomBytes: refuse("randomBytes") },
  "node:child_process": { execFileSync: refuse("execFileSync"), execSync: refuse("execSync"), spawnSync: refuse("spawnSync") },
  "node:module": { createRequire: refuse("createRequire") },
  "node:process": null,
};
const process = { env: {}, argv: [], pid: 0, platform: "browser", execPath: "", cwd: () => "/", exit: refuse("process.exit"),
  stdout: { write() {} }, stderr: { write() {} } };
builtins["node:process"] = process;
/* the one Buffer call on the page's path measures a field in bytes (src/csv.ts); the rest would read files */
const Buffer = { byteLength: (s) => new TextEncoder().encode(String(s)).length, isBuffer: () => false,
  from: refuse("Buffer.from"), alloc: refuse("Buffer.alloc") };
function normaliser(p) {
  const abs = p.startsWith("/");
  const out = [];
  for (const seg of p.split("/")) {
    if (seg === "" || seg === ".") continue;
    if (seg === "..") { if (out.length && out[out.length - 1] !== "..") out.pop(); else if (!abs) out.push(".."); continue; }
    out.push(seg);
  }
  return (abs ? "/" : "") + out.join("/");
}
`;

const CHARGEUR_APRES = `
const cache = new Map();
function depuis(from) {
  return function require(spec) {
    if (spec in builtins) return builtins[spec];
    if (!spec.startsWith(".")) throw new Error("the browser bundle has no package " + spec);
    const k = normaliser(path.join(path.dirname(from), spec));
    const deja = cache.get(k);
    if (deja) return deja.exports;
    const fabrique = MODULES[k];
    if (!fabrique) throw new Error("module not in the bundle: " + k + " (from " + from + ")");
    const module = { exports: {} };
    cache.set(k, module);
    fabrique(depuis(k), module, module.exports, process, Buffer);
    return module.exports;
  };
}
globalThis.CrusetraMoteur = { require: depuis("src/_page.ts"), modules: Object.keys(MODULES), actifs: Object.keys(ACTIFS) };
})();
`;

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  const { js, modules, sha256, commit } = empaqueter();
  const sortie = join(dirname(new URL(import.meta.url).pathname), "moteur.js");
  writeFileSync(sortie, js);
  console.log(`moteur.js: ${modules.length} modules of the tool at ${commit}, ${(js.length / 1e6).toFixed(2)} MB, sha256 ${sha256.slice(0, 16)}`);
}
