# CONTRAT — JSONB `auction` & colonnes `cars` (Vue Enchères CARNET)

**Document de jonction frontend ↔ scraper.**
Ce que le frontend `index.html` consomme pour la Vue Enchères. Dérivé du code réel — `dbRowToAuction`, `deriveAuctionStatus`, `fetchAuctionsLive` — pas de la mémoire.

- **Frontend de référence** : `index.html` md5 `dc9dbd6e` (post-Lot 48)
- **Repo scraper** : `Vinci75000/autoradar-scraper` — `~/Code/autoradar/scraper/`
- **Cible d'écriture** : table `cars`, Supabase Frankfurt
- **Principe** : la tuyauterie frontend est complète et testée. Ce document dit quelle eau envoyer pour qu'elle coule. Le scraper produit, le frontend consomme — ce papier est la frontière entre les deux.

---

## 1. Vue d'ensemble — comment une enchère arrive à l'écran

```
scraper AuctionExtractor
   └─ écrit une row dans `cars` avec :
        is_auction = true
        + colonnes plates : mk, mo, yr, km, ci, co, src, src_url
        + colonne JSONB `auction` = { status, source, lot, bid_current,
              estimate_low, estimate_high, reserve_met, h_offset,
              bids, watching, sold_price }
                          │
                          ▼
frontend  fetchAuctionsLive()
   └─ SELECT id,mk,mo,yr,km,ci,co,src,src_url,auction,updated_at
      FROM cars WHERE is_auction = true
      ORDER BY updated_at DESC LIMIT 60
                          │
                          ▼
          dbRowToAuction(row)  ── mappe row → objet enchère
                          │
                          ▼
          deriveAuctionStatus(a)  ── calcule live/upcoming/sold
                          │
                          ▼
   renderEncheresPage → 3 sections + Auction Index (Lot 48)
   renderAuctionSheet → fiche + pont vers annonces (Lot 45)
```

**Deux endroits où écrire, pas un :**
1. **Colonnes plates de `cars`** — `mk, mo, yr, km, ci, co, src, src_url` — exactement comme une annonce normale.
2. **Colonne JSONB `auction`** — un objet qui ne contient QUE les champs spécifiques à l'enchère.

Le frontend lit les deux. Une enchère est une `car` comme une autre, **plus** un sac JSONB.

---

## 2. Le filtre d'aiguillage — `is_auction`

| Colonne | Type | Valeur | Rôle |
|---|---|---|---|
| `is_auction` | bool | `true` pour une enchère, `false` pour une annonce | Le frontend sépare les deux mondes là-dessus. `fetchAuctionsLive` filtre `.eq('is_auction', true)`, `fetchListingsLive` filtre `.eq('is_auction', false)`. |

**Sans `is_auction = true`, une enchère n'apparaît jamais dans la Vue Enchères** — elle tomberait dans la vue annonces. C'est le premier interrupteur.

---

## 3. Colonnes plates de `cars` consommées par la Vue Enchères

Le mapper `dbRowToAuction` lit ces colonnes directement sur la row (pas dans le JSONB) :

| Colonne `cars` | Type | Défaut frontend si vide | Usage dans la fiche enchère |
|---|---|---|---|
| `id` | (PK) | — | identifiant du lot, sert au routing `openAuction` |
| `mk` | text | `''` | marque affichée — **sert aussi au pont enchère↔annonce (Lot 45/46)** |
| `mo` | text | `''` | modèle affiché — **sert au pont** (matching par inclusion) |
| `yr` | int | `''` | année affichée — **sert au pont** (tolérance ±2 / ±5 ans) |
| `km` | int | `'—'` | kilométrage, reformaté avec séparateurs de milliers |
| `ci` | text | `''` | ville (ex. "Stuttgart") |
| `co` | text | `''` | pays en toutes lettres (ex. "Allemagne") — sert aussi de `country` |
| `src` | text | `''` | **fallback** de `source` si `auction.source` est vide |
| `src_url` | text | `''` | lien externe vers le lot (bouton "Ouvrir sur…") |
| `updated_at` | timestamp | — | tri `ORDER BY updated_at DESC` + label de fraîcheur |

**Important — le pont (Lots 45-47) dépend de `mk`/`mo`/`yr` plats.** Si une enchère a un `mk`/`mo` incohérent avec les annonces (ex. `"chevrolet corvette"` au lieu de `"Chevrolet"` + `"Corvette"`), le pont ne matchera pas. La normalisation marque/modèle doit être **la même** que pour les annonces — c'est déjà le rôle de `normalize_brand` / `_extract_make` côté scraper.

