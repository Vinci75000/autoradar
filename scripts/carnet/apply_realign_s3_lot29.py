#!/usr/bin/env python3
"""
CARNET · Lot 29 (Phase α) — Réalignement du token --s-3 sur Fibonacci

Source        : audit A, étape A-iii (refonte des sections en géométrie
                sacrée). Le Lot 28 a posé les tokens --fib-* propres ;
                ce lot commence la MIGRATION des sections encore en
                échelle linéaire.

  Contexte : index.html porte deux échelles d'espacement. Le Lot 28 a
  ajouté les tokens Fibonacci (--fib-1..8 = 4/8/13/21/34/55/89/144) sans
  toucher aux tokens linéaires historiques (--s-1..8 = 4/8/12/16/20/24/
  32/40). Reste à faire converger les ~120 usages de --s-3..7 vers la
  géométrie sacrée.

  Stratégie globale (par paliers de risque croissant) :
    Lot 29 — --s-3 : 12→13px, delta +1px           ← CE LOT, le plus sûr
    Lot 30 — --s-4 : 16→21px, delta +5px            (réalignement vérifié)
    Lot 31 — --s-5/6/7 : deltas +14..+57px          (sélecteur par sélecteur)
  Au terme, les tokens --s-* n'ont plus aucun usage et peuvent être
  retirés — le fichier est 100% Fibonacci.

Ce lot — pourquoi le réalignement global du TOKEN est sûr ici :
  --s-3 est utilisé 71×. Le passer de 12px à 13px = la VRAIE 3e valeur
  de Fibonacci. Delta de +1px : imperceptible à l'œil, et il va dans le
  SENS de la doctrine (corrige l'écart, ne le crée pas).
  Vérifications faites avant de décider :
    · Aucune redéfinition de --s-3 en @media — une seule source de vérité.
    · Les 5 calc() qui utilisent --s-3 sont tous des ajustements
      RELATIFS (+env(), -1px, *-1+4px, *-1+5px) — ils restent cohérents
      que --s-3 vaille 12 ou 13.
    · --s-3 est aussi utilisé par .garage-card-body (section déjà
      refondue v5.31) : +1px y est imperceptible et corrige la valeur
      vers le vrai Fibonacci — donc même là, ça aligne au lieu de casser.
  Réaligner le token = corriger 71 usages d'un seul patch propre, au
  lieu de 71 remplacements var(--s-3)→var(--fib-3) dispersés.

  Note : on ne RENOMME pas --s-3 en --fib-3 (ça obligerait à toucher les
  71 sites). On corrige sa VALEUR. Le renommage final (--s-* → --fib-*)
  se fera à la toute fin, quand on retirera les tokens linéaires, une
  fois toutes les valeurs convergées.

Scope          : 1 patch sur index.html
  - CSS-1 : --s-3:12px → --s-3:13px dans :root. Une seule ligne.
            Anchor 2-bornes : --s-2 (haute) + --s-3 + --s-4 (basse).

Note sécurité :
  - CSS-1 : anchor 2-bornes — "--s-2:8px;" + "--s-3:12px;" +
    "--s-4:16px;". La ligne du milieu change → anchor rompue.
  - Un seul token modifié, valeur uniquement. Aucun sélecteur touché,
    aucun autre token touché. CSS valide.
  - Garde-fou v1.1 : anchor vérifiée non-1-borne.
  - Idempotence : marker = "--s-3:13px" (la nouvelle valeur), absente
    tant que le patch n'est pas appliqué.

Hors scope :
  - --s-4 et au-dessus (Lots 30-31)
  - Le renommage --s-* → --fib-* (étape finale, après convergence)

Prérequis : Lot 28 (Phase α) appliqué
Usage     :
    python3 apply_realign_s3_lot29.py path/to/index.html
    python3 apply_realign_s3_lot29.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — réaligne --s-3 de 12px à 13px (vraie valeur Fibonacci)
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : --s-2 (borne haute) + --s-3 (la ligne qui change) +
# --s-4 (borne basse). L'anchor est rompue par le changement de valeur.

CSS1_ANCHOR = """  --s-2:8px;
  --s-3:12px;
  --s-4:16px;"""

CSS1_REPLACEMENT = """  --s-2:8px;
  --s-3:13px;  /* Lot 29 — réaligné sur Fibonacci (était 12px) */
  --s-4:16px;"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 29 (Phase α) — Réalignement du token --s-3 sur Fibonacci",
    requires=[
        # Marker réel présent dans le fichier après le Lot 28.
        "Géométrie sacrée — tokens Fibonacci",
    ],
    patches=[
        Patch(
            name="CSS-1 · --s-3 : 12px → 13px (vraie valeur Fibonacci)",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Lot 29 — réaligné sur Fibonacci",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
