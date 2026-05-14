#!/usr/bin/env python3
"""
CARNET · Lot N (Phase X) — [Brève description en une ligne]

Prérequis : Lot N-1 appliqué (vérifier les markers requis)
Cible     : path/to/index.html
Usage     :
    python3 apply_<feature>_lot<N>.py path/to/index.html
    python3 apply_<feature>_lot<N>.py path/to/index.html --dry-run

Auteur    : [nom]
Date      : YYYY-MM-DD
"""

import sys
from pathlib import Path

# Permettre l'import de carnet_patch_lib depuis le dossier courant
sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCHES
# ═══════════════════════════════════════════════════════════════════════

# ─── Patch 1 : [titre] ────────────────────────────────────────────────
#
# Quoi : [description du changement]
# Où   : [section du fichier, par ex. "fin de <style>", "avant renderXxx"]
# Pourquoi : [intention métier]

PATCH_1_ANCHOR = """<TEXTE-EXACT-PRÉSENT-DANS-INDEX-HTML-UNIQUE>"""

PATCH_1_REPLACEMENT = """<TEXTE-EXACT-PRÉSENT-DANS-INDEX-HTML-UNIQUE>
<NOUVEAU-CONTENU-AJOUTÉ-ICI>"""

PATCH_1_MARKER = """<TEXTE-NOUVEAU-PRÉSENT-DANS-REPLACEMENT-ABSENT-DANS-ANCHOR>"""


# ─── Patch 2 : [titre] ────────────────────────────────────────────────

# PATCH_2_ANCHOR = """..."""
# PATCH_2_REPLACEMENT = """..."""
# PATCH_2_MARKER = """..."""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot N (Phase X) — [feature description]",
    requires=[
        # Markers attendus dans le fichier comme prérequis. Optionnel.
        # Ex : "LOT 1.1 appliqué"
    ],
    patches=[
        Patch(
            name="[Patch 1 court titre]",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker=PATCH_1_MARKER,
        ),
        # Patch(
        #     name="[Patch 2 court titre]",
        #     anchor=PATCH_2_ANCHOR,
        #     replacement=PATCH_2_REPLACEMENT,
        #     idempotence_marker=PATCH_2_MARKER,
        # ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
