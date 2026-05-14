#!/usr/bin/env python3
"""
CARNET · Lot 17 (Phase α) — TabBar bottom refonte φ

Source        : Refonte de la barre de navigation bottom (tabnav, 4 onglets :
                Annonces / Enchères / Garage / À l'affût) selon proportions
                Fibonacci/φ.

Scope         : 1 patch CSS sur index.html (pas de JS — la tabnav est en
                HTML inline statique, le refresh est purement stylistique).

Refonte TabBar :
  - Hauteur : Fibonacci 55px (vs var(--tabnav) variable) + safe-area iOS préservée
  - Item : gap 5px, padding 8px (Fibonacci 5/8), position relative pour la barre
  - Indicateur d'onglet actif : barre 21px en orange polo (signature CARNET),
    apparition par scaleX animée — c'était absent avant (juste un changement
    de couleur de texte)
  - Icône : transition opacity + transform, feedback pressed scale 0.92
  - Label actif : font-weight 700 (vs 600) pour ancrer le regard

Couplage non destructif :
  Tout est en surcharge additive après le bloc base .tabnav existant
  (lignes ~653-684). Aucune suppression. Si le patch échoue, le style
  base reste fonctionnel.

Note : ce lot avait été détecté par erreur comme « déjà présent » lors
  d'une désynchronisation de fichier de travail. Il est ici fait
  proprement sur la base saine resynchronisée depuis main (md5 96e413f0).

Hors scope :
  - Live badge tabnav (déjà en place, Chunk 7.a — non touché)
  - Icônes SVG des onglets (conservées telles quelles)
  - Logique switchTab (inchangée)

Prérequis : Lot 16 (Phase α) appliqué (le marker /LOT 16 sert d'anchor)
Usage     :
    python3 apply_tabbar_refonte_lot17.py path/to/index.html
    python3 apply_tabbar_refonte_lot17.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : surcharges TabBar refonte φ
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc Lot 16, avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 16 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 16 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 17 (Phase α) — TabBar bottom refonte φ
   Indicateur d'onglet actif = barre orange polo (signature CARNET).
   Espacements Fibonacci : 5 / 8 / 21 / 55.
   ═══════════════════════════════════════════════════════════════════════ */

/* Hauteur Fibonacci (55) — surcharge directe, safe-area iOS préservée */
.tabnav {
  height: calc(55px + env(safe-area-inset-bottom, 0));
}

/* Item — espacements Fibonacci + position relative pour la barre active */
.tabnav-item {
  gap: 5px;
  padding: 8px var(--s-2);
  position: relative;
}

/* Barre indicateur d'onglet actif — signature orange polo, scaleX animée */
.tabnav-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  width: 21px;
  height: 2px;
  background: var(--orange-polo);
  border-radius: 0 0 1px 1px;
  transform: translateX(-50%) scaleX(0);
  transform-origin: center;
  transition: transform var(--duration-fast) ease;
  pointer-events: none;
}
.tabnav-item.active::before {
  transform: translateX(-50%) scaleX(1);
}

/* Icône — transition douce + feedback pressed (scale 0.92) */
.tabnav-icon {
  transition: opacity var(--duration-fast) ease, transform var(--duration-fast) ease;
}
.tabnav-item.active .tabnav-icon {
  opacity: 1;
}
.tabnav-item:active .tabnav-icon {
  opacity: 1;
  transform: scale(0.92);
}

/* Label — l'onglet actif gagne un poil de poids pour ancrer le regard */
.tabnav-item.active {
  color: var(--encre);
  font-weight: 700;
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 17 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 17 (Phase α) — TabBar bottom refonte φ",
    requires=[
        # Lot 16 fournit le marker /LOT 16 (Phase α) qui sert d'anchor.
        "LOT 16 (Phase α) — Hero affût + KPI bar refonte φ",
    ],
    patches=[
        Patch(
            name="CSS — TabBar refonte φ (hauteur Fibonacci + barre indicateur orange polo + feedback pressed)",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 17 (Phase α) — TabBar bottom refonte φ",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
