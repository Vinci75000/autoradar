# CARNET · Patch Pattern Guide

> Convention d'industrialisation des modifications de `index.html`.
> Tous les changements passent par des scripts Python idempotents qui patchent le fichier via anchors uniques.

---

## Pourquoi cette approche

`index.html` fait > 23 000 lignes. Le modifier directement en éditeur ou via `sed -i` ad-hoc, c'est s'exposer à :

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
│   ├── discover.html · archetypes.html · launch.html · about.html
│   ├── privacy.html · security.html · accessibility.html
│   ├── transparency.html · genesis.html        # ← pages standalone Lots 9-12,15
│   └── scripts/
│       └── carnet/
│           ├── carnet_patch_lib.py          # ← framework
│           ├── apply_TEMPLATE.py            # ← template pour nouveaux lots
│           ├── apply_<feature>_lot<N>.py    # ← un script par lot
│           └── archive/                     # ← scripts de lots en prod 3+ mois
```

---

## Workflow · créer un nouveau lot

### Étape 0 · Resynchroniser sur la base réelle

**Avant tout audit ou patch**, s'assurer que le fichier de travail correspond bien à la version `main`. Le fichier de travail peut diverger de `main` entre les sessions (résidus de patches non poussés, scripts fantômes).

> **Règle anti-désynchro** — en cas de doute, Sly upload son `index.html` actuel, Claude repart de cette base. Ne jamais auditer ni patcher un fichier dont on n'est pas sûr qu'il est à jour. Voir Leçon 4.

### Étape 1 · Identifier la zone du fichier à modifier

```bash
grep -n "garage-summary-label" index.html
grep -n "function renderGaragePage" index.html
```

### Étape 2 · Choisir un anchor unique

Un **anchor** est un bloc de texte exact présent **une seule fois** dans `index.html`. Il doit :

- contenir le point d'insertion exact (juste avant ou juste après ce que tu ajoutes)
- être suffisamment long pour être unique (idéalement 2-5 lignes)
- ne pas inclure de contenu volatile (timestamps, valeurs dynamiques)
- **être une anchor 2-bornes** quand le replacement réinsère le texte de l'anchor (Leçon 1 — le bug le plus fréquent)

Vérifie l'unicité :

```python
from pathlib import Path
from carnet_patch_lib import find_anchor_uniqueness

find_anchor_uniqueness(Path('frontend/index.html'), """  <button class="..." """)
```

Sortie attendue : `Anchor count : 1 → unique, OK pour patcher`. Si `count > 1`, **étendre** l'anchor.

### Étape 3 · Définir le replacement

Le replacement contient l'anchor complet copié à l'identique + le nouveau contenu. Voir **Leçon 1** pour le pattern critique de l'anchor rompue.

### Étape 4 · Choisir un idempotence_marker

Un **marker** est un texte qui :

- est **présent dans le replacement**
- est **absent de l'anchor**
- est **stable** (pas un timestamp, pas un hash variable)
- est **unique dans le FICHIER ENTIER**, pas seulement dans la zone du patch (Leçon 3)

### Étape 5 · Écrire le script

Copie `apply_TEMPLATE.py`. Signature : `run_cli(PATCHSET)` prend **un seul argument**.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli

PATCHSET = PatchSet(
    name="Lot N (Phase X) — <feature>",
    requires=["<marker réel présent dans le fichier>"],  # voir Leçon 5
    patches=[
        Patch(
            name="<sous-patch>",
            anchor="""...""",          # raw string si escapes Unicode — Leçon 2
            replacement="""...""",
            idempotence_marker="LOT N (Phase X) — <feature>",
        ),
    ],
)

if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
```

### Étape 6 · Pipeline de test standard

Tout lot passe ce pipeline avant présentation :

