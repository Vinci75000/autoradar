#!/usr/bin/env python3
"""
CARNET · Lot 13 (Phase α refactor) — Composant carnet-overlay générique

Source        : Refactor add-only : extraction du pattern commun aux modes
                plein écran (Lot 5 Co-pilote, Lot 6 Track Day, Lot 7 Gumball)
                en un composant réutilisable .carnet-overlay-* + factory
                window.CarnetOverlay.

Scope         : Pattern propre disponible pour les Lots 14+ qui voudront
                créer un nouveau mode plein écran. Les 3 modes existants
                (Lot 5/6/7) ne sont PAS migrés in-place (laissés stables).

  CSS générique ajouté :
    .carnet-overlay              wrapper plein écran
    .carnet-overlay-close        bouton × top-right
    .carnet-overlay-header       header encre noir
    .carnet-overlay-header-left, -eyebrow, -title, -right, -live
    .carnet-overlay-actions      grid 3 boutons bottom (sticky)
    .carnet-overlay-action       bouton individuel
    .carnet-overlay-action.is-alert  variante orange (action critique)
    .carnet-overlay-action-icon  icône top du bouton

  JS factory ajouté :
    window.CarnetOverlay.create(id, renderFn)
      → retourne { open, close } prêts à l'emploi.

  Usage pour un futur mode plein écran (Lot 14+) :
    window.CARNET_FOO_DEMO = CarnetOverlay.create(
      'carnet-foo-overlay',
      function() { return '<header class=carnet-overlay-header>...</header>...'; }
    );

  Convention close button :
    Tout élément avec data-action="closeOverlay" déclenche la fermeture.
    Inutile de coder un handler dans chaque renderFn.

Hors scope (volontaire) :
  - Migration Lot 5/6/7 vers .carnet-overlay-* (= "Lot 13b" futur si demandé)
  - Animations open/close (Phase ε si jugé utile)
  - Mode swipe-to-close mobile (Phase ε)

Honnêteté sur le gain :
  Ce lot AJOUTE le pattern propre (~120 lignes nettes). Il n'élimine
  pas la duplication CSS existante des Lots 5/6/7. Le gain se matérialise
  quand les Lots 14+ utiliseront ce composant au lieu de redupliquer.

Prérequis : Lot 12 (Phase α) appliqué (donc Lots 5/6/7/8 aussi via prérequis chain)
Usage     :
    python3 apply_overlay_refactor_lot13.py path/to/index.html
    python3 apply_overlay_refactor_lot13.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS générique .carnet-overlay-*
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : fin du CSS Lot 8 (garage-tribu-rsvp-btn.is-secondary)
# suivi de </style>. L'insertion casse cette adjacence post-patch.

CSS_ANCHOR = """.garage-tribu-rsvp-btn.is-secondary{
  color:var(--encre);
  border:1px solid var(--gris-line);
}

</style>"""

CSS_REPLACEMENT = """.garage-tribu-rsvp-btn.is-secondary{
  color:var(--encre);
  border:1px solid var(--gris-line);
}

/* ═══════════════════════════════════════════════════════════════════════
   LOT 13 (Phase α refactor) — carnet-overlay générique
   Composant réutilisable pour les futurs modes plein écran (Lot 14+).
   Les Lots 5/6/7 conservent leurs namespaces dédiés (.copilote-* /
   .trackday-* / .gumball-*) — migration in-place possible dans un
   Lot 13b dédié si nécessaire.
   ═══════════════════════════════════════════════════════════════════════ */

/* Wrapper plein écran */
.carnet-overlay {
  position: fixed;
  inset: 0;
  background: var(--papier);
  color: var(--encre);
  z-index: 9999;
  overflow-y: auto;
  overflow-x: hidden;
  font-family: var(--sans);
  -webkit-overflow-scrolling: touch;
}
.carnet-overlay[hidden] { display: none; }

/* Bouton × top-right (par-dessus le header noir au scroll top) */
.carnet-overlay-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(244, 241, 234, 0.15);
  color: var(--papier);
  border: none;
  font-family: var(--mono);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carnet-overlay-close:hover { background: rgba(244, 241, 234, 0.3); }

/* Header noir éditorial */
.carnet-overlay-header {
  padding: 14px 18px;
  background: var(--encre);
  color: var(--papier);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}
