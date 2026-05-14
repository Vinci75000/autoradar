#!/usr/bin/env python3
"""
CARNET · Lot 19-A (Phase α) — Migration .sheet-row → .sheet-detail-row

Source        : Audit Lot 19. Les sheets détail (Match/Auction/GarageCar)
                sont déjà largement refondues via le système .sheet-detail-*
                (Fibonacci, charte v8). Le seul vrai écart : un système
                LEGACY .sheet-row / .sheet-row-label / .sheet-row-value
                (stylé lignes 820-844, pré-φ) cohabite encore, utilisé par
                4 render functions.

Scope         : 5 patches sur index.html
                  - JS-1 : renderAlertSheet   — 2 rows migrées + wrappées
                  - JS-2 : renderAuctionSheet — activityRows (code mort) retiré
                  - JS-3 : renderWatchedSheet — 3 rows migrées + wrappées
                  - JS-4 : renderListingSheet — 6 rows migrées + 2 wrappers
                  - CSS  : bloc legacy .sheet-row* retiré (820-844)

Migration :
  .sheet-row        → .sheet-detail-row        (dans un parent .sheet-detail-rows)
  .sheet-row-label  → .sheet-detail-row-label
  .sheet-row-value  → .sheet-detail-row-value

Différence sémantique gérée :
  .sheet-row legacy   = chaque row a border-bottom + padding 12px 0
  .sheet-detail-row   = pas de border, gap 13px porté par le parent
                        .sheet-detail-rows (flex column)
  → la migration WRAPPE donc les groupes de rows dans .sheet-detail-rows
    pour que l'espacement Fibonacci s'applique correctement.

activityRows (renderAuctionSheet) :
  Variable const définie lignes 17133-17136 mais JAMAIS insérée dans le
  rendu — renderAuctionSheet a déjà sa propre version inline en
  .sheet-detail-row (Maison de vente / Numéro de lot / Suiveurs / Enchères).
  C'est du code mort, simplement retiré.

Résultat : un seul langage de lignes détail dans tout le fichier
  (.sheet-detail-rows > .sheet-detail-row), CSS legacy supprimé.

Note sécurité :
  .sheet-detail-* et .sheet-row sont TOUS DEUX au niveau racine du CSS
  (vérifié — l'indentation 4-espaces du bloc v5.41 est cosmétique, pas
  une media query). La migration n'a donc aucun effet de bord de
  spécificité ou de breakpoint.

Hors scope :
  - .sheet-section-label — système distinct, toujours valide, non touché
  - Les blocs .sheet-detail-row déjà en place (Match/Auction/GarageCar) —
    déjà au bon format, non touchés

Prérequis : Lot 18b (Phase α) appliqué (cohérence chaîne des lots)
Usage     :
    python3 apply_sheetrow_migration_lot19.py path/to/index.html
    python3 apply_sheetrow_migration_lot19.py path/to/index.html --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, run_cli


# ═══════════════════════════════════════════════════════════════════════
# PATCH 1 — renderAlertSheet : 2 rows migrées + wrappées
# ═══════════════════════════════════════════════════════════════════════

JS1_ANCHOR = """      <p class="sheet-desc">${esc(a.meta)}</p>
      <div class="sheet-row">
        <span class="sheet-row-label">Type</span>
        <span class="sheet-row-value">${esc(a.label)}</span>
      </div>
      <div class="sheet-row">
        <span class="sheet-row-label">Statut</span>
        <span class="sheet-row-value">${esc(statusText)}</span>
      </div>
    </div>"""

JS1_REPLACEMENT = """      <p class="sheet-desc">${esc(a.meta)}</p>
      <div class="sheet-detail-rows">
        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Type</span>
          <span class="sheet-detail-row-value">${esc(a.label)}</span>
        </div>
        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Statut</span>
          <span class="sheet-detail-row-value">${esc(statusText)}</span>
        </div>
      </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 2 — renderAuctionSheet : activityRows (code mort) retiré
# ═══════════════════════════════════════════════════════════════════════

JS2_ANCHOR = """  // Activity stats
  const activityRows = a.status === 'upcoming'
    ? `<div class="sheet-row"><span class="sheet-row-label">Suiveurs</span><span class="sheet-row-value">${a.watching}</span></div>`
    : `<div class="sheet-row"><span class="sheet-row-label">Enchères</span><span class="sheet-row-value">${a.bids}</span></div>
       <div class="sheet-row"><span class="sheet-row-label">Suiveurs</span><span class="sheet-row-value">${a.watching}</span></div>`;
  // CTAs vary by status"""

JS2_REPLACEMENT = """  // Lot 19-A — activityRows (code mort jamais inséré) retiré : renderAuctionSheet
  // a déjà ses lignes détail inline en .sheet-detail-row plus bas.
  // CTAs vary by status"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 3 — renderWatchedSheet : 3 rows migrées + wrappées
# ═══════════════════════════════════════════════════════════════════════

JS3_ANCHOR = """      <div class="sheet-row">
        <span class="sheet-row-label">Alertes liées</span>
        <span class="sheet-row-value">${w.alerts} alerte${w.alerts === 1 ? '' : 's'}</span>
      </div>
      <div class="sheet-row">
        <span class="sheet-row-label">Tendance 12 mois</span>
        <span class="sheet-row-value">${esc(w.trendLabel)}</span>
      </div>
      <div class="sheet-row">
        <span class="sheet-row-label">Apparitions \u00b7 90 j</span>
        <span class="sheet-row-value">3 occurrences</span>
      </div>
    </div>"""

JS3_REPLACEMENT = """      <div class="sheet-detail-rows">
        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Alertes liées</span>
          <span class="sheet-detail-row-value">${w.alerts} alerte${w.alerts === 1 ? '' : 's'}</span>
        </div>
        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Tendance 12 mois</span>
          <span class="sheet-detail-row-value">${esc(w.trendLabel)}</span>
        </div>
        <div class="sheet-detail-row">
          <span class="sheet-detail-row-label">Apparitions \u00b7 90 j</span>
          <span class="sheet-detail-row-value">3 occurrences</span>
        </div>
      </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 4 — renderListingSheet : 6 rows migrées + 2 wrappers (DOSSIER/SOURCE)
