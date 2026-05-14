#!/usr/bin/env python3
"""
CARNET · Lot 47 — L'alerte enchère

Source        : la dernière pièce constructible du "6" du 3-6-9 Vue
                Enchères. Les Lots 45-46 ont posé le pont
                bidirectionnel enchère <-> annonce dans les fiches.
                Le Lot 47 branche le même croisement sur le SYSTÈME
                D'ALERTES existant : quand une alerte modèle de
                l'utilisateur correspond à une enchère live/upcoming,
                la fiche alerte le signale — avec le compte à rebours.

  Le terrain rend ce lot léger :
    - le système d'alertes existe et est fonctionnel (State.alerts,
      CRUD, persistance, renderAlertSheet). On ne le construit pas,
      on le branche.
    - findAuctionBridge (Lot 46) a déjà la logique enchère ; le Lot
      47 en est une variante adaptée à la forme d'une alerte.
    - openAuction(id) résout déjà une enchère → data-action prêt.
    - le CSS .sheet-detail-bridge* (Lot 45) est réutilisé tel quel —
      ZÉRO style neuf.

  LA CONTRAINTE QUI DÉFINIT LE SCOPE — la forme d'une alerte :
    Un objet alerte n'a PAS de champs mk/mo séparés. Il a :
      type  : 'modele' | 'criteres' | 'rarete' | 'signal' | 'ecr'
      rule  : une CHAÎNE LIBRE (ex. "Porsche 911 R 991.2",
              "Mercedes 300 SL Gullwing", "Cote en baisse 6+ mois")
      meta, matches, paused
    Seules les alertes type === 'modele' ont une `rule` qui nomme un
    modèle précis. Les types criteres/rarete/signal/ecr décrivent des
    critères ABSTRAITS ("Moins de 500 ex. produits", "Référencée ECR
    Tier 1+") — impossibles à croiser avec une enchère par simple
    texte. Donc le pont alerte -> enchère ne s'applique QU'AUX
    alertes type === 'modele'. Pour les autres, le bloc n'apparaît
    pas — et c'est honnête, pas un manque : on ne fabrique pas un
    faux match sur un critère qu'on ne sait pas évaluer.

  LA LOGIQUE — findAuctionAlertMatch(alert) :
    - si alert.type !== 'modele' -> [] (rien, le bloc disparaît) ;
    - sinon, normalise alert.rule (trim + lowercase) ;
    - pour chaque enchère du pool (liveAuctions sinon mock AUCTIONS),
      status !== 'sold' uniquement (on ne propose que l'actionnable,
      comme le Lot 46) :
        match si la `rule` CONTIENT le brand de l'enchère ET CONTIENT
        le model de l'enchère (inclusion souple : la rule de
        l'utilisateur est en général plus longue et descriptive que
        le couple brand/model brut) ;
    - tri par hOffset croissant (la clôture la plus proche d'abord) ;
    - 3 max.
    Le sens du test : c'est l'enchère qu'on cherche DANS la rule, pas
    l'inverse. "Porsche 911 R 991.2" contient bien "porsche" et
    "911" -> une enchère Porsche 911 matche.

  CE QU'ON AFFICHE — bloc .sheet-detail-bridge (CSS du Lot 45) :
    - jusqu'à 3 enchères, clôture la plus proche en tête ;
    - par enchère : modèle, année, maison + n° de lot, enchère
      actuelle ou estimation, le temps restant ;
    - tap -> openAuction -> fiche enchère ;
    - voix CARNET : "Ton alerte a une correspondance aux enchères :
      [maison], clôture dans [temps]." (ou ouverture, si upcoming).
    Fallback mock AUCTIONS si State.liveAuctions vide -> démo = prod.

  CE QUE CE LOT NE FAIT PAS : la notification push/email réelle (pas
  de canal — c'est hors frontend) ; l'historique de cote (dépend de
  price_history non alimenté). Le Lot 47 fait l'affichage in-app du
  match, qui est la partie 100% constructible aujourd'hui.

Scope          : 3 patches sur index.html. PAS de patch CSS.

  ⚠ INDENTATION RÉELLE (vérifiée à l'octet — Leçon 10) :
    renderAlertSheet est à COLONNE 0, corps à 2 espaces, précédée du
    commentaire `// ===== SHEET RENDERERS =====`. Le bloc
    sheet-detail-rows dans renderAlertSheet est à 6 espaces
    (.sheet-detail-rows) / 8 (.sheet-detail-row) / 10 (les span).

  JS-1 : findAuctionAlertMatch(alert) — colonne 0 — insérée entre le
         commentaire UNIQUE `// ===== SHEET RENDERERS =====` et
         `function renderAlertSheet`.
  JS-2 : renderAlertBridgeBlock(alert) — colonne 0 — insérée entre la
         fin de findAuctionAlertMatch (posée par JS-1) et
         `function renderAlertSheet`.
  JS-3 : injection ${renderAlertBridgeBlock(a)} dans renderAlertSheet,
         juste après le bloc statut (fin du .sheet-detail-rows),
         avant la fermeture du .sheet-content. Borne basse
         discriminante : `<div class="sheet-actions grid-2">`.

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1. La borne haute JS-1 est le
    commentaire `// ===== SHEET RENDERERS =====` — UNIQUE et ASCII,
    pas un `}\\n\\n` anonyme. JS-2 ancre sur la fin de
    findAuctionAlertMatch posée par JS-1.
  - JS-2 dépend de JS-1 en ORDRE — garanti par la liste PATCHES.
    JS-3 indépendant.
  - findAuctionAlertMatch et renderAlertBridgeBlock déclarées AVANT
    renderAlertSheet en source order -> aucun souci de hoisting.
  - JS en strings normales ; apostrophes françaises en \\u2019.
  - Bloc purement additif : findAuctionAlertMatch renvoie [] (cas
    ultra-fréquent : tous les types != modele, et les alertes modele
    sans enchère correspondante) -> renderAlertBridgeBlock renvoie ''
    -> zéro régression sur les fiches alerte sans match.
  - Idempotence : marqueurs uniques au patch —
    'function findAuctionAlertMatch',
    'function renderAlertBridgeBlock',
    'renderAlertBridgeBlock(a)'.

Prérequis : Lot 45 appliqué (CSS .sheet-detail-bridge réutilisé)
Usage     :
    python3 apply_alerte_enchere_lot47.py path/to/index.html
    python3 apply_alerte_enchere_lot47.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# JS-1 — findAuctionAlertMatch. COLONNE 0, corps 2 espaces.
# Ne traite que type === 'modele'. Cherche brand+model de l'enchère
# DANS la rule libre de l'alerte. Filtre status !== 'sold'.
# ═══════════════════════════════════════════════════════════════════════

FIND_ALERT_FN = """// \u2500\u2500\u2500 Lot 47 \u00b7 l'alerte ench\u00e8re \u2500\u2500\u2500
// Croise une alerte de l'utilisateur avec les ench\u00e8res en cours.
// Ne traite QUE les alertes type === 'modele' : seules elles ont une
// `rule` qui nomme un mod\u00e8le pr\u00e9cis. Les types criteres/rarete/
// signal/ecr d\u00e9crivent des crit\u00e8res abstraits \u2014 on ne fabrique pas
// un faux match dessus. Filtre status !== 'sold' (seul l'actionnable,
// comme le Lot 46). Tri hOffset croissant : cl\u00f4ture la plus proche
// en t\u00eate.
function findAuctionAlertMatch(alert){
  if(!alert || alert.type !== 'modele') return [];
  var rule = String(alert.rule || '').trim().toLowerCase();
  if(!rule) return [];
  // Source : liveAuctions (DB) sinon mock AUCTIONS \u2014 d\u00e9mo = prod.
  var pool = (State.liveAuctions && State.liveAuctions.length)
    ? State.liveAuctions
    : ((typeof AUCTIONS !== 'undefined') ? AUCTIONS : []);
  if(!pool.length) return [];
  var found = [];
  for(var i = 0; i < pool.length; i++){
    var au = pool[i];
    // Seul l'actionnable : on \u00e9carte les ench\u00e8res termin\u00e9es.
    if(au.status === 'sold') continue;
    var brand = String(au.brand || '').trim().toLowerCase();
    var model = String(au.model || '').trim().toLowerCase();
    if(!brand || !model) continue;
    // On cherche l'ench\u00e8re DANS la rule : la rule de l'utilisateur
    // est en g\u00e9n\u00e9ral plus longue et descriptive que brand+model.
    if(rule.indexOf(brand) !== -1 && rule.indexOf(model) !== -1){
      found.push(au);
    }
  }
  // Tri hOffset croissant (cl\u00f4ture / ouverture la plus proche), 3 max.
  found = found.slice().sort(function(a, b){
    return (parseFloat(a.hOffset) || 0) - (parseFloat(b.hOffset) || 0);
  });
  return found.slice(0, 3);
}

