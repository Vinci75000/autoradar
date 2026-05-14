#!/usr/bin/env python3
"""
CARNET · Lot 6 (Phase γ) — Track Day Mode B (Le Mans Bugatti)

Source design : carnet_track_day_gumball_modes.html (Mode B)
Scope         : Mode plein écran "track day actif" pendant une session
                circuit : header session + chronos hero (meilleur tour /
                tour précédent splits S1/S2/S3) + coaching contextuel
                (instructeur) + tableau pilotes CARNET du jour + voiture
                status entre sessions + actions bottom (Photos / Instructeur
                / Sortie pit).
                Activable via window.CARNET_TRACKDAY_DEMO.open() console.
Hors scope    : Chronométrage live via timing transponder → Phase ε
                Wiring depuis Affût quand session piste détectée → Phase γ.b
                Chat instructeur temps réel → Phase ζ

Applique 2 patches sur index.html :
  1. CSS additions   → styles overlay trackday + composants
  2. JS helpers      → renderTrackdayOverlay() + CARNET_TRACKDAY_DEMO

Pas de render hook dans Garage : mode séparé, suivant le pattern du Lot 5.

Prérequis : Lot 5 (Phase β) appliqué
Usage     :
    python3 apply_track_day_lot6.py path/to/index.html
    python3 apply_track_day_lot6.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions
# Anchor 2 bornes : fin du Lot 5 CSS + </style>
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """.copilote-action-icon{
  font-size:18px;
  margin-bottom:2px;
  display:block;
}

</style>"""

PATCH_1_REPLACEMENT = """.copilote-action-icon{
  font-size:18px;
  margin-bottom:2px;
  display:block;
}

/* ═══ LOT 6 (Phase γ) — Track Day Mode B (Le Mans Bugatti) ═════════════ */

/* Mode overlay plein écran — pattern identique au Lot 5 */
.trackday-overlay{
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
.trackday-overlay[hidden]{ display:none; }

.trackday-close{
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
.trackday-close:hover{ background:rgba(244,241,234,0.3); }

/* Header — encre noir, eyebrow + titre + pit lane + live */
.trackday-header{
  padding:14px 18px;
  background:var(--encre);
  color:var(--papier);
  display:flex;
  justify-content:space-between;
  align-items:center;
  position:relative;
}
.trackday-header-left{ flex:1; }
.trackday-header-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0;
}
.trackday-header-title{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  margin:2px 0 0 0;
  line-height:1.1;
  color:var(--papier);
}
.trackday-header-right{
  text-align:right;
  font-family:var(--mono);
  font-size:11px;
  color:#D5D0C4;
  padding-right:40px;
}
.trackday-header-right .is-positive{ color:#9FE1CB; }
.trackday-header-live{
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
  margin-top:2px;
}

/* Chronos hero — 2 cols grid (meilleur tour + tour précédent) */
.trackday-chronos{ padding:24px 24px 14px; }
.trackday-chronos-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:14px;
}
.trackday-chronos-col-r{ text-align:right; }
.trackday-chronos-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.16em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 4px 0;
}
.trackday-chronos-time{
  font-family:var(--display);
  font-style:italic;
  font-size:34px;
  letter-spacing:-0.02em;
  line-height:1;
  color:var(--encre);
  margin:0;
}
.trackday-chronos-time.is-prev{ color:#6B655B; }
.trackday-chronos-delta{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.04em;
  margin-top:3px;
}
.trackday-chronos-delta.is-positive{ color:var(--vert-anglais); }
.trackday-chronos-delta.is-mixed{ color:var(--or); }

/* Coaching contextuel — fond orange polo très léger + border-left */
.trackday-coaching{
  margin:0 18px 14px;
  padding:14px 16px;
  background:rgba(232,90,31,0.05);
  border-left:3px solid var(--orange-polo);
  border-radius:var(--r);
}
.trackday-coaching-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:var(--orange-polo);
  text-transform:uppercase;
  margin:0 0 6px 0;
}
.trackday-coaching-text{
  font-family:var(--editorial);
  font-style:italic;
  font-size:14px;
  line-height:1.45;
  margin:0;
  color:var(--encre);
}

