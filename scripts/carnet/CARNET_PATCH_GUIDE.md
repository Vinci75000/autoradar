# CARNET · Patch Pattern Guide

> Convention d'industrialisation des modifications de `index.html`.
> Tous les changements passent par des scripts Python idempotents qui patchent le fichier via anchors uniques.

---

## Pourquoi cette approche

`index.html` fait > 20 000 lignes. Le modifier directement en éditeur ou via `sed -i` ad-hoc, c'est s'exposer à :

- des conflits si plusieurs personnes y touchent
- des régressions silencieuses
- l'impossibilité de retrouver qui a fait quoi quand
- l'impossibilité de re-déployer proprement après un reset

Le pattern **anchor-based + idempotent + versionné** résout ces problèmes :

- Chaque feature = un script `apply_<feature>_lot<N>.py`
- Chaque script trouve un **texte exact unique** (anchor) dans le fichier et le remplace
- Si l'anchor n'existe pas (déjà patché OU prérequis manquant) → comportement sûr
- Les scripts sont **réversibles** (backup auto)
- Les scripts vivent dans le repo (`scripts/carnet/`) avec un nom parlant
- Les Lot N forment une **séquence ordonnée** : N+1 dépend de N

---

## Arborescence cible

```
autoradar/
├── frontend/
│   ├── index.html
│   ├── carnet-tokens.css
│   ├── carnet-archetypes.js
│   ├── discover.html
│   ├── archetypes.html
│   ├── launch.html
│   ├── about.html
│   └── scripts/
│       └── carnet/
│           ├── carnet_patch_lib.py          # ← framework
│           ├── apply_TEMPLATE.py            # ← template pour nouveaux lots
│           ├── apply_garage_alpha_lot2.py   # ← lot 2 livré
│           ├── apply_garage_social_lot3.py  # ← à venir
│           ├── apply_ledger_events_lot4.py  # ← à venir
│           └── ...
```

---

## Workflow · créer un nouveau lot

### Étape 1 · Identifier la zone du fichier à modifier

Tu sais ce que tu veux ajouter (par ex. un nouveau bloc HTML, une fonction JS, des règles CSS). Localise dans `index.html` où ça doit aller :

```bash
# Recherche d'un repère contextuel près du point d'insertion
grep -n "garage-summary-label" index.html
grep -n "function renderGaragePage" index.html
```

### Étape 2 · Choisir un anchor unique

Un **anchor** est un bloc de texte exact présent **une seule fois** dans `index.html`. Il doit :

- contenir le point d'insertion exact (juste avant ou juste après ce que tu ajoutes)
- être suffisamment long pour être unique (idéalement 2-5 lignes)
- ne pas inclure de contenu volatile (timestamps, valeurs dynamiques, etc.)

Vérifie l'unicité :

```python
# Dans un shell Python rapide :
from pathlib import Path
from carnet_patch_lib import find_anchor_uniqueness

find_anchor_uniqueness(
    Path('frontend/index.html'),
    """  <button class="garage-card-add garage-card-add-top" data-action="openAddGarage" """,
)
```

Sortie attendue :

```
Anchor count : 1
  → unique, OK pour patcher
```

Si `count > 1`, **étendre** l'anchor (ajouter des lignes contextuelles autour) jusqu'à obtenir 1.

### Étape 3 · Définir le replacement

Le replacement contient :

1. **L'anchor complet copié à l'identique** (sans rien retirer)
2. **Le nouveau contenu** ajouté avant, après, ou injecté à l'intérieur

C'est mieux que de remplacer juste le point d'insertion : si quelqu'un fait `git revert` sur le résultat patché, l'anchor est restauré et le re-patch fonctionne.

#### Pattern critique · anchor "rompue par insertion"

L'anchor doit être **rompue par l'insertion** post-patch. Sinon, l'idempotence detection signale un faux état hybride et bloque les re-runs.

**Correct** — anchor 2 bornes, insertion au milieu :

