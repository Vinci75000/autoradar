#!/usr/bin/env python3
"""
fix_cars_view.py — bascule cars_with_production (vue Supabase cassée 500)
                  vers la table cars directe.

12 mai 2026 — Sergio debug. Idempotent. Backup avant écriture.

Usage :
    cd ~/Code/autoradar/frontend
    python3 fix_cars_view.py

Conséquences :
- Le frontend récupère les 24k+ cars actives via la table cars directement.
- Le badge "production" disparaît temporairement (production_total / production_confidence
  undefined, _shouldShowProdBadge retourne false par défaut → safe).
- Réactivable plus tard si on répare la vue ou si on ajoute les colonnes à cars.
"""
from pathlib import Path
import sys

p = Path(__file__).parent / "index.html"
if not p.exists():
    print(f"❌ {p} introuvable. Lance depuis ~/Code/autoradar/frontend/")
    sys.exit(1)

content = p.read_text()
original = content

# Anchor #1 : la table dans le from()
old_1 = "_sb.from('cars_with_production').select('*')"
new_1 = "_sb.from('cars').select('*')"

# Anchor #2 : le chainage des order (drop production_confidence)
old_2 = ".eq('status', 'active').order('production_confidence', { ascending: false, nullsFirst: false }).order('sc', { ascending: false }).limit(200);"
new_2 = ".eq('status', 'active').order('sc', { ascending: false }).limit(200);"

# Idempotence : si déjà patché, exit propre
if old_1 not in content and new_1 in content:
    print("✓ Déjà patché — rien à faire")
    sys.exit(0)

# Sanity check anchors
c1 = content.count(old_1)
c2 = content.count(old_2)
if c1 != 1:
    print(f"❌ Anchor #1 trouvé {c1} fois (attendu 1). Abort.")
    print(f"   Pattern: {old_1!r}")
    sys.exit(2)
if c2 != 1:
    print(f"❌ Anchor #2 trouvé {c2} fois (attendu 1). Abort.")
    print(f"   Pattern: {old_2!r}")
    sys.exit(2)

# Apply
content = content.replace(old_1, new_1)
content = content.replace(old_2, new_2)

# Backup before write
backup = p.with_suffix(".html.before_cars_fix")
backup.write_text(original)
p.write_text(content)

print("✓ Patché :")
print(f"  L. ~5580 : cars_with_production → cars")
print(f"  L. ~5581 : drop .order('production_confidence', ...)")
print(f"✓ Backup créé : {backup.name}")
print()
print("Vérif rapide :")
print(f"  grep -n \"from('cars\" index.html")
print(f"  grep -n \"cars_with_production\" index.html  # devrait être vide")
