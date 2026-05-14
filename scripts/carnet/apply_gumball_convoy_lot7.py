#!/usr/bin/env python3
"""
CARNET · Lot 7 (Phase γ) — Gumball Convoy Mode C

Source design : carnet_track_day_gumball_modes.html (Mode C)
Scope         : Mode plein écran "convoy live" pour rally fun (Gumball
                3000, Goldrush Rally, équivalent) : header convoy +
                programme jour timeline (étapes completed/current/future)
                + reel stories horizontal + actions bottom (Story / Convoy
                / Pot).
                Activable via window.CARNET_GUMBALL_DEMO.open() console.
Hors scope    : Sync reel temps réel via backend rally → Phase ε
                Pot commun XRPL escrow → Phase ε (relié au Lot 4 Ledger)
                Geofencing étapes auto-completed → Phase ε

Applique 2 patches sur index.html :
  1. CSS additions   → styles overlay gumball + timeline + reel
  2. JS helpers      → renderGumballOverlay() + CARNET_GUMBALL_DEMO

Pas de render hook dans Garage : mode séparé, pattern Lot 5/6.

Prérequis : Lot 6 (Phase γ) appliqué
Usage     :
    python3 apply_gumball_convoy_lot7.py path/to/index.html
    python3 apply_gumball_convoy_lot7.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions
# Anchor 2 bornes : fin du Lot 6 CSS + </style>
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """.trackday-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

</style>"""

PATCH_1_REPLACEMENT = """.trackday-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

/* ═══ LOT 7 (Phase γ) — Gumball Convoy Mode C ══════════════════════════ */

/* Mode overlay plein écran — pattern identique Lot 5/6 */
.gumball-overlay{
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
.gumball-overlay[hidden]{ display:none; }

.gumball-close{
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
.gumball-close:hover{ background:rgba(244,241,234,0.3); }

/* Header — encre noir avec convoy counter */
.gumball-header{
  padding:14px 18px;
  background:var(--encre);
  color:var(--papier);
  display:flex;
  justify-content:space-between;
  align-items:center;
  position:relative;
}
.gumball-header-left{ flex:1; }
.gumball-header-eyebrow{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0;
}
.gumball-header-title{
  font-family:var(--display);
  font-style:italic;
  font-size:16px;
  margin:2px 0 0 0;
  line-height:1.1;
  color:var(--papier);
}
.gumball-header-right{
  text-align:right;
  font-family:var(--mono);
  font-size:11px;
  color:#D5D0C4;
  padding-right:40px;
}
.gumball-header-live{
  font-size:9px;
  color:#9FE1CB;
  letter-spacing:0.04em;
  margin-top:2px;
}

/* Programme du jour — timeline avec dots + lignes connectrices */
.gumball-program{ padding:24px 22px 8px; }
.gumball-program-label{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 14px 0;
}
.gumball-timeline{
  display:flex;
  flex-direction:column;
  gap:0;
}
.gumball-step{
  display:flex;
  gap:14px;
  padding-bottom:14px;
}
.gumball-step:last-child{ padding-bottom:0; }
.gumball-step-rail{
  display:flex;
  flex-direction:column;
  align-items:center;
  width:34px;
  flex-shrink:0;
}
.gumball-step-dot{
  width:10px;
  height:10px;
  border-radius:50%;
}
.gumball-step-dot.is-done{ background:var(--vert-anglais); }
.gumball-step-dot.is-current{ background:var(--orange-polo); }
.gumball-step-dot.is-future{
  background:transparent;
  border:1.5px solid #D5D0C4;
}
.gumball-step-line{
  width:1px;
  flex:1;
  background:#D5D0C4;
  margin-top:4px;
}
.gumball-step:last-child .gumball-step-line{ display:none; }

.gumball-step-body{ flex:1; min-width:0; }
.gumball-step-time{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.12em;
  text-transform:uppercase;
  margin:0;
}
.gumball-step-time.is-done{ color:var(--vert-anglais); }
.gumball-step-time.is-current{ color:var(--orange-polo); }
.gumball-step-time.is-future{ color:var(--gris); }

.gumball-step-text{
  font-family:var(--editorial);
  font-style:italic;
  font-size:15px;
  color:var(--encre);
  line-height:1.3;
  margin:2px 0 0 0;
}
.gumball-step-meta{
  font-family:var(--mono);
  font-size:9px;
  color:#6B655B;
  letter-spacing:0.04em;
  margin:3px 0 0 0;
}

/* RSVP chips dans step */
.gumball-step-rsvp{
  display:flex;
  gap:6px;
  margin-top:6px;
}
.gumball-rsvp-chip{
  font-family:var(--mono);
  font-size:9px;
  padding:3px 8px;
  border-radius:var(--r);
  letter-spacing:0.04em;
  text-transform:uppercase;
  border:1px solid #D5D0C4;
  background:transparent;
  cursor:pointer;
  color:var(--gris);
}
.gumball-rsvp-chip.is-selected{
  color:var(--encre);
  background:#FAFAF7;
  border-color:#D5D0C4;
}

/* Reel du convoy — horizontal scroll de stories */
.gumball-reel{ padding:14px 22px 4px; }
.gumball-reel-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.16em;
  color:var(--gris);
  text-transform:uppercase;
  margin:0 0 10px 0;
}
.gumball-reel-track{
  display:flex;
  gap:8px;
  overflow-x:auto;
  padding-bottom:6px;
  -webkit-overflow-scrolling:touch;
}
.gumball-story{
  flex:0 0 130px;
  aspect-ratio:0.7;
  background:var(--encre);
  border-radius:var(--r);
  position:relative;
  overflow:hidden;
  cursor:pointer;
}
.gumball-story-body{
  position:absolute;
  bottom:8px;
  left:8px;
  right:8px;
  color:var(--papier);
}
.gumball-story-author{
  font-family:var(--mono);
  font-size:9px;
  color:var(--orange-polo);
  letter-spacing:0.04em;
  text-transform:uppercase;
}
.gumball-story-caption{
  font-family:var(--editorial);
  font-style:italic;
  font-size:11px;
  line-height:1.2;
  margin:2px 0 0 0;
  color:var(--papier);
}
.gumball-story-duration{
  position:absolute;
  top:8px;
  right:8px;
  font-family:var(--mono);
  font-size:9px;
  color:var(--papier);
  background:rgba(232,90,31,0.85);
  padding:2px 6px;
  border-radius:var(--r);
}
.gumball-story.is-add{
  background:rgba(26,26,24,0.06);
  border:1px dashed #D5D0C4;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  color:var(--gris);
}
.gumball-story-add-icon{
  font-size:24px;
  line-height:1;
}
.gumball-story-add-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.08em;
  margin-top:6px;
  text-transform:uppercase;
}