```bash
# 1. dry-run — vérifie que toutes les anchors sont trouvées
python3 apply_xxx_lotN.py index.html --dry-run

# 2. apply
python3 apply_xxx_lotN.py index.html

# 3. idempotence stricte — md5 identique avant/après re-run
md5sum index.html
python3 apply_xxx_lotN.py index.html
md5sum index.html   # ← DOIT être identique

# 4. intégrité HTML — aucun tag non fermé (HTMLParser custom)
# 5. JS syntax smoke test — new Function(s) sur chaque <script> inline
# 6. métriques + vérif markers présents
wc -l index.html ; grep -c "LOT N" index.html
```

Si une étape échoue → ne pas présenter, corriger d'abord. **Pas de fausse victoire si les chiffres ne collent pas** (Leçon 6).

### Étape 7 · Appliquer + commit

```bash
git add scripts/carnet/apply_xxx_lotN.py index.html
git commit -m 'feat(<domain>): Lot N Phase X — <description>'   # ← guillemets SIMPLES, Leçon 7
git push origin main
```

---

## ⚠️ Leçons — bugs récurrents et comment les éviter

> Cette section capitalise les bugs rencontrés sur les Lots 1.1 → 22.
> Chacun est apparu **plusieurs fois** avant d'être systématisé. Les lire **avant** d'écrire un patch fait gagner un cycle entier.

### Leçon 1 — Anchor 2-bornes (le bug le plus fréquent · 7 occurrences)

**Symptôme** : au re-run, le framework signale `état hybride (marker présent + anchor encore là)` et refuse d'écrire.

**Cause** : l'anchor n'a qu'**une borne**. Le replacement réinsère le texte de l'anchor puis ajoute le nouveau contenu *après* (ou *avant*). Résultat : post-patch, l'anchor d'origine existe **toujours telle quelle**, ET le marker est présent → le framework voit les deux et conclut à un état incohérent.

**Le test mental, à faire systématiquement** :
> *« Après insertion, l'anchor d'origine existe-t-elle encore mot pour mot dans le fichier ? »*
> Si **oui** → anchor 1-borne → bug garanti. Il faut une 2e borne.

**Incorrect** — anchor 1-borne :
```
Anchor       :  "AAA"
Replacement  :  "AAA\n<NOUVEAU>"
Post-patch   :  "AAA" est toujours là intacte → faux "état hybride"
```

**Correct** — anchor 2-bornes, insertion au milieu :
```
Anchor       :  "AAA\n\nZZZ"               (2 bornes séparées par un gap)
Replacement  :  "AAA\n\n<NOUVEAU>\nZZZ"     (injecté ENTRE AAA et ZZZ)
Post-patch   :  "AAA\n\nZZZ" n'existe plus en continu → anchor cassée → propre
```

**🛡️ Garde-fou automatique (carnet_patch_lib v1.1)** : depuis la v1.1, `Patch.__post_init__` **lève une `ValueError` à l'instanciation** si le `replacement` commence ou finit par le texte exact de l'`anchor`. Le bug est attrapé avant même de toucher le fichier — au moment où le script `apply_xxx.py` est importé. C'est la 7e occurrence (JS-7 du Lot 23) qui a justifié de coder le filet plutôt que de seulement le documenter. Si le garde-fou lève : étendre l'anchor avec la borne manquante (basse si le replacement commençait par l'anchor, haute s'il finissait par).

