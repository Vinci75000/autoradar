#!/usr/bin/env python3
"""
CARNET · Lot 46 — Le pont annonce → enchère (le sens inverse)

Source        : suite du "6" du 3-6-9 Vue Enchères. Le Lot 45 a posé
                le pont enchère → annonce dans renderAuctionSheet. Le
                Lot 46 fait le miroir : depuis une annonce en vente
                fixe, signaler qu'une équivalente passe AUX ENCHÈRES.

  Le pattern du Lot 45 est validé (6/6 tests fonctionnels) — le Lot 46
  le réutilise en miroir. Même socle :
    - enchères et annonces dans la MÊME table `cars` (is_auction),
      les deux datasets déjà en mémoire (State.liveAuctions /
      State.liveListings). Zéro requête.
    - openAuction(id) sait déjà résoudre une enchère (lit AUCTIONS,
      le catalogue) → le bloc pont n'a qu'à émettre
      data-action="openAuction".

  LA DIFFÉRENCE QUI REND CE SENS MALIN — le filtre status :
    Depuis une enchère, montrer une annonce a toujours du sens
    (situer la cote). Depuis une annonce, montrer une enchère SOLD
    n'a AUCUNE valeur actionnable — c'est du passé. Donc
    findAuctionBridge ne retient que les enchères status !== 'sold'
    (live + upcoming) : on ne propose QUE ce qui est encore jouable.
    Et la voix CARNET devient temporelle — "ça clôture dans 2 jours"
    — au lieu de seulement situer un prix. C'est l'angle que les
    agrégateurs n'ont pas : depuis une annonce statique, une fenêtre
    de tir sur une vente aux enchères vivante.

  LA LOGIQUE DE MATCHING — findAuctionBridge(listing) :
    Identique à findMarketBridge mais source = enchères, cible =
    annonce. Marque normalisée identique ET inclusion souple du
    modèle ET tolérance année (niveau 1 : ±2, niveau 2 : ±5).
    PLUS : filtre status !== 'sold' appliqué AVANT le matching.
    Niveau 3 (aucun match) → rien, le bloc n'apparaît pas.
    Tri : par hOffset croissant (la clôture la plus proche d'abord —
    l'urgence en tête), 3 max.

  CE QU'ON AFFICHE — bloc .sheet-detail-bridge (CSS réutilisé du
  Lot 45, aucun style neuf) :
    - jusqu'à 3 enchères, clôture la plus proche en tête ;
    - par enchère : modèle, année, maison de vente + n° de lot,
      enchère actuelle ou estimation ;
    - tap → openAuction → fiche enchère ;
    - voix CARNET temporelle :
        live    → "Une équivalente est aux enchères chez [maison] —
                   clôture dans [temps]."
        upcoming→ "Une équivalente passe aux enchères chez [maison] —
                   ouverture dans [temps]."
    Fallback mock AUCTIONS si State.liveAuctions vide → démo = prod.

  CE QUE CE LOT NE FAIT PAS : l'alerte enchère, l'historique de cote
  (suite du 6) ; l'AutoRadar Auction Index (le 9). Mais les deux
  ponts (45 + 46) forment ensemble la structure de croisement
  bidirectionnelle sur laquelle le 9 s'agrégera.

Scope          : 3 patches sur index.html. PAS de patch CSS — le bloc
  réutilise .sheet-detail-bridge posé par le Lot 45.

  ⚠ INDENTATION RÉELLE (vérifiée à l'octet — Leçon 10) :
    renderListingSheet est à COLONNE 0, corps à 2 espaces, précédée
    de `}\\n\\n`. Le bloc SOURCE dans renderListingSheet est à 6
    espaces (.sheet-section-label) / 8 espaces (.sheet-detail-row).
    Tous les anchors et blocs insérés respectent CES indentations.

  JS-1 : findAuctionBridge(listing) — colonne 0 — insérée entre la
         fin de la fonction sœur précédente
         (`renderGarageFormStateDebug();\\n}\\n\\n` — fragment UNIQUE,
         1 occurrence) et `function renderListingSheet`.
  JS-2 : renderListingBridgeBlock(listing) — colonne 0 — insérée
         entre la fin de findAuctionBridge (posée par JS-1) et
         `function renderListingSheet`.
  JS-3 : injection ${renderListingBridgeBlock(l)} dans
         renderListingSheet, juste après le bloc SOURCE, avant la
         fermeture du .sheet-content. Borne basse discriminante :
         `<div class="sheet-actions">` (sans `-detail` — distingue
         de renderAuctionSheet).

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1. Les bornes hautes JS-1/JS-2
    utilisent des fragments UNIQUES et ASCII (pas de `}\\n\\n`
    anonyme) → garde-fou satisfait, idempotence garantie.
  - JS-2 dépend de JS-1 en ORDRE (ancre sur la fin de
    findAuctionBridge) — ordre garanti par la liste PATCHES. JS-3
    indépendant.
  - findAuctionBridge et renderListingBridgeBlock déclarées AVANT
    renderListingSheet en source order → aucun souci de hoisting.
  - JS en strings normales ; apostrophes françaises en \\u2019.
  - Bloc purement additif : findAuctionBridge renvoie [] →
    renderListingBridgeBlock renvoie '' → zéro régression sur les
    fiches sans match.
  - Idempotence : marqueurs uniques au patch —
    'function findAuctionBridge', 'function renderListingBridgeBlock',
    'renderListingBridgeBlock(l)'.

Prérequis : Lot 45 appliqué (CSS .sheet-detail-bridge réutilisé)
Usage     :
    python3 apply_pont_annonce_enchere_lot46.py path/to/index.html
    python3 apply_pont_annonce_enchere_lot46.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# JS-1 — findAuctionBridge. COLONNE 0, corps 2 espaces.
# Miroir de findMarketBridge : source = enchères, cible = annonce.
# Filtre status !== 'sold' AVANT le matching. Tri par hOffset croissant.
# ═══════════════════════════════════════════════════════════════════════

FIND_AUCTION_FN = """// \u2500\u2500\u2500 Lot 46 \u00b7 le pont annonce \u2192 ench\u00e8re (sens inverse) \u2500\u2500\u2500
// Miroir de findMarketBridge : depuis une annonce en vente fixe,
// cherche les ENCH\u00c8RES du m\u00eame mod\u00e8le. Filtre status !== 'sold' :
// une ench\u00e8re close n'a aucune valeur actionnable depuis une annonce
// \u2014 on ne propose que ce qui est encore jouable (live + upcoming).
// Tri par hOffset croissant : la cl\u00f4ture la plus proche en t\u00eate.
function findAuctionBridge(listing){
  if(!listing) return [];
  // Source : liveAuctions (DB) sinon mock AUCTIONS \u2014 d\u00e9mo = prod.
  var pool = (State.liveAuctions && State.liveAuctions.length)
    ? State.liveAuctions
    : ((typeof AUCTIONS !== 'undefined') ? AUCTIONS : []);
  if(!pool.length) return [];
  var brand = String(listing.mk || '').trim().toLowerCase();
  var model = String(listing.mo || '').trim().toLowerCase();
  var year = parseInt(listing.yr, 10);
  if(!brand || !model) return [];
  function modelMatch(auctionModel){
    var mm = String(auctionModel || '').trim().toLowerCase();
    if(!mm) return false;
    return mm.indexOf(model) !== -1 || model.indexOf(mm) !== -1;
  }
  var lvl1 = [], lvl2 = [];
  for(var i = 0; i < pool.length; i++){
    var au = pool[i];
    // Seul l'actionnable : on \u00e9carte les ench\u00e8res termin\u00e9es.
    if(au.status === 'sold') continue;
    if(String(au.brand || '').trim().toLowerCase() !== brand) continue;
    if(!modelMatch(au.model)) continue;
    var ay = parseInt(au.year, 10);
    var dy = (!isNaN(year) && !isNaN(ay)) ? Math.abs(year - ay) : 99;
    if(dy <= 2) lvl1.push(au);
    else if(dy <= 5) lvl2.push(au);
  }
  // Niveau 1 prioritaire ; \u00e0 d\u00e9faut niveau 2. Tri hOffset croissant
  // (cl\u00f4ture / ouverture la plus proche d'abord), 3 max.
  var picked = lvl1.length ? lvl1 : lvl2;
  picked = picked.slice().sort(function(a, b){
    return (parseFloat(a.hOffset) || 0) - (parseFloat(b.hOffset) || 0);
  });
  return picked.slice(0, 3);
}