/* Actions bottom — 3 boutons grid (pattern Lot 5/6) */
.gumball-actions{
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:1px;
  background:#D5D0C4;
  border-top:1px solid #D5D0C4;
  margin-top:14px;
}
.gumball-action{
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
.gumball-action-icon{
  font-size:16px;
  margin-bottom:2px;
  display:block;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers + demo opener
# Anchor 2 bornes : marker fin /Lot 6 + début renderGaragePage
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """// ─── /Lot 6 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """// ─── /Lot 6 helpers ──────────────────────────────────────────────────

// ─── Lot 7 (Phase γ) — helpers Gumball Convoy Mode C ─────────────────
//
// Phase γ = mode plein écran activable via console pour démo :
//           > window.CARNET_GUMBALL_DEMO.open()
//           > window.CARNET_GUMBALL_DEMO.close()
//
// Phase ε branchera : sync reel temps réel via backend rally, geofencing
//                     étapes auto-completed, pot commun XRPL escrow
//                     (relié au Lot 4 Ledger Events).

window.CARNET_GUMBALL_MOCK = window.CARNET_GUMBALL_MOCK || {
  event: {
    series: 'Gumball 3000',
    day: 'J3 / 7',
    leg: 'Berlin \\u2192 Prague \\u00b7 387 km',
    convoy_position: '142 / 200',
    convoy_live: true
  },
  steps: [
    {
      time_label: '8h00 \\u00b7 d\\u00e9part \\u2713',
      state: 'done',
      text: 'Brandenburger Tor, parade urbaine.',
      meta: ''
    },
    {
      time_label: '12h30 \\u00b7 maintenant',
      state: 'current',
      text: 'Brunch au Schloss Wackerbarth \\u00b7 47 RSVP.',
      meta: '22 km \\u00b7 18 min \\u00b7 A4 sortie 79'
    },
    {
      time_label: '17h00',
      state: 'future',
      text: 'Arriv\\u00e9e Prague \\u00b7 Hotel Augustine.',
      meta: ''
    },
    {
      time_label: '22h00 \\u00b7 soir\\u00e9e',
      state: 'future',
      text: 'U Fleku \\u00b7 open bar Brabus \\u00b7 67 RSVP.',
      meta: '',
      rsvp: [
        { label: 'Je viens', selected: true,  action: 'gumballRsvpYes'   },
        { label: 'Plus tard', selected: false, action: 'gumballRsvpLater' }
      ]
    }
  ],
  reel: [
    {
      author: 'JULIEN R.',
      caption: 'Parade Brandebourg.',
      duration_label: '12s'
    },
    {
      author: 'MARC D.',
      caption: 'Tunnel rugissement.',
      duration_label: '8s'
    },
    {
      is_add: true,
      add_label: 'Story'
    }
  ]
};

function renderGumballStepRail(state){
  // state : 'done' | 'current' | 'future'
  const dotCls = state === 'done' ? 'gumball-step-dot is-done'
              : state === 'current' ? 'gumball-step-dot is-current'
              : 'gumball-step-dot is-future';
  return `
    <div class="gumball-step-rail">
      <div class="${dotCls}"></div>
      <div class="gumball-step-line"></div>
    </div>`;
}

function renderGumballRsvpChip(chip){
  const cls = chip.selected ? 'gumball-rsvp-chip is-selected' : 'gumball-rsvp-chip';
  const action = chip.action || 'gumballRsvp';
  return `<button type="button" class="${cls}" data-action="${esc(action)}">${esc(chip.label)}</button>`;
}

function renderGumballStep(step){
  const timeCls = step.state === 'done' ? 'gumball-step-time is-done'
                : step.state === 'current' ? 'gumball-step-time is-current'
                : 'gumball-step-time is-future';
  const metaHtml = step.meta ? `<p class="gumball-step-meta">${esc(step.meta)}</p>` : '';
  const rsvpHtml = (step.rsvp && step.rsvp.length > 0)
    ? `<div class="gumball-step-rsvp">${step.rsvp.map(renderGumballRsvpChip).join('')}</div>`
    : '';
  return `
    <div class="gumball-step">
      ${renderGumballStepRail(step.state)}
      <div class="gumball-step-body">
        <p class="${timeCls}">${esc(step.time_label || '')}</p>
        <p class="gumball-step-text">${esc(step.text || '')}</p>
        ${metaHtml}
        ${rsvpHtml}
      </div>
    </div>`;
}

function renderGumballStory(story){
  if (story.is_add) {
    return `
      <button type="button" class="gumball-story is-add" data-action="gumballAddStory">
        <span class="gumball-story-add-icon">+</span>
        <span class="gumball-story-add-label">${esc(story.add_label || 'Story')}</span>
      </button>`;
  }
  return `
    <div class="gumball-story" data-action="openGumballStory">
      <div class="gumball-story-body">
        <div class="gumball-story-author">${esc(story.author || '')}</div>
        <p class="gumball-story-caption">${esc(story.caption || '')}</p>
      </div>
      ${story.duration_label ? `<div class="gumball-story-duration">${esc(story.duration_label)}</div>` : ''}
    </div>`;
}

function renderGumballOverlay(){
  const data = window.CARNET_GUMBALL_MOCK;
  if (!data) return '';

  const ev = data.event || {};
  const steps = data.steps || [];
  const reel = data.reel || [];

  const stepsHtml = steps.map(renderGumballStep).join('');
  const reelHtml = reel.map(renderGumballStory).join('');

  return `
    <button type="button" class="gumball-close" data-action="closeGumball" aria-label="Fermer">\\u00d7</button>

    <div class="gumball-header">
      <div class="gumball-header-left">
        <p class="gumball-header-eyebrow">${esc(ev.series || '')} \\u00b7 ${esc(ev.day || '')}</p>
        <p class="gumball-header-title">${esc(ev.leg || '')}</p>
      </div>
      <div class="gumball-header-right">
        <div>${esc(ev.convoy_position || '')}</div>
        ${ev.convoy_live ? '<div class="gumball-header-live">\\u25cf convoy live</div>' : ''}
      </div>
    </div>

    <div class="gumball-program">
      <p class="gumball-program-label">Programme du jour</p>
      <div class="gumball-timeline">${stepsHtml}</div>
    </div>

    <div class="gumball-reel">
      <p class="gumball-reel-label">Reel du convoy \\u00b7 live</p>
      <div class="gumball-reel-track">${reelHtml}</div>
    </div>

    <div class="gumball-actions">
      <button type="button" class="gumball-action" data-action="gumballStory">
        <span class="gumball-action-icon">\\u25b6</span>
        Story
      </button>
      <button type="button" class="gumball-action" data-action="gumballConvoy">
        <span class="gumball-action-icon">\\u2302</span>
        Convoy
      </button>
      <button type="button" class="gumball-action" data-action="gumballPot">
        <span class="gumball-action-icon">\\u20ac</span>
        Pot
      </button>
    </div>
  `;
}

// API démo accessible via console
window.CARNET_GUMBALL_DEMO = {
  open: function(){
    let overlay = document.getElementById('carnet-gumball-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'carnet-gumball-overlay';
      overlay.className = 'gumball-overlay';
      document.body.appendChild(overlay);
      overlay.addEventListener('click', function(e){
        const btn = e.target.closest('[data-action="closeGumball"]');
        if (btn) window.CARNET_GUMBALL_DEMO.close();
      });
    }
    overlay.innerHTML = renderGumballOverlay();
    overlay.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  },
  close: function(){
    const overlay = document.getElementById('carnet-gumball-overlay');
    if (overlay) overlay.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
};
// ─── /Lot 7 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 7 (Phase γ) — Gumball Convoy Mode C",
    requires=[
        "LOT 6 (Phase γ) — Track Day Mode B",
    ],
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 7 (Phase γ) — Gumball Convoy Mode C",
        ),
        Patch(
            name="JS helpers + demo opener",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 7 (Phase γ) — helpers Gumball Convoy",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
