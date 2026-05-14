#!/usr/bin/env python3
"""
CARNET · Lot 36 — Charte v9 : ajoute --vert-vivant-clair au :root

Source        : audit complet des couleurs. Le Lot 35 a posé les 4
                variables sémantiques (--vert-vivant, --rouge-alerte,
                --brun-enchere, --orange-polo-dark). L'audit de migration
                a révélé un cas que le Lot 35 n'avait pas anticipé.

  Le problème : #9FE1CB (vert menthe clair) est utilisé 11× dans les
  overlays démo (Co-pilote, Track Day, Gumball, Garage co-owned) pour
  les états positifs. Ces 11 usages sont sur fond SOMBRE (var(--encre)).

  --vert-vivant (#257226, Pantone 2273 C) est un vert SOMBRE — fait pour
  les fonds clairs (card crème). Le migrer tel quel sur ces 11 usages
  donnerait du vert sombre sur fond sombre = illisible.

  La solution (option A, validée) : #9FE1CB n'est pas une couleur
  "sauvage" à éliminer — c'est la déclinaison CLAIRE légitime du vert
  de service. On la NOMME : --vert-vivant-clair. Exactement comme
  --encre / --encre-soft : une couleur, deux déclinaisons selon le fond.

  Charte v9 — le vert de service a donc deux variantes :
    --vert-vivant       #257226   pour fonds clairs (card, chip crème)
    --vert-vivant-clair #9FE1CB   pour fonds sombres (overlays, header)
  (--vert-anglais #1F4D2F reste la couleur de MARQUE, distincte.)

Scope          : 1 patch sur index.html — purement additif.
  - CSS-1 : ajoute la ligne --vert-vivant-clair juste après
    --vert-vivant dans le bloc Charte v9 du :root.
    Anchor 2-bornes : --vert-vivant (haute) + --rouge-alerte (basse).

Note sécurité :
  - CSS-1 : anchor 2-bornes — la nouvelle ligne s'insère entre
    --vert-vivant et --rouge-alerte. L'anchor est rompue.
  - Purement additif : 1 variable ajoutée, 0 usage touché, 0 valeur
    existante modifiée. CSS valide.
  - Garde-fou v1.1 : anchor vérifiée non-1-borne.
  - Idempotence : marker = "--vert-vivant-clair".

Hors scope :
  - La migration des 11 usages #9FE1CB → var(--vert-vivant-clair) :
    Lot 39 (ce lot ne fait que poser la variable).
  - Migration brun-enchere (Lot 37), orange-polo-dark (Lot 38).

Prérequis : Lot 35 appliqué (variables sémantiques posées)
Usage     :
    python3 apply_vert_vivant_clair_var_lot36.py path/to/index.html
    python3 apply_vert_vivant_clair_var_lot36.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — ajoute --vert-vivant-clair entre --vert-vivant et --rouge-alerte
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : --vert-vivant (borne haute) + --rouge-alerte (basse).
# La nouvelle ligne s'insère au milieu → anchor rompue.

CSS1_ANCHOR = """  --vert-vivant:#257226;       /* succès, positif — Pantone 2273 C */
  --rouge-alerte:#9C2A2A;      /* négatif, danger — 27 usages en dur à migrer */"""

CSS1_REPLACEMENT = """  --vert-vivant:#257226;       /* succès, positif (fond clair) — Pantone 2273 C */
  --vert-vivant-clair:#9FE1CB; /* succès, positif (fond sombre) — Lot 36 */
  --rouge-alerte:#9C2A2A;      /* négatif, danger — 27 usages en dur à migrer */"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 36 — Charte v9 : ajoute --vert-vivant-clair au :root",
    requires=[
        # Marker réel présent dans le fichier après le Lot 35.
        "Charte v9",
    ],
    patches=[
        Patch(
            name="CSS-1 · ajoute --vert-vivant-clair (#9FE1CB, fonds sombres)",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="--vert-vivant-clair",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
