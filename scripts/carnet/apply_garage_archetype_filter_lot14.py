#!/usr/bin/env python3
"""
CARNET · Lot 14 (Phase α) — Filtre archétype dans Garage grid

Source        : Croise les archétypes inférés des voitures du garage avec
                les filtres choisis par l'utilisateur. Affiche des chips
                horizontaux scrollables en haut du garage, clic toggle.

Scope         : 5 patches sur index.html
                  - CSS  : styles .garage-archetype-filters + .garage-archetype-chip
                  - JS-1 : helpers inferCarArchetypes + getGarageArchetypeCounts
                           + applyGarageArchetypeFilter + renderGarageArchetypeFilters
                  - JS-2 : Actions.toggleGarageArchetype (toggle + re-render)
                  - JS-3 : renderGaragePage — calcul filters + filtrage cars + injection bar
                  - JS-4 : dispatch event handler pour data-action="toggleGarageArchetype"

  Inférence inferCarArchetypes(car) — règles simples par regex sur brand/model
  + heuristiques sur année, km, cote :
    - track_rat : GT3/GT2/Cup/Trophy/RS/R, Caterham, Lotus, Radical, BAC, KTM
    - builder   : Singer/Brabus/Mansory/RUF/Alpina/Liberty Walk/restomod
    - driver    : >100k km, ou breaks/wagons/berlines GT
    - non_driver: hypercars + cote ≥500k avec km <10k
    - collector : year <1990, ou cote ≥200k
    - enthusiast: limited/special/anniversary/Stradale/Carrera GT/Enzo/F40/F50
    - flipper   : trend === 'up'
    - social    : supercars exotiques connues des rallyes (Aventador, SF90, etc.)
  Une voiture peut matcher plusieurs archétypes (multi-tag).

  UI : chips horizontaux scrollables, état actif = filtre ON.
  Logic : OR — un chip actif = "montrer les voitures qui matchent au moins
  un des archétypes actifs". Aucun chip actif = toutes les voitures.

  State : State.garageArchetypeFilter = array of archetype IDs (legacy IDs
  cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
  builder, enthusiast, driver, non_driver, social).

  Filtre s'applique aux 3 buckets : active, in-sale, wishlist.
  KPIs (totalValue, count, etc.) restent calculés sur toutes les cars,
  pas sur le filtré — c'est cohérent (vue d'ensemble + filtre tactique).

Hors scope :
  - Persistance du filtre dans localStorage (volontaire — filtre tactique
    qui se reset à chaque session)
  - Logique AND (un car doit matcher TOUS les filtres actifs)
  - Filtrage des archives (vendues) — vendre est définitif

Prérequis : Lot 13b-3 appliqué (mais pas strictement requis — fonctionne sur
            n'importe quel index.html post-Lot 8 qui a renderGaragePage)
Usage     :
    python3 apply_garage_archetype_filter_lot14.py path/to/index.html
    python3 apply_garage_archetype_filter_lot14.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : styles chips de filtre archétype
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc CSS Lot 13 (carnet-overlay générique), avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 13 (Phase α refactor)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 13 (Phase α refactor)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 14 (Phase α) — Filtre archétype Garage grid
   ═══════════════════════════════════════════════════════════════════════ */
.garage-archetype-filters {
  display: flex;
  gap: 8px;
  padding: 14px 22px 6px;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.garage-archetype-filters::-webkit-scrollbar { display: none; }

.garage-archetype-filters-label {
  flex-shrink: 0;
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--gris);
  text-transform: uppercase;
  align-self: center;
  padding-right: 4px;
}

.garage-archetype-chip {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: var(--r);
  background: var(--papier);
  border: 1px solid var(--gris-line);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--encre);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
  white-space: nowrap;
}
.garage-archetype-chip:hover {
  border-color: var(--orange-polo);
}
.garage-archetype-chip.is-active {
  background: var(--encre);
  color: var(--papier);
  border-color: var(--encre);
}
.garage-archetype-chip-count {
  font-size: 9px;
  opacity: 0.6;
  font-weight: 500;
}
.garage-archetype-chip.is-active .garage-archetype-chip-count {
  opacity: 0.8;
}
.garage-archetype-empty-state {
  padding: 28px 22px;
  text-align: center;
  font-family: var(--editorial);
  font-style: italic;
  font-size: 14px;
  color: var(--encre-soft);
}
.garage-archetype-empty-state-clear {
  display: inline-block;
  margin-top: 8px;
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--orange-polo);
  cursor: pointer;
  border-bottom: 1px solid var(--orange-polo);
  padding-bottom: 1px;
}
/* ═══════════════════════════════════════════════════════════════════════
   /LOT 14 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers : inferCarArchetypes + getGarageArchetypeCounts
#                       + applyGarageArchetypeFilter + renderGarageArchetypeFilters
# ═══════════════════════════════════════════════════════════════════════
# Insertion avant function renderGaragePage(){

JS1_ANCHOR = """};
// ─── /Lot 13 (Phase α refactor) ────────────────────────────────────────


