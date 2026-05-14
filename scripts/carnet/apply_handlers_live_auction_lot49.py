#!/usr/bin/env python3
"""
CARNET · Lot 49 — Handlers d'enchères : live-data-aware + src_url réel

Source        : audit de la Vue Enchères post-Lot 48. Deux trous
                identifiés, tous deux du même genre — la Vue Enchères
                a été construite AVANT que le live data Supabase
                existe, donc certains handlers parlent encore au seul
                mock AUCTIONS.

  TROU 1 (bloquant) — openAuction / viewSource / toggleWatchAuction
    font `AUCTIONS.find(x => x.id === id)` — le MOCK. Quand le live
    data arrivera, les cartes d'enchères seront rendues depuis
    State.liveAuctions ; l'utilisateur tappera dessus ; ces handlers
    chercheront l'id dans le mock, ne le trouveront pas, et feront
    `return` silencieux. La carte serait CLIQUABLE MAIS MORTE.
    C'est exactement le bug qu'avait openListing — déjà corrigé pour
    les annonces (liveListings puis fallback LISTINGS). Les handlers
    d'enchères ont besoin du MÊME fix.

  TROU 2 — viewSource n'ouvre pas le vrai lien. Il affiche juste un
    toast "Ouverture de ... sur ...". Le src_url (lien réel vers le
    lot chez la maison de vente) EXISTE dans le contrat JSONB, est
    mappé par dbRowToAuction (champ `src_url`) — mais viewSource ne
    l'ouvre jamais. Le bouton "Voir sur RM Sotheby's" ne mène nulle
    part.

  LE FIX — un seul pattern, appliqué aux 3 handlers :
    Remplacer `const a = AUCTIONS.find(...)` par la résolution
    live-first identique à openListing :
        let a = (State.liveAuctions || []).find(x => x.id === id);
        if(!a) a = (typeof AUCTIONS !== 'undefined' ? AUCTIONS : []).find(x => x.id === id);
        if(!a) return;
    Plus, pour viewSource uniquement : si l'objet a un src_url,
    ouvrir ce lien dans un nouvel onglet (window.open avec
    'noopener,noreferrer'). On garde le toast comme retour visuel.
    Si pas de src_url, comportement actuel (toast seul) — pas de
    régression.

  ⚠ INDENTATION RÉELLE (vérifiée à l'octet — Leçon 10) :
    Les handlers de l'objet Actions sont indentés à 2 ESPACES, leur
    corps à 4 ESPACES, l'accolade fermante `},` à 2 ESPACES. (Pas
    4/6/4 comme on pourrait le supposer.) Tous les anchors et
    replacements ci-dessous respectent 2/4/2.

Scope          : 3 patches sur index.html, un par handler.
  JS-1 : openAuction — résolution live-first.
  JS-2 : viewSource — résolution live-first + ouverture src_url.
  JS-3 : toggleWatchAuction — résolution live-first (le reste du
         handler — persist, re-render, toast — est inchangé).

Note sécurité :
  - Anchors 2-bornes, garde-fou v1.1. Chaque anchor prend la
    signature + le corps du handler ; le replacement le réécrit
    entièrement → l'anchor d'origine ne survit pas.
  - window.open avec 'noopener,noreferrer' : hygiène standard liens
    externes. Ouverture sur action utilisateur explicite uniquement
    (clic sur "Voir sur la maison de vente") — rien d'automatique.
  - Aucune régression : State.liveAuctions vide/null → fallback
    AUCTIONS reproduit le comportement actuel. Pas de src_url →
    viewSource garde son toast seul.
  - Idempotence : marqueurs uniques au patch.

Prérequis : aucun (lot autonome — vérifie openAuction)
Usage     :
    python3 apply_handlers_live_auction_lot49.py path/to/index.html
    python3 apply_handlers_live_auction_lot49.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# JS-1 — openAuction. Indentation 2/4/2.
# ═══════════════════════════════════════════════════════════════════════

OPEN_AUCTION_OLD = """  openAuction(id){
    const a = AUCTIONS.find(x => x.id === id);
    if(!a) return;
    Sheet.open('auction', a);
  },"""

OPEN_AUCTION_NEW = """  openAuction(id){
    // Lot 49 : live-first (State.liveAuctions) puis fallback mock,
    // comme openListing \u2014 sans \u00e7a une carte live serait muette.
    let a = (State.liveAuctions || []).find(x => x.id === id);
    if(!a) a = (typeof AUCTIONS !== 'undefined' ? AUCTIONS : []).find(x => x.id === id);
    if(!a) return;
    Sheet.open('auction', a);
  },"""

# ═══════════════════════════════════════════════════════════════════════
# JS-2 — viewSource. Indentation 2/4/2.
# ═══════════════════════════════════════════════════════════════════════

VIEW_SOURCE_OLD = """  viewSource(id){
    const a = AUCTIONS.find(x => x.id === id);
    if(!a) return;
    Sheet.close();
    setTimeout(() => showToastFloat(`Ouverture de \u00ab ${a.brand} ${a.model} \u00bb sur ${a.source}\\u2026`), 340);
  },"""

VIEW_SOURCE_NEW = """  viewSource(id){
    // Lot 49 : live-first puis fallback mock.
    let a = (State.liveAuctions || []).find(x => x.id === id);
    if(!a) a = (typeof AUCTIONS !== 'undefined' ? AUCTIONS : []).find(x => x.id === id);
    if(!a) return;
    Sheet.close();
    // Lot 49 : si l'ench\u00e8re a un src_url r\u00e9el (champ du contrat JSONB),
    // on ouvre le lot chez la maison de vente. Sinon toast seul (mock,
    // ou ench\u00e8re sans lien) \u2014 pas de r\u00e9gression.
    if(a.src_url){
      window.open(a.src_url, '_blank', 'noopener,noreferrer');
    }
    setTimeout(() => showToastFloat(`Ouverture de \u00ab ${a.brand} ${a.model} \u00bb sur ${a.source}\\u2026`), 340);
  },"""

# ═══════════════════════════════════════════════════════════════════════
# JS-3 — toggleWatchAuction. Indentation 2/4/2. Anchor = signature +
# les 3 premières lignes du corps (assez pour être unique, le reste du
# handler reste intact).
# ═══════════════════════════════════════════════════════════════════════

TOGGLE_WATCH_OLD = """  toggleWatchAuction(id){
    const a = AUCTIONS.find(x => x.id === id);
    if(!a) return;
    if(!State.watchedAuctionIds) State.watchedAuctionIds = [];"""

TOGGLE_WATCH_NEW = """  toggleWatchAuction(id){
    // Lot 49 : live-first puis fallback mock.
    let a = (State.liveAuctions || []).find(x => x.id === id);
    if(!a) a = (typeof AUCTIONS !== 'undefined' ? AUCTIONS : []).find(x => x.id === id);
    if(!a) return;
    if(!State.watchedAuctionIds) State.watchedAuctionIds = [];"""


PATCHES = [
    Patch(
        name="JS-1 \u00b7 openAuction \u2014 r\u00e9solution live-first (State.liveAuctions puis mock)",
        anchor=OPEN_AUCTION_OLD,
        replacement=OPEN_AUCTION_NEW,
        idempotence_marker="// Lot 49 : live-first (State.liveAuctions) puis fallback mock,",
    ),
    Patch(
        name="JS-2 \u00b7 viewSource \u2014 live-first + ouverture du src_url r\u00e9el",
        anchor=VIEW_SOURCE_OLD,
        replacement=VIEW_SOURCE_NEW,
        idempotence_marker="if(a.src_url){",
    ),
    Patch(
        name="JS-3 \u00b7 toggleWatchAuction \u2014 r\u00e9solution live-first",
        anchor=TOGGLE_WATCH_OLD,
        replacement=TOGGLE_WATCH_NEW,
        # Marqueur unique au REPLACEMENT : la r\u00e9solution live-first
        # SUIVIE IMM\u00c9DIATEMENT de la ligne watchedAuctionIds \u2014 cette
        # s\u00e9quence n'existe qu'apr\u00e8s patch (avant, c'\u00e9tait
        # `const a = AUCTIONS.find...` qui pr\u00e9c\u00e9dait watchedAuctionIds).
        # Pas dans l'anchor d'origine \u2192 distingue patch\u00e9 / \u00e0 patcher.
        idempotence_marker="if(!a) a = (typeof AUCTIONS !== 'undefined' ? AUCTIONS : []).find(x => x.id === id);\n    if(!a) return;\n    if(!State.watchedAuctionIds) State.watchedAuctionIds = [];",
    ),
]


PATCHSET = PatchSet(
    name="Lot 49 \u2014 Handlers d'ench\u00e8res live-data-aware + src_url r\u00e9el",
    requires=[
        "openAuction(id){",
    ],
    patches=PATCHES,
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
