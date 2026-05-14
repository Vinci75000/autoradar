#!/usr/bin/env python3
"""
CARNET · Lot 39 — Charte v9 : couleurs de catégorie (clôture)

Source        : audit complet des couleurs. Les Lots 35-38 ont migré
                les couleurs SÉMANTIQUES (rouge-alerte, brun-enchere,
                orange-polo-dark, vert-vivant-clair). Restaient 3 couleurs
                de CATÉGORIE codées en dur, membres de 2 systèmes de
                classification.

  Système 1 — .alert-card-type (4 types d'alerte) :
    .modele   → var(--orange-polo)   déjà charte
    .criteres → var(--vert-anglais)  déjà charte
    .rarete   → #8A4A8A violet       orphelin
    .signal   → #B8761F ambre-brun   orphelin
  Système 2 — .garage-deadline-bar (3 niveaux de sévérité) :
    .urgent   → var(--orange-polo)   déjà charte
    .warning  → #C8943A ambre        orphelin
    .ok       → var(--vert-anglais)  déjà charte

  Dans chaque système, 2/4 ou 2/3 des couleurs sont déjà dans la charte —
  il manque juste le maillon orphelin. Même pattern que la charte v9 :
  nommer ce qui existe pour compléter le système.

Décisions (validées) :
  · #8A4A8A (violet .rarete) → NOMMER --accent-rarete.
    Aucun équivalent ni dans la charte ni dans les palettes Pantone
    explorées (les violets Pantone sont bien plus saturés). C'est une
    couleur unique — violet poudré, dit "rare/précieux" sans crier.
    Elle mérite son nom.
  · #C8943A (ambre .deadline.warning) → NOMMER --ambre-warning.
    Volontairement plus clair/jaune que --or (#BA7517) pour se
    distinguer du orange .urgent voisin dans la même barre. La nuance
    est intentionnelle → variable propre.
  · #B8761F (ambre-brun .signal) → RATTACHER à var(--or).
    Distance ~5 de --or (#BA7517) — fusion invisible. Pas besoin d'une
    variable de plus pour une couleur quasi identique à une existante.

Scope          : 4 patches sur index.html.
  - CSS-1 : ajoute --accent-rarete + --ambre-warning au :root, à la fin
            du bloc charte v9 (après --orange-polo-dark).
  - CSS-2 : .alert-card-type.rarete  → var(--accent-rarete)
  - CSS-3 : .alert-card-type.signal  → var(--or)  [rattachement]
  - CSS-4 : .garage-deadline-bar.warning → var(--ambre-warning)

Note sécurité :
  - CSS-1 : anchor 2-bornes — --orange-polo-dark (haute) + ligne blanche
    + --display (basse). Les 2 nouvelles lignes s'insèrent au milieu.
  - CSS-2/3/4 : lignes compactes uniques, anchor = ligne entière +
    ligne voisine. Le replacement rompt l'anchor.
  - Migration pure : #hex → var(), même couleur (sauf #B8761F→--or,
    décalage ~5 unités, imperceptible et voulu). Zéro régression visuelle.
  - Garde-fou v1.1 : 4 anchors vérifiées non-1-borne.
  - Idempotence : markers = la nouvelle référence var() dans son contexte.

Hors scope :
  - rien — ce lot CLÔT la charte v9. Après : 0 couleur hors charte
    dans les modules (sauf le logo Google, normatif).

Prérequis : Lot 38 appliqué
Usage     :
    python3 apply_couleurs_categorie_lot39.py path/to/index.html
    python3 apply_couleurs_categorie_lot39.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — ajoute --accent-rarete + --ambre-warning au :root
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : --orange-polo-dark (borne haute) + ligne blanche +
# --display (borne basse). Les 2 lignes s'insèrent au milieu.

CSS1_ANCHOR = """  --orange-polo-dark:#D24C12;  /* orange Polo état :active — 6 usages en dur à migrer */

  --display:'Bodoni Moda','Times New Roman',serif;"""

CSS1_REPLACEMENT = """  --orange-polo-dark:#D24C12;  /* orange Polo état :active — 6 usages en dur à migrer */
  --accent-rarete:#8A4A8A;     /* catégorie : type d'alerte « rareté » — Lot 39 */
  --ambre-warning:#C8943A;     /* catégorie : sévérité « warning » — Lot 39 */

  --display:'Bodoni Moda','Times New Roman',serif;"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — .alert-card-type.rarete → var(--accent-rarete)
# ═══════════════════════════════════════════════════════════════════════

CSS2_ANCHOR = """    .alert-card-type.criteres { color: var(--vert-anglais); }
    .alert-card-type.rarete { color: #8a4a8a; }
    .alert-card-type.signal { color: #b8761f; }"""

CSS2_REPLACEMENT = """    .alert-card-type.criteres { color: var(--vert-anglais); }
    .alert-card-type.rarete { color: var(--accent-rarete); }
    .alert-card-type.signal { color: #b8761f; }"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — .alert-card-type.signal → var(--or)  [rattachement]
# ═══════════════════════════════════════════════════════════════════════

CSS3_ANCHOR = """    .alert-card-type.rarete { color: var(--accent-rarete); }
    .alert-card-type.signal { color: #b8761f; }
    .alert-card-paused {"""

CSS3_REPLACEMENT = """    .alert-card-type.rarete { color: var(--accent-rarete); }
    .alert-card-type.signal { color: var(--or); }
    .alert-card-paused {"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 4 — .garage-deadline-bar.warning → var(--ambre-warning)
# ═══════════════════════════════════════════════════════════════════════

CSS4_ANCHOR = """.garage-deadline-bar.urgent{ background:var(--orange-polo); }
.garage-deadline-bar.warning{ background:#C8943A; }
.garage-deadline-bar.ok{ background:var(--vert-anglais); }"""

CSS4_REPLACEMENT = """.garage-deadline-bar.urgent{ background:var(--orange-polo); }
.garage-deadline-bar.warning{ background:var(--ambre-warning); }
.garage-deadline-bar.ok{ background:var(--vert-anglais); }"""


PATCHSET = PatchSet(
    name="Lot 39 — Charte v9 : couleurs de catégorie (clôture)",
    requires=[
        # Marker réel présent après le Lot 36 (la variable vert-vivant-clair).
        "--vert-vivant-clair",
    ],
    patches=[
        Patch(
            name="CSS-1 · ajoute --accent-rarete + --ambre-warning au :root",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="--accent-rarete:#8A4A8A;",
        ),
        Patch(
            name="CSS-2 · .alert-card-type.rarete → var(--accent-rarete)",
            anchor=CSS2_ANCHOR,
            replacement=CSS2_REPLACEMENT,
            idempotence_marker=".alert-card-type.rarete { color: var(--accent-rarete); }",
        ),
        Patch(
            name="CSS-3 · .alert-card-type.signal → var(--or) [rattachement]",
            anchor=CSS3_ANCHOR,
            replacement=CSS3_REPLACEMENT,
            idempotence_marker=".alert-card-type.signal { color: var(--or); }",
        ),
        Patch(
            name="CSS-4 · .garage-deadline-bar.warning → var(--ambre-warning)",
            anchor=CSS4_ANCHOR,
            replacement=CSS4_REPLACEMENT,
            idempotence_marker=".garage-deadline-bar.warning{ background:var(--ambre-warning); }",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
