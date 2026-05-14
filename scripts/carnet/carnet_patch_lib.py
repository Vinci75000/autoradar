#!/usr/bin/env python3
"""
CARNET · Patch Library

Framework pour appliquer des patches idempotents sur index.html.
Chaque lot fonctionnel = 1 script `apply_<feature>_lot<N>.py` qui importe cette lib.

Principes :
  - Patches anchor-based : on cherche un texte unique exact, on le remplace
  - Idempotence : marker dans replacement = "déjà appliqué", skip silencieux
  - Validation : anchor doit être unique (count == 1) avant remplacement
  - Backup automatique avant écriture
  - Support dry-run pour valider sans écrire
  - Exit code conforme aux conventions Unix (0 = OK, 1 = erreurs)

Usage minimal dans un script de lot :

    from carnet_patch_lib import Patch, PatchSet, run_cli

    PATCHSET = PatchSet(
        name="Lot N (Phase X) — feature",
        patches=[
            Patch(
                name="CSS additions",
                anchor=\"\"\"<TEXTE-EXACT-UNIQUE>\"\"\",
                replacement=\"\"\"<TEXTE-EXACT-UNIQUE>
+ NEW CONTENT\"\"\",
                idempotence_marker="NEW CONTENT",
            ),
        ],
    )

    if __name__ == "__main__":
        import sys
        sys.exit(run_cli(PATCHSET))

Convention de naming :
  apply_<feature_slug>_lot<N>.py
  Ex : apply_garage_alpha_lot2.py, apply_ledger_events_lot4.py

Version : 1.0 · 2026-05-14
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import argparse
import sys


# ─── Couleurs ANSI pour output console lisible ────────────────────────

class _Style:
    """ANSI styles — détection TTY auto, fallback no-op si pipe/CI."""
    _enabled = sys.stdout.isatty()
    RESET   = '\033[0m'  if _enabled else ''
    DIM     = '\033[2m'  if _enabled else ''
    BOLD    = '\033[1m'  if _enabled else ''
    GREEN   = '\033[32m' if _enabled else ''
    RED     = '\033[31m' if _enabled else ''
    YELLOW  = '\033[33m' if _enabled else ''
    BLUE    = '\033[34m' if _enabled else ''
    GREY    = '\033[90m' if _enabled else ''


# ─── Modèle de données ────────────────────────────────────────────────

@dataclass
class Patch:
    """
    Un patch unitaire : trouve un anchor unique, le remplace par replacement.

    Attributs :
      name : libellé court ("CSS additions", "Hero variante C")
      anchor : texte exact à chercher dans le fichier (doit être unique)
      replacement : texte qui remplace l'anchor
      idempotence_marker : texte présent dans replacement, ABSENT dans anchor.
                           Si déjà présent dans le fichier → patch skippé.

    L'idempotence_marker est essentiel : sans lui, un re-run écraserait des
    contenus ou échouerait sur anchor introuvable sans savoir si c'est normal.
    """
    name: str
    anchor: str
    replacement: str
    idempotence_marker: str

    def __post_init__(self):
        # Sanity checks
        if self.idempotence_marker in self.anchor:
            raise ValueError(
                f"Patch '{self.name}' : idempotence_marker présent dans anchor "
                f"— impossible de distinguer 'à patcher' vs 'déjà patché'."
            )
        if self.idempotence_marker not in self.replacement:
            raise ValueError(
                f"Patch '{self.name}' : idempotence_marker absent du replacement "
                f"— skip idempotent ne pourra jamais détecter l'état appliqué."
            )

    def is_applied(self, content: str) -> bool:
        return self.idempotence_marker in content

    def anchor_count(self, content: str) -> int:
        return content.count(self.anchor)


@dataclass
class PatchSet:
    """
    Un lot de patches qui forment un changement fonctionnel cohérent.

    Attributs :
      name : libellé du lot (apparaît dans output console + nom backup)
      patches : liste ordonnée de Patch (appliqués séquentiellement)
      requires : liste optionnelle de markers qui doivent être présents
                 avant d'appliquer ce lot (ex. "LOT 1.1 appliqué")
    """
    name: str
    patches: List[Patch]
    requires: List[str] = field(default_factory=list)

    def apply(self, path: Path, dry_run: bool = False) -> int:
        """Applique le PatchSet. Retourne exit code (0 = OK, 1 = erreurs)."""
        content = path.read_text(encoding='utf-8')
        original_chars = len(content)
        original_lines = content.count('\n')

        print(f"\n{_Style.BOLD}► {self.name}{_Style.RESET}")
        print(f"  {_Style.GREY}Fichier : {path}{_Style.RESET}")
        print(f"  {_Style.GREY}Initial : {original_chars:,} chars · {original_lines:,} lignes{_Style.RESET}\n")

        # Validation prérequis
        for req in self.requires:
            if req not in content:
                print(f"  {_Style.RED}✗ Prérequis manquant : marker '{req}' absent du fichier{_Style.RESET}")
                print(f"    {_Style.GREY}→ vérifier que les lots précédents sont appliqués{_Style.RESET}")
                return 1

        issues = 0
        applied_count = 0

        for patch in self.patches:
            anchor_count = patch.anchor_count(content)
            already_applied = patch.is_applied(content)

            if already_applied:
                if anchor_count == 0:
                    print(f"  {_Style.DIM}◇ {patch.name} : déjà appliqué (skip){_Style.RESET}")
                    continue
                else:
                    print(f"  {_Style.RED}✗ {patch.name} : état hybride (marker présent + anchor encore là){_Style.RESET}")
                    print(f"    {_Style.GREY}→ patch partiellement appliqué ? rollback manuel nécessaire{_Style.RESET}")
                    issues += 1
                    continue

            if anchor_count == 0:
                print(f"  {_Style.RED}✗ {patch.name} : ANCHOR NOT FOUND{_Style.RESET}")
                print(f"    {_Style.GREY}→ texte introuvable, vérifier prérequis ou fichier source{_Style.RESET}")
                issues += 1
                continue

            if anchor_count > 1:
                print(f"  {_Style.RED}✗ {patch.name} : ANCHOR PRÉSENT {anchor_count}× (pas unique){_Style.RESET}")
                print(f"    {_Style.GREY}→ étendre l'anchor jusqu'à unicité{_Style.RESET}")
                issues += 1
                continue

            # anchor_count == 1, marker absent → appliquer
            content = content.replace(patch.anchor, patch.replacement, 1)
            print(f"  {_Style.GREEN}✓ {patch.name}{_Style.RESET}")
            applied_count += 1

        final_chars = len(content)
        final_lines = content.count('\n')
        delta_chars = final_chars - original_chars
        delta_lines = final_lines - original_lines

        print(f"\n  {_Style.BOLD}▸ Final{_Style.RESET}  : {final_chars:,} chars ({delta_chars:+,}) · {final_lines:,} lignes ({delta_lines:+,})")

        if issues > 0:
            print(f"\n  {_Style.RED}✗ {issues} erreur(s) — aucune écriture{_Style.RESET}")
            return 1

        if applied_count == 0:
            print(f"  {_Style.DIM}◇ Aucun patch à appliquer (tous déjà présents){_Style.RESET}")
            return 0

        if dry_run:
            print(f"\n  {_Style.YELLOW}(dry-run, fichier non modifié){_Style.RESET}")
            return 0

        # Backup auto avant écriture (skip si backup déjà existe)
        slug = _slugify(self.name)
        backup_path = path.with_suffix(path.suffix + f'.before_{slug}')
        if not backup_path.exists():
            backup_path.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"  {_Style.BLUE}▸ Backup{_Style.RESET} : {backup_path.name}")
        else:
            print(f"  {_Style.DIM}◇ Backup existe déjà : {backup_path.name}{_Style.RESET}")

        path.write_text(content, encoding='utf-8')
        print(f"  {_Style.GREEN}▸ Écrit{_Style.RESET}  : {path}")
        return 0


# ─── Helpers utilitaires ──────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convertit un nom de lot en slug filesystem-safe pour les backups."""
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in (' ', '-', '_', '·'):
            out.append('_')
    slug = ''.join(out).strip('_')
    # Compress underscores consécutifs
    while '__' in slug:
        slug = slug.replace('__', '_')
    return slug[:60]  # limite raisonnable


