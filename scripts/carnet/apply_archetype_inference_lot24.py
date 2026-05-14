#!/usr/bin/env python3
"""
CARNET · Lot 24 (Phase α) — Refonte inferCarArchetypes : faisceau large

Source        : suite du Lot 23. Après le rebrand non_driver→mondain /
                social→mousquetaire, la LOGIQUE d'inférence ne collait
                plus au vrai ADN des 2 avatars :
                  - mondain inférait des hypercars (zonda/veyron) — or
                    une hypercar n'est pas "concours d'élégance" par
                    nature ; et ces modèles étaient AUSSI dans la regex
                    mousquetaire → double faux positif.
                  - mousquetaire inférait des SUV (defender/g-wagon/urus)
                    — rien à voir avec rallye historique / course de côte.

                Décision produit (Sly) : adapter la philosophie à TOUS
                les avatars, pas seulement aux 2 migrés.

Philosophie    : "filtre large mais efficace — une petite aide
                intelligente, pas un mur".
  - Faisceau d'indices : chaque avatar = plusieurs `if` indépendants,
    un seul signal DISPONIBLE suffit. Pas de `&&` bloquant (sauf couple
    cote+km pour mondain, qui a du sens ensemble).
  - Multi-match ASSUMÉ : une voiture a plusieurs interprétations d'usage
    légitimes. inferCarArchetypes renvoie un Set — une F40 est à la fois
    collector, enthusiast, mondain, mousquetaire. C'est voulu, c'est la
    magie du système ("un humain peut en être plusieurs").
  - Jamais restrictif : on préfère un faux positif léger à un avatar
    qui ne matche jamais. Le filtre AIDE, il n'EXCLUT pas.

Signaux réellement disponibles (vérifiés sur les objets car/GARAGE) :
  brand, model, year, km, cote, trend, chassis, spec, tuner, fresh.
  /!\\ fullServiceHistory & serviceUpToDate N'EXISTENT PAS sur les objets
  GARAGE (initialisés ailleurs, migration v5) — NE PAS s'appuyer dessus.
  Le champ `spec` est le vrai or : texte libre riche ("matching numbers",
  "historique complet", "220 ex.", "première main", "Restauration…").

Mapping critères Sly → signaux :

  MONDAIN (matching numbers · entretien constructeur full · <5000 ex.)
    - car.chassis présent           → numéro de châssis documenté
    - /matching|numbers matching/   dans spec
    - /historique complet|carnet complet|full service|première main|
       restauration|concours/       dans spec
    - regex modèles rares <5000 ex. (F40, Carrera GT, Miura, 959,
       Stratos, 288 GTO, CSL, RS, Gullwing…)
    - /\\(\\d{1,4} ?ex/              "(220 ex.)" — édition limitée chiffrée
    - couple cote≥300k & km<30000   chère + peu roulée = exposable

  MOUSQUETAIRE (marque prestigieuse OU modèle iconique · caractère ·
                +250cv · capable de longs trajets · style)
    - brand ∈ marques prestigieuses (liste large, toutes époques)
    - regex modèles iconiques/exception
    - car.tuner présent             → préparée = caractère assumé
    - /gt|rs\\b|turbo|amg|quattro|integrale|cup/  signature sportive
    Volontairement TRÈS large : "le Gumball en Rolls ou en SVJ, la
    course de côte en 911" — toute prestigieuse est candidate.

  Les 6 autres avatars — élargis dans le même esprit :
    track_rat   + marques/signaux circuit + tuner
    builder     + car.tuner présent (signal direct, manquait !)
    driver      + seuil km abaissé 80k + GT/grand tourisme
    collector   + chassis + spec "historique" (au-delà de year/cote)
    enthusiast  + spec spécifications + chassis
    flipper     + car.fresh (annonce récente) au-delà de trend

Scope          : 3 patches sur index.html
  - JS-1 : corps de inferCarArchetypes — les 8 blocs refondus d'un tenant
           (du commentaire "Track Rat" au "return Array.from(set)")
  - JS-2 : commentaire de doc des IDs — déjà à jour côté IDs (Lot 23),
           on ajoute une ligne sur la philosophie faisceau
  - JS-3 : banner onboarding — "le pilote, le bâtisseur, le gardien"
           → "le pilote, le bâtisseur, le mondain" (le gardien n'est
           plus un archétype). Le badge donation "gardien" n'est PAS
           touché — c'est un objet distinct.

Note sécurité :
  - JS-1 : anchor 2-bornes (commentaire "Track Rat" en borne haute,
    "return Array.from(set);\\n}" en borne basse). Tout le corps entre
    les deux est remplacé d'un bloc — pas de chevauchement interne
    possible (Leçon de l'incident JS-3/JS-4 du Lot 23).
  - Aucun nouveau champ inventé : seuls brand/model/year/km/cote/trend/
    chassis/spec/tuner/fresh sont lus, tous vérifiés présents.
  - regex en raw strings là où nécessaire ; pas d'escape Unicode ici.
  - Idempotent : le marker (commentaire "Lot 24 — faisceau large")
    n'apparaît qu'après application.

Hors scope :
  - carnet-archetypes.js / discover.html — déjà canonical, non touchés
  - badge donation "gardien" (State.userBadges) — objet distinct,
    aucun rapport avec l'archétype, non touché
  - COLLECTOR_PROFILES / PROFILE_ADVICE — déjà migrés au Lot 23

Prérequis : Lot 23 (Phase α) appliqué
Usage     :
    python3 apply_archetype_inference_lot24.py path/to/index.html
    python3 apply_archetype_inference_lot24.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — corps de inferCarArchetypes : les 8 blocs refondus
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : du commentaire "Track Rat" jusqu'à "return Array...".

JS1_ANCHOR = """  // Track Rat — voitures circuit
  if(/\\bgt3\\b|\\bgt2\\b|\\bcup\\b|trophy|\\brs\\b|sport evo|black series|caterham|lotus|bac mono|ktm x-bow|radical|porsche r\\b|\\b911 r\\b|cayman gt4|m4 csl/i.test(fullName)){
    set.add('track_rat');
  }

  // Builder / Outlaw — préparateurs et restomods
  if(/singer|brabus|mansory|\\bruf\\b|alpina|liberty walk|restomod|tuner|wide ?body|hennessey|gunther werks|tuthill/i.test(fullName)){
    set.add('builder');
  }

  // Driver / Gros rouleur — kilométrage élevé, breaks, berlines GT
  if(km > 100000){
    set.add('driver');
  }
  if(/\\bs-class\\b|7 ?series|panamera|continental|ghost|phantom|maybach|\\bcls\\b|break|estate|wagon|touring|avant|sportwagon|shooting brake/i.test(fullName)){
    set.add('driver');
  }

  // Non-Driver / Gardien — hypercars + low km, ou cote très élevée + low km
  if(cote >= 500000 && km < 10000){
    set.add('mondain');
  }
  if(/zonda|huayra|veyron|chiron|valkyrie|laferrari|918 spyder|p1|senna|jesko|tuatara|jewel|battista|nevera|evija|t.50|aventador svj|sf90|monza sp/i.test(fullName)){
    set.add('mondain');
  }

  // Collector — classics et valeurs de référence
  if(year && year < 1990){
    set.add('collector');
  }
  if(cote >= 200000){
    set.add('collector');
  }

  // Enthusiast — séries limitées, spécifications particulières
  if(/limited|special|anniversary|jubilee|carrera gt|enzo|\\bf50\\b|\\bf40\\b|carrera rs|stradale|aperta|spyder|targa florio|speedster|gma|chassis|matching/i.test(fullName)){
    set.add('enthusiast');
  }

  // Flipper — opportunité de revente (trend up)
  if(car.trend === 'up'){
    set.add('flipper');
  }

  // Mousquetaire / Rallye — supercars exotiques connues des Gumball et rallyes
  if(/aventador|huracan|sf90|\\b296\\b|\\b812\\b|720s|gt-r|\\bgtr\\b|amg gt|\\bm8\\b|\\brs6\\b|\\brs7\\b|gallardo|murcielago|diablo|countach|defender|g.?wagon|g 63|g63|urus/i.test(fullName)){
    set.add('mousquetaire');
  }

  return Array.from(set);
}"""

JS1_REPLACEMENT = """  // ─────────────────────────────────────────────────────────────
  // Lot 24 — faisceau large : chaque avatar = plusieurs signaux
  // indépendants, un seul suffit. Multi-match assumé (une voiture a
  // plusieurs usages possibles). Le filtre AIDE, il n'EXCLUT pas.
  // Champs lus : brand/model/year/km/cote/trend/chassis/spec/tuner/fresh.
  // ─────────────────────────────────────────────────────────────
  const spec = (car.spec || '').toLowerCase();
  const hasChassis = !!(car.chassis && String(car.chassis).trim());
  const hasTuner = !!(car.tuner && String(car.tuner).trim());

  // Track Rat — voiture pensée pour le circuit
  if(/\\bgt3\\b|\\bgt2\\b|\\bgt4\\b|\\bcup\\b|trophy|\\brs\\b|sport evo|black series|caterham|\\blotus\\b|bac mono|ktm x-bow|radical|\\b911 r\\b|cayman gt4|m4 csl|clubsport|track ?pack|nürburgring|nurburgring|scuderia|pista|speciale|competizione/i.test(fullName)){
    set.add('track_rat');
  }
  if(/circuit|piste|track|chrono|cage|harnais/i.test(spec)){
    set.add('track_rat');
  }

  // Builder / Outlaw — préparée, restomod, signature de préparateur
  if(/singer|brabus|mansory|\\bruf\\b|alpina|liberty walk|restomod|wide ?body|hennessey|gunther werks|tuthill|emory|kaege|theon|tuthill|outlaw|backdate/i.test(fullName)){
    set.add('builder');
  }
  if(hasTuner){
    set.add('builder');
  }
  if(/préparation|restomod|outlaw|backdate|swap|upgrade/i.test(spec)){
    set.add('builder');
  }

  // Driver / Gros rouleur — kilomètres au compteur, grand tourisme
  if(km > 80000){
    set.add('driver');
  }
  if(/\\bs-class\\b|7 ?series|panamera|continental|ghost|phantom|maybach|\\bcls\\b|break|estate|wagon|touring|avant|sportwagon|shooting brake|grand tourer|\\bgt\\b|quattroporte/i.test(fullName)){
    set.add('driver');
  }

  // Mondain — exposer ce qui se contemple : matching numbers,
  // entretien constructeur, production confidentielle (<5000 ex.)
  if(hasChassis){
    set.add('mondain');
  }
  if(/matching|numbers matching|historique complet|carnet complet|full service|première main|premiere main|restauration|concours|original|provenance|certificat/i.test(spec)){
    set.add('mondain');
  }
  if(/\\(\\s?\\d{1,4}\\s?ex/i.test(spec)){
    set.add('mondain');
  }
  if(/\\bf40\\b|\\bf50\\b|carrera gt|enzo|\\b288 gto\\b|miura|\\b959\\b|stratos|\\bcsl\\b|gullwing|\\b250 gt\\b|\\bgto\\b|delta integrale|\\bgt2 rs\\b|\\bgt3 rs\\b|sport evo|\\b911 r\\b|carrera rs|\\bsl roadster\\b|type 35|\\bdb4\\b|\\bdb5\\b/i.test(fullName)){
    set.add('mondain');
  }
  if(cote >= 300000 && km < 30000){
    set.add('mondain');
  }

  // Collector — classics, valeurs de référence, provenance documentée
  if(year && year < 1995){
    set.add('collector');
  }
  if(cote >= 180000){
    set.add('collector');
  }
  if(hasChassis || /historique|provenance|matching|original|certificat|carnet complet/i.test(spec)){
    set.add('collector');
  }

  // Enthusiast — séries spéciales, spécifications particulières
  if(/limited|special|anniversary|jubilee|carrera gt|enzo|\\bf50\\b|\\bf40\\b|carrera rs|stradale|aperta|spyder|targa florio|speedster|\\bgma\\b|matching|\\bcsl\\b|\\brs\\b|edition|série limitée|serie limitee/i.test(fullName + ' ' + spec)){
    set.add('enthusiast');
  }
  if(hasChassis){
    set.add('enthusiast');
  }

  // Flipper — opportunité de revente : tendance, fraîcheur d'annonce
  if(car.trend === 'up'){
    set.add('flipper');
  }
  if(car.fresh){
    set.add('flipper');
  }

  // Mousquetaire — rouler, en bande, n'importe où : marque prestigieuse
  // OU modèle iconique/d'exception, du caractère, capable de longs
  // trajets. Volontairement large — le Gumball en Rolls ou en SVJ.
  if(/ferrari|porsche|lamborghini|aston martin|maserati|mclaren|bentley|rolls.?royce|alpine|\\blotus\\b|jaguar|alfa romeo|bugatti|pagani|koenigsegg|amg|abarth|\\btvr\\b|de tomaso|lancia|shelby/i.test(brand)){
    set.add('mousquetaire');
  }
  if(/\\bgt\\b|\\brs\\b|turbo|quattro|integrale|\\bcup\\b|stradale|veloce|\\bgti\\b|cooper s|\\bsvj?\\b|countach|miura|stratos|\\b911\\b|\\bm3\\b|\\bm5\\b|\\be-type\\b/i.test(fullName)){
    set.add('mousquetaire');
  }
  if(hasTuner){
    set.add('mousquetaire');
  }

  return Array.from(set);
}"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — commentaire de doc des IDs : ajoute la note "faisceau large"
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = """// IDs cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
// builder, enthusiast, driver, mondain, mousquetaire.
// (Lot 23 — non_driver→mondain, social→mousquetaire : alignement Discover v1.0)
function inferCarArchetypes(car){"""

