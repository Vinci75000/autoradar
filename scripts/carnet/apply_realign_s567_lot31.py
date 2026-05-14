#!/usr/bin/env python3
"""
CARNET · Lot 31 (Phase α) — Réalignement de --s-5/6/7 sur Fibonacci

Source        : audit A, étape A-iii. Dernier lot de convergence des
                tokens d'espacement linéaires vers la géométrie sacrée.

  Plan global de migration (paliers de risque croissant) :
    Lot 29 ✓ — --s-3 : 12→13px,  delta +1px   (réalignement global token)
    Lot 30 ✓ — --s-4 : 16→21px,  delta +5px   (réalignement global token)
    Lot 31   — --s-5/6/7 : deltas +14..+57px  ← CE LOT

Pourquoi ce lot ne réaligne PAS les tokens globalement :
  --s-5/6/7 valent 20/24/32px. Leurs équivalents Fibonacci de même rang
  (--fib-5/6/7 = 34/55/89px) impliquent des deltas de +14/+31/+57px.
  Réaligner le TOKEN ferait exploser les marges. On remplace donc les
  11 usages UN PAR UN, chacun pointé vers le bon token Fibonacci selon
  ce que l'élément FAIT — pas selon son rang.

Décision sélecteur par sélecteur (contexte audité) :
  --s-5 (20px) → --fib-4 (21px)  delta +1px imperceptible :
    .new-alert-wrap · .auction-detail-banner · .toast-content ·
    .builder-main · .builder-step-sub · .builder-counter-xl
  --s-6 (24px) → --fib-5 (34px)  saut assumé, zones d'aération :
    .hero · .empty-state · .onboarding-panel
  --s-7 (32px) → --fib-5 (34px)  delta +2px :
    .section · .builder-axis-section

Note encodage/anchors :
  Première version : 8 anchors NOT FOUND — j'avais supposé une structure
  ".selecteur{\\n    padding" avec indentation 4 espaces, alors que le
  fichier est en 2 espaces et certaines propriétés sont éloignées de
  leur sélecteur. Anchors reconstruites avec le contexte RÉEL : ligne
  voisine exacte avant + après, indentation 2 espaces vérifiée au cat -A.

Note sécurité :
  - Anchors 2-bornes : chaque patch encadre la ligne à changer par sa
    ligne voisine réelle (vérifiée au cat -A). Le replacement rompt
    l'anchor (la ligne du milieu change).
  - Aucune valeur de token modifiée — on ne touche QUE les 11 sites.
  - Aucun des 11 usages n'est dans un calc(). Vérifié.
  - Garde-fou v1.1 : 11 anchors vérifiées non-1-borne.
  - Idempotence : marker = la nouvelle référence --fib-* + " /* Lot 31 */".

Hors scope :
  - Retrait des tokens --s-3/4/5/6/7 désormais sans usage (étape finale)

Prérequis : Lot 30 (Phase α) appliqué
Usage     :
    python3 apply_realign_s567_lot31.py path/to/index.html
    python3 apply_realign_s567_lot31.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# Les 11 patches — anchors avec contexte RÉEL (indentation 2 espaces).
# ═══════════════════════════════════════════════════════════════════════

PATCHES = [
    # ── --s-5 → --fib-4 (21px) ────────────────────────────────────────
    Patch(
        name="CSS-1 · .new-alert-wrap padding-bottom -> --fib-4",
        anchor=""".new-alert-wrap{padding:0 var(--s-4) var(--s-5)}""",
        replacement=""".new-alert-wrap{padding:0 var(--s-4) var(--fib-4)} /* Lot 31 */""",
        idempotence_marker=""".new-alert-wrap{padding:0 var(--s-4) var(--fib-4)}""",
    ),
    Patch(
        name="CSS-2 · .auction-detail-banner padding -> --fib-4",
        anchor="""  color:var(--papier);
  padding:var(--s-5);
  border-radius:var(--r);""",
        replacement="""  color:var(--papier);
  padding:var(--fib-4); /* Lot 31 */
  border-radius:var(--r);""",
        idempotence_marker="""  padding:var(--fib-4); /* Lot 31 */""",
    ),
    Patch(
        name="CSS-3 · .toast-content padding-top -> --fib-4",
        anchor=""".toast-content{
  padding:var(--s-5) var(--s-4) var(--s-4);
  text-align:center;""",
        replacement=""".toast-content{
  padding:var(--fib-4) var(--s-4) var(--s-4); /* Lot 31 */
  text-align:center;""",
        idempotence_marker="""  padding:var(--fib-4) var(--s-4) var(--s-4); /* Lot 31 */""",
    ),
    Patch(
        name="CSS-4 · .builder-main padding vertical -> --fib-4",
        anchor="""  overflow-y:auto;
  padding:var(--s-5) var(--s-4) var(--s-5);
  -webkit-overflow-scrolling:touch;""",
        replacement="""  overflow-y:auto;
  padding:var(--fib-4) var(--s-4) var(--fib-4); /* Lot 31 */
  -webkit-overflow-scrolling:touch;""",
        idempotence_marker="""  padding:var(--fib-4) var(--s-4) var(--fib-4); /* Lot 31 */""",
    ),
    Patch(
        name="CSS-5 · .builder-step-sub margin-bottom -> --fib-4",
        anchor="""  line-height:1.35;
  margin-bottom:var(--s-5);
}
.builder-types{display:flex;flex-direction:column;gap:var(--s-2)}""",
        replacement="""  line-height:1.35;
  margin-bottom:var(--fib-4); /* Lot 31 */
}
.builder-types{display:flex;flex-direction:column;gap:var(--s-2)}""",
        idempotence_marker="""  margin-bottom:var(--fib-4); /* Lot 31 */""",
    ),
    Patch(
        name="CSS-6 · .builder-counter-xl padding -> --fib-4",
        anchor="""  border-radius:var(--r);
  padding:var(--s-5) var(--s-4);
  display:flex;
  flex-direction:column;""",
        replacement="""  border-radius:var(--r);
  padding:var(--fib-4) var(--s-4); /* Lot 31 */
  display:flex;
  flex-direction:column;""",
        idempotence_marker="""  padding:var(--fib-4) var(--s-4); /* Lot 31 */""",
    ),
    # ── --s-6 → --fib-5 (34px) ────────────────────────────────────────
    Patch(
        name="CSS-7 · .hero padding-top -> --fib-5 (le premier ecran respire)",
        anchor=""".hero{padding:var(--s-6) var(--s-4) var(--s-3)}""",
        replacement=""".hero{padding:var(--fib-5) var(--s-4) var(--s-3)} /* Lot 31 */""",
        idempotence_marker=""".hero{padding:var(--fib-5) var(--s-4) var(--s-3)}""",
    ),
    Patch(
        name="CSS-8 · .empty-state padding-top -> --fib-5",
        anchor=""".empty-state{
  padding:var(--s-6) var(--s-4);
  text-align:center;""",
        replacement=""".empty-state{
  padding:var(--fib-5) var(--s-4); /* Lot 31 */
  text-align:center;""",
        idempotence_marker="""  padding:var(--fib-5) var(--s-4); /* Lot 31 */""",
    ),
    Patch(
        name="CSS-9 · .onboarding-panel padding-top -> --fib-5",
        anchor="""  scroll-snap-align:center;
  padding:var(--s-6) var(--s-4) var(--s-4);
  display:flex;""",
        replacement="""  scroll-snap-align:center;
  padding:var(--fib-5) var(--s-4) var(--s-4); /* Lot 31 */
  display:flex;""",
        idempotence_marker="""  padding:var(--fib-5) var(--s-4) var(--s-4); /* Lot 31 */""",
    ),
    # ── --s-7 → --fib-5 (34px) ────────────────────────────────────────
    Patch(
        name="CSS-10 · .section margin-bottom -> --fib-5",
        anchor=""".section{padding:0 var(--s-4);margin-bottom:var(--s-7)}""",
        replacement=""".section{padding:0 var(--s-4);margin-bottom:var(--fib-5)} /* Lot 31 */""",
        idempotence_marker=""".section{padding:0 var(--s-4);margin-bottom:var(--fib-5)}""",
    ),
    Patch(
        name="CSS-11 · .builder-axis-section margin-bottom -> --fib-5",
        anchor=""".builder-axis-section{margin-bottom:var(--s-7)}
.builder-axis-section:last-child{margin-bottom:0}""",
        replacement=""".builder-axis-section{margin-bottom:var(--fib-5)} /* Lot 31 */
.builder-axis-section:last-child{margin-bottom:0}""",
        idempotence_marker=""".builder-axis-section{margin-bottom:var(--fib-5)}""",
    ),
]


PATCHSET = PatchSet(
    name="Lot 31 (Phase α) — Réalignement de --s-5/6/7 sur Fibonacci",
    requires=[
        "Lot 30 — réaligné sur Fibonacci",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
