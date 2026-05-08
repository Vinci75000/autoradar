#!/usr/bin/env python3
"""
Apply Sprint B.3 step 4 — chip Cote Carnet patches to index.html.

Idempotent: refuses to run if patches already applied.
Verifies each anchor matches exactly once before replacing.

4 patches (split function/IIFE pour cross-script scope):
  1. CSS classes .ar-chip.cote-{under,at,over,insuff} (charte v8)
  2. Script 1: var _coteSegments + function coteChip(car) — avant renderCard
  3. Script 2: IIFE fetch cote_segments — apres const _sb
  4. renderCard: insert ${coteChip(car)} dans .ar-badges

Note: var (pas const) pour _coteSegments → window-attached, accessible
depuis le script 2 qui populate la Map via le fetch IIFE.
"""
import sys
from pathlib import Path

p = Path("index.html")
if not p.exists():
    sys.exit("ERROR: index.html introuvable. Lance ce script depuis ~/Code/autoradar/frontend/")

content = p.read_text()

# Idempotence guard
if 'var _coteSegments' in content:
    sys.exit(
        "ERROR: 'var _coteSegments' déjà présent dans index.html.\n"
        "       Si tu veux relancer le script, fais d'abord :\n"
        "       git reset --hard HEAD~1 && git push --force-with-lease"
    )


def apply_patch(name, content, anchor, replacement, mode="prepend"):
    """mode: 'prepend' (insert before anchor) or 'replace' (replace anchor)."""
    n = content.count(anchor)
    if n != 1:
        sys.exit(f"ERROR Patch {name}: ancre trouvée {n} fois (attendu 1). Abort.")
    if mode == "prepend":
        return content.replace(anchor, replacement + anchor)
    elif mode == "replace":
        return content.replace(anchor, replacement)
    else:
        sys.exit(f"Bad mode: {mode}")


# ============================================================
# Patch 1 — CSS chip Cote (4 classes charte v8)
# ============================================================
ANCHOR1 = '.ar-src{font-size:10px;color:var(--text3);background:var(--bg2);padding:2px 7px;border-radius:var(--rsm);border:1px solid var(--border)}'

CSS_COTE = '''.ar-chip.cote-under{background:#E85A1F;color:#F4F1EA}
.ar-chip.cote-at{background:#1F4D2F;color:#F4F1EA}
.ar-chip.cote-over{background:#0A0A0A;color:#F4F1EA}
.ar-chip.cote-insuff{background:transparent;color:#0A0A0A66;border:0.5px dashed #0A0A0A33;padding:1px 6px}
'''

content = apply_patch("1 (CSS)", content, ANCHOR1, CSS_COTE, mode="prepend")
print("✓ Patch 1 — CSS .ar-chip.cote-* injecté (charte v8)")


# ============================================================
# Patch 2 — Script 1: var _coteSegments + function coteChip
# Inséré AVANT function renderCard pour scope partagé avec elle.
# 'var' (pas const) pour devenir window._coteSegments, accessible
# depuis l'IIFE fetch dans le script 2.
# ============================================================
ANCHOR2 = 'function renderCard(car) {'

JS_COTE_FN = '''/* ═══════════════════════════════════════════════
   COTE CARNET — cache + classification (Sprint B.3)
   var (pas const) → window._coteSegments cross-script.
   Le fetch IIFE est dans le 2e <script>, apres const _sb.
═══════════════════════════════════════════════ */
var _coteSegments = new Map();

function coteChip(car) {
  const seg = _coteSegments.get(`${car.mk}|${car.mo}`);
  if (!seg) return '<span class="ar-chip cote-insuff">Donnée insuffisante</span>';
  const off = Math.round((car.px - seg.median_px) / seg.median_px * 100);
  if (car.px < seg.p25) return `<span class="ar-chip cote-under">Sous-côté −${Math.abs(off)}%</span>`;
  if (car.px > seg.p75) return `<span class="ar-chip cote-over">Surcôté +${off}%</span>`;
  return '<span class="ar-chip cote-at">Au prix</span>';
}

'''

content = apply_patch("2 (Script 1: fn coteChip)", content, ANCHOR2, JS_COTE_FN, mode="prepend")
print("✓ Patch 2 — var _coteSegments + function coteChip injectés (script 1, avant renderCard)")


# ============================================================
# Patch 3 — Script 2: IIFE fetch cote_segments
# Apres const _sb (sinon ReferenceError TDZ).
# Populate la Map globale _coteSegments definie dans le script 1.
# ============================================================
ANCHOR3 = '/* ── Cars: load from DB if available ── */'

JS_COTE_IIFE = '''/* ── Cote Carnet: fetch segments depuis Supabase ── */
(async () => {
  if (!_sb) return;
  const { data } = await _sb.from('cote_segments')
    .select('mk,mo,median_px,p25,p75').gte('n', 5);
  if (data) data.forEach(s => _coteSegments.set(`${s.mk}|${s.mo}`, s));
  if (typeof render === 'function') render();
  console.log(`[AutoRadar Cote] ${_coteSegments.size} segments chargés`);
})();

'''

content = apply_patch("3 (Script 2: IIFE fetch)", content, ANCHOR3, JS_COTE_IIFE, mode="prepend")
print("✓ Patch 3 — IIFE fetch cote_segments injectée (script 2, apres const _sb)")


# ============================================================
# Patch 4 — Insert ${coteChip(car)} dans renderCard .ar-badges
# ============================================================
OLD4 = '''${car.ch.map(c => `<span class="ar-chip ${c.t}">${c.l}</span>`).join('')}
              <span class="ar-src">'''

NEW4 = '''${car.ch.map(c => `<span class="ar-chip ${c.t}">${c.l}</span>`).join('')}
              ${coteChip(car)}
              <span class="ar-src">'''

content = apply_patch("4 (renderCard chip)", content, OLD4, NEW4, mode="replace")
print("✓ Patch 4 — ${coteChip(car)} inséré dans renderCard")


# Write
p.write_text(content)
print()
print("✅ Tous les patches Cote appliqués proprement à index.html")
