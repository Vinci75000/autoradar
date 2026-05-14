#!/usr/bin/env python3
"""
CARNET · Lot 5 (Phase β) — Co-pilote Actif (rallye TSD)

Source design : carnet_copilote_actif.html
Scope         : Mode plein écran "co-pilote actif" pour rallye TSD
                (Tour de Corse Historique étape 4 Calvi → Corte) :
                roadbook + bande régularité + odomètre + voiture status
                + 7 équipages live + actions bottom.
                Activable via window.CARNET_COPILOTE_DEMO.open() console.
Hors scope    : Détection événement rallye actif via backend → Phase ε
                Wiring depuis Affût ou notification → Phase γ
                Tracking GPS temps réel + écart cumulé live → Phase ε

Applique 2 patches sur index.html :
  1. CSS additions   → styles overlay copilote + sections
  2. JS helpers      → renderCopiloteOverlay() + CARNET_COPILOTE_DEMO

Pas de render hook dans Garage : c'est un mode séparé, pas une section.
Pour démo : window.CARNET_COPILOTE_DEMO.open() dans la console.

Prérequis : Lot 4 (Phase β) appliqué
Usage     :
    python3 apply_copilote_actif_lot5.py path/to/index.html
    python3 apply_copilote_actif_lot5.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions
# Anchor 2 bornes : fin du Lot 4 CSS + </style>, on insère au milieu.
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """.garage-ledger-settle-note{
  font-family:var(--mono);
  font-size:9px;
  color:var(--gris);
  letter-spacing:0.04em;
  text-align:center;
  line-height:1.5;
  margin:0;
}

</style>"""

PATCH_1_REPLACEMENT = """.garage-ledger-settle-note{
  font-family:var(--mono);
  font-size:9px;
  color:var(--gris);
  letter-spacing:0.04em;
  text-align:center;
  line-height:1.5;
  margin:0;
}

/* ═══ LOT 5 (Phase β) — Co-pilote Actif (rallye TSD) ═══════════════════ */

/* Mode overlay plein écran — z-index au-dessus de tout */
.copilote-overlay{
  position:fixed;
  inset:0;
  background:var(--papier);
  color:var(--encre);
  z-index:9999;
  overflow-y:auto;
  overflow-x:hidden;
  font-family:var(--sans);
  -webkit-overflow-scrolling:touch;
}
.copilote-overlay[hidden]{ display:none; }

.copilote-close{
  position:absolute;
  top:14px;
  right:14px;
  width:32px;
  height:32px;
  border-radius:50%;
  background:rgba(244,241,234,0.15);
  color:var(--papier);
  border:none;
  font-family:var(--mono);
  font-size:16px;
  line-height:1;
  cursor:pointer;
  z-index:2;
  display:flex;
  align-items:center;
  justify-content:center;
}
.copilote-close:hover{ background:rgba(244,241,234,0.3); }

/* Header minimal — encre noir, eyebrow + titre + heure + live */
.copilote-header{
  padding:14px 18px;
  background:var(--encre);
  color:var(--papier);
  display:flex;
  justify-content:space-between;
  align-items:center;
  position:relative;
}
.copilote-header-left{ flex:1; }
.copilote-header-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0;
}
.copilote-header-title{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  margin:2px 0 0 0;
  line-height:1.1;
  color:var(--papier);
}
.copilote-header-right{
  text-align:right;
  font-family:var(--mono);
  font-size:11px;
  color:#D5D0C4;
  padding-right:40px;
}
.copilote-header-live{
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
  margin-top:2px;
}