"""

# ═══════════════════════════════════════════════════════════════════════
# JS-2 — renderListingBridgeBlock. COLONNE 0, corps 2 espaces.
# Réutilise les classes CSS .sheet-detail-bridge* du Lot 45.
# ═══════════════════════════════════════════════════════════════════════

RENDER_LISTING_BRIDGE_FN = """// \u2500\u2500\u2500 Lot 46 \u00b7 rendu du bloc pont annonce \u2192 ench\u00e8re \u2500\u2500\u2500
// R\u00e9utilise les classes .sheet-detail-bridge* du Lot 45 (aucun style
// neuf). Renvoie '' si aucun match \u2192 bloc purement additif.
function renderListingBridgeBlock(listing){
  var matches = findAuctionBridge(listing);
  if(!matches.length) return '';
  var items = matches.map(function(au){
    // Prix affich\u00e9 : ench\u00e8re actuelle si live, estimation sinon.
    var priceTxt, priceLabel;
    if(au.status === 'live' && (parseFloat(au.bidCurrent) || 0) > 0){
      priceTxt = esc(fmtAuctionPrice(au.bidCurrent));
      priceLabel = 'ench\\u00e8re actuelle';
    } else {
      priceTxt = esc(fmtRange(au.estimateLow, au.estimateHigh));
      priceLabel = 'estimation';
    }
    // Ligne temps : cl\u00f4ture (live) ou ouverture (upcoming).
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
  // Voix CARNET temporelle : on prend la plus urgente (matches[0],
  // d\u00e9j\u00e0 tri\u00e9 par hOffset croissant).
  var first = matches[0];
  var voice;
  var firstSrc = esc(first.source || 'une maison de vente');
  if(first.status === 'live'){
    var tlLive = (typeof formatTimeLeft === 'function') ? formatTimeLeft(first.hOffset) : '';
    voice = 'Une \\u00e9quivalente est aux ench\\u00e8res chez ' + firstSrc
      + (tlLive ? ' \\u2014 cl\\u00f4ture dans ' + tlLive + '.' : '.');
  } else {
    var tlUp = (typeof formatTimeLeft === 'function') ? formatTimeLeft(first.hOffset) : '';
    voice = 'Une \\u00e9quivalente passe aux ench\\u00e8res chez ' + firstSrc
      + (tlUp ? ' \\u2014 ouverture dans ' + tlUp + '.' : '.');
  }
  var label = matches.length === 1 ? 'Aussi aux ench\\u00e8res' : 'Aussi aux ench\\u00e8res \\u00b7 ' + matches.length + ' lots';
  return '<div class=\"sheet-detail-bridge\">'
    + '<div class=\"sheet-detail-bridge-label\">' + label + '</div>'
    + items
    + '<div class=\"sheet-detail-bridge-voice\">' + voice + '</div>'
    + '</div>';
}

"""


PATCHES = [
    Patch(
        name="JS-1 \u00b7 findAuctionBridge \u2014 matching inverse, filtre status (avant renderListingSheet)",
        # Borne haute : la FIN de updateGarageFormStateDebug, identifiée
        # par le fragment UNIQUE et ASCII `renderGarageFormStateDebug();`
        # (1 seule occurrence — vérifié). Pas un `}\n\n` anonyme.
        # Borne basse : `function renderListingSheet`.
        anchor="renderGarageFormStateDebug();\n}\n\nfunction renderListingSheet(l){\n  if(!l) return '';",
        replacement="renderGarageFormStateDebug();\n}\n\n" + FIND_AUCTION_FN + "function renderListingSheet(l){\n  if(!l) return '';",
        idempotence_marker="function findAuctionBridge",
    ),
    Patch(
        name="JS-2 \u00b7 renderListingBridgeBlock \u2014 HTML du bloc (apr\u00e8s findAuctionBridge)",
        # Borne haute : la fin de findAuctionBridge posée par JS-1, dont
        # la dernière ligne `  return picked.slice(0, 3);` suivie de
        # `\n}\n\n` est unique à cet endroit après JS-1 (findMarketBridge
        # du Lot 45 finit pareil MAIS est suivie de
        # `function renderBridgeBlock`, pas `function renderListingSheet`
        # — la borne basse discrimine). Borne basse :
        # `function renderListingSheet`.
        anchor="  return picked.slice(0, 3);\n}\n\nfunction renderListingSheet(l){\n  if(!l) return '';",
        replacement="  return picked.slice(0, 3);\n}\n\n" + RENDER_LISTING_BRIDGE_FN + "function renderListingSheet(l){\n  if(!l) return '';",
        idempotence_marker="function renderListingBridgeBlock",
    ),
    Patch(
        name="JS-3 \u00b7 injection ${renderListingBridgeBlock(l)} dans renderListingSheet",
        # Borne haute : la fin du bloc SOURCE (le `Score CARNET` row +
        # les 2 fermetures `</div>`). Borne basse : `<div
        # class="sheet-actions">` SANS `-detail` — discrimine de
        # renderAuctionSheet (qui a `sheet-actions-detail`).
        # Indentation réelle : .sheet-detail-rows à 6 espaces, le row
        # à 8, les fermetures à 6 puis 4.
        anchor="""        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Score CARNET</span><span class="sheet-detail-row-value">${l.sc} / 100</span></div>
      </div>
    </div>
    <div class="sheet-actions">""",
        replacement="""        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Score CARNET</span><span class="sheet-detail-row-value">${l.sc} / 100</span></div>
      </div>
      ${renderListingBridgeBlock(l)}
    </div>
    <div class="sheet-actions">""",
        idempotence_marker="renderListingBridgeBlock(l)",
    ),
]


PATCHSET = PatchSet(
    name="Lot 46 \u2014 Le pont annonce \u2192 ench\u00e8re (findAuctionBridge + bloc bridge inverse)",
    requires=[
        "function renderListingSheet",
        # Le Lot 45 doit être appliqué : on réutilise son CSS.
        ".sheet-detail-bridge {",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
