#!/usr/bin/env python3
"""
CARNET · Lot 21 (Phase α) — Unification du système banner

Source        : Audit Lot 21. Constat en deux temps :

  SUJET 2 (réglé en premier — par l'audit) :
    .completion-banner (12 usages, le banner le plus utilisé du fichier)
    est DÉJÀ refondu à un haut niveau (padding Fibonacci 21/13, dot orange
    polo, tag mono 0.18em, msg Cormorant italic, progress 2px vert anglais,
    CTA mono, animation completionFadeIn 380ms). RIEN à faire. ✓
    De même : .sold-detail-banner, .dashboard-auction-banner,
    .auction-detail-banner — tous déjà cohérents charte v8.

  SUJET 1 (l'objet réel de ce lot) :
    Il existe un système .banner générique + 4 variants (info / warning /
    success / danger), entièrement stylé, structure charte v8 correcte,
    AU NIVEAU RACINE du CSS (vérifié au tokenizer — pas dans @media print
    malgré une fausse piste d'audit) — MAIS avec 0 usage HTML réel.
    C'est du CSS vivant-mais-orphelin.

    Parallèlement, .profile-onboarding-banner (1 seul usage) a une
    structure JUMELLE du .banner générique (tag mono / titre Bodoni /
    texte Cormorant / cta mono), à deux détails près : bordure pointillée
    (1px dashed orange-polo, pas border-left 2px) et banner cliquable.

Stratégie     : "structure robuste, light, slick" — ni suppression bête,
                ni migration risquée des 5 banners. On rend le .banner
                générique VIVANT en lui faisant absorber le seul cas
                qui lui ressemble (.profile-onboarding-banner), via 2
                modifiers ajoutés. Le .banner devient la source de vérité
                unique réutilisable. Les 4 banners structurellement
                spécifiques (completion/sold/dashboard/auction) restent
                autonomes — c'est légitime, ils ont progress bars, valeurs,
                layouts propres.

Scope         : 3 patches sur index.html
                  - CSS-1 : étend .banner — ajoute modifiers .is-dashed
                            (bordure pointillée onboarding) + .is-clickable
                            (curseur + feedback :active). Patch chirurgical,
                            le bloc .banner existant n'est PAS réécrit.
                  - JS-2  : renderProfileOnboardingBanner → migre vers
                            <div class="banner banner-warning is-dashed is-clickable">
                            + classes génériques banner-tag/-title/-text/-cta
                  - CSS-3 : retire le CSS .profile-onboarding-* orphelin
                            (6 règles, lignes ~3855-3884) — dette nettoyée

Résultat : .banner n'est plus orphelin, il est LE système banner
  réutilisable et propre. Un futur banner = <div class="banner banner-X">,
  zéro CSS à écrire. Une seule source de vérité.

Note sécurité :
  - .banner et .profile-onboarding-* sont tous deux au niveau racine
    (même profondeur que .sheet-btn — vérifié au tokenizer). Migration
    sans effet de bord de spécificité ou de breakpoint.
  - CSS-1 est purement ADDITIF (nouvelles règles .banner.is-dashed /
    .is-clickable), le bloc .banner d'origine reste intact → les 4
    variants existants ne bougent pas.
  - L'anchor CSS-1 (.banner-cta:active + les 4 lignes variant-cta) est
    une borne 2-points : la dernière ligne du bloc .banner. Insertion
    APRÈS, donc anchor cassée post-patch. ✓

Hors scope :
  - .completion-banner / .sold-detail-banner / .dashboard-auction-banner
    / .auction-detail-banner — déjà refondus, structures spécifiques,
    non touchés
  - .empty-state* — déjà refondu v5.x (override 6021-6066), non touché

Prérequis : Lot 20 (Phase α) appliqué (cohérence chaîne des lots)
Usage     :
    python3 apply_banner_unification_lot21.py path/to/index.html
    python3 apply_banner_unification_lot21.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — CSS : étend .banner avec modifiers .is-dashed + .is-clickable
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : les 4 dernières lignes variant-cta du bloc .banner.
# Insertion APRÈS → anchor cassée post-patch (le bloc .banner d'origine
# reste intact, les nouvelles règles s'ajoutent à la suite).

CSS1_ANCHOR = """    .banner-cta:active { opacity: 0.7; }
    .banner.banner-info .banner-cta { color: var(--encre); }
    .banner.banner-warning .banner-cta { color: var(--orange-polo); }
    .banner.banner-success .banner-cta { color: var(--vert-anglais); }
    .banner.banner-danger .banner-cta { color: #9c2a2a; }


    /* ─────────────────────────────────────────────────────────
       FORM COMPONENTS — base unifiée"""

CSS1_REPLACEMENT = """    .banner-cta:active { opacity: 0.7; }
    .banner.banner-info .banner-cta { color: var(--encre); }
    .banner.banner-warning .banner-cta { color: var(--orange-polo); }
    .banner.banner-success .banner-cta { color: var(--vert-anglais); }
    .banner.banner-danger .banner-cta { color: #9c2a2a; }

    /* Lot 21 — modifiers : .banner devient le système unique réutilisable.
       .is-dashed   : bordure pointillée tout-autour (remplace le border-left)
       .is-clickable: tout le banner est tappable (curseur + feedback :active) */
    .banner.is-dashed {
      border-left: none;
      border: 1px dashed var(--gris-line);
    }
    .banner.is-dashed.banner-info    { border-color: var(--encre); }
    .banner.is-dashed.banner-warning { border-color: var(--orange-polo); }
    .banner.is-dashed.banner-success { border-color: var(--vert-anglais); }
    .banner.is-dashed.banner-danger  { border-color: #9c2a2a; }
    .banner.is-clickable {
      cursor: pointer;
      transition: background-color var(--duration-fast) ease;
    }
    .banner.is-clickable:active { background-color: var(--papier-soft); }
    .banner.is-clickable.banner-warning:active { background-color: rgba(232, 90, 31, 0.07); }
    .banner.is-clickable.banner-success:active { background-color: rgba(31, 77, 47, 0.07); }
    .banner.is-clickable.banner-danger:active  { background-color: rgba(156, 42, 42, 0.07); }


    /* ─────────────────────────────────────────────────────────
       FORM COMPONENTS — base unifiée"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — JS : renderProfileOnboardingBanner migré vers système .banner
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = """function renderProfileOnboardingBanner(){
  if((State.userProfiles || []).length > 0) return '';
  return `
    <div class="profile-onboarding-banner" data-action="openSelectProfile">
      <div class="profile-onboarding-tag">CONSEIL CARNET</div>
      <h3 class="profile-onboarding-title">D\\u00e9finis ton profil de collectionneur.</h3>
      <p class="profile-onboarding-text">CARNET adapte ses conseils \\u00e0 ta fa\\u00e7on de vivre ta passion. Le pilote, le b\\u00e2tisseur, le gardien \\u2014 ils ne re\\u00e7oivent pas les m\\u00eames suggestions.</p>
      <div class="profile-onboarding-cta">D\\u00e9finir mon profil \\u2192</div>
    </div>
  `;
}"""

JS2_REPLACEMENT = """function renderProfileOnboardingBanner(){
  if((State.userProfiles || []).length > 0) return '';
  // Lot 21 — migré vers le système .banner générique (variant warning,
  // modifiers is-dashed + is-clickable). Plus de CSS .profile-onboarding-* dédié.
  return `
    <div class="banner banner-warning is-dashed is-clickable" data-action="openSelectProfile">
      <div class="banner-tag">CONSEIL CARNET</div>
      <h3 class="banner-title">D\\u00e9finis ton profil de collectionneur.</h3>
      <p class="banner-text">CARNET adapte ses conseils \\u00e0 ta fa\\u00e7on de vivre ta passion. Le pilote, le b\\u00e2tisseur, le gardien \\u2014 ils ne re\\u00e7oivent pas les m\\u00eames suggestions.</p>
      <button class="banner-cta">D\\u00e9finir mon profil \\u2192</button>
    </div>
  `;
}"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — CSS : retire le bloc .profile-onboarding-* orphelin
# ═══════════════════════════════════════════════════════════════════════
# Anchor 2-bornes : tout le bloc .profile-onboarding-* + la ligne suivante
# (.advice-feed) comme borne basse. Le replacement garde .advice-feed,
# supprime le bloc orphelin → anchor cassée post-patch.

CSS3_ANCHOR = """    .profile-onboarding-banner {
      background: var(--papier-bright);
      border: 1px dashed var(--orange-polo);
      border-radius: var(--r);
      padding: 21px;
      margin-bottom: 21px;
      cursor: pointer;
      transition: background var(--duration-fast) ease;
    }
    .profile-onboarding-banner:active { background: rgba(232, 90, 31, 0.04); }
    .profile-onboarding-tag {
      font-family: var(--mono);
      font-size: 9px; letter-spacing: 0.16em;
      color: var(--orange-polo); font-weight: 600;
      text-transform: uppercase; margin-bottom: 8px;
    }
    .profile-onboarding-title {
      font-family: var(--display); font-style: italic; font-weight: 500;
      font-size: 22px; line-height: 1.15;
      color: var(--encre); margin: 0 0 8px 0; letter-spacing: -0.005em;
    }
    .profile-onboarding-text {
      font-family: var(--editorial); font-style: italic;
      font-size: 14px; line-height: 1.5;
      color: var(--gris); margin: 0 0 13px 0;
    }
    .profile-onboarding-cta {
      font-family: var(--mono);
      font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
      color: var(--orange-polo); text-transform: uppercase;
    }
    .advice-feed { display: flex; flex-direction: column; gap: var(--s-2); margin-bottom: 21px; }"""

CSS3_REPLACEMENT = """    /* Lot 21 — bloc .profile-onboarding-* retiré : migré vers le système
       .banner générique (banner-warning is-dashed is-clickable). Le seul
       langage de banner contextuel-cliquable est désormais .banner. */
    .advice-feed { display: flex; flex-direction: column; gap: var(--s-2); margin-bottom: 21px; }"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 21 (Phase α) — Unification du système banner",
    requires=[
        "LOT 20 (Phase α) — Sheets création : flow Nouvelle alerte (builder)",
    ],
    patches=[
        Patch(
            name="CSS-1 · étend .banner — modifiers .is-dashed + .is-clickable",
            anchor=CSS1_ANCHOR,
            replacement=CSS1_REPLACEMENT,
            idempotence_marker="Lot 21 — modifiers : .banner devient le système unique",
        ),
        Patch(
            name="JS-2 · renderProfileOnboardingBanner migré vers système .banner",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker='<div class="banner banner-warning is-dashed is-clickable"',
        ),
        Patch(
            name="CSS-3 · retire le bloc .profile-onboarding-* orphelin",
            anchor=CSS3_ANCHOR,
            replacement=CSS3_REPLACEMENT,
            idempotence_marker="Lot 21 — bloc .profile-onboarding-* retiré",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