```
Anchor        :  "AAA\n\nZZZ"               ← 2 bornes avec gap
Replacement   :  "AAA\n\n<NOUVEAU>\nZZZ"    ← injecté entre AAA et ZZZ
Post-patch    :  l'anchor "AAA\n\nZZZ" n'existe plus continue
                 → anchor_count == 0, marker present → état "appliqué" propre
```

**Incorrect** — anchor à une seule borne, ajout après :

```
Anchor        :  "AAA"                       ← une seule borne
Replacement   :  "AAA\n<NOUVEAU>"            ← ajouté APRÈS l'anchor
Post-patch    :  l'anchor "AAA" est toujours là tel quel
                 → anchor_count == 1, marker present → faux "état hybride"
```

Si tu te retrouves en "état hybride" au re-run, c'est ce pattern qu'il faut corriger : étendre l'anchor pour qu'elle inclue le point d'insertion ET un caractère/ligne situé(e) après.

### Étape 4 · Choisir un idempotence_marker

Un **marker** est un texte qui :

- est **présent dans le replacement**
- est **absent de l'anchor**
- est **stable** (pas un timestamp, pas un hash variable)

Typiquement : un commentaire `/* ═══ LOT N (Phase X) — feature ═══ */` ou un nom de fonction unique.

### Étape 5 · Écrire le script

Copie `apply_TEMPLATE.py` vers `apply_<feature>_lot<N>.py`, remplis les sections. Exemple minimal :

```python
from carnet_patch_lib import Patch, PatchSet, run_cli
import sys

PATCHSET = PatchSet(
    name="Lot 3 (Phase β) — Garage Social Co-ownership",
    requires=["LOT 2 (Phase α)"],  # marker du lot précédent
    patches=[
        Patch(
            name="CSS social tiers",
            anchor=""".garage-deadlines-empty-add{
  display:inline-block;
  margin-top:8px;""",
            replacement=""".garage-deadlines-empty-add{
  display:inline-block;
  margin-top:8px;

/* ═══ LOT 3 (Phase β) — Garage social co-ownership ═══ */
.social-tier-card { ... }""",
            idempotence_marker="LOT 3 (Phase β)",
        ),
    ],
)

if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
```

### Étape 6 · Tester en dry-run

```bash
cd scripts/carnet/
python3 apply_garage_social_lot3.py ../../frontend/index.html --dry-run
```

Output attendu :

```
► Lot 3 (Phase β) — Garage Social Co-ownership
  ✓ CSS social tiers
  ▸ Final : ...
  (dry-run, fichier non modifié)
```

### Étape 7 · Appliquer + commit

```bash
python3 apply_garage_social_lot3.py ../../frontend/index.html
git add scripts/carnet/apply_garage_social_lot3.py ../../frontend/index.html
git commit -m "feat(garage): Lot 3 Phase β — social co-ownership"
git push
```

---

## Conventions

### Naming

- **Lot N** : numérotation séquentielle, jamais réutilisée même après revert
- **Phase α / β / γ / δ** : groupement éditorial des lots, indicatif uniquement
- **Slug feature** : `<domain>_<feature>` court, snake_case
- **Marker** : `LOT N (Phase X)` constant, présent dans replacement seulement

### Découpage en sous-lots

Un lot fait **un changement cohérent unique**. Si tu te retrouves à écrire 10+ patches dans un même lot, c'est qu'il faut le splitter en :

- Lot N : changement A
- Lot N+1 : changement B

Garde chaque PR atomique.

### Format de commit

```
feat(<domain>): Lot N Phase X — <description courte>

[optionnel : détail des patches]
```

Domaines courants : `garage`, `affut`, `auctions`, `auth`, `auctions`, `discover`.

---

## Troubleshooting

