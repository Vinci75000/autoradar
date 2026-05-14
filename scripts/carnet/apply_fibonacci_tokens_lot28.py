#!/usr/bin/env python3
"""
CARNET · Lot 28 (Phase α) — Tokens Fibonacci + échelle typo √φ dans :root

Source        : audit A — géométrie sacrée & nombre d'or.

  Constat de l'audit : 11 sections d'index.html ont déjà été refondues
  en φ/Fibonacci (v5.31, v5.39, v5.41, v5.43, v5.46, v5.50 + Lots 16-18 :
  Cards Garage/Affût, Sheets de détail, Hero+KPI, TabBar, CTA, Empty
  states, Listings, Onboarding). Elles utilisent aspect-ratio 1.618/1 et
  des espacements Fibonacci (8/13/21/34) — mais écrits EN DUR, parce que
  les tokens :root ne portaient pas les bonnes valeurs.

  Le socle :root n'a jamais suivi la doctrine. Les tokens d'espacement
  sont restés sur une échelle LINÉAIRE arithmétique :
      --s-3:12  --s-4:16  --s-5:20  --s-6:24  --s-7:32  --s-8:40
  là où la doctrine Carnet impose la suite de Fibonacci :
      --s-3:13  --s-4:21  --s-5:34  --s-6:55  --s-7:89  --s-8:144

  Conséquence : deux systèmes d'espacement coexistent. Les sections
  refondues écrivent Fibonacci en dur ; les sections non refondues
  (~129 usages de --s-3..7 : topbar, hero, section, builder) restent
  en linéaire. Migration inachevée.

Pourquoi ce lot ne TOUCHE PAS les tokens existants :
  --s-3 est utilisé 71×, --s-4 47×. Les passer brutalement de 12→13 et
  16→21 bougerait ~120 éléments d'un coup, dont beaucoup dans des
  sections déjà refondues en dur où le designer a fixé ses valeurs.
  On créerait des conflits partout. "Debug together, don't rewrite."

Stratégie (option A-ii validée) : PUREMENT ADDITIF.
  On ajoute À CÔTÉ des tokens actuels une nouvelle famille de tokens
  qui porte la VRAIE géométrie sacrée :
    - --fib-1..8  : suite de Fibonacci stricte (4 8 13 21 34 55 89 144)
    - --t-fib-1..8 : échelle typographique en steps √φ depuis base 15px
                     (11 13 15 21 28 34 55 89 — paliers majeurs = φ exact)
    - --phi, --phi-inv : le nombre d'or et son inverse, pour les ratios
                     (grilles 1.618fr 1fr, aspect-ratio, etc.)
  Rien d'existant ne bouge. Les sections déjà refondues continuent de
  marcher. Les FUTURES refontes (A-iii, section par section) utiliseront
  ces tokens propres au lieu d'écrire des valeurs en dur — ce qui était
  la cause de l'incohérence actuelle.

  Les tokens linéaires --s-* et --t-* restent en place : ils seront
  retirés section par section au fil des refontes A-iii, quand plus
  aucun sélecteur ne les utilisera. Pas avant.

Scope          : 1 patch sur index.html
  - CSS-1 : insère le bloc de tokens Fibonacci dans :root, entre le
            dernier token d'espacement linéaire (--s-8:40px) et le
            premier token de rayon (--r:2px). Anchor 2-bornes naturelle.

Note sécurité :
  - CSS-1 : anchor 2-bornes — "--s-8:40px;" + ligne blanche (borne haute)
    et "--r:2px;" (borne basse). L'insertion se fait entre les deux →
    anchor rompue, idempotence OK.
  - Purement additif : aucun token existant modifié, aucun sélecteur
    touché. CSS valide (déclarations de custom properties standard).
  - Garde-fou v1.1 : anchor vérifiée non-1-borne.
  - Idempotence : marker = le commentaire "Géométrie sacrée — tokens
    Fibonacci" qui n'existe qu'après application.

Hors scope (= les prochains lots A-iii) :
  - Refondre les sections restées linéaires (topbar, hero, section,
    builder) pour qu'elles utilisent --fib-* au lieu de --s-*
  - Retirer les tokens --s-* / --t-* une fois plus aucun usage
  - Migrer les valeurs Fibonacci écrites EN DUR vers les tokens --fib-*

Prérequis : Lot 27 (Phase α) appliqué
Usage     :
    python3 apply_fibonacci_tokens_lot28.py path/to/index.html
    python3 apply_fibonacci_tokens_lot28.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — bloc de tokens Fibonacci dans :root
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : le dernier token d'espacement linéaire + la ligne
# blanche (borne haute), et "--r:2px;" (borne basse). Le bloc Fibonacci
# s'insère entre les deux.

CSS1_ANCHOR = """  --s-7:32px;
  --s-8:40px;

  --r:2px;"""

CSS1_REPLACEMENT = """  --s-7:32px;
  --s-8:40px;

  /* ─────────────────────────────────────────────────────────────
     Géométrie sacrée — tokens Fibonacci + nombre d'or (Lot 28)
     La doctrine Carnet : aucun magic number. Les espacements suivent
     la suite de Fibonacci, l'échelle typo des steps √φ, les ratios
     le nombre d'or. Les tokens --s-* / --t-* linéaires ci-dessus
     restent le temps que les sections non encore refondues migrent
     (A-iii, section par section). Les NOUVELLES refontes utilisent
     les tokens ci-dessous — plus jamais de valeur en dur.
     ───────────────────────────────────────────────────────────── */

  /* Espacements — suite de Fibonacci stricte */
  --fib-1:4px;
  --fib-2:8px;
  --fib-3:13px;
  --fib-4:21px;
  --fib-5:34px;
  --fib-6:55px;
  --fib-7:89px;
  --fib-8:144px;

  /* Échelle typographique — steps √φ depuis base 15px.
     11 → 13 → 15 → 21 → 28 → 34 → 55 → 89.
     Les paliers majeurs (34→55, 55→89) sont exactement φ. */
  --t-fib-1:11px;
  --t-fib-2:13px;
  --t-fib-3:15px;
  --t-fib-4:21px;
  --t-fib-5:28px;
  --t-fib-6:34px;
  --t-fib-7:55px;
  --t-fib-8:89px;

  /* Nombre d'or — pour les ratios (grilles, aspect-ratio, proportions) */
  --phi:1.618;
  --phi-inv:0.618;

  --r:2px;"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 28 (Phase α) — Tokens Fibonacci + échelle typo phi dans root",
    requires=[
        # Marker réel présent dans le fichier après le Lot 27.
        "Lot 27 — openAuction : définition unique plus bas",
    ],
    patches=[
        Patch(
            name="CSS-1 · bloc tokens Fibonacci + typo √φ + ratios φ dans :root",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Géométrie sacrée — tokens Fibonacci",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
