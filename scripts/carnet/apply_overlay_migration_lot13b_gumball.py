#!/usr/bin/env python3
"""
CARNET · Lot 13b-3 (Phase α refactor in-place) — Migration Gumball Convoy

Source        : Migration in-place du mode Gumball Convoy (Lot 7) vers le
                composant générique .carnet-overlay-* + CarnetOverlay.

Scope         : 5 patches sur index.html
                  - CSS-1 : suppression bloc overlay/close/header dupliqué
                  - CSS-2 : suppression bloc actions dupliqué
                  - JS-1  : classes header → .carnet-overlay-header-*
                  - JS-2  : classes actions → .carnet-overlay-action-*
                  - JS-3  : window.CARNET_GUMBALL_DEMO → CarnetOverlay.create()

  Le contenu spécifique Gumball est conservé :
    .gumball-program, .gumball-timeline, .gumball-step*
    .gumball-reel, .gumball-reel-*, .gumball-story*

Note micro-uniformisation :
  Gumball avait padding:13px et icon font-size:16px sur les actions, plus
  margin-top:14px sur le grid. Le générique uniformise à 14px / 18px sans
  margin-top. Petit gain visuel d'uniformité avec les autres modes.

Aucun bouton `.is-alert` dans Gumball (pas de variant alert utilisé).

Gain Gumball seul : ~120 lignes éliminées (~96 CSS + ~24 JS)
Gain cumulé Lot 13b complet : ~366 lignes éliminées (Co-pilote + Track Day + Gumball)

Prérequis : Lot 13 (Phase α refactor) appliqué
Usage     :
    python3 apply_overlay_migration_lot13b_gumball.py path/to/index.html
    python3 apply_overlay_migration_lot13b_gumball.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH CSS-1 — Suppression bloc overlay/close/header Gumball
# ═══════════════════════════════════════════════════════════════════════

CSS1_ANCHOR = """/* Mode overlay plein écran — pattern identique Lot 5/6 */
.gumball-overlay{
  position:fixed;
  inset:0;
  background:var(--papier);
  color:var(--encre);
  z-index:9999;
  overflow-y:auto;
  overflow-x:hidden;
  font-family:var(--sans);
  -webkit-overflow-scrolling:touch;
}
.gumball-overlay[hidden]{ display:none; }

.gumball-close{
  position:absolute;
  top:14px;
  right:14px;
  width:32px;
  height:32px;
  border-radius:50%;
  background:rgba(244,241,234,0.15);
  color:var(--papier);
  border:none;
  font-family:var(--mono);
  font-size:16px;
  line-height:1;
  cursor:pointer;
  z-index:2;
  display:flex;
  align-items:center;
  justify-content:center;
}
.gumball-close:hover{ background:rgba(244,241,234,0.3); }

/* Header — encre noir avec convoy counter */
.gumball-header{
  padding:14px 18px;
  background:var(--encre);
  color:var(--papier);
  display:flex;
  justify-content:space-between;
  align-items:center;
  position:relative;
}
.gumball-header-left{ flex:1; }
.gumball-header-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0;
}
.gumball-header-title{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  margin:2px 0 0 0;
  line-height:1.1;
  color:var(--papier);
}
.gumball-header-right{
  text-align:right;
  font-family:var(--mono);
  font-size:11px;
  color:#D5D0C4;
  padding-right:40px;
}
.gumball-header-live{
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
  margin-top:2px;
}"""

CSS1_REPLACEMENT = """/* Migré Lot 13b-3 — overlay/close/header utilisent .carnet-overlay-* générique */"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH CSS-2 — Suppression bloc actions Gumball
# ═══════════════════════════════════════════════════════════════════════

CSS2_ANCHOR = """/* Actions bottom — 3 boutons grid (pattern Lot 5/6) */
.gumball-actions{
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:1px;
  background:#D5D0C4;
  border-top:1px solid #D5D0C4;
  margin-top:14px;
}
.gumball-action{
  padding:13px 0;
  background:var(--papier);
  border:none;
  cursor:pointer;
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--encre);
}
.gumball-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

/* ═══ LOT 8 (Phase α) — Garage Dashboard Complet ═══════════════════════ */"""