function renderGaragePage(){
  const m = document.querySelector('main.main');"""

JS1_REPLACEMENT = """};
// ─── /Lot 13 (Phase α refactor) ────────────────────────────────────────


// ─── Lot 14 (Phase α) — Filtre archétype Garage ─────────────────────
// inferCarArchetypes(car) : retourne array d'archetype IDs basé sur les
// caractéristiques de la voiture. Multi-tag — une voiture peut matcher
// plusieurs archétypes (ex: Porsche 911 R 2017 peu kilométrée → track_rat
// + collector + enthusiast).
//
// IDs cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
// builder, enthusiast, driver, non_driver, social.
function inferCarArchetypes(car){
  if(!car) return [];
  const set = new Set();
  const brand = (car.brand || '').toLowerCase();
  const model = (car.model || '').toLowerCase();
  const fullName = brand + ' ' + model;
  const year = car.year || 0;
  const km = car.km || 0;
  const cote = car.cote || 0;

  // Track Rat — voitures circuit
  if(/\\bgt3\\b|\\bgt2\\b|\\bcup\\b|trophy|\\brs\\b|sport evo|black series|caterham|lotus|bac mono|ktm x-bow|radical|porsche r\\b|\\b911 r\\b|cayman gt4|m4 csl/i.test(fullName)){
    set.add('track_rat');
  }

  // Builder / Outlaw — préparateurs et restomods
  if(/singer|brabus|mansory|\\bruf\\b|alpina|liberty walk|restomod|tuner|wide ?body|hennessey|gunther werks|tuthill/i.test(fullName)){
    set.add('builder');
  }

  // Driver / Gros rouleur — kilométrage élevé, breaks, berlines GT
  if(km > 100000){
    set.add('driver');
  }
  if(/\\bs-class\\b|7 ?series|panamera|continental|ghost|phantom|maybach|\\bcls\\b|break|estate|wagon|touring|avant|sportwagon|shooting brake/i.test(fullName)){
    set.add('driver');
  }

  // Non-Driver / Gardien — hypercars + low km, ou cote très élevée + low km
  if(cote >= 500000 && km < 10000){
    set.add('non_driver');
  }
  if(/zonda|huayra|veyron|chiron|valkyrie|laferrari|918 spyder|p1|senna|jesko|tuatara|jewel|battista|nevera|evija|t.50|aventador svj|sf90|monza sp/i.test(fullName)){
    set.add('non_driver');
  }

  // Collector — classics et valeurs de référence
  if(year && year < 1990){
    set.add('collector');
  }
  if(cote >= 200000){
    set.add('collector');
  }

  // Enthusiast — séries limitées, spécifications particulières
  if(/limited|special|anniversary|jubilee|carrera gt|enzo|\\bf50\\b|\\bf40\\b|carrera rs|stradale|aperta|spyder|targa florio|speedster|gma|chassis|matching/i.test(fullName)){
    set.add('enthusiast');
  }

  // Flipper — opportunité de revente (trend up)
  if(car.trend === 'up'){
    set.add('flipper');
  }

  // Social / Rallye — supercars exotiques connues des Gumball
  if(/aventador|huracan|sf90|\\b296\\b|\\b812\\b|720s|gt-r|\\bgtr\\b|amg gt|\\bm8\\b|\\brs6\\b|\\brs7\\b|gallardo|murcielago|diablo|countach|defender|g.?wagon|g 63|g63|urus/i.test(fullName)){
    set.add('social');
  }

  return Array.from(set);
}