JS2_REPLACEMENT = """// IDs cohérents avec COLLECTOR_PROFILES : collector, flipper, track_rat,
// builder, enthusiast, driver, mondain, mousquetaire.
// (Lot 23 — non_driver→mondain, social→mousquetaire : alignement Discover v1.0)
// (Lot 24 — inférence en faisceau large : multi-match assumé, le filtre
//  aide sans exclure. Une voiture a plusieurs usages possibles.)
function inferCarArchetypes(car){"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — banner onboarding : "le gardien" → "le mondain"
# ═══════════════════════════════════════════════════════════════════════
# "le gardien" n'est plus un archétype (c'est "le mondain"). À ne pas
# confondre avec le badge donation "gardien" (objet distinct, non touché).

JS3_ANCHOR = """      <p class="banner-text">CARNET adapte ses conseils \\u00e0 ta fa\\u00e7on de vivre ta passion. Le pilote, le b\\u00e2tisseur, le gardien \\u2014 ils ne re\\u00e7oivent pas les m\\u00eames suggestions.</p>"""

JS3_REPLACEMENT = """      <p class="banner-text">CARNET adapte ses conseils \\u00e0 ta fa\\u00e7on de vivre ta passion. Le pilote, le b\\u00e2tisseur, le mondain \\u2014 ils ne re\\u00e7oivent pas les m\\u00eames suggestions.</p>"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 24 (Phase α) — Refonte inferCarArchetypes : faisceau large",
    requires=[
        # Marker réel présent dans le fichier après le Lot 23.
        "// (Lot 23 — non_driver→mondain, social→mousquetaire",
    ],
    patches=[
        Patch(
            name="JS-1 · inferCarArchetypes — 8 blocs refondus, faisceau large",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker="Lot 24 — faisceau large : chaque avatar",
        ),
        Patch(
            name="JS-2 · commentaire doc — note philosophie faisceau",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker="(Lot 24 — inférence en faisceau large",
        ),
        Patch(
            name="JS-3 · banner onboarding — 'le gardien' → 'le mondain'",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker="Le pilote, le b\\u00e2tisseur, le mondain",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