/* Tableau pilotes CARNET du jour */
.trackday-pilots{ padding:0 22px 14px; }
.trackday-pilots-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.16em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 10px 0;
}
.trackday-pilots-list{
  font-family:var(--mono);
  font-size:11px;
  color:var(--encre-soft);
}
.trackday-pilot-row{
  display:flex;
  justify-content:space-between;
  padding:7px 0;
  border-bottom:1px solid var(--gris-line);
}
.trackday-pilot-row.is-last{ border-bottom:none; }
.trackday-pilot-row.is-self{
  background:#FAFAF7;
  margin:0 -22px;
  padding-left:22px;
  padding-right:22px;
}
.trackday-pilot-row.is-trailing{ color:#6B655B; }
.trackday-pilot-rank{ color:var(--gris); }
.trackday-pilot-row.is-self .trackday-pilot-rank{
  color:var(--orange-polo);
  font-weight:500;
}
.trackday-pilot-name strong{ font-weight:500; }
.trackday-pilot-time.is-leader{ color:var(--vert-anglais); }
.trackday-pilot-time.is-self{ color:var(--orange-polo); font-weight:500; }

/* Voiture status entre sessions — border-left vert anglais */
.trackday-car{ padding:0 22px 16px; }
.trackday-car-card{
  display:flex;
  align-items:center;
  gap:10px;
  padding:10px 12px;
  background:#FAFAF7;
  border-left:3px solid var(--vert-anglais);
  border-radius:var(--r);
}
.trackday-car-text{
  font-family:var(--mono);
  font-size:11px;
  flex:1;
  color:var(--encre);
}
.trackday-car-detail{
  font-family:var(--mono);
  font-size:9px;
  color:var(--orange-polo);
  letter-spacing:0.08em;
  text-transform:uppercase;
  cursor:pointer;
  border:none;
  background:none;
  padding:0;
}

/* Actions bottom — 3 boutons grid (pattern Lot 5) */
.trackday-actions{
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:1px;
  background:#D5D0C4;
  border-top:1px solid #D5D0C4;
}
.trackday-action{
  padding:13px 0;
  background:var(--papier);
  border:none;
  cursor:pointer;
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--encre);
}
.trackday-action.is-alert{ color:var(--orange-polo); }
.trackday-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers + demo opener
# Anchor 2 bornes : marker fin /Lot 5 + début renderGaragePage
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """// ─── /Lot 5 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """// ─── /Lot 5 helpers ──────────────────────────────────────────────────

// ─── Lot 6 (Phase γ) — helpers Track Day Mode B ──────────────────────
//
// Phase γ = mode plein écran activable via console pour démo :
//           > window.CARNET_TRACKDAY_DEMO.open()
//           > window.CARNET_TRACKDAY_DEMO.close()
//
// Phase γ.b ajoutera : détection session piste depuis Affût + trigger
//                      auto.
// Phase ε ajoutera : sync chronos live via transponder timing system
//                    (MyLaps, AMB) + WebSocket backend rallye.
// Phase ζ ajoutera : chat instructeur temps réel + comparaison datalog
//                    télémétrie.

window.CARNET_TRACKDAY_MOCK = window.CARNET_TRACKDAY_MOCK || {
  session: {
    circuit: 'Le Mans \\u00b7 Bugatti',
    label: 'session 3/5',
    title: 'Piste ouverte \\u00b7 28 min',
    pit_lane_count: 12,
    live: true,
    on_track: true
  },
  chronos: {
    best: {
      time_label: '1:42.347',
      lap_number: 7,
      delta_label: '\\u20130,3s vs perso',
      delta_class: 'is-positive'
    },
    previous: {
      time_label: '1:43.712',
      delta_label: 'S2 \\u20130,4s \\u00b7 S3 +0,2s',
      delta_class: 'is-mixed'
    }
  },
  coaching: {
    instructor: 'Romain D.',
    text: 'Au virage 3 (Esses du Tertre Rouge) tu perds 0,4s vs Marc. Freine 10 m plus tard, garde le pied droit jusqu\\u2019\\u00e0 la corde.'
  },
  pilots: [
    { rank: 1, name: 'Marc D.',    car: '911 GT3', time: '1:40.218', class: 'is-leader' },
    { rank: 2, name: 'Antoine L.', car: '968 CS',  time: '1:41.852', class: '' },
    { rank: 3, name: 'Toi',        car: 'E30 M3',  time: '1:42.347', class: 'is-self', isSelf: true },
    { rank: 4, name: 'Julien R.',  car: 'M3 CSL',  time: '1:43.104', class: '', isTrailing: true }
  ],
  car_between_sessions: {
    text: 'M3 OK \\u00b7 pneus AR 38\\u00b0 \\u00b7 pression \\u00e0 v\\u00e9rifier',
    detail_label: 'd\\u00e9tails \\u2192'
  }
};

function renderTrackdayChronosCol(c, isRight){
  if (!c) return '';
  const colCls = isRight ? 'trackday-chronos-col-r' : '';
  const timeCls = isRight ? 'trackday-chronos-time is-prev' : 'trackday-chronos-time';
  const deltaCls = c.delta_class ? `trackday-chronos-delta ${c.delta_class}` : 'trackday-chronos-delta';
  const sub = isRight
    ? esc(c.delta_label || '')
    : (c.lap_number ? `tour ${c.lap_number} \\u00b7 ${esc(c.delta_label || '')}` : esc(c.delta_label || ''));
  const label = isRight ? 'Tour pr\\u00e9c\\u00e9dent' : 'Meilleur tour \\u00b7 J';
  return `
    <div class="${colCls}">
      <p class="trackday-chronos-label">${label}</p>
      <p class="${timeCls}">${esc(c.time_label || '\\u2014')}</p>
      <p class="${deltaCls}">${sub}</p>
    </div>`;
}