---

## 4. La colonne JSONB `auction` — le cœur du contrat

Objet JSON stocké dans `cars.auction`. Le frontend lit `const a = row.auction || {}` — donc **un JSONB absent ne crashe pas**, mais l'enchère est alors quasi vide (pas de prix, pas de temps). Tous les champs ci-dessous sont en **snake_case** (le frontend les lit tels quels).

| Clé JSONB | Type attendu | Défaut frontend | Obligatoire ? | Rôle |
|---|---|---|---|---|
| `h_offset` | number (heures signées) | `0` | **CRITIQUE** | Heures jusqu'à la clôture. **Négatif = clôture passée, positif = à venir.** C'est LA vérité temporelle : `deriveAuctionStatus` s'en sert en priorité pour calculer live/upcoming/sold. Voir §5. |
| `status` | string | `''` | recommandé (filet) | Statut brut au moment du scrape. Sert de **filet uniquement si `h_offset` est absent/non numérique**. Valeurs tolérées : voir §5. |
| `source` | string | `''` (fallback `src`) | recommandé | Maison de vente affichée (ex. "RM Sotheby's"). Sert à l'Auction Index (maison la plus active). |
| `lot` | string | `''` | recommandé | Numéro de lot (ex. "#RM-2026-058"). Affiché tel quel. |
| `bid_current` | number (€) | `0` | si `status=live` | Enchère actuelle. Affichée si > 0 sur les lots live. Entre dans le calcul du volume au marteau si `sold_price` absent. |
| `estimate_low` | number (€) | `0` | recommandé | Estimation basse. Affichée partout. **Sert au pont (Lot 45)** : signal "−X%" si une annonce est sous l'estimation basse. |
| `estimate_high` | number (€) | `0` | recommandé | Estimation haute. Sert à `getSoldDelta` (adjugé au-dessus/sous estimation) et à la tension de l'Index. |
| `sold_price` | number (€) ou null | `null` | si `status=sold` | Prix d'adjudication. Affiché sur les lots vendus. Entre dans le volume au marteau de l'Index. |
| `reserve_met` | bool | `false` | si `status=live` | Réserve atteinte ou non. Affiché en chip sur les lots live (vert si atteinte). |
| `bids` | number | `0` | optionnel | Nombre d'enchères. Affiché en stat de carte. |
| `watching` | number | `0` | optionnel | Nombre de personnes qui suivent. Affiché en stat de carte. |

### Exemple — JSONB `auction` d'un lot LIVE
```json
{
  "status": "live",
  "source": "Bring a Trailer",
  "lot": "#BAT-2026-3814",
  "h_offset": 6,
  "bid_current": 825000,
  "estimate_low": 850000,
  "estimate_high": 1100000,
  "reserve_met": false,
  "bids": 42,
  "watching": 118
}
```

### Exemple — JSONB `auction` d'un lot UPCOMING
```json
{
  "status": "upcoming",
  "source": "Bring a Trailer",
  "lot": "#BAT-2026-3956",
  "h_offset": 96,
  "bid_current": null,
  "estimate_low": 18000000,
  "estimate_high": 24000000,
  "reserve_met": null,
  "bids": 0,
  "watching": 892
}
```

### Exemple — JSONB `auction` d'un lot SOLD
```json
{
  "status": "sold",
  "source": "RM Sotheby's",
  "lot": "#RM-2026-058",
  "h_offset": -72,
  "bid_current": 3650000,
  "estimate_low": 3500000,
  "estimate_high": 4500000,
  "reserve_met": true,
  "bids": 38,
  "watching": 621,
  "sold_price": 3650000
}
```

---

## 5. La règle du statut — `h_offset` d'abord, `status` en filet

C'est le point le plus important du contrat. Le frontend (`deriveAuctionStatus`, Lot 44) **ne fait pas confiance aveugle au `status` du scraper** — parce que c'est une valeur figée au moment du scrape, qui périme. Il dérive le statut de `h_offset` à chaque rendu.

### Priorité 1 — `h_offset` (si numérique)
```
h_offset <= 0           → 'sold'      (clôture passée)
h_offset > 72           → 'upcoming'  (clôture lointaine, > 3 jours)
0 < h_offset <= 72      → 'live'      (clôture proche)
```

**Le seuil `72` heures** (`UPCOMING_THRESHOLD_H` dans le frontend) = la convention des mocks (live ≤ 3j, upcoming 3-7j).