"""

# ═══════════════════════════════════════════════════════════════════════
# JS-2 — renderAlertBridgeBlock. COLONNE 0, corps 2 espaces.
# Réutilise les classes CSS .sheet-detail-bridge* du Lot 45.
# ═══════════════════════════════════════════════════════════════════════

RENDER_ALERT_BRIDGE_FN = """// \u2500\u2500\u2500 Lot 47 \u00b7 rendu du bloc alerte \u2192 ench\u00e8re \u2500\u2500\u2500
// R\u00e9utilise les classes .sheet-detail-bridge* du Lot 45 (aucun style
// neuf). Renvoie '' si aucun match \u2192 bloc purement additif. Cas
// ultra-fr\u00e9quent (tous les types != modele) : '' silencieux.
function renderAlertBridgeBlock(alert){
  var matches = findAuctionAlertMatch(alert);
  if(!matches.length) return '';
  var items = matches.map(function(au){
    var priceTxt, priceLabel;
    if(au.status === 'live' && (parseFloat(au.bidCurrent) || 0) > 0){
      priceTxt = esc(fmtAuctionPrice(au.bidCurrent));
      priceLabel = 'ench\\u00e8re actuelle';
    } else {
      priceTxt = esc(fmtRange(au.estimateLow, au.estimateHigh));
      priceLabel = 'estimation';
    }
    var timeTxt = '';
    if(typeof formatTimeLeft === 'function'){
      var tl = formatTimeLeft(au.hOffset);
      timeTxt = (au.status === 'live') ? ('cl\\u00f4ture dans ' + tl) : ('ouverture dans ' + tl);
    }
    var src = esc(au.source || '');
    var lot = au.lot ? (' \\u00b7 ' + esc(au.lot)) : '';
    return '<div class=\"sheet-detail-bridge-item\" data-action=\"openAuction\" data-auction=\"' + esc(au.id) + '\">'
      + '<div class=\"sheet-detail-bridge-item-main\">'
      + '<div class=\"sheet-detail-bridge-item-model\">' + esc(au.model || '') + '</div>'
      + '<div class=\"sheet-detail-bridge-item-meta\">' + esc(au.year || '') + ' \\u00b7 ' + src + lot
      + (timeTxt ? ' \\u00b7 ' + timeTxt : '') + '</div>'
      + '</div>'
      + '<div class=\"sheet-detail-bridge-item-price\">'
      + '<div class=\"sheet-detail-bridge-item-price-value\">' + priceTxt + '</div>'
      + '<div class=\"sheet-detail-bridge-item-price-delta\" style=\"color:var(--gris)\">' + priceLabel + '</div>'
      + '</div>'
      + '</div>';
  }).join('');
  // Voix CARNET : on prend la plus urgente (matches[0], d\u00e9j\u00e0 tri\u00e9).
  var first = matches[0];
  var firstSrc = esc(first.source || 'une maison de vente');
  var tl = (typeof formatTimeLeft === 'function') ? formatTimeLeft(first.hOffset) : '';
  var voice;
  if(first.status === 'live'){
    voice = 'Ton alerte a une correspondance aux ench\\u00e8res : ' + firstSrc
      + (tl ? ' \\u2014 cl\\u00f4ture dans ' + tl + '.' : '.');
  } else {
    voice = 'Ton alerte a une correspondance \\u00e0 venir aux ench\\u00e8res : ' + firstSrc
      + (tl ? ' \\u2014 ouverture dans ' + tl + '.' : '.');
  }
  var label = matches.length === 1 ? 'Correspondance aux ench\\u00e8res' : 'Correspondances aux ench\\u00e8res \\u00b7 ' + matches.length + ' lots';
  return '<div class=\"sheet-detail-bridge\">'
    + '<div class=\"sheet-detail-bridge-label\">' + label + '</div>'
    + items
    + '<div class=\"sheet-detail-bridge-voice\">' + voice + '</div>'
    + '</div>';
}

