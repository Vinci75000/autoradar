#!/usr/bin/env python3
"""
CARNET · Lot 45 — Le pont enchère → annonce

Source        : le "6" du 3-6-9 Vue Enchères — "apporter ce que les
                autres ne font pas". Les agrégateurs d'enchères
                montrent un lot isolé. Carnet le SITUE dans le marché :
                "cette 992 Turbo S part chez RM Sotheby's — et il y en
                a une équivalente en vente fixe chez un dealer."

  Le terrain rend ce lot possible SANS aucune intégration :
    - Enchères et annonces vivent dans la MÊME table `cars`,
      distinguées par `is_auction`. Les deux datasets sont déjà en
      mémoire : State.liveAuctions et State.liveListings, tous deux
      peuplés au boot. Zéro requête supplémentaire — on croise deux
      tableaux qui sont déjà là.
    - openListing(id) sait déjà résoudre une annonce (liveListings
      puis fallback mock LISTINGS) → le bloc pont n'a qu'à émettre
      data-action="openListing".

  LA LOGIQUE DE MATCHING — findMarketBridge(auction) — 3 niveaux :
    NIVEAU 1 — match fort : marque identique (normalisée) ET
      inclusion souple du modèle (A⊃B ou B⊃A) ET |année| <= 2.
    NIVEAU 2 — marque+modèle, |année| <= 5.
    NIVEAU 3 — aucun match → on n'affiche RIEN. Le silence est plus
      crédible que le remplissage.
  Inclusion souple car un `==` strict sur le modèle raterait la
  quasi-totalité des ponts réels. Tolérance année car année modèle
  vs production vs 1re immat — les sources datent différemment.

  CE QU'ON AFFICHE — bloc .sheet-detail-bridge :
    jusqu'à 3 annonces triées par prix croissant ; par annonce :
    modèle, année, km, prix, source ; si prix < estimation basse →
    signal "-X%" en --vert-vivant ; tap → openListing ; une ligne de
    voix CARNET factuelle. Fallback mock LISTINGS si liveListings
    vide → marche en démo comme en prod.

  CE QUE CE LOT NE FAIT PAS : le sens inverse (annonce → enchère,
  Lot 46) ; l'historique de cote / l'Index (le "9"). Mais ce bloc
  POSE la structure de croisement sur laquelle le 9 s'agrégera.

Scope          : 4 patches sur index.html.

  ⚠ INDENTATION RÉELLE (vérifiée à l'octet — Leçon 10) :
    - les fonctions JS de cette zone (renderAuctionSheet et sœurs)
      sont à COLONNE 0, corps à 2 espaces, séparées par `}\\n\\n`.
    - le CSS de cette zone : sélecteurs à 4 espaces, corps à 6.
    - le bloc voice dans renderAuctionSheet est à 8 espaces.
  Tous les anchors et tous les blocs insérés ci-dessous respectent
  CES indentations réelles, pas une indentation supposée.

  CSS-1 : styles .sheet-detail-bridge insérés entre la fermeture de
          `.sheet-detail-voice em {` et `.sheet-actions-detail {`.
          Sélecteurs 4 esp / corps 6 esp. Couleurs 100% tokens v9.
  JS-1  : findMarketBridge(auction) — colonne 0 — insérée entre la
          fin de la fonction sœur précédente (`}\\n\\n`) et
          `function renderAuctionSheet`.
  JS-2  : renderBridgeBlock(auction) — colonne 0 — insérée entre la
          fin de findMarketBridge (posée par JS-1) et
          `function renderAuctionSheet`.
  JS-3  : injection ${renderBridgeBlock(a)} dans renderAuctionSheet,
          juste après le bloc .sheet-detail-voice (8 esp).

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1.
  - JS-2 dépend de JS-1 en ORDRE (ancre sur la fin de
    findMarketBridge) — ordre garanti par la liste PATCHES.
    CSS-1 et JS-3 indépendants.
  - findMarketBridge et renderBridgeBlock déclarées AVANT
    renderAuctionSheet en source order → aucun souci de hoisting.
  - JS en strings normales ; apostrophes françaises en \\u2019
    (ASCII-safe dans le source).
  - Bloc purement additif : findMarketBridge renvoie [] →
    renderBridgeBlock renvoie '' → zéro régression sur fiches sans
    match.
  - Idempotence : marqueurs uniques au patch —
    '.sheet-detail-bridge {', 'function findMarketBridge',
    'function renderBridgeBlock', 'renderBridgeBlock(a)'.

Prérequis : aucun (vérifie juste renderAuctionSheet)
Usage     :
    python3 apply_pont_enchere_annonce_lot45.py path/to/index.html
    python3 apply_pont_enchere_annonce_lot45.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# CSS-1 — styles du bloc pont.
# Indentation RÉELLE : sélecteurs 4 espaces, corps 6 espaces (vérifié à
# l'octet sur le voisinage .sheet-detail-voice). Le voisinage utilise des
# px en dur + var(--r) : on s'y aligne. Couleurs 100% tokens charte v9.
# ═══════════════════════════════════════════════════════════════════════

CSS_HIGH = """    .sheet-detail-voice em {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 14px;
      line-height: 1.5;
      color: var(--encre);
      font-style: italic;
    }
