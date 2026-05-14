#!/usr/bin/env python3
"""
CARNET · Lot 42 — Hygiène couleur : intrus légers (clôture)

Source        : audit final post-charte v9. Dernier lot d'hygiène après
                les gris CSS (Lot 40) et les hex JS (Lot 41). Ce lot
                traite les derniers hex en dur — les "intrus légers".

  L'audit a montré que ces couleurs ne distinguent PAS des sections
  (la question posée était : "même nuance si ça améliore l'UX entre
  sections ?" — la réponse est non, ce ne sont pas des séparateurs).
  Ce sont :
    · #0D0D0D ×2  → état :active de .kpi-card.is-hero et .new-alert-btn
      (le fond NORMAL est var(--encre) ; au :active il s'assombrit).
      C'est exactement le rôle d'un -dark, comme --orange-polo-dark.
    · #0F0F0E ×1  → fond du body en desktop (phone-frame look). Un fond
      décoratif, à 1-2 unités de #0D0D0D.
    · #1F1F1D + #2C2C28  → rings d'ombre dans un box-shadow. #2C2C28 est
      quasi --encre-soft (#2A2823), #1F1F1D quasi --encre (#1A1A18).
    · #FAFAF7 ×16 + #FFFDF7 ×1  → le "blanc le plus clair", fond des
      cartes qui ressortent sur le papier crème. Vrai rôle distinct.

Décisions (validées) — 2 variables créées, le reste rattaché :
  · --encre-dark (#0D0D0D) — CRÉÉE. Complète le système :active : comme
    --orange-polo a son --orange-polo-dark, --encre a son --encre-dark.
    Le feedback tactile devient systématique et nommé. #0F0F0E (fond
    desktop) s'y rattache — écart imperceptible.
  · --papier-pur (#FAFAF7) — CRÉÉE. Le niveau de fond le plus clair,
    17 usages, mérite son nom. #FFFDF7 (1×) s'y rattache.
  · #1F1F1D → var(--encre), #2C2C28 → var(--encre-soft) — RATTACHÉS.
    Des ombres : la nuance exacte ne se voit pas. Pas de variable.

  Après ce lot : 0 hex en dur dans index.html (sauf le logo Google,
  normatif). La charte est entièrement tokenisée.

Pourquoi un remplacement de chaînes exactes (méthode Lots 40-41) :
  Chaque transformation est identique et sans ambiguïté. #0D0D0D
  devient TOUJOURS var(--encre-dark). Les chaînes box-shadow et :root
  sont uniques (1 occurrence) — le remplacement exact les cible
  précisément. Vérification stricte des comptes avant écriture.

Scope          : remplacement de chaînes exactes sur index.html.
  1. Ajout :root  : 2 lignes (--encre-dark, --papier-pur) après
     --ambre-warning.
  2. #0d0d0d → var(--encre-dark)     ×2
  3. #0F0F0E → var(--encre-dark)     ×1
  4. box-shadow ring : #1F1F1D → var(--encre), #2C2C28 → var(--encre-soft)
  5. #FAFAF7 → var(--papier-pur)     ×16
  6. #FFFDF7 → var(--papier-pur)     ×1

Note sécurité :
  - Chaînes EXACTES — l'ajout :root et le box-shadow sont des chaînes
    uniques (1 occurrence vérifiée), aucun risque de faux match.
  - Les hex #0D0D0D / #FAFAF7 etc. n'existent QUE comme valeurs CSS
    en dur (pas en :root — ils n'y sont pas encore définis, pas en JS).
  - Comptage strict : échec si un compte ne correspond pas.
  - Backup automatique. Idempotence : marker = "--encre-dark" présent.

Hors scope :
  - rien — ce lot CLÔT l'hygiène couleur.

Prérequis : Lot 41 appliqué
Usage     :
    python3 apply_intrus_legers_lot42.py path/to/index.html
    python3 apply_intrus_legers_lot42.py path/to/index.html --dry-run
"""

import sys
import shutil
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
# 1. Ajout :root — chaîne unique (anchor 2-bornes implicite : --ambre-warning
#    en haut, ligne blanche + --display en bas).
# ═══════════════════════════════════════════════════════════════════════

ROOT_ADD_SRC = """  --ambre-warning:#C8943A;     /* catégorie : sévérité « warning » — Lot 39 */

  --display:'Bodoni Moda','Times New Roman',serif;"""