def run_cli(patchset: PatchSet) -> int:
    """
    Helper CLI pour les scripts `apply_<feature>_lot<N>.py`.
    Parse argv (path + --dry-run), valide, applique le patchset.
    """
    parser = argparse.ArgumentParser(
        description=f"Apply CARNET {patchset.name}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", type=Path, help="Path to index.html")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate anchors without writing")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"{_Style.RED}Error: {args.file} not found{_Style.RESET}")
        return 1

    if not args.file.is_file():
        print(f"{_Style.RED}Error: {args.file} is not a regular file{_Style.RESET}")
        return 1

    return patchset.apply(args.file, dry_run=args.dry_run)


def find_anchor_uniqueness(path: Path, anchor: str) -> int:
    """
    Helper de développement : compte les occurrences d'un anchor candidat
    pour vérifier son unicité avant d'écrire un patch.

    Usage interactif :
        from carnet_patch_lib import find_anchor_uniqueness
        find_anchor_uniqueness(Path('index.html'), '<texte candidat>')
    """
    content = path.read_text(encoding='utf-8')
    count = content.count(anchor)
    print(f"Anchor count : {count}")
    if count == 0:
        print("  → introuvable, vérifier le texte")
    elif count == 1:
        print("  → unique, OK pour patcher")
    else:
        print(f"  → {count} occurrences, étendre l'anchor jusqu'à unicité")
    return count
