#!/usr/bin/env python3
"""
CARNET · Lot 18 (Phase α) — CTA principal .new-alert-btn refonte φ

Source        : Harmonisation du bouton CTA principal de la page « À l'affût »
                (.new-alert-btn « + Nouvelle alerte ») avec le langage de
                boutons déjà établi en v5.4x sur les .sheet-btn.

Contexte      : Les .sheet-btn (boutons de sheets) ont DÉJÀ été refondus en
                v5.4x — padding Fibonacci 13/21, font mono 11px, letter-spacing
                0.12em, 6 variantes (primary orange polo / secondary / tertiary
                / ghost / danger bordeaux / success vert anglais).
                Le .new-alert-btn était le seul CTA majeur resté en version
                originale (height 50px fixe, font sans, feedback opacity-only).
                Ce lot l'aligne sur le même langage.

Scope         : 1 patch CSS sur index.html (surcharge additive).

Refonte .new-alert-btn :
  - Hauteur : min-height 55px (Fibonacci) + height auto — vs 50px fixe
  - Police : var(--mono) — aligné v5.4x (vs var(--sans))
  - Letter-spacing : 0.12em — aligné v5.4x (vs 0.1em)
  - Font-size : 12px — un cran au-dessus des sheet-btn (11px) car CTA
    page-level qui mérite plus de présence
  - Padding : 17px 21px (Fibonacci-ish)
  - Feedback pressed : background darken (#0d0d0d) + scale 0.985 + opacity 1
    — vs opacity 0.7 seul. Cohérent avec le pattern pressed des Lots 16/17.

Choix d'identité — couleur conservée :
  Le .new-alert-btn RESTE en encre noir (fond encre, texte papier).
  Le .sheet-btn.primary v5.4x est en orange polo. C'est volontaire :
  le CTA page-level garde sa présence forte distincte du CTA in-sheet.
  Le « + » conserve sa couleur orange polo (lien chromatique avec la charte).
  → Si tu préfères aligner strictement (new-alert-btn en orange polo),
    c'est un patch d'une ligne à part — dis-le et je le fais.

Couplage non destructif :
  Surcharge additive après le bloc Lot 17, avant </style>.
  .new-alert-btn n'a aucune règle !important concurrente ailleurs
  (vérifié) — la cascade naturelle suffit, pas besoin de !important.

Hors scope :
  - .sheet-btn et variantes — déjà refondus en v5.4x, non touchés
  - CTA éditoriaux spécifiques (.discover-cta, .paywall-cta, .builder-cta,
    .auth-btn-*, .profile-onboarding-cta, .ai-advice-cta) — composants
    dédiés, lot futur si besoin
  - .topbar-icon-btn — boutons icônes, hors périmètre CTA

Prérequis : Lot 17 (Phase α) appliqué (le marker /LOT 17 sert d'anchor)
Usage     :
    python3 apply_cta_principal_lot18.py path/to/index.html
    python3 apply_cta_principal_lot18.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : surcharge .new-alert-btn refonte φ
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc Lot 17, avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 17 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 17 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 18 (Phase α) — CTA principal .new-alert-btn refonte φ
   Aligne le CTA page-level sur le langage de boutons v5.4x (.sheet-btn).
   Couleur encre noir conservée (présence page-level distincte du in-sheet).
   ═══════════════════════════════════════════════════════════════════════ */

.new-alert-btn {
  height: auto;
  min-height: 55px;
  padding: 17px 21px;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: opacity var(--duration-fast) ease,
              background var(--duration-fast) ease,
              transform var(--duration-fast) ease;
}
.new-alert-btn:active {
  background: #0d0d0d;
  opacity: 1;
  transform: scale(0.985);
}

/* Le « + » conserve l'orange polo — lien chromatique avec la charte */
.new-alert-plus {
  font-size: 16px;
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 18 (Phase α) — CTA principal .new-alert-btn refonte φ",
    requires=[
        # Lot 17 fournit le marker /LOT 17 (Phase α) qui sert d'anchor.
        "LOT 17 (Phase α) — TabBar bottom refonte φ",
    ],
    patches=[
        Patch(
            name="CSS — .new-alert-btn aligné langage boutons v5.4x (mono, Fibonacci, feedback pressed)",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 18 (Phase α) — CTA principal .new-alert-btn refonte φ",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
