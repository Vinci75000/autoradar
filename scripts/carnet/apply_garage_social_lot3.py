#!/usr/bin/env python3
"""
CARNET · Lot 3 (Phase β) — Garage Social Co-ownership (lecture seule)

Source design : carnet_garage_social_coownership.html
Scope         : Mockup 1 (section "Avec qui · cercles") + bloc co-ownership
                multisig XLS-20. Données mockées pour Year -1.
Hors scope    : Mockup 3 (sheet "Inviter un proche") — Phase δ ultérieure
                avec backend Supabase + invitations multi-cercles + permissions.

Applique 3 patches sur index.html :
  1. CSS additions   → styles section cercles + avatars stack + co-owned block
  2. JS helper       → renderGarageCirclesSection() avec data mock
  3. Render hook     → insertion dans renderGaragePage après ${archivesSection}

Prérequis : Lot 2 (Phase α) appliqué
Usage     :
    python3 apply_garage_social_lot3.py path/to/index.html
    python3 apply_garage_social_lot3.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS additions (avant </style>, après le Lot 2 CSS block)
# ═══════════════════════════════════════════════════════════════════════

PATCH_1_ANCHOR = """  background:none;
  border-left:none;
  border-right:none;
  border-top:none;
}

</style>"""

PATCH_1_REPLACEMENT = """  background:none;
  border-left:none;
  border-right:none;
  border-top:none;
}

/* ═══ LOT 3 (Phase β) — Garage Social Co-ownership ═════════════════════ */

/* Section "Avec qui · cercles" */
.garage-circles{ margin:34px 0 18px; }
.garage-circles-header{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:18px;
}
.garage-circles-title{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:0.2em;
  color:var(--gris);
  text-transform:uppercase;
}
.garage-circles-invite{
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
.garage-circles-invite:hover{ text-decoration:underline; text-decoration-color:var(--orange-polo); text-underline-offset:3px; }

.garage-circles-list{
  display:flex;
  flex-direction:column;
  gap:8px;
  margin-bottom:24px;
}

.garage-circle-row{
  display:flex;
  align-items:center;
  gap:12px;
  padding:12px 14px;
  background:#FAFAF7;
  border:1px solid var(--gris-line);
  border-radius:var(--r);
  cursor:pointer;
  transition:border-color 200ms ease;
  font:inherit;
  color:inherit;
  width:100%;
  text-align:left;
}
.garage-circle-row:hover{ border-color:var(--encre); }
.garage-circle-row:focus-visible{ outline:2px solid var(--orange-polo); outline-offset:2px; }

.garage-circle-avatars{ display:flex; flex-shrink:0; }
.garage-circle-avatar{
  width:26px;
  height:26px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--mono);
  font-size:10px;
  color:var(--papier);
  border:2px solid #FAFAF7;
}
.garage-circle-avatar + .garage-circle-avatar{ margin-left:-8px; }
.garage-circle-avatar.is-empty{
  background:var(--papier);
  border:1px dashed var(--gris-line);
  color:var(--gris);
  font-family:var(--display);
  font-style:italic;
  font-size:13px;
}
.garage-circle-avatar.is-more{
  background:var(--gris);
  color:var(--papier);
  font-size:9px;
}

.garage-circle-content{ flex:1; min-width:0; }
.garage-circle-name{
  font-family:var(--editorial);
  font-style:italic;
  font-weight:500;
  font-size:15px;
  color:var(--encre);
  line-height:1.2;
}
.garage-circle-meta{
  font-family:var(--mono);
  font-size:9px;
  color:var(--gris);
  letter-spacing:0.04em;
  margin-top:2px;
  text-transform:lowercase;
}
.garage-circle-arrow{
  font-family:var(--mono);
  font-size:14px;
  color:var(--gris);
  flex-shrink:0;
}