ROOT_ADD_DST = """  --ambre-warning:#C8943A;     /* catégorie : sévérité « warning » — Lot 39 */
  --encre-dark:#0D0D0D;        /* encre, état :active — pendant de --orange-polo-dark, Lot 42 */
  --papier-pur:#FAFAF7;        /* le fond le plus clair, cartes sur crème — Lot 42 */

  --display:'Bodoni Moda','Times New Roman',serif;"""


# ═══════════════════════════════════════════════════════════════════════
# 2. box-shadow ring — chaîne unique.
# ═══════════════════════════════════════════════════════════════════════

BOXSHADOW_SRC = "0 0 0 8px #1F1F1D,0 0 0 9px #2C2C28"
BOXSHADOW_DST = "0 0 0 8px var(--encre),0 0 0 9px var(--encre-soft)"


# ═══════════════════════════════════════════════════════════════════════
# 3. Remplacements multiples — (chaîne source, chaîne cible, compte attendu)
# ═══════════════════════════════════════════════════════════════════════

MULTI = [
    ("#0d0d0d", "var(--encre-dark)", 2),
    ("#0F0F0E", "var(--encre-dark)", 1),
    ("#FAFAF7", "var(--papier-pur)", 16),
    ("#FFFDF7", "var(--papier-pur)", 1),
]


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 1:
        print("Usage: python3 apply_intrus_legers_lot42.py <index.html> [--dry-run]")
        return 1
    path = Path(paths[0])
    if not path.exists():
        print(f"  ✗ fichier introuvable : {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    original = text

    print(f"\n► Lot 42 — Hygiène couleur : intrus légers (clôture)")
    print(f"  Fichier : {path.name}")

    # ── Idempotence : --encre-dark déjà dans :root ? ─────────────────
    if "--encre-dark:#0D0D0D;" in text:
        print(f"  ▸ --encre-dark déjà défini — déjà appliqué (skip)")
        return 0

    # ── Vérification des comptes ─────────────────────────────────────
    errors = []
    if text.count(ROOT_ADD_SRC) != 1:
        errors.append(f"  ✗ ancre :root : {text.count(ROOT_ADD_SRC)} occurrence(s), 1 attendue")
    if text.count(BOXSHADOW_SRC) != 1:
        errors.append(f"  ✗ ancre box-shadow : {text.count(BOXSHADOW_SRC)} occurrence(s), 1 attendue")
    for src, dst, expected in MULTI:
        actual = text.count(src)
        if actual != expected:
            errors.append(f"  ✗ {src} : {actual} occurrence(s), {expected} attendue(s)")
    if errors:
        print("\n".join(errors))
        print(f"  → vérifier le fichier source ou les prérequis")
        return 1

    # ── Application ──────────────────────────────────────────────────
    # ORDRE CRITIQUE : les remplacements de VALEURS d'abord, l'ajout
    # :root en DERNIER. Sinon la définition --papier-pur:#FAFAF7 qu'on
    # ajoute serait elle-même attrapée par le remplacement #FAFAF7 →
    # var(--papier-pur), créant une définition circulaire cassée
    # (--papier-pur:var(--papier-pur);). Idem #0D0D0D. On migre donc
    # tous les usages en dur AVANT d'introduire les définitions.

    text = text.replace(BOXSHADOW_SRC, BOXSHADOW_DST)
    print(f"  ✓ box-shadow ring — #1F1F1D → var(--encre), #2C2C28 → var(--encre-soft)")

    for src, dst, _ in MULTI:
        n = text.count(src)
        text = text.replace(src, dst)
        print(f"  ✓ {src} → {dst} : {n} occurrence(s) migrée(s)")

    text = text.replace(ROOT_ADD_SRC, ROOT_ADD_DST)
    print(f"  ✓ :root — --encre-dark + --papier-pur ajoutés (en dernier, après les migrations)")

    delta = len(text) - len(original)
    print(f"  ▸ Final  : {len(text):,} chars ({delta:+d})")

    if dry_run:
        print(f"  (dry-run, fichier non modifié)")
        return 0

    # ── Backup + écriture ────────────────────────────────────────────
    backup = path.with_name(path.name + ".before_lot_42_intrus_legers")
    shutil.copy2(path, backup)
    path.write_text(text, encoding="utf-8")
    print(f"  ▸ Backup : {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
