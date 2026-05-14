#!/usr/bin/env python3
"""
CARNET · Lot 51 — Vue message en lecture (boucher le "bientôt" n°2)

Source        : audit des features "bientôt". Le handler openMessage —
                quand un vendeur clique sur un message d'acheteur dans
                son tableau de bord d'annonce — affiche un toast
                "Conversation avec X — bientôt disponible". Un cul-de-
                sac : le message existe, il est listé, cliquable, mais
                cliquer ne mène à rien.

  LA DÉCISION — ce qu'on fait, ce qu'on ne fait PAS :
    Une vraie messagerie bidirectionnelle (envoi, réception, temps
    réel, notifications) c'est du BACKEND. Côté frontend pur on ne
    peut pas la construire honnêtement — un champ "Répondre" qui
    n'envoie rien serait une FAUSSE fonctionnalité, pire que le toast
    actuel. L'utilisateur taperait une réponse, cliquerait "Envoyer",
    et rien ne partirait.

    Donc ce lot NE fait PAS de champ de réponse. Il fait une vue
    message EN LECTURE : une vraie sheet, propre, qui MONTRE le
    message (l'expéditeur, le contenu, l'offre, la date, le statut),
    et qui DIT clairement et sans mentir que la réponse in-app
    arrivera avec le réseau Carnet. On remplace un cul-de-sac opaque
    (toast qui disparaît) par un cul-de-sac informatif et soigné
    (sheet qui montre tout ce qu'on a). C'est honnête : on ne promet
    pas ce qu'on n'a pas, on présente bien ce qu'on a.

  CE QUI EXISTE DÉJÀ :
    - generateListingDashboard(car) génère les messages d'une annonce
      de façon déterministe : un objet message =
        { id, from, preview, offer, daysAgo, status }
    - la liste est affichée et cliquable (.dashboard-message →
      data-action="openMessage" data-id=msgId data-car=carId)
    - le système de sheets (Sheet.open / le routing sheetView) est
      éprouvé — il suffit d'y ajouter un cas 'message'.
    Les messages ne sont PAS stockés : ils sont régénérés depuis la
    voiture. La sheet recevra donc { msg, car } en sheetData et
    openMessage les lui passera (comme il les reconstruit déjà
    aujourd'hui pour le toast).

  Les 4 patches :
    1. CSS .message-sheet-* — styles de la vue lecture. Couleurs
       100% tokens charte v9.
    2. Handler openMessage — au lieu du toast, ouvre
       Sheet.open('message', { msg, car }). Le reste (résolution
       car + msg via generateListingDashboard) est CONSERVÉ — c'est
       déjà la bonne logique.
    3. renderMessageSheet — la vue lecture : en-tête (expéditeur,
       date, statut), le contenu du message, l'offre si présente
       (mise en valeur), et un encart honnête "La réponse in-app
       arrive avec le réseau Carnet". Bouton de fermeture seulement —
       PAS de champ de saisie.
    4. Routing — sheetView === 'message' → renderMessageSheet.

Scope          : 4 patches sur index.html.

  ⚠ INDENTATION RÉELLE (vérifiée à l'octet — Leçon 10) :
    - le CSS de la zone dashboard : sélecteurs à 4 espaces.
    - les handlers de l'objet Actions : 2 espaces, corps 4.
    - les fonctions render*Sheet : COLONNE 0, template à 4-6 espaces.
    - le routing : la chaîne `else if(State.sheetView === ...`.

  P1 : CSS .message-sheet-* — inséré après la règle
       .dashboard-message:hover.
  P2 : handler openMessage — le corps `Sheet.close() + setTimeout
       toast` remplacé par `Sheet.open('message', { msg, car })`.
  P3 : renderMessageSheet — inséré entre la fin de
       renderWatchedSheet et `function renderAddGarageSheet`.
  P4 : routing — `sheetView === 'message'` ajouté après la ligne
       `sheetView === 'watched'`.

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1. Points d'ancrage vérifiés
    UNIQUES à l'octet.
  - PAS de <form> HTML, PAS de champ de saisie — décision explicite
    (voir ci-dessus). La sheet est en lecture seule.
  - renderMessageSheet est défensive : sheetData absent, msg/car
    manquants → renvoie '' (pas de crash).
  - openMessage conserve ses gardes existantes (if(!c) return ;
    if(!msg) return).
  - Idempotence : marqueurs uniques au patch.

Prérequis : aucun (lot autonome)
Usage     :
    python3 apply_message_lecture_lot51.py path/to/index.html
    python3 apply_message_lecture_lot51.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# P1 — CSS .message-sheet-*. Anchor 2-bornes : borne haute = les règles
# :active + :hover COMPLÈTES (vérifiées à l'octet), borne basse = le
# début de la règle .dashboard-message.unread. Le bloc message-sheet
# s'insère entre les deux. Sélecteurs 4 espaces. Couleurs tokens v9.
# ═══════════════════════════════════════════════════════════════════════

CSS_ANCHOR = """.dashboard-message:active { transform: scale(0.99); }
    .dashboard-message:hover { border-color: var(--orange-polo); }
    .dashboard-message.unread {"""

MESSAGE_CSS_BLOCK = """    /* ===== LOT 51 \u00b7 VUE MESSAGE EN LECTURE ===== */
    .message-sheet-meta {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 13px;
      margin-bottom: 13px;
    }
    .message-sheet-from {
      font-family: var(--editorial);
      font-size: 17px;
      color: var(--encre);
    }
    .message-sheet-date {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--gris);
      flex-shrink: 0;
    }
    .message-sheet-status {
      display: inline-block;
      font-family: var(--mono);
      font-size: 9px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: var(--r);
      margin-bottom: 13px;
    }
    .message-sheet-status.unread {
      color: var(--orange-polo);
      background: var(--orange-polo-soft);
    }
    .message-sheet-status.replied {
      color: var(--vert-vivant);
      background: var(--papier-soft);
    }
    .message-sheet-body {
      font-family: var(--editorial);
      font-size: 15px;
      line-height: 1.6;
      color: var(--encre);
      padding: 16px;
      background: var(--papier-soft);
      border-radius: var(--r);
    }
    .message-sheet-offer {
      margin-top: 13px;
      padding: 13px 16px;
      background: var(--encre);
      border-radius: var(--r);
    }
    .message-sheet-offer-label {
      font-family: var(--mono);
      font-size: 9px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--vert-vivant-clair);
      margin-bottom: 4px;
    }
    .message-sheet-offer-value {
      font-family: var(--editorial);
      font-size: 21px;
      color: var(--papier);
    }
    .message-sheet-note {
      margin-top: 16px;
      padding-top: 13px;
      border-top: 1px solid var(--gris-line-soft);
      font-family: var(--editorial);
      font-style: italic;
      font-size: 13px;
      line-height: 1.5;
      color: var(--gris);
    }
