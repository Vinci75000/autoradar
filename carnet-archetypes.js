/* ═══════════════════════════════════════════════════════════════════════
   CARNET · Archétypes canonical · Module shared
   ───────────────────────────────────────────────────────────────────────
   Source unique de vérité pour les 8 archétypes Carnet (v6 final).
   À importer avant tout script qui utilise les archétypes :
     <script src="carnet-archetypes.js"></script>

   Expose un objet global : window.CarnetArchetypes
     - COLLECTOR_PROFILES   : array des 8 archétypes (id, label, chip, teaser, long)
     - STORAGE_KEYS         : clés localStorage canoniques
     - getProfileById(id)   : helper lookup
     - migrateLegacyProfileIds(arr) : migration ex-Gardien + ex-social → mondain
     - loadProfiles()       : lit localStorage, migre, dédoublonne, filtre valides
     - saveProfiles(arr)    : écrit localStorage, dégradation gracieuse

   Compat : IIFE pur, aucune dépendance, ES5-safe (works partout).
   Version : v1.0 · 2026-05-14
   ═══════════════════════════════════════════════════════════════════════ */

(function (global) {
  'use strict';

  /* ─────────────────────────────────────────────────────────────────────
     Les 8 archétypes Carnet v6 final
     ───────────────────────────────────────────────────────────────────── */
  var COLLECTOR_PROFILES = [
    {
      id: 'collector',
      label: 'Le Collectionneur',
      chip: 'COLLECTION',
      verb: 'Conserver',
      teaser: 'Acquérir pour conserver. Provenance et rareté.',
      long:
        'Tu acquiers pour conserver. Provenance, rareté, état d\u2019origine — c\u2019est ton langage. ' +
        'Tes voitures quittent rarement le garage. Elles racontent une époque, et tu en es le ' +
        'dépositaire patient. Le marché te parle, mais c\u2019est l\u2019histoire qui te tient. ' +
        'Tu prends soin de ce qui mérite de durer.'
    },
    {
      id: 'flipper',
      label: 'Le Flippeur',
      chip: 'FLIP',
      verb: 'Trader',
      teaser: 'Acheter au bon prix, revendre au meilleur moment.',
      long:
        'Tu vois les voitures comme des paris. Achat au bon prix, revente au meilleur moment. ' +
        'La cote te parle plus que l\u2019histoire. Mouvement constant — la voiture rare ne ' +
        's\u2019attarde pas chez toi, elle traverse, et tu en tires ce qui doit l\u2019être. ' +
        'Pas par cynisme. Par lucidité.'
    },
    {
      id: 'track_rat',
      label: 'Le Track Rat',
      chip: 'CIRCUIT',
      verb: 'Pousser',
      teaser: 'Le circuit, ton terrain. Pousser jusqu\u2019aux limites.',
      long:
        'Le circuit, ton terrain. Tu pousses la voiture à ses limites — et les tiennes. Modifs ' +
        'perf ciblées, harnais, cage si nécessaire. Week-ends à Spa, Nürburgring, La Sarthe, ' +
        'Magny-Cours. Tu sais ce que veut dire un meilleur tour, et tu sais ce que ça coûte. ' +
        'La technique te répond, parce que tu lui parles bien.'
    },
    {
      id: 'builder',
      label: 'Le Bâtisseur',
      chip: 'OUTLAW',
      verb: 'Façonner',
      teaser: 'Façonner la voiture à sa vision. Restomods, outlaws.',
      long:
        'Tu façonnes la voiture à ta vision. Restomods, outlaws, modifs assumées — la convention ' +
        'te répugne. Singer, Brabus, Alpina, Carlsson, ou un artisan local de génie. Tu cherches ' +
        'l\u2019épaisseur de l\u2019objet sous celle du modèle. Tu ne dénatures pas : tu rends à ' +
        'la voiture ce qu\u2019elle aurait dû être, ou ce qu\u2019elle pourrait devenir.'
    },
    {
      id: 'enthusiast',
      label: 'L\u2019Enthousiaste',
      chip: 'DÉTAIL',
      verb: 'Savoir',
      teaser: 'Numéros de châssis, options d\u2019usine, séries spéciales.',
      long:
        'Tu sais ce qu\u2019est un système Lambda. Numéros de châssis, options d\u2019usine, ' +
        'séries spéciales, matching numbers, code couleur d\u2019origine — Carnet est ton ' +
        'terrain de jeu. Tu lis les fiches comme d\u2019autres lisent des poèmes. Tu reconnais ' +
        'une 911 1973 RS Touring d\u2019une RS Lightweight d\u2019un coup d\u2019\u0153il. La ' +
        'précision n\u2019est pas une lubie chez toi : c\u2019est ta forme de respect.'
    },
    {
      id: 'driver',
      label: 'Le Pilote',
      chip: 'ROUTE',
      verb: 'Conduire',
      teaser: 'Conduire. Vraiment. Les kilomètres sont une médaille.',
      long:
        'Tu conduis. Vraiment. Les kilomètres sont une médaille, pas une tare. Le bonheur, ' +
        'c\u2019est une route ouverte un samedi matin — la D-quelque-chose entre deux villages ' +
        'oubliés, le moteur qui chauffe doucement, les vitres baissées. Tu ne comprends pas ' +
        'qu\u2019on laisse une voiture dormir. Une voiture qu\u2019on ne conduit plus est une ' +
        'voiture qui meurt.'
    },
    {
      id: 'mondain',
      label: 'Le Mondain',
      chip: 'DISPLAY',
      verb: 'Exposer',
      teaser: 'Villa d\u2019Este, Chantilly. Exposer ce qui se contemple.',
      long:
        'Tu sors la voiture pour qu\u2019elle soit vue dans son meilleur cadre. Concours ' +
        'd\u2019élégance, pelouses anglaises, photos de famille devant la machine. Tweed, posé, ' +
        'gentleman. Tu acquiers ce que tu protèges, tu protèges ce que tu exposes. La voiture ' +
        'comme passeport social — et comme \u0153uvre dont tu es le commissaire d\u2019exposition. ' +
        'Villa d\u2019Este, Chantilly, Hampton Court, Pebble Beach : tu connais les pelouses ' +
        'par leur grain.'
    },
    {
      id: 'mousquetaire',
      label: 'Le Mousquetaire',
      chip: 'RALLYE',
      verb: 'Servir',
      teaser: 'Un pour tous, tous pour un. Pousser pour servir.',
      long:
        'Tu roules en bande, jamais seul. Mille Miglia, Gumball, Tour Auto, Modball, Goodwood — ' +
        'l\u2019itinéraire compte autant que la voiture. Réveils à l\u2019aube, départs en ' +
        'convoi, étapes folles, photos floues à minuit.\n\n' +
        'Aux yeux du commun tu pousses fort. Aux tiens, c\u2019est l\u2019évidence. Tu connais ' +
        'ta voiture comme un mousquetaire connaît sa lame — préparée, entretenue, fiable au-delà ' +
        'du raisonnable. Tu sais conduire, pas en théorie : en kilomètres et en années. Quand tu ' +
        'roules au-delà de la lettre, c\u2019est qu\u2019une \u0153uvre attend au bout de la ' +
        'route — un hôpital, une fondation, des enfants à qui ce rallye paiera la suite.\n\n' +
        'Un pour tous, tous pour un — c\u2019est la devise vécue, pas décorative. On ne laisse ' +
        'personne sur le bord de la route, ni derrière. Une panne, une fatigue, un coup de ' +
        'moins bien — la bande s\u2019arrête. Tu donnes ta clé de 13, ton litre d\u2019huile, ' +
        'ton heure de sommeil.\n\n' +
        'Tu prends à la règle ce que tu donnes au caritatif. La loi te regarde avec un demi-' +
        'sourire, parce qu\u2019elle sait que tu ne mets en danger que ta propre légende. ' +
        'Foulard au cou, plume au chapeau si tu veux. Tu partages avec ta bande comme on partage ' +
        'un secret. Et tout, à la fin, sert à plus grand que vous.'
    }
  ];

  /* ─────────────────────────────────────────────────────────────────────
     Storage keys canoniques
     ───────────────────────────────────────────────────────────────────── */
  var STORAGE_KEYS = {
    PROFILES: 'carnet:v1:profiles',
    ONBOARDING_SEEN: 'carnet:v1:onboarding-seen'
  };

  /* ─────────────────────────────────────────────────────────────────────
     Migration legacy IDs vers schéma v6 final
     - non_driver : ex-Gardien (statique)      → mondain (DISPLAY merged)
     - social     : ex-Mondain RALLYE social   → mondain (DISPLAY)
                    NOTE : à valider cas par cas si users prod ; certains
                    voulaient peut-être mousquetaire (route en bande caritative).
     ───────────────────────────────────────────────────────────────────── */
  function migrateLegacyProfileIds(profiles) {
    if (!profiles || !profiles.length) return [];
    var map = { non_driver: 'mondain', social: 'mondain' };
    var out = [];
    for (var i = 0; i < profiles.length; i++) {
      var id = profiles[i];
      out.push(map[id] || id);
    }
    return out;
  }

  /* ─────────────────────────────────────────────────────────────────────
     Lookup helper
     ───────────────────────────────────────────────────────────────────── */
  function getProfileById(id) {
    for (var i = 0; i < COLLECTOR_PROFILES.length; i++) {
      if (COLLECTOR_PROFILES[i].id === id) return COLLECTOR_PROFILES[i];
    }
    return null;
  }

  /* ─────────────────────────────────────────────────────────────────────
     Persistence (localStorage, dégradation gracieuse)
     ───────────────────────────────────────────────────────────────────── */
  function loadProfiles() {
    try {
      var raw = localStorage.getItem(STORAGE_KEYS.PROFILES);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      if (!parsed || !parsed.length) return [];

      // Migration + dedupe + filter
      var migrated = migrateLegacyProfileIds(parsed);
      var validIds = {};
      for (var i = 0; i < COLLECTOR_PROFILES.length; i++) {
        validIds[COLLECTOR_PROFILES[i].id] = true;
      }
      var seen = {};
      var result = [];
      for (var j = 0; j < migrated.length; j++) {
        var id = migrated[j];
        if (validIds[id] && !seen[id]) {
          seen[id] = true;
          result.push(id);
        }
      }
      return result;
    } catch (e) {
      // localStorage indisponible (Safari privé, quota plein, etc.)
      // Dégradation silencieuse, pas de bruit dans la console pour le user.
      return [];
    }
  }

  function saveProfiles(profiles) {
    try {
      localStorage.setItem(STORAGE_KEYS.PROFILES, JSON.stringify(profiles || []));
      return true;
    } catch (e) {
      return false;
    }
  }

  /* ─────────────────────────────────────────────────────────────────────
     Export global
     ───────────────────────────────────────────────────────────────────── */
  global.CarnetArchetypes = {
    COLLECTOR_PROFILES: COLLECTOR_PROFILES,
    STORAGE_KEYS: STORAGE_KEYS,
    getProfileById: getProfileById,
    migrateLegacyProfileIds: migrateLegacyProfileIds,
    loadProfiles: loadProfiles,
    saveProfiles: saveProfiles,
    VERSION: '1.0'
  };

  // Support CommonJS (pour bundlers éventuels)
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = global.CarnetArchetypes;
  }
})(typeof window !== 'undefined' ? window : this);