**Fix d'un patch déjà bugué** : étendre l'anchor pour inclure une borne (la ligne/le commentaire qui suit ou précède immédiatement le point d'insertion). Le fichier déjà patché reste **valide** — le bug n'est que dans le script, pas dans le résultat. Après fix, re-tester l'idempotence des deux côtés : (a) sur le fichier déjà patché → doit skip, (b) from-scratch sur le backup → doit produire le même md5.

*Occurrences : Lots 3, 4, 14 (JS-1), 17, 21 (CSS-1), 24 (JS-2), 23 (JS-7). Le garde-fou v1.1 rend cette leçon auto-appliquée.*

### Leçon 2 — Raw strings pour les escapes Unicode

**Symptôme** : `ANCHOR NOT FOUND` alors que le texte semble correct visuellement.

**Cause** : dans `index.html`, certains caractères sont stockés comme **chaînes JS littérales** — `\u00d7`, `\u00b7`, `\u25cf`, `\u2713`, etc. Ce sont 6 caractères (`backslash u 0 0 d 7`), pas le caractère Unicode natif. Une string Python normale `"\u00d7"` est interprétée comme `×` → ne matche pas.

**Fix** : utiliser des **raw strings** `r"""..."""` pour toute anchor JS contenant des `\u`. Ou échapper le backslash : `"\\u00d7"`.

**Attention au cas mixte** : certaines occurrences du même glyphe sont en `\u2713` littéral-JS, d'autres en `✓` natif. Toujours vérifier avec `grep` + `cat -A` ce qui est réellement dans le fichier.

*Occurrence : Lot 13b-1, géré préventivement aux Lots 19 et 22.*

### Leçon 3 — Markers uniques dans le FICHIER ENTIER

**Symptôme** : un patch est faussement détecté comme « déjà appliqué » et skippé alors qu'il ne l'est pas.

**Cause** : l'`idempotence_marker` n'est pas unique dans le fichier. Cas typique : plusieurs patches d'un même lot produisent un output **identique** (ex. migrer 3 classes différentes vers la même classe cible `class="tick"`). Le marker du patch 1 matche aussi les zones des patches 2 et 3.

**Fix** : le marker doit être unique dans tout le fichier. Si plusieurs patches produisent un output similaire, **étendre le marker avec le contexte voisin distinctif** :
- au lieu de `<span class="tick">` (qui apparaîtra 4×)
- utiliser `<span class="profile-card-chip">...</span>\n  <span class="tick">` (le voisin rend unique)

C'est aussi pour ça que les anchors de ce type de patch doivent inclure la ligne voisine distinctive.

*Occurrence : Lot 13b-3, géré préventivement au Lot 22 (JS-3/4/5).*

### Leçon 4 — Anti-désynchro du fichier de travail

**Symptôme** : Claude audite `index.html` et déclare qu'une feature « existe déjà » alors qu'elle n'a jamais été livrée sur `main` — ou l'inverse.

**Cause** : le fichier de travail de Claude (`/home/claude/index.html`) peut diverger de la version `main` de Sly entre les sessions. Résidus de patches appliqués localement mais non poussés, scripts fantômes.

**Fix** :
- En cas de doute, **Sly upload son `index.html` actuel**, Claude le copie comme base de vérité et repart de là.
- Toujours faire l'**Étape 0** (resynchroniser) avant un audit.
- Vérifier au `md5sum` que le fichier de travail correspond bien au dernier output connu.

*Occurrence : Lot 17 — Claude a cru à tort que le Lot 17 existait (résidu fantôme dans son working dir). Résolu en repartant de l'upload de Sly.*

### Leçon 5 — `requires` = marker réel, pas nom de PatchSet

**Symptôme** : `Prérequis manquant : marker 'XXX' absent du fichier` alors que le lot précédent est bien appliqué.

**Cause** : le `requires` d'un PatchSet cherche un **texte présent dans le fichier**. Le `name` du PatchSet (`"Lot 21 (Phase α) — Unification du système banner"`) n'est **jamais injecté** dans `index.html` — seuls les `idempotence_marker` des patches le sont. Mettre le nom du PatchSet dans `requires` échoue donc toujours.

**Fix** : dans `requires`, mettre un **`idempotence_marker` réel** d'un patch du lot précédent — celui qu'on sait présent dans le fichier après application. Vérifier avec `grep` ce qui est réellement dans le fichier.

*Occurrence : Lot 22 — `requires` pointait vers `"LOT 21 (Phase α) — Unification..."` (nom du PatchSet) au lieu de `"Lot 21 — modifiers : .banner devient le système unique"` (marker réel).*

### Leçon 6 — Vérifier les doubles définitions CSS (`!important`)

**Symptôme** : un patch CSS « réussit », mais le style attendu ne s'applique pas — ou un retrait de classe semble incomplet.

**Cause** : `index.html` a accumulé des couches de CSS (base + overrides v5.x avec `!important`). Une même classe peut être **définie 2 fois** : une fois dans le bloc de base, une fois dans un bloc d'harmonisation v5.x avec `!important`. Un patch qui ne retire que la 1re définition laisse la 2e (qui gagne par `!important`).

**Fix** : avant de migrer/retirer une classe CSS, compter **toutes** ses définitions :
```bash
grep -nE "^\s*\.ma-classe\s*\{" index.html   # combien de blocs ?
```
S'il y en a plusieurs, prévoir un patch par définition. Vérifier aussi la **profondeur** (racine vs `@media`) au tokenizer — voir section dédiée.

*Occurrence : Lot 22 — `.profile-card-tick` avait 2 définitions (base ligne ~3050 + override `!important` ligne ~3907). Le 1er patch n'avait retiré que la base.*

### Leçon 7 — Pièges zsh (messages de commit & shell)

Trois pièges zsh ont mordu pendant le projet, **tous évitables avec les guillemets simples** :

| Piège | Symptôme | Fix |
|---|---|---|
| `!` dans `"..."` (ex. `!important`) | `zsh: event not found: important` | guillemets **simples** `'...'` pour les messages de commit |
| `#` collé comme commande | `zsh: command not found: #` | ne jamais coller un commentaire `#` comme ligne de commande |
| `path` comme variable shell | écrase silencieusement `$PATH` | utiliser `pth`/`p`/`url` — jamais `path`, `cdpath`, `fpath`, `manpath` |

**Règle par défaut** : guillemets simples pour tout message de commit. Pas d'échappement à retenir, pas d'accent perdu.

### Leçon 8 — Chevauchement d'anchor entre 2 patches d'un même lot

**Symptôme** : un dry-run passe à `N-1/N`, un patch affiche `ANCHOR NOT FOUND` alors que son anchor existait bien dans le fichier de départ.

**Cause** : deux patches du même PatchSet ont des anchors qui se **chevauchent**. Les patches s'appliquent **séquentiellement** — le patch A transforme une zone que le patch B utilisait comme borne. Quand B s'exécute, sa borne a déjà été réécrite par A → introuvable.

Cas vécu : au Lot 23, JS-3 patchait le bloc `'non_driver'` de `PROFILE_ADVICE` en incluant `'social': {` comme **borne basse**. Mais JS-4 patchait justement le bloc `'social'` — dont l'anchor commençait par `'social': {`. JS-3 transformait `'social': {` → `'mousquetaire': {`, donc JS-4 ne trouvait plus rien.

**Fix** : si deux zones à patcher sont **adjacentes ou imbriquées**, ne pas les traiter en 2 patches — les **fusionner en un seul patch** qui couvre les deux d'un tenant. Une anchor continue, pas de chevauchement possible. C'est aussi plus lisible.

**Prévention** : avant d'écrire un lot multi-patches, lister les zones touchées et vérifier qu'aucune borne d'un patch n'est dans la zone réécrite par un autre.

*Occurrence : Lot 23 (JS-3/JS-4 fusionnés).*

### Leçon 9 — Vérifier qu'un champ existe sur l'objet avant de s'en servir

**Symptôme** : une logique conditionnelle (filtre, inférence, affichage) ne se déclenche jamais, ou se déclenche toujours — comme si la condition était `undefined`.

**Cause** : le code lit un champ qui n'existe pas sur l'objet à ce stade du cycle de vie. Les objets du fichier ne sont pas uniformes : un objet `car` du tableau `GARAGE` n'a pas les mêmes champs qu'un `car` après la migration v5, ou qu'un `car` issu d'un listing scrapé.

Cas vécu : au Lot 24, le premier jet de `inferCarArchetypes` s'appuyait sur `car.fullServiceHistory` et `car.serviceUpToDate` — qui **n'existent pas** sur les objets `GARAGE` (ils sont initialisés ailleurs, plus tard). La logique aurait été morte. Le vrai signal disponible était `car.spec` (texte libre riche) et `car.chassis`.

**Fix** : avant d'utiliser `car.X` dans une nouvelle logique, vérifier que `X` existe **sur les objets réels** concernés :
```bash
# Lister tous les champs réellement présents sur un objet GARAGE
sed -n '<début>,<fin>p' index.html | grep -oE "^\s+[a-zA-Z]+:"
# Et tous les car.X lus dans le code
grep -oE "car\.[a-zA-Z]+" index.html | sort -u
```
Puis ne s'appuyer que sur les champs confirmés. Préférer un champ universel (`spec`, `brand`, `model`, `year`, `km`) à un champ conditionnel.

*Occurrence : Lot 24 (fullServiceHistory/serviceUpToDate inexistants → bascule sur spec/chassis).*

---

## Conventions

### Naming

- **Lot N** : numérotation séquentielle, jamais réutilisée même après revert. Sous-lots possibles (`18b`, `19-A`) pour un correctif ou un sous-périmètre.
- **Phase α / β / γ / δ** : groupement éditorial des lots, indicatif.
- **Slug feature** : `<domain>_<feature>` court, snake_case.
- **Marker** : `LOT N (Phase X) — <feature>` constant, présent dans replacement seulement, unique dans le fichier.

### Découpage en sous-lots

Un lot fait **un changement cohérent**. Au-delà de ~6-8 patches, envisager un split. Mais un lot de migration cohérent (ex. Lot 22, 10 patches tous liés à l'unification des ticks) peut rester groupé si la cohérence prime.

### Format de commit

```
feat(<domain>): Lot N Phase X — <description courte>
refactor(<domain>): Lot N Phase X — <description>   (pour migrations / nettoyage)
fix(scripts): Lot N — <description>                 (pour correctif de script seul)
```

Domaines : `garage`, `affut`, `auctions`, `auth`, `discover`, `ui`, `genesis`, `scripts`.
**Guillemets simples** pour le `-m` (Leçon 7).

### Add-only / surcharge non destructive

Privilégier les patches **additifs** quand c'est possible : ajouter une classe modifier (`.is-grid`, `.is-dashed`), un bloc CSS en fin de `<style>`, une surcharge par cascade. Si le patch échoue, le style de base reste fonctionnel — pas de régression. Réécrire un bloc existant n'est justifié que si l'extension est impossible.

---

## Troubleshooting

| Erreur | Cause probable | Fix |
|---|---|---|
| `ANCHOR NOT FOUND` (marker absent) | Lot précédent pas appliqué, OU texte modifié, OU variable supposée ≠ réelle | Vérifier l'historique des lots ; `grep` le contexte réel (cf. JS-2 du Lot 22 : `cat.label` vs `c.label`) |
| `ANCHOR NOT FOUND` (marker présent) | Patch **déjà appliqué**, anchor modifiée depuis | Normal, le script skip — pas d'action |
| `état hybride (marker présent + anchor encore là)` | **Anchor 1-borne** | Leçon 1 — étendre l'anchor en 2-bornes |
| `ANCHOR PRÉSENT N×` | Anchor pas assez spécifique | Étendre avec plus de contexte |
| `idempotence_marker présent dans anchor` | Marker trop générique / anchor trop large | Marker plus spécifique |
| `idempotence_marker absent du replacement` | Faute de frappe | Vérifier alignement marker / replacement |
| `Prérequis manquant : marker 'XXX' absent` | `requires` pointe vers un nom de PatchSet, pas un marker réel | Leçon 5 — mettre un `idempotence_marker` réel |
| Patch « réussit » mais style pas appliqué | Double définition CSS, la 2e en `!important` | Leçon 6 — `grep` toutes les définitions |
| `ANCHOR NOT FOUND` sur du JS avec `\u...` | String Python interprète l'escape | Leçon 2 — raw string ou `\\u` |
| `ValueError: anchor 1-borne` à l'import du script | Le garde-fou v1.1 a détecté un replacement qui commence/finit par l'anchor | Leçon 1 — étendre l'anchor avec la borne manquante. Le bug est attrapé avant écriture, c'est voulu |
| `ANCHOR NOT FOUND` sur un vieux lot ré-exécuté seul | Un lot récent a réécrit la zone (ex. Lot 24 vs Lot 23) | Attendu — séquence ordonnée. Le from-scratch dans l'ordre fonctionne |

---

## Vérifier la profondeur CSS (racine vs @media)

Avant de migrer / retirer une règle CSS, vérifier si elle est au niveau racine ou dans une `@media`. **Ne jamais se fier à l'indentation visuelle** — elle est parfois purement cosmétique.

Tokenizer fiable (ignore accolades dans strings et commentaires) :

```python
def depth_at(lines, target_line):
    depth = 0; in_string = None; in_comment = False; prev = ''
    for ln in range(1, target_line):
        line = lines[ln-1]; i = 0
        while i < len(line):
            ch = line[i]; two = line[i:i+2]
            if in_comment:
                if two == '*/': in_comment = False; i += 2; continue
            elif in_string:
                if ch == in_string and prev != '\\': in_string = None
            elif two == '/*': in_comment = True; i += 2; continue
            elif ch in ('"', "'"): in_string = ch
            elif ch == '{': depth += 1
            elif ch == '}': depth -= 1
            prev = ch; i += 1
    return depth
```

Calibrer sur une classe dont on connaît le niveau (ex. `.sheet-btn` est au niveau racine du stylesheet) pour interpréter le `depth` retourné.

---

## Roadmap des lots CARNET

### Lots livrés · 1.1 → 22 (tous sur `main`)

| Lot | Phase | Domaine | Marker / fichier |
|---|---|---|---|
| 1.1 | α | Sprint Convergence v2 (nav éditoriale + carnet-archetypes.js + Mes archétypes menu user) | — |
| 2 | α | Garage Alpha (hero variante C + sparkline + échéances) | `LOT 2 (Phase α)` |
| 3 | β | Garage Social Co-ownership | `LOT 3 (Phase β)` |
| 4 | β | Ledger Events + Settlement RLUSD | `LOT 4 (Phase β)` |
| 5 | β | Co-pilote Actif (overlay `CARNET_COPILOTE_DEMO`) | `LOT 5 (Phase β)` |
| 6 | γ | Track Day Mode B (overlay `CARNET_TRACKDAY_DEMO`) | `LOT 6 (Phase γ)` |
| 7 | γ | Gumball Convoy Mode C (overlay `CARNET_GUMBALL_DEMO`) | `LOT 7 (Phase γ)` |
| 8 | α | Garage Dashboard Complet (5 sections) | `LOT 8 (Phase α)` |
| 9 | α | Page Privacy RGPD standalone | `privacy.html` · `data-lot9` |
| 10 | α | Page Security standalone | `security.html` · `data-lot10` |
| 11 | α | Page Accessibility WCAG 2.2 AA standalone | `accessibility.html` · `data-lot11` |
| 12 | α | Page Transparency standalone | `transparency.html` · `data-lot12` |
| 13 | α | Refactor `.carnet-overlay-*` générique + factory `CarnetOverlay.create()` | `LOT 13 (Phase α refactor)` |
| 13b-1/2/3 | α | Migration in-place Co-pilote / Track Day / Gumball vers CarnetOverlay | `Migré Lot 13b-*` |
| 14 | α | Filtre archétype Garage grid (chips OR multi-select) | `LOT 14 (Phase α)` |
| 15 | α | Page Mémoire Genesis standalone (founder story, VC-001) | `genesis.html` · `data-lot15` |
| 16 | α | Hero affût + KPI bar refonte φ (1 hero KPI + 4 compactes grid) | `LOT 16 (Phase α)` |
| 17 | α | TabBar bottom refonte φ (barre indicateur orange polo) | `LOT 17 (Phase α)` |
| 18 / 18b | α | CTA principal `.new-alert-btn` refonte φ + alignement orange polo | `LOT 18 / 18b (Phase α)` |
| 19-A | α | Migration `.sheet-row` legacy → `.sheet-detail-row` | `Lot 19-A` |
| 20 | α | Sheets création — flow Nouvelle alerte (builder) refonte φ | `LOT 20 (Phase α)` |
| 21 | α | Unification système banner (`.banner` générique vivant + modifiers) | `Lot 21 — modifiers` |
| 22 | α | Form components — unification des ticks (`.tick` canonique) | `Lot 22 — .tick` |
| 23 | α | Migration archétypes legacy (`non_driver`→`mondain`, `social`→`mousquetaire`) + migration localStorage | `Lot 23 — non_driver→mondain` |
| 24 | α | Refonte `inferCarArchetypes` — faisceau large, 8 avatars recalés, multi-match assumé | `Lot 24 — faisceau large` |

**Plan refonte mobile v5+ φ : 7/7 lots livrés** (Hero+KPI · TabBar · Boutons · Sheets détail · Sheets création · Empty states+banners · Form components).

**Système archétypes** (Lots 14, 23, 24) : IDs alignés sur `carnet-archetypes.js` (Discover v1.0), inférence en faisceau large cohérente avec l'ADN réel de chaque avatar.

### Pistes pour la suite

| Domaine | Notes |
|---|---|
| Convergence index unique | Greffer auth + publier + filtres sur la lignée mobile-first v6.18 |
| Phase 2 — Vue Enchères frontend | Tab Enchères 3 sections LIVE / UPCOMING / SOLD |
| Audit visuel complet | Revue des 24 lots en local / prod |

---

## Tests d'idempotence

Tout script doit passer ce test, **des deux côtés** :

```bash
# A. sur le fichier déjà patché → skip
python3 apply_xxx_lotN.py index.html
# → "X patches déjà appliqués (skip)", exit 0, fichier inchangé (md5 identique)

# B. from-scratch sur le backup pré-lot → produit le même résultat
cp index.html.before_lot_N_xxx /tmp/test.html
python3 apply_xxx_lotN.py /tmp/test.html
md5sum /tmp/test.html index.html   # ← les 2 md5 DOIVENT être identiques
```

Si le run B ne reproduit pas exactement le run A, ou si un re-run modifie le fichier, le script est cassé.

---

## Maintenance long terme

- Tous les scripts vivent dans `scripts/carnet/`, **jamais** dans `/tmp/`.
- `carnet_patch_lib.py` est versionné — si tu changes son API, bump version + adapter les scripts. **Version actuelle : v1.1** (garde-fou anti anchor 1-borne — Leçon 1 auto-appliquée).
- Signature : `run_cli(PATCHSET)` prend **un seul argument**.
- Les fichiers `.before_<lot>` sont des backups automatiques, **gitignorés**.
- Quand un lot est en prod 3+ mois sans rollback, son script peut être archivé dans `scripts/carnet/archive/`.
- **Lots qui réécrivent une zone entière** (ex. Lot 24 refait tout `inferCarArchetypes`) : ils remplacent les patches plus anciens qui touchaient cette zone. Un script ancien peut alors afficher `ANCHOR NOT FOUND` s'il est ré-exécuté seul sur un fichier déjà au lot récent — c'est attendu (séquence ordonnée), pas un bug. Le from-scratch dans l'ordre reste la référence.

`.gitignore` (patterns **relatifs** au dossier où vit le `.gitignore`) :
```
*.before_*
index.html.bak.*
```

---

*CARNET · Patch Pattern v2.1 · 2026-05-14 · couvre les Lots 1.1 → 24 · carnet_patch_lib v1.1*