// getGarageArchetypeCounts(cars) : retourne Map archetypeId → count.
function getGarageArchetypeCounts(cars){
  const counts = {};
  (cars || []).forEach(c => {
    const archs = inferCarArchetypes(c);
    archs.forEach(a => { counts[a] = (counts[a] || 0) + 1; });
  });
  return counts;
}

// applyGarageArchetypeFilter(cars, activeFilters) : filtre OR.
// Si activeFilters est vide, retourne cars inchangé.
function applyGarageArchetypeFilter(cars, activeFilters){
  if(!activeFilters || activeFilters.length === 0) return cars;
  const filtersSet = new Set(activeFilters);
  return (cars || []).filter(c => {
    const archs = inferCarArchetypes(c);
    return archs.some(a => filtersSet.has(a));
  });
}

// renderGarageArchetypeFilters(archetypeCounts, activeFilters) : HTML chips.
// Affiche uniquement les archétypes présents dans le garage (count > 0).
function renderGarageArchetypeFilters(archetypeCounts, activeFilters){
  const presentArchetypes = Object.keys(archetypeCounts).filter(id => archetypeCounts[id] > 0);
  if(presentArchetypes.length === 0) return '';
  // Tri : actifs d'abord, puis par count décroissant
  const activeSet = new Set(activeFilters || []);
  presentArchetypes.sort((a, b) => {
    const aActive = activeSet.has(a) ? 1 : 0;
    const bActive = activeSet.has(b) ? 1 : 0;
    if(aActive !== bActive) return bActive - aActive;
    return archetypeCounts[b] - archetypeCounts[a];
  });
  const chipsHtml = presentArchetypes.map(id => {
    const profile = COLLECTOR_PROFILES.find(p => p.id === id);
    if(!profile) return '';
    const isActive = activeSet.has(id);
    const count = archetypeCounts[id];
    return `<button type="button"
      class="garage-archetype-chip${isActive ? ' is-active' : ''}"
      data-action="toggleGarageArchetype"
      data-archetype="${esc(id)}"
      aria-pressed="${isActive}">
      <span>${esc(profile.chip)}</span>
      <span class="garage-archetype-chip-count">${count}</span>
    </button>`;
  }).join('');
  return `<div class="garage-archetype-filters" aria-label="Filtres par archétype">
    <span class="garage-archetype-filters-label">Profil</span>
    ${chipsHtml}
  </div>`;
}
// ─── /Lot 14 helpers ─────────────────────────────────────────────────