| Erreur | Cause probable | Fix |
|---|---|---|
| `ANCHOR NOT FOUND` (marker absent) | Lot précédent pas appliqué OU texte modifié manuellement | Vérifier l'historique des lots, ou ajuster l'anchor |
| `ANCHOR NOT FOUND` (marker présent) | Le patch est **déjà appliqué** mais l'anchor a été modifié depuis | C'est normal, le script skip — pas d'action |
| `ANCHOR PRÉSENT N×` | Anchor pas assez spécifique | Étendre l'anchor avec plus de contexte avant/après |
| `Patch X : idempotence_marker présent dans anchor` | Marker trop générique ou anchor trop large | Choisir un marker plus spécifique |
| `Patch X : idempotence_marker absent du replacement` | Faute de frappe dans le marker | Vérifier alignement marker / replacement |
| `Prérequis manquant : marker 'XXX' absent` | Lot précédent (qui ajoute ce marker) pas appliqué | Appliquer les lots dans l'ordre |

---

## Tests d'idempotence

Tout script doit passer ce test :

```bash
# Premier run : applique
python3 apply_xxx_lotN.py index.html
# → "X patches appliqués"

# Deuxième run : skip
python3 apply_xxx_lotN.py index.html
# → "X patches déjà appliqués (skip)"
# → exit code 0
# → fichier inchangé (vérifiable avec md5 avant/après)
```

Si le deuxième run modifie le fichier, le script est cassé.

---

## Roadmap des lots CARNET

### Lots déjà appliqués

| Lot | Phase | Domaine | Statut |
|---|---|---|---|
| 1.1 | α | Sprint Convergence v2 (nav éditoriale + archetypes module + Mes archétypes menu user) | ✅ main |
| 2 | α | Garage Alpha (hero variante C + sparkline + échéances) | ✅ main |

### Lots à venir · designs prêts (mockups uploadés)

| Lot | Phase | Domaine | Source mockup |
|---|---|---|---|
| 3 | β | Garage Social Co-ownership (Famille / Amis / Connaissances) | `carnet_garage_social_coownership.html` |
| 4 | β | Ledger Events + Settlement RLUSD (entretien partagé) | `carnet_ledger_events.html` |
| 5 | β | Co-pilote Actif (rallye TSD régularité Tour de Corse) | `carnet_copilote_actif.html` |
| 6 | γ | Track Day Mode B (chronos Le Mans Bugatti + coaching) | `carnet_track_day_gumball_modes.html` |
| 7 | γ | Gumball Convoy Mode C (programme jour + reel live) | `carnet_track_day_gumball_modes.html` |
| 8 | α | Garage Dashboard Complet (refonte visuelle 5,49 M€ portfolio) | `carnet_garage_dashboard_complet.html` |

### Lots à scripter · pages éditoriales

| Lot | Phase | Domaine | Notes |
|---|---|---|---|
| 9 | α | Pages légales — Privacy (RGPD article 13) | Year -1 obligatoire avant launch |
| 10 | α | Pages légales — Security | Year -1 |
| 11 | α | Pages légales — Accessibility (WCAG 2.2 AA) | Year -1 |
| 12 | α | Pages légales — Transparency (allocation + wallet) | Year -1 |

### Lots à scripter · features structurelles

| Lot | Phase | Domaine | Notes |
|---|---|---|---|
| 13 | δ | Filtre archétype dans Garage grid | Croise `CarnetArchetypes.loadProfiles()` + cars |
| 14 | δ | Tax timing test sur Mercedes Genesis (cas réel) | Étape 18 marathon |
| 15 | δ | Mémoire Genesis Co-pilot mode Discret | Year -1 oct-nov 2026 |

---

## Maintenance long terme

- Tous les scripts vivent dans `scripts/carnet/`, **jamais** dans `/tmp/`
- `carnet_patch_lib.py` est versionné — si tu changes son API, bump version + adapter les scripts
- Les fichiers `.before_<lot>` sont des backups automatiques, **gitignorés** (à ajouter à `.gitignore`)
- Quand un lot est en prod depuis 3+ mois sans rollback, son script peut être archivé dans `scripts/carnet/archive/`

`.gitignore` à compléter :
```
frontend/*.before_*
frontend/index.html.bak.*
```

---

*CARNET · Patch Pattern v1.0 · 2026-05-14*
