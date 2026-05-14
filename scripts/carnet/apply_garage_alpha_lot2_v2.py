#!/usr/bin/env python3
"""
CARNET · Lot 2 (Phase α) — Garage refonte mid-top variante C

Version refactorisée utilisant `carnet_patch_lib`. Strictement équivalente
fonctionnellement au script monolithique d'origine `apply_garage_alpha_lot2.py`.

Applique 4 patches sur index.html (post-Lot 1.1) :
  1. CSS additions     → hero garage, KPI sparkline, échéances
  2. JS helpers        → frCarsCount, padCarCount, getGarageDeadlines,
                         renderGarageSparkline, renderGarageDeadlinesBlock
  3. Hero section      → header double + h1 + sub + discover/profile
  4. KPI + Échéances   → sparkline + meta 3-col + bloc échéances

Prérequis : Sprint Convergence v2 appliqué (Lot 1.1)
Usage     :
    python3 apply_garage_alpha_lot2_v2.py path/to/index.html
    python3 apply_garage_alpha_lot2_v2.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions (avant </style>)
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """.user-menu-item:hover .user-menu-chevron { color: var(--orange-polo); }

</style>"""

PATCH_1_REPLACEMENT = """.user-menu-item:hover .user-menu-chevron { color: var(--orange-polo); }

/* ═══ LOT 2 (Phase α) — Garage refonte mid-top ═════════════════════════ */

/* Hero garage — variante C (header double + h1 + sub + lien discover) */
.hero-garage .hero-tag-row { display: none; }
.hero-garage-header{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:10px;
}
.garage-kicker{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-kicker-count{ color:var(--encre); }
.garage-sync{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--gris);
  text-transform:uppercase;
  display:inline-flex;
  align-items:center;
  gap:5px;
}
.garage-sync-dot{
  color:var(--vert-anglais);
  font-size:10px;
  line-height:1;
}
.hero-garage .hero-title{
  font-size:var(--t-2xl);
  margin:4px 0 14px;
  letter-spacing:-0.01em;
  line-height:0.95;
}
.garage-sub-lead{
  font-style:italic;
  font-family:var(--editorial);
}
.garage-discover-link{
  display:inline-block;
  font-family:var(--mono);
  font-size:11px;
  letter-spacing:0.14em;
  color:var(--encre);
  text-transform:uppercase;
  text-decoration:none;
  border-bottom:1px solid var(--encre);
  padding-bottom:2px;
  margin-top:12px;
  cursor:pointer;
}
.garage-discover-link:hover{
  color:var(--orange-polo);
  border-bottom-color:var(--orange-polo);
}

/* Cache l'ancien badge LIVE/DEMO dans le hero garage — signal porté par .garage-sync */
.hero-garage .live-mode-badge{ display:none !important; }

/* KPI bloc — sparkline + footer flex */
.hero-garage + section .garage-summary{
  padding:24px 22px 18px;
}
.hero-garage + section .garage-summary-value{
  font-size:42px;
  line-height:1;
  letter-spacing:-0.025em;
  margin-bottom:2px;
}
.hero-garage + section .garage-summary-delta{
  font-family:var(--mono) !important;
  font-style:normal !important;
  font-size:11px;
  letter-spacing:0.04em;
  margin-top:6px;
  margin-bottom:14px;
}
.garage-sparkline{
  width:100%;
  height:36px;
  display:block;
  margin-bottom:14px;
}
.garage-sparkline-line{
  stroke:var(--vert-anglais);
  stroke-width:1.2;
  fill:none;
  stroke-linecap:round;
  stroke-linejoin:round;
  opacity:0.9;
}
.garage-sparkline-end{ fill:var(--orange-polo); }
.hero-garage + section .garage-summary-meta{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding-top:14px;
  border-top:1px solid rgba(244,241,234,0.15);
  font-family:var(--mono);
  font-size:11px;
  color:rgba(244,241,234,0.55);
  letter-spacing:0.04em;
}

