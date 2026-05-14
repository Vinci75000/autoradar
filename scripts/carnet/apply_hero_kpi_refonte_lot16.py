#!/usr/bin/env python3
"""
CARNET · Lot 16 (Phase α) — Hero affût + KPI bar refonte φ

Source        : Refonte typographique et structurelle du hero d'accueil
                "À l'affût" et de la KPI bar, basée sur des proportions
                Fibonacci/φ (1.618).

Scope         : 2 patches sur index.html
                  - CSS  : surcharges Hero affût + KPI bar nouvelle structure
                  - JS-1 : modification renderKpis pour produire 1 KPI hero
                           (Voitures au Garage) + 4 compactes en grid 2×2

Refonte Hero affût :
  - Padding Fibonacci : 34/21/13 mobile, 55/34/21 desktop
  - h1 : 55px mobile / 89px desktop (Fibonacci), font-weight 500, italic
  - Sub : 17px line-height 1.45 (gain de lisibilité)
  - Tag : marge bottom 13px

Refonte KPI bar :
  - Avant : strip horizontale scrollable, 5 cartes égales
  - Après : grid structuré, 1 hero KPI (Voitures au Garage) en grand encre noir
           sur fond papier + 4 KPI compactes en grid 2×2 papier
  - Hauteurs : hero 144px, compactes 89px (Fibonacci)
  - Ratio hero:compact = 144:89 ≈ φ (1.618)
  - Animations stagger Fibonacci : 0, 80, 130, 210, 340 ms

Hors scope (volontaire) :
  - TabBar refresh (Lot 17 dédié)
  - Hero garage (.hero-garage) — non touché (surcharges spécifiques)
  - Hero pages standalone (privacy/security/etc.) — non touchés (CSS séparé)

Couplage non destructif :
  - L'ancien comportement scroll horizontal reste possible si .is-grid
    n'est pas appliqué — le JS ajoute la classe dynamiquement, donc
    aucune régression si le JS échoue.

Prérequis : Lot 14 (Phase α) appliqué (le marker /LOT 14 sert d'anchor)
Usage     :
    python3 apply_hero_kpi_refonte_lot16.py path/to/index.html
    python3 apply_hero_kpi_refonte_lot16.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : surcharges Hero affût + KPI bar grid
# ═══════════════════════════════════════════════════════════════════════
# Insertion après le bloc Lot 14, avant </style>

CSS_ANCHOR = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 14 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""

CSS_REPLACEMENT = """/* ═══════════════════════════════════════════════════════════════════════
   /LOT 14 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════
   LOT 16 (Phase α) — Hero affût + KPI bar refonte φ
   Proportions Fibonacci : 13/21/34/55/89/144. Ratio φ ≈ 1.618 partout.
   ═══════════════════════════════════════════════════════════════════════ */

/* Hero affût — surcharge ciblée (exclut hero-garage qui a ses propres règles) */
.hero:not(.hero-garage) {
  padding: 34px 21px 13px;
}
.hero:not(.hero-garage) .hero-tag {
  margin-bottom: 13px;
}
.hero:not(.hero-garage) .hero-title {
  font-size: 55px;
  font-weight: 500;
  line-height: 0.93;
  letter-spacing: -0.025em;
  margin-bottom: 13px;
}
.hero:not(.hero-garage) .hero-sub {
  font-size: 17px;
  line-height: 1.45;
  color: var(--encre-soft);
}
@media (min-width: 600px) {
  .hero:not(.hero-garage) {
    padding: 55px 34px 21px;
  }
  .hero:not(.hero-garage) .hero-title {
    font-size: 89px;
    line-height: 0.92;
  }
  .hero:not(.hero-garage) .hero-sub {
    font-size: 19px;
  }
}

/* KPI bar — nouvelle structure grid (activée via .is-grid sur le strip) */
.kpi-strip.is-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 8px;
  padding: 13px 21px 21px;
  overflow: visible;
}
.kpi-strip.is-grid::-webkit-scrollbar { display: none; }