.carnet-overlay-header-left { flex: 1; }
.carnet-overlay-header-eyebrow {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: #9FE1CB;
  text-transform: uppercase;
  margin: 0;
}
.carnet-overlay-header-title {
  font-family: var(--display);
  font-style: italic;
  font-size: 16px;
  margin: 2px 0 0 0;
  line-height: 1.1;
  color: var(--papier);
}
.carnet-overlay-header-right {
  text-align: right;
  font-family: var(--mono);
  font-size: 11px;
  color: #D5D0C4;
  padding-right: 40px;
}
.carnet-overlay-header-live {
  font-size: 9px;
  color: #9FE1CB;
  letter-spacing: 0.04em;
  margin-top: 2px;
}

/* Bottom actions sticky (grid 3 boutons par défaut) */
.carnet-overlay-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1px;
  background: #D5D0C4;
  border-top: 1px solid #D5D0C4;
  position: sticky;
  bottom: 0;
}
.carnet-overlay-actions.is-two-col { grid-template-columns: 1fr 1fr; }
.carnet-overlay-actions.is-four-col { grid-template-columns: 1fr 1fr 1fr 1fr; }

.carnet-overlay-action {
  padding: 14px 0;
  background: var(--papier);
  border: none;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--encre);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}
.carnet-overlay-action:hover { background: #FAFAF7; }
.carnet-overlay-action.is-alert { color: var(--orange-polo); }
.carnet-overlay-action.is-primary { color: var(--vert-anglais); }
.carnet-overlay-action[disabled] { opacity: 0.4; cursor: not-allowed; }

.carnet-overlay-action-icon {
  font-size: 18px;
  line-height: 1;
  display: block;
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 13 (Phase α refactor)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS factory window.CarnetOverlay
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : fin du marker /Lot 8 helpers + ligne renderGaragePage.

JS_ANCHOR = """// ─── /Lot 8 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

JS_REPLACEMENT = """// ─── /Lot 8 helpers ──────────────────────────────────────────────────


// ─── Lot 13 (Phase α refactor) — CarnetOverlay factory ─────────────────
// Composant réutilisable pour créer un mode plein écran avec ouverture/
// fermeture standardisée. Utilisé par les Lots 14+. Les Lots 5/6/7
// conservent leurs propres window.CARNET_X_DEMO indépendants.
//
// Convention :
//   - L'élément overlay reçoit la classe `.carnet-overlay`.
//   - Toute interaction avec un élément `data-action="closeOverlay"`
//     déclenche la fermeture (pas besoin d'un handler manuel par mode).
//   - Le body scroll est verrouillé pendant l'ouverture, restauré à la
//     fermeture.
//
// Usage type pour un nouveau mode (Lot 14+) :
//   window.CARNET_FOO_DEMO = CarnetOverlay.create(
//     'carnet-foo-overlay',
//     function() { return renderFooContent(); }
//   );
//   CARNET_FOO_DEMO.open();   // ouvre
//   CARNET_FOO_DEMO.close();  // ferme (ou clic sur [data-action=closeOverlay])
//
window.CarnetOverlay = {
  create: function(overlayId, renderFn) {
    return {
      open: function() {
        let overlay = document.getElementById(overlayId);
        if (!overlay) {
          overlay = document.createElement('div');
          overlay.id = overlayId;
          overlay.className = 'carnet-overlay';
          document.body.appendChild(overlay);
          overlay.addEventListener('click', function(e) {
            const closeBtn = e.target.closest('[data-action="closeOverlay"]');
            if (closeBtn) {
              overlay.setAttribute('hidden', '');
              document.body.style.overflow = '';
            }
          });
        }
        overlay.innerHTML = renderFn();
        overlay.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
      },
      close: function() {
        const overlay = document.getElementById(overlayId);
        if (overlay) overlay.setAttribute('hidden', '');
        document.body.style.overflow = '';
      }
    };
  }
};
// ─── /Lot 13 (Phase α refactor) ────────────────────────────────────────


function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 13 (Phase α refactor) — carnet-overlay composant générique",
    requires=[
        # Le Lot 8 doit être en place (Garage Dashboard ajoute la dernière
        # règle CSS et le marker /Lot 8 helpers que ce lot utilise comme
        # bornes d'ancrage).
        "LOT 8 (Phase α) — Garage Dashboard Complet",
    ],
    patches=[
        Patch(
            name="CSS générique .carnet-overlay-*",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 13 (Phase α refactor) — carnet-overlay générique",
        ),
        Patch(
            name="JS factory window.CarnetOverlay",
            anchor=JS_ANCHOR,
            replacement=JS_REPLACEMENT,
            idempotence_marker="Lot 13 (Phase α refactor) — CarnetOverlay factory",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