"""

CSS_LOW = "    .sheet-actions-detail {"

BRIDGE_CSS = """    /* ===== LOT 45 · PONT ENCHÈRE → ANNONCE ===== */
    .sheet-detail-bridge {
      margin-top: 21px;
      padding: 21px;
      background: var(--papier-soft);
      border: 1px solid var(--gris-line);
      border-radius: var(--r);
    }
    .sheet-detail-bridge-label {
      font-family: var(--mono);
      font-size: 9px;
      letter-spacing: 0.16em;
      color: var(--gris);
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 13px;
    }
    .sheet-detail-bridge-item {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 13px;
      padding: 13px 0;
      border-top: 1px solid var(--gris-line-soft);
      cursor: pointer;
    }
    .sheet-detail-bridge-item:first-of-type {
      border-top: none;
    }
    .sheet-detail-bridge-item:active {
      opacity: 0.6;
    }
    .sheet-detail-bridge-item-main {
      min-width: 0;
    }
    .sheet-detail-bridge-item-model {
      font-family: var(--editorial);
      font-size: 15px;
      color: var(--encre);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .sheet-detail-bridge-item-meta {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--gris);
      margin-top: 2px;
    }
    .sheet-detail-bridge-item-price {
      text-align: right;
      flex-shrink: 0;
    }
    .sheet-detail-bridge-item-price-value {
      font-family: var(--mono);
      font-size: 15px;
      color: var(--encre);
    }
    .sheet-detail-bridge-item-price-delta {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--vert-vivant);
      margin-top: 2px;
    }
    .sheet-detail-bridge-voice {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 14px;
      color: var(--gris);
      margin-top: 13px;
      padding-top: 13px;
      border-top: 1px solid var(--gris-line-soft);
    }
"""

# ═══════════════════════════════════════════════════════════════════════
# JS-1 — findMarketBridge. COLONNE 0 (indentation réelle de la zone).
# Corps à 2 espaces.
# ═══════════════════════════════════════════════════════════════════════

FIND_BRIDGE_FN = """// \u2500\u2500\u2500 Lot 45 \u00b7 le pont ench\u00e8re \u2192 annonce \u2500\u2500\u2500
// Croise une ench\u00e8re avec les annonces en vente fixe (m\u00eame table
// `cars`, is_auction=false). Tout est d\u00e9j\u00e0 en m\u00e9moire : aucune
// requ\u00eate. Matching en 3 niveaux ; niveau 3 = rien (le silence est
// plus cr\u00e9dible qu'un faux pont).
function findMarketBridge(auction){
  if(!auction) return [];
  // Source : liveListings (DB) sinon mock LISTINGS \u2014 marche en d\u00e9mo
  // comme en prod.
  var pool = (State.liveListings && State.liveListings.length)
    ? State.liveListings
    : ((typeof LISTINGS !== 'undefined') ? LISTINGS : []);
  if(!pool.length) return [];
  var brand = String(auction.brand || '').trim().toLowerCase();
  var model = String(auction.model || '').trim().toLowerCase();
  var year = parseInt(auction.year, 10);
  if(!brand || !model) return [];
  function modelMatch(listingModel){
    var mm = String(listingModel || '').trim().toLowerCase();
    if(!mm) return false;
    return mm.indexOf(model) !== -1 || model.indexOf(mm) !== -1;
  }
  var lvl1 = [], lvl2 = [];
  for(var i = 0; i < pool.length; i++){
    var l = pool[i];
    if(String(l.mk || '').trim().toLowerCase() !== brand) continue;
    if(!modelMatch(l.mo)) continue;
    var ly = parseInt(l.yr, 10);
    var dy = (!isNaN(year) && !isNaN(ly)) ? Math.abs(year - ly) : 99;
    if(dy <= 2) lvl1.push(l);
    else if(dy <= 5) lvl2.push(l);
  }
  // Niveau 1 prioritaire ; \u00e0 d\u00e9faut niveau 2. Tri prix croissant, 3 max.
  var picked = lvl1.length ? lvl1 : lvl2;
  picked = picked.slice().sort(function(a, b){
    return (parseFloat(a.px) || 0) - (parseFloat(b.px) || 0);
  });
  return picked.slice(0, 3);
}