/* Hero KPI — full width, encre noir, grand chiffre */
.kpi-card.is-hero {
  grid-column: 1 / -1;
  flex: none;
  min-height: 144px;
  background: var(--encre);
  color: var(--papier);
  border: none;
  border-radius: var(--r);
  padding: 18px 22px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 4px;
  cursor: pointer;
  transition: transform var(--duration-fast) ease, background var(--duration-fast) ease;
}
.kpi-card.is-hero:active {
  transform: scale(0.985);
  background: #0d0d0d;
}
.kpi-card.is-hero .kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: #9FE1CB;
  text-transform: uppercase;
}
.kpi-card.is-hero .kpi-value {
  font-family: var(--display);
  font-style: italic;
  font-weight: 500;
  font-size: 72px;
  line-height: 0.95;
  letter-spacing: -0.03em;
  color: var(--papier);
  align-self: center;
  margin: 0;
}
.kpi-card.is-hero .kpi-delta {
  font-family: var(--editorial);
  font-style: italic;
  font-size: 14px;
  line-height: 1.3;
  color: rgba(244,241,234,0.78);
}
.kpi-card.is-hero .kpi-delta.neg { color: var(--orange-polo); }
@media (min-width: 600px) {
  .kpi-card.is-hero { min-height: 178px; padding: 22px 28px; }
  .kpi-card.is-hero .kpi-value { font-size: 89px; }
}

/* Compactes — grid 2x2, papier, valeur moyenne */
.kpi-card.is-compact {
  flex: none;
  min-height: 89px;
  background: var(--papier-bright);
  border: 1px solid var(--gris-line-soft);
  border-radius: var(--r);
  padding: 13px 16px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 2px;
  cursor: pointer;
  transition: background var(--duration-fast) ease, transform var(--duration-fast) ease;
}
.kpi-card.is-compact:active {
  background: var(--papier-soft);
  transform: scale(0.97);
}
.kpi-card.is-compact .kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--gris);
  text-transform: uppercase;
}
.kpi-card.is-compact .kpi-value {
  font-family: var(--display);
  font-style: italic;
  font-weight: 400;
  font-size: 34px;
  line-height: 1;
  color: var(--encre);
  letter-spacing: -0.025em;
  align-self: center;
}
.kpi-card.is-compact .kpi-delta {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.04em;
  color: var(--vert-anglais);
  line-height: 1.2;
}
.kpi-card.is-compact .kpi-delta.neg { color: var(--orange-polo); }
.kpi-card.is-compact .kpi-delta.neutral { color: var(--gris); }

/* Animations stagger Fibonacci (0, 80, 130, 210, 340 ms) */
.kpi-strip.is-grid .kpi-card { animation: kpiFadeIn 380ms ease both; }
.kpi-strip.is-grid .kpi-card:nth-child(1) { animation-delay: 0ms; }
.kpi-strip.is-grid .kpi-card:nth-child(2) { animation-delay: 80ms; }
.kpi-strip.is-grid .kpi-card:nth-child(3) { animation-delay: 130ms; }
.kpi-strip.is-grid .kpi-card:nth-child(4) { animation-delay: 210ms; }
.kpi-strip.is-grid .kpi-card:nth-child(5) { animation-delay: 340ms; }
@keyframes kpiFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════════════════════════════════
   /LOT 16 (Phase α)
   ═══════════════════════════════════════════════════════════════════════ */

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS : renderKpis modifié pour produire layout grid
# ═══════════════════════════════════════════════════════════════════════
# Remplace l'intégralité de la fonction renderKpis (du début au } final)

JS1_ANCHOR = """function renderKpis(){
  // Calcule dynamiquement les valeurs depuis State pour rester en phase
  // v6.15 : KPI "Voitures au Garage" + Cote = owned only (wishlist exclus)
  const allGarage = State.garage || [];
  const garage = allGarage.filter(c => c.ownership !== 'wishlist');
  const wishlist = allGarage.filter(c => c.ownership === 'wishlist');
  const garageValue = garage.reduce((acc, c) => acc + (c.cote || 0), 0);
  const garageValueLabel = garageValue >= 1000000
    ? (garageValue / 1000000).toFixed(2).replace(/\\.0+$/, '').replace(/(\\.\\d)0$/, '$1') + ' M\\u202F€ estimés'
    : (garageValue / 1000).toFixed(0) + ' k\\u202F€ estimés';
  const alertsActiveCount = (State.alerts || []).filter(a => !a.paused).length;
  const alertsPausedCount = (State.alerts || []).filter(a => a.paused).length;
  const alertsDelta = alertsPausedCount > 0 ? alertsPausedCount + ' en pause' : 'toutes actives';
  const dynamicKpis = [
    {label:'Voitures au Garage', value: String(garage.length), delta: garage.length > 0 ? garageValueLabel : 'Garage vide', mood: garage.length > 0 ? 'positive' : 'neutral', target:'garage'},
    {label:'Alertes actives',    value: String(alertsActiveCount), delta: alertsDelta, mood: 'neutral', target:'alerts'},
    {label:'Détectées 7 j',      value: String((State.matches || []).length), delta:'+4 vs sem. dern.', mood:'positive', target:'matches'},
    {label:'Enchères suivies',   value: String((State.watchedAuctionIds || []).length), delta:'2 dans 7 jours', mood:'neutral', target:'auctions'},
    {label:'Modèles surveillés', value: String((State.watched || []).length), delta:'+1 ce mois', mood:'neutral', target:'watched'}
  ];
  const stripEl = document.querySelector('.kpi-strip');
  if(!stripEl) return;
  stripEl.innerHTML = dynamicKpis.map(k => `
    <div class="kpi-card" data-action="kpiNav" data-target="${esc(k.target || '')}" role="button" tabindex="0">
      <div class="kpi-label">${esc(k.label)}</div>
      <div class="kpi-value">${esc(k.value)}</div>
      <div class="kpi-delta ${k.mood === 'positive' ? '' : k.mood === 'negative' ? 'neg' : 'neutral'}">${esc(k.delta)}</div>
    </div>
  `).join('');
}"""

