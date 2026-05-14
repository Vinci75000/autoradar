#!/usr/bin/env python3
"""
CARNET · Lot 20 (Phase α) — Sheets création : flow Nouvelle alerte (builder)

Source        : Audit Lot 20. Les deux « sheets création » sont :
                  1. Ajout voiture (garage-form-*) — DÉJÀ refondu en v5.x
                     (bloc d'harmonisation lignes 6406-6447 : gap Fibonacci
                     13/5, padding 13, focus encre). Non touché.
                  2. Nouvelle alerte (builder-*) — JAMAIS refondu. Aucun
                     override v5.x/Fibonacci. C'est l'objet de ce lot.

Le builder est un flow multi-étapes à cards/chips/accordions (pas
d'inputs texte classiques). Deux écarts nets avec le langage établi :

  A. .builder-cta : même problème que .new-alert-btn avant le Lot 18 —
     height 50px fixe, font var(--sans), letter-spacing 0.1em, feedback
     opacity-only. Non aligné sur le langage de boutons v5.4x.
  B. .builder-step-title / .builder-step-sub : valeurs via variables
     (--t-2xl = 36px, --s-2/5) au lieu des valeurs Fibonacci explicites
     adoptées pour le hero au Lot 16.

Scope         : 2 patches CSS sur index.html (surcharges additives).

Patch CSS-1 — .builder-cta refonte φ :
  - Hauteur : height auto + min-height 55px (Fibonacci) — vs 50px fixe
  - Police : var(--mono) — aligné v5.4x (vs var(--sans))
  - Letter-spacing : 0.12em — aligné v5.4x (vs 0.1em)
  - Font-size : 12px — même cran que .new-alert-btn (CTA page-level)
  - Padding : 17px 21px (Fibonacci-ish)
  - Couleur : orange polo fill — cohérent décision Lot 18b (.new-alert-btn)
    Le CTA « + Nouvelle alerte » et le CTA du flow qu'il ouvre parlent
    désormais exactement la même langue chromatique.
  - Pressed : background #d24c12 + scale 0.985 + opacity 1 (vs opacity 0.65)
  - Disabled : conservé (opacity 0.35) — non touché, déjà correct
  - .builder-cta-arrow : passe en papier-bright (sinon « › » orange sur
    fond orange = invisible — même fix que .new-alert-plus au Lot 18b)

Patch CSS-2 — .builder-step-title / .builder-step-sub refonte φ :
  - step-title : font-size 55px (Fibonacci, = hero Lot 16), font-weight 500,
    line-height 0.93, margin-bottom 13px (Fibonacci, vs --s-2)
  - step-sub : font-size 17px, line-height 1.45, margin-bottom 21px
    (Fibonacci, vs --s-5) — aligné .hero-sub du Lot 16
  - @media >=600px : step-title 72px (un cran sous le hero 89px — le
    builder est un sous-flow, pas la page d'accueil)

Mécanisme :
  Surcharges additives après le bloc Lot 18b, avant </style>. Aucun
  !important concurrent sur ces 3 sélecteurs (vérifié) — la cascade
  naturelle (déclaration postérieure, spécificité égale) suffit.

Hors scope :
  - garage-form-* (Ajout voiture) — déjà refondu v5.x, non touché
  - .builder-type-card / chips / accordions — composants déjà cohérents
    (Fibonacci, charte), non touchés
  - .builder-header / progress / counter — non touchés, hors périmètre CTA+typo
  - Logique JS du Builder — inchangée

Prérequis : Lot 18b (Phase α) appliqué (le marker /LOT 18b sert d'anchor ;
            cohérence chromatique orange polo héritée du Lot 18b)
Usage     :
    python3 apply_builder_refonte_lot20.py path/to/index.html
    python3 apply_builder_refonte_lot20.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : .builder-cta + .builder-step-title/sub refonte φ
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc Lot 18b, avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18b (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 18b (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 20 (Phase α) — Sheets création : flow Nouvelle alerte (builder)
   Le form Ajout voiture (garage-form-*) est déjà refondu v5.x.
   Ce lot aligne le builder : CTA langage v5.4x + typo step Fibonacci.
   ═══════════════════════════════════════════════════════════════════════ */

/* .builder-cta — aligné langage boutons v5.4x + orange polo (cf. Lot 18b) */
.builder-cta {
  height: auto;
  min-height: 55px;
  padding: 17px 21px;
  background: var(--orange-polo);
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: opacity var(--duration-fast) ease,
              background var(--duration-fast) ease,
              transform var(--duration-fast) ease;
}
.builder-cta:active:not(:disabled) {
  background: #d24c12;
  opacity: 1;
  transform: scale(0.985);
}
/* disabled conservé tel quel (opacity 0.35) — la règle d'origine reste valide */

/* La flèche passe en papier-bright — sinon « › » orange sur fond orange */
.builder-cta-arrow {
  color: var(--papier-bright);
  font-size: 16px;
}

/* .builder-step-title / -sub — valeurs Fibonacci explicites (alignées hero Lot 16) */
.builder-step-title {
  font-size: 55px;
  font-weight: 500;
  line-height: 0.93;
  letter-spacing: -0.025em;
  margin-bottom: 13px;
}
.builder-step-sub {
  font-size: 17px;
  line-height: 1.45;
  margin-bottom: 21px;
}
@media (min-width: 600px) {
  .builder-step-title {
    font-size: 72px;
    line-height: 0.92;
  }
  .builder-step-sub {
    font-size: 19px;
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 20 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 20 (Phase α) — Sheets création : flow Nouvelle alerte (builder)",
    requires=[
        # Lot 18b fournit le marker /LOT 18b (Phase α) qui sert d'anchor,
        # et la décision chromatique orange polo dont ce lot hérite.
        "LOT 18b (Phase α) — .new-alert-btn alignement couleur orange polo",
    ],
    patches=[
        Patch(
            name="CSS — .builder-cta langage v5.4x orange polo + .builder-step-title/sub Fibonacci",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 20 (Phase α) — Sheets création : flow Nouvelle alerte (builder)",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
