# CARNET — Roadmap Rêve

> Vision figée le 12 mai 2026.
> Document de référence pour les futurs sprints.
> Principe directeur : **smart, light, clean, robust, scalable.**

---

## Vision finale en une ligne

> **24/7, les 143 000 meilleures voitures curatées d'Europe en ligne — annonces et enchères, scrapées et propres CARNET, tout le process en autopilot, business model aligné sur Ripple.**

---

## Sommaire

1. [Cadre stratégique](#1-cadre-stratégique)
2. [Couche 1 — Pilotage interne](#2-couche-1--pilotage-interne)
3. [Couche 2 — Modèle dealers](#3-couche-2--modèle-dealers)
4. [Couche 3 — Boucle dealer + Treasury fintech](#4-couche-3--boucle-dealer--treasury-fintech)
5. [Roadmap par horizon](#5-roadmap-par-horizon)
6. [Principes architecturaux](#6-principes-architecturaux)
7. [Questions à formaliser avec le Cabinet CSBC](#7-questions-à-formaliser-avec-le-cabinet-csbc)
8. [Sources et références](#8-sources-et-références)

---

## 1. Cadre stratégique

### Entité

CARNET est une **Association loi 1901 à but non lucratif**. Aucun salaire, aucun dividende, bénévoles uniquement. L'argent collecté finance l'infrastructure et des événements automobiles avec enfants.

Acronymes officiels :
- **FR** : Carnet Automatisé Référentiel du Négoce Et de la Transparence
- **EN** : Curated Automotive Records Network for Exchange and Trust

### North Star — 143 000 voitures actives, quatre canaux

La North Star n'est pas un volume de scraping, c'est un **catalogue curaté** de 143 000 voitures actives en permanence sur l'app, alimenté par quatre canaux complémentaires :

| Canal | Type | Source |
|---|---|---|
| Annonces scrapées | Fixed-price | Dealers + marketplaces (autoradar-scraper) |
| Enchères scrapées | Bidding | BaT, Collecting Cars, RM Sotheby's, Artcurial, etc. |
| Annonces propres CARNET | Fixed-price | `is_autoradar=true`, dépôt direct propriétaires/dealers |
| Enchères propres CARNET | Bidding | Asso CARNET en tant que maison d'enchères |

Les quatre canaux convergent vers une expérience unique côté utilisateur — une seule app, une seule grammaire de recherche, une seule fiche voiture.

### Autopilot par principe

Tout le process est en **autopilot** :
- Acquisition (crons scrapers GitHub Actions)
- Curation (scoring, LLM extraction)
- Mise à jour (wash cron, status sweeper enchères, refresh enchères live)
- Paiements (Worker Cloudflare `carnet-payements`)
- Royalties (XLS-20 native)
- Treasury management (rebalance EURØP ↔ XRP)

L'humain intervient uniquement pour :
- Décisions stratégiques (statuts asso, signataires multi-sig)
- Modération exceptionnelle (dispute, fraude)
- Curation éditoriale haut de gamme (featured cars, packs)

### Alignement Ripple business model

Carnet se positionne comme le **settlement layer + curation layer du marché automobile premium européen**, avec la même philosophie que Ripple sur la finance institutionnelle :

| Ripple | CARNET |
|---|---|
| Settlement cross-border pour banques | Settlement cross-border pour transactions auto européennes |
| Stablecoin EUR (EURØP via Schuman) | Paiements EURØP-native dans l'app |
| Custody enterprise-grade | Provenance NFT XLS-20 par voiture |
| Compliance MiCA-first | Asso 1901 + KYC dealers + MiCA stablecoin |
| Treasury management institutionnel | Treasury XRP-majoritaire / EURØP-opérationnelle |
| Enterprise (Fortune 500) | Dealers pros + maisons d'enchères |

*Si Ripple est le rail pour la finance institutionnelle, CARNET est le rail pour le marché automobile premium européen.* Même modèle, autre verticale.

### Stack final

XRPL pur · XRP · RLUSD · EURØP · MiCA-compliant · non-custody. Pas de token propre, pas d'EVM sidechain, pas de fractional ownership. La blockchain sert exclusivement de couche de confiance pour les paiements, royalties, et provenance.

### Trois couches développées en parallèle

Le rêve s'articule en trois couches qui peuvent évoluer indépendamment mais s'imbriquent à terme :

```
┌─────────────────────────────────────────────────────────────┐
│  Couche 3  —  Boucle dealer + Treasury fintech              │
│  Marketplace transactionnelle, NFT XLS-20, treasury XRP     │
├─────────────────────────────────────────────────────────────┤
│  Couche 2  —  Modèle dealers                                │
│  Table dealers, dealer_stats, whitelabel pages              │
├─────────────────────────────────────────────────────────────┤
│  Couche 1  —  Pilotage interne                              │
│  Dashboard admin, KPIs drilldowns, cost coverage            │
└─────────────────────────────────────────────────────────────┘
```

Chaque couche apporte de la valeur seule, sans dépendre de la suivante.

---

## 2. Couche 1 — Pilotage interne

### État actuel (admin v3d, 12 mai 2026)

12 KPIs avec drilldowns smart :

| KPI | Drilldown |
|---|---|
| Voitures actives | Progress vers North Star 143k + courbe stock 14j |
| Ajoutées 7j | Comparaison 7j vs 7j précédents, trend up/down |
| Score moyen | Distribution 4 buckets, reco SQL archive auto <30 |
| Premium (>100k€) | Breakdown luxury/super/hyper |
| Hyper (>1M€) | Top brands hyper, export CSV pack featuring |
| Annonces CARNET | Breakdown par tier, courbe stock CARNET |
| Enchères | LIVE/UPCOMING/SOLD breakdown |
| Revenus générés | Donations + commissions + royalties NFT, cost coverage |
| Donations totales | Stats temporelles (jour/semaine/mois/année) |
| Sources actives | Top sources, dormantes |
| Marques | Top concentration, brand le plus représenté |
| Archivées | Breakdown par raison |

Recos exécutables 1-click via `friendlyConfirm` :
- Archiver auto les scores < 30
- Forcer expire donations pending >24h
- Restaurer wash récentes (<7j)
- Purger archives > 90j (danger, double confirmation)

### Ce qu'il reste à construire

**Vue temporelle multi-séries.** Superposer cars/jour, revenus/jour, sources actives, donations sur un graphique unique. Les corrélations entre crons activés et revenus deviennent visibles.

**Vue cohorte utilisateurs.** Segmentation par type — collectionneur, occasionnel, pro, dealer. Comprendre qui rapporte, qui churn, qui convertit.

**Vue financière complète.** P&L mensuel et annuel, cashflow projeté à 13 semaines (standard Ripple Treasury), runway dynamique basé sur burn rate. Cost coverage actuel est statique avec une constante `CARNET_MONTHLY_COSTS_EUR` — passer en table SQL `app_config` éditable, avec breakdown détaillé des coûts (Vercel, Anthropic API, GitHub Actions, domain, email, etc.).

**Vue géographique.** Carte des sources, des cars par pays, des dealers. D3 choropleth ou Leaflet. Identifier les zones blanches.

**ROI par source.** Pour chaque source scrapée, calculer le coût d'extraction (LLM API calls × prix unitaire) versus la valeur ajoutée (cars premium gagnées × pondération qualité). Certaines sources peuvent être en perte sèche — il faut le savoir.

**Alertes proactives.** Le bandeau santé actuel détecte les erreurs passées. À étendre avec prédictif : *"À ce rythme de burn, runway épuisé dans X mois"*, *"Cron green_cron n'a rien produit depuis 48h"*.

---

## 3. Couche 2 — Modèle dealers

### Trois primitives techniques

#### Table `dealers`

```sql
CREATE TABLE public.dealers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug            TEXT UNIQUE NOT NULL,        -- URL-safe identifier
  name            TEXT NOT NULL,
  legal_name      TEXT,
  email           TEXT UNIQUE NOT NULL,
  phone           TEXT,
  country         TEXT,
  city            TEXT,
  website         TEXT,
  wallet_xrpl     TEXT,                        -- adresse XRPL du dealer
  tier            TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'premium')),
  commission_rate NUMERIC NOT NULL DEFAULT 1.7,-- pourcentage CARNET
  kyc_status      TEXT NOT NULL DEFAULT 'pending' CHECK (kyc_status IN ('pending', 'approved', 'rejected')),
  joined_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  metadata        JSONB DEFAULT '{}'::jsonb
);
```

#### Table `dealer_stats` (refresh nightly via cron)

Vue matérialisée plutôt que table — recalcul incrémental :

```sql
CREATE MATERIALIZED VIEW public.dealer_stats AS
SELECT
  d.id AS dealer_id,
  d.slug,
  d.tier,
  count(*) FILTER (WHERE c.status = 'active') AS listings_active,
  count(*) FILTER (WHERE c.created_at >= CURRENT_DATE - INTERVAL '30 days') AS listings_added_30d,
  count(*) FILTER (WHERE c.status = 'sold') AS listings_sold,
  avg(c.px) FILTER (WHERE c.status = 'active') AS avg_price,
  avg(c.sc) FILTER (WHERE c.status = 'active') AS avg_score,
  sum(t.amount * d.commission_rate / 100) FILTER (WHERE t.created_at >= date_trunc('month', now())) AS revenue_carnet_this_month
FROM public.dealers d
LEFT JOIN public.cars c ON c.dealer_id = d.id
LEFT JOIN public.transactions t ON t.car_id = c.id AND t.status = 'completed'
GROUP BY d.id, d.slug, d.tier;

CREATE UNIQUE INDEX ON public.dealer_stats (dealer_id);
```

Refresh quotidien via cron GitHub Actions à 04h UTC :
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY public.dealer_stats;
```

#### Lien `cars.dealer_id`

Ajout d'une colonne `dealer_id UUID REFERENCES dealers(id)` sur la table `cars`. Pour les cars scrapées sans dealer identifié, reste `NULL` — c'est le canal scraper anonyme actuel.

### Page profil dealer

URL `dealer.carnet.life/{slug}` ou plus simplement `/{slug}` directement sur carnet.life. Stock du dealer mis en avant, mais audience CARNET partagée. Brand premium + audit on-chain visible.

Tableau de bord dealer = subset de l'admin actuel, filtré sur leurs cars uniquement. **Même grammaire UX, données scopées**. Drilldowns identiques (vues actives, ajoutées 7j, performance), mais sans accès aux KPIs globaux de la plateforme.

### La proposition de valeur dealer

Pourquoi un pro accepterait de payer 1,7% sur ses ventes Carnet versus zéro sur son site propre ? Trois jambes obligatoires :

1. **Audience curatée** : visibilité auprès d'une base qualifiée, pas du trafic SEO générique.
2. **Outil de gestion stock** : tableau de bord intégré, statistiques, alertes — équivalent SaaS sectoriel à zéro coût supplémentaire pour le dealer.
3. **Preuve on-chain** : audit blockchain de l'historique des transactions du dealer. Devient un **argument commercial** vis-à-vis de leurs propres clients — *"voici 18 mois de ventes documentées on-chain, voici la provenance de chaque voiture"*.

Si une de ces trois jambes manque, le modèle s'effondre. Les trois doivent être visibles dès l'onboarding.

---

## 4. Couche 3 — Boucle dealer + Treasury fintech

### Boucle dealer

**Principe** : un dealer peut acheter, revendre, racheter, re-revendre la même voiture via Carnet. Chaque transaction génère 1,7% de commission CARNET + 1,7% de commission dealer (côté final). Le car_id reste constant à travers les transactions ; seul le wallet propriétaire change.

**Pourquoi c'est scalable par design** :
- 1 car_id = N transactions
- Chaque transaction est on-chain (XRPL transfer + royalty XLS-20 native)
- L'historique on-chain devient un **NFT-trail vérifiable**
- Le NFT XLS-20 du véhicule suit la voiture à travers ses changements de wallet, peu importe combien de fois elle change de mains

**Concrètement** :

```
Car #42 (NFT XLS-20)
├── 2026-03-15 : Dealer A → Acheteur 1   (+1,7% CARNET, +1,7% Dealer A)
├── 2026-09-22 : Acheteur 1 → Dealer A   (rachat, +1,7% CARNET)
├── 2027-01-08 : Dealer A → Acheteur 2   (+1,7% CARNET, +1,7% Dealer A)
└── 2027-06-30 : Acheteur 2 → Dealer A   (rachat, +1,7% CARNET)
```

Sur 18 mois, la même voiture a généré **6,8% de commissions CARNET** sans nouveau dépôt. Le NFT a accumulé un historique de provenance vérifiable qui devient un argument commercial à la revente.

**Tracking VIN ↔ NFT.** Chaque voiture physique = 1 NFT XLS-20 sur XRPL. Le mapping VIN ↔ NFT-ID est stocké dans Carnet (table `car_nfts`). En cas de dispute (voiture non conforme à l'annonce, fraude), le multi-sig de l'asso peut arbitrer avec les preuves on-chain.

### Treasury — Vision XRP-majoritaire, EURØP-opérationnelle

#### Pourquoi XRP en réserve principale

Janvier 2025, Grayscale et Artemis classifient XRP comme **store of value** sur quatre critères :
- Hard-capped supply (100 milliards, supply finie)
- Utilité globale (cross-border, bridge fiat)
- Résistance à la censure
- Adoption peer-to-peer

Grayscale a lancé le US XRP Trust, chemin vers ETF spot. Ripple Treasury (issu du rachat GTreasury) vend explicitement de la **digital asset liquidity management** à des Fortune 500, avec yield 24/7/365 sur idle cash digital. Le cadre institutionnel existe et est mature.

La thèse Carnet : tant que XRP est dans une phase d'adoption institutionnelle accélérée, accumuler représente un pari documenté — pas une hedging strategy au sens classique, mais une conviction sur l'écosystème Ripple. Le rôle de XRP dans la treasury n'est pas spéculatif, c'est structurel.

#### Pourquoi EURØP en liquidité opérationnelle

Schuman Financial a intégré EURØP nativement sur XRPL en mai 2025. C'est le premier euro stablecoin MiCA-compliant sur la chaîne. Issuer EMT licencié ACPR, réserves auditées KPMG, garde Société Générale.

Carnet asso française paye ses factures en EUR : Vercel hobby, Anthropic API, GitHub Actions, domain, email. Détenir EURØP supprime la conversion EUR ↔ USD ↔ XRP et donne une comptabilité 1:1 avec les coûts. Cost coverage ratio devient exact au centime près.

#### Allocation cible

| Allocation | Pourcentage du surplus | Justification |
|---|---|---|
| **EURØP — Runway opérationnel** | 12 mois de coûts (~840€ aujourd'hui) | Intouchable, oxygène opérationnel |
| **EURØP — Buffer** | 3 mois de coûts (~210€) | Rebalance sans urgence |
| **XRP — Cold storage** | 80% du surplus au-delà | Store of value, conviction long terme |
| **XRP — LP AMM XRPL pool XRP/EURØP** | 20% du XRP holdings | Yield 24/7/365, fees de swap |

Au démarrage (treasury < runway opérationnel + buffer), 100% va en EURØP. À mesure que les revenus dépassent les coûts, le surplus bascule en XRP via achat ponctuel sur creux ou DCA mensuel selon préférence.

#### Logique de rebalance

DCA inverse : XRP par défaut, conversion ponctuelle EURØP pour les factures du mois. Au 1er du mois, si EURØP balance < 1 mois de coûts, déclencher swap XRP → EURØP pour reconstituer le mois courant.

Règles modélisables en config :

```javascript
const TREASURY_CONFIG = {
  OPERATIONAL_RESERVE_MONTHS: 12,
  BUFFER_MONTHS: 3,
  MONTHLY_COST_EUR: 70,
  XRP_AMM_ALLOCATION_PCT: 20,
  DCA_FREQUENCY: 'monthly',
  AUTO_REBALANCE: false,        // décision manuelle au démarrage
  MULTISIG_THRESHOLD: 3,        // 3 signatures sur 5 requises
};
```

#### Dashboard public Transparence

Page `/transparence` (publique, pas de login requis) qui affiche en temps réel :
- Balance EURØP du wallet `rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU`
- Balance XRP
- LP positions sur AMM XRPL
- Historique des derniers mouvements on-chain
- Cost coverage ratio
- Liens vers explorer XRPL pour vérification publique

C'est de la **trust radicale**. Aucun marketplace classique ne peut faire ça. Devient un argument de différenciation majeur — *"vos commissions sont visibles publiquement on-chain, en temps réel"*.

### Référence Ripple Treasury

Le framework Ripple Treasury en 3 étapes correspond à ce qu'on construit :

1. **Automate Data Consolidation** — déjà : RPC `get_admin_kpis`, pagination Supabase, refresh dashboard automatique.
2. **Real-Time Monitoring** — déjà : Sentry crons, health alerts banner, drilldowns live.
3. **Use Data Insights** — déjà : insights smart par KPI, recos 1-click, cost coverage dynamique.

À l'échelle CARNET, mais le pattern est identique. La position : *en avance, pas en marge*. Carnet incarne ce que Ripple vend comme vision treasury moderne, dans le format d'une asso non-profit avec mission culturelle automobile.

---

## 5. Roadmap par horizon

### Court terme — 1 à 3 mois

**Sprint Dealers Fondation.** Schéma SQL `dealers` + `dealer_stats` + colonne `cars.dealer_id`. Vue admin "Dealers" basique (liste + détail dealer + edit). Pas encore d'onboarding public — seul l'admin peut créer un dealer manuellement. Permet de commencer à attribuer les cars scrapées aux dealers correspondants.

**Sprint 2 NFT XLS-20.** Royalties 1,7% native. Mint manuel par CARNET pour les cars vérifiées. Métadonnées IPFS via Pinata ou Filebase. Badge "Certifié CARNET" dans la fiche voiture. Transfer P2P via Xaman signing.

**EURØP integration dans `carnet-payements`.** Worker Cloudflare étendu pour accepter EURØP en plus de XRP + RLUSD. Frontend mobile : 3e choix de paiement. Trivial niveau code, gros impact narratif.

**Vue financière étendue.** Table `app_config` avec breakdown coûts (Vercel, Anthropic, GH, domain, email). Cost coverage dynamique exact. Cashflow 13 semaines (standard Ripple Treasury).

**Statuts Association CARNET au J.O.** ~6 semaines de procédure. Compte bancaire asso (Crédit Mutuel, BNP, Qonto). Cabinet CSBC pour validation terms/privacy MiCA.

### Moyen terme — 3 à 12 mois

**Vue dealer profile.** Tableau de bord dealer-side, subset de l'admin filtré. KPIs propres : leurs cars, leurs ventes, leurs revenus, leur performance comparée à la moyenne plateforme.

**Whitelabel dealer pages.** URL `dealer.carnet.life/{slug}` ou `/{slug}` direct. Branding minimal autorisé (logo, couleurs secondaires) tout en gardant l'identité CARNET dominante.

**VIN tracking + NFT provenance.** Table `car_nfts` qui mappe VIN → NFT-ID XLS-20. Historique des transferts visible publiquement sur la fiche voiture. Devient l'équivalent natif d'un ECR (Exclusive Car Registry) pour les cars passées par Carnet.

**AMM XRPL pool XRP/EURØP.** Provide LP au démarrage avec ~5% de la treasury. Suivi du yield via dashboard admin. Auto-rebalance désactivé initialement, décisions manuelles.

**Multi-sig treasury wallet.** Migration du wallet `rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU` vers un setup multi-sig 3-of-5. Signataires : Sly + 4 membres asso (à formaliser dans les statuts).

**Dashboard public Transparence.** Page `/transparence` publique sur carnet.life. Live balance treasury, LP positions, derniers mouvements, liens explorer. Pas de login requis.

**API dealer pour automation.** REST endpoints pour les dealers qui veulent automatiser la mise à jour de leur stock depuis leur DMS (Dealer Management System).

### Long terme — 12+ mois

**Marketplace transactionnelle complète.** Boucle dealer activée. Smart contract logic sur XRPL pour split commission CARNET / dealer automatique. Workflow : annonce → achat via Xaman → transfer XLS-20 + paiement EURØP/XRP → split commissions automatique → audit on-chain.

**Crypto-native features.** Tipping entre utilisateurs (passionnés qui apprécient une fiche), fan tokens éventuels (pour des marques ou modèles iconiques), badges NFT pour collectionneurs avec X voitures référencées.

**Treasury management AI-assisted.** À la GSmart AI de Ripple. Suggestions de rebalance basées sur burn rate, volatilité XRP, opportunités AMM. Décision finale reste humaine multi-sig.

**Phase 3 ECR matching.** Intégration avec exclusivecarregistry.com (140k voitures exceptionnelles, chassis-level provenance, 41 auction houses). VIN matching entre scraped listings et ECR → chip "Référencée ECR" + score +5 + notifications collectionneurs. Approche hybride partenariat + registry propre.

**Internationalisation.** Multilingue NL/IT/DE/EN/ES. Dealers européens. Eventuellement US si Phase 3 ECR ouvre la porte.

---

## 6. Principes architecturaux

### Smart, Light, Clean, Robust, Scalable

**Smart.** Utiliser la blockchain pour la couche de pure-trust uniquement : paiements, royalties, provenance. Pas pour stocker des données qui ne nécessitent pas la décentralisation (descriptions de voitures, photos, etc., restent en Supabase + R2).

**Light.** XRPL fait le payment rail. Pas de surcouche custom, pas de smart contract Solidity équivalent (XRPL a son propre langage limité mais suffisant). Le code Carnet reste minimal, le travail lourd est délégué à des couches existantes (XRPL, Xaman, Schuman, Ripple).

**Clean.** Modèle de données simple : `cars + dealers + transactions + audit_log + donations`. Pas plus de tables que nécessaire. Une nouvelle feature ne doit pas demander 5 nouvelles tables — réfléchir à ce qui peut être JSONB dans une table existante.

**Robust.** RLS Supabase strict pour la séparation des données dealer. Aucun dealer ne peut voir les données d'un autre. L'admin voit tout via la fonction `is_admin()`. Audit log immuable pour traçabilité.

**Scalable.** La boucle dealer = N transactions par car_id sans changement de schéma. La table cars existante supporte 143k+ voitures (North Star). Supabase free tier tient ~30k, Pro $25/mois au-delà de 50k.

### Philosophie lean by design

On reste malin et gratuit le plus longtemps possible :
- Supabase free tier
- Cloudflare Workers free
- Vercel hobby
- Xaman Developer free

On améliore l'infra ($10/mo Custom Domain Supabase, plans payants) **uniquement si les revenus le permettent**. Donations + commissions enchères + royalties NFT financent les upgrades. Lean by design, pas par contrainte.

### Voix et identité CARNET (rappel)

5 couleurs : Encre noir, Papier crème, Orange Polo `#E85A1F`, Vert anglais `#1F4D2F`.
3 polices : Bodoni Moda italique, Cormorant Garamond, DM Mono.
Wordmark CARNET + point carré orange.
Radius 2px partout.

Voix : la voiture est "elle". Pas de superlatif. Sobre dans la forme, vivant dans le fond. Cible 25–65 ans, beau différent, rock, fun, sensations — pas gentleman driver UK/CH poussiéreux. Refs : Petrolicious, Magneto, The Drive.

Mantra : *"smart, light, clean"*.

CARNET en full caps quand on désigne l'app/asso/assistant. "carnet de bord" (concept) reste lowercase. URLs (carnet.life) lowercase. Function names dans leur casse d'origine.

---

## 7. Questions à formaliser avec le Cabinet CSBC

Maître S. Boufenara, Associé fondateur, www.csbc-avocats.com.

1. **Asso 1901 + commissions marketplace.** Une asso loi 1901 à but non-lucratif peut-elle percevoir des commissions de 1,7% sur les transactions des dealers ? Quel cadre comptable (fonds dédiés, ressources d'activités économiques) ? Plafonnement éventuel pour ne pas perdre le statut non-profit ?

2. **Treasury en digital assets + yield via AMM XRPL = MiCA OK ?** Détenir XRP et EURØP en treasury asso, provide liquidity sur AMM XRPL pour earn fees — quelle qualification réglementaire (investissement, activité commerciale, gestion de patrimoine) ? Reporting fiscal annuel ?

3. **NFT XLS-20 issuance par asso non-profit.** Émettre des NFT XLS-20 (certificats voitures vérifiées) avec royalties 1,7% natives — encadrement ? Statut juridique des NFT (titre numérique, jeton utilitaire, autre) ?

4. **KYC dealers.** Niveau de KYC obligatoire pour onboarder des dealers professionnels (Kbis, carte ID, vérification anti-blanchiment) ? Outsourcing recommandé (Sumsub, Onfido) ou auto-géré ?

5. **Reporting fiscal dealers via CARNET.** Carnet en tant qu'intermédiaire doit-il déclarer les transactions des dealers au fisc français ? Obligations PSAN si applicable ?

6. **Multi-sig wallet asso.** Comment formaliser dans les statuts les signataires du wallet multi-sig 3-of-5 ? Délégation, révocation, succession ?

7. **Dashboard public Transparence treasury.** Obligations légales d'exposer publiquement les flux treasury d'une asso non-profit ? Inversement, obligations de **ne pas** exposer certaines données (membres, donateurs nominatifs) ?

8. **Acheteur + Vendeur paient chacun 1,7%.** Modèle "double commission" sur la boucle dealer — cadre TVA, obligations fiscales pour les deux parties, déclaration ?

9. **Statuts CARNET au J.O.** Modèle de statuts adapté à une asso mixant mission culturelle (événements automobiles avec enfants), activité économique (marketplace commissionnée), et gestion treasury blockchain. Modèles existants ou rédaction sur mesure ?

10. **Limites de couverture coûts par les commissions.** Si les commissions couvrent largement les coûts, la treasury accumule du surplus. Réinvestissement dans les événements ? Plafond avant requalification fiscale ?

---

## 8. Sources et références

### Sources externes citées

- **EURØP MiCA-compliant Euro Stablecoin sur XRPL** — Schuman Financial / Ripple, mai 2025 :
  https://ripple.com/ripple-press/euro-stablecoin-on-xrp-ledger/

- **Ripple Treasury — 3 Steps to Cash Flow Management** :
  https://treasury.ripple.com/posts/3-steps-to-achieve-seamless-cash-flow-management-with-a-cash-management-solution

- **Grayscale + Artemis classify XRP as Store of Value**, janvier 2025 :
  https://thecurrencyanalytics.com/altcoins/grayscale-and-artemis-label-xrp-as-a-store-of-value-154404

- **Grayscale Research Insights Q2 2025** :
  https://research.grayscale.com/market-commentary/grayscale-research-insights-crypto-sectors-in-q2-2025

### Documents internes CARNET

- `Carnet_methode_et_principes_v1.md` — Framework Fibonacci/φ/Tesla 3-6-9, intellectual honesty non-négociable.
- `docs/brief_extract_features_v2.md` — Multilingual rules-based parser NL/FR/DE/IT/EN.
- `docs/brief_mission_b_bis_de_extraction.md` — Extraction `de` (description) backfill.
- `SESSION_HANDOFF_2026_05_08.md` — État Sprint B.1 Auth Supabase.

### Repos

- Frontend : https://github.com/Vinci75000/autoradar (carnet.life, index.html PWA)
- Scraper : https://github.com/Vinci75000/autoradar-scraper (Python modulaire)

### Infra

- DB : Supabase Frankfurt, project `qqbssqcuxllmtapqkmkz`
- Workers Cloudflare : `carnet-payements.schaillout.workers.dev`, `carnet-photos-proxy.schaillout.workers.dev`
- R2 bucket : `carnetphotos`
- Wallet CARNET XRPL : `rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU`

---

## Annexe — Schéma SQL prévisionnel boucle dealer

Tables à créer dans les sprints à venir, pour référence anticipée :

```sql
-- Sprint Dealers Fondation
CREATE TABLE public.dealers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug            TEXT UNIQUE NOT NULL,
  name            TEXT NOT NULL,
  legal_name      TEXT,
  email           TEXT UNIQUE NOT NULL,
  phone           TEXT,
  country         TEXT,
  city            TEXT,
  website         TEXT,
  wallet_xrpl     TEXT,
  tier            TEXT NOT NULL DEFAULT 'free',
  commission_rate NUMERIC NOT NULL DEFAULT 1.7,
  kyc_status      TEXT NOT NULL DEFAULT 'pending',
  joined_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  metadata        JSONB DEFAULT '{}'::jsonb
);

ALTER TABLE public.cars ADD COLUMN dealer_id UUID REFERENCES public.dealers(id);

-- Sprint 2 NFT XLS-20
CREATE TABLE public.car_nfts (
  car_id        UUID PRIMARY KEY REFERENCES public.cars(id),
  nft_id_xrpl   TEXT UNIQUE NOT NULL,
  vin           TEXT,
  minted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  minted_by     UUID REFERENCES public.profiles(id),
  metadata_uri  TEXT,
  is_certified  BOOLEAN NOT NULL DEFAULT false
);

-- Long terme : Marketplace transactionnelle
CREATE TABLE public.transactions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  car_id            UUID NOT NULL REFERENCES public.cars(id),
  seller_id         UUID REFERENCES public.dealers(id),
  buyer_wallet      TEXT NOT NULL,
  amount            NUMERIC NOT NULL,
  currency          TEXT NOT NULL,
  commission_carnet NUMERIC NOT NULL,
  commission_dealer NUMERIC NOT NULL,
  tx_hash_xrpl      TEXT UNIQUE NOT NULL,
  status            TEXT NOT NULL DEFAULT 'pending',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Config dynamique (cost coverage, treasury rules)
CREATE TABLE public.app_config (
  key         TEXT PRIMARY KEY,
  value       JSONB NOT NULL,
  description TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by  UUID REFERENCES public.profiles(id)
);

INSERT INTO public.app_config (key, value, description) VALUES
  ('monthly_costs_breakdown', '{"vercel": 0, "anthropic": 50, "gh_actions": 2, "domain": 1, "email": 10, "supabase": 0, "cloudflare": 0, "xaman": 0}'::jsonb, 'Coûts mensuels en EUR par poste'),
  ('treasury_allocation', '{"operational_months": 12, "buffer_months": 3, "xrp_amm_pct": 20}'::jsonb, 'Règles d''allocation treasury'),
  ('north_star_target', '{"cars_active": 143000, "deadline": "2027-12-31"}'::jsonb, 'Objectif catalogue');
```

---

*Document vivant. À mettre à jour à chaque sprint livré ou pivot stratégique.*

*— CARNET, Roadmap Rêve v1, 12 mai 2026.*