"""

# ═══════════════════════════════════════════════════════════════════════
# JS-2 — renderBridgeBlock. COLONNE 0, corps 2 espaces.
# ═══════════════════════════════════════════════════════════════════════

RENDER_BRIDGE_FN = """// \u2500\u2500\u2500 Lot 45 \u00b7 rendu du bloc pont \u2500\u2500\u2500
// Renvoie '' si aucun match \u2192 bloc purement additif, z\u00e9ro r\u00e9gression
// sur les fiches sans pont.
function renderBridgeBlock(auction){
  var matches = findMarketBridge(auction);
  if(!matches.length) return '';
  var estLow = parseFloat(auction.estimateLow) || 0;
  var items = matches.map(function(l){
    var px = parseFloat(l.px) || 0;
    var kmTxt = l.km ? (String(l.km).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ' ') + ' km') : '\\u2014';
    // Signal "bon achat" : annonce sous l'estimation basse du lot.
    var deltaTxt = '';
    if(estLow > 0 && px > 0 && px < estLow){
      var pct = Math.round((1 - px / estLow) * 100);
      if(pct >= 1) deltaTxt = '<div class=\"sheet-detail-bridge-item-price-delta\">\\u2212' + pct + '% vs estimation</div>';
    }
    var priceTxt = px > 0 ? esc(fmtPrice(px)) : '\\u2014';
    return '<div class=\"sheet-detail-bridge-item\" data-action=\"openListing\" data-id=\"' + esc(l.id) + '\">'
      + '<div class=\"sheet-detail-bridge-item-main\">'
      + '<div class=\"sheet-detail-bridge-item-model\">' + esc(l.mo || '') + '</div>'
      + '<div class=\"sheet-detail-bridge-item-meta\">' + esc(l.yr || '') + ' \\u00b7 ' + kmTxt
      + (l.src ? ' \\u00b7 ' + esc(l.src) : '') + '</div>'
      + '</div>'
      + '<div class=\"sheet-detail-bridge-item-price\">'
      + '<div class=\"sheet-detail-bridge-item-price-value\">' + priceTxt + '</div>'
      + deltaTxt
      + '</div>'
      + '</div>';
  }).join('');
  // Voix CARNET : factuelle. Si la 1re annonce (la moins ch\u00e8re) bat
  // l'estimation basse, on le dit chiffr\u00e9 ; sinon on situe la cote.
  var voice;
  var cheapest = matches[0];
  var cheapestPx = parseFloat(cheapest.px) || 0;
  if(estLow > 0 && cheapestPx > 0 && cheapestPx < estLow){
    var bestPct = Math.round((1 - cheapestPx / estLow) * 100);
    voice = 'Une \\u00e9quivalente est en vente fixe \\u00e0 ' + esc(fmtPrice(cheapestPx))
      + ' \\u2014 soit \\u2212' + bestPct + '% sous l\\u2019estimation basse de ce lot.';
  } else {
    voice = 'Le m\\u00eame mod\\u00e8le se n\\u00e9gocie aussi hors ench\\u00e8res. De quoi situer la cote.';
  }
  var label = matches.length === 1 ? 'Aussi sur le march\\u00e9' : 'Aussi sur le march\\u00e9 \\u00b7 ' + matches.length + ' annonces';
  return '<div class=\"sheet-detail-bridge\">'
    + '<div class=\"sheet-detail-bridge-label\">' + label + '</div>'
    + items
    + '<div class=\"sheet-detail-bridge-voice\">' + voice + '</div>'
    + '</div>';
}