/* Échéances Q3 — nouveau bloc */
.garage-deadlines{ margin:26px 0 18px; }
.garage-deadlines-header{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:12px;
}
.garage-deadlines-title{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-deadlines-count{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.12em;
  color:var(--orange-polo);
  text-transform:uppercase;
}
.garage-deadlines-list{
  display:flex;
  flex-direction:column;
  gap:6px;
}
.garage-deadline-row{
  display:flex;
  align-items:stretch;
  gap:12px;
  padding:12px 14px;
  background:#FFFDF7;
  border:1px solid rgba(26,26,24,0.08);
  border-radius:var(--r);
}
.garage-deadline-bar{
  width:3px;
  border-radius:1px;
  background:rgba(26,26,24,0.2);
  flex-shrink:0;
}
.garage-deadline-bar.urgent{ background:var(--orange-polo); }
.garage-deadline-bar.warning{ background:#C8943A; }
.garage-deadline-bar.ok{ background:var(--vert-anglais); }
.garage-deadline-content{ flex:1; min-width:0; }
.garage-deadline-title-row{
  font-family:var(--editorial);
  font-style:italic;
  font-size:15px;
  color:var(--encre);
  line-height:1.3;
}
.garage-deadline-meta{
  font-family:var(--mono);
  font-size:10px;
  color:var(--gris);
  letter-spacing:0.04em;
  margin-top:2px;
  text-transform:uppercase;
}
.garage-deadline-arrow{
  font-family:var(--mono);
  font-size:14px;
  color:rgba(26,26,24,0.3);
  align-self:center;
}
.garage-deadlines-empty{
  padding:20px 18px;
  background:rgba(26,26,24,0.025);
  border:1px dashed rgba(26,26,24,0.15);
  border-radius:var(--r);
  text-align:center;
}
.garage-deadlines-empty-text{
  font-family:var(--editorial);
  font-style:italic;
  font-size:14px;
  color:var(--gris);
}
.garage-deadlines-empty-add{
  display:inline-block;
  margin-top:8px;
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.12em;
  color:var(--orange-polo);
  text-transform:uppercase;
  text-decoration:none;
  border-bottom:1px solid var(--orange-polo);
  padding-bottom:2px;
  cursor:pointer;
  background:none;
  border-left:none;
  border-right:none;
  border-top:none;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers (avant renderGaragePage)
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """    </div>
  `;
}

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """    </div>
  `;
}

// ─── Lot 2 (Phase α) — helpers Garage ─────────────────────────
function frCarsCount(n){
  const words=['Aucune voiture.','Une voiture.','Deux voitures.','Trois voitures.','Quatre voitures.','Cinq voitures.','Six voitures.','Sept voitures.','Huit voitures.','Neuf voitures.','Dix voitures.'];
  if(n>=0 && n<=10) return words[n];
  return n+' voitures.';
}
function padCarCount(n){ return String(n||0).padStart(2,'0'); }
function getGarageDeadlines(){
  // Phase α — placeholder. Sera rempli Lot 6+ avec data réelle (CT, révision, assurance).
  return Array.isArray(State.garageDeadlines) ? State.garageDeadlines : [];
}
function renderGarageSparkline(){
  // Mini sparkline placeholder. À brancher sur valuation_snapshots quand cette table sera live.
  // Path mock cohérent : 12 points, tendance haussière douce avec une oscillation
  return `<svg class="garage-sparkline" viewBox="0 0 300 36" preserveAspectRatio="none">
    <polyline class="garage-sparkline-line" points="0,28 25,26 50,27 75,22 100,24 125,20 150,21 175,16 200,18 225,14 250,11 275,9 295,7"/>
    <circle class="garage-sparkline-end" cx="295" cy="7" r="2.5"/>
  </svg>`;
}
function renderGarageDeadlinesBlock(){
  const deadlines = getGarageDeadlines();
  if(deadlines.length === 0){
    return `<div class="garage-deadlines">
      <div class="garage-deadlines-header">
        <span class="garage-deadlines-title">ÉCHÉANCES \\u00b7 PROCHAINS 90 J</span>
      </div>
      <div class="garage-deadlines-empty">
        <div class="garage-deadlines-empty-text">Aucune \\u00e9ch\\u00e9ance enregistr\\u00e9e.</div>
        <button type="button" class="garage-deadlines-empty-add" data-action="openAddDeadline">+ Ajouter un rappel</button>
      </div>
    </div>`;
  }
  const urgentCount = deadlines.filter(d => d.severity === 'urgent').length;
  return `<div class="garage-deadlines">
    <div class="garage-deadlines-header">
      <span class="garage-deadlines-title">\\u00c9CH\\u00c9ANCES \\u00b7 PROCHAINS 90 J</span>
      ${urgentCount > 0 ? `<span class="garage-deadlines-count">${urgentCount} URGENT${urgentCount > 1 ? 'S' : ''}</span>` : ''}
    </div>
    <div class="garage-deadlines-list">
      ${deadlines.slice(0, 5).map(d => `
        <div class="garage-deadline-row" data-action="openDeadline" data-deadline-id="${esc(d.id || '')}">
          <div class="garage-deadline-bar ${esc(d.severity || 'ok')}"></div>
          <div class="garage-deadline-content">
            <div class="garage-deadline-title-row">${esc(d.title || '')}</div>
            <div class="garage-deadline-meta">${esc(d.meta || '')}</div>
          </div>
          <div class="garage-deadline-arrow">\\u2192</div>
        </div>
      `).join('')}
    </div>
  </div>`;
}

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — Hero section variante C
# ═══════════════════════════════════════════════════════════════════════

PATCH_3_ANCHOR = '''  m.innerHTML = `
    <section class="hero">
      <div class="hero-tag-row">
        <div class="hero-tag">GARAGE</div>
        <button class="hero-profile-link" data-action="openSelectProfile">${(State.userProfiles || []).length === 0 ? \'Mon profil →\' : \'Mon profil · \' + (State.userProfiles || []).length + \' \\u2192\'}</button>
      </div>
      <h1 class="hero-title">Ma collection.</h1>
      <p class="hero-sub">Tes voitures vivent ici. Cote, entretien, photos, factures — et la fenêtre vers le marché pour étoffer ou revendre. <a class="hero-discover-link" data-action="openDiscoverCarnet">Pourquoi CARNET \\u2192</a></p>
      ${(State.userProfiles || []).length > 0 ? `
        <div class="hero-profile-chips">
          ${(State.userProfiles || []).map(id => {
            const p = COLLECTOR_PROFILES.find(x => x.id === id);
            return p ? `<span class="hero-profile-chip">${esc(p.chip)}</span>` : \'\';
          }).join(\'\')}
        </div>
      ` : \'\'}
    </section>
    <section class="section">
      ${body}
    </section>
  `;'''

PATCH_3_REPLACEMENT = '''  m.innerHTML = `
    <section class="hero hero-garage">
      <div class="hero-garage-header">
        <span class="garage-kicker">Garage <span class="garage-kicker-count">\\u00b7 ${padCarCount(activeCars.length)}</span></span>
        <span class="garage-sync">SYNC <span class="garage-sync-dot">\\u25cf</span></span>
      </div>
      <h1 class="hero-title">Ma collection.</h1>
      <p class="hero-sub"><em class="garage-sub-lead">${frCarsCount(activeCars.length)}</em> Leur cote, leur carnet, leur place sur le march\\u00e9.</p>
      <a class="garage-discover-link" data-action="openDiscoverCarnet">Pourquoi CARNET \\u2192</a>
      ${(State.userProfiles || []).length === 0 ? `<a class="garage-discover-link" data-action="openSelectProfile" style="margin-left:14px;color:var(--gris);border-bottom-color:var(--gris);">Mon profil \\u2192</a>` : \'\'}
      ${(State.userProfiles || []).length > 0 ? `
        <div class="hero-profile-chips">
          ${(State.userProfiles || []).map(id => {
            const p = COLLECTOR_PROFILES.find(x => x.id === id);
            return p ? `<span class="hero-profile-chip">${esc(p.chip)}</span>` : \'\';
          }).join(\'\')}
        </div>
      ` : \'\'}
    </section>
    <section class="section">
      ${body}
    </section>
  `;'''


# ═══════════════════════════════════════════════════════════════════════
# PATCH 4 — KPI block + Échéances insérées
# ═══════════════════════════════════════════════════════════════════════

PATCH_4_ANCHOR = '''      <div class="garage-summary">
        <div class="garage-summary-label">VALEUR ESTIMÉE · COTE CARNET</div>
        <div class="garage-summary-value">${esc(fmtPrice(totalValue))}</div>
        ${valuableCars.length > 0 ? `<div class="garage-summary-delta" style="color:${deltaColor}">${deltaSign} ${esc(fmtPrice(Math.abs(delta)))} · ${deltaSign}${Math.abs(deltaPercent).toFixed(1)} % depuis acquisition</div>` : \'\'}
        <div class="garage-summary-meta">${valuableCars.length} voiture${valuableCars.length === 1 ? \'\' : \'s\'} · ${totalDocs} document${totalDocs === 1 ? \'\' : \'s\'} · ${totalPhotos} photo${totalPhotos === 1 ? \'\' : \'s\'}</div>
        ${inSaleCars.length > 0 ? `<div class="garage-summary-sale">${inSaleCars.length} en vente · suis-les depuis ta fiche voiture</div>` : \'\'}
        ${soldCars.length > 0 ? `<div class="garage-summary-lifetime">${soldCars.length} vendue${soldCars.length > 1 ? \'s\' : \'\'} cumulée${soldCars.length > 1 ? \'s\' : \'\'} · ${esc(fmtPrice(lifetimeSalesTotal))}</div>` : \'\'}
      </div>
      <button class="garage-card-add garage-card-add-top" data-action="openAddGarage" onclick="if(window.Actions && window.Actions.openAddGarage) window.Actions.openAddGarage();">'''

PATCH_4_REPLACEMENT = '''      <div class="garage-summary">
        <div class="garage-summary-label">VALEUR ESTIM\\u00c9E \\u00b7 COTE CARNET</div>
        <div class="garage-summary-value">${esc(fmtPrice(totalValue))}</div>
        ${valuableCars.length > 0 ? `<div class="garage-summary-delta" style="color:${deltaColor}">${deltaSign} ${esc(fmtPrice(Math.abs(delta)))} \\u00b7 ${deltaSign}${Math.abs(deltaPercent).toFixed(1)} % depuis acquisition</div>` : \'\'}
        ${renderGarageSparkline()}
        <div class="garage-summary-meta">
          <span>${valuableCars.length} voiture${valuableCars.length === 1 ? \'\' : \'s\'}</span>
          <span>${totalDocs} document${totalDocs === 1 ? \'\' : \'s\'}</span>
          <span>${totalPhotos} photo${totalPhotos === 1 ? \'\' : \'s\'}</span>
        </div>
        ${inSaleCars.length > 0 ? `<div class="garage-summary-sale">${inSaleCars.length} en vente \\u00b7 suis-les depuis ta fiche voiture</div>` : \'\'}
        ${soldCars.length > 0 ? `<div class="garage-summary-lifetime">${soldCars.length} vendue${soldCars.length > 1 ? \'s\' : \'\'} cumul\\u00e9e${soldCars.length > 1 ? \'s\' : \'\'} \\u00b7 ${esc(fmtPrice(lifetimeSalesTotal))}</div>` : \'\'}
      </div>
      ${renderGarageDeadlinesBlock()}
      <button class="garage-card-add garage-card-add-top" data-action="openAddGarage" onclick="if(window.Actions && window.Actions.openAddGarage) window.Actions.openAddGarage();">'''


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 2 (Phase α) — Garage refonte mid-top",
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 2 (Phase α) — Garage refonte mid-top",
        ),
        Patch(
            name="JS helpers",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 2 (Phase α) — helpers Garage",
        ),
        Patch(
            name="Hero variante C",
            anchor=PATCH_3_ANCHOR,
            replacement=PATCH_3_REPLACEMENT,
            idempotence_marker='<section class="hero hero-garage">',
        ),
        Patch(
            name="KPI + Échéances",
            anchor=PATCH_4_ANCHOR,
            replacement=PATCH_4_REPLACEMENT,
            idempotence_marker="${renderGarageDeadlinesBlock()}",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
