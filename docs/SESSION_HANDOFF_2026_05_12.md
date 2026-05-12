# CARNET — Session Handoff (12 mai 2026)

> À coller en premier message de la prochaine session pour reprendre en cohérence totale.

---

## 0. TL;DR

**CARNET** (frontend `carnet.life`, brand) / **AutoRadar** (backend scraper, ~24 335 cars actives, ~16.4% du North Star 143k).

- Builder solo : Sly (cycle 23h–6h normal, **ne jamais commenter timing/fatigue**).
- Entité juridique : **Association loi 1901 à but non lucratif**, bénévoles uniquement.
- Stack : XRPL pur + XRP + RLUSD + EURØP + MiCA-compliant + non-custody.
- Vision finale : **24/7, les 143 000 meilleures voitures curatées d'Europe en ligne — annonces et enchères, scrapées et propres CARNET, tout le process en autopilot, business model aligné sur Ripple.**
- Mantra : *smart, light, clean, robust, scalable.*

Référence pérenne de la vision : `docs/ROADMAP_REVE.md` (frontend repo, commit `3b48391`).

---

## 1. Identité produit

### Brand
- **Backend** : AutoRadar (code + DB)
- **Frontend** : CARNET (UI publique, full caps quand on désigne l'app/asso/assistant)
- **Live prod** : https://carnet.life (Vercel DNS, service `autoradar-q4s9`)
- **Admin prod** : https://carnet.life/admin (OTP magic link only, role='admin')

### North Star
**143 000 voitures actives curatées 24/7 en Europe**, alimentées par 4 canaux :

| Canal | Type | Statut |
|---|---|---|
| Annonces scrapées | Fixed-price | ✅ Live (24k+ cars) |
| Enchères scrapées | Bidding | 🟡 PASSE 1+2 livrées, PASSE 3 frontend à venir |
| Annonces propres CARNET (`is_autoradar=true`) | Fixed-price | ⏳ À implémenter |
| Enchères propres CARNET | Bidding | ⏳ Phase ultérieure |

### Acronymes officiels
- **FR** : Carnet Automatisé Référentiel du Négoce Et de la Transparence
- **EN** : Curated Automotive Records Network for Exchange and Trust

### Cible utilisateur
25–65 ans, beau différent, rock, fun, sensations. Refs ton : Petrolicious, Magneto, The Drive. **PAS gentleman driver UK/CH poussiéreux.**

### Charte v8 (stricte)
- **5 couleurs** : Encre `#0A0A0A`, Papier `#F4F1EA`, Papier pur `#FAFAF7`, Orange Polo `#E85A1F`, Vert anglais `#1F4D2F`
- **3 polices** : Bodoni Moda 500 italique (display), Cormorant Garamond 300/400 (body), DM Mono (chiffres)
- **Wordmark** "CARNET" + point carré orange. Border-radius 2px partout.
- **Voix** : la voiture est *"elle"*. Pas de superlatif. Sobre forme, vivant fond.
- **Royalties NFT XLS-20** : 1,7% (PAS 2%)

---

## 2. État technique actuel (12 mai 2026, 23h)

### Repos & commits HEAD

| Repo | GitHub | Local | HEAD commit |
|---|---|---|---|
| Frontend | `Vinci75000/autoradar` | `~/Code/autoradar/frontend/` | `3b48391` (ROADMAP_REVE v1) |
| Scraper | `Vinci75000/autoradar-scraper` | `~/Code/autoradar/scraper/` | `adc11fa` (Phase 2 enchères PASSE 1+2) ou plus récent |

### DB Supabase Frankfurt

- Project : `qqbssqcuxllmtapqkmkz`
- API : https://qqbssqcuxllmtapqkmkz.supabase.co
- Dashboard : https://supabase.com/dashboard/project/qqbssqcuxllmtapqkmkz
- Stats : ~24 335 cars actives · 90 marques · 26 sources · 3 259 premium (>100k€) · 16.4% du North Star
- Tables clés : `cars`, `cars_archive`, `donations`, `donations_public_stats` (view), `car_fingerprints`, `data_lineage`, `admin_audit_log`, `profiles`
- Schéma `cars` : `mk, mo, yr, km, px, fu, ge, ci, co, lat, lng, src, src_url, age_label, ow, opts, sc, ve, ch, ss, hs, status, is_autoradar, is_auction, auction` (JSONB)
- **Pas** de colonne `title` ni `source` (utiliser `mo` et `src`)
- FK delete order : `data_lineage` → `car_fingerprints` → `cars`

### Tests scraper
**724/724 verts** (CI `tests.yml`).

### GitHub Actions actives (4+3 enchères)

| Cron | Fréquence | Rôle |
|---|---|---|
| `dealers_cron` | 00h + 12h UTC | Scrape dealers + LLM hook ON + Sentry ON |
| `green_cron` | 22h UTC | Sources green tier |
| `yellow_cron` | 04h UTC | Sources yellow tier |
| `wash_cron` | 03h UTC | Auto-archivage annonces expirées (clean_expired.py) |
| `status_sweeper` (enchères) | toutes les 30min | Maj statuts auctions LIVE/UPCOMING/SOLD |
| `live_refresh` (enchères) | toutes les 4h | Rafraîchit auctions LIVE via registry |
| `archive` (enchères) | 02h UTC | Archive auctions terminées |

### Infra Cloudflare

| Service | URL |
|---|---|
| Photos proxy | `carnet-photos-proxy.schaillout.workers.dev` |
| R2 bucket | `carnetphotos` (cache 1 an, fallback SVG CARNET) |
| Payments worker | `carnet-payements.schaillout.workers.dev` (**TYPO FRANÇAIS "payements" CONSERVÉE**) |

### Comptes & wallets

- Admin : `schaillout@gmail.com` · profile.id `ca903a9f-b247-450f-8192-6f2b2eca9452` · role `admin`
- SMTP : `auth@carnet.life` (Namecheap Private Email, DKIM/SPF/DMARC pass)
- Contact : `contact@carnet.life`
- Wallet CARNET XRPL : `rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU`
- Coûts mensuels actuels : **~70€** (Anthropic API 50 + email 10 + GH 2 + domain 1 + reste = free tier)

### Auth
- Magic link via Supabase Auth + SMTP custom Namecheap
- OAuth Google projet "Carnet" (`89811153795`, mode Testing, External)
- `handle_new_user` trigger défensif SECURITY DEFINER

---

## 3. Stack & infrastructure

### Frontend
- `index.html` ~5500 lignes, ~270k bytes, PWA avec Service Worker, Vercel hosting
- `admin.html` v3d : 12 KPIs drilldowns + 3 nouveaux (CARNET listings + Enchères + Revenus) + cost coverage + courbes
- DNS : NS Vercel (`ns1/ns2.vercel-dns.com`), MX/SPF Private Email
- DKIM/SPF/DMARC configurés (DMARC `p=none` actuellement)

### Backend scraper
- Python modulaire, extractors registry (`pkgutil __init__` auto-discovery)
- `phase_a_scraper.py` engine principal, `extract_symfio.py`, `extract_hollmann.py`, `extract_rivamedia.py`, etc.
- `dedup.py` 3-level (URL match / fingerprint cross-source / content_hash)
- `feature_extractor.py` v1 (26 features 7 axes) + v2 rules+LLM hybride
- `llm_extractor.py` v2.1 slim output −60% tokens, Haiku 4.5
- Routing LLM : `de>800` + no bool V1 + (collector≥25y OR px≥60k)

### Mobile v6.15 (12/5/26 PM)
- Carnet mobile LIVE sur Supabase Frankfurt
- Tri sc DESC, batch 42, photos via Cloudflare Worker + R2 lazy og:image
- Garage owned/wishlist split
- Auto wash backend pushé scraper main (`clean_expired.py` + `wash_cron` + 18 tests)
- **PENDING** : GH Secret `SUPABASE_SERVICE_KEY` à set + 1er run prod wash_cron

### Treasury (vision future, pas encore live)
- XRP-majoritaire (Grayscale + Artemis Jan 2025 = store of value)
- EURØP-opérationnelle (Schuman Financial, MiCA-compliant, ACPR-licensed)
- Allocation cible : 12-15 mois runway EURØP + buffer 3 mois + surplus XRP (dont 20% en AMM XRPL pool XRP/EURØP)

---

## 4. Ce qui a été livré (chronologie inverse)

### 12 mai 2026 (cette session)
- ✅ **Admin v3d** (commit `a665c6c`) : 12 KPIs cliquables avec drilldowns smart, insights par niveau (alert/warn/ok), recommandations 1-click exécutables, 3 nouveaux KPIs (CARNET listings + Enchères + Revenus), cost coverage ratio dynamique, courbes stock SVG
- ✅ **ROADMAP_REVE.md v1** (commit `3b48391`, 544 lignes, 29.5 KB) : vision pérenne 3 couches + treasury XRP-majoritaire + 143k North Star 4 canaux + alignement Ripple business model + DDL SQL prévisionnel en annexe + 10 questions Cabinet CSBC

### 12 mai 2026 (matin/midi)
- ✅ **CARNET Sprint 1 backend** : Worker Cloudflare `carnet-payements` (3 endpoints donation/create + status/uuid + webhook), Supabase table `donations` + RLS + view `donations_public_stats`, v6.18 frontend Xaman branché real
- ✅ **terms.html + privacy.html + support.html v1.1** mis à jour
- ✅ **Carnet mobile v6.15** : Supabase Frankfurt LIVE, photos Cloudflare Worker + R2, Garage owned/wishlist split, auto wash backend
- ✅ **OTP auth admin** debug complet : 4 SQL fixes appliqués (`get_source_stats` FILTER, RLS policies admin pour donations/audit_log, `get_admin_kpis` schéma corrigé)

### 11 mai 2026
- ✅ **Phase 2 Vue Enchères PASSE 1+2** (commit `adc11fa`) : `cars + is_auction + auction JSONB + cars_archive`, AuctionExtractor, classictrader.py HYBRID-aware, 3 crons live, auction_registry.py source-agnostic
- ✅ **A4.3 cc + A4.2 cd + fix Other** (commit `877ea92`) : Inertia.js cc 500 URLs, Drupal field-name cd 2-lvl sitemap, full run cd nuit 1927 inserted/35 err (CHECK fu/ge Other → None), DB ~24268 cars

### 8 mai 2026
- ✅ **Auth Sprint B.1** (commits `eef06e8`, `41e5148`) : `handle_new_user` défensif race FK, SMTP custom Namecheap DKIM/SPF/DMARC pass, UI Auth modal + magic link + OAuth Google, sync favoris/collections post-login OK
- ✅ **Extractor architecture S0+S1+S2.1+SA2** : ABC base + registry + sniff + 27 dealers-de.yaml + CHECK constraints, Symfio V1.1 variants A/B 40 tests + cron 03h UTC, bridge +9 cars, Hollmann html_only DE tier 1 +114 cars score 84 + 79 tests, dynamic dispatch pipeline + `pkgutil __init__` auto-discovery
- ✅ **Phase A v2 A1+A3** : 5 dealers operational +82 cars (DPM/Exclusive/RS/MZ/Monaco Infinity), découverte plateforme Rivamedia flux RSS standardisé +188 cars, fix transverse `cars_fu_check` PHEV→Hybride
- ✅ **Sprint A2 cleanup** (commit `c1680b9`) : 15 dealers DE manual_inspect classifiés, classic-trader URL fixée /de/automobile (puis recheck 11/5 : pivot enchères pures = candidat Phase 2)

### 5-6 mai 2026
- ✅ **Mission B → B-quinquies** : Mission B `7a87e68` tag v1.0 feature_extractor V1 26 features 7 axes 92 tests + backfill 3818, B-ter extract_lesanciennes 51 tests, P1a unique idx cars_src_url_active_uniq_idx, P1b/B-quater insert_car + score/chips_from_features + feat_score INT + feat_chips JSONB, B-quinquies `de` coverage 11→80% via JSON-LD + dict_to_carlisting

### LLM Phases 1→6
- ✅ Hook ON pour dealers cron, routing intelligent, backfill 432 cars at 0.76€ (−93% vs estimate), 129/129 tests, budget target <50€/month

### Modèles canonical referential (B.6+B.7, 9/5/26)
- ✅ Multi-source DBpedia 1587 + NHTSA + Wikipedia EU 1247 + Manual Porsche/MB/BMW, Porsche by generation (992/991/997/996/993/964), `refresh_cote_segments()` v5, true_match 95.3%, 14 Porsche segments éligibles

---

## 5. Ce qu'il reste à faire (priorisé)

### 🔥 Court terme — Sprints prochains (1-3 mois)

#### Sprint Dealers Fondation
**Tout prêt dans `docs/ROADMAP_REVE.md` annexe SQL.** DDL `dealers` + `dealer_stats` matérialisée + `cars.dealer_id`. Vue admin "Dealers" basique. Permet de commencer à attribuer les cars scrapées aux dealers correspondants.

#### Sprint 2 NFT XLS-20
Royalties 1,7% native. Mint manuel par CARNET pour cars vérifiées. Métadonnées IPFS via Pinata. Badge "Certifié CARNET" dans la fiche voiture. Transfer P2P via Xaman signing.

#### EURØP integration
Worker Cloudflare `carnet-payements` étendu pour accepter EURØP en plus de XRP + RLUSD. Frontend mobile : 3e choix de paiement.

#### Phase 2 Vue Enchères PASSE 3 (frontend)
Tab "Enchères" avec 3 sections LIVE / UPCOMING / SOLD. Champs : `lot_number, estimate_low/high, bid_current, closes_at, reserve_met`. Backend déjà prêt (PASSE 1+2 livrées).

#### Vue financière étendue (admin)
Table `app_config` SQL avec breakdown coûts (Vercel 0, Anthropic 50, GH 2, domain 1, email 10, Supabase 0, Cloudflare 0, Xaman 0). Cost coverage dynamique. Cashflow projeté 13 semaines (standard Ripple Treasury).

### 📋 Administratif urgent

- ☐ **Statuts officiels Asso CARNET au J.O.** (~6 semaines de procédure)
- ☐ **Compte bancaire Asso** (Crédit Mutuel / BNP / Qonto pour assos)
- ☐ **Cabinet CSBC consultation** (Maître S. Boufenara, www.csbc-avocats.com) sur les **10 questions du ROADMAP_REVE.md §7**
- ☐ **GH Secret `SUPABASE_SERVICE_KEY`** à set + 1er run prod `wash_cron`
- ☐ **Brandfetch whitelist** carnet.life (extend BRANDFETCH_VERIFIED marque par marque après test visuel)

### 🛠 Avant launch public

- ☐ **Custom Domain Supabase** $10/mo → `auth.carnet.life` (résout branding consent screen Google, URL propre dans emails) — **DIFFÉRÉ lean philosophy, upgrade quand revenus permettent**
- ☐ **DMARC** `p=none → p=quarantine` après 1-2 sem `rua`
- ☐ **Template Supabase Auth** : customiser branding CARNET + version text/plain réduire score spam
- ☐ **Privacy/Terms** validation Cabinet CSBC (asso 1901 + commissions marketplace + treasury digital assets)

### 🔧 Tech debt scraper (backlog)

- ☐ `phase_a scrape-single --limit` no-op fetched=0
- ☐ Sniff classica URL vide
- ☐ Lambo Genève + Carugati JS Cloudflare → DevTools Network XHR audit pour API endpoint
- ☐ Generic parser `cards[:25]` + CSS audit
- ☐ Mechatronik photo regex `_processed_/csm_` + 2/3 dropped silently
- ☐ Elferspot 403 → recheck Playwright stealth
- ☐ A2.b custom extractors (10 DE dealers backlog) : mechatronik / thiesen×2 / hk-engineering / mirbach / hemmels / cargold / cog / gassmann / pyritz
- ☐ 18 dealers manual_inspect → ready (sniff + ajust selectors)
- ☐ Sprint A4 marketplaces (classic-trader EU ~15k stock, ou désormais enchères)
- ☐ `de` description backfill AutoScout24 (manual séparé — JAMAIS fetch détail en cron)
- ☐ LLM hook canary validation pour green/yellow sources puis extend après 1 sem
- ☐ Architectural debt : consolider `_extract_make` (scraper.py) vs `normalize_brand` (phase_a_scraper.py)
- ☐ MAKES_OTHER frontend extension
- ☐ B.8 trim Alfa/LR/Jaguar, tuners Brabus/Mansory/Singer/RUF/Alpina

### ⚠️ Échéances tech

- ☐ **GH Actions Node 20→24** deprecation **juin 2026** (URGENT)
- ☐ `feature_extractor` v2 step 2 : multilingual rules parser NL/FR/DE/IT/EN
- ☐ `feature_extractor` v2 step 3 : SQL migration (7 LLM output columns + partial index)

### 🌅 Long terme (12+ mois)

- Marketplace transactionnelle complète (boucle dealer activée, split commission CARNET/dealer automatique)
- Crypto-native (tipping, fan tokens, badges NFT collectionneurs)
- Treasury management AI-assisted (à la GSmart AI Ripple)
- **Phase 3 ECR integration** : exclusivecarregistry.com, 140k cars exceptionnelles, VIN matching scraped vs ECR → chip "Référencée" + score +5 + notifications
- Internationalisation (multilingue NL/IT/DE/EN/ES + dealers européens + US)

### 📱 Mobile v6+ (refonte φ, 7 lots)

1. Sheets détail (GarageCar / Match / Auction)
2. Hero + KPI + TabBar
3. Boutons CTA + secondary
4. Sheets création (form Ajout voiture / Nouvelle alerte)
5. Empty states + banners
6. Form components (inputs / autocompletes / ticks)
7. Listings / Profil / Réglages

---

## 6. Mega cleanup — checklist actionnable

Pour `clean light, robust, scalable, very very cheap, top app categorie` :

### A. Cleanup local machine (~/Downloads + /tmp)

Sly à lancer un par un, valider à chaque étape :

```bash
# 1. Voir ce qu'on a accumulé dans Downloads (admin*.html, scripts patch_*, etc.)
ls -lt ~/Downloads/ | head -30

# 2. Ranger les vieux admin.html (garder seulement le dernier)
mkdir -p ~/Code/autoradar/_archives/admin_versions
mv ~/Downloads/admin_*.html ~/Code/autoradar/_archives/admin_versions/ 2>/dev/null
# Garder uniquement ~/Downloads/admin.html actuel

# 3. Ranger les scripts patch_*.py
mkdir -p ~/Code/autoradar/_archives/patches
mv ~/Downloads/patch_*.py ~/Code/autoradar/_archives/patches/ 2>/dev/null
mv ~/Downloads/apply_*.py ~/Code/autoradar/_archives/patches/ 2>/dev/null

# 4. Nettoyer /tmp (logs anciens, snapshots)
ls -lt /tmp/*.log /tmp/cd_*.log /tmp/full_*.log 2>/dev/null | head
# Examiner avant de supprimer
# rm /tmp/cd_full_*.log  # une fois validés

# 5. Vérifier .gitignore frontend
cat ~/Code/autoradar/frontend/.gitignore

# 6. Vérifier .gitignore scraper
cat ~/Code/autoradar/scraper/.gitignore
```

### B. Cleanup repo frontend (`Vinci75000/autoradar`)

```bash
cd ~/Code/autoradar/frontend

# 1. Voir structure actuelle
ls -la
tree -L 2 -I 'node_modules|.git' 2>/dev/null || find . -maxdepth 2 -not -path '*/\.*'

# 2. Vérifier qu'il y a un README.md à jour
cat README.md 2>/dev/null || echo "MANQUE: README.md à créer"

# 3. Structure cible recommandée :
# .
# ├── README.md             ← présentation CARNET + dev setup
# ├── index.html            ← app PWA principale
# ├── admin.html            ← console admin v3d
# ├── manifest.json
# ├── sw.js                 ← service worker
# ├── icons/                ← PWA icons
# ├── docs/
# │   ├── ROADMAP_REVE.md   ← vision pérenne ✅ DÉJÀ LÀ
# │   ├── SESSION_HANDOFF_2026_05_12.md ← celui-ci
# │   ├── ARCHITECTURE.md   ← à créer
# │   └── CHANGELOG.md      ← à créer (récap commits par sprint)
# ├── terms.html
# ├── privacy.html
# ├── support.html
# ├── vercel.json
# └── .gitignore

# 4. Auditer poids index.html
wc -c index.html admin.html
# index.html ~270k bytes attendu, admin.html ~148k bytes

# 5. Vérifier qu'aucun snapshot/log/backup oublié n'est dans le repo
find . -name "*.bak" -o -name "*.before_*" -o -name "*_old*" | head
```

### C. Cleanup repo scraper (`Vinci75000/autoradar-scraper`)

```bash
cd ~/Code/autoradar/scraper

# 1. Audit dossier
du -sh */ 2>/dev/null | sort -h

# 2. Vérifier .gitignore (snapshots, logs, _archives, *.before_*)
grep -E "snapshot|logs|archive|before_|venv" .gitignore

# 3. Tests passent toujours ?
source venv/bin/activate && pytest -q 2>&1 | tail -5

# 4. Auditer extractors actifs
ls extractors/*.py | wc -l
ls config/*.yaml 2>/dev/null | head
```

### D. Audit coûts & scaling (very very cheap)

| Service | Plan actuel | Limite free | À 143k cars |
|---|---|---|---|
| Supabase | Free tier | 500 MB DB / 5 GB egress | Pro $25/mo dès ~50k cars |
| Vercel | Hobby | 100 GB bandwidth/mo | Tient encore largement |
| Cloudflare Workers | Free | 100k req/jour | Tient |
| R2 bucket carnetphotos | Free | 10 GB stockage / 1M req/mo | Probablement OK |
| Anthropic API | Pay-as-you-go | — | ~50€/mo cap actuel |
| GitHub Actions | Free | 2000 min/mo public repos | Tient (private OK aussi à ce niveau) |
| Xaman Developer | Free | — | OK |
| Domain `carnet.life` | Annuel | — | ~10€/an |
| Email Namecheap PE | ~10€/mo | — | OK |

**Coût mensuel actuel : ~70€** (Anthropic 50 + email 10 + reste = négligeable).

À l'approche de 50k cars, prévoir Supabase Pro $25/mo. Surveillance via admin v3d "Cost coverage ratio" KPI Revenus.

### E. Optimisations scaling pour 143k cars (anticipation)

- **Index DB** : vérifier index sur `cars(status, created_at)`, `cars(mk, mo)`, `cars(px)`, `cars(sc)` — KPIs admin doivent rester sub-seconde même à 143k
- **Pagination** : cap 999/1000 par page Supabase, paginer systématiquement (déjà appliqué dans `dedup.py`)
- **R2 cache** : cache photos 1 an déjà en place ✅
- **Lazy loading** : `og:image` 70% succès actuel sur mobile ✅
- **Materialized views** : `dealer_stats` viendra avec Sprint Dealers, refresh nightly via cron
- **CDN Vercel** : déjà en place ✅
- **Service Worker cache-busting** : déjà SW register dans index.html, mais **à valider** que update onglet ne sert pas vieille version

### F. Structure docs/ à créer

```
docs/
├── ROADMAP_REVE.md            ← vision pérenne ✅
├── SESSION_HANDOFF_2026_05_12.md ← celui-ci
├── ARCHITECTURE.md            ← à créer : 3 couches, flow données, RLS Supabase
├── CHANGELOG.md               ← à créer : récap par sprint avec commits
├── DEPLOYMENT.md              ← à créer : comment deploy + rollback
├── brief_extract_features_v2.md  ← scraper repo
└── brief_mission_b_bis_de_extraction.md ← scraper repo
```

### G. .gitignore propre (recommandation)

**Frontend** (`~/Code/autoradar/frontend/.gitignore`) :
```
.DS_Store
node_modules/
.env
.env.local
*.log
.vercel
_archives/
*.bak
*.before_*
```

**Scraper** (`~/Code/autoradar/scraper/.gitignore`) :
```
.DS_Store
__pycache__/
*.pyc
venv/
.env
.env.local
*.log
snapshots/
logs/
_archives/
*.bak
*.before_*
```

---

## 7. Conventions de travail (à respecter)

### Style Sly
- Pédagogique step-by-step (étape 0/1/2/3, validation, why)
- **VELOCITY mode** : "do it" / "fais-le" / "go" / "block par block coller direct go" → end-to-end delivery sans grep/probing intermédiaire
- Pattern : upload (1 msg) → patch local `str_replace` → present file via `present_files` + 1 mini shell instruction
- No long explanations sauf demandé
- Debug ensemble, don't rewrite. Backup avant destructif.
- Self-relevance test : produit doit être **FUN pas poussiéreux**
- **NE JAMAIS** mentionner timing/fatigue/heure tardive (cycle 23h-6h normal)
- "Best UX possible, don't be annoying" — zero friction, voix CARNET sobre/premium

### Debug protocol (Sergio)
- TOUJOURS lire logs/console output **fully and carefully** avant répondre
- Pas de "victory" prématurée si chiffres ne matchent pas
- Lire output ligne par ligne, flag suspicious numbers immediately
- Une diagnose claire par tour, pas de revirement

### Brand rules
- **CARNET full caps** quand on désigne l'app/asso/assistant
- "carnet de bord" (concept) reste lowercase
- URLs (carnet.life) lowercase
- Function names dans leur casse d'origine

### zsh conventions (AutoRadar)
1. **NEVER** `path` (lowercase) comme var shell — tied to `$PATH`, silently overwrites. Use `pth`/`p`/`url`. Same pour `cdpath`/`fpath`/`manpath`.
2. Never `#` inline (as argument)
3. Never `!r` non quoté (history expansion). Heredoc `<<'EOF'` quoted ou `repr()`
4. `python -u` mandatory in pipes (sinon stdout block-buffered, output invisible)
5. Tests : `sys.path.insert(0, .parent.parent)` AT TOP, valider via `pytest` pas `python -c`, `load_dotenv()` via frame → scripts dans le repo pas `/tmp/`

### Schéma DB cars (rappel)
- Colonnes : `mk, mo, yr, km, px, fu, ge, ci, co, lat, lng, src, src_url, age_label, ow, opts, sc, ve, ch, ss, hs, status, is_autoradar, is_auction, auction`
- **Pas** de colonne `title` ni `source`
- FK delete order : `data_lineage` → `car_fingerprints` → `cars`
- AutoScout24 : JAMAIS fetch détail en cron, parser `__NEXT_DATA__` page liste seul
- Pagination Supabase : cap 999/1000, paginer pour scale 143k
- `yr` CHECK constraint : 1900–year+1
- `fu`/`ge` CHECK : 'Other' → None (bug récurrent)

### Méthode et principes
Référence : `Carnet_methode_et_principes_v1.md` — framework Fibonacci/φ/Tesla 3-6-9.
- Sacred geometry foundation
- Pour chaque principe : math solid / structurellement utile / symboliquement respectable
- 3 passes deliverable normal, 6 important, 9 fondamental
- Intellectual honesty non-négociable

---

## 8. Notes critiques (pièges connus)

### Service Worker zombie
`index.html` register un SW qui CACHE l'ancienne version. **TOUJOURS tester en navigation privée après push pour bypass le SW de session.**

Si Sly se plaint de bouton invisible / JS broken :
```javascript
navigator.serviceWorker.getRegistrations().then(regs => regs.forEach(r => r.unregister()));
caches.keys().then(keys => keys.forEach(k => caches.delete(k)));
```
Puis reload onglet fermé/réouvert.

### CSS variables index.html (legacy, pas v8)
`--gc` (vert primary), `--text`, `--text2`, `--text3`, `--bg`, `--bg2`, `--border`, `--border2`, `--rsm`, `--r`, `--sans`, `--mono`. La charte v8 stricte (Encre/Papier/Orange/Vert anglais) **n'est pas encore appliquée dans tout le CSS** — sprint dédié à prévoir.

`admin.html` utilise déjà v8 (`--encre`, `--papier`, `--orange-polo`, `--vert-anglais`).

### `handle_new_user` race
EXCEPTION WHEN OTHERS pour ne pas planter signup auth.users si profiles INSERT échoue. Si user créé dans auth.users mais pas dans profiles → fallback INSERT manuel ou hook frontend post-login.

### OAuth Google consent screen
Affiche `qqb...supabase.co` au lieu de "Carnet" tant que pas Custom Domain Supabase ($10/mo). C'est inhérent à la sécurité Google.

### Bouton "Connexion" invisible
Sur `index.html`, `display:none` initial. C'est `updateAuthUI()` qui l'inverse. Si pas appelé (erreur JS amont) → bouton invisible.

### Lambo Genève / Carugati
Domain confirmé `autostradasport.de` (no hyphen pour Autostrada Sport). JS Cloudflare anti-bot → requires visual DevTools XHR audit pour API endpoint.

### `de` field coverage
Était 10.8% (claimed 88%), jumped to ~78-80% après patch `phase_a_scraper.py:_vehicle_to_car()` (stop discarding JSON-LD description field).

### Insolvent dealers à exclure
- Kienle (Heimerdingen, Oct 2023, acquis par Mercedes-Benz Heritage Feb 2024)
- Auto Salon Singen (July 2025, Ferrari deposit fraud)

### Brand mapping
- `"corvette"` → `"Chevrolet"` (pas "Chevrolet Corvette")
- `"chevrolet"` → `TIER_LUXURY` (Escalade-V pricing rationale, same as Cadillac/Lincoln)

### Symfio discovery
Canonical listing URL : `/de/cars-for-sale.html`. `/de/inventory` et `/fahrzeugsuche.html` retournent 0 detail URLs malgré HTTP 200. `__NEXT_DATA__` hydration block à offset ~541k = future optimization (1 fetch = N cars).

### Rivamedia platform
White-label, flux RSS standardisé, `extract_rivamedia.py` = pattern 1 fetch = N cars.

---

## 9. Documents de référence

### Dans frontend repo (`~/Code/autoradar/frontend/docs/`)
- `ROADMAP_REVE.md` — vision pérenne 3 couches + treasury + sprints ✅ commit `3b48391`
- `SESSION_HANDOFF_2026_05_12.md` — ce document

### Dans scraper repo (`~/Code/autoradar/scraper/docs/`)
- `brief_extract_features_v2.md` — multilingual rules parser
- `brief_mission_b_bis_de_extraction.md` — `de` field backfill
- `Carnet_methode_et_principes_v1.md` — framework Fibonacci/φ/Tesla 3-6-9

### Liens externes clés
- EURØP MiCA-compliant : https://ripple.com/ripple-press/euro-stablecoin-on-xrp-ledger/
- Ripple Treasury Cash Management : https://treasury.ripple.com/posts/3-steps-to-achieve-seamless-cash-flow-management-with-a-cash-management-solution
- XRP Store of Value (Grayscale + Artemis) : https://thecurrencyanalytics.com/altcoins/grayscale-and-artemis-label-xrp-as-a-store-of-value-154404
- Repos : https://github.com/Vinci75000/autoradar (frontend), https://github.com/Vinci75000/autoradar-scraper (scraper)
- Supabase Dashboard : https://supabase.com/dashboard/project/qqbssqcuxllmtapqkmkz
- GH Actions : https://github.com/Vinci75000/autoradar-scraper/actions
- Cabinet CSBC : https://www.csbc-avocats.com (Maître S. Boufenara)

---

## 10. Reprise en nouvelle session

### Exemples de premier message selon la cible

**"On attaque Sprint Dealers Fondation"** → DDL SQL prêt dans `docs/ROADMAP_REVE.md` annexe. Plan : 1) appliquer migration SQL `dealers + dealer_stats matérialisée + cars.dealer_id` 2) RLS policies dealers 3) Vue admin "Dealers" basique (liste + détail + edit) 4) Cron refresh nightly `dealer_stats`.