⚠️ **ACTION SCRAPER** : si la fonction `derive_status` du scraper utilise une convention différente (autre seuil, autre logique), **deux options** :
- soit aligner le scraper sur 72h,
- soit me dire la convention scraper et j'ajuste `UPCOMING_THRESHOLD_H` côté frontend.
Une seule des deux. À trancher avant d'ouvrir la vanne.

### Priorité 2 — `status` brut (filet, si `h_offset` absent ou non numérique)
Le frontend normalise `status` (trim + lowercase) et accepte ces synonymes :
```
sold      ← sold, ended, closed, finished, complete, completed, vendue, vendu
upcoming  ← upcoming, coming, scheduled, soon, future, prochainement, a venir, à venir
live      ← live, active, open, running, ongoing, encours, en cours, en direct
```
Tout autre valeur **non reconnue ET sans `h_offset`** → `'live'` (visible, jamais perdu) + un `console.warn` côté navigateur signalant le statut inconnu.

### Recommandation
**Écrire toujours `h_offset` ET `status`.** `h_offset` pilote, `status` est le filet quand `h_offset` n'a pas pu être scrapé. Un lot avec `h_offset` correct affiche le bon statut même si le cron n'est pas repassé depuis des heures.

---

## 6. Champs dérivés côté frontend — NE PAS écrire

Le frontend calcule ces valeurs lui-même. Le scraper ne les écrit pas :

| Valeur | Calculée par | À partir de |
|---|---|---|
| `status` final (live/upcoming/sold) | `deriveAuctionStatus` | `h_offset` puis `status` brut |
| temps restant ("clôture dans 2j 4h") | `formatTimeLeft` | `h_offset` |
| urgence du compte à rebours | `isCountdownUrgent` | `h_offset` + statut |
| delta vs estimation ("+12 %") | `getSoldDelta` | `sold_price`, `estimate_low/high` |
| label de fraîcheur | `deriveFreshLabel` | `updated_at` |
| pont vers annonces | `findMarketBridge` (Lot 45) | `mk`/`mo`/`yr` plats |
| indicateurs de l'Auction Index | `computeAuctionIndex` (Lot 48) | agrégat de tout ce qui précède |

---

## 7. Checklist de câblage scraper — avant d'ouvrir la vanne

- [ ] `AuctionExtractor` écrit `is_auction = true` sur chaque row d'enchère
- [ ] colonnes plates renseignées : `mk, mo, yr, km, ci, co, src, src_url`
- [ ] `mk`/`mo` passent par la **même normalisation que les annonces** (sinon le pont casse)
- [ ] colonne JSONB `auction` écrite avec les clés **snake_case** du §4
- [ ] `h_offset` calculé et écrit — **numérique**, signé (négatif = passé)
- [ ] `status` écrit aussi (filet), dans le vocabulaire toléré du §5
- [ ] convention `derive_status` du scraper vérifiée vs seuil 72h du frontend → **alignée ou signalée**
- [ ] `sold_price` renseigné sur les lots vendus, `bid_current` sur les lots live
- [ ] `estimate_low`/`estimate_high` renseignés (servent au pont ET à l'Index)
- [ ] 1 run de test → vérifier dans Supabase qu'une row a bien `is_auction=true` + JSONB complet
- [ ] ouvrir la Vue Enchères → le lot apparaît dans la bonne section
- [ ] avec ≥ 8 enchères en base → l'Auction Index apparaît en haut de page (Lot 48)

---

## 8. Comportement en sous-régime — ce qui est déjà géré

La tuyauterie frontend **dégrade proprement**, c'est voulu :

- **0 enchère en base** → la Vue Enchères affiche ses empty states ("Aucune enchère en cours"), pas d'erreur.
- **< 8 enchères** → l'Auction Index ne s'affiche pas du tout (seuil `INDEX_MIN_AUCTIONS`). La Vue reste propre.
- **JSONB `auction` partiel** → chaque champ a un défaut (`0`, `''`, `false`, `null`). Pas de crash, juste des infos manquantes sur la carte.
- **`status` inconnu sans `h_offset`** → le lot tombe en `'live'` (visible) + warn console.
- **Indicateur d'Index sans assez de données** (ex. < 3 ventes) → cet indicateur seul est masqué, pas tout l'Index.

Donc : on peut **ouvrir la vanne progressivement**. Une source, quelques lots, on regarde. Puis on élargit. Le frontend suit sans rien casser.

---

*Contrat dérivé de `index.html` md5 `dc9dbd6e` — Lots 44 (statut robuste), 45-47 (ponts), 48 (Auction Index). À tenir à jour si le mapper `dbRowToAuction` évolue.*
