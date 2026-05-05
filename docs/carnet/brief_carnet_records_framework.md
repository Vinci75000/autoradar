# Brief Carnet — Records Framework (frontend pass)

**Mission : intégrer le système narratif des Quatre Records dans l'app Carnet, de façon additive et non-invasive, sur `index.html` uniquement. Le système doit gérer élégamment les 200+ voitures déjà en base (donnée souvent rare) et chaque nouvelle entrée — qu'elle vienne du scraper tiers ou d'une publication utilisateur via la modale "Publier annonce".**

---

## A. Contexte

### A.1 Où on en est

- Frontend repo : `Vinci75000/autoradar` — fichier unique `index.html` (~4800 lignes, 267 ko).
- App live : connectée à Supabase, 200 voitures servies via `.from('cars').select(...).eq('status','active').limit(200)`.
- Branding : pass 1 visuel Carnet déjà mergée sur main (palette v8, fonts, wordmark). Pass 2 (icônes PWA) effectuée.
- Score actuel : /100 sur 5 sous-axes (`px` Prix marché 25, `me` Mécanique 30, `hi` Historique 20, `an` Qualité annonce 15, `km` Kilométrage 10).
- Wizard "Publier annonce" : 5 étapes (Véhicule / Photos / Formule / Contact / Récap).

### A.2 Ce qu'on apporte ici

Le **Records Framework** est l'angle narratif décidé en session marque : chaque voiture est lue à travers quatre carnets distincts — Service, Auction, Provenance, Collection. C'est l'extension anglaise (*Curated Automotive Records Network*) du nom français *Carnet*. La traduction n'est pas littérale, elle est conceptuelle : *records* = *carnet d'entretien* = la trace écrite. La marque garde son ADN éditorial dans les deux langues.

Ce brief n'invente rien côté donnée. Il **réinterprète l'existant** (les 5 sous-axes de score, les champs DB) à travers la grille Records, et expose cette grille dans l'UI. Pas de migration SQL. Pas de touche au scraper. Pas de touche aux modules `feature_extractor.py` / `dedup.py` / `validation.py`.

### A.3 Pourquoi maintenant

- La marque Carnet est née (charte v8 stable).
- L'extension anglaise est figée (*Curated Automotive Records Network*).
- Les utilisateurs voient un score opaque (`82/100`) sans comprendre *où*. Les Records décomposent.
- Le wizard "Publier annonce" est sous-exploité : on collecte le minimum, on rate la matière narrative qui ferait la différence pour les voitures premium.
- La page manifeste / about n'existe pas. Le visiteur n'a pas de surface où comprendre la philosophie.

### A.4 Dépendances amont

Aucune. Ce pass est autonome. Il n'attend ni Mission B-bis, ni ECR Phase 3, ni Auction View Phase 2. Au contraire, il **prépare le terrain** : quand B-bis livrera la colonne `de` peuplée, le Service Record et le Collection Record s'enrichiront automatiquement via la fonction `deriveRecords()`. Quand Phase 3 ECR arrivera, le Provenance Record absorbera le matched flag. Quand Phase 2 Auction View landera, le Auction Record passera de "souvent vide" à "souvent rempli".

---

## B. Scope & architecture

### B.1 Fichiers touchés

**Modifié :**
- `index.html` (le seul fichier de prod)

**Inchangés (interdits de modification dans cette session) :**
- Tout dans `~/Code/autoradar/scraper/` (scraper, validation, dedup, feature_extractor, make_normalizer, batch_runner)
- Schéma Supabase (aucune migration SQL)
- `manifest.json`, `sw.js`, icônes PWA
- Backend / API / RLS

### B.2 Approche additive

Le pass est **non-invasif**. On n'extrait pas le CSS / JS / HTML hors du fichier unique (Sergio a délibérément choisi le single-file). On n'élague pas l'existant : on ajoute des sections, on remplace certains contenus à la marge, on garde le squelette.

Trois zones d'intervention dans `index.html` :

1. **Modale Manifeste** (nouvelle) — accessible depuis le footer / header.
2. **Bloc Records dans la card de fiche voiture** (nouveau) — rendu via JS, lit la donnée existante et dérive les 4 Records.
3. **Wizard "Publier annonce" étendu** (modifié) — passage de 5 à 7 étapes pour collecter les Records côté user-submitted.

Plus deux passes transverses :

4. **Vocabulaire / voix** — substitution ciblée de termes (table en section E.5).
5. **Hero / homepage** — copywriting refait dans la voix Carnet + Records.

### B.3 Ce qu'on ne fait PAS dans ce pass