/* Instruction roadbook — central, gros */
.copilote-instruction{
  padding:32px 24px 18px;
  text-align:center;
  background:var(--papier);
}
.copilote-instruction-eyebrow{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 8px 0;
}
.copilote-instruction-arrow{
  width:74px;
  height:74px;
  margin:6px auto 14px;
  display:block;
}
.copilote-instruction-arrow path{
  stroke:var(--orange-polo);
  stroke-width:6;
  stroke-linecap:round;
  stroke-linejoin:round;
  fill:none;
}
.copilote-instruction-title{
  font-family:var(--display);
  font-style:italic;
  font-weight:500;
  font-size:32px;
  margin:0 0 6px 0;
  line-height:1.05;
  letter-spacing:-0.01em;
  color:var(--encre);
}
.copilote-instruction-detail{
  font-family:var(--editorial);
  font-style:italic;
  font-size:15px;
  color:var(--encre-soft);
  line-height:1.4;
  margin:0;
}

/* Bande régularité TSD — encre noir, 3 cols mono */
.copilote-tsd{
  margin:0 18px 18px;
  padding:14px 16px;
  background:var(--encre);
  color:var(--papier);
  border-radius:var(--r);
}
.copilote-tsd-head{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:10px;
}
.copilote-tsd-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
}
.copilote-tsd-target{
  font-family:var(--mono);
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
}
.copilote-tsd-cols{
  display:flex;
  align-items:baseline;
  gap:14px;
}
.copilote-tsd-col{ flex:1; }
.copilote-tsd-col-r{ flex:1; text-align:right; }
.copilote-tsd-col-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.12em;
  color:var(--gris);
  text-transform:uppercase;
}
.copilote-tsd-col-value{
  font-family:var(--display);
  font-style:italic;
  font-size:28px;
  letter-spacing:-0.01em;
  margin-top:2px;
  color:var(--papier);
}
.copilote-tsd-col-value.is-positive{ color:#9FE1CB; }
.copilote-tsd-col-value.is-negative{ color:var(--orange-polo); }

/* Odomètre + ETA — 2 cards papier-soft */
.copilote-odo{ padding:0 22px 18px; }
.copilote-odo-row{ display:flex; gap:8px; }
.copilote-odo-card{
  flex:1;
  padding:12px 14px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
}
.copilote-odo-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.12em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 4px 0;
}
.copilote-odo-value{
  font-family:var(--display);
  font-style:italic;
  font-size:18px;
  letter-spacing:-0.01em;
  color:var(--encre);
  margin:0;
}

/* Voiture status — bord gauche vert anglais */
.copilote-status{ padding:0 22px 18px; }
.copilote-status-card{
  display:flex;
  align-items:center;
  gap:12px;
  padding:12px 14px;
  background:#FAFAF7;
  border-left:3px solid var(--vert-anglais);
  border-radius:var(--r);
}
.copilote-status-thumb{
  width:32px;
  height:32px;
  background:#D5D0C4;
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--display);
  font-style:italic;
  color:#6B655B;
  font-size:12px;
  border-radius:var(--r);
  flex-shrink:0;
}
.copilote-status-body{ flex:1; min-width:0; }
.copilote-status-title{
  font-family:var(--display);
  font-style:italic;
  font-size:14px;
  color:var(--encre);
  margin:0;
}
.copilote-status-meta{
  font-family:var(--mono);
  font-size:9px;
  color:#6B655B;
  letter-spacing:0.04em;
  margin:1px 0 0 0;
}