**"On attaque Sprint 2 NFT XLS-20"** → Royalties 1,7% native, mint manuel CARNET pour cars vérifiées. Plan : 1) Worker Cloudflare mint endpoint 2) Métadonnées IPFS via Pinata 3) Table SQL `car_nfts` (mapping VIN ↔ NFT-ID) 4) Badge "Certifié CARNET" dans fiche voiture frontend 5) Transfer P2P via Xaman signing.

**"On attaque EURØP integration"** → Worker `carnet-payements` étendu. Plan : 1) Lire doc Schuman EURØP issuance 2) Ajouter handler EURØP au worker 3) Frontend mobile : 3e bouton paiement 4) Test E2E payload donation EURØP.

**"On attaque Phase 2 Vue Enchères PASSE 3 frontend"** → Tab "Enchères" avec 3 sections. Plan : 1) Routing Tab dans `index.html` 2) Fetch Supabase `is_auction=true` groupé par status 3) Card design 3 sections distinctes 4) Pagination si volume élevé.

**"On attaque Vue financière étendue"** → Table `app_config` SQL + breakdown coûts. Plan : 1) CREATE TABLE `app_config` + INSERT defaults (DDL dans ROADMAP §Annexe) 2) RPC `get_admin_finances()` 3) KPI "Revenus" admin enrichi avec breakdown coûts 4) Cashflow 13 semaines projection.