- ❌ Pas de refonte de la card de listing (le visuel actuel reste).
- ❌ Pas de modification du flux Supabase fetch.
- ❌ Pas de changement du tri / filtres existants.
- ❌ Pas de migration des sous-axes de score (`px`, `me`, `hi`, `an`, `km` restent en DB).
- ❌ Pas de localisation EN globale (l'app reste en français, le manifeste a une signature anglaise).
- ❌ Pas d'auth / login / signup.
- ❌ Pas d'extraction de fichiers séparés.

---

## C. Specs fonctionnelles

### C.1 Le système des Quatre Records — taxonomie canonique

| Record | Rôle | Source de donnée actuelle | Source future |
|---|---|---|---|
| **Service** | Continuité de l'entretien documenté | Champ `de` (description) si présent + futurs `feat_carnet_complet`, `feat_factures` (Mission B-bis) | NLP sur descriptions longues |
| **Auction** | Historique des passages aux enchères | Champ `src` si maison d'enchères (Bonhams, RM Sotheby's, Artcurial, BringATrailer, CollectingCars, GoodingCo, Mecum, Aguttes) | Phase 2 Auction View |
| **Provenance** | Chaîne de propriétaires | Champ `ow` (nombre) | ECR cross-match Phase 3 |
| **Collection** | Distinctions, concours, awards | Mentions dans `de` (Pebble Beach, Villa d'Este, Rétromobile, Chantilly, Concours of Elegance) | NLP B-bis + ECR concours data |

Chaque Record a **trois états d'affichage** :
- **Riche** : donnée présente et significative → carte développée avec contenu.
- **Minimal** : trace de donnée mais pauvre → carte courte, factuelle.
- **Vide** : aucune donnée → carte avec libellé d'absence (pas une erreur, une information).

### C.2 Le Record Score — mapping vers données existantes

**Aucun changement dans la DB.** Les 5 sous-axes (`px`, `me`, `hi`, `an`, `km`) restent stockés tels quels. C'est l'**affichage** qui change : on regroupe sous les Records.

Mapping proposé :

| Records (affichage) | Sous-axes contributeurs | Total |
|---|---|---|
| Service Record | `me` (Mécanique 30) + `an` (Qualité annonce 15, partie carnet) | /35 effectif |
| Provenance Record | `hi` (Historique propriétaires 20) | /20 |
| Spec & condition | `px` (Prix marché 25) + `km` (Kilométrage 10) | /35 |
| Auction Record | bonus futur (non scoré dans la V1 du Records Score) | bonus ±5 |
| Collection Record | bonus futur | bonus ±5 |

Total V1 : 35 + 20 + 35 = 90 base + 10 marge réservée bonus futurs. La V1 doit normaliser à /100 pour ne pas casser le tri par score existant.

**Implémentation :** une fonction `mapScoreToRecords(car)` qui prend `car.ss` (le breakdown actuel) et renvoie un objet `{service, provenance, spec, total}` sans toucher à `car.sc`.

### C.3 Dérivation depuis la donnée — pseudocode

```javascript
/**
 * Lit une voiture de la base (objet Supabase) et dérive l'état
 * des quatre Records pour l'affichage.
 *
 * Garantit : ne lance jamais d'erreur, même si tous les champs sont null.
 * Renvoie toujours un objet à 4 clés.
 */
function deriveRecords(car) {
  return {
    service:    deriveServiceRecord(car),
    auction:    deriveAuctionRecord(car),
    provenance: deriveProvenanceRecord(car),
    collection: deriveCollectionRecord(car)
  };
}

function deriveServiceRecord(car) {
  const desc = (car.de || '').toLowerCase();
  const hasCarnetMention = /carnet\s+(complet|d['’]entretien|de\s+suivi)|factures\s+(disponibles|tous)|entretien\s+(complet|suivi)/i.test(desc);
  const hasNoCarnet = /sans\s+carnet|carnet\s+manquant|aucun\s+document/i.test(desc);

  // futurs feat_* viendront de Mission B-bis
  if (car.feat_carnet_complet === true) return { state: 'rich',    label: 'Carnet complet',         detail: 'Documentation continue' };
  if (hasCarnetMention)                  return { state: 'rich',    label: 'Carnet documenté',       detail: 'Mention dans la description' };
  if (car.feat_carnet_complet === false || hasNoCarnet) return { state: 'minimal', label: 'Carnet absent', detail: 'Documentation non fournie' };
  return { state: 'empty', label: 'Non renseigné', detail: 'Demander au vendeur' };
}

function deriveAuctionRecord(car) {
  const src = (car.src || '').toLowerCase();
  const auctionHouses = ['bonhams', 'sotheby', 'rmsotheby', 'artcurial',
                         'bringatrailer', 'collectingcars', 'goodingco',
                         'mecum', 'aguttes', 'oldtimergalerie'];
  const isAuction = auctionHouses.some(h => src.includes(h));

  if (isAuction) {
    const house = auctionHouses.find(h => src.includes(h));
    return { state: 'rich', label: 'Mise en vente publique', detail: `Source : ${house}` };
  }
  return { state: 'empty', label: 'Aucun passage public référencé', detail: '' };
}

function deriveProvenanceRecord(car) {
  if (car.ow != null && car.ow > 0) {
    const owners = car.ow;
    const label = owners === 1 ? 'Première main' :
                  owners === 2 ? 'Deux propriétaires' :
                  `${owners} propriétaires`;
    return { state: 'rich', label, detail: owners <= 2 ? 'Provenance favorable' : 'Provenance documentée' };
  }
  // futur ECR
  if (car.ecr_id != null) {
    return { state: 'rich', label: 'Référencée ECR', detail: 'Provenance vérifiée' };
  }
  return { state: 'empty', label: 'Provenance non documentée', detail: '' };
}

function deriveCollectionRecord(car) {
  const desc = (car.de || '').toLowerCase();
  const concoursPatterns = [
    { pattern: /pebble\s*beach/i,        name: 'Pebble Beach' },
    { pattern: /villa\s*d['’]?este/i,    name: "Villa d'Este" },
    { pattern: /rétromobile|retromobile/i, name: 'Rétromobile' },
    { pattern: /chantilly\s*arts?/i,     name: 'Chantilly Arts & Élégance' },
    { pattern: /concours\s*of\s*elegance/i, name: 'Concours of Elegance' },
    { pattern: /goodwood\s*revival/i,    name: 'Goodwood Revival' }
  ];
  const matches = concoursPatterns.filter(p => p.pattern.test(desc)).map(p => p.name);

  if (matches.length > 0) {
    return { state: 'rich', label: matches.join(' · '), detail: `${matches.length} distinction${matches.length>1?'s':''}` };
  }
  return { state: 'empty', label: 'Aucune distinction documentée', detail: '' };
}
```

Ces fonctions doivent être placées dans le bloc `<script>` global, **avant** le code de rendu de la card. Elles sont pures, sans effet de bord.

### C.4 États gracieux — règles d'affichage

Le Records block doit **toujours** afficher les 4 cartes, même si toutes sont vides. Une fiche dépouillée est aussi une information.

Règles de présentation :

- **`state: 'rich'`** : carte avec titre coloré (vert anglais `#1F4D2F` pour signal positif, ou neutre selon contexte), label en gras Bodoni italique, détail en Cormorant.
- **`state: 'minimal'`** : carte avec titre orange Polo `#E85A1F` (signal d'attention, pas alarme), label sobre.
- **`state: 'empty'`** : carte avec titre gris `var(--text3)`, label en italique discret. Pas de couleur d'alarme. C'est neutre, pas négatif.

Phrase pivot pour les states empty : **"Carnet en cours d'enrichissement"** affichable en pied de bloc si ≥3 Records sont vides — signale au user que la voiture vient juste d'arriver et que les données s'étofferont.

### C.5 Vocabulaire et voix — table de substitution

Pass de copy à appliquer **avec parcimonie** (pas un find-replace global, des remplacements ciblés section par section) :

| Ancien (AutoRadar) | Nouveau (Carnet) | Où |
|---|---|---|
| AutoRadar | Carnet | Tous les meta tags, OG, titre |
| La vérité sur chaque voiture | Une histoire de voitures | Tagline principale, OG description |
| Score de confiance | Record Score *(en EN)* / Score *(en FR seul)* | Tooltip score, modale détail score |
| Annonce | Entrée *(éditorial)* / Annonce *(usage courant — ne pas tout changer)* | Conserver "annonce" pour CTA, "entrée" pour récit |
| Trouvez votre prochain véhicule | Lisez les voitures qui méritent un carnet | Hero — variante éditoriale |
| Sans publicité | Sans bruit | Footer / value props |
| Voir l'annonce | Lire le carnet | Bouton CTA fiche |
| Mes favoris | Mes carnets | Onglet nav (peut être laissé "Favoris" si plus naturel pour user) |
| Publier une annonce | Inscrire votre voiture | CTA + titre wizard |

**Règles de voix non-négociables :**
- La voiture est *elle*, jamais *il* ni objet neutre.
- Pas de superlatifs (jamais *exceptionnelle*, *unique*, *rare opportunité*). Le matériel parle pour lui.
- Pas d'urgence factice (jamais *à saisir*, *vente flash*).
- Préférer le constatif au promotionnel : *Trois propriétaires* > *Seulement trois propriétaires*.
- Italiques Bodoni Moda pour les noms propres de modèles, de concours, de maisons d'enchères.
- DM Mono pour tous les chiffres (km, années, prix, scores).

---

## D. Structure de fichiers — modifications dans `index.html`

### D.1 Sections à AJOUTER

**D.1.1 Modale Manifeste** (nouvelle, à insérer après les autres modales, vers ligne ~1500) :

```html
<!-- ═══ MODAL: Manifeste Carnet ═══ -->
<div id="modal-manifest" class="manifest-overlay" style="display:none" onclick="if(event.target===this)closeManifest()">
  <div class="manifest-modal">
    <button class="modal-close" onclick="closeManifest()">×</button>
    <div class="manifest-body">
      <!-- Contenu : voir section E.1 -->
    </div>
  </div>
</div>
```

CSS associé (palette v8, Bodoni italique pour titre, Cormorant pour corps, max-width 720px, padding éditorial généreux).

**D.1.2 Bloc Records dans la fiche voiture** (rendu via JS) :

La card actuelle reste, mais on ajoute un bloc dépliable / une section séparée (au choix Claude Code, prévoir l'option la moins invasive). Fonction `renderRecordsBlock(car)` qui produit du HTML à injecter.

```javascript
function renderRecordsBlock(car) {
  const r = deriveRecords(car);
  const stateClass = (s) => `crn-rec-${s.state}`;
  return `
    <div class="crn-records">
      <div class="crn-records-title">Le carnet</div>
      <div class="crn-records-grid">
        <div class="crn-rec ${stateClass(r.service)}">
          <div class="crn-rec-label">Service</div>
          <div class="crn-rec-value">${r.service.label}</div>
          ${r.service.detail ? `<div class="crn-rec-detail">${r.service.detail}</div>` : ''}
        </div>
        <div class="crn-rec ${stateClass(r.auction)}">
          <div class="crn-rec-label">Enchères</div>
          <div class="crn-rec-value">${r.auction.label}</div>
          ${r.auction.detail ? `<div class="crn-rec-detail">${r.auction.detail}</div>` : ''}
        </div>
        <div class="crn-rec ${stateClass(r.provenance)}">
          <div class="crn-rec-label">Provenance</div>
          <div class="crn-rec-value">${r.provenance.label}</div>
          ${r.provenance.detail ? `<div class="crn-rec-detail">${r.provenance.detail}</div>` : ''}
        </div>
        <div class="crn-rec ${stateClass(r.collection)}">
          <div class="crn-rec-label">Collection</div>
          <div class="crn-rec-value">${r.collection.label}</div>
          ${r.collection.detail ? `<div class="crn-rec-detail">${r.collection.detail}</div>` : ''}
        </div>
      </div>
    </div>
  `;
}
```

**D.1.3 Lien d'accès au manifeste** dans le footer (si footer existe) ou dans la modale Mentions légales :
```html
<a href="#" onclick="openManifest();return false;">Le manifeste</a>
```

### D.2 Sections à MODIFIER

**D.2.1 Wizard Publier annonce — passage de 5 à 7 étapes**

Ancien `PAD_STEPS` (ligne 3931) :
```javascript
const PAD_STEPS = [
  { title:'Votre véhicule',     label:'Étape 1 sur 5 — Infos du véhicule' },
  { title:'Photos',             label:'Étape 2 sur 5 — Photos de l\'annonce' },
  { title:'Durée & formule',    label:'Étape 3 sur 5 — Choisir votre offre' },
  { title:'Vos coordonnées',    label:'Étape 4 sur 5 — Contact' },
  { title:'Récapitulatif',      label:'Étape 5 sur 5 — Vérification' }
];
```

Nouveau `PAD_STEPS` :
```javascript
const PAD_STEPS = [
  { title:'La voiture',          label:'1 sur 7 — Identité du véhicule',           key:'vehicle'   },
  { title:'Le carnet',            label:'2 sur 7 — Service & entretien',            key:'service'   },
  { title:'La provenance',        label:'3 sur 7 — Propriétaires & histoire',       key:'provenance'},
  { title:'Les distinctions',     label:'4 sur 7 — Enchères, concours, médias',     key:'collection'},
  { title:'Photos',               label:'5 sur 7 — Iconographie',                   key:'photos'    },
  { title:'Formule',              label:'6 sur 7 — Choisir votre offre',            key:'plan'      },
  { title:'Vos coordonnées',      label:'7 sur 7 — Contact & vérification',         key:'contact'   }
];
```

Cinq fonctions de rendu à créer / adapter : `padS1()` (vehicle, déjà existante, ne pas toucher au formulaire de base), `padS2()` (service — NOUVEAU), `padS3()` (provenance — NOUVEAU), `padS4()` (distinctions — NOUVEAU), `padS5()` (photos — déplacer depuis l'ancien S2), `padS6()` (plan — déplacer S3), `padS7()` (contact + récap fusionnés — adapter S4 et S5).

Tous les nouveaux champs sont **optionnels** : un user qui ne sait rien du carnet de sa Golf peut tout sauter. Mais un user avec une Pagani peut tout remplir.

Champs des nouveaux écrans (voir section E.4 pour les labels exacts) :

- **Étape 2 — Le carnet** :
  - `service_status` : radio (Carnet complet / Partiel / Absent / Je ne sais pas) — défaut "Je ne sais pas"
  - `service_last_date` : date optionnelle
  - `service_factures` : checkbox "Factures disponibles"
  - `service_notes` : textarea optionnelle (200 char max)

- **Étape 3 — La provenance** :
  - `owners_count` : number input (1, 2, 3+)
  - `first_owner` : checkbox "Première main"
  - `provenance_notes` : textarea (concessionnaire d'origine, pays d'import, particularité notable)
  - `ecr_id` : text input optionnel ("Si la voiture est référencée Exclusive Car Registry, indiquez son ID")

- **Étape 4 — Les distinctions** :
  - `auction_history` : multi-row repeatable (maison + année + prix d'adjudication + lot number) — par défaut zéro ligne
  - `concours_list` : multi-select (Pebble Beach, Villa d'Este, Rétromobile, Chantilly, Concours of Elegance, Goodwood, Autre)
  - `concours_other` : text si "Autre" coché
  - `media_features` : textarea optionnelle ("Apparitions presse, films, livres")

**D.2.2 Hero / homepage**

Remplacer le placeholder de recherche AI (ligne 899) et les meta-titres par des contenus voix Carnet (voir section E.2).

**D.2.3 Meta tags SEO**

Lignes 6 à 17 — basculer toutes les meta description / OG / Twitter sur la voix Carnet (voir section E.6).

**D.2.4 Score breakdown UI**

La modale / tooltip qui montre le détail du score doit grouper les 5 sous-axes sous les 3 catégories Records (Service / Provenance / Spec). Aucun changement de calcul, juste de présentation. Voir section E.3.

### D.3 Sections à NE PAS TOUCHER

- Le bloc `<style>` (lignes 40-868) : ajouter du CSS Records à la fin, ne pas toucher à l'existant.
- Toute la logique de filtres (`p-make`, `p-model`, `p-fuel`, etc.).
- La logique de favoris / collections.
- La logique de paywall, donations, leaderboard, partage, FAQ, signaler bug.
- La connexion Supabase (`_sb.from('cars')...`) — la requête reste identique.
- Les MAKES_MAIN, MAKES_OTHER (sauf si Claude Code détecte des oublis luxueux à compléter — proposer à Sergio avant de toucher).

---

## E. Copywriting prêt à coller

### E.1 Manifeste — texte complet (modale)

```
                    Une histoire de voitures.

Carnet est né d'une conviction : chaque voiture mérite son carnet. Pas
une fiche d'annonce, pas un dossier commercial — un carnet, au sens
ancien du mot. Le registre où s'écrivent les choses qui comptent.

Quatre Records, quatre carnets

Service Record — l'entretien.
Le carnet d'entretien d'une voiture est sa colonne vertébrale. Un
carnet complet vaut souvent plus qu'un détail esthétique. Il dit la
continuité, la main soigneuse, le respect du temps qui passe. Quand
nous avons l'information, nous l'inscrivons. Quand nous ne l'avons
pas, nous le disons aussi.

Auction Record — les passages publics.
Quand une voiture passe aux enchères, elle laisse une trace. Date,
maison, prix d'adjudication, numéro de lot. Cette trace dessine sa
trajectoire de marché et, parfois, son histoire culturelle.

Provenance Record — les propriétaires.
Une voiture n'appartient jamais qu'à elle-même et à la chaîne de ceux
qui l'ont gardée. Combien étaient-ils. Qui était le premier. Si elle
est référencée par l'Exclusive Car Registry, son provenance est
vérifiée — et nous le signalons.

Collection Record — les distinctions.
Concours d'élégance, expositions, films, parutions presse. Une
voiture qui a été vue est une voiture qui a une histoire à raconter.

Le Record Score

Notre note sur cent ne juge pas. Elle agrège. Elle rend lisible. Elle
décompose pour que vous puissiez décider — *vous* — ce qui compte
pour votre prochain achat. Une voiture peut être 95/100 sur le
Service et 40/100 sur la Provenance. À vous de lire.

Ce que nous ne ferons jamais

Pas de publicité. Pas d'urgence factice. Pas de superlatifs vides.
Pas de mise en vedette payante. Pas d'annonces réécrites pour vendre
mieux. Le matériel parle pour lui. Notre rôle est de l'organiser, pas
de le maquiller.

Si vous publiez une voiture chez nous, vous l'inscrivez dans son
carnet. Si vous en achetez une, vous reprenez l'écriture du carnet à
votre tour.

                    Carnet — A record of every record.
```

**Format CSS :**
- Bodoni Moda 500 italique pour la baseline d'ouverture *"Une histoire de voitures."* (taille ~32px desktop, ~22px mobile).
- Cormorant Garamond 400 pour le corps (taille 16px, line-height 1.7).
- Bodoni Moda italique pour les sous-titres "Service Record — l'entretien." (taille 18px, espacement vertical généreux).
- DM Mono pour la signature finale *"A record of every record."* (taille 12px, lettrage espacé).
- Couleur principale : Encre #0A0A0A sur Papier #F4F1EA.
- Pas de gras non-italique. Pas de bullet points. Pas d'icônes. Texte pur.

### E.2 Hero / homepage — variantes

**Tagline principale (à mettre dans le hero) :**
> *Une histoire de voitures.*

**Sous-tagline (variante 1, éditoriale) :**
> *Les voitures qui méritent un carnet sont rares. Leur carnet l'est encore plus. Carnet rassemble les deux.*

**Sous-tagline (variante 2, fonctionnelle) :**
> *Quatre Records pour chaque voiture : Service, Enchères, Provenance, Collection. Un score qui décompose plutôt qu'il ne juge.*

**Sous-tagline (variante 3, ouvertement bilingue) :**
> *Carnet — Curated Automotive Records Network.*

**Placeholder du champ de recherche AI (remplace ligne 899) :**
> *"Recherche libre — ex : 911 Carrera 3.2, première main, carnet complet, sous 80 000€"*

**Compteur de véhicules (ligne ~1010) :**
Remplacer *"X véhicules · X sources"* par *"X carnets ouverts · X sources"*.

### E.3 Score breakdown — labels regroupés

Dans la modale qui détaille le score, regrouper visuellement les 5 sous-axes existants sous trois catégories Records. Pas de changement de calcul.

```
                Record Score — comment se compose votre note

  ┌─ Service Record ────────────── /35 ─┐
  │  Mécanique & fiabilité            v/30 │
  │  Qualité du carnet                v/15* │
  └────────────────────────────────────┘
                                     *partie carnet de l'axe annonce

  ┌─ Provenance Record ─────────── /20 ─┐
  │  Historique propriétaires         v/20 │
  └────────────────────────────────────┘

  ┌─ Spec & condition ──────────── /35 ─┐
  │  Prix marché                      v/25 │
  │  Kilométrage cohérent             v/10 │
  └────────────────────────────────────┘
```

Au-dessus, libellé : *"Le Record Score agrège trois dimensions du carnet de la voiture. À mesure que les Auction Records et Collection Records s'enrichiront, ils contribueront en bonus."*

### E.4 Wizard "Publier annonce" — labels par étape

**Titre du modal (remplace "Votre véhicule") :**
> *Inscrire votre voiture*

**Étape 1 — La voiture (déjà existante, ne pas toucher au formulaire)**
- Garder les champs actuels (marque, modèle, année, km, prix, énergie, boîte, ville, pays, description).

**Étape 2 — Le carnet (nouvelle)**

Intro paragraphe :
> *Le carnet d'entretien est la colonne vertébrale d'une voiture. Renseignez ce que vous savez, sautez ce que vous ne savez pas. Mieux vaut une absence honnête qu'une affirmation hâtive.*

Champs :
- **L'état du carnet** (radio) :
  - ○ Complet — toutes les révisions documentées
  - ○ Partiel — quelques traces, des trous
  - ○ Absent — pas de carnet à fournir
  - ◉ Je ne sais pas *(défaut)*
- **Dernière révision** (date, optionnel) — *Si vous avez la date sous les yeux.*
- **Factures disponibles** (checkbox) — *Cochez si vous pouvez fournir les factures sur demande.*
- **Notes sur l'entretien** (textarea, 200 char max, optionnel) — *Atelier de référence, pièces remplacées, particularité.*

**Étape 3 — La provenance (nouvelle)**

Intro :
> *Une voiture n'appartient jamais qu'à elle-même et à la chaîne de ceux qui l'ont gardée.*

Champs :
- **Nombre de propriétaires** (number, défaut vide) — *Y compris vous.*
- **Première main** (checkbox) — *Cochez si la voiture n'a connu que vous depuis sa sortie d'usine ou sa première mise en circulation.*
- **Histoire de la voiture** (textarea, 400 char max, optionnel) — *Concessionnaire d'origine, pays de première immatriculation, particularité notable.*
- **ID Exclusive Car Registry** (text, optionnel) — *Si la voiture est référencée sur l'ECR, indiquez son identifiant.*

**Étape 4 — Les distinctions (nouvelle)**

Intro :
> *Une voiture qui a été vue est une voiture qui a une histoire. Si la vôtre est passée aux enchères, à un concours, dans un film ou un livre, c'est ici.*

Champs :
- **Passages aux enchères** (multi-row, défaut zéro ligne, bouton + ajouter) :
  - Maison (text)
  - Année (number)
  - Prix d'adjudication € (number, optionnel)
  - Numéro de lot (text, optionnel)
- **Concours d'élégance** (multi-select) :
  - ☐ Pebble Beach
  - ☐ Villa d'Este
  - ☐ Rétromobile
  - ☐ Chantilly Arts & Élégance
  - ☐ Concours of Elegance
  - ☐ Goodwood Revival
  - ☐ Autre — *(text si coché)*
- **Apparitions presse / films / livres** (textarea, 300 char max, optionnel) — *Référence précise si possible : titre, année, page.*

**Étape 5 — Photos (déplacée depuis ancien S2)**
Garder existante.

**Étape 6 — Formule (déplacée depuis ancien S3)**
Garder existante.

**Étape 7 — Vos coordonnées (déplacée depuis ancien S4 + S5 fusionnés ou enchaînés)**
Garder existante.

### E.5 Footer / signature globale

Ajouter en pied de page (footer ou dans Mentions légales) :

> *Carnet — A record of every record.*

En DM Mono, taille 11px, espacement de lettre +0.05em, couleur `var(--text3)`.

### E.6 Meta tags SEO — refonte

Remplacer lignes 6 à 17 :

```html
<meta name="description" content="Carnet — Quatre Records pour chaque voiture : Service, Enchères, Provenance, Collection. La marketplace éditoriale des voitures qui méritent un carnet.">
<meta name="theme-color" content="#1F4D2F">
<!-- Open Graph -->
<meta property="og:title" content="Carnet — Une histoire de voitures." />
<meta property="og:description" content="Quatre Records pour chaque voiture. Curated Automotive Records Network." />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://carnet.life" />
<meta property="og:image" content="https://carnet.life/og.png" />
<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Carnet — Une histoire de voitures." />
<meta name="twitter:description" content="Quatre Records pour chaque voiture. Curated Automotive Records Network." />
```

Et ligne 36 :
```html
<title>Carnet — Une histoire de voitures.</title>
```

### E.7 Mentions légales — paragraphe à supprimer

Ligne 1199 actuelle :
> *"AutoRadar est en phase bêta. Les données d'annonces sont actuellement illustratives. La version de production connectera des sources réelles..."*

À remplacer par :
> *"Carnet est en bêta. Les annonces affichées sont des entrées réelles, agrégées depuis nos sources partenaires (LeBonCoin, AutoScout24, La Centrale, 2ememain, et nos concessionnaires premium). Les Quatre Records s'enrichissent au fur et à mesure de l'arrivée des données."*

Cohérence indispensable : depuis le branchement Supabase actif (mai 2026), la mention "illustratives" est obsolète.

### E.8 CTA "Rechercher" — couleur

Rappel TODO Carnet : actuellement le CTA `Rechercher ↗` est en vert anglais. Selon la charte v8, l'orange Polo (#E85A1F) est la couleur d'action et de sélection ; le vert anglais est la couleur de validation et de carnet OK. Le bouton de recherche est une **action**, pas une validation.

→ Basculer le CTA `Rechercher ↗` en orange Polo `#E85A1F` (background) avec texte Papier pur `#FAFAF7`. Le hover peut être un `#D14E15` (orange légèrement plus foncé).

---

## F. Acceptance criteria

### F.1 Visuel

- [ ] Palette v8 strictement respectée (5 couleurs uniquement) sur tout le nouveau code ajouté.
- [ ] Bodoni Moda 500 italique pour les titres éditoriaux (manifeste, hero), Cormorant 400 pour le corps, DM Mono pour les chiffres.
- [ ] Border-radius 2px partout (Records cards, modale manifeste, nouveaux inputs wizard).
- [ ] Aucune nouvelle dépendance CSS / police (toutes les fonts sont déjà chargées ligne 37).
- [ ] La modale Manifeste s'ouvre, se ferme, est responsive (mobile <380px doit rester lisible).
- [ ] Le Records block s'affiche dans la card de fiche voiture, avec les 4 cartes même si toutes sont vides.

### F.2 Fonctionnel

- [ ] Les 200+ voitures actuelles s'affichent toutes sans erreur JS (vérifier dans la console).
- [ ] Pour une voiture avec `de=null` et `ow=null`, les 4 Records affichent leur état empty proprement, pas d'erreur, pas de "undefined".
- [ ] Pour une voiture issue de Bonhams, le Auction Record passe en state rich.
- [ ] Pour une voiture avec `ow=1`, le Provenance Record affiche "Première main".
- [ ] Le wizard Publier annonce passe de 5 à 7 étapes, on peut tout sauter (rien d'obligatoire dans les 3 nouvelles étapes), on arrive au récap, on peut publier.
- [ ] Le draft du wizard (sauvegardé en localStorage à la ligne ~3240) continue de fonctionner avec les nouveaux champs.
- [ ] Le score breakdown (modale détail) regroupe visuellement les 5 sous-axes sous Service / Provenance / Spec.
- [ ] Le CTA Rechercher est en orange Polo.

### F.3 Contenu

- [ ] Aucun superlatif dans le copywriting nouveau (audit textuel : pas de "exceptionnel", "unique", "rare opportunité", "à saisir", "incontournable").
- [ ] La voiture est désignée par "elle" partout dans le manifeste et le wizard.
- [ ] Le mot "AutoRadar" n'apparaît plus nulle part (audit : `grep -i AutoRadar index.html` → 0 résultat).
- [ ] La phrase "Les données d'annonces sont actuellement illustratives" a disparu.
- [ ] La signature "Carnet — A record of every record." est présente quelque part (footer ou mentions).

### F.4 Cohésion

- [ ] Le vocabulaire Records (Service / Auction / Provenance / Collection) est cohérent entre la fiche voiture, le wizard de publication, le manifeste et le score breakdown.
- [ ] L'utilisateur qui publie une annonce remplit des champs qui correspondent aux Records affichés sur la fiche.
- [ ] La voix éditoriale (italiques Bodoni pour modèles et concours, DM Mono pour chiffres, Cormorant pour corps) est appliquée dans le manifeste, le hero, et les intros de wizard.

---

## G. Garde-fous explicites

### G.1 Périmètre fichier

- ❌ **NE PAS** créer d'autres fichiers (.js, .css externes). L'app est volontairement single-file.
- ❌ **NE PAS** toucher aux fichiers du repo scraper (`~/Code/autoradar/scraper/`).
- ❌ **NE PAS** modifier `manifest.json`, `sw.js`, ou les icônes PWA.
- ❌ **NE PAS** introduire de framework (React, Vue, Alpine). L'app est en JS vanilla + Supabase JS SDK.

### G.2 Périmètre code

- ❌ **NE PAS** refactorer les fonctions existantes qui ne sont pas dans la liste de modification (filtres, favoris, paywall, leaderboard, etc.).
- ❌ **NE PAS** changer le calcul du score (les sous-axes `px`, `me`, `hi`, `an`, `km` restent stockés et calculés tels quels).
- ❌ **NE PAS** changer la requête Supabase. Aucune nouvelle colonne demandée.
- ❌ **NE PAS** introduire de nouvelles dépendances CDN ou polices.
- ❌ **NE PAS** modifier le draft localStorage existant — l'étendre avec les nouveaux champs, oui, le casser, non.

### G.3 Discipline git

- ❌ **NE PAS** force-push.
- ❌ **NE PAS** commit sur `main` directement. Travailler sur une branche `feat/records-framework`.
- ✅ **AVANT** toute modification : copie de sauvegarde locale `cp index.html index.html.before_records_pass`.
- ✅ Commits par section logique (un commit par module : manifeste, fiche, wizard, copywriting, etc.) avec messages `feat(records): ...`.

### G.4 Vérification continue

- ✅ Après chaque section terminée : ouvrir l'app dans un navigateur, vérifier qu'aucune voiture ne plante (console JS propre).
- ✅ Tester avec au moins **3 voitures différentes** : une avec données riches (`ow` rempli, `de` long, `src` = Bonhams), une avec données moyennes (`ow` rempli mais `de` court), une avec données pauvres (`de` null, `ow` null).
- ✅ Tester le wizard de bout en bout en sautant tous les champs optionnels — il doit aboutir.
- ✅ Tester le wizard en remplissant tous les champs — il doit aboutir aussi.

### G.5 En cas de doute

- Si un changement risque d'impacter une zone hors-scope (filtres, score calculation, Supabase), **demander à Sergio avant de commit**.
- Si l'audit voix textuelle révèle un superlatif dans la copy existante (pas seulement ajoutée), **proposer le remplacement à Sergio**, ne pas modifier sans validation.
- Si la mise en page Records block ne tient pas mobile <380px, **réduire à 2 colonnes (2x2)** plutôt que 4 cartes en ligne. Ne pas casser le mobile pour faire joli desktop.

---

## H. Workflow de commits

Branche : `feat/records-framework` (depuis main).

Sequence de commits proposée :

```
feat(records): backup index.html before pass + add design tokens for Records
feat(records): add deriveRecords() pure helpers (4 functions)
feat(records): add renderRecordsBlock() and CSS for Records block
feat(records): integrate Records block into car detail card
feat(records): add Manifeste modal + open/close handlers
feat(records): refresh hero copy + meta tags + title
feat(records): refactor score breakdown UI to group by Records
feat(records): expand wizard from 5 to 7 steps (Service/Provenance/Distinctions)
feat(records): voice pass — vocabulary substitutions across copy
feat(records): switch Rechercher CTA to Orange Polo
chore(records): final audit — no AutoRadar mentions, no illustratives mention
```

Chaque commit doit être atomique et l'app doit rester fonctionnelle entre commits.

Merge sur main : **uniquement après validation Sergio** sur le rendu visuel de l'app servie en local ou en preview Vercel.

---

## I. Estimation temps

| Section | Estimation | Note |
|---|---|---|
| Setup + design tokens (couleurs/CSS Records) | 30 min | Ajout uniquement, pas de refactor |
| `deriveRecords()` + helpers + tests manuels | 1h | Pseudocode déjà fourni |
| `renderRecordsBlock()` + CSS + intégration card | 1h30 | Le plus visible, à soigner |
| Modale Manifeste (HTML + CSS + texte E.1) | 1h | Texte fourni, juste à styler |
| Hero + meta + title refresh | 30 min | Find-replace ciblé |
| Score breakdown UI (regroupement visuel) | 1h | Adapter modale existante |
| Wizard expansion 5→7 étapes | 2h30 | 3 nouvelles fonctions de rendu, draft localStorage à étendre |
| Voice pass — substitutions vocabulaire | 45 min | Table E.5, ciblé |
| CTA Rechercher → orange | 10 min | Trivial |
| Audit final + tests 3 voitures + tests wizard | 45 min | Important, ne pas zapper |
| **Total** | **~9h** | Plus si Claude Code est consciencieux sur les tests |

À répartir sur 1 ou 2 sessions Claude Code. Recommandation : faire les sections D.1 (Manifeste, Records block, hero) en première session, les sections D.2 (wizard, score breakdown, voice pass) en seconde.

---

## J. Checklist pré-exécution

Avant de lancer Claude Code sur ce brief :

- [ ] Le repo `Vinci75000/autoradar` est cloné en local.
- [ ] Le fichier `index.html` à la racine du repo correspond bien à la version prod (267k bytes, 4796 lignes).
- [ ] Une branche `feat/records-framework` est créée depuis main.
- [ ] Une copie `index.html.before_records_pass` est faite.
- [ ] L'app est servable en local (ouverture directe du fichier dans le navigateur ou via `python3 -m http.server`).
- [ ] La connexion Supabase fonctionne (les 200 voitures se chargent en local).
- [ ] Sergio a relu ce brief et validé les choix structurants (notamment : passage wizard 5→7, mapping Records ↔ sous-axes, manifeste long).

Engagement Claude Code pour cette session :

- ✅ Tu modifies UNIQUEMENT `index.html` à la racine.
- ✅ Tu travailles sur la branche `feat/records-framework`.
- ✅ Tu commits par section logique avec messages `feat(records): ...`.
- ✅ Tu testes après chaque commit (console JS propre, 3 voitures vérifiées).
- ✅ Tu montres à Sergio à la fin : `git log --oneline feat/records-framework`, `git diff main..feat/records-framework --stat`, et un screenshot ou deux des nouvelles sections en local.
- ❌ Tu ne mergues PAS sur main sans validation.
- ❌ Tu ne touches à aucun autre fichier ni repo.

---

**Tout est cadré. Quand tu valides, on lance la première session sur les sections D.1 (Manifeste + Records block + hero), on revient pour review, puis on enchaîne D.2 (wizard + score breakdown + voice pass).**
