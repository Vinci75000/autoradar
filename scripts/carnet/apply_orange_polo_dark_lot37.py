#!/usr/bin/env python3
"""
CARNET · Lot 37 — Charte v9 : migration orange-polo-dark

Source        : audit complet des couleurs. Le Lot 35 a posé la variable
                --orange-polo-dark:#D24C12. Ce lot migre les 6 usages
                encore codés en dur vers la variable.

  #D24C12 est l'orange Polo en état :active (bouton pressé) — une
  déclinaison plus profonde de --orange-polo. Usages :
    .sheet-btn.primary:active        background + border-color
    .empty-state-cta.primary:active  background + border-color
    .new-alert-btn:active            background
    .builder-cta:active              background
  Tous des fonds de CTA pressé — aucun piège de lisibilité.

Note encodage/anchors :
  Première version : 4 anchors NOT FOUND — j'avais sur-indenté.
  Indentations RÉELLES vérifiées au od -c / cat -A :
    .sheet-btn.primary:active     → sélecteur 4 espaces, propriétés 6
    .empty-state-cta.primary:active → idem (4 / 6)
    .new-alert-btn:active         → sélecteur 0 espace, propriétés 2
    .builder-cta:active           → idem (0 / 2)

Scope          : 4 patches sur index.html.
  6 usages en 4 blocs : 2 blocs ont background + border-color
  consécutifs (fusionnés en 1 patch chacun — cf. Leçon 8), 2 blocs
  ont 1 seul usage.

Note sécurité :
  - Anchors 2-bornes : chaque patch inclut le sélecteur en borne haute
    et une ligne réelle en borne basse. Indentations exactes.
  - Migration pure : #d24c12 → var(--orange-polo-dark), même couleur.
    Les !important conservés. Zéro changement visuel.
  - Garde-fou v1.1 : 4 anchors vérifiées non-1-borne.
  - Idempotence : marker = var(--orange-polo-dark) dans le contexte.

Hors scope :
  - Migration vert-vivant-clair (Lot 38)

Prérequis : Lot 35 appliqué (--orange-polo-dark posée)
Usage     :
    python3 apply_orange_polo_dark_lot37.py path/to/index.html
    python3 apply_orange_polo_dark_lot37.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


PATCHES = [
    Patch(
        name="CSS-1 · .sheet-btn.primary:active (background + border-color)",
        anchor="""    .sheet-btn.primary:active {
      background: #d24c12 !important;
      border-color: #d24c12 !important;""",
        replacement="""    .sheet-btn.primary:active {
      background: var(--orange-polo-dark) !important;
      border-color: var(--orange-polo-dark) !important;""",
        idempotence_marker="""    .sheet-btn.primary:active {
      background: var(--orange-polo-dark) !important;""",
    ),
    Patch(
        name="CSS-2 · .empty-state-cta.primary:active (background + border-color)",
        anchor="""    .empty-state-cta.primary:active {
      background: #d24c12 !important;
      border-color: #d24c12 !important;""",
        replacement="""    .empty-state-cta.primary:active {
      background: var(--orange-polo-dark) !important;
      border-color: var(--orange-polo-dark) !important;""",
        idempotence_marker="""    .empty-state-cta.primary:active {
      background: var(--orange-polo-dark) !important;""",
    ),
    Patch(
        name="CSS-3 · .new-alert-btn:active (background)",
        anchor=""".new-alert-btn:active {
  background: #d24c12;
}""",
        replacement=""".new-alert-btn:active {
  background: var(--orange-polo-dark);
}""",
        idempotence_marker=""".new-alert-btn:active {
  background: var(--orange-polo-dark);""",
    ),
    Patch(
        name="CSS-4 · .builder-cta:active (background)",
        anchor=""".builder-cta:active:not(:disabled) {
  background: #d24c12;
  opacity: 1;""",
        replacement=""".builder-cta:active:not(:disabled) {
  background: var(--orange-polo-dark);
  opacity: 1;""",
        idempotence_marker=""".builder-cta:active:not(:disabled) {
  background: var(--orange-polo-dark);""",
    ),
]


PATCHSET = PatchSet(
    name="Lot 37 — Charte v9 : migration orange-polo-dark",
    requires=[
        "--orange-polo-dark",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
