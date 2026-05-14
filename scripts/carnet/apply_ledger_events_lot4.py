#!/usr/bin/env python3
"""
CARNET · Lot 4 (Phase β) — Ledger Events + Settlement RLUSD

Source design : carnet_ledger_events.html (Mockup 1)
Scope         : Section "Événements ledger récents" dans Garage —
                entretien partagé sur voiture co-owned avec breakdown
                facture + répartition co-owners + CTA settlement RLUSD.
                Données mockées (Ferrari F355 GTS, révision 60 000 km,
                33 200 €, 50/50 toi + père).
Hors scope    : Mockup 2 (track day pot commun) → Lot 5+
                Signature on-chain réelle XRPL → Phase ε avec backend Xaman
                Wiring depuis fiche voiture → Phase δ

Applique 3 patches sur index.html :
  1. CSS additions   → styles ledger event card + facture + split + CTA
  2. JS helpers      → renderGarageLedgerSection() + helpers internes
  3. Render hook     → insertion AVANT ${renderGarageCirclesSection()}

Prérequis : Lot 3 (Phase β) appliqué
Usage     :
    python3 apply_ledger_events_lot4.py path/to/index.html
    python3 apply_ledger_events_lot4.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions
# Anchor 2 bornes : fin du Lot 3 CSS + </style>, on insère au milieu.
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """  color:#9FE1CB;
  padding:4px 8px;
  background:rgba(159,225,203,0.1);
  border-radius:var(--r);
  letter-spacing:0.04em;
  text-transform:uppercase;
}

</style>"""

PATCH_1_REPLACEMENT = """  color:#9FE1CB;
  padding:4px 8px;
  background:rgba(159,225,203,0.1);
  border-radius:var(--r);
  letter-spacing:0.04em;
  text-transform:uppercase;
}

/* ═══ LOT 4 (Phase β) — Ledger Events + Settlement RLUSD ═══════════════ */

/* Section ledger events récents — wrapper */
.garage-ledger{ margin:34px 0 18px; }
.garage-ledger-header{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:12px;
}
.garage-ledger-title{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-ledger-link{
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
.garage-ledger-link:hover{ text-decoration:underline; text-underline-offset:3px; }

/* Card individuel d'un ledger event */
.garage-ledger-event{
  padding:22px 20px 24px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
}
.garage-ledger-eyebrow{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 6px 0;
}
.garage-ledger-title-h{
  font-family:var(--display);
  font-style:italic;
  font-weight:500;
  font-size:24px;
  line-height:1.05;
  letter-spacing:-0.01em;
  margin:0 0 6px 0;
  color:var(--encre);
}
.garage-ledger-sub{
  font-family:var(--editorial);
  font-style:italic;
  font-size:14px;
  color:var(--encre-soft);
  line-height:1.5;
  margin:0 0 18px 0;
}

/* Bloc détail facture */
.garage-ledger-detail{
  background:var(--papier);
  border:1px solid var(--gris-line);
  border-radius:var(--r);
  padding:14px;
  margin-bottom:14px;
}
.garage-ledger-detail-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding-bottom:8px;
  border-bottom:1px solid var(--gris-line);
  margin-bottom:8px;
}
.garage-ledger-detail-label{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.12em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-ledger-detail-signed{
  font-family:var(--mono);
  font-size:9px;
  color:var(--vert-anglais);
  letter-spacing:0.04em;
}
.garage-ledger-detail-row{
  display:flex;
  justify-content:space-between;
  font-family:var(--mono);
  font-size:11px;
  color:var(--encre-soft);
  line-height:1.8;
}
.garage-ledger-detail-total{
  display:flex;
  justify-content:space-between;
  font-family:var(--mono);
  font-size:11px;
  font-weight:500;
  color:var(--encre);
  border-top:1px solid var(--gris-line);
  padding-top:8px;
  margin-top:6px;
}
.garage-ledger-detail-total-label{
  letter-spacing:0.04em;
  text-transform:uppercase;
  font-size:10px;
}

/* Répartition co-owners */
.garage-ledger-split-title{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.16em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 10px 0;
}
.garage-ledger-split-list{
  display:flex;
  flex-direction:column;
  gap:6px;
  margin-bottom:18px;
}
.garage-ledger-split-row{
  display:flex;
  align-items:center;
  gap:12px;
  padding:12px 14px;
  background:var(--papier);
  border:1px solid var(--gris-line);
  border-radius:var(--r);
}
.garage-ledger-split-row.is-due{ border-color:var(--orange-polo); }
.garage-ledger-split-avatar{
  width:26px;
  height:26px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--mono);
  font-size:10px;
  color:var(--papier);
  flex-shrink:0;
}
.garage-ledger-split-content{ flex:1; min-width:0; }
.garage-ledger-split-name{
  font-family:var(--display);
  font-style:italic;
  font-size:14px;
  color:var(--encre);
  line-height:1.2;
}
.garage-ledger-split-meta{
  font-family:var(--mono);
  font-size:9px;
  color:var(--gris);
  letter-spacing:0.04em;
  margin-top:1px;
}
.garage-ledger-split-amount{ text-align:right; flex-shrink:0; }
.garage-ledger-split-amount-value{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  color:var(--encre);
  line-height:1.1;
}
.garage-ledger-split-row.is-due .garage-ledger-split-amount-value{ color:var(--orange-polo); }
.garage-ledger-split-amount-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.04em;
  color:var(--vert-anglais);
  margin-top:1px;
}
.garage-ledger-split-row.is-due .garage-ledger-split-amount-label{ color:var(--orange-polo); }