/* Bande participants — 7 équipages live tracking horizontal scroll */
.copilote-participants{ padding:0 22px 18px; }
.copilote-participants-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.16em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 10px 0;
}
.copilote-participants-track{
  display:flex;
  gap:8px;
  overflow-x:auto;
  padding-bottom:4px;
  -webkit-overflow-scrolling:touch;
}
.copilote-participant{
  flex-shrink:0;
  padding:8px 10px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
  min-width:90px;
}
.copilote-participant.is-self{
  background:var(--orange-polo);
  border-color:var(--orange-polo);
}
.copilote-participant.is-overflow{
  background:#FAFAF7;
  border-style:dashed;
  border-color:#D5D0C4;
  min-width:60px;
  display:flex;
  align-items:center;
  justify-content:center;
}
.copilote-participant-head{
  display:flex;
  align-items:center;
  gap:6px;
  margin-bottom:3px;
}
.copilote-participant-avatar{
  width:16px;
  height:16px;
  border-radius:50%;
  color:var(--papier);
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--mono);
  font-size:8px;
  flex-shrink:0;
}
.copilote-participant-name{
  font-family:var(--mono);
  font-size:10px;
  font-weight:500;
  color:var(--encre);
}
.copilote-participant.is-self .copilote-participant-name{ color:var(--papier); }
.copilote-participant-gap{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.04em;
}
.copilote-participant-gap.is-ahead{ color:var(--vert-anglais); }
.copilote-participant-gap.is-near{ color:#6B655B; }
.copilote-participant-gap.is-behind{ color:var(--or); }
.copilote-participant.is-self .copilote-participant-gap{ color:var(--papier); }
.copilote-participant-overflow-text{
  font-family:var(--mono);
  font-size:11px;
  color:var(--gris);
}

/* Bottom actions — 3 boutons grid */
.copilote-actions{
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:1px;
  background:#D5D0C4;
  border-top:1px solid #D5D0C4;
  margin-top:8px;
}
.copilote-action{
  padding:14px 0;
  background:var(--papier);
  border:none;
  cursor:pointer;
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--encre);
}
.copilote-action.is-alert{ color:var(--orange-polo); }
.copilote-action-icon{
  font-size:18px;
  margin-bottom:2px;
  display:block;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers + demo opener
# Anchor 2 bornes : marker fin /Lot 4 + début renderGaragePage,
# on insère les helpers Lot 5 + un nouveau marker /Lot 5.
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """// ─── /Lot 4 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """// ─── /Lot 4 helpers ──────────────────────────────────────────────────

// ─── Lot 5 (Phase β) — helpers Co-pilote Actif (rallye TSD) ──────────
//
// Phase β = mode plein écran activable via console pour démo :
//           > window.CARNET_COPILOTE_DEMO.open()
//           > window.CARNET_COPILOTE_DEMO.close()
//
// Phase γ ajoutera : trigger UI depuis Affût quand événement rallye
//                    détecté, deep-link URL.
// Phase ε ajoutera : tracking GPS temps réel + écart cumulé live +
//                    sync avec backend rallye.

window.CARNET_COPILOTE_MOCK = window.CARNET_COPILOTE_MOCK || {
  event: {
    series: 'Tour de Corse Historique',
    day: 'J2',
    stage: '\\u00c9tape 4 \\u00b7 Calvi \\u2192 Corte',
    time_label: '14h 32',
    live: true
  },
  instruction: {
    distance_label: 'dans 1,2 km',
    title: 'Droite serr\\u00e9e 3.',
    detail: 'Attention cr\\u00eate juste apr\\u00e8s \\u00b7 rev\\u00eatement gravillonn\\u00e9 sur 80 m.',
    arrow_rotation: 60   // degr\u00e9s de rotation, 0 = nord, 90 = est, etc.
  },
  tsd: {
    target_kmh: 52.0,
    instant_kmh: 54.3,
    avg_stage_kmh: 51.8,
    delta_seconds: 3,
    delta_sign: '+'      // '+' = en avance, '-' = en retard
  },
  odometer: {
    stage_done_km: 28.4,
    stage_total_km: 47.1,
    eta_label: '14h 53'
  },
  car_status: {
    label: 'M3',
    title: 'E30 M3 \\u00b7 tout va bien',
    meta: 'Temp\\u00e9rature 92\\u00b0 \\u00b7 pression bonne \\u00b7 124 478 km'
  },
  participants: [
    { initial: 'M', name: 'Marc',    color: '#1A1A18', gap_label: '+2,1 km devant',  gap_class: 'is-ahead'  },
    { initial: 'A', name: 'Antoine', color: '#1F4D2F', gap_label: '+0,4 km',         gap_class: 'is-near'   },
    { initial: 'S', name: 'Toi',     color: '#1A1A18', gap_label: 'point ref.',      gap_class: '', isSelf: true },
    { initial: 'J', name: 'Julien',  color: '#BA7517', gap_label: '\\u20131,8 km derri\\u00e8re', gap_class: 'is-behind' }
  ],
  participants_overflow: 3,
  participants_total: 7
};

function renderCopiloteArrow(rotationDeg){
  // Flèche directionnelle SVG avec rotation passée en paramètre.
  const rot = (typeof rotationDeg === 'number') ? rotationDeg : 0;
  return `<svg class="copilote-instruction-arrow" viewBox="0 0 100 100">
    <path d="M50 90 L50 25 M50 25 L25 50 M50 25 L75 50" transform="rotate(${rot} 50 50)"/>
  </svg>`;
}

function renderCopiloteParticipant(p){
  const cls = p.isSelf ? 'copilote-participant is-self' : 'copilote-participant';
  const gapCls = p.gap_class ? `copilote-participant-gap ${p.gap_class}` : 'copilote-participant-gap';
  return `
    <div class="${cls}">
      <div class="copilote-participant-head">
        <div class="copilote-participant-avatar" style="background:${esc(p.color)}">${esc(p.initial)}</div>
        <span class="copilote-participant-name">${esc(p.name)}</span>
      </div>
      <div class="${gapCls}">${esc(p.gap_label)}</div>
    </div>`;
}

function renderCopiloteOverlay(){
  // Lot 5 (Phase β) — mode plein écran rallye TSD, mock data.
  const data = window.CARNET_COPILOTE_MOCK;
  if (!data) return '';

  const participantsHtml = (data.participants || []).map(renderCopiloteParticipant).join('');
  const overflowHtml = (data.participants_overflow > 0) ? `
    <div class="copilote-participant is-overflow">
      <span class="copilote-participant-overflow-text">+${data.participants_overflow}</span>
    </div>` : '';

  const tsd = data.tsd || {};
  const deltaClass = tsd.delta_sign === '+' ? 'is-positive' : (tsd.delta_sign === '-' ? 'is-negative' : '');
  const deltaSecLabel = (tsd.delta_sign || '+') + (tsd.delta_seconds || 0) + '\\u2033';

  const odo = data.odometer || {};
  const car = data.car_status || {};
  const ev  = data.event || {};
  const ins = data.instruction || {};

  return `
    <button type="button" class="copilote-close" data-action="closeCopilote" aria-label="Fermer">\\u00d7</button>

    <div class="copilote-header">
      <div class="copilote-header-left">
        <p class="copilote-header-eyebrow">${esc(ev.series || '')} \\u00b7 ${esc(ev.day || '')}</p>
        <p class="copilote-header-title">${esc(ev.stage || '')}</p>
      </div>
      <div class="copilote-header-right">
        <div>${esc(ev.time_label || '')}</div>
        ${ev.live ? '<div class="copilote-header-live">\\u25cf live</div>' : ''}
      </div>
    </div>

    <div class="copilote-instruction">
      <p class="copilote-instruction-eyebrow">Prochain \\u00b7 ${esc(ins.distance_label || '')}</p>
      ${renderCopiloteArrow(ins.arrow_rotation)}
      <h2 class="copilote-instruction-title">${esc(ins.title || '')}</h2>
      <p class="copilote-instruction-detail">${esc(ins.detail || '')}</p>
    </div>

    <div class="copilote-tsd">
      <div class="copilote-tsd-head">
        <span class="copilote-tsd-label">R\\u00e9gularit\\u00e9 \\u00b7 vitesse moyenne cible</span>
        <span class="copilote-tsd-target">cible ${(tsd.target_kmh || 0).toFixed(1).replace('.',',')} km/h</span>
      </div>
      <div class="copilote-tsd-cols">
        <div class="copilote-tsd-col">
          <div class="copilote-tsd-col-label">Instantan\\u00e9e</div>
          <div class="copilote-tsd-col-value">${(tsd.instant_kmh || 0).toFixed(1).replace('.',',')}</div>
        </div>
        <div class="copilote-tsd-col">
          <div class="copilote-tsd-col-label">Moyenne \\u00e9tape</div>
          <div class="copilote-tsd-col-value">${(tsd.avg_stage_kmh || 0).toFixed(1).replace('.',',')}</div>
        </div>
        <div class="copilote-tsd-col-r">
          <div class="copilote-tsd-col-label">\\u00c9cart cumul\\u00e9</div>
          <div class="copilote-tsd-col-value ${deltaClass}">${esc(deltaSecLabel)}</div>
        </div>
      </div>
    </div>

    <div class="copilote-odo">
      <div class="copilote-odo-row">
        <div class="copilote-odo-card">
          <p class="copilote-odo-label">\\u00c9tape</p>
          <p class="copilote-odo-value">${(odo.stage_done_km || 0).toFixed(1).replace('.',',')} / ${(odo.stage_total_km || 0).toFixed(1).replace('.',',')} km</p>
        </div>
        <div class="copilote-odo-card">
          <p class="copilote-odo-label">Arriv\\u00e9e pr\\u00e9vue</p>
          <p class="copilote-odo-value">${esc(odo.eta_label || '')}</p>
        </div>
      </div>
    </div>

    <div class="copilote-status">
      <div class="copilote-status-card">
        <div class="copilote-status-thumb">${esc(car.label || '?')}</div>
        <div class="copilote-status-body">
          <p class="copilote-status-title">${esc(car.title || '')}</p>
          <p class="copilote-status-meta">${esc(car.meta || '')}</p>
        </div>
      </div>
    </div>

    <div class="copilote-participants">
      <p class="copilote-participants-label">Sur la route \\u00b7 ${data.participants_total || (data.participants || []).length} \\u00e9quipages</p>
      <div class="copilote-participants-track">
        ${participantsHtml}
        ${overflowHtml}
      </div>
    </div>

    <div class="copilote-actions">
      <button type="button" class="copilote-action" data-action="copilotePhoto">
        <span class="copilote-action-icon">\\ud83d\\udcf7</span>
        Photo
      </button>
      <button type="button" class="copilote-action" data-action="copiloteNote">
        <span class="copilote-action-icon">\\u270e</span>
        Note
      </button>
      <button type="button" class="copilote-action is-alert" data-action="copiloteAlert">
        <span class="copilote-action-icon">\\u26a0</span>
        Signaler
      </button>
    </div>
  `;
}

// API démo accessible via console
window.CARNET_COPILOTE_DEMO = {
  open: function(){
    let overlay = document.getElementById('carnet-copilote-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'carnet-copilote-overlay';
      overlay.className = 'copilote-overlay';
      document.body.appendChild(overlay);
      // Listener fermeture
      overlay.addEventListener('click', function(e){
        const btn = e.target.closest('[data-action="closeCopilote"]');
        if (btn) window.CARNET_COPILOTE_DEMO.close();
      });
    }
    overlay.innerHTML = renderCopiloteOverlay();
    overlay.removeAttribute('hidden');
    // Bloquer scroll body en arrière-plan
    document.body.style.overflow = 'hidden';
  },
  close: function(){
    const overlay = document.getElementById('carnet-copilote-overlay');
    if (overlay) overlay.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
};
// ─── /Lot 5 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 5 (Phase β) — Co-pilote Actif (rallye TSD)",
    requires=[
        "LOT 4 (Phase β) — Ledger Events + Settlement RLUSD",
    ],
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 5 (Phase β) — Co-pilote Actif",
        ),
        Patch(
            name="JS helpers + demo opener",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 5 (Phase β) — helpers Co-pilote Actif",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
