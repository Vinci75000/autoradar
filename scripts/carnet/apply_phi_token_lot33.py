#!/usr/bin/env python3
"""
CARNET · Lot 33 (Phase α) — Ratios φ : usage du token --phi

Source        : audit A, étape A-iii — dernier maillon de la géométrie
                sacrée après les espacements (Lots 29-31) et la typo
                (Lot 32).

  Le Lot 28 a posé le token --phi:1.618 dans :root. L'audit montre qu'il
  n'est JAMAIS utilisé : les 7 aspect-ratio des photos de cards et de
  sheets écrivent "1.618 / 1" EN DUR.

  Sélecteurs concernés (tous des conteneurs de photo de véhicule) :
    .sheet-content-detail .car-thumb-hero
    .advice-card .car-thumb-card
    .match-card .car-thumb-card
    .auction-card .car-thumb-card
    .garage-card .car-thumb-card
    .listing-card .car-thumb-card
    .skeleton-thumb

  C'est le problème de fond de l'audit A : les refontes φ précédentes
  ont écrit les valeurs en dur faute de token. Le Lot 28 a posé le
  token ; ce lot fait l'usage.

Pourquoi c'est SANS risque :
  --phi vaut 1.618. Remplacer "1.618 / 1" par "var(--phi) / 1" ne change
  STRICTEMENT RIEN au rendu — pure cohérence de tokens. Le jour où l'on
  voudrait ajuster la proportion, une seule ligne dans :root suffira au
  lieu de 7 chasses dans le fichier.

  Le line-height: 1.65 n'est PAS touché — pas φ, interligne délibéré.

Note encodage/anchors :
  Première version : 7 anchors NOT FOUND — j'avais supposé une
  indentation 8 espaces, le fichier est en 6. De plus, 3 zones
  (.match-card / .auction-card / .listing-card) ont un contexte
  identique ; leurs anchors incluent donc le SÉLECTEUR pour être uniques.
  Indentation 6 espaces vérifiée au od -c.

Scope          : 7 patches sur index.html — un par aspect-ratio.

Note sécurité :
  - Anchors 2-bornes : chaque patch encadre la ligne aspect-ratio par
    sa/ses ligne(s) voisine(s) réelle(s), indentation 6 espaces vérifiée.
  - Aucune valeur changée — "1.618" → "var(--phi)" qui VAUT 1.618.
    Zéro impact visuel.
  - Garde-fou v1.1 : 7 anchors vérifiées non-1-borne.
  - Idempotence : marker = "var(--phi) / 1" + contexte du patch.

Hors scope :
  - line-height: 1.65 (pas φ)
  - --phi-inv : aucun usage en dur détecté
  - retrait des tokens --s-5/6/7/8 sans usage (étape finale)

Prérequis : Lot 32 (Phase α) appliqué
Usage     :
    python3 apply_phi_token_lot33.py path/to/index.html
    python3 apply_phi_token_lot33.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# Les 7 patches — indentation 6 espaces, anchors incluant le sélecteur
# pour les zones au contexte identique.
# ═══════════════════════════════════════════════════════════════════════

PATCHES = [
    Patch(
        name="CSS-1 · .sheet-content-detail .car-thumb-hero aspect-ratio",
        anchor=""".sheet-content-detail .car-thumb-hero {
      width: 100%;
      aspect-ratio: 1.618 / 1;
      min-height: 0;""",
        replacement=""".sheet-content-detail .car-thumb-hero {
      width: 100%;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */
      min-height: 0;""",
        idempotence_marker=""".sheet-content-detail .car-thumb-hero {
      width: 100%;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */""",
    ),
    Patch(
        name="CSS-2 · .advice-card .car-thumb-card aspect-ratio",
        anchor=""".advice-card .car-thumb-card {
      width: 100%; height: auto; aspect-ratio: 1.618 / 1; min-height: 0;
    }""",
        replacement=""".advice-card .car-thumb-card {
      width: 100%; height: auto; aspect-ratio: var(--phi) / 1; min-height: 0; /* Lot 33 */
    }""",
        idempotence_marker="""      width: 100%; height: auto; aspect-ratio: var(--phi) / 1; min-height: 0; /* Lot 33 */""",
    ),
    Patch(
        name="CSS-3 · .match-card .car-thumb-card aspect-ratio",
        anchor=""".match-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: 1.618 / 1;
      min-height: 0;""",
        replacement=""".match-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */
      min-height: 0;""",
        idempotence_marker=""".match-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */""",
    ),
    Patch(
        name="CSS-4 · .auction-card .car-thumb-card aspect-ratio",
        anchor=""".auction-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: 1.618 / 1;
      min-height: 0;""",
        replacement=""".auction-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */
      min-height: 0;""",
        idempotence_marker=""".auction-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */""",
    ),
    Patch(
        name="CSS-5 · .garage-card .car-thumb-card aspect-ratio",
        anchor="""      height: auto;
      aspect-ratio: 1.618 / 1;  /* golden ratio horizontal */
      min-height: 0;""",
        replacement="""      height: auto;
      aspect-ratio: var(--phi) / 1;  /* Lot 33 — golden ratio horizontal */
      min-height: 0;""",
        idempotence_marker="""      aspect-ratio: var(--phi) / 1;  /* Lot 33 — golden ratio horizontal */""",
    ),
    Patch(
        name="CSS-6 · .listing-card .car-thumb-card aspect-ratio",
        anchor=""".listing-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: 1.618 / 1;
      min-height: 0;""",
        replacement=""".listing-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */
      min-height: 0;""",
        idempotence_marker=""".listing-card .car-thumb-card {
      width: 100%;
      height: auto;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */""",
    ),
    Patch(
        name="CSS-7 · .skeleton-thumb aspect-ratio",
        anchor=""".skeleton-thumb {
      width: 100%;
      aspect-ratio: 1.618 / 1;
      background: var(--papier-soft);""",
        replacement=""".skeleton-thumb {
      width: 100%;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */
      background: var(--papier-soft);""",
        idempotence_marker=""".skeleton-thumb {
      width: 100%;
      aspect-ratio: var(--phi) / 1; /* Lot 33 */""",
    ),
]


PATCHSET = PatchSet(
    name="Lot 33 (Phase α) — Ratios phi : usage du token --phi",
    requires=[
        "Lot 32 — réaligné sur √φ",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