"""

CSS_REPLACEMENT = """.dashboard-message:active { transform: scale(0.99); }
    .dashboard-message:hover { border-color: var(--orange-polo); }
""" + MESSAGE_CSS_BLOCK + """    .dashboard-message.unread {"""


# ═══════════════════════════════════════════════════════════════════════
# P2 — handler openMessage : toast → Sheet.open('message', {msg, car}).
# Indentation 2/4.
# ═══════════════════════════════════════════════════════════════════════

OPENMSG_OLD = """  openMessage(messageId, carId){
    const c = (State.garage || []).find(x => x.id === carId);
    if(!c) return;
    const dash = generateListingDashboard(c);
    const msg = dash.messages.find(m => m.id === messageId);
    if(!msg) return;
    Sheet.close();
    setTimeout(() => {
      const offerLine = msg.offer ? ` \\nOffre propos\u00e9e : ${fmtPrice(msg.offer)}.` : '';
      showToastFloat(`Conversation avec ${msg.from} \\u2014 bient\u00f4t disponible.${offerLine}`);
    }, 340);
  },"""

OPENMSG_NEW = """  openMessage(messageId, carId){
    const c = (State.garage || []).find(x => x.id === carId);
    if(!c) return;
    const dash = generateListingDashboard(c);
    const msg = dash.messages.find(m => m.id === messageId);
    if(!msg) return;
    // Lot 51 : ouvre la vue message en lecture (sheet d\\u00e9di\\u00e9e) au lieu
    // d'un toast \\u00e9ph\\u00e9m\\u00e8re. La sheet re\\u00e7oit { msg, car } \\u2014 les messages
    // ne sont pas stock\\u00e9s, ils sont reconstruits depuis la voiture.
    Sheet.open('message', { msg: msg, car: c });
  },"""

# ═══════════════════════════════════════════════════════════════════════
# P3 — renderMessageSheet. COLONNE 0. Inséré entre la fin de
# renderWatchedSheet et function renderAddGarageSheet.
# ═══════════════════════════════════════════════════════════════════════

RENDER_MSG_FN = """function renderMessageSheet(data){
  // Lot 51 : vue message EN LECTURE. data = { msg, car }. Pas de champ
  // de r\u00e9ponse \u2014 la messagerie bidirectionnelle est backend ; on ne
  // simule pas un envoi qui ne partirait pas. On montre ce qu'on a,
  // proprement, et on dit honn\u00eatement ce qui arrive.
  if(!data || !data.msg) return '';
  const msg = data.msg;
  const car = data.car || {};
  const carName = [car.brand, car.model].filter(Boolean).join(' ') || 'cette annonce';
  const statusCls = msg.status === 'replied' ? 'replied' : 'unread';
  const statusLabel = msg.status === 'replied' ? 'D\\u00e9j\\u00e0 r\\u00e9pondu' : 'Non lu';
  const dateLabel = 'il y a ' + msg.daysAgo + ' j' + (msg.daysAgo > 1 ? 's' : '');
  const offerBlock = msg.offer ? `
        <div class="message-sheet-offer">
          <div class="message-sheet-offer-label">Offre propos\\u00e9e</div>
          <div class="message-sheet-offer-value">${esc(fmtPrice(msg.offer))}</div>
        </div>
      ` : '';
  return `
    <div class="sheet-handle-area" data-sheet-drag>
      <div class="sheet-handle"></div>
    </div>
    <div class="sheet-header">
      <div>
        <div class="sheet-tag">MESSAGE \\u00b7 ${esc(carName)}</div>
        <h2 class="sheet-title">${esc(msg.from)}</h2>
      </div>
      <button class="sheet-close" data-action="closeSheet" aria-label="Fermer">\\u00d7</button>
    </div>
    <div class="sheet-content">
      <div class="message-sheet-meta">
        <span class="message-sheet-date">${esc(dateLabel)}</span>
      </div>
      <span class="message-sheet-status ${statusCls}">${esc(statusLabel)}</span>
      <div class="message-sheet-body">${esc(msg.preview)}</div>
      ${offerBlock}
      <p class="message-sheet-note">La r\\u00e9ponse in-app arrive avec le r\\u00e9seau Carnet. En attendant, tu retrouves ${esc(msg.from)} et son message ici \\u2014 rien ne se perd.</p>
    </div>
    <div class="sheet-actions">
      <button class="sheet-btn primary" data-action="closeSheet">Fermer</button>
    </div>
  `;
}

"""


PATCHES = [
    Patch(
        name="P1 \u00b7 CSS .message-sheet-* (entre :hover et .unread)",
        anchor=CSS_ANCHOR,
        replacement=CSS_REPLACEMENT,
        idempotence_marker=".message-sheet-body {",
    ),
    Patch(
        name="P2 \u00b7 openMessage \u2014 ouvre la sheet message au lieu du toast",
        anchor=OPENMSG_OLD,
        replacement=OPENMSG_NEW,
        idempotence_marker="Sheet.open('message', { msg: msg, car: c });",
    ),
    Patch(
        name="P3 \u00b7 renderMessageSheet \u2014 vue lecture (entre renderWatchedSheet et renderAddGarageSheet)",
        # Borne haute : la fin de renderWatchedSheet, identifi\u00e9e par le
        # bouton removeWatched (texte UNIQUE \u00e0 cette fonction). Borne
        # basse : function renderAddGarageSheet. Le bloc renderMessage
        # s'ins\u00e8re entre les deux.
        anchor='removeWatched" data-id="${esc(w.id)}">Retirer ce mod\u00e8le</button>\n    </div>\n  `;\n}\n\nfunction renderAddGarageSheet(){',
        replacement='removeWatched" data-id="${esc(w.id)}">Retirer ce mod\u00e8le</button>\n    </div>\n  `;\n}\n\n' + RENDER_MSG_FN + "function renderAddGarageSheet(){",
        idempotence_marker="function renderMessageSheet",
    ),
    Patch(
        name="P4 \u00b7 routing sheetView === 'message'",
        # Anchor 2-bornes : ligne 'watched' (borne haute) + ligne
        # 'garageCar' (borne basse). On ins\u00e8re la ligne 'message'
        # entre les deux \u2014 l'insertion rompt l'anchor.
        anchor="se if(State.sheetView === 'watched') html = renderWatchedSheet(State.sheetData);\n    else if(State.sheetView === 'garageCar') html = renderGarageCarSheet(State.sheetData);",
        replacement="se if(State.sheetView === 'watched') html = renderWatchedSheet(State.sheetData);\n    else if(State.sheetView === 'message') html = renderMessageSheet(State.sheetData);\n    else if(State.sheetView === 'garageCar') html = renderGarageCarSheet(State.sheetData);",
        idempotence_marker="State.sheetView === 'message'",
    ),
]


PATCHSET = PatchSet(
    name="Lot 51 \u2014 Vue message en lecture (sheet honn\u00eate, pas de faux champ d'envoi)",
    requires=[
        "openMessage(messageId, carId){",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
