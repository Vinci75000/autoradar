#!/usr/bin/env python3
"""
CARNET · Lot 23 (Phase α) — Migration archétypes legacy non_driver/social

Source        : index.html utilise encore 2 IDs d'archétype legacy
                (non_driver, social) alors que la source canonique
                carnet-archetypes.js (Discover v1.0) a tranché les 8
                archétypes définitifs. Cette migration aligne index.html.

  Ce N'EST PAS une fusion 2→1, c'est 2 rebrands distincts :

    non_driver → mondain
      Le Mondain (chip DISPLAY) : fan de concours d'élégance, voiture
      statique l'essentiel du temps, roule très peu. Ambiance chic,
      tweed, gentleman. Villa d'Este, Chantilly, Pebble Beach. La
      voiture comme œuvre exposée et passeport social.
      → c'est EXACTEMENT l'ancien non_driver ("Gardien de Musée",
        DISPLAY, acquérir/contempler/protéger). Rebrand direct.

    social → mousquetaire
      Le Mousquetaire (chip RALLYE) : rallyes caritatifs, historiques,
      Gumball, courses de côte, courses d'orientation. Plus extrême
      dans l'ADN. "Un pour tous, tous pour un" — devise vécue.
      → c'est l'ancien social ("Le Social", RALLYE, Gumballers,
        voyager/socialiser), recadré dans l'ADN Discover v1.0.

Scope         : 7 patches sur index.html
  - JS-1 : COLLECTOR_PROFILES — entrée non_driver → mondain
  - JS-2 : COLLECTOR_PROFILES — entrée social → mousquetaire
  - JS-3 : PROFILE_ADVICE — bloc 'non_driver' → 'mondain'
  - JS-4 : PROFILE_ADVICE — bloc 'social' → 'mousquetaire'
  - JS-5 : inferCarArchetypes — set.add('non_driver') ×2 → 'mondain'
  - JS-6 : inferCarArchetypes — set.add('social') → 'mousquetaire'
           + commentaire de doc des IDs mis à jour
  - JS-7 : migration localStorage — au chargement de State.userProfiles,
           remap non_driver→mondain, social→mousquetaire, dédup. Un
           utilisateur existant avec un profil legacy sauvegardé ne se
           retrouve pas avec un ID mort.

Alignement contenu : labels, chips, teasers et conseils sont alignés
  sur carnet-archetypes.js (source canonique). Le FORMAT reste celui
  d'index.html : COLLECTOR_PROFILES = {id, label, chip, teaser, text}
  (carnet-archetypes.js utilise {id, label, chip, verb, teaser, long} —
  format différent, on ne le copie pas, on aligne le sens).

Note sécurité :
  - Toutes les anchors sont 2-bornes (Leçon 1 du PATCH_GUIDE).
  - JS-5 : les 2 set.add('non_driver') sont dans des if différents avec
    des conditions distinctes → anchors 2-lignes incluant la condition,
    markers uniques (Leçon 3).
  - La migration localStorage (JS-7) s'insère dans le bloc de chargement
    existant (persistedProfiles) — idempotente : remapper un ID déjà
    canonical est un no-op.
  - inferCarArchetypes retourne un Set → si un car matchait non_driver
    ET (hypothétiquement) déjà mondain, le Set dédoublonne. Sûr.

Hors scope :
  - carnet-archetypes.js, discover.html, archetypes.html — déjà
    canonical (Discover v1.0), non touchés
  - Les autres archétypes (collector/flipper/track_rat/builder/
    enthusiast/driver) — IDs déjà alignés, non touchés

Prérequis : Lot 22 (Phase α) appliqué

⚠️ NOTE POST-LOT 24 : les patches JS-5a / JS-5b / JS-6a de ce lot
   patchaient `set.add('non_driver'|'social')` dans inferCarArchetypes.
   Le Lot 24 a entièrement réécrit le corps de inferCarArchetypes — ces
   3 anchors n'existent donc plus sur un fichier déjà au Lot 24, et le
   script affichera "ANCHOR NOT FOUND" pour eux si ré-exécuté seul après
   le Lot 24. C'est ATTENDU, pas un bug : les lots sont une séquence
   ordonnée. Un from-scratch dans l'ordre (23 puis 24) fonctionne
   parfaitement. JS-5a/5b/6a restent dans ce script pour que le
   from-scratch reste reproductible.

Usage     :
    python3 apply_archetype_migration_lot23.py path/to/index.html
    python3 apply_archetype_migration_lot23.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — COLLECTOR_PROFILES : non_driver → mondain
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : l'entrée driver (borne haute) + l'entrée non_driver.
# Le replacement garde driver, remplace non_driver par mondain.

JS1_ANCHOR = """  { id: 'driver',     label: 'Le Gros Rouleur',          chip: 'ROUTE',      teaser: \"Conduire. Vraiment. Les kilom\\u00e8tres sont une m\\u00e9daille.\",                  text: \"Conduire. Vraiment. Les kilom\\u00e8tres sont une m\\u00e9daille.\" },
  { id: 'non_driver', label: 'Le Gardien de Mus\\u00e9e', chip: 'DISPLAY',    teaser: \"Acqu\\u00e9rir, contempler, prot\\u00e9ger. Garage ou salon.\",                       text: \"Acqu\\u00e9rir, contempler, prot\\u00e9ger, que ce soit dans son garage ou son salon.\" },"""

JS1_REPLACEMENT = """  { id: 'driver',     label: 'Le Gros Rouleur',          chip: 'ROUTE',      teaser: \"Conduire. Vraiment. Les kilom\\u00e8tres sont une m\\u00e9daille.\",                  text: \"Conduire. Vraiment. Les kilom\\u00e8tres sont une m\\u00e9daille.\" },
  { id: 'mondain',    label: 'Le Mondain',               chip: 'DISPLAY',    teaser: \"Villa d\\u2019Este, Chantilly. Exposer ce qui se contemple.\",                       text: \"Sortir la voiture pour qu\\u2019elle soit vue dans son meilleur cadre. Concours d\\u2019\\u00e9l\\u00e9gance, pelouses anglaises, tweed, gentleman. Elle roule peu \\u2014 elle se contemple. La voiture comme \\u0153uvre dont on est le commissaire d\\u2019exposition.\" },"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — COLLECTOR_PROFILES : social → mousquetaire
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : l'entrée social + la fermeture du tableau "];".

JS2_ANCHOR = """  { id: 'social',     label: 'Le Social',               chip: 'RALLYE',     teaser: \"Gumballers et autres aficionados de rallies. Voyager, socialiser.\",                text: \"Gumballers et autres aficionados de rallies. Voyager, socialiser, \\u2026 bien manger, pas toujours.\" }
];"""

JS2_REPLACEMENT = """  { id: 'mousquetaire', label: 'Le Mousquetaire',        chip: 'RALLYE',     teaser: \"Un pour tous, tous pour un. Pousser pour servir.\",                                text: \"Rouler en bande, jamais seul. Rallyes caritatifs, historiques, Gumball, courses de c\\u00f4te, courses d\\u2019orientation. L\\u2019itin\\u00e9raire compte autant que la voiture. Plus extr\\u00eame dans l\\u2019ADN \\u2014 et au bout de la route, souvent une \\u0153uvre \\u00e0 servir.\" }
];"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — PROFILE_ADVICE : blocs 'non_driver' + 'social' → 'mondain' + 'mousquetaire'
# ═══════════════════════════════════════════════════════════════════════
# Les 2 blocs sont ADJACENTS dans PROFILE_ADVICE. Un seul patch couvre
# les deux d'un tenant — pas de chevauchement d'anchor possible.
# Anchor 2-bornes : le bloc non_driver+social complet + la fermeture "};".
# Note : le bloc 'social' a déjà label 'Mondain' (héritage confus) — on
# le recadre proprement en 'mousquetaire' / label 'Mousquetaire'.

JS3_ANCHOR = """  'non_driver': {
    label: 'Gardien',
    'new': "Stockage qualitatif dès maintenant : climat, lumière, mouvement périodique. C'est ce qui distingue dans 20 ans.",
    'mature': "Phase d'attente assumée. La voiture dort, tu protèges. Patience récompensée à long terme.",
    'bottom': "Tu y es presque. 5-10 ans de plus avant la remontée. Garde la conservation impeccable.",
    'collector_entry': "Ton travail commence à payer. L'auto conservée à 0 km vaut significativement plus que celle qui a roulé. Continue.",
    'vintage': "Valorisation maximale. Une voiture conservée comme musée vaut le double d'un exemplaire qui a vécu.",
    'oldtimer': "Pièce de musée. Tu as fait ce qu'il fallait. Le marché viendra à toi."
  },
  'social': {
    label: 'Mondain',
    'new': "Sors-la, montre-la. Les belles photos et la présence en rallye créent une histoire — qui devient un argument de vente plus tard.",
    'mature': "Phase visible. Concours d'élégance, sortie en clubs, presse spécialisée. Construis sa notoriété.",
    'bottom': "Tes apparitions valorisent la voiture au-delà de la moyenne du marché. Tiens le rythme.",
    'collector_entry': "L'auto a une réputation maintenant. Les acheteurs cherchent les exemplaires connus. Photographe pro, dossier complet.",
    'vintage': "Pedigree d'événements = pedigree de marché. Un Pebble Beach, un Villa d'Este, ça vaut +20% facile.",
    'oldtimer': "Voiture historique. Sa carrière publique devient son CV. Plus elle a brillé, plus elle vaut."
  }
};"""

JS3_REPLACEMENT = """  'mondain': {
    label: 'Mondain',
    'new': "Stockage qualitatif dès maintenant : climat, lumière, mouvement périodique. C'est ce qui distingue sur une pelouse de concours dans 20 ans.",
    'mature': "Phase d'exposition assumée. La voiture se montre, tu la prépares. Chaque sortie est un événement soigné.",
    'bottom': "Tu y es presque. 5-10 ans de plus avant la remontée. Garde la présentation impeccable, le pedigree d'événements se construit.",
    'collector_entry': "Ton travail commence à payer. L'auto conservée à 0 km, au pedigree d'expositions, vaut significativement plus. Continue.",
    'vintage': "Valorisation maximale. Une voiture conservée comme œuvre, montrée dans les bons cadres, vaut le double d'un exemplaire qui a vécu sans être vu.",
    'oldtimer': "Pièce de musée. Villa d'Este, Chantilly, Pebble Beach — sa carrière d'expositions est son CV. Le marché viendra à toi."
  },
  'mousquetaire': {
    label: 'Mousquetaire',
    'new': "Sors-la, engage-la. Les rallyes caritatifs et historiques dès maintenant créent une histoire — kilomètres vécus, causes servies, qui deviennent un argument plus tard.",
    'mature': "Phase d'engagement. Mille Miglia, Tour Auto, Gumball, courses de côte — l'itinéraire fait la légende. Roule en bande, sers.",
    'bottom': "Tes rallyes valorisent la voiture au-delà de la moyenne du marché : une auto qui a vécu en convoi, fiable, préparée. Tiens le rythme.",
    'collector_entry': "L'auto a un pedigree d'épreuves maintenant. Les acheteurs cherchent les exemplaires qui ont roulé fort et bien. Dossier complet, photos de route.",
    'vintage': "Pedigree de rallyes = pedigree de marché. Une Mille Miglia, un Tour Auto, une cause servie — ça vaut +20% et ça se raconte.",
    'oldtimer': "Voiture historique. Sa carrière d'épreuves devient son CV. Plus elle a servi et brillé en convoi, plus elle vaut."
  }
};"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 5 — inferCarArchetypes : set.add('non_driver') ×2 → 'mondain'
# ═══════════════════════════════════════════════════════════════════════
# 2 occurrences dans 2 if distincts. Anchors 2-lignes incluant la
# condition pour unicité (Leçon 3).

# 5a — premier set.add('non_driver') : condition cote/km
JS5A_ANCHOR = """  if(cote >= 500000 && km < 10000){
    set.add('non_driver');
  }"""

JS5A_REPLACEMENT = """  if(cote >= 500000 && km < 10000){
    set.add('mondain');
  }"""

# 5b — second set.add('non_driver') : condition regex hypercars
JS5B_ANCHOR = """  if(/zonda|huayra|veyron|chiron|valkyrie|laferrari|918 spyder|p1|senna|jesko|tuatara|jewel|battista|nevera|evija|t.50|aventador svj|sf90|monza sp/i.test(fullName)){
    set.add('non_driver');
  }"""

JS5B_REPLACEMENT = """  if(/zonda|huayra|veyron|chiron|valkyrie|laferrari|918 spyder|p1|senna|jesko|tuatara|jewel|battista|nevera|evija|t.50|aventador svj|sf90|monza sp/i.test(fullName)){
    set.add('mondain');
  }"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 6 — inferCarArchetypes : set.add('social') → 'mousquetaire'
#           + commentaire de doc des IDs mis à jour
# ═══════════════════════════════════════════════════════════════════════

JS6A_ANCHOR = """  // Social / Rallye — supercars exotiques connues des Gumball
  if(/aventador|huracan|sf90|\\b296\\b|\\b812\\b|720s|gt-r|\\bgtr\\b|amg gt|\\bm8\\b|\\brs6\\b|\\brs7\\b|gallardo|murcielago|diablo|countach|defender|g.?wagon|g 63|g63|urus/i.test(fullName)){
    set.add('social');
  }"""

JS6A_REPLACEMENT = """  // Mousquetaire / Rallye — supercars exotiques connues des Gumball et rallyes
  if(/aventador|huracan|sf90|\\b296\\b|\\b812\\b|720s|gt-r|\\bgtr\\b|amg gt|\\bm8\\b|\\brs6\\b|\\brs7\\b|gallardo|murcielago|diablo|countach|defender|g.?wagon|g 63|g63|urus/i.test(fullName)){
    set.add('mousquetaire');
  }"""

# 6b — le commentaire de doc des IDs (Lot 14)
JS6B_ANCHOR = """// IDs cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
// builder, enthusiast, driver, non_driver, social."""

JS6B_REPLACEMENT = """// IDs cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
// builder, enthusiast, driver, mondain, mousquetaire.
// (Lot 23 — non_driver→mondain, social→mousquetaire : alignement Discover v1.0)"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 7 — migration localStorage au chargement de State.userProfiles
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : la ligne de chargement persistedProfiles + sa
# voisine. Insertion du remap juste après l'affectation.

JS7_ANCHOR = """  if(persistedProfiles !== null) State.userProfiles = persistedProfiles;
  // Migration v5 : s'assurer que toute voiture a services/photos/docs initialisés"""

JS7_REPLACEMENT = """  if(persistedProfiles !== null) State.userProfiles = persistedProfiles;
  // Lot 23 — migration IDs legacy : non_driver→mondain, social→mousquetaire.
  // Un profil sauvegardé avant le Lot 23 est remappé au chargement (idempotent).
  if(Array.isArray(State.userProfiles) && State.userProfiles.length){
    const _archetypeRemap = { non_driver: 'mondain', social: 'mousquetaire' };
    State.userProfiles = [...new Set(State.userProfiles.map(id => _archetypeRemap[id] || id))];
  }
  // Migration v5 : s'assurer que toute voiture a services/photos/docs initialisés"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 23 (Phase α) — Migration archétypes legacy non_driver/social",
    requires=[
        # Marker réel présent dans le fichier (Leçon 5).
        "Lot 22 — .tick : glyphe ✓ canonique",
    ],
    patches=[
        Patch(
            name="JS-1 · COLLECTOR_PROFILES — non_driver → mondain",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker="{ id: 'mondain',    label: 'Le Mondain',",
        ),
        Patch(
            name="JS-2 · COLLECTOR_PROFILES — social → mousquetaire",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker="{ id: 'mousquetaire', label: 'Le Mousquetaire',",
        ),
        Patch(
            name="JS-3 · PROFILE_ADVICE — blocs non_driver+social → mondain+mousquetaire",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker="  'mondain': {\n    label: 'Mondain',",
        ),
        Patch(
            name="JS-5a · inferCarArchetypes — set.add('non_driver') #1 (cote/km) → mondain",
            anchor=JS5A_ANCHOR,
            replacement=JS5A_REPLACEMENT,
            idempotence_marker="if(cote >= 500000 && km < 10000){\n    set.add('mondain');",
        ),
        Patch(
            name="JS-5b · inferCarArchetypes — set.add('non_driver') #2 (hypercars) → mondain",
            anchor=JS5B_ANCHOR,
            replacement=JS5B_REPLACEMENT,
            idempotence_marker="monza sp/i.test(fullName)){\n    set.add('mondain');",
        ),
        Patch(
            name="JS-6a · inferCarArchetypes — set.add('social') → mousquetaire",
            anchor=JS6A_ANCHOR,
            replacement=JS6A_REPLACEMENT,
            idempotence_marker="// Mousquetaire / Rallye — supercars exotiques",
        ),
        Patch(
            name="JS-6b · inferCarArchetypes — commentaire doc des IDs mis à jour",
            anchor=JS6B_ANCHOR,
            replacement=JS6B_REPLACEMENT,
            idempotence_marker="// (Lot 23 — non_driver→mondain, social→mousquetaire",
        ),
        Patch(
            name="JS-7 · migration localStorage State.userProfiles au chargement",
            anchor=JS7_ANCHOR,
            replacement=JS7_REPLACEMENT,
            idempotence_marker="// Lot 23 — migration IDs legacy : non_driver→mondain",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
