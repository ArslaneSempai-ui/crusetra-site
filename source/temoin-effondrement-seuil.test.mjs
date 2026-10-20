// Witness of the collapse probe's floor choice (no browser): the two 70ch selectors get the measured-ch
// floor, every other selector keeps 45 % of the screen. usage: node --test temoin-effondrement-seuil.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ici = dirname(fileURLToPath(import.meta.url));
const CHEMIN = join(ici, 'effondrement-seuil.mjs');

// the checks, run against a module path so the same checks can be pointed at a widened copy
export async function verifier(chemin) {
  const m = await import(pathToFileURL(chemin).href + '?v=' + Math.random());
  const erreurs = [];
  const ok = (cond, msg) => { if (!cond) erreurs.push(msg); };
  const cible = sel => s => s === sel;
  const ch = () => 547.4; // a measured 70ch, as the page would return it
  ok(JSON.stringify(m.SELECTEURS_CH) === JSON.stringify(['.c-liste li', '.ex-q']), 'the ch selector list is exactly the two decided selectors');
  for (const sel of ['.c-liste li', '.ex-q']) {
    const f = m.plancher({W: 1280, matches: cible(sel), mesurerCh: ch});
    ok(Math.abs(f - 546.4) < 0.01, `${sel} floor is the measured 70ch (got ${f})`);
    const large = m.plancher({W: 1920, matches: cible(sel), mesurerCh: ch});
    ok(Math.abs(large - 546.4) < 0.01, `${sel} floor stays the measured 70ch on a wide screen (got ${large})`);
    ok(m.plancher({W: 375, matches: cible(sel), mesurerCh: ch}) === 168.75, `${sel} never gets a floor above the 45 % one (phone)`);
  }
  for (const sel of ['p', 'main li', '.fiche', 'h2', '.c-qui', '.ex-fin']) {
    ok(m.plancher({W: 1280, matches: cible(sel), mesurerCh: ch}) === 576, `${sel} keeps the 45 % floor at 1280`);
    ok(m.plancher({W: 375, matches: cible(sel), mesurerCh: ch}) === 168.75, `${sel} keeps the 45 % floor at 375`);
    ok(m.plancher({W: 200, matches: cible(sel), mesurerCh: ch}) === 150, `${sel} keeps the 150 px floor`);
  }
  // the measured width is only called for the two selectors
  let appels = 0;
  m.plancher({W: 1280, matches: cible('p'), mesurerCh: () => { appels++; return 1; }});
  ok(appels === 0, 'the ch measure is not taken for other selectors');
  return erreurs;
}

test('floor: two selectors get the ch floor, any other keeps 45 %', async () => {
  const erreurs = await verifier(CHEMIN);
  assert.deepEqual(erreurs, []);
});

test('witness bites: a copy with the selector list widened to p is refused', async () => {
  const src = readFileSync(CHEMIN, 'utf8');
  const large = src.replace("['.c-liste li', '.ex-q']", "['.c-liste li', '.ex-q', 'p']");
  assert.notEqual(large, src, 'the widening edit must change the copy');
  const dir = mkdtempSync(join(tmpdir(), 'seuil-'));
  const copie = join(dir, 'effondrement-seuil.mjs');
  writeFileSync(copie, large);
  const erreurs = await verifier(copie);
  assert.ok(erreurs.length > 0, 'a widened list must be flagged');
});

test('witness bites: a copy where every selector gets the ch floor is refused', async () => {
  const src = readFileSync(CHEMIN, 'utf8');
  const tout = src.replace('if (selecteurs.some(s => matches(s)))', 'if (true)');
  assert.notEqual(tout, src);
  const dir = mkdtempSync(join(tmpdir(), 'seuil-'));
  const copie = join(dir, 'effondrement-seuil.mjs');
  writeFileSync(copie, tout);
  assert.ok((await verifier(copie)).length > 0);
});
