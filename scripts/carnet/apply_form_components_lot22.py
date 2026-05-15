#!/usr/bin/env python3
"""
CARNET · Lot 22 (Phase α) — Form components : unification des ticks

Source        : Audit Lot 22, dernier lot du plan refonte mobile v5+.

  Cartographie des composants de formulaire :
  - .garage-form-* (67 usages) : système principal, DÉJÀ refondu v5.x
    (override lignes 6406-6447). Vivant, cohérent. Non touché.
  - .form-* générique (0 usage réel — les "5 usages" comptés sont
    l'exemple dans le commentaire) : système charte v8 stylé mais
    orphelin. Comme .banner l'était au Lot 21.
  - .form-tick (0 usage) : rangée cliquable générique box+label, état
    .checked vert anglais. C'est la version générique de
    .garage-condition-tick. Orpheline aussi.
  - 4 classes de "tick" RÉELLEMENT utilisées :
      .garage-condition-tick (3×) — VRAIE checkbox carrée 16×16, box qui
        se remplit en vert anglais. Composant à part entière, unique.
      .tuner-cat-tick (2×)        — simple glyphe ✓ orange polo
      .profile-card-tick (1×)     — simple glyphe ✓ orange polo 14px
      .onboarding-profile-tick (1×) — simple glyphe ✓ orange polo 13px

  Constat : .tuner-cat-tick / .profile-card-tick / .onboarding-profile-tick
  sont EXACTEMENT le même composant — un glyphe ✓ orange polo qui
  apparaît/disparaît — sous 3 noms et 3 tailles légèrement différentes
  (12/14/13px). C'est la vraie dette de cohérence (comme .sheet-row au
  Lot 19, .profile-onboarding au Lot 21).
  .garage-condition-tick est DIFFÉRENT (rangée-checkbox) → non touché.

Stratégie     : "slick, light, robuste, durable, user-friendly"
  - slick        : 1 composant glyphe canonique (.tick) au lieu de 3
  - light        : 3 blocs CSS redondants retirés
  - robuste      : .form-* et .form-tick (systèmes génériques déjà
                   construits, charte v8) sont CONSERVÉS et clairement
                   documentés comme systèmes-cibles intentionnels — pas
                   supprimés (on perdrait du travail propre), pas forcés
                   sur garage-form-* (67 usages, risque élevé, 0 gain).
  - durable      : un futur dev sait quoi utiliser (.tick pour un glyphe,
                   .form-tick pour une rangée-checkbox, .form-* pour un
                   nouveau form hors-garage)
  - user-friendly: ZÉRO changement visuel — le ✓ orange polo reste
                   identique, on unifie le code derrière

Scope         : 6 patches sur index.html
  - CSS-1 : crée .tick — glyphe ✓ canonique (inséré après le bloc
            .form-error, près des autres composants de form)
  - JS-2  : renderGarageTunerWrap — tuner-cat-tick → tick (1 usage ~17519)
  - JS-3  : 2e render tuner-cat — tuner-cat-tick → tick (1 usage ~18394)
  - JS-4  : renderProfileCard — profile-card-tick → tick (1 usage ~18855)
  - JS-5  : renderOnboardingProfile — onboarding-profile-tick → tick (~18968)
  - CSS-6 : retire les 3 blocs CSS orphelins (.tuner-cat-tick,
            .profile-card-tick, .onboarding-profile-tick) + documente
            .form-* / .form-tick comme systèmes-cibles intentionnels

Note sécurité :
  - Les 3 blocs tick + .form-field sont tous au niveau racine du CSS
    (vérifié au tokenizer — depth 0, comme .builder-search-input).
    Migration sans effet de bord de spécificité/breakpoint.
  - Toutes les anchors sont 2-bornes (borne haute + borne basse qui se
    séparent post-insertion) — leçon des Lots 14/17/21 intégrée.
  - CSS-1 est purement additif. Les migrations JS sont 1:1 (même glyphe,
    même condition isOn/f.xxx). Zéro changement de comportement.

Hors scope :
  - .garage-condition-tick — composant rangée-checkbox distinct, non touché
  - .garage-form-* — système principal déjà refondu v5.x, non touché
  - .form-tick — système générique conservé tel quel, juste documenté
  - .builder-search-input / .auth-input — inputs à specs propres
    (icône recherche, padding auth), cohérents, hors périmètre

Prérequis : Lot 21 (Phase α) appliqué (cohérence chaîne des lots)
Usage     :
    python3 apply_form_components_lot22.py path/to/index.html
    python3 apply_form_components_lot22.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : crée .tick (glyphe ✓ canonique)
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : bloc .form-error (borne haute) + le commentaire
# "Tick / Checkbox stylisé" qui suit (borne basse). Insertion entre les
# deux → anchor cassée post-patch.

CSS1_ANCHOR = """    .form-error {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 12px;
      line-height: 1.4;
      color: #9c2a2a;
      margin-top: 3px;
    }

    /* Tick / Checkbox stylisé */
    .form-tick {"""

CSS1_REPLACEMENT = """    .form-error {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 12px;
      line-height: 1.4;
      color: #9c2a2a;
      margin-top: 3px;
    }

    /* ─────────────────────────────────────────────────────────
       Lot 22 — .tick : glyphe ✓ canonique (composant unique)
       Remplace .tuner-cat-tick / .profile-card-tick /
       .onboarding-profile-tick — c'était le même composant sous
       3 noms. Simple span dont le contenu est ✓ ou vide.
       Usage : <span class="tick">${isOn ? '✓' : ''}</span>
       (à distinguer de .form-tick = rangée-checkbox box+label,
        et de .garage-condition-tick = checkbox carrée in-situ)
       ───────────────────────────────────────────────────────── */
    .tick {
      font-family: var(--sans);
      font-size: 14px;
      line-height: 1;
      color: var(--orange-polo);
      min-width: 14px;
      text-align: right;
      flex-shrink: 0;
      user-select: none;
    }

    /* Tick / Checkbox stylisé */
    .form-tick {"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS : tuner-cat-tick → tick (renderGarageTunerWrap, ~17519)
# ═══════════════════════════════════════════════════════════════════════
# Glyphe en \u2713. Anchor 2-lignes : inclut le <span> label voisin pour
# unicité (l'autre tuner-cat-tick utilise ✓ littéral, distinct).

JS2_ANCHOR = """                <span class="tuner-cat-tick">${isOn ? '\\u2713' : ''}</span>
                <span>${esc(c.label)}</span>"""

JS2_REPLACEMENT = """                <span class="tick">${isOn ? '\\u2713' : ''}</span>
                <span>${esc(c.label)}</span>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — JS : tuner-cat-tick → tick (2e render, ~18394)
# ═══════════════════════════════════════════════════════════════════════
# Glyphe en ✓ littéral. Anchor 2-lignes : inclut le <span> label voisin.

JS3_ANCHOR = """                <span class="tuner-cat-tick">${isOn ? '✓' : ''}</span>
                <span>${esc(cat.label)}</span>"""

JS3_REPLACEMENT = """                <span class="tick">${isOn ? '✓' : ''}</span>
                <span>${esc(cat.label)}</span>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 4 — JS : profile-card-tick → tick (~18855)
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-lignes : inclut le profile-card-chip voisin (contexte unique).

JS4_ANCHOR = """                <span class="profile-card-chip">${esc(p.chip)}</span>
                <span class="profile-card-tick">${isOn ? '✓' : ''}</span>"""

JS4_REPLACEMENT = """                <span class="profile-card-chip">${esc(p.chip)}</span>
                <span class="tick">${isOn ? '✓' : ''}</span>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 5 — JS : onboarding-profile-tick → tick (~18968)
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-lignes : inclut le onboarding-profile-chip voisin (contexte unique).

JS5_ANCHOR = """                <span class="onboarding-profile-chip">${esc(p.chip)}</span>
                <span class="onboarding-profile-tick">${isOn ? '✓' : ''}</span>"""

JS5_REPLACEMENT = """                <span class="onboarding-profile-chip">${esc(p.chip)}</span>
                <span class="tick">${isOn ? '✓' : ''}</span>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 6 — CSS : retire les 3 blocs orphelins + documente form-*/.form-tick
# ═══════════════════════════════════════════════════════════════════════

# 6a — .onboarding-profile-tick : anchor 2-bornes (borne haute = règle
# .selected qui précède, borne basse = .onboarding-profile-label qui suit)
CSS6A_ANCHOR = """    .onboarding-profile-card.selected .onboarding-profile-chip {
      color: var(--orange-polo);
    }
    .onboarding-profile-tick {
      font-family: var(--sans);
      font-size: 13px;
      color: var(--orange-polo);
      line-height: 1;
      min-width: 13px;
      text-align: right;
    }
    .onboarding-profile-label {"""

CSS6A_REPLACEMENT = """    .onboarding-profile-card.selected .onboarding-profile-chip {
      color: var(--orange-polo);
    }
    /* Lot 22 — .onboarding-profile-tick retiré : migré vers .tick canonique */
    .onboarding-profile-label {"""

# 6b — .profile-card-tick
CSS6B_ANCHOR = """    .profile-card.selected .profile-card-chip {
      color: var(--orange-polo);
    }
    .profile-card-tick {
      font-family: var(--sans);
      font-size: 14px;
      color: var(--orange-polo);
      line-height: 1;
      min-width: 14px;
      text-align: right;
    }
    .profile-card-title {"""

CSS6B_REPLACEMENT = """    .profile-card.selected .profile-card-chip {
      color: var(--orange-polo);
    }
    /* Lot 22 — .profile-card-tick retiré : migré vers .tick canonique */
    .profile-card-title {"""

# 6c — .tuner-cat-tick (borne haute = fin de la règle .selected qui précède,
# borne basse = commentaire "Tuner badge")
CSS6C_ANCHOR = """    .tuner-cat-tick {
      width: 14px;
      font-size: 12px;
      color: var(--orange-polo);
      font-weight: 600;
    }

    /* Tuner badge dans sale-status-block et autres displays */
    .tuner-badge-block {"""

CSS6C_REPLACEMENT = """    /* Lot 22 — .tuner-cat-tick retiré : migré vers .tick canonique */

    /* Tuner badge dans sale-status-block et autres displays */
    .tuner-badge-block {"""

# 6d — documente le commentaire FORM COMPONENTS (clarifie que .form-* et
# .form-tick sont des systèmes-cibles intentionnels, pas du code mort)
CSS6D_ANCHOR = """    /* ─────────────────────────────────────────────────────────
       FORM COMPONENTS — base unifiée
       
       Usage : <div class="form-field">
                 <label class="form-label">Marque</label>
                 <input class="form-input" type="text" placeholder="..." />
                 <div class="form-hint">Optionnel — un mot suffit.</div>
                 <div class="form-error">Champ requis</div>
               </div>
       ───────────────────────────────────────────────────────── */"""

CSS6D_REPLACEMENT = """    /* ─────────────────────────────────────────────────────────
       FORM COMPONENTS — base unifiée (système-cible)

       Système générique charte v8, RÉSERVÉ aux nouveaux formulaires
       hors-garage. Le form Ajout voiture utilise .garage-form-* (déjà
       refondu v5.x, 67 usages — ne pas migrer, risque élevé / 0 gain).
       Ce bloc n'est pas du code mort : c'est le système à utiliser
       pour tout futur form. .form-tick = rangée-checkbox box+label.

       Usage : <div class="form-field">
                 <label class="form-label">Marque</label>
                 <input class="form-input" type="text" placeholder="..." />
                 <div class="form-hint">Optionnel — un mot suffit.</div>
                 <div class="form-error">Champ requis</div>
               </div>
       ───────────────────────────────────────────────────────── */"""


# 6e — retire la 2e définition de .profile-card-tick : un override v5.x
# avec !important (font display 22px). CSS-6b n'a retiré que la 1re
# définition (base, ligne ~3050) ; celle-ci (~3907) gagnerait sur .tick
# par !important. Anchor 2-bornes : .profile-card-text (borne haute) +
# commentaire "Cards Affût refonte φ" (borne basse).
CSS6E_ANCHOR = """    .profile-card-text {
      font-size: 14px !important; line-height: 1.5 !important;
    }
    .profile-card-tick {
      font-family: var(--display) !important;
      font-style: italic !important;
      font-size: 22px !important;
      color: var(--orange-polo);
      min-width: 22px !important;
    }

    /* ═══════════════════════════════════════════════════════════
       Cards Affût refonte φ + Fibonacci (v5.39)"""

CSS6E_REPLACEMENT = """    .profile-card-text {
      font-size: 14px !important; line-height: 1.5 !important;
    }
    /* Lot 22 — 2e définition .profile-card-tick (override v5.x !important)
       retirée : migré vers .tick canonique. */

    /* ═══════════════════════════════════════════════════════════
       Cards Affût refonte φ + Fibonacci (v5.39)"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 22 (Phase α) — Form components : unification des ticks",
    requires=[
        # Marker réellement présent dans le fichier (le nom du PatchSet
        # n'est pas injecté ; c'est le marker du patch CSS-1 du Lot 21).
        "Lot 21 — modifiers : .banner devient le système unique",
    ],
    patches=[
        Patch(
            name="CSS-1 · crée .tick — glyphe ✓ canonique",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Lot 22 — .tick : glyphe ✓ canonique",
        ),
        Patch(
            name="JS-2 · tuner-cat-tick → tick (renderGarageTunerWrap)",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker='<span class="tick">${isOn ? \'\\u2713\' : \'\'}</span>\n                <span>${esc(c.label)}</span>',
        ),
        Patch(
            name="JS-3 · tuner-cat-tick → tick (2e render)",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker='<span class="tick">${isOn ? \'✓\' : \'\'}</span>\n                <span>${esc(cat.label)}</span>',
        ),
        Patch(
            name="JS-4 · profile-card-tick → tick",
            anchor=JS4_ANCHOR,
            replacement=JS4_REPLACEMENT,
            idempotence_marker='<span class="profile-card-chip">${esc(p.chip)}</span>\n                <span class="tick">',
        ),
        Patch(
            name="JS-5 · onboarding-profile-tick → tick",
            anchor=JS5_ANCHOR,
            replacement=JS5_REPLACEMENT,
            idempotence_marker='<span class="onboarding-profile-chip">${esc(p.chip)}</span>\n                <span class="tick">',
        ),
        Patch(
            name="CSS-6a · retire .onboarding-profile-tick orphelin",
            anchor=CSS6A_ANCHOR,
            replacement=CSS6A_REPLACEMENT,
            idempotence_marker="Lot 22 — .onboarding-profile-tick retiré",
        ),
        Patch(
            name="CSS-6b · retire .profile-card-tick orphelin",
            anchor=CSS6B_ANCHOR,
            replacement=CSS6B_REPLACEMENT,
            idempotence_marker="Lot 22 — .profile-card-tick retiré",
        ),
        Patch(
            name="CSS-6c · retire .tuner-cat-tick orphelin",
            anchor=CSS6C_ANCHOR,
            replacement=CSS6C_REPLACEMENT,
            idempotence_marker="Lot 22 — .tuner-cat-tick retiré",
        ),
        Patch(
            name="CSS-6d · documente .form-* / .form-tick comme systèmes-cibles",
            anchor=CSS6D_ANCHOR,
            replacement=CSS6D_REPLACEMENT,
            idempotence_marker="FORM COMPONENTS — base unifiée (système-cible)",
        ),
        Patch(
            name="CSS-6e · retire la 2e définition .profile-card-tick (override v5.x !important)",
            anchor=CSS6E_ANCHOR,
            replacement=CSS6E_REPLACEMENT,
            idempotence_marker="2e définition .profile-card-tick (override v5.x !important)",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
