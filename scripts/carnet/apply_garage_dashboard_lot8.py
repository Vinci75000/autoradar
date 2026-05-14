#!/usr/bin/env python3
"""
CARNET · Lot 8 (Phase α) — Garage Dashboard Complet

Source design : carnet_garage_dashboard_complet.html (sections 5-9)
Scope         : 5 nouvelles sections dans renderGaragePage, entre
                ${archivesSection} et ${renderGarageLedgerSection()} :

  1. Souvenirs · cette saison (horizontal scroll, photos + caption italique)
  2. Patrimoine · timing (tax timing test — plus-value exonérée 22 ans)
  3. Carnet on-chain · XRPL (certificats émis + ligne "émettre")
  4. L'affût · pour toi (alerte sous-cotée avec score + tags)
  5. La tribu · près de toi (avatars locaux + RSVP événement)

Hors scope    : Données réelles (Supabase) → Phase δ
                Mint XRPL certificat réel → Phase ε
                Geo-clustering tribu → Phase ε
                Recommandation marché algorithmique → Phase ε

Applique 3 patches sur index.html :
  1. CSS additions   → styles des 5 sections
  2. JS helpers      → 5 fonctions renderGarageXxxSection + data mock
  3. Render hook     → insertion des 5 sections entre archives et ledger

Prérequis : Lot 7 (Phase γ) appliqué
Usage     :
    python3 apply_garage_dashboard_lot8.py path/to/index.html
    python3 apply_garage_dashboard_lot8.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions
# Anchor 2 bornes : fin du Lot 7 CSS + </style>
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """.gumball-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

</style>"""

PATCH_1_REPLACEMENT = """.gumball-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

/* ═══ LOT 8 (Phase α) — Garage Dashboard Complet ═══════════════════════ */

/* Header générique de section dashboard */
.garage-dash-section{ margin:32px 22px 4px; }
.garage-dash-section.is-flush{ margin-left:0; margin-right:0; }
.garage-dash-header{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:14px;
}
.garage-dash-title{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-dash-action{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.12em;
  color:var(--orange-polo);
  text-transform:uppercase;
  text-decoration:none;
  background:none;
  border:none;
  padding:0;
  cursor:pointer;
}
.garage-dash-action:hover{ text-decoration:underline; text-underline-offset:3px; }

/* Section 1 — Souvenirs (cette saison) */
.garage-memories-track{
  display:flex;
  gap:10px;
  overflow-x:auto;
  padding-bottom:6px;
  -webkit-overflow-scrolling:touch;
}
.garage-memory-card{
  flex:0 0 220px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
  overflow:hidden;
  cursor:pointer;
  font:inherit;
  color:inherit;
  text-align:left;
  padding:0;
}
.garage-memory-card:hover{ border-color:var(--encre); }
.garage-memory-photo{
  aspect-ratio:1.6/1;
  background:#D5D0C4;
}
.garage-memory-body{ padding:12px; }
.garage-memory-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.14em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 4px 0;
}
.garage-memory-caption{
  font-family:var(--editorial);
  font-style:italic;
  font-size:16px;
  line-height:1.3;
  color:var(--encre);
  margin:0;
}
.garage-memory-meta{
  font-family:var(--mono);
  font-size:9px;
  color:#6B655B;
  letter-spacing:0.04em;
  margin:6px 0 0 0;
}

/* Section 2 — Patrimoine · timing (tax timing test, encre noir block) */
.garage-tax-card{
  background:var(--encre);
  color:var(--papier);
  border-radius:var(--r);
  padding:18px 20px;
}
.garage-tax-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--or);
  text-transform:uppercase;
  margin:0 0 8px 0;
}
.garage-tax-text{
  font-family:var(--editorial);
  font-style:italic;
  font-size:18px;
  line-height:1.35;
  margin:0 0 10px 0;
  color:var(--papier);
}
.garage-tax-text em{ font-style:italic; }
.garage-tax-meta{
  font-family:var(--mono);
  font-size:11px;
  color:#9FE1CB;
  letter-spacing:0.03em;
  margin:0;
}

