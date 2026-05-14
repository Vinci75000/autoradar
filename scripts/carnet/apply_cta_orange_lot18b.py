#!/usr/bin/env python3
"""
CARNET · Lot 18b (Phase α) — .new-alert-btn alignement couleur orange polo

Source        : Suite directe du Lot 18. Sly a choisi l'alignement strict :
                le CTA principal .new-alert-btn passe en orange polo, comme
                le .sheet-btn.primary v5.4x.

Scope         : 1 patch CSS sur index.html (surcharge additive, 3 règles).

Changements :
  - .new-alert-btn          background encre → var(--orange-polo)
  - .new-alert-btn:active   background #0d0d0d → #d24c12 (darken orange,
                            identique au pressed de .sheet-btn.primary)
  - .new-alert-plus         color orange polo → var(--papier-bright)
                            (sinon « + » orange sur fond orange = invisible)

Mécanisme :
  Surcharge par cascade naturelle — les 3 règles sont déclarées APRÈS le
  bloc Lot 18 (et après le CSS base .new-alert-btn ligne ~255), même
  spécificité, donc elles gagnent. Aucun !important nécessaire.

Hors scope :
  - Géométrie / typo du .new-alert-btn — déjà réglée au Lot 18, non touchée
  - .sheet-btn.primary — déjà orange polo en v5.4x, non touché

Prérequis : Lot 18 (Phase α) appliqué (le marker /LOT 18 sert d'anchor)
Usage     :
    python3 apply_cta_orange_lot18b.py path/to/index.html
    python3 apply_cta_orange_lot18b.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : .new-alert-btn → orange polo
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc Lot 18, avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 18b (Phase α) — .new-alert-btn alignement couleur orange polo
   Aligne strictement le CTA page-level sur .sheet-btn.primary v5.4x.
   ═══════════════════════════════════════════════════════════════════════ */

.new-alert-btn {
  background: var(--orange-polo);
}
.new-alert-btn:active {
  background: #d24c12;
}
.new-alert-plus {
  color: var(--papier-bright);
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18b (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 18b (Phase α) — .new-alert-btn alignement couleur orange polo",
    requires=[
        "LOT 18 (Phase α) — CTA principal .new-alert-btn refonte φ",
    ],
    patches=[
        Patch(
            name="CSS — .new-alert-btn fill orange polo + pressed darken + plus papier-bright",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 18b (Phase α) — .new-alert-btn alignement couleur orange polo",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
