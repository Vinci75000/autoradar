#!/usr/bin/env python3
"""
CARNET · Lot 38 — Charte v9 : migration vert-vivant-clair

Source        : audit complet des couleurs. Le Lot 36 a posé la variable
                --vert-vivant-clair:#9FE1CB (version claire du vert de
                service, pour fonds sombres). Ce lot migre les 11 usages
                encore codés en dur vers la variable.

  #9FE1CB est le vert "positif" des overlays démo (Co-pilote, Track Day,
  Gumball, Garage co-owned). Il vit sur fond sombre (var(--encre)) — d'où
  la nécessité d'une version claire : --vert-vivant (#257226) y serait
  illisible.

Note encodage/anchors :
  Première version : 9 anchors NOT FOUND — j'avais supposé une
  indentation 4 espaces, le fichier est en 2 (vérifié au od -c).
  Le fichier mélange aussi deux écritures : "color:#9FE1CB;" (sans
  espace, zone Garage/Co-pilote) et "color: #9FE1CB;" (avec espace,
  zone overlays génériques refondus au Lot 13b). Chaque anchor respecte
  l'écriture ET l'indentation exactes de sa zone.

Scope          : 11 patches sur index.html — un par usage.

Note sécurité :
  - Anchors 2-bornes : chaque patch encadre la ligne color par 1 ligne
    réelle avant + 1 après. Indentation 2 espaces.
  - Migration pure : #9FE1CB → var(--vert-vivant-clair), même couleur.
    Zéro changement visuel.
  - 2 usages compacts (.copilote-tsd-col-value.is-positive,
    .carnet-overlay-header-right .is-positive) : anchor = ligne entière.
  - Garde-fou v1.1 : 11 anchors vérifiées non-1-borne.
  - Idempotence : marker = var(--vert-vivant-clair) dans le contexte.

Hors scope :
  - rien — dernier lot de migration de la charte v9. Après ce lot :
    0 couleur sémantique en dur.

Prérequis : Lot 36 appliqué (--vert-vivant-clair posée)
Usage     :
    python3 apply_vert_vivant_clair_lot38.py path/to/index.html
    python3 apply_vert_vivant_clair_lot38.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# 11 patches — indentation 2 espaces. Zone Garage/Co-pilote sans espace
# après "color:", zone overlays génériques avec espace.
# ═══════════════════════════════════════════════════════════════════════

PATCHES = [
    Patch(
        name="CSS-1 · .garage-coowned-label (L8703)",
        anchor="""  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0 0 8px 0;""",
        replacement="""  letter-spacing:0.18em;
  color:var(--vert-vivant-clair); /* Lot 38 */
  text-transform:uppercase;
  margin:0 0 8px 0;""",
        idempotence_marker="""  color:var(--vert-vivant-clair); /* Lot 38 */
  text-transform:uppercase;
  margin:0 0 8px 0;""",
    ),
    Patch(
        name="CSS-2 · .garage-coowned-share (L8717)",
        anchor="""  font-size:10px;
  color:#9FE1CB;
  letter-spacing:0.04em;""",
        replacement="""  font-size:10px;
  color:var(--vert-vivant-clair); /* Lot 38 */
  letter-spacing:0.04em;""",
        idempotence_marker="""  font-size:10px;
  color:var(--vert-vivant-clair); /* Lot 38 */""",
    ),
    Patch(
        name="CSS-3 · .garage-coowned badge (L8734)",
        anchor="""  font-size:9px;
  color:#9FE1CB;
  padding:4px 8px;""",
        replacement="""  font-size:9px;
  color:var(--vert-vivant-clair); /* Lot 38 */
  padding:4px 8px;""",
        idempotence_marker="""  color:var(--vert-vivant-clair); /* Lot 38 */
  padding:4px 8px;""",
    ),
    Patch(
        name="CSS-4 · .copilote-tsd-label (L9027)",
        anchor=""".copilote-tsd-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;""",
        replacement=""".copilote-tsd-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--vert-vivant-clair); /* Lot 38 */""",
        idempotence_marker=""".copilote-tsd-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--vert-vivant-clair); /* Lot 38 */""",
    ),
    Patch(
        name="CSS-5 · .copilote-tsd sub-label (L9033)",
        anchor=""".copilote-tsd-target{
  font-family:var(--mono);
  font-size:9px;
  color:#9FE1CB;""",
        replacement=""".copilote-tsd-target{
  font-family:var(--mono);
  font-size:9px;
  color:var(--vert-vivant-clair); /* Lot 38 */""",
        idempotence_marker=""".copilote-tsd-target{
  font-family:var(--mono);
  font-size:9px;
  color:var(--vert-vivant-clair); /* Lot 38 */""",
    ),
    Patch(
        name="CSS-6 · .copilote-tsd-col-value.is-positive (L9058, compacte)",
        anchor=""".copilote-tsd-col-value.is-positive{ color:#9FE1CB; }""",
        replacement=""".copilote-tsd-col-value.is-positive{ color:var(--vert-vivant-clair); } /* Lot 38 */""",
        idempotence_marker=""".copilote-tsd-col-value.is-positive{ color:var(--vert-vivant-clair); }""",
    ),
    Patch(
        name="CSS-7 · .carnet-overlay-header-right .is-positive (L9213, compacte)",
        anchor=""".carnet-overlay-header-right .is-positive{ color:#9FE1CB; }""",
        replacement=""".carnet-overlay-header-right .is-positive{ color:var(--vert-vivant-clair); } /* Lot 38 */""",
        idempotence_marker=""".carnet-overlay-header-right .is-positive{ color:var(--vert-vivant-clair); }""",
    ),
    Patch(
        name="CSS-8 · Track Day / Gumball label (L9638)",
        anchor="""  font-size:11px;
  color:#9FE1CB;
  letter-spacing:0.03em;
  margin:0;""",
        replacement="""  font-size:11px;
  color:var(--vert-vivant-clair); /* Lot 38 */
  letter-spacing:0.03em;
  margin:0;""",
        idempotence_marker="""  color:var(--vert-vivant-clair); /* Lot 38 */
  letter-spacing:0.03em;
  margin:0;""",
    ),
    Patch(
        name="CSS-9 · .carnet-overlay-header-eyebrow (L9876, avec espace)",
        anchor="""  letter-spacing: 0.18em;
  color: #9FE1CB;
  text-transform: uppercase;
  margin: 0;""",
        replacement="""  letter-spacing: 0.18em;
  color: var(--vert-vivant-clair); /* Lot 38 */
  text-transform: uppercase;
  margin: 0;""",
        idempotence_marker="""  color: var(--vert-vivant-clair); /* Lot 38 */
  text-transform: uppercase;
  margin: 0;""",
    ),
    Patch(
        name="CSS-10 · .carnet-overlay-header-live (L9897, avec espace)",
        anchor="""  font-size: 9px;
  color: #9FE1CB;
  letter-spacing: 0.04em;
  margin-top: 2px;""",
        replacement="""  font-size: 9px;
  color: var(--vert-vivant-clair); /* Lot 38 */
  letter-spacing: 0.04em;
  margin-top: 2px;""",
        idempotence_marker="""  color: var(--vert-vivant-clair); /* Lot 38 */
  letter-spacing: 0.04em;
  margin-top: 2px;""",
    ),
    Patch(
        name="CSS-11 · overlay eyebrow variante (L10101, avec espace)",
        anchor=""".kpi-card.is-hero .kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: #9FE1CB;""",
        replacement=""".kpi-card.is-hero .kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--vert-vivant-clair); /* Lot 38 */""",
        idempotence_marker=""".kpi-card.is-hero .kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--vert-vivant-clair); /* Lot 38 */""",
    ),
]


PATCHSET = PatchSet(
    name="Lot 38 — Charte v9 : migration vert-vivant-clair",
    requires=[
        "--vert-vivant-clair",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
