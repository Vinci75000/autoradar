#!/usr/bin/env python3
"""
CARNET · Lot 40 — Hygiène couleur : gris en dur → variables

Source        : audit final post-charte v9. Les couleurs sémantiques et
                de catégorie sont toutes en variables (Lots 35-39). Mais
                l'audit a révélé une dette d'HYGIÈNE : des couleurs qui
                ONT DÉJÀ leur variable, écrites en dur par paresse.

  Ce lot traite les gris :
    #D5D0C4  →  var(--gris-line)   13 usages CSS
    #6B655B  →  var(--gris)         9 usages CSS

  Tous dans la zone des overlays démo (Co-pilote, Track Day, Gumball,
  L9100-9910) — des borders, backgrounds et colors qui auraient dû
  pointer vers --gris-line / --gris dès le départ.

Pourquoi un remplacement ciblé (pas des Patch() anchrés un par un) :
  Ces usages sont des lignes courtes et RÉPÉTÉES à l'identique
  (`  background:#D5D0C4;` apparaît 3×, `  color:#6B655B;` 4×…).
  Des anchors une-par-une seraient ingérables — impossible de les
  rendre uniques sans embarquer un gros contexte arbitraire.

  Le bon outil ici : un remplacement de chaîne EXACTE, parce que la
  transformation est identique partout — #D5D0C4 devient TOUJOURS
  var(--gris-line), quel que soit le contexte (background, border,
  color…). Aucune décision contextuelle. La couleur ne change pas.

  Sécurité du remplacement global :
  1. On ne touche QUE les occurrences hors :root. La ligne de
     définition `--gris-line:#D5D0C4;` (L21) et `--gris:#6B655B;` (L19)
     sont préservées explicitement.
  2. #6B655B a 1 usage dans le JS (L21620, une valeur de donnée dans
     un objet avatar). Le JS est EXCLU de ce lot — il sera traité au
     Lot 41 (migration des hex JS), parce que c'est un type de patch
     différent (valeur de donnée, pas déclaration CSS).
  3. Vérification stricte des comptes avant/après : on sait exactement
     combien d'occurrences doivent disparaître. Si le compte ne colle
     pas, le script échoue sans écrire.
  4. Idempotence par comptage : si 0 occurrence en dur à migrer, skip.

Scope          : remplacement ciblé sur index.html.
  - #D5D0C4 hors :root : 13 → var(--gris-line)
  - #6B655B hors :root ET hors JS : 9 → var(--gris)

Note sécurité :
  - Préservation explicite des 2 lignes de définition :root.
  - Préservation explicite de la ligne JS L21620.
  - Comptage strict : échec si le nombre d'occurrences migrées ne
    correspond pas à l'attendu.
  - Backup automatique avant écriture.
  - Idempotence : re-run → 0 occurrence à migrer → skip propre.

Hors scope :
  - #6B655B dans le JS (L21620) : Lot 41
  - Les autres hex JS (avatars #1A1A18, #1F4D2F, #E85A1F, #BA7517) : Lot 41
  - #FAFAF7, #FFFDF7, les quasi-noirs : Lot 42 (mini-décision de charte)

Prérequis : Lot 39 appliqué
Usage     :
    python3 apply_gris_en_dur_lot40.py path/to/index.html
    python3 apply_gris_en_dur_lot40.py path/to/index.html --dry-run
"""

import sys
import shutil
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

# Les définitions :root à NE PAS toucher (préservées telles quelles).
ROOT_DEFS = [
    "--gris-line:#D5D0C4;",
    "--gris:#6B655B;",
]

# La ligne JS à NE PAS toucher (valeur de donnée, traitée au Lot 41).
JS_LINE_PRESERVE = "{ initial: '+3', color: '#6B655B', isMore: true }"

# Les migrations : (hex en dur, variable cible, compte CSS attendu)
MIGRATIONS = [
    ("#D5D0C4", "var(--gris-line)", 13),
    ("#6B655B", "var(--gris)", 9),
]


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 1:
        print("Usage: python3 apply_gris_en_dur_lot40.py <index.html> [--dry-run]")
        return 1
    path = Path(paths[0])
    if not path.exists():
        print(f"  ✗ fichier introuvable : {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    original = text

    print(f"\n► Lot 40 — Hygiène couleur : gris en dur → variables")
    print(f"  Fichier : {path.name}")

    # ── Idempotence : déjà migré ? ───────────────────────────────────
    # On compte les hex en dur hors :root et hors ligne JS.
    def count_in_dur(hex_code):
        n = 0
        for line in text.splitlines():
            if hex_code not in line:
                continue
            if any(rd in line for rd in ROOT_DEFS):
                continue
            if JS_LINE_PRESERVE in line:
                continue
            n += line.count(hex_code)
        return n

    counts = {hex_code: count_in_dur(hex_code) for hex_code, _, _ in MIGRATIONS}
    total_to_migrate = sum(counts.values())

    if total_to_migrate == 0:
        print(f"  ▸ 0 occurrence en dur à migrer — déjà appliqué (skip)")
        return 0

    # ── Vérification des comptes attendus ────────────────────────────
    errors = []
    for hex_code, var, expected in MIGRATIONS:
        actual = counts[hex_code]
        if actual != expected:
            errors.append(
                f"  ✗ {hex_code} : {actual} occurrence(s) trouvée(s), "
                f"{expected} attendue(s) — divergence, arrêt sans écriture"
            )
    if errors:
        print("\n".join(errors))
        print(f"  → vérifier le fichier source ou les prérequis")
        return 1

    # ── Application — ligne par ligne, en préservant les exclusions ──
    new_lines = []
    migrated = {hex_code: 0 for hex_code, _, _ in MIGRATIONS}
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        # Préserver les définitions :root et la ligne JS.
        if any(rd in stripped for rd in ROOT_DEFS) or JS_LINE_PRESERVE in stripped:
            new_lines.append(line)
            continue
        # Sinon, appliquer les migrations.
        for hex_code, var, _ in MIGRATIONS:
            if hex_code in line:
                migrated[hex_code] += line.count(hex_code)
                line = line.replace(hex_code, var)
        new_lines.append(line)

    text = "".join(new_lines)

    # ── Rapport ──────────────────────────────────────────────────────
    for hex_code, var, _ in MIGRATIONS:
        print(f"  ✓ {hex_code} → {var} : {migrated[hex_code]} usage(s) migré(s)")

    delta = len(text) - len(original)
    print(f"  ▸ Final  : {len(text):,} chars ({delta:+d})")

    if dry_run:
        print(f"  (dry-run, fichier non modifié)")
        return 0

    # ── Backup + écriture ────────────────────────────────────────────
    backup = path.with_name(path.name + ".before_lot_40_gris_en_dur")
    shutil.copy2(path, backup)
    path.write_text(text, encoding="utf-8")
    print(f"  ▸ Backup : {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