"""


PATCHES = [
    Patch(
        name="CSS-1 \u00b7 styles .sheet-detail-bridge (fin du groupe .sheet-detail-voice)",
        anchor=CSS_HIGH + CSS_LOW,
        replacement=CSS_HIGH + BRIDGE_CSS + CSS_LOW,
        idempotence_marker=".sheet-detail-bridge {",
    ),
    Patch(
        name="JS-1 \u00b7 findMarketBridge \u2014 matching 3 niveaux (avant renderAuctionSheet)",
        # Borne haute : la FIN de renderMatchSheet, identifiée par le
        # texte UNIQUE et ASCII `dismissMatch" data-id="${esc(m.id)}">`
        # (1 seule occurrence dans le fichier — vérifié). On ne se base
        # PAS sur un `}\n\n` anonyme : ce fragment unique ne peut pas
        # être reproduit par le replacement → garde-fou satisfait,
        # idempotence garantie. Borne basse : `function renderAuctionSheet`.
        anchor='dismissMatch" data-id="${esc(m.id)}">'
               + "\\u00c9carter cette d\\u00e9tection</button>\n    </div>\n  `;\n}\n\nfunction renderAuctionSheet(a){\n  if(!a) return '';",
        replacement='dismissMatch" data-id="${esc(m.id)}">'
               + "\\u00c9carter cette d\\u00e9tection</button>\n    </div>\n  `;\n}\n\n"
               + FIND_BRIDGE_FN + "function renderAuctionSheet(a){\n  if(!a) return '';",
        idempotence_marker="function findMarketBridge",
    ),
    Patch(
        name="JS-2 \u00b7 renderBridgeBlock \u2014 HTML du bloc (apr\u00e8s findMarketBridge)",
        # Borne haute : la fin de findMarketBridge posée par JS-1, dont
        # la dernière ligne `  return picked.slice(0, 3);` est unique au
        # fichier (findMarketBridge est la seule fonction qui finit
        # ainsi). Borne basse : `function renderAuctionSheet`.
        # Le texte `  return picked.slice(0, 3);` n'apparaît PAS dans
        # RENDER_BRIDGE_FN → le replacement ne reproduit pas l'anchor.
        anchor="  return picked.slice(0, 3);\n}\n\nfunction renderAuctionSheet(a){\n  if(!a) return '';",
        replacement="  return picked.slice(0, 3);\n}\n\n" + RENDER_BRIDGE_FN + "function renderAuctionSheet(a){\n  if(!a) return '';",
        idempotence_marker="function renderBridgeBlock",
    ),
    Patch(
        name="JS-3 \u00b7 injection ${renderBridgeBlock(a)} dans renderAuctionSheet",
        # Le bloc voice `CONSEIL CARNET` existe À L'IDENTIQUE dans
        # renderMatchSheet ET renderAuctionSheet → l'anchor doit être
        # étendue pour discriminer. Borne haute : la fin du bloc
        # détail-rows qui précède, dont le fragment `` ` : ''}`` (fin
        # du ternaire ${a.bids}) est UNIQUE à renderAuctionSheet.
        # Indentation réelle : bloc voice à 8 espaces.
        anchor="""          ` : ''}
        </div>
        <div class="sheet-detail-voice">
          <div class="sheet-detail-voice-label">CONSEIL CARNET</div>
          <em>${voiceText}</em>
        </div>
      </div>""",
        replacement="""          ` : ''}
        </div>
        <div class="sheet-detail-voice">
          <div class="sheet-detail-voice-label">CONSEIL CARNET</div>
          <em>${voiceText}</em>
        </div>
        ${renderBridgeBlock(a)}
      </div>""",
        idempotence_marker="renderBridgeBlock(a)",
    ),
]


PATCHSET = PatchSet(
    name="Lot 45 \u2014 Le pont ench\u00e8re \u2192 annonce (findMarketBridge + bloc bridge)",
    requires=[
        "function renderAuctionSheet",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