/* Section 3 — Carnet on-chain · XRPL */
.garage-chain-list{
  display:flex;
  flex-direction:column;
  gap:8px;
}
.garage-chain-row{
  display:flex;
  align-items:center;
  gap:12px;
  padding:11px 14px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
}
.garage-chain-row.is-pending{
  border-style:dashed;
  border-color:#D5D0C4;
  cursor:pointer;
}
.garage-chain-row.is-pending:hover{ border-color:var(--orange-polo); }
.garage-chain-icon{
  width:24px;
  height:24px;
  border-radius:50%;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  font-family:var(--mono);
  font-size:10px;
  font-weight:500;
  flex-shrink:0;
}
.garage-chain-icon.is-done{
  background:var(--vert-anglais);
  color:var(--papier);
}
.garage-chain-icon.is-pending{
  background:transparent;
  border:1px solid #D5D0C4;
  color:var(--gris);
}
.garage-chain-body{ flex:1; min-width:0; }
.garage-chain-title{
  font-family:var(--display);
  font-style:italic;
  font-size:14px;
  color:var(--encre);
  line-height:1.2;
  margin:0;
}
.garage-chain-row.is-pending .garage-chain-title{
  font-family:var(--editorial);
  color:#6B655B;
}
.garage-chain-meta{
  font-family:var(--mono);
  font-size:9px;
  color:#6B655B;
  letter-spacing:0.04em;
  margin:1px 0 0 0;
}
.garage-chain-row.is-pending .garage-chain-meta{ color:var(--gris); }
.garage-chain-arrow{
  font-family:var(--mono);
  font-size:14px;
  color:var(--orange-polo);
  flex-shrink:0;
}

/* Section 4 — L'affût · pour toi (opportunité marché) */
.garage-opp-card{
  padding:18px;
  background:#FAFAF7;
  border:1px dashed var(--vert-anglais);
  border-radius:var(--r);
}
.garage-opp-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--vert-anglais);
  text-transform:uppercase;
  margin:0 0 8px 0;
}
.garage-opp-title{
  font-family:var(--display);
  font-style:italic;
  font-weight:500;
  font-size:22px;
  margin:0 0 6px 0;
  line-height:1.1;
  letter-spacing:-0.01em;
  color:var(--encre);
}
.garage-opp-desc{
  font-family:var(--editorial);
  font-style:italic;
  font-size:14px;
  color:var(--encre-soft);
  line-height:1.45;
  margin:0 0 12px 0;
}
.garage-opp-desc strong{
  font-weight:500;
  font-style:normal;
  font-family:var(--mono);
  font-size:12px;
  letter-spacing:0.02em;
}
.garage-opp-chips{ display:flex; gap:8px; flex-wrap:wrap; }
.garage-opp-chip{
  font-family:var(--mono);
  font-size:9px;
  color:var(--encre);
  padding:4px 8px;
  background:rgba(31,77,47,0.1);
  border-radius:var(--r);
  letter-spacing:0.04em;
  text-transform:uppercase;
}