/* Bloc co-ownership multi-sig XLS-20 — fond sombre, accent vert anglais */
.garage-coowned{
  padding:18px 20px;
  background:var(--encre);
  color:var(--papier);
  border-radius:var(--r);
}
.garage-coowned-label{
  font-family:var(--mono);
  font-size:9px;
  letter-spacing:0.18em;
  color:#9FE1CB;
  text-transform:uppercase;
  margin:0 0 8px 0;
}
.garage-coowned-share{
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:10px;
}
.garage-coowned-share-text{
  flex:1;
  font-family:var(--mono);
  font-size:10px;
  color:#9FE1CB;
  letter-spacing:0.04em;
}
.garage-coowned-share .garage-circle-avatar{ border-color:var(--encre); }
.garage-coowned-desc{
  font-family:var(--editorial);
  font-style:italic;
  font-size:16px;
  line-height:1.4;
  margin:0 0 10px 0;
  color:var(--papier);
}
.garage-coowned-desc em{ font-style:italic; }
.garage-coowned-chips{ display:flex; gap:6px; flex-wrap:wrap; }
.garage-coowned-chip{
  font-family:var(--mono);
  font-size:9px;
  color:#9FE1CB;
  padding:4px 8px;
  background:rgba(159,225,203,0.1);
  border-radius:var(--r);
  letter-spacing:0.04em;
  text-transform:uppercase;
}

</style>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS helpers (avant function renderGaragePage)
# ═══════════════════════════════════════════════════════════════════════

PATCH_2_ANCHOR = """  </div>`;
}

function renderGaragePage(){"""