# ═══════════════════════════════════════════════════════════════════════

JS4_ANCHOR = """      <div class="sheet-section-label">DOSSIER</div>
      <div class="sheet-row"><span class="sheet-row-label">Année</span><span class="sheet-row-value">${l.yr}</span></div>
      <div class="sheet-row"><span class="sheet-row-label">Kilométrage</span><span class="sheet-row-value">${esc(fmtKm(l.km))}</span></div>
      <div class="sheet-row"><span class="sheet-row-label">Verdict</span><span class="sheet-row-value">${esc(verdictLabel)}</span></div>
      <div class="sheet-row"><span class="sheet-row-label">Localisation</span><span class="sheet-row-value">${esc(l.ci)}, ${esc(l.co)}</span></div>
      <div class="sheet-section-label">SOURCE</div>
      <div class="sheet-row"><span class="sheet-row-label">Marchand</span><span class="sheet-row-value">${esc(l.src)}</span></div>
      <div class="sheet-row"><span class="sheet-row-label">Score CARNET</span><span class="sheet-row-value">${l.sc} / 100</span></div>
    </div>"""

JS4_REPLACEMENT = """      <div class="sheet-section-label">DOSSIER</div>
      <div class="sheet-detail-rows">
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Année</span><span class="sheet-detail-row-value">${l.yr}</span></div>
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Kilométrage</span><span class="sheet-detail-row-value">${esc(fmtKm(l.km))}</span></div>
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Verdict</span><span class="sheet-detail-row-value">${esc(verdictLabel)}</span></div>
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Localisation</span><span class="sheet-detail-row-value">${esc(l.ci)}, ${esc(l.co)}</span></div>
      </div>
      <div class="sheet-section-label">SOURCE</div>
      <div class="sheet-detail-rows">
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Marchand</span><span class="sheet-detail-row-value">${esc(l.src)}</span></div>
        <div class="sheet-detail-row"><span class="sheet-detail-row-label">Score CARNET</span><span class="sheet-detail-row-value">${l.sc} / 100</span></div>
      </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# PATCH 5 — CSS : bloc legacy .sheet-row* retiré
# ═══════════════════════════════════════════════════════════════════════

CSS_ANCHOR = """.sheet-row{
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  padding:var(--s-3) 0;
  border-bottom:1px solid var(--gris-line-soft);
  gap:var(--s-3);
}
.sheet-row:last-child{border-bottom:none}
.sheet-row-label{
  font-family:var(--mono);
  font-size:10px;
  color:var(--gris);
  letter-spacing:0.12em;
  text-transform:uppercase;
  flex-shrink:0;
}
.sheet-row-value{
  font-family:var(--editorial);
  font-style:italic;
  font-size:var(--t-base);
  color:var(--encre);
  text-align:right;
  flex:1;
}
.sheet-section-label{"""

CSS_REPLACEMENT = """/* Lot 19-A — système legacy .sheet-row retiré : migré vers .sheet-detail-row
   (Alert / Auction / Watched / Listing sheets). Langage unique des lignes
   détail désormais : .sheet-detail-rows > .sheet-detail-row. */
.sheet-section-label{"""


# ═══════════════════════════════════════════════════════════════════════
# PatchSet
# ═══════════════════════════════════════════════════════════════════════

PATCHSET = PatchSet(
    name="Lot 19-A (Phase α) — Migration .sheet-row → .sheet-detail-row",
    requires=[
        "LOT 18b (Phase α) — .new-alert-btn alignement couleur orange polo",
    ],
    patches=[
        Patch(
            name="JS-1 · renderAlertSheet — 2 rows migrées + wrappées .sheet-detail-rows",
            anchor=JS1_ANCHOR,
            replacement=JS1_REPLACEMENT,
            idempotence_marker='<span class="sheet-detail-row-label">Type</span>',
        ),
        Patch(
            name="JS-2 · renderAuctionSheet — activityRows (code mort) retiré",
            anchor=JS2_ANCHOR,
            replacement=JS2_REPLACEMENT,
            idempotence_marker="// Lot 19-A — activityRows (code mort jamais inséré) retiré",
        ),
        Patch(
            name="JS-3 · renderWatchedSheet — 3 rows migrées + wrappées",
            anchor=JS3_ANCHOR,
            replacement=JS3_REPLACEMENT,
            idempotence_marker='<span class="sheet-detail-row-label">Alertes liées</span>',
        ),
        Patch(
            name="JS-4 · renderListingSheet — 6 rows migrées + 2 wrappers DOSSIER/SOURCE",
            anchor=JS4_ANCHOR,
            replacement=JS4_REPLACEMENT,
            idempotence_marker='<div class="sheet-detail-row"><span class="sheet-detail-row-label">Année</span>',
        ),
        Patch(
            name="CSS · bloc legacy .sheet-row* retiré (820-844)",
            anchor=CSS_ANCHOR,
            replacement=CSS_REPLACEMENT,
            idempotence_marker="Lot 19-A — système legacy .sheet-row retiré",
        ),
    ],
)


if __name__ == "__main__":
    sys.exit(run_cli(PATCHSET))
