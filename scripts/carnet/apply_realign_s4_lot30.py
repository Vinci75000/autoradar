#!/usr/bin/env python3
"""
CARNET · Lot 30 (Phase α) — Réalignement du token --s-4 sur Fibonacci

Source        : audit A, étape A-iii. Suite du Lot 29 (--s-3 réaligné
                12→13px). Ce lot fait converger --s-4.

  Plan global de migration (paliers de risque croissant) :
    Lot 29 ✓ — --s-3 : 12→13px, delta +1px        (réalignement global)
    Lot 30   — --s-4 : 16→21px, delta +5px         ← CE LOT
    Lot 31   — --s-5/6/7 : deltas +14..+57px       (sélecteur par sélecteur)

Ce lot — pourquoi le réalignement global du token est sûr, vérifié :
  --s-4 est utilisé 47×, sur des sélecteurs structurels (.main, .section,
  .hero, .topbar, .sheet-*, .watched-rail, carrousels…). Le passer de
  16px à 21px = la vraie 4e valeur de Fibonacci, delta +5px.

  Vérifications faites AVANT de décider — c'est un delta plus visible
  que le Lot 29, donc audit plus poussé :

  1. calc() — 5 occurrences, TOUTES vérifiées :
       · 4× `margin:0 calc(var(--s-4) * -1)` — des marges négatives de
         "bleed" (carrousel/rail qui déborde du padding parent pour
         aller bord à bord). Sur CHAQUE sélecteur concerné, le padding
         horizontal du même bloc (ou de son enfant scroll-snap) utilise
         AUSSI var(--s-4). Donc margin négatif et padding bougent
         ENSEMBLE → le bleed reste exactement aligné après 16→21.
         Vérifié sur : .watched-rail, .encheres-filter-bar,
         .onboarding-track (+ .onboarding-panel enfant), .presets-carrousel.
       · 1× `padding:calc(var(--s-4) - 1px)` — ajustement relatif -1px,
         reste cohérent (20px au lieu de 15px).
  2. @media — aucune redéfinition de --s-4. Une seule source de vérité.
  3. Sections refondues — --s-4 est utilisé par des sélecteurs de
     sections déjà refondues φ (.sheet-*, .hero, .kpi-strip). Le +5px
     y va dans le SENS de la doctrine (21 est le vrai Fibonacci) — il
     aligne, il ne casse pas. Le bleed étant auto-cohérent, aucune
     mise en page ne se désaligne.

  Réaligner le token = 47 usages corrigés d'un patch propre, sans
  toucher un seul sélecteur. Le renommage final --s-* → --fib-* viendra
  à la toute fin, quand tous les tokens linéaires auront convergé.

Scope          : 1 patch sur index.html
  - CSS-1 : --s-4:16px → --s-4:21px dans :root. Une seule ligne.
            Anchor 2-bornes : --s-3 (haute) + --s-4 + --s-5 (basse).

Note sécurité :
  - CSS-1 : anchor 2-bornes — la ligne --s-3 (déjà au format Lot 29 avec
    son commentaire) + --s-4 + --s-5. La ligne du milieu change → anchor
    rompue.
  - Un seul token, valeur uniquement. Aucun sélecteur touché. CSS valide.
  - Garde-fou v1.1 : anchor vérifiée non-1-borne.
  - Idempotence : marker = "Lot 30 — réaligné sur Fibonacci".

Hors scope :
  - --s-5/6/7 (Lot 31, sélecteur par sélecteur — deltas trop gros pour
    un alias global)
  - Le renommage --s-* → --fib-* (étape finale)

Prérequis : Lot 29 (Phase α) appliqué
Usage     :
    python3 apply_realign_s4_lot30.py path/to/index.html
    python3 apply_realign_s4_lot30.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — réaligne --s-4 de 16px à 21px (vraie valeur Fibonacci)
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : --s-3 (avec son commentaire Lot 29, borne haute) +
# --s-4 (la ligne qui change) + --s-5 (borne basse).

CSS1_ANCHOR = """  --s-3:13px;  /* Lot 29 — réaligné sur Fibonacci (était 12px) */
  --s-4:16px;
  --s-5:20px;"""

CSS1_REPLACEMENT = """  --s-3:13px;  /* Lot 29 — réaligné sur Fibonacci (était 12px) */
  --s-4:21px;  /* Lot 30 — réaligné sur Fibonacci (était 16px) */
  --s-5:20px;"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 30 (Phase α) — Réalignement du token --s-4 sur Fibonacci",
    requires=[
        # Marker réel présent dans le fichier après le Lot 29.
        "Lot 29 — réaligné sur Fibonacci",
    ],
    patches=[
        Patch(
            name="CSS-1 · --s-4 : 16px → 21px (vraie valeur Fibonacci)",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Lot 30 — réaligné sur Fibonacci",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