CSS2_REPLACEMENT = """/* Migré Lot 13b-3 — actions utilisent .carnet-overlay-actions générique */

/* ═══ LOT 8 (Phase α) — Garage Dashboard Complet ═══════════════════════ */"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-1 — Classes header dans renderGumballOverlay
# Raw string pour ne pas interpréter \u00d7, \u00b7, \u25cf comme caractères Unicode
# ═══════════════════════════════════════════════════════════════════════

JS1_ANCHOR = r"""  return `
    <button type="button" class="gumball-close" data-action="closeGumball" aria-label="Fermer">\u00d7</button>

    <div class="gumball-header">
      <div class="gumball-header-left">
        <p class="gumball-header-eyebrow">${esc(ev.series || '')} \u00b7 ${esc(ev.day || '')}</p>
        <p class="gumball-header-title">${esc(ev.leg || '')}</p>
      </div>
      <div class="gumball-header-right">
        <div>${esc(ev.convoy_position || '')}</div>
        ${ev.convoy_live ? '<div class="gumball-header-live">\u25cf convoy live</div>' : ''}
      </div>
    </div>"""

JS1_REPLACEMENT = r"""  return `
    <button type="button" class="carnet-overlay-close" data-action="closeOverlay" aria-label="Fermer">\u00d7</button>

    <div class="carnet-overlay-header">
      <div class="carnet-overlay-header-left">
        <p class="carnet-overlay-header-eyebrow">${esc(ev.series || '')} \u00b7 ${esc(ev.day || '')}</p>
        <p class="carnet-overlay-header-title">${esc(ev.leg || '')}</p>
      </div>
      <div class="carnet-overlay-header-right">
        <div>${esc(ev.convoy_position || '')}</div>
        ${ev.convoy_live ? '<div class="carnet-overlay-header-live">\u25cf convoy live</div>' : ''}
      </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-2 — Classes actions dans renderGumballOverlay
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = r"""    <div class="gumball-actions">
      <button type="button" class="gumball-action" data-action="gumballStory">
        <span class="gumball-action-icon">\u25b6</span>
        Story
      </button>
      <button type="button" class="gumball-action" data-action="gumballConvoy">
        <span class="gumball-action-icon">\u2302</span>
        Convoy
      </button>
      <button type="button" class="gumball-action" data-action="gumballPot">
        <span class="gumball-action-icon">\u20ac</span>
        Pot
      </button>
    </div>"""

JS2_REPLACEMENT = r"""    <div class="carnet-overlay-actions">
      <button type="button" class="carnet-overlay-action" data-action="gumballStory">
        <span class="carnet-overlay-action-icon">\u25b6</span>
        Story
      </button>
      <button type="button" class="carnet-overlay-action" data-action="gumballConvoy">
        <span class="carnet-overlay-action-icon">\u2302</span>
        Convoy
      </button>
      <button type="button" class="carnet-overlay-action" data-action="gumballPot">
        <span class="carnet-overlay-action-icon">\u20ac</span>
        Pot
      </button>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-3 — window.CARNET_GUMBALL_DEMO → CarnetOverlay.create()
# ═══════════════════════════════════════════════════════════════════════

JS3_ANCHOR = """// API démo accessible via console
window.CARNET_GUMBALL_DEMO = {
  open: function(){
    let overlay = document.getElementById('carnet-gumball-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'carnet-gumball-overlay';
      overlay.className = 'gumball-overlay';
      document.body.appendChild(overlay);
      overlay.addEventListener('click', function(e){
        const btn = e.target.closest('[data-action="closeGumball"]');
        if (btn) window.CARNET_GUMBALL_DEMO.close();
      });
    }
    overlay.innerHTML = renderGumballOverlay();
    overlay.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  },
  close: function(){
    const overlay = document.getElementById('carnet-gumball-overlay');
    if (overlay) overlay.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
};
// ─── /Lot 7 helpers ──────────────────────────────────────────────────"""

JS3_REPLACEMENT = """// API démo accessible via console — Migré Lot 13b-3 vers CarnetOverlay factory
window.CARNET_GUMBALL_DEMO = CarnetOverlay.create('carnet-gumball-overlay', renderGumballOverlay);
// ─── /Lot 7 helpers ──────────────────────────────────────────────────"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 13b-3 (Phase α refactor in-place) — Migration Gumball vers CarnetOverlay",
    requires=[
        "LOT 13 (Phase α refactor) — carnet-overlay générique",
        "Lot 13 (Phase α refactor) — CarnetOverlay factory",
    ],
    patches=[
        Patch(
            name="CSS-1 · suppression bloc overlay/close/header Gumball",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Migré Lot 13b-3 — overlay/close/header utilisent .carnet-overlay-* générique",
        ),
        Patch(
            name="CSS-2 · suppression bloc actions Gumball",
            anchor=CSS2_ANCHOR,
            replacement=CSS2_REPLACEMENT,
            idempotence_marker="Migré Lot 13b-3 — actions utilisent .carnet-overlay-actions générique",
        ),
        Patch(
            name="JS-1 · classes header dans renderGumballOverlay",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker='class="carnet-overlay-header-title">${esc(ev.leg',
        ),
        Patch(
            name="JS-2 · classes actions dans renderGumballOverlay",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker='data-action="gumballStory">\n        <span class="carnet-overlay-action-icon"',
        ),
        Patch(
            name="JS-3 · window.CARNET_GUMBALL_DEMO → CarnetOverlay.create",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker="CarnetOverlay.create('carnet-gumball-overlay'",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