/* Section 5 — La tribu · près de toi */
.garage-tribu-card{
  padding:18px 20px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
}
.garage-tribu-avatars{
  display:flex;
  margin-bottom:12px;
}
.garage-tribu-avatar{
  width:30px;
  height:30px;
  border-radius:50%;
  color:var(--papier);
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--mono);
  font-size:10px;
  border:2px solid #FAFAF7;
}
.garage-tribu-avatar + .garage-tribu-avatar{ margin-left:-8px; }
.garage-tribu-text{
  font-family:var(--editorial);
  font-style:italic;
  font-size:16px;
  line-height:1.4;
  color:var(--encre-soft);
  margin:0 0 10px 0;
}
.garage-tribu-rsvp{ display:flex; gap:8px; }
.garage-tribu-rsvp-btn{
  font-family:var(--mono);
  font-size:10px;
  padding:5px 10px;
  border-radius:var(--r);
  letter-spacing:0.08em;
  text-transform:uppercase;
  cursor:pointer;
  background:transparent;
}
.garage-tribu-rsvp-btn.is-primary{
  color:var(--orange-polo);
  border:1px solid var(--orange-polo);
}
.garage-tribu-rsvp-btn.is-secondary{
  color:var(--encre);
  border:1px solid var(--gris-line);
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers
# Anchor 2 bornes : marker fin /Lot 7 + début renderGaragePage
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """// ─── /Lot 7 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """// ─── /Lot 7 helpers ──────────────────────────────────────────────────

// ─── Lot 8 (Phase α) — helpers Garage Dashboard Complet ──────────────
//
// Phase α = 5 sections lecture seule avec data mockée :
//   - Souvenirs (cette saison)
//   - Patrimoine timing (tax test)
//   - Carnet on-chain XRPL
//   - Opportunités marché (Affût teaser)
//   - Tribu (collectionneurs locaux)
//
// Phase δ branchera : Supabase events/memories, NHTSA/Hagerty market data,
//                     XRPL transactions réelles, geo-clustering tribu.

window.CARNET_DASHBOARD_MOCK = window.CARNET_DASHBOARD_MOCK || {
  memories: [
    {
      eyebrow: 'Route des Alpes',
      caption: 'Col du Galibier avec L\\u00e9a.',
      meta: '12 juil. \\u00b7 993 \\u00b7 420 km'
    },
    {
      eyebrow: 'Atelier',
      caption: '\\u00c9chappement d\\u2019origine retrouv\\u00e9.',
      meta: '28 juin \\u00b7 F355 \\u00b7 Marc D.'
    },
    {
      eyebrow: 'Rallye',
      caption: 'Tour Auto \\u00b7 Class C podium.',
      meta: '04 mai \\u00b7 M3 \\u00b7 7 amis'
    }
  ],
  tax_timing: {
    eyebrow_label: 'Plus-value exon\\u00e9r\\u00e9e \\u00b7 dans 8 mois',
    text: '<em>Ton 993 atteint 22 ans en mai 2027.</em> Au-del\\u00e0, plus-value de cession totalement exon\\u00e9r\\u00e9e d\\u2019imp\\u00f4t.',
    meta: 'Plus-value latente : +84 000 \\u20ac \\u00b7 \\u00e9conomie potentielle ~30 600 \\u20ac'
  },
  blockchain: {
    label: 'Carnet on-chain \\u00b7 XRPL',
    count_label: '2/4 certifi\\u00e9es',
    certificates: [
      {
        car_label: 'Porsche 993 \\u00b7 Certificat #0427',
        meta: 'Mint 12.03.2026 \\u00b7 provenance 3 propri\\u00e9taires',
        status: 'done'
      },
      {
        car_label: 'BMW E30 M3 \\u00b7 Certificat #0612',
        meta: 'Mint 28.04.2026 \\u00b7 ECR r\\u00e9f\\u00e9renc\\u00e9e',
        status: 'done'
      },
      {
        car_label: '\\u00c9mettre certificat \\u00b7 Ferrari F355',
        meta: '3 minutes \\u00b7 ~0,01 XRP',
        status: 'pending'
      }
    ]
  },
  market_opp: {
    eyebrow_label: 'SOUS-COT\\u00c9E \\u00b7 \\u201312 % vs march\\u00e9',
    title: 'Porsche 964 Carrera 2.',
    desc_html: '1991, 89 000 km, historique complet. Allemagne du Sud. <strong>78 200 \\u20ac</strong>. Cote Carnet 89 000 \\u20ac.',
    chips: ['Compl\\u00e8te la collection', 'Score 87/100']
  },
  tribu: {
    avatars: [
      { initial: 'M', color: '#1A1A18' },
      { initial: 'A', color: '#1F4D2F' },
      { initial: 'J', color: '#E85A1F' },
      { initial: '+9', color: '#BA7517' }
    ],
    text: '12 collectionneurs CARNET \\u00e0 moins de 50 km. Rassemblement \\u00ab Aircooled Sunday \\u00bb le 21 septembre.',
    rsvp: [
      { label: 'Je viens',  primary: true,  action: 'tribuRsvpYes'   },
      { label: 'Plus tard', primary: false, action: 'tribuRsvpLater' }
    ]
  }
};

function renderGarageMemoryCard(m){
  return `
    <button type="button" class="garage-memory-card" data-action="openMemory">
      <div class="garage-memory-photo"></div>
      <div class="garage-memory-body">
        <p class="garage-memory-eyebrow">${esc(m.eyebrow || '')}</p>
        <p class="garage-memory-caption">${esc(m.caption || '')}</p>
        <p class="garage-memory-meta">${esc(m.meta || '')}</p>
      </div>
    </button>`;
}

function renderGarageMemoriesSection(){
  const data = window.CARNET_DASHBOARD_MOCK;
  if (!data || !data.memories || data.memories.length === 0) return '';
  const cardsHtml = data.memories.map(renderGarageMemoryCard).join('');
  return `
    <div class="garage-dash-section">
      <div class="garage-dash-header">
        <span class="garage-dash-title">Cette saison \\u00b7 souvenirs</span>
        <button type="button" class="garage-dash-action" data-action="openAllMemories">tout voir</button>
      </div>
      <div class="garage-memories-track">${cardsHtml}</div>
    </div>`;
}

function renderGarageTaxTimingSection(){
  const data = window.CARNET_DASHBOARD_MOCK;
  if (!data || !data.tax_timing) return '';
  const t = data.tax_timing;
  // text contient <em>...</em> autorisé pour mise en valeur
  return `
    <div class="garage-dash-section">
      <div class="garage-dash-header">
        <span class="garage-dash-title">Patrimoine \\u00b7 timing</span>
      </div>
      <div class="garage-tax-card">
        <p class="garage-tax-eyebrow">${esc(t.eyebrow_label || '')}</p>
        <p class="garage-tax-text">${t.text || ''}</p>
        <p class="garage-tax-meta">${esc(t.meta || '')}</p>
      </div>
    </div>`;
}

function renderGarageChainRow(c){
  const isDone = c.status === 'done';
  const rowCls = isDone ? 'garage-chain-row' : 'garage-chain-row is-pending';
  const iconCls = isDone ? 'garage-chain-icon is-done' : 'garage-chain-icon is-pending';
  const iconChar = isDone ? '\\u2713' : '+';
  const arrow = isDone ? '' : '<span class="garage-chain-arrow">\\u2192</span>';
  return `
    <div class="${rowCls}" ${isDone ? '' : 'data-action="openMintCertificate"'}>
      <div class="${iconCls}">${iconChar}</div>
      <div class="garage-chain-body">
        <p class="garage-chain-title">${esc(c.car_label || '')}</p>
        <p class="garage-chain-meta">${esc(c.meta || '')}</p>
      </div>
      ${arrow}
    </div>`;
}

function renderGarageBlockchainSection(){
  const data = window.CARNET_DASHBOARD_MOCK;
  if (!data || !data.blockchain || !data.blockchain.certificates) return '';
  const b = data.blockchain;
  const rowsHtml = b.certificates.map(renderGarageChainRow).join('');
  return `
    <div class="garage-dash-section">
      <div class="garage-dash-header">
        <span class="garage-dash-title">${esc(b.label || 'Carnet on-chain')}</span>
        <span class="garage-dash-action" style="color:var(--orange-polo);">${esc(b.count_label || '')}</span>
      </div>
      <div class="garage-chain-list">${rowsHtml}</div>
    </div>`;
}

function renderGarageMarketOppsSection(){
  const data = window.CARNET_DASHBOARD_MOCK;
  if (!data || !data.market_opp) return '';
  const o = data.market_opp;
  const chipsHtml = (o.chips || []).map(c =>
    `<span class="garage-opp-chip">${esc(c)}</span>`
  ).join('');
  return `
    <div class="garage-dash-section">
      <div class="garage-dash-header">
        <span class="garage-dash-title">L\\u2019aff\\u00fbt \\u00b7 pour toi</span>
        <button type="button" class="garage-dash-action" data-action="openMarketOpps">3 alertes</button>
      </div>
      <div class="garage-opp-card">
        <p class="garage-opp-eyebrow">${esc(o.eyebrow_label || '')}</p>
        <h3 class="garage-opp-title">${esc(o.title || '')}</h3>
        <p class="garage-opp-desc">${o.desc_html || ''}</p>
        <div class="garage-opp-chips">${chipsHtml}</div>
      </div>
    </div>`;
}

function renderGarageTribuAvatar(a){
  return `<div class="garage-tribu-avatar" style="background:${esc(a.color || '#1A1A18')}">${esc(a.initial)}</div>`;
}

function renderGarageTribuRsvp(r){
  const cls = r.primary ? 'garage-tribu-rsvp-btn is-primary' : 'garage-tribu-rsvp-btn is-secondary';
  const action = r.action || 'tribuRsvp';
  return `<button type="button" class="${cls}" data-action="${esc(action)}">${esc(r.label)}</button>`;
}

function renderGarageTribuSection(){
  const data = window.CARNET_DASHBOARD_MOCK;
  if (!data || !data.tribu) return '';
  const t = data.tribu;
  const avatarsHtml = (t.avatars || []).map(renderGarageTribuAvatar).join('');
  const rsvpHtml = (t.rsvp || []).map(renderGarageTribuRsvp).join('');
  return `
    <div class="garage-dash-section" style="padding-bottom:6px;">
      <div class="garage-dash-header">
        <span class="garage-dash-title">La tribu \\u00b7 pr\\u00e8s de toi</span>
      </div>
      <div class="garage-tribu-card">
        <div class="garage-tribu-avatars">${avatarsHtml}</div>
        <p class="garage-tribu-text">${esc(t.text || '')}</p>
        <div class="garage-tribu-rsvp">${rsvpHtml}</div>
      </div>
    </div>`;
}
// ─── /Lot 8 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — Render hook (insertion entre archivesSection et ledger)
# Anchor 2 bornes : ${archivesSection} + ${renderGarageLedgerSection()}
# ═══════════════════════════════════════════════════════════════════════

PATCH_3_ANCHOR = """      ${archivesSection}
      ${renderGarageLedgerSection()}"""

PATCH_3_REPLACEMENT = """      ${archivesSection}
      ${renderGarageMemoriesSection()}
      ${renderGarageTaxTimingSection()}
      ${renderGarageBlockchainSection()}
      ${renderGarageMarketOppsSection()}
      ${renderGarageTribuSection()}
      ${renderGarageLedgerSection()}"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 8 (Phase α) — Garage Dashboard Complet",
    requires=[
        "LOT 7 (Phase γ) — Gumball Convoy Mode C",
    ],
    patches=[
        Patch(
            name="CSS additions (5 sections)",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 8 (Phase α) — Garage Dashboard Complet",
        ),
        Patch(
            name="JS helpers (5 fonctions + mock)",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 8 (Phase α) — helpers Garage Dashboard",
        ),
        Patch(
            name="Render hook (5 sections insérées)",
            anchor=PATCH_3_ANCHOR,
            replacement=PATCH_3_REPLACEMENT,
            idempotence_marker="${renderGarageMemoriesSection()}",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