PATCH_2_REPLACEMENT = """  </div>`;
}

// ─── Lot 3 (Phase β) — helpers Garage Social Co-ownership ─────────────
//
// Phase β = vue lecture seule + données mockées Year -1.
// Phase δ ajoutera : backend Supabase, sheet d'invitation, permissions
// granulaires (Voir/Éditer/Co-posséder), notifications cross-cercle.
//
// Source de vérité provisoire : window.CARNET_CIRCLES_MOCK (modifiable
// via console pour démo). Sera remplacée par appel API.

window.CARNET_CIRCLES_MOCK = window.CARNET_CIRCLES_MOCK || {
  circles: [
    {
      id: 'family',
      name: 'Famille',
      members: [
        { initial: 'P', color: '#1A1A18' },
        { initial: 'L', color: '#1F4D2F' },
        { initial: 'M', color: '#BA7517' }
      ],
      memberCount: 3,
      shareDescription: '4 voitures partag\\u00e9es',
      accessLevel: '\\u00e9dition'
    },
    {
      id: 'close_friends',
      name: 'Amis proches',
      members: [
        { initial: 'J', color: '#E85A1F' },
        { initial: 'T', color: '#1A1A18' },
        { initial: 'R', color: '#1F4D2F' },
        { initial: '+3', color: '#6B655B', isMore: true }
      ],
      memberCount: 6,
      shareDescription: '47 souvenirs partag\\u00e9s',
      accessLevel: 'lecture'
    },
    {
      id: 'aircooled_club',
      name: 'Club Aircooled',
      members: [
        { isEmpty: true }
      ],
      memberCount: 12,
      shareDescription: '1 voiture visible',
      accessLevel: 'commentaires'
    }
  ],
  coowned: {
    enabled: true,
    label: 'Co-owned · multi-sig XLS-20',
    members: [
      { initial: 'S', color: '#E85A1F' },
      { initial: 'P', color: '#1F4D2F' }
    ],
    shareText: '50 / 50 · ton p\\u00e8re et toi',
    description: '<em>Ferrari F355 GTS \\u00b7 1998.</em> Co-acquise mars 2024. Cession n\\u00e9cessite double signature.',
    chips: ['NFT #0856', '2 carnets co-sign\\u00e9s']
  }
};

function renderGarageCircleAvatar(member){
  if (member.isEmpty) {
    return '<div class="garage-circle-avatar is-empty">\\u2a00</div>';
  }
  const cls = member.isMore ? 'garage-circle-avatar is-more' : 'garage-circle-avatar';
  return `<div class="${cls}" style="background:${esc(member.color || '#1A1A18')}">${esc(member.initial)}</div>`;
}

function renderGarageCircleRow(circle){
  const avatars = (circle.members || []).map(renderGarageCircleAvatar).join('');
  const meta = `${circle.memberCount} membre${circle.memberCount > 1 ? 's' : ''} \\u00b7 ${esc(circle.shareDescription)} \\u00b7 ${esc(circle.accessLevel)}`;
  return `
    <button type="button" class="garage-circle-row" data-action="openCircle" data-circle-id="${esc(circle.id)}">
      <div class="garage-circle-avatars">${avatars}</div>
      <div class="garage-circle-content">
        <div class="garage-circle-name"><em>${esc(circle.name)}</em></div>
        <div class="garage-circle-meta">${meta}</div>
      </div>
      <span class="garage-circle-arrow">\\u2192</span>
    </button>`;
}

function renderGarageCoownedBlock(co){
  if (!co || !co.enabled) return '';
  const avatars = (co.members || []).map(renderGarageCircleAvatar).join('');
  const chips = (co.chips || []).map(c => `<span class="garage-coowned-chip">${esc(c)}</span>`).join('');
  // co.description peut contenir <em>...</em> (HTML autorisé pour mise en valeur du modèle)
  return `
    <div class="garage-coowned">
      <p class="garage-coowned-label">${esc(co.label || 'CO-OWNED')}</p>
      <div class="garage-coowned-share">
        <div class="garage-circle-avatars">${avatars}</div>
        <div class="garage-coowned-share-text">${esc(co.shareText || '')}</div>
      </div>
      <p class="garage-coowned-desc">${co.description || ''}</p>
      <div class="garage-coowned-chips">${chips}</div>
    </div>`;
}

function renderGarageCirclesSection(){
  // Lot 3 (Phase β) — vue lecture seule, mock data.
  // Phase δ remplacera CARNET_CIRCLES_MOCK par fetch Supabase circles + memberships.
  const data = window.CARNET_CIRCLES_MOCK;
  if (!data || !data.circles || data.circles.length === 0) {
    return ''; // Pas de section si aucun cercle.
  }
  const circlesHtml = data.circles.map(renderGarageCircleRow).join('');
  const coownedHtml = renderGarageCoownedBlock(data.coowned);
  return `
    <div class="garage-circles">
      <div class="garage-circles-header">
        <span class="garage-circles-title">AVEC QUI \\u00b7 CERCLES</span>
        <button type="button" class="garage-circles-invite" data-action="openInviteCircle">+ INVITER</button>
      </div>
      <div class="garage-circles-list">${circlesHtml}</div>
      ${coownedHtml}
    </div>`;
}
// ─── /Lot 3 helpers ──────────────────────────────────────────────────

function renderGaragePage(){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — Render hook (insertion dans renderGaragePage après archivesSection)
# ═══════════════════════════════════════════════════════════════════════

PATCH_3_ANCHOR = """      ${archivesSection}
    `;
  }"""

PATCH_3_REPLACEMENT = """      ${archivesSection}
      ${renderGarageCirclesSection()}
    `;
  }"""


# ═══════════════════════════════════════════════════════════════════════
# PATCHSET
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 3 (Phase β) — Garage Social Co-ownership",
    requires=[
        "LOT 2 (Phase α) — Garage refonte mid-top",  # marker du Lot 2
    ],
    patches=[
        Patch(
            name="CSS additions",
            anchor=PATCH_1_ANCHOR,
            replacement=PATCH_1_REPLACEMENT,
            idempotence_marker="LOT 3 (Phase β) — Garage Social Co-ownership",
        ),
        Patch(
            name="JS helpers",
            anchor=PATCH_2_ANCHOR,
            replacement=PATCH_2_REPLACEMENT,
            idempotence_marker="// ─── Lot 3 (Phase β) — helpers Garage Social Co-ownership",
        ),
        Patch(
            name="Render hook",
            anchor=PATCH_3_ANCHOR,
            replacement=PATCH_3_REPLACEMENT,
            idempotence_marker="${renderGarageCirclesSection()}",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