"""


PATCHES = [
    Patch(
        name="JS-1 \u00b7 findAuctionAlertMatch \u2014 croisement alerte/ench\u00e8re (avant renderAlertSheet)",
        # Borne haute : le commentaire de section `// ===== SHEET
        # RENDERERS =====` — UNIQUE et ASCII (1 occurrence). Borne
        # basse : `function renderAlertSheet`.
        anchor="// ===== SHEET RENDERERS =====\nfunction renderAlertSheet(a){\n  if(!a) return '';",
        replacement="// ===== SHEET RENDERERS =====\n" + FIND_ALERT_FN + "function renderAlertSheet(a){\n  if(!a) return '';",
        idempotence_marker="function findAuctionAlertMatch",
    ),
    Patch(
        name="JS-2 \u00b7 renderAlertBridgeBlock \u2014 HTML du bloc (apr\u00e8s findAuctionAlertMatch)",
        # Borne haute : la fin de findAuctionAlertMatch posée par JS-1.
        # Sa dernière ligne `  return found.slice(0, 3);` est unique
        # (les bridges des Lots 45-46 finissent par `picked.slice`,
        # celui-ci par `found.slice`). Borne basse :
        # `function renderAlertSheet`.
        anchor="  return found.slice(0, 3);\n}\n\nfunction renderAlertSheet(a){\n  if(!a) return '';",
        replacement="  return found.slice(0, 3);\n}\n\n" + RENDER_ALERT_BRIDGE_FN + "function renderAlertSheet(a){\n  if(!a) return '';",
        idempotence_marker="function renderAlertBridgeBlock",
    ),
    Patch(
        name="JS-3 \u00b7 injection ${renderAlertBridgeBlock(a)} dans renderAlertSheet",
        # Borne haute : la fin du bloc statut (la statut row + la
        # fermeture du .sheet-detail-rows). Borne basse : `<div
        # class="sheet-actions grid-2">` — discriminant.
        # Indentation réelle : .sheet-detail-row à 8 esp, span à 10,
        # fermetures à 8/6/4.
        anchor="""        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Statut</span>
          <span class="sheet-detail-row-value">${esc(statusText)}</span>
        </div>
      </div>
    </div>
    <div class="sheet-actions grid-2">""",
        replacement="""        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Statut</span>
          <span class="sheet-detail-row-value">${esc(statusText)}</span>
        </div>
      </div>
      ${renderAlertBridgeBlock(a)}
    </div>
    <div class="sheet-actions grid-2">""",
        idempotence_marker="renderAlertBridgeBlock(a)",
    ),
]


PATCHSET = PatchSet(
    name="Lot 47 \u2014 L'alerte ench\u00e8re (findAuctionAlertMatch + bloc bridge dans la fiche alerte)",
    requires=[
        "function renderAlertSheet",
        # Le Lot 45 doit être appliqué : on réutilise son CSS.
        ".sheet-detail-bridge {",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
