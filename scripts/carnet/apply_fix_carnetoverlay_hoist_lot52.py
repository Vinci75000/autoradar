#!/usr/bin/env python3
"""
CARNET · Lot 52 — FIX BLOQUANT : hoist de la factory CarnetOverlay

Symptôme      : les 4 boutons de la barre de navigation (ANNONCES /
                ENCHÈRES / GARAGE / À L'AFFÛT) ne répondent plus au
                clic. La barre s'affiche normalement mais est inerte.
                En réalité : TOUTE l'app est morte au clic.

Diagnostic    : test DOM réel (Playwright + elementFromPoint) — les
                clics ATTEIGNENT bien les boutons, aucun overlay ne
                les couvre. Le vrai coupable est une exception JS au
                chargement :

                    CarnetOverlay is not defined

                window.CarnetOverlay (la factory d'overlays, bloc
                "Lot 13 Phase α") est définie TARD dans le script
                (~offset 894954). Mais elle est UTILISÉE trois fois
                AVANT, en code top-level qui s'exécute au chargement :
                  - window.CARNET_COPILOTE_DEMO = CarnetOverlay.create(...)  (~874372)
                  - window.CARNET_TRACKDAY_DEMO = CarnetOverlay.create(...)  (~880xxx)
                  - window.CARNET_GUMBALL_DEMO  = CarnetOverlay.create(...)  (~886xxx)

                `window.CarnetOverlay = {...}` est une AFFECTATION à
                l'exécution — pas une déclaration hoistée. Au moment
                où la 1re ligne d'usage s'exécute, CarnetOverlay
                n'existe pas encore → ReferenceError non capturée →
                l'exécution du <script> s'ARRÊTE NET à cet endroit.
                Tout ce qui suit ne tourne jamais : les définitions
                suivantes, le boot, et surtout
                `document.addEventListener('click', handleClick)`.
                Sans ce addEventListener, la délégation de clic n'est
                jamais branchée → aucun [data-action] ne réagit, dans
                toute l'app.

Le fix         : déplacer le bloc factory CarnetOverlay AVANT son
                premier usage. C'est un bloc autonome (un objet avec
                deux méthodes open/close, fermetures lexicales pures)
                — il ne dépend de rien d'autre du script, donc le
                remonter est sans effet de bord. Une fois défini en
                amont, les 3 `CarnetOverlay.create(...)` trouvent leur
                référence, l'exception disparaît, le script s'exécute
                jusqu'au bout, handleClick se branche, la barre (et
                tout le reste) revit.

Scope          : 2 patches sur index.html — un DÉPLACEMENT.
  P1 : SUPPRIME le bloc factory de sa position actuelle. Anchor =
       le bloc factory complet + la ligne de section qui le suit
       (`// ─── /Lot 13 ... ─`). Replacement = juste la ligne de
       section (le bloc disparaît, le repère de section reste — la
       structure de commentaires du fichier reste cohérente).
  P2 : RÉINSÈRE le bloc factory juste avant son premier usage —
       avant le commentaire `// API démo accessible via console —
       Migré Lot 13b-1 ...` qui précède
       `window.CARNET_COPILOTE_DEMO = CarnetOverlay.create(...)`.

  Le bloc déplacé est rigoureusement IDENTIQUE (extrait à l'octet du
  fichier) — aucun caractère modifié, juste la position.

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1.
    P1 : borne haute = début du bloc factory (commentaire Lot 13),
         borne basse = la ligne `// ─── /Lot 13 ... ─` + ce qui suit.
    P2 : borne haute = la ligne `}` + `\\n` qui précède le commentaire
         d'usage, borne basse = le commentaire `// API démo ...` +
         la ligne `window.CARNET_COPILOTE_DEMO`.
  - ORDRE des patches : P1 (suppression) AVANT P2 (réinsertion).
    P1 retire le bloc ; P2 le repose plus haut. Les deux anchors
    sont disjoints (P1 vers offset ~895k, P2 vers offset ~874k) et
    P2 n'est PAS affecté par P1 (P1 agit en aval de P2). Mais par
    prudence l'ordre logique reste suppression puis insertion.
  - Idempotence : après application, le bloc factory n'existe plus
    qu'à UN endroit (le nouveau, en amont). Marqueur P1 = absence du
    bloc à l'ancienne place / présence de la ligne de section seule.
    Marqueur P2 = le bloc factory juste avant le commentaire d'usage.
  - Le résultat est vérifié par re-test Playwright : 0 pageerror,
    elementFromPoint OK, et un clic simulé sur chaque onglet doit
    changer State.activeTab.

Prérequis : aucun
Usage     :
    python3 apply_fix_carnetoverlay_hoist_lot52.py path/to/index.html
    python3 apply_fix_carnetoverlay_hoist_lot52.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# Le bloc factory, extrait À L'OCTET du fichier. Fourni avec le script
# dans _factory_block.txt — fichier d'appoint OBLIGATOIRE (le contenu
# doit être identique au byte près à ce qui est dans index.html ;
# un fallback codé en dur risquerait de désynchroniser sur les
# caractères Unicode — mieux vaut échouer franchement).
_fb_path = Path(__file__).with_name("_factory_block.txt")
if not _fb_path.exists():
    sys.stderr.write(
        "ERREUR : _factory_block.txt manquant.\n"
        "Ce fichier d'appoint est livré AVEC le script (même dossier).\n"
    )
    sys.exit(1)
FACTORY_BLOCK = _fb_path.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════════════
# P1 — SUPPRIME le bloc factory de sa position actuelle.
# Anchor 2-bornes : le bloc factory + la ligne de section qui le suit.
# Replacement : juste la ligne de section (le bloc s'évapore).
# ═══════════════════════════════════════════════════════════════════════

SECTION_CLOSE = "\n// \u2500\u2500\u2500 /Lot 13 (Phase \u03b1 refactor) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"

P1_ANCHOR = FACTORY_BLOCK + SECTION_CLOSE
P1_REPLACEMENT = "// \u2500\u2500\u2500 Lot 13 (Phase \u03b1 refactor) \u2014 CarnetOverlay factory : d\u00e9plac\u00e9e en amont (Lot 52 fix hoist) \u2500\u2500\u2500" + SECTION_CLOSE


# ═══════════════════════════════════════════════════════════════════════
# P2 — RÉINSÈRE le bloc factory avant son premier usage.
# Anchor 2-bornes : la ligne `}` + saut qui précède le commentaire
# d'usage, + le commentaire d'usage + la ligne CARNET_COPILOTE_DEMO.
# ═══════════════════════════════════════════════════════════════════════

USAGE_ANCHOR = "// API d\u00e9mo accessible via console \u2014 Migr\u00e9 Lot 13b-1 vers CarnetOverlay factory\nwindow.CARNET_COPILOTE_DEMO = CarnetOverlay.create('carnet-copilote-overlay', renderCopiloteOverlay);"

# P2_ANCHOR : extrait À L'OCTET du fichier. Fourni dans _p2_anchor.txt
# — fichier d'appoint OBLIGATOIRE (même raison que _factory_block.txt :
# le `\\u26a0` du template JS et les caractères Unicode rendent un
# fallback en dur fragile ; on préfère échouer franchement).
_p2_path = Path(__file__).with_name("_p2_anchor.txt")
if not _p2_path.exists():
    sys.stderr.write(
        "ERREUR : _p2_anchor.txt manquant.\n"
        "Ce fichier d'appoint est livré AVEC le script (même dossier).\n"
    )
    sys.exit(1)
P2_ANCHOR = _p2_path.read_text(encoding="utf-8")

# Le replacement : on réinsère la factory juste après la fin de
# renderCopiloteOverlay (après `}\n\n`) et AVANT le commentaire d'usage.
# On découpe l'anchor sur le commentaire d'usage pour insérer au bon
# endroit.
_split_at = P2_ANCHOR.find(USAGE_ANCHOR)
assert _split_at > 0, "USAGE_ANCHOR introuvable dans P2_ANCHOR"
P2_HIGH = P2_ANCHOR[:_split_at]      # fin de renderCopiloteOverlay + `}\n\n`
P2_LOW = P2_ANCHOR[_split_at:]       # le commentaire d'usage + la ligne CARNET_COPILOTE_DEMO
P2_REPLACEMENT = P2_HIGH + FACTORY_BLOCK + "\n\n" + P2_LOW


PATCHES = [
    Patch(
        name="P1 \u00b7 supprime la factory CarnetOverlay de sa position actuelle (~895k)",
        anchor=P1_ANCHOR,
        replacement=P1_REPLACEMENT,
        idempotence_marker="CarnetOverlay factory : d\u00e9plac\u00e9e en amont (Lot 52 fix hoist)",
    ),
    Patch(
        name="P2 \u00b7 r\u00e9ins\u00e8re la factory CarnetOverlay avant son 1er usage (~874k)",
        anchor=P2_ANCHOR,
        replacement=P2_REPLACEMENT,
        # Marqueur unique au patch : la factory IMM\u00c9DIATEMENT suivie du
        # commentaire d'usage \u2014 cette adjacence n'existe qu'apr\u00e8s P2.
        idempotence_marker="    };\n  }\n};\n\n// API d\u00e9mo accessible via console \u2014 Migr\u00e9 Lot 13b-1 vers CarnetOverlay factory",
    ),
]


PATCHSET = PatchSet(
    name="Lot 52 \u2014 FIX BLOQUANT : hoist factory CarnetOverlay (TabBar morte au clic)",
    requires=[
        "window.CarnetOverlay = {",
        "window.CARNET_COPILOTE_DEMO = CarnetOverlay.create",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
