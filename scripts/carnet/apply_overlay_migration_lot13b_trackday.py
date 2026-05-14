#!/usr/bin/env python3
"""
CARNET · Lot 13b-2 (Phase α refactor in-place) — Migration Track Day

Source        : Migration in-place du mode Track Day (Lot 6) vers le
                composant générique .carnet-overlay-* + CarnetOverlay.

Scope         : 5 patches sur index.html
                  - CSS-1 : suppression bloc overlay/close/header dupliqué
                            + transformation .trackday-header-right .is-positive
                              en .carnet-overlay-header-right .is-positive
                              (règle utile préservée et généralisée)
                  - CSS-2 : suppression bloc actions dupliqué
                  - JS-1  : classes header → .carnet-overlay-header-*
                  - JS-2  : classes actions → .carnet-overlay-action-*
                  - JS-3  : window.CARNET_TRACKDAY_DEMO → CarnetOverlay.create()

  Le contenu spécifique Track Day est conservé :
    .trackday-chronos, .trackday-chronos-*,
    .trackday-coaching, .trackday-coaching-*,
    .trackday-pilots, .trackday-pilots-*,
    .trackday-car, .trackday-car-*

  Particularité : .is-positive (chronos verts dans header-right) est
  promu au composant générique car potentiellement utile pour tout
  mode futur.

Note micro-uniformisation :
  Track Day avait padding:13px et icon font-size:16px sur les actions.
  Le générique uniformise à 14px / 18px (valeur Co-pilote). Pas grave.

Gain Track Day seul : ~123 lignes éliminées (~99 CSS + ~24 JS)

Prérequis : Lot 13 (Phase α refactor) appliqué
Usage     :
    python3 apply_overlay_migration_lot13b_trackday.py path/to/index.html
    python3 apply_overlay_migration_lot13b_trackday.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH CSS-1 — Suppression overlay/close/header + extraction .is-positive
# ═══════════════════════════════════════════════════════════════════════

CSS1_ANCHOR = """/* Mode overlay plein écran — pattern identique au Lot 5 */
.trackday-overlay{
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
.trackday-overlay[hidden]{ display:none; }

.trackday-close{
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
.trackday-close:hover{ background:rgba(244,241,234,0.3); }

/* Header — encre noir, eyebrow + titre + pit lane + live */
.trackday-header{
  padding:14px 18px;
  background:var(--encre);
  color:var(--papier);
  display:flex;
  justify-content:space-between;
  align-items:center;
  position:relative;
}
.trackday-header-left{ flex:1; }
.trackday-header-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0;
}
.trackday-header-title{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  margin:2px 0 0 0;
  line-height:1.1;
  color:var(--papier);
}
.trackday-header-right{
  text-align:right;
  font-family:var(--mono);
  font-size:11px;
  color:#D5D0C4;
  padding-right:40px;
}
.trackday-header-right .is-positive{ color:#9FE1CB; }
.trackday-header-live{
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
  margin-top:2px;
}

/* Chronos hero — 2 cols grid (meilleur tour + tour précédent) */"""

CSS1_REPLACEMENT = """/* Migré Lot 13b-2 — overlay/close/header utilisent .carnet-overlay-* générique */
/* Extension Lot 13b-2 : .is-positive promu au composant générique (utile pour tous modes) */
.carnet-overlay-header-right .is-positive{ color:#9FE1CB; }

/* Chronos hero — 2 cols grid (meilleur tour + tour précédent) */"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH CSS-2 — Suppression bloc actions Track Day
# ═══════════════════════════════════════════════════════════════════════

CSS2_ANCHOR = """/* Actions bottom — 3 boutons grid (pattern Lot 5) */
.trackday-actions{
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:1px;
  background:#D5D0C4;
  border-top:1px solid #D5D0C4;
}
.trackday-action{
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
.trackday-action.is-alert{ color:var(--orange-polo); }
.trackday-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

/* ═══ LOT 7 (Phase γ) — Gumball Convoy Mode C ══════════════════════════ */"""

CSS2_REPLACEMENT = """/* Migré Lot 13b-2 — actions utilisent .carnet-overlay-actions générique */

/* ═══ LOT 7 (Phase γ) — Gumball Convoy Mode C ══════════════════════════ */"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-1 — Classes header dans renderTrackdayOverlay
# Raw string pour ne pas interpréter \u00d7, \u00b7, \u25cf comme caractères Unicode
# ═══════════════════════════════════════════════════════════════════════

JS1_ANCHOR = r"""  return `
    <button type="button" class="trackday-close" data-action="closeTrackday" aria-label="Fermer">\u00d7</button>

    <div class="trackday-header">
      <div class="trackday-header-left">
        <p class="trackday-header-eyebrow">${esc(s.circuit || '')} \u00b7 ${esc(s.label || '')}</p>
        <p class="trackday-header-title">${esc(s.title || '')}</p>
      </div>
      <div class="trackday-header-right">
        <div>Pit lane <span class="is-positive">${s.pit_lane_count || 0}</span></div>
        ${s.live && s.on_track ? '<div class="trackday-header-live">\u25cf en piste</div>' : ''}
      </div>
    </div>"""

JS1_REPLACEMENT = r"""  return `
    <button type="button" class="carnet-overlay-close" data-action="closeOverlay" aria-label="Fermer">\u00d7</button>

    <div class="carnet-overlay-header">
      <div class="carnet-overlay-header-left">
        <p class="carnet-overlay-header-eyebrow">${esc(s.circuit || '')} \u00b7 ${esc(s.label || '')}</p>
        <p class="carnet-overlay-header-title">${esc(s.title || '')}</p>
      </div>
      <div class="carnet-overlay-header-right">
        <div>Pit lane <span class="is-positive">${s.pit_lane_count || 0}</span></div>
        ${s.live && s.on_track ? '<div class="carnet-overlay-header-live">\u25cf en piste</div>' : ''}
      </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-2 — Classes actions dans renderTrackdayOverlay
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = r"""    <div class="trackday-actions">
      <button type="button" class="trackday-action" data-action="trackdayPhotos">
        <span class="trackday-action-icon">\ud83d\udcf8</span>
        Photos
      </button>
      <button type="button" class="trackday-action" data-action="trackdayInstructor">
        <span class="trackday-action-icon">\u229c</span>
        Instructeur
      </button>
      <button type="button" class="trackday-action is-alert" data-action="trackdayPitOut">
        <span class="trackday-action-icon">\u26a0</span>
        Sortie pit
      </button>
    </div>"""

JS2_REPLACEMENT = r"""    <div class="carnet-overlay-actions">
      <button type="button" class="carnet-overlay-action" data-action="trackdayPhotos">
        <span class="carnet-overlay-action-icon">\ud83d\udcf8</span>
        Photos
      </button>
      <button type="button" class="carnet-overlay-action" data-action="trackdayInstructor">
        <span class="carnet-overlay-action-icon">\u229c</span>
        Instructeur
      </button>
      <button type="button" class="carnet-overlay-action is-alert" data-action="trackdayPitOut">
        <span class="carnet-overlay-action-icon">\u26a0</span>
        Sortie pit
      </button>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH JS-3 — window.CARNET_TRACKDAY_DEMO → CarnetOverlay.create()
# ═══════════════════════════════════════════════════════════════════════

JS3_ANCHOR = """// API démo accessible via console
window.CARNET_TRACKDAY_DEMO = {
  open: function(){
    let overlay = document.getElementById('carnet-trackday-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'carnet-trackday-overlay';
      overlay.className = 'trackday-overlay';
      document.body.appendChild(overlay);
      overlay.addEventListener('click', function(e){
        const btn = e.target.closest('[data-action="closeTrackday"]');
        if (btn) window.CARNET_TRACKDAY_DEMO.close();
      });
    }
    overlay.innerHTML = renderTrackdayOverlay();
    overlay.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  },
  close: function(){
    const overlay = document.getElementById('carnet-trackday-overlay');
    if (overlay) overlay.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
};
// ─── /Lot 6 helpers ──────────────────────────────────────────────────"""

JS3_REPLACEMENT = """// API démo accessible via console — Migré Lot 13b-2 vers CarnetOverlay factory
window.CARNET_TRACKDAY_DEMO = CarnetOverlay.create('carnet-trackday-overlay', renderTrackdayOverlay);
// ─── /Lot 6 helpers ──────────────────────────────────────────────────"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 13b-2 (Phase α refactor in-place) — Migration Track Day vers CarnetOverlay",
    requires=[
        "LOT 13 (Phase α refactor) — carnet-overlay générique",
        "Lot 13 (Phase α refactor) — CarnetOverlay factory",
    ],
    patches=[
        Patch(
            name="CSS-1 · suppression bloc overlay/close/header Track Day + extraction .is-positive",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Migré Lot 13b-2 — overlay/close/header utilisent .carnet-overlay-* générique",
        ),
        Patch(
            name="CSS-2 · suppression bloc actions Track Day",
            anchor=CSS2_ANCHOR,
            replacement=CSS2_REPLACEMENT,
            idempotence_marker="Migré Lot 13b-2 — actions utilisent .carnet-overlay-actions générique",
        ),
        Patch(
            name="JS-1 · classes header dans renderTrackdayOverlay",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker='class="carnet-overlay-header-eyebrow">${esc(s.circuit',
        ),
        Patch(
            name="JS-2 · classes actions dans renderTrackdayOverlay",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker='data-action="trackdayPhotos">\n        <span class="carnet-overlay-action-icon"',
        ),
        Patch(
            name="JS-3 · window.CARNET_TRACKDAY_DEMO → CarnetOverlay.create",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker="CarnetOverlay.create('carnet-trackday-overlay'",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