function renderTrackdayPilotRow(p, isLast){
  let rowCls = 'trackday-pilot-row';
  if (p.isSelf) rowCls += ' is-self';
  if (p.isTrailing) rowCls += ' is-trailing';
  if (isLast) rowCls += ' is-last';
  const rankHtml = `<span class="trackday-pilot-rank">${String(p.rank).padStart(2,'0')}.</span>`;
  const nameHtml = p.isSelf
    ? `<strong>${esc(p.name)} \\u00b7 ${esc(p.car)}</strong>`
    : `${esc(p.name)} \\u00b7 ${esc(p.car)}`;
  let timeCls = 'trackday-pilot-time';
  if (p.class && p.class.indexOf('is-leader') >= 0) timeCls += ' is-leader';
  if (p.isSelf) timeCls += ' is-self';
  return `
    <div class="${rowCls}">
      <span class="trackday-pilot-name">${rankHtml} ${nameHtml}</span>
      <span class="${timeCls}">${esc(p.time)}</span>
    </div>`;
}

function renderTrackdayOverlay(){
  const data = window.CARNET_TRACKDAY_MOCK;
  if (!data) return '';

  const s = data.session || {};
  const ch = data.chronos || {};
  const co = data.coaching || {};
  const car = data.car_between_sessions || {};
  const pilots = data.pilots || [];

  const pilotsHtml = pilots.map((p, i) => renderTrackdayPilotRow(p, i === pilots.length - 1)).join('');

  return `
    <button type="button" class="trackday-close" data-action="closeTrackday" aria-label="Fermer">\\u00d7</button>

    <div class="trackday-header">
      <div class="trackday-header-left">
        <p class="trackday-header-eyebrow">${esc(s.circuit || '')} \\u00b7 ${esc(s.label || '')}</p>
        <p class="trackday-header-title">${esc(s.title || '')}</p>
      </div>
      <div class="trackday-header-right">
        <div>Pit lane <span class="is-positive">${s.pit_lane_count || 0}</span></div>
        ${s.live && s.on_track ? '<div class="trackday-header-live">\\u25cf en piste</div>' : ''}
      </div>
    </div>

    <div class="trackday-chronos">
      <div class="trackday-chronos-grid">
        ${renderTrackdayChronosCol(ch.best, false)}
        ${renderTrackdayChronosCol(ch.previous, true)}
      </div>
    </div>

    <div class="trackday-coaching">
      <p class="trackday-coaching-eyebrow">Conseil \\u00b7 ${esc(co.instructor || '')} (instructeur)</p>
      <p class="trackday-coaching-text">${esc(co.text || '')}</p>
    </div>

    <div class="trackday-pilots">
      <p class="trackday-pilots-label">Tableau \\u00b7 pilotes CARNET du jour</p>
      <div class="trackday-pilots-list">${pilotsHtml}</div>
    </div>

    <div class="trackday-car">
      <div class="trackday-car-card">
        <span class="trackday-car-text">${esc(car.text || '')}</span>
        <button type="button" class="trackday-car-detail" data-action="openTrackdayCarDetail">${esc(car.detail_label || '')}</button>
      </div>
    </div>

    <div class="trackday-actions">
      <button type="button" class="trackday-action" data-action="trackdayPhotos">
        <span class="trackday-action-icon">\\ud83d\\udcf8</span>
        Photos
      </button>
      <button type="button" class="trackday-action" data-action="trackdayInstructor">
        <span class="trackday-action-icon">\\u229c</span>
        Instructeur
      </button>
      <button type="button" class="trackday-action is-alert" data-action="trackdayPitOut">
        <span class="trackday-action-icon">\\u26a0</span>
        Sortie pit
      </button>
    </div>
  `;
}

// API démo accessible via console
window.CARNET_TRACKDAY_DEMO = {
  open: function(){
    let overlay = document.getElementById('carnet-trackday-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'carnet-trackday-overlay';
      overlay.className = 'trackday-overlay';
      document.body.appendChild(overlay);
      overlay.addEventListener('click', function(e){
        const btn = e.target.closest('[data-action="closeTrackday"]');
        if (btn) window.CARNET_TRACKDAY_DEMO.close();
      });
    }
    overlay.innerHTML = renderTrackdayOverlay();
    overlay.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  },
  close: function(){
    const overlay = document.getElementById('carnet-trackday-overlay');
    if (overlay) overlay.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
};
// ─── /Lot 6 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 6 (Phase γ) — Track Day Mode B (Le Mans Bugatti)",
    requires=[
        "LOT 5 (Phase β) — Co-pilote Actif",
    ],
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 6 (Phase γ) — Track Day Mode B",
        ),
        Patch(
            name="JS helpers + demo opener",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 6 (Phase γ) — helpers Track Day Mode B",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
