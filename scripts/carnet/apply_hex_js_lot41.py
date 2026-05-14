#!/usr/bin/env python3
"""
CARNET · Lot 41 — Hygiène couleur : hex JS → variables de charte

Source        : audit final post-charte v9. Suite du Lot 40 (gris CSS).
                Ce lot traite les hex codés en dur dans le JAVASCRIPT.

  Les hex JS sont des couleurs d'AVATARS — l'initiale + la couleur de
  fond de chaque membre dans les structures de données des modules
  Garage social, Co-pilote, Ledger, Tribu. Ils apparaissent :
    · comme valeur de donnée :  { initial: 'M', color: '#1A1A18' }
    · comme fallback de rendu : member.color || '#1A1A18'
  Dans les deux cas, la couleur finit interpolée dans un attribut
  style="background:${...}" — c'est donc du CSS au final, et
  var(--xxx) y fonctionne parfaitement.

  Décision (lecture A, validée) : ces couleurs ne sont pas des
  identités de personne arbitraires — ce sont les couleurs de la
  CHARTE réutilisées pour les avatars. Aucun hex étranger : les 5
  hex utilisés (#1A1A18, #1F4D2F, #E85A1F, #BA7517, #6B655B) sont
  EXACTEMENT les couleurs de marque. Les migrer vers les variables
  rend les avatars cohérents avec la palette — si la charte évolue,
  les avatars suivent.

  Mapping (recensé exhaustivement) :
    '#1A1A18' → 'var(--encre)'         8 occurrences (5 data + 3 fallback)
    '#1F4D2F' → 'var(--vert-anglais)'  6 occurrences
    '#E85A1F' → 'var(--orange-polo)'   4 occurrences
    '#BA7517' → 'var(--or)'            3 occurrences
    '#6B655B' → 'var(--gris)'          1 occurrence
  Total : 22 occurrences quotées.

Pourquoi un remplacement ciblé (même méthode que le Lot 40) :
  Transformation identique partout — '#1A1A18' devient TOUJOURS
  'var(--encre)', que ce soit une donnée ou un fallback. Aucune
  décision contextuelle. On remplace la chaîne quotée EXACTE
  ('#XXXXXX' avec ses apostrophes) pour ne toucher QUE le JS et
  jamais le CSS (où les hex ne sont pas quotés).

  Sécurité :
  1. On remplace '#XXXXXX' (avec quotes) — le CSS utilise #XXXXXX
     sans quotes, donc le CSS n'est jamais touché. Les définitions
     :root (--encre:#1A1A18; …) sont intrinsèquement préservées.
  2. Vérification stricte des comptes : on sait exactement combien
     d'occurrences quotées doivent disparaître. Divergence → arrêt.
  3. Idempotence par comptage : 0 occurrence quotée → skip.

Scope          : remplacement ciblé sur index.html.
  22 chaînes '#hex' (quotées) → 'var(--xxx)' (quotées).

Note sécurité :
  - Seules les chaînes QUOTÉES sont touchées — le CSS (hex non quotés)
    est intrinsèquement hors de portée.
  - Comptage strict : échec si le nombre ne correspond pas.
  - Backup automatique avant écriture.
  - Idempotence : re-run → 0 chaîne quotée → skip propre.

Hors scope :
  - #FAFAF7, #FFFDF7, les quasi-noirs : Lot 42 (mini-décision de charte)

Prérequis : Lot 40 appliqué
Usage     :
    python3 apply_hex_js_lot41.py path/to/index.html
    python3 apply_hex_js_lot41.py path/to/index.html --dry-run
"""

import sys
import shutil
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
# Configuration — (chaîne quotée source, chaîne quotée cible, compte attendu)
# ═══════════════════════════════════════════════════════════════════════

MIGRATIONS = [
    ("'#1A1A18'", "'var(--encre)'", 8),
    ("'#1F4D2F'", "'var(--vert-anglais)'", 6),
    ("'#E85A1F'", "'var(--orange-polo)'", 4),
    ("'#BA7517'", "'var(--or)'", 3),
    ("'#6B655B'", "'var(--gris)'", 1),
]


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 1:
        print("Usage: python3 apply_hex_js_lot41.py <index.html> [--dry-run]")
        return 1
    path = Path(paths[0])
    if not path.exists():
        print(f"  ✗ fichier introuvable : {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    original = text

    print(f"\n► Lot 41 — Hygiène couleur : hex JS → variables de charte")
    print(f"  Fichier : {path.name}")

    # ── Idempotence : déjà migré ? ───────────────────────────────────
    counts = {src: text.count(src) for src, _, _ in MIGRATIONS}
    total = sum(counts.values())

    if total == 0:
        print(f"  ▸ 0 chaîne hex quotée à migrer — déjà appliqué (skip)")
        return 0

    # ── Vérification des comptes attendus ────────────────────────────
    errors = []
    for src, dst, expected in MIGRATIONS:
        actual = counts[src]
        if actual != expected:
            errors.append(
                f"  ✗ {src} : {actual} occurrence(s) trouvée(s), "
                f"{expected} attendue(s) — divergence, arrêt sans écriture"
            )
    if errors:
        print("\n".join(errors))
        print(f"  → vérifier le fichier source ou les prérequis")
        return 1

    # ── Application ──────────────────────────────────────────────────
    migrated = {}
    for src, dst, _ in MIGRATIONS:
        migrated[src] = text.count(src)
        text = text.replace(src, dst)

    # ── Rapport ──────────────────────────────────────────────────────
    for src, dst, _ in MIGRATIONS:
        print(f"  ✓ {src} → {dst} : {migrated[src]} occurrence(s) migrée(s)")

    delta = len(text) - len(original)
    print(f"  ▸ Final  : {len(text):,} chars ({delta:+d})")

    if dry_run:
        print(f"  (dry-run, fichier non modifié)")
        return 0

    # ── Backup + écriture ────────────────────────────────────────────
    backup = path.with_name(path.name + ".before_lot_41_hex_js")
    shutil.copy2(path, backup)
    path.write_text(text, encoding="utf-8")
    print(f"  ▸ Backup : {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