/* CTA settlement */
.garage-ledger-settle{
  width:100%;
  padding:14px 20px;
  background:var(--encre);
  color:var(--papier);
  border:none;
  border-radius:var(--r);
  font-family:var(--mono);
  font-size:11px;
  letter-spacing:0.16em;
  text-transform:uppercase;
  cursor:pointer;
  font-weight:500;
  margin-bottom:10px;
  transition:background 200ms ease;
}
.garage-ledger-settle:hover{ background:var(--orange-polo); }
.garage-ledger-settle-note{
  font-family:var(--mono);
  font-size:9px;
  color:var(--gris);
  letter-spacing:0.04em;
  text-align:center;
  line-height:1.5;
  margin:0;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers
# Anchor 2 bornes : marker fin /Lot 3 + début renderGaragePage,
# on insère les helpers Lot 4 + un nouveau marker /Lot 4.
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """// ─── /Lot 3 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """// ─── /Lot 3 helpers ──────────────────────────────────────────────────

// ─── Lot 4 (Phase β) — helpers Ledger Events + Settlement RLUSD ──────
//
// Phase β = vue lecture seule + mock data + CTA stub.
// Phase ε branchera : Xaman wallet, signature transaction XRPL réelle,
//                     vérification on-chain, lien Bithomp transaction.
//
// Source de vérité provisoire : window.CARNET_LEDGER_MOCK
// Schema sera persisté Supabase table ledger_events Phase δ.

window.CARNET_LEDGER_MOCK = window.CARNET_LEDGER_MOCK || {
  events: [
    {
      id: 'evt_f355_revision_60k',
      car_id: 'f355_gts_1998',
      car_label: 'Ferrari F355',
      type: 'entretien',
      title: 'R\\u00e9vision 60 000 km.',
      provider: 'Garage Marc Davezac',
      date_label: '12 ao\\u00fbt 2026',
      total_amount_eur: 33200,
      signed_pdf: true,
      details: [
        { label: 'Pi\\u00e8ces (joints, courroies, fluides)', amount_eur: 14800 },
        { label: 'Main d\\u2019\\u0153uvre \\u00b7 38 h',          amount_eur: 15200 },
        { label: 'Banc dyno + r\\u00e9glages',                    amount_eur: 3200  }
      ],
      split: [
        {
          who: 'P\\u00e8re',
          role: 'a r\\u00e9gl\\u00e9 l\\u2019atelier',
          initial: 'P',
          color: '#1F4D2F',
          meta: 'Carte pro \\u00b7 14 ao\\u00fbt \\u00b7 justificatif sign\\u00e9',
          amount_eur: 33200,
          status: 'paid',
          status_label: 'avanc\\u00e9 100%'
        },
        {
          who: 'Toi',
          role: 'ta part due',
          initial: 'S',
          color: '#E85A1F',
          meta: 'Quote-part NFT #0856 \\u00b7 50%',
          amount_eur: 16600,
          status: 'due',
          status_label: '\\u00e0 r\\u00e9gler'
        }
      ],
      settlement: {
        currency: 'RLUSD',
        amount: 16600,
        recipient_label: 'mon p\\u00e8re',
        note: 'XRPL \\u00b7 frais ~0,01 \\u20ac \\u00b7 3 sec. \\u00b7 signe le carnet on-chain'
      }
    }
  ]
};

function fmtLedgerPrice(eur){
  // Format \u00e9quivalent fmtPrice mais isol\u00e9 pour ne pas d\u00e9pendre de l'order de boot
  if (typeof eur !== 'number') return '\\u2014';
  return eur.toLocaleString('fr-FR').replace(/\\u00a0/g, ' ') + ' \\u20ac';
}

function renderGarageLedgerDetail(ev){
  const rowsHtml = (ev.details || []).map(d =>
    `<div class="garage-ledger-detail-row">
       <span>${esc(d.label)}</span><span>${fmtLedgerPrice(d.amount_eur)}</span>
     </div>`
  ).join('');
  return `
    <div class="garage-ledger-detail">
      <div class="garage-ledger-detail-head">
        <span class="garage-ledger-detail-label">D\\u00e9tail</span>
        ${ev.signed_pdf ? '<span class="garage-ledger-detail-signed">\\u25cf justificatif PDF sign\\u00e9</span>' : ''}
      </div>
      ${rowsHtml}
      <div class="garage-ledger-detail-total">
        <span class="garage-ledger-detail-total-label">Total TTC</span>
        <span>${fmtLedgerPrice(ev.total_amount_eur)}</span>
      </div>
    </div>`;
}

function renderGarageLedgerSplitRow(s){
  const cls = s.status === 'due' ? 'garage-ledger-split-row is-due' : 'garage-ledger-split-row';
  return `
    <div class="${cls}">
      <div class="garage-ledger-split-avatar" style="background:${esc(s.color || '#1A1A18')}">${esc(s.initial)}</div>
      <div class="garage-ledger-split-content">
        <div class="garage-ledger-split-name"><em>${esc(s.who)} \\u00b7 ${esc(s.role)}</em></div>
        <div class="garage-ledger-split-meta">${esc(s.meta)}</div>
      </div>
      <div class="garage-ledger-split-amount">
        <div class="garage-ledger-split-amount-value">${fmtLedgerPrice(s.amount_eur)}</div>
        <div class="garage-ledger-split-amount-label">${esc(s.status_label)}</div>
      </div>
    </div>`;
}

function renderGarageLedgerEvent(ev){
  const detailHtml = renderGarageLedgerDetail(ev);
  const splitHtml  = (ev.split || []).map(renderGarageLedgerSplitRow).join('');
  const settle     = ev.settlement || null;
  const settleHtml = settle ? `
    <button type="button" class="garage-ledger-settle"
            data-action="openLedgerSettle"
            data-event-id="${esc(ev.id)}">
      R\\u00e9gler ${fmtLedgerPrice(settle.amount).replace(' \\u20ac', '')} ${esc(settle.currency)} \\u00e0 ${esc(settle.recipient_label)}
    </button>
    <p class="garage-ledger-settle-note">${esc(settle.note)}</p>
  ` : '';
  return `
    <div class="garage-ledger-event" data-event-id="${esc(ev.id)}">
      <p class="garage-ledger-eyebrow">${esc(ev.car_label)} \\u00b7 ${esc(ev.type)}</p>
      <h3 class="garage-ledger-title-h"><em>${esc(ev.title)}</em></h3>
      <p class="garage-ledger-sub">${esc(ev.provider)} \\u00b7 ${esc(ev.date_label)} \\u00b7 facture ${fmtLedgerPrice(ev.total_amount_eur)}.</p>
      ${detailHtml}
      <p class="garage-ledger-split-title">R\\u00e9partition \\u00b7 co-owners 50/50</p>
      <div class="garage-ledger-split-list">${splitHtml}</div>
      ${settleHtml}
    </div>`;
}

function renderGarageLedgerSection(){
  // Lot 4 (Phase β) — vue lecture seule, mock data.
  // Phase δ branchera Supabase ledger_events + filter on car_id co-owned.
  const data = window.CARNET_LEDGER_MOCK;
  if (!data || !data.events || data.events.length === 0) {
    return '';
  }
  // Pour cette phase β on montre uniquement le 1er event en teaser.
  const eventsHtml = data.events.slice(0, 1).map(renderGarageLedgerEvent).join('');
  return `
    <div class="garage-ledger">
      <div class="garage-ledger-header">
        <span class="garage-ledger-title">LEDGER \\u00b7 \\u00c9V\\u00c9NEMENTS R\\u00c9CENTS</span>
        ${data.events.length > 1 ? `<button type="button" class="garage-ledger-link" data-action="openLedgerHistory">VOIR TOUT (${data.events.length})</button>` : ''}
      </div>
      ${eventsHtml}
    </div>`;
}
// ─── /Lot 4 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — Render hook (insertion AVANT renderGarageCirclesSection)
# Anchor 2 bornes : hook Lot 3 + fin du rendu garage, insertion au milieu.
# ═══════════════════════════════════════════════════════════════════════

PATCH_3_ANCHOR = """      ${archivesSection}
      ${renderGarageCirclesSection()}
    `;
  }"""

PATCH_3_REPLACEMENT = """      ${archivesSection}
      ${renderGarageLedgerSection()}
      ${renderGarageCirclesSection()}
    `;
  }"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 4 (Phase β) — Ledger Events + Settlement RLUSD",
    requires=[
        "LOT 3 (Phase β) — Garage Social Co-ownership",
    ],
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 4 (Phase β) — Ledger Events + Settlement RLUSD",
        ),
        Patch(
            name="JS helpers",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 4 (Phase β) — helpers Ledger Events",
        ),
        Patch(
            name="Render hook",
            anchor=PATCH_3_ANCHOR,
            replacement=PATCH_3_REPLACEMENT,
            idempotence_marker="${renderGarageLedgerSection()}",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