function renderGaragePage(){
  const m = document.querySelector('main.main');"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — Actions.toggleGarageArchetype
# Insertion après une méthode existante stable dans Actions
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = """  signOut(){ if(window.Auth) Auth.signOut(); },

  cancelConfirm(){"""

JS2_REPLACEMENT = """  signOut(){ if(window.Auth) Auth.signOut(); },

  // ─── Lot 14 — toggle filtre archétype Garage ────────────────────────
  toggleGarageArchetype(archetypeId){
    if(!archetypeId) return;
    State.garageArchetypeFilter = State.garageArchetypeFilter || [];
    const idx = State.garageArchetypeFilter.indexOf(archetypeId);
    if(idx >= 0){
      State.garageArchetypeFilter.splice(idx, 1);
    } else {
      State.garageArchetypeFilter.push(archetypeId);
    }
    if(State.activeTab === 'garage' && typeof renderGaragePage === 'function'){
      renderGaragePage();
    }
  },
  clearGarageArchetypeFilter(){
    State.garageArchetypeFilter = [];
    if(State.activeTab === 'garage' && typeof renderGaragePage === 'function'){
      renderGaragePage();
    }
  },

  cancelConfirm(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 4 — renderGaragePage : intégration filtre dans le body
# ═══════════════════════════════════════════════════════════════════════
# Modifier les déclarations de cars + injecter la barre + utiliser cars filtrées

JS3_ANCHOR = """  const soldCars = garage.filter(c => c.saleStatus === 'sold').sort((a, b) => {
    return (b.saleData?.soldAt || 0) - (a.saleData?.soldAt || 0);
  });
  // Calculs collection ACTIVE (n'inclut pas les vendues)"""

JS3_REPLACEMENT = """  const soldCars = garage.filter(c => c.saleStatus === 'sold').sort((a, b) => {
    return (b.saleData?.soldAt || 0) - (a.saleData?.soldAt || 0);
  });
  // Lot 14 — filtre archétype (s'applique aux 3 buckets vivants, pas aux archives)
  const _archetypeFilters = State.garageArchetypeFilter || [];
  const _archetypeCounts = getGarageArchetypeCounts([...activeCars, ...inSaleCars, ...wishlistCars]);
  const _filteredActiveCars = applyGarageArchetypeFilter(activeCars, _archetypeFilters);
  const _filteredInSaleCars = applyGarageArchetypeFilter(inSaleCars, _archetypeFilters);
  const _filteredWishlistCars = applyGarageArchetypeFilter(wishlistCars, _archetypeFilters);
  const _hasFilterMismatch = _archetypeFilters.length > 0
    && _filteredActiveCars.length === 0
    && _filteredInSaleCars.length === 0
    && _filteredWishlistCars.length === 0
    && (activeCars.length + inSaleCars.length + wishlistCars.length) > 0;
  // Calculs collection ACTIVE (n'inclut pas les vendues)"""


# Modification de inSaleSection, collectionSection, wishlistSection pour
# utiliser les versions filtrées + insertion de la barre de filtres + empty state.

JS4_ANCHOR = """    // Section "Mes ventes actives" si applicable
    const inSaleSection = inSaleCars.length > 0 ? `
      <div class="garage-section-divider">
        <span class="garage-section-divider-label">EN VENTE · ${inSaleCars.length}</span>
      </div>
      <div class="garage-feed">
        ${inSaleCars.map(renderGarageCard).join('')}
      </div>
    ` : '';

    // Section "Collection" (cars sans sale en cours)
    const collectionSection = activeCars.length > 0 ? `
      ${inSaleCars.length > 0 ? `
        <div class="garage-section-divider">
          <span class="garage-section-divider-label">COLLECTION · ${activeCars.length}</span>
        </div>
      ` : ''}
      <div class="garage-feed">
        ${activeCars.map(renderGarageCard).join('')}
      </div>
    ` : '';

    // v6.15 : Section Wishlist (cars que l'user veut, pas encore acquises)
    const wishlistSection = wishlistCars.length > 0 ? `
      <div class="garage-section-divider wishlist">
        <span class="garage-section-divider-label">WISHLIST \\u00b7 ${wishlistCars.length}</span>
        <span class="garage-section-divider-meta">${wishlistCars.length > 1 ? 'voitures suivies' : 'voiture suivie'}</span>
      </div>
      <div class="garage-feed garage-feed-wishlist">
        ${wishlistCars.map(renderGarageCard).join('')}
      </div>
      <div class="garage-wishlist-note">Les voitures que tu suis sans encore les posséder. Aucun dossier requis — juste un signet pour ne pas oublier.</div>
    ` : '';"""

JS4_REPLACEMENT = """    // Section "Mes ventes actives" si applicable (Lot 14 — utilise version filtrée)
    const inSaleSection = _filteredInSaleCars.length > 0 ? `
      <div class="garage-section-divider">
        <span class="garage-section-divider-label">EN VENTE · ${_filteredInSaleCars.length}${_archetypeFilters.length > 0 && _filteredInSaleCars.length < inSaleCars.length ? ' / ' + inSaleCars.length : ''}</span>
      </div>
      <div class="garage-feed">
        ${_filteredInSaleCars.map(renderGarageCard).join('')}
      </div>
    ` : '';

    // Section "Collection" (cars sans sale en cours) (Lot 14 — utilise version filtrée)
    const collectionSection = _filteredActiveCars.length > 0 ? `
      ${_filteredInSaleCars.length > 0 ? `
        <div class="garage-section-divider">
          <span class="garage-section-divider-label">COLLECTION · ${_filteredActiveCars.length}${_archetypeFilters.length > 0 && _filteredActiveCars.length < activeCars.length ? ' / ' + activeCars.length : ''}</span>
        </div>
      ` : ''}
      <div class="garage-feed">
        ${_filteredActiveCars.map(renderGarageCard).join('')}
      </div>
    ` : '';

    // v6.15 : Section Wishlist (Lot 14 — utilise version filtrée)
    const wishlistSection = _filteredWishlistCars.length > 0 ? `
      <div class="garage-section-divider wishlist">
        <span class="garage-section-divider-label">WISHLIST \\u00b7 ${_filteredWishlistCars.length}${_archetypeFilters.length > 0 && _filteredWishlistCars.length < wishlistCars.length ? ' / ' + wishlistCars.length : ''}</span>
        <span class="garage-section-divider-meta">${_filteredWishlistCars.length > 1 ? 'voitures suivies' : 'voiture suivie'}</span>
      </div>
      <div class="garage-feed garage-feed-wishlist">
        ${_filteredWishlistCars.map(renderGarageCard).join('')}
      </div>
      <div class="garage-wishlist-note">Les voitures que tu suis sans encore les posséder. Aucun dossier requis — juste un signet pour ne pas oublier.</div>
    ` : '';

    // Lot 14 — empty state si filtre trop strict
    const archetypeEmptyState = _hasFilterMismatch ? `
      <div class="garage-archetype-empty-state">
        Aucune voiture ne matche ce filtre.<br>
        <span class="garage-archetype-empty-state-clear" data-action="clearGarageArchetypeFilter">Tout afficher \\u2192</span>
      </div>
    ` : '';"""


# Insertion de la barre de filtres dans le body et de l'empty state
JS5_ANCHOR = """      ${renderGarageAdviceSection(activeCars)}
      ${inSaleSection}
      ${collectionSection}"""

JS5_REPLACEMENT = """      ${renderGarageAdviceSection(activeCars)}
      ${renderGarageArchetypeFilters(_archetypeCounts, _archetypeFilters)}
      ${archetypeEmptyState}
      ${inSaleSection}
      ${collectionSection}"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 5 — Event dispatch pour data-action="toggleGarageArchetype"
# ═══════════════════════════════════════════════════════════════════════

JS6_ANCHOR = """  if(action === 'toggleGarageCondition'){ Actions.toggleGarageCondition(t.dataset.field); return; }
  // Sale flow"""

JS6_REPLACEMENT = """  if(action === 'toggleGarageCondition'){ Actions.toggleGarageCondition(t.dataset.field); return; }
  // Lot 14 — filtre archétype
  if(action === 'toggleGarageArchetype'){ Actions.toggleGarageArchetype(t.dataset.archetype); return; }
  if(action === 'clearGarageArchetypeFilter'){ Actions.clearGarageArchetypeFilter(); return; }
  // Sale flow"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 14 (Phase α) — Filtre archétype Garage grid",
    requires=[
        # Le Lot 13 (Phase α refactor) ajoute le commentaire de fin qui sert d'anchor
        # pour le patch CSS Lot 14.
        "LOT 13 (Phase α refactor) — carnet-overlay générique",
    ],
    patches=[
        Patch(
            name="CSS — styles .garage-archetype-filters + chips",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 14 (Phase α) — Filtre archétype Garage grid",
        ),
        Patch(
            name="JS-1 · helpers (inferCarArchetypes + counts + filter + render)",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker="// ─── Lot 14 (Phase α) — Filtre archétype Garage",
        ),
        Patch(
            name="JS-2 · Actions.toggleGarageArchetype + clearGarageArchetypeFilter",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker="// ─── Lot 14 — toggle filtre archétype Garage",
        ),
        Patch(
            name="JS-3 · renderGaragePage — déclaration filtres + cars filtrées",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker="const _archetypeFilters = State.garageArchetypeFilter",
        ),
        Patch(
            name="JS-4 · renderGaragePage — sections utilisent cars filtrées + empty state",
            anchor=JS4_ANCHOR,
            replacement=JS4_REPLACEMENT,
            idempotence_marker="const inSaleSection = _filteredInSaleCars.length",
        ),
        Patch(
            name="JS-5 · renderGaragePage — injection barre filtres + empty state dans body",
            anchor=JS5_ANCHOR,
            replacement=JS5_REPLACEMENT,
            idempotence_marker="${renderGarageArchetypeFilters(_archetypeCounts, _archetypeFilters)}",
        ),
        Patch(
            name="JS-6 · dispatch event toggleGarageArchetype + clearGarageArchetypeFilter",
            anchor=JS6_ANCHOR,
            replacement=JS6_REPLACEMENT,
            idempotence_marker="if(action === 'toggleGarageArchetype'){ Actions.toggleGarageArchetype",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