JS1_REPLACEMENT = """function renderKpis(){
  // Lot 16 — KPI bar refonte φ : 1 hero KPI (Voitures au Garage) + 4 compactes en grid 2×2.
  // Calcule dynamiquement les valeurs depuis State pour rester en phase.
  // v6.15 : KPI "Voitures au Garage" + Cote = owned only (wishlist exclus)
  const allGarage = State.garage || [];
  const garage = allGarage.filter(c => c.ownership !== 'wishlist');
  const wishlist = allGarage.filter(c => c.ownership === 'wishlist');
  const garageValue = garage.reduce((acc, c) => acc + (c.cote || 0), 0);
  const garageValueLabel = garageValue >= 1000000
    ? (garageValue / 1000000).toFixed(2).replace(/\\.0+$/, '').replace(/(\\.\\d)0$/, '$1') + ' M\\u202F€ estimés'
    : (garageValue / 1000).toFixed(0) + ' k\\u202F€ estimés';
  const alertsActiveCount = (State.alerts || []).filter(a => !a.paused).length;
  const alertsPausedCount = (State.alerts || []).filter(a => a.paused).length;
  const alertsDelta = alertsPausedCount > 0 ? alertsPausedCount + ' en pause' : 'toutes actives';
  const dynamicKpis = [
    {label:'Voitures au Garage', value: String(garage.length), delta: garage.length > 0 ? garageValueLabel : 'Garage vide', mood: garage.length > 0 ? 'positive' : 'neutral', target:'garage'},
    {label:'Alertes actives',    value: String(alertsActiveCount), delta: alertsDelta, mood: 'neutral', target:'alerts'},
    {label:'Détectées 7 j',      value: String((State.matches || []).length), delta:'+4 vs sem. dern.', mood:'positive', target:'matches'},
    {label:'Enchères suivies',   value: String((State.watchedAuctionIds || []).length), delta:'2 dans 7 jours', mood:'neutral', target:'auctions'},
    {label:'Modèles surveillés', value: String((State.watched || []).length), delta:'+1 ce mois', mood:'neutral', target:'watched'}
  ];
  const stripEl = document.querySelector('.kpi-strip');
  if(!stripEl) return;
  // Lot 16 — activer le layout grid
  stripEl.classList.add('is-grid');
  const [heroKpi, ...compactKpis] = dynamicKpis;
  const renderCard = (k, variant) => `
    <div class="kpi-card ${variant}" data-action="kpiNav" data-target="${esc(k.target || '')}" role="button" tabindex="0">
      <div class="kpi-label">${esc(k.label)}</div>
      <div class="kpi-value">${esc(k.value)}</div>
      <div class="kpi-delta ${k.mood === 'positive' ? '' : k.mood === 'negative' ? 'neg' : 'neutral'}">${esc(k.delta)}</div>
    </div>
  `;
  const heroHtml = heroKpi ? renderCard(heroKpi, 'is-hero') : '';
  const compactHtml = compactKpis.map(k => renderCard(k, 'is-compact')).join('');
  stripEl.innerHTML = heroHtml + compactHtml;
}"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 16 (Phase α) — Hero affût + KPI bar refonte φ",
    requires=[
        # Lot 14 fournit le marker /LOT 14 (Phase α) qui sert d'anchor au CSS.
        "LOT 14 (Phase α) — Filtre archétype Garage grid",
    ],
    patches=[
        Patch(
            name="CSS — Hero affût + KPI bar refonte φ (.kpi-strip.is-grid + .kpi-card.is-hero/.is-compact)",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="LOT 16 (Phase α) — Hero affût + KPI bar refonte φ",
        ),
        Patch(
            name="JS — renderKpis produit 1 hero KPI + 4 compactes en grid",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker="// Lot 16 — KPI bar refonte φ : 1 hero KPI",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
