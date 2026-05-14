#!/usr/bin/env python3
"""
CARNET · Lot 32 (Phase α) — Réalignement de l'échelle typo sur √φ

Source        : audit A, étape A-iii. Après la convergence des
                espacements (Lots 29-31), ce lot fait converger
                l'échelle TYPOGRAPHIQUE sur la doctrine Carnet.

  La doctrine : échelle typo en steps √φ depuis base 15px —
      11 → 13 → 15 → 21 → 28 → 34 → 55 → 89
  Les paliers majeurs (34→55, 55→89) sont exactement φ.

  État de départ — l'échelle --t-* était linéaire/arbitraire :
      --t-xs:11  --t-sm:13  --t-base:15  --t-md:17
      --t-lg:22  --t-xl:28  --t-2xl:36

  Diagnostic :
    · --t-xs / --t-sm / --t-base (11/13/15) sont DÉJÀ conformes à la
      doctrine — rien à faire, on ne les touche pas.
    · --t-md / --t-lg / --t-xl / --t-2xl divergent — ce lot les réaligne.

Réalignement (les 4 tokens divergents) :
    --t-md  : 17 → 21px  (+4px)   échelon √φ
    --t-lg  : 22 → 28px  (+6px)   échelon √φ
    --t-xl  : 28 → 34px  (+6px)   échelon √φ
    --t-2xl : 36 → 55px  (+19px)  palier φ

Pourquoi le réalignement global des TOKENS est sûr ici :
  Vérifications faites avant de décider —
  1. @media — aucune redéfinition des tokens typo. Une seule source
     de vérité dans :root.
  2. calc() — aucun de --t-md/lg/xl/2xl n'est utilisé en arithmétique.
  3. --t-2xl, le gros delta (+19px) — ses 4 usages sont TOUS des titres
     en Bodoni Moda italic :
       .hero-title · .hero-garage .hero-title · .builder-step-title ·
       .auction-detail-time
     Ce sont précisément des éléments qui doivent DOMINER visuellement.
     Le saut 36→55 (×1.52, proche φ) est cohérent avec leur rôle et
     homogène (les 4 grandissent ensemble). C'est l'intention même de
     la doctrine √φ : les titres respirent.
  4. --t-md/lg/xl — deltas modérés (+4 à +6px), montée régulière de
     l'échelle. 20 + 12 + 3 usages, tous des font-size de hiérarchie
     intermédiaire.

  Réaligner les tokens = 39 usages corrigés d'un patch propre, sans
  toucher un seul sélecteur.

Scope          : 1 patch sur index.html
  - CSS-1 : les 4 lignes --t-md / --t-lg / --t-xl / --t-2xl dans :root.
            Anchor 2-bornes : --t-base (haute) + les 4 lignes +
            ligne blanche + commentaire Lot 28 (basse).

Note sécurité :
  - CSS-1 : anchor 2-bornes — "--t-base:15px;" (borne haute) et la
    ligne blanche + "/* ──...──" du bloc Fibonacci Lot 28 (borne basse).
    Les 4 lignes du milieu changent → anchor rompue.
  - Seules 4 valeurs de tokens modifiées. Aucun sélecteur touché.
    --t-xs/sm/base non touchés (déjà conformes). CSS valide.
  - Garde-fou v1.1 : anchor vérifiée non-1-borne.
  - Idempotence : marker = "Lot 32 — réaligné sur √φ".

Hors scope :
  - --t-xs/sm/base : déjà conformes
  - font-size en dur dispersées dans le fichier : pas l'objet de ce lot
  - retrait des tokens --s-5/6/7/8 sans usage (étape finale séparée)

Prérequis : Lot 31 (Phase α) appliqué
Usage     :
    python3 apply_realign_typo_lot32.py path/to/index.html
    python3 apply_realign_typo_lot32.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — réaligne --t-md/lg/xl/2xl sur l'échelle √φ
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : --t-base (borne haute, non modifié) + les 4 lignes
# à changer + la ligne blanche + le début du commentaire Lot 28 du bloc
# Fibonacci (borne basse). Les 4 lignes du milieu changent.

CSS1_ANCHOR = """  --t-base:15px;
  --t-md:17px;
  --t-lg:22px;
  --t-xl:28px;
  --t-2xl:36px;

  --s-1:4px;"""

CSS1_REPLACEMENT = """  --t-base:15px;
  --t-md:21px;   /* Lot 32 — réaligné sur √φ (était 17px) */
  --t-lg:28px;   /* Lot 32 — réaligné sur √φ (était 22px) */
  --t-xl:34px;   /* Lot 32 — réaligné sur √φ (était 28px) */
  --t-2xl:55px;  /* Lot 32 — réaligné sur √φ, palier φ (était 36px) */

  --s-1:4px;"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 32 (Phase α) — Réalignement de l'échelle typo sur racine-phi",
    requires=[
        # Marker réel présent dans le fichier après le Lot 31.
        "Lot 31 */",
    ],
    patches=[
        Patch(
            name="CSS-1 · --t-md/lg/xl/2xl réalignés sur l'échelle √φ",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Lot 32 — réaligné sur √φ",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