**"On range encore plus"** → Continuer cleanup §6 + créer `docs/ARCHITECTURE.md` + `docs/CHANGELOG.md`.

**"On débriefe avec Cabinet CSBC"** → Préparer dossier avec les 10 questions du `ROADMAP_REVE.md §7`, joindre statuts Association draft + flow paiements + capture admin.

**Sans contexte spécifique** → Mini-status : `git log --oneline -10` côté frontend + scraper, dernière DB stats via admin, ce que tu veux attaquer.

### Premier acte recommandé en nouvelle session
1. Coller ce SESSION_HANDOFF en premier message
2. Préciser le sprint visé (parmi ceux du §10)
3. Confirmer commits HEAD à jour (`git log --oneline -3` côté repo concerné)
4. Validate DB stats actuelles (peut-être avoir bougé depuis 12 mai 23h)

---

## Récap final 3 lignes

> CARNET v6.18 mobile + admin v3d + ROADMAP_REVE v1 = vision pérenne posée, infrastructure scalable jusqu'à 143k cars sous ~70€/mois, prochains sprints clairs (Dealers, NFT XLS-20, EURØP, Vue financière).
>
> Treasury XRP-majoritaire / EURØP-opérationnelle alignée sur Ripple business model. Asso 1901 non-profit en cours de formalisation (statuts J.O. + Cabinet CSBC).
>
> Le rêve : *24/7, les 143 000 meilleures voitures curatées d'Europe en ligne — annonces et enchères, scrapées et propres CARNET, tout le process en autopilot.*

---

*Fin du handoff. Reprendre en cohérence totale à la prochaine session.*

*— CARNET, 12 mai 2026.*
