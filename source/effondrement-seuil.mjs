// The floor of the collapse probe (temoin-effondrement.mjs), kept pure so it can be tested without a browser.
// Default floor: 45 % of the screen (and 150 px). Decision of 20 October 2026: the text measure of two
// selectors is held at 70ch for reading comfort, which at 1280 px is narrower than 45 % of the screen;
// for those two selectors only, the floor is the measured width of 70ch in that element's own font.
// Every other selector keeps the 45 % floor. Widening this list weakens the probe: the test refuses it.
export const SELECTEURS_CH = ['.c-liste li', '.ex-q'];
export const CH_MESURE = 70;

// matches(selector) -> boolean (the element matches that selector); mesurerCh() -> px width of 70ch
// in the element's font (measured in the page, never typed). Rounding slack: one pixel. The exception only
// relaxes the rule: on a phone, where 45 % of the screen is narrower than 70ch, the 45 % floor still applies.
export function plancher({W, matches, mesurerCh, selecteurs = SELECTEURS_CH}) {
  const defaut = Math.max(150, 0.45 * W);
  if (selecteurs.some(s => matches(s))) return Math.min(defaut, Math.max(0, mesurerCh() - 1));
  return defaut;
}
