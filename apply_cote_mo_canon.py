#!/usr/bin/env python3
"""
Apply Sprint B.5 step 4 — frontend uses mo_canon for cote lookup.

Idempotent: refuses to run if patches already applied.
2 patches on index.html:
  1. IIFE Cars mapping: add mo_canon: car.mo_canon || car.mo
  2. coteChip(car): lookup with car.mo_canon || car.mo (fallback)
"""
import sys
from pathlib import Path

p = Path("index.html")
if not p.exists():
    sys.exit("ERROR: index.html introuvable. Lance ce script depuis ~/Code/autoradar/frontend/")

content = p.read_text()

# Idempotence guard
if 'mo_canon: car.mo_canon' in content:
    sys.exit(
        "ERROR: 'mo_canon: car.mo_canon' déjà présent.\n"
        "       Pour relancer: git reset --hard HEAD~1 && git push --force-with-lease"
    )


def apply_patch(name, content, anchor, replacement, mode="prepend"):
    n = content.count(anchor)
    if n != 1:
        sys.exit(f"ERROR Patch {name}: ancre trouvée {n} fois (attendu 1). Abort.")
    if mode == "prepend":
        return content.replace(anchor, replacement + anchor)
    elif mode == "replace":
        return content.replace(anchor, replacement)
    else:
        sys.exit(f"Bad mode: {mode}")


# Patch 1 — Add mo_canon to car object in IIFE Cars mapping
OLD1 = '''id: car.id, mk: car.mk, mod: car.mod || '', mo: car.mo,'''
NEW1 = '''id: car.id, mk: car.mk, mod: car.mod || '', mo: car.mo, mo_canon: car.mo_canon || car.mo,'''
content = apply_patch("1 (mapping mo_canon)", content, OLD1, NEW1, mode="replace")
print("✓ Patch 1 — mo_canon ajouté dans le mapping IIFE Cars")


# Patch 2 — coteChip lookup uses mo_canon with mo fallback
OLD2 = '''const seg = _coteSegments.get(`${car.mk}|${car.mo}`);'''
NEW2 = '''const seg = _coteSegments.get(`${car.mk}|${car.mo_canon || car.mo}`);'''
content = apply_patch("2 (coteChip lookup)", content, OLD2, NEW2, mode="replace")
print("✓ Patch 2 — coteChip lookup utilise mo_canon avec fallback mo")


p.write_text(content)
print()
print("✅ Frontend mo_canon appliqué")
